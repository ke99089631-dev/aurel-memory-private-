# -*- coding: utf-8 -*-
"""
[REFUTE c68 — e] 2026-11-25 第 5 走。自分の D1 判定の穴を自分で突く。

d 走の A19 (ii) は「B2 (−0.5,−0.2] 内で MFE_k ≥ +0.8」を鏡像とした。**これは正しい鏡像ではない**:
cl_k ≈ −0.35 から MAE ≤ −0.8 は 0.45R の戻り、MFE ≥ +0.8 は 1.15R の往復＝必要な遠出の大きさが違う。
正しい鏡像は「符号を反転した同じ幾何」＝ **cl_k ∈ B4 [+0.2,+0.5) 内で MFE_k ≥ +0.8（上の縁を試して戻した）**
（B2 の下側距離 |cl−(−0.8)| ≈ 0.45 と B4 の上側距離 |0.8−cl| ≈ 0.45 が揃う）。

事前固定: 鏡像セル = (窓, k=24, B4) 内で MFE_k ≥ +0.8 の群 vs 残り。さらに cl 距離を厳密に揃えた版:
  下側型 = cl_k ∈ (−0.5,−0.2] ∧ MAE_k ≤ cl_k − 0.45
  上側型 = cl_k ∈ [+0.2,+0.5) ∧ MFE_k ≥ cl_k + 0.45     （距離を 0.45R に固定した対称定義）
  および距離 0.30/0.60R 版（感度）。
**D1 再判定: 上側型の Δ が 下側型の +70% 以上かつ |t| ≥ 1.5 なら、d 走の D1 非発火を取り下げ、
  T1 は「レンジ/往復の別名」＝機構主張は broken。符号が逆または ≈0 なら d 走の結論を維持。**
注: SL は −1 固定・TP は +b（≈1.4）なので幾何は本質的に非対称＝完全な鏡像は存在しない。
  上側型は「TP に近づいて戻った」なので残りの上側余地が小さい ⇒ Δ が小さく出る機械的な向きがある。
  よって「上側型 ≈ 0」は H_stop の証拠として弱い。この非対称そのものを印字する。
データ: c68 と同一キャッシュのみ。書込は AUREL_RESEARCH/data のみ。
"""
import json, os, time, math
import numpy as np, pandas as pd
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); OUT = os.path.join(DATA, "refute_c68_maeedge_e.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
df["b"] = df.entry_time.map({t["entry_time"]: t["b"] for t in c4["trades"]})
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; hiR = z["hiR"]; loR = z["loR"]; off = z["off"]
n = len(df); exp_hold = np.diff(off) - 1
if not np.all(exp_hold == df.hold.to_numpy()):
    bad = np.nonzero(exp_hold != df.hold.to_numpy())[0]; et = df.entry_time.to_numpy(); order = np.arange(n)
    for p in np.unique(et[bad]):
        grp = np.nonzero(et == p)[0]; want = exp_hold[grp]; have = df.hold.to_numpy()[grp]
        order[grp] = [int(grp[list(have).index(w)]) for w in want]
    df = df.iloc[order].reset_index(drop=True)
risk = df.risk.to_numpy(); ft = FT / risk; R = df.R.to_numpy(); hold = df.hold.to_numpy()
exitr = df.exit_reason.to_numpy(); is_slt = df.exit_reason.isin(["SL", "TP"]).to_numpy()
Rstar = R + ft * is_slt; year = df.year.to_numpy(); bb = df.b.to_numpy()
K = 24
alive = np.nonzero(hold > K)[0]
idx = off[alive][:, None] + np.arange(1, K + 1)[None, :]
LO = loR[idx]; HI = hiR[idx]; clk = clR[idx][:, -1]
MAE = LO.min(axis=1); MFE = HI.max(axis=1); e = Rstar[alive] - clk
W = {"在2010-20": year[alive] <= 2020, "外2021-26": year[alive] >= 2021, "近年2024-26": year[alive] >= 2024}
say(f"# [REFUTE c68 e] 正しい鏡像（B4 の上の縁）で自分の D1 判定を点検 — {time.strftime('%Y-%m-%d %H:%M')}")
say()
say("## (A) ビン対称版: B2 内 MAE≥ 型 vs B4 内 MFE≥ 型")
say("| 窓 | 型 | セル | 群定義 | n(群):n(残) | Δ | t |")
say("|---|---|---|---|---|---|---|")
res = {}
for wn, wm in W.items():
    for lab, bmask, q_, cellnm in (
        ("下側（c68）", (clk <= -0.2) & (clk > -0.5), MAE <= -0.8, "B2 (−0.5,−0.2]"),
        ("上側（鏡像）", (clk >= 0.2) & (clk < 0.5), MFE >= +0.8, "B4 [+0.2,+0.5)")):
        m = wm & bmask
        ee = e[m]; qq = q_[m]
        if qq.sum() < 10 or (~qq).sum() < 10:
            say(f"| {wn} | {lab} | {cellnm} | — | {qq.sum()}:{(~qq).sum()} | n 不足 | |"); continue
        dd, tw, _ = welch(ee[qq], ee[~qq]); res[(wn, lab)] = (dd, tw)
        say(f"| {wn} | {lab} | {cellnm} | {'MAE≤−0.8' if lab.startswith('下') else 'MFE≥+0.8'} | {qq.sum()}:{(~qq).sum()} | {dd:+.4f} | {tw:+.2f} |")
say()
say("## (B) 距離を厳密に揃えた対称版: 下側 = MAE ≤ cl−d／上側 = MFE ≥ cl+d（同じ d）")
say("| 窓 | d | 下側 Δ / t / n | 上側 Δ / t / n | 上側/下側 % |")
say("|---|---|---|---|---|")
SYM = {}
for wn, wm in W.items():
    for d in (0.30, 0.45, 0.60):
        mlo = wm & (clk <= -0.2) & (clk > -0.5); mhi = wm & (clk >= 0.2) & (clk < 0.5)
        qlo = (MAE <= clk - d)[mlo]; qhi = (MFE >= clk + d)[mhi]
        elo = e[mlo]; ehi = e[mhi]
        if qlo.sum() < 10 or (~qlo).sum() < 10 or qhi.sum() < 10 or (~qhi).sum() < 10:
            say(f"| {wn} | {d:.2f} | n 不足 | | |"); continue
        dl, tl, _ = welch(elo[qlo], elo[~qlo]); dh, th, _ = welch(ehi[qhi], ehi[~qhi])
        SYM[(wn, d)] = (dl, tl, dh, th)
        say(f"| {wn} | {d:.2f} | {dl:+.4f} / {tl:+.2f} / {qlo.sum()}:{(~qlo).sum()} | {dh:+.4f} / {th:+.2f} / {qhi.sum()}:{(~qhi).sum()} | {100*dh/dl if dl!=0 else float('nan'):.0f}% |")
say()
say("## (C) 幾何の非対称（上側型が機械的に小さく出る分の印字）: 残り余地 d_up / d_dn の群別平均")
say("| 窓 | セル | 群 | n | cl_k 平均 | d_up = b+ft−cl | d_dn = (1−ft)+cl | 含意 TP 率 | 観測 TP 率 | 差 z |")
say("|---|---|---|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    for lab, bmask, q_, cellnm in (
        ("下側", (clk <= -0.2) & (clk > -0.5), MAE <= -0.8, "B2"),
        ("上側", (clk >= 0.2) & (clk < 0.5), MFE >= +0.8, "B4")):
        m = wm & bmask; al = alive[m]
        if m.sum() < 30: continue
        du = bb[al] + ft[al] - clk[m]; dd_ = (1 - ft[al]) + clk[m]; pimp = dd_ / (dd_ + du)
        ex = exitr[al]; rs = (ex == "SL") | (ex == "TP")
        for gl, gq in (("群", q_[m]), ("残り", ~q_[m])):
            s_ = gq & rs
            if s_.sum() < 15: continue
            obs = (ex[s_] == "TP").mean(); imp = pimp[s_].mean()
            se = math.sqrt(max(imp * (1 - imp), 1e-9) / s_.sum())
            say(f"| {wn} | {cellnm} {lab} | {gl} | {s_.sum()} | {clk[m][s_].mean():+.3f} | {du[s_].mean():.3f} | {dd_[s_].mean():.3f} | {imp:.3f} | {obs:.3f} | {(obs-imp)/se:+.2f} |")
say()
dl0 = res.get(("外2021-26", "下側（c68）")); dh0 = res.get(("外2021-26", "上側（鏡像）"))
ratio = (dh0[0] / dl0[0]) if (dl0 and dh0 and dl0[0] != 0) else float("nan")
fire = (dh0 is not None) and (ratio >= 0.70) and (abs(dh0[1]) >= 1.5)
say(f"→ 外: 下側 {dl0[0]:+.4f} (t{dl0[1]:+.2f})／上側 鏡像 {dh0[0]:+.4f} (t{dh0[1]:+.2f}) = {100*ratio:.0f}%")
say(f"→ **D1 再判定: {'発火 ＝ d 走の結論を取り下げ（レンジ/往復の別名）' if fire else '非発火 ＝ d 走の結論を維持（下側固有）'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
