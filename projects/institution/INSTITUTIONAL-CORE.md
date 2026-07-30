---
doc_id: AURELIAN-INSTITUTIONAL-CORE-v1
tags: [institution, core, stage4, responsibility-boundary, module-registry]
type: core-definition
rank: 憲章直下（機関共通基盤の正式定義・Stage 4）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: ADVISOR-DIRECTIVE-STAGE34.md（Stage 4）
---

# Institutional Core 正式定義 — Stage 4

> **上位**: ADVISOR-DIRECTIVE-STAGE34.md（Stage 3+4 指示原本）。本文書は Stage 4 の成果物。
> **一行**: Institutional Core は「機関が動くための技術基盤」。利益源ではない。全Divisionがこの上に乗る。
> **核心の区別**: Institutional Core は **実行する技術基盤**。Audit and Risk は **監督する統治部門**。この二つを混同しない。
> **非干渉**: 本文書は定義のみ。稼働コード・g4_・プロセス・DBスキーマは一切変更していない。

---

## 1. Institutional Core とは（正式定義）

Institutional Core は、AUREL Holdings 傘下 Aurelian の**機関共通基盤**である。旧 AssetEmpire の共通基盤（台帳・防衛・バス・アロケータ・観測・執行）を機関全体の下支えとして正式配置したもの。

- **自己勘定投資部門の内部ではない。** Proprietary と Prop の両方を下から支える。
- **Core 自体は利益を生まない。** 利益源を保有するのは Proprietary Investment Division と Prop Trading Division。
- **Core は6つのサブシステムから成る**: ledger / defense / bus / allocator / observatory / execution gateway。

平たく言うと — 銀行でいう「金庫・警備・電話交換・資金配分係・監視カメラ・出納窓口」の設備一式。お金を稼ぐ部署（トレード部門）はこの設備を使って稼ぐが、設備そのものは稼がない。

---

## 2. Core と Audit and Risk の責任境界（役割分離）

| | Institutional Core | Audit and Risk |
|---|---|---|
| 性質 | 技術基盤（実行する） | 統治部門（監督する） |
| やること | 記録・防衛・信号配信・資本配分・観測・執行ゲートを**実行**する | それらの設定・動作・結果・例外・違反・資本リスクを**監督**し、会長とAURELへ**報告**する |
| 権限 | 決められた通りに動く。判断はしない。 | 検査・警告・報告。実行はしない。 |
| 例 | ledger = 取引を記録するシステム | Audit = 記録の完全性（ハッシュ連鎖の断絶・欠測）を**検査する部署** |
| 例 | defense = デッドマン床を**執行するシステム** | Risk = 床の基準値と違反を**監督する部署** |

**所有関係**: Core は Aurelian が機関資産として所有する共通基盤。
**監督関係**: Core の6サブシステムはすべて Audit and Risk の監督下にある（下表 監督部署）。

この分離により「実行する者」と「検査する者」が分かれる（自己監査の排除）。

---

## 3. Core 6サブシステム 正式登録（各10項目）

### 3-1. ledger（統合台帳）
- **正式名称**: 統合台帳 Institutional Ledger
- **所属**: Institutional Core
- **目的**: 機関の唯一の真実源。全決定・全取引・全状態変化を追記専用で刻む。
- **入力**: 各Division・Coreからの記録要求（type / payload / agent / market / symbol / mode）
- **出力**: ハッシュ連鎖された不可変レコード列。任意時点リプレイ。日次突合結果。
- **実行権限**: 追記のみ（更新・削除不可）。金銭を動かす権限は持たない。
- **監督部署**: Audit and Risk
- **保護レベル**: 高（ハッシュ連鎖の完全性が機関の信頼の土台）
- **現在状態**: 骨格（本体存在・凍結専用台帳 institution_freeze_ledger.sqlite は稼働）
- **依存先**: なし（最下層）。他が ledger に依存する。
- **実体**: `empire/ledger/`（読取のみで確認）

### 3-2. defense（防衛司令）
- **正式名称**: 防衛司令 Defense Command
- **所属**: Institutional Core
- **目的**: 資本を守る最終防衛線。段階デッドマン(-8/-12/-15%)・ファクター集約・全停止。
- **入力**: 各Divisionの損益・エクスポージャ・リスク信号
- **出力**: 減額指示・凍結指示・全停止（キルスイッチ）指示
- **実行権限**: 停止・減額の**執行権**を持つ（守りの方向のみ・攻めの発注はしない）
- **監督部署**: Audit and Risk
- **保護レベル**: 最高（キルスイッチ・床は絶対に外さない）
- **現在状態**: 骨格
- **依存先**: ledger（記録）, observatory（信号）
- **実体**: `empire/defense/risk_engine.py` 他（読取のみ）

### 3-3. bus（信号バス）
- **正式名称**: 信号バス Signal Bus
- **所属**: Institutional Core
- **目的**: 部門・モジュール間の信号を TTL/topic 付きで配信する神経網。
- **入力**: 各モジュールが発する信号（topic + payload + TTL）
- **出力**: 購読側への期限付き信号配信
- **実行権限**: 配信のみ。金銭・発注の権限なし。
- **監督部署**: Audit and Risk
- **保護レベル**: 中
- **現在状態**: 骨格
- **依存先**: なし（横断基盤）
- **実体**: `empire/bus/signal_bus.py`（読取のみ）

### 3-4. allocator（資本アロケータ）
- **正式名称**: 資本アロケータ Capital Allocator
- **所属**: Institutional Core
- **目的**: 利益源へ資本をどう配るかを決める。PSR×テールペナルティ補正・昇格遅/降格速・月次±20%上限。
- **入力**: 各利益源の実績（PSR・テールリスク・稼働状態）
- **出力**: 各利益源への配分比率（提案）
- **実行権限**: 配分計算のみ。実弾の実行は執行ゲートウェイ経由＋会長GO必須。
- **監督部署**: Audit and Risk
- **保護レベル**: 高（資本配分は資本リスクに直結）
- **現在状態**: 骨格
- **依存先**: ledger（実績）, observatory（レジーム）
- **実体**: `empire/allocator/capital_allocator.py`（読取のみ）

### 3-5. observatory（観測所）
- **正式名称**: 観測所 Observatory
- **所属**: Institutional Core
- **目的**: 市場と機関自身を観る。レジーム判定・乖離記録・生存信号・通知。
- **入力**: 市場データ・各システムのheartbeat・実績と理論の乖離
- **出力**: レジーム区分・乖離アラート・生存/死活信号・会長への通知
- **実行権限**: 観測と通知のみ。停止権限は defense が持つ。
- **監督部署**: Audit and Risk
- **保護レベル**: 中
- **現在状態**: 一部稼働（heartbeat / notifier は実働）
- **依存先**: bus（信号配信）
- **実体**: `empire/observatory/regime.py, divergence_recorder, heartbeat, notifier`（読取のみ）

### 3-6. execution gateway（執行ゲートウェイ）
- **正式名称**: 執行ゲートウェイ Execution Gateway
- **所属**: Institutional Core
- **目的**: 決定を実際の発注に変える唯一の出口。二重ロック・FLOOR丸め・約定コスト分析。
- **入力**: 各Divisionの発注意図（戦略シグナル）
- **出力**: ブローカーへの決定的発注（LIVE時のみ）／paper・dry時は計算のみ
- **実行権限**: **実弾発注の唯一の実行点**。ただし `enable_live=True` かつ `arm_code='CHAIRMAN-GO'` かつ会長最終GO の三重ロック必須。runner は order_send を直接呼ばない。
- **監督部署**: Audit and Risk
- **保護レベル**: 最高（金銭が動く唯一の出口）
- **現在状態**: 一部稼働（paper/dry経路で稼働・LIVE経路は現在利益源ゼロ）
- **依存先**: allocator（配分）, defense（停止権）, ledger（記録）
- **実体**: `empire/execution/gateway.py, mt5_live.py, sizing.py, tca.py`（読取のみ）

---

## 4. 利益源と共通基盤の分離（確認）

| 区分 | 保有者 | 内容 |
|---|---|---|
| **共通基盤（利益を生まない）** | Institutional Core | ledger / defense / bus / allocator / observatory / execution gateway |
| **利益源（利益を生む）** | Proprietary Investment Division | ETH自律枠(武装解除) / BTC・LTC枠(武装解除) / 日足19 paper / 4h暗号8 paper |
| **利益源（利益を生む）** | Prop Trading Division | 審査機(dry-run) / 維持機(frozen・合格後運用) |

- **Core は Proprietary と Prop の両方を下から支える。** どちらか一方の内部には属さない。
- **Prop への接続は引き続き読取専用**。Core から `g4_` へ命令・書込みはしない（DIVISION-PROP.md の g4_ 境界を厳守）。
- 現在、**実弾で稼働している利益源はゼロ**（ETH武装解除後）。Core は稼働しているが、それは基盤であり利益ではない。

---

## 5. 研究・進化の位置づけ

`research/edges.py` と `evolution/*` は、MODULE-ASSIGNMENT.md 上は歴史的に Core 隣接として列挙されているが、Aurelian 組織図では **Research and Evolution Division**（利益源ではない研究部門）に所属する。Core の基盤（ledger/bus/observatory）を利用して仮説生成・敗戦分析・戦略進化を行う。利益源そのものではない。

---

## 6. 各既存モジュールの所属（参照）

Core 以外を含む全モジュールの正式所属表は **MODULE-ASSIGNMENT.md** を参照（本文書と整合済み）。本文書は Core 6サブシステムの深い定義（10項目）を担当し、MODULE-ASSIGNMENT.md は全体の所属一覧を担当する。

---

## 7. 非干渉の確認

- 稼働コード変更ゼロ・g4_ 書込ゼロ・プロセス停止/再起動ゼロ・タスクスケジューラ変更ゼロ・DBスキーマ変更ゼロ・dashboard/g4_dashboard/aurel_life.html 変更ゼロ。
- 本文書はすべて既存コード・README・稼働ログの**読取のみ**に基づく定義。

---

## 改定
- v1（2026-07-30）: Stage 4 として初版。Core 6サブシステムの正式定義・Audit and Risk との責任境界・利益源と基盤の分離を確定。
