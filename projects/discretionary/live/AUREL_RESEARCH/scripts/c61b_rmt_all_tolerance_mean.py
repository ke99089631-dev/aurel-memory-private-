# -*- coding: utf-8 -*-
"""
[cycle61 補 b・記述・判定には未使用] 完全マッチ RMT の「最近傍 1 本」選択が持ち込む機械バイアスの検査。
c61 のプラセボ（R1 最近傍 vs R2 2 番目）が 6/6 セルで F' 負（−0.017〜−0.217・近年 z −2.5）＝最近傍の対照だけ
F' が低い疑い。対照を「許容 |Δv| ≤ 0.02R を満たす候補 **全部の平均**」（選択なし・同条件 M1）に置き換えて
事象 − 対照の F'(a0.5,48)・符号率・水準 D_12 を再計算する（sh1・SL/TP × 3 窓）。候補本数の分布も印字。
入力・関数は c61 と同一。書き込みは data/c61b_rmt_all_tolerance_mean.md のみ。
"""
import os, json, math, time, datetime as dt
import numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'c61b_rmt_all_tolerance_mean.md')
L = []
def P(s=''):
    print(s); L.append(s)
j = json.load(open(os.path.join(DATA, 'refute_c4_scan_paths_2010_2026.json'), encoding='utf-8'))['trades']
et = np.array([t['entry_time'] for t in j], np.int64); hold = np.array([t['hold'] for t in j], np.int64)
side = np.array([1 if t['side'] == 'BUY' else -1 for t in j]); risk = np.array([t['risk'] for t in j], float)
exitk = np.array([t['exit'] for t in j]); year = np.array([t['year'] for t in j])
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_ohlc.npz'))
ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); hi = z['high'].astype(float); lo = z['low'].astype(float)
N = len(ts)
flat = np.zeros(N, bool); flat[1:] = (cl[1:] == cl[:-1]) & (hi[1:] == lo[1:]); cf = np.concatenate([[0], np.cumsum(flat)])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N - 1); return np.where(ts[i] == t, i, -1)
ix = gidx(et + 300 * hold); day_x = np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] // 86400, -1)
base = (ix >= 1) & np.isin(exitk, ['TP', 'SL'])
def fwd_ok(i0, K, sh):
    iend = i0 + sh + K; okr = (i0 >= 1) & (iend < N) & (i0 + sh >= 0)
    a = np.clip(i0 + sh, 0, N); b = np.clip(iend + 1, 0, N); return okr & ((cf[b] - cf[a]) == 0)
def cprime(i0, s, rk, K, sh):
    a = np.clip(i0 + sh, 0, N - 1); b = np.clip(i0 + sh + K, 0, N - 1); return s * (cl[b] - cl[a]) / rk
def fpass(i0, s, rk, K, lev, sh):
    bas = cl[np.clip(i0 + sh, 0, N - 1)]
    idx = np.clip(i0[:, None] + sh + np.arange(1, K + 1)[None, :], 0, N - 1)
    path = s[:, None] * (cl[idx] - bas[:, None]) / rk[:, None]
    up = path >= lev; dn = path <= -lev
    fu = np.where(up.any(1), up.argmax(1), K + 5); fd = np.where(dn.any(1), dn.argmax(1), K + 5)
    r = np.zeros(len(i0), float); r[fu < fd] = 1; r[fd < fu] = -1; return r
def cl_t(x, g):
    x = np.asarray(x, float); n = len(x)
    if n < 3: return float('nan'), float('nan'), float('nan')
    mu = x.mean(); r = x - mu; _, inv = np.unique(g, return_inverse=True); gs = np.bincount(inv, weights=r)
    se = math.sqrt((gs ** 2).sum()) / n; return mu, se, (mu / se if se > 0 else float('nan'))
dst = np.zeros(N, bool)
for y in range(2009, 2028):
    d = dt.date(y, 3, 1); fs = d + dt.timedelta(days=(6 - d.weekday()) % 7); ss = fs + dt.timedelta(days=7)
    n = dt.date(y, 11, 1); fn = n + dt.timedelta(days=(6 - n.weekday()) % 7)
    t0 = int(dt.datetime(ss.year, ss.month, ss.day, 7, tzinfo=dt.timezone.utc).timestamp())
    t1 = int(dt.datetime(fn.year, fn.month, fn.day, 6, tzinfo=dt.timezone.utc).timestamp())
    dst |= (ts >= t0) & (ts < t1)
WINS = [('在 2010-20', (year >= 2010) & (year <= 2020)), ('外 2021-26H1', year >= 2021), ('近年 2024-26H1', year >= 2024)]
OFFS = [sg * 7 * k for k in range(1, 27) for sg in (1, -1)]; TOL_V = 0.02; sh = 1
def v_of(idx, s, rk):
    a = np.clip(idx, 1, N - 1); return s * (cl[a] - cl[a - 1]) / rk
P(f'# [cycle61 補 b] 対照 = 許容内候補 全部の平均（選択なし）  {dt.datetime.now():%Y-%m-%d %H:%M}')
for arm in ['SL', 'TP']:
    for wn, wm in WINS:
        m = base & (exitk == arm) & wm & fwd_ok(ix, 48, sh) & (~flat[np.clip(ix, 0, N - 1)])
        i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]; vE = v_of(i0, s, rk)
        sumF = np.zeros(len(i0)); sumS = np.zeros(len(i0)); sumL = np.zeros(len(i0)); cnt = np.zeros(len(i0)); sumV = np.zeros(len(i0))
        # nearest too (to reproduce c61 M1 on the same subsample)
        bd = np.full(len(i0), np.inf); bI = np.full(len(i0), -1, np.int64)
        for d in OFFS:
            cand = gidx(ts[i0] + d * 86400)
            okc = (cand >= 1) & fwd_ok(cand, 48, sh) & (~flat[np.clip(cand, 0, N - 1)]) & (dst[np.clip(cand, 0, N - 1)] == dst[i0])
            v = v_of(cand, s, rk); dv = np.abs(v - vE); cond = okc & (dv <= TOL_V)
            cc = np.where(cond, cand, 1)
            f = fpass(cc, s, rk, 48, 0.5, sh); c12 = cprime(cc, s, rk, 12, sh)
            sumF += np.where(cond, f, 0); sumS += np.where(cond, (c12 > 0).astype(float), 0); sumL += np.where(cond, c12, 0); sumV += np.where(cond, v, 0); cnt += cond
            dd = np.where(cond, dv, np.inf); upd = dd < bd; bd = np.where(upd, dd, bd); bI = np.where(upd, cand, bI)
        ok = cnt >= 1
        fE = fpass(i0[ok], s[ok], rk[ok], 48, 0.5, sh); cE = cprime(i0[ok], s[ok], rk[ok], 12, sh)
        fA = sumF[ok] / cnt[ok]; sA = sumS[ok] / cnt[ok]; lA = sumL[ok] / cnt[ok]
        muF, seF, zF = cl_t(fE - fA, g[ok]); muS, seS, zS = cl_t((cE > 0) - sA, g[ok]); muL, seL, tL = cl_t(cE - lA, g[ok])
        fR1 = fpass(bI[ok], s[ok], rk[ok], 48, 0.5, sh); mu1, se1, z1 = cl_t(fE - fR1, g[ok])
        # also: nearest vs all-mean (machinery bias)
        muB, seB, zB = cl_t(fR1 - fA, g[ok])
        q = np.percentile(cnt[ok], [10, 50, 90])
        P(f"  - {arm} {wn}: n {int(ok.sum())}/{len(i0)} | 候補本数 p10/50/90 {q[0]:.0f}/{q[1]:.0f}/{q[2]:.0f} | 較正 v 事象 {vE[ok].mean():+.3f} 全平均 {(sumV[ok]/cnt[ok]).mean():+.3f}")
        P(f"      事象 F' {fE.mean():+.4f} | 対照: 最近傍 R1 {fR1.mean():+.4f} / 全平均 {fA.mean():+.4f} | **D(事象−全平均) F' {muF:+.4f} (z {zF:+.2f} MDE {2*seF:.4f})** vs D(事象−R1) {mu1:+.4f} (z {z1:+.2f}) | 機械バイアス R1−全平均 {muB:+.4f} (z {zB:+.2f}) | 符号率 D {muS*100:+.2f} pp (z {zS:+.2f}) | 水準 D_12 {muL:+.4f} (t {tL:+.2f})")
P(f'\n実行 {time.time()-T0:.1f}s  乱数未使用・外部通信なし・MT5 なし')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L)); print('written', OUT)
