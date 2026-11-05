# -*- coding: utf-8 -*-
"""
c4_spread_structure.py — cycle4 [探索・執行] スプレッドの時間構造と、台帳 305 本への当てはめ（net R の時間帯構造）
読むだけ。入力 = spread_log.jsonl（94.6k 行・実口座 tick の 2 分サンプル）＋ setup_ledger.jsonl（統合最終状態の reaccel closed）。
scan 無し・M5 読込なし・MT5 接続なし。書き込みは AUREL_RESEARCH/data/c4_spread_structure_result.md のみ。

事前固定（コード前に記載・以後動かさない）
 問い: 執行コスト（スプレッド）は時間帯・曜日・直近ボラに構造的に依存するか。依存するなら、台帳の再加速 305 本の
       entry 時刻に当てたとき「どの帯で執行コストが edge を食うか」が記述できる（入口フィルタの再発明ではない・記述のみ）。
 データ: spread_log.jsonl 全行。ts 中央値で前半=在／後半=外（機械分割）。台帳は c3 と同じ統合手順で reaccel closed。
 帯（事前定義・JST）: rollover 6-7 / tokyo 8-14 / london 15-20 / overlap 21-1 / lateNY 2-5。本番帯 jh7-12 も併記。
 ボラ代理: 直前 12 行（≈24 分）の |Δbid| 合計を 1 行ずらして使う（look-ahead なし）。
 検定・予測（事前）:
  P1 時間帯プロファイルの安定: 在と外の JST 時別中央値の Spearman ρ ≥ 0.8。
  P2 rollover 帯の中央値 ≥ 1.5 × overlap 帯の中央値（在・外とも）。
  P3 直近ボラ依存: 在・外とも Spearman(spread, rv_lag) ≥ 0.2。時別中央値を引いた残差でも ≥ 0.1。
  P4 台帳 305 本の cost_R = spread/risk は帯で異なる（Kruskal p<0.05・方向は事前に置かない）。
  P5 台帳 entry 時刻のスプレッド中央値 < 0.56 USD（＝現行コスト仮定 0.56 の過半はスプレッドでなく滑り仮定）。
  P6 選択効果: entry 時刻のスプレッド（最近傍 ±5 分）は同時刻帯の無条件中央値より高い（逆指値は動いている時に発動する）。
 合否: 構造ありの判定 = P1 ∧ P2 ∧ P3。P4〜P6 は台帳への当てはめの報告。昇格候補ではない（コスト地図＝DATA_MAP §4 の肉）。
 最も重大な反証（事前）: spread_log は実口座(リアル)の 2 分サンプル。デモ口座の spread（10-23 実測 0.42）とは別物で、
   2 分サンプルは発動瞬間のスパイクを取り逃す → ここで出す cost_R は下限。P6 で部分的に測る。
 多重検定: 予測 6 本・帯 5 個を事前固定、格子探索なし。
"""
import json, os, sys, io, math, datetime as dt, collections
import numpy as np
import pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
SPREAD = os.path.join(LIVE, "spread_log.jsonl")
LEDGER = os.path.join(LIVE, "setup_ledger.jsonl")
OUT = os.path.join(LIVE, "AUREL_RESEARCH", "data", "c4_spread_structure_result.md")
COST_USD = 0.56
lines = []
def P(s=""):
    print(s); lines.append(s)

BANDS = {"rollover": {6, 7}, "tokyo": set(range(8, 15)), "london": set(range(15, 21)),
         "overlap": {21, 22, 23, 0, 1}, "lateNY": {2, 3, 4, 5}}
def band_of(h):
    for b, hs in BANDS.items():
        if h in hs: return b
    return "?"

def spearman(a, b):
    a = pd.Series(a).rank(); b = pd.Series(b).rank()
    return float(np.corrcoef(a, b)[0, 1])

# ---------- spread log ----------
def load_spread():
    rows = []
    with open(SPREAD, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except Exception: pass
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["ts", "spread_pt"]).sort_values("ts").reset_index(drop=True)
    df["jst"] = pd.to_datetime(df["ts"], unit="s", utc=True).dt.tz_convert("Asia/Tokyo")
    df["jh"] = df["jst"].dt.hour
    df["wd"] = df["jst"].dt.dayofweek  # Mon=0
    df["band"] = df["jh"].map(band_of)
    # lagged realized-vol proxy: sum |Δbid| over previous 12 rows, shifted by 1 (known before this row)
    db = df["bid"].diff().abs()
    df["rv_lag"] = db.rolling(12, min_periods=6).sum().shift(1)
    return df

# ---------- ledger (same reconstruction as c3) ----------
def load_ledger():
    state = {}
    with open(LEDGER, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            r = json.loads(line)
            k = r.get("kind")
            if k == "setup" and r.get("id"):
                state[r["id"]] = dict(r)
            elif k == "update" and r.get("target"):
                st = state.setdefault(r["target"], {"id": r["target"]})
                for kk, vv in r.items():
                    if kk in ("kind", "logged_at", "target"): continue
                    st[kk] = vv
    trades = []
    for sid, st in state.items():
        ra = st.get("reaccel")
        if isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None:
            e, sl = ra.get("entry"), ra.get("sl")
            risk = abs(e - sl) if (e is not None and sl is not None) else np.nan
            trades.append(dict(id=sid, t=ra.get("entry_time") or 0, R=float(ra["R"]), risk=risk,
                               exit=ra.get("exit_reason"), side=st.get("side"),
                               sp_ledger=ra.get("spread_pt", st.get("spread_pt")),
                               slip_pt=ra.get("slip_pt", st.get("slip_pt")), slip_src=ra.get("slip_src", st.get("slip_src"))))
    tr = pd.DataFrame(trades).sort_values("t").reset_index(drop=True)
    tr["jst"] = pd.to_datetime(tr["t"], unit="s", utc=True).dt.tz_convert("Asia/Tokyo")
    tr["jh"] = tr["jst"].dt.hour
    tr["band"] = tr["jh"].map(band_of)
    return tr

def kruskal(groups):
    # Kruskal-Wallis H with chi2 approx (scipy-free)
    allv = np.concatenate(groups); N = len(allv)
    ranks = pd.Series(allv).rank().values
    H = 0.0; i = 0
    for g in groups:
        r = ranks[i:i+len(g)]; i += len(g)
        H += r.sum()**2 / len(g)
    H = 12.0 / (N*(N+1)) * H - 3*(N+1)
    k = len(groups) - 1
    # chi2 sf via regularized gamma (series/continued fraction light impl)
    from math import lgamma, exp, log
    def gammainc_upper(s, x):
        # Q(s,x) via continued fraction (Numerical Recipes gcf) for x > s+1 else 1 - series
        if x < s + 1:
            term = 1.0 / s; summ = term; n = 1
            while n < 500:
                term *= x / (s + n); summ += term; n += 1
                if abs(term) < abs(summ) * 1e-12: break
            return 1.0 - summ * exp(-x + s*log(x) - lgamma(s))
        b = x + 1 - s; c = 1e300; d = 1.0 / b; h = d
        for i2 in range(1, 500):
            an = -i2 * (i2 - s); b += 2
            d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
            c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
            d = 1.0 / d; de = d * c; h *= de
            if abs(de - 1) < 1e-12: break
        return exp(-x + s*log(x) - lgamma(s)) * h
    p = gammainc_upper(k/2.0, H/2.0)
    return H, p

def main():
    P("# cycle4 [探索・執行] スプレッドの時間構造 — 2026-11-05  (scripts/c4_spread_structure.py)")
    df = load_spread()
    t0, t1 = df["jst"].iloc[0], df["jst"].iloc[-1]
    P(f"\n## spread_log 概況: n={len(df)}  期間 {t0:%Y-%m-%d %H:%M} .. {t1:%Y-%m-%d %H:%M} JST")
    gaps = df["ts"].diff()
    P(f"- サンプル間隔 中央値 {gaps.median():.0f}s  p90 {gaps.quantile(.9):.0f}s  >10 分の欠測区間 {int((gaps>600).sum())} 回（うち >12 時間 {int((gaps>43200).sum())} 回＝週末等）  最長 {gaps.max()/3600:.1f} h")
    P(f"- spread_pt(USD): 中央値 {df.spread_pt.median():.3f}  平均 {df.spread_pt.mean():.3f}  p10 {df.spread_pt.quantile(.1):.2f}  p90 {df.spread_pt.quantile(.9):.2f}  p99 {df.spread_pt.quantile(.99):.2f}  max {df.spread_pt.max():.2f}  (>0.30: {(df.spread_pt>0.30).mean()*100:.2f}%  >0.56: {(df.spread_pt>0.56).mean()*100:.3f}%)")
    per_day = df.groupby(df["jst"].dt.date).size()
    P(f"- 日別行数: 中央値 {per_day.median():.0f}  最小 {per_day.min()} ({per_day.idxmin()})  日数 {len(per_day)}")
    tmed = df["ts"].median()
    IS = df[df.ts <= tmed]; OOS = df[df.ts > tmed]
    P(f"- 在 n={len(IS)} ({IS.jst.iloc[0]:%m-%d}..{IS.jst.iloc[-1]:%m-%d}) / 外 n={len(OOS)} ({OOS.jst.iloc[0]:%m-%d}..{OOS.jst.iloc[-1]:%m-%d})")

    # Q1 hour profile
    P("\n## Q1 JST 時別プロファイル（中央値 / p90）")
    hi = IS.groupby("jh").spread_pt.agg(["median", lambda s: s.quantile(.9), "size"])
    ho = OOS.groupby("jh").spread_pt.agg(["median", lambda s: s.quantile(.9), "size"])
    hi.columns = ho.columns = ["med", "p90", "n"]
    both = hi.join(ho, lsuffix="_in", rsuffix="_out", how="inner")
    P("| JST | 在 med | 在 p90 | 在 n | 外 med | 外 p90 | 外 n | 帯 |")
    P("|---|---|---|---|---|---|---|---|")
    for h, r in both.iterrows():
        P(f"| {h:02d} | {r.med_in:.3f} | {r.p90_in:.2f} | {int(r.n_in)} | {r.med_out:.3f} | {r.p90_out:.2f} | {int(r.n_out)} | {band_of(h)} |")
    rho_med = spearman(both.med_in, both.med_out); rho_p90 = spearman(both.p90_in, both.p90_out)
    P(f"- **P1** Spearman(在時別中央値, 外時別中央値) = {rho_med:.3f}  (p90 版 {rho_p90:.3f})  → {'PASS' if rho_med>=0.8 else 'FAIL'} (基準 ≥0.8)")
    P(f"- 時別中央値の幅: 在 {both.med_in.min():.2f}..{both.med_in.max():.2f}  外 {both.med_out.min():.2f}..{both.med_out.max():.2f}  ＝ max/min 在 {both.med_in.max()/both.med_in.min():.2f}x 外 {both.med_out.max()/both.med_out.min():.2f}x")

    # Q2 bands
    P("\n## Q2 帯別（事前定義）")
    P("| 帯 | 在 med | 在 mean | 在 p90 | 在 n | 外 med | 外 mean | 外 p90 | 外 n |")
    P("|---|---|---|---|---|---|---|---|---|")
    bi = IS.groupby("band").spread_pt; bo = OOS.groupby("band").spread_pt
    for b in BANDS:
        si, so = bi.get_group(b), bo.get_group(b)
        P(f"| {b} | {si.median():.3f} | {si.mean():.3f} | {si.quantile(.9):.2f} | {len(si)} | {so.median():.3f} | {so.mean():.3f} | {so.quantile(.9):.2f} | {len(so)} |")
    r_in = bi.get_group("rollover").median() / bi.get_group("overlap").median()
    r_out = bo.get_group("rollover").median() / bo.get_group("overlap").median()
    rm_in = bi.get_group("rollover").mean() / bi.get_group("overlap").mean()
    rm_out = bo.get_group("rollover").mean() / bo.get_group("overlap").mean()
    P(f"- **P2** rollover/overlap 中央値比 在 {r_in:.2f}x 外 {r_out:.2f}x (平均比 {rm_in:.2f}x/{rm_out:.2f}x) → {'PASS' if (r_in>=1.5 and r_out>=1.5) else 'FAIL'} (基準 ≥1.5 両方)")
    prod = df[df.jh.between(7, 12)]; rest = df[~df.jh.between(7, 12)]
    P(f"- 本番帯 jh7-12: med {prod.spread_pt.median():.3f} mean {prod.spread_pt.mean():.3f} p90 {prod.spread_pt.quantile(.9):.2f} / それ以外 med {rest.spread_pt.median():.3f} mean {rest.spread_pt.mean():.3f} p90 {rest.spread_pt.quantile(.9):.2f}")
    # weekday (descriptive)
    wd = df.groupby("wd").spread_pt.agg(["median", "mean", lambda s: s.quantile(.9), "size"]); wd.columns = ["med", "mean", "p90", "n"]
    P("- 曜日(JST, Mon=0): " + "  ".join(f"{int(d)}:med {r.med:.3f}/p90 {r.p90:.2f}/n {int(r.n)}" for d, r in wd.iterrows()))

    # Q3 vol dependence
    P("\n## Q3 直近ボラ依存（rv_lag = 直前 12 行の |Δbid| 合計・1 行ずらし）")
    out = []
    for name, d in (("在", IS), ("外", OOS)):
        d = d.dropna(subset=["rv_lag"])
        # exclude rows after a gap > 10 min (rv proxy meaningless)
        d = d[d.ts.diff().fillna(0) <= 600]
        rho = spearman(d.spread_pt, d.rv_lag)
        med_h = d.groupby("jh").spread_pt.transform("median")
        rho_res = spearman(d.spread_pt - med_h, d.rv_lag)
        q = pd.qcut(d.rv_lag.rank(method="first"), 5, labels=False)
        byq = d.groupby(q).spread_pt.agg(["median", "mean", lambda s: s.quantile(.9)])
        P(f"- {name} n={len(d)}: Spearman(spread, rv_lag) = {rho:.3f}  時別中央値を引いた残差版 {rho_res:.3f}  rv 五分位の spread 中央値 " + " ".join(f"{m:.3f}" for m in byq['median']) + "  平均 " + " ".join(f"{m:.3f}" for m in byq['mean']) + "  p90 " + " ".join(f"{m:.2f}" for m in byq.iloc[:, 2]))
        out.append((rho, rho_res))
    p3 = all(r >= 0.2 for r, _ in out) and all(rr >= 0.1 for _, rr in out)
    P(f"- **P3** → {'PASS' if p3 else 'FAIL'} (基準 ρ≥0.2 両方・残差 ≥0.1 両方)")

    # Q4-6 ledger application
    P("\n## Q4-6 台帳 reaccel closed への当てはめ")
    tr = load_ledger()
    P(f"- 台帳 n={len(tr)}  期間 {tr.jst.iloc[0]:%Y-%m-%d}..{tr.jst.iloc[-1]:%Y-%m-%d}  帯別本数 {dict(collections.Counter(tr.band))}  jh7-12 {int(tr.jh.between(7,12).sum())}")
    P(f"- 台帳 spread_pt 記録あり {int(tr.sp_ledger.notna().sum())} 本 / slip_pt あり {int(tr.slip_pt.notna().sum())} 本 (slip_src: {dict(collections.Counter(tr.slip_src.dropna()))})")
    # nearest spread row within ±300 s
    sp_ts = df["ts"].values; sp_v = df["spread_pt"].values
    idx = np.searchsorted(sp_ts, tr["t"].values)
    near = np.full(len(tr), np.nan)
    for i, (t, j) in enumerate(zip(tr["t"].values, idx)):
        cands = [j-1, j]
        best = None
        for c in cands:
            if 0 <= c < len(sp_ts) and abs(sp_ts[c] - t) <= 300:
                if best is None or abs(sp_ts[c]-t) < abs(sp_ts[best]-t): best = c
        if best is not None: near[i] = sp_v[best]
    tr["sp_near"] = near
    # hour-median from IS spread (fixed, no look-ahead relative to spread halves)
    hmed_in = IS.groupby("jh").spread_pt.median()
    tr["sp_hmed"] = tr.jh.map(hmed_in)
    tr["sp_use"] = tr.sp_near.fillna(tr.sp_hmed)
    cov = tr.sp_near.notna().mean()
    P(f"- 最近傍 ±5 分の spread_log 行がある本 {cov*100:.1f}%（無い本は在の時別中央値で補完）")
    both_ok = tr.dropna(subset=["sp_near", "sp_ledger"])
    if len(both_ok):
        dlt = (both_ok.sp_ledger.astype(float) - both_ok.sp_near)
        P(f"- 検証: 台帳 spread_pt vs spread_log 最近傍 (n={len(both_ok)}): 差 中央値 {dlt.median():+.3f} 平均 {dlt.mean():+.3f} |差|≤0.02 の割合 {(dlt.abs()<=0.02).mean()*100:.0f}%  Spearman {spearman(both_ok.sp_ledger.astype(float), both_ok.sp_near):.2f}")
    tr["cost_R"] = tr.sp_use / tr.risk
    tr["netR_sp"] = tr.R - tr.cost_R
    tr["netR_056"] = tr.R - COST_USD / tr.risk
    P(f"- **P5** entry 時刻 spread 中央値 {tr.sp_use.median():.3f} USD (平均 {tr.sp_use.mean():.3f}, p90 {tr.sp_use.quantile(.9):.2f}, max {tr.sp_use.max():.2f}) vs 仮定 0.56 → {'PASS' if tr.sp_use.median() < 0.56 else 'FAIL'}; スプレッドは仮定の {tr.sp_use.median()/COST_USD*100:.0f}%")
    P(f"- risk 中央値 {tr.risk.median():.2f} USD → cost_R 中央値 {tr.cost_R.median():.4f}R 平均 {tr.cost_R.mean():.4f}R (0.56 仮定なら {np.median(COST_USD/tr.risk):.4f}R)")
    P(f"- 全体: gross 平均R {tr.R.mean():+.4f}  net(spread のみ) {tr.netR_sp.mean():+.4f}  net(0.56) {tr.netR_056.mean():+.4f}  → spread が gross を食う割合 {tr.cost_R.mean()/tr.R.mean()*100:.1f}%")
    P("\n| 帯 | n | gross 平均R | spread 中央値 | cost_R 平均 | net(spread) 平均R | cost/gross | net(0.56) 平均R |")
    P("|---|---|---|---|---|---|---|---|")
    groups = []
    for b in BANDS:
        g = tr[tr.band == b]
        if len(g) == 0: P(f"| {b} | 0 | | | | | | |"); continue
        groups.append(g.cost_R.values)
        cg = (g.cost_R.mean()/g.R.mean()*100) if g.R.mean() != 0 else float('nan')
        P(f"| {b} | {len(g)} | {g.R.mean():+.3f} | {g.sp_use.median():.3f} | {g.cost_R.mean():.4f} | {g.netR_sp.mean():+.3f} | {cg:+.0f}% | {g.netR_056.mean():+.3f} |")
    g = tr[tr.jh.between(7, 12)]; g2 = tr[~tr.jh.between(7, 12)]
    P(f"| jh7-12 | {len(g)} | {g.R.mean():+.3f} | {g.sp_use.median():.3f} | {g.cost_R.mean():.4f} | {g.netR_sp.mean():+.3f} | {g.cost_R.mean()/g.R.mean()*100:+.0f}% | {g.netR_056.mean():+.3f} |")
    P(f"| other | {len(g2)} | {g2.R.mean():+.3f} | {g2.sp_use.median():.3f} | {g2.cost_R.mean():.4f} | {g2.netR_sp.mean():+.3f} | {g2.cost_R.mean()/g2.R.mean()*100:+.0f}% | {g2.netR_056.mean():+.3f} |")
    H, p = kruskal([x for x in groups if len(x) >= 5])
    P(f"- **P4** cost_R の帯差 Kruskal H={H:.2f} p={p:.4f} → {'PASS' if p < 0.05 else 'FAIL'}; spread_use 自体の帯差: " + "  ".join(f"{b}:{tr[tr.band==b].sp_use.median():.3f}" for b in BANDS if (tr.band==b).any()))
    Hs, ps = kruskal([tr[tr.band == b].sp_use.values for b in BANDS if (tr.band == b).sum() >= 5])
    Hr, pr = kruskal([tr[tr.band == b].risk.values for b in BANDS if (tr.band == b).sum() >= 5])
    P(f"  分解: spread の帯差 H={Hs:.2f} p={ps:.4f} / risk の帯差 H={Hr:.2f} p={pr:.4f}（cost_R の帯差がどちら由来か）")
    # P6 selection: entry-time spread vs unconditional same-hour median (full log)
    hmed_all = df.groupby("jh").spread_pt.median()
    ok = tr.dropna(subset=["sp_near"])
    excess = ok.sp_near - ok.jh.map(hmed_all)
    frac_above = (excess > 0).mean(); frac_eq = (excess == 0).mean()
    # sign test (binomial, excluding ties)
    nz = excess[excess != 0]; k = int((nz > 0).sum()); n = len(nz)
    from math import comb
    p_sign = sum(comb(n, i) for i in range(k, n+1)) / 2**n if n else float('nan')
    P(f"- **P6** entry 時刻 spread − 同時刻帯無条件中央値: 中央値 {excess.median():+.3f} 平均 {excess.mean():+.3f}  >0 {frac_above*100:.0f}% / =0 {frac_eq*100:.0f}% / <0 {(excess<0).mean()*100:.0f}%  符号検定(同値除く n={n}) p={p_sign:.3f} → {'PASS' if (excess.median()>0 or (frac_above>0.5 and p_sign<0.05)) else 'FAIL'}")
    P(f"  entry 時刻 spread の分布: p50 {ok.sp_near.median():.3f} p75 {ok.sp_near.quantile(.75):.3f} p90 {ok.sp_near.quantile(.9):.3f} max {ok.sp_near.max():.2f}  vs 全ログ p50 {df.spread_pt.median():.3f} p90 {df.spread_pt.quantile(.9):.2f}")
    # cost share by outcome
    P(f"- 決着別 cost_R 平均: " + "  ".join(f"{e}:{tr[tr.exit==e].cost_R.mean():.4f}R (n{int((tr.exit==e).sum())})" for e in ("TP", "SL", "TIME") if (tr.exit==e).any()))
    # tail: top10% trades' cost
    top = tr.nlargest(max(1, len(tr)//10), "R")
    P(f"- 上位10% 本 (n={len(top)}) の cost_R 平均 {top.cost_R.mean():.4f}R  合計R {top.R.sum():+.1f} → spread 控除後 {top.netR_sp.sum():+.1f}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    P(f"\n(written {OUT})")

if __name__ == "__main__":
    main()
