# -*- coding: utf-8 -*-
"""
[REFUTE / 2026-11-17 15:40] 反証レーン — 対象: cycle45 (12:55) の判定 **H_SCHED PASS**
  「反証 09:30 が survived とした『2021+ の金 scan 本は NFP/FOMC 発表後 0〜4h に建つと +0.48R』は
    予定された情報公開に固有で、大きな 5σ ジャンプ一般（post-jump 状態）には一般化しない」
  根拠 = 外 2021-26H1 β_UJ +0.089（日クラスタ t 1.06・n 280・MDE 0.167）vs β_ANN +0.514（t 4.02）・
        ANN−UJ +0.425（t 2.84）／判定規則 H_SCHED = |t_UJ|<1.5 ∧ t(ANN−UJ)≥2。

=== 事前固定（数字を見る前・この docstring が正本・10 の破壊規則を先に宣言） ===
データ: data/macro/XAU_m5_close.npz・data/refute_c4_scan_paths_2010_2026.json（c4 凍結 19404 本）・
       FOMC_dates.csv・CPI_dates.csv・NFP = c24 v2 規則。M5 読込なし・MT5 なし・外部通信なし・発注なし・scan 無し。
推定器・R*・ジャンプ検出（5σ・σ_trail 5520 足・decluster 4h）・群定義・窓・ctrl は c45 と同一（複製してから壊す）。
D2 遵守: 在 2010-20／外 2021-26H1／近年 2024-26H1 の窓別のみ。16 年一括は使わない。seed 20261117・NPERM 2000。

R1 複製: c45 主表の再現（外 β_UJ・β_ANN・ANN−UJ）。**BREAK-0** = 再現できない。
R2 **条件づけの非対称（本命）**: c45 の ANN は「ジャンプが起きたか否かに無条件」な発表時刻全部、UJ は「5σ ジャンプが起きた」
   条件つき集合＝2 本の腕は *予定性* だけでなく *ジャンプ条件づけ* でも違う。対称化して ANN を分割する:
   ANN_J = 公表足が 5σ ジャンプ（同一検出器）／ANN_NJ = それ以外。窓は UJ と同じ [t0+300, +4h) に揃える。
   **BREAK-A** = β_ANN_NJ ≥ 0.5·β_ANN_J ∧ t(ANN_NJ) ≥ 2（＝発表の優位はジャンプを要しない → UJ は機構判別の対照になっていない）。
   **BREAK-A2** = t(ANN_J − UJ) < 2（＝見かけの予定性固有は無条件 ANN 腕が作っていた）。
R3 **検出力・同等性**: H_GEN の閾値は β_UJ ≥ 0.5·β_ANN。契約 γ = β_UJ − 0.5·β_ANN をクラスタ共分散で検定。
   **BREAK-B** = t(γ) > −2（＝H_GEN の閾値を棄却できない → 「H_GEN 不成立」は非棄却を結論に変えた誤り・正しくは inconclusive）。
R4 幾何調整（c45 の自己申告 (ii)・反証 c44 B2 の形）: FE に log atr・log risk・b・sgn を追加。
   **BREAK-C** = t(ANN−UJ) < 2 または β_UJ が t ≥ 2 になる。
R5 **帰無校正**: 偽 ANN 集合（非発表平日から NFP 本数を 08:30・FOMC 本数を 14:00 に件数一致で抽出）2000 回で
   t(偽ANN − UJ) の帰無分布を作る（2 腕 spec・ctrl は偽窓を除外）。**BREAK-D** = 片側経験 p(t ≥ 実測) > 0.025。
   併せて偽 UJ（t0 を ±7/14/21/28 日シフト = 8 セル）で t(β_UJ) の帰無 sd を出す。
   **BREAK-D2**（方法論） = 帰無 sd > 1.3（＝|t_UJ|<1.5 という H_SCHED の片方の条件が校正されていない）。
R6 在外分割の再定義: 境界 2019／2022／2023・LOYO（外 6 年）・奇偶年。
   **BREAK-E** = 2 つ以上の分割で β_UJ の t ≥ 2、または半数以上で t(ANN−UJ) < 1.5。
R7 コスト倍: R* から k·TRIG_SPREAD/risk（k=1,2,3）。**BREAK-F** = k=2 で t(ANN−UJ) < 2。
R8 **純・予定外部分集合**: UJ を「米指標の暦が無い時間帯」に限定（ET 11:00–13:00 ∪ 18:00–07:00）＝最も純粋な予定外。
   **BREAK-G** = β_UJ_pure ≥ 0.5·β_ANN ∧ t ≥ 2（H_GEN の部分復活）。
R9 窓の整合: ANN を [t0+300,+4h)、UJ を [t0,+4h) に入れ替えて双方向で測る。**BREAK-H** = どちらかで t(ANN−UJ) < 2。
R10 事象単位: 1 事象 1 観測（事象内平均 R*）で ANN 事象 vs UJ 事象を直接比較（Welch・Mann-Whitney）。
   **BREAK-I** = 事象単位 t < 2 または MWU p > 0.10。
R11 **日 vs 窓の分離**: XJ = 発表日のジャンプで発表窓 [t0,+4h) の外にあるもの。
   **BREAK-J** = β_XJ ≥ 0.5·β_ANN ∧ t ≥ 1.5（＝効いているのは「予定公表の窓」でなく「発表日」→ 予定性の読みが壊れる）。
survived = BREAK-A〜J が全部不発。ひとつでも当たれば c45 の H_SCHED PASS は broken（判定規則の瑕疵を含む）。
出力 data/refute_c45_schedvsjump.md。読取専用・AUREL_RESEARCH 配下にのみ書く。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c45_schedvsjump.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
ZMAIN = 5.0; W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0; NPERM = 2000
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


say("# [REFUTE c45] H_SCHED PASS を壊す: 条件づけの非対称・非棄却の誤読・帰無校正")
say(f"- 事前固定は docstring（BREAK-A〜J を数字より先に宣言）・seed {SEED}・NPERM {NPERM}")
say("")

# ---------- 暦（c45 と同一） ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0)
t_nfp = t_nfp[np.isfinite(t_nfp)]; t_fomc = t_fomc[np.isfinite(t_fomc)]
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

# ---------- npz・ジャンプ検出（c45 と同一） ----------
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


J5 = decluster(cand & (z >= ZMAIN)); J4 = decluster(cand & (z >= 4.0))
isevbar = np.asarray(etdate.isin(evdays))
ok_non = ~isevbar[J5]; sched = (mn[J5] % 15 == 0)
SJ5 = J5[ok_non & sched]; UJ5 = J5[ok_non & ~sched]
XJ5 = J5[isevbar[J5]]                     # 発表日のジャンプ（R11 用・窓外に絞るのは後段）
say(f"- ジャンプ 5σ declustered {len(J5)}（SJ {len(SJ5)}・UJ {len(UJ5)}・EVDAY {len(XJ5)}）・4σ {len(J4)}")

# 公表足がジャンプか（R2 の対称化）
def bar_pos(tsec):
    key = np.asarray(tsec, dtype=np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    good = ts[pos] == key
    return pos, good


p_n, g_n = bar_pos(t_nfp); p_f, g_f = bar_pos(t_fomc)
jump_n = g_n & cand[p_n] & (z[p_n] >= ZMAIN); jump_f = g_f & cand[p_f] & (z[p_f] >= ZMAIN)
say(f"- 公表足が 5σ ジャンプ: NFP {int(jump_n.sum())}/{int(g_n.sum())}・FOMC {int(jump_f.sum())}/{int(g_f.sum())}"
    f"（|r| 中央値 NFP {np.nanmedian(np.abs(r[p_n[g_n]])):.1f} bp・FOMC {np.nanmedian(np.abs(r[p_f[g_f]])):.1f}・UJ {np.median(np.abs(r[UJ5])):.1f}）")

# ---------- scan 本（c45 と同一） ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; TSP = d["frozen"]["TRIG_SPREAD"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)
sv = tr.side.astype(str).str.upper()
tr["sgn"] = np.where(sv.str.startswith("B") | (sv == "1") | (sv == "LONG"), 1, -1)
tsf = ts.astype(float)


def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(np.asarray(t0s, float)[np.isfinite(t0s)]) + off
    if len(t0s) == 0:
        return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]


m_nfp, p1 = inwin(t_nfp); m_fomc, p2 = inwin(t_fomc)
tr["ANN"] = m_nfp | m_fomc
tr["ann_t0"] = np.where(m_nfp, p1, np.where(m_fomc, p2, np.nan))
m_sj, _ = inwin(tsf[SJ5] + 300); m_uj, q_uj = inwin(tsf[UJ5] + 300)
tr["SJ"] = m_sj & ~tr.ANN & ~tr.isevday; tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
tr["uj_t0"] = np.where(tr.UJ, q_uj - 300, np.nan)
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
say(f"- 本数: ANN {int(tr.ANN.sum())}・SJ {int(tr.SJ.sum())}・UJ {int(tr.UJ.sum())}・ctrl {int(tr.ctrl.sum())}")
say("")


# ---------- 推定器（高速クラスタ OLS） ----------
def ols_cluster(y, X, gcode, G):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    Xe = X * e[:, None]
    S = np.empty((G, X.shape[1]))
    for j in range(X.shape[1]):
        S[:, j] = np.bincount(gcode, weights=Xe[:, j], minlength=G)
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V


def fit(o, groups, geo=False, ycol="Rs"):
    cols = [np.ones(len(o))]; names = ["const"]
    for c in groups:
        cols.append(o[c].to_numpy(float)); names.append(c)
    hhv = o.hh.to_numpy()
    for h in range(1, 24):
        v = (hhv == h).astype(float)
        if v.sum() > 0:
            cols.append(v); names.append(f"h{h}")
    if geo:
        cols.append(np.log(np.clip(o.atr.to_numpy(float), 1e-3, None))); names.append("latr")
        cols.append(np.log(np.clip(o.risk.to_numpy(float), 1e-3, None))); names.append("lrisk")
        cols.append(o.b.to_numpy(float)); names.append("b")
        cols.append(o.sgn.to_numpy(float)); names.append("sgn")
    X = np.column_stack(cols); y = o[ycol].to_numpy(float)
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


def sub(lo_, hi_, frame=None):
    f = tr if frame is None else frame
    return f[(f.year >= lo_) & (f.year <= hi_)]


def fmt(t3):
    b, s, n = t3
    return f"{n}/{b:+.3f}({(b/s if s>0 else float('nan')):+.2f})"


# ================= R1 複製 =================
say("## R1 複製（c45 主表・時刻 FE・日クラスタ）")
say("| 窓 | ANN n/β(t) | SJ n/β(t) | UJ n/β(t) | ANN−UJ (t) | MDE_UJ 2se |")
say("|---|---|---|---|---|---|")
R1 = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "SJ", "UJ"])
    dv, ds, dt = contrast(beta, V, ix, {"ANN": 1, "UJ": -1})
    say(f"| {lab} | {fmt(res['ANN'])} | {fmt(res['SJ'])} | {fmt(res['UJ'])} | {dv:+.3f} ({dt:+.2f}) | {2*res['UJ'][1]:.3f} |")
    R1[lab] = dict(res=res, beta=beta, V=V, ix=ix, d=(dv, ds, dt), G=G)
EXT = "外 2021-26H1"
bA = R1[EXT]["res"]["ANN"][0]; bU, sU, nU = R1[EXT]["res"]["UJ"]
say(f"- 外の再現: β_UJ {bU:+.3f} (t {bU/sU:+.2f})・β_ANN {bA:+.3f}・ANN−UJ {R1[EXT]['d'][0]:+.3f} (t {R1[EXT]['d'][2]:+.2f})"
    f" → c45 の +0.089(1.06)／+0.514／+0.425(2.84) と一致するか")
say("")

# 2 腕 spec（R5 の校正と同形の実測値）
say("## R1b 2 腕 spec（ANN・UJ のみ・SJ 本は除外・R5 校正の参照値）")
say("| 窓 | ANN n/β(t) | UJ n/β(t) | ANN−UJ (t) |")
say("|---|---|---|---|")
R1b = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "UJ"])
    dv, ds, dt = contrast(beta, V, ix, {"ANN": 1, "UJ": -1})
    say(f"| {lab} | {fmt(res['ANN'])} | {fmt(res['UJ'])} | {dv:+.3f} ({dt:+.2f}) |")
    R1b[lab] = (dv, ds, dt)
say("")

# ================= R2 条件づけの非対称（本命） =================
say("## R2 BREAK-A: 条件づけの非対称 — ANN をジャンプ有無で分割し窓も UJ に揃える")
say("- ANN_J = 公表足が 5σ ジャンプ・ANN_NJ = それ以外。窓はともに [t0+300, +4h)（UJ と同形）。")
say("| 窓 | ANN_J n/β(t) | ANN_NJ n/β(t) | UJ n/β(t) | ANN_J−UJ (t) | ANN_NJ−UJ (t) | ANN_J−ANN_NJ (t) |")
say("|---|---|---|---|---|---|---|")
R2 = {}
mJ, pJ = inwin(np.r_[t_nfp[jump_n], t_fomc[jump_f]], off=300.0)
mN, pN = inwin(np.r_[t_nfp[~jump_n & g_n], t_fomc[~jump_f & g_f]], off=300.0)
tr["ANN_J"] = mJ; tr["ANN_NJ"] = mN & ~mJ
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN_J | o.ANN_NJ | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN_J", "ANN_NJ", "UJ"])
    d1 = contrast(beta, V, ix, {"ANN_J": 1, "UJ": -1})
    d2 = contrast(beta, V, ix, {"ANN_NJ": 1, "UJ": -1})
    d3 = contrast(beta, V, ix, {"ANN_J": 1, "ANN_NJ": -1})
    say(f"| {lab} | {fmt(res['ANN_J'])} | {fmt(res['ANN_NJ'])} | {fmt(res['UJ'])} | {d1[0]:+.3f} ({d1[2]:+.2f}) | {d2[0]:+.3f} ({d2[2]:+.2f}) | {d3[0]:+.3f} ({d3[2]:+.2f}) |")
    R2[lab] = dict(res=res, d1=d1, d2=d2, d3=d3)
rJ = R2[EXT]["res"]["ANN_J"]; rN = R2[EXT]["res"]["ANN_NJ"]
bA_J = rJ[0]; bA_N = rN[0]; tN = rN[0] / rN[1] if rN[1] > 0 else float("nan")
BREAK_A = bool((bA_N >= 0.5 * bA_J) and (tN >= 2))
BREAK_A2 = bool(R2[EXT]["d1"][2] < 2)
say(f"- **BREAK-A**（β_ANN_NJ ≥ 0.5·β_ANN_J ∧ t ≥ 2）= {BREAK_A}  [{bA_N:+.3f} vs 閾値 {0.5*bA_J:+.3f}・t {tN:+.2f}]")
say(f"- **BREAK-A2**（t(ANN_J − UJ) < 2）= {BREAK_A2}  [t {R2[EXT]['d1'][2]:+.2f}]")
say("")

# ================= R3 検出力・同等性 =================
say("## R3 BREAK-B: H_GEN の閾値（β_UJ ≥ 0.5·β_ANN）は棄却できるか")
say("| 窓 | γ = β_UJ − 0.5·β_ANN | se | t | 95% CI 上限 β_UJ | 0.5·β_ANN |")
say("|---|---|---|---|---|---|")
R3 = {}
for lab, lo_, hi_ in ERAS:
    g = R1[lab]
    gv, gs, gt = contrast(g["beta"], g["V"], g["ix"], {"UJ": 1, "ANN": -0.5})
    bu, su, _ = g["res"]["UJ"]; ba = g["res"]["ANN"][0]
    say(f"| {lab} | {gv:+.3f} | {gs:.3f} | {gt:+.2f} | {bu+1.96*su:+.3f} | {0.5*ba:+.3f} |")
    R3[lab] = (gv, gs, gt)
BREAK_B = bool(R3[EXT][2] > -2)
say(f"- **BREAK-B**（t(γ) > −2 ＝ H_GEN 閾値を棄却できない）= {BREAK_B}  [t {R3[EXT][2]:+.2f}]")
say("")

# ================= R4 幾何調整 =================
say("## R4 BREAK-C: 幾何調整（log atr・log risk・b・sgn を FE に追加）")
say("| 窓 | ANN n/β(t) | SJ n/β(t) | UJ n/β(t) | ANN−UJ (t) |")
say("|---|---|---|---|---|")
R4 = {}
say(f"- atr ≤ 0 の本 {int((tr.atr <= 0).sum())}／risk ≤ 0 {int((tr.risk <= 0).sum())} は幾何版から除外")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[(o.ANN | o.SJ | o.UJ | o.ctrl) & (o.atr > 0) & (o.risk > 0)]
    res, beta, V, ix, G = fit(sel, ["ANN", "SJ", "UJ"], geo=True)
    dv, ds, dt = contrast(beta, V, ix, {"ANN": 1, "UJ": -1})
    say(f"| {lab} | {fmt(res['ANN'])} | {fmt(res['SJ'])} | {fmt(res['UJ'])} | {dv:+.3f} ({dt:+.2f}) |")
    R4[lab] = dict(res=res, d=(dv, ds, dt))
tU4 = R4[EXT]["res"]["UJ"][0] / R4[EXT]["res"]["UJ"][1]
BREAK_C = bool((R4[EXT]["d"][2] < 2) or (tU4 >= 2))
say(f"- **BREAK-C** = {BREAK_C}  [t(ANN−UJ) {R4[EXT]['d'][2]:+.2f}・t(β_UJ) {tU4:+.2f}]")
say("")

# ================= R5 帰無校正 =================
say("## R5 BREAK-D: 偽 ANN 集合 2000 回で t(ANN−UJ) の帰無分布（2 腕 spec）")
nonev_days = pd.DatetimeIndex(sorted(set(etdate[(wd <= 4)]) - set(evdays)))
say(f"- 偽 ANN の母集団: 非発表平日 {len(nonev_days)} 日（08:30 / 14:00 ET のスロットに配置）")
R5 = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_).copy()
    pool = nonev_days[(nonev_days.year >= lo_) & (nonev_days.year <= hi_)]
    n_n = int(((pd.to_datetime(t_nfp, unit="s").year >= lo_) & (pd.to_datetime(t_nfp, unit="s").year <= hi_)).sum())
    n_f = int(((pd.to_datetime(t_fomc, unit="s").year >= lo_) & (pd.to_datetime(t_fomc, unit="s").year <= hi_)).sum())
    if len(pool) < n_n + n_f + 10:
        say(f"- {lab}: 母集団不足"); continue
    obs_t = R1b[lab][2]
    tnull = np.full(NPERM, np.nan)
    pool_i = np.arange(len(pool))
    for it in range(NPERM):
        pick = rng.choice(pool_i, size=n_n + n_f, replace=False)
        d_n = pool[pick[:n_n]]; d_f = pool[pick[n_n:]]
        tz = np.r_[epoch_et(d_n, 8, 30), epoch_et(d_f, 14, 0)]
        mp, _ = inwin(tz)
        oo = o.assign(PA=mp[(tr.year >= lo_) & (tr.year <= hi_)], )
        oo = oo.assign(ctrl2=oo.ctrl & ~oo.PA, UJ2=oo.UJ & ~oo.PA)
        sel = oo[oo.PA | oo.UJ2 | oo.ctrl2]
        if sel.PA.sum() < 20 or sel.UJ2.sum() < 20: continue
        try:
            res, beta, V, ix, G = fit(sel, ["PA", "UJ2"])
            tnull[it] = contrast(beta, V, ix, {"PA": 1, "UJ2": -1})[2]
        except Exception:
            pass
    tn = tnull[np.isfinite(tnull)]
    p1s = float((tn >= obs_t).mean()) if len(tn) else float("nan")
    say(f"- {lab}: 実測 t {obs_t:+.2f}／帰無 n {len(tn)}・平均 {tn.mean():+.3f}・sd {tn.std(ddof=1):.3f}・p90 {np.percentile(tn,90):+.2f}・p97.5 {np.percentile(tn,97.5):+.2f}・max {tn.max():+.2f} → **片側経験 p {p1s:.4f}**")
    R5[lab] = (obs_t, len(tn), tn.std(ddof=1), p1s)
BREAK_D = bool(R5.get(EXT, (0, 0, 0, 1))[3] > 0.025)
say(f"- **BREAK-D**（片側経験 p > 0.025）= {BREAK_D}")

say("")
say("### R5b BREAK-D2: 偽 UJ（t0 ±7/14/21/28 日）で t(β_UJ) の帰無 sd")
say("| シフト | 在 n/β(t) | 外 n/β(t) | 近年 n/β(t) |")
say("|---|---|---|---|")
shift_t = {lab: [] for lab, _, _ in ERAS}
for sh in (-28, -21, -14, -7, 7, 14, 21, 28):
    mp, _ = inwin(tsf[UJ5] + 300 + sh * 86400.0)
    tr["PLU"] = mp & ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
    cells = []
    for lab, lo_, hi_ in ERAS:
        o = sub(lo_, hi_); o = o.assign(ctrl2=o.ctrl & ~o.PLU)
        sel = o[o.PLU | o.ctrl2]
        if sel.PLU.sum() < 20: cells.append("—"); continue
        res, beta, V, ix, G = fit(sel, ["PLU"])
        b_, s_, n_ = res["PLU"]; tval = b_ / s_ if s_ > 0 else float("nan")
        cells.append(f"{n_}/{b_:+.3f}({tval:+.2f})")
        shift_t[lab].append(tval)
    say(f"| {sh:+d} 日 | {cells[0]} | {cells[1]} | {cells[2]} |")
sd_ext = float(np.std(shift_t[EXT], ddof=1)) if len(shift_t[EXT]) > 2 else float("nan")
BREAK_D2 = bool(sd_ext > 1.3)
say(f"- 外の偽 UJ t: {['%+.2f' % v for v in shift_t[EXT]]}・sd {sd_ext:.2f} → **BREAK-D2**（sd > 1.3）= {BREAK_D2}")
say("")

# ================= R6 在外分割 =================
say("## R6 BREAK-E: 在外分割の再定義・LOYO・奇偶年")
say("| 分割 | 外 UJ n/β(t) | 外 ANN n/β(t) | ANN−UJ (t) |")
say("|---|---|---|---|")
R6 = []
splits = [("外 2019-26", 2019, 2026), ("外 2022-26", 2022, 2026), ("外 2023-26", 2023, 2026)]
for lab, lo_, hi_ in splits:
    o = sub(lo_, hi_); sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "SJ", "UJ"])
    dv, ds, dt = contrast(beta, V, ix, {"ANN": 1, "UJ": -1})
    tu = res["UJ"][0] / res["UJ"][1]
    say(f"| {lab} | {fmt(res['UJ'])} | {fmt(res['ANN'])} | {dv:+.3f} ({dt:+.2f}) |")
    R6.append((lab, tu, dt))
for y in range(2021, 2027):
    o = sub(2021, 2026); o = o[o.year != y]; sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "SJ", "UJ"])
    dv, ds, dt = contrast(beta, V, ix, {"ANN": 1, "UJ": -1})
    tu = res["UJ"][0] / res["UJ"][1]
    say(f"| LOYO −{y} | {fmt(res['UJ'])} | {fmt(res['ANN'])} | {dv:+.3f} ({dt:+.2f}) |")
    R6.append((f"LOYO-{y}", tu, dt))
for lab, par in (("外 奇数年", 1), ("外 偶数年", 0)):
    o = sub(2021, 2026); o = o[(o.year % 2) == par]; sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "SJ", "UJ"])
    dv, ds, dt = contrast(beta, V, ix, {"ANN": 1, "UJ": -1})
    tu = res["UJ"][0] / res["UJ"][1]
    say(f"| {lab} | {fmt(res['UJ'])} | {fmt(res['ANN'])} | {dv:+.3f} ({dt:+.2f}) |")
    R6.append((lab, tu, dt))
n_uj2 = sum(1 for _, tu, _ in R6 if tu >= 2); n_d15 = sum(1 for _, _, dt in R6 if dt < 1.5)
BREAK_E = bool((n_uj2 >= 2) or (n_d15 > len(R6) / 2))
say(f"- t(β_UJ) ≥ 2 の分割 {n_uj2}/{len(R6)}・t(ANN−UJ) < 1.5 の分割 {n_d15}/{len(R6)} → **BREAK-E** = {BREAK_E}")
say("")

# ================= R7 コスト倍 =================
say("## R7 BREAK-F: コスト倍（k·TRIG_SPREAD/risk を全腕から引く）")
say("| k | 外 ANN β(t) | 外 UJ β(t) | ANN−UJ (t) |")
say("|---|---|---|---|")
R7 = {}
for k in (1, 2, 3):
    o = sub(2021, 2026).copy(); o["Rk"] = o.Rs - k * TSP / o.risk
    sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "SJ", "UJ"], ycol="Rk")
    dv, ds, dt = contrast(beta, V, ix, {"ANN": 1, "UJ": -1})
    say(f"| {k} | {fmt(res['ANN'])} | {fmt(res['UJ'])} | {dv:+.3f} ({dt:+.2f}) |")
    R7[k] = dt
BREAK_F = bool(R7[2] < 2)
say(f"- **BREAK-F**（k=2 で t(ANN−UJ) < 2）= {BREAK_F}  [t {R7[2]:+.2f}]")
say("")

# ================= R8 純・予定外部分集合 =================
say("## R8 BREAK-G: 純・予定外 UJ（米指標の暦が無い時間帯 ET 11:00–13:00 ∪ 18:00–07:00）")
pure = ((hr[UJ5] >= 11) & (hr[UJ5] < 13)) | (hr[UJ5] >= 18) | (hr[UJ5] < 7)
UJp = UJ5[pure]; UJm = UJ5[~pure]
mp_, _ = inwin(tsf[UJp] + 300); mm_, _ = inwin(tsf[UJm] + 300)
tr["UJ_pure"] = mp_ & ~tr.ANN & ~tr.isevday; tr["UJ_macro"] = mm_ & ~tr.ANN & ~tr.isevday & ~tr.UJ_pure
say(f"- UJ 事象: 純 {len(UJp)}・暦時間帯 {len(UJm)}")
say("| 窓 | UJ_pure n/β(t) | UJ_macro n/β(t) | ANN n/β(t) | 0.5·β_ANN |")
say("|---|---|---|---|---|")
R8 = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.UJ_pure | o.UJ_macro | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "UJ_pure", "UJ_macro"])
    say(f"| {lab} | {fmt(res['UJ_pure'])} | {fmt(res['UJ_macro'])} | {fmt(res['ANN'])} | {0.5*res['ANN'][0]:+.3f} |")
    R8[lab] = res
rp = R8[EXT]["UJ_pure"]; tp = rp[0] / rp[1] if rp[1] > 0 else float("nan")
BREAK_G = bool((rp[0] >= 0.5 * R8[EXT]["ANN"][0]) and (tp >= 2))
say(f"- **BREAK-G** = {BREAK_G}  [β_UJ_pure {rp[0]:+.3f}・t {tp:+.2f}・閾値 {0.5*R8[EXT]['ANN'][0]:+.3f}]")
say("")

# ================= R9 窓の整合 =================
say("## R9 BREAK-H: 窓の整合（ANN を +300 起点に／UJ を t0 起点に）")
mA2, _ = inwin(np.r_[t_nfp, t_fomc], off=300.0)
mU2, _ = inwin(tsf[UJ5])
tr["ANN_s"] = mA2; tr["UJ_0"] = mU2 & ~tr.ANN & ~tr.isevday
say("| 版 | 外 ANN β(t) | 外 UJ β(t) | ANN−UJ (t) |")
say("|---|---|---|---|")
R9 = {}
for vlab, acol, ucol in (("ANN(+300) vs UJ(+300)", "ANN_s", "UJ"), ("ANN(t0) vs UJ(t0)", "ANN", "UJ_0")):
    o = sub(2021, 2026); sel = o[o[acol] | o[ucol] | o.ctrl]
    res, beta, V, ix, G = fit(sel, [acol, ucol])
    dv, ds, dt = contrast(beta, V, ix, {acol: 1, ucol: -1})
    say(f"| {vlab} | {fmt(res[acol])} | {fmt(res[ucol])} | {dv:+.3f} ({dt:+.2f}) |")
    R9[vlab] = dt
BREAK_H = bool(any(v < 2 for v in R9.values()))
say(f"- **BREAK-H** = {BREAK_H}  [{', '.join(f'{k}: {v:+.2f}' for k, v in R9.items())}]")
say("")

# ================= R10 事象単位 =================
say("## R10 BREAK-I: 事象単位（1 事象 1 観測）で ANN 事象 vs UJ 事象を直接比較")
from scipy import stats as st
o = sub(2021, 2026)
A = o[o.ANN].groupby("ann_t0").Rs.mean(); U = o[o.UJ].groupby("uj_t0").Rs.mean()
dm = A.mean() - U.mean()
se = math.sqrt(A.var(ddof=1) / len(A) + U.var(ddof=1) / len(U))
tw = dm / se if se > 0 else float("nan")
mw = st.mannwhitneyu(A.to_numpy(), U.to_numpy(), alternative="greater")
say(f"- 外: ANN 事象 {len(A)}（平均 {A.mean():+.3f}・中央値 {A.median():+.3f}）／UJ 事象 {len(U)}（平均 {U.mean():+.3f}・中央値 {U.median():+.3f}）")
say(f"- 差 {dm:+.3f} (Welch t {tw:+.2f})・Mann-Whitney（片側 ANN>UJ）U z 相当 p **{mw.pvalue:.4f}**")
BREAK_I = bool((tw < 2) or (mw.pvalue > 0.10))
say(f"- **BREAK-I** = {BREAK_I}")
say("")

# ================= R11 日 vs 窓 =================
say("## R11 BREAK-J: XJ = 発表日のジャンプで発表窓の外にあるもの（「発表日」か「発表窓」か）")
mX, _ = inwin(tsf[XJ5] + 300)
tr["XJ"] = mX & ~tr.ANN
say("| 窓 | XJ n/β(t) | ANN n/β(t) | UJ n/β(t) | 0.5·β_ANN |")
say("|---|---|---|---|---|")
R11 = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_); sel = o[o.ANN | o.XJ | o.UJ | o.ctrl]
    res, beta, V, ix, G = fit(sel, ["ANN", "XJ", "UJ"])
    say(f"| {lab} | {fmt(res['XJ'])} | {fmt(res['ANN'])} | {fmt(res['UJ'])} | {0.5*res['ANN'][0]:+.3f} |")
    R11[lab] = res
rx = R11[EXT]["XJ"]; tx = rx[0] / rx[1] if rx[1] > 0 else float("nan")
BREAK_J = bool((rx[0] >= 0.5 * R11[EXT]["ANN"][0]) and (tx >= 1.5))
say(f"- **BREAK-J** = {BREAK_J}  [β_XJ {rx[0]:+.3f}・t {tx:+.2f}・閾値 {0.5*R11[EXT]['ANN'][0]:+.3f}]")
say("")

# ================= 集計 =================
say("## 事前宣言した破壊規則の集計")
flags = [("BREAK-A 条件づけ非対称（発表はジャンプ不要）", BREAK_A), ("BREAK-A2 ANN_J−UJ が t<2", BREAK_A2),
         ("BREAK-B H_GEN 閾値を棄却できない", BREAK_B), ("BREAK-C 幾何調整", BREAK_C),
         ("BREAK-D 帰無校正 p>0.025", BREAK_D), ("BREAK-D2 偽 UJ の t 帰無 sd>1.3", BREAK_D2),
         ("BREAK-E 分割の再定義", BREAK_E), ("BREAK-F コスト k=2", BREAK_F),
         ("BREAK-G 純予定外で H_GEN 復活", BREAK_G), ("BREAK-H 窓の整合", BREAK_H),
         ("BREAK-I 事象単位", BREAK_I), ("BREAK-J 発表日 vs 発表窓", BREAK_J)]
for k, v in flags:
    say(f"- {'☠ landed' if v else '★ 不発'}: {k}")
nl = sum(1 for _, v in flags if v)
say("")
say(f"- landed {nl}/{len(flags)} → 判定: **{'broken' if nl else 'survived'}**（ひとつでも当たれば broken の事前宣言）")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
