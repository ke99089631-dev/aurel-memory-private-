#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
肥料ブースター: 再加速(reaccel)ハイレバ・デモ執行レーン。2026-10-22 会長GO。
================================================================================
位置づけ(会長の別視点): 再加速は運用(durable)でなく「旬の相場で攻めて肥料にする」ブースター。
  賞味期限あり=使えるうちに使い倒す。ゼロカット前提=入金額が上限=破綻概念なし(都度入金バーン)。
  運用(touch2sb/畑A)とは完全分離=別口座・別端末・別台帳。
目的(まず): 紙の再加速+0.16Rが「実約定でも+か」をデモで測る(実約定EV)。+なら本番ハイレバへ(会長GO+ゼロカット確認後)。
シグナル: setup_engine が生成済みの reaccel 発火(setup_ledger)を demo_exec の fold/fired で読む(再実装しない)。
          紙(コックピット)の「AI再加速」= 外壁+中壁の reaccel 全部。※touch2sb(本命)とは別物。
安全(不変):
  1) 接続先は FERT 端末固定・login=FERT_LOGIN。発注直前に毎回 account_info 再検証:
     login != 27972608(リアル) かつ trade_mode==DEMO(0)。崩れたら中止。
  2) 二重ロック: order_send には --live かつ --arm FERT-GO の両方が必要。既定=観測のみ(0円)。
  3) 荒くてよい(会長)=高レバ寄りサイズ可。ただしデモ。実弾/ゼロカットは別途会長GO。
"""
import os, sys, json, time, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ENVF = os.path.join(HERE, "fert.env")
LEDGER = os.path.join(HERE, "fert_reaccel_ledger.jsonl")
STATE = os.path.join(HERE, "fert_reaccel_state.json")
KILL = os.path.join(HERE, "KILL_FERT")
GOLD_LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
for p in (GOLD_LIVE, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import demo_exec as dx          # 再加速シグナル生成を流用(fold_setups/fired_setups)。MT5はこちらで別接続。

REAL_FORBIDDEN = 27972608
MAGIC = 909090                   # 肥料レーン専用マジック(運用と混ざらない)
FRESH_SEC = 180                  # 鮮度(late fill除外。EV測定を汚さない)
RISK_FRAC = 0.02                 # ★肥料=攻め(2%/trade)。荒くてよい(会長)。本番ハイレバはさらに別途。
MAX_CONCURRENT = 0               # ★同時ポジ上限。0=無制限(会長2026-10-22 A: 重複許可・速さ優先)。将来ゼロカット率で調整するつまみ。
NOTIFY = False                   # 手動エントリー用LINE通知=準備済だが一旦オフ(会長2026-10-22「準備だけ・様子見」)。要時Trueで即稼働。
_NOTIFY_DIR = r"C:\Users\user\.aurel\notify"
if _NOTIFY_DIR not in sys.path:
    sys.path.insert(0, _NOTIFY_DIR)


def fert_line_msg(f, ger, greg):
    """肥料ブースター(再加速)の手動エントリー用サイン。入り/SL/TP+メーター+ラグ対応。"""
    side = "売り" if f["side"] == "SELL" else "買い"
    e = f.get("entry"); sl = f.get("sl"); tp = f.get("tp")
    try:
        risk = abs(float(e) - float(sl)); rr = abs(float(tp) - float(e)) / risk if risk > 0 else 0
        chase = round(risk * 0.5, 2)
    except Exception:
        risk = rr = chase = 0
    reg = ("チョップ" if greg == "chop" else "トレンド") if greg else "—"
    kind = "中壁" if f.get("wall_kind") == "mid" else "外壁"
    return (f"🟠 肥料ブースター（再加速・{kind}）｜ {side}  [手動用]\n"
            f"入り {e:.2f} / SL {sl:.2f} / TP {tp:.2f} ／ RR≈{rr:.1f}\n"
            f"相場メーター ER {ger}（{reg}）\n"
            f"※紙と同条件。デモ(806809)は自動発注済み。\n"
            f"※遅れたら: 建値がTP方向に {chase} 以上動いてたら見送り推奨(RR悪化)。")


def notify(f, ger, greg):
    if not NOTIFY:
        return
    try:
        import line_push
        line_push.send(fert_line_msg(f, ger, greg))
    except Exception as e:
        print("notify err:", e)


def load_env(path):
    env = {}
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1); env[k.strip()] = v.strip()
    return env


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE, encoding="utf-8"))
        except Exception:
            pass
    return {"seen": [], "init": False}


def save_state(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"))


def _log(rec):
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class FertSession:
    def __init__(self, env):
        import MetaTrader5 as mt5
        self.mt5 = mt5
        self.sym = env.get("FERT_SYMBOL", "XAUUSD")
        self.login = int(env.get("FERT_LOGIN", "0"))
        pw = env.get("FERT_PASSWORD", ""); srv = env.get("FERT_SERVER", "")
        if self.login in (0, REAL_FORBIDDEN):
            raise RuntimeError("FERT_LOGIN が不正/リアル→中止")
        ok = mt5.initialize(path=env.get("FERT_TERMINAL", ""), login=self.login,
                            password=pw, server=srv, portable=True)
        if not ok:
            raise RuntimeError("FERT initialize失敗: %s" % (mt5.last_error(),))
        # ★複製端末がキャッシュ口座を自動ログインする事故対策=明示的に期待口座へ切替し検証
        ai = mt5.account_info()
        if ai is None or int(ai.login) != self.login:
            if not mt5.login(self.login, password=pw, server=srv):
                mt5.shutdown(); raise RuntimeError("FERT login %d 切替失敗: %s" % (self.login, mt5.last_error()))
        self.assert_demo("起動")
        mt5.symbol_select(self.sym, True)

    def assert_demo(self, when):
        ai = self.mt5.account_info()
        if ai is None:
            raise RuntimeError("[%s] account_info取得不可→中止" % when)
        if int(ai.login) == REAL_FORBIDDEN:
            self.mt5.shutdown(); raise RuntimeError("[%s] リアル27972608→緊急停止" % when)
        if int(ai.login) != self.login:   # ★期待口座(肥料806809)以外には絶対に撃たない
            self.mt5.shutdown(); raise RuntimeError("[%s] 接続口座%s≠肥料%s→緊急停止(誤口座防止)" % (when, ai.login, self.login))
        if int(getattr(ai, "trade_mode", -1)) != 0:
            raise RuntimeError("[%s] trade_mode非DEMO→中止" % when)
        return ai

    def open_magic(self):
        ps = self.mt5.positions_get(symbol=self.sym) or []
        return sum(1 for p in ps if int(p.magic) == MAGIC)

    def lot_for(self, entry, sl):
        mt5 = self.mt5
        ai = mt5.account_info(); si = mt5.symbol_info(self.sym)
        try:
            rp = abs(float(entry) - float(sl))
            vpp = si.trade_tick_value / si.trade_tick_size        # $/価格単位/lot
            if rp <= 0 or vpp <= 0:
                return float(si.volume_min or 0.01)
            lot = (ai.balance * RISK_FRAC) / (rp * vpp)
            step = si.volume_step or 0.01
            lot = max(si.volume_min or 0.01, round(lot / step) * step)
            return float(min(lot, si.volume_max or lot))
        except Exception:
            return float(getattr(si, "volume_min", 0.01) or 0.01)

    def bracket(self, side, lot, sl, tp, comment):
        mt5 = self.mt5
        self.assert_demo("発注直前")
        mt5.symbol_select(self.sym, True)
        t = mt5.symbol_info_tick(self.sym)
        price = t.ask if side == "BUY" else t.bid
        otype = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
        r = None
        for filling in (mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN):
            req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": self.sym, "volume": float(lot),
                   "type": otype, "price": price, "sl": float(sl), "tp": float(tp),
                   "deviation": 30, "magic": MAGIC, "comment": comment,
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


def reaccel_fires():
    """紙通りの再加速発火(外壁+中壁 全部)。setup_engine 生成を流用。"""
    setups = dx.fold_setups()
    return dx.fired_setups(setups)


def _gold_er(win=288, th=0.12):
    """発火時点の相場メーター(ER=効率比)を金ライブ足で測る。予想でなく記録ラベル=旬の炙り出し用。
       ★発注判定には使わない(メーターは予想フィルタとしてはOOSで降格)。各トレードに貼るだけ。"""
    try:
        import numpy as np, setup_engine as se
        m5 = se._fetch_bars()
        if m5 is None or len(m5) < win + 2:
            return None, None
        c = m5["close"].to_numpy()[-win:]
        path = float(np.abs(np.diff(c)).sum())
        er = abs(float(c[-1]) - float(c[0])) / path if path > 0 else 0.0
        return round(er, 4), ("chop" if er < th else "trend")
    except Exception:
        return None, None


def scan_once(sess, state, armed):
    if os.path.exists(KILL):
        print("[KILL_FERT] 停止"); return True
    fires = reaccel_fires()
    now = time.time()
    if not state.get("init"):
        state["seen"] = sorted({f["sid"] for f in fires}); state["init"] = True; save_state(state)
        print("[初期化] 既存発火 %d 件を既見(過去は撃たない)" % len(state["seen"])); return False
    seen = set(state.get("seen", []))
    for f in fires:
        if f["sid"] in seen:
            continue
        fresh = ((now - float(f["entry_time"])) <= FRESH_SEC) if f.get("entry_time") else False
        if not fresh:
            seen.add(f["sid"]); continue
        ger, greg = _gold_er()        # ★発火時の相場メーター値を各トレードに紐付け(旬の炙り出し用・発注には不使用)
        base = {"lane": "fert-reaccel", "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                "sid": f["sid"], "side": f["side"], "wall_kind": f.get("wall_kind"), "mode": f.get("mode"),
                "entry_ref": f.get("entry"), "sl": f.get("sl"), "tp": f.get("tp"),
                "gold_er": ger, "gold_regime": greg}
        notify(f, ger, greg)          # ★手動エントリー用LINE(紙と同条件・自動/手動の両用)
        if not armed:
            base["result"] = "observe-would-fire"; _log(base)
            print("[観測・撃たない] %s %s %s SL%.2f TP%.2f" % (f["sid"], f["side"], f.get("wall_kind"), f["sl"], f["tp"]))
            seen.add(f["sid"]); continue
        if MAX_CONCURRENT and sess.open_magic() >= MAX_CONCURRENT:
            base["result"] = "skip-maxpos"; _log(base)
            print("[同時ポジ上限%dにつき撃たず] %s" % (MAX_CONCURRENT, f["sid"])); seen.add(f["sid"]); continue
        lot = sess.lot_for(f["entry"], f["sl"])
        r = sess.bracket(f["side"], lot, f["sl"], f["tp"], "fert-%s" % f["sid"])
        ok = (r is not None and r.retcode == sess.mt5.TRADE_RETCODE_DONE)
        base.update({"result": "fire" if ok else "fire-ng", "lot": lot,
                     "retcode": getattr(r, "retcode", None), "deal": getattr(r, "deal", None)})
        _log(base)
        print("[発注%s] %s %s lot%.2f SL%.2f TP%.2f ret=%s" % (
            "OK" if ok else "NG", f["sid"], f["side"], lot, f["sl"], f["tp"], getattr(r, "retcode", None)))
        seen.add(f["sid"])
    state["seen"] = sorted(seen); save_state(state)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--arm", default="")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", type=int, default=0)
    args = ap.parse_args()
    armed = (args.arm == "FERT-GO")
    if not args.live:
        print("観測/発注には --live。発注はさらに --arm FERT-GO(二重ロック)。既定=何もしない。"); return
    env = load_env(ENVF)
    sess = FertSession(env)
    ai = sess.assert_demo("起動確認")
    print("[接続] 肥料reaccel %s / %s / 残高%s / %s  armed=%s risk%.1f%%" % (
        ai.login, ai.server, ai.balance, sess.sym, armed, RISK_FRAC * 100))
    print("[!!] LIVEデモ発注モード(金reaccelを実射)" if armed else "[観測モード] signal記録のみ・0円")
    state = load_state()
    try:
        while True:
            if scan_once(sess, state, armed) or args.once or args.loop <= 0:
                break
            time.sleep(args.loop)
    finally:
        sess.shutdown()
    print("[終了]")


if __name__ == "__main__":
    main()
