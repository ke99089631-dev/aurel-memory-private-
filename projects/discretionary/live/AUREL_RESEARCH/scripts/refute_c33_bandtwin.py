# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-10 23:15] 対象: cycle33 (21:55) 本番帯 jh7-12 の双子検定（主 H_T null は争わない）の残存弱信号
  W1 知識 (2)「帯外（jh∉7-12）の本は同時刻の双子より一貫して TP に到達しにくい（在 −1.74 pp t −3.28／外 −1.54 t −2.49・
      3 基準・hold≥1 で同符号）＝ refute_c27 の『scan は RW より 1.5 pp 到達しにくい』は帯外に局在する」
  W2 DiD 残差「帯 − 補 の x̄_emp 差 +2.24／+2.75／+3.37 pp（t 1.87／1.93／1.78）・3 窓同符号」＝知識 (3)「帯外の本が双子より悪いことから来る」
  W3 知識 (3)「時刻帯の背景 q̄_emp(帯)−q̄_emp(補) +3.1／+2.6／+1.2 pp ＝ アジア時間は双子でも TP に到達しやすい（夜間ドリフト c16/c22 の顔）」
  W4 事後「帯 SELL 外 +5.05 pp（t 2.63・n730）／近年 +6.39（t 2.57）」（研究レーン自身が「時代効果の疑い・判定に使わない」と明記）
  W5 前向きセル「近年窓を 2024-01〜 で延長し 帯 決着 ≥1800 本（MDE ≈2.3 pp）で x̄_emp(帯・SET SC) >0 ∧ t≥2」の検出力

=== 事前固定（この docstring を書いてから数字を見る） ===
入力: data/refute_c4_scan_paths_2010_2026.json（19404 本）・data/macro/XAU_m5_ohlc.npz（bid・読取のみ）。scan 無し・MT5 無し・外部通信無し。
R0 再現: cycle33 と同じ seed・同じ乱数消費順で SET S／SC を再生成し、主表（帯／補 × 3 窓の x̄_emp S）が ±0.05 pp で一致することを確認。
R1 (W1 帯外の負):
  (a) 較正: 16 本の双子を順に擬似実本（k=0..15・他 15 本を基準）にした負の対照 x̄ の sd（σ_nc）を名目の日クラスタ se と比べる。
      本内置換（各本で 実本＋双子 16 のうち 1 つを無作為に「実本」に選び x̄ を再計算・2000 回）で 在／外／近年 の帯外 x̄_emp の両側 p を出す。
      規則: 在の置換 p ≥ 0.05 → W1 broken（雑音）。σ_nc/se > 1.5 → 「t は名目の 1/(σ_nc/se) 倍で読む」と記す。
  (b) 別分割・部分集合（記述）: 2010-14／2015-20／2021-23／2024-26H1 の 4 窓・年別・帯外を時刻ブロック（jh 13-15／16-18／19-21／22-24／1-3／4-6）で分解。
      年別の帯外 x̄_emp と、その年の 5 分 lag-1 自己相関（非 flat・セッション内）の Spearman 相関を印字（cycle19/refute 11-07: lag-1 負は 2023 で消滅）。
  (c) 機構の置換（主）: 双子を「同 jh・±28 日・非 flat」に加えて **トリガー足（建玉足）のレンジ H−L を ±20%（log）で一致**させた SET T と、
      **SET T ∧ 直前 ATR14 ±30%（log）** の SET TC で x̄_emp を再計算（候補 <K なら許容を 2 倍・無ければ SET S に fallback）。
      双子が同じ大きさの足の終値で建つなら、「大きな足の直後の戻し（c32 知識 (3)・5 分 lag-1 負）」は双子にも乗る。
      規則: 在・外とも x̄_T(補) が x̄_S(補) の 50% 未満に縮む → W1 の帰属「壁→壁の帯外の本は悪い」は broken（＝トリガー足の大きさの効果・壁固有でない）。
            在・外とも 75% 以上残り ∧ 在 t≤−2 ∧ 外 t≤−1.5 → survived。他 inconclusive。
R2 (W2 DiD 残差): S／T／TC の各基準で DiD = x̄(帯)−x̄(補) を再計算し、本内置換で p（3 窓）。
      入れ子（近年 ⊂ 外）を明記: 独立窓は 在・外の 2 つ → 「3 窓同符号」の帰無確率は 1/2。
      規則: 在・外とも DiD_TC < 0.5·DiD_S、または 在・外とも置換 p>0.10 → broken。TC で 在 p<0.05 ∧ 外 p<0.10 → survived。他 inconclusive。
R3 (W3 背景＝夜間ドリフト): q̄_emp(帯)−q̄_emp(補) を 閉形式幾何 Δq_cf = q̄_cf(帯)−q̄_cf(補)（q_cf=(1−ft)/(1+b)）と残差に分解。
      双子自身の超過 x_pl = 1{TP_pl} − q_cf を帯／補で印字（「アジア時間のランダム建玉は RW より到達しやすいか」の直接値）。
      規則: 在・外とも |Δq_cf| ≥ 0.5·Δq_emp → 「背景＝時刻帯」の読みは broken（幾何の違い）。≤0.25 → survived。他 inconclusive。
R4 (W4 帯 SELL): 事後 12 セル（BUY／SELL／mid／outer × 3 窓）の本内置換 max|z| 分布で SELL 外 z の family-wise p。規則: p_fw>0.05 → broken。
R5 (W5 検出力): SC の近年 se から n=1800 の se・MDE を外挿、観測点推定（SC 近年 +1.21／外 +0.11／在 −0.09）での検出力、
      2025 年ペース（帯 決着 418/年）で必要年数。規則なし（設計の帰結を記す）。
多重検定: 判定は R1(c)・R2・R3 の 3 標的（Bonferroni(3) 名目 |t| 2.39 併記）。look-ahead: 双子は建玉後の足だけで決着。
survivorship: TIME 率を双子基準ごとに併記。D2: 窓別。seed 20261110。
書き込み: data/refute_c33_bandtwin.md・data/refute_c33_bandtwin_run.log のみ。
"""
import json, os, time, math, sys
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c33_bandtwin.md")
rng = np.random.default_rng(20261110)
L = []
def say(s=""): print(s, flush=True); L.append(s)

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["day"] = tr["ts"].dt.floor("D")
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["sgn"] = np.where(tr["side"] == "BUY", 1.0, -1.0)
tr["band"] = tr["jh"].between(7, 12)
tr["qcf"] = (1 - tr["ft"]) / (1 + tr["b"])
N = len(tr)

z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H, Lo, C = z["high"], z["low"], z["close"]
NB = len(TS)
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
ok = (ie < NB) & (TS[np.minimum(ie, NB - 1)] == tr["entry_time"].to_numpy(np.int64))
say(f"# [反証 cycle33] 本番帯 双子検定の残存弱信号 W1〜W5 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c33_bandtwin.py)")
say(f"本 {N}・決着 {int(tr.dec.sum())}・FEED_TOL {FT}・MAX_HOLD {MAXH}；M5 OHLC {NB} 本；entry_time の足一致 {int(ok.sum())}/{N}")
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
W = {"在2010-20": (tr.year <= 2020).to_numpy(), "外2021-26": (tr.year >= 2021).to_numpy(), "近年2024-26": (tr.year >= 2024).to_numpy()}
W4 = {"2010-14": tr.year.between(2010, 2014).to_numpy(), "2015-20": tr.year.between(2015, 2020).to_numpy(),
      "2021-23": tr.year.between(2021, 2023).to_numpy(), "2024-26H1": (tr.year >= 2024).to_numpy()}
band = tr["band"].to_numpy()

# ---------- シミュレータ（cycle33 / refute_c27 と同一） ----------
AR = np.arange(1, MAXH + 1)
def simulate(j, sgn, risk, b, ft=FT, chunk=1200):
    M = len(j); out = np.full(M, -1, np.int8)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg = sgn[sl_]; rk = risk[sl_]; bb = b[sl_]
        idx = jj[:, None] + AR[None, :]
        hh = H[idx]; ll = Lo[idx]
        ent = C[jj]
        sl = ent - sg * rk; tp = ent + sg * bb * rk
        buy = sg > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft)[:, None], hh >= (sl - ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tp + ft)[:, None], ll <= (tp - ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        res = np.full(len(jj), -1, np.int8)
        res[(kt < ks)] = 1; res[(ks <= kt) & (ks < 10**6)] = 0
        out[sl_] = res
    return out

K = 16; SPAN_S = 28 * 288; SPAN_A = 5760
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); jh = tr["jh"].to_numpy(int)
FLAT = (H == Lo); ATR = pd.Series(H - Lo).rolling(14).mean().shift(1).to_numpy()
RNG_BAR = H - Lo
HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2)
NF = np.flatnonzero(valid)

# ---- cycle33 と同じ乱数消費順で SET S／SC を再生成（R0） ----
JS = np.empty((N, K), np.int64); nS = np.empty(N, np.int64)
JSC = np.empty((N, K), np.int64)
a_e = ATR[ie]
CANDS = [None] * N
for h in range(24):
    NFh = NF[HOUR[NF] == h]
    ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii] + SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_]-50,0):hi[t_]+50]; cand = cand[cand != ie[i]]
        CANDS[i] = cand
        nS[i] = len(cand); JS[i] = cand[rng.integers(0, len(cand), K)]
        la = np.log(np.where(ATR[cand] > 0, ATR[cand], np.nan) / a_e[i]) if a_e[i] > 0 else np.full(len(cand), np.nan)
        m = np.abs(la) < 0.2
        if m.sum() < K: m = np.abs(la) < 0.4
        if m.sum() < 1: m = np.ones(len(cand), bool)
        cc = cand[m]; JSC[i] = cc[rng.integers(0, len(cc), K)]
pa_lo = np.searchsorted(NF, np.maximum(ie - SPAN_A, 0)); pa_hi = np.maximum(np.searchsorted(NF, ie + SPAN_A), pa_lo + 1)
_JA = NF[np.minimum((pa_lo[:, None] + rng.random((N, K)) * (pa_hi - pa_lo)[:, None]).astype(np.int64), len(NF) - 1)]  # 乱数消費のみ

# ---- 新基準 SET T（トリガー足レンジ一致）・SET TC（＋ATR14 一致） ----
JT = np.empty((N, K), np.int64); JTC = np.empty((N, K), np.int64); nT = np.empty(N, np.int64); nTC = np.empty(N, np.int64)
wT = wTC = fT = fTC = 0
r_e = RNG_BAR[ie]
for i in range(N):
    cand = CANDS[i]
    lr = np.log(np.where(RNG_BAR[cand] > 0, RNG_BAR[cand], np.nan) / r_e[i]) if r_e[i] > 0 else np.full(len(cand), np.nan)
    m = np.abs(lr) < 0.2
    if m.sum() < K: m = np.abs(lr) < 0.4; wT += 1
    if m.sum() < 1: m = np.ones(len(cand), bool); fT += 1
    cc = cand[m]; nT[i] = len(cc); JT[i] = cc[rng.integers(0, len(cc), K)]
    la = np.log(np.where(ATR[cand] > 0, ATR[cand], np.nan) / a_e[i]) if a_e[i] > 0 else np.full(len(cand), np.nan)
    m2 = m & (np.abs(la) < 0.3)
    if m2.sum() < K: m2 = m & (np.abs(la) < 0.6); wTC += 1
    if m2.sum() < 1: m2 = m; fTC += 1
    cc = cand[m2]; nTC[i] = len(cc); JTC[i] = cc[rng.integers(0, len(cc), K)]
say(f"SET S 候補 中央値 {np.median(nS):.0f}；SET T（トリガー足レンジ ±20%）候補 中央値 {np.median(nT):.0f}（拡大 {wT}・fallback {fT}）；"
    f"SET TC（＋ATR14 ±30%）候補 中央値 {np.median(nTC):.0f}（拡大 {wTC}・fallback {fTC}）")
say(f"トリガー足レンジ 中央値 実本 帯 {np.median(r_e[band]):.2f}／補 {np.median(r_e[~band]):.2f} USD；双子建玉足レンジ S 帯 {np.median(RNG_BAR[JS[band]]):.2f}／補 {np.median(RNG_BAR[JS[~band]]):.2f}・"
    f"T 帯 {np.median(RNG_BAR[JT[band]]):.2f}／補 {np.median(RNG_BAR[JT[~band]]):.2f}；ATR14 実本 帯 {np.nanmedian(a_e[band]):.2f}／補 {np.nanmedian(a_e[~band]):.2f}・双子 TC 帯 {np.nanmedian(ATR[JTC[band]]):.2f}／補 {np.nanmedian(ATR[JTC[~band]]):.2f}")
say(f"実本トリガー足レンジ／直前 ATR14 の比 中央値: 帯 {np.nanmedian(r_e[band]/a_e[band]):.2f}・補 {np.nanmedian(r_e[~band]/a_e[~band]):.2f}（双子 S の同比 帯 {np.nanmedian(RNG_BAR[JS[band]]/ATR[JS[band]]):.2f}・補 {np.nanmedian(RNG_BAR[JS[~band]]/ATR[JS[~band]]):.2f}）")

def rep(a): return np.repeat(a, K)
t1 = time.time()
R = {}
for nm, J in (("S", JS), ("SC", JSC), ("T", JT), ("TC", JTC)):
    R[nm] = simulate(J.ravel(), rep(sgn), rep(risk), rep(bb)).reshape(N, K)
say(f"プラセボ生成 S／SC／T／TC 各 {N}×{K}（{time.time()-t1:.0f} s）")
say()

def qemp(Rm):
    ntp = (Rm == 1).sum(1); nsl = (Rm == 0).sum(1); dec_ = ntp + nsl
    return np.where(dec_ > 0, ntp / np.maximum(dec_, 1), np.nan), (Rm == -1).mean(1)
def clus(vals, days, nboot=2000):
    s = pd.DataFrame({"v": vals, "d": days}).groupby("d")["v"].agg(["sum", "size"])
    S = s["sum"].to_numpy(float); Nn = s["size"].to_numpy(float); G = len(S)
    m = S.sum() / Nn.sum(); pick = rng.integers(0, G, (nboot, G)); bs = S[pick].sum(1) / Nn[pick].sum(1)
    se = bs.std(ddof=1); return m, se, (m / se if se > 0 else np.nan)
def clus_diff(v1, d1, v2, d2, nboot=2000):
    def boot(vals, days):
        s = pd.DataFrame({"v": vals, "d": days}).groupby("d")["v"].agg(["sum", "size"])
        S = s["sum"].to_numpy(float); Nn = s["size"].to_numpy(float); G = len(S)
        pick = rng.integers(0, G, (nboot, G)); return S.sum() / Nn.sum(), S[pick].sum(1) / Nn[pick].sum(1)
    m1, b1 = boot(v1, d1); m2, b2 = boot(v2, d2); se = (b1 - b2).std(ddof=1)
    return m1 - m2, se, (m1 - m2) / se if se > 0 else np.nan

dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy(); days = tr["day"].to_numpy(); qcf = tr["qcf"].to_numpy()
hold1 = (tr["hold"] >= 1).to_numpy()
QE = {}; TM = {}
for nm in R: QE[nm], TM[nm] = qemp(R[nm])

# ---------- R0 再現 ----------
say("## R0 再現（cycle33 主表・SET S・帯／補 × 3 窓）")
ref = {("在2010-20", True): 0.50, ("在2010-20", False): -1.74, ("外2021-26", True): 1.21, ("外2021-26", False): -1.54, ("近年2024-26", True): 2.88, ("近年2024-26", False): -0.49}
okrep = True
for wn, wm in W.items():
    for bflag, lab in ((True, "帯"), (False, "補")):
        m = wm & (band == bflag) & dec & ~np.isnan(QE["S"])
        x = 100 * (tp[m] - QE["S"][m]).mean()
        okrep &= abs(x - ref[(wn, bflag)]) <= 0.05
        say(f"- {wn} {lab}: x̄_emp S {x:+.2f} pp（cycle33 {ref[(wn,bflag)]:+.2f}）")
say(f"再現 {'一致' if okrep else '不一致（乱数順が違う・以下は本スクリプトの値で読む）'}")
say()

# ---------- R1(a) 較正: 16 本 負の対照 sd と 本内置換 ----------
say("## R1(a) 較正: 負の対照（k を順に擬似実本・他 15 本基準）16 本の sd σ_nc vs 名目 日クラスタ se；本内置換 2000 回の両側 p（帯外・帯・DiD）")
RS = R["S"]
# 本内置換: 各本 17 個（実本＋双子 16）
O = np.concatenate([np.where(dec, tp, -1.0)[:, None], RS.astype(float)], axis=1)  # (N,17)
ntp_all = (O == 1).sum(1); ndec_all = (O >= 0).sum(1)
NPERM = 2000
def perm_stats(mask_sets):
    """mask_sets: dict name -> bool mask (N,). returns dict name -> array (NPERM,) of x̄ under 本内置換"""
    out = {k: np.empty(NPERM) for k in mask_sets}
    ar = np.arange(N)
    for r_ in range(NPERM):
        u = rng.integers(0, K + 1, N); ch = O[ar, u]
        base_n = ndec_all - (ch >= 0); base_tp = ntp_all - np.where(ch == 1, 1, 0)
        okm = (ch >= 0) & (base_n > 0)
        xv = ch - base_tp / np.maximum(base_n, 1)
        for k, mk in mask_sets.items():
            mm = mk & okm; out[k][r_] = xv[mm].mean() if mm.any() else np.nan
    return out
masks = {}
for wn, wm in W.items():
    masks[(wn, "帯")] = wm & band; masks[(wn, "補")] = wm & ~band
    for sd_ in ("BUY", "SELL"): masks[(wn, sd_)] = wm & band & (tr.side.to_numpy() == sd_)
    for wk in ("mid", "outer"): masks[(wn, wk)] = wm & band & (tr.wall_kind.to_numpy() == wk)
PS = perm_stats(masks)
say("| 窓 | 集合 | x̄_emp S pp | 名目 se pp (t) | σ_nc pp（16 本）| σ_nc/se | 置換 sd pp | 置換 両側 p |")
say("|---|---|---|---|---|---|---|---|")
NC = {}
for wn, wm in W.items():
    for lab, bm in (("帯", band), ("補", ~band)):
        m = wm & bm & dec & ~np.isnan(QE["S"])
        x, se, t = clus(tp[m] - QE["S"][m], days[m])
        ncs = []
        for k in range(K):
            others = np.delete(RS, k, axis=1); q0, _ = qemp(others)
            mk = wm & bm & (RS[:, k] >= 0) & ~np.isnan(q0)
            ncs.append(((RS[:, k][mk] == 1).astype(float) - q0[mk]).mean())
        ncs = np.array(ncs); snc = ncs.std(ddof=1); NC[(wn, lab)] = (ncs.mean(), snc)
        ps = PS[(wn, lab)]; psd = np.nanstd(ps); p = np.nanmean(np.abs(ps) >= abs(x))
        say(f"| {wn} | {lab} | {100*x:+.2f} | {100*se:.2f} ({t:+.2f}) | {100*snc:.2f}（平均 {100*ncs.mean():+.2f}） | {snc/se:.2f} | {100*psd:.2f} | {p:.3f} |")
say("DiD（帯−補）の本内置換 p:")
for wn in W:
    mb = W[wn] & band & dec & ~np.isnan(QE["S"]); mo = W[wn] & ~band & dec & ~np.isnan(QE["S"])
    dx = (tp[mb] - QE["S"][mb]).mean() - (tp[mo] - QE["S"][mo]).mean()
    pd_ = PS[(wn, "帯")] - PS[(wn, "補")]; p = np.nanmean(np.abs(pd_) >= abs(dx))
    say(f"- {wn}: DiD {100*dx:+.2f} pp・置換 sd {100*np.nanstd(pd_):.2f}・両側 p {p:.3f}")
say()

# ---------- R1(b) 別分割・時刻ブロック・年別 vs lag-1 ----------
say("## R1(b) 帯外の負の別分割（SET S・x̄_emp pp (t)）")
say("| 窓 | 帯 | 補 | DiD |")
say("|---|---|---|---|")
for wn, wm in W4.items():
    cells = []
    for bm in (band, ~band):
        m = wm & bm & dec & ~np.isnan(QE["S"]); x, se, t = clus(tp[m] - QE["S"][m], days[m]); cells.append(f"{100*x:+.2f} ({t:+.2f}) n{m.sum()}")
    mb = wm & band & dec & ~np.isnan(QE["S"]); mo = wm & ~band & dec & ~np.isnan(QE["S"])
    dx, _, tx = clus_diff(tp[mb] - QE["S"][mb], days[mb], tp[mo] - QE["S"][mo], days[mo])
    say(f"| {wn} | {cells[0]} | {cells[1]} | {100*dx:+.2f} ({tx:+.2f}) |")
say()
say("帯外を JST 時刻ブロックで分解（x̄_emp S pp (t) n）:")
BLK = {"jh13-15": (13, 15), "jh16-18": (16, 18), "jh19-21": (19, 21), "jh22-24": (22, 24), "jh1-3": (1, 3), "jh4-6": (4, 6)}
say("| 窓 | " + " | ".join(BLK) + " |"); say("|---|" + "---|" * len(BLK))
for wn, wm in W.items():
    cells = []
    for bn, (a, b_) in BLK.items():
        hm = ((jh >= a) & (jh <= b_)) | ((b_ == 24) & (jh == 0))
        m = wm & hm & dec & ~np.isnan(QE["S"]); x, se, t = clus(tp[m] - QE["S"][m], days[m], nboot=800); cells.append(f"{100*x:+.2f} ({t:+.2f}) {m.sum()}")
    say(f"| {wn} | " + " | ".join(cells) + " |")
say()
# 年別 lag-1 自己相関（非 flat 連続足・セッション内）
ret = np.diff(np.log(C)); good = ~FLAT[1:] & ~FLAT[:-1]
yr_bar = pd.to_datetime(TS[1:], unit="s").year
rows = []; xs_y = []; ac_y = []
for y in range(2010, 2027):
    my = good & (yr_bar == y) & np.r_[True, good[:-1]]
    r1 = ret[my]; r0 = np.r_[np.nan, ret[:-1]][my]; mm = ~np.isnan(r0)
    ac = np.corrcoef(r1[mm], r0[mm])[0, 1]
    m = (tr.year.to_numpy() == y) & ~band & dec & ~np.isnan(QE["S"]); xo = (tp[m] - QE["S"][m]).mean()
    mT = (tr.year.to_numpy() == y) & ~band & dec & ~np.isnan(QE["T"]); xoT = (tp[mT] - QE["T"][mT]).mean()
    rows.append(f"{y}: lag1 {ac:+.4f}・補 x̄_S {100*xo:+.1f}・補 x̄_T {100*xoT:+.1f}"); xs_y.append(xo); ac_y.append(ac)
say("年別: 5 分 lag-1 自己相関 vs 帯外 x̄_emp（S／T）: " + "; ".join(rows))
from scipy.stats import spearmanr, pearsonr
rs, ps_ = spearmanr(ac_y, xs_y); rp, pp_ = pearsonr(ac_y, xs_y)
say(f"年別 Spearman(lag1, 補 x̄_S) {rs:+.3f} (p {ps_:.3f})・Pearson {rp:+.3f} (p {pp_:.3f})・n17")
say()

# ---------- R1(c) / R2 主: SET T・TC ----------
say("## R1(c)・R2 主: 双子の基準を S → T（トリガー足レンジ一致）→ TC（＋ATR14 一致）に替えた x̄_emp と DiD（pp・日クラスタ t）")
say("| 窓 | 集合 | S | T | TC | SC（参考） | TIME 実／S／T／TC | hold≥1: S / T / TC |")
say("|---|---|---|---|---|---|---|---|")
XT = {}
for wn, wm in W.items():
    for lab, bm in (("帯", band), ("補", ~band)):
        cells = [];
        for nm in ("S", "T", "TC", "SC"):
            m = wm & bm & dec & ~np.isnan(QE[nm]); x, se, t = clus(tp[m] - QE[nm][m], days[m]); XT[(wn, lab, nm)] = (x, se, t); cells.append(f"{100*x:+.2f} ({t:+.2f})")
        h1 = []
        for nm in ("S", "T", "TC"):
            m = wm & bm & dec & hold1 & ~np.isnan(QE[nm]); x, se, t = clus(tp[m] - QE[nm][m], days[m], nboot=800); h1.append(f"{100*x:+.2f} ({t:+.2f})")
        tm = f"{100*(~dec[wm&bm]).mean():.1f}／" + "／".join(f"{100*TM[nm][wm&bm].mean():.1f}" for nm in ("S", "T", "TC")) + "%"
        say(f"| {wn} | {lab} | " + " | ".join(cells) + f" | {tm} | " + " / ".join(h1) + " |")
say()
say("DiD（帯−補）: S / T / TC（独立 2 群 日クラスタ t）と、本内置換 p（T・TC）")
OT = {nm: np.concatenate([np.where(dec, tp, -1.0)[:, None], R[nm].astype(float)], axis=1) for nm in ("T", "TC")}
def perm_did(nm, masksets):
    Om = OT[nm]; na = (Om == 1).sum(1); nd = (Om >= 0).sum(1); ar = np.arange(N)
    out = {k: np.empty(NPERM) for k in masksets}
    for r_ in range(NPERM):
        u = rng.integers(0, K + 1, N); ch = Om[ar, u]
        bn = nd - (ch >= 0); bt = na - np.where(ch == 1, 1, 0); okm = (ch >= 0) & (bn > 0); xv = ch - bt / np.maximum(bn, 1)
        for k, mk in masksets.items():
            mm = mk & okm; out[k][r_] = xv[mm].mean() if mm.any() else np.nan
    return out
mk2 = {}
for wn, wm in W.items(): mk2[(wn, "帯")] = wm & band; mk2[(wn, "補")] = wm & ~band
PT = {nm: perm_did(nm, mk2) for nm in ("T", "TC")}
DID = {}
say("| 窓 | DiD S (t) | DiD T (t) [置換 p] | DiD TC (t) [置換 p] | 補 x̄: T/S・TC/S | 補 置換 p T／TC |")
say("|---|---|---|---|---|---|")
for wn, wm in W.items():
    cells = []
    for nm in ("S", "T", "TC"):
        mb = wm & band & dec & ~np.isnan(QE[nm]); mo = wm & ~band & dec & ~np.isnan(QE[nm])
        dx, _, tx = clus_diff(tp[mb] - QE[nm][mb], days[mb], tp[mo] - QE[nm][mo], days[mo]); DID[(wn, nm)] = (dx, tx)
        if nm == "S": cells.append(f"{100*dx:+.2f} ({tx:+.2f})")
        else:
            pdd = PT[nm][(wn, "帯")] - PT[nm][(wn, "補")]; p = np.nanmean(np.abs(pdd) >= abs(dx)); cells.append(f"{100*dx:+.2f} ({tx:+.2f}) [{p:.3f}]")
    rT = XT[(wn, "補", "T")][0] / XT[(wn, "補", "S")][0] if XT[(wn, "補", "S")][0] != 0 else np.nan
    rC = XT[(wn, "補", "TC")][0] / XT[(wn, "補", "S")][0] if XT[(wn, "補", "S")][0] != 0 else np.nan
    pT = np.nanmean(np.abs(PT["T"][(wn, "補")]) >= abs(XT[(wn, "補", "T")][0])); pC = np.nanmean(np.abs(PT["TC"][(wn, "補")]) >= abs(XT[(wn, "補", "TC")][0]))
    say(f"| {wn} | " + " | ".join(cells) + f" | {rT:.2f}・{rC:.2f} | {pT:.3f}／{pC:.3f} |")
say()

# ---------- R3 背景の分解 ----------
say("## R3 時刻帯の背景 q̄_emp(帯)−q̄_emp(補) の分解: 閉形式幾何 Δq_cf と残差；双子自身の超過 x_pl = 1{TP_pl} − q_cf（帯／補）")
say("| 窓 | Δq_emp S pp | Δq_cf pp（幾何） | 残差 pp | Δq_cf/Δq_emp | q̄_cf 帯／補 | b 中央値 帯／補 | x̄_pl S 帯 pp (t) | x̄_pl S 補 pp (t) | x̄_pl 帯−補 |")
say("|---|---|---|---|---|---|---|---|---|---|")
RSf = RS.astype(float)
R3 = {}
for wn, wm in W.items():
    mb = wm & band & dec & ~np.isnan(QE["S"]); mo = wm & ~band & dec & ~np.isnan(QE["S"])
    dqe = QE["S"][mb].mean() - QE["S"][mo].mean(); dqc = qcf[mb].mean() - qcf[mo].mean()
    # 双子の超過（決着双子のみ・本ごとの平均を本単位に）
    xpl = np.where(RS >= 0, RSf - qcf[:, None], np.nan); xpl_i = np.nanmean(xpl, axis=1)
    mbp = wm & band & ~np.isnan(xpl_i); mop = wm & ~band & ~np.isnan(xpl_i)
    xb, _, tb = clus(xpl_i[mbp], days[mbp]); xo, _, to = clus(xpl_i[mop], days[mop])
    R3[wn] = (dqe, dqc)
    say(f"| {wn} | {100*dqe:+.2f} | {100*dqc:+.2f} | {100*(dqe-dqc):+.2f} | {dqc/dqe if dqe else np.nan:.2f} | {qcf[mb].mean():.3f}／{qcf[mo].mean():.3f} | {np.median(bb[mb]):.2f}／{np.median(bb[mo]):.2f} | {100*xb:+.2f} ({tb:+.2f}) | {100*xo:+.2f} ({to:+.2f}) | {100*(xb-xo):+.2f} |")
say()

# ---------- R4 帯 SELL の family-wise ----------
say("## R4 事後 12 セル（帯 BUY／SELL／mid／outer × 3 窓）の本内置換 max|z| 帰無 → SELL 外・近年 の family-wise p")
cells12 = [(wn, c) for wn in W for c in ("BUY", "SELL", "mid", "outer")]
Z = np.empty((NPERM, len(cells12))); obs = {}
for ci, (wn, c) in enumerate(cells12):
    ps = PS[(wn, c)]; sd = np.nanstd(ps); Z[:, ci] = (ps - np.nanmean(ps)) / sd
    mk = masks[(wn, c)] & dec & ~np.isnan(QE["S"]); x = (tp[mk] - QE["S"][mk]).mean(); obs[(wn, c)] = (x, x / sd, mk.sum())
maxz = np.nanmax(np.abs(Z), axis=1)
say("| セル | x̄_emp pp | z（置換 sd 基準） | 単セル p | p_fw(12) |")
say("|---|---|---|---|---|")
for (wn, c), (x, zz, n_) in obs.items():
    ps = PS[(wn, c)]; p1 = np.nanmean(np.abs(ps) >= abs(x)); pfw = np.mean(maxz >= abs(zz))
    flag = " ←" if c == "SELL" and wn != "在2010-20" else ""
    say(f"| {wn} {c} n{n_} | {100*x:+.2f} | {zz:+.2f} | {p1:.3f} | {pfw:.3f}{flag} |")
say(f"max|z| 帰無: 中央値 {np.median(maxz):.2f}・95% 点 {np.quantile(maxz,0.95):.2f}")
say()

# ---------- R5 前向きセルの検出力 ----------
say("## R5 前向きセル「帯 決着 ≥1800・SET SC・x̄_emp>0 ∧ t≥2」の設計検査")
xr, ser, tr_ = XT[("近年2024-26", "帯", "SC")]; xo_, seo, _ = XT[("外2021-26", "帯", "SC")]; xi_, sei, _ = XT[("在2010-20", "帯", "SC")]
n_now = int((W["近年2024-26"] & band & dec).sum())
se1800 = ser * math.sqrt(n_now / 1800); mde = 2 * se1800
from scipy.stats import norm
def power(eff, se): return 1 - norm.cdf(2 - eff / se)
pace = int(((tr.year.to_numpy() == 2025) & band & dec).sum())
say(f"- SC 近年 x̄ {100*xr:+.2f} pp・se {100*ser:.2f}（n{n_now}）→ n1800 で se {100*se1800:.2f}・MDE(t≥2) {100*mde:.2f} pp（研究レーン ≈2.3）。")
say(f"- 検出力（t≥2）: 効果 = 近年 SC 点推定 {100*xr:+.2f} → {power(xr, se1800):.2f}；外 SC {100*xo_:+.2f} → {power(xo_, se1800):.2f}；在 SC {100*xi_:+.2f} → {power(xi_, se1800):.2f}；近年 S 点推定 +2.88 → {power(0.0288, se1800):.2f}。")
say(f"- 必要追加本数 {1800-n_now}・2025 年ペース（帯 決着 {pace}/年）で {(1800-n_now)/pace:.1f} 年。負の対照 σ_nc/se（帯 近年）{NC[('近年2024-26','帯')][1]/XT[('近年2024-26','帯','S')][1]:.2f} 倍で読むなら MDE はさらに拡大。")
say()

# ---------- 判定 ----------
say("## 判定（docstring の規則）")
# R1
p_in = np.nanmean(np.abs(PS[("在2010-20", "補")]) >= abs(XT[("在2010-20", "補", "S")][0]))
rT_in = XT[("在2010-20", "補", "T")][0] / XT[("在2010-20", "補", "S")][0]; rT_out = XT[("外2021-26", "補", "T")][0] / XT[("外2021-26", "補", "S")][0]
tT_in = XT[("在2010-20", "補", "T")][2]; tT_out = XT[("外2021-26", "補", "T")][2]
if p_in >= 0.05: v1 = "broken（在 置換 p ≥0.05・雑音）"
elif rT_in < 0.5 and rT_out < 0.5: v1 = "broken（帰属: トリガー足の大きさ・壁固有でない）"
elif rT_in >= 0.75 and rT_out >= 0.75 and tT_in <= -2 and tT_out <= -1.5: v1 = "survived"
else: v1 = "inconclusive"
say(f"- **R1 W1 帯外の負: {v1}** — 在 置換 p {p_in:.3f}・x̄_T/x̄_S 在 {rT_in:.2f}／外 {rT_out:.2f}・T の t 在 {tT_in:+.2f}／外 {tT_out:+.2f}")
# R2
dS_in, _ = DID[("在2010-20", "S")]; dS_out, _ = DID[("外2021-26", "S")]; dC_in, tC_in = DID[("在2010-20", "TC")]; dC_out, tC_out = DID[("外2021-26", "TC")]
pC_in = np.nanmean(np.abs(PT["TC"][("在2010-20", "帯")] - PT["TC"][("在2010-20", "補")]) >= abs(dC_in))
pC_out = np.nanmean(np.abs(PT["TC"][("外2021-26", "帯")] - PT["TC"][("外2021-26", "補")]) >= abs(dC_out))
if (dC_in < 0.5 * dS_in and dC_out < 0.5 * dS_out) or (pC_in > 0.10 and pC_out > 0.10): v2 = "broken"
elif pC_in < 0.05 and pC_out < 0.10: v2 = "survived"
else: v2 = "inconclusive"
say(f"- **R2 W2 DiD 残差: {v2}** — DiD S 在 {100*dS_in:+.2f}／外 {100*dS_out:+.2f} → TC 在 {100*dC_in:+.2f} (p {pC_in:.3f})／外 {100*dC_out:+.2f} (p {pC_out:.3f})・入れ子: 独立窓 2・同符号の帰無確率 1/2")
# R3
r3_in = R3["在2010-20"][1] / R3["在2010-20"][0]; r3_out = R3["外2021-26"][1] / R3["外2021-26"][0]
if r3_in >= 0.5 and r3_out >= 0.5: v3 = "broken（背景の半分以上は幾何 b の違い）"
elif r3_in <= 0.25 and r3_out <= 0.25: v3 = "survived（時刻帯の背景）"
else: v3 = "inconclusive"
say(f"- **R3 W3 背景＝時刻帯: {v3}** — Δq_cf/Δq_emp 在 {r3_in:.2f}／外 {r3_out:.2f}")
# R4
pfw_out = np.mean(maxz >= abs(obs[("外2021-26", "SELL")][1])); pfw_rec = np.mean(maxz >= abs(obs[("近年2024-26", "SELL")][1]))
v4 = "broken" if pfw_out > 0.05 else "survived（規則上）"
say(f"- **R4 W4 帯 SELL: {v4}** — p_fw(12) 外 {pfw_out:.3f}／近年 {pfw_rec:.3f}・在 符号 {'逆' if obs[('在2010-20','SELL')][0] < 0 else '同'}")
say(f"- **R5 W5 前向きセル**: 設計上、効果が近年 SC 点推定（{100*xr:+.2f} pp）のままなら検出力 {power(xr, se1800):.2f}。通るのは効果 ≥{100*mde:.1f} pp（SC 近年の {mde/xr if xr>0 else float('nan'):.1f} 倍）が続く時だけ。")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
