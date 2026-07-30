---
doc_id: AURELCAPITAL-DIVISION-PROPRIETARY-v1
tags: [institution, division, proprietary, self-account]
type: division-charter
rank: 第3層（Division個別規程）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# Proprietary Investment Division（自己勘定投資部門）規程 v1

> **上位**: AI投資機関憲章 v1 / 自己勘定系運用憲章
> **目的**: 会長の自己資本で運用する投資部門。現時点で唯一の**実弾稼働利益源（ETH自律枠）**を含む。

---

## 1. Division の構成

| 枠 | 実弾状態 | 規律 |
|---|---|---|
| ETH自律枠 ETHAutopilot | **LIVE**（2026-06-16〜・会長常時GO） | ETHのみ / 0.01 lot / SL必須 / 日次-$5停止 / 床$40 / magic 770611 |
| BTC枠 | 武装解除（live:false） | 活性化には会長の最終GO必須 |
| LTC枠 | 武装解除（live:false） | 活性化には会長の最終GO必須 |
| 日足ソルジャー群(11) | paper | 昇格ゲート通過＋会長承認で極小実弾へ |
| 4h暗号ソルジャー群(8) | paper | 同上 |

---

## 2. ETH自律枠の運用規律（自己勘定系運用憲章の体現）

【確認済】`empire/data/autopilot_config.json` より：
- `live: true`, `live_since: 2026-06-16`
- eth sleeve: `live:true`, `vol 0.01`, `sl 0.01`, `tp 0.02`, `magic 770611`
- btc/ltc sleeve: `live:false`
- `floor_usd: 40.0`, `daily_loss_usd: 5.0`
- 実行: `run_eth_autopilot.bat`（毎時 autopilot.py + emit_empire_status.py）

### 会長常時GOの範囲（憲章 第8条）
会長の常時GO（2026-06-16）は、**コード側で固定された上記の枠内でのみ有効**。枠を超える変更（ロット増・銘柄追加・床引下げ・BTC/LTC武装）は、その都度の会長の最終GOを要する。

---

## 3. 口座の区分（会長裁定 2026-07-30）

### 機関外（会長個人裁量）— 機関の管理対象から分離
- **Vantage $53 口座**: もともとETH実弾に使っていた口座。**現在は会長が裁量トレードで使用**。
- → **機関（AUREL Capital）の管理・運用対象から分離**する。自己勘定Divisionの資産に含めない。AURELは干渉しない。

### ⚠️ 新たな会長確認待ち（重要）
`empire/data/autopilot_config.json` は `live:true` のままで、`autopilot_state.json` の `day_start_equity = 25000.0`。
- Vantage($53)が会長裁量に移った以上、**ETHAutopilot が現在どの口座に対してLIVEなのか要確認**。
  - もし旧ETH口座（＝現・会長裁量Vantage）を今も指しているなら、**会長の手動裁量と自動発注が同一口座で衝突する**危険がある（要即確認）。
  - $25,000 はプロップ・チャレンジ口座額と一致するが、同一口座参照かは不明。
- **AURELは読取専用の原則により、これ以上口座を探らない**。口座同定と衝突有無の確認は会長の判断事項として INSTITUTION-STATUS.md に掲示。

---

## 4. 変更禁止事項（今回範囲）
- 実弾設定（config/state）の変更禁止。
- 実行中プロセス（autopilot.py）の停止・再起動・変更禁止。
- タスクスケジューラの変更禁止。
- 本規程は**登録・文書化のみ**であり、稼働システムへ一切干渉しない。

---

## 改定
- v1（2026-07-30）: 初版。config/state 実読に基づく登録。
