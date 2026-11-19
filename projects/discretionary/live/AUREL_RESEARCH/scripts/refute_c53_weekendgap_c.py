# -*- coding: utf-8 -*-
"""
[REFUTE c53 — C] 2026-11-19 15:30 反証レーン。c53 の中で唯一「弱い信号」の形をしているもの＝
**H_B1 近年 2024-26H1 の mean ΔR_carry = +0.3485 [+0.0099, +0.6863]**（family 12 セル中 唯一の名目 CI 除外・c53 自身は
事後・年符号交互として null と判定）。A の B1 は FEED_TOL 記帳を外すと CI 下限が −0.0023 に落ちることを示した。
ここでは **独立な 2 本目の殺し方**＝ドリフト・プラセボで、同じ数字が「出口規則の価値」でなく「持ち越し中の方向性ドリフト」で
説明できるかを測る。

=== 事前固定（数字を見る前に書く・seed 20261119・A と同一の W'・同一の budget 規約）===
プラセボ P1「無作為出口」: 各 W' 本について、再開足 r から budget = 288 − k_c 本の中の **一様乱数の 1 本** で close 決済した
  場合の ΔR_rand = SGN·(close − entry)/risk − cl_kc を 200 ドロー。SL/TP の規則を一切使わない＝**出口規則の情報量ゼロ**。
プラセボ P2「側の反転」: SGN を反転（BUY↔SELL・SL/TP 水準も鏡像）して本番規則で再シミュレーション＝ΔR_flip。
  持ち越しの価値が**方向に無差別な幾何**なら ΔR_flip ≈ ΔR_carry、**上昇ドリフトへの BUY 露出**なら符号が反転する。
判定（窓別・在/外/近年）:
  **BREAK 条件（論理和）** = 近年の H_B1 の読み「持ち越しに価値がある（かもしれない）」が壊れるのは
  (a) 無作為出口 ΔR_rand の平均が 規則ベース ΔR_carry の **≥ 50%**（＝出口規則は寄与していない・ドリフトだけ）**または**
  (b) ΔR_flip の符号が ΔR_carry と逆 かつ |ΔR_flip| が |ΔR_carry| の **≥ 50%**（＝側の露出で出来ている）。
記述: 年別・BUY/SELL 別の ΔR_carry、近年の BUY 比率と金の窓内リターン。
多重検定: 判定セルは 1 つ（近年 H_B1 に対する P1/P2 の論理和）。在/外 は記述として併記。
出力は data/refute_c53_weekendgap_c.md のみ。発注・本番編集・プロセス接触・MT5・プロップ・外部通信 無し。
"""
import os, json, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c53_weekendgap_c.md")
NY = "America/New_York"; rng = np.random.default_rng(20261119)
L = []
def say(s=""): print(s, flush=True); L.append(s)
def verdict(tag, cond, obs, broken):
    say(f"- **[{tag}] 判定 = {'BROKEN' if broken else 'not broken'}**")
    say(f"    - 条件: {cond}")
    say(f"    - 観測: {obs}")
say(f"# [REFUTE c53-C] H_B1 近年 +0.3485 にドリフト・プラセボを当てる — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c53_weekendgap_c.py)")

J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
X = pd.DataFrame(J["trades"]).sort_values("entry_time", kind="stable").reset_index(drop=True)
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64); d = np.diff(off) - 1
h = X["hold"].to_numpy().astype(int); et = X["entry_time"].to_numpy()
for t in np.unique(et[pd.Series(et).duplicated(keep=False).to_numpy()]):
    g = np.where(et == t)[0]
    if not np.array_equal(h[g], d[g]):
        perm = [int(g[list(h[g]).index(v)]) for v in d[g]]; X.iloc[g] = X.iloc[perm].to_numpy()
X = X.reset_index(drop=True); N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy(); B = X["b"].to_numpy()
FT = J["frozen"]["FEED_TOL"]; MAXH = J["frozen"]["MAX_HOLD"]; ft = FT / RISK
P = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); TS = P["ts"].astype(np.int64); O = P["open"]; H = P["high"]; LO = P["low"]; C = P["close"]
def idx_of(ts):
    i = np.searchsorted(TS, ts); i2 = np.minimum(i, len(TS) - 1); return np.where(TS[i2] == ts, i2, -1)
e_ny = pd.to_datetime(ET, unit="s", utc=True).tz_convert(NY)
sess = pd.DatetimeIndex(pd.to_datetime(list((e_ny + pd.Timedelta(hours=6)).date)))
isF = sess.weekday.to_numpy() == 4
ts_c = np.array([pd.Timestamp(dd.year, dd.month, dd.day, 16, 55, tz=NY).value // 10**9 if f else -1 for dd, f in zip(sess, isF)], dtype=np.int64)
k_c = np.where(isF, (ts_c - ET) // 300, -1)
cand = np.where(isF & (HOLD >= k_c + 1))[0]
entry = np.full(N, np.nan); rngE = np.full(N, np.nan)
for i in cand:
    ests = []
    for j in (1, 2, 3):
        ii = idx_of(np.array([ET[i] + 300 * j]))[0]
        if ii >= 0: ests.append(C[ii] - SGN[i] * clR[off[i] + j] * RISK[i])
    entry[i] = np.median(ests); rngE[i] = max(ests) - min(ests)
ic = idx_of(np.where(isF, ts_c, TS[0]))
ok = np.zeros(N, bool)
for i in cand:
    ok[i] = (rngE[i] <= 0.02) and ic[i] >= 0 and abs(SGN[i] * clR[off[i] + k_c[i]] * RISK[i] + entry[i] - C[ic[i]]) <= 0.02
Wok = np.where(ok)[0]
reo = np.full(N, -1)
for i in Wok:
    j = ic[i] + 1; lim = min(ic[i] + 288 * 4, len(TS))
    while j < lim and not (H[j] != LO[j] or C[j] != C[j - 1]): j += 1
    if j < lim: reo[i] = j
W = Wok[reo[Wok] >= 0]
cl_kc = np.array([clR[off[i] + k_c[i]] for i in W])
say(f"- W' {len(W)}（A と同一）・k_c 範囲 {k_c[W].min()}〜{k_c[W].max()}・全本 exit=TIME {bool(np.all(EXIT[W]=='TIME'))}")

def simulate(i, sgn):
    s = sgn; rk = RISK[i]; en = entry[i]; sl = en - s * rk; tp = en + s * B[i] * rk
    budget = MAXH - k_c[i]; j0 = reo[i]
    for n, j in enumerate(range(j0, min(j0 + budget, len(TS)))):
        o, hi, lo = O[j], H[j], LO[j]
        if s > 0: hitSL_o, hitTP_o, hitSL, hitTP = o <= sl, o >= tp, lo <= sl, hi >= tp
        else:     hitSL_o, hitTP_o, hitSL, hitTP = o >= sl, o <= tp, hi >= sl, lo <= tp
        if hitSL_o or hitSL: return -1.0 + ft[i]
        if hitTP_o or hitTP: return B[i] + ft[i]
    jl = min(j0 + budget, len(TS)) - 1
    return s * (C[jl] - en) / rk

Rp = np.array([simulate(i, SGN[i]) for i in W])
Rf = np.array([simulate(i, -SGN[i]) for i in W])
dcarry = Rp - cl_kc
# cl_kc の鏡像（引けの含み損益も符号反転）
dflip = Rf - (-cl_kc)
ND = 200
drand = np.zeros((ND, len(W)))
for i_, i in enumerate(W):
    budget = MAXH - k_c[i]; j0 = reo[i]; jmax = min(j0 + budget, len(TS)) - 1
    picks = rng.integers(j0, jmax + 1, ND)
    drand[:, i_] = SGN[i] * (C[picks] - entry[i]) / RISK[i] - cl_kc[i_]

WIN = {"在 2013-20": (2013, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
say("\n## P1 無作為出口（出口規則の情報量ゼロ）・P2 側の反転")
say("| 窓 | W' | 規則 ΔR_carry | P1 無作為出口 ΔR_rand 平均 | P1 の 2.5–97.5% | P1/規則 | P2 側反転 ΔR_flip | P2/規則 | BUY 率 |")
say("|---|---|---|---|---|---|---|---|---|")
res = {}
for nm, (y0, y1) in WIN.items():
    m = ((YEAR >= y0) & (YEAR <= y1))[W]
    if not m.sum(): continue
    mu = dcarry[m].mean(); mr = drand[:, m].mean(1); mf = dflip[m].mean()
    res[nm] = dict(mu=mu, mr=mr.mean(), mf=mf)
    say(f"| {nm} | {int(m.sum())} | {mu:+.4f} | {mr.mean():+.4f} | [{np.percentile(mr,2.5):+.4f},{np.percentile(mr,97.5):+.4f}] | {mr.mean()/mu*100 if mu else float('nan'):.0f}% | {mf:+.4f} | {mf/mu*100 if mu else float('nan'):.0f}% | {np.mean(SGN[W][m]>0)*100:.1f}% |")
r = res["近年 2024-26H1"]
a = abs(r["mr"]) >= 0.50 * abs(r["mu"]) and np.sign(r["mr"]) == np.sign(r["mu"])
b = (np.sign(r["mf"]) != np.sign(r["mu"])) and abs(r["mf"]) >= 0.50 * abs(r["mu"])
verdict("C1", "近年 H_B1 について (a) 無作為出口 ΔR_rand が 規則 ΔR_carry の ≥50%（同符号） **または** (b) 側反転 ΔR_flip が逆符号 かつ |·| ≥ 50%（論理和）",
        f"(a) ΔR_rand {r['mr']:+.4f} / 規則 {r['mu']:+.4f} = {r['mr']/r['mu']*100:.0f}% → {a}／(b) ΔR_flip {r['mf']:+.4f}（{r['mf']/r['mu']*100:.0f}%・逆符号 {np.sign(r['mf'])!=np.sign(r['mu'])}） → {b}",
        a or b)

say("\n## 記述")
say("| 年 | W' | BUY 率 | mean ΔR_carry | mean ΔR_rand | mean ΔR_flip | 窓内 金 ログ変化率（引け→budget 終端） |")
say("|---|---|---|---|---|---|---|")
for y in range(2013, 2027):
    m = (YEAR == y)[W]
    if not m.sum(): continue
    dr = np.array([np.log(C[min(reo[i] + (MAXH - k_c[i]), len(TS) - 1)] / C[ic[i]]) for i in W[m]])
    say(f"| {y} | {int(m.sum())} | {np.mean(SGN[W][m]>0)*100:.0f}% | {dcarry[m].mean():+.3f} | {drand[:,m].mean():+.3f} | {dflip[m].mean():+.3f} | {dr.mean()*10000:+.1f} bp |")
for nm, (y0, y1) in WIN.items():
    m = ((YEAR >= y0) & (YEAR <= y1))[W]
    mb = m & (SGN[W] > 0); ms = m & (SGN[W] < 0)
    say(f"- {nm} 側別 mean ΔR_carry: BUY {dcarry[mb].mean():+.4f}（n {int(mb.sum())}）／SELL {dcarry[ms].mean():+.4f}（n {int(ms.sum())}）・"
        f"持ち越し中の金 平均 {np.mean([np.log(C[min(reo[i]+(MAXH-k_c[i]),len(TS)-1)]/C[ic[i]]) for i in W[m]])*10000:+.1f} bp")
say(f"\n- 実行 {time.time()-T0:.1f} s・入力 = data 配下のキャッシュ 3 本・seed 20261119・ドロー {ND}・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
