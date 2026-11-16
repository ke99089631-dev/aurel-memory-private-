# -*- coding: utf-8 -*-
"""
[REFUTE c43 補足 b / 2026-11-17] 本体 refute_c43_goldfri.py の 10 攻撃のうち BREAK-E（年クラスタ）と BREAK-F（多重検定）だけが当たり、
8 つは当たらなかった。本体の結果が示した 2 つの顔を、**機構の問いとして**詰める（以下は全部 事後・supplementary と明記する）。

本体で見えた顔:
  (α) 年別 S_cont が単調に増える: 2021 −0.9 / 2022 +15.0 / 2023 +7.2 / 2024 +20.8 / 2025 +39.1 / 2026 +66.2（単年で t≥2 は 1 つも無い・最大 1.88）
      → 「bp 建ての S が金のボラ拡大にスケールしているだけ」かもしれない（＝レジームでなく単位の問題）。
  (β) 寄与上位 5 日のうち 3 日は |LAST| ≤ 7 bp（2026-06-12 LAST +5 → NEXT +338／2025-05-09 LAST −2 → NEXT −268／2024-11-22 LAST −7 → NEXT −241）
      符号一致率は 54.8%（二項 p 0.188）しかないのに S は +20.8 ＝ **符号戦略は 2 bp の向きと 50 bp の向きを同じ重みで扱い、
      巨大な NEXT 側が平均を作っている**。機構（金曜午後の情報・フローが週末に続く）なら |LAST| に用量反応があるはず。
      本体 R12 は 下位 1/3 +10.5 (t 1.16)／中位 +33.1 (t 2.98)／上位 1/3 +18.9 (t 1.38) ＝単調でない。
  (γ) 本体 R11: 非共有 LAST'(15:30→15:55) で S t 1.60・LAST5(15:55→16:00) で t 1.76 ＝両方 半分ずつ。

=== 追加攻撃（S1-S5・事後だが実行前にここに固定）===
S1 ボラ正規化: NEXT・LAST を**直前 20 金曜の sd**（look-ahead なし・t 時点で既知）で割り、無単位の S_z・β_z を出す。
   年別・era 別。**(α) が正しければ S_z の年別は平坦になり、era の t は落ちる。**
S2 用量反応: |LAST| 閾値（≥0/5/10/15/20 bp）別の S・β・符号一致率。|LAST| 加重符号戦略（= β の符号版）。
   **機構があれば閾値を上げるほど S（と符号一致率）が上がる。下がる／非単調なら (β) が正しい。**
S3 窓分解（最重要・機構の所在）: 金 16:00 → 月 10:00 を実際の金の取引時間で 3 つに割る。
   A = 金 16:00 → 金 16:55（同じ金曜セッションの残り 1 時間・まだ取引中）
   B = 金 16:55 → 日 18:05（真の週末ギャップ・閉場）
   C = 日 18:05 → 月 10:00（月曜アジア・欧州・NY 前半）
   併記 GAP = 金 16:00 → 月 09:30／FIRST = 月 09:30 → 10:00。
   **継続が A に集中していれば「週末の持ち越し効果」ではなく金曜引け際の同セッション内継続（＝16:00 の bid が遅れている疑い）。**
S4 遅れ気配（stale quote）診断: 金曜 15:30-16:00 と 16:00-17:00 の flat 足（r==0）本数を数え、
   flat が多い（＝気配が動いていない＝遅れている）金曜で継続が強いかを見る。
   **機構が「16:00 の bid が真の値に遅れていて残りが NEXT に漏れる」なら flat 多 の金曜で S が大きくなる。**
S5 独立計器: data/macro/XAU_daily_er.csv は同じ npz の派生（独立でない）＝独立計器テストは**実施不能**（needs data: 別ソースの金 1 分/5 分・
   または先物 GC の引け）。㊹ に従い「陽性対照の無い独立計器テストは void」として走らせない。
判定への使い方: S1-S4 は本体の pre-registered BREAK 判定を**上書きしない**（事後だから）。
   結論の読み方（どちらが正しいか）を決めるためだけに使い、findings には「事後」と明記する。
seed 20261117。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd
from scipy import stats as st

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c43_goldfri_b.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
def say(s=""):
    print(s, flush=True); L.append(s)
say(f"# [REFUTE c43 補足 b] 機構の所在（S1 ボラ正規化・S2 用量反応・S3 窓分解・S4 遅れ気配）— 全部 事後 — {time.strftime('%Y-%m-%d %H:%M')}")
say("")

zz = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
lg = np.log

def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31; da = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, mo, da)
def third_friday(y, m):
    d = dt.date(y, m, 1); off = (4 - d.weekday()) % 7; return d + dt.timedelta(days=off + 14)
OPEX = set()
for y in range(2010, 2027):
    gf = easter(y) - dt.timedelta(days=2)
    for m in range(1, 13):
        f3 = third_friday(y, m)
        if f3 != gf: OPEX.add(f3)

dates = pd.date_range("2010-01-01", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy(); wd = dates.weekday.to_numpy(); dser = np.array(dates.date)
E = np.array([d in OPEX for d in dser])
P = lambda h, m, off=0: price_at(epoch_et(dates, h, m, off))
p0930, p1530, p1555, p1600, p1655 = P(9, 30), P(15, 30), P(15, 55), P(16, 0), P(16, 55)
LAST = (lg(p1600) - lg(p1530)) * 1e4
CASH = (lg(p1530) - lg(p0930)) * 1e4
nx1000 = np.full(N, np.nan); nx0930 = np.full(N, np.nan); nxoff = np.full(N, np.nan)
for off in range(1, 6):
    a, b = P(9, 30, off), P(10, 0, off)
    ok = np.isnan(nx1000) & np.isfinite(a) & np.isfinite(b) & (a != b)
    nx1000[ok] = b[ok]; nx0930[ok] = a[ok]; nxoff[ok] = off
NEXT = (lg(nx1000) - lg(p1600)) * 1e4
valid = np.isfinite(LAST) & np.isfinite(NEXT) & np.isfinite(CASH) & (LAST != 0) & (CASH != 0)
FRI = valid & (wd == 4) & ~E

def hc1(y, X):
    n, k = X.shape; XtX_i = np.linalg.inv(X.T @ X); b = XtX_i @ X.T @ y; e = y - X @ b
    V = XtX_i @ (X.T * (e ** 2)) @ X @ XtX_i * n / (n - k); return b, np.sqrt(np.diag(V))
def beta(x, y):
    b, se = hc1(y, np.column_stack([np.ones(len(x)), x])); return b[1], b[1] / se[1]
def tm(v):
    v = np.asarray(v, float); n = len(v)
    if n < 3: return np.nan, np.nan, n
    return v.mean(), v.mean() / (v.std(ddof=1) / math.sqrt(n)), n
def binom_p(k, n):
    from math import comb
    lo = sum(comb(n, i) * 0.5 ** n for i in range(0, k + 1)); hi = sum(comb(n, i) * 0.5 ** n for i in range(k, n + 1))
    return min(1.0, 2 * min(lo, hi))

ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
idx = np.where(FRI & (yr >= 2012))[0]
x_all, y_all, yr_all, d_all = LAST[idx], NEXT[idx], yr[idx], dser[idx]
OUTm = (yr_all >= 2021)

# ============================ S1 ボラ正規化 ============================
say("## S1 ボラ正規化（直前 20 金曜の sd・look-ahead なし）")
say("")
nA = len(x_all)
sdN = np.full(nA, np.nan); sdL = np.full(nA, np.nan)
for i in range(nA):
    if i >= 20:
        sdN[i] = y_all[i - 20:i].std(ddof=1); sdL[i] = x_all[i - 20:i].std(ddof=1)
ok = np.isfinite(sdN) & (sdN > 0) & np.isfinite(sdL) & (sdL > 0)
zN = np.where(ok, y_all / sdN, np.nan); zL = np.where(ok, x_all / sdL, np.nan)
say(f"- 正規化に使える金曜 {int(ok.sum())}/{nA}（最初の 20 本は NaN）")
for nm, y0, y1 in ERAS:
    m = ok & (yr_all >= y0) & (yr_all <= y1)
    Sz = np.sign(zL[m]) * zN[m]; mz, tz, nz = tm(Sz)
    bz, tbz = beta(zL[m], zN[m])
    mraw, traw, _ = tm(np.sign(x_all[m]) * y_all[m])
    say(f"- {nm}（n {nz}）: **S_z {mz:+.3f} σ (t {tz:+.2f})**・β_z {bz:+.3f} (t {tbz:+.2f})｜生 S {mraw:+.1f} bp (t {traw:+.2f})")
say("- 年別（外）: " + "；".join(
    f"{y}: n {int((ok&(yr_all==y)).sum())} S_z {tm(np.sign(zL[ok&(yr_all==y)])*zN[ok&(yr_all==y)])[0]:+.3f}σ "
    f"(t {tm(np.sign(zL[ok&(yr_all==y)])*zN[ok&(yr_all==y)])[1]:+.2f})／生 {tm(np.sign(x_all[ok&(yr_all==y)])*y_all[ok&(yr_all==y)])[0]:+.1f} bp"
    for y in range(2021, 2027) if (ok & (yr_all == y)).sum() >= 10))
say("- 参考: NEXT の sd（年別・金曜）: " + " ".join(f"{y}:{y_all[yr_all==y].std(ddof=1):.0f}" for y in range(2021, 2027)))

# ============================ S2 用量反応 ============================
say("")
say("## S2 用量反応（|LAST| 閾値・機構があれば単調増加）")
say("")
mo = OUTm
xo, yo = x_all[mo], y_all[mo]
for th in (0, 5, 10, 15, 20, 25):
    sel = np.abs(xo) >= th
    if sel.sum() < 20: continue
    S = np.sign(xo[sel]) * yo[sel]; m_, t_, n_ = tm(S)
    agree = int((np.sign(xo[sel]) == np.sign(yo[sel])).sum())
    b_, tb_ = beta(xo[sel], yo[sel])
    say(f"- |LAST| ≥ {th:2d} bp（n {n_:3d}）: S_cont {m_:+6.1f} (t {t_:+.2f})・符号一致 {agree}/{n_} = {agree/n_*100:.1f}% "
        f"(二項 p {binom_p(agree,n_):.3f})・β {b_:+.2f} (t {tb_:+.2f})")
for th in (5, 10, 15):
    sel = np.abs(xo) < th
    if sel.sum() < 20: continue
    S = np.sign(xo[sel]) * yo[sel]; m_, t_, n_ = tm(S)
    agree = int((np.sign(xo[sel]) == np.sign(yo[sel])).sum())
    say(f"- （逆）|LAST| < {th:2d} bp（n {n_:3d}）: S_cont {m_:+6.1f} (t {t_:+.2f})・符号一致 {agree/n_*100:.1f}% (二項 p {binom_p(agree,n_):.3f})")
# |LAST| 加重
wS = (xo * yo) / np.abs(xo).mean()
m_, t_, n_ = tm(wS); say(f"- |LAST| 加重（x·y / mean|x|・n {n_}）: {m_:+.1f} (t {t_:+.2f})")
# 五分位
q = np.quantile(np.abs(xo), [0.2, 0.4, 0.6, 0.8])
edges = [-np.inf] + list(q) + [np.inf]
say("- |LAST| 五分位: " + "／".join(
    f"Q{i+1}(≤{edges[i+1]:.0f}bp) n {int(((np.abs(xo)>edges[i])&(np.abs(xo)<=edges[i+1])).sum())} "
    f"S {tm(np.sign(xo[(np.abs(xo)>edges[i])&(np.abs(xo)<=edges[i+1])])*yo[(np.abs(xo)>edges[i])&(np.abs(xo)<=edges[i+1])])[0]:+.1f} "
    f"(t {tm(np.sign(xo[(np.abs(xo)>edges[i])&(np.abs(xo)<=edges[i+1])])*yo[(np.abs(xo)>edges[i])&(np.abs(xo)<=edges[i+1])])[1]:+.2f})"
    for i in range(5)))

# ============================ S3 窓分解 ============================
say("")
say("## S3 窓分解（金 16:00 → 月 10:00 を金の実取引時間で割る・機構の所在）")
say("")
# 日曜 18:05 ET（=offset 2 日 18:05）・月 10:00（offset 3）
pSun = P(18, 5, 2); pSun0 = P(18, 0, 2)
pMon0930 = P(9, 30, 3); pMon1000 = P(10, 0, 3)
A = (lg(p1655) - lg(p1600)) * 1e4                      # 金 16:00 → 16:55（同セッション残り）
B = (lg(pSun) - lg(p1655)) * 1e4                       # 金 16:55 → 日 18:05（真の週末ギャップ）
C = (lg(pMon1000) - lg(pSun)) * 1e4                    # 日 18:05 → 月 10:00
GAP = (lg(nx0930) - lg(p1600)) * 1e4
FIRST = (lg(nx1000) - lg(nx0930)) * 1e4
avail = FRI & (yr >= 2021) & np.isfinite(A) & np.isfinite(B) & np.isfinite(C) & (nxoff == 3)
say(f"- 3 分割が全部取れる外の対照金曜 n {int(avail.sum())}（NEXT が月曜＝暦差 3 日のみ・日曜 18:00 足の有無で落ちる本あり）")
xs = LAST[avail]; s = np.sign(xs)
tot = NEXT[avail]
parts = [("A 金 16:00→16:55（同セッション）", A[avail]), ("B 金 16:55→日 18:05（週末ギャップ）", B[avail]),
         ("C 日 18:05→月 10:00", C[avail]), ("= 合計 A+B+C", (A + B + C)[avail]), ("（照合）NEXT 16:00→月 10:00", tot)]
for lab, v in parts:
    Sv = s * v; m_, t_, n_ = tm(Sv); b_, tb_ = beta(xs, v)
    say(f"- {lab}: sd {v.std(ddof=1):6.1f} bp・S_cont {m_:+6.1f} (t {t_:+.2f})・β {b_:+.3f} (t {tb_:+.2f})・"
        f"S の寄与率 {m_/tm(s*tot)[0]*100:+.0f}%")
for lab, v in (("GAP 16:00→月 09:30", GAP[avail]), ("FIRST 月 09:30→10:00", FIRST[avail])):
    Sv = s * v; m_, t_, n_ = tm(Sv); b_, tb_ = beta(xs, v)
    say(f"- {lab}: sd {v.std(ddof=1):6.1f} bp・S_cont {m_:+6.1f} (t {t_:+.2f})・β {b_:+.3f} (t {tb_:+.2f})")
# A の中身をさらに割る: 16:00→16:30, 16:30→16:55
p1630 = P(16, 30)
A1 = (lg(p1630) - lg(p1600)) * 1e4; A2 = (lg(p1655) - lg(p1630)) * 1e4
for lab, v in (("A1 16:00→16:30", A1[avail]), ("A2 16:30→16:55", A2[avail])):
    Sv = s * v; m_, t_, n_ = tm(Sv); b_, tb_ = beta(xs, v)
    say(f"  - {lab}: sd {v.std(ddof=1):5.1f}・S_cont {m_:+6.1f} (t {t_:+.2f})・β {b_:+.3f} (t {tb_:+.2f})")
# 在 era でも同じ分解（対照）
av_in = FRI & (yr >= 2012) & (yr <= 2020) & np.isfinite(A) & np.isfinite(B) & np.isfinite(C) & (nxoff == 3)
xi = LAST[av_in]; si = np.sign(xi)
say(f"- 在 2012-20 の同分解（n {int(av_in.sum())}・対照）: " + "／".join(
    f"{lab} S {tm(si*v)[0]:+.1f} (t {tm(si*v)[1]:+.2f})" for lab, v in
    (("A", A[av_in]), ("B", B[av_in]), ("C", C[av_in]))))

# ============================ S4 遅れ気配 ============================
say("")
say("## S4 遅れ気配（stale quote）診断")
say("")
# 金曜 15:30-16:00（6 足）と 16:00-17:00（12 足）の flat 本数
def flat_count(h0, m0, h1, m1):
    out = np.full(N, np.nan)
    T0_ = epoch_et(dates, h0, m0); T1_ = epoch_et(dates, h1, m1)
    for i in range(N):
        if not (np.isfinite(T0_[i]) and np.isfinite(T1_[i])): continue
        a = np.searchsorted(ts, int(T0_[i]) - 300); b = np.searchsorted(ts, int(T1_[i]) - 300)
        if b <= a: continue
        seg = cl[a:b + 1]
        if len(seg) < 2: continue
        out[i] = float((np.diff(seg) == 0).mean())
    return out
fl_late = flat_count(15, 30, 16, 0)
fl_post = flat_count(16, 0, 17, 0)
mm = FRI & (yr >= 2021) & np.isfinite(fl_late) & np.isfinite(fl_post)
xq, yq = LAST[mm], NEXT[mm]; sq = np.sign(xq); Sq = sq * yq
say(f"- 外・対照金曜 n {int(mm.sum())}・flat 比率 15:30-16:00 中央値 {np.median(fl_late[mm]):.2f}・16:00-17:00 中央値 {np.median(fl_post[mm]):.2f}")
for lab, f in (("15:30-16:00 の flat", fl_late[mm]), ("16:00-17:00 の flat", fl_post[mm])):
    med = np.median(f)
    hi = f > med; lo = ~hi
    m1, t1, n1 = tm(Sq[hi]); m0, t0, n0 = tm(Sq[lo])
    sed = math.sqrt(Sq[hi].var(ddof=1) / n1 + Sq[lo].var(ddof=1) / n0)
    say(f"- {lab} 多（n {n1}）S {m1:+.1f} (t {t1:+.2f}) vs 少（n {n0}）S {m0:+.1f} (t {t0:+.2f})・差 {m1-m0:+.1f} (Welch t {(m1-m0)/sed:+.2f})")
# 16:00 の bid が 16:55 と同値（＝引け後 1 時間動かない＝完全 stale）な金曜
same = np.isfinite(p1655) & np.isfinite(p1600) & (p1655 == p1600)
sel = mm & same
say(f"- 16:00 と 16:55 の bid が完全同値な外の金曜 {int(sel.sum())} 本（完全 stale・全体の {sel.sum()/mm.sum()*100:.0f}%）")
if sel.sum() >= 15:
    m_, t_, n_ = tm(np.sign(LAST[sel]) * NEXT[sel]); say(f"  その本だけ: S_cont {m_:+.1f} (t {t_:+.2f})")
    rest = mm & ~same; m2, t2, n2 = tm(np.sign(LAST[rest]) * NEXT[rest])
    say(f"  それ以外 (n {n2}): S_cont {m2:+.1f} (t {t2:+.2f})")

say("")
say("## S5 独立計器")
say("- data/macro/XAU_daily_er.csv は同じ XAU_m5 npz の派生＝独立計器ではない。㊹（独立計器テストには陽性対照が必要・"
    "対照が取れないなら void）に従い実施しない。**needs data: 別ソースの金 5 分足（または COMEX GC の 16:00/17:00 ET 気配）・優先度 中**。")
say("")
say(f"- 実行 {time.time()-T0:.1f} s・seed {SEED}・XAU bid M5 npz のみ・事後（supplementary）・scan 無し・MT5 無し・外部通信無し")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
