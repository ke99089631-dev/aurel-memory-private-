# -*- coding: utf-8 -*-
"""
[REFUTE DGS10 placebo] 事後フォロー b — 判定規則は不変。主スクリプトの結果を見てから追加した数字のみ:
  主の Q1 で「金自身 g80 × side（金トレンド乗り）」が金自身の符号区間 FE で 外 β +0.0996 (t3.99) と DGS10 (t3.94) に並んだ。
  ただし (i) 金は 2021-26 の 74% が上昇区間で Kish 有効区間数 6.2（DGS10 16.4）＝クラスタ t が信頼できない水準、
  (ii) 金自身のトレンドは「外部プラセボ」でなく経済的な競合（モメンタム乗り）。主の判定規則はこれを「プラセボ」に数えた（設計上の甘さ・本文に明記）。
  ここでは判定を変えず、何が起きているかを数字で分ける:
  B1 相互統制: 金区間 FE（金 Δ_N 符号区間・金区間クラスタ）の中で tail_rate(80) は残るか／金利区間 FE の中で ride_gold は残るか（11:30 b-B1 の再現）。N_gold ∈ {40, 80}。
  B2 区間ブロック bootstrap（1000 回）: 金区間 FE の β_ride と 金利区間 FE の β_tail の 95% CI（少クラスタでの t の過信を避ける）。
  B3 合成 RW の帰無を Kish で層別: Kish ≤8 の RW で |t| の 95%/99% 点（金 N=80 の Kish 6.2 に対応する帰無）・Kish 12〜20（DGS10 対応）。
  B4 2×2 記述（外・区間 FE なし・側別）: (tail_rate, ride_gold80) × side の平均 R と n。
"""
import os, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_dgs10_placebo_series_b.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE DGS10 placebo] 事後フォロー b — 金トレンド乗りとの相互統制・区間 bootstrap・Kish 層別帰無 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_dgs10_placebo_series_b.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}

def load_fred(name):
    m = pd.read_csv(os.path.join(MAC, f"{name}.csv")); m.columns = ["date", "v"]; m["v"] = pd.to_numeric(m["v"], errors="coerce")
    m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    return m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), m["v"].to_numpy()
def intervals_from_series(FD, v, NH):
    D = np.full(len(v), np.nan); D[NH:] = v[NH:] - v[:-NH]; sg = np.sign(D)
    for k in range(1, len(sg)):
        if sg[k] == 0 and np.isfinite(sg[k - 1]): sg[k] = sg[k - 1]
    IV = np.full(len(v), -1); cur = -1
    for k in range(len(v)):
        if not np.isfinite(sg[k]): continue
        if k == 0 or not np.isfinite(sg[k - 1]) or sg[k] != sg[k - 1]: cur += 1
        IV[k] = cur
    return D, IV
def attach(FD, D, IV, ref, tol=10):
    i = np.searchsorted(FD, ref, side="right") - 1; ok = (i >= 0) & ((ref - FD[np.clip(i, 0, None)]) <= tol)
    ii = np.clip(i, 0, len(FD) - 1); F = D[ii].copy(); IVo = IV[ii].copy(); F[~ok] = np.nan; IVo[~ok] = -1; IVo[~np.isfinite(F)] = -1
    return F, IVo
def within(v_, g):
    df = pd.DataFrame({"v": v_, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); Gc = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); Gc += 1
    V = ZtZi @ meat @ ZtZi * (Gc / max(Gc - 1, 1)); return beta, np.sqrt(np.diag(V)), Gc
def fe(y, mask, cols, iv):
    mm = mask & (iv >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    if mm.sum() < 30 or len(np.unique(iv[mm])) < 3: return dict(b=np.full(len(cols), np.nan), t=np.full(len(cols), np.nan), G=0, n=int(mm.sum()), kish=np.nan, mask=mm)
    yy = within(y[mm], iv[mm]); Z = np.column_stack([within(c[mm], iv[mm]) for c in cols])
    b, se, Gc = ols_cluster(yy, Z, iv[mm]); cnt = np.bincount(iv[mm]); cnt = cnt[cnt > 0]
    return dict(b=b, t=b / np.where(se > 0, se, np.nan), G=Gc, n=int(mm.sum()), kish=cnt.sum() ** 2 / (cnt ** 2).sum(), mask=mm)

FD_r, v_r = load_fred("DGS10")
D, IV = intervals_from_series(FD_r, v_r, 80); F_r, IV_r = attach(FD_r, D, IV, AVAIL)
OK_r = np.isfinite(F_r) & (IV_r >= 0); TAIL = np.where(OK_r, ((SGN * np.sign(F_r) * -1) > 0).astype(float), np.nan)
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); E["dt"] = pd.to_datetime(E["ts_last"], unit="s")
E = E[~E["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
FD_g = E["known"].to_numpy().astype(np.int64); v_g = E["lc"].to_numpy()   # v1: known（秒）≤ te で付与（v0 は day 列の誤読で look-ahead）
TE = X["te"].to_numpy().astype(np.int64)
GOLD = {}
for Ng in (40, 80):
    Dg, IVg = intervals_from_series(FD_g, v_g, Ng); F_g, IV_g = attach(FD_g, Dg, IVg, TE, tol=5 * 86400)
    assert np.all(FD_g[np.clip(np.searchsorted(FD_g, TE, side="right") - 1, 0, None)][IV_g >= 0] <= TE[IV_g >= 0]), "look-ahead"
    OK_g = np.isfinite(F_g) & (IV_g >= 0); RIDE = np.where(OK_g, ((SGN * np.sign(F_g)) > 0).astype(float), np.nan)
    GOLD[Ng] = dict(F=F_g, IV=IV_g, OK=OK_g, RIDE=RIDE)

# ---------- B1 相互統制 ----------
say("\n## B1 相互統制（係数 / 区間クラスタ t）")
for Ng in (40, 80):
    g = GOLD[Ng]
    for wn, wm in W.items():
        rg = fe(R, wm & OK_r & g["OK"], [g["RIDE"], SELL, TAIL], g["IV"])
        rr = fe(R, wm & OK_r & g["OK"], [TAIL, SELL, g["RIDE"]], IV_r)
        say(f"- N_gold={Ng} {wn}: **金区間 FE**（区間 {rg['G']}・Kish {rg['kish']:.1f}）: ride {rg['b'][0]:+.4f} (t{rg['t'][0]:+.2f})・**tail_rate {rg['b'][2]:+.4f} (t{rg['t'][2]:+.2f})**｜"
            f"**金利区間 FE**（区間 {rr['G']}・Kish {rr['kish']:.1f}）: tail_rate {rr['b'][0]:+.4f} (t{rr['t'][0]:+.2f})・**ride {rr['b'][2]:+.4f} (t{rr['t'][2]:+.2f})**")
    for wn, wm in W.items():
        rg0 = fe(R, wm & g["OK"], [g["RIDE"], SELL], g["IV"])
        say(f"  - 単独 N_gold={Ng} {wn}: 金区間 FE ride {rg0['b'][0]:+.4f} (t{rg0['t'][0]:+.2f})・γ_SELL {rg0['b'][1]:+.4f}・区間 {rg0['G']}・Kish {rg0['kish']:.1f}・負区間比 {np.mean(g['F'][wm & g['OK']] < 0):.2f}")

# ---------- B2 区間ブロック bootstrap ----------
say("\n## B2 区間ブロック bootstrap（1000 回・区間を復元抽出・外 2021-26）")
def block_boot(y, mask, cols, iv, B=1000):
    mm = mask & (iv >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    ivs = np.unique(iv[mm]); idx_by = {g: np.flatnonzero(mm & (iv == g)) for g in ivs}
    bs = np.full(B, np.nan)
    for b in range(B):
        pick = rng.choice(ivs, size=len(ivs), replace=True)
        rows = np.concatenate([idx_by[g] for g in pick]); lab = np.concatenate([np.full(len(idx_by[g]), j) for j, g in enumerate(pick)])
        yy = within(y[rows], lab); Z = np.column_stack([within(c[rows], lab) for c in cols])
        bs[b] = (np.linalg.pinv(Z.T @ Z) @ Z.T @ yy)[0]
    return np.nanquantile(bs, [0.025, 0.975]), np.mean(bs <= 0)
m_out = W["外2021-26"]
ci, p0 = block_boot(R, m_out & OK_r, [TAIL, SELL], IV_r); say(f"- DGS10 金利区間 FE β_tail: 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]・P(β≤0) {p0:.3f}（11:30: [+0.049, +0.199]）")
for Ng in (40, 80):
    g = GOLD[Ng]; ci, p0 = block_boot(R, m_out & g["OK"], [g["RIDE"], SELL], g["IV"]); say(f"- 金 N={Ng} 金区間 FE β_ride: 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]・P(β≤0) {p0:.3f}")
    ci, p0 = block_boot(R, m_out & g["OK"] & OK_r, [TAIL, SELL, g["RIDE"]], g["IV"]); say(f"- 金 N={Ng} 金区間 FE の中の tail_rate: 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]・P(≤0) {p0:.3f}")
    ci, p0 = block_boot(R, m_out & g["OK"] & OK_r, [g["RIDE"], SELL, TAIL], IV_r); say(f"- 金 N={Ng} 金利区間 FE の中の ride: 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]・P(≤0) {p0:.3f}")

# ---------- B3 合成 RW を Kish で層別 ----------
say("\n## B3 合成 RW 帰無（300 本・Δ80）を Kish 有効区間数で層別（外 2021-26）")
NP = 300; tt = np.full(NP, np.nan); Ks = np.full(NP, np.nan)
for p in range(NP):
    v_s = np.cumsum(rng.standard_normal(len(v_r))); Ds, IVs = intervals_from_series(FD_r, v_s, 80); Fs, IVo = attach(FD_r, Ds, IVs, AVAIL)
    OKs = np.isfinite(Fs) & (IVo >= 0); TL = (OKs & ((SGN * np.sign(Fs) * -1) > 0)).astype(float)
    r = fe(R, m_out & OKs, [TL, SELL], IVo); tt[p] = r["t"][0]; Ks[p] = r["kish"]
at = np.abs(tt)
for lo, hi, lab in [(0, 8, "Kish ≤8（金 N=80 の 6.2 に対応）"), (8, 12, "Kish 8〜12"), (12, 20, "Kish 12〜20（DGS10 16.4 に対応）"), (20, 99, "Kish >20")]:
    mk = np.isfinite(tt) & (Ks > lo) & (Ks <= hi)
    if mk.sum() >= 5: say(f"- {lab}: n{mk.sum()}・|t| 中央値 {np.median(at[mk]):.2f}・95% 点 {np.quantile(at[mk],.95):.2f}・99% 点 {np.quantile(at[mk],.99):.2f}・P(|t|≥3.94) {(at[mk]>=3.94).mean():.3f}")
    else: say(f"- {lab}: n{mk.sum()}（少なすぎ）")

# ---------- B4 2×2 記述 ----------
say("\n## B4 2×2（外 2021-26・区間 FE なし・側別）: 平均 R / n")
g = GOLD[80]; mm = m_out & OK_r & g["OK"]
for sd, sm in [("BUY", SGN > 0), ("SELL", SGN < 0)]:
    cells = []
    for tr in (1, 0):
        for rd in (1, 0):
            k = mm & sm & (TAIL == tr) & (g["RIDE"] == rd); cells.append(f"tail{tr}·ride{rd}: {R[k].mean():+.3f}/{k.sum()}")
    say(f"- {sd}: " + "｜".join(cells))
say(f"\n- 合計 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("wrote", OUT)
