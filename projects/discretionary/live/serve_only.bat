@echo off
REM wall-to-wall live chart server only (resident; no chart_gen).
REM ASCII+CRLF on purpose (Task Scheduler/cscript path). stdout/stderr -> serve_chart_run.log (2026-11-16).
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u serve_chart.py >> "%~dp0serve_chart_run.log" 2>&1
