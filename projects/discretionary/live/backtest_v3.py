# -*- coding: utf-8 -*-
"""
車線3 v3a: AURELの『裁量に近い』壁→壁。
  違い(車線2との): 箱の上下壁を「効いている壁(タッチ多い)」で選び、
  ブレイク場面を採点→合格だけ TAKE（見送りも記録）。measured move は選んだ壁基準。
  先読みなし: 各判断はその時点までの過去バーだけで壁計算・採点。
  出力: trades DataFrame（decision=TAKE/SKIP, score, skip_reason, features 付き）。
金ゼロ・読取のみ・発注なし。
"""
import os
import json
import numpy as np
import pandas as pd
from walls import find_walls, pick_box

LOOKBACK = 140      # 壁検出の窓（M5本 ≈ 11.6h）
RETRACE_BARS = 12
MAX_HOLD = 288
SL_PAD_FR = 0.33
MIN_TOUCHES = 2
SCORE_TAKE = 55     # この点以上で TAKE（0-100）

_DAMASHI = None


def _load_damashi():
    global _DAMASHI
    if _DAMASHI is None:
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "damashi_hour_jst.json"), encoding="utf-8") as f:
                _DAMASHI = json.load(f)
        except Exception:
            _DAMASHI = {}
    return _DAMASHI


def _real_rate(ts):
    dm = _load_damashi()
    jh = int(pd.Timestamp(ts).tz_convert("Asia/Tokyo").hour)
    h = (dm.get("hours") or {}).get(str(jh))
    return (h["tp_rate"] if h else dm.get("base_tp_rate", 24.0)), jh


def _score(wall_touches, real_rate, brk_str, wick_ratio, mom_align):
    """0-100の採点。壁の強さ・時間帯本物率・ブレイク足の勢い・戻り拒否・勢い整合。"""
    s_wall = min(1.0, wall_touches / 4.0)
    s_zone = min(1.0, (real_rate or 24.0) / 35.0)
    s_brk = min(1.0, brk_str / 2.0)
    s_wick = min(1.0, wick_ratio / 0.4)
    s_mom = 1.0 if mom_align else 0.4
    comp = (0.30 * s_wall + 0.25 * s_zone + 0.20 * s_brk +
            0.10 * s_wick + 0.15 * s_mom)
    return round(comp * 100, 1)


def backtest_v3(m5, record_skips=True):
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    idx = m5.index; n = len(c)
    trades = []
    i = LOOKBACK
    while i < n - 1:
        lo0 = i - LOOKBACK
        atr = float(np.mean(h[max(1, i - 14):i] - l[max(1, i - 14):i])) if i > 15 else 0.0
        walls = find_walls(h[lo0:i], l[lo0:i], c[lo0:i], atr)
        max_dist = c[i - 1] * 0.02
        box = pick_box(walls, c[i - 1], max_dist, MIN_TOUCHES)
        if box is None:
            i += 1; continue
        up, dn, width = box["up"], box["dn"], box["width"]
        if width <= 0:
            i += 1; continue

        brk = None
        if c[i] < dn and c[i - 1] >= dn:
            brk = "DOWN"; wall = dn; wtouch = box["dn_touches"]
        elif c[i] > up and c[i - 1] <= up:
            brk = "UP"; wall = up; wtouch = box["up_touches"]
        if brk is None:
            i += 1; continue

        # リテスト(戻り)待ち
        j_enter = None
        for j in range(i + 1, min(i + RETRACE_BARS, n - 2) + 1):
            if brk == "DOWN" and h[j] >= wall:
                j_enter = j; break
            if brk == "UP" and l[j] <= wall:
                j_enter = j; break
        if j_enter is None:
            i += 1; continue

        entry = o[j_enter + 1]
        if brk == "DOWN":
            side = "SELL"; sl = wall + width * SL_PAD_FR; tp = wall - width
            if not (sl > entry > tp):
                i += 1; continue
        else:
            side = "BUY"; sl = wall - width * SL_PAD_FR; tp = wall + width
            if not (tp > entry > sl):
                i += 1; continue
        risk = abs(entry - sl)
        if risk <= 0:
            i += 1; continue

        # 採点用の特徴（エントリー足）
        ie = j_enter + 1
        rng = h[ie] - l[ie]; body = abs(c[ie] - o[ie])
        body_ratio = round(body / rng, 3) if rng > 0 else 0.0
        wick = (h[ie] - max(o[ie], c[ie])) if side == "SELL" else (min(o[ie], c[ie]) - l[ie])
        wick_ratio = round(wick / rng, 3) if rng > 0 else 0.0
        brk_str = round(rng / atr, 2) if atr > 0 else 0.0
        mom = (c[i] - c[max(0, i - 20)])
        mom_align = (mom < 0) if side == "SELL" else (mom > 0)
        real_rate, jh = _real_rate(idx[ie])
        score = _score(wtouch, real_rate, brk_str, wick_ratio, mom_align)
        decision = "TAKE" if score >= SCORE_TAKE else "SKIP"
        skip_reason = "" if decision == "TAKE" else (
            "壁弱%d/本物率%.0f/勢い%.1f/ヒゲ%.2f" % (wtouch, real_rate, brk_str, wick_ratio))

        # 前進シミュレーション（TAKE/SKIP両方で結果を残す＝比較材料）
        exit_px = reason = None; exit_k = None
        k_end = min(j_enter + MAX_HOLD, n - 1)
        for k in range(j_enter + 1, k_end + 1):
            if side == "SELL":
                if h[k] >= sl: exit_px, reason, exit_k = sl, "SL", k; break
                if l[k] <= tp: exit_px, reason, exit_k = tp, "TP", k; break
            else:
                if l[k] <= sl: exit_px, reason, exit_k = sl, "SL", k; break
                if h[k] >= tp: exit_px, reason, exit_k = tp, "TP", k; break
        if exit_px is None:
            exit_k = k_end; exit_px = c[k_end]; reason = "TIME"
        pnl = (exit_px - entry) if side == "BUY" else (entry - exit_px)

        trades.append({
            "entry_time": idx[ie], "side": side,
            "entry": round(entry, 3), "sl": round(sl, 3), "tp": round(tp, 3),
            "exit": round(exit_px, 3), "exit_reason": reason,
            "R": round(pnl / risk, 3), "hold_bars": exit_k - ie,
            "wall": round(wall, 3), "width": round(width, 3),
            "wall_touches": int(wtouch), "score": score, "decision": decision,
            "skip_reason": skip_reason, "real_rate": real_rate, "jst_hour": jh,
            "break_str_atr": brk_str, "entry_body_ratio": body_ratio,
            "reject_wick_ratio": wick_ratio,
            "mid": box["mid"], "up": up, "dn": dn,
        })
        i = exit_k + 1 if decision == "TAKE" else i + 1
    df = pd.DataFrame(trades)
    if not record_skips and len(df):
        df = df[df["decision"] == "TAKE"]
    return df


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall")
    from m5_loader import load_m5
    a = sys.argv[1] if len(sys.argv) > 1 else "2026-04-01"
    b = sys.argv[2] if len(sys.argv) > 2 else "2026-07-01"
    m5 = load_m5(a, b)
    tr = backtest_v3(m5)
    if not len(tr):
        print("トレード0"); raise SystemExit
    take = tr[tr["decision"] == "TAKE"]; skip = tr[tr["decision"] == "SKIP"]
    def stat(d, label):
        if not len(d):
            print("%s: 0本" % label); return
        tp = (d["exit_reason"] == "TP").sum()
        print("%s 本数%d 本物率%.1f%% 平均R%+.3f" %
              (label, len(d), 100*tp/len(d), d["R"].mean()))
    print("=== 車線3 v3a %s..%s (M5%d本) ===" % (a, b, len(m5)))
    stat(tr, "全候補")
    stat(take, "TAKE(採用)")
    stat(skip, "SKIP(見送り)")
