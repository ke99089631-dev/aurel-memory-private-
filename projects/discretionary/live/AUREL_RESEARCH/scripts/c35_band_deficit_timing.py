# -*- coding: utf-8 -*-
"""
[研究レーン cycle35 2026-11-11] 【深化・path／機構】帯外（jh∉7-12）の「双子に対する赤字」は建玉後 1 時間に生まれるか
問い（backlog「深化の次の候補（機構・cycle33 (c)）」）: cycle33 で本番帯 jh7-12 は同時刻・同側・同幾何の双子と区別できず、
      補集合 jh∉7-12 だけが一貫して双子より悪かった（x̄_emp 在 −1.74 pp／外 −1.54・Δμ_R −0.031R）。cycle32 では建玉後 1 時間の
      方向ドリフトが 本 −0.02〜−0.04R vs 同 side プラセボ +0.01〜+0.02R（5 分 lag-1 負 × 大きいトリガー足）だった。
      仮説 M: 帯外の赤字は「建玉後 1 時間の負ドリフト」で、帯外（欧米時間・トリガー足 1.37 USD・ATR 大）に集中している。
      帯（アジア時間・静かな足 ATR 0.96）はこの負ドリフトが小さいので双子と同じ。入口フィルタの提案ではない（機構の記述）。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/refute_c4_scan_paths_2010_2026.json（19404 本）・data/refute_c2_fullpaths.npz（clR・off・entry_time 昇順）・
      data/macro/XAU_m5_ohlc.npz（bid・完全格子）。既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し。
      整合: fullpaths clR k=6 vs npz close を 2000 本で突合（≤0.02 USD ≥95% でなければ全判定 inconclusive）。
(1) 出口側の分解（主）: 「停止 path 値」stop_K = R*（K 本以内に決着）／cl_K（未決着・終値 R）。R* = +(b+ft)／−(1−ft)（c33 と同じ規則）。
    双子 = cycle33 SET S（同 JST 時・±28 暦日・非 flat・d=0 除外・K=16・終値建玉・同側同幾何・同 simulate 規則）。
    g_K,i = stop_K(本 i) − mean_k stop_K(双子 ik)。K ∈ {1,2,3,6,12,24,48,96,288}。K=288 は c33 の Δμ_R そのもの（再現で確認）。
    母数 = 決着本（TIME 除外）・双子も決着のみ（c33 と同じ）。窓 在 2010-20／外 2021-26H1／近年 2024-26H1（建玉年・D2）。
    統計 = 建玉 UTC 日クラスタ bootstrap 2000（帯と補は独立）。割合 f_K = ḡ_K(補)/ḡ_288(補)（bootstrap 同時 draw の比の 2.5/97.5%）。
(2) 機構側（副）: cycle32 の方向ドリフト D = SGN·Σ_{j=1..12} r_j / risk（建玉足終値から 1 時間・停止なし）を
    プラセボ SET D（refute_c32 ②: 同 ET 5 分スロット・±28 暦日・月〜金・非 flat・同セッション ±12 本・post flat ≤3・
    トリガー足レンジ [0.8,1.25] ∧ 建玉前 1 時間 RMS [0.8,1.25] の両方一致（<K なら [0.67,1.5]）・マスクは d≠0 のみ・K=4・同 side）
    と比べ ΔD = D(本) − mean D(プラセボ) を帯／補で印字。ΔL_pre（一致の確認）を先に印字。
判定（事前固定）:
  H_M1（赤字の時期・主・補集合）: 在 ḡ_12(補) < 0 ∧ t ≤ −2 ∧ f_12 ≥ 0.5 ∧ 外 ḡ_12(補) < 0 ∧ t ≤ −1.5 ∧ f_12 ≥ 0.5
      → PASS「帯外の赤字の半分以上は建玉後 1 時間以内に生まれる」。在/外とも f_12 ≤ 0.25 → 「1 時間以降に生まれる」。他 partial/null。
      副: 帯 ḡ_12 と 帯−補 の gap_K の割合 f^gap_K = gap_K/gap_288 を併記（分母 t 1.5〜1.9 で荒い・判定不使用）。
  H_M2（機構側・SET D）: 在 ΔD(補) < 0 ∧ t ≤ −2 ∧ [ΔD(帯) − ΔD(補)] > 0 ∧ t ≥ 1.5 ∧ 外 ΔD(補) < 0 ∧ t ≤ −1.5 → PASS
      「負ドリフトは帯外に集中」。他 null。大きさの一致 = |ΔD(補)| / |ḡ_12(補)| ∈ [0.5, 2] なら「合う」。
  予測（仮説 M が正しければ）: f_12 ≥ 0.5・ΔD(補) ≈ −0.02〜−0.04R・ΔD(帯) ≈ 0。
  対立仮説（事前に書く）: (a) 補の決着が速い（hold 中央値 8 本）ので「1 時間以内」は機械的に高くなる → 停止なしの ΔD（副）と
      決着割合 P(hold≤12) を帯／補／双子で併記し、f_12 が決着割合を超えるかを読む。(b) 赤字は 1 時間より後（壁の配置・
      反対側の壁の近さ）→ f_12 小・gap が後で開く。(c) 帯の双子だけが時刻帯の背景で TP に届きやすい（c33 の q̄_emp 差）→ 補の
      自身の赤字 ḡ(補) を主にし帯−補は副。
負の対照: 双子 k=0 を擬似実本・k=1..15 を基準にした ḡ_K（帯・補・3 窓）→ 0 ∧ |t|<2 で較正。
陽性対照: 在 補の実本の未決着 stop_12 に −0.03R を注入 → t（H_M1 の検出力）；在 補の D に −0.02R を注入 → t（H_M2）。
最重大反証（事前）: (i) 本は足の途中建玉・双子は終値建玉 → K=1 の差は建玉足の残りを含む（K=1 は記述）。(ii) stop_K の cl_K は
      終値で SL/TP は高安 → 未決着の cl_K は決着値より分散が小さい（K 小で t が高く出やすい・割合は影響なし）。(iii) bid のみ。
      (iv) TIME 除外（双子の TIME 率は帯 ≈1%・補 4〜7%）。(v) 判定 2 セル・他は記述。(vi) 2026-06 まで。seed 20261111。
コスト: npz 3 s＋双子 sim 19404×16（≈15 s）＋SET D 選択（≈10 s）。書き込み data/c35_band_deficit_timing_result.md・c35_run.log のみ。
"""
import json, os, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c35_band_deficit_timing_result.md")
rng = np.random.default_rng(20261111)
NY = "America/New_York"
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle35 研究レーン] 帯外の双子赤字は建玉後 1 時間に生まれるか（停止 path 値の K 分解＋SET D ドリフト） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c35_band_deficit_timing.py)")

# ---------- data ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"]).sort_values("entry_time").reset_index(drop=True)
N0 = len(tr); tr["full_idx"] = np.arange(N0)
zz = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = zz["clR"].astype(float); off = zz["off"].astype(np.int64)
assert len(off) in (N0, N0 + 1), (len(off), N0)   # off は末尾に番兵（終端 offset）を持つ
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H = z["high"].astype(float); Lo = z["low"].astype(float); C = z["close"].astype(float)
NB = len(TS); n_hole = int((np.diff(TS) != 300).sum())   # 格子の穴 19（DATA_MAP §1・ts 一致で引く）
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64)); ie = np.clip(ie, 0, NB - 1)
ok = TS[ie] == tr["entry_time"].to_numpy(np.int64)
say(f"- 本 {N0}・ts 一致 {ok.sum()}（不一致 {(~ok).sum()} 除外）・FEED_TOL {FT}・MAX_HOLD {MAXH}・npz {NB} 本 {pd.Timestamp(TS[0],unit='s')}..{pd.Timestamp(TS[-1],unit='s')}・格子の穴 {n_hole}")
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
sgn = np.where(tr["side"].to_numpy() == "BUY", 1.0, -1.0); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float)
ft = FT / risk; hold = tr["hold"].to_numpy(int); year = tr["year"].to_numpy(int); jh = tr["jh"].to_numpy(int)
dec = tr["exit"].isin(["SL", "TP"]).to_numpy(); istp = (tr["exit"] == "TP").to_numpy()
Rstar = np.where(istp, bb + ft, -(1 - ft))
OFF = off[tr["full_idx"].to_numpy()]
band = (jh >= 7) & (jh <= 12)
days = (tr["entry_time"].to_numpy(np.int64) // 86400)
W = {"在2010-20": (year <= 2020), "外2021-26": (year >= 2021), "近年2024-26": (year >= 2024)}

# 整合 fullpaths vs npz
cand = np.flatnonzero(hold >= 6); smp = rng.choice(cand, 2000, replace=False)
dif = np.abs((clR[OFF[smp] + 6] - clR[OFF[smp]]) - sgn[smp] * (C[ie[smp] + 6] - C[ie[smp]]) / risk[smp]) * risk[smp]
agree = (dif <= 0.02).mean()
say(f"- 整合（fullpaths clR k=6 vs npz close・2000 本）: ≤0.02 USD {agree*100:.1f}% → {'OK' if agree >= 0.95 else 'INCONCLUSIVE'}")
say(f"- 母数（決着本）: " + "・".join(f"{wn} 帯 {int((wm&band&dec).sum())}／補 {int((wm&~band&dec).sum())}" for wn, wm in W.items()))
say("- hold（決着本）中央値・P(hold≤12): " + "・".join(
    f"{wn} 帯 {np.median(hold[wm&band&dec]):.0f} 本 {100*(hold[wm&band&dec]<=12).mean():.0f}%／補 {np.median(hold[wm&~band&dec]):.0f} 本 {100*(hold[wm&~band&dec]<=12).mean():.0f}%" for wn, wm in W.items()))

# ---------- (1) real stopped path ----------
KS = np.array([1, 2, 3, 6, 12, 24, 48, 96, 288])
stop_real = np.empty((N, len(KS)))
for c_, K in enumerate(KS):
    idx = OFF + np.minimum(K, hold)
    stop_real[:, c_] = np.where(hold <= K, Rstar, clR[idx])
assert np.allclose(stop_real[dec, -1], Rstar[dec])

# ---------- twins SET S (cycle33) + stopped path sim ----------
FLAT = (H == Lo); HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2); NF = np.flatnonzero(valid)
KT = 16; SPAN_S = 28 * 288
JS = np.empty((N, KT), np.int64); nS = np.empty(N, np.int64)
for h in range(24):
    NFh = NF[HOUR[NF] == h]; ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii] + SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_] - 50, 0):hi[t_] + 50]; cand = cand[cand != ie[i]]
        nS[i] = len(cand); JS[i] = cand[rng.integers(0, len(cand), KT)]
say(f"- SET S 双子: 候補中央値 {np.median(nS):.0f}・jh 一致 {100*(HOUR[JS]==jh[:,None]).mean():.1f}%・選択 {time.time()-t0:.1f}s")

AR = np.arange(1, MAXH + 1)
def sim_stop(j, sg, rk, b_, chunk=1200):
    M = len(j); res = np.full(M, -1, np.int8); kd = np.full(M, 10**6, np.int64); ST = np.full((M, len(KS)), np.nan)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg_ = sg[sl_]; rk_ = rk[sl_]; b2 = b_[sl_]
        idx = jj[:, None] + AR[None, :]; hh = H[idx]; ll = Lo[idx]; ent = C[jj]
        sl = ent - sg_ * rk_; tp = ent + sg_ * b2 * rk_; buy = sg_ > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + FT)[:, None], hh >= (sl - FT)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tp + FT)[:, None], ll <= (tp - FT)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        r_ = np.full(len(jj), -1, np.int8); r_[kt < ks] = 1; r_[(ks <= kt) & (ks < 10**6)] = 0
        k_ = np.where(r_ == 1, kt + 1, np.where(r_ == 0, ks + 1, 10**6))
        ft_ = FT / rk_; rs = np.where(r_ == 1, b2 + ft_, -(1 - ft_))
        cc = C[jj[:, None] + KS[None, :]]; cl = sg_[:, None] * (cc - ent[:, None]) / rk_[:, None]
        st = np.where(k_[:, None] <= KS[None, :], rs[:, None], cl); st[r_ == -1] = np.nan
        res[sl_] = r_; kd[sl_] = k_; ST[sl_] = st
    return res, kd, ST
def rep(a): return np.repeat(a, KT)
t1 = time.time()
RES_T, KD_T, ST_T = sim_stop(JS.ravel(), rep(sgn), rep(risk), rep(bb))
RES_T = RES_T.reshape(N, KT); KD_T = KD_T.reshape(N, KT); ST_T = ST_T.reshape(N, KT, len(KS))
say(f"- 双子 sim {N}×{KT}: {time.time()-t1:.1f}s・双子 TIME 率 帯 {100*(RES_T[band]==-1).mean():.1f}%／補 {100*(RES_T[~band]==-1).mean():.1f}%・双子 P(k_dec≤12) 帯 {100*(KD_T[band]<=12).mean():.0f}%／補 {100*(KD_T[~band]<=12).mean():.0f}%")
twin_mean = np.nanmean(ST_T, axis=1)            # (N, K)  決着双子の平均
g = stop_real - twin_mean                        # (N, K)
use = dec & ~np.isnan(twin_mean[:, -1])

def boot_days(V, dd, nboot=2000):
    """V: (n, m) → mean vector, bootstrap draws (nboot, m) by day cluster"""
    df = pd.DataFrame(V); df["d"] = dd; S = df.groupby("d").sum().to_numpy(float); cnt = pd.Series(dd).value_counts().sort_index().to_numpy(float)
    G = len(cnt); pick = rng.integers(0, G, (nboot, G))
    bs = S[pick].sum(1) / cnt[pick].sum(1)[:, None]
    return V.mean(0), bs

say("\n## 1. 停止 path 値の分解 ḡ_K = mean[stop_K(本) − mean stop_K(双子 S)]（R・日クラスタ t）— 補集合（主）・帯・帯−補")
say("| 窓 | 集合 | n | " + " | ".join(f"K={K}" for K in KS) + " |")
say("|---|---|---|" + "---|" * len(KS))
GB = {}
for wn, wm in W.items():
    for lab, bm in (("補 jh∉7-12", ~band), ("帯 jh7-12", band)):
        m = wm & bm & use; mu, bs = boot_days(g[m], days[m]); se = bs.std(0, ddof=1)
        GB[(wn, lab)] = (mu, bs)
        say(f"| {wn} | {lab} | {m.sum()} | " + " | ".join(f"{mu[c]:+.4f} ({mu[c]/se[c]:+.1f})" for c in range(len(KS))) + " |")
    mu_o, bs_o = GB[(wn, "補 jh∉7-12")]; mu_b, bs_b = GB[(wn, "帯 jh7-12")]
    gap = mu_b - mu_o; gse = (bs_b - bs_o).std(0, ddof=1)
    say(f"| {wn} | 帯−補 gap | — | " + " | ".join(f"{gap[c]:+.4f} ({gap[c]/gse[c]:+.1f})" for c in range(len(KS))) + " |")
say()
say("割合 f_K = ḡ_K(補)/ḡ_288(補)（bootstrap 比の 95% 区間）と f^gap_K = gap_K/gap_288（副）")
say("| 窓 | 量 | " + " | ".join(f"K={K}" for K in KS[:-1]) + " |")
say("|---|---|" + "---|" * (len(KS) - 1))
F12 = {}
for wn in W:
    mu_o, bs_o = GB[(wn, "補 jh∉7-12")]; mu_b, bs_b = GB[(wn, "帯 jh7-12")]
    fr = mu_o / mu_o[-1]; frb = bs_o / bs_o[:, -1:]
    say(f"| {wn} | f_K 補 | " + " | ".join(f"{fr[c]:.2f} [{np.percentile(frb[:,c],2.5):.2f},{np.percentile(frb[:,c],97.5):.2f}]" for c in range(len(KS) - 1)) + " |")
    gap = mu_b - mu_o; gb = bs_b - bs_o; fg = gap / gap[-1]; fgb = gb / gb[:, -1:]
    say(f"| {wn} | f^gap_K | " + " | ".join(f"{fg[c]:.2f} [{np.percentile(fgb[:,c],2.5):.2f},{np.percentile(fgb[:,c],97.5):.2f}]" for c in range(len(KS) - 1)) + " |")
    c12 = int(np.flatnonzero(KS == 12)[0])
    F12[wn] = dict(g12=mu_o[c12], t12=mu_o[c12] / bs_o[:, c12].std(ddof=1), f12=fr[c12], f12lo=np.percentile(frb[:, c12], 2.5), g288=mu_o[-1], t288=mu_o[-1] / bs_o[:, -1].std(ddof=1))
say()
# 記述: 決着済み本の寄与と未決着本の寄与（K=12）
say("K=12 の内訳（補・在/外）: ḡ_12 を「12 本以内に決着した本」と「未決着（cl_12）」に分ける（本側の決着状態で分割・双子平均はそのまま）")
for wn, wm in W.items():
    m = wm & ~band & use; e = hold <= 12
    a = g[m & e, c12]; b_ = g[m & ~e, c12]
    say(f"- {wn} 補: 決着≤12 n{(m&e).sum()} 平均 g {a.mean():+.4f}・寄与 {a.sum()/m.sum():+.4f}R／未決着 n{(m&~e).sum()} 平均 {b_.mean():+.4f}・寄与 {b_.sum()/m.sum():+.4f}R；本 P(hold≤12) {100*e[m].mean():.0f}% vs 双子 {100*(KD_T[m]<=12).mean():.0f}%")

# ---------- 負の対照 ----------
say("\n## 2. 負の対照（双子 k=0 を擬似実本・k=1..15 基準）ḡ_K: K=12／288（帯・補・3 窓）")
tm0 = np.nanmean(ST_T[:, 1:, :], axis=1); g0 = ST_T[:, 0, :] - tm0; use0 = (RES_T[:, 0] >= 0) & ~np.isnan(tm0[:, -1])
for wn, wm in W.items():
    cells = []
    for lab, bm in (("補", ~band), ("帯", band)):
        m = wm & bm & use0; mu, bs = boot_days(g0[m][:, [c12, len(KS) - 1]], days[m], 1000); se = bs.std(0, ddof=1)
        cells.append(f"{lab} K12 {mu[0]:+.4f} (t {mu[0]/se[0]:+.1f})・K288 {mu[1]:+.4f} (t {mu[1]/se[1]:+.1f})")
    say(f"- {wn}: " + "／".join(cells))

# ---------- 陽性対照 H_M1 ----------
m = W["在2010-20"] & ~band & use; inj = g[m].copy(); und = hold[m] > 12; inj[und, c12] -= 0.03
mu, bs = boot_days(inj[:, [c12]], days[m], 1000)
say(f"- 陽性対照 H_M1: 在 補の未決着本（{und.sum()}/{m.sum()}）の stop_12 に −0.03R 注入 → ḡ_12 {mu[0]:+.4f} (t {mu[0]/bs.std(ddof=1):+.2f})（元 {F12['在2010-20']['g12']:+.4f} t {F12['在2010-20']['t12']:+.2f}）")

# ---------- (2) SET D drift ----------
say("\n## 3. 機構側: 建玉後 1 時間の方向ドリフト D = SGN·Σ_{1..12} r/risk（停止なし）vs SET D プラセボ（同 ET スロット・トリガー足レンジ ∧ 建玉前 1h RMS の両方一致・d≠0 のみ）")
r = np.zeros(NB); r[1:] = np.diff(C); rng_bar = H - Lo
dt_ny = pd.to_datetime(TS, unit="s", utc=True).tz_convert(NY)
SLOT = (dt_ny.hour.to_numpy() * 12 + dt_ny.minute.to_numpy() // 5).astype(np.int32); WD = dt_ny.weekday.to_numpy().astype(np.int8)
sess = dt_ny + pd.Timedelta(hours=6); SESS = sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy()
PRE = np.arange(-12, 0); POST = np.arange(1, 13)
def vpre(I): return np.sqrt((r[I[:, None] + PRE[None, :]] ** 2).mean(1))
def dsum(I): return r[I[:, None] + POST[None, :]].sum(1)
okb = (ie - 12 >= 0) & (ie + 12 < NB); I2 = np.where(okb, ie, 100)
VALD = okb & (SESS[I2 - 12] == SESS[I2]) & (SESS[I2 + 12] == SESS[I2]) & (FLAT[I2[:, None] + POST[None, :]].sum(1) <= 3) & (WD[I2] <= 4)
KD = 4; DD = np.array([x for x in range(-28, 29) if x != 0])
PD_ = np.full((N, KD), -1, np.int64); nD = np.zeros(N, np.int64); widen = 0
Vp_real = np.where(VALD, vpre(I2), np.nan)
for s in range(0, N, 4000):
    sl_ = slice(s, min(N, s + 4000)); I = I2[sl_]; v = VALD[sl_]
    Cd = np.clip(I[:, None] + 288 * DD[None, :], 13, NB - 14)
    okc = (SLOT[Cd] == SLOT[I][:, None]) & (WD[Cd] <= 4) & (~FLAT[Cd]) & (SESS[Cd - 12] == SESS[Cd]) & (SESS[Cd + 12] == SESS[Cd])
    okc &= FLAT[Cd[:, :, None] + POST[None, None, :]].sum(2) <= 3
    ratio = rng_bar[Cd] / np.maximum(rng_bar[I][:, None], 1e-9)
    vp_c = np.sqrt((r[Cd[:, :, None] + PRE[None, None, :]] ** 2).mean(2)); vr = vp_c / np.maximum(Vp_real[sl_][:, None], 1e-9)
    ok1 = okc & (ratio >= 0.8) & (ratio <= 1.25) & (vr >= 0.8) & (vr <= 1.25)
    ok2 = okc & (ratio >= 0.67) & (ratio <= 1.5) & (vr >= 0.67) & (vr <= 1.5)
    e1 = ok1.sum(1) >= KD; okc = np.where(e1[:, None], ok1, ok2); widen += int((~e1 & (ok2.sum(1) >= KD) & v).sum())
    for q in range(len(I)):
        if not v[q]: continue
        c = Cd[q][okc[q]]; nD[s + q] = len(c)
        if len(c) >= KD: PD_[s + q] = rng.choice(c, KD, replace=False)
okD = VALD & (PD_ >= 0).all(1)
say(f"- 母数 VALD {VALD.sum()}／SET D 確保 {okD.sum()}（候補中央値 {np.median(nD[VALD]):.0f}・拡大 {widen}）・{time.time()-t0:.1f}s")
D_real = sgn * dsum(I2) / risk
D_pl = np.mean([sgn * dsum(np.where(okD, PD_[:, k], 100)) / risk for k in range(KD)], 0)
Vp_pl = np.mean([np.log(np.maximum(vpre(np.where(okD, PD_[:, k], 100)), 1e-6)) for k in range(KD)], 0)
Vo_real = np.sqrt((r[I2[:, None] + POST[None, :]] ** 2).mean(1)); Vo_pl = np.mean([np.log(np.maximum(np.sqrt((r[np.where(okD, PD_[:, k], 100)[:, None] + POST[None, :]] ** 2).mean(1)), 1e-6)) for k in range(KD)], 0)
dL_pre = np.log(np.maximum(Vp_real, 1e-6)) - Vp_pl; dL_post = np.log(np.maximum(Vo_real, 1e-6)) - Vo_pl
dD = D_real - D_pl
say("| 窓 | 集合 | n | ΔL_pre (t) | ΔL_post (t) | D 本 R | D プラセボ R | **ΔD R (t) [MDE]** | ΔD BUY (t) | ΔD SELL (t) |")
say("|---|---|---|---|---|---|---|---|---|---|")
DB = {}
for wn, wm in W.items():
    for lab, bm in (("補 jh∉7-12", ~band), ("帯 jh7-12", band)):
        m = wm & bm & okD
        mu, bs = boot_days(np.c_[dL_pre[m], dL_post[m], dD[m]], days[m], 1000); se = bs.std(0, ddof=1)
        mb = m & (sgn > 0); ms = m & (sgn < 0)
        mub, bsb = boot_days(dD[mb][:, None], days[mb], 500); mus, bss = boot_days(dD[ms][:, None], days[ms], 500)
        DB[(wn, lab)] = (mu[2], bs[:, 2])
        say(f"| {wn} | {lab} | {m.sum()} | {mu[0]:+.4f} ({mu[0]/se[0]:+.1f}) | {mu[1]:+.4f} ({mu[1]/se[1]:+.1f}) | {D_real[m].mean():+.4f} | {D_pl[m].mean():+.4f} | **{mu[2]:+.4f} ({mu[2]/se[2]:+.2f}) [{2*se[2]:.4f}]** | {mub[0]:+.4f} ({mub[0]/bsb.std(ddof=1):+.1f}) | {mus[0]:+.4f} ({mus[0]/bss.std(ddof=1):+.1f}) |")
    a, ba = DB[(wn, "帯 jh7-12")]; o, bo = DB[(wn, "補 jh∉7-12")]; dse = (ba - bo).std(ddof=1)
    say(f"| {wn} | 帯−補 | — | | | | | **{a-o:+.4f} ({(a-o)/dse:+.2f})** | | |")
m = W["在2010-20"] & ~band & okD; mu, bs = boot_days((dD[m] - 0.02)[:, None], days[m], 1000)
say(f"- 陽性対照 H_M2: 在 補の D に −0.02R 注入 → ΔD {mu[0]:+.4f} (t {mu[0]/bs.std(ddof=1):+.2f})")
# 記述: トリガー足レンジ・ATR の帯差
say(f"- 記述: 本のトリガー足レンジ 中央値 帯 {np.median(rng_bar[ie[band]]):.2f}／補 {np.median(rng_bar[ie[~band]]):.2f} USD・建玉前 1h RMS 帯 {np.nanmedian(Vp_real[band]):.3f}／補 {np.nanmedian(Vp_real[~band]):.3f}・risk 中央値 帯 {np.median(risk[band]):.2f}／補 {np.median(risk[~band]):.2f}")

# ---------- 判定 ----------
say("\n## 判定（事前固定）")
i_, o_ = F12["在2010-20"], F12["外2021-26"]
pass1 = (i_["g12"] < 0 and i_["t12"] <= -2 and i_["f12"] >= 0.5 and o_["g12"] < 0 and o_["t12"] <= -1.5 and o_["f12"] >= 0.5)
late1 = (i_["f12"] <= 0.25 and o_["f12"] <= 0.25)
v1 = "PASS（帯外の赤字の半分以上は建玉後 1 時間以内）" if pass1 else ("1 時間以降に生まれる（f_12 ≤0.25）" if late1 else "partial/null")
say(f"- **H_M1: {v1}** — 在 ḡ_12(補) {i_['g12']:+.4f} (t {i_['t12']:+.2f})・f_12 {i_['f12']:.2f} [下限 {i_['f12lo']:.2f}]・ḡ_288 {i_['g288']:+.4f} (t {i_['t288']:+.2f})／外 ḡ_12 {o_['g12']:+.4f} (t {o_['t12']:+.2f})・f_12 {o_['f12']:.2f} [下限 {o_['f12lo']:.2f}]・ḡ_288 {o_['g288']:+.4f} (t {o_['t288']:+.2f})")
ai, bai = DB[("在2010-20", "帯 jh7-12")]; oi, boi = DB[("在2010-20", "補 jh∉7-12")]; ao, bao = DB[("外2021-26", "帯 jh7-12")]; oo, boo = DB[("外2021-26", "補 jh∉7-12")]
t_oi = oi / boi.std(ddof=1); t_gi = (ai - oi) / (bai - boi).std(ddof=1); t_oo = oo / boo.std(ddof=1)
pass2 = (oi < 0 and t_oi <= -2 and (ai - oi) > 0 and t_gi >= 1.5 and oo < 0 and t_oo <= -1.5)
ratio_i = abs(oi) / max(abs(i_["g12"]), 1e-9); ratio_o = abs(oo) / max(abs(o_["g12"]), 1e-9)
say(f"- **H_M2: {'PASS（負ドリフトは帯外に集中）' if pass2 else 'null'}** — 在 ΔD(補) {oi:+.4f} (t {t_oi:+.2f})・帯−補 {ai-oi:+.4f} (t {t_gi:+.2f})／外 ΔD(補) {oo:+.4f} (t {t_oo:+.2f})・帯−補 {ao-oo:+.4f}")
say(f"- 大きさの一致 |ΔD(補)|/|ḡ_12(補)|: 在 {ratio_i:.2f}／外 {ratio_o:.2f} → {'合う' if (0.5 <= ratio_i <= 2 and 0.5 <= ratio_o <= 2) else '合わない'}")
say(f"\n実行 {time.time()-t0:.1f} s・scan 無し・MT5 無し・外部通信無し・seed 20261111")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
