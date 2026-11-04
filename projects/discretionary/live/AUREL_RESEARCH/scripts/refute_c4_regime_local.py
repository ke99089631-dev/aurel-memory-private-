# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 補助 — CHARTER D2（2026-11-04 09:52 追加）対応の再検定。
D2: 16年一括の θ/平均R を edge の結論に使わない。優位はレジーム窓で測る。
→ 08:50 の C4 検定は θ を 16 年 pooled で 1 つ推定し、時代別は「θ 固定・部分集合」だった。
   ここでは各窓で θ を**その窓だけで**推定し直し、C4 の両方向（P(沈み|TP)・P(TP|沈み)）を窓内で検定する。
   窓: 2010-20 / 2021-23 / 2024-26 / 2025-26H1（最も近年）。
   さらに各窓の素の勝率・平均R(gross)・θ_local を“文脈”として並べる（edge 判定ではなく、D2 の「近年窓で測る」の実践）。
読取りのみ。入力 = data/refute_c4_scan_paths_2010_2026.json。出力 = data/refute_c4_regime_local.md。
事前固定: 対象定義・沈み定義・α=0.05/6 は 08:50 と同一。窓は 4 つ → 窓 Bonferroni は 0.05/4=0.0125 も併記。
"""
import os, json, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE)
DATA = os.path.join(RES, "data")
PATHS_JSON = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(DATA, "refute_c4_regime_local.md")
ALPHA6 = 0.05 / 6; ALPHA4 = 0.05 / 4
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def p_hit(x, a, u, th):
    if x <= -a: return 0.0
    if x >= u: return 1.0
    if abs(th) < 1e-9: return (x + a) / (a + u)
    s = lambda y: math.exp(-th * y)
    return (s(x) - s(-a)) / (s(u) - s(-a))


def p_dip_given_tp(x0, a, u, th, d=0.5):
    pT = p_hit(x0, a, u, th)
    if pT <= 0: return float("nan")
    if x0 <= -d: return 1.0
    return (1.0 - p_hit(x0, d, u, th)) * p_hit(-d, a, u, th) / pT


def fit_theta(df):
    target = int((df.R > 0).sum()); lo, hi = -5.0, 5.0
    X = df.x0.to_numpy(); A = (1.0 - df.ft).to_numpy(); U = (df.b + df.ft).to_numpy()
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = sum(p_hit(x, a, u, mid) for x, a, u in zip(X, A, U))
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return 0.5 * (lo + hi)


def pb(obs, ps):
    ok = ~np.isnan(ps); ps = ps[ok]; obs = np.asarray(obs)[ok]
    k = int(obs.sum()); n = len(ps); mu = ps.sum(); var = (ps * (1 - ps)).sum()
    z = (k - mu) / math.sqrt(var) if var > 0 else float("nan")
    pv = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))) if not np.isnan(z) else float("nan")
    return k, n, mu / n if n else float("nan"), z, pv


def row(lab, k, n, exp, z, pv):
    say("| %-18s | %5d | %5d | %5.1f%% | %5.1f%% | %+5.1fpt | %+6.2f | %.4f |" % (lab, n, k, 100 * k / n, 100 * exp, 100 * (k / n - exp), z, pv))


def main():
    J = json.load(open(PATHS_JSON, encoding="utf-8"))
    df = pd.DataFrame(J["trades"]); df["ft"] = J["frozen"]["FEED_TOL"] / df.risk
    df["ym"] = pd.to_datetime(df.entry_time, unit="s", utc=True)
    say("# AUREL [REFUTE] C4 — D2 対応: 窓ごとに θ を局所推定して再検定  (入力 %d 本, 生成 %s)" % (len(df), J["generated"]))
    say("α: 08:50 踏襲 0.05/6=%.4f ／ 窓4 Bonferroni 0.05/4=%.4f" % (ALPHA6, ALPHA4)); say()
    wins = {"2010-20": df.year <= 2020, "2021-23": (df.year >= 2021) & (df.year <= 2023),
            "2024-26": df.year >= 2024, "2025-26H1": df.year >= 2025, "全体(参考のみ・D2)": df.year >= 0}
    say("## 0. 窓ごとの素の数字（文脈。D2: 全体行は幾何検定の母数としてのみ）")
    say("| 窓 | closed n | 勝率 | 平均R gross | TP/SL/TIME | θ_local(hold≥1,x0) |"); say("|---|---|---|---|---|---|")
    TH = {}
    for lab, m in wins.items():
        g = df[m]; sub = g[(g.hold >= 1) & ((1 - g.ft) > 0.5)]
        TH[lab] = fit_theta(sub)
        ex = g.exit.value_counts()
        say("| %s | %d | %.1f%% | %+.3f | %d/%d/%d | %+.3f |" % (lab, len(g), 100 * (g.R > 0).mean(), g.R.mean(),
                                                            ex.get("TP", 0), ex.get("SL", 0), ex.get("TIME", 0), TH[lab]))
    say()
    say("## 1. 順方向 P(建玉足後に −0.5R 沈み | TP 勝ち・hold≥1・a>0.5) — θ は窓内で推定")
    say("| 窓 | n | 沈みk | 観測 | 期待(局所θ) | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    fwd = {}
    for lab, m in wins.items():
        g = df[m]; sub = g[(g.hold >= 1) & ((1 - g.ft) > 0.5)]; w = sub[(sub.R > 0) & (sub.exit == "TP")]
        ps = np.array([p_dip_given_tp(x, a, u, TH[lab]) for x, a, u in zip(w.x0, 1 - w.ft, w.b + w.ft)])
        k, n, exp, z, pv = pb(w.mae1.to_numpy() >= 0.5, ps); fwd[lab] = (z, pv); row(lab, k, n, exp, z, pv)
    say()
    say("## 2. 逆方向（使える向き） P(TP | 建玉足後に −0.5R 沈んだ) — θ は窓内で推定・TIME は非TP")
    say("| 窓 | n | TPk | 観測 | 期待(局所θ) | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    rev = {}
    for lab, m in wins.items():
        g = df[m]; sub = g[(g.hold >= 1) & ((1 - g.ft) > 0.5)]; dp = sub[sub.mae1 >= 0.5]
        ps = np.array([p_hit(-0.5, a, u, TH[lab]) for a, u in zip(1 - dp.ft, dp.b + dp.ft)])
        k, n, exp, z, pv = pb((dp.exit == "TP").to_numpy(), ps); rev[lab] = (z, pv); row(lab, k, n, exp, z, pv)
    say()
    say("## 3. 逆方向・θ=0 固定（窓の勝率に合わせない素の無記憶RW）")
    say("| 窓 | n | TPk | 観測 | 期待(θ=0) | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    for lab, m in wins.items():
        g = df[m]; sub = g[(g.hold >= 1) & ((1 - g.ft) > 0.5)]; dp = sub[sub.mae1 >= 0.5]
        ps = np.array([p_hit(-0.5, a, u, 0.0) for a, u in zip(1 - dp.ft, dp.b + dp.ft)])
        k, n, exp, z, pv = pb((dp.exit == "TP").to_numpy(), ps); row(lab, k, n, exp, z, pv)
    say()
    say("## 4. 沈んだ本 vs 沈まなかった本の平均R（窓別・gross）")
    say("| 窓 | 沈み n / 平均R | 非沈み n / 平均R |"); say("|---|---|---|")
    for lab, m in wins.items():
        g = df[m]; sub = g[(g.hold >= 1) & ((1 - g.ft) > 0.5)]; d1 = sub[sub.mae1 >= 0.5]; d0 = sub[sub.mae1 < 0.5]
        say("| %s | %d / %+.3f | %d / %+.3f |" % (lab, len(d1), d1.R.mean(), len(d0), d0.R.mean()))
    say()
    recent = [l for l in wins if l in ("2021-23", "2024-26", "2025-26H1")]
    surv_f = [l for l in recent if fwd[l][1] < ALPHA4 and fwd[l][0] > 0]
    surv_r = [l for l in recent if rev[l][1] < ALPHA4 and rev[l][0] > 0]
    say("## 判定（近年窓で局所θに対し正方向に Bonferroni(窓4) 有意な窓）: 順方向 %s ／ 逆方向 %s" % (surv_f or "なし", surv_r or "なし"))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
