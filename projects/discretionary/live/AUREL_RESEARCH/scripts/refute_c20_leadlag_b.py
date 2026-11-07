# -*- coding: utf-8 -*-
"""
[REFUTE c20 事後フォロー b] refute_c20_leadlag.py の B1 が発火（外 14:35 ET k=−1 ρ +22% t8.4・在 +7.6% t3.5）。
判定規則は変えない。発火セルの**性質**を記述で分解する（結果を見た後に書いた＝事後と明記）:
  F1 分布: Pearson／Spearman／winsor(±3)・上位 5% |x·y| 日の Σxy 寄与・上位 20 日の曜日分布（FOMC は水曜）。
  F2 ex-ante 代理（カレンダー不要）: 「声明足 14:00 の |z| ≥3（どちらかの系列）」の日を除いた ρ。
  F3 FOMC 日付リスト（私の記憶・**未検証**・補助）: FOMC 日 vs 非 FOMC 日の ρ と Σxy 寄与。
  F4 対称性・共通ドリフト: 同 slot の逆向き相互ラグ、各系列の slot 内自己相関 corr(x_s, x_{s+1})。
     純粋な先行遅行なら片側のみ正・自己相関 ≈0。共通の持続ドリフト（会見中の trend）なら両側正・自己相関 正。
  F5 経済的大きさ: β_raw bp/bp・1 sd 応答・上位 10% 条件 bp vs 半スプレッド（×1・×2）。
  F6 A2 の二値化（stale=0 vs >0）: 三分位の閾値が 0/0 に退化したため（事後・記述）。
入力同じ。seed 20261107
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c20_leadlag_b.md"); L = []
NY = "America/New_York"
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c20 b] 発火セルの分解 — {time.strftime('%Y-%m-%d %H:%M')}")

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); return zz["ts"].astype(np.int64), zz["close"].astype(float)
tsX, cX = load("XAU"); tsU, cU = load("US100"); tsS, cS = load("US500")
def join(tsA, cA, tsB, cB):
    com = np.intersect1d(tsA, tsB); return com, cA[np.searchsorted(tsA, com)], cB[np.searchsorted(tsB, com)]
def prep(ts, ca, cb):
    n = len(ts); consec = np.zeros(n, bool); consec[1:] = np.diff(ts) == 300
    ra = np.full(n, np.nan); rb = np.full(n, np.nan); ra[1:] = np.diff(np.log(ca)) * 1e4; rb[1:] = np.diff(np.log(cb)) * 1e4
    t = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    h = t.hour.to_numpy(); mn = t.minute.to_numpy(); wd = t.weekday.to_numpy(); yr = t.year.to_numpy()
    day = yr * 10000 + t.month.to_numpy() * 100 + t.day.to_numpy(); slot = h * 12 + mn // 5
    opn = ((wd <= 3) & (h != 17)) | ((wd == 4) & (h < 17)) | ((wd == 6) & (h >= 18))
    va = opn & consec & np.isfinite(ra) & (ra != 0); vb = opn & consec & np.isfinite(rb) & (rb != 0)
    def std(r, v):
        z = np.full(n, np.nan); key = (yr - yr.min()) * 288 + slot
        s2 = np.bincount(key[v], weights=r[v] ** 2, minlength=key.max() + 1); s1 = np.bincount(key[v], weights=r[v], minlength=key.max() + 1); c = np.bincount(key[v], minlength=key.max() + 1)
        var = np.where(c > 1, s2 / np.maximum(c, 1) - (s1 / np.maximum(c, 1)) ** 2, np.nan)
        ky = yr - yr.min(); ys2 = np.bincount(ky[v], weights=r[v] ** 2, minlength=ky.max() + 1); yc = np.bincount(ky[v], minlength=ky.max() + 1); yvar = ys2 / np.maximum(yc, 1)
        sd = np.sqrt(var[key]); bad = ~np.isfinite(sd) | (c[key] < 30); sd[bad] = np.sqrt(yvar[ky][bad]); z[v] = r[v] / sd[v]; return z
    za = std(ra, va); zb = std(rb, vb)
    idx = np.where(opn)[0]; fb = ((rb == 0) | ~np.isfinite(rb))[idx].astype(float); cs = np.concatenate([[0.0], np.cumsum(fb)])
    st = np.full(n, np.nan); pos = np.arange(len(idx)); ok = pos >= 24; st[idx[ok]] = (cs[pos[ok]] - cs[pos[ok] - 24]) / 24
    return dict(n=n, ts=ts, ra=ra, rb=rb, za=za, zb=zb, va=va, vb=vb, yr=yr, day=day, h=h, mn=mn, slot=slot, opn=opn, pa=ca, pb=cb, stale_b=st, wd=wd)
def shift(x, k):
    y = np.full_like(x, np.nan, dtype=float)
    if k > 0: y[k:] = x[:-k]
    elif k < 0: y[:k] = x[-k:]
    else: y = x.copy()
    return y
def corr_cl(x, y, day, W):
    m = W & np.isfinite(x) & np.isfinite(y)
    if m.sum() < 30: return np.nan, np.nan, int(m.sum())
    xx = x[m] - x[m].mean(); yy = y[m] - y[m].mean(); d = day[m]
    sxy = (xx * yy).sum(); syy = (yy * yy).sum(); sxx = (xx * xx).sum(); rho = sxy / math.sqrt(sxx * syy); beta = sxy / syy; e = xx - beta * yy
    _, inv = np.unique(d, return_inverse=True); g = np.bincount(inv, weights=yy * e); se = math.sqrt((g ** 2).sum()) / syy
    return rho, beta / se, int(m.sum())
def rho_t(x, y):
    m = np.isfinite(x) & np.isfinite(y); n = m.sum()
    if n < 30: return np.nan, np.nan, n
    r = np.corrcoef(x[m], y[m])[0, 1]; return r, r * math.sqrt(n - 2) / math.sqrt(max(1 - r * r, 1e-12)), n
def spearman(x, y):
    m = np.isfinite(x) & np.isfinite(y); return pd.Series(x[m]).corr(pd.Series(y[m]), method="spearman")
def wins(yr, lo, hi): return (yr >= lo) & (yr <= hi)

com, ca, cb = join(tsX, cX, tsU, cU); P = prep(com, ca, cb)
WIN = {"在 2012-20": wins(P["yr"], 2012, 2020), "外 2021-26H1": wins(P["yr"], 2021, 2026)}

# FOMC decision dates (from memory, UNVERIFIED — descriptive aid only; statement 14:00 ET from 2013, presser 14:30 ET)
FOMC = """2012-01-25 2012-03-13 2012-04-25 2012-06-20 2012-08-01 2012-09-13 2012-10-24 2012-12-12
2013-01-30 2013-03-20 2013-05-01 2013-06-19 2013-07-31 2013-09-18 2013-10-30 2013-12-18
2014-01-29 2014-03-19 2014-04-30 2014-06-18 2014-07-30 2014-09-17 2014-10-29 2014-12-17
2015-01-28 2015-03-18 2015-04-29 2015-06-17 2015-07-29 2015-09-17 2015-10-28 2015-12-16
2016-01-27 2016-03-16 2016-04-27 2016-06-15 2016-07-27 2016-09-21 2016-11-02 2016-12-14
2017-02-01 2017-03-15 2017-05-03 2017-06-14 2017-07-26 2017-09-20 2017-11-01 2017-12-13
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08 2018-12-19
2019-01-30 2019-03-20 2019-05-01 2019-06-19 2019-07-31 2019-09-18 2019-10-30 2019-12-11
2020-01-29 2020-03-03 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14
2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18
2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17""".split()
fomc_days = set(int(d.replace("-", "")) for d in FOMC)
is_fomc = np.isin(P["day"], list(fomc_days))

# per-day slot vectors: value of z at (day, slot)
def day_slot_vec(z, slot_idx, W):
    m = W & (P["slot"] == slot_idx) & np.isfinite(z)
    return dict(zip(P["day"][m], z[m]))
def pair(sidx, k, W, zx=None, zu=None):
    """x = z_XAU at slot sidx; y = z_US at slot sidx-k (k=+1: US previous bar; k=-1: US next bar). Returns days, x, y"""
    zx = P["za"] if zx is None else zx; zu = P["zb"] if zu is None else zu
    dx = day_slot_vec(zx, sidx, W); du = day_slot_vec(zu, sidx - k, W)
    days = np.array(sorted(set(dx) & set(du))); return days, np.array([dx[d] for d in days]), np.array([du[d] for d in days])
def statement_proxy(W):
    """days where |z| at 14:00 ET slot >= 3 in either series (ex-ante for 14:30+ cells)"""
    s = 14 * 12; dx = day_slot_vec(P["za"], s, W); du = day_slot_vec(P["zb"], s, W)
    return set(d for d, v in dx.items() if abs(v) >= 3) | set(d for d, v in du.items() if abs(v) >= 3)
WD = ["月", "火", "水", "木", "金", "土", "日"]
def wd_of(day):
    return pd.Timestamp(str(day)).weekday()

CELLS_OOS = [(14 * 12 + 7, -1), (14 * 12 + 8, 1), (14 * 12 + 6, -1), (14 * 12 + 0, -1), (18 * 12 + 2, -1), (18 * 12 + 6, -1), (22 * 12 + 2, 1), (15 * 12 + 0, 1)]
CELLS_IS = [(1 * 12 + 1, 1), (1 * 12 + 2, -1), (0 * 12 + 7, -1), (18 * 12 + 1, 1), (14 * 12 + 7, -1)]
hs_us = 0.813
def analyze(sidx, k, wl):
    W = WIN[wl]; hh, mm = divmod(sidx * 5, 60); lab = f"{hh:02d}:{mm:02d} ET k={k:+d}"
    days, x, y = pair(sidx, k, W); n = len(days)
    r, t, _ = rho_t(x, y); sp = spearman(x, y)
    xw = np.clip(x, -3, 3); yw = np.clip(y, -3, 3); rw, tw, _ = rho_t(xw, yw)
    xy = (x - x.mean()) * (y - y.mean()); order = np.argsort(-np.abs(xy)); top5 = order[: max(1, n // 20)]
    share5 = xy[top5].sum() / xy.sum() if xy.sum() != 0 else np.nan
    top20 = order[:20]; wds = [wd_of(days[i]) for i in top20]; nwed = sum(1 for w in wds if w == 2); nf = sum(1 for i in top20 if days[i] in fomc_days)
    # leave-top-5%-out rho
    keep = np.ones(n, bool); keep[top5] = False; r5, t5, _ = rho_t(x[keep], y[keep])
    # statement proxy exclusion
    prox = statement_proxy(W); mk = np.array([d not in prox for d in days]); rp, tp, npx = rho_t(x[mk], y[mk])
    # FOMC split
    mf = np.array([d in fomc_days for d in days]); rf, tf, nfo = rho_t(x[mf], y[mf]); rnf, tnf, nnf = rho_t(x[~mf], y[~mf])
    share_f = xy[mf].sum() / xy.sum() if xy.sum() != 0 else np.nan
    # symmetric counterpart and own autocorr at the slot pair
    s_lo, s_hi = (sidx, sidx + 1) if k == -1 else (sidx - 1, sidx)   # bars involved (lower, upper)
    _, xa, xb = pair(s_hi, 1, W, zx=P["za"], zu=P["za"]); rxx, txx, _ = rho_t(xa, xb)   # corr(XAU_hi, XAU_lo)
    _, ua, ub = pair(s_hi, 1, W, zx=P["zb"], zu=P["zb"]); ruu, tuu, _ = rho_t(ua, ub)   # corr(US_hi, US_lo)
    _, sx, sy = pair(s_hi if k == -1 else s_lo, -k, W); rsym, tsym, _ = rho_t(sx, sy)      # the other direction over same two slots
    # economic: raw bp
    dxr = day_slot_vec(P["ra"], sidx, W); dur = day_slot_vec(P["rb"], sidx - k, W); dd = np.array(sorted(set(dxr) & set(dur)))
    rx = np.array([dxr[d] for d in dd]); ru = np.array([dur[d] for d in dd])
    if k == -1:  # XAU leads: response of US next bar to XAU
        beta = (ru * rx).sum() / (rx * rx).sum(); resp = beta * rx.std(); big = np.abs(rx) >= np.quantile(np.abs(rx), 0.9); cond = (np.sign(rx[big]) * ru[big]).mean(); hs = hs_us; tgt = "US100"
        mkr = np.array([d not in prox for d in dd]); beta_x = (ru[mkr] * rx[mkr]).sum() / (rx[mkr] ** 2).sum(); resp_x = beta_x * rx[mkr].std()
    else:        # US leads: response of XAU next bar to US
        beta = (rx * ru).sum() / (ru * ru).sum(); resp = beta * ru.std(); big = np.abs(ru) >= np.quantile(np.abs(ru), 0.9); cond = (np.sign(ru[big]) * rx[big]).mean(); hs = 0.08 / np.median(P["pa"][W & P["va"]]) * 1e4; tgt = "XAU"
        mkr = np.array([d not in prox for d in dd]); beta_x = (rx[mkr] * ru[mkr]).sum() / (ru[mkr] ** 2).sum(); resp_x = beta_x * ru[mkr].std()
    say(f"### {wl} {lab} (n{n})")
    say(f"- F1 Pearson {r*100:+.1f}% (t{t:+.1f})・Spearman **{sp*100:+.1f}%**・winsor±3 {rw*100:+.1f}% (t{tw:+.1f})・上位 5% 日の Σxy 寄与 **{share5*100:.0f}%**・上位 5% 除外 ρ {r5*100:+.1f}% (t{t5:+.1f})・上位 20 日の水曜 {nwed}/20・FOMC リスト該当 {nf}/20")
    say(f"- F2 声明足 14:00 |z|≥3 の日（{len(prox)} 日）を除外: ρ **{rp*100:+.1f}% (t{tp:+.1f}, n{npx})**")
    say(f"- F3 FOMC 日 (n{nfo}) ρ {rf*100:+.1f}% (t{tf:+.1f})・Σxy 寄与 **{share_f*100:.0f}%**／非 FOMC 日 (n{nnf}) ρ **{rnf*100:+.1f}% (t{tnf:+.1f})**")
    say(f"- F4 逆向き同 2 足 ρ {rsym*100:+.1f}% (t{tsym:+.1f})・自己相関 XAU({divmod(s_lo*5,60)[0]:02d}:{divmod(s_lo*5,60)[1]:02d}→次) {rxx*100:+.1f}% (t{txx:+.1f})・US100 同 {ruu*100:+.1f}% (t{tuu:+.1f})")
    say(f"- F5 {tgt} 次足: β_raw {beta:+.4f} bp/bp・1 sd 応答 **{resp:+.3f} bp**・上位 10% 条件 {cond:+.3f} bp vs 半スプレッド {hs:.2f} bp（×2 {2*hs:.2f}）＝{abs(resp)/hs*100:.0f}%；声明日除外 1 sd 応答 {resp_x:+.3f} bp")
    return dict(r=r, rp=rp, rnf=rnf, share_f=share_f, sp=sp, rsym=rsym)

say("\n## 外 2021-26H1 の発火・上位セル")
RES = {}
for sidx, k in CELLS_OOS: RES[("外", sidx, k)] = analyze(sidx, k, "外 2021-26H1")
say("\n## 在 2012-20 の上位セル＋発火セルの在側")
for sidx, k in CELLS_IS: RES[("在", sidx, k)] = analyze(sidx, k, "在 2012-20")

# 14:00-15:00 ET slot-by-slot profile OOS: rho(+1), rho(-1), own autocorr both, FOMC vs non-FOMC for rho(-1)
say("\n## 14:00–15:00 ET の slot プロファイル（外）: ρ(−1)・ρ(+1)・自己相関・非 FOMC の ρ(−1)")
say("| slot | ρ(−1) XAU→US | ρ(+1) US→XAU | ρ1 XAU | ρ1 US100 | ρ(−1) 非FOMC | ρ(−1) 声明日除外 |"); say("|---|---|---|---|---|---|---|")
W = WIN["外 2021-26H1"]; prox = statement_proxy(W)
for sidx in range(14 * 12 - 2, 15 * 12 + 1):
    d1, x1, y1 = pair(sidx, -1, W); d2, x2, y2 = pair(sidx, 1, W)
    _, a1, a2 = pair(sidx + 1, 1, W, zx=P["za"], zu=P["za"]); _, b1, b2 = pair(sidx + 1, 1, W, zx=P["zb"], zu=P["zb"])
    mf = np.array([d in fomc_days for d in d1]); mp = np.array([d not in prox for d in d1])
    hh, mm = divmod(sidx * 5, 60)
    say(f"| {hh:02d}:{mm:02d} | {rho_t(x1,y1)[0]*100:+.1f}% (t{rho_t(x1,y1)[1]:+.1f}) | {rho_t(x2,y2)[0]*100:+.1f}% (t{rho_t(x2,y2)[1]:+.1f}) | {rho_t(a1,a2)[0]*100:+.1f}% | {rho_t(b1,b2)[0]*100:+.1f}% | {rho_t(x1[~mf],y1[~mf])[0]*100:+.1f}% (t{rho_t(x1[~mf],y1[~mf])[1]:+.1f}) | {rho_t(x1[mp],y1[mp])[0]*100:+.1f}% (t{rho_t(x1[mp],y1[mp])[1]:+.1f}) |")

# FOMC-day event study: mean |z| by slot 13:55-15:00 for both series, FOMC vs non-FOMC (OOS)
say("\n## FOMC 日の |z| プロファイル（外・13:55–15:00・平均 |z|）: FOMC 日／非 FOMC 日")
for lab, z in (("XAU", P["za"]), ("US100", P["zb"])):
    row = []
    for sidx in range(14 * 12 - 1, 15 * 12 + 1):
        m = W & (P["slot"] == sidx) & np.isfinite(z); f = is_fomc[m]; v = np.abs(z[m])
        row.append(f"{divmod(sidx*5,60)[0]:02d}:{divmod(sidx*5,60)[1]:02d} {v[f].mean():.1f}/{v[~f].mean():.1f}")
    say(f"- {lab}: " + "・".join(row))

# Re-run family-wise max|t| test excluding FOMC-list days and statement-proxy days (descriptive: does any cell survive?)
say("\n## 576 セル再掃引（外・記述）: (a) FOMC リスト日除外 (b) 声明足代理日除外 — 上位 5 セル（t=ρ√(n−2)）")
def slot_rhos(x, y, Wm, slot, nslot=288):
    m = Wm & np.isfinite(x) & np.isfinite(y); k = slot[m]; xx = x[m]; yy = y[m]
    n = np.bincount(k, minlength=nslot).astype(float); sx = np.bincount(k, weights=xx, minlength=nslot); sy = np.bincount(k, weights=yy, minlength=nslot)
    sxy = np.bincount(k, weights=xx * yy, minlength=nslot); sxx = np.bincount(k, weights=xx * xx, minlength=nslot); syy = np.bincount(k, weights=yy * yy, minlength=nslot)
    with np.errstate(invalid="ignore", divide="ignore"):
        rho = (sxy / n - (sx / n) * (sy / n)) / np.sqrt((sxx / n - (sx / n) ** 2) * (syy / n - (sy / n) ** 2)); rho[n < 200] = np.nan
        t = rho * np.sqrt(np.maximum(n - 2, 1)) / np.sqrt(np.maximum(1 - rho ** 2, 1e-12))
    return rho, t, n
prox_arr = np.isin(P["day"], list(prox))
for lab, excl in (("(a) FOMC リスト日除外", is_fomc), ("(b) 声明足代理日除外", prox_arr), ("(a)+(b)", is_fomc | prox_arr)):
    Wm = W & ~excl; cells = []
    for k in (1, -1):
        r, t, n = slot_rhos(P["za"], shift(P["zb"], k), Wm, P["slot"])
        for s in range(288):
            if np.isfinite(t[s]): cells.append((abs(t[s]), k, s, r[s], t[s], n[s]))
    cells.sort(reverse=True)
    say(f"- {lab}（除外 {np.unique(P['day'][W & excl]).size} 日）: " + "・".join(f"{divmod(s*5,60)[0]:02d}:{divmod(s*5,60)[1]:02d} k={k:+d} ρ{r*100:+.1f}% t{t:+.1f} (n{int(n)})" for a, k, s, r, t, n in cells[:5]) + f"・|t|≥4.14（元の 95% 点）のセル数 {sum(1 for c in cells if c[0] >= 4.14)}")

# F6: A2 binary split
say("\n## F6 A2 二値化: US100 ex-ante stale 率（直前 24 取引足）= 0 vs > 0 の ρ(−1)")
for wl, Wm in WIN.items():
    zbm1 = shift(P["zb"], -1)
    for tl, T in (("stale=0", P["stale_b"] == 0), ("stale>0", P["stale_b"] > 0)):
        r, t, n = corr_cl(P["za"], zbm1, P["day"], Wm & T); say(f"- {wl} {tl}: ρ(−1) {r*100:+.3f}% (t{t:+.2f}, n{n})")
Wp = wins(P["yr"], 2012, 2026); zbm1 = shift(P["zb"], -1)
r0, t0, n0 = corr_cl(P["za"], zbm1, P["day"], Wp & (P["stale_b"] == 0)); r1, t1, n1 = corr_cl(P["za"], zbm1, P["day"], Wp & (P["stale_b"] > 0))
say(f"- プール: stale=0 {r0*100:+.3f}% (t{t0:+.2f}, n{n0})／stale>0 {r1*100:+.3f}% (t{t1:+.2f}, n{n1}) → 比 {r1/r0:.2f}＝{'一様（stale 機構は不支持）' if abs(r1/r0) < 2 and np.sign(r1)==np.sign(r0) else '不一様'}")
# pooled rho(-1) excluding FOMC & 14:30-14:45 cells: is the weak signal driven by the fired cell?
m_ex = Wp & ~is_fomc & ~((P["h"] == 14) & (P["mn"] >= 30))
r, t, n = corr_cl(P["za"], zbm1, P["day"], m_ex); say(f"- プール ρ(−1) から FOMC 日と 14:30–14:55 slot を除外: {r*100:+.3f}% (t{t:+.2f}, n{n})（元 +0.305% t1.98）")
r, t, n = corr_cl(P["za"], zbm1, P["day"], Wp & ~((P["h"] == 14) & (P["mn"] >= 30))); say(f"- プール ρ(−1) から 14:30–14:55 slot のみ除外: {r*100:+.3f}% (t{t:+.2f}, n{n})")

say(f"\n実行 {time.time()-T0:.1f} s・入力 3 npz のみ・scan 無し・MT5 無し・外部通信無し。FOMC 日付リストは記憶由来・未検証（needs data: 公式カレンダー）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
