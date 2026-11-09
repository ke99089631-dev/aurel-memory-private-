# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-09 — 補足 b（事後・記述のみ・判定不使用）: refute_c23_pathshape Q5(a) の帰結を確かめる
  Q5(a) で 外 (k=24,B3) の ΔV −0.262 は建玉時 atr/risk 三分位差 Δ_ATR −0.241 (t−2.36) でほぼ再現し、
  V/(atr/risk) では −0.034 (t−0.33) に消えた。= 「path の形」でなく「ストップがボラ何本分か」(F_0) の情報。
  問い: その atr/risk 効果は停滞セル固有か、それとも 2021-26 の全本（建玉時点）に既にある性質か。
  (1) 全 closed 本の R* を atr/risk 三分位（窓内）で: 在／外／近年・top−bottom・Welch t・日クラスタ t。
  (2) hold>24 の全 B（停滞条件なし）で e を atr/risk 三分位で: 窓別。
  (3) 外 (k=24,B3) で atr/risk を統制した後の V の残差効果: e ~ z(atr/risk) + z(V) の 2 変数回帰（日クラスタ t）。
  (4) 外の atr/risk 三分位の幾何: b 中央値・risk 中央値・TP 率・R* 平均（記述）。
読取りのみ。入力は同キャッシュ。書き込みは data/refute_c23_pathshape_b.md のみ。
"""
import json, os, math, time
import numpy as np, pandas as pd
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c23_pathshape_b.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
def tstat(d):
    d = np.asarray(d, float); se = d.std(ddof=1) / math.sqrt(len(d)); return d.mean() / se if se > 0 else float("nan")
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return diff, diff / se
def ols_cl(y, X, g):
    X = np.column_stack([np.ones(len(y))] + list(X)); XtX_inv = np.linalg.inv(X.T @ X); beta = XtX_inv @ X.T @ y
    u = y - X @ beta; S = pd.DataFrame(X * u[:, None]).groupby(np.asarray(g)).sum().to_numpy(); V = XtX_inv @ (S.T @ S) @ XtX_inv
    return beta, beta / np.sqrt(np.diag(V))
def ter(x): q1, q2 = np.quantile(x, [1/3, 2/3]); return x >= q2, x <= q1

J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]]).sort_values("entry_time").reset_index(drop=True)
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); aux = {t["entry_time"]: t for t in c4["trades"]}
df["b"] = [aux[t]["b"] for t in df.entry_time]; df["atr"] = [aux[t]["atr"] for t in df.entry_time]
FT = J["frozen"]["FEED_TOL"]; z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"]
risk = df.risk.to_numpy(); ft = FT / risk; er = df.exit_reason.to_numpy(); is_slt = (er == "SL") | (er == "TP")
Rstar = df.R.to_numpy() + ft * is_slt; hold = df.hold.to_numpy(); year = df.year.to_numpy(); day = df.entry_time.to_numpy() // 86400
ar = (df.atr / df.risk).to_numpy(); bb = df.b.to_numpy()
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
say(f"# AUREL [REFUTE] 補足 b — atr/risk 効果は停滞セル固有か（事後・記述） {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c23_pathshape_b.py)")
say()
say("## (1) 全 closed 本の R*（公正化）を建玉時 atr/risk 三分位（窓内）で: top−bottom")
say("| 窓 | n | top R* / t | bottom R* / t | Δ_ATR / Welch t / 日クラスタ t |")
say("|---|---|---|---|---|")
for wn, wm in W.items():
    x = ar[wm]; r = Rstar[wm]; d = day[wm]; top, bot = ter(x)
    dd, tw = welch(r[top], r[bot])
    y = np.concatenate([r[top], r[bot]]); X = [np.r_[np.ones(top.sum()), np.zeros(bot.sum())]]; g = np.concatenate([d[top], d[bot]])
    _, tcl = ols_cl(y, X, g)
    say(f"| {wn} | {wm.sum()} | {r[top].mean():+.4f} / {tstat(r[top]):+.2f} | {r[bot].mean():+.4f} / {tstat(r[bot]):+.2f} | {dd:+.4f} / {tw:+.2f} / {tcl[1]:+.2f} |")
say()
say("## (2) hold>24 の建玉中本（停滞条件なし・全 B）: e = R* − cl_24 を atr/risk 三分位で")
alive = np.nonzero(hold > 24)[0]; cl24 = clR[off[alive] + 24]; e24 = Rstar[alive] - cl24
say("| 窓 | n | Δ_ATR (top−bot) / Welch t | B3 のみ Δ_ATR / t | B3 以外 Δ_ATR / t |")
say("|---|---|---|---|---|")
for wn, wm in W.items():
    m = wm[alive]; x = ar[alive][m]; e = e24[m]; c = cl24[m]; top, bot = ter(x)
    dd, tw = welch(e[top], e[bot])
    b3 = np.abs(c) < 0.2
    t3, b3b = ter(x[b3]); d3, tw3 = welch(e[b3][t3], e[b3][b3b])
    tn, bn = ter(x[~b3]); dn, twn = welch(e[~b3][tn], e[~b3][bn])
    say(f"| {wn} | {m.sum()} | {dd:+.4f} / {tw:+.2f} | {d3:+.4f} / {tw3:+.2f} ({b3.sum()}) | {dn:+.4f} / {twn:+.2f} ({(~b3).sum()}) |")
say()
say("## (3) 外 (k=24,B3): e ~ z(atr/risk) + z(V_24)（2 変数・日クラスタ t）— V の残差効果")
m = (year >= 2021)[alive] & (np.abs(cl24) < 0.2); idx = alive[m]
P = clR[off[idx][:, None] + np.arange(0, 25)[None, :]]; V = np.sqrt((np.diff(P, axis=1) ** 2).mean(axis=1))
zz = lambda v: (v - v.mean()) / v.std(ddof=1)
e = e24[m]; g = day[idx]
for lab, X in (("z(V) のみ", [zz(V)]), ("z(atr/risk) のみ", [zz(ar[idx])]), ("両方", [zz(ar[idx]), zz(V)])):
    beta, tt = ols_cl(e, X, g)
    say(f"- {lab}: " + "・".join(f"β{i+1} {beta[i+1]:+.4f} (t{tt[i+1]:+.2f})" for i in range(len(X))) + f"  n {len(e)}")
beta, tt = ols_cl(e, [zz(ar[idx]), zz(V / ar[idx])], g)
say(f"- z(atr/risk) + z(V/(atr/risk)): β_ATR {beta[1]:+.4f} (t{tt[1]:+.2f})・β_Vnorm {beta[2]:+.4f} (t{tt[2]:+.2f})")
say()
say("## (4) 外の atr/risk 三分位の幾何（全 closed 本・記述）")
wm = year >= 2021; x = ar[wm]; top, bot = ter(x)
say("| 群 | atr/risk 中央値 | b 中央値 | risk 中央値 (USD) | TP 率 | hold 中央値 | R* 平均 |")
say("|---|---|---|---|---|---|---|")
for lab, q in (("top", top), ("mid", ~top & ~bot), ("bot", bot)):
    say(f"| {lab} | {np.median(x[q]):.2f} | {np.median(bb[wm][q]):.2f} | {np.median(risk[wm][q]):.2f} | {100*(er[wm][q]=='TP').mean():.0f}% | {np.median(hold[wm][q]):.0f} | {Rstar[wm][q].mean():+.4f} |")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
