# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-05 08:15 — 05:20 [REFUTE] で自分に残した反証を潰す。
対象（05:20 末尾「自分の結論への・残すもの」）:
  「武装（+X 初到達）足 k の終値時点で建玉中の本の公正化ドリフト e = R* − cl_k について、BUY の符号が
   4 時代×5 閾値で全部負（SELL は X≥0.75 で全部正）という“向きの一貫性”は残る。
   もし本物なら 金の上昇スパイクは戻り、下落スパイクは続く という側の非対称仮説。」
読取りのみ・発注なし・scan なし・M5 読込なし。入力は既存キャッシュ（c1 json・c4 json・refute_c2_fullpaths.npz）。
書き込みは data/refute_c2_sidesign.md のみ。

事前固定（コードを書く前に固定・以後動かさない）:
  H0: e の分布は側（BUY/SELL）に依らない。「符号が揃う」は、入れ子の X 格子と重なる時代窓の中で
      post-hoc に数えた一致であり、側ラベルをでたらめに振っても同程度に揃う。
  Q1 格子の実測: 4 時代 {2010-20, 2021-23, 2024-26, 2025-26H1} × 5 閾値 X∈{0.5,0.75,1.0,1.25,1.5} × 2 側 = 40 セルの
      mean e / t。05:20 の主張「BUY 20/20 が負・SELL X≥0.75 16/16 が正」が実測で成り立つかをまず数える
      （05:20 は時代×X の全格子を出していない。2024-26 の X=0.5/0.75 は 05:20 の表で既に BUY 正）。
  Q2 同時符号パターンの置換（主検定）: 側ラベルを時代層（≤2020 / 2021-23 / 2024 / ≥2025）内でシャッフル（2000 回）。
      武装集合・e は側に依らない量なので固定、ラベルだけ振り直す。統計量:
        S_neg  = BUY セルで e<0 の数（/20）
        S_pos  = SELL セルで e>0 の数（/20）
        S_gap  = 側差 e_BUY−e_SELL<0 のセル数（/20）
        S_maxt = 40 セルの max|t|（格子全体の family-wise 補正）
        S_mint = BUY セルの min t（最も負のセル）
      p = 帰無分布で観測以上（S_mint は以下）が出る割合。
  Q3 別分割: 側差（X=1.0 と X=1.25）を 偶数年/奇数年、4 年刻み {2010-13, 2014-17, 2018-21, 2022-26} の 6 分割で。
      符号が負に揃う数（/6）と二項 p。
  Q4 レジーム部分集合（X=1.0・建玉中 e・側別）: atr/risk 四分位（建玉足で確定・look-ahead なし）4×2 と
      JST 時間帯 {7-12, 13-20, 21-6} 3×2 = 14 セル。Bonferroni α=0.05/14。BUY 負の有意セル数。
  Q5 機械チェック: (a) 建玉中集合の決着種別（SL/TP/TIME）割合を側別に。(b) e の公正化前（R − cl_k）と
      公正化後（R* − cl_k）で側差が変わるか（ft は本ごと同一なので変わらないはず）。(c) 保有時間（hold−k）の側差。
      側で保有が違えば、ドリフト以外（時間切れの比率）で e が動く。
  Q6 コスト倍: 05:20 Q5 の戦略形「BUY のみ +1R 初到達足の終値時点で建玉中なら成行で閉じる」を s∈{0.20, 0.44} USD
      （05:20 の 0.10/0.22 の倍）で在/外/2024-26 の diff・t（参考。05:20 で s=0.10 でも FAIL 済）。
  look-ahead: 武装は足 k の高値、条件 hold>k は k 終値で判明、cl_k は k 終値。atr/risk・jh は建玉足。R* は将来＝検定量。
  survivorship: closed 全本（TIME 含む）、path 切断なし。
判定（事前固定）:
  broken       = Q2 p(S_neg) > 0.05 かつ Q2 p(S_maxt) > 0.05 かつ Q4 で BUY 負の Bonferroni 有意セル 0。
  survived     = Q2 p(S_neg) < 0.01 かつ p(S_maxt) < 0.05 かつ Q3 側差負 ≥5/6 かつ Q1 で 2024-26 BUY が 5/5 負。
  それ以外     = inconclusive。
出力: data/refute_c2_sidesign.md
"""
import os, sys, math, time, json
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
from refute_c2_breakeven import load, tstat, top_ret, NPZ, DATA, C4

OUT = os.path.join(DATA, "refute_c2_sidesign.md")
XGRID = (0.5, 0.75, 1.0, 1.25, 1.5)
NPERM = 2000
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def binom_p_ge(k, n, p=0.5):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def main():
    t0 = time.time()
    df, J, FT = load()
    c4 = json.load(open(C4, encoding="utf-8"))
    aux = {t["entry_time"]: t for t in c4["trades"]}
    df["atr"] = [aux[t]["atr"] if t in aux else np.nan for t in df.entry_time]
    n = len(df); R0 = df.R.to_numpy(); risk = df.risk.to_numpy(); ft = df.ft.to_numpy()
    side = df.side.to_numpy(); year = df.year.to_numpy(); hold = df.hold.to_numpy(); er = df.exit_reason.to_numpy()
    jh = df.jh.to_numpy(); atr = df.atr.to_numpy()
    z = np.load(NPZ); hiR, loR, clR, off = z["hiR"], z["loR"], z["clR"], z["off"]
    assert len(off) - 1 == n
    Rstar = R0 + np.where((er == "SL") | (er == "TP"), ft, 0.0)
    isB = side == "BUY"
    say("# AUREL [REFUTE] 2026-11-05 — 05:20 の残存反証（BUY e 負・SELL e 正の“向きの一貫性”）を潰す  入力 %d 本  %s" % (n, time.strftime("%Y-%m-%d %H:%M")))
    say("FEED_TOL=%.2f USD、ft 平均 %.4fR。path 切断なし。BUY %d / SELL %d。atr 結合 %d/%d。" % (FT, ft.mean(), isB.sum(), (~isB).sum(), np.isfinite(atr).sum(), n))
    say()
    eras = (("2010-20", year <= 2020), ("2021-23", (year >= 2021) & (year <= 2023)), ("2024-26", year >= 2024), ("2025-26H1", year >= 2025))
    strata = np.where(year <= 2020, 0, np.where(year <= 2023, 1, np.where(year == 2024, 2, 3)))

    def arm_idx(X):
        ka = np.full(n, -1)
        for i in range(n):
            a = np.nonzero(hiR[off[i]:off[i + 1]] >= X)[0]
            if len(a): ka[i] = int(a[0])
        return ka

    cells = {}  # X -> (open_mask, e, clk)
    for X in XGRID:
        ka = arm_idx(X); open_k = (ka >= 0) & (hold > ka)
        clk = np.full(n, np.nan); idx = np.nonzero(open_k)[0]; clk[idx] = clR[off[idx] + ka[idx]]
        cells[X] = (open_k, Rstar - clk, clk, ka)

    def cell_stats(lab_b):
        """40 セルの (mean, t) を返す: dict[(era, X, side)]"""
        out = {}
        for X in XGRID:
            ok, e, _, _ = cells[X]
            for lab, m in eras:
                for sd, mm in (("BUY", lab_b), ("SELL", ~lab_b)):
                    v = e[ok & m & mm]
                    out[(lab, X, sd)] = (v.mean(), tstat(v)[0], len(v))
        return out

    def pattern(st):
        s_neg = sum(1 for (lab, X, sd), (mu, t, k) in st.items() if sd == "BUY" and mu < 0)
        s_pos = sum(1 for (lab, X, sd), (mu, t, k) in st.items() if sd == "SELL" and mu > 0)
        s_gap = sum(1 for lab, _ in eras for X in XGRID if st[(lab, X, "BUY")][0] - st[(lab, X, "SELL")][0] < 0)
        s_maxt = max(abs(t) for (mu, t, k) in st.values())
        s_mint = min(t for (lab, X, sd), (mu, t, k) in st.items() if sd == "BUY")
        return s_neg, s_pos, s_gap, s_maxt, s_mint

    # ---------- Q1 ----------
    say("## Q1. 4 時代 × 5 X × 2 側 = 40 セルの実測（建玉中 e: mean / t / n）")
    say("| 時代 | X | BUY mean / t / n | SELL mean / t / n | 側差 |")
    say("|---|---|---|---|---|")
    obs = cell_stats(isB)
    for lab, _ in eras:
        for X in XGRID:
            b = obs[(lab, X, "BUY")]; s = obs[(lab, X, "SELL")]
            say("| %s | %.2f | %+.4f / %+.2f / %d | %+.4f / %+.2f / %d | %+.4f |" % (lab, X, *b, *s, b[0] - s[0]))
    o_neg, o_pos, o_gap, o_maxt, o_mint = pattern(obs)
    pos_hi = sum(1 for (lab, X, sd), (mu, t, k) in obs.items() if sd == "SELL" and X >= 0.75 and mu > 0)
    buy24 = sum(1 for X in XGRID if obs[("2024-26", X, "BUY")][0] < 0)
    say("観測: BUY 負 **%d/20**・SELL 正 **%d/20**（X≥0.75 では %d/16）・側差負 **%d/20**・max|t| %.2f・BUY min t %.2f。2024-26 BUY 負 %d/5。" % (
        o_neg, o_pos, pos_hi, o_gap, o_maxt, o_mint, buy24))
    say("（05:20 の主張「BUY 20/20 負・SELL X≥0.75 16/16 正」との照合。）")
    say()

    # ---------- Q2 ----------
    say("## Q2. 同時符号パターンの置換（側ラベルを時代層内で %d 回シャッフル・武装集合と e は固定）" % NPERM)
    rng = np.random.default_rng(20261105)
    S = np.empty((NPERM, 5))
    for r in range(NPERM):
        lb = isB.copy()
        for g in range(4):
            ii = np.nonzero(strata == g)[0]; lb[ii] = isB[ii][rng.permutation(len(ii))]
        S[r] = pattern(cell_stats(lb))
    p_neg = np.mean(S[:, 0] >= o_neg); p_pos = np.mean(S[:, 1] >= o_pos); p_gap = np.mean(S[:, 2] >= o_gap)
    p_maxt = np.mean(S[:, 3] >= o_maxt); p_mint = np.mean(S[:, 4] <= o_mint)
    # 「どちらかの側が 20/20 で揃う」も数える（側の選び方の自由度）
    p_any20 = np.mean((S[:, 0] >= o_neg) | ((20 - S[:, 0]) >= o_neg) | (S[:, 1] >= o_neg) | ((20 - S[:, 1]) >= o_neg))
    say("| 統計量 | 観測 | 帰無 中央値 | 帰無 95%点 | p |")
    say("|---|---|---|---|---|")
    say("| S_neg BUY 負セル数 /20 | %d | %.0f | %.0f | **%.3f** |" % (o_neg, np.median(S[:, 0]), np.percentile(S[:, 0], 95), p_neg))
    say("| S_pos SELL 正セル数 /20 | %d | %.0f | %.0f | %.3f |" % (o_pos, np.median(S[:, 1]), np.percentile(S[:, 1], 95), p_pos))
    say("| S_gap 側差負セル数 /20 | %d | %.0f | %.0f | %.3f |" % (o_gap, np.median(S[:, 2]), np.percentile(S[:, 2], 95), p_gap))
    say("| S_maxt 40 セル max\\|t\\| | %.2f | %.2f | %.2f | **%.3f** |" % (o_maxt, np.median(S[:, 3]), np.percentile(S[:, 3], 95), p_maxt))
    say("| S_mint BUY min t | %.2f | %.2f | %.2f (5%%点) | %.3f |" % (o_mint, np.median(S[:, 4]), np.percentile(S[:, 4], 5), p_mint))
    say("どちらかの側・どちらかの符号で ≥%d/20 が揃う確率（側と符号の選び方の自由度込み）: **%.3f**。" % (o_neg, p_any20))
    say("帰無分布の S_neg ヒストグラム（0..20）: %s" % " ".join("%d:%d" % (k, int((S[:, 0] == k).sum())) for k in range(21) if (S[:, 0] == k).sum() > 0))
    say("（40 セルは入れ子（X）と重なり（時代）で強く相関するので、独立 20 セルの二項 p=2^-20 とは比べない。置換が正しい帰無。）")
    say()

    # ---------- Q3 ----------
    say("## Q3. 別分割の側差（e_BUY − e_SELL）: 偶数年/奇数年・4 年刻み")
    splits = (("偶数年", year % 2 == 0), ("奇数年", year % 2 == 1), ("2010-13", year <= 2013), ("2014-17", (year >= 2014) & (year <= 2017)),
              ("2018-21", (year >= 2018) & (year <= 2021)), ("2022-26", year >= 2022))
    say("| 分割 | X=1.0 BUY e / SELL e / 側差 / Welch t | X=1.25 BUY e / SELL e / 側差 / Welch t |")
    say("|---|---|---|")
    neg_cnt = {1.0: 0, 1.25: 0}
    for lab, m in splits:
        row = "| %s |" % lab
        for X in (1.0, 1.25):
            ok, e, _, _ = cells[X]; eb = e[ok & m & isB]; es = e[ok & m & ~isB]
            se = math.sqrt(eb.var(ddof=1) / len(eb) + es.var(ddof=1) / len(es)); g = eb.mean() - es.mean()
            neg_cnt[X] += int(g < 0)
            row += " %+.4f / %+.4f / %+.4f / %+.2f |" % (eb.mean(), es.mean(), g, g / se)
        say(row)
    say("側差負の分割数: X=1.0 **%d/6**（二項 p=%.3f）／X=1.25 %d/6（p=%.3f）。" % (neg_cnt[1.0], binom_p_ge(neg_cnt[1.0], 6), neg_cnt[1.25], binom_p_ge(neg_cnt[1.25], 6)))
    say()

    # ---------- Q4 ----------
    aB4 = 0.05 / 14
    say("## Q4. レジーム部分集合（X=1.0・建玉中 e・側別）。atr/risk 四分位 + JST 時間帯 = 14 セル、Bonferroni α=%.4f" % aB4)
    ok, e, clk, ka = cells[1.0]
    m1 = atr / risk; qs = np.nanpercentile(m1[ok], [25, 50, 75])
    qbin = np.digitize(m1, qs)
    say("atr/risk 四分位境界（建玉中集合）: %.3f / %.3f / %.3f" % tuple(qs))
    say("| 部分集合 | BUY n / e / t / p | SELL n / e / t / p | 側差 / Welch t |")
    say("|---|---|---|---|")
    sig4 = 0; gaps4 = []
    subsets = [("M1 Q%d" % (q + 1), qbin == q) for q in range(4)] + [("JST7-12", (jh >= 7) & (jh <= 12)), ("JST13-20", (jh >= 13) & (jh <= 20)), ("JST21-6", (jh >= 21) | (jh <= 6))]
    for lab, m in subsets:
        eb = e[ok & m & isB]; es = e[ok & m & ~isB]; tb, pb = tstat(eb); ts_, ps = tstat(es)
        sig4 += int(pb < aB4 and eb.mean() < 0)
        se = math.sqrt(eb.var(ddof=1) / len(eb) + es.var(ddof=1) / len(es)); g = eb.mean() - es.mean(); gaps4.append(g)
        say("| %s | %d / %+.4f / %+.2f / %.4f | %d / %+.4f / %+.2f / %.4f | %+.4f / %+.2f |" % (lab, len(eb), eb.mean(), tb, pb, len(es), es.mean(), ts_, ps, g, g / se))
    say("BUY 負で Bonferroni 有意: **%d/7**。側差負の部分集合 %d/7。" % (sig4, sum(1 for g in gaps4 if g < 0)))
    say()

    # ---------- Q5 ----------
    say("## Q5. 機械チェック（X=1.0 建玉中集合）")
    for sd, mm in (("BUY", isB), ("SELL", ~isB)):
        m = ok & mm; nn = m.sum()
        e_raw = R0[m] - clk[m]
        say("- %s n=%d: 決着 SL %.1f%% / TP %.1f%% / TIME %.1f%%；残り保有 hold−k 中央値 %.0f 本・平均 %.0f；cl_k 平均 %+.3f；e 公正化前 %+.4f → 後 %+.4f；b 中央値 %.2f" % (
            sd, nn, 100 * (er[m] == "SL").mean(), 100 * (er[m] == "TP").mean(), 100 * (er[m] == "TIME").mean(),
            np.median(hold[m] - ka[m]), (hold[m] - ka[m]).mean(), clk[m].mean(), e_raw.mean(), e[m].mean(), np.nanmedian(df.b.to_numpy()[m])))
    # TIME 本だけ除いた e（出口で条件づけるので判定に使わない・構造確認）
    for sd, mm in (("BUY", isB), ("SELL", ~isB)):
        m = ok & mm & (er != "TIME")
        say("- %s TIME 除外（構造確認・判定不使用）: e %+.4f (t%+.2f, n%d)" % (sd, e[m].mean(), tstat(e[m])[0], m.sum()))
    say()

    # ---------- Q6 ----------
    say("## Q6. コスト倍（05:20 Q5 の戦略形・BUY のみ +1R 初到達足の終値で成行クローズ）: s∈{0.20, 0.44} USD")
    say("| s USD | 在 diff / t | 外 diff / t | 2024-26 diff / t | 上位10% 残存 在 / 外 |")
    say("|---|---|---|---|---|")
    for s in (0.20, 0.44):
        R1 = R0.copy(); sel = ok & isB; R1[sel] = clk[sel] - s / risk[sel]; d = R1 - R0
        mi = isB & (year <= 2020); mo = isB & (year >= 2021); m24 = isB & (year >= 2024)
        say("| %.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %.0f%% / %.0f%% |" % (
            s, d[mi].mean(), tstat(d[mi])[0], d[mo].mean(), tstat(d[mo])[0], d[m24].mean(), tstat(d[m24])[0], top_ret(R0[mi], R1[mi]), top_ret(R0[mo], R1[mo])))
    say()

    # ---------- 判定 ----------
    say("## 判定（事前固定の規則）")
    say("- Q1 実測: BUY 負 %d/20・SELL(X≥0.75) 正 %d/16・2024-26 BUY 負 %d/5（主張は 20/20・16/16）" % (o_neg, pos_hi, buy24))
    say("- Q2 置換: p(S_neg) %.3f・p(S_maxt) %.3f・p(S_gap) %.3f・側/符号の自由度込み %.3f" % (p_neg, p_maxt, p_gap, p_any20))
    say("- Q3 別分割 側差負 X=1.0 %d/6" % neg_cnt[1.0])
    say("- Q4 BUY 負 Bonferroni 有意 %d/7" % sig4)
    if p_neg > 0.05 and p_maxt > 0.05 and sig4 == 0:
        v = "broken"
    elif p_neg < 0.01 and p_maxt < 0.05 and neg_cnt[1.0] >= 5 and buy24 == 5:
        v = "survived"
    else:
        v = "inconclusive"
    say("- 機械判定: **%s**（%.0fs）" % (v, time.time() - t0))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
