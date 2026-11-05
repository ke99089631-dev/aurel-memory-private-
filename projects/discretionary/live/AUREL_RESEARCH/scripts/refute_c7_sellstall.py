# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-05 23:20 — 対象: cycle7 (21:50) の残存反証（最重大反証に残されたもの）
  「P1 セル (k=24, B3: 含み −0.2〜+0.2R) の側別で SELL が 外 −0.137 (t −2.37, n308)・近年 −0.273 (t −2.74, n104)、
   BUY は 外 +0.070／近年 +0.121 と逆向き。もし本物なら『24 本停滞した SELL は閉じる』という近年の出口。」
  研究レーン自身は「在は SELL +0.048 で符号反転・側×壁種×3 窓=12 セルの事後 1 セル・family-wise で t2.7 は p≈0.1 水準」と
  見積もったが計算はしていない。本スクリプトはそれをコードで出す。
  cycle7 の null そのもの（P1/P2 FAIL・経過時間に出口情報なし）は再現して争わない。

読取りのみ・発注なし・scan なし・M5 読込なし・MT5 なし。入力は既存キャッシュ
  data/c1_reaccel_paths_2010_2026.json・data/refute_c4_scan_paths_2010_2026.json・data/refute_c2_fullpaths.npz。
書き込みは data/refute_c7_sellstall.md のみ。

=== 事前固定（この docstring を書いてから数字を見る・以後動かさない） ===
記帳: cycle7 と同一。R* = R + ft（SL/TP）・TIME そのまま。e = R* − cl_k。評価足 k は hold>k（決着足と混ぜない）、
      cl_k は足 k の終値（F_k 可測）。side・wall_kind・jh・risk・atr は建玉時に確定。look-ahead なし。
H0: e の分布は側に依らない。SELL×(k=24,B3) の負は、側×k×水準×窓 の格子から事後に拾った 1 セル。
Q0 再現: cycle7 §4 の数字（SELL 在 +0.048 t1.40 n912／外 −0.137 t−2.37 n308／近年 −0.273 t−2.74 n104）。
Q1 全格子の実測: 窓{在,外,近年} × k{3,6,12,24,48,96} × B{1..5} × 側{BUY,SELL} = 60 セル/窓。n<30 は欠測。
Q2（主検定）側ラベルを年層（≤2020／2021-23／2024／≥2025）内で 2000 回シャッフル。建玉中集合・e・水準は側に依らない量なので固定。
      統計量（観測 → 帰無分布で観測以上が出る割合）:
        S1 = 外 60 セルの max|t|（「外で |t|≥2.37 の側セルが 1 つある」の family-wise p）
        S2 = 近年 60 セルの max|t|
        S3 = 外 30 セルの側差（BUY−SELL）Welch |t| の max
        S4 = 30 セル×2 側で min(|t_外|, |t_近年|)（同符号のときのみ・それ以外 0）の max
             ＝「外と近年の両方で同じ側セルが同符号で強い」の family-wise p（近年⊂外 の従属も置換が自動で扱う）
        S5 = 事前に SELL×(k=24,B3) を選んでいた場合の単セル p（外 t ≤ 観測）
        S6 = 外 SELL 30 セルで e<0 の数
Q3 プラセボ（k 格子）: SELL B3 の e を k∈{3,6,12,18,24,30,36,48,96}（18/30/36 は格子外）で。k=24 だけ山なら選択効果の疑い、
      滑らかに負なら構造。B2/B4（隣接水準）の SELL k=24 も。
Q4 別分割: SELL×(k=24,B3) の e を 年別（2010..2026 の符号と t）／重ならない窓 2021-23・2024-26H1・2025-26H1／偶数年・奇数年／
      4 年刻み。外の leave-one-year-out t。外の中で 壁種{outer,mid}×JST{7-12,13-20,21-6} 5 セル Bonferroni α=0.01。
Q5 非独立・機械: SELL×(k=24,B3) 外/近年 の 建玉日クラスタ t・足 24 時点の暦日クラスタ t・クラスタ数・最大クラスタ・
      上位 3 日／上位 3 月の Σe 寄与。決着種別 SL/TP/TIME%・残り保有・種別ごとの e（記述）。
Q6 使える形: 「SELL・hold>24・cl_24∈B3 なら足 24 の終値で成行クローズ」を s∈{0,0.10,0.20,0.44} USD/本（slip を risk で R 換算）で、
      窓{在,外,近年}の SELL 全本に対する diff・t・上位10% 尻尾残存（研究レーン基準: 在 t≥2 ∧ 外 t≥1.5 ∧ 残存 ≥90%）。
      記帳は過去の反証 Q5/Q6 と同じ（R0 は gross・終値クローズに s を課す）。
Q7 もう 1 本の残存（在 (k=24,B1) +0.096 t2.95・Bonferroni 3.14 未達）: 重ならない窓・偶奇年・年別符号（記述のみ）。
判定（事前固定）:
  broken       = Q2 p(S1) > 0.05 ∧ p(S4) > 0.05 ∧ Q6 s=0.10 が研究レーン基準 FAIL。
  survived     = Q2 p(S4) < 0.01 ∧ Q4 で 2021-23 と 2025-26H1 の SELL セルがともに t ≤ −1.5 ∧ Q6 s=0.10 が基準 PASS。
  それ以外     = inconclusive。
seed 20261105。
"""
import json, os, math, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c7_sellstall.md")
NPERM = 2000; SEED = 20261105
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
    if len(a) < 3 or len(b) < 3: return float("nan"), float("nan")
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, diff / se if se > 0 else float("nan")

def t_cluster(d, g):
    d = np.asarray(d, float); m = d.mean(); r = d - m
    s = pd.Series(r).groupby(np.asarray(g)).sum().to_numpy()
    se = math.sqrt((s ** 2).sum()) / len(d)
    return (m / se if se > 0 else float("nan")), len(s), int(pd.Series(g).value_counts().max())

def top_ret(R0, R1):
    top = np.argsort(R0)[-max(1, len(R0) // 10):]
    return 100 * R1[top].sum() / R0[top].sum() if R0[top].sum() != 0 else 100.0

# ---------- load (cycle7 と同一) ----------
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
aux = {t["entry_time"]: t for t in c4["trades"]}
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
df["b"] = [aux[t]["b"] if t in aux else np.nan for t in df.entry_time]
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; off = z["off"]
n = len(df)
assert len(off) - 1 == n, "npz 本数不一致"
assert np.all(np.diff(off) == df.hold.to_numpy() + 1), "path 長 ≠ hold+1"
risk = df.risk.to_numpy(); ft = FT / risk; R0 = df.R.to_numpy(); hold = df.hold.to_numpy()
er = df.exit_reason.to_numpy(); is_slt = (er == "SL") | (er == "TP")
Rstar = R0 + ft * is_slt
side = df.side.to_numpy(); isS = side == "SELL"; year = df.year.to_numpy(); jh = df.jh.to_numpy(); wk = df.wall_kind.to_numpy()
et = df.entry_time.to_numpy(); day = et // 86400
strata = np.where(year <= 2020, 0, np.where(year <= 2023, 1, np.where(year == 2024, 2, 3)))
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
W2 = {"2021-23": (year >= 2021) & (year <= 2023), "2024-26H1": year >= 2024, "2025-26H1": year >= 2025}
KS = (3, 6, 12, 24, 48, 96); KP = (18, 30, 36)
BN = ("B1 ≤−0.5", "B2 (−0.5,−0.2]", "B3 (−0.2,+0.2)", "B4 [+0.2,+0.5)", "B5 ≥+0.5")
def binid(x):
    return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))
E = {}
for k in KS + KP:
    alive = np.nonzero(hold > k)[0]; clk = clR[off[alive] + k]
    E[k] = (alive, clk, Rstar[alive] - clk, binid(clk))

def cell(k, wm, b, sm):
    alive, clk, e, bid = E[k]; m = wm[alive] & (bid == b) & sm[alive]; return e[m], m

say(f"# AUREL [REFUTE] 2026-11-05 — cycle7 の残存反証「SELL×停滞 (k=24,B3) は 外/近年 で負」を潰す  入力 {n} 本  {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c7_sellstall.py)")
say(f"FEED_TOL={FT}、ft 平均 {ft.mean():.4f}R、SL/TP {is_slt.sum()}・TIME {(~is_slt).sum()}。BUY {(~isS).sum()} / SELL {isS.sum()}。npz assert 通過（本数・path 長）。")
say()

# ---------- Q0 ----------
say("## Q0. 再現（cycle7 §4）: (k=24,B3) 側別 e = R* − cl_24")
say("| 窓 | SELL e / t / n | BUY e / t / n | 側差 SELL−BUY / Welch t |")
say("|---|---|---|---|")
for wn, wm in W.items():
    es, _ = cell(24, wm, 2, isS); eb, _ = cell(24, wm, 2, ~isS); d, tw = welch(es, eb)
    say(f"| {wn} | {es.mean():+.4f} / {tstat(es)[0]:+.2f} / {len(es)} | {eb.mean():+.4f} / {tstat(eb)[0]:+.2f} / {len(eb)} | {d:+.4f} / {tw:+.2f} |")
say()

# ---------- Q1 grid + permutation machinery ----------
WN3 = list(W.keys())
def grid_stats(sellmask):
    """returns dict wn -> arrays mean[6,5,2], t[6,5,2], n[6,5,2], var[6,5,2] (side 0=BUY,1=SELL); n<30 → nan"""
    out = {}
    for wn in WN3:
        wm = W[wn]
        mean = np.full((6, 5, 2), np.nan); tt = np.full((6, 5, 2), np.nan); nn = np.zeros((6, 5, 2), int); vv = np.full((6, 5, 2), np.nan)
        for ik, k in enumerate(KS):
            alive, clk, e, bid = E[k]; wa = wm[alive]
            g = (bid * 2 + sellmask[alive].astype(int))[wa]; ee = e[wa]
            cnt = np.bincount(g, minlength=10); s1 = np.bincount(g, weights=ee, minlength=10); s2 = np.bincount(g, weights=ee * ee, minlength=10)
            with np.errstate(invalid="ignore", divide="ignore"):
                mu = s1 / cnt; var = (s2 - cnt * mu * mu) / (cnt - 1); t = mu / np.sqrt(var / cnt)
            ok = cnt >= 30
            mu = np.where(ok, mu, np.nan); t = np.where(ok, t, np.nan); var = np.where(ok, var, np.nan)
            mean[ik] = mu.reshape(5, 2); tt[ik] = t.reshape(5, 2); nn[ik] = cnt.reshape(5, 2); vv[ik] = var.reshape(5, 2)
        out[wn] = (mean, tt, nn, vv)
    return out

def pattern(G):
    mo, to, no, vo = G["外2021-26"]; mr, tr, nr, vr = G["近年2024-26"]
    S1 = np.nanmax(np.abs(to)); S2 = np.nanmax(np.abs(tr))
    with np.errstate(invalid="ignore", divide="ignore"):
        gap = (mo[:, :, 0] - mo[:, :, 1]) / np.sqrt(vo[:, :, 0] / no[:, :, 0] + vo[:, :, 1] / no[:, :, 1])
    S3 = np.nanmax(np.abs(gap))
    same = np.sign(to) == np.sign(tr)
    joint = np.where(same, np.minimum(np.abs(to), np.abs(tr)), 0.0); joint = np.where(np.isnan(joint), 0.0, joint)
    S4 = joint.max()
    S5 = to[3, 2, 1]
    S6 = int(np.nansum(mo[:, :, 1] < 0))
    return S1, S2, S3, S4, S5, S6

G_obs = grid_stats(isS)
say("## Q1. 全格子の実測 — SELL セル（k × B）e / t / n（n<30 は欠測）。BUY は要約のみ。")
for wn in WN3:
    mean, tt, nn, vv = G_obs[wn]
    say(f"### {wn}（SELL）")
    say("| k \\ B | " + " | ".join(BN) + " |"); say("|---|" + "---|" * 5)
    for ik, k in enumerate(KS):
        row = []
        for b in range(5):
            row.append(f"n={nn[ik,b,1]}" if np.isnan(tt[ik, b, 1]) else f"{mean[ik,b,1]:+.3f} / {tt[ik,b,1]:+.2f} / {nn[ik,b,1]}")
        say(f"| k={k} | " + " | ".join(row) + " |")
    ts_s = tt[:, :, 1][~np.isnan(tt[:, :, 1])]; ts_b = tt[:, :, 0][~np.isnan(tt[:, :, 0])]
    say(f"SELL {len(ts_s)} セル: |t|>2 **{(np.abs(ts_s)>2).sum()}**（期待 {0.0455*len(ts_s):.1f}）・max|t| {np.abs(ts_s).max():.2f}・e<0 {int((mean[:,:,1][~np.isnan(mean[:,:,1])]<0).sum())}/{len(ts_s)}・t sd {ts_s.std(ddof=1):.2f}。"
        f" BUY {len(ts_b)} セル: |t|>2 {(np.abs(ts_b)>2).sum()}・max|t| {np.abs(ts_b).max():.2f}・t sd {ts_b.std(ddof=1):.2f}。")
    say()
obs = pattern(G_obs)
say(f"観測統計量: S1 外 max|t| {obs[0]:.2f}／S2 近年 max|t| {obs[1]:.2f}／S3 外 側差 max|t| {obs[2]:.2f}／S4 外∧近年 同符号 min|t| の max {obs[3]:.2f}／S5 SELL(k24,B3) 外 t {obs[4]:+.2f}／S6 外 SELL e<0 セル数 {obs[5]}/30")
# which cells attain S1/S2/S4
mo, to, no, vo = G_obs["外2021-26"]; mr, tr, nr, vr = G_obs["近年2024-26"]
i1 = np.unravel_index(np.nanargmax(np.abs(to)), to.shape); i2 = np.unravel_index(np.nanargmax(np.abs(tr)), tr.shape)
say(f"S1 のセル: k={KS[i1[0]]} {BN[i1[1]]} {'SELL' if i1[2] else 'BUY'} t {to[i1]:+.2f}；S2 のセル: k={KS[i2[0]]} {BN[i2[1]]} {'SELL' if i2[2] else 'BUY'} t {tr[i2]:+.2f}")
say()

# ---------- Q2 permutation ----------
say(f"## Q2. 主検定: 側ラベルを年層内で {NPERM} 回シャッフル（建玉中集合・e・水準は固定）")
rng = np.random.default_rng(SEED)
S = np.empty((NPERM, 6))
idx_by_stratum = [np.nonzero(strata == g)[0] for g in range(4)]
for r in range(NPERM):
    lb = isS.copy()
    for ii in idx_by_stratum: lb[ii] = isS[ii][rng.permutation(len(ii))]
    S[r] = pattern(grid_stats(lb))
p1 = np.mean(S[:, 0] >= obs[0]); p2 = np.mean(S[:, 1] >= obs[1]); p3 = np.mean(S[:, 2] >= obs[2]); p4 = np.mean(S[:, 3] >= obs[3])
p5 = np.mean(S[:, 4] <= obs[4]); p6 = np.mean(S[:, 5] >= obs[5])
say("| 統計量 | 観測 | 帰無 中央値 | 帰無 95%点 | p |")
say("|---|---|---|---|---|")
say(f"| S1 外 60 セル max\\|t\\| | {obs[0]:.2f} | {np.median(S[:,0]):.2f} | {np.percentile(S[:,0],95):.2f} | **{p1:.3f}** |")
say(f"| S2 近年 60 セル max\\|t\\| | {obs[1]:.2f} | {np.median(S[:,1]):.2f} | {np.percentile(S[:,1],95):.2f} | **{p2:.3f}** |")
say(f"| S3 外 30 セル 側差 max\\|t\\| | {obs[2]:.2f} | {np.median(S[:,2]):.2f} | {np.percentile(S[:,2],95):.2f} | {p3:.3f} |")
say(f"| S4 外∧近年 同符号 min\\|t\\| の max | {obs[3]:.2f} | {np.median(S[:,3]):.2f} | {np.percentile(S[:,3],95):.2f} | **{p4:.3f}** |")
say(f"| S5 事前選択なら: SELL(k24,B3) 外 t ≤ {obs[4]:+.2f} | {obs[4]:+.2f} | {np.median(S[:,4]):+.2f} | {np.percentile(S[:,4],5):+.2f} (5%点) | {p5:.3f} |")
say(f"| S6 外 SELL e<0 セル数 /30 | {obs[5]} | {np.median(S[:,5]):.0f} | {np.percentile(S[:,5],95):.0f} | {p6:.3f} |")
say(f"置換 {time.time()-t0:.0f}s 時点。")
say()

# ---------- Q3 placebo along k ----------
say("## Q3. プラセボ（k 格子・格子外 18/30/36 を含む）: B3 の側別 e / t / n")
say("| k | 在 SELL | 外 SELL | 近年 SELL | 外 BUY | 近年 BUY | 外 側差 SELL−BUY / Welch t |")
say("|---|---|---|---|---|---|---|")
for k in sorted(KS + KP):
    row = [f"k={k}"]
    for wn in WN3:
        es, _ = cell(k, W[wn], 2, isS); row.append(f"{es.mean():+.3f} / {tstat(es)[0]:+.2f} / {len(es)}" if len(es) >= 30 else f"n={len(es)}")
    for wn in ("外2021-26", "近年2024-26"):
        eb, _ = cell(k, W[wn], 2, ~isS); row.append(f"{eb.mean():+.3f} / {tstat(eb)[0]:+.2f} / {len(eb)}" if len(eb) >= 30 else f"n={len(eb)}")
    es, _ = cell(k, W["外2021-26"], 2, isS); eb, _ = cell(k, W["外2021-26"], 2, ~isS); d, tw = welch(es, eb)
    row.append(f"{d:+.3f} / {tw:+.2f}")
    say("| " + " | ".join(row) + " |")
say("隣接水準（k=24・SELL）: " + "；".join(f"{BN[b]} 外 {cell(24, W['外2021-26'], b, isS)[0].mean():+.3f} (t{tstat(cell(24, W['外2021-26'], b, isS)[0])[0]:+.2f}) / 近年 {cell(24, W['近年2024-26'], b, isS)[0].mean():+.3f} (t{tstat(cell(24, W['近年2024-26'], b, isS)[0])[0]:+.2f})" for b in (1, 2, 3)))
say()

# ---------- Q4 splits ----------
say("## Q4. 別分割: SELL×(k=24,B3) の e")
alive24, cl24, e24, bid24 = E[24]
base = (bid24 == 2) & isS[alive24]
yrs = year[alive24]
say("| 年 | n | e | t |"); say("|---|---|---|---|")
neg_years = 0; tot_years = 0
for y in range(2010, 2027):
    m = base & (yrs == y)
    if m.sum() < 10: say(f"| {y} | {m.sum()} | — | — |"); continue
    tot_years += 1; neg_years += int(e24[m].mean() < 0)
    say(f"| {y} | {m.sum()} | {e24[m].mean():+.3f} | {tstat(e24[m])[0]:+.2f} |")
say(f"年別 e<0: **{neg_years}/{tot_years}**（n≥10 の年）。")
say("| 分割 | n | SELL e / t | BUY e / t | 側差 / Welch t |"); say("|---|---|---|---|---|")
splits = list(W2.items()) + [("偶数年", year % 2 == 0), ("奇数年", year % 2 == 1), ("2010-13", year <= 2013), ("2014-17", (year >= 2014) & (year <= 2017)), ("2018-21", (year >= 2018) & (year <= 2021)), ("2022-26", year >= 2022)]
Q4t = {}
for lab, wm in splits:
    es, _ = cell(24, wm, 2, isS); eb, _ = cell(24, wm, 2, ~isS); d, tw = welch(es, eb); Q4t[lab] = tstat(es)[0]
    say(f"| {lab} | {len(es)} | {es.mean():+.4f} / {tstat(es)[0]:+.2f} | {eb.mean():+.4f} / {tstat(eb)[0]:+.2f} | {d:+.4f} / {tw:+.2f} |")
# LOO in 外
mo_ = W["外2021-26"][alive24] & base
loo = []
for y in range(2021, 2027):
    m = mo_ & (yrs != y); loo.append(f"−{y}: {e24[m].mean():+.3f} (t{tstat(e24[m])[0]:+.2f})")
say("外 leave-one-year-out: " + "／".join(loo))
# regime cells within 外 SELL
say("| 外 SELL 部分集合 | n | e | t | p |"); say("|---|---|---|---|---|")
sub = [("outer", wk[alive24] == "outer"), ("mid", wk[alive24] == "mid"), ("JST7-12", (jh[alive24] >= 7) & (jh[alive24] <= 12)), ("JST13-20", (jh[alive24] >= 13) & (jh[alive24] <= 20)), ("JST21-6", (jh[alive24] >= 21) | (jh[alive24] <= 6))]
sig = 0
for lab, mm in sub:
    m = mo_ & mm; t_, p_ = tstat(e24[m]); sig += int(p_ < 0.01 and e24[m].mean() < 0)
    say(f"| {lab} | {m.sum()} | {e24[m].mean():+.3f} | {t_:+.2f} | {p_:.3f} |")
say(f"Bonferroni(α=0.01) 有意: **{sig}/5**。")
say()

# ---------- Q5 dependence / mechanics ----------
say("## Q5. 非独立・機械（SELL×(k=24,B3)）")
day24 = (et + 24 * 300) // 86400
for wn in ("外2021-26", "近年2024-26"):
    m = W[wn][alive24] & base; ee = e24[m]; ai = alive24[m]
    tc1, nc1, mx1 = t_cluster(ee, day[ai]); tc2, nc2, mx2 = t_cluster(ee, day24[ai])
    s_day = pd.Series(ee).groupby(day24[ai]).sum().sort_values()
    s_mon = pd.Series(ee).groupby(pd.to_datetime(et[ai], unit="s").to_period("M").astype(str)).sum().sort_values()
    top3d = s_day.iloc[:3].sum() / ee.sum() * 100 if ee.sum() != 0 else float("nan")
    top3m = s_mon.iloc[:3].sum() / ee.sum() * 100 if ee.sum() != 0 else float("nan")
    ex = er[ai]
    d3 = ", ".join("%s %+.1f" % (pd.Timestamp(int(d_) * 86400, unit="s").date(), v) for d_, v in s_day.iloc[:3].items())
    m3 = ", ".join("%s %+.1f" % (k_, v) for k_, v in s_mon.iloc[:3].items())
    say(f"- {wn} n={m.sum()}: 通常 t {tstat(ee)[0]:+.2f}／建玉日クラスタ t **{tc1:+.2f}**（{nc1} 日・最大 {mx1} 本）／足24 暦日クラスタ t **{tc2:+.2f}**（{nc2} 日・最大 {mx2} 本）。"
        f" Σe={ee.sum():+.1f}R、最も負の 3 日の寄与 **{top3d:.0f}%**（{d3}）、最も負の 3 月の寄与 {top3m:.0f}%（{m3}）。")
    say(f"  決着 SL {100*(ex=='SL').mean():.0f}% / TP {100*(ex=='TP').mean():.0f}% / TIME {100*(ex=='TIME').mean():.0f}%・残り保有 中央値 {np.median(hold[ai]-24):.0f} 本・b 中央値 {np.nanmedian(df.b.to_numpy()[ai]):.2f}。"
        f" 種別 e: SL {ee[ex=='SL'].mean():+.3f} (n{(ex=='SL').sum()})／TP {ee[ex=='TP'].mean():+.3f} (n{(ex=='TP').sum()})／TIME {ee[ex=='TIME'].mean():+.3f} (n{(ex=='TIME').sum()})（出口条件づけ・記述のみ）。")
    mb = W[wn][alive24] & (bid24 == 2) & ~isS[alive24]; exb = er[alive24[mb]]
    say(f"  対照 BUY n={mb.sum()}: SL {100*(exb=='SL').mean():.0f}% / TP {100*(exb=='TP').mean():.0f}% / TIME {100*(exb=='TIME').mean():.0f}%・b 中央値 {np.nanmedian(df.b.to_numpy()[alive24[mb]]):.2f}。")
say()

# ---------- Q6 strategy ----------
say("## Q6. 使える形「SELL・hold>24・cl_24∈B3 → 足 24 終値で成行クローズ」 s∈{0,0.10,0.20,0.44} USD（SELL 全本に対する diff・R0 は gross）")
say("| s | 在 diff / t | 外 diff / t | 近年 diff / t | 発動 在/外/近年 | 発動本のみ 外 diff / t | 上位10% 残存 在 / 外 / 近年 |")
say("|---|---|---|---|---|---|---|")
sel = np.zeros(n, bool); sel[alive24[base]] = True
cl24_full = np.full(n, np.nan); cl24_full[alive24] = cl24
Q6 = {}
for s in (0.0, 0.10, 0.20, 0.44):
    R1 = R0.copy(); R1[sel] = cl24_full[sel] - s / risk[sel]; d = R1 - R0
    row = [f"{s:.2f}"]; res = {}
    for wn in WN3:
        m = isS & W[wn]; t_ = tstat(d[m])[0]; res[wn] = (d[m].mean(), t_, top_ret(R0[m], R1[m]), (m & sel).sum())
        row.append(f"{d[m].mean():+.4f} / {t_:+.2f}")
    row.append("/".join(str(res[wn][3]) for wn in WN3))
    mo2 = isS & W["外2021-26"] & sel; row.append(f"{d[mo2].mean():+.3f} / {tstat(d[mo2])[0]:+.2f}")
    row.append(" / ".join(f"{res[wn][2]:.0f}%" for wn in WN3))
    say("| " + " | ".join(row) + " |"); Q6[s] = res
r = Q6[0.10]
pass6 = (r["在2010-20"][1] >= 2) and (r["外2021-26"][1] >= 1.5) and (r["在2010-20"][2] >= 90) and (r["外2021-26"][2] >= 90)
say(f"研究レーン基準（在 t≥2 ∧ 外 t≥1.5 ∧ 残存 ≥90%）s=0.10: **{'PASS' if pass6 else 'FAIL'}**（在 t {r['在2010-20'][1]:+.2f}・外 t {r['外2021-26'][1]:+.2f}・残存 {r['在2010-20'][2]:.0f}%/{r['外2021-26'][2]:.0f}%）。")
say()

# ---------- Q7 other leftover ----------
say("## Q7. もう 1 本の残存: (k=24,B1 ≤−0.5) 在 +0.096 (t2.95)（記述のみ）")
allm = np.ones(n, bool)
parts = []
for lab, wm in [("在2010-20", W["在2010-20"]), ("外2021-26", W["外2021-26"])] + list(W2.items()) + [("偶数年", year % 2 == 0), ("奇数年", year % 2 == 1)]:
    e_, _ = cell(24, wm, 0, allm); parts.append(f"{lab} {e_.mean():+.3f} (t{tstat(e_)[0]:+.2f}, n{len(e_)})")
say("；".join(parts))
negy = 0; toty = 0
for y in range(2010, 2027):
    m = (bid24 == 0) & (yrs == y)
    if m.sum() >= 10: toty += 1; negy += int(e24[m].mean() > 0)
say(f"年別 e>0: {negy}/{toty}（n≥10 の年）。")
say()

# ---------- verdict ----------
say("## 判定（事前固定の規則）")
say(f"- Q2: p(S1) {p1:.3f}・p(S4) {p4:.3f}・p(S2) {p2:.3f}・単セル p(S5) {p5:.3f}")
say(f"- Q4: 2021-23 SELL t {Q4t['2021-23']:+.2f}・2025-26H1 SELL t {Q4t['2025-26H1']:+.2f}・年別 e<0 {neg_years}/{tot_years}")
say(f"- Q6 s=0.10 基準: {'PASS' if pass6 else 'FAIL'}")
if p1 > 0.05 and p4 > 0.05 and not pass6: v = "broken"
elif p4 < 0.01 and Q4t["2021-23"] <= -1.5 and Q4t["2025-26H1"] <= -1.5 and pass6: v = "survived"
else: v = "inconclusive"
say(f"- 機械判定: **{v}**（{time.time()-t0:.0f}s）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
