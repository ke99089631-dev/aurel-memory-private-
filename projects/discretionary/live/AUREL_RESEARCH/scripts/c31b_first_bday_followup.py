"""
[cycle31 補足 b・事後] k=+1（月初 1 営業日）の単独セルを family-wise（k∈[−8..+3] 12 セルの max|t|・置換 2000 回）で読む。
事後観測なので判定には使わない。年別符号比率・曜日別（月曜＝週末込み vs 火〜金）も印字。
"""
import os, sys, math, time, importlib.util
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c31b_first_bday_followup.md"); L = []; T0 = time.time()
def say(s=""): print(s, flush=True); L.append(s)
# 本体の df を再構築（本体を import すると本体の出力が走るので、本体の結果 md と同じ定義をここで再実行）
sys.argv = ["x"]; import io, contextlib
spec = importlib.util.spec_from_file_location("c31", os.path.join(HERE, "c31_turn_of_month_flows.py"))
mod = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(mod)
df = mod.df; WIN = mod.WIN; welch = mod.welch
rng = np.random.default_rng(20261110)
say(f"# [cycle31 補足 b・事後] 月初 1 営業日（k=+1）の family-wise 読み — {time.strftime('%Y-%m-%d %H:%M')}")
KS = list(range(-8, 4))
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)].reset_index(drop=True)
    d_ = d_.assign(r=d_.r - d_.groupby("year").r.transform("mean"))  # 年FE
    ts = {}
    for k in KS:
        m = (d_.k == k).values; t, se = welch(d_.r[m], d_.r[~m]); ts[k] = (t, d_.r[m].mean() - d_.r[~m].mean(), se)
    t1, dl1, se1 = ts[1]
    # 置換: k ラベルを日ごとにシャッフル（月内位置を壊す）→ 12 セル max|t| の帰無
    kv = d_.k.values.copy(); r = d_.r.values; mx = []
    for _ in range(2000):
        kp = rng.permutation(kv); mt = 0.0
        for k in KS:
            m = kp == k
            a = r[m]; b = r[~m]; se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); mt = max(mt, abs((a.mean() - b.mean()) / se))
        mx.append(mt)
    mx = np.array(mx); p_fw = (mx >= abs(t1)).mean()
    yrs = sorted(d_.year.unique()); sg = [(d_[(d_.year == y) & (d_.k == 1)].r.mean() > d_[(d_.year == y) & (d_.k != 1)].r.mean()) for y in yrs]
    mon = (d_.k == 1) & (d_.wd == 0); oth = (d_.k == 1) & (d_.wd != 0)
    say(f"- {wn}: k=+1 Δ {dl1:+.1f} bp/日（t {t1:+.2f}・MDE {2*se1:.1f}・順位 {sorted([abs(v[0]) for v in ts.values()], reverse=True).index(abs(t1))+1}/12）"
        f"・12 セル max|t| の置換帰無 p_fw {p_fw:.3f}（帰無 max|t| 中央値 {np.median(mx):.2f}）・年別 正 {sum(sg)}/{len(sg)}"
        f"・月曜（週末込み）n {mon.sum()} {d_.r[mon].mean():+.0f} vs 火〜金 n {oth.sum()} {d_.r[oth].mean():+.0f} bp")
    say("  12 セル t: " + " ".join(f"{k:+d}:{ts[k][0]:+.1f}" for k in KS))
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
