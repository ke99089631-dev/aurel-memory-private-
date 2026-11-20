# -*- coding: utf-8 -*-
"""
[反証レーン / 2026-11-20 09:30 part C] part B の **B-9 の破れが私の交絡でないか**を決着させる。

part B の確定事実:
  λ_ANN = 0.986（594 draw）・λ_US2 = 1.225・λ_oth = 1.385（外）／0.981（在・FAM7 84 draw）
  B-8c: ANN 名目 p 5.94e-5 ×25 = 1.49e-3 → 生存
  B-9 : ANN × FAM_ALL 594 draw の β 族に |β| ≥ 0.513 が 4 本（最大 0.616・shift −110 日）→ p_emp 0.0084 ×25 = 0.21 → **破れ**
  B-10: ANN−oth 両腕ずらし 84 draw・λ_AO 1.122・p_emp 0.0588 → (b) 脚 **破れ**（ただし λ 補正 t +2.34 ≥ 2 は True＝符号が逆）

B-9 に私が入れた交絡（自己申告・ここで潰す）:
  プラセボ腕は c56 の構成（PL = 窓 ∧ ~isevday ∧ 月〜金 ∧ ~4σ窓 ∧ ~ANN）だが、**実 ANN 腕にはこの絞りが無い**。
  結果 プラセボ draw の n 本 中央値 58 vs 実 ANN n 138。n が小さい draw は se が大きく |β| が広く散る。
  → 「n 138 の β を n≈58 の帰無族と比べた」＝**破れの側に偏る**。しかも part B で |t|≥2 の割合は 4.5%
     （名目 4.6% と一致）＝ t スケールでは帰無はほぼ名目どおり。β スケールと t スケールで結論が逆になる。

=== part C の事前固定（数字を見る前・seed 20261120・乱数未使用） ===
データ・推定器・ctrl・複製 assert は c56 / part A / part B と完全同一。読取専用・新規データなし。
族 FAM_ALL = 3 ≤ |d| ≤ 300 の全整数日（最大 596 draw）。
判定規則（事前・boolean から合成）:
  C-1（studentize = n 非依存の正しい統計量）: p_t = (#{|t_pl| ≥ |t_ANN|} + 1)/(N+1)。
        t は n を正規化するので、draw ごとの n 差に影響されない。p_t × 25 ≥ 0.05 → **破れ**／< 0.05 → **生存**。
  C-2（n マッチ部分族）: n ∈ [110, 170]（実 ANN 138 の ±約 25%）の draw のみで β 族の p_emp。
        部分族 draw ≥ 60 を要件。p × 25 ≥ 0.05 → **破れ**／< 0.05 → **生存**。draw < 60 なら判定せず。
  C-3（構成マッチ族）: プラセボを **実 ANN 腕と同じ構成**で作る（偽窓 ∧ ~実 ANN 窓 のみ・isevday/4σ の絞りを外す）
        → n が 138 近傍に揃う。β 版・t 版の両方で p_emp。両方 ×25 ≥ 0.05 → **破れ**／片方でも < 0.05 → **生存側**。
  C-4（外れ draw の正体・診断）: part B で |β| 最大だった shift −110 日 を含む 上位 5 draw の n・se・t・
        建玉日数を印字。n が小さい draw に偏っていれば C-2/C-3 の必要性の直接証拠（記述）。
  **総合規則（事前固定・ここが本体）**: C-1・C-2・C-3 のうち「生存」が 2 つ以上 → **B-9 の破れは私の交絡＝取り下げ**
        （ANN は T2 として生存）。「破れ」が 2 つ以上 → **B-9 の破れは本物（ANN は broken）**。1:1:判定不能 → inconclusive。
事前の予測: C-1 生存（|t|≥2 が 4.5% ＝ t 族は名目どおりなので |t|≥4.02 はほぼ出ない）・C-3 生存・C-2 は draw 数が心配。
  → 総合は「B-9 取り下げ」側。**ただし外すかもしれない。外したら ANN は broken と書く。**
自分の破りの既知の弱点（結果に関わらず残す）: (1) 隣接 offset の draw は窓が重なり独立でない → 有効 draw は名目未満、
  p_emp の実効分解能は 1/597 より粗い。(2) t 版の p_emp は、帰無の t 分布の裾が名目より重い場合にだけ β 版と一致する
  ので、両者の不一致自体が「どちらのスケールで事前固定すべきだったか」という設計上の問いを残す（方法論候補として記録）。
  (3) C-3 は実 ANN 腕と構成を揃える代わりに、偽窓が実 event day や 4σ 窓に載る＝「静かな ctrl」との対比ではなくなる。
出力 data/refute_c56_empirical_null_c.md。発注なし・本番編集なし・書込は AUREL_RESEARCH 配下のみ。
"""
import os, json, math, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c56_empirical_null_c.md"); L = []
NY = "America/New_York"; SEED = 20261120
ZMAIN = 5.0; W_SIG = 5520; SPAN = 14400.0; DECL = 14400.0
US2S = {(8, 20), (8, 25), (9, 35), (9, 40)}
FAM_ALL = [d for d in range(-300, 301) if 3 <= abs(d) <= 300]
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

say("# [REFUTE 09:30 part C] B-9 の「ANN 破れ」は私の n 交絡か本物かを決着（studentize・n マッチ・構成マッチ）")
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
ANNm = (m_nfp | m_fomc)
tr["ANN"] = ANNm
tsf = ts.astype(float)
m_sj, _ = inwin(tsf[SJ5] + 300); m_uj, p_uj = inwin(tsf[UJ5] + 300)
tr["SJ"] = m_sj & ~tr.ANN & ~tr.isevday; tr["UJ"] = m_uj & ~tr.ANN & ~tr.isevday
last_is_us2 = np.isin((p_uj - 300).astype(np.int64), ts[UJ_US2])
tr["US2"] = tr.UJ & last_is_us2; tr["OTH"] = tr.UJ & ~last_is_us2
m_any4, _ = inwin(tsf[J4] + 300)
tr["ctrl"] = ~tr.isevday & (tr.wd <= 4) & ~m_any4 & ~tr.ANN

# ---------- 高速化した推定器（c56 と数値同一・design を事前計算） ----------
era = ((tr.year >= 2021) & (tr.year <= 2026)).to_numpy()
HH = tr.hh.to_numpy(); DAYc = pd.factorize(tr.day)[0]
Rsv = tr.Rs.to_numpy(float)
H_FULL = np.column_stack([(HH == h).astype(float) for h in range(1, 24)])
ctrlv = tr.ctrl.to_numpy(); evmv = tr.isevday.to_numpy(); wdmv = tr.wd.to_numpy() <= 4

def fit_fast(rows, gcols):
    """rows = bool mask（推定に使う行）, gcols = list of bool mask（群ダミー）。c56 の fe_fit と同一の数値。"""
    ri = np.where(rows)[0]
    G = np.column_stack([g[ri].astype(float) for g in gcols])
    X = np.column_stack([np.ones(len(ri)), G, H_FULL[ri]])
    y = Rsv[ri]
    XtX_inv = np.linalg.pinv(X.T @ X); beta = XtX_inv @ (X.T @ y); e = y - X @ beta
    dc = DAYc[ri]; u, inv = np.unique(dc, return_inverse=True)
    Xe = X * e[:, None]
    S = np.zeros((len(u), X.shape[1])); np.add.at(S, inv, Xe)
    nG = len(u)
    V = XtX_inv @ (S.T @ S) @ XtX_inv * (nG / max(nG - 1, 1))
    out = []
    for i in range(len(gcols)):
        b = beta[1 + i]; se = math.sqrt(max(V[1 + i, 1 + i], 0))
        out.append((b, se, int(G[:, i].sum())))
    return out, V, nG, ri

# 複製 assert（fit_fast が c56 と一致するか）
g4 = [tr.ANN.to_numpy(), tr.SJ.to_numpy(), tr.US2.to_numpy(), tr.OTH.to_numpy()]
rows4 = era & (tr.ANN | tr.SJ | tr.US2 | tr.OTH | tr.ctrl).to_numpy()
o4, V4, nG4, ri4 = fit_fast(rows4, g4)
bA, sA, nA = o4[0]; bo, so, no = o4[3]
cv = np.zeros(V4.shape[0]); cv[1] = 1; cv[4] = -1
sAO = math.sqrt(max(cv @ V4 @ cv, 0)); dAO = bA - bo
tA = bA / sA
assert nA == 138 and abs(bA - 0.513) < 0.002 and abs(sAO - 0.156) < 0.004, f"複製失敗 {nA}/{bA}/{sAO}"
say(f"- 複製 OK（高速推定器は c56 と数値一致）: 外 ANN β {bA:+.3f} (t {tA:+.2f}・n {nA})・oth {bo:+.3f} (t {bo/so:+.2f})・ANN−oth {dAO:+.3f} (t {dAO/sAO:+.2f})")
say(f"- 判定対象: |t_ANN| = **{abs(tA):.2f}**・|β_ANN| = **{abs(bA):.3f}**・族 FAM_ALL {len(FAM_ALL)} offset・Bonferroni M = {M}")
say("")

ANN_T0 = np.concatenate([t_nfp[np.isfinite(t_nfp)], t_fomc[np.isfinite(t_fomc)]])

# ---------- 2 つの族を 1 ループで ----------
say("## 族の生成: ①c56 構成（part B と同じ）②実 ANN 腕と構成を揃えた版（C-3）")
rowsB, rowsC = [], []
for sh in FAM_ALL:
    mp, _ = inwin(ANN_T0, off=sh * 86400.0)
    # ① c56 構成（part B 再現）
    pl = mp & ~evmv & wdmv & ~m_any4 & ~ANNm
    if pl.sum() >= 1:
        rr = era & (pl | (ctrlv & ~pl))
        if int((pl & era).sum()) >= 10:
            oo, VV, nGg, _ = fit_fast(rr, [pl]); b, se, n = oo[0]
            rowsB.append(dict(shd=sh, b=b, se=se, n=n, t=(b / se if se > 0 else np.nan),
                              days=int(len(np.unique(DAYc[np.where(rr & pl)[0]])))))
    # ② 構成マッチ（実 ANN 腕と同じ: 絞りは「実 ANN 窓と重ならない」だけ）
    plc = mp & ~ANNm
    if int((plc & era).sum()) >= 10:
        rr = era & (plc | (ctrlv & ~plc))
        oo, VV, nGg, _ = fit_fast(rr, [plc]); b, se, n = oo[0]
        rowsC.append(dict(shd=sh, b=b, se=se, n=n, t=(b / se if se > 0 else np.nan),
                          days=int(len(np.unique(DAYc[np.where(rr & plc)[0]])))))
PB = pd.DataFrame(rowsB); PC = pd.DataFrame(rowsC)
say(f"- ①c56 構成: draw {len(PB)}・n 中央値 {PB.n.median():.0f}（実 ANN 138 との比 {PB.n.median()/138:.2f}）・se 平均 {PB.se.mean():.4f}")
say(f"- ②構成マッチ: draw {len(PC)}・n 中央値 {PC.n.median():.0f}（比 {PC.n.median()/138:.2f}）・se 平均 {PC.se.mean():.4f}")
say(f"- 実 ANN: n 138・se {sA:.4f} ← ②の方が実腕に近いか: {abs(PC.n.median()-138) < abs(PB.n.median()-138)}")
say("")

def emp_p(vals, obs):
    ex = int((np.abs(np.asarray(vals)) >= abs(obs)).sum())
    return ex, (ex + 1) / (len(vals) + 1)

# ---------- C-1 studentize ----------
say("## C-1 studentize（n 非依存の統計量 = t で比べる・①c56 構成族）")
exB_t, pB_t = emp_p(PB.t.to_numpy(), tA)
say(f"- 族の |t| 最大 **{PB.t.abs().max():.2f}**（shift {int(PB.iloc[int(PB.t.abs().idxmax())].shd):+d} 日）・|t|≥2 の割合 {(PB.t.abs()>=2).mean()*100:.1f}%（名目 4.6%）・|t|≥3 {(PB.t.abs()>=3).mean()*100:.2f}%（名目 0.27%）")
say(f"- |t_pl| ≥ |t_ANN| = {abs(tA):.2f} の draw = **{exB_t}** / {len(PB)}")
say(f"- p_t = **{pB_t:.5f}**・Bonferroni ×{M} = {min(1, pB_t*M):.4f} → <0.05 **{min(1, pB_t*M) < 0.05}**")
c1_break = min(1, pB_t * M) >= 0.05
say(f"- **C-1 = {'破れ' if c1_break else '生存'}**")
say(f"- 対比（part B の事前固定 = β スケール）: |β_pl| ≥ {abs(bA):.3f} の draw = {emp_p(PB.b.to_numpy(), bA)[0]} → p_β {emp_p(PB.b.to_numpy(), bA)[1]:.5f}・×{M} = {min(1, emp_p(PB.b.to_numpy(), bA)[1]*M):.4f}")
say("")

# ---------- C-2 n マッチ部分族 ----------
say("## C-2 n マッチ部分族（n ∈ [110, 170]・実 ANN 138 の ±25%）")
sub = PB[(PB.n >= 110) & (PB.n <= 170)]
say(f"- 部分族 draw = **{len(sub)}**・n 中央値 {sub.n.median() if len(sub) else float('nan'):.0f}・se 平均 {sub.se.mean() if len(sub) else float('nan'):.4f}（実 ANN se {sA:.4f}）")
if len(sub) >= 60:
    ex2, p2b = emp_p(sub.b.to_numpy(), bA)
    ex2t, p2t = emp_p(sub.t.to_numpy(), tA)
    say(f"- |β_pl| ≥ {abs(bA):.3f} の draw = **{ex2}** / {len(sub)}・p_β = **{p2b:.5f}**・×{M} = {min(1, p2b*M):.4f} → <0.05 **{min(1, p2b*M) < 0.05}**")
    say(f"- 参考 t 版: |t_pl| ≥ {abs(tA):.2f} = {ex2t}・p_t {p2t:.5f}・×{M} = {min(1, p2t*M):.4f}")
    c2_break = min(1, p2b * M) >= 0.05
    say(f"- **C-2 = {'破れ' if c2_break else '生存'}**")
else:
    c2_break = None
    say(f"- 部分族 {len(sub)} < 60 → **C-2 = 判定せず**")
say("")

# ---------- C-3 構成マッチ族 ----------
say("## C-3 構成マッチ族（プラセボを実 ANN 腕と同じ構成で作る＝n を 138 近傍に揃える）")
ex3b, p3b = emp_p(PC.b.to_numpy(), bA)
ex3t, p3t = emp_p(PC.t.to_numpy(), tA)
say(f"- draw {len(PC)}・β 実測 sd {PC.b.std(ddof=1):.4f}・名目 se 平均 {PC.se.mean():.4f} → **λ = {PC.b.std(ddof=1)/PC.se.mean():.3f}**")
say(f"- |t|≥2 の割合 {(PC.t.abs()>=2).mean()*100:.1f}%（名目 4.6%）・|t|≥3 {(PC.t.abs()>=3).mean()*100:.2f}%（名目 0.27%）・族 |t| 最大 {PC.t.abs().max():.2f}・族 |β| 最大 {PC.b.abs().max():.3f}")
say(f"- β 版: |β_pl| ≥ {abs(bA):.3f} = **{ex3b}** / {len(PC)}・p = **{p3b:.5f}**・×{M} = {min(1, p3b*M):.4f} → <0.05 **{min(1, p3b*M) < 0.05}**")
say(f"- t 版: |t_pl| ≥ {abs(tA):.2f} = **{ex3t}** / {len(PC)}・p = **{p3t:.5f}**・×{M} = {min(1, p3t*M):.4f} → <0.05 **{min(1, p3t*M) < 0.05}**")
c3_break = (min(1, p3b * M) >= 0.05) and (min(1, p3t * M) >= 0.05)
say(f"- 条件 β 版・t 版の両方で ×25 ≥ 0.05 → {c3_break}")
say(f"- **C-3 = {'破れ' if c3_break else '生存'}**")
say("")

# ---------- C-4 外れ draw の正体 ----------
say("## C-4 診断: |β| 上位 5 draw は n が小さい draw に偏るか（①c56 構成族）")
say("| 順位 | shift 日 | n 本 | 事象日 | β | se | t |")
say("|---|---|---|---|---|---|---|")
topb = PB.reindex(PB.b.abs().sort_values(ascending=False).index).head(5)
for k, (_, q) in enumerate(topb.iterrows(), 1):
    say(f"| {k} | {int(q.shd):+d} | {int(q.n)} | {int(q.days)} | {q.b:+.3f} | {q.se:.3f} | {q.t:+.2f} |")
say(f"- 上位 5 draw の n 中央値 **{topb.n.median():.0f}** vs 族全体 {PB.n.median():.0f} vs 実 ANN 138 → "
    f"小 n 偏り = **{topb.n.median() < PB.n.median()}**")
say(f"- 族の n と |β| の順位相関 Spearman = **{PB[['n']].assign(ab=PB.b.abs()).corr(method='spearman').iloc[0,1]:+.3f}**"
    f"（負なら「n が小さい draw ほど |β| が大きい」＝ β スケール比較は n 交絡あり）")
say(f"- 族の n と |t| の順位相関 = {PB[['n']].assign(at=PB.t.abs()).corr(method='spearman').iloc[0,1]:+.3f}（0 近傍なら t は n 非依存＝studentize が正しい）")
say("")

# ---------- 総合 ----------
say("## part C 総合（事前固定の規則で合成）")
say("| 検定 | n の揃い | 結果 | 数字 |")
say("|---|---|---|---|")
say(f"| C-1 studentize（t 族・594 draw） | t は n 非依存 | **{'破れ' if c1_break else '生存'}** | p_t {pB_t:.5f} ×25 = {min(1, pB_t*M):.4f}・族 |t| 最大 {PB.t.abs().max():.2f} |")
say(f"| C-2 n マッチ部分族 | n 110-170 | **{('破れ' if c2_break else '生存') if c2_break is not None else '判定せず'}** | draw {len(sub)} |")
say(f"| C-3 構成マッチ族 | n 中央 {PC.n.median():.0f} | **{'破れ' if c3_break else '生存'}** | p_β {p3b:.5f}・p_t {p3t:.5f} |")
say(f"| （参考）part B の B-9 = 事前固定の β 版 | n 中央 {PB.n.median():.0f} ≠ 138 | **破れ** | p_β {emp_p(PB.b.to_numpy(), bA)[1]:.5f} ×25 = {min(1, emp_p(PB.b.to_numpy(), bA)[1]*M):.4f} |")
surv = sum(1 for x in (c1_break, c2_break, c3_break) if x is False)
brk = sum(1 for x in (c1_break, c2_break, c3_break) if x is True)
say("")
say(f"- 生存 {surv} / 破れ {brk} / 判定せず {sum(1 for x in (c1_break, c2_break, c3_break) if x is None)}")
verdict = "B-9 の破れは私の n 交絡＝**取り下げ**（ANN は T2 として生存）" if surv >= 2 else \
          ("B-9 の破れは**本物**（ANN は broken）" if brk >= 2 else "**inconclusive**")
say(f"- **part C 総合判定: {verdict}**")
say("")
say(f"- 実行時間 {time.time()-T0:.1f} s・seed {SEED}（乱数未使用）")
say("- 副作用: 読取のみ（npz 1・json 1・csv 2）。書込は data/refute_c56_empirical_null_c.md のみ。発注/デモ発注/本番編集/プロセス接触/MT5/プロップ/秘密 なし。外部通信なし。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
