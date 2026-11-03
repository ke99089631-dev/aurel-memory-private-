# -*- coding: utf-8 -*-
"""
車線3の「15分足」版（会長GO 2026-11-03『再加速と同じ記録の仕方で・15分という新しいレーン』）。
  本物の setup_engine（5分の再加速レシピ）を**そのまま15分足で**走らせ、同じ台帳形式 setup_ledger_15m.jsonl に記録する。
  → 5分の setup_ledger と同じ列(kind=setup/update・pred・features・reaccel・zone・exit_reason・R…)＝ちゃんと比較できる。
  発注なし・金ゼロ・読取りのみ。touch2sb発火は呼ばない＝実弾fert(5分setup_ledgerを読む)に一切触れない。

やり方: setup_engine を import し、時間依存の定数だけ15分に合わせて差し替え（5分の本体ファイルは編集しない）。
  RETRACE_BARS 12→4 / MAX_HOLD 288→96 / MID_POOL_BARS 6→2 / COOLDOWN 3→1 / LATE_LOOKBACK 24→8 / REACCEL_BARS 12→4
  wallbox.WALL_WIN 200→67 / BAND_WIN 48→16（24h=96本/4h=16本の比で）
  価格単位(MIN_SL_W/MIN_TP_W/FEED_TOL/TRIG_SPREAD/REACCEL_PAD)は不変。
  台帳=setup_ledger_15m.jsonl / spread_log=別ファイル / 足=/api/data の5分を15分に束ねる。
  ※初回は取得窓(約17日)を15分で埋める＝同じ期間で5分と比較できる数字が今すぐ出る。以後は前向き。
"""
import os, sys, json, time
import datetime as dt
import urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd
import setup_engine as se
import wallbox

# ── 15分に合わせて差し替え（このプロセス内だけ。5分の本体プロセスには影響しない）──
se.LEDGER = os.path.join(HERE, "setup_ledger_15m.jsonl")
se.SPREAD_LOG = os.path.join(HERE, "spread_log_15m.jsonl")
se.RETRACE_BARS = 4
se.MAX_HOLD = 96
se.MID_POOL_BARS = 2
se.COOLDOWN = 1
se.LATE_LOOKBACK = 8
se.REACCEL_BARS = 4
wallbox.WALL_WIN = 67
wallbox.BAND_WIN = 16

INTERVAL = 30


def _fetch_bars_15m(n_bars=None):
    """/api/data の5分足を15分に束ねて返す（se._fetch_bars と同じ形: dtインデックス・OHLC）。形成中の15分足は落とす。"""
    url = se.API if not n_bars else se.API.split("?")[0] + "?n=%d" % int(n_bars)
    with urllib.request.urlopen(url, timeout=25) as r:
        d = json.loads(r.read().decode("utf-8"))
    bars = d.get("bars", [])
    if len(bars) < 40:
        return None
    df = pd.DataFrame(bars)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("dt")[["open", "high", "low", "close"]]
    r15 = df.resample("15min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    if len(r15) < 2:
        return None
    return r15.iloc[:-1]        # 最後の15分足は形成中の可能性＝使わない（5分版が最終足を落とすのと同じ思想）


se._fetch_bars = _fetch_bars_15m        # sync_once が参照する fetch を差し替え


def main():
    print("車線3【15分足】起動（再加速と同じレシピ・台帳=setup_ledger_15m・%d秒・発注なし・touch2sbなし）" % INTERVAL, flush=True)
    if "--once" in sys.argv:
        a, u = se.sync_once()
        print("once: +%d 新規 / %d 更新 (ledger=%s)" % (a, u, os.path.basename(se.LEDGER)), flush=True)
        return
    while True:
        try:
            a, u = se.sync_once()
            if a or u:
                print("%s [15m] +%d 新規 / %d 更新" % (dt.datetime.now().strftime("%H:%M:%S"), a, u), flush=True)
        except Exception as e:
            sys.stderr.write("[15m] sync err: %s\n" % e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
