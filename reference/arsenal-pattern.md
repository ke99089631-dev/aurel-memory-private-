# Arsenal Pattern — 武器追加プレイブック

> 新しいAI/API/ツールを AUREL に装備するための再現可能手順。S3 で確立。

## 全体フロー

```
1. researcher 派遣 → API仕様・料金・SDK状況の一次確認
2. arsenal/_template/ をコピー
3. manifest.json を埋める
4. invoke.ps1 を実装
5. secrets.json に認証情報追加
6. aurel arsenal sync
7. aurel arsenal equip <slug>
8. テスト invoke → arsenal-log.jsonl で動作確認
9. ダッシュボード/ブリーフィングに反映確認
```

## マニフェスト記述の勘所

- **`use_when` / `avoid_when`** を必ず具体的に書く。Capability Router (S5) がここで判断する
- **`cost_tier`** は `free | low | medium | high | premium` の5段階
- **`latency`** は `instant | seconds | minutes | hours`
- **`io_schema`** は JSON Schema 風に書く（型情報があれば router がバリデーションできる）
- **`credentials_ref`** は `secrets.json` のキー名のみ。実値は manifest に絶対書かない

## invoke.ps1 規約

- stdin から JSON 入力を受ける（`io_schema.input` の形）
- stdout に JSON 出力（`io_schema.output` の形 + メタ）
- 標準終了コード:
  - `0` 成功
  - `1` 汎用失敗
  - `2` 入力不正
  - `3` 認証/credentialエラー
  - `4` 上流API障害
  - `5` レート制限
- 失敗時も JSON で `{ "status": "error", "code": "...", "message": "..." }` を返す

## 内部艦隊 vs 外部API

- 内部艦隊 (`category: internal`, `endpoint_type: internal`) は Claude Code の `Agent` ツール経由で呼ぶ
  - `agent_subagent_type` と `system_prompt_file` (system.md) を持つ
  - `invoke.ps1` はプレースホルダ（直接 PS から叩く想定がないため）
- 外部API は HTTP / SDK 経由
  - `Invoke-RestMethod` を invoke.ps1 内で使う
  - 必ず `credentials_ref` から secrets.json を読む

## エンコーディング厳守

- 全 .ps1 ファイルは **UTF-8 BOM 付き**で保存（PS 5.1 制約）
- 全 .json ファイルを読む時は **`Get-Content -Raw -Encoding UTF8`**
- 書く時は **`Set-Content -Encoding UTF8`** または **`Out-File -Encoding utf8`**
- これを怠ると日本語が文字化けし、ConvertFrom-Json が崩壊する（S3 で実際に踏んだ）

---
_Established: 2026-05-19 (S3)_
