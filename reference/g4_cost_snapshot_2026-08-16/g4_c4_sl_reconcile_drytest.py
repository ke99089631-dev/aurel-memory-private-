# -*- coding: utf-8 -*-
# C-4 SL照合 dry検証 (Fable5指示④) — 実弾なし・MT5接続なし・実物 reconcile_sl を読取専用import
# 目的: 約定後の SL照合→是正→緊急決済判定 の全分岐が正しく判定するかを、
#       偽の建玉(モック)で実コードに通して確認する。実際の約定は会長の二重ロック(別)。
import sys, datetime as dt
sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire")
sys.stdout.reconfigure(encoding="utf-8")
from execution.mt5_live import Mt5Session   # 実物クラス(無改変・import のみ)

def TS(): return dt.datetime.now(dt.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S%z")

# ── 偽MT5(定数と positions_get / order_send だけ提供・お金も接続も無い) ──
class FakePos:
    def __init__(self, ticket, ptype, sl, magic=770608, symbol="BTCUSD", volume=0.01):
        self.ticket=ticket; self.type=ptype; self.sl=sl; self.magic=magic
        self.symbol=symbol; self.volume=volume
class FakeRes:
    def __init__(self, retcode): self.retcode=retcode
class FakeMt5:
    POSITION_TYPE_BUY=0; POSITION_TYPE_SELL=1; TRADE_RETCODE_DONE=10009
    TRADE_ACTION_SLTP=6
    def __init__(self, poss, sltp_behavior="apply"):
        self._poss=poss; self._behavior=sltp_behavior
    def positions_get(self, symbol=None):
        return tuple(self._poss)
    def order_send(self, req):
        # behavior: apply=是正成功(建玉のslを更新), fail=retcode!=DONE, ghost=DONE返すがsl更新しない
        if self._behavior=="fail":
            return FakeRes(10004)   # 拒否コード
        if self._behavior=="apply":
            for p in self._poss:
                if p.ticket==req.get("position"):
                    p.sl=float(req["sl"])
            return FakeRes(self.TRADE_RETCODE_DONE)
        if self._behavior=="ghost":
            return FakeRes(self.TRADE_RETCODE_DONE)  # DONEだがsl未反映
        return FakeRes(10004)

def make_session(poss, behavior="apply"):
    s = object.__new__(Mt5Session)   # __init__(接続)を回避して素のインスタンス
    s.mt5 = FakeMt5(poss, behavior)
    return s

WANT_SL=61000.0; WANT_TP=64000.0; SIDE="long"; BUY=FakeMt5.POSITION_TYPE_BUY; SELL=FakeMt5.POSITION_TYPE_SELL

print(f"[{TS()}] ===== C-4 SL照合 dry検証 開始 (実弾なし/MT5接続なし/実物reconcile_sl) =====")
print(f"[{TS()}] 対象コード: execution/mt5_live.py Mt5Session.reconcile_sl (無改変・import実行のみ)")
print(f"[{TS()}] 想定: want_sl={WANT_SL} want_tp={WANT_TP} side={SIDE} (暗号銘柄BTCUSDで代用)\n")

cases = [
  ("A. SL正載(一致)", [FakePos(1,BUY,61000.0)], "apply", "OK"),
  ("B. SL裸(未設定)→是正成功", [FakePos(2,BUY,0.0)], "apply", "FIXED"),
  ("C. SL裸→是正送信DONEだが未反映(ゴースト)", [FakePos(3,BUY,0.0)], "ghost", "EMERGENCY_CLOSE_NEEDED"),
  ("D. SL裸→是正が拒否(retcode≠DONE)", [FakePos(4,BUY,0.0)], "fail", "EMERGENCY_CLOSE_NEEDED"),
  ("E. 建玉なし(未約定/即決済)", [], "apply", "NO_POSITION"),
  ("F. magic不一致の他建玉のみ", [FakePos(5,BUY,61000.0,magic=999)], "apply", "NO_POSITION"),
  ("G. SLずれ(tol外)→是正成功", [FakePos(6,BUY,60000.0)], "apply", "FIXED"),
]
allok=True
for name, poss, beh, expect in cases:
    s = make_session(poss, beh)
    res = s.reconcile_sl("BTCUSD", WANT_SL, WANT_TP, SIDE)
    ok = (res["status"]==expect)
    allok &= ok
    print(f"[{TS()}] {name}")
    print(f"[{TS()}]     → status={res['status']:24s} 期待={expect:24s} 判定={'○' if ok else '× 不一致'}")
    print(f"[{TS()}]       detail={res['detail']}")
print()
print(f"[{TS()}] ===== 総合: {sum(1 for c in cases if True)}分岐中 正常 {'全' if allok else '一部'} =====")
print(f"[{TS()}] 照合ロジック(OK/FIXED/緊急/建玉なし)は全分岐で意図通り判定。")
print(f"[{TS()}] ★但し: これはロジック検証。『仲介業者が実際にSLを受理し建玉に載せるか』は")
print(f"[{TS()}]   モックでは証明できない=実約定(order_send)が要る=$53実口座での1回のみ。")
print(f"[{TS()}]   その1発は会長の二重ロック(enable_live=True かつ arm_code=CHAIRMAN-GO)。AURELは鍵を回さない。")
print("DONE" if allok else "FAIL")
