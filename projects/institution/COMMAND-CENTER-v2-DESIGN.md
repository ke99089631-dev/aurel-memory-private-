---
tags: [project/institution, dashboard, design, built]
type: design-proposal
status: PHASE1 BUILT — 会長「きみに推進ですすめてくれ」でGO (2026-08-17)
created: 2026-08-16
---

> **[2026-08-17 UPDATE] Phase 1 着工完了。**
> 会長GO「きみに推進ですすめてくれ」を受け、別モジュール `circulation/command_center.py` を新規作成（現行v1 `dashboard.py` は無傷）。
> ETLはPython側で全導出→JSは描画のみ（血の捏造を構造的に不可能に）。自己完結HTML `command_center.html`（59KB, プレースホルダ残0）を生成、ダブルクリックで開く。
> 5画面: COMMAND(中央ノード網) / MARKET(源泉別P&L曲線) / INTELLIGENCE(世界観・未実装はFUTURE表示) / RESEARCH(発見フィード) / CHAIRMAN(要判断)。
> 改善#5「日次スナップショット」も本日開始: `snapshots/2026-08-17.json`（Knowledge Universeの種）。
> 読取専用・金ゼロ・二重ロック/Live Gate/会長承認権限は一切触らず。プロップ非接触。
> 残: Phase3(承認ボタン, 二重ロック不変) は会長判断待ち。

> **[2026-08-17 UPDATE] Phase 2（生中継化）着工完了。** 会長GO「第二段に進んでいい」。
> `command_center.py` に `serve()` を追加（localhost 127.0.0.1:8787 のみ・GETのみ・書込API無し・POSTは405で拒否）。
> `/` でページ配信＋`__LIVE__={url,every}`注入、`/model.json` で毎回 build_model() し直した最新値を返す。ページは既定30秒ごとに自分で取り直し、全画面を描き直す。
> 上部LIVEバッジに「更新 HH:MM:SS」を表示（画面ストリームの生存＝meta.built）。「最終呼吸」は機関が実際に動いた時刻（autowrite）で別表示＝正直な区別。
> 静的ファイル(ダブルクリック)は `LIVE=null` のまま＝従来どおり一枚の写真。二重ロック/Live Gate/会長承認は不変。金ゼロ・秘密なし・プロップ非接触。
> 起動: `python -m circulation.command_center --serve [--port 8787] [--interval 30]`。停止: Ctrl+C（=生中継停止・静的ファイルは残る）。
> 検証済: index 60KB(live注入OK) / model.json 31KB(loops=9) / POST=405拒否。
> 注意: サーバは前景プロセス。閉じれば生中継停止。常時起動は将来タスク（Windowsタスク/常駐）で会長判断。

> **[2026-08-19 UPDATE] 日次自動撮り直しを採用（会長「君に任せる／このまま使い始める」）。**
> 判明: `build_model()` は約**52秒**かかる。→ 生中継サーバ(serve)は表示ごとに52秒再構築で固まり実用不可。撤退。
> 採用方針: **静的publishを毎朝自動化**。新規 `scripts/run_command_center_publish.bat`（ASCIIのみ・ログ追記）が
> `python -m circulation.command_center --snapshot` を実行→ `data\circulation\command_center.html`(59KB) を最新化＋日付つきsnapshot保存。
> Windowsタスク **`AUREL_CommandCenter_Publish`** 毎日07:10（`AUREL_Circulation_WriteBack` 07:00の直後）。試走 LastResult=0 で確認済。
> 運用: 会長は朝このHTMLを開くだけで昨日からの成長が見える（待ち時間ゼロ）。生中継サーバは常用しない。
> 安全線不変: 紙のみ・金ゼロ・読取専用・二重ロック/Live Gate/会長承認は非接触・プロップ非接触。
> 将来の改善案（着工は会長GO要）: 「52秒を一瞬にする」= build結果を裏でキャッシュ→軽い生中継。今は不要と判断。

# AURELIAN COMMAND CENTER v2 — 監査＋設計案

> 会長号令（2026-08-16）: 現ダッシュボードを「複数パネル監視画面」から「機関そのものがリアルタイムで
> 生きて動いている中央司令端末」へ発展させる。**まず監査＋設計案を提出。会長承認前の全面実装は禁止。**
> 参考画像＝Institutional Quant Terminal。ただしコピーではなく「Aurelian内部をUIへ変換」する。

---

## 0. 結論（先に3行）
1. 実機には **45個のデータファイル**があり、現行v1は**12個しか使っていない**。素材は既に潤沢。
2. 会長最重視の「中央ノード網（神経活動）」は **`discovery.provenance` + `source_family` + `macro_causal.causal_map` + `evidence`** で
   **実データの線として描ける**（捏造ゼロ）。
3. 「動く」は3層で**正直に**実現：①常時＝時計/呼吸 ②疑似リアルタイム＝その日の実イベント再生 ③日次＝スナップショット更新。
   **intradayの実価格は機関内に存在しない → FUTURE/UNAVAILABLE と明示**（$53・プロップの生値は別事業＝機関に混ぜない）。

---

## 1. データ監査（A〜F の6分類）

### A. 現在取得できるデータ（＝ファイルとして既に存在）
| 群 | ファイル | 中身 |
|---|---|---|
| 源泉×8 | carry/trend_follow/mean_reversion/stat_arb/vol_sell/tail_hedge/macro_causal/event_driven `.json` | knob・保有・配分・total_pnl・隔離/監視 |
| 源泉の取引履歴×8 | 同 `_book.json` | trades[]・positions[]（時系列・last_step_date） |
| 樹形図 | source_family.json | 6源泉→兵士→細胞、健康判定・呼吸・advisory_weights |
| 研究 | discovery.json(候補24) / hypothesis_ledger.json(30) / validation.json / evidence.json / frontier.json | 発見→仮説→検証→証拠→壁 |
| 世界 | circulation_digest.world / external_macro.json / macro_causal.json / event_calendar.json(74件) | 地合い・マクロ系列・因果地図・イベント暦 |
| 資本/リスク | capital_book / treasury / reserve / s2_floor_status(床) / s1_forward | 配分・プール・床-8/-12/-15%・免疫 |
| 統治 | council(投票5) / personnel_roster(兵5) / proposals / approvals / technology / scorecard / progress | 合議・人事・提案・承認・技術・North Star・進捗 |
| メタ | autowrite_state / live_gate / evolve / subscribers_state / shadow_configs | 最終更新時刻・実弾ゲート・研究加速 |
| 市場記憶 | market_memory.json(1.4MB, fingerprints6000) / _summary | レジーム指紋の長期時系列・類似局面 |

### B. いま「リアルタイム表示」可能なもの（※honest定義）
- **常時動く（データ非依存の演出＝ただし意味のあるもののみ）**: 時計、機関の呼吸（振幅=実ボラ）、循環ドットの点滅。
- **疑似リアルタイム（＝その日の実イベントを再生）**: 循環が朝1拍回った際の「発見→仮説→検証→棄却」等の状態遷移を、
  実JSONの差分から復元してノード網に流す。
- **実際の更新頻度**: 毎朝07:00の自律1拍（autowrite）＋ `autowrite_state.last_run` に最終時刻。→ 画面に「最終呼吸 hh:mm」を常時表示し、
  **intradayは動かない事実を隠さない**。

### C. 履歴として表示可能（時系列の実データ）
- `*_book.json` の trades[]/positions[] → **源泉別P&L曲線・エクスポージャ・DD**（MARKET画面の主役）。
- `market_memory.fingerprints[6000]` → **レジーム履歴のヒートストリップ**。
- `council.history` / `personnel.history` / `technology.history` / `treasury.history` / `reserve.history` → 機関の趨勢カウンタ。
- `progress.history` → 能力成長曲線（**現在2点のみ＝ほぼ横ばい。正直にそう出す**）。
- `hypothesis_ledger` 各仮説の created/status → **研究タイムライン**。
- `event_calendar.events[74]` → 前方カレンダー（未来の予定イベント）。

### D. 会長承認へ接続可能（既に単一書き手モジュールがある）
- `proposals.json` ← `proposals.decide(pid, approve, enable, arm_code)`（二重ロック）。
- `approvals.json` ← `approval.approve/reject(ticket_id)`（〇/x・auto/宿題）。
- → v2の「DECISIONS REQUIRED」は**これらを束ねた表示**。実行接続はPhase3で慎重に（下記10章）。

### E. 現時点でデータ不足（EMPTY/UNAVAILABLE と明示すべき）
- **intradayの市場チャート・複数時間軸・板・ティック**: 機関内に価格フィード無し（bookは合成練習）。
- **News（ニュースショック）**: ニュース源ファイル無し（event_calendarは経済イベントであってニュースではない）。
- **World Modelの深部**（Monetary Regime/Inflation/Liquidity/Credit/Currency Strength/Safe Haven/Cross-Market anomaly）:
  external_macro/macro_causalに一部のみ。大半はEMPTY。
- **Options/Order-flow の実データ**: vol_sell/stat_arbはあるが板・流動性は無し。

### F. 将来構想のみ（FUTUREとして枠だけ置く）
- **Knowledge Universe の時間旅行**（LIVE/1D/7D/30D/1Y/ALL）: 蓄積スナップショットが約2.5か月ぶんしか無い→部分的にALLのみ可、
  リッチ版はFUTURE。
- **真のストリーミング神経活動**: 現状は日次再生。intraday連続はFUTURE。
- **市場チャートへのAurelian認識オーバレイ（REGIME SHIFT/NEWS SHOCK/EDGE ACTIVE等）**: レジーム/イベント/免疫は実データで可、
  NEWS SHOCKはニュース源が来てから。

---

## 2. 画面構成 v2（5画面＋1将来）

| 画面 | 一言 | 主データ | 動的表現 |
|---|---|---|---|
| **COMMAND** | 中央司令室・神経活動 | source_family / discovery.provenance / digest / council / live_gate | ノード網が実遷移で発光 |
| **MARKET** | 源泉の市場端末 | *_book(P&L曲線) / carry等状態 / market_memory / validation.regime | 曲線・ヒートマップ・相関 |
| **INTELLIGENCE** | 世界理解 | world / external_macro / macro_causal / event_calendar | 地合い・因果地図・暦。未実装はEMPTY |
| **RESEARCH** | 思考過程 | frontier(壁) / discovery / hypothesis / validation / evidence | Discovery Feed・研究フローグラフ |
| **CHAIRMAN** | 意思決定 | scorecard / proposals / approvals / s2_floor / progress | TODAY・DECISIONS REQUIRED |
| **KNOWLEDGE UNIVERSE**(将来) | 知識成長 | 各 *.history + hypothesis + discovery | 時間旅行で網が広がる（FUTURE） |

---

## 3. COMMAND：中央ノード網（データ駆動の神経マップ）— 設計の核

**ノード（実在の器官・捏造なし）**
- 中心: `AUREL / Institutional Core`
- 源泉層(source_family): price_action / carry / arbitrage / options / macro / event（各々に健康色=verdict、大きさ=total_pnl、呼吸=breathing）
- 兵士層: 各源泉の soldiers（active/slot/quarantine で色）
- 器官: World / MarketMemory / Frontier / Discovery / Hypothesis / Validation / Knowledge / Risk(Immune) / Capital / Council / 会長承認

**エッジ（実データの線）**
- `discovery.candidates[].provenance.origin` が出所を明示：
  - `frontier.wall_diagnosis` → Discovery（壁が発見を方向づけ）
  - `frontier.cross_domain_key` → Discovery（hedge/shift_time/stand_aside を domain 経由）
  - `macro_causal.causal_map`（DXY→EM link_strength0.55 等）→ Discovery（線の太さ=link_strength）
  - `source_family.slot`（pullback空枠）→ Discovery
  - `discovery.recombination` parents[H-0007,H-0010,H-0014] → Discovery（**知識の複利＝生存エッジ同士の再結合**）
- `evidence.evidence_map/leadlag` → Hypothesis↔証拠のリンク
- `proposals` → 会長承認ノードへの上申線

**動き（疑似リアルタイム＝正直）**
- 朝の1拍で起きた実遷移（新discovery誕生・hypothesis生成・validation棄却・knowledge復帰）を
  JSON差分から復元し、線を順に発光させて「その日の神経活動」を再生。
- ライブ感の常時要素は「呼吸」と「最終更新hh:mm」だけ。**偽の流れは出さない**。

---

## 4. MARKET（源泉の市場端末）
- 主チャート: 源泉別P&L曲線（*_book の trades 累積）＋合成/実データ別（`_synthetic_practice` フラグを明示）。
- Asset Watch: 兵士×銘柄の状態表（personnel + carry.symbols）。
- Heatmap: 源泉×レジームの成績、または銘柄相関（market_memory）。
- Regime帯: market_memory.fingerprints のカラーストリップ。
- Aurelian認識オーバレイ: REGIME/EVENT WINDOW/AVOID/EDGE ACTIVE（実データ由来のみ。NEWS SHOCKはFUTURE）。
- **実価格チャート/複数時間軸/板は E（データ不足）→ 枠にUNAVAILABLEを明示**。

## 5. INTELLIGENCE（世界理解）— Market→World→Market
- 実装済: 地合い(world)・マクロ系列(external_macro)・因果地図(macro_causal.causal_map)・イベント暦(event_calendar)。
- 枠だけ置く（FUTURE, EMPTY表示）: Global State / Risk-On·Off / Monetary Regime / Inflation / Liquidity / Credit /
  Currency Strength / Safe Haven / Cross-Market anomaly / Historical similarity / 仮説確率 / 反証条件。
- **無いものは捏造せず EMPTY/FUTURE**。

## 6. RESEARCH（思考過程）— 壁→鍵→仮説→検証→知識→Frontier更新
- 研究フローグラフ: frontier.wall_diagnosis(壁) → discovery(鍵) → hypothesis → validation → knowledge(生存) → frontier更新 の環。
- **DISCOVERY FEED**（時系列ログ）: discovery.candidates と hypothesis の created/status から
  `HH:MM 新規異常検出 / 研究要求生成 / 類似局面一致 / H-xxxx生成 / OOS棄却 / cross-source検証中` を**実イベントから**生成。
- 棄却理由・採用候補・未知Edge(level X)・過去死亡仮説の再利用(recombination)も表示。

## 7. CHAIRMAN（意思決定）
- TODAY / PROFIT / RISK / WORLD / DISCOVERY / FRONTIER / AUREL CEO VIEW / SYSTEM HEALTH。
- **DECISIONS REQUIRED（正式承認センター）**: proposals + approvals + validation.awaiting_chairman を1枚に。
  各案件に「何を / なぜ / 根拠 / Validation / Historical evidence / Risk / AURELの推奨」を展開。
- 操作は段階導入（10章）。**二重ロック・Live Gate・会長承認権限は絶対に弱めない。**

## 8. 動的表現の正直ルール（憲章「血を捏造しない」の適用）
- 動いてよい: 実データに対応する変化 / 時計 / 呼吸(実ボラ由来) / その日の実遷移の再生。
- 禁止: データ根拠のない流れ・偽ティック・意味のないネオン。
- 無いデータは EMPTY / UNAVAILABLE / FUTURE を明示。

---

## 9. 実装方式（段階・自己完結ファースト）

- **Phase 1（推奨・最初の着工単位）**: 自己完結HTML(file://)で5画面。データは生成時に焼き込み（現行方式の拡張）。
  ノード網・源泉P&L曲線・Discovery Feed・DECISIONS REQUIRED を実装。**サーバ不要・ダブルクリックで開く・金ゼロ・読取専用。**
- **Phase 2（任意）**: 極小のローカル**読取専用**サーバ（localhost）で、開いたまま数十秒ごとに最新JSONを再読込→自動更新。
  外部公開なし・秘匿情報なし・書込みなし。
- **Phase 3（任意・最重要注意）**: CHAIRMANのボタン（DETAILS/REJECT/APPROVE PAPER）を単一書き手モジュール
  （proposals.decide / approval.approve）へ接続。**APPROVE PAPER でも二重ロック(enable_live+arm_code)は温存、実弾は不可、
  鍵は会長の手のみ。** 却下/様子見は無鍵で可。実装は会長の明示GO必須。

**触らない境界**: aurel_life.html / g4_(プロップ) / G2聖域 / US100 FINAL / 本番ノブ(write_back単一書き手) / 凍結backtester。
新規は circulation 配下の独立HTML（＋Phase2で独立サーバ）のみ。

---

## 10. AUREL自身の提案（改善案）
1. **神経活動の"心拍ログ"**: 毎朝の1拍を1行イベントとして追記する軽い台帳を新設 → COMMAND再生とKnowledge Universeの燃料になる
   （現在は差分復元だが、明示ログにすると履歴が濃くなる）。
2. **源泉P&Lの"合成/実データ"二色分け**を徹底 → 見栄えのための誇張を構造的に防ぐ（正直UIの担保）。
3. **DECISIONS REQUIRED を1つの `decisions.json` に集約**（proposals+approvals+validation.awaiting を単一書き手が公開）→ 画面が単純化。
4. **EMPTY/FUTUREタイルを最初から常設**（世界理解の未実装項目）→ 「次に何を実装すべきか」のロードマップが画面自体になる。
5. **KNOWLEDGE UNIVERSEの種**: 今から日次スナップショットを1枚ずつ保存し始める → 半年後に本物の"成長の時間旅行"が撮れる（今始めるほど価値）。

---

## 11. 会長へ：決めてほしいこと（承認ポイント）
1. **Phase 1 に着工してよいか**（自己完結HTMLで5画面＋中央ノード網。読取専用・金ゼロ・境界厳守）。
2. **最初に作る1画面**の優先順（推奨: COMMANDのノード網 → RESEARCHのDiscovery Feed → MARKETのP&L曲線）。
3. Phase 2（ローカル自動更新）と Phase 3（承認ボタン）を**将来オプションとして許可するか、今は保留か**。
4. 改善案10章の①③④⑤を採用するか（特に⑤の日次スナップショット保存は「今すぐ始めるほど得」）。

**現状**: 設計提出済み。実装は全面凍結。会長のGO単位（Phase/画面）が決まり次第、その1単位だけ着工する。
