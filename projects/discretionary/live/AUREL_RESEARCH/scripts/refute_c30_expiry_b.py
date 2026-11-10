# -*- coding: utf-8 -*-
"""
[REFUTE c30 補足 b・事後・記述] 満期日の圧縮は満期日固有か、月末前の「静かな帯」か。
  (1) 月内ペア: log RV_LATE(e) − mean(log RV_LATE(e−1), log RV_LATE(e+1))（営業日）・t と符号検定。ピン留めなら <0。
      同じく e − (e−1) のみ（満期に向けて積み上がるなら <0）。
  (2) 月末までの営業日数 k（0 = 最終営業日 … −10）別の mean log RV_LATE − 窓平均（在／外）と、k=−3（4th last）の位置。
      満期日集合は k=−3 を主、金曜/休日前倒しで k=−4。
  (3) PRE/POST も同じ曲線。
入力: XAU_m5_close.npz のみ。出力: data/refute_c30_expiry_b.md。
"""
import os, math, time, datetime as dt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c30_expiry_b.md"); L = []; T0 = time.time()
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c30 補足 b・事後] 満期日 vs 隣接日・月末までの営業日数曲線 — {time.strftime('%Y-%m-%d %H:%M')}")
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d
HOL = set()
for y in range(2009, 2028):
    for h in [observed(dt.date(y, 1, 1), sat_to_fri=False), nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3),
              easter(y) - dt.timedelta(days=2), last_weekday(y, 5, 0), observed(dt.date(y, 7, 4)),
              nth_weekday(y, 9, 0, 1), nth_weekday(y, 11, 3, 4), observed(dt.date(y, 12, 25))] + \
             ([observed(dt.date(y, 6, 19))] if y >= 2022 else []):
        if h is not None: HOL.add(h)
d0 = dt.date(2009, 11, 1); d1 = dt.date(2026, 12, 31)
BDAYS = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]
BDAYS = [d for d in BDAYS if d.weekday() < 5 and d not in HOL]
BORD = np.array([d.toordinal() for d in BDAYS]); BIDX = {o: i for i, o in enumerate(BORD)}
def expiry_of_month(y, m):
    bm = [d for d in BDAYS if d.year == y and d.month == m]; e = bm[-4]
    if e.weekday() == 4 or (e + dt.timedelta(days=1)) in HOL: e = BDAYS[BIDX[e.toordinal()] - 1]
    return e
EXP = [expiry_of_month(y, m) for y in range(2010, 2027) for m in range(1, 13) if (y, m) <= (2026, 6)]
EXP_ORD = np.array([e.toordinal() for e in EXP])
# 月末までの営業日数 k（0 = 最終営業日）
K = {}
for y in range(2010, 2027):
    for m in range(1, 13):
        bm = [d.toordinal() for d in BDAYS if d.year == y and d.month == m]
        for j, o in enumerate(bm): K[o] = j - (len(bm) - 1)
z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
flat = np.r_[True, P_ALL[1:] == P_ALL[:-1]]
et_all = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
etv = et_all.values; dayv = etv.astype("datetime64[D]")
ord_all = dayv.astype("int64") + dt.date(1970, 1, 1).toordinal(); tod_all = ((etv - dayv) / np.timedelta64(1, "m")).astype(int)
keep = ~flat; P = P_ALL[keep]; ordd = ord_all[keep]; tod = tod_all[keep]; logP = np.log(P)
def day_rv(lo, hi):
    m = (tod >= lo) & (tod < hi); idx = np.flatnonzero(m)
    same = (ordd[idx[1:]] == ordd[idx[:-1]]) & (idx[1:] == idx[:-1] + 1)
    r2 = (logP[idx[1:]] - logP[idx[:-1]]) ** 2; d = ordd[idx[1:]][same]; r2 = r2[same]
    ud, inv = np.unique(d, return_inverse=True); return dict(zip(ud.tolist(), np.bincount(inv, weights=r2, minlength=len(ud)).tolist()))
RV = {k: day_rv(*v) for k, v in {"PRE": (480, 810), "LATE": (690, 810), "POST": (810, 1016)}.items()}
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
say(f"- 満期日の k 構成: " + " ".join(f"k={k}:{sum(1 for o in EXP_ORD if K.get(int(o))==k)}" for k in (-5, -4, -3, -2)))
for wn, (lo, hi) in WIN.items():
    say(f"\n## {wn}")
    for key in ("LATE", "PRE", "POST"):
        # (1) 月内ペア
        d_pair = []; d_prev = []
        for o in EXP_ORD:
            e = dt.date.fromordinal(int(o))
            if not (lo <= e.year <= hi): continue
            i = BIDX[int(o)]; om, op = int(BORD[i - 1]), int(BORD[i + 1])
            v0, vm, vp = RV[key].get(int(o)), RV[key].get(om), RV[key].get(op)
            if v0 and vm and vp and v0 > 0 and vm > 0 and vp > 0:
                d_pair.append(math.log(v0) - 0.5 * (math.log(vm) + math.log(vp))); d_prev.append(math.log(v0) - math.log(vm))
        d_pair = np.array(d_pair); d_prev = np.array(d_prev)
        tp = d_pair.mean() / (d_pair.std(ddof=1) / math.sqrt(len(d_pair))); tv = d_prev.mean() / (d_prev.std(ddof=1) / math.sqrt(len(d_prev)))
        say(f"- {key} 月内ペア e − mean(e−1,e+1): 平均 {d_pair.mean():+.3f}（比 {math.exp(d_pair.mean()):.3f}）t {tp:+.2f}・負の割合 {(d_pair<0).mean()*100:.0f}%（n {len(d_pair)}）；e − (e−1): {d_prev.mean():+.3f} t {tv:+.2f}・負 {(d_prev<0).mean()*100:.0f}%")
    # (2) k 曲線
    for key in ("LATE", "PRE", "POST"):
        lv = {}
        for o, v in RV[key].items():
            e = dt.date.fromordinal(int(o))
            if lo <= e.year <= hi and v > 0 and int(o) in K: lv.setdefault(K[int(o)], []).append(math.log(v))
        allv = np.concatenate([np.array(x) for x in lv.values()]); mu = allv.mean()
        line = f"- {key} 月末までの営業日数 k 別 mean log RV − 窓平均（se）: "
        for k in range(-10, 1):
            x = np.array(lv.get(k, [])); line += f"k{k:+d}:{x.mean()-mu:+.2f}({x.std(ddof=1)/math.sqrt(len(x)):.2f}) " if len(x) > 2 else f"k{k:+d}:nan "
        # 月初 k=+1..+3（翌月の最初の営業日）も
        lv2 = {}
        for o, v in RV[key].items():
            e = dt.date.fromordinal(int(o))
            if lo <= e.year <= hi and v > 0 and int(o) in BIDX:
                bm = [d for d in BDAYS if d.year == e.year and d.month == e.month]; j = bm.index(e)
                if j < 3: lv2.setdefault(j + 1, []).append(math.log(v))
        for k in (1, 2, 3):
            x = np.array(lv2.get(k, [])); line += f"月初{k}:{x.mean()-mu:+.2f}({x.std(ddof=1)/math.sqrt(len(x)):.2f}) "
        say(line)
say(f"\n実行時間 {time.time()-T0:.1f} s")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
print("written", OUT)
