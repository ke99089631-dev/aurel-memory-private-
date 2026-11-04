#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
畑D（BTC 壁→壁）★探索レーン★ — 観測のみ(dry)。2026-11-04 会長GO「畑Bの候補、早く作る」。
================================================================================
狙い=分散の“直交枠”。既存の相方候補を日次R相関で測ったら:
  畑A US100 × 畑B SP500 = +0.56（双子＝分散にならない）
  畑A US100 × 畑C EUR   = -0.05 / 畑B × 畑C = -0.17（直交）
  金 × US100            = +0.06（直交）
金=レンジ / 株(US100/SP500)=トレンド。この2軸と“別の資金フロー”で動くのが暗号(BTC)。
cross_market 一次検証でも壁→壁は BTC で＋側(structural-edge-cross-market)。
24時間→本数が速く貯まる＝関門30/100本に US100 より早く着く＝「早く作る」に合う。
★畑C(EUR)と同じ探索扱い: 14年関門は未確定＝まだ畑に昇格してない。まず“金/US100と相関しないか”を生で貯める。
独立フィード=yfinance BTC-USD。暗号は24時間→NYマスクなし(全時間)。
★お金ゼロ・MT5非接続・発注なし・金システム非競合。判定=touch_test.run verbatim。
昇格の順序(会長ルール)=相関→優位: 30本で ①金/US100との相関 ②単体ネット平均R ③合成DD を測る。
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

LEDGER = os.path.join(HERE, "farm_d_btc_explore_ledger.jsonl")
KILL = os.path.join(HERE, "KILL")
NEED_TOUCHES = 2
PROF = {"tp_mm": 0.85}
COST_BPS = 3.00               # BTC(暗号)は株/FXより広い・保守値(業者で実測し直す前提)
LIVE_TICKER = "BTC-USD"


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
    tr = tt.run(m5, NEED_TOUCHES, PROF)   # 暗号=全時間(NYマスクなし)
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
        rec = {"farm": "D-BTC-EXPLORE", "entry_time": et, "side": r["side"],
               "entry": round(float(r["entry"]), 2), "risk": round(float(r["risk"]), 2),
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
            print("    %s %s entry%.2f risk%.2f R%+.2f net%+.2f" % (
                r["entry_time"], r["side"], r["entry"], r["risk"], r["R"], r["netR"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    if os.path.exists(KILL):
        print("KILL あり→何もしない"); return
    if args.live:
        run_live_observe(); return
    print("使い方: --live(探索観測のみ・yfinance BTC-USD・MT5非接続)")


if __name__ == "__main__":
    main()
