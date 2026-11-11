# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-11 反証レーン] 対象: cycle37 (09:55) H_B PASS
「壁幅（週平均 log risk_bp）の lag1 持続（生 r 在 +0.589／外 +0.599）は GVZ・RVt(21)・ATR14 のどれでも消えない
 （残差 r1 在 +0.553／外 +0.501・比 0.94／0.84）のに ATR14 の持続は GVZ で 6〜8 割消える ＝ 幾何はボラと独立な状態」
周辺の知識 W1「ボラ・レジームの別名ではなく壁の配置固有の状態」／W2「対照 ATR14 は同じ残差化で比 0.18／0.38」／
W3 次の枝 (b)「同一壁の再利用で説明されるかは未分離（研究レーン自身の最重大反証）」。

=== 事前固定（この docstring を書いてから数字を見る）===
入力: data/refute_c4_scan_paths_2010_2026.json・data/macro/XAU_m5_ohlc.npz（高安）・data/macro/XAU_m5_close.npz・data/macro/GVZCLS.csv。
  既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し。seed 20261111。コスト倍は取引規則でないため該当なし。
週・有効週・窓・GVZ_known・RVt・lag1 r（連続有効週ペア）・置換帰無 2000・年内シャッフル プラセボ 200 は c37 と同じ定義。
R0 再現: G1 生 r1 在/外 と GVZ+RVt 残差 r1 在/外 が c37 表と ±0.005 で一致すること。

R1 同一壁の再利用（主・研究レーンの (i)）: 建玉価格 entry = C[ie] − sgn·x0·risk（refute_c35 の規約・exit 一致 100%）から
  SL = entry − sgn·risk・TP = entry + sgn·b·risk を復元。本 j（週 w）が「再利用」= 直前 L 日（L=7: 前週／L=28）に建った本 i の
  SL または TP 水準と |level_j − level_i| ≤ tol（tol = 0.5 USD 主・2.0 USD 副）で一致する水準を 1 つ以上持つ。
  G1_new = 週内「再利用でない本」だけの log risk_bp 平均（≥3 本・無ければ NaN）・G1_reuse = 再利用本だけ。
  判定: 【broken】= 在 ∧ 外 とも G1_new（L=7・tol 0.5）の生 lag1 r < 0.5 × c37 の生 r1（0.589／0.599）
         【survived】= 在 ∧ 外 とも ≥0.5× ∧ 置換 p <0.025（Bonferroni(3) 相当 0.05/2 片側）
         他は inconclusive。残差（GVZ+RVt）版の比も併記（H_B の規則を G1_new に再適用）。
  事前の反証（自分の結論への）: 同一壁の定義は水準の一致のみ（レンジが同じでも壁が少し更新されれば「新しい壁」になる）→ tol 2.0 を併記。
R2 レンジ地平のボラ（主）: c37 の候補ドライバは 30 日 IV・21 日 RV・70 分 ATR＝壁の形成地平（数時間〜数日）を跨いでいない。
  週初に既知の追加ドライバ: log RNGp = 前 5 セッション日の高安レンジ（max high − min low・bp）／log DR5 = 前 5 セッション日の日次レンジ平均（bp）／
  log RV5 = 前 5 日 RV。残差化 G1 on [log GVZ, log RVt, log RNGp, log DR5]（すべて週初既知・look-ahead assert）。
  判定: 【broken】= 在 ∧ 外 とも 残差 r1 < 0.5 × 生 r1（c37 の H_A 規則を正しい地平のドライバで適用）
         【survived】= 在 ∧ 外 とも ≥0.5× ∧ p <0.025／他 inconclusive。
  対照 (a) 同じ残差化（GVZ+RVt）が log DR5・log RNGp 自身の持続を消すか（比）。消さないなら W2 の「ATR は消える」対照は
  70 分 ATR 固有で、数日レンジ型のボラ量には効かない＝「ボラと独立」は「GVZ が数日レンジを包含しない」の言い換え。
  対照 (b) 同時週レンジ log RNGc（未知・上限）で残差化した比。(c) 年内シャッフル プラセボ（RNGp・DR5 の行）で校正。
R3 別分割（記述）: 独立 4 窓 2010-14／2015-20／2021-23／2024-26H1・偶数/奇数年 の G1 生・残差(c37)・残差(R2) 比。lag 1..8 プロファイル。
R4 レジーム（記述）: GVZ_known 在三分位（両週とも同じ分位のペア）内の G1 生 r1。
R5 構成（主・副次）: 本レベル log risk_bp を 窓内 jh×side×wall_kind 固定効果で残差化 → 週平均 → 生 r1。
  判定: 【broken】= 在 ∧ 外 とも < 0.5× c37 生 r1／【survived】= ≥0.5× ∧ p<0.025。
総合: H_B は R1 または R2 が broken なら broken、R1・R2・R5 すべて survived なら survived、他は inconclusive。
多重検定: 標的 3（R1・R2・R5）→ 置換 p 閾値 0.025 は Bonferroni(3) 0.0167 より緩い＝名目 0.0167 も併記。R3・R4・対照は記述。
"""
import os, time, json, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c37_geometry.md")
NY = "America/New_York"
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c37] 壁幅の持続はボラと独立か — 同一壁再利用・レンジ地平ボラ・構成 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c37_geometry.py)")

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
W4 = {"2010-14": (2010, 2014), "2015-20": (2015, 2020), "2021-23": (2021, 2023), "2024-26H1": (2024, 2026)}
C37 = {"在 2010-20": (0.589, 0.553), "外 2021-26H1": (0.599, 0.501)}
H = 21; NMIN = 5; NPERM = 2000; NPLA = 200; NWLAG = 4

# ---------- trades ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["week"] = tr["ts"].dt.to_period("W-SUN")
tr["dec"] = tr["exit"].isin(["SL", "TP"])
N0 = len(tr)

zo = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
TS = zo["ts"].astype(np.int64); HI = zo["high"].astype(float); LO = zo["low"].astype(float); C = zo["close"].astype(float)
NB = len(TS)
et = tr["entry_time"].to_numpy(np.int64)
ie = np.clip(np.searchsorted(TS, et), 0, NB - 1); ok_ie = TS[ie] == et
pos = np.clip(np.searchsorted(TS, et - 300), 0, NB - 1)
tr["P"] = C[pos]
sgn = np.where(tr["side"].to_numpy() == "BUY", 1.0, -1.0)
risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); x0 = tr["x0"].to_numpy(float)
entry = C[ie] - sgn * x0 * risk
tr["entry"] = entry; tr["SL"] = entry - sgn * risk; tr["TP"] = entry + sgn * bb * risk
tr["risk_bp"] = tr["risk"] / tr["P"] * 1e4; tr["lrb"] = np.log(tr["risk_bp"])
say(f"- 本 {N0}・建玉足 ts 一致 {ok_ie.mean()*100:.2f}%・entry−close(前足) 中央値 {np.median(entry - tr.P):+.3f} USD・|entry−close(前足)| p90 {np.quantile(np.abs(entry-tr.P),.9):.2f}・risk 中央値 {np.median(risk):.2f} USD")

# ---------- session days: RV, daily range ----------
lc = np.log(C); r = np.zeros(NB); r[1:] = np.diff(lc); flat = r == 0.0
dt_ny = pd.to_datetime(TS, unit="s", utc=True).tz_convert(NY)
sess = dt_ny + pd.Timedelta(hours=6)
S = (sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy())
df = pd.DataFrame({"s": S, "r2": r ** 2, "nf": (~flat).astype(np.int32), "hi": np.where(flat, np.nan, HI), "lo": np.where(flat, np.nan, LO), "c": C})
g = df.groupby("s", sort=True)
D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum(), "hi": g["hi"].max(), "lo": g["lo"].min(), "c": g["c"].last()})
D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d")
D = D[(D["date"].dt.weekday <= 4) & (D["nf"] >= 100)].reset_index(drop=True)
D["drng_bp"] = (D["hi"] - D["lo"]) / D["c"] * 1e4
cs = np.concatenate([[0.0], np.cumsum(D["rv"].to_numpy())]); i = np.arange(len(D))
def trail_rv(h):
    out = np.full(len(D), np.nan); ok = i - h + 1 >= 0
    out[ok] = 100 * np.sqrt(252.0 / h * (cs[i[ok] + 1] - cs[i[ok] - h + 1])); return out
D["RVt"] = trail_rv(H); D["RV5"] = trail_rv(5)
D["DR5"] = D["drng_bp"].rolling(5).mean()
D["RNGp"] = (D["hi"].rolling(5).max() - D["lo"].rolling(5).min()) / D["c"] * 1e4
say(f"- 有効セッション日 {len(D)}・日次レンジ 中央値 {D.drng_bp.median():.1f} bp・前 5 日レンジ RNGp 中央値 {D.RNGp.median():.1f} bp・DR5 {D.DR5.median():.1f} bp")

gv = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"), na_values="."); gv.columns = ["date", "gvz"]
gv["date"] = pd.to_datetime(gv["date"]); gv = gv.dropna().sort_values("date")

# ---------- same-wall reuse flags (R1) ----------
tr = tr.sort_values("entry_time").reset_index(drop=True)
etv = tr["entry_time"].to_numpy(np.int64); SLv = tr["SL"].to_numpy(); TPv = tr["TP"].to_numpy()
wk_start = np.array([p.start_time.value // 10**9 for p in tr["week"]], dtype=np.int64)
def reuse_flags(Ldays, tol):
    """本 j が、週初より前 L 日以内に建った本 i（entry_time < week_start_j, ≥ week_start_j − L 日）の SL/TP 水準と tol 以内で一致するか"""
    flag = np.zeros(len(tr), bool)
    lo_t = wk_start - Ldays * 86400
    a = np.searchsorted(etv, lo_t, side="left"); b = np.searchsorted(etv, wk_start, side="left")
    for j in range(len(tr)):
        if b[j] <= a[j]: continue
        lv = np.concatenate([SLv[a[j]:b[j]], TPv[a[j]:b[j]]])
        if np.abs(lv - SLv[j]).min() <= tol or np.abs(lv - TPv[j]).min() <= tol: flag[j] = True
    return flag
FL = {}
for Ld in (7, 28):
    for tol in (0.5, 2.0):
        FL[(Ld, tol)] = reuse_flags(Ld, tol)
tr["reuse"] = FL[(7, 0.5)]
yr = tr["year"].to_numpy()
say("- 同一壁再利用率（週初より前 L 日の本の SL/TP 水準と tol 以内一致）: " + "・".join(
    f"L{Ld} tol{tol}: 在 {100*FL[(Ld,tol)][yr<=2020].mean():.1f}%／外 {100*FL[(Ld,tol)][yr>=2021].mean():.1f}%／近年 {100*FL[(Ld,tol)][yr>=2024].mean():.1f}%" for (Ld, tol) in FL))
# within-week distinct wall pairs
def n_distinct(g_, tol=0.5):
    lv = np.round(np.concatenate([g_["SL"].to_numpy(), g_["TP"].to_numpy()]) / tol) * tol
    return len(np.unique(lv))
# same-week: fraction of trades whose SL/TP matches an EARLIER trade in the same week
same_wk = np.zeros(len(tr), bool)
for w_, idx in tr.groupby("week").indices.items():
    idx = np.sort(idx)
    for k in range(1, len(idx)):
        prev = np.concatenate([SLv[idx[:k]], TPv[idx[:k]]])
        if np.abs(prev - SLv[idx[k]]).min() <= 0.5 or np.abs(prev - TPv[idx[k]]).min() <= 0.5: same_wk[idx[k]] = True
say(f"- 同週内で先行本と壁水準一致（tol 0.5）: 在 {100*same_wk[yr<=2020].mean():.1f}%／外 {100*same_wk[yr>=2021].mean():.1f}%")

# ---------- composition residual (R5) ----------
tr["cell"] = tr["jh"].astype(str) + "_" + tr["side"] + "_" + tr["wall_kind"]
tr["lrb_fe"] = np.nan
for wn, (y0, y1) in WIN.items():
    m = (tr.year >= y0) & (tr.year <= y1)
    if wn == "近年 2024-26H1": continue
    mu = tr.loc[m].groupby("cell")["lrb"].transform("mean")
    tr.loc[m, "lrb_fe"] = tr.loc[m, "lrb"] - mu + tr.loc[m, "lrb"].mean()

# ---------- weekly ----------
dd = tr[tr.dec]
gw = dd.groupby("week").agg(n=("dec", "size"))
# c37 の定義: G1 = log( 週平均 risk_bp )（log の平均ではない）。固定効果版は本レベルで risk_bp を乗法的に補正してから週平均。
tr["risk_bp_fe"] = np.exp(tr["lrb_fe"])
def wmean(mask, col, nmin=3):
    s = tr[mask].groupby("week")[col].agg(["mean", "size"]); s.loc[s["size"] < nmin, "mean"] = np.nan; return np.log(s["mean"])
gw["G1"] = np.log(tr.groupby("week")["risk_bp"].mean())
gw["G1_mlog"] = tr.groupby("week")["lrb"].mean()
gw["G1_fe"] = np.log(tr.groupby("week")["risk_bp_fe"].mean())
gw["G1_new7"] = wmean(~FL[(7, 0.5)], "risk_bp"); gw["G1_reu7"] = wmean(FL[(7, 0.5)], "risk_bp")
gw["G1_new7w"] = wmean(~FL[(7, 2.0)], "risk_bp"); gw["G1_new28"] = wmean(~FL[(28, 0.5)], "risk_bp"); gw["G1_new28w"] = wmean(~FL[(28, 2.0)], "risk_bp")
gw["G1_newall"] = wmean(~FL[(7, 0.5)] & ~same_wk, "risk_bp")
gw["ndist"] = tr.groupby("week").apply(n_distinct)
gw["nall"] = tr.groupby("week").size()
gw["valid"] = gw["n"].fillna(0) >= NMIN
gw["start"] = [p.start_time for p in gw.index]; gw["cutoff"] = gw["start"] - pd.Timedelta(days=1); gw["year"] = gw["start"].dt.year
gw["end"] = [p.end_time for p in gw.index]
tmp = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), gv.rename(columns={"date": "gdate"}), left_on="cutoff", right_on="gdate", direction="backward")
tmp2 = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), D[["date", "RVt", "RV5", "DR5", "RNGp"]].rename(columns={"date": "rdate"}), left_on="cutoff", right_on="rdate", direction="backward")
gw = gw.join(tmp.set_index("week")[["gvz", "gdate"]]).join(tmp2.set_index("week")[["RVt", "RV5", "DR5", "RNGp", "rdate"]])
assert (gw.loc[gw.valid, "gdate"] < gw.loc[gw.valid, "start"]).all() and (gw.loc[gw.valid, "rdate"] < gw.loc[gw.valid, "start"]).all(), "look-ahead"
# contemporaneous week range (unknown at week start; upper-bound control)
wsec = np.array([p.start_time.value // 10**9 for p in gw.index]); wend = np.array([p.end_time.value // 10**9 for p in gw.index])
a_ = np.searchsorted(TS, wsec); b_ = np.searchsorted(TS, wend)
HIn = np.where(flat, np.nan, HI); LOn = np.where(flat, np.nan, LO)
rc = np.full(len(gw), np.nan)
for k in range(len(gw)):
    if b_[k] - a_[k] > 100:
        h = np.nanmax(HIn[a_[k]:b_[k]]); l = np.nanmin(LOn[a_[k]:b_[k]]); rc[k] = (h - l) / C[b_[k] - 1] * 1e4
gw["RNGc"] = rc
for c_ in ("gvz", "RVt", "RV5", "DR5", "RNGp", "RNGc"): gw["l" + c_] = np.log(gw[c_])
say(f"- 週 {len(gw)}・有効 {int(gw.valid.sum())}・look-ahead assert OK・週内 distinct 壁水準 中央値 {gw.loc[gw.valid,'ndist'].median():.0f}（本数 中央値 {gw.loc[gw.valid,'nall'].median():.0f}）")
say()

# ---------- stats ----------
def pairs(v, lag=1):
    pos_ = np.array([(p - v.index[0]).n for p in v.index]); s = {p: k for k, p in enumerate(pos_)}
    ok = np.array([(p + lag) in s for p in pos_])
    ia = np.array([s[p] for p in pos_[ok]]); ib = np.array([s[p + lag] for p in pos_[ok]]); return ia, ib
def lag1(vals, ia, ib):
    a = vals[ia]; b = vals[ib]; ok = np.isfinite(a) & np.isfinite(b); a = a[ok]; b = b[ok]
    return float(np.corrcoef(a, b)[0, 1]) if len(a) > 4 else np.nan
def perm_p(vals, ia, ib, r1, nperm=NPERM):
    out = np.empty(nperm)
    for k in range(nperm): out[k] = lag1(rng.permutation(vals), ia, ib)
    return float((out >= r1).mean()), float(np.quantile(out, .95))
def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.column_stack(X) if isinstance(X, (list, tuple)) else np.asarray(X, float).reshape(len(y), -1)
    ok = np.isfinite(y) & np.isfinite(X).all(1); y = y[ok]; X = X[ok]; n = len(y)
    Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv; se = np.sqrt(np.diag(V))
    r2 = 1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, se, b / se, n, r2, u, ok
def resid(y, X):
    b, se, t, n, r2, u, ok = nw_ols(y, X); full = np.full(len(y), np.nan); full[ok] = u; return full, b, t, r2
def placebo_resid_r1(y, Xcols, v, ia, ib, shuffle_cols, npla=NPLA):
    yrs = v.year.to_numpy(); pl = np.empty(npla)
    for k in range(npla):
        idx = np.arange(len(v)).copy()
        for yy in np.unique(yrs):
            m = np.where(yrs == yy)[0]; idx[m] = rng.permutation(m)
        X = [v[c].to_numpy()[idx] if c in shuffle_cols else v[c].to_numpy() for c in Xcols]
        u, *_ = resid(y, X); pl[k] = lag1(u, ia, ib)
    return float(np.median(pl)), float(np.quantile(pl, .05)), float(np.quantile(pl, .95))

RES = {}
say("## R0 再現 ＋ R1 同一壁 ＋ R2 レンジ地平ボラ ＋ R5 構成（窓別）")
for wn, (y0, y1) in WIN.items():
    v = gw[gw.valid & (gw.year >= y0) & (gw.year <= y1)].copy(); ia, ib = pairs(v)
    RES[wn] = {}
    say(f"### {wn}: 有効週 {len(v)}・ペア {len(ia)}・G1_new7 有効週 {int(v.G1_new7.notna().sum())}・G1_reu7 {int(v.G1_reu7.notna().sum())}・再利用本の週平均割合 {100*(1 - tr[(tr.year>=y0)&(tr.year<=y1)].groupby('week')['reuse'].mean().mean()):.0f}% が新壁")
    say("| 系列 | 生 r1 | 置換 p | 残差 r1 (GVZ+RVt) | 比 | 残差 r1 (+RNGp+DR5) | 比 | R²(+) | β RNGp (t) | β DR5 (t) | 残差 r1 (RNGc 同時・上限) | 比 | プラセボ(+RNGp,DR5 行シャッフル) 中央値 [5,95] |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for col, lab in (("G1", "G1 全本（c37 再現・log 週平均）"), ("G1_mlog", "G1_mlog 週平均 log（参考・頑健版）"), ("G1_new7", "G1_new7 新壁のみ L7 tol0.5（R1 主）"), ("G1_new7w", "G1_new7w L7 tol2.0"), ("G1_new28", "G1_new28 L28 tol0.5"), ("G1_new28w", "G1_new28w L28 tol2.0"), ("G1_newall", "G1_newall L7 ∧ 同週内も除外"), ("G1_reu7", "G1_reu7 再利用本のみ"), ("G1_fe", "G1_fe jh×side×kind 固定効果除去（R5）"), ("lRNGp", "log RNGp 前 5 日レンジ（対照 a）"), ("lDR5", "log DR5 前 5 日 日次レンジ平均（対照 a）"), ("lRV5", "log RV5（対照 a）")):
        y = v[col].to_numpy(float)
        if not np.isfinite(y).any(): continue
        r_raw = lag1(y, ia, ib); p_raw, _ = perm_p(y, ia, ib, r_raw)
        u1, b1, t1, r21 = resid(y, [v.lgvz.to_numpy(), v.lRVt.to_numpy()]); r1 = lag1(u1, ia, ib)
        ctrl = col in ("lRNGp", "lDR5", "lRV5")
        X2 = [v.lgvz.to_numpy(), v.lRVt.to_numpy()] + ([] if ctrl else [v.lRNGp.to_numpy(), v.lDR5.to_numpy()])
        u2, b2, t2, r22 = resid(y, X2); r2_ = lag1(u2, ia, ib); p2, _ = perm_p(u2, ia, ib, r2_)
        if ctrl: b2 = np.r_[b2, np.nan, np.nan]; t2 = np.r_[t2, np.nan, np.nan]
        u3, b3, t3, r23 = resid(y, [v.lRNGc.to_numpy()]); r3 = lag1(u3, ia, ib)
        plm, pl5, pl95 = placebo_resid_r1(y, ["lgvz", "lRVt", "lRNGp", "lDR5"], v, ia, ib, {"lRNGp", "lDR5"}) if col in ("G1", "G1_new7") else (np.nan, np.nan, np.nan)
        RES[wn][col] = dict(r_raw=r_raw, p_raw=p_raw, r1=r1, r2=r2_, p2=p2, r3=r3, ratio1=r1 / r_raw, ratio2=r2_ / r_raw, ratio3=r3 / r_raw, r22=r22)
        say(f"| {lab} | **{r_raw:+.3f}** | {p_raw:.4f} | {r1:+.3f} | {r1/r_raw:+.2f} | **{r2_:+.3f}** (p {p2:.4f}) | {r2_/r_raw:+.2f} | {r22:.3f} | {b2[3]:+.3f} ({t2[3]:+.1f}) | {b2[4]:+.3f} ({t2[4]:+.1f}) | {r3:+.3f} | {r3/r_raw:+.2f} | {plm:+.3f} [{pl5:+.3f},{pl95:+.3f}] |")
    # lag profile
    y = v["G1"].to_numpy(float); u2, *_ = resid(y, [v.lgvz.to_numpy(), v.lRVt.to_numpy(), v.lRNGp.to_numpy(), v.lDR5.to_numpy()])
    yn = v["G1_new7"].to_numpy(float)
    prof = []
    for lg in (1, 2, 3, 4, 6, 8):
        ia2, ib2 = pairs(v, lg); prof.append(f"lag{lg}: 生 {lag1(y, ia2, ib2):+.2f}／残差(+) {lag1(u2, ia2, ib2):+.2f}／新壁 {lag1(yn, ia2, ib2):+.2f}")
    say("- lag プロファイル G1: " + "・".join(prof))
    # R4 regime: GVZ terciles (in-sample cuts)
    if wn == "在 2010-20": gcut = v.gvz.quantile([1 / 3, 2 / 3]).to_numpy()
    tier = np.digitize(v.gvz.to_numpy(), gcut)
    out = []
    for tname, tv in (("low", 0), ("mid", 1), ("high", 2)):
        m = (tier[ia] == tv) & (tier[ib] == tv)
        out.append(f"{tname} n{m.sum()} 生 {lag1(y, ia[m], ib[m]):+.2f}／新壁 {lag1(yn, ia[m], ib[m]):+.2f}")
    say("- R4 GVZ 三分位（両週同分位のペア・在カット）: " + "・".join(out))
    say()

# ---------- R3 splits ----------
say("## R3 別分割（G1: 生 r1／残差 c37 比／残差 +RNGp+DR5 比／新壁 L7 生 r1／新壁 残差(+) 比）")
def split_row(name, v):
    ia, ib = pairs(v); y = v.G1.to_numpy(float); yn = v.G1_new7.to_numpy(float)
    r_raw = lag1(y, ia, ib); u1, *_ = resid(y, [v.lgvz.to_numpy(), v.lRVt.to_numpy()]); u2, *_ = resid(y, [v.lgvz.to_numpy(), v.lRVt.to_numpy(), v.lRNGp.to_numpy(), v.lDR5.to_numpy()])
    rn = lag1(yn, ia, ib); un, *_ = resid(yn, [v.lgvz.to_numpy(), v.lRVt.to_numpy(), v.lRNGp.to_numpy(), v.lDR5.to_numpy()])
    say(f"| {name} | {len(v)} | {r_raw:+.3f} | {lag1(u1, ia, ib)/r_raw:+.2f} | {lag1(u2, ia, ib)/r_raw:+.2f} | {rn:+.3f} | {lag1(un, ia, ib)/rn if np.isfinite(rn) and rn else np.nan:+.2f} |")
say("| 分割 | 週 | 生 r1 | 比 c37 | 比 +RNG | 新壁 生 r1 | 新壁 比 +RNG |"); say("|---|---|---|---|---|---|---|")
for name, (y0, y1) in W4.items(): split_row(name, gw[gw.valid & (gw.year >= y0) & (gw.year <= y1)].copy())
split_row("偶数年", gw[gw.valid & (gw.year % 2 == 0)].copy()); split_row("奇数年", gw[gw.valid & (gw.year % 2 == 1)].copy())
say()

# ---------- judgment ----------
say("## 判定（docstring の規則）")
A = RES["在 2010-20"]; B = RES["外 2021-26H1"]
def rule(rin, pin, rout, pout, base_in, base_out):
    if rin < 0.5 * base_in and rout < 0.5 * base_out: return "broken"
    if rin >= 0.5 * base_in and rout >= 0.5 * base_out and pin < 0.025 and pout < 0.025: return "survived"
    return "inconclusive"
rep = f"R0 再現: 生 r1 在 {A['G1']['r_raw']:+.3f} (c37 +0.589)／外 {B['G1']['r_raw']:+.3f} (+0.599)・残差 在 {A['G1']['r1']:+.3f} (+0.553)／外 {B['G1']['r1']:+.3f} (+0.501) → " + ("一致" if abs(A['G1']['r_raw'] - .589) < .005 and abs(B['G1']['r1'] - .501) < .005 else "不一致")
say("- " + rep)
v1 = rule(A["G1_new7"]["r_raw"], A["G1_new7"]["p_raw"], B["G1_new7"]["r_raw"], B["G1_new7"]["p_raw"], C37["在 2010-20"][0], C37["外 2021-26H1"][0])
say(f"- R1 同一壁（G1_new7 生 r1 vs 0.5×c37 生）: 在 {A['G1_new7']['r_raw']:+.3f} (p {A['G1_new7']['p_raw']:.4f}・比 {A['G1_new7']['r_raw']/.589:+.2f})／外 {B['G1_new7']['r_raw']:+.3f} (p {B['G1_new7']['p_raw']:.4f}・比 {B['G1_new7']['r_raw']/.599:+.2f}) → **{v1}**；tol2.0 在 {A['G1_new7w']['r_raw']:+.3f}／外 {B['G1_new7w']['r_raw']:+.3f}・L28 在 {A['G1_new28']['r_raw']:+.3f}／外 {B['G1_new28']['r_raw']:+.3f}・同週内も除外 在 {A['G1_newall']['r_raw']:+.3f}／外 {B['G1_newall']['r_raw']:+.3f}・再利用本のみ 在 {A['G1_reu7']['r_raw']:+.3f}／外 {B['G1_reu7']['r_raw']:+.3f}")
v2 = rule(A["G1"]["r2"], A["G1"]["p2"], B["G1"]["r2"], B["G1"]["p2"], A["G1"]["r_raw"], B["G1"]["r_raw"])
say(f"- R2 レンジ地平ボラ（G1 残差 +RNGp+DR5 vs 0.5×生）: 在 {A['G1']['r2']:+.3f} (比 {A['G1']['ratio2']:+.2f}・p {A['G1']['p2']:.4f})／外 {B['G1']['r2']:+.3f} (比 {B['G1']['ratio2']:+.2f}・p {B['G1']['p2']:.4f}) → **{v2}**；同時週レンジ RNGc 上限 比 在 {A['G1']['ratio3']:+.2f}／外 {B['G1']['ratio3']:+.2f}")
say(f"- R2 対照 (a) 数日レンジ型ボラ自身の持続は GVZ+RVt で消えるか: log RNGp 比 在 {A['lRNGp']['ratio1']:+.2f}／外 {B['lRNGp']['ratio1']:+.2f}・log DR5 比 在 {A['lDR5']['ratio1']:+.2f}／外 {B['lDR5']['ratio1']:+.2f}・log RV5 比 在 {A['lRV5']['ratio1']:+.2f}／外 {B['lRV5']['ratio1']:+.2f}（c37 の ATR14 対照は 0.18／0.38）")
v5 = rule(A["G1_fe"]["r_raw"], A["G1_fe"]["p_raw"], B["G1_fe"]["r_raw"], B["G1_fe"]["p_raw"], .589, .599)
say(f"- R5 構成（jh×side×kind 固定効果除去 G1_fe 生 r1）: 在 {A['G1_fe']['r_raw']:+.3f}／外 {B['G1_fe']['r_raw']:+.3f} → **{v5}**")
v2n = rule(A["G1_new7"]["r2"], A["G1_new7"]["p2"], B["G1_new7"]["r2"], B["G1_new7"]["p2"], A["G1_new7"]["r_raw"], B["G1_new7"]["r_raw"])
say(f"- R1×R2 新壁のみ ∧ レンジ地平残差（H_B の規則を新壁に再適用）: 在 {A['G1_new7']['r2']:+.3f} (比 {A['G1_new7']['ratio2']:+.2f})／外 {B['G1_new7']['r2']:+.3f} (比 {B['G1_new7']['ratio2']:+.2f}) → **{v2n}**")
overall = "broken" if "broken" in (v1, v2) else ("survived" if (v1, v2, v5) == ("survived",) * 3 else "inconclusive")
say(f"- **総合 H_B: {overall}**（R1 {v1}・R2 {v2}・R5 {v5}）")
say()
say(f"所要 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
