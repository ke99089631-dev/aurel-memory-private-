# -*- coding: utf-8 -*-
"""
[反証レーン / 2026-11-20 09:30] 対象 = cycle56（本日 06:43）＋その支えである c45 の唯一の生存正 ANN。

c56 は H_STEP underpowered・H_PURE inconclusive と自己申告したので「PASS を壊す」余地は無い。
よって攻撃するのは **c56 自身が最重大反証 (i) として書いた支え**と、**family 全体で唯一生きている正の β**:

  T1 = 「窓集合型 Δμ の帰無 sd は名目の 1.25〜1.3 倍」
       — この係数は **プラセボ 2 draw（oth の ±7 日）だけ**から読まれている。2 draw で sd 比を
         1.25〜1.3 と推定するのは不可能（sd の sd が ≈ 70%）。c56 はこの係数で自分の t を割って
         「印字以上に inconclusive」と結論し、ANN − oth の t 2.62 を ≈2.0 に落としている。
       攻撃 = **プラセボ族を 2 → 多数に増やして帰無分布を実測し、λ を直接測る**。
         λ が 1 に近ければ c56 は過剰補正（T1 破れ）／1.25 以上なら T1 は強化され family の t は全部読み替え。

  T2 = 「外 ANN β +0.513 (t 4.02・n 138)」= c45/c55/c56 family で唯一の生存正。c56 は US2 vs oth の
       状態不揃い（atr 3.68 vs 5.12）を自分で指摘したが、**ANN vs ctrl の状態差（atr 4.88 vs 2.39 = 2.0 倍）
       には同じ刃を当てていない**。時刻 FE は atr を吸収しない。
       攻撃 = (a) ANN 自身のプラセボ族による経験 p ／(b) 別の在外分割 ／(c) コスト ×2/×3
              ／(d) 状態（atr・risk）統制＋atr マッチ ctrl ／(e) jackknife（日・上位本）／(f) 多重検定補正。

=== 事前固定（数字を見る前・この docstring が正本・seed 20261120・乱数は caliper マッチのみ） ===
データ: c56 と完全同一（data/macro/XAU_m5_close.npz・data/refute_c4_scan_paths_2010_2026.json・FOMC/CPI csv・NFP c24v2）。
  新規データ取得なし・多年 scan なし・MT5 なし・外部通信なし・M5 原本なし。読取専用。
推定器: c56 と完全同一（Rs = R + (FEED_TOL/risk)·1{SL,TP}・時刻 FE 24・建玉日クラスタ se・ctrl 同定義）。
  c56 の複製 assert をそのまま継承（2166／786／937・外 ANN n 138 β +0.514・UJ n 280 β +0.089）。合わなければ停止。

プラセボ族の定義（T1 の核・事前固定）:
  OFF7  = {±7, ±14, ±21, ±28, ±35, ±42, ±49, ±56} 日（16 draw・**曜日と ET スロットを保存**＝正しい帰無）
  OFFnz = {±3, ±4, ±5, ±10, ±11, ±17, ±18, ±24, ±25, ±31, ±32, ±38, ±39, ±45} 日（28 draw・曜日を壊す＝参照）
  腕ごとに c56 と同一の構成（PL = 窓 ∧ ~isevday ∧ 月〜金 ∧ ~4σ窓 ∧ ~ANN、ctrl2 = ctrl ∧ ~PL）。
  λ(腕, 族) = sd(β_pl, ddof=1) / mean(se_pl)   ← 「帰無 sd / 名目 se」の直接推定。
  判定は **oth 腕 × OFF7** を正本とする（c56 の −7 日はこの族の 1 draw）。

判定規則（全部事前・観測前に固定・boolean から合成）:
  BREAK-1（T1 = c56 の λ 1.25〜1.3）: λ_oth7 ≤ 1.10 → **T1 破れ（c56 は過剰補正）**
                                      λ_oth7 ≥ 1.20 → **T1 生存（c56 は正しい・family の t は要読み替え）**
                                      その間 → inconclusive。族 draw 数 <12 なら判定しない。
  BREAK-2（−7 日の特異性）: oth −7 日の |t| が OFF7 族 16 draw 中で順位 1 位 ∧ 2 位の |t| の 1.5 倍以上
                            → 「−7 日は実在の構造」（c56 次の枝 (e) に根拠）。それ以外 → **単なる裾 1 draw**。
  BREAK-3（T2a = ANN の経験 p）: ANN 腕のプラセボ族（OFF7∪OFFnz, ≥30 draw）から両側経験 p を計算。
                            p_emp > 0.05 → **ANN の t 4.02 は破れ**。p_emp ≤ 0.05 → ANN 生存。
  BREAK-4（T2b = 在外分割の恣意性）: 代替分割 3 本 = ①2010-17 / 2018-26 ②偶数年 / 奇数年 ③2010-15 / 2016-26。
                            後半（または偶/奇の両側）で n_ANN ≥ 60 のセルのうち「β>0 ∧ t≥2」を満たすのが
                            3 本中 ≤1 本 → **ANN は 2021-26 という窓選択の産物（破れ）**。≥2 本 → 生存。
  BREAK-5（T2c = コスト）: Rs_k = R − (k−1)·(TRIG_SPREAD/risk) + (FEED_TOL/risk)·1{SL,TP}, k=1,2,3
                            （k=1 が c56 の主）。k=3 で β_ANN < +0.257 または t < 2 → **コスト脆弱（破れ）**。
                            ※方向の注意を事前に明記: ctrl の risk 平均は ANN より小さいので、一律コストは
                              R 単位で ctrl をより強く削り β を**上げ得る**。上がった場合は「コスト試験は
                              この contrast では保守的でない」と記録し、破れの根拠には使わない。
  BREAK-6（T2d = 状態不揃い・本命）: ① log(atr)・log(risk)・b を回帰に追加
                                    ② ctrl を ANN の atr 分布に caliper マッチ（log atr ±0.10・同 ET 時・seed 20261120）
                            ①または②で β_ANN < +0.257（= 元の 0.5 倍）または t < 2 → **ANN は「荒い状態」の症状と
                            区別できない（破れ）**。両方で β ≥ +0.257 ∧ t ≥ 2 → 生存。
  BREAK-7（jackknife）: ANN の建玉日を 1 日ずつ落とした β の最小値 < +0.257、または上位 3 本除去で
                        未調整 Δμ が < +0.257 → **裾依存（破れ）**。
  BREAK-8（多重検定）: family の主要セル（c45 3 腕×3 窓 ＝9・c55 4 会場・c56 4 腕×3 窓 ＝12・計 25）に対し
                        ANN の名目 p を Bonferroni / BH(0.05) で補正。補正後も有意でなければ破れ。
総合判定語: 「survived / broken / split / inconclusive」を上の boolean から合成する（勝手に書かない）。

事前の予測（外す覚悟で書く）: λ_oth7 ≈ 1.0〜1.15（T1 は破れる側・2 draw からの 1.25-1.3 は裾の読み過ぎ）。
  ANN は BREAK-3/4/7/8 は通る。**BREAK-6 が本命で、ここで β が落ちる**（atr 2 倍差は時刻 FE で吸収されない）。

自分の破りの既知の弱点（結果に関わらず残す）: プラセボ族の 16/28 draw は互いに独立でない（同じ scan 本を
  重複利用・隣接 offset は窓が重なる）→ λ の se は見かけより大きい。caliper マッチは ctrl を減らし se を上げる
  （β 低下と検出力低下が交絡する）ので、②は「β の大きさ」ではなく「β が ctrl 構成で動くか」として読む。
出力 data/refute_c56_empirical_null.md。発注なし・本番編集なし・書込は AUREL_RESEARCH 配下のみ。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c56_empirical_null.md"); L = []
NY = "America/New_York"; SEED = 20261120
ZMAIN = 5.0; W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0
WD = "月火水木金土日"
US2 = {(8, 20), (8, 25), (9, 35), (9, 40)}
OFF7 = [-56, -49, -42, -35, -28, -21, -14, -7, 7, 14, 21, 28, 35, 42, 49, 56]
OFFNZ = [-45, -39, -38, -32, -31, -25, -24, -18, -17, -11, -10, -5, -4, -3,
         3, 4, 5, 10, 11, 17, 18, 24, 25, 31, 32, 38, 39, 45]

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

say("# [REFUTE 09:30] c56 の支え T1（帰無 sd 1.25-1.3×・プラセボ 2 draw 由来）と T2（外 ANN +0.513 t 4.02）を壊す")
say(f"- 事前固定は docstring・seed {SEED}・推定器/データは c56 と完全同一・新規データなし")
say("")

# ---------- 暦（c56 と同一） ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ANN = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC_ANN, 14, 0)
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

# ---------- npz（c56 と同一） ----------
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
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
cand = nf3 & trading & np.isfinite(sig)
z = np.abs(r) / sig

def decluster(mask):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= DECL:
            keep.append(i); last = ts[i]
    return np.array(keep, int)

J4 = decluster(cand & (z >= 4.0)); J5 = decluster(cand & (z >= ZMAIN))
isevbar = etdate.isin(evdays)
ok5 = ~np.asarray(isevbar[J5]); sch5 = (mn[J5] % 15 == 0)
SJ5 = J5[ok5 & sch5]; UJ5 = J5[ok5 & ~sch5]
is_us2 = np.array([(int(hr[i]), int(mn[i])) in US2 for i in UJ5], bool)
UJ_US2 = UJ5[is_us2]; UJ_OTH = UJ5[~is_us2]
assert len(J5) == 2166 and len(SJ5) == 786 and len(UJ5) == 937, f"c45 事象集合の複製に失敗 {len(J5)}/{len(SJ5)}/{len(UJ5)}"
say(f"- 事象 複製 assert OK: 5σ {len(J5)}／SJ {len(SJ5)}／UJ {len(UJ5)} → US2 {len(UJ_US2)}・oth {len(UJ_OTH)}")

# ---------- scan 本（c56 と同一） ----------
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]; TSPR = d["frozen"]["TRIG_SPREAD"]
tr = pd.DataFrame(d["trades"])
tr["dec"] = tr["exit"].isin(["SL", "TP"])
tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
for k in (2, 3):
    tr[f"Rs{k}"] = tr["R"] - (k - 1) * (TSPR / tr["risk"]) + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
tr["hh"] = e_ny.hour.to_numpy(); tr["wd"] = e_ny.weekday.to_numpy()
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize())
tr["isevday"] = tr.day.isin(evdays)
tr["latr"] = np.log(np.maximum(tr.atr.to_numpy(float), 1e-6))
tr["lrisk"] = np.log(np.maximum(tr.risk.to_numpy(float), 1e-6))

def inwin(t0s, span=SPAN, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    if len(t0s) == 0: return np.zeros(len(et_), bool), np.full(len(et_), np.nan)
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span), t0s[pos]

m_nfp, p_nfp = inwin(t_nfp); m_fomc, p_fomc = inwin(t_fomc)
tr["ANN"] = m_nfp | m_fomc
tsf = ts.astype(float)
m_sj, _ = inwin(tsf[SJ5] + 300); m_uj, p_uj = inwin(tsf[UJ5] + 300)
tr["SJ"] = m_sj & ~tr.ANN & ~tr.isevday
tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
last_is_us2 = np.isin((p_uj - 300).astype(np.int64), ts[UJ_US2])
tr["US2"] = tr.UJ & last_is_us2; tr["OTH"] = tr.UJ & ~last_is_us2
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN
tr["uj_min"] = (et_ - np.where(tr.UJ, p_uj - 300, np.nan)) / 60.0

# ---------- 推定器（c56 と同一） ----------
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    dm = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return dm, dm / se if se > 0 else np.nan

def ols_cluster(y, X, g):
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    df = pd.DataFrame(X * e[:, None]); df["g"] = np.asarray(g)
    S = df.groupby("g").sum().to_numpy(); G = S.shape[0]
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (G / max(G - 1, 1))
    return beta, V, G

def fe_fit(o, groups, ycol="Rs", extra=()):
    hours = np.arange(24)
    H = np.column_stack([(o.hh.to_numpy() == h).astype(float) for h in hours[1:]])
    Gm = np.column_stack([o[c].to_numpy().astype(float) for c in groups])
    blocks = [np.ones(len(o)), Gm, H]
    if extra:
        blocks.append(np.column_stack([o[c].to_numpy(float) for c in extra]))
    X = np.column_stack(blocks); y = o[ycol].to_numpy(float)
    beta, V, G = ols_cluster(y, X, o.day.to_numpy())
    res = {c: (beta[1 + i], math.sqrt(max(V[1 + i, 1 + i], 0)), int(o[c].sum())) for i, c in enumerate(groups)}
    return res, V, G

def contrast(V, i, j):
    cv = np.zeros(V.shape[0]); cv[1 + i] = 1; cv[1 + j] = -1
    return math.sqrt(max(cv @ V @ cv, 0))

def sub(lo_, hi_): return tr[(tr.year >= lo_) & (tr.year <= hi_)]
def tstr(b, s): return f"{b:+.3f} ({(b/s if s > 0 else float('nan')):+.2f})"

# ---------- 複製 assert（c56 主表） ----------
o = sub(2021, 2026); sel = o[o.ANN | o.SJ | o.UJ | o.ctrl]
res0, V0, G0 = fe_fit(sel, ["ANN", "SJ", "UJ"])
bA0, sA0, nA0 = res0["ANN"]; bU0, sU0, nU0 = res0["UJ"]
assert nA0 == 138 and nU0 == 280 and abs(bA0 - 0.514) < 0.0015 and abs(bU0 - 0.089) < 0.0015, \
    f"c45/c56 主表の複製に失敗 {nA0}/{bA0}/{nU0}/{bU0}"
say(f"- 主表 複製 assert OK: 外 ANN n {nA0} β {tstr(bA0, sA0)}・UJ n {nU0} β {tstr(bU0, sU0)}")
o4 = sub(2021, 2026); s4 = o4[o4.ANN | o4.SJ | o4.US2 | o4.OTH | o4.ctrl]
r4, V4, G4 = fe_fit(s4, ["ANN", "SJ", "US2", "OTH"])
bA, sA, nA = r4["ANN"]; bo, so, no = r4["OTH"]; b2, s2, n2 = r4["US2"]
dAO = bA - bo; sAO = contrast(V4, 0, 3)
HALF = 0.5 * bA
say(f"- c56 4 腕 複製: ANN {tstr(bA, sA)} n {nA}／US2 {tstr(b2, s2)} n {n2}／oth {tstr(bo, so)} n {no}／ANN−oth {tstr(dAO, sAO)}")
say(f"- 閾 0.5·β_ANN = {HALF:+.3f}・FEED_TOL {FT}・TRIG_SPREAD {TSPR}")
say("")

# =================================================================
# BREAK-1/2: プラセボ族で帰無 sd を実測（T1 = c56 の λ 1.25-1.3）
# =================================================================
say("## BREAK-1/2 プラセボ族 44 draw で窓集合型 Δμ の帰無分布を実測（c56 は 2 draw で λ=1.25-1.3 と読んだ）")

def placebo_arm(ev_idx_or_t0, offs, era=(2021, 2026), is_bars=True, exclude_real=None):
    """c56 と同一構成の偽窓: PL = 窓 ∧ ~isevday ∧ 月〜金 ∧ ~4σ窓 ∧ ~ANN、ctrl2 = ctrl ∧ ~PL"""
    rows = []
    base = tsf[ev_idx_or_t0] + 300 if is_bars else np.asarray(ev_idx_or_t0, float)
    for sh in offs:
        mp, _ = inwin(base, off=sh * 86400.0)
        pl = mp & ~tr.isevday.to_numpy() & (tr.wd.to_numpy() <= 4) & ~m_any4 & ~tr.ANN.to_numpy()
        if exclude_real is not None:
            pl = pl & ~exclude_real
        t2 = tr.assign(PL=pl)
        oo = t2[(t2.year >= era[0]) & (t2.year <= era[1])]
        oo = oo.assign(ctrl2=oo.ctrl & ~oo.PL)
        s = oo[oo.PL | oo.ctrl2]
        if int(s.PL.sum()) < 10:
            continue
        rr, VV, GG = fe_fit(s, ["PL"])
        b, se, n = rr["PL"]
        rows.append(dict(shd=sh, b=b, se=se, n=n, t=(b / se if se > 0 else np.nan), days=int(s[s.PL].day.nunique())))
    return pd.DataFrame(rows)

def lam_report(df, label):
    if len(df) < 3:
        say(f"- {label}: draw {len(df)} 本（<3）→ λ 計算せず"); return np.nan
    lam = df.b.std(ddof=1) / df.se.mean()
    say(f"- **{label}**: draw {len(df)}・β 平均 {df.b.mean():+.4f}・**β 実測 sd {df.b.std(ddof=1):.4f}**・"
        f"名目 se 平均 {df.se.mean():.4f} → **λ = {lam:.3f}**・|t| 平均 {df.t.abs().mean():.2f}・"
        f"|t|≥2 の割合 {(df.t.abs() >= 2).mean()*100:.0f}%（名目期待 4.6%）・n 本 中央値 {df.n.median():.0f}")
    return lam

PL = {}
for arm, idxs in (("oth", UJ_OTH), ("US2", UJ_US2)):
    for fam, offs in (("OFF7", OFF7), ("OFFnz", OFFNZ)):
        PL[(arm, fam)] = placebo_arm(idxs, offs)
lam_oth7 = lam_report(PL[("oth", "OFF7")], "oth × OFF7（曜日保存・判定正本）")
lam_othnz = lam_report(PL[("oth", "OFFnz")], "oth × OFFnz（曜日非保存・参照）")
lam_us27 = lam_report(PL[("US2", "OFF7")], "US2 × OFF7")
lam_us2nz = lam_report(PL[("US2", "OFFnz")], "US2 × OFFnz")
say("")
say("### oth × OFF7 の全 draw（c56 が引いた −7 日はこの族の 1 本）")
say("| shift 日 | n 本 | 事象日 | β | se | t |")
say("|---|---|---|---|---|---|")
for _, q in PL[("oth", "OFF7")].sort_values("shd").iterrows():
    mark = " ← c56 が引いた draw" if int(q.shd) == -7 else ""
    say(f"| {int(q.shd):+d} | {int(q.n)} | {int(q.days)} | {q.b:+.3f} | {q.se:.3f} | **{q.t:+.2f}**{mark} |")
say("")
d7 = PL[("oth", "OFF7")]
srt = d7.reindex(d7.t.abs().sort_values(ascending=False).index)
rank_m7 = int(np.where(srt.shd.to_numpy() == -7)[0][0]) + 1 if (-7 in set(srt.shd)) else -1
top1 = float(srt.t.abs().iloc[0]); top2 = float(srt.t.abs().iloc[1]) if len(srt) > 1 else np.nan
say(f"- 順位: |t| 最大 {srt.shd.iloc[0]:+.0f} 日 {top1:.2f}・2 位 {srt.shd.iloc[1]:+.0f} 日 {top2:.2f}・"
    f"**−7 日の順位 = {rank_m7} / {len(d7)}**")
b1_break = (lam_oth7 <= 1.10) if len(d7) >= 12 else None
b1_surv = (lam_oth7 >= 1.20) if len(d7) >= 12 else None
say(f"- 条件 λ_oth7 ≤ 1.10 → 観測 {lam_oth7:.3f} → {b1_break}")
say(f"- 条件 λ_oth7 ≥ 1.20 → 観測 {lam_oth7:.3f} → {b1_surv}")
say(f"- **BREAK-1 = {'T1 破れ（c56 は過剰補正）' if b1_break else ('T1 生存（c56 は正しい）' if b1_surv else 'inconclusive')}**")
b2 = (rank_m7 == 1) and (top1 >= 1.5 * top2)
say(f"- 条件 −7 日が 1 位 → {rank_m7 == 1}・条件 1 位 ≥ 1.5×2 位 → {top1 >= 1.5*top2 if np.isfinite(top2) else False}")
say(f"- **BREAK-2 = {'−7 日は実在の構造' if b2 else '−7 日は単なる裾 1 draw（c56 次の枝 (e) は追う価値なし）'}**")
say("")

# λ で読み替えた family の t
lam_use = lam_oth7 if np.isfinite(lam_oth7) else 1.0
say("### λ 実測値で読み替えた family の主要 t（c56 は 1.25-1.3 で割っていた）")
say("| セル | 名目 β (t) | λ 補正 t = t/λ | c56 の 1.3 補正 t |")
say("|---|---|---|---|")
for nm, bb, ss in (("外 ANN", bA, sA), ("外 oth", bo, so), ("外 US2", b2, s2), ("外 ANN−oth", dAO, sAO)):
    tn = bb / ss
    say(f"| {nm} | {bb:+.3f} ({tn:+.2f}) | **{tn/lam_use:+.2f}** | {tn/1.3:+.2f} |")
say("")

# =================================================================
# BREAK-3: ANN 自身のプラセボ族 → 経験 p
# =================================================================
say("## BREAK-3 ANN のプラセボ族（NFP/FOMC t0 をずらす・OFF7∪OFFnz 44 draw）→ 外 ANN の経験 p")
ann_t0 = np.concatenate([t_nfp[np.isfinite(t_nfp)], t_fomc[np.isfinite(t_fomc)]])
PLA = placebo_arm(ann_t0, OFF7 + OFFNZ, is_bars=False, exclude_real=tr.ANN.to_numpy())
lam_ann = lam_report(PLA, "ANN × (OFF7∪OFFnz)")
if len(PLA) >= 30:
    nul = PLA.b.to_numpy()
    p_emp = (np.abs(nul) >= abs(bA)).mean()
    p_emp_adj = (np.sum(np.abs(nul) >= abs(bA)) + 1) / (len(nul) + 1)
    say(f"- 外 β_ANN {bA:+.3f}・プラセボ族の |β| 最大 {np.abs(nul).max():.3f}（shift {int(PLA.iloc[int(np.argmax(np.abs(nul)))].shd):+d} 日）")
    say(f"- 両側経験 p = {p_emp:.4f}（+1 補正 {p_emp_adj:.4f}）・族 {len(nul)} draw")
    b3_break = p_emp_adj > 0.05
    say(f"- 条件 p_emp > 0.05 → {b3_break}")
    say(f"- **BREAK-3 = {'ANN の t 4.02 は破れ' if b3_break else 'ANN は経験帰無でも生存'}**")
else:
    b3_break = None; p_emp_adj = np.nan
    say(f"- draw {len(PLA)} < 30 → 判定しない（inconclusive）")
say("")

# =================================================================
# BREAK-4: 別の在外分割
# =================================================================
say("## BREAK-4 別の在外分割で ANN は残るか（c56 の 2010-20 / 2021-26H1 は窓選択か）")
say("| 分割 | セル | n 本 / 日 | β_ANN (日cl t) | MDE 2se | β>0 ∧ t≥2 |")
say("|---|---|---|---|---|---|")
def fit_ann(o):
    s = o[o.ANN | o.SJ | o.US2 | o.OTH | o.ctrl]
    if int(s.ANN.sum()) < 10: return None
    rr, VV, GG = fe_fit(s, ["ANN", "SJ", "US2", "OTH"])
    return rr["ANN"] + (int(s[s.ANN].day.nunique()),)
SPLITS = [("①2010-17/2018-26", [("2010-17", tr[(tr.year >= 2010) & (tr.year <= 2017)]), ("2018-26", tr[(tr.year >= 2018) & (tr.year <= 2026)])]),
          ("②偶数年/奇数年", [("偶数年", tr[tr.year % 2 == 0]), ("奇数年", tr[tr.year % 2 == 1])]),
          ("③2010-15/2016-26", [("2010-15", tr[(tr.year >= 2010) & (tr.year <= 2015)]), ("2016-26", tr[(tr.year >= 2016) & (tr.year <= 2026)])])]
split_pass = []
for sname, cells in SPLITS:
    oks = []
    for cname, oo in cells:
        f = fit_ann(oo)
        if f is None:
            say(f"| {sname} | {cname} | <10 | — | — | — |"); continue
        bb, ss, nn, dd = f; tt_ = bb / ss if ss > 0 else np.nan
        ok = (bb > 0) and (tt_ >= 2) and (nn >= 60)
        if nn >= 60: oks.append(ok)
        say(f"| {sname} | {cname} | {nn} / {dd} | **{tstr(bb, ss)}** | {2*ss:.3f} | {ok}（n≥60 {nn >= 60}） |")
    split_pass.append(any(oks) if oks else False)
n_split_ok = sum(1 for x in split_pass if x)
b4_break = n_split_ok <= 1
say(f"- 3 分割のうち「β>0 ∧ t≥2（n≥60）」を満たす分割 = {n_split_ok} / 3")
say(f"- 条件 ≤1 → {b4_break}")
say(f"- **BREAK-4 = {'ANN は窓選択の産物（破れ）' if b4_break else 'ANN は分割に頑健'}**")
say("")

# =================================================================
# BREAK-5: コスト ×2 / ×3
# =================================================================
say("## BREAK-5 コスト ×2 / ×3（TRIG_SPREAD を 1 回／2 回 追加で引く・外 2021-26H1）")
say("| コスト | β_ANN (t) | β_US2 (t) | β_oth (t) | ANN−oth (t) | ctrl 平均 Rs | ANN risk 平均 / ctrl risk 平均 |")
say("|---|---|---|---|---|---|---|")
cost_rows = {}
for k, yc in ((1, "Rs"), (2, "Rs2"), (3, "Rs3")):
    rr, VV, GG = fe_fit(s4, ["ANN", "SJ", "US2", "OTH"], ycol=yc)
    dd_ = rr["ANN"][0] - rr["OTH"][0]; sd_ = contrast(VV, 0, 3)
    C = s4[s4.ctrl]
    cost_rows[k] = rr["ANN"]
    say(f"| ×{k} | **{tstr(*rr['ANN'][:2])}** | {tstr(*rr['US2'][:2])} | {tstr(*rr['OTH'][:2])} | {tstr(dd_, sd_)} | "
        f"{C[yc].mean():+.3f} | {s4[s4.ANN].risk.mean():.2f} / {C.risk.mean():.2f} |")
bA3, sA3, _ = cost_rows[3]; tA3 = bA3 / sA3 if sA3 > 0 else np.nan
b5_break = (bA3 < 0.257) or (tA3 < 2)
say(f"- 条件 ×3 で β_ANN < +0.257 → {bA3 < 0.257}・条件 t < 2 → {tA3 < 2}")
say(f"- **BREAK-5 = {'コスト脆弱（破れ）' if b5_break else 'コスト ×3 でも生存'}**"
    f"{'　※事前注意どおり β が上がった → この contrast でコスト試験は保守的でない（破れの根拠に使わない）' if bA3 > bA else ''}")
say("")

# =================================================================
# BREAK-6: 状態（atr / risk）不揃い ← 本命
# =================================================================
say("## BREAK-6（本命）状態不揃い: ANN vs ctrl は atr 2 倍違う。時刻 FE は atr を吸収しない")
C = s4[s4.ctrl]; A = s4[s4.ANN]
say(f"- 外: ANN atr 平均 {A.atr.mean():.2f}（中央 {A.atr.median():.2f}）vs ctrl {C.atr.mean():.2f}（{C.atr.median():.2f}）= **{A.atr.mean()/C.atr.mean():.2f} 倍**・"
    f"risk {A.risk.mean():.2f} vs {C.risk.mean():.2f}・b {A.b.mean():.2f} vs {C.b.mean():.2f}")
say("")
say("### ⑥-① log(atr)・log(risk)・b を統制に追加")
say("| 統制 | β_ANN (t) | β_US2 (t) | β_oth (t) | ANN−oth (t) |")
say("|---|---|---|---|---|")
ctl_rows = {}
for nm, extra in (("時刻 FE のみ（c56 主）", ()), ("+ log atr", ("latr",)), ("+ log atr + log risk", ("latr", "lrisk")),
                  ("+ log atr + log risk + b", ("latr", "lrisk", "b"))):
    rr, VV, GG = fe_fit(s4, ["ANN", "SJ", "US2", "OTH"], extra=extra)
    dd_ = rr["ANN"][0] - rr["OTH"][0]; sd_ = contrast(VV, 0, 3)
    ctl_rows[nm] = rr["ANN"]
    say(f"| {nm} | **{tstr(*rr['ANN'][:2])}** | {tstr(*rr['US2'][:2])} | {tstr(*rr['OTH'][:2])} | {tstr(dd_, sd_)} |")
bA_c, sA_c, _ = ctl_rows["+ log atr + log risk + b"]; tA_c = bA_c / sA_c if sA_c > 0 else np.nan
say("")
say("### ⑥-② ctrl を ANN の log atr に caliper マッチ（±0.10・同 ET 時・復元なし・seed 20261120）")
rng = np.random.default_rng(SEED)
pool = C.copy()
picked = []
for _, a in A.iterrows():
    cands = pool[(pool.hh == a.hh) & (np.abs(pool.latr - a.latr) <= 0.10)]
    cands = cands.drop(index=[i for i in picked if i in cands.index], errors="ignore")
    if len(cands) == 0: continue
    picked.append(int(rng.choice(cands.index.to_numpy())))
MC = C.loc[sorted(set(picked))]
say(f"- マッチ成立 {len(MC)} / ANN {len(A)}・マッチ後 ctrl atr 平均 {MC.atr.mean():.2f}（ANN {A.atr.mean():.2f}・"
    f"差 {A.atr.mean()-MC.atr.mean():+.2f}）・risk {MC.risk.mean():.2f} vs {A.risk.mean():.2f}")
if len(MC) >= 40:
    sm = pd.concat([A.assign(ANNm=True), MC.assign(ANNm=False)])
    rr, VV, GG = fe_fit(sm, ["ANNm"])
    bm, sm_, nm_ = rr["ANNm"]; tm = bm / sm_ if sm_ > 0 else np.nan
    dmw, tw = welch(A.Rs, MC.Rs)
    say(f"- **atr マッチ ctrl に対する β_ANN = {tstr(bm, sm_)}**（n {nm_}・マッチ ctrl {len(MC)}・MDE {2*sm_:.3f}）・未調整 Welch Δμ {dmw:+.3f} ({tw:+.2f})")
    say(f"- 参考 非マッチ ctrl に対する未調整 Welch Δμ {welch(A.Rs, C.Rs)[0]:+.3f} ({welch(A.Rs, C.Rs)[1]:+.2f})")
else:
    bm, sm_, tm = np.nan, np.nan, np.nan
    say(f"- マッチ {len(MC)} < 40 → 判定に使わない")
b6_1 = (bA_c < 0.257) or (tA_c < 2)
b6_2 = (bm < 0.257) or (tm < 2) if np.isfinite(bm) else None
b6_break = bool(b6_1) or bool(b6_2)
say(f"- 条件① 統制追加で β<+0.257 or t<2 → {b6_1}（β {bA_c:+.3f} t {tA_c:+.2f}）")
say(f"- 条件② atr マッチで β<+0.257 or t<2 → {b6_2}（β {bm:+.3f} t {tm:+.2f}）")
say(f"- **BREAK-6 = {'ANN は「荒い状態」と区別できない（破れ）' if b6_break else 'ANN は状態統制後も生存'}**")
say("")

# =================================================================
# BREAK-7: jackknife
# =================================================================
say("## BREAK-7 jackknife（ANN の建玉日 1 日ずつ除去・上位本除去）")
days = sorted(A.day.unique())
jb = []
for dd in days:
    s = s4[~((s4.ANN) & (s4.day == dd))]
    s = s[s.ANN | s.SJ | s.US2 | s.OTH | s.ctrl]
    rr, VV, GG = fe_fit(s, ["ANN", "SJ", "US2", "OTH"])
    jb.append((dd, rr["ANN"][0], rr["ANN"][0] / rr["ANN"][1] if rr["ANN"][1] > 0 else np.nan, int(((A.day == dd)).sum())))
JB = pd.DataFrame(jb, columns=["day", "b", "t", "n_drop"]).sort_values("b")
say(f"- ANN 建玉日 {len(days)} 日・jackknife β の 範囲 **{JB.b.min():+.3f} 〜 {JB.b.max():+.3f}**・中央 {JB.b.median():+.3f}")
say("- 最も効いている 5 日（除くと β が最も下がる）: " + " ".join(
    f"{pd.Timestamp(q.day).date()}(β{q.b:+.3f} t{q.t:+.2f} n{int(q.n_drop)})" for _, q in JB.head(5).iterrows()))
srtA = A.Rs.sort_values(ascending=False)
rem_txt = []
for k in (1, 3, 5):
    dmk, twk = welch(A.drop(srtA.index[:k]).Rs, C.Rs)
    rem_txt.append(f"上位{k}除去 Δμ {dmk:+.3f}({twk:+.2f})")
dm3 = welch(A.drop(srtA.index[:3]).Rs, C.Rs)[0]
say("- 未調整 Δμ: 全部 " + f"{welch(A.Rs, C.Rs)[0]:+.3f}・" + "・".join(rem_txt) +
    f"・ANN Rs 中央値 {A.Rs.median():+.2f}（ctrl {C.Rs.median():+.2f}）・ANN の上位 3 本 {' '.join(f'{v:+.2f}' for v in srtA.head(3))}")
b7_break = (JB.b.min() < 0.257) or (dm3 < 0.257)
say(f"- 条件 jackknife 最小 β < +0.257 → {JB.b.min() < 0.257}・条件 上位 3 除去 Δμ < +0.257 → {dm3 < 0.257}")
say(f"- **BREAK-7 = {'裾/単日依存（破れ）' if b7_break else '裾に依らない'}**")
say("")

# =================================================================
# BREAK-8: 多重検定補正
# =================================================================
say("## BREAK-8 多重検定補正（family 主要セル 25 = c45 3腕×3窓 + c55 4会場 + c56 4腕×3窓）")
from math import erfc
def p2(t): return erfc(abs(t) / math.sqrt(2.0))
tA_nom = bA / sA
pA_nom = p2(tA_nom); pA_lam = p2(tA_nom / lam_use)
M = 25
say(f"- 外 ANN 名目 t {tA_nom:+.2f} → p {pA_nom:.2e}・Bonferroni(M={M}) p {min(1, pA_nom*M):.2e} → <0.05 {min(1, pA_nom*M) < 0.05}")
say(f"- λ 実測 {lam_use:.3f} で補正した t {tA_nom/lam_use:+.2f} → p {pA_lam:.2e}・Bonferroni p {min(1, pA_lam*M):.2e} → <0.05 {min(1, pA_lam*M) < 0.05}")
if np.isfinite(p_emp_adj):
    say(f"- 経験 p（BREAK-3）{p_emp_adj:.4f}・Bonferroni p {min(1, p_emp_adj*M):.4f} → <0.05 {min(1, p_emp_adj*M) < 0.05}")
b8_break = min(1, pA_lam * M) >= 0.05
say(f"- **BREAK-8 = {'多重検定で消える（破れ）' if b8_break else '多重検定後も生存'}**")
say("")

# =================================================================
# 総合
# =================================================================
say("## 総合判定（boolean から合成・勝手に書かない）")
rows = [("BREAK-1 T1=帰無 sd 1.25-1.3", "破れ" if b1_break else ("生存" if b1_surv else "inconclusive"), f"λ_oth7 = {lam_oth7:.3f}（44 draw 実測）"),
        ("BREAK-2 −7 日の特異性", "実在" if b2 else "裾 1 draw", f"順位 {rank_m7}/{len(d7)}・1 位 {top1:.2f} vs 2 位 {top2:.2f}"),
        ("BREAK-3 ANN 経験 p", "破れ" if b3_break else "生存", f"p_emp {p_emp_adj:.4f}（{len(PLA)} draw）"),
        ("BREAK-4 別の在外分割", "破れ" if b4_break else "生存", f"{n_split_ok}/3 分割で β>0 ∧ t≥2"),
        ("BREAK-5 コスト ×3", "破れ" if b5_break else "生存", f"β {bA3:+.3f} (t {tA3:+.2f})"),
        ("BREAK-6 状態（atr）不揃い", "破れ" if b6_break else "生存", f"統制後 β {bA_c:+.3f} (t {tA_c:+.2f})・atr マッチ β {bm:+.3f} (t {tm:+.2f})"),
        ("BREAK-7 jackknife/裾", "破れ" if b7_break else "生存", f"最小 β {JB.b.min():+.3f}・上位 3 除去 Δμ {dm3:+.3f}"),
        ("BREAK-8 多重検定", "破れ" if b8_break else "生存", f"λ 補正 Bonferroni p {min(1, pA_lam*M):.2e}")]
say("| 攻撃 | 結果 | 数字 |")
say("|---|---|---|")
for a, b, c in rows: say(f"| {a} | **{b}** | {c} |")
t2_breaks = [b3_break, b4_break, b5_break, b6_break, b7_break, b8_break]
n_t2_break = sum(1 for x in t2_breaks if x is True)
say("")
say(f"- T1（c56 の帰無 sd 係数）: {'**broken**' if b1_break else ('**survived**' if b1_surv else '**inconclusive**')}")
say(f"- T2（外 ANN +0.513）: 6 攻撃のうち破れ {n_t2_break} 本 → "
    f"{'**broken**' if n_t2_break >= 2 else ('**weakened（1 本破れ）**' if n_t2_break == 1 else '**survived**')}")
say("")
say(f"- 実行時間 {time.time()-T0:.1f} s・seed {SEED}（乱数は caliper マッチのみ）")
say("- 副作用: 読取のみ（npz 1・json 1・csv 2）。書込は data/refute_c56_empirical_null.md のみ。発注/デモ発注/本番編集/プロセス接触/MT5/プロップ/秘密 なし。外部通信なし。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
