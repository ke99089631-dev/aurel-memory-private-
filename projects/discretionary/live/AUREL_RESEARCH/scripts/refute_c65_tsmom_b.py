# -*- coding: utf-8 -*-
"""
[REFUTE c65 part B 2026-11-24] part A で T1（US500 在 β −0.299）が
「符号は 11/11 の月境界・91% の総当たり窓で負」「影響点除外で**強くなる**」「US100 で β −0.42 t −4.06」と
予想より頑健だったため、**自由度そのもの**を攻撃する。

=== part B の事前固定（数字を見る前）===
機構の疑い: x ∈ {−1,+1} の二値回帰では β = (ȳ₊ − ȳ₋)/2。US500 在は x=+1 が 88%（69 か月）
→ β は **少数側 9 か月**と 69 か月の平均差。しかも x は lag1 自己相関 +0.37 の持続変数なので
その 9 か月は**連続ブロック（エピソード）**に固まる。HC1 t は 78 個を独立として数える＝自由度の過大計上。
c65 の方法論候補 112 は「少数側 <3 か月なら識別不能」としたが、**3 か月は低すぎる**という仮説。

B1 少数側の棚卸し: 各標的セルの 少数側 n・**連続 run（エピソード）数 G_min**・該当年月の列挙・ȳ₊・ȳ₋。
B2 エピソード単位の推論: クラスタ = x の連続 run（両符号）。CR1 クラスタ頑健 se・t_CR・自由度 G−1 の t 分布 p。
B3 wild cluster bootstrap-t（帰無 β=0 を課した Rademacher・クラスタ単位・2000 本）: 少数クラスタでの正しい p。
   破壊条件（事前）: T1 の p_CR または p_WCB が 0.05 以上 → 「t −2.06・p 0.021」は自由度の過大計上の産物。
B4 US100 の「追試」の正体: 少数側 n と、US500 の少数側月との重複率。
   破壊条件: 重複 ≥70% → 独立な追試ではなく同じ数か月の再計上（t −4.06 は証拠量を増やさない）。
B5 US500 全標本（2013-2026H1）の β と回転 p: 「2014-20 に現れた」が窓固有か標本全体の性質か。
B6 T2（XAU 在 L=126）・T3（XAU 近年 L=21）にも B2/B3 を適用。
B7 c65 の候補 112 の閾値の校正: 少数側 n_min を 3..30 と変えたとき、
   iid 帰無（y をシャッフル）で HC1 t≥2 が出る率（FPR）がいくつになるか＝「<3 か月」で足りるかの数値検査。
seed 20261124。書込は AUREL_RESEARCH/data のみ。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c65_tsmom_b.md")
NY = "America/New_York"
rng = np.random.default_rng(20261124)
NFMIN = 100; VOLWIN = 63
LOG = []
def say(s=""): print(s, flush=True); LOG.append(s)
say(f"# [REFUTE c65 part B] 自由度の過大計上を突く — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c65_tsmom_b.py)")

def ols_hc1(y, x):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None]); V = XtX_inv @ Sm @ XtX_inv * n / (n - 2)
    return b, np.sqrt(np.diag(V))

def daily_table(sym, nfmin=NFMIN):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep]})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "nf": g["lc"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index])
    D["wd"] = D["date"].dt.weekday
    D = D[(D.wd <= 4) & (D.nf >= nfmin)].reset_index()
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["year"] = D["date"].dt.year; D["ym"] = D["year"] * 12 + D["date"].dt.month - 1
    return D

def monthly_table(D, L):
    lc = D["lc_last"].to_numpy(); r = D["r"].to_numpy(); ym = D["ym"].to_numpy()
    ends = np.flatnonzero(np.r_[ym[1:] != ym[:-1], True])
    rows = []
    for j in range(1, len(ends)):
        e_prev, e = ends[j - 1], ends[j]
        if e_prev - L < 0 or e_prev - VOLWIN + 1 < 1: continue
        sd = np.nanstd(r[e_prev - VOLWIN + 1:e_prev + 1], ddof=1)
        if not np.isfinite(sd) or sd <= 0: continue
        R = (lc[e] - lc[e_prev]) * 1e4; x = np.sign(lc[e_prev] - lc[e_prev - L])
        if x == 0: continue
        rows.append((int(D["year"].iloc[e]), int(ym[e]), R, sd * math.sqrt(21), x))
    M = pd.DataFrame(rows, columns=["year", "ym", "R", "sig", "x"]); M["y"] = M["R"] / M["sig"]; M["S"] = M["x"] * M["y"]
    return M

def ymstr(v): return f"{int(v)//12}-{int(v)%12+1:02d}"
def runs(x):
    """x の連続 run の id（0,1,2,...）"""
    return np.r_[0, np.cumsum(x[1:] != x[:-1])]

def cr1(y, x, cl):
    """クラスタ頑健（CR1）se。"""
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    G = len(np.unique(cl)); Sm = np.zeros((2, 2))
    for g in np.unique(cl):
        m = cl == g; h = Z[m].T @ u[m]; Sm += np.outer(h, h)
    adj = G / (G - 1) * (n - 1) / (n - 2)
    V = XtX_inv @ Sm @ XtX_inv * adj
    return b, np.sqrt(np.diag(V)), G

def wcb_p(y, x, cl, nrep=2000, seed=20261124):
    """wild cluster bootstrap-t（帰無 β=0 を課す・Rademacher・クラスタ単位）。"""
    g = np.random.default_rng(seed)
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    b, se, G = cr1(y, x, cl); t_obs = b[1] / se[1]
    a0 = y.mean(); u0 = y - a0                       # 制約付き（β=0）残差
    uc = np.unique(cl); ts = np.empty(nrep)
    for i in range(nrep):
        w = g.choice([-1.0, 1.0], size=len(uc))
        wv = np.empty(n)
        for j, gg in enumerate(uc): wv[cl == gg] = w[j]
        ys = a0 + wv * u0
        bb, ss, _ = cr1(ys, x, cl); ts[i] = bb[1] / ss[1]
    return t_obs, float((np.abs(ts) >= abs(t_obs)).mean()), G

def t_dist_p(t, df):
    """t 分布両側 p（scipy 不要・連分数不要の積分近似）"""
    from math import lgamma, exp, sqrt, pi
    xs = np.linspace(abs(t), abs(t) + 60, 20001)
    logc = lgamma((df + 1) / 2) - lgamma(df / 2) - 0.5 * math.log(df * math.pi)
    pdf = np.exp(logc - (df + 1) / 2 * np.log1p(xs ** 2 / df))
    return float(2 * np.trapezoid(pdf, xs))

def beta_only(x, y):
    xm = x - x.mean(); return float((xm @ (y - y.mean())) / (xm @ xm))
def p_rotation(x, y, beta, minshift=6):
    n = len(x); bs = np.array([beta_only(np.roll(x, s), y) for s in range(minshift, n - minshift + 1)])
    return float((np.abs(bs) >= abs(beta)).mean()), len(bs)

TAB = {s: daily_table(s) for s in ["XAU", "US500", "US100"]}
MT = {}
for s in ["XAU", "US500", "US100"]:
    for L in [21, 63, 126, 252]: MT[(s, L)] = monthly_table(TAB[s], L)

CELLS = {
    "T1 US500 在 2014-20 L=252": ("US500", 252, 2014, 2020),
    "T2 XAU 在 2011-20 L=126": ("XAU", 126, 2011, 2020),
    "T3 XAU 近年 2024-26H1 L=21": ("XAU", 21, 2024, 2026),
    "A7 US100 在 2014-20 L=252": ("US100", 252, 2014, 2020),
    "（対照）XAU 在 2011-20 L=252 主セル": ("XAU", 252, 2011, 2020),
}

say("\n## B1 少数側の棚卸し（β = (ȳ₊ − ȳ₋)/2 ＝ 少数側 n か月の平均差）")
STORE = {}
for name, (sym, L, lo, hi) in CELLS.items():
    M = MT[(sym, L)]; m = M[(M.year >= lo) & (M.year <= hi)].reset_index(drop=True)
    x = m.x.to_numpy(); y = m.y.to_numpy()
    if len(np.unique(x)) < 2: say(f"- {name}: 識別不能"); continue
    minor = -1.0 if (x > 0).mean() > 0.5 else 1.0
    im = x == minor
    rid = runs(x); Gmin = len(np.unique(rid[im])); G = len(np.unique(rid))
    yp = y[x > 0].mean(); yn = y[x < 0].mean()
    b, se = ols_hc1(y, x)
    mm = [ymstr(v) for v in m.ym[im]]
    STORE[name] = (m, x, y, rid, minor, im, G, Gmin)
    say(f"- **{name}**: n {len(m)}・β {b[1]:+.4f}・HC1 t {b[1]/se[1]:+.2f}")
    say(f"  - 少数側 x={minor:+.0f} は **{int(im.sum())} か月（{im.mean()*100:.0f}%）**・"
        f"その連続エピソード数 **G_min = {Gmin}**・全 run 数 G = {G}")
    say(f"  - ȳ(x=+1) {yp:+.3f}／ȳ(x=−1) {yn:+.3f}・差 {yp-yn:+.3f}（= 2β {2*b[1]:+.3f} と一致）")
    say(f"  - 少数側の月: {', '.join(mm)}")

say("\n## B2/B3 エピソード単位の推論（クラスタ = x の連続 run）")
for name, (m, x, y, rid, minor, im, G, Gmin) in STORE.items():
    b, se = ols_hc1(y, x)
    bc, sec, Gc = cr1(y, x, rid)
    t_cr = bc[1] / sec[1]; p_cr = t_dist_p(t_cr, max(Gc - 1, 1))
    t_o, p_w, _ = wcb_p(y, x, rid)
    say(f"- **{name}**: HC1 t {b[1]/se[1]:+.2f}（p {t_dist_p(b[1]/se[1], len(y)-2):.3f}・自由度 {len(y)-2} を仮定）")
    say(f"  - CR1（クラスタ {Gc} 個・自由度 {Gc-1}）: se {sec[1]:.4f}（HC1 の {sec[1]/se[1]:.2f}×）・"
        f"**t_CR {t_cr:+.2f}・p {p_cr:.3f}**")
    say(f"  - **wild cluster bootstrap-t（2000 本・帰無を課す）: p {p_w:.3f}**")

say("\n## B4 US100「追試」の正体（少数側月の重複）")
m5 = STORE["T1 US500 在 2014-20 L=252"][0]; m1h = STORE["A7 US100 在 2014-20 L=252"][0]
s5 = set(m5.ym[m5.x < 0]); s1 = set(m1h.ym[m1h.x < 0])
say(f"- US500 少数側 {len(s5)} か月 {sorted(ymstr(v) for v in s5)}")
say(f"- US100 少数側 {len(s1)} か月 {sorted(ymstr(v) for v in s1)}")
inter = s5 & s1
say(f"- 重複 {len(inter)} か月 {sorted(ymstr(v) for v in inter)}"
    f" → US100 の少数側のうち **{len(inter)/max(len(s1),1)*100:.0f}%** は US500 と同一月"
    f"（y の corr +0.88）＝ 独立な追試ではなく**同じ数か月の再計上**")

say("\n## B5 US500 全標本の β（窓固有か標本全体の性質か）")
MU = MT[("US500", 252)]
for nm, mm in [("全標本 2013-26H1", MU), ("在 2014-20", MU[(MU.year >= 2014) & (MU.year <= 2020)]),
               ("外 2021-26H1", MU[MU.year >= 2021])]:
    x = mm.x.to_numpy(); y = mm.y.to_numpy()
    if len(np.unique(x)) < 2: say(f"- {nm}: 識別不能"); continue
    b, se = ols_hc1(y, x); rid = runs(x); bc, sec, Gc = cr1(y, x, rid)
    pr, nrot = p_rotation(x, y, b[1])
    say(f"- {nm}: n {len(mm)}・少数側 {int((x<0).sum())} か月（エピソード {len(np.unique(rid[x<0]))}）"
        f"・β {b[1]:+.4f}・HC1 t {b[1]/se[1]:+.2f}・CR1 t {bc[1]/sec[1]:+.2f} (G {Gc})・回転 p {pr:.3f}（{nrot} 本）")

say("\n## B7 c65 候補 112 の閾値「少数側 <3 か月で識別不能」の校正")
say("- 設計: 実データ（US500 在 2014-20 の y）を iid シャッフル（帰無）し、x の少数側件数を n_min に強制的に作った"
    "二値 x と回帰 → HC1 t の |t|>=2 率（＝名目 5% のはずの FPR）。x は 1 ブロックに固めた場合（持続あり）と散らした場合の両方。")
ybase = STORE["T1 US500 在 2014-20 L=252"][2]
n = len(ybase); NR = 3000
say("- n_min | FPR（1 ブロック・持続あり） | FPR（ランダム配置・持続なし）")
for n_min in [1, 2, 3, 5, 9, 15, 20, 30]:
    if n_min >= n // 2: continue
    hb = 0; hr = 0
    for i in range(NR):
        ys = rng.permutation(ybase)
        xb = np.ones(n); st = rng.integers(0, n - n_min); xb[st:st + n_min] = -1.0
        b, se = ols_hc1(ys, xb); hb += abs(b[1] / se[1]) >= 2
        xr = np.ones(n); xr[rng.choice(n, n_min, replace=False)] = -1.0
        b, se = ols_hc1(ys, xr); hr += abs(b[1] / se[1]) >= 2
    say(f"  - {n_min:>5} | {hb/NR:.3f} | {hr/NR:.3f}")
say("- 読み: FPR が名目 0.05 を大きく超える n_min の帯が「識別不能として扱うべき」帯。"
    "候補 112 の「<3 か月」はその帯の下端しか切っていないかを数字で確認。")

say(f"\n- 実行 {time.time()-T0:.1f} s・seed 20261124・書込 data/refute_c65_tsmom_b.md のみ・MT5 なし・外部通信なし")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(LOG) + "\n")
print("saved", OUT)
