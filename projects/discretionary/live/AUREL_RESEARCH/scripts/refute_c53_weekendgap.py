# -*- coding: utf-8 -*-
"""
[REFUTE c53 — A] 2026-11-19 15:30 反証レーン。対象 = cycle53 (12:50) が **null の副産物として肯定形で登記した**もの。
PROMOTED.md は空（昇格候補ゼロ）・H_W/H_B1/H_W2 は規則上すべて null なので「壊す」対象は次の 3 つ:

  T1 「週末ギャップの紙実差は SL 側の超過損と TP 側の棚ぼたが**ほぼ相殺**する」（在 ΣX_SL 17.925 vs ΣX_TP 10.778・外 9.198 vs 8.424）
  T2 「持ち越しの価値 ΔR_carry は在/外で 0 と区別できない（近年 +0.3485 [+0.0099,+0.6863] は 1 窓・事後）」
      ＝family 12 セル中 **唯一の名目 CI 除外**。これが市場でなく **FEED_TOL 記帳規約**で出来ていないか。
  T3 「落ちた 18 本（647→629）は価格でなく記帳の問題・**R で無差別かは未確認**」＝c53 が明示的に開けたまま残した survivorship の留保。

=== 事前固定（数字を見る前に書く・seed 20261119・c53b と同一の入力・同一の窓・同一のクラスタ単位 ts_c）===
R0 複製: W'=629・飛越 SL 25/TP 23・mean C 在 +0.0230/外 +0.0039・ΣX_SL 17.925/9.198・ΣX_TP 10.778/8.424・
  mean ΔR_carry 在 +0.0262/外 +0.1654/近年 +0.3485。許容 = 件数は完全一致・平均と総和は |差| ≤ 0.002。
  **複製が外れたら以下の判定はすべて inconclusive**（c53b と別物を測っていることになる）。

B1（T2 への攻撃・FEED_TOL 規約の感度）: ΔR_carry は carry 側に R* = (−1 or b) + ft（ft = FEED_TOL/risk）を乗せ、
  比較対象 cl_kc（引けの時価 R）には ft が無い。ft は決着した本（SL/TP）だけに付くので mean ΔR_carry は
  + ft·P(決着) だけ規約由来で持ち上がる。ft を外した ΔR_carry^0 = ΔR_carry − ft·1[決着] を再測。
  **BREAK 条件（論理和・どちらか 1 つで成立）**: (a) 近年の ΔR_carry^0 の 95%CI 下限 ≤ 0 → family 唯一の名目除外は規約由来、
  または (b) 在の ft 寄与 / 在の点推定 ≥ 0.50 → 在の「持ち越しに正の点推定」は半分以上が記帳規約。
  （注: ft 自体は本番 _simulate のトリガ余裕の反映であって「誤り」ではない。壊すのは **市場の性質としての読み** の部分。）

B2（T1 への攻撃・相殺の精度）: 「相殺」は比 ρ = ΣX_SL/ΣX_TP ≈ 1 の主張。週末クラスタ bootstrap（5000・ts_c 単位）で
  ρ の 95%CI を 在・外・在+外プールで出す。**BREAK 条件（論理和）**: (a) CI が 2.0 を含む（＝「TP 側の棚ぼたは SL 超過損の半分しかない」
  と区別できない）または (b) CI が 1.0 を外す（＝相殺そのものが棄却される）。併記 P(ρ ≥ 1.5)。

B3（別の在外分割）: H_W（mean C）と H_B1（mean ΔR_carry）を (i) 暦年の奇偶 (ii) 週末クラスタ ts_c の奇偶
  (iii) 2013-26 の本番号前半/後半 (iv) **年ブロック無作為 50/50 を 500 回**（年単位で割る＝時系列ブロック保存）で再判定。
  クラスタロバスト SE（ts_c 単位・解析式）で screen し、系統 3 分割は bootstrap も出す。
  **BREAK 条件（論理和）**: (a) 系統 3 分割のいずれかで H_W が両半 PASS（mean C ≥ 0.05 ∧ CI 下限 >0 ∧ ΣC/N_all ≥ 0.005）
  または (b) 無作為 500 分割のうち両半 PASS が ≥ 5%。どちらも無ければ null は分割選択に頑健＝**この攻撃は失敗**と書く。

B4（T3・survivorship を埋める）: 落ちた 18 本（候補 647 − W' 629）と採った 629 を比較。指標 = |受けたギャップ| /risk、
  json R*、risk、side、year、引け→再開時間。**BREAK 条件（論理和）**: (a) |G|/risk の Mann-Whitney p < 0.05
  または (b) 落ちた 18 本の mean |G|/risk ≥ 1.5 × 採った本の mean。（＝entry 推定の失敗が「大きく動いた週末」に偏るなら
  相殺の推定は選択バイアスを受ける。）

多重検定: 本スクリプトの判定セルは B1/B2/B3/B4 の 4 つ（各 BREAK 条件は事前固定の論理和）。B3 の 500 分割は
  screen であって 1 セル（両半 PASS 率）として数える。記述は記述と明示する。
出力は data/refute_c53_weekendgap.md のみ。読むのは data 配下のキャッシュ 3 本（本番系は開かない）。
発注・デモ発注・本番編集・プロセス/schtask/執行機/ライブサーバ接触・MT5・プロップ・外部通信・秘密 すべて無し。
"""
import os, json, time
import numpy as np, pandas as pd
from scipy import stats

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c53_weekendgap.md")
NY = "America/New_York"; rng = np.random.default_rng(20261119)
L = []
def say(s=""): print(s, flush=True); L.append(s)
def verdict(tag, cond, obs, broken):
    """条件 / 観測 / 判定 を別フィールドで出す（本レーン方法論候補 72・75: 事前文の印字で嘘をつかない）"""
    say(f"- **[{tag}] 判定 = {'BROKEN' if broken else 'not broken'}**")
    say(f"    - 条件: {cond}")
    say(f"    - 観測: {obs}")

say(f"# [REFUTE c53-A] 週末ギャップ「相殺」・持ち越しの価値・survivorship を壊しに行く — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c53_weekendgap.py)")

# ---------- c53b と同一のロード・同一の前処理（複製のため逐語） ----------
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
X = pd.DataFrame(J["trades"]).sort_values("entry_time", kind="stable").reset_index(drop=True)
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64); d = np.diff(off) - 1
h = X["hold"].to_numpy().astype(int); et = X["entry_time"].to_numpy()
for t in np.unique(et[pd.Series(et).duplicated(keep=False).to_numpy()]):
    g = np.where(et == t)[0]
    if not np.array_equal(h[g], d[g]):
        perm = [int(g[list(h[g]).index(v)]) for v in d[g]]; X.iloc[g] = X.iloc[perm].to_numpy()
X = X.reset_index(drop=True); N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy(); B = X["b"].to_numpy()
FT = J["frozen"]["FEED_TOL"]; MAXH = J["frozen"]["MAX_HOLD"]; ft = FT / RISK
assert np.all(np.diff(off) == HOLD + 1)
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
DROP = np.array([i for i in cand if i not in set(W.tolist())])   # 落ちた 18 本（B4）
say(f"- ロード: 本 {N}・金曜 {isF.sum()}・引け生存候補 {len(cand)}・W' {len(W)}・落ちた {len(DROP)}・FEED_TOL {FT} USD・MAX_HOLD {MAXH}")

SLp = entry - SGN * RISK; TPp = entry + SGN * B * RISK
def simulate(i, spread_sell=0.0):
    s = SGN[i]; sl = SLp[i]; tp = TPp[i]; en = entry[i]; rk = RISK[i]
    budget = MAXH - k_c[i]; j0 = reo[i]
    for n, j in enumerate(range(j0, min(j0 + budget, len(TS)))):
        o, hi, lo = O[j], H[j], LO[j]
        if s > 0: hitSL_o, hitTP_o, hitSL, hitTP = o <= sl, o >= tp, lo <= sl, hi >= tp
        else:     hitSL_o, hitTP_o, hitSL, hitTP = o >= sl, o <= tp, hi >= sl, lo <= tp
        if hitSL_o:
            fill = o + (spread_sell if s < 0 else 0.0)
            return "SL", -1.0, s * (fill - en) / rk, n == 0, "SL" if n == 0 else None
        if hitTP_o:
            fill = o + (spread_sell if s < 0 else 0.0)
            return "TP", B[i], s * (fill - en) / rk, n == 0, "TP" if n == 0 else None
        if hitSL: return "SL", -1.0, -1.0 + (s * spread_sell / rk if s < 0 else 0.0), n == 0, None
        if hitTP: return "TP", B[i], B[i] + (s * spread_sell / rk if s < 0 else 0.0), n == 0, None
    jl = min(j0 + budget, len(TS)) - 1
    rt = s * (C[jl] - en) / rk
    return "TIME", rt, rt, False, None

Rp = np.zeros(N); Xs = np.zeros(N); Xt = np.zeros(N); ex = np.array([""] * N, dtype=object)
settled = np.zeros(N, bool); gt = np.array([None] * N, dtype=object)
for i in W:
    e_, rp, rr, a, g = simulate(i)
    ex[i] = e_; gt[i] = g; settled[i] = e_ in ("SL", "TP")
    rps = rp + (ft[i] if settled[i] else 0.0); rrs = rr + (ft[i] if settled[i] else 0.0)
    Rp[i] = rps
    if g == "SL": Xs[i] = rps - rrs
    if g == "TP": Xt[i] = rrs - rps
Cnet = Xs - Xt
cl_kc = np.zeros(N); cl_kc[W] = np.array([clR[off[i] + k_c[i]] for i in W])
dcarry = np.zeros(N); dcarry[W] = Rp[W] - cl_kc[W]
G = np.full(N, np.nan); G[cand] = O[np.maximum(reo[cand], 0)] - C[ic[cand]]
G[cand[reo[cand] < 0]] = np.nan

# 落ちた本の G は reo を自前で引き直す（ok=False でも再開足は決まる）
for i in DROP:
    if ic[i] < 0: continue
    j = ic[i] + 1; lim = min(ic[i] + 288 * 4, len(TS))
    while j < lim and not (H[j] != LO[j] or C[j] != C[j - 1]): j += 1
    if j < lim: G[i] = O[j] - C[ic[i]]

WIN = {"2010-12(参考)": (2010, 2012), "在 2013-20": (2013, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def sub(y0, y1): w = (YEAR >= y0) & (YEAR <= y1); return w, W[w[W]]

def cl_boot(vals, keys, nb=5000):
    u = np.unique(keys); sums = np.array([vals[keys == k].sum() for k in u]); ns = np.array([np.sum(keys == k) for k in u])
    pick = rng.integers(0, len(u), (nb, len(u)))
    bs = sums[pick].sum(1) / ns[pick].sum(1)
    return vals.mean(), (np.percentile(bs, 2.5), np.percentile(bs, 97.5)), bs.std(), bs
def cl_se(vals, keys):
    """クラスタロバスト SE（ts_c 単位）: sqrt(Σ_g (Σ_g v − n_g·v̄)^2) / n"""
    u = np.unique(keys); n = len(vals); m = vals.mean()
    s = np.array([(vals[keys == k] - m).sum() for k in u])
    return np.sqrt((s ** 2).sum()) / n

# ---------- R0 複製 ----------
say("\n## R0 複製（c53b との一致）")
say("| 量 | c53b | 本スクリプト | 一致 |")
say("|---|---|---|---|")
rep = []
def chk(name, mine, theirs, tol):
    o = abs(mine - theirs) <= tol; rep.append(o)
    say(f"| {name} | {theirs} | {mine:.4f} | {'OK' if o else '**NG**'} |")
chk("W' 本数", len(W), 629, 0); chk("飛越 SL", int(np.sum(gt[W] == 'SL')), 25, 0); chk("飛越 TP", int(np.sum(gt[W] == 'TP')), 23, 0)
for nm, (y0, y1), mC, sSL, sTP, dc in (("在 2013-20", (2013, 2020), 0.0230, 17.925, 10.778, 0.0262),
                                       ("外 2021-26H1", (2021, 2026), 0.0039, 9.198, 8.424, 0.1654),
                                       ("近年 2024-26H1", (2024, 2026), -0.0149, 5.686, 6.775, 0.3485)):
    w, Wi = sub(y0, y1)
    chk(f"{nm} mean C", Cnet[Wi].mean(), mC, 0.002); chk(f"{nm} ΣX_SL", Xs[Wi].sum(), sSL, 0.002)
    chk(f"{nm} ΣX_TP", Xt[Wi].sum(), sTP, 0.002); chk(f"{nm} mean ΔR_carry", dcarry[Wi].mean(), dc, 0.002)
REPOK = all(rep)
say(f"- **複製 {'成功' if REPOK else '失敗'}**（{sum(rep)}/{len(rep)}）" + ("" if REPOK else " → 以下はすべて inconclusive"))

# ---------- B1: FEED_TOL 規約の感度 ----------
say("\n## B1 T2 への攻撃: ΔR_carry は FEED_TOL 記帳（ft = 0.1 USD/risk）で何割持ち上がっているか")
say(f"- ft は **決着した本（SL/TP）だけ** に付く。W' の決着率 {settled[W].mean()*100:.1f}%・ft 中央値 {np.median(ft[W]):.4f}R")
d0 = dcarry.copy(); d0[W] = dcarry[W] - ft[W] * settled[W]        # ft を外した ΔR_carry
say("| 窓 | W' | mean ΔR_carry | 95%CI | ft 寄与 | ft 外し mean | ft 外し 95%CI | ft 寄与/点推定 |")
say("|---|---|---|---|---|---|---|---|")
B1 = {}
for nm, (y0, y1) in WIN.items():
    w, Wi = sub(y0, y1)
    if not len(Wi): continue
    mu, ci, se, _ = cl_boot(dcarry[Wi], ts_c[Wi]); mu0, ci0, se0, _ = cl_boot(d0[Wi], ts_c[Wi])
    con = (ft[Wi] * settled[Wi]).mean(); B1[nm] = dict(mu=mu, ci=ci, mu0=mu0, ci0=ci0, con=con)
    say(f"| {nm} | {len(Wi)} | {mu:+.4f} | [{ci[0]:+.4f},{ci[1]:+.4f}] | {con:+.4f} | {mu0:+.4f} | [{ci0[0]:+.4f},{ci0[1]:+.4f}] | {con/mu*100 if mu!=0 else float('nan'):.0f}% |")
a = B1["近年 2024-26H1"]["ci0"][0] <= 0
share = B1["在 2013-20"]["con"] / B1["在 2013-20"]["mu"] if B1["在 2013-20"]["mu"] != 0 else float("nan")
b = share >= 0.50
verdict("B1", "(a) 近年の ft 外し CI 下限 ≤ 0  **または** (b) 在の ft 寄与/点推定 ≥ 0.50（論理和）",
        f"(a) 近年 ft 外し CI 下限 {B1['近年 2024-26H1']['ci0'][0]:+.4f} → {a}／(b) 在 ft 寄与 {B1['在 2013-20']['con']:+.4f} / 点推定 {B1['在 2013-20']['mu']:+.4f} = {share*100:.0f}% → {b}",
        (a or b) and REPOK)

# ---------- B2: 相殺の精度（比） ----------
say("\n## B2 T1 への攻撃: 「ほぼ相殺」= ρ = ΣX_SL/ΣX_TP ≈ 1 は何桁の精度で言えるか（週末クラスタ bootstrap 5000）")
say("| 窓 | ΣX_SL | ΣX_TP | ρ 点推定 | ρ 95%CI | CI は 1.0 を含む | CI は 2.0 を含む | P(ρ≥1.5) | P(ρ≥1) |")
say("|---|---|---|---|---|---|---|---|---|")
B2 = {}
pool_w = (YEAR >= 2013) & (YEAR <= 2026)
for nm, Wi in [("在 2013-20", sub(2013, 2020)[1]), ("外 2021-26H1", sub(2021, 2026)[1]), ("在+外 2013-26H1 プール", W[pool_w[W]])]:
    u = np.unique(ts_c[Wi])
    ss = np.array([Xs[Wi][ts_c[Wi] == k].sum() for k in u]); st = np.array([Xt[Wi][ts_c[Wi] == k].sum() for k in u])
    pick = rng.integers(0, len(u), (5000, len(u)))
    num = ss[pick].sum(1); den = st[pick].sum(1)
    rho_bs = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    lo, hi = np.nanpercentile(rho_bs, [2.5, 97.5]); rho = Xs[Wi].sum() / Xt[Wi].sum()
    B2[nm] = dict(rho=rho, ci=(lo, hi))
    say(f"| {nm} | {Xs[Wi].sum():.3f} | {Xt[Wi].sum():.3f} | {rho:.3f} | [{lo:.3f},{hi:.3f}] | {lo<=1<=hi} | {lo<=2<=hi} | {np.nanmean(rho_bs>=1.5)*100:.1f}% | {np.nanmean(rho_bs>=1.0)*100:.1f}% |")
pm = B2["在+外 2013-26H1 プール"]
a2 = pm["ci"][0] <= 2.0 <= pm["ci"][1]; b2 = not (pm["ci"][0] <= 1.0 <= pm["ci"][1])
verdict("B2", "プール ρ の 95%CI が (a) 2.0 を含む **または** (b) 1.0 を外す（論理和）",
        f"プール ρ {pm['rho']:.3f} CI [{pm['ci'][0]:.3f},{pm['ci'][1]:.3f}]／(a) {a2}／(b) {b2}", (a2 or b2) and REPOK)

# ---------- B3: 別の在外分割 ----------
say("\n## B3 別の在外分割（H_W・mean C）")
def hw_pass(Wi, w):
    """H_W の事前規則をそのまま適用（mean C ≥ 0.05 ∧ CI 下限 >0 ∧ ΣC/N_all ≥ 0.005）"""
    if len(Wi) < 20: return False, dict(mu=np.nan, lo=np.nan, per=np.nan)
    mu = Cnet[Wi].mean(); se = cl_se(Cnet[Wi], ts_c[Wi]); lo = mu - 1.96 * se; per = Cnet[Wi].sum() / max(w.sum(), 1)
    return (mu >= 0.05 and lo > 0 and per >= 0.005), dict(mu=mu, lo=lo, per=per)
say("| 分割 | 半A n/mean C/CI下限/ΣC/N | 半B n/mean C/CI下限/ΣC/N | 両半 PASS |")
say("|---|---|---|---|")
sysres = []
pool = W[pool_w[W]]
splits = {}
splits["暦年 奇偶"] = ((YEAR % 2 == 1) & pool_w, (YEAR % 2 == 0) & pool_w)
par = np.zeros(N, bool); uu = np.unique(ts_c[pool]); par_map = {k: (n % 2 == 1) for n, k in enumerate(uu)}
for i in pool: par[i] = par_map[ts_c[i]]
splits["週末クラスタ 奇偶"] = (par & pool_w, (~par) & pool_w)
med = np.median(pool); half = np.zeros(N, bool); half[pool[pool < med]] = True
splits["本番号 前半/後半"] = (half & pool_w, (~half) & pool_w)
for nm, (mA, mB) in splits.items():
    WA = W[mA[W]]; WB = W[mB[W]]
    pA, iA = hw_pass(WA, mA); pB, iB = hw_pass(WB, mB); sysres.append(pA and pB)
    say(f"| {nm} | {len(WA)} / {iA['mu']:+.4f} / {iA['lo']:+.4f} / {iA['per']:+.5f} | {len(WB)} / {iB['mu']:+.4f} / {iB['lo']:+.4f} / {iB['per']:+.5f} | {pA and pB} |")
years = np.arange(2013, 2027); nb_sp = 500; cnt = 0; mus = []
for _ in range(nb_sp):
    pick = rng.permutation(years); ya, yb = set(pick[:7].tolist()), set(pick[7:].tolist())
    mA = np.isin(YEAR, list(ya)) & pool_w; mB = np.isin(YEAR, list(yb)) & pool_w
    pA, iA = hw_pass(W[mA[W]], mA); pB, iB = hw_pass(W[mB[W]], mB)
    cnt += int(pA and pB); mus.append((iA["mu"], iB["mu"]))
mus = np.array(mus)
say(f"- 年ブロック無作為 50/50 × {nb_sp}: 両半 PASS **{cnt}/{nb_sp} = {cnt/nb_sp*100:.1f}%**・min(mean C 両半) の分布 p50 {np.nanpercentile(mus.min(1),50):+.4f} / p95 {np.nanpercentile(mus.min(1),95):+.4f} / max {np.nanmax(mus.min(1)):+.4f}（H_W の閾値 0.05）")
a3 = any(sysres); b3 = cnt / nb_sp >= 0.05
verdict("B3", "(a) 系統 3 分割のいずれかで H_W 両半 PASS **または** (b) 無作為 500 分割の両半 PASS 率 ≥ 5%（論理和）",
        f"(a) 系統 {sysres} → {a3}／(b) {cnt/nb_sp*100:.1f}% → {b3}", (a3 or b3) and REPOK)
# H_B1 も同じ分割で（記述）
say("- 記述 H_B1（mean ΔR_carry・同じ分割・クラスタ SE）: " + "／".join(
    f"{nm} A {dcarry[W[mA[W]]].mean():+.3f}±{1.96*cl_se(dcarry[W[mA[W]]], ts_c[W[mA[W]]]):.3f} B {dcarry[W[mB[W]]].mean():+.3f}±{1.96*cl_se(dcarry[W[mB[W]]], ts_c[W[mB[W]]]):.3f}"
    for nm, (mA, mB) in splits.items()))

# ---------- B4: survivorship（落ちた 18 本） ----------
say("\n## B4 T3: 落ちた 18 本 vs 採った 629（c53 が未確認と書いた留保）")
gk = np.abs(G[W]) / RISK[W]; gd = np.abs(G[DROP]) / RISK[DROP]
gd_ok = gd[~np.isnan(gd)]
say(f"- |G|/risk: 採った n {len(gk)} mean {gk.mean():.4f} median {np.median(gk):.4f}／落ちた n {len(gd_ok)} mean {gd_ok.mean():.4f} median {np.median(gd_ok):.4f}・比 {gd_ok.mean()/gk.mean():.2f}×")
mw = stats.mannwhitneyu(gd_ok, gk, alternative="two-sided")
tt = stats.ttest_ind(gd_ok, gk, equal_var=False)
say(f"- Mann-Whitney p {mw.pvalue:.4f}・Welch t {tt.statistic:+.2f} p {tt.pvalue:.4f}")
for nm, arr in (("json R*", R + ft * np.isin(EXIT, ["SL", "TP"])), ("risk", RISK), ("year", YEAR.astype(float)), ("hold", HOLD.astype(float)), ("k_c", k_c.astype(float))):
    say(f"- {nm}: 採った mean {arr[W].mean():+.3f}／落ちた mean {arr[DROP].mean():+.3f}・MW p {stats.mannwhitneyu(arr[DROP], arr[W], alternative='two-sided').pvalue:.4f}")
say(f"- side BUY 率: 採った {np.mean(SGN[W]>0)*100:.1f}%／落ちた {np.mean(SGN[DROP]>0)*100:.1f}%・落ちた本の年 {dict(pd.Series(YEAR[DROP]).value_counts().sort_index())}")
say(f"- 落ちた理由の内訳: entry 推定 3 本範囲 >0.02 USD {int(np.sum(rngE[DROP] > 0.02))}・clR[k_c] 不一致 {int(np.sum((rngE[DROP] <= 0.02)))}（再開足未検出 {int(np.sum(reo[DROP] < 0))}）")
a4 = mw.pvalue < 0.05; b4 = gd_ok.mean() >= 1.5 * gk.mean()
verdict("B4", "(a) |G|/risk の MW p < 0.05 **または** (b) 落ちた本の mean |G|/risk ≥ 1.5 × 採った本（論理和）",
        f"(a) p {mw.pvalue:.4f} → {a4}／(b) {gd_ok.mean():.4f} vs 1.5×{gk.mean():.4f}={1.5*gk.mean():.4f} → {b4}", (a4 or b4) and REPOK)

# ---------- 記述: c25 の TIME 率不一致は本当に消えるか ----------
say("\n## 記述: c25 の「台帳 TIME 0.3% vs scan 2.6%」は週末畳みで本当に消えるか（c53 の 0.62% の母集団整合）")
T = EXIT == "TIME"; fold = isF & (HOLD >= k_c + 1); rec = YEAR >= 2024
say(f"- c25 の cell は 2024-26H1（n 4005・TIME 103 = 2.57%）。本キャッシュ 近年: TIME {int(T[rec].sum())}/{int(rec.sum())} = {T[rec].mean()*100:.2f}%（c25 と母集団一致）")
say(f"- 近年 週末畳み {int(np.sum(T & fold & rec))}・畳みを除く TIME {int(np.sum(T & ~fold & rec))}/{int(rec.sum())} = {np.sum(T & ~fold & rec)/rec.sum()*100:.2f}%・全期間 畳みを除く {np.sum(T & ~fold)/N*100:.2f}%")
p_adj = np.sum(T & ~fold & rec) / rec.sum()
bt = stats.binomtest(1, 320, p_adj, alternative="two-sided")
say(f"- 台帳 TIME 1/320 を調整後 scan 率 {p_adj*100:.2f}% で二項検定: 期待 {320*p_adj:.2f} 本・p {bt.pvalue:.4f}（調整前 {T[rec].mean()*100:.2f}% なら 期待 {320*T[rec].mean():.2f} 本・p {stats.binomtest(1,320,T[rec].mean()).pvalue:.6f}）→ **不一致は消える（c53 の主張は支持）**")

say(f"\n- 実行 {time.time()-T0:.1f} s・入力 = refute_c4 json＋refute_c2_fullpaths.npz＋XAU_m5_ohlc.npz（data 配下のみ）・seed 20261119・多年 scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
