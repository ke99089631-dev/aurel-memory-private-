# -*- coding: utf-8 -*-
"""
[cycle27 研究レーン] 2026-11-10 — 【深化・レジーム／幾何の持続】壁→壁(再加速)の「優位」を
R でなく「RW 基準に対する超過 TP 到達率」で測ると、週〜月の尺度で持続するか。
＋ cycle6 で「TP 率は月次で持続（外 lag1 +0.24・近年 +0.53）するのに平均R は持続しない」のは
  TP 距離 b が TP 率を補償している（＝壁の幾何が RW として“値付け”されている）からか。

=== 事前固定（この docstring を書いてから数字を見る） ===
背景: cycle6（11-05）は週/月の平均R の lag1 自己相関・trailing 予測を null とした（MDE σ_μ≈0.10R・週 95% 上限 0.08R）。
      しかし R は b（TP 距離・R 単位）の分散と fat tail を含み、持続性の検出力が低い。本ごとの RW 基準
      q_i = P(TP before SL | 無ドリフト・SL=−(1−ft)R・TP=+(b_i+ft)R) = (1−ft_i)/(1+b_i)（ft_i = FEED_TOL/risk_i）
      に対する超過 x_i = 1{TP} − q_i（決着 SL/TP の本のみ）は分散 ≤0.25 で b の分散を含まず、
      「幾何を所与とした優位（走りやすさ）」そのものを測る。これはレジーム記述（メタ）・入口/出口の変更ではない。
      注: RW 基準の下で E[R*]=E[R+ft·1{SL/TP}]=0 が成り立つ（記帳公正化と同じ基準）。
データ: data/refute_c4_scan_paths_2010_2026.json 19404 本（entry_time・year・risk・b・R・exit・hold）。
      scan 無し・M5 読込なし・MT5 無し・外部通信なし。frozen FEED_TOL を使う。
集計: 週 = UTC 月〜日（W-SUN）・月 = 暦月。有効期間 = 決着本 n≥5（cycle6 と同じ）。
      x̄_w = mean x_i（決着本）、p_w = TP 率（決着本）、q̄_w = mean q_i、b̄_w = mean b（全本・建玉時に既知の幾何）、
      R̄*_w = mean R*（全本）、n_w = 本数。
統計: lag1 Pearson r（有効期間 w, w+1 が両方有効なペア）。帰無 = 有効期間の値を暦位置間でシャッフル 4000 回（持続だけ壊す）。
      trailing（真の前向き）: 週 t の直前 4 暦週の決着本 ≥10 本の x̄ を在の中央値で 2 群 → 週 t の x̄ の差（Welch t・週等重み）。
      月次は直前 3 暦月 ≥20 本。
予測・合否（主 = 週次・在 2010-20 で決め 外 2021-26H1 で確認・近年 2024-26H1 は記述）:
  H1 幾何の持続: b̄_w lag1 r>0・在 置換 p<0.05 ∧ 外 p<0.10（陽性対照の性格・ボラ追随で正のはず）。
  H2 補償（RW 値付け）: 週次 OLS p_w = α + β·q̄_w の β が 在・外とも 95% CI に 1 を含み 0 を含まない（幾何が RW 通りに値付け
      されている＝「TP 率の持続」は幾何の持続の別名）。補助: 反事実 R̃_w = p_w·b̄_w − (1−p_w)（b を固定しない）と
      R̂_w = p_w·b̄_all − (1−p_w)（b を全期間平均に固定）の lag1 r を実測 R̄*_w の lag1 と並べる。
  H3 主（優位の持続）: x̄_w lag1 r>0・在 置換 p<0.05 ∧ 外 p<0.10、かつ trailing 4 週 2 群差 >0・在 t≥2 ∧ 外 t≥1.5。
      H3 支持 = 両方 PASS。それ以外 null（MDE 併記）。月次 lag1・trailing は補助（Bonferroni なし・記述）。
MDE・陽性対照（方法論 ⑦）: (i) 置換帰無の 95% 点を r の検出閾値として印字。(ii) 分散分解: Var(x̄_w) − mean(q̄(1−q̄)/n_w)
      ＝レジーム分散 σ_μ² の点推定、期間ブロック（8 週）bootstrap 2000 の 95% 上限を「効果 ≤X pp」として報告。
      (iii) 注入: 週ごとに AR(1) φ=0.9 の μ_w（sd 3 pp／5 pp）を x_i に加えて lag1 r と置換 p を 200 回 → 検出率。
      (iv) 本数 n_w の lag1（既知 +0.42〜0.62）が再現すること。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 長期一括の平均 x̄ は edge 判定に使わない・窓別に印字）。
事前の最重要反証: (1) q_i は連続 RW・無ドリフト・バリア正確到達の閉形式で、離散足のオーバーシュート（SL/TP の同足優先）
      と週末ギャップを無視 → x̄ の水準には系統バイアスが乗り得る（refute_c0 の離散 MC では θ=0 勝率 0.434 vs 閉形式 0.432
      で差は小）。持続性（自己相関）は水準バイアスに影響されないので主判定は自己相関に置く。
      (2) 週内の本は同じ値動きを共有（重複建玉）→ x̄_w の実効 n は名目より小さい・分散分解の σ_μ² は過大側（保守的でない）
      → ブロック bootstrap の上限を主とし、点推定は参考。
      (3) p_w と q̄_w の回帰は同じ本の TP 指標と b を使うので、b の測定誤差は無いが「b が大きい週＝ボラが高い週」で
      TP 率が RW より下がる（ボラ依存の非 RW 性）と β<1 になる＝β の 1 からの乖離は“値付けの歪み”でなく尺度効果の可能性。
      (4) 決着本のみ（TIME 4.5% 除外）＝TIME は RW でも b 大の本に偏るので x̄ はわずかに上方バイアス（水準のみ）。
昇格候補ではない。seed 20261110。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c27_excess_hit_persistence_result.md")
rng = np.random.default_rng(20261110)
L = []
def say(s=""): print(s, flush=True); L.append(s)

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["week"] = tr["ts"].dt.to_period("W-SUN")
tr["month"] = tr["ts"].dt.to_period("M")
tr["ft"] = FT / tr["risk"]
tr["dec"] = tr["exit"].isin(["SL", "TP"])
tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"])
tr["x"] = tr["tp"] - tr["q"]
tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
say(f"# [cycle27] 超過 TP 到達率 x=1{{TP}}−q の持続性・幾何の RW 値付け — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c27_excess_hit_persistence.py)")
say(f"n={len(tr)} 本 {tr.ts.min()} .. {tr.ts.max()} UTC、FEED_TOL={FT}、決着 SL/TP {int(tr.dec.sum())}・TIME {int((~tr.dec).sum())}。")
say(f"b 中央値 {tr.b.median():.3f}（p10 {tr.b.quantile(.1):.2f}／p90 {tr.b.quantile(.9):.2f}）、q 中央値 {tr.q.median():.3f}、ft 平均 {tr.ft.mean():.4f}R。")
say()

W = {"在2010-20": tr.year <= 2020, "外2021-26": tr.year >= 2021, "近年2024-26": tr.year >= 2024}
NMIN = 5; NPERM = 4000

def agg(df, per):
    dd = df[df.dec]
    g = dd.groupby(per).agg(n=("x", "size"), xbar=("x", "mean"), p=("tp", "mean"), qbar=("q", "mean"),
                            vq=("q", lambda s: float((s * (1 - s)).mean())))
    g2 = df.groupby(per).agg(nall=("b", "size"), bbar=("b", "mean"), Rbar=("Rs", "mean"), riskbar=("risk", "mean"))
    g = g.join(g2, how="outer").sort_index()
    g["valid"] = g["n"].fillna(0) >= NMIN
    return g

def lag1_pairs_idx(g):
    idx = g.index[g["valid"]]
    pos = np.array([(p - g.index[0]).n for p in idx])
    s = set(pos.tolist())
    ok = np.array([(p + 1) in s for p in pos])
    a_pos = pos[ok]; b_pos = a_pos + 1
    posmap = {p: i for i, p in enumerate(pos)}
    ia = np.array([posmap[p] for p in a_pos]); ib = np.array([posmap[p] for p in b_pos])
    return ia, ib, len(idx)

def lag1_r(vals, ia, ib):
    a = vals[ia]; b = vals[ib]
    if len(a) < 4: return np.nan
    return float(np.corrcoef(a, b)[0, 1])

def perm_lag1(vals, ia, ib, nperm=NPERM):
    out = np.empty(nperm)
    for i in range(nperm):
        v = rng.permutation(vals); out[i] = lag1_r(v, ia, ib)
    return out

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, (diff / se if se > 0 else np.nan), se

def ols(y, x):
    X = np.column_stack([np.ones(len(x)), x]); beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    u = y - X @ beta; n, k = X.shape
    V = np.linalg.inv(X.T @ X) * (u @ u) / (n - k)
    return beta[1], math.sqrt(V[1, 1]), beta[0]

def trailing(df, g, per, L_, nmin):
    rows = []
    dd = df[df.dec]
    for t in g.index[g["valid"]]:
        prev = [t - j for j in range(1, L_ + 1)]
        sub = g.reindex(prev).dropna(subset=["n"])
        ntot = int(sub["n"].sum())
        if ntot < nmin: continue
        trail = float((sub["xbar"] * sub["n"]).sum() / ntot)
        rows.append({"per": t, "trail": trail, "xbar": g.loc[t, "xbar"], "n": g.loc[t, "n"]})
    return pd.DataFrame(rows)

RES = {}
# ---------- 0. 窓別の水準（記述・D2） ----------
say("## 0. 窓別の水準（記述・edge 判定に使わない）: 決着本の TP 率 p・RW 基準 q̄・超過 x̄（pp）・R̄*")
say("| 窓 | 決着 n | p (TP 率) | q̄ (RW) | x̄ = p−q̄ (pp) | t(x̄) | R̄* (全本) | b̄ | risk 中央値 |")
say("|---|---|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    s = tr[wm & tr.dec]; x = s.x.to_numpy()
    t_ = x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))
    say(f"| {wn} | {len(s)} | {s.tp.mean():.4f} | {s.q.mean():.4f} | {100*x.mean():+.2f} | {t_:+.2f} | {tr[wm].Rs.mean():+.4f} | {tr[wm].b.mean():.3f} | {tr[wm].risk.median():.2f} |")
say("年別 x̄（pp）: " + " ".join(f"{y}:{100*tr[(tr.year==y)&tr.dec].x.mean():+.1f}" for y in sorted(tr.year.unique())))
say()

for per, (TL, TMIN) in (("week", (4, 10)), ("month", (3, 20))):
    say(f"## {per}: 有効 = 決着本 n≥{NMIN}・lag1 自己相関（置換 {NPERM}）・trailing（直前 {TL} {per}・≥{TMIN} 本）")
    thr_in = None
    for wn, wm in W.items():
        g = agg(tr[wm], per)
        ia, ib, nv = lag1_pairs_idx(g)
        v = g[g["valid"]]
        say(f"### {wn}: 期間 {len(g)}・有効 {nv}・ペア {len(ia)}・決着本/期間 中央値 {v.n.median():.0f}・x̄ の sd {v.xbar.std():.4f}・名目 se 中央値 {np.sqrt(v.vq / v.n).median():.4f}")
        row = {}
        say("| 量 | lag1 r | 置換 片側 p (r>0) | 帰無 95% 点 | lag2 r |")
        say("|---|---|---|---|---|")
        for col, lab in (("xbar", "x̄ 超過到達率（主）"), ("p", "p TP 率"), ("qbar", "q̄ RW 基準"), ("bbar", "b̄ TP 距離"), ("Rbar", "R̄* 平均R"), ("n", "n 決着本数（陽性対照）"), ("riskbar", "risk 平均 USD")):
            vals = v[col].to_numpy(float)
            r1 = lag1_r(vals, ia, ib)
            null = perm_lag1(vals, ia, ib, NPERM if col in ("xbar", "p", "bbar", "Rbar", "n") else 1000)
            p1 = float((null >= r1).mean()); q95 = float(np.quantile(null, .95))
            # lag2
            pos = np.array([(p - g.index[0]).n for p in v.index]); s = {p: i for i, p in enumerate(pos)}
            ok2 = np.array([(p + 2) in s for p in pos]); ia2 = np.array([s[p] for p in pos[ok2]]); ib2 = np.array([s[p + 2] for p in pos[ok2]])
            r2 = lag1_r(vals, ia2, ib2) if ok2.sum() > 4 else np.nan
            row[col] = dict(r1=r1, p1=p1, q95=q95)
            say(f"| {lab} | **{r1:+.3f}** | {p1:.3f} | {q95:+.3f} | {r2:+.3f} |")
        # H2: p on qbar
        beta, se, alpha = ols(v.p.to_numpy(), v.qbar.to_numpy())
        rho_pq = np.corrcoef(v.p, v.qbar)[0, 1]; rho_pb = np.corrcoef(v.p, v.bbar)[0, 1]
        say(f"- H2 補償: 期間 OLS p = α + β·q̄: **β {beta:+.3f}（se {se:.3f}・95% CI {beta-1.96*se:+.2f}〜{beta+1.96*se:+.2f}）**・α {alpha:+.3f}・ρ(p, q̄) {rho_pq:+.3f}・ρ(p, b̄) {rho_pb:+.3f}")
        # counterfactual R
        Rt = v.p * v.bbar - (1 - v.p)
        Rh = v.p * tr[wm].b.mean() - (1 - v.p)
        r_Rt = lag1_r(Rt.to_numpy(float), ia, ib); r_Rh = lag1_r(Rh.to_numpy(float), ia, ib)
        say(f"  反事実 lag1 r: R̃（p と b̄ を期間ごと）{r_Rt:+.3f}／R̂（b を全期間平均 {tr[wm].b.mean():.2f} に固定・p だけ変動）{r_Rh:+.3f}／実測 R̄* {row['Rbar']['r1']:+.3f}／p {row['p']['r1']:+.3f}")
        # trailing
        T = trailing(tr[wm], g, per, TL, TMIN)
        if wn == "在2010-20": thr_in = float(T["trail"].median())
        thr = thr_in
        good = T["trail"] > thr; bad = ~good
        diff, t_, se_ = welch(T.loc[good, "xbar"], T.loc[bad, "xbar"])
        from scipy.stats import spearmanr
        rho, prho = spearmanr(T["trail"], T["xbar"])
        qq = pd.qcut(T["trail"], 5, labels=False, duplicates="drop")
        say(f"- trailing x̄（前向き）: 期間 {len(T)}・Spearman ρ {rho:+.4f} (p {prho:.3f})・閾値(在中央値) {100*thr:+.2f} pp・good n={good.sum()} {100*T.loc[good,'xbar'].mean():+.2f} pp vs bad n={bad.sum()} {100*T.loc[bad,'xbar'].mean():+.2f} → **diff {100*diff:+.2f} pp (t {t_:+.2f}・MDE 2se {200*se_:.2f} pp)**；五分位 " + " ".join(f"{100*m:+.1f}" for m in T.groupby(qq)["xbar"].mean()))
        row["trail"] = dict(diff=diff, t=t_, se=se_)
        # variance decomposition（週次のみ）
        if per == "week":
            xb = v.xbar.to_numpy(float); noise = (v.vq / v.n).to_numpy(float)
            excess = xb.var(ddof=1) - noise.mean()
            # block bootstrap 8 weeks
            B = 8; nb = len(xb) // B; blocks = [np.arange(i * B, (i + 1) * B) for i in range(nb)]
            bs = np.empty(2000)
            for i in range(2000):
                pick = rng.integers(0, nb, nb); idx = np.concatenate([blocks[j] for j in pick])
                bs[i] = xb[idx].var(ddof=1) - noise[idx].mean()
            up = float(np.quantile(bs, .95))
            say(f"- 分散分解（週）: Var(x̄) {xb.var(ddof=1):.5f} − 名目ノイズ mean(q̄(1−q̄)/n) {noise.mean():.5f} = σ_μ² 点推定 {excess:+.5f}（σ_μ {100*math.sqrt(max(excess,0)):.2f} pp）・8 週ブロック bootstrap 95% 上限 {up:+.5f} → **σ_μ ≤ {100*math.sqrt(max(up,0)):.2f} pp**（R 換算 ×(1+b̄) ≈ {math.sqrt(max(up,0))*(1+tr[wm].b.mean()):.3f}R）")
            row["sig_up"] = math.sqrt(max(up, 0))
            # injection
            if wn in ("在2010-20", "外2021-26"):
                det = {}
                for sd_mu in (0.03, 0.05):
                    hits = 0; rs = []
                    for rep in range(200):
                        mu = np.empty(len(xb)); mu[0] = rng.normal(0, sd_mu)
                        for i in range(1, len(xb)): mu[i] = 0.9 * mu[i - 1] + rng.normal(0, sd_mu * math.sqrt(1 - 0.81))
                        xi = xb + mu
                        r1 = lag1_r(xi, ia, ib); rs.append(r1)
                        hits += r1 > row["xbar"]["q95"]
                    det[sd_mu] = (hits / 200, float(np.mean(rs)))
                say(f"- 注入（AR(1) φ=0.9 のレジーム μ_w を週 x̄ に加算・200 回）: sd 3 pp → lag1 r 平均 {det[0.03][1]:+.3f}・検出率(r>帰無95%点) **{det[0.03][0]:.2f}**；sd 5 pp → r {det[0.05][1]:+.3f}・検出率 **{det[0.05][0]:.2f}**")
        RES[(per, wn)] = row
        say()

# ---------- 判定 ----------
say("## 判定（事前規則・週次・在で決め外で確認）")
a, b_ = RES[("week", "在2010-20")], RES[("week", "外2021-26")]
H1 = (a["bbar"]["r1"] > 0 and a["bbar"]["p1"] < 0.05) and (b_["bbar"]["r1"] > 0 and b_["bbar"]["p1"] < 0.10)
say(f"- H1 幾何の持続 b̄ lag1>0（在 p<0.05 ∧ 外 p<0.10）: 在 r {a['bbar']['r1']:+.3f} p {a['bbar']['p1']:.3f}／外 r {b_['bbar']['r1']:+.3f} p {b_['bbar']['p1']:.3f} → {'PASS' if H1 else 'FAIL'}")
say(f"- H2 補償 β（p on q̄・在/外の CI が 1 を含み 0 を含まない）: 上表参照")
P1 = (a["xbar"]["r1"] > 0 and a["xbar"]["p1"] < 0.05) and (b_["xbar"]["r1"] > 0 and b_["xbar"]["p1"] < 0.10)
P2 = (a["trail"]["diff"] > 0 and a["trail"]["t"] >= 2) and (b_["trail"]["diff"] > 0 and b_["trail"]["t"] >= 1.5)
say(f"- H3a x̄ lag1>0（在 p<0.05 ∧ 外 p<0.10）: 在 r {a['xbar']['r1']:+.3f} p {a['xbar']['p1']:.3f}／外 r {b_['xbar']['r1']:+.3f} p {b_['xbar']['p1']:.3f} → {'PASS' if P1 else 'FAIL'}")
say(f"- H3b trailing 4 週 2 群差>0（在 t≥2 ∧ 外 t≥1.5）: 在 {100*a['trail']['diff']:+.2f} pp t {a['trail']['t']:+.2f}／外 {100*b_['trail']['diff']:+.2f} pp t {b_['trail']['t']:+.2f} → {'PASS' if P2 else 'FAIL'}")
say(f"- MDE: 週 σ_μ 95% 上限 在 {100*a['sig_up']:.2f} pp／外 {100*b_['sig_up']:.2f} pp；置換帰無 95% 点 r 在 {a['xbar']['q95']:+.3f}／外 {b_['xbar']['q95']:+.3f}")
say(f"\n**結論: {'H3 支持（超過到達率に週次持続あり・反証レーンへ）' if (P1 and P2) else 'H3 null（RW 基準に対する超過 TP 到達率は週次で持続しない／検出できない・MDE 併記）'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
