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
import time as _time

ALLOWED_LOGIN = 27972608          # 裁量口座のみ。これ以外に繋がったら中断。
TERMINAL_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
SYMBOL = "XAUUSD+"                 # Vantage 金（会長の実トレード銘柄）


def _rule_offset_h(now_utc=None):
    """業者サーバ時刻のUTCオフセット(時)をニューヨーク夏時間ルールで決める。
    Vantage は NY に追随: NY夏時間中=GMT+3 / それ以外=GMT+2。
    ★2026-11-11 会長GO: 固定値3は 2026-11-01(米夏時間終了)で1時間ずれ、金AIデモが発火を全部捨てた(8本)。以後は毎回算出。"""
    import pandas as pd
    ts = pd.Timestamp.now(tz="UTC") if now_utc is None else pd.Timestamp(now_utc, tz="UTC")
    ny = ts.tz_convert("America/New_York")
    return 3 if (ny.dst() is not None and ny.dst().total_seconds() != 0) else 2


def server_utc_offset_h(mt5=None):
    """ルール値を基本に、ティック時刻(サーバ壁時計)と実UTCの差で実測検算する。
    実測が 2 or 3 の整数時間で、ルールと食い違えば実測を採る(業者が規則外の日に切替えた場合の保険)。
    市場閉場中(週末)は最終ティックが古く実測が外れるので、その時はルール値。"""
    rule = _rule_offset_h()
    if mt5 is None:
        return rule
    try:
        t = mt5.symbol_info_tick(SYMBOL)
        if t is not None and t.time:
            measured = round((float(t.time) - _time.time()) / 3600.0)
            if measured in (2, 3) and measured != rule:
                sys.stderr.write("[mt5_bridge] サーバ時差 実測%dh≠ルール%dh→実測を採用\n" % (measured, rule))
                return measured
    except Exception:
        pass
    return rule


# 互換用(slippage_sim 等が定数として参照)。import時点のルール値。足の補正は m5_bars が毎回算出する。
SERVER_UTC_OFFSET_H = _rule_offset_h()

# 発注系を「呼べない」ように、使ってよい読取関数だけを明示（自己文書化）。
_READ_ONLY_FUNCS = ("initialize", "shutdown", "account_info", "symbol_info",
                    "symbol_info_tick", "symbol_select", "copy_rates_from_pos",
                    "copy_ticks_range",          # 2026-09-25 滑りのティック再現(slippage_sim)。履歴読取のみ
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
    # rates.time はサーバ(GMT+3/冬GMT+2)の壁時計を刻む → 真UTCへ -off。以降 +9h で正しいJST表示になる。
    off = server_utc_offset_h(mt5)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True) - pd.Timedelta(hours=off)
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
