# -*- coding: utf-8 -*-
"""
[cycle47 研究レーン / 2026-11-18]【深化・機構（c45/c46 の残問）→ 市場構造（§8 マクロ発表行の機構欄）】
問い: 5σ の 5 分ジャンプの後、超過ボラ（同時刻・非事象日の対照に対する log RV 比）は、
      ジャンプが「定時公表の公表足」（NFP 08:30／FOMC 14:00（2013-03-20+）／CPI 08:30 ET・公表足 |r|≥5σ = ANN_J）のとき、
      予定外ジャンプ（UJ・c45 定義: 非発表日・足開始分 ∉ {00,15,30,45}）より速く減衰するか。
文献（記憶・外部通信なし）: Ederington–Lee 1993 JF（定時マクロ公表後のボラは 15 分で大半が解消・数時間は高止まり）／
      Andersen–Bollerslev 1998（公表効果は短命・日内周期が支配的）。機構: 定時公表は「既知の不確実性の解消」＝情報が処理されるとボラは戻る。
      予定外ジャンプは「未知の新情報／流動性の消失」＝価格発見が続きボラが持続する（仮説）。
なぜ我々に要るか: c45/c46 は「NFP/FOMC 公表後 0〜4 h の時計」に +0.5R（外）を残し、機構は未同定（ジャンプ一般でも予定公表一般でもない）。
      c44 在の post-announcement drift β +0.19 と「ボラが速く戻る」が同時なら drift/vol 比が上がり TP 到達に有利＝path 機構の候補。
      UJ は同じ大きさ・同じ幾何（c45）なのに null → 「事象後の vol path」が 2 腕で違うかは未検定。

=== 事前固定（数字を見る前・この docstring が正本） ===
データ: data/macro/XAU_m5_close.npz（bid・完全格子・前値埋め）／data/c45_jumps_5sigma_declustered.csv（UJ/SJ 事象・4 h decluster = 先着を採用）／
      data/macro/FOMC_dates.csv・CPI_dates.csv／NFP = c24 v2 規則／補⑤のみ data/refute_c4_scan_paths_2010_2026.json。scan 無し・M5 読込なし・MT5 無し・外部通信無し。
窓 = 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・16 年一括は使わない）。
ジャンプ・σ: c45 と同一（r bp・σ_trail = 直前 5520 足の非 flat RMS・足自身を含まない・z=|r|/σ）。
事象集合（互いに排反・t0 = 公表足／ジャンプ足の開始）:
  ANN_J = NFP/FOMC/CPI の公表足で z≥5（主腕・方法論 54: UJ と同じ検出器を通す）。ANN_NJ = 同 z<5（記述）。
  UJ = c45 cls UJ（主対照腕）。SJ = c45 cls SJ（副腕: 他の定時スロット）。
超過ボラ: 窓 k の RV_k = mean(r²) over 非 flat 足（PRE = 足 −12..−1／W1 = 足 1..12／W2 = 13..24／W3 = 25..48／W4 = 49..96・足 0 = ジャンプ足は除外）、
      最低非 flat 足数 6/6/6/12/24。ρ_k = log(RV_k / σ_trail²(t0))。
      対照 = 同 ET 時:分・月〜金・±28 暦日・非 NFP/FOMC/CPI 日・足 非 flat ∧ z<5 ∧ 直前 4 h に declustered 5σ ジャンプ無し・K=4 無作為（seed）。
      E_k = ρ_k(事象) − mean_K ρ_k(対照)（対照 ≥2 本が条件）。同時刻対照なので日内周期・17:00 ブレイクは相殺。
推定: E_k ~ 1{ANN_J} + log z + ET 時刻 FE（t0 の時）on ANN_J ∪ UJ、ET 日クラスタ se。D_k = β_ANN_J。未調整 Welch も印字。
判定（主セル 1 = D_W3・両側事前宣言）:
   H_DECAY  PASS = D_W3 < 0 ∧ 在 t ≤ −2 ∧ 外 同符号 t ≤ −1.5（公表後はボラが速く戻る）。
   H_PERSIST PASS = D_W3 > 0 ∧ 在 t ≥ 2 ∧ 外 t ≥ 1.5（公表後の方がボラが持続）。
   どちらでもなければ null（MDE = 2se を印字）。校正 = 時刻層内ラベル置換 2000 回の経験 p（在・外）。
副（記述）: W1/W2/W4/PRE・減衰勾配 E_W1−E_W3・SJ 腕・ANN_NJ・ANN 種別別・z 層（5–7／>7）・年別・
   感度 = 足 1 も除外（W1' = 2..12）／中央値版（Mann–Whitney）／±7 日偽事象（E≈0 の sanity）／
   陽性対照 = UJ の W3 の r を ×1.15（E_W3 +0.28 注入）で t がどれだけ動くか。
補⑤（戦略への接続・記述・判定外）: scan 本（c45 の ANN 0〜4 h／UJ 窓／ctrl 定義）の建玉後 12 足の path 粗さ
   ρ_e = log(RV(e+1..e+12)/σ_trail²(e)) を時刻 FE・日クラスタで腕差（「発表後の本は静かな path を歩くか」）。
決着可能性（事前）: E_k の事象間 sd を 0.5〜0.7 と仮定、ANN_J 在 ≈150／外 ≈100・UJ 在 ≈600／外 ≈330 → se ≈0.06／0.075 → MDE ≈0.12〜0.15（log・vol で 6〜8%）。
   文献級（公表後 2〜4 h で 1.2〜1.5× vs 直後 3×）なら腕差 0.2〜0.4 log＝決着可。
事前の最重大反証: (i) bid のみ＝予定外ジャンプは気配飛び（スプレッド正常化）を含み UJ の直後 RV を人工的に膨らませる → H_DECAY 側に偏る（感度: 足 1 除外・中央値版）。
   (ii) UJ の分規則は 08:30 系公表（PPI・小売・失業保険）の第 2 波を含む＝UJ が ANN に寄る（H_DECAY に保守的）。
   (iii) 公表後の窓に他の定時公表（10:00 ET）が入る＝同時刻対照にも入るので相殺するが、公表日は反応が大きい可能性（非対称）。
   (iv) decluster は先着採用＝事象後の窓に後続ジャンプが入り得る（両腕同じ）。(v) 多重検定: 判定セル 1（D_W3）・残りは記述。(vi) 1 社 CFD。
seed 20261118。出力 data/c47_post_jump_vol_decay_result.md。読取専用・発注なし・本番編集なし。
"""
import os, json, math, time, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
try:
    from scipy import stats as st
except Exception:  # fallback (venv に scipy が無い場合): 正規近似 Mann–Whitney と順位相関
    class _St:
        class _R:
            def __init__(self, s, p): self.statistic, self.pvalue = s, p
        @staticmethod
        def mannwhitneyu(a, b, alternative="two-sided"):
            a, b = np.asarray(a, float), np.asarray(b, float); n1, n2 = len(a), len(b)
            rk = pd.Series(np.r_[a, b]).rank().to_numpy(); U = rk[:n1].sum() - n1 * (n1 + 1) / 2
            mu, sd = n1 * n2 / 2, math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12); zz_ = (U - mu) / sd
            return _St._R(U, math.erfc(abs(zz_) / math.sqrt(2)))
        @staticmethod
        def spearmanr(a, b):
            ra, rb = pd.Series(np.asarray(a, float)).rank().to_numpy(), pd.Series(np.asarray(b, float)).rank().to_numpy()
            rho = np.corrcoef(ra, rb)[0, 1]; n = len(ra); t_ = rho * math.sqrt(max(n - 2, 1) / max(1 - rho * rho, 1e-12))
            return _St._R(rho, math.erfc(abs(t_) / math.sqrt(2)))
    st = _St()

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c47_post_jump_vol_decay_result.md"); L = []
NY = "America/New_York"; SEED = 20261118; rng = np.random.default_rng(SEED)
W_SIG = 5520; K_CTRL = 4; DAYS = 28; NPERM = 2000
WINS = {"PRE": (-12, -1, 6), "W1": (1, 12, 6), "W2": (13, 24, 6), "W3": (25, 48, 12), "W4": (49, 96, 24), "W1b": (2, 12, 6)}
WD = "月火水木金土日"
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def say(s=""):
    print(s, flush=True); L.append(s)

def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

say("# [cycle47] 5σ ジャンプ後の超過ボラの減衰: 定時公表（ANN_J）vs 予定外（UJ）")
say(f"- 事前固定は docstring・seed {SEED}・主セル = D_W3（E_W3 の ANN_J − UJ・log z＋時刻 FE・日クラスタ）")
say("")

# ---------- 暦 ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

# ---------- npz ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
N = len(ts)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yrs = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
say(f"- XAU_m5_close: {N} 本 {tt[0]}〜{tt[-1]} UTC（⑩）・flat 全体 {(~nf).mean()*100:.1f}%・曜日別 " +
    " ".join(f"{WD[w]}{(~nf[wd==w]).mean()*100:.1f}%" for w in range(7)) + "（⑪）")
r2 = np.where(nf, r * r, 0.0); c2 = np.r_[0.0, np.cumsum(r2)]; cn = np.r_[0, np.cumsum(nf.astype(np.int64))]
idx = np.arange(N)
lo = idx - 1 - W_SIG; hi = idx - 1
valid = (lo >= 0)
S2 = np.where(valid, c2[np.clip(hi + 1, 0, N)] - c2[np.clip(lo + 1, 0, N)], np.nan)
NN = np.where(valid, cn[np.clip(hi + 1, 0, N)] - cn[np.clip(lo + 1, 0, N)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
z = np.abs(r) / sig
isevbar = np.asarray(etdate.isin(evdays))
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))

def win_logrv(ii, a, b, nmin):
    """log mean r² over bars [ii+a, ii+b] (非 flat のみ)・NaN if N<nmin or out of range"""
    ii = np.asarray(ii, np.int64); out = np.full(len(ii), np.nan)
    ok = (ii + a >= 0) & (ii + b < N)
    s = c2[np.clip(ii + b + 1, 0, N)] - c2[np.clip(ii + a, 0, N)]
    n = cn[np.clip(ii + b + 1, 0, N)] - cn[np.clip(ii + a, 0, N)]
    good = ok & (n >= nmin) & (s > 0)
    out[good] = np.log(s[good] / n[good]); return out

# ---------- 事象 ----------
JC = pd.read_csv(os.path.join(DATA, "c45_jumps_5sigma_declustered.csv"))
pos = np.searchsorted(ts, JC.ts.to_numpy(np.int64)); pos = np.clip(pos, 0, N - 1)
assert (ts[pos] == JC.ts.to_numpy()).all(), "cache ts ↔ npz 不一致"
JC["idx"] = pos
chk = np.abs(z[pos] - JC.z.to_numpy()); say(f"- c45 キャッシュ {len(JC)} 事象・z 再計算との最大差 {np.nanmax(chk):.3f}（規約一致の確認）")
J5_ts = np.sort(JC.ts.to_numpy(np.int64))

def ann_bars(dates, h, m, kind):
    t = epoch_et(dates, h, m); t = t[np.isfinite(t)].astype(np.int64)
    p = np.clip(np.searchsorted(ts, t), 0, N - 1); ok = ts[p] == t
    return pd.DataFrame({"idx": p[ok], "kind": kind})
A = pd.concat([ann_bars(NFP, 8, 30, "NFP"), ann_bars(FOMC_ANN, 14, 0, "FOMC"), ann_bars(CPI, 8, 30, "CPI")], ignore_index=True)
A = A[A.idx.map(lambda i: np.isfinite(sig[i]) and nf[i])].copy()
A["z"] = z[A.idx.to_numpy()]
A["cls"] = np.where(A.z >= 5, "ANN_J", "ANN_NJ")
U = JC[JC.cls.isin(["UJ", "SJ"])][["idx", "cls", "z"]].copy(); U["kind"] = U.cls
EV = pd.concat([A[["idx", "kind", "cls", "z"]], U[["idx", "kind", "cls", "z"]]], ignore_index=True)
EV["ts"] = ts[EV.idx]; EV["hr"] = hr[EV.idx]; EV["mn"] = mn[EV.idx]; EV["year"] = yrs[EV.idx]; EV["day"] = etdate[EV.idx.to_numpy()]
EV["r"] = r[EV.idx]; EV["logz"] = np.log(EV.z.clip(lower=0.1))
say("| 窓 | ANN_J（NFP／FOMC／CPI） | ANN_NJ | UJ | SJ | ANN_J z 中央値 | UJ z 中央値 | ANN_J |r| 中央値 bp | UJ |r| 中央値 |")
say("|---|---|---|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    e = EV[(EV.year >= lo_) & (EV.year <= hi_)]
    aj = e[e.cls == "ANN_J"]; uj = e[e.cls == "UJ"]
    say(f"| {lab} | {len(aj)}（{(aj.kind=='NFP').sum()}／{(aj.kind=='FOMC').sum()}／{(aj.kind=='CPI').sum()}） | {(e.cls=='ANN_NJ').sum()} | {len(uj)} | {(e.cls=='SJ').sum()} | "
        f"{aj.z.median():.2f} | {uj.z.median():.2f} | {np.abs(aj.r).median():.1f} | {np.abs(uj.r).median():.1f} |")
say("- UJ の ET 時刻分布: " + " ".join(f"{h}:{c}" for h, c in EV[EV.cls=='UJ'].hr.value_counts().sort_index().items()))
say("")

# ---------- 対照（同 ET 時:分・±28 日・非事象日・静かな前 4 h） ----------
last_j = np.searchsorted(J5_ts, ts, side="right") - 1
since_j = np.where(last_j >= 0, ts - J5_ts[np.clip(last_j, 0, None)], 10**9)
elig = nf & trading & ~isevbar & np.isfinite(sig) & (z < 5) & (since_j >= 14400)
slot = hr * 60 + mn
slot_idx = {}
for s_ in np.unique(slot[elig]):
    slot_idx[s_] = idx[elig & (slot == s_)]
say(f"- 対照候補足 {elig.sum()}（非 flat・取引時間・非事象日・z<5・直前 4 h ジャンプ無し）")

def draw_ctrl(ev_idx, K=K_CTRL):
    out = np.full((len(ev_idx), K), -1, np.int64); ncand = np.zeros(len(ev_idx), int)
    for n_, i in enumerate(ev_idx):
        arr = slot_idx.get(slot[i])
        if arr is None: continue
        t_i = ts[i]; a = np.searchsorted(ts[arr], t_i - DAYS * 86400); b = np.searchsorted(ts[arr], t_i + DAYS * 86400, side="right")
        cand = arr[a:b]; cand = cand[cand != i]; ncand[n_] = len(cand)
        if len(cand) == 0: continue
        pick = rng.choice(cand, size=min(K, len(cand)), replace=False); out[n_, :len(pick)] = pick
    return out, ncand

C_IDX, NCAND = draw_ctrl(EV.idx.to_numpy())
EV["ncand"] = NCAND
say(f"- 対照候補数 中央値 {np.median(NCAND):.0f}・<2 本の事象 {(NCAND<2).sum()}・K=4 確保率 {(NCAND>=4).mean()*100:.1f}%")

def excess(ev_idx, c_idx, a, b, nmin, scale=None):
    rho_e = win_logrv(ev_idx, a, b, nmin) - 2 * np.log(sig[ev_idx])
    if scale is not None: rho_e = rho_e + scale
    rc = np.full(c_idx.shape, np.nan)
    for k in range(c_idx.shape[1]):
        ok = c_idx[:, k] >= 0
        if ok.any():
            ci = c_idx[ok, k]; rc[ok, k] = win_logrv(ci, a, b, nmin) - 2 * np.log(sig[ci])
    nval = np.isfinite(rc).sum(1); rcm = np.where(nval >= 2, np.nanmean(np.where(np.isfinite(rc), rc, np.nan), axis=1), np.nan)
    return rho_e - rcm, rho_e, rcm

for w, (a, b, nmin) in WINS.items():
    E_, rho_, rc_ = excess(EV.idx.to_numpy(), C_IDX, a, b, nmin)
    EV["E_" + w] = E_; EV["rho_" + w] = rho_; EV["rc_" + w] = rc_
EV["slope"] = EV.E_W1 - EV.E_W3

# ---------- 推定器 ----------
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, len(a), len(b)
    dm = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dm, (dm / se if se > 0 else np.nan), len(a), len(b)

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def arm_fit(o, ycol, treat, ctrlarm, nperm=0):
    """o: EV rows. y = E_k. X = [1, 1{treat}, logz, hour FE]. cluster by day. returns beta,se,n_t,n_c,G,p_perm"""
    o = o[(o.cls == treat) | (o.cls == ctrlarm)]; o = o[np.isfinite(o[ycol])]
    if (o.cls == treat).sum() < 5 or (o.cls == ctrlarm).sum() < 5: return (np.nan,) * 6
    hours = sorted(o.hr.unique())
    H = np.column_stack([(o.hr.to_numpy() == h).astype(float) for h in hours[1:]]) if len(hours) > 1 else np.zeros((len(o), 0))
    d = (o.cls == treat).to_numpy(float); y = o[ycol].to_numpy(float)
    X = np.column_stack([np.ones(len(o)), d, o.logz.to_numpy(float), H])
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    se = math.sqrt(max(V[1, 1], 0)); p = np.nan
    if nperm:
        # FWL: residualize on covariates (excluding d); permute d within hour strata
        Xc = np.column_stack([np.ones(len(o)), o.logz.to_numpy(float), H])
        M = np.eye(len(o)) - Xc @ np.linalg.pinv(Xc.T @ Xc) @ Xc.T
        My = M @ y; Md = M @ d; b0 = (Md @ My) / (Md @ Md)
        hh = o.hr.to_numpy(); bs = np.empty(nperm)
        for q in range(nperm):
            dp = d.copy()
            for h in hours:
                m_ = hh == h; dp[m_] = rng.permutation(dp[m_])
            Mdp = M @ dp; bs[q] = (Mdp @ My) / (Mdp @ Mdp)
        p = float((np.abs(bs) >= abs(b0)).mean())
    return beta[1], se, int((o.cls == treat).sum()), int((o.cls == ctrlarm).sum()), G, p

def sub(lo_, hi_): return EV[(EV.year >= lo_) & (EV.year <= hi_)]

# ---------- 主表 ----------
say("## 主表: 超過ボラ E_k（log RV 比・同時刻対照差）の腕別平均と ANN_J − UJ（log z＋時刻 FE・日クラスタ）")
say("| 窓 | k | ANN_J 平均 E (n) | UJ 平均 E (n) | SJ 平均 E (n) | **D = ANN_J − UJ β (日cl t)** | MDE 2se | 未調整 Welch t | 置換 p |")
say("|---|---|---|---|---|---|---|---|---|")
RES = {}
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    for w in ["PRE", "W1", "W2", "W3", "W4", "slope"]:
        yc = "E_" + w if w != "slope" else "slope"
        aj = o[o.cls == "ANN_J"][yc]; uj = o[o.cls == "UJ"][yc]; sj = o[o.cls == "SJ"][yc]
        b_, se_, nt, nc, G, p = arm_fit(o, yc, "ANN_J", "UJ", nperm=(NPERM if w == "W3" and lab != "近年 2024-26H1" else 0))
        dm, tw, _, _ = welch(aj, uj)
        bold = "**" if w == "W3" else ""
        say(f"| {lab} | {w} | {np.nanmean(aj):+.3f} ({np.isfinite(aj).sum()}) | {np.nanmean(uj):+.3f} ({np.isfinite(uj).sum()}) | {np.nanmean(sj):+.3f} ({np.isfinite(sj).sum()}) | "
            f"{bold}{b_:+.3f} ({(b_/se_ if se_ and se_>0 else float('nan')):+.2f}){bold} | {2*se_:.3f} | {tw:+.2f} | {('%.4f' % p) if np.isfinite(p) else '—'} |")
        RES[(lab, w)] = (b_, se_, nt, nc, p)
say("")

# ---------- 判定 ----------
say("## 判定（事前固定・主セル D_W3・両側）")
bi, si, _, _, pi = RES[("在 2010-20", "W3")]; bo, so, _, _, po = RES[("外 2021-26H1", "W3")]
ti = bi / si if si > 0 else float("nan"); to = bo / so if so > 0 else float("nan")
h_dec = (bi < 0) and (ti <= -2) and (bo < 0) and (to <= -1.5)
h_per = (bi > 0) and (ti >= 2) and (bo > 0) and (to >= 1.5)
verdict = "H_DECAY PASS（公表後はボラが速く戻る）" if h_dec else ("H_PERSIST PASS（公表後の方がボラが持続）" if h_per else "null")
say(f"- 在 D_W3 {bi:+.3f} (t {ti:+.2f}・置換 p {pi:.4f}・MDE {2*si:.3f})／外 D_W3 {bo:+.3f} (t {to:+.2f}・置換 p {po:.4f}・MDE {2*so:.3f})")
say(f"- **判定: {verdict}**  [H_DECAY 在 t≤−2 ∧ 外 t≤−1.5 → {h_dec} / H_PERSIST 在 t≥2 ∧ 外 t≥1.5 → {h_per}]")
say("")

# ---------- 副: 腕別の E プロファイル（PRE→W4）vol 単位 ----------
say("## 副① 腕別 E_k プロファイル（exp(E/2) = 同時刻対照に対する vol 比・中央値版は exp(median E /2)）")
say("| 窓 | 腕 | n | PRE | W1 | W2 | W3 | W4 | W1 中央値版 | W3 中央値版 |")
say("|---|---|---|---|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = sub(lo_, hi_)
    for arm in ["ANN_J", "ANN_NJ", "UJ", "SJ"]:
        a = o[o.cls == arm]
        if len(a) < 5: continue
        f = lambda w: f"{math.exp(np.nanmean(a['E_'+w])/2):.2f}"
        g = lambda w: f"{math.exp(np.nanmedian(a['E_'+w])/2):.2f}"
        say(f"| {lab} | {arm} | {len(a)} | {f('PRE')} | {f('W1')} | {f('W2')} | {f('W3')} | {f('W4')} | {g('W1')} | {g('W3')} |")
say("")

# ---------- 副② 種別別・z 層・年別（外・在） ----------
say("## 副② ANN_J 種別別 D（vs UJ・log z＋時刻 FE・日クラスタ）と z 層・感度（足 1 除外・順位）")
say("| 窓 | 種別/層 | n ANN_J / UJ | D_W1 (t) | D_W3 (t) | D_W4 (t) |")
say("|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS[:2]:
    o = sub(lo_, hi_)
    for kind in ["NFP", "FOMC", "CPI"]:
        o2 = o[(o.kind == kind) | (o.cls == "UJ")]
        cells = []
        for w in ["W1", "W3", "W4"]:
            b_, se_, nt, nc, G, _ = arm_fit(o2[o2.cls.isin(["ANN_J", "UJ"])], "E_" + w, "ANN_J", "UJ")
            cells.append(f"{b_:+.3f} ({(b_/se_ if se_ and se_>0 else float('nan')):+.2f})")
        say(f"| {lab} | {kind} | {int(((o2.kind==kind)&(o2.cls=='ANN_J')).sum())} / {int((o2.cls=='UJ').sum())} | " + " | ".join(cells) + " |")
    for zl, zh, name in [(5, 7, "z 5–7"), (7, 99, "z >7")]:
        o2 = o[(o.z >= zl) & (o.z < zh)]
        cells = []
        for w in ["W1", "W3", "W4"]:
            b_, se_, nt, nc, G, _ = arm_fit(o2, "E_" + w, "ANN_J", "UJ")
            cells.append(f"{b_:+.3f} ({(b_/se_ if se_ and se_>0 else float('nan')):+.2f})")
        say(f"| {lab} | {name} | {int((o2.cls=='ANN_J').sum())} / {int((o2.cls=='UJ').sum())} | " + " | ".join(cells) + " |")
    # sensitivity: W1b (bars 2..12) and Mann-Whitney on W3
    b_, se_, nt, nc, G, _ = arm_fit(o, "E_W1b", "ANN_J", "UJ")
    aj = o[o.cls == "ANN_J"].E_W3.dropna(); uj = o[o.cls == "UJ"].E_W3.dropna()
    mw = st.mannwhitneyu(aj, uj, alternative="two-sided"); auc = mw.statistic / (len(aj) * len(uj))
    say(f"| {lab} | 感度 | {nt} / {nc} | W1'(足 2..12) {b_:+.3f} ({(b_/se_ if se_ and se_>0 else float('nan')):+.2f}) | W3 Mann–Whitney AUC {auc:.3f} p {mw.pvalue:.4f}・中央値差 {aj.median()-uj.median():+.3f} | SJ vs UJ W3 {arm_fit(o, 'E_W3', 'SJ', 'UJ')[0]:+.3f} (t {arm_fit(o, 'E_W3', 'SJ', 'UJ')[0]/arm_fit(o, 'E_W3', 'SJ', 'UJ')[1]:+.2f}) |")
say("")
say("## 副③ 年別 D_W3（未調整 Welch・ANN_J − UJ）")
yy = []
for y in range(2010, 2027):
    o = EV[EV.year == y]; aj = o[o.cls == "ANN_J"].E_W3; uj = o[o.cls == "UJ"].E_W3
    if np.isfinite(aj).sum() >= 3 and np.isfinite(uj).sum() >= 3:
        dm, tw, na, nu = welch(aj, uj); yy.append(f"{y}:{dm:+.2f}({na}/{nu})")
say("- " + " ".join(yy))
say("")

# ---------- 副④ 偽事象（±7 日）と陽性対照 ----------
say("## 副④ sanity: UJ の t0 を ±7 日ずらした偽事象の E_k（≈0 が期待）／陽性対照（UJ の W3 r ×1.15 ＝ E_W3 +0.279 注入）")
uj_idx = EV[EV.cls == "UJ"].idx.to_numpy()
for sh in (-7, 7):
    fi = uj_idx + sh * 288
    fi = fi[(fi >= 0) & (fi < N)]; fi = fi[elig[fi]]
    ci, _ = draw_ctrl(fi)
    cells = []
    for w in ["W1", "W3"]:
        a, b, nmin = WINS[w]; E_, _, _ = excess(fi, ci, a, b, nmin)
        cells.append(f"{w} {np.nanmean(E_):+.3f} (t {np.nanmean(E_)/ (np.nanstd(E_)/math.sqrt(np.isfinite(E_).sum())):+.2f}・n {np.isfinite(E_).sum()})")
    say(f"- 偽事象 {sh:+d} 日（対照適格足のみ）: " + "・".join(cells))
for lab, lo_, hi_ in ERAS[:2]:
    o = sub(lo_, hi_).copy()
    o.loc[o.cls == "UJ", "E_W3"] = o.loc[o.cls == "UJ", "E_W3"] + 2 * math.log(1.15)
    b_, se_, nt, nc, G, _ = arm_fit(o, "E_W3", "ANN_J", "UJ")
    b0, se0, _, _, _, _ = RES[(lab, "W3")][0], RES[(lab, "W3")][1], 0, 0, 0, 0
    say(f"- 陽性対照 {lab}: D_W3 {b0:+.3f} (t {b0/se0:+.2f}) → 注入後 {b_:+.3f} (t {b_/se_:+.2f})・Δt {(b_-b0)/se_:+.2f}")
say("")

# ---------- 補⑤ 戦略への接続: scan 本の建玉後 12 足の path 粗さ ----------
say("## 補⑤（記述・判定外）scan 本の建玉後 12 足の path 粗さ ρ_e = log(RV(e+1..e+12)/σ_trail²(e))・腕 = c45 定義（ANN 0〜4 h／UJ 窓／ctrl）・時刻 FE・日クラスタ")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
tr = pd.DataFrame(d["trades"]); FT = d["frozen"]["FEED_TOL"]
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy(); tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0); tsf = ts.astype(float)
def inwin(t0s, span=14400.0):
    t0s = np.sort(t0s[np.isfinite(t0s)])
    pos_ = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos_]) & (et_ < t0s[pos_] + span)
tr["ANN"] = inwin(t_nfp) | inwin(t_fomc)
uj_all = JC[JC.cls == "UJ"].ts.to_numpy(float); sj_all = JC[JC.cls == "SJ"].ts.to_numpy(float)
tr["UJ"] = inwin(uj_all + 300) & ~tr.ANN & ~tr.isevday
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~inwin(np.r_[uj_all, sj_all] + 300) & ~tr.ANN
ei = np.clip(np.searchsorted(ts, et_.astype(np.int64)), 0, N - 1); okE = ts[ei] == et_.astype(np.int64)
rho_e = np.full(len(tr), np.nan); rho_e[okE] = win_logrv(ei[okE], 1, 12, 6) - 2 * np.log(sig[ei[okE]])
tr["rho_e"] = rho_e; tr["logz"] = 0.0; tr["hr"] = tr.hh; tr["year"] = e_ny.year.to_numpy()
say(f"- scan 本 {len(tr)}・entry_time が格子に一致 {okE.mean()*100:.1f}%・ρ_e 有効 {np.isfinite(rho_e).sum()}・ANN {int(tr.ANN.sum())}／UJ {int(tr.UJ.sum())}／ctrl {int(tr.ctrl.sum())}")
say("| 窓 | 腕 | n | ρ_e 平均（vol 比 exp(ρ/2)） | β vs ctrl（時刻 FE・日cl t） | 同腕 R* 平均 |")
say("|---|---|---|---|---|---|")
for lab, lo_, hi_ in ERAS:
    o = tr[(tr.year >= lo_) & (tr.year <= hi_)]
    for arm in ["ANN", "UJ"]:
        o2 = o[o[arm] | o.ctrl].copy(); o2["cls"] = np.where(o2[arm], arm, "ctrl")
        b_, se_, nt, nc, G, _ = arm_fit(o2, "rho_e", arm, "ctrl")
        a = o2[o2.cls == arm]
        say(f"| {lab} | {arm} | {nt} | {a.rho_e.mean():+.3f} ({math.exp(a.rho_e.mean()/2):.2f}) vs ctrl {o2[o2.cls=='ctrl'].rho_e.mean():+.3f} | {b_:+.3f} ({(b_/se_ if se_ and se_>0 else float('nan')):+.2f}) | {a.Rs.mean():+.3f} |")
# within ANN trades: does calmer path (lower rho_e) go with higher R*? (look-ahead・記述のみ)
o = tr[(tr.year >= 2021) & tr.ANN & np.isfinite(tr.rho_e)]
if len(o) > 20:
    rho_c = st.spearmanr(o.rho_e, o.Rs)
    say(f"- 外 ANN 本内（look-ahead・記述）: ρ_e と R* の Spearman {rho_c.statistic:+.3f} (p {rho_c.pvalue:.3f}・n {len(o)})・ctrl 本では {st.spearmanr(tr[(tr.year>=2021)&tr.ctrl&np.isfinite(tr.rho_e)].rho_e, tr[(tr.year>=2021)&tr.ctrl&np.isfinite(tr.rho_e)].Rs).statistic:+.3f}")
say("")
EVC = os.path.join(DATA, "c47_events_excess.csv")
EV.drop(columns=["day"]).assign(et_date=EV.day.dt.strftime("%Y-%m-%d")).to_csv(EVC, index=False, encoding="utf-8")
say(f"- 再利用キャッシュ保存: {os.path.relpath(EVC, ROOT)}（{len(EV)} 事象・腕 ANN_J/ANN_NJ/UJ/SJ・E_PRE/W1/W2/W3/W4/W1b・ρ・対照 ρ）")
say(f"- 実行時間 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
