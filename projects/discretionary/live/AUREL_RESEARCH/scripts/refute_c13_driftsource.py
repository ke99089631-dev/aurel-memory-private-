# -*- coding: utf-8 -*-
"""
[REFUTE c13] 2026-11-06 反証レーン — 対象: cycle13 (12:50) の 2 つの読み
  T1 「残り path から逆算した必要ドリフト μ_req(k) が k=0〜48 でほぼ一定・b 三分位で単調＝一定ドリフト型（M_drift）と整合」
  T2 cycle13 自身の最重大反証「そのドリフトの源が金利地合いである証拠は無い。Δ80 の符号は長い区間内の金の局所ドリフトの
     代理かもしれない。区間FE+SELL+金の局所ドリフト（直近 5 営業日の向き・known≤te）×side を同時統制して tail の β が
     残れば金利固有、消えれば局所ドリフトの代理」＝研究レーンが次の深化に残した 1 セルを、反証レーンが尺度掃引つきで先に実行。

=== 事前固定（この docstring を書いてから数字を見る）===
入力・結合規則は cycle13 / 反証 11:30 と同一（c8 特徴量 csv・c1 json・refute_c2_fullpaths.npz・FRED DGS10 Δ80・XAU_daily_er.csv 土日除外）。
tail = (BUY∧Δ80<0)∨(SELL∧Δ80>0)、区間 = FRED 営業日行の Δ80 符号連続区間、モデル R ~ 区間FE + β·tail + γ·SELL (+ 統制)、区間クラスタ SE。
窓: 在 2010-20／外 2021-26／近年 2024-26。判定は外。

Q0 再現: β_FE+side 外 +0.1336 (t3.94)、μ_req(k) 外 2.1〜2.4 USD/日（c13b）。
Q1 局所ドリフト統制（T2 の判定）: 金の N 営業日ドリフト g_N（N∈{1,2,3,5,10,20,40,80}・known≤te・許容 5 日）を
   (a) 二値 ride_N = 1{side·g_N>0}、(b) 連続 side·g_N/sd の 2 形で 1 つずつ統制、(c) 全 N の ride を同時統制（kitchen sink）、
   (d) 区間内局所ドリフト g_int = lc(te) − lc(区間開始日)（side 符号・二値と連続）、(e) 直前 24h 継続 A24（c8 ret24h）。
   判定規則（外）: **broken（代理）** = cycle13 が名指しした 5 営業日統制 (a) で β_tail < 0.5·β0 または t<2。
   **survived（金利固有）** = 全ての単独統制 (a)(b)(d)(e) と (c) で β_tail ≥ 0.75·β0 ∧ t≥2 ∧ 近年 同符号。他 inconclusive。
   (c) の β について参照日 k 週循環シフト置換 300 回で p（⑨・帰無 sd の過分散を織り込む）。
Q2 診断の識別力（T1 の判定・プラセボ）: 「μ_req(k) 一定」は一定ドリフト固有の性質か。建玉時点で決まる別の群分け
   G ∈ {A24 継続, ride_80 金トレンド乗り, outer 壁, JST7-12 帯, atr 上位半分, open_gap 上位半分} について同じ道具で
   Δe(k)=e_G−e_¬G（e=R*−cl_k・区間FE+SELL）→ μ_req(k) = Δe/(2·mean((hold−k)/risk))·276 を k∈{0,3,6,12,24,48} で出し、
   平坦度 = CV（std/|mean| over k）と 比 μ(k48)/μ(k0)。
   判定規則: **診断は識別力あり** = |Δe(0)| t≥2 のプラセボ群の CV の中央値が tail の CV の 2 倍超。**識別力なし** = プラセボ群の
   半数以上が tail と同程度（CV ≤ 1.5×tail）。他 inconclusive。識別力なしなら T1 の「M_drift と整合」は無内容（どの群差でも出る形）。
Q3 用量反応（記述・金利固有の補助）: 区間FE 内で tail×|Δ80|（標準化）の係数。金利固有のドリフトなら正、代理なら ≈0。
Q4 別分割（記述）: 外の年別 β（統制なし／5d 統制あり）、外 LOYO 最小 t。
Q5 コスト倍: レジーム記述（両群同コスト）で diff 不変＝適用不能（明記のみ）。
look-ahead: g_N は known≤te（建玉足不使用）、FRED は cycle10 の利用可能規則、g_int の区間開始は avail 時点で既知の過去。
closed 全本（TIME 含む）。D2: 16 年プール不使用・窓別。seed 20261106。scan 無し・M5 原本読込なし・MT5 なし・外部通信なし。
"""
import os, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c13_driftsource.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c13] ドリフトの源は金利か金の局所ドリフトか／μ_req(k) 一定の識別力 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c13_driftsource.py)")

# ---------- trades ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); HOLD = X["hold"].to_numpy().astype(float); RISK = X["risk"].to_numpy()
EXIT = X["exit"].to_numpy(); ATR = X["atr"].to_numpy(); OG = X["open_gap"].to_numpy(); JH = X["jh"].to_numpy(); WK = X["wall_kind"].to_numpy()
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64); TE = X["te"].to_numpy().astype(np.int64)
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c1_et = np.sort(np.array([t["entry_time"] for t in J["trades"]])); assert np.array_equal(c1_et, X["entry_time"].to_numpy())
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"]
assert len(off) - 1 == N and np.all(np.diff(off) == HOLD + 1)
say(f"- 本 {N}、entry {X['ts_jst'].min().date()}〜{X['ts_jst'].max().date()} JST（⑩）、npz 規約 OK、FEED_TOL {FT}")

# ---------- FRED DGS10 Δ80 区間 ----------
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
IV_START = np.full(cur + 1, 0, dtype=np.int64)
for k in range(len(v)):
    if IVraw[k] >= 0 and (k == 0 or IVraw[k - 1] != IVraw[k]): IV_START[IVraw[k]] = FD[k]
def feats(ref, tol=10):
    i = np.searchsorted(FD, ref, side="right") - 1; ok = (i >= 0) & ((ref - FD[np.clip(i, 0, None)]) <= tol)
    ii = np.clip(i, 0, len(FD) - 1); F = D80[ii].copy(); IV = IVraw[ii].copy(); F[~ok] = np.nan; IV[~ok] = -1; IV[~np.isfinite(F)] = -1
    return F, IV
F, IV = feats(AVAIL); OK = np.isfinite(F) & (IV >= 0); TAIL = (OK & ((SGN * np.sign(F) * -1) > 0)).astype(float)
say(f"- FRED DGS10 {len(m)} 行〜{m['date'].iloc[-1].date()}、区間 {cur+1}、付与 {OK.mean()*100:.1f}%、tail 比 {TAIL[OK].mean():.3f}")

# ---------- 金 日足（土日除外）・局所ドリフト ----------
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); E["dt"] = pd.to_datetime(E["ts_last"], unit="s")
E = E[~E["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True)
kn = E["known"].to_numpy().astype(np.int64); lcb = E["lc"].to_numpy(); dayb = E["day"].to_numpy().astype(np.int64)
gi = np.searchsorted(kn, TE, side="right") - 1; gok = (gi >= 0) & ((TE - kn[np.clip(gi, 0, None)]) <= 5 * 86400)
assert np.all(kn[gi[gok]] <= TE[gok]), "look-ahead: known > te"
def gold_drift(Nd):
    g = np.full(N, np.nan); ok = gok & (gi - Nd >= 0); g[ok] = lcb[gi[ok]] - lcb[gi[ok] - Nd]; return g
HORIZ = (1, 2, 3, 5, 10, 20, 40, 80)
G = {Nd: gold_drift(Nd) for Nd in HORIZ}
RIDE = {Nd: np.where(np.isfinite(G[Nd]) & (G[Nd] != 0), (SGN * G[Nd] > 0).astype(float), np.nan) for Nd in HORIZ}
CONT = {Nd: SGN * G[Nd] / np.nanstd(G[Nd]) for Nd in HORIZ}
# 区間内局所ドリフト: 区間開始日（FRED 日付）の直前の金 close から te 時点の金 close まで
st_day = np.where(IV >= 0, IV_START[np.clip(IV, 0, None)], 0)
si = np.searchsorted(dayb, st_day, side="right") - 1
GINT = np.full(N, np.nan); okI = OK & gok & (si >= 0) & (gi > si)
GINT[okI] = lcb[gi[okI]] - lcb[si[okI]]
RIDE_INT = np.where(np.isfinite(GINT) & (GINT != 0), (SGN * GINT > 0).astype(float), np.nan)
CONT_INT = SGN * GINT / np.nanstd(GINT)
ELAPSED = np.where(okI, gi - si, np.nan)
ret24 = X["ret24h_XAU"].to_numpy(); A24 = np.where(np.isfinite(ret24) & (ret24 != 0), (SGN * ret24 > 0).astype(float), np.nan)
say(f"- 金 日足（土日除外）{len(E)} 行、g_N 付与 {gok.mean()*100:.1f}%、区間内ドリフト付与 {okI.mean()*100:.1f}%（区間内経過 中央値 {np.nanmedian(ELAPSED):.0f} 営業日）")
for Nd in HORIZ:
    mm = OK & np.isfinite(RIDE[Nd]); say(f"  ρ(tail, ride_{Nd}) {np.corrcoef(TAIL[mm], RIDE[Nd][mm])[0,1]:+.3f}", )
mm = OK & np.isfinite(RIDE_INT); say(f"  ρ(tail, ride_int) {np.corrcoef(TAIL[mm], RIDE_INT[mm])[0,1]:+.3f}、ρ(−sign(Δ80)·g_int) 外 {np.corrcoef(-np.sign(F[mm & (YEAR>=2021)]), GINT[mm & (YEAR>=2021)])[0,1]:+.3f}（金利追い風方向に金が実際に動いたか）")

W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
def within(v_, g):
    df = pd.DataFrame({"v": v_, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); Gc = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); Gc += 1
    V = ZtZi @ meat @ ZtZi * (Gc / max(Gc - 1, 1)); return beta, np.sqrt(np.diag(V)), Gc
def fe(y, mask, cols, iv=IV):
    mm = mask & (iv >= 0) & np.isfinite(y)
    for c in cols: mm &= np.isfinite(c)
    if mm.sum() < 30: return dict(b=np.full(len(cols), np.nan), t=np.full(len(cols), np.nan), G=0, n=int(mm.sum()))
    yy = within(y[mm], iv[mm]); Z = np.column_stack([within(c[mm], iv[mm]) for c in cols])
    b, se, Gc = ols_cluster(yy, Z, iv[mm]); return dict(b=b, t=b / np.where(se > 0, se, np.nan), G=Gc, n=int(mm.sum()), mask=mm)

# ---------- Q0 ----------
say("\n## Q0 再現（区間FE+SELL・区間クラスタ SE）")
B0 = {}
for wn, wm in W.items():
    r = fe(R, wm & OK, [TAIL, SELL]); B0[wn] = r["b"][0]
    say(f"- {wn}: β_tail **{r['b'][0]:+.4f} (t{r['t'][0]:+.2f}, 区間{r['G']}, n{r['n']})** γ_SELL {r['b'][1]:+.4f} (t{r['t'][1]:+.2f})")
beta0 = B0["外2021-26"]

# ---------- Q1 ----------
say("\n## Q1 局所ドリフト統制（T2 判定）— 係数は tail / SELL / 統制")
def q1row(label, cols, names):
    out = {}
    for wn in W:
        r = fe(R, W[wn] & OK, [TAIL, SELL] + cols); out[wn] = r
    r = out["外2021-26"]; ctrl = " ".join(f"{nm} {r['b'][2+i]:+.4f}(t{r['t'][2+i]:+.1f})" for i, nm in enumerate(names))
    say(f"- {label}: 外 tail **{r['b'][0]:+.4f} (t{r['t'][0]:+.2f}, n{r['n']})** [{r['b'][0]/beta0*100:.0f}% of β0] | {ctrl} | 在 tail {out['在2010-20']['b'][0]:+.4f} (t{out['在2010-20']['t'][0]:+.2f}) | 近年 tail {out['近年2024-26']['b'][0]:+.4f} (t{out['近年2024-26']['t'][0]:+.2f})")
    return out
Q1 = {}
say("### (a) 二値 ride_N（side と同向きの N 営業日ドリフト）")
for Nd in HORIZ: Q1[("a", Nd)] = q1row(f"ride_{Nd}d", [RIDE[Nd]], [f"ride_{Nd}"])
say("### (b) 連続 side·g_N / sd")
for Nd in HORIZ: Q1[("b", Nd)] = q1row(f"cont_{Nd}d", [CONT[Nd]], [f"cont_{Nd}"])
say("### (c) kitchen sink: 全 N の ride 同時 + A24")
KS_COLS = [RIDE[Nd] for Nd in HORIZ] + [A24]; KS_NAMES = [f"r{Nd}" for Nd in HORIZ] + ["A24"]
Q1[("c", 0)] = q1row("ride_all+A24", KS_COLS, KS_NAMES)
say("### (d) 区間内局所ドリフト g_int（区間開始→te）")
Q1[("d", "bin")] = q1row("ride_int", [RIDE_INT], ["ride_int"])
Q1[("d", "cont")] = q1row("cont_int", [CONT_INT], ["cont_int"])
Q1[("d", "both")] = q1row("ride_int+ride_5+ride_20", [RIDE_INT, RIDE[5], RIDE[20]], ["ride_int", "r5", "r20"])
say("### (e) 直前 24h 継続 A24")
Q1[("e", 0)] = q1row("A24", [A24], ["A24"])
# 判定
r5 = Q1[("a", 5)]["外2021-26"]
broken = (r5["b"][0] < 0.5 * beta0) or (r5["t"][0] < 2.0)
checks = []
for key in [("a", Nd) for Nd in HORIZ] + [("b", Nd) for Nd in HORIZ] + [("c", 0), ("d", "bin"), ("d", "cont"), ("d", "both"), ("e", 0)]:
    ro = Q1[key]["外2021-26"]; rr = Q1[key]["近年2024-26"]
    checks.append((ro["b"][0] >= 0.75 * beta0) and (ro["t"][0] >= 2.0) and (np.sign(rr["b"][0]) == np.sign(ro["b"][0])))
survived = all(checks)
# 置換 for (c)
lo_d = pd.Timestamp("2011-01-03"); hi_d = pd.Timestamp("2026-06-26"); span_w = (hi_d - lo_d).days // 7
lo_i = int(lo_d.to_datetime64().astype("datetime64[D]").astype(np.int64)); base_off = AVAIL - lo_i
NP = 300; nt = np.full(NP, np.nan); tp_ = time.time()
for p in range(NP):
    kk = int(rng.integers(8, span_w - 8)); sh = lo_i + (base_off + 7 * kk) % (span_w * 7); Fp, IVp = feats(sh)
    okp = np.isfinite(Fp) & (IVp >= 0); tailp = (okp & ((SGN * np.sign(Fp) * -1) > 0)).astype(float)
    nt[p] = fe(R, W["外2021-26"] & okp, [tailp, SELL] + KS_COLS, iv=np.where(okp, IVp, -1))["t"][0]
t_ks = Q1[("c", 0)]["外2021-26"]["t"][0]; perm_p = (np.abs(nt) >= abs(t_ks)).mean()
say(f"- 置換（(c) 外 β_tail・{NP} 回・{time.time()-tp_:.0f} s）: 帰無 sd {np.nanstd(nt):.2f}・95%点|t| {np.nanquantile(np.abs(nt),0.95):.2f}、観測 t {t_ks:+.2f} → **両側 p {perm_p:.3f}**")
Q1V = "broken（局所ドリフトの代理）" if broken else ("survived（金利固有）" if survived else "inconclusive")
say(f"- **Q1 判定: {Q1V}** — 5d 統制 β {r5['b'][0]:+.4f} (t{r5['t'][0]:+.2f}) [{r5['b'][0]/beta0*100:.0f}%]; 全統制 {sum(checks)}/{len(checks)} が ≥75%∧t≥2∧近年同符号")

# ---------- Q2 プラセボ: μ_req(k) の平坦度 ----------
say("\n## Q2 診断の識別力（T1）— 建玉時点の別の群分けでも μ_req(k) は一定か（外 2021-26・区間FE+SELL）")
BPD = 276.0
def mu_profile(grp, wm, ks=(0, 3, 6, 12, 24, 48)):
    prof = []; des = []
    for k in ks:
        alive = HOLD > k; idx = np.flatnonzero(alive); clk = np.full(N, np.nan); clk[idx] = clR[off[idx] + k] if k > 0 else 0.0
        e = RSTAR - clk; mm = wm & OK & alive & np.isfinite(grp)
        cols = [grp, SELL] if grp is not TAIL else [TAIL, SELL]
        r = fe(e, mm, cols); hr = ((HOLD[r["mask"]] - k) / RISK[r["mask"]]).mean() if r["G"] else np.nan
        mu = r["b"][0] / (2 * hr) * BPD if hr and hr > 0 else np.nan; prof.append(mu); des.append(f"k{k} Δe {r['b'][0]:+.3f}(t{r['t'][0]:+.1f}) μ {mu:+.2f}")
    prof = np.array(prof); cv = np.nanstd(prof) / abs(np.nanmean(prof)) if np.nanmean(prof) != 0 else np.nan
    return prof, cv, des
GROUPS = {
    "tail(金利追い風)": TAIL,
    "A24 継続": A24,
    "ride_80 金トレンド乗り": RIDE[80],
    "ride_5 金5d乗り": RIDE[5],
    "outer 壁": (WK == "outer").astype(float),
    "JST7-12": ((JH >= 7) & (JH <= 12)).astype(float),
    "atr 上位半分": (ATR > np.nanmedian(ATR)).astype(float),
    "open_gap 上位半分": (OG > np.nanmedian(OG)).astype(float),
}
wm_out = W["外2021-26"]; PROF = {}
for gname, grp in GROUPS.items():
    prof, cv, des = mu_profile(grp, wm_out); PROF[gname] = (prof, cv)
    say(f"- {gname}: " + " / ".join(des) + f" → **CV {cv:.2f}・μ(k48)/μ(k0) {prof[-1]/prof[0] if prof[0] else float('nan'):+.2f}**")
cv_tail = PROF["tail(金利追い風)"][1]
# t at k=0 for each placebo (significance of the group difference itself)
sig = {}
for gname, grp in GROUPS.items():
    if gname.startswith("tail"): continue
    r = fe(RSTAR, wm_out & OK, [grp, SELL]); sig[gname] = abs(r["t"][0])
plac = [g for g in sig if sig[g] >= 2.0]
cvs = np.array([PROF[g][1] for g in plac]) if plac else np.array([])
say(f"- 外で |Δe(0)| t≥2 のプラセボ群: {plac}（t: " + ", ".join(f"{g} {sig[g]:.1f}" for g in sig) + ")")
if len(plac) == 0: Q2V = "inconclusive（有意なプラセボ群なし）"
elif np.median(cvs) > 2 * cv_tail: Q2V = "診断は識別力あり"
elif (cvs <= 1.5 * cv_tail).sum() >= math.ceil(len(cvs) / 2): Q2V = "診断は識別力なし（どの群差でも μ_req(k) はほぼ一定）"
else: Q2V = "inconclusive"
say(f"- **Q2 判定: {Q2V}** — tail CV {cv_tail:.2f}、プラセボ CV {np.round(cvs,2).tolist()}（中央値 {np.median(cvs) if len(cvs) else float('nan'):.2f}）")
# 近年も記述
say("- 近年 2024-26（記述）:")
for gname in ("tail(金利追い風)", "A24 継続", "outer 壁", "atr 上位半分"):
    prof, cv, des = mu_profile(GROUPS[gname], W["近年2024-26"]); say(f"  - {gname}: CV {cv:.2f}・比 {prof[-1]/prof[0] if prof[0] else float('nan'):+.2f} | " + " / ".join(des))

# ---------- Q3 用量反応（区間FE 内） ----------
say("\n## Q3 用量反応（記述）: 区間FE + SELL + tail + tail×|Δ80|z（|Δ80| は外窓 sd で標準化・区間内は定数なので tail との交互作用のみ識別）")
absz = np.abs(F) / np.nanstd(F[OK & wm_out])
for wn, wm in W.items():
    r = fe(R, wm & OK, [TAIL, SELL, TAIL * absz]); say(f"- {wn}: tail {r['b'][0]:+.4f} (t{r['t'][0]:+.2f}) tail×|Δ80|z {r['b'][2]:+.4f} (t{r['t'][2]:+.2f}) n{r['n']}")
# 同じく金の局所ドリフト大きさとの交互作用（代理なら g_int の大きさに乗る）
absg = np.abs(GINT) / np.nanstd(GINT[OK & wm_out])
for wn, wm in W.items():
    r = fe(R, wm & OK, [TAIL, SELL, RIDE_INT, TAIL * absz, TAIL * absg]); say(f"- {wn}: tail {r['b'][0]:+.4f} (t{r['t'][0]:+.2f}) ride_int {r['b'][2]:+.4f} (t{r['t'][2]:+.2f}) tail×|Δ80|z {r['b'][3]:+.4f} (t{r['t'][3]:+.2f}) tail×|g_int|z {r['b'][4]:+.4f} (t{r['t'][4]:+.2f})")

# ---------- Q4 別分割 ----------
say("\n## Q4 別分割（外 年別・統制なし／ride_5 統制／kitchen sink）と LOYO")
for yr in range(2021, 2027):
    wm = YEAR == yr; a = fe(R, wm & OK, [TAIL, SELL]); b = fe(R, wm & OK, [TAIL, SELL, RIDE[5]]); c = fe(R, wm & OK, [TAIL, SELL] + KS_COLS)
    say(f"- {yr}: β {a['b'][0]:+.4f} (t{a['t'][0]:+.2f}, 区間{a['G']}, n{a['n']}) | +ride_5 {b['b'][0]:+.4f} (t{b['t'][0]:+.2f}) | +KS {c['b'][0]:+.4f} (t{c['t'][0]:+.2f})")
loyo = []
for yr in range(2021, 2027):
    wm = wm_out & (YEAR != yr); c = fe(R, wm & OK, [TAIL, SELL] + KS_COLS); loyo.append((yr, c["b"][0], c["t"][0]))
say("- LOYO（KS 統制）: " + " / ".join(f"除{y} {b:+.4f} (t{t:+.2f})" for y, b, t in loyo) + f" → 最小 t {min(t for _,_,t in loyo):+.2f}")
say("\n## Q5 コスト倍: レジーム記述（tail/head 同コスト）で diff 不変＝適用不能。")
say(f"\n## 判定まとめ: Q1 {Q1V} ／ Q2 {Q2V}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
