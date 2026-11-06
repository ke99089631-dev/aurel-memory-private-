# -*- coding: utf-8 -*-
"""c11b: 会長11-06「レンジは苦手・トレンドが得意なはず」を同じ4週で確認。読取のみ。
   効率比ER = |終点-始点| / 道のり(各足の|Δclose|の和)。1に近い=一方向(トレンド)・0に近い=往復(レンジ)。
   ブレイク足の直前 6h(72本) と 24h(288本) で計算し、三分位でRを比べる。"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE=os.path.dirname(os.path.abspath(__file__)); LIVE=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0, LIVE); import serve_chart as sc
bars=json.load(open(os.path.join(LIVE,"AUREL_RESEARCH","data","bars_m5_merged_1008_1105.json"),encoding="utf-8"))["bars"]
T=[b["time"] for b in bars]; C=[b["close"] for b in bars]; H=[b["high"] for b in bars]; L=[b["low"] for b in bars]
idx={t:i for i,t in enumerate(T)}
def er(i,n):
    path=sum(abs(C[k]-C[k-1]) for k in range(i-n+1,i)); return abs(C[i-1]-C[i-n])/path if path else 0
def rng_atr(i,n): # 24h箱の高さ / 平均5分足レンジ(ボラ正規化した箱の相対サイズ)
    atr=sum(H[k]-L[k] for k in range(i-288,i))/288; return (max(H[i-288:i])-min(L[i-288:i]))/atr
recs=sc._load_setups(); cm=sc._cost_model(); rows=[]
for r in recs:
    i=idx.get(r.get("break_time")); 
    if i is None or i<300: continue
    ra=r.get("reaccel") if isinstance(r.get("reaccel"),dict) else None
    if not ra or ra.get("status")!="closed" or ra.get("R") is None: continue
    fake={"R":ra["R"],"entry":ra.get("entry"),"sl":ra.get("sl"),"entry_time":ra.get("entry_time"),"jst_hour":r.get("jst_hour"),"exit_reason":ra.get("exit_reason")}
    rows.append({"R":sc._net_R(fake,cm)[0],"er6":er(i,72),"er24":er(i,288),"boxatr":rng_atr(i,288),"kind":r.get("wall_kind")})
def st(g):
    if not g: return "n=0"
    n=len(g); w=sum(1 for x in g if x["R"]>0); s=sum(x["R"] for x in g); return f"n={n:3d} 勝率{100*w/n:3.0f}% 合計{s:+6.2f}R 平均{s/n:+.3f}"
def ter(feat,label):
    v=sorted(x[feat] for x in rows); q1,q2=v[len(v)//3],v[2*len(v)//3]
    print(f"### {label}")
    for nm,sel in (("レンジ寄り(低)",lambda x:x[feat]<=q1),("中",lambda x:q1<x[feat]<=q2),("トレンド寄り(高)",lambda x:x[feat]>q2)):
        g=[x for x in rows if sel(x)]; print(f"  {nm} {min(x[feat] for x in g):.2f}〜{max(x[feat] for x in g):.2f}: {st(g)}")
print(f"# c11b 再加速レーン n={len(rows)} (10-09〜11-06)  全体 {st(rows)}")
ter("er6","直前6時間の一方向性(効率比)"); ter("er24","直前24時間の一方向性(効率比)"); ter("boxatr","24h箱の相対サイズ(箱/平均5分足レンジ)=大きい=動いた日")
