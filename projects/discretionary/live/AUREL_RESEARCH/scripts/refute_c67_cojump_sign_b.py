# -*- coding: utf-8 -*-
"""
[REFUTE c67 / 2026-11-25 03:50 反証レーン・B] 対象 = cycle67 のもう一方の肯定形主張 T1:
  「株と金の 5 分ジャンプの**裾依存は実在する**（S→X lag1 RR 在 2.44 z +6.25／外 2.01 z +5.65・3 窓・θ 4/5・
    プラセボ +7d ≈1）。その形は ±1 時間で対称・平坦なボラ状態の共有である」

c67 は lag プロファイル・時間反転・用量反応で「1 本先行遅行」を自分で壊したが、**「RR≈2 の裾依存そのもの」は
実在として残した**。本スクリプトはそこを壊しに行く。筋 2 本:
 (i) **条件付き独立**: c67 の基準は スロット×窓 の平均ジャンプ率だけで、**金自身の今の荒れ**を条件にしていない。
     c67 自身の用量反応（株 z<1 の次足で RR 0.79）と自己クラスタ RR 6.8 は「次に跳ぶかは自分の状態で決まる」を示す。
     そこで基準を **金自身の状態（z_X,t ビン／金の短期ボラ比 v_X,t decile）で層化**して Mantel–Haenszel で束ねる。
     層内で RR→1 なら「株のジャンプは金自身の荒れを超える情報を持たない」＝T1 は cross-asset な主張として壊れる。
 (ii) **SE の濫用**: c67 の z は Poisson（事象独立仮定）。ジャンプは日内クラスタする。**ET 日クラスタ bootstrap**で
     RR の se を取り直し、z がどこまで落ちるかを見る（コスト倍の代わりの独立性ストレス）。
 (iii) look-ahead: 基準率 h(slot) は窓全体（＝未来の足）で推定されている。**拡張窓（t 未満のみ・収縮推定）**で
     基準を作り直して RR が動くかを見る。

=== 事前固定（数字を見る前に書いた・seed 20261125） ===
データ・検出器・適格足・窓・rr_lag の定義は c67 と同一（複製）。θ=4 主・5 感度。
層化変数（いずれも t 時点で既知）: (a) z_X,t ビン {[0,1),[1,2),[2,3),[3,4)}（事象は ¬JX_t を要求するので z_X,t<4）
  (b) v_X,t = RMS(r_X, 直前 12 足)/σ_trail,X の decile（足自身を含まない）(c) (a)×セッション（US 現物/外）。
各層 j: N_j = #{JS_t ∧ ¬JX_t ∧ JX_{t+1}}・E_j = Σ_cond h_j(slot(t+1))。h_j = 層 j・窓内の適格足の金ジャンプ率
  （スロット調整は乗法: h_j(slot) = h_j × h(slot)/h_pool・層内スロット推定の薄さを避ける）。
  MH 束ね: RR_MH = Σ N_j / Σ E_j（層内の期待を足す＝交絡の層別調整）。z_cluster = ET 日クラスタ bootstrap B=1500。
判定（事前固定）:
  **T1 broken（cross-asset の主張として）** ⇔ 在・外の両窓で 層化後 RR_MH < 1.3 または z_cluster < 2。
  **T1 survived** ⇔ 在 RR_MH ≥ 1.5 ∧ z_cluster ≥ 2 ∧ 外 RR_MH > 1.2 ∧ z_cluster ≥ 1.5。
  **inconclusive** ⇔ 中間、または層化後 MDE(=2/√ΣE) > 0.5（検出力不足）。
対照: 同じ層化で +7d プラセボ ≈1 を要求（層化が基準を壊していないことの確認）。時間反転 RR(−1) も層化後に印字。
加えて T2 の補強検査（A の続き）: (iv) **θ=0（全適格足）の符号一致率と arcsine 則 0.5+arcsin(ρ)/π** を印字し、
  「裾の一致率」が「本体の一致率」からどれだけ離れているかを同じ尺度で測る。(v) 2020 の欠落（A の R3d で
  26496 足 drop）を日単位で詰める: 2020 の ET 日のうち共通格子に残った割合・月別・drop 日の XAU ボラ。
出力 data/refute_c67_cojump_sign_b.md ＋ _run.log。読取専用・書込は AUREL_RESEARCH/ 配下のみ。
"""
import os, math, time, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c67_cojump_sign_b.md"); LOG = os.path.join(DATA, "refute_c67_cojump_sign_b_run.log"); L = []
NY = "America/New_York"; SEED = 20261125; rng = np.random.default_rng(SEED)
W_SIG = 5520; THETA = 4.0; B_BOOT = 1500
ERAS = [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def say(s=""):
    print(s, flush=True); L.append(s)
def el(): return f"{time.time()-T0:.1f}s"

say(f"# AUREL [REFUTE c67-B] RR≈2 の裾依存は「金自身の荒れ」を超える情報か  {dt.datetime.now():%Y-%m-%d %H:%M}")
say(f"- 事前固定 = docstring・seed {SEED}・c67 の検出器/適格足/窓を複製・読取専用")

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
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); FOMC_ALL = pd.DatetimeIndex(pd.to_datetime(F["date"]))
CPI = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
evdays = pd.DatetimeIndex(sorted(set(list(nfp_dates_v2().normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
    nf = np.isfinite(r) & (r != 0)
    r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
    idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = lo >= 0
    S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
    NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
    sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
    nf3 = nf.copy()
    for k in (1, 2, 3): nf3 &= np.r_[[False] * k, nf[:-k]]
    return ts, r, nf, nf3, sig
tsX, rX, nfX, nf3X, sigX = load("XAU"); tsS, rS, nfS, nf3S, sigS = load("US500")
rX_full, nfX_full = rX.copy(), nfX.copy()
ts, iX, iS = np.intersect1d(tsX, tsS, assume_unique=True, return_indices=True)
rX, nfX, nf3X, sigX = rX[iX], nfX[iX], nf3X[iX], sigX[iX]; rS, nfS, nf3S, sigS = rS[iS], nfS[iS], nf3S[iS], sigS[iS]
N = len(ts)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yr = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize()); isev = np.asarray(etdate.isin(evdays))
dayid = etdate.to_numpy().astype("datetime64[D]").astype(np.int64)
assert len(np.unique(dayid)) > 1000, "dayid 退化"
slot = (hr * 12 + mn // 5).astype(np.int64)
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
E = nf3X & nf3S & np.isfinite(sigX) & np.isfinite(sigS) & trading & ~isev
uX = rX / sigX; uS = rS / sigS; zX = np.abs(uX); zS = np.abs(uS)
cash = ((hr * 60 + mn) >= 9 * 60 + 30) & ((hr * 60 + mn) < 16 * 60)

def short_rms(r, nf, w=12):
    r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
    idx = np.arange(len(r)); lo = idx - 1 - w; hi = idx - 1; ok = lo >= 0
    S2 = np.where(ok, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
    NN = np.where(ok, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
    return np.sqrt(np.where(NN >= 6, S2 / np.maximum(NN, 1), np.nan))
vXr = short_rms(rX, nfX) / sigX
say(f"- 共通格子 {N}・適格足 {int(E.sum())}  ({el()})")

def era_mask(lo_, hi_): return (yr >= lo_) & (yr <= hi_)
def shift(a, lag, fill):
    out = np.full(N, fill, dtype=a.dtype)
    if lag > 0: out[:-lag] = a[lag:]
    elif lag < 0: out[-lag:] = a[:lag]
    else: out[:] = a
    return out
pos7 = np.searchsorted(ts, ts - 7 * 86400); pos7 = np.clip(pos7, 0, N - 1); ok7 = ts[pos7] == ts - 7 * 86400
def shifted(a, fill=False):
    out = np.full(N, fill, dtype=a.dtype); out[ok7] = a[pos7[ok7]]; return out

JX = E & (zX >= THETA); JS = E & (zS >= THETA); JSpl = shifted(JS)

def strat_rr(J_lead, J_tgt, m, strata, lag=1, excl_same=True, slotadj=True):
    """層化 RR。基準 = 「t の層」を与えた時の **t+lag での標的ジャンプ率**（同一足率ではない: 層を t で切るので
    標的が t で跳んだ足は層から落ちてしまい基準が 0 になる＝第 1 版のバグ）。比較母集団 base は cond と同じ制約
    （適格・次足適格・¬J_tgt(t)・層 >=0）に揃える。スロット調整は乗法 h_j×sfac(slot_{t+lag}) で、**base 上で
    Σ期待 = Σ実現 になるよう定数 C で再正規化**（層とスロットが相関するため積は自動では校正されない＝第 1 版で
    プラセボが 0.42 になった原因）。戻り: N, E, cond, rows, dayids, n_i, e_i, placebo 用の C"""
    ok = (shift(ts, lag, -10**12) - ts) == 300 * lag
    pop = m & E & shift(E, lag, False) & ok & (strata >= 0)
    if excl_same: pop &= ~J_tgt
    cond = pop & J_lead
    y = shift(J_tgt, lag, False).astype(float); slot_l = shift(slot, lag, 0)
    nstr = int(strata.max()) + 1
    bj = np.bincount(strata[pop], minlength=nstr).astype(float)
    cj = np.bincount(strata[pop], weights=y[pop], minlength=nstr).astype(float)
    hj = np.where(bj > 0, cj / np.maximum(bj, 1), np.nan)
    if slotadj:
        sb = np.bincount(slot_l[pop], minlength=288).astype(float)
        sc = np.bincount(slot_l[pop], weights=y[pop], minlength=288).astype(float)
        hp = y[pop].mean()
        sfac = np.where(sb > 0, (sc / np.maximum(sb, 1)) / max(hp, 1e-12), 1.0)
    else:
        sfac = np.ones(288)
    pred_pop = hj[strata[pop]] * sfac[slot_l[pop]]
    C = np.nansum(pred_pop) / max(y[pop].sum(), 1e-9)      # base 上で校正
    ci = np.where(cond)[0]
    e_i = hj[strata[ci]] * sfac[slot_l[ci]] / max(C, 1e-12)
    n_i = y[ci]
    rows = []
    for j in range(nstr):
        sel = strata[ci] == j
        if sel.sum() == 0: continue
        rows.append((j, int(sel.sum()), n_i[sel].sum(), np.nansum(e_i[sel]), int(bj[j]), hj[j]))
    return n_i.sum(), np.nansum(e_i), len(ci), rows, dayid[ci], n_i, e_i

def boot_rr(days, n_i, e_i, B=B_BOOT):
    d = np.unique(days); nd = len(d); g = np.searchsorted(d, days)
    Nj = np.bincount(g, weights=n_i, minlength=nd); Ej = np.bincount(g, weights=np.nan_to_num(e_i), minlength=nd)
    out = np.empty(B)
    for i in range(B):
        w = np.bincount(rng.integers(0, nd, nd), minlength=nd).astype(float)
        den = w @ Ej; out[i] = (w @ Nj) / den if den > 1e-9 else np.nan
    o = np.log(np.clip(out, 1e-9, None))
    return float(np.nanstd(o, ddof=1)), nd   # log RR の se

# ---------- 複製（層化なし・c67 の主セル） ----------
ALL0 = np.zeros(N, dtype=np.int64)   # 単一層 = c67 と同じ
say("\n## B0 複製と SE の作り直し（c67 の主セル S→X lag1・層化なし）")
say("| 窓 | N/E | RR | c67 の RR | Poisson z | **日クラスタ z（log RR）** | nd | Poisson/クラスタ se 比 |")
say("|---|---|---|---|---|---|---|---|")
C67RR = {"在 2014-20": 2.44, "外 2021-26H1": 2.01, "近年 2024-26H1": 2.78}
B0 = {}
for name, lo_, hi_ in ERAS:
    m = era_mask(lo_, hi_)
    n, e, c, rows, dd, ni, ei = strat_rr(JS, JX, m, ALL0)
    rr = n / e; zp = (n - e) / math.sqrt(e)
    se_log, nd = boot_rr(dd, ni, ei)
    zc = math.log(rr) / se_log if se_log > 0 else np.nan
    se_log_pois = 1 / math.sqrt(max(n, 1))
    B0[name] = dict(rr=rr, zp=zp, zc=zc, nd=nd, n=n, e=e)
    say(f"| {name} | {int(n)}/{e:.2f} | {rr:.2f} | {C67RR[name]:.2f} | {zp:+.2f} | **{zc:+.2f}** | {nd} | {se_log/se_log_pois:.2f} |")

# ---------- B1 層化（金自身の状態） ----------
def mk_strata_zx(m):
    s = np.full(N, -1, dtype=np.int64)
    bins = [(0, 1), (1, 2), (2, 3), (3, 4)]
    for j, (a_, b_) in enumerate(bins):
        s[m & E & (zX >= a_) & (zX < b_)] = j
    return s, [f"z_X[{a_},{b_})" for a_, b_ in bins]
def mk_strata_v(m, nq=10):
    s = np.full(N, -1, dtype=np.int64)
    base = m & E & np.isfinite(vXr)
    q = np.nanquantile(vXr[base], np.linspace(0, 1, nq + 1))
    dec = np.clip(np.searchsorted(q[1:-1], vXr, side="right"), 0, nq - 1)
    s[base] = dec[base]
    return s, [f"v_X d{j}" for j in range(nq)]
def mk_strata_joint(m):
    s = np.full(N, -1, dtype=np.int64)
    base = m & E & np.isfinite(vXr)
    q = np.nanquantile(vXr[base], [0.2, 0.4, 0.6, 0.8])
    dv = np.clip(np.searchsorted(q, vXr, side="right"), 0, 4)
    zb = np.clip(np.searchsorted([1, 2, 3], np.nan_to_num(zX), side="right"), 0, 3)
    lab = (dv * 4 + zb)
    s[base] = lab[base]
    return s, [f"v{j//4}×z{j%4}" for j in range(20)]

say("\n## B1 層化 RR（Mantel–Haenszel・基準を金自身の状態で層別）")
say("| 窓 | 層化 | 層数(使用) | N/ΣE | **RR_MH** | Poisson z | **日クラスタ z** | MDE | +7d プラセボ N/E RR (z) | **プラセボ校正 RR** | 時間反転 RR(−1) |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
B1 = {}
for name, lo_, hi_ in ERAS[:2]:
    m = era_mask(lo_, hi_)
    for sname, mk in (("なし（c67）", lambda mm: (ALL0.copy(), ["all"])),
                      ("z_X,t 4 ビン", mk_strata_zx), ("v_X,t decile", mk_strata_v), ("v_X 5×z_X 4", mk_strata_joint)):
        s, labs = mk(m)
        if sname == "なし（c67）": s = np.where(m & E, 0, -1)
        n, e, c, rows, dd, ni, ei = strat_rr(JS, JX, m, s)
        if e <= 0 or n == 0: say(f"| {name} | {sname} | — | — | — | — | — | — | — | — |"); continue
        rr = n / e; zp = (n - e) / math.sqrt(e); se_log, nd = boot_rr(dd, ni, ei)
        zc = math.log(rr) / se_log if se_log > 0 else np.nan
        npl, epl, *_ = strat_rr(JSpl, JX, m, s); rrpl = npl / epl if epl > 0 else np.nan
        zpl = (npl - epl) / math.sqrt(epl) if epl > 0 else np.nan
        nrv, erv, *_ = strat_rr(JS, JX, m, s, lag=-1); rrrv = nrv / erv if erv > 0 else np.nan
        mde = 2 / math.sqrt(e); rrcal = rr / rrpl if rrpl and np.isfinite(rrpl) and rrpl > 0 else np.nan
        B1[(name, sname)] = dict(rr=rr, zp=zp, zc=zc, mde=mde, rrpl=rrpl, zpl=zpl, rrcal=rrcal, rrrv=rrrv, n=n, e=e)
        say(f"| {name} | {sname} | {len(rows)} | {int(n)}/{e:.2f} | **{rr:.2f}** | {zp:+.2f} | **{zc:+.2f}** | {mde:.2f} | "
            f"{int(npl)}/{epl:.1f} {rrpl:.2f} (z {zpl:+.2f}) | **{rrcal:.2f}** | {rrrv:.2f} |")

say("\n### B1-2 層内の内訳（z_X,t ビン別・在/外）: 層内で RR が 1 に近づくか")
say("| 窓 | 層 | 層の適格足 | 層の金ジャンプ率 h_j | cond | N/E | RR |")
say("|---|---|---|---|---|---|---|")
for name, lo_, hi_ in ERAS[:2]:
    m = era_mask(lo_, hi_); s, labs = mk_strata_zx(m)
    n, e, c, rows, dd, ni, ei = strat_rr(JS, JX, m, s)
    for j, cj, nj, ej, bj, hj in rows:
        say(f"| {name} | {labs[j]} | {bj} | {hj*100:.3f}% | {cj} | {int(nj)}/{ej:.2f} | {nj/ej if ej>0 else float('nan'):.2f} |")

# ---------- B2 look-ahead: 拡張窓（causal）基準 ----------
say("\n## B2 look-ahead: 基準率を拡張窓（t 未満のみ・収縮 k=200）で作り直す")
say("| 窓 | 窓全体基準 RR | **拡張窓基準 RR** | 差 |")
say("|---|---|---|---|")
order = np.lexsort((np.arange(N), slot))
sl_sorted = slot[order]
grp_start = np.searchsorted(sl_sorted, np.arange(288))
for name, lo_, hi_ in ERAS[:2]:
    m = era_mask(lo_, hi_)
    base = m & E
    bi = base[order].astype(np.int64); ji = (base & JX)[order].astype(np.int64)
    cb = np.cumsum(bi); cj = np.cumsum(ji)
    # 位置 p（order 内）での「同スロット・自分より前」の件数
    pos_in = np.empty(N, dtype=np.int64); pos_in[order] = np.arange(N)
    off_b = cb[np.clip(grp_start - 1, 0, None)]; off_b[grp_start == 0] = 0
    off_j = cj[np.clip(grp_start - 1, 0, None)]; off_j[grp_start == 0] = 0
    p = pos_in
    prev_b = cb[p] - bi[p] - off_b[slot]; prev_j = cj[p] - ji[p] - off_j[slot]
    cum_b_all = np.cumsum(base.astype(np.int64)); cum_j_all = np.cumsum((base & JX).astype(np.int64))
    p_pool = np.where(cum_b_all > 0, cum_j_all / np.maximum(cum_b_all, 1), np.nan)
    K = 200.0
    h_caus = (prev_j + K * np.nan_to_num(p_pool)) / (prev_b + K)
    ok = (shift(ts, 1, -10**12) - ts) == 300
    cond = m & E & shift(E, 1, False) & ok & JS & ~JX
    tgt_l = shift(JX, 1, False);
    ci = np.where(cond)[0]
    # 基準は t+1 のスロットで評価（c67 と同じ）→ 拡張窓の h は t+1 の時点（自分を除く）
    e_c = h_caus[np.clip(ci + 1, 0, N - 1)]
    n_c = tgt_l[ci].astype(float)
    keep = np.isfinite(e_c) & (e_c > 0)
    rr_c = n_c[keep].sum() / e_c[keep].sum()
    say(f"| {name} | {B0[name]['rr']:.2f} | **{rr_c:.2f}** | {rr_c-B0[name]['rr']:+.2f} |")

# ---------- B3 T2 補強: 本体 vs 裾の同じ尺度 ----------
say("\n## B3 T2 補強: 「裾」の符号一致率を「本体」と同じ尺度で並べる（arcsine 則）")
say("| 窓 | ρ_core | 全適格足の符号一致率（θ=0） | arcsine 予測 0.5+asin(ρ)/π | θ=4 共跳の一致率 | 裾−本体 |")
say("|---|---|---|---|---|---|")
for name, lo_, hi_ in ERAS[:2]:
    m = era_mask(lo_, hi_) & E
    core = m & (zX < THETA) & (zS < THETA)
    x = uX[core]; y = uS[core]; k = np.isfinite(x) & np.isfinite(y)
    rho = float(np.corrcoef(x[k], y[k])[0, 1])
    ag0 = (np.sign(rX[m]) == np.sign(rS[m])).mean()
    arc = 0.5 + math.asin(rho) / math.pi
    co = m & (zX >= THETA) & (zS >= THETA)
    ag4 = (np.sign(rX[co]) == np.sign(rS[co])).mean()
    say(f"| {name} | {rho:+.4f} | {ag0*100:.1f}% | {arc*100:.1f}% | {ag4*100:.1f}% | {(ag4-ag0)*100:+.1f}pt |")

# ---------- B4 2020 の欠落を日単位で ----------
say("\n## B4 衛生: 2020 の欠落（A の R3d の 26496 足）を日単位で詰める")
dX = pd.to_datetime(tsX, unit="s", utc=True).tz_convert(NY)
dayX_all = pd.DatetimeIndex(dX.tz_localize(None).normalize())
dropX = np.setdiff1d(tsX, ts)
dd_drop = pd.DatetimeIndex(pd.to_datetime(dropX, unit="s", utc=True).tz_convert(NY).tz_localize(None).normalize())
keepdays = set(pd.DatetimeIndex(pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY).tz_localize(None).normalize()).unique())
for y in (2014, 2019, 2020, 2021):
    sel = dayX_all.year == y
    allday = pd.DatetimeIndex(dayX_all[sel]).unique()
    gone = [d for d in allday if d not in keepdays]
    mcount = pd.Series([d.month for d in gone]).value_counts().sort_index() if gone else pd.Series(dtype=int)
    say(f"- {y}: XAU 側の ET 日 {len(allday)} のうち共通格子に 1 本も残らない日 **{len(gone)}**"
        + (f"・月別 " + " ".join(f"{k}月:{v}" for k, v in mcount.items()) if gone else ""))
# drop 日の XAU ボラ（2020 限定）
absr = np.where(nfX_full, np.abs(rX_full), 0.0)
dkey = dayX_all.to_numpy().astype("datetime64[D]").astype(np.int64)
dfv = pd.DataFrame({"d": dkey, "a": absr, "nf": nfX_full.astype(int), "y": dayX_all.year}).groupby(["y", "d"]).agg(s=("a", "sum"), k=("nf", "sum"))
dfv = dfv[dfv["k"] >= 50].reset_index()
keep_i = set(pd.DatetimeIndex(sorted(keepdays)).to_numpy().astype("datetime64[D]").astype(np.int64).tolist())
dfv["kept"] = [int(d) in keep_i for d in dfv["d"]]
for y in (2020,):
    sub = dfv[dfv["y"] == y]
    k1 = sub[~sub["kept"]]["s"].to_numpy(); k0 = sub[sub["kept"]]["s"].to_numpy()
    if len(k1) >= 5 and len(k0) >= 5:
        t_ = (k1.mean() - k0.mean()) / math.sqrt(k1.var(ddof=1) / len(k1) + k0.var(ddof=1) / len(k0))
        say(f"- {y}: 落ちた日の XAU 日次 Σ|r| {k1.mean():.0f} bp (n {len(k1)}) vs 残った日 {k0.mean():.0f} bp (n {len(k0)})・Welch t {t_:+.2f}")
    else:
        say(f"- {y}: 落ちた日 {len(k1)}・残った日 {len(k0)}（判定に足りない）")

# ---------- 判定 ----------
say("\n## 判定（事前固定の規則・T1）")
res = []
for name in ("在 2014-20", "外 2021-26H1"):
    best = [B1[(name, s)] for s in ("z_X,t 4 ビン", "v_X,t decile", "v_X 5×z_X 4") if (name, s) in B1]
    res.append((name, best))
def worst(bs, key): return min(b[key] for b in bs)
a_name, a_b = res[0]; b_name, b_b = res[1]
brk = (worst(a_b, "rr") < 1.3 or worst(a_b, "zc") < 2) and (worst(b_b, "rr") < 1.3 or worst(b_b, "zc") < 2)
srv = (min(b["rr"] for b in a_b) >= 1.5 and min(b["zc"] for b in a_b) >= 2
       and min(b["rr"] for b in b_b) > 1.2 and min(b["zc"] for b in b_b) >= 1.5)
mde_bad = max(max(b["mde"] for b in a_b), max(b["mde"] for b in b_b)) > 0.5
say(f"- 層化後の最悪ケース: 在 RR {worst(a_b,'rr'):.2f}・z_cluster {worst(a_b,'zc'):+.2f}／外 RR {worst(b_b,'rr'):.2f}・z_cluster {worst(b_b,'zc'):+.2f}・最大 MDE {max(max(b['mde'] for b in a_b), max(b['mde'] for b in b_b)):.2f}")
verdict = "inconclusive（検出力不足）" if mde_bad else ("**T1 broken**" if brk else ("**T1 survived**" if srv else "inconclusive"))
say(f"- **結論（T1）: {verdict}**")
say(f"\n- 実行 {el()}・読取専用・発注/本番編集/MT5/外部通信/プロップ参照 なし・書込は AUREL_RESEARCH/data 配下のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); open(LOG, "w", encoding="utf-8").write("\n".join(L) + "\n")
