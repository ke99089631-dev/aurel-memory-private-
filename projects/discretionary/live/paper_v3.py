# -*- coding: utf-8 -*-
"""
車線3 v3a エンジン: 品質壁(walls.py)＋採点(backtest_v3)の場面を24/5で貯める研究レーン。
  ★方針: 手製の採点フィルタで間引かない。品質壁の全候補を decision(TAKE/SKIP)・score・特徴つきで記録。
          「採点が本当に勝ちを分けるか」はデータで検証し、正しい見分けは後でC2(分類器)が学ぶ。
  データ源: /api/data (Tailscale IP)。専用台帳 paper_ledger_v3.jsonl（車線1と非混合・発注なし・金ゼロ）。
"""
import os
import sys
import json
import time
import datetime as dt
import urllib.request

sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from backtest_v3 import backtest_v3

HERE = os.path.dirname(os.path.abspath(__file__))
API = "http://100.73.107.61:8793/api/data?n=2000"
PAPER = os.path.join(HERE, "paper_ledger_v3.jsonl")
INTERVAL = 300


def _fetch_bars():
    with urllib.request.urlopen(API, timeout=20) as r:
        d = json.loads(r.read().decode("utf-8"))
    bars = d.get("bars", [])
    if not bars:
        return None
    df = pd.DataFrame(bars)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.set_index("dt")[["open", "high", "low", "close"]]


def _seen():
    seen, maxn = set(), 0
    if os.path.exists(PAPER):
        for line in open(PAPER, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("entry_time") is not None:
                seen.add(int(r["entry_time"]))
            try:
                maxn = max(maxn, int(str(r.get("id", "V-0")).split("-")[1]))
            except Exception:
                pass
    return seen, maxn


def sync_once():
    m5 = _fetch_bars()
    if m5 is None or len(m5) < 160:
        return 0
    tr = backtest_v3(m5, record_skips=True)
    if not len(tr):
        return 0
    seen, maxn = _seen()
    added = 0
    for _, row in tr.iterrows():
        et = int(pd.Timestamp(row["entry_time"]).timestamp())
        if et in seen:
            continue
        maxn += 1
        rec = {
            "id": "V-%04d" % maxn, "lane": "3v3a", "kind": "paper_v3",
            "side": row["side"], "entry": float(row["entry"]),
            "sl": float(row["sl"]), "tp": float(row["tp"]),
            "exit": float(row["exit"]), "exit_reason": row["exit_reason"],
            "R": float(row["R"]), "hold_bars": int(row["hold_bars"]),
            "wall": float(row["wall"]), "width": float(row["width"]),
            "wall_touches": int(row["wall_touches"]),
            "score": float(row["score"]), "decision": row["decision"],
            "skip_reason": row["skip_reason"], "real_rate": row["real_rate"],
            "jst_hour": int(row["jst_hour"]),
            "features": {
                "break_str_atr": row["break_str_atr"],
                "entry_body_ratio": row["entry_body_ratio"],
                "reject_wick_ratio": row["reject_wick_ratio"],
                "wall_touches": int(row["wall_touches"]),
            },
            "up": float(row["up"]), "dn": float(row["dn"]), "mid": float(row["mid"]),
            "entry_time": et,
            "entry_jst": pd.Timestamp(row["entry_time"]).tz_convert("Asia/Tokyo").strftime("%Y-%m-%d %H:%M"),
            "logged_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(PAPER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        seen.add(et)
        added += 1
    return added


def main():
    print("車線3 v3a エンジン起動（品質壁＋採点・5分ごと・発注なし・金ゼロ）", flush=True)
    while True:
        try:
            n = sync_once()
            if n:
                print("%s +%d (v3a)" % (dt.datetime.now().strftime("%H:%M:%S"), n), flush=True)
        except Exception as e:
            sys.stderr.write("v3 sync err: %s\n" % e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    if "--once" in sys.argv:
        print("追加:", sync_once())
    else:
        main()
