"""
[cycle51 研究レーン] 2026-11-19 — 【探索・資金移動／先物ロール（§8「先物ロール/FND・指数ロール」行＝要取得のうち、スポットで検証できる部分）】
商品指数（S&P GSCI・BCOM）の機械的ロールは、金スポット（XAUUSD bid M5）に価格圧力の足跡を残すか。

機構（文献・記憶・外部通信は暦の確認 1 回のみ）:
  - S&P GSCI は毎月 第 5〜第 9 営業日に 1/5 ずつ期近 → 次限月へロール（売り期近・買い期先）。BCOM は第 6〜第 10 営業日。
    金 GC の指数限月は偶数月（G/J/M/Q/V/Z）→ ロールが起きる月は**奇数月**（1・3・5・7・9・11）。偶数月の同じ営業日位置にはロールが無い
    ＝暦位置を揃えた自然対照（月パリティ対照）。
  - Mou 2010 "Limits to Arbitrage and Commodity Index Investment: Front-Running the Goldman Roll": ロール窓で期近−期先スプレッドに
    価格圧力・前倒し（front-running）で窓の前にずれる。エネルギー/農産物で大・金は保管が安く裁定が厚いので最小と報告。
  - 指数のロールは COMEX 清算値（13:30 ET・TAS 注文）で執行される → 圧力はスポットでは**清算直前 1 時間（12:30→13:30 ET）**に集中し、
    直後（13:30→14:30）に戻す（流動性供給者の在庫解消）はず。日次（sd 100 bp）では MDE 16 bp/日で見えない → 1 時間窓（sd ≈25 bp）で測る。
  - 大きさの予算（記憶・桁のみ）: 指数連動 AUM 1500〜2500 億 USD × 金ウェイト（GSCI 4〜7%・BCOM 15〜17%）→ 1 ロール ≈ 200〜350 億 USD・
    5 日に分散 ≈ 40〜70 億/日 vs COMEX GC 日中名目 600〜1200 億 ＝ 出来高の 5〜10%。期近−期先の裁定が吸収すればスポット ≈0。

事前固定（数字を見る前に確定・本 docstring が正本）:
  データ: data/macro/XAU_m5_close.npz（bid・完全格子・前値埋め・flat 除外 ⑪）・US500_m5_close.npz（対照市場・ロール無し ㉝）。
  営業日 = 月〜金 − CME 休日（c30/c31 の HOL）。月内営業日番号 BD = 1,2,...（その月の何番目の営業日か）。
  処置 T = {奇数月 ∧ BD∈[5,9]}（GSCI 窓）。対照 C_A = {偶数月 ∧ BD∈[5,9]}（同じ暦位置・ロール無し）。
  窓（ET 現地・格子 close）: PRE60 = ln C(13:30) − ln C(12:30)【主】／SET30 = 13:00→13:30／POST60 = 13:30→14:30／DAY = セッション日次（c31 定義）。
       窓の端点足が flat（直前 2 本とも同値）の日は除外。早引け（13:00 ET）日は POST が flat で落ちる。
  窓期: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・記述）。
  H_ROLL（主・片側 負）: Δ_PRE = mean PRE60(T) − mean PRE60(C_A)（bp・Welch t）。PASS = 在 Δ<0 ∧ t≤−2 ∧ 外 Δ<0 ∧ t≤−1.5。
  H_REV（副・Bonferroni(2)）: Δ_POST = mean POST60(T) − mean POST60(C_A) > 0。PASS = 在 t≥2.24 ∧ 外 t≥1.5。
  プラセボ（family・記述）: ①同じ T−C_A 対比を ET 他の 1 時間窓 23 本（h→h+1・h=0..23・13 を除く）で取り max|t| を印字（時刻 family）。
       ②BD 位置プラセボ: 奇数月 BD∈[10,14] − 偶数月 BD∈[10,14]・BD∈[1,4]（front-running の受け皿・記述）。
       ③BCOM 窓（奇数月から 9 月を除く・BD∈[6,10]）を副セルとして併記（GSCI と重なる・判定には使わない）。
       ④US500 同窓（ロール無し・㉝ 本拠の負の対照）: Δ_PRE(US500) は 0 のはず。
  ボラ（記述）: PRE60 の |r| 中央値比 T/C_A（ロール取引の執行はボラを上げるはず・陽性対照に代わる「ロールが居る」の確認）。
  陽性対照: 在 T の PRE60 に −5 bp を注入して t を印字（検出力）。MDE = 2·se。
  ゲート ㉛（本番への接続・記述）: scan 19404 本のうち建玉が T 日・ET 09:00–13:30 の本の R*（SL/TP は R+ft・TIME は R−ft）− C_A 日 同時刻の本。
       在 |Δμ| <0.048R なら外は走らせない。
  最重大反証（事前）: (i) ロール暦（限月・営業日窓）は記憶＋公開 methodology の確認 1 回に依る＝暦が 1 日ずれると T は希釈する（保守側）。
       (ii) 偶数月の同 BD は「ロール無し」だが COMEX 金オプション満期（c30・第 4 最終営業日）や FND（月末）は偶数月に落ちる＝月パリティ
            は他の制度日付と同時に動く → BD5–9 は月央なので FND/満期とは重ならない（確認: c30 の満期日 BD 分布を印字）。
       (iii) 13:30 ET 窓は NFP でなく、FOMC（14:00）とも重ならないが、13:00 ET の米国債入札（月央・奇数月偏り無し）が落ちる→時刻 family で見る。
       (iv) bid のみ・1 社 CFD・清算値そのものは無い（スポットは清算の代理）。
       (v) 「スポットは期近−期先スプレッドの圧力を受けない」なら null は機構の否定ではなく「スポット経路の否定」でしかない
            → 残りは GC 当限 M5【要取得】。
  seed 20261119。多年 scan 無し・M5 読込なし（npz 2 本＋scan json 1 本）・MT5 無し。
"""
import os, sys, json, math, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c51_index_roll_footprint_result.md")
rng = np.random.default_rng(20261119); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle51] 商品指数ロール窓（GSCI BD5–9・奇数月）の金スポット足跡 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c51_index_roll_footprint.py)")

# ---------------- 暦（c30/c31 と同一） ----------------
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
BD = {}; NBD = {}
for (y, m) in sorted({(d.year, d.month) for d in BDAYS}):
    bm = [d for d in BDAYS if d.year == y and d.month == m]
    for j, d in enumerate(bm): BD[d.toordinal()] = j + 1
    NBD[(y, m)] = len(bm)
# c30 の金オプション満期（第 4 最終営業日）の BD 位置（反証 (ii) の確認用）
OPX_BD = []
for (y, m), n in NBD.items():
    bm = [d for d in BDAYS if d.year == y and d.month == m]
    if len(bm) >= 4 and 2010 <= y <= 2026: OPX_BD.append(BD[bm[-4].toordinal()])
GSCI_MONTHS = {1, 3, 5, 7, 9, 11}; GSCI_BD = (5, 9)
BCOM_MONTHS = {1, 3, 5, 7, 11}; BCOM_BD = (6, 10)

# ---------------- 価格 → 日 × ET 時刻 格子 ----------------
def load_grid(sym):
    z = np.load(os.path.join(DATA, "macro", f"{sym}_m5_close.npz")); TS = z["ts"].astype(np.int64); P = z["close"].astype(float)
    say(f"- {sym} npz {len(TS)} 本 {dt.datetime.fromtimestamp(int(TS[0]), dt.timezone.utc):%Y-%m-%d} 〜 {dt.datetime.fromtimestamp(int(TS[-1]), dt.timezone.utc):%Y-%m-%d} UTC（⑩）")
    flat1 = np.r_[True, P[1:] == P[:-1]]; flat2 = flat1 & np.r_[True, flat1[:-1]]  # 直前 2 本とも同値
    et = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
    day = et.normalize().values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
    slot = (et.hour * 12 + et.minute // 5).values  # 0..287
    days = np.unique(day); di = {o: i for i, o in enumerate(days.tolist())}
    G = np.full((len(days), 288), np.nan); F = np.ones((len(days), 288), bool)
    rows = np.array([di[o] for o in day.tolist()])
    G[rows, slot] = np.log(P); F[rows, slot] = flat2
    # セッション日次（c31 定義: (ET+6h) 暦日の最終取引足 close）
    sess = ((et + pd.Timedelta(hours=6)).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal())
    keep = ~flat1; so = sess[keep]; pc = P[keep]
    u, li = np.unique(so[::-1], return_index=True); li = len(so) - 1 - li
    cbd = dict(zip(u.tolist(), pc[li].tolist()))
    say(f"  flat 足 {flat1.mean()*100:.1f}%・日 {len(days)}・曜日別 flat: " + "/".join(f"{'月火水木金土日'[w]}{flat1[(pd.DatetimeIndex(et).weekday==w)].mean()*100:.0f}" for w in range(7)))
    return days, di, G, F, cbd

def win(G, F, di, o, s0, s1):
    """ln C(s1) − ln C(s0)（bp）・端点が flat2 なら nan"""
    i = di.get(o)
    if i is None: return np.nan
    if F[i, s0] or F[i, s1] or not (np.isfinite(G[i, s0]) and np.isfinite(G[i, s1])): return np.nan
    return (G[i, s1] - G[i, s0]) * 1e4

def build(sym):
    days, di, G, F, cbd = load_grid(sym)
    rows = []; prev = None
    for d in BDAYS:
        o = d.toordinal()
        if o < dt.date(2010, 1, 1).toordinal() or o > dt.date(2026, 6, 30).toordinal(): continue
        bd = BD[o]; m = d.month
        rec = dict(ord=o, year=d.year, month=m, wd=d.weekday(), bd=bd, odd=(m % 2 == 1),
                   TR=(m in GSCI_MONTHS and GSCI_BD[0] <= bd <= GSCI_BD[1]), CA=((m not in GSCI_MONTHS) and GSCI_BD[0] <= bd <= GSCI_BD[1]),
                   TB=(m in BCOM_MONTHS and BCOM_BD[0] <= bd <= BCOM_BD[1]), CB=((m not in BCOM_MONTHS) and BCOM_BD[0] <= bd <= BCOM_BD[1]),
                   PRE60=win(G, F, di, o, 12 * 12 + 6, 13 * 12 + 6), SET30=win(G, F, di, o, 13 * 12, 13 * 12 + 6),
                   POST60=win(G, F, di, o, 13 * 12 + 6, 14 * 12 + 6))
        for h in range(24): rec[f"H{h:02d}"] = win(G, F, di, o, h * 12, min(h * 12 + 12, 287))
        rec["DAY"] = (math.log(cbd[o] / cbd[prev]) * 1e4) if (prev is not None and o in cbd and prev in cbd) else np.nan
        if o in cbd: prev = o
        rows.append(rec)
    return pd.DataFrame(rows)

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def welch(a, b):
    a = np.asarray(a, float); a = a[np.isfinite(a)]; b = np.asarray(b, float); b = b[np.isfinite(b)]
    if len(a) < 5 or len(b) < 5: return np.nan, np.nan, np.nan, len(a), len(b)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); d = a.mean() - b.mean()
    return d, d / se, se, len(a), len(b)

say("\n## 暦（数字を見る前の確認）")
say(f"- 営業日 2010-01〜2026-06: {sum(1 for d in BDAYS if 2010 <= d.year <= 2026 and d <= dt.date(2026,6,30))}・月の営業日数 中央値 {int(np.median(list(NBD.values())))}")
say(f"- GSCI 窓 T = 奇数月 BD{GSCI_BD[0]}–{GSCI_BD[1]}／C_A = 偶数月 同 BD。BCOM 窓 = 月 {sorted(BCOM_MONTHS)} BD{BCOM_BD[0]}–{BCOM_BD[1]}")
say(f"- 反証 (ii): c30 金オプション満期（第 4 最終営業日）の BD 位置 {min(OPX_BD)}〜{max(OPX_BD)}（中央値 {int(np.median(OPX_BD))}）＝ BD5–9 と重ならない: {min(OPX_BD) > 9}")

df = build("XAU")
for c in ["TR", "CA", "TB", "CB"]: say(f"- {c} 日数 {int(df[c].sum())}（PRE60 有効 {int(df.loc[df[c], 'PRE60'].notna().sum())}）")
say("- 曜日組成 T vs C_A（月〜金 %）: " + "/".join(f"{(df[df.TR].wd==w).mean()*100:.0f}" for w in range(5)) + " vs " + "/".join(f"{(df[df.CA].wd==w).mean()*100:.0f}" for w in range(5)))
say(f"- PRE60 sd {df.PRE60.std():.1f} bp・|PRE60| 中央値 {df.PRE60.abs().median():.1f}・POST60 sd {df.POST60.std():.1f}・DAY sd {df.DAY.std():.0f}（有効 {df.PRE60.notna().sum()}/{len(df)}）")

RES = {}
def cell(d_, col, tm, cm, label, key):
    d, t, se, na, nb = welch(d_.loc[d_[tm], col], d_.loc[d_[cm], col])
    say(f"  - {label}: {col} T n {na} 平均 {np.nanmean(d_.loc[d_[tm], col]):+.2f} vs C n {nb} {np.nanmean(d_.loc[d_[cm], col]):+.2f} bp → Δ {d:+.2f}（Welch t {t:+.2f}・se {se:.2f}・MDE {2*se:.2f}）")
    RES[key] = dict(d=d, t=t, se=se, na=na, nb=nb); return RES[key]

say("\n## H_ROLL（主）PRE60 12:30→13:30 ET・T − C_A（GSCI）")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)]; cell(d_, "PRE60", "TR", "CA", wn, ("PRE60", wn))
say("## H_REV（副）POST60 13:30→14:30 ET・T − C_A")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)]; cell(d_, "POST60", "TR", "CA", wn, ("POST60", wn))
say("## 副: SET30 13:00→13:30・DAY（セッション日次）・BCOM 窓（TB − CB）")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)]
    cell(d_, "SET30", "TR", "CA", wn, ("SET30", wn)); cell(d_, "DAY", "TR", "CA", wn, ("DAY", wn)); cell(d_, "PRE60", "TB", "CB", wn + "（BCOM）", ("PRE60B", wn))

say("\n## プラセボ ①: 時刻 family（T − C_A を ET 各 1 時間窓で・max|t|）")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)]; ts = []
    for h in range(24):
        d, t, se, na, nb = welch(d_.loc[d_.TR, f"H{h:02d}"], d_.loc[d_.CA, f"H{h:02d}"]); ts.append((h, d, t))
    tv = np.array([x[2] for x in ts if np.isfinite(x[2])]); hm = max(ts, key=lambda x: abs(x[2]) if np.isfinite(x[2]) else -1)
    say(f"  - {wn}: 24 窓 t sd {tv.std(ddof=1):.2f}・max|t| {hm[2]:+.2f} @ ET {hm[0]:02d} 時（Δ {hm[1]:+.2f} bp）・|t|≥2 の窓 {int((np.abs(tv)>=2).sum())}・12:30-13:30 主セル t {RES[('PRE60', wn)]['t']:+.2f} の順位 {int((np.abs(tv) > abs(RES[('PRE60', wn)]['t'])).sum()) + 1}/24")
    say("    時刻別 Δ(bp): " + " ".join(f"{h:02d}:{d:+.1f}" for h, d, t in ts if np.isfinite(d)))

say("\n## プラセボ ②: BD 位置（奇数月 − 偶数月・同 BD 帯・PRE60）＝ front-running／窓外の受け皿")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)]; parts = []
    for lo, hi in [(1, 4), (5, 9), (10, 14), (15, 19), (20, 23)]:
        m = d_.bd.between(lo, hi)
        d, t, se, na, nb = welch(d_.loc[m & d_.odd, "PRE60"], d_.loc[m & ~d_.odd, "PRE60"]); parts.append(f"BD{lo}-{hi}: {d:+.2f} (t {t:+.2f}・n {na}/{nb})")
    say(f"  - {wn}: " + " | ".join(parts))

say("\n## ボラ（記述）: PRE60 の |r| 中央値比 T／C_A と DAY |r| 比（ロールの執行が居るか）")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)]
    r1 = d_.loc[d_.TR, "PRE60"].abs().median() / d_.loc[d_.CA, "PRE60"].abs().median(); r2 = d_.loc[d_.TR, "DAY"].abs().median() / d_.loc[d_.CA, "DAY"].abs().median()
    # 奇数月 vs 偶数月 全 BD の比（月パリティ自体のボラ差）
    r3 = d_.loc[d_.odd, "PRE60"].abs().median() / d_.loc[~d_.odd, "PRE60"].abs().median()
    say(f"  - {wn}: |PRE60| 比 {r1:.3f}・|DAY| 比 {r2:.3f}・奇数/偶数月 全 BD |PRE60| 比 {r3:.3f}")

say("\n## 対照市場 ④: US500 同窓（ロール無し・㉝）")
dus = build("US500")
for wn, (y0, y1) in WIN.items():
    d_ = dus[(dus.year >= y0) & (dus.year <= y1)]
    if wn.startswith("在"): d_ = d_[d_.year >= 2012]
    cell(d_, "PRE60", "TR", "CA", wn + "（US500）", ("PRE60_US", wn)); cell(d_, "POST60", "TR", "CA", wn + "（US500）", ("POST60_US", wn))

say("\n## 年別 Δ_PRE60（T − C_A・bp・記述）")
say("  " + " ".join(f"{y}:{np.nanmean(df.loc[(df.year==y)&df.TR,'PRE60'])-np.nanmean(df.loc[(df.year==y)&df.CA,'PRE60']):+.1f}" for y in range(2010, 2027)))

# 陽性対照
d_ = df[(df.year >= 2010) & (df.year <= 2020)].copy(); d_.loc[d_.TR, "PRE60"] -= 5.0
d, t, se, na, nb = welch(d_.loc[d_.TR, "PRE60"], d_.loc[d_.CA, "PRE60"])
say(f"\n- 陽性対照（在 T の PRE60 に −5 bp 注入）: Δ {d:+.2f} t {t:+.2f}（元 {RES[('PRE60','在 2010-20')]['t']:+.2f}）")

# ---------------- ゲート ㉛ ----------------
say("\n## 本番への接続（scan 19404 本・建玉が T 日 ET 09:00–13:30 vs C_A 日 同時刻・記述・ゲート ㉛）")
dj = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"))); TR = dj["trades"]
et_e = pd.to_datetime([t["entry_time"] for t in TR], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
eo = et_e.normalize().values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
hh = et_e.hour.values + et_e.minute.values / 60.0
Tset = set(df.ord[df.TR].tolist()); Cset = set(df.ord[df.CA].tolist())
yr = np.array([t["year"] for t in TR]); R = np.array([t["R"] for t in TR]); risk = np.array([t["risk"] for t in TR]); ex = np.array([t["exit"] for t in TR])
ft = 0.1 / risk; Rs = np.where(ex == "TIME", R - ft, R + ft)
inT = np.array([o in Tset for o in eo.tolist()]); inC = np.array([o in Cset for o in eo.tolist()]); tw = (hh >= 9.0) & (hh < 13.5)
gate_in = None
for wn, (y0, y1) in WIN.items():
    w = (yr >= y0) & (yr <= y1) & tw
    a = Rs[w & inT]; c = Rs[w & inC]
    d, t, se, na, nb = welch(a, c)
    if wn.startswith("在"): gate_in = abs(d)
    note = "ゲート ㉛: 在 |Δμ| <0.048R → 決着不能（外は参考のみ）" if (wn.startswith("在") and abs(d) < 0.048) else ""
    say(f"- {wn}: T 建玉 n {na} 平均 R* {np.mean(a):+.3f} vs C_A n {nb} {np.mean(c):+.3f} → Δμ {d:+.3f}（t {t:+.2f}・MDE {2*se:.3f}R）{note}")

# ---------------- 判定 ----------------
say("\n## 判定（事前固定）")
g = RES[("PRE60", "在 2010-20")]; o = RES[("PRE60", "外 2021-26H1")]
say(f"- H_ROLL（PRE60 T−C_A <0）: 在 Δ {g['d']:+.2f} t {g['t']:+.2f} (≤−2?) ∧ 外 Δ {o['d']:+.2f} t {o['t']:+.2f} (≤−1.5?) → "
    f"{'PASS' if (g['d']<0 and g['t']<=-2 and o['d']<0 and o['t']<=-1.5) else 'null'}（MDE 在 {2*g['se']:.2f}／外 {2*o['se']:.2f} bp）")
g = RES[("POST60", "在 2010-20")]; o = RES[("POST60", "外 2021-26H1")]
say(f"- H_REV（POST60 T−C_A >0）: 在 Δ {g['d']:+.2f} t {g['t']:+.2f} (≥2.24?) ∧ 外 Δ {o['d']:+.2f} t {o['t']:+.2f} (≥1.5?) → "
    f"{'PASS' if (g['d']>0 and g['t']>=2.24 and o['d']>0 and o['t']>=1.5) else 'null'}")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
