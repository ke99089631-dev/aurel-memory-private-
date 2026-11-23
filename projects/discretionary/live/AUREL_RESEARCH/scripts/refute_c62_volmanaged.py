# -*- coding: utf-8 -*-
"""
[REFUTE c62] 2026-11-23 -- adversarial lane vs cycle62 (18:40) "volatility-managed alpha" entry.

TARGET (what I try to break -- c62's assertions, NOT a promotion candidate; PROMOTED.md is empty):
  A1 "XAU recent 2024-26H1 alpha +5.87 bp/d: 63% of it is the MECHANICAL term +3.70 bp from
      (constant drift mu) x (vol clustering); residual +2.2 bp is 1x se => no timing information."
  A2 "the pre-registered circular-shift permutation null is misspecified / anti-conservative in
      windows with large |mu| (its centre sits at 0)."  [c62 used this to discard its own p=0.022]
  A3 "cost is not the barrier (0.05 bp/d vs alpha 1-6 bp); the barrier is statistics."
  A4 the magnitude claim "+5.87 bp/d = +14.8%/yr".
  A5 "alpha_y follows the sign of that year's raw mean return" => gold VM is a trend-sign artefact,
      not Moreira-Muir.  (cross-asset generality of that explanation)

  NOTE on the arbiter: c62's own "most serious counter-refutation" registered the decisive test and
  did NOT run it: a CALIBRATED null r* = mu_hat + sigma_real * eps*, with sigma_hat21 carrying its
  REAL forecast error, 2000 reps, ask whether +5.87 exceeds the 97.5% point. This script runs it.
  Also note an internal inconsistency in c62 that the entry does not reconcile: data/c58c_...md
  prints "mechanical share of alpha_obs -5%" (= perm centre / alpha_obs) while the findings text
  claims 63% (= formula / alpha_obs). The two nulls disagree by the whole effect. The calibrated
  null is the arbiter between them.

=== PRE-REGISTRATION (written before any number of this script is seen) ===
Data: data/macro/{XAU,US500,US100}_m5_close.npz only (existing cache, bid, 5-min grid).
  No scan, no MT5, no network, no production file touched, read-only outside AUREL_RESEARCH.
Daily layer: COPIED VERBATIM from scripts/c58_vol_managed_premium.py::daily_table (session day
  = ET+6h, valid = Mon-Fri & non-flat bars >= 100, r_d = dlog(last close) bp, RV_d = sum(dlog^2),
  sig21_d = sqrt(mean RV_{d-20..d})*1e4, sig1_d = sqrt(RV_d)*1e4).
  Alignment as c58: predictor sig21 at d (= sig21[:-1]); target r at d+1 (= r[1:]).
  T0 REPLICATION GATE: my alpha/beta/c must match c58c to 2 decimals for XAU in/out/recent
  (+0.33 / +1.77 / +5.87, c 94.7 / 104.8 / 120.7). If not, I stop and report an implementation
  mismatch instead of a verdict.

T1 CALIBRATED NULL (the arbiter; against A1+A2).
  H0: NO vol-timing information. Returns are redrawn as r*_{d+1} = mu_hat + sigma_real_{d+1}*eps*,
  with eps* resampled from the window's own standardized residuals eps_d=(r_d-mu_hat)/sigma_real_d.
  sigma_hat21 is KEPT AT ITS ACTUAL VALUES, so the forecast error of the signal is the real one
  (this is what the closed-form formula assumes away). c is re-matched in sample on each rep,
  exactly as the estimator does. 2000 reps.
  Two bracketing choices of sigma_real (reported side by side, no cherry-picking):
    S1 sigma_real = sig1_{d+1} (realised vol of the TARGET day -- gives the null the true vol path
       => the LARGEST defensible mechanical term => conservative AGAINST the signal);
    S2 sigma_real = sig21_d      (only forecastable vol => smallest mechanical term).
  eps* schemes: (a) iid, (b) stationary block (mean block 5, preserves eps autocorrelation / c19),
  (c) parametric normal. Primary = S1/(a).
  Statistics: alpha* closed form (vectorised, all reps) + NW(5) t on the first 500 reps.
  Decision rules fixed now:
    R1a FORMULA VALIDITY: the closed-form alpha_null is REJECTED as an estimate of the mechanical
        term if |formula - calibrated mean| > 2 * sd(calibrated) in >= 3 of the 7 c58c windows.
    R1b "63% mechanical" is BROKEN if calibrated mean alpha* for XAU recent lies outside
        3.70 +/- sd(calibrated), i.e. the honest mechanical share differs from 63% by more than
        one null sd. It SURVIVES if 3.70 is inside.
    R2 "no timing information" is BROKEN if alpha_obs(+5.87) > 97.5% point of the calibrated null
        under BOTH S1 and S2 (and I then keep attacking the resurrected signal with T2-T6);
        it SURVIVES if alpha_obs <= 97.5% point under S1 (the conservative bracket).
    R2b A2 (permutation null is anti-conservative) is CONFIRMED if the calibrated mean is clearly
        above the permutation centre (> 2 perm sd), BROKEN if the calibrated mean is itself ~0.
T2 EPISODE FRAGILITY (against the signal, regardless of R2).
  Leave-one-year-out inside recent (drop 2025 / 2024 / 2026H1); leave-one-month-out (all months,
  report min/max/sign flips); tail dependence: alpha after winsorising r at +/-3sd, and after
  dropping the 10 largest |r| days.  R3: single-episode if alpha(recent minus 2025) NW t < 1.0.
T3 COST AND LEVERAGE (against A3).
  Implied weight w_d = c/sig21_d. Report mean/median/max/p95 of w and mean|dw| (c62/c58b claimed
  w_bar 1.1-1.2, w_max ~2, mean|dw| 0.017-0.020, cost 0.05 bp/d). Spread cost = mean|dw| * S with
  S in {5.3, 10.6, 53.0} bp round trip (1x, 2x, 10x). Financing on excess exposure:
  cost_f = mean(max(w-1,0)) * f_annual/252; report break-even f* that sets alpha_net = 0 and the f
  that pushes NW t below 2. Leverage-capped variant w' = min(w,1) (de-risk only, no borrowing).
  R4: A3 BROKEN if break-even f* < 10%/yr, or if the capped-w alpha loses > 50% of +5.87.
T4 IN-SAMPLE SCALING / LOOK-AHEAD (against A4).
  The estimator sets c by matching sd(vm)=sd(r) INSIDE the evaluation window (future data).
  Causal variant: c_d from all history up to d-1 (expanding, >= 250 obs). Report alpha with causal
  c and with c frozen at the in-window 2010-20 value.  R5: A4 overstated if |alpha_causal - 5.87|
  / 5.87 > 0.20. (t is invariant to c by construction -- state that, do not claim it as a break.)
T5 CROSS-ASSET PLACEBO (against A5 and against the signal).
  Same pipeline + same calibrated null for US500 and US100, recent 2024-26H1 (both strongly
  up-trending, so A5 predicts a positive alpha for them too). Also Spearman(alpha_y, r_bar_y) per
  asset.  R6: if US100 and/or US500 recent also exceed their calibrated 97.5% point with z within
  1.0 of XAU's, the XAU excess is NOT gold-specific; if they sit at 0 while XAU does not, A5's
  "trend-sign artefact" explanation fails to generalise and XAU's excess needs another cause.
T6 MULTIPLE TESTING on the resurrected cell only (4 estimators x 3 windows = 12 pre-registered
  alpha cells in c58): Bonferroni(12) on the calibrated p, and max-t over the 4 estimators under
  the calibrated null (family-wise, correlation-aware).

VERDICT MAP (fixed now): per target A1..A5 -> survived / broken / inconclusive, each with numbers.
A refutation lane finding that the dismissal was wrong is NOT a promotion: any resurrected cell
still has to clear T2/T3/T6, and PROMOTED.md is not touched by this script.
Writes: data/refute_c62_volmanaged.md + _run.log only. seed 20261123.
"""
import os, sys, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c62_volmanaged.md")
NY = "America/New_York"; NFMIN = 100; LB = 21; NREP = 2000; NTREP = 500; NWLAG = 5
rng = np.random.default_rng(20261123)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)

say(f"# [REFUTE c62] calibrated null for the volatility-managed alpha -- {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c62_volmanaged.py)")
say("")

# ---------- daily layer: verbatim logic from c58_vol_managed_premium.py ----------
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
    D["year"] = D["date"].dt.year; D["month"] = D["date"].dt.month
    return D

def nw_t(y, x, lag=NWLAG):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv
    se = np.sqrt(np.diag(V))
    return b[0], b[1], se[0], b[0] / se[0]

def alpha_vec(VM, RR):
    """closed-form OLS intercept of VM on RR, row-wise (reps x n)."""
    xm = RR.mean(1, keepdims=True); ym = VM.mean(1, keepdims=True)
    xd = RR - xm; yd = VM - ym
    beta = (xd * yd).sum(1) / (xd * xd).sum(1)
    return ym.ravel() - beta * xm.ravel(), beta

def est_cell(rr, ss):
    """the c58 estimator: vm = c*r/sig with c matched in-sample; return alpha,beta,c,se,t."""
    vm0 = rr / ss; c = rr.std(ddof=1) / vm0.std(ddof=1); vm = vm0 * c
    a, b, se, t = nw_t(vm, rr)
    return dict(a=a, beta=b, c=c, se=se, t=t, n=len(rr), vm=vm, w=c / ss)

def win_slice(D, y0, y1):
    sig = D["sig21"].to_numpy()[:-1]
    sig1_tgt = D["sig1"].to_numpy()[1:]
    r = D["r"].to_numpy()[1:]; yr = D["year"].to_numpy()[1:]; mo = D["month"].to_numpy()[1:]
    m = (yr >= y0) & (yr <= y1) & np.isfinite(sig) & np.isfinite(r) & (sig > 0) & np.isfinite(sig1_tgt) & (sig1_tgt > 0)
    return r[m], sig[m], sig1_tgt[m], yr[m], mo[m]

def formula_alpha(rr, ss, c):
    mu = rr.mean()
    return c * mu * (np.mean(1.0 / ss) - np.mean(ss) / np.mean(ss ** 2))

def block_idx(n, mblock, rng, reps):
    """stationary bootstrap indices (geometric blocks, mean length mblock), reps x n."""
    p = 1.0 / mblock
    idx = np.empty((reps, n), dtype=np.int64)
    idx[:, 0] = rng.integers(n, size=reps)
    newb = rng.random((reps, n)) < p
    starts = rng.integers(n, size=(reps, n))
    for j in range(1, n):
        idx[:, j] = np.where(newb[:, j], starts[:, j], (idx[:, j - 1] + 1) % n)
    return idx

def calibrated_null(rr, ss, sreal, scheme="iid", reps=NREP, treps=NTREP, tag=""):
    """r* = mu + sreal*eps*, sig_hat kept actual; returns null alpha dist and NW t dist."""
    mu = rr.mean()
    eps = (rr - mu) / sreal
    n = len(rr)
    if scheme == "iid":
        E = eps[rng.integers(n, size=(reps, n))]
    elif scheme == "block":
        E = eps[block_idx(n, 5, rng, reps)]
    elif scheme == "normal":
        E = rng.standard_normal((reps, n)) * eps.std(ddof=1)
    RR = mu + sreal[None, :] * E
    VM0 = RR / ss[None, :]
    cvec = RR.std(axis=1, ddof=1) / VM0.std(axis=1, ddof=1)
    VM = VM0 * cvec[:, None]
    a_null, b_null = alpha_vec(VM, RR)
    tn = np.empty(treps)
    for k in range(treps):
        tn[k] = nw_t(VM[k], RR[k])[3]
    return dict(a=a_null, t=tn, eps_sd=eps.std(ddof=1), eps_mean=eps.mean(),
                eps_kurt=float(pd.Series(eps).kurt()), tag=tag)

# ---------------- data ----------------
say("## 0. data + replication gate")
DX = daily_table("XAU")
say(f"- XAU valid sessions {len(DX)}  {DX.date.min().date()}..{DX.date.max().date()}")
WX = {"in 2010-20": (2010, 2020), "out 2021-26H1": (2021, 2026), "recent 2024-26H1": (2024, 2026),
      "2025": (2025, 2025), "2013": (2013, 2013)}
cells = {}
for w, (y0, y1) in WX.items():
    rr, ss, s1, yr, mo = win_slice(DX, y0, y1)
    cells[("XAU", w)] = (rr, ss, s1, yr, mo, est_cell(rr, ss))
    e = cells[("XAU", w)][5]
    say(f"- XAU {w}: n {e['n']}  mu {rr.mean():+.2f} bp/d  c {e['c']:.1f}  alpha {e['a']:+.2f}  beta {e['beta']:.3f}  se {e['se']:.2f}  NW t {e['t']:+.2f}")
ref = {"in 2010-20": (0.33, 94.7), "out 2021-26H1": (1.77, 104.8), "recent 2024-26H1": (5.87, 120.7)}
gate_ok = True
for w, (a_ref, c_ref) in ref.items():
    e = cells[("XAU", w)][5]
    ok = abs(e["a"] - a_ref) < 0.015 and abs(e["c"] - c_ref) < 0.15
    gate_ok &= ok
    say(f"- GATE {w}: alpha {e['a']:+.3f} vs c58c {a_ref:+.2f} | c {e['c']:.2f} vs {c_ref:.1f} -> {'MATCH' if ok else 'MISMATCH'}")
say(f"- T0 replication gate: {'PASS -- same pipeline as c58/c58c, so every number below is comparable' if gate_ok else 'FAIL -- stopping before any verdict'}")
if not gate_ok:
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); sys.exit(1)

# ---------------- T1 calibrated null ----------------
say("")
say("## T1 calibrated null (arbiter for A1/A2): r* = mu + sigma_real*eps*, sigma_hat21 keeps its REAL forecast error")
say("- S1 sigma_real = sig1 of the TARGET day (true vol path -> largest defensible mechanical term, conservative against the signal)")
say("- S2 sigma_real = sig21 of day d (forecastable vol only -> smallest mechanical term)")
T1 = {}
for w in ["in 2010-20", "out 2021-26H1", "recent 2024-26H1", "2025", "2013"]:
    rr, ss, s1, yr, mo, e = cells[("XAU", w)]
    fa = formula_alpha(rr, ss, e["c"])
    say(f"\n- XAU {w}: alpha_obs {e['a']:+.2f} (NW t {e['t']:+.2f})  | closed-form formula alpha_null {fa:+.2f} (c62 uses this: share {fa/e['a']*100 if abs(e['a'])>1e-9 else float('nan'):.0f}%)")
    for sname, sre in [("S1 sig1_tgt", s1), ("S2 sig21_d", ss)]:
        for scheme in (["iid", "block", "normal"] if w == "recent 2024-26H1" else ["iid"]):
            nd = calibrated_null(rr, ss, sre, scheme=scheme)
            a = nd["a"]; q975 = np.percentile(a, 97.5); q25 = np.percentile(a, 2.5)
            p_up = (a >= e["a"]).mean()
            tq = np.percentile(nd["t"], 97.5)
            T1[(w, sname, scheme)] = dict(mean=a.mean(), sd=a.std(ddof=1), q975=q975, q25=q25,
                                          p_up=p_up, tmean=nd["t"].mean(), tq975=tq, obs=e["a"], tobs=e["t"])
            say(f"    {sname} eps={scheme}: null alpha mean {a.mean():+.2f} sd {a.std(ddof=1):.2f} "
                f"[2.5% {q25:+.2f}, 97.5% {q975:+.2f}]  P(alpha*>=obs) {p_up:.4f}  "
                f"| null NW t mean {nd['t'].mean():+.2f} 97.5% {tq:+.2f} (obs t {e['t']:+.2f})  "
                f"| eps mean {nd['eps_mean']:+.3f} sd {nd['eps_sd']:.3f} exkurt {nd['eps_kurt']:+.1f}")

# R1a formula validity across windows (XAU 5 windows + US500 2, filled after T5)
say("")
say("## T1b formula-vs-calibrated (R1a: is the closed form a usable estimate of the mechanical term?)")
r1a_rows = []
for w in ["in 2010-20", "out 2021-26H1", "recent 2024-26H1", "2025", "2013"]:
    rr, ss, s1, yr, mo, e = cells[("XAU", w)]
    fa = formula_alpha(rr, ss, e["c"]); k = (w, "S1 sig1_tgt", "iid")
    d = fa - T1[k]["mean"]; z = d / T1[k]["sd"]
    r1a_rows.append(("XAU", w, fa, T1[k]["mean"], T1[k]["sd"], z))
    say(f"- XAU {w}: formula {fa:+.2f} vs calibrated S1 {T1[k]['mean']:+.2f} (sd {T1[k]['sd']:.2f}) -> diff {d:+.2f} = {z:+.2f} null sd")

# ---------------- T2 episode fragility ----------------
say("")
say("## T2 episode fragility of the recent cell")
rr, ss, s1, yr, mo, e = cells[("XAU", "recent 2024-26H1")]
for drop in [2025, 2024, 2026]:
    k = yr != drop
    if k.sum() > 60:
        ee = est_cell(rr[k], ss[k])
        say(f"- recent minus {drop}: n {ee['n']}  mu {rr[k].mean():+.2f}  alpha {ee['a']:+.2f}  se {ee['se']:.2f}  NW t {ee['t']:+.2f}")
ym = yr * 100 + mo; uym = np.unique(ym)
lom = []
for u in uym:
    k = ym != u
    ee = est_cell(rr[k], ss[k]); lom.append((u, ee["a"], ee["t"]))
av = np.array([x[1] for x in lom])
worst = min(lom, key=lambda x: x[1]); best = max(lom, key=lambda x: x[1])
say(f"- leave-one-month-out ({len(lom)} months): alpha min {av.min():+.2f} (drop {worst[0]}, t {worst[2]:+.2f})  max {av.max():+.2f} (drop {best[0]})  median {np.median(av):+.2f}  n(t<2) {sum(1 for x in lom if x[2]<2)}/{len(lom)}  n(t<1) {sum(1 for x in lom if x[2]<1)}")
mu_ = rr.mean(); sd_ = rr.std(ddof=1)
rw = np.clip(rr, mu_ - 3 * sd_, mu_ + 3 * sd_)
ew = est_cell(rw, ss)
say(f"- winsorise r at +/-3sd ({(np.abs(rr-mu_)>3*sd_).sum()} days clipped): alpha {ew['a']:+.2f}  NW t {ew['t']:+.2f}")
ordr = np.argsort(-np.abs(rr - mu_)); keep = np.ones(len(rr), bool); keep[ordr[:10]] = False
ed = est_cell(rr[keep], ss[keep])
say(f"- drop 10 largest |r| days: n {ed['n']}  alpha {ed['a']:+.2f}  NW t {ed['t']:+.2f}")

# ---------------- T3 cost and leverage ----------------
say("")
say("## T3 cost and leverage (A3: 'cost is not the barrier, 0.05 bp/d')")
w_ = e["w"]; dw = np.abs(np.diff(w_))
say(f"- implied weight w = c/sig21: mean {w_.mean():.3f}  median {np.median(w_):.3f}  p95 {np.percentile(w_,95):.3f}  max {w_.max():.3f}  (c62/c58b claimed w_bar 1.1-1.2, w_max ~2)")
say(f"- mean|dw| {dw.mean():.4f}/d  p95 {np.percentile(dw,95):.4f}  (c58b claimed 0.017-0.020)")
for S, lab in [(5.3, "1x (c58b)"), (10.6, "2x"), (53.0, "10x")]:
    cst = dw.mean() * S
    say(f"- spread cost at {lab} round trip {S:.1f} bp: {cst:.3f} bp/d -> alpha_net {e['a']-cst:+.2f} ({(e['a']-cst)/e['a']*100:.0f}% of alpha)")
exc = np.maximum(w_ - 1.0, 0.0).mean()
say(f"- mean excess exposure max(w-1,0) = {exc:.3f} of notional")
for f in [2.0, 5.0, 7.0, 10.0, 15.0]:
    cf = exc * f * 1e4 / 100.0 / 252.0
    say(f"- financing at {f:.0f}%/yr on the excess: {cf:.3f} bp/d -> alpha_net {e['a']-cf:+.2f}  NW t_net ~{(e['a']-cf)/e['se']:+.2f}")
f_be = e["a"] / exc * 252.0 * 100.0 / 1e4 if exc > 0 else float("nan")
f_t2 = (e["a"] - 2 * e["se"]) / exc * 252.0 * 100.0 / 1e4 if exc > 0 else float("nan")
say(f"- BREAK-EVEN financing f* (alpha_net=0): {f_be:.1f}%/yr   | f that pushes NW t below 2: {f_t2:.1f}%/yr")
wc = np.minimum(w_, 1.0)
vmc = wc * rr; a_c, b_c, se_c, t_c = nw_t(vmc, rr)
say(f"- leverage-capped w'=min(w,1) (de-risk only, no borrowing): alpha {a_c:+.2f}  se {se_c:.2f}  NW t {t_c:+.2f}  ({a_c/e['a']*100:.0f}% of +{e['a']:.2f})")

# ---------------- T4 in-sample scaling ----------------
say("")
say("## T4 in-sample scaling constant c (A4: the '+14.8%/yr' magnitude)")
sig_all = DX["sig21"].to_numpy()[:-1]; r_all = DX["r"].to_numpy()[1:]; yr_all = DX["year"].to_numpy()[1:]
ok = np.isfinite(sig_all) & np.isfinite(r_all) & (sig_all > 0)
sa = sig_all[ok]; ra = r_all[ok]; ya = yr_all[ok]
vm0a = ra / sa
c_caus = np.full(len(ra), np.nan)
for i in range(250, len(ra)):
    c_caus[i] = ra[:i].std(ddof=1) / vm0a[:i].std(ddof=1)
mrec = (ya >= 2024) & np.isfinite(c_caus)
vm_caus = vm0a[mrec] * c_caus[mrec]
a_ca, b_ca, se_ca, t_ca = nw_t(vm_caus, ra[mrec])
say(f"- causal c (expanding, all history up to d-1): c mean {np.nanmean(c_caus[mrec]):.1f} (in-sample c {e['c']:.1f})  alpha {a_ca:+.2f} bp/d ({a_ca*252/1e2:+.2f}%/yr)  NW t {t_ca:+.2f}  n {mrec.sum()}")
c_in = cells[("XAU", "in 2010-20")][5]["c"]
vm_fz = vm0a[mrec] * c_in
a_fz, b_fz, se_fz, t_fz = nw_t(vm_fz, ra[mrec])
say(f"- c frozen at the in-sample-window value {c_in:.1f}: alpha {a_fz:+.2f} bp/d ({a_fz*252/1e2:+.2f}%/yr)  NW t {t_fz:+.2f}")
say(f"- note: t is invariant to c by construction (alpha and se scale together) -- the look-ahead affects the ECONOMIC MAGNITUDE claim only, not significance")

# ---------------- T5 cross-asset placebo ----------------
say("")
say("## T5 cross-asset placebo (A5 'trend-sign artefact' should generalise to other up-trending assets)")
for sym in ["US500", "US100"]:
    D2 = daily_table(sym)
    say(f"- {sym}: valid sessions {len(D2)}  {D2.date.min().date()}..{D2.date.max().date()}")
    for w, (y0, y1) in [("in 2014-20", (2014, 2020)), ("out 2021-26H1", (2021, 2026)), ("recent 2024-26H1", (2024, 2026))]:
        rr2, ss2, s12, yr2, mo2 = win_slice(D2, y0, y1)
        if len(rr2) < 100: continue
        e2 = est_cell(rr2, ss2); fa2 = formula_alpha(rr2, ss2, e2["c"])
        nd2 = calibrated_null(rr2, ss2, s12, scheme="iid", reps=NREP, treps=200)
        a2 = nd2["a"]
        say(f"  - {sym} {w}: n {e2['n']} mu {rr2.mean():+.2f}  alpha_obs {e2['a']:+.2f} (NW t {e2['t']:+.2f})  formula {fa2:+.2f}  "
            f"| calibrated S1 null mean {a2.mean():+.2f} sd {a2.std(ddof=1):.2f} 97.5% {np.percentile(a2,97.5):+.2f}  "
            f"P(>=obs) {(a2>=e2['a']).mean():.4f}  excess {e2['a']-a2.mean():+.2f} = {(e2['a']-a2.mean())/a2.std(ddof=1):+.2f} sd")
        if w == "recent 2024-26H1":
            say(f"    formula-vs-calibrated: {fa2:+.2f} vs {a2.mean():+.2f} -> {(fa2-a2.mean())/a2.std(ddof=1):+.2f} null sd")
    yrs = sorted(set(D2["year"].tolist()))
    rows = []
    for y in yrs:
        rr3, ss3, _, _, _ = win_slice(D2, y, y)
        if len(rr3) < 120: continue
        e3 = est_cell(rr3, ss3); rows.append((y, e3["a"], rr3.mean()))
    if len(rows) >= 5:
        from scipy.stats import spearmanr
        rho, pv = spearmanr([x[1] for x in rows], [x[2] for x in rows])
        sgn = sum(1 for x in rows if (x[1] > 0) == (x[2] > 0))
        say(f"  - {sym} yearly: Spearman(alpha_y, r_bar_y) {rho:+.2f} (p {pv:.3f})  sign agreement {sgn}/{len(rows)}  alpha>0 {sum(1 for x in rows if x[1]>0)}/{len(rows)}")
# XAU yearly for comparison
rows = []
for y in sorted(set(DX["year"].tolist())):
    rr3, ss3, _, _, _ = win_slice(DX, y, y)
    if len(rr3) < 120: continue
    e3 = est_cell(rr3, ss3); rows.append((y, e3["a"], rr3.mean()))
from scipy.stats import spearmanr
rho, pv = spearmanr([x[1] for x in rows], [x[2] for x in rows])
say(f"- XAU yearly (c62 reported +0.82): Spearman(alpha_y, r_bar_y) {rho:+.2f} (p {pv:.3f})  sign agreement {sum(1 for x in rows if (x[1]>0)==(x[2]>0))}/{len(rows)}")

# ---------------- T6 multiple testing on the resurrected cell ----------------
say("")
say("## T6 multiple testing (12 pre-registered alpha cells in c58: 4 estimators x 3 windows)")
rr, ss, s1, yr, mo, e = cells[("XAU", "recent 2024-26H1")]
k = ("recent 2024-26H1", "S1 sig1_tgt", "iid")
p_cal = T1[k]["p_up"]
say(f"- calibrated one-sided p for the recent cell: {p_cal:.4f}  -> Bonferroni(12) {min(1.0, p_cal*12):.4f}  (threshold 0.025/12 = 0.00208)")
# max-t over the 4 estimators under the calibrated null (correlation aware)
sig1_pred = DX["sig1"].to_numpy()[:-1]
rr_f, ss_f, s1_f, yr_f, mo_f = win_slice(DX, 2024, 2026)
# rebuild estimator variants on the same mask
sigA = DX["sig21"].to_numpy()[:-1]; sigB = DX["sig1"].to_numpy()[:-1]
rA = DX["r"].to_numpy()[1:]; s1t = DX["sig1"].to_numpy()[1:]; yA = DX["year"].to_numpy()[1:]
mm = (yA >= 2024) & np.isfinite(sigA) & np.isfinite(sigB) & (sigA > 0) & (sigB > 0) & np.isfinite(rA) & np.isfinite(s1t) & (s1t > 0)
rrm = rA[mm]; sA = sigA[mm]; sB = sigB[mm]; sr = s1t[mm]
obs_ts = []
for nm, sv in [("VM21", sA), ("VM1", sB)]:
    ee = est_cell(rrm, sv); obs_ts.append((nm, ee["t"]))
say(f"- observed NW t on the common mask: " + "  ".join(f"{nm} {t:+.2f}" for nm, t in obs_ts))
mu = rrm.mean(); eps = (rrm - mu) / sr; n = len(rrm)
NMX = 500
maxt = np.empty(NMX)
for i in range(NMX):
    rs = mu + sr * eps[rng.integers(n, size=n)]
    ts = []
    for sv in [sA, sB]:
        v0 = rs / sv; cc = rs.std(ddof=1) / v0.std(ddof=1)
        ts.append(nw_t(v0 * cc, rs)[3])
    maxt[i] = max(ts)
obs_max = max(t for _, t in obs_ts)
say(f"- max-t over the 2 vol estimators (VM21, VM1) under the calibrated null, {NMX} reps: null max-t 97.5% {np.percentile(maxt,97.5):+.2f}  mean {maxt.mean():+.2f}  | observed max-t {obs_max:+.2f}  family-wise P {(maxt>=obs_max).mean():.4f}")

say("")
say(f"- time {time.time()-T0:.1f}s  seed 20261123  no network  no scan  no MT5  no order  writes: data/refute_c62_volmanaged.md only")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT)
