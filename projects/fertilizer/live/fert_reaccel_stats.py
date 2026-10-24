# -*- coding: utf-8 -*-
"""
肥料reaccel(806809) デモ成績 — 台帳だけで集計(MT5に触らない・発注なし)。2026-10-24 会長GO(次の一手①②)。
  入力: fert_reaccel_stop_ledger.jsonl の fill/close イベント(close は執行機が履歴から自記録)。
  出力: RESULTS_fert_reaccel_stats.md ＋ fert_reaccel_stats.json(コックピット/ブリーフ用)。
  見るもの:
    ① 撃つ集合の出口判定(事前固定): デモ全部が確定30本でネット平均R<0 なら FIRE_V1="keep" に戻す。
    ② keep/drop 別・地合い(gold_regime: ER<0.12 chop / ≥0.12 trend)別のR。「トレンドでも保つか」の前向き答え合わせ。
  R は約定値基準(建値→出口 / 建値→SL)。profit は手数料込みの実額(ドル)。
"""
import os, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "fert_reaccel_stop_ledger.jsonl")
OUT_MD = os.path.join(HERE, "RESULTS_fert_reaccel_stats.md")
OUT_JS = os.path.join(HERE, "fert_reaccel_stats.json")
EXIT_N = 30            # 事前固定: 出口判定の本数
TREND_TH = 0.12        # 執行機 _gold_er と同じ閾値


def _rows():
    out = []
    if not os.path.exists(LEDGER):
        return out
    for ln in open(LEDGER, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def _st(xs):
    if not xs:
        return {"n": 0}
    rs = [x["R"] for x in xs if x.get("R") is not None]
    pf = [x.get("profit") or 0.0 for x in xs]
    if not rs:
        return {"n": len(xs)}
    wins = sum(1 for r in rs if r > 0)
    cum, peak, dd = 0.0, 0.0, 0.0
    for r in rs:
        cum += r; peak = max(peak, cum); dd = min(dd, cum - peak)
    return {"n": len(rs), "sum_R": round(sum(rs), 2), "avg_R": round(sum(rs) / len(rs), 3),
            "win": round(100.0 * wins / len(rs), 1), "max_dd_R": round(dd, 2), "profit_usd": round(sum(pf), 2)}


def main():
    rows = _rows()
    fills = {r["sid"]: r for r in rows if r.get("event") == "fill"}
    closes = [r for r in rows if r.get("event") == "close"]
    closes.sort(key=lambda r: r.get("exit_time") or "")
    # fill 側のラベル(v1/地合い)を close に補完
    for c in closes:
        f = fills.get(c["sid"]) or {}
        for k in ("v1_keep", "gold_er", "gold_regime"):
            if c.get(k) is None and f.get(k) is not None:
                c[k] = f[k]
        if c.get("gold_regime") is None and c.get("gold_er") is not None:
            c["gold_regime"] = "trend" if float(c["gold_er"]) >= TREND_TH else "chop"
    open_n = len([s for s in fills if s not in {c["sid"] for c in closes}])
    keep = [c for c in closes if c.get("v1_keep") is True]
    drop = [c for c in closes if c.get("v1_keep") is False]
    unk = [c for c in closes if c.get("v1_keep") is None]
    trend = [c for c in closes if c.get("gold_regime") == "trend"]
    chop = [c for c in closes if c.get("gold_regime") == "chop"]
    since_go = [c for c in closes if (c.get("exit_time") or "") >= "2026-10-24T05:30:00"]   # ①GO以降(全部撃ち)の前向き
    res = {"generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "n_fill": len(fills), "n_open": open_n,
           "all": _st(closes), "keep": _st(keep), "drop": _st(drop), "v1_unknown": _st(unk),
           "trend": _st(trend), "chop": _st(chop),
           "keep_trend": _st([c for c in keep if c.get("gold_regime") == "trend"]),
           "drop_trend": _st([c for c in drop if c.get("gold_regime") == "trend"]),
           "since_fire_all": _st(since_go),
           "exit_rule": {"n_needed": EXIT_N, "rule": "全部撃ちが確定%d本でネット平均R<0 → FIRE_V1='keep' に戻す" % EXIT_N,
                         "n_now": len(since_go), "verdict": None},
           "trend_milestone": {"n_needed": 30, "n_now": len(trend)}}
    sg = res["since_fire_all"]
    if sg.get("n", 0) >= EXIT_N:
        res["exit_rule"]["verdict"] = "戻す(keepのみ)" if sg.get("avg_R", 0) < 0 else "継続(全部)"
    else:
        res["exit_rule"]["verdict"] = "判定前(%d/%d本)" % (sg.get("n", 0), EXIT_N)
    json.dump(res, open(OUT_JS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def line(lab, s):
        if s.get("n", 0) == 0 or "avg_R" not in s:
            return "  %-14s n=%d\n" % (lab, s.get("n", 0))
        return "  %-14s n=%2d 平均R%+.3f 合計R%+.2f 勝率%d%% DD%.1fR 損益%+.2f$\n" % (
            lab, s["n"], s["avg_R"], s["sum_R"], s["win"], s["max_dd_R"], s["profit_usd"])
    md = "# 肥料reaccel(806809) デモ成績 — 台帳集計 %s\n\n" % res["generated"]
    md += "約定%d本(建玉中%d・確定%d)。R=約定値基準・損益は手数料込み実額。\n\n" % (len(fills), open_n, len(closes))
    md += "## ① 撃つ集合(2026-10-24 GO: keep+drop 全部)\n"
    md += line("全部(確定)", res["all"]) + line("採用keep", res["keep"]) + line("除外drop", res["drop"])
    if unk:
        md += line("v1不明", res["v1_unknown"])
    md += line("GO後(全部撃ち)", sg)
    md += "  出口判定(事前固定): %s → %s\n\n" % (res["exit_rule"]["rule"], res["exit_rule"]["verdict"])
    md += "## ② 地合い別(約定時の24h効率比ER・閾値%.2f)\n" % TREND_TH
    md += line("トレンド", res["trend"]) + line("チョップ", res["chop"])
    md += line("keep×トレンド", res["keep_trend"]) + line("drop×トレンド", res["drop_trend"])
    md += "  節目: トレンド側30本(いま%d本)。それまでは「サンプル不足」。\n\n" % len(trend)
    md += "## 明細(確定)\n"
    for c in closes:
        md += "  %s %s %s 建%.2f→出%.2f %s R%+.2f %+.2f$ v1=%s ER%s(%s)\n" % (
            (c.get("exit_time") or "")[5:16], c["sid"], c["side"], c["fill_price"], c["exit_price"], c["reason"],
            c.get("R") or 0.0, c.get("profit") or 0.0,
            {True: "keep", False: "drop"}.get(c.get("v1_keep"), "?"), c.get("gold_er"), c.get("gold_regime"))
    open(OUT_MD, "w", encoding="utf-8").write(md)
    print(md)


if __name__ == "__main__":
    main()
