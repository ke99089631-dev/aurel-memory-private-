# -*- coding: utf-8 -*-
"""
[cycle46 研究レーン / 2026-11-17 16:30]【深化・適用範囲: 独立な事象集合での追試】
反証 11-17 15:40 が c45 を broken（inconclusive）にした後に残した記述:
  「2021+ の金 scan 本は、予定された公表時刻（NFP 08:30／FOMC 14:00 ET）の後 0〜4 h に建つと +0.5R。
   情報の大きさ・ジャンプの有無・高ボラ日・幾何・発表日（窓外）はすべて否定済み＝"予定時刻の後の時計の上の何か"」
この記述が NFP/FOMC に固有か（構成依存・2 系列の偶然）、予定公表一般（scheduled-release clock）かを、
NFP/FOMC と**独立な第 3 の定時公表 = CPI（08:30 ET）**で追試する。CPI は c44 で暦を取得済み（bls 実公表日・202 回）だが、
scan 本の処置腕としては一度も使われていない（c44 は価格ドリフト β のみ・c45 は ctrl 除外のみ）。
CPI 暦の妥当性: 外 2021-26H1 J 72%（金）／83%（US500）= PASS、在 2010-20 J 35% = 「暦は妥当・価格は無風」（c44）。

=== 事前固定（数字を見る前・この docstring が正本） ===
データ: data/macro/XAU_m5_close.npz・data/refute_c4_scan_paths_2010_2026.json（c4 凍結 19404 本）・
      data/macro/CPI_dates.csv・FOMC_dates.csv・NFP = c24 v2 規則。scan 無し・M5 読込なし・MT5 無し・外部通信無し。
R* = R + (FEED_TOL/risk)·1{SL,TP}。窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括は使わない）。
腕（互いに排反・**両腕ともジャンプに無条件**＝方法論 54 の対称性を満たす）:
  ANN = NFP 08:30／FOMC（scheduled・2013-03-20+）14:00 ET の [t0, t0+4 h)（c45 と同一・複製）。
  CPI = CPI 公表日 08:30 ET の [t0, t0+4 h)、ただし NFP/FOMC と同日の CPI は ANN に譲り CPI 腕から除く。
  ctrl = 非 NFP/FOMC/CPI 日 ∧ ET 月〜金 ∧ 4σ ジャンプ後 4 h に入らない本（c45 と同一）。
推定: Rs ~ 1{ANN} + 1{CPI} + ET 時刻 FE（24）・建玉日クラスタ se。差 ANN − CPI の se はクラスタ共分散から。
校正（方法論 55／㊿ 補強・単一腕の窓集合 Δμ は帰無 sd が名目超＝反証 15:40 R5b 1.46）:
  偽 CPI = 非発表平日から**曜日構成一致**で同数の日を無作為抽出し 08:30 ET に置く（NFAKE 回）→ t(β_偽CPI) の帰無分布
  → 実測 t の片側経験 p と帰無 sd を印字。判定は経験 p で行う。
判定（外 2021-26H1・主セル 1 = β_CPI・名目 0.025 片側）:
  PASS（予定公表一般に一般化）= β_CPI > 0 ∧ 日クラスタ t ≥ 2 ∧ 偽 CPI 経験 p < 0.025。
  FAIL（NFP/FOMC 固有・CPI は半分未満）= β_CPI + 2·se < 0.5·β_ANN（同等性の棄却方向・方法論 55）。
  どちらでもなければ inconclusive（MDE = 2·se を印字・前向き条件を書く）。
在 2010-20 も同じ表を印字（ANN は在 null が既知・CPI 在は暦妥当だが無風＝「時計だけ」の強形の記述）。
副（記述・判定に使わない）: ①CPI_J／CPI_NJ（公表足が 5σ ジャンプか・c45 検出器）②経過分 0-60／60-120／120-240
  ③側×公表足方向（整合/逆行）④プラセボ = CPI t0 を ±7 日（両方向を印字・方法論 53）⑤x0 look-ahead 対照・幾何（atr/risk/b）
  ⑥公表足 |r(t0)| 四分位別 β（反証 15:40 S1 の CPI 版・プール ANN∪CPI も）⑦ANN∪CPI プール β と ANN − CPI 差 ⑧年別 ⑨裾（上位 3 本除去）。
決着可能性（事前）: CPI 外 ≈66 公表日・本 ≈1.7/日 → ≈110 本・日クラスタ se ≈ 0.158·√(82/66) ≈ 0.18 → MDE ≈0.35R。
  ANN 級 +0.5 なら t ≈2.8 で PASS 可。FAIL は β_CPI + 0.36 < 0.26 ⇔ β_CPI < −0.10 を要する＝0 近傍なら inconclusive（正直にそう書く）。
事前の最重大反証: (i) CPI は 08:30 ET のみ＝ANN の NFP 腕と同時刻・同曜日帯でなく火〜金に散る（時刻 FE で揃える・曜日 FE は副で印字）。
  (ii) 構成依存（c4 凍結 1 構成・bid 1 社）は本サイクルでも未分離。(iii) 外の CPI 日は 2021-23 のインフレ期に「重要度」が高い＝
  "予定性" と "重要度" は CPI でも分離できない（S1 型の四分位で記述のみ）。(iv) 多重検定: 判定セル 1・他は記述。
seed 20261117・NFAKE 400。出力 data/c46_cpi_scheduled_clock_result.md。読取専用・発注なし・本番編集なし。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c46_cpi_scheduled_clock_result.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
ZMAIN = 5.0; W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0; NFAKE = 400
WD = "月火水木金土日"

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

say("# [cycle46] 予定公表の時計は NFP/FOMC 固有か: 独立な第 3 の定時公表 CPI（08:30 ET）での追試")
say(f"- 事前固定は docstring・seed {SEED}・主セル = 外 β_CPI（時刻 FE・日クラスタ・偽 CPI {NFAKE} 回で校正）")
say("")

# ---------- 暦 ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI_ALL = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
nfp_fomc_days = set(list(NFP.normalize()) + list(FOMC_ALL.normalize()))
CPI = pd.DatetimeIndex([d for d in CPI_ALL if d.normalize() not in nfp_fomc_days])
n_overlap = len(CPI_ALL) - len(CPI)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0); t_cpi = epoch_et(CPI, 8, 30)
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI_ALL.normalize()))))
say(f"- CPI 暦 {len(CPI_ALL)} 回（{CPI_ALL.min().date()}〜{CPI_ALL.max().date()}）・NFP/FOMC と同日 {n_overlap} 回は ANN に譲る → CPI 腕 {len(CPI)} 回・曜日 "
    + " ".join(f"{WD[w]}{int((CPI.weekday==w).sum())}" for w in range(5)))
cpi_y = CPI.year
say("- CPI 腕の年別件数（㉔）: " + " ".join(f"{y}:{int((cpi_y==y).sum())}" for y in range(2010, 2027)))

# ---------- npz・ジャンプ検出（c45 と同一） ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
say(f"- XAU_m5_close: {len(ts)} 本 {tt[0]}〜{tt[-1]} UTC（⑩）・flat 全体 {(~nf).mean()*100:.1f}%・曜日別 " +
    " ".join(f"{WD[w]}{(~nf[wd==w]).mean()*100:.1f}%" for w in range(7)) + "（⑪）")
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

J4 = decluster(cand & (z >= 4.0))
say(f"- 4σ declustered ジャンプ {len(J4)}（ctrl 除外用・c45 と同一）")

def price_bar(tsec):
    out = np.full(len(tsec), -1); ok = np.isfinite(tsec)
    key = tsec[ok].astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    good = ts[pos] == key; tmp = np.full(ok.sum(), -1); tmp[good] = pos[good]; out[ok] = tmp; return out

# 公表足の r・z（CPI／NFP／FOMC）
b_cpi = price_bar(t_cpi); b_nfp = price_bar(t_nfp); b_fomc = price_bar(t_fomc)
def rz(b):
    rr = np.where(b >= 0, r[np.clip(b, 0, None)], np.nan); zzv = np.where(b >= 0, z[np.clip(b, 0, None)], np.nan); return rr, zzv
r_cpi, z_cpi = rz(b_cpi); r_nfp, z_nfp = rz(b_nfp); r_fomc, z_fomc = rz(b_fomc)
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
say("| 窓 | CPI 公表足 \\|r\\| 中央値 bp／5σ 率 | NFP 同 | FOMC 同 |")
say("|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    mc = (cpi_y >= lo_) & (cpi_y <= hi_); mnf = (NFP.year >= lo_) & (NFP.year <= hi_); mf = (FOMC_ANN.year >= lo_) & (FOMC_ANN.year <= hi_)
    f = lambda rr, zv, m: f"{np.nanmedian(np.abs(rr[m])):.1f}／{np.nanmean(zv[m] >= 5)*100:.0f}% (n {int(np.isfinite(rr[m]).sum())})"
    say(f"| {lab} | {f(r_cpi, z_cpi, mc)} | {f(r_nfp, z_nfp, mnf)} | {f(r_fomc, z_fomc, mf)} |")
say("")

# ---------- scan 本 ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)
sv = tr.side.astype(str).str.upper()
tr["sgn"] = np.where(sv.str.startswith("B") | (sv == "1") | (sv == "LONG"), 1, -1)
say(f"- scan 本 {len(tr)}・FEED_TOL {FT}")

def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    if len(t0s) == 0: return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, p_nfp = inwin(t_nfp); m_fomc, p_fomc = inwin(t_fomc); m_cpi, p_cpi = inwin(t_cpi)
tr["ANN"] = m_nfp | m_fomc
tr["CPI"] = m_cpi & ~tr.ANN
tr["ann_t0"] = np.where(m_nfp, p_nfp, np.where(m_fomc, p_fomc, np.nan))
tr["cpi_t0"] = np.where(tr.CPI, p_cpi, np.nan)
tsf = ts.astype(float)
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
bb = price_bar(tr.cpi_t0.to_numpy()); tr["cpi_r"] = np.where(bb >= 0, r[np.clip(bb, 0, None)], np.nan); tr["cpi_z"] = np.where(bb >= 0, z[np.clip(bb, 0, None)], np.nan)
ba = price_bar(tr.ann_t0.to_numpy()); tr["ann_r"] = np.where(ba >= 0, r[np.clip(ba, 0, None)], np.nan); tr["ann_z"] = np.where(ba >= 0, z[np.clip(ba, 0, None)], np.nan)
tr["cpi_min"] = (et_ - tr.cpi_t0.to_numpy()) / 60.0
say(f"- 本数: ANN {int(tr.ANN.sum())}・CPI {int(tr.CPI.sum())}・ctrl {int(tr.ctrl.sum())}")
say("")

# ---------- 推定器 ----------
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    dm = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dm, dm / se if se > 0 else np.nan

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    Xe = X * e[:, None]
    codes, uniq = pd.factorize(np.asarray(g))
    S = np.zeros((len(uniq), X.shape[1])); np.add.at(S, codes, Xe); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def fe_fit(o, groups, extra=None):
    hours = np.arange(24)
    H = np.column_stack([(o.hh.to_numpy() == h).astype(float) for h in hours[1:]])
    Gm = np.column_stack([o[c].to_numpy().astype(float) for c in groups])
    cols = [np.ones(len(o)), Gm, H]
    if extra is not None: cols.append(extra)
    X = np.column_stack(cols); y = o.Rs.to_numpy(float)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    res = {c: (beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(o[c].sum())) for i, c in enumerate(groups)}
    return res, V, G

def tstr(b, s): return f"{b:+.3f} ({(b/s if s>0 else float('nan')):+.2f})"
def sub(lo_, hi_): return tr[(tr.year >= lo_) & (tr.year <= hi_)]

say("## 主表: 時刻 FE 調整 β（日クラスタ t）・未調整 Welch・ANN − CPI 差")
say("| 窓 | 群 | n 本 / 事象日（本あり/暦） | β 時刻FE (日cl t) | MDE 2se | 未調整 Δμ (Welch t) | 群 平均/中央値 | ctrl 平均/中央値 |")
say("|---|---|---|---|---|---|---|---|")
RES = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.CPI | o.ctrl]
    res, V, G = fe_fit(sel, ["ANN", "CPI"])
    C = sel[sel.ctrl]
    ncal = {"ANN": int(((NFP.year >= lo_) & (NFP.year <= hi_)).sum() + ((FOMC_ANN.year >= lo_) & (FOMC_ANN.year <= hi_)).sum()),
            "CPI": int(((cpi_y >= lo_) & (cpi_y <= hi_)).sum())}
    for gname in ["ANN", "CPI"]:
        A = sel[sel[gname]]; b_, se_, n_ = res[gname]; dm, tw = welch(A.Rs, C.Rs)
        say(f"| {lab} | {gname} | {n_} / {A.day.nunique()}/{ncal[gname]} | **{tstr(b_, se_)}** | {2*se_:.3f} | {dm:+.3f} ({tw:+.2f}) | {A.Rs.mean():+.3f}/{A.Rs.median():+.2f} | {C.Rs.mean():+.3f}/{C.Rs.median():+.2f} |")
    cvec = np.zeros(V.shape[0]); cvec[1] = 1; cvec[2] = -1
    dd = res["ANN"][0] - res["CPI"][0]; sd = math.sqrt(max(cvec @ V @ cvec, 0))
    say(f"| {lab} | **ANN − CPI** | | **{tstr(dd, sd)}** | {2*sd:.3f} | | | G 日 {G} |")
    # pooled
    o2 = o.assign(SCH=o.ANN | o.CPI); sel2 = o2[o2.SCH | o2.ctrl]; res2, V2, G2 = fe_fit(sel2, ["SCH"])
    say(f"| {lab} | ANN∪CPI プール | {res2['SCH'][2]} / {sel2[sel2.SCH].day.nunique()} | {tstr(res2['SCH'][0], res2['SCH'][1])} | {2*res2['SCH'][1]:.3f} | | | |")
    RES[lab] = dict(res=res, d=(dd, sd), pool=res2["SCH"])
say("")

# ---------- 校正: 偽 CPI（曜日構成一致・非発表平日・08:30 ET） ----------
say(f"## 校正: 偽 CPI {NFAKE} 回（非発表平日から曜日構成一致で同数抽出・08:30 ET・ANN 腕は実物のまま）→ t(β_偽CPI) の帰無分布")
say("| 窓 | 実測 t(β_CPI) | 帰無 平均 | 帰無 sd | p97.5 | 片側経験 p (t_fake ≥ 実測) | 偽 β 平均 |")
say("|---|---|---|---|---|---|---|")
# trading days in npz (ET date) that are Mon-Fri & not event days
alldays = pd.DatetimeIndex(sorted(set(etdate[(wd <= 4) & nf])))
nonev = alldays[~alldays.isin(evdays)]
FAKE = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); base = o[o.ANN | o.ctrl].copy()
    tobs = RES[lab]["res"]["CPI"][0] / RES[lab]["res"]["CPI"][1]
    pool = nonev[(nonev.year >= lo_) & (nonev.year <= hi_)]
    actual = CPI[(cpi_y >= lo_) & (cpi_y <= hi_)]
    counts = {w: int((actual.weekday == w).sum()) for w in range(5)}
    tf = []; bf = []
    et_base = base.entry_time.to_numpy(float)
    for it in range(NFAKE):
        pick = []
        for w, c in counts.items():
            if c == 0: continue
            cand_w = pool[pool.weekday == w]
            pick.extend(list(rng.choice(cand_w, size=c, replace=False)))
        t0s = np.sort(epoch_et(pd.DatetimeIndex(pick), 8, 30))
        pos = np.clip(np.searchsorted(t0s, et_base, side="right") - 1, 0, len(t0s) - 1)
        fm = (et_base >= t0s[pos]) & (et_base < t0s[pos] + SPAN) & ~base.ANN.to_numpy()
        base["FK"] = fm; base["ctrl2"] = base.ctrl.to_numpy() & ~fm
        sel = base[base.ANN | base.FK | base.ctrl2]
        if sel.FK.sum() < 10: continue
        res, V, G = fe_fit(sel, ["ANN", "FK"])
        b_, s_, _ = res["FK"]; tf.append(b_ / s_ if s_ > 0 else np.nan); bf.append(b_)
    tf = np.array(tf); bf = np.array(bf)
    pemp = float(np.mean(tf >= tobs)) if len(tf) else float("nan")
    FAKE[lab] = dict(t=tf, p=pemp, sd=float(np.nanstd(tf)))
    say(f"| {lab} | {tobs:+.2f} | {np.nanmean(tf):+.2f} | {np.nanstd(tf):.2f} | {np.nanpercentile(tf, 97.5):+.2f} | **{pemp:.4f}** | {np.nanmean(bf):+.3f} |")
say("")

# ---------- 判定 ----------
say("## 判定（事前固定・外 2021-26H1・主セル β_CPI）")
ro = RES["外 2021-26H1"]; bC, sC, nC = ro["res"]["CPI"]; bA, sA, nA = ro["res"]["ANN"]
tC = bC / sC if sC > 0 else float("nan"); pC = FAKE["外 2021-26H1"]["p"]
pass_ = (bC > 0) and (tC >= 2) and (pC < 0.025)
fail_ = (bC + 2 * sC) < 0.5 * bA
verdict = "PASS（予定公表一般に一般化）" if pass_ else ("FAIL（NFP/FOMC 固有・CPI は ANN の半分未満）" if fail_ else "inconclusive")
say(f"- 外: β_CPI {bC:+.3f} (t {tC:+.2f}・n {nC}・MDE {2*sC:.3f}・偽 CPI 経験 p {pC:.4f}・帰無 sd {FAKE['外 2021-26H1']['sd']:.2f})／β_ANN {bA:+.3f} (t {bA/sA:+.2f}・n {nA})・0.5·β_ANN {0.5*bA:+.3f}・β_CPI 95% 上限 {bC+2*sC:+.3f}")
say(f"- **判定: {verdict}**  [PASS 条件 β>0 ∧ t≥2 ∧ p<0.025 → {pass_} / FAIL 条件 β_CPI+2se < 0.5·β_ANN → {fail_}]")
dd, sd = ro["d"]
say(f"- 差 ANN − CPI 外 {tstr(dd, sd)}・MDE {2*sd:.3f}・プール ANN∪CPI {tstr(*ro['pool'][:2])} (n {ro['pool'][2]})")
say("")

# ---------- 副① CPI_J / CPI_NJ ----------
say("## 副① CPI 公表足が 5σ ジャンプか（CPI_J／CPI_NJ）と ANN の同分割（反証 15:40 R2 の複製）")
say("| 窓 | CPI_J n/β(t) | CPI_NJ n/β(t) | ANN_J n/β(t) | ANN_NJ n/β(t) |")
say("|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    o = o.assign(CJ=o.CPI & (o.cpi_z >= 5), CN=o.CPI & ~(o.cpi_z >= 5), AJ=o.ANN & (o.ann_z >= 5), AN=o.ANN & ~(o.ann_z >= 5))
    sel = o[o.CJ | o.CN | o.AJ | o.AN | o.ctrl]
    res, V, G = fe_fit(sel, ["CJ", "CN", "AJ", "AN"])
    f = lambda k: f"{res[k][2]}/{tstr(res[k][0], res[k][1])}"
    say(f"| {lab} | {f('CJ')} | {f('CN')} | {f('AJ')} | {f('AN')} |")
say("")

# ---------- 副② 経過分 ----------
say("## 副② CPI 後の経過分別 β（0-60／60-120／120-240 分）")
say("| 窓 | 0-60 n/β(t) | 60-120 n/β(t) | 120-240 n/β(t) |")
say("|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); m = o.cpi_min
    o2 = o.assign(K1=o.CPI & (m < 60), K2=o.CPI & (m >= 60) & (m < 120), K3=o.CPI & (m >= 120))
    sel = o2[o2.K1 | o2.K2 | o2.K3 | o2.ctrl]; res, V, G = fe_fit(sel, ["K1", "K2", "K3"])
    f = lambda k: f"{res[k][2]}/{tstr(res[k][0], res[k][1])}"
    say(f"| {lab} | {f('K1')} | {f('K2')} | {f('K3')} |")
say("")

# ---------- 副③ 側×公表足方向 ----------
say("## 副③ 側 × CPI 公表足方向（整合 = 本の側が公表足の符号と同じ）")
say("| 窓 | CPI 整合 n/β(t) | CPI 逆行 n/β(t) | CPI 公表足 flat n |")
say("|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    o = o.assign(C_al=o.CPI & (np.sign(o.cpi_r) == o.sgn), C_ag=o.CPI & (np.sign(o.cpi_r) == -o.sgn))
    nflat = int((o.CPI & ~(o.C_al | o.C_ag)).sum())
    sel = o[o.C_al | o.C_ag | o.ctrl]; res, V, G = fe_fit(sel, ["C_al", "C_ag"])
    f = lambda k: f"{res[k][2]}/{tstr(res[k][0], res[k][1])}"
    say(f"| {lab} | {f('C_al')} | {f('C_ag')} | {nflat} |")
say("")

# ---------- 副④ プラセボ ±7 日 ----------
say("## 副④ プラセボ: CPI t0 を ±7 日（両方向・方法論 53・実事象日は除外）")
say("| シフト | 在 n/β(t) | 外 n/β(t) | 近年 n/β(t) |")
say("|---|---|---|---|")
for sh in (-7, 7):
    mp, _ = inwin(t_cpi + sh * 86400.0)
    tr["PL"] = mp & ~tr.isevday & (tr.wd <= 4) & ~tr.ANN
    cells = []
    for lab, lo_, hi_ in ERAS:
        o = sub(lo_, hi_); o = o.assign(ctrl2=o.ctrl & ~o.PL)
        sel = o[o.ANN | o.PL | o.ctrl2]
        if sel.PL.sum() < 10: cells.append(f"{int(sel.PL.sum())}/—"); continue
        res, V, G = fe_fit(sel, ["ANN", "PL"])
        cells.append(f"{res['PL'][2]}/{tstr(res['PL'][0], res['PL'][1])}")
    say(f"| {sh:+d} 日 | {cells[0]} | {cells[1]} | {cells[2]} |")
say("")

# ---------- 副⑤ x0・幾何 ----------
say("## 副⑤ look-ahead 陽性対照 x0（建玉足・㉚）と幾何の群差")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); C = o[o.ctrl]
    for gname in ["ANN", "CPI"]:
        A = o[o[gname]]
        if len(A) < 5: continue
        dx, tx = welch(A.x0, C.x0)
        say(f"- {lab} {gname}: x0 Δ {dx:+.3f} (t {tx:+.2f})・atr {A.atr.mean():.2f} vs ctrl {C.atr.mean():.2f}・risk {A.risk.mean():.2f} vs {C.risk.mean():.2f}・b {A.b.mean():.2f} vs {C.b.mean():.2f}・TP 率 {(A.exit=='TP').mean()*100:.0f}% vs {(C.exit=='TP').mean()*100:.0f}%・hold 中央値 {A.hold.median():.0f} vs {C.hold.median():.0f}・曜日 " + " ".join(f"{WD[w]}{int((A.wd==w).sum())}" for w in range(5)))
# 幾何調整版（外）
o = sub(2021, 2026); sel = o[o.ANN | o.CPI | o.ctrl]
ex = np.column_stack([np.log(sel.atr.to_numpy(float)), np.log(sel.risk.to_numpy(float)), sel.b.to_numpy(float), sel.sgn.to_numpy(float)])
res, V, G = fe_fit(sel, ["ANN", "CPI"], extra=ex)
say(f"- 外 幾何調整（log atr・log risk・b・sgn）: ANN {tstr(*res['ANN'][:2])}・CPI {tstr(*res['CPI'][:2])}")
# 曜日 FE 版（外）
dw = np.column_stack([(sel.wd.to_numpy() == w).astype(float) for w in range(1, 5)])
res, V, G = fe_fit(sel, ["ANN", "CPI"], extra=dw)
say(f"- 外 曜日 FE 追加: ANN {tstr(*res['ANN'][:2])}・CPI {tstr(*res['CPI'][:2])}")
say("")

# ---------- 副⑥ 公表足 |r| 四分位 ----------
say("## 副⑥ 公表足 |r(t0)| 四分位別 β（反証 15:40 S1 の複製・外）: CPI 単独／ANN∪CPI プール")
o = sub(2021, 2026)
for name, mask, rcol in [("CPI", o.CPI, "cpi_r"), ("ANN∪CPI", o.ANN | o.CPI, None)]:
    if rcol is None:
        rr = np.where(o.ANN, o.ann_r, o.cpi_r)
    else:
        rr = o[rcol].to_numpy()
    ar = np.abs(rr); A = o[mask & np.isfinite(ar)]
    q = np.nanquantile(np.abs(np.where(A.ANN, A.ann_r, A.cpi_r)), [0.25, 0.5, 0.75])
    arA = np.abs(np.where(o.ANN, o.ann_r, o.cpi_r))
    o2 = o.assign(Q1=mask & (arA <= q[0]), Q2=mask & (arA > q[0]) & (arA <= q[1]), Q3=mask & (arA > q[1]) & (arA <= q[2]), Q4=mask & (arA > q[2]))
    sel = o2[o2.Q1 | o2.Q2 | o2.Q3 | o2.Q4 | o2.ctrl]; res, V, G = fe_fit(sel, ["Q1", "Q2", "Q3", "Q4"])
    cv = np.zeros(V.shape[0]); cv[4] = 1; cv[1] = -1; d41 = res["Q4"][0] - res["Q1"][0]; s41 = math.sqrt(max(cv @ V @ cv, 0))
    say(f"- {name}: Q1(|r|≤{q[0]:.0f}bp) {res['Q1'][2]}/{tstr(*res['Q1'][:2])}・Q2 {res['Q2'][2]}/{tstr(*res['Q2'][:2])}・Q3 {res['Q3'][2]}/{tstr(*res['Q3'][:2])}・Q4(>{q[2]:.0f}) {res['Q4'][2]}/{tstr(*res['Q4'][:2])}・Q4−Q1 {tstr(d41, s41)}")
say("")

# ---------- 副⑧⑨ 年別・裾 ----------
say("## 副⑧⑨ 年別（未調整 Δμ vs 同年 ctrl）・裾")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); A = o[o.CPI]; C = o[o.ctrl]
    say(f"- {lab} CPI 年別 Δμ (n): " + " ".join(f"{y}:{welch(A[A.year==y].Rs, C[C.year==y].Rs)[0]:+.2f}({int((A.year==y).sum())})" for y in range(lo_, hi_ + 1) if (A.year == y).sum() >= 3))
o = sub(2021, 2026); A = o[o.CPI]; C = o[o.ctrl]
srt = A.Rs.sort_values(ascending=False)
for k in (1, 3, 5):
    a3 = A.drop(srt.index[:k]); dm, t = welch(a3.Rs, C.Rs)
    say(f"- 外 CPI 上位 {k} 本除去: 未調整 Δμ {dm:+.3f} (t {t:+.2f})")
say(f"- 外 CPI 本の分布: 中央値 {A.Rs.median():+.2f}・TP 率 {(A.exit=='TP').mean()*100:.0f}%・SL 率 {(A.exit=='SL').mean()*100:.0f}%・本/日 {len(A)/max(A.day.nunique(),1):.2f}")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
