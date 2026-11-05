# -*- coding: utf-8 -*-
"""
[cycle5 研究レーン] 2026-11-05 — 【探索→即検証】公開日次マクロ系列（米実質金利/米名目金利/広義ドル/VIX）は
再加速（壁→壁）の翌日成績を条件づけるか（DIRECTIVE タスク3・DATA_MAP §6 を【要取得】→【実験可】へ）

=== 事前固定（この docstring を書いてから数字を見る） ===
問い: 金の構造的ドライバー（実質金利=保有機会費用・ドル=建値通貨・VIX=リスク回避）の「前日の動き」は、
      翌日の再加速 setup の平均R を条件づけるか。相関でなく「建玉時点で知り得た値」で予測に使えるかを在/外で見る。
      入口フィルタの再発明ではない（条件づけの有無＝レジーム記述。採用提案はしない）。

データ:
  - 再加速 closed 19404 本: data/refute_c4_scan_paths_2010_2026.json（entry_time=UTC epoch, R gross, side, year）。
    R の ft 非対称は全セルに同一に乗るので、部分集合の差の比較には影響しない（絶対水準は使わない=D2）。
  - FRED 日次 CSV（本サイクルで取得・data/macro/*.csv）: DFII10（10y 実質）, DGS10（10y 名目）, DTWEXBGS（広義ドル）, VIXCLS。
  - 利用可能時刻の規則（5条）: FRED 日付 D の値は NY 17:00 ET 以降に確定 → **JST D+1 07:00 以降の建玉だけ**が D の値を使える。
    avail_date = (entry_JST − 7h).date() − 1 日、merge_asof backward（休日は直前営業日・staleness ≤7 日）。
    注意: DTWEXBGS は Fed H.10 公表に数日の遅れ（FRED 最終行が 10-30）＝厳密には当日観測不能。市場で見える DXY の代理として扱い、
    結果は「代理」と明記する。

特徴量（系列 s・日 D）: Δ_s(D) = v(D) − v(直前営業日)。|Δ| の過去 250 営業日内パーセンタイル（当日を含まない）→ Q5 = 上位 20%。
  F1 マクロ・ショック regime: 「前日 |Δ| が過去1年の上位20%」の本 vs それ以外。予測: diff(Q5 − 他) > 0
      （マクロの大きな動き → 翌日トレンド継続 → 壁→壁が走る）。
  F2 方向整合: 金に強気な前日の動き = Δ実質金利<0 / Δ名目<0 / Δドル<0 / ΔVIX>0。
      aligned = (BUY & 強気) or (SELL & 弱気)。予測: diff(aligned − opposed) > 0（マクロの向きが翌日に持ち越す）。
  → 4 系列 × 2 形 = 8 セル（事前に固定・増やさない）。

窓: 在 = 2010-2020 / 外 = 2021-2026H1 / D2 近年 = 2024-2026H1（参考・edge 水準は近年窓でのみ語る）。
統計: diff・Welch t（iid）・日クラスタ robust t（同日の本はマクロ値を共有）。
  family-wise: 日ラベル置換（日次特徴量の行を日単位でシャッフルして本に貼り直す・2000 回）で 外の 8 セル max|t| の帰無分布 → p_max。
合否（セル単位）: 在 t≥2 で予測方向 ∧ 外 同符号 t≥1.5 ∧ family-wise p_max<0.05。1 セルでも PASS なら「条件づけあり」。
  それ以外 = null（「条件づけなし」または「検出できない」）。
ベースライン: 各窓の無条件平均R。F1 は五分位の単調性（Spearman）も記述。
事前の最重要反証: (1) 日次マクロの「前日の動き」は M5 の壁→壁の時間尺度（数時間）より粗く、情報が薄いのは当然 → null は
  「日次粒度では」の限定つき。(2) 8 セルの格子で 1 つ拾うのは多重検定 → 置換 p_max で補正。(3) DTWEXBGS の公表遅延。
昇格候補ではない（レジーム記述・DATA_MAP 更新が主目的）。seed 20261105。
"""
import json, sys, time, os
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "c5_macro_condition_result.md")
rng = np.random.default_rng(20261105)
lines = []
def say(s=""): print(s); lines.append(s)

# ---------- trades ----------
d = json.load(open(os.path.join(ROOT, "data", "refute_c4_scan_paths_2010_2026.json")))
tr = pd.DataFrame(d["trades"])
tr["ts_utc"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True)
tr["ts_jst"] = tr["ts_utc"].dt.tz_convert(None) + pd.Timedelta(hours=9)
tr["avail_date"] = (tr["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
tr["day"] = tr["ts_jst"].dt.normalize()
tr = tr.sort_values("avail_date").reset_index(drop=True)
say(f"# [cycle5] マクロ条件づけ — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c5_macro_condition.py)")
say(f"trades n={len(tr)} {tr.ts_jst.min()} .. {tr.ts_jst.max()} JST  R mean {tr.R.mean():+.4f}")

# ---------- macro ----------
SERIES = {"DFII10": ("実質10y", -1), "DGS10": ("名目10y", -1), "DTWEXBGS": ("広義ドル(代理)", -1), "VIXCLS": ("VIX", +1)}
# bullish_sign: 金に強気な Δ の符号（-1: 下落が強気, +1: 上昇が強気）
feats = {}
for sid, (lab, bs) in SERIES.items():
    m = pd.read_csv(os.path.join(ROOT, "data", "macro", f"{sid}.csv"))
    m.columns = ["date", "v"]
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m.dropna()
    m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    m["dv"] = m["v"].diff(); m["adv"] = m["dv"].abs()
    a = m["adv"].to_numpy(); pct = np.full(len(a), np.nan)
    for i in range(len(a)):
        lo = max(0, i - 250); w = a[lo:i]; w = w[~np.isnan(w)]
        if len(w) >= 120 and not np.isnan(a[i]): pct[i] = (w < a[i]).mean()
    m["pct"] = pct
    m = m[m["date"] >= "2009-01-01"]
    feats[sid] = m[["date", "v", "dv", "pct"]].rename(columns={"v": f"v_{sid}", "dv": f"dv_{sid}", "pct": f"pct_{sid}"})

X = tr.copy()
for sid, m in feats.items():
    X = pd.merge_asof(X, m.rename(columns={"date": f"date_{sid}"}), left_on="avail_date", right_on=f"date_{sid}",
                      direction="backward", tolerance=pd.Timedelta(days=7))
    X[f"stale_{sid}"] = (X["avail_date"] - X[f"date_{sid}"]).dt.days
say("\n## 0. 結合（利用可能時刻の規則: FRED 日付 D は JST D+1 07:00 以降の本のみ）")
for sid in SERIES:
    ok = X[f"dv_{sid}"].notna() & X[f"pct_{sid}"].notna()
    say(f"- {sid}: 特徴量あり {ok.mean()*100:.1f}% (n={ok.sum()}), staleness 日 中央値 {X.loc[ok, f'stale_{sid}'].median():.0f} / max {X.loc[ok, f'stale_{sid}'].max():.0f}")

# ---------- windows ----------
W = {"在2010-20": X.year <= 2020, "外2021-26": X.year >= 2021, "近年2024-26": X.year >= 2024}
say("\n## 1. ベースライン（無条件平均R・gross・ft 非対称込み＝水準は edge に使わない）")
for wn, msk in W.items():
    r = X.loc[msk, "R"]; say(f"- {wn}: n={len(r)} mean {r.mean():+.4f} sd {r.std():.3f}")

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    diff = a.mean() - b.mean(); se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    return diff, diff/se if se > 0 else np.nan

def cluster_t(df, grp, val="R", cl="day"):
    """差の平均 (grp==True) − (grp==False) の日クラスタ robust t"""
    a = df[grp]; b = df[~grp]
    if len(a) < 2 or len(b) < 2: return np.nan
    ma, mb = a[val].mean(), b[val].mean(); na, nb = len(a), len(b)
    ia = ((a[val] - ma) / na).groupby(a[cl]).sum(); ib = ((b[val] - mb) / nb).groupby(b[cl]).sum()
    inf = ia.sub(ib, fill_value=0.0)
    se = np.sqrt((inf**2).sum())
    return (ma - mb) / se if se > 0 else np.nan

# ---------- cells ----------
def cell_masks(df, sid, form):
    dv = df[f"dv_{sid}"]; pct = df[f"pct_{sid}"]; ok = dv.notna() & pct.notna()
    if form == "F1":
        g = pct >= 0.8; return ok, g
    bs = SERIES[sid][1]
    bullish = np.sign(dv) == bs
    aligned = ((df.side == "BUY") & bullish) | ((df.side == "SELL") & ~bullish & (dv != 0))
    ok = ok & (dv != 0)
    return ok, aligned

cells = [(sid, f) for f in ("F1", "F2") for sid in SERIES]
say("\n## 2. 8 セル（diff = 条件群 − 対照群・予測 >0）")
res = {}
for sid, f in cells:
    row = {}
    for wn, msk in W.items():
        ok, g = cell_masks(X, sid, f); sub = X[msk & ok]; gg = g[msk & ok]
        diff, t = welch(sub.loc[gg, "R"], sub.loc[~gg, "R"]); tc = cluster_t(sub, gg)
        row[wn] = (diff, t, tc, int(gg.sum()), int((~gg).sum()))
    res[(sid, f)] = row
    lab = SERIES[sid][0]
    s = f"- **{f} {sid}({lab})**: " + " / ".join(
        f"{wn} n={v[3]}:{v[4]} diff {v[0]:+.4f} t {v[1]:+.2f} (cl {v[2]:+.2f})" for wn, v in row.items())
    say(s)

# F1 五分位の単調性（記述）
say("\n## 3. F1 五分位（|Δ| の過去1年パーセンタイル）別 平均R・Spearman（記述・判定不使用）")
from scipy.stats import spearmanr
for sid in SERIES:
    for wn in ("在2010-20", "外2021-26"):
        sub = X[W[wn] & X[f"pct_{sid}"].notna()]
        q = np.minimum((sub[f"pct_{sid}"] * 5).astype(int), 4)
        means = sub.groupby(q)["R"].mean().reindex(range(5))
        rho = spearmanr(q, sub["R"]).correlation
        say(f"- {sid} {wn}: Q1..Q5 " + " ".join(f"{m:+.3f}" for m in means) + f"  Spearman ρ {rho:+.4f}")

# ---------- family-wise permutation (day-level shuffle of macro features) ----------
say("\n## 4. family-wise 置換（日次特徴量の行を日単位でシャッフル・外窓・8 セル max|t|・2000 回）")
NPERM = 2000
oos = X[W["外2021-26"]].copy()
days = oos["day"].unique()
feat_cols = [c for c in oos.columns if c.startswith(("dv_", "pct_"))]
day_feats = oos.groupby("day")[feat_cols].first()  # 同日の本は同じ特徴量（avail_date が同じ）
obs_t = np.array([res[c]["外2021-26"][1] for c in cells]); obs_max = np.nanmax(np.abs(obs_t))
null_max = np.empty(NPERM); null_cell = np.empty((NPERM, len(cells)))
R = oos["R"].to_numpy(); side = oos["side"].to_numpy(); day_idx = pd.factorize(oos["day"])[0]
DF = day_feats.to_numpy(); fcol = {c: i for i, c in enumerate(feat_cols)}
def tstat(mask_ok, g):
    a = R[mask_ok & g]; b = R[mask_ok & ~g]
    if len(a) < 2 or len(b) < 2: return np.nan
    se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b)); return (a.mean()-b.mean())/se if se > 0 else np.nan
for p in range(NPERM):
    perm = rng.permutation(len(DF)); F = DF[perm][day_idx]
    for j, (sid, f) in enumerate(cells):
        dv = F[:, fcol[f"dv_{sid}"]]; pct = F[:, fcol[f"pct_{sid}"]]; ok = ~np.isnan(dv) & ~np.isnan(pct)
        if f == "F1": g = pct >= 0.8
        else:
            bs = SERIES[sid][1]; bull = np.sign(dv) == bs
            g = ((side == "BUY") & bull) | ((side == "SELL") & ~bull & (dv != 0)); ok = ok & (dv != 0)
        null_cell[p, j] = tstat(ok, g)
    null_max[p] = np.nanmax(np.abs(null_cell[p]))
p_max = (null_max >= obs_max).mean()
say(f"- 観測 外 max|t| {obs_max:.2f} → 帰無 中央値 {np.median(null_max):.2f} / 95%点 {np.quantile(null_max,0.95):.2f} / **p_max {p_max:.3f}**")
for j, c in enumerate(cells):
    pj = (np.abs(null_cell[:, j]) >= abs(obs_t[j])).mean()
    say(f"  - {c[1]} {c[0]}: 外 t {obs_t[j]:+.2f} 単セル置換 p {pj:.3f}")

# ---------- verdict ----------
say("\n## 5. 判定（事前規則: 在 t≥2 予測方向 ∧ 外 同符号 t≥1.5 ∧ p_max<0.05）")
npass = 0
for c in cells:
    r_in = res[c]["在2010-20"]; r_out = res[c]["外2021-26"]
    ok = (r_in[1] >= 2.0) and (r_out[1] >= 1.5) and (p_max < 0.05)
    npass += ok
    say(f"- {c[1]} {c[0]}: 在 t {r_in[1]:+.2f} / 外 t {r_out[1]:+.2f} / p_max {p_max:.3f} → {'PASS' if ok else 'FAIL'}")
say(f"\n**PASS {npass}/8 → {'条件づけあり' if npass else 'null（日次マクロの前日の動きは翌日の再加速 R を条件づけない／検出できない）'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
