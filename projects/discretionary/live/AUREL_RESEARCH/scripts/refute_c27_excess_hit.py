# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-10] 対象: cycle27 (03:55) の弱信号（主 H3 は null で争わない）
  W1 「幾何は RW として“ほぼ”値付け（週 β(p on q̄) 0.71/0.68 <1）」＋補足 c「TP が遠い週ほど RW より到達しやすい
      （週 ρ(x̄,q̄) 在 −0.113 t −2.70／外 −0.171 t −2.93）」
  W2 「幾何を所与とすると scan は RW よりわずかに到達しにくい（x̄ 在 −1.43 pp t −3.15／外 −1.40 pp t −2.56）」（知識 (5)）
  W3 「週の方向因子: 同週 BUY x̄×SELL x̄ の相関 在 −0.044／外 −0.198／近年 −0.264・側を混ぜた x̄ は過小分散（外 0.83）」
      ＋前向きセル提案「側別 x̄ の lag1 r>0 両側 p<0.05・≥52 週」
  W4 「H1 幾何（b̄）は数週間持続する遅い状態（週 r 0.47/0.57）」（知識 (1)）

=== 事前固定（この docstring を書いてから数字を見る） ===
攻め筋: cycle27 の RW 基準 q は「連続・無ドリフト・正確到達・ft を SL/TP の両側に対称に入れた閉形式」である。
  実データでの基準を**プラセボ建玉**で作る: 同じ本の幾何（側・risk USD・b）を、建玉時刻の近傍のランダムな足の終値で建て、
  本番エンジンと同じ決着規則（SL は FEED_TOL 手前・TP は FEED_TOL 先・同足は SL 優先・最長 288 本）で高値/安値判定する。
  これは壁の位置情報を持たない「同じ地合い・同じ幾何」の経験的 RW 基準 q_emp であり、離散足・オーバーシュート・
  fat tail・ボラ集積・FEED_TOL の非対称をすべて含む。閉形式 q との差は基準の誤差、q_emp に対する残差が市場の情報。
データ: data/refute_c4_scan_paths_2010_2026.json（19404 本）・data/macro/XAU_m5_ohlc.npz（m5_loader と同一の M5・bid・読取のみ）。
  プラセボ SET A: 本ごと K=16・建玉 index ±5760 本（≈±4 週の取引足）から一様・末尾 288 本の余裕を確保。
  プラセボ SET B: 本ごと K=8・同じ暦週（UTC 月〜日）の足から一様（W3 の「同週の方向因子」が壁に固有かを見るため）。
  建玉 = 当該足の終値、判定は次の足から 288 本（本番は建玉足の途中から＝1 足分の差・記述）。
  変種: V0 = エンジン規則（FT 0.1・SL 優先）／V1 = FT 0.2（コスト倍）／V2 = FT 0.1・TP 優先（上界）。SET B は V0 のみ。
統計: 窓 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・窓別）。se は建玉 UTC 日クラスタ bootstrap 2000（本レベル）。
  週集計は cycle27 と同じ（W-SUN・決着 n≥5・lag1 ペア）。Bonferroni: W1〜W3 の 3 標的 → 名目 |t| 閾値 2.39 を併記。
規則（判定は V0・在で決め外で確認）:
  R1 (W2): x̄_emp = mean(1{TP}_i − q_emp_i)（決着本・q_emp は決着プラセボ中の TP 率）。
      survived = 在 x̄_emp<0 ∧ 日クラスタ t≤−2 ∧ 外 同符号 t≤−1.5。broken = 在 符号≥0 または |t|<1。他 inconclusive。
      併記: 閉形式 x̄ の再現・V1/V2・TIME 率（本番 vs プラセボ・サバイバーシップ）・プール TP 率差。
  R2 (W1): (a) 週 ρ(x̄_emp, q̄_emp)・β(p_w on q̄_emp,w) を実本で再計算。(b) プラセボ双子（本ごと k 番目のプラセボを
      “取引”とみなし、その建玉週で集計・閉形式 q）で ρ^pl(x̄,q̄)・β^pl を k=0..15 の 16 組で計算し平均と範囲。
      broken = [在・外とも ρ^pl 平均 が 実 ρ と同符号で |ρ^pl| ≥ 0.5|ρ_real|]  または  [実本の ρ(x̄_emp,q̄_emp) が 在 |t|<2]。
      survived = 在 |t|≥2 ∧ 外 同符号 |t|≥1.5 ∧ |ρ^pl| < 0.25|ρ_real|（在・外）。他 inconclusive。
  R3 (W3): 同週 ρ(BUY x̄, SELL x̄) を実本（閉形式 x）と SET B 双子 8 組で比較。
      「壁に固有でない（一般の週方向因子）」= 外で ρ^pl 平均 ≤ 0.5·ρ_real（同符号・負）。固有 = |ρ^pl| < 0.25|ρ_real|。他 inconclusive。
      前向きセルの検出力: 側別 x̄ 週 lag1 r（在・外・近年）を実本で印字。52 週の se≈0.14 → 両側 p<0.05 に r≥0.27 が要る。
      在・外とも |r|<0.10 なら「設計上通らない（新レジーム前提）」と記す。
  R4 (W4): 週 b̄ の lag1 r（raw）と、週 log RV（M5 終値対数リターン二乗和）・log risk̄ に OLS 回帰した残差の lag1 r。
      残差 r < 0.5·raw r（在）なら「幾何の持続＝ボラ持続の別名（知識としては冗長）」と記す。判定語は使わず記述。
  多重検定: R1〜R3 の 3 標的 Bonferroni(3)。look-ahead: プラセボは建玉後の足だけで決着。survivorship: TIME 率を併記。
  陽性対照: プラセボに人工ドリフト（接近方向へ 1 本あたり +0.002R）を注入した時 x̄_emp が正に動くことを 1 行印字。
コスト: scan 無し・MT5 無し・外部通信無し。書き込みは data/refute_c27_excess_hit.md・_run.log のみ。seed 20261110。

=== v2 追記（v1 実行後・規則は変えない・v1 の出力は data/refute_c27_excess_hit_v1.md / _run_v1.log に保存） ===
バグ修正 2 件: (1) pandas 3 の datetime64[s] で週開始 epoch を 1e9 で割っていた → SET B が全て 2010 年初に潰れ R3 が NaN。
  (2) M5 格子は週末・祝日の flat 足（H=L=前終値・32.1%）を含む完全格子で、プラセボが flat 足に建つと 24h 平坦のまま TIME
  → v1 のプラセボ TIME 率 20〜22%（本番 3〜5%）。v2 はプラセボ候補を非 flat 足に限定（本番 scan も flat 足に建たない・建玉足の flat 0.3%）。
事後追加（判定には使わず記述）: SET C = 非 flat かつ ATR14 が建玉時の ±20%（log）に一致する足から K=16（建玉時 ATR 中央値 1.29 vs
  一般の足 0.68＝建玉はボラ 2 倍の時刻・ボラ不一致を揃えた基準）。R2 の q_emp 置換は測定誤差で ρ が機械的に負へ寄る
  （errors-in-variables）ので分割半分（k<8 を説明変数 q̂_A・k≥8 を基準 q̂_B とし x = 1{TP} − q̂_B）を主に印字。R2 双子に SET B（同週）も追加。
  R1 に hold≥1（建玉足で決着しなかった本）の行を追加: 建玉足は本番だけに有利（同足 TP 2.2% vs 同足 SL 0.3%・在）。陽性対照ドリフト 0.0005R/本。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c27_excess_hit.md")
rng = np.random.default_rng(20261110)
L = []
def say(s=""): print(s, flush=True); L.append(s)

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["week"] = tr["ts"].dt.to_period("W-SUN"); tr["day"] = tr["ts"].dt.floor("D")
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = tr["tp"] - tr["q"]
tr["sgn"] = np.where(tr["side"] == "BUY", 1.0, -1.0)
N = len(tr)

z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); O, H, Lo, C = z["open"], z["high"], z["low"], z["close"]
NB = len(TS)
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
ok = (ie < NB) & (TS[np.minimum(ie, NB - 1)] == tr["entry_time"].to_numpy(np.int64))
say(f"# [反証 cycle27] プラセボ建玉による経験的 RW 基準 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c27_excess_hit.py)")
say(f"本 {N}・決着 {int(tr.dec.sum())}・TIME {int((~tr.dec).sum())}・FEED_TOL {FT}・MAX_HOLD {MAXH}；M5 OHLC {NB} 本 {pd.Timestamp(TS[0],unit='s')}..{pd.Timestamp(TS[-1],unit='s')}；entry_time の足一致 {int(ok.sum())}/{N}")
tr["ie"] = ie
W = {"在2010-20": (tr.year <= 2020).to_numpy(), "外2021-26": (tr.year >= 2021).to_numpy(), "近年2024-26": (tr.year >= 2024).to_numpy()}

# ---------- プラセボ・シミュレータ ----------
AR = np.arange(1, MAXH + 1)
def simulate(j, sgn, risk, b, ft=FT, sl_first=True, drift=0.0, chunk=1200):
    """j: 建玉足 index (M,)・終値建玉・次足から MAXH 本。戻り: 1=TP, 0=SL, -1=TIME。"""
    M = len(j); out = np.full(M, -1, np.int8)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg = sgn[sl_]; rk = risk[sl_]; bb = b[sl_]
        idx = jj[:, None] + AR[None, :]
        hh = H[idx]; ll = Lo[idx]
        if drift:  # 陽性対照: 接近方向へ 1 本あたり drift·risk の人工ドリフト
            dr = (sg * rk * drift)[:, None] * AR[None, :]; hh = hh + dr; ll = ll + dr
        ent = C[jj]
        sl = ent - sg * rk; tp = ent + sg * bb * rk
        buy = sg > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft)[:, None], hh >= (sl - ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tp + ft)[:, None], ll <= (tp - ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        res = np.full(len(jj), -1, np.int8)
        if sl_first:
            res[(kt < ks)] = 1; res[(ks <= kt) & (ks < 10**6)] = 0
        else:
            res[(kt <= ks) & (kt < 10**6)] = 1; res[(ks < kt)] = 0
        out[sl_] = res
    return out

KA, KB = 16, 8; SPAN = 5760
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float)
FLAT = (H == Lo); ATR = pd.Series(H - Lo).rolling(14).mean().shift(1).to_numpy()
NF = np.flatnonzero(~FLAT & (np.arange(NB) <= NB - MAXH - 2))      # 非 flat・末尾余裕ありの足 index
say(f"flat 足（H=L）{100*FLAT.mean():.1f}%・建玉足が flat {100*FLAT[ie].mean():.2f}%・建玉時 ATR14 中央値 {np.nanmedian(ATR[ie]):.2f} vs 全非 flat 足 {np.nanmedian(ATR[NF]):.2f} USD")
# SET A: ±SPAN 本・非 flat
pa_lo = np.searchsorted(NF, np.maximum(ie - SPAN, 0)); pa_hi = np.maximum(np.searchsorted(NF, ie + SPAN), pa_lo + 1)
JA = NF[np.minimum((pa_lo[:, None] + rng.random((N, KA)) * (pa_hi - pa_lo)[:, None]).astype(np.int64), len(NF) - 1)]
# SET B: 同じ暦週の非 flat 足（epoch は pandas 3 の datetime64[s] に依存しない形で）
wk_start = ((tr["week"].dt.start_time - pd.Timestamp(0)) // pd.Timedelta(seconds=1)).to_numpy(np.int64); wk_end = wk_start + 7 * 86400
pb_lo = np.searchsorted(NF, np.searchsorted(TS, wk_start)); pb_hi = np.maximum(np.searchsorted(NF, np.searchsorted(TS, wk_end)), pb_lo + 1)
JB = NF[np.minimum((pb_lo[:, None] + rng.random((N, KB)) * (pb_hi - pb_lo)[:, None]).astype(np.int64), len(NF) - 1)]
# SET C（事後）: 非 flat・±SPAN・ATR14 が建玉時の ±20%（log）に一致（候補 <KA なら ±40%・それも無ければ SET A と同じ）
JC = np.empty((N, KA), np.int64); nC = np.empty(N, np.int64); widen = 0; fallback = 0
a_e = ATR[ie]
for i in range(N):
    cand = NF[pa_lo[i]:pa_hi[i]]; la = np.log(np.where(ATR[cand] > 0, ATR[cand], np.nan) / a_e[i])
    m = np.abs(la) < 0.2
    if m.sum() < KA:
        m = np.abs(la) < 0.4; widen += 1
    if m.sum() < 1:
        m = np.ones(len(cand), bool); fallback += 1
    cc = cand[m]; nC[i] = len(cc); JC[i] = cc[rng.integers(0, len(cc), KA)]
say(f"SET C ATR 一致: 候補数 中央値 {np.median(nC):.0f}（±40% へ拡大 {widen} 本・一致無し fallback {fallback} 本）")
def rep(a, k): return np.repeat(a, k)
t1 = time.time()
RA = {}
for name, kw in (("V0", dict(ft=FT, sl_first=True)), ("V1", dict(ft=2 * FT, sl_first=True)), ("V2", dict(ft=FT, sl_first=False))):
    RA[name] = simulate(JA.ravel(), rep(sgn, KA), rep(risk, KA), rep(bb, KA), **kw).reshape(N, KA)
RA["V0+drift"] = simulate(JA.ravel(), rep(sgn, KA), rep(risk, KA), rep(bb, KA), ft=FT, sl_first=True, drift=0.0005).reshape(N, KA)
RA["C0"] = simulate(JC.ravel(), rep(sgn, KA), rep(risk, KA), rep(bb, KA), ft=FT, sl_first=True).reshape(N, KA)
RB = simulate(JB.ravel(), rep(sgn, KB), rep(risk, KB), rep(bb, KB), ft=FT, sl_first=True).reshape(N, KB)
say(f"プラセボ生成: SET A {N}×{KA}×4 変種・SET C {N}×{KA}・SET B {N}×{KB}（{time.time()-t1:.0f} s）；プラセボ建玉足の ATR 中央値 A {np.nanmedian(ATR[JA]):.2f}／C {np.nanmedian(ATR[JC]):.2f}／B {np.nanmedian(ATR[JB]):.2f}")
say()

def qemp(R):
    ntp = (R == 1).sum(1); nsl = (R == 0).sum(1); dec = ntp + nsl
    return np.where(dec > 0, ntp / np.maximum(dec, 1), np.nan), (R == -1).mean(1), dec

def clus_t(vals, days, nboot=2000):
    """建玉日クラスタ bootstrap の平均と t。"""
    s = pd.DataFrame({"v": vals, "d": days}).groupby("d")["v"].agg(["sum", "size"])
    S = s["sum"].to_numpy(float); Nn = s["size"].to_numpy(float); G = len(S)
    m = S.sum() / Nn.sum()
    pick = rng.integers(0, G, (nboot, G))
    bs = S[pick].sum(1) / Nn[pick].sum(1)
    se = bs.std(ddof=1)
    return m, se, (m / se if se > 0 else np.nan)

# ---------- R1: 水準 ----------
say("## R1 (W2) 水準: 閉形式 x̄ の再現 と プラセボ基準 x̄_emp（決着本・日クラスタ t）")
say("| 窓 | 決着 n | p 実 | q̄ 閉形式 | x̄ 閉形式 pp (t) | q̄_emp V0 | **x̄_emp V0 pp (t)** | V1 FT×2 pp (t) | V2 TP優先 pp (t) | TIME 実 / プラセボ V0 | プール p 実−プラセボ pp |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
R1 = {}
dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy(); days = tr["day"].to_numpy(); q = tr["q"].to_numpy()
QE = {}; TIMER = {}
for v in ("V0", "V1", "V2", "V0+drift", "C0"):
    QE[v], TIMER[v], _ = qemp(RA[v])
hold1 = (tr["hold"] >= 1).to_numpy()
for wn, wm in W.items():
    m = wm & dec & ~np.isnan(QE["V0"])
    mc, sec, tc = clus_t(tp[m] - q[m], days[m])
    row = {}
    cells = []
    for v in ("V0", "V1", "V2"):
        mm = wm & dec & ~np.isnan(QE[v])
        me, se, te = clus_t(tp[mm] - QE[v][mm], days[mm]); row[v] = (me, se, te); cells.append(f"{100*me:+.2f} ({te:+.2f})")
    pool_pl = (RA["V0"][wm] == 1).sum() / max(((RA["V0"][wm] == 1) | (RA["V0"][wm] == 0)).sum(), 1)
    say(f"| {wn} | {m.sum()} | {tp[m].mean():.4f} | {q[m].mean():.4f} | {100*mc:+.2f} ({tc:+.2f}) | {QE['V0'][m].mean():.4f} | **{cells[0]}** | {cells[1]} | {cells[2]} | {100*(~dec[wm]).mean():.1f}% / {100*TIMER['V0'][wm].mean():.1f}% | {100*(tp[m].mean()-pool_pl):+.2f} |")
    R1[wn] = row
say()
say("事後（記述）: SET C（ATR 一致）基準・hold≥1（建玉足で決着しなかった本）・同足決着の内訳")
say("| 窓 | q̄_emp C0 | x̄_emp C0 pp (t) | TIME プラセボ C0 | hold≥1 n | x̄_emp V0 hold≥1 pp (t) | x̄_emp C0 hold≥1 pp (t) | 同足 TP % / 同足 SL %（全本比） |")
say("|---|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    mm = wm & dec & ~np.isnan(QE["C0"]); me, se, te = clus_t(tp[mm] - QE["C0"][mm], days[mm]); R1[wn]["C0"] = (me, se, te)
    m1 = wm & dec & hold1 & ~np.isnan(QE["V0"]); m1e, _, t1e = clus_t(tp[m1] - QE["V0"][m1], days[m1])
    m1c = wm & dec & hold1 & ~np.isnan(QE["C0"]); m1ce, _, t1ce = clus_t(tp[m1c] - QE["C0"][m1c], days[m1c])
    h0 = wm & ~hold1
    say(f"| {wn} | {QE['C0'][mm].mean():.4f} | {100*me:+.2f} ({te:+.2f}) | {100*TIMER['C0'][wm].mean():.1f}% | {m1.sum()} | {100*m1e:+.2f} ({t1e:+.2f}) | {100*m1ce:+.2f} ({t1ce:+.2f}) | {100*(h0 & (tp==1)).sum()/wm.sum():.2f} / {100*(h0 & dec & (tp==0)).sum()/wm.sum():.2f} |")
m = dec & ~np.isnan(QE["V0+drift"])
md, _, td = clus_t(tp[m] - QE["V0+drift"][m], days[m])
say(f"陽性対照（プラセボに接近方向 +0.0005R/本 のドリフト注入）: 全期間 x̄_emp {100*md:+.2f} pp (t {td:+.2f})（基準が有利側に動けば x̄_emp は負に動く＝機構の確認のみ）")
# 閉形式 q と q_emp の差（b 十分位）
say()
say("閉形式 q − q_emp（V0）を b 十分位（在の境界）で: 正 = 閉形式が RW の到達率を**過大**に見積もる")
edges = np.quantile(bb[W["在2010-20"]], np.linspace(0, 1, 11)); edges[0] = -1; edges[-1] = 1e9
say("| 窓 | " + " | ".join(f"D{i+1}" for i in range(10)) + " | 全体 |")
say("|---|" + "---|" * 11)
for wn, wm in W.items():
    cells = []
    for i in range(10):
        mm = wm & dec & (bb > edges[i]) & (bb <= edges[i + 1]) & ~np.isnan(QE["V0"])
        cells.append(f"{100*(q[mm]-QE['V0'][mm]).mean():+.1f}")
    mm = wm & dec & ~np.isnan(QE["V0"])
    say(f"| {wn} | " + " | ".join(cells) + f" | {100*(q[mm]-QE['V0'][mm]).mean():+.2f} |")
say()

# ---------- 週集計ユーティリティ ----------
NMIN = 5
def weekly(df, xcol, qcol, pcol):
    dd = df[df["dec"]]
    g = dd.groupby("week").agg(n=(xcol, "size"), xbar=(xcol, "mean"), p=(pcol, "mean"), qbar=(qcol, "mean"))
    return g[g["n"] >= NMIN].sort_index()
def lag1(g, col):
    idx = g.index; pos = np.array([(p - idx[0]).n for p in idx]); s = {p: i for i, p in enumerate(pos)}
    ia = [s[p] for p in pos if (p + 1) in s]; ib = [s[p + 1] for p in pos if (p + 1) in s]
    v = g[col].to_numpy(float)
    return float(np.corrcoef(v[ia], v[ib])[0, 1]) if len(ia) > 4 else np.nan
def corr_t(a, b):
    r = float(np.corrcoef(a, b)[0, 1]); n = len(a)
    return r, r * math.sqrt((n - 2) / max(1e-12, 1 - r * r))
def ols_b(y, x):
    X = np.column_stack([np.ones(len(x)), x]); beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    u = y - X @ beta; V = np.linalg.inv(X.T @ X) * (u @ u) / (len(y) - 2)
    return beta[1], math.sqrt(V[1, 1])

# ---------- R2: W1 ----------
say("## R2 (W1) 週の ρ(x̄, q̄)・β(p on q̄): 閉形式 → q_emp 置換（分割半分: 説明変数 q̂_A=k<8・基準 q̂_B=k≥8）→ プラセボ双子（閉形式 q・k ごとの平均 [範囲]）")
say("| 窓 | 有効週 | ρ 閉形式 (t) | β 閉形式 (se) | **ρ 分割半分 (t)** | β 分割半分 (se) | ρ 同一 q_emp (t)・EIV 偏り込み | ρ^pl 双子 A(±4週) 平均 [min,max] | β^pl A | ρ^pl 双子 B(同週) 平均 [min,max] | β^pl B | A で ρ^pl ≤ 0.5·ρ_real の割合 |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|")
R2 = {}
qA, _, _ = qemp(RA["V0"][:, :KA // 2]); qB, _, _ = qemp(RA["V0"][:, KA // 2:])
tr["qe"] = QE["V0"]; tr["xe"] = tr["tp"] - tr["qe"]; tr["qA"] = qA; tr["xB"] = tr["tp"] - qB
def twins(Rmat, Jmat, K, wm):
    rp = []; bp = []
    for k in range(K):
        R = Rmat[:, k]; dk = pd.DataFrame({"tp": (R == 1).astype(float), "dec": R >= 0, "q": q,
                                           "week": pd.to_datetime(TS[Jmat[:, k]], unit="s").to_period("W-SUN")})[wm]
        dk["x"] = dk["tp"] - dk["q"]
        gk = weekly(dk, "x", "q", "tp"); rk, _ = corr_t(gk.xbar, gk.qbar); bk, _ = ols_b(gk.p.to_numpy(), gk.qbar.to_numpy())
        rp.append(rk); bp.append(bk)
    return np.array(rp), np.array(bp)
for wn, wm in W.items():
    df = tr[wm & ~tr["qe"].isna() & ~tr["qA"].isna() & ~tr["xB"].isna()]
    g = weekly(df, "x", "q", "tp"); r0, t0_ = corr_t(g.xbar, g.qbar); b0, s0 = ols_b(g.p.to_numpy(), g.qbar.to_numpy())
    gs = weekly(df, "xB", "qA", "tp"); r1, t1_ = corr_t(gs.xbar, gs.qbar); b1, s1 = ols_b(gs.p.to_numpy(), gs.qbar.to_numpy())
    ge = weekly(df, "xe", "qe", "tp"); r2, t2_ = corr_t(ge.xbar, ge.qbar)
    rpA, bpA = twins(RA["V0"], JA, KA, wm); rpB, bpB = twins(RB, JB, KB, wm)
    frac = float(((np.sign(rpA) == np.sign(r0)) & (np.abs(rpA) >= 0.5 * abs(r0))).mean())
    R2[wn] = dict(r0=r0, t0=t0_, r1=r1, t1=t1_, rp=rpA.mean(), rpB=rpB.mean(), frac=frac, b0=b0, b1=b1, bp=bpA.mean(), bpB=bpB.mean())
    say(f"| {wn} | {len(g)} | {r0:+.3f} ({t0_:+.2f}) | {b0:+.3f} ({s0:.3f}) | **{r1:+.3f} ({t1_:+.2f})** | {b1:+.3f} ({s1:.3f}) | {r2:+.3f} ({t2_:+.2f}) | {rpA.mean():+.3f} [{rpA.min():+.3f},{rpA.max():+.3f}] | {bpA.mean():+.3f} | {rpB.mean():+.3f} [{rpB.min():+.3f},{rpB.max():+.3f}] | {bpB.mean():+.3f} | {frac:.2f} |")
say()

# ---------- R3: W3 ----------
say("## R3 (W3) 同週 ρ(BUY x̄, SELL x̄)（両側 ≥3 本の週）: 実本（閉形式 x）vs SET B 同週プラセボ双子（k=0..7 平均 [範囲]）；側別 x̄ 週 lag1 r（前向きセルの検出力）")
say("| 窓 | 週 | **ρ 実** | ρ^pl 同週双子 平均 [min,max] | Var/名目 実 | Var/名目 双子 | lag1 r BUY x̄ 実 | lag1 r SELL x̄ 実 | lag1 BUY 双子 | lag1 SELL 双子 |")
say("|---|---|---|---|---|---|---|---|---|---|")
R3 = {}
def side_corr(df):
    dd = df[df["dec"]]
    gb = dd[dd.side == "BUY"].groupby("week")["x"].agg(["mean", "size"]); gs = dd[dd.side == "SELL"].groupby("week")["x"].agg(["mean", "size"])
    j = gb.join(gs, lsuffix="_b", rsuffix="_s", how="inner"); j = j[(j.size_b >= 3) & (j.size_s >= 3)]
    r = float(np.corrcoef(j.mean_b, j.mean_s)[0, 1]) if len(j) > 5 else np.nan
    g = dd.groupby("week").agg(n=("x", "size"), xbar=("x", "mean"), vq=("q", lambda s: float((s * (1 - s)).mean())))
    g = g[g.n >= NMIN]; vr = float(g.xbar.var(ddof=1) / (g.vq / g.n).mean())
    lb = lag1(gb[gb["size"] >= NMIN].rename(columns={"mean": "xbar"}), "xbar"); ls_ = lag1(gs[gs["size"] >= NMIN].rename(columns={"mean": "xbar"}), "xbar")
    return r, len(j), vr, lb, ls_
for wn, wm in W.items():
    r, nw, vr, lb, ls_ = side_corr(tr[wm])
    rp = []; vp = []; lbp = []; lsp = []
    for k in range(KB):
        R = RB[:, k]; dk = pd.DataFrame({"tp": (R == 1).astype(float), "dec": R >= 0, "q": q, "side": tr["side"].to_numpy(),
                                        "week": pd.to_datetime(TS[JB[:, k]], unit="s").to_period("W-SUN")})[wm]
        dk["x"] = dk["tp"] - dk["q"]
        rk, _, vk, lbk, lsk = side_corr(dk); rp.append(rk); vp.append(vk); lbp.append(lbk); lsp.append(lsk)
    rp = np.array(rp)
    R3[wn] = dict(r=r, rp=rp.mean(), lb=lb, ls=ls_)
    say(f"| {wn} | {nw} | **{r:+.3f}** | {rp.mean():+.3f} [{rp.min():+.3f},{rp.max():+.3f}] | {vr:.3f} | {np.mean(vp):.3f} | {lb:+.3f} | {ls_:+.3f} | {np.mean(lbp):+.3f} | {np.mean(lsp):+.3f} |")
say()

# ---------- R4: W4 ----------
say("## R4 (W4) 週 b̄ の持続は週ボラの持続か: lag1 r raw／log RV・log risk̄ に回帰した残差／log RV 自身")
lr = np.diff(np.log(C)); wk_bar = pd.to_datetime(TS[1:], unit="s").to_period("W-SUN")
rv = pd.Series(lr ** 2).groupby(wk_bar.to_numpy()).sum(); rv = np.log(rv[rv > 0])
say("| 窓 | 週 | lag1 b̄ raw | lag1 残差(b̄ | log RV, log risk̄) | lag1 残差(b̄ | log RV) | lag1 log RV | lag1 log risk̄ | R² of b̄ on (log RV, log risk̄) |")
say("|---|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    g = tr[wm].groupby("week").agg(n=("b", "size"), bbar=("b", "mean"), rbar=("risk", "mean")); g = g[g.n >= NMIN]
    g = g.join(rv.rename("lrv"), how="inner"); g["lrisk"] = np.log(g.rbar)
    X = np.column_stack([np.ones(len(g)), g.lrv, g.lrisk]); beta, *_ = np.linalg.lstsq(X, g.bbar.to_numpy(), rcond=None)
    g["res2"] = g.bbar - X @ beta; r2 = 1 - g.res2.var() / g.bbar.var()
    X1 = np.column_stack([np.ones(len(g)), g.lrv]); b1_, *_ = np.linalg.lstsq(X1, g.bbar.to_numpy(), rcond=None); g["res1"] = g.bbar - X1 @ b1_
    say(f"| {wn} | {len(g)} | {lag1(g,'bbar'):+.3f} | {lag1(g,'res2'):+.3f} | {lag1(g,'res1'):+.3f} | {lag1(g,'lrv'):+.3f} | {lag1(g,'lrisk'):+.3f} | {r2:.3f} |")
say()

# ---------- 判定 ----------
say("## 判定（docstring の規則・V0・在で決め外で確認・Bonferroni(3) の名目 |t| 閾値 2.39 併記）")
a, b_ = R1["在2010-20"]["V0"], R1["外2021-26"]["V0"]
if a[0] >= 0 or abs(a[2]) < 1: v1 = "broken"
elif a[0] < 0 and a[2] <= -2 and b_[0] < 0 and b_[2] <= -1.5: v1 = "survived"
else: v1 = "inconclusive"
say(f"- **R1 (W2 「幾何を所与とすると RW より到達しにくい」）: {v1}** — x̄_emp 在 {100*a[0]:+.2f} pp (t {a[2]:+.2f})／外 {100*b_[0]:+.2f} pp (t {b_[2]:+.2f})；閉形式では 在 −1.43／外 −1.40。")
A, B = R2["在2010-20"], R2["外2021-26"]
pl_repro = all(np.sign(R2[w]["rp"]) == np.sign(R2[w]["r0"]) and abs(R2[w]["rp"]) >= 0.5 * abs(R2[w]["r0"]) for w in ("在2010-20", "外2021-26"))
if pl_repro or abs(A["t1"]) < 2: v2 = "broken"
elif abs(A["t1"]) >= 2 and np.sign(B["r1"]) == np.sign(A["r1"]) and abs(B["t1"]) >= 1.5 and all(abs(R2[w]["rp"]) < 0.25 * abs(R2[w]["r0"]) for w in ("在2010-20", "外2021-26")): v2 = "survived"
else: v2 = "inconclusive"
say(f"- **R2 (W1 「TP が遠い週ほど RW より到達しやすい／β<1 の部分補償」）: {v2}** — ρ 閉形式 在 {A['r0']:+.3f}／外 {B['r0']:+.3f} → q_emp 分割半分 在 {A['r1']:+.3f} (t {A['t1']:+.2f})／外 {B['r1']:+.3f} (t {B['t1']:+.2f})；プラセボ双子 ρ^pl A(±4週) 在 {A['rp']:+.3f}／外 {B['rp']:+.3f}・B(同週) 在 {A['rpB']:+.3f}／外 {B['rpB']:+.3f}（β^pl A 在 {A['bp']:+.3f}／外 {B['bp']:+.3f}・B 在 {A['bpB']:+.3f}／外 {B['bpB']:+.3f} vs 実 β 在 {A['b0']:+.3f}／外 {B['b0']:+.3f}）。")
C3 = R3["外2021-26"]
if C3["r"] < 0 and C3["rp"] <= 0.5 * C3["r"]: v3 = "一般の週方向因子（壁に固有でない）"
elif abs(C3["rp"]) < 0.25 * abs(C3["r"]): v3 = "壁に固有（survived）"
else: v3 = "inconclusive"
pw = all(abs(R3[w]["lb"]) < 0.10 and abs(R3[w]["ls"]) < 0.10 for w in ("在2010-20", "外2021-26"))
say(f"- **R3 (W3 週の方向因子）: {v3}** — 外 ρ 実 {C3['r']:+.3f} vs 同週双子 {C3['rp']:+.3f}；側別 x̄ lag1 r 在 BUY {R3['在2010-20']['lb']:+.3f}／SELL {R3['在2010-20']['ls']:+.3f}・外 BUY {C3['lb']:+.3f}／SELL {C3['ls']:+.3f} → 前向きセル（52 週・r≥0.27 要）は {'設計上通らない（在・外とも |r|<0.10・新レジーム前提）' if pw else '在/外の値から見て通り得る／要確認'}。")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
