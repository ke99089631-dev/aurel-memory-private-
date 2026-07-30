---
doc_id: AURELIAN-FINAL-ARCHITECTURE-v1
tags: [institution, final-architecture, master-plan, stage5, org-chart, hierarchy, roadmap]
type: master-architecture
rank: 最上位設計（Aurelian最終形態の器・全体構築マスター計画）
created: 2026-07-30
status: active（設計・段階活性化）
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: ADVISOR-DIRECTIVE-STAGE5-FINAL-ARCH.md
---

# Aurelian Final Institution Architecture — 最終機関設計マスター計画

> **原則**: Build All, Activate Gradually — **最終形の全構造を先に設計・登録し、実装と起動は段階的に行う**。
> **軸**: 現存の AssetEmpire / G4プロップ / EA群 から組織を組み立てない。**最終形を先に設計し、その器へ既存資産を配置する**。
> **プロップの位置づけ**: Prop Trading Division は Aurelian の中心ではなく、**Investment Business Group 内にある複数の利益事業部の一つ**。
> **完成率**: 単一の数字で測らない。Group別・Division別・機能別に評価する（→ GAP-ANALYSIS.md）。
> **既存資産の配置**: → ASSET-REPLACEMENT-MAP.md。差分と完成度: → GAP-ANALYSIS.md。

---

## 提出物1：Aurelian 最終組織図

```
会長 KEIKI MAEDA（オーナー・最終決定者）
│
├─ [G1] Executive and Governance Group（経営・統治）
│     └ 統括CEO AUREL / 憲章体系 / 意思決定履歴 / 会長承認ゲート
│
├─ [G2] Institutional Core（機関共通基盤・利益源ではない）
│     └ ledger / defense / bus / allocator / observatory / execution gateway
│
├─ [G3] Investment Business Group（利益事業＝複数の独立利益源）
│     ├ Proprietary Quant Division            （自己勘定クオンツ）※一部稼働(paper)
│     ├ Prop Trading Division                 （プロップ事業）※稼働(dry)・複数利益源の一つ
│     ├ Arbitrage Division                    （裁定）※枠のみ
│     ├ Macro and Global Markets Division     （マクロ・世界市場）※枠のみ
│     ├ Crypto and Digital Assets Division    （暗号・デジタル資産）※一部(paper/disarmed)
│     ├ Equity Division                       （株式）※枠のみ
│     ├ Commodity Division                    （商品）※枠のみ
│     ├ Yield / Carry / Swap Division         （利回り・キャリー・スワップ）※骨格
│     └ Future Markets Division               （将来市場）※枠のみ
│
├─ [G4] Research and Intelligence Group（研究・知能）
│     ├ Research Division                     （エッジ探索・仮説検証）※骨格稼働
│     ├ Evolution Division                    （自己進化・敗戦解剖）※稼働(週次)
│     ├ Market Intelligence Division          （レジーム判定・外部調査 Hermes）※一部稼働
│     └ AI Council Division（AI会議）          （意思決定投票・6 voters）※オンデマンド
│
├─ [G5] Risk, Audit and Compliance Group（リスク・監査・法務）
│     ├ Audit and Risk Division               （Core監督・統治）※一部稼働
│     ├ Compliance Desk                       （プロップ会社別規程・会長承認整合）※骨格
│     └ Security Desk                         （鍵隔離・秘匿・出力レダクション）※ルール稼働
│
├─ [G6] Technology and Operations Group（技術・運用）
│     ├ Platform / Daemon Ops                 （母デーモン:7878 / 司令室:7891 / 死活監視 / 自動起動）※稼働
│     ├ Tooling（Arsenal）                     （37+ ツール登録・equip/invoke）※稼働
│     ├ Knowledge Infrastructure（記憶の家）    （Obsidian vault / GitSync backup）※稼働
│     └ Data and Dashboard Infrastructure     （data / build_dashboard / dashboard群）※稼働
│
└─ [G7] Chairman Navigation Layer（会長中央司令）
      └ aurelian_command.html / INSTITUTION-STATUS.md / institution_state.json / aurel_life.html（人格窓）/ ブリーフィング
```

**注**: `会長` は全Groupの上位に立つ唯一の最終決定者。G1 は会長直下の経営執行（AUREL）と統治。G7 は会長が機関を見るための窓（実務は各Groupが担う）。

---

## 提出物2：階層定義（Group → Division → Desk → Strategy → Agent/Squad → Execution）

| 階層 | 定義 | 例 |
|---|---|---|
| **Group** | 機関の最上位機能ブロック。7個。 | Investment Business Group |
| **Division** | Group内の事業/機能部門。利益事業部 or 機能部門。 | Proprietary Quant Division |
| **Desk** | Division内の戦略クラスタ（市場観/手法でまとめる机）。 | Trend Following Desk |
| **Strategy** | 具体的な売買戦略（1つの意思決定ロジック）。 | Daily Trend Strategy / ETH Autonomous Strategy |
| **Agent / Squad** | 戦略を実行する単位（兵・分隊・自律エージェント）。 | 日足19兵 / 4H暗号8兵 |
| **Execution System** | 実際に注文・計算を行う末端（paper/dry/live）。 | paper execution / g4_dryrun / mt5_live |

**確定した階層適用（会長の指定通り）**:
- **Prop Trading Division は Division**。**G4 はその配下の Program / Strategy**（審査機＝FundingPips Program の US100 ORB Strategy）。
- **ETH Autonomous は Division ではなく Strategy**（Crypto Division 配下の1戦略）。
- **日足19兵・4H暗号8兵は組織部門ではなく Agent / Squad（Execution Unit）**。

**適用例（会長の例をそのまま実装）**:
```
Investment Business Group
 → Proprietary Quant Division
   → Trend Following Desk
     → Daily Trend Strategy
       → 日足兵（Squad）
         → paper execution
```

---

## 提出物4：最終機能一覧（現存有無に関係なく全列挙）

> 各機能に現況フラグ: 【済】完成 /【一部】一部完成 /【無】未着手。詳細評価は GAP-ANALYSIS.md。

**市場・戦略の広さ**
- 複数市場対応【一部】/ 複数時間軸【一部】/ 複数戦略【一部】/ 複数口座【無】/ 複数ブローカー【無】/ プロップ会社別管理【一部】

**ポートフォリオ・資本**
- ポートフォリオ横断リスク【一部】/ 資本配分（allocator）【一部】/ 利益源評価（PSR×テール）【一部】

**戦略ライフサイクル**
- 戦略の採用・降格・停止・退役【一部】/ 新戦略探索（research）【一部】/ 自己進化（evolution）【一部】

**市場認識・執行品質**
- 市場レジーム判定（observatory）【一部】/ 執行品質分析（tca）【一部】/ 異常検知【一部】/ 障害復旧（health-monitor）【済】

**意思決定・統治**
- AI会議（council）【一部】/ 会長承認ゲート【済(手続)】/ 意思決定履歴（hash-chain ledger）【済】/ 監査（Audit and Risk）【一部】/ セキュリティ（鍵隔離・秘匿）【済(ルール)】

**知能・研究**
- 研究（edges/sim）【一部】/ 自己進化（coroner/evolve/ai_soldier）【一部】/ 外部調査（Hermes）【済(基盤)】

**運営・UI**
- 会長中央司令UI（aurelian_command）【一部】/ 日次・週次・月次運営【一部（日次/週次あり・月次無）】

**拡張**
- 将来の新市場・新Division追加【設計済(枠)】

---

## 提出物8への布石：全体構築ロードマップ（10トラック）

> プロップ合格・ETH実弾化を中心にしない。10トラックを分離し、各トラックを段階的に活性化する。各Stageの `目的/完成条件/既存資産の利用/新規構築物/リスク/会長判断` を定義。

### T1. Institutional Foundation（機関基盤）
- 目的: 器・憲章・状態・階層・非干渉境界の確立。
- 完成条件: 最終組織図＋階層＋状態モデル＋憲章体系が登録され、AUREL/文書/UIが同一状態を参照。
- 既存利用: 憲章体系, institution_state.json, INSTITUTIONAL-CORE.md（Stage1-4成果）。
- 新規: 本FINAL-ARCHITECTURE / ASSET-REPLACEMENT-MAP / GAP-ANALYSIS。
- リスク: 設計過多で実装が遅れる。→ 器のみ先行・実装は後続Stage。
- 会長判断: 最終組織図の承認。
- **状態: ほぼ完了（本修正Stage 5）**

### T2. Institutional Core Activation（共通基盤の本活性化）
- 目的: ledger/defense/bus/allocator/observatory/execution を骨格→実稼働へ。
- 完成条件: 全取引が単一台帳に追記・日次突合・アロケータが実データで配分提案・防衛が実損益で作動。
- 既存利用: empire/{ledger,defense,bus,allocator,observatory,execution}。
- 新規: 各サブシステムの本結線・監視・日次突合ジョブ。
- リスク: 実データ結線でバグ→資本影響。paper限定で先に検証。
- 会長判断: 本活性化着手のGO。

### T3. Central Command UI（可視化）
- 目的: 会長が1画面で全機関を把握。読取専用→将来操作段階解放。
- 完成条件: aurelian_command が state.json をライブ参照・全Group/Division/機能別完成度を表示。
- 既存利用: aurelian_command.html, dashboard群, aurel_life.html。
- 新規: ローカルHTTP配信でfetch一本化・Group/Division別ビュー。
- リスク: 表示と実状態の乖離。→ 単一情報源を厳守。
- 会長判断: 操作ボタン解放の可否（当面は読取専用）。

### T4. Research and Intelligence（研究・評価）
- 目的: エッジ探索・進化・レジーム・外部調査・AI会議を統合運用。
- 完成条件: 週次で仮説→検証→採否がAI会議＋会長承認で回る。
- 既存利用: research/, evolution/, observatory/, council/, Hermes, Gemini。
- 新規: 研究→事業部への昇格パイプライン。
- リスク: AI会議のエコーチェンバー（全voterがGemini）。→ voter多様化。
- 会長判断: 新戦略の採用/降格の最終承認。

### T5. Investment Divisions（各利益事業の構築）
- 目的: 9 Division の器へ戦略を段階投入（paper→検証）。
- 完成条件: 各Divisionに最低1 Desk/Strategyが検証済みpaperで稼働。
- 既存利用: 日足19→Proprietary Quant / 4H暗号8・ETH等→Crypto / G4→Prop / carry→Yield。
- 新規: Arbitrage/Macro/Equity/Commodity/Future の初期Desk。
- リスク: 器だけ増やして中身が伴わない。→ 各Divisionに完成条件を課す。
- 会長判断: どのDivisionを次に中身入れするか。

### T6. Risk and Audit（リスク・監査の統治強化）
- 目的: Core監督・プロップ会社別規程・横断リスク・違反検知の統治確立。
- 完成条件: 全実行が監督下・違反は自動検知し会長/AURELへ報告。
- 既存利用: Audit and Risk, defense, funded_config照合。
- 新規: Compliance Desk（会社別ルールエンジン）, Security Desk手順の文書化。
- リスク: 監督の抜け。→ 実行者と監督者の分離を維持。
- 会長判断: 実弾前の監査合格基準。

### T7. Capital Allocation（資本配分）
- 目的: 利益源評価に基づく資本の動的配分（複数口座/ブローカー跨ぎ）。
- 完成条件: allocatorが全利益源のPSR×テールで月次±20%配分を提案・会長承認で反映。
- 既存利用: allocator/capital_allocator.py。
- 新規: 複数口座・複数ブローカーの資本台帳。
- リスク: 実弾配分は資本直結。→ paper実績が十分貯まるまで提案のみ。
- 会長判断: 配分方針・上限。

### T8. Execution Infrastructure（執行インフラ）
- 目的: 複数ブローカー・複数口座への決定的執行と約定品質管理。
- 完成条件: execution gatewayが口座/ブローカー別に二重ロック執行・TCAで品質監視。
- 既存利用: execution/{gateway,mt5_live,sizing,tca}。
- 新規: ブローカーアダプタ拡張・口座ルーティング。
- リスク: 誤発注・口座衝突（ETH事案の教訓）。→ 口座用途の明示登録を必須化。
- 会長判断: 実弾口座の割当。

### T9. AI Agent Organization（AI社員組織）
- 目的: Arsenal/Council/Hermes/Gemini/兵を「AI社員組織」として役割・権限・監督を定義。
- 完成条件: 各AIエージェントに職務・入出力・権限・監督部署・エスカレーション先が定義される。
- 既存利用: Arsenal(37tools), council voters, Hermes, ai_soldier。
- 新規: AI社員名簿・権限表・エスカレーション規程。
- リスク: 権限の暴走。→ 実行権は決定的コード＋会長GOに限定。
- 会長判断: AIに与える権限範囲。

### T10. Live Activation & Scale/Expansion（実弾化と拡張）
- 目的: 段階的実弾解放（paper→最小実弾→本番）と新市場/新Division追加。
- 完成条件: 二重ロック＋会長最終GOの下で最小実弾が安全に稼働・拡張手順が確立。
- 既存利用: 全Stageの成果。
- 新規: 実弾運用基盤・資本口座設計（=旧Stage 5・ここで再合流）。
- リスク: 破産リスク。→ 床/デッドマン/キルスイッチ不可侵。
- 会長判断: **各段階の最終GO（必須）**。

---

## 提出物9：次に構築すべき最優先領域

再評価順（Build All, Activate Gradually）: **1.全体の器 → 2.共通基盤 → 3.可視化 → 4.研究・評価 → 5.各利益事業 → 6.実弾化 → 7.拡張**。

- **今（最優先）= 1.全体の器**: 本修正Stage 5で提出中。最終組織図・階層・再配置・差分・ロードマップの会長承認をもって器を確定。
- **次 = 2.共通基盤（T2）**: Institutional Core の本活性化計画（paper限定で結線検証）。
- **その次 = 3.可視化（T3）**: aurelian_command をローカルHTTP化しGroup/Division別完成度をライブ表示。
- 実弾化（T10）は器・基盤・可視化・研究・各事業が整うまで**中心に据えない**。

---

## 提出物10：プロップが「中心ではなく、独立事業部の一つ」である確認

- Prop Trading Division は **Investment Business Group 内の9 Division の1つ**。同格に Proprietary Quant / Arbitrage / Macro / Crypto / Equity / Commodity / Yield / Future が並ぶ。
- G4 は Division ではなく Prop Trading Division 配下の **Program / Strategy**。
- Aurelian の完成率は**プロップの合格や現存EAの数で計算しない**（→ GAP-ANALYSIS.md は Group別/Division別/機能別で評価）。
- プロップ隔離（g4_境界・読取専用）は Stage 1-4 の通り**維持**。中心化はしない。

---

## 改定
- v1（2026-07-30）: 修正Stage 5 として初版。7 Group・9 Investment Division・6階層・10トラックのロードマップを設計登録。既存資産配置は ASSET-REPLACEMENT-MAP.md、差分/完成度は GAP-ANALYSIS.md に分離。
