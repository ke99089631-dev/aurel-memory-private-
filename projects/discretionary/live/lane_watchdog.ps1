# AUREL レーン見張り番 — 常駐型プロセスが落ちていたら起こす(重複は起こさない)。
# 対象=自前schtaskを持たない連続プロセス: setup_engine(信号の親)/demo_exec(金)/serve_chart(チャート/8793)。
# 畑A・肥料は各自のschtaskで自己回復(肥料はロックで二重防止)のためここでは触らない。
# 読取のみで判定し、無い時だけVBSランチャ(pythonw デタッチ)を起動。2026-10-23 作成。
$ErrorActionPreference = 'SilentlyContinue'
$live = 'C:\Users\user\.aurel\memory\projects\discretionary\live'
$lanes = @(
  @{ name = 'setup_engine'; match = 'setup_engine'; vbs = "$live\setup_only_launch.vbs" },
  @{ name = 'gold_demo';    match = 'demo_exec';    vbs = "$live\demo_exec_launch.vbs" },
  @{ name = 'serve_chart';  match = 'serve_chart';  vbs = "$live\serve_chart_launch.vbs" }
)
$logDir = 'C:\Users\user\.aurel\logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$log = "$logDir\lane_watchdog.log"
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe' }
foreach ($l in $lanes) {
  $alive = $procs | Where-Object { $_.CommandLine -match $l.match }
  if (-not $alive) {
    if (Test-Path $l.vbs) {
      Start-Process -FilePath 'cscript.exe' -ArgumentList '//nologo', '//B', $l.vbs -WindowStyle Hidden
      Add-Content -Path $log -Value "$stamp | DOWN->起こした | $($l.name)" -Encoding UTF8
    } else {
      Add-Content -Path $log -Value "$stamp | DOWN かつ ランチャ不在 | $($l.name) ($($l.vbs))" -Encoding UTF8
    }
  }
}
