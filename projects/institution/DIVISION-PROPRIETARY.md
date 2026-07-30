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
- → **機関（Aurelian）の管理・運用対象から分離**する。自己勘定Divisionの資産に含めない。AURELは干渉しない。

### ⚠️ ETH口座 衝突確認（2026-07-30 実測・機構確定）
【確認済・読取専用】ETHAutopilot（`autopilot.py`）の接続先を特定した：
- 接続先 = `C:\Users\user\ImperialFlow\.env` → **MT5ログイン 27972608 / サーバ VantageTradingLtd-Live**（パスワードは閲覧せず）。
- `autopilot_config.json` eth sleeve `live:true`。`autopilot.py` は runtime armコード不要で、**config の live:true だけで実弾発注**（会長の常時GO 2026-06-16 がconfigに焼き込まれている）。
- 挙動: 毎時、ETHにサインが出て資金可なら口座27972608に**本物の0.01ロットETH買い**（magic 770611・SL必須）。自分の建玉(magic770611)のみ管理し、会長の手動建玉は閉じない。
- `autopilot_state day_start_equity=25000` はこの口座で観測した当日基準（max(残高,エクイティ)）。

**⚠️ 会長への唯一の質問（J-2）**: ログイン **27972608** は、会長が今、手で（裁量で）取引しているVantage口座か？
- **YES** → 衝突。自動botが会長の裁量口座に0.01ロットETHを入れ続ける＋床/日次計算を共有。→ eth sleeve を `live:false` に武装解除するのが安全（config変更＝会長GO必須・AURELは無断変更しない）。
- **NO** → 別口座。衝突なし。現状維持でよい。

**AURELは読取専用の原則により、口座の同定・衝突判定は会長の回答を待つ。無断でconfigを変更しない。**

---

## 4. 変更禁止事項（今回範囲）
- 実弾設定（config/state）の変更禁止。
- 実行中プロセス（autopilot.py）の停止・再起動・変更禁止。
- タスクスケジューラの変更禁止。
- 本規程は**登録・文書化のみ**であり、稼働システムへ一切干渉しない。

---

## 改定
- v1（2026-07-30）: 初版。config/state 実読に基づく登録。
