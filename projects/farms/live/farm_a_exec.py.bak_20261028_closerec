#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
畑A デモ執行機 — NAS100.r / MT5Farm(806782) 専用。金システム(MT5Demo)とは別端末で非競合。
================================================================================
安全(不変):
  1) 接続先は MT5Farm 固定・login=806782。発注関数を呼ぶ毎回直前に account_info を読み、
     login != 27972608(リアル) かつ trade_mode==DEMO(0) を再検証。崩れたら発注中止。
  2) 二重ロック: 実際に order_send するには --live かつ --arm FARM-GO の両方が必要。
     どちらか欠ければ観測のみ(signalをledgerに記録するだけ・0円)。
  3) 既定は観測(dry)。会長GOがあるまで撃たない。
シグナル: NAS100.r の直近M5を自前で読み、touch2sb_engine.latest_signal(保ち2, tp_mm0.85) + NYセッションで判定
         (=金の+エンジンの忠実移植を、金固有閾値なしでUS100に適用)。フィード＝撃つ銘柄で一貫。
"""
import os, sys, json, time, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ENVF = os.path.join(HERE, "farm_a.env")
LEDGER = os.path.join(HERE, "farm_a_exec_ledger.jsonl")
STATE = os.path.join(HERE, "farm_a_exec_state.json")
KILL = os.path.join(HERE, "KILL_FARM_A")
GOLD_LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
WW = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
for p in (GOLD_LIVE, WW, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pandas as pd
import touch2sb_engine as sb
import run_gate as rg

REAL_FORBIDDEN = 27972608
NEED_TOUCHES = 2
PROF = {"tp_mm": 0.85}        # 金固有閾値なし・NYはセッションで担保
RISK_FRAC = 0.004             # 口座の0.4%/トレード(凍結仕様)
# ★2026-10-26 会長GO: 紙(touch2sb_engine.backtest MAX_HOLD=288)と同じ時間切れを実射に入れる。
#   約定から確定M5足288本(≈24h取引時間)で成行クローズ。TP/SL式・入り方は不変。同時2本化は NAS100 で別途測ってから(今は非重複のまま)。
MAX_HOLD_BARS = 288
# ★2026-10-26 会長GO(17:30)『畑Aも2本までにしよう』: 同時建玉2本まで(3本目の点火は observe)。
#   根拠(US100 NY 2024-01〜26-06・24h切れ固定・コスト0.81bps): 単ポジ 合計+35.1R/年≈+14/Sharpe0.55/DD-18.7
#   → 同時2本 +88.6R/年≈+36/Sharpe0.96/DD-22.6(OOS +0.168→+0.207)。3本以上は伸びるがDDも伸びる(無制限DD-30.8・最大同時8本)。
#   出口(事前固定)=新ルールで確定30本に達した時点でネット平均R<0 なら MAX_CONCURRENT=1 に戻す(時間切れは残す)。
#   RESULTS: AssetEmpire/empire/research/wall_to_wall/RESULTS_touch2sb_hold_and_concurrency.md
MAX_CONCURRENT = 2
BARS = sb.BOX_WINDOW + sb.RETEST_BARS + 10   # 信号判定に足りる本数


def load_env(path):
    env = {}
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding="utf-8"))
        except Exception:
            pass
    return {"last_confirm": None}


def save_state(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"))


class FarmSession:
    def __init__(self, env):
        import MetaTrader5 as mt5
        self.mt5 = mt5
        self.env = env
        self.sym = env.get("FARM_A_SYMBOL", "NAS100.r")
        self.login = int(env.get("FARM_A_LOGIN", "0"))
        pw = env.get("FARM_A_PASSWORD", ""); srv = env.get("FARM_A_SERVER", "")
        if self.login in (0, REAL_FORBIDDEN):
            raise RuntimeError("FARM_A_LOGIN が不正/リアル→中止")
        ok = mt5.initialize(path=env.get("FARM_A_TERMINAL", ""), login=self.login,
                            password=pw, server=srv, portable=True)
        if not ok:
            raise RuntimeError("MT5Farm initialize失敗: %s" % (mt5.last_error(),))
        # ★複製端末がキャッシュ口座を自動ログインする事故対策=明示的に期待口座へ切替し検証
        ai = mt5.account_info()
        if ai is None or int(ai.login) != self.login:
            if not mt5.login(self.login, password=pw, server=srv):
                mt5.shutdown(); raise RuntimeError("FARM_A login %d 切替失敗: %s" % (self.login, mt5.last_error()))
        self.assert_demo("起動")
        mt5.symbol_select(self.sym, True)

    def assert_demo(self, when):
        ai = self.mt5.account_info()
        if ai is None:
            raise RuntimeError("[%s] account_info取得不可→中止" % when)
        if int(ai.login) == REAL_FORBIDDEN:
            self.mt5.shutdown()
            raise RuntimeError("[%s] リアル27972608に接続→緊急停止" % when)
        if int(ai.login) != self.login:   # ★期待口座(畑A806782)以外には絶対に撃たない
            self.mt5.shutdown()
            raise RuntimeError("[%s] 接続口座%s≠畑A%s→緊急停止(誤口座防止)" % (when, ai.login, self.login))
        if int(getattr(ai, "trade_mode", -1)) != 0:
            raise RuntimeError("[%s] trade_mode非DEMO→発注中止" % when)
        return ai

    def bars(self, n=BARS):
        mt5 = self.mt5
        r = mt5.copy_rates_from_pos(self.sym, mt5.TIMEFRAME_M5, 0, n)
        if r is None or len(r) < sb.BOX_WINDOW + 2:
            return None
        df = pd.DataFrame(r)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.set_index("time")[["open", "high", "low", "close"]]
        # 形成中の最新足は落とす(確定足のみ)
        return df.iloc[:-1]

    def lot_for(self, risk_price):
        """口座0.4%/trade からロット。risk_price=SL幅(価格単位)。1価格単位あたりの$=tick_value/tick_size。"""
        mt5 = self.mt5
        ai = mt5.account_info(); si = mt5.symbol_info(self.sym)
        try:
            tick_val = si.trade_tick_value; tick_sz = si.trade_tick_size
            val_per_price = tick_val / tick_sz            # $ / 1価格単位 / 1lot (×pointしない)
            risk_usd = ai.balance * RISK_FRAC
            if risk_price <= 0 or val_per_price <= 0:
                return float(si.volume_min or 0.01)
            lot = risk_usd / (risk_price * val_per_price)
            step = si.volume_step or 0.01
            lot = max(si.volume_min or 0.01, round(lot / step) * step)
            return float(min(lot, si.volume_max or lot))
        except Exception:
            return float(getattr(si, "volume_min", 0.01) or 0.01)

    def open_magic_positions(self, magic):
        ps = self.mt5.positions_get(symbol=self.sym) or []
        return sum(1 for p in ps if int(p.magic) == magic)

    def bars_since(self, t_open):
        """約定(サーバ時刻epoch)からの確定M5足本数。rates.time も同じサーバ時刻基準なので補正不要。"""
        mt5 = self.mt5
        r = mt5.copy_rates_from_pos(self.sym, mt5.TIMEFRAME_M5, 0, 3000)
        if r is None:
            return None
        return int(sum(1 for x in r if int(x["time"]) > int(t_open)))

    def close_expired(self, magic, dry=False):
        """★時間切れ(MAX_HOLD_BARS)の建玉を成行クローズ。畑Aデモ限定・毎回 assert_demo。"""
        mt5 = self.mt5
        self.assert_demo("時間切れ確認")
        out = []
        for p in (mt5.positions_get(symbol=self.sym) or []):
            if int(p.magic) != magic:
                continue
            nb = self.bars_since(p.time)
            if nb is None or nb < MAX_HOLD_BARS:
                continue
            is_buy = int(p.type) == mt5.POSITION_TYPE_BUY
            t = mt5.symbol_info_tick(self.sym)
            price = t.bid if is_buy else t.ask
            rec = {"farm": "A-US100", "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                   "symbol": self.sym, "mode": "close", "reason": "TIME", "bars": nb, "ticket": int(p.ticket),
                   "comment": p.comment, "side": "BUY" if is_buy else "SELL", "entry": float(p.price_open),
                   "exit_ref": float(price), "profit_before": float(p.profit), "lot": float(p.volume)}
            if dry:
                rec["dry"] = True; out.append(rec); continue
            self.assert_demo("時間切れクローズ直前")
            r = None
            for filling in (mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN):
                req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": self.sym, "position": int(p.ticket),
                       "volume": float(p.volume), "type": (mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY),
                       "price": price, "deviation": 20, "magic": magic, "comment": "farmA-TIME",
                       "type_time": mt5.ORDER_TIME_GTC, "type_filling": filling}
                r = mt5.order_send(req)
                if r is None:
                    continue
                if r.retcode == mt5.TRADE_RETCODE_DONE or r.retcode not in (mt5.TRADE_RETCODE_INVALID_FILL,):
                    break
            rec["retcode"] = getattr(r, "retcode", None); rec["exit"] = getattr(r, "price", None)
            rec["ok"] = (r is not None and r.retcode == mt5.TRADE_RETCODE_DONE)
            out.append(rec)
        return out

    def bracket(self, side, lot, sl, tp, comment, magic):
        mt5 = self.mt5
        self.assert_demo("発注直前")       # ★毎回再検証
        mt5.symbol_select(self.sym, True)
        t = mt5.symbol_info_tick(self.sym)
        price = t.ask if side == "BUY" else t.bid
        otype = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
        r = None
        for filling in (mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN):
            req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": self.sym,
                   "volume": float(lot), "type": otype, "price": price,
                   "sl": float(sl), "tp": float(tp), "deviation": 20,
                   "magic": magic, "comment": comment,
                   "type_time": mt5.ORDER_TIME_GTC, "type_filling": filling}
            r = mt5.order_send(req)
            if r is None:
                continue
            if r.retcode == mt5.TRADE_RETCODE_DONE:
                return r
            if r.retcode not in (mt5.TRADE_RETCODE_INVALID_FILL,):
                return r
        return r

    def shutdown(self):
        self.mt5.shutdown()


MAGIC = 806782


def scan_once(sess, state, armed):
    if os.path.exists(KILL):
        print("[KILL_FARM_A] 停止"); return state, True
    # ★時間切れ(288本)の建玉を先にクローズ(紙のTIME切れと同じ)。armed時のみ実行・記録。
    if armed:
        try:
            for rec in sess.close_expired(MAGIC):
                _log(rec)
                print("[時間切れクローズ] %s bars=%d entry=%.2f exit=%s ok=%s" % (
                    rec["side"], rec["bars"], rec["entry"], rec.get("exit"), rec.get("ok")))
        except Exception as e:
            print("[時間切れ確認エラー・継続] %r" % e)
    m5 = sess.bars()
    if m5 is None:
        print("[%s] バー不足/未取得→スキップ" % datetime.now().strftime("%H:%M:%S")); return state, False
    sig = sb.latest_signal(m5, NEED_TOUCHES, PROF)
    if sig is None:
        return state, False
    # NYセッション判定(入る足=確定足+5分)
    entry_bar = pd.Timestamp(m5.index[-1]) + pd.Timedelta(minutes=5)
    ser = pd.Series(pd.to_datetime([entry_bar], utc=True))
    m = rg.ny_session_mask(ser)
    mv = m.iloc[0] if hasattr(m, "iloc") else m[0]
    if not bool(mv):
        return state, False
    cid = str(int(pd.Timestamp(m5.index[-1]).timestamp()))
    if state.get("last_confirm") == cid:
        return state, False           # 同じ確認足で二度撃たない
    state["last_confirm"] = cid; save_state(state)
    side = sig["side"]; sl = sig["sl"]; tp = sig["tp"]; wall = sig.get("wall"); risk = sig.get("risk")
    base = {"farm": "A-US100", "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
            "symbol": sess.sym, "side": side, "wall": wall, "sl": sl, "tp": tp, "risk": risk,
            "confirm_id": cid}
    # 同時建玉の上限(MAX_CONCURRENT本まで・枠が埋まっていれば撃たない)
    if armed and sess.open_magic_positions(MAGIC) >= MAX_CONCURRENT:
        base.update({"mode": "observe", "why": "同時%d本の枠が埋まり(非重複)" % MAX_CONCURRENT}); _log(base)
        print("[observe・同時%d本の枠が埋まり撃たず] %s SL%.2f TP%.2f" % (MAX_CONCURRENT, side, sl, tp)); return state, False
    if not armed:
        base.update({"mode": "observe-would-fire"}); _log(base)
        print("[観測・撃たない] %s wall%.2f SL%.2f TP%.2f risk%.2f" % (side, wall or 0, sl, tp, risk or 0))
        return state, False
    # ここから先は二重ロック(--live --arm FARM-GO)通過時のみ
    rp = abs((sig.get("entry") or m5['close'].iloc[-1]) - sl)
    lot = sess.lot_for(rp)
    r = sess.bracket(side, lot, sl, tp, "farmA-%s" % cid, MAGIC)
    ok = (r is not None and r.retcode == sess.mt5.TRADE_RETCODE_DONE)
    base.update({"mode": "fire", "lot": lot, "retcode": getattr(r, "retcode", None),
                 "deal": getattr(r, "deal", None), "ok": ok}); _log(base)
    print("[発注%s] %s lot%.2f SL%.2f TP%.2f ret=%s" % ("OK" if ok else "NG", side, lot, sl, tp, getattr(r, "retcode", None)))
    return state, False


def _log(rec):
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="MT5Farmに接続(観測含む)。無指定=接続せず説明のみ")
    ap.add_argument("--arm", default="", help="発注解錠キー。'FARM-GO'かつ--liveで初めて撃つ(二重ロック)")
    ap.add_argument("--once", action="store_true", help="1回だけスキャン")
    ap.add_argument("--loop", type=int, default=0, help="N秒おきにループ")
    args = ap.parse_args()
    armed = (args.arm == "FARM-GO")
    if not args.live:
        print("観測/発注には --live が必要。発注はさらに --arm FARM-GO(二重ロック)。既定は何もしない。"); return
    env = load_env(ENVF)
    sess = FarmSession(env)
    ai = sess.assert_demo("起動確認")
    print("[接続] 畑A %s / %s / 残高%s / %s  armed=%s" % (ai.login, ai.server, ai.balance, sess.sym, armed))
    if armed:
        print("[!!] 二重ロック解錠=LIVEデモ発注モード。NAS100.rに実際に撃ちます。")
    else:
        print("[観測モード] signalを記録するだけ・0円。")
    state = load_state()
    try:
        while True:
            state, stop = scan_once(sess, state, armed)
            if stop or args.once or args.loop <= 0:
                break
            time.sleep(args.loop)
    finally:
        sess.shutdown()
    print("[終了]")


if __name__ == "__main__":
    main()
