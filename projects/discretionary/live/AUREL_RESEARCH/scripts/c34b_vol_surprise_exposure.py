# -*- coding: utf-8 -*-
"""
[cycle34 補足 b・事後・記述・look-ahead] 壁→壁(再加速) scan は「実現ボラ・サプライズ」に対してロングか？
VS_i = RV_fwd(建玉セッション日, +21 日) − GVZ(建玉時既知)（vol pt・前向き実現 − インプライド＝look-ahead）。
scan 19404 本（決着 TP/SL）の R と x = 1{TP}−q を VS の三分位（窓内）で印字・β(R on VS)（日クラスタ t）。
問い（機構・入口規則ではない）: c34 で金の VRP が正（IV > RV・保険の売り手が受け取る）と出た。ブレイクアウト戦略は直感的にロング・ボラ
（走れば TP・走らなければ SL）。もし scan の R が VS に正に依存するなら、scan の無条件期待値 −0.02〜−0.05R（refute_c4）は
「ボラ保険料を払う側に立っている」ことで説明され得る（仮説・本補足は look-ahead なので記述のみ・予測には使えない）。
"""
import os, json, time
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro"); OUT = os.path.join(DATA, "c34b_vol_surprise_exposure.md")
NY = "America/New_York"; H = 21
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle34 補足 b] scan の実現ボラ・サプライズ露出（look-ahead・記述） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c34b_vol_surprise_exposure.py)")
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0
dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY); sess = dt_ny + pd.Timedelta(hours=6)
S = sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy()
df = pd.DataFrame({"s": S, "r2": r ** 2, "nf": (~flat).astype(np.int32)}); g = df.groupby("s", sort=True)
D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum()}); D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d")
D = D[(D["date"].dt.weekday <= 4) & (D["nf"] >= 100)].reset_index(drop=True)
rv = D["rv"].to_numpy(); n = len(D); cs = np.concatenate([[0.0], np.cumsum(rv)]); i = np.arange(n)
RVf = np.full(n, np.nan); ok = i + H < n; RVf[ok] = 100 * np.sqrt(252.0 / H * (cs[i[ok] + H + 1] - cs[i[ok] + 1]))
RVt = np.full(n, np.nan); okt = i - H + 1 >= 0; RVt[okt] = 100 * np.sqrt(252.0 / H * (cs[i[okt] + 1] - cs[i[okt] - H + 1]))
D["RVf"] = RVf; D["RVt"] = RVt
GV = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"), na_values="."); GV.columns = ["date", "IV"]; GV["date"] = pd.to_datetime(GV["date"]); GV = GV.dropna()
D = D.merge(GV, on="date", how="left")
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True); FT = J["frozen"]["FEED_TOL"]
# 建玉セッション日
e_ny = pd.to_datetime(T["entry_time"], unit="s", utc=True).dt.tz_convert(NY) + pd.Timedelta(hours=6)
T["sdate"] = e_ny.dt.normalize().dt.tz_localize(None)
# GVZ 既知（FRED 規則）
ent_jst = pd.to_datetime(T["entry_time"], unit="s", utc=True) + pd.Timedelta(hours=9)
T["avail"] = (ent_jst - pd.Timedelta(hours=7)).dt.normalize().dt.tz_localize(None) - pd.Timedelta(days=1)
K = D[["date", "IV", "RVt"]].dropna().rename(columns={"date": "kdate"}).sort_values("kdate")
T = pd.merge_asof(T.sort_values("avail"), K, left_on="avail", right_on="kdate", direction="backward", tolerance=pd.Timedelta(days=7))
# 前向き実現（建玉セッション日から +21 有効日・look-ahead）
F = D[["date", "RVf"]].rename(columns={"date": "sdate"})
T = T.merge(F, on="sdate", how="left").sort_values("entry_time").reset_index(drop=True)
T["VS"] = T["RVf"] - T["IV"]; T["VSt"] = T["RVf"] - T["RVt"]
dec = T["exit"].isin(["TP", "SL"]) & T["VS"].notna()
T["q"] = (1 - FT / T["risk"]) / (1 + T["b"]); T["x"] = (T["exit"] == "TP").astype(float) - T["q"]
T["day"] = T["entry_time"] // 86400
say(f"- scan 本 {len(T)}・決着 ∧ VS 付与 {dec.sum()}・VS 中央値 {T.loc[dec,'VS'].median():+.2f} vol pt")
def cl_t(d, day):
    d = np.asarray(d, float); m = d.mean(); s = pd.DataFrame({"d": d - m, "g": day}).groupby("g")["d"].sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / len(d); return m, se, m / se
def cl_ols(y, x, day):
    y = np.asarray(y, float); x = np.asarray(x, float); xm = x - x.mean(); b = (xm * y).sum() / (xm ** 2).sum(); a = y.mean() - b * x.mean()
    u = y - a - b * x; s = pd.DataFrame({"d": xm * u, "g": day}).groupby("g")["d"].sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / (xm ** 2).sum(); return b, se, b / se
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
say("| 窓 | n | R̄ | 三分位 VS 低／中／高: R̄ | x̄ pp | Δμ(高−低) R (日cl t) | β R on VS (R/vol pt・t) | β x on VS (pp/pt・t) | 同 β on VSt=RVf−RVt (t) |")
say("|---|---|---|---|---|---|---|---|---|")
for w, (y0, y1) in WIN.items():
    m = dec & (T["year"] >= y0) & (T["year"] <= y1); d = T[m].copy(); q = np.quantile(d["VS"], [1 / 3, 2 / 3])
    d["tc"] = np.where(d["VS"] <= q[0], 0, np.where(d["VS"] <= q[1], 1, 2))
    Rb = d.groupby("tc")["R"].mean(); xb = d.groupby("tc")["x"].mean() * 100
    hi = d[d["tc"] == 2]; lo = d[d["tc"] == 0]
    dm = hi["R"].mean() - lo["R"].mean(); se = np.sqrt(cl_t(hi["R"], hi["day"])[1] ** 2 + cl_t(lo["R"], lo["day"])[1] ** 2)
    bR = cl_ols(d["R"], d["VS"], d["day"]); bx = cl_ols(d["x"] * 100, d["VS"], d["day"]); bt = cl_ols(d["R"], d["VSt"], d["day"])
    say(f"| {w} | {len(d)} | {d['R'].mean():+.3f} | {Rb[0]:+.3f}／{Rb[1]:+.3f}／{Rb[2]:+.3f} | {xb[0]:+.1f}／{xb[1]:+.1f}／{xb[2]:+.1f} | **{dm:+.3f} ({dm/se:+.2f})** | {bR[0]:+.4f} ({bR[2]:+.2f}) | {bx[0]:+.3f} ({bx[2]:+.2f}) | {bt[0]:+.4f} ({bt[2]:+.2f}) |")
# 側別・事後
for w, (y0, y1) in WIN.items():
    out = []
    for sd in ("BUY", "SELL"):
        m = dec & (T["year"] >= y0) & (T["year"] <= y1) & (T["side"] == sd); d = T[m]; b = cl_ols(d["R"], d["VS"], d["day"])
        out.append(f"{sd} n{len(d)} β {b[0]:+.4f} (t {b[2]:+.2f})")
    say(f"- {w} 側別 β(R on VS): " + "；".join(out))
# 月次: 月平均 R vs 月の VS 平均
T["ym"] = T["sdate"].dt.to_period("M")
M = T[dec].groupby("ym").agg(R=("R", "mean"), VS=("VS", "mean"), n=("R", "size"), yr=("year", "first"))
for w, (y0, y1) in WIN.items():
    mm = M[(M["yr"] >= y0) & (M["yr"] <= y1)]; rho = mm[["R", "VS"]].corr(method="spearman").iloc[0, 1]
    say(f"- {w} 月次（n {len(mm)} か月）: Spearman ρ(月平均 R, 月平均 VS) {rho:+.3f}")
say(f"\n- 実行時間 {time.time()-T0:.1f}s・look-ahead（RV_fwd は建玉後）＝記述のみ・入口規則にしない")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
