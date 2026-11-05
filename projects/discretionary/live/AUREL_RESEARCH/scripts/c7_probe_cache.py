# -*- coding: utf-8 -*-
"""cycle7 準備: 既存キャッシュの構造確認のみ（読取り・数秒）。"""
import json, os, time
import numpy as np
t0 = time.time()
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
c4 = json.load(open(os.path.join(D, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
print("c4 keys:", list(c4.keys()))
print("c4 frozen:", c4.get("frozen"))
t = c4["trades"][0]; print("trade keys:", list(t.keys())); print("sample:", t)
print("n trades", len(c4["trades"]))
z = np.load(os.path.join(D, "refute_c2_fullpaths.npz"))
print("npz:", {k: z[k].shape for k in z.files})
off = z["off"]; print("off[:5]", off[:5], "last", off[-1])
c1 = json.load(open(os.path.join(D, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
print("c1 keys", list(c1.keys()), "frozen", c1.get("frozen"), "generated", c1.get("generated"))
print("c1 trade keys", list(c1["trades"][0].keys()))
print("c1 first entry_time", c1["trades"][0]["entry_time"], "c4 first", c4["trades"][0]["entry_time"])
# 順序一致の確認（npz は c1 の順・entry_time ソート後）
import pandas as pd
e1 = sorted(x["entry_time"] for x in c1["trades"]); e4 = sorted(x["entry_time"] for x in c4["trades"])
print("same entry set:", e1 == e4, "c1 sorted already:", [x["entry_time"] for x in c1["trades"]] == e1)
print("elapsed %.1fs" % (time.time() - t0))
