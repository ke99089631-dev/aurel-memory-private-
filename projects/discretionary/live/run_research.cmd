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
"%CLAUDE%" -p "Run one AURELIAN autonomous financial-research cycle. FIRST read AUREL_RESEARCH\CHARTER.md (constitution), AUREL_RESEARCH\DIRECTIVE.md (current directive), and AUREL_RESEARCH\DATA_MAP.md, then follow them strictly. Balance exploration (whole financial market: find where edges can structurally arise, grow DATA_MAP = what is actually testable vs read-only) and deepening (wall-to-wall/reaccel exits/path/regime). Do NOT jump to 'make a winning logic': understand the market first, then testable hypotheses. Pick ONE item from DIRECTIVE/backlog or pose a new AI-native one, pre-register it (sec.5), test in-sample AND out-of-sample using ONLY data we have, record ONE strongest counter-argument (sec.4/supp.C), and append exactly one entry to AUREL_RESEARCH\findings\<today>.md (null is fine and required). You MUST actually RUN the analysis and FILL the numeric results in THIS cycle: a findings entry left with placeholders like '(after run)' / '(実行後に記載)' is a FAILED cycle. CRITICAL EXECUTION MODEL: this cycle is ONE-SHOT and will NOT resume. Run your analysis SYNCHRONOUSLY in the foreground and WAIT for its full output within this same turn; NEVER background it (no run_in_background, no detached launch, no 'I will fill results once it completes' - there is no later). Keep analyses fast (seconds to a few minutes): the live ledgers (setup_ledger.jsonl etc.) ALREADY carry mfe_R/mae_R/hold_bars per trade, so use them for fast path analysis; AVOID heavy multi-year M5 reconstruction unless essential, and if needed subsample hard so it finishes this turn. If too heavy, reduce scope and report a REAL smaller result now, queue the full version in backlog. Every web/literature exploration must END in a data-testable hypothesis or a logged 'needs data X'. Do NOT reinvent entry filters. Read-only and analysis only: no orders, no live/demo trading, do not stop/restart/kill/edit any running executor or live server, writes ONLY under AUREL_RESEARCH, production files and prop(g4_) are read-only, never read or output secrets." --allowedTools "Read,Write,Edit,MultiEdit,Bash,Glob,Grep,WebFetch,WebSearch,TodoWrite" --append-system-prompt "You are AUREL autonomous research lane. Read-only analysis only. No orders / no real or demo trading. Do NOT stop/restart/kill/edit any running executor (demo_exec/fert/farm) or live server (serve_chart). Writes ONLY under the AUREL_RESEARCH folder. Production files (setup_engine*/fert*/*ledger*/chart_live/wallbox) and prop (g4_/FundingPips) are read-only. Never read or output secrets (passwords/API keys/.env values). When unsure, do nothing." --add-dir "C:\Users\user\.aurel" --add-dir "C:\Users\user\AssetEmpire" >>"%BASE%\run.log" 2>&1

echo %date% %time% done>>"%BASE%\run.log"
del "%LOCK%" 2>nul
endlocal
