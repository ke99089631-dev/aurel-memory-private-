# バグ修正: 返信が消える (SSE未復旧) 2026-06-03

## 症状
Master のチャットで AUREL の返信が表示されない（「返信が消えている」）。長短・ツール有無に関係なく発生。

## 診断
- messages.jsonl は 349行すべて正常・パース失敗ゼロ → サーバの保存は完璧。
- 返信はフルテキストで保存され、'done' も broadcast されていた。
- 結論: **クライアント表示のみの問題**。
- 根本原因: `aurel_life.html` の `openStream()` に SSE の再接続/再同期が無い。
  - EventSource が一度切れると、その間に発火した 'assistant_text'/'done' イベントは失われる（サーバは Last-Event-ID 再送をしない）。
  - send() は返信描画を SSE だけに依存し、履歴の再取得をしない。
  - → PCスリープ/接続断のあと、保存済みの返信がブラウザに届かず「消える」。

## 修正 (aurel_life.html, script#4 module内)
1. `resyncMessages(id)`: サーバの /messages から会話を再取得して再描画。
2. `openStream`: `onopen` で再接続を検知し resync、`onerror` で CLOSED 時に強制再接続。
3. `send()`: 送信後ウォッチドッグ。SSE不調 or 返信未着なら 7秒間隔で resync（onDoneで解除）。
- バックアップ: snapshots/aurel_life.html.pre-ssefix-20260603-1725
- 構文検証: node --check で [SYNTAX OK] 確認済。

## 反映方法
- HTML は no-store でディスクから毎回配信 → **ブラウザを再読込(Ctrl+Shift+R)するだけ**。デーモン再起動不要。
- 再読込時 activate() が全履歴を再取得 → 過去に「消えた」返信も全て復活する。

## 教訓
- リアルタイムUIは「ライブ配信」だけに依存させず、必ず権威データ(保存済み)との再同期経路を持たせる。
