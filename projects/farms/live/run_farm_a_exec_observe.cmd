@echo off
REM Farm-A demo EXECUTOR in OBSERVE mode (NAS100.r / MT5Farm 806782). No --arm => records signals only, NO orders, no money.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u farm_a_exec.py --live --once >> farm_a_exec_observe.log 2>&1
