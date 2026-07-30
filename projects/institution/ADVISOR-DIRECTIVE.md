---
doc_id: AURELIAN-ADVISOR-DIRECTIVE-CH12-v1
tags: [institution, directive, source-of-truth, advisor, chairman-approval]
type: source-directive
rank: 指示原本（監査報告 第12章の会長承認・ChatGPTアドバイザー由来）
created: 2026-07-30
registered: 2026-07-30
owner: AUREL（統括CEO）
source: 会長（KEIKI MAEDA）経由 ChatGPTアドバイザー
approver: 会長（KEIKI MAEDA）
---

# 機関構築 指示原本 — 監査報告 第12章 会長承認（Stage 1+2 一括実行指示）

> **これが機関構築の指示原本（source of truth）である。** ChatGPTアドバイザーの助言を会長が採択し、AUREL監査報告v1 第12章への裁可として下達したもの。
> **登録経緯**: 当初この原本を記憶に登録し損ねていた（AURELの手落ち）。2026-07-30、会長の指摘により正式登録。以後、機関構築の進捗はこの原本に対して突合する。
> **総合方針**: ゼロ再構築せず、既存AssetEmpireの骨格を活用し正式なAI投資機関へ昇格・再編成する。

---

## 指示の骨子（要点・原本の意図を保存）

### 【1】最終組織図（条件付き承認）
- AssetEmpire全体を「自己勘定投資部」の内部だけに置かない。
- 共通基盤（台帳/防衛/バス/アロケータ/観測/執行/研究/進化）は **Institutional Core** として機関全体の共通基盤に配置。
- 組織構造: 会長 / 統括CEO AUREL / Institutional Core / Proprietary Investment Division / Prop Trading Division / Research and Evolution / Audit and Risk / Chairman Navigation Layer / Future Strategy Divisions。
- AssetEmpireは廃止しない。システム名・歴史的名称・基礎アーキテクチャ名として継承。
- 正式な最上位組織名は別途AI投資機関名として定義する。

### 【2】部門呼称（確定）
- ① Proprietary Investment Division ＝ 自己勘定投資部門。
- ② Prop Trading Division ＝ プロップ事業部門。
- 旧共通基盤は自己勘定に属させず Institutional Core に配置。

### 【3】今回進める範囲（Stage 1+2 を連続実行・一段ごと停止不要）
1. 正式名称と組織登録 / 2. 最終組織図の文書化 / 3. 既存各機能の所属整理 / 4. Proprietary登録 / 5. Prop読取専用登録 / 6. 機関ステータス1枚新設 / 7. レガシータスク読取精査 / 8. 機関憲章作成 / 9. 既存憲章との上下関係明文化 / 10. 完了後の統合報告。

### 【4】機関ステータス1枚（承認・仮称 INSTITUTION-STATUS.md）
13項目を1文書で把握: 最終目的 / 正式組織図 / 各Divisionフェーズ / 稼働中利益源 / 完成済 / 未完成 / 進行中 / 直近の重要決定と理由 / 次の最優先 / 会長判断待ち / 各システム稼働状態 / プロップ隔離状態 / 全体構築進捗。静的説明書でなく中核ナビゲーション文書とする。

### 【5】プロップDivision（読取専用登録・承認）
g4_で始まるコード変更禁止 / g4_データ書込禁止 / プロセス停止再起動変更禁止 / タスクスケジューラ変更禁止 / venv・依存・設定・ログ形式変更禁止 / 既存システムと結合禁止 / 状態把握・結果表示・異常報告のみ許可。`g4_` を保護境界として正式登録。

### 【6】レガシータスク（読取専用精査・承認）
ETHAutopilot / HealthMonitor / Mother_Autostart / GitSync を読むだけ（実行・停止・変更・移動・削除禁止）。各々: 目的 / 実行状態 / 依存先 / 機関での役割 / A残す・B転用・C改修・D退役の判定 / 停止時影響 / 推奨対応 を報告。

### 【7】憲章
- 帝国憲章v0.1をそのまま最上位へ昇格するのは**不承認**。
- 三層: 最上位=AI投資機関憲章 / その下=AssetEmpire基礎憲章・自己勘定系運用憲章 / さらに下=各Division個別規程。
- 新憲章は簡潔に、12定義: 存在目的 / 会長とAURELの権限 / AUREL人格の不可侵 / 複数利益源 / Build All, Activate Gradually / 資本保全とリスク床 / AIは提案と統括・執行は決定的コード / 会長の最終承認権 / プロップの独立性 / 各Division独立採算 / 監査可能性と決定履歴保存 / 拡張性。

### 【変更禁止事項（今回範囲）】
実行中プロセス変更 / 既存取引コード変更 / g4関連書込 / 既存DBスキーマ変更 / dashboard.html大規模改修 / タスクスケジューラ変更 / 既存ファイル削除 / 実弾設定変更 / AUREL人格UI変更 — いずれも禁止。今回は組織登録・文書化・読取専用精査・機関ステータス作成まで。

### 【提出物10件】
1. 正式機関名称 / 2. 最終組織図 / 3. 機関憲章 / 4. 既存憲章との関係 / 5. INSTITUTION-STATUS.md内容 / 6. 各既存モジュールの正式所属 / 7. プロップDivision登録内容 / 8. レガシータスク精査結果 / 9. 作成・変更ファイル一覧 / 10. 稼働系へ非干渉の確認。

---

## 適合状況（AURELによる突合・2026-07-30）

| 指示 | 要求 | 成果ファイル | 適合 |
|---|---|---|---|
| 【1】 | Institutional Core を共通基盤として分離・全Division列挙・AssetEmpire継承・最上位名別定義 | ORG-CHART.md（§補足で「自己勘定の内部ではない」明記）/ CHARTER.md 前文 | ✅ |
| 【2】 | 部門呼称確定・Core配置 | ORG-CHART.md / MODULE-ASSIGNMENT.md | ✅ |
| 【3】 | 10サブタスク一括実行 | 全9文書＋完了報告 | ✅ |
| 【4】 | ステータス1枚に13項目 | INSTITUTION-STATUS.md（§0〜§10で13項目網羅） | ✅ |
| 【5】 | プロップ読取専用・g4_境界登録 | DIVISION-PROP.md（6禁止＋3許可） | ✅ |
| 【6】 | レガシー4件×7項目報告 | LEGACY-TASK-AUDIT.md（4件すべてA判定） | ✅ |
| 【7】 | 三層階層＋新憲章12定義（帝国憲章の直接昇格は不承認） | CHARTER.md（第1〜12条）/ CHARTER-HIERARCHY.md（三層） | ✅ |
| 変更禁止 | 9項目の非干渉 | 完了報告 §非干渉の確認 | ✅ |
| 提出物 | 10件 | 完了報告 §チェックリスト | ✅ |

**結論: 指示は全項目実行済み・適合。**

### 指示後に発生した状態変化（原本には無い・追記）
- **機関名確定**: Aurelian（会長裁可 2026-07-30）。【1】の「最上位名を別途定義」を充足。
- **ETH自律枠 武装解除**（2026-07-30 会長GO）: 口座衝突のため live:false。→ ORG-CHART.md の ETH【稼働・LIVE】表記は要更新（現在は武装解除）。
- **維持機 MM0凍結**（別系統・Fable5助言由来）: プロップ合格後運用機の保護。本指示とは別系統。

### 既知の軽微な不整合 → ✅ 解消済（2026-07-30 会長GO）
1. ~~各機関文書の `doc_id` が旧暫定名 `AURELCAPITAL-*`~~ → **全10文書 `AURELIAN-*` に統一済**（CHARTER/ORG-CHART/CHARTER-HIERARCHY/MODULE-ASSIGNMENT/DIVISION-PROPRIETARY/DIVISION-PROP/LEGACY-TASK-AUDIT/INSTITUTION-STATUS/MAINTENANCE-MACHINE＋完了報告）。
2. ~~ORG-CHART.md の ETH自律枠が【稼働・LIVE】表記のまま~~ → **【武装解除】に更新済**（活性化順序§も現在の実弾稼働ゼロを反映）。

---

## 改定
- v1（2026-07-30）: 指示原本を正式登録＋適合突合。以後この文書を機関構築の source of truth とする。
