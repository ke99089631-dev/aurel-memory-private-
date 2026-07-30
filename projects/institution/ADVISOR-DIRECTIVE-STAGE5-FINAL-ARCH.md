---
doc_id: AURELIAN-ADVISOR-DIRECTIVE-STAGE5-FINALARCH-v1
tags: [institution, directive, source-of-truth, stage5, final-architecture, master-plan]
type: source-directive
rank: 指示原本（修正Stage 5・Aurelian最終機関設計）
created: 2026-07-30
registered: 2026-07-30
owner: AUREL（統括CEO）
source: 会長（KEIKI MAEDA）経由 ChatGPTアドバイザー
approver: 会長（KEIKI MAEDA）
supersedes_scope: 旧Stage 5「実弾運用基盤・資本口座設計」は一旦保留
---

# 機関構築 指示原本 — 修正Stage 5：Aurelian Final Institution Architecture

> **これは修正Stage 5の指示原本（source of truth）。** Stage 1〜4 の成果（憲章・Institutional Core・状態管理・中央司令画面・Audit and Risk・Prop隔離）は**有効・撤回しない**。ただし今後の構築軸を修正する。
> **軸の修正（核心）**: 現在ある AssetEmpire / G4プロップ / EA群 を中心に Aurelian の最終形を考えてはならない。Aurelian は当初から**複数市場・複数戦略・複数部署・複数利益源・AI社員・研究・監査・資本配分・執行**を持つ総合AI投資機関。**Prop Trading Division は中心ではなく、複数ある利益事業部の一つ**。
> **旧Stage 5 保留**: 「実弾運用基盤・資本口座設計」は一旦保留。
> **修正Stage 5 名称**: Aurelian Final Institution Architecture（Aurelian最終機関設計・全体構築マスター計画）。
> **目的**: 現在あるシステムから組織を組み立てるのではなく、**Aurelianの本当の最終形態を先に設計し、その中へ既存資産を配置する**。

---

## 1. 最終機関図の再設計（上位Group）
1. Executive and Governance Group
2. Institutional Core
3. Investment Business Group
4. Research and Intelligence Group
5. Risk, Audit and Compliance Group
6. Technology and Operations Group
7. Chairman Navigation Layer

**Investment Business Group の最低Division枠**（稼働未でも正式枠として先に登録）:
Proprietary Quant Division / Prop Trading Division / Arbitrage Division / Macro and Global Markets Division / Crypto and Digital Assets Division / Equity Division / Commodity Division / Yield / Carry / Swap Division / Future Markets Division。

## 2. 階層の統一（混同しない）
`Group → Division → Desk → Strategy → Agent / Squad → Execution System`
- 例: Investment Business Group → Proprietary Quant Division → Trend Following Desk → Daily Trend Strategy → 日足兵 → paper execution。
- Prop Trading Division は **Division**。G4 はその配下の **Program / Strategy**。
- ETH Autonomous は Division ではなく **Strategy**。
- 日足19兵・4H兵は組織部門ではなく **Agent / Squad（Execution Unit）**。

## 3. 既存資産の再配置
全資産を新最終組織図へ再配置。対象（最低限）: AssetEmpire全モジュール / Institutional Core / 日足戦略群 / 4H戦略群 / ETH・BTC・LTC Autonomous / G4審査機 / Prop維持機 / Arsenal / Hermes / Gemini / Council / Research / Evolution / Audit and Risk / aurelian_command / institution_state / 既存dashboard群 / 自動化タスク / 記憶の家。
各資産について **現在所属 / 最終所属 / 組織階層 / 役割 / 現在状態 / 将来状態** を確定。

## 4. 最終機能一覧（現存有無に関係なく全列挙）
複数市場 / 複数時間軸 / 複数戦略 / 複数口座 / 複数ブローカー / プロップ会社別管理 / ポートフォリオ横断リスク / 資本配分 / 利益源評価 / 戦略の採用・降格・停止・退役 / 新戦略探索 / 市場レジーム判定 / 執行品質分析 / 異常検知 / 障害復旧 / AI会議 / 会長承認 / 意思決定履歴 / 監査 / セキュリティ / 研究 / 自己進化 / 会長中央司令UI / 日次週次月次運営 / 将来の新市場・新Division追加。

## 5. 現状との差分分析
最終形態を100%とし: 完成 / 一部完成 / 未着手 / 存在するが再配置要 / 重複 / 不足部署 / 不足Desk / 不足データ / 不足インフラ / 不足AI社員 / 不足統治機能 / 不足UI。
**完成率を単一の曖昧な数字で示さず、Group別・Division別・機能別に評価**。

## 6. 全体構築ロードマップ（最終形までのStage再設計）
プロップ合格やETH実弾化だけを中心にしない。少なくとも分離: Institutional Foundation / Investment Divisions / Research and Intelligence / Risk and Audit / Capital Allocation / Execution Infrastructure / AI Agent Organization / Central Command UI / Live Activation / Scale and Expansion。
各Stage: 目的 / 完成条件 / 既存資産の利用 / 新規構築物 / リスク / 会長判断。

## 7. 優先順位（Build All, Activate Gradually）
最終形の全構造を先に設計・登録。実装と起動は段階的。現存プロップ・EAに全体設計を引っ張らせない。
再評価順: 1.全体の器 → 2.共通基盤 → 3.可視化 → 4.研究・評価 → 5.各利益事業 → 6.実弾化 → 7.拡張。

## 8. 既存Stageの扱い（再定義）
- Stage 1〜2 = Institutional Foundation の一部。
- Stage 3〜4 = State Management / Governance / Command UI の初期基盤。
- Aurelian 全体の完成率をプロップや現存EAの数だけで計算しない。

## 今回の変更禁止
実弾化 / 再武装 / 資金移動 / 既存コード変更 / プロセス変更 / g4_関連への書込み / DB変更 / 既存Stage成果の削除 / 現在の組織文書の破壊的上書き。今回は**最終設計・再配置・差分分析・全体ロードマップ作成のみ**。

## 完了後の提出物（12件）
1. Aurelian最終組織図 / 2. Group/Division/Desk/Strategy/Agent/Execution 階層定義 / 3. 全既存資産の再配置表 / 4. 最終機能一覧 / 5. 現状との差分分析 / 6. Group別完成度 / 7. Division別完成度 / 8. 最終形までの全体Stageロードマップ / 9. 次に構築すべき最優先領域 / 10. プロップが独立事業部の一つであり中心ではないことの確認 / 11. 作成・変更ファイル一覧 / 12. 稼働システムへの非干渉確認。

---

## 改定
- v1（2026-07-30）: 修正Stage 5 指示原本を登録。旧Stage 5（実弾運用基盤・資本口座設計）は保留。
