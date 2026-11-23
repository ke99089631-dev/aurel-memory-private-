# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-24 03:30 補 b] refute_c63_shapeasym.py の 2 つの結果を数値で詰める（記述・新たな判定語は出さない）

本体で pre-registered に出た 2 点が追加の数字を要求している:
  (1) 攻撃D: 「事象 = 双子の純粋な位置・尺度変換」という帰無で、残差の max_p|z| の平均が 2.03・p95 が 3.17 だった。
      c63 の事前固定した誤特定規則は「|ρ(e,p)| ≥ 0.7 ∧ 端点 |z| ≥ 2」。閾値 2 は帰無で日常的に超える値なので、
      **規則そのものの偽陽性率（FPR）を帰無で測る**。c63 の方法論候補 108 は「単調と端点 |z|≥2 を独立条件にする」と
      提案したが、閾値を校正しなければ独立条件化は FPR を上げるだけ。校正後の閾値（帰無 p95/p99）も出す。
  (2) 攻撃I: 近似ゲート FAIL（同じ XAU・同じ 在 窓で λ_hi/λ_lo が c63 の 1.54 に対し近似では 1.22・差 0.594→0.245）。
      n は 655→1154 と増えているので検出力の話ではなく**点推定が半分になった**＝事象定義の仕様差で効果量が動く。
      どの仕様差が効いているかを 1 つずつ入れ替えて分解する（c45 cache を正本に）:
        S0 c63 厳密（UJ のみ・c45 の σ_bp・窓は break 除外＋flat ≤10%）
        S1 腕フィルタを外す（UJ+SJ+ANN+EVO）        ← 近似は UJ 分類を持てない
        S2 窓規則を厳密非 flat（0 本・break 規則なし）に ← 近似の窓規則
        S3 σ を「直前 288 本の非 flat r の std」に置換   ← 近似の σ
        S4 S1+S2+S3（＝近似の仕様を c45 の事象時刻で再現）
        S5 近似ビルドの事象のうち c45 UJ と時刻一致するものだけ
        S6 近似ビルドの事象のうち c45 全腕と時刻一致するものだけ
      これで「非対称は UJ 分類に依存するのか／σ・窓の定義に依存するのか」が分かる。
      前者なら攻撃I（US500 に UJ 分類が無い）は本当に不成立。後者なら c63 の非対称は仕様脆弱。

seed 20261124。記述のみ・判定語は本体の事前規則で既に出した。書き込みは AUREL_RESEARCH/data のみ。
発注なし・本番編集なし・プロセス/執行機接触なし・MT5 なし・外部通信なし。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
T0 = time.time(); SEED = 20261124
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT_MD = os.path.join(DATA, 'refute_c63_shapeasym_b.md'); OUT_LOG = os.path.join(DATA, 'refute_c63_shapeasym_b_run.log')
L = []
def P(s=''):
    print(s); L.append(s)
def el(): return f'{time.time()-T0:.1f}s'
def flush():
    open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(L)); open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L))
P(f'# [REFUTE 補 b] c63 誤特定規則の帰無 FPR ＋ 非対称の仕様分解  {dt.datetime.now():%Y-%m-%d %H:%M}')

ev = pd.read_csv(os.path.join(DATA, 'c45_jumps_5sigma_declustered.csv'))
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_close.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); N = len(ts)
lc = np.log(cl); r = np.r_[np.nan, np.diff(lc)] * 1e4; flat = ~(np.isfinite(r) & (r != 0))
NY = ZoneInfo('America/New_York'); tny = pd.to_datetime(ts, unit='s', utc=True).tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); brk = (hr == 17) | ((hr == 18) & (mn < 10))
cf = np.concatenate([[0], np.cumsum(flat.astype(np.int64))]); cb = np.concatenate([[0], np.cumsum(brk.astype(np.int64))])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i] == t, i, -1)
tsev = ev.ts.to_numpy(np.int64); i0 = gidx(tsev); s = np.sign(ev.r_bp.to_numpy()); sig45 = ev.sigma_bp.to_numpy(float)
yr = pd.to_datetime(ev.et_date).dt.year.to_numpy(); etd = ev.et_date.to_numpy(); cls = ev.cls.to_numpy(); slot = ev.sched_slot.to_numpy()
arm = np.where(cls == 'UJ', 'UJ', np.where(cls == 'SJ', 'SJ', np.where(slot == 1, 'ANN', 'EVO')))
IS = yr <= 2020
# 近似 σ（攻撃I と同一定義・厳密 trailing）
rv = np.where(flat, np.nan, r); sr = pd.Series(rv)
sd288 = sr.rolling(288, min_periods=200).std().shift(1).to_numpy()
cnt288 = sr.notna().rolling(288, min_periods=1).sum().shift(1).to_numpy()
sig288_all = np.where((cnt288 >= 200) & np.isfinite(sd288) & (sd288 > 0), sd288, np.nan)
sig288 = np.where(i0 >= 0, sig288_all[np.maximum(i0, 0)], np.nan)
P(f'c45 {len(ev)} 事象・npz {N} 本・σ_bp(c45) 中位 {np.nanmedian(sig45):.2f} bp vs σ288 中位 {np.nanmedian(sig288):.2f} bp'
  f'・相関 {np.corrcoef(sig45[np.isfinite(sig288)], sig288[np.isfinite(sig288)])[0,1]:+.3f}  ({el()})')

PS = np.arange(5, 96, 5)
def qfit(xe, xt, ps=PS):
    qE = np.percentile(xe, ps); qT = np.percentile(xt, ps)
    X = np.c_[np.ones(len(ps)), qT]; bA = np.linalg.lstsq(X, qE, rcond=None)[0]; resA = qE - X @ bA
    mT = np.percentile(xt, 50); dq = qT - mT
    XB = np.c_[np.ones(len(ps)), np.minimum(dq, 0), np.maximum(dq, 0)]; bB = np.linalg.lstsq(XB, qE, rcond=None)[0]
    return dict(muA=bA[0], lamA=bA[1], resA=resA, muB=bB[0], lam_lo=bB[1], lam_hi=bB[2])
rng = np.random.default_rng(SEED)
def cprep(g):
    code, uq = pd.factorize(g); G = len(uq); order = np.argsort(code, kind='stable')
    cnt = np.bincount(code, minlength=G); st = np.r_[0, np.cumsum(cnt)[:-1]]
    return order, cnt, st, G
def bidx(g, B):
    order, cnt, st, G = cprep(g)
    for _ in range(B):
        pk = rng.integers(0, G, G)
        yield np.concatenate([order[st[p]:st[p]+cnt[p]] for p in pk])

# ============ (1) c63 の誤特定規則の帰無 FPR ============
P('\n## 1. c63 の誤特定規則「|ρ(e,p)|≥0.7 ∧ 端点|z|≥2」の帰無 FPR（事象=双子の純粋な位置尺度変換・B=2000）')
def wok(i, K=12, sh=1):
    a = i + sh; b = i + sh + K; inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cb[bb] - cb[aa]) == 0) & ((cf[bb] - cf[aa]) <= max(1, int(0.10 * (K + 1))))
def Cm(i, sgv, K=12, sh=1):
    a = np.clip(i + sh, 0, N-1); b = np.clip(i + sh + K, 0, N-1); return s * (lc[b] - lc[a]) * 1e4 / sgv
def twl(days=(-7, 7), K=12, sgv=None, base=None, strict=False, trunc=True):
    sgv = sig45 if sgv is None else sgv; base = tsev if base is None else base
    out = []
    for d in days:
        it = gidx(base + d * 86400); rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
        ok = (it >= 0) & np.isfinite(rr) & (wok_strict(it, K) if strict else wok(it, K))
        if trunc: ok = ok & (rr < 4 * sgv)
        out.append((Cm(it, sgv, K), ok))
    return out
def wok_strict(i, K=12, sh=1):
    a = i + sh; b = i + sh + K; inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cf[bb] - cf[aa]) == 0)

T2 = twl()
okE = wok(i0); CE = Cm(i0, sig45); base0 = okE & IS & (arm == 'UJ')
xe0 = CE[base0]; ge0 = etd[base0]
xt0 = np.concatenate([c[ok & IS & (arm == 'UJ')] for c, ok in T2]); gt0 = np.concatenate([etd[ok & IS & (arm == 'UJ')] for c, ok in T2])
g0 = qfit(xe0, xt0)
assert abs(g0['lam_hi'] - 1.685) < 0.005 and abs(g0['lam_lo'] - 1.091) < 0.005, 'GATE b FAIL'
P(f'- GATE b PASS: λ_lo {g0["lam_lo"]:.3f}／λ_hi {g0["lam_hi"]:.3f}・n {len(xe0)}/{len(xt0)}')

# 観測の bootstrap se（残差用）
BS = 1000
rows = []
for ie, it in zip(bidx(ge0, BS), bidx(gt0, BS)):
    g = qfit(xe0[ie], xt0[it]); rows.append(list(g['resA']))
se_res = np.array(rows).std(axis=0, ddof=1)
z_obs = g0['resA'] / se_res
rho_obs = pd.Series(g0['resA']).corr(pd.Series(PS.astype(float)), method='spearman')
P(f'- 観測: 残差 z = ' + ' '.join(f'p{p} {v:+.2f}' for p, v in zip(PS, z_obs) if p in (5, 10, 50, 90, 95))
  + f'・端点 max(|z(p5)|,|z(p95)|) {max(abs(z_obs[0]), abs(z_obs[-1])):.2f}・Spearman(e,p) {rho_obs:+.2f}'
  + f'・c63 規則（|ρ|≥0.7 ∧ 端点|z|≥2）は {"発火" if (abs(rho_obs)>=0.7 and max(abs(z_obs[0]),abs(z_obs[-1]))>=2) else "不発火"}')

BN = 2000
rng_n = np.random.default_rng(SEED + 7)
orderT, cntT, stT, GT = cprep(gt0)
mu_h, lam_h = g0['muA'], g0['lamA']
fire_c63 = 0; fire_end = 0; fire_rho = 0; fire_cand108 = 0
mx_end = np.zeros(BN); mx_all = np.zeros(BN); rho_n = np.zeros(BN)
for b in range(BN):
    pk = rng_n.integers(0, GT, GT)
    idxT = np.concatenate([orderT[stT[p]:stT[p]+cntT[p]] for p in pk])
    draw = xt0[idxT]; sel = rng_n.integers(0, len(draw), len(xe0))
    xs = mu_h + lam_h * draw[sel]
    g = qfit(xs, xt0)
    zz = g['resA'] / se_res
    rh = pd.Series(g['resA']).corr(pd.Series(PS.astype(float)), method='spearman')
    e_mx = max(abs(zz[0]), abs(zz[-1])); a_mx = np.nanmax(np.abs(zz))
    mx_end[b] = e_mx; mx_all[b] = a_mx; rho_n[b] = rh
    if abs(rh) >= 0.7: fire_rho += 1
    if e_mx >= 2: fire_end += 1
    if abs(rh) >= 0.7 and e_mx >= 2: fire_c63 += 1
    if abs(rh) >= 0.7 or e_mx >= 2: fire_cand108 += 1
P(f'- 帰無 FPR（α は名目 5% のつもりの規則）: **c63 規則「|ρ|≥0.7 ∧ 端点|z|≥2」= {fire_c63/BN*100:.1f}%**'
  f'・端点|z|≥2 単独 = **{fire_end/BN*100:.1f}%**・|ρ|≥0.7 単独 = {fire_rho/BN*100:.1f}%'
  f'・候補108「単調 OR 端点|z|≥2」= **{fire_cand108/BN*100:.1f}%**')
P(f'- 帰無分布: 端点 max|z| 平均 {mx_end.mean():.2f}・p95 **{np.percentile(mx_end,95):.2f}**・p99 {np.percentile(mx_end,99):.2f}'
  f'／全 p の max|z| 平均 {mx_all.mean():.2f}・p95 **{np.percentile(mx_all,95):.2f}**・p99 {np.percentile(mx_all,99):.2f}'
  f'／|ρ| 平均 {np.abs(rho_n).mean():.2f}・p95 {np.percentile(np.abs(rho_n),95):.2f}')
P(f'- 校正後の正しい閾値: 端点 |z| ≥ {np.percentile(mx_end,95):.2f}（5%）／{np.percentile(mx_end,99):.2f}（1%）'
  f'・全 p max|z| ≥ {np.percentile(mx_all,95):.2f}（5%）／{np.percentile(mx_all,99):.2f}（1%）')
P(f'- 観測 端点 max|z| {max(abs(z_obs[0]),abs(z_obs[-1])):.2f} の経験 p = **{np.mean(mx_end>=max(abs(z_obs[0]),abs(z_obs[-1]))):.4f}**'
  f'／全 p max|z| {np.nanmax(np.abs(z_obs)):.2f} の経験 p = **{np.mean(mx_all>=np.nanmax(np.abs(z_obs))):.4f}**')
flush()

# ============ (2) 非対称の仕様分解 ============
P('\n## 2. 非対称（λ_hi−λ_lo）の仕様分解 — 「どの仕様差で 0.594 → 0.245 になるのか」')
def cell(tag, armmask, sgv, strict, B=400):
    wk = wok_strict if strict else wok
    ok = wk(i0); C = Cm(i0, sgv)
    bs = ok & IS & armmask & np.isfinite(sgv)
    TW = twl(sgv=sgv, strict=strict)
    xe = C[bs]; ge = etd[bs]
    xt = np.concatenate([c[o & IS & armmask & np.isfinite(sgv)] for c, o in TW])
    gt = np.concatenate([etd[o & IS & armmask & np.isfinite(sgv)] for c, o in TW])
    if len(xe) < 80 or len(xt) < 80:
        P(f'- {tag}: n {len(xe)}/{len(xt)} 不足 skip'); return None
    g = qfit(xe, xt)
    rows = []
    for ie, it in zip(bidx(ge, B), bidx(gt, B)):
        gg = qfit(xe[ie], xt[it]); rows.append(gg['lam_hi'] - gg['lam_lo'])
    se = float(np.std(rows, ddof=1)); d = g['lam_hi'] - g['lam_lo']
    P(f'- {tag}: λ_lo {g["lam_lo"]:.3f}／λ_hi {g["lam_hi"]:.3f}・**差 {d:+.3f} (se {se:.3f}・z {d/se:+.2f})**'
      f'・λ_hi/λ_lo {g["lam_hi"]/g["lam_lo"]:.2f}・λ_A {g["lamA"]:.3f}・μ_A {g["muA"]:+.3f}・n {len(xe)}/{len(xt)}')
    return dict(d=d, se=se, z=d/se, ratio=g['lam_hi']/g['lam_lo'], lamA=g['lamA'], n=len(xe))
ALL = np.ones(len(ev), bool); UJ = (arm == 'UJ')
S = {}
S['S0 c63 厳密（UJ・σ45・窓 break+flat≤10%）'] = cell('S0 c63 厳密（UJ・σ45・窓 break+flat≤10%）', UJ, sig45, False)
S['S1 腕フィルタ外す（全腕・σ45・c63 窓）'] = cell('S1 腕フィルタ外す（全腕・σ45・c63 窓）', ALL, sig45, False)
S['S2 窓を厳密非 flat（UJ・σ45）'] = cell('S2 窓を厳密非 flat（UJ・σ45）', UJ, sig45, True)
S['S3 σ を σ288 に置換（UJ・c63 窓）'] = cell('S3 σ を σ288 に置換（UJ・c63 窓）', UJ, sig288, False)
S['S4 近似仕様 3 点同時（全腕・σ288・厳密窓）'] = cell('S4 近似仕様 3 点同時（全腕・σ288・厳密窓）', ALL, sig288, True)
for a in ('SJ', 'ANN', 'EVO'):
    S[f'（参考）腕 {a} のみ・c63 仕様'] = cell(f'（参考）腕 {a} のみ・c63 仕様', (arm == a), sig45, False)
flush()

# 近似ビルド事象 ∩ c45（攻撃I の近似ビルドを c45 時刻で絞る）
P('\n### 近似ビルド（攻撃I と同一: σ288・|r|≥5σ288・±288 デクラスタ・厳密窓）の事象を c45 時刻で絞る')
cand = np.where(np.isfinite(r) & np.isfinite(sig288_all) & (np.abs(r) >= 5 * sig288_all))[0]
ratio_c = np.abs(r[cand]) / sig288_all[cand]; ordr = cand[np.argsort(-ratio_c)]
kept = []; taken = np.zeros(N, bool)
for i in ordr:
    a, b = max(0, i-288), min(N, i+289)
    if taken[a:b].any(): continue
    kept.append(i); taken[i] = True
kept = np.array(sorted(kept))
tsk = ts[kept]; sgk = sig288_all[kept]; sk = np.sign(r[kept])
yk = pd.to_datetime(tsk, unit='s', utc=True).tz_convert(NY).year.to_numpy()
dk = pd.to_datetime(tsk, unit='s', utc=True).tz_convert(NY).strftime('%Y-%m-%d').to_numpy()
set_uj = set(tsev[UJ].tolist()); set_all = set(tsev.tolist())
inUJ = np.array([int(t) in set_uj for t in tsk]); inALL = np.array([int(t) in set_all for t in tsk])
P(f'- 近似ビルド {len(kept)} 事象（c45 は 2166）・c45 UJ と時刻一致 {int(inUJ.sum())}（c45 UJ 全体 {int(UJ.sum())}）・c45 全腕一致 {int(inALL.sum())}')
def cell_k(tag, m, B=400):
    def wk(i, K=12, sh=1):
        a = i + sh; b = i + sh + K; inr = (i >= 0) & (b < N) & (a >= 1)
        aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
        return inr & ((cf[bb] - cf[aa]) == 0)
    def Ck(i, sgv, K=12, sh=1):
        a = np.clip(i + sh, 0, N-1); b = np.clip(i + sh + K, 0, N-1); return sk * (lc[b] - lc[a]) * 1e4 / sgv
    ok = wk(kept); C = Ck(kept, sgk)
    bs = ok & (yk <= 2020) & m
    TW = []
    for d in (-7, 7):
        it = gidx(tsk + d * 86400); rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
        o = (it >= 0) & np.isfinite(rr) & wk(it) & (rr < 4 * sgk)
        TW.append((Ck(it, sgk), o))
    xe = C[bs]; ge = dk[bs]
    xt = np.concatenate([c[o & (yk <= 2020) & m] for c, o in TW]); gt = np.concatenate([dk[o & (yk <= 2020) & m] for c, o in TW])
    if len(xe) < 60 or len(xt) < 60: P(f'- {tag}: n {len(xe)}/{len(xt)} 不足 skip'); return None
    g = qfit(xe, xt); rows = []
    for ie, it in zip(bidx(ge, B), bidx(gt, B)):
        gg = qfit(xe[ie], xt[it]); rows.append(gg['lam_hi'] - gg['lam_lo'])
    se = float(np.std(rows, ddof=1)); d = g['lam_hi'] - g['lam_lo']
    P(f'- {tag}: λ_lo {g["lam_lo"]:.3f}／λ_hi {g["lam_hi"]:.3f}・**差 {d:+.3f} (se {se:.3f}・z {d/se:+.2f})**'
      f'・λ_hi/λ_lo {g["lam_hi"]/g["lam_lo"]:.2f}・λ_A {g["lamA"]:.3f}・μ_A {g["muA"]+0:+.3f}・n {len(xe)}/{len(xt)}')
    return dict(d=d, se=se, z=d/se, ratio=g['lam_hi']/g['lam_lo'])
S5 = cell_k('S5 近似ビルド ∩ c45 UJ・在', inUJ)
S6 = cell_k('S6 近似ビルド ∩ c45 全腕・在', inALL)
S7 = cell_k('S7 近似ビルド 全体・在（攻撃I の XAU-近似 在）', np.ones(len(kept), bool))
S8 = cell_k('S8 近似ビルド ∖ c45 全腕・在（c45 が拾わないジャンプ）', ~inALL)
flush()

P('\n## 3. まとめ（記述）')
if S.get('S0 c63 厳密（UJ・σ45・窓 break+flat≤10%）') and S.get('S4 近似仕様 3 点同時（全腕・σ288・厳密窓）'):
    s0 = S['S0 c63 厳密（UJ・σ45・窓 break+flat≤10%）']; s4 = S['S4 近似仕様 3 点同時（全腕・σ288・厳密窓）']
    P(f'- 仕様差の経路: S0 {s0["d"]:+.3f} → S4 {s4["d"]:+.3f}（{s4["d"]/s0["d"]*100:.0f}%）')
    for k in ('S1 腕フィルタ外す（全腕・σ45・c63 窓）', 'S2 窓を厳密非 flat（UJ・σ45）', 'S3 σ を σ288 に置換（UJ・c63 窓）'):
        if S.get(k): P(f'  - {k}: 差 {S[k]["d"]:+.3f}（S0 比 {S[k]["d"]/s0["d"]*100:.0f}%・z {S[k]["z"]:+.2f}）')
if S5 and S7: P(f'- 近似ビルドでも c45 UJ に絞れば 差 {S5["d"]:+.3f}（z {S5["z"]:+.2f}・λ_hi/λ_lo {S5["ratio"]:.2f}）／絞らなければ {S7["d"]:+.3f}（z {S7["z"]:+.2f}）')
P(f'\n実行 {el()}')
flush()
print('written', OUT_MD)
