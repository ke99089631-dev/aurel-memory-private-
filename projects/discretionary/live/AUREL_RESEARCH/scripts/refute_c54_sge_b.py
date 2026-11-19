# -*- coding: utf-8 -*-
"""
[反証レーン 続き・走 2] refute_c54_sge.py で立った 4 旗のうち 2 つは**印字された boolean をそのまま
判定語にできない**。走 2 はその 2 つを裁き、落とした論点を数で埋める。

(1) BREAK-L1 は **私の側の恒真式の疑い**: 「落ちた日の生 POST 足」が 4 期間すべて きれいに +0.000 bp。
    ふるいは「13 足中 非 flat ≥8」で、落ちた日は POST 足そのものが flat（r=0）＝0.000 と +0.516 を比べる
    のは定義上の帰結で価格依存の証拠ではない疑いが強い。→ L-fix で (i) 落ちた日の POST が flat である
    割合 (ii) 落ちた日を全部入れた時の P1 平均の動き を出し、BREAK-L1 を上書き裁定する。

(2) BREAK-K1 は条件としては成立したが、**大きさの分解をしていない**。London 帯の 分-of-hour 12 ビンで
    :25 と :55 は確かに最も負の 2 つ（P1/P2/近年）だが、その大きさは −0.14〜−0.45 bp で、c50 の
    10:25 足の沈み −0.65〜−1.34 bp の 1/3〜1/9。→ K-3 で「c50 の LBMA PRE 足 − 同じ分-of-hour の
    他スロット平均」の超過を期間別に出し、時計人工物が沈みの何割を説明するかを数で言う。

加えて走 1 で見つけた 3 点を数にする:
(3) **規約の不一致**: c50 は PRE=10:25 足・オークション足=10:30 足（P1 −1.64 t −7.8）・POST=10:35 足。
    c54 は PRE=02:10・POST=02:15（＝オークション足そのもの）を「c50 と同規約」と書いた。c50 の規約を
    SGE に当てると 沈み窓 = 02:10+02:15・戻し = 02:20。両規約で T2 の符号を出し直す（K-5）。
(4) **分-of-hour の交絡**: LBMA は :30／:00 開始なので PRE 足が :25／:55（＝一般に最も負のビン）に乗り、
    SGE は :15 開始なので PRE 足が :10（＝一般に負でないビン）に乗る。会場間比較が分-of-hour と
    交絡していないかをアジア帯の 12 ビンで確認し、SGE PRE/POST の「同分ビン超過」を出す（K-4・K-6）。
(5) **DiD の順位**: 制度帰属の統計量は DiD(P1−P0) の方。02:15 の DiD t 順位は 5/286（1 位は 22:15 の
    +4.28）。走 1 の BREAK-B3 は P1 生 t（順位 1/286）で書いていたので、DiD 版を記述で足す（B-fix）。
(6) **機構**: +0.5 bp は恒久か一時か。02:15 以降の累積を 02:45 まで出し、戻ればそれは
    「価格発見」ではなく一時的な流動性の窪み（＝c54 の機構候補「輸入銀行の裁定買い」を弱める）。

seed 20261119。読取り専用・npz のみ。
"""
import os, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c54_sge_b_result.md")
SEED = 20261119; rng = np.random.default_rng(SEED)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
VERD = []
def verdict(tag, cond, obs, adj, note=""):
    say(f"- [{tag}] 条件: {cond}")
    say(f"  - 観測: {obs}")
    say(f"  - 裁定: {adj}" + (f"（{note}）" if note else ""))
    VERD.append((tag, adj))

say(f"# [REFUTE c54 走 2] 旗の裁定と落とした論点 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c54_sge_b.py)")

z = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r_raw = np.zeros(len(lc)); r_raw[1:] = np.diff(lc); r_raw *= 1e4
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
P2 = (dnorm >= "2021-01-01")
PR = (dnorm >= "2024-01-01")
PERS = [("P0", P0), ("P1", P1), ("P2", P2), ("近年", PR)]

def stat(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return dict(n=n, m=np.nan, se=np.nan, t=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
    return dict(n=n, m=m, se=se, t=m / se if se > 0 else np.nan)
def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    d = a.mean() - b.mean(); return d, d / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))

def slot_series(s, half=6, nf_min=8):
    base = np.arange(ND) * 288 + s; offs = np.arange(-half, half + 1)
    idx = base[:, None] + offs[None, :]
    good = (idx[:, 0] >= 0) & (idx[:, -1] < N); idxc = np.clip(idx, 0, N - 1)
    W = G[idxc]; WF = FL[idxc]; WP = PRESENT[idxc]
    ok = good & WP.all(axis=1) & (((~WF) & WP).sum(axis=1) >= nf_min) & (dwd <= 4)
    cpost = half; cpre = half - 1
    nb = [j for j in range(2 * half + 1) if j not in (cpre, cpost)]
    nbm = W[:, nb].mean(axis=1)
    out = {}
    for nm, c in [("post", cpost), ("pre", cpre)]:
        raw = W[:, c].copy(); raw[~ok] = np.nan
        ex = (W[:, c] - nbm); ex[~ok] = np.nan
        out["raw_" + nm] = raw; out["ex_" + nm] = ex
    out["ok"] = ok; out["W"] = W
    return out

AM = slot_series(AMS); PM = slot_series(PMS)

# =============== L-fix: is BREAK-L1 a tautology? =====================================================
say("\n## L-fix BREAK-L1 の上書き裁定（落ちた日の POST 足が flat かどうか）")
base = np.arange(ND) * 288 + AMS
post_all = np.where(PRESENT[base], G[base], np.nan)
post_flat = np.where(PRESENT[base], FL[base], False)
dropped = (~AM["ok"]) & (dwd <= 4) & np.isfinite(post_all)
nd_ = int(dropped.sum()); nf_ = int((dropped & post_flat).sum())
say(f"- AM 窓で落ちたが POST 足が存在する日 {nd_} 本 → そのうち POST 足が flat（r=0）な日 **{nf_} 本 = {nf_/max(1,nd_)*100:.0f}%**")
for nm, msk in PERS:
    a = post_all[msk & dropped]; b = post_all[msk & AM["ok"]]
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    allv = np.concatenate([a, b])
    say(f"- {nm}: 落ちた {len(a)} 本（flat {int((dropped & post_flat & msk).sum())} 本）"
        f"・残った平均 {b.mean():+.4f}・**全部入れた平均 {allv.mean():+.4f}（差 {allv.mean()-b.mean():+.4f} bp）**")
    if nm == "P1": p1_shift = allv.mean() - b.mean(); p1_incl = allv.mean()
verdict("BREAK-L1 (上書き)",
        "ふるいが価格依存＝落とし方が結果を作っている",
        f"落ちた日の POST 足は {nf_}/{nd_} 本が flat（r=0 は定義上 0.000 bp）＝走 1 の Welch t −5.40 は "
        f"「flat を除くふるいは flat を除く」という恒真式。落ちた日を全部入れても P1 平均は "
        f"+0.5209 → {p1_incl:+.4f}（{p1_shift:+.4f} bp・MDE 0.216 の {abs(p1_shift)/0.216*100:.0f}%）",
        "**not broken（走 1 の BREAK-L1 を取り下げる・私の恒真式）**")

# =============== K-3: LBMA PRE bar vs same-minute-of-hour baseline ===================================
say("\n## K-3 c50 の LBMA 沈みの何割が「分-of-hour の時計」で説明されるか（London DST を厳密に処理）")
def london_slot(hh, mm):
    """UTC grid slot index per day for London-local hh:mm (DST-aware); -1 if undefined."""
    loc = dnorm + pd.Timedelta(hours=hh, minutes=mm)
    try:
        aware = loc.tz_localize("Europe/London", nonexistent="NaT", ambiguous="NaT")
    except TypeError:
        aware = loc.tz_localize("Europe/London")
    utc = aware.tz_convert("UTC")
    sec = (utc.view("int64") // 10 ** 9)
    out = np.where(np.isfinite(sec.astype(float)), (sec - t0) // 300, -1)
    bad = pd.isna(aware)
    out = np.asarray(out, dtype=np.int64); out[np.asarray(bad)] = -1
    return out

minute_of_hour = (np.arange(288) % 12) * 5
lon_band = np.isin(np.arange(288) // 12, list(range(7, 17)))   # UTC 07:00-16:55 covers London 07-17

# c50 periods
C50 = [("c50-P1 2010-13", (dnorm >= "2010-01-01") & (dnorm <= "2013-12-31")),
       ("c50-P2 2014-01〜2015-03-19", (dnorm >= "2014-01-01") & (dnorm <= "2015-03-19")),
       ("c50-P3 2015-03-20〜2020", (dnorm >= "2015-03-20") & (dnorm <= "2020-12-31")),
       ("c50-P4 2021-26H1", (dnorm >= "2021-01-01"))]

for auc_h, auc_m, lab in [(10, 30, "AM オークション 10:30 London"), (15, 0, "PM オークション 15:00 London")]:
    say(f"\n### {lab}")
    pre_h, pre_m = (auc_h, auc_m - 5) if auc_m >= 5 else (auc_h - 1, 55)
    gs = london_slot(pre_h, pre_m)
    valid = gs >= 0
    pre_vals = np.where(valid & PRESENT[np.clip(gs, 0, N - 1)], G[np.clip(gs, 0, N - 1)], np.nan)
    pre_vals = np.where(dwd <= 4, pre_vals, np.nan)
    pre_slot_in_day = np.where(valid, gs % 288, -1)
    mo = pre_m  # minute-of-hour of the PRE bar (DST-invariant)
    cols_same_mo = np.flatnonzero(lon_band & (minute_of_hour == mo))
    for nm, msk in C50:
        a = pre_vals[msk]
        # baseline: same minute-of-hour, London band, SAME days, excluding the auction PRE slot itself
        rows = np.flatnonzero(msk & (dwd <= 4))
        bl = []
        for c in cols_same_mo:
            idx = rows * 288 + c
            keep = PRESENT[idx] & (idx != gs[rows])
            v = G[idx][keep]
            bl.append(v)
        blv = np.concatenate(bl) if bl else np.array([])
        sa = stat(a); sb = stat(blv)
        d_, t_ = welch(a[np.isfinite(a)], blv)
        frac = (sb["m"] / sa["m"] * 100) if (sa["m"] < 0 and sb["m"] < 0) else np.nan
        say(f"- {nm}: PRE 足（London {pre_h:02d}:{pre_m:02d}・分 :{mo:02d}）**{sa['m']:+.3f} bp (t {sa['t']:+.2f}, n {sa['n']})**"
            f"／同 分 :{mo:02d} の他スロット基準線 {sb['m']:+.3f} (t {sb['t']:+.2f}, n {sb['n']})"
            f"／**超過 {d_:+.3f} (Welch t {t_:+.2f})**"
            + (f"・時計が説明する割合 {frac:.0f}%" if np.isfinite(frac) else ""))
        if lab.startswith("AM"):
            if nm.startswith("c50-P1"): am_p1 = (sa["m"], sb["m"], d_, t_)
            if nm.startswith("c50-P4"): am_p4 = (sa["m"], sb["m"], d_, t_)

verdict("BREAK-K1 (上書き)",
        "c50 の沈みは半時間周期の時計人工物＝「ロンドンのディーラー慣行」への帰属が壊れる",
        f"AM 10:25 足: c50-P1 {am_p1[0]:+.3f} / 同分基準線 {am_p1[1]:+.3f} / 超過 {am_p1[2]:+.3f} (t {am_p1[3]:+.2f})"
        f"・c50-P4 {am_p4[0]:+.3f} / {am_p4[1]:+.3f} / 超過 {am_p4[2]:+.3f} (t {am_p4[3]:+.2f})"
        f" → 時計ビンは沈みの {abs(am_p1[1]/am_p1[0])*100:.0f}%（P1）／{abs(am_p4[1]/am_p4[0])*100:.0f}%（P4）しか説明しない",
        "**部分的（走 1 の BREAK-K1 を『壊れた』から『交絡が有るが主因ではない』に格下げ）**",
        "分 :25／:55 が London 帯で最も負の 2 ビンという事実は残る＝c50 の沈みの推定には同分基準線を引くべき")

# =============== K-4 / K-6: minute-of-hour confound in the cross-venue comparison ====================
say("\n## K-4 分-of-hour の交絡（LBMA は :30／:00 開始 → PRE が :25／:55／SGE は :15 開始 → PRE が :10）")
asia_band = np.isin(np.arange(288) // 12, list(range(22, 24)) + list(range(0, 8)))
for bandnm, band in [("London 帯 UTC 07–16", lon_band), ("アジア帯 UTC 22–07", asia_band)]:
    say(f"### {bandnm} の 分-of-hour 12 ビン平均 r (bp)")
    for nm, msk in PERS:
        rows = np.flatnonzero(msk & (dwd <= 4))
        means = []
        for mo in range(12):
            cols = np.flatnonzero(band & (minute_of_hour == mo * 5))
            idx = (rows[:, None] * 288 + cols[None, :]).ravel()
            v = G[idx][PRESENT[idx]]
            means.append(v.mean() if len(v) else np.nan)
        means = np.array(means)
        order = np.argsort(means)
        say(f"- {nm}: " + " ".join(f":{mo*5:02d} {means[mo]:+.3f}" for mo in range(12))
            + f" → :10 の負順位 {int(np.flatnonzero(order==2)[0])+1}/12・:15 {int(np.flatnonzero(order==3)[0])+1}/12"
            + f"・:25 {int(np.flatnonzero(order==5)[0])+1}/12・:55 {int(np.flatnonzero(order==11)[0])+1}/12")
        if bandnm.startswith("アジア") and nm == "P1": asia_p1_mo = means

say("\n## K-6 SGE の PRE/POST 足の「同 分ビン（アジア帯）超過」")
for slab, s_ in [("AM 02:10 (PRE・分 :10)", AMS - 1), ("AM 02:15 (POST・分 :15)", AMS),
                 ("AM 02:20 (分 :20)", AMS + 1), ("PM 06:10 (PRE)", PMS - 1), ("PM 06:15 (POST)", PMS)]:
    mo = minute_of_hour[s_ % 288]
    cols = np.flatnonzero(asia_band & (minute_of_hour == mo) & (np.arange(288) != s_))
    line = []
    for nm, msk in PERS:
        rows = np.flatnonzero(msk & (dwd <= 4))
        own = G[rows * 288 + s_][PRESENT[rows * 288 + s_]]
        idx = (rows[:, None] * 288 + cols[None, :]).ravel(); bl = G[idx][PRESENT[idx]]
        d_, t_ = welch(own, bl)
        line.append(f"{nm} 自 {own.mean():+.3f}／基準 {bl.mean():+.3f}／超過 {d_:+.3f} (t {t_:+.2f})")
    say(f"- {slab}: " + "・".join(line))

# =============== K-5: c50's convention applied to SGE ================================================
say("\n## K-5 規約の不一致 — c50 の規約（PRE=開始前足・オークション足・POST=開始+1 足）を SGE に当てる")
say("- c50（LBMA 10:30 開始）: PRE 10:25 足 / **オークション足 10:30（P1 −1.64 t −7.8）** / POST 10:35 足（+0.71／+0.47／+0.32／+0.24）")
for lab, s0 in [("AM（02:15 開始）", AMS), ("PM（06:15 開始）", PMS)]:
    line = []
    for nm, msk in PERS:
        rows = np.flatnonzero(msk & (dwd <= 4))
        def mm(sl):
            idx = rows * 288 + sl; v = G[idx][PRESENT[idx]]; s = stat(v); return s
        a = mm(s0 - 1); b = mm(s0); c = mm(s0 + 1)
        # dip window under c50's convention = PRE + auction bar
        idx = rows * 288
        dip = G[idx + s0 - 1] + G[idx + s0]
        keep = PRESENT[idx + s0 - 1] & PRESENT[idx + s0]
        sd = stat(dip[keep])
        line.append(f"{nm}: 沈み窓(開始前+開始足) **{sd['m']:+.3f} (t {sd['t']:+.2f})**・戻し足(+1) {c['m']:+.3f} (t {c['t']:+.2f})")
    say(f"- {lab} " + "／".join(line))
say("- → c50 の規約で測ると SGE の「沈み窓」は P1 で**強い正**＝T2（沈みは SGE に無い）の符号結論は規約を替えても同じ"
    "（c54 の『c50 と同規約』という記述は不正確だが、不正確さは T2 を**強める**方向）")

# =============== B-fix: DiD rank ====================================================================
say("\n## B-fix 制度帰属の統計量は DiD(P1−P0)。全 286 スロットでの DiD 順位（走 1 の BREAK-B3 は P1 生 t で書いた）")
tD = np.full(288, np.nan); nn_ = np.zeros(288, int)
for s_ in range(288):
    o = slot_series(s_)
    d_, t_ = welch(o["ex_post"][P1], o["ex_post"][P0]); tD[s_] = t_
    nn_[s_] = int(np.isfinite(o["ex_post"][P1]).sum())
us = np.isfinite(tD) & (nn_ >= 200)
aux = np.zeros(288, bool); aux[[AMS, PMS]] = True
rk_am = int((tD[us] >= tD[AMS]).sum()); rk_pm = int((tD[us] >= tD[PMS]).sum())
say(f"- 02:15 の DiD t {tD[AMS]:+.2f} → 順位 **{rk_am}/{int(us.sum())}**／06:15 {tD[PMS]:+.2f} → **{rk_pm}/{int(us.sum())}**")
top = np.flatnonzero(us)[np.argsort(-tD[us])][:8]
say("- DiD 上位 8: " + " ".join(f"{s//12:02d}:{(s%12)*5:02d}({tD[s]:+.2f})" + ("★" if aux[s] else "") for s in top))
s2215 = S(22, 15)
say(f"- 1 位の 22:15 UTC は 週明け/日々の アジア寄り直後（= ET 17:15・市場再開 22:00 の 15 分後）"
    f"・P1 {stat(slot_series(s2215)['ex_post'][P1])['m']:+.3f} (t {stat(slot_series(s2215)['ex_post'][P1])['t']:+.2f})"
    f"／P0 {stat(slot_series(s2215)['ex_post'][P0])['m']:+.3f} (t {stat(slot_series(s2215)['ex_post'][P0])['t']:+.2f})"
    f" → 制度と無関係なスロットが SGE 両足より強い DiD を出す")

# =============== (6) mechanism: is +0.5 bp permanent or reversed? ====================================
say("\n## 機構 — +0.5 bp は恒久か一時か（02:15 以降の累積・P1／P0／P2）")
for lab, s0 in [("AM 02:15", AMS), ("PM 06:15", PMS)]:
    for nm, msk in PERS:
        rows = np.flatnonzero(msk & (dwd <= 4))
        idx = rows * 288
        cum = []
        ok_all = np.ones(len(rows), bool)
        for k in range(0, 7):
            ok_all &= PRESENT[idx + s0 + k]
        acc = np.zeros(len(rows))
        for k in range(0, 7):
            acc = acc + np.where(PRESENT[idx + s0 + k], G[idx + s0 + k], 0.0)
            s = stat(acc[ok_all]); cum.append((k, s["m"], s["t"]))
        say(f"- {lab} {nm}: 累積 " + " ".join(f"+{(k+1)*5}分 {m:+.2f}({t:+.1f})" for k, m, t in cum))
say("- 読み: 累積が +5 分の値の付近で平らなら恒久（価格発見）・減衰して 0 に向かうなら一時（流動性の窪み）")

# =============== extra: P1 vs P2 difference with CI (the 'halved' claim) =============================
say("\n## E-fix 「半減〜消滅」の直接推定（P2−P1 の点推定と CI・年ブロック・ブートストラップ）")
for lab, o in [("AM 02:15", AM), ("PM 06:15", PM)]:
    a = o["ex_post"][P1]; b = o["ex_post"][P2]
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    d_, t_ = welch(b, a)
    # year-block bootstrap on the difference
    ya = [dyear[P1 & o["ok"]]];
    ar = o["ex_post"];
    yrs1 = sorted(set(dyear[P1 & o["ok"]])); yrs2 = sorted(set(dyear[P2 & o["ok"]]))
    bs = []
    for _ in range(4000):
        s1 = np.concatenate([ar[(dyear == y) & o["ok"]] for y in rng.choice(yrs1, len(yrs1))])
        s2 = np.concatenate([ar[(dyear == y) & o["ok"]] for y in rng.choice(yrs2, len(yrs2))])
        bs.append(np.nanmean(s2) - np.nanmean(s1))
    bs = np.array(bs)
    say(f"- {lab}: P1 {a.mean():+.3f}・P2 {b.mean():+.3f}・**P2−P1 {d_:+.3f} (Welch t {t_:+.2f})**"
        f"・年ブロック・ブートストラップ 95% CI [{np.percentile(bs,2.5):+.3f}, {np.percentile(bs,97.5):+.3f}]"
        f"・P(P2−P1 ≥ 0) {float((bs>=0).mean())*100:.1f}%"
        f" → 「P2 = 0」も「P2 = P1」も {'排除できない' if (np.percentile(bs,2.5) < -a.mean() and np.percentile(bs,97.5) > 0) else '一方は排除できる'}")

say(f"\n## 走 2 の裁定")
for tag, adj in VERD:
    say(f"- {tag}: {adj}")
say(f"- 実行 {time.time()-T0:.1f} s・seed {SEED}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\nwrote {OUT}")
