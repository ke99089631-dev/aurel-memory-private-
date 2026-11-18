# -*- coding: utf-8 -*-
"""
[反証レーン c50 補足 b] 本体 refute_c50_auction_bar.py で BREAK-1..4 が P4 で 1 つも成立せず
（= 主判定 survived）だったので、**残った代替仮説と、自分の反証道具そのものの検出力**を潰す。
事前固定（この docstring・数字を見る前）:

S1 【反転・持続】London 09:30-11:30 / 14:00-16:00 の **累積** プロファイル（期間別・bp）。
    BREAK-10 = P4 で 10:25 起点の累積が 11:30 までに -0.2 bp 以上（= ほぼ全戻し = 沈みは一過性で何も残らない）。

S2 【組成】10:25 足を 曜日 / 月末 3 営業日 / NFP 日 / 十分位 で分解。
    BREAK-11 = P4 で 「1 つの曜日」または「月末 3 営業日」を除くと点推定が -0.5 bp より 0 に寄る
    （= 「毎日の沈み」ではなく暦の一部の顔）。

S3 【近年の集中】P4 の年別・2025-26 の月別。記述（判定なし・OOS の強まりが 1 四半期の産物かを見る）。

S4 ★【自分の道具の陽性対照】21:55 London 足（P3 t -23.5 / P4 t -10.1）= 17:00 ET の日次ブレイク直前
    ＝「既知の配信/セッション境界の人工物」の最有力。これを T4 と同じ 3 通り（R_cc / R_oo / R_co / GAP）
    で分解する。
    BREAK-9 = 21:55 でも R_oo ≈ R_cc（|R_oo| >= 0.5*|R_cc| かつ t(R_oo) <= -2）＝ T4 は
    「最終ティック人工物」を検出する力が無い → 本体の T4 survived は inconclusive へ格下げ。

S5 【単位】沈みを USD でも出し、片道スプレッド（往復 0.16 USD の半分 = 0.08 USD）と比べる。
    記述（人工物なら気配幅の内側に収まるはず）。

S6 HL 中点リターンを bp で出し直す（本体は log 単位で印字してしまった）。

S7 ★【英国銀行休日プラセボ】LBMA オークションは英国銀行休日には**開かれない**が、XAU OTC は配信が続く。
    英国銀行休日（規則導出: 元日・聖金曜日・イースター月曜・5 月第 1 月曜・5 月最終月曜・
    8 月最終月曜・12/25・12/26 ＋ 週末に当たる場合の振替月曜/火曜）の 10:25 足を見る。
    BREAK-8 = 休日でも 10:25 足 <= -0.5 bp かつ t <= -1.5（= オークションが無い日にも沈む = 機構否定）。
    power 不足（|t|<1.5 かつ MDE 2se > 1.07 bp）なら「決着不能」と明記して BREAK とはしない。

判定の更新規則: BREAK-8 または BREAK-9 または BREAK-10 が成立 → 本体の survived を **broken**（S8/S10）
または **inconclusive**（S9 = 道具の力不足）に更新。BREAK-11 は記述の限定として併記。
読取りのみ・発注なし・MT5 なし・外部通信なし（休日暦は規則導出）・書込は AUREL_RESEARCH/ 配下のみ。seed 20261118。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time(); np.random.seed(20261118)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c50_auction_bar_b.md"); L = []
def say(s=""):
    print(s, flush=True); L.append(s)
BP = 1e4
def S(h, m): return h * 12 + m // 5
def lab(s): return f"{s // 12:02d}:{(s % 12) * 5:02d}"
def stat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return (np.nan, np.nan, n, np.nan)
    se = x.std(ddof=1) / math.sqrt(n)
    return (x.mean(), x.mean() / se if se > 0 else np.nan, n, se)

say(f"# [反証レーン c50 補足 b] 残った代替仮説と反証道具の検出力 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c50_auction_bar_b.py)")
say("")
say("本体で BREAK-1..4 が P4 で 0 件（survived）だったため、(a) 一過性か (b) 暦の一部か (c) **T4 自身に検出力があるか** (d) **オークションが無い日にも沈むか** を潰す。事前固定は本 script の docstring。")

z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64)
op = z["open"].astype(float); hi = z["high"].astype(float); lo = z["low"].astype(float); cl = z["close"].astype(float)
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_lon = t_utc.tz_convert("Europe/London")
wd = t_lon.weekday.to_numpy(); slot = t_lon.hour.to_numpy() * 12 + t_lon.minute.to_numpy() // 5
day = pd.DatetimeIndex(t_lon.tz_localize(None)).normalize()
flat = (cl == np.roll(cl, 1))
mwd = wd <= 4
df = pd.DataFrame({"day": day[mwd], "slot": slot[mwd], "lc": np.log(cl[mwd]), "lo_o": np.log(op[mwd]),
                   "hi": hi[mwd], "low": lo[mwd], "c": cl[mwd], "flat": flat[mwd].astype(int)})
piv = lambda c: df.pivot_table(index="day", columns="slot", values=c, aggfunc="first").reindex(columns=range(288))
C = piv("lc"); O = piv("lo_o"); H = piv("hi"); LO = piv("low"); CC = piv("c"); F = piv("flat")
d = pd.DatetimeIndex(C.index)
Cv, Ov, Hv, LOv, CCv, Fv = C.to_numpy(), O.to_numpy(), H.to_numpy(), LO.to_numpy(), CC.to_numpy(), F.to_numpy()
rng = list(range(S(9, 50), S(16, 45)))
ok = np.isfinite(Cv[:, rng]).all(axis=1) & (np.nansum(1 - Fv[:, S(14, 30):S(15, 30)], axis=1) >= 8)
PER = {"P1 2010-13": np.asarray(d <= "2013-12-31"), "P2 2014-15/03": np.asarray((d >= "2014-01-01") & (d <= "2015-03-19")),
       "P3 2015/03-20 - 20": np.asarray((d >= "2015-03-20") & (d <= "2020-12-31")), "P4 2021-26H1": np.asarray(d >= "2021-01-01")}
PER = {k: v & ok for k, v in PER.items()}
P4 = PER["P4 2021-26H1"]
def bar(s): return (Cv[:, s] - Cv[:, s - 1]) * BP

# ---------- S1 ----------
say("")
say("## S1 累積プロファイル（10:25 起点・bp・期間別）— 沈みは戻るのか")
say("")
say("| 到達時刻 | " + " | ".join(PER.keys()) + " |")
say("|---|---|---|---|---|")
base = S(10, 25) - 1
for s in [S(10, 30), S(10, 35), S(10, 45), S(11, 0), S(11, 30), S(12, 0), S(16, 0)]:
    row = [f"10:25 → {lab(s)}"]
    for k, m in PER.items():
        mu, t, n, se = stat(((Cv[:, s] - Cv[:, base]) * BP)[m]); row.append(f"{mu:+.2f} ({t:+.1f})")
    say("| " + " | ".join(row) + " |")
cum1130 = stat(((Cv[:, S(11, 30)] - Cv[:, base]) * BP)[P4])
BREAK10 = cum1130[0] >= -0.2
say("")
say("| 到達時刻 (PM・14:55 起点) | " + " | ".join(PER.keys()) + " |")
say("|---|---|---|---|---|")
base2 = S(14, 55) - 1
for s in [S(15, 0), S(15, 5), S(15, 15), S(15, 30), S(16, 0)]:
    row = [f"14:55 → {lab(s)}"]
    for k, m in PER.items():
        mu, t, n, se = stat(((Cv[:, s] - Cv[:, base2]) * BP)[m]); row.append(f"{mu:+.2f} ({t:+.1f})")
    say("| " + " | ".join(row) + " |")

# ---------- S2 ----------
say("")
say("## S2 組成（10:25 足・P4）— 曜日 / 月末 3 営業日 / NFP 日 / 十分位")
say("")
x25 = bar(S(10, 25))
WD = np.asarray(pd.DatetimeIndex(d).weekday)
row = []
for w, nm in enumerate(["月", "火", "水", "木", "金"]):
    mu, t, n, se = stat(x25[P4 & (WD == w)]); row.append(f"{nm} {mu:+.2f} (t {t:+.1f}, n {n})")
say("- 曜日: " + " ｜ ".join(row))
say("- 曜日 1 つを抜いたときの P4 点推定: " + " ｜ ".join(
    f"-{nm} {stat(x25[P4 & (WD != w)])[0]:+.2f}" for w, nm in enumerate(["月", "火", "水", "木", "金"])))
ym = np.asarray(pd.DatetimeIndex(d).to_period("M").astype(str))
bidx = pd.Series(np.arange(len(d))[P4]).groupby(pd.Series(ym[P4]).values).rank(ascending=False)
eom = np.zeros(len(d), bool); eom[np.arange(len(d))[P4][bidx.to_numpy() <= 3]] = True
a = stat(x25[P4 & eom]); b = stat(x25[P4 & ~eom])
say(f"- 月末 3 営業日 {a[0]:+.2f} (t {a[1]:+.1f}, n {a[2]}) ｜ それ以外 {b[0]:+.2f} (t {b[1]:+.1f}, n {b[2]})")
# NFP: 第 1 金曜近似ではなく「金曜かつ 1-7 日」（c24 の規則は暦 CSV 無しなので近似・記述のみ）
nfp = (WD == 4) & (np.asarray(pd.DatetimeIndex(d).day) <= 7)
a = stat(x25[P4 & nfp]); b = stat(x25[P4 & ~nfp])
say(f"- NFP 近似日（第 1 金曜・近似） {a[0]:+.2f} (t {a[1]:+.1f}, n {a[2]}) ｜ それ以外 {b[0]:+.2f} (t {b[1]:+.1f}, n {b[2]})")
xx = x25[P4]; xx = xx[np.isfinite(xx)]
q = np.quantile(xx, [0.1, 0.25, 0.5, 0.75, 0.9])
say(f"- 分布（P4・n {len(xx)}）: 十分位 {q[0]:+.1f} / 四分位 {q[1]:+.1f} / 中央 {q[2]:+.1f} / {q[3]:+.1f} / {q[4]:+.1f} ・負の日 {(xx<0).mean()*100:.1f}% ・最大負 5 日を除いた平均 {np.sort(xx)[5:].mean():+.2f} ・両端 5% を切った平均 {xx[(xx>np.quantile(xx,0.05))&(xx<np.quantile(xx,0.95))].mean():+.2f}")
BREAK11 = False
for w in range(5):
    if stat(x25[P4 & (WD != w)])[0] > -0.5: BREAK11 = True
if b[0] > -0.5 or stat(x25[P4 & ~eom])[0] > -0.5: BREAK11 = True

# ---------- S3 ----------
say("")
say("## S3 近年の集中（記述）")
say("")
yr = np.asarray(pd.DatetimeIndex(d).year)
say("- P4 年別: " + " ｜ ".join(f"{y} {stat(x25[P4 & (yr == y)])[0]:+.2f} (t {stat(x25[P4 & (yr == y)])[1]:+.1f}, n {stat(x25[P4 & (yr == y)])[2]})" for y in range(2021, 2027)))
m25 = P4 & (d >= "2025-01-01")
say("- 2025-26H1 月別: " + " ".join(f"{p}:{stat(x25[m25 & (ym == p)])[0]:+.1f}" for p in sorted(set(ym[m25]))))

# ---------- S4 ----------
say("")
say("## S4 ★ 自分の道具（T4）の陽性対照 — 21:55 London 足 = 17:00 ET 日次ブレイク直前（既知の配信境界）")
say("")
say("| 足 | 期間 | R_cc | R_oo | R_co（足内） | GAP（継ぎ目） | GAP 占有 | flat 率 |")
say("|---|---|---|---|---|---|---|---|")
BREAK9 = {}
for s in (S(21, 55), S(22, 0), S(10, 25)):
    for k, m in PER.items():
        r_cc = (Cv[:, s] - Cv[:, s - 1]) * BP; r_oo = (Ov[:, s + 1] - Ov[:, s]) * BP
        r_co = (Cv[:, s] - Ov[:, s]) * BP; gap = (Ov[:, s] - Cv[:, s - 1]) * BP
        o = [stat(x[m]) for x in (r_cc, r_oo, r_co, gap)]
        share = o[3][0] / o[0][0] if abs(o[0][0]) > 1e-9 else np.nan
        fr = np.nanmean(Fv[m, s]) * 100
        say(f"| {lab(s)} | {k} | {o[0][0]:+.2f} (t {o[0][1]:+.1f}) | **{o[1][0]:+.2f} (t {o[1][1]:+.1f})** | {o[2][0]:+.2f} | {o[3][0]:+.2f} (t {o[3][1]:+.1f}) | {share*100:.0f}% | {fr:.0f}% |")
        if s == S(21, 55):
            BREAK9[k] = (abs(o[1][0]) >= 0.5 * abs(o[0][0])) and (o[1][1] <= -2)
say("")
say("- 解釈の鍵: 21:55 は「既知の境界直前の沈み」の最有力候補。ここで R_oo が R_cc と同じなら、T4（初回ティック）は最終ティック人工物を**見分けられない** → 本体 T4 の survived は無力。21:55 の正味（21:55→22:30）も印字:")
for k, m in PER.items():
    mu, t, n, se = stat(((Cv[:, S(22, 30)] - Cv[:, S(21, 55) - 1]) * BP)[m])
    say(f"  - {k}: 21:55→22:30 累積 {mu:+.2f} bp (t {t:+.1f}, n {n})")

# ---------- S5 / S6 ----------
say("")
say("## S5/S6 単位（USD）と HL 中点（bp で出し直し）")
say("")
mid = np.log((Hv + LOv) / 2.0)
say("| 足 | 期間 | 沈み bp | 平均価格 | 沈み USD | 片道 0.08 USD の bp | HL 中点 bp (t) | CLV |")
say("|---|---|---|---|---|---|---|---|")
for s, ref in ((S(10, 25), (S(10, 0), S(11, 0))), (S(14, 55), (S(14, 0), S(15, 0)))):
    for k, m in PER.items():
        mu, t, n, se = stat(bar(s)[m]); px = np.nanmean(CCv[m, s])
        hm = stat(((mid[:, s] - mid[:, s - 1]) * BP)[m])
        rngb = Hv[:, s] - LOv[:, s]
        clv = np.nanmean(((CCv[:, s] - LOv[:, s]) / np.where(rngb > 0, rngb, np.nan))[m])
        say(f"| {lab(s)} | {k} | {mu:+.2f} | {px:.0f} | **{mu/BP*px:+.4f}** | {0.08/px*BP:.2f} | {hm[0]:+.2f} ({hm[1]:+.1f}) | {clv:.3f} |")

# ---------- S7 ----------
say("")
say("## S7 ★ 英国銀行休日プラセボ — オークションが開かれない日にも沈むか（暦は規則導出・外部通信なし）")
say("")
def easter(y):  # Anonymous Gregorian algorithm
    a = y % 19; b = y // 100; c = y % 100; dd = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - dd - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m_ = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m_ + 114) // 31; dayy = ((h + l - 7 * m_ + 114) % 31) + 1
    return dt.date(y, month, dayy)
def first_mon(y, mo):
    dd = dt.date(y, mo, 1)
    return dd + dt.timedelta(days=(7 - dd.weekday()) % 7)
def last_mon(y, mo):
    dd = dt.date(y, mo, 31) if mo in (5, 8, 12) else dt.date(y, mo, 30)
    return dd - dt.timedelta(days=(dd.weekday()) % 7)
def subst(dd):
    out = [dd]
    while out[-1].weekday() >= 5:
        out.append(out[-1] + dt.timedelta(days=1))
    return out[-1]
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
    if y == 2012: cand += [dt.date(2012, 6, 4), dt.date(2012, 6, 5)]      # Diamond Jubilee
    if y == 2022: cand += [dt.date(2022, 6, 2), dt.date(2022, 6, 3), dt.date(2022, 9, 19)]  # Platinum Jubilee / 国葬
    if y == 2023: cand += [dt.date(2023, 5, 8)]                           # 戴冠式
    if y == 2020: cand = [c for c in cand if c != first_mon(2020, 5)] + [dt.date(2020, 5, 8)]  # VE Day 振替
    for c in cand:
        if c.weekday() <= 4: HOL.add(pd.Timestamp(c))
hol = np.isin(d.values, np.array(sorted(HOL), dtype="datetime64[ns]"))
say(f"- 規則導出した英国銀行休日（平日のみ・2010-2026）= {len(HOL)} 日 ／ うち npz に平日として存在 {int(hol.sum())} 日 ／ c50 の ok を満たす {int((hol & ok).sum())} 日 ／ ok を満たさない {int((hol & ~ok).sum())} 日")
say("")
say("| 日集合 | n | 10:25 足 bp | t | MDE 2se | 10:35 足 bp (t) | 10:25→10:45 累積 (t) |")
say("|---|---|---|---|---|---|---|")
x35 = bar(S(10, 35)); net = (Cv[:, S(10, 45)] - Cv[:, S(10, 25) - 1]) * BP
# 休日は ok 条件（14:30-15:30 の非 flat>=8）で落ちやすいので ok を課さない版も出す
rows = [("全期間 営業日 (ok)", ok & ~hol), ("全期間 英国休日 (ok 不問)", hol),
        ("全期間 英国休日 (ok)", hol & ok), ("P3+P4 営業日 (ok)", ok & ~hol & np.asarray(d >= "2015-03-20")),
        ("P3+P4 英国休日 (ok 不問)", hol & np.asarray(d >= "2015-03-20"))]
for nm, m in rows:
    a = stat(x25[m]); b2 = stat(x35[m]); c2 = stat(net[m])
    say(f"| {nm} | {a[2]} | **{a[0]:+.2f}** | **{a[1]:+.2f}** | {2*a[3]:.2f} | {b2[0]:+.2f} ({b2[1]:+.1f}) | {c2[0]:+.2f} ({c2[1]:+.1f}) |")
hm_ = stat(x25[hol])
BREAK8 = (hm_[0] <= -0.5) and (hm_[1] <= -1.5)
POWER8 = (abs(hm_[1]) < 1.5) and (2 * hm_[3] > 1.07)
say("")
say(f"- 休日の非 flat 衛生（10:20-10:40 の 4 足中 非 flat の平均本数）: 休日 {np.nanmean(4 - Fv[hol, S(10,20):S(10,40)].sum(axis=1)):.2f} ／ 営業日 {np.nanmean(4 - Fv[ok & ~hol, S(10,20):S(10,40)].sum(axis=1)):.2f}")

# ---------- 判定 ----------
say("")
say("## 判定の更新")
say("")
say("| BREAK | 内容 | 成立 |")
say("|---|---|---|")
say(f"| BREAK-8 | 英国銀行休日（オークション無し）でも 10:25 が沈む | {'**YES**' if BREAK8 else ('no（ただし検出力不足 = 決着不能）' if POWER8 else 'no')} |")
say("| BREAK-9 | 21:55（既知境界）でも R_oo≈R_cc → T4 に検出力なし | " + " / ".join(f"{k}:{'**YES**' if BREAK9.get(k) else 'no'}" for k in PER) + " |")
say(f"| BREAK-10 | P4 の 10:25→11:30 累積が -0.2 bp 以上（全戻し） | {'**YES**' if BREAK10 else 'no'}（実測 {cum1130[0]:+.2f} bp t {cum1130[1]:+.1f}） |")
say(f"| BREAK-11 | 曜日 1 つ / 月末を抜くと -0.5 bp より 0 に寄る | {'**YES**' if BREAK11 else 'no'} |")
say("")
upd = []
if BREAK8: upd.append("BREAK-8 成立 → 機構（オークション）否定 = **broken**")
if any(BREAK9.get(k) for k in ("P3 2015/03-20 - 20", "P4 2021-26H1")): upd.append("BREAK-9 成立 → T4 は人工物を見分けられない = 本体 T4 の survived は **inconclusive** へ格下げ")
if BREAK10: upd.append("BREAK-10 成立 → 一過性 = 受取り対象として **broken**")
if BREAK11: upd.append("BREAK-11 成立 → 「毎日の沈み」は暦の一部に局在（記述の限定）")
say("- " + ("／".join(upd) if upd else "BREAK-8..11 いずれも不成立 → 本体の主判定 survived は維持"))
say("")
say(f"- 実行 {time.time()-T0:.1f} s・読取りのみ・発注なし・MT5 なし・外部通信なし（休日暦は規則導出）・プロップ参照なし。seed 20261118")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
