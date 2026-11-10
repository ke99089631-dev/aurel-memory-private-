# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-11 補足 c・事後・記述→規則 1 つ] 側の非対称（R4: 在 BUY ḡ_12 −0.069 t −6.3 vs SELL −0.003）と x0 の側差（hold≥1 BUY −0.050／SELL +0.009）の正体。
setup_engine.py L201-203（読取のみ）: 買いは h[k] + TRIG_SPREAD(0.22) > trig で発動し entry = trig（bid 価格）に記帳。売りは l[k] < trig（bid 発動）。
→ 買いの entry は建玉足の bid 高値より上（最大 0.22 USD）に記帳され得る＝「bid が届いていない価格で買った」＝実射で払う ask−bid を紙に写した規約。
   双子（c27/c33/c35）は bid 終値で建てスプレッドを払わない。双子との比較「本 − 双子」には、BUY 側だけこの規約差 ph_i = max(entry − H[ie], 0) が乗る。
検査:
  1. ph_i（USD・R）の分布: BUY で ph>0 の割合・平均・中央値、SELL の max(L[ie] − entry, 0)（≈0 のはず）。
  2. 側別 x̄0（hold≥1）と ph を足し戻した x̄0 + ph/risk（BUY）。
  3. 双子に同じ ph を払わせる（SET S・ent = C[j] + sgn·ph_i・同 seed）: 補 ḡ_K（K=1,12,288・在/外・側別）。
  4. RC（本を終値建玉）の側別 ḡ_12／ḡ_288（補）。
規則（1 つ・事後だが先に書く）: 在 ḡ_12(補) が ph 込み双子で原型の 50% 未満 ∧ 外 同 → 「帯外の赤字＝建玉後 1 時間の負ドリフト（市場）」は broken
      （大半は BUY のスプレッド規約）。在・外とも ≥75% 残り t ≤ −2／−1.5 → survived。他 inconclusive。seed 20261111・同じ乱数消費。
書き込み: data/refute_c35_deficit_timing_c.md・_c_run.log のみ。
"""
import json, os, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c35_deficit_timing_c.md")
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [反証 cycle35 補足 c] 側の非対称の正体＝BUY の TRIG_SPREAD 記帳規約（双子は払わない）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c35_deficit_timing_c.py)")

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"]); TRS = float(d["frozen"]["TRIG_SPREAD"])
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
x0 = tr["x0"].to_numpy(float); side = tr["side"].to_numpy()
dec = tr["exit"].isin(["SL", "TP"]).to_numpy(); istp = (tr["exit"] == "TP").to_numpy()
Rstar = np.where(istp, bb + ft, -(1 - ft))
OFF = off[tr["full_idx"].to_numpy()]
band = (jh >= 7) & (jh <= 12)
days = (tr["entry_time"].to_numpy(np.int64) // 86400)
W = {"在2010-20": (year <= 2020), "外2021-26": (year >= 2021), "近年2024-26": (year >= 2024)}
cand0 = np.flatnonzero(hold >= 6); smp = rng.choice(cand0, 2000, replace=False)
KS = np.array([1, 2, 3, 6, 12, 24, 48, 96, 288]); c12 = 4; cK = len(KS) - 1; c1 = 0
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
def sim_stop(j, sg, rk, b_, ft_abs=FT, ent=None, chunk=1200):
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
def boot_days(V, dd, nboot=1000):
    V = np.asarray(V, float); V = V[:, None] if V.ndim == 1 else V
    df = pd.DataFrame(V); df["d"] = dd; S = df.groupby("d").sum().to_numpy(float); cnt = pd.Series(dd).value_counts().sort_index().to_numpy(float)
    G = len(cnt); pick = rng.integers(0, G, (nboot, G)); bs = S[pick].sum(1) / cnt[pick].sum(1)[:, None]
    return V.mean(0), bs
def mt(V, dd, nboot=1000):
    mu, bs = boot_days(V, dd, nboot); se = bs.std(0, ddof=1); return mu, mu / np.where(se > 0, se, np.nan)
def fmt(mu, t): return f"{mu:+.4f} ({t:+.1f})"

# 1. phantom spread
entry_true = C[ie] - sgn * x0 * risk
ph = np.where(sgn > 0, np.maximum(entry_true - H[ie], 0.0), 0.0)            # BUY: bid 高値より上に記帳された分
ph_sell = np.where(sgn < 0, np.maximum(Lo[ie] - entry_true, 0.0), 0.0)      # SELL: bid 安値より下（≈0 のはず）
phR = ph / risk
say(f"- TRIG_SPREAD {TRS}・BUY {int((sgn>0).sum())} 本: ph = max(entry − bid高値, 0) >0 の割合 {100*(ph[sgn>0]>0).mean():.1f}%・平均 {ph[sgn>0].mean():.3f} USD（>0 の本のみ {ph[sgn>0][ph[sgn>0]>0].mean():.3f}・中央値 {np.median(ph[sgn>0][ph[sgn>0]>0]):.3f}・最大 {ph.max():.3f}）・R 換算 平均 {phR[sgn>0].mean():+.4f}R")
say(f"- SELL {int((sgn<0).sum())} 本: max(bid安値 − entry, 0) >0 の割合 {100*(ph_sell[sgn<0]>0).mean():.1f}%・平均 {ph_sell[sgn<0].mean():.4f} USD（売りは bid 発動＝規約差なし）")
say("- 側別 x̄0（hold≥1・補）と ph を足し戻した x̄0+ph/risk: " + "・".join(
    f"{wn} BUY {x0[wm&~band&dec&(hold>=1)&(sgn>0)].mean():+.4f} → {(x0+phR)[wm&~band&dec&(hold>=1)&(sgn>0)].mean():+.4f}／SELL {x0[wm&~band&dec&(hold>=1)&(sgn<0)].mean():+.4f}" for wn, wm in W.items()))
say(f"- 年別 ph 平均（BUY・USD）: " + "・".join(f"{y}:{ph[(year==y)&(sgn>0)].mean():.3f}" for y in range(2010, 2027)))

# 3. twins paying the same phantom
KT = 16
def twin(ent_shift):
    j = JS.ravel(); e = C[j] + np.repeat(sgn * ent_shift, KT)
    r_, k_, S_ = sim_stop(j, np.repeat(sgn, KT), np.repeat(risk, KT), np.repeat(bb, KT), FT, ent=e)
    return r_.reshape(N, KT), k_.reshape(N, KT), S_.reshape(N, KT, len(KS))
RES0, KD0, ST0 = twin(np.zeros(N)); tm0 = np.nanmean(ST0, axis=1); g0 = stop_real - tm0; u0 = dec & ~np.isnan(tm0[:, -1])
RESP, KDP, STP = twin(ph); tmp = np.nanmean(STP, axis=1); gp = stop_real - tmp; up = dec & ~np.isnan(tmp[:, -1])
RESF, KDF, STF = twin(np.where(sgn > 0, TRS, 0.0)); tmf = np.nanmean(STF, axis=1); gf = stop_real - tmf; uf = dec & ~np.isnan(tmf[:, -1])
say(f"- 双子 sim ×3 {time.time()-t0:.1f}s")
say("\n## 3. 補 ḡ_K（本 − 双子）: 双子の建玉を (a) bid 終値（c35）／(b) 終値 + 本と同じ ph_i（BUY のみ）／(c) 終値 + 0.22 固定（BUY 全本・実射の ask 相当）")
say("| 窓 | 側 | n | 双子 | K=1 | K=12 | K=288 |")
say("|---|---|---|---|---|---|---|")
RR = {}
for wn, wm in W.items():
    for lab, sm in (("全", np.ones(N, bool)), ("BUY", sgn > 0), ("SELL", sgn < 0)):
        for nm, gg, uu in (("(a) bid 終値", g0, u0), ("(b) +ph_i", gp, up), ("(c) +0.22", gf, uf)):
            m = wm & ~band & uu & sm; mu, t = mt(gg[m][:, [c1, c12, cK]], days[m]); RR[(wn, lab, nm)] = (mu, t)
            say(f"| {wn} | {lab} | {m.sum()} | {nm} | {fmt(mu[0], t[0])} | {fmt(mu[1], t[1])} | {fmt(mu[2], t[2])} |")
# 4. RC by side
okb = ie <= NB - MAXH - 2
rc_r, rc_k, rc_S = sim_stop(np.where(okb, ie, 0), sgn, risk, bb, FT); rc_r[~okb] = -1
g_rc = rc_S - tm0; use_rc = (rc_r >= 0) & ~np.isnan(tm0[:, -1]) & okb
say("\n## 4. RC（本を自分の建玉足 bid 終値で建てる＝規約を双子に揃える）側別 補 ḡ_12／ḡ_288")
for wn, wm in W.items():
    cells = []
    for lab, sm in (("BUY", sgn > 0), ("SELL", sgn < 0)):
        m = wm & ~band & use_rc & sm; mu, t = mt(g_rc[m][:, [c12, cK]], days[m]); cells.append(f"{lab} n{m.sum()} K12 {fmt(mu[0], t[0])}・K288 {fmt(mu[1], t[1])}")
    say(f"- {wn}: " + "／".join(cells))
# 帯も（記述）
say("\n帯 jh7-12（記述）: (a)/(b) の ḡ_12／ḡ_288")
for wn, wm in W.items():
    cells = []
    for nm, gg, uu in (("(a)", g0, u0), ("(b) +ph", gp, up)):
        m = wm & band & uu; mu, t = mt(gg[m][:, [c12, cK]], days[m]); cells.append(f"{nm} K12 {fmt(mu[0], t[0])}・K288 {fmt(mu[1], t[1])}")
    say(f"- {wn} 帯: " + "／".join(cells))

# 判定
say("\n## 判定（docstring の規則）")
a_i = RR[("在2010-20", "全", "(a) bid 終値")]; b_i = RR[("在2010-20", "全", "(b) +ph_i")]; a_o = RR[("外2021-26", "全", "(a) bid 終値")]; b_o = RR[("外2021-26", "全", "(b) +ph_i")]
r_i = b_i[0][1] / a_i[0][1] if a_i[0][1] != 0 else np.nan; r_o = b_o[0][1] / a_o[0][1] if a_o[0][1] != 0 else np.nan
if r_i < 0.5 and r_o < 0.5: v = "broken（大半は BUY のスプレッド規約）"
elif r_i >= 0.75 and r_o >= 0.75 and b_i[1][1] <= -2 and b_o[1][1] <= -1.5: v = "survived"
else: v = "inconclusive"
say(f"- **補足 c 規則: {v}** — ḡ_12(補) 在 (a) {fmt(a_i[0][1], a_i[1][1])} → (b) {fmt(b_i[0][1], b_i[1][1])}（残り {r_i:.2f}）／外 (a) {fmt(a_o[0][1], a_o[1][1])} → (b) {fmt(b_o[0][1], b_o[1][1])}（残り {r_o:.2f}）；"
    f"K=288 在 {a_i[0][2]:+.4f} → {b_i[0][2]:+.4f}／外 {a_o[0][2]:+.4f} → {b_o[0][2]:+.4f}")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
