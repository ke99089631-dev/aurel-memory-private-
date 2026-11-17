# -*- coding: utf-8 -*-
"""
[REFUTE c45 補足 b / 2026-11-17 15:55] 本体 refute_c45_schedvsjump.py で **BREAK-A が当たった**
（公表足がジャンプでない発表 ANN_NJ +0.588 t 3.08 ＞ ジャンプした発表 ANN_J +0.407 t 2.43）ことの帰結を詰める。
**事後（supplementary）＝本体の BREAK 判定を上書きしない。** 読み方を決めるためだけに使う。
S1 ANN の |r(t0)| 四分位別 β（情報量の用量反応 ㊾ — ジャンプ条件づけ以前の連続版）。
S2 ANN_J / ANN_NJ を種別（NFP・FOMC）に分解（BREAK-A が片方の種別の人工物か）。
S3 ANN_J vs ANN_NJ を事象単位（1 発表 1 観測）で（本数の重複を外す）。
S4 c45 の H_SCHED 判定規則が雑音でどれだけ通るか（偽 UJ の帰無 sd 1.46 を使った解析的通過率 ＋ 偽 ANN 2000 回の同時通過率）。
データ・推定器・群定義は本体と同一。seed 20261117。出力 data/refute_c45_schedvsjump_b.md。
"""
import os, json, math, time
import numpy as np, pandas as pd
from scipy import stats as st

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c45_schedvsjump_b.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
ZMAIN = 5.0; W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]


def say(s=""):
    print(s, flush=True); L.append(s)


def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)


def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)


say("# [REFUTE c45 補足 b・事後] BREAK-A の帰結: 発表の優位はジャンプを要しない")
say("- **事後（supplementary）・本体の BREAK 判定は上書きしない**・seed 20261117")
say("")

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0)
t_nfp = t_nfp[np.isfinite(t_nfp)]; t_fomc = t_fomc[np.isfinite(t_fomc)]
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = (lo >= 0)
S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
nf3 = nf.copy()
for k in (1, 2, 3):
    nf3 &= np.r_[[False] * k, nf[:-k]]
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
cand = nf3 & trading & np.isfinite(sig)
z = np.abs(r) / sig


def decluster(mask):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= DECL:
            keep.append(i); last = ts[i]
    return np.array(keep, int)


J5 = decluster(cand & (z >= ZMAIN)); J4 = decluster(cand & (z >= 4.0))
isevbar = np.asarray(etdate.isin(evdays))
UJ5 = J5[(~isevbar[J5]) & (mn[J5] % 15 != 0)]


def bar_pos(tsec):
    key = np.asarray(tsec, dtype=np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    return pos, ts[pos] == key


p_n, g_n = bar_pos(t_nfp); p_f, g_f = bar_pos(t_fomc)
z_ann = np.r_[np.where(g_n, z[p_n], np.nan), np.where(g_f, z[p_f], np.nan)]
r_ann = np.r_[np.where(g_n, np.abs(r[p_n]), np.nan), np.where(g_f, np.abs(r[p_f]), np.nan)]
t_ann = np.r_[t_nfp, t_fomc]
kind = np.r_[np.full(len(t_nfp), "NFP"), np.full(len(t_fomc), "FOMC")]
ok_ann = np.r_[g_n, g_f]

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)
tsf = ts.astype(float)


def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(np.asarray(t0s, float)[np.isfinite(t0s)]) + off
    if len(t0s) == 0:
        return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]


mA, pA = inwin(t_ann)
tr["ANN"] = mA; tr["ann_t0"] = np.where(mA, pA, np.nan)
m_uj, q_uj = inwin(tsf[UJ5] + 300)
tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
tr["uj_t0"] = np.where(tr.UJ, q_uj - 300, np.nan)
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
# ann 属性を本に貼る
amap = pd.DataFrame({"ann_t0": t_ann, "z0": z_ann, "ar0": r_ann, "kind": kind})
amap = amap[np.isfinite(amap.ann_t0) & ok_ann].drop_duplicates("ann_t0")
tr = tr.merge(amap, on="ann_t0", how="left")


def ols_cluster(y, X, gcode, G):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    Xe = X * e[:, None]
    S = np.empty((G, X.shape[1]))
    for j in range(X.shape[1]):
        S[:, j] = np.bincount(gcode, weights=Xe[:, j], minlength=G)
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V


def fit(o, groups):
    cols = [np.ones(len(o))]; names = ["const"]
    for c in groups:
        cols.append(o[c].to_numpy(float)); names.append(c)
    hhv = o.hh.to_numpy()
    for h in range(1, 24):
        v = (hhv == h).astype(float)
        if v.sum() > 0:
            cols.append(v); names.append(f"h{h}")
    X = np.column_stack(cols); y = o.Rs.to_numpy(float)
    gc, uq = pd.factorize(o.day.to_numpy()); G = len(uq)
    beta, V = ols_cluster(y, X, gc, G)
    ix = {n: i for i, n in enumerate(names)}
    res = {c: (beta[ix[c]], math.sqrt(max(V[ix[c], ix[c]], 0)), int(o[c].sum())) for c in groups}
    return res, beta, V, ix, G


def contrast(beta, V, ix, spec):
    c = np.zeros(V.shape[0])
    for k, w in spec.items():
        c[ix[k]] = w
    val = float(c @ beta); se = math.sqrt(max(c @ V @ c, 0))
    return val, se, (val / se if se > 0 else float("nan"))


def fmt(t3):
    b, s, n = t3
    return f"{n}/{b:+.3f}({(b/s if s>0 else float('nan')):+.2f})"


def sub(lo_, hi_): return tr[(tr.year >= lo_) & (tr.year <= hi_)]


# ---------- S1 |r(t0)| 四分位 ----------
say("## S1 事後: ANN の公表足 |r(t0)| 四分位別 β（情報量の連続版用量反応 ㊾）")
say("| 窓 | Q1(小) n/β(t) | Q2 n/β(t) | Q3 n/β(t) | Q4(大) n/β(t) | Q1 の |r| 範囲 bp | Q4 の |r| 範囲 bp |")
say("|---|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_).copy()
    A = o[o.ANN & np.isfinite(o.ar0)]
    if len(A) < 40:
        say(f"| {lab} | n 不足 | | | | | |"); continue
    q = np.quantile(A.ar0.to_numpy(), [0.25, 0.5, 0.75])
    for i, nmq in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        loq = -np.inf if i == 0 else q[i - 1]; hiq = np.inf if i == 3 else q[i]
        o[nmq] = o.ANN & np.isfinite(o.ar0) & (o.ar0 > loq) & (o.ar0 <= hiq)
    sel = o[o.Q1 | o.Q2 | o.Q3 | o.Q4 | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["Q1", "Q2", "Q3", "Q4"])
    say(f"| {lab} | {fmt(res['Q1'])} | {fmt(res['Q2'])} | {fmt(res['Q3'])} | {fmt(res['Q4'])} | ≤{q[0]:.0f} | >{q[2]:.0f} |")
    if lab == "外 2021-26H1":
        dq = contrast(beta, V, ix, {"Q4": 1, "Q1": -1})
        say(f"- 外 Q4 − Q1 = {dq[0]:+.3f} (t {dq[2]:+.2f}) ＝ **公表足が大きいほど良いという用量反応の有無**")
say("")

# ---------- S2 種別分解 ----------
say("## S2 事後: ANN_J / ANN_NJ を種別（NFP・FOMC）に分解（BREAK-A が片方の人工物か）")
jump_ann = np.isfinite(z_ann) & (z_ann >= ZMAIN)
for nm, msk in (("NFP", kind == "NFP"), ("FOMC", kind == "FOMC")):
    say(f"- {nm}: ジャンプ {int((jump_ann & msk & ok_ann).sum())}/{int((msk & ok_ann).sum())}")
say("| 窓 | NFP_J n/β(t) | NFP_NJ n/β(t) | FOMC_J n/β(t) | FOMC_NJ n/β(t) |")
say("|---|---|---|---|---|")
sets = {
    "NFP_J": t_ann[ok_ann & jump_ann & (kind == "NFP")],
    "NFP_NJ": t_ann[ok_ann & ~jump_ann & (kind == "NFP")],
    "FOMC_J": t_ann[ok_ann & jump_ann & (kind == "FOMC")],
    "FOMC_NJ": t_ann[ok_ann & ~jump_ann & (kind == "FOMC")],
}
for k_, v_ in sets.items():
    m_, _ = inwin(v_, off=300.0); tr[k_] = m_
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    sel = o[o.NFP_J | o.NFP_NJ | o.FOMC_J | o.FOMC_NJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["NFP_J", "NFP_NJ", "FOMC_J", "FOMC_NJ"])
    say(f"| {lab} | {fmt(res['NFP_J'])} | {fmt(res['NFP_NJ'])} | {fmt(res['FOMC_J'])} | {fmt(res['FOMC_NJ'])} |")
say("")

# ---------- S3 事象単位 ----------
say("## S3 事後: ANN_J vs ANN_NJ を事象単位（1 発表 1 観測・本数の重複を外す）")
o = sub(2021, 2026)
A = o[o.ANN].copy()
A["isJ"] = A.z0 >= ZMAIN
gj = A[A.isJ].groupby("ann_t0").Rs.mean(); gn = A[~A.isJ].groupby("ann_t0").Rs.mean()
U = o[o.UJ].groupby("uj_t0").Rs.mean()
say(f"- 外: ANN_J 事象 {len(gj)}（平均 {gj.mean():+.3f}・中央値 {gj.median():+.3f}）／ANN_NJ 事象 {len(gn)}（平均 {gn.mean():+.3f}・中央値 {gn.median():+.3f}）／UJ 事象 {len(U)}（平均 {U.mean():+.3f}・中央値 {U.median():+.3f}）")
for nm, g in (("ANN_J", gj), ("ANN_NJ", gn)):
    dm = g.mean() - U.mean(); se = math.sqrt(g.var(ddof=1) / len(g) + U.var(ddof=1) / len(U))
    mw = st.mannwhitneyu(g.to_numpy(), U.to_numpy(), alternative="greater")
    say(f"- {nm} − UJ（事象単位）= {dm:+.3f} (Welch t {dm/se:+.2f})・MWU 片側 p {mw.pvalue:.4f}")
dm = gn.mean() - gj.mean(); se = math.sqrt(gn.var(ddof=1) / len(gn) + gj.var(ddof=1) / len(gj))
mw = st.mannwhitneyu(gn.to_numpy(), gj.to_numpy(), alternative="two-sided")
say(f"- **ANN_NJ − ANN_J（事象単位）= {dm:+.3f} (Welch t {dm/se:+.2f})・MWU 両側 p {mw.pvalue:.4f}** ＝ジャンプの有無で差があるか")
say("")

# ---------- S4 判定規則の通過率 ----------
say("## S4 事後: c45 の H_SCHED 判定規則（|t_UJ|<1.5 ∧ t(ANN−UJ)≥2）は雑音でどれだけ通るか")
sd_uj = 1.46  # 本体 R5b の偽 UJ 8 セルから実測
p_leg1 = 2 * st.norm.cdf(1.5 / sd_uj) - 1
say(f"- 本体 R5b: 偽 UJ（±7/14/21/28 日）の t の実測 sd **{sd_uj:.2f}**（名目 1 ではない）。")
say(f"- ⇒ 「UJ は null（|t|<1.5）」という第 1 の脚は、**真の効果が 0 の雑音腕でも通過確率 {p_leg1*100:.0f}%**（N(0,{sd_uj}) で |t|<1.5）。")
say(f"  名目 sd 1 なら 86.6%・sd 1.46 で {p_leg1*100:.0f}% ＝どちらにしても **非棄却を『固有性』の証拠に使えない**。")
say("- 第 2 の脚 t(ANN−UJ)≥2 は本体 R5 の偽 ANN 2000 回で経験 p 0.0000（max +2.55 < 実測 +2.82）＝こちらは校正済みで情報がある。")
say("- ⇒ H_SCHED 判定規則は「情報のある 1 脚（差）」と「ほぼ自動で通る 1 脚（UJ の非有意）」の合成で、"
    "**「予定公表に固有」という機構の主張を支えられるのは差の脚だけ**。差の脚は BREAK-A2（対称化すると t 1.74）で弱まる。")
say("")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
