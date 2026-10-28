# -*- coding: utf-8 -*-
"""畑A: デモexec(806782) と 紙双子(paper・同feed/同clock) の差分トラッカー。読取のみ・発注しない。
会長2026-10-28 GO: デモの本数・成績を紙に一致させる物差し。肥料の mirror_diff.py と同趣旨。
紙双子=farm_a_paper_ledger(execと同じブローカー足・同じ時計・同じ信号でtouch=約定を模擬)。cid直結でTZ補正不要。
join: exec.close.confirm_id == paper.cid。
出力: 本数(紙双子 / exec約定) / exec約定本の1本ごとR差(exec-紙) / 合計R差 / 紙のみ(枠埋まり見送り)。
使い方: python farm_a_mirror_diff.py
※ farm_a_forward(yfinance NQ=F・別フィード)は双子でないので比較に使わない(obs#24)。
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
EXEC = os.path.join(HERE, "farm_a_exec_ledger.jsonl")
FWD = os.path.join(HERE, "farm_a_paper_ledger.jsonl")


def exec_closes():
    """confirm_id -> (R, reason) デモ約定の決着。"""
    out = {}
    if not os.path.exists(EXEC):
        return out
    for line in open(EXEC, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("mode") == "close" and d.get("confirm_id") and d.get("R") is not None:
            out[str(d["confirm_id"])] = (float(d["R"]), d.get("reason"))
    return out


def fwd_closes():
    """cid -> R 紙双子(paper)の決着。execと同じブローカー時計cidなので補正不要。"""
    out = {}
    if not os.path.exists(FWD):
        return out
    for line in open(FWD, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("cid") and d.get("R") is not None:
            out[str(d["cid"])] = float(d["R"])
    return out


def main():
    ex = exec_closes(); fw = fwd_closes()
    both = [c for c in ex if c in fw]
    only_fwd = [c for c in fw if c not in ex]
    print("=== 畑A 紙双子(paper) vs デモexec 差分 ===")
    print("本数: 紙双子 %d / デモexec約定 %d / 両方 %d / 紙のみ(execは枠埋まり等で見送り) %d"
          % (len(fw), len(ex), len(both), len(only_fwd)))
    fwt = sum(fw.values()); ext = sum(r for r, _ in ex.values())
    print("合計R: 紙双子(全)%+.2f / デモexec(約定)%+.2f" % (fwt, ext))
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
