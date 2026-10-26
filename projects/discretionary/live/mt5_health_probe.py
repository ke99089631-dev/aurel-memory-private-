# -*- coding: utf-8 -*-
"""MT5 端末の接続状態を読取専用で点検する（発注系 API は一切使わない）。
対象=デモ端末のみ(MT5Demo/MT5Fert/MT5Farm)。リアル(Program Files)は serve_chart の橋に任せる。
出力: 端末ごとに connected / algo(trade_allowed) / login / trade_mode / balance / positions 数。
"""
import sys, json, time
sys.stdout.reconfigure(encoding="utf-8")
import MetaTrader5 as mt5

TERMINALS = [
    ("MT5Demo(肥料の前身・デモ執行)", r"C:\Users\user\MT5Demo\terminal64.exe"),
    ("MT5Fert(肥料デモ)",            r"C:\Users\user\MT5Fert\terminal64.exe"),
    ("MT5Farm(畑)",                  r"C:\Users\user\MT5Farm\terminal64.exe"),
]
REAL_LOGIN = 27972608

for name, path in TERMINALS:
    row = {"terminal": name, "path": path}
    ok = mt5.initialize(path=path, timeout=15000)
    if not ok:
        row["error"] = f"initialize failed: {mt5.last_error()}"
        print(json.dumps(row, ensure_ascii=False)); continue
    try:
        ti = mt5.terminal_info()
        ai = mt5.account_info()
        row["connected"] = bool(ti.connected) if ti else None
        row["algo_trading_on"] = bool(ti.trade_allowed) if ti else None
        row["ping_ms"] = ti.ping_last/1000 if ti else None
        if ai:
            row["login"] = ai.login
            row["trade_mode"] = {0: "DEMO", 1: "CONTEST", 2: "REAL"}.get(ai.trade_mode, ai.trade_mode)
            row["server"] = ai.server
            row["balance"] = ai.balance
            row["equity"] = ai.equity
            row["is_real_account"] = (ai.login == REAL_LOGIN)
        pos = mt5.positions_get()
        row["positions"] = len(pos) if pos is not None else None
        ord_ = mt5.orders_get()
        row["pending_orders"] = len(ord_) if ord_ is not None else None
        tk = mt5.symbol_info_tick("XAUUSD")
        if tk:
            row["xauusd_bid"] = tk.bid
            row["tick_age_s"] = round(time.time() - tk.time, 1)
    finally:
        mt5.shutdown()
    print(json.dumps(row, ensure_ascii=False))
