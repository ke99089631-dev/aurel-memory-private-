@echo off
REM AUREL gold demo executor (MT5Demo 802307 only, never touches real 27972608). Same launcher pattern as setup_only.bat / pinbar_lane.bat (which the watchdog revives OK). ASCII+CRLF only.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u demo_exec.py --live --arm CHAIRMAN-GO >> demo_exec_run.log 2>&1
