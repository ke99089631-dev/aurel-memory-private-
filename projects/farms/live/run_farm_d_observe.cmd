@echo off
REM Farm-D (BTC wall-to-wall) EXPLORE observe poll. yfinance BTC-USD. No MT5, no orders, no money. Gate NOT yet confirmed.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u farm_d_btc_explore.py --live >> farm_d_observe.log 2>&1
