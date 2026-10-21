# -*- coding: utf-8 -*-
"""
touch2sb = 「素の高安の箱」版 壁→壁エンジン（会長の本命・2026-10-21②）。
  優位性は壁の引き方に宿る=過去288本(≈24h・現バー除外)の素の最高値/最安値で壁を引く。
  dynamic_box(クラスタ壁)でなく touch_test.run と同一ロジック。金近年2024-26で保ち2回×会長フィルタ=平均R+0.188。
  読取・検証用 backtest() は touch_test.run と1トレードも違わない事を前提に作る(fidelity検証で担保)。
  ライブ発火は latest_signal(): 「今ちょうど確認完了して、この足の始値で入る」場合だけ signal を返す。
  ※発注はしない。デモ配線(demo_exec)は会長の明示GO後。
"""
import numpy as np
import pandas as pd

# ── 事前固定（touch_test と同値・動かさない）──────────────
BOX_WINDOW  = 288    # 箱探索窓 ≈ 24h
RETEST_BARS = 36     # ブレイク後の床化確認上限 ≈ 3h
TOUCH_BAND  = 0.08   # 壁タッチ許容(幅比)
BREAK_TOL   = 0.15   # 床崩壊閾(幅比)
SL_FRAC_IN  = 0.33   # SL=壁の内側 幅×0.33
TP_MM       = 1.00   # TP=measured move
MAX_HOLD    = 288    # 時間切れ ≈ 24h

# 会長フィルタ（事前宣言）: 控えめTP0.85 / risk≥3USD / 箱≥10USD / 本物帯JST07-12
CHAIRMAN = {"tp_mm": 0.85, "risk_min": 3.0, "width_min": 10.0, "jst_lo": 7, "jst_hi": 12}


def _box_at(h, l, i):
    """バー i 時点の箱（現バー除外・過去288本の素の高安）。"""
    w0 = i - BOX_WINDOW
    up_b = h[w0:i].max(); dn_b = l[w0:i].min()
    return w0, up_b, dn_b, (up_b - dn_b)


def _break_at(c, i, up_b, dn_b):
    """バー i で箱端を終値が跨いだか。戻り=(side, wall) or None。"""
    if c[i] > up_b and c[i - 1] <= up_b:
        return "BUY", up_b
    if c[i] < dn_b and c[i - 1] >= dn_b:
        return "SELL", dn_b
    return None


def _wtouch(h, l, c, w0, i, side, wall, width):
    """抜ける前に壁を抜かず反発した回数（会長定義・壁選定の質）。近年は効かないが記録用に残す。"""
    wtol = width * 0.05; reject = 0; armed = True
    for jj in range(w0, i):
        if side == "BUY":
            near = h[jj] >= wall - wtol and c[jj] < wall
            away = h[jj] < wall - 2 * wtol
        else:
            near = l[jj] <= wall + wtol and c[jj] > wall
            away = l[jj] > wall + 2 * wtol
        if near and armed:
            reject += 1; armed = False
        if away:
            armed = True
    return reject


def _confirm(o, h, l, c, i, side, wall, width, need_touches, n):
    """ブレイク足 i の後、保ちタッチを数える。戻り=(enter_i or None, broke)。touch_testと同一。"""
    if need_touches == 0:
        return i, False
    band = width * TOUCH_BAND; btol = width * BREAK_TOL
    touches = 0; enter_i = None
    end = min(i + RETEST_BARS, n - 2)
    for k in range(i + 1, end + 1):
        if side == "BUY":
            if c[k] < wall - btol:
                return None, True
            if c[k] < o[k] and l[k] <= wall + band and c[k] >= wall - btol:
                touches += 1
        else:
            if c[k] > wall + btol:
                return None, True
            if c[k] > o[k] and h[k] >= wall - band and c[k] <= wall + btol:
                touches += 1
        if touches >= need_touches:
            return k, False
    return None, False


def _levels(side, wall, width, tp_mm):
    if side == "BUY":
        return wall - width * SL_FRAC_IN, wall + width * tp_mm
    return wall + width * SL_FRAC_IN, wall - width * tp_mm


def _entry_ok(side, entry, sl, tp, risk_min):
    risk = abs(entry - sl)
    if risk <= 0 or risk < risk_min:
        return False, risk
    if (side == "BUY" and tp <= entry) or (side == "SELL" and tp >= entry):
        return False, risk
    return True, risk


def backtest(m5, need_touches, prof=None):
    """touch_test.run と同一仕様（検証用）。非重複・SL優先・TIME切れ。"""
    p = prof or {}
    tp_mm = p.get("tp_mm", TP_MM); risk_min = p.get("risk_min", 0.0)
    width_min = p.get("width_min", 0.0)
    jst_lo = p.get("jst_lo"); jst_hi = p.get("jst_hi")
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    idx = m5.index
    jst_hours = idx.tz_convert("Asia/Tokyo").hour.to_numpy() if (jst_lo is not None) else None
    n = len(c); trades = []
    i = BOX_WINDOW
    while i < n - 1:
        w0, up_b, dn_b, width = _box_at(h, l, i)
        if width <= 0 or width < width_min:
            i += 1; continue
        br = _break_at(c, i, up_b, dn_b)
        if br is None:
            i += 1; continue
        side, wall = br
        wt = _wtouch(h, l, c, w0, i, side, wall, width)
        enter_i, broke = _confirm(o, h, l, c, i, side, wall, width, need_touches, n)
        if broke or enter_i is None or enter_i + 1 > n - 1:
            if broke or enter_i is None:
                i += 1; continue
            break
        if jst_hours is not None:
            hh = jst_hours[enter_i + 1]
            if not (jst_lo <= hh < jst_hi):
                i += 1; continue
        entry = o[enter_i + 1]
        sl, tp = _levels(side, wall, width, tp_mm)
        ok, risk = _entry_ok(side, entry, sl, tp, risk_min)
        if not ok:
            i += 1; continue
        exit_px = exit_k = reason = None
        k_end = min(enter_i + MAX_HOLD, n - 1)
        for k in range(enter_i + 1, k_end + 1):
            if side == "BUY":
                if l[k] <= sl: exit_px, reason, exit_k = sl, "SL", k; break
                if h[k] >= tp: exit_px, reason, exit_k = tp, "TP", k; break
            else:
                if h[k] >= sl: exit_px, reason, exit_k = sl, "SL", k; break
                if l[k] <= tp: exit_px, reason, exit_k = tp, "TP", k; break
        if exit_px is None:
            exit_k = k_end; exit_px = c[k_end]; reason = "TIME"
        pnl = (exit_px - entry) if side == "BUY" else (entry - exit_px)
        R = pnl / risk
        trades.append({"entry_time": idx[enter_i + 1], "side": side, "R": round(R, 3),
                       "reason": reason, "risk": round(risk, 3), "wtouch": wt,
                       "hold": exit_k - (enter_i + 1)})
        i = exit_k + 1
    return pd.DataFrame(trades)


def latest_signal(m5, need_touches=2, prof=CHAIRMAN):
    """今まさに新しい足が開いた直前バーで確認完了→この足の始値で入る、を検出。
       戻り: 発火=dict(side/wall/entry/sl/tp/risk/width/wtouch/jst/...) / 無し=None。
       非重複は呼び出し側(demo_exec)の建玉管理に委ねる。先読みなし=確定足のみ使用。"""
    p = prof or {}
    tp_mm = p.get("tp_mm", TP_MM); risk_min = p.get("risk_min", 0.0)
    width_min = p.get("width_min", 0.0)
    jst_lo = p.get("jst_lo"); jst_hi = p.get("jst_hi")
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    idx = m5.index; n = len(c)
    if n < BOX_WINDOW + 2:
        return None
    target = n - 1                 # 入る足（始値確定・まだ確定終値なし）
    enter_i = target - 1           # 確認が完了している確定足
    # ブレイク足 i は enter_i から最大 RETEST_BARS 遡った範囲。
    # backtest と同じ「最初(最古)の有効ブレイク」を採用=i昇順で最初にenter_iへ確認完了したものを拾う。
    i_lo = max(BOX_WINDOW, enter_i - RETEST_BARS)
    for i in range(i_lo, enter_i + 1):
        if need_touches == 0 and i != enter_i:
            continue
        w0, up_b, dn_b, width = _box_at(h, l, i)
        if width <= 0 or width < width_min:
            continue
        br = _break_at(c, i, up_b, dn_b)
        if br is None:
            continue
        side, wall = br
        ei, broke = _confirm(o, h, l, c, i, side, wall, width, need_touches, n)
        if broke or ei is None:
            continue
        if ei != enter_i:          # 確認完了が今の直前足でない=今は発火しない
            continue
        if jst_lo is not None:
            hh = int(pd.Timestamp(idx[target]).tz_convert("Asia/Tokyo").hour)
            if not (jst_lo <= hh < jst_hi):
                continue
        entry = float(o[target])
        sl, tp = _levels(side, wall, width, tp_mm)
        ok, risk = _entry_ok(side, entry, sl, tp, risk_min)
        if not ok:
            continue
        return {"side": side, "wall": round(float(wall), 3), "entry": round(entry, 3),
                "sl": round(float(sl), 3), "tp": round(float(tp), 3), "risk": round(float(risk), 3),
                "width": round(float(width), 3), "touches": need_touches,
                "wtouch": _wtouch(h, l, c, w0, i, side, wall, width),
                "break_time": int(pd.Timestamp(idx[i]).timestamp()),
                "entry_time": int(pd.Timestamp(idx[target]).timestamp()),
                "jst": pd.Timestamp(idx[target]).tz_convert("Asia/Tokyo").strftime("%Y-%m-%d %H:%M")}
    return None
