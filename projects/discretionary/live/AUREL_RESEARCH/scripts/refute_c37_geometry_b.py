# -*- coding: utf-8 -*-
"""
[REFUTE c37 補足 b 2026-11-11] 主スクリプト（refute_c37_geometry.py）の結果を見てから立てた 2 つの追加攻撃。規則は本 docstring に先に書く。
R6 価格水準の床（MIN_SL_W = 3.0 USD）: scan は risk を 3.0 USD で下から切る（在 29%／外 21%／近年 14% の本が risk==3.0）。
  床の本の risk_bp = 3e4/P は価格の逆数＝週次で r≈1 の RW。c37 は risk_bp で価格水準を除いたつもりだが USD 床が 1/P を再導入する。
  検査: (a) G1 を [log GVZ, log RVt, log P̄_w]（P̄_w = 週平均建玉価格・建玉時既知）で残差化した r1 と比／プラセボ = log P̄ の行を年内シャッフル 200 回。
        (b) G1_nf = 床でない本（risk > 3.0）だけの log 週平均 risk_bp の生 r1 と GVZ+RVt 残差 r1。(c) G1_fl = 床の本だけ（＝log(3e4/P̄)）の r1（参考・≈1 のはず）。
        (d) risk_bp の代わりに risk/atr14（価格水準を含まない）の G4 を同様に見る（c37 の G4 は生 0.635／0.728・残差 0.297／0.512 で既に印字済み・再掲のみ）。
  判定（主）: 【broken】= 在 ∧ 外 とも (a) の残差 r1 < 0.5 × 生 r1 ∧ プラセボ中央値 ≥ 0.5 × 生（＝価格水準そのものが持続を担ぐ）
              または 在 ∧ 外 とも (b) G1_nf の生 r1 < 0.5 × c37 生 r1（0.589／0.599）。
              【survived】= (a) 比 ≥0.5 ∧ (b) 比 ≥0.5 ∧ p<0.025 在外とも。他 inconclusive。
R7 R1 の減衰校正: G1_new7 は週あたり本数が減る（新壁 46〜62%）ので r1 は本レベル雑音で減衰する。各週から新壁本と同数をランダム抽出した
  G1_rand の r1（200 回・中央値・5〜95% 点）を印字。G1_new7 の r1 が 5% 点未満なら「同一壁の除外は減衰以上に持続を削る（再利用が持続の一部を担ぐ）」、
  5〜95% 内なら「新壁と全本の差は減衰で説明＝再利用は持続を担がない」。記述（R1 の読みを変えるだけ・規則は変えない）。
seed 20261111。入力は主スクリプトと同じ。scan 無し・MT5 無し・外部通信無し。
"""
import os, time, json
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c37_geometry_b.md")
NY = "America/New_York"
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c37 補足 b] 価格床 1/P の人工物・新壁 r1 の減衰校正 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c37_geometry_b.py)")
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
C37 = {"在 2010-20": 0.589, "外 2021-26H1": 0.599, "近年 2024-26H1": 0.646}
H = 21; NMIN = 5; NPERM = 2000; NPLA = 200; NWLAG = 4

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
MINW = d["frozen"]["MIN_SL_W"]
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None); tr["week"] = tr["ts"].dt.to_period("W-SUN")
tr["dec"] = tr["exit"].isin(["SL", "TP"])
zo = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); TS = zo["ts"].astype(np.int64); C = zo["close"].astype(float); NB = len(TS)
et = tr["entry_time"].to_numpy(np.int64); ie = np.clip(np.searchsorted(TS, et), 0, NB - 1)
pos = np.clip(np.searchsorted(TS, et - 300), 0, NB - 1); tr["P"] = C[pos]
sgn = np.where(tr["side"].to_numpy() == "BUY", 1.0, -1.0); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); x0 = tr["x0"].to_numpy(float)
entry = C[ie] - sgn * x0 * risk; tr["SL"] = entry - sgn * risk; tr["TP"] = entry + sgn * bb * risk
tr["risk_bp"] = tr["risk"] / tr["P"] * 1e4; tr["floor"] = tr["risk"] <= MINW + 1e-9
tr["risk_atr"] = np.where(tr["atr"] > 0, tr["risk"] / tr["atr"].replace(0, np.nan), np.nan)
say(f"- 本 {len(tr)}・MIN_SL_W {MINW}・床の本: 在 {100*tr.floor[tr.year<=2020].mean():.1f}%／外 {100*tr.floor[tr.year>=2021].mean():.1f}%／近年 {100*tr.floor[tr.year>=2024].mean():.1f}%")

# session RV & GVZ (c37 定義)
lc = np.log(C); r = np.zeros(NB); r[1:] = np.diff(lc); flat = r == 0.0
dt_ny = pd.to_datetime(TS, unit="s", utc=True).tz_convert(NY); sess = dt_ny + pd.Timedelta(hours=6)
S = (sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy())
df = pd.DataFrame({"s": S, "r2": r ** 2, "nf": (~flat).astype(np.int32)}); g = df.groupby("s", sort=True)
D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum()}); D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d")
D = D[(D["date"].dt.weekday <= 4) & (D["nf"] >= 100)].reset_index(drop=True)
cs = np.concatenate([[0.0], np.cumsum(D["rv"].to_numpy())]); i = np.arange(len(D)); okt = i - H + 1 >= 0
RVt = np.full(len(D), np.nan); RVt[okt] = 100 * np.sqrt(252.0 / H * (cs[i[okt] + 1] - cs[i[okt] - H + 1])); D["RVt"] = RVt
gv = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"), na_values="."); gv.columns = ["date", "gvz"]; gv["date"] = pd.to_datetime(gv["date"]); gv = gv.dropna().sort_values("date")

# same-wall reuse (L7 tol0.5) as in main script
tr = tr.sort_values("entry_time").reset_index(drop=True)
etv = tr["entry_time"].to_numpy(np.int64); SLv = tr["SL"].to_numpy(); TPv = tr["TP"].to_numpy()
wk_start = np.array([p.start_time.value // 10**9 for p in tr["week"]], dtype=np.int64)
lo_t = wk_start - 7 * 86400; a = np.searchsorted(etv, lo_t, side="left"); b = np.searchsorted(etv, wk_start, side="left")
reuse = np.zeros(len(tr), bool)
for j in range(len(tr)):
    if b[j] <= a[j]: continue
    lv = np.concatenate([SLv[a[j]:b[j]], TPv[a[j]:b[j]]])
    if np.abs(lv - SLv[j]).min() <= 0.5 or np.abs(lv - TPv[j]).min() <= 0.5: reuse[j] = True
tr["reuse"] = reuse

gw = tr[tr.dec].groupby("week").agg(n=("dec", "size"))
def wmean(mask, col, nmin=3, log=True):
    s = tr[mask].groupby("week")[col].agg(["mean", "size"]); s.loc[s["size"] < nmin, "mean"] = np.nan; return np.log(s["mean"]) if log else s["mean"]
gw["G1"] = np.log(tr.groupby("week")["risk_bp"].mean()); gw["lP"] = np.log(tr.groupby("week")["P"].mean())
gw["G1_nf"] = wmean(~tr.floor, "risk_bp"); gw["G1_fl"] = wmean(tr.floor, "risk_bp"); gw["G4"] = np.log(tr.groupby("week")["risk_atr"].mean())
gw["G1_new7"] = wmean(~reuse, "risk_bp"); gw["n_new7"] = tr[~reuse].groupby("week").size(); gw["nall"] = tr.groupby("week").size()
gw["fl_share"] = tr.groupby("week")["floor"].mean()
gw["valid"] = gw["n"].fillna(0) >= NMIN
gw["start"] = [p.start_time for p in gw.index]; gw["cutoff"] = gw["start"] - pd.Timedelta(days=1); gw["year"] = gw["start"].dt.year
tmp = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), gv.rename(columns={"date": "gdate"}), left_on="cutoff", right_on="gdate", direction="backward")
tmp2 = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), D[["date", "RVt"]].rename(columns={"date": "rdate"}), left_on="cutoff", right_on="rdate", direction="backward")
gw = gw.join(tmp.set_index("week")[["gvz"]]).join(tmp2.set_index("week")[["RVt"]]); gw["lgvz"] = np.log(gw.gvz); gw["lRVt"] = np.log(gw.RVt)

def pairs(v, lag=1):
    pos_ = np.array([(p - v.index[0]).n for p in v.index]); s = {p: k for k, p in enumerate(pos_)}
    ok = np.array([(p + lag) in s for p in pos_]); return np.array([s[p] for p in pos_[ok]]), np.array([s[p + lag] for p in pos_[ok]])
def lag1(vals, ia, ib):
    a_ = vals[ia]; b_ = vals[ib]; ok = np.isfinite(a_) & np.isfinite(b_); a_ = a_[ok]; b_ = b_[ok]
    return float(np.corrcoef(a_, b_)[0, 1]) if len(a_) > 4 else np.nan
def perm_p(vals, ia, ib, r1, nperm=NPERM):
    out = np.empty(nperm)
    for k in range(nperm): out[k] = lag1(rng.permutation(vals), ia, ib)
    return float((out >= r1).mean())
def resid(y, X):
    y = np.asarray(y, float); X = np.column_stack(X); ok = np.isfinite(y) & np.isfinite(X).all(1)
    Z = np.column_stack([np.ones(ok.sum()), X[ok]]); bcoef = np.linalg.lstsq(Z, y[ok], rcond=None)[0]
    full = np.full(len(y), np.nan); full[ok] = y[ok] - Z @ bcoef
    r2 = 1 - ((y[ok] - Z @ bcoef) ** 2).sum() / ((y[ok] - y[ok].mean()) ** 2).sum(); return full, bcoef, r2

RES = {}
say("\n## R6 価格床 1/P（窓別）")
say("| 窓 | 床 share 週平均 | G1 生 r1 | 残差 (GVZ,RVt) | 残差 (GVZ,RVt,log P̄) r1 | 比 | R² | プラセボ(log P̄ 年内シャッフル) 中央値 [5,95] | log P̄ 自身 r1 | G1_nf 生 r1 (p) | 比 vs c37 | G1_nf 残差(GVZ,RVt) | 比 | G1_fl 生 r1 | G4 risk/atr 生 r1 | G4 残差(GVZ,RVt) |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for wn, (y0, y1) in WIN.items():
    v = gw[gw.valid & (gw.year >= y0) & (gw.year <= y1)].copy(); ia, ib = pairs(v)
    y = v.G1.to_numpy(float); r_raw = lag1(y, ia, ib)
    u1, _, _ = resid(y, [v.lgvz.to_numpy(), v.lRVt.to_numpy()]); r1 = lag1(u1, ia, ib)
    uP, bP, r2P = resid(y, [v.lgvz.to_numpy(), v.lRVt.to_numpy(), v.lP.to_numpy()]); rP = lag1(uP, ia, ib)
    yrs = v.year.to_numpy(); pl = np.empty(NPLA)
    for k in range(NPLA):
        idx = np.arange(len(v)).copy()
        for yy in np.unique(yrs):
            m = np.where(yrs == yy)[0]; idx[m] = rng.permutation(m)
        u_, _, _ = resid(y, [v.lgvz.to_numpy(), v.lRVt.to_numpy(), v.lP.to_numpy()[idx]]); pl[k] = lag1(u_, ia, ib)
    ynf = v.G1_nf.to_numpy(float); rnf = lag1(ynf, ia, ib); pnf = perm_p(ynf, ia, ib, rnf)
    unf, _, _ = resid(ynf, [v.lgvz.to_numpy(), v.lRVt.to_numpy()]); rnf1 = lag1(unf, ia, ib)
    yfl = v.G1_fl.to_numpy(float); rfl = lag1(yfl, ia, ib)
    y4 = v.G4.to_numpy(float); r4 = lag1(y4, ia, ib); u4, _, _ = resid(y4, [v.lgvz.to_numpy(), v.lRVt.to_numpy()]); r41 = lag1(u4, ia, ib)
    RES[wn] = dict(r_raw=r_raw, rP=rP, plm=float(np.median(pl)), rnf=rnf, pnf=pnf, rnf1=rnf1)
    say(f"| {wn} | {100*v.fl_share.mean():.0f}% | {r_raw:+.3f} | {r1:+.3f} | **{rP:+.3f}** | {rP/r_raw:+.2f} | {r2P:.3f} | {np.median(pl):+.3f} [{np.quantile(pl,.05):+.3f},{np.quantile(pl,.95):+.3f}] | {lag1(v.lP.to_numpy(float), ia, ib):+.3f} | **{rnf:+.3f}** ({pnf:.4f}) | {rnf/C37[wn]:+.2f} | {rnf1:+.3f} | {rnf1/rnf:+.2f} | {rfl:+.3f} | {r4:+.3f} | {r41:+.3f} |")
    # lag profile of G1_nf
    say(f"  - {wn} G1_nf lag プロファイル: " + "・".join(f"lag{lg} {lag1(ynf, *pairs(v, lg)):+.2f}" for lg in (1, 2, 4, 8)) + f"；床本 share と G1 の週次相関 {np.corrcoef(v.fl_share, y)[0,1]:+.2f}")

say("\n## R7 R1 の減衰校正（各週から新壁本数と同数をランダム抽出した G1_rand の r1・200 回）")
say("| 窓 | 新壁 本/週 中央値 | 全本 | G1_new7 r1 | G1_rand 中央値 [5,95] | 判定 |"); say("|---|---|---|---|---|---|")
tw = tr.groupby("week").indices
rb = tr["risk_bp"].to_numpy(); weeks = list(gw.index)
for wn, (y0, y1) in WIN.items():
    v = gw[gw.valid & (gw.year >= y0) & (gw.year <= y1)].copy(); ia, ib = pairs(v)
    rn = lag1(v.G1_new7.to_numpy(float), ia, ib)
    nn = v.n_new7.fillna(0).to_numpy(int); out = np.empty(NPLA)
    widx = [tw.get(w, np.array([], int)) for w in v.index]
    for k in range(NPLA):
        gr = np.full(len(v), np.nan)
        for q in range(len(v)):
            if nn[q] >= 3 and len(widx[q]) >= nn[q]:
                gr[q] = np.log(rb[rng.choice(widx[q], nn[q], replace=False)].mean())
        out[k] = lag1(gr, ia, ib)
    q5, q50, q95 = np.quantile(out, [.05, .5, .95])
    vd = "再利用が持続の一部を担ぐ（新壁 r1 < 5% 点）" if rn < q5 else "差は減衰で説明（再利用は担がない）"
    RES[wn].update(rn=rn, rq5=q5, rq50=q50)
    say(f"| {wn} | {np.median(nn[nn>0]):.0f} | {v.nall.median():.0f} | **{rn:+.3f}** | {q50:+.3f} [{q5:+.3f},{q95:+.3f}] | {vd} |")

say("\n## 判定（docstring の規則）")
A = RES["在 2010-20"]; B = RES["外 2021-26H1"]
brkA = (A["rP"] < 0.5 * A["r_raw"] and A["plm"] >= 0.5 * A["r_raw"]) and (B["rP"] < 0.5 * B["r_raw"] and B["plm"] >= 0.5 * B["r_raw"])
brkB = A["rnf"] < 0.5 * 0.589 and B["rnf"] < 0.5 * 0.599
surv = (A["rP"] >= 0.5 * A["r_raw"]) and (B["rP"] >= 0.5 * B["r_raw"]) and (A["rnf"] >= 0.5 * 0.589) and (B["rnf"] >= 0.5 * 0.599) and A["pnf"] < 0.025 and B["pnf"] < 0.025
v6 = "broken" if (brkA or brkB) else ("survived" if surv else "inconclusive")
say(f"- R6 価格床: (a) log P̄ 残差 比 在 {A['rP']/A['r_raw']:+.2f}／外 {B['rP']/B['r_raw']:+.2f}（プラセボ中央値 在 {A['plm']:+.3f}／外 {B['plm']:+.3f}）；(b) 床でない本のみ G1_nf 生 r1 在 {A['rnf']:+.3f} (比 {A['rnf']/.589:+.2f}・p {A['pnf']:.4f})／外 {B['rnf']:+.3f} (比 {B['rnf']/.599:+.2f}・p {B['pnf']:.4f}) → **{v6}**")
say(f"- R7 減衰校正: 在 新壁 {A['rn']:+.3f} vs ランダム同数 {A['rq50']:+.3f} [5% {A['rq5']:+.3f}]／外 {B['rn']:+.3f} vs {B['rq50']:+.3f} [5% {B['rq5']:+.3f}]")
say(f"\n所要 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
