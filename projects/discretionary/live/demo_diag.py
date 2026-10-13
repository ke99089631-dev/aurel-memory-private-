#!/usr/bin/env python3
# AUREL デモ接続 診断（発注なし）。IPCが握れない原因を切り分ける。短いタイムアウトで複数方式を試す。
import os, sys, time
import MetaTrader5 as mt5

TERM = r"C:\Users\user\AurelianMT5\terminal64.exe"
p = os.path.join(os.path.expanduser("~"), ".claude", ".env")
env = {}
for ln in open(p, encoding="utf-8"):
    if "=" in ln and not ln.strip().startswith("#"):
        k, v = ln.split("=", 1); env[k.strip()] = v.strip()
login = int(env["DEMO_LOGIN"]); pw = env["DEMO_PASSWORD"]; srv = env["DEMO_SERVER"]

def run(tag, **kw):
    t0 = time.time()
    ok = mt5.initialize(**kw)
    dt = time.time() - t0
    err = mt5.last_error()
    ai = mt5.account_info() if ok else None
    acct = None if ai is None else (ai.login, ai.server, ai.trade_mode, ai.balance, ai.company)
    print("[%s] ok=%s (%.1fs) err=%s acct=%s" % (tag, ok, dt, err, acct), flush=True)
    mt5.shutdown()

# 1) パス指定・creds無し・portable無し（＝動いている橋と同じ方式／ただし別端末）
run("A attach np", path=TERM, timeout=15000)
# 2) パス指定・creds無し・portable有り
run("B attach portable", path=TERM, portable=True, timeout=15000)
# 3) パス指定・フルログイン・portable無し
run("C login np", path=TERM, login=login, password=pw, server=srv, timeout=20000)
# 4) パス指定・フルログイン・portable有り
run("D login portable", path=TERM, login=login, password=pw, server=srv, portable=True, timeout=20000)
print("DONE", flush=True)
