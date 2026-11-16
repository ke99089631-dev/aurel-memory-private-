# -*- coding: utf-8 -*-
"""
[cycle41 研究レーン 2026-11-16] 【探索・ボラティリティの非対称（レバレッジ効果と金の“逆レバレッジ”）】
株式には「下げた翌日はボラが上がる」（Black 1976・Christie 1982 のレバレッジ効果／ボラ・フィードバック）。
金は逆（Baur 2012 "Asymmetric volatility in the gold market": 上昇ショックの方がボラを上げる＝安全資産需要の流入時に
価格とボラが同時に上がる）と報告されている。我々は c38 で「2021+ の金は株の極端日に株と同方向（ヘッジでなく増幅）」を得た
→ AI らしい角度 = c38 から**予測を導いて別の統計で検証**: 金が 2021+ で“リスク資産の顔”をしているなら、ボラ非対称の符号も
株式型（負）へ動くはず（H_FLIP）。文献型（逆レバレッジ・正）が在外で続くなら H_INV。方法論 ㉝: 本拠（US500）で先に
レバレッジ効果（負）が見えることを方法の陽性対照にする。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/XAU_m5_close.npz・US500_m5_close.npz（bid・暦時刻完全格子・前値埋め）。既存キャッシュのみ・scan 無し・M5 読込なし・
  MT5 無し・外部通信無し。
セッション日 d = (ET+6h) の暦日（18:00 ET 始まり・c31/c36/c37 と同じ）。有効日 = 月〜金 ∧ 非 flat 足 ≥100（⑪）。
  r_d = ln(当日最終取引足 close) − ln(前有効日の最終取引足 close)・bp。RV_d = Σ(Δln close)² over 当日の非 flat 足（log を取る）。
  brk_{d+1} = 翌有効日が暦で 2 日以上先（週末・祝日を跨ぐ）フラグ。US500 は夜間配信が 2014 年から（㉒）→ 在 = 2014-20。
窓（D2・セッション日 d の年）: 在 2010-20（US500 2014-20）／外 2021-26H1／近年 2024-26H1。
主回帰（予測型・翌日）: log RV_{d+1} = α + φ1·log RV_d + φ5·mean(log RV_{d−4..d}) + β·|r_d| + γ·r_d + ε。
  γ = 非対称係数（/bp）。NW(5) t・HC1 t・MDE = 2·se(NW)。帰無 = r_d の**符号反転置換**（|r_d| と日の対応を保存・2000 回・両側 p・㊷）。
  記述: γ_c（同日: log RV_d on r_d, |r_d|, log RV_{d−1}, mean log RV_{d−5..d−1}＝Baur の対象に近い）・年別 γ（HC1 t）・
  r_d 五分位ごとの残差 log RV_{d+1} プロファイル（ニュース・インパクト曲線）・頑健版 = brk 除外／NFP（c24 暦・d または d+1）除外。
判定（Bonferroni(2)・名目 0.025）:
  C1 US500（本拠・方法の陽性対照）: PASS = 在 γ<0 ∧ NW t≤−2 ∧ 置換 p<0.025。C1 が立たなければ「この格子では方法がレバレッジ効果を
    見ない」＝ C2 は記述のみ（㉝）。
  C2 XAU: H_INV（文献・逆レバレッジ）PASS = 在 γ>0 ∧ t≥2 ∧ p<0.025 ∧ 外 γ>0 ∧ t≥1.5。
          H_FLIP（c38 由来の予測）PASS = 在 γ>0 ∧ t≥2 ∧ p<0.025 ∧ 外 γ<0 ∧ t≤−1.5。
          どちらでもなければ null（在/外の MDE を併記）。
決着可能性（㉝・事前）: 「±1 sd の日で翌日 RV が 10% 違う」= γ* = 0.10/(2·sd_r)。se を iid 近似 sd_ε/(sd_r·√n)（sd_ε≈0.5）で見積もると
  在 n≈2700 で t* ≈ 0.05/0.5·√2700 ≈ 5 → 決着可能。HC1/NW で se が 1.5〜2 倍でも t* ≥2.5。実測 se も印字する。
陽性対照（注入）: 在の y に γ*·r_d を注入して t を印字。
ゲート ㉛（本番接続・在のみ）: scan 19404 本の建玉セッション日の**前有効日** r_d の符号で UP／DOWN に分け Δμ(R*)（R*=R+ft·1{SL,TP}）・
  Welch t・Δx（pp）・x0 look-ahead 対照。在 |Δμ|<0.048R → 「決着不能・外は走らせない」。記述: 翌日の壁幅 log risk_bp の UP−DOWN 差。
事前の最重大反証: (1) bid のみ・Dukascopy 1 社（気配縮小のボラは bid で過大）。(2) RV は 5 分 bid で雑音上方バイアス（c34）→ log で比を
  見るので中立。(3) 週末・祝日跨ぎは r_d と RV_{d+1} の両方を歪める → brk 除外版を併記。(4) 発表日（NFP）が r_d と RV_{d+1} を同時に
  動かす → NFP 除外版。(5) 2020 夏の US500 欠落 68 日（㊵）→ 欠落営業日の年別件数を印字。(6) γ は |r| と RV ラグを統制した「符号の
  追加情報」であり Baur の GARCH 係数と単位が違う（符号と有無だけを比べる）。(7) 外の金は 2024-26 の急騰（上げ日が多い）で r_d の
  分布が非対称 → 五分位プロファイルで形を見る。
昇格候補・入口/出口規則の提案ではない（市場構造の記述・§8 源泉マップに行を 1 つ足す）。seed 20261116。
"""
import os, time, json, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c41_asymmetric_volatility_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261116)
NFMIN = 100; NPERM = 2000; NWLAG = 5
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle41] ボラティリティの非対称（レバレッジ効果 vs 金の逆レバレッジ・c38 由来の反転予測） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c41_asymmetric_volatility.py)")

# ---------- NFP calendar (c24 nfp_dates_v2) ----------
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
NFP = {d.date().toordinal() for d in nfp_dates_v2()}

# ---------- stats ----------
def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.asarray(X, float)
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    V_hc = XtX_inv @ Sm @ XtX_inv * n / (n - Z.shape[1])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv
    r2 = 1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, np.sqrt(np.diag(V)), np.sqrt(np.diag(V_hc)), u, r2
def ols_last(y, Z):
    b, *_ = np.linalg.lstsq(Z, y, rcond=None); return b[-1]
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return diff, diff / se

# ---------- session daily table ----------
def daily_table(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    say(f"- {sym}: npz {len(ts)} 本 {pd.to_datetime(ts[0], unit='s').date()}〜{pd.to_datetime(ts[-1], unit='s').date()} UTC・flat 全体 {flat.mean()*100:.1f}%（⑪）")
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep], "r2": r[keep] ** 2})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index])
    D["wd"] = D["date"].dt.weekday
    allbd = D[D.wd <= 4]
    D = D[(D.wd <= 4) & (D.nf >= NFMIN)].reset_index()
    # missing business days (㊵): weekdays with no session row at all, per year
    o_all = set(D["o"].tolist()); bd_grid = pd.bdate_range(D.date.min(), D.date.max())
    miss = [d for d in bd_grid if d.toordinal() not in set(allbd.index.tolist())]
    my = pd.Series([d.year for d in miss]).value_counts().sort_index()
    say(f"- {sym}: 有効セッション日 {len(D)}（月〜金 ∧ nf≥{NFMIN}；平日で nf<{NFMIN} は {len(allbd)-len(D)} 日）・平日で足が無い日 {len(miss)}（年別: " + ", ".join(f"{y} {c}" for y, c in my.items()) + "）")
    D["lrv"] = np.log(D["rv"]); D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["gap"] = np.r_[np.nan, np.diff(D["o"].to_numpy())]
    D["lrv5"] = D["lrv"].rolling(5).mean()
    D["year"] = D["date"].dt.year
    D["nfp"] = D["o"].isin(NFP)
    return D

def build_xy(D):
    """row t (day d) -> y = lrv[t+1]; x = lrv[t], lrv5[t], |r[t]|, r[t]; brk = gap[t+1]>1 ; nfp either day."""
    n = len(D)
    y = D["lrv"].to_numpy()[1:]; lrv = D["lrv"].to_numpy()[:-1]; lrv5 = D["lrv5"].to_numpy()[:-1]
    r = D["r"].to_numpy()[:-1]; brk = D["gap"].to_numpy()[1:] > 1
    nfp = D["nfp"].to_numpy()[1:] | D["nfp"].to_numpy()[:-1]
    year = D["year"].to_numpy()[:-1]
    ok = np.isfinite(y) & np.isfinite(lrv) & np.isfinite(lrv5) & np.isfinite(r)
    return pd.DataFrame({"y": y, "lrv": lrv, "lrv5": lrv5, "ar": np.abs(r), "r": r, "brk": brk, "nfp": nfp, "year": year})[ok].reset_index(drop=True)

def fit_gamma(v, perm=True):
    X = np.column_stack([v.lrv, v.lrv5, v.ar, v.r]); y = v.y.to_numpy()
    b, se, se_hc, u, r2 = nw_ols(y, X)
    g = b[4]; t_nw = g / se[4]; t_hc = g / se_hc[4]
    p = np.nan
    if perm:
        Z = np.column_stack([np.ones(len(y)), X]); gp = np.empty(NPERM)
        for k in range(NPERM):
            Z[:, 4] = v.r.to_numpy() * rng.choice([-1.0, 1.0], size=len(y)); gp[k] = ols_last(y, Z)
        p = float((np.abs(gp) >= abs(g)).mean())
    return dict(g=g, se=se[4], se_all=se, t=t_nw, t_hc=t_hc, p=p, n=len(y), r2=r2, b=b, u=u, sd_r=float(v.r.std()), sd_u=float(u.std()))

WIN = {"XAU": {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)},
       "US500": {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}}
RES = {}; DAILY = {}
for sym in ("XAU", "US500"):
    D = daily_table(sym); DAILY[sym] = D; V = build_xy(D)
    say(f"- {sym}: 回帰行 {len(V)}・brk 行 {int(V.brk.sum())}（{V.brk.mean()*100:.0f}%）・NFP 隣接行 {int(V.nfp.sum())}・r_d sd {V.r.std():.0f} bp・log RV sd {V.y.std():.2f}")
    RES[sym] = {}
    say(f"## {sym}: 主回帰 log RV_(d+1) = α + φ1 log RV_d + φ5 mean log RV_(d−4..d) + β|r_d| + γ r_d")
    say("| 窓 | n | γ (/bp ×1e4) | NW t | HC1 t | 置換 p（両側） | MDE(2se) ×1e4 | 2sd_r·γ（±1sd 日の log RV 差） | β \\|r\\| ×1e4 (t) | φ1 (t) | R² | brk 除外 γ (t) | NFP 除外 γ (t) | 同日 γ_c ×1e4 (t) |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for wn, (y0, y1) in WIN[sym].items():
        v = V[(V.year >= y0) & (V.year <= y1)].reset_index(drop=True)
        f = fit_gamma(v)
        f_b = fit_gamma(v[~v.brk].reset_index(drop=True), perm=False)
        f_n = fit_gamma(v[~v.nfp].reset_index(drop=True), perm=False)
        # contemporaneous (Baur-like): lrv[t] on r[t], |r[t]|, lrv[t-1], lrv5[t-1]  -> shift
        vc = pd.DataFrame({"y": v.lrv.to_numpy()[1:], "lrv": v.lrv.to_numpy()[:-1], "lrv5": v.lrv5.to_numpy()[:-1], "ar": v.ar.to_numpy()[1:], "r": v.r.to_numpy()[1:]})
        f_c = fit_gamma(vc, perm=False)
        f["brk"] = f_b; f["nfp"] = f_n; f["c"] = f_c
        RES[sym][wn] = f
        say(f"| {wn} | {f['n']} | **{f['g']*1e4:+.3f}** | **{f['t']:+.2f}** | {f['t_hc']:+.2f} | {f['p']:.4f} | {2*f['se']*1e4:.3f} | {2*f['sd_r']*f['g']:+.3f} | {f['b'][3]*1e4:+.3f} ({f['b'][3]/f['se_all'][3]:+.1f}) | {f['b'][1]:+.3f} | {f['r2']:.3f} | {f_b['g']*1e4:+.3f} ({f_b['t']:+.2f}) | {f_n['g']*1e4:+.3f} ({f_n['t']:+.2f}) | {f_c['g']*1e4:+.3f} ({f_c['t']:+.2f}) |")
    # decidability + injection (在)
    wn0 = list(WIN[sym])[0]; f0 = RES[sym][wn0]
    gstar = 0.10 / (2 * f0["sd_r"]); t_iid = gstar * f0["sd_r"] * math.sqrt(f0["n"]) / 0.5
    v0 = V[(V.year >= WIN[sym][wn0][0]) & (V.year <= WIN[sym][wn0][1])].reset_index(drop=True)
    vi = v0.copy(); vi["y"] = vi.y + gstar * vi.r; fi = fit_gamma(vi, perm=False)
    say(f"- 決着可能性（㉝・事前式）: γ* = 0.10/(2·sd_r) = {gstar*1e4:.3f} ×1e-4/bp・iid 近似 t* {t_iid:.1f}・実測 se(NW) で t* {gstar/f0['se']:.1f}；陽性対照 在に γ* 注入 → γ {fi['g']*1e4:+.3f} (NW t {fi['t']:+.2f})（実測 {f0['t']:+.2f} から）")
    # news impact profile (在・外): residual y after lrv, lrv5, |r| by r quintile
    say(f"- ニュース・インパクト（r_d 五分位 → 残差 log RV_(d+1)・|r| と RV ラグ統制後・mean ± se）:")
    for wn, (y0, y1) in list(WIN[sym].items())[:2]:
        v = V[(V.year >= y0) & (V.year <= y1)].reset_index(drop=True)
        b, se, se_hc, u, r2 = nw_ols(v.y.to_numpy(), np.column_stack([v.lrv, v.lrv5, v.ar]))
        qs = pd.qcut(v.r, 5, labels=False)
        prof = [(f"Q{q+1} r̄ {v.r[qs==q].mean():+.0f}bp: {u[qs==q].mean():+.3f}±{u[qs==q].std()/math.sqrt((qs==q).sum()):.3f}") for q in range(5)]
        say(f"  - {wn}: " + " ・ ".join(prof))
    # yearly gamma (HC1 t)
    rows = []
    for yy in sorted(V.year.unique()):
        v = V[V.year == yy].reset_index(drop=True)
        if len(v) < 100: continue
        b, se, se_hc, u, r2 = nw_ols(v.y.to_numpy(), np.column_stack([v.lrv, v.lrv5, v.ar, v.r]))
        rows.append(f"{yy} {b[4]*1e4:+.2f} ({b[4]/se_hc[4]:+.1f})")
    say(f"- 年別 γ ×1e4 (HC1 t): " + "・".join(rows))
    say()

# ---------- judgment ----------
say("## 判定（事前固定・Bonferroni(2)・名目 0.025）")
a = RES["US500"]["在 2014-20"]; b_ = RES["US500"]["外 2021-26H1"]
C1 = (a["g"] < 0) and (a["t"] <= -2) and (a["p"] < 0.025)
say(f"- C1 US500（本拠・レバレッジ効果 γ<0）: 在 γ {a['g']*1e4:+.3f} (NW t {a['t']:+.2f}・p {a['p']:.4f})／外 {b_['g']*1e4:+.3f} (t {b_['t']:+.2f}・p {b_['p']:.4f}) → **{'PASS（方法はレバレッジ効果を見る）' if C1 else 'FAIL（この格子では見えない → C2 は記述のみ）'}**")
x = RES["XAU"]["在 2010-20"]; o = RES["XAU"]["外 2021-26H1"]; nr = RES["XAU"]["近年 2024-26H1"]
inv = (x["g"] > 0) and (x["t"] >= 2) and (x["p"] < 0.025) and (o["g"] > 0) and (o["t"] >= 1.5)
flip = (x["g"] > 0) and (x["t"] >= 2) and (x["p"] < 0.025) and (o["g"] < 0) and (o["t"] <= -1.5)
vd = "H_INV PASS（逆レバレッジが在外で続く）" if inv else "H_FLIP PASS（在 正 → 外 負＝c38 の予測）" if flip else "null（どちらも立たない）"
say(f"- C2 XAU: 在 γ {x['g']*1e4:+.3f} (NW t {x['t']:+.2f}・HC1 {x['t_hc']:+.2f}・p {x['p']:.4f}・MDE {2*x['se']*1e4:.3f})／外 {o['g']*1e4:+.3f} (t {o['t']:+.2f}・p {o['p']:.4f}・MDE {2*o['se']*1e4:.3f})／近年 {nr['g']*1e4:+.3f} (t {nr['t']:+.2f}) → **{vd}**" + ("" if C1 else "（C1 FAIL のため記述扱い）"))
say()

# ---------- gate ㉛ ----------
say("## ゲート ㉛（本番接続・在のみ印字）: 建玉セッション日の前有効日 r_d の符号（UP/DOWN）で scan 本を分ける")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; tr = pd.DataFrame(d["trades"])
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = (tr["exit"] == "TP").astype(float) - tr["q"]
e_ny = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(NY)
tr["so"] = ((e_ny + pd.Timedelta(hours=6)).dt.tz_localize(None).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal())
DX = DAILY["XAU"]; ords = DX["o"].to_numpy(); rr = DX["r"].to_numpy()
pos = np.searchsorted(ords, tr["so"].to_numpy(), side="left") - 1  # last valid day strictly before entry session
okp = pos >= 0
tr["r_prev"] = np.where(okp, rr[np.clip(pos, 0, len(rr) - 1)], np.nan)
tr["stale"] = np.where(okp, tr["so"].to_numpy() - ords[np.clip(pos, 0, len(ords) - 1)], np.nan)
# entry price for risk_bp (descriptive)
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
et = tr["entry_time"].to_numpy(np.int64) - 300; pp = np.clip(np.searchsorted(ts, et), 0, len(ts) - 1); tr["P"] = C[pp]
tr["lrisk_bp"] = np.log(tr["risk"] / tr["P"] * 1e4)
ins = tr[(tr.year <= 2020) & tr.r_prev.notna()]
say(f"- 付与 {int(tr.r_prev.notna().sum())}/{len(tr)}・前有効日までの暦日差 中央値 {np.nanmedian(tr.stale):.0f}（max {np.nanmax(tr.stale):.0f}）・在 n {len(ins)}（UP {int((ins.r_prev>0).sum())}／DOWN {int((ins.r_prev<0).sum())}）")
up = ins[ins.r_prev > 0]; dn = ins[ins.r_prev < 0]
dmu, tmu = welch(up.Rs, dn.Rs); dx = 100 * (up[up.dec].x.mean() - dn[dn.dec].x.mean())
dg, tg = welch(up.lrisk_bp, dn.lrisk_bp)
x0cut = ins.x0.quantile(2 / 3); d0, t0_ = welch(ins[ins.x0 > x0cut].Rs, ins[ins.x0 <= x0cut].Rs)
say(f"- 在 UP−DOWN: Δμ **{dmu:+.3f}R (t {tmu:+.2f})**・Δx {dx:+.2f} pp・翌日壁幅 Δ log risk_bp {dg:+.3f} (t {tg:+.1f})；look-ahead 対照 x0 top Δμ {d0:+.3f}R (t {t0_:+.1f})")
say(f"- ゲート ㉛: 在 |Δμ| {abs(dmu):.3f}R {'<' if abs(dmu) < 0.048 else '≥'} 0.048R → **{'決着不能・外は走らせない' if abs(dmu) < 0.048 else '外を印字'}**")
if abs(dmu) >= 0.048:
    oos = tr[(tr.year >= 2021) & tr.r_prev.notna()]
    dmo, tmo = welch(oos[oos.r_prev > 0].Rs, oos[oos.r_prev < 0].Rs); say(f"  外 UP−DOWN Δμ {dmo:+.3f}R (t {tmo:+.2f})")
# descriptive: next-day geometry/hazard by prior sign in 外 (記述のみ)
oos = tr[(tr.year >= 2021) & tr.r_prev.notna()]
dg2, tg2 = welch(oos[oos.r_prev > 0].lrisk_bp, oos[oos.r_prev < 0].lrisk_bp)
say(f"- 記述（外）: 翌日壁幅 Δ log risk_bp UP−DOWN {dg2:+.3f} (t {tg2:+.1f})・hold 中央値 UP {oos[oos.r_prev>0].hold.median():.0f}／DOWN {oos[oos.r_prev<0].hold.median():.0f} 本")
say()
say(f"所要 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
