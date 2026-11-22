# -*- coding: utf-8 -*-
"""
[cycle59 研究レーン 2026-11-23] 【深化・出口／path（決着“後”の path）】
壁→壁/再加速の出口系統（経過時間 c7・時計 c21・含み水準・最大到達・形 c23・建値/トレール c2）は「決着前の path に出口情報なし」で閉じた。
未測定なのは **決着の“後”**: TP で畳んだ壁（目標壁）は終点（反発＝TP は良く置かれている）か通過点（継続＝runner／TP 延長の仮説が立つ）か、
それとも随機歩行（RW・出口後の価格は決着を覚えていない＝c21 のマルコフの延長）か。SL 側も対称に: SL 決着後に価格は建玉方向へ戻る（lore
「ストップ狩り後の反転」）か、逆行を続けるか。これは入口フィルタでなく、出口規則の“紙の上の”機構分析（補遺 D・E）。本番レシピは触らない。

=== 事前固定（この docstring を書いてから数字を見る・seed 20261123）===
データ: data/refute_c4_scan_paths_2010_2026.json（19404 本・entry_time/side/risk/b/exit/hold）・data/macro/XAU_m5_ohlc.npz（bid・暦時刻完全格子・前値埋め）
  ・data/refute_c2_fullpaths.npz（整合確認のみ）。既存キャッシュのみ・多年 scan 無し・M5 原本読込なし・MT5 無し・外部通信無し。
決着足 ts_x = entry_time + 300·hold（§2 規約・格子は週末 flat 足込みで連続）。格子に無い ts（穴 19）は落とす。
整合 assert: fullpaths の clR[hold]−clR[hold−1] と side·(close[ts_x]−close[ts_x−300])/risk の一致率（|差|≤0.02R）を印字・≥99% を要求。
事象集合: exit ∈ {TP, SL}（TIME 872 は週末畳み 74% なので除外）。決着足と前向き窓 [ts_x+300 .. ts_x+300·K] の全足が非 flat（flat = close 不変 ∧ high==low）
  → ブレイク/週末/祝日 stale を跨ぐ事象は K ごとに除外（率を印字）。
主統計 C_K = s·(close[ts_x+300·K] − close[ts_x]) / risk（R 単位・s = +1 BUY／−1 SELL）。主 K=12（1 時間）。副 K=1,3,6,24,48。
  アンカーずらし版（方法論 ㉙）: 決着足の close は条件づけ（TP 足は高く・SL 足は低く閉じる）で bid バウンス／lag1 負（c19 在）を拾う →
  C'_K = s·(close[ts_x+300·(K+1)] − close[ts_x+300]) / risk も併記。**判定は C' を主**（決着足のバウンスは出口規則では受け取れない）。
対照（双子・c33 型）: 同じ ET 時:分・同じ side・D±7 日（2 本・存在し窓が非 flat の方を平均・両方無ければ事象を落とす）の同じ C'_K。
  D_K = mean(C'_K^event − C'_K^twin)（対の差）。side × 時刻 × 季節のドリフト（c16/c18 の夜間ドリフト等）を差し引く。
  SE = 決着日クラスタ（同日の事象は窓が重なる）。t = D/SE。MDE = 2·SE。
窓（D2・判定は 在→外）: 在 2010-20／外 2021-26H1／近年 2024-26H1（記述）。
判定（主 2 セル = TP 腕・SL 腕の D_12・Bonferroni 2 → 在 |t| ≥2.5）:
  TP 腕: H_CONT（通過点）PASS = 在 D_12 ≥ +0.03R ∧ t ≥2.5 ∧ 外 D_12 >0 ∧ t ≥1.5／H_REV（終点）PASS = 在 D_12 ≤ −0.03R ∧ t ≤−2.5 ∧ 外 <0 ∧ t ≤−1.5。
  SL 腕: H_SLREV（戻る）PASS = 在 D_12 ≥ +0.03R ∧ t ≥2.5 ∧ 外 >0 ∧ t ≥1.5／H_SLCONT（逆行継続）対称。
  どれでもなければ null（MDE 併記）。事前の予測 = 両腕 null（c21 マルコフ・c26「水準は通過点」でも c57「ブレイク後の走りは RW」）。
  0.03R の根拠 = 実測コスト 0.03R/本（c25・c52）: それ未満の継続は runner でも受け取れない。
副（記述・判定に使わない）: K プロファイル 1..48 の D_K・TP 腕を b 三分位／wall_kind／jh 帯（7-12 vs 他）で分割・
  決着後 48 本の先着 F = P(+0.5·risk 先着) − P(−0.5·risk 先着)（決着足 close 起点・runner 0.5R トレールが取れる形か）と双子の同統計・
  中央値・10% トリム平均（裾の確認）。
陽性対照: (a) 在 TP 腕の C_1（生・アンカーずらし無し）は c19 の lag1 負＋条件づけで負になるはず（符号校正）。(b) 注入 +0.10R を事象腕に足して t を印字（検出率）。
多重検定: 主 2 セル Bonferroni。副 ≈ 40 セルは記述。look-ahead: 全統計は決着後の計上・水準は決着時に既知。survivorship: 単一銘柄・連続 CFD。
事前の最重大反証: (1) bid のみ 1 社: 決着足直後の戻しはスプレッド正常化の人工物 → C' で 1 本ずらす。(2) 双子日に同じ時刻で“別の本”が決着して
  いる確率は低いが、双子も同じ週内ドリフト状態にある（差し引き過剰の可能性＝保守側）。(3) 継続が TP 水準でなく「ボラの高い状態」の顔なら
  D は正でも runner は取れない（F の先着で確認）。(4) scan は紙の TP=b 記帳で、実約定は TP 水準に戻らない 3.9%（c4）＝事象の定義が実と少しずれる。
昇格候補・入口/出口規則の提案ではない。
"""
import os, sys, time, json, math, datetime as dt
import numpy as np
from zoneinfo import ZoneInfo

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
OUT_MD = os.path.join(DATA, 'c59_post_exit_continuation_result.md')
OUT_LOG = os.path.join(DATA, 'c59_run.log')
SEED = 20261123
rng = np.random.default_rng(SEED)
LINES = []
def P(s=''):
    print(s); LINES.append(s)

def el(): return f'{time.time()-T0:.1f}s'

P(f'# AUREL [cycle59 研究レーン] 決着後の path（TP/SL 腕）・双子対照  {dt.datetime.now():%Y-%m-%d %H:%M}')

# ---------- load ----------
j = json.load(open(os.path.join(DATA, 'refute_c4_scan_paths_2010_2026.json'), encoding='utf-8'))
tr = j['trades']; n_all = len(tr)
et = np.array([t['entry_time'] for t in tr], dtype=np.int64)
hold = np.array([t['hold'] for t in tr], dtype=np.int64)
side = np.array([1 if t['side'] == 'BUY' else -1 for t in tr], dtype=np.int64)
risk = np.array([t['risk'] for t in tr], dtype=float)
bb = np.array([t['b'] for t in tr], dtype=float)
exitk = np.array([t['exit'] for t in tr])
year = np.array([t['year'] for t in tr])
jh = np.array([t['jh'] for t in tr])
wk = np.array([t['wall_kind'] for t in tr])
Rj = np.array([t['R'] for t in tr], dtype=float)
P(f'scan json: n {n_all}  exit TP {np.sum(exitk=="TP")} SL {np.sum(exitk=="SL")} TIME {np.sum(exitk=="TIME")}  ({el()})')

z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_ohlc.npz'))
ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); hi = z['high'].astype(float); lo = z['low'].astype(float)
N = len(ts)
flat = np.zeros(N, dtype=bool); flat[1:] = (cl[1:] == cl[:-1]) & (hi[1:] == lo[1:])
P(f'npz: {N} 本 {dt.datetime.fromtimestamp(int(ts[0]), dt.UTC):%Y-%m-%d} .. {dt.datetime.fromtimestamp(int(ts[-1]), dt.UTC):%Y-%m-%d}  flat 全体 {flat.mean()*100:.1f}%  ({el()})')
# 衛生 ⑪: flat 比率 曜日別
dow = ((ts // 86400) + 3) % 7  # 1970-01-01 = Thu(3) -> Mon=0
names = ['月','火','水','木','金','土','日']
P('  flat 曜日別: ' + ' '.join(f'{names[d]} {flat[dow==d].mean()*100:.1f}%' for d in range(7)))

def grid_idx(t):
    """ts -> index in grid; -1 if not present (holes)."""
    i = np.searchsorted(ts, t)
    i = np.clip(i, 0, N-1)
    ok = ts[i] == t
    return np.where(ok, i, -1)

ts_x = et + 300 * hold
ix = grid_idx(ts_x)
P(f'決着足 ts の格子一致 {np.mean(ix>=0)*100:.2f}%（穴で落ちる {np.sum(ix<0)} 本）')

# ---------- 整合 assert vs fullpaths ----------
fp = np.load(os.path.join(DATA, 'refute_c2_fullpaths.npz'))
P(f'fullpaths keys {fp.files}')
clR = fp['clR'].astype(float); off = fp['off'].astype(np.int64)
order = np.lexsort((hold, et))  # entry_time asc, hold tiebreak (§2 衛生)
# off has n+1 entries? handle both
if len(off) == n_all + 1:
    starts = off[:-1]; lens = np.diff(off)
else:
    starts = off; lens = np.append(np.diff(off), len(clR) - off[-1])
ok_len = np.mean(lens == hold[order] + 1)
P(f'fullpaths 長さ = hold+1 の一致 {ok_len*100:.2f}%')
last = clR[starts + lens - 1]; prev = clR[starts + lens - 2]
d_fp = last - prev  # in R, sorted order
ix_s = ix[order]; m = (ix_s >= 1) & (lens >= 2)
d_grid = side[order] * (cl[ix_s] - cl[np.maximum(ix_s - 1, 0)]) / risk[order]
match = np.abs(d_fp[m] - d_grid[m]) <= 0.02
P(f'整合: 決着足の Δcl（fullpaths vs 格子）|差|≤0.02R 一致 {match.mean()*100:.2f}%（n {m.sum()}）  ({el()})')
if match.mean() < 0.99:
    P('!! 整合 <99% — 停止'); open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(LINES)); sys.exit(1)

# ---------- event metrics ----------
NY = ZoneInfo('America/New_York')
KS = [1, 3, 6, 12, 24, 48]
KMAX = 49  # need ts_x + 300*(K+1) for anchor-shift up to K=48

def fwd_ok(i0, K, shift):
    """all bars i0+shift .. i0+shift+K non-flat, in range"""
    iend = i0 + shift + K
    okr = (i0 >= 0) & (iend < N)
    out = np.zeros(len(i0), dtype=bool)
    # cumulative flat count
    cf = np.concatenate([[0], np.cumsum(flat)])
    a = np.clip(i0 + shift, 0, N); b = np.clip(iend + 1, 0, N)
    nflat = cf[b] - cf[a]
    out[okr] = (nflat[okr] == 0)
    return out

def C_metric(i0, K, shift, s, rk):
    """s·(close[i0+shift+K] − close[i0+shift]) / risk"""
    a = i0 + shift; b = i0 + shift + K
    a = np.clip(a, 0, N-1); b = np.clip(b, 0, N-1)
    return s * (cl[b] - cl[a]) / rk

def first_passage(i0, s, rk, K=48, lev=0.5):
    """from close[i0]: P(+lev·risk first) − P(−lev·risk first) within K bars (close basis). returns per-event +1/-1/0."""
    base = cl[i0]
    idx = i0[:, None] + np.arange(1, K+1)[None, :]
    idx = np.clip(idx, 0, N-1)
    path = s[:, None] * (cl[idx] - base[:, None]) / rk[:, None]
    up = path >= lev; dn = path <= -lev
    fu = np.where(up.any(1), up.argmax(1), K+5); fd = np.where(dn.any(1), dn.argmax(1), K+5)
    res = np.zeros(len(i0), dtype=int)
    res[(fu < fd)] = 1; res[(fd < fu)] = -1
    return res

def twin_idx(i0, days):
    return grid_idx(ts[np.clip(i0, 0, N-1)] + days * 86400)

def cluster_t(x, g):
    """mean, se (cluster by g), t"""
    x = np.asarray(x, float); g = np.asarray(g)
    n = len(x)
    if n < 5: return np.nan, np.nan, np.nan
    mu = x.mean()
    ug, inv = np.unique(g, return_inverse=True)
    sums = np.bincount(inv, weights=x - mu)
    G = len(ug)
    var = np.sum(sums**2) / (n**2) * (G / max(G-1, 1))
    se = math.sqrt(var)
    return mu, se, (mu/se if se > 0 else np.nan)

def win_mask(y, w):
    if w == '在 2010-20': return (y >= 2010) & (y <= 2020)
    if w == '外 2021-26H1': return (y >= 2021)
    if w == '近年 2024-26H1': return (y >= 2024)
    return np.ones_like(y, bool)
WINS = ['在 2010-20', '外 2021-26H1', '近年 2024-26H1']

day_x = ts_x // 86400  # cluster key (UTC day of settlement)
# ET clock for description
ET_hour = np.array([dt.datetime.fromtimestamp(int(t), NY).hour for t in ts_x])

base_ev = (ix >= 0) & np.isin(exitk, ['TP', 'SL'])
P(f'事象母数（TP/SL・格子あり）{base_ev.sum()}  TP {np.sum(base_ev & (exitk=="TP"))}  SL {np.sum(base_ev & (exitk=="SL"))}')

# precompute twins (±7 days) indices
tw_p = twin_idx(ix, +7); tw_m = twin_idx(ix, -7)

def arm_table(arm, K, shift, w, extra_mask=None):
    """returns dict with event mean, twin mean, paired D, se, t, n, drop rate"""
    msk = base_ev & (exitk == arm) & win_mask(year, w)
    if extra_mask is not None: msk &= extra_mask
    n0 = msk.sum()
    okE = msk & fwd_ok(ix, K, shift) & (~flat[np.clip(ix,0,N-1)])
    cE = C_metric(ix, K, shift, side, risk)
    # twins
    okP = okE & (tw_p >= 0) & fwd_ok(tw_p, K, shift)
    okM = okE & (tw_m >= 0) & fwd_ok(tw_m, K, shift)
    cP = C_metric(tw_p, K, shift, side, risk); cM = C_metric(tw_m, K, shift, side, risk)
    nt = okP.astype(int) + okM.astype(int)
    cT = (np.where(okP, cP, 0) + np.where(okM, cM, 0)) / np.maximum(nt, 1)
    use = okE & (nt > 0)
    muE, seE, tE = cluster_t(cE[use], day_x[use])
    muT, seT, tT = cluster_t(cT[use], day_x[use])
    D, seD, tD = cluster_t(cE[use] - cT[use], day_x[use])
    return dict(n0=int(n0), n=int(use.sum()), drop=1 - use.sum()/max(n0,1), muE=muE, seE=seE, tE=tE, muT=muT, tT=tT,
                D=D, se=seD, t=tD, mde=2*seD if seD==seD else np.nan,
                med=float(np.median(cE[use]-cT[use])) if use.sum() else np.nan,
                trim=float(np.mean(np.sort(cE[use]-cT[use])[int(0.1*use.sum()):int(0.9*use.sum())])) if use.sum()>20 else np.nan,
                use=use)

P('\n## 1. 主セル D_12（アンカーずらし C\'・双子 D±7 対の差・決着日クラスタ SE）')
main = {}
for arm in ['TP', 'SL']:
    for w in WINS:
        r = arm_table(arm, 12, 1, w)
        main[(arm, w)] = r
        P(f'  - {arm} 腕 {w}: n {r["n"]}/{r["n0"]}（除外 {r["drop"]*100:.1f}%・窓 flat/穴/双子無し）'
          f'  事象 C\'_12 {r["muE"]:+.4f}R (t {r["tE"]:+.2f})  双子 {r["muT"]:+.4f} (t {r["tT"]:+.2f})'
          f'  **D_12 {r["D"]:+.4f}R  se {r["se"]:.4f}  t {r["t"]:+.2f}  MDE {r["mde"]:.4f}**  中央値 {r["med"]:+.4f}  trim10 {r["trim"]:+.4f}')

def verdict(arm):
    a = main[(arm, WINS[0])]; b = main[(arm, WINS[1])]
    pos = (a['D'] >= 0.03) and (a['t'] >= 2.5) and (b['D'] > 0) and (b['t'] >= 1.5)
    neg = (a['D'] <= -0.03) and (a['t'] <= -2.5) and (b['D'] < 0) and (b['t'] <= -1.5)
    if arm == 'TP':
        return 'H_CONT PASS（通過点）' if pos else ('H_REV PASS（終点）' if neg else 'null')
    return 'H_SLREV PASS（戻る）' if pos else ('H_SLCONT PASS（逆行継続）' if neg else 'null')
P(f'\n  判定 TP 腕: **{verdict("TP")}**   判定 SL 腕: **{verdict("SL")}**'
  f'  （条件: 在 |D|≥0.03 ∧ |t|≥2.5 ∧ 外 同符号 |t|≥1.5）')

P('\n## 2. 副: K プロファイル（D_K・アンカーずらし版 C\' と 生 C の両方・在／外）')
for arm in ['TP', 'SL']:
    for w in WINS[:2]:
        row = []
        for K in KS:
            r1 = arm_table(arm, K, 1, w); r0 = arm_table(arm, K, 0, w)
            row.append(f'K{K}: C\' {r1["D"]:+.3f} (t {r1["t"]:+.1f}) / 生 {r0["D"]:+.3f} (t {r0["t"]:+.1f})')
        P(f'  - {arm} {w}: ' + ' | '.join(row))

P('\n## 3. 陽性対照')
# (a) raw C_1 of TP arm in-sample (settlement-bar bounce, lag1 negative c19) — event only, no twin
for arm in ['TP', 'SL']:
    msk = base_ev & (exitk == arm) & win_mask(year, WINS[0]) & fwd_ok(ix, 1, 0) & (~flat[np.clip(ix,0,N-1)])
    c1 = C_metric(ix, 1, 0, side, risk)[msk]
    mu, se, t = cluster_t(c1, day_x[msk])
    P(f'  - (a) {arm} 腕 在 生 C_1（決着足 close → 次足 close・事象のみ）: {mu:+.4f}R (t {t:+.2f}・n {msk.sum()})  期待: TP 負／SL 正（条件づけ＋bid バウンス）')
# (b) injection
r = main[('TP', WINS[0])]
use = r['use']
cE = C_metric(ix, 12, 1, side, risk); cPp = C_metric(tw_p, 12, 1, side, risk); cMm = C_metric(tw_m, 12, 1, side, risk)
okP = (tw_p >= 0) & fwd_ok(tw_p, 12, 1); okM = (tw_m >= 0) & fwd_ok(tw_m, 12, 1)
nt = okP.astype(int) + okM.astype(int)
cT = (np.where(okP, cPp, 0) + np.where(okM, cMm, 0)) / np.maximum(nt, 1)
for inj in [0.03, 0.05, 0.10]:
    mu, se, t = cluster_t((cE[use] + inj) - cT[use], day_x[use])
    P(f'  - (b) 在 TP 腕に +{inj:.2f}R 注入: D {mu:+.4f} t {t:+.2f}（判定 t≥2.5 の検出 {"○" if t>=2.5 else "×"}）')

P('\n## 4. 副: TP 腕の分割（D_12・C\'・在／外）')
for w in WINS[:2]:
    msk_w = base_ev & (exitk == 'TP') & win_mask(year, w)
    qs = np.quantile(bb[msk_w], [1/3, 2/3])
    parts = {
        f'b 下三分位 (<{qs[0]:.2f})': bb < qs[0], f'b 中': (bb >= qs[0]) & (bb < qs[1]), f'b 上三分位 (≥{qs[1]:.2f})': bb >= qs[1],
        'wall outer': wk == 'outer', 'wall mid': wk == 'mid', 'jh7-12': (jh >= 7) & (jh <= 12), 'jh 他': ~((jh >= 7) & (jh <= 12)),
        'BUY': side == 1, 'SELL': side == -1,
    }
    row = []
    for nm, em in parts.items():
        r = arm_table('TP', 12, 1, w, em)
        row.append(f'{nm}: {r["D"]:+.3f} (t {r["t"]:+.1f}, n {r["n"]})')
    P(f'  - {w}: ' + ' | '.join(row))

P('\n## 5. 副: 決着後 48 本の先着 F = P(+0.5R 先着) − P(−0.5R 先着)（決着足 close 起点・close 判定・事象 vs 双子）')
for arm in ['TP', 'SL']:
    for w in WINS:
        msk = base_ev & (exitk == arm) & win_mask(year, w) & fwd_ok(ix, 48, 0) & (~flat[np.clip(ix,0,N-1)])
        okP = msk & (tw_p >= 0) & fwd_ok(tw_p, 48, 0)
        fE = first_passage(ix[msk], side[msk], risk[msk])
        fT = first_passage(tw_p[okP], side[okP], risk[okP])
        FE = fE.mean(); FT = fT.mean()
        pu = np.mean(fE == 1); pd_ = np.mean(fE == -1); nz = np.mean(fE == 0)
        seE = math.sqrt(np.var(fE) / len(fE)); seT = math.sqrt(np.var(fT) / max(len(fT),1))
        diff = FE - FT; sed = math.sqrt(seE**2 + seT**2)
        P(f'  - {arm} {w}: 事象 F {FE:+.3f}（+先着 {pu*100:.1f}%・−先着 {pd_*100:.1f}%・未決 {nz*100:.1f}%・n {len(fE)}）  双子 F {FT:+.3f} (n {len(fT)})  差 {diff:+.3f} (z {diff/sed if sed>0 else float("nan"):+.2f})')

P('\n## 6. 組成（記述）: 決着 ET 時の分布・risk・除外率')
for arm in ['TP', 'SL']:
    msk = base_ev & (exitk == arm)
    h = np.bincount(ET_hour[msk], minlength=24)
    top = np.argsort(h)[::-1][:5]
    P(f'  - {arm}: 決着 ET 時 上位 {", ".join(f"{int(t)}時 {h[t]}" for t in top)}  risk 中央値 在 {np.median(risk[msk & win_mask(year,WINS[0])]):.2f}／外 {np.median(risk[msk & win_mask(year,WINS[1])]):.2f} USD'
      f'  1h sd(C\'_12) 在 {np.std(C_metric(ix,12,1,side,risk)[msk & win_mask(year,WINS[0]) & fwd_ok(ix,12,1)]):.3f}／外 {np.std(C_metric(ix,12,1,side,risk)[msk & win_mask(year,WINS[1]) & fwd_ok(ix,12,1)]):.3f}R')

P(f'\n実行時間 {el()}  seed {SEED}  多年 scan 無し・外部通信無し')
open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(LINES))
open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(LINES))
print('written', OUT_MD)
