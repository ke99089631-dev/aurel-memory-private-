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
import os, sys, json, time, argparse

# ★出力の文字コードで絶対に落ちないように（cp932コンソール/リダイレクトでもUTF-8・置換）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SETUP_LEDGER = os.path.join(HERE, "setup_ledger.jsonl")
EXEC_LEDGER = os.path.join(HERE, "demo_exec_ledger.jsonl")
STATE = os.path.join(HERE, "demo_exec_state.json")
KILL = os.path.join(HERE, "KILL")
ENV_PATH = os.path.join(os.path.expanduser("~"), ".claude", ".env")

TERMINAL = r"C:\Users\user\MT5Demo\terminal64.exe"
REAL_FORBIDDEN = 27972608
SYMBOL = "XAUUSD"          # デモの金シンボル（リアルはXAUUSD+・デモはXAUUSD）
LOT = 0.01                 # デモ検証は最小ロット固定（会長の手トレードと同じ0.01）
MAGIC = 770613             # デモ執行の目印
POLL_SEC = 20
FRESH_SEC = 600            # 発火から10分以内のものだけ発注（起動時の過去分バックフィル防止）
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
FIRE_WALL_KINDS = ("outer",)           # 発注してよい壁種別(中壁は2026-10-21降格・observe継続)
FIRE_MODES = ("reaccel",)        # 発注してよい入り方（reaccel=リテスト引き寄せ）


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
        setups = fold_setups()
        fires = fired_setups(setups)
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
            # ★方針フィルタ: 外壁×reaccelだけ発注。それ以外は observe（記録のみ・発注しない）
            do_fire = (f["wall_kind"] in FIRE_WALL_KINDS) and (f["mode"] in FIRE_MODES)
            if not do_fire:
                print("[observe・発注せず記録のみ] %s %s %s(%s) SL%.3f TP%.3f"
                      % (f["sid"], f["side"], f["wall_kind"], f["mode"], f["sl"], f["tp"]))
                log_exec({"kind": "observe", "sid": f["sid"], "side": f["side"],
                          "wall_kind": f["wall_kind"], "mode": f["mode"],
                          "sl": f["sl"], "tp": f["tp"], "entry_ref": f["entry"]})
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
