# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-09 反証レーン・補足 b] refute_c22_overnight.py の R4（上位 5% 除去）は片側の切り捨てで帰無でも負に偏る。
公平な版＝両側トリム平均（5%/5%・2.5%/2.5%）・下位 5% の寄与・在との比較を印字する。
加えて 外 2021-26H1 の US100 EU を LOYO（1 年抜き）で平均・t・順位、2021-23 vs 2024-26H1、
および「EU − 同日の他 10 ブロック平均」（日次ドリフトを引いた超過）の sign-flip p（在・外）を出す。判定規則は変えない（記述）。
seed 20261109
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c22_overnight_b.md"); L = []
NY = "America/New_York"; SEED = 20261109; rng = np.random.default_rng(SEED)
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c22 b] 両側トリム・LOYO・超過 sign-flip — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c22_overnight_b.py)")
def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T); key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
def stats(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 20: return dict(n=n, mean=np.nan, se=np.nan, t=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return dict(n=n, mean=m, se=se, t=m / se)
def f(s): return f"{s['mean']:+.2f} bp (t{s['t']:+.2f}, n{s['n']})" if s["n"] >= 20 else f"n{s['n']} —"
DATES = pd.date_range("2012-01-02", "2026-06-30", freq="D"); DATES = DATES[DATES.weekday <= 4]; YR = DATES.year.to_numpy()
BLK = ["18-20", "20-22", "22-00", "00-02", "02-04", "04-06", "06-08", "08-10", "10-12", "12-14", "14-16"]
zz = np.load(os.path.join(MAC, "US100_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
P = lambda h, m, off=0: price_at(ts, cl, epoch_et(DATES, h, m, off)); lg = np.log
p_re = P(18, 5, -1); p_0930 = P(9, 30); p_1600 = P(16, 0)
CASH = (lg(p_1600) - lg(p_0930)) * 1e4; ON = (lg(p_0930) - lg(p_re)) * 1e4
H = {18: (lg(P(19, 0, -1)) - lg(p_re)) * 1e4}
for h in range(19, 24): H[h] = (lg(P(h + 1 if h < 23 else 0, 0, -1 if h < 23 else 0)) - lg(P(h, 0, -1))) * 1e4
for h in range(0, 17): H[h] = (lg(P(h + 1, 0)) - lg(P(h, 0))) * 1e4
B = {"18-20": H[18] + H[19], "20-22": H[20] + H[21], "22-00": H[22] + H[23]}
for a in range(0, 16, 2): B[f"{a:02d}-{a+2:02d}"] = H[a] + H[a + 1]
EU = B["02-04"]; valid = np.isfinite(CASH) & (CASH != 0) & np.isfinite(ON)
XB = np.column_stack([B[k] for k in BLK]); eu = BLK.index("02-04")
def rank(m):
    mm = np.nanmean(XB[m], 0); return 1 + (mm > mm[eu]).sum()

say("\n## 両側トリム（公平版）・外 2021-26H1 vs 在 2014-20")
for lab, m in (("外 2021-26H1", valid & (YR >= 2021)), ("在 2014-20", valid & (YR >= 2014) & (YR <= 2020)), ("近年 2024-26H1", valid & (YR >= 2024))):
    x = EU[m]; x = x[np.isfinite(x)]; xs = np.sort(x); n = len(x)
    for q in (0.025, 0.05):
        k = int(round(q * n)); tm = xs[k:n - k].mean()
        say(f"- {lab} n{n}: 両側 {q*100:.1f}% トリム平均 {tm:+.2f} bp" + (f"・平均 {x.mean():+.2f}・中央値 {np.median(x):+.2f}" if q == 0.025 else ""))
    k = int(round(0.05 * n)); say(f"  - 上位 5% の和 {xs[-k:].sum():+.0f} bp・下位 5% の和 {xs[:k].sum():+.0f} bp・全体の和 {x.sum():+.0f} bp＝上位 5% 寄与 {xs[-k:].sum()/x.sum()*100:+.0f}%／下位 5% 寄与 {xs[:k].sum()/x.sum()*100:+.0f}%（対称分布なら両者はほぼ相殺）")
    # bootstrap CI for mean (iid days)
    bs = np.array([rng.choice(x, n).mean() for _ in range(4000)]); say(f"  - bootstrap 95% CI 平均 [{np.quantile(bs,.025):+.2f}, {np.quantile(bs,.975):+.2f}] bp")

say("\n## 外 2021-26H1 US100 EU の LOYO（1 年抜き）・前半/後半")
O = valid & (YR >= 2021)
say(f"- 全体 {f(stats(EU[O]))} 順位 {rank(O)}")
for y in range(2021, 2027):
    m = O & (YR != y); say(f"- −{y}: {f(stats(EU[m]))} 順位 {rank(m)}")
for lab, m in (("2021-23", valid & (YR >= 2021) & (YR <= 2023)), ("2024-26H1", valid & (YR >= 2024)), ("2024-25", valid & (YR >= 2024) & (YR <= 2025)), ("2021-25", valid & (YR >= 2021) & (YR <= 2025))):
    say(f"- {lab}: {f(stats(EU[m]))} 順位 {rank(m)}")

say("\n## 超過 EU − 同日の他 10 ブロック平均（日次ドリフトを引く）・sign-flip p")
for lab, m in (("在 2012-20", valid & (YR <= 2020)), ("在 2014-20", valid & (YR >= 2014) & (YR <= 2020)), ("外 2021-26H1", O), ("近年 2024-26H1", valid & (YR >= 2024))):
    X = XB[m]; ok = np.all(np.isfinite(X), 1); X = X[ok]; n = len(X)
    ex = X[:, eu] - (X.sum(1) - X[:, eu]) / 10; s = stats(ex)
    S = rng.choice([-1.0, 1.0], size=(4000, n)); mp = (S @ ex) / n; tp = mp / (np.sqrt((ex**2).sum()/n - mp**2) / math.sqrt(n - 1)); p = (tp >= s["t"]).mean()
    say(f"- {lab}: 超過 {f(s)}・sign-flip 片側 p {p:.3f}")

say(f"\n実行 {time.time()-T0:.1f} s・seed {SEED}・US100 npz のみ・scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
