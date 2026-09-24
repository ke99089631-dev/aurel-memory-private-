' 壁→壁 ライブ一式（チャート配信 8793 ＋ セットアップ記録エンジン）を隠しウィンドウで常駐起動する。
' ログオン時にスタートアップの aurel-chart.cmd から呼ばれる。発注なし・金ゼロ・読取のみ。
Set sh = CreateObject("WScript.Shell")
sh.Run """C:\Users\user\.aurel\memory\projects\discretionary\live\serve_only.bat""", 0, False
sh.Run """C:\Users\user\.aurel\memory\projects\discretionary\live\setup_only.bat""", 0, False
