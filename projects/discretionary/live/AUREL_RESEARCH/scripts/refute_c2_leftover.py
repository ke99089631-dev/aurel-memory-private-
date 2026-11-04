# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-05 02:15 — 23:30 [REFUTE] で自分に残した反証を潰す。
対象: 「本物の建値逆指値 A（公正記帳・s=0）の diff が 2024-26 +0.0084 (t0.94)・BUY +0.0037 (t0.87)・
      遅延武装 d=6 で 2024-26 +0.0141 (t1.79)・BUY +0.0070 (t1.79) と近年窓・BUY 側で符号が正に揃う」。
読取りのみ・発注なし・scan なし。入力は既存キャッシュ（c1 json・c4 json・refute_c2_fullpaths.npz）。書き込みは data/ のみ。

事前固定（コードを書く前に固定・以後動かさない）:
  H0: 公正に記帳した出口の移動は期待値を変えない（マルチンゲール）。近年窓の正符号は 9 窓×遅延格子の“最良セル”を拾った選択効果。
  Q1 窓選択の帰無: 月ブロック（約 198 ブロック）をシャッフルして擬似年を振り直し、9 窓の |t| の最大値の分布を 2000 回で作る。
      観測の max|t|（A s=0）がその分布のどこにあるか（p_max）。遅延 d=6 版も同じ。
  Q2 水準プラセボ: 武装(+1.0R 初到達)後の逆指値を entry でなく entry+c·risk に置く。c∈{−0.6,−0.4,−0.2,0,+0.2,+0.4}R。
      記帳は _simulate の SL 規則（安値 ≤ c+ft で c 約定）。「建値」が特別なら c=0 に不連続な山があるはず。
      滑らかに通過するなら、正符号は“武装後に逆指値を置くこと一般”の性質＝水準 0 の情報ではない。Bonferroni α=0.05/(6×3 窓)。
  Q3 武装後ドリフト（モデル非依存）: 武装足 k の終値 cl_k と、公正化した最終 R*（SL/TP は +ft 戻す・TIME はそのまま）の差 e = R* − cl_k。
      マルチンゲールなら E[e]=0。2024-26 で e が有意に負なら「+1R 後に戻る」ドリフトがあり、どんな逆指値も助かる（＝建値の話ではない）。
      e≈0 なら A の正符号はノイズ。窓 9・Bonferroni α=0.05/9。
  Q4 感度: 武装判定を fav ≥ X（23:30 と同じ）と fav ≥ X+ft（TP と同じ到達記帳）の両方で A の diff を出す。
判定（事前固定）:
  broken       = Q1 p_max > 0.05（d=0・d=6 とも）かつ Q2 で c=0 が隣接水準より Bonferroni 有意に高くない かつ Q3 2024-26 の e が Bonferroni 非有意。
  survived     = Q1 p_max < 0.05 かつ Q2 で c=0 が隣接水準（±0.2）を Bonferroni 有意に上回る かつ Q3 2024-26 e<0 Bonferroni 有意。
  それ以外     = inconclusive。
出力: data/refute_c2_leftover.md
"""
import os, sys, math, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
from refute_c2_breakeven import load, tstat, top_ret, windows, NPZ, DATA

OUT = os.path.join(DATA, "refute_c2_leftover.md")
X0 = 1.0
LEVELS = (-0.6, -0.4, -0.2, 0.0, 0.2, 0.4)
NPERM = 2000
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def main():
    t0 = time.time()
    df, J, FT = load()
    n = len(df); R0 = df.R.to_numpy(); risk = df.risk.to_numpy(); ft = df.ft.to_numpy()
    z = np.load(NPZ); hiR, loR, clR, off = z["hiR"], z["loR"], z["clR"], z["off"]
    assert len(off) - 1 == n
    say("# AUREL [REFUTE] 2026-11-05 — 23:30 の残存反証（建値逆指値 A の近年窓・BUY 正符号）を潰す  入力 %d 本  %s" % (n, time.strftime("%Y-%m-%d %H:%M")))
    say("FEED_TOL=%.2f USD、ft 平均 %.4fR。path は切断なし（refute_c2_fullpaths.npz）。" % (FT, ft.mean()))
    say()
    masks = [(lab, m.to_numpy()) for lab, m in windows(df)]

    # ---- 共通: 武装足 k（fav ≥ X）、武装後に水準 c の逆指値 ----
    def arm_idx(X, plus_ft=False):
        ka = np.full(n, -1)
        for i in range(n):
            fav = hiR[off[i]:off[i + 1]]
            thr = X + (ft[i] if plus_ft else 0.0)
            a = np.nonzero(fav >= thr)[0]
            if len(a): ka[i] = int(a[0])
        return ka

    def stop_at(ka, c, delay=0):
        """武装足 ka[i]+delay の翌足以降、adv ≤ c+ft で c 約定（_simulate SL 規則）。発動なしは原型。"""
        R1 = R0.copy(); tg = np.zeros(n, bool)
        for i in np.nonzero(ka >= 0)[0]:
            adv = loR[off[i]:off[i + 1]]; k = int(ka[i]) + delay
            if k + 1 < len(adv):
                hit = np.nonzero(adv[k + 1:] <= c + ft[i])[0]
                if len(hit): R1[i] = c; tg[i] = True
        return R1, tg

    kaA = arm_idx(X0)
    R_A, tgA = stop_at(kaA, 0.0, 0)
    R_A6, tgA6 = stop_at(kaA, 0.0, 6)
    dA = R_A - R0; dA6 = R_A6 - R0
    say("再現: A s=0 全本 diff %+.4f (t%+.2f)・発動 %d 本／d=6 %+.4f (t%+.2f)・発動 %d 本（23:30: +0.0004 / 1754 本）。" % (
        dA.mean(), tstat(dA)[0], tgA.sum(), dA6.mean(), tstat(dA6)[0], tgA6.sum()))
    say()

    # ---------- Q1 ----------
    say("## Q1. 窓選択の帰無 — 月ブロックをシャッフルして擬似年を振り直し、9 窓の max|t| の分布（%d 回）" % NPERM)
    ts = {lab: tstat(dA[m])[0] for lab, m in masks}; ts6 = {lab: tstat(dA6[m])[0] for lab, m in masks}
    obs_max = max(abs(v) for v in ts.values()); obs_max6 = max(abs(v) for v in ts6.values())
    obs_2426 = ts["2024-26"]; obs_2426_6 = ts6["2024-26"]
    say("観測 |t| (A s=0): " + "；".join("%s %+.2f" % (lab, ts[lab]) for lab, _ in masks))
    say("観測 |t| (d=6):   " + "；".join("%s %+.2f" % (lab, ts6[lab]) for lab, _ in masks))
    # 月ブロック
    et = pd.to_datetime(df.entry_time.to_numpy(), unit="s", utc=True).tz_convert("Asia/Tokyo")
    month_id = (et.year * 12 + et.month).to_numpy(); uniq = np.unique(month_id); nb = len(uniq)
    blk = np.searchsorted(uniq, month_id)
    year_of_month = uniq // 12  # 擬似年の素: 元の暦年（ブロック順に振り直す）
    # 元の窓を「年」で切るので、シャッフルしたブロック順に元の年ラベルを並べ直して擬似年にする
    orig_year_seq = (uniq // 12).astype(int)  # 月 i の年
    # 2026 は 1-6 月のみ。擬似年＝シャッフル後の位置 j に対応する元の年 orig_year_seq[j]
    rng = np.random.default_rng(20261105)
    jh = df.jh.to_numpy(); wall = df.wall_kind.to_numpy(); side = df.side.to_numpy()
    jm = (jh >= 7) & (jh <= 12)
    def win_masks(year):
        return (year <= 2020, year >= 2021, (year >= 2021) & (year <= 2023), year >= 2024, year >= 2025,
                jm & (wall == "outer"), jm & (wall == "mid"), side == "BUY", side == "SELL")
    def tvec(d, year):
        return np.array([tstat(d[m])[0] for m in win_masks(year)])
    mx = np.empty(NPERM); mx6 = np.empty(NPERM); t24 = np.empty(NPERM); t24_6 = np.empty(NPERM)
    for r in range(NPERM):
        perm = rng.permutation(nb)              # ブロック b は位置 perm[b] へ
        pyear = orig_year_seq[perm][blk]        # 各本の擬似年
        tv = tvec(dA, pyear); tv6 = tvec(dA6, pyear)
        mx[r] = np.nanmax(np.abs(tv)); mx6[r] = np.nanmax(np.abs(tv6)); t24[r] = tv[3]; t24_6[r] = tv6[3]
    say("月ブロック %d 個。max|t| 帰無分布: 中央値 %.2f・95%%点 %.2f（A s=0）／ %.2f・%.2f（d=6）。" % (nb, np.median(mx), np.percentile(mx, 95), np.median(mx6), np.percentile(mx6, 95)))
    p_max = np.mean(mx >= obs_max); p_max6 = np.mean(mx6 >= obs_max6)
    p24 = np.mean(t24 >= obs_2426); p24_6 = np.mean(t24_6 >= obs_2426_6)
    say("**観測 max|t| %.2f → p_max %.3f（A s=0）／ %.2f → p_max %.3f（d=6）。** 2024-26 窓単独（擬似 2024-26 の t ≥ 観測）: p %.3f（A）／ p %.3f（d=6）。" % (
        obs_max, p_max, obs_max6, p_max6, p24, p24_6))
    # 年別 diff 一覧（符号の散らばり）
    say()
    say("年別 A s=0 diff（符号の散らばり・|diff|≥0.0084 の年を数える）:")
    yrs = sorted(df.year.unique()); big = 0; pos = 0
    row = []
    for y in yrs:
        m = (df.year == y).to_numpy(); d = dA[m]; t_ = tstat(d)[0]
        row.append("%d %+.4f(t%+.1f,n%d)" % (y, d.mean(), t_, m.sum()))
        if abs(d.mean()) >= 0.0084: big += 1
        if d.mean() > 0: pos += 1
    say("  " + "；".join(row))
    say("  |diff|≥0.0084 の年 %d/%d・正の年 %d/%d（二項 p=%.2f）。" % (big, len(yrs), pos, len(yrs), 2 * min(sum(math.comb(len(yrs), k) for k in range(pos, len(yrs) + 1)), sum(math.comb(len(yrs), k) for k in range(0, pos + 1))) / 2 ** len(yrs)))
    say()

    # ---------- Q2 ----------
    say("## Q2. 水準プラセボ — 武装(+%.1fR)後の逆指値を entry+c·risk に置く（c=0 が建値）。記帳は SL 規則。Bonferroni α=%.4f" % (X0, 0.05 / (len(LEVELS) * 3)))
    say("| c (R) | 全本 発動 / diff / t | 在 diff / t | 外 diff / t | **2024-26 diff / t / p** | 2025-26H1 | BUY diff / t | SELL | 上位10%残存 全本 |")
    say("|---|---|---|---|---|---|---|---|---|")
    Q2 = {}
    M = dict(masks)
    for c in LEVELS:
        Rc, tgc = stop_at(kaA, c, 0); dc = Rc - R0
        cells = {lab: (dc[m].mean(), tstat(dc[m])[0], tstat(dc[m])[1]) for lab, m in masks}
        Q2[c] = (dc, cells)
        say("| %+.1f | %d / %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | **%+.4f / %+.2f / %.3f** | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %.0f%% |" % (
            c, tgc.sum(), dc.mean(), tstat(dc)[0], *cells["在 2010-20"][:2], *cells["外 2021-26"][:2], *cells["2024-26"], *cells["2025-26H1"][:2],
            *cells["BUY"][:2], *cells["SELL"][:2], top_ret(R0, Rc)))
    # c=0 vs 隣接水準の対差（同じ本・paired）
    say()
    say("c=0 と隣接水準の対差（R_c0 − R_c・paired t）:")
    for lab in ("外 2021-26", "2024-26", "BUY"):
        m = M[lab]; s = []
        for c in (-0.2, 0.2):
            dd = Q2[0.0][0][m] - Q2[c][0][m]; s.append("vs c=%+.1f: %+.4f (t%+.2f, p%.3f)" % (c, dd.mean(), *tstat(dd)))
        say("  %s: %s" % (lab, "；".join(s)))
    say("（建値が特別なら c=0 が両隣より有意に高い山。マルチンゲールなら全水準 ≈0。全水準が同符号で滑らかなら“武装後ドリフト”の話＝Q3。）")
    say()

    # ---------- Q3 ----------
    say("## Q3. 武装後ドリフト（モデル非依存）: e = R*（SL/TP は +ft で公正化・TIME はそのまま）− cl_k（武装足終値）。Bonferroni α=%.4f" % (0.05 / 9))
    er = df.exit_reason.to_numpy()
    Rstar = R0 + np.where((er == "SL") | (er == "TP"), ft, 0.0)
    armed = kaA >= 0
    clk = np.full(n, np.nan)
    for i in np.nonzero(armed)[0]:
        clk[i] = clR[off[i] + int(kaA[i])]
    e = Rstar - clk
    say("武装本 %d (%.1f%%)。武装足終値 cl_k 平均 %+.3fR（+1R 到達足の終値）。公正化 R* 平均 %+.3f。" % (armed.sum(), 100 * armed.mean(), np.nanmean(clk[armed]), Rstar[armed].mean()))
    say("| 窓 | 武装 n | mean e / t / p | e の中央値 | 原型 R 平均（武装本） | 参考: 武装本の A diff |")
    say("|---|---|---|---|---|---|")
    Q3 = {}
    for lab, m in masks:
        mm = m & armed; ee = e[mm]; t_, p_ = tstat(ee); Q3[lab] = (ee.mean(), t_, p_)
        say("| %s | %d | %+.4f / %+.2f / %.4f | %+.3f | %+.3f | %+.4f |" % (lab, mm.sum(), ee.mean(), t_, p_, np.median(ee), R0[mm].mean(), dA[mm].mean()))
    # 武装後ドリフトを「その後 0 に触れた本」と「触れなかった本」に分けるのは未来条件づけなので出さない。
    # 代わりに 2024-26 の e を年別に。
    say("2024-26 年別 e: " + "；".join("%d %+.4f (t%+.2f, n%d)" % (y, e[(df.year == y).to_numpy() & armed].mean(), tstat(e[(df.year == y).to_numpy() & armed])[0], ((df.year == y).to_numpy() & armed).sum()) for y in (2024, 2025, 2026)))
    say()
    # ---- Q3' 修正（結果を見てから追加・理由を明記）----
    # 上の Q3 は欠陥: b の中央値 0.99 のため、武装足 k で TP が決着する本が多い。その本は R*=b+ft で確定しており cl_k（スパイク足の終値）
    # と比べるのはマルチンゲール検定でない（終値は高値に引かれ R* より上に出やすい → e が機械的に負）。
    # 正しい母集団は「武装足 k の終値時点でまだ建玉中（hold > k）」の本。その本は cl_k < b+ft が保証され、E[R*|F_k]=cl_k が成り立つ。
    hold = df.hold.to_numpy()
    open_k = armed & (hold > kaA)
    say("### Q3'. 修正: 武装足 k で決着した本（hold==k）を除く → 「k の終値時点で建玉中」の本だけ。Bonferroni α=%.4f" % (0.05 / 9))
    say("武装本 %d のうち武装足で決着 %d（TP %d / SL %d）→ 建玉中 %d 本。" % (
        armed.sum(), (armed & (hold == kaA)).sum(), (armed & (hold == kaA) & (er == "TP")).sum(), (armed & (hold == kaA) & (er == "SL")).sum(), open_k.sum()))
    say("| 窓 | 建玉中 n | **mean e / t / p** | e 中央値 | cl_k 平均 | R* 平均 | 参考: 同集合の A diff |")
    say("|---|---|---|---|---|---|---|")
    Q3p = {}
    for lab, m in masks:
        mm = m & open_k; ee = e[mm]; t_, p_ = tstat(ee); Q3p[lab] = (ee.mean(), t_, p_)
        say("| %s | %d | **%+.4f / %+.2f / %.4f** | %+.3f | %+.3f | %+.3f | %+.4f |" % (lab, mm.sum(), ee.mean(), t_, p_, np.median(ee), clk[mm].mean(), Rstar[mm].mean(), dA[mm].mean()))
    say("2024-26 年別 e（建玉中）: " + "；".join("%d %+.4f (t%+.2f, n%d)" % (y, e[(df.year == y).to_numpy() & open_k].mean(), tstat(e[(df.year == y).to_numpy() & open_k])[0], ((df.year == y).to_numpy() & open_k).sum()) for y in (2024, 2025, 2026)))
    # 武装足決着本の e（アーティファクトの大きさの確認）
    ex_k = armed & (hold == kaA)
    say("武装足で決着した本の e（参考・アーティファクト）: 全本 %+.4f (t%+.2f, n%d)。" % (e[ex_k].mean(), tstat(e[ex_k])[0], ex_k.sum()))
    say()
    Q3 = Q3p  # 判定は Q3' を使う（理由は上記）

    # ---------- Q4 ----------
    say("## Q4. 感度: 武装判定 fav ≥ X（23:30）vs fav ≥ X+ft（TP と同じ到達記帳）")
    kaP = arm_idx(X0, plus_ft=True); R_P, tgP = stop_at(kaP, 0.0, 0); dP = R_P - R0
    say("| 窓 | A(fav≥X) diff / t | A(fav≥X+ft) diff / t | 発動 %d → %d |" % (tgA.sum(), tgP.sum())); say("|---|---|---|---|")
    for lab, m in masks:
        say("| %s | %+.4f / %+.2f | %+.4f / %+.2f | |" % (lab, dA[m].mean(), tstat(dA[m])[0], dP[m].mean(), tstat(dP[m])[0]))
    say()

    # ---------- 判定 ----------
    say("## 判定（事前固定の規則）")
    a_bonf = 0.05 / (len(LEVELS) * 3)
    m24 = M["2024-26"]
    bump = []
    for lab in ("外 2021-26", "2024-26", "BUY"):
        m = M[lab]; ok = True
        for c in (-0.2, 0.2):
            dd = Q2[0.0][0][m] - Q2[c][0][m]; t_, p_ = tstat(dd)
            ok = ok and (dd.mean() > 0 and p_ < a_bonf)
        bump.append(ok)
    q3sig = Q3["2024-26"][0] < 0 and Q3["2024-26"][2] < 0.05 / 9
    say("- Q1 p_max: A %.3f / d=6 %.3f（>0.05 で選択効果と区別できない）" % (p_max, p_max6))
    say("- Q2 c=0 が両隣(±0.2R)を Bonferroni 有意に上回る窓: 外 %s / 2024-26 %s / BUY %s" % tuple(bump))
    say("- Q3 2024-26 e = %+.4f (t%+.2f, p%.4f)・有意負 %s" % (Q3["2024-26"][0], Q3["2024-26"][1], Q3["2024-26"][2], q3sig))
    if p_max > 0.05 and p_max6 > 0.05 and not any(bump) and not q3sig:
        v = "broken"
    elif p_max < 0.05 and bump[1] and q3sig:
        v = "survived"
    else:
        v = "inconclusive"
    say("- 機械判定: **%s**（%.0fs）" % (v, time.time() - t0))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
