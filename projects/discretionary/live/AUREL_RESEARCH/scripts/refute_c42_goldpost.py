# -*- coding: utf-8 -*-
"""
[REFUTE c42] 対象 = cycle42 (2026-11-16 18:45) の唯一の生存正信号 W-POST
-------------------------------------------------------------------------
主張（研究レーン・事後記述・判定に使っていないが findings 末尾で「発表プール 1 セル」へ合流させた）:
  「金は FOMC 声明直後 30 分（J30 = 14:00→14:30 ET）の向きに、その後も続く」
   POST (14:30→16:00) ~ J30 : 在 2013-20 β +0.318 (HC1 t +3.12, MDE 0.20, n 62)
   NEXT (16:00→翌 10:00) ~ J30 : 在 β +0.651 (t +2.92, MDE 0.45)
   外 2021-26H1 : POST +0.202 (t 0.69, MDE 0.59) / NEXT +0.176 (t 0.53) = 同符号だが分離不能
   将来の前向きセル案: 発表プール（NFP+FOMC+CPI ≥300）で β>0 ∧ HC1 t≥2 ∧ 外 同符号 t≥1.5

反証レーンの役割（補遺 C）= 文章でなくコードで壊す。**数字を見る前に**以下を固定する。

攻撃（すべて事前固定・XAU を主・US500 を対照市場）:
 R0 独立再現: 自前の窓コードで β/HC1 t/HC3 t/n を出す。再現しない → broken(再現不能)。
 R1 ★対照日ベースライン（本命の殺し手）: **同じ回帰を声明日でない平日（声明±1・臨時・NFP を除く）で走らせる**。
    金の 14:00→14:30 → 14:30→16:00 の継続が普段の日にも同じだけあるなら、
    これは「FOMC の情報伝播」ではなく **金の NY 午後の素の自己相関** である＝FOMC 仮説は broken。
    判定: β_ctrl の t≥2 かつ |β_F − β_ctrl| が交互作用 t<2（プール回帰 POST ~ J30 + F + J30:F）→ **FOMC 固有でない**。
 R2 日付シフト・プラセボ: 声明日 ±7/14/21/28 日（同曜日・対照日に落ちるものだけ）8 集合で β。
    観測 β が 8 集合の分布の内側 → broken。
 R3 信号のランダム化（プラセボ）: 声明日の中で J30 を 2000 回シャッフル → β の両側 p・帰無 sd。
 R4 影響点・頑健性: HC3・最大 |dfbeta| 1 点除去・leave-one-year-out・|J30| 上位 2 日除去・
    Theil–Sen・符号一致率（二項検定）・5% winsorize。1 点/1 年で t<2 に落ちる → broken(fragile)。
 R5 別の在外分割: 2013-16／2017-20／2021-23／2024-26H1、OOS 境界を 2018/2019/2020/2021 に動かす、
    声明日の奇数/偶数番目で分割。符号が割れる → broken。
 R6 端点共有の人工物: J30 と POST は P(14:30) を共有（J30 は +、POST は −）＝測定ノイズは β を**負**に歪める。
    方向を確認した上で、端点を分けた gap 版（J30g 14:00→14:25 / POSTg 14:35→16:00）で β が残るかを見る。
 R7 コスト 1 倍 / 2 倍: 取引化 = 14:30 に sign(J30) で建玉 → 16:00 決済（POST 版）／翌 10:00 決済（NEXT 版）。
    1 本あたり bp と USD、往復コスト 0.32 USD（口座実測 0.16 固定・DATA_MAP §4）と 2 倍 0.64 USD を控除。
    net の平均と t（年 8 本・在 7.75 年 → 62 本）。net t<2 → 運用上 broken。
 R8 多重検定: 研究レーン自身が「6 窓 × 2 市場 × 3 時代 = 36 の記述の 1 つ」と書いた。
    Bonferroni(36) と BH(36) を、この族の p 値（本スクリプトで再計算）に当てる。
 R9 look-ahead / survivorship / 衛生: 窓端点の厳密 0・flat 率・NaN 率を年別、era 別に印字。
    声明日の有効数、2020 の欠落、bid-only・1 ベンダー・CFD を明記。
    look-ahead: J30 の終点 14:30 = POST の始点 14:30（情報は過去のみ）→ 構造的 look-ahead なし を確認。
 R10 レジーム部分集合: DFF（政策金利）の方向（hike/hold/cut）・GVZ 高低・|J30| 三分位。
     β が 1 レジームに局在 → 「局在」判定（survived-but-localized）。

判定規則（事前固定）:
  survived      = R1 で FOMC 固有性が残り（交互作用 t≥2 or β_ctrl が t<2 で β_F と有意差）
                  ∧ R3 p<0.05 ∧ R4 で 1 点/1 年除去後も t≥2 ∧ R5 で符号一貫 ∧ R7 net t≥2 ∧ R8 を通過
  broken        = 上記のどれか 1 つでも致命的に落ちる（特に R1・R8・R7）
  inconclusive  = 落ちないが MDE が大きく分離不能

データ: data/macro/XAU_m5_close.npz・US500_m5_close.npz（bid・Dukascopy CFD）、
       data/macro/FOMC_dates.csv（c42 取得）、DFF.csv・GVZCLS.csv。scan 無し・MT5 無し・外部通信無し。
出力: data/refute_c42_goldpost.md（+ _run.log）。書き込みは AUREL_RESEARCH 配下のみ。
seed 20261116。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c42_goldpost.md"); L = []
NY = "America/New_York"; SEED = 20261116; rng = np.random.default_rng(SEED); NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
WD = ['月', '火', '水', '木', '金', '土', '日']

say(f"# [REFUTE c42] 金の声明後継続 W-POST を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c42_goldpost.py)")
say("対象: POST(14:30→16:00) ~ J30(14:00→14:30) 在 2013-20 β +0.318 (HC1 t 3.12, n 62) / NEXT~J30 +0.651 (t 2.92)")
say("")

# ---------------- data ----------------
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz"))
    ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    r = np.diff(np.log(cl)); fl = np.r_[False, r == 0]
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%")
    return ts, cl

def epoch_et(dts, hour, minute, day_offset=0):
    naive = pd.DatetimeIndex(dts) + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan)
    return out

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FS = F[F.scheduled == 1]; FU = F[F.scheduled == 0]
dates = pd.date_range("2010-01-04", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy(); wdy = dates.weekday.to_numpy()
POST_OK = np.asarray(dates >= pd.Timestamp("2013-03-20"))
isF = np.isin(dates, FS.date); isU = np.isin(dates, FU.date); isNFP = np.isin(dates, nfp_dates_v2())
nearF = isF.copy(); nearF[1:] |= isF[:-1]; nearF[:-1] |= isF[1:]
isC = ~nearF & ~isU & ~isNFP
say(f"- 取引日候補 {N}・scheduled 声明日 {isF.sum()}（2013-03-20+ {int((isF&POST_OK).sum())}）・対照候補 {isC.sum()}・NFP {isNFP.sum()}")

lg = np.log
def windows(ts, cl):
    P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
    p14 = P(14, 0); p1430 = P(14, 30); p16 = P(16, 0); p10n = np.r_[P(10, 0)[1:], np.nan]
    W = {}
    W["J30"]   = (lg(p1430) - lg(p14)) * 1e4
    W["POST"]  = (lg(p16) - lg(p1430)) * 1e4
    W["NEXT"]  = (lg(p10n) - lg(p16)) * 1e4
    # R6: 端点を共有しない gap 版
    W["J30g"]  = (lg(P(14, 25)) - lg(p14)) * 1e4
    W["POSTg"] = (lg(p16) - lg(P(14, 35))) * 1e4
    W["px"]    = p1430          # コスト換算用の価格水準（USD）
    W["px16"]  = p16
    return W

# ---------------- regression toolbox ----------------
def _ols_core(y, x):
    n = len(y); xc = x - x.mean(); yc = y - y.mean()
    sxx = xc @ xc; b = (xc @ yc) / sxx; e = yc - b * xc
    h = xc ** 2 / sxx                                  # leverage (centered, slope only)
    se1 = math.sqrt((xc ** 2 @ e ** 2) / sxx ** 2 * n / (n - 2))          # HC1
    se3 = math.sqrt((xc ** 2 @ (e / np.clip(1 - h - 1.0 / n, 1e-6, None)) ** 2) / sxx ** 2)  # HC3
    dfb = xc * e / sxx / np.clip(1 - h - 1.0 / n, 1e-6, None)             # dfbeta on slope
    return b, se1, se3, e, dfb, n

def ols(y, x, nmin=20):
    m = np.isfinite(y) & np.isfinite(x); y, x = y[m], x[m]
    if len(y) < nmin:
        return dict(n=len(y), b=np.nan, t=np.nan, se=np.nan, t3=np.nan, se3=np.nan, dfb=None, idx=None)
    b, se1, se3, e, dfb, n = _ols_core(y, x)
    return dict(n=n, b=b, se=se1, t=b / se1, se3=se3, t3=b / se3, dfb=dfb, y=y, x=x)

def pooled_interaction(y, x, g, nmin=40):
    """y ~ 1 + x + g + x*g ; HC1 t on the interaction (g = 1 for statement days)."""
    m = np.isfinite(y) & np.isfinite(x) & np.isfinite(g)
    y, x, g = y[m], x[m], g[m].astype(float)
    n = len(y)
    if n < nmin: return dict(n=n, b=np.nan, t=np.nan, se=np.nan)
    X = np.column_stack([np.ones(n), x, g, x * g])
    XtXi = np.linalg.pinv(X.T @ X); beta = XtXi @ (X.T @ y); e = y - X @ beta
    k = X.shape[1]
    V = XtXi @ (X.T @ (X * (e ** 2)[:, None])) @ XtXi * n / (n - k)
    se = math.sqrt(V[3, 3])
    return dict(n=n, b=beta[3], se=se, t=beta[3] / se, b_ctrl=beta[1])

def two_sided_p(t, n):
    """normal approx is enough at these n; report both normal and t-dist."""
    from math import erf, sqrt
    pz = 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))
    return pz

def theil_sen(y, x, maxpair=200000):
    m = np.isfinite(y) & np.isfinite(x); y, x = y[m], x[m]; n = len(y)
    i, j = np.triu_indices(n, 1)
    if len(i) > maxpair:
        sel = rng.choice(len(i), maxpair, replace=False); i, j = i[sel], j[sel]
    dx = x[j] - x[i]; ok = np.abs(dx) > 1e-9
    return float(np.median((y[j] - y[i])[ok] / dx[ok]))

def binom_p(k, n, p=0.5):
    """exact two-sided binomial test (sum of pmf's no larger than the observed pmf)"""
    from math import comb
    if n == 0: return float("nan")
    pmf = np.array([comb(n, a) * p ** a * (1 - p) ** (n - a) for a in range(n + 1)])
    return float(min(1.0, pmf[pmf <= pmf[k] * (1 + 1e-12)].sum()))

def winsor(v, q=0.05):
    lo, hi = np.nanquantile(v, q), np.nanquantile(v, 1 - q)
    return np.clip(v, lo, hi)

ERAS = [("在 2013-20", 2013, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
PAIRS = [("POST~J30", "POST", "J30"), ("NEXT~J30", "NEXT", "J30")]
FAMILY = []   # for R8: (label, t, n)

W = {}
for sym in ("XAU", "US500"):
    ts, cl = load(sym); W[sym] = windows(ts, cl)
say("")

# =========================================================
say("## R9 衛生（判定の前提・数字を見る前の規則）")
for sym in ("XAU", "US500"):
    ww = W[sym]
    for lab, lo, hi in ERAS:
        era = (yr >= lo) & (yr <= hi) & POST_OK
        mF = era & isF; mC = era & isC
        nz = lambda v, m: int(np.sum((v[m] == 0) & np.isfinite(v[m])))
        say(f"- {sym} {lab}: 声明日 J30 有効 {int(np.isfinite(ww['J30'][mF]).sum())}/{int(mF.sum())}"
            f"・POST 有効 {int(np.isfinite(ww['POST'][mF]).sum())}・NEXT 有効 {int(np.isfinite(ww['NEXT'][mF]).sum())}"
            f"・厳密 0（J30/POST/NEXT）{nz(ww['J30'],mF)}/{nz(ww['POST'],mF)}/{nz(ww['NEXT'],mF)}"
            f"／対照日 有効 {int(np.isfinite(ww['POST'][mC]).sum())}/{int(mC.sum())}・厳密 0 POST {nz(ww['POST'],mC)}")
say("- look-ahead: J30 の終点と POST の始点はどちらも P(14:30)＝ts==14:30−300 の足 close（14:25-14:30 足）。"
    "説明変数は被説明変数の開始時刻までの情報しか使わない → 構造的 look-ahead なし。")
say("- survivorship / 計測器: Dukascopy CFD **bid のみ・1 ベンダー・1 商品**。mid/ask は無い（DATA_MAP §1 の bid-only 注意）。"
    "声明日は「暦が正しい日」だけを使うので銘柄の生存バイアスは無いが、**配信レジーム（c14 の 2025-09 段差型）は検査していない**。")
say("")

# =========================================================
say("## R0 独立再現（自前の窓コード）")
rep = {}
for sym in ("XAU", "US500"):
    ww = W[sym]
    for lab, lo, hi in ERAS:
        era = (yr >= lo) & (yr <= hi) & POST_OK; mF = era & isF
        for nm, ykey, xkey in PAIRS:
            o = ols(ww[ykey][mF], ww[xkey][mF])
            rep[(sym, lab, nm)] = o
            if np.isfinite(o["b"]):
                p = two_sided_p(o["t"], o["n"])
                FAMILY.append((f"{sym} {lab} {nm}", o["t"], o["n"], p))
                say(f"- {sym} {lab} {nm}: β {o['b']:+.3f}・HC1 t {o['t']:+.2f} (se {o['se']:.3f}, MDE {2*o['se']:.3f})"
                    f"・HC3 t {o['t3']:+.2f}・n {o['n']}・p(正規) {p:.4f}")
            else:
                say(f"- {sym} {lab} {nm}: n {o['n']} < 20（判定不能）")
oX = rep[("XAU", "在 2013-20", "POST~J30")]; oXn = rep[("XAU", "在 2013-20", "NEXT~J30")]
say(f"→ 再現: 金 在 POST β {oX['b']:+.3f} (t {oX['t']:+.2f}, n {oX['n']}) vs 主張 +0.318 (t +3.12, n 62)／"
    f"NEXT β {oXn['b']:+.3f} (t {oXn['t']:+.2f}) vs 主張 +0.651 (t +2.92) → "
    f"{'再現' if abs(oX['b']-0.318)<0.02 and oX['n']==62 else '不一致（下記で検討）'}")
say("")

# =========================================================
say("## R1 ★対照日ベースライン（FOMC 固有性の検定・本命）")
say("規則: 同じ回帰を声明日でない平日（声明±1・臨時・NFP を除く）で走らせ、プール回帰 y ~ 1 + x + F + x·F の"
    "交互作用（x·F）の HC1 t を見る。|t_int| < 2 かつ β_ctrl が t≥2 → **FOMC 固有でない＝素の日内継続**。")
R1 = {}
for sym in ("XAU", "US500"):
    ww = W[sym]
    for lab, lo, hi in ERAS:
        era = (yr >= lo) & (yr <= hi) & POST_OK
        mF = era & isF; mC = era & isC
        for nm, ykey, xkey in PAIRS:
            oc = ols(ww[ykey][mC], ww[xkey][mC], nmin=50)
            use = era & (isF | isC)
            pi = pooled_interaction(ww[ykey][use], ww[xkey][use], isF[use].astype(float))
            R1[(sym, lab, nm)] = (oc, pi)
            if np.isfinite(oc["b"]):
                say(f"- {sym} {lab} {nm}: **対照日 β {oc['b']:+.3f} (HC1 t {oc['t']:+.2f}, n {oc['n']})**"
                    f"／声明日 β {rep[(sym,lab,nm)]['b']:+.3f}"
                    f"／交互作用 β_F−β_C {pi['b']:+.3f} (HC1 t {pi['t']:+.2f}, se {pi['se']:.3f}, MDE {2*pi['se']:.3f}, n {pi['n']})")
say("")

# =========================================================
say("## R2 日付シフト・プラセボ（±7/14/21/28 日・同曜日・対照日に落ちるものだけ）")
R2 = {}
for sym in ("XAU", "US500"):
    ww = W[sym]
    for lab, lo, hi in ERAS[:2]:
        era = (yr >= lo) & (yr <= hi) & POST_OK; mF = era & isF
        for nm, ykey, xkey in PAIRS:
            bs = []
            for k in (-28, -21, -14, -7, 7, 14, 21, 28):
                sh = np.zeros(N, bool)
                shifted = dates[np.where(mF)[0]] + pd.Timedelta(days=k)
                pos = np.searchsorted(dates, shifted); pos = pos[pos < N]
                pos = pos[np.isin(dates[pos], shifted)]
                sh[pos] = True; sh &= isC & era
                o = ols(ww[ykey][sh], ww[xkey][sh])
                if np.isfinite(o["b"]): bs.append(o["b"])
            bs = np.array(bs); R2[(sym, lab, nm)] = bs
            obs = rep[(sym, lab, nm)]["b"]
            if len(bs) and np.isfinite(obs):
                say(f"- {sym} {lab} {nm}: 観測 β {obs:+.3f} vs シフト 8 集合 "
                    f"平均 {bs.mean():+.3f}・sd {bs.std(ddof=1):.3f}・範囲 [{bs.min():+.3f}, {bs.max():+.3f}]"
                    f"・観測を超えた集合 {int((bs>=obs).sum())}/{len(bs)}・z {(obs-bs.mean())/max(bs.std(ddof=1),1e-9):+.2f}")
say("")

# =========================================================
say("## R3 信号のランダム化（声明日の中で J30 をシャッフル 2000 回）")
for sym in ("XAU", "US500"):
    ww = W[sym]
    for lab, lo, hi in ERAS[:2]:
        era = (yr >= lo) & (yr <= hi) & POST_OK; mF = era & isF
        for nm, ykey, xkey in PAIRS:
            m = mF & np.isfinite(ww[ykey]) & np.isfinite(ww[xkey])
            y = ww[ykey][m]; x = ww[xkey][m]
            if len(y) < 20: continue
            obs = rep[(sym, lab, nm)]["b"]
            null = np.empty(NPERM)
            for j in range(NPERM):
                xp = rng.permutation(x); xc = xp - xp.mean()
                null[j] = (xc @ (y - y.mean())) / (xc @ xc)
            p = (np.abs(null) >= abs(obs)).mean()
            say(f"- {sym} {lab} {nm}: β {obs:+.3f}・置換 p {p:.4f}・帰無 sd {null.std():.3f}（n {len(y)}）")
say("")

# =========================================================
say("## R4 影響点・頑健性（在 2013-20 の金が本体）")
for sym in ("XAU", "US500"):
    ww = W[sym]
    for lab, lo, hi in ERAS[:2]:
        era = (yr >= lo) & (yr <= hi) & POST_OK; mF = era & isF
        for nm, ykey, xkey in PAIRS:
            m = mF & np.isfinite(ww[ykey]) & np.isfinite(ww[xkey])
            if m.sum() < 20: continue
            y = ww[ykey][m]; x = ww[xkey][m]; dd = dates[m]; yy = yr[m]
            o = ols(y, x)
            # drop single most influential (max |dfbeta|)
            k = int(np.argmax(np.abs(o["dfb"]))); keep = np.ones(len(y), bool); keep[k] = False
            o1 = ols(y[keep], x[keep])
            # drop top-2 |J30|
            ordr = np.argsort(-np.abs(x)); keep2 = np.ones(len(y), bool); keep2[ordr[:2]] = False
            o2 = ols(y[keep2], x[keep2])
            # leave-one-year-out
            loyo = []
            for Y in np.unique(yy):
                kk = yy != Y; oy = ols(y[kk], x[kk])
                if np.isfinite(oy["b"]): loyo.append((Y, oy["b"], oy["t"]))
            tmin = min(t for _, _, t in loyo) if loyo else np.nan
            bmin = min(b for _, b, _ in loyo) if loyo else np.nan
            # sign agreement
            s = np.sign(x) * np.sign(y); hits = int((s > 0).sum()); nn = int((s != 0).sum())
            pb = binom_p(hits, nn)
            ts_b = theil_sen(y, x)
            ow = ols(winsor(y), winsor(x))
            say(f"- {sym} {lab} {nm}: β {o['b']:+.3f} t {o['t']:+.2f}"
                f"／最大影響 1 点除去（{dd[k].date()}・J30 {x[k]:+.0f}bp・y {y[k]:+.0f}bp）→ β {o1['b']:+.3f} **t {o1['t']:+.2f}**"
                f"／|J30| 上位 2 除去 → β {o2['b']:+.3f} t {o2['t']:+.2f}"
                f"／LOYO 最小 t {tmin:+.2f}（β 最小 {bmin:+.3f}）"
                f"／符号一致 {hits}/{nn} = {hits/max(nn,1)*100:.0f}%（二項 p {pb:.3f}）"
                f"／Theil–Sen {ts_b:+.3f}／5% winsor β {ow['b']:+.3f} t {ow['t']:+.2f}")
say("")

# =========================================================
say("## R5 別の在外分割")
SPL = [("2013-16", 2013, 2016), ("2017-20", 2017, 2020), ("2021-23", 2021, 2023), ("2024-26H1", 2024, 2026)]
for sym in ("XAU",):
    ww = W[sym]
    for nm, ykey, xkey in PAIRS:
        row = []
        for lab, lo, hi in SPL:
            era = (yr >= lo) & (yr <= hi) & POST_OK; mF = era & isF
            o = ols(ww[ykey][mF], ww[xkey][mF], nmin=12)
            row.append(f"{lab} β {o['b']:+.3f} (t {o['t']:+.2f}, n {o['n']})" if np.isfinite(o["b"]) else f"{lab} n{o['n']}")
        say(f"- {sym} {nm} 4 分割: " + " ／ ".join(row))
        # rolling OOS boundary
        roll = []
        for B in (2018, 2019, 2020, 2021):
            inm = (yr <= B) & POST_OK & isF; oum = (yr > B) & POST_OK & isF
            oi = ols(ww[ykey][inm], ww[xkey][inm], nmin=12); oo = ols(ww[ykey][oum], ww[xkey][oum], nmin=12)
            roll.append(f"≤{B}: 在 {oi['b']:+.3f}(t{oi['t']:+.2f},n{oi['n']}) → 外 {oo['b']:+.3f}(t{oo['t']:+.2f},n{oo['n']})")
        say(f"  - OOS 境界を動かす: " + " ／ ".join(roll))
        # odd/even statement index
        idx = np.where(POST_OK & isF)[0]
        for par, pl in ((0, "奇数番"), (1, "偶数番")):
            mm = np.zeros(N, bool); mm[idx[par::2]] = True
            o = ols(ww[ykey][mm], ww[xkey][mm], nmin=12)
            say(f"  - {pl}目の声明日のみ: β {o['b']:+.3f} (t {o['t']:+.2f}, n {o['n']})")
say("")

# =========================================================
say("## R6 端点共有の人工物（P(14:30) を J30 と POST が共有）")
say("理論: P(14:30) の測定ノイズ ε は J30 に +ε、POST に −ε で入る → cov を**負**に歪める（正の β を作らない）。"
    "確認として端点を分けた gap 版（J30g 14:00→14:25・POSTg 14:35→16:00）を走らせる。")
for sym in ("XAU", "US500"):
    ww = W[sym]
    for lab, lo, hi in ERAS[:2]:
        era = (yr >= lo) & (yr <= hi) & POST_OK; mF = era & isF
        o = ols(ww["POST"][mF], ww["J30"][mF]); og = ols(ww["POSTg"][mF], ww["J30g"][mF])
        o_mix = ols(ww["POSTg"][mF], ww["J30"][mF])
        say(f"- {sym} {lab}: 共有端点 β {o['b']:+.3f} (t {o['t']:+.2f})／gap 版 β {og['b']:+.3f} (t {og['t']:+.2f}, n {og['n']})"
            f"／POSTg~J30 β {o_mix['b']:+.3f} (t {o_mix['t']:+.2f})")
say("")

# =========================================================
say("## R7 コスト 1 倍 / 2 倍（取引化: 14:30 に sign(J30) で建玉）")
say("規則: 1 本 = 14:30 建玉 → 16:00 決済（POST 版）／翌 10:00 決済（NEXT 版・16:00 の価格は使わず 14:30→翌 10:00 で評価）。"
    "gross USD = sign(J30) × (決済価格 − 建玉価格)。往復コスト 1 倍 = 0.32 USD（口座実測 0.16 固定・DATA_MAP §4）、2 倍 = 0.64。"
    "swap は未記録【要取得】→ NEXT 版は 1 晩分の swap が未控除（下向きの未計上）。")
ww = W["XAU"]
p1430 = ww["px"]; p16 = ww["px16"]
# 翌 10:00 の価格（NEXT は 16:00 起点だが、取引版は 14:30 建玉 → 翌 10:00 決済で評価する）
_zx = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
tsX = _zx["ts"].astype(np.int64); clX = _zx["close"].astype(float)
p10_next = np.r_[price_at(tsX, clX, epoch_et(dates, 10, 0))[1:], np.nan]
for lab, lo, hi in ERAS[:2]:
    era = (yr >= lo) & (yr <= hi) & POST_OK; mF = era & isF
    for tag, pexit in (("→16:00", p16), ("→翌10:00", p10_next)):
        m = mF & np.isfinite(ww["J30"]) & np.isfinite(p1430) & np.isfinite(pexit) & (ww["J30"] != 0)
        if m.sum() < 12: continue
        s = np.sign(ww["J30"][m]); gross = s * (pexit[m] - p1430[m])
        bp = gross / p1430[m] * 1e4
        n = len(gross); se = gross.std(ddof=1) / math.sqrt(n)
        for cmul, cl_ in ((0.0, "コスト 0"), (1.0, "1 倍 0.32"), (2.0, "2 倍 0.64")):
            net = gross - cmul * 0.32
            t = net.mean() / se
            say(f"- 金 {lab} {tag} {cl_}: 1 本 {net.mean():+.3f} USD（{net.mean()/np.median(p1430[m])*1e4:+.1f} bp）"
                f"・t {t:+.2f}・n {n}・勝率 {(net>0).mean()*100:.0f}%・合計 {net.sum():+.1f} USD"
                + (f"・gross 平均 {bp.mean():+.1f} bp" if cmul == 0 else ""))
say("")

# =========================================================
say("## R8 多重検定（研究レーン自身の族: 6 窓 × 2 市場 × 3 時代 = 36）")
ps = [(lab, t, n, p) for lab, t, n, p in FAMILY]
ps_sorted = sorted(ps, key=lambda z: z[3])
say(f"- 本スクリプトで再計算した族（POST~J30・NEXT~J30 × 2 市場 × 3 時代 = {len(ps)} 検定）の p 昇順:")
for lab, t, n, p in ps_sorted[:6]:
    say(f"  - {lab}: t {t:+.2f}・p {p:.4f}・Bonferroni(36) p·36 = {min(1,p*36):.3f}・Bonferroni({len(ps)}) = {min(1,p*len(ps)):.3f}")
mn = ps_sorted[0]
say(f"- 最小 p = {mn[3]:.4f}（{mn[0]}）→ **Bonferroni(36) 後 {min(1,mn[3]*36):.3f}**"
    f"（研究レーン自身が「36 の記述の 1 つ」と書いた族の大きさ）")
# BH on the 36-size family using our computed p's (conservative: only our subset known)
m36 = 36
bh = [(lab, p, (i + 1) / m36 * 0.05) for i, (lab, t, n, p) in enumerate(ps_sorted)]
say("- BH(36, q=0.05): " + " ／ ".join(f"{lab.split(' ')[0]}{lab.split(' ')[-1]} p {p:.4f} vs 閾 {thr:.4f} {'通' if p<=thr else '否'}" for lab, p, thr in bh[:4]))
say("")

# =========================================================
say("## R10 レジーム部分集合（在 2013-20 の金）")
# DFF direction
dff = pd.read_csv(os.path.join(MAC, "DFF.csv"))
dcol = [c for c in dff.columns if c.lower() in ("date", "observation_date")][0]
vcol = [c for c in dff.columns if c != dcol][0]
dff[dcol] = pd.to_datetime(dff[dcol]); dff[vcol] = pd.to_numeric(dff[vcol], errors="coerce")
dff = dff.dropna().set_index(dcol)[vcol].sort_index()
ff = dff.reindex(pd.DatetimeIndex(dates), method="ffill").to_numpy()
ff_chg = np.r_[np.nan, ff[1:] - ff[:-1]]
ff126 = np.r_[np.full(126, np.nan), ff[126:] - ff[:-126]]
try:
    gvz = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"))
    gc = [c for c in gvz.columns if c.lower() in ("date", "observation_date")][0]
    gv = [c for c in gvz.columns if c != gc][0]
    gvz[gc] = pd.to_datetime(gvz[gc]); gvz[gv] = pd.to_numeric(gvz[gv], errors="coerce")
    gz = gvz.dropna().set_index(gc)[gv].sort_index().reindex(pd.DatetimeIndex(dates), method="ffill").to_numpy()
except Exception as ex:
    gz = np.full(N, np.nan); say(f"- GVZ 読込不可: {ex}")
ww = W["XAU"]
era = (yr >= 2013) & (yr <= 2020) & POST_OK; mF = era & isF
sub = {}
sub["政策 引締（Δ126d>+0.1）"] = mF & (ff126 > 0.1)
sub["政策 据置（|Δ126d|≤0.1）"] = mF & (np.abs(ff126) <= 0.1)
sub["政策 緩和（Δ126d<−0.1）"] = mF & (ff126 < -0.1)
gmed = np.nanmedian(gz[mF])
sub[f"GVZ 高（>{gmed:.1f}）"] = mF & (gz > gmed)
sub[f"GVZ 低（≤{gmed:.1f}）"] = mF & (gz <= gmed)
aj = np.abs(ww["J30"]); q = np.nanquantile(aj[mF], [1/3, 2/3])
sub[f"|J30| 小（≤{q[0]:.0f}bp）"] = mF & (aj <= q[0])
sub[f"|J30| 中"] = mF & (aj > q[0]) & (aj <= q[1])
sub[f"|J30| 大（>{q[1]:.0f}bp）"] = mF & (aj > q[1])
for k, m in sub.items():
    o = ols(ww["POST"][m], ww["J30"][m], nmin=8); o2 = ols(ww["NEXT"][m], ww["J30"][m], nmin=8)
    say(f"- {k}: POST β {o['b']:+.3f} (t {o['t']:+.2f}, n {o['n']})／NEXT β {o2['b']:+.3f} (t {o2['t']:+.2f})")
say("")
say(f"- 実行 {time.time()-T0:.1f} s・npz 2 本＋FOMC_dates.csv＋DFF＋GVZ・scan 無し・MT5 無し・外部通信無し。seed {SEED}。")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
