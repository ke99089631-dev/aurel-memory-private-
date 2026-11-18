"""
[REFUTE c51 part b] 2026-11-19 — part a が開けた唯一の残差を閉じる。

part a で判明: 在 2010-20 の PRE60 +3.20 は **前半 FIRST30 −0.07 ＋ 後半 SET30 +3.26** ＝ 全部が 13:00→13:30 に居る。
SET30 は Welch t +2.55・月ブロック置換 two-sided p **0.011**（part a A4）。
c51 はこれを「約 40 セルで名目 |t|≥2 は 4 本＝期待 2 本」として棄却した。その棄却が**結論として**正しいかを決める。
（符号はロール仮説と逆・外 −1.31・近年 −2.10 なので昇格の話ではない。問いは「暦の人工物か雑音か」。）

事前固定（数字を見る前・seed 20261119・part a と同一データ/暦コードを複写）:
  B1 正しい family での FWER: 在 T−C_A を ET 48 本すべての 30 分窓で取り、max|t| と SET30 の順位。
      B1-BREAK（残差は雑音）= SET30 の |t| が 48 窓の Bonferroni 閾値（α0.05 両側 → |t|≥2.94）に届かない、
      かつ順位が上位 5%（≤2/48）に入らない。
  B2 処置定義 family: 12 か月から 6 か月の 924 分割で SET30 の t を取り、奇数月分割の順位。
      B2-BREAK = 順位が上位 5%（≤46/924）に入らない。
  B3 **BD 帯の普遍性（決め手）**: 奇数月 − 偶数月 の SET30 を BD1-4／5-9／10-14／15-19／20-23 で。
      B3-BREAK（ロール窓固有でない）= BD5-9 以外の帯でも同符号の正が出る（＝「月パリティ × 13:00-13:30」の
        一般的な暦効果であって GSCI ロール窓の性質ではない）。BD5-9 だけ正なら残差は窓固有＝要記録。
  B4 LOYO（SET30・在 11 年）: 符号・|t| の振れ。
  B5 曜日交絡: part a で 木 の μ(PRE60) が +1.21 bp と唯一大きい。SET30 を曜日 × T/C_A で分解。
      曜日組成（BD5-9 は T 20.0/C 20.2 ≒ 一様）で説明できてしまえば残差は曜日人工物。
  B6 月別分解: 奇数月 6 本・偶数月 6 本の SET30 平均（1 か月が担ぐ形か）。
  B7 コスト: T−C_A の差分セルでは対称な往復費用は差し引きで消える（part a A7 のゲート ㉛ 1×/2× が実証）。

  自己反証の予定: B1 の 48 窓は重なり無しだが日内自己相関で完全独立でない（Bonferroni は保守）。
  B3 で他帯も正なら「暦の一般効果」だが、その原因（13:00 ET 国債入札結果・月パリティに紐づく他制度）は
  本サイクルでは特定できない＝記述に留める。読取専用・書込は AUREL_RESEARCH のみ・外部通信なし。
"""
import os, math, time, datetime as dt, itertools
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c51_rollnull_b_result.md")
rng = np.random.default_rng(20261119); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c51 part b] 残差「在 SET30 +3.26（置換 p 0.011）」は暦の人工物か雑音か — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c51_rollnull_b.py)")

# ---------------- 暦（c51/part a と同一） ----------------
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d
HOL = set()
for y in range(2009, 2028):
    for h in [observed(dt.date(y, 1, 1), sat_to_fri=False), nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3),
              easter(y) - dt.timedelta(days=2), last_weekday(y, 5, 0), observed(dt.date(y, 7, 4)),
              nth_weekday(y, 9, 0, 1), nth_weekday(y, 11, 3, 4), observed(dt.date(y, 12, 25))] + \
             ([observed(dt.date(y, 6, 19))] if y >= 2022 else []):
        if h is not None: HOL.add(h)
d0 = dt.date(2009, 11, 1); d1 = dt.date(2026, 12, 31)
ALLD = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]
BDAYS = [d for d in ALLD if d.weekday() < 5 and d not in HOL]
BD = {}
for (y, m) in sorted({(d.year, d.month) for d in BDAYS}):
    bm = [d for d in BDAYS if d.year == y and d.month == m]
    for j, d in enumerate(bm): BD[d.toordinal()] = j + 1
GSCI_MONTHS = {1, 3, 5, 7, 9, 11}; GSCI_BD = (5, 9)

z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P = z["close"].astype(float)
flat1 = np.r_[True, P[1:] == P[:-1]]; flat2 = flat1 & np.r_[True, flat1[:-1]]
et = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
day = et.normalize().values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
slot = (et.hour * 12 + et.minute // 5).values
days = np.unique(day); di = {o: i for i, o in enumerate(days.tolist())}
G = np.full((len(days), 288), np.nan); F = np.ones((len(days), 288), bool)
rows_ = np.array([di[o] for o in day.tolist()]); G[rows_, slot] = np.log(P); F[rows_, slot] = flat2
say(f"- XAU npz {len(TS)} 本・日 {len(days)}（part a と同一格子）")

def win(o, s0, s1):
    i = di.get(o)
    if i is None: return np.nan
    if F[i, s0] or F[i, s1] or not (np.isfinite(G[i, s0]) and np.isfinite(G[i, s1])): return np.nan
    return (G[i, s1] - G[i, s0]) * 1e4

HW = [(h, hh) for h in range(24) for hh in (0, 30)]  # 48 本の 30 分窓
rows = []
for d in BDAYS:
    o = d.toordinal()
    if o < dt.date(2010, 1, 1).toordinal() or o > dt.date(2026, 6, 30).toordinal(): continue
    bd = BD[o]; m = d.month
    rec = dict(ord=o, year=d.year, month=m, wd=d.weekday(), bd=bd, odd=(m % 2 == 1),
               TR=(m in GSCI_MONTHS and GSCI_BD[0] <= bd <= GSCI_BD[1]),
               CA=((m not in GSCI_MONTHS) and GSCI_BD[0] <= bd <= GSCI_BD[1]),
               SET30=win(o, 13 * 12, 13 * 12 + 6))
    for h, hh in HW:
        s0 = h * 12 + (hh // 5); s1 = s0 + 6
        rec[f"W{h:02d}{hh:02d}"] = win(o, s0, min(s1, 287)) if s1 <= 287 else np.nan
    rows.append(rec)
df = pd.DataFrame(rows)
IN = df[(df.year >= 2010) & (df.year <= 2020)]
OUTW = df[(df.year >= 2021) & (df.year <= 2026)]

def welch(a, b):
    a = np.asarray(a, float); a = a[np.isfinite(a)]; b = np.asarray(b, float); b = b[np.isfinite(b)]
    if len(a) < 5 or len(b) < 5: return np.nan, np.nan, np.nan, len(a), len(b)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); d = a.mean() - b.mean()
    return d, d / se, se, len(a), len(b)

d0_, t0_, se0_, na0, nb0 = welch(IN.loc[IN.TR, "SET30"], IN.loc[IN.CA, "SET30"])
say(f"- 対象セル再確認: 在 2010-20 SET30 Δ {d0_:+.2f} bp (t {t0_:+.2f}・MDE {2*se0_:.2f}・n {na0}/{nb0})")

# ---------------- B1: 48 本の 30 分窓 family ----------------
say("\n## B1 正しい family: ET 48 本の 30 分窓で 在 T−C_A の max|t| と SET30 の順位")
ts = []
for h, hh in HW:
    d, t, se, na, nb = welch(IN.loc[IN.TR, f"W{h:02d}{hh:02d}"], IN.loc[IN.CA, f"W{h:02d}{hh:02d}"])
    if np.isfinite(t): ts.append((f"{h:02d}:{hh:02d}", d, t))
tv = np.array([x[2] for x in ts])
rank = int((np.abs(tv) > abs(t0_)).sum()) + 1
best = max(ts, key=lambda x: abs(x[2]))
say(f"- 有効窓 {len(ts)}・t sd {tv.std(ddof=1):.2f}・max|t| {best[2]:+.2f} @ ET {best[0]}（Δ {best[1]:+.2f} bp）")
say(f"- |t|≥2 の窓 {int((np.abs(tv)>=2).sum())} 本: " + " ".join(f"{n}({t:+.2f})" for n, d, t in ts if abs(t) >= 2))
bonf = 2.94
say(f"- SET30 (13:00) の順位 **{rank}/{len(ts)}**・Bonferroni(48) α0.05 両側 閾値 |t|≥{bonf:.2f} に対し |t| {abs(t0_):.2f} → 到達 {abs(t0_)>=bonf}")
say(f"- B1-BREAK（|t|<{bonf:.2f} かつ 順位 >5%）: {bool(abs(t0_) < bonf and rank > 0.05*len(ts))}")

# ---------------- B2: 924 分割 family ----------------
say("\n## B2 処置定義 family: 924 分割（6 か月選択）の中で「奇数月」の SET30 は何位か")
band = IN[IN.bd.between(*GSCI_BD)]
per_m = {m: band.loc[band.month == m, "SET30"].values for m in range(1, 13)}
per_m = {m: v[np.isfinite(v)] for m, v in per_m.items()}
recs = []
for S in itertools.combinations(range(1, 13), 6):
    A = np.concatenate([per_m[m] for m in S]); B = np.concatenate([per_m[m] for m in range(1, 13) if m not in S])
    se = math.sqrt(A.var(ddof=1) / len(A) + B.var(ddof=1) / len(B)); d = A.mean() - B.mean()
    recs.append((S, d, d / se))
tt = np.array([abs(r[2]) for r in recs]); real = [r for r in recs if set(r[0]) == GSCI_MONTHS][0]
r2 = int((tt > abs(real[2])).sum()) + 1; bst = max(recs, key=lambda r: abs(r[2]))
say(f"- 奇数月分割 Δ {real[1]:+.2f} (t {real[2]:+.2f}) の順位 **{r2}/{len(recs)}**（上位 {100*r2/len(recs):.1f}%）"
    f"・family max|t| {bst[2]:+.2f} @ 月 {sorted(bst[0])}・|t| sd {tt.std(ddof=1):.2f}")
say(f"- B2-BREAK（順位 >5%＝46 位より下）: {bool(r2 > 46)}")

# ---------------- B3: BD 帯の普遍性（決め手） ----------------
say("\n## B3 決め手: 奇数月 − 偶数月 の SET30 を BD 帯で（BD5-9 固有か・月パリティ × 13:00-13:30 の一般効果か）")
for tag, dd in [("在 2010-20", IN), ("外 2021-26H1", OUTW)]:
    parts = []; signs = []
    for lo, hi in [(1, 4), (5, 9), (10, 14), (15, 19), (20, 23)]:
        m = dd.bd.between(lo, hi)
        d, t, se, na, nb = welch(dd.loc[m & dd.odd, "SET30"], dd.loc[m & ~dd.odd, "SET30"])
        parts.append(f"BD{lo}-{hi}: {d:+.2f} (t {t:+.2f}・n {na}/{nb})"); signs.append(d)
    say(f"- {tag}: " + " | ".join(parts))
    if tag.startswith("在"):
        others = [s for i, s in enumerate(signs) if i != 1]
        pos_others = sum(1 for s in others if s > 0)
        say(f"  - BD5-9 以外の 4 帯で同符号（正）の数: **{pos_others}/4**・4 帯平均 {np.mean(others):+.2f} bp"
            f" → B3-BREAK（ロール窓固有でない）: {bool(pos_others >= 3)}")
# 全 BD（帯を問わず）奇数 − 偶数の SET30
for tag, dd in [("在 2010-20", IN), ("外 2021-26H1", OUTW)]:
    d, t, se, na, nb = welch(dd.loc[dd.odd, "SET30"], dd.loc[~dd.odd, "SET30"])
    say(f"- {tag} 全 BD 奇数月 − 偶数月 SET30: Δ {d:+.2f} (t {t:+.2f}・MDE {2*se:.2f}・n {na}/{nb})")

# ---------------- B4 LOYO ----------------
say("\n## B4 LOYO（在 SET30・1 年抜き）")
outs = []
for y in range(2010, 2021):
    e = IN[IN.year != y]; d, t, se, na, nb = welch(e.loc[e.TR, "SET30"], e.loc[e.CA, "SET30"]); outs.append((y, d, t))
say("- " + " ".join(f"-{y}:{d:+.2f}(t{t:+.2f})" for y, d, t in outs))
say(f"  - 符号が負に転じる年抜き: {[y for y,d,t in outs if d<0] or 'なし'}・|t|<2 に落ちる年抜き: {[y for y,d,t in outs if abs(t)<2] or 'なし'}")
say("- 年別 Δ(SET30): " + " ".join(f"{y}:{np.nanmean(IN.loc[(IN.year==y)&IN.TR,'SET30'])-np.nanmean(IN.loc[(IN.year==y)&IN.CA,'SET30']):+.1f}" for y in range(2010, 2021)))

# ---------------- B5 曜日 ----------------
say("\n## B5 曜日交絡（木 の μ が唯一大きい・組成は一様なので説明できないはず）")
for w in range(5):
    d, t, se, na, nb = welch(IN.loc[IN.TR & (IN.wd == w), "SET30"], IN.loc[IN.CA & (IN.wd == w), "SET30"])
    say(f"- {'月火水木金'[w]}: Δ {d:+.2f} (t {t:+.2f}・n {na}/{nb})・T 平均 {np.nanmean(IN.loc[IN.TR&(IN.wd==w),'SET30']):+.2f} vs C {np.nanmean(IN.loc[IN.CA&(IN.wd==w),'SET30']):+.2f}")
say(f"- 曜日内 Δ が正の曜日数: {sum(1 for w in range(5) if (welch(IN.loc[IN.TR&(IN.wd==w),'SET30'], IN.loc[IN.CA&(IN.wd==w),'SET30'])[0] or 0) > 0)}/5"
    "（5/5 なら曜日組成では説明できない＝曜日人工物ではない）")

# ---------------- B6 月別 ----------------
say("\n## B6 月別分解（BD5-9・在）")
say("- 奇数月: " + " ".join(f"{m}月 {np.nanmean(band.loc[band.month==m,'SET30']):+.2f}(n{int(band.loc[band.month==m,'SET30'].notna().sum())})" for m in sorted(GSCI_MONTHS)))
say("- 偶数月: " + " ".join(f"{m}月 {np.nanmean(band.loc[band.month==m,'SET30']):+.2f}(n{int(band.loc[band.month==m,'SET30'].notna().sum())})" for m in [2,4,6,8,10,12]))
mo = {m: np.nanmean(band.loc[band.month == m, "SET30"]) for m in range(1, 13)}
top = max(mo, key=lambda m: mo[m])
A = np.concatenate([per_m[m] for m in sorted(GSCI_MONTHS) if m != top]) if top in GSCI_MONTHS else None
if A is not None:
    B = np.concatenate([per_m[m] for m in [2,4,6,8,10,12]])
    se = math.sqrt(A.var(ddof=1)/len(A) + B.var(ddof=1)/len(B)); d = A.mean() - B.mean()
    say(f"- 最大の奇数月（{top}月）を落とすと: Δ {d:+.2f} (t {d/se:+.2f}・n {len(A)}/{len(B)})")

say("\n## B7 コスト倍がこのセルに無力な理由（数式・part a A7 が実証）")
say("- T−C_A は同一銘柄・同一時刻窓の**差分**なので、片道/往復の対称な費用 c は Δ = (μ_T − c) − (μ_C − c) = μ_T − μ_C で消える。")
say("- ゲート ㉛ の 1×/2× コスト（part a A7）: 在 Δμ +0.024 → +0.024（不変）・外 −0.035 → −0.034＝実証。")
say("- ∴ 本サイクルに対する有効な『コスト』攻撃は差分セルでなく**受取可能性（net 戦略）側にしか存在しない**が、c51 は戦略を提案していない。")

say(f"\n（経過 {time.time()-T0:.1f}s・seed 20261119・外部通信なし・MT5 なし・読取専用）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
