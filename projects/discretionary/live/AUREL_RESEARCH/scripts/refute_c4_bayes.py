# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 補助 — cycle0 C4 を「使える向き」で検定する。
主スクリプト refute_c4_scanpath.py は P(沈み | 勝ち) を見る。だが出口ルールに使えるのは逆向き
  P(勝ち | 建玉足の後で −0.5R まで沈んだ)
である。帰無(無記憶 RW・ドリフト θ)では、−0.5R に居る時点からの TP 到達確率は
  p_hit(−0.5, a=1−ft, u=b+ft, θ)
で、x0 にも建玉足にも依存しない。観測した沈み本の勝率がこれを Bonferroni 後も上回れば「沈みに情報あり」。
読取りのみ。入力 = data/refute_c4_scan_paths_2010_2026.json（主スクリプトが生成）。出力 = data/refute_c4_bayes_result.md。

事前固定: 対象 = hold≥1 かつ a>0.5 の全 closed 本。沈み = mae1≥0.5（offset1..exit の最大逆行）。
  主検定: 沈み本のうち exit=TP の割合 vs Σ p_hit(−0.5,a_i,u_i,θ)/n（Poisson-binomial z・両側）。TIME 決着は非TP として数える(保守側)。
  θ = 主スクリプトと同じ（hold≥1・x0 出発・勝率一致）。α = 0.05/6（前回の多重検定枠を踏襲）。
  副: TIME を除外した版／θ=0／時代×壁種（Bonferroni 6）／「沈まなかった本」の勝率 vs RW（対照）。
"""
import os, sys, json, math, collections
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE)
DATA = os.path.join(RES, "data")
PATHS_JSON = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(DATA, "refute_c4_bayes_result.md")
ALPHA = 0.05 / 6
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def p_hit(x, a, u, th):
    if x <= -a: return 0.0
    if x >= u: return 1.0
    if abs(th) < 1e-9: return (x + a) / (a + u)
    s = lambda y: math.exp(-th * y)
    return (s(x) - s(-a)) / (s(u) - s(-a))


def fit_theta(df, xcol):
    target = int((df.R > 0).sum()); lo, hi = -5.0, 5.0
    X = df[xcol].to_numpy(); A = (1.0 - df.ft).to_numpy(); U = (df.b + df.ft).to_numpy()
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = sum(p_hit(x, a, u, mid) for x, a, u in zip(X, A, U))
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return 0.5 * (lo + hi)


def pb_test(obs, ps, lab):
    k = int(obs.sum()); n = len(ps); mu = ps.sum(); var = (ps * (1 - ps)).sum()
    z = (k - mu) / math.sqrt(var) if var > 0 else float("nan")
    pv = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))) if not np.isnan(z) else float("nan")
    r = {"lab": lab, "n": n, "k": k, "obs": k / n if n else float("nan"), "exp": mu / n if n else float("nan"), "z": z, "p": pv}
    say("| %-24s | %5d | %5d | %5.1f%% | %5.1f%% | %+5.1fpt | %+6.2f | %.4f |" % (
        r["lab"], r["n"], r["k"], 100 * r["obs"], 100 * r["exp"], 100 * (r["obs"] - r["exp"]), r["z"], r["p"]))
    return r


def main():
    J = json.load(open(PATHS_JSON, encoding="utf-8"))
    ft_abs = J["frozen"]["FEED_TOL"]
    df = pd.DataFrame(J["trades"]); df["ft"] = ft_abs / df.risk
    df["a"] = 1.0 - df.ft; df["u"] = df.b + df.ft
    df["era"] = np.where(df.year <= 2020, "2010-20", np.where(df.year <= 2023, "2021-23", "2024-26"))
    say("# AUREL [REFUTE] cycle0 C4 逆向き検定 P(勝ち | 建玉足後に −0.5R 沈み) vs 無記憶RW")
    say("入力 %s (generated %s)  closed n=%d" % (os.path.basename(PATHS_JSON), J["generated"], len(df)))
    sub = df[(df.hold >= 1) & (df.a > 0.5)].copy()
    th = fit_theta(sub, "x0")
    say("対象 hold≥1・a>0.5: n=%d  exit=%s  θ(x0出発)=%.3f" % (len(sub), dict(collections.Counter(sub.exit)), th))
    dip = sub[sub.mae1 >= 0.5]; nodip = sub[sub.mae1 < 0.5]
    say("沈み本(mae1≥0.5) n=%d  exit=%s ／ 沈まず n=%d exit=%s" % (len(dip), dict(collections.Counter(dip.exit)), len(nodip), dict(collections.Counter(nodip.exit))))
    say()
    say("## 主検定: 沈み本の TP 率 vs RW p_hit(−0.5,a,u,θ)（TIME は非TP）")
    say("| 基準 | n | TP k | 観測 | 期待 | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    ps = np.array([p_hit(-0.5, a, u, th) for a, u in zip(dip.a, dip.u)])
    main_r = pb_test((dip.exit == "TP").to_numpy(), ps, "RW θ(x0) 沈み→TP")
    pb_test((dip.exit == "TP").to_numpy(), np.array([p_hit(-0.5, a, u, 0.0) for a, u in zip(dip.a, dip.u)]), "RW θ=0 沈み→TP")
    d2 = dip[dip.exit != "TIME"]; ps2 = np.array([p_hit(-0.5, a, u, th) for a, u in zip(d2.a, d2.u)])
    pb_test((d2.exit == "TP").to_numpy(), ps2, "TIME除外 沈み→TP")
    verdict = "survived(沈みに情報)" if main_r["p"] < ALPHA and main_r["obs"] > main_r["exp"] else (
        "弱い(p<0.05, Bonferroni非有意)" if main_r["p"] < 0.05 else "broken(無記憶RWで説明)")
    say("主検定: p=%.4f vs α=%.4f → **%s**  （沈み本の平均 R 観測 %+.3f）" % (main_r["p"], ALPHA, verdict, dip.R.mean()))
    say()
    say("## 対照: 沈まなかった本（offset1.. で −0.5 を見ずに決着）— RW では SL(−a<−0.5) は必ず沈みを経るので非TP は TIME のみ")
    say("  沈まず n=%d  TP %.1f%%  TIME %.1f%%  SL %.1f%%  平均R %+.3f  （SL>0 なら a>0.5 条件か mae1 の計算に穴がある=自己点検）" % (
        len(nodip), 100 * (nodip.exit == "TP").mean(), 100 * (nodip.exit == "TIME").mean(), 100 * (nodip.exit == "SL").mean(), nodip.R.mean()))
    say("  沈み本の割合 P(沈み) 観測 %.1f%% vs RW Σ(1−p_hit(x0,0.5,u,θ))/n = %.1f%%  （沈みそのものが RW より多いか＝ボラ/再テストの構造）" % (
        100 * len(dip) / len(sub), 100 * np.mean([1 - p_hit(x, 0.5, u, th) for x, u in zip(sub.x0, sub.u)])))
    say()
    say("## 部分集合（時代×壁種・θ 固定・Bonferroni 6 → α=%.4f）" % ALPHA)
    say("| 部分集合 | n | TP k | 観測 | 期待 | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    rows = []
    for era in ("2010-20", "2021-23", "2024-26"):
        for wk in ("outer", "mid"):
            g = dip[(dip.era == era) & (dip.wall_kind == wk)]
            if len(g) == 0: continue
            rows.append(pb_test((g.exit == "TP").to_numpy(), np.array([p_hit(-0.5, a, u, th) for a, u in zip(g.a, g.u)]), "%s %s" % (era, wk)))
    for sd in ("BUY", "SELL"):
        g = dip[dip.side == sd]
        pb_test((g.exit == "TP").to_numpy(), np.array([p_hit(-0.5, a, u, th) for a, u in zip(g.a, g.u)]), "側 %s" % sd)
    sig = [r for r in rows if r["p"] < ALPHA and r["obs"] > r["exp"]]
    say("時代×壁種で Bonferroni 有意(正方向): %d/%d  超過符号: %s" % (len(sig), len(rows), " ".join("%+.0f" % (100 * (r["obs"] - r["exp"])) for r in rows)))
    say()
    say("## 閾値感度 d∈{0.3,0.5,0.7}（構造確認のみ）")
    say("| d | n | TP k | 観測 | 期待 | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    for d in (0.3, 0.5, 0.7):
        g = sub[(sub.mae1 >= d) & (sub.a > d)]
        pb_test((g.exit == "TP").to_numpy(), np.array([p_hit(-d, a, u, th) for a, u in zip(g.a, g.u)]), "d=%.1f" % d)
    say()
    say("## 沈み後の平均 R（出口ルールの材料）: 沈み本 R 平均 %+.3f (n=%d) ／ 沈まず %+.3f (n=%d) ／ 全体 %+.3f" % (
        dip.R.mean(), len(dip), nodip.R.mean(), len(nodip), sub.R.mean()))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
