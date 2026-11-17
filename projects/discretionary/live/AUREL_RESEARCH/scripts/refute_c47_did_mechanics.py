# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-18 03:30 / 第 1 段]
対象 = cycle47（00:41）の **唯一の正の持ち越し**（主セルは既に null なので壊す余地なし）:
  補足 b（事後・判定外）の **DiD_W3 = ΔE_W3(ANN_J) − ΔE_W3(UJ) = 外 2021-26H1 +0.492（日cl t +2.5・MDE 0.39）／在 +0.073 (t 0.5)**
  と、そこから書かれた読み「**定時公表ジャンプは vol 状態を作り（ΔE_W3 外 +0.738 t 5.8・W4 +0.463 t 3.9）、予定外 5σ ジャンプは既に荒い状態の症状で状態を変えない（ΔE_W3 ≈0.00）**」。
  c47 自身の「最も重大な反証 (i)」は「水準 W3 は前状態が違うので同じ動学の証拠ではない・素直な定義は DiD」＝**DiD の側に正当性を置いた**。本反証はその逆を主張する。

=== 中心にある代替説明（= 壊しに行く仮説・数字を見る前に宣言） ===
H_MECH: **DiD は 2 腕の前状態 E_PRE が構造的に違うとき、機械的に ANN_J 有利へ偏る。**
  vol は平均回帰し、かつ E_PRE は 12 足の RV ＝ 潜在状態の極めてノイズの多い代理なので、
  非事象足でも  E_W3 = α + λ·E_PRE + u  の λ は 1 より**かなり小さい**。
  DiD（ΔE = E_W3 − E_PRE）は λ=1 を強制するので  E[ΔE | 腕] = α_腕 − (1−λ)·Ē_PRE(腕)  となり
      **DiD = (α_ANN − α_UJ) + (1−λ)·(Ē_PRE,UJ − Ē_PRE,ANN)**。
  c47 の実測は Ē_PRE,UJ − Ē_PRE,ANN = 外 **+0.555**（UJ +0.609・ANN_J +0.054）なので、
  λ が 0.1〜0.3 なら機械項だけで **+0.39〜+0.50** ＝ 観測された +0.492 の全部。
  さらに同じ機械項は **UJ の ΔE_W3 ≈ 0 を人工的に作る**（UJ の真の α_UJ > 0 でも −(1−λ)·0.609 で打ち消される）
  ＝ c47 の読みの**両方の脚**（ANN は状態を作る／UJ は作らない）が 1 つの推定器バイアスから出ている可能性。
  代数が正しければ、正しい仕様（レーン自身の方法論 57 候補 = **PRE を共変量にした水準**）では腕差が消えるはず。
  なお ΔE では σ_trail が完全に相殺する（ρ_k = log RV_k − 2log σ）ので、これは σ の人工物ではなく**平均回帰＋測定ノイズ**の話。

=== 事前固定（数字を見る前・この docstring が正本・破壊規則を先に宣言） ===
入力: data/c47_events_excess.csv（c47 の再利用キャッシュ 2214 事象・腕・E_PRE/W1..W4・ρ・対照 ρ）
      ＋ data/macro/XAU_m5_close.npz（λ の母集団推定・PRE2・一致プラセボ用）
      ＋ data/macro/FOMC_dates.csv・CPI_dates.csv・NFP c24 v2 規則（対照適格足の定義を c47 と一致させるため）
      ＋ data/c45_jumps_5sigma_declustered.csv（直前 4 h ジャンプ除外）。
      scan 無し・M5 読込なし・MT5 無し・外部通信無し・発注なし・本番編集なし。書き込みは AUREL_RESEARCH/ 配下のみ。
窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括は使わない）。推定器 = c47 と同一（log z＋ET 時刻 FE・ET 日クラスタ se）。
記号: D_level_k = 水準 E_k の ANN_J−UJ（c47 主表）・D_PRE = E_PRE の ANN_J−UJ・DiD_k = D_level_k − D_PRE（c47b）。

破壊規則（★=不発＝対象が生き残った / ☠=当たった）:
 R1 REPLICATE: c47b の DiD_W3（在 +0.073／外 +0.492）と c47 の D_PRE（外 −0.465）を |差| ≤ 0.01 で再現。
     再現しなければ以降の議論は無効（☠REPLICATE = c47b の数字が再現しない）。
 R2 BREAK-LAMBDA: 非事象足の母集団で λ を測る（npz・無作為 40000 適格足・ρ_W3 ~ ρ_PRE ＋ ET 時刻 FE・ET 日クラスタ）。
     **当たり条件 = λ < 0.5 ∧ t(λ−1) ≤ −5 ∧ 機械項 B = (1−λ)·(Ē_PRE,UJ − Ē_PRE,ANN) ≥ 0.5 · DiD_W3(外)**。
     副: キャッシュの対照平均（rc_W3 ~ rc_PRE）版 λ_rc・腕内 λ（UJ・ANN_J）・窓別 λ。
 R3 BREAK-COVADJ（本反証の主判定）: レーン自身の方法論 57 候補の仕様
     **E_W3 ~ 1{ANN_J} + E_PRE + log z + 時刻 FE（日クラスタ）** を走らせる。
     **当たり条件 = 外 β_ANN が |t| < 1.5 ∨ β_ANN < 0.5 · 0.492**（＝正しい仕様では DiD の読みを支えられない）。
     併記: λ̂（この仕様の E_PRE 係数）・D_adj = D_level − λ̂·D_PRE が DiD と λ=1 のどちらに近いか。
 R4 BREAK-PREMATCH: E_PRE 五分位（腕プール・窓内）を層 FE に入れて水準と DiD を再推定。
     **当たり条件 = 外 層内 DiD_W3 < 0.5 · 0.492 ∨ |t| < 1.5**。
 R5 BREAK-UJCAL: ANN_J の E_PRE 10–90 パーセンタイル帯に入る UJ だけに絞って（caliper）DiD_W3 を再計算。
     **当たり条件 = 外 caliper DiD_W3 < 0.5 · 0.492**。副: UJ の E_PRE 三分位別 ΔE_W3（c47b §3 の複製＝λ<1 の直接表示）。
 R6 BREAK-PLACEBO-DiD（最強の一致プラセボ・事象ゼロ）: npz の**非事象適格足**から偽腕を作る。
     偽 ANN_J／偽 UJ = 各実事象と**同じ ET 時**で ρ_PRE が ±0.15 以内の非事象足を 1 本無作為抽出（＝PRE の不均衡を完全に複製・ジャンプは無い）。
     偽腕で ρ ベース DiD_W3（= (ρ_W3−ρ_PRE) ~ treat + log z + 時刻 FE・日クラスタ）を NFAKE=200 回。
     **当たり条件 = 偽 DiD_W3(外) の平均 ≥ 0.5 · 実測 ρ ベース DiD_W3(外) ∨ 実測の片側経験 p > 0.05**。
     ＊ρ ベースで比べる理由: 偽足に K=4 対照を引き直すと数分かかる。ΔE と Δρ は対照の差分だけ違い、時刻一致の偽腕では
       その差分も一致するので、実測も偽も同じ ρ ベースで並べれば比較可能（実測の ΔE 版と Δρ 版の一致を印字して確認する）。
 R7 BREAK-MULTIPLE: c47b の DiD 表の family = 4 窓 × 3 窓期 × 2 対比（ANN_J−UJ／SJ−UJ）= **24 セル・全て事後**。
     外 W3 の名目 p に Holm 補正。**当たり条件 = Holm 調整後 p > 0.05**。
 R8（第 2 段・別 script）US500 の独立事象集合（c47 自身の復活条件）。
 R9（記述・判定外）λ のノイズ分解: PRE2 = 足 −24..−13 を E_PRE の操作変数にした λ_IV（測定ノイズ由来の減衰を除いた持続性）。
     λ_IV ≈ 1 なら「平均回帰ではなく測定ノイズ」・λ_IV < 1 なら両方。**どちらでも DiD の λ=1 は誤り**なので判定には使わない。
survived = R2〜R7 が全て不発。broken = R3（主判定）が当たり、かつ R2 か R6 がそれを機構として裏づけた場合。
seed 20261118。出力 data/refute_c47_did_mechanics.md。読取専用・発注なし・本番編集なし。
"""
import os, math, time, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c47_did_mechanics.md"); L = []
NY = "America/New_York"; SEED = 20261118; rng = np.random.default_rng(SEED)
W_SIG = 5520; NFAKE = 200; CAL = 0.15; NPOP = 40000
WINS = {"PRE": (-12, -1, 6), "PRE2": (-24, -13, 6), "W1": (1, 12, 6), "W2": (13, 24, 6), "W3": (25, 48, 12), "W4": (49, 96, 24)}
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
TARGET = 0.492  # c47b 外 DiD_W3（破壊規則の 0.5 倍閾値の基準・事前固定）

def say(s=""):
    print(s, flush=True); L.append(s)

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def dummies(vals, drop_first=True):
    u = sorted(pd.unique(vals))
    u = u[1:] if (drop_first and len(u) > 1) else (u if not drop_first else [])
    if not u: return np.zeros((len(vals), 0))
    return np.column_stack([(np.asarray(vals) == v).astype(float) for v in u])

def fit(o, ycol, treat, ctrlarm, extra=(), fe=("hr",), logz=True, cluster="day"):
    """y ~ 1 + 1{treat} + [extra cols] + log z + FE。戻り: beta_treat, se, 係数dict, n_t, n_c, G"""
    o = o[(o.cls == treat) | (o.cls == ctrlarm)]
    cols = [ycol] + list(extra) + (["logz"] if logz else [])
    o = o[np.isfinite(o[cols]).all(axis=1)]
    if (o.cls == treat).sum() < 5 or (o.cls == ctrlarm).sum() < 5:
        return np.nan, np.nan, {}, 0, 0, 0
    d = (o.cls == treat).to_numpy(float); y = o[ycol].to_numpy(float)
    parts = [np.ones(len(o)), d]
    names = ["const", "treat"]
    for c in extra:
        parts.append(o[c].to_numpy(float)); names.append(c)
    if logz:
        parts.append(o["logz"].to_numpy(float)); names.append("logz")
    for f in fe:
        H = dummies(o[f].to_numpy())
        if H.shape[1]: parts.append(H); names += [f"{f}_{j}" for j in range(H.shape[1])]
    X = np.column_stack(parts)
    beta, V, G = ols_cluster(y, X, o[cluster].to_numpy())
    se = math.sqrt(max(V[1, 1], 0))
    cf = {n: (beta[i], math.sqrt(max(V[i, i], 0))) for i, n in enumerate(names) if n in ("treat", "logz") or n in extra}
    return beta[1], se, cf, int((o.cls == treat).sum()), int((o.cls == ctrlarm).sum()), G

def tt(b, se): return (b / se) if (se and se > 0 and np.isfinite(se)) else float("nan")
def f2(b, se): return f"{b:+.3f} (t {tt(b,se):+.2f})"
def t0(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if len(x) < 3: return np.nan, np.nan, len(x)
    return x.mean(), x.mean() / (x.std(ddof=1) / math.sqrt(len(x))), len(x)
def pnorm2(t):
    return math.erfc(abs(t) / math.sqrt(2)) if np.isfinite(t) else float("nan")

say("# [REFUTE 2026-11-18 03:30 第1段] c47 の DiD_W3（外 +0.492 t 2.5）は推定器の機械的バイアスか")
say(f"- 事前固定 = docstring（破壊規則 R1〜R7 を数字を見る前に宣言）・seed {SEED}・主判定 = R3 BREAK-COVADJ")
say("")

# ================= 入力 =================
EV = pd.read_csv(os.path.join(DATA, "c47_events_excess.csv"))
EV["day"] = EV.et_date
for w in ["W1", "W2", "W3", "W4"]:
    EV["d" + w] = EV["E_" + w] - EV["E_PRE"]          # ΔE（c47b 定義）
    EV["dr" + w] = EV["rho_" + w] - EV["rho_PRE"]     # Δρ（対照を引かない版・σ_trail は相殺）
say(f"- c47 キャッシュ {len(EV)} 事象（ANN_J {(EV.cls=='ANN_J').sum()}／ANN_NJ {(EV.cls=='ANN_NJ').sum()}／UJ {(EV.cls=='UJ').sum()}／SJ {(EV.cls=='SJ').sum()}）")

def sub(lo, hi): return EV[(EV.year >= lo) & (EV.year <= hi)]

# ================= R1 REPLICATE =================
say("## R1 REPLICATE（c47b / c47 主表の再現）")
say("| 窓 | DiD_W3 ANN_J−UJ (t) | c47b | D_level_W3 (t) | c47 | D_PRE (t) | c47 | D_level−D_PRE |")
say("|---|---|---|---|---|---|---|---|")
REP = {"在 2010-20": (0.073, 0.076, -0.028), "外 2021-26H1": (0.492, 0.102, -0.465), "近年 2024-26H1": (0.700, 0.232, float("nan"))}
R1 = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    b_did, se_did, _, nt, nc, G = fit(o, "dW3", "ANN_J", "UJ")
    b_lev, se_lev, _, _, _, _ = fit(o, "E_W3", "ANN_J", "UJ")
    b_pre, se_pre, _, _, _, _ = fit(o, "E_PRE", "ANN_J", "UJ")
    r = REP[lab]
    say(f"| {lab} | **{f2(b_did,se_did)}** | {r[0]:+.3f} | {f2(b_lev,se_lev)} | {r[1]:+.3f} | {f2(b_pre,se_pre)} | {r[2]:+.3f} | {b_lev-b_pre:+.3f} |")
    R1[lab] = dict(did=b_did, se_did=se_did, lev=b_lev, se_lev=se_lev, pre=b_pre, se_pre=se_pre, nt=nt, nc=nc, G=G)
d_in, d_out = R1["在 2010-20"]["did"], R1["外 2021-26H1"]["did"]
rep_ok = (abs(d_in - 0.073) <= 0.01) and (abs(d_out - 0.492) <= 0.01)
say(f"- 腕別 Ē_PRE（外）: ANN_J {sub(2021,2026).query('cls==\"ANN_J\"').E_PRE.mean():+.3f}／UJ {sub(2021,2026).query('cls==\"UJ\"').E_PRE.mean():+.3f}"
    f"／差 **{sub(2021,2026).query('cls==\"UJ\"').E_PRE.mean()-sub(2021,2026).query('cls==\"ANN_J\"').E_PRE.mean():+.3f}**"
    f"（在 {sub(2010,2020).query('cls==\"UJ\"').E_PRE.mean()-sub(2010,2020).query('cls==\"ANN_J\"').E_PRE.mean():+.3f}）")
say(f"- **R1 判定: {'★不発（完全再現・以降の議論は有効）' if rep_ok else '☠REPLICATE が当たった（c47b が再現しない）'}**")
say("")

# ================= npz（λ 母集団・PRE2・プラセボ） =================
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
N = len(ts)
tt_ = pd.to_datetime(ts, unit="s", utc=True); tny = tt_.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yrs = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
r2 = np.where(nf, r * r, 0.0); c2 = np.r_[0.0, np.cumsum(r2)]; cn = np.r_[0, np.cumsum(nf.astype(np.int64))]
idx = np.arange(N)
lo_ = idx - 1 - W_SIG; hi_ = idx - 1
valid = (lo_ >= 0)
S2 = np.where(valid, c2[np.clip(hi_ + 1, 0, N)] - c2[np.clip(lo_ + 1, 0, N)], np.nan)
NN = np.where(valid, cn[np.clip(hi_ + 1, 0, N)] - cn[np.clip(lo_ + 1, 0, N)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
z = np.abs(r) / sig
say(f"- XAU_m5_close {N} 本 {tt_[0]}〜{tt_[-1]} UTC・flat {(~nf).mean()*100:.1f}%（衛生 ⑩⑪・c47 と同一前処理）")

def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d12 = pd.Timestamp(year=y, month=m, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
CPI = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
evdays = pd.DatetimeIndex(sorted(set(list(nfp_dates_v2().normalize()) + list(pd.DatetimeIndex(F.date).normalize()) + list(CPI.normalize()))))
isevbar = np.asarray(etdate.isin(evdays))
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
JC = pd.read_csv(os.path.join(DATA, "c45_jumps_5sigma_declustered.csv"))
J5 = np.sort(JC.ts.to_numpy(np.int64))
last_j = np.searchsorted(J5, ts, side="right") - 1
since_j = np.where(last_j >= 0, ts - J5[np.clip(last_j, 0, None)], 10 ** 9)
elig = nf & trading & ~isevbar & np.isfinite(sig) & (z < 5) & (since_j >= 14400)
say(f"- 対照適格足 {int(elig.sum())}（c47 と同一定義: 非 flat・取引時間・非事象日・z<5・直前 4 h ジャンプ無し）")

def win_logrv(ii, a, b, nmin):
    ii = np.asarray(ii, np.int64); out = np.full(len(ii), np.nan)
    ok = (ii + a >= 0) & (ii + b < N)
    s = c2[np.clip(ii + b + 1, 0, N)] - c2[np.clip(ii + a, 0, N)]
    n = cn[np.clip(ii + b + 1, 0, N)] - cn[np.clip(ii + a, 0, N)]
    good = ok & (n >= nmin) & (s > 0)
    out[good] = np.log(s[good] / n[good]); return out

RHO = {}
for w, (a, b, nmin) in WINS.items():
    RHO[w] = win_logrv(idx, a, b, nmin) - 2 * np.log(sig)

# ================= R2 BREAK-LAMBDA =================
say("## R2 BREAK-LAMBDA（非事象足の母集団で vol 状態の 2〜4 h 持続性 λ を測る）")
pool = idx[elig & np.isfinite(RHO["PRE"]) & np.isfinite(RHO["W3"]) & np.isfinite(RHO["PRE2"])]
LAM = {}
say("| 母集団 | 窓 | n | λ(ρ_W3 ~ ρ_PRE) | t(λ−1) | λ_W1 | λ_W4 | λ_IV（PRE2 を操作変数・R9） |")
say("|---|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    p = pool[(yrs[pool] >= lo) & (yrs[pool] <= hi)]
    if len(p) > NPOP: p = rng.choice(p, size=NPOP, replace=False)
    dd = pd.DataFrame({"y": RHO["W3"][p], "x": RHO["PRE"][p], "x2": RHO["PRE2"][p],
                       "y1": RHO["W1"][p], "y4": RHO["W4"][p], "hr": hr[p],
                       "day": etdate[p].strftime("%Y-%m-%d")})
    dd = dd[np.isfinite(dd[["y", "x", "x2", "y1", "y4"]]).all(axis=1)]
    H = dummies(dd.hr.to_numpy())
    def slope(ycol, xcol="x"):
        X = np.column_stack([np.ones(len(dd)), dd[xcol].to_numpy(), H])
        b, V, G = ols_cluster(dd[ycol].to_numpy(), X, dd.day.to_numpy())
        return b[1], math.sqrt(max(V[1, 1], 0))
    lam, se_l = slope("y"); lam1, _ = slope("y1"); lam4, _ = slope("y4")
    # IV（2SLS・PRE2 で PRE を予測 → λ_IV）: 手計算（同じ FE・日クラスタ）
    Xe = np.column_stack([np.ones(len(dd)), H])
    Me = np.eye(len(dd)) - Xe @ np.linalg.pinv(Xe.T @ Xe) @ Xe.T if len(dd) < 4000 else None
    if Me is None:
        def resid(v):
            B = np.column_stack([np.ones(len(dd)), H]); bb = np.linalg.pinv(B.T @ B) @ (B.T @ v); return v - B @ bb
        yr_, xr_, zr_ = resid(dd.y.to_numpy()), resid(dd.x.to_numpy()), resid(dd.x2.to_numpy())
    else:
        yr_, xr_, zr_ = Me @ dd.y.to_numpy(), Me @ dd.x.to_numpy(), Me @ dd.x2.to_numpy()
    lam_iv = (zr_ @ yr_) / (zr_ @ xr_)
    LAM[lab] = dict(lam=lam, se=se_l, lam_iv=lam_iv, n=len(dd))
    say(f"| 非事象適格足 | {lab} | {len(dd)} | **{lam:+.3f}** (se {se_l:.3f}) | {(lam-1)/se_l:+.1f} | {lam1:+.3f} | {lam4:+.3f} | {lam_iv:+.3f} |")
# キャッシュの対照平均版（K=4 平均なのでノイズが小さい＝λ は上がる方向）
for lab, lo, hi in ERAS[:2]:
    o = sub(lo, hi); o = o[np.isfinite(o[["rc_PRE", "rc_W3"]]).all(axis=1)]
    H = dummies(o.hr.to_numpy())
    X = np.column_stack([np.ones(len(o)), o.rc_PRE.to_numpy(), H])
    b, V, G = ols_cluster(o.rc_W3.to_numpy(), X, o.day.to_numpy())
    say(f"| 対照 K=4 平均（rc・ノイズ小） | {lab} | {len(o)} | {b[1]:+.3f} (se {math.sqrt(V[1,1]):.3f}) | {(b[1]-1)/math.sqrt(V[1,1]):+.1f} | — | — | — |")
# 腕内 λ（事象腕・E ベース）
say("")
say("| 腕内 λ（E_W3 ~ E_PRE・時刻 FE・日cl） | 在 | 外 |")
say("|---|---|---|")
for arm in ["UJ", "ANN_J", "SJ"]:
    cells = []
    for lab, lo, hi in ERAS[:2]:
        o = sub(lo, hi); o = o[(o.cls == arm) & np.isfinite(o[["E_PRE", "E_W3"]]).all(axis=1)]
        H = dummies(o.hr.to_numpy())
        X = np.column_stack([np.ones(len(o)), o.E_PRE.to_numpy(), H])
        b, V, G = ols_cluster(o.E_W3.to_numpy(), X, o.day.to_numpy())
        cells.append(f"{b[1]:+.3f} (t(λ−1) {(b[1]-1)/math.sqrt(max(V[1,1],1e-12)):+.1f}・n {len(o)})")
    say(f"| {arm} | " + " | ".join(cells) + " |")
lam_out = LAM["外 2021-26H1"]["lam"]; se_out = LAM["外 2021-26H1"]["se"]
dpre_out = sub(2021, 2026).query('cls=="UJ"').E_PRE.mean() - sub(2021, 2026).query('cls=="ANN_J"').E_PRE.mean()
B_mech = (1 - lam_out) * dpre_out
r2_hit = (lam_out < 0.5) and ((lam_out - 1) / se_out <= -5) and (B_mech >= 0.5 * TARGET)
say("")
say(f"- 機械項の予測 B = (1−λ)·(Ē_PRE,UJ − Ē_PRE,ANN) = (1−{lam_out:.3f})·{dpre_out:+.3f} = **{B_mech:+.3f}**  vs 実測 DiD_W3(外) {d_out:+.3f}"
    f"（説明率 {100*B_mech/d_out:.0f}%）")
say(f"- **R2 判定: {'☠BREAK-LAMBDA が当たった' if r2_hit else '★不発'}** [λ<0.5 → {lam_out<0.5} / t(λ−1)≤−5 → {(lam_out-1)/se_out<=-5} / B ≥ 0.5·{TARGET} → {B_mech>=0.5*TARGET}]")
say("")

# ================= R3 BREAK-COVADJ（主判定） =================
say("## R3 BREAK-COVADJ（主判定・方法論 57 候補の仕様: PRE を共変量にした水準）")
say("| 窓 | k | DiD（λ=1 強制） | 水準のみ（PRE 無視） | **PRE 共変量（正しい仕様）β_ANN (t)** | λ̂（E_PRE 係数） | MDE 2se | D_adj = D_lev − λ̂·D_PRE |")
say("|---|---|---|---|---|---|---|---|")
R3 = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    b_pre, se_pre, _, _, _, _ = fit(o, "E_PRE", "ANN_J", "UJ")
    for w in ["W1", "W2", "W3", "W4"]:
        b_did, se_did, _, _, _, _ = fit(o, "d" + w, "ANN_J", "UJ")
        b_lev, se_lev, _, _, _, _ = fit(o, "E_" + w, "ANN_J", "UJ")
        b_adj, se_adj, cf, nt, nc, G = fit(o, "E_" + w, "ANN_J", "UJ", extra=("E_PRE",))
        lh, lhse = cf.get("E_PRE", (np.nan, np.nan))
        say(f"| {lab} | {w} | {f2(b_did,se_did)} | {f2(b_lev,se_lev)} | **{f2(b_adj,se_adj)}** | {lh:+.3f} (t(λ−1) {(lh-1)/lhse:+.1f}) | {2*se_adj:.3f} | {b_lev-lh*b_pre:+.3f} |")
        R3[(lab, w)] = (b_adj, se_adj, lh)
b3, se3, lh3 = R3[("外 2021-26H1", "W3")]
r3_hit = (abs(tt(b3, se3)) < 1.5) or (b3 < 0.5 * TARGET)
say(f"- **R3 判定: {'☠BREAK-COVADJ が当たった（正しい仕様で DiD の読みは支えられない）' if r3_hit else '★不発（PRE 調整後も腕差は残る）'}**"
    f" [外 β_ANN {b3:+.3f}・t {tt(b3,se3):+.2f} → |t|<1.5 {abs(tt(b3,se3))<1.5} / β<0.5·{TARGET}={0.5*TARGET:.3f} → {b3<0.5*TARGET}]")
say("- 併記: 各腕の『状態を作ったか』を正しい仕様で（E_k ~ E_PRE ＋ 時刻 FE の腕内切片 α_腕 ＝ PRE を揃えた上での超過水準）")
say("| 窓 | 腕 | n | ΔE_W3（λ=1・c47b） | α_W3（PRE 共変量・0 との t） | λ̂_腕 |")
say("|---|---|---|---|---|---|")
for lab, lo, hi in ERAS[:2]:
    for arm in ["ANN_J", "UJ", "SJ"]:
        o = sub(lo, hi); o = o[(o.cls == arm) & np.isfinite(o[["E_PRE", "E_W3", "dW3"]]).all(axis=1)]
        if len(o) < 10: continue
        H = dummies(o.hr.to_numpy())
        X = np.column_stack([np.ones(len(o)), o.E_PRE.to_numpy(), H])
        b, V, G = ols_cluster(o.E_W3.to_numpy(), X, o.day.to_numpy())
        # α_腕 = 平均 E_PRE で評価した切片（＝PRE を全腕共通値 0 に揃えたときの水準）
        a_hat = b[0]; se_a = math.sqrt(max(V[0, 0], 0))
        m_, t_, n_ = t0(o.dW3)
        say(f"| {lab} | {arm} | {len(o)} | {m_:+.3f} (t {t_:+.1f}) | **{a_hat:+.3f} (t {tt(a_hat,se_a):+.2f})** | {b[1]:+.3f} |")
say("")

# ================= R4 BREAK-PREMATCH =================
say("## R4 BREAK-PREMATCH（E_PRE 五分位を層 FE に入れる）")
say("| 窓 | 層内 DiD_W3 (t) | 層内 水準 D_W3 (t) | 層数 | n ANN_J / UJ | 層別 DiD_W3（五分位ごと・記述） |")
say("|---|---|---|---|---|---|")
R4 = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi).copy()
    o = o[o.cls.isin(["ANN_J", "UJ"]) & np.isfinite(o[["E_PRE", "E_W3", "dW3"]]).all(axis=1)]
    q = o.E_PRE.quantile([.2, .4, .6, .8]).to_numpy()
    o["q"] = np.digitize(o.E_PRE.to_numpy(), q)
    b_did, se_did, _, nt, nc, G = fit(o, "dW3", "ANN_J", "UJ", fe=("hr", "q"))
    b_lev, se_lev, _, _, _, _ = fit(o, "E_W3", "ANN_J", "UJ", fe=("hr", "q"))
    per = []
    for qq in range(5):
        s = o[o.q == qq]
        if (s.cls == "ANN_J").sum() >= 5 and (s.cls == "UJ").sum() >= 5:
            bq, seq, _, _, _, _ = fit(s, "dW3", "ANN_J", "UJ")
            per.append(f"Q{qq+1} {bq:+.2f}({tt(bq,seq):+.1f})")
        else:
            per.append(f"Q{qq+1} n不足")
    say(f"| {lab} | **{f2(b_did,se_did)}** | {f2(b_lev,se_lev)} | 5 | {nt} / {nc} | " + "・".join(per) + " |")
    R4[lab] = (b_did, se_did)
b4, se4 = R4["外 2021-26H1"]
r4_hit = (b4 < 0.5 * TARGET) or (abs(tt(b4, se4)) < 1.5)
say(f"- **R4 判定: {'☠BREAK-PREMATCH が当たった' if r4_hit else '★不発'}** [外 {b4:+.3f} t {tt(b4,se4):+.2f}]")
say("")

# ================= R5 BREAK-UJCAL =================
say("## R5 BREAK-UJCAL（ANN_J の E_PRE 10–90 % 帯に入る UJ だけ・caliper）")
say("| 窓 | ANN_J E_PRE 帯 | caliper 後 UJ n | caliper DiD_W3 (t) | caliper 水準 D_W3 (t) | 全 UJ DiD_W3 |")
say("|---|---|---|---|---|---|")
R5 = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    a = o[(o.cls == "ANN_J") & np.isfinite(o.E_PRE)]
    q10, q90 = a.E_PRE.quantile([.1, .9]).to_numpy()
    keep = o[(o.cls == "ANN_J") | ((o.cls == "UJ") & (o.E_PRE >= q10) & (o.E_PRE <= q90))]
    b_did, se_did, _, nt, nc, G = fit(keep, "dW3", "ANN_J", "UJ")
    b_lev, se_lev, _, _, _, _ = fit(keep, "E_W3", "ANN_J", "UJ")
    say(f"| {lab} | [{q10:+.2f}, {q90:+.2f}] | {nc} | **{f2(b_did,se_did)}** | {f2(b_lev,se_lev)} | {R1[lab]['did']:+.3f} |")
    R5[lab] = (b_did, se_did)
b5, se5 = R5["外 2021-26H1"]
r5_hit = b5 < 0.5 * TARGET
say(f"- **R5 判定: {'☠BREAK-UJCAL が当たった' if r5_hit else '★不発'}** [外 caliper {b5:+.3f} < 0.5·{TARGET}={0.5*TARGET:.3f} → {r5_hit}]")
say("- 副: UJ の E_PRE 三分位別 ΔE_W3（λ<1 の直接表示・c47b §3 複製）")
say("| 窓 | 層 | n | Ē_PRE | ΔE_W3 (t) | E_W3 水準 | ANN_J 参照 ΔE_W3 |")
say("|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS[:2]:
    o = sub(lo, hi); u = o[(o.cls == "UJ") & np.isfinite(o[["E_PRE", "dW3"]]).all(axis=1)]
    a = o[(o.cls == "ANN_J") & np.isfinite(o.dW3)]
    q = u.E_PRE.quantile([1/3, 2/3]).to_numpy()
    for nm, m in [("静 T1", u.E_PRE <= q[0]), ("中 T2", (u.E_PRE > q[0]) & (u.E_PRE <= q[1])), ("荒 T3", u.E_PRE > q[1])]:
        s = u[m]
        say(f"| {lab} | {nm} | {len(s)} | {s.E_PRE.mean():+.3f} | {t0(s.dW3)[0]:+.3f} ({t0(s.dW3)[1]:+.1f}) | {s.E_W3.mean():+.3f} | {t0(a.dW3)[0]:+.3f}（Ē_PRE {a.E_PRE.mean():+.3f}） |")
say("")

# ================= R6 BREAK-PLACEBO-DiD =================
say("## R6 BREAK-PLACEBO-DiD（事象ゼロの一致プラセボ: 同 ET 時 × ρ_PRE ±0.15 の非事象足で偽腕を作る）")
# 実測の ρ ベース DiD（ΔE 版との一致確認）
say("| 窓 | 実測 ΔE 版 DiD_W3 | 実測 Δρ 版 DiD_W3 | 偽腕 Δρ 版 平均 (sd) | 超過（実測−偽平均） | 片側経験 p | 偽腕の Ē_PRE 差 |")
say("|---|---|---|---|---|---|---|")
# ρ_PRE のスロット別候補索引（ET 時ごと）
elig_pre = elig & np.isfinite(RHO["PRE"]) & np.isfinite(RHO["W3"])
by_hr = {}
for h in range(24):
    a = idx[elig_pre & (hr == h)]
    if len(a): by_hr[h] = (a, RHO["PRE"][a], np.argsort(RHO["PRE"][a]))
R6 = {}
for lab, lo, hi in ERAS[:2]:
    o = sub(lo, hi)
    o = o[o.cls.isin(["ANN_J", "UJ"]) & np.isfinite(o[["drW3", "dW3", "rho_PRE"]]).all(axis=1)].copy()
    b_de, se_de, _, _, _, _ = fit(o, "dW3", "ANN_J", "UJ")
    b_dr, se_dr, _, nt, nc, G = fit(o, "drW3", "ANN_J", "UJ")
    # 候補集合（事象ごと・同 ET 時・ρ_PRE caliper・同年代に限らない＝母集団全体）
    cand = []
    for _, row in o.iterrows():
        h = int(row.hr)
        if h not in by_hr: cand.append(np.array([], np.int64)); continue
        arr, pv, srt = by_hr[h]
        aa, bb = np.searchsorted(pv[srt], row.rho_PRE - CAL), np.searchsorted(pv[srt], row.rho_PRE + CAL, side="right")
        cand.append(arr[srt[aa:bb]])
    nc_ok = np.array([len(c) for c in cand])
    bs = np.full(NFAKE, np.nan); dpres = np.full(NFAKE, np.nan)
    treat = (o.cls == "ANN_J").to_numpy()
    for q in range(NFAKE):
        pick = np.array([(c[rng.integers(len(c))] if len(c) else -1) for c in cand])
        ok = pick >= 0
        if ok.sum() < 30: continue
        p_ = pick[ok]
        dd = pd.DataFrame({"y": RHO["W3"][p_] - RHO["PRE"][p_], "logz": o.logz.to_numpy()[ok],
                           "hr": hr[p_], "day": etdate[p_].strftime("%Y-%m-%d"),
                           "cls": np.where(treat[ok], "ANN_J", "UJ"), "rp": RHO["PRE"][p_]})
        dd = dd[np.isfinite(dd.y)]
        bq, seq, _, n1, n2, _ = fit(dd, "y", "ANN_J", "UJ")
        bs[q] = bq
        dpres[q] = dd.query('cls=="UJ"').rp.mean() - dd.query('cls=="ANN_J"').rp.mean()
    bsv = bs[np.isfinite(bs)]
    p_emp = float((bsv >= b_dr).mean()) if len(bsv) else float("nan")
    say(f"| {lab} | {b_de:+.3f} (t {tt(b_de,se_de):+.2f}) | {b_dr:+.3f} (t {tt(b_dr,se_dr):+.2f}) | **{bsv.mean():+.3f}** ({bsv.std(ddof=1):.3f}・{len(bsv)} 回) | "
        f"{b_dr-bsv.mean():+.3f} | **{p_emp:.4f}** | {np.nanmean(dpres):+.3f}（実 {o.query('cls=="UJ"').rho_PRE.mean()-o.query('cls=="ANN_J"').rho_PRE.mean():+.3f}） |")
    R6[lab] = (b_dr, bsv.mean(), p_emp, len(bsv))
    if lab == "外 2021-26H1":
        say(f"- 候補数（外・事象あたり）中央値 {np.median(nc_ok):.0f}・候補 0 の事象 {(nc_ok==0).sum()}／{len(nc_ok)}")
b_dr_o, fk_o, p_o, nfk = R6["外 2021-26H1"]
r6_hit = (fk_o >= 0.5 * b_dr_o) or (p_o > 0.05)
say(f"- **R6 判定: {'☠BREAK-PLACEBO-DiD が当たった' if r6_hit else '★不発'}** [偽平均 {fk_o:+.3f} ≥ 0.5·実測 {0.5*b_dr_o:+.3f} → {fk_o>=0.5*b_dr_o} / 経験 p {p_o:.4f} > 0.05 → {p_o>0.05}]")
say("")

# ================= R7 BREAK-MULTIPLE =================
say("## R7 BREAK-MULTIPLE（c47b の DiD 表 family = 4 窓 × 3 窓期 × 2 対比 = 24 セル・全て事後）")
fam = []
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    for w in ["W1", "W2", "W3", "W4"]:
        for tr_, ct_ in [("ANN_J", "UJ"), ("SJ", "UJ")]:
            b_, se_, _, _, _, _ = fit(o, "d" + w, tr_, ct_)
            fam.append((f"{lab}/{w}/{tr_}−{ct_}", b_, se_, pnorm2(tt(b_, se_))))
fam_df = pd.DataFrame(fam, columns=["cell", "b", "se", "p"]).dropna()
fam_df = fam_df.sort_values("p").reset_index(drop=True)
m = len(fam_df)
fam_df["holm"] = np.maximum.accumulate(np.minimum(1.0, (m - fam_df.index.to_numpy()) * fam_df.p.to_numpy()))
fam_df["bh"] = np.minimum(1.0, fam_df.p.to_numpy() * m / (fam_df.index.to_numpy() + 1))
say(f"- family {m} セル・名目 p<0.05 は {(fam_df.p<0.05).sum()} 本")
say("| 順位 | セル | β (t) | 名目 p | Holm | BH |")
say("|---|---|---|---|---|---|")
for i, row in fam_df.head(8).iterrows():
    say(f"| {i+1} | {row.cell} | {row.b:+.3f} ({tt(row.b,row.se):+.2f}) | {row.p:.4f} | {row.holm:.4f} | {row.bh:.4f} |")
tgt = fam_df[fam_df.cell == "外 2021-26H1/W3/ANN_J−UJ"]
holm_t = float(tgt.holm.iloc[0]); bh_t = float(tgt.bh.iloc[0]); p_t = float(tgt.p.iloc[0])
r7_hit = holm_t > 0.05
say(f"- 対象セル（外/W3/ANN_J−UJ）: 名目 p {p_t:.4f} → **Holm {holm_t:.4f}**・BH {bh_t:.4f}（順位 {int(tgt.index[0])+1}/{m}）")
say(f"- **R7 判定: {'☠BREAK-MULTIPLE が当たった' if r7_hit else '★不発'}**")
say("")

# ================= まとめ =================
say("## 第 1 段まとめ")
hits = [("R1 REPLICATE", not rep_ok), ("R2 BREAK-LAMBDA", r2_hit), ("R3 BREAK-COVADJ（主判定）", r3_hit),
        ("R4 BREAK-PREMATCH", r4_hit), ("R5 BREAK-UJCAL", r5_hit), ("R6 BREAK-PLACEBO-DiD", r6_hit), ("R7 BREAK-MULTIPLE", r7_hit)]
for nm, h in hits:
    say(f"- {'☠ 当たり' if h else '★ 不発'} {nm}")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
