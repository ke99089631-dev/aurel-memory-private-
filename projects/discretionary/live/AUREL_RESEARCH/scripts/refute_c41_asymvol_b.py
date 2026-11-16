# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-16 反証レーン・追撃 b] refute_c41_asymvol.py の R3/R6 で W1 の F_t 可測版（γ1(s60·r) > 0・在 t 3.19／外 2.91）と
「s60 下降で γ −6.8／−8.0（t −3.9／−3.3）」が残った。これを壊す追加規則（数字を見る前に書く）:
B1 省略変数: 状態 s の水準 δ0·s と 状態×大きさ δ1·s·|r| を同時に入れる（下降局面で |r| 応答の傾きが違えば、r の歪みを通じて γ1 に漏れる）。
   さらに |r| を五分位ダミー＋|r|² にした柔軟版も。**γ1 が 在 |t| < 2 に落ちる → broken（状態×大きさの別名）**。
B2 片側性: 上昇局面 γ_up と 下降局面 γ_dn を別推定。研究レーンの読み「符号がトレンド方向に乗る」は γ_up > 0 ∧ γ_dn < 0 を要求。
   **γ_up が 在・外とも t < 1.5 → 「符号追随」は half-broken（下降局面のレバレッジ効果のみ・上げ側は帰無）**。
B3 LOYO（下降局面セル）: 在の下降局面 γ_dn を 1 年ずつ抜いて再推定・2013 と 2021 を同時に抜いた外/在。**抜いて |t| < 2 になる年があれば「局在」**。
B4 状態の定義: K = 20／40／60／120・直近 5 日を除いた s60_lag5（r_d 自身・lrv5 窓との重なりを切る）・s を |60 日リターン| が中央値以上の日に限る（弱トレンドを除く）。
B5 シフト・プラセボ: s60 系列を 250〜(n−250) 日の循環シフトで 1000 回ずらし γ1 の |t| 分布 → **P(|t*| ≥ 実測) > 0.025 → broken（状態の自己相関が作る見かけ）**。
B6 半年格子を 在/外 で分割（R4 の続き）・年格子 在のみ p。
B7 US500 を同じ B1/B2 で（対照: 株は γ_up・γ_dn とも負のはず）。
データ・seed は本体と同じ。
"""
import os, time, math, datetime as dt, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c41_asymvol_b.md"); NY = "America/New_York"; rng = np.random.default_rng(20261116); L = []; T0 = time.time()
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c41 追撃 b] 状態依存 γ1 の省略変数・片側性・局在・プラセボ — {time.strftime('%Y-%m-%d %H:%M')}")
def nw_ols(y, X, lag=5):
    y = np.asarray(y, float); X = np.asarray(X, float); n = len(y); Z = np.column_stack([np.ones(n), X]); Xi = np.linalg.pinv(Z.T @ Z)
    b = Xi @ Z.T @ y; u = y - Z @ b; Sm = (Z * u[:, None]).T @ (Z * u[:, None]); Vh = Xi @ Sm @ Xi * n / max(n - Z.shape[1], 1)
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = Xi @ Sm @ Xi; return b, np.sqrt(np.abs(np.diag(V))), np.sqrt(np.abs(np.diag(Vh))), u
def daily(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); keep = r != 0
    sess = (pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY) + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    so = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    df = pd.DataFrame({"o": so[keep], "lc": lc[keep], "r2": r[keep] ** 2}); g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()}).reset_index()
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.o]); D = D[(D.date.dt.weekday <= 4) & (D.nf >= 100)].reset_index(drop=True)
    D["lrv"] = np.log(D.rv); D["r"] = np.r_[np.nan, np.diff(D.lc)] * 1e4; D["lrv5"] = D.lrv.rolling(5).mean(); D["year"] = D.date.dt.year
    D["half"] = D.year * 10 + (D.date.dt.month > 6).astype(int)
    for K in (20, 40, 60, 120): D[f"s{K}"] = np.sign(D.lc - D.lc.shift(K))
    D["s60_lag5"] = np.sign(D.lc.shift(5) - D.lc.shift(65)); D["m60"] = (D.lc - D.lc.shift(60)).abs()
    return D
def xy(D):
    n = len(D); t = slice(0, n - 1); t1 = slice(1, n); cols = {"y": D.lrv.to_numpy()[t1]}
    for c in ("lrv", "lrv5", "r", "year", "half", "s20", "s40", "s60", "s120", "s60_lag5", "m60"): cols[c] = D[c].to_numpy()[t]
    V = pd.DataFrame(cols); V["ar"] = V.r.abs(); ok = np.isfinite(V.y) & np.isfinite(V.lrv) & np.isfinite(V.lrv5) & np.isfinite(V.r); return V[ok].reset_index(drop=True)
def g1(v, s="s60", level=True, mag=True, flex=False):
    cols = [v.lrv, v.lrv5, v.ar]
    if flex: q = pd.qcut(v.ar, 5, labels=False).to_numpy(); cols += [v.ar ** 2] + [(q == k).astype(float) for k in range(1, 5)]
    cols += [v.r]
    if level: cols.append(v[s])
    if mag: cols.append(v[s] * v.ar)
    cols.append(v[s] * v.r); X = np.column_stack(cols); b, se, seh, u = nw_ols(v.y.to_numpy(), X); return b[-1] * 1e4, b[-1] / seh[-1], b[-1] / se[-1]
def gam(v):
    if len(v) < 100: return (np.nan, np.nan, len(v))
    X = np.column_stack([v.lrv, v.lrv5, v.ar, v.r]); b, se, seh, u = nw_ols(v.y.to_numpy(), X); return b[4] * 1e4, b[4] / se[4], len(v)

X_ = daily("XAU"); VX = xy(X_); U_ = daily("US500"); VU = xy(U_)
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026)}
def win(V, y0, y1, s="s120"): return V[(V.year >= y0) & (V.year <= y1) & np.isfinite(V[s])].reset_index(drop=True)

say("## B1 省略変数（XAU・γ1 ×1e4・HC1 t／NW t）: 基本 → +δ0 s → +δ1 s|r| → 両方 → 両方＋柔軟 |r|")
say("| 窓 | 基本 | +s 水準 | +s·\\|r\\| | +両方 | +両方+柔軟 |"); say("|---|---|---|---|---|---|")
B1 = {}
for wn, (y0, y1) in WIN.items():
    v = win(VX, y0, y1); c = [g1(v, level=False, mag=False), g1(v, level=True, mag=False), g1(v, level=False, mag=True), g1(v), g1(v, flex=True)]; B1[wn] = c
    say(f"| {wn} | {c[0][0]:+.2f} ({c[0][1]:+.2f}) | {c[1][0]:+.2f} ({c[1][1]:+.2f}) | {c[2][0]:+.2f} ({c[2][1]:+.2f}) | **{c[3][0]:+.2f} ({c[3][1]:+.2f}／{c[3][2]:+.2f})** | {c[4][0]:+.2f} ({c[4][1]:+.2f}) |")
B1_broken = abs(B1["在 2010-20"][3][1]) < 2
say(f"- B1 判定: {'**broken（状態×大きさ・水準の別名）**' if B1_broken else 'survived（省略変数を入れても γ1 残る）'}")
say()

say("## B2 片側性: 上昇局面 γ_up／下降局面 γ_dn（s60・NW t・n）と US500 対照")
say("| 銘柄 | 窓 | γ_up (t・n) | γ_dn (t・n) | 2sd_r·γ_dn |"); say("|---|---|---|---|---|")
B2 = {}
for sym, V, wins in (("XAU", VX, WIN), ("US500", VU, {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026)})):
    for wn, (y0, y1) in wins.items():
        v = win(V, y0, y1, "s60"); gu = gam(v[v.s60 > 0].reset_index(drop=True)); gd = gam(v[v.s60 < 0].reset_index(drop=True)); B2[(sym, wn)] = (gu, gd)
        say(f"| {sym} | {wn} | {gu[0]:+.2f} ({gu[1]:+.2f}・{gu[2]}) | **{gd[0]:+.2f} ({gd[1]:+.2f}・{gd[2]})** | {2*v.r.std()*gd[0]/1e4:+.3f} |")
up_null = all(B2[("XAU", w)][0][1] < 1.5 for w in WIN)
say(f"- B2 判定: {'**half-broken（上げ側 γ_up は在外とも t < 1.5＝「符号追随」でなく「下降局面のレバレッジ効果」）**' if up_null else 'survived（上げ側も立つ）'}")
say()

say("## B3 LOYO（下降局面 γ_dn・在 2010-20・NW t）")
v = win(VX, 2010, 2020, "s60"); vd = v[v.s60 < 0]
rows = []
for yy in sorted(vd.year.unique()):
    g = gam(vd[vd.year != yy].reset_index(drop=True)); rows.append(f"除{yy} {g[0]:+.1f} (t {g[1]:+.2f})")
say("- " + "・".join(rows))
yrs = vd.groupby("year").size(); say(f"- 下降局面の年別件数: " + "・".join(f"{y} {n}" for y, n in yrs.items()))
g13 = gam(vd[vd.year != 2013].reset_index(drop=True)); vo = win(VX, 2021, 2026, "s60"); vdo = vo[vo.s60 < 0]; g21 = gam(vdo[vdo.year != 2021].reset_index(drop=True))
yrs_o = vdo.groupby("year").size(); say(f"- 外 下降局面 年別件数: " + "・".join(f"{y} {n}" for y, n in yrs_o.items()))
say(f"- **在 除 2013: {g13[0]:+.2f} (t {g13[1]:+.2f}・n {g13[2]})／外 除 2021: {g21[0]:+.2f} (t {g21[1]:+.2f}・n {g21[2]})**")
# per-year gamma within downtrend state
rows = []
for yy, vv in vd.groupby("year"):
    if len(vv) >= 60: g = gam(vv.reset_index(drop=True)); rows.append(f"{yy} {g[0]:+.1f} ({g[1]:+.1f}・{g[2]})")
for yy, vv in vdo.groupby("year"):
    if len(vv) >= 60: g = gam(vv.reset_index(drop=True)); rows.append(f"{yy} {g[0]:+.1f} ({g[1]:+.1f}・{g[2]})")
say("- 下降局面・年別 γ_dn（n≥60）: " + "・".join(rows))
B3_local = (abs(g13[1]) < 2) or (abs(g21[1]) < 2)
say(f"- B3 判定: {'**局在（2013 または 2021 を抜くと t < 2）**' if B3_local else 'survived（1 年に依存しない）'}")
say()

say("## B4 状態の定義（XAU・γ1 HC1 t・水準＋s|r| 統制込み）")
say("| 窓 | K=20 | K=40 | K=60 | K=120 | s60_lag5 | s60 ∧ \\|m60\\| ≥ 中央値 |"); say("|---|---|---|---|---|---|---|")
for wn, (y0, y1) in WIN.items():
    v = win(VX, y0, y1, "s120"); cs = [g1(v, s=k) for k in ("s20", "s40", "s60", "s120", "s60_lag5")]
    vs = v[v.m60 >= v.m60.median()].reset_index(drop=True); cs.append(g1(vs, s="s60"))
    say(f"| {wn} | " + " | ".join(f"{c[0]:+.2f} ({c[1]:+.2f})" for c in cs) + " |")
say()

say("## B5 シフト・プラセボ: s60 系列を循環シフト（250〜n−250）1000 回 → γ1（水準＋s|r| 統制込み）の |t|")
B5 = {}
for wn, (y0, y1) in WIN.items():
    v = win(VX, y0, y1, "s60"); t_obs = g1(v)[1]; n = len(v); ts_ = np.empty(1000); s0 = v.s60.to_numpy().copy()
    for k in range(1000):
        sh = int(rng.integers(250, n - 250)); vv = v.copy(); vv["s60"] = np.roll(s0, sh); ts_[k] = g1(vv)[1]
    p = float((np.abs(ts_) >= abs(t_obs)).mean()); B5[wn] = (t_obs, p, ts_.std())
    say(f"- {wn}: 実測 t {t_obs:+.2f}・プラセボ |t*| sd {ts_.std():.2f}・P(|t*| ≥ 実測) **{p:.3f}**")
B5_broken = B5["在 2010-20"][1] > 0.025
say(f"- B5 判定: {'**broken（シフトした状態でも同じ t が出る）**' if B5_broken else 'survived'}")
say()

say("## B6 半年格子の 在/外 分割（年別 γ 線形統制・Spearman）")
def gper(V, col):
    rows = []
    for p, vv in V.groupby(col):
        if len(vv) < 60: continue
        g = gam(vv.reset_index(drop=True)); rows.append((p, g[0]))
    return pd.Series(dict(rows))
rh = X_.groupby("half")["lc"].agg(lambda s: (s.iloc[-1] - s.iloc[0]) * 100)
Gh = gper(VX, "half"); Th = pd.DataFrame({"g": Gh, "ret": rh}).dropna()
for wn, m in (("在 2010-20", Th.index < 20210), ("外 2021-26H1", Th.index >= 20210)):
    rho, p = spearmanr(Th.g[m], Th.ret[m]); say(f"- {wn}: ρ {rho:+.2f} (p {p:.3f}・n {int(m.sum())})・符号一致 {int((np.sign(Th.g[m])==np.sign(Th.ret[m])).sum())}/{int(m.sum())}")
say()

say("## B7 US500 対照（B1 と同じ列）")
for wn, (y0, y1) in {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026)}.items():
    v = win(VU, y0, y1); c = [g1(v, level=False, mag=False), g1(v), g1(v, flex=True)]
    say(f"- {wn}: 基本 γ1 {c[0][0]:+.2f} ({c[0][1]:+.2f})・+両方 {c[1][0]:+.2f} ({c[1][1]:+.2f})・+柔軟 {c[2][0]:+.2f} ({c[2][1]:+.2f})")
say()
say("## 追撃 b 総合")
say(f"- B1 {'broken' if B1_broken else 'survived'}（在 両方統制 γ1 t {B1['在 2010-20'][3][1]:+.2f}・外 {B1['外 2021-26H1'][3][1]:+.2f}）／B2 {'half-broken' if up_null else 'survived'}（γ_up 在 t {B2[('XAU','在 2010-20')][0][1]:+.2f}・外 {B2[('XAU','外 2021-26H1')][0][1]:+.2f}；γ_dn 在 {B2[('XAU','在 2010-20')][1][1]:+.2f}・外 {B2[('XAU','外 2021-26H1')][1][1]:+.2f}）／B3 {'局在' if B3_local else 'survived'}／B5 {'broken' if B5_broken else 'survived'}（p 在 {B5['在 2010-20'][1]:.3f}・外 {B5['外 2021-26H1'][1]:.3f}）")
say(f"所要 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
