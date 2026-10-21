@echo off
REM Farm-A' (US100 SL0.50 variant) forward OBSERVE poll. yfinance NQ=F. No MT5, no money.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u farm_a2_sl050_forward.py --live >> farm_a2_observe.log 2>&1
