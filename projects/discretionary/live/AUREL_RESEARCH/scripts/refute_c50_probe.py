# -*- coding: utf-8 -*-
"""[反証レーン c50 事前プローブ] npz の規約確認のみ（判定なし・読取のみ）。"""
import os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
MAC = os.path.join(ROOT, "data", "macro")
for f in ("XAU_m5_close.npz", "XAU_m5_ohlc.npz", "US100_m5_close.npz", "US500_m5_close.npz"):
    p = os.path.join(MAC, f)
    z = np.load(p)
    ks = list(z.keys())
    ts = z["ts"].astype(np.int64)
    t = pd.to_datetime(ts, unit="s", utc=True)
    print(f"== {f}: keys={ks} n={len(ts)}")
    print(f"   shapes={{{', '.join(k + ':' + str(z[k].shape) for k in ks)}}}")
    print(f"   span {t[0]} .. {t[-1]}  step_mode={pd.Series(np.diff(ts)).mode().tolist()[:2]}")
    print(f"   first ts%300={ts[0] % 300}  minute of first 3: {[x.strftime('%Y-%m-%d %H:%M') for x in t[:3]]}")
# OHLC 規約: ts が足の開始か終了か → close[i] と次足の open[i+1] の一致で判定
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
if "open" in z:
    o = z["open"].astype(float); c = z["close"].astype(float); ts = z["ts"].astype(np.int64)
    cont = np.diff(ts) == 300
    same = np.isclose(o[1:][cont], c[:-1][cont])
    print(f"== OHLC 連続足で open[i+1]==close[i]: {same.mean()*100:.1f}% (n {cont.sum()})")
    h = z["high"].astype(float); l = z["low"].astype(float)
    print(f"   high>=max(o,c) {np.mean(h >= np.maximum(o, c) - 1e-9)*100:.2f}%  low<=min {np.mean(l <= np.minimum(o, c) + 1e-9)*100:.2f}%")
# close npz と ohlc npz の close 一致
zc = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
a = pd.Series(zc["close"].astype(float), index=zc["ts"].astype(np.int64))
b = pd.Series(z["close"].astype(float), index=z["ts"].astype(np.int64))
j = a.index.intersection(b.index)
print(f"== close npz ∩ ohlc npz: n {len(j)} / close {len(a)} / ohlc {len(b)} ・最大|差| {np.abs(a.loc[j].to_numpy()-b.loc[j].to_numpy()).max():.4f}")
