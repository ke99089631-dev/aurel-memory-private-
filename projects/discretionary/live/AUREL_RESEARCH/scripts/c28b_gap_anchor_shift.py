# -*- coding: utf-8 -*-
"""
[cycle28 補足 b・事後・記述] 再開直後の bid 人工物（スプレッド拡大で bid が沈む・口座ログでは 18:00–18:10 ET が閉場値 0.21）を避けるため、
アンカーを 18:00 足終値（18:05 既知）→ 18:10 足終値（18:15 既知）に 2 本ずらして同じ先着判定（N=72・g_min 2 bp）。
c28 主結果の DAILY 外 小|G| (t 2.09) が人工物なら消え、1〜6 時間の実際の戻り傾向なら残る。参照は 16:50 足終値のまま。
WKND・DAILY とも。D̄ と上下・大小分割を印字。scan 無し・MT5 無し・外部通信無し。
"""
import os, time, math, io
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
MAC = os.path.join(ROOT, "data", "macro"); OUT = os.path.join(ROOT, "data", "c28b_gap_anchor_shift.md")
T0 = time.time(); buf = io.StringIO()
def say(s=""):
    print(s, flush=True); buf.write(s + "\n")
W = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64); hi = z["high"]; lo = z["low"]; cl = z["close"]
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = r == 0
t_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert("America/New_York")
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)
N = 72; SH = 2
def events(anchor0, ref):
    a = anchor0; ok = (ref >= 0) & (a > 0) & (a + SH + N < len(ts)) & (ts[np.clip(a + SH + N, 0, len(ts) - 1)] == ts[a] + 300 * (SH + N))
    brk = np.column_stack([idx_at(ts[a] - 300 * j) for j in range(1, 13)]); ok &= np.all(brk >= 0, axis=1)
    clean = np.zeros(len(a), bool); clean[ok] = np.all(flat[brk[ok]], axis=1)
    k = ok & clean; a = a[k] + SH; ref = ref[k]
    G = (lc[a] - lc[ref]) * 1e4; big = np.abs(G) >= 2.0
    return a[big], G[big]
def fp(a, G):
    s = np.sign(G); ag = np.abs(G) / 1e4; J = a[:, None] + np.arange(1, N + 1)[None, :]
    lh = np.log(hi[J]) - lc[a][:, None]; ll = np.log(lo[J]) - lc[a][:, None]
    fh = np.where(s[:, None] > 0, ll <= -ag[:, None], lh >= ag[:, None]); ch = np.where(s[:, None] > 0, lh >= ag[:, None], ll <= -ag[:, None])
    kf = np.where(fh.any(1), fh.argmax(1), N + 1); kc = np.where(ch.any(1), ch.argmax(1), N + 1)
    D = np.zeros(len(a)); D[kf < kc] = 1; D[kc < kf] = -1; return D
def ms(x):
    x = np.asarray(x, float); n = len(x); return (x.mean(), x.std(ddof=1) / math.sqrt(n), n) if n > 1 else (np.nan, np.nan, n)
say(f"# c28b アンカーを 18:10 足終値（+2 本）にずらした先着判定（N=72・事後・記述）— {pd.Timestamp.now():%Y-%m-%d %H:%M}")
iS = np.where((wd == 6) & (h == 18) & (mi == 0))[0]
iF = np.where((wd == 4) & (h == 16) & (mi == 50))[0]; pF = np.searchsorted(iF, iS) - 1
refS = np.where(pF >= 0, iF[np.clip(pF, 0, len(iF) - 1)], -1); refS = np.where((refS >= 0) & (ts[iS] - ts[np.clip(refS, 0, len(ts) - 1)] <= 3 * 86400), refS, -1)
iD = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]; refD = idx_at(ts[iD] - 70 * 60)
for lab, (a, G) in [("WKND", events(iS, refS)), ("DAILY", events(iD, refD))]:
    D = fp(a, G); yy = yr[a]; med = np.median(np.abs(G[yy <= 2020]))
    say(f"- {lab}: n {len(a)}・|G| 中央値 {np.median(np.abs(G)):.1f} bp（18:00 終値版より {'大' if lab=='WKND' else ''}）・大小閾値 {med:.1f} bp")
    for wn, (y0, y1) in W.items():
        m = (yy >= y0) & (yy <= y1); parts = []
        for nm, sel in [("全", np.ones(len(a), bool)), ("小|G|", np.abs(G) < med), ("大|G|", np.abs(G) >= med), ("上", G > 0), ("下", G < 0)]:
            mm = m & sel; mean, se, n = ms(D[mm]); parts.append(f"{nm} **{mean:+.3f}** (t {mean/se:+.2f}, n {n})" if n >= 10 else f"{nm} n{n}")
        say(f"  - {wn}: " + "／".join(parts))
say(f"- 実行時間 {time.time()-T0:.1f} s")
with open(OUT, "w", encoding="utf-8") as f: f.write(buf.getvalue())
print("->", OUT)
