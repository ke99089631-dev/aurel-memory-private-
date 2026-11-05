# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-05 — refute_c7_sellstall.py の追補（**結果を見た後**の追加・判定には使わない・理由を記す）。
理由: 主スクリプトで、B3（含み ≈0）の側差 SELL−BUY が 外 2021-26 で k=3..24 の全てで負（S3 family-wise p 0.029）、
      2014-17 では逆符号（SELL +0.108 / BUY −0.077・側差 t +2.55）だった。符号が時代で反転する側差は、
      「停滞 SELL が腐る」構造ではなく **金のトレンド（ドリフト）が側で条件づけた部分集合に漏れている**だけの疑いが強い。
検査: 期間ごとに (a) 無条件の R* の側差 BUY−SELL（全本・停滞条件なし＝ドリフトの代理）、
      (b) 固定 k=3 の e の側差（全水準・建玉中）、(c) 停滞セル (k=24,B3) の e の側差 を並べ、
      年別 17 点で (a) と (c) の Spearman を出す。(a) と (c) が同じ向きに動けば、(c) は (a) の一部＝出口情報ではない。
読取りのみ・既存キャッシュのみ。書き込みは data/refute_c7_sellstall_b.md のみ。
"""
import json, os, math, time
import numpy as np, pandas as pd
from scipy.stats import spearmanr

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c7_sellstall_b.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return float("nan"), float("nan")
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se if se > 0 else float("nan")

J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]]).sort_values("entry_time").reset_index(drop=True)
FT = J["frozen"]["FEED_TOL"]; z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"]
n = len(df); assert len(off) - 1 == n
risk = df.risk.to_numpy(); ft = FT / risk; R0 = df.R.to_numpy(); hold = df.hold.to_numpy(); er = df.exit_reason.to_numpy()
Rstar = R0 + ft * ((er == "SL") | (er == "TP")); isB = (df.side == "BUY").to_numpy(); year = df.year.to_numpy()
def ek(k):
    alive = np.nonzero(hold > k)[0]; clk = clR[off[alive] + k]; return alive, clk, Rstar[alive] - clk
a3, cl3, e3 = ek(3); a24, cl24, e24 = ek(24); b3_24 = (cl24 > -0.2) & (cl24 < 0.2)

say(f"# AUREL [REFUTE] 追補 — 停滞 SELL の負は金のドリフト（側差）の漏れか  {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c7_sellstall_b.py・結果を見た後の追加・判定不使用)")
say("| 期間 | n BUY/SELL | (a) 無条件 R* BUY−SELL / Welch t | (b) k=3 全水準 e BUY−SELL / t | (c) 停滞 (k=24,B3) e BUY−SELL / t |")
say("|---|---|---|---|---|")
periods = [("2010-13", year <= 2013), ("2014-17", (year >= 2014) & (year <= 2017)), ("2018-21", (year >= 2018) & (year <= 2021)), ("2022-26", year >= 2022),
           ("在2010-20", year <= 2020), ("外2021-26", year >= 2021), ("2021-23", (year >= 2021) & (year <= 2023)), ("近年2024-26", year >= 2024), ("2025-26H1", year >= 2025)]
for lab, m in periods:
    da, ta = welch(Rstar[m & isB], Rstar[m & ~isB])
    m3 = m[a3]; db, tb = welch(e3[m3 & isB[a3]], e3[m3 & ~isB[a3]])
    m24 = m[a24] & b3_24; dc, tc = welch(e24[m24 & isB[a24]], e24[m24 & ~isB[a24]])
    say(f"| {lab} | {(m & isB).sum()}/{(m & ~isB).sum()} | {da:+.4f} / {ta:+.2f} | {db:+.4f} / {tb:+.2f} | {dc:+.4f} / {tc:+.2f} |")
say()
say("## 年別（17 点）: (a) 無条件側差 vs (c) 停滞側差")
say("| 年 | (a) R* BUY−SELL | (b) k=3 e BUY−SELL | (c) 停滞 e BUY−SELL | n(c) |"); say("|---|---|---|---|---|")
A = []; B = []; C = []
for y in range(2010, 2027):
    m = year == y
    da, _ = welch(Rstar[m & isB], Rstar[m & ~isB]); m3 = m[a3]; db, _ = welch(e3[m3 & isB[a3]], e3[m3 & ~isB[a3]])
    m24 = m[a24] & b3_24; dc, _ = welch(e24[m24 & isB[a24]], e24[m24 & ~isB[a24]])
    A.append(da); B.append(db); C.append(dc)
    say(f"| {y} | {da:+.3f} | {db:+.3f} | {dc:+.3f} | {(m24).sum()} |")
A = np.array(A); B = np.array(B); C = np.array(C)
ra, pa = spearmanr(A, C); rb, pb = spearmanr(B, C); rab, pab = spearmanr(A, B)
say(f"Spearman 年別: (a)×(c) **ρ {ra:+.2f} (p {pa:.3f})**／(b)×(c) ρ {rb:+.2f} (p {pb:.3f})／(a)×(b) ρ {rab:+.2f} (p {pab:.3f})。符号一致 (a),(c): {int(np.sum(np.sign(A)==np.sign(C)))}/17。")
say("（(a) は停滞条件なしの全本の側差＝その期間に金がどちらへドリフトしたかの代理。(c) が (a) と同じ向きに動くなら、停滞 SELL の負は出口情報ではなくトレンドの側への漏れ。）")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
