# -*- coding: utf-8 -*-
"""
[cycle40 補足 b] c40 の衛生 2 点（結果を見た後の補足＝記述・判定には使わない）:
 (1) 置換帰無の校正: c40 の週循環シフト置換は帰無 sd 0.008 vs HC1 se 0.033（4 倍の差）。原因候補 = ボラの同時クラスタ（|FIRST| が大きい日は LAST の分散も大きい）
     をシフトが壊す → **符号反転置換**（各日の FIRST の符号を独立に反転・|FIRST| と日の対応を保存）の帰無 sd を HC1 se と並べる。
 (2) 金の 外 LAST~FIRST_B 正は「引け固有」か「1 日の継続（c8 cont_24h の時代効果）」か: 09:30 から 16:00 までの 13 半時間それぞれを FIRST_B で回帰した β_h の
     プロファイル（引けだけ跳ねるか、全日なだらかか）と、FIRST_B を ON（前日 16:00 → 09:30）と FIRST_A（09:30 → 10:00）に分けた 2 変数回帰。
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c40b_intraday_momentum_checks.md"); L = []
NY = "America/New_York"; rng = np.random.default_rng(20261111); NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle40 補足 b] 置換帰無の校正（符号反転）と金の半時間プロファイル — {time.strftime('%Y-%m-%d %H:%M')}")
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); return zz["ts"].astype(np.int64), zz["close"].astype(float)
def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T); key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]; N = len(dates); yr = dates.year.to_numpy(); lg = np.log
ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
def ols(y, x):
    m = np.isfinite(y) & np.isfinite(x); y, x = y[m], x[m]; n = len(y)
    if n < 30: return dict(n=n, b=np.nan, t=np.nan, se=np.nan)
    xc = x - x.mean(); yc = y - y.mean(); sxx = xc @ xc; b = (xc @ yc) / sxx; e = yc - b * xc
    se = math.sqrt((xc ** 2 @ e ** 2) / sxx ** 2 * n / (n - 2)); return dict(n=n, b=b, t=b / se, se=se)
def ols2(y, x1, x2):
    m = np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2); y, x1, x2 = y[m], x1[m], x2[m]; n = len(y)
    X = np.c_[np.ones(n), x1, x2]; XtXi = np.linalg.inv(X.T @ X); b = XtXi @ X.T @ y; e = y - X @ b
    V = XtXi @ (X.T * e ** 2) @ X @ XtXi * n / (n - 3); se = np.sqrt(np.diag(V)); return b, b / se, n
def signflip_sd(y, x, m):
    mm = m & np.isfinite(y) & np.isfinite(x); xv, yv = x[mm], y[mm]; yc = yv - yv.mean(); out = np.empty(NPERM)
    for j in range(NPERM):
        xs = xv * rng.choice([-1.0, 1.0], size=len(xv)); xc = xs - xs.mean(); out[j] = (xc @ yc) / (xc @ xc)
    return np.std(out)
def shift_sd(y, x, m):
    idx = np.where(m)[0]; xv, yv = x[idx], y[idx]; nweeks = len(idx) // 5; out = np.empty(NPERM)
    for j, k in enumerate(rng.integers(1, max(2, nweeks), size=NPERM)):
        xs = np.roll(xv, 5 * int(k)); mm = np.isfinite(xs) & np.isfinite(yv); xc = xs[mm] - xs[mm].mean(); yc = yv[mm] - yv[mm].mean(); out[j] = (xc @ yc) / (xc @ xc)
    return np.std(out)

for sym in ("US500", "XAU"):
    ts, cl = load(sym); P = lambda h, m: price_at(ts, cl, epoch_et(dates, h, m))
    p16 = P(16, 0); p16p = np.r_[np.nan, p16[:-1]]; p0930 = P(9, 30); p10 = P(10, 0)
    FB = (lg(p10) - lg(p16p)) * 1e4; FA = (lg(p10) - lg(p0930)) * 1e4; ON = (lg(p0930) - lg(p16p)) * 1e4
    H = {}; slots = [(10, 0), (10, 30), (11, 0), (11, 30), (12, 0), (12, 30), (13, 0), (13, 30), (14, 0), (14, 30), (15, 0), (15, 30), (16, 0)]
    prev = p10
    for (h, mi) in slots[1:]:
        cur = P(h, mi); H[f"{h:02d}:{mi:02d}"] = (lg(cur) - lg(prev)) * 1e4; prev = cur
    LAST = H["16:00"]
    valid = np.isfinite(FB) & np.isfinite(LAST) & (LAST != 0) & (FB != 0) & np.isfinite(FA)
    say(f"\n## {sym}")
    say("| 期間 | HC1 se | 符号反転 帰無 sd | 週シフト 帰無 sd | β 観測 | 符号反転 片側 p |"); say("|---|---|---|---|---|---|")
    for lab, lo, hi in ERAS:
        m = valid & (yr >= lo) & (yr <= hi); o = ols(LAST[m], FB[m]); s1 = signflip_sd(LAST, FB, m); s2 = shift_sd(LAST, FB, m)
        say(f"| {lab} | {o['se']:.4f} | {s1:.4f} | {s2:.4f} | {o['b']:+.4f} | {1 - 0.5 * (1 + math.erf(o['b'] / s1 / math.sqrt(2))):.4f} |")
    say("\n半時間プロファイル β_h（各半時間リターン ~ FIRST_B・HC1 t）:")
    say("| 期間 | " + " | ".join(H.keys()) + " |"); say("|---|" + "---|" * len(H))
    for lab, lo, hi in ERAS:
        m = valid & (yr >= lo) & (yr <= hi)
        say(f"| {lab} | " + " | ".join(f"{ols(H[k][m], FB[m])['b']:+.3f} ({ols(H[k][m], FB[m])['t']:+.1f})" for k in H) + " |")
    say("\nFIRST_B の分解: LAST = a + b1·ON(前日 16:00→09:30) + b2·FIRST_A(09:30→10:00)（HC1 t）")
    for lab, lo, hi in ERAS:
        m = valid & (yr >= lo) & (yr <= hi); b, t, n = ols2(LAST[m], ON[m], FA[m])
        say(f"- {lab}: b_ON {b[1]:+.4f} (t {t[1]:+.2f})・b_FIRST_A {b[2]:+.4f} (t {t[2]:+.2f})・n {n}・ON sd {np.nanstd(ON[m]):.0f} bp／FIRST_A sd {np.nanstd(FA[m]):.0f} bp")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
