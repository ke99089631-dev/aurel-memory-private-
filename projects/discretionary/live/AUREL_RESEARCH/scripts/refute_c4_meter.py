# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 補助 — 11:35 の「自分の結論への最も重大な反証」を自分で潰す。
11:35: 「レジームを年でなく客観メーター（ER/ボラ）で切れば結果が変わる可能性は残る」。
→ ここでは建玉時点で分かる 2 つのボラ・メーターで C4 を両方向・局所θで再検定する。
   M1: atr/risk（ATR14 ÷ ストップ幅 = “ストップがボラ何本分か”・幾何に直結・時代水準に依存しない比）
   M2: atr の 1 年ローリング順位（当年内 percentile。ドル水準のトレンドを除いた“今は荒いか静かか”）
   各メーターを 4 分位に割り、分位ごとに θ を局所推定。Bonferroni = 0.05 / (2 メーター × 4 分位) = 0.00625。
事前固定: 対象定義・沈み定義は 08:50/11:35 と同一。分位は 4 で固定。look-ahead なし（atr/risk は建玉足で確定）。
読取りのみ。入力 = data/refute_c4_scan_paths_2010_2026.json。出力 = data/refute_c4_meter.md。
"""
import os, json, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE)
DATA = os.path.join(RES, "data")
PATHS_JSON = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(DATA, "refute_c4_meter.md")
NQ = 4; ALPHA = 0.05 / (2 * NQ)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def p_hit(x, a, u, th):
    if x <= -a: return 0.0
    if x >= u: return 1.0
    if abs(th) < 1e-9: return (x + a) / (a + u)
    s = lambda y: math.exp(-th * y)
    return (s(x) - s(-a)) / (s(u) - s(-a))


def p_dip_given_tp(x0, a, u, th, d=0.5):
    pT = p_hit(x0, a, u, th)
    if pT <= 0: return float("nan")
    if x0 <= -d: return 1.0
    return (1.0 - p_hit(x0, d, u, th)) * p_hit(-d, a, u, th) / pT


def fit_theta(df):
    target = int((df.R > 0).sum()); lo, hi = -5.0, 5.0
    X = df.x0.to_numpy(); A = (1.0 - df.ft).to_numpy(); U = (df.b + df.ft).to_numpy()
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = sum(p_hit(x, a, u, mid) for x, a, u in zip(X, A, U))
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return 0.5 * (lo + hi)


def pb(obs, ps):
    ok = ~np.isnan(ps); ps = ps[ok]; obs = np.asarray(obs)[ok]
    k = int(obs.sum()); n = len(ps); mu = ps.sum(); var = (ps * (1 - ps)).sum()
    z = (k - mu) / math.sqrt(var) if var > 0 else float("nan")
    pv = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))) if not np.isnan(z) else float("nan")
    return k, n, mu / n if n else float("nan"), z, pv


def row(lab, k, n, exp, z, pv):
    say("| %-22s | %5d | %5d | %5.1f%% | %5.1f%% | %+5.1fpt | %+6.2f | %.4f |" % (lab, n, k, 100 * k / n, 100 * exp, 100 * (k / n - exp), z, pv))


def run_meter(sub, col, name):
    """sub: hold>=1 & a>0.5 の全本。col: メーター列。4 分位ごとに θ 局所推定し両方向検定。"""
    q = pd.qcut(sub[col], NQ, labels=False, duplicates="drop")
    edges = sub[col].quantile(np.linspace(0, 1, NQ + 1)).to_numpy()
    say("### %s — 分位境界: %s" % (name, " / ".join("%.3f" % e for e in edges)))
    say("| 分位 | n | 勝率 | 平均R | θ_local | 順: n_TP | 沈み観測 | 期待 | 超過 | z | p | 逆: n_dip | TP観測 | 期待 | 超過 | z | p |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    surv_f, surv_r, signs_r = [], [], []
    for qi in range(NQ):
        g = sub[q == qi]
        th = fit_theta(g)
        w = g[(g.R > 0) & (g.exit == "TP")]
        ps = np.array([p_dip_given_tp(x, a, u, th) for x, a, u in zip(w.x0, 1 - w.ft, w.b + w.ft)])
        kf, nf, ef, zf, pf = pb(w.mae1.to_numpy() >= 0.5, ps)
        dp = g[g.mae1 >= 0.5]
        ps2 = np.array([p_hit(-0.5, a, u, th) for a, u in zip(1 - dp.ft, dp.b + dp.ft)])
        kr, nr, er, zr, pr = pb((dp.exit == "TP").to_numpy(), ps2)
        say("| Q%d | %d | %.1f%% | %+.3f | %+.3f | %d | %.1f%% | %.1f%% | %+.1fpt | %+.2f | %.4f | %d | %.1f%% | %.1f%% | %+.1fpt | %+.2f | %.4f |" % (
            qi + 1, len(g), 100 * (g.R > 0).mean(), g.R.mean(), th,
            nf, 100 * kf / nf, 100 * ef, 100 * (kf / nf - ef), zf, pf,
            nr, 100 * kr / nr, 100 * er, 100 * (kr / nr - er), zr, pr))
        if pf < ALPHA and zf > 0: surv_f.append("Q%d" % (qi + 1))
        if pr < ALPHA and zr > 0: surv_r.append("Q%d" % (qi + 1))
        signs_r.append("+" if zr > 0 else "-")
    say("→ Bonferroni(α=%.5f) 正方向有意: 順 %s ／ 逆 %s ／ 逆の符号 Q1..Q4 = %s" % (ALPHA, surv_f or "なし", surv_r or "なし", "".join(signs_r)))
    say()
    return surv_f, surv_r


def main():
    J = json.load(open(PATHS_JSON, encoding="utf-8"))
    df = pd.DataFrame(J["trades"]); df["ft"] = J["frozen"]["FEED_TOL"] / df.risk
    df["t"] = pd.to_datetime(df.entry_time, unit="s", utc=True)
    df = df.sort_values("t").reset_index(drop=True)
    df["atr_risk"] = df.atr / df.risk
    # M2: atr の過去 1 年（同一銘柄・自分より前の setup のみ＝look-ahead 無し）内 percentile
    s = pd.Series(df.atr.to_numpy(), index=df.t)
    def trailing_pct(i):
        t0 = df.t.iloc[i]; win = s[(s.index > t0 - pd.Timedelta(days=365)) & (s.index < t0)]
        if len(win) < 50: return np.nan
        return (win < df.atr.iloc[i]).mean()
    df["atr_pct1y"] = [trailing_pct(i) for i in range(len(df))]
    say("# AUREL [REFUTE] C4 — 客観ボラ・メーター切り（11:35 の自分への反証を潰す）  (入力 %d 本, 生成 %s)" % (len(df), J["generated"]))
    say("Bonferroni α = 0.05 / (2 メーター × %d 分位) = %.5f。θ は分位ごとに局所推定。" % (NQ, ALPHA)); say()
    sub = df[(df.hold >= 1) & ((1 - df.ft) > 0.5)].copy()
    say("対象（hold≥1・a>0.5）n=%d。atr/risk 中央値 %.3f、atr_pct1y 利用可 n=%d（最初の 1 年は NaN）" % (len(sub), sub.atr_risk.median(), sub.atr_pct1y.notna().sum())); say()
    say("## M1: atr/risk（ストップ幅に対するボラ）")
    f1, r1 = run_meter(sub, "atr_risk", "M1 atr/risk")
    say("## M2: atr の直近 1 年内 percentile（時代水準を除いた荒さ）")
    sub2 = sub[sub.atr_pct1y.notna()]
    f2, r2 = run_meter(sub2, "atr_pct1y", "M2 atr_pct1y")
    say("## M1 × 近年窓 2024-26（D2: 近年で測る）")
    sub3 = sub[sub.year >= 2024]
    f3, r3 = run_meter(sub3, "atr_risk", "M1 atr/risk, 2024-26 のみ")
    say("## 判定: メーター切りで逆方向（使える向き）が Bonferroni 後に正で有意な分位: M1 %s ／ M2 %s ／ M1@2024-26 %s" % (r1 or "なし", r2 or "なし", r3 or "なし"))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
