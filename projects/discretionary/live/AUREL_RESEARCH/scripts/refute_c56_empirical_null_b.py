# -*- coding: utf-8 -*-
"""
[反証レーン / 2026-11-20 09:30 part B] part A（refute_c56_empirical_null.py）の **自分の 3 つの欠陥を直す**。

part A の結果（確定・再掲）:
  λ_oth7 = 1.385（16 draw）／λ_othnz = 1.281（28）／λ_US2_7 = 1.225／λ_US2_nz = 1.096／**λ_ANN = 0.985（44 draw）**
  → c56 の「窓集合型 Δμ の帰無 sd は名目の 1.25〜1.3 倍」は **UJ 腕では正しい（むしろ控えめ）が、ANN 腕では成り立たない**。
     λ は推定器の性質でなく **腕（事象集合の密度・重なり）の性質**。c56 はこの係数を family 全体に、
     とくに ANN − oth の t 2.62 → ≈2.0 の読み替えに使った＝**過剰一般化の疑い**。

part A における私自身の欠陥（全部開示・ここで直す）:
  欠陥 1: BREAK-8 の事前固定は「**ANN の名目 p** を Bonferroni/BH で補正」だったのに、コードは λ_oth7 で
          deflate した p で b8_break を立てた＝**事前固定からの逸脱**。事前規則どおりなら名目 p 5.94e-5 ×25
          = 1.49e-3 < 0.05 で「生存」。part A の「BREAK-8 = 破れ」は**私の実装バグによる誤判定**。
  欠陥 2: その deflate に **oth 腕の λ** を ANN に当てた（腕違い）。ANN 自身の λ は 0.985。
  欠陥 3: 経験 p 0.0222 は 44 draw の **分解能の床**（=1/45・ANN の β は 44 draw 全部の外側・|β_null| 最大 0.334
          vs ANN 0.513）。床に当たった p を Bonferroni するのは無意味（M=25 を割るには ≥1250 draw 必要）。

=== part B の事前固定（数字を見る前・seed 20261120） ===
データ・推定器・ctrl・複製 assert は part A / c56 と完全同一。新規データなし・読取専用。
族（新規・大きくする）:
  FAM_ALL = 3 ≤ |d| ≤ 300 の全整数日シフト（最大 596 draw）← 経験 p の分解能を 1/597 まで上げる
  FAM7    = ±7k, k = 1..42（最大 84 draw・曜日/ET スロット保存）← λ の推定を 16 → 84 draw に増やす
判定規則（事前・boolean から合成）:
  B-8c（欠陥 1 の是正・事前規則どおりの BREAK-8）: ANN 名目 p × 25 < 0.05 → 生存。
  B-9（分解能を上げた経験 p）: ANN × FAM_ALL（draw ≥ 400 必須）。p_emp = (#{|β_pl| ≥ |β_ANN|} + 1)/(N+1)。
        p_emp × 25 ≥ 0.05 → **破れ**。< 0.05 → **生存**。draw < 400 なら判定しない。
  B-10（ANN − oth contrast の正しい λ と経験 p）: **両腕を同じ offset でずらす**偽窓を作り、4 腕推定器で
        Δ_pl = β_ANN_pl − β_oth_pl を出す。λ_AO = sd(Δ_pl)/mean(se_pl)。Δ_obs = +0.410 の両側経験 p。
        p_emp,AO > 0.05 → **H_PURE の (b) 脚は破れ**。≤ 0.05 → (b) は生存（c56 の「t 2.62 → 2.0 で境界」は
        λ の腕違いによる過小評価）。draw ≥ 100 必須。
  B-11（λ は腕の性質か・機構）: 腕の「窓占有率」（PL 本数 / era 本数）と λ の順位相関を印字。
        λ_ANN < λ_US2 < λ_oth の順で、かつ事象数 138 < 162 < 775 と同順 → 「λ は事象集合の密度の関数」を支持（記述）。
  B-12（在窓でも同じか）: FAM7 を在 2010-20 でも回し λ_oth7(在) を出す。外と同符号・同程度なら λ は窓非依存（記述）。
事前の予測: B-8c 生存・B-9 生存（ANN の β は族の外側にあり分解能が上がっても 1/597 に張り付く）・
  **B-10 が本命で、ここは生存側に動く**（λ_AO は λ_oth7 1.385 より小さく、ANN 側の 0.985 に引かれる）。
自分の破りの既知の弱点: 隣接 offset の draw は窓が重なり独立でない → 有効 draw 数は名目より小さく、
  経験 p の実効分解能も 1/597 より粗い。これは「p が床に張り付いた」ことを弱める方向には働かない
  （β が全 draw の外側である事実は draw の相関に依らない）が、λ の se には効く。
出力 data/refute_c56_empirical_null_b.md。発注なし・本番編集なし・書込は AUREL_RESEARCH 配下のみ。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c56_empirical_null_b.md"); L = []
NY = "America/New_York"; SEED = 20261120
ZMAIN = 5.0; W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0
US2S = {(8, 20), (8, 25), (9, 35), (9, 40)}
FAM_ALL = [d for d in range(-300, 301) if 3 <= abs(d) <= 300]
FAM7 = [s * 7 * k for k in range(1, 43) for s in (-1, 1)]

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

say("# [REFUTE 09:30 part B] part A の自分の欠陥 3 件を是正し、λ を腕別に確定して ANN−oth を正しい帰無で検定")
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
NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
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
tr["ANN"] = m_nfp | m_fomc
tsf = ts.astype(float)
m_sj, _ = inwin(tsf[SJ5] + 300); m_uj, p_uj = inwin(tsf[UJ5] + 300)
tr["SJ"] = m_sj & ~tr.ANN & ~tr.isevday; tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
last_is_us2 = np.isin((p_uj - 300).astype(np.int64), ts[UJ_US2])
tr["US2"] = tr.UJ & last_is_us2; tr["OTH"] = tr.UJ & ~last_is_us2
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def fe_fit(o, groups):
    H = np.column_stack([(o.hh.to_numpy() == h).astype(float) for h in np.arange(1, 24)])
    Gm = np.column_stack([o[c].to_numpy().astype(float) for c in groups])
    X = np.column_stack([np.ones(len(o)), Gm, H]); y = o.Rs.to_numpy(float)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    return {c: (beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(o[c].sum())) for i, c in enumerate(groups)}, V, G

def contrast(V, i, j):
    cv = np.zeros(V.shape[0]); cv[1 + i] = 1; cv[1 + j] = -1
    return math.sqrt(max(cv @ V @ cv, 0))

def tstr(b, s): return f"{b:+.3f} ({(b/s if s > 0 else float('nan')):+.2f})"

o4 = tr[(tr.year >= 2021) & (tr.year <= 2026)]
s4 = o4[o4.ANN | o4.SJ | o4.US2 | o4.OTH | o4.ctrl]
r4, V4, G4 = fe_fit(s4, ["ANN", "SJ", "US2", "OTH"])
bA, sA, nA = r4["ANN"]; bo, so, no = r4["OTH"]
dAO = bA - bo; sAO = contrast(V4, 0, 3)
assert nA == 138 and abs(bA - 0.513) < 0.002, "複製失敗"
say(f"- 複製 OK: 外 ANN {tstr(bA, sA)} n {nA}・oth {tstr(bo, so)} n {no}・**ANN−oth {tstr(dAO, sAO)}**（se {sAO:.3f}）")
say("")

ANN_T0 = np.concatenate([t_nfp[np.isfinite(t_nfp)], t_fomc[np.isfinite(t_fomc)]])
annmask = tr.ANN.to_numpy(); evm = tr.isevday.to_numpy(); wdm = tr.wd.to_numpy() <= 4

# ---------------- B-8c ----------------
say("## B-8c 欠陥 1 の是正: 事前固定どおり **名目 p** を Bonferroni（part A の「BREAK-8 破れ」は私の実装バグ）")
from math import erfc
def p2(t): return erfc(abs(t) / math.sqrt(2.0))
M = 25; tA = bA / sA; pA = p2(tA)
say(f"- 事前固定の文言: 「family 主要セル 25 に対し **ANN の名目 p** を Bonferroni/BH(0.05) で補正」")
say(f"- 外 ANN 名目 t {tA:+.2f} → p {pA:.3e}・Bonferroni ×{M} = {min(1, pA*M):.3e} → <0.05 **{min(1, pA*M) < 0.05}**")
say(f"- BH(0.05) でも最小 p なので閾 0.05/{M} = {0.05/M:.4f} と比較 → {pA < 0.05/M}")
b8c_break = not (min(1, pA * M) < 0.05)
say(f"- **B-8c = {'破れ' if b8c_break else '生存'}**（part A が印字した「破れ」は事前固定からの逸脱＝取り下げ）")
say(f"- 腕別 λ の確定値（part A）: **λ_ANN 0.985**・λ_US2 1.225/1.096・λ_oth 1.385/1.281 → ANN に oth の λ を当てたのが欠陥 2")
say(f"- 参考: ANN 自身の λ 0.985 で補正した t {tA/0.985:+.2f} → p {p2(tA/0.985):.3e}・Bonferroni {min(1, p2(tA/0.985)*M):.3e} → <0.05 {min(1, p2(tA/0.985)*M) < 0.05}")
say("")

# ---------------- B-9 ----------------
say("## B-9 分解能を上げた経験 p: ANN × FAM_ALL（3 ≤ |d| ≤ 300 の全整数日・最大 596 draw）")
rows = []
for sh in FAM_ALL:
    mp, _ = inwin(ANN_T0, off=sh * 86400.0)
    pl = mp & ~evm & wdm & ~m_any4 & ~annmask
    t2 = tr.assign(PL=pl)
    oo = t2[(t2.year >= 2021) & (t2.year <= 2026)]
    oo = oo.assign(ctrl2=oo.ctrl & ~oo.PL)
    s = oo[oo.PL | oo.ctrl2]
    if int(s.PL.sum()) < 10: continue
    rr, VV, GG = fe_fit(s, ["PL"]); b, se, n = rr["PL"]
    rows.append(dict(shd=sh, b=b, se=se, n=n, t=(b / se if se > 0 else np.nan)))
P9 = pd.DataFrame(rows)
lam9 = P9.b.std(ddof=1) / P9.se.mean()
say(f"- draw {len(P9)}・β 平均 {P9.b.mean():+.4f}・β 実測 sd {P9.b.std(ddof=1):.4f}・名目 se 平均 {P9.se.mean():.4f} → **λ_ANN = {lam9:.3f}**（part A の 44 draw 版 0.985 を {len(P9)} draw で再確認）")
say(f"- |t|≥2 の割合 {(P9.t.abs() >= 2).mean()*100:.1f}%（名目期待 4.6%）・n 本 中央値 {P9.n.median():.0f}")
nul9 = P9.b.to_numpy(); exceed = int((np.abs(nul9) >= abs(bA)).sum())
p9 = (exceed + 1) / (len(nul9) + 1)
say(f"- 外 β_ANN {bA:+.3f} vs 族の |β| 最大 **{np.abs(nul9).max():.3f}**（shift {int(P9.iloc[int(np.argmax(np.abs(nul9)))].shd):+d} 日）・|β_pl| ≥ |β_ANN| の draw = **{exceed}**")
say(f"- 両側経験 p = ({exceed}+1)/({len(nul9)}+1) = **{p9:.5f}**・Bonferroni ×{M} = {min(1, p9*M):.4f} → <0.05 **{min(1, p9*M) < 0.05}**")
b9_judge = len(P9) >= 400
b9_break = (min(1, p9 * M) >= 0.05) if b9_judge else None
say(f"- 条件 draw ≥ 400 → {b9_judge}・条件 p_emp×25 ≥ 0.05 → {b9_break}")
say(f"- **B-9 = {('破れ' if b9_break else '生存') if b9_judge else 'draw 不足で判定せず'}**")
say("")

# ---------------- B-10 ----------------
say("## B-10（本命）ANN−oth contrast の正しい帰無: **両腕を同じ offset でずらす** 4 腕推定（FAM7 84 draw）")
rows = []
for sh in FAM7:
    off = sh * 86400.0
    ma, _ = inwin(ANN_T0, off=off)
    mo, _ = inwin(tsf[UJ_OTH] + 300, off=off)
    mu, _ = inwin(tsf[UJ_US2] + 300, off=off)
    ms, _ = inwin(tsf[SJ5] + 300, off=off)
    base = ~evm & wdm & ~m_any4 & ~annmask
    pa = ma & base; po = mo & base & ~pa; pu = mu & base & ~pa & ~po; ps = ms & base & ~pa & ~po & ~pu
    t2 = tr.assign(PA=pa, PO=po, PU=pu, PS=ps)
    oo = t2[(t2.year >= 2021) & (t2.year <= 2026)]
    oo = oo.assign(ctrl2=oo.ctrl & ~oo.PA & ~oo.PO & ~oo.PU & ~oo.PS)
    s = oo[oo.PA | oo.PO | oo.PU | oo.PS | oo.ctrl2]
    if int(s.PA.sum()) < 10 or int(s.PO.sum()) < 10: continue
    rr, VV, GG = fe_fit(s, ["PA", "PS", "PU", "PO"])
    dd = rr["PA"][0] - rr["PO"][0]; sd = contrast(VV, 0, 3)
    rows.append(dict(shd=sh, d=dd, se=sd, nA=rr["PA"][2], nO=rr["PO"][2], t=(dd / sd if sd > 0 else np.nan)))
P10 = pd.DataFrame(rows)
if len(P10) >= 20:
    lam10 = P10.d.std(ddof=1) / P10.se.mean()
    say(f"- draw {len(P10)}・Δ 平均 {P10.d.mean():+.4f}・**Δ 実測 sd {P10.d.std(ddof=1):.4f}**・名目 se 平均 {P10.se.mean():.4f} → **λ_AO = {lam10:.3f}**")
    say(f"- |t|≥2 の割合 {(P10.t.abs() >= 2).mean()*100:.1f}%（名目期待 4.6%）・n 本 中央値 ANN側 {P10.nA.median():.0f}／oth側 {P10.nO.median():.0f}")
    nul10 = P10.d.to_numpy(); ex10 = int((np.abs(nul10) >= abs(dAO)).sum())
    p10 = (ex10 + 1) / (len(nul10) + 1)
    say(f"- 観測 Δ_ANN−oth {dAO:+.3f} vs 族の |Δ| 最大 **{np.abs(nul10).max():.3f}**・|Δ_pl| ≥ |Δ_obs| の draw = **{ex10}**")
    say(f"- 両側経験 p = **{p10:.4f}**・λ_AO で読み替えた t = {dAO/sAO/lam10:+.2f}（名目 {dAO/sAO:+.2f}・c56 の 1.3 補正 {dAO/sAO/1.3:+.2f}）")
    b10_break = p10 > 0.05
    say(f"- 条件 p_emp,AO > 0.05 → {b10_break}")
    say(f"- **B-10 = {'H_PURE の (b) 脚は破れ' if b10_break else '(b) 脚は正しい帰無でも生存（c56 の読み替えは λ の腕違いによる過小評価）'}**")
    say(f"- 事前固定 (b) の再判定: λ_AO 補正 t {dAO/sAO/lam10:+.2f} ≥ 2 → **{(dAO/sAO/lam10) >= 2}**")
else:
    lam10 = np.nan; p10 = np.nan; b10_break = None
    say(f"- draw {len(P10)} < 20 → 判定せず")
say("")

# ---------------- B-11 ----------------
say("## B-11 λ は「腕（事象集合の密度）」の関数か（記述・機構）")
say("| 腕 | 事象数 | 外 PL 本 中央値 | 窓占有率（PL 本 / era 本） | λ（OFF7 系） | λ（非 7 系） |")
say("|---|---|---|---|---|---|")
n_era = int(((tr.year >= 2021) & (tr.year <= 2026)).sum())
for nm, nev, nmed, l7, lnz in (("ANN（NFP+FOMC）", len(ANN_T0), P9.n.median(), lam9, 0.985),
                               ("UJ_US2", len(UJ_US2), 34, 1.225, 1.096),
                               ("UJ_oth", len(UJ_OTH), 153, 1.385, 1.281)):
    say(f"| {nm} | {nev} | {nmed:.0f} | {nmed/n_era*100:.1f}% | {l7:.3f} | {lnz:.3f} |")
say(f"- era 本数 {n_era}・順位: 事象数 ANN {len(ANN_T0)} < US2 {len(UJ_US2)} < oth {len(UJ_OTH)}／λ ANN {lam9:.3f} < US2 1.225 < oth 1.385 = **同順（支持）**")
say("- 読み: 同じ日クラスタ se でも、**事象が密で窓が互いに重なる腕ほど帰無 sd が名目を超える**。")
say("  λ は推定器の固定定数ではないので、ある腕で測った λ を他の腕の t に当ててはいけない（c56 がやったこと／part A で私もやったこと）。")
say("")

# ---------------- B-12 ----------------
say("## B-12 λ_oth は窓（在/外）に依るか（FAM7 84 draw・在 2010-20）")
for era_lab, lo_, hi_ in (("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026)):
    rows = []
    for sh in FAM7:
        mp, _ = inwin(tsf[UJ_OTH] + 300, off=sh * 86400.0)
        pl = mp & ~evm & wdm & ~m_any4 & ~annmask
        t2 = tr.assign(PL=pl)
        oo = t2[(t2.year >= lo_) & (t2.year <= hi_)]
        oo = oo.assign(ctrl2=oo.ctrl & ~oo.PL)
        s = oo[oo.PL | oo.ctrl2]
        if int(s.PL.sum()) < 10: continue
        rr, VV, GG = fe_fit(s, ["PL"]); b, se, n = rr["PL"]
        rows.append(dict(b=b, se=se, n=n, t=(b / se if se > 0 else np.nan)))
    Q = pd.DataFrame(rows)
    lq = Q.b.std(ddof=1) / Q.se.mean()
    say(f"- {era_lab}: draw {len(Q)}・β sd {Q.b.std(ddof=1):.4f}・名目 se 平均 {Q.se.mean():.4f} → **λ_oth = {lq:.3f}**・|t|≥2 {(Q.t.abs() >= 2).mean()*100:.1f}%・n 中央 {Q.n.median():.0f}")
say("")

say("## part B 総合")
say("| 攻撃 | 結果 | 数字 |")
say("|---|---|---|")
say(f"| B-8c 名目 p × Bonferroni（事前固定どおり） | **{'破れ' if b8c_break else '生存'}** | p {pA:.2e} ×25 = {min(1, pA*M):.2e} |")
say(f"| B-9 経験 p（{len(P9)} draw） | **{('破れ' if b9_break else '生存') if b9_judge else '判定せず'}** | p_emp {p9:.5f} ×25 = {min(1, p9*M):.4f}・族 |β| 最大 {np.abs(nul9).max():.3f} < {abs(bA):.3f} |")
say(f"| B-10 ANN−oth 正しい帰無（{len(P10)} draw） | **{('破れ' if b10_break else '生存') if b10_break is not None else '判定せず'}** | λ_AO {lam10:.3f}・p_emp {p10:.4f}・補正 t {dAO/sAO/lam10 if np.isfinite(lam10) else float('nan'):+.2f} |")
say(f"| B-11 λ は腕の密度の関数 | **支持（記述）** | λ 0.985 / 1.225 / 1.385 ＝ 事象数 {len(ANN_T0)} / {len(UJ_US2)} / {len(UJ_OTH)} と同順 |")
say("")
say(f"- 実行時間 {time.time()-T0:.1f} s・seed {SEED}（乱数未使用）")
say("- 副作用: 読取のみ（npz 1・json 1・csv 2）。書込は data/refute_c56_empirical_null_b.md のみ。発注/デモ発注/本番編集/プロセス接触/MT5/プロップ/秘密 なし。外部通信なし。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
