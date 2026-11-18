# -*- coding: utf-8 -*-
"""
[反証レーン c50 補足 c] 補足 b で (i) BREAK-10 成立（P4 の 10:25→11:30 累積 +0.02 bp = 全戻し）
(ii) BREAK-9 成立（陽性対照 21:55 でも R_oo≈R_cc = T4 の格下げ）(iii) **BREAK-8 は逆に不成立で、
英国銀行休日（オークション無し）は +0.09 bp (t +0.3) vs 営業日 -0.93 (t -11.9)** になった。
= プラセボが機構を支持してしまった。ここを詰める（反証レーンの仕事は「支持した側も疑う」）。

事前固定（数字を見る前）:
C1 【休日プラセボの詰め】休日 vs 営業日の **差の t**／休日のボラで正規化（休日は配信が薄い＝
   「効果が無い」ではなく「全部が小さい」可能性）／休日の対照スロット（21:55・一般 :25）。
   BREAK-13 = 正規化後（効果 ÷ 当日 10-11 時 5 分リターンの sd）の 休日−営業日 差の |t| < 2
   （= プラセボは何も言っていない）。
C2 【正しい窓の経済性】本体 T6 は 20 分の正味で測ったが、BREAK-10（全戻し）が成立した以上、
   受け取りの対象は **5 分の往復（10:25 売り → 10:30 買い戻し）** だけ。bid-bid の沈み USD から
   往復 0.16 USD を 1 倍 / 2 倍引く。
   BREAK-12 = P4 で **2 倍コスト後 <= 0**（= コスト倍で壊れる）。
C3 【分岐点の定量】5 分間にスプレッドが w USD 開くと、買い戻しは ask で払うので受取りは w だけ減る。
   「受取り = 0」になる w（= 必要な拡大幅）を期間別に出す。= c50 が「ask【要取得】」と書いた問いを
   **定量化**する（決着不能であることは変わらないが、必要な観測精度が決まる）。
C4 【名札の価値】同じ 5 分往復を 21:55（オークションと無関係・既知境界）でもやる。
   BREAK-14 = 21:55 の net（1 倍コスト後）が 10:25 の net 以上（= 「オークション」という名札は
   経済的に何も足していない）。
C5 【OOS】5 分往復の net を in 2021-24 / out 2025-26H1 で分割。
読取りのみ・発注なし・MT5 なし・外部通信なし・書込は AUREL_RESEARCH/ 配下のみ。seed 20261118。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd
T0 = time.time(); np.random.seed(20261118)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c50_auction_bar_c.md"); L = []
def say(s=""):
    print(s, flush=True); L.append(s)
BP = 1e4
def S(h, m): return h * 12 + m // 5
def stat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return (np.nan, np.nan, n, np.nan)
    se = x.std(ddof=1) / math.sqrt(n)
    return (x.mean(), x.mean() / se if se > 0 else np.nan, n, se)
def dt_t(a, b):
    ma, _, na, sa = stat(a); mb, _, nb, sb = stat(b)
    return ma - mb, (ma - mb) / math.sqrt(sa ** 2 + sb ** 2), na, nb

say(f"# [反証レーン c50 補足 c] 休日プラセボの詰め・正しい窓の経済性・ask の分岐点 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c50_auction_bar_c.py)")
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64); cl = z["close"].astype(float); op = z["open"].astype(float)
t_lon = pd.to_datetime(ts, unit="s", utc=True).tz_convert("Europe/London")
wd = t_lon.weekday.to_numpy(); slot = t_lon.hour.to_numpy() * 12 + t_lon.minute.to_numpy() // 5
day = pd.DatetimeIndex(t_lon.tz_localize(None)).normalize(); flat = (cl == np.roll(cl, 1))
mwd = wd <= 4
df = pd.DataFrame({"day": day[mwd], "slot": slot[mwd], "lc": np.log(cl[mwd]), "c": cl[mwd], "flat": flat[mwd].astype(int)})
piv = lambda c: df.pivot_table(index="day", columns="slot", values=c, aggfunc="first").reindex(columns=range(288))
C = piv("lc"); CC = piv("c"); F = piv("flat")
d = pd.DatetimeIndex(C.index); Cv, CCv, Fv = C.to_numpy(), CC.to_numpy(), F.to_numpy()
rng = list(range(S(9, 50), S(16, 45)))
ok = np.isfinite(Cv[:, rng]).all(axis=1) & (np.nansum(1 - Fv[:, S(14, 30):S(15, 30)], axis=1) >= 8)
PER = {"P1 2010-13": np.asarray(d <= "2013-12-31"), "P2 2014-15/03": np.asarray((d >= "2014-01-01") & (d <= "2015-03-19")),
       "P3 2015/03-20 - 20": np.asarray((d >= "2015-03-20") & (d <= "2020-12-31")), "P4 2021-26H1": np.asarray(d >= "2021-01-01")}
PER = {k: v & ok for k, v in PER.items()}
def bar(s): return (Cv[:, s] - Cv[:, s - 1]) * BP

def easter(y):
    a = y % 19; b = y // 100; c = y % 100; dd = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - dd - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7; m_ = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m_ + 114) // 31; dy = ((h + l - 7 * m_ + 114) % 31) + 1
    return dt.date(y, mo, dy)
def first_mon(y, mo):
    x = dt.date(y, mo, 1); return x + dt.timedelta(days=(7 - x.weekday()) % 7)
def last_mon(y, mo):
    x = dt.date(y, mo, 31); return x - dt.timedelta(days=(x.weekday()) % 7)
def subst(x):
    while x.weekday() >= 5: x += dt.timedelta(days=1)
    return x
HOL = set()
for y in range(2010, 2027):
    e = easter(y)
    cand = [subst(dt.date(y, 1, 1)), e - dt.timedelta(days=2), e + dt.timedelta(days=1),
            first_mon(y, 5), last_mon(y, 5), last_mon(y, 8)]
    x = dt.date(y, 12, 25); y2 = dt.date(y, 12, 26)
    if x.weekday() == 5: cand += [dt.date(y, 12, 27), dt.date(y, 12, 28)]
    elif x.weekday() == 6: cand += [dt.date(y, 12, 26), dt.date(y, 12, 27)]
    elif y2.weekday() == 5: cand += [x, dt.date(y, 12, 28)]
    else: cand += [x, y2]
    if y == 2012: cand += [dt.date(2012, 6, 4), dt.date(2012, 6, 5)]
    if y == 2022: cand += [dt.date(2022, 6, 2), dt.date(2022, 6, 3), dt.date(2022, 9, 19)]
    if y == 2023: cand += [dt.date(2023, 5, 8)]
    if y == 2020: cand = [c for c in cand if c != first_mon(2020, 5)] + [dt.date(2020, 5, 8)]
    for c in cand:
        if c.weekday() <= 4: HOL.add(pd.Timestamp(c))
hol = np.isin(d.values, np.array(sorted(HOL), dtype="datetime64[ns]"))

# ---------- C1 ----------
say("")
say("## C1 休日プラセボの詰め — 「休日は沈まない」は効果の不在か、配信が薄いだけか")
say("")
x25 = bar(S(10, 25)); x2155 = bar(S(21, 55))
sd_day = np.nanstd(np.diff(Cv[:, S(10, 0):S(11, 0)], axis=1) * BP, axis=1)  # 当日 10-11 時の 5 分 sd
say("| 量 | 営業日 (ok, 休日除く) | 英国休日 | 差 | 差の t |")
say("|---|---|---|---|---|")
biz = ok & ~hol
for nm, v in (("10:25 足 bp", x25), ("21:55 足 bp（非オークション対照）", x2155),
              ("10:25 足 ÷ 当日 10-11 時 sd", x25 / np.where(sd_day > 0, sd_day, np.nan)),
              ("当日 10-11 時 5 分 sd (bp)", sd_day), ("10:35 足 bp", bar(S(10, 35)))):
    a = stat(v[biz]); b = stat(v[hol]); dm, tt, na, nb = dt_t(v[hol], v[biz])
    say(f"| {nm} | {a[0]:+.3f} (t {a[1]:+.1f}, n {a[2]}) | {b[0]:+.3f} (t {b[1]:+.1f}, n {b[2]}) | {dm:+.3f} | **{tt:+.2f}** |")
_, t_norm, _, _ = dt_t((x25 / np.where(sd_day > 0, sd_day, np.nan))[hol], (x25 / np.where(sd_day > 0, sd_day, np.nan))[biz])
BREAK13 = abs(t_norm) < 2
say("")
say("- 一般 :25 足（London 07-21 時・10/15 時除く）の 休日 vs 営業日: " + " ｜ ".join(
    f"{nm} {stat(np.concatenate([bar(S(h,25))[m][np.isfinite(bar(S(h,25))[m])] for h in range(7,21) if h not in (10,15)]))[0]:+.3f}"
    for nm, m in (("営業日", biz), ("休日", hol))))
say(f"- 休日の年別 10:25（n>=5 の年）: " + " ".join(f"{y}:{stat(x25[hol & (np.asarray(d.year)==y)])[0]:+.1f}" for y in range(2010, 2027) if (hol & (np.asarray(d.year) == y)).sum() >= 5))

# ---------- C2 / C3 / C4 / C5 ----------
say("")
say("## C2/C3 正しい窓（5 分往復）の経済性と、ask の分岐点")
say("")
say("10:25 に売り（bid で約定）→ 10:30 に買い戻し（ask で約定）。gross = bid-bid の沈み。往復コスト = 0.16 USD（c4 実測）。")
say("w = 5 分間のスプレッド拡大（USD）。受取り = gross - 0.16 - w。**w* = gross - 0.16 = 受取りが 0 になる拡大幅**。")
say("")
say("| 窓 | 期間 | gross bp (t) | 価格 | gross USD | net -1x | net -2x | **w\\* (USD)** | 基準スプレッド比 |")
say("|---|---|---|---|---|---|---|---|---|")
RES = {}
for nm, s in (("10:25 (AM オークション直前)", S(10, 25)), ("14:55 (PM オークション直前)", S(14, 55)), ("21:55 (非オークション・既知境界)", S(21, 55))):
    for k, m in PER.items():
        mu, t, n, se = stat(bar(s)[m]); px = np.nanmean(CCv[m, s])
        g = -mu / BP * px  # 売りの受取り（沈みが負なら正）
        say(f"| {nm} | {k} | {mu:+.2f} ({t:+.1f}) | {px:.0f} | {g:+.4f} | {g-0.16:+.4f} | {g-0.32:+.4f} | **{g-0.16:+.4f}** | {(g-0.16)/0.16:+.2f}x |")
        RES[(nm, k)] = (g, g - 0.16, g - 0.32)
BREAK12 = RES[("10:25 (AM オークション直前)", "P4 2021-26H1")][2] <= 0
BREAK14 = RES[("21:55 (非オークション・既知境界)", "P4 2021-26H1")][1] >= RES[("10:25 (AM オークション直前)", "P4 2021-26H1")][1]
say("")
say("- 注: 2026H1 だけ（n 127・10:25 = -3.95 bp・価格 " + f"{np.nanmean(CCv[PER['P4 2021-26H1'] & np.asarray(d>='2026-01-01'), S(10,25)]):.0f}" + " USD）: gross " +
    f"{3.95/BP*np.nanmean(CCv[PER['P4 2021-26H1'] & np.asarray(d>='2026-01-01'), S(10,25)]):.4f} USD → net -1x {3.95/BP*np.nanmean(CCv[PER['P4 2021-26H1'] & np.asarray(d>='2026-01-01'), S(10,25)])-0.16:+.4f} / -2x {3.95/BP*np.nanmean(CCv[PER['P4 2021-26H1'] & np.asarray(d>='2026-01-01'), S(10,25)])-0.32:+.4f}（ただし 2026 のスプレッド水準は【要取得】・0.16 は 2024-26 台帳の実測）")

say("")
say("## C5 OOS（5 分往復・10:25・net は 1 倍コスト後）")
say("")
P4 = PER["P4 2021-26H1"]
for nm, m in (("in 2021-24", P4 & np.asarray(d <= "2024-12-31")), ("out 2025-26H1", P4 & np.asarray(d >= "2025-01-01")),
              ("out 2025 のみ", P4 & np.asarray((d >= "2025-01-01") & (d <= "2025-12-31"))), ("out 2026H1 のみ", P4 & np.asarray(d >= "2026-01-01"))):
    mu, t, n, se = stat(bar(S(10, 25))[m]); px = np.nanmean(CCv[m, S(10, 25)])
    g = -mu / BP * px
    say(f"- {nm}: {mu:+.2f} bp (t {t:+.2f}, n {n}) ・価格 {px:.0f} ・gross {g:+.4f} USD ・net -1x **{g-0.16:+.4f}** ・net -2x {g-0.32:+.4f} ・年換算（250 日・無レバ） {(g-0.16)*250/px*100:+.2f}%")

say("")
say("## 判定の更新（補足 c）")
say("")
say("| BREAK | 内容 | 成立 |")
say("|---|---|---|")
say(f"| BREAK-12 | P4 の 5 分往復が 2 倍コストで <=0 | {'**YES**' if BREAK12 else 'no'} |")
say(f"| BREAK-13 | 休日プラセボは正規化後 |t|<2 で何も言っていない | {'**YES**' if BREAK13 else f'no（正規化後の差の t {t_norm:+.2f}）'} |")
say(f"| BREAK-14 | 21:55（非オークション）の net が 10:25 以上 = 名札に価値なし | {'**YES**' if BREAK14 else 'no'} |")
say("")
say(f"- 実行 {time.time()-T0:.1f} s・読取りのみ・発注なし・MT5 なし・外部通信なし・プロップ参照なし。seed 20261118")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
