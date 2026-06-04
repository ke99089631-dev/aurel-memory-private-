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

## 実戦評価（2026-06-05 conduit Phase1監査で確認）
- コード監査は本物の戦力。AURELが見落とした「公開ntfyへのPII送信」を検出。
- ただし全指摘が正しいわけではない → **「Codex提案・AUREL検証/決裁」を徹底**（鵜呑み禁止）。
- Master評価「実力はわかった」。当面は常駐させず、重い監査/生成時に呼ぶ運用で確定。

## 部門横断での今後の用途（Master示唆 2026-06-05）
- **資産帝国事業部で活用予定**: EA/戦略コードの監査、バックテストコードのバグ/ルックアヘッド検出、
  リスク計算(Kelly≤0.05, ES/CVaR, PF/RF)の実装レビュー、約定品質監査ロジックのセカンドオピニオン。
- 収益事業部: LP/フォーム/通知経路のセキュリティ監査（今回実証済み）。
- いずれも read-only で安全に走らせ、結果はAURELが検証してから反映。実弾判断・秘密情報は渡さない。
