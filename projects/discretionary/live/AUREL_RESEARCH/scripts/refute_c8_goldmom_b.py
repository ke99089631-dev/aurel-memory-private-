# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-06 — refute_c8_goldmom.py の事後フォロー（結果を見てから追加・判定規則は動かさない）
理由: 主スクリプト Q0 で、cycle8 が「金自身の直前 24h と同向きの本が 外 −0.078」と書いた数字は、cycle8 のコードでは
      F_A = (BUY∧ret<0)∨(SELL∧ret>0) ＝ **逆向き**群の diff だった。つまり実際の向きは「逆向きの本が悪い＝同向き（継続）の本が良い」。
      主スクリプト Q6 の入口フィルタ「A（同向き）を建てない」は向きが逆なので、正しい向き「¬A（逆向き）を建てない」で採点し直す。
      あわせて 本番窓（JST7-12）・壁種・側 の外セル、月ブロック bootstrap の CI を出す（記述）。
読取りのみ。入力 data/c8_crossasset_features.csv。書き込み data/refute_c8_goldmom_b.md のみ。
"""
import os, math, time
import numpy as np, pandas as pd
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c8_goldmom_b.md"); rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, (d / se if se > 0 else np.nan)
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv"))
X["sgn"] = np.where(X.side == "BUY", 1.0, -1.0); r = X["ret24h_XAU"].to_numpy()
X = X[~np.isnan(r) & (r != 0)].copy(); X["A"] = (X.sgn * X.ret24h_XAU) > 0
X["mon"] = pd.to_datetime(X.entry_time, unit="s").dt.to_period("M").astype(str)
say(f"# [REFUTE c8 goldmom b] 事後フォロー — {time.strftime('%Y-%m-%d %H:%M')}")
say("## 1. 正しい向きの入口フィルタ『逆向き(¬A) を建てない』（補遺 D 禁止領域・数字のみ）")
W = {"在2010-20": X.year <= 2020, "在2012-20": (X.year >= 2012) & (X.year <= 2020), "外2021-26": X.year >= 2021, "近年2024-26": X.year >= 2024, "2025-26H1": X.year >= 2025}
for wn, m in W.items():
    df = X[m]; R = df.R.to_numpy(); A = df.A.to_numpy(); risk = df.risk.to_numpy()
    top = R >= np.quantile(R, 0.9); keep = A[top].mean()
    row = [f"除外(¬A) {(~A).sum()} 本 ΣgrossR {R[~A].sum():+.1f}・残す(A) {A.sum()} 本 ΣgrossR {R[A].sum():+.1f}・上位10% 残存 {keep*100:.0f}%（A 比率 {A.mean():.2f}）"]
    for s in (0.10, 0.22, 0.44):
        net = R - s / risk; d, t = welch(net[A], net[~A]); row.append(f"s={s}: 残す−除外 {d:+.4f} (t{t:+.2f})・残す平均 {net[A].mean():+.4f} vs 全本 {net.mean():+.4f}")
    say(f"- {wn}: " + " / ".join(row))
say("- 研究レーン基準（在 t≥2 ∧ 外 t≥1.5 ∧ 残存≥90%）: 在2010-20 の diff は負（主スクリプト Q2: −0.015 t−0.74）なので **FAIL**（在で逆符号）。")
say("\n## 2. 外 2021-26 のセル（記述・Bonferroni α=0.05/8）")
df = X[W["外2021-26"]]
cells = {"JST7-12": (df.jh >= 7) & (df.jh <= 12), "JST13-20": (df.jh >= 13) & (df.jh <= 20), "JST21-6": (df.jh >= 21) | (df.jh <= 6),
         "outer": df.wall_kind == "outer", "mid": df.wall_kind == "mid", "BUY": df.side == "BUY", "SELL": df.side == "SELL",
         "JST7-12×outer": (df.jh >= 7) & (df.jh <= 12) & (df.wall_kind == "outer")}
for k, cm in cells.items():
    q = df[cm]; d, t = welch(q.R[q.A], q.R[~q.A]); say(f"- {k}: diff {d:+.4f} t {t:+.2f} (n{q.A.sum()}:{(~q.A).sum()})")
say("\n## 3. 月ブロック bootstrap（外 2021-26・2000 回）: diff の 95% CI")
mons = df.mon.unique(); byM = {m_: df[df.mon == m_] for m_ in mons}
bs = []
for _ in range(2000):
    pick = rng.choice(mons, len(mons), replace=True); q = pd.concat([byM[m_] for m_ in pick])
    bs.append(q.R[q.A].mean() - q.R[~q.A].mean())
bs = np.array(bs); say(f"- 点推定 {df.R[df.A].mean()-df.R[~df.A].mean():+.4f}・月ブロック 95% CI [{np.quantile(bs,0.025):+.4f}, {np.quantile(bs,0.975):+.4f}]・P(diff≤0) {(bs<=0).mean():.3f}")
say("\n## 4. 半年別（2021H1..2026H1）diff・t")
X["half"] = X.year.astype(str) + np.where(pd.to_datetime(X.entry_time, unit="s").dt.month <= 6, "H1", "H2")
row = []
for h, q in X[X.year >= 2021].groupby("half"):
    d, t = welch(q.R[q.A], q.R[~q.A]); row.append(f"{h} {d:+.3f} (t{t:+.1f}, n{len(q)})")
say("- " + " / ".join(row))
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
