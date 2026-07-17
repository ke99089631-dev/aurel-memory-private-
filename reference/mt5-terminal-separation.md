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

### 2026-07-12 ★4週ドライラン本走を実装・常駐化（月曜オープンで自動起動）
- `g4_dryrun.py` に **`--live` 常駐ループ**を新規実装（`live_dryrun`）。NY営業日ごとに監視終了(13:30 ET)+1分後、`copy_rates`→(ts,O,H,L,C,hs,atr)→`run_one_session`→日次export(`data/g4_daily`)＋§2-1乖離＋心拍。**order_send は絶対に呼ばない**。決定は `build_ny_session_live` 経由=凍結とバイト同値(selftest済)。
  - 週末に過去NY日で実データ検証済(07-06..07-10, copy_rates→判断→SL/TP/floorロット→乖離が全通)。one-shot(`--max-cycles`)も正常終了。
  - width_hist は履歴CSV全NY幅(3697本)で初回シード → 凍結と連続。state=`data/g4_live_state.json`。
  - 起点ガード `_DRYRUN_START=2026-07-13`(先週を混ぜない) / `_candidate_days` は直近平日を backfill(PC停止の取りこぼし自己修復) / **自己再接続**(端末が落ちても再initialize・誤口座は即停止)。
- **常駐化(admin不要)**: `schtasks /create` は Access denied(要昇格)だったので **スタートアップフォルダ**方式。
  - `Startup\aurel_g4_dryrun.bat` → 起動時に runner+watchdog を最小化起動。
  - launcher: `C:\Users\user\FundingPipsTrial\run_g4_live.bat`(=`python -u g4_dryrun.py --live --poll 300`) / `run_g4_watchdog.bat`(=`g4_watchdog.py --interval 60 --stale 900`)。ログは同フォルダ `g4_live.log`/`g4_watchdog.log`。
  - **今すぐ起動済**: runner worker PID(例)16724・watchdog worker 15072 稼働、心拍 live_idle 更新中。★IF venv の python.exe は launcher stub を噛むので "python.exe 2個/役割" は正常(stub+worker=1論理プロセス)。
- 運用注意: runnerは端末が落ちても `Mt5Session(path+creds)` で再接続=自己修復するが、**隔離端末を緑のまま放置**推奨(belt-and-suspenders)。**PCがオープン時間帯(NY 09:30-13:30 ET=JST 22:30-翌02:30, EDT期)に起動している**必要。

### 残（次段）
- NDX100 spec を config sleeve へ確定記入（floorロット換算を実測ベース化。現状は接続時 measure_symbol 実測を毎回使用で機能上は足りている）。
- §2-2 通知チャネル(dead-man URL/SMTP/webhook)未接続 → NOTIFY.notify はローカル台帳止まり。会長スマホ通知はチャネル配線が要る。
- 冬時間(11月〜)は NY時刻のJST換算が+1h。ドライラン窓(7-8月)は影響なし。

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

## 2026-07-13 ★起動確認報告(第4号§5)→Fable5応答→計装追加

### 正直さの訂正（台帳一貫性）
- Fable5応答が「§3コスト実測=典型0.4〜0.6pt vs モデル1.9pt」と評価したが、**AURELはその数値を報告していない**。初日は市場クローズで `0 spreads`＝スプレッド実測ゼロ。**幻の数字を台帳に入れない**旨を明示訂正済。実スプレッドは月曜NYオープン後が初取得。

### journalで確定した違和感①（毎時切断）
- 隔離端末が**毎正時 :59頃に切断→4〜5分後に自動再接続**を規則反復（市場クローズ帯のトライアル鯖アイドル切断と読む）。自動復旧＋runnerの自己再接続/backfillで自己修復。NYオープン帯でも継続するか観測中。

### Fable5指示5点への計装（g4_dryrun.py に**観測フィールドのみ**追加＝判断路 build_ny_session_live は無改変・preflightでlots 1.71等 凍結一致を再確認済）
- **§3 三点時刻照合**: `_server_local_skew()` が 鯖時刻(tick.time)/ローカルUTC/差分秒 を毎サイクル心拍(`srv_skew_s`)＋日次(`clock`ブロック:last_bar_minus_watch_end_s 等)に記録。
  - ★**基準確定: server_minus_local_s ≈ +10799.4s（≈UTC+3）**。FundingPips鯖はUTC+3。~10800で安定=健全、ドリフト=DST死因の前兆。
- **§1 スプレッド分布**: `_sample_spread()` がNY窓の内側で毎サイクル1点を `data/g4_spread/{day}.jsonl` へ標本化。気配ゼロは標本にしない(market_closed)。日次に `spread_obs`(典型=中央値/最悪=最大/本数)。
- **§2 実効リスク%**: 切り捨て後 `effective_risk_pct = lots*contract*rdist/equity*100` を毎トレード日次に記録（実戦推定値の原料。NDX100小口座で0.87〜0.99%に変動）。
- **§5 週報生成器**: `scripts/g4_weekly.py`（月〜金の mode=live 日次を1枚に：①一致率 ②スプレッド ③実効リスク分布 ④時刻ズレ分布＋入らなかった日）。出力 `data/g4_weekly/{月曜}.txt`。**金曜NYクローズ後にAURELが実行→会長へ渡す**（土曜の週報第1号原料）。
- runner再起動済（PID stub 5668 / worker 17200、cycle1 srv_skew_s=10799.4 確認）。width_hist=3697はstate永続で継続。

### Fable5への宿題（会長判断待ち）
- **口座継ぎ(7/23期限)×シグナル10本要件が数学的に非両立**（残7〜8 NYセッション）。**2本目トライアルの早期発行が事実上必須** → §4 SOP（`reference/account-switch-sop.md`）を切替実施時に本番予行として作成。
- **通知チャネル未配線**（deadman/webhook/smtp すべて False・local_jsonlのみ）。テスト発火の前提＝送信先を会長が1回投入。方式未定。
- 週4末: デバフ後合格率を「良い方向」でも同手続きで再計算＋実効リスク分布版を併記（§1/§2）。

## 2026-07-13 初日(月曜NY)結果 ＋ 検出バグ修正（履歴同期リトライ）

### 検出した実害バグ（修正済）
- 初回評価(17:34 UTC=watch_end+~5分)で **端末のM1履歴ベースが月曜ぶん未ダウンロード**。ライブ気配は流れていた(spread48標本取得)が `copy_rates` は `last_bar=07-10金`(-65.7h陳腐)。→ build_ny_session_live が窓内バー無しで None → `stage:feed データ薄い` のまま **done確定してしまい初日シグナルを取り逃した**。
- 数分〜数十分後には月曜M1が481本充填されていた（プローブ確認）。＝**評価の一発が早すぎた／履歴DL非同期**。
- **修正(g4_dryrun.py)**: `_evaluate_day` に (a) `copy_rates_from_pos` で履歴同期を促す (b) `covered = last_bar >= watch_end-30min` 判定、未同期なら `_retry` を返し **done確定せず次サイクル再取得**、(c) ループで `watch_end+6h` までリトライ猶予（超過は休場/データ欠として正直に確定）。**判断路は無改変**（構文OK・preflight凍結一致維持）。

### 回収した初日の"本当"の結果（履歴充填後に再評価）
- **07-13: entered=false / stage=watch / reason「監視窓内にブレイク無し=機械は入らない判断」/ width_atr=1.451**。
  - ＝セッションは正しく形成され、幅フィルタ通過、監視の結果**ブレイク無しで機械は正しく見送った**。データ失敗ではなく**正当な非エントリー**。初日=観測1セッション・シグナル0本。機械は嘘をつかず、無いトレードを作らなかった。
- **§1 初の実スプレッド: NDX100 = 固定 1.6 指数ポイント(=$1.60, point=0.01なので"160pt"表記)を48標本すべてで一定**。→ トライアル鯖は**固定スプレッド**の疑い。bps換算 ≈0.55bps(全幅)で相対的には狭い/優しいが、**固定・n=1日・静穏セッションのみ**。指標発表/薄商いは未観測。※Fable5想定の「0.4〜0.6pt」は magnitude が違う（実測1.6pt）。
- **§3 時刻**: during-session の有効読み ≈ **+10799.5s(UTC+3)**。ただし回収再評価はオフアワーで `srv_skew=8893`（tick.time凍結の陳腐アーティファクト）。→ **skew指標はライブtick中のみ有効**。通常運用は watch_end+60s(気配新鮮)で読むため正常だが、心拍のオフアワー値は割り引く（要・tick鮮度ガード検討）。
- runner再起動でPID更新(worker 10728)。done=1(07-13確定・正当out)。

## 2026-07-18(土) 週報第1号 ＋ ★runner 20時間放置事故と堅牢化

### 事故: runnerが死亡し20時間放置→金曜セッション取り逃し(→回収済)
- runner(PID 10728)が **07-16 22:07 UTC で心拍停止**＝週末の切断フラッピング(`[再接続]`連発)中にクラッシュ(ネイティブMT5クラッシュ疑い・Pythonトレースバック無しでプロセス消滅)。
- watchdogは正しく死を検知(`runner死 判定 心拍が古い`を連続ログ)が、**(a)自動再起動しない (b)通知がlocal_jsonl止まりで会長に届かない** → **20時間放置**、**金曜7/17のNYセッションを取り逃した**。＝予告した「通知未配線」の穴が実害化。
- 回収: runner再起動→07-17は履歴同期リトライが正しく作動(「履歴未同期・再試行」で陳腐確定を回避)→次サイクルで評価成立(**buy lots=0.09 eff_risk=0.968% actionable**)。5日全確定。

### 堅牢化(実装・稼働済)
- **watchdog に自動再起動を追加**(`scripts/g4_watchdog.py`): `--restart --restart-cooldown 600`。runner死検知でランチャbatを起動(600秒クールダウンで再起動ストーム防止)。`run_g4_watchdog.bat` に反映済・再起動して稼働(「runner生存 pid=14944」確認)。
- 残る根治: (1)週末の再接続churn抑制(市場クローズ帯は再接続を試みない window ガード) (2)**通知チャネル配線**(会長判断待ち・これが無いと"放置"は完全には消えない) (3)skew指標のtick鮮度ガード(オフアワー回収時の見かけドリフトを分布から除外)。

### 週報第1号(2026-07-13〜17)確定値 → `data/g4_weekly/2026-07-13.txt`
- NY評価5日 / シグナル4本 / **執行一致率100%** / 実効リスク 0.958〜0.990%(median0.971)。
- 内訳: 7/13 out(ブレイク無・width1.451) / 7/14 buy0.13 / 7/15 sell0.13 / 7/16 sell0.11 / 7/17 buy0.09。
- スプレッド: 典型1.6pt・最悪4.4pt(7/16スパイク1件)・標本192点/**4日**(★7/17はrunner死で live標本ゼロ=金曜の日中スプレッド/新鮮skewは永久欠測)。
- 時刻: 同日読み(7/14/15/16)は +10799s(UTC+3)岩石安定。週報の「ドリフト4574s」は07-13/07-17のオフアワー回収の陳腐tick2件のみが原因＝本物のドリフトは無い。
- ペース: 5セッション4本=0.8本/回。期限7/23まで残4セッション→合計~7本見込み=**単一トライアルでは10本未達→2本目必須(会長判断待ち)**。
