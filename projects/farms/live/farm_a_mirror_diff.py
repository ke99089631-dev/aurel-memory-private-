# -*- coding: utf-8 -*-
"""畑A: デモexec(806782) と 紙forward(観測) の差分トラッカー。読取のみ・発注しない。
会長2026-10-28 GO: デモの本数・成績を紙に一致させる物差し。肥料の mirror_diff.py と同趣旨。
join: exec.close.confirm_id == int(forward.entry_time - 300s)(確認足ts)。
出力: 本数(紙forward / exec約定) / exec約定本の1本ごとR差(exec-紙) / 合計R差 / exec理由内訳。
使い方: python farm_a_mirror_diff.py
"""
import os, json
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.join(HERE, "farm_a_exec_ledger.jsonl")
FWD = os.path.join(HERE, "farm_a_forward_ledger.jsonl")


def exec_closes():
    """confirm_id -> (R, reason) デモ約定の決着。"""
    out = {}
    for line in open(EXEC, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("mode") == "close" and d.get("confirm_id") and d.get("R") is not None:
            # exec.confirm_id はブローカー時刻(Vantage=UTC+3)。紙forwardは真UTC。3h=10800s引いて揃える。
            cid = int(d["confirm_id"]) - 10800
            out[str(cid)] = (float(d["R"]), d.get("reason"))
    return out


def fwd_closes():
    """confirm_id(=entry_time-300s) -> R 紙観測の決着。"""
    out = {}
    for line in open(FWD, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        et = d.get("entry_time"); r = d.get("R")
        if et is None or r is None: continue
        try:
            ts = int(datetime.fromisoformat(et.replace(" ", "T")).timestamp())
        except Exception:
            continue
        out[str(ts - 300)] = float(r)
    return out


def main():
    ex = exec_closes(); fw = fwd_closes()
    both = [c for c in ex if c in fw]
    only_fwd = [c for c in fw if c not in ex]
    print("=== 畑A 紙forward vs デモexec 差分 ===")
    print("本数: 紙forward %d / デモexec約定 %d / 両方 %d / 紙のみ(execは枠埋まり等で見送り) %d"
          % (len(fw), len(ex), len(both), len(only_fwd)))
    fwt = sum(fw.values()); ext = sum(r for r, _ in ex.values())
    print("合計R: 紙forward(全)%+.2f / デモexec(約定)%+.2f" % (fwt, ext))
    if both:
        print("\n-- 両方成立した本の1本ごとR差(exec−紙) --")
        diffs = []
        for c in sorted(both):
            er, rsn = ex[c]; fr = fw[c]; diff = er - fr
            diffs.append(abs(diff))
            flag = "" if abs(diff) < 0.1 else ("  <大ズレ" if abs(diff) >= 0.5 else "  <ズレ")
            print("  cid%s 紙%+.2f exec%+.2f 差%+.2f (%s)%s" % (c, fr, er, diff, rsn, flag))
        print("  |R差|平均 %.3f / 最大 %.3f" % (sum(diffs) / len(diffs), max(diffs)))
    if only_fwd:
        tot = sum(fw[c] for c in only_fwd)
        print("\n-- 紙は取ったがexecは見送り(同時2本枠/NY外/未約定)=本数差 n=%d 紙R合計%+.2f --" % (len(only_fwd), tot))


if __name__ == "__main__":
    main()
