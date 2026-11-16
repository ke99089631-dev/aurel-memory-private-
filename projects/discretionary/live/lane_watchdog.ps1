# AUREL lane watchdog (ASCII only + CRLF; a UTF-8/Japanese .ps1 without BOM garbled the log and masked failures).
# Runs every 3 min via schtask AUREL_LaneWatchdog. Read-only checks; when a lane is down (or hung) it launches the VBS launcher,
# then WAITS and VERIFIES the process actually came up. "launched" is never logged as success by itself
# (2026-11-16: 729 "woke it" lines for gold_demo and 1,010 for serve_chart while both stayed dead).
# Lanes with a heartbeat file: if the process exists but the heartbeat is older than hb_sec, it is treated as HUNG -> killed -> relaunched.
# Farm A and fertilizer have their own schtasks (lock-guarded) and are NOT touched here.
$ErrorActionPreference = 'SilentlyContinue'
$live = 'C:\Users\user\.aurel\memory\projects\discretionary\live'
$lanes = @(
  @{ name = 'setup_engine'; match = 'setup_engine\.py';     vbs = "$live\setup_only_launch.vbs";   hb = '';                          hb_sec = 0 },
  @{ name = 'gold_demo';    match = 'demo_exec\.py';        vbs = "$live\demo_exec_launch.vbs";    hb = "$live\demo_exec_state.json"; hb_sec = 240 },
  @{ name = 'serve_chart';  match = 'serve_chart\.py';      vbs = "$live\serve_chart_launch.vbs";  hb = '';                          hb_sec = 0 },
  @{ name = 'pinbar_lane';  match = 'pinbar_lane\.py';      vbs = "$live\pinbar_lane_launch.vbs";  hb = "$live\pinbar_state.json";    hb_sec = 240 },
  @{ name = 'setup15m';     match = 'setup_engine_15m\.py'; vbs = "$live\setup15m_launch.vbs";     hb = '';                          hb_sec = 0 },
  @{ name = 'wall_watcher'; match = 'wall_watcher\.py';     vbs = 'C:\Users\user\.aurel\notify\wall_watcher_launch.vbs'; hb = ''; hb_sec = 0 }
)
$logDir = 'C:\Users\user\.aurel\logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$log = "$logDir\lane_watchdog.log"

function Stamp { return (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') }
function Procs {
  return Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe' }
}
function Alive($match) {
  return @(Procs | Where-Object { $_.CommandLine -match $match })
}

foreach ($l in $lanes) {
  $alive = Alive $l.match
  $reason = ''
  if ($alive.Count -eq 0) {
    $reason = 'DOWN'
  } elseif ($l.hb -ne '' -and (Test-Path $l.hb)) {
    $age = [int]((Get-Date) - (Get-Item $l.hb).LastWriteTime).TotalSeconds
    if ($age -gt $l.hb_sec) {
      $reason = "HUNG heartbeat_age=${age}s"
      foreach ($p in $alive) { Stop-Process -Id $p.ProcessId -Force }
      Start-Sleep -Seconds 3
    }
  }
  if ($reason -eq '') { continue }
  if (-not (Test-Path $l.vbs)) {
    Add-Content -Path $log -Value "$(Stamp) | $reason | launcher missing | $($l.name) ($($l.vbs))" -Encoding UTF8
    continue
  }
  Start-Process -FilePath 'cscript.exe' -ArgumentList '//nologo', '//B', $l.vbs -WindowStyle Hidden
  Start-Sleep -Seconds 20
  $after = Alive $l.match
  if ($after.Count -gt 0) {
    Add-Content -Path $log -Value "$(Stamp) | $reason -> launched -> UP ok pid=$(($after | ForEach-Object { $_.ProcessId }) -join ',') | $($l.name)" -Encoding UTF8
  } else {
    Add-Content -Path $log -Value "$(Stamp) | $reason -> launched -> REVIVE FAILED (no process after 20s) | $($l.name) | $($l.vbs)" -Encoding UTF8
  }
}
