# -*- coding: utf-8 -*-
"""
[REFUTE c18] 2026-11-07 — 対象: cycle18 (03:50)「壁→壁の本は ET 17:00 ブレイクを跨ぐとき再開 pop を受け取るか払うか」の読み
  C2 外 J2 null（c −0.009R t−0.65・MDE 0.029R）→「市場構造の異常は本番の R にほぼ寄与しない」
  C3 在 2013-20 は払う側: c −0.022R (t−2.47)・純受取り −0.024R/横断本 (t−2.67)・窓 R* の 18%・DiD(ブレイク−プラセボ) c 差 −0.054R (t−2.27)
     ＝「在では pop が壁→壁の損失の 2 割を作った」
  C5 D_e(BUY−SELL 残り path) 外 +0.369R (t4.04) は pop でなく夜間〜翌日のドリフト（記述）
  C6 選択 c の符号は年で反転（2021/2024 t−3.5 負・2025/26 正）＝相場の方向でどちらが生き残るかが変わる・レジーム依存
  C7 16:55 足（最終印字）決着 23 本は BUY=SL 側・SELL=TP 側 ＝ 最終印字の沈みで紙の SL/TP が約定している疑い

=== 事前固定（数字を見る前に書く）===
データ: cycle18 と同一（c8 特徴量 csv・c1 json・refute_c2_fullpaths.npz・XAU_m5_close.npz）。母集合・アンカー・pop_R・|pop|_R・c・m3 の定義は
cycle18 のコードを再利用し、在 c −0.0223／外 c −0.0093／在 m3 −0.0242 を 1e-3 で再現できることを先に assert。コスト倍は適用不能（path 分解で戦略でない）と記録。
攻撃（破壊条件）:
 K1 置換帰無（C3 の統計的根拠）: クリーン日を日付順に並べ、日次 pop（G_5・プラセボは P_5 を同じ k）を k 日循環シフト（k=1..n_d−1 全部）。
    本の側・P・risk・生存はそのまま、pop だけ別の日のものに差し替える＝「生存側は当日の pop と無関係」の帰無。
    統計量 = c の点推定（BUY 生存 |pop|_R 平均 − SELL 生存）/2、m3 = mean(pop_R)、DiD c 差。両側 p。
    → 在 c の p ≥ 0.05 なら C3 の統計的根拠は破壊。
 K2 多重検定（C3）: cycle18 が記述した J2 c・J3 m3 の 3 窓 × {ブレイク, G_0 版, プラセボ} = 18 セル ＋ DiD 3 = 21 セル。Bonferroni 5% の |t| 閾値 ≈ 2.86。
    在 c |t| 2.47・在 m3 2.67・DiD 2.27 は閾値未満（cycle18 の記載値から決定的・再現で確認）。判定は外 2 セルだけ事前固定だったので在は事後セル。
 K3 機構（C3 の読み「払う」）: 日次 bp 回帰 G_5 ~ 1 + SGN + r_pre30(16:25→16:55) + r_day(前日18:05→16:55)（日クラスタ）。
    → SGN 係数（= c_bp）が統制後に生の 50% 未満に縮むなら「払う」は「SELL 生存日は引け前 30 分が下げており、pop はその部分的な戻し」。
 K4 会計窓（C3 の「18%」）: 横断本の符号つき受取りを窓別に: 引け前 30 分 [16:25→16:55]（アンカー直前・生存は既に確定）、pop [16:55→18:05]、
    合算 [16:25→18:05]、延長 [16:55→18:30]・[16:55→19:00]。→ 在 合算 [16:25→18:05] の日クラスタ t > −2 なら「pop が損失の 18% を作った」は
    会計の始点に依存する言い方＝破壊。
 K5 外 null の頑健性（C2）: 外の 3 年以上の部分窓（2021-23／2021-24／2022-25／LOYO 各年）で c ≤ −0.02R かつ t ≤ −2 のものが 1 つでもあれば
    「外 null＝選択なし」は inconclusive（2025-26H1 の正で相殺しているだけ）。
 K6 年別符号反転（C6）: 年別 c の |t| の最大値（14 年）を K1 と同じ循環シフト帰無で family-wise p。
    → p_fw ≥ 0.05 ∧ 正の年の max t < 2 なら「符号反転＝レジーム依存」は雑音＝破壊。p_fw < 0.05 なら「一部の年に実在する負の選択」で inconclusive。
 K7 最終印字決着（C7）: 候補本（アンカー kk≥1）について足 kk+j（j=−6..+6）での決着ハザード（直前まで生存した本のうちその足で決着した比率）。
    j=+1 が 16:55 足・j=+2 が 18:00 再開足。→ 16:55 足のハザードが隣接 j∈{−6..−1, +3..+6} の平均の 1.5 倍未満なら
    「最終印字で紙の SL/TP が約定する疑い」に超過はなく破壊（側×exit の偏りは足の方向そのもの＝記述）。
 K8 C5 記述: BUY 生存日と SELL 生存日の固定地平の市場リターン（16:55→翌 09:30 ET・bp）の差。|t|<2 なら D_e は側非依存のドリフト（cycle18 の読みを支持）。
    年別 D_e と年別 G の Spearman。判定には使わない。
判定: C3 = K1 で broken／K1 不発なら (K3 ∧ K4) で broken・片方なら inconclusive・どちらも不発なら survived。C6 = K6。C7 = K7。C2 = K5（inconclusive か survived）。
seed 20261107。読取のみ・MT5 無し・外部通信無し・scan 無し。
"""
import os, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c18_crossing.md")
NY = "America/New_York"
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c18] ブレイク横断本「払う／受け取る」を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c18_crossing.py)")

# ---------- trades (cycle18 と同一) ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy()
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c1_et = np.sort(np.array([t["entry_time"] for t in J["trades"]])); assert np.array_equal(c1_et, ET)
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64)
assert len(off) - 1 == N and np.all(np.diff(off) == HOLD + 1)
e_utc = pd.to_datetime(ET, unit="s", utc=True); e_ny = e_utc.tz_convert(NY)
E_H = e_ny.hour.to_numpy(); E_M = e_ny.minute.to_numpy(); E_WD = e_ny.weekday.to_numpy()
say(f"- 本 {N}、entry {e_utc[0].date()}〜{e_utc[-1].date()} UTC、FEED_TOL {FT}")

# ---------- XAU grid ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float); lc = np.log(cl)
r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = r == 0
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert(NY)
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
day = yr * 10000 + t_ny.month.to_numpy() * 100 + t_ny.day.to_numpy()
gap_after = np.where(np.diff(ts) != 300)[0]; valid = np.ones(len(ts), bool); valid[gap_after + 1] = False
say(f"- XAU npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC、flat {flat.mean()*100:.1f}%、格子の穴 {len(gap_after)}")
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)
iG = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]; tG = ts[iG]
i1650 = idx_at(tG - 70 * 60); i1655 = idx_at(tG - 65 * 60); i1620 = idx_at(tG - 100 * 60)
BRK = np.column_stack([idx_at(tG - 300 * j) for j in range(1, 13)])
i1150 = idx_at(tG - (6 * 3600 + 10 * 60)); i1300 = idx_at(tG - 5 * 3600); i1120 = idx_at(tG - (6 * 3600 + 40 * 60))
ok = (i1650 >= 0) & (i1655 >= 0) & (i1620 >= 0) & np.all(BRK >= 0, axis=1) & (i1150 >= 0) & (i1300 >= 0) & (i1120 >= 0) & valid[iG] & valid[i1650]
iG, i1650, i1655, i1620, BRK, i1150, i1300, i1120 = iG[ok], i1650[ok], i1655[ok], i1620[ok], BRK[ok], i1150[ok], i1300[ok], i1120[ok]
clean = np.all(flat[BRK], axis=1)
iG, i1650, i1655, i1620, i1150, i1300, i1120 = iG[clean], i1650[clean], i1655[clean], i1620[clean], i1150[clean], i1300[clean], i1120[clean]
tG = ts[iG]; dG = day[iG]
# extra clock prices (price at clock c = close of bar labelled c−5)
def price_at(off_min):
    j = idx_at(tG + (off_min - 5) * 60); out = np.full(len(iG), np.nan); okj = j >= 0; out[okj] = lc[j[okj]]; return out
p1555 = price_at(-125); p1830 = price_at(30); p1900 = price_at(60)
iPrev = idx_at(tG - 86400); prev_ok = (iPrev >= 0) & (h[np.clip(iPrev, 0, len(h) - 1)] == 18)
p_prev = np.where(prev_ok, lc[np.clip(iPrev, 0, len(lc) - 1)], np.nan)
jN = idx_at(tG + 86400 - 515 * 60); nok = (jN >= 0) & (h[np.clip(jN, 0, len(h) - 1)] == 9) & (mi[np.clip(jN, 0, len(mi) - 1)] == 25)
pN0930 = np.where(nok, lc[np.clip(jN, 0, len(lc) - 1)], np.nan)
DAY = pd.DataFrame({"d": dG, "ts1650": tG - 70 * 60, "ts1150": tG - (6 * 3600 + 10 * 60),
                    "G5": lc[iG] - lc[i1650], "G0": lc[iG] - lc[i1655], "P5": lc[i1300] - lc[i1150],
                    "P1650": cl[i1650], "P1150": cl[i1150],
                    "pre30": lc[i1650] - lc[i1620], "pre60": lc[i1650] - p1555, "rday": lc[i1650] - p_prev,
                    "G30": p1830 - lc[i1650], "G60": p1900 - lc[i1650], "nite": pN0930 - lc[i1650]}).set_index("d").sort_index()
say(f"- クリーン日 {len(DAY)}（cycle18: 2400）"); assert len(DAY) == 2400

# ---------- anchor per trade (cycle18 と同一) ----------
e_date = e_ny.normalize()
before = (E_H < 16) | ((E_H == 16) & (E_M < 50)); after = E_H >= 18
anc_date = e_date.where(before, e_date + pd.Timedelta(days=1))
anc_day = (anc_date.year * 10000 + anc_date.month * 100 + anc_date.day).to_numpy()
use = (before | after); use &= np.where(before, E_WD <= 3, (E_WD <= 2) | (E_WD == 6)); use &= np.isin(anc_day, DAY.index.to_numpy())
dd = DAY.reindex(anc_day)
def anchor(TSa):
    kk = np.full(N, -1); m = use & np.isfinite(TSa); dt = np.where(m, TSa - ET, np.nan)
    good = m & (dt > 0) & (np.mod(dt, 300) == 0); kk[good] = (dt[good] // 300).astype(int)
    return kk, good & (kk >= 1), good & (HOLD > kk) & (kk >= 1)
KB, GB, CB = anchor(dd["ts1650"].to_numpy()); KP, GP, CP = anchor(dd["ts1150"].to_numpy())
say(f"- 横断本 {CB.sum()}（cycle18: 1697）、プラセボ生存本 {CP.sum()}（1030）、アンカー候補（kk≥1）{GB.sum()}")
assert CB.sum() == 1697 and CP.sum() == 1030

# ---------- stats helpers ----------
def ols_cluster(y, Z, cl_):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    k = Z.shape[1]; meat = np.zeros((k, k)); u, inv = np.unique(cl_, return_inverse=True)
    S = np.zeros((len(u), k))
    for col in range(k): S[:, col] = np.bincount(inv, weights=Z[:, col] * e, minlength=len(u))
    meat = S.T @ S; G = len(u); V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G
def cmean(y, cl_):
    b, se, G = ols_cluster(y, np.ones((len(y), 1)), cl_); return b[0], se[0], b[0] / se[0] if se[0] > 0 else np.nan
def creg(y, x, cl_):
    Z = np.column_stack([np.ones(len(y)), x]); b, se, G = ols_cluster(y, Z, cl_); return b[1], se[1], b[1] / se[1] if se[1] > 0 else np.nan
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se if se > 0 else np.nan
W = {"在2013-20": (YEAR >= 2013) & (YEAR <= 2020), "外2021-26H1": YEAR >= 2021, "近年2024-26H1": YEAR >= 2024}

# ---------- Q0 reproduce ----------
say("\n## Q0 再現（cycle18 の c・m3）")
days_sorted = DAY.index.to_numpy(); pos_of = {d: i for i, d in enumerate(days_sorted)}
POS = np.array([pos_of.get(d, -1) for d in anc_day])
G5d = DAY["G5"].to_numpy(); P5d = DAY["P5"].to_numpy()
REP = {}
for wn, wm in W.items():
    i = np.flatnonzero(CB & wm); sg = SGN[i]; P = dd["P1650"].to_numpy()[i]; rk = RISK[i]; G = G5d[POS[i]]; dday = anc_day[i]
    clk = clR[off[i] + KB[i]]; e = RSTAR[i] - clk
    c2, se2, t2 = creg(G * P / rk, sg, dday); m3, se3, t3 = cmean(sg * G * P / rk, dday); b1, _, t1 = creg(e, sg * G * P / rk, dday)
    bs, ses, _ = creg(e, sg, dday); D = 2 * bs; seD = 2 * ses
    REP[wn] = dict(c=c2, tc=t2, se2=se2, m3=m3, tm=t3, D=D, tD=D / seD, n=len(i))
    say(f"- {wn}: n{len(i)} J1 b {b1:+.3f} (t{t1:+.2f})・J2 c {c2:+.4f}R (t{t2:+.2f})・J3 m3 {m3:+.4f}R (t{t3:+.2f})・D_e {D:+.4f}R (t{D/seD:+.2f})")
assert abs(REP["在2013-20"]["c"] - (-0.0223)) < 1e-3 and abs(REP["外2021-26H1"]["c"] - (-0.0093)) < 1e-3 and abs(REP["在2013-20"]["m3"] - (-0.0242)) < 1e-3
say("- 再現 OK（在 c −0.0223／外 c −0.0093／在 m3 −0.0242 と 1e-3 で一致）")

# ---------- K1 permutation (circular day shift of pops) ----------
say("\n## K1 置換帰無: 日次 pop をクリーン日順に k 日循環シフト（本の側・P・risk・生存は固定）")
def stat_c(G_bp, sg, pr):
    a = G_bp * pr; return (a[sg > 0].mean() - a[sg < 0].mean()) / 2
def stat_m(G_bp, sg, pr): return (sg * G_bp * pr).mean()
PERM = {}
for wn, wm in W.items():
    i = np.flatnonzero(CB & wm); sg = SGN[i]; pr = dd["P1650"].to_numpy()[i] / RISK[i]; p0 = POS[i]
    ip = np.flatnonzero(CP & wm); sgp = SGN[ip]; prp = dd["P1150"].to_numpy()[ip] / RISK[ip]; pp = POS[ip]
    # window's day range for shifting: use days within the window's years so shifted pops stay in-regime
    yrs = (YEAR[CB & wm]); dmask = (days_sorted // 10000 >= YEAR[i].min()) & (days_sorted // 10000 <= YEAR[i].max())
    didx = np.flatnonzero(dmask); nd = len(didx); loc = np.searchsorted(didx, p0); locp = np.searchsorted(didx, pp)
    assert np.all(didx[loc] == p0) and np.all(didx[locp] == pp)
    c_obs = stat_c(G5d[p0], sg, pr); m_obs = stat_m(G5d[p0], sg, pr); cp_obs = stat_c(P5d[pp], sgp, prp); did_obs = c_obs - cp_obs
    cs = np.empty(nd - 1); ms_ = np.empty(nd - 1); dids = np.empty(nd - 1)
    for j, k in enumerate(range(1, nd)):
        Gs = G5d[didx[(loc + k) % nd]]; Ps = P5d[didx[(locp + k) % nd]]
        cs[j] = stat_c(Gs, sg, pr); ms_[j] = stat_m(Gs, sg, pr); dids[j] = cs[j] - stat_c(Ps, sgp, prp)
    p_c = (np.abs(cs) >= abs(c_obs)).mean(); p_m = (np.abs(ms_) >= abs(m_obs)).mean(); p_d = (np.abs(dids) >= abs(did_obs)).mean()
    PERM[wn] = dict(p_c=p_c, p_m=p_m, p_d=p_d, c_obs=c_obs, sd_c=cs.std())
    say(f"- {wn}: c 観測 {c_obs:+.4f}R → シフト {nd-1} 通り 両側 p **{p_c:.3f}**（帰無 sd {cs.std():.4f}・帰無平均 {cs.mean():+.4f}）；"
        f"m3 観測 {m_obs:+.4f}R → p **{p_m:.3f}**；DiD c 差 観測 {did_obs:+.4f}R → p **{p_d:.3f}**")
K1_break = PERM["在2013-20"]["p_c"] >= 0.05

# ---------- K2 multiple testing (from reproduced t's) ----------
say("\n## K2 多重検定: cycle18 が記述した J2 c・J3 m3（3 窓 × ブレイク/G_0/プラセボ = 18）＋ DiD 3 = 21 セル")
from statistics import NormalDist
thr = NormalDist().inv_cdf(1 - 0.05 / 21 / 2)
say(f"- Bonferroni 5%/21 の両側 |t| 閾値 {thr:.2f}。在 c |t| {abs(REP['在2013-20']['tc']):.2f}・在 m3 |t| {abs(REP['在2013-20']['tm']):.2f}・DiD c 差 |t| 2.27（cycle18 記載）→ "
    + ("全部閾値未満＝事後セルとしては不通過" if max(abs(REP['在2013-20']['tc']), abs(REP['在2013-20']['tm']), 2.27) < thr else "通過あり"))
K2_fail = max(abs(REP['在2013-20']['tc']), abs(REP['在2013-20']['tm'])) < thr

# ---------- K3 mechanism: control pre-close and same-day return ----------
say("\n## K3 機構: 日次 bp 回帰 G_5 ~ 1 + SGN + r_pre30 + r_day（横断本・日クラスタ）")
K3_break = False
for wn, wm in W.items():
    i = np.flatnonzero(CB & wm); sg = SGN[i]; dday = anc_day[i]; G = G5d[POS[i]] * 1e4
    pre = dd["pre30"].to_numpy()[i] * 1e4; rdy = dd["rday"].to_numpy()[i] * 1e4; pre60 = dd["pre60"].to_numpy()[i] * 1e4
    okm = np.isfinite(pre) & np.isfinite(rdy) & np.isfinite(pre60)
    b_raw, se_raw, G_ = ols_cluster(G[okm], np.column_stack([np.ones(okm.sum()), sg[okm]]), dday[okm])
    b_ctl, se_ctl, _ = ols_cluster(G[okm], np.column_stack([np.ones(okm.sum()), sg[okm], pre[okm], rdy[okm]]), dday[okm])
    b_ctl2, se_ctl2, _ = ols_cluster(G[okm], np.column_stack([np.ones(okm.sum()), sg[okm], pre[okm], pre60[okm] - pre[okm], rdy[okm]]), dday[okm])
    # regressor means by survivor side
    say(f"- {wn} n{okm.sum()}: 生 SGN 係数 {b_raw[1]:+.3f} bp (t{b_raw[1]/se_raw[1]:+.2f}) → 統制後 **{b_ctl[1]:+.3f} bp (t{b_ctl[1]/se_ctl[1]:+.2f})**（残存 {b_ctl[1]/b_raw[1]*100 if b_raw[1] else np.nan:.0f}%）；"
        f"β_pre30 {b_ctl[1+1]:+.3f} (t{b_ctl[2]/se_ctl[2]:+.1f})・β_rday {b_ctl[3]:+.4f} (t{b_ctl[3]/se_ctl[3]:+.1f})；pre60 追加版 SGN {b_ctl2[1]:+.3f} (t{b_ctl2[1]/se_ctl2[1]:+.2f})")
    say(f"    生存側別の日次平均: r_pre30 BUY {pre[okm&(sg>0)].mean():+.2f} / SELL {pre[okm&(sg<0)].mean():+.2f} bp・r_day BUY {rdy[okm&(sg>0)].mean():+.1f} / SELL {rdy[okm&(sg<0)].mean():+.1f} bp・G_5 BUY {G[okm&(sg>0)].mean():+.2f} / SELL {G[okm&(sg<0)].mean():+.2f} bp")
    if wn == "在2013-20": K3_break = abs(b_ctl[1]) < 0.5 * abs(b_raw[1])

# ---------- K4 accounting window ----------
say("\n## K4 会計窓: 横断本の符号つき受取り（R/本・日クラスタ t）を窓別に")
K4_break = False
for wn, wm in W.items():
    i = np.flatnonzero(CB & wm); sg = SGN[i]; pr = dd["P1650"].to_numpy()[i] / RISK[i]; dday = anc_day[i]; tot_R_win = RSTAR[wm].sum()
    rows = []
    for lab, col in (("引け前 60 分 [15:55→16:55]", "pre60"), ("引け前 30 分 [16:25→16:55]", "pre30"), ("pop [16:55→18:05]", "G5"),
                     ("→18:30 [16:55→18:30]", "G30"), ("→19:00 [16:55→19:00]", "G60"), ("夜 [16:55→翌09:30]", "nite")):
        v = dd[col].to_numpy()[i]; okv = np.isfinite(v); m, se, t = cmean(sg[okv] * v[okv] * pr[okv], dday[okv])
        rows.append((lab, m, t, (sg[okv] * v[okv] * pr[okv]).sum() / tot_R_win * 100, okv.sum()))
    comb = dd["pre30"].to_numpy()[i] + dd["G5"].to_numpy()[i]; okc = np.isfinite(comb)
    mc, sec, tc = cmean(sg[okc] * comb[okc] * pr[okc], dday[okc])
    say(f"- {wn} n{len(i)}（窓 R* 合計 {tot_R_win:+.1f}R）:")
    for lab, m, t, share, nn in rows: say(f"    {lab}: {m:+.4f}R/本 (t{t:+.2f})・窓 R* 比 {share:+.1f}%")
    say(f"    **合算 [16:25→18:05]: {mc:+.4f}R/本 (t{tc:+.2f})・窓 R* 比 {(sg[okc]*comb[okc]*pr[okc]).sum()/tot_R_win*100:+.1f}%**")
    comb2 = dd["pre30"].to_numpy()[i] + dd["G60"].to_numpy()[i]; ok2 = np.isfinite(comb2); m2_, _, t2_ = cmean(sg[ok2] * comb2[ok2] * pr[ok2], dday[ok2])
    comb3 = dd["pre60"].to_numpy()[i] + dd["G60"].to_numpy()[i]; ok3 = np.isfinite(comb3); m3_, _, t3_ = cmean(sg[ok3] * comb3[ok3] * pr[ok3], dday[ok3])
    say(f"    合算 [16:25→19:00]: {m2_:+.4f}R/本 (t{t2_:+.2f})・合算 [15:55→19:00]: {m3_:+.4f}R/本 (t{t3_:+.2f})")
    if wn == "在2013-20": K4_break = tc > -2

# ---------- K5 out-null robustness ----------
say("\n## K5 外 null の頑健性: 3 年以上の部分窓と LOYO の c")
K5_hits = []
subs = {"2021-23": (2021, 2023), "2021-24": (2021, 2024), "2022-25": (2022, 2025), "2022-26H1": (2022, 2026), "2023-26H1": (2023, 2026)}
for lab, (a, b) in subs.items():
    i = np.flatnonzero(CB & (YEAR >= a) & (YEAR <= b)); sg = SGN[i]; pr = dd["P1650"].to_numpy()[i] / RISK[i]; dday = anc_day[i]; G = G5d[POS[i]]
    c2, se2, t2 = creg(G * pr, sg, dday); m3, _, t3 = cmean(sg * G * pr, dday)
    say(f"- 外部分窓 {lab}: n{len(i)} c {c2:+.4f}R (t{t2:+.2f}, MDE {2*se2:.4f}) m3 {m3:+.4f}R (t{t3:+.2f})" + ("  ← c≤−0.02 ∧ t≤−2" if (c2 <= -0.02 and t2 <= -2) else ""))
    K5_hits.append(c2 <= -0.02 and t2 <= -2)
for y_ in range(2021, 2027):
    i = np.flatnonzero(CB & (YEAR >= 2021) & (YEAR != y_)); sg = SGN[i]; pr = dd["P1650"].to_numpy()[i] / RISK[i]; dday = anc_day[i]; G = G5d[POS[i]]
    c2, se2, t2 = creg(G * pr, sg, dday)
    say(f"- 外 LOYO −{y_}: n{len(i)} c {c2:+.4f}R (t{t2:+.2f})" + ("  ← c≤−0.02 ∧ t≤−2" if (c2 <= -0.02 and t2 <= -2) else ""))
    K5_hits.append(c2 <= -0.02 and t2 <= -2)
K5_inconc = any(K5_hits)

# ---------- K6 yearly sign flip family-wise ----------
say("\n## K6 年別 c の family-wise（14 年の max|t|・循環シフト帰無）")
yrs = np.arange(2013, 2027)
def yearly_t(Gbp_by_trade):
    out = []
    for y_ in yrs:
        i = np.flatnonzero(CB & (YEAR == y_))
        if len(i) < 10: out.append(np.nan); continue
        a = Gbp_by_trade[i] * dd["P1650"].to_numpy()[i] / RISK[i]; sg = SGN[i]
        d, t = welch(a[sg > 0], a[sg < 0]); out.append(t)
    return np.array(out)
Gtr = G5d[np.clip(POS, 0, None)]; Gtr = np.where(POS >= 0, Gtr, np.nan)
t_obs = yearly_t(Gtr)
say("- 観測 年別 t（Welch・c の符号）: " + " ".join(f"{y_}:{t:+.1f}" for y_, t in zip(yrs, t_obs) if np.isfinite(t)))
obs_max = np.nanmax(np.abs(t_obs)); obs_pos_max = np.nanmax(np.where(t_obs > 0, t_obs, -np.inf))
# shift within full 2013-26 clean-day list (all trades at once)
iall = np.flatnonzero(CB); nd = len(days_sorted); maxs = []; posmax = []
for k in range(1, nd):
    Gs = np.full(N, np.nan); Gs[iall] = G5d[(POS[iall] + k) % nd]
    tt = yearly_t(Gs); maxs.append(np.nanmax(np.abs(tt))); posmax.append(np.nanmax(np.where(tt > 0, tt, -np.inf)))
maxs = np.array(maxs); p_fw = (maxs >= obs_max).mean()
say(f"- 観測 max|t| {obs_max:.2f} → 帰無 中央値 {np.median(maxs):.2f}・95% 点 {np.quantile(maxs, 0.95):.2f}・**p_fw {p_fw:.3f}**；正の年の max t 観測 {obs_pos_max:.2f}（帰無 95% 点 {np.quantile(posmax, 0.95):.2f}）")
say(f"- 符号の並び: 負の年 {(t_obs < 0).sum()}/{np.isfinite(t_obs).sum()}・|t|≥2 の年 {(np.abs(t_obs) >= 2).sum()}（帰無での |t|≥2 年数の平均 {np.mean([(np.abs(yearly_t(np.where(POS>=0, G5d[(POS+k)%nd], np.nan)))>=2).sum() for k in range(1, nd, 25)]):.2f}）")
K6_break = (p_fw >= 0.05) and (obs_pos_max < 2)

# ---------- K7 last-print hazard ----------
say("\n## K7 最終印字決着: アンカー候補本の足 kk+j での決着ハザード（j=+1 が 16:55 足・+2 が 18:00 再開足）")
iC = np.flatnonzero(GB); kk = KB[iC]; hd = HOLD[iC]; sgC = SGN[iC]; exC = EXIT[iC]
# 事後修正（判定規則は不変・隣接集合の定義ミスの訂正）: 初回実行で j=+2..+13 は ET 17:00–17:55 のブレイク足＝path 上で flat（決着 0）と判明。
# cycle18 の「k_b+2＝18:00 再開足」というラベルは誤りで、再開足は k_b+14。隣接は取引のある足 j∈{−6..−1} と 再開後 j∈{+15..+20}（再開ギャップ足 +14 は別掲）に改める。
haz = {}; nxt = {}
for j in list(range(-6, 3)) + list(range(13, 21)):
    alive_before = hd > kk + j - 1; exit_at = hd == kk + j
    haz[j] = exit_at.sum() / max(alive_before.sum(), 1); nxt[j] = (exit_at.sum(), alive_before.sum())
say("- ハザード: " + " ".join(f"j{j:+d}:{haz[j]*100:.2f}%({nxt[j][0]}/{nxt[j][1]})" for j in haz))
# verify break bars are flat on the path
mflat = hd > kk + 13; i_f = iC[mflat]; k_f = kk[mflat]
flat_ok = np.mean([np.all(clR[off[a] + b + 2: off[a] + b + 14] == clR[off[a] + b + 1]) for a, b in zip(i_f, k_f)])
say(f"- path 上のブレイク足 k_b+2..k_b+13 が全部 flat の比率 {flat_ok*100:.1f}%（n{mflat.sum()}）＝再開足は k_b+14")
neigh_pre = np.mean([haz[j] for j in range(-6, 0)]); neigh_post = np.mean([haz[j] for j in range(15, 21)]); neigh = np.mean([haz[j] for j in list(range(-6, 0)) + list(range(15, 21))])
say(f"- 16:55 足 j=+1 ハザード **{haz[1]*100:.2f}%** vs 隣接 取引足 平均 {neigh*100:.2f}%（前 {neigh_pre*100:.2f}%・再開後 {neigh_post*100:.2f}%・比 **{haz[1]/neigh if neigh else np.nan:.2f}**）；再開ギャップ足 j=+14 {haz[14]*100:.2f}%")
m1 = hd == kk + 1
bar1655 = (DAY["G5"] - DAY["G0"]).to_numpy() * 1e4  # = lc[16:55 足 close] − lc[16:50 足 close] = 最終印字足のリターン（bp）
# bar volatility of neighbours (clock bars 16:25..16:50 ET and 18:05..18:30 ET) for hazard scaling
nb_abs = [np.nanmean(np.abs((price_at(om + 5) - price_at(om)) * 1e4)) for om in (-100, -95, -90, -85, -80, -75)]  # bars closing 16:25..16:50 ET
post_abs = [np.nanmean(np.abs((price_at(om + 5) - price_at(om)) * 1e4)) for om in (5, 10, 15, 20, 25, 30)]  # bars closing 18:10..18:35 ET
say(f"- 足の |ret| 平均（全クリーン日）: 16:55 足 {np.nanmean(np.abs(bar1655)):.2f} bp vs 直前 6 本（16:25–16:55 閉）{np.mean(nb_abs):.2f} bp・再開後 6 本（18:10–18:40 閉）{np.mean(post_abs):.2f} bp（比 16:55/隣接 {np.nanmean(np.abs(bar1655))/np.mean(nb_abs+post_abs):.2f}）")
# does the 16:55 move revert by the reopen on settlement days? G0 = 16:55 close → 18:05
g0_set = DAY["G0"].to_numpy()[POS[iC][m1]] * 1e4; b_set = bar1655[POS[iC][m1]]
say(f"- 決着日（n{m1.sum()}）の 16:55 足 {b_set.mean():+.2f} bp → 続く 17:00→18:05（G_0）{g0_set.mean():+.2f} bp（戻し比 {-g0_set.mean()/b_set.mean()*100 if b_set.mean() else np.nan:.0f}%・符号つき回帰 β {np.polyfit(b_set, g0_set, 1)[0]:+.2f}）；全クリーン日 β(G_0 on 16:55 足) {np.polyfit(bar1655, DAY['G0'].to_numpy()*1e4, 1)[0]:+.2f}")
for wn, wm in W.items():
    mm = m1 & wm[iC]; yrs_w = DAY.index.to_numpy() // 10000
    wmask = {"在2013-20": (yrs_w >= 2013) & (yrs_w <= 2020), "外2021-26H1": yrs_w >= 2021, "近年2024-26H1": yrs_w >= 2024}[wn]
    pdown = (bar1655[wmask] < 0).mean()
    down_consistent = (((sgC == 1) & (exC == "SL")) | ((sgC == -1) & (exC == "TP"))) & mm
    if mm.sum():
        say(f"- {wn} 16:55 足決着 {mm.sum()} 本: " + "・".join(f"{s}×{x} {((sgC==(1 if s=='BUY' else -1))&(exC==x)&mm).sum()}" for s in ("BUY", "SELL") for x in ("SL", "TP", "TIME"))
            + f"；下向き整合（BUY-SL／SELL-TP）{down_consistent.sum()}/{mm.sum()} vs クリーン日の 16:55 足が負の比率 {pdown*100:.0f}%（期待 {pdown*mm.sum():.1f}）")
# how close to SL/TP were they at the anchor? cl_k at anchor for those trades vs others (anchor bar must be inside the path: hd >= kk)
mA = hd >= kk; clk_all = np.full(len(iC), np.nan); clk_all[mA] = clR[off[iC][mA] + kk[mA]]
oth = hd > kk + 1
say(f"- アンカー時点 cl_k: 16:55 足決着本 中央値 {np.nanmedian(clk_all[m1]):+.3f}R（|cl_k| 中央値 {np.nanmedian(np.abs(clk_all[m1])):.3f}）vs 他の横断本 {np.nanmedian(clk_all[oth]):+.3f}R（|cl_k| {np.nanmedian(np.abs(clk_all[oth])):.3f}）；"
    f"16:55 足の bp 平均（決着日）{bar1655[POS[iC][m1]].mean():+.2f} bp・|bp| {np.abs(bar1655[POS[iC][m1]]).mean():.2f}（全クリーン日 {bar1655.mean():+.2f}・|bp| {np.abs(bar1655).mean():.2f}）")
K7_break = haz[1] < 1.5 * neigh
# K7b 再開ギャップ足（k_b+14）での決着＝cycle18 が「k_b+2 で 0 本＝ギャップ抜け無し」と書いた箇所の実体。レベル記帳の楽観/悲観量を見積もる。
Bq = X["b"].to_numpy()
m14 = hd == kk + 14; i14 = iC[m14]; k14 = kk[m14]
cl_pre = clR[off[i14] + k14 + 13]  # = cl at k_b+1 (break bars flat)
jumpR = SGN[i14] * dd["G0"].to_numpy()[i14] * dd["P1650"].to_numpy()[i14] / RISK[i14]  # favorable-direction jump 16:55 close → 18:05 close
isSL = EXIT[i14] == "SL"; isTP = EXIT[i14] == "TP"
over_SL = (-jumpR - (cl_pre + 1.0))[isSL]; over_TP = (jumpR - (Bq[i14] - cl_pre))[isTP]
say(f"- **再開足 k_b+14 決着 {m14.sum()} 本**（SL {isSL.sum()}・TP {isTP.sum()}・TIME {(~isSL&~isTP).sum()}；BUY {(SGN[i14]>0).sum()}）: 16:55 close→18:05 close の跳び（有利方向 R）平均 {jumpR.mean():+.3f}R・|跳び| {np.abs(jumpR).mean():.3f}R；"
    f"直前 cl 中央値 {np.median(cl_pre):+.3f}R")
say(f"    SL 決着 {isSL.sum()} 本: 跳びが SL 距離を超えた分（レベル記帳が楽観）平均 {over_SL.mean():+.3f}R・>0 の本 {(over_SL>0).sum()}・合計 {np.clip(over_SL,0,None).sum():+.1f}R；"
    f"TP 決着 {isTP.sum()} 本: 超過（レベル記帳が悲観）平均 {over_TP.mean():+.3f}R・>0 {(over_TP>0).sum()}・合計 {np.clip(over_TP,0,None).sum():+.1f}R（close-to-close 近似・足の始値は npz に無い）")
for wn, wm in W.items():
    mm = wm[i14]
    if mm.sum(): say(f"    {wn}: {mm.sum()} 本（SL {isSL[mm].sum()}・TP {isTP[mm].sum()}）・SL 楽観合計 {np.clip(over_SL[wm[i14][isSL]],0,None).sum():+.1f}R・TP 悲観合計 {np.clip(over_TP[wm[i14][isTP]],0,None).sum():+.1f}R")

# ---------- K8 D_e descriptive ----------
say("\n## K8 記述: D_e は側非依存のドリフトか（BUY 生存日 vs SELL 生存日の固定地平 市場リターン）")
for wn, wm in W.items():
    i = np.flatnonzero(CB & wm); sg = SGN[i]; nite = dd["nite"].to_numpy()[i] * 1e4; g60 = dd["G60"].to_numpy()[i] * 1e4
    okn = np.isfinite(nite); d, t = welch(nite[okn & (sg > 0)], nite[okn & (sg < 0)])
    pr = (dd["P1650"].to_numpy()[i] / RISK[i]).mean()
    say(f"- {wn}: 16:55→翌09:30 市場リターン BUY 生存日 {nite[okn&(sg>0)].mean():+.2f} / SELL 生存日 {nite[okn&(sg<0)].mean():+.2f} bp・差 {d:+.2f} (t{t:+.2f})；"
        f"全体 {nite[okn].mean():+.2f} bp (t{nite[okn].mean()/nite[okn].std(ddof=1)*math.sqrt(okn.sum()):+.1f}) ＝ {nite[okn].mean()*pr*1e-4:+.3f}R → 2× = {2*nite[okn].mean()*pr*1e-4:+.3f}R vs D_e {REP[wn]['D']:+.3f}R (t{REP[wn]['tD']:+.1f})")
# yearly D_e vs yearly night drift
De_y = []; nd_y = []
for y_ in yrs:
    i = np.flatnonzero(CB & (YEAR == y_))
    if len(i) < 10: continue
    e = RSTAR[i] - clR[off[i] + KB[i]]; sg = SGN[i]; d, _ = welch(e[sg > 0], e[sg < 0]); De_y.append(d)
    v = dd["nite"].to_numpy()[i]; nd_y.append(np.nanmean(v) * 1e4)
rho = pd.Series(De_y).corr(pd.Series(nd_y), method="spearman")
say(f"- 年別 D_e vs 年別 夜間市場リターン（横断日）Spearman ρ {rho:+.2f}（{len(De_y)} 年）")

# ---------- verdict ----------
say("\n## 判定（事前固定）")
if K1_break: v3 = "broken（K1）"
elif K3_break and K4_break: v3 = "broken（K3 ∧ K4）"
elif K3_break or K4_break: v3 = "inconclusive（K3/K4 の片方）"
else: v3 = "survived"
say(f"- C3 在「払う側・pop が損失の 18%」: K1 p(在 c) {PERM['在2013-20']['p_c']:.3f} → {'破壊' if K1_break else '不発'}；K2 Bonferroni(21) {'不通過（事後セル）' if K2_fail else '通過'}；"
    f"K3 統制後残存 → {'破壊' if K3_break else '不発'}；K4 合算窓 t → {'破壊' if K4_break else '不発'} ⇒ **{v3}**")
say(f"- C2 外 null＝選択なし: K5 部分窓/LOYO で c≤−0.02∧t≤−2 {sum(K5_hits)} 件 ⇒ **{'inconclusive（2025-26H1 の相殺）' if K5_inconc else 'survived'}**")
say(f"- C6 年別符号反転＝レジーム依存: K6 p_fw {p_fw:.3f}・正の年 max t {obs_pos_max:.2f} ⇒ **{'broken（雑音）' if K6_break else ('inconclusive（一部の年に実在する負の選択・正側は未確認）' if p_fw < 0.05 else 'inconclusive')}**")
say(f"- C7 最終印字 SL/TP 約定の疑い: K7 16:55 足ハザード比 {haz[1]/neigh if neigh else np.nan:.2f} ⇒ **{'broken（超過なし）' if K7_break else 'survived（超過あり）'}**")
say("- コスト倍: 適用不能（path 分解・戦略ではない・両側同額）。look-ahead: アンカー時点の生存・側は既知、pop は事後（受取りの測定のみ）。survivorship: 横断本は hold>k_b に選択（cycle18 自認）。D2: 窓別・16 年プール不使用。")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
