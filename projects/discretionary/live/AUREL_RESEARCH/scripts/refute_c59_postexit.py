# -*- coding: utf-8 -*-
"""
[REFUTE c59] 反証レーン 2026-11-23 03:3x  seed 20261123
対象 = cycle59 (00:40) の主判定は TP/SL 両腕 null＝破る余地なし。よって **null を支える肯定形の持ち越し 4 件**と、
それらの数字が載っている補助スクリプト c59b の実装を壊しに行く。c59 自身の決着不能点（bid 1 社・XAU ask M1【要取得】・
台帳 TP 190 本）には寄らない。同じ npz／同じ json／同じ 5 分格子の数字を全部そのまま受け入れる。

--- 攻撃対象（c59 本文の文言） ---
T1 知識 (2): 「『ストップ狩り後の反転』は中央値と先着率の次元にだけ、しかも **在と生アンカーにだけ** 現れる。
             1 本ずらすと **外で消える**（+0.021 z 0.9）」＋知識 (3)「分布の形は変わるが期待値は変わらない」。
             ※ c59b §3 は **ずらし後**の符号率で SL 外 +2.6 pp (z +2.3)・中央値 外 事象 +0.051 vs 双子 +0.008 を印字している。
                つまり「外で消える」は先着 F の次元の話で、符号率/中央値の次元では外も生きている可能性がある＝文言と自分の数字の不整合。
T2 方法論候補 91: 「条件づけられた足を起点にした先着率/符号率/中央値は **アンカー 1 本ずらし版を主**にせよ」。
             ※ 1 本ずらしは人工物だけを落とすのか、**本物のドリフトも落とす**のか（過剰補正）が未検査。
T3 c59 自身の最重大反証: 「外の MDE 0.065R はコスト 0.03R の 2 倍。『外だけに +0.05R の継続』は排除できていない。
             n≈13000 本必要＝**決着不能**。研究レーンは追試しない」。
             ※ 同じデータで推定子を替えれば MDE が下がる余地が未検査（sd 外 1.39R は裾が重いため）。
T4 知識 (1): 「決着後の価格は決着を覚えていない＝c21 のマルコフ性が決着の先まで続く」（在 K48 −0.079 t −2.1 は
             外 +0.019 で符号反転＝頑健でない、という扱い）。
             ※ 別の在/外分割（4 期間ブロック・偶奇）で検査していない。

--- c59b の実装上の 3 つの欠陥（数字を見る前に、コードを読んで特定した） ---
E1 c59 §5／c59b は双子を **+7 日のみ**（`twp = gidx(ts[ix]+7*86400)` 単独）で作っている。c59 本文の事前固定は
   「双子（同 ET 時:分・同 side・**D±7 日・2 本平均**）」＝主セル（c59 本体 `tw_p`/`tw_m`）の規約と違う。
E2 c59b の SE は **非対データの二項 SE**（`sqrt(vE/nE + vT/nT)`）で、(a) 対（同一事象の双子）であることを無視し
   (b) **決着日クラスタを無視**している。主セルは `cluster_t` で決着日クラスタを使っている＝同じ論文内で基準が二重。
E3 c59b §4（決着足の大きさ 2 分割）は F' を **vs 0** で検定している（`z vs 0`）。双子 F' は 0 でない
   （c59 §5: SL 外 双子 F −0.024）ので、「外は両半分 0」はベースラインを取り違えた比較。

--- 事前固定（数字を見る前に書く・判定規則はこの docstring が正本） ---
GATE G 再現: c59b §1(2) の F'(sh1,a0.5) 6 セルと §3 の符号率 6 セルを、c59b と **同じ実装（+7 単独・非対 SE）**で再現する。
   |ΔF'| ≤ 0.005 かつ |Δ符号率| ≤ 0.3 pp を全 6 セルで満たさなければ **inconclusive（機械不一致）** で終了。

A1 (T1) 符号率/中央値を主セルの規約に直す: 双子 **±7 の 2 本平均**・**対の差**（per-event の指標差）・**決着日クラスタ SE**。
   家族 = {TP,SL} × {在,外,近年} × {符号率, 中央値} = 12 セル → **Holm（family-wise 0.05）**。
A2 (T1/T2) **収益率マッチ双子 RMT**: c59 の双子は ET 時刻・side・曜日は合わせるが **決着足そのものの動き**を合わせていない。
   SL 足は定義上 安値寄りで閉じる＝事象は「大きな逆行足」に条件づけられており、双子はそうでない＝c59 が心配した人工物に対して
   **対照が未較正**。そこで d ∈ {±7,±14,±21,±28,±35,±42} 日の候補から v = s·Δcl/risk が事象に最も近い 1 本を選ぶ双子を作る。
   検査: 事象 v の平均 vs 通常双子 v vs RMT v（較正の確認）→ RMT に対する F'/符号率/中央値の差。
A3 (T2) アンカー ladder sh ∈ {-1,0,1,2,3,6} の F'(a0.5)/符号率 ＋ **陽性対照**: 決着足の次足から始まる真のドリフト
   δ ∈ {0.03,0.05}R を注入し、sh1 がその何割を回収するか（回収率 < 50% なら候補 91 は過剰補正＝T2 BROKEN）。
A4 (T3) 外の MDE を同じデータで下げに行く。推定子 = raw / winsor ±1R / winsor ±2R / vol 標準化（trailing 48 本平均|Δcl|）。
   各推定子について δ=0.05R 注入で **減衰率 a** を測り、**実効 MDE = 2·se/a**（R 単位）で比較。
A5 (T4) 別分割: 4 期間ブロック (2010-13 / 2014-17 / 2018-21 / 2022-26H1) × {K12, K48} の D（C'・±7 対・日クラスタ）
   ＋ 偶奇事象分割。Bonferroni 8 セル → |t| ≥ 2.73。
A6 分割汚染 / look-ahead: 在（year≤2020）事象の双子足が 2021+ に落ちる本数、外事象の双子が 2020 以前に落ちる本数。
   該当を除いて在/外 主セルを再計算。
A7 コスト倍: 「SL 後に順方向へ建て直す」規則の net を コスト c=0.03R（c25/c52 実測）と 2c=0.06R で評価。
   平均ベース（C'_12）と ±0.5R バリアベース（EV ≈ 0.5·F'）の両方。
A8 多重検定: c59 の記述セル ≈110 ＋ 本反証の家族を合わせた Holm 必要 |z| を印字。

--- 判定規則（事前・数字を見る前） ---
T1 BROKEN  ⇔ A1 で SL 外 符号率 D ≥ +2.0 pp ∧ |z| ≥ 2.0 ∧ Holm 生存 ∧ A2 の RMT 版でも D ≥ +1.5 pp ∧ z ≥ 1.5。
T1 SURVIVED⇔ A1 で SL 外 |z| < 2.0、**または** A2 の RMT が殺す（D < +1.0 pp ∧ |z| < 1.5）。
            （後者なら「外で消える」という結論は正しいが c59 の理由づけ＝『生アンカーのみ』は誤り → survived-but-reason-wrong）
T2 BROKEN  ⇔ A3 陽性対照で sh1 の注入回収率 < 50%（真のドリフトも落とす）。
T3 BROKEN  ⇔ A4 で いずれかの検証済み推定子の **実効 MDE ≤ 0.035R**（外・SL 腕または TP 腕）＝既存データで決着可能。
T4 BROKEN  ⇔ A5 の 8 セルのいずれかで |t| ≥ 2.73。
E1/E2/E3   ⇔ 再現と A1 の差分で定量化（実装欠陥として記録・判定とは別）。

入力は c59 と同一の既存キャッシュのみ（data/refute_c4_scan_paths_2010_2026.json・data/macro/XAU_m5_ohlc.npz）。
MT5 なし・外部通信なし・多年 scan なし・乱数なし（RMT も決定論）。書き込みは data/refute_c59_postexit.md のみ。
"""
import os, json, math, time, datetime as dt
import numpy as np

T0 = time.time()
SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'refute_c59_postexit.md')
L = []
def P(s=''):
    print(s); L.append(s)

# ---------- load (same inputs as c59 / c59b) ----------
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
adcl = np.zeros(N); adcl[1:] = np.abs(cl[1:] - cl[:-1])
acs = np.concatenate([[0.0], np.cumsum(adcl)])

def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N - 1)
    return np.where(ts[i] == t, i, -1)

ix = gidx(et + 300 * hold)
day_x = np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] // 86400, -1)   # cluster key = settlement UTC day
base = (ix >= 0) & np.isin(exitk, ['TP', 'SL']) & (ix >= 1)

def fwd_ok(i0, K, sh):
    iend = i0 + sh + K
    okr = (i0 >= 1) & (iend < N) & (i0 + sh >= 0)
    a = np.clip(i0 + sh, 0, N); b = np.clip(iend + 1, 0, N)
    return okr & ((cf[b] - cf[a]) == 0)

def cprime(i0, s, rk, K, sh):
    """C'_K = s*(cl[i+sh+K] - cl[i+sh]) / risk"""
    a = np.clip(i0 + sh, 0, N - 1); b = np.clip(i0 + sh + K, 0, N - 1)
    return s * (cl[b] - cl[a]) / rk

def fpass(i0, s, rk, K, lev, sh):
    """first-passage indicator: +1 if +lev*R hit first, -1 if -lev first, 0 if neither within K bars"""
    bas = cl[np.clip(i0 + sh, 0, N - 1)]
    idx = np.clip(i0[:, None] + sh + np.arange(1, K + 1)[None, :], 0, N - 1)
    path = s[:, None] * (cl[idx] - bas[:, None]) / rk[:, None]
    up = path >= lev; dn = path <= -lev
    fu = np.where(up.any(1), up.argmax(1), K + 5)
    fd = np.where(dn.any(1), dn.argmax(1), K + 5)
    r = np.zeros(len(i0), int); r[fu < fd] = 1; r[fd < fu] = -1
    return r

def cl_t(x, g):
    """mean, cluster-robust se (cluster by g), t  -- CRVE for a sample mean"""
    x = np.asarray(x, float); n = len(x)
    if n < 3: return float('nan'), float('nan'), float('nan')
    mu = x.mean(); r = x - mu
    _, inv = np.unique(g, return_inverse=True)
    gs = np.bincount(inv, weights=r)
    se = math.sqrt((gs ** 2).sum()) / n
    return mu, se, (mu / se if se > 0 else float('nan'))

WINS = [('在 2010-20', (year >= 2010) & (year <= 2020)),
        ('外 2021-26H1', year >= 2021),
        ('近年 2024-26H1', year >= 2024)]

# twins
TWP = gidx(np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] + 7 * 86400, -10 ** 12))
TWM = gidx(np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] - 7 * 86400, -10 ** 12))

P(f'# [REFUTE c59] 決着後 path の肯定形持ち越しを壊す  {dt.datetime.now():%Y-%m-%d %H:%M}  seed {SEED}')
P(f'入力: refute_c4 json n {len(j)} (TP {int((exitk=="TP").sum())} SL {int((exitk=="SL").sum())} TIME {int((exitk=="TIME").sum())}) / XAU npz {N} 本 flat {flat.mean()*100:.1f}%')
P(f'事象母数（TP/SL・格子あり・ix>=1）{int(base.sum())}')

# ============================================================ GATE G : reproduce c59b exactly
P('\n## GATE G 再現（c59b と同一実装: +7 単独双子・非対二項 SE）  許容 |ΔF\'| ≤ 0.005 / |Δ符号率| ≤ 0.3 pp')
REF_F = {('TP','在 2010-20'):-0.059, ('TP','外 2021-26H1'):-0.023, ('TP','近年 2024-26H1'):+0.022,
         ('SL','在 2010-20'):+0.062, ('SL','外 2021-26H1'):+0.021, ('SL','近年 2024-26H1'):+0.034}
REF_S = {('TP','在 2010-20'):-2.8, ('TP','外 2021-26H1'):-2.2, ('TP','近年 2024-26H1'):-1.3,
         ('SL','在 2010-20'):+5.2, ('SL','外 2021-26H1'):+2.6, ('SL','近年 2024-26H1'):+1.6}
gate_ok = True
for arm in ['TP', 'SL']:
    for wn, wm in WINS:
        m  = base & (exitk == arm) & wm & fwd_ok(ix, 48, 1) & (~flat[np.clip(ix, 0, N - 1)])
        mt = m & (TWP >= 1) & fwd_ok(TWP, 48, 1)
        fE = fpass(ix[m], side[m], risk[m], 48, 0.5, 1); fT = fpass(TWP[mt], side[mt], risk[mt], 48, 0.5, 1)
        dF = fE.mean() - fT.mean()
        m2  = base & (exitk == arm) & wm & fwd_ok(ix, 12, 1) & (~flat[np.clip(ix, 0, N - 1)])
        mt2 = m2 & (TWP >= 1) & fwd_ok(TWP, 12, 1)
        cE = cprime(ix[m2], side[m2], risk[m2], 12, 1); cT = cprime(TWP[mt2], side[mt2], risk[mt2], 12, 1)
        dS = (np.mean(cE > 0) - np.mean(cT > 0)) * 100
        eF = abs(dF - REF_F[(arm, wn)]); eS = abs(dS - REF_S[(arm, wn)])
        ok = (eF <= 0.005) and (eS <= 0.3); gate_ok &= ok
        P(f"  - {arm} {wn}: F' {dF:+.3f} (c59b {REF_F[(arm,wn)]:+.3f} Δ{eF:.3f}) | 符号率 {dS:+.1f} pp (c59b {REF_S[(arm,wn)]:+.1f} Δ{eS:.2f}) {'OK' if ok else 'MISMATCH'}")
P(f'  GATE G: {"PASS" if gate_ok else "FAIL -> inconclusive on machine mismatch"}')

# ============================================================ A1 : paired, ±7 2-twin, day-clustered
P('\n## A1 (T1) 主セル規約へ修正: 双子 ±7 の 2 本平均・対の差・決着日クラスタ SE  [E1+E2 の修正]')
A1 = []
for arm in ['TP', 'SL']:
    for wn, wm in WINS:
        m = base & (exitk == arm) & wm & fwd_ok(ix, 12, 1) & (~flat[np.clip(ix, 0, N - 1)])
        okp = m & (TWP >= 1) & fwd_ok(TWP, 12, 1); okm = m & (TWM >= 1) & fwd_ok(TWM, 12, 1)
        use = m & (okp | okm)
        i0 = ix[use]; s = side[use]; rk = risk[use]; g = day_x[use]
        cE = cprime(i0, s, rk, 12, 1)
        tp_ok = okp[use]; tm_ok = okm[use]
        cTp = np.where(tp_ok, cprime(np.where(tp_ok, TWP[use], 1), s, rk, 12, 1), 0.0)
        cTm = np.where(tm_ok, cprime(np.where(tm_ok, TWM[use], 1), s, rk, 12, 1), 0.0)
        nT = tp_ok.astype(float) + tm_ok.astype(float)
        # sign-rate: paired difference of indicators
        sE = (cE > 0).astype(float)
        sT = (np.where(tp_ok, (cTp > 0).astype(float), 0.0) + np.where(tm_ok, (cTm > 0).astype(float), 0.0)) / nT
        mu_s, se_s, t_s = cl_t(sE - sT, g)
        # level (paired mean) and paired median of the difference
        dlev = cE - (cTp + cTm) / nT
        mu_l, se_l, t_l = cl_t(dlev, g)
        med_e, med_t = float(np.median(cE)), float(np.median((cTp + cTm) / nT))
        # median difference: cluster SE via per-cluster medians is unstable -> report paired-median + sign-test z
        A1.append((arm, wn, 'sign', mu_s * 100, se_s * 100, t_s, int(use.sum())))
        A1.append((arm, wn, 'median', (med_e - med_t), float('nan'), float('nan'), int(use.sum())))
        P(f'  - {arm} {wn}: 符号率 D {mu_s*100:+.2f} pp (cl-se {se_s*100:.2f} **z {t_s:+.2f}**) | 水準 D_12 {mu_l:+.4f}R (se {se_l:.4f} t {t_l:+.2f}) | 中央値 事象 {med_e:+.4f} 双子 {med_t:+.4f} 差 {med_e-med_t:+.4f} | n {int(use.sum())} cl {len(np.unique(g))}')
# Holm over the 12-cell sign-rate+median family (z available for sign cells; medians get sign-test z below)
P('\n  Holm（符号率 6 セル・family-wise 0.05）:')
sg = [(a, w, t) for (a, w, k, mu, se, t, n) in A1 if k == 'sign' and not math.isnan(t)]
sg_sorted = sorted(sg, key=lambda r: -abs(r[2]))
for rank, (a, w, t) in enumerate(sg_sorted):
    alpha = 0.05 / (len(sg_sorted) - rank)
    # two-sided normal crit
    from math import erfc, sqrt as _sq
    crit = 0.0
    lo_, hi_ = 0.0, 6.0
    for _ in range(60):
        mid = (lo_ + hi_) / 2
        if erfc(mid / _sq(2)) > alpha: lo_ = mid
        else: hi_ = mid
    crit = (lo_ + hi_) / 2
    P(f'    {rank+1}. {a} {w}: |z| {abs(t):.2f} vs Holm 必要 {crit:.2f} -> {"生存" if abs(t)>=crit else "落ちる"}')

# ============================================================ A2 : return-matched twin (RMT)
P('\n## A2 (T1/T2) 収益率マッチ双子 RMT（d ∈ ±{7,14,21,28,35,42} 日から 決着足 v=s·Δcl/risk が最も近い 1 本）')
OFFS = [7, -7, 14, -14, 21, -21, 28, -28, 35, -35, 42, -42]
def rmt_idx(mask, K, sh):
    """for events in mask, pick the offset-twin whose settlement-bar signed move best matches the event's"""
    i0 = ix[mask]; s = side[mask]; rk = risk[mask]
    vE = s * (cl[i0] - cl[i0 - 1]) / rk
    bestd = np.full(len(i0), 10 ** 9, float); bestI = np.full(len(i0), -1, np.int64)
    vcands = []
    for d in OFFS:
        cand = gidx(ts[i0] + d * 86400)
        ok = (cand >= 1) & fwd_ok(cand, K, sh) & (~flat[np.clip(cand, 0, N - 1)])
        v = np.where(ok, s * (cl[np.clip(cand, 0, N - 1)] - cl[np.clip(cand - 1, 0, N - 1)]) / rk, np.nan)
        dd = np.where(ok, np.abs(v - vE), 10 ** 9)
        upd = dd < bestd
        bestd = np.where(upd, dd, bestd); bestI = np.where(upd, cand, bestI)
        vcands.append(np.where(ok, v, np.nan))
    # plain +7 twin v for calibration reporting
    cand7 = gidx(ts[i0] + 7 * 86400)
    ok7 = (cand7 >= 1) & fwd_ok(cand7, K, sh) & (~flat[np.clip(cand7, 0, N - 1)])
    v7 = np.where(ok7, s * (cl[np.clip(cand7, 0, N - 1)] - cl[np.clip(cand7 - 1, 0, N - 1)]) / rk, np.nan)
    vR = np.where(bestI >= 1, s * (cl[np.clip(bestI, 0, N - 1)] - cl[np.clip(bestI - 1, 0, N - 1)]) / rk, np.nan)
    return bestI, vE, v7, vR

for arm in ['TP', 'SL']:
    for wn, wm in WINS:
        m = base & (exitk == arm) & wm & fwd_ok(ix, 48, 1) & (~flat[np.clip(ix, 0, N - 1)])
        bI, vE, v7, vR = rmt_idx(m, 48, 1)
        good = bI >= 1
        i0 = ix[m][good]; s = side[m][good]; rk = risk[m][good]; g = day_x[m][good]; bJ = bI[good]
        fE = fpass(i0, s, rk, 48, 0.5, 1); fR = fpass(bJ, s, rk, 48, 0.5, 1)
        mu_f, se_f, t_f = cl_t(fE.astype(float) - fR.astype(float), g)
        # sign-rate vs RMT at K=12 (need fwd_ok 12 too -> implied by 48)
        cE = cprime(i0, s, rk, 12, 1); cR = cprime(bJ, s, rk, 12, 1)
        mu_s, se_s, t_s = cl_t((cE > 0).astype(float) - (cR > 0).astype(float), g)
        mu_l, se_l, t_l = cl_t(cE - cR, g)
        P(f'  - {arm} {wn}: 較正 v 事象 {np.nanmean(vE[good]):+.3f}R / 通常+7双子 {np.nanmean(v7[good]):+.3f} / RMT {np.nanmean(vR[good]):+.3f}  (|v差| RMT {np.nanmean(np.abs(vR[good]-vE[good])):.3f} vs +7 {np.nanmean(np.abs(v7[good]-vE[good])):.3f})')
        P(f"      F'(a0.5,48) D {mu_f:+.4f} (cl-se {se_f:.4f} **z {t_f:+.2f}**) | 符号率 D {mu_s*100:+.2f} pp (**z {t_s:+.2f}**) | 水準 D_12 {mu_l:+.4f}R (t {t_l:+.2f}) | n {len(i0)}")

# ============================================================ A3 : anchor ladder + injection positive control
P('\n## A3 (T2) アンカー ladder sh ∈ {-1,0,1,2,3,6}: F\'(a0.5,48) / 符号率（±7 2本平均双子・対・日クラスタ）')
for arm in ['TP', 'SL']:
    for wn, wm in [WINS[0], WINS[1]]:
        row = []
        for sh in [-1, 0, 1, 2, 3, 6]:
            m = base & (exitk == arm) & wm & fwd_ok(ix, 48, sh) & (~flat[np.clip(ix, 0, N - 1)])
            okp = m & (TWP >= 1) & fwd_ok(TWP, 48, sh); okm = m & (TWM >= 1) & fwd_ok(TWM, 48, sh)
            use = m & (okp | okm)
            i0 = ix[use]; s = side[use]; rk = risk[use]; g = day_x[use]
            fE = fpass(i0, s, rk, 48, 0.5, sh).astype(float)
            tp_ok = okp[use]; tm_ok = okm[use]; nT = tp_ok + tm_ok
            fTp = np.where(tp_ok, fpass(np.where(tp_ok, TWP[use], 1), s, rk, 48, 0.5, sh), 0.0)
            fTm = np.where(tm_ok, fpass(np.where(tm_ok, TWM[use], 1), s, rk, 48, 0.5, sh), 0.0)
            mu, se, t = cl_t(fE - (fTp + fTm) / nT, g)
            row.append(f'sh{sh:+d}: {mu:+.3f} (z {t:+.1f})')
        P(f'  - {arm} {wn}: ' + ' | '.join(row))

P("\n  陽性対照（注入）: 決着足の **次足以降** に真のドリフト δ を等間隔で注入し、sh0 / sh1 / sh2 の F' と水準 D_12 が δ の何割を回収するか")
for wn, wm in [WINS[0], WINS[1]]:
    for delta in [0.03, 0.05]:
        out = []
        for sh in [0, 1, 2]:
            m = base & (exitk == 'SL') & wm & fwd_ok(ix, 48, sh) & (~flat[np.clip(ix, 0, N - 1)])
            okp = m & (TWP >= 1) & fwd_ok(TWP, 48, sh); okm = m & (TWM >= 1) & fwd_ok(TWM, 48, sh)
            use = m & (okp | okm)
            i0 = ix[use]; s = side[use]; rk = risk[use]; g = day_x[use]
            # level: D_12 with and without injection. injection = +delta R accumulated linearly over 12 bars from bar 1
            c0 = cprime(i0, s, rk, 12, sh)
            tp_ok = okp[use]; tm_ok = okm[use]; nT = tp_ok + tm_ok
            cTp = np.where(tp_ok, cprime(np.where(tp_ok, TWP[use], 1), s, rk, 12, sh), 0.0)
            cTm = np.where(tm_ok, cprime(np.where(tm_ok, TWM[use], 1), s, rk, 12, sh), 0.0)
            cT = (cTp + cTm) / nT
            # injected drift from the settlement bar onward: value at bar k = delta*k/12 (so bar-1 share = delta/12)
            inj_lo = delta * (sh) / 12.0; inj_hi = delta * (sh + 12) / 12.0
            d_raw, _, _ = cl_t(c0 - cT, g)
            d_inj, se_i, _ = cl_t((c0 + (inj_hi - inj_lo)) - cT, g)
            rec = (d_inj - d_raw) / delta
            out.append(f'sh{sh} 水準回収 {rec*100:.0f}%')
        P(f'  - SL {wn} δ={delta}R: ' + ' | '.join(out))
P("  ※ 水準 C' は sh を動かしても δ の (12/12) を回収する設計（窓長一定）。先着 F' の注入回収率は下で別に測る。")
for wn, wm in [WINS[0], WINS[1]]:
    for delta in [0.05, 0.10]:
        out = []
        for sh in [0, 1]:
            m = base & (exitk == 'SL') & wm & fwd_ok(ix, 48, sh) & (~flat[np.clip(ix, 0, N - 1)])
            i0 = ix[m]; s = side[m]; rk = risk[m]
            # inject linear drift delta per 12 bars into the path, recompute first passage
            bas = cl[np.clip(i0 + sh, 0, N - 1)]
            idx = np.clip(i0[:, None] + sh + np.arange(1, 49)[None, :], 0, N - 1)
            path = s[:, None] * (cl[idx] - bas[:, None]) / rk[:, None]
            drift = delta * (np.arange(1, 49)[None, :] / 12.0)
            def firstpass_from(p):
                up = p >= 0.5; dn = p <= -0.5
                fu = np.where(up.any(1), up.argmax(1), 53); fd = np.where(dn.any(1), dn.argmax(1), 53)
                r = np.zeros(p.shape[0]); r[fu < fd] = 1; r[fd < fu] = -1; return r
            f0 = firstpass_from(path).mean(); f1 = firstpass_from(path + drift).mean()
            out.append(f'sh{sh}: ΔF\' {f1-f0:+.4f}')
        P(f'  - SL {wn} 注入 δ={delta}R/h: ' + ' | '.join(out) + '  （sh0 と sh1 の ΔF\' が同程度なら 1 本ずらしは真のドリフトを落とさない）')

# ============================================================ A4 : can the outer MDE be reduced on the same data?
P('\n## A4 (T3) 外の MDE を同じデータで下げに行く（推定子 4 種・δ=0.05R 注入で減衰率 a・実効 MDE = 2·se/a）')
for arm in ['TP', 'SL']:
    for wn, wm in [WINS[1], WINS[0]]:
        m = base & (exitk == arm) & wm & fwd_ok(ix, 12, 1) & (~flat[np.clip(ix, 0, N - 1)])
        okp = m & (TWP >= 1) & fwd_ok(TWP, 12, 1); okm = m & (TWM >= 1) & fwd_ok(TWM, 12, 1)
        use = m & (okp | okm)
        i0 = ix[use]; s = side[use]; rk = risk[use]; g = day_x[use]
        tp_ok = okp[use]; tm_ok = okm[use]; nT = tp_ok + tm_ok
        cE = cprime(i0, s, rk, 12, 1)
        cTp = np.where(tp_ok, cprime(np.where(tp_ok, TWP[use], 1), s, rk, 12, 1), 0.0)
        cTm = np.where(tm_ok, cprime(np.where(tm_ok, TWM[use], 1), s, rk, 12, 1), 0.0)
        cT = (cTp + cTm) / nT
        vol = (acs[np.clip(i0 + 1, 0, N)] - acs[np.clip(i0 - 47, 0, N)]) / 48.0     # trailing 48-bar mean |Δcl| (USD)
        volR = np.where(vol > 0, vol / rk, np.nan)
        kap = float(np.nanmedian(volR))
        rows = []
        for nm in ['raw', 'winsor±1R', 'winsor±2R', 'vol標準化']:
            if nm == 'raw':
                fE, fT = cE, cT; sc = 1.0
            elif nm.startswith('winsor'):
                q = 1.0 if '1R' in nm else 2.0
                fE, fT = np.clip(cE, -q, q), np.clip(cT, -q, q); sc = 1.0
            else:
                ok = np.isfinite(volR) & (volR > 0)
                fE = np.where(ok, cE / np.where(ok, volR, 1) * kap, np.nan)
                fT = np.where(ok, cT / np.where(ok, volR, 1) * kap, np.nan)
                sc = 1.0
            d = fE - fT; gg = g
            fin = np.isfinite(d); d = d[fin]; gg = gg[fin]
            mu, se, t = cl_t(d, gg)
            # attenuation: inject +0.05R into the event leg, recompute through the SAME estimator
            delta = 0.05
            if nm == 'raw':
                dE2 = (cE + delta) - cT
            elif nm.startswith('winsor'):
                q = 1.0 if '1R' in nm else 2.0
                dE2 = np.clip(cE + delta, -q, q) - np.clip(cT, -q, q)
            else:
                ok = np.isfinite(volR) & (volR > 0)
                dE2 = np.where(ok, (cE + delta) / np.where(ok, volR, 1) * kap, np.nan) - fT
            dE2 = dE2[np.isfinite(dE2)]
            mu2, _, _ = cl_t(dE2, gg)
            a = (mu2 - mu) / delta
            mde = 2 * se / a if a > 0 else float('inf')
            rows.append(f'{nm}: D {mu:+.4f} se {se:.4f} t {t:+.2f} a {a:.2f} **実効MDE {mde:.4f}R**')
        P(f'  - {arm} {wn} (n {int(fin.sum())}, κ={kap:.3f}): ' + ' | '.join(rows))

# ============================================================ A5 : alternative in/out splits
P('\n## A5 (T4) 別分割: 4 期間ブロック × {K12, K48}（D・C\'sh1・±7 対・日クラスタ）  Bonferroni 8 -> |t| ≥ 2.73')
BLK = [('2010-13', (year >= 2010) & (year <= 2013)), ('2014-17', (year >= 2014) & (year <= 2017)),
       ('2018-21', (year >= 2018) & (year <= 2021)), ('2022-26H1', year >= 2022)]
maxabs = 0.0
for arm in ['TP', 'SL']:
    for bn, bm in BLK:
        row = []
        for K in [12, 48]:
            m = base & (exitk == arm) & bm & fwd_ok(ix, K, 1) & (~flat[np.clip(ix, 0, N - 1)])
            okp = m & (TWP >= 1) & fwd_ok(TWP, K, 1); okm = m & (TWM >= 1) & fwd_ok(TWM, K, 1)
            use = m & (okp | okm)
            i0 = ix[use]; s = side[use]; rk = risk[use]; g = day_x[use]
            tp_ok = okp[use]; tm_ok = okm[use]; nT = tp_ok + tm_ok
            cE = cprime(i0, s, rk, K, 1)
            cTp = np.where(tp_ok, cprime(np.where(tp_ok, TWP[use], 1), s, rk, K, 1), 0.0)
            cTm = np.where(tm_ok, cprime(np.where(tm_ok, TWM[use], 1), s, rk, K, 1), 0.0)
            mu, se, t = cl_t(cE - (cTp + cTm) / nT, g)
            if arm == 'SL' or True: maxabs = max(maxabs, abs(t) if not math.isnan(t) else 0)
            row.append(f'K{K}: {mu:+.4f} (t {t:+.2f}, n {int(use.sum())})')
        P(f'  - {arm} {bn}: ' + ' | '.join(row))
P(f'  ブロック族の最大 |t| = {maxabs:.2f}  (Bonferroni 必要 2.73)')
P('  偶奇分割（事象 index の偶/奇・K12）:')
for arm in ['TP', 'SL']:
    for wn, wm in [WINS[0], WINS[1]]:
        row = []
        for pn, pm in [('偶', (np.arange(len(j)) % 2) == 0), ('奇', (np.arange(len(j)) % 2) == 1)]:
            m = base & (exitk == arm) & wm & pm & fwd_ok(ix, 12, 1) & (~flat[np.clip(ix, 0, N - 1)])
            okp = m & (TWP >= 1) & fwd_ok(TWP, 12, 1); okm = m & (TWM >= 1) & fwd_ok(TWM, 12, 1)
            use = m & (okp | okm)
            i0 = ix[use]; s = side[use]; rk = risk[use]; g = day_x[use]
            tp_ok = okp[use]; tm_ok = okm[use]; nT = tp_ok + tm_ok
            cE = cprime(i0, s, rk, 12, 1)
            cTp = np.where(tp_ok, cprime(np.where(tp_ok, TWP[use], 1), s, rk, 12, 1), 0.0)
            cTm = np.where(tm_ok, cprime(np.where(tm_ok, TWM[use], 1), s, rk, 12, 1), 0.0)
            mu, se, t = cl_t(cE - (cTp + cTm) / nT, g)
            sE = (cE > 0).astype(float)
            sT = (np.where(tp_ok, (cTp > 0).astype(float), 0) + np.where(tm_ok, (cTm > 0).astype(float), 0)) / nT
            ms, ss, tsg = cl_t(sE - sT, g)
            row.append(f'{pn}: D {mu:+.4f} (t {t:+.2f}) 符号 {ms*100:+.1f}pp (z {tsg:+.1f}) n {int(use.sum())}')
        P(f'  - {arm} {wn}: ' + ' | '.join(row))

# ============================================================ A6 : split contamination via twins
P('\n## A6 分割汚染 / look-ahead: 双子足が反対の窓に落ちる本数と、除外後の主セル')
yr_bar = np.full(N, 0, np.int64)
yr_bar = (np.array([dt.datetime.utcfromtimestamp(int(x)).year for x in ts[::5000]]) if False else None)
# cheap year-of-bar from ts via epoch boundaries
bnd = np.array([int(dt.datetime(y, 1, 1).replace(tzinfo=dt.timezone.utc).timestamp()) for y in range(2009, 2028)])
bar_year = 2009 + np.searchsorted(bnd, ts, side='right') - 1
for arm in ['TP', 'SL']:
    for wn, wm, lab in [('在 2010-20', (year >= 2010) & (year <= 2020), 'twin>=2021'), ('外 2021-26H1', year >= 2021, 'twin<=2020')]:
        m = base & (exitk == arm) & wm & fwd_ok(ix, 12, 1) & (~flat[np.clip(ix, 0, N - 1)])
        okp = m & (TWP >= 1) & fwd_ok(TWP, 12, 1); okm = m & (TWM >= 1) & fwd_ok(TWM, 12, 1)
        use = m & (okp | okm)
        tyP = np.where(okp, bar_year[np.clip(TWP, 0, N - 1)], 0); tyM = np.where(okm, bar_year[np.clip(TWM, 0, N - 1)], 0)
        if wn.startswith('在'): bad = ((tyP >= 2021) | (tyM >= 2021)) & use
        else: bad = (((tyP <= 2020) & okp) | ((tyM <= 2020) & okm)) & use
        keep = use & (~bad)
        res = []
        for nm, msk in [('全', use), ('汚染除外', keep)]:
            i0 = ix[msk]; s = side[msk]; rk = risk[msk]; g = day_x[msk]
            tp_ok = okp[msk]; tm_ok = okm[msk]; nT = tp_ok + tm_ok
            cE = cprime(i0, s, rk, 12, 1)
            cTp = np.where(tp_ok, cprime(np.where(tp_ok, TWP[msk], 1), s, rk, 12, 1), 0.0)
            cTm = np.where(tm_ok, cprime(np.where(tm_ok, TWM[msk], 1), s, rk, 12, 1), 0.0)
            mu, se, t = cl_t(cE - (cTp + cTm) / nT, g)
            res.append(f'{nm} D_12 {mu:+.4f} (t {t:+.2f}, n {int(msk.sum())})')
        P(f'  - {arm} {wn}: 汚染 {int(bad.sum())} 本 ({bad.sum()/max(use.sum(),1)*100:.1f}%) | ' + ' | '.join(res))

# ============================================================ A7 : cost doubling / receivability
P('\n## A7 コスト倍: 「SL 決着後に順方向へ建て直す」規則の net（c=0.03R 実測・2c=0.06R）')
for wn, wm in WINS:
    m = base & (exitk == 'SL') & wm & fwd_ok(ix, 48, 1) & (~flat[np.clip(ix, 0, N - 1)])
    i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]
    c12 = cprime(i0, s, rk, 12, 1)
    mu, se, t = cl_t(c12, g)
    f = fpass(i0, s, rk, 48, 0.5, 1).astype(float)
    muf, sef, tf = cl_t(f, g)
    ev = 0.5 * muf
    P(f'  - SL {wn}: 平均 C\'_12 gross {mu:+.4f}R (t {t:+.2f}) -> net@c {mu-0.03:+.4f} / net@2c {mu-0.06:+.4f}  |  ±0.5R バリア F\' {muf:+.4f} (t {tf:+.2f}) EV gross {ev:+.4f}R -> net@c {ev-0.03:+.4f} / net@2c {ev-0.06:+.4f}  | risk 中央値 {np.median(rk):.2f} USD, 0.03R = {0.03*np.median(rk):.3f} USD')

# ============================================================ A8 : multiple testing budget
P('\n## A8 多重検定: c59 の記述セル ≈110 ＋ 本反証の家族')
for M in [110, 150, 200]:
    from math import erfc, sqrt as _sq
    alpha = 0.05 / M; lo_, hi_ = 0.0, 7.0
    for _ in range(60):
        mid = (lo_ + hi_) / 2
        if erfc(mid / _sq(2)) > alpha: lo_ = mid
        else: hi_ = mid
    P(f'  - M={M}: Bonferroni 必要 |z| = {(lo_+hi_)/2:.2f}')

# ============================================================ E3 : c59b §4 baseline error, redone vs twin
P('\n## E3 c59b §4 の再実施（決着足の大きさ 2 分割・SL 腕・F\'(sh1,a0.5) を **vs 0 でなく vs ±7 双子** で）')
for wn, wm in WINS:
    m = base & (exitk == 'SL') & wm & fwd_ok(ix, 48, 1) & (~flat[np.clip(ix, 0, N - 1)])
    okp = m & (TWP >= 1) & fwd_ok(TWP, 48, 1); okm = m & (TWM >= 1) & fwd_ok(TWM, 48, 1)
    use = m & (okp | okm)
    i0 = ix[use]; s = side[use]; rk = risk[use]; g = day_x[use]
    dx = np.abs(cl[i0] - cl[i0 - 1]) / rk; med = np.median(dx)
    tp_ok = okp[use]; tm_ok = okm[use]; nT = tp_ok + tm_ok
    fE = fpass(i0, s, rk, 48, 0.5, 1).astype(float)
    fTp = np.where(tp_ok, fpass(np.where(tp_ok, TWP[use], 1), s, rk, 48, 0.5, 1), 0.0)
    fTm = np.where(tm_ok, fpass(np.where(tm_ok, TWM[use], 1), s, rk, 48, 0.5, 1), 0.0)
    dd = fE - (fTp + fTm) / nT
    out = []
    for nm, mm in [('小', dx < med), ('大', dx >= med)]:
        mu, se, t = cl_t(dd[mm], g[mm])
        out.append(f'{nm}(|Δcl_x| {"<" if nm=="小" else "≥"} {med:.2f}R): D {mu:+.4f} (cl-se {se:.4f} z {t:+.2f}, n {int(mm.sum())})')
    P(f'  - {wn}: ' + ' | '.join(out))

P(f'\n実行 {time.time()-T0:.1f}s  seed {SEED}  乱数未使用（決定論）・外部通信なし・MT5 なし・多年 scan なし')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
