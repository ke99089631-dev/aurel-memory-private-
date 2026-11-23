# -*- coding: utf-8 -*-
"""
[REFUTE 補 2026-11-23] refute_c60_postjump.py の A2 記述サブ結果の定量（**新しい判定は作らない・記述のみ**）。
本体 A2 で見つかった事実: c60 の「在 +0.587σ → 外 −0.131σ＝**外で符号反転**（だからレジーム優位でもない）」は
**σ 単位（比推定子 mean(D_i/σ_i)）の顔**で、bp 単位（mean(D_i)）では 在 +3.25 bp／外 **+2.06 bp**＝同符号だった。
→ ここで 3 窓 × {σ, bp, USD} を対で印字し、さらに **C1 判定の頑健性**（双子 2/4/8 本 × raw/winsor±3σ）を格子で出す。
look-ahead 無し（本体と同一の統計）・乱数未使用・外部通信なし・多年 scan なし。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
T0 = time.time(); HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'refute_c60_postjump_b.md'); L = []
def P(s=''):
    print(s); L.append(s)
ev = pd.read_csv(os.path.join(DATA, 'c45_jumps_5sigma_declustered.csv'))
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_close.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); N = len(ts)
lc = np.log(cl); r = np.r_[np.nan, np.diff(lc)] * 1e4; flat = ~(np.isfinite(r) & (r != 0))
NY = ZoneInfo('America/New_York'); tny = pd.to_datetime(ts, unit='s', utc=True).tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); brk = (hr == 17) | ((hr == 18) & (mn < 10))
cf = np.concatenate([[0], np.cumsum(flat.astype(np.int64))]); cb = np.concatenate([[0], np.cumsum(brk.astype(np.int64))])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i] == t, i, -1)
i0 = gidx(ev.ts.to_numpy(np.int64)); s = np.sign(ev.r_bp.to_numpy()); sig = ev.sigma_bp.to_numpy(float)
yr = pd.to_datetime(ev.et_date).dt.year.to_numpy(); etd = ev.et_date.to_numpy(); cls = ev.cls.to_numpy()
WIN = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}
SH = 1
def win_ok(i, K):
    a = i + SH; b = i + SH + K; inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cb[bb] - cb[aa]) == 0) & ((cf[bb] - cf[aa]) <= max(1, int(0.10 * (K + 1))))
def Craw(i, K):  # bp 単位（σ で割らない）
    a = np.clip(i + SH, 0, N-1); b = np.clip(i + SH + K, 0, N-1); return s * (lc[b] - lc[a]) * 1e4
def paired(K, days=(-7, 7), unit='sigma'):
    okE = win_ok(i0, K); CE = Craw(i0, K) / (sig if unit == 'sigma' else 1.0)
    CT = np.zeros(len(ev)); nT = np.zeros(len(ev), int)
    for d in days:
        it = gidx(ev.ts.to_numpy(np.int64) + d * 86400)
        rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
        okT = win_ok(it, K) & (it >= 0) & np.isfinite(rr) & (rr < 4 * sig)
        c = Craw(it, K) / (sig if unit == 'sigma' else 1.0)
        CT += np.where(okT, c, 0.0); nT += okT.astype(int)
    ok = okE & (nT >= 1)
    return CE - CT / np.maximum(nT, 1), ok
def clus(x, g):
    n = len(x); m = x.mean(); e = x - m; gg = pd.Series(e).groupby(g).sum()
    return m, math.sqrt(float((gg**2).sum())) / n, n, len(gg)
P(f'# [REFUTE 補] c60 の「外で符号反転」の単位依存性・C1 判定の頑健性  {dt.datetime.now():%Y-%m-%d %H:%M}')
P('\n## 1. 単位ごとの UJ D_12（アンカー 1 本ずらし・双子 ±7 対・ET 日クラスタ）')
P('| 窓 | σ 単位 mean(D/σ) | bp 単位 mean(D) | USD/本 | 価格中央 | σ_trail 中央 |'); P('|---|---|---|---|---|---|')
for w, wm in WIN.items():
    Ds, ok = paired(12, unit='sigma'); Db, _ = paired(12, unit='bp')
    m = ok & wm & (cls == 'UJ')
    a1 = clus(Ds[m], etd[m]); a2 = clus(Db[m], etd[m]); px = float(np.median(cl[i0[m]]))
    P(f'| {w} | {a1[0]:+.3f}σ (t {a1[0]/a1[1]:+.2f}・MDE {2*a1[1]:.3f}) | {a2[0]:+.2f} bp (t {a2[0]/a2[1]:+.2f}・MDE {2*a2[1]:.2f}) | {a2[0]/1e4*px:+.4f} | {px:.0f} | {np.median(sig[m]):.2f} bp |')
P('\n## 2. K プロファイル（bp 単位・t）— c60 の表は σ 単位のみ')
KS = [1, 3, 6, 12, 24, 48]
P('| 窓 | ' + ' | '.join(f'K{K}' for K in KS) + ' |'); P('|---|' + '---|' * len(KS))
for w, wm in WIN.items():
    cells = []
    for K in KS:
        Db, ok = paired(K, unit='bp'); m = ok & wm & (cls == 'UJ'); a = clus(Db[m], etd[m])
        cells.append(f'{a[0]:+.2f} ({a[0]/a[1]:+.1f})')
    P(f'| {w} | ' + ' | '.join(cells) + ' |')
P('\n## 3. C1 判定の頑健性（在レグ: D ≥ +0.20σ ∧ t ≥ +2.5／外レグ: D > 0 ∧ t ≥ +1.5）')
P('| 設計 | 在 D σ | 在 t | 在レグ | 外 D σ | 外 t | 外レグ | C1 |'); P('|---|---|---|---|---|---|---|---|')
for nm, days in [('双子 2 本（c60）', (-7, 7)), ('双子 4 本', (-14, -7, 7, 14)), ('双子 8 本', (-28, -21, -14, -7, 7, 14, 21, 28))]:
    for est in ['raw', 'winsor±3σ']:
        Ds, ok = paired(12, days=days, unit='sigma')
        out = []
        for w in ['在 2010-20', '外 2021-26H1']:
            m = ok & WIN[w] & (cls == 'UJ'); x = Ds[m]
            if est == 'winsor±3σ':
                xx = np.clip(x, -3, 3); a0 = clus(xx, etd[m]); att = (np.mean(xx) - np.mean(np.clip(x - 0.20, -3, 3))) / 0.20
                mm, se = a0[0] / att, a0[1] / att
            else:
                a0 = clus(x, etd[m]); mm, se = a0[0], a0[1]
            out.append((mm, mm / se))
        legi = (out[0][0] >= 0.20) and (out[0][1] >= 2.5); lego = (out[1][0] > 0) and (out[1][1] >= 1.5)
        P(f'| {nm}・{est} | {out[0][0]:+.3f} | {out[0][1]:+.2f} | {"PASS" if legi else "×"} | {out[1][0]:+.3f} | {out[1][1]:+.2f} | {"PASS" if lego else "×"} | {"H_CONT PASS" if (legi and lego) else "null"} |')
P(f'\n実行 {time.time()-T0:.1f}s')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
