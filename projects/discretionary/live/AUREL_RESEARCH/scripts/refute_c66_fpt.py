# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-24 21:30] 対象 = cycle66 (18:45) first-passage time が null 判定の脇に
「生き残った記述（全 3 窓・両腕・全規約で同符号）」として肯定形で書いた主張と、その機構主張。

PROMOTED.md は空＝昇格候補ゼロ。c66 の主セル D は事前規則どおり null（在 t 1.75）＝破る余地なし。
よって c66 が肯定形・強い t（3〜6）で書いた以下を壊しにいく。

攻撃対象（事前に固定・数字を見る前に書いた）:
  T1 「実本は双子より 10〜15% 速く決着する（両腕・全窓・全規約で同符号）」
      腕別 log(mean hold 実/双) SL −0.108/−0.115/−0.127 (t −6.4/−4.8/−3.4)・TP −0.063/−0.055/−0.055
  T2 「c32 のボラ +5〜7% と量が合う（mean hold ∝ 1/σ² → hold −10〜14%）・方向を問わず速い＝ボラ状態」
  T3 「D は規約で 0〜+0.06 の幅に入り決着時間の非対称は市場の事実として立たない」（c66 の自己反証の形）
  T4 c66 の最重大反証 第 2「双子は終値建玉・実本は途中建玉＝0.5 本の露出差（log −0.015〜−0.02）」
  T5 「ρ_twin ≈ ρ_RW（±0.03）＝双子シミュレータの新しい整合テスト」

GATE（これを通らなければどの判定も書かない）:
  G1 c66 の双子抽選をビット一致で再現（同 seed 20261124・同ループ順）し、主セル 3 窓の D と
     腕別 6 値を |Δ| ≤ 0.0005 で再現。双子決着率・mean hold も再現。
  G2 実本の決着（exit・hold）を npz から simulate_k(j=ie, ent=C[ie]) で独立に再導出し一致率を印字。
     ＝実本の建玉規約（終値建玉か足中建玉か）を実証で決める。T4 の成否はここで決まる。
     規則: hold≥1 の決着本で exit 一致率 ≥0.98 ∧ hold 一致率 ≥0.95 なら「実本も終値建玉・次足から」
     ＝T4 の 0.5 本露出は存在しない（c66 の caveat 2 は void・訂正）。<0.90 なら足中建玉で T4 は生きる。

攻撃（すべて事前固定・判定規則つき）:
  A1 死に時間（dead-time）時計: hold は「足数」で数えられ、flat 足（H==Lo・祝日/休場/週末）は
     障壁を越えられない死に時間。双子の置かれる暦位置が実本より下流に flat を多く含むなら、
     双子の足数 hold は機械的に長くなる＝「実本が速い」は市場の内容ゼロの人工物。
     測定: 決着区間 (j, j+k] の flat 足数を腕別・群別に印字 → hold_active = k − nflat で腕別を再計算。
     判定: 在 ∧ 外 の両腕で |腕別| が c66 比 ≥50% 縮む → **T1 broken**／25〜50% → weakened／<25% → survived。
  A2 曜日・暦組成: 実本の UTC 曜日分布 vs 双子の分布を印字。双子を「実本と同じ UTC 曜日」に限定して
     再抽選（K=16・別 Generator）し腕別を再計算。判定規則は A1 と同じ。
  A3 打ち切り（censoring）: 両群を CAP ∈ {48, 96, 144} で同一に再打ち切り（CAP 超＝TIME 扱い・両群同規則）
     し腕別を再計算。判定: 3 CAP すべてで ≥50% 縮む ∨ 2 CAP 以上で符号反転 → **T1 broken**。
     （c66 自身の分布表から効果は裾にあるので、縮むこと自体は「裾限定」への精錬で broken ではない。
       ≈0 になった時だけ broken と事前に決める。）
  A4 プラセボ・推定量の自己校正（c66 は負の対照を D でしか印字せず腕別を出していない＝穴）:
     (a) 双子 col 0 を偽実本・残り 15 本を双子 → 腕別 期待 0。
     (b) 双子 8 vs 8 → 腕別 期待 0。
     (c) 暦組成プラセボ: 偽実本 = ±28 日内の「金曜のみ」から抽選・双子 = 全 pool
         → 純粋な暦置き換えが作れる腕別 log の大きさを校正。|それ| ≥ 0.11 なら A1/A2 の機構は
         T1 を大きさとして説明しうる。
     判定: (a) ∨ (b) で |腕別| ≥ 0.03 ∧ |t| ≥ 2 → 推定量に偏り＝T1 の 0.11 は信用できない（broken）。
  A5 se の頑健性: 建玉日クラスタ bootstrap を (i) 暦月ブロック (ii) 年クラスタ に置換。
     双子の path は本間で重なる（±28 日 pool の共有）ので日クラスタは独立性を過大評価しうる。
     判定: 在 SL 腕の |t| < 3 → T1 の「t −6.4」は過大（weakened）／|t| < 2 → broken。
  A6 T2 の算術: 建玉前 1h（(j−12, j]）の RMS log リターン σ_pre（flat 足を分母から除く）を実本・双子で測り
     Δ = log(σ_pre 実／双子) を窓別に出す。c66 の主張は −2Δ ≈ −0.11。
     判定: 観測/予測が [0.5, 2.0] の外 ∨ 符号不一致 → **T2 broken**。
     併せて弾性の直接推定: 双子のみで σ_pre 十分位ビン × b 三分位 × 腕 ごとに log(mean hold) を
     log σ̄ に回帰し傾き（理論 −2）。95%CI が −2 を除外 → 1/σ² 則は本データで棄却（T2 の土台 broken）。
  A7 コスト倍（補遺 C 必須）: ft = FEED_TOL を 2 倍（0.1→0.2・SL は早く TP は遅くなる悲観側）と
     0 倍の 2 変種で**両群を同じ simulate_k で**再導出し腕別を再計算（G2 が通れば対称）。
     判定: 両変種で ≥50% 縮む → T1 broken。
  A8 レジーム部分集合: 暦年ごとの SL 腕・TP 腕 log(実/双)（2010-2026・17 年）。
     判定: 負の年が <60% → 「全窓で同符号」の形が broken／≥80% → survived。
  A9 b 依存 vs 機構: c66 自身の表で b 下三分位の **TP 腕は正**（在 +0.059 t +2.15／外 +0.058／近年 +0.130）。
     判定 (i): b 下三分位 TP 腕が 3 窓すべて正 ∧ 在 |t| ≥ 2 → T1 の宣言形「両腕・全窓・全規約で同符号」は
       **broken**（効果は普遍でなく b に依存）。
     判定 (ii): b 上 − b 下 の腕別差が |0.10| 超 ∧ |t| ≥ 2 → 「方向を問わないボラ状態」だけでは不十分
       （T2 の機構 broken／少なくとも不完全）。
     判定 (iii): A1 の active 時計でも b 依存が残るか（残れば dead-time では説明できない）。

多重検定: 形式的な検定は A4(a)(b)・A5・A6 の弾性・A8・A9 の 6 系統。Holm（α=0.05）で補正して報告。
  記述セル family は宣言 ≈40（腕別 2 × 窓 3 × 変種 7）＝個別の名目有意は主張に使わない。
look-ahead: 双子 pool は ±28 日（未来を含む）＝c66 と同じ記述専用の制約を継承。σ_pre は建玉前のみ。
survivorship: TIME/CAP 除外は常に両群同規則で適用し、腕別の落ちる割合を数字を見る前に印字（候補 114 遵守）。
seed: 再現部 20261124（c66 と同一）・私の新規抽選 20261124 + 0x52（別 Generator）。
事前の最重大反証（自分の攻撃への）:
  (i) A1/A2 が縮めても「実本が速い」が消えるのではなく「暦ではなくボラ」の切り分けに失敗しただけの
      可能性がある → flat 足は 1 本も価格を動かさないので active 時計は上限ではなく正しい時計だと主張するが、
      active 時計は「実時間」ではない（flat が混ざる区間は実時間で長い）→ 両方印字して読者に残す。
  (ii) A9(i) は c66 の表の読み替えに過ぎず新しい計算ではない → 私の独立再現（G1）で同じ数字が出ることと、
      active 時計・コスト倍でも符号が正のままかを足して初めて break と呼ぶ。
  (iii) n は大きいが双子は 1 本につき 16 本で pool を共有＝有効 n は遥かに小さい（A5 が効く）。
書き込み: data/refute_c66_fpt.md・同 _run.log のみ（backlog.md・cells.csv は研究レーンの正本なので触らない）。
発注・本番編集・プロセス/MT5/プロップ接触・外部通信 なし。
"""
import os, sys, json, time, collections
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c66_fpt.md")
rng = np.random.default_rng(20261124)          # c66 と同一（再現用・最初の消費が JS 抽選であること必須）
rng2 = np.random.default_rng(20261124 + 0x52)  # 私の新規抽選・bootstrap 用
L = []
def say(s=""): print(s, flush=True); L.append(s)

say(f"# [REFUTE c66] first-passage time: 「実本は双子より 10〜15% 速い」を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c66_fpt.py)")

# ---------------- 入力（c66 と同一） ----------------
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
wd_utc = ((TS // 86400) + 3) % 7
SAT = (wd_utc == 5).astype(np.int64); CSAT = np.concatenate([[0], np.cumsum(SAT)])
CNF = np.concatenate([[0], np.cumsum((~FLAT).astype(np.int64))])     # CNF[i] = # 非 flat 足 in [0,i)
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
ok = (ie < NB) & (TS[np.minimum(ie, NB - 1)] == tr["entry_time"].to_numpy(np.int64))
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
hold = tr["hold"].to_numpy(int); dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy()
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); jh = tr["jh"].to_numpy(int)
yr = tr["year"].to_numpy(int)
say(f"入力: 本 {N}・決着 {int(dec.sum())}（TP {int(tp[dec].sum())}／SL {int((~tp[dec]).sum())}）・FEED_TOL {FT}・MAX_HOLD {MAXH}・npz {NB} 本・flat {100*FLAT.mean():.1f}%")

# ---------------- 双子シミュレータ（c66 と同一・k を返す） ----------------
AR = np.arange(1, MAXH + 1)
def simulate_k(j, sg, rk, b, ft=FT, chunk=1200):
    M = len(j); res = np.full(M, -1, np.int8); kk = np.full(M, MAXH, np.int32)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sgx = sg[sl_]; rkx = rk[sl_]; bx = b[sl_]
        idx = np.minimum(jj[:, None] + AR[None, :], NB - 1)   # 末端クリップ（実本の再導出用・双子 pool は valid で除外済み）
        hh = H[idx]; ll = Lo[idx]
        ent = C[jj]
        sl = ent - sgx * rkx; tpv = ent + sgx * bx * rkx
        buy = sgx > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft)[:, None], hh >= (sl - ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tpv + ft)[:, None], ll <= (tpv - ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        r = np.full(len(jj), -1, np.int8); r[(kt < ks)] = 1; r[(ks <= kt) & (ks < 10**6)] = 0
        k = np.minimum(ks, kt); k = np.where(k < 10**6, k + 1, MAXH).astype(np.int32)
        res[sl_] = r; kk[sl_] = k
    return res, kk

# ---------------- G1: c66 の双子抽選をビット一致で再現 ----------------
K = 16; SPAN_S = 28 * 288
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
        if len(cand) == 0: cand = NFh[max(lo[t_]-50, 0):hi[t_]+50]; cand = cand[cand != ie[i]]
        nS[i] = len(cand); JS[i] = cand[rng.integers(0, len(cand), K)]
def rep(a): return np.repeat(a, K)
RS, KS = simulate_k(JS.ravel(), rep(sgn), rep(risk), rep(bb))
RS = RS.reshape(N, K); KS = KS.reshape(N, K)
JSf = JS.ravel(); KSf = KS.ravel()
cross = ((CSAT[np.minimum(JSf + KSf, NB - 1) + 1] - CSAT[JSf + 1]) > 0).reshape(N, K)
dec_tw = (RS >= 0) & ~cross
say(f"G1 双子再現: 候補数 中央値 {np.median(nS):.0f}（c66 479）・jh 一致 {100*(HOUR[JS]==jh[:,None]).mean():.1f}%・決着率 {100*(RS>=0).mean():.1f}%（c66 94.9）・使用決着 {100*dec_tw.mean():.1f}%")

W = {"在2010-20": (tr.year <= 2020).to_numpy(), "外2021-26H1": (tr.year >= 2021).to_numpy(), "近年2024-26H1": (tr.year >= 2024).to_numpy()}
band = tr["band"].to_numpy()
hold1 = hold >= 1

# ---------------- 共通推定器（クラスタ可変） ----------------
def make_cluster(kind):
    if kind == "day":   key = tr["day"].to_numpy()
    elif kind == "mon": key = (tr.ts.dt.year * 12 + tr.ts.dt.month).to_numpy()
    elif kind == "year": key = yr
    u, inv = np.unique(key, return_inverse=True)
    return len(u), inv

def sums(nc, inv, mask_real, hreal, mask_tw, htw):
    out = np.zeros((nc, 8))
    mT = mask_real & tp; mS = mask_real & ~tp
    np.add.at(out[:, 0], inv[mT], hreal[mT]); np.add.at(out[:, 1], inv[mT], 1.0)
    np.add.at(out[:, 2], inv[mS], hreal[mS]); np.add.at(out[:, 3], inv[mS], 1.0)
    tT = mask_tw & (RS == 1); tS = mask_tw & (RS == 0)
    rows = np.repeat(inv[:, None], K, 1)
    np.add.at(out[:, 4], rows[tT], htw[tT]); np.add.at(out[:, 5], rows[tT], 1.0)
    np.add.at(out[:, 6], rows[tS], htw[tS]); np.add.at(out[:, 7], rows[tS], 1.0)
    return out

def stat(S):
    s = S.sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.log(s[0]/s[1]) - np.log(s[2]/s[3]); lt = np.log(s[4]/s[5]) - np.log(s[6]/s[7])
        aT = np.log((s[0]/s[1])/(s[4]/s[5])); aS = np.log((s[2]/s[3])/(s[6]/s[7]))
    return np.array([lr, lt, lr-lt, aT, aS])

def boot(S, B, gen):
    use = np.flatnonzero(S[:, [1,3,5,7]].sum(1) > 0)
    st = np.empty((B, 5))
    for i in range(B): st[i] = stat(S[use[gen.integers(0, len(use), len(use))]])
    return np.nanstd(st, 0, ddof=1)

def cellv(mask_real, hreal, mask_tw, htw, B=400, cl="day", gen=None):
    nc, inv = make_cluster(cl)
    S = sums(nc, inv, mask_real, hreal, mask_tw, htw)
    v = stat(S); se = boot(S, B, gen or rng2)
    s = S.sum(0)
    return dict(D=v[2], seD=se[2], aT=v[3], seT=se[3], aS=v[4], seS=se[4],
                rr=np.exp(v[0]), rt=np.exp(v[1]), nT=int(s[1]), nS=int(s[3]),
                mhT=s[0]/max(s[1],1), mhS=s[2]/max(s[3],1), mhTt=s[4]/max(s[5],1), mhSt=s[6]/max(s[7],1))

HR = hold.astype(float); KSf64 = KS.astype(float)
say()
say("## G1 主セル再現（c66 の表 1 と同一であること）")
say("| 窓 | 実 n TP/SL | mean hold 実 TP/SL | 双子 TP/SL | ρ_real | ρ_twin | D (t) | 腕 TP (t) | 腕 SL (t) |")
say("|---|---|---|---|---|---|---|---|---|")
C66 = {"在2010-20": dict(D=0.0450, aT=-0.0632, aS=-0.1082, tS=-6.39),
       "外2021-26H1": dict(D=0.0599, aT=-0.0552, aS=-0.1151, tS=-4.78),
       "近年2024-26H1": dict(D=0.0714, aT=-0.0554, aS=-0.1268, tS=-3.37)}
base = {}
for wn, wm in W.items():
    c = cellv(wm & dec & hold1, HR, dec_tw & wm[:, None], KSf64, B=600)
    base[wn] = c
    say(f"| {wn} | {c['nT']}/{c['nS']} | {c['mhT']:.2f}/{c['mhS']:.2f} | {c['mhTt']:.2f}/{c['mhSt']:.2f} | {c['rr']:.3f} | {c['rt']:.3f} | {c['D']:+.4f} ({c['D']/c['seD']:+.2f}) | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) |")
gmax = max(max(abs(base[w]['D']-C66[w]['D']), abs(base[w]['aT']-C66[w]['aT']), abs(base[w]['aS']-C66[w]['aS'])) for w in W)
say(f"\n**G1 判定: 最大 |Δ| vs c66 = {gmax:.5f}** → {'GATE PASS（≤0.0005）' if gmax <= 5e-4 else 'GATE FAIL — 再現できていない。以下の判定は書かない'}")

# ---------------- G2: 実本の建玉規約を実証で決める（T4） ----------------
say()
say("## G2 実本の決着を npz から独立再導出（終値建玉か足中建玉か＝T4 の成否）")
tail_ok = ie <= NB - MAXH - 2
say(f"- 末端クリップで除外する本（ie + 288 > npz 末端）: {int((~tail_ok).sum())}/{N}")
R_re, K_re = simulate_k(ie, sgn, risk, bb)
exit_re = np.where(R_re == 1, "TP", np.where(R_re == 0, "SL", "TIME"))
scan_exit = tr["exit"].to_numpy()
m = dec & hold1 & tail_ok
agree_exit = (exit_re[m] == scan_exit[m]).mean()
agree_hold = (K_re[m] == hold[m]).mean()
agree_hold1 = (np.abs(K_re[m] - hold[m]) <= 1).mean()
say(f"- hold≥1 の決着本 {int(m.sum())}: exit 一致 {100*agree_exit:.2f}%・hold 完全一致 {100*agree_hold:.2f}%・±1 本 {100*agree_hold1:.2f}%")
say(f"- hold=0 の決着本 {int((dec&~hold1).sum())}（TP {int((dec&tp&~hold1).sum())}／SL {int((dec&~tp&~hold1).sum())}）の再導出: "
    f"TP {int((R_re[dec&~hold1]==1).sum())}／SL {int((R_re[dec&~hold1]==0).sum())}／TIME {int((R_re[dec&~hold1]<0).sum())}・"
    f"再導出 hold 中央値 {np.median(K_re[dec&~hold1]):.0f}")
T4 = "void（実本も終値建玉・次足から＝0.5 本の露出差は存在しない）" if (agree_exit >= 0.98 and agree_hold >= 0.95) else ("部分的" if agree_hold >= 0.90 else "生きる（足中建玉）")
say(f"**G2 判定: T4（0.5 本露出差）= {T4}**")

# ---------------- A1 dead-time 時計 ----------------
say()
say("## A1 dead-time 時計（flat 足は障壁を越えられない死に時間・hold_active = 足数 − flat 足数）")
act_real = (CNF[np.minimum(ie + hold, NB-1) + 1] - CNF[np.minimum(ie + 1, NB-1)]).astype(float)
act_real = np.maximum(act_real, 1.0)
act_tw = (CNF[np.minimum(JSf + KSf, NB-1) + 1] - CNF[np.minimum(JSf + 1, NB-1)]).astype(float).reshape(N, K)
act_tw = np.maximum(act_tw, 1.0)
say("| 窓 | 腕 | flat 足 平均 実/双子 | flat 率 実/双子 | 腕別 足時計 (t) | 腕別 active 時計 (t) | 縮み |")
say("|---|---|---|---|---|---|---|")
A1res = {}
for wn, wm in W.items():
    c = cellv(wm & dec & hold1, act_real, dec_tw & wm[:, None], act_tw, B=400)
    A1res[wn] = c
    b0 = base[wn]
    for arm, a_old, t_old, a_new, t_new, mr, mt in [
        ("TP", b0['aT'], b0['aT']/b0['seT'], c['aT'], c['aT']/c['seT'], wm&dec&hold1&tp, dec_tw&wm[:,None]&(RS==1)),
        ("SL", b0['aS'], b0['aS']/b0['seS'], c['aS'], c['aS']/c['seS'], wm&dec&hold1&~tp, dec_tw&wm[:,None]&(RS==0))]:
        fr = (hold[mr] - act_real[mr]).mean(); ft_ = (KS[mt] - act_tw[mt]).mean()
        rr_ = 1 - act_real[mr].sum()/hold[mr].sum(); rt_ = 1 - act_tw[mt].sum()/KS[mt].sum()
        shr = 1 - abs(a_new)/max(abs(a_old), 1e-9)
        say(f"| {wn} | {arm} | {fr:.2f}/{ft_:.2f} | {100*rr_:.1f}%/{100*rt_:.1f}% | {a_old:+.4f} ({t_old:+.2f}) | {a_new:+.4f} ({t_new:+.2f}) | {100*shr:+.0f}% |")
shr_in = [1-abs(A1res["在2010-20"]['aT'])/abs(base["在2010-20"]['aT']), 1-abs(A1res["在2010-20"]['aS'])/abs(base["在2010-20"]['aS'])]
shr_out = [1-abs(A1res["外2021-26H1"]['aT'])/abs(base["外2021-26H1"]['aT']), 1-abs(A1res["外2021-26H1"]['aS'])/abs(base["外2021-26H1"]['aS'])]
v1 = "broken" if (min(shr_in) >= .5 and min(shr_out) >= .5) else ("weakened" if (min(shr_in) >= .25 and min(shr_out) >= .25) else "survived")
say(f"\n**A1 判定: T1 は {v1}**（在 縮み TP {100*shr_in[0]:+.0f}% / SL {100*shr_in[1]:+.0f}%・外 TP {100*shr_out[0]:+.0f}% / SL {100*shr_out[1]:+.0f}%）")

# ---------------- A2 曜日・暦組成 ----------------
say()
say("## A2 曜日・暦組成（双子を実本と同じ UTC 曜日に限定して再抽選）")
wd_real = wd_utc[ie]; wd_twin = wd_utc[JS]
nm = ['月','火','水','木','金','土','日']
say("- 実本 UTC 曜日% " + "/".join(f"{nm[w]} {100*(wd_real==w).mean():.1f}" for w in range(7)))
say("- 双子 UTC 曜日% " + "/".join(f"{nm[w]} {100*(wd_twin==w).mean():.1f}" for w in range(7)))
JS2 = JS.copy()
WDNF = wd_utc[NF]
for h in range(24):
    sel_h = (HOUR[NF] == h)
    ii = np.flatnonzero(jh == h)
    for w in range(7):
        iw = ii[wd_real[ii] == w]
        if len(iw) == 0: continue
        NFhw = NF[sel_h & (WDNF == w)]
        if len(NFhw) == 0: continue
        lo = np.searchsorted(NFhw, np.maximum(ie[iw] - SPAN_S, 0)); hi = np.searchsorted(NFhw, ie[iw] + SPAN_S)
        for t_, i in enumerate(iw):
            cand = NFhw[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
            if len(cand) == 0: continue
            JS2[i] = cand[rng2.integers(0, len(cand), K)]
RS2, KS2 = simulate_k(JS2.ravel(), rep(sgn), rep(risk), rep(bb))
RS2 = RS2.reshape(N, K); KS2 = KS2.reshape(N, K)
cross2 = ((CSAT[np.minimum(JS2.ravel() + KS2.ravel(), NB-1) + 1] - CSAT[JS2.ravel() + 1]) > 0).reshape(N, K)
dec_tw2 = (RS2 >= 0) & ~cross2
say(f"- 再抽選: 曜日一致 {100*(wd_utc[JS2]==wd_real[:,None]).mean():.1f}%・jh 一致 {100*(HOUR[JS2]==jh[:,None]).mean():.1f}%・決着率 {100*(RS2>=0).mean():.1f}%")
RS_save, KS_save, dec_save = RS, KS, dec_tw
RS, KS, dec_tw = RS2, KS2, dec_tw2
A2res = {}
say("| 窓 | 腕 TP 足時計 (t) | 腕 SL 足時計 (t) | 縮み TP/SL |")
say("|---|---|---|---|")
for wn, wm in W.items():
    c = cellv(wm & dec & hold1, HR, dec_tw & wm[:, None], KS.astype(float), B=400)
    A2res[wn] = c; b0 = base[wn]
    say(f"| {wn} | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) | {100*(1-abs(c['aT'])/abs(b0['aT'])):+.0f}% / {100*(1-abs(c['aS'])/abs(b0['aS'])):+.0f}% |")
s_in = [1-abs(A2res["在2010-20"]['aT'])/abs(base["在2010-20"]['aT']), 1-abs(A2res["在2010-20"]['aS'])/abs(base["在2010-20"]['aS'])]
s_out = [1-abs(A2res["外2021-26H1"]['aT'])/abs(base["外2021-26H1"]['aT']), 1-abs(A2res["外2021-26H1"]['aS'])/abs(base["外2021-26H1"]['aS'])]
v2 = "broken" if (min(s_in) >= .5 and min(s_out) >= .5) else ("weakened" if (min(s_in) >= .25 and min(s_out) >= .25) else "survived")
say(f"\n**A2 判定: T1 は {v2}**")
RS, KS, dec_tw = RS_save, KS_save, dec_save

# ---------------- A3 打ち切り ----------------
say()
say("## A3 打ち切り CAP（両群同規則・CAP 超は TIME 扱い）")
say("| CAP | 窓 | 落ちる率 実 TP/SL | 双子 TP/SL | 腕 TP (t) | 腕 SL (t) | 縮み TP/SL |")
say("|---|---|---|---|---|---|---|")
A3 = {}
for CAP in [48, 96, 144]:
    dr = dec & hold1 & (hold <= CAP); dt_ = dec_tw & (KS <= CAP)
    for wn in ["在2010-20", "外2021-26H1"]:
        wm = W[wn]
        lr_T = 1 - (dr&wm&tp).sum()/max((dec&hold1&wm&tp).sum(),1); lr_S = 1 - (dr&wm&~tp).sum()/max((dec&hold1&wm&~tp).sum(),1)
        lt_T = 1 - (dt_&wm[:,None]&(RS==1)).sum()/max((dec_tw&wm[:,None]&(RS==1)).sum(),1)
        lt_S = 1 - (dt_&wm[:,None]&(RS==0)).sum()/max((dec_tw&wm[:,None]&(RS==0)).sum(),1)
        c = cellv(dr & wm, HR, dt_ & wm[:, None], KS.astype(float), B=300)
        A3[(CAP, wn)] = c; b0 = base[wn]
        say(f"| {CAP} | {wn} | {100*lr_T:.1f}%/{100*lr_S:.1f}% | {100*lt_T:.1f}%/{100*lt_S:.1f}% | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) | {100*(1-abs(c['aT'])/abs(b0['aT'])):+.0f}% / {100*(1-abs(c['aS'])/abs(b0['aS'])):+.0f}% |")
zero3 = all(abs(A3[(cp,'在2010-20')]['aS']) < 0.02 and abs(A3[(cp,'在2010-20')]['aT']) < 0.02 for cp in [48,96,144])
flips = sum(1 for cp in [48,96,144] if A3[(cp,'在2010-20')]['aS'] > 0)
v3 = "broken" if (zero3 or flips >= 2) else "survived（裾限定への精錬）"
say(f"\n**A3 判定: T1 は {v3}**（在 SL 腕の符号反転 {flips}/3 CAP・≈0 判定 {zero3}）")

# ---------------- A4 プラセボ ----------------
say()
say("## A4 プラセボ（c66 は負の対照を D でしか出していない＝腕別の穴を埋める）")
def twin_vs_twin(mask_real_cols, mask_twin_cols, wn, lab, B=400):
    wm = W[wn]; nc, inv = make_cluster("day")
    SA = np.zeros((nc, 8))
    mf = dec_tw & wm[:, None] & mask_real_cols
    mt = dec_tw & wm[:, None] & mask_twin_cols
    rows = np.repeat(inv[:, None], K, 1); KF = KS.astype(float)
    fT = mf & (RS == 1); fS = mf & (RS == 0); tT = mt & (RS == 1); tS = mt & (RS == 0)
    np.add.at(SA[:, 0], rows[fT], KF[fT]); np.add.at(SA[:, 1], rows[fT], 1.0)
    np.add.at(SA[:, 2], rows[fS], KF[fS]); np.add.at(SA[:, 3], rows[fS], 1.0)
    np.add.at(SA[:, 4], rows[tT], KF[tT]); np.add.at(SA[:, 5], rows[tT], 1.0)
    np.add.at(SA[:, 6], rows[tS], KF[tS]); np.add.at(SA[:, 7], rows[tS], 1.0)
    v = stat(SA); se = boot(SA, B, rng2)
    say(f"- {lab} {wn}: 腕 TP {v[3]:+.4f} (t {v[3]/se[3]:+.2f})・腕 SL {v[4]:+.4f} (t {v[4]/se[4]:+.2f})・D {v[2]:+.4f} (t {v[2]/se[2]:+.2f})")
    return v, se
col0 = np.zeros((N, K), bool); col0[:, 0] = True
half = np.zeros((N, K), bool); half[:, :K//2] = True
pl = {}
for wn in ["在2010-20", "外2021-26H1"]:
    pl[('a', wn)] = twin_vs_twin(col0, ~col0, wn, "(a) 双子 col0 を偽実本 vs 残り 15 本（期待 0）")
for wn in ["在2010-20", "外2021-26H1"]:
    pl[('b', wn)] = twin_vs_twin(half, ~half, wn, "(b) 双子 8 vs 8（期待 0）")
bad = max(max(abs(pl[(k,w)][0][3]), abs(pl[(k,w)][0][4])) for k in 'ab' for w in ["在2010-20","外2021-26H1"])
badt = max(max(abs(pl[(k,w)][0][3]/pl[(k,w)][1][3]), abs(pl[(k,w)][0][4]/pl[(k,w)][1][4])) for k in 'ab' for w in ["在2010-20","外2021-26H1"])
v4ab = "推定量に偏り＝T1 broken" if (bad >= 0.03 and badt >= 2) else "推定量は不偏（T1 の 0.11 は推定量の人工物ではない）"
say(f"**A4(a)(b) 判定: 最大 |腕別| {bad:.4f}・最大 |t| {badt:.2f} → {v4ab}**")
# (c) 暦組成プラセボ: 偽実本 = 金曜のみ pool から・双子 = 全 pool
JS3 = JS.copy(); nfri = 0
for h in range(24):
    sel_h = (HOUR[NF] == h); ii = np.flatnonzero(jh == h)
    NFhw = NF[sel_h & (WDNF == 4)]
    if len(NFhw) == 0: continue
    lo = np.searchsorted(NFhw, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFhw, ie[ii] + SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFhw[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: continue
        JS3[i] = cand[rng2.integers(0, len(cand), K)]; nfri += 1
RS3, KS3 = simulate_k(JS3.ravel(), rep(sgn), rep(risk), rep(bb))
RS3 = RS3.reshape(N, K); KS3 = KS3.reshape(N, K)
cross3 = ((CSAT[np.minimum(JS3.ravel()+KS3.ravel(), NB-1)+1] - CSAT[JS3.ravel()+1]) > 0).reshape(N, K)
dec_tw3 = (RS3 >= 0) & ~cross3
say(f"- (c) 暦組成プラセボ: 金曜 pool に置換できた本 {nfri}/{N}・曜日一致(金) {100*(wd_utc[JS3]==4).mean():.1f}%・決着率 {100*(RS3>=0).mean():.1f}%")
for wn in ["在2010-20", "外2021-26H1"]:
    wm = W[wn]; nc, inv = make_cluster("day")
    SA = np.zeros((nc, 8)); rows = np.repeat(inv[:, None], K, 1)
    mf = dec_tw3 & wm[:, None]; mt = dec_tw & wm[:, None]
    K3 = KS3.astype(float); KF = KS.astype(float)
    for col, msk, arr, rsx, armv in [(0, mf, K3, RS3, 1), (2, mf, K3, RS3, 0), (4, mt, KF, RS, 1), (6, mt, KF, RS, 0)]:
        sel = msk & (rsx == armv)
        np.add.at(SA[:, col], rows[sel], arr[sel]); np.add.at(SA[:, col+1], rows[sel], 1.0)
    v = stat(SA); se = boot(SA, 300, rng2)
    say(f"  - {wn}: 偽実本(金曜) vs 双子(全) → 腕 TP {v[3]:+.4f} (t {v[3]/se[3]:+.2f})・腕 SL {v[4]:+.4f} (t {v[4]/se[4]:+.2f})（|0.11| と比べる）")

# ---------------- A5 se の頑健性 ----------------
say()
say("## A5 se の頑健性（日クラスタ → 暦月ブロック → 年クラスタ）")
say("| 窓 | クラスタ | n cluster | 腕 SL (t) | 腕 TP (t) | D (t) |")
say("|---|---|---|---|---|---|")
A5 = {}
for wn in ["在2010-20", "外2021-26H1"]:
    wm = W[wn]
    for cl in ["day", "mon", "year"]:
        nc, _ = make_cluster(cl)
        c = cellv(wm & dec & hold1, HR, dec_tw & wm[:, None], KS.astype(float), B=600 if cl!="year" else 2000, cl=cl)
        A5[(wn, cl)] = c
        say(f"| {wn} | {cl} | {nc} | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['D']:+.4f} ({c['D']/c['seD']:+.2f}) |")
tmon = abs(A5[("在2010-20","mon")]['aS']/A5[("在2010-20","mon")]['seS'])
v5 = "broken（t<2）" if tmon < 2 else ("weakened（t<3＝c66 の t −6.4 は過大）" if tmon < 3 else "survived")
say(f"\n**A5 判定: T1 の有意性は {v5}**（在 SL 腕 月ブロック |t| {tmon:.2f} vs c66 日クラスタ 6.39）")

# ---------------- A6 T2 の算術 ----------------
say()
say("## A6 T2 の算術（mean hold ∝ 1/σ² ＋ c32 のボラ +5〜7%）")
ret = np.zeros(NB); ret[1:] = np.log(np.maximum(C[1:], 1e-9) / np.maximum(C[:-1], 1e-9))
ret[FLAT] = 0.0
CR2 = np.concatenate([[0.0], np.cumsum(ret**2)])
def sig_pre(j, w=12):
    a = np.maximum(j - w, 0)
    ss = CR2[j + 1] - CR2[a + 1]
    nn = np.maximum(CNF[j + 1] - CNF[a + 1], 1)
    return np.sqrt(ss / nn)
sp_real = sig_pre(ie); sp_tw = sig_pre(JSf).reshape(N, K)
say("| 窓 | σ_pre 実 (中央値) | 双子 | Δ = log(実/双) | 予測 腕別 = −2Δ | 観測 腕別 TP/SL | 観測/予測 TP/SL |")
say("|---|---|---|---|---|---|---|")
A6 = {}
for wn, wm in W.items():
    mr = wm & dec & hold1; mt = dec_tw & wm[:, None]
    sr = np.median(sp_real[mr]); st_ = np.median(sp_tw[mt])
    dlt = np.log(sp_real[mr].mean() / sp_tw[mt].mean())
    pred = -2 * dlt
    b0 = base[wn]
    A6[wn] = (dlt, pred, b0['aT'], b0['aS'])
    say(f"| {wn} | {sr:.6f} | {st_:.6f} | {dlt:+.4f} | {pred:+.4f} | {b0['aT']:+.4f}/{b0['aS']:+.4f} | {b0['aT']/pred:.2f}/{b0['aS']/pred:.2f} |")
r_in = [A6["在2010-20"][2]/A6["在2010-20"][1], A6["在2010-20"][3]/A6["在2010-20"][1]]
v6a = "broken" if (min(r_in) < 0.5 or max(r_in) > 2.0) else "survived"
say(f"\n**A6(i) 判定: T2 の「量が合う」は {v6a}**（在 観測/予測 TP {r_in[0]:.2f}・SL {r_in[1]:.2f}・規則 [0.5, 2.0]）")
# 弾性の直接推定（双子のみ・σ_pre 十分位 × b 三分位 × 腕）
qb = np.quantile(bb[dec], [1/3, 2/3])
bt = np.digitize(bb, qb)
say("\n- 弾性の直接推定（双子のみ・理論 −2）: log(mean hold) を log σ̄ に回帰（σ_pre 十分位ビン・b 三分位内・腕別）")
slopes = []
for armv, armn in [(1, "TP"), (0, "SL")]:
    for btv in range(3):
        mt = dec_tw & (RS == armv) & (bt[:, None] == btv)
        if mt.sum() < 2000: continue
        s_ = sp_tw[mt]; k_ = KS[mt].astype(float)
        qs = np.quantile(s_, np.linspace(0, 1, 11)); binx = np.clip(np.digitize(s_, qs[1:-1]), 0, 9)
        xs = np.array([np.log(s_[binx == q].mean()) for q in range(10)])
        ys = np.array([np.log(k_[binx == q].mean()) for q in range(10)])
        A = np.vstack([np.ones(10), xs]).T
        beta, *_ = np.linalg.lstsq(A, ys, rcond=None)
        res = ys - A @ beta; s2 = (res**2).sum() / 8
        seb = np.sqrt(s2 * np.linalg.inv(A.T @ A)[1, 1])
        slopes.append(beta[1])
        say(f"  - {armn} 腕・b 三分位 {btv} (b̄ {bb[bt==btv].mean():.2f}・n {int(mt.sum())}): 弾性 {beta[1]:+.3f} ± {seb:.3f}・95%CI [{beta[1]-1.96*seb:+.3f}, {beta[1]+1.96*seb:+.3f}]・−2 を含む {abs(beta[1]+2) <= 1.96*seb}")
v6b = f"弾性の中央値 {np.median(slopes):+.2f}（理論 −2）"
say(f"**A6(ii): {v6b}**")

# ---------------- A7 コスト倍 ----------------
say()
say("## A7 コスト倍（ft ×2 ＝悲観側・ft ×0 ＝楽観側・両群を同じ simulate_k で再導出＝完全対称）")
say("| ft | 窓 | 実 n TP/SL | 腕 TP (t) | 腕 SL (t) | 縮み TP/SL |")
say("|---|---|---|---|---|---|")
A7 = {}
for lab, ftv in [("×2 (0.2)", 2*FT), ("×0 (0.0)", 0.0)]:
    Rr, Kr = simulate_k(ie, sgn, risk, bb, ft=ftv)
    Rt, Kt = simulate_k(JS.ravel(), rep(sgn), rep(risk), rep(bb), ft=ftv)
    Rt = Rt.reshape(N, K); Kt = Kt.reshape(N, K)
    crx = ((CSAT[np.minimum(JS.ravel()+Kt.ravel(), NB-1)+1] - CSAT[JS.ravel()+1]) > 0).reshape(N, K)
    dtx = (Rt >= 0) & ~crx
    sat_r = (CSAT[np.minimum(ie+Kr, NB-1)+1] - CSAT[ie+1]) > 0
    drx = (Rr >= 0) & ~sat_r & tail_ok
    tp_x = (Rr == 1)
    RS_s, KS_s, dec_s, tp_s = RS, KS, dec_tw, tp
    RS, KS, dec_tw, tp = Rt, Kt, dtx, tp_x
    for wn in ["在2010-20", "外2021-26H1"]:
        wm = W[wn]
        c = cellv(wm & drx, Kr.astype(float), dtx & wm[:, None], Kt.astype(float), B=300)
        A7[(lab, wn)] = c; b0 = base[wn]
        say(f"| {lab} | {wn} | {c['nT']}/{c['nS']} | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) | {100*(1-abs(c['aT'])/abs(b0['aT'])):+.0f}% / {100*(1-abs(c['aS'])/abs(b0['aS'])):+.0f}% |")
    RS, KS, dec_tw, tp = RS_s, KS_s, dec_s, tp_s
sh7 = [1-abs(A7[(l,w)][k])/abs(base[w][k]) for l in ["×2 (0.2)", "×0 (0.0)"] for w in ["在2010-20","外2021-26H1"] for k in ['aT','aS']]
v7 = "broken" if min(sh7) >= 0.5 else "survived"
say(f"\n**A7 判定: T1 は {v7}**（最小縮み {100*min(sh7):+.0f}%・最大 {100*max(sh7):+.0f}%）")

# ---------------- A8 年別 ----------------
say()
say("## A8 暦年別（レジーム部分集合・T1 の「全窓で同符号」）")
rowsy = []
for y in range(2010, 2027):
    wm = (yr == y)
    if (wm & dec & hold1).sum() < 150: continue
    c = cellv(wm & dec & hold1, HR, dec_tw & wm[:, None], KS.astype(float), B=200)
    rowsy.append((y, c['aT'], c['aT']/c['seT'], c['aS'], c['aS']/c['seS']))
say("| 年 | 腕 TP (t) | 腕 SL (t) |")
say("|---|---|---|")
for y, aT, tT, aS, tS in rowsy: say(f"| {y} | {aT:+.4f} ({tT:+.2f}) | {aS:+.4f} ({tS:+.2f}) |")
negT = sum(1 for r in rowsy if r[1] < 0); negS = sum(1 for r in rowsy if r[3] < 0); ny = len(rowsy)
fT_ = negT/ny; fS_ = negS/ny
v8 = "broken" if min(fT_, fS_) < 0.6 else ("survived" if min(fT_, fS_) >= 0.8 else "weakened")
say(f"\n**A8 判定: T1 の普遍性は {v8}**（負の年 TP {negT}/{ny} = {fT_:.2f}・SL {negS}/{ny} = {fS_:.2f}）")

# ---------------- A9 b 依存 ----------------
say()
say("## A9 b 依存 vs 「方向を問わないボラ状態」機構")
say("| 窓 | b 三分位 | b̄ | 実 n TP/SL | 腕 TP 足時計 (t) | 腕 SL 足時計 (t) | 腕 TP active (t) | 腕 SL active (t) |")
say("|---|---|---|---|---|---|---|---|")
A9 = {}
for wn, wm in W.items():
    for btv, lab in [(0, "下"), (1, "中"), (2, "上")]:
        mb = (bt == btv)
        c = cellv(wm & dec & hold1 & mb, HR, dec_tw & (wm & mb)[:, None], KS.astype(float), B=300)
        ca = cellv(wm & dec & hold1 & mb, act_real, dec_tw & (wm & mb)[:, None], act_tw, B=300)
        A9[(wn, btv)] = (c, ca)
        say(f"| {wn} | {lab} | {bb[wm&dec&hold1&mb].mean():.2f} | {c['nT']}/{c['nS']} | {c['aT']:+.4f} ({c['aT']/c['seT']:+.2f}) | {c['aS']:+.4f} ({c['aS']/c['seS']:+.2f}) | {ca['aT']:+.4f} ({ca['aT']/ca['seT']:+.2f}) | {ca['aS']:+.4f} ({ca['aS']/ca['seS']:+.2f}) |")
lowTP = [A9[(w, 0)][0]['aT'] for w in W]
tlow = A9[("在2010-20", 0)][0]['aT'] / A9[("在2010-20", 0)][0]['seT']
v9i = "broken（効果は普遍でなく b 依存）" if (all(x > 0 for x in lowTP) and abs(tlow) >= 2) else "survived"
gapT = A9[("在2010-20",2)][0]['aT'] - A9[("在2010-20",0)][0]['aT']
gapS = A9[("在2010-20",2)][0]['aS'] - A9[("在2010-20",0)][0]['aS']
se_gap = np.sqrt(A9[("在2010-20",2)][0]['seT']**2 + A9[("在2010-20",0)][0]['seT']**2)
v9ii = "機構 broken／不完全" if (abs(gapT) > 0.10 and abs(gapT/se_gap) >= 2) else "機構 survived"
say(f"\n**A9(i) 判定: T1 の宣言形「両腕・全窓・全規約で同符号」は {v9i}**（b 下三分位 TP 腕 在 {lowTP[0]:+.4f} (t {tlow:+.2f})／外 {lowTP[1]:+.4f}／近年 {lowTP[2]:+.4f}）")
say(f"**A9(ii) 判定: 「方向を問わないボラ状態」は {v9ii}**（在 b 上−下 TP 腕差 {gapT:+.4f} ± {se_gap:.4f}・t {gapT/se_gap:+.2f}・SL 腕差 {gapS:+.4f}）")

# ---------------- T5 ρ_twin ≈ ρ_RW ----------------
say()
say("## T5 ρ_twin ≈ ρ_RW の整合テスト（c66 の道具較正の主張）— b 三分位内でも成り立つか")
def rho_rw_m(mask):
    a = 1 - tr["ft"].to_numpy()[mask]; Bv = (bb + tr["ft"].to_numpy())[mask]
    pT = a/(a+Bv); pS = Bv/(a+Bv)
    eT = Bv*(2*a+Bv)/3; eS = a*(2*Bv+a)/3
    return (np.sum(pT*eT)/np.sum(pT)) / (np.sum(pS*eS)/np.sum(pS))
say("| 窓 | b 三分位 | ρ_twin | ρ_RW | log 差 |")
say("|---|---|---|---|---|")
t5max = 0.0
for wn, wm in W.items():
    for btv, lab in [(-1, "全"), (0, "下"), (1, "中"), (2, "上")]:
        mb = np.ones(N, bool) if btv < 0 else (bt == btv)
        m = wm & dec & hold1 & mb
        mt = dec_tw & (wm & mb)[:, None]
        if mt.sum() < 500: continue
        rt_ = (KS[mt&(RS==1)].mean()) / (KS[mt&(RS==0)].mean())
        rw_ = rho_rw_m(m); dl = np.log(rt_/rw_)
        t5max = max(t5max, abs(dl))
        say(f"| {wn} | {lab} | {rt_:.3f} | {rw_:.3f} | {dl:+.4f} |")
say(f"\n**T5 判定: 最大 |log 差| {t5max:.4f}** → {'survived（c66 の ±0.03 は全で成立・部分集合でも ' + ('成立' if t5max<=0.05 else '最大 %.3f まで広がる' % t5max) + '）' if t5max<=0.05 else 'c66 の ±0.03 は全体のみ・b 部分集合では最大 %.3f に広がる（主張の射程を狭める）' % t5max}")

say()
say(f"実行 {time.time()-t0:.1f} s・書き込み data/refute_c66_fpt.md・同 _run.log のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
open(os.path.join(DATA, "refute_c66_fpt_run.log"), "w", encoding="utf-8").write("\n".join(L) + "\n")
