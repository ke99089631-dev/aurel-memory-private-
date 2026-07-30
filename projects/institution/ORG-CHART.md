---
doc_id: AURELCAPITAL-ORGCHART-v1
tags: [institution, org-chart, foundational]
type: org-chart
rank: 憲章直下（機関の正式組織図）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
---

# Aurelian — 最終組織図 v1

> **本図の位置づけ**: 憲章 第5条「Build All, Activate Gradually」に基づき、**最終形を先に固定する**組織図。全枠を先に存在させ、権限と実資金は段階的に活性化する。
> **凡例**: 【稼働】=実際に動いている / 【骨格】=コードは存在し活性化待ち / 【枠】=名前だけ先に確保。

---

## 全体図

```
会長 KEIKI MAEDA（オーナー・最終決定者・実弾承認権者）
        │
        │  ← Chairman Navigation Layer（会長ナビゲート層）
        │
統括CEO AUREL（経営・資本配分提案・全部門統括・記録・会長への説明）
        │
        ├─ Institutional Core（機関共通基盤 = 旧AssetEmpire共通基盤）【骨格〜稼働】
        │     ├─ 統合台帳       ledger        【骨格】唯一の真実源・追記専用・ハッシュ連鎖
        │     ├─ 防衛司令       defense       【骨格】risk_engine・段階デッドマン・ファクター集約
        │     ├─ 信号バス       bus           【骨格】signal_bus・TTL/topic
        │     ├─ 資本アロケータ  allocator     【骨格】PSR×テールペナルティ・昇格遅降格速
        │     ├─ 観測所         observatory   【一部稼働】regime/divergence/heartbeat/notifier
        │     ├─ 執行ゲートウェイ execution     【一部稼働】gateway/mt5_live/sizing/tca（二重ロック）
        │     ├─ 研究           research      【骨格】edges.py 仮説先行
        │     └─ 進化           evolution     【骨格】ai_soldier/backtest/coroner/evolve
        │
        ├─ Proprietary Investment Division（自己勘定投資部門）【一部稼働】
        │     ├─ ETH自律枠 ETHAutopilot   【稼働・LIVE】会長常時GO（2026-06-16）枠内
        │     ├─ BTC枠                     【骨格・武装解除】
        │     ├─ LTC枠                     【骨格・武装解除】
        │     ├─ 日足19ソルジャー群         【稼働・paper】run_trading_cycle.py
        │     └─ 4h暗号8ソルジャー群        【稼働・paper】run_trading_cycle_4h.py
        │
        ├─ Prop Trading Division（プロップ事業部門）【稼働・読取専用登録】
        │     └─ G4 FundingPips 2-Step チャレンジ  【稼働・dry-run】g4_* 保護境界
        │           ※機関からは読取専用。状態把握・結果表示・異常報告のみ。
        │
        ├─ Research and Evolution（研究・進化部門）【骨格】
        │     ※Institutional Core の research/evolution を横断利用。
        │       仮説生成・敗戦分析(coroner)・戦略進化・バックテスト。
        │
        ├─ Audit and Risk（監査・リスク部門）【一部稼働】
        │     ※Institutional Core の ledger/defense を横断利用。
        │       全停止権限・床の維持・台帳突合・異常の言語化。
        │
        └─ Future Strategy Divisions（将来利益源の枠）【枠】
              ※共通基盤に接続するだけで機関に組み込める空き枠。
```

---

## 補足

### Institutional Core の位置づけ（重要）
Institutional Core は**自己勘定投資部門の内部ではない**。全Divisionが共用する機関の共通基盤（旧AssetEmpire共通基盤）である。台帳・防衛・バス・アロケータ・観測・執行・研究・進化は、Proprietary / Prop / Future のどのDivisionからも共用される横断レイヤーとして独立して置く。

### Chairman Navigation Layer（会長ナビゲート層）
会長とAURELの間に立つ説明・可視化層。憲章 第2条2・第2章目的に基づき、AURELが会長に「最終形／現在地／完成・未完成／過去決定と理由／次の最優先／会長判断待ち」を常に提示する機能。実体は INSTITUTION-STATUS.md とダッシュボード群。

### 権限活性化の順序（Build All, Activate Gradually）
1. 【稼働済】ETH自律枠（会長常時GO・枠内）、Prop dry-run（読取専用）、paperソルジャー群。
2. 【次段階候補】Institutional Core の台帳・アロケータの本活性化（会長承認待ち）。
3. 【将来】実弾増資・新Division活性化（各段で会長の最終GO必須）。

---

## 改定
- v1（2026-07-30）: 初版。憲章v1と同時制定。
