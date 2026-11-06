# -*- coding: utf-8 -*-
"""
[REFUTE 反証レーン] 2026-11-06 — refute_c15_rhocorr.py の事後フォロー b（判定規則は不変・数字を見た後に追加）
動機: Q5 で プール模型（区間FE + tail + tail·agree + agree + SELL）の tail·agree は 外 +0.009 (t0.21) なのに、
  部分集合（各自 FE）は agree=1 内 β +0.132 (t3.79) / agree=0 内 β +0.015 (t0.35) と大きく割れた。
  プール模型は γ_SELL と区間平均を agree 状態で共有する制約を置いており、部分集合差の推定量と一致しない。
ここで出すもの（記述・判定は a の規則のまま）:
  B1 完全交差模型: FE(区間×agree) + tail + tail·agree + SELL + SELL·agree、クラスタ = 区間×agree ブロック。tail·agree = 部分集合差。
     在/外/近年。外・近年は区間 bootstrap（区間を復元抽出・1000 回）で 95% CI。
  B2 agree=1 / agree=0 の部分集合 β を 外 年別 LOYO と 年別（⑬ の正負区間比つき）で。
  B3 構造の注記: agree = 1[tail == ride80]（代数的に恒等）。加法模型 R = β_r·tail + β_g·ride なら
     β(agree=1) − β(agree=0) = 2·β_g。17:40 b-B1 / 14:25 Q1 の区間FE 加法統制では ride80 の係数 ≈0（+0.002 t0.06）。
     → 同じ加法統制を本データで再計算し、部分集合差 と 2·β_g を並べる（食い違えばブロック（時期）組成の差）。
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c15_rhocorr_b.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE b] cycle15 Q5 遅い結合の事後フォロー（完全交差模型・LOYO・加法統制との整合） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c15_rhocorr_b.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); TE = X["te"].to_numpy().astype(np.int64)
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
def load_fred(name):
    m = pd.read_csv(os.path.join(MAC, f"{name}.csv")); m.columns = ["date", "v"]; m["v"] = pd.to_numeric(m["v"], errors="coerce")
    m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    return m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), m["v"].to_numpy()
def intervals_from_series(v, NH):
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
FD, VY = load_fred("DGS10"); D80, IV80 = intervals_from_series(VY, 80); F, IVo = attach(FD, D80, IV80, AVAIL)
OK = np.isfinite(F) & (IVo >= 0); TAIL = (OK & ((SGN * np.sign(F) * -1) > 0)).astype(float)
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); E["dt"] = pd.to_datetime(E["ts_last"], unit="s")
E = E[~E["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
KN_g = E["known"].to_numpy().astype(np.int64); LC_g = E["lc"].to_numpy()
TOLS = 10 * 86400
def attach_known(vals, known, ref_s):
    i = np.searchsorted(known, ref_s, side="right") - 1
    ok = (i >= 0) & ((ref_s - known[np.clip(i, 0, None)]) <= TOLS); ii = np.clip(i, 0, len(known) - 1)
    out = vals[ii].copy(); out[~ok] = np.nan; sel = ok & np.isfinite(out); assert np.all(known[ii][sel] <= ref_s[sel]); return out
G80 = np.full(len(LC_g), np.nan); G80[80:] = LC_g[80:] - LC_g[:-80]
g80 = attach_known(G80, KN_g, TE); nz0 = int((OK & (F == 0)).sum())
OKG = OK & np.isfinite(g80) & (g80 != 0) & (F != 0)   # Δ80 == 0 の本（sign 0 → tail=0 固定）は状態分析から除外
AGREE = (OKG & (np.sign(g80) == -np.sign(F))).astype(float); RIDE = (OKG & (SGN * g80 > 0)).astype(float)
say(f"- Δ80 == 0 の本 {nz0}（a では tail=0 扱い・ここでは除外）")
assert np.all((AGREE[OKG] == (TAIL[OKG] == RIDE[OKG]).astype(float))), "agree != 1[tail==ride]"
say(f"- 恒等 agree = 1[tail == ride80] を assert OK（n{int(OKG.sum())}）。agree 比率 " + " / ".join(f"{wn} {AGREE[wm&OKG].mean():.2f}" for wn, wm in W.items()))
BLK = np.where(OKG, IVo * 2 + AGREE.astype(int), -1)

def within(v_, g):
    codes, uniq = pd.factorize(g); s = np.bincount(codes, weights=v_, minlength=len(uniq)); c = np.bincount(codes, minlength=len(uniq))
    return v_ - (s / c)[codes]
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    codes, uniq = pd.factorize(cl); k = Z.shape[1]; S = np.zeros((len(uniq), k))
    for j in range(k): S[:, j] = np.bincount(codes, weights=Z[:, j] * e, minlength=len(uniq))
    meat = S.T @ S; Gc = len(uniq); V = ZtZi @ meat @ ZtZi * (Gc / max(Gc - 1, 1)); return beta, V, Gc
def fe(y, mask, cols, iv, cl=None):
    mm = mask & (iv >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    k = len(cols)
    if mm.sum() < 30 or len(np.unique(iv[mm])) < 3: return dict(b=np.full(k, np.nan), se=np.full(k, np.nan), t=np.full(k, np.nan), V=np.full((k, k), np.nan), G=0, n=int(mm.sum()))
    yy = within(y[mm], iv[mm]); Z = np.column_stack([within(c[mm], iv[mm]) for c in cols])
    b, V, Gc = ols_cluster(yy, Z, (iv if cl is None else cl)[mm]); se = np.sqrt(np.clip(np.diag(V), 0, None))
    return dict(b=b, se=se, t=b / np.where(se > 0, se, np.nan), V=V, G=Gc, n=int(mm.sum()))

say("\n## B1 完全交差模型: FE(区間×agree) + tail + tail·agree + SELL + SELL·agree（クラスタ = 区間×agree ブロック／区間）")
B1 = {}
for wn, wm in W.items():
    m = wm & OKG
    r = fe(R, m, [TAIL, TAIL * AGREE, SELL, SELL * AGREE], BLK)                 # クラスタ=ブロック
    r2 = fe(R, m, [TAIL, TAIL * AGREE, SELL, SELL * AGREE], BLK, cl=IVo)       # クラスタ=区間（保守）
    b1 = r["b"][0] + r["b"][1]; se1 = math.sqrt(max(r["V"][0, 0] + r["V"][1, 1] + 2 * r["V"][0, 1], 0))
    B1[wn] = r
    say(f"- {wn}: β(agree=0) {r['b'][0]:+.4f} (t{r['t'][0]:+.2f})・β(agree=1) {b1:+.4f} (t{b1/se1:+.2f})・**差 tail·agree {r['b'][1]:+.4f} (t_blk {r['t'][1]:+.2f}・t_区間 {r2['t'][1]:+.2f})**・MDE 2·se {2*r['se'][1]:.3f}R・γ_SELL {r['b'][2]:+.3f}・γ·agree {r['b'][3]:+.3f}・ブロック {r['G']}・n{r['n']}")
# 区間 bootstrap（外・近年）: 区間を復元抽出・ブロック FE は区間内で再構成
for wn in ("外2021-26", "近年2024-26"):
    m = W[wn] & OKG; ids = np.unique(IVo[m]); idx_by = {i_: np.flatnonzero(m & (IVo == i_)) for i_ in ids}; NB = 1000; bs = np.full(NB, np.nan); tb = time.time()
    for bb in range(NB):
        pick = rng.choice(ids, size=len(ids), replace=True)
        rows = np.concatenate([idx_by[i_] for i_ in pick]); gid = np.concatenate([np.full(len(idx_by[i_]), kk) for kk, i_ in enumerate(pick)])
        blk = gid * 2 + AGREE[rows].astype(int)
        y = within(R[rows], blk); Z = np.column_stack([within(c[rows], blk) for c in (TAIL, TAIL * AGREE, SELL, SELL * AGREE)])
        bs[bb] = (np.linalg.pinv(Z.T @ Z) @ Z.T @ y)[1]
    say(f"- {wn} 区間 bootstrap（{time.time()-tb:.0f} s）: tail·agree 95% CI [{np.nanquantile(bs,0.025):+.4f}, {np.nanquantile(bs,0.975):+.4f}]・P(≤0) {np.nanmean(bs<=0):.3f}")

say("\n## B2 部分集合 β（各自 FE・区間クラスタ）: 外 年別・LOYO")
def sub(m, a):
    r = fe(R, m & (AGREE == a), [TAIL, SELL], IVo); return r
for y in range(2021, 2027):
    m = OKG & (YEAR == y); r1 = sub(m, 1); r0 = sub(m, 0)
    pos1 = (F[m & (AGREE == 1)] > 0).mean() if (m & (AGREE == 1)).any() else np.nan; pos0 = (F[m & (AGREE == 0)] > 0).mean() if (m & (AGREE == 0)).any() else np.nan
    say(f"- {y}: agree=1 β {r1['b'][0]:+.3f} (t{r1['t'][0]:+.2f}, 区間 {r1['G']}, n{r1['n']}, 正区間比 {pos1:.2f}) / agree=0 β {r0['b'][0]:+.3f} (t{r0['t'][0]:+.2f}, 区間 {r0['G']}, n{r0['n']}, 正区間比 {pos0:.2f})" + ("  ⑬" if (pos1 > 0.9 or pos1 < 0.1 or pos0 > 0.9 or pos0 < 0.1) else ""))
parts = []
for y in range(2021, 2027):
    m = W["外2021-26"] & OKG & (YEAR != y); r1 = sub(m, 1); r0 = sub(m, 0)
    d = r1["b"][0] - r0["b"][0]; se = math.sqrt(r1["se"][0] ** 2 + r0["se"][0] ** 2)
    parts.append(f"除{y} a1 {r1['b'][0]:+.3f}/a0 {r0['b'][0]:+.3f}・差 {d:+.3f} (t{d/se:+.2f})")
say("- 外 LOYO: " + " / ".join(parts))
m = W["外2021-26"] & OKG & (YEAR <= 2023); r1 = sub(m, 1); r0 = sub(m, 0)
say(f"- 外 2021-23 のみ: agree=1 β {r1['b'][0]:+.3f} (t{r1['t'][0]:+.2f}, 区間 {r1['G']}) / agree=0 β {r0['b'][0]:+.3f} (t{r0['t'][0]:+.2f}, 区間 {r0['G']})")
m = W["在2010-20"] & OKG
for lab, mm in (("在 2010-15", m & (YEAR <= 2015)), ("在 2016-20", m & (YEAR >= 2016))):
    r1 = sub(mm, 1); r0 = sub(mm, 0); say(f"- {lab}: agree=1 β {r1['b'][0]:+.3f} (t{r1['t'][0]:+.2f}, 区間 {r1['G']}) / agree=0 β {r0['b'][0]:+.3f} (t{r0['t'][0]:+.2f}, 区間 {r0['G']})")

say("\n## B3 加法統制との整合: 区間FE + tail + ride80 + SELL（17:40 b-B1 型）→ 2·β_g vs 部分集合差")
for wn, wm in W.items():
    m = wm & OKG; r = fe(R, m, [TAIL, RIDE, SELL], IVo)
    say(f"- {wn}: β_tail {r['b'][0]:+.4f} (t{r['t'][0]:+.2f})・β_ride80 {r['b'][1]:+.4f} (t{r['t'][1]:+.2f}) → 2·β_g {2*r['b'][1]:+.4f} vs 完全交差の差 {B1[wn]['b'][1]:+.4f}")
say("- 読み: 加法模型（区間内で同じ側の本を g80 の向きで比べる）の β_g と、完全交差の差（区間×状態ブロック間の対比）が食い違えば、差は本の『乗り』でなく時期（ブロック）組成の差。")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
