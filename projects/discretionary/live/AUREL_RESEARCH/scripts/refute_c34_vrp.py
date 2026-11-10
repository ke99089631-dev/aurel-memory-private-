# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-11 02:15] 対象: cycle34 (00:55) 金のボラ・リスクプレミアム（H_VRP PASS・H_PRED null・ゲート ㉛ 不通過）の残存弱信号
  W1 知識 (1)「金にも正の VRP がある: GVZ は次 21 日 RV を 在 +2.51／外 +2.12 vol pt 上回る（NW t 8.9／4.7・日の 83〜86%・16/17 年）、
      在では株式 VRP（+2.3）と同じ大きさ」（判定 H_VRP PASS・vol pt 単位・分散単位は併記のみ）
  W2 知識 (4)「壁→壁 scan はほぼボラ中立（β(R on VS_21d) 在 +0.0046R/pt t 1.87・外 +0.0019 t 0.58）＝ scan の負の期待値 −0.058R のうち
      保険料で説明できるのは β×VRP ≈ 0.012R（≤20%）」（補足 b・21 日前向き RV で露出を測っている）
  W3 知識 (2)「GVZ は効率的なボラ予測（外で trailing RV を完全に包含・γ≈0・R² 0.53）」（陽性対照 ②）
  W4 「2026H1 −2.2 pt＝保険の売り手が払った半年」・「近年 +1.23（MDE 1.79）」（年別・記述）

=== 事前固定（この docstring を書いてから数字を見る） ===
入力: data/macro/XAU_m5_close.npz・XAU_m5_ohlc.npz（bid・読取のみ）・GVZCLS.csv・VIXCLS.csv・US500_m5_close.npz・refute_c4_scan_paths_2010_2026.json。
  scan 無し・MT5 無し・外部通信無し。セッション日・RV・整列・窓・NW(21) は c34 と同じ定義で再現（R0: 在 +2.51 t 8.91／外 +2.12 t 4.74 が ±0.01 で一致すること）。
R0 再現: H_VRP の 3 窓（vol pt・cc・分散単位）を再計算し c34 の表と一致を確認。
R1 (W1 単位・Jensen): vol pt の VRP = mean(IV) − mean(RVf) は、分散整合の vol 差 Δσ = sqrt(mean IV²) − sqrt(mean RVf²) と Jensen 項
      [ (sqrt(mean RVf²) − mean RVf) − (sqrt(mean IV²) − mean IV) ] に分解できる（RV の散らばりが IV より大きいほど vol pt の VRP は膨らむ）。
      3 窓で Δσ・Jensen 項・比 Δσ/VRP を印字。株式（US500×VIX）も同じ分解。
      規則: 在・外とも Δσ/VRP ≥ 0.75 → W1 の大きさ survived。在 or 外で Δσ/VRP < 0.5 → 「vol pt の大きさは Jensen で過大」= W1 の大きさ broken（符号は別）。他 inconclusive。
      「株と同じ大きさ」は分散単位 (IV²−RV²)/100 の 在 比 金/株 を印字（規則なし・記述）。
R2 (W1 有効 n・別分割): 年別平均（分散単位・vol pt）の年クラスタ t（在 11 年・外 6 年・等重み）、leave-one-year-out の外の最小値、
      独立 4 窓 2010-14／2015-20／2021-23／2024-26H1、偶数年／奇数年。
      規則（分散単位）: 在 t_year ≥2 ∧ 外 t_year ≥1.5 ∧ 4 窓すべて >0 → survived。外 t_year <1.5 or 4 窓のどれかが ≤0 → 「外の分散単位の PASS は年の少なさに依存」= inconclusive。
R3 (W1 レジーム部分集合): 在で切った GVZ 三分位（固定カット）・RV_trail 三分位で VRP（vol pt・分散単位・NW t）を在/外で印字。
      規則: GVZ top 三分位の分散単位 VRP が 在・外とも ≤0 → 「プレミアムは静穏レジームの現象（高 IV では売り手が払う）」と記す（W1 の読みの限定・broken ではない）。
R4 (W1 検定の校正・プラセボ): GVZ を年内 21 日ブロックでシャッフルした系列（水準は保つ・整列は壊す）で H_VRP の規則（在 t≥2 ∧ 外 t≥1.5）を 200 回適用し通過率を印字。
      期待: ≈100% 通過＝H_VRP の PASS は「IV の水準が RV より高い」以上の情報（予測の整列）を含まない（規則の校正・W1 を壊すものではない・記述）。
      同時に陽性対照 ② の β(RVf on GVZ_shuffled | RVt) の分布を印字（整列が壊れると β→0 になること＝対照 ② が整列の検定として機能している確認）。
R5 (W3 包含): log 指定の HAR 包含回帰 log RVf = a + β log GVZ + γ1 log RV1 + γ5 log RV5 + γ21 log RV21（NW 21）を 在/外/近年で印字。
      規則: 在・外とも HAR 成分のどれかが同符号で |t|≥2 → 「完全に包含（γ≈0）」broken。在・外とも全成分 |t|<2 → survived。他 inconclusive。
R6 (W2 地平の不一致・主): scan は最長 288 本（1 日）しか持たないのに、露出は 21 日前向き RV で測られている。
      (a) 分散単位で再計算: VSv21 = (RVf² − IV²)/100 → β_v21（日クラスタ t）・予算 = β_v21 × mean(VSv21 | 在 trades)。
      (b) 建玉セッション日（1 日・24h・季節性なし）の RV1 を年率化: VSv1 = (RV1² − IV²)/100 → β_v1・予算 = β_v1 × mean(VSv1 | 在 trades)。
      (c) 記述: 実際の保有窓（entry〜exit 足・ohlc close・年率化）の RVh: VSvh = (RVh² − IV²)/100 → β_vh・予算（時刻の季節性を含むので記述）。
      (d) 非線形: 在 trades の VSv1 十分位別 R̄・x̄（凸性の有無）。側別 6 セルの Bonferroni(6) 名目 p。
      規則: (b) の在の予算 ≤ −0.029R（= −0.058R の 50% 以上）∧ β_v1 t≥2 → W2「≤20%」broken。
            (a)(b) とも |予算| ≤ 0.015R → survived。他 inconclusive。外・近年は確認として印字。
R7 (W4 2026H1・近年): 2026 の有効日数と前向き窓の到達月（npz 終端 2026-06-30 → 5 月末まで）を印字、分散単位の 2026 と近年の値、
      近年窓の「分散単位 ≈0」の年別分解。規則なし（記述）。
多重検定: 判定は R1・R2・R5・R6 の 4 標的（Bonferroni(4) 名目 |t| 閾値 2.50 を併記）。R3・R4・R7 は記述。look-ahead: GVZ 日付 D は
  セッション日 D（18:00 ET D−1 〜 18:00 ET D）内の 16:15 ET 確定・前向き窓は D+1 から（c34 と同じ・コードで D と D+1 の境界を印字して確認）。
survivorship: GVZ 欠損日（NYSE 休日）112 日の RV 平均を印字（除外された日が低ボラなら VRP は保守側）。D2: 窓別・16 年一括は使わず。seed 20261111。
コスト倍: 取引不能（オプション無し）のため該当なし（明記）。
書き込み: data/refute_c34_vrp.md・data/refute_c34_vrp_run.log のみ。
"""
import os, time, json
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c34_vrp.md")
NY = "America/New_York"; H = 21
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [refute c34] 金 VRP の反証 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c34_vrp.py)")
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

# ---------- c34 と同じセッション日次 ----------
def session_daily(npz, min_nf=100):
    z = np.load(os.path.join(MAC, npz)); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY); sess = dt_ny + pd.Timedelta(hours=6)
    S = sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy()
    df = pd.DataFrame({"s": S, "r2": r ** 2, "nf": (~flat).astype(np.int32), "lc": lc})
    g = df.groupby("s", sort=True)
    D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum(), "lc": g["lc"].last()})
    D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d"); D["wd"] = D["date"].dt.weekday
    D = D[(D["wd"] <= 4) & (D["nf"] >= min_nf)].reset_index(drop=True); D["rcc2"] = D["lc"].diff() ** 2
    return D, ts, C, dt_ny, S

def add_windows(D):
    n = len(D); rv = D["rv"].to_numpy(); rcc = np.nan_to_num(D["rcc2"].to_numpy())
    cs = np.concatenate([[0.0], np.cumsum(rv)]); cc = np.concatenate([[0.0], np.cumsum(rcc)])
    ann = lambda x, h: 100 * np.sqrt(np.maximum(252.0 / h * x, 0))
    i = np.arange(n); okf = i + H < n; okt = i - H + 1 >= 0
    for col, arr in (("RVf", None), ("RVt", None), ("RVfcc", None), ("RVtcc", None), ("RV1", None), ("RV5", None)):
        D[col] = np.nan
    D.loc[okf, "RVf"] = ann(cs[i[okf] + H + 1] - cs[i[okf] + 1], H); D.loc[okf, "RVfcc"] = ann(cc[i[okf] + H + 1] - cc[i[okf] + 1], H)
    D.loc[okt, "RVt"] = ann(cs[i[okt] + 1] - cs[i[okt] - H + 1], H); D.loc[okt, "RVtcc"] = ann(cc[i[okt] + 1] - cc[i[okt] - H + 1], H)
    D["RV1"] = ann(rv, 1); ok5 = i - 4 >= 0; D.loc[ok5, "RV5"] = ann(cs[i[ok5] + 1] - cs[i[ok5] - 4], 5)
    return D

def fred(name):
    f = pd.read_csv(os.path.join(MAC, name), na_values="."); f.columns = ["date", "v"]; f["date"] = pd.to_datetime(f["date"]); return f.dropna()

def nw_mean(x, lag=H):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; n = len(x); m = x.mean(); u = x - m; s = (u ** 2).sum() / n
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); s += 2 * w * (u[l:] * u[:-l]).sum() / n
    se = np.sqrt(s / n); return m, se, m / se, n

def nw_ols(y, X, lag=H):
    y = np.asarray(y, float); X = np.atleast_2d(np.asarray(X, float)); X = X.T if X.shape[0] != len(y) else X
    ok = ~np.isnan(y) & ~np.isnan(X).any(1); y = y[ok]; X = X[ok]; n = len(y)
    Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z); b = XtX_inv @ Z.T @ y; u = y - Z @ b
    S = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv; se = np.sqrt(np.diag(V)); r2 = 1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, se, b / se, n, r2

def win_mask(D, w):
    y0, y1 = WIN[w]; yr = D["date"].dt.year.to_numpy(); return (yr >= y0) & (yr <= y1)

say("\n## 0. データ・整列")
XD, ts, C, dt_ny, S = session_daily("XAU_m5_close.npz"); XD = add_windows(XD)
GV = fred("GVZCLS.csv"); VX = fred("VIXCLS.csv")
XD = XD.merge(GV.rename(columns={"v": "IV"}), on="date", how="left")
XD["VRP"] = XD["IV"] - XD["RVf"]; XD["VRPcc"] = XD["IV"] - XD["RVfcc"]; XD["VRPvar"] = (XD["IV"] ** 2 - XD["RVf"] ** 2) / 100.0
# 整列の確認: セッション日 D の ET 境界
d0 = XD["date"].iloc[1000]; s0 = int(d0.strftime("%Y%m%d")); m0 = S == s0
say(f"- セッション日 {d0.date()} の足 ET 範囲: {dt_ny[m0][0]} 〜 {dt_ny[m0][-1]}（GVZ 16:15 ET 確定はこの中・前向き窓は次セッションから）")
miss = XD["IV"].isna() & XD["RVf"].notna() & (XD["date"].dt.year >= 2010)
say(f"- XAU 有効日 {len(XD)}・GVZ 欠損日（2010+・NYSE 休日）{miss.sum()} 日: その日の RV1 平均 {XD.loc[miss,'RV1'].mean():.1f}% vs 全体 {XD.loc[XD['date'].dt.year>=2010,'RV1'].mean():.1f}%")
SD, *_ = session_daily("US500_m5_close.npz"); SD = add_windows(SD); SD = SD[SD["date"].dt.year >= 2014].reset_index(drop=True)
SD = SD.merge(VX.rename(columns={"v": "IV"}), on="date", how="left"); SD["VRP"] = SD["IV"] - SD["RVf"]; SD["VRPvar"] = (SD["IV"] ** 2 - SD["RVf"] ** 2) / 100.0

# ---------- R0 ----------
say("\n## R0 再現（c34 表 1）")
for w in WIN:
    d = XD[win_mask(XD, w) & XD["VRP"].notna()]
    mu, se, t, n = nw_mean(d["VRP"]); mc, _, tc, _ = nw_mean(d["VRPcc"]); mv, _, tv, _ = nw_mean(d["VRPvar"])
    say(f"- {w} n{n}: VRP {mu:+.2f} (t {t:+.2f})・cc {mc:+.2f} (t {tc:+.2f})・分散単位 {mv:+.2f} (t {tv:+.2f})")

# ---------- R1 Jensen ----------
say("\n## R1 単位・Jensen 分解（vol pt VRP = Δσ(分散整合) + Jensen 項）")
say("| 系列 | 窓 | n | mean IV − mean RV | sqrt(mean IV²) − sqrt(mean RV²) = Δσ | Jensen 項 | Δσ/VRP | 分散単位 (t) | sd IV / sd RV |")
say("|---|---|---|---|---|---|---|---|---|")
R1 = {}
def jensen(d, label, w):
    iv = d["IV"].to_numpy(); rv = d["RVf"].to_numpy(); vrp = iv.mean() - rv.mean()
    ds = np.sqrt((iv ** 2).mean()) - np.sqrt((rv ** 2).mean()); jen = vrp - ds
    mv, _, tv, _ = nw_mean(d["VRPvar"])
    say(f"| {label} | {w} | {len(d)} | {vrp:+.2f} | {ds:+.2f} | {jen:+.2f} | {ds/vrp:.2f} | {mv:+.2f} ({tv:+.2f}) | {iv.std():.1f} / {rv.std():.1f} |")
    return ds / vrp, mv
for w in WIN:
    R1[w] = jensen(XD[win_mask(XD, w) & XD["VRP"].notna()], "金 GVZ", w)
SW = {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
R1s = {}
for w, (y0, y1) in SW.items():
    yr = SD["date"].dt.year.to_numpy(); d = SD[(yr >= y0) & (yr <= y1) & SD["VRP"].notna().to_numpy()]
    R1s[w] = jensen(d, "株 US500 VIX", w)
say(f"- 分散単位の 比 金/株（在）: {R1['在 2010-20'][1]:+.2f} / {R1s['在 2014-20'][1]:+.2f} = {R1['在 2010-20'][1]/R1s['在 2014-20'][1]:.2f}（外 {R1['外 2021-26H1'][1]:+.2f} / {R1s['外 2021-26H1'][1]:+.2f} = {R1['外 2021-26H1'][1]/R1s['外 2021-26H1'][1]:.2f}）")
r1_in, r1_out = R1["在 2010-20"][0], R1["外 2021-26H1"][0]
v1 = "survived" if (r1_in >= 0.75 and r1_out >= 0.75) else ("broken（vol pt の大きさは Jensen で過大）" if (r1_in < 0.5 or r1_out < 0.5) else "inconclusive")
say(f"- **R1 判定: Δσ/VRP 在 {r1_in:.2f}／外 {r1_out:.2f} → {v1}**")

# ---------- R2 年クラスタ・別分割 ----------
say("\n## R2 有効 n（年クラスタ）・別分割（分散単位・vol pt 併記）")
XD["yr"] = XD["date"].dt.year
Y = XD[XD["VRP"].notna() & (XD["yr"] >= 2010)].groupby("yr").agg(vrp=("VRP", "mean"), vv=("VRPvar", "mean"), n=("VRP", "size"))
say("- 年別 分散単位: " + " | ".join(f"{y}: {r.vv:+.2f} (vol {r.vrp:+.1f}・n{int(r.n)})" for y, r in Y.iterrows()))
def tyear(ys):
    a = Y.loc[ys]; m = a["vv"].mean(); se = a["vv"].std(ddof=1) / np.sqrt(len(a)); mp = a["vrp"].mean(); sep = a["vrp"].std(ddof=1) / np.sqrt(len(a))
    return m, m / se, mp, mp / sep, len(a)
yin = list(range(2010, 2021)); yout = list(range(2021, 2027))
mi, ti, mpi, tpi, ni = tyear(yin); mo, to, mpo, tpo, no = tyear(yout)
say(f"- 年クラスタ t: 在 {ni} 年 分散単位 {mi:+.2f} (t {ti:+.2f})・vol pt {mpi:+.2f} (t {tpi:+.2f})；外 {no} 年 分散単位 {mo:+.2f} (t {to:+.2f})・vol pt {mpo:+.2f} (t {tpo:+.2f})")
loo = [(y, tyear([z for z in yout if z != y])[:2]) for y in yout]
say("- 外 leave-one-year-out（分散単位 mean, t）: " + "；".join(f"除{y}: {m:+.2f} (t {t:+.2f})" for y, (m, t) in loo))
# 外 2021-25（2026 除く）の NW
d = XD[(XD["yr"] >= 2021) & (XD["yr"] <= 2025) & XD["VRP"].notna()]; m5, _, t5, n5 = nw_mean(d["VRPvar"]); mp5, _, tp5, _ = nw_mean(d["VRP"])
say(f"- 外 2021-25（2026 除く）NW: 分散単位 {m5:+.2f} (t {t5:+.2f})・vol pt {mp5:+.2f} (t {tp5:+.2f})・n{n5}")
splits = {"2010-14": (2010, 2014), "2015-20": (2015, 2020), "2021-23": (2021, 2023), "2024-26H1": (2024, 2026)}
sp = {}
for k, (y0, y1) in splits.items():
    d = XD[(XD["yr"] >= y0) & (XD["yr"] <= y1) & XD["VRP"].notna()]; mv, _, tv, n = nw_mean(d["VRPvar"]); mp, _, tp, _ = nw_mean(d["VRP"]); sp[k] = mv
    say(f"- 独立 4 窓 {k} n{n}: 分散単位 {mv:+.2f} (t {tv:+.2f})・vol pt {mp:+.2f} (t {tp:+.2f})")
for k, sel in (("偶数年", XD["yr"] % 2 == 0), ("奇数年", XD["yr"] % 2 == 1)):
    d = XD[sel & (XD["yr"] >= 2010) & XD["VRP"].notna()]; mv, _, tv, n = nw_mean(d["VRPvar"]); say(f"- {k} n{n}: 分散単位 {mv:+.2f} (t {tv:+.2f})")
v2 = "survived" if (ti >= 2 and to >= 1.5 and all(v > 0 for v in sp.values())) else "inconclusive（外の分散単位 PASS は年の少なさに依存）"
say(f"- **R2 判定: 在 t_year {ti:+.2f}・外 t_year {to:+.2f}・4 窓 >0 {all(v > 0 for v in sp.values())} → {v2}**")

# ---------- R3 レジーム ----------
say("\n## R3 レジーム部分集合（在で切った三分位・固定カット）")
ins = XD[win_mask(XD, "在 2010-20") & XD["VRP"].notna() & XD["RVt"].notna()]
cg = np.quantile(ins["IV"], [1 / 3, 2 / 3]); ct = np.quantile(ins["RVt"], [1 / 3, 2 / 3])
say(f"- カット: GVZ {cg[0]:.1f}／{cg[1]:.1f}・RV_trail {ct[0]:.1f}／{ct[1]:.1f}")
say("| 条件 | 窓 | n | VRP vol pt (NW t) | 分散単位 (NW t) | VRP>0 % |")
say("|---|---|---|---|---|---|")
R3top = {}
for nm, col, cut in (("GVZ", "IV", cg), ("RV_trail", "RVt", ct)):
    for lab, lo, hi in (("low", -np.inf, cut[0]), ("mid", cut[0], cut[1]), ("top", cut[1], np.inf)):
        for w in ("在 2010-20", "外 2021-26H1"):
            d = XD[win_mask(XD, w) & XD["VRP"].notna() & XD["RVt"].notna()]; d = d[(d[col] > lo) & (d[col] <= hi)]
            if len(d) < 30: say(f"| {nm} {lab} | {w} | {len(d)} | — | — | — |"); continue
            mp, _, tp, n = nw_mean(d["VRP"]); mv, _, tv, _ = nw_mean(d["VRPvar"])
            say(f"| {nm} {lab} | {w} | {n} | {mp:+.2f} ({tp:+.2f}) | {mv:+.2f} ({tv:+.2f}) | {(d['VRP']>0).mean()*100:.0f}% |")
            if nm == "GVZ" and lab == "top": R3top[w] = mv
say(f"- R3 記述: GVZ top 三分位 分散単位 在 {R3top['在 2010-20']:+.2f}／外 {R3top['外 2021-26H1']:+.2f} → {'高 IV では売り手が払う（静穏レジームの現象）' if all(v <= 0 for v in R3top.values()) else '高 IV でもプレミアム正（レジーム限定ではない）'}")

# ---------- R4 プラセボ校正 ----------
say("\n## R4 検定の校正（GVZ を年内 21 日ブロックでシャッフル・200 回）")
base = XD[XD["VRP"].notna() & XD["RVt"].notna() & (XD["yr"] >= 2010)].reset_index(drop=True)
def shuffle_iv(df):
    out = df["IV"].to_numpy().copy()
    for y, idx in df.groupby("yr").indices.items():
        idx = np.asarray(idx); nb = int(np.ceil(len(idx) / 21)); blocks = [idx[k * 21:(k + 1) * 21] for k in range(nb)]
        order = rng.permutation(nb); out[idx] = np.concatenate([df["IV"].to_numpy()[blocks[o]] for o in order])[:len(idx)]
    return out
pass_cnt = 0; tin = []; tout = []; bet = []
for k in range(200):
    ivs = shuffle_iv(base); vrp = ivs - base["RVf"].to_numpy()
    mi_, _, ti_, _ = nw_mean(vrp[win_mask(base, "在 2010-20")]); mo_, _, to_, _ = nw_mean(vrp[win_mask(base, "外 2021-26H1")])
    tin.append(ti_); tout.append(to_); pass_cnt += int(mi_ > 0 and ti_ >= 2 and mo_ > 0 and to_ >= 1.5)
    m = win_mask(base, "外 2021-26H1"); b, se, t, _, _ = nw_ols(base.loc[m, "RVf"], np.column_stack([ivs[m], base.loc[m, "RVt"]])); bet.append((b[1], t[1], b[2], t[2]))
bet = np.array(bet)
say(f"- H_VRP 規則の通過率（シャッフル GVZ）: **{pass_cnt/200*100:.0f}%**（在 t 中央値 {np.median(tin):+.2f}・外 {np.median(tout):+.2f}）＝ PASS は IV の水準差で決まり整列を検定していない")
say(f"- 陽性対照 ② 外（シャッフル GVZ）: β_GVZ 中央値 {np.median(bet[:,0]):+.3f} (t {np.median(bet[:,1]):+.2f})・γ_RVt 中央値 {np.median(bet[:,2]):+.3f} (t {np.median(bet[:,3]):+.2f})・β t≥2 の割合 {(bet[:,1]>=2).mean()*100:.0f}%＝対照 ② は整列の検定として機能（実測 β +1.115 t 4.81）")

# ---------- R5 HAR 包含（log） ----------
say("\n## R5 包含回帰（log HAR: log RVf = a + β log GVZ + γ1 log RV1 + γ5 log RV5 + γ21 log RV21・NW 21）")
lg = lambda s: np.log(np.maximum(s.to_numpy(float), 1e-6))
R5 = {}
for w in WIN:
    d = XD[win_mask(XD, w) & XD["VRP"].notna() & XD["RVt"].notna() & XD["RV5"].notna() & (XD["RV1"] > 0)]
    b, se, t, n, r2 = nw_ols(lg(d["RVf"]), np.column_stack([lg(d["IV"]), lg(d["RV1"]), lg(d["RV5"]), lg(d["RVt"])]))
    b0, se0, t0, _, r20 = nw_ols(lg(d["RVf"]), np.column_stack([lg(d["IV"]), lg(d["RVt"])]))
    say(f"- {w} n{n}: β_GVZ {b[1]:+.3f} (t {t[1]:+.2f})・γ1 {b[2]:+.3f} ({t[2]:+.2f})・γ5 {b[3]:+.3f} ({t[3]:+.2f})・γ21 {b[4]:+.3f} ({t[4]:+.2f})・R² {r2:.3f}｜2 変数 log: β {b0[1]:+.3f} ({t0[1]:+.2f})・γ21 {b0[2]:+.3f} ({t0[2]:+.2f})・R² {r20:.3f}")
    R5[w] = (b[2:], t[2:])
sig_in = [(np.sign(R5["在 2010-20"][0][k]), abs(R5["在 2010-20"][1][k]) >= 2) for k in range(3)]
sig_out = [(np.sign(R5["外 2021-26H1"][0][k]), abs(R5["外 2021-26H1"][1][k]) >= 2) for k in range(3)]
anyb = any(sig_in[k][1] and sig_out[k][1] and sig_in[k][0] == sig_out[k][0] for k in range(3))
allq = all((not sig_in[k][1]) and (not sig_out[k][1]) for k in range(3))
v5 = "broken（trailing RV 成分が同符号で |t|≥2・GVZ は完全には包含しない）" if anyb else ("survived" if allq else "inconclusive")
say(f"- **R5 判定: {v5}**")

# ---------- R6 scan 露出の地平 ----------
say("\n## R6 scan の露出を地平別・分散単位で（W2 の予算 ≤0.012R）")
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True); FT = J["frozen"]["FEED_TOL"]
e_ny = pd.to_datetime(T["entry_time"], unit="s", utc=True).dt.tz_convert(NY) + pd.Timedelta(hours=6)
T["sdate"] = e_ny.dt.normalize().dt.tz_localize(None)
ent_jst = pd.to_datetime(T["entry_time"], unit="s", utc=True) + pd.Timedelta(hours=9)
T["avail"] = (ent_jst - pd.Timedelta(hours=7)).dt.normalize().dt.tz_localize(None) - pd.Timedelta(days=1)
K = XD[["date", "IV"]].dropna().rename(columns={"date": "kdate"}).sort_values("kdate")
T = pd.merge_asof(T.sort_values("avail"), K, left_on="avail", right_on="kdate", direction="backward", tolerance=pd.Timedelta(days=7))
T = T.merge(XD[["date", "RVf", "RV1"]].rename(columns={"date": "sdate"}), on="sdate", how="left").sort_values("entry_time").reset_index(drop=True)
# 保有窓 RV（ohlc close・entry 足〜exit 足）
zo = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); TSo = zo["ts"].astype(np.int64); Co = zo["close"].astype(float)
lco = np.log(Co); r2o = np.zeros(len(Co)); r2o[1:] = np.diff(lco) ** 2; cso = np.concatenate([[0.0], np.cumsum(r2o)])
ie = np.searchsorted(TSo, T["entry_time"].to_numpy()); okg = (ie < len(TSo)) & (TSo[np.minimum(ie, len(TSo) - 1)] == T["entry_time"].to_numpy())
hold = T["hold"].to_numpy().astype(int); ix = np.minimum(ie + hold, len(TSo) - 1)
sumr2 = cso[ix + 1] - cso[np.minimum(ie + 1, len(TSo) - 1)]
T["RVh"] = np.where(okg & (hold >= 1), 100 * np.sqrt(np.maximum(sumr2 * 288 * 252 / np.maximum(hold, 1), 0)), np.nan)
say(f"- 建玉足の格子一致 {okg.mean()*100:.1f}%・hold 中央値 {np.median(hold):.0f} 本・RVh 中央値 {np.nanmedian(T['RVh']):.1f}%（保有窓・年率）vs RV1（建玉セッション日）中央値 {T['RV1'].median():.1f}% vs RVf 中央値 {T['RVf'].median():.1f}%")
T["VSv21"] = (T["RVf"] ** 2 - T["IV"] ** 2) / 100; T["VSv1"] = (T["RV1"] ** 2 - T["IV"] ** 2) / 100; T["VSvh"] = (T["RVh"] ** 2 - T["IV"] ** 2) / 100
T["VS21"] = T["RVf"] - T["IV"]
T["q"] = (1 - FT / T["risk"]) / (1 + T["b"]); T["x"] = (T["exit"] == "TP").astype(float) - T["q"]; T["day"] = T["entry_time"] // 86400
dec = T["exit"].isin(["TP", "SL"]) & T["IV"].notna()
def cl_ols(y, x, day):
    y = np.asarray(y, float); x = np.asarray(x, float); xm = x - x.mean(); b = (xm * y).sum() / (xm ** 2).sum(); a = y.mean() - b * x.mean()
    u = y - a - b * x; s = pd.DataFrame({"d": xm * u, "g": day}).groupby("g")["d"].sum().to_numpy(); se = np.sqrt((s ** 2).sum()) / (xm ** 2).sum()
    return b, se, b / se
say("| 窓 | n | R̄ | 露出 | β (R per 分散単位・日cl t) | mean VS (trades) | 予算 β×mean VS (R) | 予算/R̄ |")
say("|---|---|---|---|---|---|---|---|")
R6 = {}
for w, (y0, y1) in WIN.items():
    for lab, col in (("21 日 vol pt (c34b)", "VS21"), ("21 日 分散", "VSv21"), ("1 日(建玉日) 分散", "VSv1"), ("保有窓 分散(記述)", "VSvh")):
        m = dec & (T["year"] >= y0) & (T["year"] <= y1) & T[col].notna(); d = T[m]
        b, se, t = cl_ols(d["R"], d[col], d["day"]); mv = d[col].mean(); bud = b * mv
        say(f"| {w} | {len(d)} | {d['R'].mean():+.3f} | {lab} | {b:+.5f} ({t:+.2f}) | {mv:+.2f} | {bud:+.4f} | {bud/d['R'].mean()*100:.0f}% |")
        R6[(w, col)] = (b, t, mv, bud)
# 十分位（在・VSv1）
m = dec & (T["year"] >= 2010) & (T["year"] <= 2020) & T["VSv1"].notna(); d = T[m].copy(); d["dq"] = pd.qcut(d["VSv1"], 10, labels=False)
g = d.groupby("dq").agg(R=("R", "mean"), x=("x", "mean"), vs=("VSv1", "mean"), n=("R", "size"))
say("- 在 VSv1 十分位（低→高）R̄: " + " ".join(f"{v:+.3f}" for v in g["R"]) + "｜x̄ pp: " + " ".join(f"{v*100:+.1f}" for v in g["x"]) + "｜mean VSv1: " + " ".join(f"{v:+.1f}" for v in g["vs"]))
# 側別 6 セル Bonferroni
from math import erf, sqrt
pn = lambda t: 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))
for w, (y0, y1) in WIN.items():
    out = []
    for sd_ in ("BUY", "SELL"):
        m = dec & (T["year"] >= y0) & (T["year"] <= y1) & (T["side"] == sd_) & T["VS21"].notna(); d = T[m]; b, se, t = cl_ols(d["R"], d["VS21"], d["day"])
        out.append(f"{sd_} β {b:+.4f} (t {t:+.2f}・Bonf(6) p {min(1, 6*pn(t)):.3f})")
    say(f"- {w} 側別 (21 日 vol pt): " + "；".join(out))
b1, t1, mv1, bud1 = R6[("在 2010-20", "VSv1")]; b21, t21, mv21, bud21 = R6[("在 2010-20", "VSv21")]
v6 = "broken（1 日地平の予算が −0.058R の 50% 以上）" if (bud1 <= -0.029 and t1 >= 2) else ("survived" if (abs(bud1) <= 0.015 and abs(bud21) <= 0.015) else "inconclusive")
say(f"- **R6 判定: 在 予算 21 日分散 {bud21:+.4f}R (β t {t21:+.2f})・1 日分散 {bud1:+.4f}R (β t {t1:+.2f}) → {v6}**")

# ---------- R7 2026H1・近年 ----------
say("\n## R7 2026H1・近年（記述）")
d26 = XD[(XD["yr"] == 2026) & XD["VRP"].notna()]
say(f"- 2026 有効日 {len(d26)}（{d26['date'].min().date()}〜{d26['date'].max().date()}・前向き窓は npz 終端 2026-06-30 まで）: vol pt {d26['VRP'].mean():+.2f}・分散単位 {d26['VRPvar'].mean():+.2f}・GVZ {d26['IV'].mean():.1f}・RVf {d26['RVf'].mean():.1f}")
for y in (2024, 2025, 2026):
    dd = XD[(XD["yr"] == y) & XD["VRP"].notna()]; mv, _, tv, n = nw_mean(dd["VRPvar"]); say(f"- {y} n{n}: 分散単位 {mv:+.2f} (NW t {tv:+.2f})・月別 " + " ".join(f"{m:02d}:{v:+.1f}" for m, v in dd.groupby(dd["date"].dt.month)["VRPvar"].mean().items()))
# 近年 2024-25 のみ
dd = XD[(XD["yr"] >= 2024) & (XD["yr"] <= 2025) & XD["VRP"].notna()]; mv, _, tv, n = nw_mean(dd["VRPvar"]); mp, _, tp, _ = nw_mean(dd["VRP"])
say(f"- 近年 2024-25（2026 除く）n{n}: 分散単位 {mv:+.2f} (t {tv:+.2f})・vol pt {mp:+.2f} (t {tp:+.2f})")

say("\n## 判定（docstring の規則）")
say(f"- R1 (W1 大きさ・単位): {v1}")
say(f"- R2 (W1 有効 n): {v2}")
say(f"- R5 (W3 包含): {v5}")
say(f"- R6 (W2 予算): {v6}")
say(f"- Bonferroni(4) 名目 |t| 閾値 2.50 併記。コスト倍: 取引不能のため該当なし。")
say(f"\n- 実行時間 {time.time()-T0:.1f}s・scan 無し・MT5 無し・外部通信無し・seed 20261111")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
