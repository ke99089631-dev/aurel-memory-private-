@echo off
rem AI再加速 地合い別(紙)＋肥料デモ成績(台帳)の日次レポート。2026-10-24 会長GO(次の一手②)。読取のみ・発注なし。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\discretionary\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" reaccel_regime_forward.py >> reaccel_reports.log 2>&1
cd /d C:\Users\user\.aurel\memory\projects\fertilizer\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" fert_reaccel_stats.py >> C:\Users\user\.aurel\memory\projects\discretionary\live\reaccel_reports.log 2>&1

cd /d C:\Users\user\.aurel\memory\projects\discretionary\live
rem deadrange_label v1 (2026-11-10 chairman GO, observation label only, read-only)
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" deadrange_label.py >> reaccel_reports.log 2>&1
rem R-05 danger gauge (2026-11-17 chairman GO, read-only, paper net R x3)
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" danger_gauge.py >> reaccel_reports.log 2>&1
rem Farm A money-based scoring (2026-11-28 chairman GO, read-only, R is diagnostic only)
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" farm_a_money_report.py >> C:\Users\user\.aurel\memory\projects\discretionary\live\reaccel_reports.log 2>&1
rem Preserve demo SL/TP closes before the 45-day window drops them (2026-11-28, append-only, read-only source)
cd /d C:\Users\user\.aurel\memory\projects\discretionary\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" demo_closes_archive.py >> C:\Users\user\.aurel\memory\projects\discretionary\live\reaccel_reports.log 2>&1
