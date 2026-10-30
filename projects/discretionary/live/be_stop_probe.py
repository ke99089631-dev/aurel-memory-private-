# -*- coding: utf-8 -*-
"""建値SL（+XRで建値に逃がす）の材料検証（読取のみ・発注なし・会長GO 2026-10-30「2を材料として」）。
Gemini一致の「+0.5R到達後に戻されて-1Rになる55本」を、建値SLで救えるか/勝ちをどれだけ削るかを、
紙reaccelの確定トレードを近年M5バーで経路再現して測る。16年一括は使わない(金のレジーム変化でノイズ・会長指摘)。

土台の信頼: まず建値なし再現(baseline)が台帳の紙Rと一致するか検算してから、建値版を比べる。
足内の決着順は紙と同一(_simulate流儀): SL(FEED_TOL手前)優先→TP(FEED_TOL先)。建値アームは当足末で成立し翌足から有効。
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import setup_engine as se

HERE = os.path.dirname(os.path.abspath(__file__))
SET_LED = os.path.join(HERE, "setup_ledger.jsonl")
ARMS = [0.3, 0.5, 0.7, 1.0]        # 建値に逃がすトリガー(R)。材料として複数。

def fold():
    setups = {}
    for ln in open(SET_LED, encoding="utf-8"):
        ln = ln.strip()
        if not ln: continue
        try: r = json.loads(ln)
        except: continue
        if r.get("kind") == "setup":
            setups[r["id"]] = dict(r)
        elif r.get("kind") == "update":
            sid = r.get("target")
            if sid in setups:
                for k in ("reaccel", "chase", "status"):
                    if k in r: setups[sid][k] = r[k]
    return setups

def sim(o, h, l, c, ie, side, entry, sl, tp, n, be_arm=None):
    """be_arm=None なら baseline(_simulate流儀)。数値なら +be_arm R 到達後にSLを建値へ。"""
    risk = abs(entry - sl)
    if risk <= 0: return None
    FT = se.FEED_TOL; k_end = min(ie + se.MAX_HOLD, n - 1)
    sl_cur = sl; armed = False
    for k in range(ie, k_end + 1):
        if side == "SELL":
            fav = (entry - l[k]) / risk
            if h[k] >= sl_cur - FT: return _r(side, entry, sl_cur, risk, "BE" if armed else "SL", k, ie)
            if l[k] <= tp - FT:      return _r(side, entry, tp, risk, "TP", k, ie)
        else:
            fav = (h[k] - entry) / risk
            if l[k] <= sl_cur + FT: return _r(side, entry, sl_cur, risk, "BE" if armed else "SL", k, ie)
            if h[k] >= tp + FT:      return _r(side, entry, tp, risk, "TP", k, ie)
        if be_arm is not None and not armed and fav >= be_arm:
            armed = True; sl_cur = entry       # 翌足から建値SL
    # 時間切れ
    return _r(side, entry, c[k_end], risk, "TIME", k_end, ie, exitpx=c[k_end])

def _r(side, entry, exit_px, risk, reason, k, ie, exitpx=None):
    px = exitpx if exitpx is not None else exit_px
    pnl = (px - entry) if side == "BUY" else (entry - px)
    return {"R": round(pnl / risk, 3), "reason": reason, "hold": k - ie}

def main():
    setups = fold()
    trades = []
    for sid, s in setups.items():
        ra = s.get("reaccel") or {}
        if ra.get("status") == "closed" and ra.get("R") is not None and ra.get("entry_time"):
            e = float(ra["entry"]); tp = float(ra["tp"]); sl = float(ra["sl"])
            side = "SELL" if tp < e else "BUY"
            trades.append({"sid": sid, "side": side, "entry": e, "sl": sl, "tp": tp,
                           "t": int(ra["entry_time"]), "R_led": float(ra["R"]),
                           "reason_led": ra.get("exit_reason"), "mfe": ra.get("mfe_R")})
    m5 = se._fetch_bars(5000)
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    idx = m5.index; n = len(c)
    t0 = int(pd.Timestamp(idx[0]).timestamp())
    rows = []
    for t in trades:
        if t["t"] < t0: continue                  # バー期間外(近年のみ)
        ie = int(idx.searchsorted(pd.Timestamp(t["t"], unit="s", tz="UTC")))
        if ie <= 0 or ie >= n: continue
        base = sim(o, h, l, c, ie, t["side"], t["entry"], t["sl"], t["tp"], n, be_arm=None)
        if base is None: continue
        rec = {"sid": t["sid"], "side": t["side"], "R_led": t["R_led"], "mfe": t["mfe"],
               "R_base": base["R"], "reason_base": base["reason"]}
        for a in ARMS:
            r = sim(o, h, l, c, ie, t["side"], t["entry"], t["sl"], t["tp"], n, be_arm=a)
            rec["R_be%.1f" % a] = r["R"]; rec["reason_be%.1f" % a] = r["reason"]
        rows.append(rec)
    df = pd.DataFrame(rows)
    def stat(col):
        rs = df[col].to_numpy(); cum = np.cumsum(rs); dd = (cum - np.maximum.accumulate(cum)).min()
        return len(rs), rs.sum(), rs.mean(), 100*(rs > 0).mean(), dd
    print("=== 建値SL 材料検証（紙reaccel 近年%d本・M5経路再現）===" % len(df))
    # 検算: baseline vs 台帳R
    val = df.dropna(subset=["R_led"])
    agree = (np.sign(val["R_base"]) == np.sign(val["R_led"])).mean()
    mae_r = (val["R_base"] - val["R_led"]).abs().mean()
    print("検算 baseline vs 台帳R: 勝敗一致%.0f%% / 平均絶対差%.3fR （高一致なら土台OK）" % (100*agree, mae_r))
    print("%-10s n=%d 合計R%+.1f 平均R%+.3f 勝率%.0f%% DD%.1fR" % (("baseline",)+stat("R_base")))
    for a in ARMS:
        print("%-10s n=%d 合計R%+.1f 平均R%+.3f 勝率%.0f%% DD%.1fR" % (("建値+%.1fR"%a,)+stat("R_be%.1f"%a)))
    # 「+0.5R後に戻されSL」クラスターが建値+0.5でどう変わるか
    sub = df[(df["reason_base"] == "SL") & (df["mfe"].fillna(0) >= 0.5)]
    print("\n+0.5R到達後にSL(baseline)= %d本。建値+0.5Rでの決着内訳:" % len(sub))
    if len(sub):
        vc = sub["reason_be0.5"].value_counts().to_dict()
        print("  ", vc, " R変化 合計%+.1f→%+.1f" % (sub["R_base"].sum(), sub["R_be0.5"].sum()))
    json.dump({"rows": rows}, open(os.path.join(HERE, "be_stop_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nsaved be_stop_result.json")

if __name__ == "__main__":
    main()
