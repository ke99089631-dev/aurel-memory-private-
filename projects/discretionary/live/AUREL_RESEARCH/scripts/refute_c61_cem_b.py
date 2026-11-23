# -*- coding: utf-8 -*-
"""
[反証レーン・補 b] 2026-11-23  seed 20261123
本体 refute_c61_cem.py で判明した**未マッチの第 4 変数**を検出力を落とさずに決着させる。

本体の事実（数字を見てから書いた＝ここは post-hoc と明記する）:
  C0（v のみ・広プール 362 本・全平均・取引足除外）SL 在 2010-20: D +0.0593 (z +3.03 MDE 0.0392 n 3443/4921)
  その較正表で **trail = s·(cl[ix−1]−cl[ix−13])/risk（決着足に至る直前 12 本の side 符号つき走り）が
  事象 −0.420 vs 対照 +0.056（ギャップ 0.476R）** と全く揃っていない。TP 腕も鏡像（事象 +0.678 vs 対照 −0.070・ギャップ 0.748R）。
  trail を ±0.05R で揃えると D は +0.0143 (z +0.27) に落ちるが マッチ率 13%・MDE 0.106 で判定不能（本体 C3）。
  → 検出力を落とさずに trail を処理する 3 つの事後テスト。

--- 事前固定（本スクリプトの判定規則・実行前に書いた） ---
共通の母集団: 本体と同一（exit∈{TP,SL}・ix≥1・ix 非 flat・前向き 48 本 非 flat）＋ **全ラングで trail_ok(ix) を課す**
  （＝ラング間で事象集合を固定し、動くのは許容幅だけ）。対照 = 許容内候補の全平均・取引足（決着/建玉）除外・同 UTC 時刻・同 DST・|d| 2..182 日。

T6（trail 許容ラダー）: v ±0.02R を固定したまま trail 許容を ∞ → ±0.80 → ±0.40 → ±0.20 → ±0.10 → ±0.05R と締める。
  **H_TRAIL（残差は run-in で説明される）** ⇔ D が単調に減り、かつ **MDE ≤ 0.06 を満たす最も厳しいラングで D < +0.03**。
  **H_TRADE 維持** ⇔ MDE ≤ 0.06 の全ラングで D ≥ +0.05 ∧ z ≥ 2.0。 他 inconclusive。

T8（取引ゼロの用量反応）: 対照行（＝どこにも取引の無い足）だけを使い F'(a0.5,48) を trail で 5 分位に切る。
  傾き b を OLS（対照行・日クラスタ ブートストラップ 2000 回・seed 20261123）で推定。
  **統一説明が成立** ⇔ b < 0 かつ有意（|z| ≥ 2.5）かつ
    b·(trail_E − trail_C) が SL 腕 D の **50% 以上** を再現し、同じ b で TP 腕 D の符号も再現する。
  （SL ギャップ −0.476 → b<0 なら +、TP ギャップ +0.748 → b<0 なら −。観測は SL +0.059 / TP −0.038 なので符号は一致する。）

T7（回帰調整対照・全検出力）: 対照行で f ~ 1 + v + rng + cloc + wick + trail（線形・+ trail² ）を OLS 推定し、
  各事象の自分の共変量で反実仮想 f̂ を予測 → D_adj = mean(f_E − f̂_E)・SE は 事象日クラスタ ブートストラップ。
  **共通サポート検査を先に印字**: 事象の trail が対照行 trail の [p1, p99] に入る割合。
  サポート被覆が 90% 未満なら D_adj は外挿なので「**この設計では決着不能（unfalsifiable with this control pool）**」と書き、D_adj は参考値扱い。
  **H_TRAIL** ⇔ サポート被覆 ≥ 90% ∧ D_adj < +0.03 ∧ MDE ≤ 0.05。

D2: 在/外/近年 窓別・16 年一括なし。副作用: 書き込みは data/refute_c61_cem_b.md のみ。発注なし・MT5 なし・外部通信なし。
"""
import os, json, math, time, datetime as dt
import numpy as np

T0 = time.time(); SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'refute_c61_cem_b.md')
L = []
def P(s=''):
    print(s); L.append(s)

j = json.load(open(os.path.join(DATA, 'refute_c4_scan_paths_2010_2026.json'), encoding='utf-8'))['trades']
et   = np.array([t['entry_time'] for t in j], np.int64); hold = np.array([t['hold'] for t in j], np.int64)
side = np.array([1 if t['side'] == 'BUY' else -1 for t in j]); risk = np.array([t['risk'] for t in j], float)
exitk= np.array([t['exit'] for t in j]); year = np.array([t['year'] for t in j])

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

OFFS = [sg * k for k in range(2, 183) for sg in (1, -1)]
TOL_V = 0.02
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

def evmask(arm, wm, sh=1):
    return base & (exitk == arm) & wm & fwd_ok(ix, 48, sh) & (~flat[np.clip(ix, 0, N - 1)]) & trail_ok(ix)

def run(arm, wm, tol_trail, sh=1, collect=False):
    m = evmask(arm, wm, sh); i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]
    vE = v_of(i0, s, rk); tE = trail_of(i0, s, rk); dE = dst[i0]
    sF = np.zeros(len(i0)); cn = np.zeros(len(i0)); sT = np.zeros(len(i0))
    rows = {k: [] for k in ('f', 'v', 'rng', 'cloc', 'wick', 'trail', 'day')}
    for d in OFFS:
        cand = gidx(ts[i0] + d * 86400); cc = np.clip(cand, 0, N - 1)
        ok = (cand >= 1) & fwd_ok(cand, 48, sh) & trail_ok(cand) & (~flat[cc]) & (dst[cc] == dE) & (~is_trade_bar[cc])
        tc = trail_of(cand, s, rk)
        cond = ok & (np.abs(v_of(cand, s, rk) - vE) <= TOL_V)
        if np.isfinite(tol_trail): cond &= np.abs(tc - tE) <= tol_trail
        if not cond.any(): continue
        fc = fpass(cc, s, rk, 48, 0.5, sh); w = cond.astype(float)
        sF += w * fc; cn += w; sT += w * tc
        if collect:
            k = cond
            rows['f'].append(fc[k]); rows['v'].append(v_of(cand, s, rk)[k]); rows['rng'].append(rng_of(cand, rk)[k])
            rows['cloc'].append(cloc_of(cand, s)[k]); rows['wick'].append(wick_of(cand, s, rk)[k])
            rows['trail'].append(tc[k]); rows['day'].append(ts[cc][k] // 86400)
    ok = cn > 0; fE = fpass(i0, s, rk, 48, 0.5, sh)
    fC = np.where(ok, sF / np.where(ok, cn, 1), np.nan)
    mu, se, zz = cl_t((fE - fC)[ok], g[ok])
    out = dict(nE=len(i0), nM=int(ok.sum()), D=mu, se=se, z=zz, mde=2 * se, fE=float(fE[ok].mean()), fC=float(np.nanmean(fC[ok])),
               tE=float(tE[ok].mean()), tC=float((sT[ok] / cn[ok]).mean()),
               ev=dict(i0=i0[ok], s=s[ok], rk=rk[ok], g=g[ok], fE=fE[ok]))
    if collect: out['rows'] = {k: (np.concatenate(v) if len(v) else np.array([])) for k, v in rows.items()}
    return out

WINS = [('在 2010-20', (year >= 2010) & (year <= 2020)), ('外 2021-26H1', year >= 2021), ('近年 2024-26H1', year >= 2024)]
P(f'# [反証レーン・補 b] c61 残差の未マッチ第 4 変数（run-in trail）の決着  {dt.datetime.now():%Y-%m-%d %H:%M}  seed {SEED}')
P(f'母集団は本体と同一＋全ラングで trail_ok(ix) 固定。対照 = 許容内候補 全平均・取引足除外・プール {len(OFFS)} 本。')

# ============================================================ T6 trail tolerance ladder
P('\n## T6 trail 許容ラダー（v ±0.02R 固定・事象集合は全ラング同一）')
LAD = [(np.inf, '∞（trail 無視）'), (0.80, '±0.80R'), (0.40, '±0.40R'), (0.20, '±0.20R'), (0.10, '±0.10R'), (0.05, '±0.05R')]
LADR = {}
for arm in ['SL', 'TP']:
    for wn, wm in WINS:
        if arm == 'TP' and wn != '在 2010-20': continue
        P(f'  ### {arm} {wn}')
        for tol, nm in LAD:
            r = run(arm, wm, tol); LADR[(arm, wn, tol)] = r
            P(f"    - trail {nm:14s}: n {r['nM']}/{r['nE']} ({r['nM']/max(r['nE'],1)*100:4.1f}%) trail 事象 {r['tE']:+.3f}/対照 {r['tC']:+.3f} "
              f"| F' 事象 {r['fE']:+.4f} 対照 {r['fC']:+.4f} **D {r['D']:+.4f} (z {r['z']:+.2f} MDE {r['mde']:.4f})**")

sl = [(t, LADR[('SL', '在 2010-20', t)]) for t, _ in LAD]
powered = [(t, r) for t, r in sl if r['mde'] <= 0.06]
mono = all(sl[i][1]['D'] >= sl[i + 1][1]['D'] - 1e-9 for i in range(len(sl) - 1))
if powered:
    tt, rt = powered[-1]
    if mono and rt['D'] < 0.03: t6 = 'H_TRAIL（残差は run-in で説明される）= **c61 の H_TRADE broken**'
    elif all(r['D'] >= 0.05 and r['z'] >= 2.0 for _, r in powered): t6 = 'H_TRADE 維持（本テストでは壊せない）'
    else: t6 = 'inconclusive'
    P(f"  → T6: 単調減少 {mono} / MDE ≤ 0.06 の最厳ラング trail ±{tt} の D {rt['D']:+.4f} (z {rt['z']:+.2f} MDE {rt['mde']:.4f}) → **{t6}**")
else:
    P('  → T6: MDE ≤ 0.06 を満たすラングが無い → **inconclusive（検出力不足）**')

# ============================================================ T8 dose-response inside the zero-trade control rows
P('\n## T8 取引ゼロの用量反応（対照行だけ・どこにも取引が無い足で F\' を trail で 5 分位）')
rng_ = np.random.default_rng(SEED)
DOSE = {}
for arm in ['SL', 'TP']:
    r = run(arm, (year >= 2010) & (year <= 2020), np.inf, collect=True)
    ro = r['rows']; f = ro['f']; tr = ro['trail']; dy = ro['day']
    P(f"  ### {arm} 在 2010-20: 対照行 n {len(f)} | 事象 trail {r['tE']:+.3f} 対照 trail {r['tC']:+.3f} ギャップ {r['tE']-r['tC']:+.3f}R | 事象 生 F' {r['fE']:+.4f}")
    qs = np.quantile(tr, [0.2, 0.4, 0.6, 0.8])
    edges = [-np.inf] + list(qs) + [np.inf]
    for k in range(5):
        mk = (tr > edges[k]) & (tr <= edges[k + 1])
        mu, se, zz = cl_t(f[mk], dy[mk])
        P(f"    - Q{k+1} trail [{edges[k]:+.3f},{edges[k+1]:+.3f}] 平均 {tr[mk].mean():+.3f}: n {int(mk.sum())} F' {mu:+.4f} (cl-se {se:.4f})")
    # OLS slope with day-cluster bootstrap
    X = np.column_stack([np.ones(len(tr)), tr]); bhat = np.linalg.lstsq(X, f, rcond=None)[0]
    ud, inv = np.unique(dy, return_inverse=True); K = len(ud)
    order = np.argsort(inv, kind='stable'); starts = np.searchsorted(inv[order], np.arange(K)); ends = np.searchsorted(inv[order], np.arange(K), side='right')
    bs = np.empty(2000)
    for b in range(2000):
        pick = rng_.integers(0, K, K)
        idxs = np.concatenate([order[starts[p]:ends[p]] for p in pick])
        Xb = X[idxs]; bs[b] = np.linalg.lstsq(Xb, f[idxs], rcond=None)[0][1]
    bse = bs.std(); bz = bhat[1] / bse if bse > 0 else float('nan')
    gap = r['tE'] - r['tC']; pred = bhat[1] * gap
    P(f"    - OLS 傾き b {bhat[1]:+.5f} (日クラスタ bootstrap se {bse:.5f} z {bz:+.2f}) | b·ギャップ = {pred:+.4f} vs 観測 D {r['D']:+.4f}  → 説明率 {pred/r['D']*100 if r['D']!=0 else float('nan'):.0f}%")
    DOSE[arm] = dict(b=bhat[1], bse=bse, bz=bz, gap=gap, pred=pred, D=r['D'], rows=ro, ev=r)
bS, bT = DOSE['SL'], DOSE['TP']
share = bS['pred'] / bS['D'] if bS['D'] != 0 else float('nan')
sign_ok = (np.sign(bT['pred']) == np.sign(bT['D']))
t8 = ('**統一説明 成立 = c61 の「取引固有」は run-in の平均回帰に還元**' if (bS['b'] < 0 and abs(bS['bz']) >= 2.5 and share >= 0.5 and sign_ok)
      else '**統一説明 不成立（c61 の残差は trail だけでは説明できない）**')
P(f"  → T8: b(SL) {bS['b']:+.5f} z {bS['bz']:+.2f} / SL 説明率 {share*100:.0f}% / TP 符号一致 {sign_ok} → {t8}")

# ============================================================ T7 regression-adjusted control + common support
P('\n## T7 回帰調整対照（全検出力）＋共通サポート検査')
for arm in ['SL', 'TP']:
    d = DOSE[arm]; ro = d['rows']; ev = d['ev']['ev']
    tr = ro['trail']
    p1, p99 = np.quantile(tr, [0.01, 0.99])
    tEv = trail_of(ev['i0'], ev['s'], ev['rk'])
    cover = float(((tEv >= p1) & (tEv <= p99)).mean())
    Xc = np.column_stack([np.ones(len(tr)), ro['v'], ro['rng'], ro['cloc'], ro['wick'], tr, tr ** 2])
    beta = np.linalg.lstsq(Xc, ro['f'], rcond=None)[0]
    Xe = np.column_stack([np.ones(len(ev['i0'])), v_of(ev['i0'], ev['s'], ev['rk']), rng_of(ev['i0'], ev['rk']),
                          cloc_of(ev['i0'], ev['s']), wick_of(ev['i0'], ev['s'], ev['rk']), tEv, tEv ** 2])
    fhat = Xe @ beta
    mu, se, zz = cl_t(ev['fE'] - fhat, ev['g'])
    P(f"  - {arm} 在 2010-20: 対照行 trail [p1 {p1:+.3f}, p99 {p99:+.3f}] / 事象 trail 平均 {tEv.mean():+.3f} 中央 {np.median(tEv):+.3f} "
      f"→ **共通サポート被覆 {cover*100:.1f}%**")
    P(f"      係数 trail {beta[5]:+.5f} trail² {beta[6]:+.5f} wick {beta[4]:+.5f} cloc {beta[3]:+.5f} rng {beta[2]:+.5f} v {beta[1]:+.5f}")
    P(f"      **D_adj {mu:+.4f} (cl-se {se:.4f} z {zz:+.2f} MDE {2*se:.4f})** | 素の D {d['D']:+.4f}  "
      f"{'→ 外挿（サポート被覆 <90%）＝この設計では決着不能' if cover < 0.90 else '→ サポート内'}")
    if arm == 'SL':
        t7 = ('**H_TRAIL（D_adj < +0.03）**' if (cover >= 0.90 and mu < 0.03 and 2 * se <= 0.05)
              else ('**決着不能（外挿）**' if cover < 0.90 else '**H_TRAIL 不成立**'))
        P(f'      → T7 = {t7}')

P(f'\n実行 {time.time()-T0:.1f}s  seed {SEED}（乱数 = T8 bootstrap のみ）・外部通信なし・MT5 なし・発注なし')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
