# -*- coding: utf-8 -*-
"""
車線3 収束ループ・エンジン（スナイパースコープの土台）。発注なし・金ゼロ・読取のみ。
  1ブレイク = 1「セットアップ記録」。チャートと同じ壁(wallbox.dynamic_box)で、
    ・外壁ブレイク(黄) / 中間ブレイク(青) を検出
    ・AURELの予測（本物率＝時間帯統計・TP推定＝溜まり幅・理由）を"先に"記録
    ・戻り目(壁リテスト)でエントリー → TP/SL/時間切れ を追跡 → R・最大含み益(MFE)・最大含み損(MAE)
    ・「抜けで即追う」変種(chase)も同じSL/TPで並走記録（会長の"種別"の材料）
    ・検証機が見ない特徴（ブレイク足の勢い/実体/反発ヒゲ/壁タッチ数/溜まりの締まり）
  台帳 setup_ledger.jsonl は追記のみ（kind=setup / kind=update）。会長の実(車線1)とは絶対に混ぜない。
  サーバ(/api/setups)が会長のカード(ledger.jsonl)と自動で紐付け＝両者の予測を1記録に収束させる。
  先読みなし: 各バーの判断はそれ以前のバーだけで壁を計算。形成中の最終バーは使わない。
"""
import os
import sys
import json
import time
import datetime as dt
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import pandas as pd
import wallbox
from wallbox import pool_width, SL_PAD_FR

API = "http://100.73.107.61:8793/api/data?n=2000"   # サーバは Tailscale IP のみ bind
LEDGER = os.path.join(HERE, "setup_ledger.jsonl")
DAMASHI_FILE = os.path.join(HERE, "damashi_hour_jst.json")
INTERVAL = 120          # 2分ごと（M5の確定足を拾う）
RETRACE_BARS = 12       # 戻り目を待つ本数（1時間）
MAX_HOLD = 288          # 最長保有（24h）
MID_POOL_BARS = 6       # 中間ブレイク認定: 直前この本数の終値が全て反対側（溜まりがあった）
COOLDOWN = 3


def _load_damashi():
    try:
        with open(DAMASHI_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _fetch_bars():
    with urllib.request.urlopen(API, timeout=25) as r:
        d = json.loads(r.read().decode("utf-8"))
    bars = d.get("bars", [])
    if len(bars) < 2:
        return None
    bars = bars[:-1]                      # 形成中の最終バーは使わない（判断が揺れないように）
    df = pd.DataFrame(bars)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.set_index("dt")[["open", "high", "low", "close"]]


def _zone(jh):
    return "本物帯" if 7 <= jh < 12 else ("ダマシ巣" if 0 <= jh < 5 else "中立")


def _features(o, h, l, c, i, wall, pool, direction):
    """ブレイク足 i の客観特徴（検証機が記録しない質・文脈）。"""
    n0 = max(0, i - 100)
    trs = [h[k] - l[k] for k in range(max(1, i - 14), i)]
    atr = float(np.mean(trs)) if trs else 0.0
    rng = h[i] - l[i]; body = abs(c[i] - o[i])
    body_ratio = round(body / rng, 3) if rng > 0 else 0.0
    mom = round((c[i] - c[max(0, i - 20)]) / c[i] * 100, 3) if i >= 20 else 0.0
    tol = max(0.1 * pool, 0.3)
    if direction == "DOWN":
        touches = int(sum(1 for k in range(n0, i) if abs(l[k] - wall) <= tol))
    else:
        touches = int(sum(1 for k in range(n0, i) if abs(h[k] - wall) <= tol))
    s0 = max(0, i - 30)
    tight = round(float(np.std(c[s0:i])) / c[i] * 100, 3) if i > s0 else 0.0
    # 抜けた深さ（終値が壁からどれだけ外か、溜まり幅比）
    depth = round(abs(c[i] - wall) / pool, 3) if pool > 0 else 0.0
    return {
        "break_str_atr": round(rng / atr, 2) if atr > 0 else 0.0,
        "break_body_ratio": body_ratio,
        "break_depth_pool": depth,
        "momentum20_pct": mom,
        "wall_touches": touches,
        "tightness_pct": tight,
        "atr14": round(atr, 3),
    }


def _simulate(o, h, l, c, ie, side, entry, sl, tp, n):
    """ie から前進。TP/SL/TIME。MFE/MAE(R)も。未決着なら status=open。"""
    risk = abs(entry - sl)
    k_end = min(ie + MAX_HOLD, n - 1)
    mfe = mae = 0.0
    exit_px = reason = None; exit_k = None
    for k in range(ie, k_end + 1):
        if side == "SELL":
            fav = (entry - l[k]) / risk; adv = (h[k] - entry) / risk
        else:
            fav = (h[k] - entry) / risk; adv = (entry - l[k]) / risk
        mfe = max(mfe, fav); mae = max(mae, adv)
        if side == "SELL":
            if h[k] >= sl: exit_px, reason, exit_k = sl, "SL", k; break
            if l[k] <= tp: exit_px, reason, exit_k = tp, "TP", k; break
        else:
            if l[k] <= sl: exit_px, reason, exit_k = sl, "SL", k; break
            if h[k] >= tp: exit_px, reason, exit_k = tp, "TP", k; break
    if exit_px is None:
        if ie + MAX_HOLD <= n - 1:
            exit_k = k_end; exit_px = c[k_end]; reason = "TIME"
        else:
            return {"status": "open", "mfe_R": round(mfe, 2), "mae_R": round(mae, 2),
                    "hold_bars": (n - 1) - ie}
    pnl = (exit_px - entry) if side == "BUY" else (entry - exit_px)
    return {"status": "closed", "exit": round(float(exit_px), 3), "exit_reason": reason,
            "exit_k": exit_k, "R": round(pnl / risk, 3),
            "mfe_R": round(mfe, 2), "mae_R": round(mae, 2), "hold_bars": exit_k - ie}


def scan(m5, dm):
    """過去→現在へ一方向に走査し、セットアップ記録の列を返す（先読みなし・確定的）。"""
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    idx = m5.index; n = len(c)
    out = []
    i = wallbox.WALL_WIN
    cooldown_until = -1
    while i < n:
        if i <= cooldown_until:
            i += 1; continue
        win = m5.iloc[max(0, i - wallbox.WALL_WIN):i]          # バー i より前だけ
        box, _ = wallbox.dynamic_box(win)
        if box is None:
            i += 1; continue
        up, dn, mid = box["up"], box["dn"], box["mid"]
        ev = None
        if c[i] < dn and c[i - 1] >= dn:
            ev = ("DOWN", "outer", dn)
        elif c[i] > up and c[i - 1] <= up:
            ev = ("UP", "outer", up)
        elif dn < c[i] < up and i >= MID_POOL_BARS:
            prev = c[i - MID_POOL_BARS:i]
            if c[i] > mid and np.all(prev <= mid):
                ev = ("UP", "mid", mid)
            elif c[i] < mid and np.all(prev >= mid):
                ev = ("DOWN", "mid", mid)
        if ev is None:
            i += 1; continue
        direction, kind, wall = ev
        if kind == "outer":
            pool = pool_width(dn, mid, up, direction)
        else:
            pool = (up - mid) if direction == "UP" else (mid - dn)   # 中間抜け＝反対側の溜まり(外壁まで)
        if pool <= 0:
            i += 1; continue
        side = "SELL" if direction == "DOWN" else "BUY"
        if direction == "DOWN":
            sl = wall + pool * SL_PAD_FR; tp = wall - pool
        else:
            sl = wall - pool * SL_PAD_FR; tp = wall + pool
        bt = int(pd.Timestamp(idx[i]).timestamp())
        jst = pd.Timestamp(idx[i]).tz_convert("Asia/Tokyo")
        jh = int(jst.hour)
        hrec = (dm.get("hours") or {}).get(str(jh)) if dm else None
        real_rate = hrec["tp_rate"] if hrec else dm.get("base_tp_rate") if dm else None
        feats = _features(o, h, l, c, i, wall, pool, direction)
        s = {
            "break_time": bt, "break_jst": jst.strftime("%Y-%m-%d %H:%M"),
            "dir": direction, "side": side, "wall_kind": kind,
            "wall": round(float(wall), 3), "pool": round(float(pool), 3),
            "up": round(float(up), 3), "dn": round(float(dn), 3), "mid": round(float(mid), 3),
            "sl": round(float(sl), 3), "tp": round(float(tp), 3),
            "jst_hour": jh, "zone": _zone(jh),
            "pred": {  # ★AURELの事前予測（結果を見る前に固定）
                "p_real": real_rate, "p_source": "時間帯統計(機械n=6108)",
                "tp_est": round(float(tp), 3), "tp_rule": "溜まり幅1個(壁↔中間)",
                "reason": "%s %sブレイク JST%d時(%s) 本物率%s%% 溜まり%.1f 壁タッチ%d 抜け%.2f" % (
                    "下" if direction == "DOWN" else "上", "外壁" if kind == "outer" else "中間",
                    jh, _zone(jh), ("%.0f" % real_rate) if real_rate is not None else "?",
                    pool, feats["wall_touches"], feats["break_depth_pool"]),
            },
            "features": feats,
            "status": "waiting", "entry_mode": "retest",
        }
        # 追いかけ変種（抜けた足の終値で即エントリー）
        ch_entry = float(c[i])
        ok_ch = (sl > ch_entry > tp) if side == "SELL" else (tp > ch_entry > sl)
        if ok_ch and i + 1 <= n - 1:
            r = _simulate(o, h, l, c, i + 1, side, ch_entry, sl, tp, n)
            s["chase"] = {"entry": round(ch_entry, 3), "status": r["status"],
                          "exit_reason": r.get("exit_reason"), "R": r.get("R"),
                          "mfe_R": r["mfe_R"], "mae_R": r["mae_R"]}
        else:
            s["chase"] = {"entry": round(ch_entry, 3), "status": "invalid"}

        # 戻り目（壁リテスト）待ち
        j_enter = None
        j_last = min(i + RETRACE_BARS, n - 1)
        for j in range(i + 1, j_last + 1):
            if direction == "DOWN" and h[j] >= wall:
                j_enter = j; break
            if direction == "UP" and l[j] <= wall:
                j_enter = j; break
        exit_k = None
        if j_enter is None:
            s["status"] = "waiting" if (i + RETRACE_BARS > n - 1) else "no_retest"
        else:
            ie = j_enter + 1
            if ie > n - 1:
                s["status"] = "waiting"
            else:
                entry = float(o[ie])
                ok = (sl > entry > tp) if side == "SELL" else (tp > entry > sl)
                # エントリー足の反発ヒゲ（壁での拒否の強さ）
                rng = h[ie] - l[ie]
                wick = (h[ie] - max(o[ie], c[ie])) if side == "SELL" else (min(o[ie], c[ie]) - l[ie])
                s["features"]["reject_wick_ratio"] = round(wick / rng, 3) if rng > 0 else 0.0
                s["entry"] = round(entry, 3)
                s["entry_time"] = int(pd.Timestamp(idx[ie]).timestamp())
                s["entry_jst"] = pd.Timestamp(idx[ie]).tz_convert("Asia/Tokyo").strftime("%Y-%m-%d %H:%M")
                if not ok:
                    s["status"] = "invalid"      # 戻りが深すぎ＝ブレイク失敗（入る前にダマシ確定）
                else:
                    r = _simulate(o, h, l, c, ie, side, entry, sl, tp, n)
                    s["status"] = r["status"]
                    s["mfe_R"] = r["mfe_R"]; s["mae_R"] = r["mae_R"]; s["hold_bars"] = r["hold_bars"]
                    if r["status"] == "closed":
                        exit_k = r["exit_k"]
                        s["exit"] = r["exit"]; s["exit_reason"] = r["exit_reason"]; s["R"] = r["R"]
                        s["exit_time"] = int(pd.Timestamp(idx[exit_k]).timestamp())
                        s["outcome"] = "本物" if r["exit_reason"] == "TP" else (
                            "ダマシ" if r["exit_reason"] == "SL" else "時間切れ")
        out.append(s)
        if s["status"] == "open":
            break                                   # 建玉中は次を探さない（1建玉）
        if s["status"] == "closed":
            i = exit_k + 1
        elif s["status"] == "waiting":
            i += 1
        else:
            cooldown_until = i + COOLDOWN; i += 1
    return out


def _key(s):
    return "%d|%s|%s" % (int(s["break_time"]), s["dir"], s["wall_kind"])


def load_state():
    """台帳を統合（setup + update）。key→record。"""
    recs, by_key, maxn = {}, {}, 0
    if os.path.exists(LEDGER):
        for line in open(LEDGER, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") == "setup":
                recs[r["id"]] = r
                by_key[_key(r)] = r["id"]
                try:
                    maxn = max(maxn, int(r["id"].split("-")[1]))
                except Exception:
                    pass
            elif r.get("kind") == "update":
                t = recs.get(r.get("target"))
                if t:
                    for k, v in r.items():
                        if k not in ("kind", "target", "logged_at"):
                            t[k] = v
    return recs, by_key, maxn


UPDATE_FIELDS = ("status", "entry", "entry_time", "entry_jst", "exit", "exit_time", "exit_reason",
                 "R", "mfe_R", "mae_R", "hold_bars", "outcome", "chase", "features")


def sync_once():
    dm = _load_damashi()
    m5 = _fetch_bars()
    if m5 is None or len(m5) < wallbox.WALL_WIN + 20:
        return 0, 0
    setups = scan(m5, dm)
    recs, by_key, maxn = load_state()
    added = updated = 0
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LEDGER, "a", encoding="utf-8") as f:
        for s in setups:
            k = _key(s)
            if k not in by_key:
                maxn += 1
                rec = {"id": "S-%04d" % maxn, "kind": "setup", "lane": "3", "logged_at": now}
                rec.update(s)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                by_key[k] = rec["id"]; recs[rec["id"]] = rec
                added += 1
            else:
                old = recs[by_key[k]]
                if old.get("status") == "closed":
                    continue                       # 決着済みは触らない
                if old.get("status") != s["status"] or (
                        s["status"] == "open" and old.get("entry") != s.get("entry")):
                    upd = {"kind": "update", "target": old["id"], "logged_at": now}
                    for fld in UPDATE_FIELDS:
                        if fld in s:
                            upd[fld] = s[fld]
                    f.write(json.dumps(upd, ensure_ascii=False) + "\n")
                    old.update(upd)
                    updated += 1
    return added, updated


def main():
    print("車線3 収束ループ・エンジン起動（2分ごと・発注なし・金ゼロ）", flush=True)
    while True:
        try:
            a, u = sync_once()
            if a or u:
                print("%s +%d 新規 / %d 更新" % (dt.datetime.now().strftime("%H:%M:%S"), a, u), flush=True)
        except Exception as e:
            sys.stderr.write("sync err: %s\n" % e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    if "--once" in sys.argv:
        print("新規/更新:", sync_once())
    else:
        main()
