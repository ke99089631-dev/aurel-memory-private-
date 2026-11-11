# -*- coding: utf-8 -*-
"""
[cycle37 研究レーン 2026-11-11] 【深化・レジーム／幾何の持続の起源】
壁→壁(再加速)の「幾何の遅い状態」（cycle27: 週次 b̄・q̄・risk USD の lag1 r 在 +0.47〜+0.48／外 +0.49〜+0.81）は、
週初に既知の期待ボラ（CBOE GVZ・cycle34 で「効率的なボラ予測」と判明）と直近実現ボラ（RV_trail 21 日）で説明し尽くされるか。
＝ 壁の配置（risk・b）の週〜月の持続は「ボラの持続の別名」か、それともボラと独立な「壁の配置の状態」を持つか。
backlog cycle34 (d)「GVZ 既知が週の幾何を予測するか＝壁の間隔が期待ボラに追随しているか」の実行。
AI らしい角度: 2 つの既知結果（c27 の持続・c34 の GVZ 効率性）を結合して「持続の起源」を 1 本の残差自己相関で判定する。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/refute_c4_scan_paths_2010_2026.json（19404 本・entry_time/risk/b/R/exit/atr）・data/macro/XAU_m5_close.npz（建玉価格 P と
  セッション日次 RV・c34 と同じ定義: セッション日 = (ET+6h) 暦日・RV_d = Σ(Δlog close)²・有効日 月〜金 ∧ 非 flat ≥100 本）・
  data/macro/GVZCLS.csv（FRED・16:15 ET 確定）。既存キャッシュのみ・scan 無し・M5 読込なし・MT5 無し・外部通信無し。
週: c27 と同じ UTC W-SUN（月曜 00:00 UTC 始まり）・有効週 = 決着本 n≥5。窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（週の開始年・D2 窓別）。
週初に既知の情報（look-ahead なし）: GVZ_known_w = 日付 ≤ 週初前日（＝前週金曜）の最後の GVZ、RVt_w = 同じ締めまでの 21 有効日 実現ボラ（年率 %）。
  いずれも週の最初の建玉（月曜 00:00 UTC 以降）より前に確定（金曜 17:00 ET = 金曜 21/22 時 UTC）。
週の幾何（建玉時に既知の量の週平均）: G1 = log(risk_bp)（risk USD ÷ 建玉価格 ×1e4・主）／G2 = b̄（TP 距離 R・副）／
  G3 = q̄（RW 基準到達率・記述）／G4 = log(risk/atr14)（ボラ正規化した配置・記述）／G5 = log(atr_bp)（建玉時 ATR14・同時期の局所ボラ・対照）。
統計: 各窓内で G_w = α + β1·log GVZ_known_w + β2·log RVt_w の OLS（NW lag 4 t・R²）→ 残差 u_w。
  lag1 r は c27 と同じ「連続する有効週ペア」の Pearson r。置換帰無 = 有効週の値を暦位置間でシャッフル 2000 回（片側 p・95% 点 = 検出閾値）。
判定（主 = G1・副 = G2・Bonferroni(2)・在で決め外で確認）:
  H_A「幾何の持続は期待ボラの別名」PASS = 在 ∧ 外 とも 残差 lag1 r(G) < 0.5 × 生 lag1 r(G) ∧ 残差 r の置換 p ≥ 0.025。
  H_B「幾何はボラと独立な状態を持つ」PASS = 在 ∧ 外 とも 残差 lag1 r ≥ 0.5 × 生 r ∧ 置換 p < 0.025。
  どちらでもなければ「部分（ボラが持続の X% を担ぐ）」として 1 − r_res/r_raw を在/外で印字。
対照: (i) プラセボ = GVZ・RVt の行を**年内で週間シャッフル**（水準分布を保ち整列を壊す）200 回 → 残差 r1 の中央値・5〜95% 点が生 r1 と同水準なら
  「残差化そのものは持続を壊さない」（校正）。(ii) 同時期対照 = G5（同週の建玉時 ATR）で残差化した r1（既知でない・上限の参考）。
  (iii) 陽性対照（方法が持続を検出できること）= 生 r1 の置換 p が在で <0.001（c27 の再現）。
T4（記述）: G_w = α + φ·G_{w−1} + γ·log GVZ_known_w の γ の NW t（期待ボラは幾何の自己ラグを超えて翌週の配置を予測するか）。
T3（ゲート ㉛・本番接続）: 週次 x̄_w on log GVZ_known_w の β・t（在）と、本レベル（FRED 規則 avail=(entry_JST−7h).date−1・asof ≤7 日）の
  GVZ_known 在三分位 top/bottom の Δμ（Welch t）・Δx（pp）・x0 look-ahead 対照。在 max|Δμ| <0.048R → 「決着不能・外は走らせない」。
事前の最重大反証: (1) risk_bp と GVZ はともに価格水準・ボラ水準に乗る → 残差 r1 が落ちても「ボラが説明」でなく「共通の低周波トレンド
  （2010-26 の金価格 3 倍）」の除去かもしれない → 窓別（D2）＋ 年内シャッフル プラセボで低周波は保存して判定する。(2) 週あたり建玉 20〜30 本で
  b̄・q̄ の週平均は本レベル雑音を含む（c27: 名目 se 中央値 ≈ 0.02〜0.03）→ 生 r1 自体が減衰しており比 r_res/r_raw は雑音に鈍感だが絶対値は低め。
  (3) GVZ は GLD（米国時間）30 暦日 IV・RVt は 24h bid 5 分 → 定義差は c34 で符号頑健と確認済み。(4) 残差化は窓内 OLS（in-sample の β）＝
  「説明力の上限」側（前向き推定ではない）。H_A の PASS は「説明できる」の必要条件であり、前向きの予測力は T4 で別に見る。
  (5) 本数の週 lag1（c27 +0.42〜+0.62）は GVZ と同方向のはず＝記述で印字。
昇格候補・入口/出口規則の提案ではない（幾何＝レジーム記述・メタ）。seed 20261111。
"""
import os, time, json, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c37_geometry_vs_iv_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle37] 幾何の遅い状態は期待ボラ（GVZ）の別名か — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c37_geometry_vs_iv.py)")

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
H = 21; NMIN = 5; NPERM = 2000; NPLA = 200; NWLAG = 4

# ---------- trades ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["week"] = tr["ts"].dt.to_period("W-SUN")
tr["ft"] = FT / tr["risk"]
tr["dec"] = tr["exit"].isin(["SL", "TP"])
tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"])
tr["x"] = tr["tp"] - tr["q"]
tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
say(f"- 本 {len(tr)} {tr.ts.min()}〜{tr.ts.max()} UTC・FEED_TOL {FT}・決着 {int(tr.dec.sum())}・atr 列 {'有' if 'atr' in tr else '無'}")

# ---------- npz: entry price, session daily RV ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
et = tr["entry_time"].to_numpy(np.int64) - 300
pos = np.clip(np.searchsorted(ts, et), 0, len(ts) - 1)
hit = ts[pos] == et
tr["P"] = C[pos]
say(f"- npz {len(ts)} 本・建玉前足 ts 一致 {hit.mean()*100:.2f}%（⑫ 不一致は直前格子値）・建玉価格 中央値 {tr.P.median():.0f} USD")
tr["risk_bp"] = tr["risk"] / tr["P"] * 1e4
tr["atr_bp"] = tr["atr"] / tr["P"] * 1e4
tr["risk_atr"] = np.where(tr["atr"] > 0, tr["risk"] / tr["atr"].replace(0, np.nan), np.nan)
say(f"- atr≤0 の本 {int((tr.atr<=0).sum())}（risk/atr は NaN 扱い）")
say(f"- risk_bp 中央値 {tr.risk_bp.median():.1f} bp・atr_bp {tr.atr_bp.median():.1f} bp・risk/atr {tr.risk_atr.median():.2f}")

lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
sess = dt_ny + pd.Timedelta(hours=6)
S = (sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy())
wd = dt_ny.weekday.to_numpy()
say(f"- flat 全体 {flat.mean()*100:.1f}%・月〜金 {flat[wd<=4].mean()*100:.1f}%（⑪）")
df = pd.DataFrame({"s": S, "r2": r ** 2, "nf": (~flat).astype(np.int32)})
g = df.groupby("s", sort=True)
D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum()})
D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d")
D = D[(D["date"].dt.weekday <= 4) & (D["nf"] >= 100)].reset_index(drop=True)
cs = np.concatenate([[0.0], np.cumsum(D["rv"].to_numpy())])
i = np.arange(len(D)); okt = i - H + 1 >= 0
RVt = np.full(len(D), np.nan); RVt[okt] = 100 * np.sqrt(252.0 / H * (cs[i[okt] + 1] - cs[i[okt] - H + 1]))
D["RVt"] = RVt
say(f"- 有効セッション日 {len(D)}・RVt(21) 中央値 {np.nanmedian(RVt):.1f}%")

gv = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"), na_values="."); gv.columns = ["date", "gvz"]
gv["date"] = pd.to_datetime(gv["date"]); gv = gv.dropna().sort_values("date")
say(f"- GVZCLS {len(gv)} 行 {gv.date.iloc[0].date()}〜{gv.date.iloc[-1].date()}")

# ---------- weekly aggregation ----------
dd = tr[tr.dec]
gw = dd.groupby("week").agg(n=("x", "size"), xbar=("x", "mean"), qbar=("q", "mean"))
gw2 = tr.groupby("week").agg(nall=("b", "size"), bbar=("b", "mean"), risk_bp=("risk_bp", "mean"), atr_bp=("atr_bp", "mean"),
                              risk_atr=("risk_atr", "mean"), Rbar=("Rs", "mean"))
gw = gw.join(gw2, how="outer").sort_index()
gw["valid"] = gw["n"].fillna(0) >= NMIN
gw["start"] = [p.start_time for p in gw.index]
gw["cutoff"] = gw["start"] - pd.Timedelta(days=1)
gw["year"] = gw["start"].dt.year
tmp = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), gv.rename(columns={"date": "gdate"}), left_on="cutoff", right_on="gdate", direction="backward")
tmp2 = pd.merge_asof(gw[["cutoff"]].reset_index().sort_values("cutoff"), D[["date", "RVt"]].rename(columns={"date": "rdate"}), left_on="cutoff", right_on="rdate", direction="backward")
gw = gw.join(tmp.set_index("week")[["gvz", "gdate"]]).join(tmp2.set_index("week")[["RVt", "rdate"]])
gw["stale_g"] = (gw["cutoff"] - gw["gdate"]).dt.days; gw["stale_r"] = (gw["cutoff"] - gw["rdate"]).dt.days
gw["lgvz"] = np.log(gw["gvz"]); gw["lrvt"] = np.log(gw["RVt"]); gw["G1"] = np.log(gw["risk_bp"]); gw["G5"] = np.log(gw["atr_bp"]); gw["G4"] = np.log(gw["risk_atr"])
assert (gw.loc[gw.valid, "gdate"] < gw.loc[gw.valid, "start"]).all() and (gw.loc[gw.valid, "rdate"] < gw.loc[gw.valid, "start"]).all(), "look-ahead"
say(f"- 週 {len(gw)}・有効 {int(gw.valid.sum())}・GVZ staleness 中央値 {gw.loc[gw.valid,'stale_g'].median():.0f} 日（max {gw.loc[gw.valid,'stale_g'].max():.0f}）・RVt staleness {gw.loc[gw.valid,'stale_r'].median():.0f}（max {gw.loc[gw.valid,'stale_r'].max():.0f}）・look-ahead assert OK")
say()

# ---------- stats ----------
def pairs(v):
    pos_ = np.array([(p - v.index[0]).n for p in v.index]); s = {p: k for k, p in enumerate(pos_)}
    ok = np.array([(p + 1) in s for p in pos_])
    ia = np.array([s[p] for p in pos_[ok]]); ib = np.array([s[p + 1] for p in pos_[ok]]); return ia, ib
def lag1(vals, ia, ib):
    a = vals[ia]; b = vals[ib]; ok = np.isfinite(a) & np.isfinite(b); a = a[ok]; b = b[ok]
    return float(np.corrcoef(a, b)[0, 1]) if len(a) > 4 else np.nan
def nancorr(a, b):
    ok = np.isfinite(a) & np.isfinite(b); return float(np.corrcoef(a[ok], b[ok])[0, 1])
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

GEOM = [("G1", "G1 log risk_bp（主）"), ("bbar", "G2 b̄ TP 距離（副）"), ("qbar", "G3 q̄ RW 基準"), ("G4", "G4 log risk/atr14"), ("G5", "G5 log atr_bp（同時期ボラ・対照）"), ("nall", "n 本数（記述）")]
RES = {}
for wn, (y0, y1) in WIN.items():
    v = gw[gw.valid & (gw.year >= y0) & (gw.year <= y1)].copy()
    ia, ib = pairs(v)
    say(f"## {wn}: 有効週 {len(v)}・ペア {len(ia)}・GVZ 中央値 {v.gvz.median():.1f}・RVt {v.RVt.median():.1f}・risk_bp {v.risk_bp.median():.1f} bp・ρ(log GVZ, log RVt) {nancorr(v.lgvz.to_numpy(), v.lrvt.to_numpy()):+.3f}・RVt 欠損週 {int(v.lrvt.isna().sum())}（残差化・残差 r1 は有限ペアのみ）")
    say("| 量 | 生 lag1 r | 置換 p | 95% 点 | β1 log GVZ (t) | β2 log RVt (t) | R² | 残差 lag1 r | 置換 p | r_res/r_raw | プラセボ 残差 r 中央値 [5,95%] | ATR 残差 r | T4 γ_GVZ (t) |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    RES[wn] = {}
    for col, lab in GEOM:
        y = v[col].to_numpy(float)
        r_raw = lag1(y, ia, ib); p_raw, q95 = perm_p(y, ia, ib, r_raw)
        u, b, t, r2 = resid(y, [v.lgvz.to_numpy(), v.lrvt.to_numpy()])
        r_res = lag1(u, ia, ib); p_res, _ = perm_p(u, ia, ib, r_res)
        # placebo: shuffle (gvz, rvt) rows within year
        pl = np.empty(NPLA); yrs = v.year.to_numpy()
        for k in range(NPLA):
            idx = np.arange(len(v)).copy()
            for yy in np.unique(yrs):
                m = np.where(yrs == yy)[0]; idx[m] = rng.permutation(m)
            u_pl, *_ = resid(y, [v.lgvz.to_numpy()[idx], v.lrvt.to_numpy()[idx]]); pl[k] = lag1(u_pl, ia, ib)
        # contemporaneous ATR control
        u_atr, *_ = resid(y, [v.G5.to_numpy()]) if col != "G5" else (np.full(len(v), np.nan), None, None, None)
        r_atr = lag1(u_atr, ia, ib) if col != "G5" else np.nan
        # T4: y_w on y_{w-1}, lgvz_w
        bb, se4, t4, n4, r24, *_ = nw_ols(y[ib], [y[ia], v.lgvz.to_numpy()[ib]])
        RES[wn][col] = dict(r_raw=r_raw, p_raw=p_raw, r_res=r_res, p_res=p_res, ratio=r_res / r_raw if r_raw else np.nan, pl_med=float(np.median(pl)), b=b, t=t, r2=r2, t4=t4[2], g4=bb[2], r_atr=r_atr)
        say(f"| {lab} | **{r_raw:+.3f}** | {p_raw:.4f} | {q95:+.3f} | {b[1]:+.3f} ({t[1]:+.1f}) | {b[2]:+.3f} ({t[2]:+.1f}) | {r2:.3f} | **{r_res:+.3f}** | {p_res:.4f} | {r_res/r_raw if r_raw else np.nan:+.2f} | {np.median(pl):+.3f} [{np.quantile(pl,.05):+.3f},{np.quantile(pl,.95):+.3f}] | {r_atr:+.3f} | {bb[2]:+.3f} ({t4[2]:+.1f}) |")
    # extra: level link in bp units (descriptive) and n per week vs gvz
    bb, se, t, n, r2, *_ = nw_ols(v.risk_bp.to_numpy(), [v.gvz.to_numpy()])
    say(f"- 水準（記述）: risk_bp = {bb[0]:+.1f} + {bb[1]:+.2f}·GVZ（t {t[1]:+.1f}・R² {r2:.3f}）；risk_bp/GVZ 比 中央値 {(v.risk_bp/v.gvz).median():.2f} bp/vol pt")
    say()

# ---------- judgment ----------
say("## 判定（事前固定・主 G1・副 G2・Bonferroni(2)）")
def verdict(col):
    a = RES["在 2010-20"][col]; b = RES["外 2021-26H1"][col]
    HA = (a["r_res"] < 0.5 * a["r_raw"]) and (a["p_res"] >= 0.025) and (b["r_res"] < 0.5 * b["r_raw"]) and (b["p_res"] >= 0.025)
    HB = (a["r_res"] >= 0.5 * a["r_raw"]) and (a["p_res"] < 0.025) and (b["r_res"] >= 0.5 * b["r_raw"]) and (b["p_res"] < 0.025)
    sh_in = 1 - a["ratio"]; sh_out = 1 - b["ratio"]
    return ("H_A PASS（ボラの別名）" if HA else "H_B PASS（独立な状態）" if HB else "部分"), sh_in, sh_out
for col, lab in GEOM[:2]:
    vd, si, so = verdict(col)
    a = RES["在 2010-20"][col]; b = RES["外 2021-26H1"][col]; c = RES["近年 2024-26H1"][col]
    say(f"- {lab}: **{vd}** — 生 r1 在 {a['r_raw']:+.3f}／外 {b['r_raw']:+.3f}／近年 {c['r_raw']:+.3f} → 残差 r1 在 {a['r_res']:+.3f} (p {a['p_res']:.3f})／外 {b['r_res']:+.3f} (p {b['p_res']:.3f})／近年 {c['r_res']:+.3f} (p {c['p_res']:.3f})・ボラが担ぐ持続の割合 1−r_res/r_raw 在 {100*si:.0f}%／外 {100*so:.0f}%・プラセボ残差 r1 中央値 在 {a['pl_med']:+.3f}／外 {b['pl_med']:+.3f}")
say(f"- 陽性対照（生 r1 の置換 p 在 <0.001）: G1 p {RES['在 2010-20']['G1']['p_raw']:.4f}・G2 p {RES['在 2010-20']['bbar']['p_raw']:.4f} → {'OK' if RES['在 2010-20']['G1']['p_raw'] < 0.001 else 'NG'}")
say()

# ---------- T3 gate ㉛ ----------
say("## T3 本番接続（ゲート ㉛・在のみ印字）")
v = gw[gw.valid & (gw.year <= 2020)]
ia, ib = pairs(v)
bb, se, t, n, r2, *_ = nw_ols(v.xbar.to_numpy() * 100, [v.lgvz.to_numpy()])
say(f"- 週次 x̄_w (pp) on log GVZ_known: β {bb[1]:+.2f} pp/log-unit（NW t {t[1]:+.2f}・n {n}・R² {r2:.3f}）；同 R̄*_w: " + (lambda r: f"β {r[0][1]:+.3f}R (t {r[2][1]:+.2f})")(nw_ols(v.Rbar.to_numpy(), [v.lgvz.to_numpy()])))
# trade-level FRED rule
jst = tr["ts"] + pd.Timedelta(hours=9); avail = (jst - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
tt = pd.DataFrame({"avail": avail, "i": np.arange(len(tr))}).sort_values("avail")
m = pd.merge_asof(tt, gv.rename(columns={"date": "gdate"}), left_on="avail", right_on="gdate", direction="backward", tolerance=pd.Timedelta(days=7)).sort_values("i")
tr["gvz_k"] = m["gvz"].to_numpy()
ins = tr[(tr.year <= 2020) & tr.gvz_k.notna()]
lo, hi = ins.gvz_k.quantile([1 / 3, 2 / 3])
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return diff, diff / se
rows = []
for lab, mk in (("top", ins.gvz_k > hi), ("bottom", ins.gvz_k <= lo)):
    s = ins[mk]; rest = ins[~mk]
    dmu, tmu = welch(s.Rs, rest.Rs); dx = 100 * (s[s.dec].x.mean() - ins[ins.dec].x.mean())
    rows.append((lab, len(s), dmu, tmu, dx))
x0cut = ins.x0.quantile(2 / 3); s = ins[ins.x0 > x0cut]; d0, t0_ = welch(s.Rs, ins[ins.x0 <= x0cut].Rs)
say(f"- 本レベル（在・付与 {len(ins)}/{int((tr.year<=2020).sum())}・三分位 {lo:.1f}/{hi:.1f}）: " + "・".join(f"{lab} n{n_} Δμ {dmu:+.3f}R (t {tmu:+.2f})・Δx {dx:+.2f} pp" for lab, n_, dmu, tmu, dx in rows) + f"；look-ahead 対照 x0 top Δμ {d0:+.3f}R (t {t0_:+.1f})")
mx = max(abs(r_[2]) for r_ in rows)
say(f"- ゲート ㉛: 在 max|Δμ| {mx:.3f}R {'<' if mx < 0.048 else '≥'} 0.048R → **{'決着不能・外は走らせない' if mx < 0.048 else '外を印字'}**")
if mx >= 0.048:
    oos = tr[(tr.year >= 2021) & tr.gvz_k.notna()]
    for lab, mk in (("top", oos.gvz_k > hi), ("bottom", oos.gvz_k <= lo)):
        s = oos[mk]; dmu, tmu = welch(s.Rs, oos[~mk].Rs); say(f"  外 {lab} n{len(s)} Δμ {dmu:+.3f}R (t {tmu:+.2f})")
say()
say(f"所要 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
