# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-09 17:15 — 対象: cycle23 (15:50) の残存弱信号
  W1「外 2021-26H1 (k=24, B3) の V（path 実現ボラ）top−bottom 三分位差 ΔV = −0.262R（Welch t −2.54, 236:236）」
  W2「同セルの bottom（静かに停滞した本）e = +0.154R (t +2.28)＝『静かに停滞した本は外で走り、荒れて停滞した本は腐る』」
  W3（研究レーン自身の残存反証）「D2 を取るなら『外のみに宿る形の情報』を本件は否定できていない」
  cycle23 の事前固定判定 H_V FAIL／H_O FAIL（null）は再現して争わない。壊しに行くのは null の上に残された W1〜W3。

読取りのみ・発注なし・scan なし・M5 読込なし・MT5 なし・外部通信なし。入力は既存キャッシュ
  data/c1_reaccel_paths_2010_2026.json・data/refute_c4_scan_paths_2010_2026.json（b・atr）・data/refute_c2_fullpaths.npz。
書き込みは data/refute_c23_pathshape.md（＋run.log）のみ。

=== 事前固定（この docstring を書いてから数字を見る・以後動かさない） ===
記帳: cycle23 と同一。R* = R + ft（SL/TP）・TIME そのまま。e = R* − cl_k。評価足 k は hold>k。V_k = sqrt(mean_j Δcl_j²)、
      O_k = mean_j 1{cl_j>0}（j=1..k）。三分位は (窓,k,B) 内。B3 = |cl_k| < 0.2。look-ahead なし。
H0: E[e | F_k] = 0（マルチンゲール）→ ΔV = 0。W1 は 60 セル格子（2 変数×2 k×5 B×3 窓）から事後に拾った 1 セル。
Q0 再現: cycle23 §1/§3 の 外 (k=24,B3) ΔV −0.2622 / t −2.54 / 236:236、bottom e +0.1544 / t +2.28、在 ΔV +0.0209 を assert（|差|<1e-3）。
Q1 クラスタ: cycle23 の主セル t は Welch（本等重み・独立仮定）。同日建玉の本は path も V も e も共有する。
      ΔV を e ~ 1{top} の回帰で 建玉日クラスタ t・ISO 週クラスタ t・k 足時点の暦日クラスタ t で出す。bottom e の日クラスタ t。
      クラスタ数・最大クラスタ・bottom Σe の上位 3 日／上位 3 月の寄与率。
Q2 多重検定（主検定）: 各 (窓,k,B) セル内で V（および O）を 2000 回シャッフル（e・セル所属は固定＝H0 の下で e は形と独立）。
      統計量: S1 = 60 セル max|t| ≥ 2.54 の割合（family-wise p）／S2 = 外 20 セル max|t|／S3 = 全 V セル 30 の max|t|／
      S4 = 事前に 外 V (k=24,B3) を選んでいた場合の単セル両側 p／S5 = 「外 |t|≥2.54 ∧ 近年 同符号」の同時パターン p。
Q3 別分割・レジーム: 外の年別 ΔV（2021..2026H1・符号と Welch t）、重ならない窓 2021-23／2024-26H1／2025-26H1、LOYO（外から 1 年除去）、
      偶数年／奇数年、在の 4 年刻み（2010-13／2014-17／2018-20）。外の中の 壁種{outer,mid}×JST{7-12,13-20,21-6}（Bonferroni α 0.05/5）。
Q4 プラセボ（格子の位置）: 外 B3 の ΔV を k ∈ {6,9,12,18,24,30,36,48,72,96} で掃引（k=24 だけ山なら選択効果）。
      B3 の幅 {0.1,0.2,0.3,0.4}、分割 {三分位, 四分位 top−bottom, 中央値 split}（k=24）。
Q5 機構（形か・幾何/レジームか・記帳か）:
  (a) V の代わりに建玉時の atr/risk（F_0 可測・「ストップがボラ何本分か」）三分位で同セルを切った Δ_ATR、および V/(atr/risk)
      （建玉前ボラで正規化した path の揺れ）三分位の Δ。ρ(V, atr/risk) を印字。Δ_ATR が ΔV と同程度・同符号なら「形」でなく「幾何/ボラ水準」。
  (b) 記帳: bottom は TIME 24%・top は 5%。TIME 決着は終値クローズで ft を払っていない → TIME に ft（0.10 USD）を課した公正版 ΔV。
      決着種別ごとの e（SL/TP/TIME）と群内シェアで ΔV を分解（構成効果 vs 種別内効果）。
  (c) 側別 bottom e（BUY/SELL 別に正か）・top e。両側で bottom 正なら 2021-26 の金の上昇ドリフトでは説明できない。
  (d) 残り保有: bottom 中央値 66 本 vs top 22 本。e を残り保有で層化（≤24／25-72／>72）して群内差を印字（記述）。
Q6 使える形: 在の (k=24,B3) V 三分位 上位カット q2_在 を固定し、全窓で「hold>24 ∧ |cl_24|<0.2 ∧ V_24 ≥ q2_在 → 足 24 終値で成行クローズ」を
      s ∈ {0, 0.10, 0.20} USD で評価。窓の全本に対する diff（R1−R0・R0=R*）・対 t・上位 10% 尻尾残存。
      研究レーン基準: 在 t≥2 ∧ 外 t≥1.5 ∧ 残存 ≥90%。
Q7 区間: 外 ΔV の 本 bootstrap と 建玉日ブロック bootstrap 95% CI（2000 回）。bottom e の同 CI。
判定（事前固定）:
  broken       = Q2 p(S1) > 0.05 ∧ ( Q1 日クラスタ |t| < 2 ∨ ¬(Q3 2021-23 t ≤ −1.5 ∧ 2024-26H1 t ≤ −1.5) ) ∧ Q6 s=0.10 が基準 FAIL。
  survived     = Q2 p(S1) < 0.05 ∧ Q1 日クラスタ |t| ≥ 2 ∧ Q3 2021-23 と 2024-26H1 がともに t ≤ −1.5 ∧ Q5(a) |t_ATR| < 1。
  それ以外     = inconclusive。
  W2（静かな本は正）は別に: bottom e の日クラスタ t ≥ 2 ∧ 日ブロック bootstrap CI が 0 を排除 なら「記述として残す」、それ以外は「残さない」。
seed 20261109。
"""
import json, os, math, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c23_pathshape.md")
NPERM = 2000; SEED = 20261109
rng = np.random.default_rng(SEED)
L = []
def say(s=""): print(s, flush=True); L.append(s)

def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 3: return float("nan"), float("nan")
    se = d.std(ddof=1) / math.sqrt(n)
    t = d.mean() / se if se > 0 else float("nan")
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else float("nan")
    return t, p

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return float("nan"), float("nan"), float("nan")
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, (diff / se if se > 0 else float("nan")), se

def t_cluster(d, g):
    d = np.asarray(d, float); m = d.mean(); r = d - m
    s = pd.Series(r).groupby(np.asarray(g)).sum().to_numpy()
    se = math.sqrt((s ** 2).sum()) / len(d)
    return (m / se if se > 0 else float("nan")), len(s), int(pd.Series(g).value_counts().max())

def diff_cluster(e_top, e_bot, g_top, g_bot):
    """ΔV = mean(top) − mean(bot) のクラスタ頑健 t（回帰 e ~ 1 + 1{top}・クラスタ別スコア和）"""
    y = np.concatenate([e_top, e_bot]); x = np.concatenate([np.ones(len(e_top)), np.zeros(len(e_bot))])
    g = np.concatenate([g_top, g_bot])
    X = np.column_stack([np.ones(len(y)), x]); XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y; u = y - X @ beta
    S = pd.DataFrame(X * u[:, None]).groupby(g).sum().to_numpy()
    V = XtX_inv @ (S.T @ S) @ XtX_inv
    return beta[1], beta[1] / math.sqrt(V[1, 1]), len(np.unique(g))

def top_ret(R0, R1):
    top = np.argsort(R0)[-max(1, len(R0) // 10):]
    return 100 * R1[top].sum() / R0[top].sum() if R0[top].sum() != 0 else 100.0

# ---------- load (cycle23 と同一) ----------
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
aux = {t["entry_time"]: t for t in c4["trades"]}
df["b"] = [aux[t]["b"] if t in aux else np.nan for t in df.entry_time]
df["atr"] = [aux[t]["atr"] if t in aux else np.nan for t in df.entry_time]
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; off = z["off"]
n = len(df)
assert len(off) - 1 == n, "npz 本数不一致"
assert np.all(np.diff(off) == df.hold.to_numpy() + 1), "path 長 ≠ hold+1"
risk = df.risk.to_numpy(); ft = FT / risk; R0 = df.R.to_numpy(); hold = df.hold.to_numpy()
er = df.exit_reason.to_numpy(); is_slt = (er == "SL") | (er == "TP"); is_time = er == "TIME"
Rstar = R0 + ft * is_slt
Rfair = Rstar - ft * is_time          # Q5(b): TIME にも ft を課した公正版
side = df.side.to_numpy(); year = df.year.to_numpy(); jh = df.jh.to_numpy(); wk = df.wall_kind.to_numpy()
et = df.entry_time.to_numpy(); day = et // 86400
week = ((et // 86400) + 3) // 7       # 1970-01-01 木曜 → +3 で月曜始まり
atr_risk = (df.atr / df.risk).to_numpy()
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
WN = list(W.keys())
KS = (24, 12)
BN = ("B1", "B2", "B3", "B4", "B5")
def binid(x):
    return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))

def state(k):
    alive = np.nonzero(hold > k)[0]
    idx = off[alive][:, None] + np.arange(0, k + 1)[None, :]
    P = clR[idx]; d = np.diff(P, axis=1)
    V = np.sqrt((d ** 2).mean(axis=1)); O = (P[:, 1:] > 0).mean(axis=1); clk = P[:, -1]
    return dict(alive=alive, clk=clk, e=Rstar[alive] - clk, efair=Rfair[alive] - clk, V=V, O=O, b=binid(clk))
S = {k: state(k) for k in KS}

def tercile_split(x):
    q1, q2 = np.quantile(x, [1/3, 2/3]); return x >= q2, x <= q1

say(f"# AUREL [REFUTE] 2026-11-09 — cycle23 の残存「外 (k=24,B3) 荒れた本 vs 静かな本 ΔV −0.262」を潰す  入力 {n} 本  {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c23_pathshape.py)")
say(f"FEED_TOL={FT}、ft 平均 {ft.mean():.4f}R、SL/TP {is_slt.sum()}・TIME {is_time.sum()}。atr 利用可 {np.isfinite(atr_risk).sum()}。npz assert 通過。seed {SEED}・NPERM {NPERM}。")
say()

# ---------- Q0 ----------
say("## Q0. 再現（cycle23 §1/§3）: 外 (k=24,B3) V 三分位")
s24 = S[24]
def prim(wn, var="V", k=24, s=None):
    s = S[k] if s is None else s
    m = W[wn][s["alive"]] & (s["b"] == 2)
    x = s[var][m]; e = s["e"][m]; top, bot = tercile_split(x)
    return dict(m=m, x=x, e=e, top=top, bot=bot, al=s["alive"][m])
P_out = prim("外2021-26"); P_in = prim("在2010-20"); P_rec = prim("近年2024-26")
d_out, t_out, se_out = welch(P_out["e"][P_out["top"]], P_out["e"][P_out["bot"]])
d_in, t_in, _ = welch(P_in["e"][P_in["top"]], P_in["e"][P_in["bot"]])
eb_out = P_out["e"][P_out["bot"]]; et_out = P_out["e"][P_out["top"]]
say(f"- 外 ΔV {d_out:+.4f} / Welch t {t_out:+.2f} / {P_out['top'].sum()}:{P_out['bot'].sum()}；bottom e {eb_out.mean():+.4f} (t {tstat(eb_out)[0]:+.2f})・top e {et_out.mean():+.4f} (t {tstat(et_out)[0]:+.2f})")
say(f"- 在 ΔV {d_in:+.4f} / t {t_in:+.2f}；近年 ΔV {welch(P_rec['e'][P_rec['top']], P_rec['e'][P_rec['bot']])[0]:+.4f} / t {welch(P_rec['e'][P_rec['top']], P_rec['e'][P_rec['bot']])[1]:+.2f}")
assert abs(d_out - (-0.2622)) < 1e-3 and abs(t_out - (-2.54)) < 0.01 and abs(eb_out.mean() - 0.1544) < 1e-3 and abs(d_in - 0.0209) < 1e-3, "再現失敗"
say("- assert 通過（cycle23 と一致）")
say()

# ---------- Q1 clustering ----------
say("## Q1. クラスタ頑健 t（cycle23 の主セル t は Welch＝独立仮定）")
al = P_out["al"]; top, bot = P_out["top"], P_out["bot"]
g_day = day[al]; g_week = week[al]; g_kday = (et[al] + 300 * 24) // 86400
say("| 統計量 | 値 | 日クラスタ t (クラスタ数/最大) | 週クラスタ t | k 足暦日クラスタ t |")
say("|---|---|---|---|---|")
b1, tc_day, ncd = diff_cluster(et_out, eb_out, g_day[top], g_day[bot])
_, tc_week, ncw = diff_cluster(et_out, eb_out, g_week[top], g_week[bot])
_, tc_kday, nck = diff_cluster(et_out, eb_out, g_kday[top], g_kday[bot])
maxc = int(pd.Series(np.concatenate([g_day[top], g_day[bot]])).value_counts().max())
say(f"| 外 ΔV (top−bot) | {b1:+.4f} (Welch t {t_out:+.2f}) | {tc_day:+.2f} ({ncd}/{maxc}) | {tc_week:+.2f} ({ncw}) | {tc_kday:+.2f} ({nck}) |")
tb_day, nb, mb = t_cluster(eb_out, g_day[bot]); tb_week, _, _ = t_cluster(eb_out, g_week[bot]); tb_kday, _, _ = t_cluster(eb_out, g_kday[bot])
say(f"| 外 bottom e | {eb_out.mean():+.4f} (t {tstat(eb_out)[0]:+.2f}) | {tb_day:+.2f} ({nb}/{mb}) | {tb_week:+.2f} | {tb_kday:+.2f} |")
tt_day, nt, mt = t_cluster(et_out, g_day[top])
say(f"| 外 top e | {et_out.mean():+.4f} (t {tstat(et_out)[0]:+.2f}) | {tt_day:+.2f} ({nt}/{mt}) | | |")
# 寄与
sb = pd.Series(eb_out).groupby(g_day[bot]).sum().sort_values(ascending=False)
sm = pd.Series(eb_out).groupby(pd.to_datetime(et[al][bot], unit="s").strftime("%Y-%m")).sum().sort_values(ascending=False)
tot = eb_out.sum()
say(f"- bottom Σe = {tot:+.2f}R（n {len(eb_out)}）。上位 3 日 Σ {sb.iloc[:3].sum():+.2f}R（{100*sb.iloc[:3].sum()/tot:.0f}%）・上位 3 月 Σ {sm.iloc[:3].sum():+.2f}R（{100*sm.iloc[:3].sum()/tot:.0f}%）: " + "、".join(f"{i} {v:+.2f}" for i, v in sm.iloc[:3].items()))
say(f"- bottom e の中央値 {np.median(eb_out):+.4f}・正の本 {100*(eb_out>0).mean():.0f}%・上位 10% の本の Σe {np.sort(eb_out)[-len(eb_out)//10:].sum():+.2f}R（{100*np.sort(eb_out)[-len(eb_out)//10:].sum()/tot:.0f}%）")
say()

# ---------- Q2 permutation ----------
say("## Q2. セル内シャッフル（V・O を (窓,k,B) 内で 2000 回置換・e 固定）— family-wise p")
cells = []   # (var, wn, k, b, e_array, ntop, nbot, t_obs)
for var in ("V", "O"):
    for wn in WN:
        for k in KS:
            s = S[k]
            for bi in range(5):
                m = W[wn][s["alive"]] & (s["b"] == bi)
                if m.sum() < 60: continue
                x = s[var][m]; e = s["e"][m]; top, bot = tercile_split(x)
                cells.append((var, wn, k, bi, e, int(top.sum()), int(bot.sum()), welch(e[top], e[bot])[1]))
tobs = np.array([c[7] for c in cells])
say(f"セル数 {len(cells)}・観測 max|t| {np.abs(tobs).max():.2f}（cycle23: 60・2.54）")
Tperm = np.zeros((NPERM, len(cells)))
for ci, c in enumerate(cells):
    e = c[4]; nt_, nb_ = c[5], c[6]; N = len(e)
    for r in range(0, NPERM, 500):
        rr = min(500, NPERM - r)
        idx = np.argsort(rng.random((rr, N)), axis=1)
        a = e[idx[:, :nt_]]; b = e[idx[:, N - nb_:]]
        diff = a.mean(1) - b.mean(1); se = np.sqrt(a.var(1, ddof=1) / nt_ + b.var(1, ddof=1) / nb_)
        Tperm[r:r + rr, ci] = diff / se
isV = np.array([c[0] == "V" for c in cells]); isOut = np.array([c[1] == "外2021-26" for c in cells]); isRec = np.array([c[1] == "近年2024-26" for c in cells])
prim_i = [i for i, c in enumerate(cells) if c[0] == "V" and c[1] == "外2021-26" and c[2] == 24 and c[3] == 2][0]
rec_i = [i for i, c in enumerate(cells) if c[0] == "V" and c[1] == "近年2024-26" and c[2] == 24 and c[3] == 2][0]
obs = abs(tobs[prim_i])
pS1 = (np.abs(Tperm).max(1) >= obs).mean()
pS2 = (np.abs(Tperm[:, isOut]).max(1) >= obs).mean()
pS3 = (np.abs(Tperm[:, isV]).max(1) >= obs).mean()
pS4 = (np.abs(Tperm[:, prim_i]) >= obs).mean()
# S5: 外 V セル (k,B 全 10) で |t|≥obs かつ 近年の同セルが同符号
outV = [i for i, c in enumerate(cells) if c[0] == "V" and c[1] == "外2021-26"]
recV = {(c[2], c[3]): i for i, c in enumerate(cells) if c[0] == "V" and c[1] == "近年2024-26"}
hits = np.zeros(NPERM, bool)
for i in outV:
    j = recV.get((cells[i][2], cells[i][3]))
    if j is None: continue
    hits |= (np.abs(Tperm[:, i]) >= obs) & (np.sign(Tperm[:, i]) == np.sign(Tperm[:, j]))
pS5 = hits.mean()
obs_S5 = (np.sign(tobs[prim_i]) == np.sign(tobs[rec_i]))
say("| 統計量 | 観測 | 帰無 中央値 / 95% 点 | p |")
say("|---|---|---|---|")
for lab, arr, p in (("S1 60 セル max|t|", np.abs(Tperm).max(1), pS1), ("S2 外 20 セル max|t|", np.abs(Tperm[:, isOut]).max(1), pS2),
                    ("S3 V 30 セル max|t|", np.abs(Tperm[:, isV]).max(1), pS3), ("S4 単セル 外 V(24,B3) |t|", np.abs(Tperm[:, prim_i]), pS4)):
    say(f"| {lab} | {obs:.2f} | {np.median(arr):.2f} / {np.quantile(arr, 0.95):.2f} | **{p:.3f}** |")
say(f"| S5 外 V 10 セルのどれかで |t|≥{obs:.2f} ∧ 近年同セル同符号 | 観測は{'成立' if obs_S5 else '不成立'}（近年 t {tobs[rec_i]:+.2f}） | | **{pS5:.3f}** |")
say(f"- 帰無での 60 セル |t|>2 の個数: 中央値 {np.median((np.abs(Tperm)>2).sum(1)):.0f}・観測 {(np.abs(tobs)>2).sum()}")
say()

# ---------- Q3 splits ----------
say("## Q3. 別分割・レジーム（外 V (k=24,B3) ΔV）")
def dv(mask_rows, s=s24, var="V", width=0.2, split="ter"):
    m = mask_rows[s["alive"]] & (np.abs(s["clk"]) < width)
    if m.sum() < 30: return (float("nan"), float("nan"), int(m.sum()), 0, 0)
    x = s[var][m]; e = s["e"][m]
    if split == "ter": top, bot = tercile_split(x)
    elif split == "quart": q1, q3 = np.quantile(x, [0.25, 0.75]); top, bot = x >= q3, x <= q1
    else: md = np.median(x); top, bot = x > md, x <= md
    d, t, _ = welch(e[top], e[bot]); return (d, t, int(m.sum()), int(top.sum()), int(bot.sum()))
say("| 分割 | ΔV / Welch t / n(top:bot) |")
say("|---|---|")
for y in range(2021, 2027):
    d, t, nn, a, b = dv(year == y); say(f"| {y} | {d:+.3f} / {t:+.2f} / {a}:{b} |")
for lab, mk in (("2021-23", (year >= 2021) & (year <= 2023)), ("2024-26H1", year >= 2024), ("2025-26H1", year >= 2025),
                ("外 偶数年", (year >= 2021) & (year % 2 == 0)), ("外 奇数年", (year >= 2021) & (year % 2 == 1)),
                ("在 2010-13", (year >= 2010) & (year <= 2013)), ("在 2014-17", (year >= 2014) & (year <= 2017)), ("在 2018-20", (year >= 2018) & (year <= 2020))):
    d, t, nn, a, b = dv(mk); say(f"| {lab} | {d:+.3f} / {t:+.2f} / {a}:{b} |")
Q3_2123 = dv((year >= 2021) & (year <= 2023)); Q3_2426 = dv(year >= 2024)
say("| LOYO（外から 1 年除去） | " + "；".join(f"−{y}: {dv((year>=2021)&(year!=y))[0]:+.3f} (t{dv((year>=2021)&(year!=y))[1]:+.2f})" for y in range(2021, 2027)) + " |")
say()
say("外の中の部分集合（5 セル・Bonferroni α 0.01 → |t|≥2.58）:")
subs = {"outer": wk == "outer", "mid": wk == "mid", "JST7-12": (jh >= 7) & (jh <= 12), "JST13-20": (jh >= 13) & (jh <= 20), "JST21-6": (jh >= 21) | (jh <= 6)}
for lab, mk in subs.items():
    d, t, nn, a, b = dv((year >= 2021) & mk); say(f"- {lab}: ΔV {d:+.3f} / t {t:+.2f} / {a}:{b}")
say()

# ---------- Q4 placebo grid position ----------
say("## Q4. プラセボ: 格子の位置（外 B3 ΔV の k 掃引・幅・分割法）")
say("| k | 外 ΔV / t / n(top:bot) | 在 ΔV / t | 近年 ΔV / t |")
say("|---|---|---|---|")
KSW = (6, 9, 12, 18, 24, 30, 36, 48, 72, 96)
Sk = {k: (S[k] if k in S else state(k)) for k in KSW}
ksw = {}
for k in KSW:
    o = dv(year >= 2021, s=Sk[k]); i = dv(year <= 2020, s=Sk[k]); r = dv(year >= 2024, s=Sk[k]); ksw[k] = o
    say(f"| {k} | {o[0]:+.3f} / {o[1]:+.2f} / {o[3]}:{o[4]} | {i[0]:+.3f} / {i[1]:+.2f} | {r[0]:+.3f} / {r[1]:+.2f} |")
say("| 幅/分割（k=24・外） | ΔV / t / n(top:bot) |")
say("|---|---|")
for wdt in (0.1, 0.2, 0.3, 0.4):
    o = dv(year >= 2021, width=wdt); say(f"| 幅 |cl|<{wdt} 三分位 | {o[0]:+.3f} / {o[1]:+.2f} / {o[3]}:{o[4]} |")
for sp, lab in (("quart", "四分位 top−bottom"), ("med", "中央値 split")):
    o = dv(year >= 2021, split=sp); say(f"| {lab} | {o[0]:+.3f} / {o[1]:+.2f} / {o[3]}:{o[4]} |")
say()

# ---------- Q5 mechanism ----------
say("## Q5. 機構")
al = P_out["al"]; m = P_out["m"]; e = P_out["e"]; x = P_out["x"]; top, bot = P_out["top"], P_out["bot"]
ar = atr_risk[al]
say("### (a) 形か・幾何/ボラ水準か: 建玉時 atr/risk（F_0 可測）三分位・V/(atr/risk) 三分位で同セル")
ok = np.isfinite(ar)
rho = np.corrcoef(x[ok], ar[ok])[0, 1]
ta, ba = tercile_split(ar[ok]); dA, tA, _ = welch(e[ok][ta], e[ok][ba])
xn = x[ok] / ar[ok]; tn, bn_ = tercile_split(xn); dN, tN, _ = welch(e[ok][tn], e[ok][bn_])
say(f"- ρ(V_24, atr/risk) 外 B3 = {rho:+.2f}（n {ok.sum()}）")
say(f"- Δ_ATR（atr/risk top−bottom）= {dA:+.4f} / t {tA:+.2f} / {ta.sum()}:{ba.sum()}；在 同 = {welch(*[P_in['e'][np.isfinite(atr_risk[P_in['al']])][q] for q in tercile_split(atr_risk[P_in['al']][np.isfinite(atr_risk[P_in['al']])])])[0]:+.4f}")
say(f"- Δ_V/ATR（建玉前ボラで正規化した揺れ top−bottom）= {dN:+.4f} / t {tN:+.2f}")
# V を atr/risk で層化（三分位内で V 三分位）
parts = []
for lab, q in (("ATR低", ba), ("ATR中", ~ta & ~ba), ("ATR高", ta)):
    xx = x[ok][q]; ee = e[ok][q]; tt, bb = tercile_split(xx); d_, t_, _ = welch(ee[tt], ee[bb]); parts.append(f"{lab} ΔV {d_:+.3f} (t{t_:+.2f}, {tt.sum()}:{bb.sum()})")
say("- atr/risk 三分位内の V 三分位差: " + "；".join(parts))
say()
say("### (b) 記帳: TIME 決着（終値クローズ・ft 未徴収）に ft を課した公正版・決着種別分解")
ef = P_out["e"] * 0 + S[24]["efair"][m]
dF, tF, _ = welch(ef[top], ef[bot])
say(f"- 公正版 ΔV（TIME に ft を課す）= {dF:+.4f} / t {tF:+.2f}（元 {d_out:+.4f}）；bottom e 公正版 {ef[bot].mean():+.4f}")
exr = er[al]
say("| 群 | SL% e | TP% e | TIME% e | 群 e |")
say("|---|---|---|---|---|")
for lab, q in (("top", top), ("bot", bot)):
    row = []
    for kind in ("SL", "TP", "TIME"):
        qq = q & (exr == kind); row.append(f"{100*qq.sum()/q.sum():.0f}% {e[qq].mean():+.3f}" if qq.sum() else "—")
    say(f"| {lab} | " + " | ".join(row) + f" | {e[q].mean():+.4f} |")
# 構成効果: bottom のシェアで top の種別内平均を加重
sh_b = {kind: ((bot & (exr == kind)).sum() / bot.sum()) for kind in ("SL", "TP", "TIME")}
sh_t = {kind: ((top & (exr == kind)).sum() / top.sum()) for kind in ("SL", "TP", "TIME")}
mu_t = {kind: e[top & (exr == kind)].mean() for kind in ("SL", "TP", "TIME")}
mu_b = {kind: e[bot & (exr == kind)].mean() for kind in ("SL", "TP", "TIME")}
comp = sum((sh_t[k_] - sh_b[k_]) * mu_b[k_] for k_ in sh_b); within = sum(sh_t[k_] * (mu_t[k_] - mu_b[k_]) for k_ in sh_b)
say(f"- ΔV 分解: 構成効果（決着種別シェア差×bottom 種別内平均）{comp:+.4f}・種別内効果 {within:+.4f}（和 {comp+within:+.4f}）")
say()
say("### (c) 側別（ドリフト説の検査）")
sd = side[al]
for lab in ("BUY", "SELL"):
    q = sd == lab
    say(f"- {lab}: bottom e {e[bot & q].mean():+.4f} (t {tstat(e[bot & q])[0]:+.2f}, n {(bot&q).sum()})・top e {e[top & q].mean():+.4f} (t {tstat(e[top & q])[0]:+.2f}, n {(top&q).sum()})・ΔV {welch(e[top&q], e[bot&q])[0]:+.3f} (t {welch(e[top&q], e[bot&q])[1]:+.2f})")
say()
say("### (d) 残り保有で層化（記述・残り保有は F_k 非可測）")
rem = hold[al] - 24
for lab, q in (("残り ≤24", rem <= 24), ("残り 25-72", (rem > 24) & (rem <= 72)), ("残り >72", rem > 72)):
    say(f"- {lab}: top e {e[top&q].mean():+.3f} (n {(top&q).sum()})・bot e {e[bot&q].mean():+.3f} (n {(bot&q).sum()})・Welch t {welch(e[top&q], e[bot&q])[1]:+.2f}")
say()

# ---------- Q6 strategy form ----------
say("## Q6. 使える形: 在の V 三分位 上位カット q2_在 を固定 → 全窓で「hold>24 ∧ |cl_24|<0.2 ∧ V_24 ≥ q2_在 → 足 24 終値で成行クローズ（slip s）」")
q2_in = np.quantile(P_in["x"], 2/3)
say(f"q2_在 = {q2_in:.4f} R/足（外の三分位 上位カット {np.quantile(P_out['x'], 2/3):.4f}）")
say("| 窓 | s (USD) | 対象本数 / 窓の全本 | diff (R/本・全本) / 対 t | 対象本だけの diff / t | 上位 10% 尻尾残存 | 基準 |")
say("|---|---|---|---|---|---|---|")
alive24 = s24["alive"]; sel_all = np.zeros(n, bool); sel_all[alive24[(np.abs(s24["clk"]) < 0.2) & (s24["V"] >= q2_in)]] = True
cl24 = np.full(n, np.nan); cl24[alive24] = s24["clk"]
Q6 = {}
for wn, wm in W.items():
    for s_ in (0.0, 0.10, 0.20):
        R1 = Rstar.copy(); sel = sel_all & wm
        R1[sel] = cl24[sel] - s_ / risk[sel]
        d_all = (R1 - Rstar)[wm]; d_sel = (R1 - Rstar)[sel]
        tr = top_ret(Rstar[wm], R1[wm])
        Q6[(wn, s_)] = (d_all.mean(), tstat(d_all)[0], tr)
        say(f"| {wn} | {s_:.2f} | {sel.sum()} / {wm.sum()} | {d_all.mean():+.4f} / {tstat(d_all)[0]:+.2f} | {d_sel.mean():+.4f} / {tstat(d_sel)[0]:+.2f} | {tr:.0f}% | |")
q6_pass = (Q6[("在2010-20", 0.10)][1] >= 2) and (Q6[("外2021-26", 0.10)][1] >= 1.5) and (Q6[("外2021-26", 0.10)][2] >= 90)
say(f"- s=0.10 の研究レーン基準（在 t≥2 ∧ 外 t≥1.5 ∧ 外 残存 ≥90%）: **{'PASS' if q6_pass else 'FAIL'}**")
say()

# ---------- Q7 bootstrap ----------
say("## Q7. bootstrap 95% CI（2000 回）")
B = 2000
e_t, e_b = et_out, eb_out; gd_t, gd_b = g_day[top], g_day[bot]
bs_tr = np.array([e_t[rng.integers(0, len(e_t), len(e_t))].mean() - e_b[rng.integers(0, len(e_b), len(e_b))].mean() for _ in range(B)])
# 日ブロック: セル内の全日をリサンプル・ラベル固定
days_u = np.unique(np.concatenate([gd_t, gd_b]))
dt = pd.DataFrame({"e": np.concatenate([e_t, e_b]), "top": np.r_[np.ones(len(e_t), bool), np.zeros(len(e_b), bool)], "d": np.concatenate([gd_t, gd_b])})
grp = {d_: (g.e.to_numpy(), g.top.to_numpy()) for d_, g in dt.groupby("d")}
bs_blk = np.empty(B); bs_blk_b = np.empty(B)
for i in range(B):
    pick = days_u[rng.integers(0, len(days_u), len(days_u))]
    ee = np.concatenate([grp[d_][0] for d_ in pick]); tt = np.concatenate([grp[d_][1] for d_ in pick])
    bs_blk[i] = ee[tt].mean() - ee[~tt].mean() if tt.any() and (~tt).any() else np.nan
    bs_blk_b[i] = ee[~tt].mean() if (~tt).any() else np.nan
ci_tr = np.nanpercentile(bs_tr, [2.5, 97.5]); ci_blk = np.nanpercentile(bs_blk, [2.5, 97.5]); ci_b = np.nanpercentile(bs_blk_b, [2.5, 97.5])
bs_b_tr = np.array([e_b[rng.integers(0, len(e_b), len(e_b))].mean() for _ in range(B)]); ci_b_tr = np.percentile(bs_b_tr, [2.5, 97.5])
say(f"- 外 ΔV: 本 bootstrap [{ci_tr[0]:+.3f}, {ci_tr[1]:+.3f}]・日ブロック [{ci_blk[0]:+.3f}, {ci_blk[1]:+.3f}]（日数 {len(days_u)}）")
say(f"- 外 bottom e: 本 bootstrap [{ci_b_tr[0]:+.3f}, {ci_b_tr[1]:+.3f}]・日ブロック [{ci_b[0]:+.3f}, {ci_b[1]:+.3f}]")
say()

# ---------- verdict ----------
say("## 判定（docstring の事前規則）")
cond_cluster = abs(tc_day) < 2
cond_sub = not (Q3_2123[1] <= -1.5 and Q3_2426[1] <= -1.5)
broken = (pS1 > 0.05) and (cond_cluster or cond_sub) and (not q6_pass)
survived = (pS1 < 0.05) and (abs(tc_day) >= 2) and (Q3_2123[1] <= -1.5 and Q3_2426[1] <= -1.5) and (abs(tA) < 1)
verdict = "broken" if broken else ("survived" if survived else "inconclusive")
w2_keep = (tb_day >= 2) and (ci_b[0] > 0)
say(f"- W1: p(S1) {pS1:.3f}（>0.05 {'✓' if pS1>0.05 else '✗'}）／日クラスタ |t| {abs(tc_day):.2f}（<2 {'✓' if cond_cluster else '✗'}）／2021-23 t {Q3_2123[1]:+.2f}・2024-26H1 t {Q3_2426[1]:+.2f}（両方 ≤−1.5 {'✗' if cond_sub else '✓'}）／Q6 s=0.10 {'FAIL' if not q6_pass else 'PASS'}／Q5(a) t_ATR {tA:+.2f}")
say(f"- **W1 判定: {verdict}**")
say(f"- **W2（静かな本は正・記述として残すか）: bottom e 日クラスタ t {tb_day:+.2f}・日ブロック CI [{ci_b[0]:+.3f}, {ci_b[1]:+.3f}] → {'残す' if w2_keep else '残さない'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
