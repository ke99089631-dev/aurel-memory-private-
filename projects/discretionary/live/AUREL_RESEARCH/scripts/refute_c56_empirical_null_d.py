# -*- coding: utf-8 -*-
"""
[反証レーン / 2026-11-20 09:30 part D] part A/B の **λ の矛盾**を解き、ANN−oth contrast を正しい帰無で決着させる。

発見した矛盾（同じ腕・同じ構成・同じ推定器なのに λ が 1.4 倍違う）:
  part A  λ_oth（OFF7 = ±7k, k=1..8・|offset| ≤ 56 日・16 draw）  = **1.385**
  part B-12 λ_oth（FAM7 = ±7k, k=1..42・|offset| ≤ 294 日・84 draw）= **0.972**（在 0.981）
  part B-9 λ_ANN（FAM_ALL・|offset| ≤ 300 日・594 draw）           = **0.986**
→ λ は「腕の密度」ではなく **|offset| の大きさ**に依っている疑い。もしそうなら:
   (1) c56 の T1「窓集合型 Δμ の帰無 sd は名目の 1.25〜1.3 倍」は **推定器の性質としては誤り**。
       c56 が見たのは「**近傍 offset のプラセボが無効**（金のボラと 5σ 検出器の事象が数週スケールで塊になるので、
       ±7 日の偽窓は実事象の局所レジームと相関し、帰無になっていない）」という別の現象。
   (2) part A の λ_oth7 = 1.385 と、それを使った「λ 補正 t」表・part B-11 の「λ は事象密度の関数」は
       **私自身の人工物**（小 offset だけの族で測った）→ 取り下げ対象。
   (3) c56 が ANN−oth の t 2.62 を 1.3 で割って「境界」と読んだ操作は、無効な族から得た係数の適用＝二重に誤り。

=== part D の事前固定（数字を見る前・seed 20261120・乱数未使用） ===
データ・推定器・ctrl・複製 assert は c56 / part A/B/C と完全同一。読取専用・新規データなし。
族 FAM_ALL = 3 ≤ |d| ≤ 300 の全整数日。|offset| バケット = [3,14] / [15,56] / [57,140] / [141,300]。
判定規則（事前・boolean から合成）:
  D-1（λ は offset の関数か・T1 の正体）: 腕 oth と ANN について、バケット別 λ を印字。
      **oth の λ[3,56] ≥ 1.20 かつ λ[57,300] ≤ 1.10** → 「λ は推定器でなく近傍 offset の汚染」＝
        **c56 の T1 は破れ（ただし現象としては『近傍プラセボ無効』に読み替え）**／part A λ_oth7・part B-11 を取り下げ。
      oth の λ が全バケットで ≥1.20 → **T1 生存**（推定器の性質・c56 が正しい）。
      それ以外 → inconclusive。各バケット draw ≥ 30 を要件。
  D-2（近傍汚染の直接証拠）: oth 腕で |offset| と |t_pl| の Spearman 相関、および
      「偽窓が実 UJ 事象窓（±4h）と重なる本の割合」をバケット別に印字（記述・機構）。
  D-3（ANN−oth contrast の決着）: **両腕を同じ offset でずらし、構成は実腕に揃える**（偽窓 ∧ ~実 ANN 窓 のみ）。
      FAM_ALL・4 腕推定。studentize した |t_AO| の経験 95 パーセンタイル = crit95 を出す。
      観測 |t_AO| = 2.62 < crit95 → **H_PURE の (b) 脚は破れ**／≥ crit95 → **(b) 脚は生存**。
      併せて p_emp,t = (#{|t_pl| ≥ 2.62}+1)/(N+1) を印字。draw ≥ 200 を要件。
      ※part B-10 は「c56 構成（n 中央 ANN 側 62 ≠ 実 138）× 84 draw × β スケール」で破れと出た。
        part C で β スケール × n 不揃いは破れ側に偏ると確定したので、ここは t スケール × 構成マッチで再判定する。
  D-4（crit95 の提供）: 今後のサイクルが使える「この推定器・この窓での |t| の経験臨界値」を腕別に印字（成果物）。
事前の予測: D-1 は「λ は offset の関数」側（T1 破れ・私の part A も取り下げ）。D-3 は (b) 脚 **生存**側
  （part C と同じ理由で part B-10 の破れは n/スケール交絡の疑い）。**外したらそのまま書く。**
自分の破りの既知の弱点: (1) 隣接 offset は窓が重なり独立でない → バケット内の有効 draw は名目未満。
  (2) 大 offset は era 2021-26 の端で n が落ちる（±300 日で片側 10 ヶ月分）→ 大 offset バケットの λ は
      n 変動の影響を受ける。だから λ は β スケールではなく **sd(β)/mean(se) 比**で読む（n 効果は分子分母で一部打ち消す）。
  (3) crit95 は 596 draw の経験分位なので ±約 0.3 の不確実性がある。
出力 data/refute_c56_empirical_null_d.md。発注なし・本番編集なし・書込は AUREL_RESEARCH 配下のみ。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c56_empirical_null_d.md"); L = []
NY = "America/New_York"; SEED = 20261120
ZMAIN = 5.0; W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0
US2S = {(8, 20), (8, 25), (9, 35), (9, 40)}
FAM_ALL = [d for d in range(-300, 301) if 3 <= abs(d) <= 300]
BUCK = [(3, 14), (15, 56), (57, 140), (141, 300)]
M = 25

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

say("# [REFUTE 09:30 part D] λ の矛盾（1.385 vs 0.972）を解き、ANN−oth を構成マッチ×studentize で決着")
say(f"- 事前固定は docstring・seed {SEED}・データ/推定器は c56 と完全同一・読取専用")
say("")

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2(); CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0)
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)
r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = (lo >= 0)
S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
NNc = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NNc >= 1000, S2 / np.maximum(NNc, 1), np.nan))
nf3 = nf.copy()
for k in (1, 2, 3):
    nf3 &= np.r_[[False] * k, nf[:-k]]
cand = nf3 & ((wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))) & np.isfinite(sig)
z = np.abs(r) / sig

def decluster(mask):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= DECL: keep.append(i); last = ts[i]
    return np.array(keep, int)

J4 = decluster(cand & (z >= 4.0)); J5 = decluster(cand & (z >= ZMAIN))
isevbar = etdate.isin(evdays)
ok5 = ~np.asarray(isevbar[J5]); sch5 = (mn[J5] % 15 == 0)
SJ5 = J5[ok5 & sch5]; UJ5 = J5[ok5 & ~sch5]
is_us2 = np.array([(int(hr[i]), int(mn[i])) in US2S for i in UJ5], bool)
UJ_US2 = UJ5[is_us2]; UJ_OTH = UJ5[~is_us2]
assert len(J5) == 2166 and len(SJ5) == 786 and len(UJ5) == 937, "複製失敗"

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)

def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    if len(t0s) == 0: return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, _ = inwin(t_nfp); m_fomc, _ = inwin(t_fomc)
ANNm = (m_nfp | m_fomc); tr["ANN"] = ANNm
tsf = ts.astype(float)
m_sj, _ = inwin(tsf[SJ5] + 300); m_uj, p_uj = inwin(tsf[UJ5] + 300)
tr["SJ"] = m_sj & ~tr.ANN & ~tr.isevday; tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
last_is_us2 = np.isin((p_uj - 300).astype(np.int64), ts[UJ_US2])
tr["US2"] = tr.UJ & last_is_us2; tr["OTH"] = tr.UJ & ~last_is_us2
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN

era = ((tr.year >= 2021) & (tr.year <= 2026)).to_numpy()
HH = tr.hh.to_numpy(); DAYc = pd.factorize(tr.day)[0]; Rsv = tr.Rs.to_numpy(float)
H_FULL = np.column_stack([(HH == h).astype(float) for h in range(1, 24)])
ctrlv = tr.ctrl.to_numpy(); evmv = tr.isevday.to_numpy(); wdmv = tr.wd.to_numpy() <= 4
m_uj_real = tr.UJ.to_numpy()

def fit_fast(rows, gcols):
    ri = np.where(rows)[0]
    G = np.column_stack([g[ri].astype(float) for g in gcols])
    X = np.column_stack([np.ones(len(ri)), G, H_FULL[ri]])
    y = Rsv[ri]
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    dc = DAYc[ri]; u, inv = np.unique(dc, return_inverse=True)
    S = np.zeros((len(u), X.shape[1])); np.add.at(S, inv, X * e[:, None])
    nG = len(u); V = XtX_inv @ (S.T @ S) @ XtX_inv * (nG / max(nG - 1, 1))
    return [(beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(G[:, i].sum())) for i in range(len(gcols))], V, nG

g4 = [tr.ANN.to_numpy(), tr.SJ.to_numpy(), tr.US2.to_numpy(), tr.OTH.to_numpy()]
rows4 = era & (tr.ANN | tr.SJ | tr.US2 | tr.OTH | tr.ctrl).to_numpy()
o4, V4, nG4 = fit_fast(rows4, g4)
bA, sA, nA = o4[0]; bo, so, no = o4[3]
cvv = np.zeros(V4.shape[0]); cvv[1] = 1; cvv[4] = -1
sAO = math.sqrt(max(cvv @ V4 @ cvv, 0)); dAO = bA - bo; tAO = dAO / sAO
assert nA == 138 and abs(bA - 0.513) < 0.002, "複製失敗"
say(f"- 複製 OK: 外 ANN {bA:+.3f} (t {bA/sA:+.2f}・n {nA})・oth {bo:+.3f} (t {bo/so:+.2f}・n {no})・**ANN−oth {dAO:+.3f} (t {tAO:+.2f}・se {sAO:.3f})**")
say("")

ANN_T0 = np.concatenate([t_nfp[np.isfinite(t_nfp)], t_fomc[np.isfinite(t_fomc)]])
OTH_T0 = tsf[UJ_OTH] + 300

# ================= D-1 / D-2: λ を |offset| バケット別に =================
say("## D-1/D-2 λ を |offset| バケット別に測る（part A 1.385 と part B-12 0.972 の矛盾の正体）")
rows = {"oth": [], "ANN": []}
for sh in FAM_ALL:
    off = sh * 86400.0
    for arm, base in (("oth", OTH_T0), ("ANN", ANN_T0)):
        mp, _ = inwin(base, off=off)
        pl = mp & ~evmv & wdmv & ~m_any4 & ~ANNm      # c56 構成（part A/B-12 と同じ）
        if int((pl & era).sum()) < 10: continue
        rr = era & (pl | (ctrlv & ~pl))
        oo, VV, nGg = fit_fast(rr, [pl]); b, se, n = oo[0]
        ov = float((pl & era & m_uj_real).sum()) / max(int((pl & era).sum()), 1)
        rows[arm].append(dict(shd=sh, ad=abs(sh), b=b, se=se, n=n,
                              t=(b / se if se > 0 else np.nan), ovlap=ov))
D = {k: pd.DataFrame(v) for k, v in rows.items()}
say("| 腕 | |offset| バケット | draw | β 実測 sd | 名目 se 平均 | **λ** | &#124;t&#124;≥2 % | n 中央 | 偽窓が実 UJ 窓と重なる本の割合 |")
say("|---|---|---|---|---|---|---|---|---|")
LAM = {}
for arm in ("oth", "ANN"):
    for a, bb in BUCK:
        q = D[arm][(D[arm].ad >= a) & (D[arm].ad <= bb)]
        if len(q) < 3:
            say(f"| {arm} | [{a},{bb}] | {len(q)} | — | — | — | — | — | — |"); continue
        lam = q.b.std(ddof=1) / q.se.mean(); LAM[(arm, a, bb)] = (lam, len(q))
        say(f"| {arm} | [{a},{bb}] | {len(q)} | {q.b.std(ddof=1):.4f} | {q.se.mean():.4f} | **{lam:.3f}** | "
            f"{(q.t.abs()>=2).mean()*100:.1f}% | {q.n.median():.0f} | {q.ovlap.mean()*100:.1f}% |")
    q = D[arm]
    say(f"| {arm} | 全体 [3,300] | {len(q)} | {q.b.std(ddof=1):.4f} | {q.se.mean():.4f} | **{q.b.std(ddof=1)/q.se.mean():.3f}** | "
        f"{(q.t.abs()>=2).mean()*100:.1f}% | {q.n.median():.0f} | {q.ovlap.mean()*100:.1f}% |")
say("")
Qo = D["oth"]
lam_small = Qo[(Qo.ad >= 3) & (Qo.ad <= 56)]
lam_big = Qo[(Qo.ad >= 57) & (Qo.ad <= 300)]
ls = lam_small.b.std(ddof=1) / lam_small.se.mean(); lb = lam_big.b.std(ddof=1) / lam_big.se.mean()
say(f"- oth λ[3,56] = **{ls:.3f}**（draw {len(lam_small)}）／λ[57,300] = **{lb:.3f}**（draw {len(lam_big)}）")
sp_t = Qo[["ad"]].assign(at=Qo.t.abs()).corr(method="spearman").iloc[0, 1]
sp_ov = Qo[["ad"]].assign(ov=Qo.ovlap).corr(method="spearman").iloc[0, 1]
say(f"- D-2 oth: Spearman(|offset|, |t_pl|) = **{sp_t:+.3f}**・Spearman(|offset|, 実 UJ 窓との重なり率) = **{sp_ov:+.3f}**")
say(f"  （負なら「近い offset ほど t が大きく・実窓と重なる」＝近傍プラセボは帰無でない の直接証拠）")
ok_draw = (len(lam_small) >= 30) and (len(lam_big) >= 30)
d1_offsetfn = ok_draw and (ls >= 1.20) and (lb <= 1.10)
d1_t1surv = ok_draw and all(v[0] >= 1.20 for k, v in LAM.items() if k[0] == "oth" and v[1] >= 30)
say(f"- 条件 λ[3,56] ≥ 1.20 → {ls >= 1.20}・条件 λ[57,300] ≤ 1.10 → {lb <= 1.10}・draw 要件 → {ok_draw}")
say(f"- **D-1 = {'λ は offset の関数＝c56 の T1 は破れ（現象は『近傍プラセボ無効』に読み替え）' if d1_offsetfn else ('T1 生存（推定器の性質）' if d1_t1surv else 'inconclusive')}**")
say("")

# ================= D-3: contrast を構成マッチ × studentize =================
say("## D-3 ANN−oth contrast の決着（両腕を同じ offset でずらす・構成は実腕に揃える・studentize・FAM_ALL）")
rows = []
for sh in FAM_ALL:
    off = sh * 86400.0
    ma, _ = inwin(ANN_T0, off=off); mo, _ = inwin(OTH_T0, off=off)
    mu, _ = inwin(tsf[UJ_US2] + 300, off=off); ms, _ = inwin(tsf[SJ5] + 300, off=off)
    pa = ma & ~ANNm
    po = mo & ~ANNm & ~pa
    pu = mu & ~ANNm & ~pa & ~po
    ps = ms & ~ANNm & ~pa & ~po & ~pu
    if int((pa & era).sum()) < 10 or int((po & era).sum()) < 10: continue
    anyg = pa | po | pu | ps
    rr = era & (anyg | (ctrlv & ~anyg))
    oo, VV, nGg = fit_fast(rr, [pa, ps, pu, po])
    cv = np.zeros(VV.shape[0]); cv[1] = 1; cv[4] = -1
    sd = math.sqrt(max(cv @ VV @ cv, 0)); dd = oo[0][0] - oo[3][0]
    rows.append(dict(shd=sh, ad=abs(sh), d=dd, se=sd, nA=oo[0][2], nO=oo[3][2],
                     t=(dd / sd if sd > 0 else np.nan)))
P3 = pd.DataFrame(rows)
say(f"- draw **{len(P3)}**・ANN 側 n 中央 {P3.nA.median():.0f}（実 138・part B-10 は 62）・oth 側 n 中央 {P3.nO.median():.0f}（実 225）")
say(f"- Δ 平均 {P3.d.mean():+.4f}・Δ 実測 sd {P3.d.std(ddof=1):.4f}・名目 se 平均 {P3.se.mean():.4f} → **λ_AO = {P3.d.std(ddof=1)/P3.se.mean():.3f}**（part B-10 は 84 draw の小 offset 寄りで 1.122）")
say(f"- |t_pl| の分布: 中央 {P3.t.abs().median():.2f}・90% {P3.t.abs().quantile(0.90):.2f}・**95% = {P3.t.abs().quantile(0.95):.2f}**・99% {P3.t.abs().quantile(0.99):.2f}・最大 {P3.t.abs().max():.2f}・|t|≥2 {(P3.t.abs()>=2).mean()*100:.1f}%")
crit95 = float(P3.t.abs().quantile(0.95))
ex3 = int((P3.t.abs() >= abs(tAO)).sum()); p3t = (ex3 + 1) / (len(P3) + 1)
say(f"- 観測 |t_AO| = **{abs(tAO):.2f}** vs 経験臨界値 crit95 = **{crit95:.2f}** → 観測 ≥ crit95 は **{abs(tAO) >= crit95}**")
say(f"- |t_pl| ≥ {abs(tAO):.2f} の draw = **{ex3}** / {len(P3)} → p_emp,t = **{p3t:.4f}**")
say(f"- バケット別 λ_AO: " + " ".join(
    f"[{a},{b}] {P3[(P3.ad>=a)&(P3.ad<=b)].d.std(ddof=1)/P3[(P3.ad>=a)&(P3.ad<=b)].se.mean():.3f}(n{len(P3[(P3.ad>=a)&(P3.ad<=b)])})"
    for a, b in BUCK if len(P3[(P3.ad >= a) & (P3.ad <= b)]) >= 3))
d3_ok = len(P3) >= 200
d3_break = (abs(tAO) < crit95) if d3_ok else None
say(f"- 条件 draw ≥ 200 → {d3_ok}・条件 観測 |t| < crit95 → {d3_break}")
say(f"- **D-3 = {('H_PURE の (b) 脚は破れ' if d3_break else '(b) 脚は構成マッチ×studentize の帰無でも生存') if d3_ok else '判定せず'}**")
say(f"- part B-10 の取り扱い: {'維持' if d3_break else '**取り下げ**（n 不揃い 62 vs 138 ＋ β スケール ＋ 小 offset 寄りの 84 draw による交絡）'}")
say("")

# ================= D-4: crit95 の提供 =================
say("## D-4 成果物: この推定器・この窓での |t| 経験臨界値（今後のサイクルが名目 2.0 の代わりに使う値）")
say("| 統計量 | 族 | draw | &#124;t&#124; 90% | **&#124;t&#124; 95%** | &#124;t&#124; 99% | 名目 95% = 1.96 との比 |")
say("|---|---|---|---|---|---|---|")
for nm, q in (("β_oth（単腕・c56 構成・全 offset）", D["oth"]), ("β_oth（|offset| ≥ 57 のみ）", D["oth"][D["oth"].ad >= 57]),
              ("β_ANN（単腕・c56 構成・全 offset）", D["ANN"]), ("Δ_ANN−oth（構成マッチ・全 offset）", P3),
              ("Δ_ANN−oth（|offset| ≥ 57 のみ）", P3[P3.ad >= 57])):
    if len(q) < 20: continue
    c95 = q.t.abs().quantile(0.95)
    say(f"| {nm} | FAM_ALL | {len(q)} | {q.t.abs().quantile(0.90):.2f} | **{c95:.2f}** | {q.t.abs().quantile(0.99):.2f} | {c95/1.96:.2f}× |")
say("")

say("## part D 総合")
say("| 検定 | 結果 | 数字 |")
say("|---|---|---|")
say(f"| D-1 λ は offset の関数か（T1 の正体） | **{'T1 破れ→読み替え' if d1_offsetfn else ('T1 生存' if d1_t1surv else 'inconclusive')}** | oth λ[3,56] {ls:.3f} vs λ[57,300] {lb:.3f} |")
say(f"| D-2 近傍汚染の直接証拠 | **{'支持' if (sp_t < 0 and sp_ov < 0) else '不支持'}（記述）** | Spearman(&#124;offset&#124;,&#124;t&#124;) {sp_t:+.3f}・(&#124;offset&#124;,実窓重なり) {sp_ov:+.3f} |")
say(f"| D-3 ANN−oth 構成マッチ×studentize | **{('破れ' if d3_break else '生存') if d3_ok else '判定せず'}** | 観測 &#124;t&#124; {abs(tAO):.2f} vs crit95 {crit95:.2f}・p_emp,t {p3t:.4f} |")
say("")
say(f"- 実行時間 {time.time()-T0:.1f} s・seed {SEED}（乱数未使用）")
say("- 副作用: 読取のみ（npz 1・json 1・csv 2）。書込は data/refute_c56_empirical_null_d.md のみ。発注/デモ発注/本番編集/プロセス接触/MT5/プロップ/秘密 なし。外部通信なし。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
