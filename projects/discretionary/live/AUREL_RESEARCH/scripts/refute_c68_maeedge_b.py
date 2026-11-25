# -*- coding: utf-8 -*-
"""
[REFUTE c68 — b] 2026-11-25 第 2 走。a 走（refute_c68_maeedge.py）の自己点検と、a 走が見つけた新しい攻撃面。

=== a 走の結果を受けた 2 つの訂正・新攻撃（数字を見る前に固定） ===
自己点検 1（私の攻撃の公正性）: a 走の B1 は θ(8)×B(5)×k(2)×窓(3) = 182 セルを家族として
    p_fw(外) = 0.57 を出し T1 = broken と判定した。**しかし c68 の docstring は θ = −0.8 と B2/B3 を
    数字を見る前に事前宣言している**（「追加・事前宣言（記述）: MAE_k ≤ −0.8 の生存本（B2/B3 で）」）。
    事前宣言された家族は 2 B × 2 k × 3 窓 = 12 セル（外だけなら 4 セル）であって 182 ではない。
    182 セル家族は**私の側の過剰補正**であり、そのまま broken の根拠にするのは不公正。
    → C1: 事前宣言家族（外 4 セル・12 セル）で同じ層別置換 FWER を出し直す。
       **C1 が p ≤ 0.05 なら a 走の B1 発火を取り下げ、多重検定攻撃は失敗と記録する。**
自己点検 2（置換帰無の平均が 0 でない）: a 走で 外 B2 k=24 の置換 t の平均は **+0.275**（sd 0.97）。
    層 = (最細窓, B) で e を置換してもなお正のずれが残るのは、「試した」群が 近年 に偏っている
    （50/106 = 47% vs 残り 109/366 = 30%）一方で 近年 の B2 の平均 e が 外前 より高いから。
    ＝c68 の +0.332R には**窓内の年構成差（collider ではなく単純な層構成）**が混じっている。
    → C5: 層別（最細窓・年）で重み付けした Δ_adj と、置換平均で中心化した t_adj を印字。

新攻撃（a 走 §A8 が暴いた・c68 は §4 の集合で幾何を印字していない）:
A12 幾何 b の不整合: 「試した」群は b（TP 距離・R 単位）が **系統的に大きい**（a 走: 外 1.37 vs 1.15・
    近年 1.74 vs 1.46・在 0.99 vs 0.88）。e = R* − cl_k で TP 決着は R* ≈ +b なので、**b が大きいほど
    e は機械的に大きい**。c68 の事前反証 (2) は「深く沈んで生きている本は SL が遠い（risk 大・b 小）」を
    疑ったが、実際は逆向き（b 大）で、しかも §4 の集合では印字されていない。
    検定: (i) OLS e ~ tested + cl_k + b（日クラスタ se）(ii) b 三分位内でマッチした Δ（セル内層別）
    (iii) 残り上側で正規化した e_norm = e / (b + ft − cl_k)（TP で 1・SL で約 −(1−ft+cl)/(b−cl)）
    (iv) 分解 Δ ≈ ΔP(TP)·b̄ + P̄(TP)·Δb + ΔP(SL)·(−1) + TIME 項。
    **破壊条件 C2: b を統制すると Δ の係数が 50% 以上縮む、または |t| < 1.5。**
    **破壊条件 C3: b 三分位マッチの Δ が 50% 以上縮む。**
A13 ㊶ 型（在 null → 外 正）の帰無発生率: c39 メタは「在 null → 外 |t|≥1.5」が 21% で起きる主型と書いた。
    層別置換で「事前宣言 外 4 セルのどれかが |t|≥2 かつ 対応する 在 セルが |t|<0.5」の確率を直接測る。
    **破壊条件 C4: 帰無発生率 ≥ 0.15。**
A14 risk（USD）の不整合: 近年 5.52 vs 5.10（+8%）。ft = FEED_TOL/risk も違う。risk 三分位内マッチ。
A15 「縁を試した」の代替定義（look-ahead と定義恣意性）: MAE_k ≤ −0.8 は「どこかで −0.8 を割った」。
    代替: (i) 最終足 k で −0.8 を割っている（＝戻っていない）vs 戻した (ii) 割った回数 (iii) 割ってから
    cl_k までの戻り幅 D = cl_k − MAE_k の三分位（c68 が「ほぼ同義」と書いた量を直接）。
    「戻した本が強い」という伝承の中身が本当に「戻り」なのか、単に「深く行った＝高ボラ」なのかを分ける。
A16 ボラ代理の統制（c68 の結論 (2)「深く沈んだ本 = 高ボラ状態の別名」を §4 の集合で検定）:
    建玉後 1..k 足の実現レンジ V_k = mean(hi_j − lo_j) を統制した OLS。V_k を入れると tested の係数は消えるか。
    **消えるなら T1 は「ボラ状態 × 近年の b 拡大」の言い換えで、最悪点の情報ではない。**

判定（事前固定）:
  C1 p ≤ 0.05 → a 走 B1 を取り下げる（多重検定攻撃 失敗）。
  T1 = broken … C2 または C3 または C4 が発火
  T1 = weakened … C5 の構成差のみが有意に効く（Δ_adj が 20% 以上縮むが 50% 未満）かつ C2/C3/C4 非発火
  T1 = survived … C1 非発火（＝家族補正に耐える）かつ C2/C3/C4 非発火かつ A16 で係数が残る
データ: c68 と同一キャッシュのみ。scan/M5/MT5/外部通信/発注/本番書込 なし。seed 20261125b。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
rng = np.random.default_rng(2026112502)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c68_maeedge_b.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se

def norm_sf2(t):
    return 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else np.nan

def ols_cl(y, X, g, names):
    """定数込み OLS・クラスタ頑健 se"""
    y = np.asarray(y, float); X = np.asarray(X, float)
    X = np.column_stack([np.ones(len(y)), X])
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    u = y - X @ beta
    dfm = pd.DataFrame(X * u[:, None]); dfm["g"] = np.asarray(g)
    Sg = dfm.groupby("g").sum().to_numpy()
    V = XtX_inv @ (Sg.T @ Sg) @ XtX_inv
    se = np.sqrt(np.maximum(np.diag(V), 0))
    return dict(zip(["const"] + list(names), zip(beta, beta / np.where(se > 0, se, np.nan))))

# ---------- load (c68 と同一) ----------
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
df["b"] = df.entry_time.map({t["entry_time"]: t["b"] for t in c4["trades"]})
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; hiR = z["hiR"]; loR = z["loR"]; off = z["off"]
n = len(df); exp_hold = np.diff(off) - 1
if not np.all(exp_hold == df.hold.to_numpy()):
    bad = np.nonzero(exp_hold != df.hold.to_numpy())[0]; et = df.entry_time.to_numpy(); order = np.arange(n)
    for p in np.unique(et[bad]):
        grp = np.nonzero(et == p)[0]; want = exp_hold[grp]; have = df.hold.to_numpy()[grp]
        perm = [int(grp[list(have).index(w)]) for w in want]
        assert sorted(perm) == sorted(grp.tolist()); order[grp] = perm
    df = df.iloc[order].reset_index(drop=True)
    assert np.all(np.diff(off) == df.hold.to_numpy() + 1)
risk = df.risk.to_numpy(); ft = FT / risk; R = df.R.to_numpy(); hold = df.hold.to_numpy()
exitr = df.exit_reason.to_numpy(); is_slt = df.exit_reason.isin(["SL", "TP"]).to_numpy()
Rstar = R + ft * is_slt; day = df.entry_time.to_numpy() // 86400
year = df.year.to_numpy(); bb = df.b.to_numpy()
KS = (24, 12); TH = -0.8
BINS = ["B1 ≤−0.5", "B2 (−0.5,−0.2]", "B3 (−0.2,+0.2)", "B4 [+0.2,+0.5)", "B5 ≥+0.5"]
def binidx(x): return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
FINE = np.where(year <= 2020, 0, np.where(year <= 2023, 1, 2))
S = {}
for k in KS:
    alive = np.nonzero(hold > k)[0]
    idx = off[alive][:, None] + np.arange(1, k + 1)[None, :]
    LO = loR[idx]; HI = hiR[idx]; clk = clR[idx][:, -1]
    S[k] = dict(alive=alive, clk=clk, e=Rstar[alive] - clk, MAE=LO.min(axis=1), MFE=HI.max(axis=1),
                b=binidx(clk), V=(HI - LO).mean(axis=1), nbreak=(LO <= TH).sum(axis=1), lastlo=LO[:, -1])

say(f"# [REFUTE c68 b] 事前宣言家族での再評価 ＋ 幾何 b / ボラ V の統制 — {time.strftime('%Y-%m-%d %H:%M')}")
say("(scripts/refute_c68_maeedge_b.py・a 走の自己点検 2 件を含む)")
say()

# ================= C1 事前宣言家族の FWER =================
say("## C1 自己点検: c68 が**事前宣言していた**家族（θ=−0.8・B2/B3・k∈{24,12}・3 窓 = 12 セル）での置換 FWER")
say("a 走の B1 は 182 セル家族（θ も B も動かした）で p_fw(外)=0.57 → broken と判定した。θ と B2/B3 は c68 の docstring にあるので、これは私の過剰補正。")
PRE = [(wn, k, bi) for wn in W for k in KS for bi in (1, 2)]
def cellt(wn, k, bi, Esrc):
    s = S[k]; m = W[wn][s["alive"]] & (s["b"] == bi)
    q = s["MAE"][m] <= TH; e = Esrc[k][m]
    if q.sum() < 20 or (~q).sum() < 20: return np.nan
    return welch(e[q], e[~q])[1]
E0 = {k: S[k]["e"] for k in KS}
obs = {c: cellt(*c, E0) for c in PRE}
obs_out4 = max(abs(obs[c]) for c in PRE if c[0] == "外2021-26" and not np.isnan(obs[c]))
obs_all12 = max(abs(obs[c]) for c in PRE if not np.isnan(obs[c]))
tgt = abs(obs[("外2021-26", 24, 1)])
strata = {}
for k in KS:
    s = S[k]; f = FINE[s["alive"]]
    strata[k] = [np.nonzero((f == fv) & (s["b"] == bi))[0] for fv in (0, 1, 2) for bi in range(5)]
    strata[k] = [i for i in strata[k] if len(i) > 1]
NP = 20000
Ep = {k: S[k]["e"].copy() for k in KS}
mx_out4 = np.empty(NP); mx_all12 = np.empty(NP); tcell = np.empty(NP); pat = np.zeros(NP)
pre_masks = {}
for (wn, k, bi) in PRE:
    s = S[k]; m = W[wn][s["alive"]] & (s["b"] == bi)
    pre_masks[(wn, k, bi)] = (m, s["MAE"] <= TH)
for p in range(NP):
    for k in KS:
        base = S[k]["e"]; e_ = Ep[k]
        for idx in strata[k]: e_[idx] = base[rng.permutation(idx)]
    tt = {}
    for c in PRE:
        m, qg = pre_masks[c]; ee = Ep[c[1]]
        a = ee[m & qg]; b_ = ee[m & ~qg]
        tt[c] = welch(a, b_)[1] if (len(a) >= 20 and len(b_) >= 20) else np.nan
    vo = [abs(tt[c]) for c in PRE if c[0] == "外2021-26" and not np.isnan(tt[c])]
    va = [abs(tt[c]) for c in PRE if not np.isnan(tt[c])]
    mx_out4[p] = max(vo); mx_all12[p] = max(va); tcell[p] = tt[("外2021-26", 24, 1)]
    # ㊶ 型: 外の事前宣言セルのどれかが |t|≥2 かつ 対応する 在 セルが |t|<0.5
    hit = 0
    for k in KS:
        for bi in (1, 2):
            to = tt.get(("外2021-26", k, bi)); ti = tt.get(("在2010-20", k, bi))
            if to is not None and ti is not None and not np.isnan(to) and not np.isnan(ti):
                if abs(to) >= 2 and abs(ti) < 0.5: hit = 1
    pat[p] = hit
p_out4 = (mx_out4 >= tgt).mean(); p_all12 = (mx_all12 >= tgt).mean()
p_cell = (np.abs(tcell) >= tgt).mean()
say(f"- 観測: 主target |t| **{tgt:.2f}**／外 4 セルの max|t| {obs_out4:.2f}／12 セルの max|t| {obs_all12:.2f}")
say(f"- 置換 {NP} 回・単セル両側 p = **{p_cell:.4f}**（置換 t 平均 **{tcell.mean():+.3f}**・sd {tcell.std(ddof=1):.2f}）")
say(f"- **事前宣言 外 4 セル家族の FWER p = {p_out4:.4f}**／12 セル家族（在も含む）FWER p = {p_all12:.4f}")
C1_ok = p_out4 <= 0.05
say(f"\n→ **C1: 事前宣言家族では p_fw(外4) = {p_out4:.4f} → {'≤0.05 ＝ a 走の B1 発火は取り下げ（私の多重検定攻撃は失敗）' if C1_ok else '>0.05 ＝ 家族補正に耐えない'}**")
say(f"- ㊶ 型（事前宣言 外セルのどれかが |t|≥2 ∧ 対応 在 が |t|<0.5）の**帰無発生率 = {pat.mean():.4f}**（c39 メタの 21% と比較）")
C4_fire = pat.mean() >= 0.15
say(f"→ **破壊条件 C4（帰無発生率 ≥0.15）: {'発火' if C4_fire else '非発火'}**")
say()

# ================= C5 構成差（層別調整） =================
say("## C5 置換平均が +0.275 だった理由（窓内の年構成差）と層別調整")
say("| 窓 | Δ 素 | 層別重み Δ_adj（最細窓/年で層別・試した群の重みで平均） | 置換中心化 t_adj | 構成が作る分 |")
say("|---|---|---|---|---|")
C5 = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= TH
    dd, tw, se = welch(e[q], e[~q])
    # 年層別: 各年で Δ_y を出し、試した群の n で重み付け
    yy = year[al]; num = 0.0; den = 0.0
    for y in np.unique(yy):
        a = e[q & (yy == y)]; b_ = e[(~q) & (yy == y)]
        if len(a) >= 3 and len(b_) >= 3: num += len(a) * (a.mean() - b_.mean()); den += len(a)
    dadj = num / den if den > 0 else np.nan
    pm = tcell.mean() if wn == "外2021-26" else 0.0
    C5[wn] = dadj
    say(f"| {wn} | {dd:+.4f} | **{dadj:+.4f}** | {(tw - pm):+.2f} | {dd - dadj:+.4f} |")
say()

# ================= A12 幾何 b の統制 =================
say("## A12 幾何 b の不整合（c68 は §4 の集合で b を印字していない・事前反証 (2) の向きと逆）")
say("| 窓 | 群 | n | b 平均 | b 中央 | risk 平均 | V_k 平均（1..k 足の平均レンジ R） | TP% | SL% | TIME% | e 平均 |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= TH; V = s["V"][m]
    for lab, sl_ in (("試した", q), ("残り", ~q)):
        ex = exitr[al][sl_]
        say(f"| {wn} | {lab} | {sl_.sum()} | {bb[al][sl_].mean():.3f} | {np.nanmedian(bb[al][sl_]):.2f} | {risk[al][sl_].mean():.2f} | {V[sl_].mean():.4f} | {100*(ex=='TP').mean():.0f} | {100*(ex=='SL').mean():.0f} | {100*(ex=='TIME').mean():.0f} | {e[sl_].mean():+.4f} |")
say()
say("### (i) OLS: e ~ tested + cl_k + b (+ V_k)（日クラスタ se・B2 k=24 セル内）")
say("| 窓 | 模型 | β_tested / t | β_cl / t | β_b / t | β_V / t |")
say("|---|---|---|---|---|---|")
A12 = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = (s["MAE"][m] <= TH).astype(float); c = s["clk"][m]; V = s["V"][m]; g = day[al]; bv = bb[al]
    r1 = ols_cl(e, np.column_stack([q]), g, ["tested"])
    r2 = ols_cl(e, np.column_stack([q, c]), g, ["tested", "cl"])
    r3 = ols_cl(e, np.column_stack([q, c, bv]), g, ["tested", "cl", "b"])
    r4 = ols_cl(e, np.column_stack([q, c, bv, V]), g, ["tested", "cl", "b", "V"])
    A12[wn] = (r1["tested"], r3["tested"], r4["tested"])
    say(f"| {wn} | 素 | {r1['tested'][0]:+.4f} / {r1['tested'][1]:+.2f} | — | — | — |")
    say(f"| {wn} | +cl_k | {r2['tested'][0]:+.4f} / {r2['tested'][1]:+.2f} | {r2['cl'][0]:+.3f} / {r2['cl'][1]:+.2f} | — | — |")
    say(f"| {wn} | **+cl_k+b** | **{r3['tested'][0]:+.4f} / {r3['tested'][1]:+.2f}** | {r3['cl'][0]:+.3f} / {r3['cl'][1]:+.2f} | {r3['b'][0]:+.3f} / {r3['b'][1]:+.2f} | — |")
    say(f"| {wn} | **+cl_k+b+V_k** | **{r4['tested'][0]:+.4f} / {r4['tested'][1]:+.2f}** | {r4['cl'][0]:+.3f} / {r4['cl'][1]:+.2f} | {r4['b'][0]:+.3f} / {r4['b'][1]:+.2f} | {r4['V'][0]:+.3f} / {r4['V'][1]:+.2f} |")
sh_b = abs(A12["外2021-26"][1][0] / A12["外2021-26"][0][0])
C2_fire = (sh_b < 0.5) or (abs(A12["外2021-26"][1][1]) < 1.5)
say(f"\n→ 外: β_tested 素 {A12['外2021-26'][0][0]:+.4f} → b 統制後 {A12['外2021-26'][1][0]:+.4f}（残存 {100*sh_b:.0f}%・t {A12['外2021-26'][1][1]:+.2f}）→ **破壊条件 C2: {'発火' if C2_fire else '非発火'}**")
sh_v = abs(A12["外2021-26"][2][0] / A12["外2021-26"][0][0])
say(f"→ 外: +V_k まで統制すると {A12['外2021-26'][2][0]:+.4f}（残存 {100*sh_v:.0f}%・t {A12['外2021-26'][2][1]:+.2f}）＝A16")
say()
say("### (ii) b 三分位内マッチの Δ（セル内で b を 3 層に切り、層内 Δ を試した群の n で加重）")
say("| 窓 | b 層 | n(試):n(残) | b 平均（試/残） | Δ | t |")
say("|---|---|---|---|---|---|")
A12b = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= TH; bv = bb[al]
    qs = np.quantile(bv, [1/3, 2/3]); lay = np.digitize(bv, qs)
    num = 0.0; den = 0.0
    for lv in (0, 1, 2):
        sl_ = lay == lv; a = e[q & sl_]; b_ = e[(~q) & sl_]
        if len(a) < 5 or len(b_) < 5:
            say(f"| {wn} | {lv+1}/3 | {len(a)}:{len(b_)} | n 不足 | | |"); continue
        dd, tw, _ = welch(a, b_)
        num += len(a) * dd; den += len(a)
        say(f"| {wn} | {lv+1}/3 | {len(a)}:{len(b_)} | {bv[q & sl_].mean():.2f} / {bv[(~q) & sl_].mean():.2f} | {dd:+.4f} | {tw:+.2f} |")
    A12b[wn] = num / den if den > 0 else np.nan
    d0 = welch(e[q], e[~q])[0]
    say(f"| {wn} | **加重合計** | | | **{A12b[wn]:+.4f}** | 素 {d0:+.4f} の {100*A12b[wn]/d0:.0f}% |")
d0o = welch(S[24]["e"][W["外2021-26"][S[24]["alive"]] & (S[24]["b"] == 1)][S[24]["MAE"][W["外2021-26"][S[24]["alive"]] & (S[24]["b"] == 1)] <= TH],
            S[24]["e"][W["外2021-26"][S[24]["alive"]] & (S[24]["b"] == 1)][S[24]["MAE"][W["外2021-26"][S[24]["alive"]] & (S[24]["b"] == 1)] > TH])[0]
C3_fire = (A12b["外2021-26"] / d0o) < 0.5
say(f"\n→ 外 b 三分位マッチ Δ {A12b['外2021-26']:+.4f} = 素の {100*A12b['外2021-26']/d0o:.0f}% → **破壊条件 C3: {'発火' if C3_fire else '非発火'}**")
say()
say("### (iii) 残り上側で正規化した e_norm = e / (b + ft − cl_k)（TP 決着 = 1.0・b の違いを割り算で消す）")
say("| 窓 | Δ(e_norm) / t | n(試):n(残) | e_norm(試) | e_norm(残) | 素 Δ(e) の何 % に相当（Δ_norm × 平均分母） |")
say("|---|---|---|---|---|---|")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    den_ = bb[al] + ft[al] - s["clk"][m]
    en = s["e"][m] / den_
    q = s["MAE"][m] <= TH
    dd, tw, _ = welch(en[q], en[~q]); d0 = welch(s["e"][m][q], s["e"][m][~q])[0]
    say(f"| {wn} | {dd:+.4f} / {tw:+.2f} | {q.sum()}:{(~q).sum()} | {en[q].mean():+.4f} | {en[~q].mean():+.4f} | {dd*den_.mean():+.4f}R ＝ 素 {d0:+.3f} の {100*dd*den_.mean()/d0:.0f}% |")
say()
say("### (iv) 分解 Δ ≈ ΔP(TP)·b̄ + P̄(TP)·Δb + ΔP(SL)·(−1+ft) + TIME 項（外 B2 k=24）")
s = S[24]; m = W["外2021-26"][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
e = s["e"][m]; q = s["MAE"][m] <= TH; ex = exitr[al]
pt = [( (ex[sl_]=='TP').mean(), (ex[sl_]=='SL').mean(), (ex[sl_]=='TIME').mean(), bb[al][sl_].mean(), s["clk"][m][sl_].mean()) for sl_ in (q, ~q)]
(ptT, psT, piT, bT, cT), (ptR, psR, piR, bR, cR) = pt
bbar = 0.5 * (bT + bR); ptbar = 0.5 * (ptT + ptR)
term_ptp = (ptT - ptR) * bbar; term_b = ptbar * (bT - bR); term_sl = (psT - psR) * (-1.0)
say(f"- P(TP) 試 {ptT:.3f} vs 残 {ptR:.3f}（差 {ptT-ptR:+.3f}）・b 平均 試 {bT:.3f} vs 残 {bR:.3f}（差 {bT-bR:+.3f}）・P(SL) 試 {psT:.3f} vs 残 {psR:.3f}・P(TIME) 試 {piT:.3f} vs 残 {piR:.3f}")
say(f"- 分解: ΔP(TP)·b̄ = **{term_ptp:+.4f}**／P̄(TP)·Δb = **{term_b:+.4f}**／ΔP(SL)·(−1) = {term_sl:+.4f}／cl_k 差 {-(cT-cR):+.4f} → 合計 {term_ptp+term_b+term_sl-(cT-cR):+.4f}（観測 Δ {welch(e[q],e[~q])[0]:+.4f}）")
say(f"- **「b が大きい」だけで Δ の {100*term_b/welch(e[q],e[~q])[0]:.0f}%**")
say()

# ================= A14 risk マッチ =================
say("## A14 risk（USD）三分位内マッチ")
say("| 窓 | Δ 素 | risk 三分位加重 Δ | 残存 % |")
say("|---|---|---|---|")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= TH; rv = risk[al]
    qs = np.quantile(rv, [1/3, 2/3]); lay = np.digitize(rv, qs)
    num = den = 0.0
    for lv in (0, 1, 2):
        sl_ = lay == lv; a = e[q & sl_]; b_ = e[(~q) & sl_]
        if len(a) < 5 or len(b_) < 5: continue
        num += len(a) * (a.mean() - b_.mean()); den += len(a)
    d0 = welch(e[q], e[~q])[0]
    say(f"| {wn} | {d0:+.4f} | {num/den:+.4f} | {100*(num/den)/d0:.0f}% |")
say()

# ================= A15 定義の恣意性 =================
say("## A15 「縁を試した」の代替定義（戻り D か、単に深く行ったか）")
say("| 窓 | 定義 | n(群) | Δ / t |")
say("|---|---|---|---|")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; A = s["MAE"][m]; lastlo = s["lastlo"][m]; nbk = s["nbreak"][m]; D = s["clk"][m] - A
    defs = [("MAE≤−0.8（c68）", A <= TH),
            ("最終足でも −0.8 以下（戻っていない）", lastlo <= TH),
            ("−0.8 を割ったが最終足は戻した", (A <= TH) & (lastlo > TH)),
            ("−0.8 割りが 2 足以上", nbk >= 2),
            ("戻り D = cl_k−MAE_k 上位 1/3", D >= np.quantile(D, 2/3))]
    for dn, q in defs:
        if q.sum() < 10 or (~q).sum() < 10: say(f"| {wn} | {dn} | {q.sum()} | n 不足 |"); continue
        dd, tw, _ = welch(e[q], e[~q])
        say(f"| {wn} | {dn} | {q.sum()} | {dd:+.4f} / {tw:+.2f} |")
say()

# ================= 判定 =================
say("## 判定（第 2 走・事前固定の規則）")
say(f"- C1（事前宣言家族 FWER p_fw(外4) = {p_out4:.4f}）: **{'a 走の B1 発火を取り下げ' if C1_ok else 'B1 維持'}**")
say(f"- C2（b 統制で 50% 以上縮む or |t|<1.5）: **{'発火' if C2_fire else '非発火'}**（残存 {100*sh_b:.0f}%・t {A12['外2021-26'][1][1]:+.2f}）")
say(f"- C3（b 三分位マッチで 50% 以上縮む）: **{'発火' if C3_fire else '非発火'}**（残存 {100*A12b['外2021-26']/d0o:.0f}%）")
say(f"- C4（㊶ 型の帰無発生率 ≥0.15）: **{'発火' if C4_fire else '非発火'}**（{pat.mean():.3f}）")
v2 = None
if C2_fire or C3_fire or C4_fire: v2 = "broken"
elif not C1_ok: v2 = "broken（家族補正に耐えない）"
else: v2 = "survived（私の攻撃は全部失敗）"
say(f"\n**T1 第 2 走の判定 = {v2}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
