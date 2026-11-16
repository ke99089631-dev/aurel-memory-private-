# -*- coding: utf-8 -*-
"""
[REFUTE c43 / 反証レーン 2026-11-17 03:30] 標的 = cycle43（2026-11-17 00:40）の **唯一の正の持ち越し**:
「金の金曜 15:30→16:00 ET → 月曜 10:00 は外だけ継続」。research 側の枝 (d) は、これを c36 の前向き 5 曜日ペア
セル（金→月）の窓指定に併記する＝事実上の前向き登録。ここで壊す。

標的の数字（data/c43_expiration_day_effects_result.md・XAU・対照金曜＝第 3 金曜でない有効金曜）:
  外 2021-26H1 (n_ctrl 208): β_ctrl = +1.843 (HC1 t +2.70)・符号戦略（c43 は反転向き）S_ctrl = -20.8 (t -3.15)
     ⇒ **継続向き S_cont = +20.8 bp/日 (t +3.15)**
  近年 2024-26H1 (n_ctrl 94): β_ctrl = +2.175 (t +2.68)・S_cont = +37.2 (t +3.05)
  在 2012-20  (n_ctrl 340): β_ctrl = -0.328 (t -0.71)・S_cont = -3.6 (t -0.87)  ← 在 null
回帰は c43 と同じプール OLS（有効金曜のみ）: NEXT = α + β·LAST + δ·(LAST·E) + γ·E、E = OPEX（第 3 金曜）。
β_ctrl はその LAST 係数。S_ctrl = mean(sign(LAST)·NEXT | 対照金曜)（継続向き）。

=== 事前固定（この docstring を書き終えてから数字を見る）===
データ: data/macro/XAU_m5_close.npz（bid・2010-01〜2026-06-30・既存キャッシュのみ）。scan 無し・MT5 無し・外部通信無し・
  発注無し・本番ファイル読取のみ（本スクリプトは本番を読まない）。書き込みは scripts/ と data/ の自分の成果物だけ。
格子・窓・暦・有効日の定義は c43 と同一（P(T)=ts==T-300 の close／LAST 15:30→16:00・CASH 09:30→15:30・
  NEXT D 16:00 → 次営業日 10:00（最大 5 暦日先）／有効 = 窓有限 ∧ LAST≠0 ∧ CASH≠0／OPEX = 第 3 金曜・聖金曜日の月は除外）。
窓: 在 2012-20／外 2021-26H1／近年 2024-26H1（D2 遵守・16 年一括は使わない）。seed 20261117b。NPERM = 2000。

攻撃（R1-R12）と**事前の破壊判定**（どれか 1 つでも当たれば「昇格候補・前向きセルとしては broken」）:
  R1 複製: β_ctrl・S_cont を ±0.05／±1.0 bp 以内で再現。再現できない → broken（仕様不一致）。
  R2 影響点: |LAST| 上位 k（k=1,2,3）除去後の β_ctrl、|s·NEXT| 寄与上位 k 除去後の S_cont、LOYO（年 1 つ抜き）最小 t、
     上位 3 日の二乗和寄与率。**BREAK-A = 上位 3 日除去で t<1.5**（c43b が金の LAST5 VR 7.5 を殺したのと同じ型）。
  R3 ドリフト分解: S_cont = μ_NEXT·mean(s) + mean(s·(NEXT−μ_NEXT))。外era の金は上昇トレンド＝μ_NEXT>0 ∧ 符号不均衡
     mean(s)>0 なら「継続」でなく「ロング金のキャリー」。**BREAK-B = demean 後の t<1.5**（ブートストラップ t も併記）。
  R4 頑健・順位: winsor 5%／10% の β、Theil-Sen 中央値傾き、Spearman ρ(LAST, NEXT)、符号一致検定
     （sign(LAST)==sign(NEXT) の比率 vs 0.5・二項 p）。**BREAK-C = Spearman p>0.10 かつ 符号一致 二項 p>0.10**
     （＝平均二乗ベースの β/S だけが立っていて順位では無い）。
  R5 曜日一般性: 同じ窓形（D 15:30→16:00 → 次営業日 10:00）を月〜金の 5 曜日全部で走らせる。
     **BREAK-D = 金曜以外に t≥2 の曜日が 2 つ以上**（＝金曜固有でなく c40 の「XAU は終値→翌寄り継続」の一般効果の再発見。
     c40 は既に XAU LAST~ON β 外 +0.026 t 3.95・符号戦略 +1.07 bp/日 t 3.22 を前向き登録済み＝新セルなら二重計上）。
     併記: 金曜ダミーとの交互作用 t（金曜固有分）。
  R6 プラセボ・校正: (a) sign(LAST) ラベル無作為化 2000 回 → S_cont の片側 p と帰無 sd。
     (b) **週ずらしプラセボ**: 前週金曜の LAST で今週末の NEXT を説明（β_shift）。(c) 年クラスタ wild bootstrap（Rademacher・2000）
     で β_ctrl の t。**BREAK-E = 年クラスタ wild bootstrap p>0.10**（㊹ の型: HC1 t は裾で過大）。
  R7 多重検定: c43 が XAU 側で印字したセルの族を数える（C1: 3 事象集合 × 3 窓 × 3 era = 27／C2: δ・β_E・β_ctrl・S_E・S_ctrl
     × 3 事象集合 × 3 era = 45／合計 72）。β_ctrl/S_ctrl は**仮説でなく対照アーム（nuisance）**として印字された数字である。
     **BREAK-F = BH(0.05) で族内 72 を通らない**（Bonferroni も併記）。
  R8 コスト: 往復コスト c ∈ {1.0, 2.0, 4.0} bp（c43 の金 0.4〜0.9 bp の 1〜4 倍）＋ 週末 swap s ∈ {0, 2, 5} bp/本（3 日分・値は未取得）。
     net = S_cont − c − s。**BREAK-G = 2× コスト（c=2.0, s=2）で net の t<1.5**。実行時刻 16:00 ET 金曜は週末前の
     スプレッド拡大時刻＝c の見積は楽観（XAU の M5 spread npz は無い＝needs data）。
  R9 在外分割の再定義: 境界を 2019／2022／2023 に動かす・奇数年/偶数年・3 ブロック・LOYO。
     **BREAK-H = 境界を動かすと「在 null / 外 正」の構造が保たれない**（＝2021 境界固有＝分割の後出し）。
  R10 格子ずらし: 入口 15:55／16:05、出口 09:55／10:05 の 4 通り。**BREAK-I = 1 本（5 分）ずらすと t<1.5 になる組が過半**。
  R11 共有端点の除去: LAST と NEXT は p1600 を共有＝測定誤差は**負**のバイアス（継続に不利）なので、素の共有は標的を助ける。
     そこで非共有版 LAST' = 15:30→15:55（NEXT は 16:00 起点のまま）で β'・S'_cont を出す。
     **BREAK-J = 非共有版が null（t<1.5）**＝共有端点に依存した見かけの継続。
  R12 レジーム部分集合: 金の 60 営業日トレンド符号・|LAST| 三分位・NFP 金曜（第 1 金曜）除去・月末金曜除去・
     休日明け火曜 NEXT（88h）除去。記述（BREAK 判定には使わない）。
survived の条件（全部満たす）: R1 再現 ∧ BREAK-A〜J どれも当たらない ∧ R8 の 2× コストで net t≥1.5。
生き残っても「前向きセルとして登録可」までで、**昇格ではない**（9 条・会長の二重ロック）。
決着可能性（事前）: 外 n_ctrl 208・NEXT sd ≈ 100 bp → S の se ≈ 7 bp ⇒ +20.8 は t 3 で確かに外では有意。
  上位 3 日除去で n 205・S が +10 bp に落ちれば t ≈ 1.4 ＝ BREAK-A は「上位 3 日が S の半分を作っていれば」当たる設計。
事前の最重大反証（自分の攻撃への）: (i) 上位 3 日除去は**どんな fat-tail 戦略でも殺せる**（D 項: 優位は少数の大当たりに宿る）
  ＝BREAK-A が当たっても「構造が無い」とは言えず「n 208 では分布の裾と区別できない」が正しい読み。両方書く。
  (ii) 金曜以外で立つこと（BREAK-D）は「金曜固有でない」の証拠であって「継続が無い」の証拠ではない（c40 の既存セルに吸収される、が結論）。
  (iii) 在 null は 2012-20 の金のレジーム（横ばい・2013-15 下落）由来かもしれず、D2 により「在 null だから外も偽」とは言えない。
  (iv) bid・1 社・CFD・16:00 ET の金は現物ロコ london fix でない。
"""
import os, sys, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c43_goldfri.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED); NPERM = 2000
def say(s=""):
    print(s, flush=True); L.append(s)

say(f"# [REFUTE c43] 金の金曜引け→月曜寄り「継続」（外 t 3.15）を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c43_goldfri.py)")
say("")

WD = ['月', '火', '水', '木', '金', '土', '日']

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz"))
    ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC・格子の穴 {(np.diff(ts)!=300).sum()}")
    return ts, cl

def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan)
    return out

def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31; da = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, mo, da)

def third_friday(y, m):
    d = dt.date(y, m, 1); off = (4 - d.weekday()) % 7
    return d + dt.timedelta(days=off + 14)

OPEX = set()
for y in range(2010, 2027):
    gf = easter(y) - dt.timedelta(days=2)
    for m in range(1, 13):
        f3 = third_friday(y, m)
        if f3 == gf: continue
        OPEX.add(f3)

dates = pd.date_range("2010-01-01", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); lg = np.log
dser = dates.date; yr = dates.year.to_numpy(); wd = dates.weekday.to_numpy()
dom = dates.day.to_numpy()
E_OPEX = np.array([d in OPEX for d in dser])
# 第 1 金曜（NFP）・月末金曜
kth = (dom - 1) // 7 + 1
is_last_fri = np.array([(d + dt.timedelta(days=7)).month != d.month for d in dser])

ts, cl = load("XAU")

def build(h1=15, m1=30, h2=16, m2=0, h3=10, m3=0):
    """LAST = (h1:m1 -> h2:m2) 同日, NEXT = (h2:m2 -> 次営業日 h3:m3)"""
    P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
    p0930 = P(9, 30); p1530 = P(15, 30)
    pa, pb = P(h1, m1), P(h2, m2)
    LAST = (lg(pb) - lg(pa)) * 1e4
    CASH = (lg(p1530) - lg(p0930)) * 1e4
    nx = np.full(N, np.nan); nx0930 = np.full(N, np.nan); nxoff = np.full(N, np.nan)
    for off in range(1, 6):
        a, b = P(9, 30, off), P(h3, m3, off)
        ok = np.isnan(nx) & np.isfinite(a) & np.isfinite(b) & (a != b)
        nx[ok] = b[ok]; nx0930[ok] = a[ok]; nxoff[ok] = off
    NEXT = (lg(nx) - lg(pb)) * 1e4
    return dict(LAST=LAST, NEXT=NEXT, CASH=CASH, NXOFF=nxoff)

W = build()
valid = np.isfinite(W["LAST"]) & np.isfinite(W["NEXT"]) & np.isfinite(W["CASH"]) & (W["LAST"] != 0) & (W["CASH"] != 0)
say(f"- 有効日（全曜日・2010-2026H1）{valid.sum()}・うち金曜 {int((valid & (wd==4)).sum())}（c43 の金 716 と比較）")

ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def hc1(y, X):
    n, k = X.shape; XtX_i = np.linalg.inv(X.T @ X); b = XtX_i @ X.T @ y; e = y - X @ b
    V = XtX_i @ (X.T * (e ** 2)) @ X @ XtX_i * n / (n - k)
    return b, np.sqrt(np.diag(V)), e

def pooled_beta_ctrl(x, y, E):
    """c43 と同形: NEXT = a + b*LAST + d*(LAST*E) + g*E -> b = beta_ctrl"""
    X = np.column_stack([np.ones(len(x)), x, x * E.astype(float), E.astype(float)])
    b, se, e = hc1(y, X)
    return b[1], se[1], b[2], se[2], b, e, X

def tstat_mean(v):
    v = np.asarray(v, float); n = len(v)
    if n < 3: return np.nan, np.nan, n
    return v.mean(), v.mean() / (v.std(ddof=1) / math.sqrt(n)), n

def spearman(a, b):
    ra = pd.Series(a).rank().to_numpy(); rb = pd.Series(b).rank().to_numpy()
    r = np.corrcoef(ra, rb)[0, 1]; n = len(a)
    t = r * math.sqrt((n - 2) / max(1e-12, 1 - r * r))
    return r, t

def binom_p_two(k, n, p=0.5):
    from math import comb
    # 両側: 2 * min(P(X<=k), P(X>=k))
    lo = sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))
    hi = sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))
    return min(1.0, 2 * min(lo, hi))

# =====================================================================
say("")
say("## R1 複製（c43 の XAU・対照金曜アーム）")
say("")
FRI = valid & (wd == 4)
REP = {}
for nm, y0, y1 in ERAS:
    m = FRI & (yr >= y0) & (yr <= y1)
    x, y, E = W["LAST"][m], W["NEXT"][m], E_OPEX[m]
    bc, sec, dd, sed, bb, ee, XX = pooled_beta_ctrl(x, y, E)
    c = ~E
    s = np.sign(x[c]); Sc = s * y[c]
    mS, tS, nS = tstat_mean(Sc)
    REP[nm] = dict(m=m, x=x, y=y, E=E, bc=bc, sec=sec, S=mS, tS=tS, n=nS)
    say(f"- {nm}: n_ctrl {nS}・n_E {int(E.sum())}・**β_ctrl {bc:+.3f} (HC1 t {bc/sec:+.2f})**・"
        f"**S_cont {mS:+.1f} bp/日 (t {tS:+.2f})**・δ {dd:+.3f} (t {dd/sed:+.2f})")
say("- c43 の値: 在 β −0.328 (t −0.71)／S_cont −3.6 (t −0.87)；外 β +1.843 (t +2.70)／S_cont +20.8 (t +3.15)；"
    "近年 β +2.175 (t +2.68)／S_cont +37.2 (t +3.05)")

OUT_ERA = "外 2021-26H1"; REC_ERA = "近年 2024-26H1"
d_out = REP[OUT_ERA]
mo = d_out["m"]; ctrl_o = mo & ~E_OPEX
xo, yo = W["LAST"][ctrl_o], W["NEXT"][ctrl_o]
yro = yr[ctrl_o]; dso = np.array(dser)[ctrl_o]
so = np.sign(xo); So = so * yo
say(f"- 対照金曜（外）n {len(xo)}・LAST sd {xo.std(ddof=1):.1f} bp・NEXT sd {yo.std(ddof=1):.1f} bp・"
    f"mean NEXT {yo.mean():+.1f}・mean sign(LAST) {so.mean():+.3f}・R²(単回帰) "
    f"{np.corrcoef(xo, yo)[0,1]**2*100:.1f}%")

# =====================================================================
say("")
say("## R2 影響点（BREAK-A: 上位 3 日除去で t<1.5）")
say("")
def beta_simple(x, y):
    X = np.column_stack([np.ones(len(x)), x]); b, se, _ = hc1(y, X); return b[1], se[1]

b0, s0 = beta_simple(xo, yo)
say(f"- 外 対照金曜 単回帰 β {b0:+.3f} (t {b0/s0:+.2f})（プール版 {d_out['bc']:+.3f} と比較）")
ordL = np.argsort(-np.abs(xo))
for k in (1, 2, 3, 5, 10):
    keep = np.ones(len(xo), bool); keep[ordL[:k]] = False
    bk, sk = beta_simple(xo[keep], yo[keep])
    say(f"  - |LAST| 上位 {k} 日除去 (n {keep.sum()}): β {bk:+.3f} (t {bk/sk:+.2f})")
ordS = np.argsort(-So)
say(f"- S_cont の寄与: 上位 1 日 {So[ordS[0]]/So.sum()*100:.0f}%・上位 3 日 {So[ordS[:3]].sum()/So.sum()*100:.0f}%・"
    f"上位 5 日 {So[ordS[:5]].sum()/So.sum()*100:.0f}%（合計 {So.sum():.0f} bp）")
for k in (1, 2, 3, 5, 10):
    keep = np.ones(len(So), bool); keep[ordS[:k]] = False
    mk, tk, nk = tstat_mean(So[keep])
    say(f"  - 寄与上位 {k} 日除去 (n {nk}): S_cont {mk:+.1f} (t {tk:+.2f})")
# 両端 winsor ではなく |寄与| 上位除去（正負両方）
ordA = np.argsort(-np.abs(So))
for k in (3, 5):
    keep = np.ones(len(So), bool); keep[ordA[:k]] = False
    mk, tk, nk = tstat_mean(So[keep])
    say(f"  - |寄与| 上位 {k} 日除去（正負両方・n {nk}）: S_cont {mk:+.1f} (t {tk:+.2f})")
say("- 寄与上位 5 日: " + "；".join(
    f"{dso[i]} LAST {xo[i]:+.0f} NEXT {yo[i]:+.0f} → s·NEXT {So[i]:+.0f}" for i in ordS[:5]))
# LOYO
loyo = []
for y in range(2021, 2027):
    keep = yro != y
    if keep.sum() < 30: continue
    mk, tk, nk = tstat_mean(So[keep]); bk, sk = beta_simple(xo[keep], yo[keep])
    loyo.append((y, mk, tk, bk, bk / sk, nk))
say("- LOYO（年 1 つ抜き・外）: " + "；".join(f"−{y}: S {m:+.1f} (t {t:+.2f})・β {b:+.2f} (t {tb:+.2f})" for y, m, t, b, tb, n in loyo))
say(f"  → LOYO 最小 |t| : S {min(abs(t) for _,_,t,_,_,_ in loyo):.2f}・β {min(abs(tb) for _,_,_,_,tb,_ in loyo):.2f}")
# 年別
say("- 年別（外・対照金曜）: " + "；".join(
    f"{y}: n {int((yro==y).sum())} S {So[yro==y].mean():+.1f} (t {tstat_mean(So[yro==y])[1]:+.2f})"
    for y in range(2021, 2027) if (yro == y).sum() >= 10))

# =====================================================================
say("")
say("## R3 ドリフト分解（BREAK-B: demean 後 t<1.5）")
say("")
for nm in (OUT_ERA, REC_ERA):
    mm = REP[nm]["m"] & ~E_OPEX
    x, y = W["LAST"][mm], W["NEXT"][mm]; s = np.sign(x); S = s * y
    mu = y.mean(); pbar = s.mean()
    drift = mu * pbar
    z = s * (y - mu)
    mz, tz, nz = tstat_mean(z)
    bs = np.array([np.mean(zz) for zz in (z[rng.integers(0, nz, (NPERM, nz))],)][0], float) if False else None
    boot = z[rng.integers(0, nz, (NPERM, nz))].mean(axis=1)
    say(f"- {nm}: S_cont {S.mean():+.1f} = ドリフト項 μ_NEXT({mu:+.1f})·mean(s)({pbar:+.3f}) = {drift:+.1f} "
        f"＋ demean 項 {mz:+.1f} (t {tz:+.2f}・boot sd {boot.std():.1f}・boot t {mz/boot.std():+.2f})")
    say(f"    ドリフト項の寄与率 {drift/S.mean()*100:.0f}%・mean(NEXT) の t {tstat_mean(y)[1]:+.2f}・"
        f"符号不均衡 二項 p {binom_p_two(int((s>0).sum()), len(s)):.3f}（LAST>0 {int((s>0).sum())}/{len(s)}）")

# =====================================================================
say("")
say("## R4 頑健・順位（BREAK-C: Spearman p>0.10 ∧ 符号一致 二項 p>0.10）")
say("")
from scipy import stats as st
for nm in (OUT_ERA, REC_ERA):
    mm = REP[nm]["m"] & ~E_OPEX
    x, y = W["LAST"][mm], W["NEXT"][mm]
    r, tr = spearman(x, y); pr = 2 * (1 - st.t.cdf(abs(tr), len(x) - 2))
    agree = int((np.sign(x) == np.sign(y)).sum()); n = len(x)
    pb = binom_p_two(agree, n)
    for w in (0.05, 0.10):
        lo, hi = np.quantile(y, [w, 1 - w]); yw = np.clip(y, lo, hi)
        lox, hix = np.quantile(x, [w, 1 - w]); xw = np.clip(x, lox, hix)
        bw, sw = beta_simple(xw, yw)
        say(f"- {nm} winsor {int(w*100)}%: β {bw:+.3f} (t {bw/sw:+.2f})")
    # Theil-Sen
    ssub = rng.choice(n, size=min(n, 220), replace=False)
    sl = []
    for i in range(len(ssub)):
        for j in range(i + 1, len(ssub)):
            a, b = ssub[i], ssub[j]
            if x[a] != x[b]: sl.append((y[a] - y[b]) / (x[a] - x[b]))
    ts_slope = float(np.median(sl))
    med_S = float(np.median(np.sign(x) * y))
    w_st, w_p = st.wilcoxon(np.sign(x) * y)
    say(f"  Spearman ρ {r:+.3f} (t {tr:+.2f}・p {pr:.3f})・符号一致 {agree}/{n} = {agree/n*100:.1f}% (二項 p {pb:.3f})・"
        f"Theil-Sen 傾き {ts_slope:+.3f}・median(s·NEXT) {med_S:+.1f}・Wilcoxon p {w_p:.3f}")

# =====================================================================
say("")
say("## R5 曜日一般性（BREAK-D: 金曜以外に t≥2 が 2 つ以上）")
say("")
for nm, y0, y1 in ERAS:
    row = []
    for d in range(5):
        mm = valid & (wd == d) & (yr >= y0) & (yr <= y1) & ~E_OPEX
        x, y = W["LAST"][mm], W["NEXT"][mm]
        if len(x) < 30: row.append(f"{WD[d]} n{len(x)} —"); continue
        S = np.sign(x) * y; mS, tS, nS = tstat_mean(S)
        b, se = beta_simple(x, y)
        row.append(f"{WD[d]} n{nS} S {mS:+.1f}(t {tS:+.2f}) β {b:+.2f}(t {b/se:+.2f})")
    say(f"- {nm}: " + "／".join(row))
# 金曜交互作用（外）
mm = valid & (yr >= 2021) & (yr <= 2026) & ~E_OPEX
x, y, f = W["LAST"][mm], W["NEXT"][mm], (wd[mm] == 4).astype(float)
X = np.column_stack([np.ones(len(x)), x, x * f, f]); b, se, _ = hc1(y, X)
say(f"- 外・全曜日プール: β_他 {b[1]:+.3f} (t {b[1]/se[1]:+.2f})・**金曜交互作用 {b[2]:+.3f} (t {b[2]/se[2]:+.2f})**・n {len(x)}")
S = np.sign(x) * y
m1, t1, n1 = tstat_mean(S[f == 1]); m0, t0, n0 = tstat_mean(S[f == 0])
sed = math.sqrt(S[f == 1].var(ddof=1) / n1 + S[f == 0].var(ddof=1) / n0)
say(f"- 外・S_cont 金曜 {m1:+.1f} (n {n1}) vs 他曜日 {m0:+.1f} (n {n0})・差 {m1-m0:+.1f} (Welch t {(m1-m0)/sed:+.2f})")
say("- 参考（c40 既存前向きセル）: XAU LAST(15:30-16:00)~ON(16:00-09:30) β 外 +0.026 (t 3.95)・符号戦略 +1.07 bp/日 (t 3.22)")

# =====================================================================
say("")
say("## R6 プラセボ・校正（BREAK-E: 年クラスタ wild bootstrap p>0.10）")
say("")
# (a) 符号ラベル無作為化
sgn = rng.choice([-1.0, 1.0], size=(NPERM, len(yo)))
Sperm = (sgn * yo).mean(axis=1)
p_a = (Sperm >= So.mean()).mean()
say(f"- (a) sign 無作為化（2000）: S* 帰無 sd {Sperm.std():.1f}・片側 p {p_a:.4f}・観測 {So.mean():+.1f}（naive t {d_out['tS']:+.2f}）")
# (b) 週ずらしプラセボ: 前週金曜 LAST -> 今週末 NEXT
for lag in (1, 2):
    xl = np.r_[np.full(lag, np.nan), xo[:-lag]]
    ok = np.isfinite(xl)
    bl, sl_ = beta_simple(xl[ok], yo[ok]); Sl = np.sign(xl[ok]) * yo[ok]
    ml, tl, nl = tstat_mean(Sl)
    say(f"- (b) {lag} 週前の LAST → 今週末 NEXT（プラセボ・n {nl}）: β {bl:+.3f} (t {bl/sl_:+.2f})・S {ml:+.1f} (t {tl:+.2f})")
# 日付シフト・プラセボ（LAST を木曜の同窓に差し替え）
Wth = W  # 同じ窓関数・木曜の LAST を金曜の NEXT にぶつける
idx_fri = np.where(ctrl_o)[0]
xth = np.full(len(idx_fri), np.nan)
for i, ii in enumerate(idx_fri):
    if ii - 1 >= 0 and wd[ii - 1] == 3 and np.isfinite(W["LAST"][ii - 1]):
        xth[i] = W["LAST"][ii - 1]
ok = np.isfinite(xth)
bt, st_ = beta_simple(xth[ok], yo[ok]); Sth = np.sign(xth[ok]) * yo[ok]
mt, tt, nt = tstat_mean(Sth)
say(f"- (b2) 木曜 15:30→16:00 の LAST → 金曜発の NEXT（プラセボ・n {nt}）: β {bt:+.3f} (t {bt/st_:+.2f})・S {mt:+.1f} (t {tt:+.2f})")
# (c) 年クラスタ wild bootstrap（Rademacher・帰無 β=0 を課す）
Xo = np.column_stack([np.ones(len(xo)), xo])
b_hat, se_hat, _ = hc1(yo, Xo)
Xr = np.column_stack([np.ones(len(xo))])
br, ser, er = hc1(yo, Xr)   # 制約下（β=0）の残差
clusters = np.unique(yro)
tb = np.zeros(NPERM)
for r_ in range(NPERM):
    wgt = rng.choice([-1.0, 1.0], size=len(clusters))
    ww = np.array([wgt[np.where(clusters == c)[0][0]] for c in yro])
    ystar = Xr @ br + er * ww
    bs, ses, _ = hc1(ystar, Xo)
    tb[r_] = bs[1] / ses[1]
t_obs = b_hat[1] / se_hat[1]
p_c = (np.abs(tb) >= abs(t_obs)).mean()
say(f"- (c) 年クラスタ wild bootstrap（Rademacher・{len(clusters)} クラスタ・2000）: 観測 t {t_obs:+.2f}・"
    f"帰無 t sd {tb.std():.2f}・**両側 p {p_c:.4f}**")
# S_cont の年クラスタ bootstrap
tS_b = np.zeros(NPERM)
for r_ in range(NPERM):
    pick = rng.choice(clusters, size=len(clusters), replace=True)
    v = np.concatenate([So[yro == c] for c in pick])
    tS_b[r_] = v.mean()
say(f"- (c2) S_cont の年ブロック bootstrap: 平均 {tS_b.mean():+.1f}・sd {tS_b.std():.1f}・"
    f"P(S*≤0) {(tS_b<=0).mean():.4f}・2.5/97.5% [{np.quantile(tS_b,0.025):+.1f}, {np.quantile(tS_b,0.975):+.1f}]")

# =====================================================================
say("")
say("## R7 多重検定（BREAK-F: 族 72 の BH(0.05) を通らない）")
say("")
pS = 2 * (1 - st.norm.cdf(abs(d_out["tS"])))
pB = 2 * (1 - st.norm.cdf(abs(d_out["bc"] / d_out["sec"])))
for M in (45, 72):
    say(f"- 族 {M}: S_cont p {pS:.5f} → Bonferroni {min(1,pS*M):.4f}・BH 閾値（最良 1 位なら）{0.05/M:.5f} → "
        f"{'通過' if pS < 0.05/M else '不通過'}／β_ctrl p {pB:.5f} → Bonferroni {min(1,pB*M):.4f} → "
        f"{'通過' if pB < 0.05/M else '不通過'}")
say("- 注: β_ctrl・S_ctrl は c43 の**仮説セルではなく対照アーム**（nuisance）として印字された数字＝"
    "族は c43 の XAU 側 72 セルより広い（研究レーンが 43 サイクルで印字した全対照アーム）。")

# =====================================================================
say("")
say("## R8 コスト（BREAK-G: c=2.0・swap=2 で net t<1.5）")
say("")
for c_ in (0.0, 1.0, 2.0, 4.0):
    for sw in (0, 2, 5):
        v = So - c_ - sw
        mv, tv, nv = tstat_mean(v)
        tag = " ←BREAK-G 判定セル" if (c_ == 2.0 and sw == 2) else ""
        say(f"- 往復 {c_:.1f} bp ＋ swap {sw} bp: net {mv:+.1f} bp/日 (t {tv:+.2f}){tag}")
be = So.mean() - 1.645 * So.std(ddof=1) / math.sqrt(len(So))
say(f"- 片側 95% で net>0 を保てる総コスト上限 {be:.1f} bp（＝これより高いコストで優位は消える）")
say("- XAU の M5 スプレッド npz は無い（US100 のみ）＝16:00 ET 金曜（週末前）の実スプレッドは未測定・needs data（優先度 中）。")

# =====================================================================
say("")
say("## R9 在外分割の再定義（BREAK-H: 境界を動かすと構造が保たれない）")
say("")
ALLF = valid & (wd == 4) & ~E_OPEX & (yr >= 2012)
xa, ya, yra = W["LAST"][ALLF], W["NEXT"][ALLF], yr[ALLF]
Sa = np.sign(xa) * ya
for bnd in (2019, 2021, 2022, 2023):
    i1 = yra < bnd; i2 = yra >= bnd
    m1, t1, n1 = tstat_mean(Sa[i1]); m2, t2, n2 = tstat_mean(Sa[i2])
    b1, s1 = beta_simple(xa[i1], ya[i1]); b2, s2 = beta_simple(xa[i2], ya[i2])
    say(f"- 境界 {bnd}: 在 n {n1} S {m1:+.1f} (t {t1:+.2f}) β {b1:+.2f} (t {b1/s1:+.2f})｜"
        f"外 n {n2} S {m2:+.1f} (t {t2:+.2f}) β {b2:+.2f} (t {b2/s2:+.2f})")
odd = (yra % 2 == 1);
m1, t1, n1 = tstat_mean(Sa[odd]); m2, t2, n2 = tstat_mean(Sa[~odd])
say(f"- 奇数年 n {n1} S {m1:+.1f} (t {t1:+.2f})｜偶数年 n {n2} S {m2:+.1f} (t {t2:+.2f})")
blocks = [(2012, 2016), (2017, 2021), (2022, 2026)]
say("- 3 ブロック: " + "／".join(
    f"{a}-{b} n {int(((yra>=a)&(yra<=b)).sum())} S {Sa[(yra>=a)&(yra<=b)].mean():+.1f} "
    f"(t {tstat_mean(Sa[(yra>=a)&(yra<=b)])[1]:+.2f})" for a, b in blocks))

# =====================================================================
say("")
say("## R10 格子ずらし（BREAK-I: 5 分ずらすと t<1.5 が過半）")
say("")
grids = [(15, 30, 16, 0, 10, 0, "基準 15:30→16:00 / 10:00"),
         (15, 25, 16, 0, 10, 0, "入口 15:25"),
         (15, 35, 16, 0, 10, 0, "入口 15:35"),
         (15, 30, 15, 55, 10, 0, "出口(LAST) 15:55"),
         (15, 30, 16, 5, 10, 0, "出口(LAST) 16:05"),
         (15, 30, 16, 0, 9, 55, "月 09:55"),
         (15, 30, 16, 0, 10, 5, "月 10:05")]
nbreak = 0; ngrid = 0
for h1, m1, h2, m2, h3, m3, lab in grids:
    Wg = build(h1, m1, h2, m2, h3, m3)
    v = (np.isfinite(Wg["LAST"]) & np.isfinite(Wg["NEXT"]) & np.isfinite(Wg["CASH"])
         & (Wg["LAST"] != 0) & (Wg["CASH"] != 0) & (wd == 4) & ~E_OPEX & (yr >= 2021) & (yr <= 2026))
    x, y = Wg["LAST"][v], Wg["NEXT"][v]; S = np.sign(x) * y
    mS, tS, nS = tstat_mean(S); b, se = beta_simple(x, y)
    if lab != grids[0][6]:
        ngrid += 1
        if abs(tS) < 1.5: nbreak += 1
    say(f"- {lab}: n {nS}・S_cont {mS:+.1f} (t {tS:+.2f})・β {b:+.3f} (t {b/se:+.2f})")
say(f"→ ずらし {ngrid} 通りのうち t<1.5 は {nbreak}（過半 = {nbreak > ngrid/2}）")

# =====================================================================
say("")
say("## R11 共有端点の除去（BREAK-J: 非共有版が null）")
say("")
Wd_ = build(15, 30, 15, 55, 10, 0)   # LAST' = 15:30->15:55、NEXT は 15:55 起点になるので作り直す
# NEXT は 16:00 起点のままにしたいので手組み
P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
p1530, p1555, p1600 = P(15, 30), P(15, 55), P(16, 0)
LASTd = (lg(p1555) - lg(p1530)) * 1e4
v = (np.isfinite(LASTd) & (LASTd != 0) & np.isfinite(W["NEXT"]) & np.isfinite(W["CASH"]) & (W["CASH"] != 0)
     & (wd == 4) & ~E_OPEX & (yr >= 2021) & (yr <= 2026))
x, y = LASTd[v], W["NEXT"][v]; S = np.sign(x) * y
mS, tS, nS = tstat_mean(S); b, se = beta_simple(x, y)
say(f"- 非共有 LAST'(15:30→15:55) → NEXT(16:00→月 10:00)・n {nS}: S_cont {mS:+.1f} (t {tS:+.2f})・β {b:+.3f} (t {b/se:+.2f})")
# 最後 5 分だけ（15:55->16:00）
LAST5 = (lg(p1600) - lg(p1555)) * 1e4
v5 = (np.isfinite(LAST5) & (LAST5 != 0) & np.isfinite(W["NEXT"]) & (wd == 4) & ~E_OPEX & (yr >= 2021) & (yr <= 2026))
x5, y5 = LAST5[v5], W["NEXT"][v5]; S5 = np.sign(x5) * y5
m5_, t5_, n5_ = tstat_mean(S5); b5, se5 = beta_simple(x5, y5)
say(f"- 共有端点を含む最後 5 分 LAST5(15:55→16:00) → NEXT・n {n5_}: S_cont {m5_:+.1f} (t {t5_:+.2f})・β {b5:+.3f} (t {b5/se5:+.2f})")
say("  （LAST5 は p1600 を共有＝測定誤差バイアスは負。LAST' は非共有。両方を並べて共有端点の寄与を見る）")

# =====================================================================
say("")
say("## R12 レジーム部分集合（記述・BREAK 判定外）")
say("")
# 60 営業日トレンド（金曜 16:00 close の 60 日前比）
pxF = p1600.copy()
trend = np.full(N, np.nan)
fin = np.where(np.isfinite(pxF))[0]
for k, i in enumerate(fin):
    if k >= 60: trend[i] = math.log(pxF[i] / pxF[fin[k - 60]]) * 1e4
mm = ctrl_o & np.isfinite(trend)
xt, yt, tr = W["LAST"][mm], W["NEXT"][mm], trend[mm]
St = np.sign(xt) * yt
for lab, sel in (("上昇トレンド", tr > 0), ("下降トレンド", tr <= 0)):
    m_, t_, n_ = tstat_mean(St[sel]); say(f"- 外・{lab}（n {n_}）: S_cont {m_:+.1f} (t {t_:+.2f})・mean NEXT {yt[sel].mean():+.1f}")
q = np.quantile(np.abs(xo), [1/3, 2/3])
for lab, sel in (("|LAST| 下位 1/3", np.abs(xo) <= q[0]), ("中位", (np.abs(xo) > q[0]) & (np.abs(xo) <= q[1])), ("上位 1/3", np.abs(xo) > q[1])):
    m_, t_, n_ = tstat_mean(So[sel]); say(f"- 外・{lab}（n {n_}）: S_cont {m_:+.1f} (t {t_:+.2f})")
nfp = (kth == 1)[ctrl_o]; lastf = is_last_fri[ctrl_o]; nxo = W["NXOFF"][ctrl_o]
for lab, sel in (("第 1 金曜(NFP) 除去", ~nfp), ("月末金曜 除去", ~lastf), ("NEXT が火曜(88h) の本 除去", nxo == 3)):
    m_, t_, n_ = tstat_mean(So[sel]); say(f"- 外・{lab}（n {n_}）: S_cont {m_:+.1f} (t {t_:+.2f})")
say(f"- 外・NEXT の暦日差分布: " + " ".join(f"{int(o)}日:{int((nxo==o).sum())}" for o in np.unique(nxo[np.isfinite(nxo)])))

say("")
say(f"- 実行 {time.time()-T0:.1f} s・seed {SEED}・NPERM {NPERM}・XAU bid M5 npz のみ・scan 無し・MT5 無し・外部通信無し")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
