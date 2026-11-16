# -*- coding: utf-8 -*-
"""
[cycle43 補足 b・事後・記述・判定に使わない] c43 の陽性対照が 2 本とも「検出力不足」を返したので、(a) 順位ベースの頑健版（Mann–Whitney on |LAST|・|LAST5|）で
同じ問いを見直す、(b) XAU の OPEX/QW LAST5 VR（外 7.5・近年 4.6）が少数の外れ日に依るかを上位日で確認、(c) C2 在 US500 の δ +1.41（HC1 t 2.26）を置換帰無 sd と並べて
HC1 の校正を見る（㊷）。入力は c43 と同じ npz のみ。seed 20261117。
"""
import os, sys, time, math, datetime as dt
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c43b_expiration_robust_checks.md"); L = []
NY = "America/New_York"; rng = np.random.default_rng(20261117)
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle43 補足 b・事後] 満期日効果の頑健版・外れ日・校正 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c43b_expiration_robust_checks.py)")
import importlib.util
spec = importlib.util.spec_from_file_location("c43", os.path.join(HERE, "c43_expiration_day_effects.py"))
# c43 はモジュール読込で実行されるので関数だけ複製する
def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T); key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31; da = ((h + l - 7 * m + 114) % 31) + 1; return dt.date(y, mo, da)
def third_friday(y, m):
    d = dt.date(y, m, 1); off = (4 - d.weekday()) % 7; return d + dt.timedelta(days=off + 14)
OPEX, QW = set(), set()
for y in range(2012, 2027):
    gf = easter(y) - dt.timedelta(days=2)
    for m in range(1, 13):
        f3 = third_friday(y, m)
        if f3 == gf: continue
        OPEX.add(f3); QW.add(f3) if m in (3, 6, 9, 12) else None
dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]; N = len(dates); yr = dates.year.to_numpy(); lg = np.log
is_fri = dates.weekday.to_numpy() == 4; dser = dates.date
E_OPEX = np.array([d in OPEX for d in dser]); E_QW = np.array([d in QW for d in dser])
ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
def windows(ts, cl):
    P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
    p0930, p1530, p1555, p1600 = P(9, 30), P(15, 30), P(15, 55), P(16, 0)
    W = {"LAST": (lg(p1600) - lg(p1530)) * 1e4, "LAST5": (lg(p1600) - lg(p1555)) * 1e4, "CASH": (lg(p1530) - lg(p0930)) * 1e4}
    nx0930 = np.full(N, np.nan); nx1000 = np.full(N, np.nan)
    for off in range(1, 6):
        a, b = P(9, 30, off), P(10, 0, off); ok = np.isnan(nx0930) & np.isfinite(a) & np.isfinite(b) & (a != b); nx0930[ok] = a[ok]; nx1000[ok] = b[ok]
    W["NEXT"] = (lg(nx1000) - lg(p1600)) * 1e4; return W
for sym in ("US500", "XAU"):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float); W = windows(ts, cl)
    valid = is_fri & np.isfinite(W["LAST"]) & np.isfinite(W["CASH"]) & np.isfinite(W["NEXT"]) & (W["LAST"] != 0) & (W["CASH"] != 0)
    say(f"\n## {sym}")
    for e, a, b in ERAS:
        m = valid & (yr >= a) & (yr <= b); ctrl = m & ~E_OPEX
        for lab, E in (("QW", E_QW), ("OPEX", E_OPEX)):
            ev = m & E; row = []
            for wn in ("LAST", "LAST5", "CASH"):
                xe, xc = np.abs(W[wn][ev]), np.abs(W[wn][ctrl]); xe, xc = xe[np.isfinite(xe)], xc[np.isfinite(xc)]
                u, p = mannwhitneyu(xe, xc, alternative="two-sided"); auc = u / (len(xe) * len(xc))
                row.append(f"{wn} AUC {auc:.2f}（p {p:.3f}・中央値 {np.median(xe):.1f} vs {np.median(xc):.1f} bp）")
            say(f"- {e} {lab}（n {int(ev.sum())}）順位検定 |窓|: " + "・".join(row))
    # 外れ日
    ev = valid & E_OPEX & (yr >= 2021); o = np.argsort(-np.abs(W["LAST5"][ev]))[:6]; dd = dates[ev][o]
    say(f"- 外 OPEX の |LAST5| 上位 6 日: " + "・".join(f"{d.date()}{'(QW)' if d.date() in QW else ''} {W['LAST5'][ev][i]:+.0f} bp (LAST {W['LAST'][ev][i]:+.0f})" for d, i in zip(dd, o)))
    ev = valid & E_OPEX & (yr >= 2021); tot = np.sum(W["LAST5"][ev] ** 2); top = np.sort(W["LAST5"][ev] ** 2)[::-1]
    say(f"  - 外 OPEX LAST5 二乗和に占める上位 1／3 日の比率 {top[0]/tot*100:.0f}%／{top[:3].sum()/tot*100:.0f}%（n {int(ev.sum())}）・上位 3 日を除いた VR {np.mean(np.sort(W['LAST5'][ev]**2)[:-3])/np.mean(W['LAST5'][valid&~E_OPEX&(yr>=2021)]**2):.2f}")
    ctrl = valid & ~E_OPEX & (yr >= 2021); o = np.argsort(-np.abs(W["LAST5"][ctrl]))[:3]
    say(f"  - 対照金曜（外）の |LAST5| 上位 3 日: " + "・".join(f"{d.date()} {W['LAST5'][ctrl][i]:+.0f}" for d, i in zip(dates[ctrl][o], o)))
    if sym == "US500":
        m = valid & (yr <= 2020); y = W["NEXT"][m]; x = W["LAST"][m]; Ei = E_OPEX[m].astype(float); n_i = int(m.sum()); k_e = int(Ei.sum())
        X = np.c_[np.ones(n_i), x, x * Ei, Ei]; b0 = np.linalg.lstsq(X, y, rcond=None)[0]
        sims = np.empty(2000)
        for i in range(2000):
            l_ = np.zeros(n_i); l_[rng.choice(n_i, k_e, replace=False)] = 1.0; sims[i] = np.linalg.lstsq(np.c_[np.ones(n_i), x, x * l_, l_], y, rcond=None)[0][2]
        say(f"- 校正（㊷）在 US500 C2: δ 実測 {b0[2]:+.3f}・置換帰無 sd {sims.std():.3f} → z {b0[2]/sims.std():+.2f}（HC1 t +2.26）・両側置換 p {(np.abs(sims)>=abs(b0[2])).mean():.3f}・影響点: |LAST| 最大の OPEX 日を 1 つ除くと δ " + f"{np.linalg.lstsq(np.delete(X, np.argmax(np.abs(x)*Ei), axis=0), np.delete(y, np.argmax(np.abs(x)*Ei)), rcond=None)[0][2]:+.3f}")
say(f"\n（所要 {time.time()-T0:.1f} s）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
