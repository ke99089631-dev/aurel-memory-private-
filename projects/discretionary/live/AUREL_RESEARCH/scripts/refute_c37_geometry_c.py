# -*- coding: utf-8 -*-
"""
[REFUTE c37 補足 c 2026-11-11] 補足 b の R6 (a)（在で log P̄ 残差化が G1 の持続を 0.589 → 0.089 に落とす・プラセボ 0.222）を受けた記述。
問い: 壁幅は USD で粘る（価格に対し弾性 ≈0）のか。そうなら risk_bp = risk_USD/P の持続は 1/P（RW）の持続を機械的に継承する。
印字（窓別・独立 4 窓）: (1) 週次 log risk_USD 平均の生 r1 と、log P̄ への弾性 β（NW lag4）と R²。(2) log risk_USD を log P̄ で残差化した r1。
(3) G1（bp）を 既知フルセット [log GVZ, log RVt, log RNGp, log DR5, log P̄] で残差化した r1 と比。(4) 同じく G4 = log(risk/atr14)。
(5) 床でない本のみ版（G1_nf）の (3)。規則なし（記述）。seed 20261111。
"""
import os, time, json
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c37_geometry_c.md"); NY = "America/New_York"; rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c37 補足 c] 壁幅の USD 粘着と 1/P の継承 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c37_geometry_c.py)")
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026), "2010-14": (2010, 2014), "2015-20": (2015, 2020), "2021-23": (2021, 2023), "2024-26H1": (2024, 2026)}
H = 21; NMIN = 5; NWLAG = 4
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); MINW = d["frozen"]["MIN_SL_W"]
tr = pd.DataFrame(d["trades"]); tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None); tr["week"] = tr["ts"].dt.to_period("W-SUN"); tr["dec"] = tr["exit"].isin(["SL", "TP"])
zo = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); TS = zo["ts"].astype(np.int64); HI = zo["high"].astype(float); LO = zo["low"].astype(float); C = zo["close"].astype(float); NB = len(TS)
et = tr["entry_time"].to_numpy(np.int64); pos = np.clip(np.searchsorted(TS, et - 300), 0, NB - 1); tr["P"] = C[pos]
tr["risk_bp"] = tr["risk"] / tr["P"] * 1e4; tr["floor"] = tr["risk"] <= MINW + 1e-9; tr["risk_atr"] = np.where(tr["atr"] > 0, tr["risk"] / tr["atr"].replace(0, np.nan), np.nan)
lc = np.log(C); r = np.zeros(NB); r[1:] = np.diff(lc); flat = r == 0.0
dt_ny = pd.to_datetime(TS, unit="s", utc=True).tz_convert(NY); sess = dt_ny + pd.Timedelta(hours=6)
S = (sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy())
df = pd.DataFrame({"s": S, "r2": r ** 2, "nf": (~flat).astype(np.int32), "hi": np.where(flat, np.nan, HI), "lo": np.where(flat, np.nan, LO), "c": C}); g = df.groupby("s", sort=True)
D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum(), "hi": g["hi"].max(), "lo": g["lo"].min(), "c": g["c"].last()}); D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d")
D = D[(D["date"].dt.weekday <= 4) & (D["nf"] >= 100)].reset_index(drop=True); D["drng_bp"] = (D["hi"] - D["lo"]) / D["c"] * 1e4
cs = np.concatenate([[0.0], np.cumsum(D["rv"].to_numpy())]); i = np.arange(len(D)); okt = i - H + 1 >= 0
RVt = np.full(len(D), np.nan); RVt[okt] = 100 * np.sqrt(252.0 / H * (cs[i[okt] + 1] - cs[i[okt] - H + 1])); D["RVt"] = RVt
D["DR5"] = D["drng_bp"].rolling(5).mean(); D["RNGp"] = (D["hi"].rolling(5).max() - D["lo"].rolling(5).min()) / D["c"] * 1e4
gv = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"), na_values="."); gv.columns = ["date", "gvz"]; gv["date"] = pd.to_datetime(gv["date"]); gv = gv.dropna().sort_values("date")
gw = tr[tr.dec].groupby("week").agg(n=("dec", "size"))
gw["G1"] = np.log(tr.groupby("week")["risk_bp"].mean()); gw["lU"] = np.log(tr.groupby("week")["risk"].mean()); gw["lP"] = np.log(tr.groupby("week")["P"].mean()); gw["G4"] = np.log(tr.groupby("week")["risk_atr"].mean())
s_ = tr[~tr.floor].groupby("week")["risk_bp"].agg(["mean", "size"]); s_.loc[s_["size"] < 3, "mean"] = np.nan; gw["G1_nf"] = np.log(s_["mean"])
gw["valid"] = gw["n"].fillna(0) >= NMIN; gw["start"] = [p.start_time for p in gw.index]; gw["cutoff"] = gw["start"] - pd.Timedelta(days=1); gw["year"] = gw["start"].dt.year
tmp = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), gv.rename(columns={"date": "gdate"}), left_on="cutoff", right_on="gdate", direction="backward")
tmp2 = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), D[["date", "RVt", "DR5", "RNGp"]].rename(columns={"date": "rdate"}), left_on="cutoff", right_on="rdate", direction="backward")
gw = gw.join(tmp.set_index("week")[["gvz"]]).join(tmp2.set_index("week")[["RVt", "DR5", "RNGp"]])
for c_ in ("gvz", "RVt", "DR5", "RNGp"): gw["l" + c_] = np.log(gw[c_])
def pairs(v, lag=1):
    pos_ = np.array([(p - v.index[0]).n for p in v.index]); s = {p: k for k, p in enumerate(pos_)}; ok = np.array([(p + lag) in s for p in pos_])
    return np.array([s[p] for p in pos_[ok]]), np.array([s[p + lag] for p in pos_[ok]])
def lag1(vals, ia, ib):
    a_ = vals[ia]; b_ = vals[ib]; ok = np.isfinite(a_) & np.isfinite(b_); a_ = a_[ok]; b_ = b_[ok]; return float(np.corrcoef(a_, b_)[0, 1]) if len(a_) > 4 else np.nan
def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.column_stack(X); ok = np.isfinite(y) & np.isfinite(X).all(1); y = y[ok]; X = X[ok]; n = len(y)
    Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z); b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv; se = np.sqrt(np.diag(V)); r2 = 1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum()
    full = np.full(len(ok), np.nan); full[ok] = u; return b, b / se, r2, full
say("| 窓 | 週 | log risk_USD 生 r1 | 弾性 β(log U on log P̄) (t) | R² | log U 残差(log P̄) r1 | 比 | G1 生 r1 | G1 残差(フル既知+log P̄) r1 | 比 | G1_nf 残差(フル+log P̄) r1 | 比 vs G1_nf 生 | G4 生 r1 | G4 残差(フル+log P̄) | 比 |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for wn, (y0, y1) in WIN.items():
    v = gw[gw.valid & (gw.year >= y0) & (gw.year <= y1)].copy(); ia, ib = pairs(v)
    yU = v.lU.to_numpy(float); rU = lag1(yU, ia, ib); bU, tU, r2U, uU = nw_ols(yU, [v.lP.to_numpy()]); rU1 = lag1(uU, ia, ib)
    FULL = [v.lgvz.to_numpy(), v.lRVt.to_numpy(), v.lRNGp.to_numpy(), v.lDR5.to_numpy(), v.lP.to_numpy()]
    y1_ = v.G1.to_numpy(float); r1 = lag1(y1_, ia, ib); _, _, _, u1 = nw_ols(y1_, FULL); r1f = lag1(u1, ia, ib)
    ynf = v.G1_nf.to_numpy(float); rnf = lag1(ynf, ia, ib); _, _, _, unf = nw_ols(ynf, FULL); rnff = lag1(unf, ia, ib)
    y4 = v.G4.to_numpy(float); r4 = lag1(y4, ia, ib); _, _, _, u4 = nw_ols(y4, FULL); r4f = lag1(u4, ia, ib)
    say(f"| {wn} | {len(v)} | {rU:+.3f} | {bU[1]:+.2f} ({tU[1]:+.1f}) | {r2U:.2f} | {rU1:+.3f} | {rU1/rU:+.2f} | {r1:+.3f} | **{r1f:+.3f}** | {r1f/r1:+.2f} | {rnff:+.3f} | {rnff/rnf:+.2f} | {r4:+.3f} | **{r4f:+.3f}** | {r4f/r4:+.2f} |")
    if wn in ("在 2010-20", "外 2021-26H1", "近年 2024-26H1"):
        # 置換 p（残差の暦位置シャッフル 2000）と プラセボ（5 ドライバの行を年内で同時シャッフル 200）
        perm = np.array([lag1(rng.permutation(u1), ia, ib) for _ in range(2000)]); pp = float((perm >= r1f).mean())
        yrs = v.year.to_numpy(); pl = np.empty(200)
        for k in range(200):
            idx = np.arange(len(v)).copy()
            for yy in np.unique(yrs):
                m = np.where(yrs == yy)[0]; idx[m] = rng.permutation(m)
            _, _, _, u_ = nw_ols(y1_, [x[idx] for x in FULL]); pl[k] = lag1(u_, ia, ib)
        say(f"  - {wn}: G1 フル残差 r1 {r1f:+.3f} の置換 p {pp:.4f}（95% 点 {np.quantile(perm,.95):+.3f}）；プラセボ（5 ドライバ行を年内同時シャッフル）残差 r1 中央値 {np.median(pl):+.3f} [{np.quantile(pl,.05):+.3f},{np.quantile(pl,.95):+.3f}] ＝ 年固定効果だけで残る持続の目安")
say(f"\n所要 {time.time()-T0:.1f} s"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
