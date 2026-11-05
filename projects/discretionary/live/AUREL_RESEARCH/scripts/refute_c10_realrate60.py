# -*- coding: utf-8 -*-
"""
[REFUTE] 2026-11-06 08:xx 反証レーン — 対象: cycle10 (06:50) が「自分の結論への最も重大な反証」として残した
  (A) 実質金利 DFII10 Δ60（60 営業日）追い風: 外 +0.053 (t2.00, 月cl 1.72)・近年 +0.062 (t1.57)・在 −0.010 (t−0.52)
      ＝「配分フローは遅い」仮説は 20d より 60d を予測していたとも言える
  (B) 事後 2×2: 金向かい風内（金自身 20d と逆）のマクロ追い風 外/近年 +0.05〜0.10（ドル 近年 +0.096 t1.52）
  復活条件（cycle10）: 新データで 1 セル「F_T DFII10 60d diff>0（外 t≥1.5）」と「金向かい風内のドル追い風>0」を Bonferroni(2)。
  → 反証レーンは新データを待たず、既存データで (A)(B) が選択効果・時代効果・look-ahead・組成で説明できるかを先に全部掃く。

=== 事前固定（この docstring を書いてから数字を見る・結果を見てから Q を増やさない） ===
入力: data/c8_crossasset_features.csv（19404 本・cycle10 と同一）＋ data/macro/{DFII10,DTWEXBGS,DGS10}.csv ＋ data/macro/XAU_daily_er.csv。
結合規則は cycle10 と同一（avail = (JST−7h).date − 1 日・asof backward・staleness ≤10 暦日・DTWEXBGS は −7 暦日・金自身は known ≤ te・土日擬似日除外）。
scan 無し・M5 原本読込なし・MT5 なし・外部通信なし。

Q0 再現: DFII10 Δ60 の 在/外/近年 diff・t が cycle10 の md と ±0.001/±0.02 で一致、2×2 ドル 近年 金向かい風内 +0.0955 (t1.52) も一致。
   一致しなければ以降は無効。

Q1 水平線掃引（選択効果）: N ∈ {5,10,20,40,60,80,100,120,180,250} 営業日 × {DFII10, DTWEXBGS} の tail−head diff/t を 在/外/近年 で出す。
   60d が孤立した山なら選択効果、滑らかな同符号なら構造。在/外の符号一致を N ごとに見る。

Q2 family-wise 置換（主検定）: cycle10 が外窓で**記述した**マクロ系セル 15（主 2＋複製 5＋2×2 4＋側別 4）を同時に、
   参照日 avail を k 週 循環シフト（cycle10 §5 と同機構・1000 回・金自身の層は固定）して
   S1 = 外 15 セル max|t|（観測は Δ60 の 2.00 のはず）、S2 = 近年 15 セル max|t|（観測は 2×2 ドル 1.52 のはず）、
   S3 = 水平線 20 セル（Q1）の外 max|t|、S4 = 「外 t≥1.5 ∧ 近年 同符号 t≥1.5」を満たす記述セル数（観測 1: Δ60）。
   判定: S1 p ≥0.05 なら「Δ60 外 t2.00 は記述格子のノイズ」。

Q3 別分割・時代: 重ならない窓 2021-23／2024-26H1／2025-26H1、年別 diff 17 年の符号（二項）、半期別、外 LOYO（6 年）の t 範囲、
   在の 2 分割 2010-15／2016-20。判定: 在→外で符号が反転し外の年別正が 2021-26 で 4/6 以下なら「時代で符号が変わる型」。

Q4 look-ahead / 公表遅延: DFII10 Δ60 を lag k ∈ {−1, 0, 1, 2, 3, 5, 10} 行（営業日）前の値で貼り直す（k=0 が cycle10。
   Treasury の実質利回りは D 16:15 ET ≒ JST D+1 06:15 公表で cycle10 の JST D+1 07:00 はぎりぎり。k=1 が安全側）。
   k=−1 は建玉日込みの look-ahead 対照（判定不使用）。判定: k=0 だけ大きく k≥1 で 外 t<1.5 なら「観測時刻への当てはめ」。

Q5 側・金自身との混同: Δ60 実質金利は金自身の 60d トレンドと負相関（cycle10 ρ(Δ20,g20) −0.44）。
   (i) 側別 BUY/SELL の追い風効果（外/近年）、(ii) 金自身 g60 の向き内（金追い風内／金向かい風内）での Δ60 効果、
   (iii) 層化（side × g60 向き × 壁種）diff。判定: 層化で t<1.5 または片側だけなら「金自身のトレンド・側の構成が混入」。

Q6 用量反応: score = sgn(side)·(−Δ60)（>0 が追い風）。Spearman(score, R)・五分位・強追い風上位20% − 強向かい風下位20%（外/近年）。
   判定: 外で ρ≤0 または五分位が単調でなければ「符号だけで用量なし」。

Q7 レジーム部分集合（外・Bonferroni α=0.05/5）: outer/mid、JST 7-12/13-20/21-6。年別寄与（diff_y·n_y/n_外）。

Q8 コスト・戦略形（記述のみ）: diff は両群同コストなので倍にしても不変（適用不能と明記）。「向かい風を見送る」は入口フィルタ＝補遺 D 禁止。
   記述として 上位10% 本のうち向かい風の割合（見送ると尻尾の何割が消えるか）外/近年。

Q9 2×2 セル (B): 金向かい風内マクロ追い風を g20 と g60 の両方で、在/外/近年、DFII10/DTWEXBGS。Q2 の S2 が family-wise p。
   在で |t|<1 なら在→外の再現なし。

判定規則（事前）:
  broken      = Q2 S1 p ≥ 0.05 かつ 在 Δ60 t < 1.0（在で立たない）
  survived    = Q2 S1 p < 0.05 かつ 在 Δ60 t ≥ 1.0 同符号 かつ Q4 の k∈{1,2,3} 全部で 外 t ≥ 1.5 かつ Q6 外 ρ > 0
  inconclusive= それ以外
  (B) は別判定: broken_B = Q2 S2 p ≥ 0.05 かつ 在の同セル |t| < 1.0。
seed 20261106。
"""
import os, time, math
import numpy as np, pandas as pd
from scipy.stats import spearmanr, binomtest, norm

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c10_realrate60.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)

say(f"# [REFUTE c10] 実質金利 Δ60 追い風・2×2 金向かい風内 を潰す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c10_realrate60.py)")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
X["day"] = X["ts_jst"].dt.normalize(); X["month"] = X["ts_jst"].dt.to_period("M").astype(str)
X["half"] = X["ts_jst"].dt.year.astype(str) + np.where(X["ts_jst"].dt.month <= 6, "H1", "H2")
X["sgn"] = np.where(X["side"] == "BUY", 1.0, -1.0)
R = X["R"].to_numpy(); SGN = X["sgn"].to_numpy(); N = len(X)
say(f"- trades n={N} {X.ts_jst.min()}..{X.ts_jst.max()} JST")

HORIZONS = [5, 10, 20, 40, 60, 80, 100, 120, 180, 250]
SERIES = {"DFII10": 0, "DTWEXBGS": 7, "DGS10": 0}  # publication lag (calendar days) as in cycle10
def rpct(a, win=500, minp=250):
    out = np.full(len(a), np.nan)
    for i in range(len(a)):
        w = a[max(0, i - win):i]; w = w[~np.isnan(w)]
        if len(w) >= minp and not np.isnan(a[i]): out[i] = (w < a[i]).mean()
    return out
MAC_D = {}
for sid in SERIES:
    m = pd.read_csv(os.path.join(MAC, f"{sid}.csv")); m.columns = ["date", "v"]
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m.dropna().copy()
    m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    v = m["v"].to_numpy(); D = np.full((len(HORIZONS), len(v)), np.nan)
    for j, n in enumerate(HORIZONS): D[j, n:] = v[n:] - v[:-n]
    p20 = rpct(np.abs(D[HORIZONS.index(20)]))
    MAC_D[sid] = dict(d=m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), D=D, p20=p20)
    say(f"- {sid}: 営業日行 {len(v)} {m.date.min().date()}..{m.date.max().date()}")

def asof_idx(sid, ref_days, tol=10):
    d = MAC_D[sid]["d"]; i = np.searchsorted(d, ref_days, side="right") - 1
    ok = (i >= 0); ok &= (ref_days - d[np.clip(i, 0, None)]) <= tol
    return i, ok
def feats(sid, ref_days, row_shift=0):
    """全水平線の Δ（行列 H×N）と p20。row_shift>0: k 営業日前の値（lag 格子）。"""
    i, ok = asof_idx(sid, ref_days); i2 = i - row_shift
    ok &= (i2 >= 0) & (i2 < len(MAC_D[sid]["d"]))
    i2c = np.clip(i2, 0, len(MAC_D[sid]["d"]) - 1)
    F = MAC_D[sid]["D"][:, i2c]; F[:, ~ok] = np.nan
    P = MAC_D[sid]["p20"][i2c].copy(); P[~ok] = np.nan
    return F, P
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
REF = {sid: AVAIL - lag for sid, lag in SERIES.items()}
FE = {sid: feats(sid, REF[sid]) for sid in SERIES}

# gold own trend (competitor strata), identical to cycle10
G = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv"))
G["dt"] = pd.to_datetime(G["ts_last"], unit="s"); G = G[~G["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
G["g20"] = G["lc"] - G["lc"].shift(20); G["g60"] = G["lc"] - G["lc"].shift(60)
kn = G["known"].to_numpy(); te = X["te"].to_numpy(); gi = np.searchsorted(kn, te, side="right") - 1; gok = gi >= 0
GOLD = {}
for c in ("g20", "g60"):
    v = G[c].to_numpy(); o = np.full(N, np.nan); o[gok] = v[gi[gok]]; o[gok & ((te - kn[np.clip(gi, 0, None)]) > 5 * 86400)] = np.nan; GOLD[c] = o
say(f"- 金自身 g20/g60 付与 {np.isfinite(GOLD['g20']).mean()*100:.1f}% / {np.isfinite(GOLD['g60']).mean()*100:.1f}%")

W = {"在2010-20": (X.year <= 2020).to_numpy(), "外2021-26": (X.year >= 2021).to_numpy(), "近年2024-26": (X.year >= 2024).to_numpy()}
WX = {"2010-15": ((X.year >= 2010) & (X.year <= 2015)).to_numpy(), "2016-20": ((X.year >= 2016) & (X.year <= 2020)).to_numpy(),
      "2021-23": ((X.year >= 2021) & (X.year <= 2023)).to_numpy(), "2024-26H1": (X.year >= 2024).to_numpy(), "2025-26H1": (X.year >= 2025).to_numpy()}

def tstat(a, b):
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, (d / se if se > 0 else np.nan), se
def cl_t(Rv, grp, g, d):
    a, b = g, ~g
    if a.sum() < 2 or b.sum() < 2: return np.nan
    inf = np.where(a, (Rv - Rv[a].mean()) / a.sum(), 0.0) - np.where(b, (Rv - Rv[b].mean()) / b.sum(), 0.0)
    s = pd.Series(inf).groupby(grp).sum(); se = math.sqrt((s ** 2).sum()); return d / se if se > 0 else np.nan
def tail_of(delta, bull_sign=-1):
    ok = np.isfinite(delta) & (delta != 0); tail = ok & ((SGN * np.sign(delta) * bull_sign) > 0); return ok, tail
def cell(delta, wm, bull_sign=-1, extra_ok=None, clusters=False):
    ok, tail = tail_of(delta, bull_sign)
    if extra_ok is not None: ok = ok & extra_ok
    m = wm & ok; a = R[m & tail]; b = R[m & ~tail]; d, t, se = tstat(a, b)
    out = dict(diff=d, t=t, se=se, n1=len(a), n0=len(b))
    if clusters and m.sum() > 3:
        out["tcm"] = cl_t(R[m], X["month"].to_numpy()[m], tail[m], d); out["tcd"] = cl_t(R[m], X["day"].to_numpy()[m], tail[m], d)
    return out
def fmt(r): return f"{r['diff']:+.4f} (t{r['t']:+.2f}, n{r['n1']}:{r['n0']})"

H60 = HORIZONS.index(60); H20 = HORIZONS.index(20)
D60 = FE["DFII10"][0][H60]; D20 = FE["DFII10"][0][H20]; U20 = FE["DTWEXBGS"][0][H20]; U60 = FE["DTWEXBGS"][0][H60]

# ---------------- Q0 ----------------
say("\n## Q0 再現（cycle10: Δ60 在 −0.0100 t−0.52 / 外 +0.0533 t+2.00 月cl 1.72 / 近年 +0.0620 t+1.57; 2×2 ドル 近年 金向かい風内 +0.0955 t1.52）")
Q0 = {}
for wn, wm in W.items():
    r = cell(D60, wm, clusters=True); Q0[wn] = r
    say(f"- Δ60 {wn}: {fmt(r)} 日cl {r['tcd']:+.2f} 月cl {r['tcm']:+.2f}")
gok20, gtail20 = tail_of(GOLD["g20"], +1)
r22 = cell(U20, W["近年2024-26"], extra_ok=gok20 & ~gtail20)
say(f"- 2×2 ドル Δ20 近年 金向かい風内(g20): {fmt(r22)}")
repro = abs(Q0["外2021-26"]["diff"] - 0.0533) < 0.001 and abs(Q0["外2021-26"]["t"] - 2.00) < 0.02 and abs(Q0["在2010-20"]["diff"] + 0.0100) < 0.001 \
    and abs(r22["diff"] - 0.0955) < 0.001
say(f"- 再現: {'OK' if repro else 'NG'}")
assert repro, "cycle10 の数字を再現できない"

# ---------------- Q1 horizon sweep ----------------
say("\n## Q1 水平線掃引（tail−head・予測 >0）N 営業日 × 系列・在/外/近年")
Q1 = {}
for sid in ("DFII10", "DTWEXBGS"):
    say(f"- {sid}:")
    for j, n in enumerate(HORIZONS):
        row = {wn: cell(FE[sid][0][j], wm) for wn, wm in W.items()}; Q1[(sid, n)] = row
        agree = np.sign(row["在2010-20"]["diff"]) == np.sign(row["外2021-26"]["diff"])
        say(f"  - N={n:3d}: " + " / ".join(f"{wn} {r['diff']:+.4f} (t{r['t']:+.2f})" for wn, r in row.items()) + f"  在外同符号 {agree}")
nin_pos = sum(1 for n in HORIZONS if Q1[("DFII10", n)]["在2010-20"]["t"] >= 1.0)
nout15 = sum(1 for n in HORIZONS if Q1[("DFII10", n)]["外2021-26"]["t"] >= 1.5)
say(f"- DFII10: 在 t≥1.0 の水平線 {nin_pos}/10、外 t≥1.5 の水平線 {nout15}/10（60 が孤立か滑らかか）")

# ---------------- Q2 family-wise permutation ----------------
say("\n## Q2 family-wise 置換（参照日 k 週 循環シフト・1000 回・金自身の層は固定）")
BUY = (X.side == "BUY").to_numpy(); SELL = ~BUY
gok60, gtail60 = tail_of(GOLD["g60"], +1)
def described_cells(F):
    """cycle10 が外窓で記述したマクロ系 15 セル（主2・複製5・2×2 4・側別4）の t を 3 窓で返す (15×3)。F: dict sid->(Δ行列, p20)。"""
    d20r, p20r = F["DFII10"][0][H20], F["DFII10"][1]; d60r = F["DFII10"][0][H60]
    d20u, p20u = F["DTWEXBGS"][0][H20], F["DTWEXBGS"][1]; d60u = F["DTWEXBGS"][0][H60]; d20n = F["DGS10"][0][H20]
    specs = [("主 DFII10 20d", d20r, None), ("主 DTWEXBGS 20d", d20u, None), ("DGS10 20d", d20n, None), ("DFII10 60d", d60r, None),
             ("DTWEXBGS 60d", d60u, None), ("DFII10 20d 強", d20r, p20r >= 2 / 3), ("DTWEXBGS 20d 強", d20u, p20u >= 2 / 3),
             ("DFII10 20d 金追い風内", d20r, gok20 & gtail20), ("DFII10 20d 金向かい風内", d20r, gok20 & ~gtail20),
             ("DTWEXBGS 20d 金追い風内", d20u, gok20 & gtail20), ("DTWEXBGS 20d 金向かい風内", d20u, gok20 & ~gtail20),
             ("DFII10 20d BUY", d20r, BUY), ("DFII10 20d SELL", d20r, SELL), ("DTWEXBGS 20d BUY", d20u, BUY), ("DTWEXBGS 20d SELL", d20u, SELL)]
    T = np.full((len(specs), 3), np.nan)
    for i, (nm, dl, ex) in enumerate(specs):
        for k, (wn, wm) in enumerate(W.items()): T[i, k] = cell(dl, wm, extra_ok=ex)["t"]
    return [s[0] for s in specs], T
def horizon_cells(F):
    T = np.full((20, 3), np.nan); i = 0
    for sid in ("DFII10", "DTWEXBGS"):
        for j in range(len(HORIZONS)):
            for k, (wn, wm) in enumerate(W.items()): T[i, k] = cell(F[sid][0][j], wm)["t"]
            i += 1
    return T
def stats(Td, Th):
    S1 = np.nanmax(np.abs(Td[:, 1])); S2 = np.nanmax(np.abs(Td[:, 2])); S3 = np.nanmax(np.abs(Th[:, 1]))
    S4 = int(np.sum((Td[:, 1] >= 1.5) & (Td[:, 2] >= 1.5)) + np.sum((Td[:, 1] <= -1.5) & (Td[:, 2] <= -1.5)))
    return S1, S2, S3, S4
names, Td_obs = described_cells(FE); Th_obs = horizon_cells(FE); So = stats(Td_obs, Th_obs)
say("- 記述 15 セルの観測 t（在/外/近年）:")
for nm, row in zip(names, Td_obs): say(f"  - {nm}: {row[0]:+.2f} / {row[1]:+.2f} / {row[2]:+.2f}")
say(f"- 観測: S1 外 max|t| {So[0]:.2f} / S2 近年 max|t| {So[1]:.2f} / S3 水平線20 外 max|t| {So[2]:.2f} / S4 外∧近年 同符号 t≥1.5 セル数 {So[3]}")
NPERM = 1000
lo = pd.Timestamp("2011-01-03"); hi = pd.Timestamp("2026-06-26"); span_w = (hi - lo).days // 7
lo_i = int(lo.to_datetime64().astype("datetime64[D]").astype(np.int64)); base_off = AVAIL - lo_i
null = np.full((NPERM, 4), np.nan); null_d60 = np.full((NPERM, 3), np.nan); tp = time.time()
for p in range(NPERM):
    k = int(rng.integers(8, span_w - 8)); shifted = lo_i + (base_off + 7 * k) % (span_w * 7)
    Fp = {sid: feats(sid, shifted - lag) for sid, lag in SERIES.items()}
    Td = described_cells(Fp); Th = horizon_cells(Fp); null[p] = stats(Td[1], Th); null_d60[p] = Td[1][3]
    if time.time() - tp > 400: say(f"!! 置換 {p+1} 回で時間上限"); null = null[:p + 1]; null_d60 = null_d60[:p + 1]; break
pS = [(null[:, i] >= So[i]).mean() for i in range(3)] + [(null[:, 3] >= max(So[3], 1)).mean()]
say(f"- S1 外 15 セル max|t|: 帰無 中央値 {np.median(null[:,0]):.2f} 95%点 {np.quantile(null[:,0],0.95):.2f} → **p {pS[0]:.3f}**")
say(f"- S2 近年 15 セル max|t|: 帰無 中央値 {np.median(null[:,1]):.2f} 95%点 {np.quantile(null[:,1],0.95):.2f} → **p {pS[1]:.3f}**")
say(f"- S3 水平線 20 セル 外 max|t|: 帰無 中央値 {np.median(null[:,2]):.2f} 95%点 {np.quantile(null[:,2],0.95):.2f} → **p {pS[2]:.3f}**")
say(f"- S4 外∧近年 同符号 t≥1.5 のセルが ≥1 出る確率: **{pS[3]:.3f}**")
p1_out = (np.abs(null_d60[:, 1]) >= abs(Td_obs[3, 1])).mean(); p1_rec = (np.abs(null_d60[:, 2]) >= abs(Td_obs[3, 2])).mean()
say(f"- 単セル Δ60: 外 t {Td_obs[3,1]:+.2f} 置換 p {p1_out:.3f}（帰無 sd {np.nanstd(null_d60[:,1]):.2f}）／近年 t {Td_obs[3,2]:+.2f} p {p1_rec:.3f}（sd {np.nanstd(null_d60[:,2]):.2f}）"
    f"／在 帰無 sd {np.nanstd(null_d60[:,0]):.2f}（{len(null)} 回・{time.time()-tp:.0f} s）")
# 複製 5 セルだけの family（cycle10 が「複製」と呼んだ集合）
rep_idx = [2, 3, 4, 5, 6]
null_rep = np.full(len(null), np.nan)
say(f"- 参考: 複製 5 セルのみの 外 max|t| 観測 {np.nanmax(np.abs(Td_obs[rep_idx,1])):.2f}（帰無は 15 セル版より狭い＝p はこれより小さい）")

# ---------------- Q3 splits / era ----------------
say("\n## Q3 別分割・時代（Δ60 DFII10）")
for wn, wm in WX.items(): say(f"- {wn}: {fmt(cell(D60, wm))}")
yr = []
for y in range(2010, 2027):
    r = cell(D60, (X.year == y).to_numpy()); yr.append((y, r["diff"], r["t"], r["n1"] + r["n0"]))
say("- 年別: " + " ".join(f"{y}:{d:+.3f}(t{t:+.1f})" for y, d, t, n in yr))
pos_all = sum(1 for _, d, _, _ in yr if d > 0); pos_out = sum(1 for y, d, _, _ in yr if y >= 2021 and d > 0)
say(f"- 年別 正 {pos_all}/17（二項 p {binomtest(pos_all, 17, 0.5).pvalue:.3f}）、外 2021-26 正 {pos_out}/6、在 正 {pos_all-pos_out}/11")
hv = []
for h in sorted(X["half"].unique()):
    if int(h[:4]) >= 2021:
        r = cell(D60, (X["half"] == h).to_numpy()); hv.append((h, r["diff"], r["t"]))
say("- 外 半期別: " + " ".join(f"{h}:{d:+.3f}(t{t:+.1f})" for h, d, t in hv))
loo = []
for y in range(2021, 2027):
    r = cell(D60, W["外2021-26"] & (X.year != y).to_numpy()); loo.append((y, r["diff"], r["t"]))
say("- 外 LOYO: " + " ".join(f"-{y}:{d:+.3f}(t{t:+.2f})" for y, d, t in loo) + f"  t 範囲 [{min(t for *_, t in loo):+.2f}, {max(t for *_, t in loo):+.2f}]")
n_out = W["外2021-26"].sum()
say("- 外 diff への年別寄与（diff_y·n_y/n_外）: " + " ".join(f"{y}:{d*n/n_out:+.4f}" for y, d, t, n in yr if y >= 2021))
era_flip = (Q0["在2010-20"]["diff"] < 0 < Q0["外2021-26"]["diff"]) and pos_out <= 4

# ---------------- Q4 lag grid ----------------
say("\n## Q4 look-ahead / 公表遅延: DFII10 Δ60 を k 営業日前の値で（k=0 cycle10・k=−1 は look-ahead 対照）")
Q4 = {}
for k in (-1, 0, 1, 2, 3, 5, 10):
    Fk, _ = feats("DFII10", REF["DFII10"], row_shift=k); dk = Fk[H60]
    row = {wn: cell(dk, wm) for wn, wm in W.items()}; Q4[k] = row
    tag = "（look-ahead 対照・判定不使用）" if k < 0 else ("（cycle10）" if k == 0 else "")
    say(f"- k={k:+d}{tag}: " + " / ".join(f"{wn} {r['diff']:+.4f} (t{r['t']:+.2f})" for wn, r in row.items()))
lag_ok = all(Q4[k]["外2021-26"]["t"] >= 1.5 for k in (1, 2, 3))
say(f"- 観測可能 k∈{{1,2,3}} 全部で 外 t≥1.5: {lag_ok}")

# ---------------- Q5 side / gold confound ----------------
say("\n## Q5 側・金自身 60d トレンドとの混同（Δ60 DFII10）")
m = np.isfinite(D60) & np.isfinite(GOLD["g60"])
say(f"- ρ(Δ60 実質金利, g60 金) {np.corrcoef(D60[m], GOLD['g60'][m])[0,1]:+.3f}")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    wm = W[wn]
    rb = cell(D60, wm, extra_ok=BUY); rs = cell(D60, wm, extra_ok=SELL)
    rgt = cell(D60, wm, extra_ok=gok60 & gtail60); rgh = cell(D60, wm, extra_ok=gok60 & ~gtail60)
    say(f"- {wn}: BUY {fmt(rb)} / SELL {fmt(rs)} | 金追い風内(g60) {fmt(rgt)} / 金向かい風内 {fmt(rgh)}")
    # unconditional side gap and side composition of tail vs head
    ok, tail = tail_of(D60); mm = wm & ok
    say(f"    無条件 BUY−SELL {R[wm&BUY].mean()-R[wm&SELL].mean():+.4f} | 追い風群 BUY 比 {BUY[mm&tail].mean():.2f} vs 向かい風群 {BUY[mm&~tail].mean():.2f}"
        f" | 追い風群 金追い風(g60) 比 {gtail60[mm&tail].mean():.2f} vs 向かい風群 {gtail60[mm&~tail].mean():.2f}")
# stratified diff: side × g60 dir × wall_kind
say("- 層化 diff（side × g60 向き × 壁種・層内差の n 加重）:")
WK = X["wall_kind"].to_numpy()
Q5 = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    wm = W[wn]; ok, tail = tail_of(D60); num = 0.0; var = 0.0; ntot = 0
    for s in (True, False):
        for gt in (True, False):
            for wk in ("outer", "mid"):
                st = wm & ok & (BUY == s) & gok60 & (gtail60 == gt) & (WK == wk)
                a = R[st & tail]; b = R[st & ~tail]
                if len(a) >= 5 and len(b) >= 5:
                    d, t, se = tstat(a, b); w = len(a) + len(b); num += d * w; var += (se * w) ** 2; ntot += w
    Q5[wn] = (num / ntot, num / ntot / (math.sqrt(var) / ntot))
    say(f"  - {wn}: 層化 diff {Q5[wn][0]:+.4f} (t{Q5[wn][1]:+.2f}, n{ntot})")

# ---------------- Q6 dose-response ----------------
say("\n## Q6 用量反応: score = sgn(side)·(−Δ60)（>0 追い風）")
Q6 = {}
for wn, wm in W.items():
    ok = wm & np.isfinite(D60); sc = SGN[ok] * (-D60[ok]); rr = R[ok]
    rho, pv = spearmanr(sc, rr); q = pd.qcut(sc, 5, labels=False, duplicates="drop"); means = pd.Series(rr).groupby(q).mean()
    hi_ = sc >= np.quantile(sc, 0.8); lo_ = sc <= np.quantile(sc, 0.2); d, t, _ = tstat(rr[hi_], rr[lo_]); Q6[wn] = rho
    say(f"- {wn}: ρ {rho:+.4f} (p {pv:.3f}) 五分位（向かい風強→追い風強）" + " ".join(f"{v:+.3f}" for v in means) + f" | 上位20%−下位20% {d:+.4f} (t{t:+.2f})")

# ---------------- Q7 regime subsets (OOS) ----------------
say("\n## Q7 レジーム部分集合（外・Bonferroni α=0.05/5）")
JH = X["jh"].to_numpy()
subsets = {"outer": WK == "outer", "mid": WK == "mid", "JST7-12": (JH >= 7) & (JH <= 12), "JST13-20": (JH >= 13) & (JH <= 20), "JST21-6": (JH >= 21) | (JH <= 6)}
nsig = 0
for nm, m2 in subsets.items():
    r = cell(D60, W["外2021-26"] & m2); pv = 2 * (1 - norm.cdf(abs(r["t"]))); sig = pv < 0.05 / 5; nsig += sig
    say(f"- {nm}: {fmt(r)} p {pv:.4f}{' **Bonf 有意**' if sig else ''}")
say(f"- Bonferroni 有意 {nsig}/5")

# ---------------- Q8 cost / strategy form ----------------
say("\n## Q8 コスト・戦略形（記述のみ・入口フィルタは提案しない）")
say("- diff は同コストの 2 群の差 → コスト倍は不変（適用不能）。")
for wn in ("外2021-26", "近年2024-26"):
    wm = W[wn]; ok, tail = tail_of(D60); mm = wm & ok; thr = np.quantile(R[mm], 0.9); top = mm & (R >= thr)
    say(f"- {wn}: 向かい風比率 {(~tail[mm]).mean():.3f} / 上位10% 本のうち向かい風 {(~tail[top]).mean():.3f} / 上位10% 合計R のうち向かい風分 {R[top&~tail].sum()/R[top].sum():.3f}"
        f" / 見送った場合の平均R 変化 {R[mm&tail].mean()-R[mm].mean():+.4f}（本数 −{(~tail[mm]).mean()*100:.0f}%）")

# ---------------- Q9 2×2 (B) ----------------
say("\n## Q9 (B) 金向かい風内のマクロ追い風（g20 と g60・在/外/近年・Δ20）")
Q9 = {}
for sid, dl in (("DFII10", D20), ("DTWEXBGS", U20)):
    for gname, (gk, gt) in (("g20", (gok20, gtail20)), ("g60", (gok60, gtail60))):
        row = {wn: cell(dl, wm, extra_ok=gk & ~gt) for wn, wm in W.items()}; Q9[(sid, gname)] = row
        say(f"- {sid} 金向かい風内({gname}): " + " / ".join(f"{wn} {fmt(r)}" for wn, r in row.items()))
tB_in = Q9[("DTWEXBGS", "g20")]["在2010-20"]["t"]

# ---------------- verdict ----------------
say("\n## 判定（事前規則）")
t_in = Q0["在2010-20"]["t"]
broken = (pS[0] >= 0.05) and (t_in < 1.0)
survived = (pS[0] < 0.05) and (t_in >= 1.0) and lag_ok and (Q6["外2021-26"] > 0)
verdict = "broken" if broken else ("survived" if survived else "inconclusive")
say(f"- (A) Δ60: S1 p {pS[0]:.3f} / 在 t {t_in:+.2f} / lag k1-3 外 t≥1.5 {lag_ok} / 外 ρ {Q6['外2021-26']:+.4f} / 時代反転型 {era_flip} → **{verdict}**")
broken_B = (pS[1] >= 0.05) and (abs(tB_in) < 1.0)
say(f"- (B) 2×2 ドル 金向かい風内: S2 p {pS[1]:.3f} / 在 t {tB_in:+.2f} → **{'broken' if broken_B else 'inconclusive'}**")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
