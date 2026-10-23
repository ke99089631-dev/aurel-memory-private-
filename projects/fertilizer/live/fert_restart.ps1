# 肥料reaccel(逆指値) の「穏やかな再起動」。2026-10-24 会長GO(やること3つの③)。
# なぜ: 10-23 10:40 の作り直し再起動が S-0324 の発火窓(10:35-10:40)と重なり、逆指値を置けず取りこぼした。
# どうする:
#   1) 5分足の切替直後(xx:x0:00〜xx:x0:40)は紙が更新を書く時間=発火窓の入口。ここを避けて待つ。
#   2) KILL_FERT を置いて旧プロセスに自分で終わらせる(途中の発注を壊さない)。最大60秒待つ。
#   3) KILL_FERT を消してから新プロセスを起動(残っていると新プロセスも即終了するため)。
#   ※ 置き済みの逆指値はブローカー側に残るので、再起動のすき間(〜20秒)でも約定は失わない。
#   ※ プロセス検索は Name=python* に限定する(初版はこのスクリプト自身のコマンドラインが一致して「生きている」と誤判定した)。
#   ※ 各段階をログに残す(初版は段階ログが出ず、何が起きたか追えなかった)。
$live = 'C:\Users\user\.aurel\memory\projects\fertilizer\live'
$kill = Join-Path $live 'KILL_FERT'
$vbs  = Join-Path $live 'fert_stop_launch.vbs'
$log  = Join-Path $live 'fert_restart.log'
function Stamp { Get-Date -Format 'yyyy-MM-dd HH:mm:ss' }
function L($m) { Add-Content -Path $log -Value "$(Stamp) | $m" -Encoding UTF8; Write-Output $m }
function Alive {
  @(Get-CimInstance Win32_Process | Where-Object { ($_.Name -like 'python*') -and ($_.CommandLine -like '*fert_reaccel_stop_exec*') })
}

# 1) 足の切替直後を避ける(5分周期の 0〜40秒は待つ)
$now = Get-Date
$sec = ($now.Minute % 5) * 60 + $now.Second
if ($sec -lt 40) { L "切替直後のため $((40 - $sec))s 待機"; Start-Sleep -Seconds (40 - $sec) }

# 2) 旧プロセスに穏やかに終わってもらう
$old = Alive
L ("旧プロセス: " + ($(if ($old.Count -gt 0) { ($old | ForEach-Object { $_.ProcessId }) -join ',' } else { 'なし' })))
if ($old.Count -gt 0) {
  Set-Content -Path $kill -Value 'restart' -Encoding ASCII
  L ("KILL_FERT 作成: " + (Test-Path $kill))
  $waited = 0
  while ($waited -lt 60) {
    Start-Sleep -Seconds 2; $waited += 2
    if ((Alive).Count -eq 0) { break }
  }
  $still = Alive
  if ($still.Count -gt 0) {
    L ("60s 自終了せず→強制停止: " + (($still | ForEach-Object { $_.ProcessId }) -join ','))
    foreach ($p in $still) { try { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop } catch { L ("Stop-Process 失敗 pid=$($p.ProcessId): " + $_.Exception.Message) } }
    Start-Sleep -Seconds 2
  } else {
    L "旧プロセス自終了(${waited}s)"
  }
}

# 3) KILL を消してから起動
if (Test-Path $kill) { Remove-Item -Path $kill -Force }
L ("KILL_FERT 残存: " + (Test-Path $kill))
Start-Process -FilePath 'cscript.exe' -ArgumentList '//nologo', '//B', $vbs -WindowStyle Hidden
Start-Sleep -Seconds 8
$new = Alive
if ($new.Count -gt 0) { L ("再起動OK pid=" + (($new | ForEach-Object { $_.ProcessId }) -join ',')) } else { L "再起動NG(プロセス不在)" }
