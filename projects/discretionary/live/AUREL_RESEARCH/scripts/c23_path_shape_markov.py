# -*- coding: utf-8 -*-
"""
[cycle23 研究レーン] 2026-11-09 — 【深化・出口/path】出口過程は「現在の含み R（cl_k）」だけのマルコフか、
path の“形”（これまでの揺れの大きさ・含み益で過ごした時間の割合）に出口情報があるか

=== 事前固定（この docstring を書いてから数字を見る） ===
背景: cycle7（経過時間 k）・cycle21（ET 時計）・cycle2（+1.0R 到達後の建値戻り）は全部 null で、研究レーンは
      「出口過程は cl_k だけのマルコフ」と書いた。憲章 1-2（自分の結論を疑う）に従い、F_k 可測で cl_k と独立な
      path の形の変数 2 つで同じ量 e = R* − cl_k を条件づけ、マルコフ性の主張を壊しに行く。
      入口フィルタではない・TP/SL 変更でもない・昇格提案ではない。出口 path の構造記述。
データ: data/c1_reaccel_paths_2010_2026.json（19404 本・entry_time ソート）＋ data/refute_c2_fullpaths.npz
      （同順・切断なし・index0 = 建玉足・長さ hold+1）。scan 無し・M5 読込なし・MT5 無し・外部通信なし。
記帳の公正化（方法論 ①②③）: R* = R + ft（SL/TP）・TIME はそのまま。評価足 k は hold>k（決着足と混ぜない）。
      条件は k 終値で判明する量のみ（look-ahead なし）。
状態変数（足 j=1..k の終値 cl_j・R 単位）:
  V_k = sqrt(mean_j (cl_j − cl_{j−1})²)  … path の実現ボラ（1 足あたり・R 単位・“揺れの大きさ”）
  O_k = mean_j 1{cl_j > 0}                … 含み益で過ごした足の割合（占有時間・“勝っていた本か”）
格子: k ∈ {12, 24}（主 k=24・副 k=12）× 含み水準ビン B1 ≤−0.5 / B2 (−0.5,−0.2] / B3 (−0.2,+0.2) / B4 [+0.2,+0.5) / B5 ≥+0.5
      （cycle7 と同じ）。三分位は (窓, k, B) 内で切る＝cl_k の水準と幾何を揃えた上での形の比較。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 長期は幾何の帰無検定のみ・edge 判定に不使用）。
統計: e の平均・t（本等重み）・建玉日クラスタ t。差は Welch t。
      プール: e を (窓,k,B) 内で demean し、三分位内 demean した z(V)・z(O) に回帰 → β_V・β_O（窓別・日クラスタ t）。
予測（“形”に情報がある場合）:
  H_V（揺れ）: 停滞セル (k=24, B3) で top 三分位 V − bottom 三分位 V の e 差 ΔV。方向は事前に決めない（両側）が、
      PASS は 在 |t|≥2 ∧ 外 同符号 |t|≥1.5 ∧ β_V が在外同符号。
  H_O（占有時間・“利を吐いた本は腐る”伝承）: 停滞セル (k=24, B3) で top O − bottom O の e 差 ΔO <0 を予測。
      PASS は 在 t≤−2 ∧ 外 t≤−1.5 ∧ β_O 在外とも <0。
  探索格子: 2 変数 × 2 k × 5 B × 3 窓 = 60 セル（差）は Bonferroni α=0.05/60（|t|≥3.0）で数えるだけ。
合否: どちらかが PASS なら「cl_k 以外に出口情報あり（構造記述・反証レーンへ）」。両方 FAIL なら null（MDE 併記）。
MDE: 主セルの top−bottom 差の 2·se_Welch、および δ=−0.05/−0.10R を top 三分位に注入した時の Welch t。
陽性対照（同じ信頼性クラス）: 公正化しない e_raw = e − ft·1{SL/TP} の既知 −ft シフトが大セルで t≪−2（cycle7 と同じ）。
ベースライン: マルチンゲール（E[e|F_k]=0 → ΔV=ΔO=β=0）。
事前の最重要反証: (1) V_k は hold>k の生存条件と絡む（揺れが大きいのに生きている＝SL/TP から遠い＝b・risk が違う）→
      幾何（b・risk・残り保有）を三分位別に印字し、β は B 固定効果で水準を揃える。マルチンゲールなら幾何は e に効かない。
      (2) O_k と cl_k の相関（B3 内でも cl の符号と O は相関）→ 三分位内の cl_k 平均を印字し差が 0.05R 超なら注記。
      (3) 60 セルの事後選択 → Bonferroni・主セルは 2 つだけ。(4) 同時刻重複 → 日クラスタ t。
昇格候補ではない。seed 不要（置換なし）。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c23_path_shape_markov_result.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)

def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 3: return np.nan, np.nan
    se = d.std(ddof=1) / math.sqrt(n)
    t = d.mean() / se if se > 0 else np.nan
    return t, (2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else np.nan)

def t_cluster(d, g):
    d = np.asarray(d, float); m = d.mean(); r = d - m
    s = pd.Series(r).groupby(np.asarray(g)).sum().to_numpy()
    se = math.sqrt((s ** 2).sum()) / len(d)
    return (m / se if se > 0 else np.nan), len(s)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, (diff / se if se > 0 else np.nan), se

def ols_cluster(y, x, g):
    """y ~ x（切片なし・両方 demean 済み）・クラスタ頑健 t"""
    y = np.asarray(y, float); x = np.asarray(x, float)
    sxx = (x * x).sum()
    if sxx <= 0: return np.nan, np.nan
    beta = (x * y).sum() / sxx
    u = y - beta * x
    s = pd.Series(x * u).groupby(np.asarray(g)).sum().to_numpy()
    se = math.sqrt((s ** 2).sum()) / sxx
    return beta, (beta / se if se > 0 else np.nan)

# ---------- load ----------
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
bmap = {t["entry_time"]: t["b"] for t in c4["trades"]}
df["b"] = df.entry_time.map(bmap)
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; off = z["off"]
n = len(df)
assert len(off) - 1 == n, "npz 本数不一致"
assert np.all(np.diff(off) == df.hold.to_numpy() + 1), "path 長 ≠ hold+1"
risk = df.risk.to_numpy(); ft = FT / risk; R = df.R.to_numpy(); hold = df.hold.to_numpy()
is_slt = df.exit_reason.isin(["SL", "TP"]).to_numpy()
Rstar = R + ft * is_slt
day = df.entry_time.to_numpy() // 86400
year = df.year.to_numpy()
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
KS = (24, 12)
BINS = ["B1 ≤−0.5", "B2 (−0.5,−0.2]", "B3 (−0.2,+0.2)", "B4 [+0.2,+0.5)", "B5 ≥+0.5"]
def binidx(x):
    return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))

say(f"# [cycle23] 出口過程のマルコフ性 vs path の形（V_k 実現ボラ・O_k 占有時間）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c23_path_shape_markov.py)")
say(f"n={n} 本 2010-01..2026-06、FEED_TOL={FT}、ft 平均 {ft.mean():.4f}R、SL/TP {is_slt.sum()}・TIME {(~is_slt).sum()}。R* 平均 {Rstar.mean():+.4f}（gross {R.mean():+.4f}）。")
say(f"建玉中本数（hold>k）: " + " / ".join(f"k={k}: {(hold > k).sum()}" for k in KS))
say()

# ---------- state variables ----------
S = {}
for k in KS:
    alive = np.nonzero(hold > k)[0]
    idx = off[alive][:, None] + np.arange(0, k + 1)[None, :]       # (n_alive, k+1) index 0..k
    P = clR[idx]                                                    # cl_0..cl_k
    d = np.diff(P, axis=1)                                          # k 本の Δcl
    V = np.sqrt((d ** 2).mean(axis=1))
    O = (P[:, 1:] > 0).mean(axis=1)
    clk = P[:, -1]
    e = Rstar[alive] - clk
    S[k] = dict(alive=alive, clk=clk, e=e, V=V, O=O, b=binidx(clk))

# ---------- 0. 記述: 状態変数の分布・cl_k との相関・陽性対照 ----------
say("## 0. 状態変数の分布（B3 セル）・cl_k との相関・陽性対照（e_raw の既知 −ft シフト）")
say("| 窓 | k | n(B3) | V 中央値 (p10/p90) | O 中央値 (p10/p90) | ρ(V,cl_k) B3 | ρ(O,cl_k) B3 | ρ(V,O) B3 | e_raw mean / t（B3） | 期待 −ft·P |")
say("|---|---|---|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    for k in KS:
        s = S[k]; m = wm[s["alive"]] & (s["b"] == 2)
        if m.sum() < 30: continue
        V, O, c, e = s["V"][m], s["O"][m], s["clk"][m], s["e"][m]
        er = e - ft[s["alive"]][m] * is_slt[s["alive"]][m]
        say(f"| {wn} | {k} | {m.sum()} | {np.median(V):.3f} ({np.percentile(V,10):.3f}/{np.percentile(V,90):.3f}) | {np.median(O):.2f} ({np.percentile(O,10):.2f}/{np.percentile(O,90):.2f}) | {np.corrcoef(V,c)[0,1]:+.2f} | {np.corrcoef(O,c)[0,1]:+.2f} | {np.corrcoef(V,O)[0,1]:+.2f} | {er.mean():+.4f} / {tstat(er)[0]:+.2f} | {-(ft[s['alive']][m]*is_slt[s['alive']][m]).mean():+.4f} |")
say()

# ---------- 1. 三分位（窓,k,B 内）top − bottom の差 ----------
say("## 1. 形の三分位（(窓,k,B) 内で切る）: e(top) − e(bottom)（Welch）— 60 セル Bonferroni |t|≥3.0")
cells = []
PRIM = {}
for var in ("V", "O"):
    say(f"### 変数 {var}（{'実現ボラ' if var=='V' else '占有時間'}）: diff / Welch t / n_top:n_bot ／ [top 三分位の cl_k 平均 − bottom の cl_k 平均]")
    say("| 窓 | k | " + " | ".join(BINS) + " |")
    say("|---|---|" + "---|" * len(BINS))
    for wn, wm in W.items():
        for k in KS:
            s = S[k]; row = []
            for bi, bn in enumerate(BINS):
                m = wm[s["alive"]] & (s["b"] == bi)
                if m.sum() < 60: row.append(f"n={m.sum()}"); continue
                x = s[var][m]; e = s["e"][m]; c = s["clk"][m]
                q1, q2 = np.quantile(x, [1/3, 2/3])
                top = x >= q2; bot = x <= q1
                dd, tw, se = welch(e[top], e[bot])
                dcl = c[top].mean() - c[bot].mean()
                cells.append((var, wn, k, bn, dd, tw))
                row.append(f"{dd:+.3f} / {tw:+.2f} / {top.sum()}:{bot.sum()} [{dcl:+.3f}]")
                if bi == 2:
                    PRIM[(var, wn, k)] = dict(dd=dd, tw=tw, se=se, ntop=top.sum(), nbot=bot.sum(), dcl=dcl,
                                               etop=e[top], ebot=e[bot], top=top, bot=bot, m=m)
            say(f"| {wn} | k={k} | " + " | ".join(row) + " |")
    say()
ts = np.array([c[5] for c in cells if not np.isnan(c[5])])
say(f"セル数 {len(ts)}・名目 |t|>2: **{(np.abs(ts)>2).sum()}**（期待 {0.0455*len(ts):.1f}）・Bonferroni |t|≥3.0: **{(np.abs(ts)>=3.0).sum()}**・max|t| {np.abs(ts).max():.2f}・t の sd {ts.std(ddof=1):.2f}（帰無 ≈1）")
say()

# ---------- 2. プール回帰 β（(窓,k,B) 固定効果・z 内 demean） ----------
say("## 2. プール回帰: e（(k,B) 内 demean）~ z（(k,B) 内で標準化した V または O）— β（R / 1sd）・日クラスタ t・n")
say("| 窓 | 変数 | k=24 β / t / n | k=12 β / t / n | k 両方 β / t / n |")
say("|---|---|---|---|---|")
BETA = {}
for wn, wm in W.items():
    for var in ("V", "O"):
        parts = []; Ys, Xs, Gs = [], [], []
        for k in KS:
            s = S[k]; m = wm[s["alive"]]
            y = s["e"][m].copy(); x = s[var][m].copy(); g = s["b"][m]; dgrp = day[s["alive"]][m]
            for bi in range(5):
                q = g == bi
                if q.sum() < 30: y[q] = np.nan; continue
                y[q] -= y[q].mean(); sd = x[q].std(ddof=1); x[q] = (x[q] - x[q].mean()) / (sd if sd > 0 else 1)
            ok = ~np.isnan(y)
            beta, tb = ols_cluster(y[ok], x[ok], dgrp[ok]); BETA[(wn, var, k)] = (beta, tb)
            parts.append(f"{beta:+.4f} / {tb:+.2f} / {ok.sum()}")
            Ys.append(y[ok]); Xs.append(x[ok]); Gs.append(dgrp[ok])
        beta, tb = ols_cluster(np.concatenate(Ys), np.concatenate(Xs), np.concatenate(Gs)); BETA[(wn, var, "all")] = (beta, tb)
        parts.append(f"{beta:+.4f} / {tb:+.2f} / {sum(len(y) for y in Ys)}")
        say(f"| {wn} | {var} | " + " | ".join(parts) + " |")
say("（k=12 と k=24 は同じ本が重複し得るので「k 両方」は日クラスタ t だけ参照。）")
say()

# ---------- 3. 主セルの幾何（反証 (1)(2)）と MDE・注入 ----------
say("## 3. 主セル (k=24, B3) 三分位の幾何（b・risk・残り保有・決着内訳）・MDE・注入")
say("| 窓 | 変数 | 群 | n | e mean / t | cl_k 平均 | b 中央値 | risk 中央値 (USD) | 残り保有 中央値 | SL% / TP% / TIME% |")
say("|---|---|---|---|---|---|---|---|---|---|")
s = S[24]
for wn in W:
    for var in ("V", "O"):
        p = PRIM.get((var, wn, 24))
        if p is None: continue
        al = s["alive"][p["m"]]
        for lab, q in (("top", p["top"]), ("bot", p["bot"])):
            ex = df.exit_reason.to_numpy()[al][q]
            say(f"| {wn} | {var} | {lab} | {q.sum()} | {p['e'+lab if False else ('etop' if lab=='top' else 'ebot')].mean():+.4f} / {tstat(p['etop' if lab=='top' else 'ebot'])[0]:+.2f} | {s['clk'][p['m']][q].mean():+.3f} | {np.nanmedian(df.b.to_numpy()[al][q]):.2f} | {np.median(risk[al][q]):.2f} | {np.median(hold[al][q]-24):.0f} | {100*(ex=='SL').mean():.0f} / {100*(ex=='TP').mean():.0f} / {100*(ex=='TIME').mean():.0f} |")
say()
say("| 窓 | 変数 | ΔO/ΔV (top−bot) / Welch t | MDE (2·se) | 注入 δ=−0.05R(top) → t | δ=−0.10R → t |")
say("|---|---|---|---|---|---|")
for wn in W:
    for var in ("V", "O"):
        p = PRIM.get((var, wn, 24))
        if p is None: continue
        t5 = welch(p["etop"] - 0.05, p["ebot"])[1]; t10 = welch(p["etop"] - 0.10, p["ebot"])[1]
        say(f"| {wn} | {var} | {p['dd']:+.4f} / {p['tw']:+.2f} | {2*p['se']:.3f}R | {t5:+.2f} | {t10:+.2f} |")
say()

# ---------- 4. 記述: 側別（判定不使用） ----------
say("## 4. 記述: 主セルの差の側別（判定不使用）")
side = df.side.to_numpy()
for wn, wm in W.items():
    parts = []
    for var in ("V", "O"):
        p = PRIM.get((var, wn, 24))
        if p is None: continue
        al = s["alive"][p["m"]]
        for sd_ in ("BUY", "SELL"):
            q = side[al] == sd_
            dd, tw, _ = welch(p["etop"][q[p["top"]]], p["ebot"][q[p["bot"]]])
            parts.append(f"{var}×{sd_} {dd:+.3f} (t{tw:+.2f}, {q[p['top']].sum()}:{q[p['bot']].sum()})")
    say(f"- {wn}: " + "；".join(parts))
say()

# ---------- verdict ----------
say("## 判定（事前規則）")
a_V, b_V = PRIM[("V", "在2010-20", 24)], PRIM[("V", "外2021-26", 24)]
a_O, b_O = PRIM[("O", "在2010-20", 24)], PRIM[("O", "外2021-26", 24)]
bV_in, bV_out = BETA[("在2010-20", "V", "all")][0], BETA[("外2021-26", "V", "all")][0]
bO_in, bO_out = BETA[("在2010-20", "O", "all")], BETA[("外2021-26", "O", "all")]
HV = (abs(a_V["tw"]) >= 2) and (np.sign(a_V["dd"]) == np.sign(b_V["dd"])) and (abs(b_V["tw"]) >= 1.5) and (np.sign(bV_in) == np.sign(bV_out))
HO = (a_O["dd"] < 0 and a_O["tw"] <= -2) and (b_O["dd"] < 0 and b_O["tw"] <= -1.5) and (bO_in[0] < 0 and bO_out[0] < 0)
say(f"- H_V（揺れ・両側）: 主セル ΔV 在 {a_V['dd']:+.4f} t {a_V['tw']:+.2f} / 外 {b_V['dd']:+.4f} t {b_V['tw']:+.2f}；β_V 在 {bV_in:+.4f} / 外 {bV_out:+.4f} → {'PASS' if HV else 'FAIL'}")
say(f"- H_O（占有時間・ΔO<0 予測）: 主セル ΔO 在 {a_O['dd']:+.4f} t {a_O['tw']:+.2f} / 外 {b_O['dd']:+.4f} t {b_O['tw']:+.2f}；β_O 在 {bO_in[0]:+.4f} (t{bO_in[1]:+.2f}) / 外 {bO_out[0]:+.4f} (t{bO_out[1]:+.2f}) → {'PASS' if HO else 'FAIL'}")
say(f"- MDE（主セル 2·se）: V 在 {2*a_V['se']:.3f}R / 外 {2*b_V['se']:.3f}R；O 在 {2*a_O['se']:.3f}R / 外 {2*b_O['se']:.3f}R")
say(f"\n**結論: {'cl_k 以外に出口情報あり（構造記述・反証レーンへ）' if (HV or HO) else 'null（path の形 V_k・O_k に出口情報なし・MDE 以下）＝出口過程の cl_k マルコフ性は形の変数でも壊れない'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
