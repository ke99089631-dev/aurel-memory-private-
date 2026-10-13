@echo off
rem AUREL AIデモ執行 常駐ランチャ（デモ専用・実弾に触れない）。二重ロック解除で起動。
rem pythonw.exe(コンソール無し・GUI扱い)=cmdが待たず即デタッチ=ランチャ終了でも落ちない。出力はログへ。
cd /d "C:\Users\user\.aurel\memory\projects\discretionary\live"
"C:\Users\user\ImperialFlow\venv\Scripts\pythonw.exe" -u demo_exec.py --live --arm CHAIRMAN-GO >> demo_exec_run.log 2>&1
