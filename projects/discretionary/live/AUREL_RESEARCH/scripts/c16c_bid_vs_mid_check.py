# -*- coding: utf-8 -*-
"""
[cycle16 事後フォロー c・方法検証] XAU の npz は Dukascopy **bid** のみ。引け前にスプレッドが広がり（bid が mid より沈む）再開後に
狭まる（bid が戻る）なら、bid 系列だけで「引け前 負・再開後 正」の見かけのリターンが出る。XAU の ask は無いので、bid/ask が揃う
US100（2022-01〜2026-06・data/macro/US100_m5_close.npz=bid・US100_m5_spread.npz=sp_med）で、同じ時刻帯（NY 現地・日次ブレイク
17–18 ET 前後）の bid リターンと mid リターン（mid ≈ bid + sp_med/2）の差を bp で印字し、bid アーティファクトの大きさを見る。
記述のみ・判定なし。
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c16c_bid_vs_mid_check.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle16c] US100 bid vs mid の時刻帯リターン（bid アーティファクトの大きさ） — {time.strftime('%Y-%m-%d %H:%M')}")
zc = np.load(os.path.join(MAC, "US100_m5_close.npz")); tsc = zc["ts"].astype(np.int64); bid = zc["close"].astype(float)
zs = np.load(os.path.join(MAC, "US100_m5_spread.npz")); say(f"- spread npz keys {list(zs.keys())}")
tss = zs["ts"].astype(np.int64); sp = zs["sp_med"].astype(float)
i = np.searchsorted(tsc, tss); ok = (i < len(tsc)) & (tsc[np.clip(i, 0, len(tsc) - 1)] == tss)
tss = tss[ok]; sp = sp[ok]; b = bid[i[ok]]
say(f"- 突合 {ok.sum()} / {len(ok)} M5 行、{pd.to_datetime(tss[0],unit='s')}〜{pd.to_datetime(tss[-1],unit='s')} UTC（⑩）、sp_med 中央値 {np.nanmedian(sp):.2f} pt")
sp = np.where(np.isfinite(sp), sp, np.nanmedian(sp))
mid = b + sp / 2
rb = np.zeros(len(b)); rb[1:] = np.diff(np.log(b)) * 1e4; rm = np.zeros(len(b)); rm[1:] = np.diff(np.log(mid)) * 1e4
t = pd.to_datetime(tss, unit="s", utc=True).tz_convert("America/New_York"); h = t.hour.to_numpy(); wd = t.weekday.to_numpy()
day = t.year.to_numpy() * 10000 + t.month.to_numpy() * 100 + t.day.to_numpy(); keep = wd <= 4
flat = rb == 0
say("- NY 現地 時別 flat 比率（bid）: " + " ".join(f"{hh}:{flat[keep&(h==hh)].mean()*100:.0f}%" for hh in range(24)))
say("- NY 現地 時別 sp_med 中央値 pt: " + " ".join(f"{hh}:{np.median(sp[keep&(h==hh)]):.2f}" for hh in range(24)))
def hour_stats(x):
    df = pd.DataFrame({"d": day[keep], "h": h[keep], "x": x[keep]}); S = df.pivot_table(index="d", columns="h", values="x", aggfunc="sum", fill_value=0.0).reindex(columns=range(24), fill_value=0.0)
    M = S.to_numpy(); m = M.mean(0); se = M.std(0, ddof=1) / math.sqrt(len(M)); return m, m / se, len(M)
mb, tb, n = hour_stats(rb); mm, tm, _ = hour_stats(rm)
say(f"\n## NY 現地 時別 平均リターン bp/時（平日 n{n} 日）: bid vs mid、差 = bid − mid")
say("| h | bid | mid | bid−mid |"); say("|---|---|---|---|")
for hh in range(24):
    say(f"| {hh:02d} | {mb[hh]:+.2f} (t{tb[hh]:+.1f}) | {mm[hh]:+.2f} (t{tm[hh]:+.1f}) | {mb[hh]-mm[hh]:+.2f} |")
# first bar after reopen (18:00 ET) and last 30 min before close (16:30-17:00) — gap bar
mn = t.minute.to_numpy()
for lab, m_ in (("18:00–18:05 再開足", keep & (h == 18) & (mn == 0)), ("18 時 全体", keep & (h == 18)), ("16:30–17:00 引け前", keep & (h == 16) & (mn >= 30)), ("17 時台（ブレイク）", keep & (h == 17))):
    dfb = pd.DataFrame({"d": day[m_], "b": rb[m_], "m": rm[m_]}).groupby("d").sum()
    say(f"- {lab}: bid {dfb['b'].mean():+.2f} bp (t{dfb['b'].mean()/(dfb['b'].std(ddof=1)/math.sqrt(len(dfb))):+.1f}) ／ mid {dfb['m'].mean():+.2f} bp (t{dfb['m'].mean()/(dfb['m'].std(ddof=1)/math.sqrt(len(dfb))):+.1f}) ／ 差 {dfb['b'].mean()-dfb['m'].mean():+.2f} bp（n{len(dfb)}）")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
