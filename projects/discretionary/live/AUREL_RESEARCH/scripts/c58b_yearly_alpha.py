# -*- coding: utf-8 -*-
"""
[cycle62 研究レーン 2026-11-23] c58（ボラ管理 α）の補・記述のみ・判定には使わない。
目的 = c58 の最重大反証「近年 2024-26H1 の α +5.87 bp/日 は 1 本の上昇トレンド episode の顔（c41b: 金の年別 γ は年間トレンド符号に追随）」を数値化する。
  (a) 年別 VM21 α（NW(5) t・n）と 同年の raw 平均リターン・raw SR → Spearman(α_y, r̄_y)・符号一致年数（c41b と同じ検査）。
  (b) 近年を 2024／2025／2026H1 に分けた α（episode が 1 年か 3 年か）。
  (c) 受け取れるか: 日次リバランスの回転 mean|Δw|（w = c/σ̂21・名目比）× 往復 5.3 bp（0.16 USD／3000 USD）→ bp/日 のコスト概算。
データ・定義は c58 と同一（XAU_m5_close.npz／US500_m5_close.npz・セッション日 (ET+6h)・非 flat ≥100・σ̂21 = sqrt(mean RV_{d-20..d})）。seed 不要（決定論）。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd
from scipy.stats import spearmanr

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c58b_yearly_alpha.md")
NY = "America/New_York"; NFMIN = 100; LB = 21; NWLAG = 5
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle62 補 c58b] ボラ管理 α の年別構造・episode 分解・回転コスト（記述） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c58b_yearly_alpha.py)")

def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.asarray(X, float)
    if X.ndim == 1: X = X[:, None]
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv
    return b, np.sqrt(np.diag(V))

def daily_table(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    say(f"- {sym}: npz {len(ts)} 本 {pd.to_datetime(ts[0], unit='s').date()}〜{pd.to_datetime(ts[-1], unit='s').date()} UTC・flat 全体 {flat.mean()*100:.1f}%")
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep], "r2": r[keep] ** 2})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"] = D["date"].dt.weekday
    D = D[(D.wd <= 4) & (D.nf >= NFMIN)].reset_index()
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["sig21"] = np.sqrt(D["rv"].rolling(LB).mean()) * 1e4
    D["year"] = D["date"].dt.year
    return D

def alpha_cell(D, mask):
    sig = D["sig21"].to_numpy()[:-1]; r = D["r"].to_numpy()[1:]
    m = mask & np.isfinite(sig) & np.isfinite(r) & (sig > 0)
    rr = r[m]; ss = sig[m]
    if len(rr) < 60: return None
    w = 1.0 / ss; vm = w * rr; c = rr.std(ddof=1) / vm.std(ddof=1); vm = vm * c
    b, se = nw_ols(vm, rr)
    sr_raw = rr.mean() / rr.std(ddof=1) * math.sqrt(252); sr_vm = vm.mean() / vm.std(ddof=1) * math.sqrt(252)
    wn = c * w  # weight in notional units (mean ≈ 1 by construction up to sd scaling)
    turn = np.abs(np.diff(wn)).mean()
    return dict(n=len(rr), a=b[0], t=b[0]/se[0], rbar=rr.mean(), sr_raw=sr_raw, sr_vm=sr_vm, turn=turn, wmean=wn.mean(), wmax=wn.max())

for sym, y0 in [("XAU", 2010), ("US500", 2014)]:
    D = daily_table(sym)
    yr = D["year"].to_numpy()[1:]
    say(f"\n## {sym} 年別 VM21 α（NW(5) t）と同年 raw 平均・SR")
    rows = []
    for y in range(y0, 2027):
        c = alpha_cell(D, yr == y)
        if c is None: continue
        rows.append((y, c))
        say(f"- {y}: n {c['n']}・α {c['a']:+.2f} bp/日 (t {c['t']:+.2f})・raw r̄ {c['rbar']:+.1f} bp/日・SR raw {c['sr_raw']:+.2f} → VM {c['sr_vm']:+.2f}（Δ {c['sr_vm']-c['sr_raw']:+.2f}）")
    A = np.array([c["a"] for _, c in rows]); R = np.array([c["rbar"] for _, c in rows]); T = np.array([c["t"] for _, c in rows])
    rho, p = spearmanr(A, R)
    agree = int(np.sum(np.sign(A) == np.sign(R)))
    say(f"- 年横断: Spearman(α_y, r̄_y) {rho:+.2f} (p {p:.3f})・符号一致 {agree}/{len(rows)} 年・α>0 の年 {int((A>0).sum())}/{len(rows)}・|t|≥2 の年 {int((np.abs(T)>=2).sum())}（{', '.join(str(y) for (y,c) in rows if abs(c['t'])>=2)}）")
    say(f"- 年横断: Spearman(α_y, |r̄_y|) {spearmanr(A, np.abs(R))[0]:+.2f}（トレンドの強さ・向き不問）・Spearman(α_y, SR_raw_y) {spearmanr(A, [c['sr_raw'] for _, c in rows])[0]:+.2f}")
    # windows + turnover/cost
    say(f"\n## {sym} 窓別 回転と費用（w = c/σ̂21 名目比・往復 5.3 bp 仮定 = 0.16 USD／3000 USD；US500 は参考）")
    for wname, (a0, a1) in {"在": (y0, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}.items():
        c = alpha_cell(D, (yr >= a0) & (yr <= a1))
        cost = c["turn"] * 5.3 / 2  # one-way per unit notional change ≈ half round trip
        say(f"- {wname}: n {c['n']}・α {c['a']:+.2f} (t {c['t']:+.2f})・w̄ {c['wmean']:.2f}・w_max {c['wmax']:.2f}・mean|Δw| {c['turn']:.3f}/日 → 回転費用 ≈ {cost:.2f} bp/日・α − 費用 {c['a']-cost:+.2f}")
    if sym == "XAU":
        say(f"\n## XAU 近年 2024-26H1 の episode 分解と前半/後半")
        for lab, mk in [("2024", yr == 2024), ("2025", yr == 2025), ("2026H1", yr == 2026),
                        ("2024-25", (yr >= 2024) & (yr <= 2025)), ("2021-23（外の前半）", (yr >= 2021) & (yr <= 2023))]:
            c = alpha_cell(D, mk)
            if c: say(f"- {lab}: n {c['n']}・α {c['a']:+.2f} (t {c['t']:+.2f})・raw r̄ {c['rbar']:+.1f}・SR raw {c['sr_raw']:+.2f} → VM {c['sr_vm']:+.2f}")
        # 2011-12 (previous bull) and 2013 (crash) as in-sample analogues of a trend episode
        say(f"\n## XAU 在の trend episode 対照（2010-12 上昇・2013 急落・2014-18 横ばい）")
        for lab, mk in [("2010-12", (yr >= 2010) & (yr <= 2012)), ("2013", yr == 2013), ("2014-18", (yr >= 2014) & (yr <= 2018)), ("2019-20", (yr >= 2019) & (yr <= 2020))]:
            c = alpha_cell(D, mk)
            if c: say(f"- {lab}: n {c['n']}・α {c['a']:+.2f} (t {c['t']:+.2f})・raw r̄ {c['rbar']:+.1f}・SR raw {c['sr_raw']:+.2f} → VM {c['sr_vm']:+.2f}")

say(f"\n- 時間 {time.time()-T0:.1f} s・外部通信なし・scan 無し・決定論")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT)
