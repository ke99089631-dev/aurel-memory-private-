# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-07 11:15 反証レーン] 対象: cycle20 (09:50)「5 分尺度で米株指数 ↔ 金の先行遅行は無い」の判定の上に載せた読み。
cycle20 の事前固定判定 H_L null／H_R null は再現して争わない（外 ρ(+1) −0.214%／ρ(−1) +0.295%／ρ(0) +15.44% を 1e-3 で一致・assert）。
壊しに行く読み:
  C1 「5 分格子では金と米株の間に先行遅行は無い（|ρ(k)|≤0.3%・k=±1..6）＝この粒度では構造的に存在しない」
  C2 弱信号: H_R ρ(−1)（金→US100）が 在 +0.31 (t1.5)／外 +0.30 (t1.3)／近年 +0.52 (t1.5) と 3 窓とも同符号正。cycle20 は窓別 null と記した。
  C3 「同時相関 ρ(0) の符号レジーム: 2014-19 負（safe-haven 型）→ 2020 以降 正（金がリスク資産と同方向）」
  C5 「US100↔US500 の相互ラグが両側とも小さく負＝配信遅延なし（遅延なら片側が正）」
  C4 「情報は同じ 5 分足で両市場に織り込まれる」（配信の時刻ずれ検査・記述）

事前固定の判定規則（結果を見る前に書く・変えない）
  A（C2 弱信号・金→US100）
    A1 プール 2012-26H1 の ρ(−1)（日クラスタ t）と週循環シフト置換（US 系列 ±1..150 週・300 通り）p。
       **発火**（cycle20 の「null」は窓分割の産物）= t_cl ≥ 2 ∧ p < 0.05。D2: プールは構造の検定にのみ使い edge の判定には使わない。
    A2 機構（stale 部分更新）: US100 の ex-ante 局所 stale 率 s_t = 直前 24 取引足のうち flat の比率（t−24..t−1）。窓内三分位。
       **broken（市場構造でなく配信の stale）** = 最も流動的な三分位の ρ(−1) t<1 ∧ 最も stale な三分位の ρ(−1) ≥ 2× 最も流動的な三分位。
       一様（三分位の ρ(−1) が全部同符号で比 <2）なら「統計的弱信号として生存（経済的には A3）」。XAU→US500 で複製。
    A3 経済的大きさ: β_raw(r_US100,t on r_XAU,t−1)×sd(r_XAU) [bp of US100] vs US100 半スプレッド（US100_m5_spread.npz・開場足 sp_med 中央値/価格・2022-26。在は外の値を代用と明記）。
       応答 < 半スプレッド → 受け取れない（コスト倍＝半スプレッド×2 も併記）。
  B（C1 「どの時刻にも無い」）
    B1 slot 別（ET 5 分 288 枡）× k∈{+1,−1} の ρ と t=ρ√(n−2)/√(1−ρ²)（slot 内は 1 日 1 観測＝日クラスタ不要）。外・在。
       family-wise: US 系列を k 週循環シフト（±1..150・300 通り）して 576 セルの max|t| 分布 → p_fw。
       **broken（局所先行あり）** = 外に p_fw<0.05 のセルが 1 つ以上 ∧ 同セルが在で同符号 |t|≥1.5。報告: そのセルの 1 sd 応答 bp vs 半スプレッド。
    B2 ジャンプ条件: |z_US,t−1| ≥ 3 の足に限った sign(r_US,t−1)·r_XAU,t の平均 bp（日クラスタ t）／|z_XAU,t−1| ≥ 3 → US100 次足。
       **broken（条件付き先行あり）** = 外で 平均 ≥ 半スプレッド ∧ t≥2。
    B1・B2 とも不発なら C1 survived。
  C（C3 符号レジーム）
    C1' 年×セッション（Asia 18:00–02:55／London 03:00–09:25／NY 09:30–16:55 ET）の ρ(0) と t。
    C2' 日別 ρ(0)（有効対 ≥100 の日）の年別 中央値と正の日の比率。
    **survived** = 2014-19 の 6 年中 ≥5 年で 3 セッション全部 負 ∧ 2021-26H1 の 6 期中 ≥5 期で 3 セッション全部 正 ∧ 年別 日中央値の符号がプール符号と ≥13/15 年一致。
    **broken（組成）** = 1 つのセッションだけが符号を担い、別セッションで逆符号 |t|≥2 の年が 2014-19 または 2021-26 に ≥3 年。他 inconclusive。
    記述: 標準化前（生 bp）の ρ(0) 年別。
  D（C5 診断の機構・記述）
    年別 corr(US100_t, US500_t−1)・corr(US100_t, US500_t+1) と 各系列の ρ1（取引・非 flat・連続）、ρ(0)。
    予測（反証 08:30 (6) の feed-wide lag1 戻し）: 相互ラグ ≈ ρ1·ρ(0)。Spearman(年別 相互ラグ, ρ1·ρ0) ≥0.5 なら「負の相互ラグは lag1 戻しの伝播」。
    「配信遅延なし」の読みは、どの窓でも片側だけ正 ≥0.5% (t≥2) が無ければ survived。
  E（C4 時刻ずれ・記述）: 配信 B が δ 秒遅れる純粋ずれモデルでは ρ(+1) ≈ ρ_true·δ/300、ρ(0) ≈ ρ_true·(1−δ/300)
    → δ̂ = 300·ρ(+1)/(ρ(0)+ρ(+1)) 秒（US100 が遅れる側）／金が遅れる側は ρ(−1)。窓別に秒を印字。
  多重検定: B1 は 576 セル同時の置換 family-wise。C は規則に年数の閾値を内蔵。A1 は 1 セル。
  look-ahead: s_t は t−1 以前の足のみ。z の標準化は cycle20 と同じ年×slot（同年 in-sample・バイアス O(1/250)）。
  D2: 窓別。プール（A1・B1 の帰無分布）は構造検定のみ。
入力: data/macro/{XAU,US100,US500}_m5_close.npz・US100_m5_spread.npz のみ。scan 無し・MT5 無し・外部通信無し。seed 20261107
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c20_leadlag.md"); L = []
NY = "America/New_York"; SEED = 20261107; rng = np.random.default_rng(SEED)
NSHIFT = 150
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c20] 5 分 先行遅行の読み C1/C2/C3/C5/C4 を壊す — {time.strftime('%Y-%m-%d %H:%M')}")

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    say(f"- {sym}: {len(ts)} 本 {pd.to_datetime(ts[0],unit='s')}〜{pd.to_datetime(ts[-1],unit='s')} UTC・穴 {(np.diff(ts)!=300).sum()}")
    return ts, cl
tsX, cX = load("XAU"); tsU, cU = load("US100"); tsS, cS = load("US500")

def join(tsA, cA, tsB, cB):
    com = np.intersect1d(tsA, tsB); ia = np.searchsorted(tsA, com); ib = np.searchsorted(tsB, com)
    return com, cA[ia], cB[ib]

def prep(ts, ca, cb):
    """identical definitions to c20 (trading bars, flat exclusion, year x slot standardization)"""
    n = len(ts); consec = np.zeros(n, bool); consec[1:] = np.diff(ts) == 300
    ra = np.full(n, np.nan); rb = np.full(n, np.nan)
    ra[1:] = np.diff(np.log(ca)) * 1e4; rb[1:] = np.diff(np.log(cb)) * 1e4
    t = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    h = t.hour.to_numpy(); mn = t.minute.to_numpy(); wd = t.weekday.to_numpy(); yr = t.year.to_numpy()
    day = yr * 10000 + t.month.to_numpy() * 100 + t.day.to_numpy()
    slot = h * 12 + mn // 5
    opn = ((wd <= 3) & (h != 17)) | ((wd == 4) & (h < 17)) | ((wd == 6) & (h >= 18))
    va = opn & consec & np.isfinite(ra) & (ra != 0); vb = opn & consec & np.isfinite(rb) & (rb != 0)
    def std(r, v):
        z = np.full(n, np.nan); key = (yr - yr.min()) * 288 + slot
        s2 = np.bincount(key[v], weights=r[v] ** 2, minlength=key.max() + 1); s1 = np.bincount(key[v], weights=r[v], minlength=key.max() + 1); c = np.bincount(key[v], minlength=key.max() + 1)
        var = np.where(c > 1, s2 / np.maximum(c, 1) - (s1 / np.maximum(c, 1)) ** 2, np.nan)
        ky = yr - yr.min(); ys2 = np.bincount(ky[v], weights=r[v] ** 2, minlength=ky.max() + 1); yc = np.bincount(ky[v], minlength=ky.max() + 1); yvar = ys2 / np.maximum(yc, 1)
        sd = np.sqrt(var[key]); bad = ~np.isfinite(sd) | (c[key] < 30); sd[bad] = np.sqrt(yvar[ky][bad])
        z[v] = r[v] / sd[v]; return z
    za = std(ra, va); zb = std(rb, vb)
    # ex-ante local staleness of series b: flat share of prior 24 trading bars (t-24..t-1), computed on the trading-bar subsequence
    idx = np.where(opn)[0]; fb = ((rb == 0) | ~np.isfinite(rb))[idx].astype(float); cs = np.concatenate([[0.0], np.cumsum(fb)])
    st = np.full(n, np.nan); W = 24
    pos = np.arange(len(idx)); ok = pos >= W
    st[idx[ok]] = (cs[pos[ok]] - cs[pos[ok] - W]) / W   # bars pos-W .. pos-1
    return dict(n=n, ts=ts, ra=ra, rb=rb, za=za, zb=zb, va=va, vb=vb, yr=yr, day=day, h=h, mn=mn, slot=slot, opn=opn, pa=ca, pb=cb, stale_b=st, wd=wd)

def shift(x, k):
    y = np.full_like(x, np.nan, dtype=float)
    if k > 0: y[k:] = x[:-k]
    elif k < 0: y[:k] = x[-k:]
    else: y = x.copy()
    return y

def corr_cl(x, y, day, W):
    m = W & np.isfinite(x) & np.isfinite(y)
    if m.sum() < 100: return np.nan, np.nan, int(m.sum()), np.nan
    xx = x[m] - x[m].mean(); yy = y[m] - y[m].mean(); d = day[m]
    sxy = (xx * yy).sum(); syy = (yy * yy).sum(); sxx = (xx * xx).sum()
    rho = sxy / math.sqrt(sxx * syy); beta = sxy / syy; e = xx - beta * yy
    _, inv = np.unique(d, return_inverse=True); g = np.bincount(inv, weights=yy * e)
    se = math.sqrt((g ** 2).sum()) / syy; t = beta / se
    return rho, t, int(m.sum()), se * math.sqrt(syy / sxx)

def mean_cl(y, d):
    """mean with day-cluster t"""
    if len(y) < 30: return np.nan, np.nan, len(y)
    _, inv = np.unique(d, return_inverse=True); g = np.bincount(inv, weights=y); c = np.bincount(inv)
    m = y.mean(); se = math.sqrt(((g - c * m) ** 2).sum()) / len(y); return m, m / se, len(y)

def wins(yr, lo, hi): return (yr >= lo) & (yr <= hi)

com, ca, cb = join(tsX, cX, tsU, cU); P = prep(com, ca, cb)
WIN = {"在 2012-20": wins(P["yr"], 2012, 2020), "外 2021-26H1": wins(P["yr"], 2021, 2026), "近年 2024-26H1": wins(P["yr"], 2024, 2026), "プール 2012-26H1": wins(P["yr"], 2012, 2026)}
wl_is, wl_oos, wl_rec, wl_pool = list(WIN)

say("\n## 0. 再現（cycle20 外 ρ(+1)/ρ(−1)/ρ(0)・assert 1e-3）")
rep = {}
for k in (1, -1, 0):
    rho, t, n, se = corr_cl(P["za"], shift(P["zb"], k), P["day"], WIN[wl_oos]); rep[k] = (rho, t, n, se)
    say(f"- 外 k={k:+d}: ρ {rho*100:+.3f}% (t_cl {t:+.2f}, n{n})")
assert abs(rep[1][0] - (-0.00214)) < 1e-3 and abs(rep[-1][0] - 0.00295) < 1e-3 and abs(rep[0][0] - 0.1544) < 1e-3, "c20 replication failed"
say("- assert OK（cycle20 と一致）")

# ------------------------------------------------------------------ A
say("\n## A. C2 弱信号: 金→US100 ρ(−1) のプール・機構・経済")
VER = {}
def perm_p(k, W, x, y, day, nshift=NSHIFT):
    rho_obs, t_obs, n_obs, se = corr_cl(x, shift(y, k), day, W); rs = []
    for s in list(range(1, nshift + 1)) + list(range(-nshift, 0)):
        r, _, _, _ = corr_cl(x, shift(y, k + s * 2016), day, W); rs.append(r)
    rs = np.array(rs); return rho_obs, t_obs, n_obs, se, (np.abs(rs) >= abs(rho_obs)).mean(), np.nanstd(rs)
say("### A1 プール 2012-26H1")
rho, t, n, se, p, rsd = perm_p(-1, WIN[wl_pool], P["za"], P["zb"], P["day"])
a1_fire = (t >= 2) and (p < 0.05)
say(f"- プール ρ(−1) **{rho*100:+.3f}% (t_cl {t:+.2f}, n{n}, MDE {2*se*100:.3f}%)**・週循環シフト置換 p **{p:.3f}**（帰無 sd {rsd*100:.3f}%）→ A1 {'**発火**（窓分割の産物）' if a1_fire else '不発'}")
rho1, t1, n1, se1, p1, _ = perm_p(1, WIN[wl_pool], P["za"], P["zb"], P["day"])
say(f"- 対照 プール ρ(+1) {rho1*100:+.3f}% (t {t1:+.2f})・置換 p {p1:.3f}")
VER["A1"] = a1_fire
# yearly ρ(-1) sign count
ys = []
for y in range(2012, 2027):
    r, tt, nn, _ = corr_cl(P["za"], shift(P["zb"], -1), P["day"], P["yr"] == y); ys.append((y, r, tt))
npos = sum(1 for _, r, _ in ys if r > 0); kmin = min(npos, 15 - npos)
p_sign = min(1.0, 2 * sum(math.comb(15, i) for i in range(0, kmin + 1)) / 2 ** 15)
say(f"- 年別 ρ(−1) 符号: 正 {npos}/15・|t|≥2 {sum(1 for _, _, tt in ys if abs(tt) >= 2)} 年（帰無期待 0.75）・符号検定 両側 p {p_sign:.3f}・年別 t: " + " ".join(f"{y}:{tt:+.1f}" for y, _, tt in ys))

say("### A2 機構: US100 の ex-ante 局所 stale 率（直前 24 取引足の flat 比率）三分位 × ρ(−1)")
def tertile_table(Pd, lab):
    out = {}
    for wl in (wl_is, wl_oos, wl_rec, wl_pool):
        W = WIN_[wl] if Pd is not P else WIN[wl]
        zbm1 = shift(Pd["zb"], -1); m = W & np.isfinite(Pd["za"]) & np.isfinite(zbm1) & np.isfinite(Pd["stale_b"])
        q1, q2 = np.quantile(Pd["stale_b"][m], [1/3, 2/3])
        cells = []
        for tl, T in (("流動(下)", Pd["stale_b"] <= q1), ("中", (Pd["stale_b"] > q1) & (Pd["stale_b"] <= q2)), ("stale(上)", Pd["stale_b"] > q2)):
            r, tt, nn, _ = corr_cl(Pd["za"], zbm1, Pd["day"], W & T); cells.append((tl, r, tt, nn))
        out[wl] = cells
        say(f"- {lab} {wl}（閾値 {q1:.3f}/{q2:.3f}）: " + "・".join(f"{tl} {r*100:+.3f}% (t{tt:+.2f}, n{nn})" for tl, r, tt, nn in cells))
    return out
WIN_ = None
A2 = tertile_table(P, "XAU→US100")
lo_r, lo_t = A2[wl_pool][0][1], A2[wl_pool][0][2]; hi_r = A2[wl_pool][2][1]
a2_stale = (lo_t < 1) and (hi_r >= 2 * lo_r) and (hi_r > 0)
same_sign = all(np.sign(c[1]) == np.sign(A2[wl_pool][0][1]) for c in A2[wl_pool]); ratio = hi_r / lo_r if lo_r != 0 else np.inf
say(f"- A2 判定（プール）: 流動 t {lo_t:+.2f}・stale/流動 比 {ratio:.2f}・同符号 {same_sign} → {'**broken（stale 配信の部分更新）**' if a2_stale else ('一様＝統計的弱信号として生存' if same_sign and ratio < 2 else 'inconclusive')}")
VER["A2_stale"] = a2_stale; VER["A2_uniform"] = same_sign and ratio < 2
# also staleness of XAU side as control for k=+1 (US100→XAU): compute XAU stale ex-ante
idx = np.where(P["opn"])[0]; fa = ((P["ra"] == 0) | ~np.isfinite(P["ra"]))[idx].astype(float); cs = np.concatenate([[0.0], np.cumsum(fa)]); stA = np.full(P["n"], np.nan); pos = np.arange(len(idx)); ok = pos >= 24; stA[idx[ok]] = (cs[pos[ok]] - cs[pos[ok] - 24]) / 24
zb1 = shift(P["zb"], 1); m = WIN[wl_pool] & np.isfinite(P["za"]) & np.isfinite(zb1) & np.isfinite(stA); q1, q2 = np.quantile(stA[m], [1/3, 2/3])
say("- 対照 US100→XAU ρ(+1) × XAU stale 三分位（プール）: " + "・".join(f"{tl} {corr_cl(P['za'], zb1, P['day'], WIN[wl_pool] & T)[0]*100:+.3f}% (t{corr_cl(P['za'], zb1, P['day'], WIN[wl_pool] & T)[1]:+.2f})" for tl, T in (("流動", stA <= q1), ("中", (stA > q1) & (stA <= q2)), ("stale", stA > q2))))
# replication XAU -> US500
com2, ca2, cb2 = join(tsX, cX, tsS, cS); Q = prep(com2, ca2, cb2)
WIN_ = {"在 2012-20": wins(Q["yr"], 2012, 2020), "外 2021-26H1": wins(Q["yr"], 2021, 2026), "近年 2024-26H1": wins(Q["yr"], 2024, 2026), "プール 2012-26H1": wins(Q["yr"], 2012, 2026)}
rq, tq, nq, seq = corr_cl(Q["za"], shift(Q["zb"], -1), Q["day"], WIN_[wl_pool]); say(f"- 複製 XAU→US500 プール ρ(−1) {rq*100:+.3f}% (t{tq:+.2f}, n{nq})")
A2q = tertile_table(Q, "XAU→US500")

say("### A3 経済的大きさ（US100 側の次足応答 vs US100 半スプレッド）")
zz = np.load(os.path.join(MAC, "US100_m5_spread.npz")); sts = zz["ts"].astype(np.int64); spm = zz["sp_med"].astype(float); nop = zz["n_open"].astype(int)
ok = (nop > 0) & np.isfinite(spm) & (spm > 0)
ib = np.searchsorted(P["ts"], sts[ok]); ib = np.clip(ib, 0, P["n"] - 1); px = P["pb"][ib]
hs_us_bp = np.median(spm[ok] / px * 1e4) / 2
say(f"- US100 半スプレッド（2022-01〜2026-06 開場足・sp_med 中央値/価格）: **{hs_us_bp:.3f} bp**（往復 {4*hs_us_bp:.3f} bp・コスト倍 {2*hs_us_bp:.3f}）・在は外の値を代用")
for wl in (wl_is, wl_oos, wl_rec, wl_pool):
    W = WIN[wl]; m = W & P["vb"] & shift(P["va"].astype(float), 1).astype(bool)
    rx = shift(P["ra"], 1)[m]; ru = P["rb"][m]
    beta = (ru * rx).sum() / (rx * rx).sum(); resp = beta * rx.std()
    thr = np.quantile(np.abs(rx), 0.9); big = np.abs(rx) >= thr
    my, ty, ny = mean_cl(np.sign(rx[big]) * ru[big], P["day"][m][big])
    say(f"- {wl}: β_raw(US100_t on XAU_t−1) {beta:+.4f} bp/bp・sd(r_XAU) {rx.std():.2f} bp → 1 sd 応答 **{resp:+.3f} bp**（半スプレッドの {abs(resp)/hs_us_bp*100:.1f}%）；上位 10% |r_XAU,t−1| の符号つき US100 次足 {my:+.3f} bp (t{ty:+.2f}, n{ny})")

# ------------------------------------------------------------------ B
say("\n## B. C1「どの時刻にも無い」: slot 別 288×2 の family-wise・ジャンプ条件")
def slot_rhos(x, y, W, slot, nslot=288):
    m = W & np.isfinite(x) & np.isfinite(y)
    k = slot[m]; xx = x[m]; yy = y[m]
    n = np.bincount(k, minlength=nslot).astype(float); sx = np.bincount(k, weights=xx, minlength=nslot); sy = np.bincount(k, weights=yy, minlength=nslot)
    sxy = np.bincount(k, weights=xx * yy, minlength=nslot); sxx = np.bincount(k, weights=xx * xx, minlength=nslot); syy = np.bincount(k, weights=yy * yy, minlength=nslot)
    with np.errstate(invalid="ignore", divide="ignore"):
        cov = sxy / n - (sx / n) * (sy / n); vx = sxx / n - (sx / n) ** 2; vy = syy / n - (sy / n) ** 2
        rho = cov / np.sqrt(vx * vy); rho[n < 200] = np.nan
        t = rho * np.sqrt(np.maximum(n - 2, 1)) / np.sqrt(np.maximum(1 - rho ** 2, 1e-12))
    return rho, t, n
def slot_all(zb_, W):
    out = {}
    for k in (1, -1):
        out[k] = slot_rhos(P["za"], shift(zb_, k), W, P["slot"])
    return out
S_oos = slot_all(P["zb"], WIN[wl_oos]); S_is = slot_all(P["zb"], WIN[wl_is])
def maxabs(S): return np.nanmax(np.concatenate([np.abs(S[1][1]), np.abs(S[-1][1])]))
obs_max = maxabs(S_oos)
null_max = []
for s in list(range(1, NSHIFT + 1)) + list(range(-NSHIFT, 0)):
    zs = shift(P["zb"], s * 2016); null_max.append(maxabs(slot_all(zs, WIN[wl_oos])))
null_max = np.array(null_max)
p_fw = (null_max >= obs_max).mean()
say(f"- 外 576 セル max|t| 観測 **{obs_max:.2f}** → 週シフト帰無 中央値 {np.median(null_max):.2f}・95% 点 {np.quantile(null_max,0.95):.2f}・**p_fw {p_fw:.3f}**")
# list top cells OOS and their IS values
cells = []
for k in (1, -1):
    r, t, n = S_oos[k]; ri, ti, ni = S_is[k]
    for sidx in range(288):
        if np.isfinite(t[sidx]): cells.append((abs(t[sidx]), k, sidx, r[sidx], t[sidx], n[sidx], ri[sidx], ti[sidx]))
cells.sort(reverse=True)
thr95 = np.quantile(null_max, 0.95)
say("- 外 上位 8 セル（slot ET・k・ρ・t・n／在 ρ・t）:")
b1_fire = False
for a, k, sidx, r, t, n, ri, ti in cells[:8]:
    hh, mm = divmod(sidx * 5, 60); fw = (null_max >= a).mean()
    hit = (fw < 0.05) and np.isfinite(ti) and (np.sign(ri) == np.sign(r)) and (abs(ti) >= 1.5)
    b1_fire |= hit
    say(f"  - {hh:02d}:{mm:02d} ET k={k:+d}: ρ {r*100:+.2f}% t {t:+.2f} (n{int(n)}) p_fw {fw:.3f}／在 ρ {ri*100:+.2f}% t {ti:+.2f} {'← **発火**' if hit else ''}")
# same for IS top cells (descriptive)
cells_is = []
for k in (1, -1):
    ri, ti, ni = S_is[k]; r, t, n = S_oos[k]
    for sidx in range(288):
        if np.isfinite(ti[sidx]): cells_is.append((abs(ti[sidx]), k, sidx, ri[sidx], ti[sidx], ni[sidx], r[sidx], t[sidx]))
cells_is.sort(reverse=True)
say("- 在 上位 5 セル（記述・外の値を併記）:")
for a, k, sidx, ri, ti, ni, r, t in cells_is[:5]:
    hh, mm = divmod(sidx * 5, 60); say(f"  - {hh:02d}:{mm:02d} ET k={k:+d}: 在 ρ {ri*100:+.2f}% t {ti:+.2f} (n{int(ni)})／外 ρ {r*100:+.2f}% t {t:+.2f}")
# scheduled slots (08:30, 10:00, 14:00, 09:30, 18:00 reopen) explicit
say("- 指定 slot（発表・寄り・再開）外／在 ρ(+1)・ρ(−1) [%]:")
for hh, mm in ((8, 30), (8, 35), (9, 30), (9, 35), (10, 0), (10, 5), (14, 0), (14, 5), (18, 5), (18, 10)):
    sidx = hh * 12 + mm // 5
    say(f"  - {hh:02d}:{mm:02d}: 外 ρ(+1) {S_oos[1][0][sidx]*100:+.2f} (t{S_oos[1][1][sidx]:+.1f})・ρ(−1) {S_oos[-1][0][sidx]*100:+.2f} (t{S_oos[-1][1][sidx]:+.1f})／在 ρ(+1) {S_is[1][0][sidx]*100:+.2f} (t{S_is[1][1][sidx]:+.1f})・ρ(−1) {S_is[-1][0][sidx]*100:+.2f} (t{S_is[-1][1][sidx]:+.1f})")
# sign share across slots (descriptive): share of slots with rho(-1)>0 in OOS/IS
for lab, S in (("外", S_oos), ("在", S_is)):
    r = S[-1][0]; f = np.isfinite(r); say(f"- {lab} slot 別 ρ(−1)>0 の slot 比率 {np.mean(r[f]>0)*100:.0f}% (n slot {f.sum()})・ρ(+1)>0 {np.mean(S[1][0][np.isfinite(S[1][0])]>0)*100:.0f}%")
VER["B1"] = b1_fire
say(f"- B1 判定: {'**broken（局所先行あり）**' if b1_fire else '不発（局所先行なし）'}")

say("### B2 ジャンプ条件（|z_{t−1}| ≥ 3）")
hs_x = {}
for wl in (wl_is, wl_oos, wl_rec):
    W = WIN[wl]; m = W & P["va"] & shift(P["vb"].astype(float), 1).astype(bool)
    px = np.median(P["pa"][m]); hs_x[wl] = 0.08 / px * 1e4
    zu = shift(P["zb"], 1)[m]; ru = shift(P["rb"], 1)[m]; rx = P["ra"][m]; d = P["day"][m]
    big = np.abs(zu) >= 3; my, ty, ny = mean_cl(np.sign(ru[big]) * rx[big], d[big])
    # also |z|>=2
    big2 = np.abs(zu) >= 2; my2, ty2, ny2 = mean_cl(np.sign(ru[big2]) * rx[big2], d[big2])
    say(f"- {wl} US100 ジャンプ→金 次足: |z|≥3 (n{ny}) **{my:+.3f} bp (t{ty:+.2f})**・|z|≥2 (n{ny2}) {my2:+.3f} bp (t{ty2:+.2f})・金 半スプレッド {hs_x[wl]:.2f} bp")
    m2 = W & P["vb"] & shift(P["va"].astype(float), 1).astype(bool)
    zx = shift(P["za"], 1)[m2]; rxx = shift(P["ra"], 1)[m2]; ruu = P["rb"][m2]; d2 = P["day"][m2]
    bg = np.abs(zx) >= 3; mu, tu, nu = mean_cl(np.sign(rxx[bg]) * ruu[bg], d2[bg])
    bg2 = np.abs(zx) >= 2; mu2, tu2, nu2 = mean_cl(np.sign(rxx[bg2]) * ruu[bg2], d2[bg2])
    say(f"- {wl} 金 ジャンプ→US100 次足: |z|≥3 (n{nu}) **{mu:+.3f} bp (t{tu:+.2f})**・|z|≥2 (n{nu2}) {mu2:+.3f} bp (t{tu2:+.2f})・US100 半スプレッド {hs_us_bp:.3f} bp")
    if wl == wl_oos:
        b2_fire = ((my >= hs_x[wl]) and (ty >= 2)) or ((mu >= hs_us_bp) and (tu >= 2))
VER["B2"] = b2_fire
say(f"- B2 判定（外）: {'**broken（条件付き先行あり）**' if b2_fire else '不発'}")
say(f"- **C1 判定**: {'broken' if (b1_fire or b2_fire) else '**survived**（slot 別 family-wise・ジャンプ条件とも先行なし）'}")

# ------------------------------------------------------------------ C
say("\n## C. C3 符号レジーム: 年×セッション ρ(0)・日別 ρ(0)")
tmin = P["h"] * 60 + P["mn"]
SESS = {"Asia 18–03": (P["h"] >= 18) | (P["h"] < 3), "London 03–09:30": (P["h"] >= 3) & (tmin < 570), "NY 09:30–17": (tmin >= 570) & (P["h"] < 17)}
say("| 年 | プール ρ(0) | " + " | ".join(SESS) + " | 日別 中央値 | 正の日 % | 生 bp ρ(0) |"); say("|---|---|" + "---|" * len(SESS) + "---|---|---|")
rows = {}
for y in range(2012, 2027):
    W = P["yr"] == y; r0, t0, n0, _ = corr_cl(P["za"], P["zb"], P["day"], W)
    ses = [corr_cl(P["za"], P["zb"], P["day"], W & S) for S in SESS.values()]
    # daily rho
    m = W & np.isfinite(P["za"]) & np.isfinite(P["zb"]); d = P["day"][m]; xa = P["za"][m]; xb = P["zb"][m]
    u, inv = np.unique(d, return_inverse=True); n = np.bincount(inv).astype(float)
    sx = np.bincount(inv, weights=xa); sy = np.bincount(inv, weights=xb); sxy = np.bincount(inv, weights=xa * xb); sxx = np.bincount(inv, weights=xa * xa); syy = np.bincount(inv, weights=xb * xb)
    with np.errstate(invalid="ignore", divide="ignore"):
        rd = (sxy / n - sx / n * sy / n) / np.sqrt((sxx / n - (sx / n) ** 2) * (syy / n - (sy / n) ** 2))
    rd = rd[n >= 100]; med = np.nanmedian(rd); pos_ = np.nanmean(rd > 0)
    rraw, _, _, _ = corr_cl(P["ra"], P["rb"], P["day"], W & P["va"] & P["vb"])
    rows[y] = dict(r0=r0, t0=t0, ses=ses, med=med, pos=pos_, raw=rraw)
    say(f"| {y}{'H1' if y==2026 else ''} | {r0*100:+.1f}% (t{t0:+.1f}) | " + " | ".join(f"{r*100:+.1f}% (t{t:+.1f})" for r, t, _, _ in ses) + f" | {med*100:+.1f}% | {pos_*100:.0f}% | {rraw*100:+.1f}% |")
def all_sign(y, sgn): return all(np.sign(r) == sgn for r, _, _, _ in rows[y]["ses"])
neg_years = [y for y in range(2014, 2020) if all_sign(y, -1)]; pos_years = [y for y in range(2021, 2027) if all_sign(y, 1)]
med_match = sum(1 for y in rows if np.sign(rows[y]["med"]) == np.sign(rows[y]["r0"]))
opp = 0
for y in list(range(2014, 2020)) + list(range(2021, 2027)):
    sgn = np.sign(rows[y]["r0"])
    if any((np.sign(r) == -sgn) and (abs(t) >= 2) for r, t, _, _ in rows[y]["ses"]): opp += 1
c_surv = (len(neg_years) >= 5) and (len(pos_years) >= 5) and (med_match >= 13)
c_brok = opp >= 3
say(f"- 2014-19 で 3 セッション全部 負: {len(neg_years)}/6 {neg_years}／2021-26H1 で全部 正: {len(pos_years)}/6 {pos_years}／日別中央値の符号一致 {med_match}/15／逆符号 |t|≥2 のセッションを持つ年 {opp}")
VER["C"] = "survived" if c_surv else ("broken" if c_brok else "inconclusive")
say(f"- **C3 判定**: **{VER['C']}**")
# 2020 and 2012-13 transitional (descriptive)
say("- 境界年（記述）: 2012 " + f"{rows[2012]['r0']*100:+.1f}%・2013 {rows[2013]['r0']*100:+.1f}%・2020 {rows[2020]['r0']*100:+.1f}%（セッション: " + "・".join(f"{r*100:+.1f}" for r, _, _, _ in rows[2020]["ses"]) + "）")
# monthly rho(0) 2020: when did the sign flip
say("- 2019-07〜2021-06 月別 ρ(0) [%]: " + " ".join(f"{ym}:{corr_cl(P['za'], P['zb'], P['day'], (P['yr']==ym//100)&((P['day']//100)%100==ym%100))[0]*100:+.0f}" for ym in [201907+i for i in range(6)] + [202001+i for i in range(12)] + [202101+i for i in range(6)]))

# ------------------------------------------------------------------ D
say("\n## D. C5 診断の機構: US100↔US500 相互ラグ vs lag1 戻し（年別）")
com3, c3a, c3b = join(tsU, cU, tsS, cS); R3 = prep(com3, c3a, c3b)
say("| 年 | ρ(0) | corr(100_t,500_t−1) | corr(100_t,500_t+1) | ρ1 US100 | ρ1 US500 | 予測 ρ1(500)·ρ0 | 予測 ρ1(100)·ρ0 |"); say("|---|---|---|---|---|---|---|---|")
dd = []
for y in range(2012, 2027):
    W = R3["yr"] == y
    r0, _, _, _ = corr_cl(R3["za"], R3["zb"], R3["day"], W)
    rp, tp, _, _ = corr_cl(R3["za"], shift(R3["zb"], 1), R3["day"], W); rm, tm, _, _ = corr_cl(R3["za"], shift(R3["zb"], -1), R3["day"], W)
    a1, _, _, _ = corr_cl(R3["za"], shift(R3["za"], 1), R3["day"], W); b1, _, _, _ = corr_cl(R3["zb"], shift(R3["zb"], 1), R3["day"], W)
    dd.append((y, r0, rp, rm, a1, b1))
    say(f"| {y}{'H1' if y==2026 else ''} | {r0*100:.1f}% | {rp*100:+.2f}% (t{tp:+.1f}) | {rm*100:+.2f}% (t{tm:+.1f}) | {a1*100:+.2f}% | {b1*100:+.2f}% | {b1*r0*100:+.2f}% | {a1*r0*100:+.2f}% |")
df = pd.DataFrame(dd, columns=["y", "r0", "rp", "rm", "a1", "b1"])
sp1 = df["rp"].corr(df["b1"] * df["r0"], method="spearman"); sp2 = df["rm"].corr(df["a1"] * df["r0"], method="spearman")
say(f"- Spearman(年別 corr(100_t,500_t−1), ρ1(500)·ρ0) **{sp1:+.2f}**／(corr(100_t,500_t+1), ρ1(100)·ρ0) **{sp2:+.2f}**（n15）→ {'lag1 戻しの伝播と整合' if min(sp1, sp2) >= 0.5 else '整合せず（別機構）'}")
say(f"- 2014-22 プール: corr(100_t,500_t−1) {corr_cl(R3['za'], shift(R3['zb'],1), R3['day'], wins(R3['yr'],2014,2022))[0]*100:+.2f}%・ρ1 US500 {corr_cl(R3['zb'], shift(R3['zb'],1), R3['day'], wins(R3['yr'],2014,2022))[0]*100:+.2f}%／2023-26H1: {corr_cl(R3['za'], shift(R3['zb'],1), R3['day'], wins(R3['yr'],2023,2026))[0]*100:+.2f}%・ρ1 {corr_cl(R3['zb'], shift(R3['zb'],1), R3['day'], wins(R3['yr'],2023,2026))[0]*100:+.2f}%")
# one-sided positive check
one_sided = False
for wl, (lo, hi) in (("在", (2012, 2020)), ("外", (2021, 2026))):
    W = wins(R3["yr"], lo, hi); rp, tp, _, _ = corr_cl(R3["za"], shift(R3["zb"], 1), R3["day"], W); rm, tm, _, _ = corr_cl(R3["za"], shift(R3["zb"], -1), R3["day"], W)
    one_sided |= ((rp >= 0.005 and tp >= 2) != (rm >= 0.005 and tm >= 2))
VER["D"] = "survived" if not one_sided else "broken"
say(f"- **C5 判定**: 片側だけ正 ≥0.5% (t≥2) は {'あり → broken' if one_sided else 'なし → **survived**（ただし負の相互ラグは配信の lag1 戻しの伝播で「同期の証明」ではない）'}")
# also XAU lag1 by window for E-context
say("- 参考 ρ1（取引・非 flat・連続・標準化後）: XAU 在 " + f"{corr_cl(P['za'], shift(P['za'],1), P['day'], WIN[wl_is])[0]*100:+.2f}%／外 {corr_cl(P['za'], shift(P['za'],1), P['day'], WIN[wl_oos])[0]*100:+.2f}%" + "・US100 在 " + f"{corr_cl(P['zb'], shift(P['zb'],1), P['day'], WIN[wl_is])[0]*100:+.2f}%／外 {corr_cl(P['zb'], shift(P['zb'],1), P['day'], WIN[wl_oos])[0]*100:+.2f}%")

# ------------------------------------------------------------------ E
say("\n## E. C4 時刻ずれ（記述）: 純粋ずれモデル δ̂ = 300·ρ(±1)/(ρ(0)+ρ(±1)) 秒")
for wl in (wl_is, wl_oos, wl_rec):
    r0 = corr_cl(P["za"], P["zb"], P["day"], WIN[wl])[0]; rp = corr_cl(P["za"], shift(P["zb"], 1), P["day"], WIN[wl])[0]; rm = corr_cl(P["za"], shift(P["zb"], -1), P["day"], WIN[wl])[0]
    dU = 300 * rp / (r0 + rp); dX = 300 * rm / (r0 + rm)
    say(f"- {wl}: ρ(0) {r0*100:+.2f}%・US100 遅れ側 δ̂ {dU:+.1f} 秒・金 遅れ側 δ̂ {dX:+.1f} 秒（|δ̂| ≤ 10 秒なら足境界は実質同期）")

# ------------------------------------------------------------------ verdicts
say("\n## 判定まとめ")
say(f"- C2 弱信号（金→US100）: A1 {'発火' if VER['A1'] else '不発'}／A2 {'stale broken' if VER['A2_stale'] else ('一様' if VER['A2_uniform'] else 'inconclusive')}")
say(f"- C1（先行遅行なし）: {'broken' if (VER['B1'] or VER['B2']) else 'survived'}（B1 {'発火' if VER['B1'] else '不発'}・B2 {'発火' if VER['B2'] else '不発'}）")
say(f"- C3（符号レジーム）: {VER['C']}")
say(f"- C5（配信遅延なし）: {VER['D']}")
say(f"\n実行 {time.time()-T0:.1f} s・seed {SEED}・入力 3 npz＋US100 spread npz のみ・scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
