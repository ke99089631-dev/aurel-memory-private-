# -*- coding: utf-8 -*-
"""
[REFUTE c16 事後フォロー b・判定規則は不変] refute_c16_reopen_gap.py の結果を見た後に追加した記述:
 (1) 2010-13 の Dukascopy 金の取引スケジュール（ET 時別 flat 比率 年別）と、Q4 の「休止明け足」209 本の年×ET 時×休止長の内訳と平均
     （2010-12 は 17–18 ET ブレイクが無い＝cycle16 の「17 年中 15 年」の 2010-12 は再開ギャップではない。ではその年の休止はどこで、明けは正か負か）。
 (2) 同日結合: 再開 最初の 1 分 r_first を 引け最後の取引 1 分 r_last（16:55–16:56 ET）に回帰。β≈−1 なら純粋な snap-back。切片＝snap-back で説明できない残り。
 (3) 引け最後の 1 分を除いたギャップ G_5 の年別符号・t（「情報」成分の年別安定性）。
 (4) 実口座 spread_log（読取のみ）: 日別に 16:50–16:55 の bid 中央値 → 16:55–17:00 の最後の bid（最後の 1 分の沈みが別業者でも出るか）。
入力は既存キャッシュ＋M1 chunks（読取）＋spread_log（読取）。scan 無し・MT5 無し・外部通信無し。
"""
import os, time, math, json, glob
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro"); CHUNKS = r"C:\Users\user\AssetEmpire\empire\research\dukas\chunks"
OUT = os.path.join(DATA, "refute_c16_reopen_gap_b.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
def ms(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 2: return (np.nan, np.nan, np.nan, n)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return (m, se, m / se if se > 0 else np.nan, n)
def fmt(x, extra=False):
    m, se, t, n = ms(x); s = f"{m:+.2f} (t{t:+.1f}, n{n})"
    if extra and n > 1: s += f", 正 {(np.asarray(x)>0).mean()*100:.0f}%"
    return s
say(f"# [REFUTE c16 b] 再開ギャップ 事後フォロー — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c16_reopen_gap_b.py)")
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); r_bp = r * 1e4; flat = r == 0
dts = np.diff(ts); valid = np.ones(len(ts), bool); valid[np.where(dts != 300)[0] + 1] = False
t_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert("America/New_York")
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy(); mo = t_ny.month.to_numpy()
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)

say("\n## (1) スケジュール鑑識: ET 時別 flat 比率（月〜木）年別 2010-2014")
for y in range(2010, 2015):
    w = (wd <= 3) & (yr == y)
    say(f"- {y}: " + " ".join(f"{hh}:{flat[w&(h==hh)].mean()*100:.0f}" for hh in range(24)))
# summer vs winter 2010-2012
dst = (t_ny.map(lambda x: x.dst().total_seconds()) > 0).to_numpy() if False else (np.array([o.utcoffset().total_seconds() for o in t_ny[:1]]) is not None)
off = (ts - (t_ny.tz_localize(None).astype("int64").to_numpy() // 10**9))  # utc - local seconds → -offset
summer = off == -4 * 3600
for y in (2010, 2011, 2012):
    for lab, m_ in (("夏(EDT)", summer), ("冬(EST)", ~summer)):
        w = (wd <= 3) & (yr == y) & m_
        say(f"- {y} {lab}: 16-21 ET flat% " + " ".join(f"{hh}:{flat[w&(h==hh)].mean()*100:.0f}" for hh in range(15, 22)) +
            " ｜ 時別平均 bp " + " ".join(f"{hh}:{r_bp[w&(h==hh)&valid].sum()/max(1,len(np.unique((yr*10000+mo*100+t_ny.day.to_numpy())[w&(h==hh)]))):+.1f}" for hh in range(15, 22)))
# Q4 events breakdown
run = np.zeros(len(flat), dtype=np.int32)
for i in range(1, len(flat)):
    run[i] = run[i - 1] + 1 if flat[i - 1] else 0
cand = (run >= 12) & (~flat) & (wd <= 4) & (h != 18) & valid
iP = np.where(cand)[0]
df = pd.DataFrame({"yr": yr[iP], "h": h[iP], "run": run[iP], "r": r_bp[iP], "summer": summer[iP]})
say("\n- Q4 休止明け足の内訳（年 × ET 時・n／平均 bp）:")
pv = df.groupby(["yr", "h"])["r"].agg(["size", "mean"]).reset_index()
for y, g in pv.groupby("yr"):
    say(f"  - {y}: " + " ".join(f"{int(hh)}時 n{int(n)} {m:+.1f}" for hh, n, m in zip(g["h"], g["size"], g["mean"])))
for lab, m_ in (("19 時明け", df.h == 19), ("20 時明け", df.h == 20), ("夏 19/20 時明け", (df.h.isin([19, 20])) & df.summer), ("冬 19/20 時明け", (df.h.isin([19, 20])) & ~df.summer)):
    x = df.loc[m_, "r"].to_numpy(); say(f"  - {lab}: {fmt(x, True)}・休止長 中央値 {df.loc[m_,'run'].median():.0f} 本")
# For the 19/20 ET reopen bars in 2010-12: G from 1h before pause start
iQ = iP[(h[iP] >= 19) & (h[iP] <= 20) & (yr[iP] <= 2012)]
pause_start = iQ - run[iQ]           # first flat bar index; its close == last traded close (bar before it = last traded bar close? flat bar close equals previous close)
last_traded = pause_start - 1
g_pre = (lc[iQ] - lc[last_traded]) * 1e4                 # = r at reopen (same as r_bp[iQ]) sanity
g_pre30 = (lc[iQ] - lc[last_traded - 6]) * 1e4
dip30 = (lc[last_traded] - lc[last_traded - 6]) * 1e4
say(f"  - 2010-12 の 19/20 時明け n{len(iQ)}: 明け足 {fmt(r_bp[iQ], True)} ／ 休止前 30 分 {fmt(dip30, True)} ／ 休止前 30 分始点→明け {fmt(g_pre30, True)}")

say("\n## (2) 同日結合（M1）: r_first(18:00–18:01) = a + β·r_last(16:55–16:56)")
files = sorted(glob.glob(os.path.join(CHUNKS, "xauusd-m1-bid-*.csv")))
m1 = pd.concat([pd.read_csv(f, usecols=["timestamp", "close"], dtype={"timestamp": np.int64, "close": np.float64}) for f in files], ignore_index=True)
m1 = m1.drop_duplicates("timestamp").sort_values("timestamp"); ts1 = (m1["timestamp"].to_numpy() // 1000).astype(np.int64); lc1 = np.log(m1["close"].to_numpy()); del m1
iG = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]
BRK = np.column_stack([idx_at(ts[iG] - 300 * j) for j in range(1, 13)]); ok = np.all(BRK >= 0, axis=1)
iG = iG[ok]; BRK = BRK[ok]; clean = np.all(flat[BRK], axis=1); iG = iG[clean]; yG = yr[iG]
j0 = np.searchsorted(ts1, ts[iG]); okj = (ts1[np.clip(j0, 0, len(ts1) - 1)] == ts[iG]) & (j0 >= 70) & (j0 + 5 < len(ts1)); j0 = j0[okj]; yG = yG[okj]; iG = iG[okj]
r_first = (lc1[j0] - lc1[j0 - 1]) * 1e4; r_last = (lc1[j0 - 61] - lc1[j0 - 62]) * 1e4; r_rest4 = (lc1[j0 + 4] - lc1[j0]) * 1e4
g5 = (lc1[j0 + 4] - lc1[j0 - 62]) * 1e4   # from 16:55 close (before last minute) to 18:05
# check the last traded minute really is 16:55-16:56: fraction of nonzero r_last and zero r for 16:56..17:00
zero_after = np.all(np.column_stack([(lc1[j0 - 61 + k] - lc1[j0 - 62 + k]) == 0 for k in range(1, 5)]), axis=1)
say(f"- クリーン日 n{len(j0)}（2013-26）。16:56–17:00 の 4 分が全部 flat の日 {zero_after.mean()*100:.1f}%・r_last≠0 の日 {(r_last!=0).mean()*100:.1f}%（＝Dukascopy の最終取引分は 16:55–16:56 ET）")
W = {"在2013-20": (2013, 2020), "外2021-26H1": (2021, 2026), "近年2024-26H1": (2024, 2026)}
for wn, (a, b) in W.items():
    w = (yG >= a) & (yG <= b); x = r_last[w]; y = r_first[w]
    beta = np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1); alpha = y.mean() - beta * x.mean(); res = y - alpha - beta * x
    se_b = math.sqrt((res**2).sum() / (len(x) - 2) / ((x - x.mean())**2).sum()); se_a = math.sqrt((res**2).sum() / (len(x) - 2) * (1 / len(x) + x.mean()**2 / ((x - x.mean())**2).sum()))
    say(f"- {wn}: r_last {fmt(x)} bp・r_first {fmt(y)} bp；β {beta:+.3f} (t{beta/se_b:+.1f})・切片 a {alpha:+.2f} (t{alpha/se_a:+.1f})・ρ {np.corrcoef(x,y)[0,1]:+.3f}；"
        f" r_first | r_last<0: {fmt(y[x<0])} ／ r_last≥0: {fmt(y[x>=0])}；r_first + r_last（往復の純額） {fmt(y+x)}；G_5 {fmt(g5[w])}")
say("\n## (3) G_5（最後の 1 分を除いたギャップ 16:55→18:05）年別")
pos = 0; ny = 0
for y in range(2013, 2027):
    w = yG == y
    if w.sum() < 20: continue
    ny += 1; m, se, t, n = ms(g5[w]); pos += int(m > 0); mf, _, tf, _ = ms(r_first[w]); ml, _, tl, _ = ms(r_last[w])
    say(f"- {y}: G_5 {m:+.2f} (t{t:+.1f}, n{n}) ｜ r_last {ml:+.2f} (t{tl:+.1f}) ｜ r_first {mf:+.2f} (t{tf:+.1f})")
say(f"→ G_5 正の年 {pos}/{ny}")

say("\n## (4) 実口座 spread_log（読取のみ）: 最後の 1 分の沈みは別業者でも出るか")
try:
    rows = []
    with open(os.path.join(LIVE, "spread_log.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line); rows.append((int(o["ts"]), float(o["spread_pt"]), float(o["bid"])))
            except Exception: pass
    S = pd.DataFrame(rows, columns=["ts", "sp", "bid"]).drop_duplicates("ts").sort_values("ts")
    tn = pd.to_datetime(S["ts"], unit="s", utc=True).dt.tz_convert("America/New_York")
    S["d"] = (tn.dt.year * 10000 + tn.dt.month * 100 + tn.dt.day).to_numpy(); S["h"] = tn.dt.hour.to_numpy(); S["m"] = tn.dt.minute.to_numpy(); S["s"] = tn.dt.second.to_numpy(); S["wd"] = tn.dt.weekday.to_numpy()
    S = S[S["wd"] <= 3]
    recs = []
    for d, g in S.groupby("d"):
        a = g[(g.h == 16) & (g.m >= 50) & (g.m < 55)]; b = g[(g.h == 16) & (g.m >= 55)]; c = g[(g.h == 18) & (g.m < 2)]
        if len(a) >= 2 and len(b) >= 1:
            lastb = b.iloc[-1]
            recs.append((d, math.log(lastb.bid / a.bid.median()) * 1e4, lastb.m * 60 + lastb.s, len(b), lastb.sp, a.sp.median(),
                         (math.log(c.iloc[0].bid / lastb.bid) * 1e4) if len(c) else np.nan))
    R = pd.DataFrame(recs, columns=["d", "dip_bp", "last_sec", "n_last5", "sp_last", "sp_5055", "pop_bp"])
    say(f"- 日 {len(R)}: 16:50–16:55 bid 中央値 → 16:55 以降 最後の bid: {fmt(R.dip_bp.to_numpy(), True)} bp；最後の tick 時刻 中央値 16:{int(R.last_sec.median()//60)}:{int(R.last_sec.median()%60):02d}・16:55 以降の tick 数 中央値 {R.n_last5.median():.0f}；"
        f" spread 16:50-55 {R.sp_5055.median():.2f} → 最後 {R.sp_last.median():.2f} USD；再開 最初の tick（18:00–18:02）までの pop {fmt(R.pop_bp.dropna().to_numpy(), True)} bp")
    say(f"- 同期間の Dukascopy（2026-09-25〜 の M1 は無い・npz は 2026-06-30 まで）→ 直接突合不可。記述のみ。")
except Exception as e:
    say(f"- spread_log 読取失敗: {e}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
