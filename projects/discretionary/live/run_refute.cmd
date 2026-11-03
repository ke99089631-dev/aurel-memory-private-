@echo off
REM AUREL refutation lane - adversarially break the latest promotion candidate with CODE. Read-only. 2026-11-04 Chairman GO.
REM ASCII only. JP rules in AUREL_RESEARCH\CHARTER.md (UTF-8).
setlocal
set "BASE=C:\Users\user\.aurel\memory\projects\discretionary\live\AUREL_RESEARCH"
set "LOCK=%BASE%\.refuting"
set "CLAUDE=C:\Users\user\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"

powershell -NoProfile -Command "if (Test-Path '%LOCK%') { if (((Get-Date) - (Get-Item '%LOCK%').LastWriteTime).TotalMinutes -gt 100) { Remove-Item '%LOCK%' -Force } }"
if exist "%LOCK%" ( echo %date% %time% skip-overlap>>"%BASE%\refute.log" & exit /b 0 )
echo %date% %time% start>"%LOCK%"
echo ========== %date% %time% refute start ==========>>"%BASE%\refute.log"

cd /d "C:\Users\user\.aurel\memory\projects\discretionary\live"
"%CLAUDE%" -p "You are AUREL's REFUTATION lane (adversary). FIRST read AUREL_RESEARCH\CHARTER.md (esp. supplement C) and AUREL_RESEARCH\PROMOTED.md and the most recent AUREL_RESEARCH\findings. Take the newest promotion-candidate or 'weak signal' finding and TRY TO BREAK IT WITH CODE, not prose: re-run on a different in/out split, double the cost, subset by regime, randomize/placebo the signal, apply multiple-testing correction, check look-ahead and survivorship. Append a verdict (survived / broken / inconclusive) with the numbers to AUREL_RESEARCH\findings\<today>.md under a '[REFUTE]' header. If nothing to refute, append '[REFUTE] no candidate'. Read-only and analysis only: no orders, no editing production files, writes ONLY under AUREL_RESEARCH." --allowedTools "Read,Write,Edit,MultiEdit,Bash,Glob,Grep,WebFetch,WebSearch,TodoWrite" --append-system-prompt "You are AUREL refutation lane. Read-only analysis only. No orders / no real or demo trading. Do NOT stop/restart/kill/edit any running executor or live server. Writes ONLY under AUREL_RESEARCH. Production files and prop (g4_/FundingPips) are read-only. Never read or output secrets. Your job is to BREAK findings, not confirm them. When unsure, do nothing." --add-dir "C:\Users\user\.aurel" --add-dir "C:\Users\user\AssetEmpire" >>"%BASE%\refute.log" 2>&1

echo %date% %time% done>>"%BASE%\refute.log"
del "%LOCK%" 2>nul
endlocal
