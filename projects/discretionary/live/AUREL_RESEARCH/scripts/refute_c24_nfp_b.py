# -*- coding: utf-8 -*-
"""
[REFUTE c24 補足 b・事後・記述] W2 の P4 で 外/近年 の PRE 負が 08:00→08:30 ET に局在（t−3.0／−2.4）＝発表直前の bid 沈み（spread 拡大の bid 側）の疑い。
 (1) NFP 日（v3）vs 他金曜の 5 分足平均リターン profile 08:00〜08:55 ET（在/外）。
 (2) NFP 日で JUMP（08:30 足）を 08:25 足リターンに回帰（HC1）: 機械的な bid 戻りなら β≈−1 側・他金曜のプラセボと比較。
 (3) 実口座 spread_log.jsonl（読取のみ・2026-09-25〜）で NFP 時刻（08:15〜08:45 ET）の spread_pt を印字（口座側に拡大があるか）。
 判定には使わない（記述）。入力 XAU npz・spread_log.jsonl（読取のみ）。外部通信なし。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
LIVE = os.path.dirname(ROOT)  # discretionary/live
OUT = os.path.join(DATA, "refute_c24_nfp_b.md"); L = []; NY = "America/New_York"
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c24 補足 b] 発表直前 bid 沈みの検査（記述） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c24_nfp_b.py)")

def nfp_dates_v3(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day <= 3: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            if rel.month == 7 and rel.day == 3 and rel.weekday() == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    s = set(out)
    for d in ["2013-10-04", "2013-11-01", "2025-10-03", "2025-11-07", "2025-12-05"]: s.discard(pd.Timestamp(d))
    s.add(pd.Timestamp("2013-10-22")); s.add(pd.Timestamp("2013-11-08")); return pd.DatetimeIndex(sorted(s))
def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute); loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def idx_of_bar(ts, T):
    out = np.full(len(T), -1); ok = np.isfinite(T); key = T[ok].astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1); out[ok] = np.where(ts[pos] == key, pos, -1); return out
def hc1_reg(y, x):
    m = np.isfinite(y) & np.isfinite(x); y = y[m]; x = x[m]; n = len(y)
    if n < 20: return dict(b=np.nan, se=np.nan, t=np.nan, n=n)
    X = np.column_stack([np.ones(n), x]); XtXi = np.linalg.inv(X.T @ X); beta = XtXi @ X.T @ y; e = y - X @ beta
    meat = (X * e[:, None]).T @ (X * e[:, None]); V = XtXi @ meat @ XtXi * n / (n - 2); se = math.sqrt(V[1, 1]); return dict(b=beta[1], se=se, t=beta[1] / se, n=n)
def ms(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 5: return np.nan, np.nan, n
    return x.mean(), x.mean() / (x.std(ddof=1) / math.sqrt(n)), n

zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)) * 1e4
days = pd.date_range("2010-01-01", "2026-06-30", freq="D"); days = days[days.weekday == 4]; YR = days.year.to_numpy()
V3 = nfp_dates_v3(); nfp = days.isin(V3)
# (1) bar profile
say("\n## (1) 5 分足平均リターン profile（bp・足の開始 ET・NFP 日 v3 vs 他金曜）")
say("| 足 | 在 NFP (t) | 在 他 (t) | 外 NFP (t) | 外 他 (t) | 近年 NFP (t) |"); say("|---|---|---|---|---|---|")
bars = [(8, m) for m in range(0, 60, 5)] + [(9, 0)]
prof = {}
for h, m in bars:
    i = idx_of_bar(ts, epoch_et(days, h, m)); rb = np.where(i >= 0, r[np.clip(i, 0, len(r)-1)], np.nan); prof[(h, m)] = rb
    cells = []
    for lo, hi, g in ((2010, 2020, True), (2010, 2020, False), (2021, 2026, True), (2021, 2026, False), (2024, 2026, True)):
        sel = (YR >= lo) & (YR <= hi) & (nfp == g); mu, t, n = ms(rb[sel]); cells.append(f"{mu:+.2f} ({t:+.1f})")
    say(f"| {h:02d}:{m:02d} | " + " | ".join(cells) + " |")
# (2) JUMP on 08:25-bar return
say("\n## (2) JUMP（08:30 足）を 08:25 足リターンに回帰（HC1）・bid 戻りなら β<0")
r0825 = prof[(8, 25)]; jump = prof[(8, 30)]
for lab, lo, hi in (("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026), ("プール", 2010, 2026)):
    sel = (YR >= lo) & (YR <= hi)
    a = hc1_reg(jump[sel & nfp], r0825[sel & nfp]); b = hc1_reg(jump[sel & ~nfp], r0825[sel & ~nfp])
    # also 08:35 bar on 08:30 bar (post-jump continuation at 1 bar) for reference
    c = hc1_reg(prof[(8, 35)][sel & nfp], jump[sel & nfp])
    say(f"- {lab}: NFP 日 β {a['b']:+.2f} (t{a['t']:+.2f}, n{a['n']})・他金曜 β {b['b']:+.2f} (t{b['t']:+.2f}, n{b['n']})・参考 08:35 足 on 08:30 足（NFP）β {c['b']:+.3f} (t{c['t']:+.2f})")
    # share of days with 08:25 bar negative on NFP days
    x = r0825[sel & nfp]; x = x[np.isfinite(x)]; say(f"  - NFP 日 08:25 足: 平均 {x.mean():+.2f} bp・負の日 {np.mean(x<0)*100:.0f}%・中央値 {np.median(x):+.2f}・p10 {np.quantile(x,0.1):+.2f}")
# (3) account spread around NFP time (read-only)
say("\n## (3) 実口座 spread_log.jsonl（読取のみ）NFP 時刻 08:15〜08:45 ET の spread_pt")
fp = os.path.join(LIVE, "spread_log.jsonl")
try:
    rows = []
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line); rows.append((int(d["ts"]), float(d["spread_pt"]), float(d.get("bid", np.nan))))
            except Exception: pass
    A = np.array(rows, float); t_ = pd.to_datetime(A[:, 0], unit="s", utc=True).tz_convert(NY)
    say(f"- 行 {len(A)}・{t_[0]}〜{t_[-1]} ET・spread 中央値 {np.median(A[:,1]):.2f}・max {A[:,1].max():.2f}")
    dfa = pd.DataFrame({"t": t_, "sp": A[:, 1], "bid": A[:, 2]}); dfa["date"] = dfa["t"].dt.date; dfa["hm"] = dfa["t"].dt.hour * 60 + dfa["t"].dt.minute; dfa["wd"] = dfa["t"].dt.weekday
    win = dfa[(dfa["hm"] >= 8 * 60 + 15) & (dfa["hm"] <= 8 * 60 + 45) & (dfa["wd"] < 5)]
    # candidate NFP Fridays in log range by v3 rule (2026-07 以降は規則のみ・参照リスト無し)
    v3x = nfp_dates_v3(2026, 2026); cand = [d.date() for d in v3x if d.date() >= t_[0].date() and d.date() <= t_[-1].date()]
    say(f"- 期間内の v3 規則 NFP 候補日: {cand}（2026-07 以降は参照リスト無し・規則のみ・閉鎖等は未反映）")
    g = win.groupby("date")["sp"].agg(["count", "median", "max"]); g["wd"] = [pd.Timestamp(d).weekday() for d in g.index]
    say("- 平日 08:15〜08:45 ET の spread: 全日 中央値の中央値 {:.2f}・max の中央値 {:.2f}・max の最大 {:.2f}（日数 {}）".format(g["median"].median(), g["max"].median(), g["max"].max(), len(g)))
    for d in cand:
        if d in g.index: say(f"  - NFP 候補 {d}: n{int(g.loc[d,'count'])} 中央値 {g.loc[d,'median']:.2f} max {g.loc[d,'max']:.2f}")
        else: say(f"  - NFP 候補 {d}: ログ無し")
    top = g.sort_values("max", ascending=False).head(5); say("  - max 上位 5 日: " + "・".join(f"{d} {row['max']:.2f}" for d, row in top.iterrows()))
except Exception as ex:
    say(f"- 読込不可: {ex}")
say(f"\n実行 {time.time()-T0:.1f} s・判定不使用・書き込み本 md のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
