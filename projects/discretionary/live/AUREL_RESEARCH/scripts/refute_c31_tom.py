# -*- coding: utf-8 -*-
"""
[REFUTE] 2026-11-10 反証レーン — 対象: cycle31 (15:50) の残存弱信号
  W1「H_TOM／H_DASH／H_PRE の 3 仮説とも点推定が 3 窓（在・外・近年）で同符号（正・+4〜+16 bp/日）＝『小さい効果が有る』と
      『無い』を分離できない（文献サイズと矛盾しない）」＋ 在 TOM の z_pl +2.32（プラセボ 14 本比）
  W2（事後・補足 b）「月初 1 営業日（k=+1）が 3 窓とも最大級（年FE 在 +14.8 t1.53 順位 3／外 +33.8 t2.25 順位 1／近年 +28.8）・
      年別 正 15/20・月曜より火〜金で大きい（外 +12 vs +45）＝週末ギャップの別名ではない」→ 前向き 1 セル
      「k=+1・火〜金のみ・年FE・t≥2・≥36 か月」（外 +34 が続けば t≈2.2）
  W3「本番 TOM 建玉 Δμ +0.024／+0.026／+0.024R（3 窓同符号）」
  W4「文献の TOM は同期間の US500 にも無い（在 −2.8 bp/日）」（補足 c）

規則（結果を見る前に書く・変えない）:
  R0 再現: 研究レーンと同じ定義で df を再構築し、TOM 在 Δ +8.5 (t 1.69)／外 +3.9 (t 0.45)、k=+1 年FE 在 +14.8 (t 1.53)／
      外 +33.8 (t 2.25) を再現（|ΔΔ| ≤ 0.3 bp・|Δt| ≤ 0.05）。合わなければ以降の判定は保留。
  R1 W1 の分解: TOM から k=+1 を除いた集合 {0,+2,+3} の Δ、DASH の post を {+2,+3} に替えた D、PRE と TOM の重なり率を
      在／外／外a 2021-23／外b 2024-26H1 で印字。k=+1 の寄与率（TOM 超過和に占める k=+1 の和）。
      **判定 W1**: broken = 外で TOM−{+1} の Δ ≤ 0 ∧ DASH' の D ≤ 0（「3 仮説 3 窓同符号」は k=+1 の 1 セルの別名）。
                   survived = TOM−{+1} の Δ > 0 が 在・外a・外b の 3 つすべて。それ以外 inconclusive。
  R2 z_pl の基準汚染（記述）: 研究レーンのプラセボ Δ_s は「ずらした集合 vs 残り」で、残りに TOM 日を含む。TOM 効果が有るなら
      プラセボ Δ は機械的に −(Δ_TOM·n_TOM/n_rest) ≈ −2 bp 偏る。残りから TOM 日を除いたプラセボで z_pl を取り直す。
  R3 窓の独立性（記述）: 近年 ⊂ 外 なので「3 窓同符号」は 2 窓。外を 外a 2021-23／外b 2024-26H1 に分け、さらに 2021-25（ex-2026H1）
      で TOM／DASH／PRE／k=+1 を印字。
  R4 W2 k=+1（主）:
      (a) 月内置換帰無（2000 回・seed 20261110）: 各 (年,月) 内で k ラベルを置換（月の営業日数・年組成を保存・月内位置だけ壊す）。
          年FE 後の r で 12 セル k∈[−8..+3] の Δ・Welch t を 在／外／外a／外b で計算。
          統計量 S = max_k [ 1{Δ_在>0 ∧ Δ_外a>0 ∧ Δ_外b>0} · |t_外| ]（「3 つの互いに素な窓で同符号 ∧ 外で最大級」の同時帰無）。
          p_joint = P(S_null ≥ S_obs)。併せて p_fw(max|t_外|)・P(いずれかのセルが 3 窓同符号)。
      (b) 外 k=+1 の分布: 中央値・両側トリム 5%/10% 平均・正の割合（二項 p）・上位 3 日の Σ 寄与・sd。
      (c) ex-2026H1（2021-25）の t・LOYO（2021..2026 を 1 年ずつ抜く）の min t・1 月を除いた t。
      (d) 暦ギャップ: k=+1 を「前営業日との暦日差 1（平日・祝日なし）」vs「≥2（週末・祝日跨ぎ）」で分け、火〜金のうち祝日跨ぎ
          （1/2・レイバーデー翌日等）の本数と平均を印字（「火〜金 > 月曜」が祝日跨ぎの別名かの検査）。
      **判定 W2**: survived = p_joint ≤ 0.05 ∧ ex-2026H1 t ≥ 1.5 ∧ トリム 10% 平均 ≥ 0.5×生平均 ∧ 上位 3 日寄与 ≤ 50%。
                   broken = p_joint > 0.20 ∨ 上位 3 日寄与 > 60% ∨ 正の割合 ≤ 55% ∨ ex-2026H1 t < 1.0。それ以外 inconclusive。
  R5 機構の部分集合（記述・事後と明記）: k=+1 を 曜日（月 vs 火〜金・Welch t）・月（1 月 vs 他／受渡月 2,4,6,8,10,12 の初日
      = FND 翌営業日 vs 他）・金の年方向（年リターン >0 vs ≤0）で分ける。US500 の k=+1（年FE・曜日別）を同じ定義で印字。
  R6 前向きセルの設計検査: k=+1 火〜金の r の sd（在／外）と 36 か月あたりの本数（実測比率）から、t≥2 に要る平均
      （検出力 50% = 2·sd/√n、80% = 2.84·sd/√n）を印字し、在 火〜金平均・2021-25 火〜金平均・外 火〜金平均と並べる。
      全 k=+1（月曜込み・n≈36）版も併記。**W2 前向きセル**: 要求平均(50%) > 在 平均 なら「設計上 2024-26 水準の継続だけが通る」。
  R7 別の在/外分割: (2010-15|2016-26H1)・(2010-17|2018-26H1)・(偶数年|奇数年) で TOM（研究レーン規則 在 t≥2 ∧ 外 t≥1.5）と
      k=+1 年FE（同規則）の PASS 数を印字。
  R8 W3 本番 Δμ: TOM 建玉を BUY／SELL で分け 在／外／外a／外b の Δμ・建玉日クラスタ t。k=+1 建玉のみの Δμ も。
      **判定 W3**: 「drift の別名」= 外で BUY Δμ > 0 ∧ SELL Δμ ≤ 0。記述（ゲート ㉛ で既に走らせない水準）。
  R9 H_PRE（記述）: 休日種別ごとの平均（在／外）・上位 3 日寄与・両側トリム 10%。
  費用倍: 前向きセル（k=+1 ロング 1 日）の粗 +15（在）／+34（外）bp vs 往復 spread ≈1 bp＋swap 1〜2 bp → c=3／6 bp で net を印字。
  D2: 窓別・16 年一括は判定に使わない。bid のみ・Dukascopy。
入力: data/macro/XAU_m5_close.npz・data/macro/US500_m5_close.npz・data/refute_c4_scan_paths_2010_2026.json のみ。
      scan 無し・M5 読込なし・MT5 無し・外部通信無し。
出力: data/refute_c31_tom.md・data/refute_c31_tom_run.log。
"""
import os, sys, json, math, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c31_tom.md")
rng = np.random.default_rng(20261110); T0 = time.time(); L = []
NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c31] 月替わり（TOM）・月初 1 営業日（k=+1）・本番 Δμ — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c31_tom.py)")

# ---------------- 暦（c31 と同一・コピー） ----------------
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
HOL = {}; HOLSET = set()
for y in range(2009, 2028):
    items = [("NewYear", observed(dt.date(y, 1, 1), sat_to_fri=False)), ("MLK", nth_weekday(y, 1, 0, 3)), ("Presidents", nth_weekday(y, 2, 0, 3)),
             ("GoodFri", easter(y) - dt.timedelta(days=2)), ("Memorial", last_weekday(y, 5, 0)), ("July4", observed(dt.date(y, 7, 4))),
             ("Labor", nth_weekday(y, 9, 0, 1)), ("Thanks", nth_weekday(y, 11, 3, 4)), ("Xmas", observed(dt.date(y, 12, 25)))] + \
            ([("Juneteenth", observed(dt.date(y, 6, 19)))] if y >= 2022 else [])
    for nm, h in items:
        if h is not None: HOL[h] = nm; HOLSET.add(h)
d0 = dt.date(2009, 11, 1); d1 = dt.date(2026, 12, 31)
ALLD = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]
BDAYS = [d for d in ALLD if d.weekday() < 5 and d not in HOLSET]
BORD = np.array([d.toordinal() for d in BDAYS]); BIDX = {o: i for i, o in enumerate(BORD)}
K = {}
for (y, m) in sorted({(d.year, d.month) for d in BDAYS}):
    bm = [d for d in BDAYS if d.year == y and d.month == m]
    for j, d in enumerate(bm): K[d.toordinal()] = (j - (len(bm) - 1), j + 1)
def kpos(o):
    ke, ks = K[o]; return ke if ke <= 0 and ks > 3 else ks
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

def build_daily(sym):
    z = np.load(os.path.join(DATA, "macro", f"{sym}_m5_close.npz")); TS = z["ts"].astype(np.int64); P = z["close"].astype(float)
    flat = np.r_[True, P[1:] == P[:-1]]
    et_all = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
    sess = (et_all + pd.Timedelta(hours=6)).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat; so = sord[keep]; pc = P[keep]
    u, last_idx = np.unique(so[::-1], return_index=True); last_idx = len(so) - 1 - last_idx
    cbd = dict(zip(u.tolist(), pc[last_idx].tolist()))
    rows = []; prev = None
    for d in BDAYS:
        o = d.toordinal()
        if o not in cbd: continue
        if prev is not None:
            nxt = d + dt.timedelta(days=1); nxt3 = d + dt.timedelta(days=3)
            ph = (nxt in HOLSET) or (d.weekday() == 4 and nxt3 in HOLSET)
            phn = HOL.get(nxt) if nxt in HOLSET else (HOL.get(nxt3) if (d.weekday() == 4 and nxt3 in HOLSET) else "")
            rows.append((o, d.year, d.month, d.weekday(), kpos(o), math.log(cbd[o] / cbd[prev]) * 1e4, o in NFP, ph, phn, o - prev))
        prev = o
    df = pd.DataFrame(rows, columns=["ord", "year", "month", "wd", "k", "r", "nfp", "prehol", "holname", "gap"])
    df = df[(df.year >= 2010) & (df.ord <= dt.date(2026, 6, 30).toordinal())].reset_index(drop=True)
    df["ym"] = df.year * 100 + df.month
    return df

df = build_daily("XAU")
say(f"- XAU 営業日リターン {len(df)} 日・sd {df.r.std():.0f} bp・NFP {df.nfp.sum()}・休日前 {df.prehol.sum()}（c31: 4148・104・189・151）")

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return (a.mean() - b.mean()) / se, se
def yfe(d_): return d_.assign(r=d_.r - d_.groupby("year").r.transform("mean"))
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "外a 2021-23": (2021, 2023), "外b 2024-26H1": (2024, 2026), "2021-25 (ex-26H1)": (2021, 2025)}
def W(d_, name): y0, y1 = WIN[name]; return d_[(d_.year >= y0) & (d_.year <= y1)].reset_index(drop=True)
TOMK = {0, 1, 2, 3}
def cell(d_, m):
    m = np.asarray(m, bool); t, se = welch(d_.r[m], d_.r[~m]); return d_.r[m].mean() - d_.r[~m].mean(), t, se, int(m.sum())

# ---------------- R0 再現 ----------------
say("\n## R0 再現")
rep = {}
for wn in ["在 2010-20", "外 2021-26H1"]:
    d_ = W(df, wn); dl, t, se, n = cell(d_, d_.k.isin(TOMK)); rep[("TOM", wn)] = (dl, t)
    dy = yfe(d_); dl1, t1, se1, n1 = cell(dy, dy.k == 1); rep[("k1", wn)] = (dl1, t1)
    say(f"- {wn}: TOM Δ {dl:+.1f} (t {t:+.2f}, n {n})・k=+1 年FE Δ {dl1:+.1f} (t {t1:+.2f}, n {n1})")
ok = abs(rep[("TOM", "在 2010-20")][0] - 8.5) <= 0.3 and abs(rep[("TOM", "外 2021-26H1")][0] - 3.9) <= 0.3 and \
     abs(rep[("k1", "外 2021-26H1")][0] - 33.8) <= 0.3 and abs(rep[("k1", "在 2010-20")][0] - 14.8) <= 0.3 and \
     abs(rep[("TOM", "在 2010-20")][1] - 1.69) <= 0.05 and abs(rep[("k1", "外 2021-26H1")][1] - 2.25) <= 0.05
say(f"- R0: {'再現 OK' if ok else '再現 NG（以降保留）'}")

# ---------------- R1 W1 の分解 ----------------
say("\n## R1 W1 の分解（k=+1 を除く）")
R1 = {}
for wn in ["在 2010-20", "外 2021-26H1", "外a 2021-23", "外b 2024-26H1", "2021-25 (ex-26H1)"]:
    d_ = W(df, wn)
    dlT, tT, _, _ = cell(d_, d_.k.isin(TOMK)); dlX, tX, _, nX = cell(d_, d_.k.isin({0, 2, 3}))
    pre = d_.k.between(-7, -2).values; post = d_.k.isin([1, 2, 3]).values; post2 = d_.k.isin([2, 3]).values
    tD, _ = welch(d_.r[post], d_.r[pre]); D = d_.r[post].mean() - d_.r[pre].mean()
    tD2, _ = welch(d_.r[post2], d_.r[pre]); D2 = d_.r[post2].mean() - d_.r[pre].mean()
    # k=+1 の寄与: TOM 超過和 Σ_{TOM}(r − mean_rest) のうち k=+1 分
    rest_mean = d_.r[~d_.k.isin(TOMK)].mean(); exc = (d_.r[d_.k.isin(TOMK)] - rest_mean); exc1 = (d_.r[d_.k == 1] - rest_mean)
    share1 = exc1.sum() / exc.sum() if abs(exc.sum()) > 1e-9 else float("nan")
    ovl = d_[d_.prehol].k.isin(TOMK).mean()
    dlP, tP, _, nP = cell(d_, d_.prehol)
    R1[wn] = dict(dlX=dlX, D2=D2)
    say(f"- {wn}: TOM Δ {dlT:+.1f} (t {tT:+.2f}) → TOM−{{+1}} Δ {dlX:+.1f} (t {tX:+.2f}, n {nX})・k=+1 の寄与 {share1*100:+.0f}%；"
        f"DASH D {D:+.1f} (t {tD:+.2f}) → post={{+2,+3}} D' {D2:+.1f} (t {tD2:+.2f})；PRE Δ {dlP:+.1f} (t {tP:+.2f}, n {nP})・PRE∩TOM 率 {ovl*100:.0f}%")
w1_broken = R1["外 2021-26H1"]["dlX"] <= 0 and R1["外 2021-26H1"]["D2"] <= 0
w1_surv = all(R1[w]["dlX"] > 0 for w in ["在 2010-20", "外a 2021-23", "外b 2024-26H1"])
W1V = "broken" if w1_broken else ("survived" if w1_surv else "inconclusive")
say(f"- **判定 W1**: {W1V}")

# ---------------- R2 z_pl 基準汚染 ----------------
say("\n## R2 在 TOM の z_pl（プラセボの残りから TOM 日を除く）")
def tom_shift_mask(d_, s):
    oset = set(d_.ord[d_.k.isin(TOMK)].tolist()); sh = set()
    for o in oset:
        i = BIDX.get(o)
        if i is not None and 0 <= i + s < len(BORD): sh.add(int(BORD[i + s]))
    return d_.ord.isin(sh).values
for wn in ["在 2010-20", "外 2021-26H1"]:
    d_ = W(df, wn); mT = d_.k.isin(TOMK).values; dl = d_.r[mT].mean() - d_.r[~mT].mean()
    pl_lane, pl_clean = [], []
    for s in list(range(-10, -3)) + list(range(4, 11)):
        ms = tom_shift_mask(d_, s)
        if ms.sum() < 20: continue
        pl_lane.append(d_.r[ms].mean() - d_.r[~ms].mean())
        rest = ~ms & ~mT; pl_clean.append(d_.r[ms].mean() - d_.r[rest].mean())
    pl_lane = np.array(pl_lane); pl_clean = np.array(pl_clean)
    z1 = (dl - pl_lane.mean()) / pl_lane.std(ddof=1); z2 = (dl - pl_clean.mean()) / pl_clean.std(ddof=1)
    nT = mT.sum(); nR = (~mT).sum()
    say(f"- {wn}: Δ_TOM {dl:+.1f}・研究レーン流 プラセボ平均 {pl_lane.mean():+.1f} sd {pl_lane.std(ddof=1):.1f} z_pl {z1:+.2f}"
        f" → TOM 日を残りから除いたプラセボ平均 {pl_clean.mean():+.1f} sd {pl_clean.std(ddof=1):.1f} **z_pl' {z2:+.2f}**"
        f"（機械的偏り予測 −Δ·n_TOM/n_rest = {-dl*nT/nR:+.1f}）")

# ---------------- R3 窓の独立性 ----------------
say("\n## R3 互いに素な窓（年FE なし・生）")
for wn in ["在 2010-20", "外a 2021-23", "外b 2024-26H1", "2021-25 (ex-26H1)"]:
    d_ = W(df, wn); dlT, tT, _, _ = cell(d_, d_.k.isin(TOMK))
    pre = d_.k.between(-7, -2).values; post = d_.k.isin([1, 2, 3]).values; tD, _ = welch(d_.r[post], d_.r[pre]); D = d_.r[post].mean() - d_.r[pre].mean()
    dlP, tP, _, nP = cell(d_, d_.prehol); dy = yfe(d_); dl1, t1, _, n1 = cell(dy, dy.k == 1)
    say(f"- {wn}: TOM {dlT:+.1f} (t {tT:+.2f})・DASH {D:+.1f} (t {tD:+.2f})・PRE {dlP:+.1f} (t {tP:+.2f}, n {nP})・k=+1 年FE {dl1:+.1f} (t {t1:+.2f}, n {n1})")

# ---------------- R4 W2 k=+1 ----------------
say("\n## R4 k=+1（W2・主）")
KS = list(range(-8, 4)); KIDX = {k: i for i, k in enumerate(KS)}
def cells_fast(r, kv):
    """12 セルの (Δ, t) を bincount で。kv: k 値配列・r: 年FE 後。"""
    lab = np.array([KIDX.get(int(k), 12) for k in kv]); n_all = len(r); s_all = r.sum(); q_all = (r * r).sum()
    cnt = np.bincount(lab, minlength=13).astype(float); s = np.bincount(lab, weights=r, minlength=13); q = np.bincount(lab, weights=r * r, minlength=13)
    out = np.zeros((12, 2))
    for i in range(12):
        na = cnt[i]; nb = n_all - na
        if na < 2 or nb < 2: out[i] = (np.nan, np.nan); continue
        ma = s[i] / na; mb = (s_all - s[i]) / nb
        va = (q[i] - na * ma * ma) / (na - 1); vb = ((q_all - q[i]) - nb * mb * mb) / (nb - 1)
        se = math.sqrt(va / na + vb / nb); out[i] = (ma - mb, (ma - mb) / se)
    return out
dfy = yfe(df)  # 年FE は全期間の年平均（窓の年平均と同じ）
WD4 = {w: W(dfy, w) for w in ["在 2010-20", "外 2021-26H1", "外a 2021-23", "外b 2024-26H1"]}
obs = {w: cells_fast(WD4[w].r.values, WD4[w].k.values) for w in WD4}
def S_stat(c):
    sgn = (c["在 2010-20"][:, 0] > 0) & (c["外a 2021-23"][:, 0] > 0) & (c["外b 2024-26H1"][:, 0] > 0)
    return np.nanmax(np.where(sgn, np.abs(c["外 2021-26H1"][:, 1]), 0.0)), sgn.any(), np.nanmax(np.abs(c["外 2021-26H1"][:, 1]))
S_obs, any_obs, mxt_obs = S_stat(obs)
i1 = KIDX[1]
say(f"- 観測（年FE）: k=+1 Δ 在 {obs['在 2010-20'][i1,0]:+.1f} (t {obs['在 2010-20'][i1,1]:+.2f})／外 {obs['外 2021-26H1'][i1,0]:+.1f} (t {obs['外 2021-26H1'][i1,1]:+.2f})／"
    f"外a {obs['外a 2021-23'][i1,0]:+.1f} (t {obs['外a 2021-23'][i1,1]:+.2f})／外b {obs['外b 2024-26H1'][i1,0]:+.1f} (t {obs['外b 2024-26H1'][i1,1]:+.2f})")
sgn_cells = [k for k in KS if obs["在 2010-20"][KIDX[k], 0] > 0 and obs["外a 2021-23"][KIDX[k], 0] > 0 and obs["外b 2024-26H1"][KIDX[k], 0] > 0]
say(f"- 3 窓（在・外a・外b）同符号 正のセル: {sgn_cells}・S_obs {S_obs:.2f}・max|t_外| {mxt_obs:.2f}")
# 月内置換
groups = {w: [np.flatnonzero(WD4[w].ym.values == g) for g in np.unique(WD4[w].ym.values)] for w in WD4}
S_null = np.zeros(NPERM); any_null = np.zeros(NPERM, bool); mxt_null = np.zeros(NPERM); t1_null = np.zeros(NPERM)
for p in range(NPERM):
    c = {}
    for w in WD4:
        kv = WD4[w].k.values.copy()
        for g in groups[w]: kv[g] = kv[g][rng.permutation(len(g))]
        c[w] = cells_fast(WD4[w].r.values, kv)
    S_null[p], any_null[p], mxt_null[p] = S_stat(c); t1_null[p] = c["外 2021-26H1"][i1, 1]
p_joint = (S_null >= S_obs).mean(); p_any = any_null.mean(); p_fw = (mxt_null >= abs(obs["外 2021-26H1"][i1, 1])).mean()
p_single = (np.abs(t1_null) >= abs(obs["外 2021-26H1"][i1, 1])).mean()
say(f"- (a) 月内置換 {NPERM} 回: **p_joint {p_joint:.3f}**（帰無 S 中央値 {np.median(S_null):.2f}・95% 点 {np.quantile(S_null,0.95):.2f}）・"
    f"P(いずれかのセルが 3 窓同符号 正) {p_any:.3f}・p_fw(max|t_外| ≥ {abs(obs['外 2021-26H1'][i1,1]):.2f}) {p_fw:.3f}（c31b 全体置換 0.276）・"
    f"単セル k=+1 の |t_外| 両側 p {p_single:.3f}")
# (b) 分布
dO = WD4["外 2021-26H1"]; r1 = dO.r[dO.k == 1].values; rr = dO.r[dO.k != 1].values
def trim_mean(x, f):
    x = np.sort(x); c = int(math.floor(len(x) * f)); return x[c:len(x) - c].mean() if len(x) - 2 * c > 0 else float("nan")
raw = r1.mean() - rr.mean(); tr5 = trim_mean(r1, 0.05) - trim_mean(rr, 0.05); tr10 = trim_mean(r1, 0.10) - trim_mean(rr, 0.10)
med = np.median(r1) - np.median(rr); pos = (r1 > 0).mean(); npos = int((r1 > 0).sum())
from math import comb
p_bin = sum(comb(len(r1), j) for j in range(npos, len(r1) + 1)) / 2 ** len(r1)
exc = r1 - rr.mean(); top3 = np.sort(exc)[-3:].sum() / exc.sum() if exc.sum() > 0 else float("nan")
say(f"- (b) 外 k=+1 n {len(r1)}: 生 Δ {raw:+.1f}・中央値差 {med:+.1f}・トリム 5% {tr5:+.1f}／10% {tr10:+.1f}・正 {pos*100:.0f}%（{npos}/{len(r1)}・二項 片側 p {p_bin:.3f}）・"
    f"上位 3 日の Σ 寄与 {top3*100:.0f}%・sd {r1.std(ddof=1):.0f} vs 他 {rr.std(ddof=1):.0f}・上位 3 日 {np.sort(r1)[-3:].round(0).tolist()}")
dI = WD4["在 2010-20"]; r1i = dI.r[dI.k == 1].values; rri = dI.r[dI.k != 1].values
exci = r1i - rri.mean(); top3i = np.sort(exci)[-3:].sum() / exci.sum() if exci.sum() > 0 else float("nan")
say(f"    在 k=+1 n {len(r1i)}: 生 Δ {r1i.mean()-rri.mean():+.1f}・中央値差 {np.median(r1i)-np.median(rri):+.1f}・トリム 10% {trim_mean(r1i,0.1)-trim_mean(rri,0.1):+.1f}・正 {(r1i>0).mean()*100:.0f}%・上位 3 日寄与 {top3i*100:.0f}%")
# (c) ex-2026H1・LOYO・ex-Jan
dE = W(dfy, "2021-25 (ex-26H1)"); dlE, tE, _, nE = cell(dE, dE.k == 1)
loyo = []
for y in range(2021, 2027):
    d_ = dO[dO.year != y]; dl, t, _, n = cell(d_, d_.k == 1); loyo.append((y, dl, t))
dJ = dO[dO.month != 1]; dlJ, tJ, _, nJ = cell(dJ, dJ.k == 1)
say(f"- (c) ex-2026H1 (2021-25) k=+1 Δ {dlE:+.1f} (t {tE:+.2f}, n {nE})・LOYO: " + " ".join(f"−{y}:{dl:+.0f}(t{t:+.1f})" for y, dl, t in loyo) +
    f"・min t {min(t for _,_,t in loyo):+.2f}・1 月除外 {dlJ:+.1f} (t {tJ:+.2f}, n {nJ})")
yrs = sorted(dO.year.unique()); say("    年別 k=+1 平均（外・年FE）: " + " ".join(f"{y}:{dO[(dO.year==y)&(dO.k==1)].r.mean():+.0f}(n{int(((dO.year==y)&(dO.k==1)).sum())})" for y in yrs))
# (d) 暦ギャップ
for wn in ["在 2010-20", "外 2021-26H1"]:
    d_ = WD4[wn]; k1 = d_[d_.k == 1]
    plain = k1[k1.gap == 1]; span = k1[k1.gap >= 2]; mon = k1[k1.wd == 0]; tf = k1[k1.wd != 0]; tf_span = tf[tf.gap >= 2]; tf_plain = tf[tf.gap == 1]
    tw, _ = welch(tf.r, mon.r) if len(mon) > 2 and len(tf) > 2 else (float("nan"), 0)
    say(f"- (d) {wn} k=+1: 暦日差 1（跨ぎなし）n {len(plain)} {plain.r.mean():+.0f} vs 跨ぎ ≥2 n {len(span)} {span.r.mean():+.0f}；"
        f"月曜 n {len(mon)} {mon.r.mean():+.0f} vs 火〜金 n {len(tf)} {tf.r.mean():+.0f}（差の Welch t {tw:+.2f}）；火〜金のうち 祝日跨ぎ n {len(tf_span)} {tf_span.r.mean() if len(tf_span) else float('nan'):+.0f}・跨ぎなし n {len(tf_plain)} {tf_plain.r.mean():+.0f}")
w2_surv = p_joint <= 0.05 and tE >= 1.5 and tr10 >= 0.5 * raw and top3 <= 0.5
w2_broken = p_joint > 0.20 or top3 > 0.6 or pos <= 0.55 or tE < 1.0
W2V = "broken" if w2_broken else ("survived" if w2_surv else "inconclusive")
say(f"- **判定 W2**: {W2V}（p_joint {p_joint:.3f}・ex-26H1 t {tE:+.2f}・トリム10/生 {tr10/raw if raw else float('nan'):.2f}・上位 3 日 {top3*100:.0f}%・正 {pos*100:.0f}%）")

# ---------------- R5 機構の部分集合（記述） ----------------
say("\n## R5 機構の部分集合（記述・事後）")
DELIV = {2, 4, 6, 8, 10, 12}
for wn in ["在 2010-20", "外 2021-26H1"]:
    d_ = WD4[wn]; k1 = d_[d_.k == 1]; rest_m = d_.r[d_.k != 1].mean()
    jan = k1[k1.month == 1]; nj = k1[k1.month != 1]; dv = k1[k1.month.isin(DELIV)]; nd = k1[~k1.month.isin(DELIV)]
    tdv, _ = welch(dv.r, nd.r)
    yret = df.groupby("year").r.sum(); up = k1[k1.year.map(yret) > 0]; dn = k1[k1.year.map(yret) <= 0]
    say(f"- {wn} k=+1（年FE・他の平均 {rest_m:+.1f}）: 1 月 n {len(jan)} {jan.r.mean():+.0f}／他月 n {len(nj)} {nj.r.mean():+.0f}；"
        f"受渡月初日（FND 翌営業日）n {len(dv)} {dv.r.mean():+.0f} vs 非受渡月 n {len(nd)} {nd.r.mean():+.0f}（Welch t {tdv:+.2f}）；"
        f"上昇年 n {len(up)} {up.r.mean():+.0f} vs 下落年 n {len(dn)} {dn.r.mean() if len(dn) else float('nan'):+.0f}")
    say("    月別 k=+1 平均: " + " ".join(f"{m}:{k1[k1.month==m].r.mean():+.0f}" for m in range(1, 13)))
# US500
try:
    du = build_daily("US500"); duy = yfe(du)
    for wn, (y0, y1) in [("在 2012-20", (2012, 2020)), ("外 2021-26H1", (2021, 2026))]:
        d_ = duy[(duy.year >= y0) & (duy.year <= y1)]; dl1, t1, _, n1 = cell(d_, d_.k == 1); k1 = d_[d_.k == 1]
        mon = k1[k1.wd == 0]; tf = k1[k1.wd != 0]
        say(f"- US500 {wn}: k=+1 年FE Δ {dl1:+.1f} (t {t1:+.2f}, n {n1})・月曜 n {len(mon)} {mon.r.mean():+.0f} vs 火〜金 n {len(tf)} {tf.r.mean():+.0f}")
except Exception as e:
    say(f"- US500: 読込失敗 {e}")

# ---------------- R6 前向きセルの設計検査 ----------------
say("\n## R6 前向きセル「k=+1・火〜金・年FE・t≥2・36 か月」の設計検査")
k1all = dfy[dfy.k == 1]; months_total = dfy.ym.nunique(); tf_all = k1all[k1all.wd != 0]
rate_tf = len(tf_all) / months_total; n36_tf = 36 * rate_tf; n36_all = 36 * len(k1all) / months_total
for lab, sub in [("火〜金", tf_all), ("全 k=+1", k1all)]:
    n36 = n36_tf if lab == "火〜金" else n36_all
    for wn in ["在 2010-20", "外 2021-26H1"]:
        y0, y1 = WIN[wn]; s = sub[(sub.year >= y0) & (sub.year <= y1)]; sd = s.r.std(ddof=1)
        req50 = 2 * sd / math.sqrt(n36); req80 = 2.84 * sd / math.sqrt(n36)
        say(f"- {lab}・{wn}: sd {sd:.0f} bp・36 か月の n ≈ {n36:.0f} → t≥2 に要る平均: 検出力 50% {req50:.0f} bp／80% {req80:.0f} bp（実測平均 {s.r.mean():+.0f}）")
tf_in = tf_all[(tf_all.year <= 2020)].r.mean(); tf_ex = tf_all[(tf_all.year >= 2021) & (tf_all.year <= 2025)].r.mean(); tf_out = tf_all[tf_all.year >= 2021].r.mean()
sd_tf_all = tf_all.r.std(ddof=1); req50_tf = 2 * sd_tf_all / math.sqrt(n36_tf)
say(f"- 火〜金 k=+1 平均: 在 {tf_in:+.0f}／2021-25 {tf_ex:+.0f}／外 {tf_out:+.0f} bp vs 要求(50%・全期間 sd {sd_tf_all:.0f}) {req50_tf:.0f} bp → "
    f"{'設計上 2024-26 水準の継続だけが通る' if req50_tf > tf_in else '在の大きさでも通り得る'}")
for c in [3.0, 6.0]:
    say(f"- 費用 c={c:.0f} bp（往復 spread ≈1＋swap 1〜2・{'倍' if c>3 else '基準'}）: net 在 {tf_in-c:+.0f}／2021-25 {tf_ex-c:+.0f}／外 {tf_out-c:+.0f} bp/件・年 12 件")

# ---------------- R7 別の在/外分割 ----------------
say("\n## R7 別の在/外分割（研究レーン規則 在 t≥2 ∧ 外 t≥1.5）")
splits = {"2010-15|2016-26H1": (lambda d_: d_.year <= 2015), "2010-17|2018-26H1": (lambda d_: d_.year <= 2017), "偶数年|奇数年": (lambda d_: d_.year % 2 == 0)}
npass_tom = npass_k1 = 0
for nm, fn in splits.items():
    a = df[fn(df)].reset_index(drop=True); b = df[~fn(df)].reset_index(drop=True)
    dA, tA, _, _ = cell(a, a.k.isin(TOMK)); dB, tB, _, _ = cell(b, b.k.isin(TOMK))
    ay = yfe(a); by = yfe(b); d1A, t1A, _, _ = cell(ay, ay.k == 1); d1B, t1B, _, _ = cell(by, by.k == 1)
    pT = dA > 0 and tA >= 2 and dB > 0 and tB >= 1.5; pK = d1A > 0 and t1A >= 2 and d1B > 0 and t1B >= 1.5
    npass_tom += pT; npass_k1 += pK
    say(f"- {nm}: TOM 在 {dA:+.1f} (t {tA:+.2f})／外 {dB:+.1f} (t {tB:+.2f}) {'PASS' if pT else 'fail'}；k=+1 在 {d1A:+.1f} (t {t1A:+.2f})／外 {d1B:+.1f} (t {t1B:+.2f}) {'PASS' if pK else 'fail'}")
say(f"- PASS 数: TOM {npass_tom}/3・k=+1 {npass_k1}/3")

# ---------------- R8 本番 Δμ（W3） ----------------
say("\n## R8 本番 TOM 建玉 Δμ の側別・窓別（W3）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"))); TR = d["trades"]
et_e = pd.to_datetime([t["entry_time"] for t in TR], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
eo = ((et_e + pd.Timedelta(hours=6)).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal())
kmap = dict(zip(df.ord.tolist(), df.k.tolist()))
ke = np.array([kmap.get(int(o), np.nan) for o in eo]); yr = np.array([t["year"] for t in TR]); side = np.array([t["side"] for t in TR])
R = np.array([t["R"] for t in TR]); risk = np.array([t["risk"] for t in TR]); ex = np.array([t["exit"] for t in TR]); ft = 0.1 / risk
Rs = np.where(ex == "TIME", R - ft, R + ft); inTOM = np.isin(ke, list(TOMK)); isK1 = ke == 1
def clus_t(x, g, y, h):
    """建玉日クラスタ t（2 群の平均差・クラスタ化 se）"""
    def cs(v, gg):
        s = pd.Series(v).groupby(gg).agg(["sum", "count"]); n = s["count"].sum(); m = s["sum"].sum() / n
        u = s["sum"] - m * s["count"]; return m, math.sqrt((u ** 2).sum()) / n
    ma, sa = cs(x, g); mb, sb = cs(y, h); return (ma - mb) / math.sqrt(sa ** 2 + sb ** 2)
W3 = {}
for wn in ["在 2010-20", "外 2021-26H1", "外a 2021-23", "外b 2024-26H1"]:
    y0, y1 = WIN[wn]; w = (yr >= y0) & (yr <= y1) & np.isfinite(ke)
    line = []
    for sd_ in ["ALL", "BUY", "SELL"]:
        ws = w if sd_ == "ALL" else (w & (side == sd_))
        a = Rs[ws & inTOM]; c = Rs[ws & ~inTOM]; ga = eo[ws & inTOM]; gc = eo[ws & ~inTOM]
        t, se = welch(a, c); tc = clus_t(a, ga, c, gc); dm = a.mean() - c.mean(); W3[(wn, sd_)] = dm
        line.append(f"{sd_} Δμ {dm:+.3f} (t {t:+.2f}・日クラスタ {tc:+.2f}・n {len(a)}:{len(c)})")
    a1 = Rs[w & isK1]; c1 = Rs[w & ~isK1]; t1, _ = welch(a1, c1)
    say(f"- {wn}: " + "／".join(line) + f"；k=+1 建玉のみ Δμ {a1.mean()-c1.mean():+.3f} (t {t1:+.2f}, n {len(a1)})")
drift_alias = W3[("外 2021-26H1", "BUY")] > 0 and W3[("外 2021-26H1", "SELL")] <= 0
say(f"- **W3 読み**: {'外は BUY のみ正・SELL ≤0 ＝ 日次ドリフトの別名' if drift_alias else '側対称（ドリフトの別名ではない）'}（ゲート ㉛ で走らせない水準は不変）")

# ---------------- R9 H_PRE（記述） ----------------
say("\n## R9 休日前（記述）")
for wn in ["在 2010-20", "外 2021-26H1"]:
    d_ = W(df, wn); ph = d_[d_.prehol]; rest_m = d_.r[~d_.prehol].mean()
    exc = ph.r.values - rest_m; top3 = np.sort(exc)[-3:].sum() / exc.sum() if exc.sum() > 0 else float("nan")
    tr = trim_mean(ph.r.values, 0.1) - trim_mean(d_.r[~d_.prehol].values, 0.1)
    byh = ph.groupby("holname").r.agg(["mean", "count"])
    say(f"- {wn}: 休日前 n {len(ph)} Δ {ph.r.mean()-rest_m:+.1f}・トリム 10% {tr:+.1f}・中央値差 {np.median(ph.r)-np.median(d_.r[~d_.prehol]):+.1f}・上位 3 日寄与 {top3*100:.0f}%・"
        + "種別: " + " ".join(f"{h}:{v['mean']-rest_m:+.0f}(n{int(v['count'])})" for h, v in byh.iterrows()))

# ---------------- 判定まとめ ----------------
say("\n## 判定（docstring の規則どおり）")
say(f"- W1（3 仮説 3 窓同符号）: **{W1V}**")
say(f"- W2（k=+1 が 3 窓で最大級・前向きセル）: **{W2V}**・前向きセル: {'設計上 2024-26 水準の継続だけが通る' if req50_tf > tf_in else '在の大きさでも通り得る'}")
say(f"- W3（本番 Δμ 3 窓同符号）: {'drift の別名' if drift_alias else '側対称'}（記述）")
say(f"- R0 {'OK' if ok else 'NG'}")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
