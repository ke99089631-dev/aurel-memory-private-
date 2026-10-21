#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
畑C（EUR 壁→壁）★探索レーン★ — 観測のみ(dry)。2026-10-21 会長GO(A=探索で今すぐ)。
================================================================================
★畑A/Bと違い「14年関門が未確定」(Dukascopy EUR取得が0バイトで失敗)。これは探索=まだ畑に昇格してない。
狙い: EURは米株(US100/S&P)と非連動(日次相関-0.07の兆候)=分散が効くかを生で見る。
独立フィード=yfinance EURUSD=X(FX現物)。FXは24時間→NYマスクなし(全時間)。
★お金ゼロ・MT5非接続・発注なし・金システム非競合。判定=touch_test.run verbatim。
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

LEDGER = os.path.join(HERE, "farm_c_eur_explore_ledger.jsonl")
KILL = os.path.join(HERE, "KILL")
NEED_TOUCHES = 2
PROF = {"tp_mm": 0.85}
COST_BPS = 0.50               # EUR(FX)は最も狭い・保守値
LIVE_TICKER = "EURUSD=X"


def seen_entry_times():
    s = set()
    if os.path.exists(LEDGER):
        for ln in open(LEDGER, encoding="utf-8"):
            try:
                s.add(json.loads(ln)["entry_time"])
            except Exception:
                pass
    return s


def emit(m5, dry=True):
    tr = tt.run(m5, NEED_TOUCHES, PROF)   # FX=全時間(NYマスクなし)
    if len(tr) == 0:
        return 0, tr
    tr = tr.reset_index(drop=True)
    pos = m5.index.get_indexer(tr["entry_time"])
    tr["entry"] = m5["open"].to_numpy()[pos]
    tr["netR"] = tr["R"] - (tr["entry"] * COST_BPS / 10000.0) / tr["risk"]
    seen = seen_entry_times()
    new = 0
    for _, r in tr.iterrows():
        et = str(r["entry_time"])
        if et in seen:
            continue
        rec = {"farm": "C-EUR-EXPLORE", "entry_time": et, "side": r["side"],
               "entry": round(float(r["entry"]), 5), "risk": round(float(r["risk"]), 5),
               "R": round(float(r["R"]), 3), "netR": round(float(r["netR"]), 3),
               "reason": r["reason"], "wtouch": int(r["wtouch"]),
               "need_touches": NEED_TOUCHES, "mode": "explore-observe", "logged_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        if not dry:
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        new += 1
    return new, tr


def fetch_live_m5():
    import yfinance as yf
    df = yf.download(LIVE_TICKER, period="60d", interval="5m", auto_adjust=False, progress=False)
    if df is None or len(df) == 0:
        raise RuntimeError("yfinance %s 取得0件" % LIVE_TICKER)
    if hasattr(df.columns, "get_level_values"):
        try:
            df.columns = df.columns.get_level_values(0)
        except Exception:
            pass
    df = df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def run_live_observe():
    print("[探索観測] yfinance %s 取得中..." % LIVE_TICKER)
    m5 = fetch_live_m5()
    print("  M5 %d本 (%s..%s)" % (len(m5), m5.index.min(), m5.index.max()))
    if len(m5) < tt.BOX_WINDOW + 10:
        print("  本数不足→スキップ"); return
    new, tr = emit(m5, dry=False)
    print("  新規記録 %d本 / 台帳累計 %d本 → %s" % (new, len(seen_entry_times()), LEDGER))
    if new and len(tr):
        for _, r in tr.tail(min(new, 3)).iterrows():
            print("    %s %s entry%.5f risk%.5f R%+.2f net%+.2f" % (
                r["entry_time"], r["side"], r["entry"], r["risk"], r["R"], r["netR"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if os.path.exists(KILL):
        print("KILL あり→何もしない"); return
    if args.live:
        run_live_observe(); return
    print("使い方: --live(探索観測のみ・yfinance EURUSD=X・MT5非接続)")


if __name__ == "__main__":
    main()
