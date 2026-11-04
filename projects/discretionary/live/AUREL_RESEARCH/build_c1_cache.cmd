@echo off
REM One-shot: build cycle1 reaccel path cache (~19min full M5 scan). Run detached via schtask so it survives session teardown.
REM Read-only analysis. Writes only under AUREL_RESEARCH\data. AUREL main builds this offline so the research lane never has to.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\discretionary\live\AUREL_RESEARCH
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u scripts\c1_early_fold.py > data\c1_run.log 2>&1
echo done %date% %time% >> data\c1_run.log
