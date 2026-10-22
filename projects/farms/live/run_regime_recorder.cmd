@echo off
REM 相場メーター記録レーン(観測のみ・発注なし・0円)。金とUS100のERを貯める。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u regime_recorder.py >> regime_recorder.log 2>&1
