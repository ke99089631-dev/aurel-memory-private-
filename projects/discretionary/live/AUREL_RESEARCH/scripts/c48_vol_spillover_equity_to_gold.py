# -*- coding: utf-8 -*-
"""
[cycle48 研究レーン 2026-11-18] 【探索・市場間連動（ボラティリティ次元）／情報伝播の遅れ — §8 新行「ボラの伝播（株→金）」】
c20 は 5 分格子の**リターン**の先行遅行を null で閉じた（|ρ|≤0.3%）。未検定の次元 = **ボラティリティの伝播**（Diebold–Yilmaz 2009/2012:
株式ボラは他資産への net transmitter／Engle–Ito–Lin 1990 meteor shower）。問い: **当日の米株（US500 現物時間）実現ボラは、金自身の
ボラ履歴と金オプション市場の IV（GVZ）を統制した後でも、翌セッションの金の実現ボラを予測するか。** 予測するなら「金オプション市場
（GLD・GVZ）は株ボラのショックを当日中に織り込まない」＝構造的な価格付けの遅れ（受け取るにはオプション＝【要取得／要インスト】）。
しないなら「市場横断の情報伝播はボラ次元でも 1 日格子に無い」で c20 と並べて系統を閉じる。
AI らしい角度: 「予測力」でなく「**IV を超える予測力**」を問う（IV は市場参加者の最良予測の代理 → それを超える分だけが“未織込み”）。
方法論 ㉝: 文献の本拠は株式（受け手）ではなく「株 → 他資産」なので、本拠対照 = **逆方向**（金ボラ → 翌日米株ボラ | VIX）を同仕様で印字し
「株が送り手・金が受け手」の非対称が出るかを見る（対称に出るなら共通因子の疑い）。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/XAU_m5_close.npz・US500_m5_close.npz（bid・暦時刻完全格子・前値埋め）、GVZCLS.csv・VIXCLS.csv（FRED・既取得）、
  FOMC_dates.csv（scheduled のみ）・CPI_dates.csv・NFP 規則（c24 v2）。scan 接続のみ refute_c4_scan_paths_2010_2026.json。
  既存キャッシュのみ・多年 scan 無し・M5 読込なし・MT5 無し・外部通信無し。
金 セッション日 d = (ET+6h) 暦日（18:00 ET d−1 → 17:00 ET d・c31/c41 と同じ）・有効 = 月〜金 ∧ 非 flat ≥100。RV^X_d = Σ(Δln close)²（非 flat）。
米株 = **US500 現物時間 RV^S_d**（ET 09:30–16:00 の足 78 本・非 flat ≥60・暦日 d・16:00 ET 確定）。GVZ_d（16:15 ET 確定）・VIX_d。
  → 予測子は全部 17:00 ET d までに既知、被説明変数は 18:00 ET d 以降のセッション d+1 ＝ look-ahead なし。
  US500 現物 RV は 2012 年から（夜間配信 2014+ の衛生 ㉒ は現物時間に無関係）。欠落営業日（㊵）は年別件数を印字し該当行を落とす。
事象 EVT_d = NFP／FOMC 声明（scheduled・2013-03-20+ は 14:00・それ以前も当日扱い）／CPI のセッション日（暦は公開＝事前に既知）。
窓（D2・d の年）: 在 2012-20／外 2021-26H1／近年 2024-26H1（2014-20 を頑健版として併記）。
主回帰（金）: log RV^X_{d+1} = α + φ1 log RV^X_d + φ5 mean log RV^X_{d−4..d} + θ log GVZ_d
                                + γ_S log RV^S_d + γ_S5 mean log RV^S_{d−4..d} + δ0 EVT_d + δ1 EVT_{d+1} + δb brk_{d+1} + ε   （M2）
  M1 = M2 から US500 項を除く（θ の対照）。M3 = M2 + γ_S10 log RV^S_{d−10}（減衰の対照・共通レジームなら lag10 も立つ）。
  NW(5) t・HC1 t・MDE = 2·se(NW)。年 FE 版・事象日（d または d+1）除外版・2014-20 版を頑健として併記。
  ラグ・プロファイル（記述）: lag 0/1/2/5/10 を各々単独で M1 に足した γ_S(k)。
  校正: 循環シフト置換（US500 系列を k∈[20,n−20] 日ずらす・500 回）は**参照のみ**（㊷: レジームを壊すので帰無 sd は過小の疑い）→ 判定は NW t。
逆方向（本拠対照・記述・同仕様）: log RV^S_{d+1} = … + θ_V log VIX_d + γ_X log RV^X_d + γ_X5 mean log RV^X + 事象 + brk。
二次（記述・受け手の価格付け）: Δlog GVZ_{d→d+1} = … + κ_S u^S_d + κ_X u^X_d（u = log RV − 5 日平均＝ショック・Δlog GVZ_{d−1→d}・log GVZ_d 統制）。
  κ_S>0 なら「金 IV は翌日に株ショックへ追随する（当日は未織込み）」の直接の顔。
判定（Bonferroni(2)・名目 0.025）:
  C1（整列の陽性対照）: 在 M1 の θ_GVZ >0 ∧ NW t≥2。立たなければ「IV を超える」の主張は inconclusive（生の γ_S だけ記述）。
  C2 H_SPILL: PASS = 在 γ_S>0 ∧ NW t≥2 ∧ **M3 の (γ_S − γ_S10) >0 ∧ t≥2**（1 日の情報であってレジームでない）∧ 外 γ_S>0 ∧ t≥1.5。
     逆符号で同基準 = 「株ボラの翌日は金が静か」（記述）。他 null（MDE 併記）。
経済的大きさ（事前宣言）: 1 sd の株ボラ・ショック（sd(u^S)）→ 翌日の金 vol 変化 = exp(γ_S·sd/2)−1。**≥5% = オプションで意味を持ち得る／<2% = GVZ の
  日次変動（sd ≈5%）の内側＝統計的に有っても受け取れない**。
決着可能性（㉝・事前）: γ* = 0.10（1 sd 0.6 log → vol +3%）。se を iid 近似 sd_ε/(sd_x√n)（sd_ε≈0.5・sd_x≈0.5・n≈2000）≈0.022 → t* ≈4.5＝決着可能。
  実測 se（NW）で t* を印字・陽性対照 = 在の y に γ*·(log RV^S_d − 平均) を注入して Δt。
ゲート ㉛（本番接続・在のみ）: scan 本の建玉セッション日の**前有効日** d の株ボラ・ショック u^S_d で在 三分位（固定カット）top／bottom の
  Δμ(R*)・Welch t・Δx・x0 look-ahead 対照。在 max|Δμ| <0.048R → 「決着不能・外は走らせない」。（c34: scan はボラ中立 → 通らない見込み。）
事前の最重大反証: (1) 5 日平均で拾えない遅いマクロ・ボラ・レジームの共通因子 → lag10 対照・年 FE 版・逆方向の対称性で読む。(2) bid のみ・1 社。
  (3) US500 npz の欠落営業日（2020 年 60 日・㊵）＝在の 2020 ボラ局面を欠く。(4) GVZ は 30 日 IV ＝「1 日先の最良予測」ではない → θ は長期の
  情報・「IV を超える」は「30 日 IV を超える」と読む。(5) 発表日は両市場のボラを同時に動かす → EVT ダミー＋除外版。(6) 金 RV^X_d は NY 時間を含む
  ＝同日の共変動は既に own 項に入っている → γ_S は「同日中に吸収されなかった分」。(7) セッション長が違う（金 23 h vs 株 6.5 h）→ log と own 項で
  尺度は吸収。(8) 多重検定: 判定 2 セル（C1・C2）、他は記述。
昇格候補・入口/出口規則の提案ではない（市場構造の記述・§8 に行を 1 つ足す）。seed 20261118。
"""
import os, time, json, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c48_vol_spillover_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261118)
NFMIN_X = 100; NFMIN_S = 60; NWLAG = 5; NSHIFT = 500
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle48] ボラの伝播 株→金（US500 現物 RV → 翌セッション金 RV | 金 own・GVZ）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c48_vol_spillover_equity_to_gold.py)")

# ---------- calendars ----------
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
FO = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); FO = FO[FO["scheduled"] == 1]
FOMC = {pd.Timestamp(d).date().toordinal() for d in FO["date"]}
CP = pd.read_csv(os.path.join(MAC, "CPI_dates.csv")); CPI = {pd.Timestamp(d).date().toordinal() for d in CP["date"]}
EVT = NFP | FOMC | CPI
say(f"- 事象暦: NFP {len(NFP)}・FOMC scheduled {len(FOMC)}・CPI {len(CPI)}・和 {len(EVT)} 日（公開暦＝事前既知）")

# ---------- stats ----------
def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.asarray(X, float)
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b; Zu = Z * u[:, None]
    S = Zu.T @ Zu; V_hc = XtX_inv @ S @ XtX_inv * n / (n - Z.shape[1])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = Zu[l:].T @ Zu[:-l]; S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    r2 = 1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return dict(b=b, se=np.sqrt(np.diag(V)), se_hc=np.sqrt(np.diag(V_hc)), V=V, u=u, r2=r2, n=n)
def diff_t(f, i, j):
    d = f["b"][i] - f["b"][j]; se = math.sqrt(f["V"][i, i] + f["V"][j, j] - 2 * f["V"][i, j]); return d, se, d / se
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return diff, diff / se

# ---------- session tables ----------
def load_npz(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    say(f"- {sym}: npz {len(ts)} 本 {dt_ny[0]}〜{dt_ny[-1]} ET（⑩）・flat 全体 {flat.mean()*100:.1f}%（⑪）")
    return ts, lc, r, flat, dt_ny

def xau_daily():
    ts, lc, r, flat, dt_ny = load_npz("XAU")
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep], "r2": r[keep] ** 2}); g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"] = D["date"].dt.weekday
    D = D[(D.wd <= 4) & (D.nf >= NFMIN_X)].reset_index()
    D["lrv"] = np.log(D["rv"]); D["gap"] = np.r_[np.nan, np.diff(D["o"].to_numpy())]
    D["lrv5"] = D["lrv"].rolling(5).mean(); D["year"] = D["date"].dt.year; D["evt"] = D["o"].isin(EVT)
    say(f"- XAU: 有効セッション日 {len(D)}（月〜金 ∧ nf≥{NFMIN_X}）・事象日 {int(D.evt.sum())}")
    return D

def us500_cash_daily():
    ts, lc, r, flat, dt_ny = load_npz("US500")
    mins = dt_ny.hour.to_numpy() * 60 + dt_ny.minute.to_numpy()
    cash = (mins >= 570) & (mins < 960)  # bars opening 09:30..15:55 ET → closes 09:35..16:00 (78 本)
    day = dt_ny.tz_localize(None).values.astype("datetime64[D]"); o = day.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = cash & ~flat
    df = pd.DataFrame({"o": o[keep], "r2": r[keep] ** 2}); g = df.groupby("o", sort=True)
    S = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["r2"].size()})
    S["date"] = pd.to_datetime([dt.date.fromordinal(int(x)) for x in S.index]); S["wd"] = S["date"].dt.weekday
    allbd = S[S.wd <= 4]
    S = S[(S.wd <= 4) & (S.nf >= NFMIN_S)].reset_index()
    bd = pd.bdate_range(S.date.min(), S.date.max()); have = set(allbd.index.tolist())
    miss = [d for d in bd if d.toordinal() not in have]; my = pd.Series([d.year for d in miss]).value_counts().sort_index()
    say(f"- US500 現物 09:30–16:00 ET: 有効日 {len(S)}（nf≥{NFMIN_S}・nf 中央値 {S.nf.median():.0f}/78）・平日で現物足が無い日 {len(miss)}（㊵ 年別: " + ", ".join(f"{y} {c}" for y, c in my.items()) + f"）・nf<{NFMIN_S} の平日 {len(allbd)-len(S)}")
    S["lrvS"] = np.log(S["rv"]); S["lrv5S"] = S["lrvS"].rolling(5).mean(); S["gapS"] = np.r_[np.nan, np.diff(S["o"].to_numpy())]
    for k in (1, 2, 5, 10): S[f"lrvS_l{k}"] = S["lrvS"].shift(k)
    S["year"] = S["date"].dt.year; S["evt"] = S["o"].isin(EVT)
    return S

def fred(name):
    f = pd.read_csv(os.path.join(MAC, name), na_values="."); f.columns = ["date", "v"]; f["date"] = pd.to_datetime(f["date"]); f = f.dropna()
    say(f"- {name}: {len(f)} 行 {f['date'].iloc[0].date()}〜{f['date'].iloc[-1].date()}"); return f

say("\n## 0. データ")
D = xau_daily(); S = us500_cash_daily(); GV = fred("GVZCLS.csv"); VX = fred("VIXCLS.csv")
D = D.merge(S[["date", "lrvS", "lrv5S", "lrvS_l1", "lrvS_l2", "lrvS_l5", "lrvS_l10", "evt"]].rename(columns={"evt": "evtS"}), on="date", how="left")
D = D.merge(GV.rename(columns={"v": "gvz"}), on="date", how="left").merge(VX.rename(columns={"v": "vix"}), on="date", how="left")
D["lgvz"] = np.log(D["gvz"]); D["lvix"] = np.log(D["vix"])
say(f"- 結合: 金 {len(D)} 日・US500 現物あり {int(D.lrvS.notna().sum())}・GVZ あり {int(D.gvz.notna().sum())}・両方 {int((D.lrvS.notna() & D.gvz.notna()).sum())}")

# ---------- frame for gold equation ----------
def frame_gold(D):
    y = D["lrv"].to_numpy()[1:]; n = len(D)
    F = pd.DataFrame({"y": y, "lrv": D["lrv"].to_numpy()[:-1], "lrv5": D["lrv5"].to_numpy()[:-1], "lgvz": D["lgvz"].to_numpy()[:-1],
                      "lrvS": D["lrvS"].to_numpy()[:-1], "lrv5S": D["lrv5S"].to_numpy()[:-1],
                      "l1": D["lrvS_l1"].to_numpy()[:-1], "l2": D["lrvS_l2"].to_numpy()[:-1], "l5": D["lrvS_l5"].to_numpy()[:-1], "l10": D["lrvS_l10"].to_numpy()[:-1],
                      "evt0": D["evt"].to_numpy()[:-1].astype(float), "evt1": D["evt"].to_numpy()[1:].astype(float),
                      "brk": (D["gap"].to_numpy()[1:] > 1).astype(float), "year": D["year"].to_numpy()[:-1], "date": D["date"].to_numpy()[:-1]})
    ok = np.isfinite(F[["y", "lrv", "lrv5", "lgvz", "lrvS", "lrv5S", "l10"]].to_numpy()).all(1)
    return F[ok].reset_index(drop=True)
F = frame_gold(D)
F["uS"] = F["lrvS"] - F["lrv5S"]; F["uX"] = F["lrv"] - F["lrv5"]
say(f"- 金 回帰フレーム {len(F)} 行（2012+ で US500 現物・GVZ・lag10 がそろう日）・brk {F.brk.mean()*100:.0f}%・事象 d {F.evt0.mean()*100:.0f}%／d+1 {F.evt1.mean()*100:.0f}%・sd(log RV^X) {F.y.std():.2f}・sd(log RV^S) {F.lrvS.std():.2f}・sd(u^S) {F.uS.std():.2f}")

WIN = {"在 2012-20": (2012, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026), "頑健 2014-20": (2014, 2020)}
BASE = ["lrv", "lrv5", "evt0", "evt1", "brk"]
def fit(v, cols, yfe=False):
    X = v[cols].to_numpy()
    if yfe:
        yrs = sorted(v.year.unique())[1:]; X = np.column_stack([X] + [(v.year == yy).to_numpy().astype(float) for yy in yrs])
    return nw_ols(v.y.to_numpy(), X)

RES = {}
say("\n## 1. 主回帰（金）: log RV^X_(d+1) on own(φ1,φ5)・GVZ(θ)・US500 現物(γ_S, γ_S5)・事象・brk — NW(5) t")
say("| 窓 | n | θ_GVZ M1 (t) | **γ_S M2 (NW t)** | HC1 t | MDE 2se | 1sd(u^S) → 翌日 vol % | γ_S5 (t) | θ M2 (t) | φ1 (t) | R² M1→M2 | M3: γ_S (t) | γ_S10 (t) | **γ_S−γ_S10 (t)** | 年FE γ_S (t) | 事象除外 γ_S (t) |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for wn, (y0, y1) in WIN.items():
    v = F[(F.year >= y0) & (F.year <= y1)].reset_index(drop=True)
    m1 = fit(v, BASE + ["lgvz"]); m2 = fit(v, BASE + ["lgvz", "lrvS", "lrv5S"]); m3 = fit(v, BASE + ["lgvz", "lrvS", "lrv5S", "l10"])
    mfe = fit(v, BASE + ["lgvz", "lrvS", "lrv5S"], yfe=True)
    vx = v[(v.evt0 == 0) & (v.evt1 == 0)].reset_index(drop=True); mx = fit(vx, ["lrv", "lrv5", "brk", "lgvz", "lrvS", "lrv5S"])
    iSx = 5  # index of lrvS in mx (0=const)
    iS = 1 + len(BASE) + 1  # index of lrvS in m2 (0=const)
    gS = m2["b"][iS]; tS = gS / m2["se"][iS]; thS = m2["se_hc"][iS]
    dd, dse, dtt = diff_t(m3, iS, iS + 2)
    sdu = v.uS.std(); eff = (math.exp(gS * sdu / 2) - 1) * 100
    RES[wn] = dict(n=m2["n"], th1=m1["b"][6], th1_t=m1["b"][6] / m1["se"][6], gS=gS, tS=tS, se=m2["se"][iS], eff=eff, sdu=sdu,
                   d10=dd, d10_t=dtt, gS3=m3["b"][iS], gS3_t=m3["b"][iS] / m3["se"][iS], g10=m3["b"][iS + 2], g10_t=m3["b"][iS + 2] / m3["se"][iS + 2],
                   fe=mfe["b"][iS], fe_t=mfe["b"][iS] / mfe["se"][iS], ex=mx["b"][iSx], ex_t=mx["b"][iSx] / mx["se"][iSx], m2=m2, v=v)
    say(f"| {wn} | {m2['n']} | {m1['b'][6]:+.3f} ({m1['b'][6]/m1['se'][6]:+.2f}) | **{gS:+.4f} ({tS:+.2f})** | {gS/thS:+.2f} | {2*m2['se'][iS]:.4f} | {eff:+.2f}% | {m2['b'][iS+1]:+.3f} ({m2['b'][iS+1]/m2['se'][iS+1]:+.2f}) | {m2['b'][6]:+.3f} ({m2['b'][6]/m2['se'][6]:+.2f}) | {m2['b'][1]:+.3f} ({m2['b'][1]/m2['se'][1]:+.1f}) | {m1['r2']:.3f}→{m2['r2']:.3f} | {m3['b'][iS]:+.4f} ({m3['b'][iS]/m3['se'][iS]:+.2f}) | {m3['b'][iS+2]:+.4f} ({m3['b'][iS+2]/m3['se'][iS+2]:+.2f}) | **{dd:+.4f} ({dtt:+.2f})** | {mfe['b'][iS]:+.4f} ({mfe['b'][iS]/mfe['se'][iS]:+.2f}) | {mx['b'][iSx]:+.4f} ({mx['b'][iSx]/mx['se'][iSx]:+.2f}) (n {mx['n']}) |")

# decidability + injection (在)
r0 = RES["在 2012-20"]; gstar = 0.10
vi = r0["v"].copy(); vi["y"] = vi.y + gstar * (vi.lrvS - vi.lrvS.mean()); mi = fit(vi, BASE + ["lgvz", "lrvS", "lrv5S"])
say(f"- 決着可能性（㉝）: γ* = 0.10（1 sd u^S {r0['sdu']:.2f} → vol {(math.exp(0.10*r0['sdu']/2)-1)*100:+.1f}%）・実測 se(NW) {r0['se']:.4f} → t* {gstar/r0['se']:.1f}；陽性対照 在に γ* 注入 → γ_S {mi['b'][7]:+.4f} (t {mi['b'][7]/mi['se'][7]:+.2f})（実測 {r0['tS']:+.2f} から Δt {mi['b'][7]/mi['se'][7]-r0['tS']:+.2f}）")

# lag profile (each lag alone added to M1)
say("- ラグ・プロファイル（記述・各ラグを単独で M1 に足した γ_S(k)・NW t）:")
for wn in ("在 2012-20", "外 2021-26H1"):
    v = RES[wn]["v"]; prof = []
    for k, col in ((0, "lrvS"), (1, "l1"), (2, "l2"), (5, "l5"), (10, "l10")):
        vv = v[np.isfinite(v[col])].reset_index(drop=True); m = fit(vv, BASE + ["lgvz", col]); prof.append(f"k={k} {m['b'][7]:+.4f} ({m['b'][7]/m['se'][7]:+.2f})")
    say(f"  - {wn}: " + "・".join(prof))

# circular-shift placebo (reference only)
say("- 循環シフト置換（参照のみ・㊷ 過小校正の疑い）: 在/外 で US500 列を k∈[20,n−20] 日ずらして γ_S を再推定・帰無 sd と両側 p")
for wn in ("在 2012-20", "外 2021-26H1"):
    v = RES[wn]["v"]; n = len(v); X0 = v[BASE + ["lgvz"]].to_numpy(); y = v.y.to_numpy(); S2 = v[["lrvS", "lrv5S"]].to_numpy()
    gp = np.empty(NSHIFT)
    for i in range(NSHIFT):
        k = int(rng.integers(20, n - 20)); Z = np.column_stack([np.ones(n), X0, np.roll(S2, k, axis=0)])
        bb, *_ = np.linalg.lstsq(Z, y, rcond=None); gp[i] = bb[7]
    say(f"  - {wn}: 帰無 sd {gp.std():.4f}（NW se {RES[wn]['se']:.4f}）・両側 p {(np.abs(gp) >= abs(RES[wn]['gS'])).mean():.3f}")

# yearly γ_S (HC1)
rows = []
for yy in sorted(F.year.unique()):
    v = F[F.year == yy].reset_index(drop=True)
    if len(v) < 100: continue
    m = fit(v, BASE + ["lgvz", "lrvS", "lrv5S"]); rows.append(f"{yy} {m['b'][7]:+.3f} ({m['b'][7]/m['se_hc'][7]:+.1f})")
say("- 年別 γ_S (HC1 t): " + "・".join(rows))

# ---------- 2. reverse direction (home-market contrast) ----------
say("\n## 2. 逆方向（本拠対照・記述）: log RV^S_(d+1) on own(S)・VIX・金 own(γ_X, γ_X5)・事象・brk")
S2 = S.merge(D[["date", "lrv", "lrv5", "lvix"]], on="date", how="left")
y = S2["lrvS"].to_numpy()[1:]
G = pd.DataFrame({"y": y, "lrv": S2["lrvS"].to_numpy()[:-1], "lrv5": S2["lrv5S"].to_numpy()[:-1], "lvix": S2["lvix"].to_numpy()[:-1],
                  "lrvX": S2["lrv"].to_numpy()[:-1], "lrv5X": S2["lrv5"].to_numpy()[:-1], "l10": S2["lrvS_l10"].to_numpy()[:-1],
                  "evt0": S2["evt"].to_numpy()[:-1].astype(float), "evt1": S2["evt"].to_numpy()[1:].astype(float),
                  "brk": (S2["gapS"].to_numpy()[1:] > 1).astype(float), "year": S2["year"].to_numpy()[:-1]})
G = G[np.isfinite(G[["y", "lrv", "lrv5", "lvix", "lrvX", "lrv5X"]].to_numpy()).all(1)].reset_index(drop=True)
say("| 窓 | n | θ_VIX (t) | **γ_X (NW t)** | MDE | 1sd(u^X) → 翌日 株 vol % | γ_X5 (t) | R² |")
say("|---|---|---|---|---|---|---|---|")
REV = {}
for wn, (y0, y1) in list(WIN.items())[:3]:
    v = G[(G.year >= y0) & (G.year <= y1)].reset_index(drop=True)
    m = fit(v, BASE + ["lvix", "lrvX", "lrv5X"]); gX = m["b"][7]; sdx = (v.lrvX - v.lrv5X).std()
    REV[wn] = (gX, gX / m["se"][7]); say(f"| {wn} | {m['n']} | {m['b'][6]:+.3f} ({m['b'][6]/m['se'][6]:+.2f}) | **{gX:+.4f} ({gX/m['se'][7]:+.2f})** | {2*m['se'][7]:.4f} | {(math.exp(gX*sdx/2)-1)*100:+.2f}% | {m['b'][8]:+.3f} ({m['b'][8]/m['se'][8]:+.2f}) | {m['r2']:.3f} |")

# ---------- 3. does gold IV catch up next day? ----------
say("\n## 3. 二次（記述・受け手の価格付け）: Δlog GVZ_(d→d+1) on Δlog GVZ_(d−1→d)・log GVZ_d・u^X_d・u^S_d（連続する GVZ 日・暦差 ≤4 日）")
Gv = GV.rename(columns={"v": "gvz"}).copy(); Gv["lg"] = np.log(Gv.gvz); Gv["dl_next"] = Gv.lg.shift(-1) - Gv.lg; Gv["dl_prev"] = Gv.lg - Gv.lg.shift(1)
Gv["gapd"] = (Gv.date.shift(-1) - Gv.date).dt.days
Gv = Gv.merge(F[["date", "uS", "uX", "evt1", "evt0"]], on="date", how="inner")
Gv = Gv[(Gv.gapd <= 4) & np.isfinite(Gv[["dl_next", "dl_prev", "uS", "uX"]].to_numpy()).all(1)].reset_index(drop=True)
Gv["year"] = Gv.date.dt.year
say("| 窓 | n | κ_S u^S (NW t) | κ_X u^X (t) | ρ(Δlog GVZ_next) on Δlog GVZ_prev (t) | sd Δlog GVZ | 1sd u^S → GVZ 翌日 % |")
say("|---|---|---|---|---|---|---|")
for wn, (y0, y1) in list(WIN.items())[:3]:
    v = Gv[(Gv.year >= y0) & (Gv.year <= y1)].reset_index(drop=True)
    m = nw_ols(v.dl_next.to_numpy(), v[["dl_prev", "lg", "uX", "uS", "evt0", "evt1"]].to_numpy())
    say(f"| {wn} | {m['n']} | **{m['b'][4]:+.4f} ({m['b'][4]/m['se'][4]:+.2f})** | {m['b'][3]:+.4f} ({m['b'][3]/m['se'][3]:+.2f}) | {m['b'][1]:+.3f} ({m['b'][1]/m['se'][1]:+.2f}) | {v.dl_next.std():.3f} | {m['b'][4]*v.uS.std()*100:+.2f}% |")

# ---------- 4. gate ㉛ ----------
say("\n## 4. ゲート ㉛（本番接続・在のみ）: 建玉セッション日の前有効日 d の株ボラ・ショック u^S_d で scan 本を三分位")
d_ = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d_["frozen"]["FEED_TOL"]; tr = pd.DataFrame(d_["trades"])
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = (tr["exit"] == "TP").astype(float) - tr["q"]
e_ny = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(NY)
tr["so"] = ((e_ny + pd.Timedelta(hours=6)).dt.tz_localize(None).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal())
Fk = F.copy(); Fk["o"] = pd.to_datetime(Fk.date).map(lambda x: x.toordinal()); ords = Fk["o"].to_numpy(); us = Fk["uS"].to_numpy()
pos = np.searchsorted(ords, tr["so"].to_numpy(), side="left") - 1; okp = pos >= 0
tr["uS_prev"] = np.where(okp, us[np.clip(pos, 0, len(us) - 1)], np.nan); tr["stale"] = np.where(okp, tr["so"].to_numpy() - ords[np.clip(pos, 0, len(ords) - 1)], np.nan)
tr.loc[tr.stale > 4, "uS_prev"] = np.nan
ins = tr[(tr.year >= 2012) & (tr.year <= 2020) & tr.uS_prev.notna() & tr.dec]
cut = np.quantile(ins.uS_prev, [1 / 3, 2 / 3])
say(f"- 付与 {int(tr.uS_prev.notna().sum())}/{len(tr)}（staleness ≤4 日）・在 2012-20 決着本 n {len(ins)}・三分位カット u^S {cut[0]:+.3f}／{cut[1]:+.3f}")
top = ins[ins.uS_prev > cut[1]]; bot = ins[ins.uS_prev <= cut[0]]
d_top, t_top = welch(top.Rs, ins[ins.uS_prev <= cut[1]].Rs); d_bot, t_bot = welch(bot.Rs, ins[ins.uS_prev > cut[0]].Rs)
dmu_top = top.Rs.mean() - ins.Rs.mean(); dmu_bot = bot.Rs.mean() - ins.Rs.mean()
x0cut = ins.x0.quantile(2 / 3); d0, t0_ = welch(ins[ins.x0 > x0cut].Rs, ins[ins.x0 <= x0cut].Rs)
say(f"- 在: top n{len(top)} Δμ {dmu_top:+.3f}R (Welch t {t_top:+.2f}) Δx {100*(top.x.mean()-ins.x.mean()):+.2f} pp；bottom n{len(bot)} Δμ {dmu_bot:+.3f}R (t {t_bot:+.2f}) Δx {100*(bot.x.mean()-ins.x.mean()):+.2f} pp；look-ahead 対照 x0 top Δμ {d0:+.3f}R (t {t0_:+.1f})")
gate = max(abs(dmu_top), abs(dmu_bot))
say(f"- ゲート ㉛: 在 max|Δμ| {gate:.3f}R {'<' if gate < 0.048 else '≥'} 0.048R → **{'決着不能・外は走らせない' if gate < 0.048 else '外を印字'}**")
if gate >= 0.048:
    oos = tr[(tr.year >= 2021) & tr.uS_prev.notna() & tr.dec]
    say(f"  外: top Δμ {oos[oos.uS_prev > cut[1]].Rs.mean() - oos.Rs.mean():+.3f}R・bottom Δμ {oos[oos.uS_prev <= cut[0]].Rs.mean() - oos.Rs.mean():+.3f}R (n {len(oos)})")

# ---------- 判定 ----------
say("\n## 判定（事前固定・Bonferroni(2)・名目 0.025）")
a = RES["在 2012-20"]; o = RES["外 2021-26H1"]; nr = RES["近年 2024-26H1"]
C1 = a["th1"] > 0 and a["th1_t"] >= 2
say(f"- C1 整列の陽性対照（在 M1 θ_GVZ>0 ∧ t≥2）: θ {a['th1']:+.3f} (t {a['th1_t']:+.2f}) → **{'PASS（GVZ は翌日 RV に情報を持つ＝整列 OK）' if C1 else 'FAIL（IV を超える主張は inconclusive）'}**")
pos_ = a["gS"] > 0 and a["tS"] >= 2 and a["d10"] > 0 and a["d10_t"] >= 2 and o["gS"] > 0 and o["tS"] >= 1.5
neg_ = a["gS"] < 0 and a["tS"] <= -2 and a["d10"] < 0 and a["d10_t"] <= -2 and o["gS"] < 0 and o["tS"] <= -1.5
vd = "H_SPILL PASS（株ボラ → 翌日の金ボラ・IV を超える・1 日の情報）" if pos_ else ("逆符号 PASS（株ボラの翌日は金が静か）" if neg_ else "null")
say(f"- C2 H_SPILL: 在 γ_S {a['gS']:+.4f} (NW t {a['tS']:+.2f}・MDE {2*a['se']:.4f}・γ_S−γ_S10 {a['d10']:+.4f} t {a['d10_t']:+.2f})／外 {o['gS']:+.4f} (t {o['tS']:+.2f}・MDE {2*o['se']:.4f})／近年 {nr['gS']:+.4f} (t {nr['tS']:+.2f}) → **{vd}**" + ("" if C1 else "（C1 FAIL のため記述扱い）"))
say(f"- 経済的大きさ: 1 sd の株ボラ・ショック → 翌日の金 vol 在 {a['eff']:+.2f}%／外 {o['eff']:+.2f}%／近年 {nr['eff']:+.2f}%（宣言: ≥5% 意味あり／<2% GVZ 日次 sd の内側）")
say(f"- 逆方向 γ_X（金 → 翌日 株 | VIX）: 在 {REV['在 2012-20'][0]:+.4f} (t {REV['在 2012-20'][1]:+.2f})／外 {REV['外 2021-26H1'][0]:+.4f} (t {REV['外 2021-26H1'][1]:+.2f})")
say(f"\n所要 {time.time()-T0:.1f} s・scan 無し・MT5 無し・外部通信無し・seed 20261118")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
