# 8793(serve_chart)停止で紙レーン盲目 — 2026-11-14 10:03 〜 2026-11-16 12:36

## 影響範囲
| 系 | 影響 | 根拠 |
|---|---|---|
| setup_engine(信号の親)/15m車線/ピンバー車線 | 盲目。復旧後に足2000本から埋め戻し済み(紙は欠けない) | setup15m.log sync err 5,700行・setup_ledger 11-16 12:40更新 |
| demo_exec(金デモ802307) | 盲目期間の発火を受け取れず **撃っていない**。プロセスは生存・建玉0 | demo_exec_ledger 最終11-13 10:35・state毎20秒更新 |
| wall_watcher(LINE) | 同期間 watch error・通知なし | wall_watcher_run.log |
| 畑A(US100 806782)/肥料停止ループ/regime_recorder以外 | 無関係(MT5直結) | farm_a_exec_fire.log 12:27 正常 |

## 盲目期間(紙/デモ突合では除外または注記)
- **2026-11-16(月) 08:00 JST(足の開始) 〜 12:36 JST のみ(約4.5時間)**
- 8793が死んでいた実時間は 11-14(土)10:03〜11-16(月)12:36 だが、11-14は土曜(足は06:55で終了)で市場クローズ後。金曜11-13は無傷(276本・13 setups)。
- この期間の紙の本: 11-16 S-0522〜S-0527(08:15/08:40/10:00/11:10/11:45/12:15、再加速決着4本)。デモ側に対応sidは無い。
- ※初報(12:45)で「11-14(金)10:03〜も盲目」と書いたのは曜日の誤り。13:20訂正。

## 原因
- 11-14(土) 10:03 serve_chart/setup_engine/setup15m 同時死(原因未特定)。
- lane_watchdog の serve_chart 用ランチャ `serve_chart_launch.vbs` が日本語UTF-8コメントで壊れていて `Set sh` が消え即死→3分毎に1,010回「起こした」ログだけ。
- 本番起動(AUREL_ChartServe=bat直)と復旧起動(watchdog=vbs)が別経路で、vbs経路は未検証だった。

## 処置(12:36)
- `serve_chart_launch.vbs` ASCII+CRLF化(旧 .bak_utf8_20261116)
- `serve_only.bat` ASCII+CRLF化・出力を serve_chart_run.log へ(旧 .bak_lf_20261116)
- vbs経路で起動し 8793 LISTENING / tick 生 / 紙再同期 / 監視犬DOWN停止 を確認

## 未着手
- lane_watchdog.ps1: 起こした後の生存確認・連続失敗カウント・LINE通報・別経路フォールバック(schtasks /Run AUREL_ChartServe)
- 11-14 10:03 の同時死の原因
- compare_paper_vs_demo.py に盲目期間の除外印
