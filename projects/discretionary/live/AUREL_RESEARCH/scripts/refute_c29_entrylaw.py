# -*- coding: utf-8 -*-
"""
反証レーン 2026-11-10 11:15 — 対象: cycle29 (09:55) メタ「入口工夫が負ける法則」の数値形
（findings/2026-11-10.md L120-137・scripts/c29_meta_audit.py・scripts/c29b_realized_effect.py）

壊しに行く主張（cycle29 本文の表現）:
 T1 B2b「Δμ(f=0.5)=mean(R*|top)−mean(R*|all) の Welch t は t_welch(top,bottom)/2」と、それに基づく
    最重大反証 (ii)「近年 cont_24h_XAU +0.082R t 2.09 は 39 セル帰無（max|t|≈2.2 期待）の範囲」。
    ※ c8 反証 (11-06 02:30) は同じ特徴量の top−bottom 差を 外 +0.078 t 2.90 と報告している。
      Δμ(top−all) は定義上その半分だが、t は同じはず（var(top−all)=σ²/n）。
 T2 B1「Δμ ≈ 0.79〜0.90R × ρ（f=0.5）」「ρ 0.10 で上位 10% 保持 57%」「+0.05R に ρ 0.054〜0.064」
    ＝ Gaussian copula 1 族で求めた量。同じ Spearman ρ の別の依存構造で変わるか。
 T3 B3「n_req = 2(2σ/Δμ)²（t≥2）→ 0.05R に 2.2〜3.1 年 > レジーム長 2〜3 年」。
 T4「実現 |Δμ(f=0.5)| 在 ≤0.027R／外 ≤0.038R」＝ f=0.5・13 特徴量のみで取った上界。

判定規則（数字を見る前に固定）:
 R1 (T1): 近年 cont_24h_XAU の Δμ の置換 sd（循環シフト 1000 回）から t_perm = Δμ/sd_perm。
     t_perm / t_c29(2.09) が [1.6, 2.4] なら c29 の t は 2 倍過小（定義誤り）。
     その上で 13 特徴量 family-wise p（同窓・循環シフト）<0.05 かつ 2021-25（最新半年抜き）の t_welch ≥2 なら
     主張 (ii) broken。p_fw ≥0.10 なら survived。間は inconclusive。
 R2 (T2): 同じ Spearman ρ=0.10 を持つ別の依存構造（尾部狙い 1{R*≥q90}・勝ち側のみ max(z,0)・負け側のみ min(z,0)・
     SL 検知 −1{SL}・TP 検知 1{TP}）で Δμ(f=0.5) が Gaussian の [0.5, 1.5] 倍を外れる、または上位 10% 保持率 ≥75%
     となる構造が 1 つでもあれば「換算 ρ→Δμ の普遍性 broken（係数は Gaussian 固有）」。全部範囲内なら survived。
 R3 (T3): 実 R*（外）に Δμ=0.05 を注入（kept +0.05／rest −0.05・n/2 ずつ）し n=n_req（c29 式）と n_req/2 で
     検出力 P(t_welch ≥2)。n_req で ∈[0.70,0.90] かつ n_req/2 で ∈[0.40,0.60] なら
     「80% 検出力の式として survived・『t≥2 に要る本数』という表記は relabel（50% 検出力なら半分の年数）」。
     n_req で <0.60 または >0.95 なら broken。
 R4 (T4): 外 2021-26H1 で 13 特徴量 × f∈{0.3,0.5,0.7} × 上/下 = 78 セルを循環シフト置換 500 回で family-wise。
     |Δμ| ≥0.05R かつ p_fw <0.05 のセルが 1 つでもあれば「外 ≤0.038R の上界は f=0.5 固有＝broken」。無ければ survived。
 R5（記述・判定に使わない）: 近年 cont_24h_XAU を年別・2021-25・jh 7-12・壁種・コスト倍（R*−ft）で分解。
帰無（置換）: 窓内の取引順で 13 特徴量を同じ k 本 循環シフト（k∈[200, n−200]）。特徴量の自己相関・特徴量間相関・
 R* の時間クラスタを保存する（c8 §5 の週循環シフトと同趣旨）。iid シャッフルの sd も併記。
seed 20261110。入力 data/c8_crossasset_features.csv のみ。scan 無し・M5 無し・MT5 無し・外部通信無し。
D2: 窓別のみ。16 年一括の水準は使わない。
"""
import time, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, norm

t0 = time.time(); ROOT = Path(__file__).resolve().parents[1]; L = []
rng = np.random.default_rng(20261110)
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)

df = pd.read_csv(ROOT / 'data' / 'c8_crossasset_features.csv').sort_values('entry_time').reset_index(drop=True)
ft = 0.1 / df.risk.values
Rs = df.R.values + np.where(df.exit.values == 'TIME', -ft, ft)
Rs_cost2 = Rs - ft                      # 往復 1 回分を追加控除
yr = df.year.values; jh = df.jh.values; wk = df.wall_kind.values
exitv = df.exit.values
sgn = np.where(df.side.values == 'BUY', 1.0, -1.0)
known = {}
for a in ['XAU', 'US500', 'US100']:
    for h in ['4h', '24h']: known[f'cont_{h}_{a}'] = sgn * df[f'ret{h}_{a}'].values
for c in ['b', 'risk', 'jh', 'open_gap', 'atr']: known[c] = df[c].values.astype(float)
known['atr/risk'] = df.atr.values / df.risk.values
FEATS = list(known.keys())
win = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}

def welch(a, b):
    n1, n2 = len(a), len(b)
    if n1 < 3 or n2 < 3: return np.nan
    return (a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / n1 + b.var(ddof=1) / n2)

def cell(v, R, mask, f=0.5, side='top'):
    """Δμ = mean(R|kept) − mean(R|all), t_welch(kept, rest)"""
    ok = mask & np.isfinite(v)
    if ok.sum() < 50: return np.nan, np.nan, int(ok.sum())
    vv = v[ok]; rr = R[ok]
    if side == 'top':
        thr = np.quantile(vv, 1 - f); kept = vv > thr
    else:
        thr = np.quantile(vv, f); kept = vv < thr
    if kept.sum() < 20 or (~kept).sum() < 20: return np.nan, np.nan, int(ok.sum())
    return rr[kept].mean() - rr.mean(), welch(rr[kept], rr[~kept]), int(ok.sum())

def shift_feats(mask, k):
    """窓内（取引順）で全特徴量を同じ k だけ循環シフトした dict"""
    idx = np.where(mask)[0]; out = {}
    for nm in FEATS:
        v = known[nm].copy(); v[idx] = np.roll(known[nm][idx], k); out[nm] = v
    return out

P('# 反証 cycle29「入口工夫が負ける法則」(scripts/refute_c29_entrylaw.py)')
P(f'n {len(df)}・R* 平均 ' + '／'.join(f'{wn} {Rs[m].mean():+.4f} (sd {Rs[m].std(ddof=1):.3f}, n {m.sum()})' for wn, m in win.items()))

# ------------------------------------------------------------------ R0 再現
P('\n## R0 再現（c29b 表の Δμ と t_c29 = t_welch/2）')
rep = {}
for wn, m in win.items():
    d, t, n = cell(known['cont_24h_XAU'], Rs, m); rep[wn] = (d, t, n)
    P(f'- cont_24h_XAU {wn}: Δμ {d:+.4f}R・t_welch {t:+.2f}・t_c29(=t_welch/2) {t/2:+.2f}・n {n}')
d_in_jh, t_in_jh, _ = cell(known['jh'], Rs, win['在 2010-20'])
P(f'- jh 在: Δμ {d_in_jh:+.4f}R・t_welch {t_in_jh:+.2f}・t_c29 {t_in_jh/2:+.2f}')
assert abs(rep['近年 2024-26H1'][0] - 0.0817) < 0.002 and abs(rep['外 2021-26H1'][0] - 0.0380) < 0.002, 'c29b 再現失敗'
assert abs(rep['近年 2024-26H1'][1] / 2 - 2.09) < 0.05, 't_c29 再現失敗'
P('- 再現 OK（Δμ ±0.002・t_c29 ±0.05）')

# ------------------------------------------------------------------ R1 t の定義と family-wise
P('\n## R1 (T1) Δμ(top−all) の正しい se と 13 特徴量 family-wise（循環シフト 1000 回）')
NPERM = 1000
fw = {}
for wn, m in win.items():
    n_w = int(m.sum()); obs = {nm: cell(known[nm], Rs, m) for nm in FEATS}
    perm_d = {nm: [] for nm in FEATS}; perm_maxt = []
    for _ in range(NPERM):
        k = int(rng.integers(200, n_w - 200)); sf = shift_feats(m, k); mt = 0.0
        for nm in FEATS:
            d, t, _ = cell(sf[nm], Rs, m); perm_d[nm].append(d); mt = max(mt, abs(t))
        perm_maxt.append(mt)
    perm_maxt = np.array(perm_maxt)
    # iid シャッフル sd（cont_24h_XAU のみ）
    iid = []
    for _ in range(400):
        v = known['cont_24h_XAU'].copy(); idx = np.where(m)[0]; v[idx] = rng.permutation(known['cont_24h_XAU'][idx])
        iid.append(cell(v, Rs, m)[0])
    sd_iid = np.std(iid, ddof=1)
    d24, t24, n24 = obs['cont_24h_XAU']; sd_perm = np.std(perm_d['cont_24h_XAU'], ddof=1)
    se_an = Rs[m].std(ddof=1) / np.sqrt(n24)
    t_perm = d24 / sd_perm
    p_fw = float((perm_maxt >= abs(t24)).mean())
    p_fw_c29 = float((perm_maxt >= abs(t24) / 2).mean())
    fw[wn] = dict(d=d24, t=t24, t_perm=t_perm, sd_perm=sd_perm, sd_iid=sd_iid, se_an=se_an, p_fw=p_fw,
                  maxt_med=float(np.median(perm_maxt)), maxt95=float(np.quantile(perm_maxt, 0.95)))
    P(f'- {wn}: cont_24h_XAU Δμ {d24:+.4f}・se 解析 σ/√n {se_an:.4f}・sd_iid {sd_iid:.4f}・sd_循環 {sd_perm:.4f} → '
      f't_welch {t24:+.2f}・t_perm(循環) {t_perm:+.2f}・t_c29 {t24/2:+.2f}（比 t_perm/t_c29 {t_perm/(t24/2):.2f}）')
    P(f'  13 特徴量 max|t_welch| 帰無: 中央値 {np.median(perm_maxt):.2f}・95% 点 {np.quantile(perm_maxt,0.95):.2f}・99% 点 {np.quantile(perm_maxt,0.99):.2f} → '
      f'p_fw(|t| {abs(t24):.2f}) = {p_fw:.3f}；c29 の t 2.09 相当を帰無と比べた場合 p_fw = {p_fw_c29:.3f}')
    # 全 13 特徴量の観測 t（正しい定義）
    P('  観測 t_welch（正しい定義・|t|≥2 のみ）: ' + '、'.join(f'{nm} {obs[nm][1]:+.2f}（Δμ {obs[nm][0]:+.3f}）' for nm in FEATS if abs(obs[nm][1]) >= 2) )
# 39 セル同時（窓ごとに独立に k を引く＝保守的）
P('- 39 セル（13×3 窓）同時 family-wise: 窓別の max|t| 帰無を独立結合 → 近年 cont_24h_XAU の |t| が 39 セル帰無 max を超える確率を近似')
# 近似: P(max over 3 windows ≥ x) = 1 − Π P(max_w < x)
x = abs(fw['近年 2024-26H1']['t'])
# recompute per-window exceedance from stored quantiles is lossy; approximate with p_fw per window of x
# (we only stored p_fw at each window's own t; approximate using maxt_med/95 lognormal fit is overkill → use per-window p at x)
# re-derive quickly with a lighter 300-perm pass per window
pw = []
for wn, m in win.items():
    n_w = int(m.sum()); mts = []
    for _ in range(300):
        k = int(rng.integers(200, n_w - 200)); sf = shift_feats(m, k)
        mts.append(max(abs(cell(sf[nm], Rs, m)[1]) for nm in FEATS))
    pw.append(float((np.array(mts) >= x).mean()))
p39 = 1 - np.prod([1 - p for p in pw])
P(f'  窓別 P(max|t| ≥ {x:.2f}) = {pw} → 39 セル近似 p_fw39 ≈ {p39:.3f}')
# 2021-25（最新半年抜き）
m2125 = (yr >= 2021) & (yr <= 2025)
d, t, n = cell(known['cont_24h_XAU'], Rs, m2125)
P(f'- 2021-25（2026H1 抜き）cont_24h_XAU: Δμ {d:+.4f}R・t_welch {t:+.2f}・n {n}')
t2125 = t
r1_rec = fw['近年 2024-26H1']
ratio = r1_rec['t_perm'] / (r1_rec['t'] / 2)
r1_def_wrong = 1.6 <= ratio <= 2.4
if r1_rec['p_fw'] < 0.05 and t2125 >= 2: r1_verdict = 'broken'
elif r1_rec['p_fw'] >= 0.10: r1_verdict = 'survived'
else: r1_verdict = 'inconclusive'
P(f'- **R1 判定**: t 定義 {"2 倍過小（誤り）" if r1_def_wrong else "比が範囲外・要確認"}（比 {ratio:.2f}）／主張 (ii)「近年 t 2.09 は 39 セル帰無の範囲」= **{r1_verdict}**'
  f'（近年 p_fw13 {r1_rec["p_fw"]:.3f}・p_fw39≈{p39:.3f}・2021-25 t {t2125:+.2f}）')

# ------------------------------------------------------------------ R2 copula
P('\n## R2 (T2) 同じ Spearman ρ で依存構造を変える（f=0.5・200 回平均）')
def ranks01(x):
    r = pd.Series(x).rank(method='average').values; return (r - 0.5) / len(x)
def calib(g, r, rho_target, n):
    """s = a·g + ε の a を二分法で Spearman(s, r)=rho_target に合わせる（20 回平均）"""
    lo, hi = 0.0, 50.0
    for _ in range(30):
        a = (lo + hi) / 2; sp = []
        for _ in range(20):
            s = a * g + rng.standard_normal(n); sp.append(spearmanr(s, r)[0])
        if np.mean(sp) < rho_target: lo = a
        else: hi = a
    return (lo + hi) / 2
def evaluate(g, a, r, top, n, reps=200):
    dm = []; kt = []; sp = []
    for _ in range(reps):
        s = a * g + rng.standard_normal(n); kept = s >= np.quantile(s, 0.5)
        dm.append(r[kept].mean() - r.mean()); kt.append(top[kept].sum() / top.sum()); sp.append(spearmanr(s, r)[0])
    return np.mean(dm), np.mean(kt), np.mean(sp)
r2_break = False
for wn in ['外 2021-26H1', '在 2010-20']:
    m = win[wn]; r = Rs[m]; n = len(r); z = norm.ppf(ranks01(r)); top = r >= np.quantile(r, 0.9)
    ex = exitv[m]
    structs = {
        'Gaussian (c29)': z,
        '尾部狙い 1{R*≥q90}': top.astype(float),
        '勝ち側のみ max(z,0)': np.maximum(z, 0),
        '負け側のみ min(z,0)': np.minimum(z, 0),
        'SL 検知 −1{SL}': -(ex == 'SL').astype(float),
        'TP 検知 1{TP}': (ex == 'TP').astype(float),
    }
    for rho in [0.05, 0.10]:
        P(f'- {wn}・ρ={rho:.2f}:')
        base = None
        for nm, g in structs.items():
            if nm.startswith('Gaussian'):
                a = 2 * np.sin(np.pi * rho / 6); a = a / np.sqrt(1 - a**2)  # s = rg·z + sqrt(1−rg²)ε ∝ (rg/sqrt(1−rg²))·z + ε
            else:
                a = calib(g, r, rho, n)
            dm, kt, sp = evaluate(g, a, r, top, n)
            if base is None: base = dm
            ratio_g = dm / base if base else np.nan
            flag = ''
            if rho == 0.10 and not nm.startswith('Gaussian') and (ratio_g < 0.5 or ratio_g > 1.5 or kt >= 0.75):
                flag = ' ←範囲外'; r2_break = True
            P(f'    {nm:>22s}: Δμ(f=0.5) {dm:+.4f}R（Gaussian 比 {ratio_g:.2f}）・上位 10% 保持 {kt*100:.0f}%・実測 Spearman {sp:.3f}{flag}')
P(f'- **R2 判定**: 換算 ρ→Δμ（0.79〜0.90R/ρ・保持 57%）の普遍性 = **{"broken（係数は Gaussian copula 固有）" if r2_break else "survived"}**')

# ------------------------------------------------------------------ R3 power
P('\n## R3 (T3) n_req = 2(2σ/Δμ)² の検出力（実 R* 外からブートストラップ・Δμ=0.05 注入・2000 回）')
r_out = Rs[win['外 2021-26H1']]; sd_out = r_out.std(ddof=1)
nreq = int(round(2 * (2 * sd_out / 0.05) ** 2))
def power(n, dmu, reps=2000, thr=2.0):
    hits = 0
    for _ in range(reps):
        smp = rng.choice(r_out, size=n, replace=True); kept = np.zeros(n, bool); kept[: n // 2] = True
        smp = smp + np.where(kept, dmu, -dmu)
        if welch(smp[kept], smp[~kept]) >= thr: hits += 1
    return hits / reps
pw_full = power(nreq, 0.05); pw_half = power(nreq // 2, 0.05)
pw_4005 = power(4005, 0.05); pw_4005_082 = power(4005, 0.082)
# 実際の年間本数
yrs_full = {y: int((yr == y).sum()) for y in range(2021, 2026)}
per_week = np.mean(list(yrs_full.values())) / 52
P(f'- 外 σ {sd_out:.3f}・n_req(0.05R) {nreq}・c29 換算 {nreq/30/52:.1f} 年（週 30 本）；実測 2021-25 年間本数 {yrs_full} → 週 {per_week:.1f} 本 → {nreq/per_week/52:.1f} 年')
P(f'- 検出力 P(t≥2): n=n_req {pw_full:.3f}／n=n_req/2 {pw_half:.3f}／n=4005（近年窓） Δμ0.05 {pw_4005:.3f}・Δμ0.082 {pw_4005_082:.3f}')
P(f'- 解析: E[t] at n_req = Δμ√n/σ = {0.05*np.sqrt(nreq)/sd_out:.2f}（=√8）→ 80% 検出力の式。E[t]=2（50%）に要る n = (2σ/Δμ)² = {int((2*sd_out/0.05)**2)}（{(2*sd_out/0.05)**2/per_week/52:.1f} 年）')
if 0.70 <= pw_full <= 0.90 and 0.40 <= pw_half <= 0.60: r3 = 'survived（80% 検出力の式として）・表記「t≥2 に要る本数」は relabel'
elif pw_full < 0.60 or pw_full > 0.95: r3 = 'broken'
else: r3 = 'inconclusive'
P(f'- **R3 判定**: **{r3}**')

# ------------------------------------------------------------------ R4 grid
P('\n## R4 (T4) 外 2021-26H1・13 特徴量 × f{0.3,0.5,0.7} × 上/下 = 78 セル・循環シフト 500 回 family-wise')
m = win['外 2021-26H1']; n_w = int(m.sum())
grid = []
for nm in FEATS:
    for f in [0.3, 0.5, 0.7]:
        for side in ['top', 'bottom']:
            d, t, n = cell(known[nm], Rs, m, f, side); grid.append((nm, f, side, d, t, n))
maxt_null = []; maxd_null = []
for _ in range(500):
    k = int(rng.integers(200, n_w - 200)); sf = shift_feats(m, k); mt = 0.0; md = 0.0
    for nm in FEATS:
        for f in [0.3, 0.5, 0.7]:
            for side in ['top', 'bottom']:
                d, t, _ = cell(sf[nm], Rs, m, f, side)
                if np.isfinite(t): mt = max(mt, abs(t)); md = max(md, abs(d))
    maxt_null.append(mt); maxd_null.append(md)
maxt_null = np.array(maxt_null); maxd_null = np.array(maxd_null)
P(f'- 帰無 max|t| 中央値 {np.median(maxt_null):.2f}・95% 点 {np.quantile(maxt_null,0.95):.2f}；帰無 max|Δμ| 中央値 {np.median(maxd_null):.3f}R・95% 点 {np.quantile(maxd_null,0.95):.3f}R')
big = [g for g in grid if np.isfinite(g[3]) and abs(g[3]) >= 0.05]
P(f'- |Δμ| ≥0.05R のセル {len(big)} 個:')
r4_break = False
for nm, f, side, d, t, n in sorted(big, key=lambda g: -abs(g[4])):
    p = float((maxt_null >= abs(t)).mean()); pd_ = float((maxd_null >= abs(d)).mean())
    if p < 0.05: r4_break = True
    P(f'    {nm} f={f} {side}: Δμ {d:+.4f}R・t_welch {t:+.2f}・n {n}・p_fw(t) {p:.3f}・p_fw(Δμ) {pd_:.3f}')
topg = sorted([g for g in grid if np.isfinite(g[4])], key=lambda g: -abs(g[4]))[:5]
P('- |t| 上位 5 セル: ' + '；'.join(f'{nm} f={f} {side} Δμ {d:+.3f} t {t:+.2f} p_fw {float((maxt_null>=abs(t)).mean()):.3f}' for nm, f, side, d, t, n in topg))
P(f'- **R4 判定**: 「外 ≤0.038R（f=0.5）」の上界 = **{"broken（f を変えると 0.05R 超・family-wise 有意のセルあり）" if r4_break else "survived（0.05R 超で family-wise 有意なセル無し）"}**')
# 近年も記述
m_r = win['近年 2024-26H1']
gr = [(nm, f, side) + cell(known[nm], Rs, m_r, f, side) for nm in FEATS for f in [0.3, 0.5, 0.7] for side in ['top', 'bottom']]
gr = sorted([g for g in gr if np.isfinite(g[4])], key=lambda g: -abs(g[4]))[:5]
P('- （記述）近年 |t| 上位 5: ' + '；'.join(f'{nm} f={f} {side} Δμ {d:+.3f} t {t:+.2f}' for nm, f, side, d, t, n in gr))

# ------------------------------------------------------------------ R5 decomposition
P('\n## R5（記述）cont_24h_XAU の分解（Δμ(f=0.5)・t_welch 正しい定義）')
v = known['cont_24h_XAU']
subs = {'2021': yr == 2021, '2022': yr == 2022, '2023': yr == 2023, '2024': yr == 2024, '2025': yr == 2025, '2026H1': yr == 2026,
        '2021-25': m2125, '2022-26H1': yr >= 2022, '2019-23': (yr >= 2019) & (yr <= 2023), '2016-20': (yr >= 2016) & (yr <= 2020),
        '外 jh7-12': (yr >= 2021) & (jh >= 7) & (jh <= 12), '近年 jh7-12': (yr >= 2024) & (jh >= 7) & (jh <= 12),
        '外 jh 他': (yr >= 2021) & ~((jh >= 7) & (jh <= 12)),
        '外 outer': (yr >= 2021) & (wk == 'outer'), '外 mid': (yr >= 2021) & (wk != 'outer'),
        '近年 outer': (yr >= 2024) & (wk == 'outer'), '近年 mid': (yr >= 2024) & (wk != 'outer')}
for nm_s, ms in subs.items():
    d, t, n = cell(v, Rs, ms); P(f'- {nm_s}: Δμ {d:+.4f}R・t {t:+.2f}・n {n}')
for wn in ['外 2021-26H1', '近年 2024-26H1']:
    d1, t1, _ = cell(v, Rs, win[wn]); d2, t2, _ = cell(v, Rs_cost2, win[wn])
    P(f'- コスト倍（R*−ft）{wn}: Δμ {d1:+.4f} → {d2:+.4f}R・t {t1:+.2f} → {t2:+.2f}')
# ΣR の算術（c29 (3)）: f·(μ+Δμ) vs μ
for wn in ['外 2021-26H1', '近年 2024-26H1']:
    mu = Rs[win[wn]].mean(); d, _, _ = cell(v, Rs, win[wn])
    P(f'- ΣR 算術 {wn}: μ {mu:+.4f}・0.5(μ+Δμ) {0.5*(mu+d):+.4f}（scan の μ≈0 では本数半減でも ΣR は増える／台帳 μ 0.165 では Δμ>0.165 が要る）')

P(f'\n実行時間 {time.time()-t0:.1f} s')
(ROOT / 'data' / 'refute_c29_entrylaw.md').write_text('\n'.join(L), encoding='utf-8')
print('written', ROOT / 'data' / 'refute_c29_entrylaw.md')
