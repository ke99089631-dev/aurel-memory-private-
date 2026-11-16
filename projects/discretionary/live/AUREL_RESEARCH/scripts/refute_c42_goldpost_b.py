# -*- coding: utf-8 -*-
"""
[REFUTE c42 第2段] 第1段（refute_c42_goldpost.py）の結果を受けた追撃と**自分の反証の自己批判**。

第1段で分かったこと（再現は完全一致）:
 - R1 対照日 β +0.030 (t 0.54, n 1741) ／交互作用 +0.289 (t 2.52) → 在では **FOMC 固有性は残った**（素の午後自己相関ではない）。
 - R6 gap 版 +0.287 (t 3.19) → 端点共有の人工物ではない。
 - R3 置換 p 0.0095（HC1 p 0.0018 より緩い＝HC1 は楽観側）。
 - R5 ★ 4 分割で **2013-16 β +0.396 (t 3.03, n 30)／2017-20 +0.147 (t 0.79, n 32)**＝在窓の後半で既に消えている。
   奇数番目 +0.405 (t 3.23)／偶数番目 −0.103 (t −0.39)＝**同一標本の無作為分割で片側に全部乗る**。
 - R7 →16:00 の取引版は 1 倍コストで net t 1.46＝在でも売買に足りない。→翌10:00 は在 t 2.74／外 t 1.09。
 - R2 日付シフト・プラセボ（z +0.42）は **誤校正**: プラセボ日の |J30| は声明日の 1/7 しかなく x 分散が桁違い
   → β の se が 3〜4 倍膨らむ。㊷（置換帰無の誤校正）の型。**この反証は無効なので作り直す。**

本段の事前固定（数字を見る前）:
 B1 発見窓の外側: 2017-20／2021-26H1／**2017-2026H1 プール**の β・HC1 t・MDE。
    era ダミー交互作用（2013-16 vs それ以降）の t。 → |t_era| ≥ 2 なら「2013-16 局在」。
 B2 HC1 se の校正: 62 日を 2000 回 無作為 50/50 分割 → (β_A − β_B) の sd を、
    HC1 se から予測される 2·se/√2·√2 = 2·se(n/2)/… の理論値と比べる。実測 sd >> 理論 → HC1 は se を過小評価。
 B3 年ブロック・ブートストラップ（年単位で復元抽出 2000 回）→ β の se・両側 p。
    系列相関/年クラスタを許した se。これが HC1 se の 2 倍以上なら t 3.12 は見かけ倒し。
 B4 ★分散一致プラセボ（R2 の作り直し）: 同時代の対照日から **|J30| 分布を声明日に一致させて** n_F 日を抽出
    （|J30| の 5 分位ごとに同数）→ β の帰無分布 2000 本。これが正しい校正。
 B5 ★トレンド交絡（新しい攻撃）: sign(J30) が時代の方向に偏っていれば E[sign(J30)·y] は
    「継続」でなく「金のドリフト × 偏った符号」になる。
    (a) 各窓で sign(J30) の偏り（負の比率）と、同時代 対照日の y の無条件平均。
    (b) y から**同時代・同曜日の対照日平均**を引いた y' で β を再計算。
    (c) 方向統計 E[s·y] を E[s]·E[y]（交絡項）と E[s·y]−E[s]·E[y]（純継続項）に分解。
 B6 取引版の分散一致プラセボ: 対照日から |J30| 一致で抽出した「偽の声明日」で
    sign(J30) 建玉 → 翌 10:00 を回し、在 +5.87 USD/本 が偽日でも出るかを見る。
 B7 前向きセル案（発表プール β>0 ∧ HC1 t≥2 ∧ 外 同符号 t≥1.5）の事前の合格確率:
    B3 の se と B1 の点推定を使い、2017 年以降の実効 β での n_req（t 2 に要る発表数）を出す。

判定: B1 で 2013-16 局在 ∧ B4 で分散一致プラセボの内側 → broken。
      B1 局在だが B4 の外側 → survived-but-localized（発見窓のみ）。
出力: data/refute_c42_goldpost_b.md。書き込みは AUREL_RESEARCH 配下のみ。seed 20261116。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c42_goldpost_b.md"); L = []
NY = "America/New_York"; SEED = 20261116; rng = np.random.default_rng(SEED); NB = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c42 第2段] 2013-16 局在か・HC1 se は正しいか・分散一致プラセボ — {time.strftime('%Y-%m-%d %H:%M')}")
say("(scripts/refute_c42_goldpost_b.py・第1段 data/refute_c42_goldpost.md の続き)")
say("")

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

z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lg = np.log
P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
p14 = P(14, 0); p1430 = P(14, 30); p16 = P(16, 0); p10n = np.r_[P(10, 0)[1:], np.nan]
J30 = (lg(p1430) - lg(p14)) * 1e4
POST = (lg(p16) - lg(p1430)) * 1e4
NEXT = (lg(p10n) - lg(p16)) * 1e4
TRADE = (p10n - p1430)          # USD, 14:30 → 翌 10:00（取引版・R7 と同じ）
TRADE16 = (p16 - p1430)

def _ols(y, x):
    n = len(y); xc = x - x.mean(); sxx = xc @ xc
    b = (xc @ (y - y.mean())) / sxx; e = (y - y.mean()) - b * xc
    se = math.sqrt((xc ** 2 @ e ** 2) / sxx ** 2 * n / (n - 2))
    return b, se, n

def ols(y, x, m=None, nmin=12):
    if m is not None: y, x = y[m], x[m]
    k = np.isfinite(y) & np.isfinite(x); y, x = y[k], x[k]
    if len(y) < nmin: return dict(n=len(y), b=np.nan, se=np.nan, t=np.nan)
    b, se, n = _ols(y, x); return dict(n=n, b=b, se=se, t=b / se)

def zp(t):
    from math import erf, sqrt
    return 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))

def interact(y, x, g, nmin=40):
    k = np.isfinite(y) & np.isfinite(x) & np.isfinite(g)
    y, x, g = y[k], x[k], g[k].astype(float); n = len(y)
    if n < nmin: return dict(n=n, b=np.nan, t=np.nan, se=np.nan)
    X = np.column_stack([np.ones(n), x, g, x * g]); XtXi = np.linalg.pinv(X.T @ X)
    bb = XtXi @ (X.T @ y); e = y - X @ bb
    V = XtXi @ (X.T @ (X * (e ** 2)[:, None])) @ XtXi * n / (n - 4)
    return dict(n=n, b=bb[3], se=math.sqrt(V[3, 3]), t=bb[3] / math.sqrt(V[3, 3]))

YKEYS = [("POST", POST), ("NEXT", NEXT)]
mF_all = isF & POST_OK

# ---------------------------------------------------------------- B1
say("## B1 発見窓（2013-16）の外側で何が残るか")
WINS = [("2013-16", 2013, 2016), ("2017-20", 2017, 2020), ("2021-26H1", 2021, 2026), ("**2017-2026H1 プール**", 2017, 2026)]
for nm, y in YKEYS:
    row = []
    for lab, lo, hi in WINS:
        o = ols(y, J30, mF_all & (yr >= lo) & (yr <= hi))
        row.append(f"{lab}: β {o['b']:+.3f} (t {o['t']:+.2f}, MDE {2*o['se']:.3f}, n {o['n']})")
    say(f"- {nm}~J30 — " + " ／ ".join(row))
    g = ((yr >= 2017) & POST_OK).astype(float)     # g=1 → 2017 以降
    oi = interact(y[mF_all], J30[mF_all], g[mF_all], nmin=40)
    say(f"  - era 交互作用（2017+ − 2013-16）: Δβ {oi['b']:+.3f} (HC1 t {oi['t']:+.2f}, se {oi['se']:.3f}, n {oi['n']})"
        f" → {'**2013-16 局在（有意に減衰）**' if abs(oi['t'])>=2 else '減衰は分離不能（MDE 内）'}")
say("")

# ---------------------------------------------------------------- B2
say("## B2 HC1 se の校正（62 日を無作為 50/50 分割 2000 回）")
for nm, y in YKEYS:
    m = mF_all & (yr <= 2020) & np.isfinite(y) & np.isfinite(J30)
    yy = y[m]; xx = J30[m]; n = len(yy)
    b0, se0, _ = _ols(yy, xx)
    d = np.empty(NB)
    for j in range(NB):
        pr = rng.permutation(n); a = pr[: n // 2]; bb = pr[n // 2:]
        ba, _, _ = _ols(yy[a], xx[a]); bbv, _, _ = _ols(yy[bb], xx[bb]); d[j] = ba - bbv
    theo = 2 * se0 * math.sqrt(2) / math.sqrt(2) * math.sqrt(2)   # se(n/2)=se*sqrt2 → sd(diff)=2*se
    say(f"- {nm}: β {b0:+.3f}・HC1 se {se0:.3f} → 分割差の理論 sd（se 正しければ）= 2·se = {2*se0:.3f}"
        f"・**実測 sd {d.std(ddof=1):.3f}**（比 {d.std(ddof=1)/(2*se0):.2f}）"
        f"・|差|>2·se の割合 {np.mean(np.abs(d) > 2*se0)*100:.0f}%"
        f" → {'**HC1 se は過小評価**' if d.std(ddof=1) > 1.3*2*se0 else 'se は概ね校正されている'}")
    say(f"  - 第1段の奇数/偶数番目の差 {'(+0.405)−(−0.103)=+0.508' if nm=='POST' else '(+0.525)−(+0.255)=+0.270'}"
        f" はこの分布の {np.mean(np.abs(d) >= (0.508 if nm=='POST' else 0.270))*100:.0f}% 分位より外側"
        f"（無作為分割でも同程度の偏りは起きる＝奇数/偶数の割れ自体は反証にならない）")
say("")

# ---------------------------------------------------------------- B3
say("## B3 年ブロック・ブートストラップ（年単位で復元抽出 2000 回・在 2013-20）")
for nm, y in YKEYS:
    m = mF_all & (yr <= 2020) & np.isfinite(y) & np.isfinite(J30)
    yy = y[m]; xx = J30[m]; yrs = yr[m]; uq = np.unique(yrs)
    b0, se0, n0 = _ols(yy, xx)
    bs = []
    for j in range(NB):
        pick = rng.choice(uq, len(uq), replace=True)
        idx = np.concatenate([np.where(yrs == Y)[0] for Y in pick])
        if len(idx) < 20: continue
        try:
            bb, _, _ = _ols(yy[idx], xx[idx]); bs.append(bb)
        except Exception: pass
    bs = np.array(bs)
    seb = bs.std(ddof=1); p = 2 * min(np.mean(bs <= 0), np.mean(bs >= 0))
    say(f"- {nm}: β {b0:+.3f}・HC1 se {se0:.3f} → **年ブロック se {seb:.3f}（比 {seb/se0:.2f}）・t {b0/seb:+.2f}**"
        f"・ブート両側 p {p:.3f}・2.5-97.5% [{np.quantile(bs,0.025):+.3f}, {np.quantile(bs,0.975):+.3f}]"
        f" → {'**t<2 に落ちる**' if abs(b0/seb) < 2 else 't≥2 は保つ'}")
say("")

# ---------------------------------------------------------------- B4
say("## B4 ★分散一致プラセボ（第1段 R2 の作り直し・㊷ 誤校正の修正）")
say("規則: 同時代の対照日から、声明日の |J30| 5 分位に**同数ずつ**抽出して n_F 日の偽声明日を作る（x 分散を一致させる）。")
for nm, y in YKEYS:
    mF = mF_all & (yr <= 2020) & np.isfinite(y) & np.isfinite(J30)
    mC = isC & POST_OK & (yr <= 2020) & np.isfinite(y) & np.isfinite(J30)
    aF = np.abs(J30[mF]); nF = mF.sum()
    qs = np.quantile(aF, [0, .2, .4, .6, .8, 1.0]); qs[0] = -1; qs[-1] = np.inf
    cnt = [int(((aF > qs[i]) & (aF <= qs[i + 1])).sum()) for i in range(5)]
    aC = np.abs(J30); pools = []
    ok_pool = True
    for i in range(5):
        pl = np.where(mC & (aC > qs[i]) & (aC <= qs[i + 1]))[0]
        pools.append(pl)
        if len(pl) < cnt[i]: ok_pool = False
    b0, se0, _ = _ols(y[mF], J30[mF])
    if not ok_pool:
        say(f"- {nm}: 分位 {[len(p) for p in pools]} 対 必要 {cnt} → 上位分位の対照日が足りない（|J30| 大は声明日固有）"
            f"＝**x 分散一致のプラセボは構成不能**。これ自体が「声明日は普段の日と別物」の証拠。")
        # fall back: 最上位分位だけ緩める（復元抽出を許す）
        nullb = []
        for j in range(NB):
            idx = np.concatenate([rng.choice(pools[i], cnt[i], replace=len(pools[i]) < cnt[i]) for i in range(5)])
            try:
                bb, _, _ = _ols(y[idx], J30[idx]); nullb.append(bb)
            except Exception: pass
        nullb = np.array(nullb)
        say(f"  - 復元抽出で代替（上位分位は重複を許す）: 帰無 平均 {nullb.mean():+.3f}・sd {nullb.std(ddof=1):.3f}"
            f"・観測 {b0:+.3f} の両側 p {np.mean(np.abs(nullb-nullb.mean())>=abs(b0-nullb.mean())):.4f}"
            f"・z {(b0-nullb.mean())/nullb.std(ddof=1):+.2f}")
    else:
        nullb = []
        for j in range(NB):
            idx = np.concatenate([rng.choice(pools[i], cnt[i], replace=False) for i in range(5)])
            bb, _, _ = _ols(y[idx], J30[idx]); nullb.append(bb)
        nullb = np.array(nullb)
        say(f"- {nm}: 観測 β {b0:+.3f}・帰無 平均 {nullb.mean():+.3f}・sd {nullb.std(ddof=1):.3f}"
            f"・両側 p {np.mean(np.abs(nullb-nullb.mean())>=abs(b0-nullb.mean())):.4f}・z {(b0-nullb.mean())/nullb.std(ddof=1):+.2f}")
    say(f"  - |J30| 分布: 声明日 中央値 {np.median(aF):.0f} bp・90% 点 {np.quantile(aF,0.9):.0f}"
        f"／対照日 中央値 {np.median(np.abs(J30[mC])):.0f}・90% 点 {np.quantile(np.abs(J30[mC]),0.9):.0f}"
        f"（比 {np.median(aF)/max(np.median(np.abs(J30[mC])),1e-9):.1f} 倍）")
say("")

# ---------------------------------------------------------------- B5
say("## B5 ★トレンド交絡: E[s·y] = E[s]·E[y] + Cov(s,y)  （s = sign(J30)）")
say("sign(J30) が時代で偏り、かつ金の y が無条件に偏っていれば、「継続」でなく「偏った符号 × ドリフト」で正になる。")
for lab, lo, hi in [("在 2013-20", 2013, 2020), ("2013-16", 2013, 2016), ("2017-20", 2017, 2020), ("外 2021-26H1", 2021, 2026)]:
    mF = mF_all & (yr >= lo) & (yr <= hi)
    mC = isC & POST_OK & (yr >= lo) & (yr <= hi)
    for nm, y in YKEYS:
        k = mF & np.isfinite(y) & np.isfinite(J30)
        s = np.sign(J30[k]); yv = y[k]
        yc = y[mC & np.isfinite(y)]
        Es, Ey, Eyc = s.mean(), yv.mean(), yc.mean()
        conf = Es * Eyc; tot = (s * yv).mean(); pure = tot - Es * Ey
        say(f"- {lab} {nm}: 負の J30 比率 {(s<0).mean()*100:.0f}%・E[s] {Es:+.2f}"
            f"・声明日 E[y] {Ey:+.1f} bp・対照日 E[y] {Eyc:+.1f} bp"
            f"・**E[s·y] {tot:+.1f} bp** = 交絡 E[s]·E[y_ctrl] {conf:+.1f} ＋ 残り {tot-conf:+.1f}")
# (b) 対照日・同曜日平均を引いた y' で β
say("- (b) y から同時代・同曜日の対照日平均を引いた y′ での β（金のドリフト除去後）:")
for lab, lo, hi in [("在 2013-20", 2013, 2020), ("2013-16", 2013, 2016), ("外 2021-26H1", 2021, 2026)]:
    era = POST_OK & (yr >= lo) & (yr <= hi)
    for nm, y in YKEYS:
        yprime = y.copy()
        for w in range(5):
            mc = isC & era & (wdy == w) & np.isfinite(y)
            if mc.sum() >= 20:
                yprime = np.where(era & (wdy == w), y - y[mc].mean(), yprime)
        o = ols(yprime, J30, mF_all & era)
        o0 = ols(y, J30, mF_all & era)
        say(f"  - {lab} {nm}: β(y) {o0['b']:+.3f} (t {o0['t']:+.2f}) → β(y′) {o['b']:+.3f} (t {o['t']:+.2f})")
say("")

# ---------------------------------------------------------------- B6
say("## B6 取引版（14:30 建玉 → 翌 10:00）の分散一致プラセボ・コスト後")
for lab, lo, hi in [("在 2013-20", 2013, 2020), ("2013-16", 2013, 2016), ("2017-20", 2017, 2020), ("外 2021-26H1", 2021, 2026)]:
    era = POST_OK & (yr >= lo) & (yr <= hi)
    for tag, G in (("→16:00", TRADE16), ("→翌10:00", TRADE)):
        m = mF_all & era & np.isfinite(G) & np.isfinite(J30) & (J30 != 0)
        if m.sum() < 10: continue
        g = np.sign(J30[m]) * G[m]; n = len(g); se = g.std(ddof=1) / math.sqrt(n)
        n1 = g - 0.32; n2 = g - 0.64
        say(f"- 金 {lab} {tag}: gross {g.mean():+.3f} USD/本 (t {g.mean()/se:+.2f}, n {n})"
            f"・1 倍 {n1.mean():+.3f} (t {n1.mean()/se:+.2f})・2 倍 {n2.mean():+.3f} (t {n2.mean()/se:+.2f})"
            f"・勝率 {(g>0).mean()*100:.0f}%")
# placebo for the trade
say("- 分散一致プラセボ（在 2013-20・対照日から |J30| 5 分位一致・復元抽出 2000 回）:")
for tag, G in (("→16:00", TRADE16), ("→翌10:00", TRADE)):
    mF = mF_all & (yr <= 2020) & POST_OK & np.isfinite(G) & np.isfinite(J30) & (J30 != 0)
    mC = isC & POST_OK & (yr <= 2020) & np.isfinite(G) & np.isfinite(J30) & (J30 != 0)
    aF = np.abs(J30[mF]); qs = np.quantile(aF, [0, .2, .4, .6, .8, 1.0]); qs[0] = -1; qs[-1] = np.inf
    cnt = [int(((aF > qs[i]) & (aF <= qs[i + 1])).sum()) for i in range(5)]
    aC = np.abs(J30); pools = [np.where(mC & (aC > qs[i]) & (aC <= qs[i + 1]))[0] for i in range(5)]
    obs = (np.sign(J30[mF]) * G[mF]).mean()
    null = np.empty(NB)
    for j in range(NB):
        idx = np.concatenate([rng.choice(pools[i], cnt[i], replace=len(pools[i]) < cnt[i]) for i in range(5)])
        null[j] = (np.sign(J30[idx]) * G[idx]).mean()
    say(f"  - {tag}: 観測 {obs:+.3f} USD/本・偽声明日 平均 {null.mean():+.3f}・sd {null.std(ddof=1):.3f}"
        f"・片側 p(観測以上) {np.mean(null>=obs):.4f}・z {(obs-null.mean())/null.std(ddof=1):+.2f}"
        f"・プール枚数 {[len(p) for p in pools]} 対 必要 {cnt}")
say("")

# ---------------------------------------------------------------- B7
say("## B7 前向きセル案（発表プール・β>0 ∧ HC1 t≥2 ∧ 外 同符号 t≥1.5）の事前の決着可能性")
for nm, y in YKEYS:
    m17 = mF_all & (yr >= 2017) & np.isfinite(y) & np.isfinite(J30)
    b17, se17, n17 = _ols(y[m17], J30[m17])
    # n_req for t=2 at the 2017+ point estimate, scaling se ∝ 1/sqrt(n)
    nreq = n17 * (2 * se17 / max(abs(b17), 1e-9)) ** 2 if abs(b17) > 1e-9 else np.inf
    say(f"- {nm}: 2017 年以降の実効 β {b17:+.3f}（se {se17:.3f}・t {b17/se17:+.2f}・n {n17}）"
        f"→ この大きさを t 2 で立てるのに要る声明日数 **n_req ≈ {nreq:.0f}**"
        f"（年 8 回なら {nreq/8:.0f} 年・発表プール 300 件でも |J30| が FOMC 級でない発表が混ざれば se は縮まない）")
say("")
say(f"- 実行 {time.time()-T0:.1f} s・XAU npz 1 本＋FOMC_dates.csv・scan 無し・MT5 無し・外部通信無し。seed {SEED}。")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
