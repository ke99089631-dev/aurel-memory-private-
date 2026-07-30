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

## 3. 会長確認待ち（未解決・重要）

⚠️ `empire/data/autopilot_state.json` の `day_start_equity = 25000.0` がどの口座残高を指すか未確定。
- $25,000 は**プロップ・チャレンジ口座額と一致**する（偶然か、同一MT5口座を参照しているか不明）。
- 過去記録では Vantage Live 口座は $53 規模だった。
- **AURELは読取専用の原則により、これ以上口座を探らない**。口座同定は会長の確認事項として INSTITUTION-STATUS.md に掲示。

---

## 4. 変更禁止事項（今回範囲）
- 実弾設定（config/state）の変更禁止。
- 実行中プロセス（autopilot.py）の停止・再起動・変更禁止。
- タスクスケジューラの変更禁止。
- 本規程は**登録・文書化のみ**であり、稼働システムへ一切干渉しない。

---

## 改定
- v1（2026-07-30）: 初版。config/state 実読に基づく登録。
