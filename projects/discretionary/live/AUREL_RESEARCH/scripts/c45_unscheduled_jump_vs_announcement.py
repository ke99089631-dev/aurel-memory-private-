# -*- coding: utf-8 -*-
"""
[cycle45 研究レーン / 2026-11-17 12:50]【深化・機構判別】
反証 11-17 09:30 が survived とした唯一の信号
  「2021+ の金 scan 本は NFP(08:30 ET)/FOMC(14:00 ET) の発表後 0〜4 時間に建つと同時刻の非発表日より +0.45〜0.48R」
の機構を判別する: (A) 予定された情報公開（scheduled release）固有か、(B) 大きな 5 分ジャンプ一般（post-jump 状態）か。
反証 B5 は「高ボラ日」を殺したが、事象レベルの「ジャンプ」は未検定。

=== 事前固定（数字を見る前・この docstring が正本） ===
データ: data/macro/XAU_m5_close.npz（bid・ts=足開始 UTC 秒・close）／data/refute_c4_scan_paths_2010_2026.json（c4 凍結 19404 本）／
      data/macro/FOMC_dates.csv／CPI_dates.csv／NFP = c24 v2 規則。scan 無し・M5 読込なし・MT5 無し・外部通信無し。
R* = R + (FEED_TOL/risk)·1{SL,TP}（c44/反証と同一）。窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括は使わない）。

ジャンプ定義（F_t 可測）: 足 i の r_i = ln cl_i − ln cl_{i−1}（bp）。σ_trail,i = 直前 5520 足（≈20 セッション日）の非 flat 足 r の RMS（足 i を含まない・非 flat ≥1000 足）。
  候補 = 非 flat ∧ 直前 3 足 非 flat（stale 明けの蓄積リターンを除く）∧ ET 月〜金 ∧ 日次ブレイク 17:00〜18:10 ET を除く（再開直後 2 足も除く ㉙）
  ジャンプ = |r_i| ≥ 5·σ_trail,i（主）。感度 4σ・6σ は記述。
  decluster: 直前の採用ジャンプから 4 時間以内の候補は採用しない（独立事象 1 つ・全スロット共通の集合で実施）。
  事象時刻 t0 = ts_i（足開始）、ジャンプ既知時刻 = t0+300（足終値）。
  3 群の事象集合（互いに排反）:
    ANN = NFP 08:30 ET／FOMC（scheduled・2013-03-20+）14:00 ET の公表時刻（反証 R10 に従い窓は 0〜4 h: [t0, t0+14400)）。
    SJ  = 非 NFP/FOMC/CPI 日のジャンプで足開始分 ∈ {00,15,30,45} ET（= 他の定時公表の代理: 08:15 ADP・09:45 PMI・10:00・13:30 等）。
    UJ  = 非 NFP/FOMC/CPI 日のジャンプで足開始分 ∈ {05,10,20,25,35,40,50,55}（= 予定外ジャンプ）。
  SJ/UJ の本の窓 = [t0+300, t0+300+14400)（ジャンプが既知になってから 4 h）。
対照 ctrl = 非 NFP/FOMC/CPI 日 ∧ ET 月〜金 ∧ どのジャンプ（4σ 以上・全スロット）の後 4 h にも入らない本（全時刻）。
推定: Rs ~ 1{ANN} + 1{SJ} + 1{UJ} + ET 時刻 FE（24 ダミー）、建玉日クラスタ se（反証 (b)）。β_g = 時刻調整済 Δμ_g。
   差 β_ANN − β_UJ の se はクラスタ共分散から。参考に未調整 Welch と日クラスタ t も印字。
判定（外 2021-26H1・主セル 1 = β_UJ、名目 0.025 両側）:
   H_GEN（ジャンプ一般）  PASS = β_UJ > 0 ∧ t ≥ 2 ∧ β_UJ ≥ 0.5·β_ANN。
   H_SCHED（予定公表固有）PASS = |t(β_UJ)| < 1.5 ∧ (β_ANN − β_UJ) の t ≥ 2。
   どちらも満たさなければ inconclusive（MDE = 2·se を印字）。SJ は副（SJ ≈ ANN なら「定時公表一般」・SJ ≈ 0 なら「NFP/FOMC 固有」の読みを添える）。
在 2010-20 も同じ表を印字（ANN は在 null が既知＝UJ が在で立てば ANN と別構造）。
ゲート ㉛: 反証 (d) に従い「印字規則であって証拠ではない」。本サイクルは全窓を印字し、判定は ANN 信号の所在する外で行う（問いが外の信号の機構なので）。
副（記述）: ①用量反応 ㊾ = UJ の z 三分位別 β ②側×ジャンプ方向（整合/逆行）の β（ANN・UJ）③プラセボ = UJ の t0 を ±7 日ずらした偽事象（R7 型・実事象日・実ジャンプ窓は除外）
   ④look-ahead 陽性対照 x0 の群差（㉚）⑤感度 4σ/6σ ⑥事象数・本数・本/事象・ジャンプ |r| 中央値（ANN の公表足 |r| との比較）⑦事象後の経過分別（0-60/60-120/120-240）。
決着可能性（事前）: 反証の ANN 日クラスタ se 0.158（67 日）。UJ 事象が外で ≥150・本 ≥150 なら se ≈ 0.12、差の se ≈ 0.20 → ANN 0.48 vs UJ 0 で t ≈ 2.4＝決着可。少なければ MDE を印字して inconclusive。
事前の最重大反証: (i) UJ の「予定外」は分の規則による代理＝:00 に出る予定外ニュース（要人発言）は SJ に混入し、定時指標の数秒遅れは UJ に入らない（:05 以降にはならない）が、SJ/UJ の差は純粋ではない。
  (ii) UJ 本の幾何（atr・risk）は ANN 本と違い得る → 回帰は時刻 FE のみ（反証 B2 では幾何調整で 6% しか動かなかった）。(iii) bid 1 社・CFD。
  (iv) ジャンプ定義（5σ・20 日 RMS）は 1 つの選択＝感度 4/6σ を併記し判定は 5σ のみ。(v) 多重検定: 判定セル 1（β_UJ 外）・残りは記述。
seed 20261117。出力 data/c45_unscheduled_jump_vs_announcement_result.md。読取専用・発注なし・本番編集なし。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c45_unscheduled_jump_vs_announcement_result.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
ZMAIN, ZSENS = 5.0, (4.0, 6.0); W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0
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

say("# [cycle45] 予定外ジャンプ（UJ）vs 定時公表（ANN/SJ）: 発表後 +0.48R の機構判別")
say(f"- 事前固定は docstring・seed {SEED}・主セル = 外 β_UJ（時刻 FE・日クラスタ）")
say("")

# ---------- 暦 ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0)
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

# ---------- npz ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
say(f"- XAU_m5_close: {len(ts)} 本 {tt[0]}〜{tt[-1]} UTC（⑩）・flat 全体 {(~nf).mean()*100:.1f}%・曜日別 " +
    " ".join(f"{WD[w]}{(~nf[wd==w]).mean()*100:.1f}%" for w in range(7)) + "（⑪）")
# trailing sigma (exclude bar i)
r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
idx = np.arange(len(ts))
lo = idx - 1 - W_SIG; hi = idx - 1
valid = (lo >= 0)
S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
nf3 = nf.copy()
for k in (1, 2, 3):
    nf3 &= np.r_[[False] * k, nf[:-k]]
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
cand = nf3 & trading & np.isfinite(sig)
z = np.abs(r) / sig
say(f"- σ_trail 中央値 {np.nanmedian(sig[cand]):.2f} bp・候補足 {cand.sum()}・|r|≥5σ 候補 {int((cand & (z>=5)).sum())}・≥4σ {int((cand & (z>=4)).sum())}・≥6σ {int((cand & (z>=6)).sum())}")

def decluster(mask):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= DECL:
            keep.append(i); last = ts[i]
    return np.array(keep, int)

J = {zt: decluster(cand & (z >= zt)) for zt in (4.0, ZMAIN, 6.0)}
isevbar = etdate.isin(evdays)
def classify(ji):
    ok = ~np.asarray(isevbar[ji])
    sched = (mn[ji] % 15 == 0)
    return ji[ok & sched], ji[ok & ~sched]
SJ5, UJ5 = classify(J[ZMAIN])
say(f"- declustered ジャンプ: 4σ {len(J[4.0])}・5σ {len(J[ZMAIN])}（非 NFP/FOMC/CPI 日: SJ {len(SJ5)}・UJ {len(UJ5)}）・6σ {len(J[6.0])}")
# 年別事象数
yrs = tny.year.to_numpy()
def cnt(ji, lo_, hi_): return int(((yrs[ji] >= lo_) & (yrs[ji] <= hi_)).sum())
say("| 窓 | SJ 事象 | UJ 事象 | UJ |r| 中央値 bp | UJ z 中央値 | SJ |r| 中央値 | ANN 公表足 |r| 中央値（NFP／FOMC） |")
say("|---|---|---|---|---|---|---|")
def price_bar_r(tsec):
    key = tsec.astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    ok = ts[pos] == key; out = np.full(len(key), np.nan); out[ok] = r[pos[ok]]; return out
r_nfp = price_bar_r(t_nfp[np.isfinite(t_nfp)]); r_fomc = price_bar_r(t_fomc[np.isfinite(t_fomc)])
y_nfp = pd.to_datetime(t_nfp[np.isfinite(t_nfp)], unit="s").year; y_fomc = pd.to_datetime(t_fomc[np.isfinite(t_fomc)], unit="s").year
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
for lab, lo_, hi_ in ERAS:
    u = UJ5[(yrs[UJ5] >= lo_) & (yrs[UJ5] <= hi_)]; s_ = SJ5[(yrs[SJ5] >= lo_) & (yrs[SJ5] <= hi_)]
    mn_ = (y_nfp >= lo_) & (y_nfp <= hi_); mf_ = (y_fomc >= lo_) & (y_fomc <= hi_)
    say(f"| {lab} | {len(s_)} | {len(u)} | {np.median(np.abs(r[u])):.1f} | {np.median(z[u]):.2f} | {np.median(np.abs(r[s_])):.1f} | "
        f"{np.nanmedian(np.abs(r_nfp[mn_])):.1f}／{np.nanmedian(np.abs(r_fomc[mf_])):.1f} |")
# UJ の時刻分布（ET 時）
hh_uj = pd.Series(hr[UJ5]).value_counts().sort_index()
say("- UJ 事象の ET 時刻分布（時: 件数）: " + " ".join(f"{h}:{c}" for h, c in hh_uj.items()))
hh_sj = pd.Series(hr[SJ5]).value_counts().sort_index()
say("- SJ 事象の ET 時刻分布（時: 件数）: " + " ".join(f"{h}:{c}" for h, c in hh_sj.items()))
say("")

# ---------- scan 本 ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; TS_ = d["frozen"]["TRIG_SPREAD"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)
side_vals = tr.side.unique()
sv = tr.side.astype(str).str.upper()
tr["sgn"] = np.where(sv.str.startswith("B") | (sv == "1") | (sv == "LONG"), 1, -1)
say(f"- scan 本 {len(tr)}・FEED_TOL {FT}・side 値 {list(side_vals)[:4]} → sgn +1 比率 {(tr.sgn==1).mean():.2f}")

def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    if len(t0s) == 0: return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, p_nfp = inwin(t_nfp); m_fomc, p_fomc = inwin(t_fomc)
tr["ANN"] = m_nfp | m_fomc
tr["ann_t0"] = np.where(m_nfp, p_nfp, np.where(m_fomc, p_fomc, np.nan))
tsf = ts.astype(float)
m_sj, p_sj = inwin(tsf[SJ5] + 300); m_uj, p_uj = inwin(tsf[UJ5] + 300)
tr["SJ"] = m_sj & ~tr.ANN & ~tr.isevday; tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
tr["uj_t0"] = np.where(tr.UJ, p_uj - 300, np.nan); tr["sj_t0"] = np.where(tr.SJ, p_sj - 300, np.nan)
m_any4, _ = inwin(tsf[J[4.0]] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
say(f"- 本数: ANN {int(tr.ANN.sum())}・SJ {int(tr.SJ.sum())}・UJ {int(tr.UJ.sum())}・ctrl {int(tr.ctrl.sum())}（ジャンプ 4σ 後 4h の本を ctrl から除外 {int((m_any4 & ~tr.isevday & (tr.wd<=4)).sum())}）")
# jump direction & z for UJ/SJ/ANN trades
def bar_at(tsec):
    out = np.full(len(tsec), -1); ok = np.isfinite(tsec)
    key = tsec[ok].astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    good = ts[pos] == key; tmp = np.full(ok.sum(), -1); tmp[good] = pos[good]; out[ok] = tmp; return out
b_uj = bar_at(tr.uj_t0.to_numpy()); b_ann = bar_at(tr.ann_t0.to_numpy())
tr["uj_r"] = np.where(b_uj >= 0, r[np.clip(b_uj, 0, None)], np.nan); tr["uj_z"] = np.where(b_uj >= 0, z[np.clip(b_uj, 0, None)], np.nan)
tr["ann_r"] = np.where(b_ann >= 0, r[np.clip(b_ann, 0, None)], np.nan)
tr["uj_min"] = (et_ - tr.uj_t0.to_numpy()) / 60.0; tr["ann_min"] = (et_ - tr.ann_t0.to_numpy()) / 60.0
say("")

# ---------- 推定器 ----------
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    dm = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dm, dm / se if se > 0 else np.nan

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def fe_fit(o, groups):
    """o: DataFrame rows (groups ∪ ctrl). groups: list of column names (bool). returns dict name->(beta,se,n) and V, names"""
    hours = np.arange(24)
    H = np.column_stack([(o.hh.to_numpy() == h).astype(float) for h in hours[1:]])
    Gm = np.column_stack([o[c].to_numpy().astype(float) for c in groups])
    X = np.column_stack([np.ones(len(o)), Gm, H]); y = o.Rs.to_numpy(float)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    res = {c: (beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(o[c].sum())) for i, c in enumerate(groups)}
    return res, V, G

def sub(lo_, hi_): return tr[(tr.year >= lo_) & (tr.year <= hi_)]

say("## 主表: 時刻 FE 調整 Δμ（β・日クラスタ t）と未調整 Welch")
say("| 窓 | 群 | n 本 / 事象日 | β 時刻FE (日cl t) | MDE 2se | 未調整 Δμ (Welch t) | 群 平均/中央値 | ctrl 平均/中央値 |")
say("|---|---|---|---|---|---|---|---|")
RES = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
    res, V, G = fe_fit(sel, ["ANN", "SJ", "UJ"])
    C = sel[sel.ctrl]
    for gname in ["ANN", "SJ", "UJ"]:
        A = sel[sel[gname]]; b_, se_, n_ = res[gname]; dm, tw = welch(A.Rs, C.Rs)
        nd = A.day.nunique()
        say(f"| {lab} | {gname} | {n_} / {nd} | **{b_:+.3f} ({(b_/se_ if se_>0 else float('nan')):+.2f})** | {2*se_:.3f} | {dm:+.3f} ({tw:+.2f}) | {A.Rs.mean():+.3f}/{A.Rs.median():+.2f} | {C.Rs.mean():+.3f}/{C.Rs.median():+.2f} |")
    # difference ANN - UJ
    cvec = np.zeros(V.shape[0]); cvec[1] = 1; cvec[3] = -1
    dd = res["ANN"][0] - res["UJ"][0]; sd = math.sqrt(max(cvec @ V @ cvec, 0))
    cvec2 = np.zeros(V.shape[0]); cvec2[1] = 1; cvec2[2] = -1
    dd2 = res["ANN"][0] - res["SJ"][0]; sd2 = math.sqrt(max(cvec2 @ V @ cvec2, 0))
    say(f"| {lab} | **ANN − UJ** | | **{dd:+.3f} ({(dd/sd if sd>0 else float('nan')):+.2f})** | {2*sd:.3f} | | ANN − SJ {dd2:+.3f} ({(dd2/sd2 if sd2>0 else float('nan')):+.2f}) | G 日 {G} |")
    RES[lab] = dict(res=res, dANN_UJ=(dd, sd), dANN_SJ=(dd2, sd2))
say("")

# ---------- 判定 ----------
say("## 判定（事前固定・外 2021-26H1・主セル β_UJ）")
ro = RES["外 2021-26H1"]; bU, sU, nU = ro["res"]["UJ"]; bA, sA, nA = ro["res"]["ANN"]; dd, sd = ro["dANN_UJ"]
tU = bU / sU if sU > 0 else float("nan"); tD = dd / sd if sd > 0 else float("nan")
h_gen = (bU > 0) and (tU >= 2) and (bU >= 0.5 * bA)
h_sched = (abs(tU) < 1.5) and (tD >= 2)
verdict = "H_GEN PASS（ジャンプ一般）" if h_gen else ("H_SCHED PASS（予定公表固有）" if h_sched else "inconclusive")
say(f"- 外: β_UJ {bU:+.3f} (t {tU:+.2f}・n {nU}・MDE {2*sU:.3f})／β_ANN {bA:+.3f} (t {bA/sA:+.2f}・n {nA})／ANN−UJ {dd:+.3f} (t {tD:+.2f}・MDE {2*sd:.3f})")
say(f"- **判定: {verdict}**  [H_GEN 条件 β_UJ>0 ∧ t≥2 ∧ β_UJ≥0.5β_ANN → {h_gen} / H_SCHED 条件 |t_UJ|<1.5 ∧ t(ANN−UJ)≥2 → {h_sched}]")
bS, sS, nS = ro["res"]["SJ"]
say(f"- 副 SJ（他の定時公表の代理）外: β_SJ {bS:+.3f} (t {bS/sS if sS>0 else float('nan'):+.2f}・n {nS})・ANN−SJ {ro['dANN_SJ'][0]:+.3f} (t {ro['dANN_SJ'][0]/ro['dANN_SJ'][1] if ro['dANN_SJ'][1]>0 else float('nan'):+.2f})")
say("")

# ---------- 副: 用量反応（UJ z 三分位） ----------
say("## 副① 用量反応 ㊾: UJ の z 三分位別 β（時刻 FE・日クラスタ）")
say("| 窓 | T1 (小) n/β(t)/z 範囲 | T2 n/β(t) | T3 (大) n/β(t)/z 範囲 |")
say("|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); U = o[o.UJ]
    if len(U) < 15: say(f"| {lab} | n 不足 ({len(U)}) | | |"); continue
    q = U.uj_z.quantile([1/3, 2/3]).to_numpy()
    o = o.assign(T1=o.UJ & (o.uj_z <= q[0]), T2=o.UJ & (o.uj_z > q[0]) & (o.uj_z <= q[1]), T3=o.UJ & (o.uj_z > q[1]))
    sel = o[o.T1 | o.T2 | o.T3 | o.ctrl]
    res, V, G = fe_fit(sel, ["T1", "T2", "T3"])
    f = lambda k: f"{res[k][2]}/{res[k][0]:+.3f}({res[k][0]/res[k][1] if res[k][1]>0 else float('nan'):+.2f})"
    say(f"| {lab} | {f('T1')} z≤{q[0]:.1f} | {f('T2')} | {f('T3')} z>{q[1]:.1f} |")
say("")

# ---------- 副② 側×ジャンプ方向 ----------
say("## 副② 側 × ジャンプ方向（整合 = 本の側がジャンプの符号と同じ）: β（時刻 FE・日クラスタ）")
say("| 窓 | ANN 整合 n/β(t) | ANN 逆行 n/β(t) | UJ 整合 n/β(t) | UJ 逆行 n/β(t) |")
say("|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    o = o.assign(A_al=o.ANN & (np.sign(o.ann_r) == o.sgn), A_ag=o.ANN & (np.sign(o.ann_r) == -o.sgn),
                 U_al=o.UJ & (np.sign(o.uj_r) == o.sgn), U_ag=o.UJ & (np.sign(o.uj_r) == -o.sgn))
    sel = o[o.A_al | o.A_ag | o.U_al | o.U_ag | o.ctrl]
    res, V, G = fe_fit(sel, ["A_al", "A_ag", "U_al", "U_ag"])
    f = lambda k: f"{res[k][2]}/{res[k][0]:+.3f}({res[k][0]/res[k][1] if res[k][1]>0 else float('nan'):+.2f})"
    say(f"| {lab} | {f('A_al')} | {f('A_ag')} | {f('U_al')} | {f('U_ag')} |")
say("")

# ---------- 副⑦ 経過分 ----------
say("## 副⑦ 事象後の経過分別 β（0-60／60-120／120-240 分・時刻 FE・日クラスタ）")
say("| 窓 | 群 | 0-60 n/β(t) | 60-120 n/β(t) | 120-240 n/β(t) |")
say("|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    for gname, mcol in [("ANN", "ann_min"), ("UJ", "uj_min")]:
        m = o[mcol]
        o2 = o.assign(K1=o[gname] & (m < 60), K2=o[gname] & (m >= 60) & (m < 120), K3=o[gname] & (m >= 120))
        sel = o2[o2.K1 | o2.K2 | o2.K3 | o2.ctrl]
        res, V, G = fe_fit(sel, ["K1", "K2", "K3"])
        f = lambda k: f"{res[k][2]}/{res[k][0]:+.3f}({res[k][0]/res[k][1] if res[k][1]>0 else float('nan'):+.2f})"
        say(f"| {lab} | {gname} | {f('K1')} | {f('K2')} | {f('K3')} |")
say("")

# ---------- 副③ プラセボ（UJ t0 ±7 日） ----------
say("## 副③ プラセボ: UJ の t0 を ±7 日ずらした偽事象（実事象日・4σ ジャンプ窓は除外）")
say("| シフト | 在 n/β(t) | 外 n/β(t) | 近年 n/β(t) |")
say("|---|---|---|---|")
for sh in (-7, 7):
    mp, _ = inwin(tsf[UJ5] + 300 + sh * 86400.0)
    tr["PL"] = mp & ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
    cells = []
    for lab, lo_, hi_ in ERAS:
        o = sub(lo_, hi_); o = o.assign(ctrl2=o.ctrl & ~o.PL)
        sel = o[o.PL | o.ctrl2]
        if sel.PL.sum() < 10: cells.append(f"{int(sel.PL.sum())}/—"); continue
        res, V, G = fe_fit(sel, ["PL"])
        cells.append(f"{res['PL'][2]}/{res['PL'][0]:+.3f}({res['PL'][0]/res['PL'][1] if res['PL'][1]>0 else float('nan'):+.2f})")
    say(f"| {sh:+d} 日 | {cells[0]} | {cells[1]} | {cells[2]} |")
say("")

# ---------- 副④ look-ahead 陽性対照 x0・幾何 ----------
say("## 副④ look-ahead 陽性対照 x0（建玉足・㉚）と幾何（atr・risk）の群差（外）")
o = sub(2021, 2026); C = o[o.ctrl]
for gname in ["ANN", "SJ", "UJ"]:
    A = o[o[gname]]
    if len(A) < 5: continue
    dx, tx = welch(A.x0, C.x0) if "x0" in o.columns else (np.nan, np.nan)
    say(f"- {gname}: x0 Δ {dx:+.3f} (t {tx:+.2f})・atr 平均 {A.atr.mean():.2f} vs ctrl {C.atr.mean():.2f}・risk {A.risk.mean():.2f} vs {C.risk.mean():.2f}・b {A.b.mean():.2f} vs {C.b.mean():.2f}・TP 率 {(A.exit=='TP').mean()*100:.0f}% vs {(C.exit=='TP').mean()*100:.0f}%・hold 中央値 {A.hold.median():.0f} vs {C.hold.median():.0f}")
say("")

# ---------- 副⑤ 感度 4σ／6σ ----------
say("## 副⑤ 感度: ジャンプ閾値 4σ／6σ（UJ・SJ 再定義・ctrl は同じ）")
say("| 閾値 | 窓 | SJ 事象/n/β(t) | UJ 事象/n/β(t) | ANN−UJ (t) |")
say("|---|---|---|---|---|")
for zt in ZSENS:
    SJx, UJx = classify(J[zt])
    msj, _ = inwin(tsf[SJx] + 300); muj, _ = inwin(tsf[UJx] + 300)
    tr["SJx"] = msj & ~tr.ANN & ~tr.isevday; tr["UJx"] = muj & ~tr.ANN & ~tr.isevday
    for lab, lo_, hi_ in ERAS:
        o = sub(lo_, hi_); o = o.assign(ctrlx=o.ctrl & ~o.SJx & ~o.UJx)
        sel = o[o.ANN | o.SJx | o.UJx | o.ctrlx]
        res, V, G = fe_fit(sel, ["ANN", "SJx", "UJx"])
        cv = np.zeros(V.shape[0]); cv[1] = 1; cv[3] = -1
        dd_ = res["ANN"][0] - res["UJx"][0]; sd_ = math.sqrt(max(cv @ V @ cv, 0))
        ne_s = int(((yrs[SJx] >= lo_) & (yrs[SJx] <= hi_)).sum()); ne_u = int(((yrs[UJx] >= lo_) & (yrs[UJx] <= hi_)).sum())
        say(f"| {zt:.0f}σ | {lab} | {ne_s}/{res['SJx'][2]}/{res['SJx'][0]:+.3f}({res['SJx'][0]/res['SJx'][1] if res['SJx'][1]>0 else float('nan'):+.2f}) | "
            f"{ne_u}/{res['UJx'][2]}/{res['UJx'][0]:+.3f}({res['UJx'][0]/res['UJx'][1] if res['UJx'][1]>0 else float('nan'):+.2f}) | {dd_:+.3f} ({dd_/sd_ if sd_>0 else float('nan'):+.2f}) |")
say("")

# ---------- 補助: 裾依存・年別 ----------
say("## 補助: UJ 外の裾依存・年別")
o = sub(2021, 2026); U = o[o.UJ]; C = o[o.ctrl]
if len(U) >= 10:
    srt = U.Rs.sort_values(ascending=False)
    for k in (1, 3, 5):
        a3 = U.drop(srt.index[:k]); dm, t = welch(a3.Rs, C.Rs)
        say(f"- UJ 上位 {k} 本除去: 未調整 Δμ {dm:+.3f} (t {t:+.2f})")
    say("- UJ 年別 未調整 Δμ (n): " + " ".join(f"{y}:{welch(U[U.year==y].Rs, C[C.year==y].Rs)[0]:+.2f}({int((U.year==y).sum())})" for y in range(2021, 2027) if (U.year == y).sum() >= 3))
    say("- ANN 年別 未調整 Δμ (n): " + " ".join(f"{y}:{welch(o[o.ANN & (o.year==y)].Rs, C[C.year==y].Rs)[0]:+.2f}({int((o.ANN & (o.year==y)).sum())})" for y in range(2021, 2027) if (o.ANN & (o.year == y)).sum() >= 3))
# ---------- 再利用キャッシュ: declustered 5σ ジャンプ事象（SJ/UJ/発表日ジャンプの区別つき） ----------
ji = J[ZMAIN]
jc = pd.DataFrame({"ts": ts[ji], "utc": pd.to_datetime(ts[ji], unit="s").strftime("%Y-%m-%d %H:%M"),
                   "et_date": etdate[ji].strftime("%Y-%m-%d"), "et_hour": hr[ji], "et_min": mn[ji], "wd": wd[ji],
                   "r_bp": np.round(r[ji], 2), "z": np.round(z[ji], 2), "sigma_bp": np.round(sig[ji], 2),
                   "evday": np.asarray(isevbar[ji]).astype(int), "sched_slot": (mn[ji] % 15 == 0).astype(int)})
jc["cls"] = np.where(jc.evday == 1, "EVDAY", np.where(jc.sched_slot == 1, "SJ", "UJ"))
JC = os.path.join(DATA, "c45_jumps_5sigma_declustered.csv"); jc.to_csv(JC, index=False, encoding="utf-8")
say(f"- 再利用キャッシュ保存: {os.path.relpath(JC, ROOT)}（{len(jc)} 事象・列 ts/utc/et_date/et_hour/et_min/wd/r_bp/z/sigma_bp/evday/sched_slot/cls）")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
