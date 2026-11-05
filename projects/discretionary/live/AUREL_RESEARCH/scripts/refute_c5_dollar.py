# -*- coding: utf-8 -*-
"""
[REFUTE] 2026-11-05 17:xx 反証レーン — 対象: cycle5 (15:50) が「自分の結論への最も重大な反証」として残した
「F2 広義ドル（DTWEXBGS）は 3 窓すべて負（在 −0.046 t−2.41／外 −0.023 t−0.86／近年 −0.016 t−0.42）
 ＝ 逆向き仮説『ドルの前日の動きと同方向の金の壁→壁は走りにくい（翌日反転）』の符号が揃っている」を潰す。

=== 事前固定（この docstring を書いてから数字を見る・結果を見てから Q を増やさない） ===
入力: data/refute_c4_scan_paths_2010_2026.json（19404 本）＋ data/macro/*.csv（cycle5 取得済み・再取得なし）。
結合規則は cycle5 と同一（FRED 日付 D は JST D+1 07:00 以降の建玉のみ・merge_asof backward・staleness ≤7 日）。
scan 無し・M5 読込なし・MT5 なし・外部通信なし。

Q0 再現: F2 DTWEXBGS の 在/外/近年 diff・t が cycle5 の md と一致すること（一致しなければ以降は無効）。

Q1 窓の重なりを解く: 近年 2024-26 は 外 2021-26 の部分集合 → 「3 窓負」は独立 2 窓。
   重ならない 3 窓 在 2010-20／2021-23／2024-26H1 の符号と t、2025-26H1、年別 diff（17 年）の符号数（二項）。
   予測（反証側）: 2021-23 と 2024-26 のどちらかは正、または年別符号は 二項 p>0.1。

Q2 多重検定（主検定・在側 family-wise）: cycle5 は 外 8 セルの max|t| だけ置換した（p 0.73）。在 t−2.41 は 8 セル×符号自由度の中の
   最大セル。日次特徴量の行を **年層内で日単位シャッフル**（2000 回）し、8 セル×3 窓の t を全部出す。
   S1 = 在 8 セル max|t|（観測 2.41）。S2 = 「在/外/近年 3 窓の符号が揃い、かつ |t_在|≥2.41」のセル数（観測 1）。
   S3 = 8 セルの max over cells of [3 窓同符号なら min(|t|) else 0]（観測 0.42）。
   判定: S1 の p ≥0.05 なら「在の t−2.41 は格子ノイズ」。

Q3 観測可能性（look-ahead・この系列固有）: DTWEXBGS は Fed H.10 の週次公表（翌週月曜）で、日 D の値は現実には 1〜5 営業日後に見える。
   cycle5 の lag 0（D+1 朝に見えると仮定）は代理の上限評価。lag k ∈ {0,1,2,3,4,5,7,10} 営業日前の Δ を同じ規則で貼り直し、
   F2 diff/t を 在/外/近年 で出す。k=5 が「月曜公表を待つ」保守値。さらに対照 k=−1（翌日の Δ＝建玉日を含む同時共変動・look-ahead なので
   仮説検定に使わない・感応の存在確認のみ）。
   判定: 観測可能な k≥1 で 外 t ≤−1.5 のものが無ければ「代理でも実際に使えない」。k=0 だけが大きく k≥1 で消えるなら
   「前日」固有の情報でなく、観測不能な値への当てはめ。

Q4 側の分解: aligned = (BUY & Δ$<0) ∪ (SELL & Δ$>0)。群の side 構成が違うと side の無条件差が漏れる。
   2×2（side × Δ$ 符号）の平均R と、側内差 BUY: (Δ$<0 − Δ$>0)／SELL: (Δ$>0 − Δ$<0) と n 加重の層化 diff・t。
   判定: 層化 diff の符号/サイズが素の diff と違えば「側の構成差」が混入。片側だけで出ていれば「ドル反転」でなく side×曜日型の別物。

Q5 用量反応: align_score = −Δ$ (BUY) / +Δ$ (SELL)（>0 が整合）。Spearman(align_score, R) と五分位平均R（在/外/近年）。
   反転が本物なら単調減少。判定: 在・外とも ρ<0 でなければ「符号だけで用量なし」。

Q6 レジーム部分集合（在のみ・効果が出ている窓・Bonferroni α=0.05/7）: wall_kind outer/mid、JST 帯 7-12/13-20/21-6、side BUY/SELL。
   leave-one-year-out（在 11 年）で t の範囲。判定: 1〜2 年を抜いて |t|<1.5 なら年依存。

Q7 コスト・戦略形: diff は「同じコストを払う 2 群の差」なのでコスト倍は不変（倍にしても diff は動かない）＝本件には適用不能と明記。
   使える形は「整合本を見送る」入口フィルタ（憲章 D で再発明禁止）なので採用提案はしない。記述として、上位10% 本のうち aligned の
   割合（見送ると尻尾の何割が消えるか）を窓別に出す。

Q8 改定（vintage）: FRED の DTWEXBGS は最新 vintage で、H.10 は改定される。実時点の値（ALFRED）は本環境に無い → needs data として記録。

判定規則（事前）:
  broken      = Q2 S1 の p ≥ 0.05 かつ（Q1 で 2021-23／2024-26 の符号が揃わない または Q3 の観測可能 k≥1 全部で 外 t > −1.5）。
  survived    = Q2 S1 の p < 0.05 かつ Q3 の k∈{1..5} のどれかで 外 t ≤ −1.5 かつ Q5 で 在・外 ρ<0。
  inconclusive= それ以外。
seed 20261105。
"""
import json, sys, time, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr, binomtest

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "refute_c5_dollar.md")
rng = np.random.default_rng(20261105)
lines = []
def say(s=""): print(s); lines.append(s)

# ---------- trades (cycle5 と同一) ----------
d = json.load(open(os.path.join(ROOT, "data", "refute_c4_scan_paths_2010_2026.json")))
tr = pd.DataFrame(d["trades"])
tr["ts_utc"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True)
tr["ts_jst"] = tr["ts_utc"].dt.tz_convert(None) + pd.Timedelta(hours=9)
tr["avail_date"] = (tr["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
tr["day"] = tr["ts_jst"].dt.normalize()
tr = tr.sort_values("avail_date").reset_index(drop=True)
say(f"# [REFUTE c5] F2 広義ドル 3 窓負 を潰す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c5_dollar.py)")
say(f"trades n={len(tr)}  R mean {tr.R.mean():+.4f}")

SERIES = {"DFII10": ("実質10y", -1), "DGS10": ("名目10y", -1), "DTWEXBGS": ("広義ドル(代理)", -1), "VIXCLS": ("VIX", +1)}
raw = {}
for sid in SERIES:
    m = pd.read_csv(os.path.join(ROOT, "data", "macro", f"{sid}.csv")); m.columns = ["date", "v"]
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m.dropna()
    m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    m["dv"] = m["v"].diff(); a = m["dv"].abs().to_numpy(); pct = np.full(len(a), np.nan)
    for i in range(len(a)):
        lo = max(0, i - 250); w = a[lo:i]; w = w[~np.isnan(w)]
        if len(w) >= 120 and not np.isnan(a[i]): pct[i] = (w < a[i]).mean()
    m["pct"] = pct
    raw[sid] = m

def attach(df, sid, lag=0):
    """lag 営業日（行）前の dv/pct を avail_date に貼る。lag<0 は将来（対照のみ）。"""
    m = raw[sid].copy()
    m["dv"] = m["dv"].shift(lag); m["pct"] = m["pct"].shift(lag)
    m = m[m["date"] >= "2009-01-01"][["date", "dv", "pct"]].rename(columns={"date": f"date_{sid}", "dv": f"dv_{sid}", "pct": f"pct_{sid}"})
    out = pd.merge_asof(df, m, left_on="avail_date", right_on=f"date_{sid}", direction="backward", tolerance=pd.Timedelta(days=7))
    return out

X = tr.copy()
for sid in SERIES: X = attach(X, sid, 0)

W = {"在2010-20": X.year <= 2020, "外2021-26": X.year >= 2021, "近年2024-26": X.year >= 2024}
W_extra = {"2021-23": (X.year >= 2021) & (X.year <= 2023), "2024-26H1": X.year >= 2024,
           "2025-26H1": X.year >= 2025}

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    diff = a.mean() - b.mean(); se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    return diff, diff/se if se > 0 else np.nan

def cluster_t(df, grp, val="R", cl="day"):
    a = df[grp]; b = df[~grp]
    if len(a) < 2 or len(b) < 2: return np.nan
    ma, mb = a[val].mean(), b[val].mean(); na, nb = len(a), len(b)
    ia = ((a[val] - ma) / na).groupby(a[cl]).sum(); ib = ((b[val] - mb) / nb).groupby(b[cl]).sum()
    inf = ia.sub(ib, fill_value=0.0); se = np.sqrt((inf**2).sum())
    return (ma - mb) / se if se > 0 else np.nan

def masks(df, sid, form):
    dv = df[f"dv_{sid}"]; pct = df[f"pct_{sid}"]; ok = dv.notna() & pct.notna()
    if form == "F1": return ok, pct >= 0.8
    bs = SERIES[sid][1]; bullish = np.sign(dv) == bs
    aligned = ((df.side == "BUY") & bullish) | ((df.side == "SELL") & ~bullish & (dv != 0))
    return ok & (dv != 0), aligned

def cell(df, sid, form, msk):
    ok, g = masks(df, sid, form); sub = df[msk & ok]; gg = g[msk & ok]
    diff, t = welch(sub.loc[gg, "R"], sub.loc[~gg, "R"]); return diff, t, int(gg.sum()), int((~gg).sum()), sub, gg

# ---------- Q0 ----------
say("\n## Q0 再現（cycle5: 在 −0.0461 t−2.41 / 外 −0.0229 t−0.86 / 近年 −0.0164 t−0.42）")
Q0 = {}
for wn, msk in W.items():
    diff, t, na, nb, sub, gg = cell(X, "DTWEXBGS", "F2", msk); tc = cluster_t(sub, gg)
    Q0[wn] = (diff, t); say(f"- {wn}: n={na}:{nb} diff {diff:+.4f} t {t:+.2f} (cl {tc:+.2f})")
repro = abs(Q0["在2010-20"][0] + 0.0461) < 0.001 and abs(Q0["在2010-20"][1] + 2.41) < 0.02
say(f"- 再現: {'OK' if repro else 'NG'}")

# ---------- Q1 ----------
say("\n## Q1 窓の重なりを解く（近年 ⊂ 外）・重ならない窓・年別")
for wn, msk in W_extra.items():
    diff, t, na, nb, sub, gg = cell(X, "DTWEXBGS", "F2", msk); say(f"- {wn}: n={na}:{nb} diff {diff:+.4f} t {t:+.2f}")
yr = []
for y in range(2010, 2027):
    diff, t, na, nb, _, _ = cell(X, "DTWEXBGS", "F2", X.year == y); yr.append((y, diff, t, na + nb))
neg = sum(1 for _, dd, _, _ in yr if dd < 0)
say("- 年別 diff: " + " ".join(f"{y}:{dd:+.3f}(t{t:+.1f})" for y, dd, t, n in yr))
say(f"- 年別 負 {neg}/{len(yr)}（二項両側 p {binomtest(neg, len(yr), 0.5).pvalue:.3f}）、|t|≥2 の年 {sum(1 for _,_,t,_ in yr if abs(t)>=2)}")
q1_indep_agree = (cell(X, "DTWEXBGS", "F2", W_extra["2021-23"])[0] < 0) and (cell(X, "DTWEXBGS", "F2", W_extra["2024-26H1"])[0] < 0)
say(f"- 重ならない 3 窓（在/2021-23/2024-26H1）の符号が全部負: {q1_indep_agree}")

# ---------- Q2 family-wise 置換（年層内・日単位・8 セル×3 窓） ----------
say("\n## Q2 主検定: 年層内の日単位シャッフル 2000 回・8 セル×3 窓")
cells = [(sid, f) for f in ("F1", "F2") for sid in SERIES]
obs = {}
for c in cells:
    obs[c] = tuple(cell(X, c[0], c[1], W[wn])[1] for wn in W)
feat_cols = [f"{p}_{sid}" for sid in SERIES for p in ("dv", "pct")]
# 置換単位は特徴量を定義するキー avail_date（JST 暦日ではない: JST 00-07 時の本は同じ暦日でも avail_date が 1 日違う）。
# cycle5 の置換は "day"(JST 暦日) を単位に first() で貼っており、同日内で特徴量が食い違う本が混ざる（帰無の形には軽微・観測値の再構成には不可）。
day_feats = X.groupby("avail_date")[feat_cols].first()
assert (X.groupby("avail_date")[feat_cols].nunique(dropna=False).max().max() <= 1), "avail_date 内で特徴量が一意でない"
day_year = pd.Series(day_feats.index.year, index=day_feats.index)
DF = day_feats.to_numpy(); fcol = {c: i for i, c in enumerate(feat_cols)}
day_idx = pd.factorize(X["avail_date"], sort=True)[0]
assert (day_feats.index[day_idx] == X["avail_date"].to_numpy()).all()
R = X["R"].to_numpy(); side_buy = (X["side"] == "BUY").to_numpy()
wmask = {wn: msk.to_numpy() for wn, msk in W.items()}
groups = [np.flatnonzero(day_year.to_numpy() == y) for y in np.unique(day_year)]

def tstat(ok, g, wm):
    a = R[wm & ok & g]; b = R[wm & ok & ~g]
    if len(a) < 2 or len(b) < 2: return np.nan
    se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b)); return (a.mean()-b.mean())/se if se > 0 else np.nan

def all_cells(F):
    out = np.empty((len(cells), 3))
    for j, (sid, f) in enumerate(cells):
        dv = F[:, fcol[f"dv_{sid}"]]; pct = F[:, fcol[f"pct_{sid}"]]; ok = ~np.isnan(dv) & ~np.isnan(pct)
        if f == "F1": g = pct >= 0.8
        else:
            bs = SERIES[sid][1]; bull = np.sign(dv) == bs
            g = (side_buy & bull) | (~side_buy & ~bull & (dv != 0)); ok = ok & (dv != 0)
        for k, wn in enumerate(W): out[j, k] = tstat(ok, g, wmask[wn])
    return out

def stats(T):
    tin, tout, trec = T[:, 0], T[:, 1], T[:, 2]
    S1 = np.nanmax(np.abs(tin))
    same = (np.sign(tin) == np.sign(tout)) & (np.sign(tin) == np.sign(trec))
    S2 = int(np.sum(same & (np.abs(tin) >= 2.41)))
    S3 = np.max(np.where(same, np.minimum(np.minimum(np.abs(tin), np.abs(tout)), np.abs(trec)), 0.0))
    return S1, S2, S3

Tobs = all_cells(DF[day_idx]); S1o, S2o, S3o = stats(Tobs)
# 再構成が直接計算と一致することを確認（一致しなければ置換の貼り方が壊れている）
direct = np.array([obs[c] for c in cells]); recon_err = np.nanmax(np.abs(Tobs - direct))
say(f"- 再構成 t と直接計算 t の最大差 {recon_err:.4f}（{'OK' if recon_err < 0.01 else 'NG'}）")
assert recon_err < 0.01, "置換用の再構成が観測を再現しない"
say(f"- 観測: S1 在 max|t| {S1o:.2f} / S2 3窓同符号∧|t在|≥2.41 のセル数 {S2o} / S3 同符号 min|t| の最大 {S3o:.2f}")
NPERM = 2000; null = np.empty((NPERM, 3))
for p in range(NPERM):
    perm = np.arange(len(DF))
    for gi in groups: perm[gi] = gi[rng.permutation(len(gi))]
    null[p] = stats(all_cells(DF[perm][day_idx]))
pS1 = (null[:, 0] >= S1o).mean(); pS2 = (null[:, 1] >= max(S2o, 1)).mean(); pS3 = (null[:, 2] >= S3o).mean()
say(f"- S1: 帰無 中央値 {np.median(null[:,0]):.2f} / 95%点 {np.quantile(null[:,0],0.95):.2f} → **p {pS1:.3f}**")
say(f"- S2: 帰無で ≥1 セル出る確率 **{pS2:.3f}**")
say(f"- S3: 帰無 中央値 {np.median(null[:,2]):.2f} / 95%点 {np.quantile(null[:,2],0.95):.2f} → **p {pS3:.3f}**")

# ---------- Q3 lag 格子 ----------
say("\n## Q3 観測可能性: DTWEXBGS を lag k 営業日前の Δ で貼り直す（k=0 は cycle5・現実には H.10 週次公表で 1〜5 営業日遅れ）")
Q3 = {}
for k in (-1, 0, 1, 2, 3, 4, 5, 7, 10):
    Xk = attach(tr.copy(), "DTWEXBGS", k)
    row = []
    for wn, msk in W.items():
        diff, t, na, nb, _, _ = cell(Xk, "DTWEXBGS", "F2", msk.to_numpy()); row.append((diff, t))
    Q3[k] = row
    tag = "（対照・翌日Δ＝建玉日込み・look-ahead・判定不使用）" if k < 0 else ("（cycle5）" if k == 0 else "")
    say(f"- k={k:+d}{tag}: " + " / ".join(f"{wn} {dd:+.4f} (t{t:+.2f})" for wn, (dd, t) in zip(W, row)))
obs_lags = [1, 2, 3, 4, 5]
q3_usable = any(Q3[k][1][1] <= -1.5 for k in obs_lags)
say(f"- 観測可能 k∈1..5 で 外 t ≤ −1.5 のものがある: {q3_usable}")
say(f"- 在 |diff| が k=0 で最大（k=0..5 の中）: {abs(Q3[0][0][0]) >= max(abs(Q3[k][0][0]) for k in range(0,6))}")

# ---------- Q4 側の分解 ----------
say("\n## Q4 側の分解（2×2・側内差・層化 diff）")
Q4 = {}
for wn, msk in W.items():
    ok, _ = masks(X, "DTWEXBGS", "F2"); sub = X[msk & ok]
    dn = sub[f"dv_DTWEXBGS"] < 0
    cells4 = {}
    for s in ("BUY", "SELL"):
        for lab, m2 in (("$↓", dn), ("$↑", ~dn)):
            r = sub.loc[(sub.side == s) & m2, "R"]; cells4[(s, lab)] = (r.mean(), len(r))
    b_d, b_t = welch(sub.loc[(sub.side == "BUY") & dn, "R"], sub.loc[(sub.side == "BUY") & ~dn, "R"])
    s_d, s_t = welch(sub.loc[(sub.side == "SELL") & ~dn, "R"], sub.loc[(sub.side == "SELL") & dn, "R"])
    nB = (sub.side == "BUY").sum(); nS = (sub.side == "SELL").sum()
    strat = (b_d * nB + s_d * nS) / (nB + nS)
    # 層化 t: 側内差を独立として合成
    seB = b_d / b_t if b_t else np.nan; seS = s_d / s_t if s_t else np.nan
    se_strat = np.sqrt((nB/(nB+nS))**2 * seB**2 + (nS/(nB+nS))**2 * seS**2); t_strat = strat / se_strat
    sideR = sub.groupby("side")["R"].mean()
    al_share_buy = ((sub.side == "BUY") & dn).sum() / (((sub.side == "BUY") & dn).sum() + ((sub.side == "SELL") & ~dn).sum())
    op_share_buy = ((sub.side == "BUY") & ~dn).sum() / (((sub.side == "BUY") & ~dn).sum() + ((sub.side == "SELL") & dn).sum())
    Q4[wn] = (b_d, b_t, s_d, s_t, strat, t_strat)
    say(f"- {wn}: " + " ".join(f"{s}×{l} {v[0]:+.3f}(n{v[1]})" for (s, l), v in cells4.items())
        + f" | side 無条件 BUY {sideR.get('BUY', np.nan):+.3f} SELL {sideR.get('SELL', np.nan):+.3f}"
        + f" | aligned 群の BUY 比 {al_share_buy:.2f} vs opposed {op_share_buy:.2f}")
    say(f"    側内差 BUY($↓−$↑) {b_d:+.4f} (t{b_t:+.2f}) / SELL($↑−$↓) {s_d:+.4f} (t{s_t:+.2f}) / 層化 diff {strat:+.4f} (t{t_strat:+.2f})")

# ---------- Q5 用量反応 ----------
say("\n## Q5 用量反応: align_score = −Δ$ (BUY) / +Δ$ (SELL)、Spearman と五分位")
Q5 = {}
for wn, msk in W.items():
    ok, _ = masks(X, "DTWEXBGS", "F2"); sub = X[msk & ok]
    sc = np.where(sub.side == "BUY", -sub["dv_DTWEXBGS"], sub["dv_DTWEXBGS"])
    rho, pv = spearmanr(sc, sub["R"]); q = pd.qcut(sc, 5, labels=False, duplicates="drop")
    means = pd.Series(sub["R"].to_numpy()).groupby(q).mean()
    Q5[wn] = rho
    say(f"- {wn}: ρ {rho:+.4f} (p {pv:.3f}) 五分位（整合弱→強） " + " ".join(f"{m:+.3f}" for m in means))
    # 整合の大きさ上位 20% vs 逆行の大きさ上位 20%
    hi = sc >= np.quantile(sc, 0.8); lo = sc <= np.quantile(sc, 0.2)
    dd, tt = welch(sub.loc[hi, "R"], sub.loc[lo, "R"]); say(f"    強い整合(上位20%) − 強い逆行(下位20%): {dd:+.4f} (t{tt:+.2f})")

# ---------- Q6 レジーム（在） ----------
say("\n## Q6 レジーム部分集合（在 2010-20・Bonferroni α=0.05/7）と leave-one-year-out")
msk_in = W["在2010-20"]
subsets = {"outer": X.wall_kind == "outer", "mid": X.wall_kind == "mid",
           "JST7-12": X.jh.between(7, 12), "JST13-20": X.jh.between(13, 20), "JST21-6": ~X.jh.between(7, 20),
           "BUY": X.side == "BUY", "SELL": X.side == "SELL"}
from scipy.stats import norm
nsig = 0
for nm, m2 in subsets.items():
    diff, t, na, nb, _, _ = cell(X, "DTWEXBGS", "F2", msk_in & m2); p = 2 * (1 - norm.cdf(abs(t))) if not np.isnan(t) else np.nan
    sig = p < 0.05 / 7; nsig += sig
    say(f"- {nm}: n={na}:{nb} diff {diff:+.4f} t {t:+.2f} p {p:.4f}{' **Bonf 有意**' if sig else ''}")
say(f"- Bonferroni 有意 {nsig}/7")
loo = []
for y in range(2010, 2021):
    diff, t, _, _, _, _ = cell(X, "DTWEXBGS", "F2", msk_in & (X.year != y)); loo.append((y, diff, t))
say("- leave-one-year-out 在: " + " ".join(f"-{y}:{dd:+.3f}(t{t:+.2f})" for y, dd, t in loo))
say(f"  t の範囲 [{min(t for _,_,t in loo):+.2f}, {max(t for _,_,t in loo):+.2f}]")
# 在の effect の年別寄与（diff×n／総 n）
tot_n = sum(n for y, _, _, n in yr if y <= 2020)
say("- 在 diff への年別寄与（diff_y × n_y / n_在）: " + " ".join(f"{y}:{dd*n/tot_n:+.4f}" for y, dd, t, n in yr if y <= 2020))

# ---------- Q7 コスト・戦略形 ----------
say("\n## Q7 コスト・戦略形（記述のみ・入口フィルタは採用提案しない）")
say("- diff は同じコストを払う 2 群の差 → コスト倍は diff に不変（適用不能）。")
for wn, msk in W.items():
    ok, g = masks(X, "DTWEXBGS", "F2"); sub = X[msk & ok]; gg = g[msk & ok]
    thr = sub["R"].quantile(0.9); top = sub["R"] >= thr
    say(f"- {wn}: aligned 比率 {gg.mean():.3f} / 上位10% 本のうち aligned {gg[top].mean():.3f} / 上位10% 合計R のうち aligned 分 {sub.loc[top & gg,'R'].sum()/sub.loc[top,'R'].sum():.3f}"
        f" / 見送った場合の全本平均R 変化 {(sub.loc[~gg,'R'].mean() - sub['R'].mean()):+.4f}（本数 −{gg.mean()*100:.0f}%）")

# ---------- verdict ----------
say("\n## 判定（事前規則）")
broken = (pS1 >= 0.05) and ((not q1_indep_agree) or (not q3_usable))
survived = (pS1 < 0.05) and q3_usable and (Q5["在2010-20"] < 0) and (Q5["外2021-26"] < 0)
verdict = "broken" if broken else ("survived" if survived else "inconclusive")
say(f"- Q2 S1 p {pS1:.3f} ({'≥' if pS1>=0.05 else '<'}0.05) / Q1 重ならない窓の符号一致 {q1_indep_agree} / Q3 観測可能 lag で 外 t≤−1.5 {q3_usable} / Q5 ρ 在 {Q5['在2010-20']:+.4f} 外 {Q5['外2021-26']:+.4f}")
say(f"- **{verdict}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
