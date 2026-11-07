# -*- coding: utf-8 -*-
"""
[cycle20 研究レーン 2026-11-07] 【探索・市場間連動（先行遅行）】5 分尺度で米株指数（US100 主・US500 複製）は金を先導するか／金は米株を先導するか
（憲章 2 条「市場間連動・先行遅行」の実データ検証。既存キャッシュ 3 本のみ・scan 無し・入口フィルタではない・市場構造の記述）

事前固定（検証前に書く・結果を見て変えない）
- データ: data/macro/XAU_m5_close.npz・US100_m5_close.npz・US500_m5_close.npz（Dukascopy bid・暦時刻の完全格子・前値埋め）。ts 一致で結合（⑫）。
  読込後に min/max 時刻（⑩）・曜日別 flat 比率（⑪）を印字。
- リターン r_t = ln c_t − ln c_{t−1} [bp]。足 t の時刻 = ts_t（足の開始・両系列同規約）。連続格子（ts 差 300）の対のみ。
- 取引足（ET 現地）: 月〜木 17:00–17:55 を除く・金 17:00 以降・土・日 18:00 前を除く。**flat（r=0）足は両系列とも除く**（stale の先行遅行アーティファクト対策）。
- 季節性除去（反証 08:30 教訓 (a)）: 年×slot（ET 5 分 288 枡）の sd で標準化 z = r/sd_{年,slot}（n<30 の枡は年 sd）。相関は z で計算、β_raw は bp で別途。
- 統計: ρ(k) = corr(z_XAU,t, z_US,t−k)、k>0 ＝ 米株が金を先導、k<0 ＝ 金が米株を先導。t は ET 日クラスタ（回帰 z_X ~ z_U,lag の β/se_cluster）。
- 窓: 在 2012-20／外 2021-26H1／近年 2024-26H1（D2・判定は外）。
- 主セル（2・Bonferroni 2）: **H_L** = ρ(+1)（US100→XAU・外）、予測 正（cycle8: 外の同時相関 +0.15＝同方向レジーム・株が情報の先導）。
  **H_R** = ρ(−1)（XAU→US100・外）、予測 ≈0。
  PASS（先行あり）= 外 |t_cl|≥2 ∧ 近年 同符号 |t_cl|≥1.5 ∧ 週循環シフト置換（US 系列を ±1..150 週シフト・300 通り・⑨）p<0.025。
  他 null（MDE = 2·se(ρ)）。
- 陽性対照: 外の ρ(0)（同時相関）が t≫2 で出ること／注入 z_X' = z_X + 0.02·z_U,t−1 で H_L の t が ≥2 になること。
- 経済的大きさ（判定でなく記述・ただし事前に書く）: β_raw [bp/bp]×sd(r_US) ＝ 1 sd の米株 5 分動きに対する金の次足 bp。上位 10% |r_US,t−1| 条件の sign(r_US,t−1)·r_X,t 平均 bp（日クラスタ t）。
  比較基準 = 金の片道半スプレッド 0.08 USD を窓の中央値価格で bp 化。**ρ が有意でも 1 sd 応答 < 半スプレッドなら「統計的先行・経済的に受け取れない」と記す。**
- 記述のみ: 相関図 k=−6..6、年別 ρ(+1)/ρ(−1)/ρ(0)、セッション別（NY 現物 09:30–16:00 ET vs 他）、US500 複製、0.1% winsor・flat 込みの頑健性。
- 事前の最重大反証: (i) 両系列が同ベンダー bid 配信＝配信遅延（CFD 指数の更新が futures より遅い）なら「株が遅れる」側に偽の ρ(−1) が出る。
  逆に金の更新が遅ければ偽の ρ(+1)。判別: 配信遅延なら ρ は**全時間帯で一様**・情報拡散なら NY 現物で大きい筈（セッション別を併記）。
  (ii) n≈10^6 で ρ 0.01 でも t>2 ＝統計的有意と経済的大きさは別（上記の bp 基準で言う）。(iii) bid のみ・2026-06 まで。
seed 20261107
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c20_crossasset_leadlag_result.md"); L = []
NY = "America/New_York"; SEED = 20261107; rng = np.random.default_rng(SEED)
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle20] 5 分尺度の市場間 先行遅行（US100/US500 ↔ XAU・Dukascopy bid・slot 標準化） — {time.strftime('%Y-%m-%d %H:%M')}")

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    say(f"- {sym}: {len(ts)} 本 {pd.to_datetime(ts[0],unit='s')}〜{pd.to_datetime(ts[-1],unit='s')} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}")
    return ts, cl
tsX, cX = load("XAU"); tsU, cU = load("US100"); tsS, cS = load("US500")

def join(tsA, cA, tsB, cB):
    com = np.intersect1d(tsA, tsB); ia = np.searchsorted(tsA, com); ib = np.searchsorted(tsB, com)
    return com, cA[ia], cB[ib]

def prep(ts, ca, cb, labb):
    n = len(ts); consec = np.zeros(n, bool); consec[1:] = np.diff(ts) == 300
    ra = np.full(n, np.nan); rb = np.full(n, np.nan)
    ra[1:] = np.diff(np.log(ca)) * 1e4; rb[1:] = np.diff(np.log(cb)) * 1e4
    t = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    h = t.hour.to_numpy(); mn = t.minute.to_numpy(); wd = t.weekday.to_numpy(); yr = t.year.to_numpy()
    day = yr * 10000 + t.month.to_numpy() * 100 + t.day.to_numpy()
    slot = h * 12 + mn // 5
    opn = ((wd <= 3) & (h != 17)) | ((wd == 4) & (h < 17)) | ((wd == 6) & (h >= 18))
    # flat ratios by weekday (⑪)
    for lab, r in (("XAU", ra), (labb, rb)):
        fl = (r == 0)
        say(f"- {lab} flat 比率 曜日別（全格子）: " + " ".join(f"{['月','火','水','木','金','土','日'][w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + f"・取引足内 flat {fl[opn].mean()*100:.2f}%")
    va = opn & consec & np.isfinite(ra) & (ra != 0); vb = opn & consec & np.isfinite(rb) & (rb != 0)
    say(f"- 結合 {n} 本・取引足 {opn.mean()*100:.1f}%・有効（非 flat・連続）XAU {va.sum()}／{labb} {vb.sum()}・両方 {(va&vb).sum()}")
    # slot standardization per year
    def std(r, v):
        z = np.full(n, np.nan); key = (yr - yr.min()) * 288 + slot
        s2 = np.bincount(key[v], weights=r[v] ** 2, minlength=key.max() + 1); s1 = np.bincount(key[v], weights=r[v], minlength=key.max() + 1); c = np.bincount(key[v], minlength=key.max() + 1)
        var = np.where(c > 1, s2 / np.maximum(c, 1) - (s1 / np.maximum(c, 1)) ** 2, np.nan)
        # year fallback
        ky = yr - yr.min(); ys2 = np.bincount(ky[v], weights=r[v] ** 2, minlength=ky.max() + 1); yc = np.bincount(ky[v], minlength=ky.max() + 1); yvar = ys2 / np.maximum(yc, 1)
        sd = np.sqrt(var[key]); bad = ~np.isfinite(sd) | (c[key] < 30); sd[bad] = np.sqrt(yvar[ky][bad])
        z[v] = r[v] / sd[v]; return z
    za = std(ra, va); zb = std(rb, vb)
    return dict(n=n, ra=ra, rb=rb, za=za, zb=zb, va=va, vb=vb, yr=yr, day=day, h=h, mn=mn, slot=slot, opn=opn, pa=ca, pb=cb)

def shift(x, k):
    """y[t] = x[t-k] (k>0: past), NaN fill"""
    y = np.full_like(x, np.nan, dtype=float)
    if k > 0: y[k:] = x[:-k]
    elif k < 0: y[:k] = x[-k:]
    else: y = x.copy()
    return y

def corr_cl(x, y, day, W):
    """rho, cluster-t (regress x on y, cluster by day), n, se_rho"""
    m = W & np.isfinite(x) & np.isfinite(y)
    if m.sum() < 100: return np.nan, np.nan, int(m.sum()), np.nan
    xx = x[m] - x[m].mean(); yy = y[m] - y[m].mean(); d = day[m]
    sxy = (xx * yy).sum(); syy = (yy * yy).sum(); sxx = (xx * xx).sum()
    rho = sxy / math.sqrt(sxx * syy); beta = sxy / syy; e = xx - beta * yy
    _, inv = np.unique(d, return_inverse=True); g = np.bincount(inv, weights=yy * e)
    se = math.sqrt((g ** 2).sum()) / syy; t = beta / se
    se_rho = se * math.sqrt(syy / sxx)
    return rho, t, int(m.sum()), se_rho

def wins(yr, lo, hi): return (yr >= lo) & (yr <= hi)

# ---------------- primary: XAU vs US100 ----------------
say("\n## 1. 結合・衛生（XAU × US100）")
com, ca, cb = join(tsX, cX, tsU, cU); P = prep(com, ca, cb, "US100")
WIN = {"在 2012-20": wins(P["yr"], 2012, 2020), "外 2021-26H1": wins(P["yr"], 2021, 2026), "近年 2024-26H1": wins(P["yr"], 2024, 2026)}
# slot variance profile sanity (ET hour) for XAU & US100 (OOS)
prof = []
for hh in range(24):
    m = P["va"] & P["vb"] & (P["h"] == hh) & WIN["外 2021-26H1"]
    prof.append((hh, np.mean(P["ra"][m] ** 2) if m.sum() else np.nan, np.mean(P["rb"][m] ** 2) if m.sum() else np.nan))
mx = np.nanmean([p[1] for p in prof]); mu = np.nanmean([p[2] for p in prof])
say("- 外 ET 時別 r² / 全日平均 XAU: " + " ".join(f"{hh}:{v/mx:.2f}" for hh, v, _ in prof if np.isfinite(v)))
say("- 外 ET 時別 r² / 全日平均 US100: " + " ".join(f"{hh}:{v/mu:.2f}" for hh, _, v in prof if np.isfinite(v)))
say(f"- z の sd 検査（≈1）: XAU {np.nanstd(P['za']):.3f}／US100 {np.nanstd(P['zb']):.3f}")

say("\n## 2. 相関図 ρ(k) = corr(z_XAU,t, z_US100,t−k)（k>0 米株先導・k<0 金先導）・日クラスタ t")
say("| 窓 | " + " | ".join(f"k={k:+d}" for k in range(-6, 7)) + " |"); say("|---|" + "---|" * 13)
RES = {}
for wl, W in WIN.items():
    row = []
    for k in range(-6, 7):
        rho, t, n, se = corr_cl(P["za"], shift(P["zb"], k), P["day"], W); RES[(wl, k)] = (rho, t, n, se)
        row.append(f"{rho*100:+.2f}% (t{t:+.1f})")
    say(f"| {wl} | " + " | ".join(row) + " |")
say(f"- 有効対 n: " + "・".join(f"{wl} k=+1 {RES[(wl,1)][2]}" for wl in WIN))

say("\n## 3. 主セル H_L（ρ(+1)・外）／H_R（ρ(−1)・外）＋置換・陽性対照・MDE")
def perm_p(k, W, nshift=150):
    rho0 = RES[(wl_oos, k)][0] if False else None
    rho_obs, t_obs, n_obs, _ = corr_cl(P["za"], shift(P["zb"], k), P["day"], W)
    rs = []; ts_ = []
    for s in list(range(1, nshift + 1)) + list(range(-nshift, 0)):
        zs = shift(P["zb"], k + s * 2016)
        r, t, n, _ = corr_cl(P["za"], zs, P["day"], W); rs.append(r); ts_.append(t)
    rs = np.array(rs); ts_ = np.array(ts_)
    p = (np.abs(rs) >= abs(rho_obs)).mean(); return rho_obs, t_obs, n_obs, p, np.nanstd(ts_), np.nanstd(rs)
wl_oos = "外 2021-26H1"; wl_rec = "近年 2024-26H1"; wl_is = "在 2012-20"
verdict = {}
for lab, k in (("H_L (US100→XAU, k=+1)", 1), ("H_R (XAU→US100, k=−1)", -1)):
    rho, t, n, p, tsd, rsd = perm_p(k, WIN[wl_oos])
    rr, tr, nr, ser = RES[(wl_rec, k)]; ri, ti, ni, sei = RES[(wl_is, k)]; _, _, _, seo = RES[(wl_oos, k)]
    pass_ = (abs(t) >= 2) and (np.sign(rr) == np.sign(rho)) and (abs(tr) >= 1.5) and (p < 0.025)
    verdict[lab] = "PASS（先行あり）" if pass_ else "null"
    say(f"- **{lab}**: 外 ρ {rho*100:+.3f}% (t_cl {t:+.2f}, n{n}, MDE 2se {2*seo*100:.3f}%)・週循環シフト置換 p **{p:.3f}**（帰無 ρ sd {rsd*100:.3f}%・t sd {tsd:.2f}）"
        f"／近年 ρ {rr*100:+.3f}% (t{tr:+.2f}, MDE {2*ser*100:.3f}%)／在 ρ {ri*100:+.3f}% (t{ti:+.2f}, MDE {2*sei*100:.3f}%) → **{verdict[lab]}**")
# positive controls
rho0, t0, n0, _ = RES[(wl_oos, 0)]; say(f"- 陽性対照 1: 外 同時相関 ρ(0) {rho0*100:+.2f}% (t{t0:+.1f}, n{n0})／在 {RES[(wl_is,0)][0]*100:+.2f}% (t{RES[(wl_is,0)][1]:+.1f})／近年 {RES[(wl_rec,0)][0]*100:+.2f}% (t{RES[(wl_rec,0)][1]:+.1f})")
zl = shift(P["zb"], 1); zinj = P["za"] + 0.02 * np.where(np.isfinite(zl), zl, 0.0)
rI, tI, _, _ = corr_cl(zinj, zl, P["day"], WIN[wl_oos]); say(f"- 陽性対照 2（注入 ρ≈+0.02 を外に）: ρ {rI*100:+.3f}% (t{tI:+.2f}) → 検出 {'可' if tI>=2 else '不可'}")

say("\n## 4. 経済的大きさ（記述・事前に書いた基準）")
for wl, W in WIN.items():
    m = W & P["va"] & shift(P["vb"].astype(float), 1).astype(bool)
    ru = shift(P["rb"], 1)[m]; rx = P["ra"][m]
    beta = (rx * ru).sum() / (ru * ru).sum(); sdu = ru.std(); resp = beta * sdu
    px = np.median(P["pa"][m]); hs_bp = 0.08 / px * 1e4
    # top decile |ru|
    thr = np.quantile(np.abs(ru), 0.9); big = np.abs(ru) >= thr
    y = np.sign(ru[big]) * rx[big]; d = P["day"][m][big]
    _, inv = np.unique(d, return_inverse=True); g = np.bincount(inv, weights=y); c = np.bincount(inv)
    mean_y = y.mean(); se_y = math.sqrt(((g - c * mean_y) ** 2).sum()) / len(y); t_y = mean_y / se_y
    # same for bottom-90% (small moves)
    y2 = np.sign(ru[~big]) * rx[~big]; d2 = P["day"][m][~big]; _, inv2 = np.unique(d2, return_inverse=True); g2 = np.bincount(inv2, weights=y2); c2 = np.bincount(inv2)
    m2 = y2.mean(); t2 = m2 / (math.sqrt(((g2 - c2 * m2) ** 2).sum()) / len(y2))
    say(f"- {wl}: β_raw {beta:+.4f} bp/bp・sd(r_US100) {sdu:.2f} bp → 1 sd 応答 **{resp:+.3f} bp**；上位 10% |r_US,t−1|（≥{thr:.1f} bp・n{big.sum()}）の符号つき次足 金 **{mean_y:+.3f} bp (t{t_y:+.2f})**・下位 90% {m2:+.3f} bp (t{t2:+.2f})；"
        f"金 中央値価格 {px:.0f} → 半スプレッド 0.08 USD = **{hs_bp:.2f} bp**（往復 {4*hs_bp:.2f} bp）")

say("\n## 5. セッション別（ET・記述）: NY 現物 09:30–16:00 vs 他（配信遅延なら一様・情報拡散なら現物で大）")
tmin = P["h"] * 60 + P["mn"]; cash = (tmin >= 570) & (tmin < 960)
say("| 窓 | セッション | ρ(+1) US100→XAU | ρ(−1) XAU→US100 | ρ(0) |"); say("|---|---|---|---|---|")
for wl, W in WIN.items():
    for sl, S in (("NY 現物", cash), ("他（夜間・欧州）", ~cash)):
        r1, t1, n1, _ = corr_cl(P["za"], shift(P["zb"], 1), P["day"], W & S); rm1, tm1, nm1, _ = corr_cl(P["za"], shift(P["zb"], -1), P["day"], W & S); r0, t0_, n0_, _ = corr_cl(P["za"], P["zb"], P["day"], W & S)
        say(f"| {wl} | {sl} (n{n1}) | {r1*100:+.2f}% (t{t1:+.1f}) | {rm1*100:+.2f}% (t{tm1:+.1f}) | {r0*100:+.2f}% (t{t0_:+.1f}) |")
# hourly profile of rho(+1) OOS
say("- 外 ET 時別 ρ(+1) [%]: " + " ".join(f"{hh}:{corr_cl(P['za'], shift(P['zb'],1), P['day'], WIN[wl_oos]&(P['h']==hh))[0]*100:+.1f}" for hh in range(24) if (WIN[wl_oos]&(P['h']==hh)&P['va']).sum()>1000))
say("- 外 ET 時別 ρ(−1) [%]: " + " ".join(f"{hh}:{corr_cl(P['za'], shift(P['zb'],-1), P['day'], WIN[wl_oos]&(P['h']==hh))[0]*100:+.1f}" for hh in range(24) if (WIN[wl_oos]&(P['h']==hh)&P['va']).sum()>1000))

say("\n## 6. 年別（記述）")
say("| 年 | n 対 | ρ(+1) US100→XAU | ρ(−1) XAU→US100 | ρ(0) | ρ(+2) |"); say("|---|---|---|---|---|---|")
for y in range(2012, 2027):
    W = P["yr"] == y
    r1, t1, n1, _ = corr_cl(P["za"], shift(P["zb"], 1), P["day"], W); rm, tm, _, _ = corr_cl(P["za"], shift(P["zb"], -1), P["day"], W); r0, t0_, _, _ = corr_cl(P["za"], P["zb"], P["day"], W); r2, t2_, _, _ = corr_cl(P["za"], shift(P["zb"], 2), P["day"], W)
    say(f"| {y}{'H1' if y==2026 else ''} | {n1} | {r1*100:+.2f}% (t{t1:+.1f}) | {rm*100:+.2f}% (t{tm:+.1f}) | {r0*100:+.2f}% (t{t0_:+.1f}) | {r2*100:+.2f}% (t{t2_:+.1f}) |")

say("\n## 7. 頑健性（記述）: 0.1% winsor／flat 込み（取引足のみ・stale 除外なし）")
def winz(z, q=0.001):
    w = z.copy(); f = np.isfinite(w); lo, hi = np.nanquantile(w[f], [q, 1 - q]); w[f] = np.clip(w[f], lo, hi); return w
zaw, zbw = winz(P["za"]), winz(P["zb"])
for wl in (wl_is, wl_oos, wl_rec):
    r1, t1, _, _ = corr_cl(zaw, shift(zbw, 1), P["day"], WIN[wl]); rm, tm, _, _ = corr_cl(zaw, shift(zbw, -1), P["day"], WIN[wl])
    say(f"- {wl} winsor: ρ(+1) {r1*100:+.3f}% (t{t1:+.2f})・ρ(−1) {rm*100:+.3f}% (t{tm:+.2f})")
# flat-included: standardize with flat kept
def std_keep(r, v):
    n = P["n"]; yr = P["yr"]; slot = P["slot"]; key = (yr - yr.min()) * 288 + slot; z = np.full(n, np.nan)
    s2 = np.bincount(key[v], weights=r[v] ** 2, minlength=key.max() + 1); c = np.bincount(key[v], minlength=key.max() + 1)
    sd = np.sqrt(s2 / np.maximum(c, 1))[key]; sd[~np.isfinite(sd) | (sd == 0)] = np.nan; z[v] = r[v] / sd[v]; return z
cons = np.zeros(P["n"], bool); cons[1:] = np.diff(com) == 300
vk = P["opn"] & cons & np.isfinite(P["ra"]) & np.isfinite(P["rb"])
zak = std_keep(P["ra"], vk); zbk = std_keep(P["rb"], vk)
for wl in (wl_is, wl_oos, wl_rec):
    r1, t1, n1, _ = corr_cl(zak, shift(zbk, 1), P["day"], WIN[wl]); rm, tm, _, _ = corr_cl(zak, shift(zbk, -1), P["day"], WIN[wl])
    say(f"- {wl} flat 込み (n{n1}): ρ(+1) {r1*100:+.3f}% (t{t1:+.2f})・ρ(−1) {rm*100:+.3f}% (t{tm:+.2f})")

# ---------------- replication: US500 ----------------
say("\n## 8. US500 複製（記述）")
com2, ca2, cb2 = join(tsX, cX, tsS, cS); Q = prep(com2, ca2, cb2, "US500")
WIN2 = {"在 2012-20": wins(Q["yr"], 2012, 2020), "外 2021-26H1": wins(Q["yr"], 2021, 2026), "近年 2024-26H1": wins(Q["yr"], 2024, 2026)}
say("| 窓 | ρ(+1) US500→XAU | ρ(−1) XAU→US500 | ρ(0) | ρ(+2) |"); say("|---|---|---|---|---|")
for wl, W in WIN2.items():
    r1, t1, n1, _ = corr_cl(Q["za"], shift(Q["zb"], 1), Q["day"], W); rm, tm, _, _ = corr_cl(Q["za"], shift(Q["zb"], -1), Q["day"], W); r0, t0_, _, _ = corr_cl(Q["za"], Q["zb"], Q["day"], W); r2, t2_, _, _ = corr_cl(Q["za"], shift(Q["zb"], 2), Q["day"], W)
    say(f"| {wl} (n{n1}) | {r1*100:+.2f}% (t{t1:+.1f}) | {rm*100:+.2f}% (t{tm:+.1f}) | {r0*100:+.2f}% (t{t0_:+.1f}) | {r2*100:+.2f}% (t{t2_:+.1f}) |")
# US100 vs US500 lead-lag as a vendor-latency diagnostic (same vendor, two CFD indices)
say("\n## 9. 診断: US100 ↔ US500 の先行遅行（同ベンダー 2 指数・配信遅延の指標・記述）")
com3, c3a, c3b = join(tsU, cU, tsS, cS); R3 = prep(com3, c3a, c3b, "US500")  # here 'za' = US100, 'zb' = US500
for wl, (lo, hi) in (("在 2012-20", (2012, 2020)), ("外 2021-26H1", (2021, 2026))):
    W = wins(R3["yr"], lo, hi)
    r1, t1, n1, _ = corr_cl(R3["za"], shift(R3["zb"], 1), R3["day"], W); rm, tm, _, _ = corr_cl(R3["za"], shift(R3["zb"], -1), R3["day"], W); r0, t0_, _, _ = corr_cl(R3["za"], R3["zb"], R3["day"], W)
    say(f"- {wl} (n{n1}): corr(US100_t, US500_t−1) {r1*100:+.2f}% (t{t1:+.1f})・corr(US100_t, US500_t+1) {rm*100:+.2f}% (t{tm:+.1f})・同時 {r0*100:+.1f}% (t{t0_:+.1f})")

say(f"\n## 判定\n- H_L: {verdict['H_L (US100→XAU, k=+1)']}／H_R: {verdict['H_R (XAU→US100, k=−1)']}")
say(f"\n実行 {time.time()-T0:.1f} s・seed {SEED}・入力 3 npz のみ・scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
