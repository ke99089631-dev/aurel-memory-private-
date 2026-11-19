# -*- coding: utf-8 -*-
"""
[REFUTE c55-b] 2026-11-20 — 第 1 走（refute_c55_venue_open.py）の 2 つの弱点の修理と感度。seed 20261120。
定義の変更は無い。判定閾値は第 1 走の docstring で凍結したものを引き継ぐ。

B1 【自分の A4 の欠陥を直す】第 1 走の A4 は開場スロットを **ET 時計のスロット番号**で表現した。
    SGE 01:00 UTC と London 08:00 は DST で ET スロットが 2 つに割れる（03:05/03:10・04:05/04:10・
    20:05/20:10・21:05/21:10）ため、
      (a) 分子に窓外の UJ が混ざる（観測 192 ≠ 開場窓事象 180）
      (b) 分母 N も窓の一部しか対応しない
    → 各会場を**自分の時計で**集計し直し、ET 完全一致の 4 スロット（08:20/08:25/09:35/09:40）と
      会場別に、段差回帰（log UJ 率 ~ log median(|r|/σ_trail)）の予測との比を出す。
    さらに残差が「開場という class」か「08:20 の 1 スロット」かを分けて示す（08:20 を抜いた版）。
B2 【自分の A7 の弱点】NYSE の vol 整合対照が 1 スロット（33/2821）しか残らなかった。
    許容幅を ±7.5%（第 1 走）/ ±15% / ±25% で振り、対照スロット数と ρ_matched の安定性を出す。
    再開条件は第 1 走と同一（在 ρ≥1.3 ∧ z≥2 ∧ p≤0.0125 ∧ 外 ρ>1）。
B3 【c55 の結論(3)「開場で裾が軽いのは実質的」への攻撃】近傍対照 C（c55）と vol 整合対照の ρ を
    同じ表に並べ、負の ρ が vol 勾配で何%説明されるかを出す。
読むのは data/macro/XAU_m5_close.npz・FOMC/CPI csv のみ。scan 無し・MT5 無し・外部通信無し。
"""
import os, time, math
import numpy as np, pandas as pd
from scipy.stats import norm

T0 = time.time(); SEED = 20261120
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c55_venue_open_b.md")
NY = "America/New_York"
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
def S(h, m): return h * 12 + m // 5

say(f"# [REFUTE c55-b] 第 1 走の修理と感度 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c55_venue_open_b.py・seed {SEED})")

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

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
evdays = pd.DatetimeIndex(sorted(set(list(nfp_dates_v2().normalize()) + list(pd.DatetimeIndex(F.date).normalize()) +
                                     list(pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date).normalize()))))

zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize()); year = tt.year.to_numpy()
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
W_SIG = 5520; DECL = 14400.0; ZMAIN = 5.0
r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = (lo >= 0)
S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
nf3 = nf.copy()
for k in (1, 2, 3): nf3 &= np.r_[[False] * k, nf[:-k]]
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
cand = nf3 & trading & np.isfinite(sig)
zabs = np.abs(r) / sig
isevbar = np.asarray(etdate.isin(evdays))
uj_slot = (mn % 15 != 0)
etslot = (tny.hour * 12 + tny.minute // 5).to_numpy()

def decluster(mask, decl=DECL):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= decl: keep.append(i); last = ts[i]
    return np.array(keep, int)

J5 = decluster(cand & (zabs >= ZMAIN))
UJ = J5[(~isevbar[J5]) & uj_slot[J5]]
pool_uj = cand & (~isevbar) & uj_slot
say(f"- 複製: 5σ declustered {len(J5)}・UJ {len(UJ)}（c45 2166/937）")

step = np.where(np.isfinite(sig) & nf, np.abs(r) / sig, np.nan)
CLK = {}
def slots(name):
    if name not in CLK:
        tl = tt if name == "UTC" else tt.tz_convert(name)
        CLK[name] = ((tl.hour * 12 + tl.minute // 5).to_numpy(), tl.weekday.to_numpy())
    return CLK[name]

VENUES = [("SGE 01:00 UTC", "UTC", S(1, 0), 3), ("London 08:00", "Europe/London", S(8, 0), 3),
          ("COMEX 08:20 ET", NY, S(8, 20), 2), ("NYSE 09:30 ET", NY, S(9, 30), 3)]

# ===================== B1 =====================
say("\n## B1 段差回帰の予測との比（各会場を自分の時計で・第 1 走 A4 の ET スロット混線を修理）")
def step_reg(clockname):
    sl, _ = slots(clockname); rows = []
    for s in range(288):
        m = pool_uj & (sl == s)
        if m.sum() < 200: continue
        rows.append((s, int(m.sum()), int((sl[UJ] == s).sum()), float(np.nanmedian(step[m]))))
    D = pd.DataFrame(rows, columns=["s", "N", "k", "x"]); D = D[D.x > 0]
    rate = (D.k + 0.5) / D.N
    X = np.c_[np.ones(len(D)), np.log(D.x.to_numpy())]; yv = np.log(rate.to_numpy()); w = D.N.to_numpy().astype(float)
    XtW = X.T * w; b = np.linalg.solve(XtW @ X, XtW @ yv)
    D["pred_k"] = np.exp(X @ b) * D.N
    return D, b

REG = {}
for cn_ in ["UTC", "Europe/London", NY]:
    REG[cn_] = step_reg(cn_)
    say(f"- 時計 {cn_}: log(UJ率) = {REG[cn_][1][0]:.2f} + **{REG[cn_][1][1]:+.2f}**·log(median |r|/σ_trail)・{len(REG[cn_][0])} スロット")

tot_obs = tot_exp = 0.0
for vn, ck, osl, wl in VENUES:
    D, b = REG[ck]
    ws = [(osl + k) % 288 for k in range(wl)]
    sub = D[D.s.isin(ws) & D.s.isin([s for s in ws if (s * 5) % 15 != 0 or True])]
    # UJ になれるのは分%15≠0 のスロットのみ（スロット番号→分 = (s%12)*5）
    sub = sub[sub.s.map(lambda s: ((s % 12) * 5) % 15 != 0)]
    o = int(sub.k.sum()); e = float(sub.pred_k.sum()); tot_obs += o; tot_exp += e
    se = math.sqrt(1 / max(o, 1)); rt = o / e if e > 0 else np.nan
    say(f"- **{vn}**: UJ eligible スロット {[f'{s//12:02d}:{(s%12)*5:02d}' for s in sorted(sub.s)]}・"
        f"観測 {o} vs 段差予測 {e:.1f} → **{rt:.2f}×** [{rt*math.exp(-1.96*se):.2f}, {rt*math.exp(1.96*se):.2f}]")
rt_all = tot_obs / tot_exp; se_all = math.sqrt(1 / max(tot_obs, 1))
say(f"- **4 会場合算**: 観測 {int(tot_obs)} vs 段差予測 {tot_exp:.1f} → **{rt_all:.2f}×** "
    f"[{rt_all*math.exp(-1.96*se_all):.2f}, {rt_all*math.exp(1.96*se_all):.2f}]（第 1 走 A4 の 1.49× は ET 混線版）")
# 08:20 を抜く
D, b = REG[NY]
s820 = S(8, 20)
o8 = int(D[D.s == s820].k.sum()); e8 = float(D[D.s == s820].pred_k.sum())
rt_x = (tot_obs - o8) / (tot_exp - e8); se_x = math.sqrt(1 / max(tot_obs - o8, 1))
say(f"- 08:20 ET 単独: 観測 {o8} vs 予測 {e8:.1f} → **{o8/e8:.2f}×**／08:20 を除いた残り 7 スロット: "
    f"観測 {int(tot_obs-o8)} vs 予測 {tot_exp-e8:.1f} → **{rt_x:.2f}×** [{rt_x*math.exp(-1.96*se_x):.2f}, {rt_x*math.exp(1.96*se_x):.2f}]")
B1_CLASS = (rt_x * math.exp(-1.96 * se_x) > 1.0)
say(f"- **B1 判定**: 08:20 を除いても段差超過が残るか = {'残る（開場 class に上乗せ）' if B1_CLASS else '残らない（残差は 08:20 の 1 スロット）'}")

# ===================== B2/B3 =====================
say("\n## B2/B3 vol 整合対照の許容幅感度と、c55 近傍対照 C との並置")
def c55_z(clockname):
    sl, wdl = slots(clockname)
    ok = nf & ~((etslot >= S(17, 0)) & (etslot <= S(18, 5))) & (wdl <= 4)
    df = pd.DataFrame({"y": year[ok], "s": sl[ok], "r": r[ok]})
    g = df.groupby(["y", "s"])["r"]
    med = g.transform("median")
    mad = (df["r"] - med).abs().groupby([df["y"], df["s"]]).transform("median")
    n = g.transform("size")
    sg = 1.4826 * mad.to_numpy(); sg[n.to_numpy() < 100] = np.nan
    zc = np.full(len(r), np.nan); zc[ok] = df["r"].to_numpy() / sg
    return sl, zc, ok & np.isfinite(zc)

def ann_excl(clockname):
    ex = set()
    if clockname == NY:
        for h, m in [(8, 30), (8, 35), (10, 0), (10, 5), (14, 0), (14, 5)]: ex.add(S(h, m))
    if clockname == "Europe/London":
        for h, m in [(7, 0), (7, 5)]: ex.add(S(h, m))
    if clockname == "UTC":
        for h, m in [(1, 15), (1, 20)]: ex.add(S(h, m))
    return ex

def pair(mW, mC, jump, msk):
    JW = int((msk & mW & jump).sum()); NW = int((msk & mW).sum())
    JC = int((msk & mC & jump).sum()); NC = int((msk & mC).sum())
    rW = JW / max(NW, 1); rC = JC / max(NC, 1); rho = rW / rC if rC > 0 else np.nan
    se = math.sqrt(1 / max(JW, 0.5) + 1 / max(JC, 0.5)); zs = math.log(rho) / se if rho and rho > 0 else np.nan
    return dict(JW=JW, NW=NW, JC=JC, NC=NC, rho=rho, z=zs, p=(1 - norm.cdf(zs)) if np.isfinite(zs) else np.nan)

PERIODS = [("在", 2010, 2020), ("外", 2021, 2026), ("近年", 2024, 2026)]
ZC = {}
REOPEN = False
for vn, ck, osl, wl in VENUES:
    if ck not in ZC: ZC[ck] = c55_z(ck)
    sl, zc, okc = ZC[ck]; ex = ann_excl(ck)
    Wsl = [(osl + k) % 288 for k in range(wl) if ((osl + k) % 288) not in ex]
    mW = np.isin(sl, Wsl); jump = np.abs(zc) >= 4
    m_in = okc & (year >= 2010) & (year <= 2020)
    vW = float(np.median(np.abs(r[m_in & mW])))
    # c55 の近傍対照
    Cn = [s % 288 for s in list(range(osl - 12, osl)) + list(range(osl + wl, osl + wl + 12))]
    Cn = [s for s in Cn if s not in ex and s not in Wsl]
    mCn = np.isin(sl, Cn)
    say(f"- **{vn}**（W median|r| {vW:.2f} bp）")
    for pn, y0, y1 in PERIODS:
        msk = okc & (year >= y0) & (year <= y1); d = pair(mW, mCn, jump, msk)
        say(f"  - {pn} c55 近傍対照 C（{len(Cn)} 足）: ρ {d['rho']:.2f}（z {d['z']:+.2f}）")
    for tol in (0.075, 0.15, 0.25):
        near = set((osl + k) % 288 for k in range(-2, wl + 2))
        cs = []
        for s in range(288):
            if s in near or s in ex: continue
            m = m_in & (sl == s)
            if m.sum() < 300: continue
            v = float(np.median(np.abs(r[m])))
            if v > 0 and abs(math.log(v / vW)) <= math.log(1 + tol): cs.append(s)
        mC = np.isin(sl, cs)
        out = []
        for pn, y0, y1 in PERIODS:
            msk = okc & (year >= y0) & (year <= y1); d = pair(mW, mC, jump, msk)
            out.append((pn, d))
        a = dict(out)["在"]; b = dict(out)["外"]
        rp = (a["rho"] >= 1.3) and (a["z"] >= 2.0) and (a["p"] <= 0.0125) and (b["rho"] > 1)
        REOPEN |= rp
        say(f"  - vol 整合 ±{tol*100:.0f}%（対照 {len(cs)} スロット）: " +
            " ／ ".join(f"{pn} ρ {d['rho']:.2f}（z {d['z']:+.2f}・W {d['JW']}/{d['NW']}・C {d['JC']}/{d['NC']}）" for pn, d in out) +
            f" → 再開 {'成立' if rp else '不成立'}")
say(f"- **B2 判定**: 許容幅 3 通り × 4 会場 で H_OPEN 再開 = {'成立あり' if REOPEN else '全て不成立'}")
say(f"\n- 実行 {time.time()-T0:.1f} s・seed {SEED}・読んだのは XAU_m5_close.npz・FOMC/CPI csv のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", OUT)
