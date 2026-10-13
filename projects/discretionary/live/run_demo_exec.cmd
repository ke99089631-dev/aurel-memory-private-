@echo off
rem AUREL AIデモ執行 常駐ランチャ（デモ専用・実弾に触れない）。二重ロック解除で起動。
cd /d "C:\Users\user\.aurel\memory\projects\discretionary\live"
"C:\Users\user\ImperialFlow\venv\Scripts\python.exe" -u demo_exec.py --live --arm CHAIRMAN-GO >> demo_exec_run.log 2>&1
