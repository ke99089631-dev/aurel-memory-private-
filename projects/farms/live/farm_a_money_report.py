# -*- coding: utf-8 -*-
"""畑A(US100)の採点を金額ベースで出す。読取のみ・発注なし・台帳は書かない。
  2026-11-28 会長GO「畑Aは実行してくれ」。Rだけ見ていると口座が減っていても成績が良く見えるため、
  運用の採点を「1本あたりの金額リスク」と「金額ベースの山からの落ち幅」に移す。Rは型の診断用に残す。
  出力: RESULTS_farm_a_money.md / farm_a_money.json
"""
import os, json, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
LED = os.path.join(HERE, "farm_a_exec_ledger.jsonl")
OUT_MD = os.path.join(HERE, "RESULTS_farm_a_money.md")
OUT_JS = os.path.join(HERE, "farm_a_money.json")
RISK_FRAC = 0.004          # 凍結仕様の設計値(口座0.4%/トレード)
VAL_PER_PRICE = 1.0        # NAS100.r: 1価格単位 = 1USD / 1lot(31本で実損益と突合して検算済み)


def load():
    rows = []
    for line in open(LED, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def main():
    rows = load()
    fires = [r for r in rows if r.get("mode") == "fire"]
    closed = [r for r in rows if r.get("R") is not None]
    for r in closed:
        try:
            rp = abs(float(r["entry"]) - float(r["sl"]))
        except Exception:
            rp = None
        lot = float(r.get("lot") or 0.1)
        # 台帳に risk_usd_actual があればそれを使う(2026-11-28以降の本)。無ければ幅×ロットから再現。
        r["_risk_usd"] = float(r["risk_usd_actual"]) if r.get("risk_usd_actual") is not None else (
            round(rp * lot * VAL_PER_PRICE, 2) if rp else None)
        r["_R"] = float(r["R"])
        r["_p"] = float(r.get("profit") or 0.0)

    ok = [r for r in closed if r["_risk_usd"]]
    tot_p = sum(r["_p"] for r in closed)
    tot_R = sum(r["_R"] for r in closed)

    # 金額ベースの山からの落ち幅(=口座が実際に味わった痛み)
    cum = peak = 0.0; dd = 0.0
    for r in closed:
        cum += r["_p"]; peak = max(peak, cum); dd = min(dd, cum - peak)

    # Rベースの落ち幅(比較用)
    cR = pR = 0.0; ddR = 0.0
    for r in closed:
        cR += r["_R"]; pR = max(pR, cR); ddR = min(ddR, cR - pR)

    ru = sorted(r["_risk_usd"] for r in ok)
    win = [r for r in closed if r["_R"] > 0]; los = [r for r in closed if r["_R"] <= 0]
    floored = sum(1 for r in fires if r.get("floored_by_min"))
    has_new = sum(1 for r in fires if r.get("risk_usd_actual") is not None)

    # 反事実: 1本あたりの金額リスクを揃えていたら
    flat = (sum(r["_R"] for r in ok) * st.mean(ru)) if ok else None

    res = {
        "n_fire": len(fires), "n_closed": len(closed),
        "money": {"total_usd": round(tot_p, 2), "dd_usd": round(dd, 2),
                  "avg_usd": round(tot_p / len(closed), 2) if closed else None},
        "R": {"total_R": round(tot_R, 2), "dd_R": round(ddR, 2),
              "avg_R": round(tot_R / len(closed), 3) if closed else None},
        "risk_usd": {"n": len(ok), "min": ru[0] if ru else None, "med": st.median(ru) if ru else None,
                     "mean": round(st.mean(ru), 2) if ru else None, "max": ru[-1] if ru else None,
                     "spread_x": round(ru[-1] / ru[0], 1) if ru else None},
        "risk_skew": {"win_n": len(win), "win_avg_risk": round(st.mean([r["_risk_usd"] for r in win if r["_risk_usd"]]), 2) if win else None,
                      "los_n": len(los), "los_avg_risk": round(st.mean([r["_risk_usd"] for r in los if r["_risk_usd"]]), 2) if los else None},
        "counterfactual_flat_risk_usd": round(flat, 2) if flat is not None else None,
        "min_lot_floor": {"fires_with_new_fields": has_new, "floored": floored,
                          "note": "新しい列は2026-11-28以降の発注にだけ入る。それ以前は幅×ロットから再現。"},
        "design_risk_frac": RISK_FRAC,
    }
    m = "# 畑A(US100) 金額ベースの採点 : 読取のみ\n\n"
    m += "確定%d本(発注%d本)\n\n" % (len(closed), len(fires))
    m += "## 運用の採点(こちらが本番)\n"
    m += "  合計 %+.2f USD / 1本あたり %+.2f USD / 山からの落ち幅 %.2f USD\n" % (
        tot_p, tot_p / len(closed) if closed else 0, dd)
    m += "\n## 型の診断(Rは診断用・口座の成績ではない)\n"
    m += "  合計 %+.2fR / 1本あたり %+.3fR / 落ち幅 %.2fR\n" % (
        tot_R, tot_R / len(closed) if closed else 0, ddR)
    m += "  ★Rと金額の符号が違う場合、原因はサイズ決め(下)であって型ではない\n"
    m += "\n## 1本あたりの金額リスク(=1Rの値段)\n"
    if ru:
        m += "  最小 %.2f / 中央 %.2f / 平均 %.2f / 最大 %.2f USD → **%.1f倍のばらつき**\n" % (
            ru[0], st.median(ru), st.mean(ru), ru[-1], ru[-1] / ru[0])
        m += "  勝ち%d本の平均リスク %.2f USD / 負け%d本の平均リスク %.2f USD\n" % (
            len(win), res["risk_skew"]["win_avg_risk"] or 0, len(los), res["risk_skew"]["los_avg_risk"] or 0)
        m += "  リスク金額を揃えていたら %+.2f USD(実際は %+.2f USD)\n" % (flat, tot_p)
    m += "\n## 設計どおりなら谷はどれくらいだったか(一番効く比較)\n"
    # ★畑Aは金デモとは別口座。畑A自身の起動ログの最新「残高」を使う(金デモの残高を混ぜると間違える)
    bal = None
    try:
        import re
        txt = open(os.path.join(HERE, "farm_a_exec_fire.log"), encoding="utf-8", errors="replace").read()
        hits = re.findall(r"残高([0-9]+(?:\.[0-9]+)?)", txt)
        if hits:
            bal = float(hits[-1])
    except Exception:
        pass
    design_dd_pct = 100 * abs(ddR) * RISK_FRAC
    m += "  Rの落ち幅 %.2fR × 設計の%.1f%%/本 = **口座の %.1f%%** が設計どおりの谷\n" % (ddR, 100 * RISK_FRAC, design_dd_pct)
    if bal:
        actual_pct = 100 * abs(dd) / bal
        m += "  実際の谷 %.2f USD は今の残高に対して **%.1f%%** → 設計の **約%.1f倍**\n" % (dd, actual_pct, actual_pct / design_dd_pct if design_dd_pct else 0)
        res["design_vs_actual"] = {"design_dd_pct": round(design_dd_pct, 2), "actual_dd_pct": round(actual_pct, 2),
                                   "over_x": round(actual_pct / design_dd_pct, 2) if design_dd_pct else None}
    else:
        m += "  (残高が読めないので実際の%は出せない)\n"
    m += "\n## 最小ロットの床\n"
    m += "  設計は口座の%.1f%%/本。NAS100.rの最小ロットが床になり、予算どおりのロットが出ない。\n" % (100 * RISK_FRAC)
    m += "  新しい列が入った発注 %d本 / そのうち床で切り上がった %d本\n" % (has_new, floored)
    m += "  → 口座が小さいうちは、どんなに正しいリスク式でも床に負ける(肥料実弾 R-03 と同じ病気)\n"
    json.dump(res, open(OUT_JS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(OUT_MD, "w", encoding="utf-8").write(m)
    print(m)


if __name__ == "__main__":
    main()
