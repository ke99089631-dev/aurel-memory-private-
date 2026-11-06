# -*- coding: utf-8 -*-
"""
[REFUTE 反証レーン] 2026-11-06 — 対象: cycle15 (18:55)
  C1 構造主張: 金×DGS10 の日次 60 日 rolling 相関 ρ60 は 2014〜2024 のほぼ全日（年別 負比率 0.97〜1.00）で負。
  C2 読み(ii): ρ60 の符号・強度は DGS10 Δ80 追い風セル（区間FE+SELL・外 β +0.134 t3.94）を識別しない。
  W  弱信号（事後 15 セルの最大）: ρ60 **最上位五分位（相関が最も弱い）で β 最大**が在 (+0.095 t2.4) と外 (+0.239 t2.8) で揃う。
  S  cycle15 自身の最重大反証: 尺度不一致＝「遅い結合」（金 80d トレンドの符号 vs 金利 80d トレンドの符号）なら識別できるかも（3 重相互作用・検出力不足と自己申告）。

=== 事前固定（この docstring を書いてから数字を見る）===
入力（既存キャッシュのみ・scan 無し・M1 原本無し・MT5 無し・外部通信無し）:
  data/c8_crossasset_features.csv／data/macro/{DGS10,DTWEXBGS,VIXCLS}.csv／data/macro/XAU_daily_er.csv／data/macro/XAU_m5_close.npz（Q1 の境界変種のみ・⑪ flat 除外）。
結合規則 = cycle15 と同一（Δ80: avail=(JST−7h).date−1・asof ≤10 日・tail=(BUY∧Δ<0)∨(SELL∧Δ>0)・0 は直前符号継承／ρ: known ≤ te（秒）で asof ≤10 日・assert）。
道具 = 区間FE（Δ80 符号区間）＋区間クラスタ SE（cycle15 と同じ閉形式）。窓 在2010-20／外2021-26／近年2024-26。D2: 16 年プール不使用。

Q0 再現: 外 β_FE+side +0.1336 (±0.005)、五分位 Q5 在 +0.095／外 +0.239 (±0.01)。合わなければ以降は無効。

Q1 C1 の頑健性（推定量・窓・日境界を変える）: 年別 負比率を
  (a) 基準 Pearson ρ60（22:00 UTC 擬似日）／(b) Spearman ρ60／(c) Pearson ρ20・ρ120／
  (d) 金の日境界を 21:00 UTC・23:00 UTC（XAU_m5_close.npz から・平日のみ・flat 日除外）／(e) 週次（非重複・金曜 close）26 週 rolling（記述）。
  規則: **C1 survived** = (a)(b)(c-120)(d-21)(d-23) の 5 変種すべてで 2014〜2024 の 11 年中 ≥9 年が負比率 ≥0.90。
        **C1 broken** = いずれかの変種で 2014〜2024 に負比率 <0.75 の年が ≥3。他は inconclusive。

Q2 W の family-wise（事後選択「どの五分位が最大か」を帰無に入れる）:
  1 本の FE 回帰 R ~ FE + β·tail + Σ_k δ_k·tail·1[Q_k] + Σ_k λ_k·1[Q_k] + γ·SELL（Q1 基準）。各 k の対比 c_k = β_Qk − mean(β_Q≠k)（区間クラスタ t）。
  統計量 T = max_k s_k、s_k = min(|t_在(c_k)|, |t_外(c_k)|)（在外で符号が一致する k のみ・不一致は 0）。
  帰無 = ρ60 の参照時刻を k 週循環シフト（cycle15 Q2 と同機構・tail/区間固定・窓内五分位を再計算）1000 回 → p_fw = P(T_perm ≥ T_obs)。
  併記: Q5 を事前に選んでいた場合の p_5 = P(s_5,perm ≥ s_5,obs)、近年の c_5、Q5 セルの区間数・Kish 有効区間数。
  規則: **W broken** = p_fw ≥ 0.05。**W survived** = p_fw < 0.05 ∧ 近年 c_5 > 0 (t≥1)。他 inconclusive。

Q3 強度の連続形（五分位でなく用量）: FE + SELL + tail + tail·ρz + ρz（ρz = 窓内標準化 ρ60）、同じく |ρ|z。
  W の含意 = tail·ρz の係数 >0（相関が 0 に近いほど β 大）＝ tail·|ρ|z <0。外 置換 p（2 形の max|t| で family-wise）。
  規則: 「強度が識別する」= 外 |t|≥2 ∧ 在 同符号 ∧ p_fw<0.05。それ以外は C2 の読み(ii) survived。

Q4 W が「時代の代理」か・「金利に固有」か（記述＋判定補助）:
  (a) 在/外の Q5 の年組成（年別シェア）。(b) 統制: 外に tail·1[year≥2025]、在に tail·1[year≤2013] を加えて c_5 がどれだけ残るか（残存率 = c_5(統制後)/c_5）。
  (c) プラセボ識別子: 金×DTWEXBGS（ドル・利用可能 −7 日）・金×VIXCLS の ρ60 で同じ五分位対比と T。ドル/VIX で T ≥ T_obs(DGS10) なら W は「金利に固有」でない。
  (d) 合成帰無 2: 金×ガウス RW（DGS10 と同じ日次格子・200 本）の ρ60 → T の分布。P(T ≥ T_obs)。
  (e) **外 LOYO**: 外窓から各年を 1 つ除いて c_5 を再計算し t の最小を印字（除 2025・除 2026H1 が焦点）。

Q5 S（遅い結合・cycle15 の自己反証を数字に）: g80 = 金 80 営業日 log リターン（XAU_daily_er 土日除外・known ≤ te・assert）。
  agree = 1[sign(g80) = −sign(Δ80)]（通説の結合＝金利↑で金↓ がトレンド尺度で成立している時点）。agree は時点の状態（側に依らない）。
  窓別・年別の agree 比率を印字（⑬: 0.10〜0.90 の外なら識別不能）。
  モデル: FE + SELL + tail + agree + tail·agree。β_tail(agree=1)・β_tail(agree=0)・差 = tail·agree の係数（区間クラスタ t）。外 区間 bootstrap 1000 回で差の 95% CI。MDE 2·se。
  規則: 「遅い結合が識別する」= 外 |tail·agree| t≥2 ∧ 在 同符号 ∧ 外 bootstrap CI が 0 を含まない。それ以外 → cycle15 の自己反証は識別子を救わない（null 維持）。

総合判定（事前）: cycle15 の判定「識別不能＋null・読み(ii)」は、Q1 C1 survived ∧ Q2 W broken ∧ Q3 強度 non-identify ∧ Q5 non-identify なら **survived**。
  Q2 W survived または Q3/Q5 が識別すれば読み(ii) は **broken**（＝ρ60 の強度／遅い結合がレジーム識別子になる）。混在は inconclusive。
closed 全本（TIME 含む）。seed 20261106。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c15_rhocorr.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE] cycle15 (18:55) ρ60 レジーム識別子 — C1 構造・W 弱信号（最上位五分位）・C2 読み(ii)・S 遅い結合 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c15_rhocorr.py)")

# ---------- 本 ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); TE = X["te"].to_numpy().astype(np.int64)
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
say(f"- 本 {N}（closed 全本・TIME 含む）、entry {X['ts_jst'].min().date()}〜{X['ts_jst'].max().date()} JST（⑩）")

# ---------- FRED ----------
def load_fred(name):
    m = pd.read_csv(os.path.join(MAC, f"{name}.csv")); m.columns = ["date", "v"]; m["v"] = pd.to_numeric(m["v"], errors="coerce")
    m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    say(f"- FRED {name}: {len(m)} 行 {m['date'].iloc[0].date()}〜{m['date'].iloc[-1].date()}（⑩）")
    return m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), m["v"].to_numpy()
def intervals_from_series(v, NH):
    D = np.full(len(v), np.nan); D[NH:] = v[NH:] - v[:-NH]; sg = np.sign(D)
    for k in range(1, len(sg)):
        if sg[k] == 0 and np.isfinite(sg[k - 1]): sg[k] = sg[k - 1]
    IV = np.full(len(v), -1); cur = -1
    for k in range(len(v)):
        if not np.isfinite(sg[k]): continue
        if k == 0 or not np.isfinite(sg[k - 1]) or sg[k] != sg[k - 1]: cur += 1
        IV[k] = cur
    return D, IV
def attach(FD, D, IV, ref, tol=10):
    i = np.searchsorted(FD, ref, side="right") - 1; ok = (i >= 0) & ((ref - FD[np.clip(i, 0, None)]) <= tol)
    ii = np.clip(i, 0, len(FD) - 1); F = D[ii].copy(); IVo = IV[ii].copy(); F[~ok] = np.nan; IVo[~ok] = -1; IVo[~np.isfinite(F)] = -1
    return F, IVo
FD, VY = load_fred("DGS10"); FDd, VD = load_fred("DTWEXBGS"); FDv, VV = load_fred("VIXCLS")
D80, IV80 = intervals_from_series(VY, 80)
F, IVo = attach(FD, D80, IV80, AVAIL)
OK = np.isfinite(F) & (IVo >= 0); TAIL = (OK & ((SGN * np.sign(F) * -1) > 0)).astype(float)
say(f"- Δ80 付与 {OK.mean()*100:.1f}%・区間 {IV80.max()+1}・tail 比 {TAIL[OK].mean():.3f}・n 内訳 BUY∧Δ<0 {int(((SGN>0)&(F<0)&OK).sum())} / BUY∧Δ>0 {int(((SGN>0)&(F>0)&OK).sum())} / SELL∧Δ>0 {int(((SGN<0)&(F>0)&OK).sum())} / SELL∧Δ<0 {int(((SGN<0)&(F<0)&OK).sum())}")

# ---------- 金 擬似日足 ----------
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv"))
E["dt"] = pd.to_datetime(E["ts_last"], unit="s")
say(f"- XAU_daily_er.csv {len(E)} 行・ts_last {E['dt'].min()}〜{E['dt'].max()} UTC（⑩）・day=開始日規約（cycle15 確認済）")
E = E[~E["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
E["date"] = E["dt"].dt.normalize().to_numpy().astype("datetime64[D]").astype(np.int64)
KN_g = E["known"].to_numpy().astype(np.int64); LC_g = E["lc"].to_numpy()

def daily_frame(gdate, glc, gknown, FDx, Vx, lag_days=0):
    """金 close 暦日 D と FRED 日付 D を inner 結合 → rg, dx, known(= max(金 known, FRED 利用可能 22:00 UTC D+lag))"""
    G = pd.DataFrame({"date": gdate, "lc": glc, "kn": gknown}); Yd = pd.DataFrame({"date": FDx, "x": Vx})
    M = G.merge(Yd, on="date", how="inner").sort_values("date").reset_index(drop=True)
    M["rg"] = M["lc"].diff(); M["dx"] = M["x"].diff()
    M = M[np.isfinite(M["rg"]) & np.isfinite(M["dx"]) & (M["rg"] != 0)].reset_index(drop=True)
    fred_known = (M["date"].to_numpy() + lag_days) * 86400 + 22 * 3600
    M["known"] = np.maximum(M["kn"].to_numpy(), fred_known)
    return M
def rolling_corr(M, NC, method="pearson"):
    if method == "pearson": return M["rg"].rolling(NC, min_periods=NC).corr(M["dx"]).to_numpy()
    # Spearman: rank within window
    rg = M["rg"].to_numpy(); dx = M["dx"].to_numpy(); out = np.full(len(M), np.nan)
    for i in range(NC - 1, len(M)):
        u = rg[i - NC + 1:i + 1]; v = dx[i - NC + 1:i + 1]
        ru = pd.Series(u).rank().to_numpy(); rv = pd.Series(v).rank().to_numpy()
        out[i] = np.corrcoef(ru, rv)[0, 1]
    return out
TOLS = 10 * 86400
def attach_known(vals, known, ref_s, check=True):
    i = np.searchsorted(known, ref_s, side="right") - 1
    ok = (i >= 0) & ((ref_s - known[np.clip(i, 0, None)]) <= TOLS); ii = np.clip(i, 0, len(known) - 1)
    out = vals[ii].copy(); out[~ok] = np.nan
    if check:
        sel = ok & np.isfinite(out); assert np.all(known[ii][sel] <= ref_s[sel]), "look-ahead: known > te"
    return out
def year_neg_ratio(M, rho, label):
    yr = pd.to_datetime(M["date"], unit="D").dt.year.to_numpy(); fin = np.isfinite(rho)
    parts = []; tab = {}
    for y in range(2010, 2027):
        m = fin & (yr == y)
        if m.sum() < 20: continue
        nr = float((rho[m] < 0).mean()); tab[y] = nr; parts.append(f"{y}:{np.median(rho[m]):+.2f}/{nr:.2f}")
    say(f"  - {label}: " + " ".join(parts))
    return tab

M0 = daily_frame(E["date"].to_numpy(), LC_g, KN_g, FD, VY)
assert np.all(np.diff(M0["known"].to_numpy()) > 0)
RHO60_d = rolling_corr(M0, 60); M0["rho60"] = RHO60_d
say(f"- 金×DGS10 日次（22:00 UTC 境界・flat 除外）: {len(M0)} 日 {pd.Timestamp(int(M0['date'].iloc[0]),unit='D').date()}〜{pd.Timestamp(int(M0['date'].iloc[-1]),unit='D').date()}")
KN0 = M0["known"].to_numpy().astype(np.int64)
RHO = attach_known(RHO60_d, KN0, TE); OKR = OK & np.isfinite(RHO)
say(f"- ρ60 付与 {np.isfinite(RHO).mean()*100:.1f}%・known≤te assert OK・本ベース中央値 {np.nanmedian(RHO[OKR]):+.3f}・窓別 NEG 比率 " + " / ".join(f"{wn} {(RHO[wm&OKR]<0).mean():.2f}" for wn, wm in W.items()))

# ---------- 回帰道具（高速 within） ----------
def within(v_, g):
    codes, uniq = pd.factorize(g); s = np.bincount(codes, weights=v_, minlength=len(uniq)); c = np.bincount(codes, minlength=len(uniq))
    return v_ - (s / c)[codes]
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    codes, uniq = pd.factorize(cl); k = Z.shape[1]
    S = np.zeros((len(uniq), k))
    for j in range(k): S[:, j] = np.bincount(codes, weights=Z[:, j] * e, minlength=len(uniq))
    meat = S.T @ S; Gc = len(uniq)
    V = ZtZi @ meat @ ZtZi * (Gc / max(Gc - 1, 1)); return beta, V, Gc
def fe(y, mask, cols, iv):
    mm = mask & (iv >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    k = len(cols)
    if mm.sum() < 30 or len(np.unique(iv[mm])) < 3:
        return dict(b=np.full(k, np.nan), se=np.full(k, np.nan), t=np.full(k, np.nan), V=np.full((k, k), np.nan), G=0, n=int(mm.sum()))
    yy = within(y[mm], iv[mm]); Z = np.column_stack([within(c[mm], iv[mm]) for c in cols])
    b, V, Gc = ols_cluster(yy, Z, iv[mm]); se = np.sqrt(np.clip(np.diag(V), 0, None))
    return dict(b=b, se=se, t=b / np.where(se > 0, se, np.nan), V=V, G=Gc, n=int(mm.sum()))
def kish(iv, m):
    c = np.bincount(pd.factorize(iv[m])[0]); return (c.sum() ** 2) / (c ** 2).sum()

# ---------- 五分位対比 ----------
def quint(rho, m):
    q = np.full(N, -1); qs = np.nanquantile(rho[m], [0.2, 0.4, 0.6, 0.8]); q[m] = np.searchsorted(qs, rho[m]); return q
def contrasts(y, m, q, extra=None):
    """1 本の FE 回帰: tail + tail·1[Q2..5] + 1[Q2..5] + SELL (+extra). 返り: 各 k の c_k=β_Qk − mean(β_others), t, β_k"""
    cols = [TAIL]
    for k in range(1, 5): cols.append(TAIL * (q == k))
    for k in range(1, 5): cols.append((q == k).astype(float))
    cols.append(SELL)
    if extra is not None:
        for e_ in extra: cols.append(e_)
    r = fe(y, m, cols, IVo); b, V = r["b"], r["V"]
    if not np.isfinite(b[0]): return None
    # β_k = b0 + d_k (d_1=0)
    A = np.zeros((5, len(cols))); A[:, 0] = 1.0
    for k in range(1, 5): A[k, k] = 1.0
    beta_k = A @ b
    out = []
    for k in range(5):
        w = np.full(5, -0.25); w[k] = 1.0; a = w @ A
        c = a @ b; se = math.sqrt(max(a @ V @ a, 0)); out.append((c, c / se if se > 0 else np.nan))
    return dict(c=np.array([o[0] for o in out]), t=np.array([o[1] for o in out]), beta=beta_k, G=r["G"], n=r["n"])
def T_stat(res_in, res_out):
    s = np.zeros(5)
    for k in range(5):
        ti, to = res_in["t"][k], res_out["t"][k]
        if np.isfinite(ti) and np.isfinite(to) and np.sign(res_in["c"][k]) == np.sign(res_out["c"][k]): s[k] = min(abs(ti), abs(to))
    return s

# ---------- Q0 ----------
say("\n## Q0 再現")
r_out = fe(R, W["外2021-26"] & OK, [TAIL, SELL], IVo); say(f"- 外 β_FE+side {r_out['b'][0]:+.4f} (t{r_out['t'][0]:+.2f}, 区間 {r_out['G']}) → {'OK' if abs(r_out['b'][0]-0.1336)<=0.005 else 'NG'}（cycle15 +0.1336）")
Q = {wn: quint(RHO, wm & OKR) for wn, wm in W.items()}
Q0rep = {}
for wn, wm in W.items():
    m = wm & OKR; parts = []
    for k in range(5):
        r = fe(R, m & (Q[wn] == k), [TAIL, SELL], IVo); parts.append(f"Q{k+1} {r['b'][0]:+.3f} (t{r['t'][0]:+.1f}, 区間{r['G']}, Kish {kish(IVo, m & (Q[wn]==k) & (IVo>=0)):.1f})")
        if k == 4: Q0rep[wn] = r["b"][0]
    say(f"- {wn} 五分位 β_FE+side（各自 FE）: " + " / ".join(parts))
say(f"- Q5 再現: 在 {Q0rep['在2010-20']:+.3f}（cycle15 +0.095）／外 {Q0rep['外2021-26']:+.3f}（+0.239）→ {'OK' if abs(Q0rep['在2010-20']-0.095)<=0.01 and abs(Q0rep['外2021-26']-0.239)<=0.01 else 'NG'}")

# ---------- Q1 C1 頑健性 ----------
say("\n## Q1 C1 の頑健性: 年別 ρ 中央値／負比率（変種）")
TABS = {}
TABS["(a) Pearson ρ60 22:00"] = year_neg_ratio(M0, RHO60_d, "(a) Pearson ρ60 22:00")
t_ = time.time(); TABS["(b) Spearman ρ60 22:00"] = year_neg_ratio(M0, rolling_corr(M0, 60, "spearman"), "(b) Spearman ρ60 22:00");
TABS["(c) Pearson ρ20"] = year_neg_ratio(M0, rolling_corr(M0, 20), "(c) Pearson ρ20（記述）")
TABS["(c) Pearson ρ120"] = year_neg_ratio(M0, rolling_corr(M0, 120), "(c) Pearson ρ120")
# (d) 境界変種（npz）
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); CL = z["close"]
say(f"- XAU_m5_close.npz {len(TS)} 本 {pd.Timestamp(TS[0],unit='s')}〜{pd.Timestamp(TS[-1],unit='s')} UTC（⑩）・flat 足比率 {(np.diff(CL)==0).mean():.3f}（⑪）")
def daily_from_npz(bh):
    """境界 bh:00 UTC。各暦日 D の close = D bh:00 の直前の足（bh−5min）の close。平日のみ・flat 日除外。known = D bh:00。"""
    d0 = pd.Timestamp(TS[0], unit="s").normalize(); d1 = pd.Timestamp(TS[-1], unit="s").normalize()
    days = pd.date_range(d0 + pd.Timedelta(days=1), d1, freq="D")
    tgt = days.to_numpy().astype("datetime64[s]").astype(np.int64) + bh * 3600 - 300
    i = np.searchsorted(TS, tgt, side="right") - 1; ok = (i >= 0) & (TS[np.clip(i, 0, None)] == tgt)
    dd = days[ok]; lc = np.log(CL[i[ok]]); kn = tgt[ok] + 300
    wk = dd.dayofweek.to_numpy(); keep = (wk < 5)
    dd, lc, kn = dd[keep], lc[keep], kn[keep]
    # flat 日除外（前日と同値）
    keep2 = np.r_[True, np.diff(lc) != 0]
    return dd[keep2].to_numpy().astype("datetime64[D]").astype(np.int64), lc[keep2], kn[keep2]
for bh in (21, 23, 15):
    gd, glc, gkn = daily_from_npz(bh)
    Mb = daily_frame(gd, glc, gkn, FD, VY); rb = rolling_corr(Mb, 60)
    lab = f"(d) Pearson ρ60 境界 {bh:02d}:00 UTC" + ("（記述・米国 fixing 前）" if bh == 15 else "")
    TABS[lab] = year_neg_ratio(Mb, rb, lab + f"・{len(Mb)} 日")
# (e) 週次
Mw = M0.copy(); Mw["wk"] = pd.to_datetime(Mw["date"], unit="D").dt.to_period("W-FRI")
Wk = Mw.groupby("wk").agg(date=("date", "last"), lc=("lc", "last"), x=("x", "last")).reset_index(drop=True)
Wk["rg"] = Wk["lc"].diff(); Wk["dx"] = Wk["x"].diff(); Wk = Wk[np.isfinite(Wk["rg"]) & np.isfinite(Wk["dx"])].reset_index(drop=True)
rw = Wk["rg"].rolling(26, min_periods=26).corr(Wk["dx"]).to_numpy()
year_neg_ratio(Wk, rw, "(e) 週次 Pearson ρ26w（記述・26 点で雑音大）")
# 判定
KEYS = ["(a) Pearson ρ60 22:00", "(b) Spearman ρ60 22:00", "(c) Pearson ρ120", "(d) Pearson ρ60 境界 21:00 UTC", "(d) Pearson ρ60 境界 23:00 UTC"]
ge90 = {k: sum(1 for y in range(2014, 2025) if TABS[k].get(y, 0) >= 0.90) for k in KEYS}
lt75 = {k: sum(1 for y in range(2014, 2025) if TABS[k].get(y, 1) < 0.75) for k in KEYS}
say(f"- 2014〜2024 で負比率 ≥0.90 の年数（/11）: " + " / ".join(f"{k} {ge90[k]}" for k in KEYS))
say(f"- 2014〜2024 で負比率 <0.75 の年数: " + " / ".join(f"{k} {lt75[k]}" for k in KEYS))
if all(v >= 9 for v in ge90.values()): C1 = "survived"
elif any(v >= 3 for v in lt75.values()): C1 = "broken"
else: C1 = "inconclusive"
say(f"- **Q1 判定 C1: {C1}**")

# ---------- Q2 W family-wise ----------
say("\n## Q2 W の family-wise（五分位対比 c_k=β_Qk−mean(β_others)・1 本の FE 回帰・事後選択を帰無に入れる）")
RES = {wn: contrasts(R, wm & OKR, Q[wn]) for wn, wm in W.items()}
for wn in W:
    r = RES[wn]; say(f"- {wn}: " + " / ".join(f"c{k+1} {r['c'][k]:+.3f} (t{r['t'][k]:+.2f})" for k in range(5)) + f"・β_k " + " ".join(f"{b:+.3f}" for b in r["beta"]) + f"・区間 {r['G']}・n{r['n']}")
s_obs = T_stat(RES["在2010-20"], RES["外2021-26"]); T_obs = s_obs.max(); k_obs = int(s_obs.argmax()) + 1
say(f"- 観測 s_k（在外符号一致の min|t|）: " + " ".join(f"Q{k+1} {s_obs[k]:.2f}" for k in range(5)) + f" → **T_obs {T_obs:.2f}（Q{k_obs}）**・s_5 {s_obs[4]:.2f}")
lo_d = pd.Timestamp("2011-01-03"); hi_d = pd.Timestamp("2026-06-26"); span_w = (hi_d - lo_d).days // 7
lo_s = int(lo_d.timestamp()); base_off = TE - lo_s; span_s = span_w * 7 * 86400
NP = 1000; Tp = np.full(NP, np.nan); s5p = np.full(NP, np.nan); c5near = np.full(NP, np.nan); tp_ = time.time()
for p in range(NP):
    k = int(rng.integers(8, span_w - 8)); sh = lo_s + (base_off + 7 * k * 86400) % span_s
    rp = attach_known(RHO60_d, KN0, sh, check=False); okp = OK & np.isfinite(rp)
    ri = contrasts(R, W["在2010-20"] & okp, quint(rp, W["在2010-20"] & okp)); ro = contrasts(R, W["外2021-26"] & okp, quint(rp, W["外2021-26"] & okp))
    if ri is None or ro is None: continue
    s = T_stat(ri, ro); Tp[p] = s.max(); s5p[p] = s[4]
p_fw = float(np.nanmean(Tp >= T_obs)); p_5 = float(np.nanmean(s5p >= s_obs[4]))
say(f"- 置換 1000 回（{time.time()-tp_:.0f} s）: T 帰無 中央値 {np.nanmedian(Tp):.2f}・95%点 {np.nanquantile(Tp,0.95):.2f}・**p_fw {p_fw:.3f}**；Q5 を事前に選んでいた場合 s_5 帰無 中央値 {np.nanmedian(s5p):.2f}・95%点 {np.nanquantile(s5p,0.95):.2f}・**p_5 {p_5:.3f}**")
c5n = RES["近年2024-26"]["c"][4]; t5n = RES["近年2024-26"]["t"][4]
say(f"- 近年 c_5 {c5n:+.3f} (t{t5n:+.2f})（近年の最大は Q{int(np.argmax(RES['近年2024-26']['beta']))+1}）")
if p_fw >= 0.05: Wv = "broken"
elif c5n > 0 and t5n >= 1: Wv = "survived"
else: Wv = "inconclusive"
say(f"- **Q2 判定 W: {Wv}**")

# ---------- Q3 連続形 ----------
say("\n## Q3 強度の連続形: tail·ρz／tail·|ρ|z（窓内標準化・FE+SELL+主効果）")
def zed(v, m): mu = np.nanmean(v[m]); sd = np.nanstd(v[m]); out = np.full(N, np.nan); out[m] = (v[m] - mu) / sd; return out
CONT = {}
for wn, wm in W.items():
    m = wm & OKR; rz = zed(RHO, m); az = zed(np.abs(RHO), m)
    r1 = fe(R, m, [TAIL, TAIL * rz, rz, SELL], IVo); r2 = fe(R, m, [TAIL, TAIL * az, az, SELL], IVo)
    CONT[wn] = (r1["b"][1], r1["t"][1], r2["b"][1], r2["t"][1])
    say(f"- {wn}: tail·ρz {r1['b'][1]:+.4f} (t{r1['t'][1]:+.2f})／tail·|ρ|z {r2['b'][1]:+.4f} (t{r2['t'][1]:+.2f})・β_tail(ρz=0) {r1['b'][0]:+.4f}・区間 {r1['G']}")
obs_max = max(abs(CONT["外2021-26"][1]), abs(CONT["外2021-26"][3])); mp = np.full(NP, np.nan); tp_ = time.time()
for p in range(NP):
    k = int(rng.integers(8, span_w - 8)); sh = lo_s + (base_off + 7 * k * 86400) % span_s
    rp = attach_known(RHO60_d, KN0, sh, check=False); m = W["外2021-26"] & OK & np.isfinite(rp)
    rz = zed(rp, m); az = zed(np.abs(rp), m)
    a = fe(R, m, [TAIL, TAIL * rz, rz, SELL], IVo)["t"][1]; b = fe(R, m, [TAIL, TAIL * az, az, SELL], IVo)["t"][1]
    mp[p] = max(abs(a), abs(b))
p_cont = float(np.nanmean(mp >= obs_max))
say(f"- 外 置換（2 形 max|t|・{time.time()-tp_:.0f} s）: 観測 {obs_max:.2f} → 帰無 中央値 {np.nanmedian(mp):.2f}・95%点 {np.nanquantile(mp,0.95):.2f}・**p_fw {p_cont:.3f}**")
sign_ok = np.sign(CONT["外2021-26"][0]) == np.sign(CONT["在2010-20"][0])
Q3v = "識別する" if (abs(CONT["外2021-26"][1]) >= 2 and sign_ok and p_cont < 0.05) else "識別しない（C2 読み(ii) survived）"
say(f"- **Q3 判定 強度: {Q3v}**")

# ---------- Q4 時代の代理・金利固有 ----------
say("\n## Q4 W は時代の代理か・金利に固有か")
for wn in ("在2010-20", "外2021-26"):
    m = W[wn] & OKR & (Q[wn] == 4); yrs, cnt = np.unique(YEAR[m], return_counts=True)
    say(f"- (a) {wn} Q5 の年組成: " + " ".join(f"{y}:{c/cnt.sum():.2f}" for y, c in zip(yrs, cnt)) + f"（n{cnt.sum()}）")
late = (YEAR >= 2025).astype(float); early = (YEAR <= 2013).astype(float)
ro_c = contrasts(R, W["外2021-26"] & OKR, Q["外2021-26"], extra=[TAIL * late, late])
ri_c = contrasts(R, W["在2010-20"] & OKR, Q["在2010-20"], extra=[TAIL * early, early])
say(f"- (b) 統制後 c_5: 外（+tail·1[≥2025]）{ro_c['c'][4]:+.3f} (t{ro_c['t'][4]:+.2f})・残存率 {ro_c['c'][4]/RES['外2021-26']['c'][4]:.2f}／在（+tail·1[≤2013]）{ri_c['c'][4]:+.3f} (t{ri_c['t'][4]:+.2f})・残存率 {ri_c['c'][4]/RES['在2010-20']['c'][4]:.2f}")
# (c) プラセボ識別子
def placebo_T(FDx, Vx, lag, label):
    Mx = daily_frame(E["date"].to_numpy(), LC_g, KN_g, FDx, Vx, lag_days=lag); rx = rolling_corr(Mx, 60)
    knx = Mx["known"].to_numpy().astype(np.int64); rr = attach_known(rx, knx, TE); okx = OK & np.isfinite(rr)
    ri = contrasts(R, W["在2010-20"] & okx, quint(rr, W["在2010-20"] & okx)); ro = contrasts(R, W["外2021-26"] & okx, quint(rr, W["外2021-26"] & okx))
    s = T_stat(ri, ro)
    say(f"- (c) {label}: 本ベース ρ60 中央値 {np.nanmedian(rr[okx]):+.3f}・NEG 比率 外 {(rr[W['外2021-26']&okx]<0).mean():.2f}・在 c_k t " + " ".join(f"{t:+.1f}" for t in ri["t"]) + "・外 c_k t " + " ".join(f"{t:+.1f}" for t in ro["t"]) + f" → **T {s.max():.2f}（Q{int(s.argmax())+1}）**・s_5 {s[4]:.2f}")
    return s.max()
T_dxy = placebo_T(FDd, VD, 7, "金×DTWEXBGS（ドル・−7 日）"); T_vix = placebo_T(FDv, VV, 0, "金×VIXCLS")
# (d) 合成 RW
NS = 200; Ts = np.full(NS, np.nan); tp_ = time.time()
rg0 = M0["rg"].to_numpy(); KNx = KN0
for s_ in range(NS):
    dx = rng.standard_normal(len(M0)); rr_d = pd.Series(rg0).rolling(60, min_periods=60).corr(pd.Series(dx)).to_numpy()
    rr = attach_known(rr_d, KNx, TE, check=False); okx = OK & np.isfinite(rr)
    ri = contrasts(R, W["在2010-20"] & okx, quint(rr, W["在2010-20"] & okx)); ro = contrasts(R, W["外2021-26"] & okx, quint(rr, W["外2021-26"] & okx))
    if ri is None or ro is None: continue
    Ts[s_] = T_stat(ri, ro).max()
say(f"- (d) 合成 RW 200 本（金×RW の ρ60・{time.time()-tp_:.0f} s）: T 中央値 {np.nanmedian(Ts):.2f}・95%点 {np.nanquantile(Ts,0.95):.2f}・**P(T ≥ T_obs {T_obs:.2f}) {np.nanmean(Ts >= T_obs):.3f}**")
# (e) 外 LOYO
parts = []
for y in range(2021, 2027):
    m = W["外2021-26"] & OKR & (YEAR != y); rr = contrasts(R, m, quint(RHO, m))
    parts.append(f"除{y} c_5 {rr['c'][4]:+.3f} (t{rr['t'][4]:+.2f})")
say("- (e) 外 LOYO（窓内五分位再計算）: " + " / ".join(parts))

# ---------- Q5 遅い結合 ----------
say("\n## Q5 S 遅い結合: agree = 1[sign(g80) = −sign(Δ80)]（金 80 営業日トレンドが金利トレンドと通説どおり逆向き）")
G80 = np.full(len(LC_g), np.nan); G80[80:] = LC_g[80:] - LC_g[:-80]
g80 = attach_known(G80, KN_g, TE); OKG = OKR & np.isfinite(g80) & (g80 != 0)
AGREE = (OKG & (np.sign(g80) == -np.sign(F))).astype(float)
say(f"- g80 付与 {np.isfinite(g80).mean()*100:.1f}%・known≤te assert OK。agree 比率 窓別 " + " / ".join(f"{wn} {AGREE[wm&OKG].mean():.2f} (n{int((wm&OKG).sum())})" for wn, wm in W.items()))
say("  - 年別 agree 比率: " + " ".join(f"{y}:{AGREE[OKG&(YEAR==y)].mean():.2f}" for y in range(2010, 2027) if (OKG & (YEAR == y)).any()))
ident5 = {wn: (0.10 <= AGREE[wm & OKG].mean() <= 0.90) for wn, wm in W.items()}
S5 = {}
for wn, wm in W.items():
    m = wm & OKG; r = fe(R, m, [TAIL, TAIL * AGREE, AGREE, SELL], IVo)
    b, V = r["b"], r["V"]; b1 = b[0] + b[1]; se1 = math.sqrt(max(V[0, 0] + V[1, 1] + 2 * V[0, 1], 0))
    S5[wn] = (b[1], r["t"][1], r["se"][1])
    ra = fe(R, m & (AGREE > 0), [TAIL, SELL], IVo); rd = fe(R, m & (AGREE == 0), [TAIL, SELL], IVo)
    say(f"- {wn}: β_tail(agree=0) {b[0]:+.4f} (t{r['t'][0]:+.2f})・β_tail(agree=1) {b1:+.4f} (t{b1/se1 if se1>0 else float('nan'):+.2f})・**差 tail·agree {b[1]:+.4f} (t{r['t'][1]:+.2f})**・MDE 2·se {2*r['se'][1]:.3f}R・λ_agree {b[2]:+.4f}・区間 {r['G']}・n{r['n']}")
    say(f"    部分集合（各自 FE）: agree=1 内 β {ra['b'][0]:+.4f} (t{ra['t'][0]:+.2f}, 区間 {ra['G']}, n{ra['n']}) / agree=0 内 β {rd['b'][0]:+.4f} (t{rd['t'][0]:+.2f}, 区間 {rd['G']}, n{rd['n']})")
# 外 区間 bootstrap
m = W["外2021-26"] & OKG; ids = np.unique(IVo[m]); idx_by = {i_: np.flatnonzero(m & (IVo == i_)) for i_ in ids}; NB = 1000; bs = np.full(NB, np.nan); tb = time.time()
for bb in range(NB):
    pick = rng.choice(ids, size=len(ids), replace=True)
    rows = np.concatenate([idx_by[i_] for i_ in pick]); gid = np.concatenate([np.full(len(idx_by[i_]), kk) for kk, i_ in enumerate(pick)])
    y = within(R[rows], gid); Z = np.column_stack([within(c[rows], gid) for c in (TAIL, TAIL * AGREE, AGREE, SELL)])
    bs[bb] = (np.linalg.pinv(Z.T @ Z) @ Z.T @ y)[1]
ci = (np.nanquantile(bs, 0.025), np.nanquantile(bs, 0.975))
say(f"- 外 区間 bootstrap（{time.time()-tb:.0f} s）: tail·agree 95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}]・P(≤0) {(bs<=0).mean():.3f}")
sign5 = np.sign(S5["外2021-26"][0]) == np.sign(S5["在2010-20"][0])
Q5v = "識別する" if (abs(S5["外2021-26"][1]) >= 2 and sign5 and (ci[0] > 0 or ci[1] < 0)) else "識別しない（cycle15 の自己反証は識別子を救わない）"
if not (ident5["在2010-20"] and ident5["外2021-26"]): Q5v += "（⑬ agree 比率が片側・識別不能を併記）"
say(f"- **Q5 判定 遅い結合: {Q5v}**")

# ---------- 総合 ----------
say("\n## 総合判定（事前規則）")
ident_ok = Q3v.startswith("識別しない") and Q5v.startswith("識別しない")
if C1 == "survived" and Wv == "broken" and ident_ok: FINAL = "cycle15 の判定（識別不能＋null・読み(ii)）は **survived**"
elif Wv == "survived" or not ident_ok: FINAL = "cycle15 の読み(ii) は **broken**（ρ60 の強度／遅い結合がレジーム識別子になる）"
else: FINAL = "**inconclusive**（混在）"
say(f"- C1 {C1}／W {Wv}／強度 {Q3v.split('（')[0]}／遅い結合 {Q5v.split('（')[0]} → {FINAL}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
