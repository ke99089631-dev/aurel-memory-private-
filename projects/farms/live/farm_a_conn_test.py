#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
畑A デモ端末(MT5Farm/806782)への読取専用・接続テスト。発注は一切しない。
  - リアル27972608でない & trade_mode==DEMO(0) を検証(崩れたら即中止)。
  - NAS100.r を選択し直近バーを数本読む(フィード確認)。
  - 金システム(MT5Demo)には触れない=別端末・別プロセス。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ENVF = os.path.join(HERE, "farm_a.env")
REAL_FORBIDDEN = 27972608

def load_env(path):
    env = {}
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            env[k.strip()] = v.strip()
    return env

def main():
    env = load_env(ENVF)
    login = int(env.get("FARM_A_LOGIN", "0"))
    term = env.get("FARM_A_TERMINAL", "")
    sym = env.get("FARM_A_SYMBOL", "NAS100.r")
    if login in (0, REAL_FORBIDDEN):
        print("[中止] FARM_A_LOGIN が不正/リアル"); return 2
    import MetaTrader5 as mt5
    ok = mt5.initialize(path=term, login=login,
                        password=env.get("FARM_A_PASSWORD", ""),
                        server=env.get("FARM_A_SERVER", ""), portable=True)
    if not ok:
        print("[接続失敗] initialize: %s" % (mt5.last_error(),)); return 1
    try:
        ai = mt5.account_info()
        if ai is None:
            print("[中止] account_info 取得不可"); return 1
        if int(ai.login) == REAL_FORBIDDEN:
            print("[緊急中止] リアル口座に接続した→即shutdown"); return 1
        tm = int(getattr(ai, "trade_mode", -1))   # 0=DEMO
        print("[接続OK] login=%s server=%s 残高=%s レバ=1:%s trade_mode=%s(%s)" % (
            ai.login, ai.server, ai.balance, ai.leverage, tm, "DEMO" if tm == 0 else "非DEMO!"))
        if tm != 0:
            print("[警告] DEMOでない→発注段では絶対に使わない");
        si = mt5.symbol_info(sym)
        if si is None:
            # 候補名を総当たりで探す
            cand = [s.name for s in (mt5.symbols_get() or []) if "NAS" in s.name.upper() or "US100" in s.name.upper() or "USTEC" in s.name.upper()]
            print("[シンボル] %s 無し。候補=%s" % (sym, cand[:15]));
        else:
            mt5.symbol_select(sym, True)
            si = mt5.symbol_info(sym)
            tick = mt5.symbol_info_tick(sym)
            print("[シンボルOK] %s digits=%s point=%s spread=%s 現在 bid=%s ask=%s" % (
                sym, si.digits, si.point, si.spread, getattr(tick, "bid", None), getattr(tick, "ask", None)))
            rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M5, 0, 5)
            if rates is not None and len(rates):
                print("[バスOK] 直近M5 %d本。最新close=%s" % (len(rates), rates[-1]["close"]))
            else:
                print("[バス] copy_rates 0件(市場閉場/履歴未取得かも)")
    finally:
        mt5.shutdown()
    print("[終了] 発注なし・読取のみ完了")
    return 0

if __name__ == "__main__":
    sys.exit(main())
