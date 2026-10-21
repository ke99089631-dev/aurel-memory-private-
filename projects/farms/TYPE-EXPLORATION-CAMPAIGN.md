---
tags: [project/investment, farm, campaign, pinned]
type: campaign
created: 2026-10-21
updated: 2026-10-21
owner: AUREL
audience: 会長(KEIKI MAEDA)
---

# 🧪 型探索キャンペーン（畑を増やす作業）

> 2026-10-21 会長GO「金で使った物を全て未検証・効きそう順でUS100等に掃く→済んだら別の型」。AURELに一任。
> 規律(不変): 今日と同じ関門=コスト後・70/30 OOS・Sharpe≥0.25・BH-FDR。通ったものだけ畑/改善に昇格。金ゼロ・読取のみ。
> 狙い: 連動しない優位を増やす=束ねて年率の天井を上げる(単一型は1桁〜十数%が限界)。

## フェーズ1 — 金で使った壁→壁レーンをUS100/S&Pで総なめ（効きそう順）
| # | レーン | 中身 | エンジン | 状態 |
|---|---|---|---|---|
| 1a | **外壁 調整** | 保ちタッチN×TP×SL スイープ | touch_test | ⏳実行中(sweep_us100_tune.py) |
| 1b | **中壁(青)×戻り** | 箱の中間壁で発火=別location=準非連動の新レーン | setup_engine | ⬜次 |
| 1c | **再加速/飛び乗り** | reaccel(戻り後の再加速トリガ)・chase(ブレイク即) | setup_engine | ⬜ |
| 1d | **時間軸/セッション** | M15・H1 / ロンドン・全時間 | touch_test | ⬜ |

## フェーズ2 — 別の型（新規・最も非連動）
- 逆張り(fade): 壁で跳ね返す=順張り畑と逆の値動き=分散が最大。
- 平均回帰・レンジ型など。

## 収穫ルール
- 関門通過×現farm(US100/S&P)と**低相関** → 新しい畑に昇格(別の観測レーン→デモ→実弾)。
- 関門通過だが高相関 → 既存畑の改善として採用検討(出口/選別)。
- 落選 → 棚卸し記録のみ(対照群)。

## 現farm基準(超える相手)
- 畑A US100: 保ち2回・TP0.85・SL0.33・NY = n2828 OOS平均R+0.080 Sharpe+0.63。
- 畑B S&P500: 同 = +0.045 / Sharpe0.35(単体)。束ね(保ち3回)Sharpe0.75。

## 🔗 マップ: `projects/INVESTMENT-DIVISION-MAP.md` / 畑A仕様: `farms/FARM-A-US100-SPEC.md`
結果: `AssetEmpire/empire/research/wall_to_wall/RESULTS_sweep_*.md`
