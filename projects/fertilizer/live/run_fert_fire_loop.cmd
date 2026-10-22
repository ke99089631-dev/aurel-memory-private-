@echo off
REM 肥料reaccel 武装・高速ループ(10秒おき常駐・重複許可無制限・鮮度180s)。会長GO 2026-10-22 A+B。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\fertilizer\live
"C:\Users\user\ImperialFlow\venv\Scripts\pythonw.exe" -u fert_reaccel_exec.py --live --arm FERT-GO --loop 10 >> fert_fire_loop.log 2>&1
