# -*- coding: utf-8 -*-
"""
[cycle16 事後フォロー・記述のみ] c16 の 24 時プロファイルで事前固定セルに無かった **London 23 時（日次メンテ明けの最初の 1 時間）**
が 在 +3.11 bp (t14.3)・外 +3.28 (t6.9)・近年 +4.64 (t4.7) と全窓で立った。判定は変えない（事後）。ここでは
 (1) London 時別の flat 比率（メンテ時間帯の所在）、(2) 23 時の最初の 5 分足（再開ギャップ）と残り 55 分の分解、
 (3) 年別の 23 時 平均・正の日比率・中央値（尻尾依存か）、(4) AM フィックス 10 時の 2010-14 vs 2015-20（2015-03 の LBMA 電子化）、
 (5) spread_log（実口座 tick・42 日・読取のみ）で再開直後 10 分のスプレッド、を印字する。入力は既存キャッシュのみ。
"""
import os, time, json, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c16b_reopen_gap_followup.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle16b] 再開ギャップ（London 23 時）の記述フォロー — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c16b_reopen_gap_followup.py)")
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); r_bp = r * 1e4
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_lon = t_utc.tz_convert("Europe/London")
wd = t_lon.weekday.to_numpy(); hour = t_lon.hour.to_numpy(); minute = t_lon.minute.to_numpy(); year = t_utc.year.to_numpy()
hour_utc = t_utc.hour.to_numpy()
day_lon = (t_lon.year.to_numpy() * 10000 + t_lon.month.to_numpy() * 100 + t_lon.day.to_numpy())
keep = wd <= 4; flat = r == 0

say("\n## (1) London 時別 flat 比率（平日）・UTC 時別も")
say("- London: " + " ".join(f"{h}:{flat[keep&(hour==h)].mean()*100:.0f}%" for h in range(24)))
say("- UTC   : " + " ".join(f"{h}:{flat[keep&(hour_utc==h)].mean()*100:.0f}%" for h in range(24)))
# 夏/冬で UTC 上のメンテ時間がずれるか
summ = t_lon.map(lambda x: x.dst().total_seconds() > 0).to_numpy() if False else (t_lon.hour.to_numpy() != t_utc.hour.to_numpy())
say("- UTC flat 比率（夏時間 London=UTC+1）: " + " ".join(f"{h}:{flat[keep&summ&(hour_utc==h)].mean()*100:.0f}%" for h in range(20, 24)) +
    " ／ 冬時間: " + " ".join(f"{h}:{flat[keep&~summ&(hour_utc==h)].mean()*100:.0f}%" for h in range(20, 24)))

def dstat(mask_bar, label):
    df = pd.DataFrame({"d": day_lon[mask_bar], "r": r_bp[mask_bar]}); s = df.groupby("d")["r"].sum()
    yrs = pd.Series(year[mask_bar]).groupby(day_lon[mask_bar]).first().reindex(s.index)
    return s, yrs
W = {"在2010-20": (2010, 2020), "外2021-26H1": (2021, 2026), "近年2024-26H1": (2024, 2026)}
def rep(s, yrs, name):
    row = []
    for wn, (a, b) in W.items():
        x = s[(yrs >= a) & (yrs <= b)]; n = len(x); m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
        row.append(f"{wn} {m:+.2f} bp (t{m/se:+.1f}, n{n}, 中央値 {x.median():+.2f}, 正 {(x>0).mean()*100:.0f}%, sd {x.std(ddof=1):.1f})")
    say(f"- {name}: " + " ｜ ".join(row))

say("\n## (2) London 23 時の分解: 最初の 5 分足（再開ギャップ）vs 残り 55 分、および 22 時・21 時")
h23 = keep & (hour == 23)
rep(*dstat(h23 & (minute == 0), "23:00 足"), "23:00–23:05（再開ギャップ足）")
rep(*dstat(h23 & (minute > 0), "23:05-"), "23:05–24:00（残り 55 分）")
rep(*dstat(h23, "23h"), "23 時 全体")
rep(*dstat(keep & (hour == 22), "22h"), "22 時 全体（メンテ帯）")
rep(*dstat(keep & (hour == 21), "21h"), "21 時 全体（NY 引け前）")
rep(*dstat(keep & (hour == 21) & (minute >= 30), "21h30"), "21:30–22:00（引け直前 30 分）")

say("\n## (3) 年別: 23 時 全体の平均 bp・t・正の日比率（尻尾依存か）、参考 無条件 日次ドリフト bp/日")
s23, y23 = dstat(h23, "23h"); sall, yall = dstat(keep, "all")
for yv in range(2010, 2027):
    x = s23[y23 == yv]; xa = sall[yall == yv]
    if len(x) < 20: continue
    se = x.std(ddof=1) / math.sqrt(len(x))
    say(f"- {yv}: 23 時 {x.mean():+.2f} bp (t{x.mean()/se:+.1f}, n{len(x)}, 正 {(x>0).mean()*100:.0f}%, 中央値 {x.median():+.2f}) ／ 無条件 日次 {xa.mean():+.2f} bp/日 → 23 時の占有 {x.mean()/xa.mean()*100 if abs(xa.mean())>0.3 else float('nan'):+.0f}%")
# ウィンザー化（±3 sd）で平均が残るか
for wn, (a, b) in W.items():
    x = s23[(y23 >= a) & (y23 <= b)]; sd = x.std(ddof=1); xw = x.clip(-3 * sd, 3 * sd)
    say(f"- {wn} 23 時 ±3sd ウィンザー化: {xw.mean():+.2f} bp (t{xw.mean()/(xw.std(ddof=1)/math.sqrt(len(xw))):+.1f}) vs 生 {x.mean():+.2f}")

say("\n## (4) AM フィックス（London 10 時）と PM 14 時: 2010-14 vs 2015-20 vs 2021-26（2015-03-20 に LBMA 金価格が電子オークション化）")
for hh in (10, 14):
    s, y = dstat(keep & (hour == hh), f"{hh}h")
    for a, b in ((2010, 2014), (2015, 2020), (2021, 2026)):
        x = s[(y >= a) & (y <= b)]; se = x.std(ddof=1) / math.sqrt(len(x))
        say(f"- {hh} 時 {a}-{b}: {x.mean():+.2f} bp (t{x.mean()/se:+.1f}, n{len(x)})")

say("\n## (5) spread_log（実口座 tick・読取のみ）: 再開直後 10 分 vs 開場中の中央値")
try:
    rows = []
    with open(os.path.join(LIVE, "spread_log.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line); rows.append((o["ts"], o["spread_pt"]))
            except Exception: pass
    S = pd.DataFrame(rows, columns=["ts", "sp"]); tl = pd.to_datetime(S["ts"], unit="s", utc=True).dt.tz_convert("Europe/London")
    S["h"] = tl.dt.hour.to_numpy(); S["m"] = tl.dt.minute.to_numpy(); S["wd"] = tl.dt.weekday.to_numpy()
    S = S[S["wd"] <= 4]
    say(f"- 行 {len(S)}（平日）、期間 {tl.min()}〜{tl.max()} London")
    for lab, m in (("22 時台（メンテ）", S["h"] == 22), ("23:00–23:10", (S["h"] == 23) & (S["m"] < 10)), ("23:10–24:00", (S["h"] == 23) & (S["m"] >= 10)),
                   ("21:50–22:00", (S["h"] == 21) & (S["m"] >= 50)), ("開場中 08–20 時", (S["h"] >= 8) & (S["h"] < 20))):
        x = S.loc[m, "sp"]
        if len(x): say(f"- {lab}: n{len(x)} 中央値 {x.median():.2f} USD・p90 {x.quantile(0.9):.2f}・max {x.max():.2f}・>0.20 比率 {(x>0.20).mean()*100:.0f}%")
except Exception as e:
    say(f"- spread_log 読取失敗: {e}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
