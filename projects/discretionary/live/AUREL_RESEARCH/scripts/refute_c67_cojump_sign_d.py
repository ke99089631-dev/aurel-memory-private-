# -*- coding: utf-8 -*-
"""
[REFUTE c67 / 2026-11-25 04:00 反証レーン・D] C で「金自身のボラ状態で層化しても校正済み RR 1.7〜2.1 (z≈+4) が残る」
＝条件付き独立の攻撃は失敗した。だが C のプラセボ（±7〜±35 **日**ずらし）は**日をまたぐ**ので、
「株ジャンプが起きた時間帯の局所ボラ環境」は保存していない（株ジャンプは高ボラ期に塊で出る）。
つまり C の校正は過剰補正の疑いがあり、条件付き RR は [1.19, 1.97] の幅しか言えていない。

本スクリプトは**同日内の局所環境を保存するプラセボ**でそこを決める。
c67 は lag ±12 本（±1 時間）で RR が 1.6〜3.0 に平坦だと示し「ボラ状態の共有」と結論した。それなら
**「同じ日の ±30 分〜±2 時間だけずらした株ジャンプ」を基準に取れば、本物の lag+1 の RR は 1 に落ちる**はずである。
落ちれば「5 分の整列（lag+1）に固有の cross-asset 依存は無い＝RR≈2 は時間帯スケールの環境統計」＝c67 の機構読みは
正しいが「RR≈2 の裾依存」という**数字の提示の仕方**が壊れる。落ちなければ 5 分固有の成分が実在する。

=== 事前固定（数字を見る前・seed 20261125） ===
プラセボ（同日内・足ずらし）: 株ジャンプを ±6, ±12, ±18, ±24 本（30 分〜2 時間）ずらした 8 本。
  条件: ずらし元・先ともに同一 ET 日（dayid 一致）を要求＝日内の局所環境・セッションを保存。lag±1,2,3 は使わない
  （主張の近傍を避ける）。基準・層化・RR の定義は C と完全同一。
判定:
  **T1 の「5 分固有」成分は broken** ⇔ 在・外とも RR_obs / RR_pl(同日内足ずらし) < 1.3 または z_cal < 2。
  **5 分固有成分あり（T1 survived）** ⇔ 在 比 ≥1.5 ∧ z_cal ≥2 ∧ 外 比 >1.2 ∧ z_cal ≥1.5。
  **inconclusive** ⇔ その他・プラセボ MDE > 0.15。
対照: 同日内プラセボ自身の生 RR（層化なし基準に対する値）も印字する。これが c67 の lag プロファイル（±12 で 1.6〜3.0）
  と整合すれば、プラセボは意図通り「時間帯環境」を担いでいることの確認になる。
出力 data/refute_c67_cojump_sign_d.md ＋ _run.log。読取専用・書込は AUREL_RESEARCH/ 配下のみ。
"""
import os, math, time, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c67_cojump_sign_d.md"); LOG = os.path.join(DATA, "refute_c67_cojump_sign_d_run.log"); L = []
NY = "America/New_York"; SEED = 20261125; rng = np.random.default_rng(SEED)
W_SIG = 5520; THETA = 4.0; B_BOOT = 1500
BSHIFTS = (-24, -18, -12, -6, 6, 12, 18, 24)
ERAS = [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def say(s=""):
    print(s, flush=True); L.append(s)
def el(): return f"{time.time()-T0:.1f}s"
say(f"# AUREL [REFUTE c67-D] 同日内・足ずらしプラセボ: lag+1 に「5 分固有」の成分はあるか  {dt.datetime.now():%Y-%m-%d %H:%M}")
say(f"- 事前固定 = docstring・seed {SEED}・プラセボ足ずらし {BSHIFTS}（同一 ET 日を要求）・読取専用")

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
def barshift_sameday(J, k):
    """Jp[t] = J[t+k] かつ dayid[t]==dayid[t+k]（同日内）"""
    out = shift(J, k, False)
    sameday = shift(dayid, k, -10**12) == dayid
    return out & sameday
JX = E & (zX >= THETA); JS = E & (zS >= THETA)

def cells(J_lead, J_tgt, m, strata, lag=1):
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
    C = np.nansum(hj[strata[pop]] * sfac[slot_l[pop]]) / max(y[pop].sum(), 1e-9)
    ci = np.where(cond)[0]
    return y[ci], hj[strata[ci]] * sfac[slot_l[ci]] / max(C, 1e-12), dayid[ci]

def mk_none(m): return np.where(m & E, 0, -1).astype(np.int64)
def mk_joint(m):
    s = np.full(N, -1, dtype=np.int64); base = m & E & np.isfinite(vXr)
    q = np.nanquantile(vXr[base], [0.2, 0.4, 0.6, 0.8])
    dv = np.clip(np.searchsorted(q, vXr, side="right"), 0, 4)
    zb = np.clip(np.searchsorted([1, 2, 3], np.nan_to_num(zX), side="right"), 0, 3)
    s[base] = (dv * 4 + zb)[base]; return s

def boot_ratio(n1, e1, d1, n2, e2, d2, B=B_BOOT):
    days = np.unique(np.r_[d1, d2]); nd = len(days)
    g1 = np.searchsorted(days, d1); g2 = np.searchsorted(days, d2)
    N1 = np.bincount(g1, weights=n1, minlength=nd); E1 = np.bincount(g1, weights=np.nan_to_num(e1), minlength=nd)
    N2 = np.bincount(g2, weights=n2, minlength=nd); E2 = np.bincount(g2, weights=np.nan_to_num(e2), minlength=nd)
    out = np.full(B, np.nan)
    for i in range(B):
        w = np.bincount(rng.integers(0, nd, nd), minlength=nd).astype(float)
        a1 = w @ N1; b1 = w @ E1; a2 = w @ N2; b2 = w @ E2
        if a1 > 0 and b1 > 0 and a2 > 0 and b2 > 0: out[i] = math.log((a1 / b1) / (a2 / b2))
    return float(np.nanstd(out, ddof=1)), nd

say("\n## D1 同日内・足ずらしプラセボで校正した lag+1 RR")
say("| 窓 | 層化 | 観測 N/E RR | 同日内プラセボ N/E RR (z・MDE) | **比 = RR_obs/RR_pl** | **z_cal（日クラスタ）** |")
say("|---|---|---|---|---|---|")
RES = {}
for name, lo_, hi_ in ERAS:
    m = era_mask(lo_, hi_)
    for sname, mk in (("なし（c67）", mk_none), ("v_X5×z_X4", mk_joint)):
        s = mk(m)
        n1, e1, d1 = cells(JS, JX, m, s)
        n2s, e2s, d2s = [], [], []
        for k in BSHIFTS:
            Jp = barshift_sameday(JS, k)
            a, b, c = cells(Jp, JX, m, s); n2s.append(a); e2s.append(b); d2s.append(c)
        n2 = np.concatenate(n2s); e2 = np.concatenate(e2s); d2 = np.concatenate(d2s)
        RR = n1.sum() / np.nansum(e1); Epl = np.nansum(e2); RRpl = n2.sum() / Epl
        zpl = (n2.sum() - Epl) / math.sqrt(Epl); mde_pl = 2 / math.sqrt(Epl)
        ratio = RR / RRpl; se, nd = boot_ratio(n1, e1, d1, n2, e2, d2)
        zc = math.log(ratio) / se if se > 0 else np.nan
        RES[(name, sname)] = dict(RR=RR, RRpl=RRpl, ratio=ratio, z=zc, mde_pl=mde_pl)
        say(f"| {name} | {sname} | {int(n1.sum())}/{np.nansum(e1):.2f} {RR:.2f} | {int(n2.sum())}/{Epl:.1f} {RRpl:.2f} "
            f"(z {zpl:+.2f}・MDE {mde_pl:.3f}) | **{ratio:.2f}** | **{zc:+.2f}** |")

say("\n## D2 判定（事前固定）")
for sname in ("なし（c67）", "v_X5×z_X4"):
    A = RES[("在 2014-20", sname)]; Bo = RES[("外 2021-26H1", sname)]
    brk = (A["ratio"] < 1.3 or A["z"] < 2) and (Bo["ratio"] < 1.3 or Bo["z"] < 2)
    srv = (A["ratio"] >= 1.5 and A["z"] >= 2 and Bo["ratio"] > 1.2 and Bo["z"] >= 1.5)
    bad = max(A["mde_pl"], Bo["mde_pl"]) > 0.15
    v = "inconclusive（プラセボ MDE 不足）" if bad else ("**5 分固有成分 broken**" if brk else ("**5 分固有成分あり**" if srv else "inconclusive"))
    say(f"- 層化 {sname}: 在 比 {A['ratio']:.2f} (z {A['z']:+.2f})／外 比 {Bo['ratio']:.2f} (z {Bo['z']:+.2f}) → {v}")
say(f"\n- 実行 {el()}・読取専用・発注/本番編集/MT5/外部通信/プロップ参照 なし・書込は AUREL_RESEARCH/data 配下のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); open(LOG, "w", encoding="utf-8").write("\n".join(L) + "\n")
