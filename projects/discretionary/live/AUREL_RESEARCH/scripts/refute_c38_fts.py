# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-11 反証レーン] 対象: cycle38 (12:50) 安全資産需要（flight-to-safety）の残存知識
 W1 知識 (1)「外 2021-26H1 では符号が反転して金は株の極端日に同方向へ ±35〜50 bp 動く（DOWN −32 bp・UP +38 bp・t −5.47・6/6 年）
            ＝ 2021 年以降の金は株のテールをヘッジしていない（増幅している）」
 W2 同 (1)「経済的大きさは 5 分格子（0.01 bp）の 3000 倍」（c20 との比較）
 W3 年別「2014-20 は 7/7 年 正・2021-26H1 は 6/6 年 負」（符号レジーム）
 W4 研究レーン自身の最重大反証 (i)「共通の第 3 因子（実質金利・ドル）かは日次 bid 2 系列では分離できない」
H1 null・H2 null・ゲート ㉛ 不通過は争わない（自己申告どおり）。

=== 事前固定（この docstring を書いてから数字を見る）===
入力: data/macro/US500_m5_close.npz・US100_m5_close.npz・XAU_m5_close.npz（bid）・data/macro/DFII10.csv・DGS10.csv・DTWEXBGS.csv（FRED 日次）。
  既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し。seed 20261111。コスト倍は取引規則でないため該当なし。
定義は c38 と同一（取引日 = ET 平日・r_eq = ln P(16:00)−ln P(09:30)・sd60 = D を含まない直前 60 有効日・θ=1.5・金 SAME 同窓・Welch t）。
R0 再現: 主表の SAME DOWN−UP（3 窓）と NEXT DOWN−REST が c38 と ±0.1 bp で一致。sd60 の look-ahead を乱択 200 日で明示再計算して assert。

R1 線形 β 分解（主・W1 の「テール固有／増幅」の枠組み）:
  Baur–Lucey の safe haven は「極端日の条件つき関係」が「平均的な関係（hedge）」と違うかで定義される。c38 は極端日の差だけを測った。
  β_REST = REST 日（|r_eq| ≤ θ·sd60）だけで推定した金 SAME on r_eq の OLS 傾き。Δ_pred = β_REST × (r̄_eq DOWN − r̄_eq UP)。
  テール超過 E = Δ_obs − Δ_pred（日ブートストラップ 2000・窓内の日を復元抽出し β_REST と Δ_obs を同時再計算）。
  併記: ダミー回帰 g = a + β r + δ_D·1{DOWN} + δ_U·1{UP}（HC1）の δ_D − δ_U（= E の回帰版）・z = r/sd60 の 9 ビンの β（線形なら平坦）。
  判定（外 2021-26H1）: 【broken】= |E| < 0.5·|Δ_obs| ∧ |t_E| < 2（「増幅」は平均 β の言い換え・テール固有成分なし）
                       【survived】= |E| ≥ 0.5·|Δ_obs| ∧ |t_E| ≥ 2 ∧ 近年 同符号 ／ 他 inconclusive。在 2012-20 の +16.5 も同分解を印字。
R2 別銘柄（符号の再現・W1 符号）: 株を US100 に替えて同じ事象定義（US100 自身の sd60）で SAME DOWN−UP・β_REST・E を 3 窓印字。
  判定: 【survived】= 外 Δ<0 ∧ t≤−2 ／【broken】= 外 Δ≥0 または |t|<1 ／ 他 inconclusive。US500 DOWN 日と US100 DOWN 日の重なり率を印字（独立ではない）。
R3 符号の頑健性（W1・W3）: 外 で leave-one-year-out（2021..2026）・winsor 5%・Mann–Whitney z・|r_eq| 上位 5 日ずつ除外・
  独立 3 小窓 2021-22／2023-24／2025-26H1。判定: 【survived】= LOYO 全て t≤−2 ∧ MW z≤−2 ∧ winsor t≤−2 ／【broken】= LOYO のいずれか t>−1.5 ／ 他 inconclusive。
R4 共通因子（W4・記述・FRED 日次は close-to-close で夜間を含む＝同窓ではない）: 外 で g on r_eq → g on r_eq + ΔDFII10 + Δlog DTWEXBGS の β_eq 比。
  DOWN 日を ΔDFII10 の符号（上昇／低下）と Δドル の符号で分け、金 SAME の平均と t を印字。DOWN/UP/REST 日の平均 ΔDFII10・Δドル（窓別）。
R5 校正（プラセボ）: (a) 窓内ラベル置換 2000（件数保存）で Welch t を校正。
  (b) 線形帰無の parametric bootstrap: g* = a + β_REST·r_eq + e*（e* は REST 残差の復元抽出）2000 回 → Δ*_obs の t*、年別 6/6 負の頻度、E* の分布（観測 E の p）。
      「β だけで c38 の観測（t −5.5・6/6 年）が出る確率」を印字。在 2012-20（+16.5・7/7 年 2014-20）も同じ。
R6 c20 整合（W2・記述）: 同じ npz で現物時間の 5 分同時 β_5・ρ_5（窓別）を出し、日次 β_REST と比べる（リード・ラグが無ければ一致するはず）。
  c20 の「0.01 bp」は 1 本先のリード・ラグ応答で、同時相関（c20 ρ(0) 外 +15%）ではない → 「3000 倍」が単位の取り違えかを判定（記述）。
総合: W1 の「符号反転」は R2・R3 で、「テール固有／増幅」の枠組みは R1 で別々に判定。多重検定: 標的 3（R1〜R3）Bonferroni(3) 名目 |t| 2.39 併記。R4〜R6 は記述。
事前の最重大反証（自分の結論への）: (1) 線形 β の分解は「平均 β も 2021+ に反転した」ことを否定しない＝壊すのは枠組みであって符号ではない。
  (2) US100 と US500 の極端日は 7〜8 割重なる見込み → R2 は独立再現ではない。(3) FRED 日次は窓が違う（記述に留める）。(4) bid のみ・2020 夏の US500 欠落は c38 と同じ。
"""
import os, time, math, json
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c38_fts.md")
NY = "America/New_York"; SEED = 20261111; rng = np.random.default_rng(SEED)
THETA = 1.5; SD_N = 60; NBOOT = 2000; NPERM = 2000
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c38] 極端日の金×株「同方向」は線形 β の言い換えか — 別銘柄・LOYO・共通因子・線形帰無 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c38_fts.py)")

C38 = {"在 2012-20": (16.5, -5.2), "外 2021-26H1": (-70.7, 0.8), "近年 2024-26H1": (-93.9, 19.6)}
ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC・格子の穴 {(np.diff(ts)!=300).sum()}")
    return ts, cl
def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out

ts_e, cl_e = load("US500"); ts_q, cl_q = load("US100"); ts_g, cl_g = load("XAU")
dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy(); lg = np.log

def equity_series(ts, cl):
    r = (lg(price_at(ts, cl, epoch_et(dates, 16, 0))) - lg(price_at(ts, cl, epoch_et(dates, 9, 30)))) * 1e4
    valid = np.isfinite(r) & (r != 0)
    s = pd.Series(np.where(valid, r, np.nan))
    sd = s.dropna().shift(1).rolling(SD_N).std().reindex(s.index).to_numpy()
    return r, valid, sd
r_eq, valid_eq, sd60 = equity_series(ts_e, cl_e)
r_q, valid_q, sd60_q = equity_series(ts_q, cl_q)
def Pg_idx(h, m, k):
    out = np.full(N, np.nan); d2 = dates[k:]; out[:N - k] = price_at(ts_g, cl_g, epoch_et(d2, h, m)); return out
g1600 = Pg_idx(16, 0, 0); g0930 = Pg_idx(9, 30, 0); g1600n = Pg_idx(16, 0, 1)
G_SAME = (lg(g1600) - lg(g0930)) * 1e4; G_NEXT = (lg(g1600n) - lg(g1600)) * 1e4
base = valid_eq & np.isfinite(sd60); base_q = valid_q & np.isfinite(sd60_q)

# ---------- look-ahead check on sd60 ----------
idx_b = np.where(base)[0]; chk = rng.choice(idx_b[idx_b > 400], 200, replace=False); bad = 0
for i in chk:
    prev = r_eq[:i][valid_eq[:i]][-SD_N:]
    if abs(np.std(prev, ddof=1) - sd60[i]) > 1e-9: bad += 1
say(f"- sd60 look-ahead 検査: 乱択 200 日で「D より前の 60 有効日の sd」と不一致 {bad} 件（0 なら look-ahead なし）")
assert bad == 0

def grp(x, m):
    x = x[m]; x = x[np.isfinite(x) & (x != 0)]; n = len(x)
    return dict(n=n, mean=x.mean() if n else np.nan, se=x.std(ddof=1) / math.sqrt(n) if n > 1 else np.nan, x=x)
def delta(x, ma, mb):
    a, b = grp(x, ma), grp(x, mb)
    if a["n"] < 5 or b["n"] < 5: return dict(d=np.nan, se=np.nan, t=np.nan, a=a, b=b)
    se = math.sqrt(a["se"] ** 2 + b["se"] ** 2); return dict(d=a["mean"] - b["mean"], se=se, t=(a["mean"] - b["mean"]) / se, a=a, b=b)
def events(theta, m, r, sd):
    dn = m & (r < -theta * sd); up = m & (r > theta * sd); rest = m & ~dn & ~up; return dn, up, rest
def ols_hc(X, y):
    X = np.column_stack([np.ones(len(y)), X]); b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b; n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X); meat = (X * (e ** 2)[:, None]).T @ X; V = XtX_inv @ meat @ XtX_inv * n / (n - k)
    return b, V, e
def slope(r, g):
    r, g = np.asarray(r, float), np.asarray(g, float); rc = r - r.mean(); return float((rc * (g - g.mean())).sum() / (rc ** 2).sum())
def mw_z(a, b):
    x = np.r_[a, b]; rk = pd.Series(x).rank().to_numpy(); n1, n2 = len(a), len(b)
    U = rk[:n1].sum() - n1 * (n1 + 1) / 2; mu = n1 * n2 / 2; sd = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12); return (U - mu) / sd

# ---------- R0 reproduce ----------
say("\n## R0 再現（θ=1.5・主表）")
say("| 期間 | n DOWN/UP/REST | SAME DOWN−UP | c38 | NEXT DOWN−REST | c38 |"); say("|---|---|---|---|---|---|")
EV = {}
for lab, lo, hi in ERAS:
    m = base & (yr >= lo) & (yr <= hi); dn, up, rest = events(THETA, m, r_eq, sd60); EV[lab] = (m, dn, up, rest)
    a = delta(G_SAME, dn, up); b = delta(G_NEXT, dn, rest)
    say(f"| {lab} | {dn.sum()}/{up.sum()}/{rest.sum()} | {a['d']:+.1f} (t{a['t']:+.2f}) | {C38[lab][0]:+.1f} | {b['d']:+.1f} (t{b['t']:+.2f}) | {C38[lab][1]:+.1f} |")
    assert abs(a["d"] - C38[lab][0]) < 0.15 and abs(b["d"] - C38[lab][1]) < 0.15, (lab, a["d"], b["d"])
say("- R0: 3 窓とも ±0.1 bp で一致（assert 通過）")

# ---------- R1 linear-beta decomposition ----------
def decompose(g, r, sd, m, dn, up, rest, nboot=NBOOT, label=""):
    ok = m & np.isfinite(g) & (g != 0) & np.isfinite(r)
    DN, UP, RS = dn & ok, up & ok, rest & ok
    d_obs = g[DN].mean() - g[UP].mean(); se_w = math.sqrt(g[DN].var(ddof=1) / DN.sum() + g[UP].var(ddof=1) / UP.sum())
    b_rest = slope(r[RS], g[RS]); b_all = slope(r[ok], g[ok])
    dr = r[DN].mean() - r[UP].mean(); d_pred = b_rest * dr; E = d_obs - d_pred
    # bootstrap over days
    idx = np.where(ok)[0]; lab = np.where(DN, 1, np.where(UP, 2, np.where(RS, 0, -1)))
    Eb = np.empty(nboot); Db = np.empty(nboot); Bb = np.empty(nboot)
    for j in range(nboot):
        s = rng.choice(idx, len(idx), replace=True); ls = lab[s]; gs = g[s]; rs = r[s]
        a1, a2, a0 = ls == 1, ls == 2, ls == 0
        if a1.sum() < 5 or a2.sum() < 5 or a0.sum() < 30: Eb[j] = Db[j] = Bb[j] = np.nan; continue
        bb = slope(rs[a0], gs[a0]); dd = gs[a1].mean() - gs[a2].mean(); Bb[j] = bb; Db[j] = dd; Eb[j] = dd - bb * (rs[a1].mean() - rs[a2].mean())
    se_E = np.nanstd(Eb); se_B = np.nanstd(Bb)
    # dummy regression
    X = np.column_stack([r[ok], DN[ok].astype(float), UP[ok].astype(float)]); b, V, e = ols_hc(X, g[ok])
    c = np.array([0, 0, 1, -1.0]); dd_reg = float(c @ b); se_reg = math.sqrt(float(c @ V @ c))
    # bins
    z = r / sd; edges = [-np.inf, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, np.inf]; bins = []
    for lo_, hi_ in zip(edges[:-1], edges[1:]):
        mb = ok & (z >= lo_) & (z < hi_)
        if mb.sum() >= 20:
            bb_, Vb_, _ = ols_hc(r[mb][:, None], g[mb]); bins.append(f"[{lo_:+.1f},{hi_:+.1f}) n{mb.sum()} β{bb_[1]:+.3f}±{math.sqrt(Vb_[1,1]):.3f} ḡ{g[mb].mean():+.1f}")
        else: bins.append(f"[{lo_:+.1f},{hi_:+.1f}) n{mb.sum()} —")
    return dict(d_obs=d_obs, t_obs=d_obs / se_w, se_w=se_w, b_rest=b_rest, se_b=se_B, b_all=b_all, dr=dr, d_pred=d_pred, E=E, se_E=se_E,
                t_E=E / se_E if se_E > 0 else np.nan, share=d_pred / d_obs if d_obs != 0 else np.nan, dd_reg=dd_reg, se_reg=se_reg, bins=bins,
                nD=int(DN.sum()), nU=int(UP.sum()), nR=int(RS.sum()), ok=ok, DN=DN, UP=UP, RS=RS)

say("\n## R1 線形 β 分解（US500・θ=1.5・金 SAME）")
say("| 期間 | n D/U/R | Δ_obs (Welch t) | β_REST (bp/bp・boot se) | β_all | r̄_D−r̄_U | Δ_pred=β_REST·Δr | share | E=Δ_obs−Δ_pred (boot t) | δ_D−δ_U 回帰 (HC1 t) |")
say("|---|---|---|---|---|---|---|---|---|---|")
R1 = {}
for lab, lo, hi in ERAS:
    m, dn, up, rest = EV[lab]; D = decompose(G_SAME, r_eq, sd60, m, dn, up, rest); R1[lab] = D
    say(f"| {lab} | {D['nD']}/{D['nU']}/{D['nR']} | {D['d_obs']:+.1f} (t{D['t_obs']:+.2f}) | {D['b_rest']:+.4f} (±{D['se_b']:.4f}) | {D['b_all']:+.4f} | {D['dr']:+.0f} | {D['d_pred']:+.1f} | {D['share']:.2f} | **{D['E']:+.1f} (t{D['t_E']:+.2f})** | {D['dd_reg']:+.1f} (t{D['dd_reg']/D['se_reg']:+.2f}) |")
for lab, _, _ in ERAS:
    say(f"- {lab} z=r_eq/sd60 ビン別 β（線形なら平坦）: " + "・".join(R1[lab]["bins"]))
o, n_ = R1["外 2021-26H1"], R1["近年 2024-26H1"]
if abs(o["E"]) < 0.5 * abs(o["d_obs"]) and abs(o["t_E"]) < 2: v1 = "broken（外のテール超過 E は |E|<0.5|Δ_obs| ∧ |t|<2 ＝「増幅」は平均 β の言い換え）"
elif abs(o["E"]) >= 0.5 * abs(o["d_obs"]) and abs(o["t_E"]) >= 2 and np.sign(n_["E"]) == np.sign(o["E"]): v1 = "survived（テール固有成分あり）"
else: v1 = "inconclusive"
say(f"- **R1 判定: {v1}**（Bonferroni(3) 名目 |t| 2.39）")

# ---------- R2 US100 ----------
say("\n## R2 別銘柄 US100（US100 自身の sd60・金 SAME）")
say("| 期間 | n D/U/R | Δ_obs (t) | β_REST | Δ_pred | E (t) | US500-DOWN∩US100-DOWN／US500-DOWN |"); say("|---|---|---|---|---|---|---|")
R2 = {}
for lab, lo, hi in ERAS:
    mq = base_q & (yr >= lo) & (yr <= hi); dq, uq, rq = events(THETA, mq, r_q, sd60_q)
    D = decompose(G_SAME, r_q, sd60_q, mq, dq, uq, rq, nboot=500); R2[lab] = D
    d5 = EV[lab][1]; ov = (d5 & dq).sum() / max(1, d5.sum())
    say(f"| {lab} | {D['nD']}/{D['nU']}/{D['nR']} | {D['d_obs']:+.1f} (t{D['t_obs']:+.2f}) | {D['b_rest']:+.4f} | {D['d_pred']:+.1f} | {D['E']:+.1f} (t{D['t_E']:+.2f}) | {ov*100:.0f}% |")
o2 = R2["外 2021-26H1"]
v2 = "survived（外 Δ<0 ∧ t≤−2）" if (o2["d_obs"] < 0 and o2["t_obs"] <= -2) else ("broken" if (o2["d_obs"] >= 0 or abs(o2["t_obs"]) < 1) else "inconclusive")
say(f"- **R2 判定: {v2}**（重なり率が高いので独立再現ではない）")

# ---------- R3 robustness of sign (US500, 外) ----------
say("\n## R3 符号の頑健性（US500・外 2021-26H1・SAME DOWN−UP）")
m, dn, up, rest = EV["外 2021-26H1"]; ok = m & np.isfinite(G_SAME) & (G_SAME != 0)
rows = []; loyo_t = []
for y in range(2021, 2027):
    mm = ok & (yr != y); a = delta(G_SAME, dn & mm, up & mm); rows.append(f"除{y} {a['d']:+.1f} (t{a['t']:+.2f})"); loyo_t.append(a["t"])
say("- LOYO: " + "・".join(rows))
gw = G_SAME.copy(); lo_, hi_ = np.nanpercentile(G_SAME[ok], [5, 95]); gw[ok] = np.clip(G_SAME[ok], lo_, hi_)
aw = delta(gw, dn & ok, up & ok); say(f"- winsor 5%: {aw['d']:+.1f} (t{aw['t']:+.2f})")
z = mw_z(G_SAME[dn & ok], G_SAME[up & ok]); say(f"- Mann–Whitney z {z:+.2f}（中央値 DOWN {np.median(G_SAME[dn&ok]):+.1f}／UP {np.median(G_SAME[up&ok]):+.1f}）")
iD = np.where(dn & ok)[0]; iU = np.where(up & ok)[0]
dropD = iD[np.argsort(r_eq[iD])[:5]]; dropU = iU[np.argsort(-r_eq[iU])[:5]]
mk = ok.copy(); mk[dropD] = False; mk[dropU] = False; ad = delta(G_SAME, dn & mk, up & mk)
say(f"- |r_eq| 上位 5 日ずつ除外: {ad['d']:+.1f} (t{ad['t']:+.2f})（除外日 r_eq DOWN {np.round(r_eq[dropD]).astype(int).tolist()}・UP {np.round(r_eq[dropU]).astype(int).tolist()}）")
subs = []
for lab2, lo2, hi2 in [("2021-22", 2021, 2022), ("2023-24", 2023, 2024), ("2025-26H1", 2025, 2026)]:
    mm = ok & (yr >= lo2) & (yr <= hi2); a = delta(G_SAME, dn & mm, up & mm); ds, ds2 = events(THETA, base & (yr >= lo2) & (yr <= hi2), r_eq, sd60)[:2]
    D = decompose(G_SAME, r_eq, sd60, base & (yr >= lo2) & (yr <= hi2), ds, ds2, events(THETA, base & (yr >= lo2) & (yr <= hi2), r_eq, sd60)[2], nboot=500)
    subs.append(f"{lab2} Δ {a['d']:+.1f} (t{a['t']:+.2f}) β_REST {D['b_rest']:+.3f} E {D['E']:+.1f} (t{D['t_E']:+.2f})")
say("- 独立 3 小窓: " + "・".join(subs))
if all(t <= -2 for t in loyo_t) and z <= -2 and aw["t"] <= -2: v3 = "survived（LOYO 全 t≤−2 ∧ MW z≤−2 ∧ winsor t≤−2）"
elif any(t > -1.5 for t in loyo_t): v3 = "broken（LOYO のいずれかで t>−1.5）"
else: v3 = "inconclusive"
say(f"- **R3 判定: {v3}**")

# ---------- R4 common factor (descriptive) ----------
say("\n## R4 共通因子（FRED 日次・記述・close-to-close＝夜間込み・同窓ではない）")
def fred(sid, logdiff=False):
    f = pd.read_csv(os.path.join(MAC, f"{sid}.csv")); f.columns = ["d", "v"]; f["v"] = pd.to_numeric(f["v"], errors="coerce"); f = f.dropna()
    f["d"] = pd.to_datetime(f["d"]); v = f["v"].to_numpy(); dv = (np.diff(np.log(v)) * 1e4) if logdiff else np.diff(v) * 100  # bp or pp*100=bp of yield
    s = pd.Series(dv, index=f["d"].iloc[1:]); return s.reindex(dates).to_numpy()
dRR = fred("DFII10"); dNY = fred("DGS10"); dUSD = fred("DTWEXBGS", logdiff=True)
say("- 単位: ΔDFII10・ΔDGS10 = bp（利回り）・Δドル = bp（log 広義ドル）")
say("| 期間 | mean ΔDFII10 D/U/R | mean Δドル D/U/R | β_eq 単独 (HC1 t) | β_eq +実質金利+ドル (t) | 比 | β_実質金利 (t) | β_ドル (t) | R² 単独→同時 |"); say("|---|---|---|---|---|---|---|---|---|")
R4 = {}
for lab, lo, hi in ERAS:
    m, dn, up, rest = EV[lab]; ok = m & np.isfinite(G_SAME) & (G_SAME != 0) & np.isfinite(dRR) & np.isfinite(dUSD)
    b1, V1, e1 = ols_hc(r_eq[ok][:, None], G_SAME[ok]); X = np.column_stack([r_eq[ok], dRR[ok], dUSD[ok]]); b3, V3, e3 = ols_hc(X, G_SAME[ok])
    r2a = 1 - e1.var() / G_SAME[ok].var(); r2b = 1 - e3.var() / G_SAME[ok].var()
    mr = lambda v, mm: np.nanmean(v[mm & ok])
    say(f"| {lab} | {mr(dRR,dn):+.1f}/{mr(dRR,up):+.1f}/{mr(dRR,rest):+.1f} | {mr(dUSD,dn):+.1f}/{mr(dUSD,up):+.1f}/{mr(dUSD,rest):+.1f} | {b1[1]:+.4f} (t{b1[1]/math.sqrt(V1[1,1]):+.1f}) | {b3[1]:+.4f} (t{b3[1]/math.sqrt(V3[1,1]):+.1f}) | {b3[1]/b1[1]:.2f} | {b3[2]:+.2f} (t{b3[2]/math.sqrt(V3[2,2]):+.1f}) | {b3[3]:+.2f} (t{b3[3]/math.sqrt(V3[3,3]):+.1f}) | {r2a:.3f}→{r2b:.3f} |")
    R4[lab] = (b1[1], b3[1])
say("- DOWN 日の金 SAME を同日 FRED の符号で分割:")
say("| 期間 | ΔDFII10>0（実質金利↑）| ΔDFII10≤0 | 差 (t) | Δドル>0（ドル高）| Δドル≤0 | 差 (t) |"); say("|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    m, dn, up, rest = EV[lab]; ok = m & np.isfinite(G_SAME) & (G_SAME != 0) & np.isfinite(dRR) & np.isfinite(dUSD)
    a = grp(G_SAME, dn & ok & (dRR > 0)); b = grp(G_SAME, dn & ok & (dRR <= 0)); c = delta(G_SAME, dn & ok & (dRR > 0), dn & ok & (dRR <= 0))
    a2 = grp(G_SAME, dn & ok & (dUSD > 0)); b2 = grp(G_SAME, dn & ok & (dUSD <= 0)); c2 = delta(G_SAME, dn & ok & (dUSD > 0), dn & ok & (dUSD <= 0))
    tt = lambda g_: f"{g_['mean']:+.1f} (t{g_['mean']/g_['se']:+.1f}, n{g_['n']})" if g_['n'] > 1 else f"—(n{g_['n']})"
    say(f"| {lab} | {tt(a)} | {tt(b)} | {c['d']:+.1f} (t{c['t']:+.2f}) | {tt(a2)} | {tt(b2)} | {c2['d']:+.1f} (t{c2['t']:+.2f}) |")

# ---------- R5 calibration ----------
say("\n## R5 校正（プラセボ）")
for lab in ["在 2012-20", "外 2021-26H1"]:
    m, dn, up, rest = EV[lab]; D = R1[lab]; ok = D["ok"]; idx = np.where(ok)[0]
    labv = np.where(D["DN"], 1, np.where(D["UP"], 2, 0))[idx]; g = G_SAME[idx]; r = r_eq[idx]; yy = yr[idx]
    # (a) label permutation
    ts_ = np.empty(NPERM)
    for j in range(NPERM):
        p = rng.permutation(labv); a, b = g[p == 1], g[p == 2]
        ts_[j] = (a.mean() - b.mean()) / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    say(f"- {lab} (a) ラベル置換 {NPERM}: Welch t の帰無 sd {ts_.std():.2f}・|t*|≥|観測 {D['t_obs']:+.2f}| の割合 {np.mean(np.abs(ts_) >= abs(D['t_obs'])):.4f}")
    # (b) linear null parametric bootstrap
    RS = labv == 0; a0 = g[RS].mean() - D["b_rest"] * r[RS].mean(); res = g[RS] - (a0 + D["b_rest"] * r[RS])
    years = np.unique(yy); tb = np.empty(NBOOT); Eb = np.empty(NBOOT); sgn = np.empty(NBOOT); db = np.empty(NBOOT)
    for j in range(NBOOT):
        gs = a0 + D["b_rest"] * r + rng.choice(res, len(r), replace=True)
        a, b = gs[labv == 1], gs[labv == 2]; dd = a.mean() - b.mean(); db[j] = dd
        tb[j] = dd / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        bb = slope(r[RS], gs[RS]); Eb[j] = dd - bb * (r[labv == 1].mean() - r[labv == 2].mean())
        cnt = 0; tot = 0
        for y in years:
            my1 = (yy == y) & (labv == 1); my2 = (yy == y) & (labv == 2)
            if my1.sum() >= 3 and my2.sum() >= 3: tot += 1; cnt += (gs[my1].mean() - gs[my2].mean() < 0) if D["b_rest"] > 0 else (gs[my1].mean() - gs[my2].mean() > 0)
        sgn[j] = cnt == tot
    obs_years = 0; tot_y = 0
    for y in years:
        my1 = (yy == y) & (labv == 1); my2 = (yy == y) & (labv == 2)
        if my1.sum() >= 3 and my2.sum() >= 3: tot_y += 1; obs_years += (g[my1].mean() - g[my2].mean() < 0) if D["b_rest"] > 0 else (g[my1].mean() - g[my2].mean() > 0)
    say(f"- {lab} (b) 線形帰無 g*=a+β_REST·r+e*（β_REST {D['b_rest']:+.4f}）{NBOOT}: Δ* 平均 {db.mean():+.1f} bp（観測 {D['d_obs']:+.1f}）・t* 平均 {tb.mean():+.2f}（観測 {D['t_obs']:+.2f}）・"
        f"P(|t*|≥|観測|) {np.mean(np.abs(tb) >= abs(D['t_obs'])):.3f}・年別「β の向きに全年一致」の頻度 {sgn.mean():.3f}（観測 {obs_years}/{tot_y} 年）・E* sd {Eb.std():.1f}・P(|E*|≥|観測 E {D['E']:+.1f}|) {np.mean(np.abs(Eb) >= abs(D['E'])):.3f}")

# ---------- R6 5-min contemporaneous beta in cash hours (c20 consistency) ----------
say("\n## R6 c20 整合: 現物時間（09:30–16:00 ET）の 5 分同時 β_5・ρ_5 vs 日次 β_REST（記述）")
pos = np.searchsorted(ts_g, ts_e); pos = np.clip(pos, 0, len(ts_g) - 1); hit = ts_g[pos] == ts_e
te = pd.to_datetime(ts_e, unit="s", utc=True).tz_convert(NY); hh = te.hour.to_numpy() * 60 + te.minute.to_numpy(); wd = te.weekday.to_numpy(); ye = te.year.to_numpy()
cash = hit & (wd <= 4) & (hh > 9 * 60 + 30) & (hh <= 16 * 60)   # bar closing at t covers (t-5, t]; include bars closing 09:35..16:00
re5 = np.r_[np.nan, np.diff(lg(cl_e))] * 1e4; rg5 = np.r_[np.nan, np.diff(lg(cl_g[pos]))] * 1e4
say("| 期間 | n 本 | β_5 (bp/bp) | ρ_5 | 日次 β_REST | 日次 β_all | β_5/β_REST |"); say("|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    mm = cash & (ye >= lo) & (ye <= hi) & np.isfinite(re5) & np.isfinite(rg5) & ~((re5 == 0) & (rg5 == 0))
    b5 = slope(re5[mm], rg5[mm]); rho = np.corrcoef(re5[mm], rg5[mm])[0, 1]
    say(f"| {lab} | {mm.sum()} | {b5:+.4f} | {rho:+.3f} | {R1[lab]['b_rest']:+.4f} | {R1[lab]['b_all']:+.4f} | {b5/R1[lab]['b_rest']:.2f} |")
say("- 読み: 5 分同時 β を 78 本足し上げたものが日次 β（リード・ラグが無ければ一致）。c20 の「0.01 bp」は 1 本先の応答（β_raw −0.0014 bp/bp × 1 sd）で同時 β ではない。")

say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
