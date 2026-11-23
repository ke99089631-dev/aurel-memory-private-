# [REFUTE c62 supp c] drift-orthogonal test + unlevered form -- 2026-11-23 21:40 (scripts/refute_c62_volmanaged_c.py)

## C1 low-drift subsample: does the alpha follow the drift? (D1)
- recent 2024-26H1 (full): n 641  mu +10.36  alpha +5.87 (NW t +2.82)  null mean +3.27 sd 2.13 97.5% +7.56  excess +2.59 = +1.22 sd  P(null>=obs) 0.1095
- recent minus 2025: n 386  mu +4.30  alpha +4.84 (NW t +1.59)  null mean +1.71 sd 3.04 97.5% +7.30  excess +3.13 = +1.03 sd  P(null>=obs) 0.1590
- 2024 only: n 259  mu +9.30  alpha +1.02 (NW t +0.95)  null mean +0.34 sd 0.92 97.5% +2.17  excess +0.69 = +0.75 sd  P(null>=obs) 0.2210
- 2026H1 only: n 127  mu -5.89  alpha -0.48 (NW t -0.09)  null mean -0.52 sd 5.23 97.5% +9.69  excess +0.03 = +0.01 sd  P(null>=obs) 0.4940
- out 2021-26H1 minus 2025: n 1158  mu +2.15  alpha +1.15 (NW t +0.96)  null mean +0.50 sd 1.15 97.5% +2.72  excess +0.65 = +0.56 sd  P(null>=obs) 0.2790
- 2021-23 (flat-drift control): n 772  mu +1.08  alpha -0.10 (NW t -0.15)  null mean +0.05 sd 0.59 97.5% +1.19  excess -0.15 = -0.25 sd  P(null>=obs) 0.5925
- D1 check: mu +10.36 -> +4.30 (41% of drift retained); mechanical null +3.27 -> +1.71; excess +1.22 sd -> +1.03 sd

## C2 per-year excess over the calibrated null (XAU)  [structural null test, not an edge measurement -- D2]
| year | n | mu_y | alpha_y | NW t | null mean | null sd | excess | z |
| 2010 | 240 | +11.35 | +1.47 | +1.81 | +0.42 | 0.93 | +1.04 | +1.12 |
| 2011 | 259 | +3.79 | +3.22 | +1.25 | +0.76 | 2.55 | +2.45 | +0.96 |
| 2012 | 259 | +2.62 | -0.79 | -0.78 | +0.17 | 0.87 | -0.96 | -1.11 |
| 2013 | 245 | -13.43 | -4.18 | -1.80 | -1.50 | 2.22 | -2.68 | -1.20 |
| 2014 | 258 | -0.70 | -0.80 | -0.81 | -0.08 | 0.96 | -0.73 | -0.75 |
| 2015 | 258 | -4.25 | -0.93 | -1.26 | -0.05 | 0.67 | -0.88 | -1.31 |
| 2016 | 258 | +3.14 | +0.47 | +0.40 | +0.05 | 1.06 | +0.42 | +0.40 |
| 2017 | 257 | +4.84 | +0.03 | +0.05 | +0.10 | 0.45 | -0.08 | -0.17 |
| 2018 | 258 | -0.61 | +0.00 | +0.00 | +0.00 | 0.36 | -0.00 | -0.00 |
| 2019 | 258 | +6.52 | +0.97 | +0.80 | +0.94 | 1.15 | +0.03 | +0.02 |
| 2020 | 259 | +8.65 | +3.18 | +1.14 | +1.64 | 2.72 | +1.53 | +0.56 |
| 2021 | 258 | -1.43 | -0.15 | -0.18 | -0.04 | 0.73 | -0.11 | -0.15 |
| 2022 | 258 | -0.12 | -0.02 | -0.02 | -0.04 | 1.05 | +0.02 | +0.02 |
| 2023 | 256 | +4.82 | -0.62 | -0.52 | +0.20 | 0.87 | -0.82 | -0.95 |
| 2024 | 259 | +9.30 | +1.02 | +0.95 | +0.33 | 0.93 | +0.70 | +0.75 |
| 2025 | 255 | +19.54 | +5.21 | +2.50 | +2.48 | 1.96 | +2.73 | +1.39 |
| 2026 | 127 | -5.89 | -0.48 | -0.09 | -0.76 | 5.21 | +0.28 | +0.05 |
- Spearman(alpha_y, mu_y) +0.82 (p 0.000)  [c62 reported +0.82]
- Spearman(excess_y, mu_y) +0.67 (p 0.003)  <-- if the drift explains alpha, this must be ~0
- excess_y: mean +0.17 bp/d  median +0.02  positive 9/17  mean z -0.02  Stouffer z -0.09 (two-sided p 0.930)
- D2r verdict input: |rho(excess,mu)| 0.67 vs threshold 0.35; Stouffer |z| 0.09 vs threshold 2

## C3 tradeable unlevered form w' = min(w,1): de-risk only, no borrowing, no financing leg (D3)
- XAU recent uncapped (c58 estimator): w mean 1.199 max 2.064  alpha +5.87 (NW t +2.82)  null mean +3.13 sd 2.13 97.5% +7.42  excess +2.73 = +1.28 sd  P(null>=obs) 0.1025
- XAU recent cap w<=1.0: w mean 0.914 max 1.000  alpha +2.41 (NW t +2.39)  null mean +1.34 sd 1.14 97.5% +3.58  excess +1.07 = +0.94 sd  P(null>=obs) 0.1775
- XAU recent cap w<=1.2: w mean 1.037 max 1.200  alpha +3.66 (NW t +2.64)  null mean +2.03 sd 1.49 97.5% +4.99  excess +1.63 = +1.10 sd  P(null>=obs) 0.1425

## C4 equity placebo combined (does the drift explanation generalise? A5)
- US500 in 2014-20 ex2020: mu +3.66 (positive drift => A5 predicts alpha ~ mechanical +0.99)  alpha_obs -0.25  excess -1.25 = -1.51 sd
- US500 recent 2024-26H1: mu +6.95 (positive drift => A5 predicts alpha ~ mechanical +2.01)  alpha_obs +0.31  excess -1.71 = -1.00 sd
- US100 in 2014-20 ex2020: mu +5.83 (positive drift => A5 predicts alpha ~ mechanical +1.34)  alpha_obs +0.39  excess -0.95 = -0.97 sd
- US100 recent 2024-26H1: mu +9.10 (positive drift => A5 predicts alpha ~ mechanical +1.87)  alpha_obs +0.27  excess -1.60 = -0.83 sd
- combined equity Stouffer z -2.16 (two-sided p 0.031)  n cells 4  all negative: True
- A5 prediction for an up-trending asset: alpha_obs ~ mechanical term > 0. Equities show alpha_obs ~ 0 while the mechanical term is positive.

## C5 corrected multiple testing on the recent cell
- calibrated one-sided p 0.1115  (c58 permutation p was 0.022)  -> Bonferroni(12 pre-registered alpha cells) 1.000; threshold 0.025/12 = 0.00208 -> does NOT pass

- time 5.0s  seed 20261123  no network  no scan  no MT5  no order  writes: data/refute_c62_volmanaged_c.md only
