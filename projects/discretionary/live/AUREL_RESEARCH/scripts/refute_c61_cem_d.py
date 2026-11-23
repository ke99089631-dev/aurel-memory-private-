# -*- coding: utf-8 -*-
"""
[反証レーン・補 d / GATE] 2026-11-23  seed 20261123
(1) GATE: 自前コードで c61 の主セル（M1・最近傍 1 本・52 候補・同曜日・取引足除外なし）を再現し、
    c61 の **+0.0962 (cl-se 0.0302 z +3.19 n 2121/4921)** と |Δ| ≤ 0.002 で一致するか確認する。
    一致しなければ本反証の全数字は「設計差」でなく「実装差」の可能性があるため、判定を保留する。
(2) 分解: 本反証が c61 に加えた 3 変更 W1（プール 52→362・全曜日）・W2（最近傍 1 本→許容内全平均）・
    W3（取引足＝決着/建玉足を候補から除外）の 2×2×2 = 8 設計を走らせ、+0.0962 → +0.0593 の落ち分を
    どの変更が担っているかを数値で分解する（事前固定は不要な記述＝ablation）。
対象セルは SL 在 2010-20・sh1・F'(a0.5,48) の 1 つだけ。
副作用: 書き込みは data/refute_c61_cem_d.md のみ。発注なし・MT5 なし・外部通信なし。
"""
import os, json, math, time, datetime as dt
import numpy as np
T0 = time.time(); SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'refute_c61_cem_d.md'); L = []
def P(s=''):
    print(s); L.append(s)
j = json.load(open(os.path.join(DATA, 'refute_c4_scan_paths_2010_2026.json'), encoding='utf-8'))['trades']
et = np.array([t['entry_time'] for t in j], np.int64); hold = np.array([t['hold'] for t in j], np.int64)
side = np.array([1 if t['side'] == 'BUY' else -1 for t in j]); risk = np.array([t['risk'] for t in j], float)
exitk = np.array([t['exit'] for t in j]); year = np.array([t['year'] for t in j])
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_ohlc.npz'))
ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); hi = z['high'].astype(float); lo = z['low'].astype(float)
N = len(ts); flat = np.zeros(N, bool); flat[1:] = (cl[1:] == cl[:-1]) & (hi[1:] == lo[1:])
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
def v_of(i, s, rk):
    a = np.clip(i, 1, N - 1); return s * (cl[a] - cl[a - 1]) / rk
TOL_V = 0.02
POOL52 = [sg * 7 * k for k in range(1, 27) for sg in (1, -1)]
POOL362 = [sg * k for k in range(2, 183) for sg in (1, -1)]

def design(wide, allmean, exclude_trade, sh=1, K=48):
    OFFS = POOL362 if wide else POOL52
    m = base & (exitk == 'SL') & (year >= 2010) & (year <= 2020) & fwd_ok(ix, K, sh) & (~flat[np.clip(ix, 0, N - 1)])
    i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]
    vE = v_of(i0, s, rk); dE = dst[i0]
    bd = np.full(len(i0), np.inf); bI = np.full(len(i0), -1, np.int64)
    sF = np.zeros(len(i0)); cn = np.zeros(len(i0))
    for d in OFFS:
        cand = gidx(ts[i0] + d * 86400); cc = np.clip(cand, 0, N - 1)
        ok = (cand >= 1) & fwd_ok(cand, K, sh) & (~flat[cc]) & (dst[cc] == dE)
        if exclude_trade: ok &= ~is_trade_bar[cc]
        dv = np.abs(v_of(cand, s, rk) - vE)
        cond = ok & (dv <= TOL_V)
        if not cond.any(): continue
        if allmean:
            fc = fpass(cc, s, rk, K, 0.5, sh); w = cond.astype(float); sF += w * fc; cn += w
        else:
            dd = np.where(cond, dv, np.inf); upd = dd < bd
            bd = np.where(upd, dd, bd); bI = np.where(upd, cand, bI)
    fE = fpass(i0, s, rk, K, 0.5, sh)
    if allmean:
        ok = cn > 0; fC = np.where(ok, sF / np.where(ok, cn, 1), np.nan)
    else:
        ok = bI >= 1; fC = np.where(ok, fpass(np.where(ok, bI, 1), s, rk, K, 0.5, sh), np.nan)
    mu, se, zz = cl_t((fE - fC)[ok], g[ok])
    return dict(D=mu, se=se, z=zz, mde=2 * se, n=int(ok.sum()), nE=len(i0), fE=float(fE[ok].mean()), fC=float(np.nanmean(fC[ok])))

P(f'# [反証レーン・補 d / GATE] c61 主セルの自前再現 と 設計変更 W1/W2/W3 の分解  {dt.datetime.now():%Y-%m-%d %H:%M}  seed {SEED}')
P('\n## (1) GATE: c61 の設計そのまま（プール 52・最近傍 1 本・取引足除外なし）')
g0 = design(wide=False, allmean=False, exclude_trade=False)
P(f"  - 自前: D {g0['D']:+.4f} (cl-se {g0['se']:.4f} z {g0['z']:+.2f} MDE {g0['mde']:.4f}) n {g0['n']}/{g0['nE']} | 事象 F' {g0['fE']:+.4f} 対照 {g0['fC']:+.4f}")
P(f"  - c61: D +0.0962 (cl-se 0.0302 z +3.19) n 2121/4921 | 事象 +0.062 対照 −0.034")
dd = abs(g0['D'] - 0.0962)
P(f"  - |Δ(D)| {dd:.4f} / n 差 {g0['n']-2121:+d} → **GATE {'PASS' if dd <= 0.002 and abs(g0['n']-2121) <= 5 else 'FAIL'}**"
  + ('' if dd <= 0.002 else '  ※不一致なら以下の分解は実装差を含む'))

P('\n## (2) W1/W2/W3 の分解（SL 在 2010-20・sh1・F\'(a0.5,48)）')
P('  W1 = プール 52(±7k・同曜日) → 362(|d|2..182・全曜日) / W2 = 最近傍 1 本 → 許容内全平均 / W3 = 候補から取引足（決着+建玉）除外')
rows = []
for w1 in [False, True]:
    for w2 in [False, True]:
        for w3 in [False, True]:
            r = design(w1, w2, w3)
            tag = ('W1 ' if w1 else '-- ') + ('W2 ' if w2 else '-- ') + ('W3' if w3 else '--')
            rows.append((tag, r))
            P(f"  - {tag}: D {r['D']:+.4f} (z {r['z']:+.2f} MDE {r['mde']:.4f}) n {r['n']}/{r['nE']} ({r['n']/r['nE']*100:.0f}%) | 事象 F' {r['fE']:+.4f} 対照 {r['fC']:+.4f}")
b = dict(rows)
P('\n  ### 単独効果（c61 の基準設計 「-- -- --」 からの差）')
for tag in ['W1 -- --', '-- W2 --', '-- -- W3']:
    P(f"    {tag}: ΔD {b[tag]['D'] - b['-- -- --']['D']:+.4f}")
P(f"    W1 W2 W3（本反証 C0）: D {b['W1 W2 W3']['D']:+.4f} / 合計 ΔD {b['W1 W2 W3']['D'] - b['-- -- --']['D']:+.4f}")
P(f'\n実行 {time.time()-T0:.1f}s  seed {SEED}（乱数未使用・決定論）・外部通信なし・MT5 なし・発注なし')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
