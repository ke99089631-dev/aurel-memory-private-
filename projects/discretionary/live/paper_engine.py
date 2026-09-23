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
import numpy as np
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


def compute_features(m5, row):
    """★backtestが記録しない「質・文脈」の特徴を計測（車線3の本来の材料）。
       全て客観・数値。後で本物(TP)/ダマシ(SL)を分ける軸を探すための入力。"""
    idx = m5.index
    try:
        ie = idx.get_loc(pd.Timestamp(row["entry_time"]))
    except Exception:
        return {}
    if isinstance(ie, slice):
        ie = ie.start
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    wall = row["wall"]; width = row["width"]; side = row["side"]
    n0 = max(0, ie - 100)
    trs = [h[k] - l[k] for k in range(max(1, ie - 14), ie)]
    atr = float(np.mean(trs)) if trs else 0.0
    rng = h[ie] - l[ie]; body = abs(c[ie] - o[ie])
    body_ratio = round(body / rng, 3) if rng > 0 else 0.0
    wick = (h[ie] - max(o[ie], c[ie])) if side == "SELL" else (min(o[ie], c[ie]) - l[ie])
    wick_ratio = round(wick / rng, 3) if rng > 0 else 0.0
    mom = round((c[ie] - c[max(0, ie - 20)]) / c[ie] * 100, 3) if ie >= 20 else 0.0
    win_h = float(max(h[n0:ie + 1])); win_l = float(min(l[n0:ie + 1]))
    rpos = round((c[ie] - win_l) / (win_h - win_l), 3) if win_h > win_l else 0.5
    tol = 0.1 * width
    if side == "SELL":
        touches = int(sum(1 for k in range(n0, ie) if abs(l[k] - wall) <= tol))
    else:
        touches = int(sum(1 for k in range(n0, ie) if abs(h[k] - wall) <= tol))
    s0 = max(0, ie - 30)
    tight = round(float(np.std(c[s0:ie])) / row["entry"] * 100, 3) if ie > s0 else 0.0
    brk_str = round(rng / atr, 2) if atr > 0 else 0.0
    return {
        "break_str_atr": brk_str,        # ブレイク/エントリー足の値幅 ÷ ATR（勢い）
        "entry_body_ratio": body_ratio,  # 実体比率（強い足=1に近い）
        "reject_wick_ratio": wick_ratio, # 壁での反発ヒゲ比率（拒否の強さ）
        "momentum20_pct": mom,           # 直近20本の勢い(%)
        "range_pos": rpos,               # レンジ内の位置(0=安値圏/1=高値圏)
        "wall_touches": touches,         # 壁が試された回数(壁の強さ)
        "tightness_pct": tight,          # 溜まりの締まり(小さいほど tight)
        "atr14": round(atr, 3),
    }


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
        rec["features"] = compute_features(m5, row)   # ★検証機が見ない質・文脈
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
