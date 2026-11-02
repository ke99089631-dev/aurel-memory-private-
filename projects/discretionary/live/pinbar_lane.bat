@echo off
REM Pinbar reversal paper lane (2026-11-02 Chairman GO). Read-only, no orders. Loop 30s.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" pinbar_lane.py >> pinbar_lane.log 2>&1
