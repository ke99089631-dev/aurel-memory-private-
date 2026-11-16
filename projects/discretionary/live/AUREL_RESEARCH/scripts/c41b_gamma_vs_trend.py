# -*- coding: utf-8 -*-
"""
[cycle41 補足 b・記述・事後] 金の年別 γ（翌日 log RV の非対称係数・c41 と同じ回帰）は年間トレンドの方向に追随するか。
c41 の年別 γ は 2013 −13.6（t −4.5・金 −28% の年）／2019 +16.4（t +3.6・+18%）／2021 −15.4（t −3.7）／2025 +6.5（t +2.2）と符号が年で割れる
→ 事後の読み「非対称の符号は固定でなく、その年の大きな動きの向き（トレンド）に乗る」を 年別 γ × 年間リターン の Spearman で 1 行。
US500（本拠）は全年負＝対照（トレンドに依存しないはず）。数字を見た後の読みなので判定には使わない（記述・新仮説の種）。
"""
import os, math, datetime as dt, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c41b_gamma_vs_trend.md"); NY = "America/New_York"; L = []
def say(s=""): print(s, flush=True); L.append(s)
def hc1(y, X):
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z); b = XtX_inv @ Z.T @ y; u = y - Z @ b
    V = XtX_inv @ ((Z * u[:, None]).T @ (Z * u[:, None])) @ XtX_inv * n / (n - Z.shape[1]); return b, np.sqrt(np.diag(V))
say("# [cycle41 補足 b] 年別 γ × 年間リターン（記述・事後）")
for sym, y0 in (("XAU", 2010), ("US500", 2014)):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); keep = r != 0
    sess = (pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY) + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    so = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    df = pd.DataFrame({"o": so[keep], "lc": lc[keep], "r2": r[keep] ** 2}); g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()}).reset_index()
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.o]); D = D[(D.date.dt.weekday <= 4) & (D.nf >= 100)].reset_index(drop=True)
    D["lrv"] = np.log(D.rv); D["r"] = np.r_[np.nan, np.diff(D.lc)] * 1e4; D["lrv5"] = D.lrv.rolling(5).mean(); D["year"] = D.date.dt.year
    y = D.lrv.to_numpy()[1:]; X = np.column_stack([D.lrv.to_numpy()[:-1], D.lrv5.to_numpy()[:-1], np.abs(D.r.to_numpy()[:-1]), D.r.to_numpy()[:-1]]); yr = D.year.to_numpy()[:-1]
    ok = np.isfinite(y) & np.isfinite(X).all(1); y, X, yr = y[ok], X[ok], yr[ok]
    rows = []
    for yy in range(y0, 2027):
        m = yr == yy
        if m.sum() < 100: continue
        b, se = hc1(y[m], X[m]); ret = (D.lc[D.year == yy].iloc[-1] - D.lc[D.year == yy].iloc[0]) * 100
        rows.append((yy, b[4] * 1e4, b[4] / se[4], ret))
    T = pd.DataFrame(rows, columns=["year", "gamma", "t", "ret_pct"])
    rho, p = spearmanr(T.gamma, T.ret_pct); same = int((np.sign(T.gamma) == np.sign(T.ret_pct)).sum())
    say(f"## {sym}: 年 {len(T)}・Spearman ρ(γ_year, 年間リターン) {rho:+.2f} (p {p:.3f})・符号一致 {same}/{len(T)}・|t|≥2 の年: " + "・".join(f"{int(a.year)} γ {a.gamma:+.1f} (t {a.t:+.1f}) ret {a.ret_pct:+.0f}%" for a in T.itertuples() if abs(a.t) >= 2))
    say("| " + " | ".join(str(int(v)) for v in T.year) + " |"); say("|" + "---|" * len(T))
    say("| " + " | ".join(f"{v:+.1f}" for v in T.gamma) + " |"); say("| " + " | ".join(f"{v:+.0f}%" for v in T.ret_pct) + " |")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
