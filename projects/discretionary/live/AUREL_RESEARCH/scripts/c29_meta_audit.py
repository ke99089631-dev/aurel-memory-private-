# -*- coding: utf-8 -*-
"""
cycle29 [メタ] 研究体制の監査 — 2026-11-10 研究レーン
憲章 F.6（10 サイクルに 1 回のメタ問い）・DIRECTIVE 立ち上げタスク 4（過去の全実験の一覧化・
「入口工夫が負ける法則」の数値化・研究方法の盲点）。c19〜c28 の 10 サイクルでメタ無し → 本サイクル。

事前固定（数字を見る前に書く）
A. 研究ポートフォリオの監査（findings/*.md・backlog.md・DATA_MAP.md のテキスト・正規表現で集計）
   A1 研究レーンのサイクル数・反証エントリ数・ヘッドラインの判定語（null / PASS / inconclusive / FAIL）の件数。
   A2 R 単位で報告された MDE の分布（中央値・p25/p75）。予測 P3: 中央値 ≥ 0.05R（台帳 gross +0.165R の 30%）。
   A3 「needs data / 要取得」をデータ項目別に、言及エントリ数で順位付け。
      予測 P4: 「2026-07 以降の新データ（M5 延長）」待ちの前向きセルが ≥8 件で単独最大。
   A4 反証レーンが「最新半年（2026H1）が作る」と指摘した回数（c22/c25/c26/c28 で 4 回と自己申告・テキストで数える）。
B. 入口工夫が負ける法則（scan キャッシュ data/c8_crossasset_features.csv = refute_c4 19404 本 + 直前リターン特徴量）
   R* = R+ft（SL/TP）／R−ft（TIME）、ft = 0.1/risk（方法論 ①）。窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2）。
   B1 ρ-フィルタ曲線: Gaussian copula で R* と Spearman ρ の潜在シグナル s を作り、上位 f（0.5／0.7）を残す。
      Δμ(ρ,f) = mean(R*|kept) − mean(R*|all)、上位 10% 本の保持率、200 回平均。ρ ∈ {0.02,0.05,0.10,0.20,0.30,1.0(oracle)}。
      在で曲線を求め、外・近年で同じ ρ の Δμ が ±30% 以内に再現するか（法則の在外再現）。
      予測 P2: f=0.5 で +0.05R を得るのに必要な ρ ≥ 0.08。
   B2 実現 ρ: 建玉時に既知の特徴量（side 符号つき ret4h/ret24h × {XAU,US500,US100}・b・risk・jh・open_gap・atr・x0・
      mae_bar0・mfe_bar0）と R* の Spearman |ρ|（窓別・se=1/√n）。予測 P1: 全特徴量で |ρ| ≤ 0.05（全窓）。
   B3 検出限界: 2 群（f=0.5）Welch で Δμ を t≥2 で見るのに要る本数 n_req = 2·(2σ/Δμ)²（σ = sd(R*) 窓別）、
      週 30 本換算の年数。Δμ ∈ {0.03,0.05,0.10,0.165}。研究レーンの主セル MDE（A2 中央値）が
      「レジームの長さ（c25: 幾何は 2〜3 年で動く）内で確認できる効果」か。
C. 4 つのメタ問い（盲点／未使用手法／方法が原因か／少ない実験で誤仮説を捨てる方法）への回答は結果 md に数字つきで。
判定: P1〜P4 の成否を個別に記す（メタなので PROMOTED・入口/出口の提案ではない）。seed 20261110。
事前の最重大反証: (i) Gaussian copula の単調フィルタは 1 族にすぎず、分布全体を切り替える「レジーム型」条件づけは
ρ では測れない（ただし c5/c8/c9/c10/c15/c16 の条件づけセルは全部 2 群差 = 同じ検出問題に帰着）。
(ii) 実現 ρ は同データで推定（雑音込み・上方に偏る）→ 上界として読む。(iii) テキスト集計は書式依存で欠落あり。
"""
import re, glob, json, time, sys
import numpy as np, pandas as pd
from pathlib import Path

t0 = time.time()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'c29_meta_audit_result.md'
rng = np.random.default_rng(20261110)
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)

P('# cycle29 [メタ] 研究体制の監査 — 2026-11-10 (scripts/c29_meta_audit.py)')
# ------------------------------------------------------------------ A. テキスト監査
files = sorted(glob.glob(str(ROOT / 'findings' / '*.md')))
txt_all = ''
entries = []  # (kind, cycle, headline, body)
for f in files:
    t = Path(f).read_text(encoding='utf-8'); txt_all += t
    parts = re.split(r'\n(?=## \[)', t)
    for p in parts:
        m = re.match(r'## \[(cycle(\d+) 研究レーン|REFUTE)\]', p)
        if not m: continue
        kind = 'R' if m.group(1).startswith('cycle') else 'F'
        cyc = int(m.group(2)) if kind == 'R' else None
        head = p.split('\n', 1)[0]
        entries.append((kind, cyc, head, p))
res = [e for e in entries if e[0] == 'R']; ref = [e for e in entries if e[0] == 'F']
P(f'\n## A1 エントリ数: 研究レーン {len(res)} サイクル（番号 {sorted(set(e[1] for e in res))}）／反証 {len(ref)} エントリ／findings 計 {sum(len(Path(f).read_text(encoding="utf-8")) for f in files)} 文字')
def cls(head):
    h = head
    tags = []
    if re.search(r'null', h): tags.append('null')
    if re.search(r'PASS', h): tags.append('PASS')
    if re.search(r'inconclusive', h): tags.append('inconclusive')
    if re.search(r'FAIL', h): tags.append('FAIL')
    return tags or ['other']
cnt = {}
for e in res:
    for tg in cls(e[2]): cnt[tg] = cnt.get(tg, 0) + 1
P('- ヘッドラインの判定語（重複あり）:', cnt)
only_null = sum(1 for e in res if cls(e[2]) == ['null'])
any_pass = sum(1 for e in res if 'PASS' in cls(e[2]))
P(f'- null のみ {only_null}／PASS を含む {any_pass}（PASS は幾何・衛生・構造の確認で edge の PASS は 0 と自己申告）')
# A2 MDE in R units
mde_R = []
for e in res:
    for m in re.finditer(r'MDE[^\n]{0,30}?(\d+\.\d+)(?:\s*[〜~/／]\s*(\d+\.\d+))?\s*R', e[3]):
        mde_R.append(float(m.group(1)))
        if m.group(2): mde_R.append(float(m.group(2)))
mde_R = np.array(mde_R)
P(f'\n## A2 R 単位の MDE（研究レーン本文・{len(mde_R)} 件）: 中央値 {np.median(mde_R):.3f}R・p25 {np.percentile(mde_R,25):.3f}・p75 {np.percentile(mde_R,75):.3f}・min {mde_R.min():.3f}・max {mde_R.max():.3f}')
P(f'- 台帳 gross +0.165R（c25）に対する比: 中央値 {np.median(mde_R)/0.165*100:.0f}%・p25 {np.percentile(mde_R,25)/0.165*100:.0f}%；'
  f'MDE ≤0.03R（コスト 0.031R 級）の件数 {int((mde_R<=0.03).sum())}／≤0.05R {int((mde_R<=0.05).sum())}')
P(f'- 予測 P3（中央値 ≥0.05R）: {"成立" if np.median(mde_R)>=0.05 else "不成立"}')
# A3 needs data ranking
backlog = (ROOT / 'backlog.md').read_text(encoding='utf-8'); dmap = (ROOT / 'DATA_MAP.md').read_text(encoding='utf-8')
items = {
 '金 M5 延長 2026-07〜（前向きセルの新データ）': r'2026-07 以降|2026-07〜|M5 延長|M5 の延長|延長待ち|延長を AUREL',
 'XAU ask M1（mid・bid 人工物の除去）': r'ask M1|XAU ask|ask（mid）|ask での再現|ask\s*M1',
 'MT5 probe（symbol_info spread/swap/銘柄）': r'MT5 probe|symbol_info|swap_long|スワップ|swap 未記録',
 'EURUSD M1（ドルのイントラデイ）': r'EURUSD',
 '発表カレンダー CPI/FOMC/PCE': r'CPI|FOMC|PCE',
 'XAU/US100 M1 close npz（分尺度）': r'M1 close npz|M1 npz',
 'US100/US500 の壁→壁 scan キャッシュ': r'US100 の壁→壁|US500/US100 で|US100 scan|scan キャッシュを US|refute_c4 相当',
 '口座 commission／デモ spread': r'commission|手数料|デモ執行口座の spread|デモ 0\.42',
}
P('\n## A3 needs data の順位（言及エントリ数: 研究レーン／反証／backlog 行）')
rows = []
bl_lines = [l for l in backlog.split('\n') if l.strip().startswith('-')]
for k, pat in items.items():
    nr = sum(1 for e in res if re.search(pat, e[3])); nf = sum(1 for e in ref if re.search(pat, e[3]))
    nb = sum(1 for l in bl_lines if re.search(pat, l))
    rows.append((k, nr, nf, nb, nr + nf + nb))
rows.sort(key=lambda r: -r[4])
for r in rows: P(f'- {r[0]}: 研究 {r[1]}／反証 {r[2]}／backlog {r[3]} → 計 {r[4]}')
fwd = [e for e in res if re.search(r'前向き', e[3]) and re.search(r'2026-07 以降|新データ', e[3])]
fwd_bl = sum(1 for l in bl_lines if re.search(r'前向き', l) and re.search(r'2026-07 以降|新データ', l))
P(f'- 「前向き（新データ 2026-07 以降）」を含む研究エントリ {len(fwd)} 件（cycle {[e[1] for e in fwd]}）・backlog 行 {fwd_bl}')
P(f'- 予測 P4（M5 延長待ちが ≥8 件で単独最大）: {"成立" if (rows[0][0].startswith("金 M5") and len(fwd)>=8) else "不成立"}（1 位 = {rows[0][0]}）')
# A4 latest-window disease
pat_lw = r'最新半年|最新窓の選択|2026H1 が作|2026H1 だけ|2026H1 依存|最新窓'
n_lw_ref = sum(1 for e in ref if re.search(pat_lw, e[3])); n_lw_res = sum(1 for e in res if re.search(pat_lw, e[3]))
P(f'\n## A4 「最新半年（2026H1）が作る」型の指摘: 反証エントリ {n_lw_ref} 件／研究エントリ {n_lw_res} 件（反証の自己申告は 4 回）')
# 教訓の数
n_meth = len(set(re.findall(r'方法論 ([①-㉚]+|[0-9]{1,2}|㉑|㉒|㉓|㉔|㉕|㉖|㉗|㉘|㉙)', backlog)))
P(f'- backlog に登録された方法論番号の種類 {n_meth}')

# ------------------------------------------------------------------ B. 入口工夫が負ける法則
df = pd.read_csv(ROOT / 'data' / 'c8_crossasset_features.csv')
P(f'\n## B データ: c8_crossasset_features.csv {len(df)} 本・entry_time {pd.to_datetime(df.entry_time.min(),unit="s")}〜{pd.to_datetime(df.entry_time.max(),unit="s")}')
ft = 0.1 / df.risk.values
Rs = df.R.values + np.where(df.exit.values == 'TIME', -ft, ft)
df['Rs'] = Rs
yr = df.year.values
win = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}
sgn = np.where(df.side.values == 'BUY', 1.0, -1.0)
feats = {}
for a in ['XAU', 'US500', 'US100']:
    for h in ['4h', '24h']:
        feats[f'cont_{h}_{a}'] = sgn * df[f'ret{h}_{a}'].values
for c in ['b', 'risk', 'jh', 'open_gap', 'atr', 'x0', 'mae_bar0', 'mfe_bar0']:
    feats[c] = df[c].values.astype(float)

from scipy.stats import spearmanr, norm
def ranks01(x):
    r = pd.Series(x).rank(method='average').values
    return (r - 0.5) / len(x)

P('\n## B1 ρ-フィルタ曲線（Gaussian copula・200 回平均・Δμ = mean(R*|kept)−mean(R*|all)・top10 保持率 = 上位 10% 本のうち kept の割合）')
rhos = [0.02, 0.05, 0.10, 0.20, 0.30, 1.0]
curve = {}
for wn, mk in win.items():
    r = Rs[mk]; n = len(r); mu = r.mean(); sd = r.std(ddof=1)
    z_r = norm.ppf(ranks01(r))
    top = r >= np.quantile(r, 0.9)
    P(f'- {wn}: n {n}・mean R* {mu:+.4f}・sd {sd:.3f}・TP 率 {(df.exit.values[mk]=="TP").mean()*100:.1f}%・上位 10% の正 R* 合計 share {r[top].sum()/r[r>0].sum()*100:.1f}%')
    for f in [0.5, 0.7]:
        line = []
        for rho in rhos:
            dm = []; keep_top = []
            for _ in range(200 if rho < 1 else 1):
                if rho >= 1: s = z_r
                else:
                    # Gaussian copula: latent corr r_g s.t. Spearman = rho (r_g = 2 sin(pi rho/6))
                    rg = 2 * np.sin(np.pi * rho / 6)
                    s = rg * z_r + np.sqrt(1 - rg**2) * rng.standard_normal(n)
                kept = s >= np.quantile(s, 1 - f)
                dm.append(r[kept].mean() - mu); keep_top.append(top[kept].sum() / top.sum())
            curve[(wn, f, rho)] = (np.mean(dm), np.mean(keep_top))
            line.append(f'ρ{rho:.2f}: Δμ {np.mean(dm):+.3f}R top10 保持 {np.mean(keep_top)*100:.0f}%')
        P(f'  f={f}: ' + ' | '.join(line))
# ρ needed for +0.05R at f=0.5 (interpolate in 在)
def rho_needed(wn, f, target):
    xs = [rho for rho in rhos if rho < 1]; ys = [curve[(wn, f, rho)][0] for rho in xs]
    return float(np.interp(target, ys, xs)) if target <= max(ys) else float('nan')
for wn in win:
    P(f'- {wn}: f=0.5 で +0.03R に要る ρ {rho_needed(wn,0.5,0.03):.3f}／+0.05R {rho_needed(wn,0.5,0.05):.3f}／+0.10R {rho_needed(wn,0.5,0.10):.3f}；f=0.7 で +0.05R {rho_needed(wn,0.7,0.05):.3f}')
rn_in = rho_needed('在 2010-20', 0.5, 0.05)
P(f'- 予測 P2（f=0.5・+0.05R に ρ ≥0.08）: {"成立" if rn_in>=0.08 else "不成立"}（在 {rn_in:.3f}）')
# in/out reproduction of the law: Δμ per unit ρ (slope) at rho=0.10
for f in [0.5, 0.7]:
    sl = {wn: curve[(wn, f, 0.10)][0] for wn in win}
    base = sl['在 2010-20']
    P(f'- 法則の在外再現 f={f}・ρ=0.10 の Δμ: ' + '／'.join(f'{wn} {v:+.3f}R ({(v/base-1)*100:+.0f}%)' for wn, v in sl.items()))

P('\n## B2 実現 ρ（建玉時既知の特徴量 × R*・Spearman・窓別・se ≈ 1/√n）')
hdr = '| 特徴量 | ' + ' | '.join(win) + ' |'
P(hdr); P('|---|' + '---|' * len(win))
maxabs = {wn: 0.0 for wn in win}; maxname = {wn: '' for wn in win}
for name, x in feats.items():
    cells = []
    for wn, mk in win.items():
        ok = mk & np.isfinite(x)
        rho, _ = spearmanr(x[ok], Rs[ok]); se = 1 / np.sqrt(ok.sum())
        cells.append(f'{rho:+.3f} (t {rho/se:+.1f}, n {ok.sum()})')
        if abs(rho) > maxabs[wn]: maxabs[wn] = abs(rho); maxname[wn] = name
    P(f'| {name} | ' + ' | '.join(cells) + ' |')
for wn in win: P(f'- {wn}: 最大 |ρ| = {maxabs[wn]:.3f}（{maxname[wn]}）→ f=0.5 の Δμ 換算 ≈ {np.interp(maxabs[wn], [r for r in rhos if r<1], [curve[(wn,0.5,r)][0] for r in rhos if r<1]):+.3f}R')
P(f'- 予測 P1（全特徴量 |ρ| ≤0.05・全窓）: {"成立" if max(maxabs.values())<=0.05 else "不成立"}（最大 {max(maxabs.values()):.3f}）')
# 事後: 既知の最強セル DGS10 Δ80 外 β +0.134 (2 群差) → 等価 ρ
P('- 参考（事後）: 反証 11:30 の最強セル DGS10 Δ80×side 外 β +0.134R（2 群差）= Δμ 換算 +0.067R（群 = 半分）→ 在の曲線で ρ ≈ '
  f'{rho_needed("在 2010-20",0.5,0.067):.3f} 相当・外 ≈ {rho_needed("外 2021-26H1",0.5,0.067):.3f}')

P('\n## B3 検出限界（2 群 f=0.5 Welch t≥2 に要る総本数 n_req = 2·(2σ/Δμ)²・週 30 本換算）')
for wn, mk in win.items():
    sd = Rs[mk].std(ddof=1); line = []
    for dmu in [0.03, 0.05, 0.10, 0.165]:
        nreq = 2 * (2 * sd / dmu) ** 2
        line.append(f'Δμ {dmu:.3f}R: n {nreq:,.0f}（{nreq/30/52:.1f} 年）')
    P(f'- {wn}（σ {sd:.3f}）: ' + ' | '.join(line))
P(f'- 研究レーンの MDE 中央値 {np.median(mde_R):.3f}R を 2 群で確認するのに要る本数（外 σ）: {2*(2*Rs[win["外 2021-26H1"]].std(ddof=1)/np.median(mde_R))**2:,.0f} 本 = {2*(2*Rs[win["外 2021-26H1"]].std(ddof=1)/np.median(mde_R))**2/30/52:.1f} 年 vs レジームの長さ 2〜3 年（c25）')
# Sign-stability n* reference (ledger gross +0.165 with sd 1.4): n* 300 (c25). For a conditioning of +0.05R on top: n ~ 2(2*1.4/0.05)^2
P(f'- 台帳の gross edge 自体（+0.165R・σ 1.4）の符号確認 n*(95%) 300（c25）に対し、その 30%（+0.05R）の条件づけ差は n {2*(2*1.4/0.05)**2:,.0f}（{2*(2*1.4/0.05)**2/45/52:.1f} 年・台帳 45 本/週）')
P(f'\n実行時間 {time.time()-t0:.1f} s')
OUT.write_text('\n'.join(L), encoding='utf-8')
print('written', OUT)
