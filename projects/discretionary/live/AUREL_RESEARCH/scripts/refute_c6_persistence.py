# -*- coding: utf-8 -*-
"""
[REFUTE c6] 2026-11-05 20:20 — 対象: cycle6 (18:50)「成績の時間持続性 = null」と、その副産物
「週/月平均R の分散は本レベル標本ノイズで全部説明される（レジーム由来 σ_μ ≤0.02〜0.03R）」、
および残存反証「月次・外 trailing 2 群差 +0.0495 (t1.92)」。

=== 事前固定（この docstring を書いてから数字を見る） ===
壊しに行く主張（cycle6 本文から引用）:
  (A) 副産物: 「超過分散 ≈0・σ_μ ≤0.02〜0.03R」= 真の期間平均R のレジーム揺れは実用サイズ以下。
      → 中央値 SE との素朴な引き算で、推定誤差（CI）も分散分解の正しい式（E[s²/n]）も無い。
  (B) 判定: 「方法自体は本数の持続（r +0.4〜+0.7）を明瞭に拾うので『検出できない』は方法の欠陥ではない」
      → 本数 n の信頼性（reliability）は ≈1 だが、週平均R の信頼性 = σ_μ²/(σ_μ²+SE²) は σ_μ=0.05R・SE=0.23R で 4.5%。
        持続が完全（φ=1）でも lag1 r の期待値は 0.045。陽性対照は別の量の検出力を示しただけ。
  (C) 残存反証: 月次・外 trailing diff +0.0495 (t1.92・本レベル t1.99)。
データ: data/refute_c4_scan_paths_2010_2026.json（19404 本・entry_time/R/hold/b/exit/year）。scan 無し・M5 無し・MT5 無し。
窓: 在 ≤2020 / 外 ≥2021 / 近年 ≥2024（cycle6 と同じ）。集計 UTC 週（W-SUN）・暦月・四半期・半期・年。有効 = n≥5。

Q0 再現: 週 lag1 r 在/外、月 外 trailing diff t、週 sd vs 中央値 SE。cycle6 の md と一致すること。
Q1 分散分解を正しく: σ_μ² = Var(m_w) − mean(s_w²/n_w)（s_w は期間内 sd。n_w<2 は pooled sd）。
    期間ブロック bootstrap 2000 回で σ_μ の 95% CI（負は 0 に切る）。週・月・四半期・半期・年 × 3 窓。
    さらに一元配置の置換 F 検定（本レベル R を窓内でシャッフル・期間所属は固定・2000 回）: 「期間平均が標本ノイズ以上に違う」の p。
    5 尺度×3 窓=15 セル・Bonferroni α=0.05/15。TP 指標（R>0）版も併記（重い尻尾の影響確認）。
Q2 検出力シミュレーション（cycle6 の M1/M2 判定規則をそのまま使う）:
    実データの R に、週ごとの AR(1) レジーム μ_w（sd σ_μ・φ）を加えて（本の週所属は実データ）、P1（在 p<0.05∧外 p<0.10・r>0）
    と P2（在 t≥2∧外 t≥1.5）を再計算。σ_μ∈{0.03,0.05,0.10}R × φ∈{0.9,0.97}、各 200 回・置換 p は 400 回。
    判定規則: σ_μ=0.05・φ=0.9（「月〜季の尺度で ±0.05R 揺れるレジーム」）で P1∧P2 の検出率 <50% なら、cycle6 の null は
    「不在の証拠」でなく「検出不能」であり (B) は broken。
Q3 残存反証 (C) の family-wise: 窓内で本レベル R をシャッフル（2000 回）→ 6 セル（週/月×3 窓）の trailing diff t と Spearman ρ を
    全部再計算し、max t・max|ρ| の帰無分布。観測 max t=1.92 の p_max。別分割: trailing 長 {2,3,4,6} か月・閾値を外自身の中央値・
    2021-23 / 2024-26H1 の部分窓。判定: p_max>0.10 かつ在と符号不一致のまま → broken。
Q4 look-ahead: trailing に入る本のうち exit（≈entry+hold×5 分・週末ギャップ無視＝下限）が期間 t 開始より後の割合。
    週次でその本を除いて M2 を再計算（月次は無視できる規模のはず）。
Q5 記述（判定不使用）: 月次 TP 率・平均 b・平均R の lag1 と、TP 率と b の同月相関（cycle6 の「b が補償」疑いの確認）。

総合判定（事前）:
  (A) broken  = 週または月の σ_μ 95% 上限 ≥0.05R、または置換 F の Bonferroni 有意セルが 1 つ以上。
      survived = 全窓・全尺度で上限 <0.04R かつ F p>0.10。それ以外 inconclusive。
  (B) broken  = Q2 の検出率 <50%（σ_μ=0.05・φ=0.9）。
  (C) broken  = Q3 p_max >0.10 かつ 在 符号不一致。survived = p_max<0.05 かつ別分割で同符号。
D2 注意: 16 年 pooled の平均R 水準（−0.046 gross）は edge の判定に使わない。本件は「期間平均の分散」と「持続性の検出力」だけ。
seed 20261105。
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.stats import spearmanr, pearsonr

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "refute_c6_persistence.md")
rng = np.random.default_rng(20261105)
lines = []
def say(s=""): print(s, flush=True); lines.append(s)

d = json.load(open(os.path.join(ROOT, "data", "refute_c4_scan_paths_2010_2026.json")))
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["exit_ts"] = tr["ts"] + pd.to_timedelta(tr["hold"] * 5, unit="m")   # 下限（週末ギャップ無視）
tr["tp"] = (tr["R"] > 0).astype(float)
for per, code in (("week", "W-SUN"), ("month", "M"), ("quarter", "Q"), ("half", None), ("yearP", "Y")):   # 'year' 列（窓マスク）を上書きしない
    if per == "half":
        tr[per] = tr["ts"].dt.year * 2 + (tr["ts"].dt.month > 6).astype(int)
    else:
        tr[per] = tr["ts"].dt.to_period(code).apply(lambda p: p.ordinal)
say(f"# [REFUTE c6] 成績の持続性 null・分散分解・検出力 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c6_persistence.py)")
say(f"trades n={len(tr)}  R mean {tr.R.mean():+.4f} sd {tr.R.std():.3f}")

W = {"在2010-20": tr.year <= 2020, "外2021-26": tr.year >= 2021, "近年2024-26": tr.year >= 2024}
NMIN = 5
NPERM = 2000

# ---------- 基本集計（numpy・高速） ----------
def period_stats(codes, R, nmin=NMIN):
    """期間コード→ (uniq codes, n, mean, within var)  有効 n>=nmin のみ返す"""
    u, inv = np.unique(codes, return_inverse=True)
    n = np.bincount(inv).astype(float)
    s = np.bincount(inv, weights=R); m = s / n
    ss = np.bincount(inv, weights=R * R)
    var = np.where(n > 1, (ss - n * m * m) / np.maximum(n - 1, 1), np.nan)
    ok = n >= nmin
    return u[ok], n[ok], m[ok], var[ok], inv, ok

def lag_r_vals(u, m, k=1):
    idx = {c: i for i, c in enumerate(u)}
    a = []; b = []
    for i, c in enumerate(u):
        j = idx.get(c + k)
        if j is not None: a.append(m[i]); b.append(m[j])
    a = np.asarray(a); b = np.asarray(b)
    return (pearsonr(a, b)[0] if len(a) > 3 else np.nan), len(a)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    diff = a.mean() - b.mean(); se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, (diff / se if se > 0 else np.nan)

def trailing_table(codes, R, L, nmin_trail, nmin=NMIN):
    """全期間（有効でなくても）の sum/n を作り、有効期間 t の直前 L 期間の本の平均R を trailing に"""
    u, inv = np.unique(codes, return_inverse=True)
    n = np.bincount(inv).astype(float); s = np.bincount(inv, weights=R)
    full = np.arange(u.min(), u.max() + 1)
    nn = np.zeros(len(full)); ss = np.zeros(len(full))
    nn[u - full[0]] = n; ss[u - full[0]] = s
    cn = np.concatenate([[0], np.cumsum(nn)]); cs = np.concatenate([[0], np.cumsum(ss)])
    out = []
    for i in range(len(full)):
        if nn[i] < nmin: continue
        lo = max(0, i - L); nt = cn[i] - cn[lo]
        if nt < nmin_trail: continue
        out.append((full[i], (cs[i] - cs[lo]) / nt, ss[i] / nn[i], nn[i]))
    T = np.array(out) if out else np.zeros((0, 4))
    return T  # cols: per, trail, mR, n

def m2(codes, R, L, nmin_trail, thr=None):
    T = trailing_table(codes, R, L, nmin_trail)
    if len(T) < 10: return dict(rho=np.nan, diff=np.nan, t=np.nan, thr=np.nan, ng=0, nb=0, T=T)
    rho = spearmanr(T[:, 1], T[:, 2])[0]
    if thr is None: thr = float(np.median(T[:, 1]))
    good = T[:, 1] > thr
    diff, t = welch(T[good, 2], T[~good, 2])
    return dict(rho=rho, diff=diff, t=t, thr=thr, ng=int(good.sum()), nb=int((~good).sum()), T=T)

TRAIL = {"week": (4, 10), "month": (3, 20)}

# ---------- Q0 再現 ----------
say("\n## Q0 再現（cycle6 md: 週 lag1 r 在 −0.059／外 −0.032／近年 −0.120、月次 外 trailing diff +0.0495 t1.92、週 sd 0.232 vs SE中央値 0.231）")
thr_in = {}
rep = {}
for per in ("week", "month"):
    for wn, msk in W.items():
        R = tr.loc[msk, "R"].to_numpy(); c = tr.loc[msk, per].to_numpy()
        u, n, m, v, _, _ = period_stats(c, R)
        r1, np1 = lag_r_vals(u, m, 1)
        if wn == "在2010-20":
            T0 = trailing_table(c, R, *TRAIL[per]); thr_in[per] = float(np.median(T0[:, 1]))
        res = m2(c, R, *TRAIL[per], thr=thr_in[per])
        rep[(per, wn)] = dict(r1=r1, t=res["t"], diff=res["diff"], rho=res["rho"])
        se_med = np.median(R.std(ddof=1) / np.sqrt(n))
        say(f"- {per} {wn}: 有効 {len(u)} / lag1 r {r1:+.3f} (pairs {np1}) / 期間平均R sd {m.std(ddof=1):.3f} vs 中央値SE {se_med:.3f} / "
            f"trailing ρ {res['rho']:+.4f} diff {res['diff']:+.4f} t {res['t']:+.2f} (good {res['ng']} bad {res['nb']})")
ok0 = (abs(rep[("week", "在2010-20")]["r1"] + 0.059) < 0.003 and abs(rep[("week", "外2021-26")]["r1"] + 0.032) < 0.003
       and abs(rep[("month", "外2021-26")]["t"] - 1.92) < 0.05)
say(f"- 再現: {'OK' if ok0 else 'NG（要確認）'}")

# ---------- Q1 分散分解・置換 F ----------
say("\n## Q1 分散分解を正しく（σ_μ² = Var(m_w) − mean(s_w²/n_w)・期間ブロック bootstrap 95%CI）＋ 置換 F 検定（本レベル R を窓内シャッフル・期間所属固定）")
say("Bonferroni α = 0.05/15 = 0.0033（5 尺度×3 窓）。TP 指標版は尻尾の影響確認（記述）。")
scales = ["week", "month", "quarter", "half", "yearP"]
assert tr.year.min() == 2010 and tr.year.max() == 2026, "year 列が壊れている"
assert int((tr.year <= 2020).sum()) == 11696, f"在の本数 {int((tr.year<=2020).sum())} ≠ 11696"
sig_cells = []; upper_bounds = {}
for per in scales:
    for wn, msk in W.items():
        R = tr.loc[msk, "R"].to_numpy(); c = tr.loc[msk, per].to_numpy(); tp = tr.loc[msk, "tp"].to_numpy()
        u, n, m, v, inv, ok = period_stats(c, R)
        if len(u) < 4:
            say(f"- {per} {wn}: 有効期間 {len(u)} <4 → skip"); continue
        pooled = R.var(ddof=1)
        v_use = np.where(np.isnan(v), pooled, v)
        noise = np.mean(v_use / n)
        var_m = m.var(ddof=1)
        sig2 = var_m - noise
        # bootstrap over periods
        B = 2000; bs = np.empty(B)
        for b_ in range(B):
            ii = rng.integers(0, len(u), len(u))
            bs[b_] = m[ii].var(ddof=1) - np.mean(v_use[ii] / n[ii])
        lo, hi = np.quantile(bs, [0.025, 0.975])
        s_hat = np.sqrt(max(sig2, 0)); s_hi = np.sqrt(max(hi, 0))
        upper_bounds[(per, wn)] = s_hi
        # permutation F (one-way ANOVA), 全期間（有効条件なし・所属固定）
        uu, inv_all = np.unique(c, return_inverse=True)
        nall = np.bincount(inv_all).astype(float); k = len(uu); N = len(R)
        def Fstat(x):
            mm = np.bincount(inv_all, weights=x) / nall
            gm = x.mean()
            ssb = np.sum(nall * (mm - gm) ** 2); sst = np.sum((x - gm) ** 2)
            ssw = sst - ssb
            return (ssb / (k - 1)) / (ssw / (N - k))
        F_obs = Fstat(R); F_tp = Fstat(tp)
        Fn = np.empty(NPERM); Fn_tp = np.empty(NPERM)
        for p_ in range(NPERM):
            perm = rng.permutation(N)
            Fn[p_] = Fstat(R[perm]); Fn_tp[p_] = Fstat(tp[perm])
        pF = (Fn >= F_obs).mean(); pF_tp = (Fn_tp >= F_tp).mean()
        if pF < 0.05 / 15: sig_cells.append((per, wn, pF))
        # 期待 lag1 r 上限（完全持続）: reliability
        rel = max(sig2, 0) / var_m if var_m > 0 else np.nan
        say(f"- {per} {wn}: 期間 {len(u)} (本/期間 中央値 {np.median(n):.0f}) / Var(m) {var_m:.5f} − noise {noise:.5f} = σ_μ² {sig2:+.5f} → "
            f"σ_μ {s_hat:.3f}R  95%CI [{np.sqrt(max(lo,0)):.3f}, {s_hi:.3f}] / 信頼性(=完全持続時 lag1 r 上限) {rel:.3f} / "
            f"置換F: F {F_obs:.3f} p **{pF:.4f}**（帰無 F 中央値 {np.median(Fn):.3f}）/ TP版 F {F_tp:.3f} p {pF_tp:.4f}")
say(f"- Bonferroni(0.0033) 有意セル: {len(sig_cells)}/15 → {sig_cells if sig_cells else 'なし'}")
wk_hi = max(upper_bounds.get(("week", w), 0) for w in W); mo_hi = max(upper_bounds.get(("month", w), 0) for w in W)
say(f"- 週 σ_μ 95% 上限の最大 {wk_hi:.3f}R / 月 {mo_hi:.3f}R（cycle6 主張 ≤0.02〜0.03R）")

# ---------- Q2 検出力シミュレーション ----------
say("\n## Q2 検出力: 実データに週次 AR(1) レジーム μ_w を加えて cycle6 の P1/P2 を再判定（各 200 回・置換 400 回）")
say("P1 = 在 lag1 r>0 ∧ 置換 p<0.05 ∧ 外 r>0 ∧ p<0.10 / P2 = 在 trailing diff>0 ∧ t≥2 ∧ 外 diff>0 ∧ t≥1.5。H 支持 = P1∧P2。")
wk_all = tr["week"].to_numpy(); wk0 = wk_all.min(); nW = wk_all.max() - wk0 + 1
R_all = tr["R"].to_numpy()
masks = {wn: msk.to_numpy() for wn, msk in W.items()}

def perm_p_lag1(u, m, nperm=400):
    idx = {c: i for i, c in enumerate(u)}
    a_i = []; b_i = []
    for i, c in enumerate(u):
        j = idx.get(c + 1)
        if j is not None: a_i.append(i); b_i.append(j)
    a_i = np.array(a_i); b_i = np.array(b_i)
    def r_of(vals):
        a = vals[a_i]; b = vals[b_i]
        a = a - a.mean(); b = b - b.mean()
        den = np.sqrt((a * a).sum() * (b * b).sum())
        return (a * b).sum() / den if den > 0 else 0.0
    r_obs = r_of(m)
    cnt = 0
    for _ in range(nperm):
        if r_of(rng.permutation(m)) >= r_obs: cnt += 1
    return r_obs, cnt / nperm

def judge(Rvec):
    out = {}
    for wn in ("在2010-20", "外2021-26"):
        mk = masks[wn]; R = Rvec[mk]; c = wk_all[mk]
        u, n, m, v, _, _ = period_stats(c, R)
        r1, p1 = perm_p_lag1(u, m)
        if wn == "在2010-20":
            T0 = trailing_table(c, R, 4, 10); thr = float(np.median(T0[:, 1]))
        res = m2(c, R, 4, 10, thr=thr)
        out[wn] = (r1, p1, res["diff"], res["t"])
    P1 = out["在2010-20"][0] > 0 and out["在2010-20"][1] < 0.05 and out["外2021-26"][0] > 0 and out["外2021-26"][1] < 0.10
    P2 = out["在2010-20"][2] > 0 and out["在2010-20"][3] >= 2.0 and out["外2021-26"][2] > 0 and out["外2021-26"][3] >= 1.5
    return P1, P2, out

NSIM = 200
power = {}
for sig in (0.03, 0.05, 0.10):
    for phi in (0.9, 0.97):
        c1 = c2 = c12 = 0; r_in = []; t_in = []
        for s_ in range(NSIM):
            eps = rng.normal(0, sig * np.sqrt(1 - phi * phi), nW)
            mu = np.empty(nW); mu[0] = rng.normal(0, sig)
            for i in range(1, nW): mu[i] = phi * mu[i - 1] + eps[i]
            Rs = R_all + mu[wk_all - wk0]
            P1, P2, out = judge(Rs)
            c1 += P1; c2 += P2; c12 += (P1 and P2)
            r_in.append(out["在2010-20"][0]); t_in.append(out["在2010-20"][3])
        power[(sig, phi)] = (c1 / NSIM, c2 / NSIM, c12 / NSIM)
        say(f"- σ_μ={sig:.2f}R φ={phi:.2f}（半減期 {np.log(0.5)/np.log(phi):.1f} 週）: P1 検出率 {c1/NSIM:.2f} / P2 {c2/NSIM:.2f} / **P1∧P2 {c12/NSIM:.2f}** "
            f"/ 在 lag1 r 中央値 {np.median(r_in):+.3f} / 在 trailing t 中央値 {np.median(t_in):+.2f}")
# 陽性対照の信頼性（本数 n）
for wn, msk in W.items():
    R = tr.loc[msk, "R"].to_numpy(); c = tr.loc[msk, "week"].to_numpy()
    u, n, m, v, _, _ = period_stats(c, R)
    say(f"- 参考 {wn}: 週あたり本数 n の sd {n.std(ddof=1):.2f}（Poisson ノイズ √mean {np.sqrt(n.mean()):.2f}）→ 本数の信頼性 ≈ {1 - n.mean()/n.var(ddof=1):.2f}（平均R の信頼性は Q1 の 0.0x）")
pw = power[(0.05, 0.9)][2]
say(f"- 判定規則（σ_μ=0.05・φ=0.9 で P1∧P2 <0.50 → (B) broken）: 検出率 {pw:.2f} → {'(B) broken' if pw < 0.5 else '(B) survived'}")

# ---------- Q3 残存反証 (C) family-wise ----------
say("\n## Q3 残存反証「月次・外 trailing diff +0.0495 t1.92」の family-wise（窓内で本レベル R を 2000 回シャッフル → 6 セルの t・ρ を再計算）")
cells = [(per, wn) for per in ("week", "month") for wn in W]
def all_cells(Rvec):
    ts = []; rhos = []; thr_loc = {}
    for per, wn in cells:
        mk = masks[wn]; R = Rvec[mk]; c = tr.loc[mk, per].to_numpy()
        if wn == "在2010-20":
            T0 = trailing_table(c, R, *TRAIL[per]); thr_loc[per] = float(np.median(T0[:, 1]))
        res = m2(c, R, *TRAIL[per], thr=thr_loc[per])
        ts.append(res["t"]); rhos.append(res["rho"])
    return np.array(ts), np.array(rhos)
t_obs, rho_obs = all_cells(R_all)
say("- 観測 6 セル t: " + " / ".join(f"{per[:2]}{wn[:1]} {t:+.2f}" for (per, wn), t in zip(cells, t_obs)) + f" → max t {np.nanmax(t_obs):+.2f}")
say("- 観測 6 セル ρ: " + " / ".join(f"{r:+.3f}" for r in rho_obs) + f" → max|ρ| {np.nanmax(np.abs(rho_obs)):.3f}")
maxt = np.empty(NPERM); maxr = np.empty(NPERM); mo_out = np.empty(NPERM)
for p_ in range(NPERM):
    Rp = R_all.copy()
    for wn, mk in masks.items():
        if wn == "近年2024-26": continue      # 近年 ⊂ 外: 外のシャッフルで一緒に壊れる
        Rp[mk] = rng.permutation(Rp[mk])
    ts, rs = all_cells(Rp)
    maxt[p_] = np.nanmax(ts); maxr[p_] = np.nanmax(np.abs(rs)); mo_out[p_] = ts[cells.index(("month", "外2021-26"))]
p_maxt = (maxt >= np.nanmax(t_obs)).mean(); p_maxr = (maxr >= np.nanmax(np.abs(rho_obs))).mean()
p_single = (mo_out >= t_obs[cells.index(("month", "外2021-26"))]).mean()
say(f"- 帰無 max t 中央値 {np.median(maxt):.2f}・95%点 {np.quantile(maxt,.95):.2f} → 観測 {np.nanmax(t_obs):.2f} の **p_max {p_maxt:.3f}**；max|ρ| p {p_maxr:.3f}；月次外セル単独 p {p_single:.3f}")
# 別分割
say("- 別分割（月次・trailing 長 L か月・閾値 = 在中央値 / 外自身中央値）:")
mk_out = masks["外2021-26"]; R_out = R_all[mk_out]; c_out = tr.loc[mk_out, "month"].to_numpy()
mk_in = masks["在2010-20"]; R_in = R_all[mk_in]; c_in = tr.loc[mk_in, "month"].to_numpy()
for L in (2, 3, 4, 6):
    T_in = trailing_table(c_in, R_in, L, 20); thr = float(np.median(T_in[:, 1]))
    ri = m2(c_in, R_in, L, 20, thr=thr); ro = m2(c_out, R_out, L, 20, thr=thr); ro2 = m2(c_out, R_out, L, 20, thr=None)
    say(f"  L={L}: 在 diff {ri['diff']:+.4f} t {ri['t']:+.2f} ρ {ri['rho']:+.3f} / 外(在閾値) diff {ro['diff']:+.4f} t {ro['t']:+.2f} ρ {ro['rho']:+.3f} / 外(自閾値) diff {ro2['diff']:+.4f} t {ro2['t']:+.2f}")
for wn2, msk2 in (("2021-23", (tr.year >= 2021) & (tr.year <= 2023)), ("2024-26H1", tr.year >= 2024)):
    mk2 = msk2.to_numpy(); r_ = m2(tr.loc[mk2, "month"].to_numpy(), R_all[mk2], 3, 20, thr=thr_in["month"])
    say(f"  部分窓 {wn2}: diff {r_['diff']:+.4f} t {r_['t']:+.2f} ρ {r_['rho']:+.3f} (good {r_['ng']} bad {r_['nb']})")
# 使える形: good 月だけ取る → net・尻尾
res_o = m2(c_out, R_out, 3, 20, thr=thr_in["month"]); T = res_o["T"]
good_months = set(T[T[:, 1] > thr_in["month"], 0].astype(int)); bad_months = set(T[T[:, 1] <= thr_in["month"], 0].astype(int))
in_good = np.isin(c_out, list(good_months)); in_bad = np.isin(c_out, list(bad_months))
top = np.quantile(R_out, 0.9); tail_all = R_out[R_out >= top].sum(); tail_good = R_out[in_good & (R_out >= top)].sum()
cost = 0.0325
say(f"- 使える形（外・good 月のみ取引）: good 月の本 {in_good.sum()} 平均R gross {R_out[in_good].mean():+.4f} → net(−0.0325R) {R_out[in_good].mean()-cost:+.4f}；"
    f"bad 月 {in_bad.sum()} gross {R_out[in_bad].mean():+.4f}；上位10% 尻尾の残存 {tail_good/tail_all*100:.0f}%（good 月の本数シェア {in_good.sum()/(in_good.sum()+in_bad.sum())*100:.0f}%）")

# ---------- Q4 look-ahead ----------
say("\n## Q4 look-ahead: trailing に入る本の exit が期間 t の開始より後の割合（exit は entry+hold×5 分の下限）")
for per, (L, nmt) in TRAIL.items():
    for wn, mk in masks.items():
        sub = tr[mk]
        codes = sub[per].to_numpy(); ex = sub["exit_ts"].to_numpy(); en = sub["ts"].to_numpy()
        # 各本が属する期間の「次の期間開始」= 次期間の最初の本の時刻で近似 → 期間開始の厳密値: pandas Period
        if per == "week":
            start_next = (sub["ts"].dt.to_period("W-SUN") + 1).dt.start_time.to_numpy()
        else:
            start_next = (sub["ts"].dt.to_period("M") + 1).dt.start_time.to_numpy()
        leak = ex > start_next
        say(f"- {per} {wn}: 次期間にまたがる本 {leak.mean()*100:.2f}%（{leak.sum()} 本）")
        if per == "week":
            keep = ~leak
            R = sub["R"].to_numpy()
            T_full = trailing_table(codes, R, L, nmt)
            # trailing を「またがらない本だけ」で計算: 簡便に leak 本を trailing 側から除外（期間 t 側はそのまま）
            u, inv = np.unique(codes, return_inverse=True)
            n_k = np.bincount(inv, weights=keep.astype(float)); s_k = np.bincount(inv, weights=R * keep)
            n_a = np.bincount(inv).astype(float); s_a = np.bincount(inv, weights=R)
            full = np.arange(u.min(), u.max() + 1); nn = np.zeros(len(full)); ss = np.zeros(len(full)); na = np.zeros(len(full)); sa = np.zeros(len(full))
            nn[u - full[0]] = n_k; ss[u - full[0]] = s_k; na[u - full[0]] = n_a; sa[u - full[0]] = s_a
            cn = np.concatenate([[0], np.cumsum(nn)]); cs = np.concatenate([[0], np.cumsum(ss)])
            rows = []
            for i in range(len(full)):
                if na[i] < NMIN: continue
                lo = max(0, i - L); nt = cn[i] - cn[lo]
                if nt < nmt: continue
                rows.append(((cs[i] - cs[lo]) / nt, sa[i] / na[i]))
            Tk = np.array(rows)
            thr = thr_in["week"]; g = Tk[:, 0] > thr
            diff, t = welch(Tk[g, 1], Tk[~g, 1]); rho = spearmanr(Tk[:, 0], Tk[:, 1])[0]
            say(f"    またがる本を trailing から除外 → ρ {rho:+.4f} diff {diff:+.4f} t {t:+.2f}（cycle6: ρ {rep[('week', wn)]['rho']:+.4f} t {rep[('week', wn)]['t']:+.2f}）")

# ---------- Q5 記述: TP 率 vs b ----------
say("\n## Q5 記述（判定不使用）: 月次 TP 率・平均 b・平均R の lag1 と TP 率×b の同月相関")
for wn, mk in masks.items():
    sub = tr[mk]; g = sub.groupby("month").agg(n=("R", "size"), mR=("R", "mean"), tp=("tp", "mean"), b=("b", "mean"), atr=("atr", "mean"), risk=("risk", "mean"))
    g = g[g.n >= NMIN]
    u = g.index.to_numpy()
    r_tp = lag_r_vals(u, g.tp.to_numpy())[0]; r_b = lag_r_vals(u, g.b.to_numpy())[0]; r_m = lag_r_vals(u, g.mR.to_numpy())[0]
    r_atr = lag_r_vals(u, g.atr.to_numpy())[0]
    c_tpb = pearsonr(g.tp, g.b)[0]; c_bR = pearsonr(g.b, g.mR)[0]; c_tpR = pearsonr(g.tp, g.mR)[0]
    say(f"- {wn}: lag1 r — TP率 {r_tp:+.3f} / b {r_b:+.3f} / atr {r_atr:+.3f} / 平均R {r_m:+.3f}；同月相関 — TP率×b **{c_tpb:+.3f}** / b×平均R {c_bR:+.3f} / TP率×平均R {c_tpR:+.3f}")

# ---------- 総合 ----------
say("\n## 判定（事前規則）")
A_broken = (wk_hi >= 0.05 or mo_hi >= 0.05) or len(sig_cells) > 0
A_surv = (wk_hi < 0.04 and mo_hi < 0.04 and len(sig_cells) == 0)
say(f"- (A) 副産物「σ_μ ≤0.02〜0.03R・超過分散 ≈0」: 週 上限 {wk_hi:.3f} / 月 上限 {mo_hi:.3f} / F 有意 {len(sig_cells)} → **{'broken' if A_broken else ('survived' if A_surv else 'inconclusive')}**")
say(f"- (B) 「検出できないのは方法の欠陥ではない」: σ_μ=0.05 φ=0.9 の P1∧P2 検出率 {pw:.2f} → **{'broken' if pw < 0.5 else 'survived'}**")
C_broken = p_maxt > 0.10 and rep[("month", "在2010-20")]["diff"] <= 0
C_surv = p_maxt < 0.05
say(f"- (C) 月次・外 trailing +0.05 t1.9: p_max {p_maxt:.3f}・在 diff {rep[('month','在2010-20')]['diff']:+.4f} → **{'broken' if C_broken else ('survived' if C_surv else 'inconclusive')}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
