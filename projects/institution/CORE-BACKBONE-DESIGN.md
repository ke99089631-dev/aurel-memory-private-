---
doc_id: AURELIAN-CORE-BACKBONE-DESIGN-v1
tags: [institution, G2-core, backbone, circulation, build-step1, wiring]
type: backbone-design
rank: STEP1 成果（G2 Coreを単一背骨にする配線設計）
created: 2026-07-30
status: active
owner: AUREL（統括CEO）
approver: 会長（KEIKI MAEDA）
source: CIRCULATION-ARCHITECTURE.md（思想）/ CIRCULATION-GAPMAP.md（断裂地図）/ 実コード読取調査（Explore・読取専用）
scope: 設計のみ。実装・稼働システム変更・DB変更・金の移動は一切含まない。
---

# G2 Institutional Core — 単一背骨 配線設計（STEP 1）

> **目的**: バラバラの臓器を、1本の背骨（血管＋神経＋記憶）に繋ぐ設計を、**現物のコードに基づいて**引く。
> **原則**: 空箱を作らない。既存の実体を背骨に接続する。追記のみ・非破壊・凍結資産は読取専用。

---

## 0. 現物調査でわかった“血管の実態”（重要・正直）

読取専用調査（実パス確認済み）で判明した現実。**綺麗な単一情報源は、まだ存在しない。**

| 項目 | 現実 | 意味 |
|---|---|---|
| **バス** | `empire/bus/signal_bus.py` は在る（SQLite pub/sub・publish/subscribe）が、**背骨として使われていない**。実際は squad→defense→gateway の直接呼び出し | 血管はあるが、血が通っていない配管がほとんど |
| **状態(state)** | **`institution_state.json` は人手で維持する静的ファイルで、コードから書かれていない**。本当の運用状態は `empire/data/` の複数JSON（autopilot_state / paper_book / paper_book_4h / evolved_configs / evolution_roster）に**分散・ロック無し** | 「単一情報源」は現状“看板だけ”。運用の実体と繋がっていない |
| **Ledger** | `empire/ledger/ledger.py` は**実稼働**。ハッシュ連鎖・append専用。trading cycleがSIGNAL/ORDER/FILLを実際に書いている | 永続記憶は生きている。ここは資産 |
| **defense/allocator/observatory** | いずれも**骨格**（コードは在る・中央に接続されていない）。gatewayとledgerだけ実使用 | 臓器はあるが神経に繋がっていない |
| **中央ハブ** | **無い**。各スクリプトが ledger/defense/gateway を各自instオして使う | 背骨が無い＝生命体でなく臓器の寄せ集め |
| **帰還ループ(④知識)** | 骨格として**既に存在**：trading→paper_book/ledger→（dashboardが読む/evolutionが手動で読む）→evolved_configs→次のtradingが拾う。ただし**手動・非連続・分断** | ゼロから作るのではない。**既存の鎖を自動化し1本に通す**のがSTEP2 |

> **最重要の発見**: 帰還ループはゼロから作るのではない。**既に鎖はある。切れているのは「自動で・単一背骨を通って・連続で」回る部分だけ**。だから最初の呼吸は“新造”でなく“接続と自動化”になる。コストは思ったより低い。

---

## 1. 背骨の定義（3臓器を1本に）

単一背骨 = **Core Hub** が次の3つを1回だけ生成し、全部門をこれに読み書きさせる：

```
            ┌───────────────────────── Core Hub ─────────────────────────┐
            │                                                            │
  [各部門]──┤  ① SignalBus (神経)   publish/subscribe ← 既存 signal_bus.py │──[各部門]
            │  ② Ledger    (記憶)   append専用・ハッシュ連鎖 ← 既存 ledger.py │
            │  ③ StateStore(現在値) 単一writer・ロック・原子的書込 ← 新規(集約) │
            │                                                            │
            └────────── supervised_by: G5 Audit & Risk（監督） ───────────┘
```

- **① SignalBus = 神経**：部門間は直接呼び出しをやめ、**必ずバス経由**で信号を渡す（受・渡がここを通る）。
- **② Ledger = 永続記憶**：起きたこと（産）は全部ここに残る。既存の実稼働をそのまま背骨の記憶に採用。
- **③ StateStore = 現在値**：分散した `empire/data/*.json` を**単一のwriter＋ロック＋原子的書込**の窓口に集約。`institution_state.json` は**手書きをやめ、StateStoreから生成される“投影(ビュー)”**にする（看板→実体の反映へ）。

---

## 2. 循環契約（5点）をバスの“通信規約”として具体化

抽象の「受・判・産・渡・帰」を、背骨上の**具体的なメッセージ規約**に落とす。バスのトピック命名で循環を表現する：

| 5点 | バス上の実体 | トピック例（既存 `sig.*`/`fill.*`/`risk.*` を踏襲） |
|---|---|---|
| ①受 | subscribe | 各部門が自分の入力トピックを購読 |
| ②判 | 部門内処理 | （バスに出さない・内部判断） |
| ③産 | publish | `sig.{market}` / `fill.*` / `risk.*` / `knowledge.*`（新）/ `alloc.*`（新） |
| ④渡 | 下流がsubscribe | 下流部門が③のトピックを購読して受け取る |
| ⑤帰還 | **結果トピック→上流が購読** | `result.*`（新）/ `divergence.*`（既存recorder活用）を**上流(Research)が購読** |

> **⑤帰還の鍵**: 今まで欠けていたのは「結果を上流が購読する線」。`result.*` トピックを新設し、**Researchがそれを購読して次の仮説に反映**する。これが循環を閉じる1本の線。

---

## 3. 6サブシステムの背骨接続（何を購読し何を発行するか）

| Core サブシステム | 現状 | 背骨での役割 | 購読(受) | 発行(産) |
|---|---|---|---|---|
| SignalBus | 在・未活用 | 神経そのもの | — | （運ぶ） |
| Ledger | 実稼働 | 記憶。全publishを監査記録 | 全トピック(写経) | — |
| Defense(risk_engine) | 骨格 | 免疫の前段。発注前検問 | `sig.*` | `risk.*`(ALLOW/HALVE/REJECT) |
| Allocator(capital_allocator) | 骨格 | 資本の判断 | `result.*` | `alloc.*`(配分提案) |
| Observatory | 骨格 | 感覚。レジーム/死活/乖離 | 市場・`fill.*` | `regime.*`/`hb.*`/`divergence.*` |
| Execution Gateway | 実稼働(paper) | 筋肉の出口 | `sig.*`(検問通過後) | `fill.*` |

> 凍結・独立資産は**接続しない/読取のみ**：維持機(MM0)・審査機(G0)・凍結backtester(SHA256)・プロップ(独立事業)・g4_（読取専用）。背骨に繋ぐのは機関の循環対象のみ。

---

## 4. STEP 2 への橋（最初に閉じる1ループを背骨上に描く）

既存の分断された鎖を、背骨で**自動・連続**に繋ぎ替える（詳細設計は次工程）：

```
Business(paper) --fill.*--> Ledger(記憶)
                       \--result.*--> [Research/Evolution が購読]
                                          → evolve_once() で改善案生成
                                          → knowledge.* / config更新を publish
                                          → StateStore(evolved_configs 集約)
                                          → 次の Business cycle が購読して反映
                                          ↑__________ 一周 __________↓
```

- 既存資産をそのまま使う：`run_trading_cycle.py`(FILL産出)・`ledger.py`・`run_evolution_cycle.py`(evolve)・`evolved_configs.json`。
- **新設は「線」だけ**：`result.*` トピックと、それを購読して evolution をトリガする細い配線。手動起動を**イベント駆動**に変える。
- **金ゼロ・paper のみ**。live adapter は非武装のまま触らない。

---

## 5. 実装時の絶対条件（未実装・GO待ち）

本書は**設計のみ**。実装は会長GO後、かつ以下厳守：
- 既存の稼働コード（run_trading_cycle 等）は**改変でなくラップ/追加**で接続。凍結SHA256資産・維持機・審査機は不可侵。
- StateStore集約は**既存JSONを壊さず**、まず「読取で統合ビューを作る」→段階的に単一writer化。DBスキーマは変えない。
- g4_・プロップ・.env は読取専用/非接続を維持。
- プロセス停止・再起動・タスクスケジューラ変更なし（イベント駆動化は新規プロセスの追加で、既存を止めない）。
- 二重ロック（enable_live+arm_code）・床(deadman)・キルスイッチは外さない。

---

## 6. STEP 1 の結論
- 背骨の3臓器は**既に全部存在する**（bus・ledger・分散state）。足りないのは「1本に束ねるハブ」と「結果を上流へ返す線(`result.*`)」。
- `institution_state.json` は**看板と実体が分離**している。これを StateStore からの投影に変えることが、G7（会長へライブで状態が届く帰還）の前提でもある。
- 次工程 STEP 2 = この背骨上で**最初の1ループ（④知識/⑨自己進化の最小形）を自動で一周させる**詳細設計。

## 改定
- v1（2026-07-30）: STEP1。現物コード調査に基づく単一背骨設計。bus/ledger/StateStore・循環契約のバス規約化・6サブシステム接続・STEP2への橋を定義。実装は未・GO待ち。
