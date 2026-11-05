# -*- coding: utf-8 -*-
"""
[REFUTE c10 事後フォロー b] 2026-11-06 — 本編 Q1 の水平線掃引で N=80 営業日の実質金利追い風が 外 t+4.14・近年 t+4.13・在 t+0.15、
20 セル family-wise p 0.014 と出た（主張 Δ60 より強い・事前には名指ししていない＝事後セル）。本編の判定規則は変えない。
ここでは N=80 セルを「自分の verdict への最も重大な反証」として、同じ道具で叩く（数字の追加のみ・判定は本編のまま）。
  B1 細かい水平線 N ∈ {50..130 step 5} 外/在/近年（80 が尖っているか滑らかか）、単セル置換 p（N=80）と 60..120 格子の family-wise。
  B2 時代: 年別・半期別・LOYO（外）・2021-23／2024-26H1／2025-26H1、在の 2 分割。
  B3 lag 格子 k ∈ {−1,0,1,2,3,5,10}（N=80）。
  B4 側・金自身 g80 との混同: 側別、g80 向き内、層化 (side × g80 × 壁種)、ρ(Δ80, g80)。金自身 g80 × side の競合セル。
  B5 名目 DGS10 N=80 と 「実質−名目」（≒ −ブレークイーブン）N=80: 実質金利固有か金利全般か。
  B6 用量反応（N=80・外/近年）。
  B7 組成（outer 比率・b・risk・TP 率）追い風 vs 向かい風（外）。
入力・結合規則は本編と同一。seed 20261106。
"""
import os, time, math
import numpy as np, pandas as pd
from scipy.stats import spearmanr, binomtest

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c10_realrate60_b.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c10 b] 事後セル N=80 実質金利追い風 を叩く — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c10_realrate60_b.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
X["half"] = X["ts_jst"].dt.year.astype(str) + np.where(X["ts_jst"].dt.month <= 6, "H1", "H2")
X["month"] = X["ts_jst"].dt.to_period("M").astype(str)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); N = len(X)
BUY = SGN > 0; WK = X["wall_kind"].to_numpy(); YEAR = X["year"].to_numpy()
HOR = list(range(50, 135, 5)); H80 = HOR.index(80)
def load(sid):
    m = pd.read_csv(os.path.join(MAC, f"{sid}.csv")); m.columns = ["date", "v"]
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    v = m["v"].to_numpy(); D = np.full((len(HOR), len(v)), np.nan)
    for j, n in enumerate(HOR): D[j, n:] = v[n:] - v[:-n]
    return dict(d=m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), D=D, v=v)
MAC_D = {sid: load(sid) for sid in ("DFII10", "DGS10")}
# 実質−名目 系列（同日行を揃える）
a = pd.DataFrame({"d": MAC_D["DFII10"]["d"], "r": MAC_D["DFII10"]["v"]}); b = pd.DataFrame({"d": MAC_D["DGS10"]["d"], "n": MAC_D["DGS10"]["v"]})
j = a.merge(b, on="d"); v = (j["r"] - j["n"]).to_numpy(); D = np.full((len(HOR), len(v)), np.nan)
for jj, n in enumerate(HOR): D[jj, n:] = v[n:] - v[:-n]
MAC_D["REAL-NOM"] = dict(d=j["d"].to_numpy(), D=D, v=v)
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
def feats(sid, ref, shift=0, tol=10):
    d = MAC_D[sid]["d"]; i = np.searchsorted(d, ref, side="right") - 1; ok = (i >= 0) & ((ref - d[np.clip(i, 0, None)]) <= tol)
    i2 = i - shift; ok &= (i2 >= 0); i2 = np.clip(i2, 0, len(d) - 1); F = MAC_D[sid]["D"][:, i2].copy(); F[:, ~ok] = np.nan; return F
F_R = feats("DFII10", AVAIL); F_N = feats("DGS10", AVAIL); F_B = feats("REAL-NOM", AVAIL)
D80 = F_R[H80]

G = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); G["dt"] = pd.to_datetime(G["ts_last"], unit="s")
G = G[~G["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True); G["g80"] = G["lc"] - G["lc"].shift(80)
kn = G["known"].to_numpy(); te = X["te"].to_numpy(); gi = np.searchsorted(kn, te, side="right") - 1; gok = gi >= 0
g80 = np.full(N, np.nan); g80[gok] = G["g80"].to_numpy()[gi[gok]]; g80[gok & ((te - kn[np.clip(gi, 0, None)]) > 5 * 86400)] = np.nan

W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
def tstat(a, b):
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, (d / se if se > 0 else np.nan), se
def tail_of(delta, bull=-1):
    ok = np.isfinite(delta) & (delta != 0); return ok, ok & ((SGN * np.sign(delta) * bull) > 0)
def cell(delta, wm, bull=-1, ex=None):
    ok, tail = tail_of(delta, bull)
    if ex is not None: ok &= ex
    m = wm & ok; a = R[m & tail]; b = R[m & ~tail]; d, t, se = tstat(a, b); return dict(diff=d, t=t, se=se, n1=len(a), n0=len(b))
def fmt(r): return f"{r['diff']:+.4f} (t{r['t']:+.2f}, n{r['n1']}:{r['n0']})"

say("\n## B1 細かい水平線（実質金利・tail−head）")
for jj, n in enumerate(HOR):
    row = {wn: cell(F_R[jj], wm) for wn, wm in W.items()}
    say(f"- N={n:3d}: " + " / ".join(f"{wn} {r['diff']:+.4f} (t{r['t']:+.2f})" for wn, r in row.items()))
# permutation: week circular shift, fine grid 17 cells, OOS max|t| and single-cell N=80
lo = pd.Timestamp("2011-01-03"); hi = pd.Timestamp("2026-06-26"); span_w = (hi - lo).days // 7
lo_i = int(lo.to_datetime64().astype("datetime64[D]").astype(np.int64)); base_off = AVAIL - lo_i
NP = 1000; null_max = np.full(NP, np.nan); null_80 = np.full((NP, 3), np.nan); null_in80 = np.full(NP, np.nan); tp = time.time()
obs_max = max(abs(cell(F_R[jj], W["外2021-26"])["t"]) for jj in range(len(HOR))); obs80 = [cell(D80, wm)["t"] for wm in W.values()]
for p in range(NP):
    k = int(rng.integers(8, span_w - 8)); sh = lo_i + (base_off + 7 * k) % (span_w * 7); Fp = feats("DFII10", sh)
    ts = [cell(Fp[jj], W["外2021-26"])["t"] for jj in range(len(HOR))]; null_max[p] = np.nanmax(np.abs(ts))
    null_80[p] = [cell(Fp[H80], wm)["t"] for wm in W.values()]
say(f"- 置換（{NP} 回・{time.time()-tp:.0f} s）: 外 17 セル max|t| 観測 {obs_max:.2f} → 帰無 中央値 {np.median(null_max):.2f} 95%点 {np.quantile(null_max,0.95):.2f} 99%点 {np.quantile(null_max,0.99):.2f} **p {(null_max>=obs_max).mean():.3f}**")
say(f"- 単セル N=80: 外 t {obs80[1]:+.2f} p {(np.abs(null_80[:,1])>=abs(obs80[1])).mean():.3f}（帰無 sd {np.nanstd(null_80[:,1]):.2f}）／近年 t {obs80[2]:+.2f} p {(np.abs(null_80[:,2])>=abs(obs80[2])).mean():.3f}（sd {np.nanstd(null_80[:,2]):.2f}）／在 t {obs80[0]:+.2f}（帰無 sd {np.nanstd(null_80[:,0]):.2f}）")
say(f"- 外∧近年 同時: 帰無で min(t外,t近)≥{min(obs80[1],obs80[2]):.2f} の確率 {((null_80[:,1]>=min(obs80[1],obs80[2]))&(null_80[:,2]>=min(obs80[1],obs80[2]))).mean():.3f}（近年⊂外なので独立でない）")

say("\n## B2 時代（N=80）")
for wn, wm in {"2010-15": (YEAR >= 2010) & (YEAR <= 2015), "2016-20": (YEAR >= 2016) & (YEAR <= 2020), "2021-23": (YEAR >= 2021) & (YEAR <= 2023),
               "2024-26H1": YEAR >= 2024, "2025-26H1": YEAR >= 2025}.items(): say(f"- {wn}: {fmt(cell(D80, wm))}")
yr = [(y, cell(D80, YEAR == y)) for y in range(2010, 2027)]
say("- 年別: " + " ".join(f"{y}:{r['diff']:+.3f}(t{r['t']:+.1f})" for y, r in yr))
say(f"- 年別 正 在 {sum(1 for y,r in yr if y<=2020 and r['diff']>0)}/11・外 {sum(1 for y,r in yr if y>=2021 and r['diff']>0)}/6")
hv = [(h, cell(D80, (X['half'] == h).to_numpy())) for h in sorted(X["half"].unique()) if int(h[:4]) >= 2021 and h != "2026H2"]
say("- 外 半期別: " + " ".join(f"{h}:{r['diff']:+.3f}(t{r['t']:+.1f})" for h, r in hv) + f"  正 {sum(1 for _,r in hv if r['diff']>0)}/{len(hv)}")
loo = [(y, cell(D80, W["外2021-26"] & (YEAR != y))) for y in range(2021, 2027)]
say("- 外 LOYO: " + " ".join(f"-{y}:{r['diff']:+.3f}(t{r['t']:+.2f})" for y, r in loo))
n_out = W["外2021-26"].sum()
say("- 外 diff への年別寄与: " + " ".join(f"{y}:{r['diff']*(r['n1']+r['n0'])/n_out:+.4f}" for y, r in yr if y >= 2021))
# 追い風群の時代組成: 外で追い風/向かい風の年分布（実質金利 80d の向きは年単位で固まる）
ok, tail = tail_of(D80); mm = W["外2021-26"] & ok
say("- 外 年別 追い風比率（BUY∧金利低下 ∨ SELL∧金利上昇）: " + " ".join(f"{y}:{tail[mm&(YEAR==y)].mean():.2f}" for y in range(2021, 2027)))
say("- 外 年別 BUY 比率: " + " ".join(f"{y}:{BUY[W['外2021-26']&(YEAR==y)].mean():.2f}" for y in range(2021, 2027)))
say("- 外 年別 実質金利 Δ80 の符号 正比率（本加重）: " + " ".join(f"{y}:{(D80[mm&(YEAR==y)]>0).mean():.2f}" for y in range(2021, 2027)))

say("\n## B3 lag 格子（N=80）")
for k in (-1, 0, 1, 2, 3, 5, 10):
    Fk = feats("DFII10", AVAIL, shift=k); row = {wn: cell(Fk[H80], wm) for wn, wm in W.items()}
    say(f"- k={k:+d}: " + " / ".join(f"{wn} {r['diff']:+.4f} (t{r['t']:+.2f})" for wn, r in row.items()))

say("\n## B4 側・金自身 g80 との混同（N=80）")
m = np.isfinite(D80) & np.isfinite(g80); say(f"- ρ(Δ80 実質金利, g80 金) {np.corrcoef(D80[m], g80[m])[0,1]:+.3f}")
gok80, gt80 = tail_of(g80, +1)
for wn, wm in W.items():
    say(f"- {wn}: BUY {fmt(cell(D80, wm, ex=BUY))} / SELL {fmt(cell(D80, wm, ex=~BUY))} | 金追い風内(g80) {fmt(cell(D80, wm, ex=gok80&gt80))} / 金向かい風内 {fmt(cell(D80, wm, ex=gok80&~gt80))}")
    say(f"    競合 金自身 g80×side: {fmt(cell(g80, wm, bull=+1))} | 無条件 BUY−SELL {R[wm&BUY].mean()-R[wm&~BUY].mean():+.4f}")
    ok, tail = tail_of(D80); num = var = 0.0; ntot = 0
    for s in (True, False):
        for gt in (True, False):
            for wk in ("outer", "mid"):
                st = wm & ok & (BUY == s) & gok80 & (gt80 == gt) & (WK == wk); a = R[st & tail]; b = R[st & ~tail]
                if len(a) >= 5 and len(b) >= 5:
                    d, t, se = tstat(a, b); w = len(a) + len(b); num += d * w; var += (se * w) ** 2; ntot += w
    say(f"    層化 diff (side×g80×壁種) {num/ntot:+.4f} (t{num/ntot/(math.sqrt(var)/ntot):+.2f}, n{ntot})")

say("\n## B5 実質か名目か（N=80・tail−head）")
for nm, F, bull in (("実質 DFII10", F_R, -1), ("名目 DGS10", F_N, -1), ("実質−名目（≒−BEI）", F_B, -1)):
    say(f"- {nm}: " + " / ".join(f"{wn} {fmt(cell(F[H80], wm, bull))}" for wn, wm in W.items()))
# 実質と名目を同時に: 実質追い風 ∧ 名目逆 など 2×2（外）
okr, tr_ = tail_of(F_R[H80]); okn, tn_ = tail_of(F_N[H80]); wm = W["外2021-26"]
for a_, an in ((True, "実質追い風"), (False, "実質向かい風")):
    for b_, bn in ((True, "名目追い風"), (False, "名目向かい風")):
        s = wm & okr & okn & (tr_ == a_) & (tn_ == b_); say(f"  - 外 {an}∧{bn}: mean R {R[s].mean():+.4f} (n{s.sum()})")

say("\n## B6 用量反応（N=80）")
for wn, wm in W.items():
    ok = wm & np.isfinite(D80); sc = SGN[ok] * (-D80[ok]); rr = R[ok]; rho, pv = spearmanr(sc, rr)
    q = pd.qcut(sc, 5, labels=False, duplicates="drop"); means = pd.Series(rr).groupby(q).mean()
    say(f"- {wn}: ρ {rho:+.4f} (p {pv:.3f}) 五分位 " + " ".join(f"{v:+.3f}" for v in means))

say("\n## B7 組成（外・N=80）")
ok, tail = tail_of(D80); mm = W["外2021-26"] & ok
for nm, g in (("追い風", mm & tail), ("向かい風", mm & ~tail)):
    s = X[g]; say(f"- {nm}: n{len(s)} outer {np.mean(s.wall_kind=='outer'):.2f} b {s.b.mean():.3f} risk {s.risk.mean():.3f} TP率 {np.mean(s.exit=='TP'):.3f} BUY比 {np.mean(s.side=='BUY'):.2f} 上位10% 本数 {int((s.R>=np.quantile(R[mm],0.9)).sum())}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
