# -*- coding: utf-8 -*-
"""
[cycle10 研究レーン] 2026-11-06 — 【探索・日次マクロの遅い状態】金の構造的ドライバー（米 10y 実質金利・広義ドル）の
**20 営業日トレンド**は、再加速（壁→壁）の平均R を「追い風／向かい風」として条件づけるか

=== 事前固定（この docstring を書いてから数字を見る） ===
背景: cycle5 は日次マクロの「前日の 1 日変化」のみを試し null（粒度の限界と明記）。backlog「【探索・日次マクロの遅い状態】
      20 営業日トレンド（実質金利の向き・ドルの向き）× side の整合＝遅いレジームとしての条件づけは未試験」を選ぶ。
      cycle9/反証 05:30 は「金自身のトレンド度（ER）」が条件づけないことを確定したが、それは向きを持たない状態量。
      ここでは**外部ドライバーの向き**（金に強気か弱気か）を遅い状態として使う。
経済仮説: 金は無利子の長期実質資産。実質金利の持続的低下（・ドルの持続的下落）は ETF/機関の配分フローを**数週間かけて**動かす
      （フローは日次ショックより遅い）。その追い風の中では上方向の壁抜けが走り（TP）、向かい風の中では壁抜けが戻される。
      参加者: 配分を遅く調整する機関・ETF。解消されない理由: フロー自体が遅く、壁→壁の成否は数時間尺度でその背景流に乗る/逆らう。
      成立しなくなる条件: 金が実質金利・ドルから切り離される時代（2022-24 の中銀買い主導）。
問い（主セル 2）:
  F_T(DFII10): tailwind = (BUY ∧ Δ20 実質金利 < 0) ∨ (SELL ∧ Δ20 > 0)、headwind = その逆。予測 diff(tail − head) > 0。
  F_T(DTWEXBGS): 同形（ドル下落が BUY の追い風）。**公表遅延を明示的に課す**: Fed H.10 は約 4〜5 営業日遅れ →
      ドルの参照日 = avail_date − 7 暦日（cycle5 は D+1 で結合し「代理」と注記した。本サイクルは厳密側に寄せる）。
  複製（記述・判定不使用）: DGS10 名目 20d／各系列 60d／強度付き（|Δ20| が直近 500 営業日の上位 1/3 の本だけで tail − head）。
  競合（記述）: 金自身の 20 営業日の向き × side（金は実質金利に逆相関で動くので、追い風 = 金自身の上昇トレンドの代理かもしれない）。
      その上で「マクロ追い風 ∧ 金自身の 20d と逆」のセルを出し、マクロが金自身の向きを超える情報を持つかを見る。
データ（既存キャッシュのみ・scan 無し・path 再構築無し・M1/M5 原本読込なし・MT5 無し・外部通信無し）:
  - 本: data/c8_crossasset_features.csv（19404 本・R gross・side・te・year）
  - マクロ: data/macro/{DFII10,DGS10,DTWEXBGS}.csv（FRED 日次・欠損 "." を落として営業日行）→ Δ20 = v(D) − v(20 行前)。
  - 利用可能時刻（5条・cycle5 と同一）: FRED 日付 D の値は JST D+1 07:00 以降の本のみ → avail_date = (entry_JST − 7h).date() − 1 日、
    asof backward・staleness ≤10 暦日。DTWEXBGS のみ avail_date − 7 暦日。
  - 金自身: data/macro/XAU_daily_er.csv の lc（擬似日 22:00 UTC 境界）。土日の擬似日（flat・反証 05:30）を落として営業日行にし Δ20。
    参照 = known ≤ te（建玉足の 1 本前までに確定した日足）。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 水準は近年で語る・16 年プールは使わない）。
統計: Welch t・日クラスタ t・**月クラスタ t**（20d トレンドは数週間持続するので日クラスタでは不足・記述）・MDE 2·se・注入 +0.05R → t。
  family-wise: 参照日 avail_date を k 週 循環シフト（⑨・1000 回・曜日/自己相関構造を保つ）で 外窓 主 2 セル max|t| → p_max。
合否（c5/c8/c9 と同じ）: 在 t≥2 で予測方向 ∧ 外 同符号 t≥1.5 ∧ p_max<0.05 のセルが 1 つでもあれば「条件づけあり」、無ければ null。
構造仮説の読み（判定と別・事前に書いた規則）: 主セルが null でも、競合「金自身の 20d 向き × side」が 在/外で同符号 t≥1.5 なら
  「遅い追い風は金自身の価格トレンドに還元される」と読む。両方 null なら「数週間尺度の背景流は壁→壁の成否を条件づけない」。
事前の最重要反証: (1) 追い風群と金自身の上昇トレンド（および outer 壁・大きい b の組成）が重なる＝幾何差の混入 → 競合セル＋側別で確認。
  (2) 20d トレンドの強い自己相関で有効 n は本数より遥かに小さい → 月クラスタ t と週シフト置換で校正。(3) 2 主セル＋複製の事後選択 → 主 2 セルのみ判定。
昇格候補ではない（レジーム記述・DATA_MAP §6 の更新が主目的）。seed 20261106.
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c10_slow_macro_result.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)

say(f"# [cycle10] 遅いマクロ・トレンド（20 営業日）× 再加速 R — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c10_slow_macro_trend.py)")
say("## 0. データ")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
X["day"] = X["ts_jst"].dt.normalize(); X["month"] = X["ts_jst"].dt.to_period("M").astype(str)
X["sgn"] = np.where(X["side"] == "BUY", 1.0, -1.0)
say(f"- trades n={len(X)} {X.ts_jst.min()}..{X.ts_jst.max()} JST、R mean {X.R.mean():+.4f}（水準は使わない・D2）")

# ---- macro series: business-day rows, Δ20 / Δ60, |Δ| percentile over trailing 500 rows (current excluded) ----
SERIES = {"DFII10": ("実質10y", 0), "DTWEXBGS": ("広義ドル", 7), "DGS10": ("名目10y", 0)}  # (label, publication lag days)
def rpct(a, win=500, minp=250):
    out = np.full(len(a), np.nan)
    for i in range(len(a)):
        w = a[max(0, i - win):i]; w = w[~np.isnan(w)]
        if len(w) >= minp and not np.isnan(a[i]): out[i] = (w < a[i]).mean()
    return out
MAC_D = {}
for sid, (lab, lag) in SERIES.items():
    m = pd.read_csv(os.path.join(MAC, f"{sid}.csv")); m.columns = ["date", "v"]
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m.dropna().copy()
    m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    for n in (20, 60):
        m[f"d{n}"] = m["v"] - m["v"].shift(n); m[f"p{n}"] = rpct(m[f"d{n}"].abs().to_numpy())
    MAC_D[sid] = m
    say(f"- {sid}({lab}): 営業日行 {len(m)} {m.date.min().date()}..{m.date.max().date()}、公表遅延 {lag} 日を課す、Δ20 sd {m.d20.std():.3f}")

def asof_series(m, ref_dates, cols, tol_days=10):
    d = m["date"].to_numpy().astype("datetime64[D]").astype(np.int64); r = ref_dates.to_numpy().astype("datetime64[D]").astype(np.int64)
    i = np.searchsorted(d, r, side="right") - 1; ok = i >= 0
    out = {}
    for c in cols:
        v = m[c].to_numpy(); o = np.full(len(r), np.nan); o[ok] = v[i[ok]]
        o[ok & ((r - d[np.clip(i, 0, None)]) > tol_days)] = np.nan; out[c] = o
    return out

def attach(X, ref_shift=None):
    """ref_shift: dict sid -> int64 shift in days applied to the reference date (for permutation); None = observed"""
    for sid, (lab, lag) in SERIES.items():
        ref = X["avail"] - pd.Timedelta(days=lag)
        if ref_shift is not None: ref = ref + pd.to_timedelta(ref_shift, unit="D")
        o = asof_series(MAC_D[sid], ref, ["d20", "d60", "p20", "p60"])
        for c, v in o.items(): X[f"{c}_{sid}"] = v
    return X
X = attach(X)
for sid in SERIES:
    ok = X[f"d20_{sid}"].notna()
    say(f"- 付与 {sid}: Δ20 あり {ok.mean()*100:.1f}%、p20 あり {X[f'p20_{sid}'].notna().mean()*100:.1f}%")

# ---- gold own 20-business-day trend (competitor) ----
G = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv"))
G["dt"] = pd.to_datetime(G["ts_last"], unit="s"); G["dow"] = G["dt"].dt.dayofweek
# 擬似日 22:00 UTC 境界: ts_last が土曜/日曜に落ちる擬似日は flat（反証 05:30）→ 落として営業日行にする
G = G[~G["dow"].isin([5, 6])].reset_index(drop=True)
G["g20"] = G["lc"] - G["lc"].shift(20); G["g60"] = G["lc"] - G["lc"].shift(60)
kn = G["known"].to_numpy(); te = X["te"].to_numpy()
i = np.searchsorted(kn, te, side="right") - 1; ok = i >= 0
for c in ("g20", "g60"):
    v = G[c].to_numpy(); o = np.full(len(X), np.nan); o[ok] = v[i[ok]]; o[ok & ((te - kn[np.clip(i, 0, None)]) > 5 * 86400)] = np.nan; X[c] = o
say(f"- 金自身 日足（土日擬似日除外）{len(G)} 行、g20 付与 {X.g20.notna().mean()*100:.1f}%、"
    f"相関 ρ(Δ20 実質金利, g20) {np.corrcoef(X.loc[X.g20.notna()&X.d20_DFII10.notna(),'d20_DFII10'], X.loc[X.g20.notna()&X.d20_DFII10.notna(),'g20'])[0,1]:+.3f}、"
    f"ρ(Δ20 ドル, g20) {np.corrcoef(X.loc[X.g20.notna()&X.d20_DTWEXBGS.notna(),'d20_DTWEXBGS'], X.loc[X.g20.notna()&X.d20_DTWEXBGS.notna(),'g20'])[0,1]:+.3f}")

W = {"在2010-20": X.year <= 2020, "外2021-26": X.year >= 2021, "近年2024-26": X.year >= 2024}
say("\n## 1. ベースライン（無条件平均R・gross）")
for wn, m in W.items(): say(f"- {wn}: n={m.sum()} mean {X.loc[m,'R'].mean():+.4f} sd {X.loc[m,'R'].std():.3f}")

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se
def cl_t(R, grp, g, d):
    """diff mean(R[g]) − mean(R[~g]) のクラスタ robust t（grp: cluster labels）"""
    a, b = g, ~g
    if a.sum() < 2 or b.sum() < 2: return np.nan
    inf = np.where(a, (R - R[a].mean()) / a.sum(), 0.0) - np.where(b, (R - R[b].mean()) / b.sum(), 0.0)
    s = pd.Series(inf).groupby(grp).sum(); se = math.sqrt((s ** 2).sum()); return d / se if se > 0 else np.nan

def tail_mask(df, col, bull_sign=-1):
    """tailwind = sign(side)·sign(Δ)·bull_sign > 0 ; bull_sign=-1: Δ<0 は BUY の追い風"""
    v = df[col].to_numpy(); ok = ~np.isnan(v) & (v != 0)
    tail = ok & ((df["sgn"].to_numpy() * np.sign(v) * bull_sign) > 0)
    return ok, tail

def cell(df, col, bull_sign=-1, strong_col=None, inject=0.0):
    ok, tail = tail_mask(df, col, bull_sign)
    if strong_col is not None: ok = ok & (df[strong_col].to_numpy() >= 2 / 3)
    R = df["R"].to_numpy().copy(); R[tail] += inject
    a = R[ok & tail]; b = R[ok & ~tail]
    d, t, se = welch(a, b)
    sub = ok
    tcd = cl_t(R[sub], df["day"].to_numpy()[sub], tail[sub], d) if sub.sum() > 3 else np.nan
    tcm = cl_t(R[sub], df["month"].to_numpy()[sub], tail[sub], d) if sub.sum() > 3 else np.nan
    return dict(diff=d, t=t, tcd=tcd, tcm=tcm, se=se, n1=int(len(a)), n0=int(len(b)))

def run(col, label, bull_sign=-1, strong_col=None):
    say(f"\n### {label}")
    out = {}
    for wn, m in W.items():
        r = cell(X[m], col, bull_sign, strong_col); ri = cell(X[m], col, bull_sign, strong_col, 0.05); out[wn] = r
        say(f"- {wn}: n={r['n1']}:{r['n0']} diff {r['diff']:+.4f} t {r['t']:+.2f} (日cl {r['tcd']:+.2f}・月cl {r['tcm']:+.2f}) MDE {2*r['se']:.3f}R 注入+0.05→t {ri['t']:+.2f}")
    return out

say("\n## 2. 主セル（diff = 追い風 − 向かい風・予測 >0・判定に使用）")
MAIN = {"F_T DFII10 20d": run("d20_DFII10", "F_T 実質金利 Δ20（BUY は実質金利低下が追い風）"),
        "F_T DTWEXBGS 20d": run("d20_DTWEXBGS", "F_T 広義ドル Δ20（公表遅延 7 日・BUY はドル下落が追い風）")}
say("\n## 3. 複製（記述・判定不使用）")
run("d20_DGS10", "名目10y Δ20"); run("d60_DFII10", "実質金利 Δ60"); run("d60_DTWEXBGS", "広義ドル Δ60（遅延 7 日）")
run("d20_DFII10", "実質金利 Δ20・強度上位 1/3 のみ", strong_col="p20_DFII10"); run("d20_DTWEXBGS", "広義ドル Δ20・強度上位 1/3 のみ", strong_col="p20_DTWEXBGS")

say("\n## 4. 競合（記述）: 金自身の 20 営業日の向き × side（BUY は金の上昇トレンドが追い風）")
GOLD = run("g20", "金自身 Δ20 log close", bull_sign=+1); run("g60", "金自身 Δ60", bull_sign=+1)
say("- マクロ追い風 ∧ 金自身 20d と**逆**（マクロが金自身の向きを超える情報を持つか）: tail − head を金 20d の向き内で")
for sid in ("DFII10", "DTWEXBGS"):
    for wn in ("在2010-20", "外2021-26", "近年2024-26"):
        sub = X[W[wn]]; okg, gtail = tail_mask(sub, "g20", +1)
        parts = []
        for nm, gm in (("金追い風内", gtail), ("金向かい風内", okg & ~gtail)):
            s2 = sub[gm]; r = cell(s2, f"d20_{sid}")
            parts.append(f"{nm} {r['diff']:+.4f} (t{r['t']:+.2f}, n{r['n1']}:{r['n0']})")
        say(f"  - {sid} {wn}: " + " / ".join(parts))
say("- 側別（追い風効果が BUY/SELL で対称か・外/近年）:")
for sid in ("DFII10", "DTWEXBGS"):
    for wn in ("在2010-20", "外2021-26", "近年2024-26"):
        parts = []
        for sd in ("BUY", "SELL"):
            r = cell(X[W[wn] & (X.side == sd)], f"d20_{sid}"); parts.append(f"{sd} {r['diff']:+.4f} (t{r['t']:+.2f})")
        say(f"  - {sid} {wn}: " + " / ".join(parts))
say("- 組成（外・追い風 vs 向かい風の outer 比率・b 平均・risk 平均）:")
for sid in ("DFII10", "DTWEXBGS"):
    sub = X[W["外2021-26"]]; ok, tail = tail_mask(sub, f"d20_{sid}")
    for nm, gm in (("追い風", ok & tail), ("向かい風", ok & ~tail)):
        s2 = sub[gm]; say(f"  - {sid} {nm}: n{len(s2)} outer {np.mean(s2.wall_kind=='outer'):.2f} b {s2.b.mean():.3f} risk {s2.risk.mean():.3f} TP率 {np.mean(s2.exit=='TP'):.3f}")
say("- 五分位（符号付き追い風量 = sign(side)·(−Δ20) の五分位・平均R・在/外）:")
for sid in ("DFII10", "DTWEXBGS"):
    for wn in ("在2010-20", "外2021-26"):
        sub = X[W[wn] & X[f"d20_{sid}"].notna()]; s = sub["sgn"] * (-sub[f"d20_{sid}"]); q = pd.qcut(s, 5, labels=False, duplicates="drop")
        say(f"  - {sid} {wn}: " + " ".join(f"{v:+.3f}" for v in sub.groupby(q)['R'].mean()))

# ---- family-wise permutation: circular weekly shift of the macro reference date (OOS, 2 main cells) ----
say("\n## 5. family-wise 置換（参照日を k 週 循環シフト・外窓・主 2 セル max|t|・1000 回）")
NPERM = 1000
oos = X[W["外2021-26"]].copy().reset_index(drop=True)
lo = pd.Timestamp("2011-01-03"); hi = pd.Timestamp("2026-06-26"); span_w = (hi - lo).days // 7
obs = np.array([MAIN["F_T DFII10 20d"]["外2021-26"]["t"], MAIN["F_T DTWEXBGS 20d"]["外2021-26"]["t"]]); obs_max = np.nanmax(np.abs(obs))
null = np.full((NPERM, 2), np.nan); tp = time.time()
base_off = (oos["avail"] - lo).dt.days.to_numpy()
for p in range(NPERM):
    k = int(rng.integers(8, span_w - 8))
    shifted = (base_off + 7 * k) % (span_w * 7)
    o2 = oos.copy(); o2["avail"] = lo + pd.to_timedelta(shifted, unit="D")
    o2 = attach(o2)
    null[p, 0] = cell(o2, "d20_DFII10")["t"]; null[p, 1] = cell(o2, "d20_DTWEXBGS")["t"]
    if time.time() - tp > 150: say(f"!! 置換 {p+1} 回で時間上限"); null = null[:p + 1]; break
nmax = np.nanmax(np.abs(null), axis=1); p_max = (nmax >= obs_max).mean()
say(f"- 観測 外 max|t| {obs_max:.2f} → 帰無 中央値 {np.median(nmax):.2f} / 95%点 {np.quantile(nmax,0.95):.2f} / **p_max {p_max:.3f}**（{len(nmax)} 回・{time.time()-tp:.0f} s）")
for j, nm in enumerate(MAIN):
    say(f"  - {nm}: 外 t {obs[j]:+.2f} 単セル置換 p {(np.abs(null[:, j]) >= abs(obs[j])).mean():.3f}（帰無 sd {np.nanstd(null[:, j]):.2f}）")

say("\n## 6. 判定（事前規則: 在 t≥2 予測方向 ∧ 外 同符号 t≥1.5 ∧ p_max<0.05）")
npass = 0
for nm, r in MAIN.items():
    ti, to, tr = r["在2010-20"]["t"], r["外2021-26"]["t"], r["近年2024-26"]["t"]
    ok = (ti >= 2.0) and (to >= 1.5) and (p_max < 0.05); npass += ok
    say(f"- {nm}: 在 t {ti:+.2f} / 外 t {to:+.2f} / 近年 t {tr:+.2f} / p_max {p_max:.3f} → {'PASS' if ok else 'FAIL'}")
say(f"\n**PASS {npass}/2 → {'条件づけあり' if npass else 'null'}**")
say("\n## 7. 構造仮説の読み（判定と別・事前に書いた規則）")
gi, go = GOLD["在2010-20"]["t"], GOLD["外2021-26"]["t"]
say(f"- 金自身 20d 向き × side: 在 t {gi:+.2f} / 外 t {go:+.2f} → " +
    ("在/外で同符号 t≥1.5 ＝『遅い追い風は金自身の価格トレンドに還元される』側" if (abs(gi) >= 1.5 and abs(go) >= 1.5 and np.sign(gi) == np.sign(go))
     else "金自身の 20d 向きも条件づけない ＝『数週間尺度の背景流は壁→壁の成否を条件づけない』側"))
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
