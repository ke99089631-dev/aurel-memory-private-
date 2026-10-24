# -*- coding: utf-8 -*-
"""
AI再加速(紙・setup_ledger) の「地合い別R」前向き答え合わせ。2026-10-24 会長GO(次の一手②)。
  会長仮説(2026-10-24): 『トレンドでも再加速はRを保つ可能性がある』。
  やること: 各セットアップの break_time 時点の地合い(24h効率比ER・24h荒れ比)をラベル化してキャッシュに貯め、
           再加速(全/keep/drop/外壁)とAI本線のRを地合い別に出す。
  なぜキャッシュ: 8793のAPIは約5000本(≈17日)しか返さない。毎日回して新しいセットアップにその場でラベルを貼れば
           前向きに全数カバーできる(10-24時点の過去分は窓内107本だけ=部分)。ラベルは一度貼ったら固定(後出し変更なし)。
  閾値(事前固定): ER≥0.12=トレンド(肥料の約定ラベル _gold_er と同じ) / 三分位も併記。
  出力: reaccel_regime_labels.json(キャッシュ) / reaccel_regime_forward.json(コックピット用) / RESULTS_reaccel_regime_forward.md
  読取のみ・発注なし。
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_engine as se

LED = os.path.join(HERE, "setup_ledger.jsonl")
CACHE = os.path.join(HERE, "reaccel_regime_labels.json")
OUT_JS = os.path.join(HERE, "reaccel_regime_forward.json")
OUT_MD = os.path.join(HERE, "RESULTS_reaccel_regime_forward.md")
TREND_TH = 0.12
WIN = 288          # 24h
VOL_REF = 1440     # 5日


def fold():
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
                for k in ("reaccel", "chase", "status", "R", "v1", "exit_reason"):
                    if k in r:
                        s[k] = r[k]
    return recs


def label_new(recs, cache):
    m5 = se._fetch_bars(14000)
    if m5 is None or len(m5) < WIN + 10:
        return cache, 0, None
    c = m5["close"]; h = m5["high"]; l = m5["low"]
    er = (c - c.shift(WIN)).abs() / c.diff().abs().rolling(WIN).sum()
    rng = h.rolling(WIN).max() - l.rolling(WIN).min()
    vol = rng / rng.rolling(VOL_REF).median()
    first_ok = m5.index[VOL_REF] if len(m5) > VOL_REF else m5.index[-1]
    added = 0
    for sid, s in recs.items():
        if sid in cache:
            continue
        bt = int(s.get("break_time") or 0)
        if not bt:
            continue
        t = pd.Timestamp(bt, unit="s", tz="UTC")
        if t < m5.index[WIN] or t > m5.index[-1]:
            continue
        i = int(m5.index.searchsorted(t)) - 1
        e = float(er.iloc[i]); v = float(vol.iloc[i]) if t >= first_ok else None
        if np.isnan(e):
            continue
        cache[sid] = {"er": round(e, 4), "vol": None if (v is None or np.isnan(v)) else round(v, 3),
                      "regime": "trend" if e >= TREND_TH else "chop", "labeled_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M")}
        added += 1
    return cache, added, (str(m5.index[0])[:16], str(m5.index[-1])[:16])


def _st(rs):
    if not rs:
        return {"n": 0}
    wins = sum(1 for r in rs if r > 0)
    return {"n": len(rs), "avg_R": round(float(np.mean(rs)), 3), "sum_R": round(float(np.sum(rs)), 2),
            "win": round(100.0 * wins / len(rs), 1)}


def main():
    recs = fold()
    cache = {}
    if os.path.exists(CACHE):
        try:
            cache = json.load(open(CACHE, encoding="utf-8"))
        except Exception:
            cache = {}
    cache, added, window = label_new(recs, cache)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    lanes = {}
    def put(lane, sid, R):
        lanes.setdefault(lane, []).append((sid, float(R)))
    for sid, s in recs.items():
        if sid not in cache:
            continue
        keep = bool((s.get("v1") or {}).get("keep", False))
        ra = s.get("reaccel") or {}
        if ra.get("status") == "closed" and ra.get("R") is not None:
            put("再加速(全)", sid, ra["R"])
            put("再加速/keep" if keep else "再加速/drop", sid, ra["R"])
            if s.get("wall_kind") == "outer":
                put("再加速/外壁", sid, ra["R"])
        if s.get("status") == "closed" and s.get("R") is not None:
            put("AI本線", sid, s["R"])
    n_re_total = sum(1 for s in recs.values() if (s.get("reaccel") or {}).get("status") == "closed")
    out = {"generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "trend_th": TREND_TH,
           "coverage": {"labeled_setups": len(cache), "setups_total": len(recs),
                        "reaccel_closed_labeled": len(lanes.get("再加速(全)", [])), "reaccel_closed_total": n_re_total,
                        "bars_window": window, "added_now": added},
           "lanes": {}}
    for lane, xs in lanes.items():
        tr = [R for sid, R in xs if cache[sid]["regime"] == "trend"]
        ch = [R for sid, R in xs if cache[sid]["regime"] == "chop"]
        d = {"all": _st([R for _, R in xs]), "trend": _st(tr), "chop": _st(ch)}
        if len(xs) >= 9:
            ers = np.array([cache[sid]["er"] for sid, _ in xs]); Rs = np.array([R for _, R in xs])
            q1, q2 = np.quantile(ers, [1 / 3, 2 / 3])
            d["tertile"] = {"低": _st(Rs[ers <= q1].tolist()), "中": _st(Rs[(ers > q1) & (ers <= q2)].tolist()),
                            "高": _st(Rs[ers > q2].tolist()), "edges": [round(float(q1), 3), round(float(q2), 3)]}
        out["lanes"][lane] = d
    json.dump(out, open(OUT_JS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def line(lab, s):
        return "  %-10s n=%3d 平均R%+.3f 合計%+.1f 勝率%d%%\n" % (lab, s["n"], s["avg_R"], s["sum_R"], s["win"]) if s.get("n") else "  %-10s n=0\n" % lab
    cov = out["coverage"]
    md = "# AI再加速 地合い別R(前向き答え合わせ) %s\n\n" % out["generated"]
    md += "対象: ラベル済み %d/%d セットアップ・再加速確定 %d/%d本(=**部分**。足API窓 %s・今回追加%d)。" % (
        cov["labeled_setups"], cov["setups_total"], cov["reaccel_closed_labeled"], cov["reaccel_closed_total"], cov["bars_window"], added)
    md += " 地合い=ブレイク時点の24h効率比ER(≥%.2f=トレンド)。gross=TP手前・コスト前。\n" % TREND_TH
    md += "会長仮説(10-24)『トレンドでも再加速は保つ』の採点欄。節目=トレンド側30本。それまでサンプル不足。\n\n"
    for lane in ("再加速(全)", "再加速/外壁", "再加速/keep", "再加速/drop", "AI本線"):
        d = out["lanes"].get(lane)
        if not d:
            continue
        md += "## %s\n" % lane + line("全体", d["all"]) + line("トレンド", d["trend"]) + line("チョップ", d["chop"])
        if "tertile" in d:
            t = d["tertile"]
            md += "  三分位(ER境界 %s): 低%+.3f(%d) 中%+.3f(%d) 高%+.3f(%d)\n" % (
                t["edges"], t["低"].get("avg_R", 0), t["低"]["n"], t["中"].get("avg_R", 0), t["中"]["n"], t["高"].get("avg_R", 0), t["高"]["n"])
        md += "\n"
    open(OUT_MD, "w", encoding="utf-8").write(md)
    print(md)


if __name__ == "__main__":
    main()
