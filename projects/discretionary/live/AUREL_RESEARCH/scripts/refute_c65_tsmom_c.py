# -*- coding: utf-8 -*-
"""
[REFUTE c65 part C 2026-11-24] part A/B で残った 3 点を閉じる。

C1 **捨てられた在サンプル**: c65 の US500 在は 2014-20 だが、キャッシュは 2012-01 から有り
   L=252 の月次は 2013 年から作れる（part A の 在 2013-19 は n 67 で t −1.57）。
   「利用可能な在データを全部使う」版 = 在 **2013-2020** を計算。c65 の窓選択が任意だったかを数字で示す。
   破壊条件: 在データを全部使うと |t|<1.5。

C2 **VR の有限標本帰無を実際の窓長で**: part B の iid MC は n=250（年別）で中央値 0.871 を再現し
   c65 の候補 ⑲ 主張を支持した。しかし c65 が「|z|≤1.4 で RW を棄却しない」と書いた**窓レベル** VR は
   n≈1400〜2500 日で計算されている（年別とは別物）。その n での有限標本帰無中央値を
   **実データ r_d の iid ブートストラップ**（裾を保存）で作り、観測 VR の両側 p を出す。
   目的 = c65 の「3 窓とも RW と区別不能」が (i) 偏り補正後も成り立つか (ii) LM z が保守的すぎて
   実は弱い平均回帰を見落としていないか、の双方向の検査。
   破壊条件: 偏り補正後の p<0.05 のセルが期待数を超える → c65 の「区別不能」は誤り。

C3 **候補 112 の校正を一般化**: part B の FPR 表は n=78 のみ。n ∈ {30, 78, 120} で
   HC1 |t|≥2 の FPR を少数側件数 n_min の関数として出し、**FPR≤0.06 を満たす最小の n_min**（＝使える閾値）を提示。
   ついでに「少数側割合」での閾値も出す。これは c65 候補 112（「少数側<3 か月なら識別不能」）の置き換え案。

C4 外（US500 外 2021-26H1）の少数側 13 か月が **1 エピソード**だったことの帰結:
   外 β +0.133（c65 が C0 の外として報告）は実質 1 事象。回転 p と WCB を併記。

seed 20261124。書込は AUREL_RESEARCH/data のみ。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c65_tsmom_c.md")
NY = "America/New_York"
rng = np.random.default_rng(20261124)
NFMIN = 100; VOLWIN = 63
LOG = []
def say(s=""): print(s, flush=True); LOG.append(s)
say(f"# [REFUTE c65 part C] 残り 3 点 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c65_tsmom_c.py)")

def ols_hc1(y, x):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None]); V = XtX_inv @ Sm @ XtX_inv * n / (n - 2)
    return b, np.sqrt(np.diag(V))
def cr1(y, x, cl):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    G = len(np.unique(cl)); Sm = np.zeros((2, 2))
    for g in np.unique(cl):
        m = cl == g; h = Z[m].T @ u[m]; Sm += np.outer(h, h)
    V = XtX_inv @ Sm @ XtX_inv * (G / (G - 1) * (n - 1) / (n - 2))
    return b, np.sqrt(np.diag(V)), G
def runs(x): return np.r_[0, np.cumsum(x[1:] != x[:-1])]
def beta_only(x, y):
    xm = x - x.mean(); return float((xm @ (y - y.mean())) / (xm @ xm))
def p_rotation(x, y, beta, minshift=6):
    n = len(x); bs = np.array([beta_only(np.roll(x, s), y) for s in range(minshift, n - minshift + 1)])
    return float((np.abs(bs) >= abs(beta)).mean()), len(bs)
def wcb_p(y, x, cl, nrep=2000, seed=20261124):
    g = np.random.default_rng(seed)
    y = np.asarray(y, float); n = len(y)
    b, se, G = cr1(y, x, cl); t_obs = b[1] / se[1]
    a0 = y.mean(); u0 = y - a0; uc = np.unique(cl); ts = np.empty(nrep)
    for i in range(nrep):
        w = g.choice([-1.0, 1.0], size=len(uc)); wv = np.empty(n)
        for j, gg in enumerate(uc): wv[cl == gg] = w[j]
        bb, ss, _ = cr1(a0 + wv * u0, x, cl); ts[i] = bb[1] / ss[1]
    return t_obs, float((np.abs(ts) >= abs(t_obs)).mean()), G
def vr_lm(r, q):
    r = np.asarray(r, float); n = len(r); mu = r.mean(); d = r - mu
    s2 = (d ** 2).sum() / (n - 1)
    rq = np.convolve(r, np.ones(q), mode="valid"); m = (n - q + 1)
    s2q = ((rq - q * mu) ** 2).sum() / (m - 1)
    vr = s2q / (q * s2)
    theta = 0.0
    for k in range(1, q):
        dk = ((d[k:] ** 2) * (d[:-k] ** 2)).sum() / ((d ** 2).sum() ** 2) * n
        theta += (2 * (q - k) / q) ** 2 * dk
    z = (vr - 1) / math.sqrt(theta / n) if theta > 0 else float("nan")
    return vr, z

def daily_table(sym, nfmin=NFMIN):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep]})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "nf": g["lc"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index])
    D["wd"] = D["date"].dt.weekday
    D = D[(D.wd <= 4) & (D.nf >= nfmin)].reset_index()
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["year"] = D["date"].dt.year; D["ym"] = D["year"] * 12 + D["date"].dt.month - 1
    return D
def monthly_table(D, L):
    lc = D["lc_last"].to_numpy(); r = D["r"].to_numpy(); ym = D["ym"].to_numpy()
    ends = np.flatnonzero(np.r_[ym[1:] != ym[:-1], True]); rows = []
    for j in range(1, len(ends)):
        e_prev, e = ends[j - 1], ends[j]
        if e_prev - L < 0 or e_prev - VOLWIN + 1 < 1: continue
        sd = np.nanstd(r[e_prev - VOLWIN + 1:e_prev + 1], ddof=1)
        if not np.isfinite(sd) or sd <= 0: continue
        R = (lc[e] - lc[e_prev]) * 1e4; x = np.sign(lc[e_prev] - lc[e_prev - L])
        if x == 0: continue
        rows.append((int(D["year"].iloc[e]), int(ym[e]), R, sd * math.sqrt(21), x))
    M = pd.DataFrame(rows, columns=["year", "ym", "R", "sig", "x"]); M["y"] = M["R"] / M["sig"]; M["S"] = M["x"] * M["y"]
    return M

TAB = {s: daily_table(s) for s in ["XAU", "US500"]}

# ---------- C1 ----------
say("\n## C1 捨てられた在サンプル（US500 L=252・『在データを全部使う』版）")
MU = monthly_table(TAB["US500"], 252)
say(f"- 月次テーブルの範囲: {int(MU.ym.min())//12}-{int(MU.ym.min())%12+1:02d} 〜 {int(MU.ym.max())//12}-{int(MU.ym.max())%12+1:02d}・n {len(MU)}")
for nm, lo, hi in [("c65 の在 2014-2020", 2014, 2020), ("**在データ全部 2013-2020**", 2013, 2020),
                   ("在 2013-2019", 2013, 2019), ("在 2013-2021", 2013, 2021)]:
    m = MU[(MU.year >= lo) & (MU.year <= hi)].reset_index(drop=True)
    x = m.x.to_numpy(); y = m.y.to_numpy()
    if len(np.unique(x)) < 2: say(f"- {nm}: 識別不能"); continue
    b, se = ols_hc1(y, x); rid = runs(x)
    bc, sec, G = cr1(y, x, rid); pr, nr = p_rotation(x, y, b[1])
    _, pw, _ = wcb_p(y, x, rid)
    say(f"- {nm}: n {len(m)}・少数側 {int((x<0).sum())} か月（エピソード {len(np.unique(rid[x<0]))}）"
        f"・β {b[1]:+.4f}・**HC1 t {b[1]/se[1]:+.2f}**・CR1 t {bc[1]/sec[1]:+.2f} (G {G})・回転 p {pr:.3f}・WCB p {pw:.3f}")

# ---------- C4 ----------
say("\n## C4 US500 外 2021-26H1 の少数側 13 か月 = 1 エピソード")
m = MU[MU.year >= 2021].reset_index(drop=True); x = m.x.to_numpy(); y = m.y.to_numpy(); rid = runs(x)
b, se = ols_hc1(y, x); pr, nr = p_rotation(x, y, b[1]); _, pw, _ = wcb_p(y, x, rid)
mm = [f"{int(v)//12}-{int(v)%12+1:02d}" for v in m.ym[x < 0]]
say(f"- n {len(m)}・β {b[1]:+.4f}・HC1 t {b[1]/se[1]:+.2f}・回転 p {pr:.3f}・WCB p {pw:.3f}（G {len(np.unique(rid))}）")
say(f"- 少数側（x=−1）の月 = {', '.join(mm)} ＝ **連続 1 本**（2022 の下落局面）"
    f" → 外の β は『1 つの弱気相場』に対する 1 観測。c65 が外として報告した +0.133 は再現性の検査になっていない。")

# ---------- C2 ----------
say("\n## C2 VR(q) の有限標本帰無を**実際の窓長**で（実データ r_d の iid ブートストラップ・裾保存）")
NB = 1000
for sym, wins in [("XAU", [("在 2011-20", 2011, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]),
                  ("US500", [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026)])]:
    D = TAB[sym]; r = D["r"].to_numpy(); yr = D["year"].to_numpy()
    for wn, lo, hi in wins:
        rr = r[(yr >= lo) & (yr <= hi) & np.isfinite(r)]
        n = len(rr); parts = []
        for q in [2, 5, 10, 21, 63]:
            v, z = vr_lm(rr, q)
            null = np.array([vr_lm(rng.choice(rr, n, replace=True), q)[0] for _ in range(NB)])
            med = np.median(null)
            p2 = 2 * min(float((null <= v).mean()), float((null >= v).mean()))
            parts.append(f"VR({q}) {v:.3f}（帰無中央値 {med:.3f}・両側 p {p2:.3f}・LM z {z:+.2f}）")
        say(f"- {sym} {wn}（n {n} 日）: " + "・".join(parts))
say("- 読み: 帰無中央値が 1 から離れていれば c65 の『VR<1』の見かけは有限標本の偏り。"
    "偏り補正後の両側 p が 0.05 を割るセルが期待（5% × セル数）を超えるかが c65 の『区別不能』の検査。")

# ---------- C3 ----------
say("\n## C3 候補 112 の校正を一般化（HC1 |t|>=2 の FPR を n と少数側件数 n_min の関数で）")
NR = 2000
say("- 帰無 y = 標準正規 iid（c65 の y は sd≈1 の無次元）・x は少数側を 1 ブロックに固めた二値")
say("- n | n_min=1 | 2 | 3 | 5 | 9 | 15 | 20 | 30 | **FPR<=0.06 を満たす最小 n_min**")
for n in [30, 66, 78, 120]:
    row = []; nmins = [1, 2, 3, 5, 9, 15, 20, 30]
    fprs = {}
    for n_min in list(range(1, min(n // 2, 41))):
        h = 0
        for i in range(NR):
            ys = rng.standard_normal(n)
            xb = np.ones(n); st = rng.integers(0, n - n_min); xb[st:st + n_min] = -1.0
            b, se = ols_hc1(ys, xb); h += abs(b[1] / se[1]) >= 2
        fprs[n_min] = h / NR
    ok = [k for k in sorted(fprs) if fprs[k] <= 0.06]
    thr = ok[0] if ok else None
    say(f"  - n={n:>3} | " + " | ".join(f"{fprs[k]:.3f}" if k in fprs else "—" for k in nmins)
        + f" | **{thr if thr else '>'+str(max(fprs))}**（割合 {thr/n*100:.0f}%）" if thr else
        f"  - n={n:>3} | " + " | ".join(f"{fprs[k]:.3f}" if k in fprs else "—" for k in nmins) + " | 該当なし")
say("- 置換案（候補 112 の校正版）: 二値状態で条件づける回帰は **少数側 n_min >= 20 か月（または少数側割合 >= 25%）** を"
    "満たさないセルは HC1 t を報告しない（FPR が名目の 1.5〜14 倍）。満たさない場合は wild cluster bootstrap-t か回転帰無の p を主統計にする。")

say(f"\n- 実行 {time.time()-T0:.1f} s・seed 20261124・書込 data/refute_c65_tsmom_c.md のみ・MT5 なし・外部通信なし")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(LOG) + "\n")
print("saved", OUT)
