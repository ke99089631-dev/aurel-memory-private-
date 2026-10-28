# -*- coding: utf-8 -*-
"""②焼かれ測定 — 会長仮説2026-10-28『極厚壁の連続タッチのダマシでやられる』を数字にする。読取のみ・発注しない。
2軸: (A)連続タッチ=setup.features.wall_touches / (B)厚い壁=壁が当日の厚い行使価格(goldinfo pack options.strikes)に近く建玉が厚い。
対象: lane3 reaccel の確定本(reaccel.R)。出力: 厚い壁近接×タッチ数のクロス表 / 直近の焼かれ本の明細。
使い方: python fakeout_probe.py [--near 15] [--oi 30000] [--touch 5]
"""
import os, sys, json, glob, argparse
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "setup_ledger.jsonl")
GOLDINFO = r"C:\Users\user\.aurel\goldinfo"


def load_strikes_by_date():
    """date(YYYY-MM-DD) -> [(xau_price, oi_total), ...]。"""
    out = {}
    for p in glob.glob(os.path.join(GOLDINFO, "pack_*.json")):
        dt = os.path.basename(p)[5:15]
        try:
            d = json.load(open(p, encoding="utf-8"))
            st = (d.get("options") or {}).get("strikes") or []
            out[dt] = [(float(s["xau_equiv"]), float(s.get("oi_total") or 0)) for s in st if s.get("xau_equiv")]
        except Exception:
            pass
    return out


def nearest_strike(wall, strikes):
    """壁に最も近い行使価格の (距離$, その建玉oi)。strikes無ければ (None,None)。"""
    best = None
    for px, oi in strikes:
        dist = abs(wall - px)
        if best is None or dist < best[0]:
            best = (dist, oi)
    return best if best else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--near", type=float, default=15.0, help="壁がこの$以内の行使価格に近いと『壁に接触』")
    ap.add_argument("--oi", type=float, default=30000.0, help="その行使価格の建玉がこれ以上なら『厚い』")
    ap.add_argument("--touch", type=int, default=5, help="タッチ数がこれ以上なら『連続タッチ』")
    args = ap.parse_args()

    strikes_by_date = load_strikes_by_date()
    setups = {}; R = {}
    for line in open(LEDGER, encoding="utf-8"):
        try: d = json.loads(line)
        except Exception: continue
        sid = d.get("id") or d.get("target")
        if d.get("kind") == "setup" and d.get("lane") == "3":
            setups[sid] = {"wt": (d.get("features") or {}).get("wall_touches"),
                           "wall": d.get("wall"), "wall_kind": d.get("wall_kind"),
                           "jst": d.get("break_jst")}
        ra = d.get("reaccel")
        if isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None:
            R[sid] = float(ra["R"])

    rows = []
    for sid, r in R.items():
        s = setups.get(sid)
        if not s or s.get("wt") is None or s.get("wall") is None or not s.get("jst"):
            continue
        dt = s["jst"][:10]
        dist, oi = nearest_strike(float(s["wall"]), strikes_by_date.get(dt, []))
        thick = (dist is not None and dist <= args.near and oi is not None and oi >= args.oi)
        many = s["wt"] >= args.touch
        rows.append({"sid": sid, "jst": s["jst"], "wt": s["wt"], "wk": s["wall_kind"],
                     "R": r, "dist": dist, "oi": oi, "thick": thick, "many": many})

    def summ(name, xs):
        if not xs:
            print("%-28s n=0" % name); return
        import statistics
        print("%-28s n=%3d 平均R%+.3f 勝率%3.0f%% 合計R%+.1f" % (
            name, len(xs), statistics.mean([x["R"] for x in xs]),
            100 * sum(1 for x in xs if x["R"] > 0) / len(xs), sum(x["R"] for x in xs)))

    print("=== ②焼かれ測定 (near<=%.0f$ / oi>=%.0f / touch>=%d) 対象%d本 ===" % (args.near, args.oi, args.touch, len(rows)))
    summ("厚い壁×連続タッチ(会長説)", [x for x in rows if x["thick"] and x["many"]])
    summ("厚い壁×タッチ少", [x for x in rows if x["thick"] and not x["many"]])
    summ("薄い壁×連続タッチ", [x for x in rows if not x["thick"] and x["many"]])
    summ("薄い壁×タッチ少", [x for x in rows if not x["thick"] and not x["many"]])
    summ("全体", rows)

    print("\n-- 直近の焼かれ本(R<0・新しい順12) wall↔厚い行使価格の距離/建玉 --")
    losers = [x for x in rows if x["R"] < 0]
    losers.sort(key=lambda x: x["jst"], reverse=True)
    for x in losers[:12]:
        ds = ("%.1f$/oi%.0f%s" % (x["dist"], x["oi"], "★厚" if x["thick"] else "")) if x["dist"] is not None else "strike無"
        print("  %s %s タッチ%2d %-5s R%+.2f  最寄行使%s" % (x["sid"], x["jst"], x["wt"], x["wk"], x["R"], ds))


if __name__ == "__main__":
    main()
