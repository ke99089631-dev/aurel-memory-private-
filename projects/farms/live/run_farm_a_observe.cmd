@echo off
REM Farm-A (US100 wall-to-wall) forward OBSERVE poll. yfinance NQ=F feed. No MT5, no orders, no money.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u farm_a_forward.py --live >> farm_a_observe.log 2>&1
