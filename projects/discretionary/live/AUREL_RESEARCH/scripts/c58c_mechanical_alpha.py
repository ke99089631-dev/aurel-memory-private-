# -*- coding: utf-8 -*-
"""
[cycle62 supp c58c] Mechanical component of the volatility-managed alpha under the null of CONSTANT drift mu with vol clustering.
vm = c*r/sig, r = mu + sig*eps  =>  E[vm] = c*mu*E[1/sig],  beta = cov(vm,r)/var(r) ~ c*E[sig]/E[sig^2]
=> alpha_null = c*mu*(E[1/sig] - E[sig]/E[sig^2])  >= 0 for mu>0 (Cauchy-Schwarz) : alpha has the SIGN OF THE DRIFT with no timing skill.
Checks: (1) alpha_null by formula per window; (2) circular-shift permutation null of alpha itself (not t): centre, sd, excess = alpha_obs - mean(alpha_perm);
(3) two-sided p of alpha around the null centre. Descriptive; does not change c58's pre-registered verdict (c58's perm p already uses this null).
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd
T0=time.time(); HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); DATA=os.path.join(ROOT,"data"); MAC=os.path.join(DATA,"macro")
OUT=os.path.join(DATA,"c58c_mechanical_alpha.md"); NY="America/New_York"; NFMIN=100; LB=21; NPERM=2000
rng=np.random.default_rng(20261123); L=[]
def say(s=""): print(s,flush=True); L.append(s)
say(f"# [cycle62 supp c58c] mechanical alpha under constant-drift null vs permutation centre -- {time.strftime('%Y-%m-%d %H:%M')} (scripts/c58c_mechanical_alpha.py)")
def daily_table(sym):
    z=np.load(os.path.join(MAC,f"{sym}_m5_close.npz")); ts=z["ts"].astype(np.int64); C=z["close"].astype(float)
    lc=np.log(C); r=np.zeros(len(C)); r[1:]=np.diff(lc); flat=r==0.0
    dt_ny=pd.to_datetime(ts,unit="s",utc=True).tz_convert(NY)
    sess=(dt_ny+pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]"); sord=sess.astype("int64")+dt.date(1970,1,1).toordinal()
    keep=~flat; df=pd.DataFrame({"o":sord[keep],"lc":lc[keep],"r2":r[keep]**2}); g=df.groupby("o",sort=True)
    D=pd.DataFrame({"lc_last":g["lc"].last(),"rv":g["r2"].sum(),"nf":g["r2"].size()})
    D["date"]=pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"]=D["date"].dt.weekday
    D=D[(D.wd<=4)&(D.nf>=NFMIN)].reset_index(); D["r"]=np.r_[np.nan,np.diff(D["lc_last"].to_numpy())]*1e4
    D["sig21"]=np.sqrt(D["rv"].rolling(LB).mean())*1e4; D["year"]=D["date"].dt.year; return D
def ols_alpha(vm,rr):
    Z=np.column_stack([np.ones(len(rr)),rr]); b=np.linalg.lstsq(Z,vm,rcond=None)[0]; return b[0],b[1]
for sym,wins in [("XAU",{"in 2010-20":(2010,2020),"out 2021-26H1":(2021,2026),"recent 2024-26H1":(2024,2026),"2025":(2025,2025),"2013":(2013,2013)}),
                 ("US500",{"in 2014-20":(2014,2020),"out 2021-26H1":(2021,2026)})]:
    D=daily_table(sym); sig=D["sig21"].to_numpy()[:-1]; r=D["r"].to_numpy()[1:]; yr=D["year"].to_numpy()[1:]
    say(f"\n## {sym}")
    for w,(y0,y1) in wins.items():
        m=(yr>=y0)&(yr<=y1)&np.isfinite(sig)&np.isfinite(r)&(sig>0); rr=r[m]; ss=sig[m]; n=len(rr)
        vm0=rr/ss; c=rr.std(ddof=1)/vm0.std(ddof=1); vm=vm0*c; a_obs,b_obs=ols_alpha(vm,rr)
        mu=rr.mean(); a_null=c*mu*(np.mean(1/ss)-np.mean(ss)/np.mean(ss**2))
        ap=np.empty(NPERM)
        for k in range(NPERM):
            off=int(rng.integers(30,n-30)); s2=np.roll(ss,off); v2=rr/s2; v2*=rr.std(ddof=1)/v2.std(ddof=1); ap[k]=ols_alpha(v2,rr)[0]
        ctr=ap.mean(); sd=ap.std(); exc=a_obs-ctr; p2=(np.abs(ap-ctr)>=abs(exc)).mean()
        say(f"- {w}: n {n}  mu {mu:+.2f} bp/d  c {c:.1f}  alpha_obs {a_obs:+.2f}  beta {b_obs:.3f} | alpha_null(formula) {a_null:+.2f} | perm centre {ctr:+.2f} (sd {sd:.2f}) -> excess {exc:+.2f} bp/d  z {exc/sd:+.2f}  p2 {p2:.3f} | mechanical share of alpha_obs {ctr/a_obs*100 if abs(a_obs)>1e-9 else float('nan'):.0f}%")
say(f"\n- time {time.time()-T0:.1f}s  seed 20261123  no network  no scan")
open(OUT,"w",encoding="utf-8").write("\n".join(L)+"\n"); print("WROTE",OUT)
