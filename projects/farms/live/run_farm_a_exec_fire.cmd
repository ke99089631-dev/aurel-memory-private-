@echo off
REM Farm-A demo EXECUTOR ARMED (NAS100.r / MT5Farm 806782). --arm FARM-GO => fires DEMO orders on NAS100.r during NY session.
REM Chairman double-lock GO given 2026-10-22. DEMO only (login 806782). Real 27972608 re-verified-excluded every order.
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\farms\live
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u farm_a_exec.py --live --arm FARM-GO --once >> farm_a_exec_fire.log 2>&1
