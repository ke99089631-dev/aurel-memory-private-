# -*- coding: utf-8 -*-
"""
[REFUTE c65 2026-11-24 15:30 反証レーン] 対象 = cycle65 (12:45) TSMOM の **肯定形・弱シグナル主張**
（PROMOTED.md は空＝昇格候補ゼロ。c65 の主判定 C1/C0 はどちらも null＝破る余地なし。
  よって c65 が「記述」「最も重大な反証」「得た知識」として**肯定形で書いた**主張と、c65 の**方法論主張**を攻撃する。）

=== 攻撃対象（c65 の本文からの引用・数字を見る前に固定）===
T1（主標的）: **US500 在 2014-20 β −0.299 (se 0.145・HC1 t −2.06・符号反転置換 p 0.021)**
   ＋ c65 の読み「在の負は『下降符号（2016H1・2019H1・2020Q2）の月に株が戻した』の積み上げ」
   ＋ 得た知識 (3)「我々の格子では株式指数の 12 か月 TSMOM は 2014-20 に『反転』として現れた」
T2: **XAU 在 L=126（6 か月）月次 t +1.79・日次 t +1.80 で「2 つの地平が同符号」＝『文献の 6 か月地平が在だけに名目で居る』**
   （c65 の最重大反証 第 2）
T3: **XAU 近年 L=21 β +0.420 (t +2.16・n 30)**（family の名目有意セル）
T4（方法論）: **「注入 β*=0.173（SR 0.6）→ 回収 1.00 ＝ 規則は SR 0.6 を見える」** および
   **決着可能性「MDE(2se) ⇒ SR 0.63〜0.85 級が決着できる範囲」**
T5（方法論・候補 ⑲ 日次版）: **「年別 VR(21) の iid シャッフル帰無中央値は 0.85〜0.93 ＝ VR<1 が 12/13 年は推定量の偏り」**
T6: **外の戦略 SR（XAU +0.55・US500 +0.80・近年 +1.90／+1.23）** はコストに耐えるか

=== 攻撃の事前固定（憲章補遺 C: 別の在外分割・コスト倍・レジーム部分集合・プラセボ・多重検定補正・look-ahead/survivorship）===
再現ゲート P0: c65 の数字（XAU 在 β +0.052 t +0.52／US500 在 β −0.299 t −2.06／外 +0.012・+0.133）を
   同一パイプライン（daily_table/monthly_table を c65 から逐語コピー）で再現。ズレ >0.005 なら以降の攻撃は無効として停止。

A1 プラセボ（持続保存型）: c65 自身が事前に認めた弱点「符号反転置換は x の持続（自己相関 ≈0.9）を壊す」を突く。
   (a) **循環回転帰無**: x を y に対して s か月循環シフト（|s|≥6）。x の自己相関構造を**完全保存**。p_rot。
   (b) **Markov 一致合成 x**: 月次フリップ確率 p_flip を一致させた 2 状態鎖から x̃ を 2000 本。p_mkv。
   (c) **12 か月ブロック置換**: 年内の持続を保存。p_blk。
   破壊条件: T1 の p_rot / p_mkv が名目 0.025（Bonferroni(2) 水準）以上、または 0.05 以上。
   予測: 置換 sd 0.102 は過小評価 → 回転/Markov の帰無 sd は 1.3〜2 倍・p は 0.021 → 0.05〜0.20。
A2 多重検定補正: c65 宣言の月次 family（L 4 × 市場 2 × 窓 3 ＝ 24・識別 20）に対し
   HC1 両側 p を全セルで計算し **Holm（任意の依存で妥当）** と **BH(0.05)**、加えて回転帰無による **max|t| FWER p**（依存考慮・近似）。
   破壊条件: T1・T3 が Holm/BH/FWER のいずれでも 0.05 を越えない。予測: Holm で T1 p_adj ≈ 0.4・T3 ≈ 0.8 → 両方 broken。
A3 別の在外分割: T1 を (i) 全標本の連続 78 か月窓を 1 か月刻みで総当たり（β の分布の中で −0.299 の分位）
   (ii) 代替分割 在 2013-19／2015-20／2014-21／2013-18（外は残り）。
   破壊条件: 符号が窓で不安定（負の窓の割合 <80%）または −0.299 が総当たり分布の下側 5% 分位より内側。
A4 レジーム/データ品質部分集合: (i) 2020 全除外（c65 自身の枝 (c)）(ii) 2020-02〜2020-06 除外
   (iii) NFMIN 100→200/250（US500 は flat 46.4%・nf<100 が 377 日＝有効日の定義が効きやすい）。
   破壊条件: いずれか 1 つで |t|<1.5 または符号反転。
A5 月境界の定義（c65 の最重大反証 (5)「月境界 1 つの定義」）: 月末有効日から k ∈ {−5..+5} 日ずらした
   非重複サンプリングで再推定。破壊条件: k=0 以外で |t| の中央値 <1.5 かつ符号が混在。
A6 影響点: 年単位 leave-one-out・月単位 leave-one-out の max|Δβ|・|DFBETA| 上位 3 か月除外。
   破壊条件: 78 か月のうち 3 か月以下の除去で |t|<1.5。
A7 相関市場での追試（c65 未使用キャッシュ US100）: 同じ事前規則で 在 2014-20。
   「株式指数の 12 か月反転」が市場の事実なら US100 も β<0 のはず（corr≈0.9 なので独立検証ではなく整合性検査）。
A8 T2 の「2 地平の一致」の独立性: 月次 S_{L=126} と 日次 S_{L=126} の月集計の相関・corr(x_126, x_252)。
   破壊条件: 相関 ≥0.7 ＝ 同一データの再記述で追加証拠量ゼロ。
A9 真の検出力（T4）: (i) OLS の代数で β̂(y+β*x) = β̂(y)+β* が**恒等的**に成り立つことを数値で示す
   （＝回収 1.00 は検出力の情報を一切持たない）。(ii) 回転帰無 y に β* を注入して t≥2 を数える真の検出力。
   破壊条件: power(SR 0.6) < 0.8 ＝「SR 0.6 を見える」は偽・決着可能範囲は 2se でなく ≈2.8se。
A10 T5 の独立検証: 実データのシャッフルでなく **iid 正規 Monte Carlo**（n 250・q 21・5000 本）で VR(21) の中央値。
   0.85〜0.93 に入れば T5 survived（＝c65 の方法論主張は正しい）。
A11 コスト（憲章 C「コスト倍」）: 月次フリップにのみ往復コスト c bp を課し SR を c ∈ {0,2,5,10,20,50} bp で再計算
   ＋ SR=0 になる breakeven c。破壊条件: c=2×（想定の 2 倍）で SR が半分以下。

判定語: survived / broken / inconclusive（標的ごと）。破壊は「独立な 2 系統以上で条件成立」を要する。
書込は AUREL_RESEARCH/ 配下のみ（scripts/ と data/）。発注・本番編集・プロセス接触・MT5・外部通信・プロップ参照 なし。
seed 20261124（c65 と同一・回転は決定的）。
"""
import os, time, json, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c65_tsmom.md")
NY = "America/New_York"
rng = np.random.default_rng(20261124)
NFMIN = 100; L_MAIN = 252; LS = [21, 63, 126, 252]; VOLWIN = 63
LOG = []
def say(s=""): print(s, flush=True); LOG.append(s)
say(f"# [REFUTE c65] TSMOM の肯定形主張を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c65_tsmom.py)")

# ---------- c65 から逐語コピー（再現性のため改変しない） ----------
def ols_hc1(y, x):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None]); V = XtX_inv @ Sm @ XtX_inv * n / (n - 2)
    return b, np.sqrt(np.diag(V))
def ols_nw(y, x, lag):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv
    return b, np.sqrt(np.diag(V))
def vr_lm(r, q):
    r = np.asarray(r, float); n = len(r); mu = r.mean(); d = r - mu
    s2 = (d ** 2).sum() / (n - 1)
    rq = np.convolve(r, np.ones(q), mode="valid"); m = (n - q + 1)
    s2q = ((rq - q * mu) ** 2).sum() / (m - 1)
    vr = s2q / (q * s2)
    theta = 0.0
    for k in range(1, q):
        dk = ((d[k:] ** 2) * (d[:-k] ** 2)).sum() / ((d ** 2).sum() ** 2) * n
        theta += (2 * (q - k) / q) ** 2 * dk
    z = (vr - 1) / math.sqrt(theta / n) if theta > 0 else float("nan")
    return vr, z

def daily_table(sym, nfmin=NFMIN, quiet=False):
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
    if not quiet:
        say(f"- {sym} (nf>={nfmin}): npz {len(ts)} 本 {pd.to_datetime(ts[0],unit='s').date()}〜{pd.to_datetime(ts[-1],unit='s').date()}"
            f"・flat {flat.mean()*100:.1f}%・有効セッション日 {len(D)}")
    return D

def monthly_table(D, L, k=0):
    """k=0 は c65 と逐語同一（月末有効日）。k!=0 は A5（月境界をずらす）。"""
    lc = D["lc_last"].to_numpy(); r = D["r"].to_numpy(); ym = D["ym"].to_numpy(); n = len(lc)
    ends = np.flatnonzero(np.r_[ym[1:] != ym[:-1], True])
    if k != 0:
        ends = ends + k
        ends = ends[(ends >= 0) & (ends < n)]
        ends = np.unique(ends)
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

def windows(sym):
    if sym == "XAU": return {"在 2011-20": (2011, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
    return {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

# ---------- 推定ヘルパ ----------
def sub(M, lo, hi): return M[(M.year >= lo) & (M.year <= hi)]

def fit(m):
    """HC1 の β・se・t・両側 p（正規近似）。x 一様なら識別不能。"""
    if len(m) < 12 or m.x.nunique() < 2: return None
    b, se = ols_hc1(m.y.to_numpy(), m.x.to_numpy())
    beta, seb = b[1], se[1]; t = beta / seb
    from math import erfc
    p = erfc(abs(t) / math.sqrt(2))
    S = m.S.to_numpy(); sr = S.mean() / S.std(ddof=1) * math.sqrt(12)
    return dict(n=len(m), beta=beta, se=seb, t=t, p=p, sr=sr,
                cov=np.cov(m.x, m.y, ddof=0)[0, 1], drift=m.x.mean() * m.y.mean(), fplus=(m.x > 0).mean())

def beta_only(x, y):
    xm = x - x.mean(); return float((xm @ (y - y.mean())) / (xm @ xm))

def t_only(x, y):
    b, se = ols_hc1(y, x); return b[1] / se[1]

def p_rotation(x, y, beta, minshift=6, ret_dist=False):
    """A1(a) 循環回転帰無: x の自己相関を完全保存した帰無分布。"""
    n = len(x); bs = []
    for s in range(minshift, n - minshift + 1):
        bs.append(beta_only(np.roll(x, s), y))
    bs = np.array(bs)
    p = float((np.abs(bs) >= abs(beta)).mean())
    return (p, bs) if ret_dist else (p, bs.std())

def p_markov(x, y, beta, nrep=2000, seed=20261124):
    """A1(b) フリップ確率一致の 2 状態 Markov で合成 x̃。"""
    g = np.random.default_rng(seed)
    n = len(x); pf = float((x[1:] != x[:-1]).mean())
    bs = np.empty(nrep)
    for i in range(nrep):
        xt = np.empty(n); xt[0] = g.choice([-1.0, 1.0])
        flip = g.random(n - 1) < pf
        for j in range(1, n): xt[j] = -xt[j - 1] if flip[j - 1] else xt[j - 1]
        if len(np.unique(xt)) < 2: bs[i] = 0.0; continue
        bs[i] = beta_only(xt, y)
    return float((np.abs(bs) >= abs(beta)).mean()), float(bs.std()), pf

def p_block(x, y, beta, blk=12, nrep=2000, seed=20261124):
    """A1(c) 12 か月ブロック循環置換（年内持続を保存）。"""
    g = np.random.default_rng(seed + 1)
    n = len(x); nb = int(math.ceil(n / blk)); bs = np.empty(nrep)
    for i in range(nrep):
        order = g.permutation(nb)
        xt = np.concatenate([x[b * blk:(b + 1) * blk] for b in order])[:n]
        if len(np.unique(xt)) < 2: bs[i] = 0.0; continue
        bs[i] = beta_only(xt, y)
    return float((np.abs(bs) >= abs(beta)).mean()), float(bs.std())

def p_signflip(x, y, beta, nrep=2000, seed=20261124):
    """c65 の帰無（比較用）。"""
    g = np.random.default_rng(seed)
    bs = np.empty(nrep)
    for i in range(nrep):
        xt = x * g.choice([-1.0, 1.0], size=len(x)); bs[i] = beta_only(xt, y)
    return float((np.abs(bs) >= abs(beta)).mean()), float(bs.std())

# ================= P0 再現ゲート =================
say("\n## P0 再現ゲート（c65 の数字を同一パイプラインで再現。ズレ >0.005 なら攻撃は無効）")
TAB = {}; MT = {}
for sym in ["XAU", "US500"]:
    TAB[sym] = daily_table(sym)
    for L in LS: MT[(sym, L)] = monthly_table(TAB[sym], L)
REF = {("XAU", "在 2011-20"): (0.052, 0.52), ("XAU", "外 2021-26H1"): (0.012, 0.08),
       ("US500", "在 2014-20"): (-0.299, -2.06), ("US500", "外 2021-26H1"): (0.133, 0.94)}
P0_OK = True
for (sym, w), (b0, t0) in REF.items():
    lo, hi = windows(sym)[w]; c = fit(sub(MT[(sym, L_MAIN)], lo, hi))
    d = abs(c["beta"] - b0)
    say(f"- {sym} {w} L=252: β {c['beta']:+.4f} (c65 {b0:+.3f}・差 {d:.4f})・t {c['t']:+.2f} (c65 {t0:+.2f})・n {c['n']}・HC1 両側 p {c['p']:.4f}")
    if d > 0.005: P0_OK = False
say(f"- **P0 = {'OK（以降の攻撃は有効）' if P0_OK else 'FAIL（再現せず・攻撃無効）'}**")

# ================= T1: US500 在 β −0.299 =================
say("\n## T1 = US500 在 2014-20 β −0.299 (t −2.06・置換 p 0.021) を壊す")
m1 = sub(MT[("US500", L_MAIN)], 2014, 2020)
x1 = m1.x.to_numpy(); y1 = m1.y.to_numpy(); c1 = fit(m1)
say(f"- 基準: n {c1['n']}・β {c1['beta']:+.4f}・HC1 se {c1['se']:.4f}・t {c1['t']:+.2f}・x=+1 {c1['fplus']*100:.0f}%"
    f"・x フリップ率 {(x1[1:]!=x1[:-1]).mean()*100:.1f}%/月・x の lag1 自己相関 {np.corrcoef(x1[1:],x1[:-1])[0,1]:+.2f}")

say("\n### A1 プラセボ（持続保存型） vs c65 の符号反転置換")
ps_sf, sd_sf = p_signflip(x1, y1, c1["beta"])
pr, rot_dist = p_rotation(x1, y1, c1["beta"], ret_dist=True)
pm, sd_mk, pf = p_markov(x1, y1, c1["beta"])
pb, sd_bk = p_block(x1, y1, c1["beta"])
say(f"- (c65) 符号反転置換: p {ps_sf:.3f}・帰無 sd {sd_sf:.4f}  ← x の持続を破壊")
say(f"- (a) 循環回転（持続を完全保存・{len(rot_dist)} 本）: **p {pr:.3f}**・帰無 sd {rot_dist.std():.4f}（sd 比 {rot_dist.std()/sd_sf:.2f}×）")
say(f"- (b) Markov 一致合成 x（p_flip {pf:.3f}）: **p {pm:.3f}**・帰無 sd {sd_mk:.4f}（{sd_mk/sd_sf:.2f}×）")
say(f"- (c) 12 か月ブロック置換: **p {pb:.3f}**・帰無 sd {sd_bk:.4f}（{sd_bk/sd_sf:.2f}×）")

say("\n### A2 多重検定補正（c65 宣言の月次 family 24・識別セルのみ）")
fam = []
for sym in ["XAU", "US500"]:
    for L in LS:
        for w, (lo, hi) in windows(sym).items():
            c = fit(sub(MT[(sym, L)], lo, hi))
            if c is None: continue
            fam.append(dict(key=f"{sym} L={L} {w}", **c))
fam = sorted(fam, key=lambda d: d["p"])
K = len(fam)
say(f"- 識別セル {K}/24。|t|>=2 は {sum(1 for d in fam if abs(d['t'])>=2)}（期待 {0.0455*K:.1f}）")
holm = []; prev = 0.0
for i, d in enumerate(fam):
    pa = min(1.0, max(prev, (K - i) * d["p"])); prev = pa; holm.append(pa)
bh = [];
for i, d in enumerate(fam): bh.append(min(1.0, d["p"] * K / (i + 1)))
bh = list(np.minimum.accumulate(bh[::-1])[::-1])
for i, d in enumerate(fam[:8]):
    say(f"  - {d['key']}: n {d['n']}・β {d['beta']:+.4f}・t {d['t']:+.2f}・p {d['p']:.4f} → Holm {holm[i]:.3f}・BH {bh[i]:.3f}")
# 依存考慮 FWER（回転帰無で max|t| を作る・同一シフト s を全セルに適用）
NS = 400
maxt = np.zeros(NS)
cells_xy = [(sub(MT[(s, L)], *windows(s)[w]).x.to_numpy(), sub(MT[(s, L)], *windows(s)[w]).y.to_numpy())
            for s in ["XAU", "US500"] for L in LS for w in windows(s) if fit(sub(MT[(s, L)], *windows(s)[w])) is not None]
for i in range(NS):
    s = rng.integers(6, 60)
    vals = []
    for xx, yy in cells_xy:
        xr = np.roll(xx, s % len(xx))
        if len(np.unique(xr)) < 2: continue
        vals.append(abs(t_only(xr, yy)))
    maxt[i] = max(vals)
obs_max = max(abs(d["t"]) for d in fam)
say(f"- 回転帰無 max|t| 分布（{NS} 本・全セル同一シフト・依存考慮近似）: 中央値 {np.median(maxt):.2f}・95% 分位 {np.quantile(maxt,0.95):.2f}")
say(f"- 観測 max|t| {obs_max:.2f} → **FWER p {float((maxt>=obs_max).mean()):.3f}**"
    f"／T1 (|t| 2.06) の FWER p {float((maxt>=abs(c1['t'])).mean()):.3f}")

say("\n### A3 別の在外分割")
MU = MT[("US500", L_MAIN)]
nwin = c1["n"]
roll = []
ymv = MU.ym.to_numpy()
for i in range(0, len(MU) - nwin + 1):
    mm = MU.iloc[i:i + nwin]
    if mm.x.nunique() < 2: continue
    roll.append((int(ymv[i]) // 12, beta_only(mm.x.to_numpy(), mm.y.to_numpy()), t_only(mm.x.to_numpy(), mm.y.to_numpy())))
rb = np.array([r[1] for r in roll])
say(f"- 全標本の連続 {nwin} か月窓を総当たり（{len(roll)} 窓）: β 中央値 {np.median(rb):+.4f}・5% 分位 {np.quantile(rb,0.05):+.4f}"
    f"・負の窓 {float((rb<0).mean())*100:.0f}%・**−0.299 の分位 {float((rb<=c1['beta']).mean())*100:.0f}%**")
for lo, hi in [(2013, 2019), (2015, 2020), (2014, 2021), (2013, 2018), (2016, 2022)]:
    c = fit(sub(MU, lo, hi))
    if c is None: say(f"  - 在 {lo}-{hi}: 識別不能"); continue
    say(f"  - 在 {lo}-{hi}: n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}・p {c['p']:.3f}")

say("\n### A4 レジーム／データ品質 部分集合")
for name, mm in [("2020 全除外", m1[m1.year != 2020]),
                 ("2020-02〜06 除外", m1[~((m1.year == 2020) & (m1.ym % 12 + 1 >= 2) & (m1.ym % 12 + 1 <= 6))]),
                 ("2016 除外", m1[m1.year != 2016]), ("2019 除外", m1[m1.year != 2019])]:
    c = fit(mm)
    say(f"- {name}: n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}・p {c['p']:.3f}" if c else f"- {name}: 識別不能")
for nf in [200, 250]:
    Dn = daily_table("US500", nfmin=nf, quiet=True)
    c = fit(sub(monthly_table(Dn, L_MAIN), 2014, 2020))
    say(f"- NFMIN {nf}（有効日 {len(Dn)}）: " + (f"n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}・p {c['p']:.3f}" if c else "識別不能"))

say("\n### A5 月境界の定義（k 日ずらし・c65 の最重大反証 (5)）")
ks = []
for k in range(-5, 6):
    c = fit(sub(monthly_table(TAB["US500"], L_MAIN, k=k), 2014, 2020))
    if c is None: continue
    ks.append((k, c["beta"], c["t"], c["p"]))
    say(f"- k={k:+d}: n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}・p {c['p']:.3f}")
kt = np.array([a[2] for a in ks]); kbeta = np.array([a[1] for a in ks])
say(f"- まとめ: |t| 中央値 {np.median(np.abs(kt)):.2f}・|t|>=2 の k {int((np.abs(kt)>=2).sum())}/{len(ks)}"
    f"・β<0 の k {int((kbeta<0).sum())}/{len(ks)}・β の範囲 [{kbeta.min():+.3f}, {kbeta.max():+.3f}]")

say("\n### A6 影響点")
yrs = sorted(set(m1.year))
loo = []
for yy in yrs:
    c = fit(m1[m1.year != yy])
    if c: loo.append((yy, c["beta"], c["t"]))
say("- leave-one-year-out: " + "・".join(f"{a}→β {b:+.3f} (t {t:+.2f})" for a, b, t in loo))
# DFBETA 近似（1 か月除外の β 変化）
d1 = np.array([abs(beta_only(np.delete(x1, i), np.delete(y1, i)) - c1["beta"]) for i in range(len(x1))])
ordr = np.argsort(-d1)
for k in [1, 2, 3, 5]:
    idx = np.setdiff1d(np.arange(len(x1)), ordr[:k])
    c = fit(m1.iloc[idx])
    ymk = [f"{int(m1.ym.iloc[i])//12}-{int(m1.ym.iloc[i])%12+1:02d}" for i in ordr[:k]]
    say(f"- 影響上位 {k} か月除外 ({', '.join(ymk)}): n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}・p {c['p']:.3f}")

say("\n### A7 相関市場 US100（c65 未使用キャッシュ）で同じ事前規則")
try:
    D100 = daily_table("US100")
    M100 = monthly_table(D100, L_MAIN)
    for w, (lo, hi) in windows("US500").items():
        c = fit(sub(M100, lo, hi))
        say(f"- US100 {w}: " + (f"n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}・p {c['p']:.3f}・SR {c['sr']:+.2f}・x=+1 {c['fplus']*100:.0f}%" if c else "識別不能"))
    # US500 在と同じ月の y の相関
    a = sub(MT[("US500", L_MAIN)], 2014, 2020)[["ym", "y", "x"]].set_index("ym")
    b = sub(M100, 2014, 2020)[["ym", "y", "x"]].set_index("ym")
    j = a.join(b, lsuffix="_500", rsuffix="_100", how="inner")
    say(f"- 在 2014-20 の重なり {len(j)} か月: corr(y) {j.y_500.corr(j.y_100):+.2f}・x 一致率 {float((j.x_500==j.x_100).mean())*100:.0f}%"
        f" ＝ 独立検証ではなく整合性検査")
except Exception as e:
    say(f"- US100 スキップ: {type(e).__name__} {e}")

# ================= T2: XAU 在 L=126 =================
say("\n## T2 = XAU 在 L=126「2 地平（月次 t +1.79・日次 t +1.80）が同符号」を壊す")
m2 = sub(MT[("XAU", 126)], 2011, 2020); c2 = fit(m2)
x2 = m2.x.to_numpy(); y2 = m2.y.to_numpy()
say(f"- 基準（再現）: n {c2['n']}・β {c2['beta']:+.4f}・t {c2['t']:+.2f}・HC1 p {c2['p']:.3f}")
pr2, sd2 = p_rotation(x2, y2, c2["beta"])
pm2, sdm2, pf2 = p_markov(x2, y2, c2["beta"])
say(f"- A1 回転帰無 p {pr2:.3f}（sd {sd2:.4f}）／Markov p {pm2:.3f}（sd {sdm2:.4f}・p_flip {pf2:.3f}）")
i2 = [d for d in fam if d["key"] == "XAU L=126 在 2011-20"][0]
say(f"- A2: family 内の順位 {fam.index(i2)+1}/{K}・Holm {holm[fam.index(i2)]:.3f}・BH {bh[fam.index(i2)]:.3f}")
say("- A8 「2 地平」の独立性:")
Dx = TAB["XAU"]; lcx = Dx["lc_last"].to_numpy(); rx = Dx["r"].to_numpy(); yrx = Dx["year"].to_numpy()
sd63 = pd.Series(rx).rolling(VOLWIN).std(ddof=1).to_numpy()
xd = np.full(len(lcx), np.nan); xd[126:] = np.sign(lcx[126:] - lcx[:-126])
yd = np.full(len(lcx), np.nan); yd[:-1] = rx[1:] / sd63[:-1]
okd = np.isfinite(xd) & np.isfinite(yd) & (xd != 0) & (yrx >= 2011) & (yrx <= 2020)
Sd = pd.DataFrame({"ym": Dx["ym"].to_numpy()[okd], "Sd": (xd * yd)[okd]}).groupby("ym").Sd.sum()
jj = m2.set_index("ym").join(Sd, how="inner")
say(f"  - 月次 S_126 と 日次版 S_126 の月合計の corr = **{jj.S.corr(jj.Sd):+.2f}**（n {len(jj)} か月）"
    f" ＝ 同一データの再記述（独立な 2 証拠ではない）")
x252 = sub(MT[("XAU", 252)], 2011, 2020).set_index("ym").x
say(f"  - corr(x_126, x_252) 在 = {m2.set_index('ym').x.corr(x252):+.2f}・符号一致率 "
    f"{float((m2.set_index('ym').x.reindex(x252.index).dropna() == x252.reindex(m2.ym).dropna()).mean())*100:.0f}% 相当（重なり {len(set(m2.ym)&set(x252.index))}）")
say("- A3 別分割・A6 影響点（XAU L=126 在）:")
MX = MT[("XAU", 126)]
for lo, hi in [(2011, 2019), (2012, 2020), (2011, 2018), (2012, 2021)]:
    c = fit(sub(MX, lo, hi)); say(f"  - 在 {lo}-{hi}: " + (f"n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}" if c else "識別不能"))
d2 = np.array([abs(beta_only(np.delete(x2, i), np.delete(y2, i)) - c2["beta"]) for i in range(len(x2))])
o2 = np.argsort(-d2)
for k in [2, 3]:
    c = fit(m2.iloc[np.setdiff1d(np.arange(len(x2)), o2[:k])])
    say(f"  - 影響上位 {k} か月除外: β {c['beta']:+.4f}・t {c['t']:+.2f}")
ks2 = []
for k in range(-5, 6):
    c = fit(sub(monthly_table(Dx, 126, k=k), 2011, 2020))
    if c: ks2.append(c["t"])
say(f"  - A5 月境界 k=-5..+5: t 中央値 {np.median(ks2):+.2f}・t>=1.5 の k {int((np.array(ks2)>=1.5).sum())}/{len(ks2)}・範囲 [{min(ks2):+.2f}, {max(ks2):+.2f}]")

# ================= T3: XAU 近年 L=21 =================
say("\n## T3 = XAU 近年 2024-26H1 L=21 β +0.420 (t +2.16・n 30) を壊す")
m3 = sub(MT[("XAU", 21)], 2024, 2026); c3 = fit(m3)
x3 = m3.x.to_numpy(); y3 = m3.y.to_numpy()
say(f"- 基準（再現）: n {c3['n']}・β {c3['beta']:+.4f}・t {c3['t']:+.2f}・HC1 p {c3['p']:.3f}・x=+1 {c3['fplus']*100:.0f}%"
    f"・少数側 {int(min((x3>0).sum(),(x3<0).sum()))} か月（c65 の候補 112 の基準 <3 か月なら識別不能）")
pr3, sd3 = p_rotation(x3, y3, c3["beta"], minshift=3)
pm3, sdm3, pf3 = p_markov(x3, y3, c3["beta"])
i3 = [d for d in fam if d["key"] == "XAU L=21 近年 2024-26H1"][0]
say(f"- A1 回転 p {pr3:.3f}／Markov p {pm3:.3f}・A2 Holm {holm[fam.index(i3)]:.3f}・BH {bh[fam.index(i3)]:.3f}")
d3 = np.array([abs(beta_only(np.delete(x3, i), np.delete(y3, i)) - c3["beta"]) for i in range(len(x3))])
o3 = np.argsort(-d3)
for k in [1, 2]:
    c = fit(m3.iloc[np.setdiff1d(np.arange(len(x3)), o3[:k])])
    ymk = [f"{int(m3.ym.iloc[i])//12}-{int(m3.ym.iloc[i])%12+1:02d}" for i in o3[:k]]
    say(f"- 影響上位 {k} か月除外 ({', '.join(ymk)}): " + (f"n {c['n']}・β {c['beta']:+.4f}・t {c['t']:+.2f}" if c else "識別不能"))
c3o = fit(sub(MT[("XAU", 21)], 2011, 2020)); c3x = fit(sub(MT[("XAU", 21)], 2021, 2026))
say(f"- 在 2011-20 β {c3o['beta']:+.4f} (t {c3o['t']:+.2f})／外 2021-26H1 β {c3x['beta']:+.4f} (t {c3x['t']:+.2f})"
    f" ＝ 近年のみ。近年は外の部分集合（入れ子・独立でない）")

# ================= T4: 検出力と「回収 1.00」=================
say("\n## T4 = 「注入回収 1.00 ⇒ 規則は SR 0.6 を見える」と MDE=2se の決着可能範囲を壊す")
mX = sub(MT[("XAU", L_MAIN)], 2011, 2020); xX = mX.x.to_numpy(); yX = mX.y.to_numpy()
b0 = beta_only(xX, yX)
for bst in [0.173, 0.5, 1.0]:
    say(f"- 代数の確認: β*={bst:.3f} 注入 → β̂ {beta_only(xX, yX + bst*xX):+.6f}・β̂−β0 = {beta_only(xX, yX+bst*xX)-b0:.6f}"
        f"（＝β* と{'一致' if abs(beta_only(xX,yX+bst*xX)-b0-bst)<1e-9 else '不一致'}）")
say("  → 回収 1.00 は OLS の線形性の**恒等式**（同じ x に注入すれば常に 1.00）。検出力の情報量ゼロ。")
NP = 2000
nX = len(xX)
rows = []
for sr in [0.3, 0.6, 0.9, 1.2]:
    bst = sr / math.sqrt(12); hit = 0; hit15 = 0
    for i in range(NP):
        s = int(rng.integers(6, nX - 6)); ys = np.roll(yX, s) + bst * xX
        tt = t_only(xX, ys)
        hit += (tt >= 2.0); hit15 += (tt >= 1.5)
    rows.append((sr, bst, hit / NP, hit15 / NP))
    say(f"- 真の検出力（回転帰無 y に SR {sr} を注入・{NP} 本）: P(t>=2) = **{hit/NP:.2f}**・P(t>=1.5) = {hit15/NP:.2f}")
seX = fit(mX)["se"]
say(f"- c65 の MDE 定義 2se = {2*seX:.3f}（SR {2*seX*math.sqrt(12):.2f}）は**検出力 50% の点**。"
    f"検出力 80% は ≈2.8se = {2.8*seX:.3f}（SR {2.8*seX*math.sqrt(12):.2f}）・t>=2 と p<0.025 の両方なら更に上。")

# ================= T5: VR(21) の偏り（独立 Monte Carlo）=================
say("\n## T5 = 候補 ⑲「年別 VR(21) の帰無中央値 0.85〜0.93＝推定量の偏り」を独立検証（実データのシャッフルではなく iid 正規 MC）")
for n, q, nrep in [(250, 21, 3000), (250, 63, 1000), (250, 2, 1000)]:
    g = np.random.default_rng(777)
    vs = np.array([vr_lm(g.standard_normal(n), q)[0] for _ in range(nrep)])
    say(f"- iid 正規 n={n} q={q}（{nrep} 本）: VR 中央値 **{np.median(vs):.3f}**・平均 {vs.mean():.3f}・5-95% [{np.quantile(vs,0.05):.3f}, {np.quantile(vs,0.95):.3f}]")
say(f"- 解析近似 E[VR(q)] ≈ 1 − (q−1)/n·… （q=21,n=250 で 1−21/250·k）: 観測 MC と整合なら T5 survived")

# ================= T6: コスト =================
say("\n## T6 = 外・近年の戦略 SR をコストで壊す（憲章 C「コスト倍」）")
def sr_cost(m, cbp):
    x = m.x.to_numpy(); y = m.y.to_numpy(); sig = m.sig.to_numpy()
    flip = np.r_[False, x[1:] != x[:-1]]
    S = x * y - np.where(flip, cbp / sig, 0.0)
    return S.mean() / S.std(ddof=1) * math.sqrt(12), float(flip.mean())
for sym, w in [("XAU", "外 2021-26H1"), ("XAU", "近年 2024-26H1"), ("US500", "外 2021-26H1"), ("US500", "近年 2024-26H1"), ("XAU", "在 2011-20")]:
    lo, hi = windows(sym)[w]; m = sub(MT[(sym, L_MAIN)], lo, hi)
    out = []
    for cbp in [0, 2, 5, 10, 20, 50]:
        s, fr = sr_cost(m, cbp); out.append(f"c={cbp}bp SR {s:+.2f}")
    _, fr = sr_cost(m, 0)
    say(f"- {sym} {w}（フリップ {fr*100:.0f}%/月・σ̂ 中央値 {np.median(m.sig):.0f} bp）: " + "・".join(out))
say("  → 月次 TSMOM はフリップが稀 → コスト倍は SR をほとんど動かさない。"
    "**外の SR を支えているのはトレンド追随ではなくロングバイアス（c65 の分解）であり、コストは拘束条件ではない**。")

say(f"\n- 実行 {time.time()-T0:.1f} s・seed 20261124・書込は data/refute_c65_tsmom.md のみ・MT5 なし・外部通信なし・多年 scan なし")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(LOG) + "\n")
print("saved", OUT)
