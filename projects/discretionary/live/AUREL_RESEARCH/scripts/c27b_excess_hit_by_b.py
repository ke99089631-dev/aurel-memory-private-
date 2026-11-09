# -*- coding: utf-8 -*-
"""
[cycle27 補足 b・事後・記述] 2026-11-10 — c27 の H2 で β(p on q̄) ≈0.7 <1 と、外で Var(週 x̄) < 名目ノイズ（過小分散）が出た。
その 2 つの“形”を本レベルで記述する（判定には使わない・入口フィルタの提案ではない・D2: 窓別）。
(a) 本レベル OLS x_i = α + β·q_i（窓別・建玉日クラスタ t）と、b 十分位別の x̄（pp）・R̄*（全本）・n。
    RW 基準では全十分位で x̄=0・R̄*=0。β<1 ⇔ 遠い TP（q 小）の本が RW より到達しやすく、近い TP が到達しにくい。
(b) 過小分散の候補 = 同週に BUY と SELL が共存し一方が TP・他方が SL になる負の相関。
    週内の BUY x̄ と SELL x̄ の相関（有効週・両側 ≥3 本）・側別の Var(x̄) 対 名目ノイズ・同週の建玉時刻重複率。
"""
import json, os, time, math
import numpy as np, pandas as pd
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c27b_excess_hit_by_b.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["week"] = tr["ts"].dt.to_period("W-SUN"); tr["day"] = tr["entry_time"] // 86400
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = tr["tp"] - tr["q"]; tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
W = {"在2010-20": tr.year <= 2020, "外2021-26": tr.year >= 2021, "近年2024-26": tr.year >= 2024}
def ols_cl(y, x, g):
    X = np.column_stack([np.ones(len(x)), x]); beta = np.linalg.lstsq(X, y, rcond=None)[0]; u = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X); S = pd.DataFrame(X * u[:, None]).groupby(np.asarray(g)).sum().to_numpy()
    V = XtX_inv @ (S.T @ S) @ XtX_inv; return beta[1], math.sqrt(V[1, 1]), beta[0]
say(f"# [cycle27 補足 b・事後・記述] 本レベルの x on q・b 十分位・週内 側の相関 — {time.strftime('%Y-%m-%d %H:%M')}")
say("## (a) 本レベル OLS x_i = α + β·q_i（決着本・建玉日クラスタ se）")
say("| 窓 | n | β | se | α | 含意: q=0.3(b≈2.3) の x̄ | q=0.6(b≈0.65) の x̄ |"); say("|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    s = tr[wm & tr.dec]; b_, se, a_ = ols_cl(s.x.to_numpy(), s.q.to_numpy(), s.day.to_numpy())
    say(f"| {wn} | {len(s)} | **{b_:+.3f}** | {se:.3f} | {a_:+.3f} | {100*(a_+b_*0.3):+.1f} pp | {100*(a_+b_*0.6):+.1f} pp |")
say()
say("## (a') b 十分位（在の分位点で固定・全窓同じ境界）別: 決着 n・x̄ (pp)・t・R̄*（全本・R）・t・TP 率 p・q̄")
edges = np.quantile(tr[tr.year <= 2020].b, np.linspace(0, 1, 11)); edges[0] = -1; edges[-1] = 1e9
for wn, wm in W.items():
    say(f"### {wn}"); say("| 十分位 | b 範囲 | 決着 n | x̄ pp | t | R̄* | t | p | q̄ |"); say("|---|---|---|---|---|---|---|---|---|")
    for i in range(10):
        m = wm & (tr.b > edges[i]) & (tr.b <= edges[i + 1]); s = tr[m & tr.dec]; a = tr[m]
        tx = 100 * s.x.mean() / (100 * s.x.std(ddof=1) / math.sqrt(len(s))) if len(s) > 3 else np.nan
        tR = a.Rs.mean() / (a.Rs.std(ddof=1) / math.sqrt(len(a))) if len(a) > 3 else np.nan
        lo = max(edges[i], 0); hi = edges[i + 1] if edges[i + 1] < 1e8 else tr.b.max()
        say(f"| D{i+1} | {lo:.2f}–{hi:.2f} | {len(s)} | {100*s.x.mean():+.2f} | {tx:+.2f} | {a.Rs.mean():+.4f} | {tR:+.2f} | {s.tp.mean():.3f} | {s.q.mean():.3f} |")
    say()
say("## (b) 週内の側の相関（過小分散の候補）")
say("| 窓 | 有効週(両側≥3) | ρ(BUY x̄, SELL x̄) | Var(x̄_全) / 名目 | Var(x̄_BUY) / 名目 | Var(x̄_SELL) / 名目 | 同週に反対側の本が建玉中に重なる本の割合 |"); say("|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    s = tr[wm & tr.dec].copy()
    g = s.groupby(["week", "side"]).agg(n=("x", "size"), xbar=("x", "mean"), vq=("q", lambda v: float((v * (1 - v)).mean()))).reset_index()
    pv = g.pivot(index="week", columns="side", values=["n", "xbar", "vq"])
    ok = (pv[("n", "BUY")] >= 3) & (pv[("n", "SELL")] >= 3)
    rho = np.corrcoef(pv.loc[ok, ("xbar", "BUY")], pv.loc[ok, ("xbar", "SELL")])[0, 1]
    def ratio(sub):
        gg = sub.groupby("week").agg(n=("x", "size"), xbar=("x", "mean"), vq=("q", lambda v: float((v * (1 - v)).mean())))
        gg = gg[gg.n >= 5]; return gg.xbar.var(ddof=1) / (gg.vq / gg.n).mean()
    r_all = ratio(s); r_b = ratio(s[s.side == "BUY"]); r_s = ratio(s[s.side == "SELL"])
    # overlap with opposite side
    ent = s.entry_time.to_numpy(); ex = ent + 300 * s.hold.to_numpy(); sd = s.side.to_numpy(); ov = np.zeros(len(s), bool)
    order = np.argsort(ent); ent_o, ex_o, sd_o = ent[order], ex[order], sd[order]
    for i in range(len(s)):
        j = np.searchsorted(ent_o, ex_o[i], side="right"); k = np.searchsorted(ent_o, ent_o[i] - 300 * 288)
        cand = slice(k, j); m = (sd_o[cand] != sd_o[i]) & (ex_o[cand] >= ent_o[i]) & (ent_o[cand] <= ex_o[i])
        ov[order[i]] = m.any()
    say(f"| {wn} | {int(ok.sum())} | **{rho:+.3f}** | {r_all:.3f} | {r_b:.3f} | {r_s:.3f} | {100*ov.mean():.1f}% |")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
