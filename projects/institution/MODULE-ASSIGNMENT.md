---
doc_id: AURELIAN-MODULE-ASSIGNMENT-v1
tags: [institution, modules, assignment]
type: module-assignment
rank: 憲章直下（各既存モジュールの正式所属）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# Aurelian — 既存モジュール正式所属表 v1

> **目的**: 既存 `AssetEmpire/empire/` の各モジュールを、機関組織図のどこに正式所属させるかを確定する。**コードは一切変更しない**。所属を定義する台帳としての文書。
> **凡例**: 【確認済】=README/コード/稼働ログで実在確認 / 【推測】=構成から推定・要精査。

---

## Institutional Core（機関共通基盤 = 旧AssetEmpire共通基盤）

| モジュール | パス（empire/配下） | 役割 | 状態 | 確度 |
|---|---|---|---|---|
| 統合台帳 ledger | `ledger/` | 唯一の真実源・追記専用・ハッシュ連鎖・任意時点リプレイ・日次突合 | 骨格 | 【確認済】 |
| 防衛司令 defense | `defense/risk_engine.py` 他 | 段階デッドマン(-8/-12/-15%)・ファクター集約・全停止権限 | 骨格 | 【確認済】 |
| 信号バス bus | `bus/signal_bus.py` | TTL/topic 付き信号配信 | 骨格 | 【確認済】 |
| 資本アロケータ allocator | `allocator/capital_allocator.py` | PSR×テールペナルティ補正・昇格遅/降格速・月次±20% | 骨格 | 【確認済】 |
| 観測所 observatory | `observatory/regime.py`, `divergence_recorder`, `heartbeat`, `notifier` | レジーム判定・乖離記録・生存信号・通知 | 一部稼働 | 【確認済】 |
| 執行ゲートウェイ execution | `execution/gateway.py`, `mt5_live.py`, `sizing.py`, `tca.py` | 決定的発注・二重ロック・FLOOR丸め・約定コスト分析 | 一部稼働 | 【確認済】 |
| 研究 research | `research/edges.py` | 仮説先行のエッジ探索 | 骨格 | 【確認済】 |
| 進化 evolution | `evolution/ai_soldier`, `backtest`, `coroner`, `evolve` | ソルジャー生成・検証・敗戦分析・進化 | 骨格 | 【確認済】 |

---

## Proprietary Investment Division（自己勘定投資部門）

| モジュール | パス | 役割 | 状態 | 確度 |
|---|---|---|---|---|
| ETH自律枠 | `scripts/autopilot.py` + `run_eth_autopilot.bat` | ETH実弾自律。2026-07-30 会長GOで **武装解除**（口座27972608=会長裁量口座と衝突）。タスクは毎時稼働だが live:false で実弾発注なし（paper計算のみ）。 | **武装解除 DISARMED** | 【確認済】 |
| BTC枠 | autopilot 内 sleeve | BTC枠（武装解除 live:false） | 骨格 | 【確認済】 |
| LTC枠 | autopilot 内 sleeve | LTC枠（武装解除 live:false） | 骨格 | 【確認済】 |
| 日足ソルジャー群(11) | `scripts/run_trading_cycle.py` | 日足戦略 paper 実行 | 稼働・paper | 【確認済】 |
| 4h暗号ソルジャー群(8) | `scripts/run_trading_cycle_4h.py` | 4時間足暗号 paper 実行 | 稼働・paper | 【確認済】 |
| trackA戦略群 | `strategies/trackA_*` | Track A 戦略 | 骨格 | 【推測】 |
| squads | `squads/fx_trend, hourly_trend, carry, cross_sectional, mean_reversion` | 戦略分隊 | 骨格 | 【確認済】 |

> ⚠️ **会長確認待ち**: `autopilot_state.json` の `day_start_equity=25000` が、どの口座を指すか未確定（$25kはプロップ口座額と一致）。口座同定は会長の確認事項。AURELは読取のみで踏み込まない。

---

## Prop Trading Division（プロップ事業部門・読取専用）

| モジュール | パス | 役割 | 状態 | 確度 |
|---|---|---|---|---|
| G4 チャレンジ一式 | `scripts/g4_*.py` | FundingPips 2-Step dry-run 実行・計画生成・heartbeat・watchdog | 稼働・dry | 【確認済】 |

> **保護境界**: `g4_` プレフィックス。詳細は DIVISION-PROP.md。機関からは**読取専用**。コード・データ・プロセス・タスク・venv・ログ形式を一切変更しない。

---

## UI / ダッシュボード

| ファイル | 役割 | 所属 | 変更可否 |
|---|---|---|---|
| `C:\Users\user\aurel_life.html` | AUREL人格UI（163KB） | Chairman Navigation Layer（人格窓） | **変更禁止**（const sharedU 事故歴） |
| `empire/data/dashboard.html` | 投資ダッシュボード（24KB） | Chairman Navigation Layer | 大規模改修禁止（今回範囲外） |
| `empire/data/g4_dashboard.html` + `g4_public.png` | プロップ盤 | Prop Division（読取専用） | **変更禁止**（g4_境界） |

---

## 改定
- v1（2026-07-30）: 初版。README・稼働ログ・config/state 実読に基づく。
