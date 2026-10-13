#!/usr/bin/env python3
# AUREL デモ端末 能力検証（発注なし・読取のみ）。
#  ①デモ再確認 ②金シンボル名の特定 ③金のライブtick/M5足が流れるか ④1端末に2プロセス同時接続できるか。
import os, sys, subprocess, json
import MetaTrader5 as mt5

TERM = r"C:\Users\user\MT5Demo\terminal64.exe"
REAL_FORBIDDEN = 27972608
p = os.path.join(os.path.expanduser("~"), ".claude", ".env")
env = {}
for ln in open(p, encoding="utf-8"):
    if "=" in ln and not ln.strip().startswith("#"):
        k, v = ln.split("=", 1); env[k.strip()] = v.strip()
login = int(env["DEMO_LOGIN"]); pw = env["DEMO_PASSWORD"]; srv = env["DEMO_SERVER"]

if not mt5.initialize(path=TERM, login=login, password=pw, server=srv, portable=True):
    print("INIT FAIL", mt5.last_error()); sys.exit(1)

ai = mt5.account_info()
print("[acct] login=%s mode=%s(0=demo) bal=%s %s" % (ai.login, ai.trade_mode, ai.balance, ai.company))
if ai.login == REAL_FORBIDDEN or ai.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
    print("[ABORT] not a safe demo"); mt5.shutdown(); sys.exit(3)

# ② 金シンボル候補を探す
print("--- 金シンボル候補 ---")
cands = []
for s in mt5.symbols_get("*XAU*") or []:
    cands.append(s.name)
print("XAU含むシンボル:", cands[:20])

# ③ 代表候補でtick/M5足
for sym in ["XAUUSD", "XAUUSD+", "XAUUSD.", "GOLD"]:
    if mt5.symbol_select(sym, True):
        t = mt5.symbol_info_tick(sym)
        bars = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M5, 0, 3)
        nb = 0 if bars is None else len(bars)
        bid = None if t is None else t.bid
        last_close = None if (bars is None or nb == 0) else float(bars[-1]["close"])
        print("[sym %s] select=OK bid=%s M5本数=%s 最新close=%s" % (sym, bid, nb, last_close))
    else:
        print("[sym %s] select=NG (%s)" % (sym, mt5.last_error()))

# ④ 2プロセス同時接続テスト: 親が握ったまま子pythonが同端末へ繋げるか
child = r'''
import MetaTrader5 as mt5, sys
ok = mt5.initialize(path=r"%s", portable=True)
print("CHILD init=%%s err=%%s" %% (ok, mt5.last_error()))
if ok:
    ai = mt5.account_info()
    print("CHILD acct=%%s" %% (None if ai is None else ai.login))
mt5.shutdown()
''' % TERM
print("--- 2プロセス同時接続テスト（親が接続保持中に子が接続を試みる）---")
r = subprocess.run([sys.executable, "-c", child], capture_output=True, text=True, timeout=40)
print(r.stdout.strip() or r.stderr.strip())

mt5.shutdown()
print("DONE")
