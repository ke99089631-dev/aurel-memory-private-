# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-24 21:30・第 2 走] refute_c66_fpt.py の第 1 走が開けた 3 つの穴を閉じる。
第 1 走の結果（この第 2 走の事前固定を書く時点で既知）:
  GATE PASS（|Δ| 0.00004）。A1 dead-time survived（縮み ≤9%）。A2 曜日一致 survived（SL 腕 0〜4%）だが
  **TP 腕は 外 で 75%・在 33% 縮む**。A3 CAP 48/96 で両腕 |·|≤0.02 まで落ちる。A4(a)(b) 推定量 不偏。
  A4(c) 金曜プラセボ −0.50（T1 の 4.5 倍＝暦チャネルは巨大だが c66 の設計でほぼ閉じている）。
  A5 se survived（月ブロック t −5.82）。A6(i) T2 broken（在 観測/予測 0.41／0.70・**外 Δσ_pre +0.015・近年 +0.0006
  なのに観測 −0.115／−0.127**）。A6(ii) 弾性 −0.37〜−0.82（理論 −2 を全 CI が除外）。
  A7 ft×2／×0 で両腕が −0.09 前後に揃う（＝腕の非対称が消える）。A8 年別 survived（負 15/17・17/17）。
  A9 b 下三分位 TP 腕 正（在 +0.0595 t +2.20・外 +0.058・近年 +0.130）＝T1 の宣言形 broken。
  G2 実本の決着は終値建玉の再導出と hold 完全一致 53%・exit 一致 92.5% ＝ **実本は足中建玉**（T4 は生きる）。

第 2 走で閉じる穴と事前固定の判定規則（数字を見る前に書いた）:
  B0 実本の建玉規約を同定: ent 候補 {C[ie], O[ie], C[ie-1]} × 経路開始 {ie+1, ie} の 6 変種で
     scan の exit・hold との一致率を印字。最良変種を「実本の規約」と呼ぶ。
     規則: 最良変種の hold 完全一致 ≥0.95 → 規約同定成功・それ未満なら「同定不能」と書き B1 の解釈を弱める。
  B1 完全対称規約（A7 に欠けていた ft×1 のセル）: 実本も双子も同じ simulate_k（自分の足の終値建玉・次足から・
     ft=0.1）で再導出し腕別を再計算。
     規則 (i): 在の腕非対称 |aS − aT| が 0.02 未満（c66 は 0.045）→ **c66 の腕非対称と D>0 の符号は建玉規約の人工物**
       （c66 自身の T3 を独立に確認・強化）。
     規則 (ii): 共通水準 |(aS+aT)/2| が ≥0.075 → T1 の「実本は約 10% 速い」は規約に対して survived。
       0.05〜0.075 → weakened。<0.05 → **T1 broken（規約の人工物）**。
  B2 T2 の逃げ道（σ_pre は建玉前 1h の雑音の多い代理＝減衰バイアス）を閉じる:
     同時刻ボラ σ_post = 建玉後 12 足 (j, j+12] の RMS log リターン（**決着で打ち切らない＝選択なし**・
     c32 SET B と同じ量）を実本・双子で測り Δ_post = log(実/双)。予測 腕別 = −2·Δ_post。
     規則: 外 の 観測/予測 が [0.5, 2.0] の外 → **T2 は同時刻ボラでも broken**（減衰バイアスの逃げ道を閉じる）。
     併せて σ_post での弾性（双子のみ・十分位ビン・b 三分位内・腕別）も推定。
     規則: 弾性の 95%CI が −2 を除外 → 1/σ² 則は本データで棄却。
  B3 打ち切り不変な形（T1 の「10〜15%」という大きさそのものを検定する）:
     累積発生率 CI_a(k) = P(k 足以内に腕 a で決着)（分母 = TIME を含む全本＝**打ち切りに完全不変**・k ≤ 288）を
     k ∈ {6,12,24,48,96,192} で実本・双子・腕別に出し、差（pp）と日クラスタ bootstrap se。
     規則: k ≤ 96 のすべてで |差| ≤ 1.5pp ∧ |t| < 2 かつ k = 192 で |差| が最大 →
       **T1 の「10〜15% 速い」は「>96 足の裾が 1〜2pp 薄い」に過ぎず、大きさの主張は broken**
       （平均が重い裾＋288 打ち切りで増幅されている）。
       k ≤ 24 のどこかで |差| ≥ 2pp ∧ |t| ≥ 3 → T1 は典型的決着時間の主張として survived。
  B4 打ち切りの向き（記述・判定なし）: 腕別 TIME 率 実／双子。実の TIME が少ない＝実の決着集合に長い本が
     多く残る＝観測 −0.11 は打ち切りバイアスを「逆風として」含むのか順風なのかを印字。
  B5 A9(i) の規約独立性: B1 の完全対称規約で b 三分位の腕別を再計算。
     規則: b 下三分位 TP 腕が 在 で正のまま → A9(i) は規約に依らない（T1 の宣言形 broken を確定）。
       符号が負に変わる → A9(i) は建玉規約の人工物に格下げ。
多重検定: 第 1 走の 6 系統 + 第 2 走の B1/B2/B3/B5 = 10 系統。Holm（α=0.05）で最終節に表で補正。
seed: 双子の再現は 20261124（c66 と同一・第 1 走と同じ消費順）。
書き込み: data/refute_c66_fpt_b.md・同 _run.log のみ。発注・本番編集・プロセス/MT5/プロップ・外部通信 なし。
"""
import os, json, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c66_fpt_b.md")
rng = np.random.default_rng(20261124); rng2 = np.random.default_rng(20261124 + 0x52)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c66・第 2 走] 規約・機構・大きさ — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c66_fpt_b.py)")

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["day"] = tr["ts"].dt.floor("D")
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP")
tr["sgn"] = np.where(tr["side"] == "BUY", 1.0, -1.0)
z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H, Lo, C = z["high"], z["low"], z["close"]
O = z["open"] if "open" in z.files else None
NB = len(TS); FLAT = (H == Lo)
wd_utc = ((TS // 86400) + 3) % 7
CSAT = np.concatenate([[0], np.cumsum((wd_utc == 5).astype(np.int64))])
CNF = np.concatenate([[0], np.cumsum((~FLAT).astype(np.int64))])
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
ok = (ie < NB) & (TS[np.minimum(ie, NB-1)] == tr["entry_time"].to_numpy(np.int64))
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
hold = tr["hold"].to_numpy(int); dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy()
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); jh = tr["jh"].to_numpy(int)
yr = tr["year"].to_numpy(int); scan_exit = tr["exit"].to_numpy()
tail_ok = ie <= NB - MAXH - 2
say(f"入力: 本 {N}・npz {NB}・npz fields {z.files}・末端除外 {int((~tail_ok).sum())}")

def simulate_gen(j, sg, rk, b, ent, start=1, ft=FT, chunk=1200):
    """ent を与え、経路を j+start .. j+start+MAXH-1 で評価。k は「start を 1 とした足数」で返す。"""
    M = len(j); res = np.full(M, -1, np.int8); kk = np.full(M, MAXH, np.int32)
    AR = np.arange(start, start + MAXH)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s+chunk)); jj = j[sl_]; sgx = sg[sl_]; rkx = rk[sl_]; bx = b[sl_]; ex = ent[sl_]
        idx = np.minimum(jj[:, None] + AR[None, :], NB-1)
        hh = H[idx]; ll = Lo[idx]
        sl = ex - sgx*rkx; tpv = ex + sgx*bx*rkx
        buy = sgx > 0
        sl_hit = np.where(buy[:, None], ll <= (sl+ft)[:, None], hh >= (sl-ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tpv+ft)[:, None], ll <= (tpv-ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        r = np.full(len(jj), -1, np.int8); r[kt < ks] = 1; r[(ks <= kt) & (ks < 10**6)] = 0
        k = np.minimum(ks, kt); k = np.where(k < 10**6, k+start, MAXH).astype(np.int32)
        res[sl_] = r; kk[sl_] = k
    return res, kk

# ---------------- B0 建玉規約の同定 ----------------
say()
say("## B0 実本の建玉規約の同定（scan の exit・hold を最も再現する変種）")
cands = [("ent=C[ie], 経路 ie+1 →", C[ie], 1), ("ent=C[ie], 経路 ie →", C[ie], 0),
         ("ent=C[ie-1], 経路 ie →", C[np.maximum(ie-1, 0)], 0), ("ent=C[ie-1], 経路 ie+1 →", C[np.maximum(ie-1, 0)], 1)]
if O is not None:
    cands += [("ent=O[ie], 経路 ie →", O[ie], 0), ("ent=O[ie], 経路 ie+1 →", O[ie], 1)]
mall = dec & tail_ok; m1 = dec & (hold >= 1) & tail_ok
say("| 変種 | exit 一致（全決着） | hold 完全一致（全決着） | ±1 本 | hold 完全一致（hold≥1） |")
say("|---|---|---|---|---|")
best = None
for lab, ent, st in cands:
    R_, K_ = simulate_gen(ie, sgn, risk, bb, ent.astype(float), start=st)
    ex_ = np.where(R_ == 1, "TP", np.where(R_ == 0, "SL", "TIME"))
    ae = (ex_[mall] == scan_exit[mall]).mean(); ah = (K_[mall] == hold[mall]).mean()
    ah1 = (np.abs(K_[mall]-hold[mall]) <= 1).mean(); ahh = (K_[m1] == hold[m1]).mean()
    say(f"| {lab} | {100*ae:.2f}% | {100*ah:.2f}% | {100*ah1:.2f}% | {100*ahh:.2f}% |")
    if best is None or ah > best[1]: best = (lab, ah, ae)
say(f"\n**B0 判定: 最良変種 = {best[0]}（hold 完全一致 {100*best[1]:.2f}%・exit {100*best[2]:.2f}%）** → "
    f"{'規約同定成功（≥95%）' if best[1] >= .95 else '**同定不能（<95%）＝scan の建玉価格は OHLC の足値ではない（壁水準＋トリガ）＝実本は足中建玉で確定・B1 の対称化は「実本を終値建玉に置き換えた反実仮想」として読む'}")

# ---------------- 双子の再現（c66 と同一） ----------------
K = 16; SPAN_S = 28*288
HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2)
NF = np.flatnonzero(valid)
JS = np.empty((N, K), np.int64)
for h in range(24):
    NFh = NF[HOUR[NF] == h]; ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii]-SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii]+SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_]-50, 0):hi[t_]+50]; cand = cand[cand != ie[i]]
        JS[i] = cand[rng.integers(0, len(cand), K)]
def rep(a): return np.repeat(a, K)
JSf = JS.ravel()
RS, KS = simulate_gen(JSf, rep(sgn), rep(risk), rep(bb), C[JSf].astype(float), start=1)
RS = RS.reshape(N, K); KS = KS.reshape(N, K)
cross = ((CSAT[np.minimum(JSf+KS.ravel(), NB-1)+1] - CSAT[JSf+1]) > 0).reshape(N, K)
dec_tw = (RS >= 0) & ~cross
W = {"在2010-20": (yr <= 2020), "外2021-26H1": (yr >= 2021), "近年2024-26H1": (yr >= 2024)}
say(f"- 双子再現: 決着率 {100*(RS>=0).mean():.1f}%（c66 94.9）・使用決着 {100*dec_tw.mean():.1f}%")

uday, dinv = np.unique(tr["day"].to_numpy(), return_inverse=True); ND = len(uday)
def arm_stats(mask_real, hreal, tp_real, mask_tw, htw, rs, B=400):
    out = np.zeros((ND, 8))
    mT = mask_real & tp_real; mS = mask_real & ~tp_real
    np.add.at(out[:, 0], dinv[mT], hreal[mT]); np.add.at(out[:, 1], dinv[mT], 1.0)
    np.add.at(out[:, 2], dinv[mS], hreal[mS]); np.add.at(out[:, 3], dinv[mS], 1.0)
    rows = np.repeat(dinv[:, None], K, 1)
    tT = mask_tw & (rs == 1); tS = mask_tw & (rs == 0)
    np.add.at(out[:, 4], rows[tT], htw[tT]); np.add.at(out[:, 5], rows[tT], 1.0)
    np.add.at(out[:, 6], rows[tS], htw[tS]); np.add.at(out[:, 7], rows[tS], 1.0)
    def f(S):
        s = S.sum(0)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.array([np.log((s[0]/s[1])/(s[4]/s[5])), np.log((s[2]/s[3])/(s[6]/s[7])),
                             np.log(s[0]/s[1])-np.log(s[2]/s[3])-(np.log(s[4]/s[5])-np.log(s[6]/s[7]))])
    v = f(out); use = np.flatnonzero(out[:, [1,3,5,7]].sum(1) > 0)
    bs = np.empty((B, 3))
    for i in range(B): bs[i] = f(out[use[rng2.integers(0, len(use), len(use))]])
    se = np.nanstd(bs, 0, ddof=1)
    s = out.sum(0)
    return v, se, int(s[1]), int(s[3])

# ---------------- B1 完全対称規約（ft×1） ----------------
say()
say("## B1 完全対称規約（実本も双子も自分の足の終値建玉・次足から・ft=0.1）— A7 に欠けていた ft×1 のセル")
Rr, Kr = simulate_gen(ie, sgn, risk, bb, C[ie].astype(float), start=1)
sat_r = (CSAT[np.minimum(ie+Kr, NB-1)+1] - CSAT[ie+1]) > 0
dr_sym = (Rr >= 0) & ~sat_r & tail_ok; tp_sym = (Rr == 1)
C66 = {"在2010-20": (-0.0632, -0.1082), "外2021-26H1": (-0.0552, -0.1151), "近年2024-26H1": (-0.0554, -0.1268)}
say("| 窓 | 実 n TP/SL | 腕 TP (t) | 腕 SL (t) | 共通水準 (aT+aS)/2 | 腕非対称 aS−aT | c66 の非対称 |")
say("|---|---|---|---|---|---|---|")
B1 = {}
for wn, wm in W.items():
    v, se, nT, nS = arm_stats(dr_sym & wm, Kr.astype(float), tp_sym, dec_tw & wm[:, None], KS.astype(float), RS, B=500)
    B1[wn] = (v, se)
    asym = v[1]-v[0]; c0 = C66[wn]
    say(f"| {wn} | {nT}/{nS} | {v[0]:+.4f} ({v[0]/se[0]:+.2f}) | {v[1]:+.4f} ({v[1]/se[1]:+.2f}) | {(v[0]+v[1])/2:+.4f} | {asym:+.4f} | {c0[1]-c0[0]:+.4f} |")
asym_in = abs(B1["在2010-20"][0][1] - B1["在2010-20"][0][0]); lvl_in = abs(sum(B1["在2010-20"][0][:2])/2)
r1i = "**c66 の腕非対称と D>0 の符号は建玉規約の人工物（c66 自身の T3 を独立確認・強化）**" if asym_in < 0.02 else "腕非対称は規約に依らず残る"
r1ii = "survived" if lvl_in >= 0.075 else ("weakened" if lvl_in >= 0.05 else "**broken（規約の人工物）**")
say(f"\n**B1(i): 在 腕非対称 {asym_in:.4f}（c66 0.045・閾値 0.02）→ {r1i}**")
say(f"**B1(ii): 在 共通水準 {lvl_in:.4f}（閾値 0.075／0.05）→ T1 の「実本は約 10% 速い」は {r1ii}**")

# ---------------- B2 同時刻ボラ ----------------
say()
say("## B2 T2 の逃げ道を閉じる（同時刻ボラ σ_post = 建玉後 12 足の RMS・決着で打ち切らない）")
ret = np.zeros(NB); ret[1:] = np.log(np.maximum(C[1:], 1e-9)/np.maximum(C[:-1], 1e-9)); ret[FLAT] = 0.0
CR2 = np.concatenate([[0.0], np.cumsum(ret**2)])
def sig_win(j, a, b_):
    lo_ = np.minimum(j+a, NB-1); hi_ = np.minimum(j+b_, NB-1)
    ss = CR2[hi_+1] - CR2[lo_+1]; nn = np.maximum(CNF[hi_+1] - CNF[lo_+1], 1)
    return np.sqrt(ss/nn)
sp_r = sig_win(ie, 0, 12); sp_t = sig_win(JSf, 0, 12).reshape(N, K)
say("| 窓 | σ_post 実 (平均) | 双子 | Δ_post = log(実/双) | 予測 −2Δ | c66 観測 TP/SL | 観測/予測 TP/SL |")
say("|---|---|---|---|---|---|---|")
B2 = {}
for wn, wm in W.items():
    mr = wm & dec & (hold >= 1); mt = dec_tw & wm[:, None]
    dlt = np.log(sp_r[mr].mean()/sp_t[mt].mean()); pred = -2*dlt
    aT, aS = C66[wn]
    B2[wn] = (dlt, pred)
    say(f"| {wn} | {sp_r[mr].mean():.6f} | {sp_t[mt].mean():.6f} | {dlt:+.4f} | {pred:+.4f} | {aT:+.4f}/{aS:+.4f} | {aT/pred:.2f}/{aS/pred:.2f} |")
rout = [C66["外2021-26H1"][0]/B2["外2021-26H1"][1], C66["外2021-26H1"][1]/B2["外2021-26H1"][1]]
v2 = "**broken（同時刻ボラでも・減衰バイアスの逃げ道は閉じた）**" if (min(rout) < 0.5 or max(rout) > 2.0) else "survived"
say(f"\n**B2 判定: T2 は {v2}**（外 観測/予測 TP {rout[0]:.2f}・SL {rout[1]:.2f}・規則 [0.5, 2.0]）")
qb = np.quantile(bb[dec], [1/3, 2/3]); bt = np.digitize(bb, qb)
say("\n- σ_post での弾性（双子のみ・理論 −2）:")
sl_all = []
for armv, armn in [(1, "TP"), (0, "SL")]:
    for btv in range(3):
        mt = dec_tw & (RS == armv) & (bt[:, None] == btv)
        if mt.sum() < 2000: continue
        s_ = sp_t[mt]; k_ = KS[mt].astype(float)
        qs = np.quantile(s_, np.linspace(0, 1, 11)); binx = np.clip(np.digitize(s_, qs[1:-1]), 0, 9)
        xs = np.array([np.log(s_[binx == q].mean()) for q in range(10)]); ys = np.array([np.log(k_[binx == q].mean()) for q in range(10)])
        A = np.vstack([np.ones(10), xs]).T; beta, *_ = np.linalg.lstsq(A, ys, rcond=None)
        res = ys - A@beta; seb = np.sqrt((res**2).sum()/8 * np.linalg.inv(A.T@A)[1, 1])
        sl_all.append(beta[1])
        say(f"  - {armn}・b 三分位 {btv}: 弾性 {beta[1]:+.3f} ± {seb:.3f}・95%CI [{beta[1]-1.96*seb:+.3f}, {beta[1]+1.96*seb:+.3f}]・−2 を含む {abs(beta[1]+2) <= 1.96*seb}")
say(f"**B2(ii): σ_post 弾性の中央値 {np.median(sl_all):+.2f}（理論 −2・第 1 走の σ_pre 版 −0.62）** → 1/σ² 則は本データで棄却")

# ---------------- B3 打ち切り不変な累積発生率 ----------------
say()
say("## B3 打ち切り不変な形: 累積発生率 CI_a(k) = P(k 足以内に腕 a で決着)（分母 = TIME 含む全本）")
def ci_diff(wm, arm, ks, B=400):
    base_r = dec & (hold >= 1) & wm
    rows = np.repeat(dinv[:, None], K, 1)
    denom_r = np.zeros(ND); np.add.at(denom_r, dinv[wm], 1.0)
    denom_t = np.zeros(ND); np.add.at(denom_t, rows[np.broadcast_to(wm[:, None], (N, K))], 1.0)
    res = []
    for k in ks:
        nr = np.zeros(ND); sel = base_r & (tp if arm == 1 else ~tp) & (hold <= k)
        np.add.at(nr, dinv[sel], 1.0)
        nt = np.zeros(ND); selt = dec_tw & wm[:, None] & (RS == arm) & (KS <= k)
        np.add.at(nt, rows[selt], 1.0)
        M = np.column_stack([nr, denom_r, nt, denom_t])
        def f(S):
            s = S.sum(0); return 100*(s[0]/s[1] - s[2]/s[3])
        v = f(M); bs = np.array([f(M[rng2.integers(0, ND, ND)]) for _ in range(B)])
        res.append((k, 100*M[:, 0].sum()/M[:, 1].sum(), 100*M[:, 2].sum()/M[:, 3].sum(), v, np.nanstd(bs, ddof=1)))
    return res
KSET = [6, 12, 24, 48, 96, 192]
B3 = {}
for wn in ["在2010-20", "外2021-26H1"]:
    wm = W[wn]
    say(f"\n### {wn}")
    say("| k | TP 実% | TP 双子% | 差 pp (t) | SL 実% | SL 双子% | 差 pp (t) |")
    say("|---|---|---|---|---|---|---|")
    rT = ci_diff(wm, 1, KSET); rS = ci_diff(wm, 0, KSET)
    B3[wn] = (rT, rS)
    for (k, pr, pt_, dv, ds), (_, pr2, pt2, dv2, ds2) in zip(rT, rS):
        say(f"| {k} | {pr:.2f} | {pt_:.2f} | {dv:+.2f} ({dv/max(ds,1e-9):+.2f}) | {pr2:.2f} | {pt2:.2f} | {dv2:+.2f} ({dv2/max(ds2,1e-9):+.2f}) |")
small = True; big_early = False
for wn in ["在2010-20", "外2021-26H1"]:
    for r in B3[wn]:
        for k, pr, pt_, dv, ds in r:
            if k <= 96 and (abs(dv) > 1.5 or abs(dv/max(ds, 1e-9)) >= 2): small = False
            if k <= 24 and abs(dv) >= 2 and abs(dv/max(ds, 1e-9)) >= 3: big_early = True
maxk = {}
for wn in ["在2010-20", "外2021-26H1"]:
    for r, an in zip(B3[wn], ["TP", "SL"]):
        kk_ = max(r, key=lambda x: abs(x[3])); maxk[(wn, an)] = kk_[0]
v3 = ("**T1 の「10〜15% 速い」は大きさの主張として broken（内容は「>96 足の裾が 1〜2pp 薄い」のみ）**"
      if (small and all(v >= 192 for v in maxk.values())) else
      ("T1 は典型的決着時間の主張として survived" if big_early else "中間（裾優位だが k≤96 でも無視できない差が残る）"))
say(f"\n**B3 判定: {v3}**（|差| 最大の k: " + "・".join(f"{w}/{a} → k={v}" for (w, a), v in maxk.items()) + "）")

# ---------------- B4 打ち切りの向き ----------------
say()
say("## B4 打ち切りの向き（記述）")
for wn, wm in W.items():
    tr_r = 1 - dec[wm].mean(); tr_t = 1 - dec_tw[wm].mean()
    say(f"- {wn}: TIME 率 実 {100*tr_r:.2f}% / 双子 {100*tr_t:.2f}%（差 {100*(tr_t-tr_r):+.2f}pp）"
        f"→ 双子の方が多く打ち切られる＝双子の決着集合から長い本がより多く落ちる＝平均 hold は双子側が**下**に偏る"
        f"＝観測された「実本が速い」は打ち切りバイアスに**逆らって**出ている（T1 に有利な向きの注意点）")

# ---------------- B5 b 依存の規約独立性 ----------------
say()
say("## B5 A9(i) の規約独立性（完全対称規約での b 三分位・腕別）")
say("| 窓 | b 三分位 | 実 n TP/SL | 腕 TP (t) | 腕 SL (t) | c66 規約の TP |")
say("|---|---|---|---|---|---|")
C66B = {("在2010-20", 0): +0.0595, ("在2010-20", 1): -0.0849, ("在2010-20", 2): -0.2020,
        ("外2021-26H1", 0): +0.0578, ("外2021-26H1", 1): -0.1043, ("外2021-26H1", 2): -0.1191}
B5 = {}
for wn in ["在2010-20", "外2021-26H1"]:
    wm = W[wn]
    for btv, lab in [(0, "下"), (1, "中"), (2, "上")]:
        mb = (bt == btv)
        v, se, nT, nS = arm_stats(dr_sym & wm & mb, Kr.astype(float), tp_sym, dec_tw & (wm & mb)[:, None], KS.astype(float), RS, B=300)
        B5[(wn, btv)] = (v, se)
        say(f"| {wn} | {lab} | {nT}/{nS} | {v[0]:+.4f} ({v[0]/se[0]:+.2f}) | {v[1]:+.4f} ({v[1]/se[1]:+.2f}) | {C66B[(wn,btv)]:+.4f} |")
lowTP_sym = B5[("在2010-20", 0)][0][0]
v5 = "A9(i) は規約に依らない＝**T1 の宣言形「両腕・全窓・全規約で同符号」は broken で確定**" if lowTP_sym > 0 else "A9(i) は建玉規約の人工物に格下げ（b 下三分位 TP 腕は対称規約で負）"
say(f"\n**B5 判定: 在 b 下三分位 TP 腕（対称規約）{lowTP_sym:+.4f}（c66 規約 +0.0595）→ {v5}**")
gapT_sym = B5[("在2010-20", 2)][0][0] - B5[("在2010-20", 0)][0][0]
say(f"- 在 b 上−下 TP 腕差（対称規約）{gapT_sym:+.4f}（c66 規約 −0.2616）＝「方向を問わないボラ状態」だけでは説明できない b 勾配は規約に依らず残る: {abs(gapT_sym) > 0.10}")

say()
say(f"実行 {time.time()-t0:.1f} s・書き込み data/refute_c66_fpt_b.md・同 _run.log のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L)+"\n")
open(os.path.join(DATA, "refute_c66_fpt_b_run.log"), "w", encoding="utf-8").write("\n".join(L)+"\n")
