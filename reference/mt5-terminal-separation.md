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

## 2026-07-11 追検証で確定した「唯一の壁」＝FundingPipsサーバ接続

### 検証で分かった事実（重要・再発防止）
- **MetaTrader5 Python APIの `initialize()` は「トレードサーバに接続済みの端末」でしか IPC を確立しない。**
  - 証拠: Vantage端末(実弾・接続済み)へ読取アタッチ → `initialize=True, connected=True, account=(27972608, VantageTradingLtd-Live)`。IPCはこのマシンで**動く**。
  - 逆に、コピーした portable 端末(`C:\FundingPips-MT5`)は FundingPips-Trial に接続できず → `initialize` は毎回 **-10005 IPC timeout**。
  - つまり過去の -6/-10005 は全部「サーバ未接続」の症状。**パッケージ版・venv・権限・複数端末は主因ではない**（新venvでも同版5.0.5735で同じ／権限は同一ユーザ非昇格でOK）。
- portable端末は起動・ネット疎通OK(MQL5 Cloud探索まで到達)だが、**journalに Network/authorized 行がゼロ = FundingPips-Trial のサーバ住所を知らず接続を試みてすらいない**。
- 汎用/コピーMT5には FundingPips のサーバ住所(.srv)が入っていない。**FundingPips公式配布のMT5 or ブローカー検索で「FundingPips」登録が必須**。
  - Web調査: MT5ログインで「FundingPips」検索→ `FundingPips Corp` / `FundingPips Corp (2)` の2社。ダッシュボードCredentialsのサーバ名に合う方を選ぶ。
  - ブラウザ版WebTerminal: https://mt5.fundingpips.com/terminal
  - ★注意: .envのサーバ名 `FundingPips-Trial` が実サーバ名と一致するか要確認（SIM系 `FundingPips-SIM1`/`FundingPips2-SIM` 等の可能性。会長ダッシュボードのCredentials欄が正）。

## 2026-07-12 ★解決（接続確立・G4ドライラン起動段まで通過）

### 真因の最終確定（誤診の訂正）
- サーバ名は会長が正しかった＝**`FundingPips-Trial` が実サーバ名**（SIM1/SIM2説はこの口座には的外れ。ブローカーは "FundingPips Corp"）。
- 壁の正体＝**`servers.dat` に FundingPips-Trial のアクセスポイント(サーバIP住所)が未登録**。口座はタイトルに残像表示されるが、ダイヤル先住所が無く「緑にならず・エラーも出ずハング」。
- **決定的な入口の違い**: 「ファイル→取引口座にログイン」ではサーバ住所(.srv)は落ちない。**「ファイル→口座開設(Open an Account)」でブローカー"FundingPips"を検索→選択**すると住所がDLされ servers.dat に入る。**これが全失敗を貫いていた唯一の欠落操作**。
- 会長がこの口座開設ウィザードを実行 → journal に確定行:
  - `'40000162046': authorized on FundingPips-Trial`
  - `terminal synchronized with FundingPips Corp: 52 symbols, trading enabled - hedging mode`

### 接続後にAURELが自動で通したこと（本番配線・検証済）
- `initialize(path=C:\FundingPips-MT5\terminal64.exe, portable=True)` で**接続済み端末へ純アタッチ成功**。
- 口座照合OK: `login=40000162046 server=FundingPips-Trial currency=USD balance=25000 name='Guest U'`。
- **US100実シンボル = `NDX100`**（contract_size=20.0, vol_min=0.01, step=0.01, max=10.0, digits=2, point=0.01）。※日曜クローズ中は bid/ask=0（スペックは取得可）。
- 本番 `g4_dryrun.py --mt5` が IF venv 経由で**接続→誤口座ガード→spec実測→心拍**まで一気通貫（order_send不使用・--dry厳守）。

### コード/設定変更（恒久化・済）
- `execution/mt5_live.py` `Mt5Session.__init__`: **`MT5_PATH`/`MT5_PORTABLE` 対応**追加。端末名指しアタッチ＋接続済みなら creds 無しの純アタッチにフォールバック。→ 実弾Vantage端末と混ざらない。
- `FundingPipsTrial\.env`: `MT5_PATH=C:\FundingPips-MT5\terminal64.exe` / `MT5_PORTABLE=1` を追記。
- `scripts/g4_dryrun.py` `SYMBOL_CANDIDATES` に **`NDX100`** 追加。

### 残（次段）
- NY セッションのリアルタイム評価ループ(copy_rates→FEED→BRAIN→plan→乖離記録)を**この接続の上で回す**＝実際の4週ドライラン本走。市場オープン(月曜NY)以降に稼働。要: 隔離端末を起動状態で維持（会長が緑のまま放置 or 自動起動）。
- NDX100 spec を config sleeve へ確定記入（floorロット換算を実測ベース化）。
- §2-2 通知チャネル(dead-man URL/SMTP/webhook)は未接続のまま。

### 済んだこと（AUREL側・自動）
- `C:\FundingPips-MT5\terminal64.exe` に **portable 分離インスタンス**を作成済（Vantage実弾データに非接触）。初回更新・全再コンパイル(131ファイル)完了・build 5836。
- 隔離venv `C:\Users\user\FundingPipsTrial\venv` に MetaTrader5 導入済（検証用）。
- IPC疎通の健全性を確認済（接続済み端末なら動く）。

### 残り(会長の手＝一度だけGUI/web)
1. FundingPips ダッシュボード → 「Platform/Download MT5」から**公式MT5をDL**、または既存MT5で **File→Login→サーバ欄に「FundingPips」検索→正しいサーバ選択**。
   - Vantage端末と混ぜたくないので、可能なら `C:\FundingPips-MT5` とは別に**公式MT5を別フォルダに新規インストール**が理想。
2. `40000162046` + パスワードでログイン→**右下が緑(接続)**を確認。この瞬間サーバ住所が servers.dat にキャッシュされる。
3. 以降 AUREL は **その接続済み端末へ path 名指しでアタッチ**（`initialize(path=<FundingPips terminal64.exe>, portable=…)`）→ 口座アサート(login==40000162046) → US100 spec実測 → 心拍。Vantage実弾には一切触れない。
   - 起動: `C:\Users\user\ImperialFlow\venv\Scripts\python.exe scripts\g4_dryrun.py --mt5`（要 path 引数追加 / MT5モジュールはIF venv・FundingPips venv どちらでも可）。
   - ★MT5ログの調査時は **Bash/PowerShellツールのサンドボックスを解除**しないと Program Files/AppData\MetaQuotes のファイルが読めない。
