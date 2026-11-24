# -*- coding: utf-8 -*-
"""
[cycle65 研究レーン 2026-11-24] 【探索・時系列モメンタム（トレンド追随）— 日次〜月次地平の金・本拠 US500】
源泉マップ §8 に無い行: 時系列モメンタム（Moskowitz–Ooi–Pedersen 2012 "Time series momentum"・Hurst–Ooi–Pedersen 2017 "A century of
evidence"）。機構 = 情報の遅い拡散・アンカリング（初動の過小反応）→ 群集行動・ヘッジャーの遅い再配置（過剰反応）。商品・通貨・債券・株式指数
の先物で 1〜12 か月の自己の過去リターンの符号が翌月を予測すると報告（個別資産 SR 0.2〜0.5・分散化後 1 超）。金は商品のうち最も「金融資産」
的で、ETF・中央銀行・個人の需給が遅いフロー → 成立し得る。我々の既存結果: c19 は日内（1h〜12h）で外 随機歩行・5 分 lag1 負の消滅。c10 は
20 日トレンドの向きが壁→壁 R を条件づけない（null）。**日次〜月次地平で金自身の系列に持続（モメンタム）があるかは未検査**。
補遺 D: 入口フィルタの再発明ではない（市場レベルの源泉の検証）。D2: 在/外/近年 窓別。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/XAU_m5_close.npz・US500_m5_close.npz（bid・暦時刻完全格子・前値埋め）＋ data/refute_c4_scan_paths_2010_2026.json（ゲート ㉛）。
  既存キャッシュのみ・多年 scan 無し・M5 読込なし・MT5 無し・外部通信無し。
セッション日 d = (ET+6h) の暦日（c31/c36/c41 と同じ）。有効日 = 月〜金 ∧ 非 flat 足 ≥100（⑪）。lc_d = ln(当日最終取引足 close)。
  r_d = (lc_d − lc_{d−1})·1e4 bp（前有効日比）。US500 は 2014+（㉒）。
窓（D2・判定月の年）: 在 XAU 2011-20（lookback 252 有効日で 2010 は使えない）／US500 2014-20。外 2021-26H1。近年 2024-26H1（記述）。
主セル（MOP 型・月次・非重複）:
  月 m の最終有効日 e_m。R_m = (lc_{e_m} − lc_{e_{m−1}})·1e4。σ̂_m = sd(r_d, 直前 63 有効日 ≤ e_{m−1})·√21（既知）。y_m = R_m/σ̂_m（ボラ標準化・無次元）。
  x_m = sign(lc_{e_{m−1}} − lc_{e_{m−1}−L})、L = 252 有効日（≈12 か月・文献の標準・スキップ無し）。
  回帰 y_m = α + β·x_m + ε（HC1 t）。**β = ドリフト調整後のモメンタム**（α が無条件ドリフトを吸収）＝主統計。
  併記: 戦略 S_m = x_m·y_m の平均・年率 SR＝mean/sd·√12（ドリフト込み）。分解 E[S] = Cov(x,y) + E[x]·E[y]（後者 = ロングバイアス項）。
  帰無 = x_m の符号反転置換（㊷・2000 回・両側 p）。注入陽性対照 = 在の y に β*·x を注入（β* = SR 0.6 相当 = 0.6/√12 ≈ 0.173）。
判定（主セル 2 つ・Bonferroni(2)・名目 0.025）:
  C1 XAU L=252: PASS = 在 β>0 ∧ HC1 t≥2 ∧ 置換 p<0.025 ∧ 外 β>0 ∧ t≥1.5。在が立たなければ null（在/外 MDE=2se を併記・外は記述）。
  C0 US500 L=252（本拠 ㉝・文献の株式指数先物に効果ありの報告）: 同じ規則。
決着可能性（候補 93・事前宣言）: 月次 n 在 120（XAU）／84（US500）・外 66。sd(y)≈1 → se(β) ≈ 1/√n = 0.091／0.109／0.123。
  MDE(2se) 0.18／0.22／0.25 ＝ 年率 SR 換算 0.63／0.76／0.85（β·√12）。**文献の個別資産 TSMOM（SR 0.2〜0.5）は在でも検出圏外**。
  → 本セルが決着できるのは「金に SR ≥0.6 級のトレンド追随優位があるか」。無ければ null（文献級は排除できない）と書く。
記述（family 宣言・判定に使わない）: L ∈ {21, 63, 126, 252} × 2 市場 × 3 窓 の β・SR（24 セル）。日次重複版（y_d = r_{d+1}/σ̂_d・x_d = sign(lc_d − lc_{d−L})・
  NW(21) t）。年別 S_y と年間リターン・x=+1 の月の割合（ロングバイアスの読み）。分散比 VR(q) q∈{2,5,10,21,63} の在/外（c19 の日内 12h の先）・
  Lo–MacKinlay 不均一分散頑健 z。
ゲート ㉛（本番接続・在のみ）: scan 19404 本の建玉セッション日の**前有効日**までの 252 日トレンド符号と side の整合（ALIGNED／AGAINST）で
  Δμ(R*)（R* = R + ft·1{SL,TP}・ft = 0.1/risk）・Welch t・Δx(pp)・x0 look-ahead 対照。在 |Δμ|<0.048R → 外は走らせない。
事前の予測: XAU 在 β +0.05〜+0.15（t 0.5〜1.6・立たない）・外 β は 2023-26 の一方向上昇で正だが α が吸収して t<1.5・戦略 SR は外で 1 超
  （ロングバイアス項が過半）。US500 在 β ≈0（2014-20 は 2018Q4・2020-03 の反転で負側）。VR(21) 在 >1・外 ≈1。ゲート 在 |Δμ|<0.048。
事前の最重大反証: (1) 月次 n 120 で文献級効果は検出不能＝null は「無い」でなく「SR<0.6」。(2) 外 2021-26H1 の正は 1 本の長い上昇トレンド
  （2023-26）＝独立事象 1〜2 個・年別 S_y と年間リターンの関係で可視化。(3) bid 1 社・セッション最終足＝日次終値の定義依存（COMEX 清算と違う）。
  (4) 符号反転置換は x の持続（自己相関 ≈0.9）を壊す → 帰無 sd は名目側（β の HC1 と並べる・y は非重複なので主は HC1）。(5) 月境界 1 つの定義。
昇格候補・入口/出口規則の提案ではない（源泉マップに行を 1 つ足す）。seed 20261124。
"""
import os, time, json, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c65_tsmom_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261124)
NFMIN = 100; NPERM = 2000
L_MAIN = 252; LS = [21, 63, 126, 252]; VOLWIN = 63
LOG = []
def say(s=""): print(s, flush=True); LOG.append(s)
say(f"# [cycle65] 時系列モメンタム（TSMOM）— 金・本拠 US500・日次〜月次 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c65_tsmom_gold.py)")

# ---------- stats ----------
def ols_hc1(y, x):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None]); V = XtX_inv @ Sm @ XtX_inv * n / (n - 2)
    return b, np.sqrt(np.diag(V))
def ols_nw(y, x, lag):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    Z = np.column_stack([np.ones(n), x]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv
    return b, np.sqrt(np.diag(V))
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return diff, diff / se
def vr_lm(r, q):
    """Lo-MacKinlay VR(q) with heteroskedasticity-robust z (overlapping q-period returns)."""
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

# ---------- session daily table (c41 convention) ----------
def daily_table(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    say(f"- {sym}: npz {len(ts)} 本 {pd.to_datetime(ts[0], unit='s').date()}〜{pd.to_datetime(ts[-1], unit='s').date()} UTC・flat 全体 {flat.mean()*100:.1f}%（⑪）")
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep]})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "nf": g["lc"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index])
    D["wd"] = D["date"].dt.weekday
    allbd = D[D.wd <= 4]
    D = D[(D.wd <= 4) & (D.nf >= NFMIN)].reset_index()
    bd_grid = pd.bdate_range(D.date.min(), D.date.max()); have = set(allbd.index.tolist())
    miss = [d for d in bd_grid if d.toordinal() not in have]
    my = pd.Series([d.year for d in miss]).value_counts().sort_index()
    say(f"- {sym}: 有効セッション日 {len(D)}（月〜金 ∧ nf≥{NFMIN}；平日で nf<{NFMIN} は {len(allbd)-len(D)} 日）・平日で足が無い日 {len(miss)}（年別: " + ", ".join(f"{y} {c}" for y, c in my.items()) + "）（㊵）")
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["year"] = D["date"].dt.year; D["ym"] = D["year"] * 12 + D["date"].dt.month - 1
    return D

def windows(sym):
    if sym == "XAU": return {"在 2011-20": (2011, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
    return {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

def monthly_table(D, L):
    lc = D["lc_last"].to_numpy(); r = D["r"].to_numpy(); ym = D["ym"].to_numpy()
    ends = np.flatnonzero(np.r_[ym[1:] != ym[:-1], True])  # index of last valid day of each month
    rows = []
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

def cell(M, lo, hi, perm=False):
    m = M[(M.year >= lo) & (M.year <= hi)]
    if len(m) < 12: return None
    S = m.S.to_numpy(); sr = S.mean() / S.std(ddof=1) * math.sqrt(12)
    cov = np.cov(m.x, m.y, ddof=0)[0, 1]; drift = m.x.mean() * m.y.mean()
    if m.x.nunique() < 2:  # all months same trend sign -> β not identified (strategy == buy&hold)
        return dict(n=len(m), beta=np.nan, se=np.nan, t=np.nan, mde=np.nan, S=S.mean(), sr=sr, cov=cov, drift=drift, fplus=(m.x > 0).mean(),
                    ybar=m.y.mean(), p=np.nan, uniform=True)
    b, se = ols_hc1(m.y, m.x); beta, seb = b[1], se[1]
    out = dict(n=len(m), beta=beta, se=seb, t=beta / seb, mde=2 * seb, S=S.mean(), sr=sr, cov=cov, drift=drift, fplus=(m.x > 0).mean(),
               ybar=m.y.mean(), p=np.nan, uniform=False)
    if perm:
        x = m.x.to_numpy(); y = m.y.to_numpy(); n = len(x)
        bs = np.empty(NPERM)
        for i in range(NPERM):
            xs = x * rng.choice([-1.0, 1.0], size=n)
            bs[i] = np.polyfit(xs, y, 1)[0]
        out["p"] = (np.abs(bs) >= abs(beta)).mean(); out["perm_sd"] = bs.std()
    return out

def fmt(c):
    if c is None: return "n<12"
    if c.get("uniform"):
        return f"n {c['n']}・**β 識別不能（x が全月 {'+1' if c['fplus']>0.5 else '-1'}＝戦略はバイ&ホールドと同一）**・戦略 S̄ {c['S']:+.3f}/月・SR {c['sr']:+.2f}（全部ロングバイアス項 E[x]E[y] {c['drift']:+.3f}・ȳ {c['ybar']:+.3f}）"
    s = f"n {c['n']}・β {c['beta']:+.3f} (se {c['se']:.3f}・t {c['t']:+.2f}・MDE {c['mde']:.3f}＝SR {c['mde']*math.sqrt(12):.2f})"
    if np.isfinite(c["p"]): s += f"・置換 p {c['p']:.3f}（帰無 sd {c['perm_sd']:.3f}）"
    s += f"・戦略 S̄ {c['S']:+.3f}/月・SR {c['sr']:+.2f}（Cov {c['cov']:+.3f} + ロングバイアス E[x]E[y] {c['drift']:+.3f}・x=+1 {c['fplus']*100:.0f}%・ȳ {c['ybar']:+.3f}）"
    return s

# ====================== run ======================
RES = {}
TABLES = {}
for sym in ["XAU", "US500"]:
    say(f"\n## {sym}")
    D = daily_table(sym); TABLES[sym] = D
    W = windows(sym)
    say(f"- r_d: sd 在 {np.nanstd(D[(D.year>=W[list(W)[0]][0])&(D.year<=2020)].r):.1f} bp・外 {np.nanstd(D[D.year>=2021].r):.1f} bp・|r| 中央値 {np.nanmedian(np.abs(D.r)):.1f} bp")
    # main L=252 monthly
    for L in LS:
        M = monthly_table(D, L)
        say(f"\n### 月次・非重複 L={L} 有効日（{'主セル' if L==L_MAIN else '記述'}）・月 {M.ym.min()//12}-{M.ym.min()%12+1:02d} 〜 {M.ym.max()//12}-{M.ym.max()%12+1:02d}・n {len(M)}")
        for wname, (lo, hi) in W.items():
            c = cell(M, lo, hi, perm=(L == L_MAIN)); say(f"- {wname}: {fmt(c)}")
            RES[(sym, L, wname)] = c
        if L == L_MAIN:
            # injection positive control (in-sample)
            lo, hi = W[list(W)[0]]; m = M[(M.year >= lo) & (M.year <= hi)]
            bstar = 0.6 / math.sqrt(12)
            b, se = ols_hc1(m.y + bstar * m.x, m.x)
            say(f"- 陽性対照（在に β*={bstar:.3f}＝SR 0.6 を注入）: β {b[1]:+.3f}・t {b[1]/se[1]:+.2f}（回収 {(b[1]-RES[(sym,L,list(W)[0])]['beta'])/bstar:.2f}）")
            # yearly table
            say(f"- 年別（L={L}）: 年 | n | S̄_y | ȳ_y（年間 vol 単位） | x=+1 % | β_y")
            for y, g in M.groupby("year"):
                if len(g) < 6: continue
                by = np.polyfit(g.x, g.y, 1)[0] if g.x.nunique() > 1 else float("nan")
                say(f"  - {y} | {len(g)} | {g.S.mean():+.3f} | {g.y.mean():+.3f} | {(g.x>0).mean()*100:.0f} | {by:+.3f}")
            yy = M.groupby("year").agg(S=("S", "mean"), yb=("y", "mean"), n=("S", "size")); yy = yy[yy.n >= 6]
            rs = pd.Series(yy.S).corr(pd.Series(yy.yb), method="spearman"); ra = pd.Series(yy.S).corr(pd.Series(yy.yb.abs()), method="spearman")
            say(f"- 年別 Spearman: S̄_y vs ȳ_y（符号つき） {rs:+.2f}／ vs |ȳ_y| {ra:+.2f}（n 年 {len(yy)}）＝トレンド年の大きさに乗るのは当然・符号つきと強ければロングバイアス")
    # daily overlapping version
    say(f"\n### 日次版（y_d = r_(d+1)/σ̂_d・x_d = sign(lc_d − lc_(d−L))・NW(21) t・記述）")
    lc = D["lc_last"].to_numpy(); r = D["r"].to_numpy(); yr = D["year"].to_numpy()
    sd63 = pd.Series(r).rolling(VOLWIN).std(ddof=1).to_numpy()
    for L in LS:
        x = np.full(len(lc), np.nan); x[L:] = np.sign(lc[L:] - lc[:-L])
        y = np.full(len(lc), np.nan); y[:-1] = r[1:] / sd63[:-1]
        ok = np.isfinite(x) & np.isfinite(y) & (x != 0)
        parts = []
        for wname, (lo, hi) in W.items():
            w = ok & (yr >= lo) & (yr <= hi)
            if w.sum() < 100: parts.append(f"{wname}: n<100"); continue
            S = x[w] * y[w]
            nmin = min((x[w] > 0).sum(), (x[w] < 0).sum())
            if nmin < 20:  # (事後追加・第 3 走) 少数側 <20 日では β が数値的に発散（第 2 走 US500 近年 L=252 t −152 の人工物）→ 識別不能扱い
                parts.append(f"{wname}: n {w.sum()}・β 識別不能（少数側の符号 {nmin} 日 <20）・SR {S.mean()/S.std(ddof=1)*math.sqrt(252):+.2f}（≈バイ&ホールド）"); continue
            b, se = ols_nw(y[w], x[w], 21)
            parts.append(f"{wname}: n {w.sum()}・β {b[1]:+.4f} (t {b[1]/se[1]:+.2f}・MDE {2*se[1]:.4f})・SR {S.mean()/S.std(ddof=1)*math.sqrt(252):+.2f}")
        say(f"- L={L}: " + "／".join(parts))
    # variance ratios on daily returns
    say(f"\n### 分散比 VR(q)（セッション日次 r_d・Lo–MacKinlay 不均一分散頑健 z・記述・c19 の 12h の先）")
    for wname, (lo, hi) in W.items():
        w = (yr >= lo) & (yr <= hi) & np.isfinite(r)
        rr = r[w]
        say(f"- {wname} (n {len(rr)}): " + "・".join(f"VR({q}) {vr_lm(rr,q)[0]:.3f} (z {vr_lm(rr,q)[1]:+.2f})" for q in [2, 5, 10, 21, 63]))
    # yearly VR(21) + shuffle null (事後追加・第 3 走: 第 2 走で 12/13 年が 1 未満に見えたため、年内シャッフル帰無（自己相関を壊し周辺分布を保存）の中央値と片側 p を併記)
    ys = [y for y in sorted(set(yr)) if ((yr == y) & np.isfinite(r)).sum() > 120]
    rows = []; nsig = 0
    for y in ys:
        rr = r[(yr == y) & np.isfinite(r)]; v = vr_lm(rr, 21)[0]
        null = np.array([vr_lm(rng.permutation(rr), 21)[0] for _ in range(300)])
        p = (null <= v).mean(); nsig += p < 0.05
        rows.append(f"{y} {v:.2f} (帰無中央値 {np.median(null):.2f}・p {p:.2f})")
    say("- 年別 VR(21) vs 年内シャッフル帰無 300 回: " + "・".join(rows))
    say(f"- 年別 VR(21): 帰無中央値を下回る年 {sum(1 for y in ys if True)} 中 {sum(1 for s in rows if float(s.split()[1]) < float(s.split('帰無中央値 ')[1].split('・')[0]))}・片側 p<0.05 の年 {nsig}/{len(ys)}（期待 {0.05*len(ys):.1f}）")

# ====================== gate ㉛ ======================
say("\n## ゲート ㉛（本番接続・在のみ）: 建玉前有効日までの 252 日トレンド符号 × side（scan 19404 本）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
tr = pd.DataFrame(d["trades"])
D = TABLES["XAU"]; lc = D["lc_last"].to_numpy(); o_arr = D["o"].to_numpy()
ent = pd.to_datetime(tr.entry_time, unit="s", utc=True).dt.tz_convert(NY)
sess_o = np.array([(t + pd.Timedelta(hours=6)).date().toordinal() for t in ent])
idx_prev = np.searchsorted(o_arr, sess_o, side="left") - 1  # last valid session strictly before entry session
ok = idx_prev - L_MAIN >= 0
trend = np.full(len(tr), np.nan); trend[ok] = np.sign(lc[idx_prev[ok]] - lc[idx_prev[ok] - L_MAIN])
tr["trend"] = trend
tr["ft"] = 0.1 / tr.risk; tr["Rs"] = tr.R + tr.ft * tr.exit.isin(["SL", "TP"])
tr["aligned"] = ((tr.side == "BUY") & (tr.trend > 0)) | ((tr.side == "SELL") & (tr.trend < 0))
tr["tp"] = (tr.exit == "TP").astype(float)
assert (sess_o[ok] > o_arr[idx_prev[ok]]).all(), "look-ahead: prev session must be strictly before entry session"
say(f"- トレンド付与 {ok.sum()}/{len(tr)} 本（2010 の 252 日未満を除く）・BUY {int((tr.side=='BUY').sum())}・up トレンド {int((tr.trend>0).sum())}・aligned 率 {tr.aligned[ok].mean()*100:.1f}%")
for wname, (lo, hi) in {"在 2011-20": (2011, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}.items():
    m = tr[ok & (tr.year >= lo) & (tr.year <= hi)]
    a, g = m[m.aligned], m[~m.aligned]
    dmu, t = welch(a.Rs, g.Rs); dx, tx = welch(a.tp, g.tp); dx0, tx0 = welch(a.x0, g.x0)
    se = dmu / t if t != 0 else float("nan")
    say(f"- {wname}: n aligned {len(a)}／against {len(g)}・Δμ(R*) {dmu:+.4f} (t {t:+.2f}・MDE {2*abs(se):.3f})・ΔTP {dx*100:+.2f} pp (t {tx:+.2f})・x0 look-ahead 対照 Δ {dx0:+.4f} (t {tx0:+.2f})"
        + ("" if lo != 2011 else ("　→ 在 |Δμ|<0.048R ＝ 外は判定に使わない（記述のみ）" if abs(dmu) < 0.048 else "　→ 在 |Δμ|≥0.048R ＝ 外を判定")))

# ====================== verdict ======================
say("\n## 判定（事前規則・Bonferroni(2)・名目 0.025）")
def verdict(sym):
    W = list(windows(sym)); cin = RES[(sym, L_MAIN, W[0])]; cout = RES[(sym, L_MAIN, W[1])]
    ins = cin["beta"] > 0 and cin["t"] >= 2 and cin["p"] < 0.025
    outs = cout["beta"] > 0 and cout["t"] >= 1.5
    if ins and outs: v = "PASS"
    elif ins: v = "在 PASS → 外 不再現（null）"
    else: v = "null（在 不成立）"
    say(f"- {'C1' if sym=='XAU' else 'C0'} {sym} L=252: {v}。在 β {cin['beta']:+.3f} t {cin['t']:+.2f} p {cin['p']:.3f}・MDE {cin['mde']:.3f}（SR {cin['mde']*math.sqrt(12):.2f}）／外 β {cout['beta']:+.3f} t {cout['t']:+.2f}・MDE {cout['mde']:.3f}（SR {cout['mde']*math.sqrt(12):.2f}）")
    return v
V1 = verdict("XAU"); V0 = verdict("US500")
say(f"\n- 実行 {time.time()-T0:.1f} s・seed 20261124・多年 scan なし・MT5 なし・外部通信なし")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(LOG) + "\n")
print("saved", OUT)
