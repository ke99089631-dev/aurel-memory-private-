# 畑A 変更記録 2026-11-28 「金額リスクを台帳に見えるようにする」(会長GO「畑Aは実行してくれ」)

## 何を変えたか(farm_a_exec.py・2か所だけ)
1. `lot_for()` — **返すロットの値は一切変えていない**。`self.last_risk` に次を入れるだけ追加:
   `risk_budget_usd`(0.4%の予算) / `lot_wanted`(予算どおりなら出るロット) / `lot_min` / `lot_step` /
   `floored_by_min`(最小ロットの床で切り上がったか) / `risk_usd_actual`(実際に賭かった金額) /
   `risk_pct_actual`(口座の何%) / `over_budget_x`(予算の何倍) / `usd_per_R`(1Rの値段)
2. 発注記録(`mode:"fire"`)に `base.update(sess.last_risk)` を1行足し、画面表示に1Rの値段を出した。

**変えていないもの**: ロットの値・撃つ/撃たないの判断・SL/TP・同時本数・NY時間帯の条件・凍結仕様G0。
つまり**成績に影響する分岐はゼロ**。台帳に列が増えるだけ。

## なぜ(事実)
`lot_for()` のリスク比例(口座0.4%/トレード)は**元から正しく書かれていた**。効いていなかったのは
`max(volume_min, ...)` の床。NAS100.r の最小ロット0.1に対し、予算どおりのロットは0.016〜0.056しか出ない。
結果 **32本/32本が最小ロットの床**で、1本あたりの実際のリスクは **8.9〜74.4ドル=口座の0.7〜6.0%**
(設計は0.4%)。だから R の合計(+4.64)と口座の損益(-176ドル)が別物になった。

同じ病気が肥料の実弾でも起きていた(R-03「残高110USDでlot0.01が床=2%ルールが効かない」)。
**口座が小さいと、どんなに正しいリスク式を書いても床に負ける。**

## 元に戻し方(バックアップを取る前に編集したため手順で残す)
`lot_for()` を次に戻し、`base.update(getattr(sess,"last_risk",None) or {})` の行と print の追記を消す:

```python
    def lot_for(self, risk_price):
        mt5 = self.mt5
        ai = mt5.account_info(); si = mt5.symbol_info(self.sym)
        try:
            tick_val = si.trade_tick_value; tick_sz = si.trade_tick_size
            val_per_price = tick_val / tick_sz
            risk_usd = ai.balance * RISK_FRAC
            if risk_price <= 0 or val_per_price <= 0:
                return float(si.volume_min or 0.01)
            lot = risk_usd / (risk_price * val_per_price)
            step = si.volume_step or 0.01
            lot = max(si.volume_min or 0.01, round(lot / step) * step)
            return float(min(lot, si.volume_max or lot))
        except Exception:
            return float(getattr(si, "volume_min", 0.01) or 0.01)
```
元のprint: `print("[発注%s] %s lot%.2f SL%.2f TP%.2f ret=%s" % ("OK" if ok else "NG", side, lot, sl, tp, getattr(r, "retcode", None)))`

## 採点の切り替え(会長GO分)
畑Aの採点を**金額ベース**に移した。正本 `farm_a_money_report.py` → `RESULTS_farm_a_money.md`(読取のみ)。
Rは型の診断用として残す。関連: メモリ r-positive-money-negative-size-the-risk / LEARNING.md 2026-11-28。

## やっていないこと(意図的・会長の判断待ち)
- 「金額リスクが予算のN倍を超える本は撃たない」ガード。**撃つ本を選ぶ変更=型を触ること**になり、紙との鏡も壊れる。
  会長の方針「全部撃って理由を浮かばせる」とも衝突するので提案だけに留めた。
- 最小ロットそのものの回避(別の銘柄/別のCFDサイズ)。
