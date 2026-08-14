---
tags: [reference, kikan, strategy, adoption, h0007]
type: reference
updated: 2026-08-14
---

# H-0007 「予定イベント接近では戻りを見送る」採用と実装（2026-08-14）

## 何を採用したか
- 仮説 H-0007 = mean_reversion（戻り/逆張り）を、決算・経済指標など**予定された事件の直前は見送る**（サプライズで一方向に暴走し戻らない事故を避ける）。
- ガントレット全段通過の唯一候補（他9件は却下）。会長が2026-08-14に採用GO（二重ロック）。

## 会長への説明（正式記録）
- 採用＝機関の台帳に「会長が採用を決めた」と永久記録するのが正式。承認しても勝手に実装・送金はされない設計。
- ledger NOTE: `chairman_approval`(seq976) → `chairman_approval_implemented`(seq978)。すべて paper・金ゼロ。

## 実装した中身（construction）
- ファイル: `C:\Users\user\AssetEmpire\empire\circulation\mean_reversion.py`
- 追加: 定数 `MR_EVENT_GATE_DAYS=1`、`_event_near_dates()`（接近日プロバイダ）、`_real_trades(..., event_near=None)` にゲート1行、`rebuild_from_bars` で接近日を計算し `book["_event_gate"]` に状態記録、`assess` が `event_gate` を公開。
- selftest 追加: 接近日を注入すると戻りが1件抑制される（機構は正しい）／実運用パス(None/空)は**バイト同一で不変**。`python -m circulation.mean_reversion --selftest` = PASS。

## ★正直な壁（最重要）
- H-0007 は「いつイベントが近いか」を知る**実イベントカレンダー/ニュースフィード**が必要。**機体にそれは無い**（data/ には bars_*.csv の価格のみ。event_driven 源泉も同じ理由で正直に休眠）。
- ゆえに `_event_near_dates()` は**空集合**を返す＝ゲートは今は**発火ゼロ・P&Lへの影響ゼロ**。「機構は装填済み・血は通さない」正直な休眠。**イベントを捏造しない**（機関の憲章「血を捏造しない」を厳守）。
- 実フィードを接続した日から、このゲートは自動で効き始める（A項＝データ接続は別作業・会長判断）。

## 実イベントカレンダー接続（2026-08-14 会長GO「つなごう」）— 完了
- 新モジュール `circulation/event_calendar.py`: ForexFactory 週次カレンダー（faireconomy ミラー XML・**APIキー不要・実データ**）を読取専用で取得→ `data/circulation/event_calendar.json` に公開。
  - 対象は **High重要度のみ**（大きな予定＝サプライズ源）。国(通貨)・日付・時刻付き。
  - ★制約: 無料フィードは**今週分（約7日）のみ**（nextweek は404）。→ 毎日取り直して直近1週間を最新化（rolling）。
  - 取得失敗時は前回良データを `stale=True` で保持。**でっち上げない**（selftest で検証）。
- ゲート配線: `mean_reversion._event_near_dates(currencies)` がカレンダーを読み、器の通貨に関係する High イベントの前後 `MR_EVENT_GATE_DAYS(=1)` 日を接近日に。`rebuild_from_bars` が器ごと通貨一致で近接日を計算し戻りを見送る。
  - 器→通貨: EURCHF=EUR/CHF, EURGBP=EUR/GBP, AUDCAD=AUD/CAD, USDJPY=USD/JPY, NAS100=USD。
- 毎日更新: `mean_reversion.step()` 冒頭で `event_calendar.refresh()` を best-effort 呼び出し（ネット不通でも非致命・前回保持で続行）。
- selftest 全通過: 接近日展開(±1日)・通貨絞り・gate_days<=0無効・注入で戻り1件抑制・既定パス不変。

## 現在の状態（2026-08-14）
- カレンダー: fetched_ok=True, stale=False, n_high=11, high_dates=[08-11,08-12,08-13]。
- `mean_reversion_book.json` の `_event_gate`: armed=True, **active=True**, near_dates=4 (08-10〜08-13), gate_days=1。
- total_pnl は不変(2.177791)=その接近日には held器の戻り建玉が無かっただけ。**機構は稼働中**で、今後 High イベント日に戻りシグナルが出れば自動で見送る。
- 台帳: seq976 承認 / seq978 実装 / seq981 カレンダー接続。すべて paper・金ゼロ・プロップ非接触。

## 運用メモ
- カレンダー鮮度は日次 step 依存。指令室/PCが動いていない日は前回保持(stale)。復帰時に最新化。
- 効きを強めたい時のノブ: `MR_EVENT_GATE_DAYS`（前後日数）、`GATE_IMPACTS`（Highに加えMedium等）。変更は会長GO後。
