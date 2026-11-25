# -*- coding: utf-8 -*-
"""
[REFUTE c68] 2026-11-25 反証レーン — 対象: cycle68 (06:40) が null 判定の脇に「事後・記述」として
肯定形・|t|≥2 で残した唯一の弱シグナル T1、および c68 の null 主張の射程 T2/T3。

=== 攻撃対象（c68 本文からの引用・数字を見る前に固定） ===
T1 (主target・弱シグナル): B2 (−0.5,−0.2]・k=24 で「逆指値の縁 MAE_k ≤ −0.8R を試して戻った生存本」は
    同セルの残りより残り path e = R*−cl_k が良い: 外 2021-26H1 **+0.332R (Welch t +2.45・n 106:366・TP 34% vs 25%)**／
    近年 2024-26H1 **+0.581R (t +2.48・n 50:109・TP 42% vs 27%)**／在 2010-20 +0.013 (t +0.19・n 225:1058)。
    c68 は「㊶ 型（在 null → 外 正）・前向き 1 セルのみ」と自己格下げしたが、**数字は肯定形で登記されている**。
T2: 「出口過程の cl_k マルコフ性は、F_k 可測の最悪点 MAE_k・最良点 MFE_k でも壊れない（MDE 在 0.11R／外 0.20R）」
T3: 「探索格子 60 セルは 名目 |t|>2 が 4（期待 2.7）・Bonferroni 0・t の sd 1.02 ＝ 帰無の幅」
    （攻撃点: 60 セルは 近年 ⊂ 外・k=12 ⊃ k=24 で重複しており、独立前提の「期待 2.7」と「sd≈1」は
      帰無分布の正しい基準ではない可能性。重複を保存した置換で帰無分布そのものを作る。）

=== 事前固定した攻撃（この docstring を書き終えてから実行・乱数 seed 20261125 固定） ===
再現確認 R0: c68 §4 の 12 セルを独立実装で再計算し、Δ・t・n が c68 の印字と一致するか（一致しなければ以降は無効）。

A1 閾値感度（＝c68 自身の「最も重大な反証 第1」の定量化）: 実口座の逆指値は ask 側・bid の 5 分 low は
    0.1〜0.5 USD（risk 3.4 USD で 0.03〜0.15R）ずれる。これは閾値 θ = −0.8 を ±0.03〜0.15R ぼかすことと同じ。
    θ ∈ {−0.60,−0.65,−0.70,−0.75,−0.80,−0.85,−0.90,−0.95} で 外 B2 k=24 の Δ/t を印字。
    **破壊条件 B2: θ=−0.80 の隣（−0.75 と −0.85）で両方とも |t| < 1.5 になる** → 「縁を試した集合」の定義が
    1 ビン動くと消える＝実口座で識別できない量。
A2 格子の正直な家族: ≤θ 集合の検定は c68 が印字した 12 セル（B2/B3 × k × 3 窓）ではなく
    θ(8) × B(5) × k(2) × 窓(3) = 240 セルの家族から 1 つを読んでいる。全格子の |t| を印字し Holm/Bonferroni。
A3 置換プラセボ（家族単位の正しい p）: 帰無 H0: e ⫫ MAE | (窓, k, B)。窓（在/外前/近年の最細分割）× B_k 内で
    **e を取引レベルで置換**（セル所属・cl_k 水準・窓構成・n を完全保存）。5000 回。
    p_cell = 単セル（外 B2 k=24 θ=−0.8）の片側/両側 p／p_fw = 外窓の θ×B×k 格子（80 セル）の max|t| に対する FWER p。
    **破壊条件 B1: p_fw > 0.10**。
A4 コスト倍: c68 の e は R* = R + ft·1{SL/TP}（記帳公正化）。全本が往復コストを払う現実では
    e_λ = (R + ft·1{SL/TP} − λ·ft) − cl_k。λ ∈ {0 (c68), 1, 2, 3}。λ は SL/TP/TIME 構成比が群間で違うときだけ Δ を動かす。
    **破壊条件 B6: λ=2 で |t| < 1.5**。
A5 クラスタ・ブートストラップ: c68 §4 は素の Welch t しか印字していない（主セルでは日クラスタ t を併記していたのに）。
    建玉日クラスタ Welch t ＋ 移動ブロック・ブートストラップ（ブロック = 建玉日・20 営業日・2000 回）の両側 p。
    **破壊条件 B4: 日クラスタ |t| < 1.5**。
A6 裾依存（憲章 D「優位は少数の大当たりに乗る」の逆用）: 差 +0.33R が少数の e に依存していないか。
    (i) 1 点抜き（最大影響本を落とした |t|）(ii) 両群 5% トリム平均の差 (iii) Mann–Whitney の順位検定
    (iv) e の中央値差。**破壊条件 B5: 最大影響 1 本を落とすと |t| < 1.5**。
A7 別の在外分割（c68 の分割は 近年 ⊂ 外 で「外 +0.33 と 近年 +0.58 の 2 つが支持」は二重計上の疑い）:
    (a) 外前 2021-23 ＝ 外 ∖ 近年 を独立に印字（**破壊条件 B3: 外前の符号が逆 or |t| < 0.5**
        ＝ 外 +0.33 は 近年 50 本だけで、在外の「外で再現」は成立していない）
    (b) 偶数年／奇数年 (c) 全標本を建玉時刻順に 4 等分したブロック別 (d) 在を 2010-15／2016-20 に二分。
A8 機構・構成の印字（マルコフなら幾何は e に効かない・c68 は §4 の集合では印字していない）:
    b・risk・ft・side・年・残り保有・決着内訳（SL/TP/TIME）を「試した」群 vs 残りで印字。
    とくに **SL%** （c68 は TP% しか印字していない）。cl_k 水準差・SL までの距離・TP までの距離。
A9 プラセボ変数: MAE の代わりに (i) 同セル内で時刻シフトした他本の MAE（構造を持つが無関係）
    (ii) 一様乱数 を使って同じ 240 セル格子を走らせ、|t|≥2 の出現率と max|t| を比較。
A10 T2 の射程（検出力曲線）: 主セル (k=24,B3) に真の効果 δ ∈ {−0.02,−0.04,−0.10,−0.20}R を注入したときの
    検出確率（置換 null の 95 分位を閾値に・2000 回）。c29 の「条件づけで実現し得る |Δμ| ≤0.04R」が
    検出できるか。**T2 の射程が狭まる条件: δ=−0.04R の検出力 < 0.30**。
A11 T3 の帰無分布: 60 セル格子（2 変数 × 2 k × 5 B × 3 窓）の「名目 |t|>2 の個数」「t の sd」「max|t|」を
    A3 の置換（窓・B・k の重複を保存）で作り、c68 の観測値 4／1.02／2.36 が帰無のどこに居るか。
    **T3 が壊れる条件: 観測 4 が置換 null の 95 分位を超える（＝「期待 2.7」は重複を無視した過大な基準だった）。**

判定規則（事前固定）:
  T1 = broken … B1 が発火、または B2〜B6 のうち 2 つ以上が発火
  T1 = weakened … B2〜B6 のうち 1 つだけ発火し B1 は非発火
  T1 = survived … B1〜B6 いずれも非発火
  T2/T3 は survived / 射程を狭める / broken の 3 値で A10/A11 の数値をもって判定。

データ: c68 と同一キャッシュのみ（data/c1_reaccel_paths_2010_2026.json・refute_c4_scan_paths・refute_c2_fullpaths.npz）。
  scan 無し・M5 読込なし・MT5 接続なし・外部通信なし・発注なし・本番ファイル書込なし。書込は AUREL_RESEARCH/ 配下のみ。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
SEED = 20261125
rng = np.random.default_rng(SEED)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c68_maeedge.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)

def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 3: return np.nan
    se = d.std(ddof=1) / math.sqrt(n)
    return d.mean() / se if se > 0 else np.nan

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, (diff / se if se > 0 else np.nan), se

def welch_cluster(a, b, ga, gb):
    a = np.asarray(a, float); b = np.asarray(b, float)
    diff = a.mean() - b.mean()
    ra = (a - a.mean()) / len(a); rb = -(b - b.mean()) / len(b)
    s = pd.Series(np.concatenate([ra, rb])).groupby(np.concatenate([ga, gb])).sum().to_numpy()
    se = math.sqrt((s ** 2).sum())
    return (diff / se if se > 0 else np.nan), len(s)

def norm_sf2(t):
    return 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else np.nan

# ---------- load (c68 と同一手順) ----------
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
bmap = {t["entry_time"]: t["b"] for t in c4["trades"]}
df["b"] = df.entry_time.map(bmap)
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; hiR = z["hiR"]; loR = z["loR"]; off = z["off"]
n = len(df)
assert len(off) - 1 == n, "npz 本数不一致"
exp_hold = np.diff(off) - 1
if not np.all(exp_hold == df.hold.to_numpy()):
    bad_pos = np.nonzero(exp_hold != df.hold.to_numpy())[0]
    et = df.entry_time.to_numpy(); order = np.arange(n)
    for p in np.unique(et[bad_pos]):
        grp = np.nonzero(et == p)[0]
        want = exp_hold[grp]; have = df.hold.to_numpy()[grp]
        perm = [int(grp[list(have).index(w)]) for w in want]
        assert sorted(perm) == sorted(grp.tolist())
        order[grp] = perm
    df = df.iloc[order].reset_index(drop=True)
    assert np.all(np.diff(off) == df.hold.to_numpy() + 1), "path 長 ≠ hold+1"
risk = df.risk.to_numpy(); ft = FT / risk; R = df.R.to_numpy(); hold = df.hold.to_numpy()
exitr = df.exit_reason.to_numpy(); is_slt = df.exit_reason.isin(["SL", "TP"]).to_numpy()
Rstar = R + ft * is_slt
day = df.entry_time.to_numpy() // 86400
year = df.year.to_numpy(); bb = df.b.to_numpy(); side = df.side.to_numpy()
KS = (24, 12)
BINS = ["B1 ≤−0.5", "B2 (−0.5,−0.2]", "B3 (−0.2,+0.2)", "B4 [+0.2,+0.5)", "B5 ≥+0.5"]
def binidx(x):
    return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
# 最細分割（置換の層・近年 ⊂ 外 を保存するため）
FINE = np.where(year <= 2020, 0, np.where(year <= 2023, 1, 2))   # 0=在 1=外前2021-23 2=近年2024-26
FINE_NAME = {0: "在2010-20", 1: "外前2021-23", 2: "近年2024-26"}

S = {}
for k in KS:
    alive = np.nonzero(hold > k)[0]
    idx = off[alive][:, None] + np.arange(1, k + 1)[None, :]
    P = clR[idx]; LO = loR[idx]; HI = hiR[idx]
    clk = P[:, -1]
    S[k] = dict(alive=alive, clk=clk, e=Rstar[alive] - clk, MAE=LO.min(axis=1), MFE=HI.max(axis=1), b=binidx(clk))

say(f"# [REFUTE c68] MAE_k ≤ −0.8「逆指値の縁を試して戻った本」の外 +0.33R を壊しにいく — {time.strftime('%Y-%m-%d %H:%M')}")
say(f"(scripts/refute_c68_maeedge.py・seed {SEED}・c68 と同一キャッシュ・scan/M5/MT5/外部通信なし)")
say(f"n={n}・hold>24 {(hold>24).sum()}・hold>12 {(hold>12).sum()}・FEED_TOL {FT}・ft 平均 {ft.mean():.4f}R")
say()

# ================= R0 再現確認 =================
say("## R0 再現確認（c68 §4 の 12 セルを独立実装で再計算）")
say("| 窓 | k | B | n(試):n(残) | Δ | Welch t | c68 の印字 |")
say("|---|---|---|---|---|---|---|")
C68 = {("外2021-26",24,1): (+0.332, +2.45, 106, 366), ("近年2024-26",24,1): (+0.581, +2.48, 50, 109),
       ("在2010-20",24,1): (+0.013, +0.19, 225, 1058), ("在2010-20",24,2): (+0.035, +0.36, None, None),
       ("外2021-26",24,2): (-0.197, -1.64, None, None), ("近年2024-26",24,2): (-0.290, -1.63, None, None)}
repro_ok = True
for wn, wm in W.items():
    for k in KS:
        s = S[k]
        for bi in (1, 2):
            m = wm[s["alive"]] & (s["b"] == bi)
            A = s["MAE"][m]; e = s["e"][m]
            q = A <= -0.8
            if q.sum() < 20 or (~q).sum() < 20:
                say(f"| {wn} | {k} | {BINS[bi]} | {q.sum()}:{(~q).sum()} | n 不足 | | |"); continue
            dd, tw, _ = welch(e[q], e[~q])
            ref = C68.get((wn, k, bi))
            tag = ""
            if ref:
                ok = abs(dd - ref[0]) < 0.004 and abs(tw - ref[1]) < 0.03
                if ref[2]: ok = ok and q.sum() == ref[2] and (~q).sum() == ref[3]
                tag = f"{ref[0]:+.3f} / t{ref[1]:+.2f}" + (f" / {ref[2]}:{ref[3]}" if ref[2] else "") + ("  ✅" if ok else "  ❌不一致")
                repro_ok = repro_ok and ok
            say(f"| {wn} | {k} | {BINS[bi]} | {q.sum()}:{(~q).sum()} | {dd:+.4f} | {tw:+.2f} | {tag} |")
say(f"\n**再現: {'一致（以降の攻撃は有効）' if repro_ok else '不一致 → 攻撃結果は無効'}**")
say()

# 主target セルの材料
TGT = dict(win="外2021-26", k=24, bi=1, th=-0.8)
def cell_arrays(win, k, bi):
    s = S[k]; m = W[win][s["alive"]] & (s["b"] == bi)
    return dict(m=m, al=s["alive"][m], MAE=s["MAE"][m], MFE=s["MFE"][m], e=s["e"][m], clk=s["clk"][m])
T = cell_arrays(TGT["win"], TGT["k"], TGT["bi"])
qT = T["MAE"] <= TGT["th"]

# ================= A1 閾値感度 =================
say("## A1 閾値感度（＝ask 側 0.03〜0.15R のぼかしと同義・破壊条件 B2: θ=−0.75 と −0.85 の両方で |t|<1.5）")
THS = [-0.60, -0.65, -0.70, -0.75, -0.80, -0.85, -0.90, -0.95]
say("| θ | 在 Δ / t / n(試) | 外 Δ / t / n(試) | 近年 Δ / t / n(試) |")
say("|---|---|---|---|")
A1 = {}
for th in THS:
    row = []
    for wn in ("在2010-20", "外2021-26", "近年2024-26"):
        c = cell_arrays(wn, 24, 1); q = c["MAE"] <= th
        if q.sum() < 20 or (~q).sum() < 20: row.append(f"n {q.sum()} 不足"); A1[(wn, th)] = np.nan; continue
        dd, tw, _ = welch(c["e"][q], c["e"][~q]); A1[(wn, th)] = tw
        row.append(f"{dd:+.3f} / {tw:+.2f} / {q.sum()}")
    say(f"| {th:+.2f} | " + " | ".join(row) + " |")
B2_fire = (abs(A1.get(("外2021-26", -0.75), np.nan)) < 1.5) and (abs(A1.get(("外2021-26", -0.85), np.nan)) < 1.5)
say(f"\n→ 外 B2 k=24: θ=−0.75 t {A1.get(('外2021-26',-0.75)):+.2f}・θ=−0.80 t {A1.get(('外2021-26',-0.80)):+.2f}・θ=−0.85 t {A1.get(('外2021-26',-0.85)):+.2f} → **B2 {'発火' if B2_fire else '非発火'}**")
say()

# ================= A2 正直な家族（240 セル） =================
say("## A2 正直な家族: θ(8) × B(5) × k(2) × 窓(3) = 240 セル（c68 の印字は 12 セル）")
grid = []
for wn in W:
    for k in KS:
        for bi in range(5):
            c = cell_arrays(wn, k, bi)
            for th in THS:
                q = c["MAE"] <= th
                if q.sum() < 20 or (~q).sum() < 20: continue
                dd, tw, _ = welch(c["e"][q], c["e"][~q])
                if not np.isnan(tw): grid.append((wn, k, bi, th, dd, tw, int(q.sum()), int((~q).sum())))
G = pd.DataFrame(grid, columns=["win", "k", "bi", "th", "dd", "t", "nq", "nr"])
say(f"- 有効セル {len(G)}（n≥20 の両群）・名目 |t|>2 **{(G.t.abs()>2).sum()}**（独立なら期待 {0.0455*len(G):.1f}）・max|t| **{G.t.abs().max():.2f}**・t の sd {G.t.std(ddof=1):.2f}")
say(f"- Bonferroni 0.05（|t|≥{abs(-0.0):.0f}…）: 閾値 |t| ≥ {abs(np.sqrt(2)*0):.0f}" if False else "")
bonf_t = 0
from math import erf, sqrt
def z_for_p(p):
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if norm_sf2(mid) > p: lo = mid
        else: hi = mid
    return (lo + hi) / 2
bonf_t = z_for_p(0.05 / len(G))
say(f"- Bonferroni 0.05 の閾値 |t| ≥ {bonf_t:.2f} → 通過 **{(G.t.abs()>=bonf_t).sum()}** セル")
pv = G.t.abs().map(norm_sf2).to_numpy()
ordr = np.argsort(pv); holm_pass = 0
for r, j in enumerate(ordr):
    if pv[j] <= 0.05 / (len(G) - r): holm_pass += 1
    else: break
say(f"- Holm 0.05 通過 **{holm_pass}** セル（最小 p {pv.min():.2e}）")
say("\n上位 |t| 10 セル:")
say("| 窓 | k | B | θ | Δ | t | n(試):n(残) |")
say("|---|---|---|---|---|---|---|")
for _, r in G.reindex(G.t.abs().sort_values(ascending=False).index).head(10).iterrows():
    say(f"| {r.win} | {r.k} | {BINS[int(r.bi)]} | {r.th:+.2f} | {r.dd:+.3f} | {r.t:+.2f} | {int(r.nq)}:{int(r.nr)} |")
say()

# ================= A3 置換プラセボ =================
say("## A3 置換プラセボ（帰無 e ⫫ MAE | 窓,k,B・最細窓 × B_k 内で e を取引レベル置換・セル所属と cl_k 水準を完全保存）")
NPERM = 5000
# 層: (FINE, B_k) ごとに e を置換。窓 在/外/近年 の構成も B 構成も保存される。
perm_t_cell = np.zeros(NPERM)           # 外 B2 k=24 θ=−0.8
perm_max_out = np.zeros(NPERM)          # 外窓 θ×B×k の max|t|
perm_max_all = np.zeros(NPERM)          # 240 セル全体の max|t|
perm_cnt_all = np.zeros(NPERM)          # 240 セルの |t|>2 個数
# 事前に層のインデックスを用意
strata = {}
for k in KS:
    s = S[k]; f = FINE[s["alive"]]
    lst = []
    for fv in (0, 1, 2):
        for bi in range(5):
            idx = np.nonzero((f == fv) & (s["b"] == bi))[0]
            if len(idx) > 1: lst.append(idx)
    strata[k] = lst
# 観測値
obs_cell_t = welch(T["e"][qT], T["e"][~qT])[1]
obs_max_out = G[G.win == "外2021-26"].t.abs().max()
obs_max_all = G.t.abs().max()
obs_cnt_all = int((G.t.abs() > 2).sum())
cells_def = [(r.win, int(r.k), int(r.bi), r.th) for _, r in G.iterrows()]
sel = np.array([w == "外2021-26" for (w, _, _, _) in cells_def])
# 置換ループ
Eperm = {k: S[k]["e"].copy() for k in KS}
masks = {}
for wn in W:
    for k in KS:
        masks[(wn, k)] = W[wn][S[k]["alive"]]
qmask = {}
for (wn, k, bi, th) in cells_def:
    c = masks[(wn, k)] & (S[k]["b"] == bi)
    qmask[(wn, k, bi, th)] = (c, S[k]["MAE"] <= th)
for p in range(NPERM):
    for k in KS:
        ep = Eperm[k]; base = S[k]["e"]
        for idx in strata[k]:
            ep[idx] = base[rng.permutation(idx)]
    ts_all = []
    for key in cells_def:
        wn, k, bi, th = key
        cm, qm = qmask[key]
        ee = Eperm[k]
        a = ee[cm & qm]; b_ = ee[cm & ~qm]
        tw = welch(a, b_)[1]
        ts_all.append(abs(tw) if not np.isnan(tw) else 0.0)
        if key == ("外2021-26", 24, 1, -0.8): perm_t_cell[p] = tw
    ts_all = np.array(ts_all)
    perm_max_all[p] = ts_all.max()
    perm_cnt_all[p] = (ts_all > 2).sum()
    perm_max_out[p] = ts_all[sel].max()
p_cell = (np.abs(perm_t_cell) >= abs(obs_cell_t)).mean()
p_fw_out = (perm_max_out >= obs_max_out).mean()
p_fw_all = (perm_max_all >= obs_max_all).mean()
p_cell_target_fw = (perm_max_out >= abs(obs_cell_t)).mean()
say(f"- 単セル（外 B2 k=24 θ=−0.8）観測 |t| {abs(obs_cell_t):.2f} → 置換 両側 **p_cell = {p_cell:.4f}**（置換 t の sd {perm_t_cell.std(ddof=1):.2f}・平均 {perm_t_cell.mean():+.3f}）")
say(f"- 外窓の θ×B×k 格子（{int(sel.sum())} セル）max|t| 観測 {obs_max_out:.2f} → **p_fw(外) = {p_fw_out:.4f}**")
say(f"- 主target を家族内の 1 つとして評価: 外格子の max|t| が {abs(obs_cell_t):.2f} 以上になる確率 = **{p_cell_target_fw:.4f}**  ← これが T1 の正しい p")
say(f"- 240 セル全体 max|t| 観測 {obs_max_all:.2f} → p_fw(全) = {p_fw_all:.4f}")
B1_fire = p_cell_target_fw > 0.10
say(f"\n→ **破壊条件 B1（p_fw > 0.10）: {'発火' if B1_fire else '非発火'}**")
say()

# ================= A4 コスト倍 =================
say("## A4 コスト倍（全本が往復コストを払う現実: e_λ = (R + ft·1{SL/TP} − λ·ft) − cl_k）")
say("| λ | 在 Δ / t | 外 Δ / t | 近年 Δ / t |")
say("|---|---|---|---|")
A4t = {}
for lam in (0, 1, 2, 3):
    row = []
    for wn in ("在2010-20", "外2021-26", "近年2024-26"):
        s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
        e = (Rstar[al] - lam * ft[al]) - s["clk"][m]
        q = s["MAE"][m] <= -0.8
        dd, tw, _ = welch(e[q], e[~q]); A4t[(wn, lam)] = tw
        row.append(f"{dd:+.3f} / {tw:+.2f}")
    say(f"| {lam} | " + " | ".join(row) + " |")
B6_fire = abs(A4t[("外2021-26", 2)]) < 1.5
say(f"\n→ λ=2（コスト倍）外 t {A4t[('外2021-26',2)]:+.2f} → **破壊条件 B6: {'発火' if B6_fire else '非発火'}**")
say()

# ================= A5 クラスタ・ブートストラップ =================
say("## A5 建玉日クラスタ t とブロック・ブートストラップ（c68 §4 は素の Welch t のみ）")
say("| 窓 | Δ | Welch t | 日クラスタ t | n日 | ブロック boot 両側 p | boot CI95 |")
say("|---|---|---|---|---|---|---|")
A5 = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= -0.8; g = day[al]
    dd, tw, _ = welch(e[q], e[~q])
    tc, nday = welch_cluster(e[q], e[~q], g[q], g[~q])
    # 移動ブロック・ブートストラップ（ブロック = 連続 20 建玉日）
    udays = np.unique(g); nb = 2000; BL = 20
    starts = np.arange(len(udays))
    boots = np.empty(nb)
    d2i = {d: i for i, d in enumerate(udays)}
    gi = np.array([d2i[x] for x in g])
    nblocks = max(1, int(np.ceil(len(udays) / BL)))
    for ib in range(nb):
        st = rng.integers(0, len(udays), nblocks)
        pick = np.concatenate([np.arange(x, min(x + BL, len(udays))) for x in st])
        sel = np.isin(gi, pick)
        # 重み付き（ブロック内の日を 1 回ずつ）
        ee = e[sel]; qq = q[sel]
        if qq.sum() < 5 or (~qq).sum() < 5: boots[ib] = np.nan; continue
        boots[ib] = ee[qq].mean() - ee[~qq].mean()
    bo = boots[~np.isnan(boots)]
    pb = (np.sign(bo) != np.sign(dd)).mean() * 2
    A5[wn] = tc
    say(f"| {wn} | {dd:+.3f} | {tw:+.2f} | **{tc:+.2f}** | {nday} | {min(pb,1.0):.3f} | [{np.percentile(bo,2.5):+.3f}, {np.percentile(bo,97.5):+.3f}] |")
B4_fire = abs(A5["外2021-26"]) < 1.5
say(f"\n→ 外 日クラスタ t {A5['外2021-26']:+.2f} → **破壊条件 B4: {'発火' if B4_fire else '非発火'}**")
say()

# ================= A6 裾依存 =================
say("## A6 裾依存（1 点抜き・トリム・順位・中央値）")
say("| 窓 | Δ | t | 最大影響 1 本抜き Δ / t | 抜いた本の e | 5% トリム Δ | Mann-Whitney z / p | 中央値差 |")
say("|---|---|---|---|---|---|---|---|")
A6 = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1)
    e = s["e"][m]; q = s["MAE"][m] <= -0.8
    dd, tw, _ = welch(e[q], e[~q])
    # 1 点抜き（試した群の各点を落として |t| が最小になる点）
    worst_t, worst_d, worst_e = None, None, None
    ii = np.nonzero(q)[0]
    for j in ii:
        kp = q.copy(); kp[j] = False
        d2, t2, _ = welch(e[kp], e[~q])
        if worst_t is None or abs(t2) < abs(worst_t): worst_t, worst_d, worst_e = t2, d2, e[j]
    # 5% トリム
    def trim(x, f=0.05):
        x = np.sort(x); c = int(np.floor(len(x) * f))
        return x[c:len(x) - c] if len(x) - 2 * c >= 3 else x
    dt = trim(e[q]).mean() - trim(e[~q]).mean()
    # Mann-Whitney
    a, b_ = e[q], e[~q]
    allv = np.concatenate([a, b_]); rk = pd.Series(allv).rank().to_numpy()
    n1, n2 = len(a), len(b_); R1 = rk[:n1].sum()
    U = R1 - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2; sdU = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    zU = (U - mu) / sdU
    A6[wn] = worst_t
    say(f"| {wn} | {dd:+.3f} | {tw:+.2f} | {worst_d:+.3f} / **{worst_t:+.2f}** | {worst_e:+.2f} | {dt:+.3f} | {zU:+.2f} / {norm_sf2(zU):.3f} | {np.median(a)-np.median(b_):+.3f} |")
B5_fire = abs(A6["外2021-26"]) < 1.5
say(f"\n→ 外 1 点抜き |t| {abs(A6['外2021-26']):.2f} → **破壊条件 B5: {'発火' if B5_fire else '非発火'}**")
say()

# ================= A7 別分割 =================
say("## A7 別の在外分割（c68 の 外 +0.33 と 近年 +0.58 は 近年 ⊂ 外 ＝ 二重計上の疑い）")
say("### (a) 外前 2021-23 ＝ 外 ∖ 近年 を独立に（破壊条件 B3: 符号逆 or |t|<0.5）")
say("| 部分窓 | n(試):n(残) | e(試) | e(残) | Δ | t | 寄与（Δ·n比） |")
say("|---|---|---|---|---|---|---|")
splits = {"在2010-20": year <= 2020, "外前2021-23": (year >= 2021) & (year <= 2023), "近年2024-26": year >= 2024,
          "外2021-26(参照)": year >= 2021}
A7 = {}
for sn, sm in splits.items():
    s = S[24]; m = sm[s["alive"]] & (s["b"] == 1)
    e = s["e"][m]; q = s["MAE"][m] <= -0.8
    if q.sum() < 10 or (~q).sum() < 10: say(f"| {sn} | {q.sum()}:{(~q).sum()} | n 不足 | | | | |"); continue
    dd, tw, _ = welch(e[q], e[~q]); A7[sn] = (dd, tw, q.sum())
    say(f"| {sn} | {q.sum()}:{(~q).sum()} | {e[q].mean():+.3f} | {e[~q].mean():+.3f} | {dd:+.3f} | {tw:+.2f} | {q.sum()} 本 |")
B3_fire = ("外前2021-23" in A7) and ((np.sign(A7["外前2021-23"][0]) != np.sign(A7["外2021-26(参照)"][0])) or abs(A7["外前2021-23"][1]) < 0.5)
say(f"\n→ **破壊条件 B3: {'発火' if B3_fire else '非発火'}**")
say()
say("### (b) 偶数年／奇数年　(c) 建玉時刻順 4 等分ブロック　(d) 在の二分")
say("| 分割 | n(試):n(残) | Δ | t |")
say("|---|---|---|---|")
s = S[24]; mB2 = (s["b"] == 1); alB2 = s["alive"][mB2]
yB2 = year[alB2]; eB2 = s["e"][mB2]; qB2 = s["MAE"][mB2] <= -0.8; etB2 = df.entry_time.to_numpy()[alB2]
subs = [("偶数年 全標本", (yB2 % 2) == 0), ("奇数年 全標本", (yB2 % 2) == 1),
        ("在 2010-15", (yB2 <= 2015)), ("在 2016-20", (yB2 >= 2016) & (yB2 <= 2020))]
ordt = np.argsort(etB2); qt = np.quantile(np.arange(len(ordt)), [0.25, 0.5, 0.75])
rankpos = np.empty(len(ordt)); rankpos[ordt] = np.arange(len(ordt))
for i in range(4):
    lo = 0 if i == 0 else qt[i - 1]; hi = len(ordt) if i == 3 else qt[i]
    subs.append((f"時系列ブロック {i+1}/4", (rankpos >= lo) & (rankpos < hi)))
for sn, sm in subs:
    e = eB2[sm]; q = qB2[sm]
    if q.sum() < 10 or (~q).sum() < 10: say(f"| {sn} | {q.sum()}:{(~q).sum()} | n 不足 | |"); continue
    dd, tw, _ = welch(e[q], e[~q])
    say(f"| {sn} | {q.sum()}:{(~q).sum()} | {dd:+.3f} | {tw:+.2f} |")
say()

# ================= A8 機構・構成 =================
say("## A8 機構・構成（c68 は TP% のみ印字・SL%/幾何/残り保有は未印字）")
say("| 窓 | 群 | n | e mean / t | cl_k 平均 | MAE 平均 | b 中央 | risk 中央 | ft 平均 | 残り保有 中央 | SL% / TP% / TIME% | BUY% | SL まで | TP まで |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    e = s["e"][m]; q = s["MAE"][m] <= -0.8; c = s["clk"][m]
    for lab, sel in (("試した", q), ("残り", ~q)):
        ex = exitr[al][sel]
        say(f"| {wn} | {lab} | {sel.sum()} | {e[sel].mean():+.4f} / {tstat(e[sel]):+.2f} | {c[sel].mean():+.3f} | {s['MAE'][m][sel].mean():+.3f} | {np.nanmedian(bb[al][sel]):.2f} | {np.median(risk[al][sel]):.2f} | {ft[al][sel].mean():.4f} | {np.median(hold[al][sel]-24):.0f} | {100*(ex=='SL').mean():.0f} / {100*(ex=='TP').mean():.0f} / {100*(ex=='TIME').mean():.0f} | {100*(side[al][sel]=='BUY').mean():.0f} | {(-(1-ft[al][sel])-c[sel]).mean():+.3f} | {(bb[al][sel]+ft[al][sel]-c[sel]).mean():+.3f} |")
say()
say("### 年別の内訳（外 B2・試した群）")
say("| 年 | n(試) | e(試) mean | n(残) | e(残) mean | Δ |")
say("|---|---|---|---|---|---|")
s = S[24]; m = W["外2021-26"][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
e = s["e"][m]; q = s["MAE"][m] <= -0.8; yy = year[al]
for y in sorted(np.unique(yy)):
    a = e[q & (yy == y)]; b_ = e[(~q) & (yy == y)]
    say(f"| {y} | {len(a)} | {a.mean():+.3f} | {len(b_)} | {b_.mean():+.3f} | {a.mean()-b_.mean():+.3f} |" if len(a) >= 3 and len(b_) >= 3 else f"| {y} | {len(a)} | — | {len(b_)} | — | — |")
say()

# ================= A9 プラセボ変数 =================
say("## A9 プラセボ変数（MAE を無関係な量に差し替えて同じ 240 セル格子を走らせる）")
say("| プラセボ | 有効セル | 名目 |t|>2 | max|t| | 外 B2 k=24 θ=−0.8 の t |")
say("|---|---|---|---|---|")
for pname in ("時刻シフト MAE（同窓内 roll 50）", "一様乱数", "MAE の符号反転（＝MFE 風）"):
    cnt = 0; mx = 0.0; tt_target = np.nan; nc = 0
    for wn in W:
        for k in KS:
            s = S[k]
            for bi in range(5):
                mm = W[wn][s["alive"]] & (s["b"] == bi)
                if mm.sum() < 60: continue
                base = s["MAE"][mm]
                if pname.startswith("時刻"): X = np.roll(base, 50)
                elif pname == "一様乱数": X = rng.random(mm.sum()) * (base.max() - base.min()) + base.min()
                else: X = -base
                ee = s["e"][mm]
                for th in THS:
                    # プラセボ変数は分布が違うので「同じ割合」を切る（θ の分位を合わせる）
                    frac = (base <= th).mean()
                    if frac <= 0 or frac >= 1: continue
                    cut = np.quantile(X, frac); qq = X <= cut
                    if qq.sum() < 20 or (~qq).sum() < 20: continue
                    _, tw, _ = welch(ee[qq], ee[~qq])
                    if np.isnan(tw): continue
                    nc += 1
                    if abs(tw) > 2: cnt += 1
                    mx = max(mx, abs(tw))
                    if wn == "外2021-26" and k == 24 and bi == 1 and th == -0.8: tt_target = tw
    say(f"| {pname} | {nc} | {cnt} ({100*cnt/max(nc,1):.1f}%) | {mx:.2f} | {tt_target:+.2f} |")
say(f"| **実データ MAE** | {len(G)} | {(G.t.abs()>2).sum()} ({100*(G.t.abs()>2).sum()/len(G):.1f}%) | {G.t.abs().max():.2f} | {obs_cell_t:+.2f} |")
say()

# ================= A10 T2 の射程（検出力） =================
say("## A10 T2 の射程: 主セル (k=24,B3) の検出力曲線（置換 null の 95 分位を閾値・2000 回）")
NP2 = 2000
pow_rows = []
for wn in ("在2010-20", "外2021-26"):
    s = S[24]; m = W[wn][s["alive"]] & (s["b"] == 2)
    x = s["MAE"][m]; e = s["e"][m]
    q1, q2 = np.quantile(x, [1/3, 2/3]); top = x >= q2; bot = x <= q1
    et, eb = e[top], e[bot]
    # 置換 null: top/bot ラベルを入れ替え
    pool = np.concatenate([et, eb]); n1 = len(et)
    null_t = np.empty(NP2)
    for i in range(NP2):
        pp = rng.permutation(pool); null_t[i] = welch(pp[:n1], pp[n1:])[1]
    crit = np.percentile(np.abs(null_t), 95)
    row = [wn, f"{crit:.2f}"]
    for d in (-0.02, -0.04, -0.10, -0.20):
        # 検出力: top に δ を注入し、ブートストラップ再標本で |t|>crit となる率
        hit = 0
        for i in range(NP2):
            ia = rng.integers(0, len(et), len(et)); ib = rng.integers(0, len(eb), len(eb))
            tt = welch(et[ia] + d, eb[ib])[1]
            if abs(tt) > crit: hit += 1
        row.append(f"{hit/NP2:.2f}")
    pow_rows.append(row)
say("| 窓 | 置換 null の |t| 95 分位 | 検出力 δ=−0.02R | −0.04R | −0.10R | −0.20R |")
say("|---|---|---|---|---|---|")
for r in pow_rows: say("| " + " | ".join(r) + " |")
say()

# ================= A11 T3 の帰無分布 =================
say("## A11 T3「60 セルは帰無の幅」の検証（c68: 名目 |t|>2 が 4・期待 2.7・t sd 1.02・max|t| 2.36）")
# c68 の 60 セル格子（三分位）を再計算 + 置換帰無
tri_cells = []
for var in ("MAE", "MFE"):
    for wn in W:
        for k in KS:
            s = S[k]
            for bi in range(5):
                mm = W[wn][s["alive"]] & (s["b"] == bi)
                if mm.sum() < 60: continue
                tri_cells.append((var, wn, k, bi))
def tri_t(cells, Esrc):
    out = []
    for (var, wn, k, bi) in cells:
        s = S[k]; mm = W[wn][s["alive"]] & (s["b"] == bi)
        x = s[var][mm]; ee = Esrc[k][mm]
        q1, q2 = np.quantile(x, [1/3, 2/3]); top = x >= q2; bot = x <= q1
        tw = welch(ee[top], ee[bot])[1]
        out.append(tw if not np.isnan(tw) else 0.0)
    return np.array(out)
obs_tri = tri_t(tri_cells, {k: S[k]["e"] for k in KS})
say(f"- 再現: セル {len(obs_tri)}・名目 |t|>2 **{(np.abs(obs_tri)>2).sum()}**・max|t| **{np.abs(obs_tri).max():.2f}**・t sd **{obs_tri.std(ddof=1):.2f}**（c68: 4 / 2.36 / 1.02）")
NP3 = 1500
cnt_null = np.empty(NP3); sd_null = np.empty(NP3); mx_null = np.empty(NP3)
for p in range(NP3):
    for k in KS:
        ep = Eperm[k]; base = S[k]["e"]
        for idx in strata[k]: ep[idx] = base[rng.permutation(idx)]
    tv = tri_t(tri_cells, Eperm)
    cnt_null[p] = (np.abs(tv) > 2).sum(); sd_null[p] = tv.std(ddof=1); mx_null[p] = np.abs(tv).max()
say(f"- 置換帰無（窓/B/k の重複を保存）: |t|>2 の個数 平均 **{cnt_null.mean():.2f}**（独立前提の「期待 2.7」と比較）・95 分位 **{cnt_null.max() if False else np.percentile(cnt_null,95):.1f}**・観測 {(np.abs(obs_tri)>2).sum()} の p = **{(cnt_null>=(np.abs(obs_tri)>2).sum()).mean():.3f}**")
say(f"- 置換帰無 t の sd: 平均 {sd_null.mean():.2f}・[{np.percentile(sd_null,2.5):.2f}, {np.percentile(sd_null,97.5):.2f}]・観測 {obs_tri.std(ddof=1):.2f}")
say(f"- 置換帰無 max|t|: 平均 {mx_null.mean():.2f}・95 分位 {np.percentile(mx_null,95):.2f}・観測 {np.abs(obs_tri).max():.2f} の p = **{(mx_null>=np.abs(obs_tri).max()).mean():.3f}**")
say()

# ================= 判定 =================
say("## 判定（事前固定の規則）")
fires = {"B1 置換 FWER p>0.10": B1_fire, "B2 閾値の隣で消える": B2_fire, "B3 外前 2021-23 が支持しない": B3_fire,
         "B4 日クラスタ |t|<1.5": B4_fire, "B5 1 点抜きで |t|<1.5": B5_fire, "B6 コスト倍で |t|<1.5": B6_fire}
for kk, vv in fires.items(): say(f"- {kk}: **{'発火' if vv else '非発火'}**")
nfire = sum(1 for kk, vv in fires.items() if vv and kk != "B1 置換 FWER p>0.10")
if B1_fire or nfire >= 2: verdict = "broken"
elif nfire == 1: verdict = "weakened"
else: verdict = "survived"
say(f"\n**T1（B2 の「縁を試して戻った本」外 +0.33R）＝ {verdict}**（B1 {'発火' if B1_fire else '非発火'}・B2〜B6 の発火数 {nfire}）")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
