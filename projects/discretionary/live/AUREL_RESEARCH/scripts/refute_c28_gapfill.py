# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-10 08:15 反証レーン] 対象: cycle28 (06:55) 「ギャップは埋まるか」の残存弱信号。
主セル WKND/DAILY N=72 null は争わない（R0 で再現 assert）。壊しに行くのは null の周りに残った:
  W1 「遅い埋まり（6〜23 h）2〜4 pp は否定できていない」: DAILY 外 N=276 D̄ +0.070 (t 1.95)・近年 +0.119 (t 2.37)・
      触れた率差 +2.2 pp (t 1.83)／+4.0 (t 2.03)・fade 粗損益 外 +1.64 bp (t 2.04) vs 往復 1.58 bp。
  W2 「上下非対称（平日: 上は続き下は埋まる・3 窓・18:10 アンカーでも残る）は再開後の背景ドリフトの別名」＝研究レーンの読み。
      bid 正常化（18:00 の bid 沈み→戻り）も同じ向き（下は埋まり上は続く）を作るので、ドリフトと人工物とギャップ情報の 3 つを分ける。
  W3 知識 (2)「再開後の価格はギャップを覚えていない（マルコフ）」＝符号情報ゼロの主張。
  W4 「先着検定は最初の 1 時間の反転にしか感度が無い（陽性対照 50% 注入で t 1.87）」＝検出力の主張。

事前固定の規則（結果を見る前に書く）:
  帰無 = **符号置換**: 各イベントの |G| とアンカーを固定し G の符号だけを独立に ±1 で振る（2000 回・seed 20261110）。
        「再開後の価格はギャップの向きを知らない」の正確な帰無で、ドリフト・ボラ・bid 正常化はすべて帰無に含まれる
        （向きと無関係な成分は符号を振っても残るため）。統計量ごとに観測値の片側 p と、セル族の max|t| の family-wise p。
  アンカー = 18:00 足終値（c28）と +2/+4/+6/+12 本（18:10/18:20/18:30/19:00 終値）。|G| は各アンカーで再計算・|G|≥2 bp。
  窓 = 在 2013-20（DAILY は 2013+）／外 2021-26H1／近年 2024-26H1／外-ex2026（2021-25）／年別。
  統計量 = D̄（先着）・touch 差（FILL 水準に触れた率 − CONT 水準に触れた率）・fade 粗損益 bp（c28 と同定義）・
           β = OLS slope of r_N(bp) on −G(bp)（1 = 完全埋め・0 = 無記憶）。
  R1 (W1): DAILY 外・N=276。
     survived = 18:10 アンカーで D̄ t ≥ 2.0 ∧ 符号置換 family-wise p（N∈{12,72,276}×アンカー∈{0,+2} の 6 セル・D̄）< 0.05
                ∧ 2021-25（2026H1 除く）D̄ t ≥ 1.5 ∧ fade net（往復 1.58 bp ×2）> 0。
     broken    = 18:10 アンカーで D̄ t < 1.5 ∨ family-wise p ≥ 0.10 ∨ 2021-25 D̄ t < 1.0。
     それ以外 inconclusive。
  R2 (W2/W3): ギャップの向きが再開後の動きを条件づけるか（ドリフトを除いた形）。
     符号に依存しない結果 D_up（+1 = 下バリア先着・−1 = 上バリア先着）を、実際の上ギャップ日と下ギャップ日で比べる:
     Δ = mean(D_up | 上) − mean(D_up | 下)。純粋なドリフト（＋bid 正常化）は両群を同じだけ動かすので Δ=0。
     Δ>0 = 上ギャップ後は下へ（反転情報）・Δ<0 = 継続情報。Welch t と群ラベル置換（群サイズ保存・2000 回・両側 p）。
     DAILY・N=72・アンカー 0/2/4/6/12。
     「ギャップ情報あり（W3 broken）」= アンカー +2 で 在 p < 0.05 ∧ 外 p < 0.05 ∧ 同符号。
     「ドリフトの別名（研究レーンの読み survived）」= 在・外とも p ≥ 0.10。それ以外 inconclusive。
     v1 の統計量 A = D̄(下) − D̄(上) は符号置換の下で −2·mean(D_up) に退化し（群サイズが等しいと分散 ≈0）、p 0.000 は人工物
     → v1 出力は data/refute_c28_gapfill_v1.md に保存し、本版で差し替え（自己訂正）。
  R2b (W3・ドリフト除去の条件付き期待値): Δ_r = mean(r_N | 上) − mean(r_N | 下)（bp・N=72／276・反転なら <0）、
     Δ_dir = P(r_N>0 | 上) − P(r_N>0 | 下)。Welch t。注入 f=0.25／0.50 で t がどこまで動くか（検出力）。
  R3 (事後グリッドの多重検定): c28 の事後族（2 クラス × 3 N × 3 窓 × 5 部分集合 = 90 セル・アンカー 0）の max|t| 3.53（DAILY 在 下）
     の符号置換 family-wise p。置換の下では上/下の部分集合も割り当て直す。
  R4 (W4 検出力): DAILY 外 18:10 アンカー N=276 に「N 本で |G| の f=25／50% を参照側へ戻す」決定論的ドリフトを
     線形（c28 と同じ）と前倒し（1−e^{−3j/N} 形・6 h で 7 割）の 2 形で注入し、D̄・touch 差・β それぞれの t を印字。
     β の MDE（2se）を「埋まる割合」の単位で併記 → 「2〜4 pp は否定できていない」の pp を f に換算する。
  R5 (費用倍): fade 粗損益（18:10・N=276・外・近年）を往復 1.58／0.96 bp の ×1／×2 で net。
  look-ahead: 全統計はアンカー足の後の足だけで計算。|G|≥2・クリーン条件はアンカー以前で定義。
  D2: 窓別・16 年一括は使わず。scan 無し・M5 読込無し・MT5 無し・外部通信無し。書き込みは AUREL_RESEARCH/data のみ。
"""
import os, sys, time, math, io
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
MAC = os.path.join(ROOT, "data", "macro"); OUT = os.path.join(ROOT, "data", "refute_c28_gapfill.md")
rng = np.random.default_rng(20261110)
NPERM = 2000
T0 = time.time(); buf = io.StringIO()
def say(s=""):
    print(s, flush=True); buf.write(s + "\n")

W = {"在 2013-20": (2013, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026), "外-ex2026 2021-25": (2021, 2025)}
NS = [12, 72, 276]
G_MIN = 2.0

z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64); hi = z["high"]; lo = z["low"]; cl = z["close"]
lc = np.log(cl); lh_all = np.log(hi); ll_all = np.log(lo)
r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = r == 0
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert("America/New_York")
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
say(f"# refute_c28 ギャップ先着の残存弱信号（符号置換・アンカー掃引・検出力）— 実行 {pd.Timestamp.now():%Y-%m-%d %H:%M}")
say(f"- npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]}・flat {flat.mean()*100:.1f}%・seed 20261110・置換 {NPERM}")

def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)
NMAX = max(NS) + 12
def window_ok(a):
    a = np.asarray(a); e = a + NMAX
    return (e < len(ts)) & (ts[np.clip(e, 0, len(ts) - 1)] == ts[a] + 300 * NMAX)

def build(anchor0, ref0, shift):
    a = anchor0; ref = ref0
    ok = (ref >= 0) & (a > 0) & window_ok(a)
    brk = np.column_stack([idx_at(ts[a] - 300 * j) for j in range(1, 13)]); ok &= np.all(brk >= 0, axis=1)
    clean = np.zeros(len(a), bool); clean[ok] = np.all(flat[brk[ok]], axis=1)
    k = ok & clean; a = a[k] + shift; ref = ref[k]
    G = (lc[a] - lc[ref]) * 1e4; big = np.abs(G) >= G_MIN
    return a[big], G[big]

# events (same definitions as c28)
iS = np.where((wd == 6) & (h == 18) & (mi == 0))[0]
iF = np.where((wd == 4) & (h == 16) & (mi == 50))[0]; pF = np.searchsorted(iF, iS) - 1
refS = np.where(pF >= 0, iF[np.clip(pF, 0, len(iF) - 1)], -1)
refS = np.where((refS >= 0) & (ts[iS] - ts[np.clip(refS, 0, len(ts) - 1)] <= 3 * 86400), refS, -1)
iD = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]; refD = idx_at(ts[iD] - 70 * 60)

class Ev:
    """per-event precomputation independent of sign: first-hit index of lower (kL) / upper (kU) barrier at distance |G|,
    terminal log-return, so that sign permutations are O(n) each."""
    def __init__(self, a, G, N):
        self.a, self.G, self.N = a, G, N
        self.ag = np.abs(G) / 1e4; self.s = np.sign(G); self.yr = yr[a]; self.n = len(a)
        J = a[:, None] + np.arange(1, N + 1)[None, :]
        dh = lh_all[J] - lc[a][:, None]; dl = ll_all[J] - lc[a][:, None]
        up = dh >= self.ag[:, None]; dn = dl <= -self.ag[:, None]
        self.kU = np.where(up.any(1), up.argmax(1), N + 1); self.kL = np.where(dn.any(1), dn.argmax(1), N + 1)
        self.rN = (lc[J[:, -1]] - lc[a]) * 1e4  # bp
        self.price = cl[a]
    def stats(self, s, m):
        """s: sign vector (+1 up gap). returns D̄, touch-diff, fade pnl mean, beta, and t's for mask m"""
        kF = np.where(s > 0, self.kL, self.kU); kC = np.where(s > 0, self.kU, self.kL)
        D = np.zeros(self.n); D[kF < kC] = 1; D[kC < kF] = -1
        touch = (kF <= self.N).astype(float) - (kC <= self.N)
        pnl = np.where(D != 0, D * self.ag * 1e4, -s * self.rN)
        x = -s * self.ag * 1e4; y = self.rN
        out = {}
        for nm, v in [("D", D), ("touch", touch), ("pnl", pnl)]:
            vv = v[m]; n = len(vv); mu = vv.mean(); se = vv.std(ddof=1) / math.sqrt(n) if n > 1 else np.nan
            out[nm] = (mu, se, mu / se if se else np.nan)
        xm = x[m]; ym = y[m]; xc = xm - xm.mean(); yc = ym - ym.mean()
        sxx = (xc ** 2).sum()
        if sxx > 0 and len(xm) > 3:
            b = (xc * yc).sum() / sxx; e = yc - b * xc
            se_b = math.sqrt(((xc ** 2) * (e ** 2)).sum()) / sxx  # HC0
            out["beta"] = (b, se_b, b / se_b)
        else:
            out["beta"] = (np.nan, np.nan, np.nan)
        return out, D

def wmask(ev, wn):
    y0, y1 = W[wn]; return (ev.yr >= y0) & (ev.yr <= y1)

# ---------------- R0 reproduce ----------------
say("\n## R0 再現（c28 主結果・アンカー 0）")
rep = {}
for lab, (i0, r0) in [("WKND", (iS, refS)), ("DAILY", (iD, refD))]:
    a, G = build(i0, r0, 0)
    for N in NS:
        ev = Ev(a, G, N); rep[(lab, N)] = ev
        parts = []
        for wn in ["在 2013-20", "外 2021-26H1", "近年 2024-26H1"]:
            m = wmask(ev, wn) if lab == "DAILY" else ((ev.yr >= (2010 if wn.startswith("在") else W[wn][0])) & (ev.yr <= W[wn][1]))
            o, _ = ev.stats(ev.s, m)
            parts.append(f"{wn} n{m.sum()} D̄ {o['D'][0]:+.3f} (t {o['D'][2]:+.2f})・touch {o['touch'][0]*100:+.1f} pp (t {o['touch'][2]:+.2f})・pnl {o['pnl'][0]:+.2f} bp (t {o['pnl'][2]:+.2f})・β {o['beta'][0]:+.3f} (t {o['beta'][2]:+.2f})")
        say(f"- {lab} N={N}: " + "／".join(parts))
evD72 = rep[("DAILY", 72)]; evD276 = rep[("DAILY", 276)]; evW72 = rep[("WKND", 72)]
oW, _ = evW72.stats(evW72.s, (evW72.yr >= 2010) & (evW72.yr <= 2020)); oW2, _ = evW72.stats(evW72.s, evW72.yr >= 2021)
oD, _ = evD72.stats(evD72.s, wmask(evD72, "在 2013-20")); oD2, _ = evD72.stats(evD72.s, wmask(evD72, "外 2021-26H1"))
o276, _ = evD276.stats(evD276.s, wmask(evD276, "外 2021-26H1"))
assert abs(oW['D'][0] - 0.000) < 0.003 and abs(oW2['D'][0] - 0.025) < 0.003, (oW['D'], oW2['D'])
assert abs(oD['D'][0] - 0.013) < 0.003 and abs(oD2['D'][0] - 0.066) < 0.003, (oD['D'], oD2['D'])
assert abs(o276['D'][0] - 0.070) < 0.003 and abs(o276['touch'][0] - 0.022) < 0.004 and abs(o276['pnl'][0] - 1.64) < 0.05
say("- assert: WKND 在 +0.000／外 +0.025・DAILY 在 +0.013／外 +0.066・DAILY N=276 外 D̄ +0.070／touch +2.2 pp／pnl +1.64 → **一致**")

# ---------------- anchor sweep (DAILY) ----------------
say("\n## アンカー掃引（DAILY・|G| は各アンカーで再計算・|G|≥2 bp）: D̄／touch 差／fade pnl／β")
SHIFTS = [0, 2, 4, 6, 12]
EV = {}
for sh in SHIFTS:
    a, G = build(iD, refD, sh)
    for N in NS:
        EV[(sh, N)] = Ev(a, G, N)
for N in NS:
    say(f"- N={N}")
    for sh in SHIFTS:
        ev = EV[(sh, N)]; parts = []
        for wn in W:
            m = wmask(ev, wn); o, _ = ev.stats(ev.s, m)
            parts.append(f"{wn.split()[0]} n{m.sum()} D̄ {o['D'][0]:+.3f} (t {o['D'][2]:+.2f}) touch {o['touch'][0]*100:+.1f}pp (t {o['touch'][2]:+.2f}) pnl {o['pnl'][0]:+.2f} (t {o['pnl'][2]:+.2f}) β {o['beta'][0]:+.3f} (t {o['beta'][2]:+.2f})")
        say(f"  - アンカー +{sh} 本（{18 + (sh*5)//60:02d}:{(sh*5)%60:02d} 終値）: " + "／".join(parts))

# ---------------- sign permutation null ----------------
def perm_stats(ev, m, nperm=NPERM):
    """returns dict stat -> array of permuted t (nperm) and observed t"""
    obs, _ = ev.stats(ev.s, m)
    S = rng.choice([-1.0, 1.0], size=(nperm, ev.n))
    res = {k: np.empty(nperm) for k in ["D", "touch", "pnl", "beta"]}
    vals = {k: np.empty(nperm) for k in ["D", "touch", "pnl", "beta"]}
    for p in range(nperm):
        o, _ = ev.stats(S[p], m)
        for k in res: res[k][p] = o[k][2]; vals[k][p] = o[k][0]
    return obs, res, vals

say("\n## R1 (W1) 符号置換の帰無・DAILY 外 2021-26H1（|G|・アンカー固定・符号 ±1 を独立に振る）")
cells = [(sh, N) for sh in [0, 2] for N in NS]
obsT = {}; permT = {}
for (sh, N) in cells:
    ev = EV[(sh, N)]; m = wmask(ev, "外 2021-26H1")
    obs, res, vals = perm_stats(ev, m)
    obsT[(sh, N)] = obs; permT[(sh, N)] = res
    parts = []
    for k in ["D", "touch", "pnl", "beta"]:
        p1 = (res[k] >= obs[k][2]).mean()  # one-sided (fill direction positive)
        parts.append(f"{k} {obs[k][0]:+.3f} t {obs[k][2]:+.2f} 置換 sd(t) {res[k].std():.2f} 片側 p {p1:.3f}")
    say(f"- アンカー +{sh}・N={N}: " + "／".join(parts))
say("- family-wise（6 セル = N×アンカー・外）: 観測 max t vs 置換 max t の分布")
fw = {}
for k in ["D", "touch", "pnl", "beta"]:
    omax = max(obsT[c][k][2] for c in cells)
    pm = np.max(np.column_stack([permT[c][k] for c in cells]), axis=1)
    fw[k] = (pm >= omax).mean()
    say(f"  - {k}: 観測 max t {omax:+.2f}（帰無 95% 点 {np.percentile(pm,95):.2f}・中央値 {np.median(pm):.2f}）→ **p_fw {fw[k]:.3f}**")
omax_all = max(obsT[c][k][2] for c in cells for k in ["D", "touch", "pnl", "beta"])
pm_all = np.max(np.column_stack([permT[c][k] for c in cells for k in ["D", "touch", "pnl", "beta"]]), axis=1)
say(f"  - 4 統計量 × 6 セル = 24: 観測 max t {omax_all:+.2f}（帰無 95% 点 {np.percentile(pm_all,95):.2f}）→ p_fw {(pm_all>=omax_all).mean():.3f}")

# yearly / LOYO at anchor +2, N=276
ev = EV[(2, 276)]
say("- 年別・LOYO（DAILY・アンカー +2・N=276・D̄）:")
ys = []
for y in range(2013, 2027):
    m = ev.yr == y
    if m.sum() >= 10:
        o, _ = ev.stats(ev.s, m); ys.append(f"{y}:{o['D'][0]:+.3f} (t {o['D'][2]:+.1f}, n{m.sum()})")
say("  - 年別: " + " ".join(ys))
mo = wmask(ev, "外 2021-26H1"); loyo = []
for y in range(2021, 2027):
    m = mo & (ev.yr != y); o, _ = ev.stats(ev.s, m); loyo.append(f"−{y}: {o['D'][0]:+.3f} (t {o['D'][2]:+.2f})")
say("  - LOYO 外: " + "／".join(loyo))
for wn in ["外-ex2026 2021-25", "近年 2024-26H1"]:
    m = wmask(ev, wn); o, _ = ev.stats(ev.s, m)
    say(f"  - {wn}: D̄ {o['D'][0]:+.3f} (t {o['D'][2]:+.2f})・touch {o['touch'][0]*100:+.1f} pp (t {o['touch'][2]:+.2f})・pnl {o['pnl'][0]:+.2f} (t {o['pnl'][2]:+.2f})・β {o['beta'][0]:+.3f} (t {o['beta'][2]:+.2f})")
# 2026H1 alone
m = ev.yr == 2026; o, _ = ev.stats(ev.s, m)
say(f"  - 2026H1 単独: n{m.sum()} D̄ {o['D'][0]:+.3f} (t {o['D'][2]:+.2f})・pnl {o['pnl'][0]:+.2f} (t {o['pnl'][2]:+.2f})")

# small/large |G| at anchor +2 N=276 (the c28 '小|G|' residual)
med = np.median(ev.ag[wmask(ev, "在 2013-20")]) * 1e4
for wn in ["外 2021-26H1", "近年 2024-26H1"]:
    m = wmask(ev, wn); parts = []
    for nm, sel in [("小|G|", ev.ag * 1e4 < med), ("大|G|", ev.ag * 1e4 >= med)]:
        o, _ = ev.stats(ev.s, m & sel); parts.append(f"{nm} D̄ {o['D'][0]:+.3f} (t {o['D'][2]:+.2f}, n{(m&sel).sum()})")
    say(f"  - {wn} 大小（在中央値 {med:.1f} bp）: " + "／".join(parts))

# R1 verdict
o2, _ = EV[(2, 276)].stats(EV[(2, 276)].s, wmask(EV[(2, 276)], "外 2021-26H1"))
oex, _ = EV[(2, 276)].stats(EV[(2, 276)].s, wmask(EV[(2, 276)], "外-ex2026 2021-25"))
cost = 1.58
net2 = o2["pnl"][0] - 2 * cost
if o2["D"][2] >= 2.0 and fw["D"] < 0.05 and oex["D"][2] >= 1.5 and net2 > 0: v1 = "survived"
elif o2["D"][2] < 1.5 or fw["D"] >= 0.10 or oex["D"][2] < 1.0: v1 = "broken"
else: v1 = "inconclusive"
say(f"- **R1 判定 W1: {v1}**（18:10 D̄ t {o2['D'][2]:+.2f}・p_fw(D) {fw['D']:.3f}・2021-25 D̄ t {oex['D'][2]:+.2f}・fade net ×2 {net2:+.2f} bp）")

# ---------------- R2 asymmetry ----------------
say("\n## R2 (W2/W3) 上下非対称 A = D̄(下) − D̄(上)・DAILY N=72・符号置換の帰無（= ドリフト＋bid 正常化が作る非対称）")
def asym(ev, s, m):
    _, D = ev.stats(s, m)
    up = m & (s > 0); dn = m & (s < 0)
    return D[dn].mean() - D[up].mean(), D[up].mean(), D[dn].mean()
A_obs = {}
for sh in SHIFTS:
    ev = EV[(sh, 72)]; parts = []
    for wn in ["在 2013-20", "外 2021-26H1", "近年 2024-26H1"]:
        m = wmask(ev, wn)
        A, du, dd = asym(ev, ev.s, m)
        S = rng.choice([-1.0, 1.0], size=(NPERM, ev.n))
        Ap = np.array([asym(ev, S[p], m)[0] for p in range(NPERM)])
        p1 = (Ap >= A).mean()
        A_obs[(sh, wn)] = (A, Ap.mean(), Ap.std(), p1)
        parts.append(f"{wn.split()[0]} 上 {du:+.3f}／下 {dd:+.3f}・A {A:+.3f} vs 帰無 {Ap.mean():+.3f}±{Ap.std():.3f}・片側 p **{p1:.3f}**")
    say(f"- アンカー +{sh}: " + "／".join(parts))
pi = A_obs[(2, "在 2013-20")][3]; po = A_obs[(2, "外 2021-26H1")][3]
if pi < 0.05 and po < 0.05: v2 = "ギャップ情報あり（W3 broken・研究レーンの『ドリフトの別名』は不十分）"
elif pi >= 0.10 and po >= 0.10: v2 = "ドリフトの別名（研究レーンの読み survived・W3 survived）"
else: v2 = "inconclusive"
say(f"- **R2 判定: {v2}**（アンカー +2 片側 p 在 {pi:.3f}／外 {po:.3f}）")
# decomposition: how much of A at anchor 0 is removed by anchor +2 (bid normalisation)
for wn in ["在 2013-20", "外 2021-26H1"]:
    a0 = A_obs[(0, wn)]; a2 = A_obs[(2, wn)]
    say(f"  - {wn}: A(18:00) {a0[0]:+.3f}（帰無 {a0[1]:+.3f}）→ A(18:10) {a2[0]:+.3f}（帰無 {a2[1]:+.3f}）＝ 帰無を超える分 {a0[0]-a0[1]:+.3f} → {a2[0]-a2[1]:+.3f}")
# the unconditional drift after reopen (bp over 72 bars) for context
for sh in [0, 2]:
    ev = EV[(sh, 72)]; parts = []
    for wn in ["在 2013-20", "外 2021-26H1", "近年 2024-26H1"]:
        m = wmask(ev, wn); mu = ev.rN[m].mean(); se = ev.rN[m].std(ddof=1) / math.sqrt(m.sum())
        parts.append(f"{wn.split()[0]} {mu:+.2f} bp (t {mu/se:+.2f})")
    say(f"  - 再開後 6 h の無条件ドリフト（アンカー +{sh}）: " + "／".join(parts))

# ---------------- R3 post-hoc grid family-wise ----------------
say("\n## R3 事後グリッド（c28 の副: 2 クラス × 3 N × 3 窓 × 5 部分集合 = 90 セル・アンカー 0）の符号置換 family-wise")
def grid_max_t(sign_W, sign_D):
    mx = 0.0; arg = None
    for lab, ev_by_N, s in [("WKND", {N: rep[("WKND", N)] for N in NS}, sign_W), ("DAILY", {N: rep[("DAILY", N)] for N in NS}, sign_D)]:
        for N in NS:
            ev = ev_by_N[N]
            medg = np.median(ev.ag[(ev.yr <= 2020)]) * 1e4
            for wn, (y0, y1) in [("在", (2010 if lab == "WKND" else 2013, 2020)), ("外", (2021, 2026)), ("近年", (2024, 2026))]:
                m = (ev.yr >= y0) & (ev.yr <= y1)
                _, D = ev.stats(s, m)
                for nm, sel in [("全", np.ones(ev.n, bool)), ("小", ev.ag * 1e4 < medg), ("大", ev.ag * 1e4 >= medg), ("上", s > 0), ("下", s < 0)]:
                    mm = m & sel
                    if mm.sum() < 10: continue
                    v = D[mm]; t = v.mean() / (v.std(ddof=1) / math.sqrt(len(v)))
                    if abs(t) > mx: mx = abs(t); arg = (lab, N, wn, nm, v.mean(), t, len(v))
    return mx, arg
obs_mx, obs_arg = grid_max_t(rep[("WKND", 72)].s, rep[("DAILY", 72)].s)
say(f"- 観測 max|t| {obs_mx:.2f} @ {obs_arg}")
NP3 = 400
pm3 = np.empty(NP3)
for p in range(NP3):
    sW = rng.choice([-1.0, 1.0], size=rep[("WKND", 72)].n); sD = rng.choice([-1.0, 1.0], size=rep[("DAILY", 72)].n)
    pm3[p], _ = grid_max_t(sW, sD)
say(f"- 符号置換 {NP3} 回の max|t|: 中央値 {np.median(pm3):.2f}・95% 点 {np.percentile(pm3,95):.2f} → **p_fw {(pm3>=obs_mx).mean():.3f}**（上/下セルは帰無でもドリフトで |t| が立つため、この p は『ドリフト以上の符号情報』の検定）")

# ---------------- R4 power ----------------
say("\n## R4 (W4) 検出力: DAILY 外・アンカー +2・N=276 に埋まり f を注入（線形 vs 前倒し 1−e^{−3j/N}）")
ev = EV[(2, 276)]; m = wmask(ev, "外 2021-26H1"); N = 276
a = ev.a; J = a[:, None] + np.arange(1, N + 1)[None, :]
dh0 = lh_all[J] - lc[a][:, None]; dl0 = ll_all[J] - lc[a][:, None]; rN0 = lc[J[:, -1]] - lc[a]
jj = np.arange(1, N + 1)[None, :] / N
for shape, w in [("線形", jj), ("前倒し", (1 - np.exp(-3 * jj)) / (1 - math.exp(-3)))]:
    for f in [0.10, 0.25, 0.50]:
        d = -ev.s[:, None] * f * ev.ag[:, None] * w
        dh = dh0 + d; dl = dl0 + d; rN = (rN0 + d[:, -1]) * 1e4
        up = dh >= ev.ag[:, None]; dn = dl <= -ev.ag[:, None]
        kU = np.where(up.any(1), up.argmax(1), N + 1); kL = np.where(dn.any(1), dn.argmax(1), N + 1)
        kF = np.where(ev.s > 0, kL, kU); kC = np.where(ev.s > 0, kU, kL)
        D = np.zeros(ev.n); D[kF < kC] = 1; D[kC < kF] = -1
        touch = (kF <= N).astype(float) - (kC <= N)
        x = -ev.s * ev.ag * 1e4
        def tt(v):
            vv = v[m]; return vv.mean(), vv.mean() / (vv.std(ddof=1) / math.sqrt(len(vv)))
        xm = x[m]; ym = rN[m]; xc = xm - xm.mean(); yc = ym - ym.mean(); b = (xc * yc).sum() / (xc ** 2).sum()
        e = yc - b * xc; se_b = math.sqrt(((xc ** 2) * (e ** 2)).sum()) / (xc ** 2).sum()
        dm, dt = tt(D); tm, tt_ = tt(touch)
        say(f"- {shape} f={f:.2f}: D̄ {dm:+.3f} (t {dt:+.2f})・touch {tm*100:+.1f} pp (t {tt_:+.2f})・β {b:+.3f} (t {b/se_b:+.2f})")
o0, _ = ev.stats(ev.s, m)
say(f"- 観測（注入なし）: D̄ {o0['D'][0]:+.3f} (t {o0['D'][2]:+.2f})・touch {o0['touch'][0]*100:+.1f} pp (t {o0['touch'][2]:+.2f})・β {o0['beta'][0]:+.3f} (se {o0['beta'][1]:.3f}・t {o0['beta'][2]:+.2f})"
    f" → β の MDE(2se) = 埋まり {2*o0['beta'][1]*100:.0f}%・観測 β の 95% CI [{o0['beta'][0]-1.96*o0['beta'][1]:+.3f}, {o0['beta'][0]+1.96*o0['beta'][1]:+.3f}]")
# beta in-sample / recent for completeness
for wn in ["在 2013-20", "近年 2024-26H1", "外-ex2026 2021-25"]:
    mm = wmask(ev, wn); o, _ = ev.stats(ev.s, mm)
    say(f"  - β {wn}: {o['beta'][0]:+.3f} (se {o['beta'][1]:.3f}・t {o['beta'][2]:+.2f})")

# ---------------- R5 cost ----------------
say("\n## R5 費用倍（fade 粗損益・アンカー +2・N=276）")
for wn, c in [("外 2021-26H1", 1.58), ("近年 2024-26H1", 0.96), ("外-ex2026 2021-25", 1.75)]:
    mm = wmask(ev, wn); o, _ = ev.stats(ev.s, mm)
    say(f"- {wn}: 粗 {o['pnl'][0]:+.2f} bp (t {o['pnl'][2]:+.2f})・net ×1 {o['pnl'][0]-c:+.2f}・net ×2 {o['pnl'][0]-2*c:+.2f}")
# positive-share and tail share of fade pnl, 外 anchor +2 N=276
mm = wmask(ev, "外 2021-26H1"); o, D = ev.stats(ev.s, mm)
pnl = np.where(D != 0, D * ev.ag * 1e4, -ev.s * ev.rN)[mm]
srt = np.sort(pnl)[::-1]; top = srt[: max(1, len(srt) // 10)].sum()
say(f"- 外 fade pnl の中身: 正 {np.mean(pnl>0)*100:.0f}%・中央値 {np.median(pnl):+.2f} bp・上位 10% 件が Σ の {top/pnl.sum()*100 if pnl.sum()!=0 else float('nan'):.0f}%")

say(f"\n- 実行時間 {time.time()-T0:.1f} s・scan 無し・M5 読込無し・MT5 無し・外部通信無し")
with open(OUT, "w", encoding="utf-8") as fo: fo.write(buf.getvalue())
print("->", OUT)
