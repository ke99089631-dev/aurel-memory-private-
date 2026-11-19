# -*- coding: utf-8 -*-
"""
[cycle54 補助・事後] POST 足（02:15／06:15 UTC）の「隣接 12 足（PRE/POST を除く ±30 分）平均に対する超過」版。
c54 主走の結果を見た後に書いた＝判定には使わない（事前固定 H_REB の脚 (c) は生の P0 足で既に裁定済み）。
目的: P0 2010-16 の ±30 分プロファイルが期間固有の正ドリフト（13 足 t sd 1.44・6/13 |t|≥2）を持つため、
「時間内プラセボ」を生の足で切ると期間ドリフトが混ざる。超過版で P0 が清くなるか・P2 が残るかを**記述**し、
新仮説として前向き事前固定に回す数字を作る。プラセボ時刻（01/03/04/05:15）も同形で印字。
"""
import os, math, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c54b_neighbor_relative.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
T0 = time.time()
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = (r == 0)
t_utc = pd.to_datetime(ts, unit="s", utc=True); wd = t_utc.weekday.to_numpy()
slot = t_utc.hour.to_numpy() * 12 + t_utc.minute.to_numpy() // 5
day = pd.DatetimeIndex(t_utc.tz_localize(None)).normalize()
def S(h, m): return h * 12 + m // 5
SLOTS = list(range(S(0, 30), S(8, 0) + 1)); sel = np.isin(slot, SLOTS) & (wd <= 4)
df = pd.DataFrame({"day": day[sel], "slot": slot[sel], "r": r[sel] * 1e4, "flat": flat[sel].astype(int)})
R = df.pivot_table(index="day", columns="slot", values="r", aggfunc="first").reindex(columns=SLOTS).to_numpy()
F = df.pivot_table(index="day", columns="slot", values="flat", aggfunc="first").reindex(columns=SLOTS).to_numpy()
days = pd.DatetimeIndex(df.pivot_table(index="day", columns="slot", values="r", aggfunc="first").index)
PER = {"P0 開始前": (days >= "2010-01-01") & (days <= "2016-04-18"), "P1 在": (days >= "2016-04-19") & (days <= "2020-12-31"),
       "P2 外": (days >= "2021-01-01"), "近年": (days >= "2024-01-01")}
def st(x):
    x = x[np.isfinite(x)]; n = len(x); m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return m, m / se, n, 2 * se
def excess(h, m):
    c = SLOTS.index(S(h, m)); cols = list(range(c - 6, c + 7)); nb = [j for j in cols if j not in (c - 1, c)]
    ok = np.isfinite(R[:, cols]).all(axis=1) & ((1 - np.nan_to_num(F[:, cols], nan=1)).sum(axis=1) >= 8)
    ex_post = R[:, c] - R[:, nb].mean(axis=1); ex_pre = R[:, c - 1] - R[:, nb].mean(axis=1)
    return ok, ex_pre, ex_post
say(f"# [cycle54b 事後・記述] POST/PRE 足の隣接 12 足平均に対する超過（bp/足）— {time.strftime('%Y-%m-%d %H:%M')}")
for (h, m, lab) in [(2, 15, "AM 02:15 (SGE 10:15)"), (6, 15, "PM 06:15 (SGE 14:15)"), (1, 15, "プラセボ 01:15"), (3, 15, "プラセボ 03:15"), (4, 15, "プラセボ 04:15"), (5, 15, "プラセボ 05:15")]:
    ok, ex_pre, ex_post = excess(h, m); line = []
    for k, msk in PER.items():
        a = st(ex_post[msk & ok]); b = st(ex_pre[msk & ok])
        line.append(f"{k} POST超過 {a[0]:+.3f} (t {a[1]:+.2f}, MDE {a[3]:.3f}) PRE超過 {b[0]:+.3f} (t {b[1]:+.2f})")
    say(f"- {lab}: " + "／".join(line))
    def dt(a, b):
        a = a[np.isfinite(a)]; b = b[np.isfinite(b)]; return (a.mean() - b.mean()) / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    p0 = PER["P0 開始前"] & ok; p1 = PER["P1 在"] & ok; p2 = PER["P2 外"] & ok
    say(f"  - 差 POST超過: P1−P0 {np.nanmean(ex_post[p1]) - np.nanmean(ex_post[p0]):+.3f} (t {dt(ex_post[p1], ex_post[p0]):+.2f})・P2−P0 {np.nanmean(ex_post[p2]) - np.nanmean(ex_post[p0]):+.3f} (t {dt(ex_post[p2], ex_post[p0]):+.2f})・P2−P1 {np.nanmean(ex_post[p2]) - np.nanmean(ex_post[p1]):+.3f} (t {dt(ex_post[p2], ex_post[p1]):+.2f})")
    # yearly POST excess for the two auctions
    if (h, m) in [(2, 15), (6, 15)]:
        yrs = days.year
        say("  - 年別 POST超過 (t): " + " ".join(f"{y} {st(ex_post[(yrs==y)&ok])[0]:+.2f}({st(ex_post[(yrs==y)&ok])[1]:+.1f})" for y in range(2010, 2027) if ((yrs==y)&ok).sum() > 50))
say(f"- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
