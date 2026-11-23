# -*- coding: utf-8 -*-
"""
[cycle63 研究レーン 2026-11-24] 【深化・ジャンプ後の価格（c60 系統）の決着: 位置/尺度 2 パラメータ模型で μ を測る】

問い: 5σ ジャンプ（c45 cache・UJ 腕）後 1 時間の価格変化 C'_12 は、同時刻の双子に対して **位置（ドリフト μ）** が動いているのか、
**尺度（分散 λ）** だけが動いているのか。反証 11-23 09:45 の補 c は「平均 +0.59σ は上側の裾が 4〜12 倍広がる副産物で位置ずらしでない」
と診断し、決着条件として「Q_E(p) ≈ μ + λ·Q_T(p) を分位回帰で当て、μ の区間が ±0.20σ を排除するか」を登記した（backlog 345・高）。
c60 の T1「反転は無い」は汎関数を言わない排除主張だったので broken。本サイクルはその汎関数を **位置母数 μ** に固定して決着させる。

=== 事前固定（この docstring を書いてから数字を見る・seed 20261123・乱数はブートストラップのみ）===
データ: data/c45_jumps_5sigma_declustered.csv（2166 事象）＋ data/macro/XAU_m5_close.npz（bid・完全格子）。既存キャッシュのみ・多年 scan 無し・MT5 無し・外部通信無し。
事象/双子/窓の構成は c60 と同一（GATE: c60 の主セル 在 UJ D'_12 +0.587／外 −0.131 を |Δ|≤0.002 で再現できなければ停止）:
  C'_K = s·1e4·(log cl[i0+1+K] − log cl[i0+1])/σ_trail（アンカー 1 本ずらし）・主 K=12・双子 = 同 ET 時:分 D±7 日（既定 2 本・候補 96 の格子 4 本 ±7,±14 を併記）・
  双子足自身 |r|≥4σ は除外・窓 = ブレイク帯を含まず flat ≤10%。窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（記述）。判定は 在→外（D2）。
模型 A（主）: p 格子 = 5,10,…,95（19 点）。Q_E(p) = 事象 C' の分位・Q_T(p) = プール双子（有効本すべて）の分位。OLS で Q_E(p) = μ_A + λ_A·Q_T(p)。
  μ_A = 「双子分布を λ 倍したうえで何 σ ずれているか」＝位置母数。λ_A = 尺度比。
模型 B（副・記述）: ヒンジ Q_E(p) = μ_B + λ_lo·min(Q_T(p)−m_T, 0) + λ_hi·max(Q_T(p)−m_T, 0)（m_T = 双子中央値）＝非対称尺度を許した位置。
  補 c の「上側だけ広がる」が真なら λ_hi ≫ λ_lo で、μ_A は上側の裾に引かれて μ_B より正に出るはず（事前の予測）。
se: ET 日クラスタ・ブートストラップ（事象側と双子側を別々に再抽出・B=1000）。CI95 = est ± 2se（百分位 CI 併記）。
判定（主セル 1 つ = UJ 在 μ_A・外は符号脚）:
  EXCL = 在 CI95 ⊂ (−0.20, +0.20) → 「±0.20σ の位置ずらしを在で排除」。
  REV  = 在 μ_A ≤ −0.20 ∧ t ≤ −2.0 ∧ 外 μ_A < 0 ∧ t ≤ −1.5。CONT = 対称正。
  それ以外 = underpowered（候補 93）。その場合 **何を排除したか**を書く: 反転 ≤ (μ̂−2se) を排除／継続 ≥ (μ̂+2se) を排除。
  0.20σ の根拠 = c60（往復スプレッド 0.16 USD ≈ ジャンプ σ の 12〜20%）。
模型の適合（事前に決める読み方）: 模型 A の残差 e(p) を p で Spearman。|ρ|≥0.7 ∧ 端点 p5/p95 の |e|/se ≥2 なら「A は誤特定＝μ_A は分位加重の位置推定にすぎない」と明記し μ_B を主たる解釈に回す（判定語は A の規則で出す）。
陽性対照: (a) 事象側に −0.20σ を注入 → μ_A が −0.20 動く（a = Δμ̂/δ・位置模型なら 1.00）。(b) 事象側を 0 を中心に ×1.3 スケール → Δμ_A（尺度が μ に漏れる量・非対称なら ≠0）。
感度（記述）: p 格子 10..90／25..75・双子 4 本・K = 3/48・腕 SJ/ANN・μ の bp／USD 換算（候補 95）。
多重検定: 主 1 セル（在 |t|≥2.0）。記述 ≈ 40 セル。look-ahead: 統計は i0+1 以降の格子 close のみ・σ_trail は厳密 trailing（c45）・双子は対照のみ。survivorship: 単一銘柄・連続 CFD・bid 1 社。
事前の予測: 在 μ_A ≈ +0.1〜+0.2σ・se ≈ 0.15 → 継続 +0.20 は排除できず反転 ≤ −0.20 は排除（＝underpowered・片側排除）。模型 A は誤特定（残差 単調）。外は CI 幅 ≥0.6σ。
事前の最重大反証: (1) 分位格子 OLS は分位点を等重み・独立とみなす＝μ_A は格子の選び方に依存（10..90／25..75 で感度）。(2) 双子は「大きな足の後」という条件づけを揃えない
  （反証 09:45 A5: 5σ 事象に較正済み対照は作れない）→ μ は「無条件の同時刻足に対する位置ずれ」であり、分散拡大（c47 既知）は模型が λ で吸収する前提。(3) bid 1 社。
昇格候補・入口/出口規則の提案ではない。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
T0 = time.time(); SEED = 20261123; B = 1000
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT_MD = os.path.join(DATA, 'c63_postjump_location_scale_result.md'); OUT_LOG = os.path.join(DATA, 'c63_run.log')
L = []
def P(s=''):
    print(s); L.append(s)
def el(): return f'{time.time()-T0:.1f}s'
P(f'# AUREL [cycle63 研究レーン] ジャンプ後 1h の位置/尺度 2 パラメータ模型（UJ・双子対照・σ 単位）  {dt.datetime.now():%Y-%m-%d %H:%M}')

ev = pd.read_csv(os.path.join(DATA, 'c45_jumps_5sigma_declustered.csv'))
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_close.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); N = len(ts)
lc = np.log(cl); r = np.r_[np.nan, np.diff(lc)] * 1e4; flat = ~(np.isfinite(r) & (r != 0))
P(f'c45 cache {len(ev)} 事象・npz {N} 本 {dt.datetime.fromtimestamp(int(ts[0]), dt.UTC):%Y-%m-%d}..{dt.datetime.fromtimestamp(int(ts[-1]), dt.UTC):%Y-%m-%d}・flat {flat.mean()*100:.1f}%  ({el()})')
dow = ((ts // 86400) + 3) % 7; names = ['月','火','水','木','金','土','日']
P('  flat 曜日別（⑪）: ' + ' '.join(f'{names[d]} {flat[dow==d].mean()*100:.1f}%' for d in range(7)))
NY = ZoneInfo('America/New_York'); tny = pd.to_datetime(ts, unit='s', utc=True).tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); brk = (hr == 17) | ((hr == 18) & (mn < 10))
cf = np.concatenate([[0], np.cumsum(flat.astype(np.int64))]); cb = np.concatenate([[0], np.cumsum(brk.astype(np.int64))])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i] == t, i, -1)
tsev = ev.ts.to_numpy(np.int64); i0 = gidx(tsev); s = np.sign(ev.r_bp.to_numpy()); sig = ev.sigma_bp.to_numpy(float)
yr = pd.to_datetime(ev.et_date).dt.year.to_numpy(); etd = ev.et_date.to_numpy(); cls = ev.cls.to_numpy(); slot = ev.sched_slot.to_numpy()
arm = np.where(cls == 'UJ', 'UJ', np.where(cls == 'SJ', 'SJ', np.where(slot == 1, 'ANN', 'EVO')))
ok0 = i0 >= 0; r_re = np.where(ok0, r[np.maximum(i0, 0)], np.nan)
P(f'事象足 格子一致 {ok0.mean()*100:.2f}%・cache r_bp vs npz |差|≤0.05bp {np.mean(np.abs(r_re - ev.r_bp.to_numpy())[ok0] <= 0.05)*100:.2f}%')
WIN = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}
px_med = {w: float(np.median(cl[i0[ok0 & m]])) for w, m in WIN.items()}

def win_ok(i, K, sh=1):
    a = i + sh; b = i + sh + K; inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cb[bb] - cb[aa]) == 0) & ((cf[bb] - cf[aa]) <= max(1, int(0.10 * (K + 1))))
def Cm(i, K, sh=1):
    a = np.clip(i + sh, 0, N-1); b = np.clip(i + sh + K, 0, N-1); return s * (lc[b] - lc[a]) * 1e4 / sig
def twins(days, K):
    out = []
    for d in days:
        it = gidx(tsev + d * 86400); rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
        okT = win_ok(it, K) & (it >= 0) & np.isfinite(rr) & (rr < 4 * sig)
        out.append((Cm(it, K), okT))
    return out

# ---------- GATE: c60 主セル（対の平均差）を再現 ----------
P('\n## 0. GATE（c60 主セルの再現・対の平均差・ET 日クラスタ）')
def clus(x, g):
    n = len(x); m = x.mean(); e = x - m
    se = math.sqrt(float((pd.Series(e).groupby(g).sum()**2).sum())) / n; return m, se, n
tw2 = twins((-7, 7), 12); okE12 = win_ok(i0, 12); CE12 = Cm(i0, 12)
CT = np.zeros(len(ev)); nT = np.zeros(len(ev))
for c, okT in tw2: CT += np.where(okT, c, 0); nT += okT
okP = okE12 & (nT >= 1); Dp = CE12 - CT / np.maximum(nT, 1)
gate = {}
for w, wm in WIN.items():
    m = okP & wm & (arm == 'UJ'); mm, se, n = clus(Dp[m], etd[m]); gate[w] = mm
    P(f'- UJ D\'_12 {w}: {mm:+.4f}σ (se {se:.4f}・t {mm/se:+.2f}・n {n})')
if abs(gate['在 2010-20'] - 0.587) > 0.002 or abs(gate['外 2021-26H1'] - (-0.131)) > 0.002:
    P('!! GATE FAIL — c60 主セルを再現できない。停止'); open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(L)); sys.exit(1)
P('GATE PASS（|Δ| ≤ 0.002）')

# ---------- 分位模型 ----------
PS_MAIN = np.arange(5, 96, 5)
def qfit(xe, xt, ps):
    """returns dict: muA, lamA, residA(p), muB, lam_lo, lam_hi, qE, qT"""
    qE = np.percentile(xe, ps); qT = np.percentile(xt, ps)
    X = np.c_[np.ones(len(ps)), qT]; bA = np.linalg.lstsq(X, qE, rcond=None)[0]
    resA = qE - X @ bA
    mT = np.percentile(xt, 50); dq = qT - mT
    XB = np.c_[np.ones(len(ps)), np.minimum(dq, 0), np.maximum(dq, 0)]; bB = np.linalg.lstsq(XB, qE, rcond=None)[0]
    return dict(muA=bA[0], lamA=bA[1], resA=resA, muB=bB[0], lam_lo=bB[1], lam_hi=bB[2], qE=qE, qT=qT, mT=mT)
rng = np.random.default_rng(SEED)
def boot_idx(g, B):
    code, uq = pd.factorize(g); G = len(uq); order = np.argsort(code, kind='stable')
    cnt = np.bincount(code, minlength=G); st = np.r_[0, np.cumsum(cnt)[:-1]]
    for _ in range(B):
        pick = rng.integers(0, G, G)
        yield np.concatenate([order[st[p]:st[p]+cnt[p]] for p in pick])
def analyse(xe, ge, xt, gt, ps, B=B, extra_resid=False):
    f = qfit(xe, xt, ps)
    bs = []
    for ie, it in zip(boot_idx(ge, B), boot_idx(gt, B)):
        g = qfit(xe[ie], xt[it], ps); bs.append([g['muA'], g['lamA'], g['muB'], g['lam_lo'], g['lam_hi']] + (list(g['resA']) if extra_resid else []))
    bs = np.array(bs); se = bs.std(axis=0, ddof=1); pc = np.percentile(bs, [2.5, 97.5], axis=0)
    f['se'] = se; f['pc'] = pc; f['mean_diff'] = xe.mean() - xt.mean(); f['nE'] = len(xe); f['nT'] = len(xt)
    return f
def pool(a, wm, K, twl):
    okE = win_ok(i0, K); CE = Cm(i0, K); base = okE & wm & (arm == a)
    xe = CE[base]; ge = etd[base]
    xt = np.concatenate([c[okT & wm & (arm == a)] for c, okT in twl]); gt = np.concatenate([etd[okT & wm & (arm == a)] for c, okT in twl])
    return xe, ge, xt, gt
def line(tag, f, w=None, unit_extra=True):
    muA, lamA, muB, llo, lhi = f['muA'], f['lamA'], f['muB'], f['lam_lo'], f['lam_hi']; se = f['se']; pc = f['pc']
    t = muA / se[0]
    sx = f'- {tag}: **μ_A {muA:+.3f}σ (se {se[0]:.3f}・t {t:+.2f}・CI95 [{muA-2*se[0]:+.3f},{muA+2*se[0]:+.3f}]・百分位 [{pc[0,0]:+.3f},{pc[1,0]:+.3f}])**・λ_A {lamA:.3f} (se {se[1]:.3f})・' \
         f'μ_B {muB:+.3f} (se {se[2]:.3f}・t {muB/se[2]:+.2f})・λ_lo {llo:.3f} (se {se[3]:.3f})／λ_hi {lhi:.3f} (se {se[4]:.3f})・平均差 {f["mean_diff"]:+.3f}・n {f["nE"]}/{f["nT"]}'
    P(sx)

RES = {}
P('\n## 1. 主セル: UJ・K=12・双子 2 本（±7）・p 格子 5..95（19 点）・B=1000 ET 日クラスタ bootstrap')
for w, wm in WIN.items():
    xe, ge, xt, gt = pool('UJ', wm, 12, tw2)
    f = analyse(xe, ge, xt, gt, PS_MAIN, extra_resid=True); RES[('UJ', w)] = f
    line(f'UJ {w}', f)
    sigm = sig[win_ok(i0, 12) & wm & (arm == 'UJ')].mean()
    P(f'    bp/USD 換算（候補 95）: μ_A {f["muA"]*sigm:+.2f} bp = {f["muA"]*sigm/1e4*px_med[w]:+.3f} USD・μ_B {f["muB"]*sigm:+.2f} bp・往復スプレッド 0.16 USD = {0.16/px_med[w]*1e4/sigm:.3f}σ')
    # 適合: 残差 e(p)
    res = f['resA']; se_res = f['se'][5:]; zres = res / np.where(se_res > 0, se_res, np.nan)
    rho = pd.Series(res).corr(pd.Series(PS_MAIN.astype(float)), method='spearman')
    P(f'    模型 A 残差 e(p): ' + ' '.join(f'p{p} {e:+.2f}({zz:+.1f})' for p, e, zz in zip(PS_MAIN, res, zres) if p in (5, 10, 25, 50, 75, 90, 95)) + f'・Spearman(e,p) {rho:+.2f}・max|z| {np.nanmax(np.abs(zres)):.1f}')
    mis = (abs(rho) >= 0.7) and (abs(zres[0]) >= 2 or abs(zres[-1]) >= 2)
    f['misspec'] = mis; f['rho_res'] = rho
    P(f'    → 模型 A {"誤特定（単調残差・端点有意）＝μ_A は分位加重の位置推定" if mis else "適合は規則上 可"}')
    P(f'    分位 事象: ' + ' '.join(f'p{p} {q:+.2f}' for p, q in zip(PS_MAIN, f['qE']) if p in (5, 25, 50, 75, 95)) + ' ／ 双子: ' + ' '.join(f'p{p} {q:+.2f}' for p, q in zip(PS_MAIN, f['qT']) if p in (5, 25, 50, 75, 95)))

P('\n## 2. 判定（事前規則・主セル UJ 在 μ_A・外は符号脚）')
fi, fo = RES[('UJ', '在 2010-20')], RES[('UJ', '外 2021-26H1')]
mi, si = fi['muA'], fi['se'][0]; mo, so = fo['muA'], fo['se'][0]; ti, to = mi / si, mo / so
lo_i, hi_i = mi - 2 * si, mi + 2 * si
if lo_i > -0.20 and hi_i < 0.20: verdict = 'EXCL（±0.20σ の位置ずらしを在で排除）'
elif mi <= -0.20 and ti <= -2.0 and mo < 0 and to <= -1.5: verdict = 'REV PASS'
elif mi >= 0.20 and ti >= 2.0 and mo > 0 and to >= 1.5: verdict = 'CONT PASS'
else: verdict = 'underpowered（候補 93）'
P(f'- 在 μ_A {mi:+.3f} (t {ti:+.2f}) CI95 [{lo_i:+.3f},{hi_i:+.3f}]／外 μ_A {mo:+.3f} (t {to:+.2f}) CI95 [{mo-2*so:+.3f},{mo+2*so:+.3f}] → **{verdict}**')
P(f'- 排除できた範囲: 在 反転（位置）≤ {lo_i:+.3f}σ を排除・継続（位置）≥ {hi_i:+.3f}σ を排除／外 ≤ {mo-2*so:+.3f}・≥ {mo+2*so:+.3f}')
P(f'- 事前閾値 0.20σ に対する MDE（2se）: 在 {2*si:.3f}σ／外 {2*so:.3f}σ（c60 の平均 D の MDE 0.537／0.925 と比較）')
if fi.get('misspec'): P('- 注: 模型 A は在で誤特定（残差単調）→ 位置の解釈は μ_B（ヒンジ・双子中央値での位置）を主に読む: ' + f'在 μ_B {fi["muB"]:+.3f} (se {fi["se"][2]:.3f}・CI95 [{fi["muB"]-2*fi["se"][2]:+.3f},{fi["muB"]+2*fi["se"][2]:+.3f}])／外 μ_B {fo["muB"]:+.3f} (se {fo["se"][2]:.3f}・CI95 [{fo["muB"]-2*fo["se"][2]:+.3f},{fo["muB"]+2*fo["se"][2]:+.3f}])')

P('\n## 3. 陽性対照（在 UJ）')
xe, ge, xt, gt = pool('UJ', WIN['在 2010-20'], 12, tw2)
f0 = qfit(xe, xt, PS_MAIN)
fa = qfit(xe - 0.20, xt, PS_MAIN); fb = qfit(xe * 1.3, xt, PS_MAIN)
P(f'- (a) 事象 −0.20σ 注入: μ_A {f0["muA"]:+.3f} → {fa["muA"]:+.3f}（Δ {fa["muA"]-f0["muA"]:+.3f}・回収 a {(fa["muA"]-f0["muA"])/(-0.20):.2f}）・μ_B Δ {fa["muB"]-f0["muB"]:+.3f}・λ_A 不変 {fa["lamA"]:.3f}')
P(f'- (b) 事象 ×1.3 スケール（0 中心）: μ_A Δ {fb["muA"]-f0["muA"]:+.3f}σ・λ_A {f0["lamA"]:.3f} → {fb["lamA"]:.3f}・μ_B Δ {fb["muB"]-f0["muB"]:+.3f}（尺度が位置に漏れる量＝事象分布の非対称性の指標）')
# bootstrap power for δ=±0.20 under the model: fraction of bootstrap reps where injected μ CI excludes 0 (approx via se)
P(f'- 事前閾値の検出可能性: δ=0.20 注入時の t = {(f0["muA"]+0.20)/si:+.2f}（在・規則 |t|≥2.0）／外 {(mo+0.20)/so:+.2f}（規則 1.5）')

P('\n## 4. 感度（記述）: p 格子・双子本数・K・腕')
for ps_name, ps in [('p 10..90', np.arange(10, 91, 5)), ('p 25..75', np.arange(25, 76, 5))]:
    for w in ['在 2010-20', '外 2021-26H1']:
        xe, ge, xt, gt = pool('UJ', WIN[w], 12, tw2); f = analyse(xe, ge, xt, gt, ps, B=400); line(f'UJ {w} {ps_name}', f)
tw4 = twins((-14, -7, 7, 14), 12)
for w in ['在 2010-20', '外 2021-26H1']:
    xe, ge, xt, gt = pool('UJ', WIN[w], 12, tw4); f = analyse(xe, ge, xt, gt, PS_MAIN, B=400); line(f'UJ {w} 双子 4 本', f)
for K in (3, 48):
    twK = twins((-7, 7), K)
    for w in ['在 2010-20', '外 2021-26H1']:
        xe, ge, xt, gt = pool('UJ', WIN[w], K, twK); f = analyse(xe, ge, xt, gt, PS_MAIN, B=400); line(f'UJ {w} K={K}', f)
for a in ('SJ', 'ANN'):
    for w in ['在 2010-20', '外 2021-26H1']:
        xe, ge, xt, gt = pool(a, WIN[w], 12, tw2)
        if len(xe) < 30: P(f'- {a} {w}: n {len(xe)} <30 skip'); continue
        f = analyse(xe, ge, xt, gt, PS_MAIN, B=400); line(f'{a} {w}', f)
# 上/下ジャンプ分割（bid 人工物: 下ジャンプの μ が正なら気配正常化の形）
for nm, sm in (('上ジャンプ', s > 0), ('下ジャンプ', s < 0)):
    for w in ['在 2010-20', '外 2021-26H1']:
        okE = win_ok(i0, 12); CE = Cm(i0, 12); base = okE & WIN[w] & (arm == 'UJ') & sm
        xe = CE[base]; ge = etd[base]
        xt = np.concatenate([c[okT & WIN[w] & (arm == 'UJ') & sm] for c, okT in tw2]); gt = np.concatenate([etd[okT & WIN[w] & (arm == 'UJ') & sm] for c, okT in tw2])
        f = analyse(xe, ge, xt, gt, PS_MAIN, B=400); line(f'UJ {w} {nm}', f)

P(f'\n実行 {el()}')
open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(L)); open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT_MD)
