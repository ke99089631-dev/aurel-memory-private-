@echo off
rem Detached runner for backtest_reaccel.py (read-only research; no orders). Launched via backtest_reaccel_launch.vbs.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\user\.aurel\memory\projects\discretionary\live"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" backtest_reaccel.py 2010 2026 --no-verify > backtest_reaccel_run.log 2>&1
echo exit=%ERRORLEVEL% >> backtest_reaccel_run.log
