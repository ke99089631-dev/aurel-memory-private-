# -*- coding: utf-8 -*-
"""
[cycle19 研究レーン 2026-11-07] 【探索・市場構造 → 深化・レジーム（副）】金 M5 の日内「分散比 VR(q)」（自己相関構造）は
2021+ で随機歩行からトレンド型へ変わったか。月次 VR は翌月の壁→壁(再加速) R を条件づけるか。

動機（AI らしい問い）: 壁→壁/再加速は「短い地平（1〜4 時間）で動きが続く」ことに賭ける構造。優位がレジーム依存（D2）なら、
金 M5 系列そのものの短地平の自己相関構造（分散比 VR(q)=Var(r_q)/(q·Var(r_1))、Lo–MacKinlay）が 2021+ で変わっている筈。
cycle9 の ER20/ER60（日足・経路効率）は null で閉じたが、VR は **日内・自己相関ベース**の別統計（同じ量の再試行ではない）。
主目的は市場構造の記述（探索）。条件づけ（深化）は 1 セルだけ事前固定し、入口フィルタには変換しない（補遺 D）。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/XAU_m5_close.npz（bid・暦時刻の完全格子・前値埋め・穴 19＝ts 一致参照 ⑫）、
  data/c8_crossasset_features.csv（再加速 closed 19404 本・entry_time/side/R/year/hold/risk/exit）、data/c1_reaccel_paths_2010_2026.json（FEED_TOL のみ）。
取引足の定義（ET 現地・⑰）: 閉場＝金 17:00 以降・土・日 18:00 前・月〜木 17:00–17:55（2010-12 にはブレイクが無いがその 1 時間も一律除く）。
  セッション日 = (ET 時刻 + 6h) の暦日（18:00 ET が翌セッション日の先頭）。リターン r_1 = Δlog close は**同じセッション日・格子連続**の対だけ。
  q 本リターン r_q = lc[i]−lc[i−q] は同じセッション日・ts 差 = 300q・途中に閉場足 0 本の時だけ有効（重なりあり・Lo–MacKinlay）。
統計（年別・月別）: ρ_k (k=1..48・年内で平均を引く・不均一分散ロバスト t = Σ r_i r_{i−k} / sqrt(Σ r_i² r_{i−k}²))、
  VR(q) q∈{12,48,144}（1h/4h/12h）直接推定（重なり q 本リターンの分散 ÷ q·分散 r_1）と Lo–MacKinlay 不均一分散ロバスト z（M2）。
  セッション内 flat 足比率（stale quote の代理・年別に併記）。日別 VR(48) の年内中央値（尻尾の少数日への感度）。
窓: 在 2010-20（11 年・132 月）／外 2021-26H1（6 年・66 月）／近年 2024-26H1（記述）。
判定 H_E（探索・主）: 年別 VR(48) の 外 平均 − 在 平均 の Welch t ≥ 2 → 「2021+ で日内トレンド型へ変化」、≤ −2 → 「平均回帰型へ」、
  それ以外 null（MDE = 2·se を添える）。月別 VR(48) の Welch t（66 vs 132）を併記。予測の向き: **外 > 在**（優位の局在と整合する向き）。
判定 H_D（深化・副・1 セル）: 月 m の再加速 closed の平均 R*（R* = R + ft·1{SL,TP}・①）を、**前月 m−1 の VR(48)**（月初に既知）に
  WLS（重み n_m）で回帰。予測 β > 0。PASS = 在 t ≥ 2 ∧ 外 t ≥ 1.5 ∧ 外 置換 p < 0.05（VR 系列の月循環シフト全通り・⑨の月版）。
  それ以外 null（MDE 2·se）。陽性対照（⑦）: 外の R*̄ に +0.05R·sign(z(VR_{m−1})) を注入して同じ規則の t を印字。
  記述（判定不使用・機構の問いへの回答のみ）: 同月 VR(48) と R*̄_m の関係（同時期＝前向き不可）、VR 三分位別の R*̄。
事前の最重大反証: (i) **stale quote**: 更新が遅い年（セッション内 flat 足が多い 2010-12）は観測リターンに正の自己相関が人工的に入り VR>1 に
  見える → 年別 flat 比率との年横断相関を印字し、|ρ|>0.5 なら「構造変化」は配信品質で汚染と宣言。(ii) VR>1 は少数のトレンド日で作れる
  → 日別 VR の中央値で再確認。(iii) 同月の VR×R は機械的（トレンド日が両方を作る）→ 判定に使わない。(iv) 月次メーターは遅い（cycle9 の
  閉鎖理由）→ 1 セルのみ・PASS でも「レジーム記述」であって昇格候補でも入口でもない。
入力は既存キャッシュのみ・scan 無し・M5 原本読込なし・MT5 無し・外部通信無し。seed 20261107。
"""
import os, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c19_variance_ratio_regime_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261107)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle19] 金 M5 日内 分散比 VR(q) のレジーム構造と翌月 R の条件づけ — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c19_variance_ratio_regime.py)")

# ---------- XAU grid ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float); lc = np.log(cl)
n = len(ts)
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert(NY)
h = t_ny.hour.to_numpy(); wd = t_ny.weekday.to_numpy()
sess_dt = t_ny + pd.Timedelta(hours=6)
SESS = (sess_dt.year * 10000 + sess_dt.month * 100 + sess_dt.day).to_numpy()
SYR = sess_dt.year.to_numpy(); SMO = (sess_dt.year * 100 + sess_dt.month).to_numpy()
closed = (wd == 5) | ((wd == 4) & (h >= 17)) | ((wd == 6) & (h < 18)) | ((wd <= 3) & (h == 17))
trade = ~closed
r1 = np.full(n, np.nan); r1[1:] = np.diff(lc)
flat_all = np.zeros(n, bool); flat_all[1:] = np.diff(lc) == 0
gap_after = np.where(np.diff(ts) != 300)[0]
say(f"- npz {n} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）、flat 全体 {flat_all.mean()*100:.1f}%（⑪）、格子の穴 {len(gap_after)}（⑫）、取引足 {trade.mean()*100:.1f}%")
# weekday flat print (⑪)
say("- 曜日別 flat 比率: " + " ".join(f"{d}:{flat_all[wd==i].mean()*100:.1f}%" for i, d in enumerate("月火水木金土日")))
ccl = np.cumsum(closed.astype(np.int64))  # closed bars count prefix
def valid_q(q):
    """overlapping q-bar returns valid: same session day, ts diff == 300q, zero closed bars in (i-q, i]"""
    v = np.zeros(n, bool)
    v[q:] = (SESS[q:] == SESS[:-q]) & ((ts[q:] - ts[:-q]) == 300 * q) & ((ccl[q:] - ccl[:-q]) == 0) & trade[q:]
    return v
V1 = valid_q(1)
say(f"- 有効 r_1（同セッション日・連続・取引足）{V1.sum()}（セッション内 flat 比率 {(r1[V1]==0).mean()*100:.2f}%）")

# ---------- per-group statistics ----------
KS = [1, 2, 3, 6, 12, 24, 48]
QS = [12, 48, 144]
VQ = {q: valid_q(q) for q in QS}
RQ = {q: np.full(n, np.nan) for q in QS}
for q in QS: RQ[q][q:] = lc[q:] - lc[:-q]

def acf_t(mask, k):
    """rho_k and robust t within group mask (pairs i, i-k both valid r_1, contiguous within session)."""
    i = np.flatnonzero(mask & V1); i = i[i >= k]
    ok = V1[i - k] & (SESS[i] == SESS[i - k]) & ((ts[i] - ts[i - k]) == 300 * k) & ((ccl[i] - ccl[i - k]) == 0)
    i = i[ok]
    if len(i) < 100: return np.nan, np.nan, len(i)
    a = r1[i]; b = r1[i - k]; mu = r1[mask & V1].mean(); a = a - mu; b = b - mu
    rho = (a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum())
    t = (a * b).sum() / math.sqrt(((a * a) * (b * b)).sum())
    return rho, t, len(i)

def vr(mask, q):
    """Lo-MacKinlay VR(q) direct (overlapping) with heteroskedasticity-robust z (M2)."""
    m1 = mask & V1; x = r1[m1]; mu = x.mean(); s1 = ((x - mu) ** 2).mean()
    mq = mask & VQ[q]; y = RQ[q][mq]
    if len(x) < 500 or len(y) < 100: return np.nan, np.nan, len(y)
    sq = ((y - q * mu) ** 2).mean()
    VR = sq / (q * s1)
    # theta = sum_{k=1}^{q-1} (2(q-k)/q)^2 delta_k ; delta_k = sum (r_i-mu)^2 (r_{i-k}-mu)^2 / (sum (r_i-mu)^2)^2
    i = np.flatnonzero(m1); d = r1 - mu; den = (d[i] ** 2).sum() ** 2
    theta = 0.0
    for k in range(1, q):
        j = i[i >= k]; ok = m1[j - k] & (SESS[j] == SESS[j - k]) & ((ts[j] - ts[j - k]) == 300 * k)
        j = j[ok]
        dk = ((d[j] ** 2) * (d[j - k] ** 2)).sum() / den
        theta += (2 * (q - k) / q) ** 2 * dk
    z = (VR - 1) / math.sqrt(theta) if theta > 0 else np.nan
    return VR, z, len(y)

def daily_vr_median(mask, q=48):
    """median over session days of per-day VR(q) (fat-tail sensitivity) — grouped, no per-day scan."""
    m1 = mask & V1; mq = mask & VQ[q]
    d1 = pd.DataFrame({"s": SESS[m1], "x": r1[m1]}); d1["x2"] = d1.x ** 2
    g1 = d1.groupby("s").agg(mu=("x", "mean"), x2=("x2", "mean"), n1=("x", "size"))
    g1["var"] = g1.x2 - g1.mu ** 2
    dq = pd.DataFrame({"s": SESS[mq], "y": RQ[q][mq]})
    mu = g1["mu"].reindex(dq.s.to_numpy()).to_numpy()
    dq["e2"] = (dq.y.to_numpy() - q * mu) ** 2
    gq = dq.groupby("s").agg(e2q=("e2", "mean"), nq=("e2", "size"))
    df = g1.join(gq, how="inner")
    df = df[(df.n1 >= 100) & (df.nq >= 50) & (df["var"] > 0)]
    vrd = df["e2q"] / (q * df["var"])
    return (float(np.median(vrd)) if len(vrd) else np.nan), int(len(vrd))

# ---------- yearly table ----------
say("\n## 1. 年別: 自己相関 ρ_k（ロバスト t）・VR(q)（LM z）・セッション内 flat 比率（stale 代理）・日別 VR48 中央値")
say("| 年 | n r_1 | flat% | ρ1 (t) | ρ2 (t) | ρ3 (t) | ρ6 (t) | ρ12 (t) | VR12 (z) | VR48 (z) | VR144 (z) | 日別VR48 中央値 (日数) |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|")
YEARS = list(range(2010, 2027))
YV = {}
for y in YEARS:
    m = SYR == y
    nr = (m & V1).sum()
    if nr < 1000: continue
    fl = (r1[m & V1] == 0).mean() * 100
    row = [f"{y}", f"{nr}", f"{fl:.1f}"]
    rhos = {}
    for k in [1, 2, 3, 6, 12]:
        rho, t, _ = acf_t(m, k); rhos[k] = rho; row.append(f"{rho:+.4f} ({t:+.1f})")
    vrs = {}
    for q in QS:
        v, z, nq = vr(m, q); vrs[q] = (v, z); row.append(f"{v:.3f} ({z:+.1f})")
    dmed, nd = daily_vr_median(m, 48); row.append(f"{dmed:.3f} ({nd})")
    YV[y] = dict(flat=fl, rho=rhos, vr=vrs, dmed=dmed, n=nr)
    say("| " + " | ".join(row) + " |")

# ---------- window table ----------
say("\n## 2. 窓別（プール）: VR(q) と LM z")
WIN = {"在2010-20": (SYR >= 2010) & (SYR <= 2020), "外2021-26H1": SYR >= 2021, "近年2024-26H1": SYR >= 2024}
for wn, wm in WIN.items():
    parts = []
    for q in QS:
        v, z, nq = vr(wm, q); parts.append(f"VR{q} {v:.3f} (z{z:+.1f}, n{nq})")
    rho1, t1, _ = acf_t(wm, 1); rho2, t2, _ = acf_t(wm, 2)
    say(f"- {wn}: ρ1 {rho1:+.4f} (t{t1:+.1f})・ρ2 {rho2:+.4f} (t{t2:+.1f})・" + "・".join(parts))

# ---------- H_E: yearly VR48 在 vs 外 ----------
say("\n## 3. H_E（探索・主）: 年別 VR(48) 外 2021-26H1 − 在 2010-20")
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, se, d / se
res_E = {}
for q in QS:
    a = [YV[y]["vr"][q][0] for y in YV if y >= 2021]; b = [YV[y]["vr"][q][0] for y in YV if 2010 <= y <= 2020]
    d, se, t = welch(a, b)
    res_E[q] = (d, se, t)
    say(f"- VR{q}: 在 平均 {np.mean(b):.3f}（年 sd {np.std(b, ddof=1):.3f}・n{len(b)}）／外 平均 {np.mean(a):.3f}（sd {np.std(a, ddof=1):.3f}・n{len(a)}）→ 差 **{d:+.3f} (Welch t{t:+.2f}, MDE {2*se:.3f})**")
# stale contamination check
fl = np.array([YV[y]["flat"] for y in YV]); v48 = np.array([YV[y]["vr"][48][0] for y in YV]); v12 = np.array([YV[y]["vr"][12][0] for y in YV])
from scipy.stats import spearmanr
rs48 = spearmanr(fl, v48).correlation; rs12 = spearmanr(fl, v12).correlation
say(f"- 反証 (i) stale: 年横断 Spearman(flat%, VR48) **{rs48:+.2f}**、(flat%, VR12) {rs12:+.2f}（|ρ|>0.5 なら配信品質で汚染）")
a = [YV[y]["dmed"] for y in YV if y >= 2021]; b = [YV[y]["dmed"] for y in YV if 2010 <= y <= 2020]
d, se, t = welch(a, b)
say(f"- 反証 (ii) 日別 VR48 中央値: 在 {np.mean(b):.3f}／外 {np.mean(a):.3f}・差 {d:+.3f} (t{t:+.2f})")

# ---------- monthly VR48 ----------
say("\n## 4. 月別 VR(48)（H_D の説明変数・月初に既知）")
MONTHS = np.unique(SMO[V1])
MV = {}
for mo in MONTHS:
    m = SMO == mo
    if (m & V1).sum() < 2000: continue
    v, z, nq = vr(m, 48); MV[mo] = v
mv = pd.Series(MV).sort_index()
say(f"- 月数 {len(mv)}（{mv.index.min()}〜{mv.index.max()}）、VR48 中央値 {mv.median():.3f}・p10 {mv.quantile(.1):.3f}・p90 {mv.quantile(.9):.3f}、lag1 自己相関 {mv.autocorr(1):+.2f}")
a = mv[mv.index >= 202101].to_numpy(); b = mv[(mv.index >= 201001) & (mv.index <= 202012)].to_numpy()
d, se, t = welch(a, b)
say(f"- 月別 Welch: 在 {b.mean():.3f} (n{len(b)})／外 {a.mean():.3f} (n{len(a)}) → 差 **{d:+.3f} (t{t:+.2f})**（月 lag1 自己相関 {mv.autocorr(1):+.2f} → 過分散に注意 ⑫）")

# ---------- trades ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
FT = J["frozen"]["FEED_TOL"]
X["ft"] = FT / X["risk"]; X["Rs"] = X["R"] + X["ft"] * X["exit"].isin(["SL", "TP"])
e_utc = pd.to_datetime(X["entry_time"], unit="s", utc=True); e_ny = e_utc.dt.tz_convert(NY) + pd.Timedelta(hours=6)
X["mo"] = (e_ny.dt.year * 100 + e_ny.dt.month).to_numpy()
G = X.groupby("mo").agg(Rbar=("Rs", "mean"), n=("Rs", "size"), Rsd=("Rs", "std")).reset_index()
say(f"\n- 本 {len(X)} {e_utc.iloc[0].date()}〜{e_utc.iloc[-1].date()}（⑩）、FEED_TOL {FT}、R* 平均 {X.Rs.mean():+.4f}、月 {len(G)}・本/月 中央値 {G.n.median():.0f}")
# previous-month VR
mv_idx = mv.index.to_numpy()
def prev_month(mo):
    y, m = divmod(mo, 100); return (y - 1) * 100 + 12 if m == 1 else mo - 1
G["vr_prev"] = [MV.get(prev_month(mo), np.nan) for mo in G.mo]
G["vr_same"] = [MV.get(mo, np.nan) for mo in G.mo]
G = G.dropna(subset=["vr_prev"]).reset_index(drop=True)
G["yr"] = G.mo // 100

def wls(y, x, w):
    Z = np.column_stack([np.ones(len(y)), x]); Wm = np.diag(w)
    A = np.linalg.pinv(Z.T @ Wm @ Z); b = A @ Z.T @ Wm @ y; e = y - Z @ b
    # HC1 robust
    meat = (Z * (w * e)[:, None]).T @ (Z * (w * e)[:, None]); V = A @ meat @ A * len(y) / (len(y) - 2)
    se = np.sqrt(np.diag(V)); return b[1], se[1], b[1] / se[1]

say("\n## 5. H_D（深化・副・1 セル）: 月 m の平均 R*（再加速 closed・WLS 重み n_m）~ 前月 VR(48)")
WT = {"在2010-20": (G.yr >= 2010) & (G.yr <= 2020), "外2021-26H1": G.yr >= 2021, "近年2024-26H1": G.yr >= 2024}
res_D = {}
for wn, wm in WT.items():
    g = G[wm]
    if len(g) < 12: say(f"- {wn}: 月 {len(g)} 不足"); continue
    x = g.vr_prev.to_numpy(); xz = (x - x.mean()) / x.std(ddof=1); y = g.Rbar.to_numpy(); w = g.n.to_numpy().astype(float)
    b, se, t = wls(y, xz, w)
    bu, seu, tu = wls(y, xz, np.ones(len(y)))
    # permutation: circular shift of VR series (all shifts)
    tt = []
    for s in range(1, len(x)):
        xs = np.roll(xz, s); bb, ss, tsh = wls(y, xs, w); tt.append(tsh)
    tt = np.array(tt); p = (np.abs(tt) >= abs(t)).mean()
    # same-month (descriptive)
    xs_ = g.vr_same.to_numpy(); xsz = (xs_ - np.nanmean(xs_)) / np.nanstd(xs_, ddof=1); ok = np.isfinite(xsz)
    bs_, ses_, ts_ = wls(y[ok], xsz[ok], w[ok])
    # tertiles of vr_prev
    q1, q2 = np.quantile(x, [1 / 3, 2 / 3]); lo = x <= q1; hi = x >= q2
    Rlo = np.average(y[lo], weights=w[lo]); Rhi = np.average(y[hi], weights=w[hi])
    # injection positive control
    yin = y + 0.05 * np.sign(xz); bi, sei, ti = wls(yin, xz, w)
    res_D[wn] = dict(b=b, se=se, t=t, p=p, n=len(g))
    say(f"- {wn}: 月 {len(g)}・β(R*̄ per 1sd VR_prev) **{b:+.4f}R (t{t:+.2f}, MDE {2*se:.4f}R)**・非加重 {bu:+.4f} (t{tu:+.2f})・循環シフト置換 p **{p:.3f}**（帰無 t sd {tt.std():.2f}）"
        f"・前月 VR 三分位 下 {Rlo:+.4f}／上 {Rhi:+.4f}（差 {Rhi-Rlo:+.4f}R）・注入 +0.05R·sign → t{ti:+.2f}・【記述】同月 VR β {bs_:+.4f} (t{ts_:+.2f})")

# ---------- yearly VR vs yearly R (descriptive) ----------
say("\n## 6. 記述: 年別 VR48 と年別 平均 R*（同時期・D2: 判定不使用）")
GY = X.assign(yr=(X.mo // 100)).groupby("yr").agg(Rbar=("Rs", "mean"), n=("Rs", "size"))
rows = []
for y in YV:
    if y in GY.index: rows.append((y, YV[y]["vr"][48][0], YV[y]["vr"][12][0], GY.loc[y, "Rbar"], GY.loc[y, "n"]))
say("| 年 | VR48 | VR12 | 平均 R* | n |"); say("|---|---|---|---|---|")
for y, v48_, v12_, rb, nn in rows: say(f"| {y} | {v48_:.3f} | {v12_:.3f} | {rb:+.4f} | {nn} |")
arr = np.array([(v48_, rb) for _, v48_, _, rb, _ in rows])
say(f"- 年横断 Spearman(VR48, 平均R*) {spearmanr(arr[:,0], arr[:,1]).correlation:+.2f}（n{len(arr)}・記述）")

# ---------- verdict ----------
say("\n## 判定（事前固定）")
d, se, t = res_E[48]
if t >= 2: vE = "変化あり（2021+ で日内トレンド型へ・外 > 在）"
elif t <= -2: vE = "変化あり（逆向き・平均回帰型へ）"
else: vE = f"null（年別 VR48 の在外差は MDE {2*se:.3f} 以下）"
say(f"- H_E: ΔVR48 {d:+.3f} (Welch t{t:+.2f}) → **{vE}**")
if "在2010-20" in res_D and "外2021-26H1" in res_D:
    i_, o_ = res_D["在2010-20"], res_D["外2021-26H1"]
    ok = (i_["t"] >= 2) and (o_["t"] >= 1.5) and (o_["p"] < 0.05)
    say(f"- H_D: 在 t{i_['t']:+.2f}／外 t{o_['t']:+.2f}・置換 p {o_['p']:.3f} → **{'PASS（前月 VR48 が翌月 R*̄ を条件づける・レジーム記述）' if ok else f'null（MDE 在 {2*i_['se']:.4f}R／外 {2*o_['se']:.4f}R）'}**")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
