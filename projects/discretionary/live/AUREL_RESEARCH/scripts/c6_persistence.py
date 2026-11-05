# -*- coding: utf-8 -*-
"""
[cycle6 研究レーン] 2026-11-05 — 【レジーム・メタ】再加速の成績は時間方向に持続するか
（週次/月次 平均R の自己相関＝「優位はレジーム依存（憲章 D2）」の検証可能な核）

=== 事前固定（この docstring を書いてから数字を見る） ===
問い: 憲章 D2 は「壁→壁/再加速の優位はレジーム依存で近年に宿る」と言う。レジーム依存が本物なら、
      成績の時系列には**持続性**（良い週の次は良い週・悪い月の次は悪い月）が残るはず。
      逆に成績が時間方向に無記憶なら、「近年の優位」は事後に切った窓の差でしかなく、
      直近の成績からレジームを読む手段（連続レジームメーター）には予測力が無いことになる。
      これは入口フィルタでも出口でもない。レジーム記述（メタ）であり、採用提案はしない。
      ※「直近成績で取引を on/off」＝エクイティカーブ・フィルタは既知の罠。本件は記述のみ。

データ: data/refute_c4_scan_paths_2010_2026.json 再加速 closed 19404 本（entry_time UTC epoch・R gross・year・hold）。
      ft 非対称は全本に同一に乗る定数シフトなので、自己相関・差の比較には影響しない（絶対水準は使わない=D2）。
      scan 無し・M5 読込なし・MT5 なし。

集計: 週 = UTC 月〜日（Period W-SUN）、月 = 暦月。**有効期間 = 本数 n≥5** の週/月のみ（平均R の分散を抑える）。
  M1 自己相関: 有効週 w と w+k（k=1..4 暦週）の両方が有効なペアで Pearson r。帰無 = 有効週の値を暦位置の間で
      シャッフル（2000 回・持続性だけ壊す）→ lag1 の p と、k=1..4 の max r の p_max。月次は k=1..3。
  M2 予測（真の前向き）: 週 t の直前 4 暦週にあった本（≥10 本）の平均R = trailing。
      (a) Spearman(trailing, 週 t 平均R)。(b) trailing を**在の中央値**で 2 群に分け（外へは在の閾値を固定適用）、
      週 t 平均R の差（good − bad）を週等重みの Welch t で。月次は直前 3 暦月（≥20 本）。
  陽性対照: 週あたり**本数** n の lag1 自己相関（ボラ・クラスタリングで正になるはず＝方法が持続性を検出できる確認）。
窓: 在 = 2010-2020 / 外 = 2021-2026H1 / 近年 2024-2026H1（D2・記述のみ）。
予測: P1 週次 lag1 r>0 で 在 置換 p<0.05 ∧ 外 同符号 p<0.10。
      P2 週次 trailing 2 群差 >0 で 在 t≥2 ∧ 外 t≥1.5。
      P3 月次 lag1 r>0 在外とも（記述・補助）。
合否: H（持続性あり）支持 = P1 ∧ P2。それ以外 = null（「週〜月の尺度では成績に持続性なし／検出できない」）。
ベースライン: 無記憶（置換帰無）。各窓の無条件平均R。
事前の最重要反証: (1) 週あたり n≈20〜30 本で週平均R の SE≈0.25R と大きく、r の検出力は小さい（r≈0.1 を見るには
      ≈400 週要る＝在は十分・外は境界）。null は「この粒度では」限定。(2) 持続性があっても、それは
      ボラ・クラスタリングによる「本数の持続」が平均R に漏れたものかもしれない → 本数の lag1 を陽性対照として分離。
      (3) 保有は最長 288 本（1 日）なので隣接週の本が同じ値動きを共有するのは週末境界のみ・影響は小。
昇格候補ではない。seed 20261105。
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.stats import spearmanr, pearsonr

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "c6_persistence_result.md")
rng = np.random.default_rng(20261105)
lines = []
def say(s=""): print(s, flush=True); lines.append(s)

d = json.load(open(os.path.join(ROOT, "data", "refute_c4_scan_paths_2010_2026.json")))
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["week"] = tr["ts"].dt.to_period("W-SUN")
tr["month"] = tr["ts"].dt.to_period("M")
say(f"# [cycle6] 成績の時間持続性 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c6_persistence.py)")
say(f"trades n={len(tr)} {tr.ts.min()} .. {tr.ts.max()} UTC  R mean {tr.R.mean():+.4f} sd {tr.R.std():.3f}")

W = {"在2010-20": tr.year <= 2020, "外2021-26": tr.year >= 2021, "近年2024-26": tr.year >= 2024}
NMIN = {"week": 5, "month": 5}
TRAIL = {"week": (4, 10), "month": (3, 20)}   # (直前期間数, 最小本数)
NPERM = 2000

def agg(df, per):
    g = df.groupby(per).agg(n=("R", "size"), mR=("R", "mean"), tp=("R", lambda x: (x > 0).mean()))
    g = g.sort_index()
    g["valid"] = g["n"] >= NMIN[per]
    return g

def lag_pairs(g, k, col="mR"):
    """有効期間 w と w+k の両方が有効なペアの値列"""
    v = g.loc[g["valid"], col]
    idx = v.index
    nxt = idx + k
    ok = nxt.isin(idx)
    a = v.loc[idx[ok]].to_numpy(); b = v.reindex(nxt[ok]).to_numpy()
    return a, b

def lag_r(g, k, col="mR"):
    a, b = lag_pairs(g, k, col)
    return (pearsonr(a, b)[0] if len(a) > 3 else np.nan), len(a)

def perm_null(g, lags, col="mR"):
    """有効期間の値を暦位置間でシャッフル → lag r の帰無分布（lag1 と max over lags）"""
    gg = g.copy(); vidx = gg.index[gg["valid"]]
    vals = gg.loc[vidx, col].to_numpy().copy()
    n1 = np.empty(NPERM); nmax = np.empty(NPERM)
    for p in range(NPERM):
        gg.loc[vidx, col] = rng.permutation(vals)
        rs = [lag_r(gg, k, col)[0] for k in lags]
        n1[p] = rs[0]; nmax[p] = np.nanmax(rs)
    return n1, nmax

def trailing(df, g, per):
    """各有効期間 t の直前 L 期間にあった本の平均R（≥ nmin 本）"""
    L, nmin = TRAIL[per]
    rows = []
    for t in g.index[g["valid"]]:
        prev = [t - j for j in range(1, L + 1)]
        sub = g.reindex(prev).dropna(subset=["n"])
        ntot = int(sub["n"].sum())
        if ntot < nmin: continue
        trail = float((sub["mR"] * sub["n"]).sum() / ntot)
        rows.append({"per": t, "trail": trail, "ntrail": ntot, "mR": g.loc[t, "mR"], "n": g.loc[t, "n"]})
    return pd.DataFrame(rows)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    diff = a.mean() - b.mean(); se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    return diff, diff/se if se > 0 else np.nan

res = {}
for per, lags in (("week", [1, 2, 3, 4]), ("month", [1, 2, 3])):
    say(f"\n## {per}: 集計（有効 = n≥{NMIN[per]}）")
    thr_in = None
    for wn, msk in W.items():
        g = agg(tr[msk], per)
        nv = int(g["valid"].sum())
        v = g.loc[g["valid"]]
        say(f"- {wn}: 期間数 {len(g)} 有効 {nv} / 本数 中央値 {v.n.median():.0f} (p10 {v.n.quantile(.1):.0f}, p90 {v.n.quantile(.9):.0f}) / 期間平均R: mean {v.mR.mean():+.4f} sd {v.mR.std():.3f} / 本レベル sd/√n 中央値 {(tr[msk].R.std()/np.sqrt(v.n)).median():.3f}")
        # M1 自己相関
        rs = {k: lag_r(g, k) for k in lags}
        n1, nmax = perm_null(g, lags)
        r1 = rs[lags[0]][0]; rmax = np.nanmax([rs[k][0] for k in lags])
        p1 = (n1 >= r1).mean() if not np.isnan(r1) else np.nan          # 片側（予測 >0）
        pmax = (nmax >= rmax).mean()
        say(f"  - M1 自己相関 平均R: " + " / ".join(f"lag{k} r {rs[k][0]:+.3f} (pairs {rs[k][1]})" for k in lags))
        say(f"    lag1 片側置換 p **{p1:.3f}**（帰無 r 中央値 {np.median(n1):+.3f}・95%点 {np.quantile(n1,.95):+.3f}）/ max r {rmax:+.3f} p_max {pmax:.3f}")
        # 陽性対照: 本数・TP 率
        rn = lag_r(g, 1, "n"); rtp = lag_r(g, 1, "tp")
        gn = g.copy(); nn1, _ = perm_null(gn, [1], "n")
        say(f"  - 陽性対照 lag1 r: 本数 n **{rn[0]:+.3f}**（置換 p {(nn1 >= rn[0]).mean():.4f}）/ TP 率 {rtp[0]:+.3f}")
        # M2 予測
        T = trailing(tr[msk], g, per)
        rho, prho = spearmanr(T["trail"], T["mR"])
        if wn == "在2010-20": thr_in = float(T["trail"].median())
        thr = thr_in if thr_in is not None else float(T["trail"].median())
        good = T["trail"] > thr; bad = ~good
        diff, t = welch(T.loc[good, "mR"], T.loc[bad, "mR"])
        # 本レベル（週内の本を等重み）も併記
        R_good = tr[msk & tr[per].isin(T.loc[good, "per"])]["R"]; R_bad = tr[msk & tr[per].isin(T.loc[bad, "per"])]["R"]
        d2, t2 = welch(R_good, R_bad)
        say(f"  - M2 trailing（直前 {TRAIL[per][0]} {per}・≥{TRAIL[per][1]} 本）: 期間数 {len(T)} / Spearman ρ **{rho:+.4f}** (p {prho:.3f}) / 閾値(在中央値) {thr:+.4f} / good n={good.sum()} mean {T.loc[good,'mR'].mean():+.4f} vs bad n={bad.sum()} mean {T.loc[bad,'mR'].mean():+.4f} → diff **{diff:+.4f} t {t:+.2f}**（本レベル diff {d2:+.4f} t {t2:+.2f}, n {len(R_good)}:{len(R_bad)}）")
        # 五分位（記述）
        q = pd.qcut(T["trail"], 5, labels=False, duplicates="drop")
        say(f"    trailing 五分位（低→高）の期間平均R: " + " ".join(f"{m:+.3f}" for m in T.groupby(q)["mR"].mean()))
        res[(per, wn)] = dict(r1=r1, p1=p1, rmax=rmax, pmax=pmax, rho=rho, diff=diff, t=t, rn=rn[0])

say("\n## 判定（事前規則）")
w1 = res[("week", "在2010-20")]; w2 = res[("week", "外2021-26")]
m1 = res[("month", "在2010-20")]; m2 = res[("month", "外2021-26")]
P1 = (w1["r1"] > 0 and w1["p1"] < 0.05) and (w2["r1"] > 0 and w2["p1"] < 0.10)
P2 = (w1["diff"] > 0 and w1["t"] >= 2.0) and (w2["diff"] > 0 and w2["t"] >= 1.5)
P3 = (m1["r1"] > 0) and (m2["r1"] > 0)
say(f"- P1 週次 lag1 r>0 (在 p<0.05 ∧ 外 p<0.10): 在 r {w1['r1']:+.3f} p {w1['p1']:.3f} / 外 r {w2['r1']:+.3f} p {w2['p1']:.3f} → {'PASS' if P1 else 'FAIL'}")
say(f"- P2 週次 trailing 2 群差 (在 t≥2 ∧ 外 t≥1.5): 在 {w1['diff']:+.4f} t {w1['t']:+.2f} / 外 {w2['diff']:+.4f} t {w2['t']:+.2f} → {'PASS' if P2 else 'FAIL'}")
say(f"- P3 月次 lag1 r>0 在外とも（補助）: 在 {m1['r1']:+.3f} / 外 {m2['r1']:+.3f} → {'PASS' if P3 else 'FAIL'}")
say(f"\n**H（週〜月の持続性あり）= P1∧P2 → {'支持' if (P1 and P2) else 'null（週〜月の尺度で成績の持続性は検出できない）'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
