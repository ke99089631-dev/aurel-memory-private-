# -*- coding: utf-8 -*-
"""
[cycle47 補足 b / 2026-11-18・事後（supplementary）・判定を上書きしない]
主表で腕の PRE（ジャンプ前 1 時間の超過ボラ）が違う（UJ 1.3〜1.4×・ANN_J ≈1.0〜1.2×）ことが見えたので、
「事象が vol 状態を変えたか」を 自腕の前状態からの変化 ΔE_k = E_k − E_PRE（DiD）で読み直す。
  D_k^DiD = (ΔE_k | ANN_J) − (ΔE_k | UJ)・log z＋時刻 FE・日クラスタ（主表と同じ推定器）。
  併記: 各腕の E_PRE（0 との t）・ΔE_k（0 との t）・SJ − UJ。
入力 = data/c47_events_excess.csv（c47 主 script の再利用キャッシュ）。数字を見た後の読みなので 事後 と明記する。
"""
import os, math, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c47b_prestate_did.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
EV = pd.read_csv(os.path.join(DATA, "c47_events_excess.csv")); EV["day"] = EV.et_date
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
for w in ["W1", "W2", "W3", "W4"]: EV["d" + w] = EV["E_" + w] - EV["E_PRE"]

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1)); return beta, V, G
def arm_fit(o, ycol, treat, ctrlarm):
    o = o[(o.cls == treat) | (o.cls == ctrlarm)]; o = o[np.isfinite(o[ycol])]
    if (o.cls == treat).sum() < 5 or (o.cls == ctrlarm).sum() < 5: return np.nan, np.nan, 0, 0
    hours = sorted(o.hr.unique())
    H = np.column_stack([(o.hr.to_numpy() == h).astype(float) for h in hours[1:]]) if len(hours) > 1 else np.zeros((len(o), 0))
    d = (o.cls == treat).to_numpy(float); y = o[ycol].to_numpy(float)
    X = np.column_stack([np.ones(len(o)), d, o.logz.to_numpy(float), H]); beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    return beta[1], math.sqrt(max(V[1, 1], 0)), int((o.cls == treat).sum()), int((o.cls == ctrlarm).sum())
def t0(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return (x.mean(), x.mean() / (x.std(ddof=1) / math.sqrt(len(x))), len(x)) if len(x) > 2 else (np.nan, np.nan, len(x))
def fmt(b, se): return f"{b:+.3f} ({(b/se if se and se>0 else float('nan')):+.2f})"

say("# [cycle47 補足 b・事後] 前状態からの変化 ΔE_k = E_k − E_PRE（DiD）: 事象は vol 状態を変えたか")
say("## 1. 腕別 E_PRE（ジャンプ前 1 時間・同時刻対照差・0 との t）")
say("| 窓 | ANN_J | ANN_NJ | UJ | SJ | ANN_J − UJ (log z＋時刻 FE・日cl t) |")
say("|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = EV[(EV.year >= lo_) & (EV.year <= hi_)]
    c = [f"{t0(o[o.cls==a].E_PRE)[0]:+.3f} (t {t0(o[o.cls==a].E_PRE)[1]:+.1f}・n {t0(o[o.cls==a].E_PRE)[2]})" for a in ["ANN_J", "ANN_NJ", "UJ", "SJ"]]
    b, se, _, _ = arm_fit(o, "E_PRE", "ANN_J", "UJ")
    say(f"| {lab} | " + " | ".join(c) + f" | {fmt(b, se)} |")
say("")
say("## 2. ΔE_k（自腕の前状態からの変化・0 との t）と DiD = ANN_J − UJ／SJ − UJ（log z＋時刻 FE・日クラスタ）")
say("| 窓 | k | ANN_J ΔE (t) | UJ ΔE (t) | SJ ΔE (t) | **DiD ANN_J − UJ (t)** | MDE 2se | SJ − UJ (t) |")
say("|---|---|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = EV[(EV.year >= lo_) & (EV.year <= hi_)]
    for w in ["W1", "W2", "W3", "W4"]:
        yc = "d" + w
        c = [f"{t0(o[o.cls==a][yc])[0]:+.3f} ({t0(o[o.cls==a][yc])[1]:+.1f})" for a in ["ANN_J", "UJ", "SJ"]]
        b, se, nt, nc = arm_fit(o, yc, "ANN_J", "UJ"); b2, se2, _, _ = arm_fit(o, yc, "SJ", "UJ")
        say(f"| {lab} | {w} | " + " | ".join(c) + f" | **{fmt(b, se)}** | {2*se:.3f} | {fmt(b2, se2)} |")
say("")
say("## 3. UJ の前状態の層別（E_PRE 三分位）: 前が静かな UJ は ANN_J のように vol を作るか（事後・記述）")
say("| 窓 | 層 | n | E_PRE 平均 | ΔE_W1 (t) | ΔE_W3 (t) | E_W3 水準 |")
say("|---|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS[:2]:
    o = EV[(EV.year >= lo_) & (EV.year <= hi_) & (EV.cls == "UJ") & np.isfinite(EV.E_PRE)]
    q = o.E_PRE.quantile([1/3, 2/3]).to_numpy()
    for name, m in [("静 T1", o.E_PRE <= q[0]), ("中 T2", (o.E_PRE > q[0]) & (o.E_PRE <= q[1])), ("荒 T3", o.E_PRE > q[1])]:
        s = o[m]
        say(f"| {lab} | {name} | {len(s)} | {s.E_PRE.mean():+.3f} | {t0(s.dW1)[0]:+.3f} ({t0(s.dW1)[1]:+.1f}) | {t0(s.dW3)[0]:+.3f} ({t0(s.dW3)[1]:+.1f}) | {t0(s.E_W3)[0]:+.3f} |")
    a = EV[(EV.year >= lo_) & (EV.year <= hi_) & (EV.cls == "ANN_J")]
    say(f"| {lab} | ANN_J 参照 | {len(a)} | {a.E_PRE.mean():+.3f} | {t0(a.dW1)[0]:+.3f} ({t0(a.dW1)[1]:+.1f}) | {t0(a.dW3)[0]:+.3f} ({t0(a.dW3)[1]:+.1f}) | {t0(a.E_W3)[0]:+.3f} |")
say("")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
