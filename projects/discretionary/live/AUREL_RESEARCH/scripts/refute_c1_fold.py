# -*- coding: utf-8 -*-
"""
AUREL 反証レーン — cycle1「非始動の早畳み」(K=6, T=0.5R) を壊す。読取りのみ・発注なし・書き込みは AUREL_RESEARCH/data のみ。

対象: data/c1_early_fold_result.md (2026-11-04 16:13)。在 diff +0.015 t+2.25 / 外 diff +0.010 t+1.28。
事前固定（このスクリプトを書く前に決めた・以後動かさない）:
  P0 事前固定の昇格条件 5 項目をそのまま採点（研究レーンの基準で既に落ちているか）。
  P1 プラセボ: 「K 本時点で未決着」の集合 U_K で、畳み条件 (MFE_K<T) の情報量を検定。
      (a) 全部畳む (b) 補集合 (MFE_K≥T) を畳む (c) ラベル置換 2000 回（畳み本数固定）
      (d) cl_K 十分位で層化した置換 — 「今いる位置 cl_K」以外に MFE_K が情報を持つか。これが主検定。
  P2 RW 帰無: 本ごとの a=1−ft, u=b+ft, x=cl_K から θ_local（U_K の勝率で推定）の吸収壁RWで E[R_final|cl_K] を閉形式計算。
      null diff_i = cl_K − E[R_final|cl_K]。観測 diff_i − null diff_i の paired t（畳んだ本）。θ=0 版も併記。
  P3 別分割: 在/外を入替（在=2016-26・外=2010-15）／偶数年・奇数年。
  P4 レジーム: 2024-26・2025-26H1・壁種・側・JST時間帯（7-12 / 13-20 / 21-6）。Bonferroni。
  P5 多重検定: 8 格子 (K×T) × 外サンプル → α=0.05/8。
  P6 コスト: 畳み出口は成行。畳み 1 本あたり追加滑り s∈{0,0.10,0.22,0.44} USD/risk で diff を再計算（TRIG_SPREAD=0.22）。
  P7 look-ahead / 建玉足: mfe[K], cl[K] は bar K 終値時点の情報のみ（構造確認）。bar0 の MFE は約定前を含み得る → MFE_K を offset1..K で再計算した版。
  P8 尻尾: 原型上位 10% / 5% / 1% の合計Rがルール後に何%残るか。
入力: data/c1_reaccel_paths_2010_2026.json（研究レーン 16:13）＋ data/refute_c4_scan_paths_2010_2026.json（b, x0, atr を entry_time で結合）
出力: data/refute_c1_fold.md
"""
import os, json, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE)
DATA = os.path.join(RES, "data")
C1 = os.path.join(DATA, "c1_reaccel_paths_2010_2026.json")
C4 = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(DATA, "refute_c1_fold.md")
COST = 0.56; K0, T0 = 6, 0.5; NPERM = 2000; SEED = 20261104
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def p_hit(x, a, u, th):
    if x <= -a: return 0.0
    if x >= u: return 1.0
    if abs(th) < 1e-9: return (x + a) / (a + u)
    s = lambda y: math.exp(-th * y)
    return (s(x) - s(-a)) / (s(u) - s(-a))


def e_final(x, a, u, th):
    p = p_hit(x, a, u, th)
    return p * u - (1 - p) * a


def fit_theta(X, A, U, target):
    lo, hi = -5.0, 5.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = sum(p_hit(x, a, u, mid) for x, a, u in zip(X, A, U))
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return 0.5 * (lo + hi)


def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 2: return float("nan"), float("nan")
    se = d.std(ddof=1) / math.sqrt(n)
    t = d.mean() / se if se > 0 else float("nan")
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else float("nan")
    return t, p


def maxdd(r):
    cum = np.cumsum(r); peak = np.maximum.accumulate(np.concatenate([[0.0], cum]))[1:]
    return float((cum - peak).min()) if len(r) else 0.0


def load():
    J = json.load(open(C1, encoding="utf-8")); c4 = json.load(open(C4, encoding="utf-8"))
    ft_abs = J["frozen"]["FEED_TOL"]
    aux = {t["entry_time"]: t for t in c4["trades"]}
    rows = []
    for t in J["trades"]:
        a = aux.get(t["entry_time"])
        rows.append({**{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")},
                     "mfe": t["mfe"], "cl": t["cl"], "mae": t["mae"],
                     "b": a["b"] if a else np.nan, "x0": a["x0"] if a else np.nan, "atr": a["atr"] if a else np.nan,
                     "mfe_bar0": a["mfe_bar0"] if a else np.nan})
    df = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)
    df["ft"] = ft_abs / df.risk; df["a"] = 1 - df.ft; df["u"] = df.b + df.ft
    return df, J


def with_rule(df, K, T, mfe_from1=False):
    """畳みフラグ・畳み時R(cl_K)・MFE_K を列に。未決着= hold>K かつ path が K まである。"""
    unres = (df.hold > K) & (df.mfe.map(len) > K)
    mfeK = np.array([(max(m[1:K + 1]) if mfe_from1 else m[K]) if ok else np.nan for m, ok in zip(df.mfe, unres)])
    clK = np.array([c[K] if ok else np.nan for c, ok in zip(df.cl, unres)])
    fold = unres.to_numpy() & (mfeK < T)
    return unres.to_numpy(), mfeK, clK, fold


def summary(df, K, T, slip=0.0, mfe_from1=False):
    unres, mfeK, clK, fold = with_rule(df, K, T, mfe_from1)
    R0 = df.R.to_numpy(); R1 = np.where(fold, clK - slip / df.risk.to_numpy(), R0)
    d = R1 - R0; t, p = tstat(d)
    net0 = R0 - COST / df.risk.to_numpy(); net1 = R1 - COST / df.risk.to_numpy()
    out = {"n": len(df), "folded": int(fold.sum()), "diff": d.mean(), "t": t, "p": p, "dd0": maxdd(net0), "dd1": maxdd(net1)}
    for q in (10, 5, 1):
        top = np.argsort(R0)[-max(1, len(R0) * q // 100):]
        out["top%d" % q] = (R0[top].sum(), R1[top].sum(), int(fold[top].sum()))
    return out, unres, mfeK, clK, fold, d


def main():
    rng = np.random.default_rng(SEED)
    df, J = load()
    IS = df[df.year <= 2020].reset_index(drop=True); OOS = df[df.year >= 2021].reset_index(drop=True)
    say("# AUREL [REFUTE] cycle1 非始動の早畳み (K=%d, T=%.1f) — 反証  (入力 %d 本, c1 生成 %s)" % (K0, T0, len(df), J["generated"]))
    say("b/x0/atr 結合: %d/%d 本に b あり" % (df.b.notna().sum(), len(df))); say()

    # ---------- P0 事前固定の昇格条件 ----------
    say("## P0. 研究レーン自身の事前固定 5 条件の採点（K=6,T=0.5）")
    sI, *_ = summary(IS, K0, T0); sO, *_ = summary(OOS, K0, T0)
    say("| 条件 | 在 | 外 | 判定 |"); say("|---|---|---|---|")
    say("| diff>0 | %+.4f | %+.4f | %s |" % (sI["diff"], sO["diff"], "PASS" if sI["diff"] > 0 and sO["diff"] > 0 else "FAIL"))
    say("| 在 t≥2.0 ／ 外 t≥1.5 | t=%+.2f | t=%+.2f | %s |" % (sI["t"], sO["t"], "PASS" if sI["t"] >= 2 and sO["t"] >= 1.5 else "FAIL（外 t<1.5）"))
    rI = 100 * (1 - sI["top10"][1] / sI["top10"][0]); rO = 100 * (1 - sO["top10"][1] / sO["top10"][0])
    say("| 上位10%%合計R 減少≤10%% | −%.1f%% (畳まれ %d) | −%.1f%% (畳まれ %d) | %s |" % (rI, sI["top10"][2], rO, sO["top10"][2], "PASS" if rI <= 10 and rO <= 10 else "FAIL"))
    say("| 最大DD 悪化しない | %.1f→%.1f | %.1f→%.1f | %s |" % (sI["dd0"], sI["dd1"], sO["dd0"], sO["dd1"], "PASS" if sI["dd1"] >= sI["dd0"] and sO["dd1"] >= sO["dd0"] else "FAIL"))
    say("（再現確認: 研究レーンの md と diff/t/畳み本数が一致 → 在 %d 本 / 外 %d 本）" % (sI["folded"], sO["folded"])); say()

    # ---------- P8 尻尾 ----------
    say("## P8. 尻尾の削り（原型上位 q% の合計R → ルール後）")
    say("| 標本 | top10% | top5% | top1% |"); say("|---|---|---|---|")
    for lab, s in (("在", sI), ("外", sO)):
        say("| %s | %+.0f→%+.0f (%d本畳まれ) | %+.0f→%+.0f (%d) | %+.0f→%+.0f (%d) |" % (lab, *s["top10"], *s["top5"], *s["top1"]))
    say()

    # ---------- P1 プラセボ ----------
    say("## P1. プラセボ: 畳み条件 MFE_K<T に情報があるか（U_K = K本時点で未決着の本・d_i = cl_K − R_final）")
    say("| 標本 | U_K n | 畳み n | 畳んだ本 mean d | 補集合 mean d | 全部畳む mean d | 置換 p(非層化) | 置換 p(cl_K 十分位層化) | 層化期待 mean d |")
    say("|---|---|---|---|---|---|---|---|---|")
    P1 = {}
    for lab, g in (("在 2010-20", IS), ("外 2021-26", OOS), ("2024-26", df[df.year >= 2024].reset_index(drop=True)),
                   ("2025-26H1", df[df.year >= 2025].reset_index(drop=True)),
                   ("JST21-6 (P4 で有意の1セル)", df[(df.jh >= 21) | (df.jh <= 6)].reset_index(drop=True))):
        s, unres, mfeK, clK, fold, d = summary(g, K0, T0)
        U = np.where(unres)[0]; dU = (clK - g.R.to_numpy())[U]; fU = fold[U]; nf = int(fU.sum())
        obs = dU[fU].mean(); comp = dU[~fU].mean(); allm = dU.mean()
        # 非層化置換
        cnt = 0
        for _ in range(NPERM):
            idx = rng.choice(len(dU), nf, replace=False)
            if dU[idx].mean() >= obs: cnt += 1
        p_un = (cnt + 1) / (NPERM + 1)
        # cl_K 十分位層化置換
        xU = clK[U]; dec = pd.qcut(xU, 10, labels=False, duplicates="drop")
        strata = [np.where(dec == q)[0] for q in np.unique(dec)]
        nfold_s = [int(fU[s_].sum()) for s_ in strata]
        exp_strat = sum(dU[s_].mean() * k for s_, k in zip(strata, nfold_s)) / nf
        cnt = 0
        for _ in range(NPERM):
            tot = 0.0
            for s_, k in zip(strata, nfold_s):
                if k: tot += dU[rng.choice(s_, k, replace=False)].sum()
            if tot / nf >= obs: cnt += 1
        p_st = (cnt + 1) / (NPERM + 1)
        P1[lab] = (obs, comp, allm, p_un, p_st, exp_strat, nf)
        say("| %s | %d | %d | %+.4f | %+.4f | %+.4f | %.4f | %.4f | %+.4f |" % (lab, len(U), nf, obs, comp, allm, p_un, p_st, exp_strat))
    say("（読み方: 全部畳む・補集合も正なら、情報は MFE_K でなく「早く降りる」こと自体。層化置換 p が大きければ MFE_K は cl_K の代理に過ぎない）"); say()

    # cl_K 十分位 × MFE_K<T の有無 で d の平均（在）
    say("### P1b. 在: cl_K 十分位ごとの mean d（畳み条件あり vs なし）— 同じ位置にいて MFE_K だけ違う本の比較")
    s, unres, mfeK, clK, fold, d = summary(IS, K0, T0)
    U = np.where(unres)[0]; dU = (clK - IS.R.to_numpy())[U]; fU = fold[U]; xU = clK[U]
    dec = pd.qcut(xU, 10, labels=False, duplicates="drop")
    say("| 十分位 | cl_K 範囲 | n畳み / mean d | n非畳み / mean d | 差 | 差の t |"); say("|---|---|---|---|---|---|")
    for q in np.unique(dec):
        m = dec == q; a_ = dU[m & fU]; b_ = dU[m & ~fU]
        if len(a_) and len(b_):
            se = math.sqrt(a_.var(ddof=1) / len(a_) + b_.var(ddof=1) / len(b_)); tt = (a_.mean() - b_.mean()) / se if se > 0 else float("nan")
            say("| %d | [%+.2f,%+.2f] | %d / %+.4f | %d / %+.4f | %+.4f | %+.2f |" % (q, xU[m].min(), xU[m].max(), len(a_), a_.mean(), len(b_), b_.mean(), a_.mean() - b_.mean(), tt))
        else:
            say("| %d | [%+.2f,%+.2f] | %d / %s | %d / %s | – | – |" % (q, xU[m].min(), xU[m].max(), len(a_), ("%+.4f" % a_.mean()) if len(a_) else "–", len(b_), ("%+.4f" % b_.mean()) if len(b_) else "–"))
    say()

    # ---------- P2 RW 帰無 ----------
    say("## P2. 吸収壁RW帰無: null diff_i = cl_K − E_RW[R_final | cl_K]（θ は U_K の勝率で窓内推定） vs 観測 diff_i（畳んだ本・paired t）")
    say("| 標本 | 畳み n | θ_local(U_K) | 観測 mean diff | RW期待 mean diff(θ_local) | 超過 | t | p | RW期待(θ=0) | 超過(θ=0) | t(θ=0) | 補集合 超過 / t | 全部畳む 超過 / t |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    P2 = {}
    for lab, g in (("在 2010-20", IS), ("外 2021-26", OOS), ("2024-26", df[df.year >= 2024].reset_index(drop=True)),
                   ("2025-26H1", df[df.year >= 2025].reset_index(drop=True)),
                   ("JST21-6", df[(df.jh >= 21) | (df.jh <= 6)].reset_index(drop=True))):
        s, unres, mfeK, clK, fold, d = summary(g, K0, T0)
        ok = unres & g.b.notna().to_numpy() & (g.a.to_numpy() > 0.3)
        X = clK[ok]; A = g.a.to_numpy()[ok]; Uu = g.u.to_numpy()[ok]
        th = fit_theta(X, A, Uu, int((g.R.to_numpy()[ok] > 0).sum()))
        f = fold & ok
        obs = (clK - g.R.to_numpy())[f]
        null = np.array([x - e_final(x, a, u, th) for x, a, u in zip(clK[f], g.a.to_numpy()[f], g.u.to_numpy()[f])])
        null0 = np.array([x - e_final(x, a, u, 0.0) for x, a, u in zip(clK[f], g.a.to_numpy()[f], g.u.to_numpy()[f])])
        t1, p1 = tstat(obs - null); t0, p0 = tstat(obs - null0)
        P2[lab] = (th, obs.mean(), null.mean(), t1, p1)
        # 補集合（MFE_K≥T・未決着）と 全未決着 に同じ RW 帰無を当てる → 超過が MFE 条件に固有か
        ex = {}
        for nm, msk in (("comp", ok & unres & ~fold), ("all", ok & unres)):
            o_ = (clK - g.R.to_numpy())[msk]
            n_ = np.array([x - e_final(x, a, u, th) for x, a, u in zip(clK[msk], g.a.to_numpy()[msk], g.u.to_numpy()[msk])])
            tt, _ = tstat(o_ - n_); ex[nm] = ((o_ - n_).mean(), tt)
        say("| %s | %d | %+.3f | %+.4f | %+.4f | %+.4f | %+.2f | %.4f | %+.4f | %+.4f | %+.2f | %+.4f / %+.2f | %+.4f / %+.2f |" % (
            lab, f.sum(), th, obs.mean(), null.mean(), obs.mean() - null.mean(), t1, p1, null0.mean(), obs.mean() - null0.mean(), t0,
            *ex["comp"], *ex["all"]))
    say("（θ=0 なら E[R_final|cl_K]=cl_K で null diff≡0 → 観測 diff の素の t と一致するはず。θ<0 なら RW だけで diff>0 が出る）"); say()

    # ---------- P3 別分割 ----------
    say("## P3. 別の在/外分割（K=6,T=0.5）")
    say("| 分割 | n | 畳み | diff | t | p | 上位10% 減少 | DD 変化 |"); say("|---|---|---|---|---|---|---|---|")
    splits = {"在=2016-26 (入替)": df.year >= 2016, "外=2010-15 (入替)": df.year <= 2015,
              "偶数年": df.year % 2 == 0, "奇数年": df.year % 2 == 1,
              "2010-13": df.year <= 2013, "2014-17": (df.year >= 2014) & (df.year <= 2017), "2018-21": (df.year >= 2018) & (df.year <= 2021),
              "2022-26": df.year >= 2022}
    for lab, m in splits.items():
        s, *_ = summary(df[m].reset_index(drop=True), K0, T0)
        say("| %s | %d | %d | %+.4f | %+.2f | %.4f | −%.0f%% | %.0f→%.0f |" % (lab, s["n"], s["folded"], s["diff"], s["t"], s["p"],
                                                                     100 * (1 - s["top10"][1] / s["top10"][0]), s["dd0"], s["dd1"]))
    say()

    # ---------- P4 レジーム ----------
    say("## P4. レジーム部分集合（K=6,T=0.5・全期間）— Bonferroni α=0.05/%d" % 9)
    say("| 部分集合 | n | 畳み | diff | t | p | 上位10% 減少 |"); say("|---|---|---|---|---|---|---|")
    jh = df.jh
    subs = {"2024-26": df.year >= 2024, "2025-26H1": df.year >= 2025,
            "outer": df.wall_kind == "outer", "mid": df.wall_kind != "outer", "BUY": df.side == "BUY", "SELL": df.side == "SELL",
            "JST 7-12": (jh >= 7) & (jh <= 12), "JST 13-20": (jh >= 13) & (jh <= 20), "JST 21-6": (jh >= 21) | (jh <= 6)}
    for lab, m in subs.items():
        s, *_ = summary(df[m].reset_index(drop=True), K0, T0)
        say("| %s | %d | %d | %+.4f | %+.2f | %.4f%s | −%.0f%% |" % (lab, s["n"], s["folded"], s["diff"], s["t"], s["p"],
                                                              " **" if s["p"] < 0.05 / 9 and s["diff"] > 0 else "", 100 * (1 - s["top10"][1] / s["top10"][0])))
    say()
    # atr/risk 分位（14:25 の宿題 (e)）
    say("### P4b. atr/risk 四分位（建玉足で確定・全期間）")
    q = pd.qcut(df.atr / df.risk, 4, labels=False)
    say("| 分位 | n | 畳み | diff | t | p |"); say("|---|---|---|---|---|---|")
    for qq in range(4):
        s, *_ = summary(df[q == qq].reset_index(drop=True), K0, T0)
        say("| Q%d | %d | %d | %+.4f | %+.2f | %.4f |" % (qq + 1, s["n"], s["folded"], s["diff"], s["t"], s["p"]))
    say()

    # ---------- P5 多重検定 ----------
    say("## P5. 8 格子 (K×T) × 外サンプル — Bonferroni α=0.05/8=%.4f" % (0.05 / 8))
    say("| K | T | 在 diff / t / p | 外 diff / t / p | 外 Bonferroni |"); say("|---|---|---|---|---|")
    for K in (3, 6, 12, 24):
        for T in (0.3, 0.5):
            a_, *_ = summary(IS, K, T); b_, *_ = summary(OOS, K, T)
            say("| %d | %.1f | %+.4f / %+.2f / %.4f | %+.4f / %+.2f / %.4f | %s |" % (K, T, a_["diff"], a_["t"], a_["p"], b_["diff"], b_["t"], b_["p"],
                                                                                 "有意" if b_["p"] < 0.05 / 8 and b_["diff"] > 0 else "非有意"))
    say()

    # ---------- P6 コスト ----------
    say("## P6. 畳み出口の追加滑り s (USD/risk・畳んだ本だけに課す) — diff (K=6,T=0.5)")
    say("| s USD | 在 diff / t | 外 diff / t | 2024-26 diff / t | 畳み 1 本あたり R 換算(中央値 risk) |"); say("|---|---|---|---|---|")
    R24 = df[df.year >= 2024].reset_index(drop=True); med_risk = float(df.risk.median())
    for sl in (0.0, 0.10, 0.22, 0.44):
        a_, *_ = summary(IS, K0, T0, slip=sl); b_, *_ = summary(OOS, K0, T0, slip=sl); c_, *_ = summary(R24, K0, T0, slip=sl)
        say("| %.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %.3fR |" % (sl, a_["diff"], a_["t"], b_["diff"], b_["t"], c_["diff"], c_["t"], sl / med_risk))
    say("（risk 中央値 %.2f USD。TRIG_SPREAD=%.2f）" % (med_risk, J["frozen"]["TRIG_SPREAD"])); say()

    # ---------- P7 look-ahead / 建玉足 ----------
    say("## P7. look-ahead と建玉足")
    say("- 構造: 畳み判定は mfe[K], cl[K]（bar K の高値/終値まで）。hold>K は exit bar index>K で bar K 内の決着を含まない → look-ahead なし。")
    say("- 建玉足(bar0)の MFE は約定前を含み得る（逆指値）。キャッシュの mfe は累積最大なので bar0 を厳密には除けない。上限評価: 未決着かつ "
        "mfe[K]==mfe[0]≥T（T 到達が bar0 のみで以後更新なし）の本を“bar0 除外なら畳まれる”とみなして全部畳む。")
    for lab, g in (("在", IS), ("外", OOS)):
        s1, unres, mfeK, clK, fold, d = summary(g, K0, T0)
        m0 = np.array([m[0] for m in g.mfe]); bar0_only = unres & ~fold & (np.isclose(m0, mfeK)) & (m0 >= T0)
        fold2 = fold | bar0_only
        R0 = g.R.to_numpy(); R1 = np.where(fold2, clK, R0); t2, _ = tstat(R1 - R0)
        say("  - %s: bar0 のみで T 到達・以後更新なし %d 本（未決着 %d 中, c4 mfe_bar0≥T は %d 本）。それも畳むと diff %+.4f→%+.4f (t %+.2f→%+.2f)" % (
            lab, bar0_only.sum(), unres.sum(), int(((g.mfe_bar0 >= T0) & unres).sum()), s1["diff"], (R1 - R0).mean(), s1["t"], t2))
    say("- survivorship: scan closed 全本 (TP/SL/TIME) 使用。TIME %d 本含む。" % (df.exit_reason == "TIME").sum()); say()

    # ---------- 判定 ----------
    say("## 判定")
    ok_is = P1["在 2010-20"][4] < 0.05; ok_oos = P1["外 2021-26"][4] < 0.05
    say("- P0: 事前固定 5 条件のうち FAIL あり（外 t<1.5・上位10% の削りが上限 10% を大きく超過）→ 研究レーン自身の基準で昇格不可。")
    say("- P1 層化置換 p: 在 %.4f / 外 %.4f / 2024-26 %.4f / 2025-26H1 %.4f / JST21-6 %.4f" % (
        P1["在 2010-20"][4], P1["外 2021-26"][4], P1["2024-26"][4], P1["2025-26H1"][4], P1["JST21-6 (P4 で有意の1セル)"][4]))
    say("- P1 非層化置換 p（畳んだ本 vs 同数ランダム畳み）: 在 %.4f / 外 %.4f / JST21-6 %.4f" % (
        P1["在 2010-20"][3], P1["外 2021-26"][3], P1["JST21-6 (P4 で有意の1セル)"][3]))
    say("- P2 RW超過 t: 在 %+.2f / 外 %+.2f / 2024-26 %+.2f / 2025-26H1 %+.2f" % (P2["在 2010-20"][3], P2["外 2021-26"][3], P2["2024-26"][3], P2["2025-26H1"][3]))
    verdict = "broken" if not (ok_is and ok_oos) else "inconclusive"
    say("- 機械判定: **%s**" % verdict)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
