# -*- coding: utf-8 -*-
"""
[cycle69b 研究レーン 2026-11-25・事後] c69 の最重大反証を数字で: 「米国祝日の負の ρ1 は“薄い日”固有か、それとも単に“静かな日”一般の性質か」。
c69 第 1 走を見てから書いた（事後・判定には使わない・記述）。通常平日（非 HOL・非事象）の TW 08:00→13:00 ET の RV を期間内 5 分位に切り、
分位ごとの群 ρ1（Σa/Σb）・ρ1_15・VR6・π を印字。祝日群（RV 中央値 ≈ 0.21×）が同じ RV 水準の通常日と同じ ρ1 なら「低ボラ一般（LeBaron 1992 型）」、
祝日の方がさらに負なら「参加者欠落に固有」。加えて log RV を連続説明変数にした日次回帰 ρ1_d（日内 59 対の自己相関）~ log RV_d ＋ 1{THIN} で
祝日ダミーの係数を印字（HC1 t）。同じ関数・同じ暦・同じ窓（c69 から import せず複製・決定論）。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c69b_lowvol_days_rho.md"); L = []
NY = "America/New_York"; rng = np.random.default_rng(20261125); NB = 1000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle69b・事後] 静かな通常日 vs 米国祝日: RV 分位別の ρ1（TW 08:00→13:00 ET・金 bid M5）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c69b_lowvol_days_rho.py)")
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)) * 1e4
def epoch_et(dates, hour, minute, day_offset=0):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n): d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m + 1, 1) - dt.timedelta(days=1); return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d
THIN, OTHER = set(), set()
for y in range(2010, 2027):
    THIN |= {nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3), last_weekday(y, 5, 0), observed(dt.date(y, 7, 4)), nth_weekday(y, 9, 0, 1), nth_weekday(y, 11, 3, 4)}
    if y >= 2022: THIN.add(observed(dt.date(y, 6, 19)))
    for h in (observed(dt.date(y, 1, 1), sat_to_fri=False), easter(y) - dt.timedelta(days=2), observed(dt.date(y, 12, 25)), nth_weekday(y, 10, 0, 2), observed(dt.date(y, 11, 11)), nth_weekday(y, 11, 3, 4) + dt.timedelta(days=1), dt.date(y, 7, 3), dt.date(y, 12, 24)):
        if h is not None: OTHER.add(h)
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
EV = set(d.date() for d in nfp_dates_v2()) | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")).date).dt.date) | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date).dt.date)
dates = pd.date_range("2010-01-04", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]; N = len(dates); ddate = np.array([d.date() for d in dates]); yr = dates.year.to_numpy()
T0_ = epoch_et(dates, 8, 0); nb = 60; M = np.full((N, nb), np.nan); ok = np.isfinite(T0_)
i0 = np.clip(np.searchsorted(ts, T0_[ok].astype(np.int64)), 0, len(ts) - nb); good = (ts[i0] == T0_[ok].astype(np.int64)) & (ts[i0 + nb - 1] == T0_[ok].astype(np.int64) + (nb - 1) * 300)
M[np.where(ok)[0][good]] = r[i0[good][:, None] + np.arange(nb)[None, :]]
is_thin = np.array([d in THIN for d in ddate]); is_other = np.array([d in OTHER for d in ddate]); is_ev = np.array([d in EV for d in ddate])
full = np.isfinite(M).all(1); nfw = np.where(full, np.mean(M != 0, axis=1), np.nan); elig = full & (nfw >= 0.5) & ~is_ev
a = np.nansum(M[:, 1:] * M[:, :-1], 1); b = np.nansum(M[:, 1:] ** 2, 1); rv = np.nansum(M ** 2, 1)
X3 = M[:, :60].reshape(N, 20, 3).sum(2); a15 = np.sum(X3[:, 1:] * X3[:, :-1], 1); b15 = np.sum(X3[:, 1:] ** 2, 1)
X6 = M.reshape(N, 10, 6).sum(2); v30 = np.sum(X6 ** 2, 1)
prev, nxt = M[:, :-1], M[:, 1:]; mk = prev != 0; pi = np.where(mk.sum(1) > 0, np.sum(np.where(mk, -np.sign(prev) * nxt, 0), 1) / np.maximum(mk.sum(1), 1), np.nan)
rho_d = np.where(b > 0, a / np.maximum(b, 1e-12), np.nan)
def grp(idx):
    return a[idx].sum() / b[idx].sum(), a15[idx].sum() / b15[idx].sum(), (v30[idx].mean() / 10) / (6 * rv[idx].mean() / 60), np.nanmean(pi[idx]), np.median(rv[idx])
def boot_se(idx):
    out = np.array([grp(idx[rng.integers(0, len(idx), len(idx))])[0] for _ in range(NB)]); return out.std(ddof=1)
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
for lab, lo, hi in ERAS:
    era = (yr >= lo) & (yr <= hi) & elig; norm = np.where(era & ~is_thin & ~is_other)[0]; thin = np.where(era & is_thin)[0]
    q = np.quantile(rv[norm], [0.2, 0.4, 0.6, 0.8]); bins = np.digitize(rv[norm], q)
    say(f"\n## {lab}: 通常平日 {len(norm)} 日（TW RV 5 分位）vs THIN {len(thin)} 日")
    say("| 群 | n 日 | RV 中央値 (bp²) | RV 比 vs 通常全体 | ρ1 (boot se) | ρ1_15 分 | VR6 | π bp/本 |"); say("|---|---|---|---|---|---|---|---|")
    rv_all = np.median(rv[norm])
    for k in range(5):
        idx = norm[bins == k]; g = grp(idx); say(f"| 通常 Q{k+1}{'（最も静か）' if k==0 else ''} | {len(idx)} | {g[4]:.0f} | {g[4]/rv_all:.2f} | {g[0]:+.3f} ({boot_se(idx):.3f}) | {g[1]:+.3f} | {g[2]:.3f} | {g[3]:+.3f} |")
    # Q1 の中でさらに下半分（祝日の RV 水準に近づける）
    q1 = norm[bins == 0]; lowhalf = q1[rv[q1] <= np.median(rv[q1])]; g = grp(lowhalf); say(f"| 通常 Q1 の下半分（最も祝日に近い水準） | {len(lowhalf)} | {g[4]:.0f} | {g[4]/rv_all:.2f} | {g[0]:+.3f} ({boot_se(lowhalf):.3f}) | {g[1]:+.3f} | {g[2]:.3f} | {g[3]:+.3f} |")
    g = grp(thin); se_t = boot_se(thin); say(f"| **THIN 祝日** | {len(thin)} | {g[4]:.0f} | {g[4]/rv_all:.2f} | **{g[0]:+.3f} ({se_t:.3f})** | {g[1]:+.3f} | {g[2]:.3f} | {g[3]:+.3f} |")
    # 一致 RV 対照: 各祝日に RV が最も近い通常日 4 本（同期間）
    near = []
    for i in thin:
        o = np.argsort(np.abs(np.log(rv[norm]) - np.log(rv[i])))[:4]; near.extend(norm[o].tolist())
    near = np.array(sorted(set(near))); gn = grp(near); se_n = boot_se(near)
    D = g[0] - gn[0]; se_D = math.sqrt(se_t ** 2 + se_n ** 2)
    say(f"| 通常・RV 一致対照（祝日ごとに最近傍 4 日） | {len(near)} | {gn[4]:.0f} | {gn[4]/rv_all:.2f} | {gn[0]:+.3f} ({se_n:.3f}) | {gn[1]:+.3f} | {gn[2]:.3f} | {gn[3]:+.3f} |")
    say(f"- **祝日 − RV 一致通常日: D_ρ1 {D:+.3f} (z {D/se_D:+.2f})**・D_ρ1_15 {g[1]-gn[1]:+.3f}・D_VR6 {g[2]-gn[2]:+.3f}・D_π {g[3]-gn[3]:+.3f} bp/本")
    # 日次回帰 ρ1_d ~ log RV + THIN
    idx = np.r_[norm, thin]; y = rho_d[idx]; x1 = np.log(rv[idx]); x2 = is_thin[idx].astype(float); m = np.isfinite(y)
    Xm = np.c_[np.ones(m.sum()), x1[m] - x1[m].mean(), x2[m]]; yv = y[m]; beta = np.linalg.lstsq(Xm, yv, rcond=None)[0]; e = yv - Xm @ beta
    XtXi = np.linalg.inv(Xm.T @ Xm); V = XtXi @ (Xm.T * e ** 2) @ Xm @ XtXi * len(yv) / (len(yv) - 3); se = np.sqrt(np.diag(V))
    say(f"- 日次回帰 ρ1_d = α + β·log RV_d + γ·1{{THIN}}（HC1）: β {beta[1]:+.4f} (t {beta[1]/se[1]:+.2f}・RV 1 log 低下で ρ1 {-beta[1]:+.4f}) ／ **γ_THIN {beta[2]:+.4f} (t {beta[2]/se[2]:+.2f})**・n {len(yv)}・通常日 ρ1_d sd {np.nanstd(rho_d[norm]):.3f}")
say(f"\n_実行 {time.time()-T0:.1f} s_"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
