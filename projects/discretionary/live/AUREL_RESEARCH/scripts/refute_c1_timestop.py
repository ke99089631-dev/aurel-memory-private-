# -*- coding: utf-8 -*-
"""
AUREL 反証レーン — 17:30 [REFUTE] cycle1 で自分が残した反証「6 本目に開いている本を全部閉じる（時間切れ短縮／戻し後利確）は
RW 期待を全窓で上回る」を壊す。読取りのみ・発注なし・書き込みは AUREL_RESEARCH/data のみ。

機械仮説 H0（スクリプトを書く前に固定）:
  setup_engine._simulate は SL を「FEED_TOL(0.1USD) 手前に触れたら sl で約定」、TP を「FEED_TOL 先まで届いて tp で約定」と判定する。
  つまり紙の SL/TP 決着は、価格が実際に到達した境界より常に 0.1USD 不利に記帳される（決着 1 本あたり ft_i = 0.1/risk_i R）。
  価格がマルチンゲールなら E[境界到達R | cl_K] = cl_K、ゆえに E[R_final | cl_K] = cl_K − ft_i（TIME 決着は cl_288 なので ft なし）。
  → 「K 本目に開いている本を全部 cl_K で閉じる」の利得 d = cl_K − R_final は、情報ゼロでも期待値 +ft_i（≈ +0.026R）になる。
  17:30 の P2 RW 帰無は payoff を (u=b+ft, a=1−ft) の境界位置で払っていたので E_RW = 真の期待 + ft。超過が ft 分だけ水増しされていた。

事前固定の検定:
  Q1 公正化: R* = R_final + ft_i（SL/TP のみ）。e_i = cl_K − R*。H0: E[e]=0。U_K（K本目に未決着）全体と補集合（MFE_K≥0.5）で mean e・paired t。
      窓 = 在 2010-20 / 外 2021-26 / 2024-26 / 2025-26H1 / JST21-6。Bonferroni α = 0.05/(5窓×2集合) = 0.005。K=6 が主、K∈{1,2,3,12,24} は構造確認。
  Q2 TIME 除外版（TIME は ft なし・MAX_HOLD の切断があるので別掲）。
  Q3 時間切れ戦略としての採点: 「K=6 で未決着なら全部 cl_6 で成行クローズ」に滑り s∈{0,0.10,0.22} USD。diff・t・上位10%合計R の減少。
      H0 の下では s=0.10 で diff≈0（紙の決着 shortfall と成行滑りが同額）。
  Q4 17:30 P2 の再計算: θ_local は同じ推定、payoff を p·b − (1−p)·1 に修正した E_RW' で超過を再掲（畳んだ本／補集合／全部）。
  Q5 診断: cl_6 十分位ごとの mean e（全未決着）。マルチンゲールなら全十分位で ≈0。
判定（事前固定）:
  broken(mechanical) = Q1 で「全部」「補集合」とも 在・外 で Bonferroni 有意な正の e が無い、かつ Q3 の s=0.10 で 在・外・2024-26 の diff が t<2。
  inconclusive = 補集合の e が 在・外 とも Bonferroni 有意 → 研究レーンへ新仮説として渡す。
入力: data/c1_reaccel_paths_2010_2026.json ＋ data/refute_c4_scan_paths_2010_2026.json（b を結合）
出力: data/refute_c1_timestop.md
"""
import os, json, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE)
DATA = os.path.join(RES, "data")
C1 = os.path.join(DATA, "c1_reaccel_paths_2010_2026.json")
C4 = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(DATA, "refute_c1_timestop.md")
K0, T0 = 6, 0.5
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 2: return float("nan"), float("nan")
    se = d.std(ddof=1) / math.sqrt(n)
    t = d.mean() / se if se > 0 else float("nan")
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else float("nan")
    return t, p


def p_hit(x, a, u, th):
    if x <= -a: return 0.0
    if x >= u: return 1.0
    if abs(th) < 1e-9: return (x + a) / (a + u)
    s = lambda y: math.exp(-th * y)
    return (s(x) - s(-a)) / (s(u) - s(-a))


def fit_theta(X, A, U, target):
    lo, hi = -5.0, 5.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = sum(p_hit(x, a, u, mid) for x, a, u in zip(X, A, U))
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return 0.5 * (lo + hi)


def load():
    J = json.load(open(C1, encoding="utf-8")); c4 = json.load(open(C4, encoding="utf-8"))
    ft_abs = J["frozen"]["FEED_TOL"]
    aux = {t["entry_time"]: t for t in c4["trades"]}
    rows = []
    for t in J["trades"]:
        a = aux.get(t["entry_time"])
        rows.append({**{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")},
                     "mfe": t["mfe"], "cl": t["cl"], "b": a["b"] if a else np.nan})
    df = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)
    df["ft"] = ft_abs / df.risk
    df["shortfall"] = np.where(df.exit_reason == "TIME", 0.0, df.ft)   # 紙の決着が境界到達より不利に記帳された量 (R)
    df["Rstar"] = df.R + df.shortfall                                   # 公正化した最終R（境界到達R）
    df["a"] = 1 - df.ft; df["u"] = df.b + df.ft
    return df, J


def openK(df, K):
    unres = ((df.hold > K) & (df.mfe.map(len) > K)).to_numpy()
    mfeK = np.array([m[K] if ok else np.nan for m, ok in zip(df.mfe, unres)])
    clK = np.array([c[K] if ok else np.nan for c, ok in zip(df.cl, unres)])
    return unres, mfeK, clK


def windows(df):
    return (("在 2010-20", df[df.year <= 2020]), ("外 2021-26", df[df.year >= 2021]), ("2024-26", df[df.year >= 2024]),
            ("2025-26H1", df[df.year >= 2025]), ("JST21-6", df[(df.jh >= 21) | (df.jh <= 6)]))


def main():
    df, J = load()
    say("# AUREL [REFUTE] 「K 本目に開いている本を全部閉じる」時間切れ短縮の反証 — FEED_TOL 決着 shortfall の機械仮説  (入力 %d 本, c1 生成 %s)" % (len(df), J["generated"]))
    say("FEED_TOL=%.2f USD。ft=0.1/risk: 平均 %.4fR・中央値 %.4fR。TIME 決着 %d 本 (%.1f%%) は shortfall 0。" % (
        J["frozen"]["FEED_TOL"], df.ft.mean(), df.ft.median(), (df.exit_reason == "TIME").sum(), 100 * (df.exit_reason == "TIME").mean()))
    say("確認: SL 本の (R+1)·risk は全本 0.000 USD（sl で約定記帳）、TP 本の (R−b)·risk 中央値 0.000 USD（tp で約定記帳）。_simulate は SL を sl∓FEED_TOL 手前で・TP を tp±FEED_TOL 先で判定（setup_engine.py L148-154・読むだけ）。")
    say()

    # ---------- Q1 ----------
    say("## Q1. 公正化 e = cl_K − R*（R* = R_final + ft_i for SL/TP）。H0: E[e]=0 — Bonferroni α=0.05/10=0.005（K=6 主判定）")
    say("| 窓 | 集合 | n | mean d (素・17:30 の“全部畳む”) | mean ft | **mean e** | t | p | Bonferroni |")
    say("|---|---|---|---|---|---|---|---|---|")
    Q1 = {}
    for lab, g in windows(df):
        g = g.reset_index(drop=True); unres, mfeK, clK = openK(g, K0)
        d = clK - g.R.to_numpy(); e = clK - g.Rstar.to_numpy()
        for nm, m in (("全部", unres), ("補集合 MFE_6≥0.5", unres & (mfeK >= T0)), ("畳み MFE_6<0.5", unres & (mfeK < T0))):
            t, p = tstat(e[m]); Q1[(lab, nm)] = (e[m].mean(), t, p, int(m.sum()))
            say("| %s | %s | %d | %+.4f | %.4f | **%+.4f** | %+.2f | %.4f | %s |" % (
                lab, nm, m.sum(), d[m].mean(), g.ft.to_numpy()[m].mean(), e[m].mean(), t, p, "有意(+)" if p < 0.005 and e[m].mean() > 0 else "非有意"))
    say()
    say("### Q1b. K 格子（全部・mean e と t）— 構造確認")
    say("| K | 在 n / e / t | 外 n / e / t | 2024-26 n / e / t | 2025-26H1 n / e / t |"); say("|---|---|---|---|---|")
    for K in (1, 2, 3, 6, 12, 24):
        cells = []
        for lab, g in windows(df)[:4]:
            g = g.reset_index(drop=True); unres, mfeK, clK = openK(g, K)
            e = (clK - g.Rstar.to_numpy())[unres]; t, p = tstat(e)
            cells.append("%d / %+.4f / %+.2f" % (unres.sum(), e.mean(), t))
        say("| %d | %s |" % (K, " | ".join(cells)))
    say()

    # ---------- Q2 ----------
    say("## Q2. TIME 決着を除外（SL/TP のみ・shortfall=ft 一律）— K=6")
    say("| 窓 | 集合 | n | mean d | mean e | t | p |"); say("|---|---|---|---|---|---|---|")
    for lab, g in windows(df):
        g = g[g.exit_reason != "TIME"].reset_index(drop=True); unres, mfeK, clK = openK(g, K0)
        d = clK - g.R.to_numpy(); e = clK - g.Rstar.to_numpy()
        for nm, m in (("全部", unres), ("補集合", unres & (mfeK >= T0))):
            t, p = tstat(e[m]); say("| %s | %s | %d | %+.4f | %+.4f | %+.2f | %.4f |" % (lab, nm, m.sum(), d[m].mean(), e[m].mean(), t, p))
    say()

    # ---------- Q3 ----------
    say("## Q3. 戦略採点: K=6 で未決着なら全部 cl_6 で成行クローズ（滑り s USD）。diff = R_new − R_orig（全本）・上位10%合計R の減少")
    say("| 窓 | s USD | 閉じた本 | diff | t | p | 上位10% 合計R 原→新 (減少%) | 上位1% 原→新 |"); say("|---|---|---|---|---|---|---|---|")
    Q3 = {}
    for lab, g in windows(df)[:4]:
        g = g.reset_index(drop=True); unres, mfeK, clK = openK(g, K0); R0 = g.R.to_numpy()
        for s in (0.0, 0.10, 0.22):
            R1 = np.where(unres, clK - s / g.risk.to_numpy(), R0); dd = R1 - R0; t, p = tstat(dd)
            top10 = np.argsort(R0)[-max(1, len(R0) // 10):]; top1 = np.argsort(R0)[-max(1, len(R0) // 100):]
            Q3[(lab, s)] = (dd.mean(), t)
            say("| %s | %.2f | %d | %+.4f | %+.2f | %.4f | %+.0f→%+.0f (−%.0f%%) | %+.0f→%+.0f |" % (
                lab, s, unres.sum(), dd.mean(), t, p, R0[top10].sum(), R1[top10].sum(), 100 * (1 - R1[top10].sum() / R0[top10].sum()),
                R0[top1].sum(), R1[top1].sum()))
    say("（補集合だけ閉じる＝「+0.5R 到達後に戻した本を利確」版）")
    say("| 窓 | s USD | 閉じた本 | diff | t | 上位10% 減少% |"); say("|---|---|---|---|---|---|")
    for lab, g in windows(df)[:4]:
        g = g.reset_index(drop=True); unres, mfeK, clK = openK(g, K0); R0 = g.R.to_numpy(); m = unres & (mfeK >= T0)
        for s in (0.0, 0.10):
            R1 = np.where(m, clK - s / g.risk.to_numpy(), R0); dd = R1 - R0; t, p = tstat(dd)
            top10 = np.argsort(R0)[-max(1, len(R0) // 10):]
            say("| %s | %.2f | %d | %+.4f | %+.2f | −%.0f%% |" % (lab, s, m.sum(), dd.mean(), t, 100 * (1 - R1[top10].sum() / R0[top10].sum())))
    say()

    # ---------- Q4 ----------
    say("## Q4. 17:30 P2 の再計算: θ_local 同じ・payoff を p·b − (1−p)·1 に修正（旧 = p·u − (1−p)·a = 新 + ft）。超過 = 観測 d − (cl_K − E_RW')")
    say("| 窓 | θ_local | 畳み 超過 / t (旧) | 畳み 超過 / t (新) | 補集合 超過 / t (新) | 全部 超過 / t (新) |"); say("|---|---|---|---|---|---|")
    for lab, g in windows(df):
        g = g.reset_index(drop=True); unres, mfeK, clK = openK(g, K0)
        ok = unres & g.b.notna().to_numpy() & (g.a.to_numpy() > 0.3)
        X = clK[ok]; A = g.a.to_numpy()[ok]; Uu = g.u.to_numpy()[ok]
        th = fit_theta(X, A, Uu, int((g.R.to_numpy()[ok] > 0).sum()))
        def excess(m, old=False):
            o_ = (clK - g.R.to_numpy())[m]
            n_ = []
            for x, a, u, b in zip(clK[m], g.a.to_numpy()[m], g.u.to_numpy()[m], g.b.to_numpy()[m]):
                p = p_hit(x, a, u, th)
                E = p * u - (1 - p) * a if old else p * b - (1 - p) * 1.0
                n_.append(x - E)
            t, _ = tstat(o_ - np.array(n_)); return (o_ - np.array(n_)).mean(), t
        fo = ok & (mfeK < T0); co = ok & (mfeK >= T0)
        say("| %s | %+.3f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f |" % (lab, th, *excess(fo, True), *excess(fo), *excess(co), *excess(ok)))
    say()

    # ---------- Q5 ----------
    say("## Q5. 診断: cl_6 十分位ごとの mean e（全未決着・全期間）。マルチンゲールなら全十分位 ≈0")
    unres, mfeK, clK = openK(df, K0); e = clK - df.Rstar.to_numpy(); U = np.where(unres)[0]
    dec = pd.qcut(clK[U], 10, labels=False, duplicates="drop")
    say("| 十分位 | cl_6 範囲 | n | mean e | t | 補集合比率 |"); say("|---|---|---|---|---|---|")
    for q in np.unique(dec):
        idx = U[dec == q]; t, p = tstat(e[idx])
        say("| %d | [%+.2f,%+.2f] | %d | %+.4f | %+.2f | %.0f%% |" % (q, clK[idx].min(), clK[idx].max(), len(idx), e[idx].mean(), t, 100 * (mfeK[idx] >= T0).mean()))
    say()

    # ---------- 判定 ----------
    say("## 判定（事前固定の規則）")
    sig_all = [Q1[(w, "全部")][2] < 0.005 and Q1[(w, "全部")][0] > 0 for w in ("在 2010-20", "外 2021-26")]
    sig_comp = [Q1[(w, "補集合 MFE_6≥0.5")][2] < 0.005 and Q1[(w, "補集合 MFE_6≥0.5")][0] > 0 for w in ("在 2010-20", "外 2021-26")]
    q3ok = all(Q3[(w, 0.10)][1] < 2 for w in ("在 2010-20", "外 2021-26", "2024-26"))
    say("- Q1 全部: 在・外 Bonferroni 有意(+) = %s / %s" % tuple(sig_all))
    say("- Q1 補集合: 在・外 Bonferroni 有意(+) = %s / %s" % tuple(sig_comp))
    say("- Q3 s=0.10 で 在・外・2024-26 の t<2 = %s（t: %+.2f / %+.2f / %+.2f）" % (q3ok, Q3[("在 2010-20", 0.10)][1], Q3[("外 2021-26", 0.10)][1], Q3[("2024-26", 0.10)][1]))
    if all(sig_comp):
        v = "inconclusive（補集合に ft 超過が在・外とも残る → 研究レーンへ新仮説）"
    elif not any(sig_all) and q3ok:
        v = "broken（mechanical: FEED_TOL 決着 shortfall で説明）"
    else:
        v = "inconclusive"
    say("- 機械判定: **%s**" % v)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
