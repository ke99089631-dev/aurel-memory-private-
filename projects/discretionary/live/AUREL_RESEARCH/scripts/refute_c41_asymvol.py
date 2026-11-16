# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-16 14:15 反証レーン] 対象: cycle41 (12:55) の残存弱信号
  W1 補足 b「金の年別 γ は年間トレンドの符号に追随（Spearman ρ +0.69・p 0.002・符号一致 14/17）＝窓プール γ≈0 は反対符号の年の平均」
     と、それから導いた前向き 1 セル「γ1(s_d·r_d) > 0（s_d = sign(直近 60 有効日リターン)）」。
  W2 知識 (3)「同日 γ_c は金でも負で 2021+ に拡大（−2.8 → −6.7 → −8.7・t −2.5〜−7.4）」。
  W3 知識 (2)「金に翌日型の非対称は無い（在 −2.1・外 −0.2・MDE 2.6〜3.3）」＝ null をレジーム部分集合で壊せるか。
  W4 ゲート記述「上げ日の翌日は壁幅（log risk_bp）が 2.5〜3.5% 細い（t −6.6／−2.7）」。
  C1 US500 PASS・C2 XAU null・ゲート ㉛ 不通過 は争わない（事前固定セルの通り）。

=== 規則（数字を見る前に書く・Bonferroni は規則数 7 → 名目 |t| 2.69 / p 0.007 を併記）===
R1 関数形（W1・機械的交絡）: 年別 γ は |r| を**線形**で統制しているだけ。log RV の |r| 応答が非線形なら、年内の r 分布の歪み（上げ年は大きい |r| が上げ側）が
   γ に漏れ、年間リターンと機械的に相関する。→ |r| を 窓内五分位ダミー＋|r|＋|r|² で統制して年別 γ を再推定し ρ(γ, 年間リターン) を再計算。
   併せて ρ(γ, 年内 r の歪度)・ρ(γ, 年内 r² 加重残差) を印字。**ρ_flex < +0.30 または p > 0.05 → W1 broken（関数形の人工物）**。
R2 プラセボ（W1）: r_d の符号を日ごと iid ±1 で反転（|r| と y を保存・年間リターンも反転後の Σ s·r で再計算）して 年別 γ* と ρ* を 2000 回。
   帰無に符号情報は無いので、ρ* が +0.69 を超える頻度 p_perm が **> 0.025（Bonferroni 0.007 併記）→ W1 broken（符号情報なしで出る相関）**。
   機械的結合の診断 = Σ r² ũ / Σ r²（ũ = y の |r|・RV ラグ統制後残差）を年別に印字。
R3 F_t 可測版（W1 の前向きセルの在内検証）: y = ... + γ r + γ1 (s_d·r_d)、s_d = sign(lc_d − lc_{d−K})、K = 60／120／250 有効日。窓 在 2010-20／外 2021-26H1。
   陽性対照 = s を**その年の年間リターンの符号**（look-ahead）にした γ1_LA。**γ1_LA が在 t ≥ 2 なのに K=60 の γ1 が在 |t| < 2 または 外で符号逆 →
   W1 は look-ahead 相関（当年リターンは未来を含む）＝ 前向きセルは在内で既に不成立 → broken（予測的主張として）**。K=60 在 t ≥ 2 ∧ 外 同符号 t ≥ 1.5 → survived。
R4 脆弱性（W1）: LOYO（1 年抜き）の ρ の範囲・|t|≥2 の 4 年（2013/2019/2021/2025）を抜いた ρ・半年格子（γ_half × 半年リターン・n≈33）・四半期格子（n≈66）。
   **半年格子 ρ < +0.30 または p > 0.05 → fragile（別格子で立たない）**。
R5 同日 γ_c の格子依存（W2・bid 人工物の間接検査）: RV_d を 5 分／15 分／30 分／60 分の終値格子で計算し同日 γ_c を再推定（在／外／近年）。
   bid 気配の広がり（下げ日に bid が過剰に跳ねる）なら粗い格子で |γ_c| が縮む。**60 分格子の |γ_c| が 5 分の 50% 未満 → W2 は人工物に整合（broken as 市場事実）**。
   US500 を対照（本物のレバレッジ効果なら格子で縮まないはず）。翌日型 γ も同時に印字（格子で変わらないことの確認）。
R6 レジーム部分集合（W3 null を壊す試み）: 在／外 × {lrv5 三分位 低/中/高}・{s60 上昇/下降}・{brk なし・NFP なし} の γ（NW t）。セル数 10×2 → Bonferroni |t| 2.81。
   **在で |t| ≥ 2.81 ∧ 外で同符号 t ≥ 1.5 の部分集合があれば W3 null は weakened**；無ければ W3 survived。
R7 壁幅（W4）: scan 本の log risk_bp を UP/DOWN ダミー＋前日 log RV_d＋mean log RV_{d−4..d}＋年ダミーで回帰（在／外）。
   **UP−DOWN 係数が RV 統制で 50% 以上縮む → 「ボラ経由」（W4 は翌日ボラの別名・独立の記述ではない）**；縮まなければ独立の記述として survived。
データ: data/macro/XAU_m5_close.npz・US500_m5_close.npz・data/refute_c4_scan_paths_2010_2026.json（既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し）。seed 20261116.
"""
import os, time, json, math, datetime as dt
import numpy as np, pandas as pd
from scipy.stats import spearmanr, skew

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c41_asymvol.md"); NY = "America/New_York"
rng = np.random.default_rng(20261116); NFMIN = 100; NPERM = 2000; NWLAG = 5
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c41] ボラ非対称の残存弱信号 W1〜W4 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c41_asymvol.py)")

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
NFP = {d.date().toordinal() for d in nfp_dates_v2()}

def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.asarray(X, float); n = len(y)
    Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.pinv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None]); V_hc = XtX_inv @ Sm @ XtX_inv * n / max(n - Z.shape[1], 1)
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv
    return b, np.sqrt(np.abs(np.diag(V))), np.sqrt(np.abs(np.diag(V_hc))), u
def hc1(y, X):
    b, se, se_hc, u = nw_ols(y, X, lag=0); return b, se_hc, u

# ---------- session daily table with multi-grid RV ----------
def daily_table(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep], "r2": r[keep] ** 2, "ts": ts[keep]})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()})
    # coarser grids: subsample non-flat closes at the last bar of each 15/30/60-min calendar bucket within the session day
    for M in (15, 30, 60):
        bucket = (df["ts"] // (M * 60))
        last = df.groupby(["o", bucket], sort=True)["lc"].last().reset_index()
        last["d"] = last.groupby("o")["lc"].diff()
        D[f"rv{M}"] = last.groupby("o")["d"].apply(lambda s: float(np.nansum(s.to_numpy() ** 2)))
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"] = D["date"].dt.weekday
    D = D[(D.wd <= 4) & (D.nf >= NFMIN)].reset_index()
    D["lrv"] = np.log(D["rv"])
    for M in (15, 30, 60): D[f"lrv{M}"] = np.log(D[f"rv{M}"].replace(0, np.nan))
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["gap"] = np.r_[np.nan, np.diff(D["o"].to_numpy())]; D["lrv5"] = D["lrv"].rolling(5).mean()
    D["year"] = D["date"].dt.year; D["half"] = D["year"] * 10 + (D["date"].dt.month > 6).astype(int)
    D["qtr"] = D["year"] * 10 + (D["date"].dt.month - 1) // 3
    D["nfp"] = D["o"].isin(NFP)
    for K in (60, 120, 250):
        D[f"s{K}"] = np.sign(D["lc_last"] - D["lc_last"].shift(K))
    say(f"- {sym}: 有効セッション日 {len(D)}・{D.date.min().date()}〜{D.date.max().date()}")
    return D

def build_xy(D):
    n = len(D); t = slice(0, n - 1); t1 = slice(1, n)
    V = pd.DataFrame({"y": D["lrv"].to_numpy()[t1], "lrv": D["lrv"].to_numpy()[t], "lrv5": D["lrv5"].to_numpy()[t],
                      "r": D["r"].to_numpy()[t], "brk": D["gap"].to_numpy()[t1] > 1,
                      "nfp": D["nfp"].to_numpy()[t1] | D["nfp"].to_numpy()[t], "year": D["year"].to_numpy()[t],
                      "half": D["half"].to_numpy()[t], "qtr": D["qtr"].to_numpy()[t],
                      "s60": D["s60"].to_numpy()[t], "s120": D["s120"].to_numpy()[t], "s250": D["s250"].to_numpy()[t],
                      "lc": D["lc_last"].to_numpy()[t]})
    V["ar"] = V.r.abs()
    ok = np.isfinite(V.y) & np.isfinite(V.lrv) & np.isfinite(V.lrv5) & np.isfinite(V.r)
    return V[ok].reset_index(drop=True)

def period_ret(D, col):
    g = D.groupby(col)["lc_last"]; return ((g.last() - g.first()) * 100)

def gamma_by_period(V, col, flex=False, qbins=None, rcol="r", min_n=100):
    rows = []
    for p, v in V.groupby(col):
        if len(v) < min_n: continue
        X = [v.lrv, v.lrv5, v.ar]
        if flex:
            X += [v.ar ** 2] + [(qbins[v.index] == q).astype(float) for q in range(1, 5)]
        X = np.column_stack(X + [v[rcol]])
        b, se, u = hc1(v.y.to_numpy(), X)
        rows.append((p, b[-1] * 1e4, b[-1] / se[-1] if se[-1] > 0 else np.nan, len(v)))
    return pd.DataFrame(rows, columns=["p", "g", "t", "n"]).set_index("p")

XAU = daily_table("XAU"); US = daily_table("US500")
VX = build_xy(XAU); VU = build_xy(US)
rets_year = period_ret(XAU, "year")

# ================= R1: functional form =================
say("## R1 関数形: 年別 γ の |r| 統制を 線形 → 五分位ダミー＋|r|＋|r|² に変えて ρ(γ_year, 年間リターン) を再計算（XAU 2010-26）")
G_lin = gamma_by_period(VX, "year")
qb = pd.qcut(VX.ar, 5, labels=False).to_numpy()
G_flex = gamma_by_period(VX, "year", flex=True, qbins=qb)
T = pd.DataFrame({"g_lin": G_lin.g, "t_lin": G_lin.t, "g_flex": G_flex.g, "t_flex": G_flex.t}).join(rets_year.rename("ret"))
sk = VX.groupby("year")["r"].apply(lambda s: skew(s.to_numpy())); T["sk_r"] = sk
# r²-weighted residual (coupling diagnostic): residual of y on [lrv, lrv5, ar] within year
cw = {}
for yy, v in VX.groupby("year"):
    if len(v) < 100: continue
    b, se, u = hc1(v.y.to_numpy(), np.column_stack([v.lrv, v.lrv5, v.ar])); cw[yy] = float((v.r ** 2 * u).sum() / (v.r ** 2).sum())
T["r2w_resid"] = pd.Series(cw)
rho_lin, p_lin = spearmanr(T.g_lin, T.ret); rho_flex, p_flex = spearmanr(T.g_flex, T.ret)
rho_sk, p_sk = spearmanr(T.g_lin, T.sk_r); rho_sk_ret, p_sk_ret = spearmanr(T.sk_r, T.ret); rho_cw, p_cw = spearmanr(T.g_lin, T.r2w_resid)
same_lin = int((np.sign(T.g_lin) == np.sign(T.ret)).sum()); same_flex = int((np.sign(T.g_flex) == np.sign(T.ret)).sum())
say(f"- 再現 線形: ρ {rho_lin:+.2f} (p {p_lin:.3f})・符号一致 {same_lin}/{len(T)}（c41b は +0.69・14/17）")
say(f"- **柔軟統制: ρ_flex {rho_flex:+.2f} (p {p_flex:.3f})・符号一致 {same_flex}/{len(T)}**")
say(f"- 診断: ρ(γ_lin, 年内 r 歪度) {rho_sk:+.2f} (p {p_sk:.3f})・ρ(歪度, 年間リターン) {rho_sk_ret:+.2f} (p {p_sk_ret:.3f})・ρ(γ_lin, r² 加重残差) {rho_cw:+.2f} (p {p_cw:.3f})")
say("| 年 | γ_lin (t) | γ_flex (t) | 年間リターン % | r 歪度 | r² 加重残差 |"); say("|---|---|---|---|---|---|")
for yy, a in T.iterrows(): say(f"| {yy} | {a.g_lin:+.1f} ({a.t_lin:+.1f}) | {a.g_flex:+.1f} ({a.t_flex:+.1f}) | {a.ret:+.0f} | {a.sk_r:+.2f} | {a.r2w_resid:+.3f} |")
R1_broken = (rho_flex < 0.30) or (p_flex > 0.05)
say(f"- R1 判定: {'**broken（関数形で消える）**' if R1_broken else 'survived（柔軟統制でも残る）'}")
say()

# ================= R2: sign-flip placebo for rho =================
say("## R2 プラセボ: r_d の符号を iid ±1 で反転（|r|・y 保存）→ 年別 γ*・年間リターン* = Σ s·r → ρ* を 2000 回")
years = sorted(VX.year.unique()); Yidx = {yy: VX.index[VX.year == yy].to_numpy() for yy in years if (VX.year == yy).sum() >= 100}
pre = {}
for yy, idx in Yidx.items():
    v = VX.loc[idx]; Z0 = np.column_stack([np.ones(len(v)), v.lrv, v.lrv5, v.ar]); pre[yy] = (Z0, v.y.to_numpy(), v.r.to_numpy())
rho_star = np.empty(NPERM); g_star_sd = []
for k in range(NPERM):
    gs = []; rs = []
    for yy, (Z0, y, r) in pre.items():
        s = rng.choice([-1.0, 1.0], size=len(y)); Z = np.column_stack([Z0, s * r])
        b = np.linalg.lstsq(Z, y, rcond=None)[0]; gs.append(b[-1] * 1e4); rs.append((s * r).sum() / 1e2)
    rho_star[k] = spearmanr(gs, rs)[0]
p_perm = float((rho_star >= rho_lin).mean()); p_perm2 = float((np.abs(rho_star) >= abs(rho_lin)).mean())
say(f"- ρ* 平均 {rho_star.mean():+.3f}・sd {rho_star.std():.3f}・5/95% {np.percentile(rho_star,5):+.2f}/{np.percentile(rho_star,95):+.2f}・**P(ρ* ≥ {rho_lin:+.2f}) = {p_perm:.4f}**（両側 {p_perm2:.4f}）")
R2_broken = p_perm > 0.025
say(f"- R2 判定: {'**broken（符号情報なしで同じ ρ が出る）**' if R2_broken else 'survived（プラセボは再現しない）'}" + ("・Bonferroni 0.007 では " + ("不通過" if p_perm > 0.007 else "通過")))
say()

# ================= R3: F_t-measurable interaction =================
say("## R3 F_t 可測の状態 s_d との交互作用: y = α + φ1 lrv + φ5 lrv5 + β|r| + γ r + γ1 (s_d·r)（HC1 t／NW t）")
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
ysign = np.sign(rets_year); VX["sLA"] = VX.year.map(ysign)
say("| 窓 | n | γ ×1e4 (HC1 t) | γ1 K=60 (HC1 t／NW t) | γ1 K=120 (t) | γ1 K=250 (t) | 陽性対照 γ1_LA 当年符号 (t) | 2sd_r·γ1_60 |"); say("|---|---|---|---|---|---|---|---|")
R3 = {}
for wn, (y0, y1) in WIN.items():
    v = VX[(VX.year >= y0) & (VX.year <= y1) & np.isfinite(VX.s250)].reset_index(drop=True); cells = {}
    for K in ("s60", "s120", "s250", "sLA"):
        X = np.column_stack([v.lrv, v.lrv5, v.ar, v.r, v[K] * v.r]); b, se, se_hc, u = nw_ols(v.y.to_numpy(), X)
        cells[K] = (b[5] * 1e4, b[5] / se_hc[5], b[5] / se[5], b[4] * 1e4, b[4] / se_hc[4])
    R3[wn] = cells
    say(f"| {wn} | {len(v)} | {cells['s60'][3]:+.2f} ({cells['s60'][4]:+.2f}) | **{cells['s60'][0]:+.2f} ({cells['s60'][1]:+.2f}／{cells['s60'][2]:+.2f})** | {cells['s120'][0]:+.2f} ({cells['s120'][1]:+.2f}) | {cells['s250'][0]:+.2f} ({cells['s250'][1]:+.2f}) | {cells['sLA'][0]:+.2f} ({cells['sLA'][1]:+.2f}) | {2*v.r.std()*cells['s60'][0]/1e4:+.3f} |")
# same for US500 as control
vU = VU[(VU.year >= 2014) & np.isfinite(VU.s250)].reset_index(drop=True); ysU = np.sign(period_ret(US, "year")); vU["sLA"] = vU.year.map(ysU)
cu = {}
for K in ("s60", "sLA"):
    X = np.column_stack([vU.lrv, vU.lrv5, vU.ar, vU.r, vU[K] * vU.r]); b, se, se_hc, u = nw_ols(vU.y.to_numpy(), X); cu[K] = (b[5] * 1e4, b[5] / se_hc[5])
say(f"- 対照 US500 2014-26: γ1 K=60 {cu['s60'][0]:+.2f} (t {cu['s60'][1]:+.2f})・γ1_LA {cu['sLA'][0]:+.2f} (t {cu['sLA'][1]:+.2f})")
a = R3["在 2010-20"]; o = R3["外 2021-26H1"]
R3_surv = (a["s60"][0] > 0) and (a["s60"][1] >= 2) and (o["s60"][0] > 0) and (o["s60"][1] >= 1.5)
R3_la_only = (a["sLA"][1] >= 2) and ((abs(a["s60"][1]) < 2) or (np.sign(o["s60"][0]) != np.sign(a["s60"][0])))
say(f"- R3 判定: {'survived（F_t 可測の状態で在外とも正）' if R3_surv else ('**broken（look-ahead 相関: 当年符号では立つが trailing では立たない／外で符号逆）**' if R3_la_only else 'inconclusive（当年符号でも立たない＝R1/R2 と整合・W1 は在内で検出不能）')}")
say()

# ================= R4: fragility =================
say("## R4 脆弱性: LOYO・|t|≥2 の 4 年抜き・半年格子・四半期格子（線形統制・XAU）")
loyo = [spearmanr(T.g_lin.drop(yy), T.ret.drop(yy))[0] for yy in T.index]
drop4 = [y for y in (2013, 2019, 2021, 2025) if y in T.index]; r4, p4 = spearmanr(T.g_lin.drop(drop4), T.ret.drop(drop4))
Gh = gamma_by_period(VX, "half", min_n=60); rh = period_ret(XAU, "half"); Th = Gh.join(rh.rename("ret")).dropna(); rho_h, p_h = spearmanr(Th.g, Th.ret)
Gq = gamma_by_period(VX, "qtr", min_n=40); rq = period_ret(XAU, "qtr"); Tq = Gq.join(rq.rename("ret")).dropna(); rho_q, p_q = spearmanr(Tq.g, Tq.ret)
# in/out split at year grid
ri, pi_ = spearmanr(T.g_lin[T.index <= 2020], T.ret[T.index <= 2020]); ro, po = spearmanr(T.g_lin[T.index >= 2021], T.ret[T.index >= 2021])
# US500 half-year control
GhU = gamma_by_period(VU[VU.year >= 2014], "half", min_n=60); rhU = period_ret(US[US.year >= 2014], "half"); ThU = GhU.join(rhU.rename("ret")).dropna(); rho_hU, p_hU = spearmanr(ThU.g, ThU.ret)
say(f"- LOYO ρ 範囲 {min(loyo):+.2f}〜{max(loyo):+.2f}・4 年（{drop4}）抜き ρ {r4:+.2f} (p {p4:.3f}・n {len(T)-len(drop4)})")
say(f"- 年格子 在 2010-20 ρ {ri:+.2f} (p {pi_:.3f}・n 11)／外 2021-26 ρ {ro:+.2f} (p {po:.3f}・n {int((T.index>=2021).sum())})")
say(f"- **半年格子 ρ {rho_h:+.2f} (p {p_h:.3f}・n {len(Th)})・符号一致 {int((np.sign(Th.g)==np.sign(Th.ret)).sum())}/{len(Th)}**／四半期格子 ρ {rho_q:+.2f} (p {p_q:.3f}・n {len(Tq)})・符号一致 {int((np.sign(Tq.g)==np.sign(Tq.ret)).sum())}/{len(Tq)}")
say(f"- 対照 US500 半年格子 ρ {rho_hU:+.2f} (p {p_hU:.3f}・n {len(ThU)})")
R4_fragile = (rho_h < 0.30) or (p_h > 0.05)
say(f"- R4 判定: {'**fragile（半年格子で立たない）**' if R4_fragile else 'survived（半年格子でも残る）'}")
say()

# ================= R5: same-day gamma_c vs sampling grid =================
say("## R5 同日 γ_c の格子依存（W2）: RV_d を 5/15/30/60 分格子で計算し γ_c（log RV_d on r_d, |r_d|, log RV_{d−1}, mean log RV_{d−5..d−1}）を再推定")
def gamma_c_grid(D, y0, y1, col):
    d = D[(D.year >= y0) & (D.year <= y1)].reset_index(drop=True)
    y = d[col].to_numpy()[1:]; X = np.column_stack([d["lrv"].to_numpy()[:-1], d["lrv5"].to_numpy()[:-1], np.abs(d["r"].to_numpy()[1:]), d["r"].to_numpy()[1:]])
    ok = np.isfinite(y) & np.isfinite(X).all(1); b, se, se_hc, u = nw_ols(y[ok], X[ok]); return b[4] * 1e4, b[4] / se[4], int(ok.sum())
def gamma_next_grid(D, y0, y1, col):
    d = D[(D.year >= y0) & (D.year <= y1)].reset_index(drop=True)
    y = d[col].to_numpy()[1:]; X = np.column_stack([d["lrv"].to_numpy()[:-1], d["lrv5"].to_numpy()[:-1], np.abs(d["r"].to_numpy()[:-1]), d["r"].to_numpy()[:-1]])
    ok = np.isfinite(y) & np.isfinite(X).all(1); b, se, se_hc, u = nw_ols(y[ok], X[ok]); return b[4] * 1e4, b[4] / se[4]
say("| 銘柄 | 窓 | γ_c 5分 (NW t) | 15分 | 30分 | 60分 | 60分/5分 | 翌日 γ 5分 (t) | 翌日 γ 60分 (t) |"); say("|---|---|---|---|---|---|---|---|---|")
R5 = {}
for sym, D, wins in (("XAU", XAU, WIN), ("US500", US, {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)})):
    for wn, (y0, y1) in wins.items():
        gs = {M: gamma_c_grid(D, y0, y1, "lrv" if M == 5 else f"lrv{M}") for M in (5, 15, 30, 60)}
        gn5 = gamma_next_grid(D, y0, y1, "lrv"); gn60 = gamma_next_grid(D, y0, y1, "lrv60")
        ratio = gs[60][0] / gs[5][0] if gs[5][0] != 0 else np.nan; R5[(sym, wn)] = (gs, ratio)
        say(f"| {sym} | {wn} | {gs[5][0]:+.2f} ({gs[5][1]:+.2f}) | {gs[15][0]:+.2f} ({gs[15][1]:+.2f}) | {gs[30][0]:+.2f} ({gs[30][1]:+.2f}) | **{gs[60][0]:+.2f} ({gs[60][1]:+.2f})** | {ratio:.2f} | {gn5[0]:+.2f} ({gn5[1]:+.2f}) | {gn60[0]:+.2f} ({gn60[1]:+.2f}) |")
rx = [R5[("XAU", w)][1] for w in ("外 2021-26H1", "近年 2024-26H1")]
R5_art = all(abs(x) < 0.5 for x in rx)
say(f"- R5 判定（XAU 外・近年の 60分/5分 比 {rx[0]:.2f}／{rx[1]:.2f}）: {'**broken as 市場事実（粗い格子で半分以下＝bid 人工物に整合）**' if R5_art else ('survived（格子で縮まない＝微細構造でなく日内分散の形）' if all(abs(x) >= 0.8 for x in rx) else 'inconclusive（一部縮む）')}")
say()

# ================= R6: regime subsets to break the XAU null =================
say("## R6 レジーム部分集合（W3 null を壊す試み・XAU 翌日 γ・NW t・Bonferroni 20 セル |t| 2.81）")
def fit_g(v):
    if len(v) < 100: return (np.nan, np.nan, len(v))
    X = np.column_stack([v.lrv, v.lrv5, v.ar, v.r]); b, se, se_hc, u = nw_ols(v.y.to_numpy(), X); return (b[4] * 1e4, b[4] / se[4], len(v))
say("| 部分集合 | 在 γ (t・n) | 外 γ (t・n) |"); say("|---|---|---|")
hits = []
for wn_pair in [("在 2010-20", "外 2021-26H1")]:
    vi = VX[(VX.year >= 2010) & (VX.year <= 2020)]; vo = VX[(VX.year >= 2021)]
    subs = {}
    for name, vv in (("在", vi), ("外", vo)):
        q = pd.qcut(vv.lrv5, 3, labels=False)
        subs.setdefault("lrv5 低", {})[name] = vv[q == 0]; subs.setdefault("lrv5 中", {})[name] = vv[q == 1]; subs.setdefault("lrv5 高", {})[name] = vv[q == 2]
        subs.setdefault("s60 上昇", {})[name] = vv[vv.s60 > 0]; subs.setdefault("s60 下降", {})[name] = vv[vv.s60 < 0]
        subs.setdefault("s250 上昇", {})[name] = vv[vv.s250 > 0]; subs.setdefault("s250 下降", {})[name] = vv[vv.s250 < 0]
        subs.setdefault("brk なし ∧ NFP なし", {})[name] = vv[~vv.brk & ~vv.nfp]
        subs.setdefault("|r| 上位 1/3", {})[name] = vv[vv.ar >= vv.ar.quantile(2 / 3)]
        subs.setdefault("|r| 下位 2/3", {})[name] = vv[vv.ar < vv.ar.quantile(2 / 3)]
    for name, dd in subs.items():
        gi = fit_g(dd["在"].reset_index(drop=True)); go = fit_g(dd["外"].reset_index(drop=True))
        hit = (abs(gi[1]) >= 2.81) and (np.sign(go[0]) == np.sign(gi[0])) and (abs(go[1]) >= 1.5)
        if hit: hits.append(name)
        say(f"| {name} | {gi[0]:+.2f} ({gi[1]:+.2f}・{gi[2]}) | {go[0]:+.2f} ({go[1]:+.2f}・{go[2]}) |{' ←' if hit else ''}")
say(f"- R6 判定: {('**W3 null weakened（' + '、'.join(hits) + '）**') if hits else 'W3 null survived（在 Bonferroni 通過 ∧ 外 同符号 の部分集合なし）'}")
say()

# ================= R7: wall width vs prior-day sign, controlling RV =================
say("## R7 壁幅（W4）: log risk_bp on UP ダミー（＋前日 log RV_d・mean log RV_{d−4..d}・年ダミー）")
try:
    d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); tr = pd.DataFrame(d["trades"])
    e_ny = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(NY)
    tr["so"] = ((e_ny + pd.Timedelta(hours=6)).dt.tz_localize(None).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal())
    ords = XAU["o"].to_numpy(); pos = np.searchsorted(ords, tr["so"].to_numpy(), side="left") - 1; okp = pos >= 0; pc = np.clip(pos, 0, len(ords) - 1)
    tr["r_prev"] = np.where(okp, XAU["r"].to_numpy()[pc], np.nan); tr["lrv_prev"] = np.where(okp, XAU["lrv"].to_numpy()[pc], np.nan); tr["lrv5_prev"] = np.where(okp, XAU["lrv5"].to_numpy()[pc], np.nan)
    z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    et = tr["entry_time"].to_numpy(np.int64) - 300; pp = np.clip(np.searchsorted(ts, et), 0, len(ts) - 1); tr["P"] = C[pp]; tr["lrisk_bp"] = np.log(tr["risk"] / tr["P"] * 1e4)
    tr = tr[np.isfinite(tr.r_prev) & np.isfinite(tr.lrv_prev) & np.isfinite(tr.lrv5_prev) & (tr.r_prev != 0)]
    say("| 窓 | n | UP−DOWN 生 (HC1 t) | +RV 統制 (t) | +RV+年ダミー (t) | 縮み率 (RV) | β lrv_prev (t) |"); say("|---|---|---|---|---|---|---|")
    R7 = {}
    for wn, m in (("在 2010-20", tr.year <= 2020), ("外 2021-26H1", tr.year >= 2021)):
        s = tr[m]; up = (s.r_prev > 0).astype(float).to_numpy(); y = s.lrisk_bp.to_numpy()
        b0, se0, _ = hc1(y, up[:, None]); b1, se1, _ = hc1(y, np.column_stack([up, s.lrv_prev, s.lrv5_prev]))
        yd = pd.get_dummies(s.year, drop_first=True).to_numpy(float); b2, se2, _ = hc1(y, np.column_stack([up, s.lrv_prev, s.lrv5_prev, yd]))
        shrink = 1 - b1[1] / b0[1] if b0[1] != 0 else np.nan; R7[wn] = shrink
        say(f"| {wn} | {len(s)} | {b0[1]:+.4f} ({b0[1]/se0[1]:+.1f}) | **{b1[1]:+.4f} ({b1[1]/se1[1]:+.1f})** | {b2[1]:+.4f} ({b2[1]/se2[1]:+.1f}) | {shrink*100:+.0f}% | {b1[2]:+.3f} ({b1[2]/se1[2]:+.1f}) |")
    R7_via = R7["在 2010-20"] >= 0.5
    say(f"- R7 判定: {'**ボラ経由（RV 統制で半減以上＝W4 は翌日ボラの別名）**' if R7_via else 'survived（RV 統制でも残る＝独立の記述）'}")
except Exception as e:
    say(f"- R7 実行不能: {e!r}"); R7_via = None
say()

say("## 総合（規則は docstring に先に書いた）")
say(f"- W1 年別 γ × 年間リターン: R1 {'broken' if R1_broken else 'survived'}（ρ_flex {rho_flex:+.2f} p {p_flex:.3f}）／R2 {'broken' if R2_broken else 'survived'}（p_perm {p_perm:.4f}）／R3 {'survived' if R3_surv else ('broken' if R3_la_only else 'inconclusive')}（在 γ1_60 t {a['s60'][1]:+.2f}・外 {o['s60'][1]:+.2f}・LA 在 t {a['sLA'][1]:+.2f}）／R4 {'fragile' if R4_fragile else 'survived'}（半年 ρ {rho_h:+.2f} p {p_h:.3f}）")
say(f"- W2 同日 γ_c: R5 {'broken as 市場事実' if R5_art else 'survived/inconclusive'}（60分/5分 比 外 {rx[0]:.2f}・近年 {rx[1]:.2f}）")
say(f"- W3 null: R6 {'weakened' if hits else 'survived'}")
say(f"- W4 壁幅: R7 {'ボラ経由' if R7_via else ('survived' if R7_via is not None else 'n/a')}")
say(f"所要 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
