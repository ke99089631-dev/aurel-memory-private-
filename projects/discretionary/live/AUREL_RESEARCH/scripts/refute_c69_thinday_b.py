# -*- coding: utf-8 -*-
"""
[REFUTE c69 第 2 走 / 2026-11-25] 第 1 走（refute_c69_thinday.py）の結果を見てから書いた。目的は 3 つ:
**自分の攻撃の弱点を閉じる**・**2 本の失敗した攻撃を正しいセルでやり直す**・**攻撃の副産物を正しく推論する**。

=== 事前固定（第 1 走の数字は見たが、以下の判定規則は本 docstring を書いた時点で固定・以後書き換えない）===

B1 【第 1 走 A2 への自己反証 = 弱い操作変数の疑い】A2(ii)「前半 RV → 後半 ρ1」の β ≈ 0 (在 t −0.16) は
   「日のボラ状態は ρ1 を動かさない」ではなく **「前半 RV が日のボラ状態の弱い代理でしかない（減衰バイアス）」**
   でも同じ形になる。古典的な errors-in-variables: 真の回帰子を λ_d、代理を λ_d + e とすると β は
   Var(λ)/Var(代理) 倍に減衰する。そしてその減衰率は **lrv_h2 を lrv_h1 に回した 1 段目の傾き**に等しい。
   → よって正しい検定は **2SLS**: ρ1(後半) を lrv(後半) に回し、**lrv(前半) を操作変数**にする（共有足ゼロ・
   同一標本条件付けだけが除かれ、減衰は補正される）。前日 RV を操作変数にした版も出す。
   **判定規則: T2 が survive する条件 = β_IV の符号が OLS と同じ(+) ∧ 在 |t| ≥ 2 ∧ 1 段目 F ≥ 10。
   1 段目 F ≥ 10 なのに β_IV が 0 近傍（|t| < 2）なら「弱い操作変数」の逃げ道は閉じ、T2 は broken。
   1 段目 F < 10 なら私の A2 は決着不能（overreach）として撤回する。**
   併せて corr(lrv_h1, lrv_h2)・corr(lrv_prev, lrv)・各 1 段目 F を印字。
   さらに A2(iii)「後半 RV → 前半 ρ1 は β +0.021 t +5.38 で生き残る」という**時間的非対称**を数字で詰める:
   同じ 2SLS を向きを変えて（lrv_h1 を lrv_h2 で操作変数化）走らせ、非対称が 1 段目の強さの差で説明できるかを見る。

B2 【第 1 走 A4 のセル違いを修正】A4 は全標本の (ρ1_5, ρ1_15) で φ を探したが、c69 の読み分け主張は
   **最静分位 Q1** と **THIN 群**でなされている（「Q1 の 15 分 ρ1 −0.059 ≈ 5 分 −0.057」）。その 2 群で
   ρ1_5・ρ1_15・ρ1_30 と、φ グリッド 0.0〜0.9（刻み 0.1）の sim 比を出し直す。
   **判定規則: 観測の (ρ1_15/ρ1_5, ρ1_30/ρ1_5) の組を ±0.20 以内で同時に再現する φ が (0,1) に存在すれば、
   c69 の「15 分で減衰しない ⇒ 価格水準の構造（気配人工物ではない）」は bid 単系列では成立しない ⇒ 読み分け broken。
   存在しなければ読み分け survived（＝私の攻撃の失敗を 2 度目も記録する）。**

B3 【第 1 走 A5 の正しい効果量】置換帰無 (c)（曜日 × log RV 十分位 保存）の帰無平均は 0 ではなく 在 −0.053 /
   外 −0.043 だった＝生の D_ρ1 の半分以上が「同じ曜日・同じ静けさの擬似祝日」で再現される。
   → **祝日固有の効果量 = 観測 − 帰無平均**、se = 帰無 sd として印字し、c69 の生の headline との比を出す。
   置換は B=20000 に増やす（第 1 走は 4000）。

B4 【第 1 走 A7 の副産物を正しく推論する = 攻撃が逆に当たった箇所】第 1 走で THIN 群の契約回帰は地平を
   延ばすと伸びた（近年 π(6) +0.926 bp vs 往復 0.52 bp = 179%）。c69 は h=1 しか測っておらず「受取り不可」と
   書いた＝その結論は**地平依存**。ただし第 1 走の π(h) は**毎足重複**で se が無い。正しくやる:
     (a) **非重複**: 窓内で h 本ごとに 1 回だけ建てる（60/h 回）＝往復を本当に h 本に 1 回払う形。
     (b) 日クラスタ bootstrap B=2000 で se・z。
     (c) **コスト後**の純額 = π_net(h) = π(h) − 往復コスト（×1 / ×2 / ×3）を THIN と対照で。
     (d) n が小さい（近年 18 日）ので MDE も印字。
   **判定規則: 非重複かつコスト後で 在 の z ≥ +2 ∧ 外 同符号 z ≥ +1.5 を満たさなければ「受け取れない」は
   c69 の結論どおり survived（地平の指摘は射程の訂正にとどまる）。満たした場合は c69 の H2 結論が broken だが、
   それは私が事後に作った新しいセル＝憲章 5 条により新規の事前固定として backlog に回し、昇格候補にはしない。**

B5 Q1 と THIN の重なり（T1 と T2 が同じものか別のものか）: THIN 日が通常日 RV 分位のどこに落ちるかの分布、
   および THIN 群 vs「RV 一致（最近傍 log RV・同曜日）通常日」の ρ1 差を、第 1 走の置換とは独立に印字。

読むのは AUREL_RESEARCH/ 配下のみ。発注なし・デモ発注なし・本番ファイル編集なし・プロセス/執行機/ライブサーバ
接触なし・MT5 なし・プロップ（g4_/FundingPips）参照なし・秘密なし・外部通信なし・多年 scan なし。
書き込みは AUREL_RESEARCH/data/refute_c69_thinday_b.md のみ。seed 20261125。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c69_thinday_b.md"); L = []
NY = "America/New_York"; SEED = 20261125; NB = 2000; NPERM = 20000
def say(s=""):
    print(s, flush=True); L.append(s)
say(f"# [REFUTE c69 第 2 走] 2SLS で T2 の逃げ道を閉じる・A4 を Q1/THIN でやり直す・祝日固有の効果量・契約回帰の地平 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c69_thinday_b.py)")
say("")

zz = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)) * 1e4

def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451; month = (h + l - 7*m + 114) // 31; day = ((h + l - 7*m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7*(n-1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m+1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d
THIN, FULL, BOND, HALF = {}, set(), set(), set()
for y in range(2010, 2027):
    THIN[nth_weekday(y,1,0,3)] = "MLK"; THIN[nth_weekday(y,2,0,3)] = "Presidents"; THIN[last_weekday(y,5,0)] = "Memorial"
    if y >= 2022: THIN[observed(dt.date(y,6,19))] = "Juneteenth"
    THIN[observed(dt.date(y,7,4))] = "July4"; THIN[nth_weekday(y,9,0,1)] = "Labor"; THIN[nth_weekday(y,11,3,4)] = "Thanksgiving"
    for h in (observed(dt.date(y,1,1), sat_to_fri=False), easter(y) - dt.timedelta(days=2), observed(dt.date(y,12,25))):
        if h is not None: FULL.add(h)
    BOND.add(nth_weekday(y,10,0,2)); BOND.add(observed(dt.date(y,11,11)))
    HALF.add(nth_weekday(y,11,3,4) + dt.timedelta(days=1))
    for d in (dt.date(y,7,3), dt.date(y,12,24)):
        if d.weekday() < 5 and d not in FULL and d not in THIN: HALF.add(d)
HOL_ALL = set(THIN) | FULL | BOND | HALF
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1+1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
EV = (set(d.date() for d in nfp_dates_v2())
      | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")).date).dt.date)
      | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date).dt.date))

dates = pd.date_range("2010-01-04", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); ddate = np.array([d.date() for d in dates]); yr = dates.year.to_numpy(); wdy = dates.weekday.to_numpy()
di = {d: i for i, d in enumerate(ddate)}
T8 = epoch_et(dates, 8, 0); M = np.full((N, 60), np.nan); PX = np.full(N, np.nan)
ok = np.isfinite(T8); i0 = np.clip(np.searchsorted(ts, T8[ok].astype(np.int64)), 0, len(ts)-60)
good = (ts[i0] == T8[ok].astype(np.int64)) & (ts[i0+59] == T8[ok].astype(np.int64) + 59*300)
rows = np.where(ok)[0][good]; M[rows] = r[i0[good][:, None] + np.arange(60)[None, :]]; PX[rows] = cl[i0[good]]

is_thin = np.array([d in THIN for d in ddate]); is_hol = np.array([d in HOL_ALL for d in ddate])
is_ev = np.array([d in EV for d in ddate])
full_row = np.isfinite(M).all(1); nfw = np.where(full_row, np.mean(M != 0, axis=1), np.nan)
elig = full_row & (nfw >= 0.5) & ~is_ev; norm = elig & ~is_hol
WINS = [("在 2010-20", (yr >= 2010) & (yr <= 2020)), ("外 2021-26H1", yr >= 2021), ("近年 2024-26H1", yr >= 2024)]

a_d = np.nansum(M[:, 1:]*M[:, :-1], 1); b_d = np.nansum(M[:, 1:]**2, 1); rv_d = np.nansum(M**2, 1)
H1, H2 = M[:, :30], M[:, 30:]
a1 = np.nansum(H1[:, 1:]*H1[:, :-1], 1); b1 = np.nansum(H1[:, 1:]**2, 1); rv1 = np.nansum(H1**2, 1)
a2 = np.nansum(H2[:, 1:]*H2[:, :-1], 1); b2 = np.nansum(H2[:, 1:]**2, 1); rv2 = np.nansum(H2**2, 1)
lv  = np.where(elig & (rv_d > 0), np.log(np.maximum(rv_d, 1e-12)), np.nan)
lv1 = np.where(elig & (rv1 > 0), np.log(np.maximum(rv1, 1e-12)), np.nan)
lv2 = np.where(elig & (rv2 > 0), np.log(np.maximum(rv2, 1e-12)), np.nan)
lv_prev = np.full(N, np.nan); lv_prev[1:] = lv[:-1]

def ols_hc1(X, y):
    XtXi = np.linalg.pinv(X.T @ X); bh = XtXi @ (X.T @ y); e = y - X @ bh
    n, k = X.shape; S = (X*e[:, None]).T @ (X*e[:, None]); V = XtXi @ S @ XtXi * (n/(n-k))
    return bh, np.sqrt(np.diag(V))
def tsls(y, x, z):
    """one endogenous regressor + intercept, one instrument. returns beta, HC1 se, first-stage F"""
    n = len(y); Z = np.column_stack([np.ones(n), z]); Xc = np.column_stack([np.ones(n), x])
    bf, sef = ols_hc1(Z, x); F = (bf[1]/sef[1])**2
    xh = Z @ bf; Xh = np.column_stack([np.ones(n), xh])
    bh = np.linalg.pinv(Xh.T @ Xh) @ (Xh.T @ y); e = y - Xc @ bh
    A = np.linalg.pinv(Xh.T @ Xc); S = (Xh*e[:, None]).T @ (Xh*e[:, None])
    V = A @ S @ A.T * (n/(n-2))
    return bh[1], math.sqrt(max(V[1, 1], 0)), F

# ====================================================================== B1
say("## B1 2SLS — 「弱い操作変数」の逃げ道を閉じる（T2 への主攻撃の確定版）")
say("- 設計: y = ρ1_d(後半 30 本)、x = log RV(後半)、z = log RV(前半) ＝ 共有足ゼロ・減衰補正済み。")
say("- 比較のため OLS(同一標本)・OLS(前半 RV・減衰あり)・2SLS を並べる。前日 RV を z にした全日版も。")
say("")
say("| 窓 | n | corr(lv1,lv2) | 1段目 F | OLS 同一標本 β (t) | OLS 代理(前半) β (t) | **2SLS β (t)** | 2SLS/OLS |")
say("|---|---|---|---|---|---|---|---|")
B1 = {}
for nm, wm in WINS:
    sel = norm & wm & np.isfinite(lv1) & np.isfinite(lv2) & (b2 > 0) & (b1 > 0)
    ix = np.where(sel)[0]; y = a2[ix]/b2[ix]; x = lv2[ix]; z = lv1[ix]
    bo, seo = ols_hc1(np.column_stack([np.ones(len(ix)), x]), y)
    bp, sep = ols_hc1(np.column_stack([np.ones(len(ix)), z]), y)
    bi, sei, F = tsls(y, x, z)
    B1[nm] = dict(n=len(ix), F=F, ols=(bo[1], bo[1]/seo[1]), proxy=(bp[1], bp[1]/sep[1]), iv=(bi, bi/sei))
    say(f"| {nm} | {len(ix)} | {np.corrcoef(z, x)[0,1]:+.3f} | {F:.1f} | {bo[1]:+.4f} ({bo[1]/seo[1]:+.2f}) | {bp[1]:+.4f} ({bp[1]/sep[1]:+.2f}) | **{bi:+.4f} ({bi/sei:+.2f})** | {bi/bo[1]*100 if bo[1] else float('nan'):.0f}% |")
say("")
say("### 向きを逆にした 2SLS（y = ρ1 前半・x = log RV 前半・z = log RV 後半）＝ A2(iii) の非対称を詰める")
say("| 窓 | n | 1段目 F | OLS 同一標本 β (t) | **2SLS β (t)** |")
say("|---|---|---|---|---|")
for nm, wm in WINS:
    sel = norm & wm & np.isfinite(lv1) & np.isfinite(lv2) & (b2 > 0) & (b1 > 0)
    ix = np.where(sel)[0]; y = a1[ix]/b1[ix]
    bo, seo = ols_hc1(np.column_stack([np.ones(len(ix)), lv1[ix]]), y)
    bi, sei, F = tsls(y, lv1[ix], lv2[ix])
    say(f"| {nm} | {len(ix)} | {F:.1f} | {bo[1]:+.4f} ({bo[1]/seo[1]:+.2f}) | **{bi:+.4f} ({bi/sei:+.2f})** |")
say("")
say("### 前日 RV を操作変数にした全日版（y = ρ1 全 60 本・x = log RV 当日・z = log RV 前日）")
say("| 窓 | n | corr(lv_prev,lv) | 1段目 F | OLS 同一標本 β (t) | **2SLS β (t)** | 2SLS/OLS |")
say("|---|---|---|---|---|---|---|")
for nm, wm in WINS:
    sel = norm & wm & np.isfinite(lv) & np.isfinite(lv_prev) & (b_d > 0)
    ix = np.where(sel)[0]; y = a_d[ix]/b_d[ix]
    bo, seo = ols_hc1(np.column_stack([np.ones(len(ix)), lv[ix]]), y)
    bi, sei, F = tsls(y, lv[ix], lv_prev[ix])
    say(f"| {nm} | {len(ix)} | {np.corrcoef(lv_prev[ix], lv[ix])[0,1]:+.3f} | {F:.1f} | {bo[1]:+.4f} ({bo[1]/seo[1]:+.2f}) | **{bi:+.4f} ({bi/sei:+.2f})** | {bi/bo[1]*100 if bo[1] else float('nan'):.0f}% |")
say("")

# ====================================================================== B2
say("## B2 A4 のやり直し — c69 の読み分け主張は Q1（最静分位）と THIN 群でなされている")
V_all = np.nansum(b_d[norm]) / max((np.isfinite(b_d) & norm).sum()*59, 1)
rho_all = np.nansum(a_d[norm])/np.nansum(b_d[norm]); sig_u2 = max(-rho_all*V_all, 1e-9)
say(f"- 校正（第 1 走と同じ）: 全体 ρ1 {rho_all:+.5f}・V {V_all:.2f} bp² → σ_u² {sig_u2:.4f} bp²")
def agg_rho(mask, h):
    k = 60 // h; X = M[:, :k*h].reshape(N, k, h).sum(2)
    aa = np.nansum(X[:, 1:]*X[:, :-1], 1); bb = np.nansum(X[:, 1:]**2, 1)
    sb = np.nansum(bb[mask]); return (np.nansum(aa[mask])/sb) if sb > 0 else np.nan
def sim_ratios(sel_idx, phi, nsim=60, seed=SEED):
    g = np.random.default_rng(seed); nd = len(sel_idx)
    se2 = np.maximum(b_d[sel_idx]/59 - 2*sig_u2, 1e-9); out = []
    for s in range(nsim):
        eff = g.standard_normal((nd, 60)) * np.sqrt(se2)[:, None]
        if phi <= 0:
            u = g.standard_normal((nd, 61)) * math.sqrt(sig_u2)
        else:
            eps = g.standard_normal((nd, 61)) * math.sqrt(sig_u2*(1-phi**2))
            u = np.empty((nd, 61)); u[:, 0] = g.standard_normal(nd)*math.sqrt(sig_u2)
            for j in range(1, 61): u[:, j] = phi*u[:, j-1] + eps[:, j]
        Ms = eff + np.diff(u, axis=1); rr = []
        for h in (1, 3, 6):
            k = 60//h; X = Ms[:, :k*h].reshape(nd, k, h).sum(2)
            rr.append(np.sum(X[:, 1:]*X[:, :-1])/np.sum(X[:, 1:]**2))
        out.append(rr)
    o = np.array(out); m = o.mean(0)
    return m[0], (m[1]/m[0] if m[0] else np.nan), (m[2]/m[0] if m[0] else np.nan)
PHIS = [round(0.1*i, 1) for i in range(10)]
for gname in ("Q1 最静分位（通常平日）", "THIN 群"):
    say("")
    say(f"### {gname}")
    say("| 窓 | n | ρ1_5 | ρ1_15 | ρ1_30 | 比 15/5 | 比 30/5 | 同時再現する φ（±0.20） | φ=0 の比 15/5 | φ=0.5 | φ=0.8 |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    for nm, wm in WINS:
        if gname.startswith("Q1"):
            ixw = np.where(norm & wm & np.isfinite(lv))[0]
            q = np.quantile(lv[ixw], .2); mk = np.zeros(N, bool); mk[ixw[lv[ixw] <= q]] = True
        else:
            mk = is_thin & elig & wm
        r5, r15, r30 = agg_rho(mk, 1), agg_rho(mk, 3), agg_rho(mk, 6)
        o15, o30 = (r15/r5 if r5 else np.nan), (r30/r5 if r5 else np.nan)
        ixs = np.where(mk & np.isfinite(b_d) & (b_d > 0))[0]
        hits, shown = [], {}
        for phi in PHIS:
            _, s15, s30 = sim_ratios(ixs, phi, nsim=60, seed=SEED+int(phi*1000))
            shown[phi] = s15
            if np.isfinite(s15) and np.isfinite(s30) and abs(s15-o15) <= 0.20 and abs(s30-o30) <= 0.20:
                hits.append(f"{phi:.1f}")
        say(f"| {nm} | {mk.sum()} | {r5:+.4f} | {r15:+.4f} | {r30:+.4f} | **{o15:+.2f}** | **{o30:+.2f}** | {'・'.join(hits) if hits else '**なし**'} | {shown[0.0]:+.2f} | {shown[0.5]:+.2f} | {shown[0.8]:+.2f} |")
say("")

# ====================================================================== B3
say("## B3 祝日固有の効果量 — 置換帰無 (c) を B=20000 に増やし、観測 − 帰無平均 を効果量として出す")
OFF = [-28, -21, -14, -7, 7, 14, 21, 28]
NEI = np.full((N, len(OFF)), -1, dtype=np.int64)
for j, o in enumerate(OFF):
    for i in range(N):
        NEI[i, j] = di.get(ddate[i] + dt.timedelta(days=o), -1)
ctrl_ok = elig & ~is_hol
def controls_of(tmask, exclude=None):
    nn = NEI[tmask].ravel(); nn = nn[nn >= 0]; m = np.zeros(N, bool); m[nn] = True; m &= ctrl_ok
    if exclude is not None: m &= ~exclude
    return m
def rho(mask):
    sb = np.nansum(b_d[mask]); return np.nansum(a_d[mask])/sb if sb > 0 else np.nan
dec = np.full(N, -1)
for nm, wm in WINS:
    ixw = np.where(elig & wm & np.isfinite(lv))[0]
    if len(ixw) > 20:
        qs = np.quantile(lv[ixw], np.linspace(.1, .9, 9)); dec[ixw] = np.digitize(lv[ixw], qs)
say("")
say("| 窓 | 生 D_ρ1 | 帰無(c) 平均 | 帰無 sd | **固有効果量 = 観測−帰無平均** | z | p(両側) | 生の何 % が擬似祝日で再現 |")
say("|---|---|---|---|---|---|---|---|")
for nm, wm in WINS:
    tm = is_thin & elig & wm; treal = np.where(tm)[0]
    obs = rho(tm) - rho(controls_of(tm, exclude=is_thin))
    cand = np.where(elig & ~is_hol & wm)[0]
    memb, need = {}, {}
    for w in range(5):
        for dq in range(10):
            memb[(w,dq)] = cand[(wdy[cand] == w) & (dec[cand] == dq)]
            need[(w,dq)] = int(((wdy[treal] == w) & (dec[treal] == dq)).sum())
    g = np.random.default_rng(SEED+101); out = []
    for k in range(NPERM):
        pick = []
        for key, nn in need.items():
            if nn == 0: continue
            pl = memb[key]
            pick.append(pl if len(pl) <= nn else g.choice(pl, nn, False))
        if not pick: continue
        tmp = np.zeros(N, bool); tmp[np.concatenate(pick)] = True
        cmp_ = controls_of(tmp, exclude=tmp | is_thin)
        if cmp_.sum() < 10: continue
        out.append(rho(tmp) - rho(cmp_))
    out = np.array([v for v in out if np.isfinite(v)])
    mu, sd = out.mean(), out.std(ddof=1)
    eff = obs - mu; z = eff/sd
    p = (np.sum(np.abs(out - mu) >= abs(eff)) + 1)/(len(out)+1)
    say(f"| {nm} | {obs:+.4f} | {mu:+.4f} | {sd:.4f} | **{eff:+.4f}** | {z:+.2f} | {p:.4f} | {mu/obs*100:.0f}% |")
say("")

# ====================================================================== B4
say("## B4 契約回帰の地平 — 第 1 走の副産物（c69 の H2「受取り不可」は h=1 限定）を正しく推論する")
cost1 = 0.16/PX*1e4
def pi_nonoverlap(h, mask, B=NB, seed=SEED+7):
    """trade only every h-th bar inside the window: entries at j = 0, h, 2h, ... signal = -sign(r_j), hold h bars"""
    starts = np.arange(0, 60-h, h)
    pd_ = np.full(N, np.nan); ntr = np.zeros(N)
    prev = M[:, starts]
    cum = np.stack([np.nansum(M[:, s+1:s+1+h], 1) for s in starts], axis=1)
    mk = (prev != 0) & np.isfinite(cum)
    v = np.where(mk, -np.sign(prev)*cum, np.nan)
    with np.errstate(invalid="ignore"):
        pd_ = np.nanmean(v, 1); ntr = mk.sum(1)
    ix = np.where(mask & np.isfinite(pd_))[0]
    if len(ix) < 3: return np.nan, np.nan, np.nan, 0
    g = np.random.default_rng(seed); obs = np.mean(pd_[ix])
    bs = np.array([np.mean(pd_[g.choice(ix, len(ix), True)]) for _ in range(B)])
    se = bs.std(ddof=1)
    return obs, se, obs/se if se > 0 else np.nan, int(np.mean(ntr[ix]))
say("- 非重複版: 窓内で h 本ごとに 1 回建て h 本保有（往復は 1 トレードに 1 回）。日クラスタ bootstrap B=2000。")
say("")
say("| 窓 | 群 | h | 回/日 | π(h) bp | se | z | 往復×1 | 純 ×1 (z) | 純 ×2 | 純 ×3 | MDE(2se) |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|")
for nm, wm in WINS:
    tm = is_thin & elig & wm; cm = controls_of(tm, exclude=is_thin)
    for lab, mk in [("THIN", tm), ("対照", cm)]:
        c1 = np.nanmedian(cost1[mk])
        for h in (1, 3, 6, 12):
            o, se, z, ntr = pi_nonoverlap(h, mk)
            if not np.isfinite(o): continue
            n1 = o - c1; zn = n1/se if se > 0 else np.nan
            say(f"| {nm} | {lab} | {h} | {ntr} | {o:+.3f} | {se:.3f} | {z:+.2f} | {c1:.2f} | **{n1:+.3f} ({zn:+.2f})** | {o-2*c1:+.3f} | {o-3*c1:+.3f} | {2*se:.3f} |")
say("")

# ====================================================================== B5
say("## B5 T1 と T2 は同じものか — THIN 日の RV 分位分布と、log RV 最近傍・同曜日の一致対照")
say("")
say("| 窓 | THIN 日の通常日 RV 分位（Q1..Q5 の日数） | THIN の log RV 中位 | 通常日 Q1 の log RV 中位 |")
say("|---|---|---|---|")
for nm, wm in WINS:
    ixw = np.where(norm & wm & np.isfinite(lv))[0]
    qs = np.quantile(lv[ixw], [.2, .4, .6, .8])
    tix = np.where(is_thin & elig & wm & np.isfinite(lv))[0]
    bk = np.digitize(lv[tix], qs); cnt = [int((bk == k).sum()) for k in range(5)]
    q1 = lv[ixw][lv[ixw] <= qs[0]]
    say(f"| {nm} | {cnt} | {np.median(lv[tix]):+.2f} | {np.median(q1):+.2f} |")
say("")
say("### log RV 最近傍 × 同曜日 一致対照（1:4・置換とは独立）")
say("| 窓 | n(THIN) | ρ1 THIN | ρ1 一致対照 | D | z(日 bootstrap) | 対照 log RV / THIN log RV |")
say("|---|---|---|---|---|---|---|")
for nm, wm in WINS:
    tix = np.where(is_thin & elig & wm & np.isfinite(lv))[0]
    cand = np.where(norm & wm & np.isfinite(lv))[0]
    chosen = []
    for i in tix:
        pool = cand[(wdy[cand] == wdy[i])]
        if len(pool) == 0: pool = cand
        d = np.abs(lv[pool] - lv[i]); chosen += list(pool[np.argsort(d)[:4]])
    chosen = np.array(sorted(set(chosen)))
    mt = np.zeros(N, bool); mt[tix] = True; mc = np.zeros(N, bool); mc[chosen] = True
    D = rho(mt) - rho(mc)
    g = np.random.default_rng(SEED+31)
    bs = np.array([ (np.nansum(a_d[g.choice(tix, len(tix), True)])/np.nansum(b_d[g.choice(tix, len(tix), True)])) for _ in range(5)])
    bsd = []
    for _ in range(NB):
        t2 = g.choice(tix, len(tix), True); c2 = g.choice(chosen, len(chosen), True)
        bsd.append(np.nansum(a_d[t2])/np.nansum(b_d[t2]) - np.nansum(a_d[c2])/np.nansum(b_d[c2]))
    sd = np.std(bsd, ddof=1)
    say(f"| {nm} | {len(tix)} | {rho(mt):+.4f} | {rho(mc):+.4f} | **{D:+.4f}** | {D/sd:+.2f} | {np.median(lv[chosen]):+.2f} / {np.median(lv[tix]):+.2f} |")

say("")
say(f"（実行 {time.time()-T0:.1f}s・seed {SEED}・perm {NPERM}・boot {NB}）")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n--> {OUT}")
