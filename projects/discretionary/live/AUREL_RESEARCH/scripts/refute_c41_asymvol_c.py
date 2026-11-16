# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-16 反証レーン・追撃 c] 下降局面の γ_dn（在 −6.8 t −3.9／外 −8.0 t −3.3・2013／2021 に局在）への最後の別説明:
「日次の符号非対称」ではなく「数週間スケールで 価格↓ と ボラ↑ が同時に進む（暴落局面の共通トレンド）」。lrv・lrv5 は**ラグ**なので、
ボラが上昇トレンドにある期間は残差が平均的に正、同じ期間 r は平均的に負 → 低周波の共変動が γ に負として漏れる。
規則 C1: 年月固定効果（年月内で y・lrv・lrv5・|r|・r を中心化）で γ_dn を再推定。**在 |t| < 2 に落ちる → 「低周波共変動」＝ 日次非対称としては broken**。
規則 C2: r を 直近 20 日平均で中心化した r̃ の符号非対称 γ̃_dn（同じ趣旨の別実装）。
規則 C3: 同じ処理を US500 の γ（全体）に当てて、本物のレバレッジ効果が年月 FE で消えないことを対照にする。
"""
import os, time, datetime as dt, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c41_asymvol_c.md"); NY = "America/New_York"; L = []; T0 = time.time()
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c41 追撃 c] 年月固定効果で γ_dn は残るか — {time.strftime('%Y-%m-%d %H:%M')}")
def nw_ols(y, X, lag=5):
    y = np.asarray(y, float); X = np.asarray(X, float); n = len(y); Z = np.column_stack([np.ones(n), X]); Xi = np.linalg.pinv(Z.T @ Z)
    b = Xi @ Z.T @ y; u = y - Z @ b; Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = Xi @ Sm @ Xi; return b, np.sqrt(np.abs(np.diag(V)))
def daily(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); keep = r != 0
    sess = (pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY) + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    so = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    df = pd.DataFrame({"o": so[keep], "lc": lc[keep], "r2": r[keep] ** 2}); g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()}).reset_index()
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.o]); D = D[(D.date.dt.weekday <= 4) & (D.nf >= 100)].reset_index(drop=True)
    D["lrv"] = np.log(D.rv); D["r"] = np.r_[np.nan, np.diff(D.lc)] * 1e4; D["lrv5"] = D.lrv.rolling(5).mean(); D["year"] = D.date.dt.year
    D["ym"] = D.year * 100 + D.date.dt.month; D["s60"] = np.sign(D.lc - D.lc.shift(60)); D["r20"] = D.r.rolling(20).mean()
    n = len(D); V = pd.DataFrame({"y": D.lrv.to_numpy()[1:], "lrv": D.lrv.to_numpy()[:-1], "lrv5": D.lrv5.to_numpy()[:-1], "r": D.r.to_numpy()[:-1],
                                   "r20": D.r20.to_numpy()[:-1], "year": D.year.to_numpy()[:-1], "ym": D.ym.to_numpy()[:-1], "s60": D.s60.to_numpy()[:-1]})
    V["ar"] = V.r.abs(); V["rt"] = V.r - V.r20; V["art"] = V.rt.abs()
    ok = np.isfinite(V.y) & np.isfinite(V.lrv) & np.isfinite(V.lrv5) & np.isfinite(V.r) & np.isfinite(V.r20) & np.isfinite(V.s60); return V[ok].reset_index(drop=True)
def gam(v, cols=("lrv", "lrv5", "ar", "r"), fe=None):
    if len(v) < 100: return (np.nan, np.nan, len(v))
    M = v[list(cols) + ["y"]].copy()
    if fe is not None: M = M - M.groupby(v[fe]).transform("mean")
    b, se = nw_ols(M.y.to_numpy(), M[list(cols)].to_numpy()); return b[-1] * 1e4, b[-1] / se[-1], len(v)
VX = daily("XAU"); VU = daily("US500")
say("| 銘柄 | 窓 | 部分集合 | γ 基本 (t・n) | γ 年月 FE (t) | γ̃ r 中心化 (t) | γ̃ 年月 FE (t) |"); say("|---|---|---|---|---|---|---|")
RES = {}
for sym, V, wins in (("XAU", VX, {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026)}), ("US500", VU, {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026)})):
    for wn, (y0, y1) in wins.items():
        v = V[(V.year >= y0) & (V.year <= y1)].reset_index(drop=True)
        for name, vv in (("全体", v), ("s60 下降", v[v.s60 < 0].reset_index(drop=True)), ("s60 上昇", v[v.s60 > 0].reset_index(drop=True))):
            g0 = gam(vv); g1 = gam(vv, fe="ym"); g2 = gam(vv, cols=("lrv", "lrv5", "art", "rt")); g3 = gam(vv, cols=("lrv", "lrv5", "art", "rt"), fe="ym")
            RES[(sym, wn, name)] = (g0, g1, g2, g3)
            say(f"| {sym} | {wn} | {name} | {g0[0]:+.2f} ({g0[1]:+.2f}・{g0[2]}) | **{g1[0]:+.2f} ({g1[1]:+.2f})** | {g2[0]:+.2f} ({g2[1]:+.2f}) | {g3[0]:+.2f} ({g3[1]:+.2f}) |")
a = RES[("XAU", "在 2010-20", "s60 下降")]; o = RES[("XAU", "外 2021-26H1", "s60 下降")]
C1_broken = abs(a[1][1]) < 2
say(f"- C1 判定（在 下降局面 年月 FE t {a[1][1]:+.2f}・外 {o[1][1]:+.2f}）: {'**broken（年月 FE で消える＝低周波共変動）**' if C1_broken else 'survived（月内の日次変動でも γ_dn < 0）'}")
say(f"- 対照 US500 全体 年月 FE: 在 {RES[('US500','在 2014-20','全体')][1][0]:+.2f} (t {RES[('US500','在 2014-20','全体')][1][1]:+.2f})・外 {RES[('US500','外 2021-26H1','全体')][1][0]:+.2f} (t {RES[('US500','外 2021-26H1','全体')][1][1]:+.2f})")
say(f"所要 {time.time()-T0:.1f} s"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
