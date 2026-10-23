# setup_engine(信号の親・発注なし) の再起動。2026-10-24 作成。
# 足の切替直後(xx:x0:00〜xx:x0:40)は紙が台帳へ更新を書く時間なので避けて待ち、
# python プロセスだけを止めて VBS ランチャで起こす(LaneWatchdog と同じ起こし方)。
$ErrorActionPreference = 'SilentlyContinue'
$live = 'C:\Users\user\.aurel\memory\projects\discretionary\live'
$vbs  = Join-Path $live 'setup_only_launch.vbs'
$log  = Join-Path $live 'engine_restart.log'
function Stamp { Get-Date -Format 'yyyy-MM-dd HH:mm:ss' }
function Alive { Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'setup_engine\.py' } }

$sec = ((Get-Date).Minute % 5) * 60 + (Get-Date).Second
if ($sec -lt 40) { Start-Sleep -Seconds (40 - $sec) }

$old = Alive
if ($old) { $old | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }; Start-Sleep -Seconds 2 }
Start-Process -FilePath 'cscript.exe' -ArgumentList '//nologo', '//B', $vbs -WindowStyle Hidden
Start-Sleep -Seconds 8
$new = Alive
if ($new) { Add-Content -Path $log -Value "$(Stamp) | 再起動OK pid=$($new.ProcessId -join ',')" -Encoding UTF8; Write-Output "OK pid=$($new.ProcessId -join ',')" }
else      { Add-Content -Path $log -Value "$(Stamp) | 再起動NG(プロセス不在)" -Encoding UTF8; Write-Output "NG" }
