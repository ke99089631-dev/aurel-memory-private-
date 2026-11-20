# -*- coding: utf-8 -*-
"""
[REFUTE 反証レーン] 2026-11-20 — 対象: cycle57 (12:55) の **事後の弱シグナル**
「δ=0.10R に帯を広げると真の前セッション極値だけ p_cross が +5〜13 pp 高い
（在 D_H +0.066 z +2.95／D_L +0.079 z +3.75・外 D_H +0.094 z +3.33／D_L +0.051 z +1.70・
近年 D_H +0.132 z +3.44・6 セル中 5 セル正）＝磁石方向」。
c57 の主判定（δ=0.05R の H_BARRIER）は null なので壊す余地は無い。攻撃対象は
**次サイクルで前向き 1 セルに送られようとしている事後の正** のみ。

c57 自身が最重大反証 (ii) で「帯入り深さの機械項と未分離」と書き、復活条件として
「深さ四分位内で D>0 が残る（在 z≥2.5・外 同符号 z≥1.5）」を事前に置いた。
本レーンはその条件を実装し、さらに c57 の自己批判に無い 4 本（打ち切り選択・
近傍水準プラセボ・δ 格子の単調性・時間圧縮）を足して壊しに行く。

------------------------------------------------------------------------------
事前固定（走る前に書く・結果を見てから変えない・seed 20261121）
------------------------------------------------------------------------------
データ・事象定義は c57 と**完全に同一**（data/macro/XAU_m5_ohlc.npz・bid・flat 除外・
セッション日 =(ET+6h) 暦日・有効 = 月〜金 ∧ 非 flat ≥100・水準 = 直前有効セッションの H/L・
R = H−L・接近 = 帯 [X−δ, X) に下から入る最初の 1 回・K=24 本先着・
CROSS = y ≥ Y+δ／RETREAT = y ≤ Y−3δ、y = dir*close, Y = dir*X）。
c57 の数字を自前実装で再現できることを先に印字する（再現ゲート: δ=0.10R の在 D_H/D_L が
c57 の +0.066/+0.079 と ±0.010 以内・事象数が ±3% 以内。外れたら以降の判定は inconclusive）。

幾何（c57 が自分で開示した誤り＝RW 基準は 0.5 でない）を定量化する:
  帯入り深さ u = (Y − y_t)/δ ∈ (0, 1]（u 小 = X に近い所で帯に入った = CROSS が近い）
  CROSS までの距離 = (1+u)δ・RETREAT までの距離 = (3−u)δ
  無ドリフト BM の先着確率 p_RW(u) = (3−u)/4   [u=0.5 で 0.625・u→0 で 0.75・u→1 で 0.50]

攻撃（A1 が主・A2〜A6 は支え。どれも c57 と同じ npz・同じ格子・同じ事象機械を使う）:
  A1 深さ（機械項）分解 = c57 の復活条件そのもの
     (a) Δu = mean(u|真) − mean(u|擬似) を印字（負なら真は深く入る＝機械的に CROSS 有利）
     (b) 深さ層別 D: u の四分位（窓×向きごとに真+擬似プールで切る）内で D を出し、
         真の u 分布で重みづけた **深さ整合 D_strat** と日ブロック bootstrap se
     (c) RW 調整超過 excess = cross − p_RW(u)（事象ごと）の差 **D_adj**（方法論候補 90）
  A2 近傍水準プラセボ（特異性）: N0.90 = L+0.90R（= H−0.10R）・N0.95・
     B1.05 = L+1.05R・B1.10（極値の直外）・下側対称。
     真の極値の D が「レンジ上端近傍であること」でなく「まさにその極値であること」に
     由来するなら、近傍水準の D は真の半分未満であるべき。
  A3 古い極値プラセボ: S5 = 5 セッション前の有効セッションの H/L（本物の極値だが陳腐）。
  A4 連続ランダム水準プラセボ: Q = L + m·R, m ~ U(0.05, 0.95)（セッションごと 5 本・seed 固定）
     ＝ c57 の 5 点固定 m の退化を外す。
  A5 コスト倍（スプレッド）: CROSS/RETREAT を両方 +s ずらす（買い側に不利）。s = 0.20 USD（実測域）
     と s = 0.40 USD（倍）。δ 中央値 0.10R は在 1.6／外 2.9 USD なので s は 7〜25% の重み。
  A6 打ち切り選択: p_cross は決着本の条件つき比（δ=0.10R の censor は 55.6%）。
     真/擬似の censor 率差を印字し、**非条件（競合リスク）版** CI_cross = CROSS/n_all の差
     D_uncond を出す。条件つきで出て非条件で消えるなら「決着しやすさの選択」。
  A7 δ 格子の形: δ ∈ {0.03, 0.05, 0.075, 0.10, 0.15, 0.20}R で D と Δu を印字。
     機械項仮説 (b) は D が δ とともに単調増（Δu も）と予測。
     Osler 型の「直外 0.05〜0.10R に逆指値集積」仮説 (a) は D が 0.10R 付近で山・0.20R で減衰と予測。
  A8 別の在外分割（c57 の 2010-20／2021-26H1 以外）: 偶奇セッション交互分割・
     4 期ブロック（2010-14／2015-18／2019-22／2023-26H1）。実在なら多数のブロックに出る。
  A9 時間圧縮（look-ahead 隣接・c57 の自己批判に無い）: flat 足を落とした圧縮系列で
     「K=24 本 = 2 時間」を仮定している。事象足から決着足までの実経過時間が
     2.5 時間（= 24 本 ×5 分 ×1.25）を超える事象の比率を真/擬似で印字し、
     実時間が連続な事象だけに絞った D を出す。
  A10 モメンタム整合: 接近直前 1h リターン（接近向き・bp）の十分位で擬似を真に再重みづけした D。
  A11 多重検定: 本レーンの判定セルは A1(b)(c) の 在/外 × H/L = 8 セル（Holm）。
     さらに c57 の記述約 40 セル全体に Bonferroni を当てた必要 |z|（α=0.05 両側 → 3.23）を併記。

判定規則（事前・この順に評価）:
  BROKEN   = 以下のいずれか: (1) 深さ整合 D_strat（δ=0.10R・在）が |z_boot| < 2.5 または符号反転
             (2) D_adj（RW 調整）が 在 |z_boot| < 2.5
             (3) 近傍水準プラセボ（N0.90 または B1.05）の D が真と同符号で |D| ≥ 0.5·|D_真|
  SURVIVED = D_strat ≥ +0.03 ∧ 在 z_boot ≥ 2.5 ∧ 外 同符号 z ≥ 1.5 ∧ D_adj も同様 ∧
             近傍プラセボ < 半分 ∧ Bonferroni 3.23 を在で越える ∧ 4 期ブロックの 3 つ以上で正
  INCONCLUSIVE = 上のどちらにも入らない（層別で MDE が広がり検出力を失った場合を含む・MDE を印字）

書込は AUREL_RESEARCH/ 配下のみ（data/refute_c57_banddepth_result.md・同 .log）。
発注・デモ発注なし・本番ファイル編集なし・プロセス/執行機/ライブサーバ/schtask 接触なし・
MT5 接続なし・プロップ参照なし・秘密の読取出力なし・外部通信なし・多年 scan なし。
"""
import os, sys, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c57_banddepth_result.md")
rng = np.random.default_rng(20261121); T0 = time.time(); LOG = []
def say(s=""):
    print(s, flush=True); LOG.append(s)
def utc(x): return dt.datetime.fromtimestamp(int(x), dt.timezone.utc)

say(f"# [REFUTE] c57 δ=0.10R の事後の正を壊す — 帯入り深さ・打ち切り・近傍プラセボ "
    f"({time.strftime('%Y-%m-%d %H:%M')}・scripts/refute_c57_banddepth.py・seed 20261121)")

K_MAIN = 24
DELTA_FLOOR = 0.30
DGRID = [0.03, 0.05, 0.075, 0.10, 0.15, 0.20]
M_INT = [0.2, 0.35, 0.5, 0.65, 0.8]          # c57 と同一の擬似プール
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
BLOCKS = {"B1 2010-14": (2010, 2014), "B2 2015-18": (2015, 2018), "B3 2019-22": (2019, 2022), "B4 2023-26H1": (2023, 2026)}

# ----------------------------------------------------------------------------- データ（c57 と同一手順）
z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); Hi = z["high"].astype(float); Lo = z["low"].astype(float); C = z["close"].astype(float)
say(f"- npz {len(TS)} 本 {utc(TS[0])} 〜 {utc(TS[-1])} UTC")
flat = np.r_[True, (C[1:] == C[:-1]) & (Hi[1:] == Lo[1:])]
et = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
sess = (et + pd.Timedelta(hours=6)).normalize().values.astype("datetime64[D]")
et_hour = et.hour.values; year = et.year.values
idx = np.flatnonzero(~flat)
sess_k = sess[idx]; C_k = C[idx]; H_k = Hi[idx]; L_k = Lo[idx]; hr_k = et_hour[idx]; ts_k = TS[idx]

us, inv = np.unique(sess_k, return_inverse=True); ns = len(us)
cnt = np.bincount(inv, minlength=ns)
hi_s = np.full(ns, -np.inf); np.maximum.at(hi_s, inv, H_k)
lo_s = np.full(ns, np.inf);  np.minimum.at(lo_s, inv, L_k)
wd_s = pd.DatetimeIndex(us).weekday.values
yr_s = pd.DatetimeIndex(us).year.values
valid = (cnt >= 100) & (wd_s <= 4)
prev_idx = np.full(ns, -1); last = -1
for i in range(ns):
    prev_idx[i] = last
    if valid[i]: last = i
# 5 セッション前の有効セッション（A3 の古い極値）
vlist = np.flatnonzero(valid); rank = np.full(ns, -1); rank[vlist] = np.arange(len(vlist))
prev5 = np.full(ns, -1)
for i in vlist:
    r = rank[i]
    if r >= 5: prev5[i] = vlist[r - 5]
use_s = valid & (prev_idx >= 0)
starts = np.r_[0, np.flatnonzero(np.diff(inv)) + 1]; ends = np.r_[starts[1:], len(inv)]
say(f"- セッション {ns}・有効 {int(valid.sum())}・判定に使う {int(use_s.sum())}（c57 は 4590/—/4242）")

# ----------------------------------------------------------------------------- 事象収集（ベクトル化）
# 1 セッション内で全水準・全δを同時に処理する。c57 の per-session×per-level ループ(150s)の置換。
S_USE = np.flatnonzero(use_s)

def build_levels(s_i):
    """(label, X, dir) のリスト。c57 の H/L/I* をそのまま含み、反証用の水準を足す。"""
    p = prev_idx[s_i]; Hp, Lp = hi_s[p], lo_s[p]; R = Hp - Lp
    out = [("H", Hp, +1), ("L", Lp, -1)]
    for m in M_INT:
        out += [(f"I{m}", Lp + m * R, +1), (f"I{m}", Lp + m * R, -1)]
    # A2 近傍水準（特異性）: 極値の直内 / 直外
    out += [("N0.90", Lp + 0.90 * R, +1), ("N0.95", Lp + 0.95 * R, +1),
            ("B1.05", Lp + 1.05 * R, +1), ("B1.10", Lp + 1.10 * R, +1)]
    out += [("N0.90", Lp + 0.10 * R, -1), ("N0.95", Lp + 0.05 * R, -1),
            ("B1.05", Lp - 0.05 * R, -1), ("B1.10", Lp - 0.10 * R, -1)]
    # A3 古い極値
    p5 = prev5[s_i]
    if p5 >= 0:
        out += [("S5", hi_s[p5], +1), ("S5", lo_s[p5], -1)]
    # A4 連続ランダム水準
    for m in rng.uniform(0.05, 0.95, 5):
        out += [("Q", Lp + m * R, +1), ("Q", Lp + m * R, -1)]
    return out, R

COSTS = [0.0, 0.20, 0.40]   # A5

rows = []
for s_i in S_USE:
    a, b = starts[s_i], ends[s_i]
    c = C_k[a:b]; n = len(c)
    if n < 3: continue
    lv, R = build_levels(s_i)
    labs = [x[0] for x in lv]
    X = np.array([x[1] for x in lv]); D = np.array([x[2] for x in lv], float)
    y = c[None, :] * D[:, None]                  # (J, n)
    Y = X * D                                    # (J,)
    pre_r = np.empty(n)
    k12 = np.maximum(np.arange(n) - 12, 0)
    pre_r = (c / c[k12] - 1.0) * 1e4             # bp（向き未適用）
    for dfrac in DGRID:
        delta = max(dfrac * R, DELTA_FLOOR)
        inband = (y >= Y[:, None] - delta) & (y < Y[:, None])
        prevout = np.zeros_like(inband)
        prevout[:, 1:] = y[:, :-1] < (Y[:, None] - delta)
        ev = inband & prevout
        ev[:, 0] = False                         # 直前足が同セッション内に要る（c57 と同じ）
        has = ev.any(1)
        if not has.any(): continue
        t0 = ev.argmax(1)
        jj = np.flatnonzero(has)
        tt = t0[jj][:, None] + 1 + np.arange(K_MAIN)[None, :]
        ok = tt < n
        ttc = np.clip(tt, 0, n - 1)
        yseg = np.take_along_axis(y[jj], ttc, axis=1)
        Yj = Y[jj][:, None]
        u = (Y[jj] - y[jj, t0[jj]]) / delta      # 帯入り深さ ∈ (0,1]
        pre = pre_r[t0[jj]] * D[jj]              # 接近向きの直前 1h リターン
        for s in COSTS:
            hc = (yseg >= Yj + delta + s) & ok
            hr = (yseg <= Yj - 3 * delta + s) & ok
            anyc = hc.any(1); anyr = hr.any(1)
            kc = np.where(anyc, hc.argmax(1), 10 ** 6)
            kr = np.where(anyr, hr.argmax(1), 10 ** 6)
            res = np.where(~anyc & ~anyr, -1, (kc < kr).astype(int))   # -1 = censor
            kres = np.minimum(kc, kr)
            # 決着足の実経過秒（A9 時間圧縮）
            tres = np.clip(t0[jj] + 1 + np.minimum(kres, K_MAIN - 1), 0, n - 1)
            dsec = ts_k[a + tres] - ts_k[a + t0[jj]]
            for q, j in enumerate(jj):
                rows.append((s_i, yr_s[s_i], labs[j], int(D[j]), dfrac, s,
                             int(res[q]), float(u[q]), float(pre[q]), int(dsec[q]), float(delta)))
    if len(rows) > 12_000_000: break

df = pd.DataFrame(rows, columns=["s", "year", "lab", "dir", "dfrac", "cost",
                                 "res", "u", "pre", "dsec", "delta"])
say(f"- 事象総数 {len(df)}（水準 {df['lab'].nunique()} 種 × δ {len(DGRID)} × コスト {len(COSTS)}）・{time.time()-T0:.1f}s")

# ----------------------------------------------------------------------------- 統計ユーティリティ
def p_rw_(u): return (3.0 - u) / 4.0

def boot_se(t, p, kind, e=None, B=1500, CH=200):
    """セッション日ブロック bootstrap（ベクトル化）。kind: D / adj / uncond / strat。
    strat は u 四分位 4 層・重みは各 draw の真の層別 n（深さ整合 D と同じ推定量）。"""
    sd = np.unique(np.r_[t["s"].values, p["s"].values]); nd = len(sd)
    pos = pd.Series(np.arange(nd), index=sd)
    Q = 4 if kind == "strat" else 1
    def agg(d):
        if kind == "uncond":
            dd = d; num = (dd["res"].values == 1).astype(float)
        else:
            dd = d[d["res"] >= 0]
            num = dd["res"].values.astype(float)
            if kind == "adj": num = num - p_rw_(dd["u"].values)
        b = np.digitize(dd["u"].values, e) if kind == "strat" else np.zeros(len(dd), int)
        i = pos.reindex(dd["s"].values).values.astype(int)
        A = np.zeros((nd, Q)); N = np.zeros((nd, Q))
        np.add.at(A, (i, b), num); np.add.at(N, (i, b), 1.0)
        return A, N
    At, Nt = agg(t); Ap, Np_ = agg(p)
    out = np.empty(B)
    for s0 in range(0, B, CH):
        s1 = min(s0 + CH, B)
        dr = rng.integers(0, nd, size=(s1 - s0, nd))
        atb = At[dr].sum(1); ntb = Nt[dr].sum(1); apb = Ap[dr].sum(1); npb = Np_[dr].sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            pt = atb / ntb; pp = apb / npb
        ok = (ntb > 0) & (npb > 0)
        w = np.where(ok, ntb, 0.0); dd = np.where(ok, pt - pp, 0.0)
        out[s0:s1] = (w * dd).sum(1) / np.maximum(w.sum(1), 1e-9)
    return float(np.nanstd(out, ddof=1))

def p_cross(d):
    r = d[d["res"] >= 0]["res"].values
    return r.mean() if len(r) else np.nan

def stat_D(t, p): return p_cross(t) - p_cross(p)

def p_rw(u): return (3.0 - u) / 4.0

def stat_Dadj(t, p):
    tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
    if not len(tr) or not len(pr): return np.nan
    return (tr["res"].values - p_rw(tr["u"].values)).mean() - (pr["res"].values - p_rw(pr["u"].values)).mean()

EDGES = {}
def make_strata(t, p, key):
    pool = np.r_[t["u"].values, p["u"].values]
    e = np.quantile(pool, [0.25, 0.5, 0.75])
    EDGES[key] = e
    return e

def stat_Dstrat(t, p, e):
    """真の u 分布で重みづけた深さ整合 D（4 層）。層が空なら層を落として重みを再正規化。"""
    tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
    if not len(tr) or not len(pr): return np.nan
    bt = np.digitize(tr["u"].values, e); bp = np.digitize(pr["u"].values, e)
    num = 0.0; wsum = 0.0
    for q in range(4):
        mt = bt == q; mp = bp == q
        if mt.sum() < 3 or mp.sum() < 3: continue
        w = mt.sum()
        num += w * (tr["res"].values[mt].mean() - pr["res"].values[mp].mean()); wsum += w
    return num / wsum if wsum else np.nan

def pick(d, lab, dr, win, dfrac, cost=0.0):
    lo, hi = win
    m = ((d["lab"] == lab) & (d["dir"] == dr) & (d["year"] >= lo) & (d["year"] <= hi)
         & (d["dfrac"] == dfrac) & (d["cost"] == cost))
    return d[m]

def pool_int(d, dr, win, dfrac, cost=0.0):
    lo, hi = win
    m = (d["lab"].str.startswith("I") & (d["dir"] == dr) & (d["year"] >= lo) & (d["year"] <= hi)
         & (d["dfrac"] == dfrac) & (d["cost"] == cost))
    return d[m]

SIDES = [("H↑", "H", +1), ("L↓", "L", -1)]

# ----------------------------------------------------------------------------- 再現ゲート
say("\n## 0. 再現ゲート（c57 の δ=0.10R を自前実装で再現できるか）")
repro = {}
for wn, w in [("在 2010-20", WIN["在 2010-20"]), ("外 2021-26H1", WIN["外 2021-26H1"]), ("近年 2024-26H1", WIN["近年 2024-26H1"])]:
    for sn, lab, dr in SIDES:
        t = pick(df, lab, dr, w, 0.10); p = pool_int(df, dr, w, 0.10)
        D = stat_D(t, p)
        nt = (t["res"] >= 0).sum(); npl = (p["res"] >= 0).sum()
        cens_t = (t["res"] < 0).mean() * 100; cens_p = (p["res"] < 0).mean() * 100
        repro[(wn, sn)] = D
        say(f"- {wn} {sn}: p_cross 真 {p_cross(t):.3f}（決着 n {nt}／全 {len(t)}・censor {cens_t:.1f}%） "
            f"vs 擬似 {p_cross(p):.3f}（決着 n {npl}／全 {len(p)}・censor {cens_p:.1f}%）・**D {D:+.4f}**")
C57 = {("在 2010-20", "H↑"): 0.066, ("在 2010-20", "L↓"): 0.079,
       ("外 2021-26H1", "H↑"): 0.094, ("外 2021-26H1", "L↓"): 0.051,
       ("近年 2024-26H1", "H↑"): 0.132, ("近年 2024-26H1", "L↓"): 0.023}
dev = {k: repro[k] - v for k, v in C57.items() if k in repro}
say("- c57 との差: " + "・".join(f"{k[0]} {k[1]} {v:+.4f}" for k, v in dev.items()))
GATE = all(abs(v) <= 0.010 for v in dev.values())
say(f"- **再現ゲート {'PASS' if GATE else 'FAIL'}**（全セル ±0.010 以内）"
    + ("" if GATE else " → 以降の判定は inconclusive 扱い（事象機械の不一致が先）"))

# ----------------------------------------------------------------------------- A1 深さ分解（主攻撃）
say("\n## A1 帯入り深さ u の分解（c57 の最重大反証 (ii)・復活条件そのもの）")
say("u = (X−close_t)/δ ∈ (0,1]・u 小 = 深く入った = CROSS が近い。RW 先着 p_RW(u) = (3−u)/4")
MAIN = {}
for wn, w in WIN.items():
    for sn, lab, dr in SIDES:
        t = pick(df, lab, dr, w, 0.10); p = pool_int(df, dr, w, 0.10)
        tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
        if len(tr) < 20 or len(pr) < 20:
            say(f"- {wn} {sn}: n 不足"); continue
        ut, up = tr["u"].mean(), pr["u"].mean()
        D = stat_D(t, p)
        e = make_strata(tr, pr, (wn, sn))
        Ds = stat_Dstrat(t, p, e)
        Da = stat_Dadj(t, p)
        se_D = boot_se(t, p, "D")
        se_s = boot_se(t, p, "strat", e)
        se_a = boot_se(t, p, "adj")
        MAIN[(wn, sn)] = dict(D=D, Ds=Ds, Da=Da, zD=D / se_D, zs=Ds / se_s, za=Da / se_a,
                              se_s=se_s, se_a=se_a, ut=ut, up=up, nt=len(tr), npl=len(pr))
        say(f"- {wn} {sn}: **Δu {ut-up:+.4f}**（真 {ut:.3f} vs 擬似 {up:.3f}）"
            f"・生 D {D:+.4f} (z {D/se_D:+.2f})"
            f"・**深さ整合 D_strat {Ds:+.4f}** (se {se_s:.4f}・z {Ds/se_s:+.2f}・MDE ±{2*se_s:.3f})"
            f"・**RW 調整 D_adj {Da:+.4f}** (se {se_a:.4f}・z {Da/se_a:+.2f})")
        # 層別の内訳
        bt = np.digitize(tr["u"].values, e); bp = np.digitize(pr["u"].values, e)
        parts = []
        for q in range(4):
            mt = bt == q; mp = bp == q
            if mt.sum() < 3 or mp.sum() < 3: parts.append(f"Q{q+1}:n不足"); continue
            parts.append(f"Q{q+1}(u≤{e[q] if q<3 else 1.0:.2f}) {tr['res'].values[mt].mean()-pr['res'].values[mp].mean():+.3f}"
                         f"[{mt.sum()}/{mp.sum()}]")
        say("    深さ四分位内 D: " + " ".join(parts))

# ----------------------------------------------------------------------------- A6 打ち切り選択
say("\n## A6 打ち切り選択（p_cross は決着本の条件つき比・censor 55%）")
for wn, w in WIN.items():
    for sn, lab, dr in SIDES:
        t = pick(df, lab, dr, w, 0.10); p = pool_int(df, dr, w, 0.10)
        if len(t) < 20 or len(p) < 20: continue
        ct = (t["res"] < 0).mean(); cp = (p["res"] < 0).mean()
        cit = (t["res"] == 1).mean(); cip = (p["res"] == 1).mean()
        rit = (t["res"] == 0).mean(); rip = (p["res"] == 0).mean()
        se_un = boot_se(t, p, "uncond")
        say(f"- {wn} {sn}: censor 真 {ct*100:.1f}% vs 擬似 {cp*100:.1f}%（差 {(ct-cp)*100:+.1f} pp）"
            f"・非条件 CI_cross 真 {cit:.3f} vs 擬似 {cip:.3f}・**D_uncond {cit-cip:+.4f}** "
            f"(se {se_un:.4f}・z {(cit-cip)/se_un:+.2f})・CI_retreat 真 {rit:.3f} vs 擬似 {rip:.3f}")

# ----------------------------------------------------------------------------- A2/A3/A4 プラセボ家族
say("\n## A2/A3/A4 プラセボ家族（特異性: 真の極値だけか）")
for wn, w in [("在 2010-20", WIN["在 2010-20"]), ("外 2021-26H1", WIN["外 2021-26H1"])]:
    for sn, lab, dr in SIDES:
        base = MAIN.get((wn, sn))
        if base is None: continue
        p = pool_int(df, dr, w, 0.10)
        out = []
        for pl in ["H" if dr > 0 else "L", "N0.95", "N0.90", "B1.05", "B1.10", "S5", "Q"]:
            t2 = pick(df, pl, dr, w, 0.10)
            tr2 = t2[t2["res"] >= 0]
            if len(tr2) < 20: out.append(f"{pl}:n{len(tr2)}"); continue
            D2 = stat_D(t2, p); e2 = np.quantile(np.r_[tr2["u"].values, p[p["res"]>=0]["u"].values], [.25, .5, .75])
            Ds2 = stat_Dstrat(t2, p, e2)
            out.append(f"{pl} D {D2:+.3f}/Ds {Ds2:+.3f}(n{len(tr2)})")
        say(f"- {wn} {sn}: " + " ｜ ".join(out))
say("  （Q = ランダム m の連続プラセボ・擬似プール I* に対する D なので ≈0 が健全）")

# ----------------------------------------------------------------------------- A5 コスト倍
say("\n## A5 コスト倍（CROSS/RETREAT を両方 +s・買い側に不利）")
for wn, w in WIN.items():
    for sn, lab, dr in SIDES:
        line = []
        for s in COSTS:
            t = pick(df, lab, dr, w, 0.10, s); p = pool_int(df, dr, w, 0.10, s)
            if (t["res"] >= 0).sum() < 20: line.append(f"s={s}: n不足"); continue
            e = np.quantile(np.r_[t[t["res"]>=0]["u"].values, p[p["res"]>=0]["u"].values], [.25,.5,.75])
            line.append(f"s={s:.2f}: D {stat_D(t,p):+.4f}/Ds {stat_Dstrat(t,p,e):+.4f}")
        say(f"- {wn} {sn}: " + " ｜ ".join(line))

# ----------------------------------------------------------------------------- A7 δ 格子の形
say("\n## A7 δ 格子（機械項仮説は単調増・Osler 型は 0.10R 付近で山）")
for wn, w in WIN.items():
    for sn, lab, dr in SIDES:
        line = []
        for dfrac in DGRID:
            t = pick(df, lab, dr, w, dfrac); p = pool_int(df, dr, w, dfrac)
            tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
            if len(tr) < 20: line.append(f"{dfrac}: n不足"); continue
            e = np.quantile(np.r_[tr["u"].values, pr["u"].values], [.25,.5,.75])
            line.append(f"{dfrac:.3f}: D {stat_D(t,p):+.3f} Ds {stat_Dstrat(t,p,e):+.3f} Δu {tr['u'].mean()-pr['u'].mean():+.3f} cen {(t['res']<0).mean()*100:.0f}%")
        say(f"- {wn} {sn}: " + " ｜ ".join(line))

# ----------------------------------------------------------------------------- A8 別分割
say("\n## A8 別の在外分割（c57 の 2010-20／2021-26H1 以外）")
for sn, lab, dr in SIDES:
    line = []
    for bn, w in BLOCKS.items():
        t = pick(df, lab, dr, w, 0.10); p = pool_int(df, dr, w, 0.10)
        tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
        if len(tr) < 20: line.append(f"{bn}: n不足"); continue
        e = np.quantile(np.r_[tr["u"].values, pr["u"].values], [.25,.5,.75])
        se = boot_se(t, p, "strat", e, B=800)
        Ds = stat_Dstrat(t, p, e)
        line.append(f"{bn}: D {stat_D(t,p):+.3f} Ds {Ds:+.3f} (z {Ds/se:+.2f}・n{len(tr)})")
    say(f"- {sn} 4 期ブロック: " + " ｜ ".join(line))
# 偶奇セッション
say("- 偶奇セッション交互分割（同じ地合いを両側に入れる・在外の地合い差を消す）:")
for sn, lab, dr in SIDES:
    line = []
    for par, pn in [(0, "偶"), (1, "奇")]:
        t = pick(df, lab, dr, (2010, 2026), 0.10); p = pool_int(df, dr, (2010, 2026), 0.10)
        t = t[t["s"] % 2 == par]; p = p[p["s"] % 2 == par]
        tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
        if len(tr) < 20: continue
        e = np.quantile(np.r_[tr["u"].values, pr["u"].values], [.25,.5,.75])
        se = boot_se(t, p, "strat", e, B=800)
        Ds = stat_Dstrat(t, p, e)
        line.append(f"{pn} D {stat_D(t,p):+.3f} Ds {Ds:+.3f} (z {Ds/se:+.2f}・n{len(tr)})")
    say(f"  - {sn}: " + " ｜ ".join(line) + "（D2: 16 年一括は幾何/機械項の検定にのみ使用・edge の結論には使わない）")

# ----------------------------------------------------------------------------- A9 時間圧縮
say("\n## A9 時間圧縮（flat 足を落とした圧縮系列で「24 本 = 2 時間」を仮定している）")
LIM = int(K_MAIN * 300 * 1.25)
for wn, w in WIN.items():
    for sn, lab, dr in SIDES:
        t = pick(df, lab, dr, w, 0.10); p = pool_int(df, dr, w, 0.10)
        tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
        if len(tr) < 20: continue
        ft = (tr["dsec"] > LIM).mean() * 100; fp = (pr["dsec"] > LIM).mean() * 100
        t2 = t[(t["res"] < 0) | (t["dsec"] <= LIM)]; p2 = p[(p["res"] < 0) | (p["dsec"] <= LIM)]
        tr2 = t2[t2["res"] >= 0]; pr2 = p2[p2["res"] >= 0]
        e = np.quantile(np.r_[tr2["u"].values, pr2["u"].values], [.25,.5,.75])
        say(f"- {wn} {sn}: 決着まで実時間 >2.5h 真 {ft:.1f}% vs 擬似 {fp:.1f}%"
            f"・実時間連続のみ D {stat_D(t2,p2):+.4f}/Ds {stat_Dstrat(t2,p2,e):+.4f}（n {len(tr2)}）")

# ----------------------------------------------------------------------------- A10 モメンタム整合
say("\n## A10 モメンタム整合（接近直前 1h リターン十分位で擬似を真に再重みづけ）")
for wn, w in WIN.items():
    for sn, lab, dr in SIDES:
        t = pick(df, lab, dr, w, 0.10); p = pool_int(df, dr, w, 0.10)
        tr = t[t["res"] >= 0]; pr = p[p["res"] >= 0]
        if len(tr) < 40 or len(pr) < 40: continue
        e = np.quantile(np.r_[tr["pre"].values, pr["pre"].values], np.arange(1, 10) / 10)
        bt = np.digitize(tr["pre"].values, e); bp = np.digitize(pr["pre"].values, e)
        num = 0.0; wsum = 0.0
        for q in range(10):
            mt = bt == q; mp = bp == q
            if mt.sum() < 3 or mp.sum() < 3: continue
            num += mt.sum() * (tr["res"].values[mt].mean() - pr["res"].values[mp].mean()); wsum += mt.sum()
        Dm = num / wsum if wsum else np.nan
        # 深さ＋モメンタム両方で整合（2 次元・4×4）
        eu = np.quantile(np.r_[tr["u"].values, pr["u"].values], [.25,.5,.75])
        ep = np.quantile(np.r_[tr["pre"].values, pr["pre"].values], [.25,.5,.75])
        but = np.digitize(tr["u"].values, eu) * 4 + np.digitize(tr["pre"].values, ep)
        bup = np.digitize(pr["u"].values, eu) * 4 + np.digitize(pr["pre"].values, ep)
        num2 = 0.0; w2 = 0.0
        for q in np.unique(but):
            mt = but == q; mp = bup == q
            if mt.sum() < 3 or mp.sum() < 3: continue
            num2 += mt.sum() * (tr["res"].values[mt].mean() - pr["res"].values[mp].mean()); w2 += mt.sum()
        D2 = num2 / w2 if w2 else np.nan
        say(f"- {wn} {sn}: pre 中央値 真 {np.median(tr['pre']):+.1f} bp vs 擬似 {np.median(pr['pre']):+.1f} bp"
            f"・モメンタム整合 D {Dm:+.4f}・**深さ×モメンタム整合 D {D2:+.4f}**（有効セル重み {w2:.0f}）")

# ----------------------------------------------------------------------------- A11 多重検定 + 判定
say("\n## A11 多重検定と判定")
cells = [(wn, sn) for wn in ["在 2010-20", "外 2021-26H1"] for sn in ["H↑", "L↓"]]
pv = []
for k in cells:
    m = MAIN.get(k)
    if m is None: continue
    for nm, zz in [("D_strat", m["zs"]), ("D_adj", m["za"])]:
        from math import erfc, sqrt
        p = erfc(abs(zz) / sqrt(2))
        pv.append((f"{k[0]} {k[1]} {nm}", zz, p))
pv.sort(key=lambda x: x[2])
mtot = len(pv)
say(f"- 判定セル {mtot}（Holm）: " + " ｜ ".join(f"{n} z {z:+.2f} p {p:.4f} (閾 {0.05/(mtot-i):.4f})"
                                                for i, (n, z, p) in enumerate(pv)))
say(f"- c57 の記述約 40 セル全体に Bonferroni（α=0.05 両側）→ 必要 |z| ≈ 3.23")

say("\n### 事前規則の評価")
inn = MAIN.get(("在 2010-20", "H↑")); inl = MAIN.get(("在 2010-20", "L↓"))
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG) + "\n")
say(f"\n（出力 {OUT}・総 {time.time()-T0:.1f}s）")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LOG) + "\n")
with open(os.path.join(DATA, "refute_c57_banddepth.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(LOG) + "\n")
