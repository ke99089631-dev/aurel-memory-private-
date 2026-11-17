# -*- coding: utf-8 -*-
"""
[REFUTE / 2026-11-17 21:30 反証レーン] 対象 = cycle46 (18:35) の**読み**と、レーン唯一の正の持ち越し β_ANN。

c46 の判定は事前規則どおり **inconclusive** なので「判定を壊す」余地は無い。壊す対象は c46 が判定の外で書いた
**読み**（findings の「得た知識 (1)(2)」）と、その読みが依存している **β_ANN = +0.511（外 2021-26H1・t 4.01・n 138）**:
  c46 の読み: 「予定された公表時刻の後 0〜4 h という時計は第 3 の定時公表 CPI には移らない（ANN−CPI +0.368 t 2.23・
             CPI は ANN の 28%・±7 日プラセボと同大）。よって残る記述は『NFP/FOMC の後 0〜4 h』であり
             『予定公表一般』ではない。*予定性* も機構の軸から外す。」
  c46 自身が未実施と申告した穴: (ii) 差 ANN−CPI の帰無 sd 未校正、(iii) 高ボラ日一致プラセボ（方法論 52）未実施。

本反証の中心仮説（c46 も c45 も c44 も一度も検定していない代替説明）=
  **H_DOW「効いているのは『予定公表の時計』ではなく『2021+ の金における曜日 × 日内時刻のセル』」**。
  NFP は **ほぼ常に金曜** 08:30 ET → 窓 = 金 08:30-12:30。FOMC 公表は **ほぼ常に水曜** 14:00 ET → 窓 = 水 14:00-18:00。
  一方 CPI は火〜金に散る（暦 火 47／水 56／木 48／金 40）。
  ⇒ もし 2021+ の金 scan が「金曜午前」「水曜午後」のセルで強いだけなら、(a) ANN は自動的に強く、
    (b) CPI は曜日が薄まる分だけ弱くなり、**ANN − CPI = +0.37 は機構でなく曜日組成の算術**になる。
  c44 反証 09:30 R3 は *時刻* 一致（hour-matched +0.484）まで。c46 副⑤ は *加法* 曜日 FE（+0.519）まで。
  **曜日 × 時刻の交互作用（セル一致）は誰も取っていない**。本レーンは c36（曜日）・c43 反証（W-FRI 金曜 15:30→月曜
  外 β +1.84 t 2.70）で「2021+ の金に金曜固有の何か」を既に見ているので、代替説明として最有力。

=== 事前固定（数字を見る前・この docstring が正本） ===
データ: data/macro/XAU_m5_close.npz・data/refute_c4_scan_paths_2010_2026.json（c4 凍結 19404 本）・
      data/macro/CPI_dates.csv・FOMC_dates.csv・NFP = c24 v2 規則。scan 無し・M5 読込なし・MT5 無し・外部通信無し・発注無し。
R* = R + (FEED_TOL/risk)·1{SL,TP}。窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括は使わない）。
腕: ANN／CPI／ctrl は c46 と**完全同一**（ANN = NFP 08:30 ／FOMC scheduled 2013-03-20+ 14:00 の [t0,t0+4h)、
   CPI = CPI 公表日 08:30 の同窓で ANN と排反、ctrl = 非発表日 ∧ 月〜金 ∧ 4σ ジャンプ後 4h でない本）。
推定: 既定は Rs ~ 腕 + ET 時刻 FE(24)・建玉日クラスタ se（c46 と同一）。差の se はクラスタ共分散から。

**破壊規則（先に宣言・ひとつでも当たれば c46 の読みは broken）**
R1 複製（判定なし）: β_ANN・β_CPI・ANN−CPI が c46 と一致するか。
R2 **BREAK-DOW（本命）** 曜日 × 時刻セル一致:
   セル = (ET 曜日, ET 時). 処置腕のセル集合に限定し、**処置本と ctrl 本が両方 1 本以上あるセルだけ**残して
   セル FE で推定（＝曜日 × 時刻の完全一致内比較）。方法論 51 に従い **点推定の変化と se の変化を分解して併記**。
   - **BREAK-DOW** = β_ANN(セル一致・外) < 0.5 × β_ANN(時刻 FE・外)（＝点推定が半分未満。主判定は点推定・t は併記）。
   - R2b CPI を曜日で割る: **BREAK-DOW2** = β_CPI_FRI ≥ 0.5·β_ANN ∧ t_CPI_FRI ≥ 1.5
     （＝金曜の CPI は ANN 級＝「CPI に移らない」は曜日組成の人工物）。
   - R2c 公表と無関係な純曜日プラセボ: FRI_AM = **非発表**金曜の時 8-12 の本／WED_PM = **非発表**水曜の時 14-17 の本、
     各 vs 残りの ctrl・時刻 FE。**BREAK-DOW3** = いずれかが β ≥ 0.5·β_ANN(+0.255) ∧ t ≥ 2。
   - R2d ANN を NFP／FOMC に割り、各々を自分の曜日 × 時刻セルに一致させる（記述・DOW の内訳）。
R3 **BREAK-DIFFCAL**（c46 の穴 (ii)）: 偽 CPI（c46 と同じ曜日一致・非発表平日・08:30・NFAKE 回）で
   **t(β_ANN − β_偽CPI) の帰無分布**を取る。**BREAK-DIFFCAL** = 実測 t(ANN−CPI) の片側経験 p > 0.025。
R4 **BREAK-VOL**（c46 の穴 (iii)・方法論 52）: 偽 CPI を **曜日 × 当日実現ボラ五分位**で一致させて抽出（NFAKE 回）。
   - **BREAK-VOL-A** = この帰無の下で実測 t(β_CPI) の片側経験 p < 0.025（＝CPI 腕は本物で c46 の「移らない」が壊れる）。
   - **BREAK-VOL-B** = 偽 β の平均 ≥ +0.100（＝c46 が校正に使った曜日一致だけの偽集合は基準線を過小評価＝
     c46 の「得た知識 (3)（帰無 sd は名目 1.0 に乗る）」が集合の作り方で崩れる）。
R5 **BREAK-SPLIT**: CPI 腕の在/外境界を 11 通りに取り直す（境界 2019/2022/2023・LOYO 2021-26 の 6 本・公表回の奇偶）。
   **BREAK-SPLIT** = 3 本以上で β_CPI ≥ 0.5·β_ANN(同一分割) ∧ t_CPI ≥ 1.5。
R6 **BREAK-COST**: k·TRIG_SPREAD/risk を全腕から引く（k=1,2,3）。**BREAK-COST** = k=3 で ANN−CPI < +0.18。
R7 **BREAK-EVENTUNIT**: 事象日単位（1 日 1 観測）の ANN 日平均 vs CPI 日平均。
   **BREAK-EVENTUNIT** = Mann-Whitney 片側 p > 0.05、または ANN 上位 3 日除去後の差 < +0.18。
R8（記述・判定に使わない）: family 定義の算術（反証 09:30 (c)）。findings の判定セル数を機械集計し、
   経験 p 5.9e-4（09:30 C1）が Bonferroni で死ぬ K を印字。
survived = R2〜R7 の BREAK がひとつも当たらない。

事前の自己反証: (i) R2 のセル一致は対照プールを激減させる＝se が機械的に膨らむ（方法論 51）。だから主判定を
   **点推定**に置き、se 変化を分解して印字する。(ii) R2b の CPI_FRI は外で ~15 公表日・~25 本＝検出力が無く、
   BREAK-DOW2 が不発でも「CPI_FRI は弱い」とは言えない（MDE を印字する）。(iii) 曜日 × 時刻セル FE は
   「2021+ の金曜午前が良い」と「発表機構」が同じセルに同居するので、**H_DOW を支持する結果が出ても
   『発表機構でない』ことの証明にはならない**（分離には非発表金曜の検出力が必要＝R2c がその脚）。
   (iv) 構成依存（c4 凍結 1 構成・Dukascopy bid 1 社・CFD）は本サイクルでも未分離・継承。
seed 20261117・NFAKE 400。出力 data/refute_c46_cpi_clock.md。読取専用・発注なし・本番編集なし・書込は AUREL_RESEARCH 配下のみ。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c46_cpi_clock.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0; NFAKE = 400
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

say("# [REFUTE 2026-11-17 21:30] c46 の読みと β_ANN を H_DOW（曜日 × 日内時刻）で壊す")
say(f"- 事前固定は docstring・seed {SEED}・NFAKE {NFAKE}・破壊規則 BREAK-DOW/DOW2/DOW3/DIFFCAL/VOL-A/VOL-B/SPLIT/COST/EVENTUNIT")
say("")

# ---------- 暦（c46 と同一） ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI_ALL = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
nfp_fomc_days = set(list(NFP.normalize()) + list(FOMC_ALL.normalize()))
CPI = pd.DatetimeIndex([d for d in CPI_ALL if d.normalize() not in nfp_fomc_days])
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0); t_cpi = epoch_et(CPI, 8, 30)
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI_ALL.normalize()))))
cpi_y = CPI.year

say("## 暦の曜日組成（H_DOW の前提の確認）")
say("| 系列 | n | 月 | 火 | 水 | 木 | 金 |")
say("|---|---|---|---|---|---|---|")
for nm, D in (("NFP (08:30)", NFP), ("FOMC scheduled (14:00)", FOMC_ANN), ("CPI 腕 (08:30)", CPI)):
    say(f"| {nm} | {len(D)} | " + " | ".join(str(int((D.weekday == w).sum())) for w in range(5)) + " |")
say("")

# ---------- npz・ジャンプ検出（c45/c46 と同一） ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
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

J4 = decluster(cand & (z >= 4.0))

# 当日実現ボラ（R4 のマッチ用・ET 日ごとの M5 |r| RMS）
dv = pd.DataFrame({"d": etdate[nf], "r2": r[nf] ** 2}).groupby("d").agg(rms=("r2", lambda x: math.sqrt(float(np.mean(x)))), n=("r2", "size"))
dv = dv[dv.n >= 100]
day_vol = dv["rms"]
say(f"- 日次実現ボラ（M5 |r| RMS・bp）: {len(day_vol)} 日・中位 {day_vol.median():.1f} bp（R4 の一致次元）")

# ---------- scan 本（c46 と同一） ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; TS_ = d["frozen"]["TRIG_SPREAD"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)
tr["cell"] = tr.wd * 24 + tr.hh

def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    if len(t0s) == 0: return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, p_nfp = inwin(t_nfp); m_fomc, p_fomc = inwin(t_fomc); m_cpi, p_cpi = inwin(t_cpi)
tr["NFPw"] = m_nfp; tr["FOMCw"] = m_fomc & ~m_nfp
tr["ANN"] = m_nfp | m_fomc
tr["CPI"] = m_cpi & ~tr.ANN
tsf = ts.astype(float)
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
tr["cost1"] = TS_ / tr.risk
say(f"- scan 本 {len(tr)}・FEED_TOL {FT}・TRIG_SPREAD {TS_}")
say(f"- 本数: ANN {int(tr.ANN.sum())}（NFP窓 {int(tr.NFPw.sum())}／FOMC窓 {int(tr.FOMCw.sum())}）・CPI {int(tr.CPI.sum())}・ctrl {int(tr.ctrl.sum())}")
say("")

ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

# ---------- 推定器（c46 と同一） ----------
def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    Xe = X * e[:, None]
    codes, uniq = pd.factorize(np.asarray(g))
    S = np.zeros((len(uniq), X.shape[1])); np.add.at(S, codes, Xe); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def fit(o, groups, fe="hour", ycol="Rs"):
    """fe='hour' = ET 時刻 FE(24)・fe='cell' = (曜日 × 時刻) セル FE・fe=None = 定数のみ"""
    if fe == "hour":
        lv = sorted(set(o.hh.to_numpy().tolist())); M = o.hh.to_numpy()
    elif fe == "cell":
        lv = sorted(set(o.cell.to_numpy().tolist())); M = o.cell.to_numpy()
    else:
        lv = []; M = None
    cols = [np.ones(len(o))]
    Gm = np.column_stack([o[c].to_numpy().astype(float) for c in groups]); cols.append(Gm)
    if len(lv) > 1:
        cols.append(np.column_stack([(M == v).astype(float) for v in lv[1:]]))
    X = np.column_stack(cols); y = o[ycol].to_numpy(float)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    res = {c: (beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(o[c].sum())) for i, c in enumerate(groups)}
    return res, V, G

def contrast(V, res, a, b, groups):
    ia = groups.index(a) + 1; ib = groups.index(b) + 1
    c = np.zeros(V.shape[0]); c[ia] = 1; c[ib] = -1
    dd = res[a][0] - res[b][0]; sd = math.sqrt(max(c @ V @ c, 0))
    return dd, sd

def tstr(b, s): return f"{b:+.3f} ({(b/s if s and s>0 else float('nan')):+.2f})"
def sub(lo_, hi_): return tr[(tr.year >= lo_) & (tr.year <= hi_)]

# =====================================================================
say("## R1 複製（c46 主表の再現・時刻 FE・日クラスタ）")
say("| 窓 | β_ANN (t・n) | β_CPI (t・n・MDE) | ANN − CPI (t) |")
say("|---|---|---|---|")
RAW = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.CPI | o.ctrl]
    res, V, G = fit(sel, ["ANN", "CPI"], fe="hour")
    dd, sd = contrast(V, res, "ANN", "CPI", ["ANN", "CPI"])
    bA, sA, nA = res["ANN"]; bC, sC, nC = res["CPI"]
    say(f"| {lab} | {tstr(bA,sA)} n {nA} | {tstr(bC,sC)} n {nC}・MDE {2*sC:.3f} | **{tstr(dd,sd)}** |")
    RAW[lab] = dict(A=(bA, sA, nA), C=(bC, sC, nC), d=(dd, sd), G=G)
say("")
bANN_out = RAW["外 2021-26H1"]["A"][0]
THR = 0.5 * bANN_out
say(f"- 以降の閾値: 0.5·β_ANN(外) = **{THR:+.3f}**・実測 t(ANN−CPI) 外 = {RAW['外 2021-26H1']['d'][0]/RAW['外 2021-26H1']['d'][1]:+.2f}")
say("")

# =====================================================================
say("## R2 BREAK-DOW（本命）: 曜日 × 日内時刻セル一致")
say("### R2a ANN を (曜日 × 時) セル FE で測る（方法論 51 に従い 点推定 と se を分解）")
say("| 窓 | 時刻FE β_ANN (t) | セル一致 β_ANN (t) | 点推定 比 | se 比 | 処置本 | ctrl 本 (時刻FE→セル一致) | 使ったセル数 |")
say("|---|---|---|---|---|---|---|---|")
DOW = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    base = o[o.ANN | o.ctrl]
    res0, V0, _ = fit(base, ["ANN"], fe="hour")
    b0, s0, n0 = res0["ANN"]
    tcells = set(base.loc[base.ANN, "cell"].unique().tolist())
    ccells = set(base.loc[base.ctrl, "cell"].unique().tolist())
    keep = tcells & ccells
    m = base[base.cell.isin(keep)]
    res1, V1, G1 = fit(m, ["ANN"], fe="cell")
    b1, s1, n1 = res1["ANN"]
    say(f"| {lab} | {tstr(b0,s0)} | **{tstr(b1,s1)}** | {b1/b0 if b0 else float('nan'):.2f} | {s1/s0 if s0 else float('nan'):.2f} | {n1} | {int(base.ctrl.sum())}→{int(m.ctrl.sum())} | {len(keep)} |")
    DOW[lab] = (b0, s0, b1, s1, n1)
b1_out = DOW["外 2021-26H1"][2]; s1_out = DOW["外 2021-26H1"][3]
BREAK_DOW = b1_out < THR
say(f"- **BREAK-DOW**（β_ANN セル一致 < {THR:+.3f}）→ **{BREAK_DOW}**（セル一致 {b1_out:+.3f}・t {b1_out/s1_out:+.2f}）")
say("")

say("### R2b CPI を曜日で割る（金曜 CPI は NFP と同じ 金 08:30 セル）")
say("| 窓 | CPI_FRI n/β(t)/MDE | CPI_OTH n/β(t) | 0.5·β_ANN |")
say("|---|---|---|---|")
BREAK_DOW2 = False
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    o = o.assign(CFRI=o.CPI & (o.wd == 4), COTH=o.CPI & (o.wd != 4))
    sel = o[o.ANN | o.CFRI | o.COTH | o.ctrl]
    res, V, G = fit(sel, ["ANN", "CFRI", "COTH"], fe="hour")
    bf, sf, nf_ = res["CFRI"]; bo, so, no_ = res["COTH"]
    thr = 0.5 * res["ANN"][0]
    say(f"| {lab} | {nf_}/{tstr(bf,sf)}/{2*sf:.3f} | {no_}/{tstr(bo,so)} | {thr:+.3f} |")
    if lab == "外 2021-26H1":
        BREAK_DOW2 = (bf >= thr) and (sf > 0) and (bf / sf >= 1.5)
        cfri_out = (bf, sf, nf_)
say(f"- **BREAK-DOW2**（外 β_CPI_FRI ≥ 0.5·β_ANN ∧ t ≥ 1.5）→ **{BREAK_DOW2}**")
say("")

say("### R2c 純曜日プラセボ: **非発表日**の 金 08-12 時／水 14-17 時（公表は一切関与しない）")
say("| 窓 | FRI_AM n/β(t)/MDE | WED_PM n/β(t)/MDE | 閾値 0.5·β_ANN |")
say("|---|---|---|---|")
BREAK_DOW3 = False
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    c0 = o.ctrl.to_numpy()
    fa = c0 & (o.wd.to_numpy() == 4) & np.isin(o.hh.to_numpy(), [8, 9, 10, 11, 12])
    wp = c0 & (o.wd.to_numpy() == 2) & np.isin(o.hh.to_numpy(), [14, 15, 16, 17])
    o = o.assign(FRI_AM=fa, WED_PM=wp, ctrl2=c0 & ~fa & ~wp)
    sel = o[o.FRI_AM | o.WED_PM | o.ctrl2]
    res, V, G = fit(sel, ["FRI_AM", "WED_PM"], fe="hour")
    bf, sf, nf_ = res["FRI_AM"]; bw, sw, nw_ = res["WED_PM"]
    thr = 0.5 * RAW[lab]["A"][0]
    say(f"| {lab} | {nf_}/{tstr(bf,sf)}/{2*sf:.3f} | {nw_}/{tstr(bw,sw)}/{2*sw:.3f} | {thr:+.3f} |")
    if lab == "外 2021-26H1":
        BREAK_DOW3 = ((bf >= THR) and sf > 0 and bf / sf >= 2) or ((bw >= THR) and sw > 0 and bw / sw >= 2)
say(f"- **BREAK-DOW3**（非発表の金午前 or 水午後 が β ≥ {THR:+.3f} ∧ t ≥ 2）→ **{BREAK_DOW3}**")
say("")

say("### R2d ANN の内訳（NFP窓／FOMC窓）を各々の曜日 × 時刻セルに一致させる（記述）")
say("| 窓 | 腕 | 時刻FE β(t・n) | セル一致 β(t・n) | 点推定比 | se比 |")
say("|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    for arm in ("NFPw", "FOMCw"):
        o = sub(lo_, hi_)
        base = o[o[arm] | o.ctrl]
        if base[arm].sum() < 10:
            say(f"| {lab} | {arm} | n {int(base[arm].sum())} 不足 | | | |"); continue
        r0, V0, _ = fit(base, [arm], fe="hour"); b0, s0, n0 = r0[arm]
        keep = set(base.loc[base[arm], "cell"].unique()) & set(base.loc[base.ctrl, "cell"].unique())
        m = base[base.cell.isin(keep)]
        r1, V1, _ = fit(m, [arm], fe="cell"); b1, s1, n1 = r1[arm]
        say(f"| {lab} | {arm} | {tstr(b0,s0)} n {n0} | **{tstr(b1,s1)}** n {n1} | {b1/b0 if b0 else float('nan'):.2f} | {s1/s0 if s0 else float('nan'):.2f} |")
say("")

# =====================================================================
say(f"## R3 BREAK-DIFFCAL: 偽 CPI {NFAKE} 回（c46 と同じ曜日一致・非発表平日・08:30）での **差の統計量** の帰無分布")
alldays = pd.DatetimeIndex(sorted(set(etdate[(wd <= 4) & nf])))
nonev = alldays[~alldays.isin(evdays)]
say("| 窓 | 実測 t(ANN−CPI) | 帰無 平均 | 帰無 sd | p97.5 | max | 片側経験 p | 偽 t(β_FK) sd |")
say("|---|---|---|---|---|---|---|---|")
DIFF = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); base = o[o.ANN | o.ctrl].copy()
    dobs, sobs = RAW[lab]["d"]; tobs = dobs / sobs
    pool = nonev[(nonev.year >= lo_) & (nonev.year <= hi_)]
    actual = CPI[(cpi_y >= lo_) & (cpi_y <= hi_)]
    counts = {w: int((actual.weekday == w).sum()) for w in range(5)}
    et_base = base.entry_time.to_numpy(float); annv = base.ANN.to_numpy(); ctrlv = base.ctrl.to_numpy()
    td = []; tfk = []
    for it in range(NFAKE):
        pick = []
        for w, c in counts.items():
            if c == 0: continue
            cw = pool[pool.weekday == w]
            if len(cw) < c: continue
            pick.extend(list(rng.choice(cw, size=c, replace=False)))
        t0s = np.sort(epoch_et(pd.DatetimeIndex(pick), 8, 30))
        pos = np.clip(np.searchsorted(t0s, et_base, side="right") - 1, 0, len(t0s) - 1)
        fm = (et_base >= t0s[pos]) & (et_base < t0s[pos] + SPAN) & ~annv
        base["FK"] = fm; base["ctrl2"] = ctrlv & ~fm
        sel = base[base.ANN | base.FK | base.ctrl2]
        if sel.FK.sum() < 10: continue
        res, V, G = fit(sel, ["ANN", "FK"], fe="hour")
        dd, sd = contrast(V, res, "ANN", "FK", ["ANN", "FK"])
        td.append(dd / sd if sd > 0 else np.nan)
        tfk.append(res["FK"][0] / res["FK"][1] if res["FK"][1] > 0 else np.nan)
    td = np.array(td, float); tfk = np.array(tfk, float)
    p = float(np.nanmean(td >= tobs))
    DIFF[lab] = dict(p=p, sd=float(np.nanstd(td)), tobs=tobs)
    say(f"| {lab} | {tobs:+.2f} | {np.nanmean(td):+.2f} | {np.nanstd(td):.2f} | {np.nanpercentile(td,97.5):+.2f} | {np.nanmax(td):+.2f} | **{p:.4f}** | {np.nanstd(tfk):.2f} |")
BREAK_DIFFCAL = DIFF["外 2021-26H1"]["p"] > 0.025
say(f"- **BREAK-DIFFCAL**（外 片側経験 p > 0.025）→ **{BREAK_DIFFCAL}**（p {DIFF['外 2021-26H1']['p']:.4f}・帰無 sd {DIFF['外 2021-26H1']['sd']:.2f}）")
say("")

# =====================================================================
say(f"## R4 BREAK-VOL: **曜日 × 当日実現ボラ五分位** 一致の偽 CPI {NFAKE} 回（c46 の穴 (iii)・方法論 52）")
say("| 窓 | 実 CPI 日 ボラ中位 | 偽(曜日のみ) ボラ中位 | 偽(曜日×ボラ五分位) ボラ中位 | 実測 t(β_CPI) | 帰無 平均 t | 帰無 sd | 片側経験 p | 偽 β 平均 |")
say("|---|---|---|---|---|---|---|---|---|")
VOL = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); base = o[o.ANN | o.ctrl].copy()
    bC, sC, nC = RAW[lab]["C"]; tobs = bC / sC if sC > 0 else np.nan
    pool = nonev[(nonev.year >= lo_) & (nonev.year <= hi_)]
    pool = pool[pool.isin(day_vol.index)]
    actual = CPI[(cpi_y >= lo_) & (cpi_y <= hi_)]
    actual = actual[actual.isin(day_vol.index)]
    pv = day_vol.reindex(pool); av = day_vol.reindex(actual)
    qs = np.nanpercentile(pv.to_numpy(), [20, 40, 60, 80])
    pq = np.searchsorted(qs, pv.to_numpy(), side="right")
    aq = np.searchsorted(qs, av.to_numpy(), side="right")
    cnt = {}
    for w, q in zip(actual.weekday, aq):
        cnt[(int(w), int(q))] = cnt.get((int(w), int(q)), 0) + 1
    pool_df = pd.DataFrame({"d": pool, "w": pool.weekday, "q": pq})
    et_base = base.entry_time.to_numpy(float); annv = base.ANN.to_numpy(); ctrlv = base.ctrl.to_numpy()
    tf = []; bf = []; vm = []
    for it in range(NFAKE):
        pick = []
        for (w, q), c in cnt.items():
            cw = pool_df[(pool_df.w == w) & (pool_df.q == q)].d.to_numpy()
            if len(cw) == 0: continue
            pick.extend(list(rng.choice(cw, size=min(c, len(cw)), replace=False)))
        if len(pick) < 10: continue
        pk = pd.DatetimeIndex(pick)
        vm.append(float(np.nanmedian(day_vol.reindex(pk).to_numpy())))
        t0s = np.sort(epoch_et(pk, 8, 30))
        pos = np.clip(np.searchsorted(t0s, et_base, side="right") - 1, 0, len(t0s) - 1)
        fm = (et_base >= t0s[pos]) & (et_base < t0s[pos] + SPAN) & ~annv
        base["FK"] = fm; base["ctrl2"] = ctrlv & ~fm
        sel = base[base.ANN | base.FK | base.ctrl2]
        if sel.FK.sum() < 10: continue
        res, V, G = fit(sel, ["ANN", "FK"], fe="hour")
        b_, s_, _ = res["FK"]; tf.append(b_ / s_ if s_ > 0 else np.nan); bf.append(b_)
    tf = np.array(tf, float); bf = np.array(bf, float)
    p = float(np.nanmean(tf >= tobs)) if len(tf) else float("nan")
    # 曜日のみ一致の偽集合のボラ中位（参考）
    vonly = []
    for it in range(50):
        pick = []
        for w in range(5):
            c = int((actual.weekday == w).sum())
            cw = pool[pool.weekday == w]
            if c == 0 or len(cw) < c: continue
            pick.extend(list(rng.choice(cw, size=c, replace=False)))
        if pick: vonly.append(float(np.nanmedian(day_vol.reindex(pd.DatetimeIndex(pick)).to_numpy())))
    VOL[lab] = dict(p=p, bmean=float(np.nanmean(bf)), sd=float(np.nanstd(tf)))
    say(f"| {lab} | {np.nanmedian(av.to_numpy()):.1f} | {np.nanmedian(vonly) if vonly else float('nan'):.1f} | {np.nanmedian(vm) if vm else float('nan'):.1f} | {tobs:+.2f} | {np.nanmean(tf):+.2f} | {np.nanstd(tf):.2f} | **{p:.4f}** | {np.nanmean(bf):+.3f} |")
BREAK_VOL_A = VOL["外 2021-26H1"]["p"] < 0.025
BREAK_VOL_B = VOL["外 2021-26H1"]["bmean"] >= 0.100
say(f"- **BREAK-VOL-A**（ボラ一致帰無で 実測 t(β_CPI) の片側 p < 0.025）→ **{BREAK_VOL_A}**（p {VOL['外 2021-26H1']['p']:.4f}）")
say(f"- **BREAK-VOL-B**（ボラ一致偽 β 平均 ≥ +0.100）→ **{BREAK_VOL_B}**（{VOL['外 2021-26H1']['bmean']:+.3f}）")
say("")

# =====================================================================
say("## R5 BREAK-SPLIT: CPI 腕の在/外分割を 11 通りに取り直す")
say("| 分割 | n_CPI | β_CPI (t) | β_ANN (t) | 0.5·β_ANN | β_CPI ≥ 閾値 ∧ t≥1.5 |")
say("|---|---|---|---|---|---|")
splits = []
for y0 in (2019, 2022, 2023):
    splits.append((f"外 = {y0}-2026", lambda o, y0=y0: (o.year >= y0)))
for yl in range(2021, 2027):
    splits.append((f"LOYO 外 2021-26 除 {yl}", lambda o, yl=yl: (o.year >= 2021) & (o.year <= 2026) & (o.year != yl)))
cpi_rank = pd.Series(np.arange(len(CPI)), index=CPI.normalize())
tr["cpi_idx"] = tr.day.map(cpi_rank)
splits.append(("外 2021-26・公表回 奇数", lambda o: (o.year >= 2021) & (o.year <= 2026) & (~o.CPI | (o.cpi_idx % 2 == 1))))
splits.append(("外 2021-26・公表回 偶数", lambda o: (o.year >= 2021) & (o.year <= 2026) & (~o.CPI | (o.cpi_idx % 2 == 0))))
hits = 0
for nm, fn in splits:
    o = tr[fn(tr)]
    sel = o[o.ANN | o.CPI | o.ctrl]
    if sel.CPI.sum() < 20:
        say(f"| {nm} | {int(sel.CPI.sum())} | n 不足 | | | |"); continue
    res, V, G = fit(sel, ["ANN", "CPI"], fe="hour")
    bC, sC, nC = res["CPI"]; bA, sA, _ = res["ANN"]; thr = 0.5 * bA
    hit = (bC >= thr) and sC > 0 and (bC / sC >= 1.5)
    hits += int(hit)
    say(f"| {nm} | {nC} | {tstr(bC,sC)} | {tstr(bA,sA)} | {thr:+.3f} | {'**YES**' if hit else 'no'} |")
BREAK_SPLIT = hits >= 3
say(f"- **BREAK-SPLIT**（3 本以上が閾値超）→ **{BREAK_SPLIT}**（{hits}/{len(splits)}）")
say("")

# =====================================================================
say("## R6 BREAK-COST: k·TRIG_SPREAD/risk を全腕から引く")
say("| k | β_ANN (t) | β_CPI (t) | ANN − CPI (t) |")
say("|---|---|---|---|")
o = sub(2021, 2026)
dk3 = None
for k in (0, 1, 2, 3):
    oo = o.assign(Rk=o.Rs - k * o.cost1)
    sel = oo[oo.ANN | oo.CPI | oo.ctrl]
    res, V, G = fit(sel, ["ANN", "CPI"], fe="hour", ycol="Rk")
    dd, sd = contrast(V, res, "ANN", "CPI", ["ANN", "CPI"])
    say(f"| {k} | {tstr(*res['ANN'][:2])} | {tstr(*res['CPI'][:2])} | {tstr(dd,sd)} |")
    if k == 3: dk3 = dd
BREAK_COST = dk3 < 0.18
say(f"- **BREAK-COST**（k=3 で ANN−CPI < +0.18）→ **{BREAK_COST}**（{dk3:+.3f}）")
say("")

# =====================================================================
say("## R7 BREAK-EVENTUNIT: 事象日単位（1 日 1 観測）")
def mwu_one_sided(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    allv = np.r_[a, b]; rk = pd.Series(allv).rank().to_numpy()
    n1, n2 = len(a), len(b); R1 = rk[:n1].sum()
    U = R1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0; sdv = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    zv = (U - mu) / sdv if sdv > 0 else np.nan
    from math import erf
    return zv, 1.0 - 0.5 * (1 + erf(zv / math.sqrt(2)))
o = sub(2021, 2026)
dA = o[o.ANN].groupby("day").Rs.mean(); dC = o[o.CPI].groupby("day").Rs.mean(); dK = o[o.ctrl].groupby("day").Rs.mean()
dm = dA.mean() - dC.mean()
se = math.sqrt(dA.var(ddof=1) / len(dA) + dC.var(ddof=1) / len(dC))
zv, pw = mwu_one_sided(dA.to_numpy(), dC.to_numpy())
say(f"- 外: ANN {len(dA)} 日 平均 {dA.mean():+.3f}／中央 {dA.median():+.3f}・CPI {len(dC)} 日 平均 {dC.mean():+.3f}／中央 {dC.median():+.3f}・ctrl {len(dK)} 日 平均 {dK.mean():+.3f}／中央 {dK.median():+.3f}")
say(f"- 日単位 差 ANN−CPI **{dm:+.3f}（Welch t {dm/se:+.2f}）・Mann-Whitney 片側 z {zv:+.2f}・p {pw:.4f}**")
cut = []
for kk in (1, 3, 5):
    keep = dA.sort_values(ascending=False).iloc[kk:]
    cut.append(keep.mean() - dC.mean())
    say(f"- ANN 上位 {kk} 日除去後の差: {keep.mean()-dC.mean():+.3f}（ANN 平均 {keep.mean():+.3f}）")
BREAK_EVENTUNIT = (pw > 0.05) or (cut[1] < 0.18)
say(f"- **BREAK-EVENTUNIT**（MWU 片側 p > 0.05 もしくは 上位3日除去後の差 < +0.18）→ **{BREAK_EVENTUNIT}**（p {pw:.4f}・上位3除去 {cut[1]:+.3f}）")
say("")

# CPI 側の裾（c46 ⑨ の複製）
dCs = o[o.CPI].Rs.sort_values(ascending=False)
say(f"- （参考・c46 ⑨ の複製）CPI 外 {len(dCs)} 本の平均 {dCs.mean():+.3f}・上位1/3/5 本除去で {dCs.iloc[1:].mean():+.3f}／{dCs.iloc[3:].mean():+.3f}／{dCs.iloc[5:].mean():+.3f}")
say("")

# =====================================================================
say("## R8（記述）family 定義の算術")
import glob, re
fcnt = {}
for fp in sorted(glob.glob(os.path.join(ROOT, "findings", "*.md"))):
    txt = open(fp, encoding="utf-8").read()
    fcnt[os.path.basename(fp)] = len(re.findall(r"(?<![A-Za-z])C\d+\s", txt))
ncycle = 46
say(f"- findings 各日の 'C<数字>' 出現数（判定セル表記の粗い代理）: " + "・".join(f"{k[:10]} {v}" for k, v in fcnt.items()))
pemp = 5.9e-4
say(f"- 09:30 反証の条件づけ経験 p = {pemp:.1e}（ゲート通過 ∧ 在 null に条件づけ）。Bonferroni で 0.05 を割る K = **{int(0.05/pemp)}**")
say(f"- サイクル数 {ncycle}・1 サイクル 1 判定セルなら K={ncycle} → 補正後 p {pemp*ncycle:.4f}（生存）・1 サイクル 2 セルなら K={2*ncycle} → {pemp*2*ncycle:.4f}（生存）・1 サイクル 3 セルなら K={3*ncycle} → {pemp*3*ncycle:.4f}（{'死亡' if pemp*3*ncycle>0.05 else '生存'}）")
say("")

# =====================================================================
say("## 判定")
rules = [("BREAK-DOW", BREAK_DOW), ("BREAK-DOW2", BREAK_DOW2), ("BREAK-DOW3", BREAK_DOW3),
         ("BREAK-DIFFCAL", BREAK_DIFFCAL), ("BREAK-VOL-A", BREAK_VOL_A), ("BREAK-VOL-B", BREAK_VOL_B),
         ("BREAK-SPLIT", BREAK_SPLIT), ("BREAK-COST", BREAK_COST), ("BREAK-EVENTUNIT", BREAK_EVENTUNIT)]
landed = [n for n, v in rules if v]
say("| 破壊規則 | 結果 |")
say("|---|---|")
for n, v in rules:
    say(f"| {n} | {'☠ **当たった**' if v else '★ 不発'} |")
say("")
say(f"- 当たった破壊規則: **{landed if landed else 'なし'}**")
say(f"- **判定: {'broken（c46 の読み／β_ANN のどちらかが落ちた）' if landed else 'survived（9 規則すべて不発）'}**")
say(f"- 実行時間 {time.time()-T0:.1f} s")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
