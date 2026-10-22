#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相場メーター記録レーン（撃たない・観測のみ・0円）。2026-10-22 会長GO「使わないのは勿体ない、記録はすべき」。
  役割: 相場メーター(ER=効率比)を金とUS100で測り続けて貯める。発注フィルタには使わない
        (未来データで通用せず=降格。理屈は operating-baseline-gold-us100)。だが計器として記録は継続
        =後で「そのトレードは有利な地合いだったか」をトレード台帳に重ねて見るための生データ。
  ★発注に一切干渉しない。金システム(setup_engine/demo_exec)・畑A執行機とは独立。MT5非接続。
  金の足=8793 API(setup_engine._fetch_bars 再利用) / US100=yfinance NQ=F(farm_a_forward 再利用)。
  有利地合い: 金=チョップ(ER低)で有利 / US100=トレンド(ER高)で有利(鏡写し・gold-chop-us100-trend-complementary)。
"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
for p in (HERE, LIVE):
    if p not in sys.path:
        sys.path.insert(0, p)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LOG = os.path.join(HERE, "regime_log.jsonl")
WIN = 288          # ≈24h(5分足)。touch2sb BOX_WINDOW と同じ窓。
ER_TH = 0.12       # ER<0.12=チョップ寄り / 以上=トレンド寄り(研究と同じ事前固定閾)。判定でなく記録ラベル。


def er(closes, win=WIN):
    seg = np.asarray(closes[-win:], dtype=float)
    if len(seg) < 3:
        return None
    path = np.abs(np.diff(seg)).sum()
    return float(abs(seg[-1] - seg[0]) / path) if path > 0 else 0.0


def gold_closes():
    try:
        import setup_engine as se
        m5 = se._fetch_bars()
        if m5 is None or len(m5) < WIN + 1:
            return None
        return m5["close"].to_numpy()
    except Exception as e:
        print("gold fetch err:", e); return None


def us100_closes():
    try:
        import farm_a_forward as fa
        m5 = fa.fetch_live_m5()
        if m5 is None or len(m5) < WIN + 1:
            return None
        return m5["close"].to_numpy()
    except Exception as e:
        print("us100 fetch err:", e); return None


def label(e):
    if e is None:
        return None, None
    lab = "chop" if e < ER_TH else "trend"
    return lab, round(e, 4)


def main():
    ge = er(gold_closes()) if True else None
    ue = er(us100_closes())
    glab, gv = label(ge)
    ulab, uv = label(ue)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),  # UTC
        "gold_er": gv, "gold_regime": glab,
        "gold_favorable": (glab == "chop") if glab else None,     # 金はチョップで有利
        "us100_er": uv, "us100_regime": ulab,
        "us100_favorable": (ulab == "trend") if ulab else None,   # US100はトレンドで有利
    }
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("[regime] %s 金ER=%s(%s) US100ER=%s(%s)" % (
        rec["ts"], gv, glab, uv, ulab))


if __name__ == "__main__":
    main()
