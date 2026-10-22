@echo off
REM 肥料reaccel 観測モード(--arm無し=signal記録のみ・発注なし・0円)。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\fertilizer\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u fert_reaccel_exec.py --live --once >> fert_observe.log 2>&1
