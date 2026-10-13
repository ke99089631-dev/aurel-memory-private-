#!/usr/bin/env python3
# AUREL デモMT5ログインテスト（2026-10-13）。AurelianMT5端末にプログラムからログインし、
# 「本当にデモ口座か」を読取検証するだけ。発注は一切しない・残高も1円も動かさない。
# 認証情報は ~/.claude/.env の DEMO_LOGIN / DEMO_PASSWORD / DEMO_SERVER から読む。
# ★安全ガード（不変）: trade_mode==DEMO かつ login!=27972608 でなければ即中断。
# ★秘密保持: パスワードは絶対に画面に出さない・ログに残さない。
import os, sys

TERMINAL = r"C:\Users\user\AurelianMT5\terminal64.exe"
REAL_FORBIDDEN = 27972608  # 会長のリアル口座。これには絶対ログインしない
ENV_PATH = os.path.join(os.path.expanduser("~"), ".claude", ".env")

def load_env():
    vals = {}
    if not os.path.exists(ENV_PATH):
        return vals
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals

def main():
    import MetaTrader5 as mt5
    env = load_env()
    login = env.get("DEMO_LOGIN", "")
    password = env.get("DEMO_PASSWORD", "")
    server = env.get("DEMO_SERVER", "")
    missing = [k for k, v in [("DEMO_LOGIN", login), ("DEMO_PASSWORD", password), ("DEMO_SERVER", server)] if not v or v.startswith("<")]
    if missing:
        print("ERROR: 未設定:", ", ".join(missing), "（~/.claude/.env に登録してください）", file=sys.stderr)
        return 2
    try:
        login_i = int(login)
    except ValueError:
        print("ERROR: DEMO_LOGIN は数字のみ:", login, file=sys.stderr)
        return 2
    if login_i == REAL_FORBIDDEN:
        print("ABORT: DEMO_LOGIN がリアル口座(27972608)と同じ。デモ専用です。", file=sys.stderr)
        return 3

    ok = mt5.initialize(path=TERMINAL, login=login_i, password=password, server=server, portable=True)
    if not ok:
        code, msg = mt5.last_error()
        print("ログイン失敗 last_error=(%s) %s  server=%s login=%s" % (code, msg, server, login_i), file=sys.stderr)
        mt5.shutdown()
        return 1

    ai = mt5.account_info()
    if ai is None:
        print("ログインは通ったが account_info が取得できません。", file=sys.stderr)
        mt5.shutdown()
        return 1

    # trade_mode: 0=REAL, 1=DEMO, 2=CONTEST
    MODE = {0: "REAL(実弾)", 1: "DEMO(デモ)", 2: "CONTEST(コンテスト)"}
    mode_txt = MODE.get(ai.trade_mode, "不明(%s)" % ai.trade_mode)

    print("=== ログイン成功 ===")
    print("口座番号 :", ai.login)
    print("サーバー :", ai.server)
    print("口座種別 :", mode_txt)
    print("通貨     :", ai.currency)
    print("残高     :", ai.balance)
    print("会社     :", ai.company)

    verdict_ok = True
    if ai.login == REAL_FORBIDDEN:
        print("⛔ 危険: リアル口座(27972608)にログインしている。即遮断。", file=sys.stderr)
        verdict_ok = False
    if ai.trade_mode != 1:
        print("⛔ 危険: これはデモ口座ではない(trade_mode=%s)。デモ以外では発注させない。" % ai.trade_mode, file=sys.stderr)
        verdict_ok = False
    if verdict_ok:
        print("✅ 安全確認OK: デモ口座・リアルではない。発注ガード通過（ただし発注は会長GO後のみ）。")

    mt5.shutdown()
    return 0 if verdict_ok else 3

if __name__ == "__main__":
    sys.exit(main())
