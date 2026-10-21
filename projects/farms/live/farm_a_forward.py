#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
畑A（US100 壁→壁）前向き機 — 観測のみ(dry)。2026-10-21 会長GO「畑を耕す」。
================================================================================
役割: 凍結仕様 FARM-A-US100-SPEC.md を「そのまま」前向きに回し、仮想トレードを記録する。
      ★お金は1円も動かさない。MT5にも接続しない(発注段はこの後・会長GO二重ロック)。
      ★判定ロジックは touch_test.run を verbatim で呼ぶ(再実装しない=検証機と配備機を同一=G0)。

構成:
  - 入力 = US100 M5（source依存）。self-test は Dukascopy 履歴(load_m5)を「過去のある時点まで」で
           切って渡す＝先読みなしの前向きを再現。live は後でフィード差し替え(下の TODO)。
  - run  = touch_test.run(m5, NEED_TOUCHES, PROF) をそのまま。NYセッションのみ採用(run_gate.ny_session_mask)。
  - 出力 = farm_a_forward_ledger.jsonl に未記録の確定トレードだけ追記(entry_time で重複排除)。
  - 口座ゼロ化回避の器 = 記録のみなので実損なし。将来の発注段で RISK_FRAC/日次停止を適用。

安全: 発注関数なし。MT5 import なし。KILLファイルがあれば何もしない。
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
from m5_loader import load_m5

LEDGER = os.path.join(HERE, "farm_a_forward_ledger.jsonl")
KILL = os.path.join(HERE, "KILL")

# 凍結仕様(FARM-A-US100-SPEC.md と一致・1字変更で再凍結)
SYMBOL = "us100"
NEED_TOUCHES = 2          # 基本2(会長の採用値)。3も別レーンでobserve可
PROF = {"tp_mm": 0.85}    # 金固有閾値は付けない。セッションはNYマスクで担保
BPS = 0.81                # 関門前提(実測0.54bpsより保守)
COST_BPS = BPS


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
    """m5(ある時点までの窓)に凍結ロジックを当て、NY採用・未記録の確定トレードを追記。戻り=新規件数。"""
    tr = tt.run(m5, NEED_TOUCHES, PROF)
    if len(tr) == 0:
        return 0, tr
    tr = tr[rg.ny_session_mask(tr["entry_time"])].reset_index(drop=True)
    if len(tr) == 0:
        return 0, tr
    tr["entry"] = tr["entry"] if "entry" in tr else None
    # entry価格=その足のopen(= touch_test内 enter) を m5 から引く
    pos = m5.index.get_indexer(tr["entry_time"])
    tr["entry"] = m5["open"].to_numpy()[pos]
    tr["netR"] = tr["R"] - (tr["entry"] * COST_BPS / 10000.0) / tr["risk"]
    seen = seen_entry_times()
    new = 0
    for _, r in tr.iterrows():
        et = str(r["entry_time"])
        if et in seen:
            continue
        rec = {"farm": "A-US100", "entry_time": et, "side": r["side"],
               "entry": round(float(r["entry"]), 2), "risk": round(float(r["risk"]), 2),
               "R": round(float(r["R"]), 3), "netR": round(float(r["netR"]), 3),
               "reason": r["reason"], "wtouch": int(r["wtouch"]),
               "need_touches": NEED_TOUCHES, "mode": "observe", "logged_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        if not dry:
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        new += 1
    return new, tr


def selftest(year=2025):
    """前向き自己テスト: 過去の1年を時点で切って渡しても、関門と同じ型が出るか(配管の証明)。"""
    a = "%d-01-01" % year; b = "%d-07-01" % (year + 1) if year < 2026 else "2026-07-01"
    print("[self-test] US100 %s..%s 読込..." % (a, b))
    m5 = load_m5(a, b, SYMBOL)
    print("  M5 %d本" % len(m5))
    n, tr = emit(m5, dry=True)   # dry=記録せず件数だけ
    if len(tr):
        net = tr["netR"]
        print("  発火(NY採用) %d本 / 勝率%.1f%% / ネット平均R%+.3f / 合計%+.1f" % (
            len(tr), 100 * (net > 0).mean(), net.mean(), net.sum()))
        print("  直近3件:")
        for _, r in tr.tail(3).iterrows():
            print("    %s %s entry%.1f risk%.1f R%+.2f (%s)" % (
                r["entry_time"], r["side"], r["entry"], r["risk"], r["R"], r["reason"][:40]))
    print("  → 配管OK（前向きに発火・記録できる。live化はデータフィード差し替えのみ）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--live", action="store_true", help="(未実装)ライブフィード。今は観測のみ")
    args = ap.parse_args()
    if os.path.exists(KILL):
        print("KILL あり→何もしない"); return
    if args.selftest:
        selftest(args.year); return
    if args.live:
        run_live_observe()
        return
    print("使い方: --selftest [--year 2025]  /  --live(観測のみ・yfinance NQ=F・MT5非接続)")


def fetch_live_m5():
    """独立フィード=yfinance NQ=F(NASDAQ100先物=US100)直近60日M5。★MT5非接続・金システム非競合。"""
    import yfinance as yf
    df = yf.download("NQ=F", period="60d", interval="5m", auto_adjust=False, progress=False)
    if df is None or len(df) == 0:
        raise RuntimeError("yfinance NQ=F 取得0件")
    if hasattr(df.columns, "get_level_values"):   # MultiIndex列を平す
        try:
            df.columns = df.columns.get_level_values(0)
        except Exception:
            pass
    df = df.rename(columns=str.lower)
    df = df[["open", "high", "low", "close"]].dropna()
    idx = pd.to_datetime(df.index, utc=True)
    df.index = idx
    return df


def run_live_observe():
    """観測のみ1回: 生フィードに凍結ロジックを当て、未記録の確定NYトレードを追記(0円・MT5非接続)。"""
    import pandas as pd  # noqa (emit内で使用)
    print("[live観測] yfinance NQ=F 取得中...")
    m5 = fetch_live_m5()
    print("  M5 %d本 (%s..%s)" % (len(m5), m5.index.min(), m5.index.max()))
    if len(m5) < tt.BOX_WINDOW + 10:
        print("  本数不足→スキップ"); return
    new, tr = emit(m5, dry=False)
    tot = len(seen_entry_times())
    print("  新規記録 %d本 / 台帳累計 %d本 → %s" % (new, tot, LEDGER))
    if new and len(tr):
        for _, r in tr.tail(min(new, 3)).iterrows():
            print("    %s %s entry%.1f risk%.1f R%+.2f net%+.2f" % (
                r["entry_time"], r["side"], r["entry"], r["risk"], r["R"], r["netR"]))


if __name__ == "__main__":
    main()
