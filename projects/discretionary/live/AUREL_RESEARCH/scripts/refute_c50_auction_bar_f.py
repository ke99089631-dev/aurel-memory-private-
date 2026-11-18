# -*- coding: utf-8 -*-
"""[反証レーン c50 補足 f] 沈みの近年の拡大（2021-24 -0.66 → 2026H1 -3.95 bp → 口座 2026 秋 -2.61 bp）は
ボラの拡大で説明できるか。ボラ単位（当日 10-11 時の 5 分リターン sd）で年別に出す。事前固定: 判定なし・記述のみ。"""
import os, io, json, math, time
import numpy as np, pandas as pd
T0=time.time(); HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); LIVE=os.path.dirname(ROOT)
OUT=os.path.join(ROOT,"data","refute_c50_auction_bar_f.md"); L=[]
def say(s=""):
    print(s,flush=True); L.append(s)
def S(h,m): return h*12+m//5
def stat(x):
    x=np.asarray(x,float); x=x[np.isfinite(x)]; n=len(x)
    if n<3: return (np.nan,np.nan,n,np.nan)
    se=x.std(ddof=1)/math.sqrt(n); return (x.mean(), x.mean()/se if se>0 else np.nan, n, se)
BP=1e4
say(f"# [反証レーン c50 補足 f] 沈みの拡大はボラの拡大か（記述） — {time.strftime('%Y-%m-%d %H:%M')}")
z=np.load(os.path.join(ROOT,"data","macro","XAU_m5_ohlc.npz")); ts=z["ts"].astype(np.int64); cl=z["close"].astype(float)
tl=pd.to_datetime(ts,unit="s",utc=True).tz_convert("Europe/London")
wd=tl.weekday.to_numpy(); sl=tl.hour.to_numpy()*12+tl.minute.to_numpy()//5
day=pd.DatetimeIndex(tl.tz_localize(None)).normalize(); flat=(cl==np.roll(cl,1)); m=wd<=4
df=pd.DataFrame({"day":day[m],"slot":sl[m],"lc":np.log(cl[m]),"flat":flat[m].astype(int)})
C=df.pivot_table(index="day",columns="slot",values="lc",aggfunc="first").reindex(columns=range(288))
F=df.pivot_table(index="day",columns="slot",values="flat",aggfunc="first").reindex(columns=range(288))
d=pd.DatetimeIndex(C.index); Cv=C.to_numpy(); Fv=F.to_numpy()
ok=np.isfinite(Cv[:,list(range(S(9,50),S(16,45)))]).all(axis=1)&(np.nansum(1-Fv[:,S(14,30):S(15,30)],axis=1)>=8)
x25=(Cv[:,S(10,25)]-Cv[:,S(10,25)-1])*BP
sd=np.nanstd(np.diff(Cv[:,S(10,0):S(11,0)],axis=1)*BP,axis=1)
yr=np.asarray(d.year)
say(""); say("| 年 | n | 沈み bp | 当日 10-11 時 5 分 sd bp | **沈み / sd** | t(沈み/sd) |"); say("|---|---|---|---|---|---|")
for y in range(2010,2027):
    mk=ok&(yr==y)
    if mk.sum()<100: continue
    a=stat(x25[mk]); s=np.nanmean(sd[mk]); r=stat((x25/np.where(sd>0,sd,np.nan))[mk])
    say(f"| {y} | {a[2]} | {a[0]:+.2f} | {s:.2f} | **{r[0]:+.3f}** | {r[1]:+.2f} |")
for nm,mk in (("P1 2010-13",ok&(yr<=2013)),("P3 2015/03-20 - 20",ok&np.asarray((d>="2015-03-20")&(d<="2020-12-31"))),
              ("P4 2021-26H1",ok&np.asarray(d>="2021-01-01")),("in 2021-24",ok&np.asarray((d>="2021-01-01")&(d<="2024-12-31"))),
              ("out 2025-26H1",ok&np.asarray(d>="2025-01-01"))):
    a=stat(x25[mk]); s=np.nanmean(sd[mk]); r=stat((x25/np.where(sd>0,sd,np.nan))[mk])
    say(f"| **{nm}** | {a[2]} | {a[0]:+.2f} | {s:.2f} | **{r[0]:+.3f}** | {r[1]:+.2f} |")
# 口座ログ（2026 秋）
rec={}
for fn in ("spread_log.jsonl","spread_log_15m.jsonl"):
    p=os.path.join(LIVE,fn)
    if not os.path.exists(p): continue
    with io.open(p,"r",encoding="utf-8",errors="replace") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: o=json.loads(line)
            except Exception: continue
            if "ts" in o and "bid" in o: rec[int(o["ts"])]=float(o["bid"])
tsa=np.array(sorted(rec.keys()),dtype=np.int64); bid=np.array([rec[t] for t in tsa])
tla=pd.to_datetime(tsa,unit="s",utc=True).tz_convert("Europe/London")
days=sorted(set(pd.Timestamp(x) for x,w in zip(pd.DatetimeIndex(tla.tz_localize(None)).normalize(),tla.weekday.to_numpy()) if w<=4))
G=np.full((len(days),288),np.nan)
for i,dd in enumerate(days):
    gi=(pd.Timestamp(dd).tz_localize("Europe/London")+pd.to_timedelta(np.arange(288)*5,unit="m")).tz_convert("UTC").tz_localize(None)
    g=np.asarray(gi,dtype="datetime64[s]").astype(np.int64)
    idx=np.searchsorted(tsa,g,side="right")-1; good=idx>=0
    age=np.where(good,g-tsa[np.clip(idx,0,len(tsa)-1)],np.inf); take=good&(age<=120)
    G[i,take]=bid[np.clip(idx,0,len(tsa)-1)][take]
lg=np.log(G); xa=(lg[:,S(10,30)]-lg[:,S(10,25)])*BP
sda=np.nanstd(np.diff(lg[:,S(10,0):S(11,0)],axis=1)*BP,axis=1)
a=stat(xa); s=np.nanmean(sda); r=stat(xa/np.where(sda>0,sda,np.nan))
say(f"| **口座配信 2026-09/11（別ベンダー・OOS）** | {a[2]} | {a[0]:+.2f} | {s:.2f} | **{r[0]:+.3f}** | {r[1]:+.2f} |")
say(""); say("- 読み方: 「沈み / 当日 10-11 時 sd」が年を通じて一定なら拡大はボラの拡大。増えているなら構造が変わった（別の説明が必要）。")
say(f"- 実行 {time.time()-T0:.1f} s・読取りのみ・記述のみ（判定なし）。seed 20261118")
open(OUT,"w",encoding="utf-8").write("\n".join(L)+"\n")
print(f"\n[written] {OUT}")
