@echo off
REM 壁→壁 静的チャート起動（読取のみ・承認1回で完結）。RDP接続時に実行。
REM 1) 最新チャートHTMLを生成 → 2) Tailscale:8793 で配る（携帯で開ける）。
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PY="C:\Users\user\ImperialFlow\venv\Scripts\python.exe"
REM ↑pandas/m5_loader が入った venv。既定の python には pandas が無いので必須。
cd /d "%~dp0"
echo [1/2] chart.html 生成中...
%PY% chart_gen.py
echo [2/2] http://100.73.107.61:8793/ で配信開始（Ctrl+Cで停止）
%PY% serve_chart.py
