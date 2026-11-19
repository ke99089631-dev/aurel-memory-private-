# -*- coding: utf-8 -*-
"""
[cycle56 研究レーン / 2026-11-20 06:35]【深化・発表プール・機構判別】
c45（11-17）の「予定外ジャンプ UJ」腕は、c55（本日 01:05）＋反証 04:10 で
  「UJ 937 事象の 19.2% が COMEX 08:20–08:25 ET と NYSE 09:35–09:40 ET の 4 スロットに局在（濃縮 5.8〜8.7×・decluster 無しでも 15%）＝
   trailing σ 検出器が米国朝の日内ボラ段差（予定時刻・情報なし・高ボラ）を『5σ 予定外』として拾ったもの」
と判明した。c45 の H_SCHED（予定公表固有）は反証 15:40 で inconclusive（腕の非対称 BREAK-A・雑音通過率 BREAK-D2）。
本サイクルは backlog（c55 次の枝 (a)・反証 04:10 次の枝 (a) = 2 スロット版）を実行する:
  UJ を UJ_US2（事象足の ET (時,分) ∈ {(8,20),(8,25),(9,35),(9,40)}）と UJ_oth（その他）に分け、scan 本の β を c45 と同一の推定器で印字する。

問い: (Q1) 「予定された時刻の vol 段差」だけで建玉後 0〜4 h の本は走るか（ANN の +0.5R は『予定性』か『情報公表』か）。
      (Q2) 汚染を除いた純予定外腕 UJ_oth は ANN と同等性の方向で区別できるか（方法論 55: 非棄却でなく TOST 方向）。

=== 事前固定（数字を見る前・この docstring が正本・seed 20261120・乱数は未使用） ===
データ: data/macro/XAU_m5_close.npz（bid）／data/refute_c4_scan_paths_2010_2026.json（c4 凍結 19404 本）／data/macro/FOMC_dates.csv／CPI_dates.csv／NFP = c24 v2 規則。
      c45 と同一コード（σ_trail 5520 足・5σ・4 h decluster・SJ/UJ 分規則・窓 [t0+300, t0+300+14400)・ctrl = 非発表日 ∧ 月〜金 ∧ 4σ 後 4h 外 ∧ 非 ANN）。
      scan 無し・M5 原本読込なし・MT5 無し・外部通信無し。R* = R + (FEED_TOL/risk)·1{SL,TP}。窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括は使わない）。
複製 assert（走る前に宣言）: declustered 5σ 2166・SJ 786・UJ 937・外 ANN n 138 β +0.514・外 UJ n 280 β +0.089（c45 result md と 3 桁一致しなければ停止）。
腕: ANN（不変）・SJ（不変）・UJ_US2・UJ_oth。推定 Rs ~ 1{ANN}+1{SJ}+1{UJ_US2}+1{UJ_oth}+ET 時刻 FE（24）、建玉日クラスタ se。
判定窓 = 外 2021-26H1（ANN 信号の所在・c45 と同じ理由）。在・近年は印字。条件は 1 行ずつ独立印字し判定語は boolean から合成（方法論候補 72/75）。
  H_STEP（予定時刻の段差だけで走る）PASS = β_US2 > 0 ∧ t(β_US2) ≥ 2 ∧ β_US2 ≥ 0.5·β_ANN。
     予測（事前）: 不成立（β_US2 ≈ 0）。決着可能性: 外 UJ_US2 本は ≈280×0.19 ≈ 55・事象日 ≈40 → se ≈ 0.158·√(67/40) ≈ 0.20・MDE ≈ 0.41R。
     **MDE_US2 > 0.5·β_ANN（≈0.26）なら H_STEP は「検出力不足（underpowered）」と宣言し PASS/FAIL を言わない**（方法論 61）。
  H_PURE（純予定外腕は ANN と別）: (a) |t(β_oth)| < 1.5 ／(b) t(β_ANN − β_oth) ≥ 2 ／(c) β_oth + 2·se_oth < 0.5·β_ANN（同等性の方向・TOST 片側 97.5%）。
     PASS = (a)∧(b)∧(c)。(a) は雑音通過率 70〜87% の弱い脚（反証 15:40 BREAK-D2）→ 内容は (c)。(c) 不成立なら inconclusive（c45 と同じ）。
     予測（事前）: (b)(c) 成立の見込み（c45 UJ 全体で β 上限 +0.252 vs 閾 +0.257＝紙一重。汚染 55 本を抜いた se はやや大きくなる）。
  差 β_US2 − β_oth（汚染部分が残りと違うか）はクラスタ共分散から t を印字（記述）。
副（記述）: ①US2 を 08:20/08:25（08:30 公表前）と 09:35/09:40（NYSE 開場後）に分けた β ②プラセボ: US2・oth の t0 を ±7 日ずらした偽事象 ③x0 look-ahead 陽性対照の群差（㉚）と幾何（atr/risk/b/TP 率）
   ④経過分 0-60/60-120/120-240（US2・oth）⑤感度 4σ/6σ（同じ 4 スロットで分割）⑥US2 事象の曜日分布（木曜 = 新規失業保険申請 08:30 の顔か・反証 A6 の複製）⑦年別 未調整 Δμ。
事前の最重大反証: (i) 非 NFP/FOMC/CPI 日の 08:20/08:25 ジャンプの 5〜10 分後には他の 08:30 ET 公表（新規失業保険申請・PPI・小売・GDP・耐久財…）が来る → UJ_US2 は「情報なし」でなく
   「他の定時公表の直前 10 分」＝β_US2 > 0 でも段差でなく公表の顔かもしれない（決着には 08:30 公表の完全暦【要取得】）。(ii) 検出力: 外 US2 ≈55 本（上記）。
   (iii) UJ_oth にも 10:05/10:10（10:00 公表の第 2 波）・08:35/08:40 が残る＝純化は部分的（反証 04:10 の UJ 上位スロット表）。(iv) bid 1 社・CFD。(v) 多重検定: 判定セル 2（H_STEP・H_PURE(c)）。
出力 data/c56_uj_two_slot_split_result.md。読取専用・発注なし・本番編集なし。
"""
import os, json, math, time, sys
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c56_uj_two_slot_split_result.md"); L = []
NY = "America/New_York"; SEED = 20261120
ZMAIN, ZSENS = 5.0, (4.0, 6.0); W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0
WD = "月火水木金土日"
US2 = {(8, 20), (8, 25), (9, 35), (9, 40)}

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

say("# [cycle56] c45 UJ 腕の 2 スロット分割: UJ_US2 {08:20,08:25,09:35,09:40 ET} vs UJ_oth（β・時刻 FE・日クラスタ）")
say(f"- 事前固定は docstring・seed {SEED}・判定窓 外 2021-26H1・判定セル 2（H_STEP・H_PURE(c)）")
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

J = {zt: decluster(cand & (z >= zt)) for zt in (4.0, ZMAIN, 6.0)}
isevbar = etdate.isin(evdays)
def classify(ji):
    ok = ~np.asarray(isevbar[ji])
    sched = (mn[ji] % 15 == 0)
    return ji[ok & sched], ji[ok & ~sched]
SJ5, UJ5 = classify(J[ZMAIN])
is_us2 = np.array([(int(hr[i]), int(mn[i])) in US2 for i in UJ5], bool)
UJ_US2 = UJ5[is_us2]; UJ_OTH = UJ5[~is_us2]
say(f"- declustered ジャンプ: 5σ {len(J[ZMAIN])}（SJ {len(SJ5)}・UJ {len(UJ5)}）→ UJ_US2 {len(UJ_US2)}・UJ_oth {len(UJ_OTH)}")
# 複製 assert（事象集合）
assert len(J[ZMAIN]) == 2166 and len(SJ5) == 786 and len(UJ5) == 937, "c45 事象集合の複製に失敗"
# 反証 04:10 の 180 事象と一致するか
say(f"- 複製 assert OK（2166／786／937）・UJ_US2 = {len(UJ_US2)}（反証 04:10 の印字 180 と{'一致' if len(UJ_US2)==180 else '不一致'}）")
yrs = tny.year.to_numpy()
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
say("| 窓 | UJ_US2 事象（08:20/08:25／09:35/09:40） | UJ_oth 事象 | US2 |r| 中央値 bp / z | oth |r| / z |")
say("|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    u2 = UJ_US2[(yrs[UJ_US2] >= lo_) & (yrs[UJ_US2] <= hi_)]; uo = UJ_OTH[(yrs[UJ_OTH] >= lo_) & (yrs[UJ_OTH] <= hi_)]
    n_pre = int((hr[u2] == 8).sum()); n_post = int((hr[u2] == 9).sum())
    say(f"| {lab} | {len(u2)}（{n_pre}／{n_post}） | {len(uo)} | {np.median(np.abs(r[u2])):.1f} / {np.median(z[u2]):.2f} | {np.median(np.abs(r[uo])):.1f} / {np.median(z[uo]):.2f} |")
# ⑥ 曜日分布（US2 事象）
wdc = pd.Series(wd[UJ_US2]).value_counts().sort_index()
say("- ⑥ UJ_US2 事象の曜日分布: " + " ".join(f"{WD[w]}{int(c)}" for w, c in wdc.items()) + "（全 UJ: " +
    " ".join(f"{WD[w]}{int(c)}" for w, c in pd.Series(wd[UJ5]).value_counts().sort_index().items()) + "）")
# UJ_oth の上位 ET スロット（純化の残り）
slot = pd.Series([f"{hr[i]:02d}:{mn[i]:02d}" for i in UJ_OTH]).value_counts().head(8)
say("- UJ_oth の上位 8 ET スロット（純化の残り・反証 (iii)）: " + " ".join(f"{s}:{int(c)}" for s, c in slot.items()))
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
tr["sgn"] = np.where(sv.str.startswith("B"), 1, -1)
say(f"- scan 本 {len(tr)}・FEED_TOL {FT}")

def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    if len(t0s) == 0: return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, p_nfp = inwin(t_nfp); m_fomc, p_fomc = inwin(t_fomc)
tr["ANN"] = m_nfp | m_fomc
tr["ann_t0"] = np.where(m_nfp, p_nfp, np.where(m_fomc, p_fomc, np.nan))
tsf = ts.astype(float)
m_sj, _ = inwin(tsf[SJ5] + 300); m_uj, p_uj = inwin(tsf[UJ5] + 300)
m_u2, p_u2 = inwin(tsf[UJ_US2] + 300); m_uo, p_uo = inwin(tsf[UJ_OTH] + 300)
tr["SJ"] = m_sj & ~tr.ANN & ~tr.isevday; tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
# 本の帰属: c45 の UJ 本（最後の UJ 事象の窓）を、その最後の UJ 事象が US2 かで分ける（排反・UJ = US2 ∪ oth を保証）
last_uj_t0 = p_uj - 300
last_is_us2 = np.isin(last_uj_t0.astype(np.int64), ts[UJ_US2])
tr["US2"] = tr.UJ & last_is_us2; tr["OTH"] = tr.UJ & ~last_is_us2
tr["uj_t0"] = np.where(tr.UJ, last_uj_t0, np.nan)
m_any4, _ = inwin(tsf[J[4.0]] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
assert int(tr.UJ.sum()) == int(tr.US2.sum()) + int(tr.OTH.sum())
say(f"- 本数: ANN {int(tr.ANN.sum())}・SJ {int(tr.SJ.sum())}・UJ {int(tr.UJ.sum())} = US2 {int(tr.US2.sum())} + oth {int(tr.OTH.sum())}・ctrl {int(tr.ctrl.sum())}")
def bar_at(tsec):
    out = np.full(len(tsec), -1); ok = np.isfinite(tsec)
    key = tsec[ok].astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    good = ts[pos] == key; tmp = np.full(ok.sum(), -1); tmp[good] = pos[good]; out[ok] = tmp; return out
b_uj = bar_at(tr.uj_t0.to_numpy())
tr["uj_r"] = np.where(b_uj >= 0, r[np.clip(b_uj, 0, None)], np.nan)
tr["uj_hr"] = np.where(b_uj >= 0, hr[np.clip(b_uj, 0, None)], -1)
tr["uj_min"] = (et_ - tr.uj_t0.to_numpy()) / 60.0; tr["ann_min"] = (et_ - tr.ann_t0.to_numpy()) / 60.0
say("")

# ---------- 推定器（c45 と同一） ----------
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
    hours = np.arange(24)
    H = np.column_stack([(o.hh.to_numpy() == h).astype(float) for h in hours[1:]])
    Gm = np.column_stack([o[c].to_numpy().astype(float) for c in groups])
    X = np.column_stack([np.ones(len(o)), Gm, H]); y = o.Rs.to_numpy(float)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    res = {c: (beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(o[c].sum())) for i, c in enumerate(groups)}
    return res, V, G

def contrast(V, i, j):
    cv = np.zeros(V.shape[0]); cv[1 + i] = 1; cv[1 + j] = -1
    return math.sqrt(max(cv @ V @ cv, 0))

def sub(lo_, hi_): return tr[(tr.year >= lo_) & (tr.year <= hi_)]
def tstr(b, s): return f"{b:+.3f} ({(b/s if s>0 else float('nan')):+.2f})"

# ---------- 複製（c45 主表の ANN/UJ・外） ----------
say("## 0. 複製: c45 主表（ANN・SJ・UJ 全体）外 2021-26H1")
o = sub(2021, 2026); sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
res0, V0, G0 = fe_fit(sel, ["ANN", "SJ", "UJ"])
bA0, sA0, nA0 = res0["ANN"]; bU0, sU0, nU0 = res0["UJ"]
say(f"- 外 ANN n {nA0} β {tstr(bA0, sA0)}（c45: 138 / +0.514 (+4.02)）・UJ n {nU0} β {tstr(bU0, sU0)}（c45: 280 / +0.089 (+1.06)）・SJ n {res0['SJ'][2]} β {tstr(*res0['SJ'][:2])}")
assert nA0 == 138 and nU0 == 280 and abs(bA0 - 0.514) < 0.0015 and abs(bU0 - 0.089) < 0.0015, "c45 主表の複製に失敗"
say("- 複製 assert OK（n・β 3 桁一致）")
say("")

# ---------- 主表 ----------
say("## 1. 主表: 4 腕（ANN・SJ・UJ_US2・UJ_oth）の時刻 FE 調整 β（日クラスタ t）・MDE 2se・未調整 Welch")
say("| 窓 | 群 | n 本 / 事象日 | β 時刻FE (日cl t) | MDE 2se | 未調整 Δμ (Welch t) | 群 平均/中央値 | TP 率 |")
say("|---|---|---|---|---|---|---|---|")
RES = {}
GROUPS = ["ANN", "SJ", "US2", "OTH"]
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.SJ | o.US2 | o.OTH | o.ctrl]
    res, V, G = fe_fit(sel, GROUPS); C = sel[sel.ctrl]
    for g in GROUPS:
        A = sel[sel[g]]; b_, se_, n_ = res[g]; dm, tw = welch(A.Rs, C.Rs)
        say(f"| {lab} | {g} | {n_} / {A.day.nunique()} | **{tstr(b_, se_)}** | {2*se_:.3f} | {dm:+.3f} ({tw:+.2f}) | {A.Rs.mean():+.3f}/{A.Rs.median():+.2f} | {(A.exit=='TP').mean()*100:.0f}% |")
    dAO = res["ANN"][0] - res["OTH"][0]; sAO = contrast(V, 0, 3)
    dAU = res["ANN"][0] - res["US2"][0]; sAU = contrast(V, 0, 2)
    dUO = res["US2"][0] - res["OTH"][0]; sUO = contrast(V, 2, 3)
    say(f"| {lab} | **ANN − oth** | | **{tstr(dAO, sAO)}** | {2*sAO:.3f} | ANN − US2 {tstr(dAU, sAU)} | US2 − oth {tstr(dUO, sUO)} | G 日 {G}・ctrl 平均 {C.Rs.mean():+.3f} |")
    RES[lab] = dict(res=res, V=V, dAO=(dAO, sAO), dAU=(dAU, sAU), dUO=(dUO, sUO))
say("")

# ---------- 判定 ----------
say("## 2. 判定（事前固定・外 2021-26H1・条件は 1 行ずつ・判定語は boolean から合成）")
ro = RES["外 2021-26H1"]; bA, sA, nA = ro["res"]["ANN"]; b2, s2, n2 = ro["res"]["US2"]; bo, so, no = ro["res"]["OTH"]
t2 = b2 / s2 if s2 > 0 else float("nan"); to = bo / so if so > 0 else float("nan")
dAO, sAO = ro["dAO"]; tAO = dAO / sAO if sAO > 0 else float("nan")
half = 0.5 * bA
say(f"- 外 β_ANN {bA:+.3f} (t {bA/sA:+.2f}・n {nA})・0.5·β_ANN = {half:+.3f}")
say(f"- 外 β_US2 {b2:+.3f} (t {t2:+.2f}・n {n2}・MDE {2*s2:.3f})／β_oth {bo:+.3f} (t {to:+.2f}・n {no}・MDE {2*so:.3f})／ANN − oth {dAO:+.3f} (t {tAO:+.2f}・MDE {2*sAO:.3f})")
say("### H_STEP（予定時刻の vol 段差だけで走る）")
c1 = b2 > 0; c2_ = t2 >= 2; c3 = b2 >= half; under = (2 * s2) > half
say(f"- 条件 1: β_US2 > 0 → 観測 {b2:+.3f} → {c1}")
say(f"- 条件 2: t(β_US2) ≥ 2 → 観測 {t2:+.2f} → {c2_}")
say(f"- 条件 3: β_US2 ≥ 0.5·β_ANN ({half:+.3f}) → {c3}")
say(f"- 検出力: MDE_US2 {2*s2:.3f} vs 0.5·β_ANN {half:.3f} → underpowered = {under}")
h_step = c1 and c2_ and c3
say(f"- **H_STEP = {'PASS' if h_step else ('underpowered（PASS/FAIL を言わない・β_US2 の 95% 上限 ' + f'{b2+2*s2:+.3f}' + '）' if under else 'FAIL')}**")
say("### H_PURE（純予定外腕 UJ_oth は ANN と別・同等性の方向）")
pa = abs(to) < 1.5; pb = tAO >= 2; pc = (bo + 2 * so) < half
say(f"- (a) |t(β_oth)| < 1.5 → 観測 {abs(to):.2f} → {pa}（弱い脚・雑音通過率 70〜87%）")
say(f"- (b) t(β_ANN − β_oth) ≥ 2 → 観測 {tAO:+.2f} → {pb}")
say(f"- (c) β_oth + 2se = {bo+2*so:+.3f} < 0.5·β_ANN {half:+.3f} → {pc}（TOST 方向・判定の内容）")
h_pure = pa and pb and pc
say(f"- **H_PURE = {'PASS' if h_pure else 'inconclusive'}**（c45 全 UJ では (c) 上限 +0.252 vs 閾 +0.257 の紙一重）")
# 比較: c45 の UJ 全体での (c)
say(f"- 参考 c45 UJ 全体: β_UJ +0.089・se {sU0:.3f} → 上限 {bU0+2*sU0:+.3f} vs 閾 {0.5*bA0:+.3f} → (c) {bU0+2*sU0 < 0.5*bA0}")
say("")

# ---------- 副① US2 の前/後分割 ----------
say("## 副① UJ_US2 を 08:20/08:25（08:30 公表前）と 09:35/09:40（NYSE 開場後）に分けた β（時刻 FE・日クラスタ）")
say("| 窓 | US2_pre 08:2x n/β(t)/MDE | US2_post 09:3x n/β(t)/MDE | oth n/β(t) |")
say("|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    o = o.assign(PRE=o.US2 & (o.uj_hr == 8), POST=o.US2 & (o.uj_hr == 9))
    sel = o[o.ANN | o.SJ | o.PRE | o.POST | o.OTH | o.ctrl]
    res, V, G = fe_fit(sel, ["ANN", "SJ", "PRE", "POST", "OTH"])
    f = lambda k: f"{res[k][2]}/{tstr(res[k][0], res[k][1])}/{2*res[k][1]:.2f}"
    say(f"| {lab} | {f('PRE')} | {f('POST')} | {res['OTH'][2]}/{tstr(res['OTH'][0], res['OTH'][1])} |")
say("")

# ---------- 副④ 経過分 ----------
say("## 副④ 事象後の経過分別 β（0-60／60-120／120-240 分・時刻 FE・日クラスタ）")
say("| 窓 | 群 | 0-60 n/β(t) | 60-120 n/β(t) | 120-240 n/β(t) |")
say("|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    for g in ["US2", "OTH"]:
        m = o.uj_min
        o2 = o.assign(K1=o[g] & (m < 60), K2=o[g] & (m >= 60) & (m < 120), K3=o[g] & (m >= 120))
        other = "OTH" if g == "US2" else "US2"
        sel = o2[o2.K1 | o2.K2 | o2.K3 | o2.ANN | o2.SJ | o2[other] | o2.ctrl]
        res, V, G = fe_fit(sel, ["K1", "K2", "K3", "ANN", "SJ", other])
        f = lambda k: f"{res[k][2]}/{tstr(res[k][0], res[k][1])}"
        say(f"| {lab} | {g} | {f('K1')} | {f('K2')} | {f('K3')} |")
say("")

# ---------- 副② プラセボ ----------
say("## 副② プラセボ: US2・oth の t0 を ±7 日ずらした偽事象（実事象日・4σ ジャンプ窓・ANN は除外）")
say("| 腕 | シフト | 在 n/β(t) | 外 n/β(t) | 近年 n/β(t) |")
say("|---|---|---|---|---|")
for arm, ji in (("US2", UJ_US2), ("oth", UJ_OTH)):
    for sh in (-7, 7):
        mp, _ = inwin(tsf[ji] + 300 + sh * 86400.0)
        tr["PL"] = mp & ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
        cells = []
        for lab, lo_, hi_ in ERAS:
            o = sub(lo_, hi_); o = o.assign(ctrl2=o.ctrl & ~o.PL)
            sel = o[o.PL | o.ctrl2]
            if sel.PL.sum() < 10: cells.append(f"{int(sel.PL.sum())}/—"); continue
            res, V, G = fe_fit(sel, ["PL"])
            cells.append(f"{res['PL'][2]}/{tstr(res['PL'][0], res['PL'][1])}")
        say(f"| {arm} | {sh:+d} 日 | {cells[0]} | {cells[1]} | {cells[2]} |")
say("")

# ---------- 副③ x0・幾何（外） ----------
say("## 副③ look-ahead 陽性対照 x0（建玉足・㉚）と幾何の群差（外 2021-26H1）")
o = sub(2021, 2026); C = o[o.ctrl]
for g in ["ANN", "US2", "OTH"]:
    A = o[o[g]]
    if len(A) < 5: continue
    dx, tx = welch(A.x0, C.x0)
    say(f"- {g}: n {len(A)}・x0 Δ {dx:+.3f} (t {tx:+.2f})・atr 平均 {A.atr.mean():.2f} vs ctrl {C.atr.mean():.2f}・risk {A.risk.mean():.2f} vs {C.risk.mean():.2f}・b {A.b.mean():.2f} vs {C.b.mean():.2f}・TP 率 {(A.exit=='TP').mean()*100:.0f}% vs {(C.exit=='TP').mean()*100:.0f}%・hold 中央値 {A.hold.median():.0f} vs {C.hold.median():.0f}・建玉 ET 時 中央値 {A.hh.median():.0f}")
say("")

# ---------- 副⑤ 感度 4σ/6σ ----------
say("## 副⑤ 感度: 4σ／6σ で同じ 4 スロット分割（ctrl は 5σ 版と同じ・事象再定義）")
say("| 閾値 | 窓 | US2 事象/n/β(t) | oth 事象/n/β(t) | ANN − oth (t) | oth 上限 vs 0.5β_ANN |")
say("|---|---|---|---|---|---|")
for zt in ZSENS:
    SJx, UJx = classify(J[zt])
    isu = np.array([(int(hr[i]), int(mn[i])) in US2 for i in UJx], bool)
    U2x, UOx = UJx[isu], UJx[~isu]
    msj, _ = inwin(tsf[SJx] + 300); mu, pu = inwin(tsf[UJx] + 300)
    last_us2x = np.isin((pu - 300).astype(np.int64), ts[U2x])
    tr["SJx"] = msj & ~tr.ANN & ~tr.isevday; ujx = mu & ~tr.ANN & ~tr.isevday
    tr["U2x"] = ujx & last_us2x; tr["UOx"] = ujx & ~last_us2x
    for lab, lo_, hi_ in ERAS:
        o = sub(lo_, hi_); o = o.assign(ctrlx=o.ctrl & ~o.SJx & ~o.U2x & ~o.UOx)
        sel = o[o.ANN | o.SJx | o.U2x | o.UOx | o.ctrlx]
        res, V, G = fe_fit(sel, ["ANN", "SJx", "U2x", "UOx"])
        dd_ = res["ANN"][0] - res["UOx"][0]; sd_ = contrast(V, 0, 3)
        ne2 = int(((yrs[U2x] >= lo_) & (yrs[U2x] <= hi_)).sum()); neo = int(((yrs[UOx] >= lo_) & (yrs[UOx] <= hi_)).sum())
        up = res["UOx"][0] + 2 * res["UOx"][1]
        say(f"| {zt:.0f}σ | {lab} | {ne2}/{res['U2x'][2]}/{tstr(res['U2x'][0], res['U2x'][1])} | {neo}/{res['UOx'][2]}/{tstr(res['UOx'][0], res['UOx'][1])} | {tstr(dd_, sd_)} | {up:+.3f} vs {0.5*res['ANN'][0]:+.3f} → {up < 0.5*res['ANN'][0]} |")
say("")

# ---------- 副⑦ 年別・裾 ----------
say("## 副⑦ 外の年別 未調整 Δμ（n）と上位本除去（US2・oth）")
o = sub(2021, 2026); C = o[o.ctrl]
for g in ["US2", "OTH"]:
    U = o[o[g]]
    if len(U) < 10: continue
    srt = U.Rs.sort_values(ascending=False)
    rem = " ".join(f"上位{k}除去 {welch(U.drop(srt.index[:k]).Rs, C.Rs)[0]:+.3f}({welch(U.drop(srt.index[:k]).Rs, C.Rs)[1]:+.2f})" for k in (1, 3))
    say(f"- {g}: 年別 " + " ".join(f"{y}:{welch(U[U.year==y].Rs, C[C.year==y].Rs)[0]:+.2f}({int((U.year==y).sum())})" for y in range(2021, 2027) if (U.year == y).sum() >= 3) + f"・{rem}・中央値 {U.Rs.median():+.2f}")
say("")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
