---
tags: [reference, prop, mt5, safety]
type: reference
updated: 2026-07-11
---

# MT5 端末分離メモ（トライアル ≠ 実弾）

## 2026-07-11 判明した本マシンのMT5構成

- 本PCの MT5 は **1インストールのみ**: `C:\Program Files\MetaTrader 5\terminal64.exe`
  - データフォルダ: `C:\Users\user\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075`
- この端末が実際に認証・接続している口座（journalログ確定）:
  - **口座 `27972608` / サーバ `VantageTradingLtd-Live`（会長の実弾ライブ口座・本人確認済）**
- FundingPips-Trial（口座 `40000162046`）は**この端末で一度も接続成功していない**。
  - 画面タイトルに出た「40000162046 - FundingPips-Trial」は**失敗設定の残像**（cached）。
  - スマホは FundingPips 専用アプリ（正しいサーバ内蔵）なので入れる。PC端末は Vantage 用で FundingPips サーバ認証が通らない。

## 症状と誤診の履歴（再発防止）

- python `MetaTrader5.initialize()` の症状:
  - 既存端末が起動中に資格情報で接続 → **-6 Authorization failed**
  - 端末killしてpython起動 → **-10005 IPC timeout**（実接続できないアカウント＝ハンドシェイク不成立）
- 一時「端末が管理者権限で権限不一致」と誤診したが**誤り**。
  - 真因は**このBash/PowerShellツールのサンドボックス**が Program Files / AppData\Roaming\MetaQuotes の**ファイル読取をブロック**していただけ。
  - `dangerouslyDisableSandbox: true` にすると端末データフォルダ・logs が読めた。→ **MT5のログ調査時はサンドボックス解除が必要**。

## 鉄則（Fable5/会長）

- **審査(トライアル)は実弾の冷たい口座と絶対に混ぜない。** 同一端末に同居させない。
- よって FundingPips-Trial は**別インストールのMT5（別データフォルダ）**で動かす。

## 正しい起動手順（会長の手＝GUI）

1. FundingPips ダッシュボードから**専用MT5をDL → 別フォルダに新規インストール**（例 `C:\FundingPips MT5\`）。Vantage端末と分離。
2. その FundingPips 版で `40000162046 / FundingPips-Trial` にログイン（緑=接続）。
3. AUREL は**その FundingPips 専用端末を path 名指しでアタッチ**。connect_assert_measure の口座アサート(login==40000162046)で Vantage実弾へは絶対に触れない。
   - 起動: `C:\Users\user\ImperialFlow\venv\Scripts\python.exe scripts\g4_dryrun.py --mt5`（MT5モジュールはIF venvのみ）
   - ★path 名指しが要る場合は Mt5Session/connect に terminal path 引数を足す（FundingPips端末の terminal64.exe を指す）。
