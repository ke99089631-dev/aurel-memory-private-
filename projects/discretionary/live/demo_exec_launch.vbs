' AUREL AIデモ執行を隠しウィンドウで起動（Bash終了で死なない detached 起動）。
Set s = CreateObject("WScript.Shell")
s.Run "cmd /c ""C:\Users\user\.aurel\memory\projects\discretionary\live\run_demo_exec.cmd""", 0, False
