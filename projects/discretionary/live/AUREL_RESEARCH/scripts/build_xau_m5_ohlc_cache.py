# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-10] XAU M5 OHLC キャッシュ構築（読取のみ・年ごとに load_m5 → npz）。
出力: data/macro/XAU_m5_ohlc.npz（ts int64 秒 UTC・open/high/low/close float64）。
既存 XAU_m5_close.npz（同じ m5_loader 由来・1728576 本）と ts が一致することを印字で確認する。
Dukascopy m1 bid チャンクを読むだけ。本番・プロップには触れない。
"""
import os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
W2W = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
sys.path.insert(0, W2W)
from m5_loader import load_m5
OUT = os.path.join(ROOT, "data", "macro", "XAU_m5_ohlc.npz")
t0 = time.time(); fr = []
for y in range(2010, 2027):
    a, b = "%d-01-01" % y, "%d-01-01" % (y + 1)
    if b > "2026-07-01": b = "2026-07-01"
    if a >= "2026-07-01": break
    try:
        m = load_m5(a, b); fr.append(m); print(y, len(m), "%.0fs" % (time.time() - t0), flush=True)
    except FileNotFoundError as e:
        print("skip", y, e, flush=True)
m5 = pd.concat(fr); m5 = m5[~m5.index.duplicated(keep="first")].sort_index()
# pandas 3 は index が datetime64[ms]/[s] になり得る → 単位に依存しない epoch 秒変換（v1 は //1e9 で 1262 になっていた・close npz の ts で差し替え済み）
ts = ((m5.index.tz_convert(None) - pd.Timestamp(0)) // pd.Timedelta(seconds=1)).to_numpy().astype(np.int64)
np.savez_compressed(OUT, ts=ts, open=m5["open"].to_numpy(float), high=m5["high"].to_numpy(float),
                    low=m5["low"].to_numpy(float), close=m5["close"].to_numpy(float))
zc = np.load(os.path.join(ROOT, "data", "macro", "XAU_m5_close.npz"))
same_len = len(zc["ts"]) == len(ts)
print("bars", len(ts), "close npz bars", len(zc["ts"]), "ts identical" if same_len and np.array_equal(zc["ts"].astype(np.int64), ts) else "TS MISMATCH",
      "close max|diff| %.4f" % (np.abs(zc["close"] - m5["close"].to_numpy()).max() if same_len else float("nan")))
print("done %.0fs ->" % (time.time() - t0), OUT, flush=True)
