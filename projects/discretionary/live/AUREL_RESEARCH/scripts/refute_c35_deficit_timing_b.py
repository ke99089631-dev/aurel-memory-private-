# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-11 補足 b・事後・記述] refute_c35 R1 の追跡: 外で RC（本を建玉足終値で建てる）にすると K=288 の赤字が消える（−0.030 → −0.002）。
何が消したかを同じ母数（hold≥1・okb・各版で決着）で 4 変種に分解する:
  A: 建玉価格=真（トリガー価格）・バリア=真から   （R6 FT0.1 と同じ＝原型から建玉足の残りだけ除いた版）
  B: 建玉価格=終値・バリア=終値から               （RC）
  C: 損益の基準=終値・バリア=真の建玉価格から     （バリアは壁に揃えたまま・損益だけ終値基準）
  D: 損益の基準=真・バリア=終値から               （バリアだけ ±x0 ずらす）
B−A が消えた量。C≈A ∧ B≈D → 「バリアの位置（壁に揃える）」が原因。C≈B ∧ D≈A → 「損益の基準（x0）」が原因。
併せて x0 の符号／三分位で 原型 g と RC g_rc の K=12／288 を層化（記述）。規則なし（記述）。seed 20261111・同じ乱数消費。
書き込み: data/refute_c35_deficit_timing_b.md・_b_run.log のみ。
"""
import json, os, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c35_deficit_timing_b.md")
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [反証 cycle35 補足 b] RC で消える外の赤字の分解（建玉価格 × バリア位置）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c35_deficit_timing_b.py)")

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"]).sort_values("entry_time").reset_index(drop=True)
N0 = len(tr); tr["full_idx"] = np.arange(N0)
zz = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = zz["clR"].astype(float); off = zz["off"].astype(np.int64)
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H = z["high"].astype(float); Lo = z["low"].astype(float); C = z["close"].astype(float)
NB = len(TS)
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64)); ie = np.clip(ie, 0, NB - 1)
ok = TS[ie] == tr["entry_time"].to_numpy(np.int64)
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
sgn = np.where(tr["side"].to_numpy() == "BUY", 1.0, -1.0); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float)
ft = FT / risk; hold = tr["hold"].to_numpy(int); year = tr["year"].to_numpy(int); jh = tr["jh"].to_numpy(int)
x0 = tr["x0"].to_numpy(float)
dec = tr["exit"].isin(["SL", "TP"]).to_numpy(); istp = (tr["exit"] == "TP").to_numpy()
Rstar = np.where(istp, bb + ft, -(1 - ft))
OFF = off[tr["full_idx"].to_numpy()]
band = (jh >= 7) & (jh <= 12)
days = (tr["entry_time"].to_numpy(np.int64) // 86400)
W = {"在2010-20": (year <= 2020), "外2021-26": (year >= 2021), "近年2024-26": (year >= 2024)}
cand0 = np.flatnonzero(hold >= 6); smp = rng.choice(cand0, 2000, replace=False)
KS = np.array([1, 2, 3, 6, 12, 24, 48, 96, 288]); c12 = 4; cK = len(KS) - 1
stop_real = np.empty((N, len(KS)))
for c_, K in enumerate(KS):
    idx = OFF + np.minimum(K, hold); stop_real[:, c_] = np.where(hold <= K, Rstar, clR[idx])
FLAT = (H == Lo); HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2); NF = np.flatnonzero(valid)
SPAN_S = 28 * 288
JS = np.empty((N, 16), np.int64)
for h in range(24):
    NFh = NF[HOUR[NF] == h]; ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii] + SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_] - 50, 0):hi[t_] + 50]; cand = cand[cand != ie[i]]
        JS[i] = cand[rng.integers(0, len(cand), 16)]
AR = np.arange(1, MAXH + 1)
def sim_gen(j, ent_pl, ent_bar, sg, rk, b_, ft_abs=FT, chunk=1200):
    M = len(j); res = np.full(M, -1, np.int8); kd = np.full(M, 10**6, np.int64); ST = np.full((M, len(KS)), np.nan)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg_ = sg[sl_]; rk_ = rk[sl_]; b2 = b_[sl_]; ep = ent_pl[sl_]; eb = ent_bar[sl_]
        idx = jj[:, None] + AR[None, :]; hh = H[idx]; ll = Lo[idx]
        sl = eb - sg_ * rk_; tp = eb + sg_ * b2 * rk_; buy = sg_ > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft_abs)[:, None], hh >= (sl - ft_abs)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tp + ft_abs)[:, None], ll <= (tp - ft_abs)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        r_ = np.full(len(jj), -1, np.int8); r_[kt < ks] = 1; r_[(ks <= kt) & (ks < 10**6)] = 0
        k_ = np.where(r_ == 1, kt + 1, np.where(r_ == 0, ks + 1, 10**6))
        fill = np.where(r_ == 1, tp + sg_ * ft_abs, sl + sg_ * ft_abs); rs = sg_ * (fill - ep) / rk_
        cc = C[jj[:, None] + KS[None, :]]; cl = sg_[:, None] * (cc - ep[:, None]) / rk_[:, None]
        st = np.where(k_[:, None] <= KS[None, :], rs[:, None], cl); st[r_ == -1] = np.nan
        res[sl_] = r_; kd[sl_] = k_; ST[sl_] = st
    return res, kd, ST
def boot_days(V, dd, nboot=1000):
    V = np.asarray(V, float); V = V[:, None] if V.ndim == 1 else V
    df = pd.DataFrame(V); df["d"] = dd; S = df.groupby("d").sum().to_numpy(float); cnt = pd.Series(dd).value_counts().sort_index().to_numpy(float)
    G = len(cnt); pick = rng.integers(0, G, (nboot, G)); bs = S[pick].sum(1) / cnt[pick].sum(1)[:, None]
    return V.mean(0), bs
def mt(V, dd, nboot=1000):
    mu, bs = boot_days(V, dd, nboot); se = bs.std(0, ddof=1); return mu, mu / np.where(se > 0, se, np.nan)
def fmt(mu, t): return f"{mu:+.4f} ({t:+.1f})"

KT = 16
rt, kt_, St = sim_gen(JS.ravel(), C[JS.ravel()], C[JS.ravel()], np.repeat(sgn, KT), np.repeat(risk, KT), np.repeat(bb, KT))
St = St.reshape(N, KT, len(KS)); twin_mean = np.nanmean(St, axis=1)
say(f"- 双子 sim {time.time()-t0:.1f}s")
okb = ie <= NB - MAXH - 2
entry_true = C[ie] - sgn * x0 * risk; close_e = C[ie]
J = np.where(okb, ie, 0)
VAR = {"A 真/真（R6 FT0.1）": (entry_true, entry_true), "B 終値/終値（RC）": (close_e, close_e), "C 損益=終値・バリア=真": (close_e, entry_true), "D 損益=真・バリア=終値": (entry_true, close_e)}
say("\n## 4 変種（hold≥1・okb・各版で決着・同 SET S 双子）補 ḡ_12／ḡ_288（日クラスタ t）・TP 率・TIME 率")
say("| 変種 | 在 n | 在 ḡ_12 | 在 ḡ_288 | 在 TP率 本/双子 | 外 n | 外 ḡ_12 | 外 ḡ_288 | 外 TP率 本/双子 | TIME 率 補 |")
say("|---|---|---|---|---|---|---|---|---|---|")
RESV = {}
tp_t = np.nanmean(np.where(rt.reshape(N, KT) >= 0, (rt.reshape(N, KT) == 1).astype(float), np.nan), axis=1)
for nm, (ep, eb) in VAR.items():
    r_, k_, S_ = sim_gen(J, ep, eb, sgn, risk, bb); r_[~okb] = -1
    gg = S_ - twin_mean; u = (r_ >= 0) & ~np.isnan(twin_mean[:, -1]) & okb & (hold >= 1); cells = []
    for wn in ("在2010-20", "外2021-26"):
        m = W[wn] & ~band & u; mu, t = mt(gg[m][:, [c12, cK]], days[m]); RESV[(nm, wn)] = (mu, t)
        cells += [f"{m.sum()}", fmt(mu[0], t[0]), fmt(mu[1], t[1]), f"{100*(r_[m]==1).mean():.1f}／{100*np.nanmean(tp_t[m]):.1f}"]
    say(f"| {nm} | " + " | ".join(cells) + f" | {100*(r_[~band&okb&(hold>=1)]==-1).mean():.1f}% |")
    RESV[nm] = (r_, k_, S_, u)
# A と B の exit 不一致本の寄与
rA, kA, SA, uA = RESV["A 真/真（R6 FT0.1）"]; rB, kB, SB, uB = RESV["B 終値/終値（RC）"]
say("\nA と B で exit が違う本（バリアのずれで結果が変わる本）の寄与（補・K=288・両方決着）")
for wn in ("在2010-20", "外2021-26"):
    m = W[wn] & ~band & uA & uB; diff = rA != rB
    gA = SA[:, cK] - twin_mean[:, cK]; gB = SB[:, cK] - twin_mean[:, cK]
    say(f"- {wn}: n{m.sum()}・exit 不一致 {100*diff[m].mean():.1f}%（A TP→B SL {100*((rA==1)&(rB==0))[m].mean():.1f}%・A SL→B TP {100*((rA==0)&(rB==1))[m].mean():.1f}%）；"
        f"ḡ_288 A {gA[m].mean():+.4f} vs B {gB[m].mean():+.4f}；差 B−A 全体 {(gB-gA)[m].mean():+.4f} ＝ 不一致本の寄与 {(gB-gA)[m&diff].sum()/m.sum():+.4f} ＋ 一致本の寄与 {(gB-gA)[m&~diff].sum()/m.sum():+.4f}")
# x0 層化
say("\n## x0（建玉足の残り・R）の三分位で層化: 原型 g と RC g_rc（補・K=12／288・日クラスタ t）")
rc_r, rc_k, rc_S = sim_gen(J, close_e, close_e, sgn, risk, bb); rc_r[~okb] = -1
g = stop_real - twin_mean; g_rc = rc_S - twin_mean
use = dec & ~np.isnan(twin_mean[:, -1]); use_rc = (rc_r >= 0) & ~np.isnan(twin_mean[:, -1]) & okb
say("| 窓 | x0 層 | x̄0 | n | 原型 ḡ_12 | 原型 ḡ_288 | RC ḡ_12 | RC ḡ_288 |")
say("|---|---|---|---|---|---|---|---|")
for wn in ("在2010-20", "外2021-26"):
    m0 = W[wn] & ~band & use; qs = np.quantile(x0[m0], [1/3, 2/3])
    for lab, lo_, hi_ in (("低（逆行）", -np.inf, qs[0]), ("中", qs[0], qs[1]), ("高（順行）", qs[1], np.inf)):
        sel = (x0 > lo_) & (x0 <= hi_); m = m0 & sel; m2 = W[wn] & ~band & use_rc & sel
        mu, t = mt(g[m][:, [c12, cK]], days[m]); mu2, t2 = mt(g_rc[m2][:, [c12, cK]], days[m2])
        say(f"| {wn} | {lab} | {x0[m].mean():+.3f} | {m.sum()} | {fmt(mu[0], t[0])} | {fmt(mu[1], t[1])} | {fmt(mu2[0], t2[0])} | {fmt(mu2[1], t2[1])} |")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
