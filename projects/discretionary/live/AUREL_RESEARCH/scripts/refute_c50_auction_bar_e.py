# -*- coding: utf-8 -*-
"""
[反証レーン c50 補足 e] 独立ベンダー・完全 OOS での再現試験。
補足 d で spread_log.jsonl（口座の配信・2026-09-25..11-18・16 s 刻み）に **bid** が入っていると判った。
これは (1) Dukascopy とは別ベンダー、(2) XAU npz（..2026-06-30）の**完全に外**の期間。
c50 の沈みが「Dukascopy bid 固有の形」なら、ここには出ない。出れば独立再現。

事前固定（数字を見る前）:
E1 格子の作り方: London 5 分格子の各時刻 g について、g 以前で最も近い観測を採る。
   ただし |g − 観測時刻| <= 120 s のみ採用（それ以上古いものは NaN = stale を使わない）。
   平日のみ。両ログ（spread_log.jsonl ＋ spread_log_15m.jsonl）の ts 和集合を使う。
E2 主検定: R(10:25→10:30) = ln bid(10:30) − ln bid(10:25) の日次系列（bp）。
   **SURVIVE-17 = 点推定 <= -1.0 bp かつ t <= -1.5**（= 独立ベンダー・OOS で再現）
   **BREAK-17 = 点推定 >= 0、または（|t| < 1.5 かつ MDE 2se > 2.0 bp）**（= 再現せず／決着不能）
   どちらでもない（-1.0 < 点推定 < 0 かつ t<=-1.5 等）は「弱い再現」と明記。
E3 併記: 09:30-11:30 の 5 分プロファイル全部（n と MDE つき）・14:55→15:00・
   10:25→11:30 の累積（補足 b の BREAK-10「全戻し」が別ベンダーでも成立するか）。
E4 衛生: スロット別の採用日数・stale で落ちた率・bid の重複/逆行の有無。
限界: n <= 39 営業日＝検出力は 2026H1 の効果量（-3.95 bp）なら足りるが P4 平均（-1.07 bp）には足りない。
読取りのみ（本番ログは読取専用で開く）・発注なし・MT5 なし・外部通信なし・書込は AUREL_RESEARCH/ 配下のみ。
seed 20261118。
"""
import os, io, json, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "data", "refute_c50_auction_bar_e.md"); L = []
def say(s=""):
    print(s, flush=True); L.append(s)
def S(h, m): return h * 12 + m // 5
def lab(s): return f"{s // 12:02d}:{(s % 12) * 5:02d}"
def stat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return (np.nan, np.nan, n, np.nan)
    se = x.std(ddof=1) / math.sqrt(n)
    return (x.mean(), x.mean() / se if se > 0 else np.nan, n, se)
BP = 1e4; TOL = 120

say(f"# [反証レーン c50 補足 e] 独立ベンダー・完全 OOS での再現試験 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c50_auction_bar_e.py)")
say("")
say("口座配信の bid（spread_log*.jsonl・2026-09-25..11-18 = XAU npz の外）で 10:25→10:30 London の沈みを測り直す。Dukascopy bid 固有の形なら出ない。")

rec = {}
for fn in ("spread_log.jsonl", "spread_log_15m.jsonl"):
    p = os.path.join(LIVE, fn)
    if not os.path.exists(p): continue
    with io.open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try: o = json.loads(line)
            except Exception: continue
            if "ts" in o and "bid" in o:
                rec[int(o["ts"])] = float(o["bid"])
ts = np.array(sorted(rec.keys()), dtype=np.int64); bid = np.array([rec[t] for t in ts], dtype=float)
t_lon = pd.to_datetime(ts, unit="s", utc=True).tz_convert("Europe/London")
dayl = pd.DatetimeIndex(t_lon.tz_localize(None)).normalize()
wdl = t_lon.weekday.to_numpy()
say("")
say(f"- 観測 {len(ts)} 点（2 ログの ts 和集合）・{t_lon.min():%Y-%m-%d} .. {t_lon.max():%Y-%m-%d} London・平日 {int((wdl<=4).sum())} 点・bid {bid.min():.0f}-{bid.max():.0f} USD・間隔 中央値 {np.median(np.diff(ts)):.0f} s")

# ---------- E1 格子 ----------
days = sorted(set(pd.Timestamp(x) for x, w in zip(dayl, wdl) if w <= 4))
grid = np.full((len(days), 288), np.nan)
# 各日・各スロットの格子時刻（London 現地）を UTC 秒に直して探索
for i, dd in enumerate(days):
    base = pd.Timestamp(dd).tz_localize("Europe/London")
    gidx = (base + pd.to_timedelta(np.arange(288) * 5, unit="m")).tz_convert("UTC").tz_localize(None)
    gts = np.asarray(gidx, dtype="datetime64[s]").astype(np.int64)
    idx = np.searchsorted(ts, gts, side="right") - 1
    good = idx >= 0
    age = np.where(good, gts - ts[np.clip(idx, 0, len(ts) - 1)], np.inf)
    take = good & (age <= TOL)
    grid[i, take] = bid[np.clip(idx, 0, len(ts) - 1)][take]
lg = np.log(grid)
cov = np.isfinite(grid).mean(axis=0)
say(f"- 格子の採用率（120 s 以内の観測が有る日の割合）: 10:25 **{cov[S(10,25)]*100:.0f}%**／10:30 {cov[S(10,30)]*100:.0f}%／14:55 {cov[S(14,55)]*100:.0f}%／15:00 {cov[S(15,0)]*100:.0f}%／London 09:30-11:30 平均 {cov[S(9,30):S(11,30)].mean()*100:.0f}%・平日 {len(days)} 日")

# ---------- E2 ----------
say("")
say("## E2 主検定 — 10:25→10:30 London（独立ベンダー・完全 OOS）")
say("")
r = (lg[:, S(10, 30)] - lg[:, S(10, 25)]) * BP
mu, t, n, se = stat(r)
say(f"- **R(10:25→10:30) = {mu:+.2f} bp (t {t:+.2f}, n {n} 日・MDE 2se {2*se:.2f} bp)**・中央値 {np.nanmedian(r):+.2f}・負の日 {np.nanmean(r[np.isfinite(r)]<0)*100:.0f}%")
pm = (lg[:, S(15, 0)] - lg[:, S(14, 55)]) * BP
mu2, t2, n2, se2 = stat(pm)
say(f"- R(14:55→15:00) = {mu2:+.2f} bp (t {t2:+.2f}, n {n2}・MDE {2*se2:.2f})")
SURV17 = (mu <= -1.0) and (t <= -1.5)
BREAK17 = (mu >= 0) or ((abs(t) < 1.5) and (2 * se > 2.0))
say("")
say("- 参照（Dukascopy・同じ測り方の期間別）: P4 2021-26H1 -1.07 bp (t -7.9) ／ 2026H1 のみ -3.95 (t -6.2) ／ 2025 -1.30 (t -3.9)")

# ---------- E3 ----------
say("")
say("## E3 5 分プロファイル 09:30-11:30（独立ベンダー・bp・n つき）")
say("")
say("| 足（開始時刻） | 平均 bp | t | n | MDE 2se |")
say("|---|---|---|---|---|")
for s in range(S(9, 30), S(11, 30)):
    x = (lg[:, s + 1] - lg[:, s]) * BP
    m_, t_, n_, se_ = stat(x)
    if n_ < 5: continue
    bold = "**" if s == S(10, 25) else ""
    say(f"| {bold}{lab(s)}→{lab(s+1)}{bold} | {bold}{m_:+.2f}{bold} | {t_:+.2f} | {n_} | {2*se_:.2f} |")
say("")
say("- 累積（10:25 起点・別ベンダー）: " + " ｜ ".join(
    f"→{lab(s)} {stat((lg[:, s] - lg[:, S(10,25)]) * BP)[0]:+.2f} (t {stat((lg[:, s] - lg[:, S(10,25)]) * BP)[1]:+.1f}, n {stat((lg[:, s] - lg[:, S(10,25)]) * BP)[2]})"
    for s in (S(10, 35), S(10, 45), S(11, 0), S(11, 30))))

# ---------- 判定 ----------
say("")
say("## 判定（補足 e）")
say("")
say(f"| SURVIVE-17 | 点推定 <= -1.0 bp かつ t <= -1.5（独立ベンダー・OOS で再現） | {'**YES**' if SURV17 else 'no'} |")
say(f"| BREAK-17 | 点推定 >= 0、または \\|t\\|<1.5 かつ MDE > 2.0 bp（再現せず／決着不能） | {'**YES**' if BREAK17 else 'no'} |")
say("")
if SURV17: say("→ **独立ベンダー・完全 OOS で再現**（Dukascopy bid 固有の配信人工物という説明は否定される）")
elif BREAK17 and mu >= 0: say("→ **再現せず（符号が逆）= Dukascopy 固有の形の疑いが強まる**")
elif BREAK17: say("→ **決着不能（検出力不足）**: n が足りない")
else: say(f"→ **弱い再現**（点推定 {mu:+.2f} bp・t {t:+.2f}）: 符号は一致するが事前固定の閾値に届かない")
say("")
say("- 限界: n = " + f"{n}" + " 営業日のみ・口座配信は固定スプレッド（0.15/0.16）の加工済み気配である可能性・2026 秋は金が 3751-4315 USD の下落局面（P4 の組成と違う）。")
say(f"- 実行 {time.time()-T0:.1f} s・本番ログは**読取専用で開いたのみ**・発注なし・MT5 なし・外部通信なし・プロップ参照なし・秘密なし。seed 20261118")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
