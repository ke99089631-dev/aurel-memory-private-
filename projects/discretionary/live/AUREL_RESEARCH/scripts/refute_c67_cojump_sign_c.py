# -*- coding: utf-8 -*-
"""
[REFUTE c67 / 2026-11-25 03:55 反証レーン・C] B の判定が inconclusive になった原因を潰す。
B で 金自身の状態（z_X,t・v_X,t）で基準を層化すると S→X lag1 RR は 在 2.68→1.57／外 2.25→1.19 に落ちたが、
**同じ層化基準の下で +7 日プラセボが 0.70〜0.89 に漂った**（n 12／29・|z|≤1.26 ＝ 1 と区別できない）。
プラセボで割り戻すと 在 2.26／外 1.48 に戻る。つまり「層化で消えた」のか「層化基準が 20〜30% 過大予測している」のか、
プラセボの標本が小さすぎて分離できない＝これが inconclusive の正体。

本スクリプトは**プラセボの質量を 10 倍にして校正定数を固定する**。
=== 事前固定（数字を見る前・seed 20261125） ===
プラセボ = 株ジャンプ系列を ±7/±14/±21/±28/±35 暦日ずらした 10 本（同曜日・同スロットを保つ）。
  各ずらしで B と同一の層化 RR を計算し、(n_i, e_i, ET 日) を**全ずらしでプール**→ RR_pl。
  se は ET 日クラスタ bootstrap B=1500（分子セルとプラセボを**同じ日の再抽出で同時に**再計算し、log(RR/RR_pl) の se を取る）。
校正済み RR = RR_obs / RR_pl。層化は B と同じ 4 本（なし・z_X 4 ビン・v_X decile・v_X5×z_X4）。
判定（T1 = 「株↔金の裾依存 RR≈2 は金自身のボラ状態を超える cross-asset な実在」）:
  **broken** ⇔ 外 2021-26H1 で 最も細かい層化（v_X5×z_X4）の 校正済み RR < 1.3 または z_cal < 1.5（c67 自身の外ゲート）
             かつ 在でも 校正済み RR < 1.5 または z_cal < 2。
  **partially broken（外のみ）** ⇔ 外が上の条件を満たし、在は満たさない（＝在残差は残るが外で再現しない
             ＝c67 の in→out 規則に照らすと「3 窓で実在」は言えない）。
  **survived** ⇔ 在 校正済み RR ≥1.5 ∧ z_cal ≥2 ∧ 外 校正済み RR >1.2 ∧ z_cal ≥1.5。
  **inconclusive** ⇔ プラセボの MDE（2/√ΣE_pl）> 0.15（校正が依然として甘い）など上記以外。
出力 data/refute_c67_cojump_sign_c.md ＋ _run.log。読取専用・書込は AUREL_RESEARCH/ 配下のみ。
"""
import os, math, time, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c67_cojump_sign_c.md"); LOG = os.path.join(DATA, "refute_c67_cojump_sign_c_run.log"); L = []
NY = "America/New_York"; SEED = 20261125; rng = np.random.default_rng(SEED)
W_SIG = 5520; THETA = 4.0; B_BOOT = 1500
SHIFTS = (-35, -28, -21, -14, -7, 7, 14, 21, 28, 35)
ERAS = [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def say(s=""):
    print(s, flush=True); L.append(s)
def el(): return f"{time.time()-T0:.1f}s"
say(f"# AUREL [REFUTE c67-C] プラセボ質量 10 倍で層化基準を校正し T1 を判定  {dt.datetime.now():%Y-%m-%d %H:%M}")
say(f"- 事前固定 = docstring・seed {SEED}・プラセボずらし {SHIFTS} 日・読取専用")

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
ts, iX, iS = np.intersect1d(tsX, tsS, assume_unique=True, return_indices=True)
rX, nfX, nf3X, sigX = rX[iX], nfX[iX], nf3X[iX], sigX[iX]; rS, nfS, nf3S, sigS = rS[iS], nfS[iS], nf3S[iS], sigS[iS]
N = len(ts)
tny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yr = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize()); isev = np.asarray(etdate.isin(evdays))
dayid = etdate.to_numpy().astype("datetime64[D]").astype(np.int64)
assert len(np.unique(dayid)) > 1000, "dayid 退化"
slot = (hr * 12 + mn // 5).astype(np.int64)
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
E = nf3X & nf3S & np.isfinite(sigX) & np.isfinite(sigS) & trading & ~isev
zX = np.abs(rX / sigX); zS = np.abs(rS / sigS)
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
def dayshift(a, days, fill=False):
    pos = np.searchsorted(ts, ts - days * 86400); pos = np.clip(pos, 0, N - 1); ok = ts[pos] == ts - days * 86400
    out = np.full(N, fill, dtype=a.dtype); out[ok] = a[pos[ok]]; return out
JX = E & (zX >= THETA); JS = E & (zS >= THETA)

def cells(J_lead, J_tgt, m, strata, lag=1):
    """B と同一の層化基準（次足率・pop 校正）で (n_i, e_i, dayid) を返す"""
    ok = (shift(ts, lag, -10**12) - ts) == 300 * lag
    pop = m & E & shift(E, lag, False) & ok & (strata >= 0) & ~J_tgt
    cond = pop & J_lead
    y = shift(J_tgt, lag, False).astype(float); slot_l = shift(slot, lag, 0)
    nstr = int(strata.max()) + 1
    bj = np.bincount(strata[pop], minlength=nstr).astype(float)
    cj = np.bincount(strata[pop], weights=y[pop], minlength=nstr).astype(float)
    hj = np.where(bj > 0, cj / np.maximum(bj, 1), np.nan)
    sb = np.bincount(slot_l[pop], minlength=288).astype(float)
    sc = np.bincount(slot_l[pop], weights=y[pop], minlength=288).astype(float)
    hp = y[pop].mean()
    sfac = np.where(sb > 0, (sc / np.maximum(sb, 1)) / max(hp, 1e-12), 1.0)
    pred_pop = hj[strata[pop]] * sfac[slot_l[pop]]
    C = np.nansum(pred_pop) / max(y[pop].sum(), 1e-9)
    ci = np.where(cond)[0]
    return y[ci], hj[strata[ci]] * sfac[slot_l[ci]] / max(C, 1e-12), dayid[ci]

def mk_none(m): return np.where(m & E, 0, -1).astype(np.int64), 1
def mk_zx(m):
    s = np.full(N, -1, dtype=np.int64)
    for j, (a_, b_) in enumerate([(0, 1), (1, 2), (2, 3), (3, 4)]): s[m & E & (zX >= a_) & (zX < b_)] = j
    return s, 4
def mk_v(m, nq=10):
    s = np.full(N, -1, dtype=np.int64); base = m & E & np.isfinite(vXr)
    q = np.nanquantile(vXr[base], np.linspace(0, 1, nq + 1))
    dec = np.clip(np.searchsorted(q[1:-1], vXr, side="right"), 0, nq - 1); s[base] = dec[base]; return s, nq
def mk_joint(m):
    s = np.full(N, -1, dtype=np.int64); base = m & E & np.isfinite(vXr)
    q = np.nanquantile(vXr[base], [0.2, 0.4, 0.6, 0.8])
    dv = np.clip(np.searchsorted(q, vXr, side="right"), 0, 4)
    zb = np.clip(np.searchsorted([1, 2, 3], np.nan_to_num(zX), side="right"), 0, 3)
    s[base] = (dv * 4 + zb)[base]; return s, 20

def boot_ratio(n1, e1, d1, n2, e2, d2, B=B_BOOT):
    """同じ日の再抽出で RR_obs と RR_pl を同時に再計算 → log(RR_obs/RR_pl) の se"""
    days = np.unique(np.r_[d1, d2]); nd = len(days)
    g1 = np.searchsorted(days, d1); g2 = np.searchsorted(days, d2)
    N1 = np.bincount(g1, weights=n1, minlength=nd); E1 = np.bincount(g1, weights=np.nan_to_num(e1), minlength=nd)
    N2 = np.bincount(g2, weights=n2, minlength=nd); E2 = np.bincount(g2, weights=np.nan_to_num(e2), minlength=nd)
    out = np.full(B, np.nan)
    for i in range(B):
        w = np.bincount(rng.integers(0, nd, nd), minlength=nd).astype(float)
        a1 = (w @ N1); b1 = (w @ E1); a2 = (w @ N2); b2 = (w @ E2)
        if a1 > 0 and b1 > 0 and a2 > 0 and b2 > 0: out[i] = math.log((a1 / b1) / (a2 / b2))
    return float(np.nanstd(out, ddof=1)), nd

say("\n## C1 プラセボ 10 本プールで校正した層化 RR")
say("| 窓 | 層化 | 観測 N/E RR | プラセボ N/E RR (Poisson z・MDE) | **校正 RR = RR/RR_pl** | **z_cal（日クラスタ）** | nd |")
say("|---|---|---|---|---|---|---|")
RES = {}
for name, lo_, hi_ in ERAS:
    m = era_mask(lo_, hi_)
    for sname, mk in (("なし（c67）", mk_none), ("z_X,t 4 ビン", mk_zx), ("v_X,t decile", mk_v), ("v_X5×z_X4", mk_joint)):
        s, _ = mk(m)
        n1, e1, d1 = cells(JS, JX, m, s)
        n2s, e2s, d2s = [], [], []
        for sh in SHIFTS:
            Jp = dayshift(JS, sh)
            a, b, c = cells(Jp, JX, m, s); n2s.append(a); e2s.append(b); d2s.append(c)
        n2 = np.concatenate(n2s); e2 = np.concatenate(e2s); d2 = np.concatenate(d2s)
        RR = n1.sum() / np.nansum(e1); Epl = np.nansum(e2)
        RRpl = n2.sum() / Epl; zpl = (n2.sum() - Epl) / math.sqrt(Epl)
        mde_pl = 2 / math.sqrt(Epl)
        cal = RR / RRpl
        se, nd = boot_ratio(n1, e1, d1, n2, e2, d2)
        RES[(name, sname)] = dict(RR=RR, RRpl=RRpl, cal=cal, z=math.log(cal) / se if se > 0 else np.nan,
                                  mde_pl=mde_pl, npl=n2.sum(), Epl=Epl)
        say(f"| {name} | {sname} | {int(n1.sum())}/{np.nansum(e1):.2f} {RR:.2f} | {int(n2.sum())}/{Epl:.1f} {RRpl:.3f} "
            f"(z {zpl:+.2f}・MDE {mde_pl:.3f}) | **{cal:.2f}** | **{math.log(cal)/se if se>0 else float('nan'):+.2f}** | {nd} |")

say("\n## C2 判定（事前固定・T1）")
A = RES[("在 2014-20", "v_X5×z_X4")]; Bo = RES[("外 2021-26H1", "v_X5×z_X4")]
say(f"- 最も細かい層化 v_X5×z_X4: 在 校正 RR {A['cal']:.2f} (z {A['z']:+.2f})／外 校正 RR {Bo['cal']:.2f} (z {Bo['z']:+.2f})"
    f"・プラセボ MDE 在 {A['mde_pl']:.3f}／外 {Bo['mde_pl']:.3f}")
pl_ok = max(A["mde_pl"], Bo["mde_pl"]) <= 0.15
out_fail = (Bo["cal"] < 1.3) or (Bo["z"] < 1.5)
in_fail = (A["cal"] < 1.5) or (A["z"] < 2)
srv = (A["cal"] >= 1.5 and A["z"] >= 2 and Bo["cal"] > 1.2 and Bo["z"] >= 1.5)
if not pl_ok: v = "inconclusive（プラセボ校正が依然甘い）"
elif out_fail and in_fail: v = "**T1 broken**"
elif out_fail: v = "**T1 partially broken（外で再現しない＝「3 窓で実在」は言えない）**"
elif srv: v = "**T1 survived**"
else: v = "inconclusive"
say(f"- **結論（T1）: {v}**")
say(f"\n- 実行 {el()}・読取専用・発注/本番編集/MT5/外部通信/プロップ参照 なし・書込は AUREL_RESEARCH/data 配下のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); open(LOG, "w", encoding="utf-8").write("\n".join(L) + "\n")
