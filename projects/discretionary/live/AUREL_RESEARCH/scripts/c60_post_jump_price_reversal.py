# -*- coding: utf-8 -*-
"""
[cycle60 研究レーン 2026-11-23] 【探索・市場微細構造（ジャンプ後の価格は戻るか続くか）】

問い: 金 5 分足の 5σ ジャンプ（c45 キャッシュ）の“後”、**価格そのもの**は戻る（反転）か続く（継続）か RW か。
これまで c24（NFP 公表足後 β≈0・月 1 回で決着不能）・c45/c56（ジャンプ後に建った scan 本の R）・c47（ジャンプ後のボラ水準）は測ったが、
**予定外ジャンプ（UJ）後の生の価格ドリフト**は未測定。文献の機構: 公開情報を伴わないジャンプは流動性の一時的枯渇・注文フローの不均衡で起こり、
流動性供給者が在庫を戻すにつれ部分的に反転する（Nagel 2012 の流動性供給リターン／Jiang–Yao 2013 の「情報なしジャンプは反転」）。
公表（情報）ジャンプは反転しない（または遅れた反応で継続）。→ 腕の差 UJ − ANN が機構判別。方向なしの保険需要とは別＝裁定で消え得る。

=== 事前固定（この docstring を書いてから数字を見る・seed 20261123・乱数は注入対照のみ使わず決定論）===
データ: data/c45_jumps_5sigma_declustered.csv（2166 事象・ts=ジャンプ足・r_bp 符号つき・sigma_bp=直前 σ_trail・cls EVDAY/SJ/UJ・sched_slot）
  ・data/macro/XAU_m5_close.npz（bid・暦時刻完全格子・前値埋め）。既存キャッシュのみ・多年 scan 無し・M5 原本読込なし・MT5 無し・外部通信無し。
整合 assert: キャッシュ r_bp と npz から再計算した 1e4·Δlog close の |差| ≤0.05 bp 一致率 ≥99% を要求（不一致なら停止）。
腕: UJ（非発表日・非定時分・937）／SJ（非発表日・定時分 :00/:15/:30/:45・786）／ANN（発表日 ∧ 公表スロット足・293）／EVO（発表日の非スロット足・150・記述）。
単位: 事象の σ_trail（sigma_bp）で割った σ 単位（腕・時代で |r| が違っても比較可能）。併記 = ジャンプ比（D/|z|）・bp・USD。
主統計（方法論 ㉙／91・アンカー 1 本ずらし）: C'_K = s·1e4·(log cl[i0+1+K] − log cl[i0+1]) / σ（s = sign(r_jump)・i0 = ジャンプ足）。主 K=12（1 時間）。
  副 K = 1,3,6,24,48。生 C_K = s·1e4·(log cl[i0+K] − log cl[i0])/σ も併記（ジャンプ足直後 1 本の bid バウンスはここに局在するはず）。
対照（双子・c59 型）: 同じ ET 時:分の D±7 日の足を起点に同じ C'_K（時刻帯・季節のドリフトを差し引く）。双子足が自身 |r| ≥4σ_event なら除外。
  2 本の平均・両方無ければ事象を落とす。D_K = mean(C'^event − C'^twin)。SE = 事象 ET 日クラスタ。t = D/SE。MDE = 2·SE。
窓有効性: 窓 [i0+1 .. i0+1+K] に ET 17:00–18:10 の足を含まない ∧ flat 足（r=0）が K の 10% 以下。除外率を印字。
窓（D2・判定は 在→外）: 在 2010-20／外 2021-26H1／近年 2024-26H1（記述）。
判定（主 2 セル・Bonferroni 2 → 在 |t| ≥2.5）:
  C1 UJ 腕 D'_12: H_REV PASS = 在 D ≤ −0.20σ ∧ t ≤ −2.5 ∧ 外 D <0 ∧ t ≤ −1.5／H_CONT PASS = 対称正。それ以外 null（MDE 併記）。
  C2 機構判別 Δ = D'_12(UJ) − D'_12(ANN): PASS = 在 |Δ| ≥0.20σ ∧ |t| ≥2.5 ∧ 外 同符号 ∧ |t| ≥1.5。
  0.20σ の根拠 = 口座スプレッド往復 0.16 USD ≈ σ_trail 中央値 5.3 bp × 価格 1500〜2500 USD ≈ 0.8〜1.3 USD の 12〜20%＝受け取れる最小の大きさ。
  事前の予測 = C1 null か弱い反転（文献は株・ここは bid 1 社の 5 分格子）・C2 null（c47 で 2〜4 h 後のボラ水準は腕で同じ）。
副（記述・判定に使わない）: K プロファイル・UJ の上/下ジャンプ分割（**bid 人工物の診断**: 下ジャンプだけ戻るなら気配拡大→正常化の顔）・
  UJ の ET 08–10 時 vs 他・|z| 三分位と用量反応（C'_12 on z の傾き）・UJ_open（c55 の開場スロット: ET 08:20/08:25・09:35/09:40・03:00/03:05・20:00/20:05）vs UJ_other・
  先着 F' = P(ジャンプの半分を戻す 先着) − P(半分だけ延長 先着)（i0+1 の close 起点・48 本・事象のみ・対照なし＝条件づけ足起点なので記述のみ）・中央値・符号率。
陽性対照: (a) 生 C_1（ずらし無し）は在で負のはず（c19 lag1 負＋bid バウンス）。(b) UJ 腕に −0.20σ を注入して t（検出率）。
ゲート ㉛: scan 本（UJ 後 0〜4 h 建玉 β +0.089 t 1.06・c45）は既に測定済み → 本サイクルは走らせない（参照のみ）。
多重検定: 主 2 セル Bonferroni。副 ≈ 60 セルは記述。look-ahead: 全統計はジャンプ足の後の格子 close のみ・σ_trail はジャンプ足を含まない。survivorship: 単一銘柄・連続 CFD。
事前の最重大反証: (1) bid 1 社: 下ジャンプで気配が広がり数本かけて正常化すると「反転」に見える（上/下分割で診断・XAU ask M1【要取得】が決着条件）。
  (2) 5 分足の 5σ は 1 分のジャンプと 5 分のボラ・バースト（Christensen–Oomen–Podolskij 2014）を区別しない＝UJ 腕は混合（|z| 三分位で部分診断）。
  (3) 双子は「ジャンプの無い普通の日」なので条件づけ（大きな足の後）を揃えない＝RMT（反証 11-23）の問題。ただし主統計は平均 D（条件づけに鈍い・c59）で先着/符号率は記述に留める。
  (4) 時刻集中（ET 08–10 に 55%）: 時刻の背景ドリフトは双子が差し引くが、08:30 公表の第 2 波（UJ に残る）は情報ジャンプの混入。
昇格候補・入口/出口規則の提案ではない。
"""
import os, sys, time, math, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT_MD = os.path.join(DATA, 'c60_post_jump_price_reversal_result.md'); OUT_LOG = os.path.join(DATA, 'c60_run.log')
LINES = []
def P(s=''):
    print(s); LINES.append(s)
def el(): return f'{time.time()-T0:.1f}s'
P(f'# AUREL [cycle60 研究レーン] 5σ ジャンプ後の価格（反転/継続）・腕 UJ/SJ/ANN・双子対照  {dt.datetime.now():%Y-%m-%d %H:%M}')

# ---------- load ----------
ev = pd.read_csv(os.path.join(DATA, 'c45_jumps_5sigma_declustered.csv'))
P(f'c45 cache: {len(ev)} 事象・cls ' + ' '.join(f'{k} {v}' for k, v in ev.cls.value_counts().items()) + f'  ({el()})')
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_close.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); N = len(ts)
lc = np.log(cl); r = np.r_[np.nan, np.diff(lc)] * 1e4; flat = ~(np.isfinite(r) & (r != 0))
P(f'npz: {N} 本 {dt.datetime.fromtimestamp(int(ts[0]), dt.UTC):%Y-%m-%d} .. {dt.datetime.fromtimestamp(int(ts[-1]), dt.UTC):%Y-%m-%d}  flat 全体 {flat.mean()*100:.1f}%  ({el()})')
dow = ((ts // 86400) + 3) % 7; names = ['月','火','水','木','金','土','日']
P('  flat 曜日別（⑪）: ' + ' '.join(f'{names[d]} {flat[dow==d].mean()*100:.1f}%' for d in range(7)))
NY = ZoneInfo('America/New_York')
tny = pd.to_datetime(ts, unit='s', utc=True).tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy()
brk = (hr == 17) | ((hr == 18) & (mn < 10))  # ET 日次ブレイク帯
cf = np.concatenate([[0], np.cumsum(flat.astype(np.int64))]); cb = np.concatenate([[0], np.cumsum(brk.astype(np.int64))])

def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i] == t, i, -1)

i0 = gidx(ev.ts.to_numpy(np.int64)); ok0 = i0 >= 0
P(f'事象足の格子一致 {ok0.mean()*100:.2f}%（落ちる {np.sum(~ok0)}）')
r_re = np.where(ok0, r[np.maximum(i0, 0)], np.nan)
match = np.abs(r_re - ev.r_bp.to_numpy()) <= 0.05
P(f'整合: cache r_bp vs npz 再計算 |差|≤0.05 bp 一致 {match[ok0].mean()*100:.2f}%（n {ok0.sum()}）')
if match[ok0].mean() < 0.99:
    P('!! 整合 <99% — 停止'); open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(LINES)); sys.exit(1)

s = np.sign(ev.r_bp.to_numpy()); sig = ev.sigma_bp.to_numpy(float); zabs = ev.z.to_numpy(float)
yr = pd.to_datetime(ev.et_date).dt.year.to_numpy(); etd = ev.et_date.to_numpy()
cls = ev.cls.to_numpy(); slot = ev.sched_slot.to_numpy()
arm = np.where(cls == 'UJ', 'UJ', np.where(cls == 'SJ', 'SJ', np.where(slot == 1, 'ANN', 'EVO')))
P('腕: ' + ' '.join(f'{a} {np.sum(arm==a)}' for a in ['UJ','SJ','ANN','EVO']) + f'・UJ 上 {np.sum((arm=="UJ")&(s>0))}／下 {np.sum((arm=="UJ")&(s<0))}')
P(f'σ_trail 中央値 {np.median(sig):.2f} bp・|z| 中央値 UJ {np.median(zabs[arm=="UJ"]):.2f}／SJ {np.median(zabs[arm=="SJ"]):.2f}／ANN {np.median(zabs[arm=="ANN"]):.2f}')
px_med = {w: float(np.median(cl[i0[(i0>=0)&m]])) for w, m in [('在', (yr<=2020)), ('外', (yr>=2021)), ('近年', (yr>=2024))]}
P('価格中央値 USD: ' + '・'.join(f'{k} {v:.0f}' for k, v in px_med.items()) + '  → 往復 0.16 USD = ' + '・'.join(f'{k} {0.16/v*1e4:.2f} bp' for k, v in px_med.items()))

KS = [1, 3, 6, 12, 24, 48]; KMAIN = 12
def win_ok(i, K, shift):
    a = i + shift; b = i + shift + K  # bars a..b inclusive
    inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    nfl = cf[bb] - cf[aa]; nbr = cb[bb] - cb[aa]
    return inr & (nbr == 0) & (nfl <= max(1, int(0.10 * (K + 1))))
def Cm(i, K, shift, sg, sgm):
    a = np.clip(i + shift, 0, N-1); b = np.clip(i + shift + K, 0, N-1)
    return sg * (lc[b] - lc[a]) * 1e4 / sgm

# twins: same ET h:m, D±7 days
tw = [gidx(ev.ts.to_numpy(np.int64) + d * 86400) for d in (-7, 7)]
def twin_bad(it):
    # twin bar itself a big move (|r| >= 4 σ_event) or missing
    rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
    return (it < 0) | ~np.isfinite(rr) | (rr >= 4 * sig)

def paired(K, shift, mask):
    """returns D per event (event − mean twin), validity mask"""
    okE = win_ok(i0, K, shift) & mask
    CE = Cm(i0, K, shift, s, sig)
    CT = np.zeros(len(ev)); nT = np.zeros(len(ev))
    for it in tw:
        okT = win_ok(it, K, shift) & ~twin_bad(it)
        c = Cm(it, K, shift, s, sig); CT += np.where(okT, c, 0.0); nT += okT
    ok = okE & (nT >= 1)
    D = CE - CT / np.maximum(nT, 1)
    return D, CE, ok

def clus(x, g):
    """mean, clustered se (by g), n, n_clusters"""
    n = len(x)
    if n < 3: return np.nan, np.nan, n, 0
    m = x.mean(); e = x - m
    df_ = pd.DataFrame({'e': e, 'g': g}).groupby('g')['e'].sum()
    se = math.sqrt(float((df_**2).sum())) / n
    return m, se, n, len(df_)
def fmt(m, se, n, g, unit='σ'):
    t = m / se if se and se > 0 else np.nan
    return f'{m:+.3f}{unit} (se {se:.3f}・t {t:+.2f}・MDE {2*se:.3f}・n {n}/{g} 日)'

WIN = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}
ARMS = ['UJ', 'SJ', 'ANN', 'EVO']
res = {}  # (arm, win, K, shift) -> (m, se, n, g, Dvec, mask)

P('\n## 1. 主統計 D\'_K（アンカー 1 本ずらし・双子対差・σ 単位・ET 日クラスタ）')
for K in KS:
    for shift in (1, 0):
        D, CE, ok = paired(K, shift, np.ones(len(ev), bool))
        for a in ARMS:
            for w, wm in WIN.items():
                m = ok & wm & (arm == a)
                mm, se, n, g = clus(D[m], etd[m])
                res[(a, w, K, shift)] = (mm, se, n, g, D[m], m)
                if shift == 1 and K == KMAIN:
                    excl = 1 - m.sum() / max(1, np.sum(wm & (arm == a)))
                    P(f'- D\'_12 {a:4s} {w:14s}: {fmt(mm, se, n, g)}・除外 {excl*100:.1f}%・事象側 生平均 {CE[m].mean():+.3f}σ・ジャンプ比 {mm/np.mean(zabs[m]):+.3f}・bp {mm*np.mean(sig[m]):+.2f}')

P('\n## 2. 判定（事前規則）')
def g(a, w, K=12, sh=1): return res[(a, w, K, sh)]
mi, si, *_ = g('UJ', '在 2010-20'); mo, so, *_ = g('UJ', '外 2021-26H1')
ti, to = mi / si, mo / so
c1 = 'H_REV PASS' if (mi <= -0.20 and ti <= -2.5 and mo < 0 and to <= -1.5) else ('H_CONT PASS' if (mi >= 0.20 and ti >= 2.5 and mo > 0 and to >= 1.5) else 'null')
P(f'- C1 UJ D\'_12: 在 {mi:+.3f}σ t {ti:+.2f}／外 {mo:+.3f}σ t {to:+.2f} → **{c1}**（MDE 在 {2*si:.3f}／外 {2*so:.3f}σ）')
# C2: UJ − ANN difference, cluster se on union
def diff_cell(w):
    _, _, _, _, Du, mu = g('UJ', w); _, _, _, _, Da, ma = g('ANN', w)
    x = np.concatenate([Du, Da]); gg = np.concatenate([etd[mu], etd[ma]]); ind = np.concatenate([np.ones(len(Du)), np.zeros(len(Da))])
    # regression D on indicator, cluster se: diff of means; se via cluster sums of residuals with group centering
    m1, m0 = Du.mean(), Da.mean(); e = np.where(ind == 1, x - m1, x - m0)
    n1, n0 = len(Du), len(Da)
    # influence: for diff of means, cluster-robust se = sqrt(sum_g (sum_{i in g} (ind_i e_i/n1 - (1-ind_i) e_i/n0))^2)
    inf = np.where(ind == 1, e / n1, -e / n0)
    se = math.sqrt(float((pd.Series(inf).groupby(gg).sum()**2).sum()))
    return m1 - m0, se, n1, n0
di, sdi, n1i, n0i = diff_cell('在 2010-20'); do, sdo, n1o, n0o = diff_cell('外 2021-26H1'); dr, sdr, _, _ = diff_cell('近年 2024-26H1')
tdi, tdo = di / sdi, do / sdo
c2 = 'PASS' if (abs(di) >= 0.20 and abs(tdi) >= 2.5 and np.sign(do) == np.sign(di) and abs(tdo) >= 1.5) else 'null'
P(f'- C2 Δ = UJ − ANN D\'_12: 在 {di:+.3f}σ (se {sdi:.3f}・t {tdi:+.2f}・n {n1i}/{n0i})／外 {do:+.3f} (se {sdo:.3f}・t {tdo:+.2f}・n {n1o}/{n0o})／近年 {dr:+.3f} (t {dr/sdr:+.2f}) → **{c2}**')

P('\n## 3. K プロファイル（D\'_K・σ 単位・t）')
P('| 腕 | 窓 | ' + ' | '.join(f'K{K}' for K in KS) + ' |'); P('|---|---|' + '---|' * len(KS))
for a in ARMS:
    for w in WIN:
        P(f'| {a} | {w} | ' + ' | '.join((lambda q: f'{q[0]:+.3f} ({q[0]/q[1]:+.1f})' if q[1] > 0 else 'nan')(res[(a, w, K, 1)]) for K in KS) + ' |')
P('\n生 C_K（ずらし無し・双子対差）: 陽性対照 (a) 在 K=1 は負のはず')
P('| 腕 | 窓 | ' + ' | '.join(f'K{K}' for K in KS) + ' |'); P('|---|---|' + '---|' * len(KS))
for a in ['UJ', 'SJ', 'ANN']:
    for w in WIN:
        P(f'| {a} | {w} | ' + ' | '.join((lambda q: f'{q[0]:+.3f} ({q[0]/q[1]:+.1f})' if q[1] > 0 else 'nan')(res[(a, w, K, 0)]) for K in KS) + ' |')

P('\n## 4. UJ の分割（D\'_12・記述）')
D12, CE12, ok12 = paired(12, 1, np.ones(len(ev), bool))
open_slot = np.isin(ev.et_hour.to_numpy() * 100 + ev.et_min.to_numpy(), [820, 825, 935, 940, 300, 305, 2000, 2005])
us_morn = (ev.et_hour.to_numpy() >= 8) & (ev.et_hour.to_numpy() <= 10)
zt = {}
for w, wm in WIN.items():
    mu = ok12 & wm & (arm == 'UJ')
    if mu.sum() >= 30:
        q = np.quantile(zabs[mu], [1/3, 2/3]); zt[w] = q
splits = {'上ジャンプ': s > 0, '下ジャンプ': s < 0, 'ET 08-10': us_morn, 'ET 他': ~us_morn, '開場スロット': open_slot, '非開場': ~open_slot}
for w, wm in WIN.items():
    base = ok12 & wm & (arm == 'UJ')
    row = []
    for nm, sm in splits.items():
        m = base & sm; mm, se, n, gg = clus(D12[m], etd[m]); row.append(f'{nm} {mm:+.3f} (t {mm/se if se>0 else np.nan:+.1f}・n {n})')
    if w in zt:
        q = zt[w]
        for nm, sm in [('|z| 下', zabs < q[0]), ('|z| 中', (zabs >= q[0]) & (zabs < q[1])), ('|z| 上', zabs >= q[1])]:
            m = base & sm; mm, se, n, gg = clus(D12[m], etd[m]); row.append(f'{nm} {mm:+.3f} (t {mm/se if se>0 else np.nan:+.1f}・n {n})')
        # dose-response slope D on |z|
        x = zabs[base]; y = D12[base]
        if len(x) > 10:
            b = np.polyfit(x, y, 1)[0]; yhat = np.polyval(np.polyfit(x, y, 1), x); e = y - yhat
            xc = x - x.mean(); inf = xc * e / (xc**2).sum(); se_b = math.sqrt(float((pd.Series(inf).groupby(etd[base]).sum()**2).sum()))
            row.append(f'傾き D on |z| {b:+.3f}σ/z (t {b/se_b:+.1f})')
    P(f'- UJ {w}: ' + '・'.join(row))
# sign-split also for ANN/SJ (bid artefact diagnostic across arms)
for a in ['SJ', 'ANN']:
    for w, wm in WIN.items():
        base = ok12 & wm & (arm == a)
        out = []
        for nm, sm in [('上', s > 0), ('下', s < 0)]:
            m = base & sm; mm, se, n, gg = clus(D12[m], etd[m]); out.append(f'{nm} {mm:+.3f} (t {mm/se if se>0 else np.nan:+.1f}・n {n})')
        P(f'- {a} {w} 上/下: ' + '・'.join(out))

P('\n## 5. 先着 F\'・中央値・符号率（事象のみ・i0+1 close 起点・48 本・記述）')
def first_passage(i, sg, sgm, zz, K=48, frac=0.5):
    base_i = np.clip(i + 1, 0, N-1); base = lc[base_i]
    lev = frac * zz * sgm / 1e4  # half the jump in log units
    out = np.zeros(len(i))
    for k in range(1, K + 1):
        j = np.clip(base_i + k, 0, N-1); d = sg * (lc[j] - base)
        hit_ext = (d >= lev) & (out == 0); hit_rev = (d <= -lev) & (out == 0)
        out[hit_ext] = 1; out[hit_rev] = -1
    return out
for a in ['UJ', 'SJ', 'ANN']:
    for w, wm in WIN.items():
        m = win_ok(i0, 48, 1) & wm & (arm == a)
        fp = first_passage(i0[m], s[m], sig[m], zabs[m])
        pe, pr = (fp == 1).mean(), (fp == -1).mean(); F = pe - pr; seF = math.sqrt((pe + pr - F**2) / max(1, m.sum()))
        med = np.median(D12[m & ok12]); pos = (D12[m & ok12] > 0).mean()
        P(f'- {a} {w}: F\'(半分延長 − 半分戻し) {F:+.3f} (z {F/seF:+.1f}・延長 {pe*100:.0f}%・戻し {pr*100:.0f}%・未決 {(fp==0).mean()*100:.0f}%・n {m.sum()})・D\'_12 中央値 {med:+.3f}σ・P(D\'>0) {pos*100:.1f}%')

P('\n## 6. 陽性対照 (b) 注入 −0.20σ を UJ 腕へ')
for w in WIN:
    mm, se, n, gg, Dv, m = g('UJ', w)
    P(f'- UJ {w}: 注入後 D {mm-0.20:+.3f}σ・t {(mm-0.20)/se:+.2f}（判定規則 |t|≥2.5 在／1.5 外）')

P('\n## 7. 経済的大きさ（UJ D\'_12）')
for w in WIN:
    mm, se, n, gg, Dv, m = g('UJ', w)
    bp = mm * np.mean(sig[m]); usd = bp / 1e4 * px_med[w.split()[0]]
    P(f'- UJ {w}: D\'_12 {mm:+.3f}σ = {bp:+.2f} bp = {usd:+.3f} USD（往復スプレッド 0.16 USD・ジャンプ |r| 中央値 {np.median(np.abs(ev.r_bp.to_numpy()[m])):.1f} bp）')

P(f'\n実行 {el()}')
open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(LINES))
open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(LINES))
print('written', OUT_MD)
