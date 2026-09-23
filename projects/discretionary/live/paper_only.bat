@echo off
REM 車線3 AUREL紙トレードエンジン 常駐起動（5分ごと・発注なし・金ゼロ）。
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" paper_engine.py
