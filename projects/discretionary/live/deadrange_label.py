# -*- coding: utf-8 -*-
"""死んだレンジ票 v1 — 会長2026-11-10 GO。観測ラベルのみ・撃ち方不変・読取のみ・発注なし。

会長の言葉: 「抜けそうで抜けない死んだレンジも負けゾーンでは?」
定義 v1(事前固定 2026-11-10・測るための固定であって永続ではない):
  fake10  = ブレイク時刻以前に決着していた直近10本(lane3 基礎トレード)のダマシ率   ← rules_v1.rain_rate と同式
  streak  = 再加速(紙)の約定時刻以前に決着していた本の直近連敗数(最後の勝ちで0)   ← 執行機 _context_labels.streak_paper と同式
  dead    = fake10 ≥ 0.60 かつ streak ≥ 3
  いずれも各時点の過去データだけで計算(先読みなし)。過去の本に遡って付けても前向きと同じ値になる。

判定の事前固定(切替は会長GO):
  dead側が30本に達した時点で、dead側の平均Rが 0 未満 かつ 非dead側との差が -0.2R 以下なら
  「執行機で dead の本は撃たない or lot半分」を会長に提案する。それまではサンプル不足・ラベルだけ。

出力: RESULTS_deadrange_label.md / deadrange_labels.json(sid→ラベル)。台帳は書き換えない。
"""
import os, json
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, HERE)
from rules_v1 import rain_rate

LED = os.path.join(HERE, "setup_ledger.jsonl")
REG = os.path.join(HERE, "reaccel_regime_labels.json")
OUT_MD = os.path.join(HERE, "RESULTS_deadrange_label.md")
OUT_JS = os.path.join(HERE, "deadrange_labels.json")

VERSION = "deadrange_v1"
FROZEN_AT = "2026-11-10"
FAKE_TH = 0.60
STREAK_TH = 3
N_NEEDED = 30


def fold_setups():
    recs = {}
    for ln in open(LED, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if r.get("kind") == "setup":
            recs[r["id"]] = dict(r)
        elif r.get("kind") == "update":
            s = recs.get(r.get("target"))
            if s:
                for k, v in r.items():
                    if k not in ("kind", "target", "logged_at"):
                        s[k] = v
    return recs


def load_regime():
    try:
        d = json.load(open(REG, encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    if isinstance(d, dict):
        for sid, v in d.items():
            if isinstance(v, dict):
                out[sid] = v.get("regime") or v.get("gold_regime")
            elif isinstance(v, str):
                out[sid] = v
    return out


def stats(xs):
    n = len(xs)
    if n == 0:
        return {"n": 0}
    R = [x["R"] for x in xs]
    cum = pk = dd = 0.0
    for r in R:
        cum += r; pk = max(pk, cum); dd = min(dd, cum - pk)
    return {"n": n, "avg_R": round(sum(R) / n, 3), "sum_R": round(sum(R), 2),
            "win": round(100.0 * sum(1 for r in R if r > 0) / n, 1), "max_dd_R": round(dd, 2)}


def fmt(label, s):
    if s["n"] == 0:
        return "  %-26s n=  0" % label
    return "  %-26s n=%3d 平均R%+.3f 合計%+.2f 勝率%.0f%% DD%.1fR" % (label, s["n"], s["avg_R"], s["sum_R"], s["win"], s["max_dd_R"])


def main():
    recs = fold_setups()
    regime = load_regime()
    closed_hist = [s for s in recs.values() if s.get("status") == "closed" and s.get("exit_time") is not None]
    # 再加速 確定本(紙)
    rows = []
    for sid, s in recs.items():
        ra = s.get("reaccel") or {}
        if ra.get("status") != "closed" or ra.get("R") is None or not ra.get("entry_time"):
            continue
        rows.append({"sid": sid, "R": float(ra["R"]), "entry_time": int(ra["entry_time"]),
                     "exit_time": int(ra.get("exit_time") or ra["entry_time"]),
                     "entry_jst": ra.get("entry_jst"), "break_time": s.get("break_time"),
                     "side": s.get("side"), "regime": regime.get(sid)})
    rows.sort(key=lambda r: r["entry_time"])
    closes_sorted = sorted(((r["exit_time"], r["R"], r["sid"]) for r in rows))

    labels = {}
    for r in rows:
        fr, nprev = rain_rate(r["break_time"], closed_hist)
        # 直近連敗(この本の約定時刻以前に決着した本・自分は除く)
        k = 0
        for et, R, sid2 in reversed([c for c in closes_sorted if c[0] <= r["entry_time"] and c[2] != r["sid"]]):
            if R < 0:
                k += 1
            else:
                break
        dead = (fr is not None and fr >= FAKE_TH and k >= STREAK_TH)
        r.update({"fake10": fr, "fake_n": nprev, "streak": k, "dead": bool(dead),
                  "fake_hi": bool(fr is not None and fr >= FAKE_TH), "streak_hi": bool(k >= STREAK_TH)})
        labels[r["sid"]] = {"version": VERSION, "fake10": fr, "fake_n": nprev, "streak": k, "dead": bool(dead),
                            "R": r["R"], "entry_jst": r["entry_jst"]}

    L = []
    L.append("# 死んだレンジ票 v1(紙・再加速 確定本) — %s" % __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"))
    L.append("")
    L.append("定義(事前固定 %s): dead = 直前10本ダマシ率≥%.0f%% かつ 紙連敗≥%d。観測ラベルのみ・撃ち方不変。" % (FROZEN_AT, FAKE_TH * 100, STREAK_TH))
    L.append("判定の節目: dead側%d本。到達時に dead平均R<0 かつ 非deadとの差≤-0.2R なら執行機側の扱い(見送り/lot半分)を会長に提案。" % N_NEEDED)
    L.append("")
    allr = rows
    dead = [r for r in rows if r["dead"]]
    nd = [r for r in rows if not r["dead"]]
    L.append("## 全体")
    L.append(fmt("全部", stats(allr)))
    L.append(fmt("dead(死んだレンジ)", stats(dead)))
    L.append(fmt("非dead", stats(nd)))
    sd, sn = stats(dead), stats(nd)
    if sd["n"] and sn["n"]:
        L.append("  差(dead−非dead) %+.3f R/本 ・ 節目まで dead あと%d本%s" % (sd["avg_R"] - sn["avg_R"], max(0, N_NEEDED - sd["n"]),
                 "" if sd["n"] >= N_NEEDED else " = サンプル不足"))
    L.append("")
    L.append("## 部品ごと(どちらが効いているか)")
    L.append(fmt("ダマシ率≥60%", stats([r for r in rows if r["fake_hi"]])))
    L.append(fmt("ダマシ率<60%", stats([r for r in rows if r["fake10"] is not None and not r["fake_hi"]])))
    L.append(fmt("ダマシ率 履歴不足", stats([r for r in rows if r["fake10"] is None])))
    L.append(fmt("連敗≥3", stats([r for r in rows if r["streak_hi"]])))
    L.append(fmt("連敗<3", stats([r for r in rows if not r["streak_hi"]])))
    L.append("")
    L.append("## 2×2")
    for fh in (True, False):
        for sh in (True, False):
            xs = [r for r in rows if r["fake_hi"] == fh and r["streak_hi"] == sh and r["fake10"] is not None]
            L.append(fmt("ダマシ%s×連敗%s" % ("高" if fh else "低", "高" if sh else "低"), stats(xs)))
    L.append("")
    L.append("## 連敗数ごと(連敗0/1/2/3/4+)")
    for k in (0, 1, 2, 3):
        L.append(fmt("連敗%d" % k, stats([r for r in rows if r["streak"] == k])))
    L.append(fmt("連敗4+", stats([r for r in rows if r["streak"] >= 4])))
    L.append("")
    L.append("## ダマシ率 帯ごと")
    for lo, hi in ((0.0, 0.3), (0.3, 0.6), (0.6, 0.8), (0.8, 1.01)):
        xs = [r for r in rows if r["fake10"] is not None and lo <= r["fake10"] < hi]
        L.append(fmt("ダマシ率 %.0f-%.0f%%" % (lo * 100, min(hi, 1.0) * 100), stats(xs)))
    if any(r["regime"] for r in rows):
        L.append("")
        L.append("## dead × 地合い(ER)")
        for reg in ("chop", "trend"):
            L.append(fmt("dead×%s" % reg, stats([r for r in dead if r["regime"] == reg])))
            L.append(fmt("非dead×%s" % reg, stats([r for r in nd if r["regime"] == reg])))
    L.append("")
    L.append("## dead の本 明細(新しい順・最大40)")
    for r in sorted(dead, key=lambda r: -r["entry_time"])[:40]:
        L.append("  %s %s %s R%+.2f ダマシ%.0f%% 連敗%d %s" % (r["entry_jst"], r["sid"], r["side"], r["R"],
                 (r["fake10"] or 0) * 100, r["streak"], r["regime"] or ""))
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump({"version": VERSION, "frozen_at": FROZEN_AT, "fake_th": FAKE_TH, "streak_th": STREAK_TH,
               "n_needed": N_NEEDED, "generated": L[0].split("— ")[-1],
               "summary": {"all": stats(allr), "dead": stats(dead), "not_dead": stats(nd)},
               "labels": labels}, open(OUT_JS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(L[:12]))
    print("... -> %s" % OUT_MD)


if __name__ == "__main__":
    main()
