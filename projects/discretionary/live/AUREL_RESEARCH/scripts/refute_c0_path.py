# -*- coding: utf-8 -*-
"""
AUREL 反証レーン — cycle0「建玉中の path(MFE/MAE) に勝ち負けの情報がある」を壊す。
読取りのみ・発注なし・書き込みは AUREL_RESEARCH/data 配下のみ。

cycle0 の主張（findings/2026-11-04.md cycle0）:
  C1 +0.5R 見えた本 → 最終勝ち 67% 平均+0.725R
  C2 +0.5R 見えなかった本 → 最終勝ち 18% 平均−0.776R
  C3 負け(SL)の 41% は途中 +0.5R を見せて負けた
  C4 勝ち(TP)の 50% は途中 −0.5R まで沈んだ
  C5 MAE≥1.0R の勝ちは 0 本
  C6 勝ちの平均MAE −0.50R / 負けの平均MFE +0.59R

反証の設計:
  (a) 幾何の帳消し: SL=−1R / TP=+b_i R(本ごとに異なる・中央値1.5R) の吸収壁つきランダムウォークなら、
      同じ条件付き統計がどうなるか（連続ブラウン運動の到達確率・閉形式）。ドリフト0 と、全体勝率に合わせたドリフト θ の2本。
  (b) 離散版 Monte Carlo: 足の高値/安値・FEED_TOL・同足SL優先・MAX_HOLD=288 を本番 _simulate と同じ規則で再現。σ は保有本数の中央値で校正（1自由度）。
  (c) 実データ・プラセボ: 金M5 2025-07..2026-07 の実足に、同じ時刻帯(JST時)・同じ側・同じ R 幾何(ATRで尺度合わせ)で**ランダム建玉**。入口シグナル無しの path 統計。
  (d) 別分割(台帳前半/後半)・部分集合(壁種/時間帯)・ブートストラップCI・Bonferroni(6主張)。
"""
import os, sys, json, math, time, collections
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE); LIVE = os.path.dirname(RES)
W2W = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
sys.path.insert(0, W2W)
from m5_loader import load_m5

OUT = os.path.join(RES, "data", "refute_c0_path_result.md")
FEED_TOL = 0.1; MAX_HOLD = 288
rng = np.random.default_rng(20261104)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


# ─────────────────────────── 1. 台帳 ───────────────────────────
def load_ledger():
    recs = [json.loads(l) for l in open(os.path.join(LIVE, "setup_ledger.jsonl"), encoding="utf-8") if l.strip()]
    base = {r["id"]: r for r in recs if r.get("kind") != "update" and r.get("id")}
    final = {}
    for r in recs:
        ra = r.get("reaccel")
        if isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None:
            t = r["target"] if r.get("kind") == "update" else r.get("id"); final[t] = ra
    rows = []
    for t, ra in final.items():
        b0 = base.get(t, {})
        risk = abs(ra["entry"] - ra["sl"])
        rows.append({"id": t, "side": b0.get("side", "BUY"), "wall_kind": b0.get("wall_kind", "?"), "jh": int(ra["entry_jst"][11:13]),
                     "entry_time": int(ra["entry_time"]), "risk": risk, "b": abs(ra["tp"] - ra["entry"]) / risk,
                     "R": float(ra["R"]), "mfe": float(ra["mfe_R"]), "mae": float(ra["mae_R"]), "hold": int(ra["hold_bars"]),
                     "exit": ra["exit_reason"], "atr": float((b0.get("features") or {}).get("atr14", np.nan))})
    df = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)
    df["ft"] = FEED_TOL / df["risk"]            # FEED_TOL を R 単位に
    return df


def cond_stats(R, mfe, mae, b):
    """cycle0 の6主張を同じコードで計算（観測・シミュレーション共通）。"""
    w = R > 0; reached = mfe >= 0.5
    out = collections.OrderedDict()
    out["n"] = len(R); out["win"] = w.mean(); out["meanR"] = R.mean()
    out["C1_win|reached"] = w[reached].mean() if reached.any() else np.nan
    out["C1_R|reached"] = R[reached].mean() if reached.any() else np.nan
    out["C2_win|notreached"] = w[~reached].mean() if (~reached).any() else np.nan
    out["C2_R|notreached"] = R[~reached].mean() if (~reached).any() else np.nan
    out["C3_reached|loss"] = reached[~w].mean() if (~w).any() else np.nan
    out["C4_dip0.5|win"] = (mae[w] >= 0.5).mean() if w.any() else np.nan
    out["C5_wins_mae>=1"] = int((w & (mae >= 1.0)).sum())
    out["C6_mae|win"] = mae[w].mean() if w.any() else np.nan
    out["C6_mfe|loss"] = mfe[~w].mean() if (~w).any() else np.nan
    out["reached_share"] = reached.mean()
    return out


# ─────────────────────────── 2. 閉形式ランダムウォーク ───────────────────────────
def p_hit(x, a, u, th):
    """ドリフト θ=2μ/σ² のBMが x から出発し、−a より先に +u に当たる確率。θ=0 は (x+a)/(a+u)。"""
    if abs(th) < 1e-9:
        return (x + a) / (a + u)
    s = lambda y: math.exp(-th * y)
    return (s(x) - s(-a)) / (s(u) - s(-a))


def analytic(df, th):
    """本ごとの到達確率から、cycle0 の各統計の期待値を合成。+0.5R 到達の議論は u>0.5 の本のみ意味を持つ(u≤0.5は到達⇔TP)。"""
    E = collections.defaultdict(float)
    for _, t in df.iterrows():
        a = 1.0 - t.ft; u = t.b + t.ft                      # 実効壁: SLは手前 FEED_TOL で発動・TPは FEED_TOL 先
        pT = p_hit(0.0, a, u, th)                           # P(TP)
        E["n"] += 1; E["win"] += pT; E["meanR"] += pT * t.b - (1 - pT) * 1.0
        if u > 0.5:
            pr = p_hit(0.0, a, 0.5, th)                     # P(+0.5R 到達)
            pT_r = p_hit(0.5, a, u, th)                     # P(TP | 到達)
            E["reached"] += pr; E["reached&win"] += pr * pT_r; E["reached_R"] += pr * (pT_r * t.b - (1 - pT_r))
            E["notreached"] += 1 - pr; E["notreached&win"] += 0.0; E["notreached_R"] += -(1 - pr) * 1.0
            E["loss"] += 1 - pT; E["loss&reached"] += pr * (1 - pT_r)
        else:                                               # TP ≤ 0.5R: 到達 ⇔ TP（連続モデル）
            E["reached"] += pT; E["reached&win"] += pT; E["reached_R"] += pT * t.b
            E["notreached"] += 1 - pT; E["notreached_R"] += -(1 - pT)
            E["loss"] += 1 - pT
        # 勝ちのうち −0.5R まで沈んだ: 0→−0.5 に先着 → −0.5 から TP
        if a > 0.5:
            p_dip = 1.0 - p_hit(0.0, 0.5, u, th)            # −0.5 に u より先に到達
            pT_from_dip = p_hit(-0.5, a, u, th)
            E["win_cnt"] += pT; E["win&dip"] += p_dip * pT_from_dip
    r = collections.OrderedDict()
    r["n"] = int(E["n"]); r["win"] = E["win"] / E["n"]; r["meanR"] = E["meanR"] / E["n"]
    r["C1_win|reached"] = E["reached&win"] / E["reached"]; r["C1_R|reached"] = E["reached_R"] / E["reached"]
    r["C2_win|notreached"] = E["notreached&win"] / E["notreached"]; r["C2_R|notreached"] = E["notreached_R"] / E["notreached"]
    r["C3_reached|loss"] = E["loss&reached"] / E["loss"]; r["C4_dip0.5|win"] = E["win&dip"] / E["win_cnt"]
    r["C5_wins_mae>=1"] = 0; r["C6_mae|win"] = np.nan; r["C6_mfe|loss"] = np.nan; r["reached_share"] = E["reached"] / E["n"]
    r["_E_reached"] = E["reached"]; r["_E_reached&win"] = E["reached&win"]
    return r


def fit_theta(df, target_wins):
    lo, hi = -5.0, 5.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = sum(p_hit(0.0, 1.0 - t.ft, t.b + t.ft, mid) for _, t in df.iterrows())
        lo, hi = (mid, hi) if s < target_wins else (lo, mid)
    return 0.5 * (lo + hi)


# ─────────────────────────── 3. 離散 Monte Carlo（_simulate と同じ決着規則） ───────────────────────────
def simulate_bars(H, Lo, C, b, ft, side_sign=1.0):
    """H/Lo/C: (nsim, nbars) の R 単位 path（建玉=0・有利方向が正）。本番 _simulate と同じ: SL手前ft・TP先ft・同足SL優先・時間切れは終値。"""
    nsim, nb = H.shape
    sl_hit = Lo <= -(1.0 - ft); tp_hit = H >= (b + ft)
    any_hit = sl_hit | tp_hit
    first = np.where(any_hit.any(1), any_hit.argmax(1), nb - 1)
    rows = np.arange(nsim)
    is_sl = sl_hit[rows, first]; is_tp = tp_hit[rows, first] & ~is_sl
    R = np.where(is_sl, -1.0, np.where(is_tp, b, C[rows, first]))
    mask = np.arange(nb)[None, :] <= first[:, None]
    mfe = np.where(mask, H, -np.inf).max(1); mae = -np.where(mask, Lo, np.inf).min(1)
    mfe = np.maximum(mfe, 0.0); mae = np.maximum(mae, 0.0)
    return R, mfe, mae, first + 0, is_sl, is_tp


def mc_rw(df, kappa, th, nsim=1000, m=6):
    allR, allM, allA, allH = [], [], [], []
    for _, t in df.iterrows():
        sig = kappa * t.atr / t.risk                       # 1足の σ (R単位) = κ × ATR/risk
        ss = sig / math.sqrt(m); mu = th * ss * ss / 2.0
        inc = rng.normal(mu, ss, size=(nsim, MAX_HOLD + 1, m))
        path = np.cumsum(inc.reshape(nsim, -1), axis=1).reshape(nsim, MAX_HOLD + 1, m)
        H = path.max(2); Lo = path.min(2); C = path[:, :, -1]
        H = np.maximum(H, 0.0 * H); Lo = np.minimum(Lo, 0.0 * Lo)    # 建玉足は 0 を含む
        R, mfe, mae, hold, _, _ = simulate_bars(H, Lo, C, t.b, t.ft)
        allR.append(R); allM.append(mfe); allA.append(mae); allH.append(hold)
    R = np.concatenate(allR); mfe = np.concatenate(allM); mae = np.concatenate(allA); hold = np.concatenate(allH)
    s = cond_stats(R, mfe, mae, None); s["hold_med"] = float(np.median(hold)); return s


# ─────────────────────────── 4. 実データ・プラセボ（ランダム建玉） ───────────────────────────
def placebo_real(df, m5, nper=100, hour_match=True):
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    n = len(o); tr = h - l
    atr = pd.Series(tr).rolling(14).mean().shift(1).to_numpy()        # 直前14本の平均レンジ（_features と同じ定義の近似）
    hours_utc = m5.index.hour.to_numpy()
    valid = np.arange(14, n - MAX_HOLD - 2)
    allR, allM, allA, allH = [], [], [], []
    for _, t in df.iterrows():
        cand = valid
        if hour_match:
            hu = (t.jh - 9) % 24; cand = valid[hours_utc[valid] == hu]
        j = rng.choice(cand, size=nper, replace=True)
        scale = atr[j] / t.atr                                        # 当時のATR比で尺度合わせ
        risk_s = t.risk * scale; entry = o[j]
        idx = j[:, None] + np.arange(MAX_HOLD + 1)[None, :]
        sgn = 1.0 if t.side == "BUY" else -1.0
        A = sgn * (h[idx] - entry[:, None]) / risk_s[:, None]; B = sgn * (l[idx] - entry[:, None]) / risk_s[:, None]
        H = np.maximum(A, B); Lo = np.minimum(A, B)                   # 有利方向を正に揃える（SELL は high/low が入れ替わる）
        C = sgn * (c[idx] - entry[:, None]) / risk_s[:, None]
        R, mfe, mae, hold, _, _ = simulate_bars(H, Lo, C, t.b, t.ft)
        allR.append(R); allM.append(mfe); allA.append(mae); allH.append(hold)
    R = np.concatenate(allR); mfe = np.concatenate(allM); mae = np.concatenate(allA); hold = np.concatenate(allH)
    s = cond_stats(R, mfe, mae, None); s["hold_med"] = float(np.median(hold)); return s


# ─────────────────────────── 5. 検定・整形 ───────────────────────────
def binom_z(k, n, p):
    if n == 0 or p <= 0 or p >= 1: return float("nan"), float("nan")
    z = (k - n * p) / math.sqrt(n * p * (1 - p))
    from math import erf
    pv = 2 * (1 - 0.5 * (1 + erf(abs(z) / math.sqrt(2))))
    return z, pv


def boot_ci(x, f, B=4000):
    x = np.asarray(x); vals = [f(x[rng.integers(0, len(x), len(x))]) for _ in range(B)]
    return np.nanpercentile(vals, [2.5, 97.5])


KEYS = ["n", "win", "meanR", "C1_win|reached", "C1_R|reached", "C2_win|notreached", "C2_R|notreached",
        "C3_reached|loss", "C4_dip0.5|win", "C5_wins_mae>=1", "C6_mae|win", "C6_mfe|loss", "reached_share"]


def row(lab, s):
    v = []
    for k in KEYS:
        x = s.get(k, np.nan)
        v.append(("%d" % x) if k in ("n", "C5_wins_mae>=1") else ("%+.3f" % x if isinstance(x, float) and not np.isnan(x) else "—"))
    return "| %-26s | " % lab + " | ".join(v) + " |"


def main():
    t0 = time.time()
    df = load_ledger()
    say("# AUREL [REFUTE] cycle0 path情報  %s" % time.strftime("%Y-%m-%d %H:%M"))
    say("台帳 再加速 closed n=%d  期間 %s..%s  exit: %s" % (len(df), pd.Timestamp(df.entry_time.min(), unit="s", tz="Asia/Tokyo").strftime("%m-%d"),
        pd.Timestamp(df.entry_time.max(), unit="s", tz="Asia/Tokyo").strftime("%m-%d"), dict(collections.Counter(df.exit))))
    say("TP_R(b) 分位 10/25/50/75/90 = %s  b≤0.5 の本 %d (%.0f%%)  risk中央値 %.2f  ATR14中央値 %.2f  保有中央値 %d" % (
        np.percentile(df.b, [10, 25, 50, 75, 90]).round(2).tolist(), (df.b <= 0.5).sum(), 100 * (df.b <= 0.5).mean(), df.risk.median(), df.atr.median(), df.hold.median()))
    say()
    obs = cond_stats(df.R.to_numpy(), df.mfe.to_numpy(), df.mae.to_numpy(), df.b.to_numpy())

    # ── 恒真チェック
    say("## 0. 恒真(定義から出る)チェック")
    w = df.R > 0
    say("- C5: MAE≥1.0R は定義上 SL 発動(SL=−1R・手前FEED_TOL)。MAE≥1.0 の本 %d / うち exit=SL %d / 勝ち %d → 恒真。" % ((df.mae >= 1).sum(), ((df.mae >= 1) & (df.exit == "SL")).sum(), (w & (df.mae >= 1)).sum()))
    nr_w = w & (df.mfe < 0.5)
    say("- C2 の『見えなかったのに勝った 18%%』= %d 本。その全てが TP_R<0.5 の本か: %d/%d。→ TP が 0.5R 手前にある本は +0.5R を見ずに勝つのが当然＝幾何。" % (nr_w.sum(), (nr_w & (df.b < 0.5)).sum(), nr_w.sum()))
    say("- 勝ち本の MAE 分布: MAE∈[0.9,1.0) の勝ち %d / MAE≥0.8 の勝ち %d（SL直前まで沈んで勝った本は存在）。" % ((w & (df.mae >= 0.9) & (df.mae < 1.0)).sum(), (w & (df.mae >= 0.8)).sum()))
    say()

    # ── 閉形式
    say("## 1. 閉形式ランダムウォーク基準（本ごとの SL=−1R / TP=+b_i R、FEED_TOL 込み）")
    th = fit_theta(df, w.sum())
    a0 = analytic(df, 0.0); a1 = analytic(df, th)
    say("ドリフト θ を全体勝率(%d/%d)に合わせて推定: θ=%.3f（θ=0 が無情報・正なら入口に優位）" % (w.sum(), len(df), th))
    say(); say("| 系列 | " + " | ".join(KEYS) + " |"); say("|" + "---|" * (len(KEYS) + 1))
    say(row("観測(台帳)", obs)); say(row("RW θ=0", a0)); say(row("RW θ=%.2f(勝率一致)" % th, a1))
    say()
    # 到達→勝ち の検定（u>0.5 の本のみ・到達本の中で）
    sub = df[(df.b + df.ft) > 0.5]
    reached = sub.mfe >= 0.5; k = int(((sub.R > 0) & reached).sum()); n = int(reached.sum())
    pexp = analytic(sub, th)["C1_win|reached"]; z, pv = binom_z(k, n, pexp)
    say("C1 検定（TP>0.5R の本 n=%d のうち +0.5R 到達 %d 本）: 観測 勝ち %d (%.1f%%) vs RW(θ一致) 期待 %.1f%%  z=%+.2f p=%.3f" % (len(sub), n, k, 100 * k / n, 100 * pexp, z, pv))
    pexp0 = analytic(sub, 0.0)["C1_win|reached"]; z0, pv0 = binom_z(k, n, pexp0)
    say("   同・θ=0 基準: 期待 %.1f%%  z=%+.2f p=%.3f" % (100 * pexp0, z0, pv0))
    lo, hi = boot_ci(((sub.R > 0) & reached)[reached].to_numpy().astype(float), np.mean)
    say("   観測 C1 の bootstrap 95%%CI = [%.1f%%, %.1f%%]" % (100 * lo, 100 * hi))
    # C3, C4 の検定
    loss = sub.R <= 0; k3 = int((reached & loss).sum()); n3 = int(loss.sum()); p3 = analytic(sub, th)["C3_reached|loss"]; z3, pv3 = binom_z(k3, n3, p3)
    say("C3 検定: 負け %d 本のうち +0.5R 到達 %d (%.1f%%) vs RW(θ一致) %.1f%%  z=%+.2f p=%.3f" % (n3, k3, 100 * k3 / n3, 100 * p3, z3, pv3))
    sub4 = df[(1 - df.ft) > 0.5]; win4 = sub4.R > 0; k4 = int((win4 & (sub4.mae >= 0.5)).sum()); n4 = int(win4.sum()); p4 = analytic(sub4, th)["C4_dip0.5|win"]; z4, pv4 = binom_z(k4, n4, p4)
    say("C4 検定: 勝ち %d 本のうち −0.5R まで沈んだ %d (%.1f%%) vs RW(θ一致) %.1f%%  z=%+.2f p=%.3f" % (n4, k4, 100 * k4 / n4, 100 * p4, z4, pv4))
    pvals = {"C1": pv, "C3": pv3, "C4": pv4}
    say()

    # ── 離散 MC
    say("## 2. 離散 Monte Carlo（足の高値安値・FEED_TOL・同足SL優先・時間切れ288本を本番規則で再現、1000本/取引）")
    say("σ(1足,R単位)=κ×ATR14/risk。κ は保有本数の中央値(観測 %d 本)に合わせて校正。" % df.hold.median())
    best = None
    for kappa in (0.6, 0.8, 1.0, 1.2, 1.5, 2.0):
        s = mc_rw(df, kappa, th, nsim=300)
        say("  κ=%.1f → 保有中央値 %.0f  勝率 %.3f" % (kappa, s["hold_med"], s["win"]))
        if best is None or abs(s["hold_med"] - df.hold.median()) < abs(best[1] - df.hold.median()):
            best = (kappa, s["hold_med"])
    kap = best[0]
    say("採用 κ=%.1f" % kap); say()
    say("| 系列 | " + " | ".join(KEYS) + " |"); say("|" + "---|" * (len(KEYS) + 1))
    say(row("観測(台帳)", obs))
    for kk, lab in ((kap, "MC κ=%.1f θ一致" % kap), (kap * 0.7, "MC κ×0.7"), (kap * 1.4, "MC κ×1.4")):
        say(row(lab, mc_rw(df, kk, th, nsim=1000)))
    say(row("MC κ=%.1f θ=0" % kap, mc_rw(df, kap, 0.0, nsim=1000)))
    say()

    # ── 実データ・プラセボ
    say("## 3. 実データ・プラセボ: 金M5 2025-07-01..2026-07-01 にランダム建玉（同JST時・同側・同R幾何・ATR尺度合わせ、100本/取引）")
    m5 = load_m5("2025-07-01", "2026-07-01")
    say("  M5 %d 本 %s..%s" % (len(m5), m5.index[0].strftime("%Y-%m-%d"), m5.index[-1].strftime("%Y-%m-%d")))
    say("| 系列 | " + " | ".join(KEYS) + " |"); say("|" + "---|" * (len(KEYS) + 1))
    say(row("観測(台帳)", obs))
    pl_h = placebo_real(df, m5, nper=100, hour_match=True); say(row("プラセボ 時刻一致", pl_h))
    pl_a = placebo_real(df, m5, nper=100, hour_match=False); say(row("プラセボ 時刻無視", pl_a))
    say("  プラセボ保有中央値: 時刻一致 %.0f / 時刻無視 %.0f（観測 %d）" % (pl_h["hold_med"], pl_a["hold_med"], df.hold.median()))
    say()

    # ── 別分割・部分集合: 観測の C1 − RW(θ一致)期待 の超過
    say("## 4. 別分割・部分集合（C1 の超過 = 観測の到達後勝率 − RW(θは全体で固定)期待、TP>0.5R の本のみ）")
    say("| 部分集合 | n | 到達n | 観測 勝率|到達 | RW期待 | 超過 | z | 全体勝率 |"); say("|---|---|---|---|---|---|---|---|")
    half = len(df) // 2
    subsets = [("台帳前半(9/15-)", df.iloc[:half]), ("台帳後半(-11/3)", df.iloc[half:])]
    for wk, g in df.groupby("wall_kind"): subsets.append(("壁種 %s" % wk, g))
    def zone(j): return "本物帯7-12" if 7 <= j < 12 else ("ダマシ巣0-5" if j < 5 else "中立")
    for zn, g in df.groupby(df.jh.map(zone)): subsets.append(("時間帯 %s" % zn, g))
    for sd, g in df.groupby("side"): subsets.append(("側 %s" % sd, g))
    for lab, g in subsets:
        g = g[(g.b + g.ft) > 0.5]
        if len(g) < 10: continue
        rr = g.mfe >= 0.5; kk = int(((g.R > 0) & rr).sum()); nn = int(rr.sum())
        if nn == 0: continue
        pe = analytic(g, th)["C1_win|reached"]; zz, _ = binom_z(kk, nn, pe)
        say("| %-18s | %3d | %3d | %.1f%% | %.1f%% | %+.1fpt | %+.2f | %.1f%% |" % (lab, len(g), nn, 100 * kk / nn, 100 * pe, 100 * (kk / nn - pe), zz, 100 * (g.R > 0).mean()))
    say()

    # ── 多重検定
    say("## 5. 多重検定補正（cycle0 は6主張。Bonferroni α=0.05/6=0.0083）")
    for k_, v_ in pvals.items():
        say("  %s: p=%.3f → %s" % (k_, v_, "有意" if v_ < 0.05 / 6 else "有意でない"))
    say("  C2/C5 は恒真(検定不要)。C6 は C1/C3/C4 の言い換え。")
    say()
    say("(elapsed %.0fs)" % (time.time() - t0))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
