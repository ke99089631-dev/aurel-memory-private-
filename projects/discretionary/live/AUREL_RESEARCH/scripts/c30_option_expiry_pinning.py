# -*- coding: utf-8 -*-
"""
[cycle30 研究レーン] 2026-11-10 — 【探索・制度カレンダー／ヘッジ需要（収益機会の源泉マップ: ディーラーのガンマ・ヘッジ）】
COMEX 金オプション（OG・毎月）の最終取引日（12:30 CT = 13:30 ET）に、スポット金 M5 は「ピン留め」（キリ番＝行使価格の集積
への滞留・分散の圧縮）を示すか。機構: 満期直前、ロング・ガンマのディーラーは ATM 行使価格の周りで逆張りヘッジ（価格が行使価格に
引き寄せられる＝pinning・Ni–Pearson–Poteshman 2005 は米株で確認）。ショート・ガンマなら逆（行使価格から弾かれる）。
cycle26/反証 02:30 で「金の 5 分足は 00/50 を速く通過する（占有 ρ_O ≈0.77）」が確定しているので、満期日に限って ρ_O が
上がる（1 に近づく／超える）なら「ヘッジ需要が制度カレンダーで価格形成を変える」証拠になる。入口フィルタではない（市場構造の記述）。

事前固定（検証前に書く・結果を見てから変えない）:
  データ: data/macro/XAU_m5_close.npz（bid・完全格子）→ flat 足除外の取引足。ET 現地時刻（America/New_York・DST 追随）。
        窓 在 2010-20／外 2021-26H1／近年 2024-26H1（ET 年・D2）。
  暦（制度側の規則で導出・外部データ不要）: 満期日 = 「当月の最終営業日から数えて 4 番目の営業日（4th last business day）。
        その日が金曜日、または翌暦日が取引所休日なら、その前営業日」。営業日 = 月〜金 − CME 休日（元日[日→月]・MLK・大統領の日・
        聖金曜日・戦没者追悼・ジューンティーンス(2022+)・独立記念日・労働者の日・感謝祭・クリスマス[土→金/日→月]）。
        対象月 2010-01〜2026-06（198 か月）。暦の検証 = (a) 導出した休日の ET 09–16 時 flat 比率が通常日より高い（祝日暦の陽性対照）、
        (b) 2023-12〜2025-05 の満期日を AI の記憶の照合（外部確認なし・一致数を印字するだけ・判定には使わない）。
  窓（ET・足の時刻）: PRE = 08:00–13:30（最終取引までの米国セッション）・LATE = 11:30–13:30・POST = 13:30–16:55。
  対照 C = 同じ窓の全取引日（月〜金・非休日）から 満期日 ±1 営業日を除いたもの。
  プラセボ日集合 = 同じ規則の満期日を s 営業日ずらした集合（s ∈ {−12..−2, +2..+12}・22 本）。各 s で同じ統計 D(s)=E(s)−C(s)
        を取り、z_pl = (D(0) − mean_s D(s)) / sd_s D(s)。MDE = 2·sd_s（プラセボ帰無の se・反証 02:30 の教訓 (a): 日ブロックでなく
        オフセット間分布で se を取る）。
  H_PIN（主）: G=50・δ=1 USD の占有比 ρ_O = f_0 / mean_{θ∈{5..45}} f_θ を PRE 窓の E と C で取り、D_ρ = ρ_E − ρ_C。
        ピン留め → D_ρ > 0。PASS = 在 D_ρ>0 ∧ z_pl ≥ 2 ∧ 外 D_ρ>0 ∧ z_pl ≥ 1.5。副: G=100・LATE 窓・細格子 θ=0..49 での
        f_0 の順位（1=最小・C では順位 1 が既知）。
  H_ADJ（副・Bonferroni(2) で z≥2.24）: 行使価格は先物（当限）の価格なので、スポットの水準は K − basis にずれる
        （basis = S·r·τ・r = FRED DFF 実効 FF・τ = 満期日→受渡初日: 1/3/5/7/9/11 月満期（偶数限月の通常オプション）は翌月初営業日、
        12/2/4/6/8/10 月満期（シリアル）は翌々月初営業日）。P + basis_d で格子を取り直し、ρ_adj(E) をプラセボ集合（同じ手順）
        と比べる。外（金利 4〜5%・basis 10〜25 USD）で意味を持つ。在（ZIRP）は basis ≈0 で主と同じ。
  H_VAR（副・両側・記述）: LATE 窓の実現分散（5 分対数リターンの二乗和・日ごと）の E/C 比（平均比・中央値比）。ピン留め → <1、
        ショート・ガンマ → >1。PRE 窓の分散比も併記。
  H_DIR（記述）: PRE 窓（08:00→13:30）と POST 窓（13:30→16:55）の平均対数リターン（bp）E vs C・日レベル Welch t・プラセボ z。
  本番への接続（記述）: scan 19404 本のうち満期日 PRE 窓に建玉した本の n・平均 R*（SL/TP は R+ft・TIME は R−ft）vs 対照日の
        同時刻帯の本・MDE。満期時刻 13:30 ET を生きて跨ぐ本の n・平均 R*。
  陽性対照（注入）: 在の満期日 PRE 窓で |P−L50|≤3 USD の足を L+(P−L)·0.5 に寄せて（半分ピン留め）D_ρ と z_pl を再計算。
  seed 20261110。事前の最重大反証: (i) 暦の規則（4th last・金曜/休日前倒し）の誤り＝満期日が 1〜2 営業日ずれると効果は消える
        （プラセボ s=±1 は除外しているので、s=±2 の D も印字して確認）；(ii) CFD スポット bid vs 先物: ピン留めは先物価格で起き、
        スポットは basis 分ずれる（H_ADJ で対処・在は ZIRP で影響小）；(iii) 週次オプション（金曜満期・2020 年代から月/水も）の
        存在で月次満期の特異性が薄まる；(iv) 満期日は月末 4 営業日前＝月末フローと混じる（プラセボ s は同じ月内の位置を変えるので
        月末効果は部分的に帰無に含まれる）；(v) 占有の日数 在 ≈132 日／外 ≈66／近年 ≈30＝近年は記述のみ。
  D2: 窓別（16 年一括は使わない）。昇格候補・入口/出口規則の提案ではない。
入力: data/macro/XAU_m5_close.npz・data/macro/DFF.csv（FRED・本サイクルで取得 0.2 s）・data/refute_c4_scan_paths_2010_2026.json。
      scan 無し・M5 読込なし・MT5 無し。
出力: data/c30_option_expiry_pinning_result.md・data/c30_run.log。
"""
import os, sys, json, math, time, datetime as dt
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c30_option_expiry_pinning_result.md")
rng = np.random.default_rng(20261110); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle30] COMEX 金オプション満期日のピン留め — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c30_option_expiry_pinning.py)")

# ---------------- 暦（CME 休日・営業日・満期） ----------------
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
EXP = []  # (date, 受渡初日)
for y in range(2010, 2027):
    for m in range(1, 13):
        if (y, m) > (2026, 6): break
        e = expiry_of_month(y, m)
        dm = m + 1 if m in (1, 3, 5, 7, 9, 11) else m + 2  # 受渡月
        dy = y + (dm - 1) // 12; dm = (dm - 1) % 12 + 1
        fd = [d for d in BDAYS if d.year == dy and d.month == dm][0]
        EXP.append((e, fd))
EXP_ORD = np.array([e.toordinal() for e, _ in EXP]); TAU = np.array([(fd - e).days for e, fd in EXP], float)
say(f"- 満期日 {len(EXP)} 本（2010-01〜2026-06）・τ（満期→受渡初日・日）中央値 通常月 {np.median(TAU[[e.month in (1,3,5,7,9,11) for e,_ in EXP]]):.0f}／"
    f"シリアル月 {np.median(TAU[[e.month in (12,2,4,6,8,10) for e,_ in EXP]]):.0f}・金曜/休日前倒し {sum(1 for (e,_) in EXP if [d for d in BDAYS if d.year==e.year and d.month==e.month][-4]!=e)} 本")
MEM = {dt.date(2023,12,26), dt.date(2024,3,25), dt.date(2024,7,25), dt.date(2024,11,25), dt.date(2024,12,26), dt.date(2025,1,28),
       dt.date(2025,2,25), dt.date(2025,3,26), dt.date(2025,4,24), dt.date(2025,5,27)}
der = {e for e, _ in EXP if dt.date(2023, 12, 1) <= e <= dt.date(2025, 5, 31)}
say("- 導出 2023-12〜2025-05: " + " ".join(sorted(e.isoformat() for e in der)))
say(f"- AI 記憶との照合（外部確認なし・判定不使用）: 一致 {len(MEM & der)}/{len(MEM)}・不一致 {sorted((MEM ^ der))}")
say("- 休日 2024-25: " + " ".join(sorted(h.isoformat() for h in HOL if 2024 <= h.year <= 2025)))

# ---------------- データ ----------------
z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
say(f"- npz {len(TS)} 本 {dt.datetime.fromtimestamp(int(TS[0]), dt.timezone.utc)} 〜 {dt.datetime.fromtimestamp(int(TS[-1]), dt.timezone.utc)} UTC・close {P_ALL.min():.1f}〜{P_ALL.max():.1f}（⑩）")
flat = np.r_[True, P_ALL[1:] == P_ALL[:-1]]
et_all = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
etv = et_all.values; dayv = etv.astype("datetime64[D]")
ord_all = dayv.astype("int64") + dt.date(1970, 1, 1).toordinal()
tod_all = ((etv - dayv) / np.timedelta64(1, "m")).astype(int)
year_all = et_all.year.values
wd_all = (dayv.astype("int64") + 3) % 7  # 0=月
hol_ord = np.array(sorted(h.toordinal() for h in HOL)); is_hol_all = np.isin(ord_all, hol_ord)
# 祝日暦の陽性対照: ET 09–16 時の flat 比率
m_mid = (tod_all >= 540) & (tod_all < 960) & (wd_all < 5) & (year_all >= 2013)
say(f"- 祝日暦の陽性対照（flat 比率 ET 09–16 時・月〜金・2013+）: 導出休日 {flat[m_mid & is_hol_all].mean()*100:.1f}% vs 通常日 {flat[m_mid & ~is_hol_all].mean()*100:.1f}%"
    f"（休日 {len(np.unique(ord_all[m_mid & is_hol_all]))} 日）；休日別: " +
    " ".join(f"{dt.date.fromordinal(int(o)).isoformat()}:{flat[m_mid & (ord_all==o)].mean()*100:.0f}%" for o in np.unique(ord_all[m_mid & is_hol_all]) if dt.date.fromordinal(int(o)).year in (2024, 2025)))
keep = ~flat
P = P_ALL[keep]; ordd = ord_all[keep]; tod = tod_all[keep]; year = year_all[keep]; wd = wd_all[keep]; is_hol = is_hol_all[keep]
logP = np.log(P)
say(f"- 取引足 {len(P)} 本（flat {flat.mean()*100:.1f}%・⑪）")
trade_day = (wd < 5) & ~is_hol
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
PRE = (tod >= 480) & (tod < 810); LATE = (tod >= 690) & (tod < 810); POST = (tod >= 810) & (tod <= 1015)
# DFF（basis 用）
dff = pd.read_csv(os.path.join(DATA, "macro", "DFF.csv")); dff.columns = ["date", "v"]; dff["v"] = pd.to_numeric(dff["v"], errors="coerce")
dff["ord"] = pd.to_datetime(dff["date"]).map(lambda x: x.toordinal()); dff = dff.dropna().sort_values("ord")
DFF_ORD = dff["ord"].values; DFF_V = dff["v"].values
def dff_at(o): i = np.searchsorted(DFF_ORD, o, side="right") - 1; return DFF_V[max(i, 0)]
say(f"- DFF {dff['date'].iloc[0]}〜{dff['date'].iloc[-1]}（{len(dff)} 行）")

# ---------------- 統計 ----------------
THETA9 = list(range(5, 50, 5)); FINE = list(range(0, 50))
def rho_of(Pm, G, deltas=1.0, thetas=None, adj=None):
    """占有比 ρ_O = f_0 / mean f_θ（θ 9 本）と細格子順位。adj = 足ごとの basis 加算。"""
    if len(Pm) == 0: return np.nan, np.nan, np.nan
    Q = Pm + (adj if adj is not None else 0.0)
    r = np.mod(Q, G)
    def f(th): d = np.abs(r - th); d = np.minimum(d, G - d); return (d <= deltas).mean()
    f0 = f(0); fpl = np.mean([f(th) for th in (THETA9 if G == 50 else list(range(10, 100, 10)))])
    rank = 1 + sum(f(th) < f0 for th in (FINE if G == 50 else list(range(1, 100)))[1:])
    return f0 / fpl, f0, rank
def day_rv(mask_bars):
    """mask 内の足で同日連続の 5 分対数リターン二乗和を日ごとに。"""
    idx = np.flatnonzero(mask_bars)
    if len(idx) < 2: return np.array([]), np.array([])
    same = (ordd[idx[1:]] == ordd[idx[:-1]]) & (idx[1:] == idx[:-1] + 1)
    r2 = (logP[idx[1:]] - logP[idx[:-1]]) ** 2
    d = ordd[idx[1:]][same]; r2 = r2[same]
    ud, inv = np.unique(d, return_inverse=True); return ud, np.bincount(inv, weights=r2, minlength=len(ud))
def day_ret(mask_bars):
    """mask 内の足で日ごとの (最後 − 最初) 対数リターン（bp）。"""
    idx = np.flatnonzero(mask_bars)
    if len(idx) == 0: return np.array([]), np.array([])
    d = ordd[idx]; ud, first = np.unique(d, return_index=True); last = np.r_[first[1:], len(idx)] - 1
    return ud, (logP[idx[last]] - logP[idx[first]]) * 1e4
def shift_set(s):
    i = np.array([BIDX[o] for o in EXP_ORD]) + s; ok = (i >= 0) & (i < len(BORD)); return BORD[i[ok]], TAU[ok]
_u, _fi = np.unique(ordd[PRE], return_index=True); DAY_FIRST_P = dict(zip(_u.tolist(), P[np.flatnonzero(PRE)[_fi]].tolist()))
def stats(S, wmask, adj_map=None, Pov=None):
    """S = 日集合（ordinal）。E = S の足・C = 取引日から S±1 営業日を除外。"""
    Pm = P if Pov is None else Pov
    i = np.array([BIDX.get(o, -1) for o in S]); i = i[i >= 0]
    Spm = np.unique(np.concatenate([BORD[np.clip(i + k, 0, len(BORD) - 1)] for k in (-1, 0, 1)]))
    inE = np.isin(ordd, S) & wmask; inC = trade_day & ~np.isin(ordd, Spm) & wmask
    out = {}
    out["nE"] = len(np.unique(ordd[inE & PRE])); out["nC"] = len(np.unique(ordd[inC & PRE]))
    for nm, W in (("PRE", PRE), ("LATE", LATE)):
        rE, f0E, rkE = rho_of(Pm[inE & W], 50); rC, f0C, rkC = rho_of(Pm[inC & W], 50)
        out[f"rho50_{nm}"] = (rE, rC, rE - rC, rkE, rkC, f0E, f0C)
        rE1, _, rkE1 = rho_of(Pm[inE & W], 100); rC1, _, rkC1 = rho_of(Pm[inC & W], 100)
        out[f"rho100_{nm}"] = (rE1, rC1, rE1 - rC1, rkE1, rkC1)
    if adj_map is not None:
        adj = np.array([adj_map.get(o, 0.0) for o in ordd[inE & PRE]])
        rA, _, rkA = rho_of(Pm[inE & PRE], 50, adj=adj); out["rho50adj_PRE"] = (rA, rkA)
    for nm, W in (("PRE", PRE), ("LATE", LATE)):
        _, vE = day_rv(inE & W); _, vC = day_rv(inC & W)
        out[f"rv_{nm}"] = (vE.mean() / vC.mean() if len(vE) and len(vC) else np.nan,
                           np.median(vE) / np.median(vC) if len(vE) and len(vC) else np.nan, len(vE), len(vC))
    for nm, W in (("PRE", PRE), ("POST", POST)):
        _, rE = day_ret(inE & W); _, rC = day_ret(inC & W)
        if len(rE) > 2 and len(rC) > 2:
            t = (rE.mean() - rC.mean()) / math.sqrt(rE.var(ddof=1) / len(rE) + rC.var(ddof=1) / len(rC))
        else: t = np.nan
        out[f"dir_{nm}"] = (rE.mean() if len(rE) else np.nan, rC.mean() if len(rC) else np.nan, t, len(rE))
    return out

SHIFTS = [s for s in range(-12, 13) if abs(s) >= 2]
# basis マップ（満期日と各プラセボ日）: basis_d = P_ref(日の PRE 最初の足) × DFF/100 × τ/365（τ は実満期の値）
def basis_map(S, taus):
    m = {}
    for o, tau in zip(S.tolist(), taus):
        if o in DAY_FIRST_P: m[o] = DAY_FIRST_P[o] * dff_at(o) / 100.0 * tau / 365.0
    return m
RES = {}
for wn, (lo, hi) in WIN.items():
    wmask = (year >= lo) & (year <= hi)
    S0 = EXP_ORD
    bm0 = basis_map(S0, TAU)
    r0 = stats(S0, wmask, adj_map=bm0)
    pl = []
    for s in SHIFTS:
        Ss, Ts = shift_set(s); pl.append((s, stats(Ss, wmask, adj_map=basis_map(Ss, Ts))))
    RES[wn] = (r0, pl, bm0)
    say(f"\n## {wn}: 満期日 {r0['nE']} 日・対照 {r0['nC']} 日（PRE 窓）")
    bvals = np.array([bm0[o] for o in S0 if o in bm0 and lo <= dt.date.fromordinal(int(o)).year <= hi])
    say(f"- basis（USD・満期日の P·DFF·τ/365）中央値 {np.median(bvals):.2f}・p90 {np.percentile(bvals, 90):.2f}・max {bvals.max():.2f}（{len(bvals)} 日）")
    def zline(key, pick, label, unit="", scale=1.0, extra=""):
        D0 = pick(r0[key]); Ds = np.array([pick(p[key]) for _, p in pl]); Ds = Ds[np.isfinite(Ds)]
        mu, sd = Ds.mean(), Ds.std(ddof=1); zz = (D0 - mu) / sd if sd > 0 else np.nan
        s2 = {s: pick(p[key]) for s, p in pl if abs(s) == 2}
        say(f"- {label}: D(0) {D0*scale:+.4f}{unit} vs プラセボ 22 本 平均 {mu*scale:+.4f} sd {sd*scale:.4f} → z_pl {zz:+.2f}・MDE(2sd) {2*sd*scale:.4f}{unit}"
            f"・s=−2 {s2.get(-2, np.nan)*scale:+.4f}／+2 {s2.get(2, np.nan)*scale:+.4f}{extra}")
        return D0, zz, sd
    r = r0["rho50_PRE"]
    say(f"- **H_PIN（主）G=50 PRE**: ρ_E {r[0]:.4f}（f_0 {r[5]*100:.3f}%・細格子順位 {r[3]}/50）vs ρ_C {r[1]:.4f}（f_0 {r[6]*100:.3f}%・順位 {r[4]}/50）")
    D_pin, z_pin, sd_pin = zline("rho50_PRE", lambda x: x[2], "  D_ρ(G=50・PRE)")
    r = r0["rho50_LATE"]; say(f"- 副 G=50 LATE: ρ_E {r[0]:.4f}（順位 {r[3]}/50）vs ρ_C {r[1]:.4f}（順位 {r[4]}）"); zline("rho50_LATE", lambda x: x[2], "  D_ρ(G=50・LATE)")
    r = r0["rho100_PRE"]; say(f"- 副 G=100 PRE: ρ_E {r[0]:.4f}（順位 {r[3]}/100）vs ρ_C {r[1]:.4f}（順位 {r[4]}）"); zline("rho100_PRE", lambda x: x[2], "  D_ρ(G=100・PRE)")
    rA = r0["rho50adj_PRE"]; As = np.array([p["rho50adj_PRE"][0] for _, p in pl]); As = As[np.isfinite(As)]
    zA = (rA[0] - As.mean()) / As.std(ddof=1)
    say(f"- **H_ADJ（副・basis 調整 G=50 PRE）**: ρ_adj(E) {rA[0]:.4f}（細格子順位 {rA[1]}/50）vs プラセボ 平均 {As.mean():.4f} sd {As.std(ddof=1):.4f} → z_pl {zA:+.2f}・MDE {2*As.std(ddof=1):.4f}")
    for nm in ("LATE", "PRE"):
        v = r0[f"rv_{nm}"]
        zline(f"rv_{nm}", lambda x: math.log(x[0]), f"  H_VAR {nm} 分散比（log 平均比）", extra=f"；平均比 {v[0]:.3f}・中央値比 {v[1]:.3f}（E {v[2]} 日／C {v[3]} 日）")
    for nm in ("PRE", "POST"):
        v = r0[f"dir_{nm}"]
        zline(f"dir_{nm}", lambda x: x[0] - x[1], f"  H_DIR {nm} 平均リターン差", unit=" bp", extra=f"；E {v[0]:+.2f} vs C {v[1]:+.2f} bp・Welch t {v[2]:+.2f}（E {v[3]} 日）")
    RES[wn] = (r0, pl, bm0, D_pin, z_pin, sd_pin)

# ---------------- 陽性対照（注入・在） ----------------
wn = "在 2010-20"; lo, hi = WIN[wn]; wmask = (year >= lo) & (year <= hi)
inE = np.isin(ordd, EXP_ORD) & wmask & PRE
Lnear = np.round(P / 50) * 50; dpin = P - Lnear
Pinj = P.copy(); m_inj = inE & (np.abs(dpin) <= 3.0); Pinj[m_inj] = Lnear[m_inj] + dpin[m_inj] * 0.5
rI = stats(EXP_ORD, wmask, Pov=Pinj)["rho50_PRE"]
sd_pin = RES[wn][5]; mu_pl = np.mean([p["rho50_PRE"][2] for _, p in RES[wn][1]])
say(f"\n## 陽性対照（在・満期日 PRE の |P−L50|≤3 USD を半分寄せる・{m_inj.sum()} 足）: ρ_E {rI[0]:.4f} → D_ρ {rI[2]:+.4f}・z_pl {(rI[2]-mu_pl)/sd_pin:+.2f}（実測 D_ρ {RES[wn][3]:+.4f} z {RES[wn][4]:+.2f}）")

# ---------------- 本番への接続（記述） ----------------
with open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8") as f: TR = json.load(f)["trades"]
te = np.array([t["entry_time"] for t in TR], np.int64); R = np.array([t["R"] for t in TR]); risk = np.array([t["risk"] for t in TR])
ex = np.array([t["exit"] for t in TR]); hold = np.array([t["hold"] for t in TR]); ft = 0.1 / risk
Rs = np.where(ex == "TIME", R - ft, R + ft)
et_tr = pd.to_datetime(te, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
tr_ord = et_tr.values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
tr_tod = ((et_tr.values - et_tr.values.astype("datetime64[D]")) / np.timedelta64(1, "m")).astype(int); tr_year = et_tr.year.values
exp_ts = {}
for e, _ in EXP:
    exp_ts[e.toordinal()] = int(pd.Timestamp(dt.datetime(e.year, e.month, e.day, 13, 30), tz="America/New_York").timestamp())
say("\n## 本番への接続（scan 19404 本・記述）")
for wn, (lo, hi) in WIN.items():
    wm = (tr_year >= lo) & (tr_year <= hi); inpre = (tr_tod >= 480) & (tr_tod < 810)
    onE = np.isin(tr_ord, EXP_ORD)
    i = np.array([BIDX.get(o, -1) for o in EXP_ORD]); Spm = np.unique(np.concatenate([BORD[np.clip(i + k, 0, len(BORD) - 1)] for k in (-1, 0, 1)]))
    onC = ~np.isin(tr_ord, Spm)
    a = Rs[wm & inpre & onE]; c = Rs[wm & inpre & onC]
    if len(a) > 2:
        se = math.sqrt(a.var(ddof=1) / len(a) + c.var(ddof=1) / len(c)); t = (a.mean() - c.mean()) / se
    else: se = t = np.nan
    alive = np.array([o in exp_ts and te[j] < exp_ts[o] < te[j] + 300 * hold[j] for j, o in enumerate(tr_ord)])
    al = Rs[wm & alive]
    say(f"- {wn}: 満期日 PRE 建玉 n {len(a)}・平均 R* {a.mean() if len(a) else np.nan:+.3f} vs 対照日 同時刻 n {len(c)} {c.mean():+.3f} → Δμ {a.mean()-c.mean() if len(a) else np.nan:+.3f}（t {t:+.2f}・MDE {2*se:.3f}R）"
        f"；13:30 ET 満期を生きて跨ぐ本 n {len(al)}・平均 R* {al.mean() if len(al) else np.nan:+.3f}")

# ---------------- 判定 ----------------
say("\n## 判定（事前固定）")
Din, zin = RES["在 2010-20"][3], RES["在 2010-20"][4]; Dout, zout = RES["外 2021-26H1"][3], RES["外 2021-26H1"][4]
pass_pin = (Din > 0) and (zin >= 2) and (Dout > 0) and (zout >= 1.5)
say(f"- H_PIN: 在 D_ρ {Din:+.4f} z {zin:+.2f}／外 {Dout:+.4f} z {zout:+.2f} → {'PASS' if pass_pin else 'null'}")
say(f"\n実行時間 {time.time()-T0:.1f} s")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
print("written", OUT)
