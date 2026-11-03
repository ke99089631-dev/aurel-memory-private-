@echo off
REM AUREL autonomous research lane - one cycle. Read-only / analysis only / no orders. 2026-11-04 Chairman GO.
REM ASCII only (cmd is cp932). All JP rules live in AUREL_RESEARCH\CHARTER.md (UTF-8, read by claude).
setlocal
set "BASE=C:\Users\user\.aurel\memory\projects\discretionary\live\AUREL_RESEARCH"
set "LOCK=%BASE%\.running"
set "CLAUDE=C:\Users\user\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"

REM Clear stale lock (prev cycle hung > 100 min)
powershell -NoProfile -Command "if (Test-Path '%LOCK%') { if (((Get-Date) - (Get-Item '%LOCK%').LastWriteTime).TotalMinutes -gt 100) { Remove-Item '%LOCK%' -Force } }"
if exist "%LOCK%" ( echo %date% %time% skip-overlap>>"%BASE%\run.log" & exit /b 0 )
echo %date% %time% start>"%LOCK%"
echo ========== %date% %time% cycle start ==========>>"%BASE%\run.log"

cd /d "C:\Users\user\.aurel\memory\projects\discretionary\live"
"%CLAUDE%" -p "Run one AUREL autonomous-research cycle. FIRST read AUREL_RESEARCH\CHARTER.md in full and follow its steps and discipline strictly. Pick one question from AUREL_RESEARCH\backlog.md or pose a new AI-native one, pre-register it, test in-sample AND out-of-sample, and append exactly one entry to AUREL_RESEARCH\findings\<today>.md (null results are fine and required). Do NOT reinvent entry filters. Read-only and analysis only: no orders, no live/demo trading, do not stop/restart/kill/edit any running executor or live server, writes ONLY under AUREL_RESEARCH, production files and prop(g4_) are read-only, never read or output secrets." --allowedTools "Read,Write,Edit,MultiEdit,Bash,Glob,Grep,WebFetch,WebSearch,TodoWrite" --append-system-prompt "You are AUREL autonomous research lane. Read-only analysis only. No orders / no real or demo trading. Do NOT stop/restart/kill/edit any running executor (demo_exec/fert/farm) or live server (serve_chart). Writes ONLY under the AUREL_RESEARCH folder. Production files (setup_engine*/fert*/*ledger*/chart_live/wallbox) and prop (g4_/FundingPips) are read-only. Never read or output secrets (passwords/API keys/.env values). When unsure, do nothing." --add-dir "C:\Users\user\.aurel" --add-dir "C:\Users\user\AssetEmpire" >>"%BASE%\run.log" 2>&1

echo %date% %time% done>>"%BASE%\run.log"
del "%LOCK%" 2>nul
endlocal
