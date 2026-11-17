# -*- coding: utf-8 -*-
"""
[REFUTE / 2026-11-17 21:30 反証レーン・第 2 段] 第 1 段（refute_c46_cpi_clock.py）で当たった 3 本の決着と、
第 1 段が偶発的に出した 1 つの新事実の検定。

第 1 段の結果（数字は _b を書く前に確定済み）:
  ☠BREAK-DOW2  外 β_CPI_FRI +0.587 (t 1.53・**n 9 本**・MDE 0.769) ≥ 0.5·β_ANN ∧ t≥1.5 → 規則上は当たったが n 9。
  ☠BREAK-DIFFCAL 偽 CPI 400 回での t(β_ANN − β_偽CPI) の帰無は 外 **平均 +2.54・sd 0.84**、実測 +2.23 の片側 p 0.6375。
  ☠BREAK-VOL-B 曜日 × 当日実現ボラ五分位 一致の偽 CPI の β 平均 **+0.103**（c46 の曜日のみ一致版は +0.03〜0.04）。
  ★BREAK-DOW 不発（セル一致 β_ANN +0.533 t 3.86）・★BREAK-DOW3 不発（非発表の金午前 −0.035・水午後 +0.037）
    ＝**本反証の中心仮説 H_DOW は自分の検定で死んだ**。
  新事実（事前に予期していない・第 1 段 R2d）: **在 2010-20 の FOMC 窓は +0.320 (t 2.06・n 54)／セル一致 +0.362 (t 2.21)**。
    レーンは c44 以降ずっと「在 ANN は null（+0.053）」と書いてきたが、その null は 在 NFP 窓 −0.044 と 在 FOMC 窓 +0.320 の平均。

=== 第 2 段の事前固定（数字を見る前・この docstring が正本） ===
S1 **同等性検定を正しく書く（方法論 55）**: c46 の FAIL 規則 β_CPI + 2·se_CPI < 0.5·β_ANN は 0.5·β_ANN を**定数扱い**し
   Var(β_ANN) を無視している。クラスタ共分散から γ = β_CPI − 0.5·β_ANN の se を正しく取り t(γ) を出す。
   - **BREAK-TOST** = 外で t(γ) < −2（＝c46 の判定は inconclusive でなく **FAIL（NFP/FOMC 固有）**であるべきだった）。
S2 **在 FOMC 窓 +0.320 の検定**（第 1 段の新事実）: 偽 FOMC（在の非発表**水曜**から同数抽出し 14:00 ET に置く・NFAKE 回）で
   t(β_FOMCw) の帰無分布 → 実測の片側経験 p。あわせて 在 を 2010-15／2016-20 に割り、LOYO（2013-2020 の 8 年）も印字。
   - **BREAK-INSAMPLE** = 在 FOMC 窓の片側経験 p < 0.025 ∧ 2 分割の両方で β > 0
     （＝「ANN の優位は 2021+ レジーム固有」というレーンの D2 的な枠組みが崩れ、FOMC 午後窓は在でも立っていた）。
S3 **両腕に同一の帰無構成を当てる（方法論 54 の校正版・本第 2 段の中心）**: 第 1 段 R4 の
   「曜日 × 当日実現ボラ五分位 一致の非発表日」という偽集合の作り方を **ANN 腕にもそのまま当てる**。
   偽 ANN = 非発表**金曜**（ボラ五分位一致・NFP 件数）を 08:30 ＋ 非発表**水曜**（同・FOMC 件数）を 14:00 に置いた合成腕。
   → t(β_偽ANN) の帰無分布と実測 t(β_ANN)=4.01 の片側経験 p。CPI 側（第 1 段 p 0.235）と**同一構成**で並べる。
   - **BREAK-SYM** = 外で 実測 t(β_ANN) の片側経験 p > 0.025（＝ボラ・曜日・時刻を一致させた偽集合が β_ANN を再現する
     ＝反証 09:30 B5 の「ボラ説は死亡」は一致次元が粗かっただけ）。
survived（第 2 段）= BREAK-TOST／BREAK-INSAMPLE／BREAK-SYM がいずれも不発。
事前の自己反証: (i) S2 の在 FOMC は 54 本/在 FOMC 公表 ~63 回・事後に見つけた腕なので、経験 p が通っても
   「事後の腕を 1 本選んだ」分の多重性がある（在 ANN の分割は NFP/FOMC の 2 通りしかないので K=2 の補正を印字する）。
   (ii) S3 の偽 ANN は NFP が金曜・FOMC が水曜に固定されるためプールが小さく（在/外で 非発表金曜・水曜のみ）、
   抽出の重複が増える＝帰無分布が狭くなる方向のバイアス（＝BREAK-SYM が当たりやすくなる方向＝私に不利でなく有利）。
   (iii) 実現ボラ五分位は**当日**の RMS＝建玉時刻より後の情報を含む（look-ahead）。だが帰無集合の作り方に使うだけで
   処置腕の推定には使わないので、判定の look-ahead にはならない（c46 の R4 と同じ扱い・明記する）。
seed 20261117・NFAKE 400。出力 data/refute_c46_cpi_clock_b.md。読取専用・発注なし・本番編集なし。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c46_cpi_clock_b.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0; NFAKE = 400

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

say("# [REFUTE 2026-11-17 21:30 第2段] 同等性検定・在 FOMC 窓・両腕に同一帰無構成")
say(f"- 事前固定は docstring・seed {SEED}・NFAKE {NFAKE}・規則 BREAK-TOST／BREAK-INSAMPLE／BREAK-SYM")
say("")

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI_ALL = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
nfp_fomc_days = set(list(NFP.normalize()) + list(FOMC_ALL.normalize()))
CPI = pd.DatetimeIndex([d for d in CPI_ALL if d.normalize() not in nfp_fomc_days])
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0); t_cpi = epoch_et(CPI, 8, 30)
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI_ALL.normalize()))))

zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = (lo >= 0)
S2v = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2v / np.maximum(NN, 1), np.nan))
nf3 = nf.copy()
for k in (1, 2, 3):
    nf3 &= np.r_[[False] * k, nf[:-k]]
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
z = np.abs(r) / sig
cand = nf3 & trading & np.isfinite(sig)

def decluster(mask):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= DECL:
            keep.append(i); last = ts[i]
    return np.array(keep, int)

J4 = decluster(cand & (z >= 4.0))
dv = pd.DataFrame({"d": etdate[nf], "r2": r[nf] ** 2}).groupby("d").agg(rms=("r2", lambda x: math.sqrt(float(np.mean(x)))), n=("r2", "size"))
day_vol = dv[dv.n >= 100]["rms"]

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays); tr["cell"] = tr.wd * 24 + tr.hh

def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    if len(t0s) == 0: return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, _ = inwin(t_nfp); m_fomc, _ = inwin(t_fomc); m_cpi, _ = inwin(t_cpi)
tr["NFPw"] = m_nfp; tr["FOMCw"] = m_fomc & ~m_nfp
tr["ANN"] = m_nfp | m_fomc; tr["CPI"] = m_cpi & ~tr.ANN
m_any4, _ = inwin(ts.astype(float)[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    Xe = X * e[:, None]
    codes, uniq = pd.factorize(np.asarray(g))
    S = np.zeros((len(uniq), X.shape[1])); np.add.at(S, codes, Xe); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def fit(o, groups, fe="hour"):
    if fe == "hour":
        lv = sorted(set(o.hh.to_numpy().tolist())); M = o.hh.to_numpy()
    elif fe == "cell":
        lv = sorted(set(o.cell.to_numpy().tolist())); M = o.cell.to_numpy()
    else:
        lv = []; M = None
    cols = [np.ones(len(o)), np.column_stack([o[c].to_numpy().astype(float) for c in groups])]
    if len(lv) > 1:
        cols.append(np.column_stack([(M == v).astype(float) for v in lv[1:]]))
    X = np.column_stack(cols); y = o.Rs.to_numpy(float)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    res = {c: (beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(o[c].sum())) for i, c in enumerate(groups)}
    return res, V, G

def tstr(b, s): return f"{b:+.3f} ({(b/s if s and s>0 else float('nan')):+.2f})"
def sub(lo_, hi_): return tr[(tr.year >= lo_) & (tr.year <= hi_)]
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
alldays = pd.DatetimeIndex(sorted(set(etdate[(wd <= 4) & nf])))
nonev = alldays[~alldays.isin(evdays)]
nonev = nonev[nonev.isin(day_vol.index)]

# =====================================================================
say("## S1 BREAK-TOST: γ = β_CPI − 0.5·β_ANN を**クラスタ共分散で正しく**（c46 は 0.5·β_ANN を定数扱い）")
say("| 窓 | β_ANN | β_CPI | corr(β_ANN,β_CPI) | γ = β_CPI − 0.5·β_ANN | se(γ) 正しい | t(γ) | c46 の素朴版 β_CPI+2se vs 0.5β_ANN |")
say("|---|---|---|---|---|---|---|---|")
TOST = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.CPI | o.ctrl]
    res, V, G = fit(sel, ["ANN", "CPI"], fe="hour")
    bA, sA, _ = res["ANN"]; bC, sC, _ = res["CPI"]
    cv = np.zeros(V.shape[0]); cv[2] = 1.0; cv[1] = -0.5
    g = bC - 0.5 * bA; sg = math.sqrt(max(cv @ V @ cv, 0))
    rho = V[1, 2] / (sA * sC) if sA > 0 and sC > 0 else float("nan")
    TOST[lab] = (g, sg)
    say(f"| {lab} | {tstr(bA,sA)} | {tstr(bC,sC)} | {rho:+.3f} | {g:+.3f} | {sg:.3f} | **{g/sg if sg>0 else float('nan'):+.2f}** | {bC+2*sC:+.3f} vs {0.5*bA:+.3f} → {'FAIL' if bC+2*sC < 0.5*bA else 'not FAIL'} |")
g_out, sg_out = TOST["外 2021-26H1"]
BREAK_TOST = (g_out / sg_out) < -2 if sg_out > 0 else False
say(f"- **BREAK-TOST**（外 t(γ) < −2 ＝ c46 は FAIL と書くべきだった）→ **{BREAK_TOST}**（t {g_out/sg_out:+.2f}）")
say("")

# =====================================================================
say(f"## S2 BREAK-INSAMPLE: 在 2010-20 の **FOMC 午後窓 +0.320 (t 2.06)** は本物か（偽 FOMC {NFAKE} 回・非発表水曜 14:00）")
o = sub(2010, 2020)
base = o[o.FOMCw | o.ctrl].copy()
res0, V0, G0 = fit(base, ["FOMCw"], fe="hour"); b0, s0, n0 = res0["FOMCw"]; tobs = b0 / s0
pool_w = nonev[(nonev.year >= 2010) & (nonev.year <= 2020) & (nonev.weekday == 2)]
nev = int(((FOMC_ANN.year >= 2010) & (FOMC_ANN.year <= 2020)).sum())
et_base = base.entry_time.to_numpy(float); ctrlv = base.ctrl.to_numpy()
tf = []
for it in range(NFAKE):
    pick = pd.DatetimeIndex(rng.choice(pool_w, size=min(nev, len(pool_w)), replace=False))
    t0s = np.sort(epoch_et(pick, 14, 0))
    pos = np.clip(np.searchsorted(t0s, et_base, side="right") - 1, 0, len(t0s) - 1)
    fm = (et_base >= t0s[pos]) & (et_base < t0s[pos] + SPAN) & ~base.FOMCw.to_numpy()
    base["FK"] = fm; base["ctrl2"] = ctrlv & ~fm
    sel = base[base.FOMCw | base.FK | base.ctrl2]
    if sel.FK.sum() < 10: continue
    res, V, G = fit(sel, ["FOMCw", "FK"], fe="hour")
    tf.append(res["FK"][0] / res["FK"][1] if res["FK"][1] > 0 else np.nan)
tf = np.array(tf, float); p_in = float(np.nanmean(tf >= tobs))
say(f"- 在 FOMC 窓: β {b0:+.3f}・se {s0:.3f}・t **{tobs:+.2f}**・n {n0} 本・FOMC 公表 {nev} 回")
say(f"- 偽 FOMC（非発表水曜 {len(pool_w)} 日から {nev} 日・14:00 ET）{len(tf)} 回: 帰無 平均 {np.nanmean(tf):+.2f}・sd {np.nanstd(tf):.2f}・p97.5 {np.nanpercentile(tf,97.5):+.2f}・max {np.nanmax(tf):+.2f} → **片側経験 p {p_in:.4f}**（事後腕 K=2 の Bonferroni: {min(1.0,p_in*2):.4f}）")
say("")
say("| 在の分割 | NFP 窓 n/β(t) | FOMC 窓 n/β(t) |")
say("|---|---|---|")
for nm, a, b_ in (("2010-15", 2010, 2015), ("2016-20", 2016, 2020), ("2013-20（FOMC 腕の実在期間）", 2013, 2020)):
    oo = sub(a, b_)
    cells = []
    for arm in ("NFPw", "FOMCw"):
        bse = oo[oo[arm] | oo.ctrl]
        if bse[arm].sum() < 10: cells.append(f"{int(bse[arm].sum())}/n 不足"); continue
        rr, VV, _ = fit(bse, [arm], fe="hour"); cells.append(f"{rr[arm][2]}/{tstr(*rr[arm][:2])}")
    say(f"| {nm} | {cells[0]} | {cells[1]} |")
say("")
say("- 在 FOMC 窓 LOYO（2013-2020・1 年抜き）:")
loyo = []
for yl in range(2013, 2021):
    oo = tr[(tr.year >= 2013) & (tr.year <= 2020) & (tr.year != yl)]
    bse = oo[oo.FOMCw | oo.ctrl]
    rr, VV, _ = fit(bse, ["FOMCw"], fe="hour")
    loyo.append(rr["FOMCw"][0] / rr["FOMCw"][1] if rr["FOMCw"][1] > 0 else np.nan)
    say(f"  - 除 {yl}: {tstr(*rr['FOMCw'][:2])} n {rr['FOMCw'][2]}")
h1 = fit(sub(2010, 2015)[sub(2010,2015).FOMCw | sub(2010,2015).ctrl], ["FOMCw"], fe="hour")[0]["FOMCw"] if sub(2010,2015).FOMCw.sum() >= 10 else (np.nan, np.nan, 0)
h2 = fit(sub(2016, 2020)[sub(2016,2020).FOMCw | sub(2016,2020).ctrl], ["FOMCw"], fe="hour")[0]["FOMCw"]
BREAK_INSAMPLE = (p_in < 0.025) and (h1[0] > 0 if np.isfinite(h1[0]) else False) and (h2[0] > 0)
say(f"- **BREAK-INSAMPLE**（在 FOMC 窓 経験 p < 0.025 ∧ 2 分割とも β>0）→ **{BREAK_INSAMPLE}**（p {p_in:.4f}・2010-15 {h1[0]:+.3f}・2016-20 {h2[0]:+.3f}）")
say("")

# =====================================================================
say(f"## S3 BREAK-SYM（中心）: **第 1 段 R4 と完全に同一の帰無構成**（曜日 × 当日実現ボラ五分位 一致）を ANN 腕にも当てる")
say("偽 ANN = 非発表**金曜**（ボラ五分位一致・NFP 件数）を 08:30 ＋ 非発表**水曜**（同・FOMC 件数）を 14:00 に置いた合成腕")
say("| 窓 | 実 ANN 日 ボラ中位 | 偽 ANN 日 ボラ中位 | 実測 t(β_ANN) | 帰無 平均 t | 帰無 sd | p97.5 | max | **片側経験 p** | 偽 β 平均 |")
say("|---|---|---|---|---|---|---|---|---|---|")
SYM = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); base = o[o.ANN | o.ctrl].copy()
    res0, V0, _ = fit(base, ["ANN"], fe="hour"); bA, sA, nA = res0["ANN"]; tobsA = bA / sA
    nfp_e = NFP[(NFP.year >= lo_) & (NFP.year <= hi_)]; fom_e = FOMC_ANN[(FOMC_ANN.year >= lo_) & (FOMC_ANN.year <= hi_)]
    nfp_e = nfp_e[nfp_e.isin(day_vol.index)]; fom_e = fom_e[fom_e.isin(day_vol.index)]
    pool = nonev[(nonev.year >= lo_) & (nonev.year <= hi_)]
    pv = day_vol.reindex(pool).to_numpy(); qs = np.nanpercentile(pv, [20, 40, 60, 80])
    pq = np.searchsorted(qs, pv, side="right")
    pdf = pd.DataFrame({"d": pool, "w": pool.weekday, "q": pq})
    def cnt_of(ev):
        qq = np.searchsorted(qs, day_vol.reindex(ev).to_numpy(), side="right")
        c = {}
        for q in qq: c[int(q)] = c.get(int(q), 0) + 1
        return c
    c_nfp = cnt_of(nfp_e); c_fom = cnt_of(fom_e)
    et_base = base.entry_time.to_numpy(float); annv = base.ANN.to_numpy(); ctrlv = base.ctrl.to_numpy()
    tf = []; bf = []; vm = []
    for it in range(NFAKE):
        pk_f = []; pk_w = []
        for q, c in c_nfp.items():
            cw = pdf[(pdf.w == 4) & (pdf.q == q)].d.to_numpy()
            if len(cw): pk_f.extend(list(rng.choice(cw, size=min(c, len(cw)), replace=False)))
        for q, c in c_fom.items():
            cw = pdf[(pdf.w == 2) & (pdf.q == q)].d.to_numpy()
            if len(cw): pk_w.extend(list(rng.choice(cw, size=min(c, len(cw)), replace=False)))
        if len(pk_f) + len(pk_w) < 10: continue
        t0s = np.sort(np.r_[epoch_et(pd.DatetimeIndex(pk_f), 8, 30) if pk_f else np.array([]),
                            epoch_et(pd.DatetimeIndex(pk_w), 14, 0) if pk_w else np.array([])])
        vm.append(float(np.nanmedian(day_vol.reindex(pd.DatetimeIndex(list(pk_f) + list(pk_w))).to_numpy())))
        pos = np.clip(np.searchsorted(t0s, et_base, side="right") - 1, 0, len(t0s) - 1)
        fm = (et_base >= t0s[pos]) & (et_base < t0s[pos] + SPAN) & ~annv
        base["FK"] = fm; base["ctrl2"] = ctrlv & ~fm
        sel = base[base.ANN | base.FK | base.ctrl2]
        if sel.FK.sum() < 10: continue
        res, V, G = fit(sel, ["ANN", "FK"], fe="hour")
        b_, s_, _ = res["FK"]; tf.append(b_ / s_ if s_ > 0 else np.nan); bf.append(b_)
    tf = np.array(tf, float); bf = np.array(bf, float)
    p = float(np.nanmean(tf >= tobsA)) if len(tf) else float("nan")
    av = float(np.nanmedian(day_vol.reindex(pd.DatetimeIndex(list(nfp_e) + list(fom_e))).to_numpy()))
    SYM[lab] = dict(p=p, bmean=float(np.nanmean(bf)), t=tobsA, sd=float(np.nanstd(tf)))
    say(f"| {lab} | {av:.1f} | {np.nanmedian(vm) if vm else float('nan'):.1f} | **{tobsA:+.2f}** | {np.nanmean(tf):+.2f} | {np.nanstd(tf):.2f} | {np.nanpercentile(tf,97.5):+.2f} | {np.nanmax(tf):+.2f} | **{p:.4f}** | {np.nanmean(bf):+.3f} |")
BREAK_SYM = SYM["外 2021-26H1"]["p"] > 0.025
say(f"- **BREAK-SYM**（外 実測 t(β_ANN) の片側経験 p > 0.025）→ **{BREAK_SYM}**（p {SYM['外 2021-26H1']['p']:.4f}）")
say("")
say("### 同一帰無構成での 2 腕の並置（これが c46 が出すべきだった表・方法論 54 の校正版）")
say("| 腕（外 2021-26H1） | β | t | 偽 β 平均（曜日×ボラ一致） | β − 偽 β 平均 | 片側経験 p |")
say("|---|---|---|---|---|---|")
say(f"| ANN（NFP 金 08:30 ＋ FOMC 水 14:00） | +0.511 | +4.01 | {SYM['外 2021-26H1']['bmean']:+.3f} | {0.511-SYM['外 2021-26H1']['bmean']:+.3f} | **{SYM['外 2021-26H1']['p']:.4f}** |")
say("| CPI（08:30・火〜金） | +0.143 | +1.30 | +0.103（第 1 段 R4） | +0.040 | **0.2350**（第 1 段 R4） |")
say("")

say("## 第 2 段 判定")
rules = [("BREAK-TOST", BREAK_TOST), ("BREAK-INSAMPLE", BREAK_INSAMPLE), ("BREAK-SYM", BREAK_SYM)]
landed = [n for n, v in rules if v]
for n, v in rules:
    say(f"- {n}: {'☠ **当たった**' if v else '★ 不発'}")
say(f"- 第 2 段で当たった規則: **{landed if landed else 'なし'}**")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
