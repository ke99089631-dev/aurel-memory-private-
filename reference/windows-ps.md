# PowerShell 5.1 (Windows) Pitfalls

> AUREL を Windows 上で構築する際に踏んだ罠と回避策。S2 で実体験。

## 1. BOM必須 (UTF-8 encoding)

PS 5.1 はBOMなしUTF-8ファイルを **ANSI (Windows-1252)** として解釈する。
非ASCII文字（日本語、エムダッシュ `—`、矢印 `↑↓` 等）が含まれると、後続バイトが壊れ、構文解析が完全に崩壊する（例: `"|---"` の中の `-` が単項演算子と解釈される）。

**対策:**
```powershell
$p = "path\to\file.ps1"
$c = Get-Content $p -Raw -Encoding UTF8
$c | Out-File $p -Encoding utf8   # ← BOM付与される
```

Write tool で `.ps1` を書いた直後は必ずこの BOM 再保存を行う。

## 2. `$args` 自動変数との衝突

関数の `param()` に `$args` を使うと PowerShell 自動変数と衝突して引数が消える。

**Bad:**
```powershell
function Foo { param($args) Write-Host $args.Count }   # 常に 0
```

**Good:**
```powershell
function Foo { param($argv) Write-Host $argv.Count }
```

## 3. 単一要素 → `.Count` の罠

`ForEach-Object` が単一の hashtable を出力した場合、結果は配列ではなく hashtable 単体。
`.Count` は要素数ではなく **hashtable のキー数** を返す。

**Bad:**
```powershell
$projs = Get-Things  # 単一なら hashtable @{slug=...; data=...} が返る
$projs.Count         # → 2 (keys count, NOT 1)
```

**Good:**
```powershell
$projs = @(Get-Things)   # 必ず配列化
$projs.Count             # → 1
```

## 4. `2>&1` で `$?` が壊れる

PS 5.1 でネイティブ実行ファイル (git, npm, etc.) の stderr を `2>&1` でリダイレクトすると、
各行が NativeCommandError でラップされ、exit 0 でも `$?` が `$false` になる。

**対策:** stderr は既にキャプチャされる。`2>&1` を付けない。必要なら `2>$null`。

## 5. パイプライン連結演算子の不在

PS 5.1 には `&&` `||` がない。

**代替:**
```powershell
cmd1; if ($?) { cmd2 }   # cmd1 が成功したら cmd2
```

---
_Updated: 2026-05-19_
