# -*- coding: utf-8 -*-
"""
②足の時間軸 前向き紙レーン（会長GO 2026-11-02）。5分と15分を同じエンジンで並走記録＝「15分なら？」をOOSで比較。
  発注なし・金ゼロ・読取のみ。会長の裁量台帳とは絶対に混ぜない。

背景: `research/wall_to_wall/tf_compare.py` の過去計測で、15分で壁を取ると近年ヒゲ抜けの騙しが減り
  本物率8→12%・勝率17→26%・平均R-0.025→+0.145・最大DD-145→-42R。ただし未有意・2022-23は逆・研究用の型。
  過去で良くても前で崩れることがある(再加速16年)ので前向きで確かめる。関門=各足 確定30本で中間報告。

★事前固定（tf_compare と同一・結果を見て動かさない）:
  箱=24時間の高安(現バー除外)。幅<10除外。band=幅×8%。ブレイク=終値が壁の外・同方向は時間で6本dedup。
  リテスト=ブレイク後1時間以内に割った壁(±band)へ戻る最初の足。
  再加速確認=リテスト後15分以内に終値が再び継続側→次足始値で建玉。
  SL=リテスト極値の外+0.20 / TP=メジャードムーブ(壁±幅1個) / リスク<3は不成立 / 時間切れ24時間 / netR=R−0.56/リスク。
  5分: 箱288・リテスト12・確認3・時間切れ288・dedup6。15分: 箱96・リテスト4・確認1・時間切れ96・dedup2。
  前向き開始=初回起動時刻。過去のブレイクは記録しない(OOS)。
データ源=8793 /api/data(2000本・形成中の最終バー除外→5分は束ねて15分も作る)。台帳 tf_ledger.jsonl 追記のみ(kind=tf/update)。
"""
import os, sys, json, time
import datetime as dt
import urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import pandas as pd

API = "http://100.73.107.61:8793/api/data?n=2000"
LEDGER = os.path.join(HERE, "tf_ledger.jsonl")
STATE = os.path.join(HERE, "tf_lane_state.json")
INTERVAL = 30
WIDTH_MIN = 10.0; BAND = 0.08
SL_PAD = 0.20; RISK_MIN = 3.0; COST = 0.56
TARGET = 30
JST = dt.timezone(dt.timedelta(hours=9))


def tf_params(bar_min):
    bph = 60 // bar_min
    return dict(bar_min=bar_min, bph=bph, BOX=24 * bph, RETEST=bph,
                CONF=max(1, 15 // bar_min), HOLD=24 * bph, DEDUP=max(1, bph // 2))


def _now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _jst(epoch):
    return dt.datetime.fromtimestamp(int(epoch), JST).strftime("%Y-%m-%d %H:%M")


def _zone(epoch):
    jh = dt.datetime.fromtimestamp(int(epoch), JST).hour
    return "本物帯" if 7 <= jh < 12 else ("ダマシ巣" if 0 <= jh < 5 else "中立")


def _fetch_5m():
    with urllib.request.urlopen(API, timeout=25) as r:
        d = json.loads(r.read().decode("utf-8"))
    bars = d.get("bars", [])
    if len(bars) < 320:
        return None
    return bars[:-1]                        # 形成中の最終バーは使わない


def _resample(bars5, bar_min):
    if bar_min == 5:
        rows = [(b["time"], b["open"], b["high"], b["low"], b["close"]) for b in bars5]
    else:
        slot = bar_min * 60
        cur = None; rows = []
        for b in bars5:
            s = b["time"] - (b["time"] % slot)
            if cur is None or cur[0] != s:
                if cur is not None: rows.append(tuple(cur))
                cur = [s, b["open"], b["high"], b["low"], b["close"]]
            else:
                cur[2] = max(cur[2], b["high"]); cur[3] = min(cur[3], b["low"]); cur[4] = b["close"]
        if cur is not None: rows.append(tuple(cur))
    t = np.array([r[0] for r in rows]); o = np.array([r[1] for r in rows], float)
    h = np.array([r[2] for r in rows], float); l = np.array([r[3] for r in rows], float)
    c = np.array([r[4] for r in rows], float)
    return t, o, h, l, c


def load_ledger():
    recs, order = {}, []
    if os.path.exists(LEDGER):
        for ln in open(LEDGER, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if r.get("kind") == "tf":
                recs[r["id"]] = r; order.append(r["id"])
            elif r.get("kind") == "update":
                t = recs.get(r.get("target"))
                if t:
                    for k, v in r.items():
                        if k not in ("kind", "target", "logged_at"): t[k] = v
    return recs, order


def load_state():
    try: return json.load(open(STATE, encoding="utf-8"))
    except Exception: return {}


def save_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"))


def _write(f, rec): f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _update(f, rec, **fields):
    upd = {"kind": "update", "target": rec["id"], "logged_at": _now()}
    upd.update(fields); _write(f, upd); rec.update(fields)


def scan_breaks(t, o, h, l, c, P):
    """ブレイク事件を列挙（事件ごとに index i・dir・wall・width）。先読みなし。"""
    n = len(c); BOX = P["BOX"]
    up = pd.Series(h).rolling(BOX).max().shift(1).to_numpy()
    dn = pd.Series(l).rolling(BOX).min().shift(1).to_numpy()
    last_b = {+1: -10**9, -1: -10**9}; out = []
    for i in range(BOX + 1, n):
        if not (np.isfinite(up[i]) and np.isfinite(dn[i])): continue
        w = up[i] - dn[i]
        if w < WIDTH_MIN: continue
        for dirn, wall in ((+1, up[i]), (-1, dn[i])):
            broke = (c[i] > wall) if dirn == +1 else (c[i] < wall)
            if not broke: continue
            if i - last_b[dirn] <= P["DEDUP"]: continue
            last_b[dirn] = i
            out.append(dict(i=i, dir=dirn, wall=float(wall), width=float(w), btime=int(t[i])))
    return out


def advance(rec, t, o, h, l, c, pos, P, f):
    """1記録を今の足まで前進。break→retest→open→closed(＋終端 no_retest/no_resume/skip_*/lost)。"""
    n = len(c); dirn = rec["dir"]; wall = rec["wall"]; w = rec["width"]
    bi = pos.get(int(rec["btime"]))
    if bi is None:
        if rec.get("status") in ("break", "retest", "open"):
            _update(f, rec, status="lost", note="ブレイク足が取得窓から外れた")
        return
    band = w * BAND
    if rec.get("status") == "break":
        r = None
        for k in range(bi + 1, min(n, bi + 1 + P["RETEST"])):
            back = (l[k] <= wall + band) if dirn == +1 else (h[k] >= wall - band)
            if back: r = k; break
        if r is None:
            if n - 1 >= bi + P["RETEST"]:
                _update(f, rec, status="no_retest")
            return
        rlo = float(min(l[bi + 1:r + 1])); rhi = float(max(h[bi + 1:r + 1]))
        _update(f, rec, status="retest", rtime=int(t[r]), rjst=_jst(t[r]), rlo=rlo, rhi=rhi)
    if rec.get("status") == "retest":
        ri = pos.get(int(rec["rtime"]))
        if ri is None:
            _update(f, rec, status="lost", note="リテスト足が窓外"); return
        conf = None
        for k in range(ri + 1, min(n, ri + 1 + P["CONF"])):
            resume = (c[k] > wall) if dirn == +1 else (c[k] < wall)
            if resume: conf = k; break
        if conf is None:
            if n - 1 >= ri + P["CONF"]:
                _update(f, rec, status="no_resume")
            return
        if conf + 1 >= n:
            return                                  # 確認は出たが建玉足が未確定
        ent = conf + 1; entry = float(o[ent])
        sl = (rec["rlo"] - SL_PAD) if dirn == +1 else (rec["rhi"] + SL_PAD)
        risk = (entry - sl) if dirn == +1 else (sl - entry)
        tp = (wall + w) if dirn == +1 else (wall - w)
        reward = (tp - entry) if dirn == +1 else (entry - tp)
        base = dict(entry=round(entry, 3), sl=round(sl, 3), tp=round(tp, 3), risk=round(risk, 3),
                    entry_time=int(t[ent]), entry_jst=_jst(t[ent]), rr=round(reward / risk, 2) if risk > 0 else None)
        if risk < RISK_MIN: _update(f, rec, status="skip_risk", **base); return
        if reward <= 0: _update(f, rec, status="skip_reward", **base); return
        _update(f, rec, status="open", mfe_R=0.0, mae_R=0.0, hold_bars=0, **base)
    if rec.get("status") == "open":
        ent = pos.get(int(rec["entry_time"]))
        if ent is None: _update(f, rec, status="lost", note="建玉足が窓外"); return
        entry = rec["entry"]; sl = rec["sl"]; tp = rec["tp"]; risk = rec["risk"]
        mfe = rec.get("mfe_R", 0.0); mae = rec.get("mae_R", 0.0)
        exit_px = None; reason = None; kx = None
        for k in range(ent, n):
            fav = ((h[k] - entry) if dirn == +1 else (entry - l[k])) / risk
            adv = ((entry - l[k]) if dirn == +1 else (h[k] - entry)) / risk
            mfe = max(mfe, fav); mae = max(mae, adv)
            if dirn == +1:
                if l[k] <= sl: exit_px, reason, kx = sl, "SL", k; break
                if h[k] >= tp: exit_px, reason, kx = tp, "TP", k; break
            else:
                if h[k] >= sl: exit_px, reason, kx = sl, "SL", k; break
                if l[k] <= tp: exit_px, reason, kx = tp, "TP", k; break
            if k - ent + 1 >= P["HOLD"]:
                exit_px, reason, kx = float(c[k]), "TIME", k; break
        hold = (kx - ent + 1) if kx is not None else (n - ent)
        if exit_px is None:
            if hold != rec.get("hold_bars") or round(mfe, 2) != rec.get("mfe_R") or round(mae, 2) != rec.get("mae_R"):
                _update(f, rec, mfe_R=round(mfe, 2), mae_R=round(mae, 2), hold_bars=int(hold))
            return
        R = ((exit_px - entry) if dirn == +1 else (entry - exit_px)) / risk
        _update(f, rec, status="closed", exit=round(float(exit_px), 3), exit_reason=reason,
                exit_time=int(t[kx]), exit_jst=_jst(t[kx]), hold_bars=int(hold),
                mfe_R=round(mfe, 2), mae_R=round(mae, 2), R=round(R, 3), netR=round(R - COST / risk, 3))


def sync_once():
    bars5 = _fetch_5m()
    if bars5 is None:
        return 0, 0
    recs, order = load_ledger()
    st = load_state()
    if "lane_start" not in st:
        st["lane_start"] = int(bars5[-1]["time"])     # 前向き開始＝初回の最新確定足
    start = int(st["lane_start"])
    maxn = 0
    for rid in order:
        try: maxn = max(maxn, int(rid.split("-")[1]))
        except Exception: pass
    by_key = {(recs[i]["tf"], int(recs[i]["btime"]), recs[i]["dir"]): i for i in order}
    added = 0
    before = {rid: recs[rid].get("status") for rid in order}
    with open(LEDGER, "a", encoding="utf-8") as f:
        for bar_min in (5, 15):
            P = tf_params(bar_min)
            t, o, h, l, c = _resample(bars5, bar_min)
            if len(c) < P["BOX"] + 5: continue
            pos = {int(t[i]): i for i in range(len(t))}
            for ev in scan_breaks(t, o, h, l, c, P):
                if ev["btime"] < start: continue       # OOS: 開始前のブレイクは入れない
                key = (bar_min, ev["btime"], ev["dir"])
                if key in by_key: continue
                maxn += 1
                rec = {"id": "TF-%04d" % maxn, "kind": "tf", "tf": bar_min, "logged_at": _now(),
                       "btime": ev["btime"], "bjst": _jst(ev["btime"]), "dir": ev["dir"],
                       "side": "BUY" if ev["dir"] == +1 else "SELL",
                       "wall": round(ev["wall"], 3), "width": round(ev["width"], 3),
                       "zone": _zone(ev["btime"]), "status": "break"}
                _write(f, rec); recs[rec["id"]] = rec; order.append(rec["id"]); by_key[key] = rec["id"]
                added += 1
            # advance（この足の記録だけ）
            for rid in order:
                r = recs[rid]
                if r.get("tf") != bar_min: continue
                if r.get("status") in ("break", "retest", "open"):
                    try: advance(r, t, o, h, l, c, pos, P, f)
                    except Exception as e: sys.stderr.write("adv %s: %s\n" % (rid, e))
        changed = sum(1 for rid in order if recs[rid].get("status") != before.get(rid))
    save_state(st)
    return added, changed


def _grp(recs, tf):
    cl = [r for r in recs if r.get("tf") == tf and r.get("status") == "closed" and r.get("netR") is not None]
    if not cl: return "決着0"
    r = np.array([x["netR"] for x in cl])
    cum = np.cumsum(r); dd = float((np.maximum.accumulate(cum) - cum).max())
    return "決着%d/%d 勝率%.0f%% 平均net%+.3f 合計%+.1f DD-%.1f" % (
        len(cl), TARGET, 100 * (r > 0).mean(), r.mean(), r.sum(), dd)


def summary():
    recs, order = load_ledger()
    rs = [recs[i] for i in order]
    return "5分[%s] / 15分[%s]" % (_grp(rs, 5), _grp(rs, 15))


def main():
    print("足の時間軸 前向きレーン起動（5分vs15分・%d秒・発注なし・金ゼロ・関門各30本）" % INTERVAL, flush=True)
    if "--once" in sys.argv:
        a, u = sync_once(); print("once: +%d 新規 / %d 変化 / %s" % (a, u, summary()), flush=True); return
    while True:
        try:
            a, u = sync_once()
            if a or u:
                print("%s +%d / %d変化 / %s" % (dt.datetime.now().strftime("%H:%M:%S"), a, u, summary()), flush=True)
        except Exception as e:
            sys.stderr.write("sync err: %s\n" % e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
