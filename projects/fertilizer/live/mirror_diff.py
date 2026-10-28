# -*- coding: utf-8 -*-
"""紙(setup_ledger reaccel)とデモ(fert逆指値+成行)の差分トラッカー。読取のみ・発注しない。
会長2026-10-28 GO: 目的=デモの本数・成績を紙に一致させる。その"どれだけ寄ったか"を測る物差し。
出力: 本数差 / 取りこぼし本(紙は約定だがデモ未約定)とその紙R / 両約定本の1本ごとのR差 / 合計R差 / 入り方内訳。
使い方: python mirror_diff.py
"""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(os.path.dirname(os.path.dirname(HERE)), "discretionary", "live", "setup_ledger.jsonl")
FERT = os.path.join(HERE, "fert_reaccel_stop_ledger.jsonl")


def paper_reaccel():
    """lane3 reaccel の最終R・最終statusをsidごとに。"""
    R = {}; status = {}
    for line in open(PAPER, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        sid = d.get("id") or d.get("target")
        if not sid: continue
        ra = d.get("reaccel")
        if isinstance(ra, dict):
            if ra.get("status"): status[sid] = ra["status"]
            if ra.get("status") == "closed" and ra.get("R") is not None:
                R[sid] = float(ra["R"])
    return R, status


def demo_fills():
    """fert台帳: 約定(fill)と決着(close)のR・入り方をsidごとに。"""
    mode = {}; closeR = {}; filled = set(); cancelled = set()
    for line in open(FERT, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        sid = d.get("sid"); e = d.get("event")
        if e == "fill":
            filled.add(sid); mode[sid] = d.get("entry_mode", "stop")
        elif e == "close":
            if d.get("R") is not None: closeR[sid] = float(d["R"])
        elif e == "cancel":
            cancelled.add(sid)
    return filled, closeR, mode, cancelled


def main():
    pR, pst = paper_reaccel()
    filled, dR, mode, cancelled = demo_fills()
    seen = filled | cancelled
    # 紙が決着R(勝/負)を出し、かつ fert が触れた(置いた/約定/取消)universe
    universe = [sid for sid in pR if sid in seen]
    got = [sid for sid in universe if sid in filled]
    missed = [sid for sid in universe if sid not in filled]

    print("=== 紙 vs デモ 差分 (lane3 reaccel・紙が決着Rを出した本) n=%d ===" % len(universe))
    print("本数: 紙%d / デモ約定%d / 取りこぼし%d" % (len(universe), len(got), len(missed)))

    pot = sum(pR[s] for s in universe)
    dmt = sum(dR.get(s, 0.0) for s in got)
    print("合計R: 紙%+.2f / デモ(約定本のみ)%+.2f / 差%+.2f" % (pot, dmt, dmt - pot))
    mode_n = {}
    for s in got: mode_n[mode.get(s, "?")] = mode_n.get(mode.get(s, "?"), 0) + 1
    print("入り方内訳(約定本):", {k: v for k, v in sorted(mode_n.items())})

    print("\n-- 取りこぼし本(紙は約定・デモ未約定)=ここを減らすのが目標 --")
    if missed:
        for s in sorted(missed):
            print("  %s 紙R%+.2f (紙status=%s)" % (s, pR[s], pst.get(s)))
        print("  取りこぼし紙R合計 %+.2f" % sum(pR[s] for s in missed))
    else:
        print("  なし")

    print("\n-- 両方約定した本の1本ごとR差(デモ−紙) --")
    big = []
    for s in sorted(got):
        if s in dR:
            diff = dR[s] - pR[s]
            big.append(abs(diff))
            flag = "" if abs(diff) < 0.1 else ("  <大ズレ" if abs(diff) >= 0.5 else "  <ズレ")
            print("  %s 紙%+.2f デモ%+.2f 差%+.2f (%s)%s" % (s, pR[s], dR[s], diff, mode.get(s), flag))
    if big:
        print("  |R差|平均 %.3f / 最大 %.3f" % (sum(big) / len(big), max(big)))


if __name__ == "__main__":
    main()
