#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
畑A' = US100 壁→壁 SL0.50版(改善候補) 前向き観測。2026-10-21 会長GO(放置しない)。
  畑A(SL0.33)と並走し、SL0.50(1aでSharpe0.78→0.88・コスト耐性最良)が生でも良いか裏取り。
  独立フィード=yfinance NQ=F・MT5非接続・0円・発注なし。判定=touch_test.run(SL_FRAC_IN=0.50)。
"""
import os, sys, json, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__))
WW = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
for p in (WW, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import pandas as pd
import touch_test as tt
import run_gate as rg

tt.SL_FRAC_IN = 0.50          # ★この版の違い(畑AはデフォルトSL0.33)
LEDGER = os.path.join(HERE, "farm_a2_sl050_forward_ledger.jsonl")
KILL = os.path.join(HERE, "KILL")
NEED_TOUCHES = 2
PROF = {"tp_mm": 0.85}
COST_BPS = 0.81
LIVE_TICKER = "NQ=F"


def seen():
    s = set()
    if os.path.exists(LEDGER):
        for ln in open(LEDGER, encoding="utf-8"):
            try:
                s.add(json.loads(ln)["entry_time"])
            except Exception:
                pass
    return s


def fetch():
    import yfinance as yf
    df = yf.download(LIVE_TICKER, period="60d", interval="5m", auto_adjust=False, progress=False)
    if df is None or len(df) == 0:
        raise RuntimeError("yfinance NQ=F 0件")
    if hasattr(df.columns, "get_level_values"):
        try:
            df.columns = df.columns.get_level_values(0)
        except Exception:
            pass
    df = df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def run_live():
    if os.path.exists(KILL):
        print("KILL"); return
    print("[畑A' SL0.50観測] NQ=F取得...")
    m5 = fetch()
    if len(m5) < tt.BOX_WINDOW + 10:
        print("本数不足"); return
    tr = tt.run(m5, NEED_TOUCHES, PROF)
    if len(tr):
        tr = tr[rg.ny_session_mask(tr["entry_time"])].reset_index(drop=True)
    sn = seen(); new = 0
    if len(tr):
        pos = m5.index.get_indexer(tr["entry_time"]); tr["entry"] = m5["open"].to_numpy()[pos]
        tr["netR"] = tr["R"] - (tr["entry"] * COST_BPS / 10000.0) / tr["risk"]
        for _, r in tr.iterrows():
            et = str(r["entry_time"])
            if et in sn:
                continue
            rec = {"farm": "A2-US100-SL0.50", "entry_time": et, "side": r["side"], "entry": round(float(r["entry"]), 2),
                   "risk": round(float(r["risk"]), 2), "R": round(float(r["R"]), 3), "netR": round(float(r["netR"]), 3),
                   "reason": r["reason"], "need_touches": NEED_TOUCHES, "sl_frac": 0.50, "mode": "observe",
                   "logged_at": time.strftime("%Y-%m-%d %H:%M:%S")}
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            new += 1
    print("新規%d / 累計%d → %s" % (new, len(seen()), LEDGER))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--live", action="store_true"); a = ap.parse_args()
    run_live() if a.live else print("--live で観測")
