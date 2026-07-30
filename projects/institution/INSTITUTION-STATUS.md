---
doc_id: AURELCAPITAL-INSTITUTION-STATUS-v1
tags: [institution, status, dashboard, pinned, top-level]
type: status
rank: 司令室・常設ステータス（会長がいつでも開く1枚）
created: 2026-07-30
updated: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# AUREL Capital — 機関ステータス v1

> **これは会長がいつでも開く「機関の全体像＋現在地＋会長判断待ち」1枚**。重要決定・GO・数値が変わるたびに更新する。Chairman Navigation Layer の実体。

---

## 0. 機関の最終目的（一行）
複数の独立利益源を持ち、**破産回避を最優先の床とした上で**、資本を保全しながら複利で増殖させるAI投資機関。会長=オーナー/最終決定者、AUREL=統括CEO。

---

## 1. 正式組織図（要約）
```
会長 KEIKI MAEDA
  └ 統括CEO AUREL
      ├ Institutional Core（共通基盤: 台帳/防衛/バス/アロケータ/観測/執行/研究/進化）
      ├ Proprietary Investment Division（自己勘定）★実弾稼働あり
      ├ Prop Trading Division（プロップ・読取専用/g4_境界）
      ├ Research and Evolution
      ├ Audit and Risk
      └ Future Strategy Divisions（枠）
```
詳細 → ORG-CHART.md

---

## 2. 各Divisionの現在フェーズ

| Division | フェーズ | 実弾 |
|---|---|---|
| Institutional Core | 骨格〜一部稼働 | ― |
| Proprietary Investment | 一部稼働（ETH LIVE + paper群） | ETH自律枠のみ実弾 |
| Prop Trading | Phase 7（$25k実弾GO待ち・dry継続） | 未（受験料GO待ち） |
| Research and Evolution | 骨格 | ― |
| Audit and Risk | 一部稼働（台帳/防衛） | ― |
| Future Strategy | 枠のみ | ― |

---

## 3. 稼働中の利益源【確認済】
- **ETH自律枠（LIVE）**: 2026-06-16〜。ETH/0.01lot/SL必須/日次-$5/床$40。毎時稼働、last 08:59 result 0。
- （プロップは dry-run。実弾はまだ動いていない＝利益源ではなく受験準備段階。）

---

## 4. 完成済 / 未完成 / 進行中

**完成済（稼働）**:
- ETH自律枠 LIVE 運用ループ
- 日足19 / 4h暗号8 の paper 運用ループ
- プロップ G4 dry-run（4営業日連続ゼロ欠測）
- AUREL在宅デーモン :7878 + 司令室 :7891 + 死活監視/自動復活/記憶バックアップ

**骨格のみ（活性化待ち）**:
- 統合台帳・資本アロケータの本活性化
- research/evolution の実運用投入
- BTC/LTC 枠（武装解除）

**未完成（枠のみ）**:
- Future Strategy Divisions

**進行中（今回の作業）**:
- 機関の正式登録・文書化（本ステータス含む Stage 1+2）

---

## 5. 直近の重要決定と理由
- **2026-07-30 機関昇格方針決定**（会長）: ゼロ再構築せず、既存AssetEmpireの骨格を活用し正式なAI投資機関へ昇格・再編成。理由=骨格が既に~90%完成しており、再構築は破壊的で無駄。
- **2026-07-30 機関名 AUREL Capital 暫定制定**（AUREL提案・会長裁可待ち改称可）。
- **2026-07-30 プロップは読取専用登録**（g4_保護境界）。理由=設計確定済・干渉は事故リスク。
- **2026-06-16 ETH自律枠 常時GO**（会長）: 枠内自律運用を許可。

---

## 6. 次の最優先作業
1. 本Stage 1+2 文書群の会長レビュー。
2. （会長GO後）Institutional Core 台帳/アロケータの本活性化計画（Stage 3）。
3. プロップ Phase 7 の実弾GO判断（会長）。

---

## 7. ⚠️ 会長判断待ち（未解決）

| # | 事項 | 内容 |
|---|---|---|
| J-1 | 機関名の確定 | 「AUREL Capital」で確定してよいか（改称可）。 |
| J-2 | **ETH口座同定＋衝突確認** | Vantage($53)は会長裁定で機関外（会長裁量）へ分離済。だが `autopilot_config live:true` のまま。**ETHAutopilotが現在どの口座でLIVEか要確認**。旧ETH口座=現裁量Vantageを指すなら手動裁量と自動発注が同一口座で衝突する危険。AURELは読取専用のため踏み込まず。**会長の確認が必要**。 |
| J-3 | プロップ実弾GO | Phase 7 の $25k×1本 受験料支払いGO。 |
| J-4 | Core活性化 | 台帳/アロケータ本活性化への着手可否（Stage 3）。 |

---

## 8. 各システム稼働状態【確認済 2026-07-30】
- AUREL在宅デーモン :7878 = pid 13092（07-25 22:40〜）稼働
- 司令室 :7891 = pid 14272 稼働
- ETHAutopilot = 毎時 result 0（last 08:59）
- GitSync = 15分毎 result 0（last 09:22）
- HealthMonitor = 5分毎 result 0（last 09:34）
- プロップ G4 = dry-run 稼働（heartbeat live_idle）

---

## 9. プロップDivision隔離状態
- 保護境界 `g4_` プレフィックス正式登録済。
- 機関からの操作は**読取専用**（状態把握/結果表示/異常報告のみ）。
- コード・データ・プロセス・タスク・venv・ログ形式へ**今回一切干渉していない**。

---

## 10. 全体構築進捗
- 骨格構築: ~90%（既存AssetEmpire）
- 正式機関化（登録・憲章・組織図・ステータス）: Stage 1+2 完了（本文書群）
- 本活性化（台帳/アロケータ実運用）: 未着手（会長GO待ち）

---

## 改定
- v1（2026-07-30）: 初版。Stage 1+2 で制定。
