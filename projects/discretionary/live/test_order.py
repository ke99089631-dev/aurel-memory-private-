#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AUREL デモ発注 接続テスト（デモ専用・実弾ゼロ）。0.01を成行で出し→即クローズ→通るか証明。
import sys, time
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import demo_exec

sess = demo_exec.DemoSession()            # 接続＋assert_demo（リアルでない・デモである を検証）
ai = sess.assert_demo("test")
print("接続OK login=%s mode=%s(0=demo) 残高=%s" % (ai.login, ai.trade_mode, ai.balance))
mt5 = sess.mt5
SYM = demo_exec.SYMBOL
mt5.symbol_select(SYM, True)
t = mt5.symbol_info_tick(SYM)
sl = round(t.bid - 8.0, 2); tp = round(t.bid + 8.0, 2)
print("発注: BUY 0.01 %s price≈%.2f SL%.2f TP%.2f" % (SYM, t.ask, sl, tp))
r = sess.bracket("BUY", 0.01, sl, tp, "aurel-conn-test")
ok = (r is not None and r.retcode == mt5.TRADE_RETCODE_DONE)
print("発注結果: ok=%s retcode=%s deal=%s 約定price=%s" % (ok, getattr(r,'retcode',None), getattr(r,'deal',None), getattr(r,'price',None)))
time.sleep(1.0)
pos = mt5.positions_get(symbol=SYM) or []
mine = [p for p in pos if getattr(p,'magic',0) == demo_exec.MAGIC]
print("建玉確認: 自分の建玉 %d 件" % len(mine))
# 即クローズ
for p in mine:
    tick = mt5.symbol_info_tick(SYM)
    is_long = (p.type == mt5.POSITION_TYPE_BUY)
    price = tick.bid if is_long else tick.ask
    otype = mt5.ORDER_TYPE_SELL if is_long else mt5.ORDER_TYPE_BUY
    cr = None
    for filling in (mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN):
        req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": SYM, "volume": p.volume,
               "type": otype, "position": p.ticket, "price": price, "deviation": 20,
               "magic": demo_exec.MAGIC, "comment": "aurel-conn-test-close",
               "type_time": mt5.ORDER_TIME_GTC, "type_filling": filling}
        cr = mt5.order_send(req)
        if cr is not None and cr.retcode == mt5.TRADE_RETCODE_DONE:
            break
    print("クローズ結果: retcode=%s" % getattr(cr,'retcode',None))
ai2 = mt5.account_info()
rem = mt5.positions_get(symbol=SYM) or []
print("最終: 残高=%s 残建玉(自分分)=%d" % (ai2.balance, len([p for p in rem if getattr(p,'magic',0)==demo_exec.MAGIC])))
print("=> 発注→約定→クローズまで通れば『注文できる』の証明")
sess.shutdown()
