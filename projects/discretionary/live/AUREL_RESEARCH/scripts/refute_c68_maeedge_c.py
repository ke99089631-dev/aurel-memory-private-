# -*- coding: utf-8 -*-
"""
[REFUTE c68 — c] 2026-11-25 第 3 走。2 つの訂正と 1 つの機構分解。

訂正 1（私の a 走 A10 の欠陥・自己申告）: a 走の「検出力曲線」は観測された Δ（在 +0.0475）の**上に** δ を足して
  いたので、報告した数字は「真の効果が δ のときの検出力」ではなく「真の効果が 観測Δ+δ のときの棄却率」だった。
  → 正しく центр 化して再計算（真の効果 = δ ちょうど・観測の中心は 0 に寄せる）＋解析式 Φ(δ/se − 1.96) + Φ(−δ/se − 1.96)。
  目的: c68 が毎サイクル使う「**MDE = 2·se**」という書式が、実は**検出力 50% の点**であって
  「この大きさ以下は見えない」という読み方（検出力 80% の MDE）と 1.75 倍ずれていないかを数値で確定する。
  これは c68 固有ではなく c7/c23/c59/c65/c66 と研究機関全体の書式なので、効けば方法論の訂正になる。

訂正 2（b 走 C1 の閾値の取り違え・自己申告）: a 走の破壊条件 B1 は「p_fw > 0.10」だった。b 走は
  事前宣言家族で p_fw(外4) = 0.0672 を得たが、判定コードに 0.05 を書いていたため「B1 維持 → broken」と出した。
  **a 走の規則どおりなら 0.0672 < 0.10 ＝ B1 非発火**。本走で 3 つの公正な家族の p を並べて確定させる:
  (i) 外 4 セル max|t|  (ii) 事前宣言 12 セル max|t|  (iii) ㊶ 型（外 |t|≥観測 ∧ 対応 在 |t|<0.5）。

新・機構分解 A17: +0.33R は「決着の内訳（TP 多・TIME 少）」だけで出るのか、それとも
  **決着種類の中（TP 本の中・SL 本の中）でも e が違う**のか。
  マルチンゲールの下では混ざり方が変わっても E[e|F_k] = 0 は破れないので、「混ざりだけで +0.33」なら
  それは幾何（バリア距離）と ボラの機械的帰結＝c68 の結論 (2) の言い換えで、方向情報ではない。
  逆に TP 本の中・SL 本の中でも差が残るなら、c68 の「ボラ状態の別名」説明では足りない。
  併せて: TIME 決着本の e（時間切れの値）が群間で違うか。

新 A18: 独立ブロック数。106 本・50 本は何日・何週に散っているか（同日/同週の重複＝実効 n）。

データ: c68 と同一キャッシュのみ。scan/M5/MT5/外部通信/発注/本番書込 なし。seed 固定。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
rng = np.random.default_rng(2026112503)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c68_maeedge_c.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
def PHI(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se

J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
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
        order[grp] = perm
    df = df.iloc[order].reset_index(drop=True)
risk = df.risk.to_numpy(); ft = FT / risk; R = df.R.to_numpy(); hold = df.hold.to_numpy()
exitr = df.exit_reason.to_numpy(); is_slt = df.exit_reason.isin(["SL", "TP"]).to_numpy()
Rstar = R + ft * is_slt; etime = df.entry_time.to_numpy(); day = etime // 86400
year = df.year.to_numpy(); bb = df.b.to_numpy()
def binidx(x): return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
S = {}
for k in (24, 12):
    alive = np.nonzero(hold > k)[0]
    idx = off[alive][:, None] + np.arange(1, k + 1)[None, :]
    LO = loR[idx]; HI = hiR[idx]; clk = clR[idx][:, -1]
    S[k] = dict(alive=alive, clk=clk, e=Rstar[alive] - clk, MAE=LO.min(axis=1), MFE=HI.max(axis=1), b=binidx(clk))
TH = -0.8

say(f"# [REFUTE c68 c] 自己訂正 2 件（検出力の計算式・B1 閾値）＋ 決着内訳の分解 — {time.strftime('%Y-%m-%d %H:%M')}")
say()

# ===== 訂正 1: MDE = 2·se は検出力 50% の点 =====
say("## 訂正 1 — 「MDE = 2·se」は検出力 50% の点（研究機関の書式の訂正・c7/c23/c59/c65/c66/c68 共通）")
say("a 走 A10 は観測 Δ の上に δ を足していた（私の欠陥）。以下は真の効果 = δ ちょうどでの検出力。")
say("| 窓 | 主セル (k=24,B3) se | c68 の MDE=2·se | 検出力 δ=0.04R | 0.10R | 0.20R | 0.30R | 検出力 50% の δ | **検出力 80% の δ** |")
say("|---|---|---|---|---|---|---|---|---|")
NP = 4000
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 2)
    x = s["MAE"][m]; e = s["e"][m]
    q1, q2 = np.quantile(x, [1/3, 2/3]); top = x >= q2; bot = x <= q1
    et_, eb_ = e[top], e[bot]
    _, _, se = welch(et_, eb_)
    # 中心化して真の効果を δ だけにする
    etc = et_ - et_.mean(); ebc = eb_ - eb_.mean()
    pw = []
    for d in (0.04, 0.10, 0.20, 0.30):
        hit = 0
        for i in range(NP):
            ia = rng.integers(0, len(etc), len(etc)); ib = rng.integers(0, len(ebc), len(ebc))
            tt = welch(etc[ia] + d, ebc[ib])[1]
            if abs(tt) > 1.96: hit += 1
        pw.append(hit / NP)
    d50 = 1.96 * se; d80 = 2.802 * se
    say(f"| {wn} | {se:.4f} | {2*se:.3f}R | {pw[0]:.2f} | {pw[1]:.2f} | {pw[2]:.2f} | {pw[3]:.2f} | {d50:.3f}R | **{d80:.3f}R** |")
say()
say("解析式の確認（正規近似・両側 0.05）: 検出力 = Φ(δ/se − 1.96) + Φ(−δ/se − 1.96)。δ = 2·se → **0.52**。")
say("→ c68 の「MDE 在 0.11R／外 0.20R」は「**50% の確率で見える大きさ**」であって「これ以下は見えない」ではない。")
say("→ 検出力 80% で言える MDE は 在 **0.157R**／外 **0.280R** 級（下表の 2.802·se）＝c68 が引いた射程より 1.4 倍広い。")
say("→ c29 の「条件づけで実現し得る |Δμ| ≤0.04R」に対する検出力は **0.05〜0.11**（≒検定の大きさそのもの）。")
say()

# ===== 訂正 2: 3 つの公正な家族の p（b 走の 0.05/0.10 取り違えの確定） =====
say("## 訂正 2 — 公正な家族 3 通りの FWER（a 走の破壊条件は p_fw > 0.10 だった）")
PRE = [(wn, k, bi) for wn in W for k in (24, 12) for bi in (1, 2)]
FINE = np.where(year <= 2020, 0, np.where(year <= 2023, 1, 2))
strata = {}
for k in (24, 12):
    s = S[k]; f = FINE[s["alive"]]
    st = [np.nonzero((f == fv) & (s["b"] == bi))[0] for fv in (0, 1, 2) for bi in range(5)]
    strata[k] = [i for i in st if len(i) > 1]
pre_masks = {}
for (wn, k, bi) in PRE:
    s = S[k]; pre_masks[(wn, k, bi)] = (W[wn][s["alive"]] & (s["b"] == bi), s["MAE"] <= TH)
def tcells(Esrc):
    out = {}
    for c in PRE:
        m, qg = pre_masks[c]; ee = Esrc[c[1]]
        a = ee[m & qg]; b_ = ee[m & ~qg]
        out[c] = welch(a, b_)[1] if (len(a) >= 20 and len(b_) >= 20) else np.nan
    return out
obs = tcells({k: S[k]["e"] for k in (24, 12)})
tgt = abs(obs[("外2021-26", 24, 1)])
NPM = 20000
Ep = {k: S[k]["e"].copy() for k in (24, 12)}
m4 = np.empty(NPM); m12 = np.empty(NPM); pat = np.zeros(NPM); tc1 = np.empty(NPM)
for p in range(NPM):
    for k in (24, 12):
        base = S[k]["e"]; e_ = Ep[k]
        for idx in strata[k]: e_[idx] = base[rng.permutation(idx)]
    tt = tcells(Ep)
    vo = [abs(tt[c]) for c in PRE if c[0] == "外2021-26" and not np.isnan(tt[c])]
    va = [abs(tt[c]) for c in PRE if not np.isnan(tt[c])]
    m4[p] = max(vo); m12[p] = max(va); tc1[p] = tt[("外2021-26", 24, 1)]
    h = 0
    for k in (24, 12):
        for bi in (1, 2):
            to = tt.get(("外2021-26", k, bi)); ti = tt.get(("在2010-20", k, bi))
            if to is not None and ti is not None and not np.isnan(to) and not np.isnan(ti) and abs(to) >= tgt and abs(ti) < 0.5: h = 1
    pat[p] = h
say(f"- 単セル（外 B2 k=24）観測 |t| {tgt:.2f} → 層別置換 両側 p = **{(np.abs(tc1)>=tgt).mean():.4f}**（置換 t 平均 {tc1.mean():+.3f}＝年構成が作る下駄）")
say(f"- (i) 事前宣言 外 4 セル max|t|: p_fw = **{(m4>=tgt).mean():.4f}**")
say(f"- (ii) 事前宣言 12 セル max|t|（在 を負の対照として読む分も家族に入れる）: p_fw = **{(m12>=tgt).mean():.4f}**")
say(f"- (iii) ㊶ 型（外 の事前宣言セルのどれかが |t|≥{tgt:.2f} ∧ 対応 在 が |t|<0.5）: 帰無発生率 = **{pat.mean():.4f}**")
say(f"\n→ a 走の破壊条件「p_fw > 0.10」に照らすと: (i) {'非発火' if (m4>=tgt).mean()<=0.10 else '発火'}／(ii) {'非発火' if (m12>=tgt).mean()<=0.10 else '発火'}／(iii) {'非発火' if pat.mean()<=0.10 else '発火'}")
say()

# ===== A17 決着内訳の分解 =====
say("## A17 +0.33R は「決着の混ざり」だけか、決着種類の中でも違うか（マルチンゲールの可否）")
say("| 窓 | 群 | n | P(TP)/P(SL)/P(TIME) | e|TP 平均 | e|SL 平均 | e|TIME 平均 | 混ざりだけの予測 Δ | 観測 Δ |")
say("|---|---|---|---|---|---|---|---|---|")
MIX = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= TH; ex = exitr[al]
    rows = {}
    for lab, sl_ in (("試した", q), ("残り", ~q)):
        pr = {t_: (ex[sl_] == t_).mean() for t_ in ("TP", "SL", "TIME")}
        mu = {t_: (e[sl_][ex[sl_] == t_].mean() if (ex[sl_] == t_).sum() >= 3 else np.nan) for t_ in ("TP", "SL", "TIME")}
        rows[lab] = (sl_.sum(), pr, mu)
    # 混ざりだけ: 両群共通の e|type（プール）を使い、確率だけ群で変える
    pool_mu = {t_: e[ex == t_].mean() for t_ in ("TP", "SL", "TIME")}
    mix_pred = sum((rows["試した"][1][t_] - rows["残り"][1][t_]) * pool_mu[t_] for t_ in ("TP", "SL", "TIME"))
    dd = welch(e[q], e[~q])[0]
    MIX[wn] = (mix_pred, dd)
    for lab in ("試した", "残り"):
        nn, pr, mu = rows[lab]
        say(f"| {wn} | {lab} | {nn} | {pr['TP']:.3f}/{pr['SL']:.3f}/{pr['TIME']:.3f} | {mu['TP']:+.3f} | {mu['SL']:+.3f} | {mu['TIME']:+.3f} | {mix_pred:+.4f} | {dd:+.4f} |" if lab == "試した" else f"| {wn} | {lab} | {nn} | {pr['TP']:.3f}/{pr['SL']:.3f}/{pr['TIME']:.3f} | {mu['TP']:+.3f} | {mu['SL']:+.3f} | {mu['TIME']:+.3f} | | |")
say()
say("| 窓 | 混ざりだけの Δ | 観測 Δ | 混ざりで説明できる % | 決着種類内の差（TP 本同士 / SL 本同士）|")
say("|---|---|---|---|---|")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= TH; ex = exitr[al]
    within = []
    for t_ in ("TP", "SL"):
        a = e[q & (ex == t_)]; b_ = e[(~q) & (ex == t_)]
        if len(a) >= 3 and len(b_) >= 3:
            d2, t2, _ = welch(a, b_); within.append(f"{t_} {d2:+.3f} (t{t2:+.2f}, {len(a)}:{len(b_)})")
        else: within.append(f"{t_} n 不足")
    mp, dd = MIX[wn]
    say(f"| {wn} | {mp:+.4f} | {dd:+.4f} | **{100*mp/dd:.0f}%** | " + " / ".join(within) + " |")
say()

# ===== A18 独立ブロック数 =====
say("## A18 独立ブロック数（106 本・50 本の実効的な独立性）")
say("| 窓 | 群 | n | 固有日数 | 固有週数 | 固有月数 | 最大同日本数 | 上位 3 日が占める % |")
say("|---|---|---|---|---|---|---|---|")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    q = s["MAE"][m] <= TH
    for lab, sl_ in (("試した", q), ("残り", ~q)):
        d = day[al][sl_]; wk = etime[al][sl_] // (7 * 86400); mo = pd.to_datetime(etime[al][sl_], unit="s").to_period("M")
        vc = pd.Series(d).value_counts()
        say(f"| {wn} | {lab} | {sl_.sum()} | {len(np.unique(d))} | {len(np.unique(wk))} | {len(set(mo))} | {vc.max()} | {100*vc.head(3).sum()/sl_.sum():.0f}% |")
say()
say(f"実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
