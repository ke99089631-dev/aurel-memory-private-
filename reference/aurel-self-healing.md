# AUREL 自己治癒（OS-8）と蘇生アラート

母デーモン(`~/aurel/aurel.mjs`, port 7878)が落ちても自動復旧し、その事実を会長へ surface する仕組み。

## 経路
1. **HealthMonitor**（`~/.aurel/daemon/health-monitor.ps1`, スケジュールタスク `AUREL_HealthMonitor`, 5分毎）
   - `GET http://127.0.0.1:7878/api/health` を叩く。生存=無言。
   - DOWN → `~/.aurel/boot/mother-autostart.ps1` で `aurel.mjs` を再起動。
   - 蘇生**成功後**に `~/.aurel/state/last-death.json`（`{revivedAt,cause,revivalNum,reported:false}`）を書く。
   - 3連続失敗で30分クールダウン。
2. **surface（会長への通知）**
   - `postToMother`（aurel.mjs 内）＝母チャットへメッセージ注入。
   - proactive エンジン（`~/.aurel/daemon/proactive.mjs`, 60秒ティック）が会長へ届ける経路。

## 2026-08-07 に発見・修正した2つのバグ（会長GO「無言問題を閉じる」）
自己治癒（再起動）は機能していたが、**「死んで直した」事実が会長に一度も届いていなかった**。原因は2つ:
1. **boot-race**: 既存 consumer は aurel.mjs の**起動時1回**しか last-death.json を読まない。だが HealthMonitor は蘇生【後】に書く → 読み終えた後に書かれ、構造的に取りこぼす。
2. **BOM**: last-death.json は PowerShell `Set-Content -Encoding utf8` で**BOM付き**。`JSON.parse` が BOM で落ちる（既存 boot consumer も同じ）。

### 修正（proactive.mjs へ追加のみ・既存無改変）
- 新ルール `daemon_revival_alert`（`action: revival_alert`, interval 5分, **既定 ON**＝安全用途）。
- 新アクション `revival_alert`: last-death.json を**常時ポーリング**（BOM剥がし付き）→ `reported:false` なら `postToMother`→`reported:true/reportedBy/reportedAt` で冪等化。hook無なら reported を立てず次回再試行。
- 常時ティックゆえ boot-race を構造的に解消。BOM は `charCodeAt(0)===0xFEFF` で除去。
- 検証: mock hook で triggerNow → 実イベント surface・reported:true・2回目は無投稿を確認（実stateは reported:false に温存）。

### 未対応（任意・別GO）
- aurel.mjs の boot consumer(行~1411) の `JSON.parse(raw)` も BOM で落ちるが、proactive ポーラが同ケースを完全にカバーするため母デーモン core は無改変のまま放置。belt&suspenders で直すなら1行。
- health-monitor.ps1 が BOM無しで書くよう `Out-File -Encoding utf8NoBOM`（PS7）or `[IO.File]::WriteAllText` に変えるのも根治策。

### 有効化条件
- 稼働中デーモンは**古い proactive.mjs をメモリキャッシュ**しているため、新コード＋孤児イベント(6/25 revival #2)は**デーモン再起動後に初めて surface**する。次の自然な再起動/蘇生で有効化。手動なら mother-autostart.ps1。
