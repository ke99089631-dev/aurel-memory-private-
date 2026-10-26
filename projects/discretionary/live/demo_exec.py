#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUREL AIデモ執行（車線3の検証口）— MT5Demo(デモ口座)にだけ発注する。実弾は絶対に触らない。
================================================================================
役割: setup_engine が出すAIセットアップ(S系列)が「発火」した瞬間に、デモ口座へ
      SL/TP付きのブラケット成行をサーバー側に載せ、実執行コスト(スプレッド/滑り/約定)
      込みで優位性を検証する。コックピット(リアル読取)とは別プロセスで並走する。

★多重安全（不変）:
  1) 接続先は MT5Demo 固定。発注する関数を呼ぶ「毎回」直前に account_info を読み、
     login != 27972608(リアル) かつ trade_mode == DEMO(0) を再検証。1つでも崩れたら発注中止。
  2) 二重ロック: 実際に order_send するには --live かつ --arm CHAIRMAN-GO の両方が必要。
     既定は DRY-RUN（何を出すかをログするだけ・1円も動かさない）。
  3) キルスイッチ: 同フォルダに KILL ファイルがあれば即停止（発注しない）。
  4) デモでも「初回の実発注は会長GO後」。このスクリプトを --live で回すのが会長GOの実体。
  5) 発注はデモのみ=実弾出金機能なし。リアル(27972608)にはログインすらしない。
使い方:
  python demo_exec.py --dry            # 既定。発火検知と「出す内容」を表示するだけ
  python demo_exec.py --dry --once     # 1回だけスキャン
  python demo_exec.py --live --arm CHAIRMAN-GO   # 実デモ発注（会長GOの実体）
"""
import os, sys, json, time, argparse, datetime

# ★出力の文字コードで絶対に落ちないように（cp932コンソール/リダイレクトでもUTF-8・置換）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SETUP_LEDGER = os.path.join(HERE, "setup_ledger.jsonl")
T2SB_LEDGER = os.path.join(HERE, "touch2sb_ledger.jsonl")   # ★本命touch2sbの発火（setup_engineが書く・素の高安箱）
EXEC_LEDGER = os.path.join(HERE, "demo_exec_ledger.jsonl")
STATE = os.path.join(HERE, "demo_exec_state.json")
POS_SNAPSHOT = os.path.join(HERE, "demo_positions.json")   # ★2026-10-26: デモ建玉/決着のスナップショット(読取のみ・チャート表示用)
KILL = os.path.join(HERE, "KILL")
ENV_PATH = os.path.join(os.path.expanduser("~"), ".claude", ".env")

TERMINAL = r"C:\Users\user\MT5Demo\terminal64.exe"
REAL_FORBIDDEN = 27972608
SYMBOL = "XAUUSD"          # デモの金シンボル（リアルはXAUUSD+・デモはXAUUSD）
LOT = 0.01                 # デモ検証は最小ロット固定（会長の手トレードと同じ0.01）
MAGIC = 770613             # デモ執行の目印
POLL_SEC = 20
FRESH_SEC = 180            # ★2026-10-22 会長GO: 発火から3分以内だけ発注(旧600)。late fill退治=紙と実射の乖離源(S-0277で勝ち2/3消失)を断つ。
                           #   touch2sbは確認足直後に発火(生成30s+poll20s≈50s)なので180sで十分。古い発火は撃たない。
ARM = "CHAIRMAN-GO"

# ★発注対象の方針（会長GO 2026-10-13）: 会長の型と同じ「外壁×リテスト(reaccel)」だけ発注。
#   内壁(mid)・chaseは発注せず observe（記録のみ）＝後で比較用に紙で貯める。いつでも広げられる。
# ★2026-10-20 会長GO: 中壁(mid)を発注対象に追加。根拠=10-15に事前固定した基準
#   「中壁×再加速が確定30本でネット平均+0.3R以上」を10-20に到達(n=30・+0.32R)。
#   出口(事前固定)=デモで撃った中壁が30本に達した時点でネット平均<0なら "mid" を外す(この1行を戻す)。
#   v1フィルタ(雨・箱の締まり・時間帯)はそのまま掛かる＝撃つのは採用側だけ。chaseは引き続き observe。
# ★2026-10-21 会長GO: 中壁(mid)を発注対象から降格(=observeに戻す・記録は継続)。
#   根拠=時代別+勝つ出口で再検証(gold_midwall_era.py)→中壁は全時代マイナス(近年も-0.69R・勝率24%)。
#   昇格根拠だった「30本+0.32R」は余計な年+好窓の数字と判明。30本待たず降格(14年regime検証が優先)。
#   中壁は FIRE_WALL_KINDS から外れても setup は記録される=observeで紙を貯め続ける。
# ★2026-10-21 会長GO: デモの発火エンジンを「本命 touch2sb(素の高安箱・保ち2回・会長フィルタ・TP手前0.85)」に切替。
#   根拠=時代別+忠実性検証で touch2sb=金近年+0.188R Sharpe1.0 p0.03。dynamic_box版reaccel(+0.046/近年)より本命が強い。
#   旧reaccelは発注停止(FIRE_MODES空)=setup_ledgerに記録は残り observe(対照群)として並走。
#   出口(事前固定)=デモ touch2sb が確定30本に達した時点でネット平均R<0 なら本切替を戻す(FIRE_ENGINE=reaccel)。
FIRE_ENGINE = "touch2sb"               # 発注の主系統（touch2sb=本命 / reaccel=旧・観測のみ）
FIRE_WALL_KINDS = ("outer",)           # (旧reaccel用)発注してよい壁種別。FIRE_MODES空なので実質observe
FIRE_MODES = ()                        # ★旧reaccelは発注停止(observe継続)。本命は touch2sb_ledger から撃つ


def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        for ln in open(ENV_PATH, encoding="utf-8"):
            if "=" in ln and not ln.strip().startswith("#"):
                k, v = ln.split("=", 1); env[k.strip()] = v.strip()
    return env


def log_exec(rec):
    rec["logged_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(EXEC_LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {"seen": [], "initialized": False}


def save_state(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False)


def fold_setups():
    """setup_ledger を畳んで S-id ごとの最新状態を返す。"""
    setups = {}
    if not os.path.exists(SETUP_LEDGER):
        return setups
    for ln in open(SETUP_LEDGER, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if r.get("kind") == "setup":
            setups[r["id"]] = dict(r)
        elif r.get("kind") == "update":
            sid = r.get("target")
            if sid in setups:
                # update が持つ reaccel/chase を上書き反映
                for key in ("reaccel", "chase", "status"):
                    if key in r:
                        setups[sid][key] = r[key]
    return setups


def fired_setups(setups):
    """発火＝reaccel.status=='open'（entry/sl/tp確定）かつ v1.keep。発火時刻も返す。"""
    out = []
    for sid, s in setups.items():
        if s.get("lane") != "3":
            continue
        v1 = s.get("v1") or {}
        if not v1.get("keep", False):
            continue
        for mode in ("reaccel", "chase"):
            blk = s.get(mode) or {}
            if blk.get("status") == "open" and blk.get("entry") is not None \
                    and blk.get("sl") is not None and blk.get("tp") is not None:
                out.append({
                    "sid": sid, "mode": mode, "side": s.get("side"),
                    "entry": blk["entry"], "sl": blk["sl"], "tp": blk["tp"],
                    "entry_time": blk.get("entry_time") or s.get("break_time") or 0,
                    "wall": s.get("wall"), "wall_kind": s.get("wall_kind"),
                })
                break
    return out


def touch2sb_fires():
    """touch2sb_ledger の発火を読む（1行＝1発火）。sid は確認足tsで一意。
       発注対象は外壁×保ち2回×会長フィルタに限って setup_engine が既に絞り済み＝ここでは全件が発注候補。"""
    out = []
    if not os.path.exists(T2SB_LEDGER):
        return out
    for ln in open(T2SB_LEDGER, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if r.get("kind") != "touch2sb":
            continue
        ct = int(r.get("confirm_time") or 0)
        out.append({
            "sid": "T2-%d" % ct, "mode": "touch2sb", "side": r.get("side"),
            "entry": r.get("entry"), "sl": r.get("sl"), "tp": r.get("tp"),
            "entry_time": r.get("entry_time") or ct, "wall": r.get("wall"),
            "wall_kind": "outer_sb", "risk": r.get("risk"), "jst": r.get("jst"),
        })
    return out


# ── MT5デモ接続（発注直前の毎回検証つき）──────────────────────────────
class DemoSession:
    def __init__(self):
        import MetaTrader5 as mt5
        self.mt5 = mt5
        env = load_env()
        login = int(env.get("DEMO_LOGIN", "0"))
        if login == REAL_FORBIDDEN or login == 0:
            raise RuntimeError("DEMO_LOGIN が不正(リアルor未設定)。中止。")
        ok = mt5.initialize(path=TERMINAL, login=login,
                            password=env.get("DEMO_PASSWORD", ""),
                            server=env.get("DEMO_SERVER", ""), portable=True)
        if not ok:
            raise RuntimeError("MT5Demo initialize失敗: %s" % (mt5.last_error(),))
        self.assert_demo("接続直後")

    def assert_demo(self, when):
        """★発注する毎回これを通す。デモ以外・リアルなら例外で発注を止める。"""
        ai = self.mt5.account_info()
        if ai is None:
            raise RuntimeError("[%s] account_info取得不可→発注中止" % when)
        if int(ai.login) == REAL_FORBIDDEN:
            raise RuntimeError("[%s] ⛔リアル口座(27972608)に繋がっている→発注中止" % when)
        if ai.trade_mode != self.mt5.ACCOUNT_TRADE_MODE_DEMO:
            raise RuntimeError("[%s] ⛔デモ口座ではない(trade_mode=%s)→発注中止" % (when, ai.trade_mode))
        return ai

    def open_magic_positions(self):
        """このエンジンのデモ建玉数（MAGIC一致）。read-only（positions_get）。非重複ガード用。"""
        self.assert_demo("建玉確認")
        ps = self.mt5.positions_get(symbol=SYMBOL)
        if ps is None:
            return 0
        return sum(1 for p in ps if int(p.magic) == MAGIC)

    def bracket(self, side, lot, sl, tp, comment):
        """SL/TPを成行と同じorder_sendでサーバー側に載せる（約定と同時に床が立つ）。"""
        mt5 = self.mt5
        self.assert_demo("発注直前")           # ★毎回再検証
        mt5.symbol_select(SYMBOL, True)
        t = mt5.symbol_info_tick(SYMBOL)
        price = t.ask if side == "BUY" else t.bid
        otype = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
        r = None
        for filling in (mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN):
            req = {"action": mt5.TRADE_ACTION_DEAL, "symbol": SYMBOL,
                   "volume": float(lot), "type": otype, "price": price,
                   "sl": float(sl), "tp": float(tp), "deviation": 20,
                   "magic": MAGIC, "comment": comment,
                   "type_time": mt5.ORDER_TIME_GTC, "type_filling": filling}
            r = mt5.order_send(req)
            if r is None:
                continue
            if r.retcode == mt5.TRADE_RETCODE_DONE:
                return r
            if r.retcode not in (mt5.TRADE_RETCODE_INVALID_FILL,):
                return r
        return r

    def snapshot(self, path, days=14):
        """★2026-10-26 会長GO: デモ建玉と決着を read-only で書き出す(コックピット表示用)。
           positions_get / history_deals_get のみ・発注系は呼ばない。MT5の時刻はサーバ時刻(GMT+3)なので真UTCへ-3h補正。"""
        mt5 = self.mt5
        OFF = 3 * 3600
        now = time.time()
        opens = []
        ps = mt5.positions_get(symbol=SYMBOL) or []
        for p in ps:
            if int(p.magic) != MAGIC:
                continue
            opens.append({"ticket": int(p.ticket), "comment": p.comment, "sid": p.comment.replace("ai-demo-", ""),
                          "side": "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL",
                          "entry": float(p.price_open), "sl": float(p.sl), "tp": float(p.tp),
                          "lot": float(p.volume), "profit": float(p.profit), "swap": float(p.swap),
                          "time": int(p.time) - OFF})
        closed = []
        try:
            import datetime as _dt
            deals = mt5.history_deals_get(_dt.datetime.utcfromtimestamp(now - days * 86400 + OFF),
                                          _dt.datetime.utcfromtimestamp(now + 86400 + OFF)) or []
            by_pos = {}
            for d in deals:
                if int(d.magic) != MAGIC or d.symbol != SYMBOL:
                    continue
                g = by_pos.setdefault(int(d.position_id), {"in": None, "out": None})
                if d.entry == mt5.DEAL_ENTRY_IN:
                    g["in"] = d
                elif d.entry in (mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_INOUT, mt5.DEAL_ENTRY_OUT_BY):
                    g["out"] = d
            for pid, g in by_pos.items():
                i, o = g["in"], g["out"]
                if i is None or o is None:
                    continue
                closed.append({"ticket": pid, "comment": i.comment, "sid": i.comment.replace("ai-demo-", ""),
                               "side": "BUY" if i.type == mt5.DEAL_TYPE_BUY else "SELL",
                               "entry": float(i.price), "exit": float(o.price),
                               "profit": float(o.profit), "swap": float(o.swap), "commission": float(o.commission),
                               "time": int(i.time) - OFF, "exit_time": int(o.time) - OFF,
                               "exit_reason": ("TP" if "tp" in (o.comment or "").lower() else
                                               "SL" if "sl" in (o.comment or "").lower() else "manual")})
        except Exception as e:
            closed = [{"error": repr(e)}]
        snap = {"ts": int(now), "login": int(self.mt5.account_info().login), "open": opens, "closed": closed}
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False)
        os.replace(tmp, path)

    def snapshot(self):
        """★読取専用: このエンジン(MAGIC)のデモ建玉と直近45日の決着を demo_positions.json に書く。
           コックピット(serve_chart 8793)がこれを読んで2タッチ型の建玉・決着をチャートに描く。
           positions_get / history_deals_get のみ。発注系APIは使わない。失敗しても発注ループには影響させない(呼び側でtry)。"""
        mt5 = self.mt5
        ai = self.assert_demo("スナップショット")
        off = SERVER_UTC_OFFSET_S
        buy_pos = getattr(mt5, "POSITION_TYPE_BUY", 0)
        opens = []
        for p in (mt5.positions_get(symbol=SYMBOL) or []):
            if int(p.magic) != MAGIC:
                continue
            opens.append({"ticket": int(p.ticket), "sid": (p.comment or "").replace("ai-demo-", ""),
                          "side": "BUY" if int(p.type) == buy_pos else "SELL",
                          "entry": float(p.price_open), "sl": float(p.sl), "tp": float(p.tp),
                          "time_open": int(p.time) - off, "profit": float(p.profit),
                          "volume": float(p.volume), "price_now": float(p.price_current)})
        d_in = getattr(mt5, "DEAL_ENTRY_IN", 0)
        d_out = (getattr(mt5, "DEAL_ENTRY_OUT", 1), getattr(mt5, "DEAL_ENTRY_INOUT", 2), getattr(mt5, "DEAL_ENTRY_OUT_BY", 3))
        r_sl = getattr(mt5, "DEAL_REASON_SL", 4); r_tp = getattr(mt5, "DEAL_REASON_TP", 5)
        buy_deal = getattr(mt5, "DEAL_TYPE_BUY", 0)
        now = datetime.datetime.now()
        deals = mt5.history_deals_get(now - datetime.timedelta(days=45), now + datetime.timedelta(days=2)) or []
        by_pos = {}
        for d in deals:
            if int(d.magic) != MAGIC or d.symbol != SYMBOL:
                continue
            slot = by_pos.setdefault(int(d.position_id), {})
            if int(d.entry) == d_in:
                slot["in"] = d
            elif int(d.entry) in d_out:
                slot["out"] = d
        closed = []
        for pid, io in by_pos.items():
            i = io.get("in"); o = io.get("out")
            if i is None or o is None:
                continue
            reason = "TP" if int(o.reason) == r_tp else ("SL" if int(o.reason) == r_sl else "manual")
            closed.append({"position_id": pid, "sid": (i.comment or "").replace("ai-demo-", ""),
                           "side": "BUY" if int(i.type) == buy_deal else "SELL",
                           "entry": float(i.price), "exit": float(o.price),
                           "time_open": int(i.time) - off, "time_close": int(o.time) - off,
                           "profit": round(float(o.profit) + float(o.swap) + float(o.commission) + float(i.commission), 2),
                           "reason": reason})
        closed.sort(key=lambda x: x["time_close"])
        snap = {"ts": int(time.time()), "login": int(ai.login), "balance": float(ai.balance),
                "equity": float(ai.equity), "tz_offset_s": off, "open": opens, "closed": closed[-100:]}
        tmp = POS_SNAPSHOT + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False)
        os.replace(tmp, POS_SNAPSHOT)
        return snap

    def shutdown(self):
        self.mt5.shutdown()


def run(dry=True, armed=False, once=False):
    if dry:
        print("[モード] DRY-RUN（発注しない・出す内容を表示するだけ）")
    else:
        print("[モード] LIVE デモ発注（armed=%s）" % armed)
    state = load_state()
    sess = None
    if not dry:
        sess = DemoSession()
        ai = sess.assert_demo("起動")
        print("[接続] デモ %s / %s / 残高%s 検証OK" % (ai.login, ai.server, ai.balance))

    def one_scan():
        if os.path.exists(KILL):
            print("[KILL] キルスイッチ検知→発注せず停止")
            return False
        if sess is not None:
            try:
                sess.snapshot()          # 読取のみ。失敗は発注ループに影響させない
            except Exception as e:
                print("[snapshot error・継続] %r" % e, flush=True)
        setups = fold_setups()
        fires = fired_setups(setups)
        if FIRE_ENGINE == "touch2sb":
            fires = fires + touch2sb_fires()      # 本命touch2sbの発火を発注候補に合流（旧reaccelはFIRE_MODES空でobserve）
        now = time.time()
        # 初回は既存の発火を全部「既見」にして、以降の新規発火だけ扱う
        if not state.get("initialized"):
            state["seen"] = sorted({f["sid"] for f in fires})
            state["initialized"] = True
            save_state(state)
            print("[初期化] 既存の発火 %d 件を既見登録（過去分は発注しない）" % len(state["seen"]))
            return True
        seen = set(state.get("seen", []))
        for f in fires:
            if f["sid"] in seen:
                continue
            fresh = (now - float(f["entry_time"])) <= FRESH_SEC if f["entry_time"] else False
            tag = "新規発火"
            if not fresh:
                print("[skip] %s %s（発火が古い>%ds・バックフィル防止）" % (f["sid"], f["side"], FRESH_SEC))
                seen.add(f["sid"]); continue
            # ★方針フィルタ: 本命 touch2sb は発注。旧reaccel等は observe（FIRE_MODES空＝記録のみ）。
            do_fire = (f["mode"] == "touch2sb") or \
                      ((f["wall_kind"] in FIRE_WALL_KINDS) and (f["mode"] in FIRE_MODES))
            if not do_fire:
                print("[observe・発注せず記録のみ] %s %s %s(%s) SL%.3f TP%.3f"
                      % (f["sid"], f["side"], f["wall_kind"], f["mode"], f["sl"], f["tp"]))
                log_exec({"kind": "observe", "sid": f["sid"], "side": f["side"],
                          "wall_kind": f["wall_kind"], "mode": f["mode"],
                          "sl": f["sl"], "tp": f["tp"], "entry_ref": f["entry"]})
                seen.add(f["sid"]); continue
            # ★非重複ガード(touch2sb): 既にデモ建玉があれば今回の発火は撃たない＝backtest(+0.188)の「同時1本」に合わせる。
            if f["mode"] == "touch2sb" and not dry and armed and sess is not None:
                try:
                    if sess.open_magic_positions() > 0:
                        print("[observe・建玉中につき撃たず] %s %s SL%.3f TP%.3f" % (f["sid"], f["side"], f["sl"], f["tp"]))
                        log_exec({"kind": "observe", "sid": f["sid"], "side": f["side"],
                                  "wall_kind": f["wall_kind"], "mode": f["mode"],
                                  "sl": f["sl"], "tp": f["tp"], "entry_ref": f["entry"], "why": "建玉中(非重複)"})
                        seen.add(f["sid"]); continue
                except Exception as e:
                    print("[建玉確認エラー・安全側で撃たず] %s %r" % (f["sid"], e))
                    seen.add(f["sid"]); continue
            line = ("%s %s %s %s(%s) lot%.2f SL%.3f TP%.3f (entry≈%.3f wall%.3f)"
                    % (tag, f["sid"], f["side"], f["wall_kind"], f["mode"], LOT,
                       f["sl"], f["tp"], f["entry"], f["wall"] or 0))
            if dry:
                print("[DRY→出す] " + line)
                log_exec({"kind": "dry", "sid": f["sid"], "side": f["side"],
                          "lot": LOT, "sl": f["sl"], "tp": f["tp"], "entry_ref": f["entry"]})
            elif not armed:
                print("[未武装のため出さない] " + line + "  （--arm CHAIRMAN-GO が必要）")
            else:
                print("[LIVE→発注] " + line)
                r = sess.bracket(f["side"], LOT, f["sl"], f["tp"], "ai-demo-%s" % f["sid"])
                ok = (r is not None and r.retcode == sess.mt5.TRADE_RETCODE_DONE)
                rec = {"kind": "live", "sid": f["sid"], "side": f["side"], "lot": LOT,
                       "sl": f["sl"], "tp": f["tp"], "entry_ref": f["entry"],
                       "retcode": getattr(r, "retcode", None),
                       "deal": getattr(r, "deal", None), "order": getattr(r, "order", None),
                       "fill_price": getattr(r, "price", None), "ok": ok}
                log_exec(rec)
                print("   結果 ok=%s retcode=%s deal=%s" % (ok, rec["retcode"], rec["deal"]))
            seen.add(f["sid"])
        state["seen"] = sorted(seen)
        save_state(state)
        if sess is not None:
            try:
                sess.snapshot(POS_SNAPSHOT)      # 読取のみ・コックピットが建玉/決着を描く材料
            except Exception as e:
                print("[snapshot error・継続] %r" % e, flush=True)
        return True

    try:
        if once:
            one_scan()
        else:
            print("[起動] デモ執行 %d秒おき（Ctrl+C / KILLファイルで停止）" % POLL_SEC, flush=True)
            while True:
                try:
                    if not one_scan():
                        break
                except Exception as e:
                    print("[loop error・継続] %r" % e, flush=True)
                time.sleep(POLL_SEC)
    finally:
        if sess:
            sess.shutdown()


LOCK = os.path.join(HERE, "demo_exec.lock")

def acquire_lock():
    """単一インスタンス保証。既に生きているdemo_execがあれば起動しない（二重発注防止）。"""
    if os.path.exists(LOCK):
        try:
            old = int(open(LOCK).read().strip())
            # 同名プロセスが生きているか（tasklistで確認）
            import subprocess
            out = subprocess.run(["tasklist", "/fi", "PID eq %d" % old],
                                 capture_output=True, text=True).stdout
            if str(old) in out:
                print("既に起動中(pid %d)→二重起動を回避して終了" % old)
                return False
        except Exception:
            pass
    open(LOCK, "w").write(str(os.getpid()))
    return True

def main():
    if not acquire_lock():
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="実デモ発注（既定はDRY）")
    ap.add_argument("--dry", action="store_true", help="明示的にDRY-RUN（既定・no-op）")
    ap.add_argument("--arm", default="", help="二重ロック解除コード（CHAIRMAN-GO）")
    ap.add_argument("--once", action="store_true", help="1回だけスキャン")
    a = ap.parse_args()
    dry = not a.live
    armed = (a.arm == ARM)
    run(dry=dry, armed=armed, once=a.once)


if __name__ == "__main__":
    sys.exit(main())
