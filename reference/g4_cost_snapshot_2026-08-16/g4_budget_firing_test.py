# -*- coding: utf-8 -*-
# G4 予算門 発火テスト (Fable5指示⑥) — 実弾なし・凍結コード読取専用import・無改変
# 完了定義=「実際に門が閉じるのを見た」。全ログにTS付与。
import sys, os, datetime as dt
sys.path.insert(0, r"C:\Users\user\AssetEmpire\empire")
sys.stdout.reconfigure(encoding="utf-8")
import research.session_breakout_trackA as ORB
from defense.risk_engine import DefenseCommand, RiskConfig, NORMAL, NEW_ENTRY_STOPPED, SIZE_HALVED, KILLED, REJECT, ALLOW

def TS():
    return dt.datetime.now(dt.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S%z")

print(f"[{TS()}] ===== G4 予算門 発火テスト 開始 (実弾なし/order_send呼ばない) =====")
print(f"[{TS()}] 凍結モジュール: research.session_breakout_trackA (import/実行のみ・無改変)")
print(f"[{TS()}] 既定門: DAILY_BUDGET={ORB.DAILY_BUDGET}  WEEKLY_BUDGET={ORB.WEEKLY_BUDGET}\n")

# ─────────────────────────────────────────────
# TEST-A: 日次-2% / 週次-4% 予算門 (凍結ORB.simulate)
# ─────────────────────────────────────────────
CODE = "usatechidxusd"
ORB.SESSION_FILTER = "NY"
fn, ts, O, H, L, C = ORB.load_m1(CODE)
hs, atr = ORB.build_hour_atr(ts, H, L, C)
sessions = ORB.precompute_sessions(CODE, ts, O, H, L, C, hs, atr)
side_bps = ORB.get_cost_model(CODE)[0]
_ny_disp = ORB._cost_side_bps(side_bps, "NY")
print(f"[{TS()}] 実データ: {os.path.basename(fn)}  NYセッション {len(sessions)}本  NY片道コスト={_ny_disp:.4f}bps")
print(f"[{TS()}] --- 門の締め付けスイープ(予算を絞るほど取引が止まる=門が閉じる) ---")

def run(db, wb):
    daily, trades = ORB.simulate(sessions, ts, O, H, L, C, 3, 0.0, "3.0R", 0.010, side_bps, db, wb)
    return daily, trades

sweep = [(1.0,1.0,"門OFF"), (0.02,0.04,"規定 日次-2%/週次-4%"), (0.01,0.02,"半分"), (0.005,0.01,"1/4"), (0.002,0.004,"1/10")]
base_n = None
for db, wb, lab in sweep:
    daily, trades = run(db, wb)
    n = len(trades)
    if base_n is None: base_n = n
    fired_days = [(d.isoformat(), round(net,4)) for (d,net,gr) in daily if net <= -db and db < 1.0]
    print(f"[{TS()}]   予算({db:.3f}/{wb:.3f}) {lab:22s}: 取引数={n:4d}  (門OFF比 {n-base_n:+d})  当日締め発火日数={len(fired_days)}")

# 規定門(0.02/0.04)での発火日・週を明示(タイムスタンプ=NYセッション日)
daily, trades = run(0.02, 0.04)
fired_daily = [(d, net) for (d,net,gr) in daily if net <= -0.02]
import collections
wk = collections.defaultdict(float)
for (d,net,gr) in daily:
    wk[d.isocalendar()[:2]] += net
fired_weekly = [(k, v) for k,v in wk.items() if v <= -0.04]
print(f"\n[{TS()}] === 規定門(日次-2%/週次-4%)での実データ発火 ===")
print(f"[{TS()}]   日次門 発火日数={len(fired_daily)} / 全{len(daily)}取引日")
for d,net in fired_daily[:12]:
    print(f"[{TS()}]     ★日次門CLOSE {d.isoformat()}  当日net={net:+.4f}(≦-0.02で新規停止)")
if len(fired_daily) > 12:
    print(f"[{TS()}]     …他 {len(fired_daily)-12}日")
print(f"[{TS()}]   週次門 発火週数={len(fired_weekly)}")
for k,v in fired_weekly[:8]:
    print(f"[{TS()}]     ★週次門CLOSE {k[0]}-W{k[1]:02d}  週net={v:+.4f}(≦-0.04で週内新規停止)")
if len(fired_weekly) > 8:
    print(f"[{TS()}]     …他 {len(fired_weekly)-8}週")

# ─────────────────────────────────────────────
# TEST-B: 床 -8%/-12%/-15% デッドマン (防衛エンジン)
# ─────────────────────────────────────────────
print(f"\n[{TS()}] ===== TEST-B: 段階デッドマン床(防衛エンジン) =====")
dc = DefenseCommand()   # 既定 -8%/-12%/-15%, executor=安全スタブ(実鍵に触れない)
PEAK = 25000.0
print(f"[{TS()}]   基準ピーク equity=${PEAK:,.0f}  閾値: 新規停止-8% / サイズ半減-12% / KILL-15%")
seq = [
    (PEAK,   "開設直後(ピーク確立)"),
    (24500,  "-2%(平時)"),
    (23500,  "-6%(平時)"),
    (23000,  "-8%(床①: 新規停止のはず)"),
    (22400,  "-10.4%(床①継続)"),
    (22000,  "-12%(床②: サイズ半減のはず)"),
    (21250,  "-15%(床③: KILL=全クローズ+キー失効のはず)"),
]
for eq, note in seq:
    lvl = dc.evaluate_account(eq, mode="paper")
    dd = (PEAK - eq)/PEAK
    print(f"[{TS()}]   equity=${eq:>8,.0f}  DD={dd:6.2%}  → LEVEL={lvl:18s} [{note}]")

# 門が実際に新規を弾くか: pretrade_check(増し玉注文)
print(f"\n[{TS()}]   --- 門が新規注文を弾くか(pretrade_check) ---")
order = {"symbol": "NDX100", "side": "buy", "qty": 0.1, "price": 20000.0}
verdict, why = dc.pretrade_check(order, positions=[], equity=21250, mode="paper")
print(f"[{TS()}]   KILL中の新規buy → 判定={verdict} 理由={why}")
# -8%だけ再現(新しいDCで NEW_ENTRY_STOPPED を作る)
dc2 = DefenseCommand()
dc2.evaluate_account(PEAK); dc2.evaluate_account(23000)  # -8%
v2, w2 = dc2.pretrade_check(order, positions=[], equity=23000, mode="paper")
print(f"[{TS()}]   -8%新規停止中の新規buy → 判定={v2} 理由={w2}")
print(f"[{TS()}]   (参考)平時NORMALの新規buy → ", end="")
dc3 = DefenseCommand(); dc3.evaluate_account(PEAK)
v3, w3 = dc3.pretrade_check(order, positions=[], equity=24500, mode="paper")
print(f"判定={v3} 理由={w3}")

print(f"\n[{TS()}] ===== 発火テスト 完了 =====  (order_send未呼出・実鍵未接触)")
print("DONE")
