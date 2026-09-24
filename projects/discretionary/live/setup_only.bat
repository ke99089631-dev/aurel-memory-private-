@echo off
REM 車線3 収束ループ・エンジン（セットアップ記録）常駐起動。2分ごと・発注なし・金ゼロ。
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" setup_engine.py
