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

## 状態
- `data/circulation/mean_reversion_book.json` の `_event_gate`: armed=True, active=False, near_dates=0, gate_days=1。
- 次に効かせるには「実イベントカレンダー接続」という別のデータ作業が要る（会長に提示済み）。
