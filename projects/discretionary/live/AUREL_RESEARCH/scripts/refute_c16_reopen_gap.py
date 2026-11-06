# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-06 23:15 反証レーン] 対象: cycle16 (21:55) の事後弱信号
  「日次メンテ明け（London 23 時 = 18:00 ET）の再開ギャップ足 23:00–23:05 は 在 +2.61 bp (t19.4)・外 +2.12 (t8.5)・近年 +2.69 (t5.5)、
   23 時全体 在 +3.12／外 +3.29／近年 +4.65、17 年中 15 年で正。機構候補 = 1 時間のブレイクに世界の情報が凝縮される close-to-open プレミアム」
  ＋ cycle16 自身の最重大反証「ギャップは受け取れない（スワップ＋広がったスプレッドの往復）」。

=== 事前固定（この docstring を書いてから数字を見る）===
時刻は **America/New_York（ET）** で切る。実際の制度スケジュールは CME Globex／Dukascopy 金の日次ブレイク 17:00–18:00 ET で、
cycle16 の London 現地は 3〜4 週/年の DST 不一致週でブレイクが 21–22 時 or 23–24 時 London にずれる（cycle16 の 23 時 flat 22% ≒ 金曜 20% + 不一致週）。
ET で切った版を主にし、London 版（Q0）で cycle16 の数字を再現して突合する。
「クリーンなブレイク日」= ET 平日（月〜木。金は 17:00 以降 週末 flat）で 17:00–17:55 ET の 12 本が全部 flat の日。主集合はこれ。
G_k = ln bid(18:05 ET) − ln bid(17:00 − k 分 ET)、k ∈ {0,5,10,15,30,60,120}（k=0 は 16:55 足の close = 引け値）。
窓 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年プール不使用）。bp 単位・日クラスタ（1 日 1 観測）。

Q0 再現: London 23:00 足（cycle16b と同じ定義）を 1e-10 で再現。ET 18:00 足との差（不一致週の影響）を印字。
Q1 バウンス分解（引け前の bid 沈み → 再開で戻る なら「情報」でなく microstructure）:
   (a) G_k を k 別に（外で G_30 < G_0/3 なら「ギャップの 2/3 以上は引け前 30 分の沈みの戻り」）。
   (b) 日レベル: 再開足 r_gap を 引け前 30 分 r_pre30 に回帰（傾き <−0.3 なら戻り）。r_pre30≥0 の日と <0 の日の r_gap 条件付き平均。
   (c) M1（Dukascopy xauusd M1 bid chunks・66 本）で 18:00–18:01 の最初の 1 分 vs 18:01–18:05、引け前 16:55..16:59 の分別。
       最初の 1 分がギャップの大半で、その後 4 分で逆行するなら「寄り付き印字」の性質（保有者は受け取れるが縮む）。
Q2 bid アーティファクトの上限: bid で測ったギャップの偏り = (s_reopen − s_preclose)/2。
   (a) 全ギャップを説明するのに要る Δspread = 2·G_0·price（USD）を窓別に印字（Dukascopy 金の典型 0.2〜0.4 USD と比較）。
   (b) 実口座 spread_log（bid・spread_pt・42 日・読取のみ）で日別に 引け直前 10 分の最後の spread と 再開 5 分以内の最初の spread → 偏り bp。
       実口座の bid ギャップ・mid ギャップも印字（n ≈ 30・記述）。業者が違うので「上限の目安」。
Q3 分散比例ドリフトのプラセボ: ET 288 スロットごとに 平均 m_s と分散 v_s（平日全本）。18:00 スロットを除いて m = a + b·v を OLS、
   18:00 スロットの残差 z（残差 sd 単位）。z<2 なら「分散の大きい足ほど平均も大きい」の一般則で説明がつく（再開は特別でない）。
   残差上位 5 スロットも印字（18:00 が孤立か）。
Q4 「休止明けの最初の足は正」プラセボ（ベンダー／前値埋めの一般アーティファクトか）: ET 平日で直前 ≥12 本 flat（≥1h）の後の最初の非 flat 足、
   ただし ET 18 時を除く（日次ブレイクでない休止＝祝日・データ欠落）。n・平均・t。外で 平均 ≥ G_0/2 ∧ t≥3 なら「休止明けは何でも正」。
Q5 構造の掃引: ET 曜日別（月〜木）の G_0／週次オープン（金 16:55 → 日 18:05 ET・49 時間）の G／年別符号（G_0・G_30・G_60）／
   外の月ブロック bootstrap 95% CI（G_0・G_30）／近年 LOYO（2026H1 除去）。
Q6 市場横断プラセボ（記述）: US500（bid・2012-26）の 18:00 ET 再開足 G_0・G_30（株の overnight premium は既知）。
Q7 受け取れるか（コードで）: 「16:55 ET 引けで買い、18:05 ET で売る」日次の net bp = G_0 − 往復スプレッド bp − swap bp。
   往復スプレッド = 0.42 USD（実口座 21:50–22:00 と 23:00–23:10 の中央値 0.21×2）と 0.84（倍）。swap ∈ {0, 1, 2} bp/日（口座仕様は needs data）。
   窓別 平均・t・年率 SR。16:25 ET から持つ版（G_30）も。
   判定: 外で 0.42 USD ∧ swap 2 bp で t≥2 なら「受け取れる」、そうでなければ「受け取れない（小売コスト）」。

=== 判定規則（事前固定）===
主張 T: 「18:00 ET 再開足の正ギャップは外 2021-26 で実在し、引け前の沈みの戻りでも bid-spread アーティファクトでも分散比例ドリフトでも
休止明け一般のアーティファクトでもない」。
- broken: 次のいずれか。(B1) 外 G_30 < G_0/3 または 外 G_30 の t<2 ／(B2) 外 Q3 の z<2 ／(B3) 実口座 bias 上限 ≥ 外 G_0 の 50% ／
  (B4) Q4 プラセボ 外 平均 ≥ G_0/2 ∧ t≥3。
- survived: 全部。外 G_30・G_60 とも t≥3 かつ ≥ 2/3·G_0 ／ 外 z≥3 ／ bias 上限 < 20% ／ Q4 プラセボ < G_0/4（または n<30）／ 年別 G_30 正 ≥12/17。
- それ以外 inconclusive。
受け取れるかは Q7 で別採点。看板の「15/17 年」「t 19」は争わない（再現で確認するだけ）。
入力は既存キャッシュ（XAU/US500 npz）＋ Dukascopy M1 chunks（読取・AssetEmpire 側）＋ spread_log.jsonl（読取）。scan 無し・MT5 無し・外部通信無し。
seed 20261106。
"""
import os, time, math, json, glob
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
CHUNKS = r"C:\Users\user\AssetEmpire\empire\research\dukas\chunks"
OUT = os.path.join(DATA, "refute_c16_reopen_gap.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c16] 再開ギャップ（18:00 ET）を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c16_reopen_gap.py)")

W = {"在2010-20": (2010, 2020), "外2021-26H1": (2021, 2026), "近年2024-26H1": (2024, 2026)}
def ms(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 2: return (np.nan, np.nan, np.nan, n)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return (m, se, m / se if se > 0 else np.nan, n)
def fmt(x, extra=False):
    m, se, t, n = ms(x)
    s = f"{m:+.2f} (t{t:+.1f}, n{n})"
    if extra and n > 1: s += f", 中央値 {np.median(x):+.2f}, 正 {(np.asarray(x)>0).mean()*100:.0f}%"
    return s
def wrow(vals, yrs, extra=False):
    return " ｜ ".join(f"{wn} {fmt(vals[(yrs>=a)&(yrs<=b)], extra)}" for wn, (a, b) in W.items())

# ---------- load XAU M5 (bid) ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); r_bp = r * 1e4; flat = r == 0
t_utc = pd.to_datetime(ts, unit="s", utc=True)
t_ny = t_utc.tz_convert("America/New_York"); t_lon = t_utc.tz_convert("Europe/London")
h_ny = t_ny.hour.to_numpy(); m_ny = t_ny.minute.to_numpy(); wd_ny = t_ny.weekday.to_numpy()
day_ny = t_ny.year.to_numpy() * 10000 + t_ny.month.to_numpy() * 100 + t_ny.day.to_numpy(); yr_ny = t_ny.year.to_numpy()
h_lo = t_lon.hour.to_numpy(); m_lo = t_lon.minute.to_numpy(); wd_lo = t_lon.weekday.to_numpy(); yr_utc = t_utc.year.to_numpy()
dts = np.diff(ts); gap_after = np.where(dts != 300)[0]  # bar i+1 follows a hole
valid = np.ones(len(ts), bool); valid[gap_after + 1] = False   # return of the bar after a hole spans >5 min → exclude from slot/pause stats
r_bp_v = np.where(valid, r_bp, np.nan)
say(f"- XAU npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）、flat 比率 全体 {flat.mean()*100:.1f}%（⑪）。"
    f"**格子の穴 {len(gap_after)} 箇所**（欠落日: " + ", ".join(str(pd.to_datetime(ts[i], unit='s').date()) for i in gap_after[:6]) + " …）→ 参照は index でなく ts 一致で取る。穴直後の足は Q3/Q4 から除外")
def idx_at(target_ts):
    """exact-timestamp lookup; -1 where missing"""
    j = np.searchsorted(ts, target_ts); j = np.clip(j, 0, len(ts) - 1); return np.where(ts[j] == target_ts, j, -1)
say("- ET 時別 flat 比率（ET 平日）: " + " ".join(f"{hh}:{flat[(wd_ny<=4)&(h_ny==hh)].mean()*100:.0f}%" for hh in range(24)))
# per-year flat ratio of ET 17h (schedule stability)
say("- ET 17 時 flat 比率 年別（月〜木）: " + " ".join(f"{y}:{flat[(wd_ny<=3)&(h_ny==17)&(yr_ny==y)].mean()*100:.0f}%" for y in range(2010, 2027)))

# ---------- Q0 reproduce London 23:00 bar ----------
say("\n## Q0 再現（London 23:00–23:05 足・cycle16b 定義）と ET 18:00–18:05 足の比較")
mL = (wd_lo <= 4) & (h_lo == 23) & (m_lo == 0)
say(f"- London 23:00 足: " + wrow(r_bp[mL], yr_utc[mL], True))
say(f"  （cycle16b: 在 +2.61 (t+19.4, n2857) ｜ 外 +2.12 (t+8.5, n1429) ｜ 近年 +2.69 (t+5.5, n649)）")
# ET gap bars: start 18:00 ET, weekday Mon-Thu (Fri 18:00 is weekend flat), Sunday excluded
iG = np.where((wd_ny <= 3) & (h_ny == 18) & (m_ny == 0))[0]
KS = [0, 5, 10, 15, 30, 60, 120]
tG = ts[iG]
REF = {k: idx_at(tG - (65 + k) * 60) for k in KS}            # bar starting 17:00−k−5 ET (its close = 17:00−k)
BRK = np.column_stack([idx_at(tG - 300 * j) for j in range(1, 13)])   # 17:00..17:55 ET bars
NXT = idx_at(tG + 3600)                                        # 19:00 ET bar
present = (NXT >= 0) & np.all(BRK >= 0, axis=1) & np.all(np.column_stack([REF[k] for k in KS]) >= 0, axis=1) & (iG > 0) & valid[iG]
iG = iG[present]; tG = tG[present]; NXT = NXT[present]; BRK = BRK[present]; REF = {k: REF[k][present] for k in KS}
clean = np.all(flat[BRK], axis=1)  # 17:00..17:55 ET all flat
say(f"- ET 18:00 足 候補日 {len(iG)}（月〜木・参照 ts 全部実在）、クリーンなブレイク日（17:00–17:55 ET 12 本 flat）{clean.sum()} = {clean.mean()*100:.1f}%")
say("  非クリーン日の年別数: " + " ".join(f"{y}:{((~clean)&(yr_ny[iG]==y)).sum()}" for y in range(2010, 2027)))
gap_all = r_bp[iG]; yG_all = yr_ny[iG]
say(f"- ET 18:00 足（全候補日）: " + wrow(gap_all, yG_all, True))
iG = iG[clean]; NXT = NXT[clean]; REF = {k: REF[k][clean] for k in KS}; yG = yr_ny[iG]; dG = day_ny[iG]; wdG = wd_ny[iG]
gap = r_bp[iG]
say(f"- ET 18:00 足（クリーン日のみ・以下の主集合）: " + wrow(gap, yG, True))

# ---------- Q1 bounce decomposition ----------
say("\n## Q1 バウンス分解: G_k = ln bid(18:05) − ln bid(17:00−k)")
G = {k: (lc[iG] - lc[REF[k]]) * 1e4 for k in KS}
for k in KS:
    say(f"- G_{k:<3}: " + wrow(G[k], yG))
pre30 = (lc[REF[0]] - lc[REF[30]]) * 1e4   # 16:30 → 17:00 ET
pre60 = (lc[REF[0]] - lc[REF[60]]) * 1e4
say(f"- 引け前 30 分 (16:30→17:00 ET): " + wrow(pre30, yG, True))
say(f"- 引け前 60 分 (16:00→17:00 ET): " + wrow(pre60, yG, True))
say("- (b) 日レベル回帰 r_gap = a + β·r_pre30、条件付き平均:")
for wn, (a, b) in W.items():
    w = (yG >= a) & (yG <= b); x = pre30[w]; y = gap[w]
    beta = np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1); res = y - y.mean() - beta * (x - x.mean())
    se_b = math.sqrt((res**2).sum() / (len(x) - 2) / ((x - x.mean())**2).sum()); rho = np.corrcoef(x, y)[0, 1]
    qa, qb = np.quantile(x, [1 / 3, 2 / 3]); ter = [x <= qa, (x > qa) & (x <= qb), x > qb]
    say(f"  - {wn}: β {beta:+.3f} (t{beta/se_b:+.1f}, ρ {rho:+.3f})；r_gap | pre30≥0: {fmt(y[x>=0])} ／ pre30<0: {fmt(y[x<0])}；"
        f" pre30 三分位別 r_gap（下/中/上）: " + " / ".join(fmt(y[m_]) for m_ in ter))
# last 5-min bar before close (16:55–17:00 ET) = G_0 − G_5
last5 = G[0] - G[5]
say(f"- 引け最後の 5 分足 16:55→17:00 ET（= G_0 − G_5）: " + wrow(last5, yG, True))
# no-break era 2010-12 (ET 17h traded): what did 17h and 18:00 bar look like?
say("- **ブレイク無し時代（2010-12・ET 17 時が取引されていた日）**: 17:00–18:00 ET の和・18:00 足・16:55 足 を年別に（London 23 時が『再開』でなかった年の正リターンの中身）")
iN = np.where((wd_ny <= 3) & (h_ny == 18) & (m_ny == 0) & (yr_ny <= 2012))[0]
RN = {k: idx_at(ts[iN] - (65 + k) * 60) for k in (0, 5, 30, 60)}; BN = np.column_stack([idx_at(ts[iN] - 300 * j) for j in range(1, 13)])
okN = np.all(BN >= 0, axis=1) & np.all(np.column_stack([RN[k] for k in RN]) >= 0, axis=1)
iN = iN[okN]; BN = BN[okN]; RN = {k: RN[k][okN] for k in RN}; traded = ~np.all(flat[BN], axis=1); yN = yr_ny[iN]
for y in (2010, 2011, 2012):
    w = (yN == y) & traded
    h17 = r_bp[BN[w]].sum(axis=1); b18 = r_bp[iN[w]]; b1655 = (lc[RN[0][w]] - lc[RN[5][w]]) * 1e4; g30n = (lc[iN[w]] - lc[RN[30][w]]) * 1e4
    say(f"  - {y} 取引日 n{w.sum()}: 17h 和 {fmt(h17)} ／ 18:00 足 {fmt(b18, True)} ／ 16:55 足 {fmt(b1655)} ／ G_30 相当 {fmt(g30n)}；17h の flat 本数 中央値 {np.median(flat[BN[w]].sum(axis=1)):.0f}/12")
Q1_out = {k: ms(G[k][(yG >= 2021)]) for k in KS}

# ---------- Q1(c) M1 decomposition ----------
say("\n## Q1(c) M1（Dukascopy xauusd bid）: 最初の 1 分 vs 残り 4 分、引け前 5 分の分別")
tm = time.time()
files = sorted(glob.glob(os.path.join(CHUNKS, "xauusd-m1-bid-*.csv")))
parts = [pd.read_csv(f, usecols=["timestamp", "close"], dtype={"timestamp": np.int64, "close": np.float64}) for f in files]
m1 = pd.concat(parts, ignore_index=True); m1 = m1.drop_duplicates("timestamp").sort_values("timestamp")
ts1 = (m1["timestamp"].to_numpy() // 1000).astype(np.int64); lc1 = np.log(m1["close"].to_numpy()); del parts, m1
say(f"- M1 {len(files)} chunks・{len(ts1)} 行・{pd.to_datetime(ts1[0],unit='s')}〜{pd.to_datetime(ts1[-1],unit='s')} UTC（⑩）・読込 {time.time()-tm:.0f} s・1 分格子 {np.all(np.diff(ts1)==60)}")
j0 = np.searchsorted(ts1, ts[iG]); okj = (j0 + 5 < len(ts1)) & (j0 >= 70) & (ts1[np.clip(j0, 0, len(ts1) - 1)] == ts[iG])
j0 = j0[okj]; y1 = yG[okj]
first1 = (lc1[j0] - lc1[j0 - 1]) * 1e4          # 18:00–18:01 (vs 17:59 close = pre-close bid)
rest4 = (lc1[j0 + 4] - lc1[j0]) * 1e4           # 18:01–18:05
g5 = (lc1[j0 + 4] - lc1[j0 - 1]) * 1e4
say(f"- 突合 {okj.sum()}/{len(okj)} 日。M1 5 分ギャップ（= M5 G_0 の筈）: " + wrow(g5, y1))
say(f"- 最初の 1 分 18:00–18:01: " + wrow(first1, y1, True))
say(f"- 残り 4 分 18:01–18:05 : " + wrow(rest4, y1, True))
for mm_ in range(5):
    jj = j0 - 61 + mm_   # bar starting 16:55+mm_ ET (close at 16:56+mm_)
    rr = (lc1[jj] - lc1[jj - 1]) * 1e4
    say(f"- 引け前 1 分足 16:{55+mm_:02d}–16:{56+mm_:02d} ET: " + wrow(rr, y1, True))
# first minute later reversal within hour: 18:05 -> 19:00 from M5
rest55 = (lc[NXT] - lc[iG]) * 1e4
say(f"- 18:05→19:00 ET（残り 55 分・M5）: " + wrow(rest55, yG, True))

# ---------- Q2 bid artifact bound ----------
say("\n## Q2 bid アーティファクトの上限")
for wn, (a, b) in W.items():
    w = (yG >= a) & (yG <= b); p_med = np.median(cl[iG[w]]); g0 = G[0][w].mean()
    say(f"- {wn}: 中央値価格 {p_med:.0f} USD・G_0 {g0:+.2f} bp → 全部を bid 偏りで説明するのに要る Δspread(引け前−再開) = {2*g0*1e-4*p_med:.2f} USD")
try:
    rows = []
    with open(os.path.join(LIVE, "spread_log.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line); rows.append((int(o["ts"]), float(o["spread_pt"]), float(o["bid"])))
            except Exception: pass
    S = pd.DataFrame(rows, columns=["ts", "sp", "bid"]).drop_duplicates("ts").sort_values("ts")
    tn = pd.to_datetime(S["ts"], unit="s", utc=True).dt.tz_convert("America/New_York")
    S["d"] = (tn.dt.year * 10000 + tn.dt.month * 100 + tn.dt.day).to_numpy(); S["h"] = tn.dt.hour.to_numpy(); S["m"] = tn.dt.minute.to_numpy(); S["wd"] = tn.dt.weekday.to_numpy()
    S = S[S["wd"] <= 3]
    recs = []
    for d, g in S.groupby("d"):
        pre = g[(g["h"] == 16) & (g["m"] >= 50)]; post = g[(g["h"] == 18) & (g["m"] < 5)]
        if len(pre) and len(post):
            p0 = pre.iloc[-1]; p1 = post.iloc[0]
            bias_bp = (p1["sp"] - p0["sp"]) / 2 / p0["bid"] * 1e4
            gb = math.log(p1["bid"] / p0["bid"]) * 1e4; gm = math.log((p1["bid"] + p1["sp"] / 2) / (p0["bid"] + p0["sp"] / 2)) * 1e4
            recs.append((d, p0["sp"], p1["sp"], bias_bp, gb, gm, (p1["ts"] - p0["ts"]) / 60))
    Rr = pd.DataFrame(recs, columns=["d", "sp_pre", "sp_post", "bias_bp", "gap_bid", "gap_mid", "gap_min"])
    say(f"- 実口座 spread_log（読取のみ）: 日 {len(Rr)}、引け前最後の spread 中央値 {Rr.sp_pre.median():.2f}・再開最初の spread 中央値 {Rr.sp_post.median():.2f} USD、"
        f"参照間隔 中央値 {Rr.gap_min.median():.0f} 分")
    say(f"  bid 偏り (s_post−s_pre)/2 → {fmt(Rr.bias_bp.to_numpy())} bp（正＝bid が再開ギャップを過大に見せる）；実口座 bid ギャップ {fmt(Rr.gap_bid.to_numpy())} bp・mid ギャップ {fmt(Rr.gap_mid.to_numpy())} bp（n 小・記述）")
    BIAS = Rr.bias_bp.mean()
except Exception as e:
    say(f"- spread_log 読取失敗: {e}"); BIAS = np.nan

# ---------- Q3 mean-variance placebo across 288 ET slots ----------
say("\n## Q3 分散比例ドリフトのプラセボ（ET 288 スロット・平日・m_s = a + b·v_s、18:00 スロット除いて OLS）")
slot = h_ny * 12 + m_ny // 5; wk = wd_ny <= 4
Z3 = {}
for wn, (a, b) in W.items():
    w = wk & (yr_ny >= a) & (yr_ny <= b)
    df = pd.DataFrame({"s": slot[w], "r": r_bp_v[w]}).dropna(); g = df.groupby("s")["r"]
    m_s = g.mean().reindex(range(288)).to_numpy(); v_s = g.var(ddof=1).reindex(range(288)).to_numpy(); n_s = g.size().reindex(range(288)).to_numpy()
    s18 = 18 * 12; mask = np.arange(288) != s18
    X = np.column_stack([np.ones(mask.sum()), v_s[mask]]); beta = np.linalg.lstsq(X, m_s[mask], rcond=None)[0]
    res = m_s[mask] - X @ beta; sd = res.std(ddof=2); pred18 = beta[0] + beta[1] * v_s[s18]; z18 = (m_s[s18] - pred18) / sd
    resid_all = m_s - (beta[0] + beta[1] * v_s); top = np.argsort(-np.abs(resid_all))[:5]
    # also mean/sd ratio ranking (per-bar Sharpe)
    sh = m_s / np.sqrt(v_s); rank_sh = int((sh > sh[s18]).sum()) + 1
    Z3[wn] = z18
    say(f"- {wn}: b {beta[1]:+.4f} bp/bp² (切片 {beta[0]:+.3f})、18:00 スロット m {m_s[s18]:+.2f} bp・sd {math.sqrt(v_s[s18]):.1f} bp・予測 {pred18:+.2f} → **残差 z {z18:+.1f}**；"
        f" 足 Sharpe 順位 {rank_sh}/288（{sh[s18]:+.3f}）；残差上位 5 スロット: " + ", ".join(f"{s//12:02d}:{(s%12)*5:02d} {resid_all[s]:+.2f}" for s in top))

# ---------- Q4 first bar after any pause (non-break) ----------
say("\n## Q4 「休止明けの最初の足は正」プラセボ（ET 平日・直前 ≥12 本 flat・ET 18 時を除く）")
# run length of flats ending at i-1
run = np.zeros(len(flat), dtype=np.int32)
for i in range(1, len(flat)):
    run[i] = run[i - 1] + 1 if flat[i - 1] else 0
cand = (run >= 12) & (~flat) & (wd_ny <= 4) & (h_ny != 18) & valid
# exclude Monday 00:00-? weekly open is Sunday 18:00 ET (wd 6) so fine; but Sunday open could be delayed to Monday for holidays -> those are 'pauses' too (keep, they are non-break reopens)
iP = np.where(cand)[0]; yP = yr_ny[iP]
say(f"- 候補 {len(iP)} 本。ET 時別分布: " + " ".join(f"{hh}:{(h_ny[iP]==hh).sum()}" for hh in range(24) if (h_ny[iP]==hh).sum() > 0))
say(f"- 最初の非 flat 足のリターン: " + wrow(r_bp[iP], yP, True))
# subset: pauses ending 18:00-ish excluded already; split by run length
for lo, hi in ((12, 24), (24, 288), (288, 10**9)):
    mm_ = (run[iP] >= lo) & (run[iP] < hi)
    say(f"  - 休止 {lo}〜{hi} 本: " + wrow(r_bp[iP][mm_], yP[mm_], True))
Q4_out = ms(r_bp[iP][yP >= 2021])

# ---------- Q5 structure sweep ----------
say("\n## Q5 構造の掃引")
say("- ET 曜日別 G_0: " + " ｜ ".join(f"{['月','火','水','木'][d]} " + wrow(G[0][wdG == d], yG[wdG == d]) for d in range(4)))
# weekly open: Friday 16:55 ET close -> Sunday 18:05 ET
iS = np.where((wd_ny == 6) & (h_ny == 18) & (m_ny == 0))[0]
refS = idx_at(ts[iS] - 589 * 300)   # Friday 16:55 ET bar is 49h05m earlier
okS = refS >= 0; iS = iS[okS]; refS = refS[okS]
gW = (lc[iS] - lc[refS]) * 1e4; yS = yr_ny[iS]
fri_ok = (h_ny[refS] == 16) & (m_ny[refS] == 55)
say(f"- 週次オープン（金 16:55 → 日 18:05 ET・49h・参照整合 {fri_ok.mean()*100:.0f}%）: " + wrow(gW[fri_ok], yS[fri_ok], True) + "  ← 1 時間ブレイクの G_0 と比較（情報凝縮なら時間に比例して大きい筈）")
say("- 年別 符号・t（G_0 / G_30 / G_60）:")
pos = {0: 0, 30: 0, 60: 0}; nyears = 0
for y in range(2010, 2027):
    w = yG == y
    if w.sum() < 20: continue
    nyears += 1
    cells = []
    for k in (0, 30, 60):
        m, se, t, n = ms(G[k][w]); cells.append(f"{m:+.2f} (t{t:+.1f})"); pos[k] += int(m > 0)
    say(f"  - {y}: n{w.sum()} " + " / ".join(cells))
say(f"  → 正の年数 G_0 {pos[0]}/{nyears}・G_30 {pos[30]}/{nyears}・G_60 {pos[60]}/{nyears}")
# month-block bootstrap, out-of-sample
wo = yG >= 2021; mon = dG[wo] // 100
def block_boot(x, blocks, B=2000):
    ub = np.unique(blocks); idx = [np.where(blocks == u)[0] for u in ub]; out = np.empty(B)
    for bb in range(B):
        pick = rng.integers(0, len(ub), len(ub)); out[bb] = np.concatenate([x[idx[p]] for p in pick]).mean()
    return out
for k in (0, 30):
    bs = block_boot(G[k][wo], mon)
    say(f"- 外 月ブロック bootstrap G_{k}: 95% CI [{np.quantile(bs,0.025):+.2f}, {np.quantile(bs,0.975):+.2f}] bp・P(≤0) {(bs<=0).mean():.3f}")
wr = (yG >= 2024) & (yG <= 2025)
say(f"- 近年 LOYO 2026H1 除去（2024-25）: G_0 {fmt(G[0][wr])}・G_30 {fmt(G[30][wr])}；2026H1 のみ: G_0 {fmt(G[0][yG==2026])}・G_30 {fmt(G[30][yG==2026])}")
# half-year series out-of-sample
say("- 半期別 G_0（外）: " + " ".join(f"{y}H{hf}:{G[0][(yG==y)&(((dG//100)%100>6)==(hf==2))].mean():+.1f}" for y in range(2021, 2027) for hf in (1, 2) if ((yG==y)&(((dG//100)%100>6)==(hf==2))).sum() > 20))

# ---------- Q6 US500 placebo ----------
say("\n## Q6 市場横断（記述）: US500 bid 18:00 ET 再開足")
try:
    zu = np.load(os.path.join(MAC, "US500_m5_close.npz")); tsu = zu["ts"].astype(np.int64); clu = zu["close"].astype(float); lcu = np.log(clu)
    ru = np.zeros(len(lcu)); ru[1:] = np.diff(lcu); fu = ru == 0
    tu = pd.to_datetime(tsu, unit="s", utc=True).tz_convert("America/New_York"); hu = tu.hour.to_numpy(); mu = tu.minute.to_numpy(); wu = tu.weekday.to_numpy(); yu = tu.year.to_numpy()
    say(f"- US500 npz {len(tsu)} 本 {tu[0]}〜{tu[-1]}（⑩）。ET 時別 flat（平日）: " + " ".join(f"{hh}:{fu[(wu<=4)&(hu==hh)].mean()*100:.0f}%" for hh in range(14, 24)))
    def idx_u(target):
        j = np.clip(np.searchsorted(tsu, target), 0, len(tsu) - 1); return np.where(tsu[j] == target, j, -1)
    iU = np.where((wu <= 3) & (hu == 18) & (mu == 0))[0]
    BRU = np.column_stack([idx_u(tsu[iU] - 300 * j) for j in range(1, 13)]); RU = {k: idx_u(tsu[iU] - (65 + k) * 60) for k in (0, 30, 60)}
    pu = np.all(BRU >= 0, axis=1) & np.all(np.column_stack([RU[k] for k in RU]) >= 0, axis=1)
    iU = iU[pu]; BRU = BRU[pu]; RU = {k: RU[k][pu] for k in RU}
    cu = np.all(fu[BRU], axis=1); iU = iU[cu]; RU = {k: RU[k][cu] for k in RU}; yU = yu[iU]
    WU = {"在2012-20": (2012, 2020), "外2021-26": (2021, 2026), "近年2024-26": (2024, 2026)}
    for k in (0, 30, 60):
        gu = (lcu[iU] - lcu[RU[k]]) * 1e4
        say(f"- US500 G_{k}: " + " ｜ ".join(f"{wn} {fmt(gu[(yU>=a)&(yU<=b)], k==0)}" for wn, (a, b) in WU.items()) + f"（クリーン日 {cu.sum()}/{len(cu)}）")
except Exception as e:
    say(f"- US500 読取失敗: {e}")

# ---------- Q7 capturability ----------
say("\n## Q7 受け取れるか: net = G_k − 往復スプレッド bp − swap bp/日（16:55 or 16:25 ET 買い → 18:05 ET 売り）")
P_ref = cl[REF[0]]
CAP = {}
for k in (0, 30):
    for rt_usd in (0.42, 0.84):
        for swap in (0.0, 1.0, 2.0):
            net = G[k] - rt_usd / P_ref * 1e4 - swap
            cells = []
            for wn, (a, b) in W.items():
                w = (yG >= a) & (yG <= b); m, se, t, n = ms(net[w]); sr = m / net[w].std(ddof=1) * math.sqrt(250)
                cells.append(f"{wn} {m:+.2f} bp (t{t:+.1f}, SR {sr:+.2f})"); CAP[(k, rt_usd, swap, wn)] = (m, t)
            say(f"- G_{k:<2} 往復 {rt_usd:.2f} USD・swap {swap:.0f} bp: " + " ｜ ".join(cells))
say("- （swap の口座仕様＝swap_long／3 倍日／1 時間跨ぎへの適用 は needs data。2023-26 の USD 金利−リース料 ≈ 4〜5%/年 ≈ 1.6〜2.0 bp/日 が cycle16 の見積り）")

# ---------- verdict ----------
say("\n## 判定（事前固定の規則）")
g0o = Q1_out[0][0]; g30 = Q1_out[30]; g60 = Q1_out[60]; z_out = Z3["外2021-26H1"]
b1 = (g30[0] < g0o / 3) or (g30[2] < 2)
b2 = z_out < 2
b3 = (np.isfinite(BIAS)) and (BIAS >= 0.5 * g0o)
b4 = (Q4_out[3] >= 30) and (Q4_out[0] >= g0o / 2) and (Q4_out[2] >= 3)
s_all = (g30[2] >= 3) and (g60[2] >= 3) and (g30[0] >= 2 / 3 * g0o) and (g60[0] >= 2 / 3 * g0o) and (z_out >= 3) and \
        (np.isfinite(BIAS) and abs(BIAS) < 0.2 * g0o) and ((Q4_out[3] < 30) or (Q4_out[0] < g0o / 4)) and (pos[30] >= 12)
say(f"- 外 G_0 {g0o:+.2f}・G_30 {g30[0]:+.2f} (t{g30[2]:+.1f})・G_60 {g60[0]:+.2f} (t{g60[2]:+.1f})；Q3 z {z_out:+.1f}；実口座 bias {BIAS:+.3f} bp；Q4 外 {Q4_out[0]:+.2f} (t{Q4_out[2]:+.1f}, n{Q4_out[3]})；年別 G_30 正 {pos[30]}/{nyears}")
say(f"- B1 {b1}・B2 {b2}・B3 {b3}・B4 {b4} → " + ("**broken**" if (b1 or b2 or b3 or b4) else ("**survived**" if s_all else "**inconclusive**")))
cap = CAP[(0, 0.42, 2.0, "外2021-26H1")]
say(f"- 受け取れるか（外・往復 0.42 USD・swap 2 bp）: net {cap[0]:+.2f} bp (t{cap[1]:+.1f}) → " + ("受け取れる" if cap[1] >= 2 else "**受け取れない（小売コスト）**"))
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
