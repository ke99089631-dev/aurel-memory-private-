# -*- coding: utf-8 -*-
"""
[反証レーン 続き・走 3]
走 2 の 2 点を直す／伸ばす。

(A) **走 2 の K-3 は私のバグで n=0（全 NaN）**。tz-aware DatetimeIndex に .view("int64") を使ったため
    London ローカル時刻 → UTC グリッド添字の変換が全滅した。.asi8 で直して c50 の LBMA PRE 足と
    「同じ 分-of-hour の他スロット」基準線を出し直す（走 2 で印字した BREAK-K1 上書き裁定の
    nan% は無効＝走 3 の数字で裁定し直す）。

(B) 走 2 の K-6 が出した一番効く数字を正しい DiD にする。アジア帯の 分 :15 ビンは P1 で一般に正
    （+0.166 bp・12 ビン中 2 番目に正）。SGE POST 足の「同分ビン超過」は P1 +0.382 (t 3.77)／
    **P0 +0.248 (t 2.34)** ＝時間内プラセボも同分基準で見ると清くない。c54 の DiD（+0.415・t 2.72）は
    隣接 ±30 分（分ビン無差別）の超過で測ったもの。**同じ 分-of-hour で揃えた二重差**を計算する:
      X_day = r(02:15) − 同日の 他の :15 足（UTC 00–08・02:15/06:15 を除く）の平均
      DiD   = mean X[P1] − mean X[P0]
    事前固定の BREAK 条件（走 3 を走らせる前に確定）:
      BREAK-N1: 分-of-hour を揃えた二重差の |t| < 2.24（c54 自身が H_REB に使った Bonferroni(2) 閾値）
                → 「2016-20 の SGE 直後 5 分」の**制度帰属**は分-of-hour の交絡で説明され得る。
      BREAK-N2: 同条件を 06:15 でも計算し、AM・PM の**両方**が t < 2.24 → 「2 つの独立な時計」の
                根拠が同時に消える。
      （05:15 を基準線に含める版／除く版の両方を印字。05:15 は c54 のプラセボで唯一点灯した足。）
(C) 走 2 の機構結果（P1 の +0.5 は 10 分で +0.87 に積み上がり 35 分で +0.45 に減衰）を半減期で数にする。
    BREAK-N3: PM P1 の累積が +25 分で +5 分値の 50% 未満 → 一時的な流動性の窪みで、c54 の機構候補
    「輸入銀行の裁定買いによる価格発見」は支持されない（恒久なら減衰しない）。

seed 20261119。読取り専用・npz のみ。
"""
import os, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c54_sge_c_result.md")
SEED = 20261119; rng = np.random.default_rng(SEED)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
VERD = []
def brk(tag, cond, obs, broken):
    say(f"- [{tag}] 条件: {cond}")
    say(f"  - 観測: {obs}")
    say(f"  - 判定: {'BROKEN' if broken else 'not broken'}")
    VERD.append((tag, bool(broken)))

say(f"# [REFUTE c54 走 3] 分-of-hour を揃えた二重差・c50 の沈みの分解（走 2 の bug fix）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c54_sge_c.py)")

z = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
r_raw = np.zeros(len(cl)); r_raw[1:] = np.diff(np.log(cl)); r_raw *= 1e4
flat_raw = (r_raw == 0)
t0 = (ts[0] // 86400) * 86400; t1 = ((ts[-1] // 86400) + 1) * 86400 - 300
N = (t1 - t0) // 300 + 1; ND = N // 288
G = np.full(N, np.nan); FL = np.zeros(N, bool); PRESENT = np.zeros(N, bool)
gi = (ts - t0) // 300; G[gi] = r_raw; FL[gi] = flat_raw; PRESENT[gi] = True
day_start = t0 + np.arange(ND) * 288 * 300
dday = pd.to_datetime(day_start, unit="s", utc=True)
dwd = dday.weekday.to_numpy(); dyear = dday.year.to_numpy()
dnorm = pd.DatetimeIndex(dday.tz_localize(None))
def S(h, m): return h * 12 + m // 5
AMS, PMS = S(2, 15), S(6, 15)
P0 = (dnorm >= "2010-01-01") & (dnorm <= "2016-04-18")
P1 = (dnorm >= "2016-04-19") & (dnorm <= "2020-12-31")
P2 = (dnorm >= "2021-01-01"); PR = (dnorm >= "2024-01-01")
PERS = [("P0", P0), ("P1", P1), ("P2", P2), ("近年", PR)]
minute_of_hour = (np.arange(288) % 12) * 5

def stat(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return dict(n=n, m=np.nan, se=np.nan, t=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
    return dict(n=n, m=m, se=se, t=m / se if se > 0 else np.nan)
def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    d = a.mean() - b.mean(); return d, d / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))

# c54's own validity filter (13-bar window, >=8 non-flat), needed so the comparison is apples-to-apples
def c54_ok(s, half=6, nf=8):
    base = np.arange(ND) * 288 + s; idx = base[:, None] + np.arange(-half, half + 1)[None, :]
    good = (idx[:, 0] >= 0) & (idx[:, -1] < N); idxc = np.clip(idx, 0, N - 1)
    return good & PRESENT[idxc].all(axis=1) & (((~FL[idxc]) & PRESENT[idxc]).sum(axis=1) >= nf) & (dwd <= 4)

okAM = c54_ok(AMS); okPM = c54_ok(PMS)

# ============ A. fixed London-local slot mapping → c50's LBMA dip decomposition =======================
say("\n## A（走 2 の bug fix）c50 の LBMA 沈みと「同 分-of-hour の他スロット」基準線")
def london_slot(hh, mm):
    loc = dnorm + pd.Timedelta(hours=hh, minutes=mm)
    aware = loc.tz_localize("Europe/London", nonexistent="NaT", ambiguous="NaT")
    bad = np.asarray(pd.isna(aware))
    utc = aware.tz_convert("UTC")
    sec = np.asarray(utc.asi8, dtype="float64") / 1e9
    out = np.full(ND, -1, dtype=np.int64)
    gidx = ((sec - t0) / 300)
    okm = (~bad) & np.isfinite(gidx) & (gidx >= 0) & (gidx < N)
    out[okm] = np.round(gidx[okm]).astype(np.int64)
    return out

lon_band = np.isin(np.arange(288) // 12, list(range(7, 17)))
C50 = [("c50-P1 2010-13", (dnorm >= "2010-01-01") & (dnorm <= "2013-12-31")),
       ("c50-P2 2014-01〜2015-03-19", (dnorm >= "2014-01-01") & (dnorm <= "2015-03-19")),
       ("c50-P3 2015-03-20〜2020", (dnorm >= "2015-03-20") & (dnorm <= "2020-12-31")),
       ("c50-P4 2021-26H1", (dnorm >= "2021-01-01"))]
C50REF = {("AM", "c50-P1 2010-13"): -1.34, ("AM", "c50-P3 2015-03-20〜2020"): -0.65, ("AM", "c50-P4 2021-26H1"): -1.07,
          ("PM", "c50-P2 2014-01〜2015-03-19"): -2.21, ("PM", "c50-P3 2015-03-20〜2020"): -0.90, ("PM", "c50-P4 2021-26H1"): -0.86}
K1 = {}
for tag, (ah, am_) in [("AM", (10, 30)), ("PM", (15, 0))]:
    ph, pm_ = (ah, am_ - 5) if am_ >= 5 else (ah - 1, 55)
    gs = london_slot(ph, pm_)
    valid = (gs >= 0)
    own = np.full(ND, np.nan)
    pres = valid & PRESENT[np.clip(gs, 0, N - 1)] & (dwd <= 4)
    own[pres] = G[gs[pres]]
    mo = pm_
    cols = np.flatnonzero(lon_band & (minute_of_hour == mo))
    say(f"\n### {tag} オークション {ah:02d}:{am_:02d} London → PRE 足 {ph:02d}:{pm_:02d}（分 :{mo:02d}）"
        f"・UTC スロット分布 {dict(pd.Series(np.where(valid, gs % 288, -1)[valid]).value_counts().head(3))}")
    for nm, msk in C50:
        a = own[msk]
        rows = np.flatnonzero(msk & (dwd <= 4))
        idx = (rows[:, None] * 288 + cols[None, :])
        excl = (idx == gs[rows][:, None])
        keep = PRESENT[idx] & (~excl)
        bl = G[idx][keep]
        sa = stat(a); sb = stat(bl); d_, t_ = welch(a[np.isfinite(a)], bl)
        ref = C50REF.get((tag, nm))
        share = (sb["m"] / sa["m"] * 100) if (sa["m"] < 0 and sb["m"] < 0) else 0.0
        say(f"- {nm}: PRE 足 **{sa['m']:+.3f} bp (t {sa['t']:+.2f}, n {sa['n']})**"
            + (f"〔c50 公表 {ref:+.2f}〕" if ref is not None else "")
            + f"／同分 :{mo:02d} 基準線 {sb['m']:+.3f} (t {sb['t']:+.2f}, n {sb['n']})"
            + f"／**超過 {d_:+.3f} (Welch t {t_:+.2f})**・時計ビンが説明する割合 {share:.0f}%")
        K1[(tag, nm)] = (sa["m"], sb["m"], d_, t_, share)
sh = [v[4] for k, v in K1.items() if v[0] < 0 and v[1] < 0]
brk("BREAK-K1 (走 3 で裁定し直し)",
    "c50 の沈みが「分 :25／:55 の時計ビン」でおおむね説明される（説明割合の中央値 ≥ 50%）",
    "／".join(f"{k[0]} {k[1].split()[0]}: 沈み {v[0]:+.2f}・基準線 {v[1]:+.2f}・超過 {v[2]:+.2f} (t {v[3]:+.1f})・説明 {v[4]:.0f}%"
              for k, v in K1.items())
    + f" → 負×負のセルの説明割合 中央値 {np.median(sh) if sh else float('nan'):.0f}%",
    bool(sh) and float(np.median(sh)) >= 50)

# ============ B. minute-of-hour-matched double difference ===========================================
say("\n## B 分-of-hour を揃えた二重差（c54 の DiD は隣接 ±30 分＝分ビン無差別の超過で測っている）")
def mo_matched(s_target, drop0515=True, band=(0, 8)):
    mo = minute_of_hour[s_target]
    lo, hi = band
    cand = [s for s in range(288) if (lo * 12 <= s < hi * 12) and minute_of_hour[s] == mo and s not in (AMS, PMS)]
    if drop0515 and S(5, 15) in cand: cand.remove(S(5, 15))
    cand = np.array(cand)
    rows = np.arange(ND)
    idx = rows[:, None] * 288 + cand[None, :]
    W = np.where(PRESENT[idx], G[idx], np.nan)
    bl = np.nanmean(W, axis=1)
    own_i = rows * 288 + s_target
    own = np.where(PRESENT[own_i], G[own_i], np.nan)
    return own - bl, cand

for lab, s_, ok in [("AM 02:15", AMS, okAM), ("PM 06:15", PMS, okPM)]:
    for drop in (True, False):
        X, cand = mo_matched(s_, drop0515=drop)
        Xo = np.where(ok, X, np.nan)
        s0 = stat(Xo[P0]); s1 = stat(Xo[P1]); s2 = stat(Xo[P2]); sr = stat(Xo[PR])
        d10, t10 = welch(Xo[P1], Xo[P0]); d20, t20 = welch(Xo[P2], Xo[P0])
        say(f"- {lab}・基準線 = 同日の 分 :{minute_of_hour[s_]:02d} 足 "
            f"{[f'{c//12:02d}:{(c%12)*5:02d}' for c in cand]}"
            + (" (05:15 除く)" if drop else " (05:15 含む)"))
        say(f"  - X: P0 {s0['m']:+.3f} (t {s0['t']:+.2f}, n {s0['n']})・P1 {s1['m']:+.3f} (t {s1['t']:+.2f}, n {s1['n']})"
            f"・P2 {s2['m']:+.3f} (t {s2['t']:+.2f})・近年 {sr['m']:+.3f} (t {sr['t']:+.2f})")
        say(f"  - **二重差 P1−P0 {d10:+.3f} (Welch t {t10:+.2f})**・P2−P0 {d20:+.3f} (t {t20:+.2f})"
            f"〔c54 の隣接超過 DiD: AM +0.415 (t 2.72)／PM +0.655 (t 3.45)〕")
        if drop:
            if lab.startswith("AM"): tAM = t10; dAM = d10
            else: tPM = t10; dPM = d10
brk("BREAK-N1", "分-of-hour を揃えた二重差（AM 02:15・05:15 除く）の t < 2.24（c54 自身の H_REB Bonferroni(2) 閾値）",
    f"AM 二重差 {dAM:+.3f} (t {tAM:+.2f})・c54 の隣接超過 DiD は +0.415 (t 2.72)", tAM < 2.24)
brk("BREAK-N2", "AM と PM の両方で 分-of-hour 揃えの二重差 t < 2.24（＝「2 つの独立な時計」の根拠が同時に消える）",
    f"AM t {tAM:+.2f}・PM t {tPM:+.2f}", (tAM < 2.24) and (tPM < 2.24))

# rank 02:15 on the mo-matched DiD across all slots in UTC 00-08
say("\n## B-2 同じ推定子で UTC 00–08 の全 96 スロットを走らせた順位")
tt = np.full(96, np.nan); labs = []
for j, s_ in enumerate(range(0, 96)):
    X, _ = mo_matched(s_, drop0515=True)
    Xo = np.where(c54_ok(s_), X, np.nan)
    _, t_ = welch(Xo[P1], Xo[P0]); tt[j] = t_
    labs.append(f"{s_//12:02d}:{(s_%12)*5:02d}")
fin = np.isfinite(tt)
order = np.argsort(-np.where(fin, tt, -99))
say("- 二重差 t 上位 10: " + " ".join(f"{labs[i]}({tt[i]:+.2f})" + ("★" if i in (AMS, PMS) else "") for i in order[:10]))
say(f"- 02:15 順位 **{int((tt[fin] >= tt[AMS]).sum())}/{int(fin.sum())}**（t {tt[AMS]:+.2f}）"
    f"・06:15 順位 **{int((tt[fin] >= tt[PMS]).sum())}/{int(fin.sum())}**（t {tt[PMS]:+.2f}）"
    f"・t≥2.24 の割合 {float((tt[fin]>=2.24).mean())*100:.1f}%")

# ============ C. half-life of the move ==============================================================
say("\n## C 持続性（半減期）— 累積が +5 分値の何割まで戻るか")
for lab, s0 in [("AM 02:15", AMS), ("PM 06:15", PMS)]:
    for nm, msk in PERS:
        rows = np.flatnonzero(msk & (dwd <= 4))
        idx = rows * 288
        okall = np.ones(len(rows), bool)
        for k in range(12): okall &= PRESENT[idx + s0 + k]
        acc = np.zeros(len(rows)); series = []
        for k in range(12):
            acc = acc + G[idx + s0 + k]
            s = stat(acc[okall]); series.append((k, s["m"], s["t"]))
        first = series[0][1]
        at25 = series[4][1]; at55 = series[11][1]
        say(f"- {lab} {nm}: +5 分 {first:+.3f} → +25 分 {at25:+.3f} ({at25/first*100 if first!=0 else float('nan'):.0f}%)"
            f" → +60 分 {at55:+.3f} ({at55/first*100 if first!=0 else float('nan'):.0f}%)"
            f"・最大 {max(s[1] for s in series):+.3f} @ +{(max(series, key=lambda s: s[1])[0]+1)*5} 分")
        if lab.startswith("PM") and nm == "P1": pm_ratio = at25 / first
        if lab.startswith("AM") and nm == "P1": am_ratio = at25 / first
brk("BREAK-N3", "PM P1 の累積が +25 分で +5 分値の 50% 未満（＝一時的な流動性の窪みで価格発見ではない）",
    f"PM P1 +25 分 / +5 分 = {pm_ratio*100:.0f}%・AM P1 = {am_ratio*100:.0f}%", pm_ratio < 0.50)

say("\n## 走 3 のまとめ")
nb = sum(1 for _, v in VERD if v)
for tag, v in VERD: say(f"- {tag}: {'BROKEN' if v else 'not broken'}")
say(f"- **BROKEN {nb}/{len(VERD)}**・実行 {time.time()-T0:.1f} s・seed {SEED}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\nwrote {OUT}")
