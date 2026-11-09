# -*- coding: utf-8 -*-
"""
[REFUTE 反証レーン 2026-11-09 20:15] 対象: cycle24 (18:50) 「NFP 発表窓（暦導出）」の残存弱信号。事前固定判定（PC v1 FAIL→v2 PASS／H1 null／H2 null／H3 inconclusive）は再現して争わない。
 W1 H3 在 2010-20: NFP J 日に 08:20 足で生存する再加速本 n36 の e −0.414R (日cl t−2.86)・他金曜との差 −0.295R (t−1.84)・側符号つき受取り SGN·jump −0.78R (t−1.92)・SL 78%・BUY 比 0.39
    → cycle24 の読み (4)「NFP を生きてまたぐ本は（SELL 偏り×上方ジャンプで）ジャンプを払う側」
 W2 H2: PRE 02:00→08:30 の差（NFP−他金曜）が 3 窓とも負（−5.8/−4.2/−12.1 bp・全部 MDE 以下）＋ RV_PRE 比 0.77〜0.89 ＝「発表前は弱い負＋静穏」
 W3 記述: NFP 日の DAY 08:30→16:00 在 +20.2 bp (t2.3) vs 他 +3.6（cycle24 は「追わない」と明記）
 W4 PC v2 暦: 「BLS 規則で暦だけから導ける・第 1 金曜は 16.5 年で 20 回ずれる」（v1 FAIL を見た後の第 2 パス）

=== 事前固定（この docstring を書いてから数字を見る）===
共通: cycle24 と同一定義（P(T)=ts==T−300 の close・ET 現地・窓 PRE/JUMP/POST/DAY・有効日=JUMP/POST/PRE 非 NaN かつ 08:30 足 flat の非 NFP 日を除外・J=|r_JUMP|≥他金曜 q90）。
      本の母集合: ET セッション日（建玉 18 時以降は翌暦日）＝アンカー日、08:20 足（k=(T0820−entry)/300）で hold>k≥1。金曜に制限すると cycle24 の H3 と一致（assert）。
W1（主）:
 R1 ラベル置換: 在の有効金曜の中で、年ごとに NFP-J 日数・NFP 候補日数を保存して金曜ラベルを置換（2000 回）。統計 = 生存本の e の群平均（日クラスタ t 近似）と差 (J−他)。両側 p。
 R2 受取りの分解: rec = SGN·r_JUMP·P/risk。側均等化 rec_bal = (mean rec|BUY + mean rec|SELL)/2。|rec_bal| < 0.5·|rec| なら「側構成（SELL 偏り × 正ジャンプ）」が過半。
    日単位のジャンプ符号 sign-flip（2000 回）で rec_J・rec_cand・rec_bal の両側 p（「生存本は平均してジャンプの逆側にいる」の検定）。
 R3 プラセボ（NFP 固有性）: (i) 在 他金曜の非 NFP ジャンプ日（|r_JUMP|≥q90）(ii) 在 月〜木の 08:30 ジャンプ日（|r_JUMP| ≥ 全平日 08:30 の q90・NFP 候補除く）で同じ e・rec（日cl t）。
    rec_plc ≤ −0.4R ∧ |t| ≥ 1.5 なら発火＝「08:30 ジャンプ一般で生存本は払う」（NFP 固有ではない）。
 R4 多重検定: 在の記述 6 統計 {e_J, e_cand, diff_J, diff_cand, rec_J, rec_cand} の max|t| の帰無（e 系は R1 置換・rec 系は R2 sign-flip）→ p_fw。
 R5 記述: e = e_pre(08:25 足) + e_jump(08:30 足) + e_after の分解・側別・2010-14/2015-20・LOYO・ジャンプ (bp) と PRE の関係。
 判定: broken = R1 p(diff) ≥ 0.10 ∨ (|rec_bal| < 0.5|rec| ∧ |t_bal| < 1.5) ∨ R3 発火。survived = R1 p(diff) < 0.05 ∧ t_bal ≤ −2 ∧ R3 不発 ∧ R4 p_fw < 0.05。他 inconclusive。
W2:
 P1 年内ラベル置換（2000）で PRE 差（NFP−他金曜・Welch）の両側 p: 在・外・プール 2010-26H1（構造の帰無検定・edge 判定に不使用＝D2）。
 P2 プラセボ: NFP 前日（木曜）の PRE vs 他の木曜／NFP+7 金曜 vs 他金曜／NFP−7 金曜 vs 他金曜（Welch）。
 P3 RV_PRE 中央値比（NFP/他）の置換 p（在・外・プール）。
 P4 記述: PRE を 02→05／05→08／08→08:30 ET に分解（NFP−他）。
 判定: broken = プール p ≥ 0.10 ∨ 木曜プラセボ差が同符号で観測の 0.7 倍以上かつ |t|≥1（週効果）。survived = プール p < 0.05 ∧ 在・外 同符号 ∧ P3 プール p < 0.05 ∧ プラセボ不発。他 inconclusive。
W3:
 D1 年内ラベル置換で 在 DAY 差の p、および 在の記述 6 セル {PRE,POST,DAY}×{NFP 平均の t, 差の Welch t} の max|t| → p_fw。
 D2 LOYO（在 11 年）・2010-14／2015-20・外の符号。
 判定: broken = p_fw ≥ 0.05 ∨ (外 逆符号 ∧ LOYO min|t| < 1.5)。survived = p_fw < 0.05 ∧ LOYO 全 |t| ≥ 2 ∧ 外 同符号。他 inconclusive。
W4:
 C1 v2 を参照リスト（BLS 公表日・モデル記憶・外部通信なし・2026 年は精度低）と照合。不一致を列挙し、v2 側の日と参照側の日の J フラグ（データ）を印字＝記憶に依らないデータ側の裏付け。
 C2 v3 = v2 + 「1 月の公表日 ≤ 3 日 → +7 日」+「7/3 金曜（7/4 土）→ 前日木曜」+ 閉鎖（2013-10-04→10-22 火・2013-11-01→11-08・2025-10-03/11-07/12-05 非公表）。PC・H1・H2・H3 在 を v3 で再計算。
 C3 J 閾値感度 q80/q90/q95 の J 率と PC。
 判定: broken = v3 で PC FAIL または H1/H2 判定が変わる。survived = PC PASS 維持 ∧ 不一致 ≤ 10% ∧ 不一致の v2 日は非 J・参照日は J が過半。他 inconclusive。
seed 20261109。入力 既存キャッシュのみ（XAU npz・c8 csv・c1 json・refute_c2 npz）・scan 無し・MT5 無し・外部通信無し。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c24_nfp.md"); L = []
NY = "America/New_York"; SEED = 20261109; rng = np.random.default_rng(SEED); NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c24] NFP 発表窓の残存弱信号 W1〜W4 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c24_nfp.py)")

# ---------- calendars ----------
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
def nfp_dates_v3(y0=2009, y1=2026):
    """v2 + 1 月 ≤3 日→+7 ／ 7/3 金曜（7/4 土曜）→木曜 ／ 閉鎖の記憶ベース修正"""
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day <= 3: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            if rel.month == 7 and rel.day == 3 and rel.weekday() == 4: rel -= pd.Timedelta(days=1)  # 7/4 土曜 → 7/3 金曜が振替休日
            out.append(rel)
    s = set(out)
    for d in ["2013-10-04", "2013-11-01", "2025-10-03", "2025-11-07", "2025-12-05"]: s.discard(pd.Timestamp(d))
    s.add(pd.Timestamp("2013-10-22")); s.add(pd.Timestamp("2013-11-08"))
    return pd.DatetimeIndex(sorted(s))
# 参照（モデル記憶・BLS Employment Situation 公表日・外部通信なし・2026 年は精度低・閉鎖年は注記）
REF_TXT = """
2010: 01-08 02-05 03-05 04-02 05-07 06-04 07-02 08-06 09-03 10-08 11-05 12-03
2011: 01-07 02-04 03-04 04-01 05-06 06-03 07-08 08-05 09-02 10-07 11-04 12-02
2012: 01-06 02-03 03-09 04-06 05-04 06-01 07-06 08-03 09-07 10-05 11-02 12-07
2013: 01-04 02-01 03-08 04-05 05-03 06-07 07-05 08-02 09-06 10-22 11-08 12-06
2014: 01-10 02-07 03-07 04-04 05-02 06-06 07-03 08-01 09-05 10-03 11-07 12-05
2015: 01-09 02-06 03-06 04-03 05-08 06-05 07-02 08-07 09-04 10-02 11-06 12-04
2016: 01-08 02-05 03-04 04-01 05-06 06-03 07-08 08-05 09-02 10-07 11-04 12-02
2017: 01-06 02-03 03-10 04-07 05-05 06-02 07-07 08-04 09-01 10-06 11-03 12-08
2018: 01-05 02-02 03-09 04-06 05-04 06-01 07-06 08-03 09-07 10-05 11-02 12-07
2019: 01-04 02-01 03-08 04-05 05-03 06-07 07-05 08-02 09-06 10-04 11-01 12-06
2020: 01-10 02-07 03-06 04-03 05-08 06-05 07-02 08-07 09-04 10-02 11-06 12-04
2021: 01-08 02-05 03-05 04-02 05-07 06-04 07-02 08-06 09-03 10-08 11-05 12-03
2022: 01-07 02-04 03-04 04-01 05-06 06-03 07-08 08-05 09-02 10-07 11-04 12-02
2023: 01-06 02-03 03-10 04-07 05-05 06-02 07-07 08-04 09-01 10-06 11-03 12-08
2024: 01-05 02-02 03-08 04-05 05-03 06-07 07-05 08-02 09-06 10-04 11-01 12-06
2025: 01-10 02-07 03-07 04-04 05-02 06-06 07-03 08-01 09-05
2026: 01-09 02-06 03-06 04-03 05-08 06-05
"""
REF = []
for line in REF_TXT.strip().splitlines():
    y, rest = line.split(":"); REF += [pd.Timestamp(f"{y.strip()}-{md}") for md in rest.split()]
REF = pd.DatetimeIndex(sorted(REF))

# ---------- data ----------
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)); fl = r == 0
    say(f"- {sym}: {len(ts)} 本 {pd.to_datetime(ts[0],unit='s')}〜{pd.to_datetime(ts[-1],unit='s')} UTC・格子の穴 {(np.diff(ts)!=300).sum()}")
    return ts, cl, r, fl
def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def idx_of_bar(ts, T):
    out = np.full(len(T), -1); ok = np.isfinite(T); key = T[ok].astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, pos, -1); return out
def price_at(ts, cl, T):
    i = idx_of_bar(ts, T - 300); return np.where(i >= 0, cl[np.clip(i, 0, len(cl)-1)], np.nan)
def hc1_reg(y, x):
    m = np.isfinite(y) & np.isfinite(x); y = y[m]; x = x[m]; n = len(y)
    if n < 20: return dict(b=np.nan, se=np.nan, t=np.nan, n=n)
    X = np.column_stack([np.ones(n), x]); XtXi = np.linalg.inv(X.T @ X); beta = XtXi @ X.T @ y; e = y - X @ beta
    meat = (X * e[:, None]).T @ (X * e[:, None]); V = XtXi @ meat @ XtXi * n / (n - 2); se = math.sqrt(V[1, 1])
    return dict(b=beta[1], se=se, t=beta[1] / se, n=n)
def mstats(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 5: return dict(n=n, mean=np.nan, se=np.nan, t=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return dict(n=n, mean=m, se=se, t=m / se)
def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 5 or len(b) < 5: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, se, d / se
def ols_cluster(y, Z, cl_):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); G = 0
    for c in np.unique(cl_):
        idx = cl_ == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G += 1
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G
def grp(n_d, S_d):
    """day-aggregated group mean with cluster-robust se (approx used in permutations)"""
    N = n_d.sum()
    if N < 5: return np.nan, np.nan, 0
    mu = S_d.sum() / N; G = int((n_d > 0).sum()); V = ((S_d - n_d * mu) ** 2).sum() / N ** 2 * G / max(G - 1, 1)
    return mu, math.sqrt(V), G

say("\n## データ")
ts, cl, r, fl = load("XAU")
days = pd.date_range("2010-01-01", "2026-06-30", freq="D"); days = days[days.weekday < 5]
WDN = days.weekday.to_numpy(); YR = days.year.to_numpy(); isFri = WDN == 4
P = lambda h, m: price_at(ts, cl, epoch_et(days, h, m))
p0200, p0500, p0800, p0830, p0835, p0930, p1600 = P(2, 0), P(5, 0), P(8, 0), P(8, 30), P(8, 35), P(9, 30), P(16, 0)
lg = np.log
W = dict(PRE=(lg(p0830) - lg(p0200)) * 1e4, PRE_a=(lg(p0500) - lg(p0200)) * 1e4, PRE_b=(lg(p0800) - lg(p0500)) * 1e4, PRE_c=(lg(p0830) - lg(p0800)) * 1e4,
         JUMP=(lg(p0835) - lg(p0830)) * 1e4, POST=(lg(p0930) - lg(p0835)) * 1e4, DAY=(lg(p1600) - lg(p0830)) * 1e4)
cs = np.cumsum(r ** 2)
i0200 = idx_of_bar(ts, epoch_et(days, 2, 0)); i0825 = idx_of_bar(ts, epoch_et(days, 8, 25)); okp = (i0200 >= 0) & (i0825 >= 0)
RVP = np.full(len(days), np.nan); RVP[okp] = (cs[i0825[okp]] - cs[i0200[okp] - 1]) * 1e8
i0830 = idx_of_bar(ts, epoch_et(days, 8, 30)); flat0830 = np.where(i0830 >= 0, fl[np.clip(i0830, 0, len(fl)-1)], True)
valid0 = np.isfinite(W["JUMP"]) & np.isfinite(W["POST"]) & np.isfinite(W["PRE"])
T0820 = epoch_et(days, 8, 20); P0825 = price_at(ts, cl, T0820 + 300)
day_key = (days.year * 10000 + days.month * 100 + days.day).to_numpy()
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

# trades
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy()
Jn = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
assert np.array_equal(np.sort(np.array([t["entry_time"] for t in Jn["trades"]])), ET)
FT = Jn["frozen"]["FEED_TOL"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64)
assert len(off) - 1 == N and np.all(np.diff(off) == HOLD + 1)
e_ny = pd.to_datetime(ET, unit="s", utc=True).tz_convert(NY); e_date = e_ny.normalize(); E_H = e_ny.hour.to_numpy()
anc = e_date.where(E_H < 18, e_date + pd.Timedelta(days=1))
anc_key = (anc.year * 10000 + anc.month * 100 + anc.day).to_numpy()
pos = pd.Index(day_key).get_indexer(anc_key); has = pos >= 0
TSa = np.where(has, T0820[np.clip(pos, 0, len(days)-1)], np.nan); dt = TSa - ET
kk = np.full(N, -1); good = has & np.isfinite(dt) & (dt > 0) & (np.mod(dt, 300) == 0); kk[good] = (dt[good] // 300).astype(int)
ALIVE0 = good & (HOLD > kk) & (kk >= 1)
DPOS = np.where(ALIVE0, pos, -1)
say(f"- 本 {N}・FEED_TOL {FT}・平日アンカー 08:20 足で生存（有効日条件前）{ALIVE0.sum()}（金曜 {(ALIVE0 & (WDN[np.clip(DPOS,0,len(days)-1)]==4)).sum()}）")
# path pieces
CLK = np.full(N, np.nan); E = np.full(N, np.nan); E_PRE = np.full(N, np.nan); E_JUMP = np.full(N, np.nan); E_AFT = np.full(N, np.nan); REC = np.full(N, np.nan)
ii = np.flatnonzero(ALIVE0)
for i in ii:
    k = kk[i]; h = HOLD[i]; o = off[i]; c0 = clR[o + k]; CLK[i] = c0; E[i] = RSTAR[i] - c0
    if h == k + 1: E_PRE[i] = RSTAR[i] - c0; E_JUMP[i] = 0.0; E_AFT[i] = 0.0
    else:
        c1 = clR[o + k + 1]; E_PRE[i] = c1 - c0
        if h == k + 2: E_JUMP[i] = RSTAR[i] - c1; E_AFT[i] = 0.0
        else: c2 = clR[o + k + 2]; E_JUMP[i] = c2 - c1; E_AFT[i] = RSTAR[i] - c2
    REC[i] = SGN[i] * W["JUMP"][DPOS[i]] * 1e-4 * P0825[DPOS[i]] / RISK[i]

def day_agg(sel_trades, nd):
    """per-day n and sum of e, rec for selected trades, over `nd` days (index positions)"""
    n_d = np.zeros(nd); S_e = np.zeros(nd); S_r = np.zeros(nd)
    np.add.at(n_d, DPOS[sel_trades], 1); np.add.at(S_e, DPOS[sel_trades], E[sel_trades]); np.add.at(S_r, DPOS[sel_trades], REC[sel_trades]); return n_d, S_e, S_r

def h3_row(lab, g, sel):
    ii = np.flatnonzero(sel)
    if len(ii) < 10: say(f"| {lab} | {g} | {len(ii)} | 不足 | | | | | |"); return None
    e = E[ii]; d = anc_key[ii]; b, se, G = ols_cluster(e, np.ones((len(ii), 1)), d); br, ser, _ = ols_cluster(REC[ii], np.ones((len(ii), 1)), d)
    ex = pd.Series(EXIT[ii]).value_counts(normalize=True)
    say(f"| {lab} | {g} | {len(ii)} ({G}) | {b[0]:+.3f} ({b[0]/se[0]:+.2f}) | {np.nanmean(E_PRE[ii]):+.3f}/{np.nanmean(E_JUMP[ii]):+.3f}/{np.nanmean(E_AFT[ii]):+.3f} | {br[0]:+.3f} ({br[0]/ser[0]:+.2f}) | {ex.get('SL',0)*100:.0f}/{ex.get('TP',0)*100:.0f}/{ex.get('TIME',0)*100:.0f} | {(SGN[ii]>0).mean():.2f} | {np.nanmean(W['JUMP'][DPOS[ii]]):+.1f} |")
    return dict(mean=b[0], se=se[0], t=b[0]/se[0], rec=br[0], rec_se=ser[0], rec_t=br[0]/ser[0], ii=ii)

def analyze(nfp_mask, tag):
    """PC / H1 / H2 / H3(在) under a given NFP Friday mask (over `days`). Returns dict."""
    v = valid0 & ~(flat0830 & ~nfp_mask)
    out = dict(v=v)
    # PC + J
    J = np.zeros(len(days), bool); Q90 = {}; aj = np.abs(W["JUMP"])
    say(f"\n### [{tag}] PC（|r_JUMP| 中央値比・J 率）")
    say("| 窓 | NFP n | 比 | q90 他金曜 | J 率 q90 | J 率 q80 | J 率 q95 | NFP+7 J 率 | 他金曜 J 率 |"); say("|---|---|---|---|---|---|---|---|---|")
    PC = {}
    nfp7 = np.zeros(len(days), bool); p7 = pd.Index(day_key).get_indexer(((days[nfp_mask] + pd.Timedelta(days=7)).year*10000 + (days[nfp_mask] + pd.Timedelta(days=7)).month*100 + (days[nfp_mask] + pd.Timedelta(days=7)).day).to_numpy()); nfp7[p7[p7 >= 0]] = True
    for lab, lo, hi in ERAS:
        m = v & isFri & (YR >= lo) & (YR <= hi); nf = m & nfp_mask; of = m & ~nfp_mask
        q90 = np.nanquantile(aj[of], 0.9); q80 = np.nanquantile(aj[of], 0.8); q95 = np.nanquantile(aj[of], 0.95); Q90[lab] = q90; J[nf & (aj >= q90)] = True
        ratio = np.nanmedian(aj[nf]) / np.nanmedian(aj[of]); jr = (aj[nf] >= q90).mean(); PC[lab] = (ratio >= 2) and (jr >= 0.5)
        say(f"| {lab} | {nf.sum()} | {ratio:.2f} | {q90:.1f} | **{jr*100:.0f}%** | {(aj[nf]>=q80).mean()*100:.0f}% | {(aj[nf]>=q95).mean()*100:.0f}% | {(aj[m&nfp7]>=q90).mean()*100:.0f}% | {(aj[of&~nfp7]>=q90).mean()*100:.0f}% |")
    out["PC"] = PC["在 2010-20"] and PC["外 2021-26H1"]; out["J"] = J; out["Q90"] = Q90; out["nfp7"] = nfp7
    say(f"- PC: **{'PASS' if out['PC'] else 'FAIL'}**")
    # H1
    say(f"\n### [{tag}] H1 J 日 β(POST on JUMP・HC1)")
    H1 = {}
    for lab, lo, hi in ERAS:
        m = v & isFri & (YR >= lo) & (YR <= hi) & J; rg = hc1_reg(W["POST"][m], W["JUMP"][m]); H1[lab] = rg
        say(f"- {lab}: n{rg['n']} β {rg['b']:+.3f} (t{rg['t']:+.2f}, MDE {2*rg['se']:.3f})")
    mp = v & isFri & J; rg = hc1_reg(W["POST"][mp], W["JUMP"][mp]); say(f"- プール 2010-26H1（構造の記述）: n{rg['n']} β {rg['b']:+.3f} (t{rg['t']:+.2f}, MDE {2*rg['se']:.3f})")
    out["H1"] = H1
    # H2
    say(f"\n### [{tag}] H2 PRE 差（NFP−他金曜・Welch）・RV_PRE 比・DAY 差")
    H2 = {}
    for lab, lo, hi in ERAS + [("プール 2010-26H1", 2010, 2026)]:
        m = v & isFri & (YR >= lo) & (YR <= hi); a = W["PRE"][m & nfp_mask]; b = W["PRE"][m & ~nfp_mask]; d, se, t = welch(a, b)
        rv = np.nanmedian(RVP[m & nfp_mask]) / np.nanmedian(RVP[m & ~nfp_mask]); dd_, dse, dtt = welch(W["DAY"][m & nfp_mask], W["DAY"][m & ~nfp_mask])
        H2[lab] = dict(d=d, se=se, t=t, rv=rv, day=dd_, day_t=dtt)
        say(f"- {lab}: PRE 差 {d:+.2f} bp (t{t:+.2f}, MDE {2*se:.2f})・RV_PRE 比 {rv:.2f}・DAY 差 {dd_:+.2f} (t{dtt:+.2f})")
    out["H2"] = H2
    # H3 在
    say(f"\n### [{tag}] H3 在 2010-20（アンカー 08:20・金曜）")
    say("| 窓 | 群 | n (日) | e (日cl t) | e_pre/e_jump/e_after | rec (t) | SL/TP/TIME % | BUY 比 | 日 jump bp |"); say("|---|---|---|---|---|---|---|---|---|")
    vd = v[np.clip(DPOS, 0, len(days)-1)] & ALIVE0; fri_t = isFri[np.clip(DPOS, 0, len(days)-1)]; nfp_t = nfp_mask[np.clip(DPOS, 0, len(days)-1)]; J_t = J[np.clip(DPOS, 0, len(days)-1)]
    H3 = {}
    for lab, lo, hi in ERAS:
        wm = vd & fri_t & (YEAR >= lo) & (YEAR <= hi)
        rJ = h3_row(lab, "NFP J 日", wm & J_t); rC = h3_row(lab, "NFP 候補 全日", wm & nfp_t); rO = h3_row(lab, "他の金曜", wm & ~nfp_t)
        H3[lab] = dict(J=rJ, C=rC, O=rO, wm=wm)
        for nm, a in (("J", rJ), ("C", rC)):
            if a and rO:
                y = np.r_[E[a["ii"]], E[rO["ii"]]]; xg = np.r_[np.ones(len(a["ii"])), np.zeros(len(rO["ii"]))]; c_ = np.r_[anc_key[a["ii"]], anc_key[rO["ii"]]]
                beta, se, G = ols_cluster(y, np.column_stack([np.ones(len(y)), xg]), c_); H3[lab][f"diff_{nm}"] = dict(d=beta[1], se=se[1], t=beta[1]/se[1])
                say(f"- {lab}: e 差（{'NFP J' if nm=='J' else 'NFP 候補'} − 他金曜）{beta[1]:+.3f}R (日cl t{beta[1]/se[1]:+.2f}, MDE {2*se[1]:.3f})")
    out["H3"] = H3; out["vd"] = vd; out["fri_t"] = fri_t; out["nfp_t"] = nfp_t; out["J_t"] = J_t
    return out

# ============ reproduce cycle24 (v2) ============
V2 = nfp_dates_v2(); nfp2 = days.isin(V2) & isFri
say(f"\n## 再現（v2 暦・NFP 金曜 {nfp2.sum()}）")
A2 = analyze(nfp2, "v2")
h3 = A2["H3"]["在 2010-20"]
say(f"\n- 再現 assert: e_J {h3['J']['mean']:+.4f} (目標 −0.414)・差 {h3['diff_J']['d']:+.4f} (−0.295)・rec {h3['J']['rec']:+.4f} (−0.780)・n {len(h3['J']['ii'])}/{len(h3['O']['ii'])} (36/159)")
assert abs(h3["J"]["mean"] + 0.414) < 2e-3 and abs(h3["diff_J"]["d"] + 0.295) < 2e-3 and abs(h3["J"]["rec"] + 0.780) < 2e-3 and len(h3["J"]["ii"]) == 36 and len(h3["O"]["ii"]) == 159
h2 = A2["H2"]; assert abs(h2["在 2010-20"]["d"] + 5.78) < 0.02 and abs(h2["外 2021-26H1"]["d"] + 4.19) < 0.02
assert abs(A2["H1"]["在 2010-20"]["b"] - 0.038) < 2e-3 and A2["PC"]
say("- 再現 OK（cycle24 の H1/H2/H3 在・PC と一致）")

# ============ W1 ============
say("\n## W1 H3 在「NFP をまたぐ本はジャンプを払う」")
v = A2["v"]; J = A2["J"]; vd = A2["vd"]; fri_t = A2["fri_t"]; nfp_t = A2["nfp_t"]; J_t = A2["J_t"]
IN_T = vd & fri_t & (YEAR >= 2010) & (YEAR <= 2020)          # 在の金曜生存本
IN_D = v & isFri & (YR >= 2010) & (YR <= 2020)                # 在の有効金曜
nd = len(days); n_d, S_e, S_r = day_agg(IN_T, nd)
iiJ = h3["J"]["ii"]; iiC = h3["C"]["ii"]; iiO = h3["O"]["ii"]
def stats_from_labels(labJ, labC):
    """labJ/labC: bool over days (J ⊂ C). returns dict of (mean,t) for e_J,e_C,diff_J,diff_C using day aggregates"""
    o = {}
    for nm, lab in (("J", labJ), ("C", labC)):
        mu1, se1, G1 = grp(n_d[lab], S_e[lab]); mu0, se0, G0 = grp(n_d[IN_D & ~labC], S_e[IN_D & ~labC])
        o[f"e_{nm}"] = (mu1, mu1 / se1 if se1 and se1 > 0 else np.nan); d = mu1 - mu0; o[f"diff_{nm}"] = (d, d / math.sqrt(se1**2 + se0**2) if se1 and se0 else np.nan)
    return o
obs = stats_from_labels(J & IN_D, nfp2 & IN_D)
say(f"- 日集約近似の観測値: e_J {obs['e_J'][0]:+.3f} (t{obs['e_J'][1]:+.2f})・e_C {obs['e_C'][0]:+.3f} (t{obs['e_C'][1]:+.2f})・diff_J {obs['diff_J'][0]:+.3f} (t{obs['diff_J'][1]:+.2f})・diff_C {obs['diff_C'][0]:+.3f} (t{obs['diff_C'][1]:+.2f})（ols_cluster 版: e_J t{h3['J']['t']:+.2f}・diff_J t{h3['diff_J']['t']:+.2f}）")
# R1 label permutation within year
yrs = np.arange(2010, 2021); idx_by_year = {y: np.flatnonzero(IN_D & (YR == y)) for y in yrs}
nJ_by = {y: int((J & IN_D & (YR == y)).sum()) for y in yrs}; nC_by = {y: int((nfp2 & IN_D & (YR == y)).sum()) for y in yrs}
null = {k: np.zeros(NPERM) for k in ("e_J", "e_C", "diff_J", "diff_C")}; null_maxe = np.zeros(NPERM)
for p in range(NPERM):
    labJ = np.zeros(nd, bool); labC = np.zeros(nd, bool)
    for y in yrs:
        ix = idx_by_year[y]; perm = rng.permutation(ix); labJ[perm[:nJ_by[y]]] = True; labC[perm[:nC_by[y]]] = True
    s = stats_from_labels(labJ, labC)
    for k in null: null[k][p] = s[k][1]
    null_maxe[p] = np.nanmax([abs(s[k][1]) for k in null])
def p2(nullv, o): nullv = nullv[np.isfinite(nullv)]; return (np.abs(nullv) >= abs(o)).mean()
say(f"- **R1 年内ラベル置換（{NPERM}）両側 p**: e_J {p2(null['e_J'], obs['e_J'][1]):.3f}・e_C {p2(null['e_C'], obs['e_C'][1]):.3f}・**diff_J {p2(null['diff_J'], obs['diff_J'][1]):.3f}**・diff_C {p2(null['diff_C'], obs['diff_C'][1]):.3f}（帰無 |t| 95% 点 e_J {np.nanquantile(np.abs(null['e_J']),0.95):.2f}・diff_J {np.nanquantile(np.abs(null['diff_J']),0.95):.2f}）")
p_diff = p2(null["diff_J"], obs["diff_J"][1])
# R2 receipt decomposition + sign-flip
recJ = REC[iiJ]; dJ = anc_key[iiJ]; sJ = SGN[iiJ]
def rec_stats(ii):
    rec = REC[ii]; d = anc_key[ii]; s = SGN[ii]
    b, se, _ = ols_cluster(rec, np.ones((len(ii), 1)), d); mB = rec[s > 0].mean() if (s > 0).sum() else np.nan; mS = rec[s < 0].mean() if (s < 0).sum() else np.nan
    bal = 0.5 * (mB + mS)
    # cluster se for bal via weights
    w = np.where(s > 0, 0.5 / max((s > 0).sum(), 1), 0.5 / max((s < 0).sum(), 1)); wt = w * rec
    ud = np.unique(d); S = np.array([wt[d == c].sum() for c in ud]); Ex = np.array([w[d == c].sum() for c in ud]) * bal; G = len(ud)
    se_bal = math.sqrt(((S - Ex) ** 2).sum() * G / max(G - 1, 1))
    return dict(rec=b[0], t=b[0]/se[0], mB=mB, nB=int((s > 0).sum()), mS=mS, nS=int((s < 0).sum()), bal=bal, t_bal=bal / se_bal if se_bal > 0 else np.nan)
rs = rec_stats(iiJ); rsC = rec_stats(iiC)
say(f"- **R2 受取り分解（在 NFP J 日 n36）**: rec {rs['rec']:+.3f}R (日cl t{rs['t']:+.2f})・BUY {rs['mB']:+.3f} (n{rs['nB']})・SELL {rs['mS']:+.3f} (n{rs['nS']})・**側均等化 rec_bal {rs['bal']:+.3f} (t{rs['t_bal']:+.2f})**・|bal|/|rec| {abs(rs['bal'])/abs(rs['rec']):.2f}")
say(f"  - NFP 候補 全日 n{len(iiC)}: rec {rsC['rec']:+.3f} (t{rsC['t']:+.2f})・BUY {rsC['mB']:+.3f}／SELL {rsC['mS']:+.3f}・bal {rsC['bal']:+.3f} (t{rsC['t_bal']:+.2f})")
# jump (bp) on days with alive SELL vs BUY
dJdays = np.unique(dJ); jb = {c: W["JUMP"][DPOS[iiJ][dJ == c][0]] for c in dJdays}
sell_days = [c for c in dJdays if (sJ[dJ == c] < 0).any()]; buy_days = [c for c in dJdays if (sJ[dJ == c] > 0).any()]
allJ_in = np.flatnonzero(J & IN_D)
say(f"  - 日次ジャンプ bp: 在 全 J 日 n{len(allJ_in)} 平均 {W['JUMP'][allJ_in].mean():+.1f} (sd {W['JUMP'][allJ_in].std(ddof=1):.0f})・生存本のある J 日 n{len(dJdays)} 平均 {np.mean([jb[c] for c in dJdays]):+.1f}・SELL 生存日 n{len(sell_days)} 平均 {np.mean([jb[c] for c in sell_days]):+.1f}・BUY 生存日 n{len(buy_days)} 平均 {np.mean([jb[c] for c in buy_days]):+.1f}")
# sign-flip null for rec_J, rec_C, rec_bal
def signflip_null(ii, nperm):
    rec = REC[ii]; d = anc_key[ii]; s = SGN[ii]; ud, inv = np.unique(d, return_inverse=True); outp = np.zeros((nperm, 2))
    nB = max((s > 0).sum(), 1); nS = max((s < 0).sum(), 1); w = np.where(s > 0, 0.5 / nB, 0.5 / nS)
    for p in range(nperm):
        f = rng.choice([-1.0, 1.0], size=len(ud))[inv]; rr = rec * f
        # cluster t of mean
        mu = rr.mean(); S = np.bincount(inv, weights=rr); n_c = np.bincount(inv); G = len(ud); se = math.sqrt(((S - n_c * mu) ** 2).sum() / len(rr) ** 2 * G / (G - 1))
        bal = (w * rr).sum(); Sw = np.bincount(inv, weights=w * rr); Ew = np.bincount(inv, weights=w) * bal; se_b = math.sqrt(((Sw - Ew) ** 2).sum() * G / (G - 1))
        outp[p] = (mu / se if se > 0 else 0, bal / se_b if se_b > 0 else 0)
    return outp
sfJ = signflip_null(iiJ, NPERM); sfC = signflip_null(iiC, NPERM)
say(f"- **R2 日単位 sign-flip（{NPERM}）両側 p**: rec_J {p2(sfJ[:,0], rs['t']):.3f}・rec_bal_J {p2(sfJ[:,1], rs['t_bal']):.3f}・rec_C {p2(sfC[:,0], rsC['t']):.3f}・rec_bal_C {p2(sfC[:,1], rsC['t_bal']):.3f}")
# R4 family-wise: 6 stats
obs_max = max(abs(obs["e_J"][1]), abs(obs["e_C"][1]), abs(obs["diff_J"][1]), abs(obs["diff_C"][1]), abs(rs["t"]), abs(rsC["t"]))
null_max6 = np.maximum(null_maxe, np.maximum(np.abs(sfJ[:, 0]), np.abs(sfC[:, 0])))
p_fw6 = (null_max6 >= obs_max).mean()
say(f"- **R4 多重検定（在の記述 6 統計・max|t| 観測 {obs_max:.2f}）**: p_fw {p_fw6:.3f}（帰無 max|t| 中央値 {np.median(null_max6):.2f}・95% 点 {np.quantile(null_max6,0.95):.2f}）")
# R3 placebo: generic 08:30 jump days
say("\n### R3 プラセボ（08:30 ジャンプ一般）")
say("| 窓 | 群 | n (日) | e (日cl t) | e_pre/e_jump/e_after | rec (t) | SL/TP/TIME % | BUY 比 | 日 jump bp |"); say("|---|---|---|---|---|---|---|---|---|")
aj = np.abs(W["JUMP"]); IN_ALL = v & (YR >= 2010) & (YR <= 2020) & ~nfp2
q90_all = np.nanquantile(aj[IN_ALL], 0.9); q90_fri = A2["Q90"]["在 2010-20"]
genJ_fri = IN_ALL & isFri & (aj >= q90_fri); genJ_mt = IN_ALL & ~isFri & (aj >= q90_all)
vd_all = v[np.clip(DPOS, 0, nd-1)] & ALIVE0; in_t = vd_all & (YEAR >= 2010) & (YEAR <= 2020)
R3 = {}
R3["fri"] = h3_row("在", f"他金曜 非NFPジャンプ日 (|r|≥{q90_fri:.0f})", in_t & genJ_fri[np.clip(DPOS, 0, nd-1)])
R3["mt"] = h3_row("在", f"月〜木 08:30 ジャンプ日 (|r|≥{q90_all:.0f})", in_t & genJ_mt[np.clip(DPOS, 0, nd-1)])
for w_, nm in ((0, "月"), (1, "火"), (2, "水"), (3, "木")):
    h3_row("在", f"  {nm}曜 ジャンプ日", in_t & genJ_mt[np.clip(DPOS, 0, nd-1)] & (WDN[np.clip(DPOS, 0, nd-1)] == w_))
R3["mt_all"] = h3_row("在", "月〜木 全日（非ジャンプ含む）", in_t & ~isFri[np.clip(DPOS, 0, nd-1)] & IN_ALL[np.clip(DPOS, 0, nd-1)])
R3["out_mt"] = h3_row("外 2021-26H1", f"月〜木 08:30 ジャンプ日", vd_all & (YEAR >= 2021) & ~isFri[np.clip(DPOS, 0, nd-1)] & (aj[np.clip(DPOS, 0, nd-1)] >= q90_all) & ~nfp2[np.clip(DPOS, 0, nd-1)])
R3["out_nfp"] = h3_row("外 2021-26H1", "NFP 候補 全日", vd_all & (YEAR >= 2021) & nfp_t)
fire_R3 = any(x is not None and x["rec"] <= -0.4 and abs(x["rec_t"]) >= 1.5 for x in (R3["fri"], R3["mt"]))
say(f"- R3 判定: {'発火（NFP 固有ではない）' if fire_R3 else '不発'}")
# R5 descriptive
say("\n### R5 記述（在 NFP J 日 n36）")
for nm, sel in (("BUY", SGN[iiJ] > 0), ("SELL", SGN[iiJ] < 0)):
    jj = iiJ[sel]; b, se, G = ols_cluster(E[jj], np.ones((len(jj), 1)), anc_key[jj])
    say(f"- 側 {nm}: n{len(jj)} e {b[0]:+.3f} (t{b[0]/se[0]:+.2f})・e_pre/e_jump/e_after {np.mean(E_PRE[jj]):+.3f}/{np.mean(E_JUMP[jj]):+.3f}/{np.mean(E_AFT[jj]):+.3f}・rec {REC[jj].mean():+.3f}・SL {np.mean(EXIT[jj]=='SL')*100:.0f}%・cl_k {CLK[jj].mean():+.3f}")
for lab, lo, hi in (("2010-14", 2010, 2014), ("2015-20", 2015, 2020)):
    jj = iiJ[(YEAR[iiJ] >= lo) & (YEAR[iiJ] <= hi)]
    if len(jj) >= 5:
        b, se, G = ols_cluster(E[jj], np.ones((len(jj), 1)), anc_key[jj]); say(f"- {lab}: n{len(jj)} e {b[0]:+.3f} (t{b[0]/se[0]:+.2f})・rec {REC[jj].mean():+.3f}・BUY 比 {(SGN[jj]>0).mean():.2f}")
loyo = []
for y in yrs:
    jj = iiJ[YEAR[iiJ] != y]; b, se, G = ols_cluster(E[jj], np.ones((len(jj), 1)), anc_key[jj]); loyo.append((y, b[0], b[0]/se[0], int((YEAR[iiJ]==y).sum())))
say("- LOYO e_J: " + "・".join(f"−{y} {m:+.2f} (t{t:+.2f}, 除外 {n})" for y, m, t, n in loyo))
# PRE vs JUMP relation on J days (reversal of pre-drift at announcement?)
rg = hc1_reg(W["JUMP"][allJ_in], W["PRE"][allJ_in]); rgo = hc1_reg(W["JUMP"][J & v & isFri & (YR >= 2021)], W["PRE"][J & v & isFri & (YR >= 2021)])
say(f"- 記述: J 日の JUMP on PRE β 在 {rg['b']:+.3f} (t{rg['t']:+.2f}, n{rg['n']})／外 {rgo['b']:+.3f} (t{rgo['t']:+.2f}, n{rgo['n']})（負なら発表前ドリフトの反転）")
# W1 verdict
comp = abs(rs["bal"]) < 0.5 * abs(rs["rec"]) and abs(rs["t_bal"]) < 1.5
if p_diff >= 0.10 or comp or fire_R3: W1 = "broken"
elif p_diff < 0.05 and rs["t_bal"] <= -2 and not fire_R3 and p_fw6 < 0.05: W1 = "survived"
else: W1 = "inconclusive"
say(f"\n- **W1 判定: {W1}**（R1 p(diff) {p_diff:.3f}・側構成 {'過半' if comp else '過半でない'}（|bal|/|rec| {abs(rs['bal'])/abs(rs['rec']):.2f}, t_bal {rs['t_bal']:+.2f}）・R3 {'発火' if fire_R3 else '不発'}・R4 p_fw {p_fw6:.3f}）")

# ============ W2 ============
say("\n## W2 H2「発表前は 3 窓とも弱い負＋静穏」")
def perm_welch(mask_grp, mask_all, var, nperm, stat="welch"):
    """permute group label within year among mask_all days; return null array of stat and observed"""
    yrs_ = np.unique(YR[mask_all]); idx_by = {y: np.flatnonzero(mask_all & (YR == y)) for y in yrs_}; n_by = {y: int((mask_grp & (YR == y)).sum()) for y in yrs_}
    def st(g):
        if stat == "welch": return welch(var[g], var[mask_all & ~g])[2]
        return np.nanmedian(var[g]) / np.nanmedian(var[mask_all & ~g])
    o = st(mask_grp); nul = np.zeros(nperm)
    for p in range(nperm):
        g = np.zeros(nd, bool)
        for y in yrs_:
            ix = idx_by[y]; g[rng.permutation(ix)[:n_by[y]]] = True
        nul[p] = st(g)
    return o, nul
W2P = {}
for lab, lo, hi in ERAS + [("プール 2010-26H1", 2010, 2026)]:
    m = v & isFri & (YR >= lo) & (YR <= hi); o, nul = perm_welch(nfp2 & m, m, W["PRE"], NPERM); orv, nulrv = perm_welch(nfp2 & m, m, RVP, NPERM, stat="ratio")
    W2P[lab] = dict(t=o, p=p2(nul, o), rv=orv, p_rv=(np.abs(np.log(nulrv)) >= abs(np.log(orv))).mean())
    say(f"- P1/P3 {lab}: PRE 差 t {o:+.2f} → 置換 p **{W2P[lab]['p']:.3f}**・RV_PRE 比 {orv:.2f} → 置換 p **{W2P[lab]['p_rv']:.3f}**")
# P2 placebos
thu_nfp = np.zeros(nd, bool); pth = pd.Index(day_key).get_indexer(((days[nfp2] - pd.Timedelta(days=1)).year*10000 + (days[nfp2] - pd.Timedelta(days=1)).month*100 + (days[nfp2] - pd.Timedelta(days=1)).day).to_numpy()); thu_nfp[pth[pth >= 0]] = True
nfp_m7 = np.zeros(nd, bool); pm7 = pd.Index(day_key).get_indexer(((days[nfp2] - pd.Timedelta(days=7)).year*10000 + (days[nfp2] - pd.Timedelta(days=7)).month*100 + (days[nfp2] - pd.Timedelta(days=7)).day).to_numpy()); nfp_m7[pm7[pm7 >= 0]] = True
nfp7 = A2["nfp7"]
say("- P2 プラセボ（プール 2010-26H1・Welch 差 bp (t)・RV 比）:")
PL = {}
for nm, g, base in (("NFP 前日 木曜 vs 他木曜", thu_nfp, v & (WDN == 3)), ("NFP+7 金曜 vs 他金曜(NFP 除く)", nfp7 & isFri, v & isFri & ~nfp2), ("NFP−7 金曜 vs 他金曜(NFP 除く)", nfp_m7 & isFri, v & isFri & ~nfp2)):
    d, se, t = welch(W["PRE"][base & g], W["PRE"][base & ~g]); rv = np.nanmedian(RVP[base & g]) / np.nanmedian(RVP[base & ~g]); PL[nm] = dict(d=d, t=t, rv=rv)
    d_in, _, t_in = welch(W["PRE"][base & g & (YR <= 2020)], W["PRE"][base & ~g & (YR <= 2020)]); d_out, _, t_out = welch(W["PRE"][base & g & (YR >= 2021)], W["PRE"][base & ~g & (YR >= 2021)])
    say(f"  - {nm}: {d:+.2f} (t{t:+.2f})・RV 比 {rv:.2f}［在 {d_in:+.2f} (t{t_in:+.2f})／外 {d_out:+.2f} (t{t_out:+.2f})］")
dpool, _, tpool = welch(W["PRE"][v & isFri & nfp2], W["PRE"][v & isFri & ~nfp2])
say(f"  - 観測（プール NFP 金曜 vs 他金曜）: {dpool:+.2f} (t{tpool:+.2f})")
# P4 sub-windows
say("- P4 PRE 分解（NFP−他金曜・bp (Welch t)）: " + " ｜ ".join(f"{lab}: " + "・".join(f"{nm} {welch(W[k][v&isFri&nfp2&(YR>=lo)&(YR<=hi)], W[k][v&isFri&~nfp2&(YR>=lo)&(YR<=hi)])[0]:+.2f} (t{welch(W[k][v&isFri&nfp2&(YR>=lo)&(YR<=hi)], W[k][v&isFri&~nfp2&(YR>=lo)&(YR<=hi)])[2]:+.2f})" for k, nm in (("PRE_a","02→05"),("PRE_b","05→08"),("PRE_c","08→08:30"))) for lab, lo, hi in ERAS + [("プール", 2010, 2026)]))
thu = PL["NFP 前日 木曜 vs 他木曜"]
week_eff = (np.sign(thu["d"]) == np.sign(dpool)) and abs(thu["d"]) >= 0.7 * abs(dpool) and abs(thu["t"]) >= 1
pp = W2P["プール 2010-26H1"]
if pp["p"] >= 0.10 or week_eff: W2 = "broken"
elif pp["p"] < 0.05 and np.sign(W2P["在 2010-20"]["t"]) == np.sign(W2P["外 2021-26H1"]["t"]) and pp["p_rv"] < 0.05 and not week_eff and all(abs(x["t"]) < 1.5 for x in PL.values()): W2 = "survived"
else: W2 = "inconclusive"
say(f"\n- **W2 判定: {W2}**（プール PRE 差 p {pp['p']:.3f}・RV 比 p {pp['p_rv']:.3f}・木曜プラセボ {thu['d']:+.2f} (t{thu['t']:+.2f}) {'=週効果' if week_eff else ''}）")

# ============ W3 ============
say("\n## W3 記述「NFP 日の DAY 在 +20 bp (t2.3)」")
m_in = v & isFri & (YR <= 2020)
def six_stats(g, m):
    o = []
    for k in ("PRE", "POST", "DAY"):
        o.append(mstats(W[k][m & g])["t"]); o.append(welch(W[k][m & g], W[k][m & ~g])[2])
    return np.array(o, float)
obs6 = six_stats(nfp2, m_in); idx_by = {y: np.flatnonzero(m_in & (YR == y)) for y in yrs}; n_by = {y: int((nfp2 & m_in & (YR == y)).sum()) for y in yrs}
null6 = np.zeros((NPERM, 6))
for p in range(NPERM):
    g = np.zeros(nd, bool)
    for y in yrs: g[rng.permutation(idx_by[y])[:n_by[y]]] = True
    null6[p] = six_stats(g, m_in)
p_day = (np.abs(null6[:, 5]) >= abs(obs6[5])).mean(); p_daym = (np.abs(null6[:, 4]) >= abs(obs6[4])).mean()
nullmax = np.nanmax(np.abs(null6), axis=1); p_fw_day = (nullmax >= np.nanmax(np.abs(obs6))).mean()
say(f"- D1 在 6 セル t: PRE 平均 {obs6[0]:+.2f}・PRE 差 {obs6[1]:+.2f}・POST 平均 {obs6[2]:+.2f}・POST 差 {obs6[3]:+.2f}・DAY 平均 {obs6[4]:+.2f}・DAY 差 {obs6[5]:+.2f} → 置換 p DAY 差 {p_day:.3f}・DAY 平均 {p_daym:.3f}・**max|t| {np.nanmax(np.abs(obs6)):.2f} の p_fw {p_fw_day:.3f}**（帰無 95% 点 {np.quantile(nullmax,0.95):.2f}）")
loyo_d = []
for y in yrs:
    mm = m_in & (YR != y); d, se, t = welch(W["DAY"][mm & nfp2], W["DAY"][mm & ~nfp2]); loyo_d.append((y, d, t))
say("- D2 LOYO DAY 差: " + "・".join(f"−{y} {d:+.1f} (t{t:+.2f})" for y, d, t in loyo_d))
for lab, lo, hi in (("2010-14", 2010, 2014), ("2015-20", 2015, 2020), ("外 2021-26H1", 2021, 2026)):
    mm = v & isFri & (YR >= lo) & (YR <= hi); d, se, t = welch(W["DAY"][mm & nfp2], W["DAY"][mm & ~nfp2]); say(f"- D2 {lab}: DAY 差 {d:+.1f} (t{t:+.2f})・NFP 平均 {mstats(W['DAY'][mm&nfp2])['mean']:+.1f} (t{mstats(W['DAY'][mm&nfp2])['t']:+.2f})")
out_day = welch(W["DAY"][v & isFri & (YR >= 2021) & nfp2], W["DAY"][v & isFri & (YR >= 2021) & ~nfp2])
min_loyo = min(abs(t) for _, _, t in loyo_d)
if p_fw_day >= 0.05 or (np.sign(out_day[0]) != np.sign(obs6[5]) and min_loyo < 1.5): W3 = "broken"
elif p_fw_day < 0.05 and min_loyo >= 2 and np.sign(out_day[0]) == np.sign(obs6[5]): W3 = "survived"
else: W3 = "inconclusive"
say(f"\n- **W3 判定: {W3}**（p_fw {p_fw_day:.3f}・外 DAY 差 {out_day[0]:+.1f} (t{out_day[2]:+.2f})・LOYO min|t| {min_loyo:.2f}）")

# ============ W4 ============
say("\n## W4 暦 v2 の検証")
rng_lo, rng_hi = pd.Timestamp("2010-01-01"), pd.Timestamp("2026-06-30")
ref = REF[(REF >= rng_lo) & (REF <= rng_hi)]; v2d = V2[(V2 >= rng_lo) & (V2 <= rng_hi)]; v3d = nfp_dates_v3(); v3d = v3d[(v3d >= rng_lo) & (v3d <= rng_hi)]
Jall = A2["J"]; aj = np.abs(W["JUMP"])
def jflag(d):
    p = pd.Index(day_key).get_indexer([d.year * 10000 + d.month * 100 + d.day])[0]
    if p < 0 or not np.isfinite(aj[p]): return "NaN"
    q = A2["Q90"]["在 2010-20" if d.year <= 2020 else "外 2021-26H1"]; return f"{aj[p]:.0f}bp{'J' if aj[p] >= q else '-'}"
only_v2 = [d for d in v2d if d not in set(ref)]; only_ref = [d for d in ref if d not in set(v2d)]
say(f"- C1 v2 {len(v2d)} 日 vs 参照（記憶）{len(ref)} 日: 一致 {len(set(v2d)&set(ref))}・v2 のみ {len(only_v2)}・参照のみ {len(only_ref)}（不一致率 {len(only_v2)/len(v2d)*100:.1f}%）")
say("  - v2 のみ（|r_JUMP| と J）: " + " ".join(f"{d.date()}[{jflag(d)}]" for d in only_v2))
say("  - 参照のみ（|r_JUMP| と J）: " + " ".join(f"{d.date()}[{jflag(d)}]" for d in only_ref))
only_v3 = [d for d in v3d if d not in set(ref)]; only_ref3 = [d for d in ref if d not in set(v3d)]
say(f"- C2 v3 {len(v3d)} 日 vs 参照: v3 のみ {len(only_v3)} {[str(d.date()) for d in only_v3]}・参照のみ {len(only_ref3)} {[str(d.date()) for d in only_ref3]}")
nonJ_v2 = sum(1 for d in only_v2 if jflag(d).endswith("-")); J_ref = sum(1 for d in only_ref if jflag(d).endswith("J"))
say(f"  - 不一致の v2 日で非 J: {nonJ_v2}/{len(only_v2)}・参照のみの日で J: {J_ref}/{len(only_ref)}（記憶に依らないデータ側の裏付け）")
nfp3 = days.isin(v3d) & isFri
A3 = analyze(nfp3, "v3")
h3_3 = A3["H3"]["在 2010-20"]
say(f"\n- v3 での判定: PC {'PASS' if A3['PC'] else 'FAIL'}・H1 在 β {A3['H1']['在 2010-20']['b']:+.3f} (t{A3['H1']['在 2010-20']['t']:+.2f})／外 {A3['H1']['外 2021-26H1']['b']:+.3f} (t{A3['H1']['外 2021-26H1']['t']:+.2f})・H2 在 {A3['H2']['在 2010-20']['d']:+.2f} (t{A3['H2']['在 2010-20']['t']:+.2f})／外 {A3['H2']['外 2021-26H1']['d']:+.2f} (t{A3['H2']['外 2021-26H1']['t']:+.2f})・H3 在 e_J {h3_3['J']['mean']:+.3f} (t{h3_3['J']['t']:+.2f}, n{len(h3_3['J']['ii'])})・差 {h3_3['diff_J']['d']:+.3f} (t{h3_3['diff_J']['t']:+.2f})・rec {h3_3['J']['rec']:+.3f} (t{h3_3['J']['rec_t']:+.2f})")
h1_same = (abs(A3["H1"]["在 2010-20"]["t"]) < 2) and (abs(A3["H2"]["在 2010-20"]["t"]) < 2)
mism = len(only_v2) / len(v2d)
if not A3["PC"] or not h1_same: W4 = "broken"
elif A3["PC"] and mism <= 0.10 and nonJ_v2 > len(only_v2) / 2 and J_ref > len(only_ref) / 2: W4 = "survived"
else: W4 = "inconclusive"
say(f"- **W4 判定: {W4}**（v3 PC {'PASS' if A3['PC'] else 'FAIL'}・H1/H2 null 維持 {h1_same}・不一致率 {mism*100:.1f}%）")

say(f"\n## 判定まとめ: W1 {W1}／W2 {W2}／W3 {W3}／W4 {W4}")
say(f"\n実行 {time.time()-T0:.1f} s・seed {SEED}・置換 {NPERM}・入力 既存キャッシュのみ（XAU npz・c8 csv・c1 json・refute_c2 npz）・scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
