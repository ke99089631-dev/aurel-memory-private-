# -*- coding: utf-8 -*-
"""
[cycle13 研究レーン] 2026-11-06 — 【深化・機構】DGS10 Δ80 追い風セル（反証 08:30 → cycle12 → 反証 11:30 で生き残り）の
経済機構を **検証前に 2 つ書き**、それぞれが予測する「別の観測」を同じキャッシュで確かめる（反証 11:30 の提案 (b)）。

=== 事前固定（この docstring を書いてから数字を見る） ===
対象セル: tail = (BUY ∧ Δ80<0) ∨ (SELL ∧ Δ80>0)（FRED DGS10 営業日行 80 行差・利用可能規則 cycle10/12 と同一）。
  外 2021-26 の β_FE+side（区間FE＋SELL 主効果・区間クラスタ SE）= +0.134R（反証 11:30）。本サイクルはまず Q0 で再現。

機構 M_drift（背景ドリフト）: 金利トレンドは金に「保有時間尺度（数時間）の方向性ドリフト」を伴う。壁抜けがドリフトと
  同方向なら、拡散経路にドリフトが足されるだけで TP 到達率が上がる。
  予測 D1（量的予算）: ドリフト μ[USD/本] が本の R に寄与する量は s_j·μ·hold_j/risk_j（s=±1 向きの整合）なので、
     tail−head の差 ≈ 2·μ·mean(hold/risk)。必要な μ_req = β / (2·mean(hold/risk))。これを「金利レジームで条件づけた
     金の実測ドリフト」（取引非依存・擬似日 22:00 UTC・外 2021-26・土日擬似日除外・FRED 利用可能規則）と比べる。
     予算比 = 2·μ_obs·mean(hold/risk) / β。
  予測 D2: 差は TP 距離 b（事前決定の共変量）が大きいほど大きい（ドリフトは時間で積む）。
  予測 D3: 建玉直後（k=3〜6 本）の含み差はほぼ 0（1 本あたりのドリフトは微小）。
機構 M_flow（状態依存のフォロースルー）: 壁抜けがマクロ地合いと整合する時、トレンド/マクロ参加者が抜けを「確認」として
  追随し、直後に流れが乗る。逆らう抜けは即座に戻される。
  予測 F1: 効果は経路の早期に現れる＝固定 k（hold>k）での cl_k（含み R）の tail−head が k=6 で既に正。
  予測 F2: 差は b に単調でない（TP 率の差が b に依らず現れる）。
  予測 F3: 取引非依存のドリフト予算は不足（D1 の否定）。

判定規則（事前固定・外 2021-26・主セル 2）:
  J1 予算比 r = 2·μ_obs·mean(hold/risk)/β（μ_obs は擬似日次の条件付きドリフト／取引本数換算 276 本/日）。
     r < 0.2 → M_drift は単独機構として量的に不足（棄却）。r ≥ 0.5 → 十分。他 inconclusive。
     符号が負（2021-26 の金が金利上昇中に上がる＝切り離し）なら M_drift は方向からも不成立。
  J2 早期含み差: cl_6（hold>6・建玉足 index0 は約定前レンジ混入のため k≥3）の tail−head を区間FE+SELL・区間クラスタ SE で。
     PASS(M_flow 支持) = t ≥ 2.0 ∧ 近年 同符号。FAIL = |t| < 1.0。他 inconclusive。置換（参照日 k 週循環シフト 500 回・⑨）で p。
     補助: 同じ hold>6 部分集合での最終 R*（R+ft·1{SL/TP}）の差に対する cl_6 差の割合（早期に実現した割合）。
  記述（判定に使わない）: k=3/12/24、出口分解（TP 率・SL 率・E[R|TP]・E[R|SL]・hold・mfe1・mae1）、b 三分位の差（D2/F2）、
     取引時点からの金の前向き 4h/24h リターンを −sign(Δ80) で符号づけ（取引時刻条件付きドリフト・側非依存）、在/近年。
機構判定（事前の読み）: J1 棄却 ∧ J2 PASS → 「金利地合いに整合する抜けが早期にフォローされる」M_flow を支持（構造仮説の候補）。
  J1 棄却 ∧ J2 FAIL → 両機構とも不支持＝効果は TP 到達の後期過程（記述で場所を探す・新仮説は別サイクル）。
  J1 十分 → M_drift で説明可＝「金利トレンド中の金のドリフト」に還元（新規性低）。
入力: data/c8_crossasset_features.csv（19404 本・R gross・exit/hold/b/risk/mfe1/mae1）、data/c1_reaccel_paths_2010_2026.json（ソート順と FEED_TOL）、
  data/refute_c2_fullpaths.npz（clR/off・index0=建玉足・長さ hold+1）、data/macro/DGS10.csv、data/macro/XAU_daily_er.csv、data/macro/XAU_m5_close.npz。
scan 無し・M5 原本読込なし・MT5 なし・外部通信なし。D2: 16 年プール不使用・窓別。昇格候補ではない。seed 20261106。
"""
import os, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c13_mechanism_budget_result.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle13] DGS10 Δ80 追い風セルの機構予算テスト — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c13_mechanism_budget.py)")

# ---------- trades ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
N = len(X); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); SELL = (SGN < 0).astype(float)
R = X["R"].to_numpy(); YEAR = X["year"].to_numpy(); HOLD = X["hold"].to_numpy().astype(float); RISK = X["risk"].to_numpy()
B = X["b"].to_numpy(); EXIT = X["exit"].to_numpy(); MFE1 = X["mfe1"].to_numpy(); MAE1 = X["mae1"].to_numpy()
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
TE = X["te"].to_numpy().astype(np.int64)
say(f"- 本 {N}（closed 全本・TIME 含む）、entry {X['ts_jst'].min().date()}〜{X['ts_jst'].max().date()} JST（⑩）、exit 内訳 {dict(pd.Series(EXIT).value_counts())}")

J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c1 = pd.DataFrame([{k: t[k] for k in ("entry_time", "hold", "risk", "exit_reason")} for t in J["trades"]]).sort_values("entry_time").reset_index(drop=True)
assert np.array_equal(c1["entry_time"].to_numpy(), X["entry_time"].to_numpy()), "c1 と c8 の entry_time 不一致"
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"]
assert len(off) - 1 == N and np.all(np.diff(off) == c1["hold"].to_numpy() + 1), "npz 規約不一致"
IS_SLT = np.isin(EXIT, ["SL", "TP"]); RSTAR = R + ft * IS_SLT
say(f"- npz 規約 assert OK（長さ hold+1・index0 建玉足）、FEED_TOL {FT}、ft 平均 {ft.mean():.4f}R、R* 平均 {RSTAR.mean():+.4f}（gross {R.mean():+.4f}）")

# ---------- FRED DGS10 Δ80 + 符号区間 ----------
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
say(f"- FRED DGS10 {len(m)} 行 {m['date'].iloc[0].date()}〜{m['date'].iloc[-1].date()}、符号区間 {cur+1}")
def feats(ref, tol=10):
    i = np.searchsorted(FD, ref, side="right") - 1; ok = (i >= 0) & ((ref - FD[np.clip(i, 0, None)]) <= tol)
    ii = np.clip(i, 0, len(FD) - 1); F = D80[ii].copy(); IV = IVraw[ii].copy(); F[~ok] = np.nan; IV[~ok] = -1; IV[~np.isfinite(F)] = -1
    return F, IV
F, IV = feats(AVAIL); OK = np.isfinite(F) & (IV >= 0); TAIL = OK & ((SGN * np.sign(F) * -1) > 0); S_RATE = -np.sign(F)  # 金利追い風の向き（+1=上、−1=下）
say(f"- 付与 {OK.mean()*100:.1f}%、tail 比 {TAIL[OK].mean():.3f}、n 内訳 BUY∧Δ80<0 {int(((SGN>0)&(F<0)).sum())} / BUY∧Δ80>0 {int(((SGN>0)&(F>0)).sum())} / SELL∧Δ80>0 {int(((SGN<0)&(F>0)).sum())} / SELL∧Δ80<0 {int(((SGN<0)&(F<0)).sum())}")

W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
def within(v_, g):
    df = pd.DataFrame({"v": v_, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); G = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G += 1
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G
def fe(y, mask, tail=TAIL, iv=IV):
    mm = mask & (iv >= 0) & np.isfinite(y)
    if mm.sum() < 30 or tail[mm].sum() < 5 or (~tail[mm]).sum() < 5: return dict(b=np.nan, se=np.nan, t=np.nan, G=0, n=int(mm.sum()))
    yy = within(y[mm], iv[mm]); Z = np.column_stack([within(tail[mm].astype(float), iv[mm]), within(SELL[mm], iv[mm])])
    beta, se, G = ols_cluster(yy, Z, iv[mm]); return dict(b=beta[0], se=se[0], t=beta[0] / se[0] if se[0] > 0 else np.nan, G=G, n=int(mm.sum()))
def fmt(r, d=4): return f"{r['b']:+.{d}f} (t{r['t']:+.2f}, 区間{r['G']}, n{r['n']})"
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se if se > 0 else np.nan

say("\n## Q0 再現（β_FE+side・区間FE＋SELL・区間クラスタ SE）と生 Welch")
BETA = {}
for wn, wm in W.items():
    r = fe(R, wm & OK); BETA[wn] = r["b"]; d, t = welch(R[wm & OK & TAIL], R[wm & OK & ~TAIL])
    say(f"- {wn}: β_FE+side **{fmt(r)}**、生 tail−head {d:+.4f} (t{t:+.2f})")
beta_out = BETA["外2021-26"]

# ---------- J1 ドリフト予算（取引非依存・擬似日） ----------
say("\n## J1 ドリフト予算（M_drift の量的検査）")
E = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv"))
day = E["day"].to_numpy().astype(np.int64); lc = E["lc"].to_numpy()
wd = (day + 3) % 7  # Monday=0（1970-01-01 木曜）
keep = wd <= 4
Eb = pd.DataFrame({"day": day[keep], "lc": lc[keep]}).reset_index(drop=True)
# 擬似日 d（22:00 UTC d−1 → 22:00 UTC d）。開始時点 JST 07:00 の d に利用可能な FRED 日付は d−1。
Fd, IVd = feats(Eb["day"].to_numpy() - 1); s_d = -np.sign(Fd)  # 金利追い風の向き
ret1 = np.full(len(Eb), np.nan); ret1[1:] = Eb["lc"].to_numpy()[1:] - Eb["lc"].to_numpy()[:-1]  # 擬似日 d の収益（d−1 close → d close）
ret5 = np.full(len(Eb), np.nan); ret5[1:-4] = Eb["lc"].to_numpy()[5:] - Eb["lc"].to_numpy()[:-5]  # 擬似日 d 開始（d−1 close）→ d+4 close
price = np.exp(Eb["lc"].to_numpy())
yr_d = pd.to_datetime(Eb["day"], unit="D").dt.year.to_numpy()
BARS_PER_DAY = 276.0
say(f"- 擬似日（土日除外）{len(Eb)} 日 {pd.to_datetime(Eb['day'].min(), unit='D').date()}〜{pd.to_datetime(Eb['day'].max(), unit='D').date()}、Δ80 付与 {np.isfinite(Fd).mean()*100:.1f}%、flat 日（ret1=0）{(ret1==0).mean()*100:.1f}%")
WD = {"在2010-20": (yr_d >= 2010) & (yr_d <= 2020), "外2021-26": yr_d >= 2021, "近年2024-26": yr_d >= 2024}
MU = {}
for wn, wm in WD.items():
    mm = wm & np.isfinite(Fd) & np.isfinite(ret1) & (ret1 != 0)
    sr = s_d[mm] * ret1[mm]; usd = sr * price[mm]  # 追い風方向に符号づけた日次 USD 変化
    t1 = sr.mean() / (sr.std(ddof=1) / math.sqrt(len(sr)))
    mm5 = wm & np.isfinite(Fd) & np.isfinite(ret5); sr5 = s_d[mm5] * ret5[mm5]
    mu_bar = usd.mean() / BARS_PER_DAY; MU[wn] = mu_bar
    # 無条件（金利の向きを見ない）の金の日次ドリフト
    say(f"- {wn}: 符号づけ日次リターン 平均 {sr.mean()*1e4:+.2f} bp/日 (t{t1:+.2f}, n{len(sr)})、5 日 {sr5.mean()*1e4:+.2f} bp、USD/日 {usd.mean():+.3f} → μ_obs {mu_bar:+.5f} USD/本；"
        f" 参考 無条件 金日次 {ret1[mm].mean()*1e4:+.2f} bp/日、正区間比率 {(Fd[mm]>0).mean():.2f}、ρ(Δ80, ret1) {np.corrcoef(Fd[mm], ret1[mm])[0,1]:+.3f}")
# 予算
for wn, wm in W.items():
    mm = wm & OK; hr = (HOLD[mm] / RISK[mm]).mean(); beta = BETA[wn]
    mu_req = beta / (2 * hr) if hr > 0 else np.nan; implied = 2 * MU[wn] * hr; ratio = implied / beta if beta != 0 else np.nan
    say(f"- {wn}: mean(hold/risk) {hr:.3f} 本/USD（hold 平均 {HOLD[mm].mean():.1f} 本・中央値 {np.median(HOLD[mm]):.0f}・risk 平均 {RISK[mm].mean():.2f} USD）、β {beta:+.4f} → 必要 μ_req {mu_req:+.5f} USD/本 (= {mu_req*BARS_PER_DAY:+.2f} USD/日)、"
        f"実測 μ_obs {MU[wn]:+.5f} → 含意される差 {implied:+.4f}R、**予算比 r = {ratio:+.3f}**")
r_out = 2 * MU["外2021-26"] * (HOLD[W["外2021-26"] & OK] / RISK[W["外2021-26"] & OK]).mean() / beta_out
J1 = "M_drift 不足（棄却）" if r_out < 0.2 else ("M_drift 十分" if r_out >= 0.5 else "inconclusive")
say(f"- **J1 判定（外）: 予算比 {r_out:+.3f} → {J1}**" + ("（符号負＝金利上昇中に金が上がる・方向からも不成立）" if r_out < 0 else ""))

# 取引時点条件付きの前向きドリフト（側非依存・−sign(Δ80) で符号づけ）
say("\n### 取引時刻からの金の前向きリターン（側非依存・金利追い風方向に符号づけ・XAU_m5_close.npz）")
zc = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zc["ts"].astype(np.int64); cl = zc["close"]
say(f"- npz {len(ts)} 本 {pd.to_datetime(ts.min(), unit='s')}〜{pd.to_datetime(ts.max(), unit='s')} UTC（⑩）")
def px(t_):
    i = np.searchsorted(ts, t_, side="right") - 1; return cl[np.clip(i, 0, len(cl) - 1)]
p0 = px(TE)
for H, lab in ((4 * 3600, "4h"), (24 * 3600, "24h"), (5 * 86400, "5d")):
    fw = np.log(px(TE + H)) - np.log(p0); sf = S_RATE * fw
    for wn, wm in W.items():
        mm = wm & OK & np.isfinite(sf); t = sf[mm].mean() / (sf[mm].std(ddof=1) / math.sqrt(mm.sum()))
        usd = (sf[mm] * p0[mm]).mean(); inR = (sf[mm] * p0[mm] / RISK[mm]).mean()
        say(f"- {lab} {wn}: 符号づけ前向き {sf[mm].mean()*1e4:+.2f} bp (t{t:+.2f}, n{mm.sum()})、{usd:+.3f} USD、R 換算 {inR:+.4f}R（β {BETA[wn]:+.4f} の {inR/BETA[wn]*100 if BETA[wn] else float('nan'):+.0f}%）")

# ---------- J2 早期含み差 ----------
say("\n## J2 早期含み差 cl_k（hold>k・区間FE+SELL・区間クラスタ SE）と最終 R* の差")
RES = {}
for k in (3, 6, 12, 24):
    alive = HOLD > k; clk = np.full(N, np.nan); idx = np.flatnonzero(alive); clk[idx] = clR[off[idx] + k]
    row = []
    for wn, wm in W.items():
        rc = fe(clk, wm & OK & alive); rf = fe(RSTAR, wm & OK & alive); RES[(k, wn)] = (rc, rf)
        share = rc["b"] / rf["b"] * 100 if rf["b"] else np.nan
        row.append(f"{wn}: cl_{k} {fmt(rc)} / 最終 R* {fmt(rf)} / 早期割合 {share:+.0f}%")
    say(f"- k={k}（建玉中 {alive.sum()} 本）: " + " ｜ ".join(row))
rc6 = RES[(6, "外2021-26")][0]; rc6r = RES[(6, "近年2024-26")][0]
# 置換（参照日 k 週循環シフト）
lo_d = pd.Timestamp("2011-01-03"); hi_d = pd.Timestamp("2026-06-26"); span_w = (hi_d - lo_d).days // 7
lo_i = int(lo_d.to_datetime64().astype("datetime64[D]").astype(np.int64)); base_off = AVAIL - lo_i
alive6 = HOLD > 6; cl6 = np.full(N, np.nan); i6 = np.flatnonzero(alive6); cl6[i6] = clR[off[i6] + 6]
NP = 500; nt = np.full(NP, np.nan); tp_ = time.time()
for p in range(NP):
    kk = int(rng.integers(8, span_w - 8)); sh = lo_i + (base_off + 7 * kk) % (span_w * 7); Fp, IVp = feats(sh)
    okp = np.isfinite(Fp) & (IVp >= 0); tailp = okp & ((SGN * np.sign(Fp) * -1) > 0)
    nt[p] = fe(cl6, W["外2021-26"] & okp & alive6, tail=tailp, iv=np.where(okp, IVp, -1))["t"]
perm_p = (np.abs(nt) >= abs(rc6["t"])).mean()
say(f"- 置換（外 cl_6・{NP} 回・{time.time()-tp_:.0f} s）: 帰無 sd {np.nanstd(nt):.2f}・95%点|t| {np.nanquantile(np.abs(nt),0.95):.2f}、**両側 p {perm_p:.3f}**")
if rc6["t"] >= 2.0 and np.sign(rc6r["b"]) == np.sign(rc6["b"]) and perm_p < 0.05: J2 = "PASS（M_flow 支持）"
elif abs(rc6["t"]) < 1.0: J2 = "FAIL（早期に差なし）"
else: J2 = "inconclusive"
say(f"- **J2 判定（外 cl_6）: {fmt(rc6)}・近年 {fmt(rc6r)}・置換 p {perm_p:.3f} → {J2}**")

# ---------- 記述: 出口分解 ----------
say("\n## 記述: 出口分解（tail−head・区間FE+SELL）")
for wn, wm in W.items():
    mm = wm & OK
    parts = []
    for lab, y in (("P(TP)", (EXIT == "TP").astype(float)), ("P(SL)", (EXIT == "SL").astype(float)), ("hold", HOLD), ("mfe1", MFE1), ("mae1", MAE1), ("b", B), ("risk", RISK)):
        parts.append(f"{lab} {fmt(fe(y, mm), 3)}")
    # E[R|TP], E[R|SL]
    for lab, ex in (("E[R|TP]", "TP"), ("E[R|SL]", "SL")):
        d, t = welch(R[mm & TAIL & (EXIT == ex)], R[mm & ~TAIL & (EXIT == ex)]); parts.append(f"{lab} {d:+.3f} (t{t:+.2f})")
    say(f"- {wn}: " + " / ".join(parts))
    # 分解: ΔE[R] ≈ ΔP(TP)·(E[R|TP]−E[R|SL])
    pt_ = fe((EXIT == "TP").astype(float), mm)["b"]; gap = R[mm & (EXIT == "TP")].mean() - R[mm & (EXIT == "SL")].mean()
    say(f"  → ΔP(TP)×(E[R|TP]−E[R|SL]) = {pt_:+.4f}×{gap:.3f} = {pt_*gap:+.4f}R（β {BETA[wn]:+.4f} の {pt_*gap/BETA[wn]*100 if BETA[wn] else float('nan'):.0f}%）")

say("\n## 記述: b 三分位（D2 ドリフト予測＝単調増加／F2 非単調）・hold 三分位は結果依存なので参考")
for wn, wm in W.items():
    mm = wm & OK; q = np.nanquantile(B[mm], [1 / 3, 2 / 3]); row = []
    for lab, sel in (("b低", B <= q[0]), ("b中", (B > q[0]) & (B <= q[1])), ("b高", B > q[1])):
        row.append(f"{lab}(≤{q[0]:.2f}/≤{q[1]:.2f}) {fmt(fe(R, mm & sel), 3)}")
    say(f"- {wn}: " + " / ".join(row))
for wn, wm in W.items():
    mm = wm & OK; q = np.nanquantile(HOLD[mm], [1 / 3, 2 / 3]); row = []
    for lab, sel in (("hold短", HOLD <= q[0]), ("hold中", (HOLD > q[0]) & (HOLD <= q[1])), ("hold長", HOLD > q[1])):
        row.append(f"{lab}(≤{q[0]:.0f}/≤{q[1]:.0f}) {fmt(fe(R, mm & sel), 3)}")
    say(f"- {wn}（参考・結果依存）: " + " / ".join(row))

say("\n## 記述: 早期 path の形（外・hold>k の cl_k を k=1..12 で・区間FE+SELL・b と t）")
row = []
for k in range(1, 13):
    alive = HOLD > k; clk = np.full(N, np.nan); idx = np.flatnonzero(alive); clk[idx] = clR[off[idx] + k]
    r = fe(clk, W["外2021-26"] & OK & alive); row.append(f"k{k} {r['b']:+.3f}(t{r['t']:+.1f},n{r['n']})")
say("- " + " / ".join(row))
# 同じく mfe/mae の早期（hiR/loR の累積最大・最小）k=6
hiR = z["hiR"]; loR = z["loR"]
alive = HOLD > 6; idx = np.flatnonzero(alive)
mfe6 = np.full(N, np.nan); mae6 = np.full(N, np.nan)
mfe6[idx] = [hiR[off[i] + 1: off[i] + 7].max() for i in idx]; mae6[idx] = [loR[off[i] + 1: off[i] + 7].min() for i in idx]
for wn, wm in W.items():
    say(f"- {wn} k≤6 の MFE(1..6) tail−head {fmt(fe(mfe6, wm & OK & alive), 3)} / MAE(1..6) {fmt(fe(mae6, wm & OK & alive), 3)}")

say(f"\n## 機構判定（事前の読み）: J1 {J1} ／ J2 {J2}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
