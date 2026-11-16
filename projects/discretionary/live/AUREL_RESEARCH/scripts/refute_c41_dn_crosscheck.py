# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-16 15:30 反証レーン・第2撃] 対象 = 14:30 反証レーン自身が残した唯一の生存残差（憲章 1条2「自身の過去の回答も疑う」）

  **W5「60 日下降局面の金は株と同じレバレッジ効果を持つ」**
     γ_dn（s60 < 0 部分集合・y = log RV_{d+1}・統制 log RV_d・mean log RV_{d-4..d}・|r_d|）
     = 在 2010-20 −6.75（NW t −3.86・n 1202）／外 2021-26H1 −7.95（t −3.27・n 477）
     14:30 の判定 = survived-but-localized（2013/2021 に局在・シフトプラセボ p 0.018/0.010 は Bonferroni 0.007 不通過）。
     14:30 が通した攻撃: 関数形・符号反転 ρ プラセボ・状態×大きさ省略変数・状態定義 K・年月 FE・半年格子・LOYO・シフトプラセボ。
     14:30 が**やっていない**攻撃 = 本スクリプト: (1) 下降局面の系列相関を正しく扱う推論（NW(5) は episode をまたげない）、
     (2) **独立計測器**（CBOE GVZ・Dukascopy bid と無関係）、(3) ボラ計測の定義（レンジ/ジャンプ頑健）、(4) 別の在外分割、
     (5) 生存セル自体への直接プラセボ、(6) 実質金利/ドル/VIX の交絡（14:30 自身が「2013/2021 の実質金利主導の金の下げ相場に根がある」と書いた）、
     (7) 探索経路全体の多重検定、(8) セッション日の切り方（±2h）。

=== 規則（数字を見る前に書く・規則 8 本 → Bonferroni 名目 p 0.00625／|t| 2.73 を併記。BH q=0.10 も報告）===
E0 複製: まず γ_dn 在 −6.75 (t −3.86・n 1202)／外 −7.95 (t −3.27・n 477) を再現する。
   **係数が ±0.3 以内で一致しなければ以降を実行せず halt（複製不能＝攻撃の対象が特定できない）。**
E1 推論（episode クラスタ）: 下降局面は連続した episode（s60 の符号の連続区間）であり、日次の独立 n ではない。
   γ_dn を episode クラスタ頑健 se と wild cluster bootstrap（Rademacher・制約付き帰無 γ=0・999 回）で再検定。episode 数 G を印字。
   **在の クラスタ |t| < 2 または WCR p > 0.05 → broken as inference（NW(5) の過小 se が作った見かけ）。**
E2 独立計測器（最重要・bid 人工物と Dukascopy から完全に独立）: y_IV = Δlog GVZ_{d→d+1}（CBOE・GLD 30 日 IV）を
   r_d に回帰（統制 log GVZ_d・Δlog GVZ_{d-1→d}・|r_d|）。陽性対照 = Δlog VIX on US500 r_d（株のレバレッジ効果は IV にも強く出るはず）。
   **対照 VIX/US500 が |t| ≥ 3 なのに XAU 下降局面 γ_dn^GVZ が 在・外とも |t| < 2 → broken as 市場事実
   （方法は IV で効果を捕まえられるのに、金の下降局面の非対称が独立計測器に無い＝Dukascopy bid RV 固有）。**
   survived = γ_dn^GVZ < 0 ∧ 在 t ≤ −2 ∧ 外 同符号。
E3 ボラ計測の定義: y を (a) Parkinson（セッションの高安レンジ・bid の跳ねと 5 分格子に非依存）・(b) 切断 RV（|r_5m| > 5×日中位数 を 0 に）・
   (c) BPV（二乗和でなく |r_i||r_{i+1}| のジャンプ頑健版）で作り直して γ_dn を再推定（OHLC キャッシュ）。
   **(a) と (b) がともに 在 |t| < 2 → broken as ボラ過程の事実（5 分二乗和固有の計測人工物）。**
E4 別の在外分割（憲章補遺 C「別の在外分割」）: (a) 反転 在=2021-26／外=2010-20、(b) 奇数年／偶数年、(c) 下降局面日の連続 3 分割（等 n）、
   (d) 下降局面 episode の奇数/偶数。各分割で「両半分が負 ∧ 少なくとも一方 |t| ≥ 2」を通過条件とする。
   **4 分割のうち 2 つ以上 不通過 → broken as 安定した事実（分割依存）。**
E5 生存セル直接プラセボ: 下降局面部分集合の中で r_d の符号を (a) iid 反転・(b) 連続 20 日ブロック反転（符号の持続を保存）2000 回。
   |r|・y・統制は保存。**P(t* ≤ 実測) > 0.025 のものがあれば broken（符号情報なしで出る）。** t* の sd で se の膨らみを測る。
E6 交絡（14:30 自身の「最も重大な反証」への検定）: 下降局面回帰に F 可測でない同時点マクロを**あえて**入れる（最も厳しい交絡統制）:
   ΔDFII10_d（実質金利）・Δlog DTWEXBGS_d（ドル）・Δlog VIX_d。
   **γ_dn が 在 |t| < 2 に落ちる → broken（金のボラ非対称でなく実質金利/ドル/株ボラ channel の別名）。**
E7 多重検定: c41（事前固定 2 セル）＋14:30 反証（R6 の 20 セル・B4 の 6 定義・γ_up/γ_dn 分割・年別）＋本サイクルで
   XAU 翌日 γ に対して実際に走らせた検定数 M を数え、プラセボ p に Bonferroni と BH(q=0.10) を当てる。
   **BH q=0.10 を通らない → inconclusive 以下に格下げ。**
E8 セッション日の切り方: sess = (ET + Xh) の X を 4／6（基準）／8 に振る（日境界 20:00／18:00／16:00 ET）。
   **X=4 または 8 で符号が反転、または両方で |t| < 2 → broken as 頑健な事実（日境界の人工物）。**

総合判定（事前固定）: **broken** = {E1, E2, E3, E6} のうち 2 つ以上が fail／**survived** = E1,E2,E3,E5,E6 全通過 ∧ E4 が 3/4 以上／他は **inconclusive**。
データ: data/macro/XAU_m5_close.npz・XAU_m5_ohlc.npz・US500_m5_close.npz・GVZCLS.csv・VIXCLS.csv・DFII10.csv・DTWEXBGS.csv
（既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し・発注なし）。seed 20261116。
コスト倍は取引不能の構造主張のため該当なし（代替 = E3 の計測定義・E6 の交絡統制を「倍の厳しさ」として課す）。
D2: 窓は 在 2010-20／外 2021-26H1 を基準に別分割（E4）。16 年一括の平均 γ を edge の判定に使わない。
"""
import os, sys, time, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c41_dn_crosscheck.md"); NY = "America/New_York"
rng = np.random.default_rng(20261116); NFMIN = 100; NPERM = 2000; NBOOT = 999
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
def save():
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT, flush=True)

say(f"# [REFUTE c41 第2撃] W5「60 日下降局面の金のレバレッジ効果」を壊す — {time.strftime('%Y-%m-%d %H:%M')}")
say("規則 8 本は scripts/refute_c41_dn_crosscheck.py の docstring に数字を見る前に記載（Bonferroni 名目 p 0.00625／|t| 2.73）")
say()

# ---------------- estimators ----------------
def nw_ols(y, X, lag=5):
    y = np.asarray(y, float); X = np.asarray(X, float); n = len(y)
    Z = np.column_stack([np.ones(n), X]); Xi = np.linalg.pinv(Z.T @ Z)
    b = Xi @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None]); Vh = Xi @ Sm @ Xi * n / max(n - Z.shape[1], 1)
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = Xi @ Sm @ Xi
    return b, np.sqrt(np.abs(np.diag(V))), np.sqrt(np.abs(np.diag(Vh))), u

def cluster_ols(y, X, g):
    y = np.asarray(y, float); X = np.asarray(X, float); n = len(y)
    Z = np.column_stack([np.ones(n), X]); k = Z.shape[1]; Xi = np.linalg.pinv(Z.T @ Z)
    b = Xi @ Z.T @ y; u = y - Z @ b
    S = np.zeros((k, k)); gu = np.unique(g)
    for gg in gu:
        m = g == gg; s = Z[m].T @ u[m]; S += np.outer(s, s)
    G = len(gu); c = G / max(G - 1, 1) * (n - 1) / max(n - k, 1)
    V = Xi @ S @ Xi * c
    return b, np.sqrt(np.abs(np.diag(V))), int(G), Z, Xi, u

# baseline gamma on a subsample: y on [lrv, lrv5, ar, r]
def gam(v, extra=None, ycol="y", lag=5):
    if len(v) < 60: return (np.nan, np.nan, len(v))
    cols = [v.lrv, v.lrv5, v.ar]
    if extra is not None: cols += [v[c] for c in extra]
    cols += [v.r]
    X = np.column_stack(cols); b, se, seh, u = nw_ols(v[ycol].to_numpy(), X, lag=lag)
    return b[-1] * 1e4, b[-1] / se[-1], len(v)

# ---------------- daily session table (replicates refute_c41_asymvol_b.daily) ----------------
def daily(sym, shift_h=6, src="close"):
    fn = f"{sym}_m5_ohlc.npz" if src == "ohlc" else f"{sym}_m5_close.npz"
    z = np.load(os.path.join(MAC, fn))
    ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); keep = r != 0
    sess = (pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY) + pd.Timedelta(hours=shift_h)).tz_localize(None).values.astype("datetime64[D]")
    so = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    df = pd.DataFrame({"o": so[keep], "lc": lc[keep], "r": r[keep], "r2": r[keep] ** 2})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()}).reset_index()
    if src == "ohlc":
        H = z["high"].astype(float); Lo = z["low"].astype(float)
        dfa = pd.DataFrame({"o": so, "h": H, "l": Lo})           # all bars for the range
        ga = dfa.groupby("o", sort=True)
        rng_ = pd.DataFrame({"hi": ga["h"].max(), "lo": ga["l"].min()}).reset_index()
        D = D.merge(rng_, on="o", how="left")
        D["pk"] = (np.log(D.hi / D.lo) ** 2) / (4 * np.log(2))
        # jump-robust: truncated RV (|r| > 5x within-day median |r|) and bipower variation
        def _rob(s):
            a = s.to_numpy(); m = np.median(np.abs(a))
            trv = float(np.sum(np.where(np.abs(a) > 5 * m, 0.0, a) ** 2))
            bpv = float((np.pi / 2) * np.sum(np.abs(a[:-1]) * np.abs(a[1:]))) if len(a) > 1 else np.nan
            return pd.Series({"trv": trv, "bpv": bpv})
        rb = df.groupby("o", sort=True)["r"].apply(_rob).unstack().reset_index()
        D = D.merge(rb, on="o", how="left")
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.o])
    D = D[(D.date.dt.weekday <= 4) & (D.nf >= NFMIN)].reset_index(drop=True)
    D["lrv"] = np.log(D.rv); D["r"] = np.r_[np.nan, np.diff(D.lc)] * 1e4
    D["lrv5"] = D.lrv.rolling(5).mean(); D["year"] = D.date.dt.year
    if src == "ohlc":
        for c in ("pk", "trv", "bpv"):
            D["l" + c] = np.log(D[c].replace(0, np.nan))
            D["l" + c + "5"] = D["l" + c].rolling(5).mean()
    D["s60"] = np.sign(D.lc - D.lc.shift(60))
    D["epi"] = (D.s60 != D.s60.shift()).cumsum()
    return D

def xy(D, extra=()):
    n = len(D); t = slice(0, n - 1); t1 = slice(1, n)
    cols = {"y": D.lrv.to_numpy()[t1], "o": D.o.to_numpy()[t], "date": D.date.to_numpy()[t]}
    for c in ("lrv", "lrv5", "r", "year", "s60", "epi"): cols[c] = D[c].to_numpy()[t]
    for c in extra:                      # alternative y built from the SAME day d+1
        cols["y_" + c] = D["l" + c].to_numpy()[t1]
        cols["lrv_" + c] = D["l" + c].to_numpy()[t]; cols["lrv5_" + c] = D["l" + c + "5"].to_numpy()[t]
    V = pd.DataFrame(cols); V["ar"] = V.r.abs()
    ok = np.isfinite(V.y) & np.isfinite(V.lrv) & np.isfinite(V.lrv5) & np.isfinite(V.r)
    return V[ok].reset_index(drop=True)

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026)}
def win(V, y0, y1):
    return V[(V.year >= y0) & (V.year <= y1) & np.isfinite(V.s60)].reset_index(drop=True)
def dn(V, y0, y1):
    v = win(V, y0, y1); return v[v.s60 < 0].reset_index(drop=True)
def up(V, y0, y1):
    v = win(V, y0, y1); return v[v.s60 > 0].reset_index(drop=True)

X_ = daily("XAU"); VX = xy(X_)
U_ = daily("US500"); VU = xy(U_)
say(f"- 読込: XAU 有効セッション日 {len(X_)}（回帰行 {len(VX)}）・US500 {len(U_)}（{len(VU)}）・{time.time()-T0:.1f} s")

# ================= E0 replication =================
say()
say("## E0 複製（14:30 の γ_dn を再現できるか）")
say("| 窓 | γ_dn ×1e4 (NW t・n) | 14:30 の値 | 一致 |"); say("|---|---|---|---|")
REF = {"在 2010-20": (-6.75, -3.86, 1202), "外 2021-26H1": (-7.95, -3.27, 477)}
E0_ok = True; BASE = {}
for wn, (y0, y1) in WIN.items():
    g = gam(dn(VX, y0, y1)); BASE[wn] = g; rf = REF[wn]
    ok = abs(g[0] - rf[0]) <= 0.3 and g[2] == rf[2]
    E0_ok &= ok
    say(f"| {wn} | {g[0]:+.2f} ({g[1]:+.2f}・{g[2]}) | {rf[0]:+.2f} ({rf[1]:+.2f}・{rf[2]}) | {'OK' if ok else '**不一致**'} |")
if not E0_ok:
    say("- **E0 halt: 複製不能 → 攻撃を実行しない（憲章: 迷ったらやらない）**"); save(); sys.exit(0)
say("- E0: 複製 OK → 以下の攻撃を実行")

# ================= E1 episode-clustered inference =================
say()
say("## E1 推論: 下降局面 episode クラスタ頑健 se ＋ wild cluster bootstrap（Rademacher・制約付き帰無・999 回）")
say("| 窓 | n | episode 数 G | 中位 episode 長 | γ_dn | NW t | HC1 t | **クラスタ t** | **WCR p** |"); say("|---|---|---|---|---|---|---|---|---|")
E1 = {}
for wn, (y0, y1) in WIN.items():
    v = dn(VX, y0, y1)
    X = np.column_stack([v.lrv, v.lrv5, v.ar, v.r]); y = v.y.to_numpy(); gcl = v.epi.to_numpy()
    b, se_nw, se_hc, _ = nw_ols(y, X)
    bc, se_cl, G, Z, Xi, u = cluster_ols(y, X, gcl)
    t_cl = bc[-1] / se_cl[-1]
    # restricted-null wild cluster bootstrap
    Z0 = Z[:, :-1]; Xi0 = np.linalg.pinv(Z0.T @ Z0); b0 = Xi0 @ Z0.T @ y; f0 = Z0 @ b0; u0 = y - f0
    gu = np.unique(gcl); gidx = {gg: (gcl == gg) for gg in gu}
    ts = np.empty(NBOOT)
    for k in range(NBOOT):
        vsign = rng.choice([-1.0, 1.0], size=len(gu))
        mult = np.empty(len(y))
        for j, gg in enumerate(gu): mult[gidx[gg]] = vsign[j]
        ys = f0 + mult * u0
        bb, sse, _, _, _, _ = cluster_ols(ys, X, gcl)
        ts[k] = bb[-1] / sse[-1] if sse[-1] > 0 else np.nan
    p_wcr = float((np.abs(ts) >= abs(t_cl)).mean())
    lens = v.groupby("epi").size()
    E1[wn] = (t_cl, p_wcr, G, float(np.nanstd(ts)))
    say(f"| {wn} | {len(v)} | **{G}** | {int(lens.median())} | {b[-1]*1e4:+.2f} | {b[-1]/se_nw[-1]:+.2f} | {b[-1]/se_hc[-1]:+.2f} | **{t_cl:+.2f}** | **{p_wcr:.3f}** |")
say(f"- WCR 帰無 |t*| sd: 在 {E1['在 2010-20'][3]:.2f}／外 {E1['外 2021-26H1'][3]:.2f}（1.0 なら漸近 t が正しい）")
E1_fail = (abs(E1["在 2010-20"][0]) < 2) or (E1["在 2010-20"][1] > 0.05)
say(f"- **E1 判定: {'**broken as inference**' if E1_fail else 'survived（episode クラスタでも残る）'}**")

# ================= E2 independent instrument: GVZ / VIX =================
say()
say("## E2 独立計測器: Δlog GVZ_{d→d+1}（CBOE・GLD 30 日 IV）を r_d に回帰／陽性対照 Δlog VIX × US500")
def fred(fn, col):
    d = pd.read_csv(os.path.join(MAC, fn))
    d.columns = [c.strip() for c in d.columns]
    dc = d.columns[0]
    d[dc] = pd.to_datetime(d[dc], errors="coerce")
    d[col] = pd.to_numeric(d[col], errors="coerce")
    d = d.dropna(subset=[dc, col])
    d["o"] = d[dc].map(lambda x: x.date().toordinal())
    return d.set_index("o")[col]

def add_iv(V, series, name):
    s = series.reindex(V.o.to_numpy())
    lv = np.log(s.to_numpy())
    V = V.copy(); V["liv"] = lv
    V["y_iv"] = np.r_[lv[1:], np.nan] - lv          # d -> d+1 (next-day change)
    V["dliv"] = lv - np.r_[np.nan, lv[:-1]]         # d-1 -> d (lagged change, control)
    return V

def gam_iv(v):
    v = v[np.isfinite(v.y_iv) & np.isfinite(v.liv) & np.isfinite(v.dliv)].reset_index(drop=True)
    if len(v) < 60: return (np.nan, np.nan, len(v))
    X = np.column_stack([v.liv, v.dliv, v.ar, v.r]); b, se, seh, u = nw_ols(v.y_iv.to_numpy(), X)
    return b[-1] * 1e4, b[-1] / se[-1], len(v)

GVZ = fred("GVZCLS.csv", "GVZCLS"); VIX = fred("VIXCLS.csv", "VIXCLS")
VXiv = add_iv(VX, GVZ, "GVZ"); VUiv = add_iv(VU, VIX, "VIX")
say("| 系列 | 窓 | 全体 γ^IV (t・n) | 上昇局面 γ_up^IV (t・n) | 下降局面 γ_dn^IV (t・n) |"); say("|---|---|---|---|---|")
E2 = {}
for nm, V, wins in (("XAU × GVZ", VXiv, WIN), ("US500 × VIX (対照)", VUiv, {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026)})):
    for wn, (y0, y1) in wins.items():
        ga = gam_iv(win(V, y0, y1)); gu = gam_iv(up(V, y0, y1)); gd = gam_iv(dn(V, y0, y1))
        E2[(nm, wn)] = (ga, gu, gd)
        say(f"| {nm} | {wn} | {ga[0]:+.2f} ({ga[1]:+.2f}・{ga[2]}) | {gu[0]:+.2f} ({gu[1]:+.2f}・{gu[2]}) | **{gd[0]:+.2f} ({gd[1]:+.2f}・{gd[2]})** |")
ctl = max(abs(E2[("US500 × VIX (対照)", w)][0][1]) for w in ("在 2014-20", "外 2021-26H1"))
gdn_i = E2[("XAU × GVZ", "在 2010-20")][2]; gdn_o = E2[("XAU × GVZ", "外 2021-26H1")][2]
E2_fail = (ctl >= 3) and (abs(gdn_i[1]) < 2) and (abs(gdn_o[1]) < 2)
E2_surv = (gdn_i[0] < 0) and (gdn_i[1] <= -2) and (np.sign(gdn_o[0]) == np.sign(gdn_i[0]))
say(f"- 対照の最大 |t| {ctl:.2f}（方法が IV で非対称を捕まえられるか）・XAU 下降局面 在 t {gdn_i[1]:+.2f}／外 {gdn_o[1]:+.2f}")
say(f"- **E2 判定: {'**broken as 市場事実（独立計測器に無い＝bid RV 固有）**' if E2_fail else ('survived（独立計測器でも下降局面で負）' if E2_surv else 'inconclusive（対照が弱い／部分的）')}**")

# ================= E3 volatility measurement definition =================
say()
say("## E3 ボラ計測の定義: Parkinson（高安レンジ）・切断 RV・BPV で γ_dn を再推定（XAU OHLC キャッシュ）")
t_ohlc = time.time()
XO = daily("XAU", src="ohlc"); VXO = xy(XO, extra=("pk", "trv", "bpv"))
say(f"- OHLC 読込・集計 {time.time()-t_ohlc:.1f} s・有効日 {len(XO)}（回帰行 {len(VXO)}）・plain RV 列の相関 ρ(lrv_close, lrv_ohlc) = {np.corrcoef(VXO.lrv, VXO.lrv)[0,1]:.3f}")
def gam_alt(v, tag):
    vv = v[np.isfinite(v["y_" + tag]) & np.isfinite(v["lrv_" + tag]) & np.isfinite(v["lrv5_" + tag])].reset_index(drop=True)
    if len(vv) < 60: return (np.nan, np.nan, len(vv))
    X = np.column_stack([vv["lrv_" + tag], vv["lrv5_" + tag], vv.ar, vv.r])
    b, se, seh, u = nw_ols(vv["y_" + tag].to_numpy(), X)
    return b[-1] * 1e4, b[-1] / se[-1], len(vv)
say("| 窓 | 5分二乗和 RV（基準） | **Parkinson** | **切断 RV** | BPV |"); say("|---|---|---|---|---|")
E3 = {}
for wn, (y0, y1) in WIN.items():
    v = dn(VXO, y0, y1)
    g0 = gam(v); gp = gam_alt(v, "pk"); gt = gam_alt(v, "trv"); gb = gam_alt(v, "bpv")
    E3[wn] = (g0, gp, gt, gb)
    say(f"| {wn} | {g0[0]:+.2f} ({g0[1]:+.2f}・{g0[2]}) | **{gp[0]:+.2f} ({gp[1]:+.2f}・{gp[2]})** | **{gt[0]:+.2f} ({gt[1]:+.2f}・{gt[2]})** | {gb[0]:+.2f} ({gb[1]:+.2f}・{gb[2]}) |")
# uptrend control for the same measures (asymmetry must be one-sided)
vu = up(VXO, 2010, 2020)
say(f"- 対照 在 上昇局面: Parkinson {gam_alt(vu,'pk')[0]:+.2f} (t {gam_alt(vu,'pk')[1]:+.2f})・切断 RV {gam_alt(vu,'trv')[0]:+.2f} (t {gam_alt(vu,'trv')[1]:+.2f})")
E3_fail = (abs(E3["在 2010-20"][1][1]) < 2) and (abs(E3["在 2010-20"][2][1]) < 2)
say(f"- **E3 判定: {'**broken as ボラ過程の事実（レンジ・ジャンプ頑健版で消える）**' if E3_fail else 'survived（計測定義に依存しない）'}**")

# ================= E4 alternative in/out splits =================
say()
say("## E4 別の在外分割（両半分が負 ∧ 一方 |t| ≥ 2 を通過条件）")
say("| 分割 | 半分 A | 半分 B | 通過 |"); say("|---|---|---|---|")
E4 = {}
vall = VX[np.isfinite(VX.s60)].reset_index(drop=True); vdn_all = vall[vall.s60 < 0].reset_index(drop=True)
def pf(a, b):
    return (a[0] < 0) and (b[0] < 0) and (max(abs(a[1]), abs(b[1])) >= 2)
# (a) reversed
a1 = gam(dn(VX, 2021, 2026)); b1 = gam(dn(VX, 2010, 2020)); E4["(a) 反転 在=2021-26/外=2010-20"] = pf(a1, b1)
say(f"| (a) 反転（在=2021-26・外=2010-20） | {a1[0]:+.2f} ({a1[1]:+.2f}・{a1[2]}) | {b1[0]:+.2f} ({b1[1]:+.2f}・{b1[2]}) | {'OK' if E4['(a) 反転 在=2021-26/外=2010-20'] else '**不通過**'} |")
# (b) odd/even years
ao = gam(vdn_all[vdn_all.year % 2 == 1].reset_index(drop=True)); ae = gam(vdn_all[vdn_all.year % 2 == 0].reset_index(drop=True))
E4["(b) 奇数年/偶数年"] = pf(ao, ae)
say(f"| (b) 奇数年／偶数年 | {ao[0]:+.2f} ({ao[1]:+.2f}・{ao[2]}) | {ae[0]:+.2f} ({ae[1]:+.2f}・{ae[2]}) | {'OK' if E4['(b) 奇数年/偶数年'] else '**不通過**'} |")
# (c) three contiguous thirds of downtrend days (report all three; pass = all negative & >=1 with |t|>=2)
n3 = len(vdn_all); cut = [0, n3 // 3, 2 * n3 // 3, n3]
g3 = [gam(vdn_all.iloc[cut[i]:cut[i + 1]].reset_index(drop=True)) for i in range(3)]
E4["(c) 連続 3 分割"] = all(g[0] < 0 for g in g3) and (max(abs(g[1]) for g in g3) >= 2)
say(f"| (c) 下降局面日 連続 3 分割 | " + " ／ ".join(f"{g[0]:+.2f} ({g[1]:+.2f}・{g[2]})" for g in g3) + f" | （3 分割） | {'OK' if E4['(c) 連続 3 分割'] else '**不通過**'} |")
# (d) odd/even downtrend episodes
eids = np.sort(vdn_all.epi.unique()); rank = {e: i for i, e in enumerate(eids)}
par = vdn_all.epi.map(rank) % 2
d1 = gam(vdn_all[par == 0].reset_index(drop=True)); d2 = gam(vdn_all[par == 1].reset_index(drop=True))
E4["(d) 奇数/偶数 episode"] = pf(d1, d2)
say(f"| (d) 下降局面 episode 奇数／偶数（{len(eids)} episode） | {d1[0]:+.2f} ({d1[1]:+.2f}・{d1[2]}) | {d2[0]:+.2f} ({d2[1]:+.2f}・{d2[2]}) | {'OK' if E4['(d) 奇数/偶数 episode'] else '**不通過**'} |")
E4_pass = sum(1 for v_ in E4.values() if v_)
E4_fail = E4_pass <= 2
say(f"- **E4 判定: 通過 {E4_pass}/4 → {'**broken as 安定した事実（分割依存）**' if E4_fail else 'survived（分割に依存しない）'}**")

# ================= E5 direct placebo on the surviving cell =================
say()
say("## E5 生存セル直接プラセボ: 下降局面部分集合で r_d の符号を iid／連続 20 日ブロックで反転（2000 回・|r|・y 保存）")
say("| 窓 | 実測 NW t | iid 反転 P(t* ≤ 実測) | iid \\|t*\\| sd | ブロック 20 日 P | ブロック \\|t*\\| sd |"); say("|---|---|---|---|---|---|")
E5 = {}
for wn, (y0, y1) in WIN.items():
    v = dn(VX, y0, y1); y = v.y.to_numpy(); ar = v.ar.to_numpy(); n = len(v)
    Z0 = np.column_stack([np.ones(n), v.lrv, v.lrv5, ar])
    t_obs = BASE[wn][1]
    def run(block):
        out = np.empty(NPERM)
        for k in range(NPERM):
            if block is None:
                s = rng.choice([-1.0, 1.0], size=n)
            else:
                nb = int(np.ceil(n / block)); s = np.repeat(rng.choice([-1.0, 1.0], size=nb), block)[:n]
            Z = np.column_stack([Z0, s * ar * np.sign(v.r.to_numpy())])
            b, se, seh, u = nw_ols(y, Z[:, 1:], lag=5)
            out[k] = b[-1] / se[-1] if se[-1] > 0 else np.nan
        return out
    ti = run(None); tb = run(20)
    pi_ = float((ti <= t_obs).mean()); pb = float((tb <= t_obs).mean())
    E5[wn] = (pi_, pb, float(np.nanstd(ti)), float(np.nanstd(tb)))
    say(f"| {wn} | {t_obs:+.2f} | **{pi_:.4f}** | {np.nanstd(ti):.2f} | **{pb:.4f}** | {np.nanstd(tb):.2f} |")
E5_fail = max(E5["在 2010-20"][0], E5["在 2010-20"][1]) > 0.025
say(f"- **E5 判定: {'**broken（符号情報なしで出る）**' if E5_fail else 'survived（プラセボは再現しない）'}**・ブロック反転の \\|t*\\| sd が 1 を超える分だけ漸近 t は過大")

# ================= E6 macro confounders =================
say()
say("## E6 交絡: 下降局面回帰に同時点 ΔDFII10・Δlog DTWEXBGS・Δlog VIX を入れる（最も厳しい統制・F 可測でない）")
DFII = fred("DFII10.csv", "DFII10"); DXY = fred("DTWEXBGS.csv", "DTWEXBGS")
def add_macro(V):
    V = V.copy(); o = V.o.to_numpy()
    for nm, s, logd in (("dfii", DFII, False), ("dxy", DXY, True), ("vix", VIX, True)):
        cur = s.reindex(o).to_numpy(float)
        prev = s.reindex(o - 1).to_numpy(float)
        prev2 = s.reindex(o - 2).to_numpy(float); prev3 = s.reindex(o - 3).to_numpy(float)
        pv = np.where(np.isfinite(prev), prev, np.where(np.isfinite(prev2), prev2, prev3))
        V["d_" + nm] = (np.log(cur) - np.log(pv)) if logd else (cur - pv)
    return V
VXm = add_macro(VX)
say("| 窓 | 統制なし | +ΔDFII10 | +Δlog DXY | +Δlog VIX | **3 つ全部** | n |"); say("|---|---|---|---|---|---|---|")
E6 = {}
for wn, (y0, y1) in WIN.items():
    v = dn(VXm, y0, y1)
    v = v[np.isfinite(v.d_dfii) & np.isfinite(v.d_dxy) & np.isfinite(v.d_vix)].reset_index(drop=True)
    g0 = gam(v); g1 = gam(v, ["d_dfii"]); g2 = gam(v, ["d_dxy"]); g3 = gam(v, ["d_vix"]); g4 = gam(v, ["d_dfii", "d_dxy", "d_vix"])
    E6[wn] = (g0, g4)
    say(f"| {wn} | {g0[0]:+.2f} ({g0[1]:+.2f}) | {g1[0]:+.2f} ({g1[1]:+.2f}) | {g2[0]:+.2f} ({g2[1]:+.2f}) | {g3[0]:+.2f} ({g3[1]:+.2f}) | **{g4[0]:+.2f} ({g4[1]:+.2f})** | {g4[2]} |")
E6_fail = abs(E6["在 2010-20"][1][1]) < 2
say(f"- **E6 判定: {'**broken（マクロ channel の別名）**' if E6_fail else 'survived（実質金利・ドル・株ボラ統制でも残る）'}**")

# ================= E8 session day cut =================
say()
say("## E8 セッション日の切り方: sess = (ET + Xh)・X = 4／6（基準）／8（日境界 20:00／18:00／16:00 ET）")
say("| X（日境界 ET） | 在 γ_dn (t・n) | 外 γ_dn (t・n) | 有効日 |"); say("|---|---|---|---|")
E8 = {}
for X, lab in ((4, "20:00"), (6, "18:00 基準"), (8, "16:00")):
    Dx = X_ if X == 6 else daily("XAU", shift_h=X); Vx = VX if X == 6 else xy(Dx)
    gi = gam(dn(Vx, 2010, 2020)); go = gam(dn(Vx, 2021, 2026)); E8[X] = (gi, go)
    say(f"| X={X}（{lab}） | {gi[0]:+.2f} ({gi[1]:+.2f}・{gi[2]}) | {go[0]:+.2f} ({go[1]:+.2f}・{go[2]}) | {len(Dx)} |")
sgn_flip = any(E8[X][0][0] > 0 for X in (4, 8))
weak_both = all(abs(E8[X][0][1]) < 2 for X in (4, 8))
E8_fail = sgn_flip or weak_both
say(f"- **E8 判定: {'**broken as 頑健な事実（日境界の人工物）**' if E8_fail else 'survived（±2h の日境界で不変）'}**")

# ================= E7 multiple testing =================
say()
say("## E7 多重検定（XAU 翌日 γ に実際に走らせた検定の家族）")
FAM = [("c41 事前固定 C2（金・全体 γ）", 2), ("14:30 R6 レジーム部分集合", 20), ("14:30 B4 状態定義 K・lag・強度", 6),
       ("14:30 B2 γ_up/γ_dn 分割", 2), ("14:30 B3 LOYO（下降局面・年別）", 11 + 6), ("本サイクル E1〜E8（セル数）", 8 + 6 + 8 + 10 + 4 + 10 + 6)]
M = sum(k for _, k in FAM)
say("| 家族 | 検定数 |"); say("|---|---|")
for nmf, k in FAM: say(f"| {nmf} | {k} |")
say(f"| **合計 M** | **{M}** |")
ps = {"E5 iid 反転（在）": E5["在 2010-20"][0], "E5 ブロック反転（在）": E5["在 2010-20"][1],
      "E1 WCR（在）": E1["在 2010-20"][1], "E1 WCR（外）": E1["外 2021-26H1"][1],
      "14:30 B5 シフト（在）": 0.018, "14:30 B5 シフト（外）": 0.010}
srt = sorted(ps.items(), key=lambda kv: kv[1]); m_ = len(srt)
say(f"- Bonferroni 閾値（M={M}）: p < {0.05/M:.5f}")
say("| プラセボ/bootstrap p | 値 | Bonferroni(M) 通過 | BH q=0.10 閾値 (i/m·q) | BH 通過 |"); say("|---|---|---|---|---|")
bh_ok_any = False
for i, (k, p) in enumerate(srt, 1):
    thr = i / m_ * 0.10; ok = p <= thr; bh_ok_any |= ok
    say(f"| {k} | {p:.4f} | {'OK' if p < 0.05/M else '不通過'} | {thr:.4f} | {'OK' if ok else '不通過'} |")
say(f"- E7: BH q=0.10 を通る p が {'ある' if bh_ok_any else '**無い**'}・Bonferroni(M={M}) を通る p は {sum(1 for _,p in srt if p < 0.05/M)}/{m_}")

# ================= verdict =================
say()
say("## 総合判定（事前固定の集計規則）")
fails = {"E1 推論": E1_fail, "E2 独立計測器": E2_fail, "E3 計測定義": E3_fail, "E6 交絡": E6_fail}
nf = sum(1 for v_ in fails.values() if v_)
others = {"E4 分割": E4_fail, "E5 直接プラセボ": E5_fail, "E8 日境界": E8_fail}
if nf >= 2: verdict = "**broken**"
elif (not E1_fail) and (not E2_fail) and (not E3_fail) and (not E5_fail) and (not E6_fail) and (E4_pass >= 3): verdict = "**survived**"
else: verdict = "**inconclusive**"
for k, v_ in list(fails.items()) + list(others.items()): say(f"- {k}: {'fail（壊れた）' if v_ else 'pass（残った）'}")
say(f"- 中核 4 規則のうち fail = {nf} → **W5 の判定: {verdict}**")
say(f"所要 {time.time()-T0:.1f} s")
save()
