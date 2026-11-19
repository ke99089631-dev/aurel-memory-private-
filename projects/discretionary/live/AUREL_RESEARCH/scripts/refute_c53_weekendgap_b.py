# -*- coding: utf-8 -*-
"""
[REFUTE c53 — B] 2026-11-19 15:30 反証レーン。A（refute_c53_weekendgap.py）で複製 15/15 を確認した上での **射程（scope）への攻撃**。

c53 の結論は「**週末ギャップの紙実差は本番コストとして無視できる**（全本当たり ≤0.001R/本）＝n* 不変」。
これは *週末の再開足 1 本* だけで測った量である。しかし c53/scan の記帳規約（紙 = SL なら −1、TP なら b・R* は +ft）と
**実際の約定（その足の open）** の差＝X_SL/X_TP は、**週末に限らず「足の open が既に水準を飛び越えていた全ての出口足」で発生する**。
金は毎日 ET 17:00–18:00 に取引休止（格子は flat 足）があるので、同じ紙実差は **毎日の休止明け** にも立つ。
c53 はその 5 倍頻度の兄弟事象を測っていない。射程が狭ければ「無視できる」は正しくても **無関係** になる。

=== 事前固定（数字を見る前に書く・seed 20261119・A と同一入力・同一窓・c53 と同一の X_SL/X_TP 定義）===
母集団 = 全 19404 本。各本の **scan 自身の出口足** ix（ts = entry_time + 300·hold）で
  飛越 SL（BUY: O[ix] ≤ SL / SELL: O[ix] ≥ SL ∧ exit=SL）→ X_SL = −1 − SGN·(O[ix]−entry)/risk  （c53 と同形・ft は相殺）
  飛越 TP（BUY: O[ix] ≥ TP / SELL: O[ix] ≤ TP ∧ exit=TP）→ X_TP = SGN·(O[ix]−entry)/risk − b
  C = X_SL − X_TP。整合: |C[ix] − (entry + SGN·clR[off+hold]·risk)| ≤ 0.02 を要求し、一致率 <95% なら inconclusive。
バケット = 出口足の直前の flat 足連の長さ runlen（flat = high==low ∧ close==前足 close）:
  **(a) 連続場中 runlen=0**（M5 標本化の人工物＝tick 駆動の本番なら SL 近傍で約定した筈＝**上限値であってコストではない**・そう明記する）
  **(b) 日次休止明け 1 ≤ runlen ≤ 30**（ET 17:00–18:00 の 12 足＝**真の休止＝真のコスト**）
  **(c) 週末/祝日明け runlen > 30**（scan は金曜引けで畳むので出口足がここに来る本は少ない筈）
窓 = 在 2013-20／外 2021-26H1／近年 2024-26H1（2010-12 は参考列・D2 遵守・16 年一括の θ は edge 判定に使わない）。

B5（射程）**BREAK 条件（論理和）**: 真の休止バケット (b)+(c) の ΣX_SL/N_all が
  (a') 在 または 外 で **≥ 0.005R/本**（＝c53 自身が H_W の PASS 線に置いた値）**または**
  (b') 在 または 外 で **c53 の週末 ΣC/N_all（在 +0.00089／外 +0.00010）の 5 倍以上**。
  ＝「週末は無視できる」が、同じ機構の兄弟事象を足すと無視できない水準になるか。
B6（プラセボ＝週末ラベルの無作為化の代わりに **ラベルの移動**）: c52/c53 の「尻尾は週末に住む」を、
  休止明け 1 件あたりの X_SL で日次休止 vs 週末で比較。**BREAK 条件**: 日次休止明け 1 件あたり mean X_SL が
  週末の 1 件あたり（在 1.12／外 1.02R）の **≥ 50%** かつ 件数が週末の **≥ 2 倍**（＝週末特異性の否定）。
B7（コスト倍・非対称）: 方法論候補 73 より「対称コスト倍は差分セルに無効」。効く向きで倍にする＝c53 自身の最重大反証 (i):
  TP は指値価格で約定（棚ぼた無し）・SL は open ＋ スプレッド 0.21 を **0.42 に倍**。週末 629 本と全本の両方で ΣC/N_all。
  **BREAK 条件**: 在 または 外 で ΣC/N_all ≥ 0.005R/本。
多重検定: 判定セルは B5／B6／B7 の 3 つ（各条件は事前固定の論理和・窓は在/外の 2 つで or を取る＝甘い側に置く＝
  壊せなければ「壊れない」が強く言える向き）。バケット別・年別は記述。
出力は data/refute_c53_weekendgap_b.md のみ。読むのは data 配下のキャッシュ 3 本。発注・本番編集・プロセス接触・MT5・プロップ・外部通信 無し。
"""
import os, json, time
import numpy as np, pandas as pd
from scipy import stats

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c53_weekendgap_b.md")
NY = "America/New_York"; rng = np.random.default_rng(20261119)
L = []
def say(s=""): print(s, flush=True); L.append(s)
def verdict(tag, cond, obs, broken):
    say(f"- **[{tag}] 判定 = {'BROKEN' if broken else 'not broken'}**")
    say(f"    - 条件: {cond}")
    say(f"    - 観測: {obs}")
say(f"# [REFUTE c53-B] 射程: 紙実差は週末だけでなく **毎日の休止明け** にも立つ — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c53_weekendgap_b.py)")

J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
X = pd.DataFrame(J["trades"]).sort_values("entry_time", kind="stable").reset_index(drop=True)
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64); d = np.diff(off) - 1
OFF = off[:-1]  # 本ごとの開始 off（off は N+1 要素）
h = X["hold"].to_numpy().astype(int); et = X["entry_time"].to_numpy()
for t in np.unique(et[pd.Series(et).duplicated(keep=False).to_numpy()]):
    g = np.where(et == t)[0]
    if not np.array_equal(h[g], d[g]):
        perm = [int(g[list(h[g]).index(v)]) for v in d[g]]; X.iloc[g] = X.iloc[perm].to_numpy()
X = X.reset_index(drop=True); N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy(); B = X["b"].to_numpy()
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK
P = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); TS = P["ts"].astype(np.int64); O = P["open"]; H = P["high"]; LO = P["low"]; C = P["close"]
def idx_of(ts):
    i = np.searchsorted(TS, ts); i2 = np.minimum(i, len(TS) - 1); return np.where(TS[i2] == ts, i2, -1)

# ---------- entry 推定（全本・ベクトル化・Part A と同じ 3 本中央値＋範囲 ≤0.02） ----------
ests = np.full((3, N), np.nan)
for jj, j in enumerate((1, 2, 3)):
    ii = idx_of(ET + 300 * j); good = (ii >= 0) & (HOLD >= j)
    ests[jj, good] = C[ii[good]] - SGN[good] * clR[OFF[good] + j] * RISK[good]
entry = np.nanmedian(ests, axis=0); rngE = np.nanmax(ests, axis=0) - np.nanmin(ests, axis=0)
nest = np.sum(~np.isnan(ests), axis=0)
SL = entry - SGN * RISK; TP = entry + SGN * B * RISK
say(f"- entry 推定: 可 {int(np.sum(nest>0))}/{N}・3 本範囲 ≤0.02 USD {np.nanmean(rngE[nest==3]<=0.02)*100:.1f}%（中央値 {np.nanmedian(rngE[nest==3]):.4f}）")

# ---------- 出口足と整合 ----------
ix = idx_of(ET + 300 * HOLD)
align = np.zeros(N, bool)
g = (ix >= 1) & (nest > 0) & (rngE <= 0.02)
align[g] = np.abs(C[ix[g]] - (entry[g] + SGN[g] * clR[OFF[g] + HOLD[g]] * RISK[g])) <= 0.02
say(f"- 出口足 ts 一致 {int(np.sum(ix>=0))}/{N}・整合（close と clR[off+hold] が ≤0.02）**{align.sum()}/{N} = {align.mean()*100:.1f}%**")
OKA = align.mean() >= 0.95
if not OKA: say("- **整合 <95% → 事前規則どおり B5/B6/B7 は inconclusive**")

# ---------- flat 足連（格子全体・ベクトル化） ----------
flat = np.zeros(len(TS), bool); flat[1:] = (H[1:] == LO[1:]) & (C[1:] == C[:-1])
ia = np.arange(len(TS)); grp = np.maximum.accumulate(np.where(~flat, ia, 0)); runlen = np.where(flat, ia - grp, 0)
say(f"- 格子 {len(TS)} 足中 flat {int(flat.sum())}（{flat.mean()*100:.1f}%）・flat 連の長さ分布 p50 {np.median(runlen[flat]):.0f}/p90 {np.percentile(runlen[flat],90):.0f}/max {runlen.max()}")
pre = np.zeros(N, int)
pre[align] = np.where(flat[ix[align] - 1], runlen[ix[align] - 1], 0)
GAP = np.full(N, np.nan); GAP[align] = O[ix[align]] - C[ix[align] - 1]

# ---------- X_SL / X_TP（c53 と同形）----------
Xs = np.zeros(N); Xt = np.zeros(N)
isSL = align & (EXIT == "SL"); isTP = align & (EXIT == "TP")
thrSL = np.where(SGN > 0, O[np.maximum(ix, 0)] <= SL, O[np.maximum(ix, 0)] >= SL) & isSL
thrTP = np.where(SGN > 0, O[np.maximum(ix, 0)] >= TP, O[np.maximum(ix, 0)] <= TP) & isTP
Xs[thrSL] = -1.0 - SGN[thrSL] * (O[ix[thrSL]] - entry[thrSL]) / RISK[thrSL]
Xt[thrTP] = SGN[thrTP] * (O[ix[thrTP]] - entry[thrTP]) / RISK[thrTP] - B[thrTP]
Xs = np.maximum(Xs, 0.0); Xt = np.maximum(Xt, 0.0); Cn = Xs - Xt
BUCK = {"(a) 連続場中 runlen=0【上限・人工物】": (pre == 0), "(b) 日次休止明け 1≤runlen≤30【真のコスト】": (pre >= 1) & (pre <= 30), "(c) 週末/祝日明け runlen>30【真のコスト】": (pre > 30)}
WIN = {"2010-12(参考)": (2010, 2012), "在 2013-20": (2013, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

say(f"\n## B5 射程: scan 自身の出口足での飛越（全 {N} 本・c53 と同一の X_SL/X_TP 定義）")
say(f"- 飛越 合計: SL {int(thrSL.sum())} 本／TP {int(thrTP.sum())} 本（整合本の {thrSL.sum()/align.sum()*100:.2f}%／{thrTP.sum()/align.sum()*100:.2f}%）・|GAP| 中央値 {np.nanmedian(np.abs(GAP[thrSL|thrTP])):.3f} USD")
say("| 窓 | バケット | N_all | 飛越 SL | 飛越 TP | 1 件あたり X_SL | ΣX_SL | ΣX_TP | ΣC | **ΣX_SL/N_all** | ΣC/N_all |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
tot = {}
for wn, (y0, y1) in WIN.items():
    w = (YEAR >= y0) & (YEAR <= y1); nall = int(w.sum())
    for bn, bm in BUCK.items():
        m = w & bm & align
        ns = int((thrSL & m).sum()); nt = int((thrTP & m).sum())
        say(f"| {wn} | {bn} | {nall} | {ns} | {nt} | {Xs[thrSL&m].mean() if ns else 0:+.3f} | {Xs[m].sum():.3f} | {Xt[m].sum():.3f} | {Cn[m].sum():+.3f} | **{Xs[m].sum()/nall:+.5f}** | {Cn[m].sum()/nall:+.5f} |")
    real = w & align & ((pre >= 1))
    tot[wn] = dict(xsl=Xs[real].sum() / nall, c=Cn[real].sum() / nall, n=int((thrSL & real).sum()), nt=int((thrTP & real).sum()), nall=nall)
    say(f"| {wn} | **(b)+(c) 真の休止 合計** | {nall} | {tot[wn]['n']} | {tot[wn]['nt']} | {Xs[thrSL&real].mean() if tot[wn]['n'] else 0:+.3f} | {Xs[real].sum():.3f} | {Xt[real].sum():.3f} | {Cn[real].sum():+.3f} | **{tot[wn]['xsl']:+.5f}** | {tot[wn]['c']:+.5f} |")
c53_week = {"在 2013-20": 0.00089, "外 2021-26H1": 0.00010}
a5 = any(tot[k]["xsl"] >= 0.005 for k in c53_week)
b5 = any(tot[k]["xsl"] >= 5 * c53_week[k] for k in c53_week)
verdict("B5", "真の休止 (b)+(c) の ΣX_SL/N_all が (a') 在/外 で ≥ 0.005R/本 **または** (b') c53 の週末 ΣC/N_all の 5 倍以上（論理和）",
        "／".join(f"{k} ΣX_SL/N_all {tot[k]['xsl']:+.5f}（0.005 → {tot[k]['xsl']>=0.005}・5×週末 {5*c53_week[k]:.5f} → {tot[k]['xsl']>=5*c53_week[k]}）" for k in c53_week),
        (a5 or b5) and OKA)

say("\n## B6 プラセボ（ラベル移動）: 「尻尾は週末に住む」— 1 件あたりの大きさと頻度を 日次休止 vs 週末 で比べる")
say("| 窓 | 日次休止 飛越 SL 件数 | 1 件あたり mean X_SL | 週末（c53b・再開足）件数 | c53b の 1 件あたり | 件数比 日次/週末 | 大きさ比 |")
say("|---|---|---|---|---|---|---|")
c53_week_n = {"在 2013-20": (16, 1.12), "外 2021-26H1": (9, 1.02)}
B6 = {}
for wn, (nw, sz) in c53_week_n.items():
    y0, y1 = WIN[wn]; w = (YEAR >= y0) & (YEAR <= y1)
    m = w & align & (pre >= 1) & (pre <= 30) & thrSL
    n_d = int(m.sum()); sz_d = Xs[m].mean() if n_d else 0.0
    B6[wn] = dict(n=n_d, sz=sz_d, rn=n_d / nw, rs=sz_d / sz)
    say(f"| {wn} | {n_d} | {sz_d:+.3f} | {nw} | {sz:+.3f} | {n_d/nw:.2f}× | {sz_d/sz:.2f}× |")
a6 = all(B6[k]["rs"] >= 0.50 and B6[k]["rn"] >= 2.0 for k in B6)
verdict("B6", "日次休止明け 1 件あたり mean X_SL が 週末の ≥50% **かつ** 件数が週末の ≥2 倍（両窓で・論理積＝厳しい側）",
        "／".join(f"{k} 大きさ {B6[k]['rs']:.2f}× 件数 {B6[k]['rn']:.2f}×" for k in B6), a6 and OKA)

say("\n## B7 コスト倍（非対称・c53 自身の最重大反証 (i) を数字にする）")
say("- 規約: TP は指値価格で約定（棚ぼた X_TP = 0）・SL は open ＋ スプレッド。スプレッド 0.21（c53 の感度）と **0.42（倍）** の 2 水準。")
say("| 窓 | 母集団 | ΣX_SL/N_all (spread 0) | spread 0.21 | **spread 0.42（倍）** | ≥0.005 か |")
say("|---|---|---|---|---|---|")
B7 = {}
for wn in ("在 2013-20", "外 2021-26H1", "近年 2024-26H1"):
    y0, y1 = WIN[wn]; w = (YEAR >= y0) & (YEAR <= y1); nall = int(w.sum())
    for pn, pm in (("真の休止 (b)+(c)・全本", align & (pre >= 1)), ("全バケット（上限）", align)):
        m = w & pm
        base = Xs[m].sum() / nall
        vals = []
        for sp in (0.0, 0.21, 0.42):
            extra = np.zeros(N); sel = thrSL & m
            extra[sel] = sp / RISK[sel]           # SL は open の外側に スプレッド 分だけ滑る
            vals.append((Xs[m] + extra[m]).sum() / nall)
        say(f"| {wn} | {pn} | {vals[0]:+.5f} | {vals[1]:+.5f} | **{vals[2]:+.5f}** | {vals[2]>=0.005} |")
        if pn.startswith("真の休止"): B7[wn] = vals[2]
a7 = any(B7[k] >= 0.005 for k in ("在 2013-20", "外 2021-26H1"))
verdict("B7", "非対称コスト（TP 棚ぼた無し・SL は open＋スプレッド 0.42）で 在 または 外 の ΣC/N_all ≥ 0.005R/本",
        "／".join(f"{k} {B7[k]:+.5f}" for k in ("在 2013-20", "外 2021-26H1")), a7 and OKA)

say("\n## 記述")
say(f"- 飛越の内訳（整合本・全期間）: " + "／".join(f"{bn} SL {int((thrSL&bm&align).sum())}/TP {int((thrTP&bm&align).sum())}" for bn, bm in BUCK.items()))
say(f"- 日次休止明けに出口が来た本（整合本）: {int(np.sum(align&(pre>=1)&(pre<=30)))}・週末/祝日明け {int(np.sum(align&(pre>30)))}・連続場中 {int(np.sum(align&(pre==0)))}")
hh = pd.to_datetime(TS[np.maximum(ix, 0)], unit="s", utc=True).tz_convert(NY).hour.to_numpy()
say(f"- 日次休止明けの出口足 ET 時刻 分布: {dict(pd.Series(hh[align&(pre>=1)&(pre<=30)]).value_counts().head(6))}")
say(f"- 週末/祝日明けの出口足 ET 時刻 分布: {dict(pd.Series(hh[align&(pre>30)]).value_counts().head(6))}")
say(f"- 整合しなかった {int((~align).sum())} 本: exit {dict(pd.Series(EXIT[~align]).value_counts())}・hold 中央値 {np.median(HOLD[~align]):.0f}・年 {dict(pd.Series(YEAR[~align]).value_counts().sort_index().head(5))}")
say(f"- 連続場中バケットの 1 件あたり X_SL（上限・tick 駆動なら SL 近傍で約定した筈＝コストではない）: " + "／".join(
    f"{wn} {Xs[thrSL & align & (pre==0) & ((YEAR>=y0)&(YEAR<=y1))].mean():+.3f}（n {int((thrSL & align & (pre==0) & ((YEAR>=y0)&(YEAR<=y1))).sum())}）" for wn, (y0, y1) in WIN.items()))
say(f"\n- 実行 {time.time()-T0:.1f} s・入力 = refute_c4 json＋refute_c2_fullpaths.npz＋XAU_m5_ohlc.npz（data 配下のみ）・seed 20261119・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
