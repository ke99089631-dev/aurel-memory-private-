# -*- coding: utf-8 -*-
"""
[REFUTE c62 supp c] 2026-11-23 -- the drift-orthogonal test, plus the tradeable (unlevered) form.

WHY: the mechanical term is proportional to mu (alpha_null = c*mu*(E[1/sig]-E[sig]/E[sig^2])), so
c62's explanation A5 ("alpha_y follows the sign of that year's raw return") and A1 ("63% is
mechanical") both predict: REMOVE THE DRIFT AND THE ALPHA GOES WITH IT. supp a found
recent-minus-2025 keeps alpha +4.84 while its mu collapses +10.36 -> +4.30, which is the opposite
prediction. This script tests it against the properly calibrated (pool-demeaned) null:
  C1 low-drift subsample: XAU recent minus 2025 -- alpha vs its OWN calibrated null.
  C2 per-year excess: for every XAU year, alpha_y, mu_y, calibrated null mean_y, excess_y, z_y.
     Spearman(alpha_y, mu_y) [c62 reported +0.82] vs Spearman(excess_y, mu_y). If the drift
     explanation is right, the second must be ~0 AND the excesses must centre on 0.
     Stouffer z over years = STRUCTURAL test of "is there any timing information at all" --
     D2 note: this is a structural/null test, NOT an edge measurement on a 16y pool, and no
     16y average alpha is used or quoted as an edge.
  C3 the tradeable unlevered form w' = min(w,1) (de-risk only, no borrowing -> no financing leg)
     for XAU recent, against its own calibrated null.
  C4 equity placebo combined: Stouffer z over US500/US100 in-sample-ex2020 + recent excesses.
  C5 corrected multiple testing on the resurrected cell.
Decision rules (fixed before running):
  D1 c62's A1/A5 "it is the drift" BROKEN if the low-drift subsample keeps an excess >= +1.0 sd
     over its own null while mu falls by more than half.
  D2r the drift explanation SURVIVES if Spearman(excess_y, mu_y) is |rho| < 0.35 with the excesses
     centred on 0 (Stouffer |z| < 2).
  D3 C3 relevant only if the unlevered alpha exceeds its own null's 97.5% point.
seed 20261123. Writes data/refute_c62_volmanaged_c.md + _run.log only. No orders, no scan, no network.
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd
from scipy.stats import spearmanr, norm

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c62_volmanaged_c.md")
NY = "America/New_York"; NFMIN = 100; LB = 21; NREP = 2000; NTREP = 300; NWLAG = 5
rng = np.random.default_rng(20261123); L = []
def say(s=""):
    print(s, flush=True); L.append(s)
say(f"# [REFUTE c62 supp c] drift-orthogonal test + unlevered form -- {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c62_volmanaged_c.py)")

def daily_table(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep], "r2": r[keep] ** 2}); g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"] = D["date"].dt.weekday
    D = D[(D.wd <= 4) & (D.nf >= NFMIN)].reset_index()
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["sig21"] = np.sqrt(D["rv"].rolling(LB).mean()) * 1e4
    D["sig1"] = np.sqrt(D["rv"]) * 1e4
    D["year"] = D["date"].dt.year
    return D

def nw_t(y, x, lag=NWLAG):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv; se = np.sqrt(np.diag(V))
    return b[0], b[1], se[0], b[0] / se[0]

def alpha_vec(VM, RR):
    xm = RR.mean(1, keepdims=True); ym = VM.mean(1, keepdims=True)
    xd = RR - xm; yd = VM - ym
    return ym.ravel() - ((xd * yd).sum(1) / (xd * xd).sum(1)) * xm.ravel()

def est_cell(rr, ss, cap=None):
    vm0 = rr / ss; c = rr.std(ddof=1) / vm0.std(ddof=1)
    w = c / ss
    if cap is not None: w = np.minimum(w, cap)
    vm = w * rr
    a, b, se, t = nw_t(vm, rr)
    return dict(a=a, beta=b, c=c, se=se, t=t, n=len(rr), w=w)

def cal_null(rr, ss, sreal, cap=None, reps=NREP, treps=NTREP):
    """pool-demeaned calibrated null (primary from supp b)."""
    mu = rr.mean(); n = len(rr)
    eps = (rr - mu) / sreal; ed = eps - eps.mean()
    E = ed[rng.integers(n, size=(reps, n))]
    RR = mu + sreal[None, :] * E
    VM0 = RR / ss[None, :]
    cv = RR.std(axis=1, ddof=1) / VM0.std(axis=1, ddof=1)
    if cap is None:
        VM = VM0 * cv[:, None]
    else:
        W = np.minimum(cv[:, None] / ss[None, :], cap); VM = W * RR
    a = alpha_vec(VM, RR)
    tn = np.array([nw_t(VM[k], RR[k])[3] for k in range(treps)])
    return a, tn

def win(D, y0, y1, drop=None, keep_only=None):
    sig = D["sig21"].to_numpy()[:-1]; s1t = D["sig1"].to_numpy()[1:]
    r = D["r"].to_numpy()[1:]; yr = D["year"].to_numpy()[1:]
    m = (yr >= y0) & (yr <= y1) & np.isfinite(sig) & np.isfinite(r) & (sig > 0) & np.isfinite(s1t) & (s1t > 0)
    if drop is not None: m &= (yr != drop)
    if keep_only is not None: m &= (yr == keep_only)
    return r[m], sig[m], s1t[m], yr[m]

DX = daily_table("XAU")

say("")
say("## C1 low-drift subsample: does the alpha follow the drift? (D1)")
rows = []
for lab, kw in [("recent 2024-26H1 (full)", dict(y0=2024, y1=2026)),
                ("recent minus 2025", dict(y0=2024, y1=2026, drop=2025)),
                ("2024 only", dict(y0=2024, y1=2024)),
                ("2026H1 only", dict(y0=2026, y1=2026)),
                ("out 2021-26H1 minus 2025", dict(y0=2021, y1=2026, drop=2025)),
                ("2021-23 (flat-drift control)", dict(y0=2021, y1=2023))]:
    rr, ss, s1, yr = win(DX, kw["y0"], kw["y1"], kw.get("drop"))
    if len(rr) < 120: continue
    e = est_cell(rr, ss); a, tn = cal_null(rr, ss, s1)
    exc = e["a"] - a.mean(); z = exc / a.std(ddof=1)
    rows.append((lab, len(rr), rr.mean(), e["a"], e["t"], a.mean(), a.std(ddof=1), exc, z, (a >= e["a"]).mean()))
    say(f"- {lab}: n {len(rr)}  mu {rr.mean():+.2f}  alpha {e['a']:+.2f} (NW t {e['t']:+.2f})  "
        f"null mean {a.mean():+.2f} sd {a.std(ddof=1):.2f} 97.5% {np.percentile(a,97.5):+.2f}  "
        f"excess {exc:+.2f} = {z:+.2f} sd  P(null>=obs) {(a>=e['a']).mean():.4f}")
r_full = rows[0]; r_no25 = rows[1]
say(f"- D1 check: mu {r_full[2]:+.2f} -> {r_no25[2]:+.2f} ({r_no25[2]/r_full[2]*100:.0f}% of drift retained); "
    f"mechanical null {r_full[5]:+.2f} -> {r_no25[5]:+.2f}; excess {r_full[8]:+.2f} sd -> {r_no25[8]:+.2f} sd")

say("")
say("## C2 per-year excess over the calibrated null (XAU)  [structural null test, not an edge measurement -- D2]")
say("| year | n | mu_y | alpha_y | NW t | null mean | null sd | excess | z |")
Y = []
for y in sorted(set(DX["year"].tolist())):
    rr, ss, s1, yr = win(DX, y, y)
    if len(rr) < 120: continue
    e = est_cell(rr, ss); a, tn = cal_null(rr, ss, s1, reps=1000, treps=1)
    exc = e["a"] - a.mean(); z = exc / a.std(ddof=1)
    Y.append(dict(y=y, n=len(rr), mu=rr.mean(), a=e["a"], t=e["t"], nm=a.mean(), nsd=a.std(ddof=1), exc=exc, z=z))
    say(f"| {y} | {len(rr)} | {rr.mean():+.2f} | {e['a']:+.2f} | {e['t']:+.2f} | {a.mean():+.2f} | {a.std(ddof=1):.2f} | {exc:+.2f} | {z:+.2f} |")
mu_y = [d["mu"] for d in Y]; al_y = [d["a"] for d in Y]; ex_y = [d["exc"] for d in Y]; z_y = [d["z"] for d in Y]
r1, p1 = spearmanr(al_y, mu_y); r2, p2 = spearmanr(ex_y, mu_y)
st = np.sum(z_y) / math.sqrt(len(z_y))
say(f"- Spearman(alpha_y, mu_y) {r1:+.2f} (p {p1:.3f})  [c62 reported +0.82]")
say(f"- Spearman(excess_y, mu_y) {r2:+.2f} (p {p2:.3f})  <-- if the drift explains alpha, this must be ~0")
say(f"- excess_y: mean {np.mean(ex_y):+.2f} bp/d  median {np.median(ex_y):+.2f}  positive {sum(1 for x in ex_y if x>0)}/{len(ex_y)}  "
    f"mean z {np.mean(z_y):+.2f}  Stouffer z {st:+.2f} (two-sided p {2*(1-norm.cdf(abs(st))):.3f})")
say(f"- D2r verdict input: |rho(excess,mu)| {abs(r2):.2f} vs threshold 0.35; Stouffer |z| {abs(st):.2f} vs threshold 2")

say("")
say("## C3 tradeable unlevered form w' = min(w,1): de-risk only, no borrowing, no financing leg (D3)")
rr, ss, s1, yr = win(DX, 2024, 2026)
for cap, lab in [(None, "uncapped (c58 estimator)"), (1.0, "cap w<=1.0"), (1.2, "cap w<=1.2")]:
    e = est_cell(rr, ss, cap=cap); a, tn = cal_null(rr, ss, s1, cap=cap)
    exc = e["a"] - a.mean(); z = exc / a.std(ddof=1)
    say(f"- XAU recent {lab}: w mean {e['w'].mean():.3f} max {e['w'].max():.3f}  alpha {e['a']:+.2f} (NW t {e['t']:+.2f})  "
        f"null mean {a.mean():+.2f} sd {a.std(ddof=1):.2f} 97.5% {np.percentile(a,97.5):+.2f}  excess {exc:+.2f} = {z:+.2f} sd  "
        f"P(null>=obs) {(a>=e['a']).mean():.4f}")

say("")
say("## C4 equity placebo combined (does the drift explanation generalise? A5)")
zs = []
for sym in ["US500", "US100"]:
    D2d = daily_table(sym)
    for lab, y0, y1, dy in [("in 2014-20 ex2020", 2014, 2020, 2020), ("recent 2024-26H1", 2024, 2026, None)]:
        sig = D2d["sig21"].to_numpy()[:-1]; s1t = D2d["sig1"].to_numpy()[1:]
        r = D2d["r"].to_numpy()[1:]; yrv = D2d["year"].to_numpy()[1:]
        m = (yrv >= y0) & (yrv <= y1) & np.isfinite(sig) & np.isfinite(r) & (sig > 0) & np.isfinite(s1t) & (s1t > 0)
        if dy is not None: m &= (yrv != dy)
        rr2, ss2, s12 = r[m], sig[m], s1t[m]
        e2 = est_cell(rr2, ss2); a2, _ = cal_null(rr2, ss2, s12, treps=1)
        z2 = (e2["a"] - a2.mean()) / a2.std(ddof=1); zs.append(z2)
        say(f"- {sym} {lab}: mu {rr2.mean():+.2f} (positive drift => A5 predicts alpha ~ mechanical {a2.mean():+.2f})  "
            f"alpha_obs {e2['a']:+.2f}  excess {e2['a']-a2.mean():+.2f} = {z2:+.2f} sd")
stq = np.sum(zs) / math.sqrt(len(zs))
say(f"- combined equity Stouffer z {stq:+.2f} (two-sided p {2*(1-norm.cdf(abs(stq))):.3f})  n cells {len(zs)}  all negative: {all(x<0 for x in zs)}")
say("- A5 prediction for an up-trending asset: alpha_obs ~ mechanical term > 0. Equities show alpha_obs ~ 0 while the mechanical term is positive.")

say("")
say("## C5 corrected multiple testing on the recent cell")
rr, ss, s1, yr = win(DX, 2024, 2026)
e = est_cell(rr, ss); a, _ = cal_null(rr, ss, s1, treps=1)
p_cal = (a >= e["a"]).mean()
say(f"- calibrated one-sided p {p_cal:.4f}  (c58 permutation p was 0.022)  -> Bonferroni(12 pre-registered alpha cells) {min(1.0,p_cal*12):.3f}; "
    f"threshold 0.025/12 = 0.00208 -> {'passes' if p_cal*12 < 0.025 else 'does NOT pass'}")
say("")
say(f"- time {time.time()-T0:.1f}s  seed 20261123  no network  no scan  no MT5  no order  writes: data/refute_c62_volmanaged_c.md only")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT)
