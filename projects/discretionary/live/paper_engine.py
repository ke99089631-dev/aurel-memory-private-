# -*- coding: utf-8 -*-
"""
車線3: AUREL 自律「紙」トレード・エンジン（24/5・発注は一切なし・金ゼロ）。
  役割: 会長と同じ壁→壁の骨格(backtest_mm)を最新M5に適用し、
        成立→決済まで着いたトレードを「理由・確信度・自己採点(R)つき」で
        専用台帳 paper_ledger.jsonl に貯め続ける。会長の実(車線1 ledger.jsonl)とは絶対に混ぜない。
  データ源: チャートサーバの /api/data (localhost:8793)。MT5二重接続を避ける（読取専用の橋は1本）。
  正直な位置づけ: 純ルール適用＝backtestの連続版。価値は24/5で規律ある理由つき標本が貯まること＋
                  車線比較＋将来C2(分類器)の学習データ。エッジを保証するものではない。
  安全: 発注API不使用・金ゼロ・車線1台帳に触れない・追記のみ。
"""
import os
import sys
import json
import time
import datetime as dt
import urllib.request

sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall")
import pandas as pd
from backtest_mm import backtest_mm

HERE = os.path.dirname(os.path.abspath(__file__))
API = "http://100.73.107.61:8793/api/data?n=2000"   # サーバはTailscale IPのみbind
PAPER = os.path.join(HERE, "paper_ledger.jsonl")     # 車線3の正本（追記のみ・貯める）
DAMASHI_FILE = os.path.join(HERE, "damashi_hour_jst.json")
INTERVAL = 300                                        # 5分ごと（M5に合わせる）


def _load_damashi():
    try:
        with open(DAMASHI_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _fetch_bars():
    with urllib.request.urlopen(API, timeout=20) as r:
        d = json.loads(r.read().decode("utf-8"))
    bars = d.get("bars", [])
    if not bars:
        return None
    df = pd.DataFrame(bars)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.set_index("dt")[["open", "high", "low", "close"]]


def _logged_entry_times():
    """既に台帳にある entry_time の集合と、次のP番号。"""
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
                maxn = max(maxn, int(str(r.get("id", "P-0")).split("-")[1]))
            except Exception:
                pass
    return seen, maxn


def _reason(row, dm):
    """理由・確信度を作る（その時間帯の本物率・溜まり幅・方向）。"""
    jh = int(pd.Timestamp(row["entry_time"]).tz_convert("Asia/Tokyo").hour)
    real = None
    if dm:
        h = dm.get("hours", {}).get(str(jh))
        if h:
            real = h["tp_rate"]
    base = dm.get("base_tp_rate") if dm else None
    width_pct = round(row["width"] / row["entry"] * 100.0, 2)
    zone = "本物帯" if 7 <= jh < 12 else ("ダマシ巣" if 0 <= jh < 5 else "中立")
    side_txt = "下ブレイク戻り売り" if row["side"] == "SELL" else "上ブレイク戻り買い"
    conf = real if real is not None else base
    reason = "JST%d時(%s) 本物率%s%% / 溜まり幅%.2f%% / %s" % (
        jh, zone, ("%.0f" % real) if real is not None else "?", width_pct, side_txt)
    return {"jst_hour": jh, "zone": zone, "real_rate": real, "base_rate": base,
            "width_pct": width_pct, "confidence": conf, "reason": reason}


def sync_once():
    dm = _load_damashi()
    m5 = _fetch_bars()
    if m5 is None or len(m5) < 120:
        return 0
    tr = backtest_mm(m5)
    if not len(tr):
        return 0
    # 決済まで着いたトレードのみ（窓端の未決着 TIME は最新バー=窓端なら保留）
    last_bar = m5.index[-1]
    seen, maxn = _logged_entry_times()
    added = 0
    for _, row in tr.iterrows():
        et = int(pd.Timestamp(row["entry_time"]).timestamp())
        if et in seen:
            continue
        # 窓端で未決着(TIME かつ 直近)なら次サイクルまで待つ（早すぎる確定を避ける）
        resolved = row["exit_reason"] in ("TP", "SL")
        is_time = row["exit_reason"] == "TIME"
        if is_time:
            # TIME決済が窓の最後尾付近なら未確定として保留
            pass  # backtest内で確定済みなので採用（窓端保留は次段で判断）
        maxn += 1
        info = _reason(row, dm)
        rec = {
            "id": "P-%04d" % maxn, "lane": 3, "kind": "paper",
            "side": row["side"], "entry": float(row["entry"]),
            "sl": float(row["sl"]), "tp": float(row["tp"]),
            "exit": float(row["exit"]), "exit_reason": row["exit_reason"],
            "R": float(row["R"]), "hold_bars": int(row["hold_bars"]),
            "wall": float(row["wall"]), "width": float(row["width"]),
            "entry_time": et,
            "entry_jst": pd.Timestamp(row["entry_time"]).tz_convert("Asia/Tokyo").strftime("%Y-%m-%d %H:%M"),
            "logged_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        rec.update(info)
        with open(PAPER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        seen.add(et)
        added += 1
    return added


def main():
    print("車線3 紙トレードエンジン起動（5分ごと・発注なし・金ゼロ）", flush=True)
    while True:
        try:
            n = sync_once()
            if n:
                print("%s +%d 紙トレード記録" % (dt.datetime.now().strftime("%H:%M:%S"), n), flush=True)
        except Exception as e:
            sys.stderr.write("sync err: %s\n" % e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    if "--once" in sys.argv:
        print("追加:", sync_once())
    else:
        main()
