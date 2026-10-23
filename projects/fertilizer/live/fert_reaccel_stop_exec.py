#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
肥料reaccel 逆指値(pending-stop)執行レーン — 2026-10-23 会長GO(再構築)。
================================================================================
なぜ作り直したか(2026-10-23 判明):
  旧 fert_reaccel_exec.py は「確定足を見てから成行で後追い」。再加速の建値時刻は
  "割れた足の頭" に刻まれ、その足が確定(5分後)するまで機械は気づけない=検知時点で
  建値は必ず ~302秒前。鮮度ゲート FRESH_SEC=180 を常に超えて無言スキップ。結果、
  MT5 806809 の残高は初期1000のまま不動・約定履歴ゼロ=一度も発注できていなかった。

本機の考え方(紙=バックテストの約定機序そのものを再現):
  バックテストは「直前足の安値(SELL)/高値(BUY)に逆指値を置き、次足がそこを割った瞬間に約定」。
  だから live も "逆指値(SELL_STOP/BUY_STOP)を置いて足の最中に約定" させる。
  リテスト確定→トリガー待ちの窓(setup_ledger reaccel.status=="waiting")の間、
  毎tick「直前(最新確定)足の極値」に逆指値を置き直す(トレーリングでなく"直前足追従")。
  これで鮮度問題が消え、紙+0.16Rが実約定でも残るかを初めて測れる。

安全(不変):
  1) 接続=FERT端末固定・login=FERT_LOGIN。発注/変更/取消の直前に毎回 account_info 再検証
     (リアル27972608排除・trade_mode==DEMO限定・誤口座なら緊急停止)。
  2) 二重ロック: 実際に order_send(置く/変える/消す)するには --live かつ --arm FERT-GO。
     既定=観測のみ(0円・"何を置くはずか"を台帳に記録するだけ)。
  3) 状態はMT5の実オーダー/建玉から毎tick再構成(ローカルstate非依存=消失に強い)。
     再約定防止の done 集合だけ git同期外(MT5Fert隣)に保持。
"""
import os, sys, json, time, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ENVF = os.path.join(HERE, "fert.env")
LEDGER = os.path.join(HERE, "fert_reaccel_stop_ledger.jsonl")   # 発注/変更/取消/約定の記録(台帳=成績の素)
KILL = os.path.join(HERE, "KILL_FERT")
GOLD_LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
for p in (GOLD_LIVE, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pandas as pd
import demo_exec as dx           # fold_setups(setup_ledgerを畳む)を流用。シグナルは再実装しない。
import setup_engine as se        # 定数(REACCEL_PAD/REACCEL_BARS/MIN_SL_W)と _fetch_bars(メーター用)

REAL_FORBIDDEN = 27972608
MAGIC = 909090                   # 肥料レーン専用マジック(運用と混ざらない)
RISK_FRAC = 0.02                 # 肥料=攻め(2%/trade・会長)。実弾ハイレバは別途GO。
MAX_CONCURRENT = 0               # 同時ポジ上限。0=無制限(会長2026-10-22 A)。将来ゼロカット率で絞るつまみ。
BARS = 80                        # ブローカーM5確定足の取得本数(リテスト窓≤24本に十分)
PRICE_EPS = 0.02                 # 逆指値/SL の変更を発注し直す閾値(ドル)。微小差で連打しない。
NOTIFY = False

# runtime(done集合)は git同期の外へ=消失/巻き戻しに強い。MT5Fert端末の隣に置く。
def _runtime_dir():
    env = load_env(ENVF)
    term = env.get("FERT_TERMINAL", "")
    base = os.path.dirname(term) if term else HERE
    d = os.path.join(base, "fert_reaccel_runtime")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        d = HERE
    return d


def load_env(path):
    env = {}
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1); env[k.strip()] = v.strip()
    return env


def _done_path():
    return os.path.join(_runtime_dir(), "fert_done.json")


def load_done():
    p = _done_path()
    if os.path.exists(p):
        try:
            return set(json.load(open(p, encoding="utf-8")))
        except Exception:
            pass
    return set()


def save_done(s):
    try:
        json.dump(sorted(s), open(_done_path(), "w", encoding="utf-8"))
    except Exception as e:
        print("done保存失敗:", e)


def _log(rec):
    rec.setdefault("ts", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"))
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _gold_er(win=288, th=0.12):
    """約定に貼る相場メーター(ER)。予想でなく記録ラベル(旬の炙り出し用)・発注判定には不使用。"""
    try:
        import numpy as np
        m5 = se._fetch_bars()
        if m5 is None or len(m5) < win + 2:
            return None, None
        c = m5["close"].to_numpy()[-win:]
        path = float(np.abs(np.diff(c)).sum())
        er = abs(float(c[-1]) - float(c[0])) / path if path > 0 else 0.0
        return round(er, 4), ("chop" if er < th else "trend")
    except Exception:
        return None, None


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
        if int(ai.login) != self.login:
            self.mt5.shutdown(); raise RuntimeError("[%s] 接続口座%s≠肥料%s→緊急停止(誤口座防止)" % (when, ai.login, self.login))
        if int(getattr(ai, "trade_mode", -1)) != 0:
            raise RuntimeError("[%s] trade_mode非DEMO→中止" % when)
        return ai

    def bars(self, n=BARS):
        mt5 = self.mt5
        r = mt5.copy_rates_from_pos(self.sym, mt5.TIMEFRAME_M5, 0, n)
        if r is None or len(r) < 5:
            return None
        df = pd.DataFrame(r)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.set_index("time")[["open", "high", "low", "close"]]
        return df.iloc[:-1]      # 形成中の最新足は落とす(確定足のみ)

    def tick(self):
        return self.mt5.symbol_info_tick(self.sym)

    def lot_for(self, entry, sl):
        mt5 = self.mt5
        ai = mt5.account_info(); si = mt5.symbol_info(self.sym)
        try:
            rp = abs(float(entry) - float(sl))
            vpp = si.trade_tick_value / si.trade_tick_size
            if rp <= 0 or vpp <= 0:
                return float(si.volume_min or 0.01)
            lot = (ai.balance * RISK_FRAC) / (rp * vpp)
            step = si.volume_step or 0.01
            lot = max(si.volume_min or 0.01, round(lot / step) * step)
            return float(min(lot, si.volume_max or lot))
        except Exception:
            return float(getattr(si, "volume_min", 0.01) or 0.01)

    def stops_level(self):
        si = self.mt5.symbol_info(self.sym)
        pt = getattr(si, "point", 0.01) or 0.01
        lvl = getattr(si, "trade_stops_level", 0) or 0
        return lvl * pt

    # ---- pending-order 操作(すべて assert_demo を直前に通す) ----
    def pending_by_sid(self):
        orders = self.mt5.orders_get(symbol=self.sym) or []
        out = {}
        for o in orders:
            if int(o.magic) != MAGIC:
                continue
            sid = (o.comment or "").replace("fert-", "")
            if sid:
                out[sid] = o
        return out

    def positions_by_sid(self):
        ps = self.mt5.positions_get(symbol=self.sym) or []
        out = {}
        for p in ps:
            if int(p.magic) != MAGIC:
                continue
            sid = (p.comment or "").replace("fert-", "")
            if sid:
                out[sid] = p
        return out

    def place_stop(self, side, lot, price, sl, tp, comment):
        mt5 = self.mt5
        self.assert_demo("逆指値発注直前")
        mt5.symbol_select(self.sym, True)
        otype = mt5.ORDER_TYPE_SELL_STOP if side == "SELL" else mt5.ORDER_TYPE_BUY_STOP
        r = None
        for filling in (mt5.ORDER_FILLING_RETURN, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK):
            req = {"action": mt5.TRADE_ACTION_PENDING, "symbol": self.sym, "volume": float(lot),
                   "type": otype, "price": float(price), "sl": float(sl), "tp": float(tp),
                   "magic": MAGIC, "comment": comment, "type_time": mt5.ORDER_TIME_GTC,
                   "type_filling": filling}
            r = mt5.order_send(req)
            if r is None:
                continue
            if r.retcode == mt5.TRADE_RETCODE_DONE:
                return r
            if r.retcode not in (mt5.TRADE_RETCODE_INVALID_FILL,):
                return r
        return r

    def modify_stop(self, ticket, price, sl, tp):
        mt5 = self.mt5
        self.assert_demo("逆指値変更直前")
        req = {"action": mt5.TRADE_ACTION_MODIFY, "order": int(ticket), "price": float(price),
               "sl": float(sl), "tp": float(tp), "type_time": mt5.ORDER_TIME_GTC}
        return mt5.order_send(req)

    def cancel(self, ticket):
        mt5 = self.mt5
        self.assert_demo("取消直前")
        req = {"action": mt5.TRADE_ACTION_REMOVE, "order": int(ticket)}
        return mt5.order_send(req)

    def shutdown(self):
        self.mt5.shutdown()


def reaccel_armed():
    """リテスト確定・トリガー待ちの窓(reaccel.status=='waiting' かつ retest_time有り)。lane3(外壁+中壁)全部・v1.keep。"""
    setups = dx.fold_setups()
    out = []
    for sid, s in setups.items():
        if s.get("lane") != "3":
            continue
        if not (s.get("v1") or {}).get("keep", False):
            continue
        blk = s.get("reaccel") or {}
        if blk.get("status") == "waiting" and blk.get("retest_time"):
            out.append({"sid": sid, "side": s.get("side"), "wall": s.get("wall"),
                        "wall_kind": s.get("wall_kind"), "sl_base": float(s.get("sl")),
                        "tp": float(s.get("tp")), "retest_time": int(blk["retest_time"])})
    return out


def compute_arm(sess, a):
    """ブローカー(806809)のM5確定足から逆指値パラメータを算出(紙 _reaccel_from と同式)。
       trig=直前足の極値 / ext=リテスト足〜最新確定足の極値 / sl=max(sl_base,ext±PAD)→最小SL幅フロア。
       崩壊(最新確定足の終値がsl_baseの外)なら collapse=True。"""
    m5 = sess.bars(BARS)
    if m5 is None or len(m5) < 2:
        return None
    sell = (a["side"] == "SELL")
    # ★ブローカー(Vantage)のM5足時刻はサーバTZ(実測UTC+3)で、信号(8793=UTC)とズレる。
    #   retest_time(信号UTC)をブローカー時間基準へ整数時間オフセットで合わせてから窓を切る。
    #   (2026-10-23: このズレでS-0323のextが3h前の高値を拾いSL過大化=初約定のバグ源)。
    rt = pd.to_datetime(a["retest_time"], unit="s", utc=True)
    try:
        feed = se._fetch_bars()
        off_h = round((m5.index[-1] - feed.index[-1]).total_seconds() / 3600.0)
        rt = rt + pd.Timedelta(hours=off_h)
    except Exception:
        pass
    seg = m5[m5.index >= rt]
    # 保険: reaccel窓はリテスト→トリガーで最大~12本。異常に広い窓は時刻ズレの兆候=末尾30本に制限。
    if len(seg) > 30:
        seg = seg.iloc[-30:]
    if len(seg) < 1:
        seg = m5.iloc[-1:]
    last = m5.iloc[-1]
    lc = float(last["close"])
    sl_base = a["sl_base"]; tp = a["tp"]
    # 崩壊: 最新確定足の終値が既存SL(構造)の外
    if (sell and lc >= sl_base) or ((not sell) and lc <= sl_base):
        return {"collapse": True}
    ext = float(seg["high"].max()) if sell else float(seg["low"].min())
    trig = float(last["low"]) if sell else float(last["high"])
    pad = se.REACCEL_PAD; minw = getattr(se, "MIN_SL_W", 3.0)
    sl = max(sl_base, ext + pad) if sell else min(sl_base, ext - pad)
    sl = max(sl, trig + minw) if sell else min(sl, trig - minw)
    entry = trig
    ok = (sl > entry > tp) if sell else (tp > entry > sl)
    if not ok:
        return None
    return {"entry": round(entry, 3), "sl": round(sl, 3), "tp": round(tp, 3),
            "ext": round(ext, 3), "collapse": False}


def scan_once(sess, armed_flag, observe):
    if os.path.exists(KILL):
        print("[KILL_FERT] 停止"); return True
    armed = reaccel_armed()
    armed_sids = {a["sid"] for a in armed}
    pend = sess.pending_by_sid()
    posn = sess.positions_by_sid()
    done = load_done()
    stops = sess.stops_level()

    # 1) 新規約定の検知(pending→建玉): done記録+台帳(メーター貼付)
    for sid, p in posn.items():
        if sid not in done:
            ger, greg = _gold_er()
            _log({"event": "fill", "sid": sid, "side": ("SELL" if p.type == sess.mt5.POSITION_TYPE_SELL else "BUY"),
                  "fill_price": p.price_open, "sl": p.sl, "tp": p.tp, "volume": p.volume,
                  "position": p.ticket, "gold_er": ger, "gold_regime": greg})
            print("[約定検知] %s 建値%.2f lot%.2f pos%d" % (sid, p.price_open, p.volume, p.ticket))
            done.add(sid); save_done(done)

    # 2) armed を処理: 置く / 追従変更
    for a in armed:
        sid = a["sid"]
        if sid in posn or sid in done:
            continue                       # 既に約定/決着
        arm = compute_arm(sess, a)
        if arm is None:
            continue
        if arm.get("collapse"):
            if sid in pend:
                r = sess.cancel(pend[sid].ticket) if not observe else None
                _log({"event": "cancel", "sid": sid, "why": "床崩壊(終値が構造の外)",
                      "retcode": getattr(r, "retcode", None), "observe": observe})
                print("[取消・崩壊] %s" % sid)
            continue
        side = a["side"]; sell = (side == "SELL")
        t = sess.tick()
        if t is None:
            continue
        # 逆指値の有効条件: SELL_STOPは現値(bid)より下・BUY_STOPは現値(ask)より上。stops_levelぶん離す。
        if sell and arm["entry"] >= t.bid - stops:
            # 既に割り込み済み=クリーンな入りを逃した→追わない(飛び乗り禁止)。既存pendingは残す(次足で更新)。
            continue
        if (not sell) and arm["entry"] <= t.ask + stops:
            continue
        lot = sess.lot_for(arm["entry"], arm["sl"])
        comment = "fert-%s" % sid
        if sid in pend:
            o = pend[sid]
            if abs(float(o.price_open) - arm["entry"]) > PRICE_EPS or abs(float(o.sl) - arm["sl"]) > PRICE_EPS:
                if observe:
                    _log({"event": "would-modify", "sid": sid, "entry": arm["entry"], "sl": arm["sl"], "tp": arm["tp"], "lot": lot})
                    print("[観測・変更するはず] %s entry%.2f SL%.2f" % (sid, arm["entry"], arm["sl"]))
                else:
                    r = sess.modify_stop(o.ticket, arm["entry"], arm["sl"], arm["tp"])
                    _log({"event": "modify", "sid": sid, "order": o.ticket, "entry": arm["entry"],
                          "sl": arm["sl"], "tp": arm["tp"], "retcode": getattr(r, "retcode", None)})
                    print("[逆指値追従] %s entry%.2f SL%.2f ret=%s" % (sid, arm["entry"], arm["sl"], getattr(r, "retcode", None)))
        else:
            if MAX_CONCURRENT and len(posn) >= MAX_CONCURRENT:
                _log({"event": "skip-maxpos", "sid": sid}); continue
            if observe:
                ger, greg = _gold_er()
                _log({"event": "would-place", "sid": sid, "side": side, "wall_kind": a["wall_kind"],
                      "entry": arm["entry"], "sl": arm["sl"], "tp": arm["tp"], "lot": lot,
                      "gold_er": ger, "gold_regime": greg})
                print("[観測・置くはず] %s %s entry%.2f SL%.2f TP%.2f lot%.2f" % (sid, side, arm["entry"], arm["sl"], arm["tp"], lot))
            else:
                r = sess.place_stop(side, lot, arm["entry"], arm["sl"], arm["tp"], comment)
                ok = (r is not None and r.retcode == sess.mt5.TRADE_RETCODE_DONE)
                _log({"event": "place" if ok else "place-ng", "sid": sid, "side": side, "wall_kind": a["wall_kind"],
                      "entry": arm["entry"], "sl": arm["sl"], "tp": arm["tp"], "lot": lot,
                      "order": getattr(r, "order", None), "retcode": getattr(r, "retcode", None)})
                print("[逆指値設置%s] %s %s entry%.2f SL%.2f TP%.2f ret=%s" % (
                    "OK" if ok else "NG", sid, side, arm["entry"], arm["sl"], arm["tp"], getattr(r, "retcode", None)))

    # 3) もう armed でない pending = 窓切れ/無効 → 取消(約定済みは done で既に処理済)
    for sid, o in pend.items():
        if sid in armed_sids or sid in posn:
            continue
        if observe:
            _log({"event": "would-cancel", "sid": sid, "why": "窓切れ/非armed", "order": o.ticket})
            print("[観測・取消するはず] %s" % sid)
        else:
            r = sess.cancel(o.ticket)
            _log({"event": "cancel", "sid": sid, "why": "窓切れ/非armed", "order": o.ticket, "retcode": getattr(r, "retcode", None)})
            print("[取消・窓切れ] %s ret=%s" % (sid, getattr(r, "retcode", None)))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="MT5Fertに接続。無指定=説明のみ")
    ap.add_argument("--arm", default="", help="'FERT-GO'かつ--liveで初めて発注/変更/取消する(二重ロック)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", type=int, default=20, help="N秒おきにループ(既定20s)")
    args = ap.parse_args()
    armed_flag = (args.arm == "FERT-GO")
    observe = not armed_flag
    if not args.live:
        print("観測/発注には --live。発注はさらに --arm FERT-GO(二重ロック)。既定=何もしない。"); return
    # ★単一インスタンス保証(二重起動=同一sidに逆指値を二重に置く事故を防ぐ)。
    #   OSレベルのファイルロックを保持。別インスタンスが生きている間は起動しない。
    lock_fh = None
    try:
        import msvcrt
        lock_fh = open(os.path.join(_runtime_dir(), "fert_stop.lock"), "w")
        msvcrt.locking(lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print("別インスタンスが稼働中→起動中止(二重発注防止)"); return
    except Exception:
        pass   # ロック取得に失敗しても停止はしない(保険が無いだけ)
    env = load_env(ENVF)
    sess = FertSession(env)
    ai = sess.assert_demo("起動確認")
    print("[接続] 肥料reaccel(逆指値) %s / %s / 残高%s / %s  armed=%s risk%.1f%% runtime=%s" % (
        ai.login, ai.server, ai.balance, sess.sym, armed_flag, RISK_FRAC * 100, _runtime_dir()))
    print("[!!] LIVEデモ発注モード(逆指値を実際に置く/変える/消す)" if armed_flag else "[観測モード] 置くはず/変えるはず/消すはず を台帳に記録のみ・0円")
    try:
        while True:
            if scan_once(sess, armed_flag, observe) or args.once or args.loop <= 0:
                break
            time.sleep(args.loop)
    finally:
        sess.shutdown()
    print("[終了]")


if __name__ == "__main__":
    main()
