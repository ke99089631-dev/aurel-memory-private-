# -*- coding: utf-8 -*-
"""cycle10 準備: 反証 05:30 のデータ衛生指摘（XAU npz は暦時刻の完全格子・週末は前値埋め）を US500/US100 npz でも確認する。
読取りのみ・数秒。方法論⑪候補: npz を読んだら min/max 時刻に加えて flat 足の比率を曜日別に印字する。"""
import os, time
import numpy as np, pandas as pd
t0 = time.time()
MAC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "macro")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle10 prep] npz flat-bar hygiene — {time.strftime('%Y-%m-%d %H:%M')}")
for sym in ("XAU", "US500", "US100"):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(np.float64)
    dt = pd.to_datetime(ts, unit="s")
    flat = np.r_[False, np.diff(cl) == 0]
    dow = dt.dayofweek
    per = pd.Series(flat).groupby(dow).mean()
    gaps = np.diff(ts); grid = (gaps == 300).mean()
    say(f"- {sym}: n={len(ts)} {dt[0]}..{dt[-1]} UTC, 5-min grid 連続率 {grid*100:.2f}%, flat 足 全体 {flat.mean()*100:.1f}%, "
        f"曜日別 Mon..Sun " + " ".join(f"{per.get(d, np.nan)*100:.1f}" for d in range(7)))
say(f"実行 {time.time()-t0:.1f} s")
open(os.path.join(os.path.dirname(MAC), "c10_npz_hygiene.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
