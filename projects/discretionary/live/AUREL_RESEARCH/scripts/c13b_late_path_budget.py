# -*- coding: utf-8 -*-
"""
[cycle13 事後フォロー b] 2026-11-06 — c13 本体の結果（J2 FAIL: 早期 k≤6 に差なし・差は k>12 以降と長 hold に集中・b 三分位で単調増加）を見た後、
M_drift の内部整合性を同じ道具で数字にする。判定規則は変えない（c13 本体の J1/J2 が判定）。
 (1) 建玉中（hold>k）の本について、残り path の差 e_tail−e_head（e = R*−cl_k）と、残り保有 mean((hold−k)/risk) から必要ドリフト μ_req(k) を出す。
     M_drift なら μ_req(k) は k に依らず一定（全体の μ_req と同じ水準）。
 (2) 擬似日次の符号づけドリフトの 95% CI（bp/日）と、必要 μ_req（bp/日）を並べる（予算比の不確かさ）。
 (3) 差の分布上の場所: tail−head の差を R の分位（R<−0.5 / −0.5..0 / 0..+1 / +1..+2 / ≥+2）の確率差×区間平均で分解（ジャンプ型か面型か）。
入力・結合規則は c13 本体と同一。scan 無し・MT5 無し・外部通信無し。
"""
import os, json, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c13b_late_path_budget_result.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle13b] 残り path の予算と差の分布上の場所 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c13b_late_path_budget.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); HOLD = X["hold"].to_numpy().astype(float); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy()
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"]
NH = 80
m = pd.read_csv(os.path.join(MAC, "DGS10.csv")); m.columns = ["date", "v"]; m["v"] = pd.to_numeric(m["v"], errors="coerce")
m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
v = m["v"].to_numpy(); D80 = np.full(len(v), np.nan); D80[NH:] = v[NH:] - v[:-NH]
sg = np.sign(D80)
for k in range(1, len(sg)):
    if sg[k] == 0 and np.isfinite(sg[k - 1]): sg[k] = sg[k - 1]
IVraw = np.full(len(v), -1); cur = -1
for k in range(len(v)):
    if not np.isfinite(sg[k]): continue
    if k == 0 or not np.isfinite(sg[k - 1]) or sg[k] != sg[k - 1]: cur += 1
    IVraw[k] = cur
FD = m["date"].to_numpy().astype("datetime64[D]").astype(np.int64)
def feats(ref, tol=10):
    i = np.searchsorted(FD, ref, side="right") - 1; ok = (i >= 0) & ((ref - FD[np.clip(i, 0, None)]) <= tol)
    ii = np.clip(i, 0, len(FD) - 1); F = D80[ii].copy(); IV = IVraw[ii].copy(); F[~ok] = np.nan; IV[~ok] = -1; IV[~np.isfinite(F)] = -1
    return F, IV
F, IV = feats(AVAIL); OK = np.isfinite(F) & (IV >= 0); TAIL = OK & ((SGN * np.sign(F) * -1) > 0)
W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
def within(v_, g):
    df = pd.DataFrame({"v": v_, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); G = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G += 1
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G
def fe(y, mask):
    mm = mask & (IV >= 0) & np.isfinite(y)
    if mm.sum() < 30: return dict(b=np.nan, t=np.nan, G=0, n=int(mm.sum()))
    yy = within(y[mm], IV[mm]); Z = np.column_stack([within(TAIL[mm].astype(float), IV[mm]), within(SELL[mm], IV[mm])])
    beta, se, G = ols_cluster(yy, Z, IV[mm]); return dict(b=beta[0], t=beta[0] / se[0] if se[0] > 0 else np.nan, G=G, n=int(mm.sum()))

# (2) 擬似日次ドリフト CI
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); day = E["day"].to_numpy().astype(np.int64); lc = E["lc"].to_numpy()
keep = ((day + 3) % 7) <= 4; dayb = day[keep]; lcb = lc[keep]
Fd, _ = feats(dayb - 1); s_d = -np.sign(Fd); ret1 = np.full(len(dayb), np.nan); ret1[1:] = lcb[1:] - lcb[:-1]; price = np.exp(lcb)
yr_d = pd.to_datetime(dayb, unit="D").year.to_numpy() if hasattr(pd.to_datetime(dayb, unit="D"), "year") else pd.DatetimeIndex(pd.to_datetime(dayb, unit="D")).year.to_numpy()
WD = {"在2010-20": (yr_d >= 2010) & (yr_d <= 2020), "外2021-26": yr_d >= 2021, "近年2024-26": yr_d >= 2024}
BPD = 276.0
say("\n## (2) 擬似日次の符号づけドリフト（bp/日）95% CI vs 必要ドリフト")
for wn in W:
    mm = WD[wn] & np.isfinite(Fd) & np.isfinite(ret1) & (ret1 != 0); sr = s_d[mm] * ret1[mm]; se = sr.std(ddof=1) / math.sqrt(len(sr))
    pr = price[mm].mean()
    tm = W[wn] & OK; hr = (HOLD[tm] / RISK[tm]).mean(); beta = fe(R, tm)["b"]; mu_req_usd_day = beta / (2 * hr) * BPD; mu_req_bp = mu_req_usd_day / pr * 1e4
    say(f"- {wn}: 実測 {sr.mean()*1e4:+.2f} bp/日 [95% {(sr.mean()-1.96*se)*1e4:+.2f}, {(sr.mean()+1.96*se)*1e4:+.2f}]（年率換算 {sr.mean()*252*100:+.1f}%）、必要 {mu_req_bp:+.2f} bp/日（{mu_req_usd_day:+.2f} USD/日・平均価格 {pr:.0f}）→ 必要値は CI の {'内' if (sr.mean()-1.96*se)*1e4 <= mu_req_bp <= (sr.mean()+1.96*se)*1e4 else '外'}")

# (1) 残り path の予算
say("\n## (1) 建玉中（hold>k）の残り path: e = R*−cl_k の tail−head、残り保有、必要 μ_req(k)")
for wn, wm in W.items():
    row = []
    for k in (0, 3, 6, 12, 24, 48):
        alive = HOLD > k; idx = np.flatnonzero(alive); clk = np.full(N, np.nan); clk[idx] = clR[off[idx] + k] if k > 0 else 0.0
        e = RSTAR - clk; mm = wm & OK & alive; r = fe(e, mm); hr = ((HOLD[mm] - k) / RISK[mm]).mean()
        mu = r["b"] / (2 * hr) if hr > 0 else np.nan
        row.append(f"k{k}: Δe {r['b']:+.3f}(t{r['t']:+.1f},n{r['n']}) 残り{(HOLD[mm]-k).mean():.0f}本 μ_req {mu*BPD:+.2f} USD/日")
    say(f"- {wn}: " + " / ".join(row))

# (3) 差の分布上の場所
say("\n## (3) tail−head 差の R 分位への分解（区間FE+SELL の確率差 × 全体の分位平均）")
BINS = [("R≤−0.5", -np.inf, -0.5), ("(−0.5,0]", -0.5, 0.0), ("(0,1]", 0.0, 1.0), ("(1,2]", 1.0, 2.0), ("R>2", 2.0, np.inf)]
for wn, wm in W.items():
    mm = wm & OK; tot = 0; parts = []
    for lab, lo, hi in BINS:
        ind = ((R > lo) & (R <= hi)).astype(float); r = fe(ind, mm); mean_bin = R[mm & (ind > 0)].mean() if (mm & (ind > 0)).any() else 0
        contrib = r["b"] * mean_bin; tot += contrib
        parts.append(f"{lab} ΔP {r['b']:+.3f}(t{r['t']:+.1f}) ×{mean_bin:+.2f} = {contrib:+.3f}")
    say(f"- {wn}: " + " / ".join(parts) + f" → 合計 {tot:+.3f}（β {fe(R, mm)['b']:+.3f}）")
    # 上位 10% 本（窓内 R 上位 10%）の tail 比率
    thr = np.quantile(R[mm], 0.9); top = mm & (R >= thr)
    say(f"  上位10%（R≥{thr:.2f}）n{top.sum()}: tail 比 {TAIL[top].mean():.3f}（全体 {TAIL[mm].mean():.3f}）、上位10% の R 合計 tail {R[top & TAIL].sum():+.0f} / head {R[top & ~TAIL].sum():+.0f}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
