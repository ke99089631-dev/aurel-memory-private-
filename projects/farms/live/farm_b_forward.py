#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
畑B（S&P500 壁→壁）前向き機 — 観測のみ(dry)。2026-10-21 会長GO「畑Bも並走」。
================================================================================
畑A(farm_a_forward.py)と同設計の別口。独立フィード=yfinance ES=F(S&P500先物)。
★お金ゼロ・MT5非接続・発注関数なし・金システムと非競合。判定=touch_test.run verbatim。
凍結仕様: 型=壁→壁 / 銘柄=S&P500 / NY採用 / 保ち2回(基本) / TP0.85 / 金固有閾値なし。
根拠: RESULTS_gate_us100_wall系と同関門でS&P500も14年+(保ち3回Sharpe0.58・束ねSharpe0.75)。
"""
import os, sys, json, argparse, time, glob
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

LEDGER = os.path.join(HERE, "farm_b_forward_ledger.jsonl")
KILL = os.path.join(HERE, "KILL")
CHUNKS = r"C:\Users\user\AssetEmpire\empire\research\dukas\chunks"

NEED_TOUCHES = 2
PROF = {"tp_mm": 0.85}
COST_BPS = 0.81
LIVE_TICKER = "ES=F"          # S&P500先物(独立フィード)
SELFTEST_CODE = "usa500idxusd"  # 過去自己テスト用チャンク


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
    tr = tt.run(m5, NEED_TOUCHES, PROF)
    if len(tr) == 0:
        return 0, tr
    tr = tr[rg.ny_session_mask(tr["entry_time"])].reset_index(drop=True)
    if len(tr) == 0:
        return 0, tr
    pos = m5.index.get_indexer(tr["entry_time"])
    tr["entry"] = m5["open"].to_numpy()[pos]
    tr["netR"] = tr["R"] - (tr["entry"] * COST_BPS / 10000.0) / tr["risk"]
    seen = seen_entry_times()
    new = 0
    for _, r in tr.iterrows():
        et = str(r["entry_time"])
        if et in seen:
            continue
        rec = {"farm": "B-SP500", "entry_time": et, "side": r["side"],
               "entry": round(float(r["entry"]), 2), "risk": round(float(r["risk"]), 2),
               "R": round(float(r["R"]), 3), "netR": round(float(r["netR"]), 3),
               "reason": r["reason"], "wtouch": int(r["wtouch"]),
               "need_touches": NEED_TOUCHES, "mode": "observe", "logged_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        if not dry:
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        new += 1
    return new, tr


def load_chunks_m5(code):
    files = sorted(glob.glob(os.path.join(CHUNKS, "%s-m1-bid-*.csv" % code)))
    frames = []
    for p in files:
        if os.path.getsize(p) < 50:
            continue
        try:
            frames.append(pd.read_csv(p))
        except Exception:
            continue
    m1 = pd.concat(frames, ignore_index=True)
    m1["dt"] = pd.to_datetime(m1["timestamp"], unit="ms", utc=True)
    m1 = m1.drop_duplicates(subset="timestamp").sort_values("timestamp").set_index("dt")
    return pd.DataFrame({"open": m1["open"].resample("5min").first(), "high": m1["high"].resample("5min").max(),
                         "low": m1["low"].resample("5min").min(), "close": m1["close"].resample("5min").last()}).dropna()


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


def selftest():
    print("[self-test] S&P500(%s) チャンク読込..." % SELFTEST_CODE)
    m5 = load_chunks_m5(SELFTEST_CODE)
    print("  M5 %d本 (%s..%s)" % (len(m5), m5.index.min().date(), m5.index.max().date()))
    _, tr = emit(m5, dry=True)
    if len(tr):
        net = tr["netR"]
        print("  発火(NY採用) %d本 / 勝率%.1f%% / ネット平均R%+.3f / 合計%+.1f" % (
            len(tr), 100 * (net > 0).mean(), net.mean(), net.sum()))
    print("  → 配管OK")


def run_live_observe():
    print("[live観測] yfinance %s 取得中..." % LIVE_TICKER)
    m5 = fetch_live_m5()
    print("  M5 %d本 (%s..%s)" % (len(m5), m5.index.min(), m5.index.max()))
    if len(m5) < tt.BOX_WINDOW + 10:
        print("  本数不足→スキップ"); return
    new, tr = emit(m5, dry=False)
    print("  新規記録 %d本 / 台帳累計 %d本 → %s" % (new, len(seen_entry_times()), LEDGER))
    if new and len(tr):
        for _, r in tr.tail(min(new, 3)).iterrows():
            print("    %s %s entry%.1f risk%.1f R%+.2f net%+.2f" % (
                r["entry_time"], r["side"], r["entry"], r["risk"], r["R"], r["netR"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if os.path.exists(KILL):
        print("KILL あり→何もしない"); return
    if args.selftest:
        selftest(); return
    if args.live:
        run_live_observe(); return
    print("使い方: --selftest / --live(観測のみ・yfinance ES=F・MT5非接続)")


if __name__ == "__main__":
    main()
