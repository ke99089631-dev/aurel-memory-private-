# -*- coding: utf-8 -*-
"""
[cycle58 研究レーン 2026-11-20] 【探索・リスクプレミアムの時間変動（ボラ管理 / volatility-managed returns）】
Moreira–Muir (2017 JF) は「前月の実現ボラの逆数で資産エクスポージャを調整すると、株式・一部通貨/商品で α（appraisal alpha）が正」
と報告した。機構 = ボラが高い期間に期待リターンがボラの二乗ほど上がらない（risk-return tradeoff の弱さ・レバレッジ制約で
裁定されない）。Harvey et al. (2018 JPM "The Impact of Volatility Targeting") は、効果は株・クレジットなど「レバレッジ効果
（下げ→ボラ上昇）のある資産」で出て、債券・通貨・商品では小さいと報告。我々は c41 で **US500 は強い負の非対称（レバレッジ効果）・
金は非対称なし** を確認した → AI らしい角度 = c41 から予測を導いて別統計で検証: ボラ管理 α は US500 で正（本拠・陽性対照 ㉝）、
金では 0（H_VM null）。§8 源泉マップに「ボラ管理（ボラの時間変動 × 期待リターンの非比例）」行を 1 つ足す。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/XAU_m5_close.npz・US500_m5_close.npz（bid・暦時刻完全格子・前値埋め）・GVZCLS.csv／VIXCLS.csv（FRED・副）
  ・refute_c4_scan_paths_2010_2026.json（ゲートのみ）。既存キャッシュのみ・scan 無し・M5 読込なし・MT5 無し・外部通信無し。
セッション日 d = (ET+6h) の暦日・有効 = 月〜金 ∧ 非 flat ≥100（⑪）・r_d = Δ ln(最終取引足 close) bp・RV_d = Σ(Δln)²（c41 と同じ）。
ボラ推定（d の終わりに既知・d+1 に適用）: σ̂21_d = sqrt(mean RV_{d−20..d})（主）／σ̂1_d = sqrt(RV_d)（副・Moreira–Muir は月次 RV）
  ／IV_d = GVZ（金）・VIX（US500）の FRED 日付 d（16:15 ET 確定・look-ahead なし・副）。
ボラ管理リターン: r^VM_{d+1} = (c/σ̂_d)·r_{d+1}・c は窓内で sd(r^VM)=sd(r) となる定数（α の t・SR には無関係）。
窓（D2）: 在 2010-20（US500 は夜間配信 ㉒ と無関係だが c41 と揃え 2014-20）／外 2021-26H1／近年 2024-26H1。
主統計: (A) α: r^VM = α + β·r + ε（Moreira–Muir の appraisal α）・NW(5) t・HC1 t・MDE = 2·se(NW)・bp/日と %/年（×252/1e4）。
  帰無校正 = σ̂ 系列を r に対して**循環シフト**（オフセット ≥30 セッション・2000 回・両側 p・方法論 ⑨ の日次版：両系列の自己相関を保存）。
  (B) ΔSR = SR(VM) − SR(raw)（年率）・定常ブロック bootstrap（平均ブロック 22 日・2000 回）95% CI。
  (C) 機構: σ̂21 五分位（窓内）ごとの 翌日 mean r・sd r・mean/var（この比が五分位で一定なら VM に α は無い）・r_{d+1} on log σ̂_d の β。
判定（Bonferroni(2)・名目 0.025）:
  C1 US500（本拠・陽性対照）: PASS = 在 α>0 ∧ NW t≥2 ∧ 置換 p<0.025。立たなければ「この格子・この長さでは方法が VM 効果を見ない」
    （検出力不足か効果不在か未分離）→ C2 は記述のみ（㉝）。
  C2 XAU: H_VM PASS = 在 α>0 ∧ t≥2 ∧ p<0.025 ∧ 外 α>0 ∧ t≥1.5。H_NEG（VM が害）PASS = 在 α<0 ∧ t≤−2 ∧ p<0.025 ∧ 外 α<0 ∧ t≤−1.5。
    どちらでもなければ null（MDE 併記）。事前の予測 = null（Harvey 2018・c41 非対称なし）。
決着可能性（事前・正直に）: 文献の α は株で ≈4〜5%/年 ≈ 1.6〜2.0 bp/日。残差 sd ≈ 0.6×sd_r（≈60 bp）・n 在 ≈1700（US500）〜2700（金）
  → se ≈ 1.2〜1.5 bp/日・MDE ≈ 2.4〜3.0 bp/日 ≈ 6〜7.5%/年 ＝ **文献級は在の長さで決着不能の縁**。US500 在は 2020-03 を含み
  VM の利得は危機に集中（Harvey）→ 陽性対照は episode 1 つに依存し得る（2020 除外版を併記）。効果 2×文献級の注入で t を印字。
ゲート ㉛（本番接続・在のみ・記述）: scan の本を建玉時 ATR14（既知）の窓内三分位で分け R*（R+ft·1{SL,TP}）の Δμ（高−低）・Welch t・
  1/ATR 加重平均 R* − 単純平均。|Δμ|<0.048R → 「本のサイズをボラで変える根拠なし・外は走らせない」。
事前の最重大反証: (1) 検出力（上記）。(2) bid のみの 5 分 RV は上方バイアス（c34）→ log 比を使う VM では σ̂ の水準定数に吸収され中立。
  (3) 日次リバランスの取引費用は未控除（null 判定には保守側・正の場合だけ問題）。(4) 2020 夏の US500 欠落 68 日（㊵）。
  (5) α は β·r を引いた残り＝「ボラが低い日に大きく張る」の線形部分を除いた非線形分。(6) 週末・祝日跨ぎは σ̂ と r の両方を歪める → brk 除外版。
昇格候補・入口/出口規則の提案ではない。seed 20261120.
"""
import os, time, json, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c58_vol_managed_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261120)
NFMIN = 100; NPERM = 2000; NBOOT = 2000; NWLAG = 5; LB = 21
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle58] ボラ管理リターン（volatility-managed）の α — 金 vs US500（陽性対照） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c58_vol_managed_premium.py)")

def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.asarray(X, float)
    if X.ndim == 1: X = X[:, None]
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b
    Sm = (Z * u[:, None]).T @ (Z * u[:, None])
    V_hc = XtX_inv @ Sm @ XtX_inv * n / (n - Z.shape[1])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = (Z[l:] * u[l:, None]).T @ (Z[:-l] * u[:-l, None]); Sm += w * (G + G.T)
    V = XtX_inv @ Sm @ XtX_inv
    return b, np.sqrt(np.diag(V)), np.sqrt(np.diag(V_hc)), u

def daily_table(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    wd = dt_ny.weekday.values
    say(f"- {sym}: npz {len(ts)} 本 {pd.to_datetime(ts[0], unit='s').date()}〜{pd.to_datetime(ts[-1], unit='s').date()} UTC・flat 全体 {flat.mean()*100:.1f}%（⑪ 曜日別: " + " ".join(f"{d}:{flat[wd==i].mean()*100:.1f}" for i, d in enumerate("月火水木金土日")) + "）")
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep], "r2": r[keep] ** 2})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "rv": g["r2"].sum(), "nf": g["r2"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"] = D["date"].dt.weekday
    allbd = D[D.wd <= 4]
    D = D[(D.wd <= 4) & (D.nf >= NFMIN)].reset_index()
    bd_grid = pd.bdate_range(D.date.min(), D.date.max()); have = set(allbd.index.tolist())
    miss = [d for d in bd_grid if d.toordinal() not in have]
    my = pd.Series([d.year for d in miss]).value_counts().sort_index()
    say(f"- {sym}: 有効セッション日 {len(D)}（平日 nf<{NFMIN} {len(allbd)-len(D)} 日・足無し平日 {len(miss)} 日: " + ", ".join(f"{y} {c}" for y, c in my.items()) + "）（㊵）")
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["gap"] = np.r_[np.nan, np.diff(D["o"].to_numpy())]
    D["sig21"] = np.sqrt(D["rv"].rolling(LB).mean()) * 1e4   # bp/day-ish units
    D["sig1"] = np.sqrt(D["rv"]) * 1e4
    D["year"] = D["date"].dt.year
    return D

def load_fred(name):
    p = os.path.join(MAC, f"{name}.csv")
    if not os.path.exists(p): return None
    f = pd.read_csv(p); f.columns = ["date", "v"]; f["v"] = pd.to_numeric(f["v"], errors="coerce")
    f["o"] = pd.to_datetime(f["date"]).map(lambda x: x.toordinal()); return f.dropna().set_index("o")["v"]

def sharpe(x): return x.mean() / x.std(ddof=1) * math.sqrt(252)

def stationary_boot_idx(n, block, rng):
    # circular block bootstrap (fixed block length) — vectorized
    nb = int(math.ceil(n / block)); starts = rng.integers(n, size=nb)
    idx = (starts[:, None] + np.arange(block)[None, :]) % n
    return idx.ravel()[:n]

def analyze(D, sym, windows, iv=None, inject=None):
    res = {}
    for wname, (y0, y1) in windows.items():
        # target day d+1 in window; predictor sigma at d (previous valid session)
        sig = D["sig21"].to_numpy()[:-1]; sig1 = D["sig1"].to_numpy()[:-1]
        r = D["r"].to_numpy()[1:]; yr = D["year"].to_numpy()[1:]; brk = D["gap"].to_numpy()[1:] > 1
        ivv = None
        if iv is not None:
            ivv = D["o"].map(iv).to_numpy()[:-1]
        m = (yr >= y0) & (yr <= y1) & np.isfinite(sig) & np.isfinite(r) & (sig > 0)
        for tag, s, mm in [("VM21", sig, m), ("VM1", sig1, m & np.isfinite(sig1) & (sig1 > 0)),
                           ("VM21_nobrk", sig, m & ~brk), ("IV", ivv, (m & np.isfinite(ivv)) if ivv is not None else None)]:
            if mm is None: continue
            rr = r[mm]; ss = s[mm]
            if inject is not None and tag == "VM21": rr = rr.copy()
            w = 1.0 / ss; vm = w * rr; vm = vm * (rr.std(ddof=1) / vm.std(ddof=1))
            if inject is not None and tag == "VM21":
                # inject: add alpha*: vm_inj = vm + a*(w/mean(w) - beta-neutral?) simple: add a*(1 - ...)? use alpha shift orthogonal to r: residualize w on r
                pass
            b, se, seh, u = nw_ols(vm, rr)
            a, beta = b[0], b[1]; t_nw = a / se[0]; t_hc = a / seh[0]
            n = len(rr)
            # permutation: circular shift of sigma vs r
            tp = np.empty(NPERM) if tag == "VM21" else None
            if tag == "VM21":
                for k in range(NPERM):
                    off = int(rng.integers(30, n - 30)); ss2 = np.roll(ss, off); vm2 = rr / ss2; vm2 *= rr.std(ddof=1) / vm2.std(ddof=1)
                    b2, se2, _, _ = nw_ols(vm2, rr); tp[k] = b2[0] / se2[0]
                p_perm = (np.abs(tp) >= abs(t_nw)).mean(); sd_null = tp.std()
            else:
                p_perm = np.nan; sd_null = np.nan
            sr_raw = sharpe(rr); sr_vm = sharpe(vm); dsr = sr_vm - sr_raw
            if tag == "VM21":
                bs = np.empty(NBOOT)
                for k in range(NBOOT):
                    ix = stationary_boot_idx(n, 22, rng); bs[k] = sharpe(vm[ix]) - sharpe(rr[ix])
                lo, hi = np.percentile(bs, [2.5, 97.5]); p_bs = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
            else: lo = hi = p_bs = np.nan
            res[(wname, tag)] = dict(n=n, a=a, se=se[0], t_nw=t_nw, t_hc=t_hc, beta=beta, p_perm=p_perm, sd_null=sd_null,
                                     sr_raw=sr_raw, sr_vm=sr_vm, dsr=dsr, lo=lo, hi=hi, p_bs=p_bs, mde=2 * se[0])
            say(f"  - {sym} {wname} {tag}: n {n}・α {a:+.2f} bp/日（{a*252/1e2:+.2f}%/年）・se {se[0]:.2f}・NW t {t_nw:+.2f}・HC1 t {t_hc:+.2f}・β {beta:.3f}・MDE {2*se[0]:.2f} bp/日"
                + (f"・置換 p {p_perm:.3f}（帰無 sd {sd_null:.2f}）" if tag == "VM21" else "")
                + f"・SR raw {sr_raw:+.2f} → VM {sr_vm:+.2f}（Δ {dsr:+.2f}" + (f"・CI [{lo:+.2f},{hi:+.2f}]・p_bs {p_bs:.3f}" if tag == "VM21" else "") + "）")
        # mechanism: quintiles of sig21
        rr = r[m]; ss = sig[m]
        q = np.quantile(ss, [0.2, 0.4, 0.6, 0.8]); bins = np.digitize(ss, q)
        rows = []
        for k in range(5):
            x = rr[bins == k]; rows.append(f"Q{k+1} n {len(x)} σ̂ {ss[bins==k].mean():.0f} mean {x.mean():+.1f} sd {x.std(ddof=1):.0f} mean/var×1e4 {x.mean()/x.var(ddof=1)*1e4:+.2f}")
        bb, sse, _, _ = nw_ols(rr, np.log(ss))
        say(f"  - {sym} {wname} 機構（σ̂21 五分位・翌日 r bp）: " + " | ".join(rows) + f" ‖ r on log σ̂ β {bb[1]:+.1f} bp/log (t {bb[1]/sse[1]:+.2f})")
        # injection positive control (VM21, in-sample only): add alpha* via scaling vm by (1 + a*·g) where g = standardized 1/sig residualized on r
        if inject is not None and wname == list(windows.keys())[0]:
            ss_ = sig[m]; w = 1.0 / ss_; vm = w * rr; vm *= rr.std(ddof=1) / vm.std(ddof=1)
            vm_inj = vm + inject  # pure level shift = alpha shift of `inject` bp/day
            b, se, _, _ = nw_ols(vm_inj, rr)
            say(f"  - {sym} {wname} 注入対照: α* {inject:+.1f} bp/日 を加えると α {b[0]:+.2f}・NW t {b[0]/se[0]:+.2f}（判定規則 t≥2 の検出）")
    return res

# ---------------- run ----------------
say("\n## 1. データ")
DX = daily_table("XAU"); DS = daily_table("US500")
GVZ = load_fred("GVZCLS"); VIX = load_fred("VIXCLS")
say(f"- GVZ {('有 ' + str(len(GVZ))) if GVZ is not None else '無'}・VIX {('有 ' + str(len(VIX))) if VIX is not None else '無'}（FRED 日付 D = セッション日 D・16:15 ET 確定・d+1 に適用）")
say(f"- σ̂21 中央値 bp/日: XAU 在 {DX[(DX.year>=2010)&(DX.year<=2020)].sig21.median():.0f}／外 {DX[DX.year>=2021].sig21.median():.0f}；US500 在 {DS[(DS.year>=2014)&(DS.year<=2020)].sig21.median():.0f}／外 {DS[DS.year>=2021].sig21.median():.0f}")

WX = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
WS = {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026), "在 2014-20 除 2020": None}

say("\n## 2. C1 本拠・陽性対照 US500")
RS = analyze(DS, "US500", {k: v for k, v in WS.items() if v is not None}, iv=VIX, inject=3.6)
# 2020-excluded in-sample
DS2 = DS[DS.year != 2020].reset_index(drop=True)
say("  (2020 年除外版・在 2014-19)")
RS2 = analyze(DS2, "US500", {"在 2014-20 除 2020": (2014, 2020)}, iv=VIX)

say("\n## 3. C2 金 XAU")
RX = analyze(DX, "XAU", WX, iv=GVZ, inject=3.6)

say("\n## 4. ゲート ㉛（scan 本・建玉時 ATR14 三分位・在のみ判定・外は記述）")
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
rows = J["trades"]
P = pd.DataFrame(rows)
say(f"- scan json {len(P)} 本・列 {list(P.columns)[:14]}…")
ft = 0.1 / P["risk"].to_numpy(); ex = P["exit"].astype(str).str.upper().to_numpy()
P["Rs"] = P["R"].to_numpy() + ft * np.isin(ex, ["SL", "TP"])
for wname, (y0, y1) in WX.items():
    S = P[(P.year >= y0) & (P.year <= y1) & P.atr.notna() & (P.atr > 0)]
    q = S.atr.quantile([1/3, 2/3]).to_numpy(); hi = S[S.atr > q[1]]; lo = S[S.atr <= q[0]]
    d = hi.Rs.mean() - lo.Rs.mean(); se = math.sqrt(hi.Rs.var(ddof=1)/len(hi) + lo.Rs.var(ddof=1)/len(lo))
    w = 1.0 / S.atr.to_numpy(); wm = (w * S.Rs.to_numpy()).sum() / w.sum()
    say(f"- {wname}: n {len(S)}・R̄* 高 ATR {hi.Rs.mean():+.4f} (n {len(hi)}) − 低 {lo.Rs.mean():+.4f} (n {len(lo)}) = Δμ {d:+.4f}R (Welch t {d/se:+.2f}・MDE {2*se:.3f})・sd 高 {hi.Rs.std():.2f}／低 {lo.Rs.std():.2f}・1/ATR 加重 R̄* {wm:+.4f} vs 単純 {S.Rs.mean():+.4f}（差 {wm-S.Rs.mean():+.4f}）")

say("\n## 5. 判定（事前規則）")
def g(R, w, tag="VM21"): return R[(w, tag)]
us_in = g(RS, "在 2014-20"); c1 = us_in["a"] > 0 and us_in["t_nw"] >= 2 and us_in["p_perm"] < 0.025
say(f"- C1 US500 在: α {us_in['a']:+.2f} bp/日 t {us_in['t_nw']:+.2f} p {us_in['p_perm']:.3f} → {'PASS' if c1 else 'FAIL'}（外 α {g(RS,'外 2021-26H1')['a']:+.2f} t {g(RS,'外 2021-26H1')['t_nw']:+.2f}・2020 除外 α {g(RS2,'在 2014-20 除 2020')['a']:+.2f} t {g(RS2,'在 2014-20 除 2020')['t_nw']:+.2f}）")
xi = g(RX, "在 2010-20"); xo = g(RX, "外 2021-26H1")
hvm = xi["a"] > 0 and xi["t_nw"] >= 2 and xi["p_perm"] < 0.025 and xo["a"] > 0 and xo["t_nw"] >= 1.5
hneg = xi["a"] < 0 and xi["t_nw"] <= -2 and xi["p_perm"] < 0.025 and xo["a"] < 0 and xo["t_nw"] <= -1.5
say(f"- C2 XAU: 在 α {xi['a']:+.2f} t {xi['t_nw']:+.2f} p {xi['p_perm']:.3f}（MDE {xi['mde']:.2f}）／外 α {xo['a']:+.2f} t {xo['t_nw']:+.2f}（MDE {xo['mde']:.2f}） → H_VM {'PASS' if hvm else 'FAIL'}・H_NEG {'PASS' if hneg else 'FAIL'} → {'null' if not (hvm or hneg) else 'PASS'}" + ("" if c1 else "（C1 FAIL のため記述のみ ㉝）"))
say(f"\n- 時間 {time.time()-T0:.1f} s・seed 20261120・外部通信なし・scan 無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT)
