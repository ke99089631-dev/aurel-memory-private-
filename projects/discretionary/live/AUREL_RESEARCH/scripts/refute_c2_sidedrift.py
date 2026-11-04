# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-05 05:15 — 02:25 [REFUTE] で自分に残した反証を潰す。
対象: 「+1R 到達後に建玉中の本の公正化ドリフト e = R* − cl_k が BUY −0.058 (t−1.86, p0.063, n1926) / SELL +0.032 (t0.91) と
      側で符号が分かれる。BUY は +1R 後にやや戻り、SELL はやや伸びる。2024-26 の側別は未計算。」
読取りのみ・発注なし・scan なし。入力は既存キャッシュ（c1 json・c4 json・refute_c2_fullpaths.npz）。書き込みは data/ のみ。

事前固定（コードを書く前に固定・以後動かさない）:
  H0: 武装（+1.0R 初到達）足 k の終値時点で建玉中の本について、価格はマルチンゲール（E[e]=0）で側に依らない。
      BUY の負は 9 窓の中の 1 セル（側 2 窓）を post-hoc に拾った選択効果。
  Q1 側×時代の格子: BUY/SELL × {2010-20, 2021-23, 2024-26, 2025-26H1} の 8 セルで e の平均・t。Bonferroni α=0.05/8。
      BUY が本物の戻りなら時代をまたいで符号が負に揃うはず。側差 e_BUY − e_SELL も時代別に出す。
  Q2 側ラベル置換: 建玉中集合の中で BUY/SELL ラベルをシャッフル（2000 回）し、側差 |e_BUY − e_SELL| と max(|t_BUY|,|t_SELL|) の帰無分布。
      観測の側差 −0.090 と max|t| 1.86 の p。
  Q3 X プラセボ: 武装閾値 X∈{0.5,0.75,1.0,1.25,1.5} で同じ e を側別に。BUY 負が X=1.0 だけなら閾値選択。Bonferroni α=0.05/10。
  Q4 ランダム足プラセボ: 武装条件なしで、保有中の足 k'（1 ≤ k' < hold）を一様に 1 本選び e' = R* − cl_k' を側別に。200 回の平均。
      BUY が同じ大きさで負なら「+1R 後」でなく「この scan の BUY 全般のドリフト（記帳/データの側非対称）」＝出口の情報ではない。
  Q5 戦略採点（使える形）: 「BUY のみ、+1R 初到達足の終値時点で建玉中なら成行で閉じる」。diff = (cl_k − s) − R0（s∈{0,0.10,0.22} USD/risk）。
      在/外/2024-26 の平均 diff・t、全 BUY 本の上位10% 合計R 残存率。研究レーンの昇格基準（在 t≥2・外 t≥1.5・残存≥90%）で採点。
  look-ahead: 「k の終値時点で建玉中」は k の終値で判明する条件（hold>k）。cl_k は k の終値。R* は将来。問題なし。
判定（事前固定）:
  broken       = Q2 側差 p > 0.05 かつ Q1 8 セルで Bonferroni 有意 0 かつ Q5(s=0.10) が在 t≥2・外 t≥1.5・残存≥90% のどれかを欠く。
  survived     = Q2 側差 p < 0.05 かつ Q1 の BUY 2024-26 が Bonferroni 有意に負 かつ Q5(s=0.10) が 3 条件すべて満たす。
  それ以外     = inconclusive。
出力: data/refute_c2_sidedrift.md
"""
import os, sys, math, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
from refute_c2_breakeven import load, tstat, top_ret, NPZ, DATA

OUT = os.path.join(DATA, "refute_c2_sidedrift.md")
X0 = 1.0
XGRID = (0.5, 0.75, 1.0, 1.25, 1.5)
NPERM = 2000
NRAND = 200
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def main():
    t0 = time.time()
    df, J, FT = load()
    n = len(df); R0 = df.R.to_numpy(); risk = df.risk.to_numpy(); ft = df.ft.to_numpy()
    side = df.side.to_numpy(); year = df.year.to_numpy(); hold = df.hold.to_numpy(); er = df.exit_reason.to_numpy()
    z = np.load(NPZ); hiR, loR, clR, off = z["hiR"], z["loR"], z["clR"], z["off"]
    assert len(off) - 1 == n
    Rstar = R0 + np.where((er == "SL") | (er == "TP"), ft, 0.0)
    isB = side == "BUY"; isS = side == "SELL"
    say("# AUREL [REFUTE] 2026-11-05 — 02:25 の残存反証（武装後ドリフト e の BUY/SELL 非対称）を潰す  入力 %d 本  %s" % (n, time.strftime("%Y-%m-%d %H:%M")))
    say("FEED_TOL=%.2f USD、ft 平均 %.4fR。path は切断なし（refute_c2_fullpaths.npz）。BUY %d / SELL %d。" % (FT, ft.mean(), isB.sum(), isS.sum()))
    say()
    eras = (("2010-20", year <= 2020), ("2021-23", (year >= 2021) & (year <= 2023)), ("2024-26", year >= 2024), ("2025-26H1", year >= 2025))

    def arm_idx(X):
        ka = np.full(n, -1)
        for i in range(n):
            a = np.nonzero(hiR[off[i]:off[i + 1]] >= X)[0]
            if len(a): ka[i] = int(a[0])
        return ka

    def e_for(ka):
        armed = ka >= 0
        open_k = armed & (hold > ka)
        clk = np.full(n, np.nan)
        idx = np.nonzero(open_k)[0]
        clk[idx] = clR[off[idx] + ka[idx]]
        return open_k, clk, Rstar - clk

    ka = arm_idx(X0)
    open_k, clk, e = e_for(ka)
    say("再現: 武装 %d 本・建玉中 %d 本。e BUY %+.4f (t%+.2f, n%d) / SELL %+.4f (t%+.2f, n%d)（02:25: −0.0578 t−1.86 n1926 / +0.0321 t0.91 n1758）。" % (
        (ka >= 0).sum(), open_k.sum(), e[open_k & isB].mean(), tstat(e[open_k & isB])[0], (open_k & isB).sum(),
        e[open_k & isS].mean(), tstat(e[open_k & isS])[0], (open_k & isS).sum()))
    say()

    # ---------- Q1 ----------
    aB1 = 0.05 / 8
    say("## Q1. 側×時代の格子（建玉中 e）。Bonferroni α=%.4f" % aB1)
    say("| 時代 | BUY n / mean e / t / p | SELL n / mean e / t / p | 側差 BUY−SELL / t(Welch) |")
    say("|---|---|---|---|")
    sig1 = 0; q1 = {}
    for lab, m in eras:
        mb = m & open_k & isB; ms = m & open_k & isS
        eb, es = e[mb], e[ms]; tb, pb = tstat(eb); ts_, ps = tstat(es)
        q1[lab] = (eb.mean(), tb, pb, es.mean(), ts_, ps)
        sig1 += int(pb < aB1) + int(ps < aB1)
        # Welch
        se = math.sqrt(eb.var(ddof=1) / len(eb) + es.var(ddof=1) / len(es)); dw = eb.mean() - es.mean()
        say("| %s | %d / %+.4f / %+.2f / %.4f | %d / %+.4f / %+.2f / %.4f | %+.4f / %+.2f |" % (lab, len(eb), eb.mean(), tb, pb, len(es), es.mean(), ts_, ps, dw, dw / se))
    say("Bonferroni 有意セル: %d/8。BUY の符号: %s。" % (sig1, " ".join("%s%s" % (lab, "−" if q1[lab][0] < 0 else "+") for lab, _ in eras)))
    say()

    # ---------- Q2 ----------
    say("## Q2. 側ラベル置換（建玉中集合内で BUY/SELL を %d 回シャッフル）" % NPERM)
    idx = np.nonzero(open_k)[0]; ee = e[idx]; lab_b = isB[idx]
    obs_gap = ee[lab_b].mean() - ee[~lab_b].mean()
    obs_mt = max(abs(tstat(ee[lab_b])[0]), abs(tstat(ee[~lab_b])[0]))
    rng = np.random.default_rng(20261105)
    gaps = np.empty(NPERM); mts = np.empty(NPERM)
    nb_ = lab_b.sum()
    for r in range(NPERM):
        p = rng.permutation(len(ee)); b = np.zeros(len(ee), bool); b[p[:nb_]] = True
        gaps[r] = ee[b].mean() - ee[~b].mean()
        mts[r] = max(abs(tstat(ee[b])[0]), abs(tstat(ee[~b])[0]))
    p_gap = np.mean(np.abs(gaps) >= abs(obs_gap)); p_mt = np.mean(mts >= obs_mt)
    say("観測 側差 %+.4f → 両側 p **%.3f**（帰無 |側差| 中央値 %.4f・95%%点 %.4f）。観測 max|t| %.2f → p **%.3f**（帰無 95%%点 %.2f）。" % (
        obs_gap, p_gap, np.median(np.abs(gaps)), np.percentile(np.abs(gaps), 95), obs_mt, p_mt, np.percentile(mts, 95)))
    # 2024-26 だけで同じ置換
    idx2 = np.nonzero(open_k & (year >= 2024))[0]; ee2 = e[idx2]; lb2 = isB[idx2]
    og2 = ee2[lb2].mean() - ee2[~lb2].mean(); g2 = np.empty(NPERM); nb2 = lb2.sum()
    for r in range(NPERM):
        p = rng.permutation(len(ee2)); b = np.zeros(len(ee2), bool); b[p[:nb2]] = True
        g2[r] = ee2[b].mean() - ee2[~b].mean()
    p_gap2 = np.mean(np.abs(g2) >= abs(og2))
    say("2024-26 のみ: 側差 %+.4f（BUY n%d / SELL n%d）→ 両側 p %.3f。" % (og2, nb2, len(ee2) - nb2, p_gap2))
    say()

    # ---------- Q3 ----------
    aB3 = 0.05 / 10
    say("## Q3. X プラセボ（武装閾値を動かす）。Bonferroni α=%.4f" % aB3)
    say("| X | 建玉中 n | BUY mean e / t / p | SELL mean e / t / p | 側差 | 2024-26 BUY e / t | 2024-26 SELL e / t |")
    say("|---|---|---|---|---|---|---|")
    sig3 = 0
    for X in XGRID:
        kx = arm_idx(X); ox, cx, ex = e_for(kx)
        eb, es = ex[ox & isB], ex[ox & isS]; tb, pb = tstat(eb); ts_, ps = tstat(es)
        sig3 += int(pb < aB3) + int(ps < aB3)
        m24 = year >= 2024
        say("| %.2f | %d | %+.4f / %+.2f / %.4f | %+.4f / %+.2f / %.4f | %+.4f | %+.4f / %+.2f | %+.4f / %+.2f |" % (
            X, ox.sum(), eb.mean(), tb, pb, es.mean(), ts_, ps, eb.mean() - es.mean(),
            ex[ox & isB & m24].mean(), tstat(ex[ox & isB & m24])[0], ex[ox & isS & m24].mean(), tstat(ex[ox & isS & m24])[0]))
    say("Bonferroni 有意セル: %d/10。" % sig3)
    say()

    # ---------- Q4 ----------
    say("## Q4. ランダム足プラセボ（武装条件なし・保有中の足 k' を一様に 1 本・%d 回）: e' = R* − cl_k' を側別に" % NRAND)
    elig = hold >= 2  # k' ∈ [1, hold-1] が存在
    eb_r = np.empty(NRAND); es_r = np.empty(NRAND); eb24 = np.empty(NRAND); es24 = np.empty(NRAND); tb_r = np.empty(NRAND)
    ie = np.nonzero(elig)[0]
    for r in range(NRAND):
        kp = rng.integers(1, hold[ie])  # [1, hold-1]
        clp = clR[off[ie] + kp]; ep = Rstar[ie] - clp
        sb = isB[ie]; m24 = year[ie] >= 2024
        eb_r[r] = ep[sb].mean(); es_r[r] = ep[~sb].mean(); tb_r[r] = tstat(ep[sb])[0]
        eb24[r] = ep[sb & m24].mean(); es24[r] = ep[~sb & m24].mean()
    say("対象 %d 本（hold≥2）。BUY e' 平均 %+.4f（200 回の SD %.4f・t 平均 %+.2f）／SELL %+.4f（SD %.4f）。側差 %+.4f。" % (
        elig.sum(), eb_r.mean(), eb_r.std(), tb_r.mean(), es_r.mean(), es_r.std(), eb_r.mean() - es_r.mean()))
    say("2024-26: BUY e' %+.4f ／ SELL %+.4f ／ 側差 %+.4f。" % (eb24.mean(), es24.mean(), eb24.mean() - es24.mean()))
    say("（武装後 BUY −0.058 と同程度で負なら「+1R 後」固有でなく scan の BUY 全般のドリフト。≈0 なら武装後だけの現象＝Q1/Q2 で判定。）")
    # 全足プーリング版（分散を落とす）: 各本の保有中全足 k'=1..hold-1 の e' を本ごとに平均してから側平均
    eb_all = []; es_all = []
    for i in ie:
        ks = clR[off[i] + 1: off[i] + hold[i]]
        if len(ks) == 0: continue
        v = (Rstar[i] - ks).mean()
        (eb_all if isB[i] else es_all).append(v)
    eb_all = np.array(eb_all); es_all = np.array(es_all)
    say("本ごとの全保有足平均 e'（本単位 t）: BUY %+.4f (t%+.2f, n%d) ／ SELL %+.4f (t%+.2f, n%d)。" % (
        eb_all.mean(), tstat(eb_all)[0], len(eb_all), es_all.mean(), tstat(es_all)[0], len(es_all)))
    say()
    # ---- Q4' 修正（初回実行の結果を見てから追加・理由を明記）----
    # 上の Q4 は欠陥: k' を [1, hold−1] から一様に選ぶと、本ごとの重みが 1/(hold−1) になり hold（将来の決着時刻）に依存する。
    # 直後に SL で決着する本（hold 小・e' 負）が重く数えられ、マルチンゲールでも e' が機械的に負に出る（BUY/SELL 両側で −0.01〜−0.07）。
    # 正しい母集団は「固定の k' で、k' の終値時点で建玉中（hold>k'）」の本を等重み: 条件は F_k' 可測で E[e'|open]=0 が成り立つ。
    # 主検定の e（k=+1R 初到達足・停止時刻、hold>k）は本ごと等重みなのでこの欠陥は無い。判定には Q4' を使う。
    say("### Q4'. 修正: 固定 k'∈{1,2,3,6,12,24,48}・hold>k' の本を等重み（F_k' 可測・look-ahead なし）")
    say("| k' | 建玉中 n | BUY e' / t | SELL e' / t | 側差 | 2024-26 BUY e' / t | 2024-26 SELL e' / t |")
    say("|---|---|---|---|---|---|---|")
    q4p = {}
    for kq in (1, 2, 3, 6, 12, 24, 48):
        ok_ = hold > kq; ii = np.nonzero(ok_)[0]
        ep = Rstar[ii] - clR[off[ii] + kq]; sb = isB[ii]; m24 = year[ii] >= 2024
        q4p[kq] = (ep[sb].mean(), ep[~sb].mean())
        say("| %d | %d | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f | %+.4f / %+.2f | %+.4f / %+.2f |" % (
            kq, ok_.sum(), ep[sb].mean(), tstat(ep[sb])[0], ep[~sb].mean(), tstat(ep[~sb])[0], ep[sb].mean() - ep[~sb].mean(),
            ep[sb & m24].mean(), tstat(ep[sb & m24])[0], ep[~sb & m24].mean(), tstat(ep[~sb & m24])[0]))
    say("（固定 k' で BUY e' ≈0 かつ側差 ≈0 なら、scan 全般に BUY ドリフトは無く、武装後 BUY −0.058 は武装集合固有＝Q1/Q2 で判定。）")
    say()

    # ---------- Q5 ----------
    say("## Q5. 戦略採点: BUY のみ、+1R 初到達足の終値時点で建玉中なら成行で閉じる（diff = cl_k − s − R0、s は USD/risk）")
    say("| s USD | 在 diff / t（全 BUY 本）| 外 diff / t | 2024-26 diff / t | 閉じた本 diff/本 | 上位10% 残存（全 BUY） | 在 残存 | 外 残存 |")
    say("|---|---|---|---|---|---|---|---|")
    q5 = {}
    for s in (0.0, 0.10, 0.22):
        R1 = R0.copy(); sel = open_k & isB
        R1[sel] = clk[sel] - s / risk[sel]
        d = R1 - R0
        mi = isB & (year <= 2020); mo = isB & (year >= 2021); m24 = isB & (year >= 2024)
        q5[s] = (d[mi].mean(), tstat(d[mi])[0], d[mo].mean(), tstat(d[mo])[0], d[m24].mean(), tstat(d[m24])[0],
                 top_ret(R0[isB], R1[isB]), top_ret(R0[mi], R1[mi]), top_ret(R0[mo], R1[mo]))
        say("| %.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f | %.0f%% | %.0f%% | %.0f%% |" % (
            s, *q5[s][:6], d[sel].mean(), *q5[s][6:]))
    say("（閉じた本 n=%d／全 BUY %d。原型の BUY 上位10%% 合計R と、閉じた後の合計R の比。）" % ((open_k & isB).sum(), isB.sum()))
    say()

    # ---------- 判定 ----------
    say("## 判定（事前固定の規則）")
    s10 = q5[0.10]
    q5ok = (s10[1] >= 2.0) and (s10[3] >= 1.5) and (s10[7] >= 90) and (s10[8] >= 90)
    buy24_sig = q1["2024-26"][0] < 0 and q1["2024-26"][2] < aB1
    say("- Q1 Bonferroni 有意セル %d/8・BUY 2024-26 有意負 %s" % (sig1, buy24_sig))
    say("- Q2 側差 置換 p %.3f（2024-26 のみ %.3f）" % (p_gap, p_gap2))
    say("- Q3 X 格子 有意セル %d/10" % sig3)
    say("- Q4 ランダム足（無効・hold 重み付きの look-ahead）BUY e' %+.4f / SELL %+.4f；**Q4' 固定 k'=6** BUY %+.4f / SELL %+.4f（武装後 BUY %+.4f / SELL %+.4f）" % (
        eb_r.mean(), es_r.mean(), q4p[6][0], q4p[6][1], e[open_k & isB].mean(), e[open_k & isS].mean()))
    say("- Q5 s=0.10: 在 t %+.2f（≥2）・外 t %+.2f（≥1.5）・残存 在 %.0f%%／外 %.0f%%（≥90）→ %s" % (s10[1], s10[3], s10[7], s10[8], "PASS" if q5ok else "FAIL"))
    if p_gap > 0.05 and sig1 == 0 and not q5ok:
        v = "broken"
    elif p_gap < 0.05 and buy24_sig and q5ok:
        v = "survived"
    else:
        v = "inconclusive"
    say("- 機械判定: **%s**（%.0fs）" % (v, time.time() - t0))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
