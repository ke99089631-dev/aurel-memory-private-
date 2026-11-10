"""
[cycle36 研究レーン] 2026-11-11 — 【探索・制度カレンダー／ヘッジ需要（収益機会の源泉マップ §8 新行: 週末閉場リスクの保険需要＝曜日効果）】
金 XAUUSD の ET セッション日次リターンに「曜日効果」（金曜 正・月曜 負）はあるか。機構 = 週末 49 時間の閉場中はヘッジ不能
（地政学・政策・金融事故は週末に出やすい）→ 金曜に保険としての金買い（金曜 正）・週明けに解消（月曜 負）。

文献（AI 記憶・独立確認なし）: Ma 1986 "A further investigation of the day-of-the-week effect in the gold market"（月曜 負・金曜 正）、
  その後の研究は市場・時代で混在。株式の曜日効果（French 1980 月曜 負）は 1990 年代以降 消滅/反転が通説＝本拠で立たない効果（㉝）。
  金の機構（週末保険）は株と別なので「金が本拠」。

既知（我々のデータ・再測定しない）: 週末ギャップ 金 16:55→日 18:05 ET の符号つき平均は refute_c16 で 在 +5.05 bp (t 4.8)／外 +3.46 (t 1.8)
  ／近年 +3.46 (t 1.0)、平日の再開 G_5 は 在 +1.02／外 +1.91（c17）。c31 の TOM/休日前は null（MDE 10〜17 bp/日）。

事前固定（数字を見る前に確定）:
  データ: data/macro/XAU_m5_close.npz（bid・取引足）。日次 = c31 と同じ ET セッション日（18:00 ET 開始 → 翌 17:00 ET 終了の暦日で付与・
        最終取引足 close の対数差・bp）。営業日 = 月〜金 − CME 休日（c30/c31 HOL）。休日の足は翌営業日へ（休日明けは posthol フラグ）。
        曜日 = セッション日の暦日の曜日（月曜セッション = 日 18:00 → 月 17:00 ET＝週末ギャップを含む）。
  窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・記述）。基準 = 火・水・木（posthol 除外）。
  H_FRI（主）: 金曜セッションの平均 − 基準 >0。PASS = 在 Δ>0 ∧ t≥2.39（Bonferroni(2)）∧ 外 Δ>0 ∧ t≥1.5、かつ NFP 除外版でも 在 t≥2 ∧ 外 同符号。
  H_MON（主）: 月曜セッションの平均 − 基準 <0。PASS = 在 Δ<0 ∧ t≤−2.39 ∧ 外 Δ<0 ∧ t≤−1.5。
  family-wise: 曜日ラベルを「同じ週の中で」シャッフル（2000 回）→ 5 曜日セル（各曜日 − 他）の max|t| の帰無分布で p_fw。
  決着可能性（㉝）: 文献サイズ +10 bp/日 × 在 11 年の期待 t を数字を見る前に印字。期待 t<2 なら「決着不能」と書く。
  陽性対照: 在の金曜に +10 bp/日 を注入して t。
  分解（記述・判定に不使用）: セッションを gap（前営業日 16:55 → 当日 18:05 ET）／early（18:05 → 12:00）／late（12:00 → 16:55）に分け、
        金曜の正が late（週末前の NY 午後＝保険買いの時間帯・NFP 08:30 を含まない）に局在するか、月曜の負が gap（週末）か post-gap か。
  本拠対照（㉝）: SYM=US500（2014+・㉒）で同じ H_FRI/H_MON（株の曜日効果は消滅が通説＝「立たない」が期待）。
  本番への接続（記述・ゲート ㉛）: scan 19404 本の建玉曜日（ET セッション日）で Δμ（R*・SL/TP は R+ft・TIME は R−ft）金曜 vs 他・月曜 vs 他。
        在 |Δμ| <0.048R なら「決着不能・外は走らせない」。look-ahead 陽性対照 = x0 上位三分位（㉚）。曜日×side は入口フィルタ＝計算しない。
  反証（最重大・事前に書く）: (i) 金曜 = NFP 日（月 1 回・c24: 在 NFP 日 DAY +20 bp t2.3）→ NFP 除外版を判定に含める。
        (ii) 曜日の n ≈ 550（在）・sd 104 bp → MDE ≈ 2·104·sqrt(1/550+1/1650) ≈ 10 bp/日。文献級 +10 bp は t≈2 の境界＝決着不能の可能性大。
        (iii) 2021-26 の上昇年が外の全曜日を持ち上げる → 年FE 版併記。(iv) bid のみ・Dukascopy 1 社・最終印字 16:55 の沈み（全曜日共通で相殺）。
        (v) 月曜セッションは週末ギャップ（既知 +3〜5 bp・正）を含む → 「月曜 負」の機構予測と既知の正ギャップは逆向き＝post-gap で読む。
  seed 20261111。多年 scan 無し・M5 読込なし（npz 1 本＋refute_c4 json）。
"""
import os, sys, json, math, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
SYM = os.environ.get("SYM", "XAU")
OUT = os.path.join(DATA, "c36_day_of_week_result.md" if SYM == "XAU" else f"c36c_day_of_week_{SYM}.md")
rng = np.random.default_rng(20261111); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle36] 金の曜日効果（週末保険需要）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c36_day_of_week.py) SYM={SYM}")

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
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
NFP = {d.date().toordinal() for d in nfp_dates_v2()}

# ---------------- データ → ET セッション日次リターン＋日内分解 ----------------
z = np.load(os.path.join(DATA, "macro", f"{SYM}_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
say(f"- npz {len(TS)} 本 {dt.datetime.fromtimestamp(int(TS[0]), dt.timezone.utc)} 〜 {dt.datetime.fromtimestamp(int(TS[-1]), dt.timezone.utc)} UTC・close {P_ALL.min():.1f}〜{P_ALL.max():.1f}（⑩）")
flat = np.r_[True, P_ALL[1:] == P_ALL[:-1]]
et_all = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
cal_ord = et_all.values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
mod = (et_all.hour * 60 + et_all.minute).values
sess = (et_all + pd.Timedelta(hours=6)).values.astype("datetime64[D]")
sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
wd_all = et_all.weekday.values
say("- flat 比率 曜日別(ET 暦日): " + " ".join(f"{'月火水木金土日'[w]}{flat[wd_all==w].mean()*100:.1f}%" for w in range(7)) + f"・全体 {flat.mean()*100:.1f}%（⑪）")
keep = ~flat
so = sord[keep]; pc = P_ALL[keep]
u, last_idx = np.unique(so[::-1], return_index=True); last_idx = len(so) - 1 - last_idx
close_by_day = dict(zip(u.tolist(), pc[last_idx].tolist()))
# 格子の固定時刻 close（分解用・前値埋めの格子値）
GRID = {}
for m_ in (18 * 60 + 5, 12 * 60, 16 * 60 + 55):
    mk = mod == m_; GRID[m_] = dict(zip(cal_ord[mk].tolist(), P_ALL[mk].tolist()))
rows = []; prev = None
for d in BDAYS:
    o = d.toordinal()
    if o not in close_by_day: continue
    if prev is not None:
        c1805 = GRID[18 * 60 + 5].get(o - 1); c1200 = GRID[12 * 60].get(o); c1655 = GRID[16 * 60 + 55].get(o); p1655 = GRID[16 * 60 + 55].get(prev)
        ok = all(v is not None for v in (c1805, c1200, c1655, p1655))
        gap = math.log(c1805 / p1655) * 1e4 if ok else np.nan
        early = math.log(c1200 / c1805) * 1e4 if ok else np.nan
        late = math.log(c1655 / c1200) * 1e4 if ok else np.nan
        rows.append((o, d.year, d.isocalendar()[1], d.weekday(), math.log(close_by_day[o] / close_by_day[prev]) * 1e4, o in NFP,
                     (o - prev) > (3 if d.weekday() == 0 else 1), gap, early, late))
    prev = o
df = pd.DataFrame(rows, columns=["ord", "year", "week", "wd", "r", "nfp", "posthol", "gap", "early", "late"])
Y0 = 2010 if SYM == "XAU" else 2014
df = df[(df.year >= Y0) & (df.ord <= dt.date(2026, 6, 30).toordinal())].reset_index(drop=True)
df["wk"] = df.year * 100 + df.week
WD = "月火水木金"
say(f"- 営業日リターン {len(df)} 日・{Y0}-01〜2026-06・sd {df.r.std():.0f} bp・|r| 中央値 {df.r.abs().median():.0f} bp・NFP 日 {df.nfp.sum()}（金曜の {df[df.wd==4].nfp.mean()*100:.0f}%）・休日明け {df.posthol.sum()}・分解 OK {df.gap.notna().sum()}")
say("- 曜日別 n: " + " ".join(f"{WD[w]}{(df.wd==w).sum()}" for w in range(5)))

WIN = {"在 2010-20": (Y0, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
if SYM != "XAU": WIN = {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return (a.mean() - b.mean()) / se, se

# ---------------- 決着可能性（㉝・数字を見る前） ----------------
say("\n## 決着可能性（㉝）: 文献サイズ +10 bp/日 の期待 t（在）")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)]
    base = d_[d_.wd.isin([1, 2, 3]) & ~d_.posthol]; nf = (d_.wd == 4).sum(); nm = (d_.wd == 0).sum(); sd = d_.r.std()
    se_f = sd * math.sqrt(1 / nf + 1 / len(base)); se_m = sd * math.sqrt(1 / nm + 1 / len(base))
    say(f"- {wn}: n 金 {nf}／月 {nm}／基準 {len(base)}・sd {sd:.0f} → +10 bp の期待 t 金 {10/se_f:.2f}・月 {10/se_m:.2f}・MDE 金 {2*se_f:.1f}／月 {2*se_m:.1f} bp/日")

# ---------------- 主検定 ----------------
def cells(d_):
    base = d_.r[d_.wd.isin([1, 2, 3]) & ~d_.posthol].values
    out = {}
    for w in range(5):
        a = d_.r[(d_.wd == w) & ~d_.posthol].values if w in (1, 2, 3) else d_.r[d_.wd == w].values
        if w in (1, 2, 3):
            b = d_.r[d_.wd.isin([1, 2, 3]) & ~d_.posthol & (d_.wd != w)].values
        else:
            b = base
        t, se = welch(a, b); out[w] = (a.mean() - b.mean(), t, se, len(a), a.mean())
    return out
RES = {}
VARS = [("生", lambda d_: d_), ("NFP 除外", lambda d_: d_[~d_.nfp]),
        ("年FE", lambda d_: d_.assign(r=d_.r - d_.groupby("year").r.transform("mean")))]
for vname, fn in VARS:
    say(f"\n## 曜日セル（{vname}）: 各曜日 − 基準（火水木・休日明け除外；火水木は自分を除く）bp/日")
    for wn, (y0, y1) in WIN.items():
        d_ = fn(df[(df.year >= y0) & (df.year <= y1)].reset_index(drop=True))
        c = cells(d_); RES[(vname, wn)] = c
        say(f"- {wn}: " + " ｜ ".join(f"{WD[w]} {c[w][4]:+.1f}（Δ {c[w][0]:+.1f}・t {c[w][1]:+.2f}・n {c[w][3]}）" for w in range(5)))

# ---------------- family-wise（週内シャッフル） ----------------
say("\n## family-wise（曜日ラベルを同じ週の中でシャッフル・2000 回・5 セル max|t|）")
NREP = 2000
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)].sort_values(["wk", "ord"]).reset_index(drop=True)
    wk = d_.wk.values; wd = d_.wd.values; r = d_.r.values; ph = d_.posthol.values
    obs = RES[("生", wn)]; obs_t = np.array([obs[w][1] for w in range(5)])
    mx = np.empty(NREP); tf = np.empty(NREP); tm = np.empty(NREP)
    for i in range(NREP):
        order = np.lexsort((rng.random(len(r)), wk)); pw = wd[order]
        ts_ = []
        for w in range(5):
            if w in (1, 2, 3):
                a = r[(pw == w) & ~ph]; b = r[np.isin(pw, [1, 2, 3]) & ~ph & (pw != w)]
            else:
                a = r[pw == w]; b = r[np.isin(pw, [1, 2, 3]) & ~ph]
            ts_.append(welch(a, b)[0])
        ts_ = np.array(ts_); mx[i] = np.abs(ts_).max(); tf[i] = ts_[4]; tm[i] = ts_[0]
    say(f"- {wn}: 観測 max|t| {np.abs(obs_t).max():.2f}（曜日 {WD[int(np.abs(obs_t).argmax())]}）→ p_fw {(mx >= np.abs(obs_t).max()).mean():.3f}・帰無 max|t| 中央値 {np.median(mx):.2f}；"
        f"金曜 t {obs_t[4]:+.2f} → p_fw(max) {(mx >= abs(obs_t[4])).mean():.3f}・片側 p_cell {(tf >= obs_t[4]).mean():.3f}；月曜 t {obs_t[0]:+.2f} → p_fw(max) {(mx >= abs(obs_t[0])).mean():.3f}・片側 p_cell {(tm <= obs_t[0]).mean():.3f}；帰無 t sd 金 {tf.std():.2f}／月 {tm.std():.2f}")

# ---------------- 陽性対照 ----------------
d_ = df[(df.year >= WIN[list(WIN)[0]][0]) & (df.year <= 2020)].copy(); m = (d_.wd == 4).values
d_.loc[m, "r"] += 10.0; c = cells(d_)
say(f"\n- 陽性対照（在の金曜に +10 bp/日 注入）: 金曜 Δ {c[4][0]:+.1f} t {c[4][1]:+.2f}（元 {RES[('生', list(WIN)[0])][4][1]:+.2f}）")

# ---------------- 年別（記述） ----------------
say("\n## 年別 金曜 Δ／月曜 Δ（生・bp/日・記述）")
yl = []
for y in range(Y0, 2027):
    dy = df[df.year == y]
    if len(dy) < 50: continue
    c = cells(dy); yl.append(f"{y}:金{c[4][0]:+.0f}/月{c[0][0]:+.0f}")
say("  " + " ".join(yl))
say("  金曜 Δ>0 の年: " + f"{sum(1 for y in range(Y0, 2027) if len(df[df.year==y])>=50 and cells(df[df.year==y])[4][0]>0)}/{sum(1 for y in range(Y0, 2027) if len(df[df.year==y])>=50)}"
    + "・月曜 Δ<0 の年: " + f"{sum(1 for y in range(Y0, 2027) if len(df[df.year==y])>=50 and cells(df[df.year==y])[0][0]<0)}/{sum(1 for y in range(Y0, 2027) if len(df[df.year==y])>=50)}")

# ---------------- 分解（記述） ----------------
say("\n## 分解（記述・gap = 前営業日 16:55→当日 18:05 ET／early = 18:05→12:00／late = 12:00→16:55・格子値・bp）")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1) & df.gap.notna()]
    base = d_[d_.wd.isin([1, 2, 3]) & ~d_.posthol]
    for w, lab in [(4, "金"), (0, "月")]:
        a = d_[d_.wd == w]; s = []
        for comp in ("gap", "early", "late"):
            t, se = welch(a[comp], base[comp]); s.append(f"{comp} {a[comp].mean():+.1f} vs 基準 {base[comp].mean():+.1f}（Δ {a[comp].mean()-base[comp].mean():+.1f}・t {t:+.2f}）")
        say(f"- {wn} {lab}曜 n {len(a)}: " + " ｜ ".join(s))
    # NFP 除外の金曜 late／early
    a = d_[(d_.wd == 4) & ~d_.nfp]
    t_l, _ = welch(a.late, base.late); t_e, _ = welch(a.early, base.early)
    say(f"    金曜 NFP 除外 n {len(a)}: early Δ {a.early.mean()-base.early.mean():+.1f}（t {t_e:+.2f}）・late Δ {a.late.mean()-base.late.mean():+.1f}（t {t_l:+.2f}）")

# ---------------- 判定 ----------------
say("\n## 判定（事前固定・Bonferroni(2): 在 |t|≥2.39・外 |t|≥1.5 同符号・NFP 除外版 在 |t|≥2 ∧ 外 同符号）")
k_in = list(WIN)[0]; k_out = "外 2021-26H1"
gF = RES[("生", k_in)][4]; oF = RES[("生", k_out)][4]; gFn = RES[("NFP 除外", k_in)][4]; oFn = RES[("NFP 除外", k_out)][4]
passF = gF[0] > 0 and gF[1] >= 2.39 and oF[0] > 0 and oF[1] >= 1.5 and gFn[0] > 0 and gFn[1] >= 2 and oFn[0] > 0
say(f"- H_FRI: 在 Δ {gF[0]:+.1f} t {gF[1]:+.2f} ∧ 外 Δ {oF[0]:+.1f} t {oF[1]:+.2f}；NFP 除外 在 {gFn[0]:+.1f} t {gFn[1]:+.2f} ∧ 外 {oFn[0]:+.1f} t {oFn[1]:+.2f} → {'PASS' if passF else 'null'}（MDE 在 {2*gF[2]:.1f}／外 {2*oF[2]:.1f} bp/日）")
gM = RES[("生", k_in)][0]; oM = RES[("生", k_out)][0]
passM = gM[0] < 0 and gM[1] <= -2.39 and oM[0] < 0 and oM[1] <= -1.5
say(f"- H_MON: 在 Δ {gM[0]:+.1f} t {gM[1]:+.2f} ∧ 外 Δ {oM[0]:+.1f} t {oM[1]:+.2f} → {'PASS' if passM else 'null'}（MDE 在 {2*gM[2]:.1f}／外 {2*oM[2]:.1f} bp/日）")

if SYM != "XAU":
    say(f"\n- 実行 {time.time()-T0:.1f} s"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); sys.exit(0)

# ---------------- 本番への接続（記述・ゲート ㉛） ----------------
say("\n## 本番への接続（scan 19404 本・建玉の ET セッション曜日・記述・ゲート ㉛）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"))); TR = d["trades"]
et_e = pd.to_datetime([t["entry_time"] for t in TR], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
wde = (et_e + pd.Timedelta(hours=6)).weekday.values
yr = np.array([t["year"] for t in TR]); R = np.array([t["R"] for t in TR]); risk = np.array([t["risk"] for t in TR])
ex = np.array([t["exit"] for t in TR]); ft = 0.1 / risk; Rs = np.where(ex == "TIME", R - ft, R + ft)
x0 = np.array([t.get("x0", np.nan) for t in TR], float)
say("- 建玉曜日の分布（全 scan）: " + " ".join(f"{WD[w]}{(wde==w).sum()}" for w in range(5)) + f"・土日 {(wde>=5).sum()}")
gate_open = True
for wn, (y0, y1) in WIN.items():
    w = (yr >= y0) & (yr <= y1) & (wde < 5)
    if wn.startswith("外") and not gate_open:
        say(f"- {wn}: ゲート ㉛ により走らせない"); continue
    if wn.startswith("近年") and not gate_open:
        continue
    s = []
    for wdx, lab in [(4, "金"), (0, "月")]:
        a = Rs[w & (wde == wdx)]; c = Rs[w & (wde != wdx)]; t, se = welch(a, c)
        s.append(f"{lab}曜 n {len(a)} Δμ {a.mean()-c.mean():+.3f}R（t {t:+.2f}・MDE {2*se:.3f}）")
        if wn.startswith("在") and abs(a.mean() - c.mean()) >= 0.048: gate_open = gate_open and True
    if wn.startswith("在"):
        dF = abs(Rs[w & (wde == 4)].mean() - Rs[w & (wde != 4)].mean()); dM = abs(Rs[w & (wde == 0)].mean() - Rs[w & (wde != 0)].mean())
        gate_open = max(dF, dM) >= 0.048
        xx = x0[w]; q = np.nanquantile(xx, 2 / 3); a = Rs[w][xx >= q]; c = Rs[w][xx < q]; t, _ = welch(a, c)
        s.append(f"look-ahead 対照 x0 上位三分位 Δμ {a.mean()-c.mean():+.3f}R（t {t:+.2f}）")
        s.append("ゲート ㉛: 在 |Δμ| <0.048R → 決着不能・外は走らせない" if not gate_open else "ゲート ㉛ 通過 → 外を印字")
    say(f"- {wn}: " + " ｜ ".join(s))

say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
