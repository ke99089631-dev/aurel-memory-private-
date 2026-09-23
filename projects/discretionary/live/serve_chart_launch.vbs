' 壁→壁 ライブチャート配信サーバを「隠しウィンドウ・セッション非依存」で常駐起動する。
' 会長の他の部屋(start_chat_rooms.vbs)と同じ方式＝Claudeセッションが終わっても生き続ける。
Set sh = CreateObject("WScript.Shell")
sh.Run """C:\Users\user\.aurel\memory\projects\discretionary\live\serve_only.bat""", 0, False
