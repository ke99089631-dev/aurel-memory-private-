# -*- coding: utf-8 -*-
# G4 DST(夏冬時刻)切替 検証 (Fable5指示⑧-①) — 実弾なし・純粋な時刻計算・凍結コード読取専用
# 目的: 過去/将来のDST切替日を跨いで NY監視窓(09:30 America/New_York錨)が
#       正しく1時間ずれるか。ライブ窓構築コードは凍結と同一の session_open_utc を使う。
import sys, datetime as dt
sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire")
sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire\research")
sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire\strategies")
sys.stdout.reconfigure(encoding="utf-8")
from zoneinfo import ZoneInfo
import session_breakout_trackA as ORB
import trackA_signal as SIG

UTC = ZoneInfo("UTC")
def TS(): return dt.datetime.now(dt.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S%z")

def open_utc_str(tz, hh, mm, d):
    ms = ORB.session_open_utc(tz, hh, mm, d)
    u = dt.datetime.fromtimestamp(ms/1000, UTC)
    loc = u.astimezone(tz)
    return ms, u.strftime("%H:%M UTC"), loc.strftime("%H:%M %Z"), loc.utcoffset()

print(f"[{TS()}] ===== G4 DST切替 検証 開始 (実弾なし/純粋時刻計算) =====")
cfg = SIG.CONFIRMED
tzname = cfg["tz"]; hh, mm = cfg["open_local"]; wlen = cfg["watch_len_h"]
print(f"[{TS()}] ライブ窓CFG(SIG.CONFIRMED): tz={tzname} 開場={hh:02d}:{mm:02d} 監視長={wlen}h")
print(f"[{TS()}] ライブ窓構築 build_ny_session_live() は open_ms=ORB.session_open_utc(ZoneInfo(cfg['tz']),..) を呼ぶ")
print(f"[{TS()}]   → 凍結バックテスターと同一関数=DST処理はzoneinfoで年2回自動\n")

TZ_NY = ZoneInfo("America/New_York")
TZ_LON = ZoneInfo("Europe/London")

def cross(label, tz, hh, mm, before, after, expect_before, expect_after):
    _, ub, lb, ob = open_utc_str(tz, hh, mm, before)
    _, ua, la, oa = open_utc_str(tz, hh, mm, after)
    shift = (ob - oa).total_seconds()  # offset差(秒)。DSTで±3600のはず
    ok = (abs(abs(shift) - 3600) < 1) and (ub == expect_before) and (ua == expect_after)
    print(f"[{TS()}] {label}")
    print(f"[{TS()}]   {before} 開場 {hh:02d}:{mm:02d}{la[-4:] if False else ''} → UTC {ub} (現地{lb}, offset {ob})")
    print(f"[{TS()}]   {after } 開場 {hh:02d}:{mm:02d}          → UTC {ua} (現地{la}, offset {oa})")
    print(f"[{TS()}]   窓のUTC移動 = {abs((ORB.session_open_utc(tz,hh,mm,after)-ORB.session_open_utc(tz,hh,mm,before))/3600000):.2f}h  判定={'○ 1時間ずれOK' if ok else '× 異常'}")
    print()
    return ok

D = dt.date
results = []
print(f"[{TS()}] --- NY監視窓(America/New_York 09:30錨) DST境界 ---")
# 米DST2025: 春3/9(EST->EDT), 秋11/2(EDT->EST)
results.append(cross("① 2025春(3/9 EST→EDT): 冬14:30UTC → 夏13:30UTC",
      TZ_NY, hh, mm, D(2025,3,7), D(2025,3,10), "14:30 UTC", "13:30 UTC"))
results.append(cross("② 2025秋(11/2 EDT→EST): 夏13:30UTC → 冬14:30UTC",
      TZ_NY, hh, mm, D(2025,10,31), D(2025,11,3), "13:30 UTC", "14:30 UTC"))
# 米DST2026: 春3/8, ★秋11/1(=審査期間の切替日)
results.append(cross("③ 2026春(3/8 EST→EDT)",
      TZ_NY, hh, mm, D(2026,3,6), D(2026,3,9), "14:30 UTC", "13:30 UTC"))
results.append(cross("④ ★2026秋(11/1 EDT→EST)=審査中の切替日",
      TZ_NY, hh, mm, D(2026,10,30), D(2026,11,2), "13:30 UTC", "14:30 UTC"))

print(f"[{TS()}] --- 参考: ロンドン窓(Europe/London 08:00錨) 英DST境界 ---")
# 英DST2026: BST開始3/29, 終了10/25。夏07:00UTC / 冬08:00UTC
results.append(cross("⑤ 2026英春(3/29 GMT→BST)",
      TZ_LON, 8, 0, D(2026,3,27), D(2026,3,30), "08:00 UTC", "07:00 UTC"))
results.append(cross("⑥ 2026英秋(10/25 BST→GMT)",
      TZ_LON, 8, 0, D(2026,10,23), D(2026,10,26), "07:00 UTC", "08:00 UTC"))

print(f"[{TS()}] ===== 総合判定 =====")
print(f"[{TS()}]   検証境界 {len(results)}件中 正常 {sum(results)}件 / 異常 {len(results)-sum(results)}件")
print(f"[{TS()}]   → 監視窓は現地09:30(NY)/08:00(London)に錨。DSTでUTC側が年2回自動で1h移動する。")
print(f"[{TS()}] ★審査中の要記録日: 2026-11-01(日) 米EDT→EST。翌営業日11/2(月)から NY窓=14:30 UTC。")
print(f"[{TS()}]   当日=日曜(休場)。実効ずれは 11/2(月)の最初の稼働で確認。カレンダー固定して当日記録する。")
print("DONE" if all(results) else "FAIL")
