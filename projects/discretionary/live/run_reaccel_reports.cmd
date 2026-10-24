@echo off
rem AI再加速 地合い別(紙)＋肥料デモ成績(台帳)の日次レポート。2026-10-24 会長GO(次の一手②)。読取のみ・発注なし。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\discretionary\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" reaccel_regime_forward.py >> reaccel_reports.log 2>&1
cd /d C:\Users\user\.aurel\memory\projects\fertilizer\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" fert_reaccel_stats.py >> C:\Users\user\.aurel\memory\projects\discretionary\live\reaccel_reports.log 2>&1
