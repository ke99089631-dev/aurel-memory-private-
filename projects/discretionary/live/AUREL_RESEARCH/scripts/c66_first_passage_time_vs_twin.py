# -*- coding: utf-8 -*-
"""
[cycle66 研究レーン・深化 path] 決着までの時間（first-passage time）は無ドリフト RW の予測どおりか
— TP 決着と SL 決着の保有時間の比を、同時刻・同側・同幾何の双子（実価格上のプラセボ建玉）と比べる。

事前固定（数字を見る前に書いた・2026-11-24 19:xx）:
  問い: 壁→壁（再加速）の決着時間の構造。無ドリフト BM（障壁 −a=−(1−ft)R・+B=(b+ft)R）では
        E[τ | TP] = B(2a+B)/3σ²・E[τ | SL] = a(2B+a)/3σ²・比 ρ_RW = B(2a+B)/(a(2B+a))（σ は約分）。
        b>1 なら TP の方が時間がかかる（ρ_RW ≈ 1.1〜1.3）。実本の比 ρ_real がこれから外れるかを、
        解析式でなく**双子**（実価格・離散足・ボラクラスタ・FEED_TOL・同足 SL 優先 を全部含む帰無）で測る。
  主統計: D = [log mean(hold|TP) − log mean(hold|SL)]_実 − [同]_双子  （ratio of ratios の log）。
        hold は建玉足の次足から数える（実本 hold≥1 の部分集合・双子は定義上 ≥1）。TIME（週末畳み含む）除外。
        双子が週末（土曜 UTC 足）を跨いで決着した場合は実本の規則（金曜引け畳み）に合わせ TIME 扱い（除外）。
  双子: c33 SET S と同一（同 JST 時・±28 暦日・非 flat・d=0 除外・K=16・終値建玉・次足から 288 本・refute_c27 の simulate）
        に「決着足番号 k」を返す拡張。seed 20261124。
  窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 16 年一括は edge 判定に使わない・本件は edge ではなく幾何）。
  判定（1 セル・在→外）: PASS = 在 |t_D|≥2 ∧ 外 同符号 ∧ |t_D|≥1.5 ／ それ以外 null（MDE 2se=50% 検出力・2.8se=80% を併記）。
  予測: c35（帯外の赤字は建玉後 1 時間で全部生まれる・K=1 が半分）から **D > 0**（実本の SL は双子の SL より相対的に早く来る）。
        大きさの予想 在 +0.05〜+0.10（log）・外 は半分。Markov/RW（c7/c21/c23）が決着時間にも成り立つなら D ≈ 0。
  se: 建玉日クラスタ bootstrap（B=1000・実本の日を再抽出し、その本の双子を一緒に持っていく＝対になった再抽出）。
  陽性対照: 実本の hold|SL を ×0.8（≥1）にして D が +log(1.25)=+0.223 動くか・その t（検出力の目安）。
  負の対照: 双子 16 本を 8+8 に割り、双子同士の D（期待 0）。
  記述（判定に使わない・family 宣言 ≈24 セル）: 腕別 log(mean hold 実／双子)（SL 腕・TP 腕）×3 窓・帯 jh7-12／補×3 窓・
        hold≥0 版・b 三分位・ρ_RW 解析値・中央値版・台帳（下）。
  台帳（前向き記述・1 セル）: setup_ledger.jsonl reaccel closed（候補 74: reaccel dict のみ）の ρ_ledger（hold≥1）と
        scan 近年 ρ_real の log 差（双子は無い＝M5 延長待ち）。記帳規則境界 10-24 の前後も印字。
  ゲート ㉛: n/a（条件づけでなく構造・R を動かす提案ではない）。
  衛生（必ず印字）: npz min/max・flat 比率・entry_time 格子一致・実本 決着本が週末足を含まないこと（0 を期待）・
        双子の週末跨ぎ率・TIME 率 実／双子・hold 分布分位。
  look-ahead: 双子は建玉後の足のみ。survivorship: TIME 除外は両群同規則。多年 scan なし・MT5 なし・外部通信なし。
  書き込み: data/c66_first_passage_time_result.md・data/c66_run.log のみ（cells.csv は別途 2 行）。
"""
import os, sys, json, time, collections
import numpy as np, pandas as pd
from datetime import datetime, timezone

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
LIVE = os.path.dirname(ROOT)
OUT = os.path.join(DATA, "c66_first_passage_time_result.md")
rng = np.random.default_rng(20261124)
L = []
def say(s=""): print(s, flush=True); L.append(s)

say(f"# [cycle66 研究レーン] 決着までの時間 vs 双子（first-passage time・ratio of ratios） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c66_first_passage_time_vs_twin.py)")

# ---------- scan キャッシュ ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["day"] = tr["ts"].dt.floor("D")
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP")
tr["sgn"] = np.where(tr["side"] == "BUY", 1.0, -1.0)
tr["band"] = tr["jh"].between(7, 12)
N = len(tr)

z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H, Lo, C = z["high"], z["low"], z["close"]
NB = len(TS)
FLAT = (H == Lo)
wd_utc = ((TS // 86400) + 3) % 7          # 1970-01-01 = 木曜 → Mon=0 規約で 3；0=月 ... 5=土 6=日（第 1 走は +4 で土=金の取り違え・衛生印字で検出）
SAT = (wd_utc == 5).astype(np.int64); CSAT = np.concatenate([[0], np.cumsum(SAT)])   # CSAT[i] = # Saturday bars in [0,i)
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
ok = (ie < NB) & (TS[np.minimum(ie, NB - 1)] == tr["entry_time"].to_numpy(np.int64))
say(f"本 {N}・決着 {int(tr.dec.sum())}（TP {int(tr.tp.sum())}／SL {int((tr.exit=='SL').sum())}／TIME {int((tr.exit=='TIME').sum())}）・FEED_TOL {FT}・MAX_HOLD {MAXH}")
say(f"npz {NB} 本 {pd.Timestamp(TS[0],unit='s')}..{pd.Timestamp(TS[-1],unit='s')}・flat 全体 {100*FLAT.mean():.1f}%・曜日別 flat% " +
    "/".join(f"{['月','火','水','木','金','土','日'][w]} {100*FLAT[wd_utc==w].mean():.1f}" for w in range(7)) + f"・entry_time 格子一致 {int(ok.sum())}/{N}")
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
hold = tr["hold"].to_numpy(int); dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy()
# 衛生: 決着本が週末（土曜 UTC）足を含むか
ix_end = np.minimum(ie + hold, NB - 1)
sat_in = CSAT[ix_end + 1] - CSAT[ie]
say(f"衛生: 決着本 {int(dec.sum())} のうち path に土曜 UTC 足を含む本 {int((sat_in[dec] > 0).sum())}（期待 0・c53 の週末畳み規則）・TIME 本のうち含む {int((sat_in[~dec] > 0).sum())}/{int((~dec).sum())}")
say(f"hold 分位（決着本）: TP p10/50/90 {np.percentile(hold[dec&tp],10):.0f}/{np.percentile(hold[dec&tp],50):.0f}/{np.percentile(hold[dec&tp],90):.0f}・SL {np.percentile(hold[dec&~tp],10):.0f}/{np.percentile(hold[dec&~tp],50):.0f}/{np.percentile(hold[dec&~tp],90):.0f}・hold=0 の決着本 {int((dec&(hold==0)).sum())}（{100*(dec&(hold==0)).sum()/dec.sum():.1f}%・TP {int((dec&tp&(hold==0)).sum())}／SL {int((dec&~tp&(hold==0)).sum())}）")

W = {"在2010-20": (tr.year <= 2020).to_numpy(), "外2021-26H1": (tr.year >= 2021).to_numpy(), "近年2024-26H1": (tr.year >= 2024).to_numpy()}
band = tr["band"].to_numpy()

# ---------- 双子シミュレータ（refute_c27/c33 と同一規則＋決着足 k を返す） ----------
AR = np.arange(1, MAXH + 1)
def simulate_k(j, sgn, risk, b, ft=FT, chunk=1200):
    M = len(j); res = np.full(M, -1, np.int8); kk = np.full(M, MAXH, np.int32)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg = sgn[sl_]; rk = risk[sl_]; bb = b[sl_]
        idx = jj[:, None] + AR[None, :]
        hh = H[idx]; ll = Lo[idx]
        ent = C[jj]
        sl = ent - sg * rk; tpv = ent + sg * bb * rk
        buy = sg > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft)[:, None], hh >= (sl - ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tpv + ft)[:, None], ll <= (tpv - ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        r = np.full(len(jj), -1, np.int8); r[(kt < ks)] = 1; r[(ks <= kt) & (ks < 10**6)] = 0
        k = np.minimum(ks, kt); k = np.where(k < 10**6, k + 1, MAXH).astype(np.int32)   # AR は 1 始まり → 次足 = k=1
        res[sl_] = r; kk[sl_] = k
    return res, kk

K = 16; SPAN_S = 28 * 288
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); jh = tr["jh"].to_numpy(int)
HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2)
NF = np.flatnonzero(valid)
JS = np.empty((N, K), np.int64); nS = np.empty(N, np.int64)
for h in range(24):
    NFh = NF[HOUR[NF] == h]
    ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii] + SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_]-50,0):hi[t_]+50]; cand = cand[cand != ie[i]]
        nS[i] = len(cand); JS[i] = cand[rng.integers(0, len(cand), K)]
def rep(a): return np.repeat(a, K)
t1 = time.time()
RS, KS = simulate_k(JS.ravel(), rep(sgn), rep(risk), rep(bb))
RS = RS.reshape(N, K); KS = KS.reshape(N, K)
# 双子の週末跨ぎ → TIME 扱い
JSf = JS.ravel(); KSf = KS.ravel()
cross = (CSAT[np.minimum(JSf + KSf, NB - 1) + 1] - CSAT[JSf + 1]) > 0
cross = cross.reshape(N, K)
dec_tw = (RS >= 0) & ~cross
say(f"双子生成 {N}×{K}（{time.time()-t1:.0f} s）・候補数 中央値 {np.median(nS):.0f}・jh 一致 {100*(HOUR[JS]==jh[:,None]).mean():.1f}%・双子 決着率 {100*(RS>=0).mean():.1f}%（週末跨ぎで TIME 扱い {100*((RS>=0)&cross).mean():.2f}%）→ 使用決着 {100*dec_tw.mean():.1f}%・実本 決着率 {100*dec.mean():.1f}%")
say(f"双子 hold 分位（決着・週末除外）: TP p10/50/90 {np.percentile(KS[dec_tw&(RS==1)],10):.0f}/{np.percentile(KS[dec_tw&(RS==1)],50):.0f}/{np.percentile(KS[dec_tw&(RS==1)],90):.0f}・SL {np.percentile(KS[dec_tw&(RS==0)],10):.0f}/{np.percentile(KS[dec_tw&(RS==0)],50):.0f}/{np.percentile(KS[dec_tw&(RS==0)],90):.0f}")
say()

# ---------- 統計 ----------
days = tr["day"].to_numpy()
uday, dinv = np.unique(days, return_inverse=True)
ND = len(uday)

def day_sums(mask_real, hreal, mask_tw, htw):
    """日別の [Σh_TP, n_TP, Σh_SL, n_SL] を実本・双子それぞれ返す"""
    out = np.zeros((ND, 8))
    mT = mask_real & tp; mS = mask_real & ~tp
    np.add.at(out[:, 0], dinv[mT], hreal[mT]); np.add.at(out[:, 1], dinv[mT], 1)
    np.add.at(out[:, 2], dinv[mS], hreal[mS]); np.add.at(out[:, 3], dinv[mS], 1)
    tT = mask_tw & (RS == 1); tS = mask_tw & (RS == 0)
    rows = np.repeat(dinv[:, None], K, 1)
    np.add.at(out[:, 4], rows[tT], htw[tT]); np.add.at(out[:, 5], rows[tT], 1)
    np.add.at(out[:, 6], rows[tS], htw[tS]); np.add.at(out[:, 7], rows[tS], 1)
    return out

def D_from(S):
    s = S.sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.log(s[0] / s[1]) - np.log(s[2] / s[3]); lt = np.log(s[4] / s[5]) - np.log(s[6] / s[7])
        aT = np.log((s[0] / s[1]) / (s[4] / s[5])); aS = np.log((s[2] / s[3]) / (s[6] / s[7]))
    return lr, lt, lr - lt, aT, aS

def boot(S, B=1000):
    use = np.flatnonzero(S[:, [1, 3, 5, 7]].sum(1) > 0)
    stats = np.empty((B, 5))
    for bi in range(B):
        pick = use[rng.integers(0, len(use), len(use))]
        stats[bi] = D_from(S[pick])
    return np.nanstd(stats, 0, ddof=1)

def cell(name, mask_real, hreal, mask_tw, htw, B=1000):
    S = day_sums(mask_real, hreal, mask_tw, htw)
    lr, lt, Dv, aT, aS = D_from(S); se = boot(S, B)
    nT = int((mask_real & tp).sum()); nS_ = int((mask_real & ~tp).sum())
    return dict(name=name, rho_real=np.exp(lr), rho_tw=np.exp(lt), D=Dv, se=se[2], t=Dv / se[2], aT=aT, seT=se[3], aS=aS, seS=se[4],
                nT=nT, nS=nS_, nTt=int((mask_tw & (RS == 1)).sum()), nSt=int((mask_tw & (RS == 0)).sum()),
                mhT=S[:, 0].sum() / max(S[:, 1].sum(), 1), mhS=S[:, 2].sum() / max(S[:, 3].sum(), 1),
                mhTt=S[:, 4].sum() / max(S[:, 5].sum(), 1), mhSt=S[:, 6].sum() / max(S[:, 7].sum(), 1))

def rho_rw(mask):
    """解析 RW 参照値（σ 共通の仮定・ft 込み）: Σ P_TP E[τ|TP] / Σ P_TP ÷ Σ P_SL E[τ|SL] / Σ P_SL"""
    a = 1 - tr["ft"].to_numpy()[mask]; Bv = (bb + tr["ft"].to_numpy())[mask]
    pT = a / (a + Bv); pS = Bv / (a + Bv)
    eT = Bv * (2 * a + Bv) / 3; eS = a * (2 * Bv + a) / 3
    return (np.sum(pT * eT) / np.sum(pT)) / (np.sum(pS * eS) / np.sum(pS))

hold1 = hold >= 1
HR = hold.astype(float)
say("## 1. 主セル: D = log ρ_real − log ρ_twin（ρ = mean hold|TP ÷ mean hold|SL・hold≥1・TIME/週末跨ぎ除外・建玉日クラスタ bootstrap B=1000）")
say("| 窓 | 実 n TP/SL | 双子 n TP/SL | mean hold 実 TP/SL | 双子 TP/SL | ρ_real | ρ_twin | ρ_RW(解析) | **D (t)** | MDE 2se／2.8se | 腕 TP log(実/双) (t) | 腕 SL log(実/双) (t) |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|")
main = {}
for wn, wm in W.items():
    c = cell(wn, wm & dec & hold1, HR, dec_tw & wm[:, None], KS.astype(float))
    main[wn] = c
    say(f"| {wn} | {c['nT']}/{c['nS']} | {c['nTt']}/{c['nSt']} | {c['mhT']:.2f}/{c['mhS']:.2f} | {c['mhTt']:.2f}/{c['mhSt']:.2f} | {c['rho_real']:.3f} | {c['rho_tw']:.3f} | {rho_rw(wm&dec&hold1):.3f} | **{c['D']:+.4f} ({c['t']:+.2f})** | {2*c['se']:.3f}／{2.8*c['se']:.3f} | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) |")
cin, cout = main["在2010-20"], main["外2021-26H1"]
verdict = "PASS" if (abs(cin["t"]) >= 2 and np.sign(cin["D"]) == np.sign(cout["D"]) and abs(cout["t"]) >= 1.5) else "null"
say(f"\n**判定（事前規則）: {verdict}** — 在 D {cin['D']:+.4f} (t {cin['t']:+.2f})・外 {cout['D']:+.4f} (t {cout['t']:+.2f})・予測は D>0（c35 の早期赤字）。")
say()

say("## 2. 対照")
# 陽性対照: 実本 SL の hold ×0.8（≥1）
Hinj = HR.copy(); mS_ = dec & hold1 & ~tp; Hinj[mS_] = np.maximum(1.0, np.round(HR[mS_] * 0.8))
for wn in ["在2010-20", "外2021-26H1"]:
    wm = W[wn]
    c = cell(wn, wm & dec & hold1, Hinj, dec_tw & wm[:, None], KS.astype(float), B=600)
    say(f"- 陽性対照（実本 hold|SL ×0.8・期待 ΔD ≈ +0.22）{wn}: D {c['D']:+.4f} (t {c['t']:+.2f})・ΔD {c['D']-main[wn]['D']:+.4f}")
# 負の対照: 双子 8+8
half = np.zeros((N, K), bool); half[:, :K // 2] = True
for wn in ["在2010-20", "外2021-26H1"]:
    wm = W[wn]
    SA = day_sums(np.zeros(N, bool), HR, dec_tw & wm[:, None] & half, KS.astype(float))
    SB = day_sums(np.zeros(N, bool), HR, dec_tw & wm[:, None] & ~half, KS.astype(float))
    S2 = SA.copy(); S2[:, :4] = SB[:, 4:]   # 前半 = B 側を「実」の位置に
    lr, lt, Dv, _, _ = D_from(S2); se = boot(S2, 600)
    say(f"- 負の対照（双子 8 本 vs 8 本・期待 0）{wn}: D {Dv:+.4f} (t {Dv/se[2]:+.2f})")
say()

say("## 3. 記述（判定に使わない・family ≈24 セル）")
say("| セル | 窓 | 実 n TP/SL | ρ_real | ρ_twin | D (t) | 腕 TP (t) | 腕 SL (t) |")
say("|---|---|---|---|---|---|---|---|")
def desc(label, wn, mr, hr, mt, ht, B=500):
    c = cell(label, mr, hr, mt, ht, B)
    say(f"| {label} | {wn} | {c['nT']}/{c['nS']} | {c['rho_real']:.3f} | {c['rho_tw']:.3f} | {c['D']:+.4f} ({c['t']:+.2f}) | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) |")
    return c
for wn, wm in W.items():
    desc("hold≥0 版（実本に建玉足決着を含む）", wn, wm & dec, HR, dec_tw & wm[:, None], KS.astype(float))
# 第 3 の規約（第 1 走を見て追加・記述）: 両群とも「建玉後 1 本を生き残った本」= 実 hold≥1（建玉足 0 を生存）／双子 k≥2（次足 1 を生存）・双子 k' = k−1
KS1 = (KS - 1).astype(float)
for wn, wm in W.items():
    desc("両群 1 本生存版（実 hold≥1・双子 k≥2→k−1）", wn, wm & dec & hold1, HR, dec_tw & (KS >= 2) & wm[:, None], KS1)
say(f"| （参考）hold=0 決着の腕内訳 | 全窓 | TP {int((dec&tp&(hold==0)).sum())}／SL {int((dec&~tp&(hold==0)).sum())} | hold≥1 条件づけは TP 腕を {100*(dec&tp&(hold==0)).sum()/(dec&tp).sum():.1f}%・SL 腕を {100*(dec&~tp&(hold==0)).sum()/(dec&~tp).sum():.1f}% 落とす＝腕非対称 | | | | |")
for wn, wm in W.items():
    desc("帯 jh7-12", wn, wm & dec & hold1 & band, HR, dec_tw & (wm & band)[:, None], KS.astype(float))
    desc("補 jh∉7-12", wn, wm & dec & hold1 & ~band, HR, dec_tw & (wm & ~band)[:, None], KS.astype(float))
qb = np.quantile(bb[dec], [1/3, 2/3])
for wn, wm in W.items():
    for lab, mb in [("b 下三分位", bb <= qb[0]), ("b 中", (bb > qb[0]) & (bb <= qb[1])), ("b 上三分位", bb > qb[1])]:
        desc(f"{lab}（b̄ {bb[wm&dec&hold1&mb].mean():.2f}）", wn, wm & dec & hold1 & mb, HR, dec_tw & (wm & mb)[:, None], KS.astype(float), B=300)
# 中央値版（記述・bootstrap なし）
for wn, wm in W.items():
    m = wm & dec & hold1; mt = dec_tw & wm[:, None]
    say(f"| 中央値版 ρ | {wn} | {int((m&tp).sum())}/{int((m&~tp).sum())} | {np.median(hold[m&tp])/np.median(hold[m&~tp]):.3f} | {np.median(KS[mt&(RS==1)])/np.median(KS[mt&(RS==0)]):.3f} | 実 med TP/SL {np.median(hold[m&tp]):.0f}/{np.median(hold[m&~tp]):.0f}・双子 {np.median(KS[mt&(RS==1)]):.0f}/{np.median(KS[mt&(RS==0)]):.0f} | | |")
# hold 分布の形: 実/双子の生存関数比（SL 腕・TP 腕）k=1,3,6,12,24,48,96 (外)
say()
say("### 3b. 決着時間の分布（外 2021-26H1・hold≥1）: P(hold ≤ k | 腕) 実 vs 双子")
wm = W["外2021-26H1"]; m = wm & dec & hold1; mt = dec_tw & wm[:, None]
say("| k | TP 実 | TP 双子 | SL 実 | SL 双子 |")
say("|---|---|---|---|---|")
for k in [1, 2, 3, 6, 12, 24, 48, 96]:
    say(f"| {k} | {100*(hold[m&tp]<=k).mean():.1f}% | {100*(KS[mt&(RS==1)]<=k).mean():.1f}% | {100*(hold[m&~tp]<=k).mean():.1f}% | {100*(KS[mt&(RS==0)]<=k).mean():.1f}% |")
say()

# ---------- 台帳（前向き記述） ----------
say("## 4. 台帳（setup_ledger.jsonl・reaccel dict のみ・候補 74）— 前向き記述 1 セル（双子なし＝M5 延長待ち）")
LEDGER = os.path.join(LIVE, "setup_ledger.jsonl")
rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]
setups = [r for r in rows if r.get("kind") == "setup" and "id" in r]
st = {r["id"]: dict(r) for r in setups}
for r in rows:
    if r.get("kind") == "update" and r.get("target") in st:
        for k_, v in r.items():
            if k_ not in ("kind", "target"): st[r["target"]][k_] = v
led = []
for r in st.values():
    ra = r.get("reaccel") or {}
    er = ra.get("exit_reason")
    if not er: continue
    ent, sl, tpv, hb, et, en = ra.get("entry"), ra.get("sl"), ra.get("tp"), ra.get("hold_bars"), ra.get("exit_time"), ra.get("entry_time")
    if None in (ent, sl, tpv, hb, et): continue
    rk = abs(float(ent) - float(sl))
    if rk <= 0: continue
    led.append(dict(er=er, hold=int(hb), b=abs(float(tpv) - float(ent)) / rk, risk=rk, exit_time=int(et), entry_time=int(en) if en else int(et) - 300 * int(hb)))
ld = pd.DataFrame(led)
say(f"台帳 rows {len(rows)}・setup {len(setups)}・reaccel closed {len(ld)} 内訳 {dict(collections.Counter(ld.er))}・exit_time {datetime.fromtimestamp(ld.exit_time.min(), timezone.utc):%Y-%m-%d} → {datetime.fromtimestamp(ld.exit_time.max(), timezone.utc):%Y-%m-%d %H:%M} UTC・b 中央値 {ld.b.median():.2f}（scan 近年 {np.median(bb[W['近年2024-26H1']]):.2f}）・risk 中央値 {ld.risk.median():.2f} USD")
ld["dec"] = ld.er.isin(["SL", "TP"]); ld["tp"] = ld.er == "TP"; ld["day"] = pd.to_datetime(ld.entry_time, unit="s").dt.floor("D")
say(f"台帳 hold 分位（決着）: TP p10/50/90 {np.percentile(ld.hold[ld.dec&ld.tp],10):.0f}/{np.percentile(ld.hold[ld.dec&ld.tp],50):.0f}/{np.percentile(ld.hold[ld.dec&ld.tp],90):.0f}・SL {np.percentile(ld.hold[ld.dec&~ld.tp],10):.0f}/{np.percentile(ld.hold[ld.dec&~ld.tp],50):.0f}/{np.percentile(ld.hold[ld.dec&~ld.tp],90):.0f}・hold=0 決着 {int((ld.dec&(ld.hold==0)).sum())}")
def rho_boot(df, B=2000):
    df = df[df.dec & (df.hold >= 1)]
    g = df.groupby("day").apply(lambda x: pd.Series(dict(hT=x.hold[x.tp].sum(), nT=x.tp.sum(), hS=x.hold[~x.tp].sum(), nS=(~x.tp).sum()))).to_numpy(float)
    s = g.sum(0); lr = np.log(s[0] / s[1]) - np.log(s[2] / s[3])
    bs = np.empty(B)
    for i in range(B):
        p = g[rng.integers(0, len(g), len(g))].sum(0)
        with np.errstate(divide="ignore", invalid="ignore"): bs[i] = np.log(p[0] / p[1]) - np.log(p[2] / p[3])
    return lr, np.nanstd(bs, ddof=1), int(s[1]), int(s[3]), s[0] / s[1], s[2] / s[3]
lr_l, se_l, nT_l, nS_l, mT_l, mS_l = rho_boot(ld)
cr = main["近年2024-26H1"]
# scan 近年 ρ_real の se（実側だけ）
S = day_sums(W["近年2024-26H1"] & dec & hold1, HR, dec_tw & W["近年2024-26H1"][:, None], KS.astype(float))
use = np.flatnonzero(S[:, [1, 3]].sum(1) > 0); bsr = np.empty(1000)
for i in range(1000):
    p = S[use[rng.integers(0, len(use), len(use))]].sum(0); bsr[i] = np.log(p[0] / p[1]) - np.log(p[2] / p[3])
se_r = bsr.std(ddof=1)
dl = lr_l - np.log(cr["rho_real"]); se_dl = np.sqrt(se_l**2 + se_r**2)
say(f"**台帳 ρ_ledger（hold≥1）= {np.exp(lr_l):.3f}**（mean hold TP {mT_l:.2f} n {nT_l}／SL {mS_l:.2f} n {nS_l}・log se {se_l:.3f}）vs scan 近年 ρ_real {cr['rho_real']:.3f}（se {se_r:.3f}）→ log 差 {dl:+.4f} (t {dl/se_dl:+.2f})・scan 近年 双子 ρ_twin {cr['rho_tw']:.3f} との log 差 {lr_l-np.log(cr['rho_tw']):+.4f}")
# 幾何（b）の組成差の参照: 台帳 b で解析 ρ_RW・scan 近年を台帳の b 三分位シェアで再重み付け
ldd = ld[ld.dec & (ld.hold >= 1)]
a_l = 1 - FT / ldd.risk.to_numpy(); B_l = ldd.b.to_numpy() + FT / ldd.risk.to_numpy()
pT_l = a_l / (a_l + B_l); pS_l = B_l / (a_l + B_l)
rho_rw_led = (np.sum(pT_l * B_l * (2 * a_l + B_l) / 3) / pT_l.sum()) / (np.sum(pS_l * a_l * (2 * B_l + a_l) / 3) / pS_l.sum())
mrec = W["近年2024-26H1"] & dec & hold1
bins_ = np.array([-np.inf, qb[0], qb[1], np.inf])
sh_led = np.histogram(ldd.b, bins_)[0] / len(ldd); sh_scan = np.histogram(bb[mrec], bins_)[0] / mrec.sum()
wgt = (sh_led / sh_scan)[np.digitize(bb, bins_) - 1]
def rho_w(m, w):
    return (np.sum(w[m & tp] * HR[m & tp]) / np.sum(w[m & tp])) / (np.sum(w[m & ~tp] * HR[m & ~tp]) / np.sum(w[m & ~tp]))
say(f"- 幾何の参照: 台帳 b 三分位シェア（scan 全体の切点 {qb[0]:.2f}/{qb[1]:.2f}）{np.round(sh_led,2)} vs scan 近年 {np.round(sh_scan,2)}・解析 ρ_RW 台帳 {rho_rw_led:.3f} vs scan 近年 {rho_rw(mrec):.3f}・scan 近年 ρ_real を台帳 b 組成に再重み付け {rho_w(mrec, wgt):.3f}（生 {rho_w(mrec, np.ones(N)):.3f}）→ 台帳 1.49 のうち b 組成で説明される分 log {np.log(rho_w(mrec, wgt)/rho_w(mrec, np.ones(N))):+.3f}")
cut = int(datetime(2026, 10, 24, 0, 0, tzinfo=timezone.utc).timestamp())
for lab, m in [("exit ≤10-24（旧記帳規則の疑い）", ld.exit_time < cut), ("exit >10-24", ld.exit_time >= cut)]:
    sub = ld[m]
    if (sub.dec & (sub.hold >= 1)).sum() > 20:
        a, b_, nt, ns, mt_, ms_ = rho_boot(sub, 800)
        say(f"- {lab}: ρ {np.exp(a):.3f}（se {b_:.3f}・TP n {nt} mean {mt_:.2f}／SL n {ns} mean {ms_:.2f}）")
say()
say(f"実行 {time.time()-t0:.1f} s・書き込み {os.path.relpath(OUT, ROOT)}・data/c66_run.log のみ・多年 scan なし・MT5 なし・外部通信なし")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
open(os.path.join(DATA, "c66_run.log"), "w", encoding="utf-8").write("\n".join(L) + "\n")
