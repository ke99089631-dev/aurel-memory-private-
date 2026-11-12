# demo_exec 不点火の復旧手順（2026-11-13 会長報告で発覚）

## 症状
touch2sb の LINE 通知（🔵AI発注サイン「デモが今撃った」）は来るのに、デモ口座に建玉が入らない。

## 原因の構造（重要）
- 通知は `notify/wall_watcher.py`（常駐）が **自前で同じ発火を再計算**して送っている。
  実際にデモ発注したかは確認していない＝「デモが今撃った」は執行の証明ではない。
- 実発注は `live/demo_exec.py`（別プロセス・MT5デモ802307へ order_send）。
- 2026-11-11 18:50 に demo_exec が死亡（最後の state 書込）。以降 2日間プロセス不在。
- 監視 `lane_watchdog.ps1`（AUREL_LaneWatchdog）は3分毎に「DOWN->起こした gold_demo」を
  出し続けたが復活せず＝**ロックとwatchdogのデッドロック**。
  `demo_exec.lock` は生PIDだけを持ち、`acquire_lock()` の tasklist 判定はPID再利用で誤判定しうる。
  lock の mtime が何日も更新されない＝acquire_lock が成功していない印。

## 復旧（今回やったこと・再現手順）
1. 死プロセス確認: `Get-CimInstance Win32_Process` に `demo_exec` が無い。
2. 停滞の証拠: `demo_exec.lock` の中身(死PID)と mtime が古い／`demo_exec_run.log` が伸びていない。
3. 古い lock を削除: `rm live/demo_exec.lock`（KILLファイルが無いことも確認）。
4. 動作確認（デモ・副作用なし）:
   `ImperialFlow\venv\Scripts\python.exe -u demo_exec.py --live --arm CHAIRMAN-GO --once`
   → 「[接続] デモ802307 検証OK」＋古い発火は age>180s で skip が出れば健全。
5. 常駐起動（デタッチ）: Git Bash で `MSYS_NO_PATHCONV=1 cscript //nologo //B demo_exec_launch.vbs`
6. 確認: pythonw が demo_exec で2つ（venvランチャ+Python312子＝重複でない）／lock が新PID+新mtime／
   run.log に「[起動] デモ執行 20秒おき」。

## 注意
- 新しい発火は「発火から180秒以内」のみ撃つ（バックフィル防止）。古い通知分は撃ち直さない＝正常。
- これはデモ(802307)のみ。実弾27972608には触れない。
