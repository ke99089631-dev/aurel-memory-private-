# -*- coding: utf-8 -*-
"""
[cycle27 補足 c・事後・探索的] 2026-11-10 — c27 H2 の β(p_w on q̄_w)≈0.7 と c27b の本レベル β(x on q)≈0 の食い違い
＝ 超過到達率 x̄ は「本の b」でなく「その週の b̄（幾何の水準）」と結びついている可能性。
(1) 週レベル: ρ(x̄_w, q̄_w)・ρ(x̄_w, b̄_w)・ρ(x̄_w, risk̄_w)・ρ(x̄_w, n_w)（同時・記述）、within/between 分解。
(2) 前向き（事後に立てた新仮説の予備検査・判定ではない）: 前週の b̄_{w−1}（既知）で今週の x̄_w を 2 群（在の中央値で固定）
    → Welch t（週等重み）・Spearman。競合予測子 risk̄_{w−1}・n_{w−1}・q̄_{w−1} も同形で並べる（b̄ がボラの別名かを見る）。
    有効週 = 決着 n≥5、前週も有効。窓別（D2）。本レベル（週内の本を等重み）も併記。
"""
import json, os, time, math
import numpy as np, pandas as pd
from scipy.stats import spearmanr
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c27c_weekly_b_vs_excess.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["week"] = tr["ts"].dt.to_period("W-SUN")
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = tr["tp"] - tr["q"]; tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
W = {"在2010-20": tr.year <= 2020, "外2021-26": tr.year >= 2021, "近年2024-26": tr.year >= 2024}
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return diff, diff / se, se
say(f"# [cycle27 補足 c・事後・探索的] 週の幾何水準 b̄ と超過到達率 x̄ — {time.strftime('%Y-%m-%d %H:%M')}")
say("## (1) 同時（週）: 相関と within/between 分解")
say("| 窓 | 有効週 | ρ(x̄,q̄) | t | ρ(x̄,b̄) | ρ(x̄,risk̄) | ρ(x̄,n) | ρ(R̄*,b̄) | between Cov(x̄,q̄)/Var(q̄) | within β(x on q−q̄_w) |"); say("|---|---|---|---|---|---|---|---|---|---|")
G = {}
for wn, wm in W.items():
    s = tr[wm & tr.dec].copy()
    g = s.groupby("week").agg(n=("x", "size"), xbar=("x", "mean"), qbar=("q", "mean"), bbar=("b", "mean"), rbar=("risk", "mean"))
    gR = tr[wm].groupby("week").agg(Rbar=("Rs", "mean")); g = g.join(gR); g = g[g.n >= 5]; G[wn] = g
    r_xq = np.corrcoef(g.xbar, g.qbar)[0, 1]; t_xq = r_xq * math.sqrt((len(g) - 2) / (1 - r_xq ** 2))
    s = s.join(g[["qbar"]], on="week", how="inner"); dq = (s.q - s.qbar).to_numpy(); bw = np.cov(dq, s.x)[0, 1] / dq.var()
    say(f"| {wn} | {len(g)} | **{r_xq:+.3f}** | {t_xq:+.2f} | {np.corrcoef(g.xbar, g.bbar)[0,1]:+.3f} | {np.corrcoef(g.xbar, g.rbar)[0,1]:+.3f} | {np.corrcoef(g.xbar, g.n)[0,1]:+.3f} | {np.corrcoef(g.Rbar, g.bbar)[0,1]:+.3f} | {np.cov(g.xbar, g.qbar)[0,1]/g.qbar.var():+.3f} | {bw:+.3f} |")
say()
say("## (2) 前向き予備検査（事後・判定なし）: 前週の量で今週の x̄_w を 2 群（在の中央値で閾値固定・high − low）")
say("| 窓 | 予測子 (w−1) | ペア週 | Spearman ρ | p | high n／x̄ pp | low n／x̄ pp | diff pp | Welch t | 本レベル diff pp / t | R̄* diff / t |"); say("|---|---|---|---|---|---|---|---|---|---|---|")
THR = {}
for wn, wm in W.items():
    g = G[wn]; idx = g.index
    prev = idx - 1; ok = prev.isin(idx)
    cur = g.loc[idx[ok]]; pre = g.reindex(prev[ok]); pre.index = cur.index
    for col in ("bbar", "qbar", "rbar", "n"):
        if wn == "在2010-20": THR[col] = float(pre[col].median())
        hi = pre[col] > THR[col]; lo = ~hi
        rho, p = spearmanr(pre[col], cur.xbar)
        diff, t, se = welch(cur.xbar[hi], cur.xbar[lo])
        s = tr[wm & tr.dec]; shi = s[s.week.isin(cur.index[hi])]; slo = s[s.week.isin(cur.index[lo])]
        d2, t2, _ = welch(shi.x, slo.x)
        a = tr[wm]; ahi = a[a.week.isin(cur.index[hi])]; alo = a[a.week.isin(cur.index[lo])]
        d3, t3, _ = welch(ahi.Rs, alo.Rs)
        say(f"| {wn} | {col} | {len(cur)} | {rho:+.3f} | {p:.3f} | {hi.sum()}／{100*cur.xbar[hi].mean():+.2f} | {lo.sum()}／{100*cur.xbar[lo].mean():+.2f} | **{100*diff:+.2f}** | **{t:+.2f}** | {100*d2:+.2f} / {t2:+.2f} | {d3:+.4f} / {t3:+.2f} |")
say("\n注: 閾値は在の前週中央値で固定（b̄ " + f"{THR['bbar']:.3f}・q̄ {THR['qbar']:.3f}・risk {THR['rbar']:.2f}・n {THR['n']:.0f}" + "）。外・近年は b̄ の水準が上がっているので high 群が多数になる（均衡分割は別途）。")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
