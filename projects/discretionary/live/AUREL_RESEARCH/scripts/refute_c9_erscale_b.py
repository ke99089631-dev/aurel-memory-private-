# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-06 — refute_c9_erscale.py の事後フォロー（判定規則は不変・数字の追加のみ）
主スクリプトの判定が inconclusive になった唯一の理由 = Q3 の半期横断 ρ(top比率, D) が 1d +0.48 / 2d +0.37（≥0.3）。
ここで (1) ER_1d の付与率が 77% と低い理由（どの本が欠けるか・偏りの有無）、(2) ρ の置換 p（半期ラベルの置換 2000 回）と
9 尺度 Bonferroni、(3) 極端 2 半期（2023H2・2026H1）を除いた ρ、(4) 本レベルの 1d/2d 相互作用（主で ≈0）との食い違いの説明、
を数字で出す。読取りのみ・既存キャッシュのみ・書き込みは data/refute_c9_erscale_b.md。
"""
import os, math, time, importlib.util
import numpy as np, pandas as pd
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro"); OUT = os.path.join(DATA, "refute_c9_erscale_b.md")
rng = np.random.default_rng(20261106); L = []
def say(s=""): print(s, flush=True); L.append(s)
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se, se
def asof(ts, v, q, tol):
    i = np.searchsorted(ts, q, side="right") - 1; ok = i >= 0; out = np.full(len(q), np.nan); ii = i[ok]; age = q[ok] - ts[ii]
    out[ok] = np.where(age <= tol, v[ii], np.nan); return out

say(f"# [REFUTE c9 erscale b] 事後フォロー — {time.strftime('%Y-%m-%d %H:%M')}")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["sgn"] = np.where(X["side"] == "BUY", 1.0, -1.0); X["okA"] = X["ret24h_XAU"].notna() & (X["ret24h_XAU"] != 0)
X["A"] = (X["sgn"] * X["ret24h_XAU"]) > 0
dt = pd.to_datetime(X["entry_time"], unit="s"); X["half"] = X["year"].astype(str) + np.where(dt.dt.month <= 6, "H1", "H2"); X["dow"] = dt.dt.dayofweek
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); lc = np.log(z["close"].astype(np.float64))
def grid(step, off, strip_flat=False):
    gid = (ts - off) // step; df = pd.DataFrame({"g": gid, "ts": ts, "lc": lc}).groupby("g").agg(ts_last=("ts", "last"), lc=("lc", "last")).reset_index()
    df["known"] = df["ts_last"] + 300
    if strip_flat: df = df[df["lc"].diff().fillna(1.0) != 0.0].reset_index(drop=True)   # v1: flat（週末/休場）時間足を除外
    return df
DAY = grid(86400, 22 * 3600); HR = grid(3600, 0, strip_flat=True)
def er_series(lcv, n):
    s = pd.Series(lcv); return ((s - s.shift(n)).abs() / s.diff().abs().rolling(n).sum().replace(0, np.nan)).to_numpy()
def refs_daily(vals, win=500, minp=250):
    out = []
    for i in range(len(vals)):
        w = vals[max(0, i - win):i]; w = w[~np.isnan(w)]; out.append(np.sort(w) if len(w) >= minp else None)
    return out
def scale_H(n):
    er = er_series(HR["lc"].to_numpy(), n); known = HR["known"].to_numpy(); dk = DAY["known"].to_numpy()
    idx = np.searchsorted(known, dk, side="right") - 1; dvals = np.where(idx >= 0, er[np.clip(idx, 0, None)], np.nan); refs = refs_daily(dvals)
    di = np.searchsorted(dk, known, side="right") - 1; p = np.full(len(er), np.nan)
    for j in range(len(er)):
        r = refs[di[j]] if di[j] >= 0 else None
        if r is not None and not np.isnan(er[j]): p[j] = np.searchsorted(r, er[j]) / len(r)
    return known, p, er, refs
q = X["te"].to_numpy() - 86400
R = X["R"].to_numpy(); A = X["A"].to_numpy(); okA = X["okA"].to_numpy()

say("\n## (1) ER_1d の付与率 77% の内訳")
k1, p1, er1, refs1 = scale_H(24)
say(f"- 時間足 ER_1d: er NaN {np.isnan(er1).mean()*100:.1f}%・pct NaN {np.isnan(p1).mean()*100:.1f}%（er NaN は den=0 or 冒頭 24 本）")
# where NaN on trades
pt = asof(k1, p1, q, 5 * 86400); miss = np.isnan(pt)
say(f"- 本の付与率 {100-miss.mean()*100:.1f}%・欠ける本の曜日分布: " + ", ".join(f"{d}:{(X.dow[miss]==d).mean():.2f}" for d in range(7)) + f"・全本: " + ", ".join(f"{d}:{(X.dow==d).mean():.2f}" for d in range(7)))
# reason: hourly rolling(24) counts rows; weekend gap ⇒ den fine; pct NaN happens when the value is above/below? no—check refs None rate
dk = DAY["known"].to_numpy(); idx = np.searchsorted(k1, dk, side="right") - 1
dvals = np.where(idx >= 0, er1[np.clip(idx, 0, None)], np.nan)
say(f"- 日次サンプル（22:00 境界時点の時間足 ER_1d）: NaN {np.isnan(dvals).mean()*100:.1f}%（22:00 UTC は金の日次休場 21:00-22:00 直後＝その時刻に時間足が無い日が多い → 参照分布が薄い/欠ける）")
missing_days = pd.to_datetime(dk[np.isnan(dvals)], unit="s").dayofweek
say(f"- 日次サンプル NaN の曜日: " + ", ".join(f"{d}:{(missing_days==d).mean():.2f}" for d in range(7)))
# 欠ける本の R と A の分布（偏りの有無）
say(f"- 欠ける本 mean R {R[miss].mean():+.4f} (n{miss.sum()}) vs 付与あり {R[~miss].mean():+.4f}；A 比率 欠け {A[miss&okA].mean():.2f} vs あり {A[~miss&okA].mean():.2f}")

say("\n## (2) Q3 の ρ の置換 p（半期ラベル置換 2000 回）・9 尺度 Bonferroni・極端半期除外")
SCALES = [("1d", "H", 24), ("2d", "H", 48), ("3d", "H", 72), ("5d", "H", 120), ("10d", "H", 240), ("20d", "D", 20), ("60d", "D", 60), ("120d", "D", 120), ("250d", "D", 250)]
halves = sorted(X["half"].unique()); hl = X["half"].to_numpy()
Dh = np.array([welch(R[(hl == h) & okA & A], R[(hl == h) & okA & ~A])[0] for h in halves])
def scale_D(n):
    er = er_series(DAY["lc"].to_numpy(), n); known = DAY["known"].to_numpy(); refs = refs_daily(er); p = np.full(len(er), np.nan)
    for i in range(len(er)):
        r = refs[i]
        if r is not None and not np.isnan(er[i]): p[i] = np.searchsorted(r, er[i]) / len(r)
    return known, p
NP = 2000
rows = []
for name, kind, n in SCALES:
    known, p = (scale_H(n)[:2] if kind == "H" else scale_D(n)); pt = asof(known, p, q, 5 * 86400)
    frac = np.array([np.mean(pt[(hl == h) & ~np.isnan(pt)] >= 2 / 3) if ((hl == h) & ~np.isnan(pt)).sum() else np.nan for h in halves])
    ok = ~np.isnan(frac) & ~np.isnan(Dh); f, d = frac[ok], Dh[ok]
    rho = pd.Series(f).corr(pd.Series(d), method="spearman")
    null = np.array([pd.Series(f).corr(pd.Series(rng.permutation(d)), method="spearman") for _ in range(NP)])
    pperm = (np.abs(null) >= abs(rho)).mean()
    # drop 2 extreme halves (2023H2, 2026H1) and also LOO max-influence
    hh = np.array(halves)[ok]; keep = ~np.isin(hh, ["2023H2", "2026H1"])
    rho_x = pd.Series(f[keep]).corr(pd.Series(d[keep]), method="spearman")
    loo = [pd.Series(np.delete(f, i)).corr(pd.Series(np.delete(d, i)), method="spearman") for i in range(len(f))]
    # within-window: 2010-20 only
    k10 = np.array([h <= "2020H2" for h in hh]); rho_in = pd.Series(f[k10]).corr(pd.Series(d[k10]), method="spearman")
    rows.append((name, rho, pperm, min(1.0, pperm * 9), rho_x, min(loo), max(loo), rho_in, len(f)))
    say(f"- {name}: ρ {rho:+.2f} 置換 p {pperm:.3f} Bonf(9) {min(1.0,pperm*9):.3f} ｜ 除 2023H2+2026H1 ρ {rho_x:+.2f} ｜ LOO ρ 範囲 [{min(loo):+.2f}, {max(loo):+.2f}] ｜ 在 2010-20 の 22 半期のみ ρ {rho_in:+.2f}（n半期 {len(f)}）")
say(f"- ρ の最大 |ρ| の family-wise（9 尺度の max|ρ| を置換で）: ", )
# family-wise for max|rho| across scales: permute D once per iteration, compute all 9 rho
FR = []
for name, kind, n in SCALES:
    known, p = (scale_H(n)[:2] if kind == "H" else scale_D(n)); pt = asof(known, p, q, 5 * 86400)
    FR.append(np.array([np.mean(pt[(hl == h) & ~np.isnan(pt)] >= 2 / 3) if ((hl == h) & ~np.isnan(pt)).sum() else np.nan for h in halves]))
FR = np.array(FR); okh = ~np.isnan(FR).any(axis=0) & ~np.isnan(Dh)
obs = max(abs(pd.Series(FR[j, okh]).corr(pd.Series(Dh[okh]), method="spearman")) for j in range(9))
nullmax = []
for _ in range(NP):
    dp = rng.permutation(Dh[okh]); nullmax.append(max(abs(pd.Series(FR[j, okh]).corr(pd.Series(dp), method="spearman")) for j in range(9)))
nullmax = np.array(nullmax); say(f"  観測 max|ρ| {obs:.2f} → 帰無 中央値 {np.median(nullmax):.2f} / 95%点 {np.quantile(nullmax,0.95):.2f} / **p_fw {(nullmax >= obs).mean():.3f}**（{okh.sum()} 半期・{NP} 回）")

say("\n## (3) 本レベルで 1d/2d の top/bot 内の D（主の再掲・外/近年）と、半期の top 比率の時系列")
for name, n in (("1d", 24), ("2d", 48)):
    known, p, er, _ = scale_H(n); pt = asof(known, p, q, 5 * 86400)
    fr = [np.mean(pt[(hl == h) & ~np.isnan(pt)] >= 2 / 3) for h in halves]
    say(f"- {name} 半期 top 比率: " + " ".join(f"{h[2:]}:{v:.2f}" for h, v in zip(halves, fr)))
    for wn, m in (("外2021-26", X.year.to_numpy() >= 2021), ("近年2024-26", X.year.to_numpy() >= 2024)):
        top = m & ~np.isnan(pt) & (pt >= 2 / 3); bot = m & ~np.isnan(pt) & (pt <= 1 / 3)
        dT = welch(R[top & okA & A], R[top & okA & ~A]); dB = welch(R[bot & okA & A], R[bot & okA & ~A])
        say(f"  - {wn}: D_top {dT[0]:+.3f} (t{dT[1]:+.2f}) / D_bot {dB[0]:+.3f} (t{dB[1]:+.2f}) → I {dT[0]-dB[0]:+.3f}")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
