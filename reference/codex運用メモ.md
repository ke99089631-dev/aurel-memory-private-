# Codex 端末運用メモ（2026-06-05 確定）

## 起動方法（AURELが端末から叩く）
- 実体: `C:\Users\user\AppData\Roaming\npm\codex.cmd`（npmグローバル。codex-cli 0.136.0）
- bashにはPATHが通っていない → 実行前に `export PATH="$PATH:/c/Users/user/AppData/Roaming/npm"`
- 基本形: `echo "<プロンプト>" | codex exec --skip-git-repo-check`
- 既定: model=gpt-5.5 / sandbox=read-only / approval=never / workdir=カレント
- 出力はstdoutに最終回答が出る。長尺は `| tail -N` で末尾回収。

## 役割（会社内の位置づけ）
- Codex = AURELが指揮する「実行部隊／社外頭脳」。常駐エージェント(ノード)ではなく、AURELが必要時に叩く道具。
- 用途: ①重い設計のセカンドオピニオン(社外監査) ②コード生成/レビューの下請け ③並列調査。
- 安全: 既定read-onlyなので勝手に書かない。書き込み/実行を伴う作業はAURELが結果を検証してから自分の手で反映。
- 実弾・秘密情報・決裁事項はCodexに渡さない/任せない（Master決裁の境界はAUREL側で守る）。
