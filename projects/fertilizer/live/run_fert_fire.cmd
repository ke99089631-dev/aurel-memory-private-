@echo off
REM 肥料reaccel 武装(--arm FERT-GO=金reaccelをデモ806809に実射)。会長GO後にタスクを切替。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\fertilizer\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u fert_reaccel_exec.py --live --arm FERT-GO --once >> fert_fire.log 2>&1
