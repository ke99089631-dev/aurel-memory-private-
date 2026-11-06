# -*- coding: utf-8 -*-
"""
[REFUTE c13 事後フォロー b] 2026-11-06 — 本編（refute_c13_driftsource.py）の Q4 年別で 2022 −0.16／2026 −0.05 が出た。
年内の区間FE は「正区間と負区間の両方が年内に無いと β が γ と分離できない」ので、識別の内訳を出す。判定規則は変えない。
 B1 外 年別・半期別: 正区間本数/負区間本数、TH_pos（正区間内 SELL−BUY）、TH_neg（負区間内 BUY−SELL）、β=(TH_pos+TH_neg)/2、γ。
 B2 ride_int 統制を長区間（≥20 営業日）に限って再計算（g_int が意味を持つ区間だけで β が削れるか）。
 B3 プラセボ open_gap の平坦度の意味: open_gap 群の hold/b/risk 組成を tail と並べる（平坦な μ_req が組成由来か）。
入力・結合規則は本編と同一。置換なし。
"""
import os, json, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c13_driftsource_b.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c13 b] 年別識別の内訳・長区間での ride_int 統制・プラセボ組成 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c13_driftsource_b.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); HOLD = X["hold"].to_numpy().astype(float); RISK = X["risk"].to_numpy(); B = X["b"].to_numpy()
EXIT = X["exit"].to_numpy(); OG = X["open_gap"].to_numpy(); WK = X["wall_kind"].to_numpy()
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64); TE = X["te"].to_numpy().astype(np.int64)
HALF = YEAR * 10 + (X["ts_jst"].dt.month > 6).astype(int).to_numpy()
NH = 80
m = pd.read_csv(os.path.join(MAC, "DGS10.csv")); m.columns = ["date", "v"]; m["v"] = pd.to_numeric(m["v"], errors="coerce")
m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
v = m["v"].to_numpy(); D80 = np.full(len(v), np.nan); D80[NH:] = v[NH:] - v[:-NH]
sg = np.sign(D80)
for k in range(1, len(sg)):
    if sg[k] == 0 and np.isfinite(sg[k - 1]): sg[k] = sg[k - 1]
IVraw = np.full(len(v), -1); cur = -1
for k in range(len(v)):
    if not np.isfinite(sg[k]): continue
    if k == 0 or not np.isfinite(sg[k - 1]) or sg[k] != sg[k - 1]: cur += 1
    IVraw[k] = cur
FD = m["date"].to_numpy().astype("datetime64[D]").astype(np.int64)
ln = np.bincount(IVraw[IVraw >= 0])
IV_START = np.zeros(cur + 1, dtype=np.int64)
for k in range(len(v)):
    if IVraw[k] >= 0 and (k == 0 or IVraw[k - 1] != IVraw[k]): IV_START[IVraw[k]] = FD[k]
i = np.searchsorted(FD, AVAIL, side="right") - 1; ok = (i >= 0) & ((AVAIL - FD[np.clip(i, 0, None)]) <= 10)
ii = np.clip(i, 0, len(FD) - 1); F = D80[ii].copy(); IV = IVraw[ii].copy(); F[~ok] = np.nan; IV[~ok] = -1; IV[~np.isfinite(F)] = -1
OK = IV >= 0; TAIL = (OK & ((SGN * np.sign(F) * -1) > 0)).astype(float); LEN = np.where(OK, ln[np.clip(IV, 0, None)], 0)

E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); E["dt"] = pd.to_datetime(E["ts_last"], unit="s")
E = E[~E["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
kn = E["known"].to_numpy().astype(np.int64); lcb = E["lc"].to_numpy(); dayb = E["day"].to_numpy().astype(np.int64)
gi = np.searchsorted(kn, TE, side="right") - 1; gok = (gi >= 0) & ((TE - kn[np.clip(gi, 0, None)]) <= 5 * 86400)
st_day = np.where(OK, IV_START[np.clip(IV, 0, None)], 0); si = np.searchsorted(dayb, st_day, side="right") - 1
GINT = np.full(N, np.nan); okI = OK & gok & (si >= 0) & (gi > si); GINT[okI] = lcb[gi[okI]] - lcb[si[okI]]
RIDE_INT = np.where(np.isfinite(GINT) & (GINT != 0), (SGN * GINT > 0).astype(float), np.nan)

def within(v_, g):
    df = pd.DataFrame({"v": v_, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); Gc = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); Gc += 1
    V = ZtZi @ meat @ ZtZi * (Gc / max(Gc - 1, 1)); return beta, np.sqrt(np.diag(V)), Gc
def fe(y, mask, cols):
    mm = mask & (IV >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    if mm.sum() < 30: return dict(b=np.full(len(cols), np.nan), t=np.full(len(cols), np.nan), G=0, n=int(mm.sum()))
    yy = within(y[mm], IV[mm]); Z = np.column_stack([within(c[mm], IV[mm]) for c in cols])
    b, se, Gc = ols_cluster(yy, Z, IV[mm]); return dict(b=b, t=b / np.where(se > 0, se, np.nan), G=Gc, n=int(mm.sum()))
def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se if se > 0 else np.nan

say("\n## B1 外 年別・半期別の識別内訳（n_pos/n_neg = 正/負区間の本数、TH_pos = 正区間内 SELL−BUY、TH_neg = 負区間内 BUY−SELL）")
def decomp(mask, label):
    pos = mask & OK & (F > 0); neg = mask & OK & (F < 0)
    dp, tp = welch(R[pos & (SELL > 0)], R[pos & (SELL == 0)]); dn, tn = welch(R[neg & (SELL == 0)], R[neg & (SELL > 0)])
    beta = np.nanmean([dp, dn]) if np.isfinite(dp) and np.isfinite(dn) else np.nan; gam = (dp - dn) / 2 if np.isfinite(dp) and np.isfinite(dn) else np.nan
    r = fe(R, mask, [TAIL, SELL])
    say(f"- {label}: n_pos {int(pos.sum())} / n_neg {int(neg.sum())}（負比率 {neg.sum()/max(pos.sum()+neg.sum(),1):.2f}）| TH_pos {dp:+.4f} (t{tp:+.2f}) | TH_neg {dn:+.4f} (t{tn:+.2f}) | β=(TH_pos+TH_neg)/2 {beta:+.4f}・γ {gam:+.4f} | FE β {r['b'][0]:+.4f} (t{r['t'][0]:+.2f}, 区間{r['G']})"
        + ("  ← 片符号 ≥90%: β と γ は分離不能（⑬）" if max(pos.sum(), neg.sum()) / max(pos.sum() + neg.sum(), 1) >= 0.9 else ""))
for yr in range(2021, 2027): decomp(YEAR == yr, str(yr))
say("")
for h in sorted(set(HALF[YEAR >= 2021])): decomp(HALF == h, f"{h//10}H{1 + h%10}")
say("\n- 外 2021-26 全体:"); decomp(YEAR >= 2021, "外2021-26")
say("- 外から 2024 を除く:"); decomp((YEAR >= 2021) & (YEAR != 2024), "外 除2024")
say("- 外から 2024-25 を除く:"); decomp((YEAR >= 2021) & ~np.isin(YEAR, [2024, 2025]), "外 除2024-25")

say("\n## B2 長区間（≥20 営業日）に限った ride_int 統制（外）")
for lab, mk in (("全区間", OK), ("長区間 ≥20", OK & (LEN >= 20)), ("長区間 ≥40", OK & (LEN >= 40))):
    wm = (YEAR >= 2021) & mk
    a = fe(R, wm, [TAIL, SELL]); b = fe(R, wm, [TAIL, SELL, RIDE_INT])
    mm = wm & np.isfinite(RIDE_INT)
    say(f"- {lab}: β {a['b'][0]:+.4f} (t{a['t'][0]:+.2f}, 区間{a['G']}, n{a['n']}) → +ride_int β **{b['b'][0]:+.4f} (t{b['t'][0]:+.2f})** ride_int {b['b'][2]:+.4f} (t{b['t'][2]:+.2f})、ρ(tail, ride_int) {np.corrcoef(TAIL[mm], RIDE_INT[mm])[0,1]:+.3f}、"
        f"金利追い風方向に金が動いた区間内比率 {((-np.sign(F[mm]) * GINT[mm]) > 0).mean():.2f}")
# 金が実際に金利追い風方向に動いた区間 vs 逆に動いた区間で β を分ける（代理なら前者だけ正）
wm = (YEAR >= 2021) & OK & np.isfinite(GINT)
agree = (-np.sign(F) * GINT) > 0
for lab, sel in (("金が金利方向に動いた区間内", agree), ("金が金利と逆に動いた区間内", ~agree)):
    r = fe(R, wm & sel, [TAIL, SELL]); say(f"- {lab}: β {r['b'][0]:+.4f} (t{r['t'][0]:+.2f}, 区間{r['G']}, n{r['n']})")

say("\n## B3 プラセボ open_gap 上位半分と tail の組成（外）: 平坦な μ_req(k) が組成の差で出ていないか")
wm = (YEAR >= 2021) & OK
for gname, grp in (("tail", TAIL > 0), ("open_gap 上位半分", OG > np.nanmedian(OG))):
    a = wm & grp; b_ = wm & ~grp
    say(f"- {gname}: n {int(a.sum())}:{int(b_.sum())} | hold {HOLD[a].mean():.1f} vs {HOLD[b_].mean():.1f} | b {B[a].mean():.2f} vs {B[b_].mean():.2f} | risk {RISK[a].mean():.2f} vs {RISK[b_].mean():.2f} | outer 率 {(WK[a]=='outer').mean():.2f} vs {(WK[b_]=='outer').mean():.2f} | TP 率 {(EXIT[a]=='TP').mean():.3f} vs {(EXIT[b_]=='TP').mean():.3f} | SL 率 {(EXIT[a]=='SL').mean():.3f} vs {(EXIT[b_]=='SL').mean():.3f} | mean R {R[a].mean():+.4f} vs {R[b_].mean():+.4f}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
