---
doc_id: AURELIAN-GAP-ANALYSIS-v1
tags: [institution, stage5, gap-analysis, completion, final-architecture]
type: gap-analysis
rank: 最終設計付属（現状との差分・完成度評価）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: FINAL-ARCHITECTURE.md / ASSET-REPLACEMENT-MAP.md
---

# 現状との差分分析・完成度評価 — Aurelian 最終形態=100%

> **原則**: 完成率を単一の曖昧な数字で示さない。**Group別・Division別・機能別**に評価する。
> **完成率の意味**: 「最終形の器に対して、どれだけ中身が検証済みで動いているか」。実弾でなくても paper/dry で検証済みなら加点、器だけなら低評価。
> **凡例**: 済=検証済で稼働 / 一部=一部稼働・未検証あり / 骨格=コードはあるが本活性化前 / 枠=器のみ / 無=未着手。

---

## 提出物5：現状との差分（分類）

### (a) 現在完成している機能【済】
- 意思決定履歴（ハッシュ連鎖台帳・seq=3・全鎖検証OK）
- 会長承認ゲート（手続として確立：enable_live+arm_code+会長GO）
- セキュリティ規約（.env非読取・出力レダクション・鍵隔離）
- 障害復旧（health-monitor 自動復活・mother-autostart）
- 常駐基盤（母デーモン:7878・司令室:7891）
- 記憶基盤（Obsidian vault + GitSync）
- 状態の単一情報源（institution_state.json）＋読取専用中央司令画面

### (b) 一部完成している機能【一部】
- 複数市場/複数時間軸/複数戦略（日足+4H+暗号のpaper・維持機は多市場だが凍結）
- 資本配分（allocator：コードあり・実データ本活性化前）
- 利益源評価（PSR×テール：骨格）
- 戦略ライフサイクル（採用/降格/退役：capital_allocatorの状態遷移あり・運用未確立）
- 市場レジーム判定（observatory：一部稼働）
- 執行品質分析（tca：paper/dry）
- 自己進化（coroner/evolve/ai_soldier/週次cycle：研究モード）
- AI会議（council：オンデマンド・voter多様性に課題）
- 監査（Audit and Risk：統治文書化済・自動検知は未）

### (c) 未着手の機能【無】
- 複数口座・複数ブローカー管理
- ポートフォリオ横断リスクの一元集約（部分的にdefense、全体は未）
- 口座別/ブローカー別ルールエンジン（機関自身の将来の実弾運用向け。※現・独立プロップは非関与で対象外）
- 月次運営サイクル（日次/週次はあり）
- AI社員の職務・権限・エスカレーション規程
- 新市場・新Divisionの追加手順（枠は設計済・手順は未）

### (d) 存在するが再配置が必要な機能【再配置】
- 全 empire/ モジュール（→ G2 Core / G3 事業 / G4 研究に再配置：ASSET-REPLACEMENT-MAP.md）
- Arsenal / Hermes / Gemini / Council（AUREL基盤 → G4/G6 に正式所属）
- 日足19・4H暗号8・ETH等（Proprietary一括 → Proprietary Quant / Crypto に分離）
- G4/審査機/維持機（プロップ中心の扱い → **独立事業・機関非関与**として切り離し。組織図に置くだけ・機関の運用/資本配分/ロードマップ/完成率から除外・さわらない）

### (e) 重複機能
- レジーム判定が observatory（G2寄り）と Market Intelligence（G4）で重なる → **G2が信号供給・G4が解釈/研究**と役割分離（重複解消方針）。
- 通知が observatory/notifier と Hermes/各ツール notifier で分散 → 将来一本化。
- 静的組織図HTML（3種）と最終組織図（FINAL-ARCHITECTURE.md）が併存 → 最終形へ差替検討。

### (f) 不足一覧
- **不足部署（Division）**: Arbitrage / Macro and Global Markets / Equity / Commodity / Future Markets（枠のみ・中身なし）。
- **不足Desk**: Compliance Desk / Security Desk（骨格）/ 各利益Divisionの初期Desk。
- **不足データ**: 複数口座の資本台帳 / ブローカー別約定データ / 各市場のライブデータ購読。
- **不足インフラ**: 複数ブローカーアダプタ / ローカルHTTP配信（UI）/ 口座ルーティング。
- **不足AI社員（定義）**: AI社員名簿・権限表・エスカレーション先（Arsenal/Council/Hermes/ai_soldierは在るが職務未定義）。
- **不足統治機能**: 自動違反検知・口座別/ブローカー別ルールエンジン（機関自身の将来の実弾運用向け。※独立プロップは非関与で対象外）・月次運営。
- **不足UI**: Group/Division別完成度ビュー・ライブ更新・操作段階解放。

---

## 提出物6：Group別完成度

| Group | 完成度 | 根拠 |
|---|---|---|
| G1 Executive and Governance | **70%** | 憲章・会長承認・決定履歴・AUREL稼働。自動統治は未。 |
| G2 Institutional Core | **35%** | 6基盤のコードは在るが多くが骨格。observatory/executionのみ一部稼働。 |
| G3 Investment Business | **10%** | 機関が構築する Division中、実質はProprietary Quant(paper)・Crypto(paper/disarmed) の部分のみ。他は枠。**Prop Trading は独立事業・機関非関与のため算入外**。 |
| G4 Research and Intelligence | **40%** | research/evolution/observatory/council/Hermes は在り稼働。昇格パイプラインと多様性が未。 |
| G5 Risk, Audit and Compliance | **30%** | Audit and Risk統治文書化済。自動検知・Compliance/Securityの実装は骨格。 |
| G6 Technology and Operations | **75%** | デーモン/死活監視/自動起動/Arsenal/記憶/データ盤が稼働。UI配信・複数口座インフラが未。 |
| G7 Chairman Navigation | **55%** | 中央司令画面・状態SoT・人格UIあり。ライブ更新・Group別ビューが未。 |

> **総括（単一数字を避けた上での一言）**: 「**基盤と運用（G2骨格・G6稼働）は進むが、利益事業の中身（G3）が最も薄い**」。Aurelianは器は立ち上がったが、複数利益源の実体はこれから。

---

## 提出物7：Division別完成度（G3 Investment Business Group）

| Division | 完成度 | 現況 | 次の一歩 |
|---|---|---|---|
| Proprietary Quant | **30%** | 日足19 paper稼働・断面/回帰は骨格 | Trend Desk検証→最小実弾候補化 |
| Prop Trading | **算入外** | 独立事業・機関非関与（置いてあるだけ・さわらない） | 機関は関与しない（プロップ側運用軸で完結） |
| Crypto and Digital Assets | **20%** | 4H暗号8 paper・ETH/BTC/LTCはDISARMED | ETH別口座再武装 or paper継続の選択 |
| Yield / Carry / Swap | **8%** | carry squad 骨格のみ | Carry Desk を初期中身化 |
| Arbitrage | **0%** | 枠のみ | 裁定手法の研究着手（G4起点） |
| Macro and Global Markets | **0%** | 枠のみ | observatory連携でマクロDesk設計 |
| Equity | **0%** | 枠のみ（維持機ETF近似は別扱い） | 株式データ購読から |
| Commodity | **0%** | 枠のみ（維持機商品は別扱い） | 商品データ購読から |
| Future Markets | **0%** | 枠のみ | 新市場追加手順の確立後 |

---

## 機能別完成度（横断・主要25機能）

| 機能 | 完成度 | 機能 | 完成度 |
|---|---|---|---|
| 複数市場対応 | 一部(35%) | 異常検知 | 一部(30%) |
| 複数時間軸 | 一部(40%) | 障害復旧 | 済(85%) |
| 複数戦略 | 一部(35%) | AI会議 | 一部(40%) |
| 複数口座 | 無(5%) | 会長承認 | 済(80%) |
| 複数ブローカー | 無(5%) | 意思決定履歴 | 済(90%) |
| 口座別/ブローカー別管理※ | 無(10%) | 監査 | 一部(35%) |
| ポートフォリオ横断リスク | 一部(25%) | セキュリティ | 済(80%) |
| 資本配分 | 一部(30%) | 研究 | 一部(45%) |
| 利益源評価 | 一部(30%) | 自己進化 | 一部(45%) |
| 戦略採用/降格/停止/退役 | 一部(30%) | 会長中央司令UI | 一部(55%) |
| 新戦略探索 | 一部(45%) | 日次/週次運営 | 一部(60%) |
| 市場レジーム判定 | 一部(40%) | 月次運営 | 無(10%) |
| 執行品質分析 | 一部(35%) | 新市場/新Division追加 | 枠設計(20%) |

> ※「口座別/ブローカー別管理」は**機関自身の将来の実弾運用**に向けた機能を指す。現・独立プロップは運用軸が別・機関非関与のため対象外。
> ※パーセントは「最終形に対する体感進捗」で、権威的計測値ではない（**推測を含む**）。目的は数字自慢ではなく、**どこが薄いかを見えるようにする**こと。最も薄いのは「複数口座/複数ブローカー/月次運営/各利益Division中身」。

---

## 最も重要な差分（要約）
1. **利益事業（G3）が最薄**。器9 Divisionに対し実体は3 Divisionの一部のみ。
2. **複数口座・複数ブローカーが未着手**。ここがない限り「複数利益源の分離運用」は不完全。
3. **統治の自動化が未**（監査は文書、違反検知は手動）。実弾前に必須。
4. **AI社員の職務・権限が未定義**。エージェントは在るが組織化されていない。
5. **UIがライブでない**（現状は写しフォールバック）。可視化トラック(T3)で解消。

---

## 改定
- v1（2026-07-30）: 修正Stage 5 として初版。Group別/Division別/機能別に評価。単一完成率は用いない。
