# -*- coding: utf-8 -*-
"""
[cycle7 研究レーン] 2026-11-05 — 【深化・出口/path】再加速の出口過程は「現在の含み R」だけで決まるか、
「建玉からの経過時間」に情報があるか（持続時間依存 duration dependence＝“停滞した本は腐る”仮説）

=== 事前固定（この docstring を書いてから数字を見る） ===
問い: 価格がマルチンゲールなら、足 k の終値時点で建玉中の本について E[R* | F_k] = cl_k（含み R）であり、
      k（経過時間）も cl_k の水準も期待値に影響しない。反証レーン 05:20 Q4' は固定 k・全ポジション pooled で
      e' = R* − cl_k ≈ 0（|t|≤1.1）を確認済み。本サイクルは pooled null の裏に**相殺するセル**が隠れていないかを
      「経過時間 k × 含み R の水準」の格子で見る。経済仮説（stall decay）: 壁→壁は始動したら走り、
      長く建玉して含みが 0 近傍に停滞した本は、壁へ戻る（e<0）。走っている本（含み +）は時間に依らず e≈0。
      これは入口フィルタでも TP/SL 変更でもない。出口 path の構造記述。昇格提案はしない。
データ: data/c1_reaccel_paths_2010_2026.json（19404 本・entry_time ソート）＋ data/refute_c2_fullpaths.npz
      （同順・切断なし・index0 = 建玉足・長さ hold+1）＋ refute_c4 json（b）。scan 無し・M5 読込なし・MT5 なし。
記帳の公正化（backlog ①②③）: R* = R + ft（SL/TP）・TIME はそのまま。評価足 k は hold>k（決着足と混ぜない）。
      対照は固定 k・F_k 可測条件のみ（cl_k の水準は k 終値で判明）。bar0 は約定前レンジ混入のため k≥3。
格子: k ∈ {3, 6, 12, 24, 48, 96} × 含み水準 B1 cl_k≤−0.5 / B2 (−0.5,−0.2] / B3 (−0.2,+0.2) / B4 [+0.2,+0.5) / B5 ≥+0.5。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 水準は近年窓で、長期は幾何の帰無検定のみ）。
統計: e = R* − cl_k の平均・paired t（本等重み）。頑健性: 建玉日（UTC）クラスタ SE。
予測（stall decay が本物なら）:
  P1 停滞セル (k=24, B3): e<0 で 在 t≤−2 ∧ 外 t≤−1.5。
  P2 B3 内の時間依存: e(k≥24, B3) − e(k≤6, B3) <0（Welch）で 在 t≤−2 ∧ 外 t≤−1.5。
  探索格子: 30 セル/窓は Bonferroni α=0.05/30。名目 |t|>2 のセル数 vs 期待 1.5。
合否: H 支持 = P1 ∧ P2。それ以外 = null（経過時間に出口情報なし／MDE 以下）。
MDE（20:25 教訓 c）: P1 セルの最小検出効果 = 2·sd/√n、および δ∈{0.05,0.10}R を注入した時の t（注入は決定論的）。
陽性対照（同じ信頼性クラス・20:25 教訓 b）: 公正化しない e_raw = e − ft·1{SL/TP} は既知の −ft≈−0.02R シフトを持つ。
      大セルで e_raw が t≪−2 になることを確認＝0.02R 級のシフトをこの量で拾える。
ベースライン: マルチンゲール e=0（k・水準に依らず）。
事前の最重要反証: (1) 同時刻の重複建玉で本が独立でない → クラスタ SE。(2) 停滞本は b が大きい（遠い TP）集合に
      偏るが、マルチンゲールなら b に依らず E[e]=0 なので幾何は e に効かない。(3) 格子 30×3 の事後選択 → Bonferroni。
      (4) 水準ビンは cl_k で切るため SL 近傍（B1）は決着直前の本が多く残り保有が短い＝セル間の n/sd 差は大きい（記述）。
昇格候補ではない。seed 不要（置換なし）。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c7_duration_dependence_result.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)

def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 3: return np.nan, np.nan
    se = d.std(ddof=1) / math.sqrt(n)
    t = d.mean() / se if se > 0 else np.nan
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else np.nan
    return t, p

def t_cluster(d, g):
    """クラスタ頑健 t（クラスタ内合計の分散）"""
    d = np.asarray(d, float); m = d.mean(); r = d - m
    s = pd.Series(r).groupby(np.asarray(g)).sum().to_numpy()
    se = math.sqrt((s ** 2).sum()) / len(d)
    return m / se if se > 0 else np.nan, len(s)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, diff / se if se > 0 else np.nan

# ---------- load ----------
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
bmap = {t["entry_time"]: t["b"] for t in c4["trades"]}
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
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
day = (df.entry_time.to_numpy() // 86400)
W = {"在2010-20": (df.year <= 2020).to_numpy(), "外2021-26": (df.year >= 2021).to_numpy(), "近年2024-26": (df.year >= 2024).to_numpy()}
KS = (3, 6, 12, 24, 48, 96)
BINS = [("B1 ≤−0.5", -np.inf, -0.5), ("B2 (−0.5,−0.2]", -0.5, -0.2), ("B3 (−0.2,+0.2)", -0.2, 0.2), ("B4 [+0.2,+0.5)", 0.2, 0.5), ("B5 ≥+0.5", 0.5, np.inf)]
def binmask(x, lo, hi, name):
    if name.startswith("B1"): return x <= -0.5
    if name.startswith("B2"): return (x > -0.5) & (x <= -0.2)
    if name.startswith("B3"): return (x > -0.2) & (x < 0.2)
    if name.startswith("B4"): return (x >= 0.2) & (x < 0.5)
    return x >= 0.5

say(f"# [cycle7] 出口過程の持続時間依存（k × 含み R 格子の e = R* − cl_k）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c7_duration_dependence.py)")
say(f"n={n} 本 2010-01..2026-06、FEED_TOL={FT}、ft 平均 {ft.mean():.4f}R、SL/TP {is_slt.sum()}・TIME {(~is_slt).sum()}。R* 平均 {Rstar.mean():+.4f}（gross R {R.mean():+.4f}）。")
say(f"建玉中本数（hold>k）: " + " / ".join(f"k={k}: {(hold > k).sum()}" for k in KS))
say()

# ---------- per-k arrays ----------
E = {}   # k -> (idx_alive, cl_k, e)
for k in KS:
    alive = np.nonzero(hold > k)[0]
    clk = clR[off[alive] + k]
    E[k] = (alive, clk, Rstar[alive] - clk)

# ---------- 0. pooled replication (Q4') + positive control ----------
say("## 0. 固定 k・全水準 pooled（反証 05:20 Q4' の再現）と陽性対照（公正化なし e_raw の既知シフト −ft）")
say("| 窓 | k | n | e mean / t | クラスタ t (日数) | e_raw mean / t（既知 ≈ −ft·P(SL/TP)） | 期待シフト −ft·P |")
say("|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    for k in KS:
        alive, clk, e = E[k]; m = wm[alive]
        if m.sum() < 30: continue
        er = e[m] - ft[alive][m] * is_slt[alive][m]
        tc, nd = t_cluster(e[m], day[alive][m])
        say(f"| {wn} | {k} | {m.sum()} | {e[m].mean():+.4f} / {tstat(e[m])[0]:+.2f} | {tc:+.2f} ({nd}) | {er.mean():+.4f} / {tstat(er)[0]:+.2f} | {-(ft[alive][m] * is_slt[alive][m]).mean():+.4f} |")
say()

# ---------- 1. grid ----------
say("## 1. 格子 k × 含み水準 B（e mean / paired t / n）— Bonferroni α=0.05/30=0.00167（|t|≥3.14）")
cells = {}
for wn, wm in W.items():
    say(f"### {wn}")
    say("| k \\ B | " + " | ".join(b[0] for b in BINS) + " |")
    say("|---|" + "---|" * len(BINS))
    for k in KS:
        alive, clk, e = E[k]; row = []
        for name, lo, hi in BINS:
            m = wm[alive] & binmask(clk, lo, hi, name)
            if m.sum() < 30:
                row.append(f"n={m.sum()}"); cells[(wn, k, name)] = (np.nan, np.nan, m.sum(), np.nan); continue
            t, p = tstat(e[m]); tc, _ = t_cluster(e[m], day[alive][m])
            cells[(wn, k, name)] = (e[m].mean(), t, m.sum(), tc)
            row.append(f"{e[m].mean():+.3f} / {t:+.2f} / {m.sum()}")
        say(f"| k={k} | " + " | ".join(row) + " |")
    ts = np.array([v[1] for kk, v in cells.items() if kk[0] == wn and not np.isnan(v[1])])
    say(f"セル数 {len(ts)}・名目 |t|>2: **{(np.abs(ts) > 2).sum()}**（期待 {0.0455 * len(ts):.1f}）・Bonferroni 有意 **{(np.abs(ts) >= 3.14).sum()}**・max|t| {np.abs(ts).max():.2f}・t の sd {ts.std(ddof=1):.2f}（帰無 ≈1）")
    say()

# ---------- 2. P1 / P2 ----------
say("## 2. 事前固定の判定セル")
say("| 窓 | P1 (k=24,B3) e / t / クラスタ t / n | k=48,B3 e / t / n | P2 e(k≥24,B3) − e(k≤6,B3) diff / Welch t / n | MDE(2·sd/√n) P1 | 注入 δ=−0.05 → t | δ=−0.10 → t |")
say("|---|---|---|---|---|---|---|")
P = {}
for wn, wm in W.items():
    def cellvals(k):
        alive, clk, e = E[k]; m = wm[alive] & binmask(clk, -0.2, 0.2, "B3"); return e[m], day[alive][m]
    e24, d24 = cellvals(24); e48, _ = cellvals(48); e96, _ = cellvals(96); e3, _ = cellvals(3); e6, _ = cellvals(6)
    t24, p24 = tstat(e24); tc24, _ = t_cluster(e24, d24); t48, _ = tstat(e48)
    late = np.concatenate([e24, e48, e96]); early = np.concatenate([e3, e6])
    dd, tw = welch(late, early)
    sd = e24.std(ddof=1); mde = 2 * sd / math.sqrt(len(e24))
    tin5 = tstat(e24 - 0.05)[0]; tin10 = tstat(e24 - 0.10)[0]
    P[wn] = dict(e24=e24.mean(), t24=t24, tc24=tc24, n24=len(e24), dd=dd, tw=tw, mde=mde)
    say(f"| {wn} | {e24.mean():+.4f} / {t24:+.2f} / {tc24:+.2f} / {len(e24)} | {e48.mean():+.4f} / {t48:+.2f} / {len(e48)} | {dd:+.4f} / {tw:+.2f} / {len(late)}:{len(early)} | {mde:.3f}R | {tin5:+.2f} | {tin10:+.2f} |")
say("（注入 = 停滞セルの全本に δ の負ドリフトがあった場合の t。t≤−2 になる δ が検出可能サイズ。）")
say()

# ---------- 3. descriptive: what stalled trades become ----------
say("## 3. 記述: k=24 で建玉中の本の行き先（水準別）— 幾何の確認・判定不使用")
say("| 窓 | B | n | 最終 SL% / TP% / TIME% | 残り保有 中央値 | b 中央値 | 最終 R* 平均 | cl_k 平均 |")
say("|---|---|---|---|---|---|---|---|")
alive, clk, e = E[24]
for wn, wm in W.items():
    for name, lo, hi in BINS:
        m = wm[alive] & binmask(clk, lo, hi, name)
        if m.sum() < 30: continue
        ex = df.exit_reason.to_numpy()[alive][m]
        say(f"| {wn} | {name} | {m.sum()} | {100*(ex=='SL').mean():.0f} / {100*(ex=='TP').mean():.0f} / {100*(ex=='TIME').mean():.0f} | {np.median(hold[alive][m] - 24):.0f} | {np.nanmedian(df.b.to_numpy()[alive][m]):.2f} | {Rstar[alive][m].mean():+.3f} | {clk[m].mean():+.3f} |")
say()

# ---------- 4. side split of P1 cell (description) ----------
say("## 4. 記述: P1 セル (k=24,B3) の側別・壁種別（判定不使用）")
side = df.side.to_numpy(); wk = df.wall_kind.to_numpy()
for wn, wm in W.items():
    alive, clk, e = E[24]; m = wm[alive] & binmask(clk, -0.2, 0.2, "B3")
    parts = []
    for lab, mm in (("BUY", side[alive] == "BUY"), ("SELL", side[alive] == "SELL"), ("outer", wk[alive] == "outer"), ("mid", wk[alive] == "mid")):
        q = m & mm
        if q.sum() >= 30: parts.append(f"{lab} {e[q].mean():+.3f} (t{tstat(e[q])[0]:+.2f}, n{q.sum()})")
    say(f"- {wn}: " + "；".join(parts))
say()

# ---------- verdict ----------
say("## 判定（事前規則）")
a, b_ = P["在2010-20"], P["外2021-26"]
P1 = (a["e24"] < 0 and a["t24"] <= -2) and (b_["e24"] < 0 and b_["t24"] <= -1.5)
P2 = (a["dd"] < 0 and a["tw"] <= -2) and (b_["dd"] < 0 and b_["tw"] <= -1.5)
say(f"- P1 停滯セル e<0（在 t≤−2 ∧ 外 t≤−1.5）: 在 {a['e24']:+.4f} t {a['t24']:+.2f} / 外 {b_['e24']:+.4f} t {b_['t24']:+.2f} → {'PASS' if P1 else 'FAIL'}")
say(f"- P2 B3 内 late−early <0（在 t≤−2 ∧ 外 t≤−1.5）: 在 {a['dd']:+.4f} t {a['tw']:+.2f} / 外 {b_['dd']:+.4f} t {b_['tw']:+.2f} → {'PASS' if P2 else 'FAIL'}")
say(f"- MDE（P1 セル・2sd/√n）: 在 {a['mde']:.3f}R / 外 {b_['mde']:.3f}R / 近年 {P['近年2024-26']['mde']:.3f}R")
say(f"\n**H（stall decay）= P1∧P2 → {'支持' if (P1 and P2) else 'null（経過時間に出口情報なし・MDE 以下）'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
