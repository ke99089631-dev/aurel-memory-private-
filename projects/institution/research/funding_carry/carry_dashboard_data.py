# -*- coding: utf-8 -*-
"""キャリー畑 尻尾ダッシュボードの元データ(読取のみ・発注なし・金は動かさない)。
会長GO 2026-10-30。BTC+ETH 50/50 のデルタ中立キャリー(現物買い×永久売り)。

出すもの(会長の壁=尻尾):
  ①普段の利回り(年率ネット) ②負け側だった割合 ③最悪の一撃(最大DD)
  + 水面下日数(ずっと払い続けた最長) + 畳むルールの発火回数
正直な限界: ここは「受け取る資金調達料」だけの曲線。現物と先物の一時的なズレ(ベーシス)
  や証拠金・清算リスクは別(価格系列が要る)。だから尻尾の下限でなく「料金ベースの尻尾」。
"""
import urllib.request, json, time

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
WEIGHTS = {"BTCUSDT": 0.5, "ETHUSDT": 0.5}
DAYS = 365
MS_PER_DAY = 86400000
NOW_MS = int(time.time() * 1000)
START_MS = NOW_MS - DAYS * MS_PER_DAY
RT_COST = 0.0029          # 往復手数料(個人の広めコスト・入口出口1回)
FOLD_WIN = 30             # 畳むルール: 直近30回(=10日)の合計資金調達
FOLD_THRESH = 0.0         # それがマイナスに沈んだら「畳む(縮小/停止)」合図

def fetch(sym):
    rows, cur = [], START_MS
    while cur < NOW_MS:
        url = ("https://fapi.binance.com/fapi/v1/fundingRate?symbol=%s"
               "&startTime=%d&endTime=%d&limit=1000" % (sym, cur, NOW_MS))
        with urllib.request.urlopen(url, timeout=20) as r:
            batch = json.load(r)
        if not batch:
            break
        rows.extend(batch)
        last = batch[-1]["fundingTime"]
        if last <= cur:
            break
        cur = last + 1
        if len(batch) < 1000:
            break
        time.sleep(0.2)
    out = {}
    for x in rows:
        out[x["fundingTime"]] = float(x["fundingRate"])
    return out

def max_drawdown(equity):
    peak = equity[0]; mdd = 0.0; peak_i = 0; trough_i = 0; bi = 0; bj = 0
    for i, v in enumerate(equity):
        if v > peak:
            peak = v; peak_i = i
        dd = v - peak
        if dd < mdd:
            mdd = dd; trough_i = i; bi = peak_i; bj = i
    return mdd, bi, bj

def main():
    series = {s: fetch(s) for s in SYMBOLS}
    # 共通の資金調達時刻だけ使う(両方が資金調達した時刻)
    times = sorted(set(series[SYMBOLS[0]]) & set(series[SYMBOLS[1]]))
    basket = [sum(WEIGHTS[s] * series[s][t] for s in SYMBOLS) for t in times]
    n = len(basket)
    # 累積(エクイティ)カーブ: 入口でRT_COSTを一度引く
    equity = []
    acc = -RT_COST
    for r in basket:
        acc += r
        equity.append(acc)
    days_cov = (times[-1] - times[0]) / MS_PER_DAY
    gross = sum(basket)
    gross_annual = gross / days_cov * 365
    net_annual = (gross - RT_COST) / days_cov * 365
    neg = sum(1 for r in basket if r < 0)
    mdd, bi, bj = max_drawdown(equity)
    # 水面下日数(直近ピークを下回り続けた最長)
    peak = equity[0]; uw = 0; max_uw = 0
    for v in equity:
        if v >= peak:
            peak = v; uw = 0
        else:
            uw += 1; max_uw = max(max_uw, uw)
    # 畳むルールの発火(直近30回の合計がマイナス)
    folds = 0; in_fold = False; fold_periods = 0
    for i in range(n):
        w = basket[max(0, i - FOLD_WIN + 1): i + 1]
        trail = sum(w)
        if trail < FOLD_THRESH:
            fold_periods += 1
            if not in_fold:
                folds += 1; in_fold = True
        else:
            in_fold = False
    out = {
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "basket": "BTC50/ETH50 デルタ中立キャリー",
        "days": round(days_cov, 1), "n_periods": n,
        "cost_roundtrip_pct": RT_COST * 100,
        "yield_gross_annual_pct": round(gross_annual * 100, 2),
        "yield_net_annual_pct": round(net_annual * 100, 2),
        "pct_negative": round(neg / n * 100, 1),
        "max_drawdown_pct": round(mdd * 100, 2),
        "dd_from_days": round((times[bi] - times[0]) / MS_PER_DAY, 1),
        "dd_to_days": round((times[bj] - times[0]) / MS_PER_DAY, 1),
        "longest_underwater_days": round(max_uw * 8 / 24, 1),
        "worst8h_pct": round(min(basket) * 100, 4),
        "best8h_pct": round(max(basket) * 100, 4),
        "fold_rule": "直近%d回(=10日)の合計がマイナスで畳む" % FOLD_WIN,
        "fold_events": folds,
        "fold_coverage_pct": round(fold_periods / n * 100, 1),
        # チャート用(日次に間引き: 3回/日→1日1点)
        "curve_days": [round((t - times[0]) / MS_PER_DAY, 2) for t in times[::3]],
        "curve_equity_pct": [round(e * 100, 3) for e in equity[::3]],
    }
    with open(__file__.replace("carry_dashboard_data.py", "carry_dashboard_data.json"),
              "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    # 画面にはサマリだけ(曲線は出さない)
    brief = {k: v for k, v in out.items() if not k.startswith("curve_")}
    print(json.dumps(brief, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
