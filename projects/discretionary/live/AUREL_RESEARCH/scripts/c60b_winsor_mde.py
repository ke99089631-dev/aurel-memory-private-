# -*- coding: utf-8 -*-
"""
[cycle60 補 2026-11-23] 方法論候補 92（反証 11-23）の適用: 裾の重い系列の主セルに winsor 推定子と減衰補正 MDE（2·se/a）を併記。
対象 = c60 主セル UJ D'_12（σ 単位・双子対差・ET 日クラスタ）。推定子: raw／winsor ±10σ／winsor ±5σ／事後ボラ標準化（窓 12 本の RMS で割る）。
a = −0.20σ 注入の回収率（winsor は注入を部分的に切る）。事前の予測: winsor で se は 20〜40% 縮むが 0.20σ には届かない。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
T0 = time.time(); HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'c60b_winsor_mde.md'); L = []
def P(s=''):
    print(s); L.append(s)
ev = pd.read_csv(os.path.join(DATA, 'c45_jumps_5sigma_declustered.csv'))
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_close.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); N = len(ts)
lc = np.log(cl); r = np.r_[np.nan, np.diff(lc)] * 1e4; flat = ~(np.isfinite(r) & (r != 0))
tny = pd.to_datetime(ts, unit='s', utc=True).tz_convert(ZoneInfo('America/New_York')); hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy()
brk = (hr == 17) | ((hr == 18) & (mn < 10)); cf = np.concatenate([[0], np.cumsum(flat.astype(np.int64))]); cb = np.concatenate([[0], np.cumsum(brk.astype(np.int64))])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i] == t, i, -1)
i0 = gidx(ev.ts.to_numpy(np.int64)); s = np.sign(ev.r_bp.to_numpy()); sig = ev.sigma_bp.to_numpy(float)
yr = pd.to_datetime(ev.et_date).dt.year.to_numpy(); etd = ev.et_date.to_numpy(); cls = ev.cls.to_numpy()
K, SH = 12, 1
def win_ok(i):
    a = i + SH; b = i + SH + K; inr = (i >= 0) & (b < N) & (a >= 1); aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cb[bb] - cb[aa]) == 0) & ((cf[bb] - cf[aa]) <= 1)
def Cm(i):
    a = np.clip(i + SH, 0, N-1); b = np.clip(i + SH + K, 0, N-1); return s * (lc[b] - lc[a]) * 1e4 / sig
def rms_post(i):
    out = np.zeros(len(i))
    for k in range(1, K + 1):
        a = np.clip(i + SH + k, 0, N-1); out += np.nan_to_num(r[a])**2
    return np.sqrt(out / K)
tw = [gidx(ev.ts.to_numpy(np.int64) + d * 86400) for d in (-7, 7)]
okE = win_ok(i0); CE = Cm(i0); CT = np.zeros(len(ev)); nT = np.zeros(len(ev))
for it in tw:
    rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf); okT = win_ok(it) & np.isfinite(rr) & (rr < 4 * sig)
    CT += np.where(okT, Cm(it), 0.0); nT += okT
ok = okE & (nT >= 1); D = CE - CT / np.maximum(nT, 1)
rp = rms_post(i0); Dv = D * sig / np.maximum(rp, 1e-9)  # 事後ボラ標準化（事象側の 12 本 RMS で割る）
def clus(x, g):
    n = len(x); m = x.mean(); e = x - m; se = math.sqrt(float((pd.Series(e).groupby(g).sum()**2).sum())) / n; return m, se, n
P(f'# c60b winsor / 減衰補正 MDE（UJ D\'_12）  {dt.datetime.now():%Y-%m-%d %H:%M}')
P('| 窓 | 推定子 | D | se | t | 生 MDE 2se | 回収率 a（−0.20σ 注入） | 実効 MDE 2se/a | 事象 sd |'); P('|---|---|---|---|---|---|---|---|---|')
for w, wm in [('在 2010-20', yr <= 2020), ('外 2021-26H1', yr >= 2021), ('近年 2024-26H1', yr >= 2024)]:
    m = ok & wm & (cls == 'UJ'); x = D[m]; g = etd[m]
    ests = {'raw': (lambda v: v), 'winsor ±10σ': (lambda v: np.clip(v, -10, 10)), 'winsor ±5σ': (lambda v: np.clip(v, -5, 5)), 'winsor ±3σ': (lambda v: np.clip(v, -3, 3))}
    for nm, f in ests.items():
        mm, se, n = clus(f(x), g); mi, _, _ = clus(f(x - 0.20), g); a = (mm - mi) / 0.20
        P(f'| {w} | {nm} | {mm:+.3f} | {se:.3f} | {mm/se:+.2f} | {2*se:.3f} | {a:.2f} | {2*se/max(a,1e-9):.3f} | {np.std(f(x)):.2f} |')
    xv = Dv[m]; mm, se, n = clus(xv, g); mi, _, _ = clus(xv - 0.20 * sig[m] / np.maximum(rp[m], 1e-9), g); a = (mm - mi) / 0.20
    P(f'| {w} | 事後ボラ標準化（×σ_post/σ_trail 中央値 {np.median(rp[m]/sig[m]):.2f}） | {mm:+.3f} | {se:.3f} | {mm/se:+.2f} | {2*se:.3f} | {a:.2f} | {2*se/max(a,1e-9):.3f} | {np.std(xv):.2f} |')
    q = np.quantile(x, [0.01, 0.05, 0.5, 0.95, 0.99]); P(f'  - {w} D 分位 1/5/50/95/99%: ' + ' '.join(f'{v:+.1f}' for v in q) + f'σ・n {n}・必要倍率 (MDE_raw/0.20)² = {(2*clus(x,g)[1]/0.20)**2:.0f}×')
P(f'実行 {time.time()-T0:.1f}s'); open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
