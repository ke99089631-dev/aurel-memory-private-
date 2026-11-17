# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-18 03:30 / 第 3 段 = c47 自身の復活条件を独立事象集合で執行]
c47 の「次の枝 (a)」は、補足 b の弱信号（DiD_W3 ANN_J−UJ 外 +0.492 t 2.5）を
**US500 npz の独立事象集合**（c45 検出器・SJ/UJ 分規則・NFP/FOMC/CPI の公表足）で 1 セル事前固定し直すと書いた。
復活条件（c47 の原文）: 「DiD_W3 ANN_J − UJ > 0 ∧ t≥2（2014-20）∧ 外 同符号 t≥1.5」。
本段はその条件を**レーンの代わりに執行**する（反証レーンは同じ検定を別の切り口で壊す役なので、
レーンが自分で決めた復活条件を独立標本で先に走らせることが最も安い破壊になる）。

=== 事前固定（数字を見る前・この docstring が正本） ===
データ: data/macro/US500_m5_close.npz（1481760 本 2012-01-01〜2026-06-09・完全格子・前値埋め・flat 46.4%・
        **欠落営業日 平日 97 日**（2020 年 68 日ほか・DATA_MAP §80）→ 読込時に年別欠落と flat を印字する ㊵）
        ＋ FOMC_dates.csv・CPI_dates.csv・NFP c24 v2 規則。XAU は一切使わない（独立標本）。
        scan 無し・M5 読込なし・MT5 無し・外部通信なし・発注なし・本番編集なし。
検出器・窓・対照は c45/c47 と**完全同一の規約**（銘柄だけ差し替え）:
  r bp・σ_trail = 直前 5520 足の非 flat RMS（足自身を含まない・非 flat ≥1000）・z=|r|/σ。
  候補 = 非 flat ∧ 直前 3 足 非 flat ∧ ET 月〜金 ∧ 17:00〜18:10 ET を除く。ジャンプ = z ≥ 5。decluster 4 h 先着採用。
  ANN_J = NFP 08:30／FOMC（scheduled・2013-03-20+）14:00／CPI 08:30 ET の公表足で z≥5。ANN_NJ = 同 z<5（記述）。
  SJ = 非 NFP/FOMC/CPI 日のジャンプで足開始分 ∈ {00,15,30,45}／UJ = 同 ∈ {05,10,20,25,35,40,50,55}。
  窓 PRE −12..−1／W1 1..12／W2 13..24／W3 25..48（主）／W4 49..96・最低非 flat 足 6/6/6/12/24・足 0 除外。
  ρ_k = log(RV_k/σ_trail²(t0))・対照 = 同 ET 時:分・月〜金・±28 暦日・非 NFP/FOMC/CPI 日・非 flat ∧ z<5 ∧ 直前 4 h ジャンプ無し・K=4 無作為。
  E_k = ρ_k − mean_K ρ_k(対照)（対照 ≥2 本）。
窓期 = **在 2014-20**（c47 の指定・σ_trail 暖機と 2012-13 の薄い板を避ける）／**外 2021-26H1**。D2 遵守（16 年一括なし）。
推定 = c47 と同一（E ~ 1{ANN_J} + log z + ET 時刻 FE・ET 日クラスタ）。

破壊規則:
 T1 BREAK-US500（主判定）: c47 の復活条件 **DiD_W3 > 0 ∧ 在 t≥2 ∧ 外 同符号 t≥1.5** を US500 で評価。
    **当たり条件 = 条件が成立しない**（＝弱信号は独立事象集合で復活しない）。MDE 2se を必ず印字（不成立が検出力不足由来かを区別する）。
 T2 BREAK-US500-ADJ: 同じ US500 で第 1 段 R3 の正しい仕様（E_W3 ~ 1{ANN_J} + E_PRE + log z + 時刻 FE）。
    **当たり条件 = 外 |t| < 1.5**。併記: US500 の λ（非事象適格足の母集団・ρ_W3 ~ ρ_PRE）と腕別 Ē_PRE。
 T3 BREAK-US500-PREGAP（機構の前提の検証）: 金で DiD を機械的に偏らせた前提は「UJ の Ē_PRE ≫ ANN_J の Ē_PRE」。
    US500 でも **Ē_PRE,UJ − Ē_PRE,ANN_J ≥ +0.30（外）** なら同じ機械項が働くので、T1 の結果は金の結果と同じ読み方になる。
    **当たり条件 = PRE 差 ≥ +0.30**（＝独立標本でも「ジャンプは状態の症状」が再現＝c47 の PRE 事実は頑健）。
 T4（記述・判定外）: 腕別 A_W3 = Ē_W3 − λ_pop·Ē_PRE（第 2 段 S2 と同じ量）を US500 で。
    金で S2 が示した「UJ も状態を作る」が独立標本で再現するか。W1 も併記（公表の直後効果は教科書なので陽性対照になる）。
seed 20261118。出力 data/refute_c47_did_us500.md。読取専用。
"""
import os, math, time, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c47_did_us500.md"); L = []
NY = "America/New_York"; SEED = 20261118; rng = np.random.default_rng(SEED)
W_SIG = 5520; K_CTRL = 4; DAYS = 28; DECL = 14400
WINS = {"PRE": (-12, -1, 6), "W1": (1, 12, 6), "W2": (13, 24, 6), "W3": (25, 48, 12), "W4": (49, 96, 24)}
ERAS = [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026)]
WD = "月火水木金土日"

def say(s=""):
    print(s, flush=True); L.append(s)

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def dummies(vals):
    u = sorted(pd.unique(vals))[1:]
    if not u: return np.zeros((len(vals), 0))
    return np.column_stack([(np.asarray(vals) == v).astype(float) for v in u])

def fit(o, ycol, treat, ctrlarm, extra=()):
    o = o[(o.cls == treat) | (o.cls == ctrlarm)]
    cols = [ycol] + list(extra) + ["logz"]
    o = o[np.isfinite(o[cols]).all(axis=1)]
    if (o.cls == treat).sum() < 5 or (o.cls == ctrlarm).sum() < 5: return np.nan, np.nan, {}, 0, 0
    d = (o.cls == treat).to_numpy(float); y = o[ycol].to_numpy(float)
    parts = [np.ones(len(o)), d]; names = ["const", "treat"]
    for c in extra: parts.append(o[c].to_numpy(float)); names.append(c)
    parts.append(o.logz.to_numpy(float)); names.append("logz")
    H = dummies(o.hr.to_numpy())
    if H.shape[1]: parts.append(H); names += [f"hr{j}" for j in range(H.shape[1])]
    X = np.column_stack(parts)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    cf = {n: (beta[i], math.sqrt(max(V[i, i], 0))) for i, n in enumerate(names) if n in extra}
    return beta[1], math.sqrt(max(V[1, 1], 0)), cf, int((o.cls == treat).sum()), int((o.cls == ctrlarm).sum())

def tt(b, se): return (b / se) if (se and se > 0 and np.isfinite(se)) else float("nan")
def f2(b, se): return f"{b:+.3f} (t {tt(b,se):+.2f})"

def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d12 = pd.Timestamp(year=y, month=m, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

say("# [REFUTE 2026-11-18 03:30 第3段] c47 の復活条件を US500 の独立事象集合で執行")
say(f"- 事前固定 = docstring（T1〜T3 を数字を見る前に宣言）・seed {SEED}・主判定 = T1（c47 の原文の復活条件）")
say("")

# ---------- US500 npz ----------
zz = np.load(os.path.join(MAC, "US500_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
N = len(ts); tt_ = pd.to_datetime(ts, unit="s", utc=True); tny = tt_.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yrs = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
say(f"- US500_m5_close: {N} 本 {tt_[0]}〜{tt_[-1]} UTC・flat 全体 {(~nf).mean()*100:.1f}%・曜日別 " +
    " ".join(f"{WD[w]}{(~nf[wd==w]).mean()*100:.0f}%" for w in range(7)) + "（衛生 ⑩⑪）")
# 欠落営業日（㊵）
bd = pd.bdate_range(tny[0].tz_localize(None).normalize(), tny[-1].tz_localize(None).normalize())
have = set(pd.DatetimeIndex(etdate[nf]).unique())
miss = pd.DatetimeIndex([d for d in bd if d not in have])
mc = pd.Series(1, index=miss).groupby(miss.year).sum() if len(miss) else pd.Series(dtype=int)
say(f"- **欠落営業日 {len(miss)} 日**（年別: " + "／".join(f"{y}:{c}" for y, c in mc.items()) + f"）・最長連続 "
    f"{int(max([len(list(g)) for _, g in __import__('itertools').groupby(enumerate(miss), lambda t: t[1].toordinal()-t[0])], default=0))} 日（㊵・DATA_MAP §80 と一致確認）")
r2 = np.where(nf, r * r, 0.0); c2 = np.r_[0.0, np.cumsum(r2)]; cn = np.r_[0, np.cumsum(nf.astype(np.int64))]
idx = np.arange(N); lo_ = idx - 1 - W_SIG; hi_ = idx - 1; valid = (lo_ >= 0)
S2_ = np.where(valid, c2[np.clip(hi_ + 1, 0, N)] - c2[np.clip(lo_ + 1, 0, N)], np.nan)
NN_ = np.where(valid, cn[np.clip(hi_ + 1, 0, N)] - cn[np.clip(lo_ + 1, 0, N)], 0)
sig = np.sqrt(np.where(NN_ >= 1000, S2_ / np.maximum(NN_, 1), np.nan)); z = np.abs(r) / sig

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
NFP = nfp_dates_v2(); CPI = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(pd.DatetimeIndex(F.date).normalize()) + list(CPI.normalize()))))
isevbar = np.asarray(etdate.isin(evdays))
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))

# ---------- ジャンプ検出（c45 規約） ----------
prev3 = nf & np.r_[False, nf[:-1]] & np.r_[False, False, nf[:-2]] & np.r_[False, False, False, nf[:-3]]
cand = prev3 & trading & np.isfinite(sig) & (z >= 5.0)
ci = idx[cand]
keep = []; last_t = -10 ** 18
for i in ci:                      # decluster 4 h・先着採用（c45 と同一）
    if ts[i] - last_t >= DECL: keep.append(i); last_t = ts[i]
keep = np.array(keep, np.int64)
say(f"- ジャンプ候補 {len(ci)} → decluster 4 h 先着採用で **{len(keep)}** 事象（c45 と同一規約）")
J5 = np.sort(ts[keep])
JK = pd.DataFrame({"idx": keep})
JK["evday"] = isevbar[keep]; JK["mn"] = mn[keep]
JK["cls"] = np.where(JK.evday, "ANNDAY_J", np.where(JK.mn.isin([0, 15, 30, 45]), "SJ", "UJ"))

def ann_bars(dates, h, m, kind):
    t = epoch_et(dates, h, m); t = t[np.isfinite(t)].astype(np.int64)
    p = np.clip(np.searchsorted(ts, t), 0, N - 1); ok = ts[p] == t
    return pd.DataFrame({"idx": p[ok], "kind": kind})
A = pd.concat([ann_bars(NFP, 8, 30, "NFP"), ann_bars(FOMC_ANN, 14, 0, "FOMC"), ann_bars(CPI, 8, 30, "CPI")], ignore_index=True)
A = A[A.idx.map(lambda i: np.isfinite(sig[i]) and nf[i])].copy()
A["z"] = z[A.idx.to_numpy()]; A["cls"] = np.where(A.z >= 5, "ANN_J", "ANN_NJ")
U = JK[JK.cls.isin(["UJ", "SJ"])][["idx", "cls"]].copy(); U["z"] = z[U.idx.to_numpy()]; U["kind"] = U.cls
EV = pd.concat([A[["idx", "kind", "cls", "z"]], U[["idx", "kind", "cls", "z"]]], ignore_index=True)
EV["ts"] = ts[EV.idx]; EV["hr"] = hr[EV.idx]; EV["mn"] = mn[EV.idx]; EV["year"] = yrs[EV.idx]
EV["day"] = etdate[EV.idx.to_numpy()].strftime("%Y-%m-%d"); EV["r"] = r[EV.idx]
EV["logz"] = np.log(EV.z.clip(lower=0.1))
say("| 窓 | ANN_J（NFP／FOMC／CPI） | ANN_NJ | UJ | SJ | ANN_J z 中央値 | UJ z 中央値 | ANN_J \\|r\\| 中央値 bp | UJ \\|r\\| |")
say("|---|---|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    e = EV[(EV.year >= lo) & (EV.year <= hi)]; aj = e[e.cls == "ANN_J"]; uj = e[e.cls == "UJ"]
    say(f"| {lab} | {len(aj)}（{(aj.kind=='NFP').sum()}／{(aj.kind=='FOMC').sum()}／{(aj.kind=='CPI').sum()}） | {(e.cls=='ANN_NJ').sum()} | {len(uj)} | {(e.cls=='SJ').sum()} | "
        f"{aj.z.median():.2f} | {uj.z.median():.2f} | {np.abs(aj.r).median():.1f} | {np.abs(uj.r).median():.1f} |")
say("- UJ の ET 時刻分布: " + " ".join(f"{h}:{c}" for h, c in EV[EV.cls == 'UJ'].hr.value_counts().sort_index().items()))
say("")

# ---------- 対照 ----------
last_j = np.searchsorted(J5, ts, side="right") - 1
since_j = np.where(last_j >= 0, ts - J5[np.clip(last_j, 0, None)], 10 ** 9)
elig = nf & trading & ~isevbar & np.isfinite(sig) & (z < 5) & (since_j >= DECL)
slot = hr * 60 + mn
slot_idx = {s_: idx[elig & (slot == s_)] for s_ in np.unique(slot[elig])}
say(f"- 対照適格足 {int(elig.sum())}")

def win_logrv(ii, a, b, nmin):
    ii = np.asarray(ii, np.int64); out = np.full(len(ii), np.nan)
    ok = (ii + a >= 0) & (ii + b < N)
    s = c2[np.clip(ii + b + 1, 0, N)] - c2[np.clip(ii + a, 0, N)]
    n = cn[np.clip(ii + b + 1, 0, N)] - cn[np.clip(ii + a, 0, N)]
    good = ok & (n >= nmin) & (s > 0); out[good] = np.log(s[good] / n[good]); return out

def draw_ctrl(ev_idx, K=K_CTRL):
    out = np.full((len(ev_idx), K), -1, np.int64); ncand = np.zeros(len(ev_idx), int)
    for n_, i in enumerate(ev_idx):
        arr = slot_idx.get(slot[i])
        if arr is None: continue
        a = np.searchsorted(ts[arr], ts[i] - DAYS * 86400); b = np.searchsorted(ts[arr], ts[i] + DAYS * 86400, side="right")
        c = arr[a:b]; c = c[c != i]; ncand[n_] = len(c)
        if len(c) == 0: continue
        pick = rng.choice(c, size=min(K, len(c)), replace=False); out[n_, :len(pick)] = pick
    return out, ncand

C_IDX, NCAND = draw_ctrl(EV.idx.to_numpy())
say(f"- 対照候補数 中央値 {np.median(NCAND):.0f}・<2 本 {(NCAND<2).sum()}／{len(NCAND)}・K=4 確保率 {(NCAND>=4).mean()*100:.1f}%")

def excess(ev_idx, c_idx, a, b, nmin):
    rho_e = win_logrv(ev_idx, a, b, nmin) - 2 * np.log(sig[ev_idx])
    rc = np.full(c_idx.shape, np.nan)
    for k in range(c_idx.shape[1]):
        ok = c_idx[:, k] >= 0
        if ok.any():
            ci_ = c_idx[ok, k]; rc[ok, k] = win_logrv(ci_, a, b, nmin) - 2 * np.log(sig[ci_])
    nval = np.isfinite(rc).sum(1)
    rcm = np.where(nval >= 2, np.nanmean(rc, axis=1), np.nan)
    return rho_e - rcm, rho_e, rcm

for w, (a, b, nmin) in WINS.items():
    E_, rho_, rc_ = excess(EV.idx.to_numpy(), C_IDX, a, b, nmin)
    EV["E_" + w] = E_; EV["rho_" + w] = rho_; EV["rc_" + w] = rc_
for w in ["W1", "W2", "W3", "W4"]: EV["d" + w] = EV["E_" + w] - EV["E_PRE"]
say(f"- E_W3 有効率: ANN_J {np.isfinite(EV[EV.cls=='ANN_J'].E_W3).mean()*100:.0f}%・UJ {np.isfinite(EV[EV.cls=='UJ'].E_W3).mean()*100:.0f}%"
    f"（FOMC 14:00 の W3 は 16:05〜18:00 ET で現物引け・17:00 ブレイクを跨ぐため欠損が出る＝事前に想定した穴）")
say("")
def sub(lo, hi): return EV[(EV.year >= lo) & (EV.year <= hi)]

# ---------- T1 BREAK-US500（主判定） ----------
say("## T1 BREAK-US500（主判定・c47 の復活条件を独立事象集合で）")
say("| 窓 | k | ANN_J Ē (n) | UJ Ē (n) | **DiD = ΔE_k の ANN_J−UJ (t)** | MDE 2se | 水準 D_k (t) | D_PRE (t) |")
say("|---|---|---|---|---|---|---|---|")
T1 = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    bp, sep, _, _, _ = fit(o, "E_PRE", "ANN_J", "UJ")
    for w in ["W1", "W2", "W3", "W4"]:
        bd_, sed_, _, nt, nc = fit(o, "d" + w, "ANN_J", "UJ")
        bl, sel, _, _, _ = fit(o, "E_" + w, "ANN_J", "UJ")
        aj = o[o.cls == "ANN_J"]["d" + w]; uj = o[o.cls == "UJ"]["d" + w]
        bold = "**" if w == "W3" else ""
        say(f"| {lab} | {w} | {np.nanmean(aj):+.3f} ({np.isfinite(aj).sum()}) | {np.nanmean(uj):+.3f} ({np.isfinite(uj).sum()}) | "
            f"{bold}{f2(bd_,sed_)}{bold} | {2*sed_:.3f} | {f2(bl,sel)} | {f2(bp,sep)} |")
        T1[(lab, w)] = (bd_, sed_)
bi, si = T1[("在 2014-20", "W3")]; bo, so = T1[("外 2021-26H1", "W3")]
ti, to = tt(bi, si), tt(bo, so)
pass_c47 = (bi > 0) and (ti >= 2) and (bo > 0) and (to >= 1.5)
t1_hit = not pass_c47
say(f"- c47 の復活条件 = DiD_W3 > 0 ∧ 在 t≥2 ∧ 外 同符号 t≥1.5 → 在 {bi:+.3f} (t {ti:+.2f}・MDE {2*si:.3f})／外 {bo:+.3f} (t {to:+.2f}・MDE {2*so:.3f})")
say(f"- **T1 判定: {'☠BREAK-US500 が当たった（復活条件は独立事象集合で成立しない）' if t1_hit else '★不発（c47 の弱信号は US500 で復活した）'}**")
say("")

# ---------- T2 BREAK-US500-ADJ ----------
say("## T2 BREAK-US500-ADJ（US500 で正しい仕様: PRE 共変量）")
pool = idx[elig & np.isfinite(win_logrv(idx, -12, -1, 6)) ]
rpre = win_logrv(idx, -12, -1, 6) - 2 * np.log(sig); rw3 = win_logrv(idx, 25, 48, 12) - 2 * np.log(sig)
say("| 窓 | DiD_W3（λ=1） | **PRE 共変量 β_ANN (t)** | λ̂（仕様内） | λ_pop（非事象適格足） | MDE 2se |")
say("|---|---|---|---|---|---|")
T2 = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    bd_, sed_, _, _, _ = fit(o, "dW3", "ANN_J", "UJ")
    ba, sea, cf, nt, nc = fit(o, "E_W3", "ANN_J", "UJ", extra=("E_PRE",))
    lh, lhse = cf.get("E_PRE", (np.nan, np.nan))
    p = pool[(yrs[pool] >= lo) & (yrs[pool] <= hi) & np.isfinite(rw3[pool]) & np.isfinite(rpre[pool])]
    if len(p) > 40000: p = rng.choice(p, size=40000, replace=False)
    H = dummies(hr[p]); X = np.column_stack([np.ones(len(p)), rpre[p], H])
    bq, Vq, _ = ols_cluster(rw3[p], X, etdate[p].strftime("%Y-%m-%d").to_numpy())
    say(f"| {lab} | {f2(bd_,sed_)} | **{f2(ba,sea)}** | {lh:+.3f} (t(λ−1) {(lh-1)/lhse:+.1f}) | {bq[1]:+.3f} (n {len(p)}) | {2*sea:.3f} |")
    T2[lab] = (ba, sea, bq[1])
ba_o, sea_o, lam_o = T2["外 2021-26H1"]
t2_hit = abs(tt(ba_o, sea_o)) < 1.5
say(f"- **T2 判定: {'☠BREAK-US500-ADJ が当たった' if t2_hit else '★不発'}** [外 {ba_o:+.3f} t {tt(ba_o,sea_o):+.2f}]")
say("")

# ---------- T3 BREAK-US500-PREGAP ----------
say("## T3 BREAK-US500-PREGAP（「ジャンプは状態の症状」が独立標本で再現するか = 機械項の前提）")
say("| 窓 | ANN_J Ē_PRE (t) | UJ Ē_PRE (t) | SJ Ē_PRE | **PRE 差 UJ−ANN_J** | 機械項 (1−λ_pop)·PRE差 | 実測 DiD_W3 |")
say("|---|---|---|---|---|---|---|")
T3 = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    def m_(arm, col="E_PRE"):
        x = o[o.cls == arm][col].dropna()
        return x.mean(), (x.mean() / (x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 2 else np.nan), len(x)
    a_, at, an = m_("ANN_J"); u_, ut, un = m_("UJ"); s_, _, _ = m_("SJ")
    gap = u_ - a_; lam = T2[lab][2]; mech = (1 - lam) * gap
    say(f"| {lab} | {a_:+.3f} (t {at:+.1f}・n {an}) | {u_:+.3f} (t {ut:+.1f}・n {un}) | {s_:+.3f} | **{gap:+.3f}** | {mech:+.3f} | {T1[(lab,'W3')][0]:+.3f} |")
    T3[lab] = gap
t3_hit = T3["外 2021-26H1"] >= 0.30
say(f"- **T3 判定: {'☠BREAK-US500-PREGAP が当たった（PRE 不均衡は独立標本でも再現＝機械項は同じく働く）' if t3_hit else '★不発（US500 では PRE 不均衡が小さい）'}** [外 PRE 差 {T3['外 2021-26H1']:+.3f}]")
say("")

# ---------- T4（記述）A_腕 ----------
say("## T4（記述・判定外）US500 の腕別 PRE 調整済み超過水準 A_k = Ē_k − λ_pop·Ē_PRE（第 2 段 S2 の US500 版）")
say("| 窓 | 腕 | n | Ē_PRE | A_W1 (vol 比) | A_W3 (vol 比) | ΔE_W3（λ=1） |")
say("|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    lam = T2[lab][2]; o = sub(lo, hi)
    for arm in ["ANN_J", "UJ", "SJ"]:
        s = o[(o.cls == arm)]
        if len(s) < 10: continue
        pre = s.E_PRE.mean()
        a1 = s.E_W1.mean() - lam * pre; a3 = s.E_W3.mean() - lam * pre
        say(f"| {lab} | {arm} | {len(s)} | {pre:+.3f} | {a1:+.3f} ({math.exp(a1/2):.2f}) | {a3:+.3f} ({math.exp(a3/2):.2f}) | {(s.E_W3-s.E_PRE).mean():+.3f} |")
say("")
say("## 第 3 段まとめ")
for nm, h in [("T1 BREAK-US500（主判定）", t1_hit), ("T2 BREAK-US500-ADJ", t2_hit), ("T3 BREAK-US500-PREGAP", t3_hit)]:
    say(f"- {'☠ 当たり' if h else '★ 不発'} {nm}")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
