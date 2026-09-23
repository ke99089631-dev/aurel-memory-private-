# -*- coding: utf-8 -*-
"""
壁→壁 コックピット: 動くライブチャートを Tailscale:8793 で配る独立サーバ。
  既存のチャット室サーバ(8792)・司令室(7878)には一切触れない（別プロセス・別ポート）。
  ブラウザ側で TradingView Lightweight Charts が描く＝ズーム/パン/スクロール/リアルタイム更新。
  サーバはデータ(JSON)を配るだけ:
    GET /                       → chart_live.html（対話チャート本体）
    GET /lightweight-charts.js  → 取り込んだ描画ライブラリ（ローカル・ネット非依存）
    GET /api/data?n=1500        → 直近n本のM5 + 現在tick + 壁(箱/中間/直近ブレイクのTP/SL) を JSON
  MT5接続は開いたまま保持し、リクエスト毎に読むだけ（読取専用・発注なし・金は動かない）。
  Tailscale IP のみにバインド。
"""
import os
import sys
import json
import time
import threading
import http.server
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chart_gen  # current_box / detect_last_break / latest_m5 を再利用

HOST = "100.73.107.61"     # Tailscale IP のみ（Wi-Fi/インターネットには出さない）
PORT = 8793
PAGE = os.path.join(HERE, "chart_live.html")
LIB = os.path.join(HERE, "lightweight-charts.js")

# C1 ダマシ確率メーター用: JST時間帯別 本物率(TP率) テーブル（compute_damashi_jst.py が生成）
_DAMASHI = None
try:
    with open(os.path.join(HERE, "damashi_hour_jst.json"), encoding="utf-8") as _f:
        _DAMASHI = json.load(_f)
except Exception:
    _DAMASHI = None

# ── MT5接続をプロセス内で保持（都度 initialize/shutdown しない）──────────
# MetaTrader5 API はスレッド安全でないため、全読取を1本のロックで直列化する。
_MT5 = None
_LOCK = threading.Lock()


def _get_mt5():
    """保持中の接続を返す。無ければ張り直す。失敗時は None を返して履歴にフォールバックさせる。"""
    global _MT5
    if _MT5 is not None:
        return _MT5
    try:
        import mt5_bridge
        _MT5 = mt5_bridge.connect()   # 口座27972608限定・発注なし・安全弁つき
    except Exception as e:
        sys.stderr.write("[MT5接続不可→履歴] %s\n" % (e,))
        _MT5 = None
    return _MT5


def _live_df_tick(n):
    """保持接続から M5(UTC index) と tick。失敗したら接続を破棄して例外。ロックで直列化。"""
    global _MT5
    import mt5_bridge
    with _LOCK:
        mt5 = _get_mt5()
        if mt5 is None:
            raise RuntimeError("no MT5")
        try:
            df = mt5_bridge.m5_bars(mt5, n)
            tick = mt5_bridge.live_tick(mt5)
        except Exception:
            try:
                mt5.shutdown()
            except Exception:
                pass
            _MT5 = None
            raise
    df = df.set_index("dt")
    return df[["open", "high", "low", "close"]], tick


def build_tick():
    """毎秒ポーリング用の軽量データ: 現在tick + 直近数本(形成中ローソクの成長を反映)。壁計算はしない。"""
    import pandas as pd
    try:
        m5, tick = _live_df_tick(3)
    except Exception:
        return {"source": "hist", "ts": int(time.time()), "tick": None, "lastbars": []}
    idx = m5.index
    lastbars = [{"time": int(pd.Timestamp(idx[k]).timestamp()),
                 "open": round(float(m5["open"].iloc[k]), 3),
                 "high": round(float(m5["high"].iloc[k]), 3),
                 "low": round(float(m5["low"].iloc[k]), 3),
                 "close": round(float(m5["close"].iloc[k]), 3)}
                for k in range(len(m5))]
    return {"source": "live", "ts": int(time.time()), "tick": tick, "lastbars": lastbars}


_PAPER_V3_FILE = os.path.join(HERE, "paper_ledger_v3.jsonl")
_AI_MAX_HOLD_S = 288 * 300   # backtest_v3 の MAX_HOLD(288本) 秒換算


def latest_ai_position(tick):
    """AURELの直近の建玉(車線3 v3a の最新TAKE)を、今の価格で追跡して返す。
       現在値がSL/TP未達かつ保有時間内なら open(=ライブ追跡), それ以外は closed。"""
    last = None
    try:
        for line in open(_PAPER_V3_FILE, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("decision") == "TAKE":
                last = r
    except Exception:
        return None
    if not last:
        return None
    entry = last["entry"]; sl = last["sl"]; tp = last["tp"]; side = last["side"]
    risk = abs(entry - sl) or 1e-9
    price = ((tick["bid"] + tick["ask"]) / 2.0) if tick else entry
    if side == "SELL":
        live_r = (entry - price) / risk
        hit_sl = price >= sl; hit_tp = price <= tp
    else:
        live_r = (price - entry) / risk
        hit_sl = price <= sl; hit_tp = price >= tp
    now = int(time.time())
    within = (now - int(last["entry_time"])) < _AI_MAX_HOLD_S
    is_open = (not hit_sl) and (not hit_tp) and within
    return {
        "id": last.get("id"), "side": side, "entry": entry, "sl": sl, "tp": tp,
        "entry_time": int(last["entry_time"]), "entry_jst": last.get("entry_jst"),
        "wall": last.get("wall"), "width": last.get("width"),
        "score": last.get("score"), "real_rate": last.get("real_rate"),
        "reason": last.get("skip_reason") or "",
        "open": bool(is_open), "live_r": round(live_r, 2),
        "recorded_exit": last.get("exit"), "recorded_reason": last.get("exit_reason"),
    }


def fixed_box_and_break(m5):
    """効いてる固定の壁(スイング＋タッチ)で箱を決める。ローリング最安値のように価格を追わない。
       価格が壁の外に出ていれば break(メジャードムーブ目標つき)を返す。"""
    import numpy as np
    import walls
    h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    n = len(c)
    if n < 40:
        return None, None
    win = 200                      # 直近~15hの構造から壁を採る
    lo0 = max(0, n - win)
    atr = float(np.mean(h[max(1, n - 14):n] - l[max(1, n - 14):n])) if n > 15 else 0.0
    ws = walls.find_walls(h[lo0:n], l[lo0:n], c[lo0:n], atr)
    res = [w for w in ws if w["kind"] == "res"]
    sup = [w for w in ws if w["kind"] == "sup"]
    if not res or not sup:
        return None, None
    R = max(res, key=lambda w: (w["touches"], w["price"]))    # 強い抵抗(タッチ優先,高い方)
    S = max(sup, key=lambda w: (w["touches"], -w["price"]))   # 強い支持(タッチ優先,低い方)
    up, dn = R["price"], S["price"]
    if up <= dn:
        return None, None
    width = up - dn
    mids = [w for w in ws if dn < w["price"] < up]
    mid = max(mids, key=lambda w: w["touches"])["price"] if mids else (up + dn) / 2.0
    box = {"up": round(up, 3), "dn": round(dn, 3), "mid": round(mid, 3),
           "width": round(width, 3), "up_touches": R["touches"], "dn_touches": S["touches"]}
    price = float(c[-1])
    brk = None
    if price < dn:
        brk = {"dir": "DOWN", "wall": round(dn, 3), "width": round(width, 3),
               "tp": round(dn - width, 3), "sl": round(dn + width * 0.33, 3)}
    elif price > up:
        brk = {"dir": "UP", "wall": round(up, 3), "width": round(width, 3),
               "tp": round(up + width, 3), "sl": round(up - width * 0.33, 3)}
    return box, brk


def build_data(n=1500):
    """チャート用データ一式（bars/tick/walls/source）。live優先→hist フォールバック。"""
    tick = None
    source = "live"
    try:
        m5, tick = _live_df_tick(n)
        if len(m5) == 0:
            raise RuntimeError("live 0本")
    except Exception:
        source = "hist"
        m5 = chart_gen.latest_m5(n)

    import pandas as pd
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    idx = m5.index
    bars = [{"time": int(pd.Timestamp(idx[k]).timestamp()),
             "open": round(float(o[k]), 3), "high": round(float(h[k]), 3),
             "low": round(float(l[k]), 3), "close": round(float(c[k]), 3)}
            for k in range(len(m5))]
    # 効いてる固定の壁に差し替え（ローリング最安値=価格追従の弱点を解消）。失敗時のみ旧方式。
    box, brk = fixed_box_and_break(m5)
    if box is None:
        box = chart_gen.current_box(m5)
        brk = None
    ai_pos = latest_ai_position(tick)

    # C1: いまの時間帯(JST)の本物率(機械統計)
    damashi = None
    if _DAMASHI:
        try:
            jh = int(pd.Timestamp(m5.index[-1]).tz_convert("Asia/Tokyo").hour)
            hrec = _DAMASHI.get("hours", {}).get(str(jh))
            base = _DAMASHI.get("base_tp_rate")
            if hrec:
                damashi = {"jst_hour": jh, "real_rate": hrec["tp_rate"],
                           "n": hrec["n"], "base": base}
        except Exception:
            damashi = None

    return {
        "symbol": "XAUUSD (金) M5",
        "source": source,
        "ts": int(time.time()),
        "tick": tick,
        "bars": bars,
        "box": {k: round(v, 3) for k, v in box.items()},
        "break": ({k: (round(v, 3) if isinstance(v, float) else v)
                   for k, v in brk.items()} if brk else None),
        "damashi": damashi,
        "ai_pos": ai_pos,
        "range_w": chart_gen.RANGE_W,
    }


LEDGER = r"C:\Users\user\.aurel\memory\projects\discretionary\ledger.jsonl"


def _jst_epoch(ts):
    """台帳の ts (JST naive '2026-09-22T21:44:00') → epoch秒(UTC)。"""
    import datetime as dt
    try:
        d = dt.datetime.fromisoformat(ts)
        return int(d.replace(tzinfo=dt.timezone(dt.timedelta(hours=9))).timestamp())
    except Exception:
        return None


def build_trades():
    """台帳(ledger.jsonl)を統合して会長の実トレード一覧を返す。
       kind=trade を基本に、kind=update(target一致)で exit/sl/tp/post を上書き。"""
    trades = {}
    order = []
    try:
        f = open(LEDGER, encoding="utf-8")
    except Exception:
        return {"trades": []}
    with f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            k = r.get("kind")
            if k == "trade":
                tid = r.get("id")
                trades[tid] = {
                    "id": tid, "side": r.get("side"),
                    "entry": r.get("entry"), "sl": r.get("sl"), "tp": r.get("tp"),
                    "exit": r.get("exit"), "entry_time": _jst_epoch(r.get("ts")),
                    "exit_time": None, "post": r.get("post") or "",
                    "wall": r.get("wall") or "",
                }
                order.append(tid)
            elif k == "update":
                t = trades.get(r.get("target"))
                if not t:
                    continue
                if r.get("exit") is not None:
                    t["exit"] = r.get("exit"); t["exit_time"] = _jst_epoch(r.get("ts"))
                if r.get("sl") is not None:
                    t["sl"] = r.get("sl")
                if r.get("tp") is not None:
                    t["tp"] = r.get("tp")
                if r.get("post"):
                    t["post"] = r.get("post")
    return {"trades": [trades[t] for t in order]}


PAPER_LEDGER = os.path.join(HERE, "paper_ledger.jsonl")


def build_paper():
    """車線3(AUREL紙トレード)の一覧＋集計。会長の実(車線1)とは別物・発注なし。"""
    rows = []
    try:
        for line in open(PAPER_LEDGER, encoding="utf-8"):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    except Exception:
        rows = []
    n = len(rows)
    if not n:
        return {"trades": [], "summary": {"n": 0}}
    tp = sum(1 for r in rows if r.get("exit_reason") == "TP")
    sl = sum(1 for r in rows if r.get("exit_reason") == "SL")
    tm = sum(1 for r in rows if r.get("exit_reason") == "TIME")
    avg_r = sum(r.get("R", 0) for r in rows) / n
    # 時間帯(zone)別
    zones = {}
    for r in rows:
        z = r.get("zone", "中立")
        zones.setdefault(z, {"n": 0, "tp": 0, "sumR": 0.0})
        zones[z]["n"] += 1
        zones[z]["tp"] += 1 if r.get("exit_reason") == "TP" else 0
        zones[z]["sumR"] += r.get("R", 0)
    by_zone = {z: {"n": v["n"], "tp_rate": round(100.0 * v["tp"] / v["n"], 1),
                   "avg_r": round(v["sumR"] / v["n"], 3)}
               for z, v in zones.items() if v["n"] > 0}
    # ★本物(TP) vs ダマシ(SL) で「質・文脈の特徴」の平均を比較＝どの特徴が分けるか
    FEATS = ["break_str_atr", "entry_body_ratio", "reject_wick_ratio",
             "momentum20_pct", "range_pos", "wall_touches", "tightness_pct"]
    tp_rows = [r for r in rows if r.get("exit_reason") == "TP"]
    sl_rows = [r for r in rows if r.get("exit_reason") == "SL"]

    def _mean(rs, key):
        vals = [r.get("features", {}).get(key) for r in rs]
        vals = [v for v in vals if isinstance(v, (int, float))]
        return round(sum(vals) / len(vals), 3) if vals else None

    feature_split = {}
    for k in FEATS:
        feature_split[k] = {"本物": _mean(tp_rows, k), "ダマシ": _mean(sl_rows, k)}

    summary = {"n": n, "tp": tp, "sl": sl, "time": tm,
               "tp_rate": round(100.0 * tp / n, 1), "avg_r": round(avg_r, 3),
               "by_zone": by_zone,
               "feature_split": feature_split,
               "tp_n": len(tp_rows), "sl_n": len(sl_rows)}
    return {"trades": rows[-40:], "summary": summary}


PAPER_V3 = os.path.join(HERE, "paper_ledger_v3.jsonl")


def build_paper_v3():
    """車線3 v3a(品質壁＋採点)の集計。全候補 / TAKE / SKIP を比較（採点が効くか）。"""
    rows = []
    try:
        for line in open(PAPER_V3, encoding="utf-8"):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    except Exception:
        rows = []
    if not rows:
        return {"summary": {"n": 0}, "trades": []}

    def grp(rs):
        if not rs:
            return {"n": 0}
        tp = sum(1 for r in rs if r.get("exit_reason") == "TP")
        return {"n": len(rs), "tp_rate": round(100.0 * tp / len(rs), 1),
                "avg_r": round(sum(r.get("R", 0) for r in rs) / len(rs), 3)}

    take = [r for r in rows if r.get("decision") == "TAKE"]
    skip = [r for r in rows if r.get("decision") == "SKIP"]
    return {"summary": {"n": len(rows), "all": grp(rows),
                        "take": grp(take), "skip": grp(skip)},
            "trades": rows[-300:]}


# ── 会長が引いた水平線（AURELが読める共有ファイル。チャットで「白線見て」に応えるための正本）──
USER_LINES = os.path.join(HERE, "user_lines.json")


def load_lines():
    try:
        with open(USER_LINES, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"lines": []}


def save_lines(lines):
    clean = []
    for L in (lines or []):
        try:
            clean.append({"id": str(L.get("id")),
                          "price": round(float(L["price"]), 3),
                          "color": str(L.get("color", "#ffffff"))[:16],
                          "width": int(L.get("width", 2)),
                          "label": str(L.get("label", ""))[:40]})
        except Exception:
            continue
    with open(USER_LINES, "w", encoding="utf-8") as f:
        json.dump({"lines": clean, "updated": time.strftime("%Y-%m-%d %H:%M:%S")},
                  f, ensure_ascii=False, indent=1)


class H(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            p = self.path.split("?")[0]
            if p == "/" or p == "/index.html":
                with open(PAGE, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif p == "/lightweight-charts.js":
                with open(LIB, "rb") as f:
                    self._send(200, f.read(), "application/javascript; charset=utf-8")
            elif p == "/api/data":
                from urllib.parse import urlparse, parse_qs
                q = parse_qs(urlparse(self.path).query)
                n = int((q.get("n") or ["1500"])[0])
                n = max(50, min(5000, n))
                data = build_data(n)
                self._send(200, json.dumps(data, ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/tick":
                self._send(200, json.dumps(build_tick(), ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/trades":
                self._send(200, json.dumps(build_trades(), ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/paper":
                self._send(200, json.dumps(build_paper(), ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/paperv3":
                self._send(200, json.dumps(build_paper_v3(), ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/lines":
                self._send(200, json.dumps(load_lines(), ensure_ascii=False), "application/json; charset=utf-8")
            else:
                self._send(404, "not found", "text/plain; charset=utf-8")
        except Exception as e:
            self._send(500, "err: %s" % e, "text/plain; charset=utf-8")

    def do_POST(self):
        try:
            p = self.path.split("?")[0]
            if p == "/api/lines":
                n = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(n).decode("utf-8") if n else "{}"
                data = json.loads(body)
                save_lines(data.get("lines", []))
                self._send(200, json.dumps({"ok": True}), "application/json; charset=utf-8")
            else:
                self._send(404, "not found", "text/plain; charset=utf-8")
        except Exception as e:
            self._send(500, "err: %s" % e, "text/plain; charset=utf-8")

    def log_message(self, *a):
        pass


class Threaded(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = False   # Windowsの二重バインド回避（2つ目は明確に失敗させる）


if __name__ == "__main__":
    # 毎秒ティックと重いフル取得(1500本)が並行して来ても詰まらないようスレッド化。
    # MT5読取は _LOCK で直列化しているのでAPI非スレッド安全でも安全。
    srv = Threaded((HOST, PORT), H)
    print("壁→壁 ライブチャート on http://%s:%d/ (/api/data?n=1500, /api/tick)" % (HOST, PORT))
    srv.serve_forever()
