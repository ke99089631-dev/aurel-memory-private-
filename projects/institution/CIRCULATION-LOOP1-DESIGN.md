---
doc_id: AURELIAN-CIRCULATION-LOOP1-DESIGN-v1
tags: [institution, circulation, loop1, knowledge, self-evolution, build-step2, paper-only]
type: loop-design
rank: STEP2 成果（最初の1ループ＝最小の“呼吸”の詳細設計）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: CORE-BACKBONE-DESIGN.md（背骨）/ 実コード読取調査
scope: 設計のみ。paperのみ・金ゼロ・稼働システム無変更。実装はGO待ち。
closes_loops: ④知識 + ⑨自己進化（最小形）
---

# 最初の1ループ — 知識/自己進化の最小“呼吸”（STEP 2）

> **目標**: Aurelianを初めて“呼吸”させる。1つのpaper結果が、一周して戻り、**次の判断を実際に変える**ことを自動で・観測可能に成立させる。
> **鍵**: これは新造でない。**既に存在する手動の鎖を、背骨(`result.*`)で自動・連続に繋ぎ替える**だけ。

---

## 0. 何を閉じるのか
- CIRCULATION-GAPMAP.md の **④知識ループ**（成功→Research→知識→次戦略）と **⑨自己進化ループ**（経験→改善→新経験）の**最小形**。
- 金は一切動かさない。live adapterは非武装のまま。**paperの中だけで循環を一周させる**。

---

## 1. 既存の鎖（現物）と、切れている場所

調査で確認した実体（すべて実在ファイル）：

```
run_trading_cycle.py ──(FILL/実現PnL)──> ledger.sqlite + paper_book.json
        │                                        │
        │                                        ├─> build_dashboard.py が読む（PSR/歪度/勝率）→ dashboard.html（人が見る・戻らない）
        │                                        │
        │                                        └─> run_evolution_cycle.py が【手動起動で】読む
        │                                                 → run_backtest() → evolve_once()（ノブ変異）
        │                                                 → allocator.stats()（PSR×テール採点）
        │                                                 → 昇格/降格/退役（roster更新）
        │                                                 → evolved_configs.json 保存
        │                                                        │
        └<──── evolved_cfg() が evolved_configs.json を拾って次サイクルへ反映 <──┘
```

**切れている点**：
- evolution は **手動起動・非連続**。結果が出ても自動で回らない。
- dashboard は結果を人に見せるだけで**機関に戻らない**（帰還でなく表示）。
- 各段が別JSONを各自読み書き（単一背骨を通らない）。

→ **鎖はある。切れているのは「自動・連続・単一背骨」だけ。** ここを1本の線で繋ぐ。

---

## 2. 閉じたループ（背骨上・目標形）

```
[G3 Business] run_trading_cycle(paper)
      │ produces
      ├── fill.*  ──────────────> [Ledger 記憶に永続]
      └── result.*（新設）────────> [Bus 神経]
                                        │ subscribe
                    ┌───────────────────┼────────────────────┐
                    ▼                                        ▼
        [G4 Research/Evolution]                   [Observatory 乖離記録]
        result.* を購読                            divergence.* を産出
        → evolve_once() 改善案                     （模型vs実際・失敗の種）
        → allocator.stats() 採点
        → lifecycle判定（QUARANTINE/PROBATION/ACTIVE/RETIRED）
        → knowledge.*（新設）を publish（学習の記録）
        → evolved_configs を StateStore へ
                    │
                    ▼
        [StateStore 現在値]  evolved_configs 集約（単一writer・ロック）
                    │ subscribe / 参照
                    ▼
        [G3 Business] 次サイクルが新configで判断  ← 一周閉じる
                    │
                    └── 変化を Ledger に NOTE（loop_closed 証跡）
```

---

## 3. 新設する“線”＝2トピックのみ（最小追加）

背骨に足すのは**線（イベント）だけ**。臓器は既存を使う。

### `result.*`（帰還の要）
- **発行者**: trading cycle のサイクル終了フック（既存を止めず、後段に追加）。
- **契機**: 1サイクル完了・実現PnL確定時。
- **payload（案）**: `{cycle_id, market, symbol, mode:"paper", realized_pnl, trades_n, win_rate, psr, skew, config_hash, ts}`。
- **購読者**: Research/Evolution（学習の入力）＋ Observatory（乖離）。

### `knowledge.*`（学習の記録）
- **発行者**: evolution が改善案/昇降格を出した時。
- **payload（案）**: `{from_result: cycle_id, action:"mutate|promote|demote|retire", symbol, old_config_hash, new_config_hash, score_before, score_after, reason, ts}`。
- **購読者**: Ledger（NOTEとして永続）＋ StateStore（configs反映）＋ 将来G1 Executive（方針材料）。

> `result.*` と `knowledge.*` は既存トピック命名（`sig.*`/`fill.*`/`risk.*`）と同じ規約。Ledgerは全トピックを写経して監査記録。

---

## 4. 手動 → イベント駆動（既存を止めずに）

- **既存プロセスは停止も改変もしない**。`run_evolution_cycle.py` の手動起動はそのまま残す。
- 新規に**細い購読プロセス（listener）を1つ追加**：`result.*` を購読し、条件を満たしたら evolution を呼ぶ。
- 既存 `run_trading_cycle.py` は改変でなく**後段フックの追加**（サイクル終了後に result を publish するだけの薄いラッパ）。
- タスクスケジューラ変更なし・DBスキーマ変更なし。listenerは新規プロセスの**追加**であり、既存の起動系に触れない。

---

## 5. “呼吸した”とどう証明するか（閉ループ判定）

設計は「回ったつもり」を許さない。**観測可能な合格条件**を先に決める：

- **合格条件**: あるpaper結果(`cycle_id=X`)が原因で evolution が config を変え(`new_config_hash`)、**その新configで次サイクルの判断が実際に変わった**ことを、Ledgerの `NOTE(loop_closed)` が `result→knowledge→next_cycle` のIDで連結して示す。
- **観測**: `loop_closed` NOTEが1件でも連鎖検証OKで残れば、**④/⑨ループは●（閉じた）**と記録。GAPMAPを更新。
- これが Aurelian の**最初の心拍**。1拍でも打てば、同じ型を他ループへ複製できる。

---

## 6. 学習ループ自体の安全弁（正直に：ここが一番危ない）

**自己改変して回るループは、機関で最も事故が起きやすい場所**（過学習・変異暴走・フィードバック不安定）。閉じる前に安全弁を設計に組み込む：

- **paper限定**: この心拍は全部paper。live武装(enable_live+arm_code)には一切触れない。ACTIVE昇格＝paperでの昇格であり、実弾化は別GO。
- **変異の上限**: 一定期間あたりの mutation 回数・変化幅に上限（既存allocatorの月±20%制約思想を踏襲）。
- **ライフサイクル関門**: 新config は即本番でなく QUARANTINE→PROBATION を通す（既存 evolution_roster の状態機械を関門に使う）。
- **監督**: G5 Audit & Risk がこのループを supervised_by。異常な採点急変・連続退役は `risk.*` で停止提案。
- **凍結不可侵**: 維持機(MM0)・審査機(G0)・凍結backtester(SHA256)・プロップ・g4_ は**この学習ループの対象外**（読取専用/非接続）。心拍が触れるのは機関のpaper戦略のみ。
- **キルスイッチ**: listenerは単独プロセス。止めれば手動運用に戻るだけで、既存の取引系は無傷。

---

## 7. 実装の前提（未実装・会長GO待ち）
- 本書は設計のみ。実装時は「線(`result.*`/`knowledge.*`)＋listener＋薄い後段フック＋StateStore集約(まず読取統合)」の**追加のみ**。既存コードは改変せずラップ。
- 変更禁止9項目・凍結SHA256・維持機#5凍結・g4_読取専用・プロップ非接続・二重ロック/床/キルスイッチ全順守。
- 金ゼロ・paperのみ。

---

## 8. STEP 2 の結論
- 最初の心拍に必要なのは **新トピック2本＋listener1個＋薄いフック＋config集約** だけ。臓器は全部既存。
- 合格条件は「`loop_closed` NOTEが連鎖検証OKで1件残る」＝結果が次の判断を実際に変えた証跡。
- ここが●になれば、同じ型（結果→帰還→反映）を ⑤失敗・⑥AI・②資本 へ順に複製していく。**Aurelianが生命体になる出発点。**

## 改定
- v1（2026-07-30）: STEP2。最小の知識/自己進化ループを背骨上に詳細設計。result.*/knowledge.*・イベント駆動化・閉ループ判定・学習ループの安全弁を定義。実装はGO待ち・paperのみ・金ゼロ。
