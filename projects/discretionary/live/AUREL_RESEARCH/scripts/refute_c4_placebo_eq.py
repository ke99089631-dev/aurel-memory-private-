# -*- coding: utf-8 -*-
"""診断3: 実データ・プラセボを「本ごとに等重み」で再計算（pooled の pT 重み付けバイアスを除く）。読取りのみ。"""
import os, sys, json, math, time, numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import refute_c4_scanpath as R
J=json.load(open(R.PATHS_JSON,encoding="utf-8")); df=pd.DataFrame(J["trades"]); df["ft"]=R.FEED_TOL/df.risk; df["atr"]=pd.to_numeric(df.atr,errors="coerce")
sub=df[(df.hold>=1)&((1-df.ft)>0.5)]; g=sub[(sub.R>0)&(sub.exit=="TP")&sub.atr.notna()].sample(800,random_state=5)
m5=R.load_all(); o=m5["open"].to_numpy(); h=m5["high"].to_numpy(); l=m5["low"].to_numpy(); c=m5["close"].to_numpy()
n=len(o); atr=pd.Series(h-l).rolling(14).mean().shift(1).to_numpy(); hours=m5.index.hour.to_numpy(); valid=np.arange(14,n-R.MAX_HOLD-2)
rng=np.random.default_rng(11); rates=[]; pooled_k=pooled_n=0; tp_rate=[]
for _,t in g.iterrows():
    hu=(t.jh-9)%24; cand=valid[hours[valid]==hu]; j=rng.choice(cand,size=80,replace=True)
    scale=atr[j]/t.atr; risk_s=t.risk*scale; entry=o[j]; idx=j[:,None]+np.arange(R.MAX_HOLD+1)[None,:]
    sgn=1.0 if t.side=="BUY" else -1.0
    A=sgn*(h[idx]-entry[:,None])/risk_s[:,None]; B=sgn*(l[idx]-entry[:,None])/risk_s[:,None]
    H=np.maximum(A,B); Lo=np.minimum(A,B); C=sgn*(c[idx]-entry[:,None])/risk_s[:,None]
    sl0=Lo[:,0]<=-(1-t.ft); tp0=H[:,0]>=(t.b+t.ft); alive=~(sl0|tp0)
    if alive.sum()<5: continue
    is_tp,mae=R.simulate_bars(H[alive,1:],Lo[alive,1:],C[alive,1:],t.b,t.ft)
    k=int((is_tp&(mae>=0.5)).sum()); m=int(is_tp.sum())
    if m>0: rates.append(k/m); pooled_k+=k; pooled_n+=m; tp_rate.append(m/alive.sum())
L=["# 診断3: 実データ・プラセボ 等重み版（勝ち本 %d 本 × 80 建玉・建玉足除外）"%len(rates),
   "- 本ごと等重み mean_i[dips_i/TPs_i] = %.1f%%"%(100*np.mean(rates)),
   "- pooled Σk/Σn (主スクリプトと同じ計算) = %.1f%%"%(100*pooled_k/pooled_n),
   "- プラセボの TP 率 平均 %.1f%%  (観測 hold≥1 勝率 47.1%%)"%(100*np.mean(tp_rate)),
   "- 観測 32.8% / 閉形式RW 31.9%"]
print("\n".join(L)); open(os.path.join(R.DATA,"refute_c4_placebo_eq.md"),"w",encoding="utf-8").write("\n".join(L)+"\n")
