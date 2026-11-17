# -*- coding: utf-8 -*-
"""
[REFUTE cycle44 / 2026-11-17 09:30 反証レーン] 対象 = cycle44 (06:50) の唯一の正の持ち越し
  ゲート 31 の外: 「2021-26H1 の scan 本は NFP(08:30 ET)/FOMC(14:00 ET) の発表後 2 時間に建玉すると
   同時刻の非発表日対照より Δμ(R*) +0.481R (Welch t 3.23・n 85/1440)・近年 +0.598 (t 2.70)」
  研究レーン自身の反証レーン申し送り = 「外 +0.48R を双子（同時刻・同幾何・c33 SET S）で壊せるか」

=== 事前固定（結果を見る前に確定・10 の破壊規則 / 各規則の「landed」条件を先に書く） ===
母数 = data/refute_c4_scan_paths_2010_2026.json（c4 凍結 scan・19404 本）。
R* = R + (FEED_TOL/risk)*1{exit in (SL,TP)}（cycle44 と同一）。ev = 建玉時刻が [t0, t0+7200s)。
ctrl = 非発表日（NFP/FOMC/CPI 暦を除外）の平日 ET [08:30,10:30) ∪ [14:00,16:00)。
外 = year 2021..2026、在 = 2010..2020、近年 = 2024..2026。

R1 複製: Δμ・t・n が cycle44 の数値（+0.481 / 3.23 / 85）と一致するか。
    landed = 一致しない（|Δμ| の差 >0.01 または n 不一致）。
R2 クラスタ推論: Welch t は本単位で独立を仮定する。日でクラスタ化（ev は同一発表日に複数本）。
    (a) 日クラスタ robust se、(b) 日単位 pairs ブートストラップ 2000 回（ev 日と ctrl 日を別個に再抽出）、
    (c) 発表イベント単位（NFP/FOMC 1 回 = 1 クラスタ）。
    landed = クラスタ t < 2.0。
R3 時刻ミスマッチ（双子 その1・同時刻）: ev の NFP 群は朝窓だけ・FOMC 群は午後窓だけだが ctrl は両窓プール。
    窓別に Δμ を取り直し、ev の窓構成で重み付けた Δμ_hourmatched を計算。
    landed = Δμ_hourmatched < 0.5 * Δμ_raw、または窓別 t がどちらも <2。
R4 日内双子（双子 その2・同日の別窓）: 発表日の「発表窓」本 vs 同じ発表日の「もう一方の窓」本。
    日レベルのレジーム（地合い・ボラ）を完全に落とす。
    landed = Δμ_withinday の t < 2.0 かつ点推定が raw の半分未満。
R5 幾何双子（双子 その3・c33 SET S）: 事前幾何（log atr・log risk・b・wall_kind・side・窓）で
    ev 本 1 本ずつに ctrl 本を最近傍マッチ（caliper 0.5sd・非復元）。
    landed = マッチ後 Δμ < 0.5 * Δμ_raw または t < 2.0。
R6 コスト倍: 追加コスト k*TRIG_SPREAD/risk（k=1,2,3）を両群から引く。ev 本の risk が小さいなら ev が多く損する。
    landed = k=2 で t < 2.0。破綻閾値 k* も報告。
R7 プラセボ発表日: t0 を ±7/±14/±21/±28 日ずらした偽発表日（同時刻・同窓・実発表日は除外）で同じ Δμ を再計算。
    landed = 実測 +0.481 がプラセボ分布の 95 パーセンタイル未満（経験 p ≥0.05）。
R8 ゲート校正（本命の多重検定）: ゲート 31 の在側の通過条件は |Δμ_在| ≥0.048（MDE 0.194 の 1/4）。
    ランダムな「2 時間窓の集合」（実発表日と同数・同時刻分布・非発表日から抽出）2000 組について
    在 Δμ を計算し、(a) ゲート通過率、(b) 通過した組の外 t の分布を出す。
    landed = 通過率 ≥0.5（＝ゲートはほぼ無条件）かつ 通過組の外 |t| ≥3.23 の割合 ≥0.05。
R9 年次頑健性: leave-one-year-out（外 6 年）・外半期分割・ev 日の leave-one-out jackknife。
    landed = どれか 1 年を抜くと t < 2.0。
R10 機構（用量反応・近接性）: t0 からの経過分（0-30/30-60/60-120）別 Δμ、および
    「発表後 2-4 時間」（t0+7200..t0+14400）窓の Δμ。発表が機構なら近い方が強く、2-4h は弱いはず。
    landed = 単調性なし、または 2-4h 窓が 0-2h と同程度以上。
補足: look-ahead 検査 = 使用した全列が建玉時刻までの情報か（x0/mfe/mae/exit/hold は建玉後 → 判定に使わない。
    atr・risk・b・wall_kind・side・jh のみ事前情報として扱う）。
出力: data/refute_c44_gate_ev2h.md。読取専用・発注なし・本番編集なし。seed 20261117.
"""
import os, json, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c44_gate_ev2h.md"); L = []
NY = "America/New_York"; SEED = 20261117
rng = np.random.default_rng(SEED)

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

# ---------- データ ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
NFP = nfp_dates_v2()
CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC, 14, 0)

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; TS = d["frozen"]["TRIG_SPREAD"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)

def inwin(t0s, span=7200.0, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, p_nfp = inwin(t_nfp); m_fomc, p_fomc = inwin(t_fomc)
tr["nfp"] = m_nfp; tr["fomc"] = m_fomc; tr["ev"] = m_nfp | m_fomc
tr["mins"] = np.where(m_nfp, (et_ - p_nfp) / 60.0, np.where(m_fomc, (et_ - p_fomc) / 60.0, np.nan))

e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
hh = e_ny.hour.to_numpy() + e_ny.minute.to_numpy() / 60
day = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["day"] = day; tr["hh"] = hh; tr["wd"] = e_ny.weekday.to_numpy()
evdays = pd.DatetimeIndex(list(NFP) + list(FOMC) + list(CPI))
isevday = day.isin(evdays)
tr["isevday"] = isevday
tr["am"] = (hh >= 8.5) & (hh < 10.5); tr["pm"] = (hh >= 14) & (hh < 16)
tr["inwinhours"] = tr.am | tr.pm
tr["ctrl"] = tr.inwinhours & ~isevday & (tr.wd <= 4)

ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    dm = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dm, dm / se if se > 0 else np.nan

def sub(lo, hi): return tr[(tr.year >= lo) & (tr.year <= hi)]

say("# [REFUTE cycle44] ゲート 31 外「発表後 2 時間建玉 Δμ +0.481R (t 3.23, n 85)」を壊す")
say(f"- 母数 19404 本・FEED_TOL {FT}・TRIG_SPREAD {TS}・seed {SEED}・事前固定 10 規則（docstring）")
say("")

# ---------- R1 複製 ----------
say("## R1 複製")
say("| 窓 | n ev/ctrl | Δμ (Welch t) | ev 平均/中央値 | ctrl 平均/中央値 | ev 日数 | 本/日 |")
say("|---|---|---|---|---|---|---|")
rep = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A, B = o[o.ev], o[o.ctrl]
    dm, t = welch(A.Rs, B.Rs); nd = A.day.nunique()
    rep[lab] = (dm, t, len(A), len(B), nd)
    say(f"| {lab} | {len(A)}/{len(B)} | **{dm:+.3f} ({t:+.2f})** | {A.Rs.mean():+.3f}/{A.Rs.median():+.2f} | {B.Rs.mean():+.3f}/{B.Rs.median():+.2f} | {nd} | {len(A)/max(nd,1):.2f} |")
DM_OUT, T_OUT, N_OUT = rep["外 2021-26H1"][0], rep["外 2021-26H1"][1], rep["外 2021-26H1"][2]
say(f"- R1 判定: cycle44 報告 +0.481 / t 3.23 / n 85 → 実測 {DM_OUT:+.3f} / {T_OUT:+.2f} / {N_OUT}  "
    f"=> {'複製 OK（landed せず）' if (abs(DM_OUT-0.481)<=0.01 and N_OUT==85) else 'LANDED（複製不一致）'}")
say("")

# ---------- R2 クラスタ推論 ----------
say("## R2 クラスタ推論（日クラスタ・ブートストラップ・イベントクラスタ）")
def cluster_t(A, B, keyA, keyB):
    """2 標本平均差の日クラスタ robust se（群別に clustered mean の se を出して合成）"""
    def cl_se(x, k):
        g = pd.DataFrame({"x": np.asarray(x, float), "k": np.asarray(k)})
        n = len(g); m = g.x.mean()
        s = g.groupby("k").x.apply(lambda v: (v - m).sum())
        G = len(s)
        if G < 2: return np.nan, G
        v = (s.pow(2).sum()) / (n ** 2) * (G / (G - 1.0))
        return math.sqrt(v), G
    sa, Ga = cl_se(A, keyA); sb, Gb = cl_se(B, keyB)
    dm = np.mean(A) - np.mean(B); se = math.sqrt(sa ** 2 + sb ** 2)
    return dm, dm / se, Ga, Gb

def pairs_boot(A, kA, B, kB, reps=2000):
    A = np.asarray(A, float); B = np.asarray(B, float)
    ua = pd.unique(kA); ub = pd.unique(kB)
    ia = {u: np.where(kA == u)[0] for u in ua}; ib = {u: np.where(kB == u)[0] for u in ub}
    out = np.empty(reps)
    for r in range(reps):
        sa = np.concatenate([ia[u] for u in rng.choice(ua, len(ua), replace=True)])
        sb = np.concatenate([ib[u] for u in rng.choice(ub, len(ub), replace=True)])
        out[r] = A[sa].mean() - B[sb].mean()
    return out

say("| 窓 | Welch t | 日クラスタ t (G_ev/G_ctrl) | boot sd | boot t | boot p(両側) | イベントクラスタ t |")
say("|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A, B = o[o.ev], o[o.ctrl]
    dm, tw = welch(A.Rs, B.Rs)
    _, tc, Ga, Gb = cluster_t(A.Rs.to_numpy(), B.Rs.to_numpy(), A.day.to_numpy(), B.day.to_numpy())
    bo = pairs_boot(A.Rs.to_numpy(), A.day.to_numpy(), B.Rs.to_numpy(), B.day.to_numpy())
    sd = bo.std(ddof=1); tb = dm / sd if sd > 0 else np.nan
    pb = 2 * min((bo <= 0).mean(), (bo >= 0).mean())
    # イベントクラスタ = 発表 1 回（NFP 日 or FOMC 日）
    evk = A.day.astype(str) + np.where(A.nfp, "_N", "_F")
    _, te, Ge, _ = cluster_t(A.Rs.to_numpy(), B.Rs.to_numpy(), evk.to_numpy(), B.day.to_numpy())
    say(f"| {lab} | {tw:+.2f} | {tc:+.2f} ({Ga}/{Gb}) | {sd:.3f} | {tb:+.2f} | {pb:.4f} | {te:+.2f} (G {Ge}) |")
say("")

# ---------- R3 時刻ミスマッチ（双子1） ----------
say("## R3 双子1 = 同時刻（窓別 Δμ と ev 窓構成で重み付け）")
say("| 窓 | 群 | n ev/ctrl | Δμ (t) |")
say("|---|---|---|---|")
hm = {}
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A, B = o[o.ev], o[o.ctrl]
    parts = []
    for wlab, mA, mB in [("朝 08:30-10:30 (NFP)", A.am, B.am), ("午後 14:00-16:00 (FOMC)", A.pm, B.pm)]:
        a, b = A[mA], B[mB]; dm, t = welch(a.Rs, b.Rs)
        say(f"| {lab} | {wlab} | {len(a)}/{len(b)} | {dm:+.3f} ({t:+.2f}) |")
        parts.append((len(a), dm, a.Rs.var(ddof=1) / max(len(a),1) + b.Rs.var(ddof=1) / max(len(b),1)))
    W = sum(p[0] for p in parts)
    dmw = sum(p[0] * p[1] for p in parts) / W
    sew = math.sqrt(sum((p[0] / W) ** 2 * p[2] for p in parts))
    hm[lab] = (dmw, dmw / sew)
    say(f"| {lab} | **窓構成で重み付け（hour-matched）** | {W} | **{dmw:+.3f} ({dmw/sew:+.2f})** |")
say(f"- R3 判定: 外 raw {DM_OUT:+.3f} → hour-matched {hm['外 2021-26H1'][0]:+.3f} (t {hm['外 2021-26H1'][1]:+.2f})  "
    f"=> {'LANDED' if (hm['外 2021-26H1'][0] < 0.5*DM_OUT or abs(hm['外 2021-26H1'][1])<2) else 'landed せず'}")
say("")

# ---------- R4 日内双子 ----------
say("## R4 双子2 = 日内（同じ発表日の「もう一方の窓」本を対照に）")
say("| 窓 | n ev/同日他窓 | Δμ (t) | 日クラスタ t | 同日ペア日数 | ペア内差平均 (t) |")
say("|---|---|---|---|---|---|")
# NFP 日: ev=朝窓, twin=午後窓(14:00-16:00) / FOMC 日: ev=午後窓, twin=朝窓
nfpd = set(NFP.normalize()); fomcd = set(FOMC.normalize())
isn = tr.day.isin(nfpd); isf = tr.day.isin(fomcd)
twin = ((isn & tr.pm & ~tr.ev) | (isf & tr.am & ~tr.ev)) & (tr.wd <= 4)
tr["twin"] = twin
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A, B = o[o.ev], o[o.twin]
    dm, t = welch(A.Rs, B.Rs)
    _, tc, _, _ = cluster_t(A.Rs.to_numpy(), B.Rs.to_numpy(), A.day.to_numpy(), B.day.to_numpy()) if len(B) > 2 else (np.nan, np.nan, 0, 0)
    ma = A.groupby("day").Rs.mean(); mb = B.groupby("day").Rs.mean()
    j = pd.concat([ma.rename("a"), mb.rename("b")], axis=1).dropna()
    if len(j) > 2:
        dd = j.a - j.b; tp = dd.mean() / (dd.std(ddof=1) / math.sqrt(len(dd)))
    else: dd, tp = pd.Series(dtype=float), np.nan
    say(f"| {lab} | {len(A)}/{len(B)} | {dm:+.3f} ({t:+.2f}) | {tc:+.2f} | {len(j)} | {dd.mean() if len(j)>2 else float('nan'):+.3f} ({tp:+.2f}) |")
say("")

# ---------- R5 幾何双子（c33 SET S） ----------
say("## R5 双子3 = 幾何マッチ（log atr・log risk・b を caliper 0.5sd・同 side/wall_kind/窓・非復元）")
def geo_match(A, B, caliper=0.5):
    cols = ["atr", "risk", "b"]
    X = np.column_stack([np.log(A.atr.to_numpy()), np.log(A.risk.to_numpy()), A.b.to_numpy()])
    Y = np.column_stack([np.log(B.atr.to_numpy()), np.log(B.risk.to_numpy()), B.b.to_numpy()])
    sdv = np.std(np.vstack([X, Y]), axis=0, ddof=1); sdv[sdv == 0] = 1
    Xs, Ys = X / sdv, Y / sdv
    strA = (A.side.astype(str) + "|" + A.wall_kind.astype(str) + "|" + np.where(A.am, "AM", "PM")).to_numpy()
    strB = (B.side.astype(str) + "|" + B.wall_kind.astype(str) + "|" + np.where(B.am, "AM", "PM")).to_numpy()
    used = np.zeros(len(B), bool); pa, pb = [], []
    order = np.argsort(rng.random(len(A)))
    for i in order:
        cand = np.where((strB == strA[i]) & ~used)[0]
        if len(cand) == 0: continue
        dist = np.sqrt(((Ys[cand] - Xs[i]) ** 2).sum(1))
        k = int(np.argmin(dist))
        if dist[k] > caliper * math.sqrt(3): continue
        used[cand[k]] = True; pa.append(i); pb.append(cand[k])
    return np.array(pa, int), np.array(pb, int)

say("| 窓 | マッチ数/ev | Δμ_matched (t) | ペア差平均 (対応 t) | 日クラスタ t | ev atr/risk/b 中央値 | ctrl(全) atr/risk/b 中央値 |")
say("|---|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A, B = o[o.ev].reset_index(drop=True), o[o.ctrl].reset_index(drop=True)
    pa, pb = geo_match(A, B)
    if len(pa) < 10:
        say(f"| {lab} | {len(pa)}/{len(A)} | マッチ不足 | | | | |"); continue
    a, b = A.iloc[pa], B.iloc[pb]
    dm, t = welch(a.Rs, b.Rs)
    dd = a.Rs.to_numpy() - b.Rs.to_numpy(); tp = dd.mean() / (dd.std(ddof=1) / math.sqrt(len(dd)))
    _, tc, _, _ = cluster_t(a.Rs.to_numpy(), b.Rs.to_numpy(), a.day.to_numpy(), b.day.to_numpy())
    say(f"| {lab} | {len(pa)}/{len(A)} | {dm:+.3f} ({t:+.2f}) | {dd.mean():+.3f} ({tp:+.2f}) | {tc:+.2f} | "
        f"{A.atr.median():.3f}/{A.risk.median():.2f}/{A.b.median():.2f} | {B.atr.median():.3f}/{B.risk.median():.2f}/{B.b.median():.2f} |")
# 幾何の在外差（バランス診断）
say("- バランス診断（外 2021-26H1・ev vs ctrl・標準化差 SMD）:")
o = sub(2021, 2026); A, B = o[o.ev], o[o.ctrl]
for c in ["atr", "risk", "b", "hh"]:
    sp = math.sqrt((A[c].var(ddof=1) + B[c].var(ddof=1)) / 2)
    say(f"  - {c}: ev {A[c].mean():.4f} / ctrl {B[c].mean():.4f} / SMD {(A[c].mean()-B[c].mean())/sp:+.3f}")
say("")

# ---------- R6 コスト倍 ----------
say("## R6 コスト倍（追加 k*TRIG_SPREAD/risk を両群から控除）")
say("| 窓 | k=0 | k=1 | k=2 | k=3 | 破綻 k*(t<2) |")
say("|---|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A, B = o[o.ev], o[o.ctrl]
    row = []; kstar = None
    for k in (0, 1, 2, 3):
        a = A.Rs - k * TS / A.risk; b = B.Rs - k * TS / B.risk
        dm, t = welch(a, b); row.append(f"{dm:+.3f} ({t:+.2f})")
    for k in np.arange(0, 12.01, 0.25):
        a = A.Rs - k * TS / A.risk; b = B.Rs - k * TS / B.risk
        dm, t = welch(a, b)
        if abs(t) < 2.0: kstar = k; break
    say(f"| {lab} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {('>12' if kstar is None else f'{kstar:.2f}')} |")
say("")

# ---------- R7 プラセボ発表日 ----------
say("## R7 プラセボ（t0 を ±7/14/21/28 日ずらした偽発表日）")
say("| シフト日 | 在 Δμ (t) | 外 Δμ (t) | n 外 |")
say("|---|---|---|---|")
pl_out = []
for sh in [-28, -21, -14, -7, 7, 14, 21, 28]:
    off = sh * 86400.0
    mn, pn = inwin(t_nfp, off=off); mf, pf = inwin(t_fomc, off=off)
    mev = mn | mf
    # 偽発表日が実発表日（NFP/FOMC/CPI）に当たる本は除外
    mev = mev & ~isevday
    tmp = tr.assign(pev=mev)
    r = []
    for lo, hi in [(2010, 2020), (2021, 2026)]:
        o = tmp[(tmp.year >= lo) & (tmp.year <= hi)]; a, b = o[o.pev], o[o.ctrl]
        dm, t = welch(a.Rs, b.Rs); r.append((dm, t, len(a)))
    pl_out.append(r[1][0])
    say(f"| {sh:+d} | {r[0][0]:+.3f} ({r[0][1]:+.2f}) | {r[1][0]:+.3f} ({r[1][1]:+.2f}) | {r[1][2]} |")
pl = np.array(pl_out)
say(f"- プラセボ外 Δμ: 平均 {pl.mean():+.3f}・sd {pl.std(ddof=1):.3f}・max {pl.max():+.3f}・実測 {DM_OUT:+.3f} 超は {int((pl>=DM_OUT).sum())}/{len(pl)}")
say("")

# ---------- R8 ゲート校正（多重検定の本命） ----------
say("## R8 ゲート 31 の校正（在 |Δμ|≥0.048 はどれだけ無条件か／通過組の外 t 分布）")
# 非発表日の平日から「実発表日と同数・同時刻窓構成」の偽イベント集合を 2000 組
allday = pd.DatetimeIndex(sorted(tr.day.unique()))
cand_days = allday[(~allday.isin(evdays)) & (allday.weekday <= 4)]
n_nfp_real = int(pd.Series(NFP.normalize()).isin(allday).sum())
n_fomc_real = int(pd.Series(FOMC.normalize()).isin(allday).sum())
cd = np.asarray(cand_days)
reps8 = 2000; rows = []
Rs_all = tr.Rs.to_numpy(); day_i = tr.day.to_numpy(); yr = tr.year.to_numpy()
ctrl_m = tr.ctrl.to_numpy(); am_m = tr.am.to_numpy(); pm_m = tr.pm.to_numpy()
for r in range(reps8):
    pick_am = rng.choice(len(cd), n_nfp_real, replace=False)
    pick_pm = rng.choice(len(cd), n_fomc_real, replace=False)
    sa = set(cd[pick_am]); sp = set(cd[pick_pm])
    m = (np.isin(day_i, list(sa)) & am_m) | (np.isin(day_i, list(sp)) & pm_m)
    out = []
    for lo, hi in [(2010, 2020), (2021, 2026)]:
        e = m & (yr >= lo) & (yr <= hi); c = ctrl_m & (yr >= lo) & (yr <= hi) & ~m
        if e.sum() < 5: out.append((np.nan, np.nan)); continue
        dm, t = welch(Rs_all[e], Rs_all[c]); out.append((dm, t))
    rows.append((out[0][0], out[0][1], out[1][0], out[1][1]))
G = pd.DataFrame(rows, columns=["dm_in", "t_in", "dm_out", "t_out"]).dropna()
passg = G[G.dm_in.abs() >= 0.048]
say(f"- 偽イベント集合 {len(G)} 組（朝 {n_nfp_real} 日 + 午後 {n_fomc_real} 日・非発表日から抽出）")
say(f"- 在 |Δμ| ≥0.048 の**ゲート通過率 = {len(passg)/len(G)*100:.1f}%**（在 Δμ の sd {G.dm_in.std(ddof=1):.3f}・|Δμ| 中央値 {G.dm_in.abs().median():.3f}）")
if len(passg) > 20:
    say(f"- 通過組の外 t: sd {passg.t_out.std(ddof=1):.2f}・|t|≥2 {(passg.t_out.abs()>=2).mean()*100:.1f}%・"
        f"|t|≥3.23 **{(passg.t_out.abs()>=3.23).mean()*100:.2f}%**・t≥+3.23 {(passg.t_out>=3.23).mean()*100:.2f}%")
    say(f"- 通過組の外 Δμ: sd {passg.dm_out.std(ddof=1):.3f}・Δμ≥+0.481 **{(passg.dm_out>=DM_OUT).mean()*100:.2f}%**")
say(f"- 全組（ゲート無視）の外 t: sd {G.t_out.std(ddof=1):.2f}・t≥+3.23 {(G.t_out>=3.23).mean()*100:.2f}%・Δμ≥+0.481 {(G.dm_out>=DM_OUT).mean()*100:.2f}%")
say("")

# ---------- R9 年次頑健性 ----------
say("## R9 leave-one-year-out（外）・半期分割・ev 日 jackknife")
o = sub(2021, 2026); A, B = o[o.ev], o[o.ctrl]
say("| 抜いた年 | n ev | Δμ (t) |")
say("|---|---|---|")
tmin = (9e9, None)
for y in range(2021, 2027):
    a, b = A[A.year != y], B[B.year != y]
    if len(a) < 5: continue
    dm, t = welch(a.Rs, b.Rs)
    say(f"| {y} | {len(a)} | {dm:+.3f} ({t:+.2f}) |")
    if abs(t) < tmin[0]: tmin = (abs(t), y)
say(f"- 最小 |t| = {tmin[0]:.2f}（{tmin[1]} を抜いたとき）")
jk = []
for dd_ in A.day.unique():
    a = A[A.day != dd_]
    dm, t = welch(a.Rs, B.Rs); jk.append(t)
jk = np.array(jk)
say(f"- ev 日 leave-one-out jackknife t: min {jk.min():+.2f}・max {jk.max():+.2f}・<2 の日数 {int((jk<2).sum())}/{len(jk)}")
say("")

# ---------- R10 機構（近接性・用量反応） ----------
say("## R10 機構（t0 からの経過分・発表後 2-4 時間窓）")
say("| 窓 | 0-30 分 n/Δμ(t) | 30-60 分 n/Δμ(t) | 60-120 分 n/Δμ(t) |")
say("|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A, B = o[o.ev], o[o.ctrl]
    cells = []
    for m0, m1 in [(0, 30), (30, 60), (60, 120)]:
        a = A[(A.mins >= m0) & (A.mins < m1)]
        dm, t = welch(a.Rs, B.Rs) if len(a) > 2 else (np.nan, np.nan)
        cells.append(f"{len(a)}/{dm:+.3f}({t:+.2f})")
    say(f"| {lab} | {cells[0]} | {cells[1]} | {cells[2]} |")
# 2-4h 窓（NFP 10:30-12:30 / FOMC 16:00-18:00）
m2n, p2n = inwin(t_nfp, span=7200.0, off=7200.0); m2f, p2f = inwin(t_fomc, span=7200.0, off=7200.0)
tr["ev24"] = (m2n | m2f)
say("| 窓 | 0-2h（本体）n/Δμ(t) | 2-4h n/Δμ(t) |")
say("|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); B = o[o.ctrl]
    a1 = o[o.ev]; a2 = o[o.ev24 & ~o.ev]
    d1, t1 = welch(a1.Rs, B.Rs); d2, t2 = welch(a2.Rs, B.Rs) if len(a2) > 2 else (np.nan, np.nan)
    say(f"| {lab} | {len(a1)}/{d1:+.3f}({t1:+.2f}) | {len(a2)}/{d2:+.3f}({t2:+.2f}) |")
say("")

# ---------- look-ahead / 分布 ----------
say("## 補助: 分布と look-ahead 検査")
o = sub(2021, 2026); A, B = o[o.ev], o[o.ctrl]
say(f"- 外 ev: n {len(A)}・日数 {A.day.nunique()}・Σ R* {A.Rs.sum():+.2f}・上位 1 本 {A.Rs.max():+.2f}（Σ の {A.Rs.max()/max(A.Rs.sum(),1e-9)*100:.0f}%）")
srt = A.Rs.sort_values(ascending=False)
for k in (1, 3, 5, 10):
    a3 = A.drop(srt.index[:k]); dm, t = welch(a3.Rs, B.Rs)
    say(f"  - 上位 {k} 本除去: Δμ {dm:+.3f} (t {t:+.2f})")
say(f"- 符号検定（ev R*>0 の割合 vs ctrl）: ev {(A.Rs>0).mean()*100:.1f}% / ctrl {(B.Rs>0).mean()*100:.1f}%")
say(f"- 使用列は事前情報のみ（atr/risk/b/wall_kind/side/entry_time）。x0・mfe・mae・exit・hold は建玉後 → 判定に未使用（記述のみ）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
