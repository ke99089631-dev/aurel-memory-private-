# -*- coding: utf-8 -*-
"""
[研究レーン cycle33 2026-11-10] 【深化・レジーム／機構】本番帯 jh7-12 の双子検定
問い: 本番エンジンが実際に建てる時間帯（JST 7–12 時・jh7-12）の壁→壁(再加速)の本は、
      「同じ地合い・同じ時刻帯・同じ側・同じ幾何（risk USD・b）」でランダムに建てた双子（プラセボ建玉）より
      TP に到達しやすいか。= 壁の位置情報は、時刻帯の背景（夜間ドリフト・ボラの日内形）を差し引いた後に
      なお残るか。cycle32 (e) の提案・refute_c27 の経験的 RW 基準 q_emp（x̄_emp 全 scan 在 −1.64 pp／外 −1.47／近年 −0.42）を
      本番帯に限定し、プラセボを「同じ JST 時刻（同 jh）・±28 暦日・非 flat 足」から引く（SET S・主）。
      入口フィルタの提案ではない（建玉の有無を変えない・本番母集団が情報を持つかの記述）。

=== 事前固定（この docstring を書いてから数字を見る） ===
データ: data/refute_c4_scan_paths_2010_2026.json（19404 本・jh = JST 時・frozen FEED_TOL 0.1／MAX_HOLD 288）
      data/macro/XAU_m5_ohlc.npz（bid・完全格子・前値埋め・flat 32.6%・読取のみ）。scan 無し・MT5 無し・外部通信無し。
本番帯 = jh ∈ {7..12}（DATA_MAP §3 の「本番帯 jh7-12」と同じ）。補集合 = それ以外（記述）。
母数（検定前に確認した本数）: jh7-12 在 2250（決着 2234）／外 1622（1612）／近年 931（925）。
プラセボ（refute_c27 の simulate を再利用・終値建玉・次足から MAX_HOLD 本・SL は FEED_TOL 手前／TP は FEED_TOL 先・同足 SL 優先）:
  SET S（主）: 本ごと K=16・同じ JST 時（jh 一致）・建玉 index ±28 暦日（±8064 本）・非 flat（H≠L）・末尾 288 本の余裕・
               実本の建玉足そのもの（d=0）だけ除外（refute_c32 ①: 片側マスクを避ける）。
  SET A（副・c27 と同形）: 本ごと K=16・±5760 本・非 flat・時刻を揃えない（時刻帯の背景を含まない基準）。
  SET SC（事後・記述）: SET S ∧ ATR14（直前 14 本の H−L 平均）が建玉時の ±20%（log）に一致（<K なら ±40%・無ければ SET S）。
統計: 本 i の q_emp_i = 決着プラセボ中の TP 率（決着 0 なら NaN・除外）。x_i = 1{TP_i} − q_emp_i（決着本のみ）。
      x̄_emp = 平均・se は建玉 UTC 日クラスタ bootstrap 2000・t = x̄/se。MDE = 2·se。
      R 換算 Δμ_R = mean_i[ R*_i − mean_k R*_pl,ik ]（R* = +(b+ft) if TP／−(1−ft) if SL・決着のみ・TIME 除外）。
      窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 優位の判定は近年で・在は構造の記述）。
判定（1 セル・事前固定）:
  H_T: **近年 2024-26H1・jh7-12・SET S・x̄_emp > 0 ∧ t ≥ 2** → PASS（本番帯の本は同時刻の双子より TP に到達しやすい）、
       確認 = 外 2021-26H1 同符号 t ≥ 1.5。近年 x̄_emp < 0 ∧ t ≤ −2 → 「双子より悪い」（c27 全 scan と同じ向き）。他 null。
  検出力の事前宣言: 近年 決着 925 本・x の sd ≤0.5 → 独立 se ≈1.6 pp・日クラスタで ≈1.8 pp → MDE ≈3.5 pp ≈ 0.08R（1+b̄ ≈2.3）。
       期待の大きさ: 近年の本番帯 R̄ +0.035 vs 補集合 −0.029（差 +0.064R ≈ +2.8 pp）= MDE と同桁 → **t≥2 に届かない可能性が高いと事前に書く**
       （null は「3.5 pp 以下」としか読まない）。ゲート ㉛ は入口フィルタ用で本件（母集団の情報の有無）には適用しないが ρ_eq を併記。
併記（記述・判定に使わない）: 在の同セル／補集合 jh∉7-12／DiD = [x̄(帯) − x̄(補)]（実本の帯差から双子の帯差を引く）／
      時刻帯の背景 = q̄_emp(帯) − q̄_emp(補)（双子だけで見た本番帯の TP 到達しやすさ）／SET A／SET SC／hold≥1（建玉足で決着しなかった本・
      c27: 建玉足は本番だけに有利）／side 別／wall_kind 別／年別 x̄_emp（帯）。
負の対照（refute_c32 ④）: プラセボ k=0 を擬似実本・k=1..15 を基準にした x̄ → 0 ∧ |t|<2 で較正確認（帯・3 窓）。
陽性対照: 帯の実本の TP 指標を 近年 で +3.5 pp 分だけ人工的に反転（SL→TP を無作為に 3.5% 分）した時 t が +2 を超えるか（検出力の実測）；
          プラセボに接近方向ドリフト +0.0005R/本 を注入 → x̄_emp が負に動く（機構の確認・c27 と同じ）。
最重大反証（事前に書く）: (i) プラセボ ±28 日は建玉後の日を含み壁抜け後の地合いを拾う（c32 でも小）。(ii) 本番の建玉は足の途中・プラセボは終値
      → 建玉足 1 本分の差（hold≥1 版で確認）。(iii) bid のみ（両群同配信）。(iv) 同時刻の双子は実本と path が重なる（同日クラスタで吸収）。
      (v) jh7-12 の本は 2010-26 で時刻帯の母集団が同じでも建玉規則が違う可能性（scan は frozen 定数・同一）。(vi) 判定 1 セル。
多重検定: 判定は 1 セル。他は記述。look-ahead: 双子は建玉後の足だけで決着。survivorship: TIME 率を本番／双子で併記。seed 20261110。
コスト: npz 3 s＋プラセボ 19404×16×(S・A・SC・drift) ≈ 20〜40 s。書き込み data/c33_production_band_twin_result.md・data/c33_run.log のみ。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c33_production_band_twin_result.md")
rng = np.random.default_rng(20261110)
L = []
def say(s=""): print(s, flush=True); L.append(s)

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["day"] = tr["ts"].dt.floor("D")
tr["ft"] = FT / tr["risk"]; tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["sgn"] = np.where(tr["side"] == "BUY", 1.0, -1.0)
tr["band"] = tr["jh"].between(7, 12)
tr["Rstar"] = np.where(tr["tp"] == 1, tr["b"] + tr["ft"], -(1 - tr["ft"]))
N = len(tr)

z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H, Lo, C = z["high"], z["low"], z["close"]
NB = len(TS)
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
ok = (ie < NB) & (TS[np.minimum(ie, NB - 1)] == tr["entry_time"].to_numpy(np.int64))
say(f"# [cycle33 研究レーン] 本番帯 jh7-12 の双子検定（同 JST 時刻・同側・同幾何のプラセボ建玉） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c33_production_band_twin.py)")
say(f"本 {N}・決着 {int(tr.dec.sum())}・FEED_TOL {FT}・MAX_HOLD {MAXH}；M5 OHLC {NB} 本 {pd.Timestamp(TS[0],unit='s')}..{pd.Timestamp(TS[-1],unit='s')}；entry_time の足一致 {int(ok.sum())}/{N}")
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
W = {"在2010-20": (tr.year <= 2020).to_numpy(), "外2021-26": (tr.year >= 2021).to_numpy(), "近年2024-26": (tr.year >= 2024).to_numpy()}
band = tr["band"].to_numpy()
say("母数（本数／決着）: " + "・".join(f"{wn} 帯 {int((wm&band).sum())}/{int((wm&band&tr.dec.to_numpy()).sum())}・補 {int((wm&~band).sum())}/{int((wm&~band&tr.dec.to_numpy()).sum())}" for wn, wm in W.items()))

# ---------- プラセボ・シミュレータ（refute_c27 と同一規則） ----------
AR = np.arange(1, MAXH + 1)
def simulate(j, sgn, risk, b, ft=FT, drift=0.0, chunk=1200):
    M = len(j); out = np.full(M, -1, np.int8)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg = sgn[sl_]; rk = risk[sl_]; bb = b[sl_]
        idx = jj[:, None] + AR[None, :]
        hh = H[idx]; ll = Lo[idx]
        if drift:
            dr = (sg * rk * drift)[:, None] * AR[None, :]; hh = hh + dr; ll = ll + dr
        ent = C[jj]
        sl = ent - sg * rk; tp = ent + sg * bb * rk
        buy = sg > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft)[:, None], hh >= (sl - ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tp + ft)[:, None], ll <= (tp - ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        res = np.full(len(jj), -1, np.int8)
        res[(kt < ks)] = 1; res[(ks <= kt) & (ks < 10**6)] = 0
        out[sl_] = res
    return out

K = 16; SPAN_S = 28 * 288; SPAN_A = 5760
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); jh = tr["jh"].to_numpy(int)
FLAT = (H == Lo); ATR = pd.Series(H - Lo).rolling(14).mean().shift(1).to_numpy()
HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2)
NF = np.flatnonzero(valid)
say(f"flat 足 {100*FLAT.mean():.1f}%・建玉足が flat {100*FLAT[ie].mean():.2f}%・建玉時 ATR14 中央値 帯 {np.nanmedian(ATR[ie[band]]):.2f}／補 {np.nanmedian(ATR[ie[~band]]):.2f} USD")

# SET S: 同 JST 時・±28 暦日・非 flat・d=0 除外
JS = np.empty((N, K), np.int64); nS = np.empty(N, np.int64)
JSC = np.empty((N, K), np.int64); nSC = np.empty(N, np.int64); widen = 0; fallback = 0
a_e = ATR[ie]
for h in range(24):
    NFh = NF[HOUR[NF] == h]
    ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii] + SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_]-50,0):hi[t_]+50]; cand = cand[cand != ie[i]]
        nS[i] = len(cand); JS[i] = cand[rng.integers(0, len(cand), K)]
        la = np.log(np.where(ATR[cand] > 0, ATR[cand], np.nan) / a_e[i]) if a_e[i] > 0 else np.full(len(cand), np.nan)
        m = np.abs(la) < 0.2
        if m.sum() < K:
            m = np.abs(la) < 0.4; widen += 1
        if m.sum() < 1:
            m = np.ones(len(cand), bool); fallback += 1
        cc = cand[m]; nSC[i] = len(cc); JSC[i] = cc[rng.integers(0, len(cc), K)]
# SET A: ±5760 本・非 flat
pa_lo = np.searchsorted(NF, np.maximum(ie - SPAN_A, 0)); pa_hi = np.maximum(np.searchsorted(NF, ie + SPAN_A), pa_lo + 1)
JA = NF[np.minimum((pa_lo[:, None] + rng.random((N, K)) * (pa_hi - pa_lo)[:, None]).astype(np.int64), len(NF) - 1)]
say(f"SET S 候補数 中央値 {np.median(nS):.0f}（p10 {np.quantile(nS,0.1):.0f}）・jh 一致 {100*(HOUR[JS]==jh[:,None]).mean():.1f}%・SET SC ATR 一致 候補 中央値 {np.median(nSC):.0f}（±40% 拡大 {widen}・fallback {fallback}）")
def rep(a): return np.repeat(a, K)
t1 = time.time()
RS = simulate(JS.ravel(), rep(sgn), rep(risk), rep(bb)).reshape(N, K)
RA = simulate(JA.ravel(), rep(sgn), rep(risk), rep(bb)).reshape(N, K)
RSC = simulate(JSC.ravel(), rep(sgn), rep(risk), rep(bb)).reshape(N, K)
RSd = simulate(JS.ravel(), rep(sgn), rep(risk), rep(bb), drift=0.0005).reshape(N, K)
say(f"プラセボ生成: S／A／SC／S+drift 各 {N}×{K}（{time.time()-t1:.0f} s）；双子建玉足 ATR 中央値 S {np.nanmedian(ATR[JS]):.2f}／A {np.nanmedian(ATR[JA]):.2f}／SC {np.nanmedian(ATR[JSC]):.2f}")
say()

def qemp(R):
    ntp = (R == 1).sum(1); nsl = (R == 0).sum(1); dec = ntp + nsl
    return np.where(dec > 0, ntp / np.maximum(dec, 1), np.nan), (R == -1).mean(1)
def rstar_pl(R):
    """決着プラセボの R* 平均（TIME 除外）"""
    rs = np.where(R == 1, (bb + FT / risk)[:, None], np.where(R == 0, -(1 - FT / risk)[:, None], np.nan))
    return np.nanmean(rs, axis=1)
def clus(vals, days, nboot=2000):
    s = pd.DataFrame({"v": vals, "d": days}).groupby("d")["v"].agg(["sum", "size"])
    S = s["sum"].to_numpy(float); Nn = s["size"].to_numpy(float); G = len(S)
    m = S.sum() / Nn.sum(); pick = rng.integers(0, G, (nboot, G)); bs = S[pick].sum(1) / Nn[pick].sum(1)
    se = bs.std(ddof=1); return m, se, (m / se if se > 0 else np.nan)
def clus_diff(v1, d1, v2, d2, nboot=2000):
    """2 群の平均差・各群 日クラスタ bootstrap（独立）"""
    def boot(vals, days):
        s = pd.DataFrame({"v": vals, "d": days}).groupby("d")["v"].agg(["sum", "size"])
        S = s["sum"].to_numpy(float); Nn = s["size"].to_numpy(float); G = len(S)
        pick = rng.integers(0, G, (nboot, G)); return S.sum() / Nn.sum(), S[pick].sum(1) / Nn[pick].sum(1)
    m1, b1 = boot(v1, d1); m2, b2 = boot(v2, d2); se = (b1 - b2).std(ddof=1)
    return m1 - m2, se, (m1 - m2) / se if se > 0 else np.nan

dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy(); days = tr["day"].to_numpy(); Rst = tr["Rstar"].to_numpy()
hold1 = (tr["hold"] >= 1).to_numpy()
QE = {}; TM = {}; RP = {}
for nm, R in (("S", RS), ("A", RA), ("SC", RSC), ("Sd", RSd)):
    QE[nm], TM[nm] = qemp(R); RP[nm] = rstar_pl(R)

# ---------- 主表 ----------
say("## 1. 主セル H_T: 本番帯 jh7-12 の x̄_emp = mean(1{TP} − q_emp)（決着本・日クラスタ t・MDE=2se）と R 換算 Δμ_R；補集合・DiD・時刻帯の背景")
say("| 窓 | 集合 | 決着 n | p 実 | q̄_emp S | **x̄_emp S pp (t) [MDE]** | Δμ_R S (t) | x̄_emp A pp (t) | x̄_emp SC pp (t) | TIME 実／双子 S | hold≥1 x̄_emp S pp (t) |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
RES = {}
for wn, wm in W.items():
    for lab, bm in (("帯 jh7-12", band), ("補 jh∉7-12", ~band)):
        m = wm & bm & dec & ~np.isnan(QE["S"])
        mS, seS, tS = clus(tp[m] - QE["S"][m], days[m])
        mR = m & ~np.isnan(RP["S"]); dR, seR, tR = clus(Rst[mR] - RP["S"][mR], days[mR])
        mA = wm & bm & dec & ~np.isnan(QE["A"]); mAe, _, tA = clus(tp[mA] - QE["A"][mA], days[mA])
        mC = wm & bm & dec & ~np.isnan(QE["SC"]); mCe, _, tC = clus(tp[mC] - QE["SC"][mC], days[mC])
        m1 = m & hold1; m1e, _, t1e = clus(tp[m1] - QE["S"][m1], days[m1])
        RES[(wn, lab)] = dict(x=mS, se=seS, t=tS, dR=dR, tR=tR, p=tp[m].mean(), q=QE["S"][m].mean(), n=int(m.sum()))
        say(f"| {wn} | {lab} | {m.sum()} | {tp[m].mean():.4f} | {QE['S'][m].mean():.4f} | **{100*mS:+.2f} ({tS:+.2f}) [{200*seS:.1f}]** | {dR:+.4f} ({tR:+.2f}) | {100*mAe:+.2f} ({tA:+.2f}) | {100*mCe:+.2f} ({tC:+.2f}) | {100*(~dec[wm&bm]).mean():.1f}%／{100*TM['S'][wm&bm].mean():.1f}% | {100*m1e:+.2f} ({t1e:+.2f}) |")
say()
say("DiD（帯 − 補）: 実本の帯差 [p(帯)−p(補)]・双子の帯差 [q̄_emp(帯)−q̄_emp(補)]＝時刻帯の背景・x̄_emp の帯差（日クラスタ・独立 2 群）")
say("| 窓 | p 帯−補 pp | q̄_emp 帯−補 pp（背景） | **x̄_emp 帯−補 pp (t)** | Δμ_R 帯−補 R (t) | R̄ 実 帯 / 補 | ρ_eq（参考 ㉛） |")
say("|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    mb = wm & band & dec & ~np.isnan(QE["S"]); mo = wm & ~band & dec & ~np.isnan(QE["S"])
    dx, sex, tx = clus_diff(tp[mb] - QE["S"][mb], days[mb], tp[mo] - QE["S"][mo], days[mo])
    mbR = mb & ~np.isnan(RP["S"]); moR = mo & ~np.isnan(RP["S"])
    dr, ser, trr = clus_diff(Rst[mbR] - RP["S"][mbR], days[mbR], Rst[moR] - RP["S"][moR], days[moR])
    say(f"| {wn} | {100*(tp[mb].mean()-tp[mo].mean()):+.2f} | {100*(QE['S'][mb].mean()-QE['S'][mo].mean()):+.2f} | **{100*dx:+.2f} ({tx:+.2f})** | {dr:+.4f} ({trr:+.2f}) | {tr.R[wm&band].mean():+.3f} / {tr.R[wm&~band].mean():+.3f} | {abs(dr)/0.8:.3f} |")
say()

# ---------- 較正・対照 ----------
say("## 2. 負の対照（双子 k=0 を擬似実本・k=1..15 を基準）・陽性対照（帯）")
say("| 窓 | 負の対照 x̄ pp (t)（帯） | 負の対照 x̄ pp (t)（補） | 陽性 A: 近年帯 実本 TP を +3.5 pp 反転 → x̄_emp (t) | 陽性 B: 双子に +0.0005R/本 ドリフト → x̄_emp 帯 pp (t) |")
say("|---|---|---|---|---|")
q0, _ = qemp(RS[:, 1:])
for wn, wm in W.items():
    cells = []
    for bm in (band, ~band):
        m = wm & bm & (RS[:, 0] >= 0) & ~np.isnan(q0)
        me, _, te = clus((RS[:, 0][m] == 1).astype(float) - q0[m], days[m]); cells.append(f"{100*me:+.2f} ({te:+.2f})")
    m = wm & band & dec & ~np.isnan(QE["S"])
    if wn == "近年2024-26":
        tpi = tp.copy(); sl_idx = np.flatnonzero(m & (tp == 0)); flip = rng.choice(sl_idx, int(round(0.035 * m.sum())), replace=False); tpi[flip] = 1
        mi, _, ti = clus(tpi[m] - QE["S"][m], days[m]); posA = f"{100*mi:+.2f} ({ti:+.2f})"
    else: posA = "—"
    md = wm & band & dec & ~np.isnan(QE["Sd"]); me_d, _, te_d = clus(tp[md] - QE["Sd"][md], days[md])
    say(f"| {wn} | {cells[0]} | {cells[1]} | {posA} | {100*me_d:+.2f} ({te_d:+.2f}) |")
say()

# ---------- 記述: side / wall_kind / 年別 ----------
say("## 3. 記述（判定に使わない）: 帯 jh7-12 の x̄_emp S を side／wall_kind／年で")
say("| 窓 | BUY pp (t) n | SELL pp (t) n | " + " | ".join(f"{wk} pp (t) n" for wk in sorted(tr.wall_kind.unique())) + " |")
say("|---|---|---|" + "---|" * tr.wall_kind.nunique())
for wn, wm in W.items():
    cells = []
    for sd in ("BUY", "SELL"):
        m = wm & band & dec & ~np.isnan(QE["S"]) & (tr.side.to_numpy() == sd); me, _, te = clus(tp[m] - QE["S"][m], days[m]); cells.append(f"{100*me:+.2f} ({te:+.2f}) {m.sum()}")
    for wk in sorted(tr.wall_kind.unique()):
        m = wm & band & dec & ~np.isnan(QE["S"]) & (tr.wall_kind.to_numpy() == wk)
        if m.sum() >= 30: me, _, te = clus(tp[m] - QE["S"][m], days[m]); cells.append(f"{100*me:+.2f} ({te:+.2f}) {m.sum()}")
        else: cells.append(f"— {m.sum()}")
    say(f"| {wn} | " + " | ".join(cells) + " |")
say()
say("年別（帯 jh7-12）: x̄_emp S pp (t) n ／ 補集合 x̄_emp S pp")
rows = []
for y in sorted(tr.year.unique()):
    m = (tr.year.to_numpy() == y) & band & dec & ~np.isnan(QE["S"]); mo = (tr.year.to_numpy() == y) & ~band & dec & ~np.isnan(QE["S"])
    if m.sum() >= 20:
        me, _, te = clus(tp[m] - QE["S"][m], days[m], nboot=500); moe = (tp[mo] - QE["S"][mo]).mean()
        rows.append(f"{y}: {100*me:+.1f} ({te:+.1f}) n{m.sum()} ／ 補 {100*moe:+.1f}")
say("; ".join(rows))
pos_years = sum(1 for r in rows if r.split(": ")[1].startswith("+"))
say(f"帯の年別 x̄_emp が正の年: {pos_years}/{len(rows)}")
say()

# ---------- 判定 ----------
say("## 判定（事前固定・1 セル: 近年 2024-26H1・帯 jh7-12・SET S・x̄_emp>0 ∧ t≥2・確認 外 同符号 t≥1.5）")
r_n = RES[("近年2024-26", "帯 jh7-12")]; r_o = RES[("外2021-26", "帯 jh7-12")]; r_i = RES[("在2010-20", "帯 jh7-12")]
if r_n["x"] > 0 and r_n["t"] >= 2:
    v = "PASS" + ("（外 確認 ○）" if (r_o["x"] > 0 and r_o["t"] >= 1.5) else "（外 確認 ×＝近年のみ）")
elif r_n["x"] < 0 and r_n["t"] <= -2:
    v = "双子より悪い" + ("（外 同符号 ○）" if (r_o["x"] < 0 and r_o["t"] <= -1.5) else "（外 ×）")
else:
    v = "null（MDE 以下）"
say(f"- **H_T: {v}** — 近年 x̄_emp {100*r_n['x']:+.2f} pp (t {r_n['t']:+.2f}・MDE {200*r_n['se']:.1f} pp・Δμ_R {r_n['dR']:+.4f}R t {r_n['tR']:+.2f})／外 {100*r_o['x']:+.2f} (t {r_o['t']:+.2f})／在 {100*r_i['x']:+.2f} (t {r_i['t']:+.2f})")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
