' Detached hidden launcher for serve_only.bat (wall-to-wall live chart server, port 8793). Read-only, no orders.
' ASCII only + CRLF on purpose: UTF-8 Japanese comments made VBScript mis-parse and die at "Set sh" (watchdog crash loop 2026-11-14..16).
Set sh = CreateObject("WScript.Shell")
sh.Run """C:\Users\user\.aurel\memory\projects\discretionary\live\serve_only.bat""", 0, False
