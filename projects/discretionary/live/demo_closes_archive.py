# -*- coding: utf-8 -*-
"""金デモ(touch2sb/旧reaccel)の決済を追記専用で保全する。読取のみ+新規ファイルへの追記のみ。
  発注しない・既存台帳を書き換えない・MT5に触らない(demo_positions.json を読むだけ)。

なぜ必要か(2026-11-28 発見):
  demo_exec.py の kind:close は「自分が成行で閉じた時間切れ(TIME)」しか書かない。
  SL/TP はサーバ側で発動するので執行機は気づかず、追記台帳に1行も残らない。
  唯一の保管先 demo_positions.json は毎スキャンの**上書き**で、しかも
    demo_exec.py:306  history_deals_get(now-45日, ...)
    demo_exec.py:331  "closed": closed[-100:]
  つまり **45日を過ぎた決済は静かに消える**。TIME勝ちだけが永久に残る =
  時間が経つほど勝ちだけが残る構造(生存者バイアスが自動で育つ)。

実際の歪み(2026-11-28時点):
  追記台帳だけ: 3本・全部TIME・全勝 +101.23 USD
  真値(demo_positions): 10本・TP4/TIME3/SL3・7勝3敗 +251.26 USD
  → 金額は過小だが「負けの存在」と「勝率」が消える。

使い方: 定期的に実行するだけ(重複は position_id で弾く)。出力 demo_closes_archive.jsonl
"""
import os, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "demo_positions.json")
OUT = os.path.join(HERE, "demo_closes_archive.jsonl")


def existing_ids():
    ids = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(str(json.loads(line).get("position_id")))
            except Exception:
                continue
    return ids


def main():
    try:
        pos = json.load(open(SRC, encoding="utf-8"))
    except Exception as e:
        print("demo_positions.json が読めない: %s" % e)
        return
    have = existing_ids()
    closed = pos.get("closed") or []
    added = 0
    with open(OUT, "a", encoding="utf-8") as f:
        for c in closed:
            pid = str(c.get("position_id"))
            if pid in have:
                continue
            rec = dict(c)
            rec["archived_at"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rec["src"] = "demo_positions.json"
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            have.add(pid); added += 1
    total = len(existing_ids())
    print("保全: 新規%d件 / 累計%d件 → %s" % (added, total, os.path.basename(OUT)))
    # 保全済みの集計(真値)
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8") if l.strip()]
    for pre, lab in (("T2", "touch2sb"), ("S-", "旧reaccel")):
        xs = [r for r in rows if str(r.get("sid", "")).startswith(pre)]
        if xs:
            import collections
            p = sum(float(r.get("profit") or 0) for r in xs)
            w = sum(1 for r in xs if float(r.get("profit") or 0) > 0)
            print("  %-9s %2d本 %+8.2f USD 勝率%.0f%% 理由%s" % (
                lab, len(xs), p, 100 * w / len(xs), dict(collections.Counter(r.get("reason") for r in xs))))


if __name__ == "__main__":
    main()
