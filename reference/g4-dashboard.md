---
tags: [reference, monitoring, g4, operational]
type: reference
updated: 2026-07-25
---

# G4 トライアル・ドライラン監視ダッシュボード

> 発端: 2026-07-20〜24 の「静かに死んで5日欠測」。誰も見ていなければ気づけない。
> → 一目で生死が分かる1枚を常設。会長が毎朝チラ見するだけで欠測を即察知できる。

## アーキテクチャ（彼の仕様: データ源は共通JSON・2026-07-25拡張）
```
g4_dashboard.py → data/g4_state.json（唯一の真実・共通データ源）
    ├─ ビューA: data/g4_dashboard.html（運用監視・自動更新）  ←実装済
    └─ ビューB: data/g4_public.png（公開用・載せないもの厳守） ←後続
```
- 共通JSONキー: generated_at/ny_date/heartbeat/connection/expiry/calendar/live_tally/tasks/decisions
- **優先3項目（事故を捕まえる最小構成・実装済）**: ①心拍経過の色分け(hero) ②稼働カレンダー14日 ③口座期限カウントダウン
- ③の期限は `data/g4_trial_meta.json`（trial_no/expiry_date/status/note）。**2本目発行後、会長情報で更新**。現状=1本目失効表示。
- カレンダー判定: stage=='pending_sync'→欠測(赤✕) / entered→観測ENTRY(緑●) / watch等→見送り(緑■) / 平日ファイル無し→欠測(赤) / 土日→休場(灰·) / 当日→青□。検証: 07-20〜23が✕赤4連＝5日欠測が一目・稼働率60%・欠測4日。
- ビューB「載せないもの」: ログインID/PW・サーバ名/ブローカー・.envパス・残高絶対額・EP/SL/TP価格・lot数・pid/host/パス・未確定判断。載せてよい=生死/稼働率%/カレンダー色/シグナル本数。

## 設計の肝（事故の教訓の反映）
- **本体(runner)とは別プロセス**が心拍ファイルの"鮮度"を再計算してHTMLを吐く。
  runnerが死ぬと心拍tsが止まり、経過時間が伸びて画面が**自動で赤くなる＝叫ぶ**。
  runner同梱だと死んだ瞬間に画面も凍り"静かに死ぬ"再発になるので、必ず独立させた。
- 読取専用・お金は動かさない・ネットも触らない・秘密は出さない。

## 構成ファイル
| 役割 | パス |
|------|------|
| 生成スクリプト | `C:\Users\user\AssetEmpire\empire\scripts\g4_dashboard.py` |
| 起動bat | `C:\Users\user\FundingPipsTrial\run_g4_dashboard.bat` |
| 出力HTML | `C:\Users\user\AssetEmpire\empire\data\g4_dashboard.html`（30秒自動リフレッシュ） |
| ログ | `C:\Users\user\FundingPipsTrial\g4_dashboard.log` |
| ログオン自動オープン | `...\Startup\g4_dashboard_open.bat`（25秒待って既定ブラウザで開く） |
| 共通データ源 | `data/g4_state.json`（ビューA/B共通の唯一の真実） |
| ビューB公開PNG | `data/g4_public.png`（生成=`scripts/g4_public.py`・毎分ビューA生成に同梱） |
| 期限メタ | `data/g4_trial_meta.json`（trial_no/expiry_date/status/note・2本目発行後に会長情報で更新） |

## ビューB公開PNG（実装済 2026-07-26）
- 依存: **Pillow**（ImperialFlow venvに導入済）＋Windows同梱JPフォント(YuGothB/meiryo)。
- `g4_dashboard.py` main() が `from g4_public import generate_png` を try/except で呼ぶ＝**PNG失敗はビューAを壊さない**。
- 描画するのは4つだけ: **生死状態（稼働中/注意/停止）・稼働率%・カレンダー色・シグナル本数(X/10)**。
- 「載せないもの」を state から一切参照しない構造: login/PW/サーバ/ブローカー/残高絶対額/EP/SL/TP/lot/pid/host/パス/skew生値/未確定判断。
- フッタに免責「※ドライラン(記録のみ)。売買実績・損益ではありません」（景表法/金商法配慮）。
- 検証: 1200x630 PNG。稼働中(緑)・60%・5/10・欠測4連が赤で表示、秘密の漏れなしを目視確認。

## 常駐タスク
- **`AUREL_G4_Dashboard`**: schtasks `/sc MINUTE /mo 1`（1分毎・無期限）。State=Ready。
  非管理者で作成成功（`schtasks.exe`方式。Register-ScheduledTask(CIM)は0x80070005で拒否された）。
- 既存3タスク（Runner=Running / Watchdog=Running / Keepalive=Ready）と並び、ダッシュボード自身にも4タスクの生死が出る。

## 可視ウィンドウ抑止（2026-07-28 修正・恒久）
> 症状: 会長PCに cmd 窓が**定期的に開く**＋「AUREL/Attaches/order_send は認識されていません」エラー窓。かなり迷惑との指摘。
- **原因①** 反復タスク（Dashboard=毎分 / Keepalive=5分毎）が Interactive で `cmd/bat` を直接起動＝毎回**可視窓**が点滅。
- **原因②** batのREMコメントが日本語(UTF-8)。cmd(cp932)が化けてREM解析が壊れ、英単語をコマンド扱い→「〜は認識されていません」。会長が撮った窓の正体は `run_g4_live.bat` の「会長」バイト。
- **対策A（隠し起動）** `C:\Users\user\FundingPipsTrial\hidden_run.vbs` を新設。`WScript.Shell.Run "<bat>", 0, True`（0=非表示／**True=完了待ち**）。Dashboard/Keepalive の action を `wscript.exe //B "hidden_run.vbs" "<bat>"` に付け替え（`Set-ScheduledTask`・非管理者で成功）。
  - **落とし穴**: 最初 `,0,False`（非同期）にしたら wscript が即終了→Task Schedulerが完了扱い→pythonが走らずHTML凍結（LastResult=0なのに未更新）。**必ず True（同期待ち）**にする。短命タスク限定。Runner等の常駐は wrap しない（Trueだと永久ブロック）。
- **対策B（ASCII化）** 全 `run_g4_*.bat` の日本語コメントをASCIIに。検証: `nonASCII_bytes=0` 全bat。
- **検証(2026-07-28)**: 自然発火(毎分)で HTML/state 更新=True・LastResult=0・**可視窓 NONE**。Runner心拍 pid=12168（C-002同一pid＝不変）新鮮。Runner/Watchdog=Running 継続。
- Startup の `g4_dashboard_open.bat` は `timeout /t 25` の窓がログオン時に**1回だけ**出る（定期ではない）。気になれば同VBSで隠せるが今回は据置。

## 読むデータ
- `data/g4_heartbeat.json` … 生死（ts鮮度）・phase・cycle・srv_skew_s
- `data/g4_daily/*.json` … 日別判断（entered/side/lots/eff_risk）
- タスク状態 … PowerShell `Get-ScheduledTask`（ロケール非依存。schtasksは日本語WinでShift-JIS化けするため不使用）

## 生死しきい値（心拍経過）
- ≤5分=緑ALIVE / ≤20分=黄WARN / >20分=赤DEAD（`GREEN_S=300 / YELLOW_S=1200`、調整可）

## パネル
1. 生死（最大・最上段）＝心拍経過
2. MT5接続（srv_skew_s＝週末クローズ/1本目失効のstale窓を平易表示）
3. LIVEシグナル累計（7/14以降）X/10本
4. 常駐タスク4種の状態
5. 直近12日の判断テーブル

## 検証（2026-07-25）
- 手動生成・タスク経由生成いずれもHTML更新を確認（LastResult=0）。
- タスク表: Runner=Running / Watchdog=Running / Keepalive=Ready / Dashboard=Ready を正しく表示。
- 現状表示: ALIVE・LIVE 5/10・判断15行。srv_skew≈-52913s＝週末stale窓（想定内）。
