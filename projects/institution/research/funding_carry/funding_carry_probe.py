# -*- coding: utf-8 -*-
"""資金調達率キャリー 1次検証（読取のみ・発注なし・金は動かさない）。
会長GO 2026-10-30。大口が入らない「遅い」ニッチの見込みを初めて数字にする。

やること: Binanceの永久先物の資金調達率(8時間ごと)を過去約1年ぶん取得し、
現物買い×永久先物売り(デルタ中立)で受け取れるキャリーを年率で出す。
価格の上下は中立で相殺される前提なので、損益の源泉≒受け取る資金調達料。

コスト: 往復手数料(現物taker0.10%×2 + 先物taker0.045%×2 ≈ 0.29%)を
保有期間に対して1回だけ引く(1年保有なら年率0.29%)。借入なし(自己資金の中立)。
"""
import urllib.request, json, time, statistics as st

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
DAYS = 365
MS_PER_DAY = 86400000
NOW_MS = int(time.time() * 1000)
START_MS = NOW_MS - DAYS * MS_PER_DAY
RT_COST = 0.0029  # 往復手数料(年1回保有想定)

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
    # 重複除去
    seen, out = set(), []
    for x in rows:
        t = x["fundingTime"]
        if t in seen:
            continue
        seen.add(t); out.append(x)
    out.sort(key=lambda x: x["fundingTime"])
    return out

def analyze(sym, rows):
    rates = [float(x["fundingRate"]) for x in rows]
    n = len(rates)
    if n == 0:
        return None
    per_year = 3 * 365  # 8時間ごと=1日3回
    mean8h = st.mean(rates)
    gross_annual = mean8h * per_year          # 年率(グロス)
    net_annual = gross_annual - RT_COST       # 年率(往復コスト1回引き)
    neg = sum(1 for r in rates if r < 0)
    pos = sum(1 for r in rates if r > 0)
    cum = sum(rates)                           # 実測期間の累積(実測キャリー)
    days_cov = (rows[-1]["fundingTime"] - rows[0]["fundingTime"]) / MS_PER_DAY
    cum_annual = cum / days_cov * 365          # 実測を年率換算
    return {
        "symbol": sym, "n": n, "days": round(days_cov, 1),
        "mean8h_pct": round(mean8h * 100, 5),
        "gross_annual_pct": round(gross_annual * 100, 2),
        "net_annual_pct": round(net_annual * 100, 2),
        "cum_realized_pct": round(cum * 100, 2),
        "cum_annualized_pct": round(cum_annual * 100, 2),
        "pct_negative": round(neg / n * 100, 1),
        "pct_positive": round(pos / n * 100, 1),
        "worst8h_pct": round(min(rates) * 100, 4),
        "best8h_pct": round(max(rates) * 100, 4),
    }

def main():
    results = []
    for s in SYMBOLS:
        rows = fetch(s)
        a = analyze(s, rows)
        if a:
            results.append(a)
            print(json.dumps(a, ensure_ascii=False))
    out = {"generated": time.strftime("%Y-%m-%d %H:%M"), "cost_roundtrip_pct": RT_COST * 100,
           "note": "読取のみ・発注なし。価格中立前提の受取キャリー。借入なし。",
           "results": results}
    with open(__file__.replace("funding_carry_probe.py", "funding_carry_result.json"),
              "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("SAVED funding_carry_result.json")

if __name__ == "__main__":
    main()
