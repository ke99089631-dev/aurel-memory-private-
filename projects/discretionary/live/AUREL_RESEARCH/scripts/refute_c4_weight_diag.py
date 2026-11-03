# -*- coding: utf-8 -*-
"""診断2: MC/プラセボの pooled 比率は各本を pT_i で重み付けする(小さい TP の本が過大)。観測の勝ち集合は各勝ち本を等重み。閉形式で両方を出して差を確認。"""
import os, json, math, numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__)); DATA=os.path.join(os.path.dirname(HERE),"data")
J=json.load(open(os.path.join(DATA,"refute_c4_scan_paths_2010_2026.json"),encoding="utf-8")); ft_abs=J["frozen"]["FEED_TOL"]
df=pd.DataFrame(J["trades"]); df["ft"]=ft_abs/df.risk; df["a"]=1-df.ft; df["u"]=df.b+df.ft
sub=df[(df.hold>=1)&(df.a>0.5)]; g=sub[(sub.R>0)&(sub.exit=="TP")]
def p_hit(x,a,u,th=0.0):
    if x<=-a: return 0.0
    if x>=u: return 1.0
    return (x+a)/(a+u)
def pd_tp(x0,a,u,d=0.5):
    pT=p_hit(x0,a,u); 
    if pT<=0: return float("nan"),0.0
    if x0<=-d: return 1.0,pT
    return (1-p_hit(x0,d,u))*p_hit(-d,a,u)/pT, pT
P=np.array([pd_tp(x,a,u) for x,a,u in zip(g.x0,g.a,g.u)]); ok=~np.isnan(P[:,0]); pdip=P[ok,0]; pT=P[ok,1]
L=["# 診断2: 重み付けの違い（θ=0・勝ち本 n=%d）"%ok.sum(),
   "- 等重み E[P(沈み|TP,i)] (観測勝ち集合に対する正しい期待) = %.1f%%"%(100*pdip.mean()),
   "- pT_i 重み Σ pT_i·P(沈み|TP,i)/Σ pT_i (MC/プラセボの pooled 比率が実際に計算している量) = %.1f%%"%(100*(pdip*pT).sum()/pT.sum()),
   "- 観測 = %.1f%%"%(100*(g.mae1>=0.5).mean()),
   "- u(TP距離) 四分位ごとの P(沈み|TP) 期待/観測:"]
q=pd.qcut(g.u[ok],4); 
for lab,m in zip(q.cat.categories,[q==c for c in q.cat.categories]):
    L.append("  u∈%s n=%d 期待 %.1f%% 観測 %.1f%%"%(lab,m.sum(),100*pdip[m.to_numpy()].mean(),100*(g.mae1[ok][m]>=0.5).mean()))
print("\n".join(L)); open(os.path.join(DATA,"refute_c4_weight_diag.md"),"w",encoding="utf-8").write("\n".join(L)+"\n")
