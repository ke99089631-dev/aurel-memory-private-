# -*- coding: utf-8 -*-
"""
AUREL cycle1 — 非始動の早畳み（時間で切る出口）。読取りのみ・発注なし・書き込みは AUREL_RESEARCH 配下のみ。

事前固定（findings/2026-11-04.md cycle1 に先に記載。ここは実装）:
  ルール: 建玉足=offset0。offset K の終値時点で未決着かつ「offset0..K の最大含み益 MFE_K < T」なら offset K の終値で畳む。
          K 本以内に SL/TP/TIME で決着済なら原型どおり。
  主判定: K=6(30分), T=0.5R。感度表 K∈{3,6,12,24}×T∈{0.3,0.5} は構造を見るだけ・採用判断には使わない。
  在サンプル: 金M5 2010-01-01..2020-12-31 の scan 再加速 closed 全本（外壁+中壁・全時間帯）
  外サンプル: 2021-01-01..2026-07-01 同上
  第3チェック(ライブ台帳・上下限のみ): setup_ledger.jsonl 再加速 closed 本の open スナップショットから MFE_K を復元。
  指標: 原型 vs ルールの 対の差 diff=R_new−R_orig の平均・t値(paired)・勝率・合計R・最大DD(建玉順累積)・
        尻尾: 原型上位10%本の合計Rがルールで何%残るか。コスト=0.56USD/risk (gross と net 併記、畳みも1往復なので diff は同一)。
  昇格条件: diff>0 が在・外とも、在 t≥2.0・外 t≥1.5、上位10%合計Rの減少≤10%、最大DDが在・外とも悪化しない。全部満たさなければ null/弱い兆候。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(HERE)                       # AUREL_RESEARCH
LIVE = os.path.dirname(RES)                       # discretionary/live
W2W = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
for p in (LIVE, W2W):
    if p not in sys.path:
        sys.path.insert(0, p)

import wallbox
import setup_engine as se
import backtest_reaccel as br
from m5_loader import load_m5

COST = 0.56
PATH_MAX = 48          # 保存する path の最大 offset
KS = (3, 6, 12, 24)
TS = (0.3, 0.5)
PRIMARY = (6, 0.5)
IS_LAST_YEAR = 2020
DATA_DIR = os.path.join(RES, "data"); os.makedirs(DATA_DIR, exist_ok=True)
TRADES_JSON = os.path.join(DATA_DIR, "c1_reaccel_paths_2010_2026.json")
OUT_MD = os.path.join(RES, "data", "c1_early_fold_result.md")


def load_all(y0=2010, y1=2026, last="2026-07-01"):
    frames = []
    for y in range(y0, y1 + 1):
        a, b = "%d-01-01" % y, "%d-01-01" % (y + 1)
        if a >= last: break
        if b > last: b = last
        try:
            frames.append(load_m5(a, b))
        except FileNotFoundError as e:
            print("skip", y, e, flush=True)
    m5 = pd.concat(frames)
    return m5[~m5.index.duplicated(keep="first")].sort_index()


def build_paths():
    print("金M5 読込...", flush=True)
    m5 = load_all()
    print("  %d bars %s..%s" % (len(m5), m5.index[0], m5.index[-1]), flush=True)
    fb = br.FastBox(m5); wallbox.dynamic_box = fb.box
    dm = se._load_damashi()
    t0 = time.time(); recs = se.scan(m5, dm)
    print("  scan %d setups %.0fs" % (len(recs), time.time() - t0), flush=True)
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    pos = {int(pd.Timestamp(t).timestamp()): i for i, t in enumerate(m5.index)}
    trades = []
    for r in recs:
        ra = r.get("reaccel") or {}
        if ra.get("status") != "closed" or ra.get("R") is None or ra.get("sl") is None:
            continue
        ie = pos.get(int(ra["entry_time"])); ek = pos.get(int(ra["exit_time"]))
        if ie is None or ek is None:
            continue
        entry = float(ra["entry"]); sl = float(ra["sl"]); risk = abs(entry - sl)
        if risk <= 0: continue
        sgn = 1.0 if r["side"] == "BUY" else -1.0
        mfe = mae = 0.0; P_mfe = []; P_mae = []; P_cl = []
        for k in range(ie, min(ek, ie + PATH_MAX) + 1):
            fav = sgn * (h[k] - entry) / risk if sgn > 0 else (entry - l[k]) / risk
            adv = (entry - l[k]) / risk if sgn > 0 else (h[k] - entry) / risk
            mfe = max(mfe, fav); mae = max(mae, adv)
            P_mfe.append(round(mfe, 3)); P_mae.append(round(mae, 3)); P_cl.append(round(sgn * (c[k] - entry) / risk, 3))
        trades.append({"entry_time": int(ra["entry_time"]), "year": int(pd.Timestamp(ra["entry_time"], unit="s", tz="UTC").year),
                       "jh": int(((int(ra["entry_time"]) // 3600) + 9) % 24), "wall_kind": r["wall_kind"], "side": r["side"],
                       "risk": round(risk, 3), "R": float(ra["R"]), "exit_reason": ra["exit_reason"], "hold": int(ek - ie),
                       "mfe": P_mfe, "mae": P_mae, "cl": P_cl})
    json.dump({"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "bars": int(len(m5)), "setups": len(recs),
               "frozen": {"MIN_SL_W": se.MIN_SL_W, "FEED_TOL": se.FEED_TOL, "TRIG_SPREAD": se.TRIG_SPREAD, "MAX_HOLD": se.MAX_HOLD},
               "trades": trades}, open(TRADES_JSON, "w", encoding="utf-8"))
    print("  再加速 closed %d 本 → %s" % (len(trades), TRADES_JSON), flush=True)
    return trades


def apply_rule(tr, K, T):
    """畳んだら (True, R_new) / 原型のまま (False, R)."""
    if tr["hold"] <= K or K >= len(tr["mfe"]):
        return False, tr["R"]
    if tr["mfe"][K] < T:
        return True, tr["cl"][K]
    return False, tr["R"]


def maxdd(r):
    cum = np.cumsum(r); peak = np.maximum.accumulate(np.concatenate([[0.0], cum]))[1:]
    return float((cum - peak).min()) if len(r) else 0.0


def stats(trs, K, T):
    trs = sorted(trs, key=lambda x: x["entry_time"])
    R0 = np.array([t["R"] for t in trs]); risk = np.array([t["risk"] for t in trs])
    fl, R1 = zip(*[apply_rule(t, K, T) for t in trs]); fl = np.array(fl); R1 = np.array(R1)
    net0 = R0 - COST / risk; net1 = R1 - COST / risk
    d = R1 - R0; se_ = d.std(ddof=1) / math.sqrt(len(d)) if len(d) > 1 else float("nan")
    top = np.argsort(R0)[-max(1, len(R0) // 10):]
    out = {"n": len(trs), "folded": int(fl.sum()), "fold_pct": 100.0 * fl.mean(),
           "mean0": R0.mean(), "mean1": R1.mean(), "net0": net0.mean(), "net1": net1.mean(),
           "sum0": R0.sum(), "sum1": R1.sum(), "win0": 100.0 * (R0 > 0).mean(), "win1": 100.0 * (R1 > 0).mean(),
           "dd0": maxdd(net0), "dd1": maxdd(net1), "diff": d.mean(), "t": d.mean() / se_ if se_ and se_ > 0 else 0.0,
           "top10_sum0": R0[top].sum(), "top10_sum1": R1[top].sum(), "top10_folded": int(fl[top].sum()),
           "folded_R_orig": R0[fl].mean() if fl.any() else float("nan"), "folded_R_new": R1[fl].mean() if fl.any() else float("nan")}
    return out


def fmt(s, lab):
    return ("%-16s n%5d 畳み%4d(%4.1f%%) 平均R %+.3f→%+.3f net %+.3f→%+.3f 合計 %+7.1f→%+7.1f 勝率 %4.1f→%4.1f%% "
            "DD %+6.1f→%+6.1f diff %+.3f t%+.2f | 畳んだ本: 原型%+.3f→畳み%+.3f | 上位10%%合計 %+.1f→%+.1f(畳まれ%d)") % (
        lab, s["n"], s["folded"], s["fold_pct"], s["mean0"], s["mean1"], s["net0"], s["net1"], s["sum0"], s["sum1"],
        s["win0"], s["win1"], s["dd0"], s["dd1"], s["diff"], s["t"], s["folded_R_orig"], s["folded_R_new"],
        s["top10_sum0"], s["top10_sum1"], s["top10_folded"])


def conditional_table(trs, K):
    """診断: offset K 時点の MFE_K バケット別に、その後の最終R（原型）。機械的でないかの確認用。"""
    rows = []
    for t in trs:
        if t["hold"] > K and K < len(t["mfe"]):
            rows.append((t["mfe"][K], t["cl"][K], t["R"]))
    if not rows: return "  (none)"
    a = np.array(rows); bins = [0, 0.25, 0.5, 0.75, 1.0, 99]
    L = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (a[:, 0] >= lo) & (a[:, 0] < hi)
        if m.sum():
            L.append("  MFE_%d∈[%.2f,%.2f) n%5d  その時の終値R %+.3f  最終R %+.3f  最終勝率 %4.1f%%" % (
                K, lo, hi, m.sum(), a[m, 1].mean(), a[m, 2].mean(), 100.0 * (a[m, 2] > 0).mean()))
    return "\n".join(L)


def live_check(K, T):
    """ライブ台帳: open スナップショットから MFE_K を復元。畳み時の終値Rは無い→ [−MAE_K, +MFE_K] の範囲で上下限。"""
    import collections
    snaps = collections.defaultdict(list); final = {}
    with open(os.path.join(LIVE, "setup_ledger.jsonl"), encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln: continue
            r = json.loads(ln)
            ra = r.get("reaccel")
            if not isinstance(ra, dict): continue
            t = r["target"] if r.get("kind") == "update" else r.get("id")
            if ra.get("status") == "open" and ra.get("hold_bars") is not None:
                snaps[t].append((int(ra["hold_bars"]), float(ra["mfe_R"]), float(ra["mae_R"])))
            elif ra.get("status") == "closed" and ra.get("R") is not None:
                final[t] = ra
    n_all = len(final); kept = []; fold = []; nocov = 0
    for t, ra in final.items():
        hold = int(ra["hold_bars"]); R = float(ra["R"])
        if hold <= K:
            kept.append(R); continue
        ss = [s for s in snaps[t] if s[0] <= K]
        if not ss:
            nocov += 1; continue
        mfeK = max(s[1] for s in ss); maeK = max(s[2] for s in ss)
        if mfeK < T:
            fold.append((R, mfeK, maeK))
        else:
            kept.append(R)
    L = ["  ライブ台帳 再加速 closed n=%d（K=%d,T=%.1f）: K本以内決着/未畳み %d, 畳み対象 %d, スナップ無しで判定不能 %d" % (
        n_all, K, T, len(kept), len(fold), nocov)]
    if fold:
        a = np.array(fold)
        L.append("  畳み対象の最終R(原型) 平均 %+.3f 合計 %+.1f 勝率 %.0f%% | 畳み時Rの範囲: 下限(−MAE_K)平均 %+.3f 〜 上限(+MFE_K)平均 %+.3f" % (
            a[:, 0].mean(), a[:, 0].sum(), 100.0 * (a[:, 0] > 0).mean(), -a[:, 2].mean(), a[:, 1].mean()))
        L.append("  → 畳みが得になる条件: 畳み時R > 原型の最終R(%+.3f)。上限でも %+.3f、下限なら %+.3f" % (
            a[:, 0].mean(), a[:, 1].mean(), -a[:, 2].mean()))
    return "\n".join(L)


def main():
    if os.path.exists(TRADES_JSON) and "--rebuild" not in sys.argv:
        trades = json.load(open(TRADES_JSON, encoding="utf-8"))["trades"]
        print("cached paths %d trades" % len(trades), flush=True)
    else:
        trades = build_paths()
    IS = [t for t in trades if t["year"] <= IS_LAST_YEAR]; OOS = [t for t in trades if t["year"] > IS_LAST_YEAR]
    L = ["# AUREL cycle1 非始動の早畳み  %s" % time.strftime("%Y-%m-%d %H:%M"),
         "在=2010-%d(n%d) 外=%d-2026/07(n%d)  主判定 K=%d T=%.1f" % (IS_LAST_YEAR, len(IS), IS_LAST_YEAR + 1, len(OOS), *PRIMARY), ""]
    K, T = PRIMARY
    L.append("## 主判定 K=%d T=%.1f" % (K, T))
    L.append(fmt(stats(IS, K, T), "在 2010-%d" % IS_LAST_YEAR)); L.append(fmt(stats(OOS, K, T), "外 %d-26" % (IS_LAST_YEAR + 1)))
    L.append(""); L.append("## 感度表（構造確認のみ・採用判断に使わない）")
    for k in KS:
        for tt in TS:
            L.append(fmt(stats(IS, k, tt), "在 K%d T%.1f" % (k, tt))); L.append(fmt(stats(OOS, k, tt), "外 K%d T%.1f" % (k, tt)))
    L.append(""); L.append("## 診断: K=6 時点の MFE_6 バケット別 → その後の最終R（原型）")
    L.append("在:"); L.append(conditional_table(IS, 6)); L.append("外:"); L.append(conditional_table(OOS, 6))
    L.append(""); L.append("## 第3チェック: ライブ台帳（上下限のみ）")
    L.append(live_check(*PRIMARY))
    hold = np.array([t["hold"] for t in trades])
    L.append(""); L.append("保有本数: 中央値 %d, ≤6本で決着 %.0f%%, ≤12本 %.0f%%" % (np.median(hold), 100 * (hold <= 6).mean(), 100 * (hold <= 12).mean()))
    txt = "\n".join(L); print(txt)
    open(OUT_MD, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
