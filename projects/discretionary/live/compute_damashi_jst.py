# -*- coding: utf-8 -*-
"""
C1 ダマシ確率メーターの土台: 機械の壁→壁トレードを JST時間帯別の本物率(TP率) に集計。
  会長の裁量と同じ骨格(backtest_mm)の全トレードで「この時間はブレイクが本物になりやすいか」を数値化。
  出力: damashi_hour_jst.json  { "hours": {"0":{"n":..,"tp_rate":..}, ...}, "base_tp_rate":.., "total":..}
金ゼロ・読取のみ。断定でなく確率の目安（機械レンジ代理＝会長の主観壁より控えめ）。
"""
import os
import sys
import json
sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall")
import pandas as pd
from m5_loader import load_m5
from backtest_mm import backtest_mm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "damashi_hour_jst.json")


def main():
    a = sys.argv[1] if len(sys.argv) > 1 else "2018-01-01"
    b = sys.argv[2] if len(sys.argv) > 2 else "2026-07-01"
    print("M5読み込み %s..%s" % (a, b), flush=True)
    m5 = load_m5(a, b)
    print("M5 %d本 → backtest…" % len(m5), flush=True)
    tr = backtest_mm(m5)
    n = len(tr)
    tp = (tr["exit_reason"] == "TP")
    jst_hour = pd.DatetimeIndex(
        pd.to_datetime(tr["entry_time"].to_numpy(), utc=True)
    ).tz_convert("Asia/Tokyo").hour
    tr = tr.assign(_jh=jst_hour, _tp=tp.astype(int))
    hours = {}
    for h, g in tr.groupby("_jh"):
        hours[str(int(h))] = {"n": int(len(g)),
                              "tp_rate": round(100.0 * g["_tp"].mean(), 1)}
    out = {
        "hours": hours,
        "base_tp_rate": round(100.0 * tp.mean(), 1),
        "total": int(n),
        "range": [a, b],
        "note": "機械レンジ代理の壁→壁。TP率=本物率の目安。会長の主観壁選定はこれより上を狙う。",
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("[OK] %s  base本物率 %.1f%% / n=%d" % (OUT, out["base_tp_rate"], n))
    for h in sorted(hours, key=lambda x: int(x)):
        r = hours[h]
        if r["n"] >= 30:
            print("  JST%2s時 n=%5d 本物率%5.1f%%" % (h, r["n"], r["tp_rate"]))


if __name__ == "__main__":
    main()
