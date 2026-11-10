# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-11 05:15] 対象: cycle35 (03:50) H_M1 PASS「帯外（jh∉7-12）の双子赤字 −0.03R は建玉後 12 本で全部生まれ、
  12 本生き残った本はその後 双子と区別できない」（f_12 在 1.16 [0.74,3.24]／外 1.14 [−0.18,4.35]）と周辺の知識
  W1 知識 (1)(2)「赤字は建玉後 1 時間の負ドリフト（市場）」／W2 知識 (4)「K=1 が赤字の半分＝トリガー足内の戻し（双子は負わない）」
  W3 知識 (1) 後半「12 本生き残った本は以後 双子と区別できない（マルコフ）」／W4 知識 (3)「在の帯は同じ早期赤字を持ち K 48〜288 で取り戻す」
  H_M2 null（帯−補 在 t −0.26）は争わない。

=== 事前固定（この docstring を書いてから数字を見る）===
入力: data/refute_c4_scan_paths_2010_2026.json・data/refute_c2_fullpaths.npz・data/macro/XAU_m5_ohlc.npz（bid・読取のみ）。
      scan 無し・MT5 無し・外部通信無し。c35 と同じ seed 20261111・同じ乱数消費順で SET S（KT=16）を再生成。
R0 再現: 表 1 の 補 K=12／K=288（在・外）が ±0.0005R で一致。真の建玉価格 entry = C[ie] − sgn·x0·risk から npz で再決着（FT 0.1・建玉足の残りは
      見ない＝hold≥1 の本のみ）して exit・hold が ≥97% 一致（整合の確認・不一致なら R6 は inconclusive）。
R1 (W1/W2 記帳規約・主): 本は足の途中建玉・双子は終値建玉。本を「自分の建玉足の終値で建てた双子」（RC: j=ie・同 side/risk/b・同 simulate）として
      同じ SET S 双子と比べる ḡ^RC_K。これで K=1 の「建玉足の残り x0」と「建玉価格と終値のずれによる SL/TP 位置の差」が消える。
      併せて x̄0（補・窓別）と 再基底 ḡ^rb_K = (stop_K − x0) − twin（幾何は本のまま・x0 だけ除く）を印字。
      建玉オフセット s∈{0,1,2,3,6,12} 本（ie+s の終値で建てる）の ḡ_12 プロファイル＝赤字が建玉足にどれだけ張り付いているか。
      規則: ρ = ḡ^RC_12(補)/ḡ_12(補)。在 ρ ≥ 0.5 ∧ t(ḡ^RC_12) ≤ −2 ∧ 外 ρ ≥ 0.5 ∧ t ≤ −1.5 → survived（赤字は建玉足終値以降の市場の動き）。
            在・外とも ρ < 0.25、または 在 |t| < 1 → broken（赤字の大半は記帳規約＝建玉足内の戻し）。他 inconclusive。
R2 (W3 マルコフ・主): 条件付きの直接検定。本 hold>12 ∧ 双子 未決着 (k_dec>12) に限り、残り = stop_288 − cl_12 を 本 − 双子平均 で Δrem。
      cl_12 の構成差（本と双子の 12 本目の位置）を併記し、本の cl_12 三分位で層化した Δrem も印字（記述）。
      規則: 在 |t(Δrem)| < 2 ∧ 外 |t| < 1.5 → survived。在 |t| ≥ 2 ∧ 外 同符号 |t| ≥ 1.5 → broken（12 本後も赤字が続く／取り戻す）。他 inconclusive。
R3 (双子の抽選ばらつき・主): seed 20261111 に加え 3 seed（1,2,3）で KT=16、seed 20261111 で KT=64 → ḡ_12(補)・ḡ_288(補)（在・外）。
      規則: 在 ḡ_12(補) の max−min ≤ 0.006R（名目 se 0.008 の 1 倍未満）∧ 全 seed で t ≤ −2 → survived。他 inconclusive。
R4 (部分集合・記述＋符号規則): 独立 4 窓 2010-14／2015-20／2021-23／2024-26H1・側 BUY/SELL・時刻ブロック（jh13-18／19-24／1-6）・wall_kind。
      規則: ḡ_12(補) < 0 が独立 4 窓で ≥3 ∧ 在 BUY/SELL 両方 <0 → 符号 survived。他 inconclusive。
R5 (W4 帯の「取り戻し」・記述): 帯の ḡ_K を RC 版で印字（K=1〜24 の早期赤字が RC で消えるか）。規則なし。
R6 (コスト・記述＋規則): 真の建玉価格で npz 再決着（R0 の整合が前提）・FT ∈ {0, 0.1, 0.2}（本・双子とも同じ FT）で ḡ_12・ḡ_288（補・在/外）。
      規則: FT=0.2 で 在 ḡ_12(補) が FT=0.1 の ≥50% ∧ t ≤ −2 → survived。
多重検定: 判定は R1・R2・R3 の 3 標的（Bonferroni(3) 名目 |t| 2.39 併記）。R4〜R6 は記述＋符号。look-ahead: 双子は建玉後の足だけで決着（c35 と同じ）。
survivorship: 決着本のみ（TIME 除外・双子も決着のみ）＝c35 と同じ母数。RC・オフセット版は TIME 率を併記。D2: 窓別・16 年一括は使わず。
書き込み: data/refute_c35_deficit_timing.md・data/refute_c35_deficit_timing_run.log のみ。
"""
import json, os, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c35_deficit_timing.md")
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [反証 cycle35] 帯外の双子赤字「建玉後 1 時間で全部」の反証 R0〜R6 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c35_deficit_timing.py)")

# ---------- data（c35 と同じ読み方） ----------
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
x0 = tr["x0"].to_numpy(float); side = tr["side"].to_numpy(); wk = tr["wall_kind"].to_numpy()
dec = tr["exit"].isin(["SL", "TP"]).to_numpy(); istp = (tr["exit"] == "TP").to_numpy()
Rstar = np.where(istp, bb + ft, -(1 - ft))
OFF = off[tr["full_idx"].to_numpy()]
band = (jh >= 7) & (jh <= 12)
days = (tr["entry_time"].to_numpy(np.int64) // 86400)
W = {"在2010-20": (year <= 2020), "外2021-26": (year >= 2021), "近年2024-26": (year >= 2024)}
W4 = {"2010-14": (year <= 2014), "2015-20": (year >= 2015) & (year <= 2020), "2021-23": (year >= 2021) & (year <= 2023), "2024-26H1": (year >= 2024)}
say(f"- 本 {N}（ts 一致 {ok.sum()}/{N0}）・決着 {dec.sum()}・FEED_TOL {FT}・MAX_HOLD {MAXH}・npz {NB} 本")
# x0 と clR[OFF] の一致（建玉足の残り）
say(f"- x0 vs fullpaths clR[k=0] 一致（|差|≤0.001）: {100*(np.abs(clR[OFF]-x0)<=0.001).mean():.1f}%")

# c35 と同じ乱数消費: 整合の 2000 本抽選 → 双子
cand0 = np.flatnonzero(hold >= 6); smp = rng.choice(cand0, 2000, replace=False)

KS = np.array([1, 2, 3, 6, 12, 24, 48, 96, 288]); c12 = 4; cK = len(KS) - 1
stop_real = np.empty((N, len(KS)))
for c_, K in enumerate(KS):
    idx = OFF + np.minimum(K, hold)
    stop_real[:, c_] = np.where(hold <= K, Rstar, clR[idx])

FLAT = (H == Lo); HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2); NF = np.flatnonzero(valid)
SPAN_S = 28 * 288
def draw_twins(rg, KT):
    JS = np.empty((N, KT), np.int64)
    for h in range(24):
        NFh = NF[HOUR[NF] == h]; ii = np.flatnonzero(jh == h)
        lo = np.searchsorted(NFh, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii] + SPAN_S)
        for t_, i in enumerate(ii):
            cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
            if len(cand) == 0: cand = NFh[max(lo[t_] - 50, 0):hi[t_] + 50]; cand = cand[cand != ie[i]]
            JS[i] = cand[rg.integers(0, len(cand), KT)]
    return JS

AR = np.arange(1, MAXH + 1)
def sim_stop(j, sg, rk, b_, ft_abs=FT, ent=None, chunk=1200):
    """j: anchor bar; entry = C[j] (or ent); decision from bar j+1..j+288 (c35 と同じ規則)。返り値 res(−1/0/1), k_dec, ST(M,9)"""
    M = len(j); res = np.full(M, -1, np.int8); kd = np.full(M, 10**6, np.int64); ST = np.full((M, len(KS)), np.nan)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg_ = sg[sl_]; rk_ = rk[sl_]; b2 = b_[sl_]
        idx = jj[:, None] + AR[None, :]; hh = H[idx]; ll = Lo[idx]; e_ = C[jj] if ent is None else ent[sl_]
        sl = e_ - sg_ * rk_; tp = e_ + sg_ * b2 * rk_; buy = sg_ > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft_abs)[:, None], hh >= (sl - ft_abs)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tp + ft_abs)[:, None], ll <= (tp - ft_abs)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        r_ = np.full(len(jj), -1, np.int8); r_[kt < ks] = 1; r_[(ks <= kt) & (ks < 10**6)] = 0
        k_ = np.where(r_ == 1, kt + 1, np.where(r_ == 0, ks + 1, 10**6))
        f2 = ft_abs / rk_; rs = np.where(r_ == 1, b2 + f2, -(1 - f2))
        cc = C[jj[:, None] + KS[None, :]]; cl = sg_[:, None] * (cc - e_[:, None]) / rk_[:, None]
        st = np.where(k_[:, None] <= KS[None, :], rs[:, None], cl); st[r_ == -1] = np.nan
        res[sl_] = r_; kd[sl_] = k_; ST[sl_] = st
    return res, kd, ST
def twin_sim(JS, ft_abs=FT):
    KT = JS.shape[1]
    r_, k_, S_ = sim_stop(JS.ravel(), np.repeat(sgn, KT), np.repeat(risk, KT), np.repeat(bb, KT), ft_abs)
    return r_.reshape(N, KT), k_.reshape(N, KT), S_.reshape(N, KT, len(KS))

def boot_days(V, dd, nboot=2000, rg=None):
    rg = rng if rg is None else rg
    V = np.asarray(V, float); V = V[:, None] if V.ndim == 1 else V
    df = pd.DataFrame(V); df["d"] = dd; S = df.groupby("d").sum().to_numpy(float); cnt = pd.Series(dd).value_counts().sort_index().to_numpy(float)
    G = len(cnt); pick = rg.integers(0, G, (nboot, G))
    bs = S[pick].sum(1) / cnt[pick].sum(1)[:, None]
    return V.mean(0), bs
def mt(V, dd, nboot=2000):
    mu, bs = boot_days(V, dd, nboot); se = bs.std(0, ddof=1); return mu, mu / np.where(se > 0, se, np.nan), se
def fmt(mu, t): return f"{mu:+.4f} ({t:+.1f})"

# ---------- twins (c35 と同一) ----------
JS = draw_twins(rng, 16)
RES_T, KD_T, ST_T = twin_sim(JS)
twin_mean = np.nanmean(ST_T, axis=1); g = stop_real - twin_mean
use = dec & ~np.isnan(twin_mean[:, -1])
say(f"- SET S 再生成 KT=16・双子 sim {time.time()-t0:.1f}s・双子 TIME 率 補 {100*(RES_T[~band]==-1).mean():.1f}%")

# ---------- R0 再現 ----------
say("\n## R0 再現（補 ḡ_K・在/外・K=12／288）と 真の建玉価格での npz 再決着の整合")
ref = {("在2010-20", 12): -0.0352, ("在2010-20", 288): -0.0303, ("外2021-26", 12): -0.0342, ("外2021-26", 288): -0.0300}
okrep = True
for wn in ("在2010-20", "外2021-26"):
    m = W[wn] & ~band & use; mu, t, _ = mt(g[m][:, [c12, cK]], days[m])
    okrep &= abs(mu[0] - ref[(wn, 12)]) <= 0.0005 and abs(mu[1] - ref[(wn, 288)]) <= 0.0005
    say(f"- {wn} 補 n{m.sum()}: ḡ_12 {fmt(mu[0], t[0])}（c35 {ref[(wn,12)]:+.4f}）・ḡ_288 {fmt(mu[1], t[1])}（c35 {ref[(wn,288)]:+.4f}）")
say(f"再現 {'一致' if okrep else '不一致（以下は本スクリプトの値で読む）'}")
entry_true = C[ie] - sgn * x0 * risk
okb = ie <= NB - MAXH - 2
res_tr, kd_tr, ST_tr = sim_stop(np.where(okb, ie, 0), sgn, risk, bb, FT, ent=entry_true)
res_tr[~okb] = -1
ex_json = np.where(dec, istp.astype(int), -1)
m1 = okb & (hold >= 1)
agree_exit = (res_tr[m1] == ex_json[m1]).mean(); agree_hold = ((res_tr[m1] == ex_json[m1]) & (kd_tr[m1] == np.where(dec[m1], hold[m1], 10**6))).mean()
say(f"- 真の建玉価格 entry=C[ie]−sgn·x0·risk で npz 再決着（FT 0.1・hold≥1 の {m1.sum()} 本）: exit 一致 {100*agree_exit:.2f}%・exit∧hold 一致 {100*agree_hold:.2f}%・"
    f"hold=0 の本 {(hold==0).sum()}（建玉足内決着・再決着では見ない）→ R6 {'OK' if agree_exit >= 0.97 else 'INCONCLUSIVE'}")
say(f"- x̄0（建玉足の残り・R）: " + "・".join(f"{wn} 補 {x0[wm&~band&dec].mean():+.4f}／帯 {x0[wm&band&dec].mean():+.4f}" for wn, wm in W.items())
    + f"；|x0| 中央値 補 {np.median(np.abs(x0[~band&dec])):.3f}")

# ---------- R1 記帳規約: RC（本を自分の建玉足終値で建てる）・再基底・オフセット ----------
say("\n## R1 記帳規約（主）: ḡ^RC_K（本を建玉足終値で建てた双子として同じ SET S と比較）・ḡ^rb_K（stop_K − x0）・オフセット s のプロファイル")
res_rc, kd_rc, ST_rc = sim_stop(np.where(okb, ie, 0), sgn, risk, bb, FT)
res_rc[~okb] = -1
g_rc = ST_rc - twin_mean; use_rc = (res_rc >= 0) & ~np.isnan(twin_mean[:, -1]) & okb
g_rb = (stop_real - x0[:, None]) - twin_mean
say("| 窓 | 集合 | 版 | n | " + " | ".join(f"K={K}" for K in KS) + " |")
say("|---|---|---|---|" + "---|" * len(KS))
R1 = {}
for wn, wm in W.items():
    for lab, bm in (("補", ~band), ("帯", band)):
        m = wm & bm & use; mu, t, _ = mt(g[m], days[m]); R1[(wn, lab, "orig")] = (mu, t)
        say(f"| {wn} | {lab} | 原型 c35 | {m.sum()} | " + " | ".join(fmt(mu[c], t[c]) for c in range(len(KS))) + " |")
        mu, t, _ = mt(g_rb[m], days[m]); R1[(wn, lab, "rb")] = (mu, t)
        say(f"| {wn} | {lab} | 再基底 −x0 | {m.sum()} | " + " | ".join(fmt(mu[c], t[c]) for c in range(len(KS))) + " |")
        m2 = wm & bm & use_rc; mu, t, _ = mt(g_rc[m2], days[m2]); R1[(wn, lab, "rc")] = (mu, t)
        say(f"| {wn} | {lab} | RC 終値建玉 | {m2.sum()} | " + " | ".join(fmt(mu[c], t[c]) for c in range(len(KS))) + " |")
        m3 = wm & bm & use_rc & use; mu, t, _ = mt(g_rc[m3], days[m3]); R1[(wn, lab, "rc_both")] = (mu, t)
        say(f"| {wn} | {lab} | RC（両方決着） | {m3.sum()} | " + " | ".join(fmt(mu[c], t[c]) for c in range(len(KS))) + " |")
say(f"- RC の TIME 率 補 {100*(res_rc[~band&okb]==-1).mean():.1f}%（本 {100*(~dec[~band]).mean():.1f}%）・RC と本の exit 一致（hold≥1・補）{100*(res_rc[m1&~band]==ex_json[m1&~band]).mean():.1f}%")
say("\nオフセット s（ie+s の終値で建てる・同幾何・同 SET S 双子）の ḡ_12・ḡ_288（補・日クラスタ t）")
say("| 窓 | s=0 (RC) | s=1 | s=2 | s=3 | s=6 | s=12 |")
say("|---|---|---|---|---|---|---|")
PROF = {wn: [] for wn in W}
for s_ in (0, 1, 2, 3, 6, 12):
    if s_ == 0: r_s, k_s, S_s = res_rc, kd_rc, ST_rc
    else:
        okb2 = ie + s_ <= NB - MAXH - 2
        r_s, k_s, S_s = sim_stop(np.where(okb2, ie + s_, 0), sgn, risk, bb, FT); r_s[~okb2] = -1
    g_s = S_s - twin_mean; u_s = (r_s >= 0) & ~np.isnan(twin_mean[:, -1])
    for wn, wm in W.items():
        m = wm & ~band & u_s; mu, t, _ = mt(g_s[m][:, [c12, cK]], days[m], 1000); PROF[wn].append(f"{fmt(mu[0], t[0])}／{fmt(mu[1], t[1])}")
for wn in W: say(f"| {wn} | " + " | ".join(PROF[wn]) + " |")

# ---------- R2 マルコフ（条件付き） ----------
say("\n## R2 マルコフ（主）: 本 hold>12 ∧ 双子 未決着 → 残り rem = stop_288 − cl_12 の 本 − 双子平均 Δrem（補／帯・日クラスタ t）・cl_12 の構成")
und_t = KD_T > 12
rem_t = np.where(und_t, ST_T[:, :, cK] - ST_T[:, :, c12], np.nan)
rem_t_mean = np.nanmean(rem_t, axis=1); cl12_t_mean = np.nanmean(np.where(und_t, ST_T[:, :, c12], np.nan), axis=1)
rem_r = stop_real[:, cK] - stop_real[:, c12]
drem = rem_r - rem_t_mean
use2 = dec & (hold > 12) & ~np.isnan(rem_t_mean)
say("| 窓 | 集合 | n | Δrem (t) | rem 本 | rem 双子 | cl_12 本 | cl_12 双子 | 本の cl_12 三分位別 Δrem (t) 低／中／高 |")
say("|---|---|---|---|---|---|---|---|---|")
R2 = {}
for wn, wm in W.items():
    for lab, bm in (("補", ~band), ("帯", band)):
        m = wm & bm & use2; mu, t, _ = mt(drem[m], days[m]); R2[(wn, lab)] = (mu[0], t[0])
        cl = stop_real[m, c12]; qs = np.quantile(cl, [1/3, 2/3]); cells = []
        for lo_, hi_ in ((-np.inf, qs[0]), (qs[0], qs[1]), (qs[1], np.inf)):
            mm = m & (stop_real[:, c12] > lo_) & (stop_real[:, c12] <= hi_); mu2, t2, _ = mt(drem[mm], days[mm], 800); cells.append(fmt(mu2[0], t2[0]))
        say(f"| {wn} | {lab} | {m.sum()} | **{fmt(mu[0], t[0])}** | {rem_r[m].mean():+.4f} | {rem_t_mean[m].mean():+.4f} | {cl.mean():+.4f} | {cl12_t_mean[m].mean():+.4f} | " + "／".join(cells) + " |")
# 同じ量の非条件版（c35 の f_12→288 の差）
for wn, wm in W.items():
    m = wm & ~band & use; mu, t, _ = mt(g[m][:, cK] - g[m][:, c12], days[m], 1000)
    say(f"- 参考（非条件・c35 と同じ母数）{wn} 補 ḡ_288 − ḡ_12 = {fmt(mu[0], t[0])}")

# ---------- R3 seed・KT ----------
say("\n## R3 双子の抽選ばらつき: seed 別（KT=16）と KT=64 の ḡ_12(補)・ḡ_288(補)（在／外・t）")
say("| 双子 | 在 ḡ_12 (t) | 在 ḡ_288 (t) | 外 ḡ_12 (t) | 外 ḡ_288 (t) | 在 帯 ḡ_12 (t) | 外 帯 ḡ_12 (t) |")
say("|---|---|---|---|---|---|---|")
R3 = []
def row_for(JS_, label):
    _, _, S_ = twin_sim(JS_); tm = np.nanmean(S_, axis=1); gg = stop_real - tm; u = dec & ~np.isnan(tm[:, -1]); cells = []; vals = []
    for wn in ("在2010-20", "外2021-26"):
        m = W[wn] & ~band & u; mu, t, _ = mt(gg[m][:, [c12, cK]], days[m], 1000); cells += [fmt(mu[0], t[0]), fmt(mu[1], t[1])]; vals.append((mu[0], t[0]))
    for wn in ("在2010-20", "外2021-26"):
        m = W[wn] & band & u; mu, t, _ = mt(gg[m][:, [c12]], days[m], 600); cells.append(fmt(mu[0], t[0]))
    say(f"| {label} | " + " | ".join(cells) + " |"); R3.append(vals)
row_for(JS, "seed 20261111 KT16（c35）")
for sd in (1, 2, 3):
    row_for(draw_twins(np.random.default_rng(sd), 16), f"seed {sd} KT16")
row_for(draw_twins(np.random.default_rng(20261111), 64), "seed 20261111 KT64")
say(f"- {time.time()-t0:.1f}s")

# ---------- R4 部分集合 ----------
say("\n## R4 部分集合（補・ḡ_12 と ḡ_288・日クラスタ t）: 独立 4 窓・側・時刻ブロック・wall_kind")
say("| 分割 | 在 ḡ_12 (t) | 在 ḡ_288 (t) | 外 ḡ_12 (t) | 外 ḡ_288 (t) |")
say("|---|---|---|---|---|")
R4 = {}
def sub_row(label, mk, wins=None):
    cells = []
    for wn in (("在2010-20", "外2021-26") if wins is None else wins):
        m = W[wn] & ~band & use & mk if wins is None else mk & ~band & use
        mu, t, _ = mt(g[m][:, [c12, cK]], days[m], 1000); cells += [fmt(mu[0], t[0]) + f" n{m.sum()}", fmt(mu[1], t[1])]; R4[(label, wn)] = (mu[0], t[0])
    say(f"| {label} | " + " | ".join(cells) + " |")
for wn4, wm4 in W4.items():
    m = wm4 & ~band & use; mu, t, _ = mt(g[m][:, [c12, cK]], days[m], 1000); R4[("win", wn4)] = (mu[0], t[0])
    say(f"| 独立窓 {wn4} | {fmt(mu[0], t[0])} n{m.sum()} | {fmt(mu[1], t[1])} | — | — |")
for sd_ in ("BUY", "SELL"): sub_row(f"側 {sd_}", side == sd_)
for bn, (a, b_) in {"jh13-18": (13, 18), "jh19-24": (19, 24), "jh1-6": (1, 6)}.items():
    sub_row(bn, ((jh >= a) & (jh <= b_)) | ((b_ == 24) & (jh == 0)))
for wk_ in np.unique(wk): sub_row(f"wall {wk_}", wk == wk_)
sub_row("hold≥1", hold >= 1)

# ---------- R5 帯の RC（記述） ----------
say("\n## R5 帯 jh7-12 の早期赤字と「取り戻し」（記述）: 上表 R1 の 帯 行を参照 — 在 帯 原型 K=1〜24 vs RC")
for wn in W:
    mo, to = R1[(wn, "帯", "orig")]; mr, tr_ = R1[(wn, "帯", "rc")]
    say(f"- {wn} 帯: 原型 K=1 {fmt(mo[0], to[0])}・K=12 {fmt(mo[c12], to[c12])}・K=288 {fmt(mo[cK], to[cK])}／RC K=1 {fmt(mr[0], tr_[0])}・K=12 {fmt(mr[c12], tr_[c12])}・K=288 {fmt(mr[cK], tr_[cK])}")

# ---------- R6 コスト（FT 0／0.1／0.2・真の建玉価格で再決着・双子も同 FT） ----------
say("\n## R6 コスト感度: 真の建玉価格で npz 再決着・FT ∈ {0, 0.1, 0.2}（本・双子とも）・補 ḡ_12／ḡ_288（在／外）")
say("| FT | 在 ḡ_12 (t) n | 在 ḡ_288 (t) | 外 ḡ_12 (t) n | 外 ḡ_288 (t) | 本 TIME 率 補 |")
say("|---|---|---|---|---|---|")
R6 = {}
for ftv in (0.0, 0.1, 0.2):
    r_r, k_r, S_r = sim_stop(np.where(okb, ie, 0), sgn, risk, bb, ftv, ent=entry_true); r_r[~okb] = -1
    _, _, S_t = twin_sim(JS, ftv); tm = np.nanmean(S_t, axis=1)
    gg = S_r - tm; u = (r_r >= 0) & ~np.isnan(tm[:, -1]) & okb & (hold >= 1); cells = []
    for wn in ("在2010-20", "外2021-26"):
        m = W[wn] & ~band & u; mu, t, _ = mt(gg[m][:, [c12, cK]], days[m], 1000); cells += [fmt(mu[0], t[0]) + f" n{m.sum()}", fmt(mu[1], t[1])]; R6[(ftv, wn)] = (mu[0], t[0])
    say(f"| {ftv:.1f} | " + " | ".join(cells) + f" | {100*(r_r[~band&okb&(hold>=1)]==-1).mean():.1f}% |")

# ---------- 判定 ----------
say("\n## 判定（docstring の規則・Bonferroni(3) 名目 |t| 2.39 併記）")
gi, ti = R1[("在2010-20", "補", "orig")]; gri, tri = R1[("在2010-20", "補", "rc")]
go, to_ = R1[("外2021-26", "補", "orig")]; gro, tro = R1[("外2021-26", "補", "rc")]
rho_i = gri[c12] / gi[c12] if gi[c12] != 0 else np.nan; rho_o = gro[c12] / go[c12] if go[c12] != 0 else np.nan
if (rho_i < 0.25 and rho_o < 0.25) or abs(tri[c12]) < 1: v1 = "broken（赤字の大半は記帳規約＝建玉足内の戻し・双子は負わない）"
elif rho_i >= 0.5 and tri[c12] <= -2 and rho_o >= 0.5 and tro[c12] <= -1.5: v1 = "survived（建玉足終値以降の市場の動き）"
else: v1 = "inconclusive"
say(f"- **R1 W1/W2 記帳規約: {v1}** — ρ = ḡ^RC_12/ḡ_12 在 {rho_i:.2f}（RC {fmt(gri[c12], tri[c12])} vs 原型 {fmt(gi[c12], ti[c12])}）／外 {rho_o:.2f}（RC {fmt(gro[c12], tro[c12])} vs {fmt(go[c12], to_[c12])}）；"
    f"K=1: 原型 在 {gi[0]:+.4f}・再基底 {R1[('在2010-20','補','rb')][0][0]:+.4f}・RC {gri[0]:+.4f}；x̄0 補 在 {x0[W['在2010-20']&~band&dec].mean():+.4f}")
mi, tti = R2[("在2010-20", "補")]; mo_, tto = R2[("外2021-26", "補")]
if abs(tti) < 2 and abs(tto) < 1.5: v2 = "survived（12 本後は双子と区別できない）"
elif abs(tti) >= 2 and abs(tto) >= 1.5 and np.sign(mi) == np.sign(mo_): v2 = "broken（12 本後も" + ("赤字が続く" if mi < 0 else "取り戻す") + "）"
else: v2 = "inconclusive"
say(f"- **R2 W3 マルコフ: {v2}** — Δrem 在 {fmt(mi, tti)}／外 {fmt(mo_, tto)}")
g12s = [v[0][0] for v in R3]; t12s = [v[0][1] for v in R3]
spread_ = max(g12s) - min(g12s)
v3 = "survived" if (spread_ <= 0.006 and all(t <= -2 for t in t12s)) else "inconclusive"
say(f"- **R3 抽選ばらつき: {v3}** — 在 ḡ_12(補) 5 本の範囲 {min(g12s):+.4f}〜{max(g12s):+.4f}（幅 {spread_:.4f}）・t {min(t12s):+.1f}〜{max(t12s):+.1f}")
nwin = sum(R4[("win", w)][0] < 0 for w in W4); bs_ok = R4[("側 BUY", "在2010-20")][0] < 0 and R4[("側 SELL", "在2010-20")][0] < 0
v4 = "符号 survived" if (nwin >= 3 and bs_ok) else "inconclusive"
say(f"- **R4 部分集合: {v4}** — 独立 4 窓で ḡ_12(補)<0 は {nwin}/4・在 BUY {R4[('側 BUY','在2010-20')][0]:+.4f}／SELL {R4[('側 SELL','在2010-20')][0]:+.4f}")
if agree_exit >= 0.97:
    r6 = R6[(0.2, "在2010-20")][0] / R6[(0.1, "在2010-20")][0] if R6[(0.1, "在2010-20")][0] != 0 else np.nan
    v6 = "survived" if (r6 >= 0.5 and R6[(0.2, "在2010-20")][1] <= -2) else "inconclusive"
    say(f"- **R6 コスト: {v6}** — 在 ḡ_12(補) FT0.1 {R6[(0.1,'在2010-20')][0]:+.4f} → FT0.2 {R6[(0.2,'在2010-20')][0]:+.4f}（比 {r6:.2f}・t {R6[(0.2,'在2010-20')][1]:+.1f}）・FT0 {R6[(0.0,'在2010-20')][0]:+.4f}")
else:
    say(f"- **R6 コスト: inconclusive（再決着の整合 {100*agree_exit:.1f}% <97%）**")
say(f"\n実行 {time.time()-t0:.1f} s・scan 無し・MT5 無し・外部通信無し・seed 20261111")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
