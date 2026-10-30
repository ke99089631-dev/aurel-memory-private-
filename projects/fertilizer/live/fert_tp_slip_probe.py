# -*- coding: utf-8 -*-
"""ヒゲ/スプレッド計測プローブ(読取のみ・発注API不使用・会長GO 2026-10-30「1からやろう」)。
肥料デモ端末(806809)のティック(bid/ask)で、各決済が「紙(bid)ならTP約定・デモ(実約定価格)は未約定」
= ヒゲ/スプレッドで奪われた/救われた勝ちだったかを測る。
  売り: 決済はASK側。TP(下)はASK<=tpで約定・紙基準はBID<=tp。SL(上)はASK>=sl。
  買い: 決済はBID側(=紙と同じ)なのでスプレ差は原則出ない(対照)。
安全: account_info().login を検証(肥料806809のみ)。REAL(27972608)に繋がったら即shutdown+中断。
      copy_ticks_range / account_info / history_deals_get / symbol_info_tick だけ。パスワードは出力しない。
"""
import os, json, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENVF = os.path.join(HERE, "fert.env")
LEDGER = os.path.join(HERE, "fert_reaccel_stop_ledger.jsonl")
OUT = os.path.join(HERE, "fert_tp_slip_report.json")
REAL_FORBIDDEN = 27972608

def load_env(path):
    env = {}
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        env[k.strip()] = v.strip()
    return env

def connect(env):
    import MetaTrader5 as mt5
    login = int(env.get("FERT_LOGIN", "0"))
    if login in (0, REAL_FORBIDDEN):
        raise RuntimeError("FERT_LOGIN 不正(リアル禁止)")
    ok = mt5.initialize(path=env.get("FERT_TERMINAL", ""), login=login,
                        password=env.get("FERT_PASSWORD", ""), server=env.get("FERT_SERVER", ""),
                        portable=True)
    if not ok:
        raise RuntimeError("initialize失敗: %s" % (mt5.last_error(),))
    ai = mt5.account_info()
    if ai is None or int(ai.login) == REAL_FORBIDDEN or int(ai.login) != login:
        mt5.shutdown()
        raise RuntimeError("★安全弁: 口座検証失敗(繋がった口座が肥料でない)")
    return mt5, login

def main(limit=12, validate=True):
    env = load_env(ENVF)
    rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]
    closes = [r for r in rows if r.get("event") == "close" and r.get("reason") in ("TP", "SL")]
    closes = closes[-limit:]
    mt5, login = connect(env)
    sym = env.get("FERT_SYMBOL", "XAUUSD")
    try:
        mt5.symbol_select(sym, True)
        res = []
        for c in closes:
            sid = c["sid"]; side = c["side"]; sl = float(c["sl"]); tp = float(c["tp"])
            pos = int(c["position"])
            deals = mt5.history_deals_get(position=pos) or []
            ins = [d for d in deals if int(getattr(d, "entry", -1)) == 0]
            outs = [d for d in deals if int(getattr(d, "entry", -1)) == 1]
            if not ins or not outs:
                continue
            t0 = int(ins[0].time); t1 = int(outs[-1].time)
            # 窓はサーバ時刻のズレ(GMT+3)に強いよう広く取り、ティックのepochで厳密に絞る(tz非依存)
            a = dt.datetime.fromtimestamp(t0 - 21600, dt.timezone.utc)
            b = dt.datetime.fromtimestamp(t1 + 21600, dt.timezone.utc)
            raw = mt5.copy_ticks_range(sym, a, b, mt5.COPY_TICKS_ALL)
            row = {"sid": sid, "side": side, "reason": c["reason"], "R": c.get("R"),
                   "sl": sl, "tp": tp, "n_ticks": 0}
            if raw is not None and len(raw):
                tt = np.asarray(raw["time"], np.int64)
                m = (tt >= t0) & (tt <= t1)      # 建玉〜決済の間のティックだけ
                row["n_ticks"] = int(m.sum()); row["n_raw"] = int(len(raw))
                row["t0"] = t0; row["t1"] = t1
            if row["n_ticks"]:
                bid = np.asarray(raw["bid"], float)[m]; ask = np.asarray(raw["ask"], float)[m]
                row["spread_med"] = round(float(np.median(ask - bid)), 3)
                row["bid_lo"] = round(float(bid.min()), 2); row["bid_hi"] = round(float(bid.max()), 2)
                row["ask_lo"] = round(float(ask.min()), 2); row["ask_hi"] = round(float(ask.max()), 2)
                if side == "SELL":
                    tp_bid = bool((bid <= tp).any()); tp_ask = bool((ask <= tp).any())
                    row["tp_paper_touch"] = tp_bid       # 紙(bid)がTPに触れた
                    row["tp_demo_fill"] = tp_ask         # デモ(ask)が実際に約定できた
                    row["tp_spread_miss"] = bool(tp_bid and not tp_ask)   # ヒゲで奪われた
                    row["sl_paper_touch"] = bool((bid >= sl).any())
                    row["sl_demo_hit"] = bool((ask >= sl).any())
                else:  # BUY: 決済はbid=紙と同じ(対照)
                    tp_bid = bool((bid >= tp).any())
                    row["tp_paper_touch"] = tp_bid; row["tp_demo_fill"] = tp_bid
                    row["tp_spread_miss"] = False
                    row["sl_paper_touch"] = bool((bid <= sl).any())
                    row["sl_demo_hit"] = bool((bid <= sl).any())
            res.append(row)
        # 集計
        sells = [r for r in res if r.get("side") == "SELL" and r.get("n_ticks")]
        miss = [r for r in sells if r.get("tp_spread_miss")]
        agg = {"generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "login": login, "symbol": sym,
               "n_measured": len([r for r in res if r.get("n_ticks")]),
               "n_sell": len(sells), "tp_spread_miss_sell": len(miss),
               "spread_med_all": round(float(np.median([r["spread_med"] for r in res if r.get("n_ticks")])), 3) if res else None}
        json.dump({"summary": agg, "rows": res}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # 検証出力(画面)
        print("接続OK 口座=%d 銘柄=%s (読取のみ)" % (login, sym))
        print("計測 %d本 / ティック取得できた本 %d" % (len(res), agg["n_measured"]))
        for r in res:
            if not r.get("n_ticks"):
                print("  %-8s %s %s  ティック0(時刻ズレ疑い)" % (r["sid"], r["side"], r["reason"])); continue
            tag = ""
            if r["side"] == "SELL" and r.get("tp_spread_miss"):
                tag = " ★ヒゲでTP奪われ(紙勝ち/デモ負け)"
            print("  %-8s %-4s %s R%+.2f | sp中央%.3f bid[%.2f-%.2f] ask[%.2f-%.2f] TP%.2f→紙触%s/デモ約定%s%s" % (
                r["sid"], r["side"], r["reason"], r.get("R") or 0, r["spread_med"],
                r["bid_lo"], r["bid_hi"], r["ask_lo"], r["ask_hi"], r["tp"],
                r.get("tp_paper_touch"), r.get("tp_demo_fill"), tag))
        print("\n売り%d本中 ヒゲ/スプレッドでTP奪われ=%d本 / 中央スプレッド%.3f" % (
            agg["n_sell"], agg["tp_spread_miss_sell"], agg["spread_med_all"] or 0))
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
