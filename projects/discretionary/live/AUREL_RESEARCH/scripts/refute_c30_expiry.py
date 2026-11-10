# -*- coding: utf-8 -*-
"""
[REFUTE] 2026-11-10 反証レーン — 対象: cycle30 (12:55) の残存弱信号
  W1「満期日の LATE (11:30–13:30 ET) 実現分散は外のみ圧縮（平均比 0.62・z_pl −1.99／金曜除外 0.68・z −2.30、
      曜日一致プラセボ s=±5,±10 の平均 +0.02 vs 実測 −0.39）＝大分散日の不在型・発表暦との非重複で説明できる可能性」
  W2（事後・プラセボ列から）「s=+3（概ね月末最終営業日）の LATE 分散は 外 2.5 倍／近年 3.4 倍・在 1 倍」

規則（結果を見る前に書く・変えない）:
  R0 再現: 研究レーンの LATE log 平均比 在 −0.179／外 −0.479／近年 −0.489 を同じ定義で再現（|差| ≤ 0.02）。
  R1 満期日固有性: (a) 営業日シフト s=−1, 0, +1 の D(s) を印字（研究レーンは ±1 を除外していた）。
      (b) POST 窓（13:30–16:55 ET・満期後）と全日（ET 取引日）の分散比を同じ手順で印字。
      ピン留め機構なら圧縮は 13:30 で終わるはず。
  R2 曜日一致・近接週プラセボ（主）: 各満期日 e に対し e ± 7k 暦日（k=1..4・取引日・満期日±1 営業日を除く）から 1 日を無作為に
      選び同サイズの集合を作る（2000 回）。D = log(mean RV_E) − log(mean RV_C)（C = 窓内取引日 − 集合±1 営業日）。
      z_m = (D0 − mean)/sd・両側 p_m = P(|D_pl − mean| ≥ |D0 − mean|)。同じ帰無で mean-of-log 差 Dlog と AUC = P(RV_E > RV_C) も。
      **判定 W1**: survived = 外 p_m < 0.05 ∧ 外-ex-2026H1 p_m < 0.10 ∧ 外 POST の p_m ≥ 0.10（満期後は圧縮なし）。
                  broken = 外 p_m ≥ 0.05、または POST が D ≤ −0.25 かつ p_m < 0.10（機構がピン留めでない＝静かな日の選択）。
                  それ以外 inconclusive。
  R3 分布の形: 外で LATE RV 上位 5%（窓内取引日基準）の日を E・C 双方から除いた D（両側対称トリム）、E 内の上位 10% 日の割合、
      AUC。「大分散日の不在型」なら トリム後 |D| が半減し AUC ≈ 0.5。
  R4 年別・LOYO・ex-2026H1（外）: 年別 D と matched p、2026H1 を抜いた D と p。
  R5 発表日プロキシ（記述・研究レーンの仮説の検査）: 08:30／10:00／14:00 ET の 5 分 |対数リターン| が窓内上位 5% の日を
      「発表日」とし、E と C での割合、発表日を双方から除いた D を印字（LATE 窓外の足で定義＝循環なし）。
      13:00 ET（入札結果・LATE 内）は別途割合のみ。
  R6 family-wise: {PRE, LATE, POST} × {在, 外, 近年} = 9 セルの max|z_m| の帰無分布（同じ 2000 回のプラセボ）→ 観測 max|z_m| の p_fw。
  R7 W2 月末最終営業日集合 M（規則: 各月の最終営業日・2010-01〜2026-06）: LATE/PRE の D と matched p（在/外/近年）・年別・
      上位 3 日の寄与・ex-2026H1。選択の帰無: 研究レーンは 22 シフト×3 セルの最大を読んだ → 外の D(s) 列（s≠+3 の 21 本）
      の平均/sd で z を取り直し、matched 帰無での「22 本の max|D| ≥ 観測」の確率を近似（各シフト集合に matched 置換）。
      **判定 W2**: broken = 在 p_m ≥ 0.10 または 外-ex-2026H1 p_m ≥ 0.05。それ以外 inconclusive（事後の max なので survived は出さない）。
  D2: 窓別・16 年一括は使わない。bid のみ・Dukascopy。seed 20261110。
入力: data/macro/XAU_m5_close.npz のみ。scan 無し・M5 読込なし・MT5 無し・外部通信無し。
出力: data/refute_c30_expiry.md・data/refute_c30_expiry_run.log。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c30_expiry.md")
rng = np.random.default_rng(20261110); T0 = time.time(); L = []
NPL = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c30] 満期日 LATE 分散圧縮（W1）・月末分散（W2） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c30_expiry.py)")

# ---------------- 暦（c30 と同一の規則・コピー） ----------------
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d
HOL = set()
for y in range(2009, 2028):
    for h in [observed(dt.date(y, 1, 1), sat_to_fri=False), nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3),
              easter(y) - dt.timedelta(days=2), last_weekday(y, 5, 0), observed(dt.date(y, 7, 4)),
              nth_weekday(y, 9, 0, 1), nth_weekday(y, 11, 3, 4), observed(dt.date(y, 12, 25))] + \
             ([observed(dt.date(y, 6, 19))] if y >= 2022 else []):
        if h is not None: HOL.add(h)
d0 = dt.date(2009, 11, 1); d1 = dt.date(2026, 12, 31)
BDAYS = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]
BDAYS = [d for d in BDAYS if d.weekday() < 5 and d not in HOL]
BORD = np.array([d.toordinal() for d in BDAYS]); BIDX = {o: i for i, o in enumerate(BORD)}
def expiry_of_month(y, m):
    bm = [d for d in BDAYS if d.year == y and d.month == m]
    e = bm[-4]
    if e.weekday() == 4 or (e + dt.timedelta(days=1)) in HOL:
        e = BDAYS[BIDX[e.toordinal()] - 1]
    return e
EXP = []; MEND = []
for y in range(2010, 2027):
    for m in range(1, 13):
        if (y, m) > (2026, 6): break
        EXP.append(expiry_of_month(y, m)); MEND.append([d for d in BDAYS if d.year == y and d.month == m][-1])
EXP_ORD = np.array([e.toordinal() for e in EXP]); MEND_ORD = np.array([e.toordinal() for e in MEND])
say(f"- 満期日 {len(EXP)} 本・月末最終営業日 {len(MEND)} 本（2010-01〜2026-06）・暦は c30 と同一（コピー）")

# ---------------- データ → 日レベル ----------------
z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
flat = np.r_[True, P_ALL[1:] == P_ALL[:-1]]
et_all = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
etv = et_all.values; dayv = etv.astype("datetime64[D]")
ord_all = dayv.astype("int64") + dt.date(1970, 1, 1).toordinal()
tod_all = ((etv - dayv) / np.timedelta64(1, "m")).astype(int)
keep = ~flat
P = P_ALL[keep]; ordd = ord_all[keep]; tod = tod_all[keep]; logP = np.log(P)
say(f"- npz {len(TS)} 本・取引足 {len(P)} 本（flat {flat.mean()*100:.1f}%）")
WINS = {"PRE": (480, 810), "LATE": (690, 810), "POST": (810, 1016), "DAY": (0, 1440)}
def day_rv(lo, hi):
    m = (tod >= lo) & (tod < hi); idx = np.flatnonzero(m)
    same = (ordd[idx[1:]] == ordd[idx[:-1]]) & (idx[1:] == idx[:-1] + 1)
    r2 = (logP[idx[1:]] - logP[idx[:-1]]) ** 2
    d = ordd[idx[1:]][same]; r2 = r2[same]
    ud, inv = np.unique(d, return_inverse=True); return dict(zip(ud.tolist(), np.bincount(inv, weights=r2, minlength=len(ud)).tolist()))
RV = {k: day_rv(*v) for k, v in WINS.items()}
# 発表プロキシ: 指定 tod の足の |Δlog| (その足の close − 直前足 close)
def bar_absret(t_min):
    m = np.isin(tod, [t_min - 5, t_min]); idx = np.flatnonzero(m)
    out = {}
    for a, b in zip(idx[:-1], idx[1:]):
        if ordd[a] == ordd[b] and tod[a] == t_min - 5 and tod[b] == t_min: out[int(ordd[b])] = abs(logP[b] - logP[a])
    return out
AR = {t: bar_absret(t) for t in (510, 600, 780, 840)}
# 取引日 = 営業日（月〜金・非休日）かつ PRE 窓に足がある日
TD = np.array(sorted(o for o in BORD if o in RV["PRE"] and o in RV["LATE"]))
TD_YEAR = np.array([dt.date.fromordinal(int(o)).year for o in TD]); TD_WD = np.array([dt.date.fromordinal(int(o)).weekday() for o in TD])
TDSET = set(TD.tolist())
rv = {k: np.array([RV[k].get(int(o), np.nan) for o in TD]) for k in WINS}
ar = {t: np.array([AR[t].get(int(o), np.nan) for o in TD]) for t in AR}
say(f"- 取引日（PRE/LATE に足あり）{len(TD)} 日・2010〜2026H1")
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

def pm1(S):
    """集合 S（ordinal 配列）の ±1 営業日を含む集合"""
    i = np.array([BIDX.get(int(o), -1) for o in S]); i = i[i >= 0]
    return np.unique(np.concatenate([BORD[np.clip(i + k, 0, len(BORD) - 1)] for k in (-1, 0, 1)]))
def D_stats(S, wmask, key, excl_days=None):
    """D = log mean RV_E − log mean RV_C, Dlog = mean log 差, AUC, nE, nC"""
    inS = np.isin(TD, S) & wmask; inC = wmask & ~np.isin(TD, pm1(S))
    if excl_days is not None: inS &= ~excl_days; inC &= ~excl_days
    vE = rv[key][inS]; vC = rv[key][inC]; vE = vE[np.isfinite(vE) & (vE > 0)]; vC = vC[np.isfinite(vC) & (vC > 0)]
    if len(vE) < 3 or len(vC) < 3: return np.nan, np.nan, np.nan, len(vE), len(vC)
    D = math.log(vE.mean()) - math.log(vC.mean()); Dl = np.log(vE).mean() - np.log(vC).mean()
    # AUC = P(E > C)
    allv = np.concatenate([vE, vC]); rk = pd.Series(allv).rank().values; auc = (rk[:len(vE)].sum() - len(vE) * (len(vE) + 1) / 2) / (len(vE) * len(vC))
    return D, Dl, auc, len(vE), len(vC)
def matched_sets(S, n=NPL, weeks=(1, 2, 3, 4)):
    """各 e∈S について e±7k（取引日・満期日±1 営業日を除く）から 1 日。n 本の集合（list of arrays）"""
    bad = set(pm1(EXP_ORD).tolist())
    cands = []
    for o in S:
        c = [o + 7 * k * sg for k in weeks for sg in (-1, 1)]
        c = [x for x in c if x in TDSET and x not in bad]
        cands.append(np.array(c))
    out = []
    for _ in range(n):
        out.append(np.array([c[rng.integers(len(c))] for c in cands if len(c)]))
    return out
def matched_test(S, wmask, key, excl_days=None, sets=None):
    D0, Dl0, auc0, nE, nC = D_stats(S, wmask, key, excl_days)
    if sets is None: sets = matched_sets(S)
    Ds = []; Dls = []; aucs = []
    for Sp in sets:
        d, dl, a, _, _ = D_stats(Sp, wmask, key, excl_days); Ds.append(d); Dls.append(dl); aucs.append(a)
    Ds = np.array(Ds); Dls = np.array(Dls); aucs = np.array(aucs)
    def zp(x0, xs):
        xs = xs[np.isfinite(xs)]
        if len(xs) < 10 or not np.isfinite(x0): return np.nan, np.nan, np.nan, np.nan
        mu, sd = xs.mean(), xs.std(ddof=1); zz = (x0 - mu) / sd if sd > 0 else np.nan
        p = (np.abs(xs - mu) >= abs(x0 - mu)).mean(); return zz, p, mu, sd
    return dict(D=D0, Dl=Dl0, auc=auc0, nE=nE, nC=nC, zD=zp(D0, Ds), zDl=zp(Dl0, Dls), zA=zp(auc0, aucs), Ds=Ds)
def fmt(r, label):
    zD, pD, mu, sd = r["zD"]; zL, pL, _, _ = r["zDl"]; zA, pA, _, _ = r["zA"]
    return (f"{label}: D {r['D']:+.3f}（比 {math.exp(r['D']) if np.isfinite(r['D']) else np.nan:.3f}・プラセボ平均 {mu:+.3f} sd {sd:.3f}）z_m {zD:+.2f} p_m {pD:.3f}"
            f"／Dlog {r['Dl']:+.3f} z {zL:+.2f} p {pL:.3f}／AUC {r['auc']:.3f} z {zA:+.2f} p {pA:.3f}（E {r['nE']}／C {r['nC']} 日）")

# ---------------- R0 再現 ----------------
say("\n## R0 再現（研究レーン定義: C = 取引日 − 満期日±1 営業日・log 平均比）")
REP = {"在 2010-20": -0.1787, "外 2021-26H1": -0.4789, "近年 2024-26H1": -0.4885}
for wn, (lo, hi) in WIN.items():
    wm = (TD_YEAR >= lo) & (TD_YEAR <= hi)
    D, Dl, auc, nE, nC = D_stats(EXP_ORD, wm, "LATE")
    say(f"- {wn} LATE: D {D:+.4f}（研究レーン {REP[wn]:+.4f}・差 {D-REP[wn]:+.4f}）・平均比 {math.exp(D):.3f}・E {nE}／C {nC} 日")
    assert abs(D - REP[wn]) <= 0.02, "再現失敗"

# ---------------- R1 満期日固有性 ----------------
say("\n## R1 満期日固有性: s=−1/0/+1（営業日シフト）と窓別（PRE/LATE/POST/DAY）")
def shift_set(s):
    i = np.array([BIDX[int(o)] for o in EXP_ORD]) + s; ok = (i >= 0) & (i < len(BORD)); return BORD[i[ok]]
for wn, (lo, hi) in WIN.items():
    wm = (TD_YEAR >= lo) & (TD_YEAR <= hi)
    line = f"- {wn}:"
    for key in ("PRE", "LATE", "POST", "DAY"):
        ds = {s: D_stats(shift_set(s), wm, key)[0] for s in (-2, -1, 0, 1, 2)}
        line += f" {key} D(−2..+2) " + "/".join(f"{ds[s]:+.2f}" for s in (-2, -1, 0, 1, 2)) + ";"
    say(line)

# ---------------- R2 曜日一致・近接週プラセボ（主）＋ R6 family ----------------
say(f"\n## R2 曜日一致・近接週（±1..4 週）プラセボ {NPL} 回 — 主判定")
SETS = matched_sets(EXP_ORD)
say(f"- プラセボ集合サイズ {len(SETS[0])}（満期日 {len(EXP_ORD)}）・各 e の候補数 中央値 {np.median([len([x for k in (1,2,3,4) for sg in (-1,1) for x in [o+7*k*sg] if x in TDSET and x not in set(pm1(EXP_ORD).tolist())]) for o in EXP_ORD]):.0f}")
R2 = {}; ZM = {}
for wn, (lo, hi) in WIN.items():
    wm = (TD_YEAR >= lo) & (TD_YEAR <= hi)
    for key in ("PRE", "LATE", "POST"):
        r = matched_test(EXP_ORD, wm, key, sets=SETS); R2[(wn, key)] = r; ZM[(wn, key)] = r
        say("- " + fmt(r, f"{wn} {key}"))
# family-wise: 9 セルの max|z| 帰無 = 各プラセボ集合 j について 9 セルの z_j を同じ (mu, sd) で標準化
say("\n## R6 family-wise（9 セル = 3 窓 × PRE/LATE/POST・同一プラセボ集合で max|z|）")
Zmat = []
for k, r in R2.items():
    Ds = r["Ds"]; mu, sd = np.nanmean(Ds), np.nanstd(Ds, ddof=1); Zmat.append((Ds - mu) / sd)
Zmat = np.array(Zmat); maxz_null = np.nanmax(np.abs(Zmat), axis=0)
obs = {k: r["zD"][0] for k, r in R2.items()}; kmax = max(obs, key=lambda k: abs(obs[k]))
p_fw = (maxz_null >= abs(obs[kmax])).mean()
say(f"- 観測 max|z_m| {abs(obs[kmax]):.2f}（{kmax[0]} {kmax[1]}）・帰無 max|z| 中央値 {np.median(maxz_null):.2f}・95% 点 {np.percentile(maxz_null, 95):.2f} → **p_fw(9) {p_fw:.3f}**")
k_late = ("外 2021-26H1", "LATE"); p_fw_late = (maxz_null >= abs(obs[k_late])).mean()
say(f"- 外 LATE の z_m {obs[k_late]:+.2f} を 9 セル family で見た p_fw {p_fw_late:.3f}")

# ---------------- R3 分布の形（外） ----------------
say("\n## R3 分布の形（外・LATE）: 上位 5% 対称トリム・上位 10% 日の割合・AUC")
for wn in ("外 2021-26H1", "在 2010-20"):
    lo, hi = WIN[wn]; wm = (TD_YEAR >= lo) & (TD_YEAR <= hi)
    v = rv["LATE"]; thr95 = np.nanpercentile(v[wm], 95); thr90 = np.nanpercentile(v[wm], 90)
    big = wm & (v >= thr95)
    r_tr = matched_test(EXP_ORD, wm, "LATE", excl_days=big, sets=SETS)
    inE = np.isin(TD, EXP_ORD) & wm; inC = wm & ~np.isin(TD, pm1(EXP_ORD))
    say(f"- {wn}: 上位 10% 日の割合 E {np.mean(v[inE] >= thr90)*100:.1f}% vs C {np.mean(v[inC] >= thr90)*100:.1f}%（期待 10%）・上位 5% E {np.mean(v[inE] >= thr95)*100:.1f}% vs C {np.mean(v[inC] >= thr95)*100:.1f}%"
        f"・中央値比 {np.nanmedian(v[inE])/np.nanmedian(v[inC]):.3f}")
    say("  - " + fmt(r_tr, f"上位 5% 日を E・C から除外"))

# ---------------- R4 年別・LOYO・ex-2026H1（外） ----------------
say("\n## R4 外の年別・ex-2026H1・LOYO（LATE・matched p）")
wm_out = (TD_YEAR >= 2021) & (TD_YEAR <= 2026)
for y in range(2021, 2027):
    wm = TD_YEAR == y; r = matched_test(EXP_ORD, wm, "LATE", sets=SETS)
    say("- " + fmt(r, f"{y}"))
r_ex26 = matched_test(EXP_ORD, (TD_YEAR >= 2021) & (TD_YEAR <= 2025), "LATE", sets=SETS); say("- **" + fmt(r_ex26, "外 ex-2026H1 (2021-25)") + "**")
r_ex26_post = matched_test(EXP_ORD, (TD_YEAR >= 2021) & (TD_YEAR <= 2025), "POST", sets=SETS); say("- " + fmt(r_ex26_post, "外 ex-2026H1 POST"))
for y in range(2021, 2027):
    wm = wm_out & (TD_YEAR != y); r = matched_test(EXP_ORD, wm, "LATE", sets=SETS)
    say(f"- LOYO −{y}: D {r['D']:+.3f} z_m {r['zD'][0]:+.2f} p_m {r['zD'][1]:.3f}")
# 上位寄与: E の LATE RV 上位 3 日
inE = np.isin(TD, EXP_ORD) & wm_out; vE = rv["LATE"][inE]; oE = TD[inE]; srt = np.argsort(-vE)
say("- 外 満期日 LATE RV 上位 5 日: " + " ".join(f"{dt.date.fromordinal(int(oE[i])).isoformat()}:{vE[i]*1e8:.0f}" for i in srt[:5]) + f"（単位 1e-8・E 平均 {vE.mean()*1e8:.0f}・C 平均 {rv['LATE'][wm_out & ~np.isin(TD, pm1(EXP_ORD))].mean()*1e8:.0f}）")

# ---------------- R5 発表日プロキシ（記述） ----------------
say("\n## R5 発表日プロキシ（08:30／10:00／14:00 ET の 5 分 |Δlog| 窓内上位 5%・LATE 窓外で定義）")
for wn, (lo, hi) in WIN.items():
    wm = (TD_YEAR >= lo) & (TD_YEAR <= hi)
    flags = np.zeros(len(TD), bool); parts = []
    for t, nm in ((510, "08:30"), (600, "10:00"), (840, "14:00"), (780, "13:00")):
        a = ar[t]; thr = np.nanpercentile(a[wm], 95); f = wm & (a >= thr)
        inE = np.isin(TD, EXP_ORD) & wm; inC = wm & ~np.isin(TD, pm1(EXP_ORD))
        parts.append(f"{nm} E {np.mean(f[inE])*100:.1f}% vs C {np.mean(f[inC])*100:.1f}%")
        if t != 780: flags |= f
    inE = np.isin(TD, EXP_ORD) & wm; inC = wm & ~np.isin(TD, pm1(EXP_ORD))
    say(f"- {wn}: 発表プロキシ日の割合 " + "・".join(parts) + f"；いずれか（13:00 除く）E {np.mean(flags[inE])*100:.1f}% vs C {np.mean(flags[inC])*100:.1f}%")
    r_ex = matched_test(EXP_ORD, wm, "LATE", excl_days=flags, sets=SETS)
    say("  - " + fmt(r_ex, "発表プロキシ日を E・C から除外 LATE"))
    r_exp = matched_test(EXP_ORD, wm, "PRE", excl_days=flags, sets=SETS)
    say("  - " + fmt(r_exp, "同 PRE"))

# ---------------- R7 W2 月末最終営業日 ----------------
say("\n## R7 W2 月末最終営業日 M（LATE／PRE・matched p）")
SETS_M = matched_sets(MEND_ORD)
R7 = {}
for wn, (lo, hi) in WIN.items():
    wm = (TD_YEAR >= lo) & (TD_YEAR <= hi)
    for key in ("LATE", "PRE", "POST"):
        r = matched_test(MEND_ORD, wm, key, sets=SETS_M); R7[(wn, key)] = r; say("- " + fmt(r, f"{wn} {key}"))
r_m_ex26 = matched_test(MEND_ORD, (TD_YEAR >= 2021) & (TD_YEAR <= 2025), "LATE", sets=SETS_M); say("- **" + fmt(r_m_ex26, "外 ex-2026H1 LATE") + "**")
for y in range(2021, 2027):
    r = matched_test(MEND_ORD, TD_YEAR == y, "LATE", sets=SETS_M); say(f"- {y} LATE: D {r['D']:+.3f} z_m {r['zD'][0]:+.2f} p_m {r['zD'][1]:.3f}（E {r['nE']}）")
inM = np.isin(TD, MEND_ORD) & wm_out; vM = rv["LATE"][inM]; oM = TD[inM]; srt = np.argsort(-vM)
say("- 外 月末 LATE RV 上位 5 日: " + " ".join(f"{dt.date.fromordinal(int(oM[i])).isoformat()}:{vM[i]*1e8:.0f}" for i in srt[:5]) + f"（E 平均 {vM.mean()*1e8:.0f}・上位 3 日の Σ 寄与 {vM[srt[:3]].sum()/vM.sum()*100:.0f}%）")
# 上位 3 日除外
big3 = np.zeros(len(TD), bool); big3[np.flatnonzero(inM)[srt[:3]]] = True
r_m_tr = matched_test(MEND_ORD, wm_out, "LATE", excl_days=big3, sets=SETS_M); say("- " + fmt(r_m_tr, "外 LATE 上位 3 日除外"))
# 選択の帰無: s=+3 と月末集合の一致度・22 シフトの max
s3 = shift_set(3); say(f"- s=+3 集合と月末集合 M の一致 {len(set(s3.tolist()) & set(MEND_ORD.tolist()))}/{len(MEND_ORD)} 日")
Dsh = {s: D_stats(shift_set(s), wm_out, "LATE")[0] for s in range(-12, 13) if abs(s) >= 2}
oth = np.array([v for s, v in Dsh.items() if s != 3]); say(f"- 外 LATE D(s) s≠+3 の 21 本: 平均 {oth.mean():+.3f} sd {oth.std(ddof=1):.3f} → D(+3) {Dsh[3]:+.3f} の z {(Dsh[3]-oth.mean())/oth.std(ddof=1):+.2f}")
# 22 本 max の帰無: 各シフト集合に matched 置換（200 回・計算量）
nmx = 200; mx = []
sets_s = {s: matched_sets(shift_set(s), n=nmx) for s in Dsh}
for j in range(nmx):
    mx.append(max(abs(D_stats(sets_s[s][j], wm_out, "LATE")[0]) for s in Dsh))
mx = np.array(mx); say(f"- 22 シフト集合それぞれに matched 置換（{nmx} 回）: max|D| 帰無 中央値 {np.median(mx):.3f}・95% 点 {np.percentile(mx, 95):.3f} → 観測 |D(+3)| {abs(Dsh[3]):.3f} の p_fw {(mx >= abs(Dsh[3])).mean():.3f}")

# ---------------- 判定 ----------------
say("\n## 判定（docstring の規則）")
pL = R2[("外 2021-26H1", "LATE")]["zD"][1]; pX = r_ex26["zD"][1]; rP = R2[("外 2021-26H1", "POST")]; pP = rP["zD"][1]
if pL >= 0.05: v1 = "broken（外 p_m ≥ 0.05）"
elif rP["D"] <= -0.25 and pP < 0.10: v1 = "broken（POST も圧縮＝機構がピン留めでない）"
elif pL < 0.05 and pX < 0.10 and pP >= 0.10: v1 = "survived"
else: v1 = "inconclusive"
say(f"- **W1 {v1}**: 外 LATE p_m {pL:.3f}・ex-2026H1 p_m {pX:.3f}・POST D {rP['D']:+.3f} p_m {pP:.3f}")
pMin = R7[("在 2010-20", "LATE")]["zD"][1]; pMx = r_m_ex26["zD"][1]
v2 = "broken" if (pMin >= 0.10 or pMx >= 0.05) else "inconclusive"
say(f"- **W2 {v2}**: 在 LATE p_m {pMin:.3f}（D {R7[('在 2010-20','LATE')]['D']:+.3f}）・外 ex-2026H1 p_m {pMx:.3f}（D {r_m_ex26['D']:+.3f}）")
say(f"\n実行時間 {time.time()-T0:.1f} s")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
print("written", OUT)
