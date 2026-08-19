---
tags: [reference, infra, shirei-shitsu, delivery]
type: reference
updated: 2026-08-14
---

# この指令室への定時配信アーキテクチャ（機関 朝ブリーフ）

## 判明した事実（2026-08-14）
- **会長が実際に使う「指令室」= aurel.mjs の `home` ルーム**。証拠: この claude.exe(SDK, PID可変) の親プロセス = `node aurel.mjs --bind 0.0.0.0`。
- 旧 HTML マスターコンソール（aurel_life.html / AUREL会社_sample_v4.html, 127.0.0.1:7878）は**会長は使っていない**。配信先として無意味。
- **会長の通常メッセージと同一の経路 = `POST /api/projects/home/send {prompt}`**（localhost は認証不要）。これで走るターン出力は runTurn→broadcast('done')＋messages.jsonl 永続化で、会長の画面に確実に出る。

## 過去の空振りの原因
- proactive.mjs の `postToMother` が SSE 宛先に**存在しない `mother.subscribers` を使用**（正は `p.sseListeners`）。さらにディスク非永続。→ 誰にも届かずファイルに溜まるだけだった。
- 教訓: 「生成できた」≠「届いた」。配信は必ず**会長が実際に読む経路**で疎通確認する。

## 恒久配信(B)の実装
- OSタスク **`AUREL_Shirei_Brief_Deliver`**（毎日 07:06 / Interactive / StartWhenAvailable=True / 現ユーザー）。
  - 実行: `C:\Users\user\.aurel\bin\deliver_brief_to_room.cmd`
  - 中身: `curl POST http://127.0.0.1:7878/api/projects/home/send --data-binary @brief_room_payload.json`
  - ペイロード: `C:\Users\user\.aurel\bin\brief_room_payload.json`（UTF-8。「chairman_brief_latest.txt を読んで会長に提示せよ」）
- ブリーフ生成は既存 `AUREL_Chairman_Brief`（07:05, `run_chairman_brief.bat --no-send`）が `chairman_brief_latest.txt` を吐く。配達はこの新タスク(07:06)が担う。
- ログ: `C:\Users\user\.aurel\state\logs\brief_deliver.log`（+ `.last` に直近レスポンス）。疎通OKの印 = 202。room busy時は 409。

## 制約（会長へ明示済み）
- **aurel.mjs が生きている＝会長がログイン済みである必要**。ロック/ログイン画面のまま(未ログイン)では aurel.mjs 自体が停止しているため配達不可（aurel.mjs系タスクは Interactive/logon 起動）。会長の実運用（日中ログイン）では問題なし。
- PC が 07:06 に起動していない場合、StartWhenAvailable で**復帰時に1回だけ後追い配達**。
- 別件: 機関の日次拍 `AUREL_Circulation_WriteBack` の S4U 化（未ログインでも07:00自走）は会長のUAC 1クリック待ち（`機関_再起動でも回す設定.cmd`）。

## 補足
- aurel.mjs 側の `postToMother` バグ修正はディスク上に済（sseListeners＋assistant_text/done＋appendMessage）。ただし未再起動のため未ロード。B は /send 経路で proactive に依存しないため、この修正の要否とは独立。

## [2026-08-19] 修正: 「承認待ち」カウントのズレ
- 症状: 朝ブリーフ「研究レーン 会長承認待ち 2」だが、その2件(H-0007/H-0014)は8/16に会長承認済み(chairman_approval.approved=true)。
- 原因: `circulation/hypothesis_ledger.py` `_summarize()` が `awaiting_chairman = by_state["promoted_candidate"]` と“棚上げ候補”を全数カウントし、承認済みを差し引いていなかった。
- 修正: promoted_candidate のうち `chairman_approval.approved` が真の分を除外して数える。再生成で awaiting_chairman=0 を確認。chairman_brief はこの summary を読むだけなので連動して0に。
- 安全: 数え方のみ。戦略/鍵/金/プロップ非接触。紙のみ。
