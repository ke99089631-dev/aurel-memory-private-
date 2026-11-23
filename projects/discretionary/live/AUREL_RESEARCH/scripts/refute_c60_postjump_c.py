# -*- coding: utf-8 -*-
"""
[REFUTE 補 c 2026-11-23] **事後・記述のみ（判定には使わない）**。
本反証の「最も重大な反証（自分への）」の診断: A1 の LB 補正（est/a・se/a）は **位置ずらしモデル**を仮定している。
もし「ジャンプ後の継続」が真に**裾だけの現象**（少数が大きく続き大多数は無反応）なら、winsor/中央値は構造的に無力で、
a で割っても検出力は戻らない＝「ロバスト LB −0.31σ」は平均の下限ではなく**別の汎関数の下限**にすぎない（T1 の破りは言い方の問題に縮む）。
逆に移動が全分位に一様なら位置ずらしであり、ロバスト推定子は同じ母数を測っている＝T1 の破りは実質的。
診断 = **ずらし関数 Q_event(p) − Q_twin(p)**（p = 5/10/25/50/75/90/95%・σ 単位・UJ 腕・アンカー 1 本ずらし・双子は有効な全本をプール）。
位置ずらしなら全 p でほぼ一定、裾だけなら上側 p に集中。クラスタブートストラップ（B=400・ET 日・seed 20261123）で se。
事前固定の外なので**判定は変えない**（T1 の判定文に前提として明記する）。乱数 = ブートストラップのみ・外部通信なし。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
T0 = time.time(); SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'refute_c60_postjump_c.md'); L = []
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
K, SH = 12, 1
def win_ok(i):
    a = i + SH; b = i + SH + K; inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cb[bb] - cb[aa]) == 0) & ((cf[bb] - cf[aa]) <= 1)
def Cm(i):
    a = np.clip(i + SH, 0, N-1); b = np.clip(i + SH + K, 0, N-1); return s * (lc[b] - lc[a]) * 1e4 / sig
PS = [5, 10, 25, 50, 75, 90, 95]
P(f'# [REFUTE 補 c・事後記述] ずらし関数 Q_event(p) − Q_twin(p)（UJ・D\'_12 の構成要素・σ 単位）  {dt.datetime.now():%Y-%m-%d %H:%M}')
P('位置ずらし（全 p で一定）なら A1 のロバスト LB は平均の下限として有効／上側 p に集中なら裾だけの現象＝ロバスト推定子は無力。')
P('\n| 窓 | n_event | n_twin | ' + ' | '.join(f'p{p}' for p in PS) + ' | 平均差 |')
P('|---|---|---|' + '---|' * (len(PS) + 1))
okE = win_ok(i0); CE = Cm(i0)
twin_list = []
for d in (-7, 7):
    it = gidx(ev.ts.to_numpy(np.int64) + d * 86400)
    rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
    okT = win_ok(it) & (it >= 0) & np.isfinite(rr) & (rr < 4 * sig)
    twin_list.append((Cm(it), okT))
for w, wm in [('在 2010-20', yr <= 2020), ('外 2021-26H1', yr >= 2021)]:
    base = okE & wm & (cls == 'UJ')
    xe = CE[base]; ge = etd[base]
    xt = np.concatenate([c[okT & wm & (cls == 'UJ')] for c, okT in twin_list])
    gt = np.concatenate([etd[okT & wm & (cls == 'UJ')] for c, okT in twin_list])
    shift = [np.percentile(xe, p) - np.percentile(xt, p) for p in PS]
    # cluster bootstrap se（事象側・対照側それぞれ ET 日クラスタで再抽出）
    rr2 = np.random.default_rng(SEED)
    def boot_idx(g, B):
        code, uq = pd.factorize(g); G = len(uq); order = np.argsort(code, kind='stable')
        cnt = np.bincount(code, minlength=G); st = np.r_[0, np.cumsum(cnt)[:-1]]
        return [np.concatenate([order[st[p]:st[p]+cnt[p]] for p in rr2.integers(0, G, G)]) for _ in range(B)]
    B = 400; ie = boot_idx(ge, B); it_ = boot_idx(gt, B)
    bs = np.array([[np.percentile(xe[a], p) - np.percentile(xt[b], p) for p in PS] for a, b in zip(ie, it_)])
    se = bs.std(axis=0, ddof=1)
    P(f'| {w} | {len(xe)} | {len(xt)} | ' + ' | '.join(f'{v:+.2f} ({v/s2:+.1f})' for v, s2 in zip(shift, se)) + f' | {xe.mean()-xt.mean():+.3f} |')
    P(f'  - 事象 分位: ' + ' '.join(f'p{p} {np.percentile(xe,p):+.2f}' for p in PS) + f'・sd {xe.std():.2f}')
    P(f'  - 双子 分位: ' + ' '.join(f'p{p} {np.percentile(xt,p):+.2f}' for p in PS) + f'・sd {xt.std():.2f}')
    up = shift[-1] - shift[0]
    P(f'  - 上側−下側 ずらし差（p95 − p5）= {up:+.2f}σ（位置ずらしなら ≈0・裾だけなら大）・中央のずらし p50 {shift[3]:+.2f}σ')
P(f'\n実行 {time.time()-T0:.1f}s')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
