# -*- coding: utf-8 -*-
"""
[cycle15 研究レーン] 2026-11-06 — 【深化・レジーム】「なぜ 2024-25 だけか」（反証 14:25 の手渡し (a)・cycle14 が backlog に事前固定した 1 セル）

背景: 反証 08:30/11:30/14:25/17:40 で唯一生き残った条件づけ＝「DGS10 Δ80（80 営業日の名目金利トレンド）追い風 × side」
  外 2021-26 β_FE+side +0.134 (t3.94・区間FE＋SELL・区間クラスタ)、在 2010-20 +0.039 (t1.80)、質量は 2024-25 に局在。
  14:25 が残した最重大反証 = 「効果は 2024-25 の 3 半期に局在し、独立なレジーム観測が少ない。なぜその時期だけか」。
問い: 効果は「近年」でなく「金利主導期（金が金利に反応している期間）」に宿るのか。
  金利主導期の客観メーター = 金の日次リターン r_g と DGS10 の日次変化 Δy の **60 営業日 rolling 相関 ρ60**（known ≤ te・look-ahead なし）。
  通説の向き = 負（金利↑→金↓）。ρ60<0 の期間＝金利が金を動かしている期間。

=== 事前固定（この docstring を書いてから数字を見る）===
入力（既存キャッシュのみ・scan 無し・M5 原本無し・MT5 無し・外部通信無し）:
  data/c8_crossasset_features.csv（19404 本・R・side・year・entry_time・te）／data/macro/DGS10.csv（FRED）／data/macro/XAU_daily_er.csv（擬似日足・22:00 UTC 境界）。
結合規則:
  - DGS10 Δ80・符号区間・tail = 反証 c12/placebo と同一（avail=(JST−7h).date−1・asof ≤10 日・tail=(BUY∧Δ<0)∨(SELL∧Δ>0)・0 は直前符号を継承）。
  - 金 擬似日足: `day` は擬似日の**開始日**（反証 17:40 の指摘）。close の暦日 = date(ts_last UTC)・既知時刻 = `known`（ts_last+300）。土日（ts_last の曜日）除外。
    DGS10 日付 D（NY 午後確定）と金 close 暦日 D を inner 結合 → r_g = Δlc・Δy = Δy、金 flat 日（r_g=0）は除外。ρ60(D) = 直近 60 行の Pearson（当日含む・min 60）。
    本への付与 = avail 日で asof backward（≤10 日）。**assert: 付与した行の金 known ≤ te**（反証 17:40 v0 の look-ahead の再発防止）。
  - 読込後に min/max 時刻・最初の 3 行（day・ts_last・known）・ρ60 の符号比率（窓別・本別）を印字（⑩⑪⑬）。
モデル（主・区間FE＝DGS10 Δ80 符号区間・区間クラスタ頑健 SE）:
  R = α_i + β·tail + δ·tail·NEG + λ·NEG + γ·SELL + ε、NEG = 1[ρ60 < 0]（avail 時点）。
  β_non = β（相関非負期の追い風効果）、β_neg = β+δ（相関負＝金利主導期の追い風効果）、**δ = β_neg − β_non が主統計量**。
予測（H: 効果は金利主導期に宿る）: 外 δ > 0・在 δ > 0（在でも金利主導期なら立つ）。β_non ≈ 0。
判定規則（backlog cycle14 の事前固定どおり）:
  **PASS** = 外 δ>0 ∧ t_cl≥2 ∧ 在 δ>0 ∧ t_cl≥1.5 ∧ 置換 p(外)<0.05（参照日 k 週循環シフト・ρ60 系列のみシフト・tail/区間は固定・1000 回）。
  それ以外 **null**。⑬: 窓内の NEG 比率が >0.90 または <0.10 なら「識別不能」と宣言して判定しない。
構造の読み（判定とは別・事前に書く）:
  (i) PASS → 「近年に宿る」でなく「金利主導期に宿る」。在の β_neg >0 がその証拠。
  (ii) 外 δ ≤ 0 または |t|<1 → ρ60 の符号は効果を識別しない。効果が 2024-25 に局在する理由は「金利主導期」ではない（時代、または別の識別子）。
  (iii) 外 δ < 0 で t≤−2 → 効果は金が金利に**反応していない**期（相関非負）に強い＝「金利→金」の直接経路ではなく、金利トレンドが別の何か（配分フロー・ドル）の代理である可能性。
補助（記述・判定外）: 2024-25 の本の NEG 比率（「なぜ 2024-25 だけか」への直接の答え）／年別 ρ60 中央値と負比率／ρ60 五分位ごとの β_FE+side／
  複製 ρ120／閾値を窓中央値にした均衡分割／区間ブロック bootstrap（外・1000 回）の δ 95% CI／MDE=2·se(δ)／注入 +0.10R·tail·NEG → t（陽性対照 ⑦）。
D2: 16 年プールは使わない（窓別 在 2010-20／外 2021-26／近年 2024-26）。closed 全本（TIME 含む）。seed 20261106。
事前の最重大反証: ρ60 は 60 日の窓で、Δ80 の符号区間（中央値 77 営業日）とほぼ同じ尺度＝両者は機械的に相関し得る（金利トレンド期は金が反応していれば相関が立つ）。
  → NEG の主効果 λ と β_non を併記し、ρ60 と Δ80 符号のクロス表（本ベース）を印字する。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c15_rate_corr_regime_result.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle15] 「なぜ 2024-25 だけか」— 金×金利の 60 日 rolling 相関（金利主導期）は DGS10 Δ80 追い風セルを条件づけるか — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c15_rate_corr_regime.py)")

# ---------- 本 ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); TE = X["te"].to_numpy().astype(np.int64)
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
say(f"- 本 {N}（closed 全本・TIME 含む）、entry {X['ts_jst'].min().date()}〜{X['ts_jst'].max().date()} JST（⑩）")

# ---------- DGS10 Δ80 符号区間（反証 c12 と同一） ----------
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
FD, VY = load_fred("DGS10")
D80, IV80 = intervals_from_series(VY, 80)
F, IVo = attach(FD, D80, IV80, AVAIL)
OK = np.isfinite(F) & (IVo >= 0); TAIL = (OK & ((SGN * np.sign(F) * -1) > 0)).astype(float)
say(f"- Δ80 付与 {OK.mean()*100:.1f}%・符号区間 {IV80.max()+1}・tail 比 {TAIL[OK].mean():.3f}・n 内訳 BUY∧Δ<0 {int(((SGN>0)&(F<0)&OK).sum())} / BUY∧Δ>0 {int(((SGN>0)&(F>0)&OK).sum())} / SELL∧Δ>0 {int(((SGN<0)&(F>0)&OK).sum())} / SELL∧Δ<0 {int(((SGN<0)&(F<0)&OK).sum())}")

# ---------- 金 擬似日足 × DGS10 → ρ60 ----------
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv"))
E["dt"] = pd.to_datetime(E["ts_last"], unit="s"); E["kn"] = pd.to_datetime(E["known"], unit="s")
say(f"- XAU_daily_er.csv {len(E)} 行・ts_last {E['dt'].min()}〜{E['dt'].max()} UTC（⑩）。最初の 3 行 day/ts_last/known: " +
    "; ".join(f"day={int(r.day)}({pd.Timestamp(int(r.day), unit='D').date()}) ts_last={r.dt} known={r.kn}" for r in E.head(3).itertuples()))
E = E[~E["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
E["date"] = E["dt"].dt.normalize().to_numpy().astype("datetime64[D]").astype(np.int64)
Gd = E[["date", "lc", "known"]]
Yd = pd.DataFrame({"date": FD, "y": VY})
M = Gd.merge(Yd, on="date", how="inner").sort_values("date").reset_index(drop=True)
M["rg"] = M["lc"].diff(); M["dy"] = M["y"].diff()
n0 = len(M); M = M[np.isfinite(M["rg"]) & np.isfinite(M["dy"]) & (M["rg"] != 0)].reset_index(drop=True)
say(f"- 金×DGS10 日次結合: inner {n0} 日 → 金 flat 日除外後 {len(M)} 日（{pd.Timestamp(int(M['date'].iloc[0]),unit='D').date()}〜{pd.Timestamp(int(M['date'].iloc[-1]),unit='D').date()}）")
for NC in (60, 120):
    M[f"rho{NC}"] = M["rg"].rolling(NC, min_periods=NC).corr(M["dy"])
say(f"- ρ60 全期間: 中央値 {M['rho60'].median():+.3f}・負比率 {(M['rho60']<0).mean():.2f}・|ρ|<0.1 比率 {(M['rho60'].abs()<0.1).mean():.2f}")
say("- 年別 ρ60（日次）: 中央値 / 負比率: " + " ".join(f"{y}:{g['rho60'].median():+.2f}/{(g['rho60']<0).mean():.2f}" for y, g in M.assign(yr=pd.to_datetime(M['date'], unit='D').dt.year).groupby('yr') if y >= 2010))
CD = M["date"].to_numpy().astype(np.int64); KN = M["known"].to_numpy().astype(np.int64)
assert np.all(np.diff(KN) > 0), "known not monotone"
# 付与規則（v1）: ρ60(D) の既知時刻 = max(金 close 既知 22:00 UTC D, FRED D の利用可能 JST D+1 07:00 = 22:00 UTC D) = KN[D]。
#   ref = te（秒）で asof backward（known ≤ te・許容 10 日）。v0 は avail 日で付与し、22:00 UTC ちょうどに建玉した本で known = entry_time > te
#   （5 分の境界）となり assert が止めた → 反証 placebo と同じ「known ≤ te」に揃えた（判定規則は不変・数字を見る前の修正）。
TOLS = 10 * 86400
def attach_rho(col, ref_s, check=True):
    rho = M[col].to_numpy(); i = np.searchsorted(KN, ref_s, side="right") - 1
    ok = (i >= 0) & ((ref_s - KN[np.clip(i, 0, None)]) <= TOLS); ii = np.clip(i, 0, len(KN) - 1)
    out = rho[ii].copy(); out[~ok] = np.nan
    if check:
        sel = ok & np.isfinite(out); assert np.all(KN[ii][sel] <= ref_s[sel]), "look-ahead: gold known > te"
    return out
RHO = attach_rho("rho60", TE); RHO120 = attach_rho("rho120", TE)
OKR = OK & np.isfinite(RHO); NEG = (OKR & (RHO < 0)).astype(float)
say(f"- ρ60 付与 {np.isfinite(RHO).mean()*100:.1f}%・known≤te assert OK。本ベース ρ60: 中央値 {np.nanmedian(RHO[OKR]):+.3f}")
say("- ⑬ 窓別 NEG 比率（本）: " + " / ".join(f"{wn} {NEG[wm&OKR].mean():.2f} (n{int((wm&OKR).sum())})" for wn, wm in W.items()))
for yv in range(2010, 2027):
    m_ = OKR & (YEAR == yv)
    if m_.any(): L.append(f"  - {yv}: 本 {int(m_.sum())}・NEG 比率 {NEG[m_].mean():.2f}・ρ60 中央値 {np.nanmedian(RHO[m_]):+.2f}・tail 比 {TAIL[m_].mean():.2f}")
print("\n".join(L[-17:]))
# クロス表（本ベース）: Δ80 符号 × NEG
for wn, wm in W.items():
    m_ = wm & OKR; pos = F[m_] > 0; ng = NEG[m_] > 0
    say(f"- クロス表 {wn}: Δ80>0∧NEG {int((pos&ng).sum())} / Δ80>0∧nonneg {int((pos&~ng).sum())} / Δ80<0∧NEG {int((~pos&ng).sum())} / Δ80<0∧nonneg {int((~pos&~ng).sum())}（φ {np.corrcoef(pos.astype(float), ng.astype(float))[0,1]:+.2f}）")

# ---------- 回帰道具 ----------
def within(v_, g):
    df = pd.DataFrame({"v": v_, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); Gc = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); Gc += 1
    V = ZtZi @ meat @ ZtZi * (Gc / max(Gc - 1, 1)); return beta, V, Gc
def fe(y, mask, cols, iv):
    mm = mask & (iv >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    if mm.sum() < 30 or len(np.unique(iv[mm])) < 3:
        k = len(cols); return dict(b=np.full(k, np.nan), se=np.full(k, np.nan), t=np.full(k, np.nan), V=np.full((k, k), np.nan), G=0, n=int(mm.sum()))
    yy = within(y[mm], iv[mm]); Z = np.column_stack([within(c[mm], iv[mm]) for c in cols])
    b, V, Gc = ols_cluster(yy, Z, iv[mm]); se = np.sqrt(np.diag(V))
    return dict(b=b, se=se, t=b / np.where(se > 0, se, np.nan), V=V, G=Gc, n=int(mm.sum()))
def main_cell(y, mask, neg, label=""):
    """R ~ FE + β tail + δ tail·NEG + λ NEG + γ SELL。return dict with beta_non, beta_neg, delta, lam, gam"""
    r = fe(y, mask, [TAIL, TAIL * neg, neg, SELL], IVo)
    b, V = r["b"], r["V"]
    bneg = b[0] + b[1]; se_bneg = math.sqrt(max(V[0, 0] + V[1, 1] + 2 * V[0, 1], 0)) if np.isfinite(V[0, 0]) else np.nan
    return dict(beta_non=b[0], t_non=r["t"][0], beta_neg=bneg, t_neg=bneg / se_bneg if se_bneg > 0 else np.nan,
                delta=b[1], se_delta=r["se"][1], t_delta=r["t"][1], lam=b[2], t_lam=r["t"][2], gam=b[3], G=r["G"], n=r["n"])
def fmt_main(o):
    return (f"δ=β_neg−β_non **{o['delta']:+.4f} (t{o['t_delta']:+.2f})**・β_neg {o['beta_neg']:+.4f} (t{o['t_neg']:+.2f})・β_non {o['beta_non']:+.4f} (t{o['t_non']:+.2f})"
            f"・λ_NEG {o['lam']:+.4f} (t{o['t_lam']:+.2f})・γ_SELL {o['gam']:+.4f}・区間 {o['G']}・n{o['n']}")

# ---------- Q0 再現 ----------
say("\n## Q0 再現（区間FE+SELL・β_FE+side）")
for wn, wm in W.items():
    r = fe(R, wm & OK, [TAIL, SELL], IVo); say(f"- {wn}: β_FE+side {r['b'][0]:+.4f} (t{r['t'][0]:+.2f}, 区間 {r['G']}, n{r['n']})")
r_out = fe(R, W["外2021-26"] & OK, [TAIL, SELL], IVo); say(f"- 再現 {'OK' if abs(r_out['b'][0]-0.1336)<=0.005 else 'NG'}（11:30: +0.1336 t3.94）")

# ---------- Q1 主セル ----------
say("\n## Q1 主セル: ρ60<0（金利主導期）× tail（区間FE＋NEG 主効果＋SELL・区間クラスタ）")
MAIN = {}
for wn, wm in W.items():
    o = main_cell(R, wm & OKR, NEG); MAIN[wn] = o; say(f"- {wn}: {fmt_main(o)}")
    say(f"  - MDE(δ)=2·se {2*o['se_delta']:.3f}R")
# 部分集合（記述）: NEG 本だけ／nonneg 本だけで区間FE+SELL
say("- 部分集合（記述・各自の区間FE+SELL）:")
for wn, wm in W.items():
    rn = fe(R, wm & OKR & (NEG > 0), [TAIL, SELL], IVo); rp = fe(R, wm & OKR & (NEG == 0), [TAIL, SELL], IVo)
    say(f"  - {wn}: NEG 内 β {rn['b'][0]:+.4f} (t{rn['t'][0]:+.2f}, 区間 {rn['G']}, n{rn['n']}) / nonneg 内 β {rp['b'][0]:+.4f} (t{rp['t'][0]:+.2f}, 区間 {rp['G']}, n{rp['n']})")

# ---------- Q2 置換（ρ60 系列の参照日 k 週循環シフト・tail/区間固定） ----------
say("\n## Q2 置換帰無（ρ60 の参照日を k 週 循環シフト・1000 回・tail/区間は固定）: δ の t")
lo_d = pd.Timestamp("2011-01-03"); hi_d = pd.Timestamp("2026-06-26"); span_w = (hi_d - lo_d).days // 7
lo_s = int(lo_d.timestamp()); base_off = TE - lo_s; span_s = span_w * 7 * 86400
NP = 1000; WN2 = ["在2010-20", "外2021-26"]; nt = np.full((NP, 2), np.nan); tp_ = time.time()
for p in range(NP):
    k = int(rng.integers(8, span_w - 8)); sh = lo_s + (base_off + 7 * k * 86400) % span_s
    rp = attach_rho("rho60", sh, check=False); okp = OK & np.isfinite(rp); negp = (okp & (rp < 0)).astype(float)
    for j, wn in enumerate(WN2):
        nt[p, j] = main_cell(R, W[wn] & okp, negp)["t_delta"]
PERM = {}
for j, wn in enumerate(WN2):
    ot = MAIN[wn]["t_delta"]; pv = float((np.abs(nt[:, j]) >= abs(ot)).mean()); PERM[wn] = pv
    say(f"- {wn}: 観測 t {ot:+.2f} → 帰無 sd {np.nanstd(nt[:,j]):.2f}・95%点|t| {np.nanquantile(np.abs(nt[:,j]),0.95):.2f}・**両側 p {pv:.3f}**")
say(f"  （{time.time()-tp_:.0f} s）")

# ---------- Q3 区間ブロック bootstrap（外・1000 回） ----------
say("\n## Q3 区間ブロック bootstrap（区間を復元抽出・1000 回）: δ の 95% CI")
NB = 1000
for wn in ("在2010-20", "外2021-26"):
    m = W[wn] & OKR; ids = np.unique(IVo[m]); idx_by = {i_: np.flatnonzero(m & (IVo == i_)) for i_ in ids}; bs = np.full(NB, np.nan); tb = time.time()
    for bb in range(NB):
        pick = rng.choice(ids, size=len(ids), replace=True)
        rows = np.concatenate([idx_by[i_] for i_ in pick]); gid = np.concatenate([np.full(len(idx_by[i_]), kk) for kk, i_ in enumerate(pick)])
        y = within(R[rows], gid); Z = np.column_stack([within(c[rows], gid) for c in (TAIL, TAIL * NEG, NEG, SELL)])
        bs[bb] = (np.linalg.pinv(Z.T @ Z) @ Z.T @ y)[1]
    say(f"- {wn}: δ 点 {MAIN[wn]['delta']:+.4f}、95% CI [{np.nanquantile(bs,0.025):+.4f}, {np.nanquantile(bs,0.975):+.4f}]、P(δ≤0) {(bs<=0).mean():.3f}（{time.time()-tb:.0f} s）")

# ---------- Q4 陽性対照（注入） ----------
say("\n## Q4 陽性対照: R に +0.10R·tail·NEG（と +0.05R）を注入 → δ の t")
for inj in (0.10, 0.05):
    say(f"- 注入 {inj:+.2f}R: " + " / ".join(f"{wn} δ {main_cell(R + inj*TAIL*NEG, wm & OKR, NEG)['delta']:+.4f} (t{main_cell(R + inj*TAIL*NEG, wm & OKR, NEG)['t_delta']:+.2f})" for wn, wm in W.items()))

# ---------- Q5 記述: 五分位・複製 ρ120・均衡分割 ----------
say("\n## Q5 記述: ρ60 五分位ごとの β_FE+side（窓内分位・各自の区間FE+SELL）")
for wn, wm in W.items():
    m = wm & OKR; q = np.full(N, -1); qs = np.nanquantile(RHO[m], [0.2, 0.4, 0.6, 0.8]); q[m] = np.searchsorted(qs, RHO[m])
    parts = []
    for k in range(5):
        r = fe(R, m & (q == k), [TAIL, SELL], IVo); lo_, hi_ = np.nanmin(RHO[m & (q == k)]), np.nanmax(RHO[m & (q == k)])
        parts.append(f"Q{k+1}[{lo_:+.2f},{hi_:+.2f}] {r['b'][0]:+.3f} (t{r['t'][0]:+.1f}, n{r['n']})")
    say(f"- {wn}: " + " / ".join(parts))
say("\n## Q5b 複製 ρ120・均衡分割（閾値＝窓内中央値）")
OK120 = OK & np.isfinite(RHO120); NEG120 = (OK120 & (RHO120 < 0)).astype(float)
for wn, wm in W.items():
    o = main_cell(R, wm & OK120, NEG120); say(f"- ρ120 {wn}: NEG 比率 {NEG120[wm&OK120].mean():.2f}・{fmt_main(o)}")
for wn, wm in W.items():
    m = wm & OKR; thr = np.nanmedian(RHO[m]); negm = (m & (RHO < thr)).astype(float); o = main_cell(R, m, negm)
    say(f"- 均衡分割 {wn}（閾値 ρ60<{thr:+.3f}）: {fmt_main(o)}")

# ---------- 判定 ----------
say("\n## 判定（事前固定）")
ident = {wn: (0.10 <= NEG[wm & OKR].mean() <= 0.90) for wn, wm in W.items()}
o_out, o_in = MAIN["外2021-26"], MAIN["在2010-20"]
conds = dict(外δ正=o_out["delta"] > 0, 外t2=o_out["t_delta"] >= 2.0, 在δ正=o_in["delta"] > 0, 在t15=o_in["t_delta"] >= 1.5, 置換p=PERM["外2021-26"] < 0.05)
if not (ident["在2010-20"] and ident["外2021-26"]): verdict = "識別不能（⑬・NEG 比率が片側 >90%）"
elif all(conds.values()): verdict = "PASS（金利主導期に宿る）"
else: verdict = "null"
say(f"- 識別可能 {ident} / 条件 {conds} → **{verdict}**")
# 構造の読み（事前の規則）
if verdict.startswith("PASS"): reading = "(i) 効果は「近年」でなく「金利主導期（ρ60<0）」に宿る。在の β_neg が証拠。"
elif o_out["delta"] <= 0 or abs(o_out["t_delta"]) < 1: reading = "(ii) ρ60 の符号は効果を識別しない＝2024-25 への局在は「金利主導期」では説明できない（時代、または別の識別子）。"
elif o_out["delta"] < 0 and o_out["t_delta"] <= -2: reading = "(iii) 効果は金が金利に反応していない期（ρ60≥0）に強い＝金利トレンドは別要因の代理の可能性。"
else: reading = "外で予測方向だが在で再現せず／置換で立たず＝inconclusive 寄りの null。"
say(f"- 構造の読み: {reading}")
m24 = (YEAR >= 2024) & OKR
say(f"- 「なぜ 2024-25 だけか」への直接の答え（記述）: 近年 2024-26 の本の NEG 比率 {NEG[m24].mean():.2f}・ρ60 中央値 {np.nanmedian(RHO[m24]):+.3f}（在 {np.nanmedian(RHO[W['在2010-20']&OKR]):+.3f}・外 {np.nanmedian(RHO[W['外2021-26']&OKR]):+.3f}）")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
