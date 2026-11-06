# -*- coding: utf-8 -*-
"""
[REFUTE DGS10 placebo] 2026-11-06 反証レーン — 対象: 11:30／14:25 で生き残った唯一の条件づけセル
  「DGS10 Δ80 追い風 × side・区間FE+SELL・外 2021-26 β +0.134 (t3.94・区間クラスタ)」
  新しい攻撃 = **「金利」は特別か**。同じ機械（Δ80 符号区間 FE + β·tail + γ·SELL・区間クラスタ SE）に別の遅い系列を通す。
  これまでの帰無（参照日の週循環シフト）は「DGS10 系列そのものと本の整列」を壊す帰無で、「どんな遅い系列でも長い符号区間×side で
  t≈4 が出る」可能性（長区間 FE の機械的な膨張・2024-25 局在の時代効果を拾う遅い二値変数一般の性質）は未検査。

=== 事前固定（この docstring を書いてから数字を見る）===
入力: c8_crossasset_features.csv（R・side・year・entry_time）、FRED csv DGS10／DTWEXBGS／VIXCLS、XAU_daily_er.csv（土日除外・金自身 80d）。
結合規則 = cycle10/08:30/11:30 と同一: FRED 日付 D は JST D+1 07:00 以降の本（avail=(JST−7h).date−1）・asof ≤10 日・DTWEXBGS は加えて −7 暦日。
モデル: R ~ 区間FE(系列 X の Δ_N 符号連続区間) + β·tail_X + γ·SELL、区間クラスタ SE。窓: 在 2010-20／外 2021-26／近年 2024-26。判定は外。
tail の符号規約（金の追い風方向・事前に固定）:
  DGS10（基準）: 金利↓=BUY 追い風 → tail=(BUY∧Δ<0)∨(SELL∧Δ>0)
  DTWEXBGS（ドル）: ドル↓=BUY 追い風 → 同じ規約
  VIXCLS: 経済的向きの事前が無い（リスクオフ→金↑ と 流動性逼迫→金↓ の両説）→ 両符号を試し |t| の大きい方を報告（自由度 ×2 を注記）
  金自身 g80（ride）: 同向き=追い風 → tail=(BUY∧g>0)∨(SELL∧g<0)
Q0 再現: DGS10 N=80 外 β +0.134 (t3.94) を ±0.005 で。
Q1 実プラセボ系列（判定）: DTWEXBGS・VIXCLS・金 g80 を N=80 で。記述: N∈{40,60,100,120} 掃引・Kish 有効区間数・正負区間比。
Q2 合成プラセボ（判定）: DGS10 と同じ営業日格子上のガウス random walk を 300 本生成し Δ80 符号区間 → 同じ FE+side で外 β の t。
   |t| の帰無分布から P(|t| ≥ 観測 3.94) と 95%/99% 点。区間数・Kish 有効区間数の中央値も印字（DGS10 の 65／16.4 と比較）。
判定規則（外 2021-26）:
  **broken（金利は特別でない）** = 実プラセボのいずれかが N=80 で |t| ≥ 3.0（VIX は両符号の max）、または 合成 RW の P(|t|≥3.94) ≥ 0.05。
  **survived（金利固有）** = 実プラセボ全部 N=80 で |t| < 2.0 ∧ 合成 P < 0.01。他 inconclusive。
look-ahead: FRED 利用可能規則どおり。金 g80 は known≤te。closed 全本（TIME 含む）。D2: 16 年プール不使用・窓別。seed 20261106。
scan 無し・M5 原本読込なし・MT5 なし・外部通信なし。コスト倍はレジーム記述で diff 不変＝適用不能。
"""
import os, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_dgs10_placebo_series.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE DGS10 placebo] 「金利」は特別か — 別の遅い系列・合成 RW を同じ区間FE+side に通す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_dgs10_placebo_series.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); TE = X["te"].to_numpy().astype(np.int64)
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
say(f"- 本 {N}・{X['ts_jst'].min().date()}〜{X['ts_jst'].max().date()} JST（⑩）")

def load_fred(name):
    m = pd.read_csv(os.path.join(MAC, f"{name}.csv")); m.columns = ["date", "v"]; m["v"] = pd.to_numeric(m["v"], errors="coerce")
    m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    return m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), m["v"].to_numpy()
def intervals_from_series(FD, v, NH):
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
def within(v_, g):
    df = pd.DataFrame({"v": v_, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); Gc = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); Gc += 1
    V = ZtZi @ meat @ ZtZi * (Gc / max(Gc - 1, 1)); return beta, np.sqrt(np.diag(V)), Gc
def fe(y, mask, cols, iv):
    mm = mask & (iv >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    if mm.sum() < 30 or len(np.unique(iv[mm])) < 3: return dict(b=np.full(len(cols), np.nan), t=np.full(len(cols), np.nan), G=0, n=int(mm.sum()), kish=np.nan)
    yy = within(y[mm], iv[mm]); Z = np.column_stack([within(c[mm], iv[mm]) for c in cols])
    b, se, Gc = ols_cluster(yy, Z, iv[mm]); cnt = np.bincount(iv[mm]); cnt = cnt[cnt > 0]
    return dict(b=b, t=b / np.where(se > 0, se, np.nan), G=Gc, n=int(mm.sum()), kish=cnt.sum() ** 2 / (cnt ** 2).sum())
def run_cell(FD, v, NH, sign_conv, lag_days=0, label="", ref=None, tol=10):
    """sign_conv=+1: Δ<0 が BUY 追い風（金利・ドル）。−1: Δ>0 が BUY 追い風。
    ref=None → FRED 規則（avail 日・tol 10 日）。金自身は ref=TE（秒）・FD=known（秒）・tol 5 日で known ≤ te を保証（v0 は day 列を
    暦日と誤読して 1 日先の擬似日足を付けていた＝look-ahead。11:30/14:25 の g80 係数 ≈0 と食い違い、突合で発見・v1 で修正）。"""
    D, IV = intervals_from_series(FD, v, NH)
    F, IVo = attach(FD, D, IV, (AVAIL - lag_days) if ref is None else ref, tol=tol)
    if ref is not None: assert np.all(FD[np.clip(np.searchsorted(FD, ref, side="right") - 1, 0, None)][IVo >= 0] <= ref[IVo >= 0]), "look-ahead"
    OK = np.isfinite(F) & (IVo >= 0); TAIL = (OK & ((SGN * np.sign(F) * (-sign_conv)) > 0)).astype(float)
    out = {}
    for wn, wm in W.items():
        r = fe(R, wm & OK, [TAIL, SELL], IVo); negr = np.mean(F[wm & OK] < 0) if (wm & OK).any() else np.nan
        out[wn] = dict(b=r["b"][0], t=r["t"][0], G=r["G"], n=r["n"], kish=r["kish"], neg=negr)
    o = out["外2021-26"]
    say(f"- {label} N={NH}: 外 β **{o['b']:+.4f} (t{o['t']:+.2f})** 区間 {o['G']}・Kish {o['kish']:.1f}・負区間比 {o['neg']:.2f}・n{o['n']}｜在 {out['在2010-20']['b']:+.4f} (t{out['在2010-20']['t']:+.2f})｜近年 {out['近年2024-26']['b']:+.4f} (t{out['近年2024-26']['t']:+.2f})")
    return out

# ---------- Q0 ----------
say("\n## Q0 再現 DGS10")
FD_r, v_r = load_fred("DGS10")
base = run_cell(FD_r, v_r, 80, +1, 0, "DGS10")
t_obs = base["外2021-26"]["t"]; b_obs = base["外2021-26"]["b"]
say(f"- 再現 {'OK' if abs(b_obs-0.1336)<=0.005 else 'NG'}（11:30: +0.1336 t3.94）")

# ---------- Q1 実プラセボ ----------
say("\n## Q1 実プラセボ系列（同じ機械・同じ結合規則）")
FD_d, v_d = load_fred("DTWEXBGS"); FD_v, v_v = load_fred("VIXCLS")
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); E["dt"] = pd.to_datetime(E["ts_last"], unit="s")
E = E[~E["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
FD_g = E["known"].to_numpy().astype(np.int64); v_g = E["lc"].to_numpy()   # v1: known（秒）で付与・ref=TE
GTOL = 5 * 86400
res_pl = {}
for NH in (40, 60, 80, 100, 120):
    say(f"### N={NH}")
    res_pl[("DGS10", NH)] = run_cell(FD_r, v_r, NH, +1, 0, "DGS10 名目金利")
    res_pl[("DXY", NH)] = run_cell(FD_d, v_d, NH, +1, 7, "DTWEXBGS ドル（−7 日）")
    a = run_cell(FD_v, v_v, NH, +1, 0, "VIXCLS 符号A（VIX↓=BUY 追い風）"); b = run_cell(FD_v, v_v, NH, -1, 0, "VIXCLS 符号B（VIX↑=BUY 追い風）")
    res_pl[("VIX", NH)] = a if abs(a["外2021-26"]["t"]) >= abs(b["外2021-26"]["t"]) else b
    res_pl[("GOLD", NH)] = run_cell(FD_g, v_g, NH, -1, 0, "金自身 g（同向き=追い風・known≤te）", ref=TE, tol=GTOL)
t80 = {k: abs(res_pl[(k, 80)]["外2021-26"]["t"]) for k in ("DXY", "VIX", "GOLD")}
say(f"- N=80 実プラセボ |t|: ドル {t80['DXY']:.2f}・VIX(両符号 max) {t80['VIX']:.2f}・金自身 {t80['GOLD']:.2f}（基準 DGS10 {abs(t_obs):.2f}）")
sweep_max = {k: max(abs(res_pl[(k, n)]["外2021-26"]["t"]) for n in (40, 60, 80, 100, 120)) for k in ("DXY", "VIX", "GOLD")}
say(f"- 掃引 5 水平線の max|t|（記述）: ドル {sweep_max['DXY']:.2f}・VIX {sweep_max['VIX']:.2f}・金自身 {sweep_max['GOLD']:.2f}")

# ---------- Q2 合成 RW ----------
say("\n## Q2 合成プラセボ: DGS10 の営業日格子上のガウス random walk 300 本 → Δ80 符号区間 → 同じ FE+side（外 2021-26）")
NP = 300; tt = np.full(NP, np.nan); Gs = np.full(NP, np.nan); Ks = np.full(NP, np.nan); negs = np.full(NP, np.nan); tp = time.time()
m_out = W["外2021-26"]
for p in range(NP):
    v_s = np.cumsum(rng.standard_normal(len(v_r)))
    D, IV = intervals_from_series(FD_r, v_s, 80); F, IVo = attach(FD_r, D, IV, AVAIL)
    OK = np.isfinite(F) & (IVo >= 0); TAIL = (OK & ((SGN * np.sign(F) * -1) > 0)).astype(float)
    r = fe(R, m_out & OK, [TAIL, SELL], IVo); tt[p] = r["t"][0]; Gs[p] = r["G"]; Ks[p] = r["kish"]; negs[p] = np.mean(F[m_out & OK] < 0)
at = np.abs(tt[np.isfinite(tt)])
p_syn = (at >= abs(t_obs)).mean()
say(f"- {NP} 本（{time.time()-tp:.0f} s）: |t| 中央値 {np.median(at):.2f}・sd(t) {np.nanstd(tt):.2f}・95% 点 {np.quantile(at,.95):.2f}・99% 点 {np.quantile(at,.99):.2f}・max {at.max():.2f}")
say(f"- 区間数 中央値 {np.nanmedian(Gs):.0f}（DGS10 {base['外2021-26']['G']}）・Kish 中央値 {np.nanmedian(Ks):.1f}（DGS10 {base['外2021-26']['kish']:.1f}）・負区間比 中央値 {np.nanmedian(negs):.2f}（DGS10 {base['外2021-26']['neg']:.2f}）")
say(f"- **P(|t| ≥ {abs(t_obs):.2f}) = {p_syn:.3f}**（{int((at>=abs(t_obs)).sum())}/{len(at)}）")
# 補助: 識別可能な RW だけ（負区間比 0.2〜0.8）に限った帰無
idm = np.isfinite(tt) & (negs >= 0.2) & (negs <= 0.8)
say(f"- 補助: 正負が均衡（負区間比 0.2〜0.8）する RW {idm.sum()} 本に限ると |t| 95% 点 {np.quantile(np.abs(tt[idm]),.95):.2f}・P(|t|≥{abs(t_obs):.2f}) {(np.abs(tt[idm])>=abs(t_obs)).mean():.3f}")

# ---------- 判定 ----------
broken = (max(t80.values()) >= 3.0) or (p_syn >= 0.05)
survived = (max(t80.values()) < 2.0) and (p_syn < 0.01)
V = "broken（金利は特別でない）" if broken else ("survived（金利固有）" if survived else "inconclusive")
say(f"\n- **判定: {V}** — 実プラセボ N=80 max|t| {max(t80.values()):.2f}（規則: ≥3.0 broken／<2.0 survived）・合成 P {p_syn:.3f}（≥0.05 broken／<0.01 survived）・合計 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("wrote", OUT)
