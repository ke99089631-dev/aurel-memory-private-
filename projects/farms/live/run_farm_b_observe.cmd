@echo off
REM Farm-B (S&P500 wall-to-wall) forward OBSERVE poll. yfinance ES=F feed. No MT5, no orders, no money.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u farm_b_forward.py --live >> farm_b_observe.log 2>&1
