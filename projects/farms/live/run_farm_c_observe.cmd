@echo off
REM Farm-C (EUR wall-to-wall) EXPLORE observe poll. yfinance EURUSD=X. No MT5, no orders, no money. Gate NOT yet confirmed.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u farm_c_eur_explore.py --live >> farm_c_observe.log 2>&1
