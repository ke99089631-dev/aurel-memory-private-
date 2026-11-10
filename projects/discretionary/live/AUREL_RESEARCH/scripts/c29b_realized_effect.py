# -*- coding: utf-8 -*-
"""
cycle29 補足 b — 実現効果の正しい物差し（B2 の自己訂正・事後と明記）
c29 本体 B2 の Spearman ρ(特徴量, R*) は幾何（b・risk・ft）経由の順位構造を拾う（TP 率が幾何で動いても平均 R は動かない:
refute_c4_meter の atr/risk 四分位 勝率 53→41% vs 平均R −0.055〜−0.024）。研究レーンが実際に検定してきたのは 2 群の平均差なので、
ここでは (1) Δμ(f=0.5) = mean(R*|特徴量 > 窓中央値) − mean(R*|全体)（符号つき・Welch t）、(2) 幾何を差し引いた超過到達率
x = 1{TP} − q（q=(1−ft)/(1+b)・決着本のみ・cycle27 の道具）との Spearman と Δx(f=0.5) を、建玉時既知の特徴量について窓別に出す。
x0／mfe_bar0／mae_bar0 は建玉足（path index 0）の量で建玉時に未知 → 「look-ahead 対照」として別群で印字（Δμ が大きいのは機械的）。
ρ 換算: 在の ρ-曲線（f=0.5）の傾き 0.79R/ρ で |Δμ| → ρ_eq。
"""
import time, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import spearmanr, ttest_ind
t0 = time.time(); ROOT = Path(__file__).resolve().parents[1]; L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
df = pd.read_csv(ROOT / 'data' / 'c8_crossasset_features.csv')
ft = 0.1 / df.risk.values
Rs = df.R.values + np.where(df.exit.values == 'TIME', -ft, ft)
dec = df.exit.values != 'TIME'
q = (1 - ft) / (1 + df.b.values); x = np.where(df.exit.values == 'TP', 1.0, 0.0) - q
yr = df.year.values
win = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}
sgn = np.where(df.side.values == 'BUY', 1.0, -1.0)
known = {}
for a in ['XAU', 'US500', 'US100']:
    for h in ['4h', '24h']: known[f'cont_{h}_{a}'] = sgn * df[f'ret{h}_{a}'].values
for c in ['b', 'risk', 'jh', 'open_gap', 'atr']: known[c] = df[c].values.astype(float)
known['atr/risk'] = df.atr.values / df.risk.values
ctrl = {c: df[c].values.astype(float) for c in ['x0', 'mfe_bar0', 'mae_bar0']}
SLOPE = 0.79
P('# cycle29 補足 b — 実現効果（Δμ(f=0.5)・Spearman(特徴量, x)・Δx）(scripts/c29b_realized_effect.py)')
P(f'n {len(df)}・決着本 {dec.sum()}・q 中央値 {np.median(q):.3f}・x 平均 {x[dec].mean()*100:+.2f} pp')
def table(feats, title):
    P(f'\n## {title}')
    P('| 特徴量 | 窓 | n | Δμ(f=0.5) R | Welch t | ρ_eq | ρ(feat,x) | t | Δx(f=0.5) pp |'); P('|---|---|---|---|---|---|---|---|---|')
    mx = {}
    for name, v in feats.items():
        for wn, mk in win.items():
            ok = mk & np.isfinite(v); med = np.median(v[ok]); hi = ok & (v > med); lo = ok & (v <= med)
            dmu = Rs[hi].mean() - Rs[ok].mean(); t = ttest_ind(Rs[hi], Rs[lo], equal_var=False).statistic / 2  # /2: top − all = (top − bottom)/2
            okd = ok & dec; rho, _ = spearmanr(v[okd], x[okd]); tr = rho * np.sqrt(okd.sum())
            dx = (x[hi & dec].mean() - x[okd].mean()) * 100
            P(f'| {name} | {wn} | {ok.sum()} | {dmu:+.4f} | {t:+.2f} | {abs(dmu)/SLOPE:.3f} | {rho:+.3f} | {tr:+.1f} | {dx:+.2f} |')
            if abs(dmu) > mx.get(wn, (0.0, ''))[0]: mx[wn] = (abs(dmu), name)
    return mx
mx = table(known, 'B2b 建玉時既知の特徴量（研究レーンが検定してきた形 = 2 群差）')
for wn, (v, nm) in mx.items():
    P(f'- {wn}: 最大 |Δμ(f=0.5)| = {v:.4f}R（{nm}）→ ρ_eq {v/SLOPE:.3f}・台帳 gross +0.165R の {v/0.165*100:.0f}%')
table(ctrl, 'look-ahead 対照（建玉足 path index 0 の量・建玉時に未知・機械的に大きいはず）')
P(f'\n実行時間 {time.time()-t0:.1f} s')
(ROOT / 'data' / 'c29b_realized_effect.md').write_text('\n'.join(L), encoding='utf-8')
