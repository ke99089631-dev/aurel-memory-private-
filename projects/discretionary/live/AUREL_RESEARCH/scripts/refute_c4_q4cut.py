# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-05 11:20 — 11-04 14:25 [REFUTE] で自分に残した反証（唯一の未着手の残存反証）を潰す。
対象: 「M1 Q4（atr/risk 上位 25%＝ストップが ATR の半分以下の“狭いストップ”本）では、建玉足後に −0.5R まで沈んだら
      切る方が持つより +0.052R/沈み本 良い（t≈3・n3386）、2024-26 も同符号 +0.063（n1399）。隣の Q2 は符号が逆。
      24 セル中の post-hoc 1 セル・事前固定なし・負方向」。
読取りのみ・発注なし・scan なし・M5 読込なし。入力は既存キャッシュ（c1 json・c4 json・refute_c2_fullpaths.npz）。書き込みは data/ のみ。

事前固定（コードを書く前に固定・以後動かさない）:
  H0: 公正に記帳した出口の移動は期待値を変えない（マルチンゲール）。M1 Q4 の +0.05 は 2 メーター×4 分位×近年窓 の格子から
      post-hoc に最良セルを拾った選択効果。
  記帳: 「切る」は本物の逆指値規則（_simulate の SL 規則と同じ: 足 k≥1 の安値R ≤ c+ft で c 約定、c=−0.5R）。原型 SL/TP も
      同じ規則で記帳されているので、R_cut − R_orig は記帳の非対称なし（20:25/23:30 の贈り物問題は生じない）。bar0 は約定前
      レンジを含むため 14:25 と同じく除外（感度で bar0 込みも出す）。
  Q0 再現: 14:25 の数字（mae1≥0.5 集合で 平均R − (−0.5)）を同じ定義で再現。
  Q1 本物の逆指値規則での diff（発動本の平均・t・n）。M1 の 4 分位すべて・全体・2024-26。
  Q2 選択効果の帰無（主検定）: 年層内で本の (M1 分位, M2 分位) ラベルを 2000 回シャッフル。各回 12 セル（M1 Q1-4・M2 Q1-4・
      M1@2024-26 Q1-4）の「発動本 diff の t」を出し、最大値の帰無分布。観測の最大 t（M1 Q4）の p_max。
  Q3 別分割（真の在→外）: 在 2010-20 だけで Q4 境界（75% 点）を決め、外 2021-26 / 2021-23 / 2024-26 / 2025-26H1 に固定閾値で
      適用。逆（外で決めて在に適用）、偶数/奇数年、4 年刻み。
  Q4 単調性: atr/risk 十分位ごとの発動本 diff。「狭いストップほど効く」なら上位十分位へ単調に増えるはず。隣接の符号反転を数える。
  Q5 水準プラセボ（Q4 内）: c∈{−0.3,−0.4,−0.5,−0.6,−0.7}R。マルチンゲールなら全水準 ≈0。−0.5 に山があるか。
  Q6 コスト倍: 切りの成行滑り s∈{0, 0.10, 0.20} USD（14:25 の想定 ≈0.1 USD の倍まで）。戦略形「Q4（固定閾値）の本だけ
      −0.5R で切る」を全本 paired diff で 在/外/2024-26/2025-26H1/本番窓 で採点。研究レーン基準: 在 t≥2・外 t≥1.5・上位10% 残存≥90%。
  Q7 構造: Q4 の risk==MIN_SL_W 比率、発動本の決着種別、b 分布（文脈・判定不使用）。
判定（事前固定）:
  broken       = Q2 p_max > 0.05、または Q3 外（在境界固定・2021-26）の発動本 diff t < 1.0、または Q6 s=0.10 で 在・外ともに基準不達。
  survived     = Q2 p_max < 0.05 かつ Q3 外 t ≥ 1.5 かつ Q4 上位 3 十分位がすべて正 かつ Q6 s=0.10 で基準 3 つを満たす。
  それ以外     = inconclusive。
出力: data/refute_c4_q4cut.md
"""
import os, sys, math, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
from refute_c2_breakeven import load, tstat, top_ret, NPZ, DATA, C4
import json

OUT = os.path.join(DATA, "refute_c4_q4cut.md")
NPERM = 2000
C_MAIN = -0.5
LEVELS = (-0.3, -0.4, -0.5, -0.6, -0.7)
SLIPS = (0.0, 0.10, 0.20)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def cell(d):
    d = np.asarray(d, float); d = d[~np.isnan(d)]
    if len(d) < 2: return (len(d), float("nan"), float("nan"), float("nan"))
    t, p = tstat(d)
    return (len(d), d.mean(), t, p)


def fmt(c):
    return "n%d %+.4f (t%+.2f, p%.3f)" % c


def main():
    t_start = time.time()
    df, J, FT = load()
    c4 = json.load(open(C4, encoding="utf-8"))
    aux = pd.DataFrame(c4["trades"])[["entry_time", "atr", "x0", "mae1", "mfe1", "exit"]]
    n_before = len(df); dup = int(aux.entry_time.duplicated().sum())
    aux = aux.drop_duplicates("entry_time", keep="first")
    df = df.merge(aux, on="entry_time", how="left")
    assert len(df) == n_before, (len(df), n_before)
    MIN_SL_W = c4["frozen"]["MIN_SL_W"]
    n = len(df); R0 = df.R.to_numpy(); risk = df.risk.to_numpy(); ft = df.ft.to_numpy()
    z = np.load(NPZ); hiR, loR, clR, off = z["hiR"], z["loR"], z["clR"], z["off"]
    assert len(off) - 1 == n
    df["atr"] = pd.to_numeric(df.atr, errors="coerce"); df["atr_risk"] = df.atr / df.risk
    say("# AUREL [REFUTE] 2026-11-05 — 14:25 の残存反証「M1 Q4（狭いストップ）は −0.5R で切る方が良い」を潰す  入力 %d 本  %s" % (n, time.strftime("%Y-%m-%d %H:%M")))
    say("FEED_TOL=%.2f USD、ft 平均 %.4fR、MIN_SL_W=%.1f。path は切断なし（refute_c2_fullpaths.npz）。ATR14 は建玉足の 1 本前まで（shift(1)）＝look-ahead なし。c4 の entry_time 重複 %d 本は先頭を採用。" % (FT, ft.mean(), MIN_SL_W, dup))
    # 整合: bar1 以降の最小 loR と −mae1
    chk = []
    for i in range(n):
        if df.hold.iat[i] >= 1 and off[i + 1] - off[i] > 1:
            chk.append(abs(-loR[off[i] + 1:off[i + 1]].min() - df.mae1.iat[i]))
    chk = np.array(chk)
    say("整合: bar1 以降の min(loR) vs キャッシュ mae1（n%d）: 中央値差 %.4fR、|差|>0.01R %d 本、>0.1R %d 本、最大 %.2fR（23:30 の再構築不一致 37 本＝境界丸めと同系）。" % (
        len(chk), np.median(chk), (chk > 0.01).sum(), (chk > 0.1).sum(), chk.max()))
    say()

    # ---- 対象集合（14:25 と同じ）: hold≥1・a>0.5・atr 有り ----
    sub_m = ((df.hold >= 1) & ((1 - df.ft) > 0.5) & df.atr_risk.notna()).to_numpy()
    year = df.year.to_numpy(); jh = df.jh.to_numpy(); wall = df.wall_kind.to_numpy(); side = df.side.to_numpy()
    ar = df.atr_risk.to_numpy()
    edges = np.nanquantile(ar[sub_m], [0, .25, .5, .75, 1])
    q1 = np.full(n, -1); q1[sub_m] = np.clip(np.searchsorted(edges[1:4], ar[sub_m], side="right"), 0, 3)
    say("対象（hold≥1・a>0.5）n=%d。M1 atr/risk 四分位境界 %s（14:25: 0.237/0.331/0.470）。" % (sub_m.sum(), "/".join("%.3f" % e for e in edges[1:4])))
    # M2: atr の直近 1 年 percentile（自分より前の setup のみ）
    et = df.entry_time.to_numpy().astype(np.int64); atr_v = df.atr.to_numpy()
    m2 = np.full(n, np.nan)
    for i in range(n):
        j0 = np.searchsorted(et, et[i] - 365 * 86400, side="right")
        w = atr_v[j0:i]; w = w[~np.isnan(w)]
        if len(w) >= 50 and not np.isnan(atr_v[i]): m2[i] = (w < atr_v[i]).mean()
    sub2_m = sub_m & ~np.isnan(m2)
    e2 = np.nanquantile(m2[sub2_m], [.25, .5, .75])
    q2 = np.full(n, -1); q2[sub2_m] = np.clip(np.searchsorted(e2, m2[sub2_m], side="right"), 0, 3)
    say("M2 atr_pct1y 利用可 n=%d、境界 %s。" % (sub2_m.sum(), "/".join("%.3f" % e for e in e2)))
    say()

    # ---- 切りの逆指値（本物の規則）----
    def cut(c, from_bar=1, slip_usd=0.0):
        """足 k≥from_bar の安値R ≤ c+ft で c−slip/risk 約定。返り値 R_cut（非発動は原型）, fired mask。"""
        R1 = R0.copy(); fired = np.zeros(n, bool)
        for i in range(n):
            lo = loR[off[i]:off[i + 1]]
            if len(lo) <= from_bar: continue
            hit = np.nonzero(lo[from_bar:] <= c + ft[i])[0]
            if len(hit):
                R1[i] = c - slip_usd / risk[i]; fired[i] = True
        return R1, fired

    # ---- Q0 再現 ----
    say("## Q0. 再現（14:25 の定義: mae1≥0.5 の本で 平均R(持つ) − (−0.5)）")
    dip = sub_m & (df.mae1.to_numpy() >= 0.5)
    for qi in range(4):
        m = dip & (q1 == qi); d = R0[m] + 0.5
        say("- M1 Q%d: n%d 平均R %+.3f 持つ−切る %+.4f (t%+.2f)" % (qi + 1, m.sum(), R0[m].mean(), d.mean(), tstat(d)[0]))
    m = dip & (q1 == 3) & (year >= 2024); d = R0[m] + 0.5
    say("- M1 Q4 @2024-26: n%d 持つ−切る %+.4f (t%+.2f)（14:25: −0.063, n1399）" % (m.sum(), d.mean(), tstat(d)[0]))
    say()

    # ---- Q1 本物の規則 ----
    say("## Q1. 本物の逆指値規則（安値R ≤ −0.5+ft で −0.5 約定・bar1 以降）での diff = R_cut − R_orig（発動本）")
    Rc, fired = cut(C_MAIN)
    d_all = np.where(fired, Rc - R0, np.nan)
    say("| 集合 | 発動 n | diff 平均 | t | p | 2024-26 | 2025-26H1 |")
    say("|---|---|---|---|---|---|---|")
    for qi in range(4):
        m = sub_m & (q1 == qi)
        c_ = cell(d_all[m]); c24 = cell(d_all[m & (year >= 2024)]); c25 = cell(d_all[m & (year >= 2025)])
        say("| M1 Q%d | %d | %+.4f | %+.2f | %.4f | %s | %s |" % (qi + 1, c_[0], c_[1], c_[2], c_[3], fmt(c24), fmt(c25)))
    c_ = cell(d_all[sub_m]); say("| 全体 | %d | %+.4f | %+.2f | %.4f | %s | %s |" % (c_[0], c_[1], c_[2], c_[3], fmt(cell(d_all[sub_m & (year >= 2024)])), fmt(cell(d_all[sub_m & (year >= 2025)]))))
    obs_q4 = cell(d_all[sub_m & (q1 == 3)])
    Rc0, fired0 = cut(C_MAIN, from_bar=0); d0 = np.where(fired0, Rc0 - R0, np.nan)
    say("感度 bar0 込み（約定前レンジ混入・上限評価）: M1 Q4 %s／全体 %s。" % (fmt(cell(d0[sub_m & (q1 == 3)])), fmt(cell(d0[sub_m]))))
    say("発動本の原型決着（Q4）: SL %d / TP %d / TIME %d。発動本の原型平均R %+.3f。" % (
        ((df.exit_reason == "SL") & fired & sub_m & (q1 == 3)).sum(), ((df.exit_reason == "TP") & fired & sub_m & (q1 == 3)).sum(),
        ((df.exit_reason == "TIME") & fired & sub_m & (q1 == 3)).sum(), R0[fired & sub_m & (q1 == 3)].mean()))
    say()

    # ---- Q2 置換（主検定）----
    say("## Q2. 選択効果の帰無 — 年層内で (M1 分位, M2 分位) ラベルを %d 回シャッフル、12 セルの max t" % NPERM)
    rng = np.random.default_rng(20261105)
    idx = np.nonzero(sub_m)[0]; dv = d_all[idx]; fired_v = ~np.isnan(dv); yv = year[idx]
    q1v = q1[idx]; q2v = q2[idx]; rec = yv >= 2024
    def cells_t(q1l, q2l):
        ts = []
        for qi in range(4):
            ts.append(cell(dv[fired_v & (q1l == qi)])[2])
        for qi in range(4):
            ts.append(cell(dv[fired_v & (q2l == qi)])[2])
        for qi in range(4):
            ts.append(cell(dv[fired_v & rec & (q1l == qi)])[2])
        return np.array(ts)
    obs_ts = cells_t(q1v, q2v); obs_max = np.nanmax(obs_ts)
    names = ["M1Q%d" % (i + 1) for i in range(4)] + ["M2Q%d" % (i + 1) for i in range(4)] + ["M1@24-26 Q%d" % (i + 1) for i in range(4)]
    say("観測 12 セル t（切る−持つ・正＝切る方が良い）: " + "；".join("%s %+.2f" % (a, b) for a, b in zip(names, obs_ts)))
    strata = {y: np.nonzero(yv == y)[0] for y in np.unique(yv)}
    mx = np.empty(NPERM); tq4 = np.empty(NPERM)
    for r in range(NPERM):
        p1 = q1v.copy(); p2 = q2v.copy()
        for y, ii in strata.items():
            pp = rng.permutation(ii); p1[ii] = q1v[pp]; p2[ii] = q2v[pp]
        ts = cells_t(p1, p2); mx[r] = np.nanmax(ts); tq4[r] = ts[3]
    p_max = np.mean(mx >= obs_max); p_q4 = np.mean(tq4 >= obs_ts[3])
    say("**帰無 max t: 中央値 %.2f・95%%点 %.2f。観測 max t %.2f（%s）→ p_max %.3f。** M1 Q4 セル単独（1 セルを事前に選んでいた場合）: p %.3f。" % (
        np.median(mx), np.percentile(mx, 95), obs_max, names[int(np.nanargmax(obs_ts))], p_max, p_q4))
    say()

    # ---- Q3 別分割 ----
    say("## Q3. 別分割 — 在 2010-20 で Q4 境界を決め、外へ固定閾値で適用（真の在→外）")
    thr_in = np.nanquantile(ar[sub_m & (year <= 2020)], .75); thr_out = np.nanquantile(ar[sub_m & (year >= 2021)], .75)
    say("在境界 %.3f／外境界 %.3f／全体境界 %.3f。" % (thr_in, thr_out, edges[3]))
    hi_in = sub_m & (ar >= thr_in)
    say("| 窓 | 在境界 Q4 発動本 diff | 全体境界 Q4 | 全体 Q1-3（対照） |")
    say("|---|---|---|---|")
    jm = (jh >= 7) & (jh <= 12)
    wins = (("在 2010-20", year <= 2020), ("**外 2021-26**", year >= 2021), ("2021-23", (year >= 2021) & (year <= 2023)), ("2024-26", year >= 2024),
            ("2025-26H1", year >= 2025), ("本番窓 JST7-12×outer", jm & (wall == "outer")), ("本番窓 JST7-12×mid", jm & (wall == "mid")), ("BUY", side == "BUY"), ("SELL", side == "SELL"))
    q3_out = None
    for lab, m in wins:
        c_in = cell(d_all[hi_in & m]); c_full = cell(d_all[sub_m & (q1 == 3) & m]); c_lo = cell(d_all[sub_m & (q1 < 3) & m])
        if lab.startswith("**外"): q3_out = c_in
        say("| %s | %s | %s | %s |" % (lab, fmt(c_in), fmt(c_full), fmt(c_lo)))
    say("逆（外境界 %.3f を在に適用）: %s。" % (thr_out, fmt(cell(d_all[sub_m & (ar >= thr_out) & (year <= 2020)]))))
    say("偶数年 %s／奇数年 %s（全体境界）。" % (fmt(cell(d_all[sub_m & (q1 == 3) & (year % 2 == 0)])), fmt(cell(d_all[sub_m & (q1 == 3) & (year % 2 == 1)]))))
    blocks = []
    for y0 in (2010, 2014, 2018, 2022):
        m = sub_m & (q1 == 3) & (year >= y0) & (year <= y0 + 3); blocks.append("%d-%d %s" % (y0, y0 + 3, fmt(cell(d_all[m]))))
    say("4 年刻み: " + "；".join(blocks))
    say()

    # ---- Q4 十分位 ----
    say("## Q4. atr/risk 十分位ごとの発動本 diff（狭いストップほど効くなら上位へ単調増）")
    dec_e = np.nanquantile(ar[sub_m], np.linspace(0, 1, 11))
    dec = np.full(n, -1); dec[sub_m] = np.clip(np.searchsorted(dec_e[1:10], ar[sub_m], side="right"), 0, 9)
    say("| 十分位 | 範囲 | 発動 n | diff | t | 2024-26 diff / t |")
    say("|---|---|---|---|---|---|")
    means = []
    for di in range(10):
        m = sub_m & (dec == di); c_ = cell(d_all[m]); c24 = cell(d_all[m & (year >= 2024)]); means.append(c_[1])
        say("| D%d | %.3f-%.3f | %d | %+.4f | %+.2f | %+.4f / %+.2f |" % (di + 1, dec_e[di], dec_e[di + 1], c_[0], c_[1], c_[2], c24[1], c24[2]))
    means = np.array(means); flips = int(np.sum(np.sign(means[1:]) != np.sign(means[:-1])))
    rho = pd.Series(means).corr(pd.Series(np.arange(10)), method="spearman")
    say("隣接十分位の符号反転 %d 回／Spearman ρ(十分位, diff) %+.2f／上位 3 十分位 D8-D10 の符号 %s。" % (flips, rho, "".join("+" if v > 0 else "-" for v in means[7:])))
    say()

    # ---- Q5 水準プラセボ ----
    say("## Q5. 水準プラセボ（M1 Q4・全体境界）: c の格子で発動本 diff と戦略 diff")
    say("| c (R) | 発動 n | 発動本 diff / t | Q4 全本 diff / t | 2024-26 Q4 全本 diff / t | 上位10% 残存 (Q4 内) |")
    say("|---|---|---|---|---|---|")
    mq4 = sub_m & (q1 == 3)
    for c in LEVELS:
        Rc_, f_ = cut(c); d_ = np.where(f_, Rc_ - R0, np.nan); dz = np.where(f_, Rc_ - R0, 0.0)
        cf = cell(d_[mq4]); ca = cell(dz[mq4]); c24 = cell(dz[mq4 & (year >= 2024)])
        say("| %+.1f | %d | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %.0f%% |" % (c, cf[0], cf[1], cf[2], ca[1], ca[2], c24[1], c24[2], top_ret(R0[mq4], Rc_[mq4])))
    say()

    # ---- Q6 コスト倍・戦略採点 ----
    say("## Q6. 戦略形「Q4（在境界 %.3f 固定）の本だけ −0.5R で切る」全本 paired diff・滑り s（研究レーン基準: 在 t≥2・外 t≥1.5・上位10%% 残存≥90%%）" % thr_in)
    say("| s USD | 在 diff / t | 外 diff / t | 2024-26 | 2025-26H1 | 本番窓 outer | 本番窓 mid | 上位10% 残存 在/外 | 基準 |")
    say("|---|---|---|---|---|---|---|---|---|")
    q6_pass = {}
    for s in SLIPS:
        Rc_, f_ = cut(C_MAIN, slip_usd=s)
        apply = f_ & hi_in
        R1 = np.where(apply, Rc_, R0); dz = R1 - R0
        cells_ = [cell(dz[m]) for _, m in wins]
        ret_in = top_ret(R0[year <= 2020], R1[year <= 2020]); ret_out = top_ret(R0[year >= 2021], R1[year >= 2021])
        ok = (cells_[0][2] >= 2.0) and (cells_[1][2] >= 1.5) and (ret_in >= 90) and (ret_out >= 90)
        q6_pass[s] = ok
        say("| %.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %.0f%% / %.0f%% | %s |" % (
            s, cells_[0][1], cells_[0][2], cells_[1][1], cells_[1][2], cells_[3][1], cells_[3][2], cells_[4][1], cells_[4][2],
            cells_[5][1], cells_[5][2], cells_[6][1], cells_[6][2], ret_in, ret_out, "PASS" if ok else "FAIL"))
    # Q4 本だけで見た戦略 diff（希釈なし）
    Rc_, f_ = cut(C_MAIN, slip_usd=0.10); dz = np.where(f_ & hi_in, Rc_ - R0, 0.0)
    say("Q4 本のみ（希釈なし・s=0.10）: 在 %s／外 %s／2024-26 %s。" % (fmt(cell(dz[hi_in & (year <= 2020)])), fmt(cell(dz[hi_in & (year >= 2021)])), fmt(cell(dz[hi_in & (year >= 2024)]))))
    say()

    # ---- Q7 構造 ----
    say("## Q7. 構造（文脈・判定不使用）")
    mq = sub_m & (q1 == 3)
    say("- Q4 の risk==MIN_SL_W(%.1f) 比率 %.1f%%（Q1-3: %.1f%%）。Q4 の risk 中央値 %.2f USD（Q1-3 %.2f）、ft 中央値 %.3fR（Q1-3 %.3f）。" % (
        MIN_SL_W, 100 * (risk[mq] <= MIN_SL_W + 1e-9).mean(), 100 * (risk[sub_m & (q1 < 3)] <= MIN_SL_W + 1e-9).mean(),
        np.median(risk[mq]), np.median(risk[sub_m & (q1 < 3)]), np.median(ft[mq]), np.median(ft[sub_m & (q1 < 3)])))
    say("- Q4 の b 中央値 %.2f（Q1-3 %.2f）、勝率 %.1f%%（Q1-3 %.1f%%）、hold 中央値 %d（Q1-3 %d）、発動率 %.1f%%（Q1-3 %.1f%%）。" % (
        np.nanmedian(df.b.to_numpy()[mq]), np.nanmedian(df.b.to_numpy()[sub_m & (q1 < 3)]), 100 * (R0[mq] > 0).mean(), 100 * (R0[sub_m & (q1 < 3)] > 0).mean(),
        int(np.median(df.hold.to_numpy()[mq])), int(np.median(df.hold.to_numpy()[sub_m & (q1 < 3)])), 100 * fired[mq].mean(), 100 * fired[sub_m & (q1 < 3)].mean()))
    # 公正記帳の確認: SL 本の到達安値 vs −1+ft
    sl = (df.exit_reason == "SL").to_numpy() & fired & mq
    say("- 記帳の対称性: Q4 発動本のうち SL 決着 %d 本は原型 −1 で記帳（安値到達は −1+ft）、切りは −0.5 で記帳（安値到達は −0.5+ft）＝同じ規則。diff に記帳の贈り物なし。" % sl.sum())
    say()

    # ---- 判定 ----
    broken = (p_max > 0.05) or (q3_out[2] < 1.0) or (not q6_pass[0.10])
    survived = (p_max < 0.05) and (q3_out[2] >= 1.5) and all(v > 0 for v in means[7:]) and q6_pass[0.10]
    verdict = "broken" if broken else ("survived" if survived else "inconclusive")
    say("## 判定: **%s**" % verdict)
    say("- Q2 p_max %.3f（閾 0.05）／Q3 外（在境界固定）t %+.2f（broken<1.0・survived≥1.5）／Q4 上位 3 十分位 %s／Q6 s=0.10 基準 %s。" % (
        p_max, q3_out[2], "".join("+" if v > 0 else "-" for v in means[7:]), "PASS" if q6_pass[0.10] else "FAIL"))
    say("所要 %.0f 秒。" % (time.time() - t_start))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
