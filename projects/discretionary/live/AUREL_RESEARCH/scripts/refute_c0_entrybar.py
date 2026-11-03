# -*- coding: utf-8 -*-
"""
AUREL 反証レーン — cycle0 C4「勝ち(TP)の50%は途中 −0.5R まで沈む」の建玉足アーティファクト検査。
読取りのみ。bars は serve_chart の /api/data（GET・読むだけ）を data/refute_api_bars_probe.json に保存したもの（5000本=2026-10-08..11-03）。

疑い: _simulate は建玉足(ie)を丸ごと含めて MAE を取る。再加速は「直前足の安値割れ(買いは高値超え)」の逆指値なので、
建玉足の始値はトリガーの反対側にあり、建玉足の高値(売り)/安値(買い)は**約定前**の値動きを含む。
→ 建玉足の逆行幅は「建玉後に沈んだ」のではなく幾何（足のレンジ÷risk、MIN_SL_W=3.0 ≈ ATR）で出る。
検査: 建玉足を除いた MAE_ex0 で C4 を再計算し、建玉足終値から出発するRW(θ=0.22・refute_c0_path と同じ)の期待と比べる。
"""
import os, sys, json, math, collections
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE); LIVE = os.path.dirname(RES)
sys.path.insert(0, HERE)
from refute_c0_path import load_ledger, p_hit, fit_theta, FEED_TOL

OUT = os.path.join(RES, "data", "refute_c0_entrybar_result.md")
L = []
def say(s=""):
    print(s, flush=True); L.append(s)

df = load_ledger()
bars = json.load(open(os.path.join(RES, "data", "refute_api_bars_probe.json"), encoding="utf-8"))["bars"]
B = pd.DataFrame(bars).sort_values("time").drop_duplicates("time").reset_index(drop=True)
pos = {int(t): i for i, t in enumerate(B.time)}
o = B.open.to_numpy(); h = B.high.to_numpy(); l = B.low.to_numpy(); c = B.close.to_numpy()
t_first, t_last = int(B.time.iloc[0]), int(B.time.iloc[-1])
say("# AUREL [REFUTE] cycle0 C4 建玉足アーティファクト検査")
say("API bars %d 本 %s..%s(UTC)" % (len(B), pd.Timestamp(t_first, unit="s"), pd.Timestamp(t_last, unit="s")))

# 台帳には exit_time がある → 再読込
recs = [json.loads(x) for x in open(os.path.join(LIVE, "setup_ledger.jsonl"), encoding="utf-8") if x.strip()]
exit_t = {}
for r in recs:
    ra = r.get("reaccel")
    if isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("exit_time"):
        exit_t[r["target"] if r.get("kind") == "update" else r.get("id")] = (int(ra["exit_time"]), float(ra["entry"]), float(ra["sl"]))
rows = []
for _, t in df.iterrows():
    if t.id not in exit_t: continue
    et, entry, sl = exit_t[t.id]
    ie = pos.get(int(t.entry_time)); ek = pos.get(et)
    if ie is None or ek is None: continue
    risk = abs(entry - sl); sgn = 1.0 if t.side == "BUY" else -1.0
    fav = sgn * ((h if sgn > 0 else l)[ie:ek + 1] - entry) / risk
    adv = -sgn * ((l if sgn > 0 else h)[ie:ek + 1] - entry) / risk
    rows.append({"id": t.id, "R": t.R, "b": t.b, "ft": t.ft, "hold": ek - ie, "mfe_led": t.mfe, "mae_led": t.mae,
                 "mfe_rec": fav.max(), "mae_rec": adv.max(), "mae_bar0": adv[0], "mfe_bar0": fav[0],
                 "mae_ex0": adv[1:].max() if len(adv) > 1 else 0.0, "mfe_ex0": fav[1:].max() if len(fav) > 1 else 0.0,
                 "x0": sgn * (c[ie] - entry) / risk, "open_gap": -sgn * (o[ie] - entry) / risk, "bar0_range_R": (h[ie] - l[ie]) / risk})
g = pd.DataFrame(rows)
say("API期間に建玉・決着が収まる台帳 本数 n=%d（全体 %d）" % (len(g), len(df)))
say("再現チェック: |MAE_rec − MAE_台帳| 中央値 %.3f 最大 %.3f / |MFE_rec − MFE_台帳| 中央値 %.3f 最大 %.3f（≈0なら同じ足で再現できている）" % (
    (g.mae_rec - g.mae_led).abs().median(), (g.mae_rec - g.mae_led).abs().max(), (g.mfe_rec - g.mfe_led).abs().median(), (g.mfe_rec - g.mfe_led).abs().max()))
say()
w = g.R > 0
say("## 建玉足(約定前を含む)の寄与")
say("- 建玉足の始値はトリガーの反対側(open_gap>0=始値が逆行側): 全本の %.0f%%、中央値 %+.2fR。建玉足レンジ÷risk 中央値 %.2f" % (100 * (g.open_gap > 0).mean(), g.open_gap.median(), g.bar0_range_R.median()))
say("- 建玉足だけの逆行 MAE_bar0: 中央値 %.2fR、≥0.5R の本 %.0f%%（勝ち本では %.0f%%）" % (g.mae_bar0.median(), 100 * (g.mae_bar0 >= 0.5).mean(), 100 * (g.mae_bar0[w] >= 0.5).mean()))
say("- 勝ち本で MAE 全体の最大が建玉足で出ている割合: %.0f%%" % (100 * (g.mae_bar0[w] >= g.mae_rec[w] - 1e-9).mean()))
say()
say("## C4 の再計算（この部分集合）")
say("| 定義 | 勝ちn | −0.5R まで沈んだ割合 |"); say("|---|---|---|")
say("| 台帳どおり(建玉足込み) | %d | %.1f%% |" % (w.sum(), 100 * (g.mae_rec[w] >= 0.5).mean()))
say("| 建玉足を除く(ie+1..exit) | %d | %.1f%% |" % (w.sum(), 100 * (g.mae_ex0[w] >= 0.5).mean()))
say("| 建玉足のみ | %d | %.1f%% |" % (w.sum(), 100 * (g.mae_bar0[w] >= 0.5).mean()))
# RW 期待: 建玉足終値 x0 から出発し、−0.5 に TP より先に到達して、その後 TP
th = fit_theta(df, int((df.R > 0).sum()))
def dip_expect(gg, th):
    num = den = 0.0
    for _, t in gg.iterrows():
        a = 1.0 - t.ft; u = t.b + t.ft
        if t.hold == 0: continue
        x0 = min(max(t.x0, -a + 1e-6), u - 1e-6)
        pT = p_hit(x0, a, u, th)
        if x0 <= -0.5: pdip_T = pT
        else:
            p_dip = 1.0 - p_hit(x0, 0.5, u, th); pdip_T = p_dip * p_hit(-0.5, a, u, th)
        num += pdip_T; den += pT
    return num / den if den else float("nan")
e_rw = dip_expect(g, th); e_rw0 = dip_expect(g, 0.0)
gw = g[w & (g.hold > 0)]
k = int((gw.mae_ex0 >= 0.5).sum()); n = len(gw)
z = (k - n * e_rw) / math.sqrt(n * e_rw * (1 - e_rw)); pv = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
say()
say("建玉足を除いた C4（hold≥1 の勝ち n=%d）: 観測 %d (%.1f%%) vs 建玉足終値から出発するRW期待 θ=%.2f: %.1f%% / θ=0: %.1f%%  z=%+.2f p=%.3f" % (n, k, 100 * k / n, th, 100 * e_rw, 100 * e_rw0, z, pv))
say()
say("## 同じ検査を C1 側(建玉足の有利方向 MFE_bar0)にも")
say("- 建玉足だけで +0.5R に届いた本 %.0f%%、建玉足内で決着(hold=0) %.0f%%" % (100 * (g.mfe_bar0 >= 0.5).mean(), 100 * (g.hold == 0).mean()))
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
