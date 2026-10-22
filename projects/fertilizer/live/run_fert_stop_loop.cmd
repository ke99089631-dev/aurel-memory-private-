@echo off
REM 肥料reaccel 逆指値(pending-stop)執行・武装・常駐ループ(20秒おき)。会長GO 2026-10-23(再構築)。
REM pythonw=コンソール無し=ランチャ終了でも落ちない。出力はログへ。state非依存(MT5実オーダーから再構成)。
set PYTHONUTF8=1
cd /d C:\Users\user\.aurel\memory\projects\fertilizer\live
"C:\Users\user\ImperialFlow\venv\Scripts\pythonw.exe" -u fert_reaccel_stop_exec.py --live --arm FERT-GO --loop 20 >> fert_stop_loop.log 2>&1
