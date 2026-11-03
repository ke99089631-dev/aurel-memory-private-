@echo off
REM Wall->wall reaccel recipe on 15m bars (2026-11-03 Chairman GO). Read-only, no orders, no touch2sb. Loop 30s.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" setup_engine_15m.py >> setup15m.log 2>&1
