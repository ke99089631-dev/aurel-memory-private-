---
doc_id: AURELIAN-LEGACY-TASK-AUDIT-v1
tags: [institution, audit, legacy-tasks, read-only]
type: audit
rank: 憲章直下（レガシータスク精査結果）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# Aurelian — レガシータスク精査結果 v1（読取専用）

> **目的**: 常駐タスク/スケジュール系スクリプトを一つずつ読取のみで精査し、機関での役割とA〜E判定を確定する。
> **結論（先出し）**: **停止候補(D)はゼロ**。4件すべて稼働中かつ機関の中核インフラまたは実弾利益源。v1監査報告の暫定「D/要精査」を、実読により訂正する。

---

## 精査4件サマリ

| タスク | 目的 | 現在実行状態 | 機関での役割 | 判定 | 停止時影響 | 推奨対応 |
|---|---|---|---|---|---|---|
| ETHAutopilot | ETH実弾自律運用 | 稼働・LIVE（毎時, last 08:59 result 0） | Proprietary Div の唯一の実弾利益源 | **A 残す** | 実弾利益源が停止 | 現状維持・枠内運用 |
| HealthMonitor | :7878 死活監視・自動復活 | 稼働（5分毎, last 09:34 result 0） | AUREL在宅デーモンの生命維持 | **A 残す** | AUREL本体の自動復活が失われる | 現状維持（中核インフラ） |
| Mother_Autostart | logon時 aurel.mjs 起動 | 稼働（:7878 pid 13092） | AUREL在宅デーモンの起動器 | **A 残す** | 再起動後AURELが立ち上がらない | 現状維持（AUREL本体の一部） |
| GitSync | memory/ vault の commit+push | 稼働（15分毎, last 09:22 result 0） | 記憶の災害復旧 | **A 残す** | 記憶のバックアップ喪失 | 現状維持 |

---

## 各タスク詳細（読取確認済）

### 1. ETHAutopilot 【A 残す】
- **スクリプト**: `AssetEmpire\empire\scripts\run_eth_autopilot.bat` → `autopilot.py` + `emit_empire_status.py`（毎時）。
- **依存先**: 専用MT5端末・autopilot_config.json・autopilot_state.json。
- **状態**: LIVE（live_since 2026-06-16）。last_tick 08:59:03、result 0。
- **機関での役割**: Proprietary Investment Division の実弾稼働枠。
- **停止時影響**: 稼働中の唯一の実弾利益源が止まる。
- **推奨**: 現状維持。枠（ETH/0.01lot/SL必須/日次-$5/床$40）を超える変更のみ会長GO。

### 2. HealthMonitor 【A 残す】
- **スクリプト**: `.aurel\daemon\health-monitor.ps1`。
- **挙動**: 5分毎に `:7878/api/health` を ping、失敗で mother-autostart 経由で復活。3連続失敗→30分クールダウン、last-death.json 記録。
- **機関での役割**: AUREL在宅デーモン（機関の中枢神経）の生命維持装置。
- **停止時影響**: AUREL本体が落ちても自動復活しなくなる（過去の週2欠測の再来リスク）。
- **推奨**: 現状維持。中核インフラ。

### 3. Mother_Autostart 【A 残す】
- **スクリプト**: `.aurel\boot\mother-autostart.ps1`。
- **挙動**: logon時に `aurel.mjs --bind 0.0.0.0` を :7878 で起動。listening ならスキップ。
- **状態**: :7878 pid 13092（07-25 22:40〜稼働）。
- **機関での役割**: AUREL在宅デーモンの起動器＝AUREL本体の一部。
- **停止時影響**: 再起動後にAURELが自動起動しない。
- **推奨**: 現状維持。

### 4. GitSync 【A 残す】
- **スクリプト**: `.aurel\starter-kit\git-sync.ps1`。
- **挙動**: 15分毎に memory/ vault を commit+push（災害復旧）。`git -c user.email=ke99089631@gmail.com`。
- **機関での役割**: 機関の記憶（統括CEOの永続記憶）の遠隔バックアップ。
- **停止時影響**: 記憶のバックアップが止まる（マシン故障時に記憶喪失リスク）。
- **推奨**: 現状維持。

---

## 訂正記録
- v1監査報告書（Ch.12前）では上記の一部を暫定「D/要精査」としていた。**実読の結果、D判定は撤回**。4件すべてA（残す）。稼働システムへ干渉せず読取のみで確認。

## 改定
- v1（2026-07-30）: 初版。全4スクリプト＋config/state 実読に基づく。
