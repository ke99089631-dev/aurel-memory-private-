# -*- coding: utf-8 -*-
"""
MT5 読取専用ライブ橋（裁量「壁→壁」コックピット/車線3 の土台）。
  役割: 稼働中の MT5 ターミナルに attach し、XAUUSD+ の M5 足と現在ティック(bid/ask/spread)を
        「読むだけ」で取得する。Web地図と AUREL 紙トレードに供給する。
  ★安全設計（不変・二重の壁）:
    1) 発注系 API は import も呼び出しも一切しない（order_send/order_check/... を本モジュールで使わない）。
    2) attach 後に account_info().login が裁量口座 ALLOWED_LOGIN と一致するか検証。
       不一致（＝プロップ g4_ 等の別口座に繋がった）なら即 shutdown して RuntimeError。
       → プロップには「触れない・読取のみ」の境界を機械的に担保。
    3) ログイン(パスワード)は渡さない。既に会長がログイン済みのターミナルに attach するだけ。
  ※初回接続は会長が起きている時に監督付きで。深夜の自律接続はしない。
"""
import sys

ALLOWED_LOGIN = 27972608          # 裁量口座のみ。これ以外に繋がったら中断。
TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
SYMBOL = "XAUUSD+"                 # Vantage 金（会長の実トレード銘柄）

# 発注系を「呼べない」ように、使ってよい読取関数だけを明示（自己文書化）。
_READ_ONLY_FUNCS = ("initialize", "shutdown", "account_info", "symbol_info",
                    "symbol_info_tick", "symbol_select", "copy_rates_from_pos",
                    "last_error")


def connect():
    """稼働中ターミナルに attach し、口座が裁量口座であることを検証して返す。"""
    import MetaTrader5 as mt5
    if not mt5.initialize(path=TERMINAL_PATH):
        raise RuntimeError("MT5 initialize 失敗: %s" % (mt5.last_error(),))
    info = mt5.account_info()
    if info is None:
        mt5.shutdown()
        raise RuntimeError("account_info 取得不可（未ログイン?）")
    if int(info.login) != ALLOWED_LOGIN:
        got = int(info.login)
        mt5.shutdown()
        raise RuntimeError("★安全弁作動: 想定外の口座 %d に接続（許可=%d のみ）。"
                           "プロップ/別口座の可能性→中断。" % (got, ALLOWED_LOGIN))
    return mt5


def live_tick(mt5):
    """現在の bid/ask/spread(pt, bps) を読む。"""
    mt5.symbol_select(SYMBOL, True)
    t = mt5.symbol_info_tick(SYMBOL)
    if t is None:
        raise RuntimeError("tick 取得不可: %s" % SYMBOL)
    spread_pt = t.ask - t.bid
    mid = (t.ask + t.bid) / 2.0
    return {"bid": t.bid, "ask": t.ask, "spread_pt": round(spread_pt, 3),
            "spread_bps": round(spread_pt / mid * 10000.0, 3) if mid else None,
            "time": t.time}


def m5_bars(mt5, count=300):
    """直近 count 本の M5 OHLC を読む（pandas DataFrame）。"""
    import pandas as pd
    mt5.symbol_select(SYMBOL, True)
    rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, count)
    if rates is None or len(rates) == 0:
        raise RuntimeError("M5 rates 取得不可: %s" % SYMBOL)
    df = pd.DataFrame(rates)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)   # MT5=GMT+3だが epoch は UTC
    return df[["dt", "open", "high", "low", "close", "tick_volume"]]


if __name__ == "__main__":
    # ★初回テストは監督付きで実行する（会長在席時）。安全弁の作動確認込み。
    print("MT5 読取橋 テスト（読取のみ・発注なし・裁量口座%d限定）" % ALLOWED_LOGIN)
    mt5 = connect()
    try:
        print("接続OK 口座=%d 検証通過" % ALLOWED_LOGIN)
        print("tick:", live_tick(mt5))
        bars = m5_bars(mt5, 5)
        print(bars.to_string(index=False))
    finally:
        mt5.shutdown()
