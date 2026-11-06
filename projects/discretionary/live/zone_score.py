# -*- coding: utf-8 -*-
"""
ゾーン票の採点(会長の感覚の予測力を測る)。読取のみ・発注なし。
  票(Z-xxxx・ledger.jsonl) ごとに「票の時刻から次の票まで(上限 HORIZON_H 時間)」を有効区間とし、
  その区間にブレイクした AI紙(再加速レーン・setup_ledger.jsonl・ネットR)の成績を 勝ち票/負け票/わからない で比べる。
  会長自身のトレード(T-xxxx)も同じ区間で並べる。
  事前固定(2026-11-06 v1): 有効区間=次の票まで・上限6時間 / 対照=票が無い時間帯の同レーン成績 / 判定は票30件以上で。
出力: live/zone_score.json(コックピット用) と標準出力の短い表。
"""
import json, os, sys, io, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, r"C:\Users\user\.aurel\phone")
import serve_chart as sc
import aurel_trade_room as tr

HORIZON_H = 6
OUT = os.path.join(HERE, "zone_score.json")
JST = dt.timezone(dt.timedelta(hours=9))

def jst_epoch(ts):
    return int(dt.datetime.fromisoformat(ts).replace(tzinfo=JST).timestamp())

def main():
    recs = tr.load_records()
    votes = sorted([r for r in recs if r.get("kind") == "zone"], key=lambda r: r["ts"])
    spans = []
    for i, v in enumerate(votes):
        t0 = jst_epoch(v["ts"])
        t1 = t0 + HORIZON_H * 3600
        if i + 1 < len(votes):
            t1 = min(t1, jst_epoch(votes[i+1]["ts"]))
        spans.append({"id": v["id"], "zone": v["zone"], "t0": t0, "t1": t1, "note": v.get("note") or ""})
    setups = sc._load_setups(); cm = sc._cost_model()
    ai = []
    for r in setups:
        ra = r.get("reaccel") if isinstance(r.get("reaccel"), dict) else None
        if not ra or ra.get("status") != "closed" or ra.get("R") is None:
            continue
        fake = {"R": ra["R"], "entry": ra.get("entry"), "sl": ra.get("sl"), "entry_time": ra.get("entry_time"),
                "jst_hour": r.get("jst_hour"), "exit_reason": ra.get("exit_reason")}
        ai.append({"id": r["id"], "bt": int(r.get("break_time") or 0), "R": sc._net_R(fake, cm)[0]})
    chair = [{"id": t["id"], "bt": jst_epoch(t["ts"]), "R": t["R"]} for t in tr.effective(recs)
             if t.get("R") is not None and not str(t.get("post") or "").startswith("未執行") and not t.get("exclude")]
    def agg(rows):
        n = len(rows); w = sum(1 for x in rows if x["R"] > 0); s = sum(x["R"] for x in rows)
        return {"n": n, "win": w, "sumR": round(s, 2), "avgR": round(s / n, 3) if n else None}
    out = {"generated": dt.datetime.now(JST).strftime("%Y-%m-%d %H:%M"), "horizon_h": HORIZON_H,
           "votes": len(votes), "by_zone": {}, "spans": []}
    covered = set()
    for z in tr.ZONES:
        zs = [s for s in spans if s["zone"] == z]
        a = [x for s in zs for x in ai if s["t0"] <= x["bt"] < s["t1"]]
        c = [x for s in zs for x in chair if s["t0"] <= x["bt"] < s["t1"]]
        covered.update(x["id"] for x in a)
        out["by_zone"][z] = {"votes": len(zs), "ai": agg(a), "chair": agg(c)}
    if votes:
        first = spans[0]["t0"]
        rest = [x for x in ai if x["bt"] >= first and x["id"] not in covered]
        out["no_vote_ai"] = agg(rest)
    for s in spans:
        a = [x for x in ai if s["t0"] <= x["bt"] < s["t1"]]
        out["spans"].append({**s, "t0_jst": dt.datetime.fromtimestamp(s["t0"], JST).strftime("%m-%d %H:%M"),
                             "ai": agg(a)})
    out["note"] = ("票30件未満=サンプル不足。判定は票30件以上・勝ち票区間と負け票区間のAI平均Rの差で見る。"
                   "フィルタには使わない(観測)。")
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ゾーン票 {len(votes)}件  区間=次の票まで(上限{HORIZON_H}h)")
    for z, v in out["by_zone"].items():
        a, c = v["ai"], v["chair"]
        print(f"  {z}票 {v['votes']}件: AI紙 n={a['n']} 勝{a['win']} 合計{a['sumR']:+}R 平均{a['avgR']} / 会長 n={c['n']} 合計{c['sumR']:+}R")
    if votes:
        r = out["no_vote_ai"]; print(f"  票なし区間(対照): AI紙 n={r['n']} 合計{r['sumR']:+}R 平均{r['avgR']}")
    print("  " + out["note"]); print("saved:", OUT)

if __name__ == "__main__":
    main()
