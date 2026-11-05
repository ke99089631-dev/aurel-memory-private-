# -*- coding: utf-8 -*-
"""
c3_inventory.py — DATA_MAP v1 用の棚卸し（読むだけ・書かない）
対象: live フォルダ直下の *.jsonl と AUREL_RESEARCH/data/ のキャッシュ。
各ファイルの 行数 / キー集合 / 時刻範囲 / 主要カテゴリ件数 を標準出力に出す。
秘密は読まない（.env/キー類は対象外）。MT5 には接続しない。
"""
import json, os, sys, glob, collections, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
DATA = os.path.join(LIVE, "AUREL_RESEARCH", "data")

TIME_KEYS = ("entry_time", "time", "ts", "t", "opened_at", "closed_at", "exit_time", "signal_time", "bar_time")

def summarize_jsonl(path, maxrows=None):
    n = 0; bad = 0
    keys = collections.Counter()
    tmin = tmax = None
    cats = {k: collections.Counter() for k in ("kind", "type", "status", "side", "setup", "result", "exit", "symbol", "wall", "tf")}
    tkey_used = None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n += 1
            try:
                d = json.loads(line)
            except Exception:
                bad += 1
                continue
            if not isinstance(d, dict):
                continue
            keys.update(d.keys())
            for tk in TIME_KEYS:
                if tk in d and isinstance(d[tk], str) and len(d[tk]) >= 10:
                    v = d[tk]
                    tkey_used = tk
                    tmin = v if tmin is None or v < tmin else tmin
                    tmax = v if tmax is None or v > tmax else tmax
                    break
            for ck in cats:
                if ck in d and isinstance(d[ck], (str, int, float, bool)):
                    cats[ck][str(d[ck])] += 1
    print(f"\n=== {os.path.basename(path)}  rows={n} bad={bad} size={os.path.getsize(path)//1024}KB")
    print(f"  time[{tkey_used}]: {tmin} .. {tmax}")
    print("  keys:", ", ".join(f"{k}({c})" for k, c in keys.most_common(60)))
    for ck, c in cats.items():
        if c:
            print(f"  {ck}:", dict(c.most_common(12)))

def summarize_json_cache(path):
    sz = os.path.getsize(path) // 1024
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        obj = json.load(f)
    print(f"\n=== data/{os.path.basename(path)} size={sz}KB type={type(obj).__name__}")
    if isinstance(obj, dict):
        print("  top keys:", list(obj.keys())[:30])
        for k, v in obj.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print(f"  {k}: list[{len(v)}] rec keys:", list(v[0].keys())[:40])
                print("   first:", json.dumps(v[0])[:400])
                break
            if isinstance(v, dict) and v:
                fk = next(iter(v))
                print(f"  {k}: dict[{len(v)}] first key={fk} -> {json.dumps(v[fk])[:300]}")
    elif isinstance(obj, list):
        print(f"  list[{len(obj)}]")
        if obj and isinstance(obj[0], dict):
            print("  rec keys:", list(obj[0].keys()))
            print("  first:", json.dumps(obj[0])[:400])
            print("  last :", json.dumps(obj[-1])[:400])

def main():
    for p in sorted(glob.glob(os.path.join(LIVE, "*.jsonl"))):
        try:
            summarize_jsonl(p)
        except Exception as e:
            print(f"\n=== {os.path.basename(p)} ERROR {e}")
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        try:
            summarize_json_cache(p)
        except Exception as e:
            print(f"\n=== data/{os.path.basename(p)} ERROR {e}")
    for p in sorted(glob.glob(os.path.join(DATA, "*.npz"))):
        import numpy as np
        z = np.load(p, allow_pickle=False)
        print(f"\n=== data/{os.path.basename(p)} size={os.path.getsize(p)//1024//1024}MB")
        for k in z.files:
            a = z[k]
            print(f"  {k}: shape={a.shape} dtype={a.dtype}")

if __name__ == "__main__":
    main()
