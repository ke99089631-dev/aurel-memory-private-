# -*- coding: utf-8 -*-
"""
[cycle67 研究レーン / 2026-11-25 00:40]【探索・市場間連動の“裾”次元: 株(US500)↔金 の 5 分ジャンプ共起と 1 本先行遅行】
§8 源泉マップ「市場間先行遅行（株↔金）」は c20 で 5 分格子の線形相関 |ρ|≤0.3% の null。線形相関は裾（ジャンプ）の
依存を見ない（tail dependence ≠ linear correlation）。問い: 株指数の 5σ 級ジャンプの直後 1 本（5 分）に金のジャンプが
基準率より多く起こるか（情報は深い市場＝株先物側で先に価格化され、金 CFD が 1 本遅れる）。
源泉（憲章 3 条）: 情報到着への反応速度差・クロスアセットのヘッジ注文（株急落→金買い/売りの機械的フロー）・流動性供給者の
在庫調整。参加者 = HFT/マクロヘッジ・ETF の裁定。なぜ残り得るか = 5 分格子では秒単位の裁定が見えないので「残る」のは
記述レベルの可能性が高い＝既定の期待値は「同一足の共跳のみ・先行遅行なし」。

=== 事前固定（数字を見る前・この docstring が正本・seed 20261125） ===
データ: data/macro/XAU_m5_close.npz・US500_m5_close.npz（bid・暦時刻完全格子・前値埋め・同一ベンダー Dukascopy＝時計は共通）
      ＋ FOMC_dates.csv・CPI_dates.csv・NFP c24 v2 規則（事象日の除外）。ゲート ㉛ に refute_c4 json＋refute_c2_fullpaths.npz。
      scan 無し・M5 読込なし・MT5 無し・外部通信なし・発注なし・本番編集なし。
ジャンプ検出 = c45 と同一規約（銘柄別）: r=1e4·Δln close・σ_trail = 直前 5520 足の非 flat RMS（足自身を含まない・非 flat ≥1000）・
      z=|r|/σ。主閾値 θ=4（c45 の 5σ は事象数が少ないので先行遅行の検出力のため 4σ を主・5σ は感度）。decluster はしない
      （足単位の共起・遅れを数えるので）。
適格足 E_t = 両銘柄とも 非 flat ∧ 直前 3 足 非 flat ∧ σ 有限 ∧ ET 月〜金 ∧ 17:00–18:10 ET を除く ∧ 非 NFP/FOMC/CPI 日。
窓 = 在 2014-20（c47 と同じ: US500 2012-13 の夜間配信不備・σ 暖機を避ける）／外 2021-26H1／近年 2024-26H1（記述）。D2 遵守。
定義: JS_t = E_t ∧ zS_t≥θ（株ジャンプ）・JX_t = E_t ∧ zX_t≥θ（金ジャンプ）。対（t,t+1）は E_t ∧ E_{t+1} ∧ ts 差 300 s を要求。
  N_S→X = #{t: JS_t ∧ ¬JX_t ∧ JX_{t+1}}（株が先・金が 1 本遅れ）／N_X→S = #{t: JX_t ∧ ¬JS_t ∧ JS_{t+1}}。
  基準 = スロット（ET hh:mm 288）× 窓 ごとの適格足中のジャンプ率 h(slot) → 期待 E = Σ_cond h(slot(t+1))。RR = N/E。
  主統計: RR_S→X（H1）と A = log RR_S→X − log RR_X→S（H2・非対称）。
  se: RR は Poisson z=(N−E)/√E・A は ET 日クラスタ bootstrap B=1000（条件足の日を再抽出）。
判定（主セル 2・名目 0.025 両側）:
  H1 PASS = 在 RR_S→X ≥ 2 ∧ z ≥ 2 ∧ 外 RR>1 ∧ z ≥ 1.5。
  H2 PASS = 在 A>0 ∧ z_boot ≥ 2 ∧ 外 A>0 ∧ z_boot ≥ 1.5。
  どちらも満たさねば null。MDE（RR 検出下限）= 1 + 2/√E を併記（候補 93: MDE > 2 なら underpowered と書く）。
予測方向: H1 RR>1・H2 A>0（株が先）。大きさの事前の予想: RR 1.5〜3（同一ニュースの第 2 波）、A は 0 と区別できない可能性が高い。
対照: ①陽性 = 同一足の共跳比 ρ0 = N00/E00 ≫ 1（格子整合と共通ニュースの確認・数字の大きさは主張に使わない）
      ②プラセボ = US500 系列を +7 暦日ずらした偽 JS（同スロット・同曜日）で RR_S→X^pl ≈ 1 を要求（スロット基準の校正）
      ③lag 2・3 の RR（減衰の形・記述）④θ=5 感度 ⑤セッション別（US 現物 09:30–16:00 ET／それ以外）⑥先行足の分（定時 :00/15/30/45 vs 非定時）
      ⑦同一足共跳の符号一致率（c20 の符号レジーム 2020 反転の裾版・記述）。
ゲート ㉛（印字規則・証拠ではない）: scan 本が生きている足（1≤k<hold）に株ジャンプ（非事象日・適格）が当たった時の残り path
      e = R* − cl_k から同窓・同 k の全本平均 ē_k を引いた D（建玉日クラスタ se・MDE）。R* = R + (0.1/risk)·1{SL,TP}。
      副: 株ジャンプの方向 × side（整合/逆行）の D 差（方向情報の有無・記述）。
事前の最重大反証: (i) 同一ベンダーでも銘柄ごとの配信遅延・足の締め時刻のミリ秒差で「1 本遅れ」は生じ得る＝先行遅行は
  ベンダーの時計の人工物と区別できない（M1/tick【要取得】）。(ii) 4σ の閾値は株と金で絶対 bp が違う（σ の違い）＝RR は
  閾値の相対定義に依存。(iii) 非事象日でも PPI/小売/ISM 等の定時公表（c60 ④）が :00/:30 に残る → ⑥で分ける。
  (iv) 多重検定: 判定セル 2（在→外）・残りは記述。(v) bid のみ。
出力 data/c67_crossasset_cojump_result.md・data/c67_run.log。読取専用。
"""
import os, sys, json, math, time, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c67_crossasset_cojump_result.md"); LOG = os.path.join(DATA, "c67_run.log"); L = []
NY = "America/New_York"; SEED = 20261125; rng = np.random.default_rng(SEED)
W_SIG = 5520; THETA = 4.0; THETA2 = 5.0; B_BOOT = 1000
ERAS = [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
WD = "月火水木金土日"

def say(s=""):
    print(s, flush=True); L.append(s)
def el(): return f"{time.time()-T0:.1f}s"

say(f"# AUREL [cycle67 研究レーン] 株↔金 5 分ジャンプの共起と 1 本先行遅行  {dt.datetime.now():%Y-%m-%d %H:%M}")
say(f"- 事前固定は docstring・seed {SEED}・θ={THETA:g}（感度 {THETA2:g}）・主セル = 在 RR_S→X と A → 外")

# ---------- 暦 ----------
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
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); FOMC_ALL = pd.DatetimeIndex(pd.to_datetime(F["date"]))
CPI = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
NFP = nfp_dates_v2()
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))
say(f"- 事象日（NFP/FOMC/CPI）{len(evdays)} 日を除外")

# ---------- npz ----------
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
    nf = np.isfinite(r) & (r != 0)
    r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
    idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = lo >= 0
    S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
    NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
    sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
    nf3 = nf.copy()
    for k in (1, 2, 3): nf3 &= np.r_[[False] * k, nf[:-k]]
    tt = pd.to_datetime(ts, unit="s", utc=True)
    say(f"- {sym}_m5_close: {len(ts)} 本 {tt[0]:%Y-%m-%d}〜{tt[-1]:%Y-%m-%d} UTC（⑩）・flat 全体 {(~nf).mean()*100:.1f}%（⑪）・σ_trail 中央値 {np.nanmedian(sig):.2f} bp")
    return ts, r, nf, nf3, sig
tsX, rX, nfX, nf3X, sigX = load("XAU"); tsS, rS, nfS, nf3S, sigS = load("US500")
ts, iX, iS = np.intersect1d(tsX, tsS, assume_unique=True, return_indices=True)
rX, nfX, nf3X, sigX = rX[iX], nfX[iX], nf3X[iX], sigX[iX]; rS, nfS, nf3S, sigS = rS[iS], nfS[iS], nf3S[iS], sigS[iS]
N = len(ts); nxt_ok = np.r_[np.diff(ts) == 300, False]
say(f"- 共通格子 {N} 本（XAU 側 穴 {len(tsX)-len(ts)-int((tsX<ts[0]).sum())-int((tsX>ts[-1]).sum())}・US500 側 穴 {len(tsS)-N}）・次足 300 s 連続 {nxt_ok.mean()*100:.3f}%  ({el()})")
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yr = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize()); isev = np.asarray(etdate.isin(evdays))
dayid = (etdate.asi8 // 86_400_000_000_000).astype(np.int64)
slot = (hr * 12 + mn // 5).astype(np.int64)
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
E = nf3X & nf3S & np.isfinite(sigX) & np.isfinite(sigS) & trading & ~isev
zX = np.abs(rX) / sigX; zS = np.abs(rS) / sigS
cash = ((hr * 60 + mn) >= 9 * 60 + 30) & ((hr * 60 + mn) < 16 * 60)
sched = (mn % 15 == 0)
say(f"- 適格足 E {E.sum()}（flat/事象日/ブレイク除外後）・うち US 現物時間 {(E&cash).mean()*100:.1f}%  ({el()})")

# placebo: US500 shifted +7 days (same slot/weekday)
pos7 = np.searchsorted(ts, ts - 7 * 86400); pos7 = np.clip(pos7, 0, N - 1); ok7 = ts[pos7] == ts - 7 * 86400
def shifted(a, fill=False):
    out = np.full(N, fill, dtype=a.dtype); out[ok7] = a[pos7[ok7]]; return out

def era_mask(lo_, hi_): return (yr >= lo_) & (yr <= hi_)

def rr_lag(J_lead, J_tgt, m, lag=1, excl_same=True):
    """RR of target jump at t+lag given lead jump at t (and no target jump at t), slot-matched baseline. Returns N, E, cond count, per-day (n,e)."""
    ok = np.ones(N, bool)
    for k in range(lag): ok &= np.r_[nxt_ok[k:], [False] * k] if k else nxt_ok
    Eshift = np.r_[E[lag:], [False] * lag]
    cond = m & E & Eshift & ok & J_lead
    if excl_same: cond &= ~J_tgt
    tgt_next = np.r_[J_tgt[lag:], [False] * lag]
    base_m = m & E
    h = np.bincount(slot[base_m & J_tgt], minlength=288) / np.maximum(np.bincount(slot[base_m], minlength=288), 1)
    slot_next = np.r_[slot[lag:], np.zeros(lag, np.int64)]
    e_i = h[slot_next[cond]]; n_i = tgt_next[cond].astype(float)
    return n_i.sum(), e_i.sum(), int(cond.sum()), dayid[cond], n_i, e_i

def boot_A(d1, n1, e1, d2, n2, e2, B=B_BOOT):
    days = np.unique(np.r_[d1, d2]); nd = len(days)
    g1 = np.searchsorted(days, d1); g2 = np.searchsorted(days, d2)
    N1 = np.bincount(g1, n1, nd); E1 = np.bincount(g1, e1, nd); N2 = np.bincount(g2, n2, nd); E2 = np.bincount(g2, e2, nd)
    out = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, nd, nd), minlength=nd).astype(float)
        a1 = (w @ N1) / max(w @ E1, 1e-9); a2 = (w @ N2) / max(w @ E2, 1e-9)
        if a1 > 0 and a2 > 0: out.append(math.log(a1) - math.log(a2))
    out = np.array(out); return out.std(ddof=1) if len(out) > 10 else np.nan

def fmt(n, e):
    rr = n / e if e > 0 else np.nan; z = (n - e) / math.sqrt(e) if e > 0 else np.nan
    return rr, z

RES = {}
for theta, tag in ((THETA, "主 θ=4"), (THETA2, "感度 θ=5")):
    JX = E & (zX >= theta); JS = E & (zS >= theta); JSpl = shifted(JS)
    say(f"\n## {tag}: ジャンプ足 金 {JX.sum()}・株 {JS.sum()}・同一足共跳 {(JX&JS).sum()}")
    say("| 窓 | 適格足 | 金 J | 株 J | 同一足 N00/E00 (ρ0) | 符号一致率 | **S→X lag1 N/E RR (z) [MDE RR]** | X→S lag1 N/E RR (z) | **A=log RR 差 (z_boot)** | S→X プラセボ +7d RR (z) | S→X lag2 RR | lag3 RR |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, lo_, hi_ in ERAS:
        m = era_mask(lo_, hi_); bm = m & E
        # same-bar
        hX = np.bincount(slot[bm & JX], minlength=288) / np.maximum(np.bincount(slot[bm], minlength=288), 1)
        hS = np.bincount(slot[bm & JS], minlength=288) / np.maximum(np.bincount(slot[bm], minlength=288), 1)
        E00 = (hX * hS * np.bincount(slot[bm], minlength=288)).sum(); N00 = int((bm & JX & JS).sum())
        co = bm & JX & JS; agree = (np.sign(rX[co]) == np.sign(rS[co])).mean() if co.sum() else np.nan
        se_ag = math.sqrt(0.25 / max(co.sum(), 1))
        n1, e1, c1, d1, ni1, ei1 = rr_lag(JS, JX, m); rr1, z1 = fmt(n1, e1)
        n2, e2, c2, d2, ni2, ei2 = rr_lag(JX, JS, m); rr2, z2 = fmt(n2, e2)
        A = math.log(rr1) - math.log(rr2) if (rr1 > 0 and rr2 > 0) else np.nan
        seA = boot_A(d1, ni1, ei1, d2, ni2, ei2); zA = A / seA if seA and np.isfinite(A) else np.nan
        npl, epl, cpl, *_ = rr_lag(JSpl, JX, m); rrpl, zpl = fmt(npl, epl)
        nl2, el2, *_ = rr_lag(JS, JX, m, lag=2); rl2, zl2 = fmt(nl2, el2)
        nl3, el3, *_ = rr_lag(JS, JX, m, lag=3); rl3, zl3 = fmt(nl3, el3)
        mde = 1 + 2 / math.sqrt(e1) if e1 > 0 else np.nan
        say(f"| {name} | {bm.sum()} | {(bm&JX).sum()} | {(bm&JS).sum()} | {N00}/{E00:.1f} ({N00/E00:.1f}) | {agree*100:.0f}% ±{se_ag*100:.0f} (n {co.sum()}) | "
            f"**{int(n1)}/{e1:.2f} RR {rr1:.2f} (z {z1:+.2f}) [MDE {mde:.2f}]** (cond {c1}) | {int(n2)}/{e2:.2f} RR {rr2:.2f} (z {z2:+.2f}) (cond {c2}) | "
            f"**{A:+.3f} (z {zA:+.2f})** | {int(npl)}/{epl:.2f} RR {rrpl:.2f} (z {zpl:+.2f}) | {rl2:.2f} (z {zl2:+.2f}) | {rl3:.2f} (z {zl3:+.2f}) |")
        RES[(tag, name)] = dict(rr1=rr1, z1=z1, e1=e1, rr2=rr2, z2=z2, A=A, zA=zA, mde=mde, rrpl=rrpl, zpl=zpl, n1=n1, n2=n2, rho0=N00 / E00 if E00 else np.nan, agree=agree, nco=int(co.sum()))
    # stratified (descriptive) for main theta only
    if theta == THETA:
        say("\n### 記述: 層別 S→X lag1（在／外）— セッション・先行足の分")
        say("| 層 | 窓 | N/E RR (z) | cond |")
        say("|---|---|---|---|")
        for lname, lm in (("US 現物 09:30–16:00 ET", cash), ("現物時間外", ~cash), ("先行足 定時分 :00/15/30/45", sched), ("先行足 非定時分", ~sched)):
            for name, lo_, hi_ in ERAS[:2]:
                m = era_mask(lo_, hi_) & lm
                n1, e1, c1, *_ = rr_lag(JS, JX, m); rr1, z1 = fmt(n1, e1)
                say(f"| {lname} | {name} | {int(n1)}/{e1:.2f} RR {rr1:.2f} (z {z1:+.2f}) | {c1} |")
        # yearly counts
        say("\n### 記述: 年別（θ=4）金 J・株 J・同一足共跳・S→X lag1 N／X→S lag1 N")
        rows = []
        for y in range(2012, 2027):
            m = (yr == y); bm = m & E
            n1, e1, *_ = rr_lag(JS, JX, m); n2, e2, *_ = rr_lag(JX, JS, m)
            rows.append(f"{y}: E {bm.sum()} 金 {(bm&JX).sum()} 株 {(bm&JS).sum()} 共 {(bm&JX&JS).sum()} S→X {int(n1)}/{e1:.1f} X→S {int(n2)}/{e2:.1f}")
        say("- " + " ／ ".join(rows))

# ---------- 判定 ----------
say("\n## 判定（事前規則）")
a, b = RES[("主 θ=4", "在 2014-20")], RES[("主 θ=4", "外 2021-26H1")]
h1 = (a["rr1"] >= 2 and a["z1"] >= 2 and b["rr1"] > 1 and b["z1"] >= 1.5)
h2 = (np.isfinite(a["A"]) and a["A"] > 0 and a["zA"] >= 2 and np.isfinite(b["A"]) and b["A"] > 0 and b["zA"] >= 1.5)
say(f"- H1（株ジャンプ → 次足 金ジャンプ RR）: 在 RR {a['rr1']:.2f} z {a['z1']:+.2f}（MDE RR {a['mde']:.2f}）／外 RR {b['rr1']:.2f} z {b['z1']:+.2f}（MDE {b['mde']:.2f}） → **{'PASS' if h1 else ('underpowered' if a['mde'] > 2 else 'null')}**")
say(f"- H2（非対称 A = log RR_S→X − log RR_X→S）: 在 {a['A']:+.3f} (z {a['zA']:+.2f})／外 {b['A']:+.3f} (z {b['zA']:+.2f}) → **{'PASS' if h2 else 'null'}**")
say(f"- 対照: 同一足共跳 ρ0 在 {a['rho0']:.1f}／外 {b['rho0']:.1f}（陽性・格子整合）・プラセボ +7d RR 在 {a['rrpl']:.2f} (z {a['zpl']:+.2f})／外 {b['rrpl']:.2f} (z {b['zpl']:+.2f})（≈1 ならスロット基準は校正）")
say(f"- 符号一致率（同一足共跳）在 {a['agree']*100:.0f}% (n {a['nco']})／外 {b['agree']*100:.0f}% (n {b['nco']})")

# ---------- ゲート ㉛ ----------
say("\n## ゲート ㉛（印字規則）: scan 本が生きている足に株ジャンプ（θ=4・非事象日・適格）が当たった時の残り path D = e − ē_k")
try:
    j = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); tr = j["trades"]; n_all = len(tr)
    et = np.array([t["entry_time"] for t in tr], np.int64); hold = np.array([t["hold"] for t in tr], np.int64)
    side = np.array([1 if t["side"] == "BUY" else -1 for t in tr]); risk = np.array([t["risk"] for t in tr], float)
    exitk = np.array([t["exit"] for t in tr]); Rj = np.array([t["R"] for t in tr], float); tyear = np.array([t["year"] for t in tr])
    Rs = Rj + (0.1 / risk) * np.isin(exitk, ["SL", "TP"])
    fp = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = fp["clR"].astype(float); off = fp["off"].astype(np.int64)
    order = np.lexsort((hold, et))
    starts = off[:-1] if len(off) == n_all + 1 else off
    lens = np.diff(off) if len(off) == n_all + 1 else np.append(np.diff(off), len(clR) - off[-1])
    assert np.mean(lens == hold[order] + 1) > 0.999, "fullpaths 長さ不一致"
    et_s, hold_s, side_s, Rs_s, yr_s = et[order], hold[order], side[order], Rs[order], tyear[order]
    # all (trade,k) pairs 1<=k<hold for baseline ē_k per era
    JS = E & (zS >= THETA); JX = E & (zX >= THETA)
    jsi = np.where(JS)[0]; ts_j = ts[jsi]
    # candidate trades: et in (ts_j - 300*288, ts_j)
    lo_i = np.searchsorted(et_s, ts_j - 300 * 288, side="right"); hi_i = np.searchsorted(et_s, ts_j, side="left")
    ti = np.concatenate([np.arange(a_, b_) for a_, b_ in zip(lo_i, hi_i)]); jj = np.repeat(np.arange(len(jsi)), hi_i - lo_i)
    k = (ts_j[jj] - et_s[ti]) // 300; keep = (k >= 1) & (k < hold_s[ti]); ti, jj, k = ti[keep], jj[keep], k[keep]
    e_hit = Rs_s[ti] - clR[starts[ti] + k]
    dirn = side_s[ti] * np.sign(rS[jsi[jj]]); cojump = JX[jsi[jj]]
    say(f"- 当たり (本,k) {len(ti)}（本 {len(np.unique(ti))}・株ジャンプ足 {len(np.unique(jj))}）・そのうち金も同一足共跳 {cojump.sum()}")
    say("| 窓 | n (本,k) | mean e | ē_k 基準 | **D (cluster t)** | MDE | D 株のみ／共跳 | D 整合 − 逆行 (t) |")
    say("|---|---|---|---|---|---|---|---|")
    for name, lo_, hi_ in ERAS:
        em = (yr_s >= lo_) & (yr_s <= hi_)
        # baseline per k over all trades in era
        idx_tr = np.where(em)[0]; kk = np.concatenate([np.arange(1, h) for h in hold_s[idx_tr]]); tt_ = np.repeat(idx_tr, np.maximum(hold_s[idx_tr] - 1, 0))
        e_all = Rs_s[tt_] - clR[starts[tt_] + kk]
        ebar = np.bincount(kk, e_all, 289) / np.maximum(np.bincount(kk, minlength=289), 1)
        hm = em[ti]
        if hm.sum() < 20: say(f"| {name} | {hm.sum()} | — | — | — | — | — | — |"); continue
        D = e_hit[hm] - ebar[k[hm]]; g = et_s[ti[hm]] // 86400
        def ct(x, g):
            df = pd.DataFrame({"x": x, "g": g}).groupby("g")["x"].agg(["sum", "count"]); G = len(df)
            mu = x.mean(); s = df["sum"].to_numpy() - mu * df["count"].to_numpy(); se = math.sqrt((s @ s) * G / max(G - 1, 1)) / len(x)
            return mu, se
        mu, se = ct(D, g); mde = 2 * se
        d_only = D[~cojump[hm]].mean() if (~cojump[hm]).sum() else np.nan; d_co = D[cojump[hm]].mean() if cojump[hm].sum() else np.nan
        al = dirn[hm] > 0; ag = dirn[hm] < 0
        if al.sum() >= 10 and ag.sum() >= 10:
            m1, s1 = ct(D[al], g[al]); m2, s2 = ct(D[ag], g[ag]); dd = m1 - m2; tdd = dd / math.sqrt(s1**2 + s2**2)
        else: dd, tdd = np.nan, np.nan
        say(f"| {name} | {hm.sum()} | {e_hit[hm].mean():+.4f} | {ebar[k[hm]].mean():+.4f} | **{mu:+.4f} (t {mu/se:+.2f})** | {mde:.4f} | {d_only:+.4f}／{d_co:+.4f} (n {(~cojump[hm]).sum()}/{cojump[hm].sum()}) | {dd:+.4f} (t {tdd:+.2f}) (n {al.sum()}/{ag.sum()}) |")
except Exception as ex:
    say(f"- ゲート失敗: {ex!r}")

say(f"\n- 実行 {el()}・読取専用・発注/本番編集/MT5/外部通信なし")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); open(LOG, "w", encoding="utf-8").write("\n".join(L) + "\n")
