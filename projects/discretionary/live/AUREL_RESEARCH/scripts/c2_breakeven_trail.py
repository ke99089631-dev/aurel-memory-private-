# -*- coding: utf-8 -*-
"""
AUREL cycle2 — 建値トレール（+Xで実力証明後にSLを建値へ）。読取りのみ・発注なし・書込は AUREL_RESEARCH 配下のみ。
会長2026-11-04「もったいない＝+0.5R後に戻される負け」の直感を検証。TPは不変・SL側だけ。

事前固定ルール:
  各トレードで含み益MFEが +X に一度でも到達したら、その後に終値Rが <=0 に戻ったら 0R（建値）で決済。
  +Xに届かない or 届いた後に建値へ戻らない → 原型(TP/SL/時間切れ)のまま。
  主判定 X=1.0R（0.75〜1.25の感度も）。在=2010-2020 / 外=2021-2026/07。評価=原型との対の差diff・t値(paired)・勝率・合計R・最大DD・上位10%(大当たり)残存率。
  昇格条件(候補): diff>0 が在・外とも有意 / 上位10%残存≥90% / DD悪化なし / 近年窓でも維持 / 前向き紙で同符号 / ネット(滑り)でも残る。
  ★今はグロス・全時間フラットscanの一次確認。残り検証=本番窓/前向き紙/滑りネット/レジーム交互作用/反証(RW・プラセボ・多重検定)。
使い方: python scripts\c2_breakeven_trail.py  （c1キャッシュ data/c1_reaccel_paths_2010_2026.json を読む・軽い）
"""
import os, sys, json, math
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); RES=os.path.dirname(HERE)
CACHE=os.path.join(RES,"data","c1_reaccel_paths_2010_2026.json")
OUT=os.path.join(RES,"data","c2_breakeven_trail_result.md")

def apply_be(tr,X):
    mfe=tr["mfe"]; cl=tr["cl"]; armed=None
    for k in range(len(mfe)):
        if mfe[k]>=X: armed=k; break
    if armed is None: return tr["R"]
    for k in range(armed+1,len(cl)):
        if cl[k]<=0.0: return 0.0
    return tr["R"]

def maxdd(r):
    cum=np.cumsum(r); peak=np.maximum.accumulate(np.concatenate([[0.0],cum]))[1:]
    return float((cum-peak).min()) if len(r) else 0.0

def block(trs,X):
    trs=sorted(trs,key=lambda x:x["entry_time"])
    R0=np.array([t["R"] for t in trs]); R1=np.array([apply_be(t,X) for t in trs])
    diff=R1-R0; se=diff.std(ddof=1)/math.sqrt(len(diff)) if len(diff)>1 else float('nan')
    top=np.argsort(R0)[-max(1,len(R0)//10):]
    return dict(n=len(trs),diff=diff.mean(),t=(diff.mean()/se if se and se>0 else 0.0),
                s0=R0.sum(),s1=R1.sum(),w0=100*(R0>0).mean(),w1=100*(R1>0).mean(),
                dd0=maxdd(R0),dd1=maxdd(R1),
                topret=100*(R1[top].sum()/R0[top].sum()) if R0[top].sum()!=0 else 100.0)

def main():
    trades=json.load(open(CACHE,encoding="utf-8"))["trades"]
    L=["# AUREL cycle2 建値トレール（+Xで建値へ・TP不変）  グロス/全時間scan 一次確認",""]
    IS=[t for t in trades if t["year"]<=2020]; OOS=[t for t in trades if t["year"]>2020]
    L.append("## 主判定 X=1.0R（在/外）")
    for lab,g in (("在2010-20",IS),("外2021-26",OOS)):
        s=block(g,1.0)
        L.append(f"  {lab}: n{s['n']} 差{s['diff']:+.3f} t{s['t']:+.1f} 合計{s['s0']:+.0f}→{s['s1']:+.0f} 勝率{s['w0']:.0f}→{s['w1']:.0f}% DD{s['dd0']:+.0f}→{s['dd1']:+.0f} 大当たり残存{s['topret']:.0f}%")
    L.append("\n## 時代別 X=1.0R（頑丈性）")
    for name,fn in (("2010-20",lambda y:y<=2020),("2021-23",lambda y:2021<=y<=2023),("2024-26",lambda y:y>=2024),("2025-26",lambda y:y>=2025)):
        g=[t for t in trades if fn(t["year"])]
        if not g: continue
        s=block(g,1.0); L.append(f"  {name}: n{s['n']} 差{s['diff']:+.3f} t{s['t']:+.1f} 大当たり残存{s['topret']:.0f}%")
    L.append("\n## 感度 X（全期間）")
    for X in (0.5,0.75,1.0,1.25,1.5):
        s=block(trades,X); L.append(f"  X={X}: 差{s['diff']:+.3f} t{s['t']:+.1f} 大当たり残存{s['topret']:.0f}%")
    txt="\n".join(L); print(txt); open(OUT,"w",encoding="utf-8").write(txt+"\n")

if __name__=="__main__":
    main()
