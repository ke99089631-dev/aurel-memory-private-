---
doc_id: AURELIAN-EXECUTOR-PROPOSAL-v1
tags: [institution, executor, proposal, live-gate, pinned]
type: build-proposal
created: 2026-09-16
status: 段1 着工GO（会長「GOだ」2026-09-16）→ executor_shadow.py 実装・selftest PASS・cadence 配線済（5営業日の実見待ち）。段2/段3 は別GO
owner: AUREL
approver: 会長（KEIKI MAEDA）
source: AURELIAN-REVIEW-2026-09.md §3-A「畑の鍬」
---

# 機関の発注器（畑の鍬）— 起案 v1

> 一言: いまの Aurelian は「鍵穴」まではあるが「鍬」が無い。資金が来た日に1円も動かせない。
> 施錠したまま鍬を作っておき、会長が鍵を回した時だけ動く。この書は「何を・どの順で・どこまで」の設計。

## 0. 位置づけ
- 対象＝機関（Aurelian）自身の口座。**プロップ(g4_)・会長の裁量口座とは別の口座**（「頭は一つ・手と財布は別々」）。
- 既定＝**施錠**。二重ロック（`enable_live=True` ＋ `arm_code='CHAIRMAN-GO'`）は会長のみ。AUREL は鍵を回さない。
- 段1（建設）は**紙の口座に影の発注**を流すだけ＝金ゼロ。実弾は段3以降・源泉ごとに会長GO。

## 1. 既にある部品（読取で確認済・2026-09-16）
| 部品 | 場所 | 状態 |
|---|---|---|
| 発注の関所（防衛→発注→台帳） | `execution/gateway.py` TradeGateway / PaperBroker / Mt5LiveAdapter(未武装スタブ) | 稼働（紙） |
| 本物のMT5アダプタ | `execution/mt5_live.py` RealMt5Adapter / Mt5Session（成行＋**SL/TP同時設置**・**約定後SL照合 reconcile_sl**・付け直し・緊急クローズ・deal履歴で真の約定価格） | **8/16 に $53 実口座で実約定→照合OK（C4-PASS）** |
| 防衛（床・予算・pretrade） | `defense/risk_engine.py` DefenseCommand（-8%新規停止／-12%半減／-15%KILL・ALLOW/HALVE/REJECT） | 稼働（凍結BT＋単体で発火実証 8/16） |
| ロット換算 | `execution/sizing.py`（単位⇄ロット・契約サイズ・最小ロット床） | 稼働 |
| 台帳（改竄検知の鎖） | `ledger/ledger.py`（hash chain・ORDER_SUBMIT/FILL/RISK_EVENT） | 稼働（chain_verified=True 毎朝） |
| 鍵穴 | `circulation/live_gate.py`（readiness 7条件・arm 二重ロック・**executor_present=False**） | 稼働（LOCKED） |
| 実弾フロアの計器 | `circulation/s2_floor_monitor.py`（源泉ごと 30日前進・血・床・芽） | 稼働 |
| 死活3層 | プロップ側 runner/watchdog/keepalive（7/25 kill/再起動実証） | **プロップ専用＝機関側には無い**（読んで別名で移植） |

**結論: 部品の8割はある。無いのは「循環の紙の持ち高を、口座の目標持ち高に翻訳し、差分だけを施錠のまま流す配管」。**

## 2. 建てるもの（E1〜E8・全て新規モジュール・既存とプロップは無改変）
- **E1 目標持ち高の翻訳器** `circulation/executor_targets.py`
  7源泉の公開面（carry.json / trend_follow.json / mean_reversion.json …）の held と重みを読み、「口座の目標ポジション（銘柄・向き・名目）」の1枚に畳む。資本は `capital_book`/会長設定の**運用元本**（段1は紙の 1.0）。
  **対象は第1段で FX/CFD/暗号のみ**（carry・trend_follow・mean_reversion）。**オプション（vol_sell/tail_hedge）は MT5 では建てられないので対象外**（別口座種別が要る＝将来の別起案）。
  銘柄写像＝機関の記号（AUDUSD, SPY, BTC…）→ 口座の銘柄（AUDUSD, US500, BTCUSD…）。写像に無い銘柄は**建てない**（fail-closed・捏造しない）。
- **E2 口座の鏡** `circulation/executor_mirror.py`
  実 equity／建玉／証拠金／銘柄仕様（契約サイズ・最小ロット・刻み・取引時間）を**読むだけ**で取得し、`account_mirror.json` に公開。段1は PaperBroker の紙口座を鏡に映す。
  ★プロップ側で「⑩ 実equity→DefenseCommand→pretrade の配線」が未配線だった穴を、機関側では**最初から配線**する（鏡の equity が防衛に流れる）。
- **E3 差分発注器** `circulation/executor_reconcile.py`
  目標（E1）− 現在（E2）＝差分だけを注文に。ロット丸め・最小ロット床（`sizing.py`）・証拠金上限・**サーバー側SL同時設置**（bracket）・**約定後SL照合→付け直し→失敗なら緊急クローズ**（`mt5_live.py` の既存機構を呼ぶ）。
  発注は必ず `TradeGateway.execute()` 経由＝防衛の pretrade を通らない注文は物理的に出ない。
- **E4 予算門** `circulation/executor_budget.py`
  日次 −2%／週次 −4%（プロップと同じ語彙）＋床 −8/−12/−15（deadman）。実 equity で追跡し、門が閉じたら E3 は新規ゼロ・KILL 時は全クローズ。**門は「実際に閉じるのを見た」テストを段1で紙口座で実施**（8/16 の教訓）。
- **E5 死活** `empire/scripts/run_executor_*.bat` ＋ Windows タスク（Runner／Watchdog／Keepalive の3層・プロップと別名）
  心拍ファイル・自動再起動・再起動後の台帳照合。**ゾンビ検知**（心拍は進むが判断ファイルが古い）を最初から入れる（F05-03/04 の未解決を機関側で先に塞ぐ）。
- **E6 施錠と鍵** `live_gate.py` 拡張（既存関数は無改変・追加のみ）
  `executor_present` を段3以降に True へ。**arm の実体**＝会長が自分の手で置くファイル `data/circulation/LIVE_ARM.json`（enable_live）＋会長がコマンド実行時に打つ合言葉（arm_code＝ファイルにも記憶にも書かない）。AUREL のセッションからは `LIVE_ARM.json` を書かない（**書き込み禁止を CLAUDE.md/自己規律に明記**）。killswitch ファイル `DISABLE_EXECUTOR` で即停止。
- **E7 口座分離のハードガード** `executor_mirror` 起動時
  `expected_account`（login/server）を照合し、不一致なら**起動拒否**（C-5）。裁量口座 27972608・プロップ口座・$53 テスト口座を**拒否リスト**に明示。MT5_PATH 名指し固定（8/16 の穴の恒久対策を機関側で先に実装）。
- **E8 乖離台帳** `data/circulation/executor_divergence.jsonl`
  紙の目標 vs 実際の約定（価格・時刻・スリッページ・拒否理由）を毎回記録。段3の「紙と実弾のズレ」実測＝ `cost_table` の実測差替の源。

## 3. 段階（各段が会長GO単位・段1は金ゼロ）
| 段 | 中身 | 金 | 完了の定義 |
|---|---|---|---|
| **0** | 本起案 | 0 | 会長が読み、順番と対象を承認 |
| **1 建設（影）** | E1〜E4・E6〜E8 を紙口座（PaperBroker）で建て、**毎朝07:00の実循環に「影の発注」を配線** | 0 | 実循環で 5営業日、紙の目標と紙の口座の乖離ゼロ／予算門が紙で「閉じる」のを実見／台帳 chain_verified／live_gate LOCKED／selftest 全PASS |
| **2 接続試験（読むだけ）** | 機関用口座（会長が用意）の口座情報・銘柄仕様を E2 で読取。発注なし | 0 | 鏡に実 equity と銘柄仕様が映る／E7 が正しい口座だけ通し、拒否リストを弾く |
| **3 極小実弾** | 会長の二重ロック → 最小ロット1本（C-4 と同じ作法：約定→SL照合→即クローズ） | 極小 | 実約定1本の全経路（防衛→発注→SL照合→台帳→乖離記録）を実見。E8 から実コストを `cost_table` へ |
| **4 源泉ごと解錠** | S2フロア（30日・real・床・芽）に達した源泉だけ、会長が源泉ごとに鍵を回す | 極小→漸増 | LIVE-GATE-CRITERIA v2 のとおり |

## 4. やらないこと（不変）
- プロップ(g4_)のコード・データ・タスク・venv に**触れない**（読んで別モジュールに書く。凍結ハッシュ不変）。
- 会長の裁量口座に**接続しない**（拒否リスト）。
- 出金権限のあるキーを使わない。LLM を発注経路に置かない（決定的）。
- オプション兵の実弾化は本起案の範囲外。
- 段1で `executor_present=True` にしない（紙口座は発注器ではない）。

## 5. 会長の手が要ること
1. 段0: 本起案の承認（順番・対象・「オプションは対象外」の了解）。
2. 段2まで: 機関用口座の準備（証券会社の選定・開設・**入金は段3の直前でよい**）。
3. 段3: 二重ロック（`LIVE_ARM.json` を自分で置く＋合言葉）。AUREL は鍵を回さない。

## 6. 工数と危険
- 段1＝1〜2セッション（既存部品の配線が大半）。段2＝口座が来れば1時間。段3＝会長の手＋AUREL 1時間。
- 危険1: **単位の取り違え**（ロット／単位／契約サイズ）→ E3 は `sizing.py` と `symbol_info` だけを使い、selftest で往復変換を検証。
- 危険2: **口座衝突**（7/30 の ETH 事故）→ E7 ハードガード＋拒否リスト。
- 危険3: **ゾンビ**（心拍あり判断なし）→ E5 に判断ファイル鮮度の検知を最初から。
- 危険4: **紙と実弾の乖離**（7月の「検証した機械と走る機械が別物」）→ E8 で毎回記録し、乖離が出たら段を戻す（G0 の思想）。

## 7. AUREL の推し
段1の着工GOを頂ければ、明日の実循環実見（載せ替え5件のクローズ）の後に着手する。段1は金ゼロ・施錠のまま・既存無改変で、機関に「鍬」の形が生まれる。
