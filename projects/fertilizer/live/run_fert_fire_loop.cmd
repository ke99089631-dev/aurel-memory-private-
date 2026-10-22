@echo off
REM 肥料reaccel 武装・高速ループ(25秒おき常駐=金デモと同速。鮮度180s内に撃つ)。会長GO 2026-10-22。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\fertilizer\live
"C:\Users\user\ImperialFlow\venv\Scripts\pythonw.exe" -u fert_reaccel_exec.py --live --arm FERT-GO --loop 25 >> fert_fire_loop.log 2>&1
