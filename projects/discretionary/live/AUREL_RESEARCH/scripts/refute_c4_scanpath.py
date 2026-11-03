# -*- coding: utf-8 -*-
"""
AUREL 反証レーン — 02:40 の [REFUTE] で唯一 inconclusive に残った cycle0 C4
「勝ち(TP)の本は途中 −0.5R まで沈む割合が RW より高い」を、2010-2026 の scan path（n≈数千）で壊しにいく。
読取りのみ・発注なし・書き込みは AUREL_RESEARCH/data 配下のみ。

前回の結論(台帳 n=299): 建玉足(約定前レンジ含む)を除くと C4 は 51%→41%、hold≥1 の勝ち n=74 で
  観測 47.3% vs 建玉足終値から出発する RW 期待 34.3% → z=+2.36 p=0.018（Bonferroni 0.0083 で非有意）。
覆す条件(前回明記): 2010-2026 scan path で同じ比較を n≈数千本で行い、建玉足除外版が θ 一致 RW を Bonferroni 後も上回れば C4 復活。

事前固定(ここで固定・以後動かさない):
  データ: 金M5 2010-01-01..2026-07-01、setup_engine.scan（本番値 MIN_SL_W/FEED_TOL/TRIG_SPREAD）。再加速 closed 全本・全壁種・全時間帯。
  主検定: 勝ち(exit=TP)かつ hold≥1 かつ 有効SL壁 a=1−ft>0.5 の本について、
          「建玉足を除く offset1..exit の MAE ≥ 0.5R」の割合を、
          建玉足終値 x0 から出発する吸収壁RW（SL=−a, TP=+u=b+ft, ドリフト θ）の条件付き確率 P(dip|TP, x0) の平均と比べる。
          θ は hold≥1 の本の勝率に合わせて x0 出発で 1 つ推定（＝入口に優位はあるが path は無情報、という帰無）。
  合否: 両側 z 検定。前回の多重検定枠(6主張 → α=0.0083)を踏襲。p<0.0083 なら C4 復活(=survived)、そうでなければ broken。
  追加(構造確認・採用判断には使わない): θ=0 基準／θ を x=0 全本で推定した基準／時代(2010-20, 21-23, 24-26)×壁種の部分集合（Bonferroni 6分割）／
          離散MC（建玉足終値から出発・足の高値安値・FEED_TOL・同足SL優先）／実データ・プラセボ（同JST時・同側・同幾何でランダム建玉）。
  look-ahead: scan は一方向走査（先読みなし）。path は entry 足以降のみ使用。survivorship: closed 全本（invalid/no_trigger は建玉無しなので対象外が自然）。
"""
import os, sys, json, math, time, collections
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE); LIVE = os.path.dirname(RES)
W2W = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
for p in (LIVE, W2W):
    if p not in sys.path:
        sys.path.insert(0, p)
import wallbox
import setup_engine as se
import backtest_reaccel as br
from m5_loader import load_m5

DATA = os.path.join(RES, "data"); os.makedirs(DATA, exist_ok=True)
PATHS_JSON = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(DATA, "refute_c4_scanpath_result.md")
FEED_TOL = se.FEED_TOL; MAX_HOLD = se.MAX_HOLD
ALPHA = 0.05 / 6
rng = np.random.default_rng(20261104)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


# ─────────────────────────── 1. path 構築（scan は本番コードそのまま） ───────────────────────────
def load_all(last="2026-07-01"):
    fr = []
    for y in range(2010, 2027):
        a, b = "%d-01-01" % y, "%d-01-01" % (y + 1)
        if a >= last: break
        if b > last: b = last
        try:
            fr.append(load_m5(a, b))
        except FileNotFoundError as e:
            print("skip", y, e, flush=True)
    m5 = pd.concat(fr)
    return m5[~m5.index.duplicated(keep="first")].sort_index()


def build_paths():
    say("金M5 読込...")
    m5 = load_all()
    say("  %d bars %s..%s" % (len(m5), m5.index[0], m5.index[-1]))
    fb = br.FastBox(m5); wallbox.dynamic_box = fb.box
    dm = se._load_damashi()
    t0 = time.time(); recs = se.scan(m5, dm)
    say("  scan %d setups %.0fs" % (len(recs), time.time() - t0))
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    tr_ = h - l; atr = pd.Series(tr_).rolling(14).mean().shift(1).to_numpy()
    pos = {int(pd.Timestamp(t).timestamp()): i for i, t in enumerate(m5.index)}
    trades = []
    for r in recs:
        ra = r.get("reaccel") or {}
        if ra.get("status") != "closed" or ra.get("R") is None or ra.get("sl") is None:
            continue
        ie = pos.get(int(ra["entry_time"])); ek = pos.get(int(ra["exit_time"]))
        if ie is None or ek is None:
            continue
        entry = float(ra["entry"]); sl = float(ra["sl"]); tp = float(ra["tp"]); risk = abs(entry - sl)
        if risk <= 0: continue
        sgn = 1.0 if r["side"] == "BUY" else -1.0
        fav = sgn * (h[ie:ek + 1] - entry) / risk if sgn > 0 else (entry - l[ie:ek + 1]) / risk
        adv = (entry - l[ie:ek + 1]) / risk if sgn > 0 else (h[ie:ek + 1] - entry) / risk
        mfe0 = float(max(0.0, fav.max())); mae0 = float(max(0.0, adv.max()))
        mfe1 = float(max(0.0, fav[1:].max())) if ek > ie else 0.0
        mae1 = float(max(0.0, adv[1:].max())) if ek > ie else 0.0
        trades.append({"entry_time": int(ra["entry_time"]), "year": int(pd.Timestamp(ra["entry_time"], unit="s", tz="UTC").year),
                       "jh": int(((int(ra["entry_time"]) // 3600) + 9) % 24), "wall_kind": r["wall_kind"], "side": r["side"],
                       "risk": round(risk, 4), "b": round(abs(tp - entry) / risk, 4), "R": float(ra["R"]), "exit": ra["exit_reason"],
                       "hold": int(ek - ie),
                       "x0": round(sgn * (c[ie] - entry) / risk, 4),              # 建玉足の終値（R）
                       "open_gap": round(-sgn * (o[ie] - entry) / risk, 4),      # 建玉足の始値が逆行側なら正
                       "mfe0": round(mfe0, 4), "mae0": round(mae0, 4),           # 建玉足込み
                       "mfe1": round(mfe1, 4), "mae1": round(mae1, 4),           # 建玉足除外(offset1..exit)
                       "mae_bar0": round(float(max(0.0, adv[0])), 4), "mfe_bar0": round(float(max(0.0, fav[0])), 4),
                       "atr": round(float(atr[ie]), 4) if not np.isnan(atr[ie]) else None})
    json.dump({"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "bars": int(len(m5)), "setups": len(recs),
               "frozen": {"MIN_SL_W": se.MIN_SL_W, "FEED_TOL": se.FEED_TOL, "TRIG_SPREAD": se.TRIG_SPREAD, "MAX_HOLD": se.MAX_HOLD},
               "trades": trades}, open(PATHS_JSON, "w", encoding="utf-8"))
    say("  再加速 closed %d 本 → %s" % (len(trades), PATHS_JSON))
    return trades, m5


# ─────────────────────────── 2. 閉形式 RW ───────────────────────────
def p_hit(x, a, u, th):
    """ドリフト θ の BM が x から出発し、−a より先に +u に当たる確率。"""
    if x <= -a: return 0.0
    if x >= u: return 1.0
    if abs(th) < 1e-9:
        return (x + a) / (a + u)
    s = lambda y: math.exp(-th * y)
    return (s(x) - s(-a)) / (s(u) - s(-a))


def p_dip_given_tp(x0, a, u, th, d=0.5):
    """x0 から出発して TP に至る path のうち、途中 −d まで沈む確率（a>d 前提）。"""
    pT = p_hit(x0, a, u, th)
    if pT <= 0: return float("nan"), 0.0
    if x0 <= -d: return 1.0, pT
    p_dip_first = 1.0 - p_hit(x0, d, u, th)          # −d に u より先に到達
    pT_from_dip = p_hit(-d, a, u, th)
    return p_dip_first * pT_from_dip / pT, pT


def fit_theta(df, xcol):
    target = int((df.R > 0).sum())
    lo, hi = -5.0, 5.0
    X = df[xcol].to_numpy(); A = (1.0 - df.ft).to_numpy(); U = (df.b + df.ft).to_numpy()
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = sum(p_hit(x, a, u, mid) for x, a, u in zip(X, A, U))
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return 0.5 * (lo + hi)


def binom_z(k, n, p):
    if n == 0 or p <= 0 or p >= 1: return float("nan"), float("nan")
    z = (k - n * p) / math.sqrt(n * p * (1 - p))
    pv = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return z, pv


def c4_test(g, th, lab, d=0.5, use_x0=True):
    """g: 勝ち・hold≥1・a>0.5 の本。観測 = mae1≥d の割合。期待 = 本ごとの P(dip|TP,x0) を『勝ちである』条件で平均（Poisson-binomial 近似の z）。"""
    if len(g) == 0: return None
    X = g.x0.to_numpy() if use_x0 else np.zeros(len(g)); A = (1.0 - g.ft).to_numpy(); U = (g.b + g.ft).to_numpy()
    ps = np.array([p_dip_given_tp(x, a, u, th, d)[0] for x, a, u in zip(X, A, U)])
    ok = ~np.isnan(ps); ps = ps[ok]; obs = (g.mae1.to_numpy() >= d)[ok]
    k = int(obs.sum()); n = int(ok.sum()); mu = ps.sum(); var = (ps * (1 - ps)).sum()
    z = (k - mu) / math.sqrt(var) if var > 0 else float("nan")
    pv = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))) if not np.isnan(z) else float("nan")
    return {"lab": lab, "n": n, "k": k, "obs": k / n, "exp": mu / n, "z": z, "p": pv}


def fmt_row(r):
    return "| %-22s | %5d | %5d | %5.1f%% | %5.1f%% | %+5.1fpt | %+6.2f | %.4f |" % (
        r["lab"], r["n"], r["k"], 100 * r["obs"], 100 * r["exp"], 100 * (r["obs"] - r["exp"]), r["z"], r["p"])


# ─────────────────────────── 3. 離散 MC（建玉足終値から出発） ───────────────────────────
def simulate_bars(H, Lo, C, b, ft):
    nsim, nb = H.shape
    sl_hit = Lo <= -(1.0 - ft); tp_hit = H >= (b + ft)
    any_hit = sl_hit | tp_hit
    first = np.where(any_hit.any(1), any_hit.argmax(1), nb - 1)
    rows = np.arange(nsim)
    is_sl = sl_hit[rows, first]; is_tp = tp_hit[rows, first] & ~is_sl
    mask = np.arange(nb)[None, :] <= first[:, None]
    mae = np.maximum(-np.where(mask, Lo, np.inf).min(1), 0.0)
    return is_tp, mae


def mc_from_x0(g, kappa, th, nsim=400, m=6):
    """各本: 建玉足終値 x0 から、σ=κ×ATR/risk の RW を offset1.. で回し、TP で終わった path の MAE(offset1..)≥0.5 の割合。"""
    k_tot = 0; n_tot = 0; holds = []
    for _, t in g.iterrows():
        if t.atr is None or np.isnan(t.atr): continue
        sig = kappa * t.atr / t.risk; ss = sig / math.sqrt(m); mu = th * ss * ss / 2.0
        inc = rng.normal(mu, ss, size=(nsim, MAX_HOLD, m))
        path = t.x0 + np.cumsum(inc.reshape(nsim, -1), axis=1).reshape(nsim, MAX_HOLD, m)
        H = path.max(2); Lo = path.min(2); C = path[:, :, -1]
        # 足の始値(=前足終値)も足のレンジに含める
        prev = np.concatenate([np.full((nsim, 1), t.x0), C[:, :-1]], axis=1)
        H = np.maximum(H, prev); Lo = np.minimum(Lo, prev)
        is_tp, mae = simulate_bars(H, Lo, C, t.b, t.ft)
        k_tot += int((is_tp & (mae >= 0.5)).sum()); n_tot += int(is_tp.sum())
    return k_tot, n_tot


# ─────────────────────────── 4. 実データ・プラセボ ───────────────────────────
def placebo_real(g, m5, nper=50):
    """同JST時・同側・同幾何(ATR尺度合わせ)でランダム建玉。建玉足終値を x0 として、offset1.. の MAE≥0.5 | TP。"""
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    n = len(o); tr_ = h - l; atr = pd.Series(tr_).rolling(14).mean().shift(1).to_numpy()
    hours = m5.index.hour.to_numpy(); valid = np.arange(14, n - MAX_HOLD - 2)
    k_tot = 0; n_tot = 0; k_all = 0; n_all = 0
    for _, t in g.iterrows():
        if t.atr is None or np.isnan(t.atr) or t.atr <= 0: continue
        hu = (t.jh - 9) % 24; cand = valid[hours[valid] == hu]
        j = rng.choice(cand, size=nper, replace=True)
        scale = atr[j] / t.atr; risk_s = t.risk * scale; entry = o[j]   # 建玉=足の始値(逆指値の約定前レンジは無い)
        idx = j[:, None] + np.arange(MAX_HOLD + 1)[None, :]
        sgn = 1.0 if t.side == "BUY" else -1.0
        A = sgn * (h[idx] - entry[:, None]) / risk_s[:, None]; B = sgn * (l[idx] - entry[:, None]) / risk_s[:, None]
        H = np.maximum(A, B); Lo = np.minimum(A, B); C = sgn * (c[idx] - entry[:, None]) / risk_s[:, None]
        # 全体(建玉足込み)
        is_tp, mae = simulate_bars(H, Lo, C, t.b, t.ft)
        k_all += int((is_tp & (mae >= 0.5)).sum()); n_all += int(is_tp.sum())
        # 建玉足除外: offset1.. のみ（建玉足で決着した path は除く）
        sl0 = Lo[:, 0] <= -(1 - t.ft); tp0 = H[:, 0] >= (t.b + t.ft); alive = ~(sl0 | tp0)
        if alive.any():
            is_tp1, mae1 = simulate_bars(H[alive, 1:], Lo[alive, 1:], C[alive, 1:], t.b, t.ft)
            k_tot += int((is_tp1 & (mae1 >= 0.5)).sum()); n_tot += int(is_tp1.sum())
    return (k_tot, n_tot), (k_all, n_all)


# ─────────────────────────── main ───────────────────────────
def main():
    t0 = time.time()
    say("# AUREL [REFUTE] cycle0 C4 — 2010-2026 scan path 版  %s" % time.strftime("%Y-%m-%d %H:%M"))
    m5 = None
    if os.path.exists(PATHS_JSON) and "--rebuild" not in sys.argv:
        trades = json.load(open(PATHS_JSON, encoding="utf-8"))["trades"]; say("cached paths %d trades" % len(trades))
    else:
        trades, m5 = build_paths()
    df = pd.DataFrame(trades); df["ft"] = FEED_TOL / df.risk; df["atr"] = pd.to_numeric(df.atr, errors="coerce")
    df["era"] = np.where(df.year <= 2020, "2010-20", np.where(df.year <= 2023, "2021-23", "2024-26"))
    w = df.R > 0
    say("再加速 closed n=%d  勝率 %.1f%%  exit %s  期間 %d..%d" % (len(df), 100 * w.mean(), dict(collections.Counter(df.exit)), df.year.min(), df.year.max()))
    say("TP_R(b) 分位 10/50/90 = %s  b≤0.5 の本 %.0f%%  保有中央値 %d  hold=0 決着 %.1f%%" % (
        np.percentile(df.b, [10, 50, 90]).round(2).tolist(), 100 * (df.b <= 0.5).mean(), df.hold.median(), 100 * (df.hold == 0).mean()))
    say()
    # ── 建玉足アーティファクトの再確認（n 大）
    say("## 1. 建玉足(約定前レンジ含む)の寄与 — 台帳 n=167 で見えた構造が 16 年でも出るか")
    say("- 建玉足の始値が逆行側(open_gap>0): %.0f%%、open_gap 中央値 %+.2fR。建玉足だけの逆行 MAE_bar0 中央値 %.2fR、≥0.5R の本 %.0f%%" % (
        100 * (df.open_gap > 0).mean(), df.open_gap.median(), df.mae_bar0.median(), 100 * (df.mae_bar0 >= 0.5).mean()))
    say("- 勝ち本で MAE 全体の最大が建玉足で出ている割合: %.0f%%" % (100 * ((df.mae_bar0 >= df.mae0 - 1e-9) & w).sum() / w.sum()))
    say("- 建玉足終値 x0: 中央値 %+.2fR、勝ち %+.2f / 負け %+.2f" % (df.x0.median(), df.x0[w].median(), df.x0[~w].median()))
    say("| 定義 | 勝ちn | −0.5R まで沈んだ割合 |"); say("|---|---|---|")
    say("| 建玉足込み(台帳どおり) | %d | %.1f%% |" % (w.sum(), 100 * (df.mae0[w] >= 0.5).mean()))
    say("| 建玉足を除く(offset1..exit) | %d | %.1f%% |" % (w.sum(), 100 * (df.mae1[w] >= 0.5).mean()))
    say("| 建玉足のみ | %d | %.1f%% |" % (w.sum(), 100 * (df.mae_bar0[w] >= 0.5).mean()))
    say()

    # ── 主検定
    say("## 2. 主検定 C4（建玉足除外・x0 出発 RW・θ は hold≥1 本の勝率で推定）")
    sub = df[(df.hold >= 1) & ((1 - df.ft) > 0.5)].copy()
    th_x0 = fit_theta(sub, "x0")
    df0 = df.copy(); df0["zero"] = 0.0; th_all = fit_theta(df0, "zero")
    say("θ(x0 出発・hold≥1 n=%d・勝率 %.1f%%) = %.3f ／ θ(x=0・全本 n=%d) = %.3f ／ 台帳前回 θ=0.22" % (len(sub), 100 * (sub.R > 0).mean(), th_x0, len(df), th_all))
    g = sub[(sub.R > 0) & (sub.exit == "TP")]
    say("対象 = 勝ち(TP)・hold≥1・a>0.5: n=%d" % len(g))
    say("| 基準 | n | 沈んだk | 観測 | 期待 | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    main_r = c4_test(g, th_x0, "RW θ(x0) x0出発"); say(fmt_row(main_r))
    say(fmt_row(c4_test(g, 0.0, "RW θ=0 x0出発")))
    say(fmt_row(c4_test(g, th_all, "RW θ(全本) x0出発")))
    say(fmt_row(c4_test(g, th_x0, "RW θ(x0) 0出発(参考)", use_x0=False)))
    verdict_main = "復活(survived)" if main_r["p"] < ALPHA else ("弱い(p<0.05 だが Bonferroni 非有意)" if main_r["p"] < 0.05 else "broken")
    say("主検定: p=%.4f vs α=%.4f → **%s**" % (main_r["p"], ALPHA, verdict_main))
    say()

    # ── 部分集合（時代×壁種、Bonferroni 6）
    say("## 3. 部分集合（時代×壁種・θ は全体 x0 で固定・Bonferroni 6 → α=%.4f）" % (0.05 / 6))
    say("| 部分集合 | n | 沈んだk | 観測 | 期待 | 超過 | z | p |"); say("|---|---|---|---|---|---|---|---|")
    rows = []
    for era in ("2010-20", "2021-23", "2024-26"):
        for wk in ("outer", "mid"):
            gg = g[(g.era == era) & (g.wall_kind == wk)]
            r = c4_test(gg, th_x0, "%s %s" % (era, wk))
            if r: rows.append(r); say(fmt_row(r))
    for era in ("2010-20", "2021-23", "2024-26"):
        r = c4_test(g[g.era == era], th_x0, "時代 %s" % era)
        if r: say(fmt_row(r))
    for sd in ("BUY", "SELL"):
        r = c4_test(g[g.side == sd], th_x0, "側 %s" % sd)
        if r: say(fmt_row(r))
    def zone(j): return "本物帯7-12" if 7 <= j < 12 else ("ダマシ巣0-5" if j < 5 else "中立")
    for zn, gg in g.groupby(g.jh.map(zone)):
        r = c4_test(gg, th_x0, "時間帯 %s" % zn)
        if r: say(fmt_row(r))
    sig = [r for r in rows if r["p"] < 0.05 / 6]
    say("時代×壁種 6 分割で Bonferroni 有意: %d/%d  超過の符号: %s" % (len(sig), len(rows), " ".join("%+.0f" % (100 * (r["obs"] - r["exp"])) for r in rows)))
    say()

    # ── 別の閾値（構造確認）
    say("## 4. 閾値感度（d=0.3/0.5/0.7・採用判断に使わない）")
    for d in (0.3, 0.5, 0.7):
        gd = sub[(sub.R > 0) & (sub.exit == "TP") & ((1 - sub.ft) > d)]
        r = c4_test(gd, th_x0, "d=%.1f" % d, d=d); say(fmt_row(r))
    say()

    # ── 離散 MC
    say("## 5. 離散 MC（x0 出発・足高値安値・FEED_TOL・同足SL優先、κ は保有中央値校正）")
    gm = g[g.atr.notna()].sample(min(600, g.atr.notna().sum()), random_state=1) if len(g) > 600 else g[g.atr.notna()]
    say("  対象のうちサンプル %d 本 × 400 path" % len(gm))
    for kappa in (0.4, 0.6, 0.8, 1.0):
        k, n = mc_from_x0(gm, kappa, th_x0, nsim=400)
        say("  κ=%.1f: TP path %d のうち −0.5R 沈み %d = %.1f%%  （観測 %.1f%%）" % (kappa, n, k, 100 * k / max(n, 1), 100 * main_r["obs"]))
    say()

    # ── 実データ・プラセボ
    say("## 6. 実データ・プラセボ（同JST時・同側・同幾何、ランダム建玉=足の始値、50本/取引）")
    if m5 is None:
        m5 = load_all()
    gp = g[g.atr.notna()]
    gp = gp.sample(min(1500, len(gp)), random_state=2) if len(gp) > 1500 else gp
    (k1, n1), (ka, na) = placebo_real(gp, m5, nper=50)
    say("  建玉足除外: TP path %d のうち −0.5R 沈み %d = %.1f%%  ／ 建玉足込み: %d のうち %d = %.1f%%  （観測 建玉足除外 %.1f%% ／ 込み %.1f%%）" % (
        n1, k1, 100 * k1 / max(n1, 1), na, ka, 100 * ka / max(na, 1), 100 * main_r["obs"], 100 * (df.mae0[w] >= 0.5).mean()))
    say()
    say("(elapsed %.0fs)" % (time.time() - t0))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
