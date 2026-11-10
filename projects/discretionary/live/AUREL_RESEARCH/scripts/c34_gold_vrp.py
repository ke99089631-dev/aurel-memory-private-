# -*- coding: utf-8 -*-
"""
[cycle34 研究レーン 2026-11-11] 【探索・リスクプレミアム／ヘッジ需要（収益機会の源泉マップ §8 新行: ボラティリティ・リスクプレミアム）】
金のインプライド・ボラ（CBOE GVZ・GLD オプション 30 日・FRED GVZCLS・無料）は、その後 21 取引日の実現ボラ（我々の XAU M5 bid から計算）を
系統的に上回るか（＝保険需要の対価 VRP が金にも存在するか）。VRP は株式では最も頑健なリスクプレミアムの一つ（Bollerslev–Tauchen–Zhou 2009・
Carr–Wu 2009）。金は「安全資産」で上昇時にボラが上がる逆レバレッジ効果（Baur 2012）があり、コール側のヘッジ需要が売り手に対価を払う構造が
あるかは別問題。参加者: 生産者ヘッジ（コール売り・プット買い）・ETF/機関の保険買い・ディーラーのガンマ在庫。
問い:
  (H_VRP・主・構造) 金 VRP_d = GVZ_d − RV_fwd(d, +21 日) > 0 が在/外で成立するか（ボラ・ポイント・年率 %・併記 分散単位）。
  (H_PRED・副・予測) 時点 d で既知の VRP_known_d = GVZ_d − RV_trail(d, −21 日) は次 21 取引日の金リターンを予測するか（株式では β>0 の文献）。
  (陽性対照) ① US500 npz × VIX で同じ計算 → 株式 VRP は正（文献 +3〜+5 vol pt）であること（方法・整列の健全性）。
             ② GVZ は trailing RV を超えて次 21 日 RV を予測する（β>0・t≥2）＝ IV の整列が正しいこと。
  (本番への接続・ゲート ㉛) 建玉時既知の VRP_known の三分位で scan 19404 本の平均 R と超過到達率 x を在で印字し、|Δμ| <0.048R なら「決着不能・外は走らせない」。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/XAU_m5_close.npz（bid・完全格子・前値埋め）、data/macro/US500_m5_close.npz（2014+ のみ・夜間配信の衛生 ㉒）、
  data/macro/GVZCLS.csv（FRED・本サイクルで取得・2008-06-03〜）、data/macro/VIXCLS.csv（既存）、data/refute_c4_scan_paths_2010_2026.json。
  既存キャッシュ＋FRED 1 本・scan 無し・MT5 無し。読込後に min/max 時刻と flat 比率を印字（⑩⑪）。
セッション日次: セッション日 = (ET 現地 + 6h) の暦日（18:00 ET 始まり・c31 と同じ）。RV_d = Σ (Δlog close)² （flat 足は 0・週末ギャップは月曜セッションに入る）。
  有効日 = 月〜金 ∧ 非 flat 足 ≥100 本。lc_d = セッション最終足の log close。close-to-close 版 RVcc_d = (lc_d − lc_{d−1})² を併記（bid 5 分の
  マイクロストラクチャ雑音で 5 分 RV は上方バイアス → VRP は保守側）。
整列: GVZ 日付 D（NYSE 取引日・16:15 ET 確定）= セッション日 D（17:00 ET 終了）に結合。前向き窓は D のセッション終値から +21 有効日。
  RV_fwd(d) = 100·sqrt(252/21 · Σ_{j=1..21} RV_{d+j})、RV_trail(d) = 同 j=0..20。ret_fwd(d) = lc_{d+21} − lc_d（bp）。
統計: 重なり窓 → Newey–West（lag 21）t と移動ブロック bootstrap（ブロック 63 日・2000 回）se を併記。窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（日付で切る）。
判定:
  H_VRP: PASS = 在 mean(VRP)>0 ∧ NW t≥2 ∧ 外 >0 ∧ t≥1.5。負で同基準なら「金 IV は RV を下回る（逆 VRP）」。他 null（MDE=2se）。
  H_PRED: PASS = 在 β(ret_fwd on VRP_known)>0 ∧ t≥2 ∧ 外 同符号 t≥1.5。他 null。競合: GVZ 水準・RV_trail 単独の β を併記。
  陽性対照 ① US500 VRP 在 2014-20 >0 t≥2 でなければ本サイクルの RV 計算を inconclusive とする。② β(RV_fwd on GVZ | RV_trail) >0 t≥2。
  本番接続: 在 三分位（在で切る・固定）top／bottom の Δμ = mean R − mean R(全)・Welch t・Δx（pp）。|Δμ| 最大 <0.048R → ゲート ㉛「走らせない」と記録し外を印字しない。
  look-ahead 陽性対照 = x0（建玉足・㉚）の top 三分位 Δμ を同時印字。
look-ahead: GVZ_d は 16:15 ET 確定・窓は 17:00 ET 以降 → 無し。本番接続は FRED 規則（avail = (entry_JST−7h).date−1 日・asof backward・staleness ≤7 日）。
事前の最重大反証: (i) RV は Dukascopy bid 5 分（雑音↑）・GLD は米国現物時間の ETF（24h スポットと分散の定義が違う）→ close-to-close 版で符号が変わるなら inconclusive。
  (ii) 重なり窓の有効 n は日数/21（在 ≈130・外 ≈65）→ 小さい効果は MDE 以下。(iii) VRP が正でも我々はオプションを売れない（needs data/instrument）＝構造の確認であり戦略ではない。
  (iv) H_PRED は文献でも脆い（株で R² 1〜5%）。(v) 多重検定: 判定は H_VRP・H_PRED の 2 セル＋対照 2。seed 20261111。
"""
import os, time, json
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c34_gold_vrp_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261111)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle34] 金のボラティリティ・リスクプレミアム（GVZ vs 実現ボラ）と VRP の予測力 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c34_gold_vrp.py)")

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
H = 21

# ---------- session-daily builder ----------
def session_daily(npz, label, min_nf=100):
    z = np.load(os.path.join(MAC, npz))
    ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = dt_ny + pd.Timedelta(hours=6)
    S = (sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy())
    wd = dt_ny.weekday.to_numpy()
    say(f"- {label}: {len(ts)} 本 {dt_ny[0]}〜{dt_ny[-1]} ET（⑩）・flat 全体 {flat.mean()*100:.1f}%・月〜金 flat {flat[wd<=4].mean()*100:.1f}%（⑪）")
    df = pd.DataFrame({"s": S, "r2": r ** 2, "nf": (~flat).astype(np.int32), "lc": lc})
    g = df.groupby("s", sort=True)
    D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["nf"].sum(), "lc": g["lc"].last()})
    D["date"] = pd.to_datetime(D.index.astype(str), format="%Y%m%d")
    D["wd"] = D["date"].dt.weekday
    D = D[(D["wd"] <= 4) & (D["nf"] >= min_nf)].reset_index(drop=True)
    D["rcc2"] = D["lc"].diff() ** 2
    say(f"  有効セッション日 {len(D)}（月〜金 ∧ 非 flat ≥{min_nf}）・非 flat 本数 中央値 {D['nf'].median():.0f}・日次 5 分 RV 年率 中央値 {100*np.sqrt(252*D['rv'].median()):.1f}%・cc 版 {100*np.sqrt(252*D['rcc2'].median()):.1f}%")
    return D

def add_windows(D):
    n = len(D); rv = D["rv"].to_numpy(); rcc = np.nan_to_num(D["rcc2"].to_numpy()); lc = D["lc"].to_numpy()
    cs = np.concatenate([[0.0], np.cumsum(rv)]); cc = np.concatenate([[0.0], np.cumsum(rcc)])
    ann = lambda x: 100 * np.sqrt(np.maximum(252.0 / H * x, 0))
    RVf = np.full(n, np.nan); RVt = np.full(n, np.nan); RVfcc = np.full(n, np.nan); RVtcc = np.full(n, np.nan); retf = np.full(n, np.nan)
    i = np.arange(n)
    okf = i + H < n; okt = i - H + 1 >= 0
    RVf[okf] = ann(cs[i[okf] + H + 1] - cs[i[okf] + 1]); RVfcc[okf] = ann(cc[i[okf] + H + 1] - cc[i[okf] + 1])
    RVt[okt] = ann(cs[i[okt] + 1] - cs[i[okt] - H + 1]); RVtcc[okt] = ann(cc[i[okt] + 1] - cc[i[okt] - H + 1])
    retf[okf] = (lc[i[okf] + H] - lc[i[okf]]) * 1e4
    D["RVf"] = RVf; D["RVt"] = RVt; D["RVfcc"] = RVfcc; D["RVtcc"] = RVtcc; D["retf_bp"] = retf
    return D

def fred(name):
    f = pd.read_csv(os.path.join(MAC, name), na_values=".")
    f.columns = ["date", "v"]; f["date"] = pd.to_datetime(f["date"]); f = f.dropna()
    say(f"- {name}: {len(f)} 行 {f['date'].iloc[0].date()}〜{f['date'].iloc[-1].date()}・欠損除去後")
    return f

# ---------- stats ----------
def nw_mean(x, lag=H):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; n = len(x); m = x.mean(); u = x - m
    s = (u ** 2).sum() / n
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); s += 2 * w * (u[l:] * u[:-l]).sum() / n
    se = np.sqrt(s / n); return m, se, m / se, n

def block_boot_mean(x, blk=63, nb=2000):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; n = len(x); nblk = int(np.ceil(n / blk))
    starts = rng.integers(0, max(n - blk, 1), size=(nb, nblk))
    idx = (starts[:, :, None] + np.arange(blk)[None, None, :]).reshape(nb, -1)[:, :n]
    return x[idx].mean(1).std()

def nw_ols(y, X, lag=H):
    """y on [1, X...]; returns beta, se (NW), t"""
    y = np.asarray(y, float); X = np.atleast_2d(np.asarray(X, float)); X = X.T if X.shape[0] != len(y) else X
    ok = ~np.isnan(y) & ~np.isnan(X).any(1); y = y[ok]; X = X[ok]; n = len(y)
    Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    S = (Z * u[:, None]).T @ (Z * u[:, None])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv; se = np.sqrt(np.diag(V))
    r2 = 1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, se, b / se, n, r2

def win_mask(D, w):
    y0, y1 = WIN[w]; yr = D["date"].dt.year.to_numpy(); return (yr >= y0) & (yr <= y1)

# ---------- build ----------
say("\n## 0. データ")
XD = add_windows(session_daily("XAU_m5_close.npz", "XAU"))
GV = fred("GVZCLS.csv"); VX = fred("VIXCLS.csv")
XD = XD.merge(GV.rename(columns={"v": "IV"}), on="date", how="left")
say(f"- XAU セッション日 × GVZ 結合: IV あり {XD['IV'].notna().sum()}/{len(XD)}（GVZ 開始 2008-06・NYSE 休日で金が開く日は欠損）")
XD["VRP"] = XD["IV"] - XD["RVf"]; XD["VRPcc"] = XD["IV"] - XD["RVfcc"]
XD["VRPk"] = XD["IV"] - XD["RVt"]; XD["VRPkcc"] = XD["IV"] - XD["RVtcc"]
XD["VRPvar"] = (XD["IV"] ** 2 - XD["RVf"] ** 2) / 100.0   # (vol%)^2 / 100

SD = add_windows(session_daily("US500_m5_close.npz", "US500"))
SD = SD[SD["date"].dt.year >= 2014].reset_index(drop=True)   # ㉒ 夜間配信 2014+
SD = SD.merge(VX.rename(columns={"v": "IV"}), on="date", how="left")
SD["VRP"] = SD["IV"] - SD["RVf"]; SD["VRPcc"] = SD["IV"] - SD["RVfcc"]; SD["VRPk"] = SD["IV"] - SD["RVt"]
say(f"- US500（2014+）セッション日 {len(SD)}・VIX あり {SD['IV'].notna().sum()}")

# ---------- 1. H_VRP ----------
say("\n## 1. H_VRP: 金 VRP_d = GVZ_d − RV_fwd(+21 日)（vol pt・年率 %）— NW(21) t・ブロック bootstrap se・MDE=2se")
say("| 窓 | n 日 | GVZ 平均 | RV_fwd 平均 | **VRP 平均 (NW t) [MDE]** | boot se | VRP>0 の日 % | VRP cc 版 (t) | 分散単位 (IV²−RV²)/100 (t) |")
say("|---|---|---|---|---|---|---|---|---|")
resV = {}
for w in WIN:
    m = win_mask(XD, w) & XD["VRP"].notna()
    d = XD[m]
    mu, se, t, n = nw_mean(d["VRP"]); bse = block_boot_mean(d["VRP"])
    mc, sec, tc, _ = nw_mean(d["VRPcc"]); mv, sev, tv, _ = nw_mean(d["VRPvar"])
    say(f"| {w} | {n} | {d['IV'].mean():.2f} | {d['RVf'].mean():.2f} | **{mu:+.2f} ({t:+.2f}) [{2*se:.2f}]** | {bse:.2f} | {(d['VRP']>0).mean()*100:.0f}% | {mc:+.2f} ({tc:+.2f}) | {mv:+.2f} ({tv:+.2f}) |")
    resV[w] = (mu, se, t, n, mc, tc)
# 年別
rows = []
for y in range(2010, 2027):
    d = XD[(XD["date"].dt.year == y) & XD["VRP"].notna()]
    if len(d) < 40: continue
    rows.append(f"{y}: GVZ {d['IV'].mean():.1f} RVf {d['RVf'].mean():.1f} VRP {d['VRP'].mean():+.1f} (cc {d['VRPcc'].mean():+.1f}) >0 {(d['VRP']>0).mean()*100:.0f}%")
say("- 年別: " + " | ".join(rows))

say("\n### 陽性対照 ①: US500 VRP = VIX − RV_fwd（2014+）")
say("| 窓 | n 日 | VIX 平均 | RV_fwd 平均 | **VRP (NW t)** | cc 版 (t) | VRP>0 % |")
say("|---|---|---|---|---|---|---|")
ctrl = {}
for w, (y0, y1) in {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}.items():
    yr = SD["date"].dt.year.to_numpy(); m = (yr >= y0) & (yr <= y1) & SD["VRP"].notna().to_numpy()
    d = SD[m]; mu, se, t, n = nw_mean(d["VRP"]); mc, sec, tc, _ = nw_mean(d["VRPcc"])
    say(f"| {w} | {n} | {d['IV'].mean():.2f} | {d['RVf'].mean():.2f} | **{mu:+.2f} ({t:+.2f})** | {mc:+.2f} ({tc:+.2f}) | {(d['VRP']>0).mean()*100:.0f}% |")
    ctrl[w] = (mu, t)

say("\n### 陽性対照 ②: 整列（RV_fwd on GVZ ＋ RV_trail・NW t）")
for w in WIN:
    m = win_mask(XD, w) & XD["VRP"].notna() & XD["RVt"].notna(); d = XD[m]
    b, se, t, n, r2 = nw_ols(d["RVf"], np.column_stack([d["IV"], d["RVt"]]))
    b1, se1, t1, _, r21 = nw_ols(d["RVf"], d["RVt"])
    say(f"- {w} n{n}: RV_fwd = {b[0]:+.2f} + **{b[1]:+.3f}·GVZ (t {t[1]:+.2f})** + {b[2]:+.3f}·RV_trail (t {t[2]:+.2f})・R² {r2:.3f}；RV_trail 単独 β {b1[1]:+.3f} R² {r21:.3f}")

# ---------- 2. H_PRED ----------
say("\n## 2. H_PRED: 次 21 日リターン（bp）on 既知 VRP_known = GVZ − RV_trail（NW(21) t・MDE = 2se・bp/vol pt）")
say("| 窓 | n | **β VRP_known (t) [MDE]** | R² | β GVZ 水準 (t) | β RV_trail (t) | β VRP_known cc 版 (t) | 無条件 mean ret (bp・NW t) |")
say("|---|---|---|---|---|---|---|---|")
resP = {}
for w in WIN:
    m = win_mask(XD, w) & XD["VRPk"].notna() & XD["retf_bp"].notna(); d = XD[m]
    b, se, t, n, r2 = nw_ols(d["retf_bp"], d["VRPk"]); bg, seg, tg, _, _ = nw_ols(d["retf_bp"], d["IV"])
    br, ser, tr, _, _ = nw_ols(d["retf_bp"], d["RVt"]); bc, sec, tc, _, _ = nw_ols(d["retf_bp"], d["VRPkcc"])
    mu, semu, tmu, _ = nw_mean(d["retf_bp"])
    say(f"| {w} | {n} | **{b[1]:+.2f} ({t[1]:+.2f}) [{2*se[1]:.2f}]** | {r2:.4f} | {bg[1]:+.2f} ({tg[1]:+.2f}) | {br[1]:+.2f} ({tr[1]:+.2f}) | {bc[1]:+.2f} ({tc[1]:+.2f}) | {mu:+.0f} ({tmu:+.2f}) |")
    resP[w] = (b[1], se[1], t[1], n)
# quintiles (window-internal) of VRP_known → mean ret_fwd, mean RVf−RVt
say("- 五分位（窓内・VRP_known 低→高）: 平均 ret_fwd bp ／ 平均 (RV_fwd − RV_trail) vol pt")
for w in WIN:
    m = win_mask(XD, w) & XD["VRPk"].notna() & XD["retf_bp"].notna(); d = XD[m].copy()
    d["q"] = pd.qcut(d["VRPk"], 5, labels=False)
    gq = d.groupby("q").agg(ret=("retf_bp", "mean"), dv=("RVf", lambda s: np.nan), n=("retf_bp", "size"))
    dv = d.assign(dv=d["RVf"] - d["RVt"]).groupby("q")["dv"].mean()
    say(f"  - {w}: ret " + " ".join(f"{v:+.0f}" for v in gq["ret"]) + " ／ ΔRV " + " ".join(f"{v:+.1f}" for v in dv) + f"（n/五分位 {int(gq['n'].iloc[0])}）")
# US500 competitor (literature home)
say("- 比較（文献の本拠）: US500 ret_fwd on VRP_known（VIX − RV_trail）")
for w, (y0, y1) in {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026)}.items():
    yr = SD["date"].dt.year.to_numpy(); m = (yr >= y0) & (yr <= y1) & SD["VRPk"].notna().to_numpy() & SD["retf_bp"].notna().to_numpy(); d = SD[m]
    b, se, t, n, r2 = nw_ols(d["retf_bp"], d["VRPk"])
    say(f"  - {w} n{n}: β {b[1]:+.2f} bp/pt (t {t[1]:+.2f}・MDE {2*se[1]:.2f})・R² {r2:.4f}")

# ---------- 3. 本番接続（ゲート ㉛） ----------
say("\n## 3. 本番への接続（ゲート ㉛・在で印字 → |Δμ|<0.048R なら外は走らせない）")
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True); FT = J["frozen"]["FEED_TOL"]
ent_jst = pd.to_datetime(T["entry_time"], unit="s", utc=True) + pd.Timedelta(hours=9)
T["avail"] = (ent_jst - pd.Timedelta(hours=7)).dt.normalize().dt.tz_localize(None) - pd.Timedelta(days=1)
K = XD[["date", "IV", "RVt", "VRPk"]].dropna().rename(columns={"date": "kdate"}).sort_values("kdate")
T = pd.merge_asof(T.sort_values("avail"), K, left_on="avail", right_on="kdate", direction="backward", tolerance=pd.Timedelta(days=7))
T = T.sort_values("entry_time").reset_index(drop=True)
has = T["VRPk"].notna(); say(f"- scan 本 {len(T)}・VRP_known 付与 {has.sum()}（staleness 中央値 {(T['avail']-T['kdate']).dt.days.median():.0f} 日・FRED 規則 avail=(entry_JST−7h).date−1）")
dec = T["exit"].isin(["TP", "SL"]) & has
T["q"] = (1 - FT / T["risk"]) / (1 + T["b"]); T["x"] = (T["exit"] == "TP").astype(float) - T["q"]
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return (a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
ins = dec & (T["year"] >= 2010) & (T["year"] <= 2020)
cut = np.quantile(T.loc[ins, "VRPk"], [1 / 3, 2 / 3]); say(f"- 在 三分位カット（固定）: VRP_known {cut[0]:+.2f}／{cut[1]:+.2f} vol pt")
def cells(mask, w):
    d = T[mask]; top = d["VRPk"] > cut[1]; bot = d["VRPk"] <= cut[0]
    out = []
    for nm, sel in (("top", top), ("bottom", bot)):
        dmu = d.loc[sel, "R"].mean() - d["R"].mean(); tt = welch(d.loc[sel, "R"], d.loc[~sel, "R"])
        dx = (d.loc[sel, "x"].mean() - d["x"].mean()) * 100
        out.append((nm, dmu, tt, dx, int(sel.sum())))
    say(f"- {w} n{len(d)} R̄ {d['R'].mean():+.3f}: " + "；".join(f"{nm} n{n} Δμ {dmu:+.3f}R (Welch t {tt:+.2f}) Δx {dx:+.2f} pp" for nm, dmu, tt, dx, n in out))
    return max(abs(o[1]) for o in out)
gate = cells(ins, "在 2010-20")
x0top = T.loc[ins, "x0"] > np.quantile(T.loc[ins, "x0"], 2 / 3)
say(f"- look-ahead 陽性対照（㉚・在）: x0 top 三分位 Δμ {T.loc[ins & x0top.reindex(T.index, fill_value=False), 'R'].mean() - T.loc[ins, 'R'].mean():+.3f}R (Welch t {welch(T.loc[ins & x0top.reindex(T.index, fill_value=False), 'R'], T.loc[ins & ~x0top.reindex(T.index, fill_value=False), 'R']):+.2f})")
if gate >= 0.048:
    say(f"- ゲート ㉛: 在 max|Δμ| {gate:.3f}R ≥0.048 → 外を印字")
    cells(dec & (T["year"] >= 2021), "外 2021-26H1"); cells(dec & (T["year"] >= 2024), "近年 2024-26H1")
else:
    say(f"- **ゲート ㉛: 在 max|Δμ| {gate:.3f}R <0.048R → 「決着不能・走らせない」（外・近年は印字しない）**")

# ---------- 判定 ----------
say("\n## 判定（事前固定）")
vi = resV["在 2010-20"]; vo = resV["外 2021-26H1"]
passV = vi[0] > 0 and vi[2] >= 2 and vo[0] > 0 and vo[2] >= 1.5
negV = vi[0] < 0 and vi[2] <= -2 and vo[0] < 0 and vo[2] <= -1.5
ccok = np.sign(vi[4]) == np.sign(vi[0]) and np.sign(vo[4]) == np.sign(vo[0])
c_ok = ctrl["在 2014-20"][0] > 0 and ctrl["在 2014-20"][1] >= 2
say(f"- 陽性対照 ① US500 VRP 在 2014-20 {ctrl['在 2014-20'][0]:+.2f} (t {ctrl['在 2014-20'][1]:+.2f}) → {'OK' if c_ok else 'FAIL → 本サイクル inconclusive'}")
say(f"- H_VRP: 在 {vi[0]:+.2f} (t {vi[2]:+.2f})／外 {vo[0]:+.2f} (t {vo[2]:+.2f})・cc 版 同符号 {ccok} → **{('PASS（金 IV は RV を上回る＝正の VRP）' if passV else ('PASS 逆向き（IV < RV）' if negV else 'null')) if c_ok else 'inconclusive'}**{'' if ccok else '（cc 版で符号反転 → inconclusive）'}")
pi = resP["在 2010-20"]; po = resP["外 2021-26H1"]
passP = pi[0] > 0 and pi[2] >= 2 and np.sign(po[0]) == np.sign(pi[0]) and po[2] >= 1.5
say(f"- H_PRED: 在 β {pi[0]:+.2f} (t {pi[2]:+.2f})／外 {po[0]:+.2f} (t {po[2]:+.2f}) → **{'PASS' if passP else 'null'}**")
say(f"\n- 実行時間 {time.time()-T0:.1f}s・scan 無し・MT5 無し・外部通信 = FRED GVZCLS 1 本（事前取得）・seed 20261111")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
