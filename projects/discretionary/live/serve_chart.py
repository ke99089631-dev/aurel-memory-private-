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


def latest_ai_position(tick):
    """AURELの現在の建玉（setup_ledger の status=open）を今の価格で追跡して返す。無ければ None。"""
    try:
        recs = _load_setups()
    except Exception:
        return None
    opens = [r for r in recs if r.get("status") == "open" and r.get("entry") is not None]
    if not opens:
        return None
    last = opens[-1]
    entry = last["entry"]; sl = last["sl"]; tp = last["tp"]; side = last["side"]
    risk = abs(entry - sl) or 1e-9
    price = ((tick["bid"] + tick["ask"]) / 2.0) if tick else entry
    live_r = ((entry - price) if side == "SELL" else (price - entry)) / risk
    return {
        "id": last.get("id"), "side": side, "entry": entry, "sl": sl, "tp": tp,
        "entry_time": int(last["entry_time"]), "entry_jst": last.get("entry_jst"),
        "wall": last.get("wall"), "width": last.get("pool"),
        "real_rate": (last.get("pred") or {}).get("p_real"),
        "reason": (last.get("pred") or {}).get("reason", ""),
        "open": True, "live_r": round(live_r, 2),
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
    # ① 壁の動的組み直し（トレンドでも箱が置いてけぼりにならず段階的に乗り換わる）。
    import wallbox
    box, brk = wallbox.dynamic_box(m5)
    if box is None:
        box, brk = fixed_box_and_break(m5)     # 予備1: 帯無しなら強壁固定
    if box is None:
        box = chart_gen.current_box(m5); brk = None  # 予備2: 旧ローリング
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
                    # 会長の眼（カード v1 の主観タグ）＝収束ループの入力
                    "feel": r.get("feel") or "", "env": r.get("env") or "",
                    "pre": bool(r.get("pre")), "tags": _card_tags(r.get("note") or ""),
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
                more = _card_tags(r.get("note") or "")
                if more:
                    t["tags"].update(more)
    return {"trades": [trades[t] for t in order]}


PHONE_DIR = r"C:\Users\user\.aurel\phone"


def build_stats():
    """会長の現状成績（台帳の集計）。計算は検証室(aurel_trade_room.stats)をそのまま使う＝チャットの『成績:』行と同じ数字。
       閾値(30本/100本)や除外規則(未執行)を二重に持たない。"""
    try:
        if PHONE_DIR not in sys.path:
            sys.path.insert(0, PHONE_DIR)
        import importlib
        import aurel_trade_room as tr
        importlib.reload(tr)                       # 検証室側の修正を再起動なしで拾う
        recs = tr.load_records()
        trades = tr.effective(recs)
        st = tr.stats(trades)
        # 成績に数えるカード＝stats と同じ除外（未執行は落とす）
        counted = [t for t in trades if not str(t.get("post") or "").startswith("未執行")]
        recent = []
        for t in counted:
            recent.append({"id": t["id"], "side": t.get("side"), "R": t.get("R"),
                           "post": t.get("post") or "", "pre": bool(t.get("pre")),
                           "ts": (t.get("ts") or "")[5:16].replace("T", " ")})
        st["recent"] = recent[-8:]
        st["open_ids"] = [t["id"] for t in counted if t.get("R") is None]
        st["losses"] = st["closed"] - st["wins"]
        return {"ok": True, "stats": st, "ledger_mtime": os.path.getmtime(LEDGER) if os.path.exists(LEDGER) else None}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _card_tags(note):
    """note 内の固定フォーマット「質=… / 種別=… / 余地=…」を拾う（無ければ空）。"""
    import re
    tags = {}
    for key in ("質", "種別", "余地", "感触", "環境"):
        m = re.search(key + r"\s*[=＝]\s*([^/／\n]+)", note)
        if m:
            tags[key] = m.group(1).strip()
    return tags


# ── 収束ループ: AURELのセットアップ記録（setup_engine.py が書く台帳）──
SETUP_LEDGER = os.path.join(HERE, "setup_ledger.jsonl")


def _load_setups():
    """setup_ledger.jsonl を統合（setup + update）して時系列で返す。"""
    recs, order = {}, []
    if not os.path.exists(SETUP_LEDGER):
        return []
    for line in open(SETUP_LEDGER, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("kind") == "setup":
            recs[r["id"]] = r; order.append(r["id"])
        elif r.get("kind") == "update":
            t = recs.get(r.get("target"))
            if t:
                for k, v in r.items():
                    if k not in ("kind", "target", "logged_at"):
                        t[k] = v
    return [recs[i] for i in order]


def _confidence(n):
    if n < 30:
        return "低（サンプル不足・手順固定は30本）"
    if n < 100:
        return "中（優位性判定は+0.2Rなら約100本）"
    return "高"


def build_setups(tick=None):
    """AIのセットアップ一覧＋会長トレードの自動紐付け＋予測vs実測の較正。"""
    recs = _load_setups()
    trades = build_trades()["trades"]
    price = ((tick["bid"] + tick["ask"]) / 2.0) if tick else None
    # 会長の実トレードを近いセットアップに紐付け（同方向・時間差≤4h・壁の近く）
    for t in trades:
        if t.get("entry_time") is None or t.get("entry") is None:
            continue
        best, bd = None, 1e18
        for s in recs:
            if s.get("side") != t.get("side"):
                continue
            dtm = t["entry_time"] - s["break_time"]
            if dtm < -3600 or dtm > 4 * 3600:
                continue
            if abs(t["entry"] - s["wall"]) > max(1.5 * s.get("pool", 0), 10.0):
                continue
            if abs(dtm) < bd:
                best, bd = s, abs(dtm)
        if best is not None:
            best["chairman"] = {"id": t["id"], "feel": t.get("feel"), "env": t.get("env"),
                                "post": t.get("post"), "pre": t.get("pre"), "tags": t.get("tags", {}),
                                "entry": t.get("entry"), "sl": t.get("sl"), "tp": t.get("tp"),
                                "exit": t.get("exit")}
    # ライブR（建玉中）
    for s in recs:
        if s.get("status") == "open" and price is not None and s.get("entry") is not None:
            risk = abs(s["entry"] - s["sl"]) or 1e-9
            s["live_r"] = round(((s["entry"] - price) if s["side"] == "SELL" else (price - s["entry"])) / risk, 2)

    closed = [s for s in recs if s.get("status") == "closed"]
    n = len(closed)

    def grp(rs):
        if not rs:
            return {"n": 0}
        tp = sum(1 for r in rs if r.get("exit_reason") == "TP")
        preds = [r["pred"]["p_real"] for r in rs if (r.get("pred") or {}).get("p_real") is not None]
        return {"n": len(rs), "tp_rate": round(100.0 * tp / len(rs), 1),
                "avg_r": round(sum(r.get("R", 0) for r in rs) / len(rs), 3),
                "pred_rate": round(sum(preds) / len(preds), 1) if preds else None,
                "avg_mfe": round(sum(r.get("mfe_R", 0) for r in rs) / len(rs), 2)}

    chase = [r["chase"] for r in recs if (r.get("chase") or {}).get("status") == "closed"]
    linked = [s for s in recs if s.get("chairman")]
    agree = 0
    for s in linked:
        post = (s["chairman"].get("post") or "")
        if s.get("outcome") and post:
            if (post == "ダマシ" and s["outcome"] == "ダマシ") or (post != "ダマシ" and s["outcome"] != "ダマシ"):
                agree += 1
    summary = {
        "n_setups": len(recs), "n_closed": n,
        "status": {k: sum(1 for r in recs if r.get("status") == k)
                   for k in ("open", "closed", "waiting", "no_retest", "invalid")},
        "all": grp(closed),
        "outer": grp([r for r in closed if r.get("wall_kind") == "outer"]),
        "mid": grp([r for r in closed if r.get("wall_kind") == "mid"]),
        "by_zone": {z: grp([r for r in closed if r.get("zone") == z]) for z in ("本物帯", "中立", "ダマシ巣")},
        "chase": grp(chase),
        "linked": len(linked), "agree": agree,
        "confidence": _confidence(n),
    }
    recs.sort(key=lambda r: int(r.get("break_time") or 0))     # 表示は時系列（IDの順ではなく）
    return {"setups": recs[-120:], "summary": summary}


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
            elif p == "/api/stats":
                self._send(200, json.dumps(build_stats(), ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/paper":
                self._send(200, json.dumps(build_paper(), ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/paperv3":
                self._send(200, json.dumps(build_paper_v3(), ensure_ascii=False), "application/json; charset=utf-8")
            elif p == "/api/setups":
                tick = None
                try:
                    tick = build_tick().get("tick")
                except Exception:
                    tick = None
                self._send(200, json.dumps(build_setups(tick), ensure_ascii=False), "application/json; charset=utf-8")
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
