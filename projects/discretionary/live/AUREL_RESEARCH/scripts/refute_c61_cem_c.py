# -*- coding: utf-8 -*-
"""
[反証レーン・補 c] 2026-11-23  seed 20261123
補 b の T7（回帰調整対照）が c61 残差を **+0.0962 → +0.0428 (cl-se 0.0167 z +2.56 MDE 0.0333・共通サポート 99.6%)** まで
削ったが消さなかった。残差が本物かを決めるのは次の 3 点。**自分の T7 自身を攻撃する placebo を含む。**

--- 事前固定（実行前に書いた） ---
対照行 = v ±0.02R 以内・取引足（決着/建玉）除外・同 UTC 時刻・同 DST・|d| 2..182 日・trail_ok・前向き K 本 非 flat。
回帰調整: 対照行で f ~ 1 + v + rng + cloc + wick + trail + trail² を OLS → 事象の自分の共変量で f̂ を予測 → D_adj = mean(f_E − f̂)・決着日クラスタ SE。
**モデルは必ず「その窓の対照行」だけで推定**（窓をまたいだ外挿をしない）。

T9（部分窓の安定性）: SL 腕を 2010-12 / 2013-15 / 2016-18 / 2019-20 / 2021-23 / 2024-26H1 の 6 窓で D_adj。
  **broken（在の残差は 1 つの時代の記述）** ⇔ 在側 4 窓のうち D_adj ≥ +0.04 を満たすのが 1 窓以下、
  または在側で符号が揃わない（2 窓以上が負）。**survived** ⇔ 在側 4 窓すべて D_adj > 0 かつ 3 窓以上で z ≥ 1.5。
T12（地平 K の頑健性・look-ahead 検査）: K = 12 / 24 / 48 本（fwd_ok も K に合わせる＝前向き非 flat の要求を緩める）で D_adj。
  fwd_ok は「決着後 K 本が連続取引だった」という**未来条件づけ**なので、K を縮めれば事象集合は広がる。
  **broken** ⇔ K=12 または 24 で D_adj < +0.02 ∧ MDE ≤ 0.04。**survived** ⇔ 3 つの K すべてで D_adj > +0.02 ∧ z ≥ 2.0。
T11（**自分の T7 への placebo**・モデル誤特定検査）: 対照行の中から、事象の共変量平均ベクトルに（標準化距離で）最も近い
  n_event 行を**擬似事象**として抜き、**残りの対照行だけ**でモデルを推定し D_adj を計算。どこにも取引は無いので 0 のはず。
  **T7 無効（+0.0428 はモデル誤特定）** ⇔ |D_adj_placebo| ≥ 0.6 × 0.0428 = 0.026。
  **T7 有効** ⇔ |D_adj_placebo| < 0.015 ∧ そのセルの MDE ≤ 0.04。
D2: 窓別・16 年一括なし。副作用: 書き込みは data/refute_c61_cem_c.md のみ。発注なし・MT5 なし・外部通信なし。
"""
import os, json, math, time, datetime as dt
import numpy as np

T0 = time.time(); SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'refute_c61_cem_c.md')
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
flat = np.zeros(N, bool); flat[1:] = (cl[1:] == cl[:-1]) & (hi[1:] == lo[1:])
cf = np.concatenate([[0], np.cumsum(flat)])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N - 1); return np.where(ts[i] == t, i, -1)
ix = gidx(et + 300 * hold); iy = gidx(et)
day_x = np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] // 86400, -1)
base = (ix >= 1) & np.isin(exitk, ['TP', 'SL'])
is_trade_bar = np.zeros(N, bool); is_trade_bar[ix[ix >= 0]] = True; is_trade_bar[iy[iy >= 0]] = True
def fwd_ok(i0, K, sh):
    iend = i0 + sh + K; okr = (i0 >= 1) & (iend < N) & (i0 + sh >= 0)
    a = np.clip(i0 + sh, 0, N); b = np.clip(iend + 1, 0, N); return okr & ((cf[b] - cf[a]) == 0)
def trail_ok(i0):
    a = np.clip(i0 - 13, 0, N); b = np.clip(i0, 0, N); return (i0 >= 13) & ((cf[b] - cf[a]) == 0)
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
    mu = x.mean(); r = x - mu; _, inv = np.unique(g, return_inverse=True)
    gs = np.bincount(inv, weights=r); se = math.sqrt((gs ** 2).sum()) / n
    return mu, se, (mu / se if se > 0 else float('nan'))
dst = np.zeros(N, bool)
for y in range(2009, 2028):
    d = dt.date(y, 3, 1); fs = d + dt.timedelta(days=(6 - d.weekday()) % 7); ss = fs + dt.timedelta(days=7)
    n_ = dt.date(y, 11, 1); fsn = n_ + dt.timedelta(days=(6 - n_.weekday()) % 7)
    t0 = int(dt.datetime(ss.year, ss.month, ss.day, 7, tzinfo=dt.timezone.utc).timestamp())
    t1 = int(dt.datetime(fsn.year, fsn.month, fsn.day, 6, tzinfo=dt.timezone.utc).timestamp())
    dst |= (ts >= t0) & (ts < t1)
OFFS = [sg * k for k in range(2, 183) for sg in (1, -1)]; TOL_V = 0.02
def v_of(i, s, rk):
    a = np.clip(i, 1, N - 1); return s * (cl[a] - cl[a - 1]) / rk
def rng_of(i, rk):
    a = np.clip(i, 0, N - 1); return (hi[a] - lo[a]) / rk
def cloc_of(i, s):
    a = np.clip(i, 0, N - 1); r = hi[a] - lo[a]
    return np.where(r > 0, s * (cl[a] - (hi[a] + lo[a]) / 2) / np.where(r > 0, r, 1), 0.0)
def trail_of(i, s, rk):
    a = np.clip(i, 13, N - 1); return s * (cl[a - 1] - cl[a - 13]) / rk
def wick_of(i, s, rk):
    a = np.clip(i, 1, N - 1); ext = np.where(s > 0, lo[a], hi[a]); return s * (cl[a - 1] - ext) / rk

def collect(arm, wm, K, sh=1):
    m = base & (exitk == arm) & wm & fwd_ok(ix, K, sh) & (~flat[np.clip(ix, 0, N - 1)]) & trail_ok(ix)
    i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]
    vE = v_of(i0, s, rk); dE = dst[i0]
    rows = {k: [] for k in ('f', 'v', 'rng', 'cloc', 'wick', 'trail', 'day')}
    hit = np.zeros(len(i0), bool)
    for d in OFFS:
        cand = gidx(ts[i0] + d * 86400); cc = np.clip(cand, 0, N - 1)
        ok = (cand >= 1) & fwd_ok(cand, K, sh) & trail_ok(cand) & (~flat[cc]) & (dst[cc] == dE) & (~is_trade_bar[cc])
        cond = ok & (np.abs(v_of(cand, s, rk) - vE) <= TOL_V)
        if not cond.any(): continue
        hit |= cond
        fc = fpass(cc, s, rk, K, 0.5, sh); k = cond
        rows['f'].append(fc[k]); rows['v'].append(v_of(cand, s, rk)[k]); rows['rng'].append(rng_of(cand, rk)[k])
        rows['cloc'].append(cloc_of(cand, s)[k]); rows['wick'].append(wick_of(cand, s, rk)[k])
        rows['trail'].append(trail_of(cand, s, rk)[k]); rows['day'].append(ts[cc][k] // 86400)
    R = {k: (np.concatenate(v) if len(v) else np.array([])) for k, v in rows.items()}
    ev = dict(i0=i0[hit], s=s[hit], rk=rk[hit], g=g[hit], fE=fpass(i0, s, rk, K, 0.5, sh)[hit], nAll=len(i0))
    return R, ev

COLS = ('v', 'rng', 'cloc', 'wick', 'trail')
def design(v, rg, cc, wk, tr):
    return np.column_stack([np.ones(len(v)), v, rg, cc, wk, tr, tr ** 2])
def adj(R, ev, fit_mask=None):
    fm = np.ones(len(R['f']), bool) if fit_mask is None else fit_mask
    Xc = design(R['v'][fm], R['rng'][fm], R['cloc'][fm], R['wick'][fm], R['trail'][fm])
    beta = np.linalg.lstsq(Xc, R['f'][fm], rcond=None)[0]
    i0, s, rk = ev['i0'], ev['s'], ev['rk']
    Xe = design(v_of(i0, s, rk), rng_of(i0, rk), cloc_of(i0, s), wick_of(i0, s, rk), trail_of(i0, s, rk))
    fhat = Xe @ beta
    mu, se, zz = cl_t(ev['fE'] - fhat, ev['g'])
    return mu, se, zz, beta, int(fm.sum())

P(f'# [反証レーン・補 c] 回帰調整残差 +0.0428 の部分窓安定性 / 地平 / **T7 自身への placebo**  {dt.datetime.now():%Y-%m-%d %H:%M}  seed {SEED}')

# ============================================================ T9 sub-window stability
P('\n## T9 部分窓の安定性（SL 腕・K48・回帰調整・モデルは各窓の対照行だけで推定）')
SUB = [('2010-12', (year >= 2010) & (year <= 2012)), ('2013-15', (year >= 2013) & (year <= 2015)),
       ('2016-18', (year >= 2016) & (year <= 2018)), ('2019-20', (year >= 2019) & (year <= 2020)),
       ('2021-23', (year >= 2021) & (year <= 2023)), ('2024-26H1', year >= 2024)]
T9 = {}
for nm, wm in SUB:
    R, ev = collect('SL', wm, 48)
    mu, se, zz, beta, nf = adj(R, ev)
    raw, rse, rz = cl_t(ev['fE'], ev['g'])
    T9[nm] = (mu, se, zz, len(ev['i0']))
    P(f"  - {nm}: 事象 {len(ev['i0'])}/{ev['nAll']} 対照行 {nf} | 事象 生 F' {raw:+.4f} | **D_adj {mu:+.4f} (cl-se {se:.4f} z {zz:+.2f} MDE {2*se:.4f})** | trail 係数 {beta[5]:+.5f}")
ins = ['2010-12', '2013-15', '2016-18', '2019-20']
n_big = sum(1 for k in ins if T9[k][0] >= 0.04); n_neg = sum(1 for k in ins if T9[k][0] < 0)
n_z = sum(1 for k in ins if T9[k][2] >= 1.5)
if n_big <= 1 or n_neg >= 2: t9 = '**broken（在の残差は 1 つの時代の記述・在の中でも再現しない）**'
elif all(T9[k][0] > 0 for k in ins) and n_z >= 3: t9 = '**survived（在 4 窓すべてで正・3 窓以上で z≥1.5）**'
else: t9 = '**inconclusive**'
P(f'  → T9: 在 4 窓のうち D_adj ≥ +0.04 が {n_big} 窓・負が {n_neg} 窓・z≥1.5 が {n_z} 窓 → {t9}')

# ============================================================ T12 horizon robustness / look-ahead on fwd_ok
P('\n## T12 地平 K の頑健性（fwd_ok も K に合わせる＝未来条件づけを緩める）SL 在 2010-20')
WIN_IN = (year >= 2010) & (year <= 2020)
T12 = {}
for K in [12, 24, 48]:
    R, ev = collect('SL', WIN_IN, K)
    mu, se, zz, beta, nf = adj(R, ev)
    raw, rse, rz = cl_t(ev['fE'], ev['g'])
    T12[K] = (mu, se, zz)
    P(f"  - K {K:2d} 本 ({K*5:3d} 分): 事象 {len(ev['i0'])}/{ev['nAll']} 対照行 {nf} | 事象 生 F' {raw:+.4f} | **D_adj {mu:+.4f} (cl-se {se:.4f} z {zz:+.2f} MDE {2*se:.4f})**")
    if K == 48: R48, ev48 = R, ev
brk = any(T12[K][0] < 0.02 and 2 * T12[K][1] <= 0.04 for K in [12, 24])
srv = all(T12[K][0] > 0.02 and T12[K][2] >= 2.0 for K in [12, 24, 48])
P(f"  → T12: {'**broken**' if brk else ('**survived**' if srv else '**inconclusive**')}")

# ============================================================ T11 placebo against my own T7
P('\n## T11 自分の T7 への placebo（事象の共変量平均に最も近い対照行を擬似事象・残りでモデル推定・取引はどこにも無い）')
R, ev = R48, ev48
i0, s, rk = ev['i0'], ev['s'], ev['rk']
EV = np.column_stack([v_of(i0, s, rk), rng_of(i0, rk), cloc_of(i0, s), wick_of(i0, s, rk), trail_of(i0, s, rk)])
CR = np.column_stack([R['v'], R['rng'], R['cloc'], R['wick'], R['trail']])
mu_c = CR.mean(0); sd_c = CR.std(0); sd_c[sd_c == 0] = 1
dist = np.sqrt((((CR - EV.mean(0)) / sd_c) ** 2).sum(1))
n_ev = len(i0)
order = np.argsort(dist, kind='stable')
pick = order[:min(n_ev, len(order) // 2)]
pm = np.zeros(len(dist), bool); pm[pick] = True
P(f"  擬似事象 n {int(pm.sum())}（事象 n {n_ev}）| 共変量 事象平均 " + ' '.join(f'{c} {EV.mean(0)[k]:+.3f}' for k, c in enumerate(COLS)))
P(f"  　　　　　　　　　　　　　　　| 共変量 擬似事象平均 " + ' '.join(f'{c} {CR[pm].mean(0)[k]:+.3f}' for k, c in enumerate(COLS)))
P(f"  　　　　　　　　　　　　　　　| 共変量 残り対照平均 " + ' '.join(f'{c} {CR[~pm].mean(0)[k]:+.3f}' for k, c in enumerate(COLS)))
Xf = design(R['v'][~pm], R['rng'][~pm], R['cloc'][~pm], R['wick'][~pm], R['trail'][~pm])
beta_p = np.linalg.lstsq(Xf, R['f'][~pm], rcond=None)[0]
Xp = design(R['v'][pm], R['rng'][pm], R['cloc'][pm], R['wick'][pm], R['trail'][pm])
resid = R['f'][pm] - Xp @ beta_p
mu, se, zz = cl_t(resid, R['day'][pm])
P(f"  - **D_adj_placebo {mu:+.4f} (cl-se {se:.4f} z {zz:+.2f} MDE {2*se:.4f})** | 擬似事象の生 F' {R['f'][pm].mean():+.4f}")
if abs(mu) >= 0.6 * 0.0428: t11 = '**T7 無効（+0.0428 はモデル誤特定で作れる大きさ）**'
elif abs(mu) < 0.015 and 2 * se <= 0.04: t11 = '**T7 有効（機械は 0 を返す）**'
else: t11 = '**inconclusive**'
P(f'  → T11 = {t11}')

P(f'\n実行 {time.time()-T0:.1f}s  seed {SEED}（乱数未使用・決定論）・外部通信なし・MT5 なし・発注なし')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
