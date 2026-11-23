# [REFUTE c62] calibrated null for the volatility-managed alpha -- 2026-11-23 21:35 (scripts/refute_c62_volmanaged.py)

## 0. data + replication gate
- XAU valid sessions 4243  2010-01-01..2026-06-30
- XAU in 2010-20: n 2809  mu +2.01 bp/d  c 94.7  alpha +0.33  beta 0.952  se 0.61  NW t +0.55
- XAU out 2021-26H1: n 1413  mu +5.29 bp/d  c 104.8  alpha +1.77  beta 0.936  se 1.10  NW t +1.62
- XAU recent 2024-26H1: n 641  mu +10.36 bp/d  c 120.7  alpha +5.87  beta 0.925  se 2.08  NW t +2.82
- XAU 2025: n 255  mu +19.54 bp/d  c 110.5  alpha +5.21  beta 0.963  se 2.08  NW t +2.50
- XAU 2013: n 245  mu -13.43 bp/d  c 104.2  alpha -4.18  beta 0.959  se 2.32  NW t -1.80
- GATE in 2010-20: alpha +0.334 vs c58c +0.33 | c 94.66 vs 94.7 -> MATCH
- GATE out 2021-26H1: alpha +1.773 vs c58c +1.77 | c 104.85 vs 104.8 -> MATCH
- GATE recent 2024-26H1: alpha +5.866 vs c58c +5.87 | c 120.72 vs 120.7 -> MATCH
- T0 replication gate: PASS -- same pipeline as c58/c58c, so every number below is comparable

## T1 calibrated null (arbiter for A1/A2): r* = mu + sigma_real*eps*, sigma_hat21 keeps its REAL forecast error
- S1 sigma_real = sig1 of the TARGET day (true vol path -> largest defensible mechanical term, conservative against the signal)
- S2 sigma_real = sig21 of day d (forecastable vol only -> smallest mechanical term)

- XAU in 2010-20: alpha_obs +0.33 (NW t +0.55)  | closed-form formula alpha_null +0.43 (c62 uses this: share 128%)
    S1 sig1_tgt eps=iid: null alpha mean +0.57 sd 0.56 [2.5% -0.52, 97.5% +1.67]  P(alpha*>=obs) 0.6650  | null NW t mean +1.06 97.5% +2.99 (obs t +0.55)  | eps mean +0.023 sd 0.935 exkurt -0.0
    S2 sig21_d eps=iid: null alpha mean +0.46 sd 0.65 [2.5% -0.81, 97.5% +1.75]  P(alpha*>=obs) 0.5755  | null NW t mean +0.73 97.5% +2.66 (obs t +0.55)  | eps mean +0.000 sd 1.036 exkurt +8.3

- XAU out 2021-26H1: alpha_obs +1.77 (NW t +1.62)  | closed-form formula alpha_null +1.40 (c62 uses this: share 79%)
    S1 sig1_tgt eps=iid: null alpha mean +1.70 sd 1.08 [2.5% -0.28, 97.5% +3.90]  P(alpha*>=obs) 0.4505  | null NW t mean +1.45 97.5% +3.27 (obs t +1.62)  | eps mean +0.038 sd 0.976 exkurt -0.1
    S2 sig21_d eps=iid: null alpha mean +1.59 sd 1.26 [2.5% -0.81, 97.5% +4.11]  P(alpha*>=obs) 0.4350  | null NW t mean +1.26 97.5% +2.98 (obs t +1.62)  | eps mean +0.006 sd 1.054 exkurt +1.7

- XAU recent 2024-26H1: alpha_obs +5.87 (NW t +2.82)  | closed-form formula alpha_null +3.70 (c62 uses this: share 63%)
    S1 sig1_tgt eps=iid: null alpha mean +4.63 sd 2.22 [2.5% +0.53, 97.5% +9.27]  P(alpha*>=obs) 0.2870  | null NW t mean +2.13 97.5% +3.86 (obs t +2.82)  | eps mean +0.077 sd 1.011 exkurt -0.3
    S1 sig1_tgt eps=block: null alpha mean +4.68 sd 2.18 [2.5% +0.73, 97.5% +9.23]  P(alpha*>=obs) 0.2810  | null NW t mean +2.19 97.5% +3.89 (obs t +2.82)  | eps mean +0.077 sd 1.011 exkurt -0.3
    S1 sig1_tgt eps=normal: null alpha mean +3.21 sd 2.09 [2.5% -0.92, 97.5% +7.39]  P(alpha*>=obs) 0.1045  | null NW t mean +1.53 97.5% +3.37 (obs t +2.82)  | eps mean +0.077 sd 1.011 exkurt -0.3
    S2 sig21_d eps=iid: null alpha mean +4.54 sd 2.70 [2.5% -0.51, 97.5% +10.29]  P(alpha*>=obs) 0.2975  | null NW t mean +1.69 97.5% +3.49 (obs t +2.82)  | eps mean +0.025 sd 1.102 exkurt +1.8
    S2 sig21_d eps=block: null alpha mean +4.61 sd 2.69 [2.5% -0.24, 97.5% +10.43]  P(alpha*>=obs) 0.3080  | null NW t mean +1.74 97.5% +3.45 (obs t +2.82)  | eps mean +0.025 sd 1.102 exkurt +1.8
    S2 sig21_d eps=normal: null alpha mean +3.99 sd 2.37 [2.5% -0.54, 97.5% +8.66]  P(alpha*>=obs) 0.2055  | null NW t mean +1.61 97.5% +3.35 (obs t +2.82)  | eps mean +0.025 sd 1.102 exkurt +1.8

- XAU 2025: alpha_obs +5.21 (NW t +2.50)  | closed-form formula alpha_null +3.41 (c62 uses this: share 66%)
    S1 sig1_tgt eps=iid: null alpha mean +3.07 sd 1.93 [2.5% -0.58, 97.5% +6.93]  P(alpha*>=obs) 0.1365  | null NW t mean +1.56 97.5% +3.63 (obs t +2.50)  | eps mean +0.069 sd 1.002 exkurt -0.3
    S2 sig21_d eps=iid: null alpha mean +3.66 sd 2.57 [2.5% -1.10, 97.5% +8.83]  P(alpha*>=obs) 0.2675  | null NW t mean +1.52 97.5% +3.28 (obs t +2.50)  | eps mean +0.020 sd 1.083 exkurt +1.5

- XAU 2013: alpha_obs -4.18 (NW t -1.80)  | closed-form formula alpha_null -2.04 (c62 uses this: share 49%)
    S1 sig1_tgt eps=iid: null alpha mean -1.20 sd 2.17 [2.5% -5.27, 97.5% +3.14]  P(alpha*>=obs) 0.9215  | null NW t mean -0.64 97.5% +1.49 (obs t -1.80)  | eps mean +0.033 sd 0.991 exkurt -0.3
    S2 sig21_d eps=iid: null alpha mean -2.77 sd 2.39 [2.5% -7.30, 97.5% +1.91]  P(alpha*>=obs) 0.7260  | null NW t mean -1.17 97.5% +0.94 (obs t -1.80)  | eps mean -0.042 sd 1.333 exkurt +24.2

## T1b formula-vs-calibrated (R1a: is the closed form a usable estimate of the mechanical term?)
- XAU in 2010-20: formula +0.43 vs calibrated S1 +0.57 (sd 0.56) -> diff -0.14 = -0.25 null sd
- XAU out 2021-26H1: formula +1.40 vs calibrated S1 +1.70 (sd 1.08) -> diff -0.31 = -0.28 null sd
- XAU recent 2024-26H1: formula +3.70 vs calibrated S1 +4.63 (sd 2.22) -> diff -0.93 = -0.42 null sd
- XAU 2025: formula +3.41 vs calibrated S1 +3.07 (sd 1.93) -> diff +0.34 = +0.18 null sd
- XAU 2013: formula -2.04 vs calibrated S1 -1.20 (sd 2.17) -> diff -0.84 = -0.39 null sd

## T2 episode fragility of the recent cell
- recent minus 2025: n 386  mu +4.30  alpha +4.84  se 3.04  NW t +1.59
- recent minus 2024: n 382  mu +11.08  alpha +8.36  se 2.75  NW t +3.04
- recent minus 2026: n 514  mu +14.38  alpha +2.66  se 1.38  NW t +1.93
- leave-one-month-out (30 months): alpha min +4.93 (drop 202403, t +2.52)  max +6.91 (drop 202411)  median +5.89  n(t<2) 0/30  n(t<1) 0
- winsorise r at +/-3sd (8 days clipped): alpha +5.07  NW t +2.71
- drop 10 largest |r| days: n 631  alpha +3.42  NW t +1.95

## T3 cost and leverage (A3: 'cost is not the barrier, 0.05 bp/d')
- implied weight w = c/sig21: mean 1.199  median 1.278  p95 1.716  max 2.064  (c62/c58b claimed w_bar 1.1-1.2, w_max ~2)
- mean|dw| 0.0200/d  p95 0.0655  (c58b claimed 0.017-0.020)
- spread cost at 1x (c58b) round trip 5.3 bp: 0.106 bp/d -> alpha_net +5.76 (98% of alpha)
- spread cost at 2x round trip 10.6 bp: 0.212 bp/d -> alpha_net +5.65 (96% of alpha)
- spread cost at 10x round trip 53.0 bp: 1.062 bp/d -> alpha_net +4.80 (82% of alpha)
- mean excess exposure max(w-1,0) = 0.285 of notional
- financing at 2%/yr on the excess: 0.226 bp/d -> alpha_net +5.64  NW t_net ~+2.71
- financing at 5%/yr on the excess: 0.566 bp/d -> alpha_net +5.30  NW t_net ~+2.55
- financing at 7%/yr on the excess: 0.793 bp/d -> alpha_net +5.07  NW t_net ~+2.44
- financing at 10%/yr on the excess: 1.132 bp/d -> alpha_net +4.73  NW t_net ~+2.28
- financing at 15%/yr on the excess: 1.699 bp/d -> alpha_net +4.17  NW t_net ~+2.01
- BREAK-EVEN financing f* (alpha_net=0): 51.8%/yr   | f that pushes NW t below 2: 15.1%/yr
- leverage-capped w'=min(w,1) (de-risk only, no borrowing): alpha +2.41  se 1.01  NW t +2.39  (41% of +5.87)

## T4 in-sample scaling constant c (A4: the '+14.8%/yr' magnitude)
- causal c (expanding, all history up to d-1): c mean 93.6 (in-sample c 120.7)  alpha +4.32 bp/d (+10.89%/yr)  NW t +2.75  n 641
- c frozen at the in-sample-window value 94.7: alpha +4.60 bp/d (+11.59%/yr)  NW t +2.82
- note: t is invariant to c by construction (alpha and se scale together) -- the look-ahead affects the ECONOMIC MAGNITUDE claim only, not significance

## T5 cross-asset placebo (A5 'trend-sign artefact' should generalise to other up-trending assets)
- US500: valid sessions 3264  2012-01-16..2026-06-09
  - US500 in 2014-20: n 1716 mu +4.13  alpha_obs +0.58 (NW t +0.37)  formula +2.93  | calibrated S1 null mean +5.11 sd 2.09 97.5% +9.13  P(>=obs) 0.9960  excess -4.53 = -2.17 sd
  - US500 out 2021-26H1: n 1384 mu +4.88  alpha_obs +0.29 (NW t +0.30)  formula +1.62  | calibrated S1 null mean +2.55 sd 1.16 97.5% +4.95  P(>=obs) 0.9760  excess -2.26 = -1.94 sd
  - US500 recent 2024-26H1: n 628 mu +6.95  alpha_obs +0.31 (NW t +0.21)  formula +2.59  | calibrated S1 null mean +3.29 sd 1.95 97.5% +7.55  P(>=obs) 0.9520  excess -2.98 = -1.53 sd
    formula-vs-calibrated: +2.59 vs +3.29 -> -0.36 null sd
  - US500 yearly: Spearman(alpha_y, r_bar_y) +0.18 (p 0.566)  sign agreement 4/13  alpha>0 3/13
- US100: valid sessions 3338  2013-03-06..2026-06-30
  - US100 in 2014-20: n 1785 mu +7.16  alpha_obs +1.16 (NW t +0.80)  formula +3.66  | calibrated S1 null mean +5.75 sd 1.60 97.5% +9.23  P(>=obs) 0.9995  excess -4.59 = -2.86 sd
  - US100 out 2021-26H1: n 1416 mu +6.02  alpha_obs +1.08 (NW t +0.91)  formula +1.63  | calibrated S1 null mean +2.64 sd 1.32 97.5% +5.30  P(>=obs) 0.8890  excess -1.56 = -1.19 sd
  - US100 recent 2024-26H1: n 644 mu +9.10  alpha_obs +0.27 (NW t +0.17)  formula +2.50  | calibrated S1 null mean +3.22 sd 2.08 97.5% +7.76  P(>=obs) 0.9345  excess -2.95 = -1.42 sd
    formula-vs-calibrated: +2.50 vs +3.22 -> -0.35 null sd
  - US100 yearly: Spearman(alpha_y, r_bar_y) +0.47 (p 0.103)  sign agreement 3/13  alpha>0 3/13
- XAU yearly (c62 reported +0.82): Spearman(alpha_y, r_bar_y) +0.82 (p 0.000)  sign agreement 14/17

## T6 multiple testing (12 pre-registered alpha cells in c58: 4 estimators x 3 windows)
- calibrated one-sided p for the recent cell: 0.2870  -> Bonferroni(12) 1.0000  (threshold 0.025/12 = 0.00208)
- observed NW t on the common mask: VM21 +2.82  VM1 +2.69
- max-t over the 2 vol estimators (VM21, VM1) under the calibrated null, 500 reps: null max-t 97.5% +3.91  mean +2.48  | observed max-t +2.82  family-wise P 0.3340

- time 15.1s  seed 20261123  no network  no scan  no MT5  no order  writes: data/refute_c62_volmanaged.md only
