---
tags: [reference, infra, safeguard, sessions, mirror-frames]
type: reference
updated: 2026-08-14
---

# 画面共有キャプチャの自動整理（mirror-frame capper）2026-08-14

## 背景 / なぜ作ったか
- 車事業の部屋 (p_143c5262) が「画像制限」でセッションが開けなくなった。
- 原因: 画面共有のキャプチャ画像 (mirror-frame) が会話に溜まりすぎ。1枚ごとは
  1280x675 で寸法上限(2096px)以下だが、**枚数**が積み上がって上限を超えた。
- 画像は `[添付ファイル: C:\Users\user\.aurel\state\mirror-frames\mirror-<ts>-<hex>.jpg]`
  というタグで各 `projects/*/messages.jsonl` に埋め込まれ、モデル送信時に画像化される。
- 生成元: `C:\Users\user\.aurel\daemon\companion.mjs` の `saveMirrorFrame()`（保存先
  `~/.aurel/state/mirror-frames`）。ただし messages.jsonl へタグを書く本体は特定できず →
  「書く側を直す」のではなく「溜まったら間引く見張り役」で対処した（確実・低リスク）。

## 作ったもの
- スクリプト: `C:\Users\user\.aurel\bin\mirror_frame_capper.py`（読み書きのみ・金/鍵/プロップ非接触）
  - 各 `projects/*/messages.jsonl` のキャプチャタグを**最新 KEEP_RECENT=2 枚だけ残し**、
    古い分を `[画面キャプチャ:古い分は自動整理済み]` に置換。**会話テキストは一切消さない**。
  - `IDLE_GUARD_SEC=90`: 直近90秒に更新された部屋は触らない（書込中の競合回避）。
  - 書込は temp→`os.replace` の原子的置換（途中失敗でも壊れない）。
  - ディスク回収: どの会話からも参照されず `DISK_STALE_DAYS=3` より古い `mirror-*.jpg` を削除。
  - `--selftest` あり（一時ファイルで検証・本物に触れない）。PASS 済み。
- 自動起動: Windowsタスク `AUREL_MirrorFrameCapper`、**10分ごと**、`pythonw.exe`（画面出さず）。
  - 実行体: `C:\Users\user\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe`
- ログ: `C:\Users\user\.aurel\state\mirror-capper.log`

## 初回実行の結果（2026-08-14 21:33〜21:43）
- home 部屋: キャプチャ 86枚→2枚（全2,133行 JSON妥当・テキスト無傷を確認）。
- p_962e3092: 3枚置換→2枚保持。p_localboost(2)/p_143c5262(0) は対象外。
- ディスク: **削除 144,923枚 / 回収 約10.3GB**（参照中6枚は保持）。
- 全部屋の一回きりバックアップ: `messages.jsonl.capbak-20260814-213250`。

## 調整ノブ（変更は会長GO後）
- `KEEP_RECENT`（残す枚数）、`IDLE_GUARD_SEC`（書込中回避の猶予）、`DISK_STALE_DAYS`（画像削除の古さ）。

## 運用メモ
- 初回はフォルダが巨大で掃除に約10分。以降は残数が少なく高速。
- 車事業の部屋復旧も同日実施（別途 tag 置換、backup: `messages.jsonl.bak-20260814-191139`）。
- 会長への案内: 画面共有はつけっぱなしでも部屋が死ににくくなった。操作不要。
