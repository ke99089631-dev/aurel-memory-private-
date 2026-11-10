"""
[cycle31 研究レーン] 2026-11-10 — 【探索・制度カレンダー／資金移動（収益機会の源泉マップ: 機関投資家の月末資金需要）】
金 XAUUSD の日次リターンに「月替わり（turn-of-month・TOM）」と「月末前の現金化（dash for cash）」の構造はあるか。

機構（文献）:
  - Lakonishok–Smidt 1988 / Ogden 1990: 株式は TOM（最終営業日〜翌月 3 営業日）に正の超過リターン。給与・年金・配当の月次決済フロー
    が月初に資金を市場へ押し込む（payment-cycle 仮説）。
  - Etula–Rinne–Suominen–Vaittinen 2020 "Dash for Cash": 機関の月末支払い需要で月末前（T−8〜T−2）に売り圧力・月初（T+1〜T+3）に
    反転買い。株・国債で確認。金（ETF・先物を通じた機関保有）に同じフローが乗るかは未検証（我々のデータで検証可能）。
  - Ariel 1990: 休日前営業日の正リターン（pre-holiday effect）。金は CME 休日もスポットが薄く取引される（c30: 休日 flat 56.9%）。

事前固定（数字を見る前に確定）:
  データ: data/macro/XAU_m5_close.npz（bid・取引足）。日次 = ET セッション日（18:00 ET 開始→翌 17:00 ET 終了の暦日で付与・
        その日の最終取引足 close → 前セッション日の最終取引足 close の対数差・bp）。週末・CME 休日（c30 と同じ暦）は営業日でない
        （休日の足は翌営業日のリターンに含める=休日をまたぐ）。土日は除外。
  営業日 = 月〜金 − CME 休日（c30 の HOL）。月内位置 k = 当月末最終営業日を 0 とし、その前を −1,−2,...、翌月初 1 営業日を +1,+2,+3。
        注意: 本定義では「最終営業日」= k=0、Lakonishok の TOM は [k=0, +1, +2, +3]（=「−1」を最終営業日と呼ぶ文献表記と同じ日集合）。
  窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・記述）。
  H_TOM（主）: TOM = {k ∈ {0,+1,+2,+3}} の平均日次リターン − それ以外の営業日の平均（bp/日・Welch t）。
        PASS = 在 Δ>0 ∧ t≥2 ∧ 外 Δ>0 ∧ t≥1.5。プラセボ = 同じ 4 日窓を s 営業日ずらした集合 s∈{±4..±10}（14 本）で z_pl・MDE=2sd。
  H_DASH（副・Bonferroni(2)・z≥2.24 相当は t≥2.24）: mean(k∈[−7,−2]) < mean(k∈[+1,+3])。差 D = post − pre（bp/日）>0。
        PASS = 在 D>0 ∧ t≥2.24 ∧ 外 D>0 ∧ t≥1.5。
  H_PRE（副・Bonferroni(2)）: CME 休日の前営業日（休日が月〜金で金が休場または短縮の日の直前）の平均リターン − 他 >0。
        PASS = 在 t≥2.24 ∧ 外 t≥1.5。
  反証（最重大・事前に書く）: (i) NFP（第 1 金曜付近＝k=+1..+3 に落ちることが多い）と重なる → NFP 日を除いた版を併記し、除くと
        消えるなら「発表効果の別名」。(ii) 曜日組成（k=+1 が月曜に偏る等）→ 曜日比率を印字し、曜日固定効果を引いた版を併記。
        (iii) 日次 sd ≈100 bp で n_TOM ≈ 4×132 か月 ≈ 530 日（在）→ MDE ≈ 2·100·sqrt(1/530+1/2200) ≈ 9.7 bp/日。+5 bp/日 級は見えない。
        (iv) 2021-26 は金の強い上昇年（2024-25）が外の平均を持ち上げる → 窓内で年固定効果（年平均を引く）版を併記。
  本番への接続（記述・ゲート ㉛）: scan 19404 本の建玉日が TOM 窓の本の Δμ（R*・SL/TP は R+ft・TIME は R−ft）vs 他。在 |Δμ| <0.048R なら
        「決着不能」と 1 行。
  陽性対照: 在の TOM 日に +10 bp/日 を注入して t を印字（検出率の目安）。
  seed 20261110。多年 scan 無し・M5 読込なし（npz 1 本）。
"""
import os, sys, json, math, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
SYM = os.environ.get("SYM", "XAU")  # 補足 c: SYM=US500 で同じ検定を米株指数（文献の本拠・陽性対照）に適用
OUT = os.path.join(DATA, "c31_turn_of_month_result.md" if SYM == "XAU" else f"c31c_turn_of_month_{SYM}.md")
rng = np.random.default_rng(20261110); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle31] 金の月替わり（TOM）・月末現金化・休日前効果 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c31_turn_of_month_flows.py)")

# ---------------- 暦（c30 と同一） ----------------
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
BORD = np.array([d.toordinal() for d in BDAYS]); BIDX = {o: i for i, o in enumerate(BORD)}
# 月内位置 k
K = {}
months = sorted({(d.year, d.month) for d in BDAYS})
for (y, m) in months:
    bm = [d for d in BDAYS if d.year == y and d.month == m]
    for j, d in enumerate(bm):
        K[d.toordinal()] = (j - (len(bm) - 1), j + 1)  # (k_end: 0=最終営業日・負=その前, k_start: +1=月初 1 営業日)
def kpos(o):
    ke, ks = K[o]; return ke if ke <= 0 and ks > 3 else ks  # 月初 1..3 は +1..+3、それ以外は末からの負の番号／0
# NFP（c24 nfp_dates_v2）
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

# ---------------- データ → ET セッション日次リターン ----------------
z = np.load(os.path.join(DATA, "macro", f"{SYM}_m5_close.npz")); say(f"- SYM {SYM}"); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
say(f"- npz {len(TS)} 本 {dt.datetime.fromtimestamp(int(TS[0]), dt.timezone.utc)} 〜 {dt.datetime.fromtimestamp(int(TS[-1]), dt.timezone.utc)} UTC・close {P_ALL.min():.1f}〜{P_ALL.max():.1f}（⑩）")
flat = np.r_[True, P_ALL[1:] == P_ALL[:-1]]
et_all = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
sess = (et_all + pd.Timedelta(hours=6)).values.astype("datetime64[D]")  # 18:00 ET 始まりのセッション日
sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
keep = ~flat
so = sord[keep]; pc = P_ALL[keep]
# セッション日ごとの最終取引足 close
u, last_idx = np.unique(so[::-1], return_index=True); last_idx = len(so) - 1 - last_idx
close_by_day = dict(zip(u.tolist(), pc[last_idx].tolist()))
say(f"- 取引足 {keep.sum()} 本（flat {flat.mean()*100:.1f}%・⑪）・セッション日 {len(u)} 日")
# 営業日系列（BDAYS に close がある日）: r_d = ln C_d − ln C_{prev business day with close}
rows = []
prev = None
for d in BDAYS:
    o = d.toordinal()
    if o not in close_by_day: continue
    if prev is not None:
        rows.append((o, d.year, d.weekday(), kpos(o), math.log(close_by_day[o] / close_by_day[prev]) * 1e4, o in NFP,
                     (d + dt.timedelta(days=1)) in HOL or (d.weekday() == 4 and (d + dt.timedelta(days=3)) in HOL)))
    prev = o
df = pd.DataFrame(rows, columns=["ord", "year", "wd", "k", "r", "nfp", "prehol"])
df = df[(df.year >= 2010) & (df.ord <= dt.date(2026, 6, 30).toordinal())].reset_index(drop=True)
say(f"- 営業日リターン {len(df)} 日・2010-01〜2026-06・sd {df.r.std():.0f} bp・|r| 中央値 {df.r.abs().median():.0f} bp・NFP 日 {df.nfp.sum()}・休日前営業日 {df.prehol.sum()}")
# 曜日組成（数字を見る前に印字）
WD = "月火水木金"
say("- 曜日組成 k別: " + " | ".join(f"k={k}: " + "/".join(f"{WD[w]}{(df[df.k==k].wd==w).mean()*100:.0f}" for w in range(5)) for k in [-2, -1, 0, 1, 2, 3]))
say(f"- NFP が k=+1..+3 に落ちる率: {df[df.k.isin([1,2,3])].nfp.mean()*100:.1f}%（NFP 日のうち k∈+1..+3: {df[df.nfp].k.isin([1,2,3]).mean()*100:.0f}%）")

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return (a.mean() - b.mean()) / se, se
TOMK = {0, 1, 2, 3}
def tom_set_shift(d_, s):
    """TOM 窓を s 営業日ずらした集合（営業日 index で）"""
    oset = set(d_.ord[d_.k.isin(TOMK)].tolist())
    sh = set()
    for o in oset:
        i = BIDX.get(o)
        if i is not None and 0 <= i + s < len(BORD): sh.add(int(BORD[i + s]))
    return d_.ord.isin(sh).values

def run_tom(d_, label):
    res = {}
    m = d_.k.isin(TOMK).values
    t, se = welch(d_.r[m], d_.r[~m]); delta = d_.r[m].mean() - d_.r[~m].mean()
    pl = []
    for s in list(range(-10, -3)) + list(range(4, 11)):
        ms = tom_set_shift(d_, s)
        if ms.sum() < 20: continue
        pl.append(d_.r[ms].mean() - d_.r[~ms].mean())
    pl = np.array(pl); zpl = (delta - pl.mean()) / pl.std(ddof=1)
    say(f"  - {label}: TOM n {m.sum()} 平均 {d_.r[m].mean():+.1f} vs 他 n {(~m).sum()} {d_.r[~m].mean():+.1f} bp/日 → Δ {delta:+.1f}（Welch t {t:+.2f}・se {se:.1f}・MDE {2*se:.1f}）"
        f"；プラセボ s=±4..10 {len(pl)} 本 平均 {pl.mean():+.1f} sd {pl.std(ddof=1):.1f} → z_pl {zpl:+.2f}")
    res.update(dict(n=int(m.sum()), delta=delta, t=t, se=se, zpl=zpl))
    # k 別プロファイル
    say("    k 別平均（bp/日・n）: " + " ".join(f"{k:+d}:{d_.r[d_.k==k].mean():+.0f}({(d_.k==k).sum()})" for k in [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]))
    return res
def run_dash(d_, label):
    pre = d_.k.between(-7, -2).values; post = d_.k.isin([1, 2, 3]).values
    t, se = welch(d_.r[post], d_.r[pre]); D = d_.r[post].mean() - d_.r[pre].mean()
    say(f"  - {label}: pre[−7,−2] n {pre.sum()} {d_.r[pre].mean():+.1f} / post[+1,+3] n {post.sum()} {d_.r[post].mean():+.1f} → D {D:+.1f} bp/日（t {t:+.2f}・MDE {2*se:.1f}）")
    return dict(D=D, t=t, se=se)
def run_pre(d_, label):
    m = d_.prehol.values
    t, se = welch(d_.r[m], d_.r[~m]); delta = d_.r[m].mean() - d_.r[~m].mean()
    say(f"  - {label}: 休日前 n {m.sum()} {d_.r[m].mean():+.1f} vs 他 {d_.r[~m].mean():+.1f} → Δ {delta:+.1f} bp（t {t:+.2f}・MDE {2*se:.1f}）")
    return dict(delta=delta, t=t, se=se)

RES = {}
for variant, fn in [("生", lambda d_: d_), ("NFP 除外", lambda d_: d_[~d_.nfp]),
                    ("年FE（年平均を引く）", lambda d_: d_.assign(r=d_.r - d_.groupby("year").r.transform("mean"))),
                    ("曜日FE＋年FE", lambda d_: d_.assign(r=d_.r - d_.groupby("year").r.transform("mean")).pipe(lambda x: x.assign(r=x.r - x.groupby("wd").r.transform("mean"))))]:
    say(f"\n## H_TOM（{variant}）")
    for wn, (y0, y1) in WIN.items():
        d_ = fn(df[(df.year >= y0) & (df.year <= y1)].reset_index(drop=True))
        RES[(variant, wn, "TOM")] = run_tom(d_, wn)
    say(f"## H_DASH（{variant}）")
    for wn, (y0, y1) in WIN.items():
        d_ = fn(df[(df.year >= y0) & (df.year <= y1)].reset_index(drop=True))
        RES[(variant, wn, "DASH")] = run_dash(d_, wn)
say("\n## H_PRE（休日前営業日・生／年FE）")
for wn, (y0, y1) in WIN.items():
    d_ = df[(df.year >= y0) & (df.year <= y1)].reset_index(drop=True)
    RES[("生", wn, "PRE")] = run_pre(d_, wn)
    d2 = d_.assign(r=d_.r - d_.groupby("year").r.transform("mean")); RES[("年FE", wn, "PRE")] = run_pre(d2, wn + "（年FE）")
# 年別 TOM Δ（記述）
say("\n## 年別 TOM Δ（bp/日・記述）")
say("  " + " ".join(f"{y}:{df[(df.year==y)&df.k.isin(TOMK)].r.mean()-df[(df.year==y)&~df.k.isin(TOMK)].r.mean():+.0f}" for y in range(2010, 2027)))
# 陽性対照: 在 TOM に +10 bp/日 注入
d_ = df[(df.year >= 2010) & (df.year <= 2020)].copy(); m = d_.k.isin(TOMK).values
d_.loc[m, "r"] += 10.0; t_inj, _ = welch(d_.r[m], d_.r[~m])
say(f"\n- 陽性対照（在 TOM に +10 bp/日 注入）: Welch t {t_inj:+.2f}（元 {RES[('生','在 2010-20','TOM')]['t']:+.2f}）")

# ---------------- 本番への接続（記述・ゲート ㉛） ----------------
if SYM != "XAU":  # 補足 c（US500 等）: 金の scan への接続は無意味なので判定だけ印字して終了
    say("\n## 判定（事前固定・陽性対照用）")
    for hn, key, lab in [("H_TOM", "TOM", "delta"), ("H_DASH", "DASH", "D"), ("H_PRE", "PRE", "delta")]:
        g = RES[("生", "在 2010-20", key)]; o = RES[("生", "外 2021-26H1", key)]
        say(f"- {hn}: 在 Δ {g[lab]:+.1f} t {g['t']:+.2f} ∧ 外 Δ {o[lab]:+.1f} t {o['t']:+.2f}")
    say(f"\n- 実行 {time.time()-T0:.1f} s"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); sys.exit(0)
say("\n## 本番への接続（scan 19404 本・建玉日が TOM 窓・記述）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"))); TR = d["trades"]
et_e = pd.to_datetime([t["entry_time"] for t in TR], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
eo = ((et_e + pd.Timedelta(hours=6)).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal())
kmap = dict(zip(df.ord.tolist(), df.k.tolist()))
ke = np.array([kmap.get(int(o), np.nan) for o in eo]); yr = np.array([t["year"] for t in TR])
R = np.array([t["R"] for t in TR]); risk = np.array([t["risk"] for t in TR]); ex = np.array([t["exit"] for t in TR]); ft = 0.1 / risk
Rs = np.where(ex == "TIME", R - ft, R + ft)
for wn, (y0, y1) in WIN.items():
    w = (yr >= y0) & (yr <= y1) & np.isfinite(ke)
    a = Rs[w & np.isin(ke, list(TOMK))]; c = Rs[w & ~np.isin(ke, list(TOMK))]
    t, se = welch(a, c)
    gate = "ゲート ㉛: 在 |Δμ| <0.048R → 決着不能（走らせない）" if (wn.startswith("在") and abs(a.mean() - c.mean()) < 0.048) else ""
    say(f"- {wn}: TOM 建玉 n {len(a)} 平均 R* {a.mean():+.3f} vs 他 n {len(c)} {c.mean():+.3f} → Δμ {a.mean()-c.mean():+.3f}（t {t:+.2f}・MDE {2*se:.3f}R）{gate}")

# ---------------- 判定 ----------------
say("\n## 判定（事前固定）")
g = RES[("生", "在 2010-20", "TOM")]; o = RES[("生", "外 2021-26H1", "TOM")]
say(f"- H_TOM: 在 Δ {g['delta']:+.1f} t {g['t']:+.2f} (≥2?) ∧ 外 Δ {o['delta']:+.1f} t {o['t']:+.2f} (≥1.5?) → "
    f"{'PASS' if (g['delta']>0 and g['t']>=2 and o['delta']>0 and o['t']>=1.5) else 'null'}")
g = RES[("生", "在 2010-20", "DASH")]; o = RES[("生", "外 2021-26H1", "DASH")]
say(f"- H_DASH: 在 D {g['D']:+.1f} t {g['t']:+.2f} (≥2.24?) ∧ 外 D {o['D']:+.1f} t {o['t']:+.2f} (≥1.5?) → "
    f"{'PASS' if (g['D']>0 and g['t']>=2.24 and o['D']>0 and o['t']>=1.5) else 'null'}")
g = RES[("生", "在 2010-20", "PRE")]; o = RES[("生", "外 2021-26H1", "PRE")]
say(f"- H_PRE: 在 Δ {g['delta']:+.1f} t {g['t']:+.2f} (≥2.24?) ∧ 外 Δ {o['delta']:+.1f} t {o['t']:+.2f} (≥1.5?) → "
    f"{'PASS' if (g['delta']>0 and g['t']>=2.24 and o['delta']>0 and o['t']>=1.5) else 'null'}")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
