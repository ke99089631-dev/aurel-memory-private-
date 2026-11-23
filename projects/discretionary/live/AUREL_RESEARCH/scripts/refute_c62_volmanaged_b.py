# -*- coding: utf-8 -*-
"""
[REFUTE c62 supp b] 2026-11-23 -- SELF-REFUTATION of refute_c62_volmanaged.py's own null.

BUG FOUND IN MY OWN T1 (found before writing a verdict, reported because it moved the headline):
  the calibrated null drew r* = mu_hat + sigma_real * eps* with eps* resampled IID from
  eps_d = (r_d - mu_hat)/sigma_real_d. By construction mean(sigma_real*eps) = 0 over the MATCHED
  pairs, but resampling breaks the pairing, so
      E[mean(r*)] = mu_hat + mean(sigma_real) * mean(eps),
  and mean(eps) is NOT zero (XAU recent +0.077). mean(eps) > 0 means "(r-mu) tends to be positive
  when sigma_real is small" -- which IS the vol-timing signal. So my null injected part of the
  signal into its own drift, inflating the null's mechanical alpha (alpha_null is proportional to
  mu) and biasing the test TOWARDS "c62 survived". Direction of the bias favoured the conclusion I
  was about to report, so it has to be fixed before the verdict, not after.

FIX (primary here): demean the eps POOL once, eps~ = eps - mean(eps), then r* = mu_hat +
  sigma_real * eps~*. Now E[mean(r*)] = mu_hat exactly, the drift is calibrated to the observed
  drift, and no timing information survives. Pool-level (not per-rep) demeaning keeps the null's
  sampling variation in the drift comparable to the data's.
SECONDARY: per-rep drift match (demean eps* inside each rep) -> conditions on mu_hat, narrower null.
ALSO ADDED: (1) mean(eps) printed for every asset/window so the size of the bug is visible;
  (2) US500 in-sample EX-2020 window (c58 reported alpha -0.25 there; the 2020 vol dispersion drives
  a large mechanical term, so the equity "negative excess" must be checked without it);
  (3) the tradeable timing statistic mean((r-mu)/sigma_hat21_{d-1}) with its calibrated null.
No new daily-layer code: same daily_table as c58 (gate re-asserted). seed 20261123.
Writes data/refute_c62_volmanaged_b.md + _run.log only. Read-only elsewhere. No orders, no scan.
"""
import os, sys, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c62_volmanaged_b.md")
NY = "America/New_York"; NFMIN = 100; LB = 21; NREP = 2000; NTREP = 400; NWLAG = 5
rng = np.random.default_rng(20261123)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
say(f"# [REFUTE c62 supp b] drift-calibrated null (fixes a bias in my own supp a) -- {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c62_volmanaged_b.py)")

def daily_table(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep], "r2": r[keep] ** 2})
    g = df.groupby("o", sort=True)
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
    beta = (xd * yd).sum(1) / (xd * xd).sum(1)
    return ym.ravel() - beta * xm.ravel()

def est_cell(rr, ss):
    vm0 = rr / ss; c = rr.std(ddof=1) / vm0.std(ddof=1); vm = vm0 * c
    a, b, se, t = nw_t(vm, rr)
    return dict(a=a, beta=b, c=c, se=se, t=t, n=len(rr))

def win_slice(D, y0, y1, drop_year=None):
    sig = D["sig21"].to_numpy()[:-1]; s1t = D["sig1"].to_numpy()[1:]
    r = D["r"].to_numpy()[1:]; yr = D["year"].to_numpy()[1:]
    m = (yr >= y0) & (yr <= y1) & np.isfinite(sig) & np.isfinite(r) & (sig > 0) & np.isfinite(s1t) & (s1t > 0)
    if drop_year is not None: m &= (yr != drop_year)
    return r[m], sig[m], s1t[m]

def formula_alpha(rr, ss, c):
    mu = rr.mean(); return c * mu * (np.mean(1.0 / ss) - np.mean(ss) / np.mean(ss ** 2))

def cal_null(rr, ss, sreal, mode="pool_demean", reps=NREP, treps=NTREP):
    mu = rr.mean(); n = len(rr)
    eps = (rr - mu) / sreal
    e_mean = eps.mean()
    if mode == "raw":            # the biased version from supp a, kept for comparison
        E = eps[rng.integers(n, size=(reps, n))]
    elif mode == "pool_demean":  # PRIMARY fix
        ed = eps - e_mean; E = ed[rng.integers(n, size=(reps, n))]
    elif mode == "rep_demean":   # per-rep exact drift match
        E = eps[rng.integers(n, size=(reps, n))]; E = E - E.mean(1, keepdims=True)
    RR = mu + sreal[None, :] * E
    VM0 = RR / ss[None, :]
    cv = RR.std(axis=1, ddof=1) / VM0.std(axis=1, ddof=1)
    VM = VM0 * cv[:, None]
    a = alpha_vec(VM, RR)
    tn = np.array([nw_t(VM[k], RR[k])[3] for k in range(treps)])
    return dict(a=a, t=tn, e_mean=e_mean, mu_null=RR.mean(1).mean(), mu_obs=mu)

WINS = {
    "XAU": [("in 2010-20", 2010, 2020, None), ("out 2021-26H1", 2021, 2026, None),
            ("recent 2024-26H1", 2024, 2026, None), ("2025", 2025, 2025, None), ("2013", 2013, 2013, None)],
    "US500": [("in 2014-20", 2014, 2020, None), ("in 2014-20 ex2020", 2014, 2020, 2020),
              ("out 2021-26H1", 2021, 2026, None), ("recent 2024-26H1", 2024, 2026, None)],
    "US100": [("in 2014-20", 2014, 2020, None), ("in 2014-20 ex2020", 2014, 2020, 2020),
              ("out 2021-26H1", 2021, 2026, None), ("recent 2024-26H1", 2024, 2026, None)],
}
say("")
say("## 1. size of the bug: mean(eps) and the drift it injected into supp a's null")
say("| asset | window | n | mu_obs | mean(eps) | injected drift = mean(sig_real)*mean(eps) | mu_null(raw) |")
for sym, ws in WINS.items():
    D = daily_table(sym)
    for (w, y0, y1, dy) in ws:
        rr, ss, s1 = win_slice(D, y0, y1, dy)
        if len(rr) < 120: continue
        eps = (rr - rr.mean()) / s1
        inj = s1.mean() * eps.mean()
        say(f"| {sym} | {w} | {len(rr)} | {rr.mean():+.2f} | {eps.mean():+.4f} | {inj:+.2f} bp/d | {rr.mean()+inj:+.2f} |")

say("")
say("## 2. corrected calibrated null (primary = pool-demeaned eps; sigma_real = sig1 of target day)")
say("   rule from supp a: c62's 'no timing information' SURVIVES if alpha_obs <= 97.5% of the null; BROKEN if above under both brackets.")
SUM = {}
for sym, ws in WINS.items():
    D = daily_table(sym)
    say(f"\n### {sym}")
    for (w, y0, y1, dy) in ws:
        rr, ss, s1 = win_slice(D, y0, y1, dy)
        if len(rr) < 120: continue
        e = est_cell(rr, ss); fa = formula_alpha(rr, ss, e["c"])
        out = [f"- {w}: n {e['n']} mu {rr.mean():+.2f}  **alpha_obs {e['a']:+.2f}** (NW t {e['t']:+.2f}, se {e['se']:.2f})  formula {fa:+.2f}"]
        for mode in ["raw", "pool_demean", "rep_demean"]:
            nd = cal_null(rr, ss, s1, mode=mode)
            a = nd["a"]; q = np.percentile(a, [2.5, 97.5])
            exc = e["a"] - a.mean(); z = exc / a.std(ddof=1)
            p_up = (a >= e["a"]).mean(); p_dn = (a <= e["a"]).mean()
            if mode == "pool_demean":
                SUM[(sym, w)] = dict(obs=e["a"], t=e["t"], nullmean=a.mean(), nullsd=a.std(ddof=1),
                                     q975=q[1], p_up=p_up, p_dn=p_dn, z=z, n=e["n"], mu=rr.mean(),
                                     tnull975=np.percentile(nd["t"], 97.5), formula=fa)
            star = "  <-- PRIMARY" if mode == "pool_demean" else ""
            out.append(f"    {mode:12s}: mu_null {nd['mu_null']:+.2f}  null alpha mean {a.mean():+.2f} sd {a.std(ddof=1):.2f} "
                       f"[{q[0]:+.2f},{q[1]:+.2f}]  excess {exc:+.2f} = {z:+.2f} sd  P(null>=obs) {p_up:.4f}  P(null<=obs) {p_dn:.4f}"
                       f"  null t 97.5% {np.percentile(nd['t'],97.5):+.2f}{star}")
        for o in out: say(o)

say("")
say("## 3. tradeable timing statistic  m = mean((r - mu)/sigma_hat21_{d-1})  (uses only information known at d)")
say("   m > 0 <=> returns were better when the PREDICTED vol was low. Null = pool-demeaned calibrated null.")
for sym, ws in WINS.items():
    D = daily_table(sym)
    for (w, y0, y1, dy) in ws:
        rr, ss, s1 = win_slice(D, y0, y1, dy)
        if len(rr) < 120: continue
        mu = rr.mean(); m_obs = np.mean((rr - mu) / ss) * 1e2   # x100 for readability
        eps = (rr - mu) / s1; ed = eps - eps.mean(); n = len(rr)
        E = ed[rng.integers(n, size=(NREP, n))]
        RR = mu + s1[None, :] * E
        mnull = ((RR - RR.mean(1, keepdims=True)) / ss[None, :]).mean(1) * 1e2
        z = (m_obs - mnull.mean()) / mnull.std(ddof=1)
        say(f"- {sym} {w}: m_obs {m_obs:+.3f} (x100)  null mean {mnull.mean():+.3f} sd {mnull.std(ddof=1):.3f}  z {z:+.2f}  P(null>=obs) {(mnull>=m_obs).mean():.4f}")

say("")
say("## 4. verdict inputs (pool-demeaned primary)")
say("| asset | window | alpha_obs | NW t | null mean | null sd | null 97.5% | excess (sd) | P(null>=obs) |")
for k, v in SUM.items():
    say(f"| {k[0]} | {k[1]} | {v['obs']:+.2f} | {v['t']:+.2f} | {v['nullmean']:+.2f} | {v['nullsd']:.2f} | {v['q975']:+.2f} | {v['z']:+.2f} | {v['p_up']:.4f} |")
say("")
say(f"- time {time.time()-T0:.1f}s  seed 20261123  no network  no scan  no MT5  no order  writes: data/refute_c62_volmanaged_b.md only")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT)
