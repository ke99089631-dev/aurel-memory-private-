# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-06 02:20 — 対象: cycle8 (00:55) の残存反証（最重大反証に残されたもの・backlog 低優先）
  「金自身の直前 24h リターンと同向きの本（BUY∧ret>0 ∨ SELL∧ret<0）は 外 2021-26 −0.078 (t −2.90)・近年 2024-26 −0.124 (t −3.10)、
   在 2012-20 は +0.027 (t 1.22) と符号反転。『近年の金は数時間〜1 日尺度で平均回帰的で、壁→壁は反転側が走る』の構造仮説。」
  cycle8 の null そのもの（US500 4 セル FAIL・p_max 0.30）は再現して争わない。壊すのは上の残存。
  研究レーン自身が挙げた弱点: (a) 事前固定セルでない競合 2 セル×3 窓の記述、(b) 在で逆符号＝時代で符号が反転、
  (c) 入口条件づけ（補遺 D の禁止領域）、(d) 4h⊂24h で入れ子。本スクリプトは (a)(b) をコードで数え、未検査の
  「組成の差（b・risk・壁種・時間帯）」「金のトレンド漏れ」「水平線の選択効果」「少数年への集中」を追加で叩く。

読取りのみ・発注なし・scan なし・MT5 なし・外部通信なし。入力は既存キャッシュのみ
  data/c8_crossasset_features.csv（c8 特徴量・19404 本）・data/macro/{XAU,US500,US100}_m5_close.npz（c8 の M5 close）。
書き込みは data/refute_c8_goldmom.md のみ。

=== 事前固定（この docstring を書いてから数字を見る・以後動かさない） ===
記帳: cycle8 と同一（R gross・closed 全本 TIME 含む・特徴量は te=entry_time−300 の close まで＝建玉足の値は使わない）。
定義: A(H) = (BUY ∧ ret_H(XAU)>0) ∨ (SELL ∧ ret_H(XAU)<0)（同向き）。diff = mean R[A] − mean R[¬A]。cycle8 の「整合」F_A は
      リスクオフ向き（BUY∧ret<0）なので cycle8 の数字は符号が逆転して出る: cycle8 F_A diff = −diff(A)。
H0: R は A に依らない。外/近年の負は、記述された 10 セル（US500 4・US100 4・金 2）×窓 の中から事後に拾った最強セル、
    または 2021-26 の少数年・特定の組成に宿る揺れ。
Q0 再現: cycle8 §4 の 金 F_A 4h/24h × 3 窓（符号反転で一致するはず）。
Q1（主検定・family-wise）参照時刻の週循環シフト置換（cycle8 §5 と同じ機構・3 系列に同じ k・1000 回）で
      S1 = 外 2021-26 の記述 10 セル（US500 F_A/F_M×4h/24h・US100 同・金 A×4h/24h）の max|t| → p_fw10
      S2 = 外 の金 2 セルのみ max|t| → p_fw2（事前に金 2 セルだけ見ていた場合）
      S3 = 近年 2024-26 の金 2 セル max|t| → p_fw2_recent
      S4 = 金 24h の「在−外 符号反転」: diff_在 − diff_外 の |t|（相互作用）→ p_int
Q2 別分割: 年別 diff(A,24h) 2010..2026（符号と t）／外の leave-one-year-out t／重ならない窓 2021-22・2023・2024・2025-26H1／
      偶数年・奇数年／在に 2010-11 を加えた 2010-20。週クラスタ t（24h 窓の重なり）。
Q3 水平線プラセボ: H∈{1h,2h,4h,8h,12h,24h,48h,72h,120h} で diff(A,H) 外/近年（XAU npz から再計算）。
      24h だけ山なら選択効果、8h〜72h で滑らかに同符号なら構造。
Q4 競合: (i) 金のトレンド漏れ: 側別に分ける（BUY 内: ret>0 − ret<0／SELL 内: ret<0 − ret>0）。片側だけなら「上げた後の BUY が走らない」
      ＝近年の上昇トレンドでの戻り、という側の話で「平均回帰」一般ではない。無条件 BUY−SELL gap を併記。
      (ii) 大きさ: |ret| を 3 分位に分け、A の効果が |ret| 大だけに宿るか（ボラ・ストレスの話か向きの話か）。
      (iii) 連続化: 符号付き ret（side 向き）と R の Spearman ρ、符号付き ret の 5 分位の平均 R（単調か）。
Q5 組成: A と ¬A で b・risk・atr/risk・壁種・JST 帯・hold の分布差（記述）。層別（側×壁種×b 三分位×JST 帯 3）の
      層内 diff を層サイズで加重した調整 diff と t。組成で半分以上消えれば「幾何の差」。
Q6 使える形（補遺 D で禁止の入口フィルタだが数字は出す）: 「A(24h) の本を建てない」。各窓で 除外本の Σ gross R、
      残す本の平均 net R − 全本の平均 net R（s∈{0.10,0.22,0.44} USD/本・risk で R 換算）、上位10% 本の残存率。
      研究レーン基準: 在 t≥2 ∧ 外 t≥1.5 ∧ 残存 ≥90%（在は 2010-20・事前に決めた在で判定）。
判定（事前固定）:
  broken       = Q1 p_fw10 > 0.05 ∧ （Q2 外 4 分割で負が 2 以下 ∨ Q3 で 8h〜72h の隣接水平線に外 t≤−1.5 が 24h 以外に 1 つ以下
                 ∨ Q5 層別調整で |t|<1.5）∧ Q6 s=0.10 が基準 FAIL。
  survived     = Q1 p_fw10 < 0.01 ∧ Q2 外 4 分割すべて負 ∧ Q3 8h〜72h が同符号で t≤−1.5 ∧ Q5 調整 |t|≥2 ∧ Q4(i) 両側とも同符号。
  それ以外     = inconclusive。
seed 20261106。
"""
import os, math, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c8_goldmom.md")
NPERM = 1000; rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se

def cluster_t(R, g, cl):
    a = g; b = ~g
    if a.sum() < 3 or b.sum() < 3: return np.nan
    ma, mb = R[a].mean(), R[b].mean(); na, nb = a.sum(), b.sum()
    inf = pd.Series(np.where(a, (R - ma) / na, 0.0) - np.where(b, (R - mb) / nb, 0.0)).groupby(cl).sum()
    se = math.sqrt((inf ** 2).sum()); return (ma - mb) / se if se > 0 else np.nan

def asof(ts, v, q, tol):
    i = np.searchsorted(ts, q, side="right") - 1; ok = i >= 0
    out = np.full(len(q), np.nan); ii = i[ok]; age = q[ok] - ts[ii]
    out[ok] = np.where(age <= tol, v[ii], np.nan); return out

say(f"# [REFUTE c8 goldmom] 金自身の直前 24h 同向き本の負 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c8_goldmom.py)")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv"))
X["te"] = X["entry_time"] - 300
X["day"] = (X["entry_time"] + 9 * 3600) // 86400
X["week"] = (X["entry_time"] + 9 * 3600 + 3 * 86400) // (7 * 86400)
sgn = np.where(X["side"].to_numpy() == "BUY", 1.0, -1.0); X["sgn"] = sgn
S = {}
for sym in ("XAU", "US500", "US100"):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); S[sym] = (z["ts"].astype(np.int64), np.log(z["close"].astype(float)))
say(f"- 特徴量 {len(X)} 本 / M5 close: " + ", ".join(f"{k} {len(v[0])}" for k, v in S.items()) + f"（{time.time()-t0:.1f} s）")

W = {"在2012-20": (X.year >= 2012) & (X.year <= 2020), "外2021-26": X.year >= 2021, "近年2024-26": X.year >= 2024,
     "在2010-20": X.year <= 2020}
def A_mask(df, col):
    r = df[col].to_numpy(); ok = ~np.isnan(r) & (r != 0)
    return ok, (df["sgn"].to_numpy() * r) > 0

def cell(df, wm, col):
    ok, g = A_mask(df, col); m = wm.to_numpy() & ok
    R = df.loc[m, "R"].to_numpy(); gg = g[m]
    d, t, se = welch(R[gg], R[~gg]); return d, t, se, int(gg.sum()), int((~gg).sum()), m, gg

say("\n## Q0 再現（diff = 同向き − 逆向き・cycle8 F_A の符号反転に一致するはず）")
base = {}
for hn in ("4h", "24h"):
    row = []
    for wn in ("在2012-20", "外2021-26", "近年2024-26"):
        d, t, se, n1, n0, m, gg = cell(X, W[wn], f"ret{hn}_XAU"); base[(hn, wn)] = (d, t, se)
        R = X.loc[m, "R"].to_numpy()
        tcd = cluster_t(R, gg, X.loc[m, "day"].to_numpy()); tcw = cluster_t(R, gg, X.loc[m, "week"].to_numpy())
        row.append(f"{wn} n={n1}:{n0} diff {d:+.4f} t {t:+.2f} (日cl {tcd:+.2f}・週cl {tcw:+.2f})")
    say(f"- **A {hn}**: " + " / ".join(row))

# ---------------- Q1 family-wise permutation ----------------
say(f"\n## Q1 family-wise 置換（3 系列の参照時刻を同じ k 週 循環シフト・{NPERM} 回）")
HORIZ = {"4h": 4 * 3600, "24h": 24 * 3600}; FRESH = 2 * 3600; TOLP = 3 * 86400
def thresholds(sym):
    ts, v = S[sym]; grid = np.arange(ts[0] + 86400 * 2, ts[-1], 3600)
    c_now = asof(ts, v, grid, FRESH); thr = {}
    for hn, H in HORIZ.items():
        c_prev = asof(ts, v, grid - H, TOLP); r = pd.Series(np.abs(c_now - c_prev), index=grid)
        thr[hn] = (grid, r.rolling(250 * 24, min_periods=120 * 24).quantile(0.8).to_numpy())
    return thr
TH = {sym: thresholds(sym) for sym in ("US500", "US100")}
say(f"- 閾値グリッド {time.time()-t0:.1f} s")

def feats_at(q):
    """shifted lookup time q → dict of (ret, thr) per sym/horizon"""
    out = {}
    for sym in ("XAU", "US500", "US100"):
        ts, v = S[sym]; c_now = asof(ts, v, q, FRESH)
        for hn, H in HORIZ.items():
            r = c_now - asof(ts, v, q - H, TOLP); out[(sym, hn)] = r
            if sym != "XAU":
                g_, qv = TH[sym][hn]; out[(sym, hn, "thr")] = asof(g_, qv, q, 3 * 3600)
    return out

def tstat(R, ok, g):
    a = R[ok & g]; b = R[ok & ~g]
    if len(a) < 3 or len(b) < 3: return np.nan
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return (a.mean() - b.mean()) / se if se > 0 else np.nan

CELLS = [("US500", "F_A", "4h"), ("US500", "F_A", "24h"), ("US500", "F_M", "4h"), ("US500", "F_M", "24h"),
         ("US100", "F_A", "4h"), ("US100", "F_A", "24h"), ("US100", "F_M", "4h"), ("US100", "F_M", "24h"),
         ("XAU", "A", "4h"), ("XAU", "A", "24h")]
def cell_ts(F, side_sgn, R):
    out = []
    for sym, form, hn in CELLS:
        r = F[(sym, hn)]; ok = ~np.isnan(r)
        if form == "F_A": g = (side_sgn * r) < 0; ok &= (r != 0)       # risk-off alignment
        elif form == "A": g = (side_sgn * r) > 0; ok &= (r != 0)       # gold same-direction
        else: thr = F[(sym, hn, "thr")]; ok &= ~np.isnan(thr); g = np.abs(r) >= thr
        out.append(tstat(R, ok, g))
    return np.array(out)

def observed(wm):
    df = X[wm]; F = feats_at(df["te"].to_numpy()); return cell_ts(F, df["sgn"].to_numpy(), df["R"].to_numpy())
obs_o = observed(W["外2021-26"]); obs_r = observed(W["近年2024-26"]); obs_i = observed(W["在2012-20"])
say("- 観測 外 10 セル t: " + ", ".join(f"{c[0]}/{c[1]}/{c[2]} {t:+.2f}" for c, t in zip(CELLS, obs_o)))
say("- 観測 近年 金 2 セル t: " + ", ".join(f"{c[2]} {t:+.2f}" for c, t in zip(CELLS[8:], obs_r[8:])))
# interaction (在−外) for gold 24h
dI, tI, seI = base[("24h", "在2012-20")]; dO, tO, seO = base[("24h", "外2021-26")]
t_int_obs = (dI - dO) / math.sqrt(seI ** 2 + seO ** 2)
say(f"- 観測 相互作用（金 24h 在 diff − 外 diff）= {dI-dO:+.4f} t {t_int_obs:+.2f}")
S1o, S2o, S3o = np.nanmax(np.abs(obs_o)), np.nanmax(np.abs(obs_o[8:])), np.nanmax(np.abs(obs_r[8:]))

xs_lo, xs_hi = S["XAU"][0][0] + 30 * 86400, S["US500"][0][-1] - 2 * 86400
# shift domain: 2012-01-30 .. 2026-06-07 so all three series are populated
lo = max(S["US500"][0][0], S["US100"][0][0]) + 30 * 86400; hi = min(S["XAU"][0][-1], S["US500"][0][-1], S["US100"][0][-1]) - 2 * 86400
span_w = (hi - lo) // 604800
dfO = X[W["外2021-26"]]; dfR = X[W["近年2024-26"]]; dfI = X[W["在2012-20"]]
teO, sgO, RO = dfO["te"].to_numpy(), dfO["sgn"].to_numpy(), dfO["R"].to_numpy()
teR, sgR, RR = dfR["te"].to_numpy(), dfR["sgn"].to_numpy(), dfR["R"].to_numpy()
teI, sgI, RI = dfI["te"].to_numpy(), dfI["sgn"].to_numpy(), dfI["R"].to_numpy()
def gold24_diff(F, sg, R):
    r = F[("XAU", "24h")]; ok = ~np.isnan(r) & (r != 0); g = (sg * r) > 0
    return welch(R[ok & g], R[ok & ~g])
nullS1 = np.full(NPERM, np.nan); nullS2 = nullS1.copy(); nullS3 = nullS1.copy(); nullS4 = nullS1.copy(); null10 = np.full((NPERM, 10), np.nan)
tp = time.time()
for p in range(NPERM):
    k = int(rng.integers(8, span_w - 8)); sh = lambda te: lo + ((te - lo + k * 604800) % (span_w * 604800))
    FO = feats_at(sh(teO)); tO_ = cell_ts(FO, sgO, RO); null10[p] = tO_
    nullS1[p] = np.nanmax(np.abs(tO_)); nullS2[p] = np.nanmax(np.abs(tO_[8:]))
    FR = feats_at(sh(teR)); rR = FR[("XAU", "4h")]; rR24 = FR[("XAU", "24h")]
    tR4 = tstat(RR, ~np.isnan(rR) & (rR != 0), (sgR * rR) > 0); tR24 = tstat(RR, ~np.isnan(rR24) & (rR24 != 0), (sgR * rR24) > 0)
    nullS3[p] = np.nanmax(np.abs([tR4, tR24]))
    FI = feats_at(sh(teI)); dI_, _, seI_ = gold24_diff(FI, sgI, RI); dO_, _, seO_ = gold24_diff(FO, sgO, RO)
    nullS4[p] = (dI_ - dO_) / math.sqrt(seI_ ** 2 + seO_ ** 2)
    if time.time() - tp > 240: say(f"!! 置換 {p+1} 回で時間上限"); nullS1, nullS2, nullS3, nullS4, null10 = nullS1[:p+1], nullS2[:p+1], nullS3[:p+1], nullS4[:p+1], null10[:p+1]; break
p_fw10 = (nullS1 >= S1o).mean(); p_fw2 = (nullS2 >= S2o).mean(); p_fw2r = (nullS3 >= S3o).mean(); p_int = (np.abs(nullS4) >= abs(t_int_obs)).mean()
say(f"- S1 外 10 セル max|t| 観測 {S1o:.2f} → 帰無 中央値 {np.median(nullS1):.2f} / 95%点 {np.quantile(nullS1,0.95):.2f} / **p_fw10 {p_fw10:.3f}**（{len(nullS1)} 回・{time.time()-tp:.0f} s）")
say(f"- S2 外 金 2 セル max|t| 観測 {S2o:.2f} → 帰無 中央値 {np.median(nullS2):.2f} / 95%点 {np.quantile(nullS2,0.95):.2f} / **p_fw2 {p_fw2:.3f}**")
say(f"- S3 近年 金 2 セル max|t| 観測 {S3o:.2f} → 帰無 中央値 {np.median(nullS3):.2f} / 95%点 {np.quantile(nullS3,0.95):.2f} / **p_fw2_recent {p_fw2r:.3f}**")
say(f"- S4 相互作用 |t| 観測 {abs(t_int_obs):.2f} → 帰無 sd {np.nanstd(nullS4):.2f} / **p_int {p_int:.3f}**")
say("- 単セル置換 p（外）: " + ", ".join(f"{c[0]}/{c[1]}/{c[2]} {((np.abs(null10[:,j]) >= abs(obs_o[j])).mean()):.3f} (帰無sd {np.nanstd(null10[:,j]):.2f})" for j, c in enumerate(CELLS)))

# ---------------- Q2 別分割 ----------------
say("\n## Q2 別分割（A 24h・diff 同向き−逆向き）")
col = "ret24h_XAU"
yr = []
for y in range(2010, 2027):
    d, t, se, n1, n0, _, _ = cell(X, X.year == y, col); yr.append((y, d, t, n1 + n0))
say("- 年別: " + " / ".join(f"{y} {d:+.3f} (t{t:+.1f}, n{n})" for y, d, t, n in yr))
neg_oos = sum(1 for y, d, t, n in yr if y >= 2021 and d < 0); neg_is = sum(1 for y, d, t, n in yr if y <= 2020 and d < 0)
say(f"- 符号: 在 2010-20 負 {neg_is}/11・外 2021-26 負 {neg_oos}/6")
for y in range(2021, 2027):
    d, t, se, n1, n0, _, _ = cell(X, (X.year >= 2021) & (X.year != y), col); say(f"- 外 LOYO 除{y}: diff {d:+.4f} t {t:+.2f} (n{n1+n0})")
subw = {"2021-22": (X.year >= 2021) & (X.year <= 2022), "2023": X.year == 2023, "2024": X.year == 2024, "2025-26H1": X.year >= 2025}
sub = {}
for wn, wm in subw.items():
    d, t, se, n1, n0, _, _ = cell(X, wm, col); sub[wn] = (d, t); say(f"- 外 重ならない窓 {wn}: diff {d:+.4f} t {t:+.2f} (n{n1}:{n0})")
n_sub_neg = sum(1 for v in sub.values() if v[0] < 0)
for wn, wm in {"偶数年": X.year % 2 == 0, "奇数年": X.year % 2 == 1, "在2010-20": W["在2010-20"], "2010-11": X.year <= 2011,
               "2012-15": (X.year >= 2012) & (X.year <= 2015), "2016-20": (X.year >= 2016) & (X.year <= 2020)}.items():
    d, t, se, n1, n0, _, _ = cell(X, wm, col); say(f"- {wn}: diff {d:+.4f} t {t:+.2f} (n{n1}:{n0})")
for wn in ("外2021-26", "近年2024-26"):
    _, _, _, _, _, m, gg = cell(X, W[wn], col); R = X.loc[m, "R"].to_numpy()
    # top contributions: by month ΣR difference
    mon = pd.to_datetime(X.loc[m, "entry_time"], unit="s").dt.to_period("M").astype(str).to_numpy()
    dfm = pd.DataFrame({"R": R, "g": gg, "mon": mon})
    per = dfm.groupby("mon").apply(lambda q: q.R[q.g].sum() - q.R[~q.g].sum() if (q.g.sum() > 0 and (~q.g).sum() > 0) else 0.0)
    top = per.sort_values().head(3)
    say(f"- {wn} 月別 ΣR(同向き)−ΣR(逆向き) 最小 3 月: " + ", ".join(f"{k} {v:+.1f}" for k, v in top.items()) + f"（総差 {per.sum():+.1f}・月数 {len(per)}）")

# ---------------- Q3 水平線プラセボ ----------------
say("\n## Q3 水平線プラセボ（XAU npz から再計算・diff 同向き−逆向き）")
ts, v = S["XAU"]; te_all = X["te"].to_numpy(); c_now = asof(ts, v, te_all, FRESH)
HS = [("1h", 3600), ("2h", 7200), ("4h", 4 * 3600), ("8h", 8 * 3600), ("12h", 12 * 3600), ("24h", 86400), ("48h", 2 * 86400), ("72h", 3 * 86400), ("120h", 5 * 86400)]
q3 = {}
for hn, H in HS:
    r = c_now - asof(ts, v, te_all - H, TOLP + (2 * 86400 if H > 86400 else 0)); X[f"rh_{hn}"] = r
    row = []
    for wn in ("在2012-20", "外2021-26", "近年2024-26"):
        d, t, se, n1, n0, _, _ = cell(X, W[wn], f"rh_{hn}"); q3[(hn, wn)] = (d, t); row.append(f"{wn} {d:+.4f} (t{t:+.2f})")
    say(f"- H={hn}: " + " / ".join(row))
chk = abs(X["rh_24h"] - X["ret24h_XAU"]).max(); say(f"- 整合: 再計算 24h と c8 ret24h_XAU の最大差 {chk:.2e}")
nb_neg = sum(1 for hn in ("8h", "12h", "48h", "72h") if q3[(hn, "外2021-26")][1] <= -1.5)
say(f"- 外で t≤−1.5 の隣接水平線（8h/12h/48h/72h）: {nb_neg}/4")

# ---------------- Q4 競合 ----------------
say("\n## Q4 競合（A 24h）")
for wn in ("在2012-20", "外2021-26", "近年2024-26"):
    m = W[wn]; r = X[col].to_numpy(); ok = ~np.isnan(r) & (r != 0)
    B = m.to_numpy() & ok & (X.side == "BUY").to_numpy(); Sx = m.to_numpy() & ok & (X.side == "SELL").to_numpy()
    R = X["R"].to_numpy()
    dB, tB, _ = welch(R[B & (r > 0)], R[B & (r < 0)]); dS, tS, _ = welch(R[Sx & (r < 0)], R[Sx & (r > 0)])
    dU, tU, _ = welch(R[m.to_numpy() & (X.side == "BUY").to_numpy()], R[m.to_numpy() & (X.side == "SELL").to_numpy()])
    fracBuyA = ((B & (r > 0)).sum()) / max(1, (B & (r > 0)).sum() + (Sx & (r < 0)).sum())
    say(f"- {wn} (i) BUY 内 上げ後−下げ後 {dB:+.4f} (t{tB:+.2f}, n{(B&(r>0)).sum()}:{(B&(r<0)).sum()})・SELL 内 下げ後−上げ後 {dS:+.4f} (t{tS:+.2f}, n{(Sx&(r<0)).sum()}:{(Sx&(r>0)).sum()})・無条件 BUY−SELL {dU:+.4f} (t{tU:+.2f})・同向き群の BUY 比率 {fracBuyA:.2f}・ret>0 比率 {(r[m.to_numpy()&ok]>0).mean():.2f}")
    # (ii) magnitude terciles
    mm = m.to_numpy() & ok; ar = np.abs(r[mm]); qs = np.quantile(ar, [1 / 3, 2 / 3]); terc = np.digitize(ar, qs)
    g = (X["sgn"].to_numpy()[mm] * r[mm]) > 0; Rm = R[mm]; row = []
    for k in range(3):
        d, t, _ = welch(Rm[(terc == k) & g], Rm[(terc == k) & ~g]); row.append(f"T{k+1} {d:+.4f} (t{t:+.2f})")
    # (iii) continuous
    sr = X["sgn"].to_numpy()[mm] * r[mm]; rho = pd.Series(sr).corr(pd.Series(Rm), method="spearman")
    qq = np.quantile(sr, [0.2, 0.4, 0.6, 0.8]); dec = np.digitize(sr, qq)
    say(f"- {wn} (ii) |ret| 三分位の A 効果: " + " / ".join(row) + f"｜(iii) Spearman ρ(符号付き ret, R) {rho:+.4f}・符号付き ret 5 分位の平均R: " + " ".join(f"Q{k+1} {Rm[dec==k].mean():+.3f}" for k in range(5)))

# ---------------- Q5 組成 ----------------
say("\n## Q5 組成と層別調整（A 24h）")
X["jb"] = pd.cut(X["jh"], [-1, 6, 12, 20, 24], labels=["21-6", "7-12", "13-20", "21-6b"]).astype(str).replace({"21-6b": "21-6"})
adj = {}
for wn in ("在2012-20", "外2021-26", "近年2024-26"):
    _, _, _, _, _, m, gg = cell(X, W[wn], col); df = X[m].copy(); df["A"] = gg
    desc = []
    for c in ("b", "risk", "hold"):
        desc.append(f"{c} 中央値 A {df.loc[df.A, c].median():.2f} / ¬A {df.loc[~df.A, c].median():.2f}")
    desc.append(f"atr/risk 中央値 A {(df.atr/df.risk)[df.A].median():.2f} / ¬A {(df.atr/df.risk)[~df.A].median():.2f}")
    desc.append(f"outer 比率 A {(df.wall_kind[df.A]=='outer').mean():.2f} / ¬A {(df.wall_kind[~df.A]=='outer').mean():.2f}")
    desc.append(f"JST7-12 比率 A {(df.jb[df.A]=='7-12').mean():.2f} / ¬A {(df.jb[~df.A]=='7-12').mean():.2f}")
    desc.append(f"TP率 A {(df.exit[df.A]=='TP').mean():.3f} / ¬A {(df.exit[~df.A]=='TP').mean():.3f}")
    say(f"- {wn}: " + "・".join(desc))
    df["bt"] = pd.qcut(df["b"], 3, labels=False, duplicates="drop")
    num = 0.0; var = 0.0; nused = 0
    for key, q in df.groupby(["side", "wall_kind", "bt", "jb"]):
        a = q.R[q.A].to_numpy(); bb = q.R[~q.A].to_numpy()
        if len(a) < 3 or len(bb) < 3: continue
        w = len(q); d = a.mean() - bb.mean(); se2 = a.var(ddof=1) / len(a) + bb.var(ddof=1) / len(bb)
        num += w * d; var += (w ** 2) * se2; nused += w
    d_adj = num / nused; t_adj = d_adj / math.sqrt(var) * nused; adj[wn] = (d_adj, t_adj)
    say(f"  → 層別調整 diff {d_adj:+.4f} t {t_adj:+.2f}（使用 {nused} 本）・生 diff {base[('24h', wn)][0]:+.4f}")

# ---------------- Q6 使える形 ----------------
say("\n## Q6 使える形（入口フィルタ『A(24h) を建てない』・補遺 D 禁止領域・数字のみ）")
res6 = {}
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    _, _, _, _, _, m, gg = cell(X, W[wn], col); df = X[m]; R = df.R.to_numpy(); risk = df.risk.to_numpy()
    top = R >= np.quantile(R, 0.9); keep_top = (~gg)[top].mean()
    row = [f"除外 {gg.sum()} 本 ΣgrossR {R[gg].sum():+.1f}（残す {(~gg).sum()} 本 ΣgrossR {R[~gg].sum():+.1f}）・上位10% 残存 {keep_top*100:.0f}%"]
    for s in (0.10, 0.22, 0.44):
        net = R - s / risk; d, t, _ = welch(net[~gg], net[gg])
        row.append(f"s={s}: 残す−除外 {d:+.4f} (t{t:+.2f})・残す平均 {net[~gg].mean():+.4f} vs 全本 {net.mean():+.4f}")
        if s == 0.10: res6[wn] = (d, t, keep_top)
    say(f"- {wn}: " + " / ".join(row))
pass6 = (res6["在2010-20"][1] >= 2.0) and (res6["外2021-26"][1] >= 1.5) and (res6["在2010-20"][2] >= 0.9) and (res6["外2021-26"][2] >= 0.9)
say(f"- 研究レーン基準（在2010-20 t≥2 ∧ 外 t≥1.5 ∧ 残存≥90%）: {'PASS' if pass6 else 'FAIL'}")

# ---------------- verdict ----------------
say("\n## 判定（事前固定）")
adj_t = adj["外2021-26"][1]
both_sides = None
cond_broken = (p_fw10 > 0.05) and ((n_sub_neg <= 2) or (nb_neg <= 1) or (abs(adj_t) < 1.5)) and (not pass6)
cond_surv = (p_fw10 < 0.01) and (n_sub_neg == 4) and (nb_neg == 4) and (abs(adj_t) >= 2)
verdict = "broken" if cond_broken else ("survived" if cond_surv else "inconclusive")
say(f"- p_fw10 {p_fw10:.3f} / 外 4 分割 負 {n_sub_neg}/4 / 隣接水平線 t≤−1.5 {nb_neg}/4 / 層別調整 外 t {adj_t:+.2f} / Q6 {'PASS' if pass6 else 'FAIL'}")
say(f"\n**VERDICT: {verdict}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
