# -*- coding: utf-8 -*-
"""
[反証レーン] 2026-11-23  seed 20261123
対象 = cycle61 (2026-11-23 12:40) の主張:
  「SL 決着後の反転は決着足の符号つき収益率 v では還元できない取引固有の残差を持つ」
  主セル SL 在 2010-20・M1(v のみ完全マッチ)・sh1・F'(a0.5,48) = **+0.0962 (cl-se 0.0302 z +3.19 MDE 0.060 n 2121/4921)**
  判定 H_TRADE・在のみ（外 2021-26H1 +0.0059 z +0.16）。c61b（許容内候補 全平均）で +0.0810 (z +2.93)。
  c61 自身の最重大反証 = 「M1 は v しか揃えていない。形（刺して戻すヒゲ）と壁の存在と未分離。
  M2/M3 で +0.04〜+0.05 に落ちるが n 1/2 で MDE 0.08〜0.09＝判定不能」。
  c61 が登記した決着条件 ① = 候補を 同 ET スロット・全曜日 ±182 日（候補 7 倍）に広げ (v, レンジ, 終値位置) を
  同時に ±0.02R／×1.25／±0.15 で揃える粗化厳密マッチ (CEM) で 在 F' が +0.03 未満 かつ MDE ≤ 0.05 か。

--- 本反証の事前固定（この docstring が正本・数字を見る前に書いた） ---
入力は c61 と同一: data/refute_c4_scan_paths_2010_2026.json・data/macro/XAU_m5_ohlc.npz（bid・完全格子）。
事象定義も c61 と同一: exit∈{TP,SL}・ix=gidx(entry+300·hold)・ix≥1・ix 非 flat・前向き 48 本(sh 以降) 非 flat。
統計も同一: F'(a=0.5R, 48 本, sh=1) = P(+0.5R 先着) − P(−0.5R 先着)、事象 − 対照 の対差、決着日クラスタ SE、MDE = 2SE。

**c61 との 3 つの違い（すべて c61 の弱点を突く向き）**
 (W1) 候補プール: c61 は ±7k 日（同曜日・52 本）。本反証は **|d| ∈ [2,182] 日の全日（362 本・同 UTC 時刻・同 US DST 状態＝同 ET スロット）**。
      → M2/M3 のマッチ率 17〜25%（MDE 0.08〜0.09）が c61 の判定不能の原因だったので、プールを 7 倍にして検出力で決着させる。
 (W2) 対照 = **許容内候補の全平均**（c61b 方式）。c61 主結果の「最近傍 1 本」は c61 自身のプラセボで F' を低めに出す機械バイアス
      （R1−R2 在 −0.036・近年 −0.217 z −2.52）を持つ。最近傍 1 本は使わない。
 (W3) 候補から **実トレードの決着足・建玉足を除外**（c61 は未除外）。「取引の無い足」を文字通りにする。

**マッチ変種（すべて v は共通で ±0.02R）**
  C0 = v のみ                                （c61 M1 の広プール・全平均版＝ゲート）
  C1 = v ∧ レンジ/risk ×[0.8,1.25] ∧ 終値位置 ±0.15     （= c61 の決着条件① CEM-3）
  C2 = C1 ∧ **直前 12 本の side 符号つき累積 trail = s·(cl[ix−1]−cl[ix−13])/risk を ±0.05R**  （本反証の追加攻撃 T5）
  C3 = v ∧ trail のみ                        （trail 単独の寄与の分離）

**T5 の動機（c61 が揃えていない第 4 の変数・本反証の独自攻撃）**
  SL 決着足は「直前 hold 本のあいだ TP に当たらなかった」という**前方向きでない事前 path の条件づけ**を必ず背負う
  （建玉が生きていた＝逆行が続いていた）。c61 は決着足 1 本の (v, レンジ, 終値位置) だけを揃え、**その足に至る軌道**は揃えていない。
  もし残差が trail で消えるなら、「SL 後の戻り」は取引固有ではなく「持続した逆行を終わらせた足の後の平均回帰」＝純微細構造。

**破壊規則（事前・主セルは SL 在 2010-20・sh1・a0.5・対照 = 全平均）**
  T1（CEM-3 = c61 決着条件①）: **broken** ⇔ D < +0.03 ∧ MDE ≤ 0.05 ／ **survived** ⇔ D ≥ +0.05 ∧ z ≥ 2.5 ／ 他 inconclusive。
  T5（CEM-4 = +trail）        : 同じ閾値。
  T2（形だけ・取引ゼロ）      : C0 の**対照母集団の中だけ**で（＝どこにも取引が無い）、逆行ヒゲ深さ
      w = s·(cl[a−1] − (lo if s>0 else hi))/risk の 三分位 × 終値位置で F' を測る。
      **trade-specificity broken** ⇔ 「事象に似た形」ビン − 「反対の形」ビン ≥ +0.058 (=0.6×0.096) ∧ z ≥ 2.5
      ∧ 事象の生 F' が「事象に似た形」ビンの ±2SE に入る。
  T4a（在の分割安定性）: 2010-15 / 2016-20 で主セルを再計算。**不安定** ⇔ 片方 D ≤ +0.02 ∧ 他方 D ≥ +0.12。
  T4b（クラスタ符号反転プラセボ）: 決着日クラスタ単位で対差の符号を ±1 ランダム反転 5000 回 → |平均| の帰無分布。
      **broken** ⇔ p > 0.05。（本テストのみ乱数使用・seed 20261123）
  T4c（系統全体の多重検定）: c59→反証 11-23→c61→本反証 で「SL 在」1 問に試した対照設計の総数を数え Holm 補正。
  T4d（コスト倍）: 往復スプレッド s_usd ∈ {0.20, 0.40}（倍）を R 換算 c = s_usd/risk し、
      バリアを 上 +0.5+c / 下 −0.5+c に不利方向へずらして F'_net を事象・対照 同一規則で再計算。
事前の予測: **T1 は survived（c61 の M2/M3 が n 不足で落ちただけ・広プールなら +0.05 以上で立つ）**、
  **T5 が broken を出す**（trail こそ未マッチの主犯）。T2 は trade-specificity を壊す側に出る。
D2 遵守: 在/外/近年 窓別・16 年一括なし。
副作用: 書き込みは data/refute_c61_cem.md のみ。MT5 なし・外部通信なし・多年 scan なし・発注なし。
"""
import os, json, math, time, datetime as dt
import numpy as np

T0 = time.time()
SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'refute_c61_cem.md')
L = []
def P(s=''):
    print(s); L.append(s)

# ---------- load (identical inputs to c61) ----------
j = json.load(open(os.path.join(DATA, 'refute_c4_scan_paths_2010_2026.json'), encoding='utf-8'))['trades']
et   = np.array([t['entry_time'] for t in j], np.int64)
hold = np.array([t['hold'] for t in j], np.int64)
side = np.array([1 if t['side'] == 'BUY' else -1 for t in j])
risk = np.array([t['risk'] for t in j], float)
exitk= np.array([t['exit'] for t in j])
year = np.array([t['year'] for t in j])

z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_ohlc.npz'))
ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); hi = z['high'].astype(float); lo = z['low'].astype(float)
N = len(ts)
flat = np.zeros(N, bool); flat[1:] = (cl[1:] == cl[:-1]) & (hi[1:] == lo[1:])
cf = np.concatenate([[0], np.cumsum(flat)])

def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N - 1)
    return np.where(ts[i] == t, i, -1)

ix = gidx(et + 300 * hold)
iy = gidx(et)
day_x = np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] // 86400, -1)
base = (ix >= 1) & np.isin(exitk, ['TP', 'SL'])

# (W3) bars that ARE a real trade's settlement or entry bar -> excluded from the control pool
is_trade_bar = np.zeros(N, bool)
is_trade_bar[ix[ix >= 0]] = True
is_trade_bar[iy[iy >= 0]] = True

def fwd_ok(i0, K, sh):
    iend = i0 + sh + K
    okr = (i0 >= 1) & (iend < N) & (i0 + sh >= 0)
    a = np.clip(i0 + sh, 0, N); b = np.clip(iend + 1, 0, N)
    return okr & ((cf[b] - cf[a]) == 0)

def trail_ok(i0):
    a = np.clip(i0 - 13, 0, N); b = np.clip(i0, 0, N)
    return (i0 >= 13) & ((cf[b] - cf[a]) == 0)

def fpass(i0, s, rk, K, lev_up, lev_dn, sh):
    bas = cl[np.clip(i0 + sh, 0, N - 1)]
    idx = np.clip(i0[:, None] + sh + np.arange(1, K + 1)[None, :], 0, N - 1)
    path = s[:, None] * (cl[idx] - bas[:, None]) / rk[:, None]
    up = path >= (lev_up[:, None] if np.ndim(lev_up) else lev_up)
    dn = path <= -(lev_dn[:, None] if np.ndim(lev_dn) else lev_dn)
    fu = np.where(up.any(1), up.argmax(1), K + 5)
    fd = np.where(dn.any(1), dn.argmax(1), K + 5)
    r = np.zeros(len(i0), float); r[fu < fd] = 1; r[fd < fu] = -1
    return r

def cl_t(x, g):
    x = np.asarray(x, float); n = len(x)
    if n < 3: return float('nan'), float('nan'), float('nan')
    mu = x.mean(); r = x - mu
    _, inv = np.unique(g, return_inverse=True)
    gs = np.bincount(inv, weights=r)
    se = math.sqrt((gs ** 2).sum()) / n
    return mu, se, (mu / se if se > 0 else float('nan'))

# ---------- US DST state per bar (identical to c61) ----------
dst = np.zeros(N, bool)
for y in range(2009, 2028):
    d = dt.date(y, 3, 1); first_sun = d + dt.timedelta(days=(6 - d.weekday()) % 7); second_sun = first_sun + dt.timedelta(days=7)
    n = dt.date(y, 11, 1); first_sun_nov = n + dt.timedelta(days=(6 - n.weekday()) % 7)
    t0 = int(dt.datetime(second_sun.year, second_sun.month, second_sun.day, 7, tzinfo=dt.timezone.utc).timestamp())
    t1 = int(dt.datetime(first_sun_nov.year, first_sun_nov.month, first_sun_nov.day, 6, tzinfo=dt.timezone.utc).timestamp())
    dst |= (ts >= t0) & (ts < t1)

WINS = [('在 2010-20', (year >= 2010) & (year <= 2020)),
        ('外 2021-26H1', year >= 2021),
        ('近年 2024-26H1', year >= 2024)]
OFFS = [sg * k for k in range(2, 183) for sg in (1, -1)]      # (W1) 362 offsets, all weekdays, |d| in [2,182]
TOL_V, TOL_RNG, TOL_CLOC, TOL_TRAIL = 0.02, math.log(1.25), 0.15, 0.05

def v_of(idx, s, rk):
    a = np.clip(idx, 1, N - 1); return s * (cl[a] - cl[a - 1]) / rk
def rng_of(idx, rk):
    a = np.clip(idx, 0, N - 1); return (hi[a] - lo[a]) / rk
def cloc_of(idx, s):
    a = np.clip(idx, 0, N - 1); r = hi[a] - lo[a]
    return np.where(r > 0, s * (cl[a] - (hi[a] + lo[a]) / 2) / np.where(r > 0, r, 1), 0.0)
def trail_of(idx, s, rk):
    a = np.clip(idx, 13, N - 1); return s * (cl[a - 1] - cl[a - 13]) / rk
def wick_of(idx, s, rk):
    """adverse wick depth below the previous close (>=0 for a stab-and-recover bar)"""
    a = np.clip(idx, 1, N - 1); ext = np.where(s > 0, lo[a], hi[a])
    return s * (cl[a - 1] - ext) / rk

MODES = {'C0': ('v のみ（広プール・全平均・ゲート）', False, False),
         'C1': ('v ∧ レンジ ∧ 終値位置 = CEM-3（c61 決着条件①）', True, False),
         'C2': ('C1 ∧ 直前 12 本 trail ±0.05R = CEM-4（T5）', True, True),
         'C3': ('v ∧ trail のみ', False, True)}

def match_mean(i0, s, rk, sh, mode, lev_up=0.5, lev_dn=0.5, collect=False):
    """control = unweighted mean over ALL in-tolerance candidates (W2). returns per-event sums/counts."""
    _, use_shape, use_trail = MODES[mode]
    vE = v_of(i0, s, rk); rE = rng_of(i0, rk); cE = cloc_of(i0, s); dE = dst[i0]
    tE = trail_of(i0, s, rk)
    sumF = np.zeros(len(i0)); cnt = np.zeros(len(i0))
    sumR = np.zeros(len(i0)); sumC = np.zeros(len(i0)); sumV = np.zeros(len(i0)); sumW = np.zeros(len(i0)); sumT = np.zeros(len(i0))
    rows = {'f': [], 'w': [], 'cloc': [], 'v': [], 'day': [], 'ev': []}
    for d in OFFS:
        cand = gidx(ts[i0] + d * 86400)
        cc = np.clip(cand, 0, N - 1)
        okc = (cand >= 1) & fwd_ok(cand, 48, sh) & (~flat[cc]) & (dst[cc] == dE) & (~is_trade_bar[cc])
        if use_trail: okc &= trail_ok(cand)
        vc = v_of(cand, s, rk)
        cond = okc & (np.abs(vc - vE) <= TOL_V)
        if use_shape:
            rc = rng_of(cand, rk); cond &= (rE > 0) & (rc > 0)
            with np.errstate(divide='ignore', invalid='ignore'):
                lr = np.abs(np.log(np.where(rc > 0, rc, 1) / np.where(rE > 0, rE, 1)))
            cond &= (lr <= TOL_RNG) & (np.abs(cloc_of(cand, s) - cE) <= TOL_CLOC)
        if use_trail:
            cond &= np.abs(trail_of(cand, s, rk) - tE) <= TOL_TRAIL
        if not cond.any(): continue
        fc = fpass(cc, s, rk, 48, lev_up, lev_dn, sh)
        w = cond.astype(float)
        sumF += w * fc; cnt += w
        sumR += w * rng_of(cand, rk); sumC += w * cloc_of(cand, s); sumV += w * vc
        sumW += w * wick_of(cand, s, rk); sumT += w * trail_of(cand, s, rk)
        if collect:
            m = cond
            rows['f'].append(fc[m]); rows['w'].append(wick_of(cand, s, rk)[m]); rows['cloc'].append(cloc_of(cand, s)[m])
            rows['v'].append(vc[m]); rows['day'].append(ts[cc][m] // 86400); rows['ev'].append(np.where(m)[0])
    out = dict(sumF=sumF, cnt=cnt, sumR=sumR, sumC=sumC, sumV=sumV, sumW=sumW, sumT=sumT)
    if collect:
        out['rows'] = {k: (np.concatenate(v) if len(v) else np.array([])) for k, v in rows.items()}
    return out

def cell(arm, wm, mode, sh=1, lev_up=0.5, lev_dn=0.5, extra=None, collect=False):
    m = base & (exitk == arm) & wm & fwd_ok(ix, 48, sh) & (~flat[np.clip(ix, 0, N - 1)])
    if MODES[mode][2]: m = m & trail_ok(ix)
    if extra is not None: m = m & extra
    i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]
    lu = lev_up if np.ndim(lev_up) == 0 else lev_up[m]
    ld = lev_dn if np.ndim(lev_dn) == 0 else lev_dn[m]
    r = match_mean(i0, s, rk, sh, mode, lu, ld, collect=collect)
    ok = r['cnt'] > 0
    fE = fpass(i0, s, rk, 48, lu, ld, sh)
    fC = np.where(ok, r['sumF'] / np.where(ok, r['cnt'], 1), np.nan)
    mu, se, zz = cl_t((fE - fC)[ok], g[ok])
    res = dict(nE=len(i0), nM=int(ok.sum()), D=mu, se=se, z=zz, mde=2 * se,
               fE=float(fE[ok].mean()), fC=float(np.nanmean(fC[ok])),
               ncand=float(np.median(r['cnt'][ok])) if ok.any() else 0.0,
               vE=float(v_of(i0, s, rk)[ok].mean()), vC=float((r['sumV'][ok] / r['cnt'][ok]).mean()),
               rE=float(rng_of(i0, rk)[ok].mean()), rC=float((r['sumR'][ok] / r['cnt'][ok]).mean()),
               cE=float(cloc_of(i0, s)[ok].mean()), cC=float((r['sumC'][ok] / r['cnt'][ok]).mean()),
               wE=float(wick_of(i0, s, rk)[ok].mean()), wC=float((r['sumW'][ok] / r['cnt'][ok]).mean()),
               tE=float(trail_of(i0, s, rk)[ok].mean()), tC=float((r['sumT'][ok] / r['cnt'][ok]).mean()),
               fdrop=float(fE[~ok].mean()) if (~ok).any() else float('nan'),
               diffs=(fE - fC)[ok], g=g[ok], rows=r.get('rows'))
    return res

P(f'# [反証レーン] c61 「SL 決着後の取引固有残差 +0.0962」を壊す — CEM 広プール / trail マッチ / 形だけ対照  {dt.datetime.now():%Y-%m-%d %H:%M}  seed {SEED}')
P(f'入力: refute_c4 json n {len(j)} / XAU_m5_ohlc.npz {N} 本 flat {flat.mean()*100:.1f}% / DST 足 {dst.mean()*100:.1f}% / 取引足（決着+建玉）除外対象 {int(is_trade_bar.sum())} 本')
P(f'候補プール {len(OFFS)} 本（|d| 2..182 日・全曜日・同 UTC 時刻・同 DST）vs c61 の 52 本（±7k・同曜日）／対照 = 許容内候補の全平均（c61b 方式）')
P(f'事象母数（TP/SL・格子あり）{int(base.sum())}')

# ============================================================ grid: all modes x arms x windows
P('\n## 本体グリッド（事象 − 許容内候補全平均・F\'(a0.5,48)・sh1）')
R = {}
for mode in ['C0', 'C1', 'C2', 'C3']:
    P(f'\n### {mode}: {MODES[mode][0]}')
    for arm in ['SL', 'TP']:
        for wn, wm in WINS:
            c = cell(arm, wm, mode, collect=(mode == 'C0' and arm == 'SL' and wn == '在 2010-20'))
            R[(mode, arm, wn)] = c
            P(f"  - {arm} {wn}: n {c['nE']} → マッチ {c['nM']} ({c['nM']/max(c['nE'],1)*100:.1f}%・候補中央値 {c['ncand']:.0f}) | "
              f"較正 v {c['vE']:+.3f}/{c['vC']:+.3f} レンジ {c['rE']:.3f}/{c['rC']:.3f} 終値位置 {c['cE']:+.3f}/{c['cC']:+.3f} "
              f"ヒゲ {c['wE']:.3f}/{c['wC']:.3f} trail {c['tE']:+.3f}/{c['tC']:+.3f}")
            P(f"      F' 事象 {c['fE']:+.4f} 対照 {c['fC']:+.4f} **D {c['D']:+.4f} (cl-se {c['se']:.4f} z {c['z']:+.2f} MDE {c['mde']:.4f})** | 脱落事象の生 F' {c['fdrop']:+.4f}")

# ============================================================ T1 / T5 verdicts
def rule(c, name):
    if c['D'] < 0.03 and c['mde'] <= 0.05: return f'{name} = **broken**'
    if c['D'] >= 0.05 and c['z'] >= 2.5:   return f'{name} = **survived**'
    return f'{name} = **inconclusive**'

P('\n## T1 / T5 判定（事前規則・主セル SL 在 2010-20・sh1・a0.5）')
c1 = R[('C1', 'SL', '在 2010-20')]; c2 = R[('C2', 'SL', '在 2010-20')]; c0 = R[('C0', 'SL', '在 2010-20')]
P(f"  - ゲート C0 (v のみ・広プール): D {c0['D']:+.4f} (z {c0['z']:+.2f} MDE {c0['mde']:.4f} n {c0['nM']})  ← c61b の +0.0810 (z +2.93) と並べて読む")
P(f"  - T1 CEM-3: D {c1['D']:+.4f} (z {c1['z']:+.2f} MDE {c1['mde']:.4f} n {c1['nM']}) → {rule(c1, 'T1')}  [c61 M3 は +0.054 z 1.31 MDE 0.083 n 1159]")
P(f"  - T5 CEM-4: D {c2['D']:+.4f} (z {c2['z']:+.2f} MDE {c2['mde']:.4f} n {c2['nM']}) → {rule(c2, 'T5')}")
P(f"  - C3 (v ∧ trail): D {R[('C3','SL','在 2010-20')]['D']:+.4f} (z {R[('C3','SL','在 2010-20')]['z']:+.2f} MDE {R[('C3','SL','在 2010-20')]['mde']:.4f})")

# ============================================================ T2 shape-only, zero trades anywhere
P('\n## T2 形だけ・取引ゼロ（C0 の対照母集団の中だけで ヒゲ深さ×終値位置 で F\' を測る）')
rows = c0['rows']
P(f"  対照行 n {len(rows['f'])}（SL 在・v 許容内・取引足除外）| 事象側の平均 ヒゲ {c0['wE']:.3f} 終値位置 {c0['cE']:+.3f} 生 F' {c0['fE']:+.4f}")
if len(rows['f']) > 100:
    w = rows['w']; cc = rows['cloc']; f = rows['f']; dy = rows['day']
    q = np.quantile(w, [1/3, 2/3])
    bins = [('ヒゲ 浅 (下 1/3)', w <= q[0]), ('ヒゲ 中', (w > q[0]) & (w < q[1])), ('ヒゲ 深 (上 1/3)', w >= q[1])]
    for nm, mk in bins:
        mu, se, zz = cl_t(f[mk], dy[mk])
        P(f"    - {nm}: n {int(mk.sum())} ヒゲ {w[mk].mean():.3f} 終値位置 {cc[mk].mean():+.3f} F' {mu:+.4f} (cl-se {se:.4f})")
    # event-like = deep wick AND mid/high close location (like the SL bar: cloc ~ -0.04 vs control ~ -0.18)
    like = (w >= q[1]) & (cc >= c0['cE'] - 0.15)
    anti = (w <= q[0]) & (cc <= c0['cC'] + 0.15)
    mL, sL, zL = cl_t(f[like], dy[like]); mA, sA, zA = cl_t(f[anti], dy[anti])
    gap = mL - mA; gse = math.sqrt(sL ** 2 + sA ** 2); gz = gap / gse if gse > 0 else float('nan')
    P(f"    - 事象似の形（深ヒゲ ∧ 終値位置 ≥ {c0['cE']-0.15:+.2f}）: n {int(like.sum())} F' {mL:+.4f} (±2SE {2*sL:.4f})")
    P(f"    - 反対の形（浅ヒゲ ∧ 終値位置 ≤ {c0['cC']+0.15:+.2f}）: n {int(anti.sum())} F' {mA:+.4f} (±2SE {2*sA:.4f})")
    P(f"    - **形だけのギャップ {gap:+.4f} (se {gse:.4f} z {gz:+.2f})** / 閾値 ≥ +0.058 ∧ z ≥ 2.5")
    inband = abs(c0['fE'] - mL) <= 2 * sL
    t2 = ('**trade-specificity broken**' if (gap >= 0.058 and gz >= 2.5 and inband)
          else '**inconclusive / trade-specificity 維持**')
    P(f"    - 事象の生 F' {c0['fE']:+.4f} は 事象似ビン {mL:+.4f} の ±2SE {'内' if inband else '外'} → T2 = {t2}")

# ============================================================ T4a in-sample split-half
P('\n## T4a 在の分割安定性（主セル設計 C0 / C1 / C2 を 2010-15 と 2016-20 で）')
for mode in ['C0', 'C1', 'C2']:
    row = []
    for nm, wm in [('2010-15', (year >= 2010) & (year <= 2015)), ('2016-20', (year >= 2016) & (year <= 2020))]:
        c = cell('SL', wm, mode)
        row.append(f"{nm}: D {c['D']:+.4f} (z {c['z']:+.2f} MDE {c['mde']:.4f} n {c['nM']})")
    P(f'  - {mode}: ' + ' | '.join(row))

# ============================================================ T4b cluster sign-flip permutation
P('\n## T4b クラスタ符号反転プラセボ（決着日クラスタ単位・5000 回・seed 20261123）')
rng = np.random.default_rng(SEED)
for mode in ['C0', 'C1', 'C2']:
    c = R[(mode, 'SL', '在 2010-20')]
    d_ = c['diffs']; g_ = c['g']
    _, inv = np.unique(g_, return_inverse=True); K = inv.max() + 1
    gs = np.bincount(inv, weights=d_); gn = np.bincount(inv)
    obs = d_.mean()
    S = rng.choice([-1.0, 1.0], size=(5000, K))
    null = (S @ gs) / len(d_)
    p = float((np.abs(null) >= abs(obs)).mean())
    P(f"  - {mode}: 観測 平均 {obs:+.4f} | 帰無 sd {null.std():.4f} 95% {np.quantile(np.abs(null),0.95):.4f} | **p {p:.4f}** (クラスタ {K}) → {'broken' if p > 0.05 else '生存'}")

# ============================================================ T4d cost doubled
P('\n## T4d コスト倍（往復スプレッド 0.20 / 0.40 USD を R 換算しバリアを不利方向へ）')
med_risk = float(np.median(risk[base]))
P(f'  risk 中央値 {med_risk:.3f} USD → 0.20 USD ≈ {0.20/med_risk:.4f}R / 0.40 USD ≈ {0.40/med_risk:.4f}R')
for sp in [0.0, 0.20, 0.40]:
    cR = sp / risk
    for mode in ['C0', 'C1', 'C2']:
        c = cell('SL', (year >= 2010) & (year <= 2020), mode, lev_up=0.5 + cR, lev_dn=0.5 - cR)
        P(f"  - spread {sp:.2f} USD {mode}: F'_net 事象 {c['fE']:+.4f} 対照 {c['fC']:+.4f} D {c['D']:+.4f} (z {c['z']:+.2f} MDE {c['mde']:.4f})")

# ============================================================ T4c lineage multiple testing
P('\n## T4c 系統全体の多重検定（「SL 在 2010-20 の決着後 F\'」1 問に試した対照設計）')
designs = [('c59 通常双子 ±7 (sh1)', 0.063, 3.68), ('c59 sh0', 0.111, 3.73), ('反証 11-23 sh3', 0.065, 3.80),
           ('反証 11-23 RMT12', 0.064, 3.21), ('c61 M1 最近傍', 0.0962, 3.19), ('c61 M2', 0.038, 0.88),
           ('c61 M3', 0.054, 1.31), ('c61b 全平均', 0.0810, 2.93),
           ('本反証 C0 広プール', c0['D'], c0['z']), ('本反証 C1 CEM-3', c1['D'], c1['z']), ('本反証 C2 CEM-4', c2['D'], c2['z']),
           ('本反証 C3 v+trail', R[('C3','SL','在 2010-20')]['D'], R[('C3','SL','在 2010-20')]['z'])]
mz = len(designs)
P(f'  設計 {mz} 個（同じ事象・同じ統計・対照だけ差し替え）→ Holm 補正の必要 |z|（両側 α 0.05）を昇順に並べる')
srt = sorted(designs, key=lambda x: -abs(x[2]))
try:
    from scipy.stats import norm
    need = lambda k: norm.ppf(1 - 0.05 / (2 * (mz - k)))
except Exception:
    # inverse normal via bisection (no scipy dependency)
    def _ppf(pp):
        a, b = 0.0, 8.0
        for _ in range(200):
            m = (a + b) / 2
            if 0.5 * (1 + math.erf(m / math.sqrt(2))) < pp: a = m
            else: b = m
        return (a + b) / 2
    need = lambda k: _ppf(1 - 0.05 / (2 * (mz - k)))
for k, (nm, dd, zz) in enumerate(srt):
    nd = need(k)
    P(f"    {k+1:2d}. {nm:24s} D {dd:+.4f} |z| {abs(zz):.2f} / Holm 必要 {nd:.2f} → {'通過' if abs(zz) >= nd else '不通過'}")

P(f'\n実行 {time.time()-T0:.1f}s  seed {SEED}（乱数は T4b のみ）・外部通信なし・MT5 なし・多年 scan なし・発注なし')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
