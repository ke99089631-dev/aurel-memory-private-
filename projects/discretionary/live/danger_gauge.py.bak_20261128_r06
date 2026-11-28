# -*- coding: utf-8 -*-
"""
肥料(紙・再加速)の「危ない判定」3本 — R-05(2026-11-17 会長GO・事前固定)。読取のみ・発注なし・台帳は書かない。
  物差しはコックピットと同じ「正味R」(スプレッド時間帯中央値+手数料を控除・break_time順)。
  ① レンジ側(ER<0.12)の平均R: 2026-11-01以降の確定本で数え、100本到達時に平均R<0 なら触れた。
  ② 山からの落ち幅: 正味累積Rの最高値から現在までの落ち幅が -15R に届いたら触れた(想定DD-10.6R)。
  ③ 大当たり頻度: 直近100本(確定・正味)のうち +2R以上の割合が 5% を切ったら触れた(基準10〜12%)。
  どれか1つで「合わない」の検討に入る=レシピ変更でなく サイズ縮小/休止 の検討(会長GO必須)。
  出力: RESULTS_danger_gauge.md / danger_gauge.json(コックピット用)。
"""
import os, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
LED = os.path.join(HERE, "setup_ledger.jsonl")
LABELS = os.path.join(HERE, "reaccel_regime_labels.json")
OUT_MD = os.path.join(HERE, "RESULTS_danger_gauge.md")
OUT_JS = os.path.join(HERE, "danger_gauge.json")
TREND_TH = 0.12
CHOP_SINCE = "2026-11-01"      # 事前固定: 停滞期の起点
CHOP_N = 100                   # ① 判定本数
DD_LIMIT = -15.0               # ② 落ち幅
BIG_R, BIG_WIN, BIG_MIN = 2.0, 100, 0.05   # ③ 直近100本の+2R以上割合 < 5%


def _cost_model():
    cm = {"commission_pt": 0.06, "spread_pt_default": 0.25, "slippage_pt": 0.0}
    try:
        cm.update({k: v for k, v in json.load(open(os.path.join(HERE, "cost_model.json"), encoding="utf-8")).items()
                   if not k.startswith("_") and not k.endswith("_note")})
    except Exception:
        pass
    by_hour = {}
    try:
        for line in open(os.path.join(HERE, "spread_log.jsonl"), encoding="utf-8"):
            try:
                r = json.loads(line); by_hour.setdefault(int(r["jst_hour"]), []).append(float(r["spread_pt"]))
            except Exception:
                continue
    except Exception:
        pass
    med = {}
    for h, xs in by_hour.items():
        if len(xs) >= 20:
            xs = sorted(xs); med[h] = round(xs[len(xs) // 2], 3)
    cm["spread_by_hour"] = med
    return cm


def _net_R(ra, jst_hour, cm):
    risk = abs(float(ra["entry"]) - float(ra["sl"])) if ra.get("entry") is not None and ra.get("sl") is not None else None
    if not risk:
        return float(ra["R"])
    jh = None
    try:
        jh = int(((int(ra["entry_time"]) // 3600) + 9) % 24) if ra.get("entry_time") else int(jst_hour)
    except Exception:
        pass
    sp = cm["spread_by_hour"][jh] if jh is not None and jh in cm["spread_by_hour"] else float(cm["spread_pt_default"])
    cost = sp + float(cm["commission_pt"]) + float(cm.get("slippage_pt") or 0.0)
    return round(float(ra["R"]) - cost / risk, 3)


def _load():
    recs, order = {}, []
    for line in open(LED, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("kind") == "setup":
            recs[r["id"]] = r; order.append(r["id"])
        elif r.get("kind") == "update":
            t = recs.get(r.get("target"))
            if t:
                for k, v in r.items():
                    if k not in ("kind", "target", "logged_at"):
                        t[k] = v
    return [recs[i] for i in order]


def main():
    cm = _cost_model()
    labels = {}
    try:
        labels = json.load(open(LABELS, encoding="utf-8"))
    except Exception:
        pass
    tr = []
    for r in _load():
        ra = r.get("reaccel") if isinstance(r.get("reaccel"), dict) else None
        if not ra or ra.get("status") != "closed" or ra.get("R") is None:
            continue
        et = int(ra.get("exit_time") or r.get("break_time") or 0)
        lab = labels.get(r["id"]) or {}
        er = lab.get("er") if isinstance(lab, dict) else None
        tr.append({"sid": r["id"], "bt": int(r.get("break_time") or 0), "R": _net_R(ra, r.get("jst_hour"), cm),
                   "exit_jst": (dt.datetime.utcfromtimestamp(et) + dt.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M") if et else "",
                   "er": er})
    tr.sort(key=lambda x: x["bt"])
    cum = peak = 0.0
    for x in tr:
        cum += x["R"]; peak = max(peak, cum); x["cum"] = round(cum, 2)
    # ① レンジ側 平均R(11-01以降・ラベル有のみ)
    chop = [x for x in tr if x["exit_jst"] >= CHOP_SINCE and x["er"] is not None and float(x["er"]) < TREND_TH]
    unl = sum(1 for x in tr if x["exit_jst"] >= CHOP_SINCE and x["er"] is None)
    chop_avg = round(sum(x["R"] for x in chop) / len(chop), 3) if chop else None
    g1 = {"n": len(chop), "n_needed": CHOP_N, "avg_R": chop_avg, "unlabeled": unl,
          "hit": bool(chop and len(chop) >= CHOP_N and chop_avg < 0),
          "state": ("触れた" if (chop and len(chop) >= CHOP_N and chop_avg < 0) else
                    ("本数到達・平均R≥0=無事" if len(chop) >= CHOP_N else "サンプル不足(%d/%d)" % (len(chop), CHOP_N)))}
    # ② 落ち幅
    dd_now = round(cum - peak, 2)
    g2 = {"cum_R": round(cum, 2), "peak_R": round(peak, 2), "dd_now": dd_now, "limit": DD_LIMIT,
          "hit": dd_now <= DD_LIMIT, "state": "触れた" if dd_now <= DD_LIMIT else "想定内(%.1fR / 線%.0fR)" % (dd_now, DD_LIMIT)}
    # ③ 大当たり頻度
    last = tr[-BIG_WIN:]
    big = sum(1 for x in last if x["R"] >= BIG_R)
    share = round(big / len(last), 3) if last else None
    g3 = {"n": len(last), "big_n": big, "share": share, "min": BIG_MIN,
          "hit": bool(last and len(last) >= BIG_WIN and share < BIG_MIN),
          "state": ("触れた" if (last and len(last) >= BIG_WIN and share < BIG_MIN) else
                    ("健在(%.0f%%)" % (100 * share) if share is not None else "n/a"))}
    any_hit = g1["hit"] or g2["hit"] or g3["hit"]
    res = {"generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "rule": "R-05 (2026-11-17 会長GO)",
           "metric": "紙・再加速 正味R(コックピットと同じ)", "n_closed": len(tr),
           "g1_chop_avg": g1, "g2_drawdown": g2, "g3_big_share": g3, "any_hit": any_hit,
           "action": "触れたら『合わない』の検討(サイズ縮小/休止・会長GO)。レシピは変えない。"}
    json.dump(res, open(OUT_JS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = "# 危ない判定 R-05(紙・再加速 正味R) %s\n\n" % res["generated"]
    md += "確定%d本・正味累積%+.2fR(最高%+.2fR)\n" % (len(tr), cum, peak)
    md += "  ① レンジ側(ER<0.12・%s以降)平均R: n=%d/%d 平均%s → %s%s\n" % (
        CHOP_SINCE, g1["n"], CHOP_N, ("%+.3f" % chop_avg) if chop_avg is not None else "n/a", g1["state"],
        (" (ラベル未付与%d本)" % unl) if unl else "")
    md += "  ② 山からの落ち幅: %+.2fR(線 %.0fR) → %s\n" % (dd_now, DD_LIMIT, g2["state"])
    md += "  ③ 直近%d本の+2R以上: %d本=%s → %s\n" % (len(last), big, ("%.0f%%" % (100 * share)) if share is not None else "n/a", g3["state"])
    md += "  判定: %s\n" % ("★どれかが触れた → 『合わない』の検討へ(サイズ縮小/休止・会長GO)" if any_hit else "3本とも触れていない → 継続(レシピ不変)")
    open(OUT_MD, "w", encoding="utf-8").write(md)
    print(md)


if __name__ == "__main__":
    main()
