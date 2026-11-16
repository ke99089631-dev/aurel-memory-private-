' Detached hidden launcher for demo_exec.bat (gold demo executor). Same pattern as setup_only_launch.vbs. ASCII only, CRLF.
' 2026-11-16: old version wrapped run_demo_exec.cmd in cmd /c + pythonw; worked from a shell but never from the watchdog task (729 failed revives 11-11..11-13).
Set sh = CreateObject("WScript.Shell")
sh.Run """C:\Users\user\.aurel\memory\projects\discretionary\live\demo_exec.bat""", 0, False
