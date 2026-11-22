# -*- coding: utf-8 -*-
"""
[cycle59b 研究レーン 2026-11-23] c59 §5 の事後観測（SL 決着後の先着 F = P(+0.5R 先着) − P(−0.5R 先着) が 3 窓とも正・z 2.9〜3.7）に対する
最重大反証「決着足 close のアンカー条件づけ（SL 足は安値寄りで閉じる → 小さな戻しが先着を偏らせる）」を 1 回だけ検査する（事後・記述・判定に使わない）。
  (1) アンカーを 1 本ずらした F'（close[ix+1] 起点・窓 48 本）。人工物なら F' は 0 へ。
  (2) バリア幅 0.25R／0.5R／1.0R の F'（短距離だけなら微細構造・幅に鈍感なら分布の形）。
  (3) 符号率 P(C'_12 > 0) 事象 − 双子（中央値 正・平均 ≈0 = 「典型は戻る・裾は逆行継続」の確認）。
  (4) 条件づけの別路: 決着足の“行き過ぎ” s·(close_x − SL 水準)/risk は不明（entry 価格なし）→ 代理として決着足 |Δcl| の大きさで 2 分割し F' を印字。
入力は c59 と同じ（既存キャッシュのみ）。seed 不要（決定論）。
"""
import os, json, math, time, datetime as dt
import numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'c59b_first_passage_anchor_check.md')
L = []
def P(s=''): print(s); L.append(s)
j = json.load(open(os.path.join(DATA, 'refute_c4_scan_paths_2010_2026.json'), encoding='utf-8'))['trades']
et = np.array([t['entry_time'] for t in j], np.int64); hold = np.array([t['hold'] for t in j], np.int64)
side = np.array([1 if t['side']=='BUY' else -1 for t in j]); risk = np.array([t['risk'] for t in j], float)
exitk = np.array([t['exit'] for t in j]); year = np.array([t['year'] for t in j])
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_ohlc.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); hi = z['high'].astype(float); lo = z['low'].astype(float)
N = len(ts); flat = np.zeros(N, bool); flat[1:] = (cl[1:]==cl[:-1]) & (hi[1:]==lo[1:]); cf = np.concatenate([[0], np.cumsum(flat)])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i]==t, i, -1)
ix = gidx(et + 300*hold); twp = gidx(ts[np.clip(ix,0,N-1)] + 7*86400)
def fwd_ok(i0, K, sh):
    iend = i0+sh+K; okr = (i0>=0) & (iend < N); a = np.clip(i0+sh,0,N); b = np.clip(iend+1,0,N)
    return okr & ((cf[b]-cf[a])==0)
def fp(i0, s, rk, K, lev, sh):
    base = cl[np.clip(i0+sh,0,N-1)]; idx = np.clip(i0[:,None]+sh+np.arange(1,K+1)[None,:],0,N-1)
    path = s[:,None]*(cl[idx]-base[:,None])/rk[:,None]; up = path>=lev; dn = path<=-lev
    fu = np.where(up.any(1), up.argmax(1), K+5); fd = np.where(dn.any(1), dn.argmax(1), K+5)
    r = np.zeros(len(i0), int); r[fu<fd]=1; r[fd<fu]=-1; return r
def win(w):
    return {'在 2010-20': (year>=2010)&(year<=2020), '外 2021-26H1': year>=2021, '近年 2024-26H1': year>=2024}[w]
WINS = ['在 2010-20','外 2021-26H1','近年 2024-26H1']
base = (ix>=0) & np.isin(exitk, ['TP','SL'])
P(f'# AUREL [cycle59b] 先着 F のアンカー／バリア幅 検査（事後・記述）  {dt.datetime.now():%Y-%m-%d %H:%M}')
P('\n## (1)(2) F(事象) − F(双子 D+7)・窓 48 本・アンカー shift 0（c59 §5 再現）と shift 1・バリア 0.25／0.5／1.0R')
for arm in ['TP','SL']:
    for w in WINS:
        row = []
        for sh in [0,1]:
            for lev in [0.25,0.5,1.0]:
                m = base & (exitk==arm) & win(w) & fwd_ok(ix,48,sh) & (~flat[np.clip(ix,0,N-1)])
                mt = m & (twp>=0) & fwd_ok(twp,48,sh)
                fE = fp(ix[m], side[m], risk[m], 48, lev, sh); fT = fp(twp[mt], side[mt], risk[mt], 48, lev, sh)
                FE, FT = fE.mean(), fT.mean(); se = math.sqrt(fE.var()/len(fE) + fT.var()/max(len(fT),1)); d = FE-FT
                row.append(f'sh{sh} a{lev}: {d:+.3f} (z {d/se:+.1f})')
        P(f'  - {arm} {w}: ' + ' | '.join(row))
P('\n## (3) 符号率 P(C\'_12 > 0)（アンカー shift 1・12 本）事象 − 双子（pp）と 平均/中央値')
for arm in ['TP','SL']:
    for w in WINS:
        m = base & (exitk==arm) & win(w) & fwd_ok(ix,12,1) & (~flat[np.clip(ix,0,N-1)]); mt = m & (twp>=0) & fwd_ok(twp,12,1)
        cE = side[m]*(cl[np.clip(ix[m]+13,0,N-1)]-cl[np.clip(ix[m]+1,0,N-1)])/risk[m]
        cT = side[mt]*(cl[np.clip(twp[mt]+13,0,N-1)]-cl[np.clip(twp[mt]+1,0,N-1)])/risk[mt]
        pE, pT = np.mean(cE>0), np.mean(cT>0); se = math.sqrt(pE*(1-pE)/len(cE)+pT*(1-pT)/len(cT))
        P(f'  - {arm} {w}: P>0 事象 {pE*100:.1f}% 双子 {pT*100:.1f}% 差 {(pE-pT)*100:+.1f} pp (z {(pE-pT)/se:+.1f})  平均 事象 {cE.mean():+.4f} 双子 {cT.mean():+.4f}  中央値 事象 {np.median(cE):+.4f} 双子 {np.median(cT):+.4f}  下 5% 事象 {np.quantile(cE,0.05):+.3f} 双子 {np.quantile(cT,0.05):+.3f}  上 5% {np.quantile(cE,0.95):+.3f}／{np.quantile(cT,0.95):+.3f}')
P('\n## (4) 決着足の大きさ |Δcl_x|/risk で 2 分割（中央値）・SL 腕・F\'(sh1, a0.5)')
for w in WINS:
    m = base & (exitk=='SL') & win(w) & fwd_ok(ix,48,1) & (~flat[np.clip(ix,0,N-1)]) & (ix>=1)
    dx = np.abs(cl[ix[m]]-cl[ix[m]-1])/risk[m]; med = np.median(dx)
    out = []
    for nm, mm in [('小', dx<med), ('大', dx>=med)]:
        sub = np.where(m)[0][mm]
        fE = fp(ix[sub], side[sub], risk[sub], 48, 0.5, 1); FE = fE.mean(); se = math.sqrt(fE.var()/len(fE))
        out.append(f'{nm}（|Δcl_x| {"<" if nm=="小" else "≥"} {med:.2f}R）F\' {FE:+.3f} (z vs 0 {FE/se:+.1f}, n {len(fE)})')
    P(f'  - {w}: ' + ' | '.join(out))
P(f'\n実行 {time.time()-T0:.1f}s')
open(OUT,'w',encoding='utf-8').write('\n'.join(L)); print('written', OUT)
