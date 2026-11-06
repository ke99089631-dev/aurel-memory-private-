# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-07 08:15 反証レーン] 対象: cycle19 (06:50) の読み
  C1「在 2010-20 は多時間地平の正自己相関（VR48 1.049 z2.7・VR144 1.100 z3.7）／外 2021-26H1 はどの地平も随機歩行（z<1）」
  C2「5 分 lag1 の負自己相関（在 −0.019 t−6.2）は 2021+ で消えた＝配信・流動性の微細構造変化」
  C3「H_D null＝前月 VR48 は翌月 R*̄ を条件づけない」（代理変数ノイズの null か）
事前固定の判定 H_E null／H_D null は再現して争わない。

=== 攻撃の仮説（数字を見る前に固定）===
A. **日内ボラ季節性による機械的 VR>1**。cycle19 の r_q は「同セッション日・途中閉場 0」の窓だけ有効 → q=144 の窓はセッション開始から
   144 本以降（ET 06:00 以降に終わる＝ロンドン/NY の高ボラ帯）に限られる。一方 分母 q·Var(r_1) は Asia の静かな帯を含む全日平均。
   ⇒ 自己相関 0 でも VR(q) は q と共に 1 を超える（VR12 0.98 < VR48 1.05 < VR144 1.10 の単調増加・全年で VR144>1 がこれで出る）。
   検定: (A1) 符号反転プラセボ: r_1 に独立な ±1 を掛けて再累積（自己相関 0・|r| の季節性と不均一分散は保存）→ 同じ有効窓で VR(q) を 20 回。
         (A2) 解析的期待値: 年別・スロット別（セッション開始からの 5 分番号）分散 v(s) で E_RW[VR(q)] = mean_窓 Σv / (q·s1)。
         (A3) 季節性除去: r_1 / sd_年(slot) で標準化して VR(q) を再計算（RW なら →1）。
   規則: 在 VR144 の超過 (VR−1) のうちプラセボが ≥50% を説明 or 補正 z_c=(VR−E_plc)/√θ < 2 → C1 前半「在に正自己相関」**broken**。
B. **プール z と年別の不一致**。外プール VR は分散加重（高ボラ 2026H1 VR 0.90 が支配）。年別表では外 6 年中 VR144 z≥2 が 4 年。
   規則: 補正後 年別 VR144 z_c≥2 が外 6 年中 ≥3 → 「外は随機歩行」broken。補正後 0〜1 年 → 年別の有意は季節性で、C1 後半は別の理由で survive。
   多重検定: 年別 51 セル（17 年×3 q）の |z|≥2 件数を補正前後で印字（帰無期待 ≈2.3）。
C. **ρ1 の消滅時期と機構**。年別表は 2022 でも t−2.8。規則: 2021-22 プール ρ1 t≤−2 → 「2021+ で消えた」broken（2023+ が正しい境）。
   機構の切り分け（記述）: ET 時間帯別（18–01/02–07/08–16）・零リターン対を除外・US100/US500 の同統計（年別・非零対）で
   「金固有 vs 配信一般」・年別 ρ1 と 1/価格（tick 離散性）の Spearman。
D. **H_D の代理変数**。季節性除去後の月別 VR48 で同じ 1 セル（前月→翌月 R*̄・WLS・在 t≥2 ∧ 外 t≥1.5 ∧ 置換 p<0.05）。
   PASS なら「null は代理のノイズ」、null なら C3 survive。
在外・窓・取引足・セッション日・有効窓・LM θ は cycle19 と同一コード。再現 assert: 在 VR48 1.049／VR144 1.100／ρ1 −0.0192、外 VR48 1.011（1e-3）。
入力は既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し。seed 20261107. 書き込み: data/refute_c19_vr.md のみ。
"""
import os, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c19_vr.md")
NY = "America/New_York"
rng = np.random.default_rng(20261107)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c19] 日内 VR(q) の季節性アーティファクトと ρ1 の境界 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c19_vr.py)")

# ---------- grid (identical to cycle19) ----------
def load_grid(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    return ts, cl
ts, cl = load_grid("XAU"); lc = np.log(cl); n = len(ts)
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert(NY)
h = t_ny.hour.to_numpy(); wd = t_ny.weekday.to_numpy(); mi = t_ny.minute.to_numpy()
sess_dt = t_ny + pd.Timedelta(hours=6)
SESS = (sess_dt.year * 10000 + sess_dt.month * 100 + sess_dt.day).to_numpy()
SYR = sess_dt.year.to_numpy(); SMO = (sess_dt.year * 100 + sess_dt.month).to_numpy()
SLOT = (((h + 6) % 24) * 60 + mi) // 5          # 0 = 18:00 ET session start, 275 = 16:55 ET, 276..287 = 17:00-17:55 closed
closed = (wd == 5) | ((wd == 4) & (h >= 17)) | ((wd == 6) & (h < 18)) | ((wd <= 3) & (h == 17))
trade = ~closed
r1 = np.zeros(n); r1[1:] = np.diff(lc)
ccl = np.cumsum(closed.astype(np.int64))
def valid_q(q):
    v = np.zeros(n, bool)
    v[q:] = (SESS[q:] == SESS[:-q]) & ((ts[q:] - ts[:-q]) == 300 * q) & ((ccl[q:] - ccl[:-q]) == 0) & trade[q:]
    return v
V1 = valid_q(1)
QS = [12, 48, 144]
VQ = {q: valid_q(q) for q in QS}
say(f"- npz {n} 本・有効 r_1 {V1.sum()}・有効窓 q12 {VQ[12].sum()} q48 {VQ[48].sum()} q144 {VQ[144].sum()}")
# where do valid windows end (slot) -> show the selection
for q in QS:
    s = SLOT[VQ[q]]; say(f"- q={q} 有効窓の終端 slot: min {s.min()} (ET {(18 + s.min()*5//60) % 24:02d}:{(s.min()*5) % 60:02d}) 〜 max {s.max()}・r_1 の slot 範囲 {SLOT[V1].min()}〜{SLOT[V1].max()}")

def vr_point(mask, q, r, R):
    m1 = mask & V1; x = r[m1]; mu = x.mean(); s1 = ((x - mu) ** 2).mean()
    y = R[q][mask & VQ[q]]
    return (((y - q * mu) ** 2).mean()) / (q * s1)
def theta_lm(mask, q, r):
    m1 = mask & V1; x = r[m1]; mu = x.mean()
    i = np.flatnonzero(m1); d = r - mu; den = (d[i] ** 2).sum() ** 2
    th = 0.0
    for k in range(1, q):
        j = i[i >= k]; ok = m1[j - k] & (SESS[j] == SESS[j - k]) & ((ts[j] - ts[j - k]) == 300 * k); j = j[ok]
        th += (2 * (q - k) / q) ** 2 * (((d[j] ** 2) * (d[j - k] ** 2)).sum() / den)
    return th
def cumR(r):
    c = np.cumsum(r); R = {}
    for q in QS:
        R[q] = np.full(n, np.nan); R[q][q:] = c[q:] - c[:-q]
    return R
RQ = cumR(r1)
def acf_t(mask, k, r=r1, extra=None):
    i = np.flatnonzero(mask & V1); i = i[i >= k]
    ok = V1[i - k] & (SESS[i] == SESS[i - k]) & ((ts[i] - ts[i - k]) == 300 * k) & ((ccl[i] - ccl[i - k]) == 0)
    i = i[ok]
    if extra is not None: i = i[extra[i] & extra[i - k]]
    if len(i) < 100: return np.nan, np.nan, len(i)
    a = r[i]; b = r[i - k]; mu = r[mask & V1].mean(); a = a - mu; b = b - mu
    return (a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum()), (a * b).sum() / math.sqrt(((a * a) * (b * b)).sum()), len(i)

WIN = {"在2010-20": (SYR >= 2010) & (SYR <= 2020), "外2021-26H1": SYR >= 2021, "近年2024-26H1": SYR >= 2024}
# ---------- reproduce ----------
say("\n## 0. 再現（cycle19 と同一定義）")
rep = {}
for wn, wm in WIN.items():
    rep[wn] = {q: vr_point(wm, q, r1, RQ) for q in QS}
    rho1, t1, _ = acf_t(wm, 1)
    say(f"- {wn}: VR12 {rep[wn][12]:.3f}・VR48 {rep[wn][48]:.3f}・VR144 {rep[wn][144]:.3f}・ρ1 {rho1:+.4f} (t{t1:+.1f})")
assert abs(rep["在2010-20"][48] - 1.049) < 1.5e-3 and abs(rep["在2010-20"][144] - 1.100) < 1.5e-3 and abs(rep["外2021-26H1"][48] - 1.011) < 1.5e-3, "再現失敗"
say("- assert OK（在 VR48 1.049／VR144 1.100／外 VR48 1.011）")

# ---------- A. seasonality ----------
say("\n## A. 日内ボラ季節性は VR(q)>1 を自己相関なしで作るか")
# per-year slot variance profile
yrs = np.unique(SYR[V1])
sd_slot = np.ones(n)
VSLOT = {}
for y in yrs:
    m = (SYR == y) & V1
    df = pd.DataFrame({"s": SLOT[m], "x": r1[m]})
    g = df.groupby("s").x.agg(["var", "size"])
    v = g["var"].reindex(range(288)).to_numpy(); v = np.where(np.isfinite(v), v, np.nanmedian(v))
    VSLOT[y] = v
    idx = np.flatnonzero(SYR == y); sd_slot[idx] = np.sqrt(v[SLOT[idx]])
# print profile summary for one window: variance by ET hour block relative to day mean (在)
m = WIN["在2010-20"] & V1
prof = pd.DataFrame({"hb": ((SLOT[m] * 5) // 60), "x2": r1[m] ** 2}).groupby("hb").x2.mean()
prof = prof / prof.mean()
say("- 在 時間帯別 r_1² / 全日平均（slot 時 = セッション開始 18:00 ET からの時間）: " + " ".join(f"h{int(k)}:{v:.2f}" for k, v in prof.items()))

def expected_vr_rw(mask, q):
    """analytic E[VR(q)] under RW with deterministic slot variance (per-year profile): mean over valid windows of sum v / (q * s1)"""
    m1 = mask & V1; s1 = np.mean(r1[m1] ** 2) - np.mean(r1[m1]) ** 2
    idx = np.flatnonzero(mask & VQ[q])
    tot = 0.0
    for y in np.unique(SYR[idx]):
        ii = idx[SYR[idx] == y]; cv = np.concatenate([[0.0], np.cumsum(VSLOT[y])])
        tot += (cv[SLOT[ii] + 1] - cv[SLOT[ii] + 1 - q]).sum()
    return tot / len(idx) / (q * s1)

NPL = 20
r1_ds = r1 / sd_slot; RQ_ds = cumR(r1_ds)
say("\n| 窓 | q | VR 観測 | E_RW 季節性(解析) | プラセボ符号反転 平均 (sd, 20回) | 補正 VR_c=obs/plc | 季節性で説明される超過の割合 | z_LM 元 | z_c=(obs−plc)/√θ | VR 季節性除去 (z_LM) |")
say("|---|---|---|---|---|---|---|---|---|---|")
A_res = {}
for wn, wm in WIN.items():
    for q in QS:
        obs = rep[wn][q]
        e_rw = expected_vr_rw(wm, q)
        plc = []
        for _ in range(NPL):
            s = rng.choice([-1.0, 1.0], size=n); rf = r1 * s; Rf = cumR(rf)
            plc.append(vr_point(wm, q, rf, Rf))
        plc = np.array(plc)
        th = theta_lm(wm, q, r1); z0 = (obs - 1) / math.sqrt(th); zc = (obs - plc.mean()) / math.sqrt(th)
        vds = vr_point(wm, q, r1_ds, RQ_ds); th_ds = theta_lm(wm, q, r1_ds); zds = (vds - 1) / math.sqrt(th_ds)
        frac = (plc.mean() - 1) / (obs - 1) if abs(obs - 1) > 1e-9 else np.nan
        A_res[(wn, q)] = dict(obs=obs, e_rw=e_rw, plc=plc.mean(), plc_sd=plc.std(), vrc=obs / plc.mean(), frac=frac, z0=z0, zc=zc, vds=vds, zds=zds)
        say(f"| {wn} | {q} | {obs:.3f} | {e_rw:.3f} | {plc.mean():.3f} ({plc.std():.3f}) | {obs/plc.mean():.3f} | {frac*100:+.0f}% | {z0:+.1f} | {zc:+.1f} | {vds:.3f} ({zds:+.1f}) |")

# ---------- B. yearly, corrected ----------
say("\n## B. 年別 VR(q): 元 z vs 季節性除去後 z（多重検定 51 セル）")
say("| 年 | VR12 (z) → 除去後 (z) | VR48 (z) → 除去後 (z) | VR144 (z) → 除去後 (z) | 年 r_1 分散 (×1e-8) |")
say("|---|---|---|---|---|")
cnt0 = cnt1 = 0; Y = {}
oos_144 = []
for y in range(2010, 2027):
    m = SYR == y
    if (m & V1).sum() < 1000: continue
    row = [str(y)]; Y[y] = {}
    for q in QS:
        o = vr_point(m, q, r1, RQ); th = theta_lm(m, q, r1); z0 = (o - 1) / math.sqrt(th)
        d = vr_point(m, q, r1_ds, RQ_ds); thd = theta_lm(m, q, r1_ds); zd = (d - 1) / math.sqrt(thd)
        Y[y][q] = (o, z0, d, zd); cnt0 += abs(z0) >= 2; cnt1 += abs(zd) >= 2
        row.append(f"{o:.3f} ({z0:+.1f}) → {d:.3f} ({zd:+.1f})")
    var_y = np.var(r1[m & V1]) * 1e8; Y[y]["var"] = var_y
    row.append(f"{var_y:.2f}")
    say("| " + " | ".join(row) + " |")
say(f"- |z|≥2 の件数（51 セル・帰無期待 ≈2.3）: 元 **{cnt0}** → 季節性除去後 **{cnt1}**")
for q in QS:
    s0 = sum(Y[y][q][0] > 1 for y in Y); s1_ = sum(Y[y][q][2] > 1 for y in Y)
    say(f"- VR{q} > 1 の年数 /{len(Y)}: 元 {s0} → 除去後 {s1_}")
oos_y = [y for y in Y if y >= 2021]
n_oos_sig0 = sum(Y[y][144][1] >= 2 for y in oos_y); n_oos_sig1 = sum(Y[y][144][3] >= 2 for y in oos_y)
say(f"- 外 6 年の VR144 z≥2: 元 {n_oos_sig0}/6 → 除去後 {n_oos_sig1}/6")
# pooled vs equal-weight; exclude 2026H1
mw = (SYR >= 2021) & (SYR <= 2025)
say(f"- 外 プール VR48 {rep['外2021-26H1'][48]:.3f}／年別 等加重平均 {np.mean([Y[y][48][0] for y in oos_y]):.3f}／2026H1 除外プール {vr_point(mw, 48, r1, RQ):.3f}・VR144 プール {rep['外2021-26H1'][144]:.3f}／等加重 {np.mean([Y[y][144][0] for y in oos_y]):.3f}／2026H1 除外 {vr_point(mw, 144, r1, RQ):.3f}")
say(f"- 年 r_1 分散の比 2026H1/外平均: {Y[2026]['var']/np.mean([Y[y]['var'] for y in oos_y]):.2f}（プールは分散加重）")
# equal-weight yearly Welch after deseasonalizing (H_E re-run on corrected VR48, same rule)
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, se, d / se
for q in QS:
    a = [Y[y][q][2] for y in Y if y >= 2021]; b = [Y[y][q][2] for y in Y if y <= 2020]
    d, se, t = welch(a, b)
    say(f"- H_E 季節性除去版 VR{q}: 在 {np.mean(b):.3f}／外 {np.mean(a):.3f}・差 {d:+.3f} (Welch t{t:+.2f}・MDE {2*se:.3f})")

# ---------- C. rho1 ----------
say("\n## C. ρ1 の境界と機構")
for wn, wm in {"2021-22": (SYR >= 2021) & (SYR <= 2022), "2023-26H1": SYR >= 2023, "2014-20": (SYR >= 2014) & (SYR <= 2020), "2010-13": (SYR >= 2010) & (SYR <= 2013)}.items():
    rho, t, nn = acf_t(wm, 1); rho_ds, t_ds, _ = acf_t(wm, 1, r=r1_ds)
    nz = r1 != 0; rho_nz, t_nz, n_nz = acf_t(wm, 1, extra=nz)
    say(f"- {wn}: ρ1 {rho:+.4f} (t{t:+.1f}, n{nn})・季節性除去 {rho_ds:+.4f} (t{t_ds:+.1f})・非零対のみ {rho_nz:+.4f} (t{t_nz:+.1f}, n{n_nz})")
say("- ET 時間帯別 ρ1（対の後側 i の時刻）:")
HB = {"18–01 Asia": ((h >= 18) | (h <= 1)), "02–07 London": (h >= 2) & (h <= 7), "08–16 NY": (h >= 8) & (h <= 16)}
say("| 窓 | " + " | ".join(HB) + " |"); say("|---|" + "---|" * len(HB))
for wn, wm in WIN.items():
    cells = []
    for hb, hm in HB.items():
        rho, t, nn = acf_t(wm & hm, 1); cells.append(f"{rho:+.4f} (t{t:+.1f})")
    say(f"| {wn} | " + " | ".join(cells) + " |")
# per-year rho1 vs 1/price (tick discreteness proxy) and non-zero pairs
say("| 年 | 平均価格 | ρ1 全対 (t) | ρ1 非零対 (t) | 零リターン率% | ρ1 季節性除去 (t) |"); say("|---|---|---|---|---|---|")
yr_rho = []; yr_p = []
for y in Y:
    m = SYR == y; rho, t, _ = acf_t(m, 1); rnz, tnz, _ = acf_t(m, 1, extra=(r1 != 0)); rds, tds, _ = acf_t(m, 1, r=r1_ds)
    pz = (r1[m & V1] == 0).mean() * 100; pbar = cl[m & V1].mean()
    yr_rho.append(rho); yr_p.append(pbar)
    say(f"| {y} | {pbar:.0f} | {rho:+.4f} ({t:+.1f}) | {rnz:+.4f} ({tnz:+.1f}) | {pz:.1f} | {rds:+.4f} ({tds:+.1f}) |")
from scipy.stats import spearmanr
say(f"- 年横断 Spearman(ρ1, 1/価格) {spearmanr(yr_rho, 1/np.array(yr_p)).correlation:+.2f}（n{len(yr_rho)}・離散性なら負のρ1が低価格年で強い＝正の相関）")
# US100 / US500 same statistic (non-zero pairs, same trade mask & session logic on the shared calendar grid)
say("- US100 / US500 の同統計（年別 ρ1・非零対のみ・同じ取引足/セッション定義）:")
say("| 年 | XAU 非零 | US500 非零 (t) | US100 非零 (t) |"); say("|---|---|---|---|")
IDX = {}
for sym in ["US500", "US100"]:
    ts2, cl2 = load_grid(sym)
    # align to XAU grid by ts
    pos = np.searchsorted(ts, ts2); ok = (pos < n) & (ts[np.minimum(pos, n - 1)] == ts2)
    r = np.zeros(n); lc2 = np.log(cl2); d2 = np.zeros(len(ts2)); d2[1:] = np.diff(lc2)
    present = np.zeros(n, bool); r[pos[ok]] = d2[ok]; present[pos[ok]] = True
    IDX[sym] = (r, present)
for y in Y:
    m = SYR == y
    rx, tx, _ = acf_t(m, 1, extra=(r1 != 0)); cells = [f"{rx:+.4f} ({tx:+.1f})"]
    for sym in ["US500", "US100"]:
        r, present = IDX[sym]
        if (m & V1 & present).sum() < 5000: cells.append("—"); continue
        rr, tt, nn = acf_t(m, 1, r=r, extra=(r != 0) & present); cells.append(f"{rr:+.4f} ({tt:+.1f})" if nn >= 1000 else "—")
    say(f"| {y} | " + " | ".join(cells) + " |")

# ---------- D. H_D with deseasonalized monthly VR48 ----------
say("\n## D. H_D 再実行（季節性除去後の月別 VR48・同じ 1 セル規則）")
MV = {}
for mo in np.unique(SMO[V1]):
    m = SMO == mo
    if (m & V1).sum() < 2000: continue
    MV[mo] = vr_point(m, 48, r1_ds, RQ_ds)
mv = pd.Series(MV).sort_index()
say(f"- 月数 {len(mv)}・除去後 VR48 中央値 {mv.median():.3f}・p10 {mv.quantile(.1):.3f}・p90 {mv.quantile(.9):.3f}・lag1 自己相関 {mv.autocorr(1):+.2f}")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8")); FT = J["frozen"]["FEED_TOL"]
X["Rs"] = X["R"] + (FT / X["risk"]) * X["exit"].isin(["SL", "TP"])
e_ny = pd.to_datetime(X["entry_time"], unit="s", utc=True).dt.tz_convert(NY) + pd.Timedelta(hours=6)
X["mo"] = (e_ny.dt.year * 100 + e_ny.dt.month).to_numpy()
G = X.groupby("mo").agg(Rbar=("Rs", "mean"), n=("Rs", "size")).reset_index()
def prev_month(mo):
    y, m = divmod(mo, 100); return (y - 1) * 100 + 12 if m == 1 else mo - 1
G["vr_prev"] = [MV.get(prev_month(mo), np.nan) for mo in G.mo]; G = G.dropna().reset_index(drop=True); G["yr"] = G.mo // 100
def wls(y, x, w):
    Z = np.column_stack([np.ones(len(y)), x]); Wm = np.diag(w)
    A = np.linalg.pinv(Z.T @ Wm @ Z); b = A @ Z.T @ Wm @ y; e = y - Z @ b
    meat = (Z * (w * e)[:, None]).T @ (Z * (w * e)[:, None]); V = A @ meat @ A * len(y) / (len(y) - 2)
    se = np.sqrt(np.diag(V)); return b[1], se[1], b[1] / se[1]
D_res = {}
for wn, wm in {"在2010-20": (G.yr <= 2020), "外2021-26H1": (G.yr >= 2021)}.items():
    g = G[wm]; x = g.vr_prev.to_numpy(); xz = (x - x.mean()) / x.std(ddof=1); y = g.Rbar.to_numpy(); w = g.n.to_numpy().astype(float)
    b, se, t = wls(y, xz, w)
    tt = np.array([wls(y, np.roll(xz, s), w)[2] for s in range(1, len(x))]); p = (np.abs(tt) >= abs(t)).mean()
    D_res[wn] = (b, se, t, p)
    say(f"- {wn}: 月 {len(g)}・β {b:+.4f}R/1sd (t{t:+.2f}, MDE {2*se:.4f}R)・循環シフト置換 p {p:.3f}")
okD = D_res["在2010-20"][2] >= 2 and D_res["外2021-26H1"][2] >= 1.5 and D_res["外2021-26H1"][3] < 0.05
say(f"- 判定 D: {'PASS（null は代理ノイズだった）' if okD else 'null 維持（C3 survive）'}")

# ---------- verdicts ----------
say("\n## 判定（事前固定の規則）")
a = A_res[("在2010-20", 144)]
vA = "broken" if (a["frac"] >= 0.5 or a["zc"] < 2) else "survived"
say(f"- A（在の多時間地平 正自己相関）: 在 VR144 超過 {a['obs']-1:+.3f} のうち季節性プラセボが {a['frac']*100:.0f}% を説明・補正 z_c {a['zc']:+.1f}・除去後 VR {a['vds']:.3f} (z{a['zds']:+.1f}) → **{vA}**")
a48 = A_res[("在2010-20", 48)]
say(f"-   同 VR48: 超過 {a48['obs']-1:+.3f}・季節性 {a48['frac']*100:.0f}%・z_c {a48['zc']:+.1f}・除去後 {a48['vds']:.3f} (z{a48['zds']:+.1f})")
if n_oos_sig1 >= 3: vB = "broken（補正後も外 年別 VR144 が有意）"
elif n_oos_sig1 <= 1: vB = "survived（ただし年別の元の有意 4/6 は季節性・在外とも補正後は RW）"
else: vB = "inconclusive"
say(f"- B（外はどの地平も随機歩行）: 外 年別 VR144 z≥2 元 {n_oos_sig0}/6 → 除去後 {n_oos_sig1}/6・51 セル |z|≥2 {cnt0}→{cnt1} → **{vB}**")
rho, t, _ = acf_t((SYR >= 2021) & (SYR <= 2022), 1)
vC = "broken（境界は 2023、2021-22 は依然負で有意）" if t <= -2 else "survived"
say(f"- C（ρ1 負は 2021+ で消えた）: 2021-22 プール ρ1 {rho:+.4f} (t{t:+.1f}) → **{vC}**")
say(f"- D（H_D null は代理ノイズか）: {'PASS → C3 broken' if okD else 'null 維持 → C3 survived'}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
