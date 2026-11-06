# -*- coding: utf-8 -*-
"""
ゾーン票を台帳に1件追記する(会長が会話で言った感覚を AUREL が代筆する時に使う)。
  python zone_vote.py 勝ち|負け|わからない ["会長の言葉(メモ)"] [--when 2026-11-06T09:30]
携帯フォームの「ゾーン」タブと同じ add_record() を通す=同じ ID 体系(Z-xxxx)・同じ LEDGER.md 描画。
成績には入らない観測欄。金ゼロ・読取/追記のみ・発注なし。
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\.aurel\phone")
import aurel_trade_room as tr

def main(argv):
    if not argv or argv[0] not in tr.ZONES:
        print("使い方: zone_vote.py 勝ち|負け|わからない [メモ] [--when YYYY-MM-DDTHH:MM]"); return 2
    zone, note, when = argv[0], "", ""
    rest = argv[1:]
    if "--when" in rest:
        i = rest.index("--when"); when = rest[i+1] if i+1 < len(rest) else ""; rest = rest[:i] + rest[i+2:]
    if rest:
        note = " ".join(rest)
    rec, line = tr.add_record({"kind": "zone", "zone": zone, "note": note, "when": when})
    print(line); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
