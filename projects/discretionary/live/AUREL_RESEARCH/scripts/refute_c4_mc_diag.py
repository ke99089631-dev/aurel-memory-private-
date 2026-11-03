# -*- coding: utf-8 -*-
"""
診断: refute_c4_scanpath の離散MC(25-26%)/プラセボ(23.6%)が閉形式RW(31.9%)より低いのは何か。
仮説: MAX_HOLD=288 の時間切れ切断 + σ(κ)校正ずれ → 長い path(=沈みやすい)が TIME に落ちて TP 集合から消える。
検査: κ と MAX_HOLD を変えて TP/SL/TIME 比率と P(沈み|TP) を出し、観測の TIME 率(4.6%)・保有中央値(16)と比べる。
読取りのみ。出力 data/refute_c4_mc_diag.md
"""
import os, sys, json, math
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE); DATA = os.path.join(RES, "data")
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
ft_abs = J["frozen"]["FEED_TOL"]
df = pd.DataFrame(J["trades"]); df["ft"] = ft_abs / df.risk; df["atr"] = pd.to_numeric(df.atr, errors="coerce")
sub = df[(df.hold >= 1) & ((1 - df.ft) > 0.5)]
g = sub[(sub.R > 0) & (sub.exit == "TP") & sub.atr.notna()].sample(150, random_state=3)
rng = np.random.default_rng(7)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)

def run(kappa, max_hold, nsim=300, m=6):
    tp = sl = tm = 0; dip_tp = 0; holds = []
    for _, t in g.iterrows():
        sig = kappa * t.atr / t.risk; ss = sig / math.sqrt(m)
        inc = rng.normal(0.0, ss, size=(nsim, max_hold, m))
        path = t.x0 + np.cumsum(inc.reshape(nsim, -1), axis=1).reshape(nsim, max_hold, m)
        H = path.max(2); Lo = path.min(2); C = path[:, :, -1]
        prev = np.concatenate([np.full((nsim, 1), t.x0), C[:, :-1]], axis=1)
        H = np.maximum(H, prev); Lo = np.minimum(Lo, prev)
        a = 1 - t.ft; u = t.b + t.ft
        sl_hit = Lo <= -a; tp_hit = H >= u; any_hit = sl_hit | tp_hit
        hit = any_hit.any(1); first = np.where(hit, any_hit.argmax(1), max_hold - 1)
        rows = np.arange(nsim); is_sl = sl_hit[rows, first] & hit; is_tp = tp_hit[rows, first] & ~is_sl & hit
        mask = np.arange(max_hold)[None, :] <= first[:, None]
        mae = np.maximum(-np.where(mask, Lo, np.inf).min(1), 0.0)
        tp += int(is_tp.sum()); sl += int(is_sl.sum()); tm += int((~hit).sum()); dip_tp += int((is_tp & (mae >= 0.5)).sum())
        holds.extend((first[is_tp] + 1).tolist())
    n = tp + sl + tm
    say("| κ=%.1f MAX_HOLD=%4d | TP %4.1f%% SL %4.1f%% TIME %4.1f%% | TP保有中央値 %3d | P(沈み|TP) %.1f%% |" % (
        kappa, max_hold, 100 * tp / n, 100 * sl / n, 100 * tm / n, int(np.median(holds)) if holds else -1, 100 * dip_tp / max(tp, 1)))

say("# 診断: MC の時間切れ切断と σ 校正")
say("観測(scan hold≥1): TIME %.1f%%  TP本の保有中央値 %d  全体保有中央値 %d  ATR/risk 中央値 %.2f" % (
    100 * (sub.exit == "TIME").mean(), int(sub[sub.exit == "TP"].hold.median()), int(sub.hold.median()), float((sub.atr / sub.risk).median())))
say("| 設定 | 決着比率 | 保有 | P(沈み|TP) |"); say("|---|---|---|---|")
for kappa in (0.4, 1.0, 2.0):
    run(kappa, 288)
run(1.0, 1500); run(2.0, 1500)
open(os.path.join(DATA, "refute_c4_mc_diag.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
