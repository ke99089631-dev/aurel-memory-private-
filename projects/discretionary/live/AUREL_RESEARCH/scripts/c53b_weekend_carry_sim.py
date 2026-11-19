# -*- coding: utf-8 -*-
"""
[cycle53b 研究レーン 2026-11-19] c53 Part A の発見「scan は金曜 16:55 ET 引けで生きている本（647）を**全部 TIME（hold=288）で週末の flat 足内に
引け値で畳む**（m5_loader 格子は週末 flat 足を含む）」を受けて、本番エンジン（台帳: 週末を持ち越し日曜再開足で SL/TP が決着する・S-0521）の
挙動を XAU_m5_ohlc.npz で**再開足から再シミュレーション**し、(B1) 持ち越しの紙 R と scan の引け値 R の差、(B2) 再開足ギャップの紙実差（c53 の X_SL/X_TP/C）を測る。
Part A の H_W の定義（X_SL・X_TP・C・判定規則・窓・クラスタ）はそのまま流用。**数字を見る前にこの docstring を書く**（Part A の結果を見た後の新仮説＝事後に新設した
セルとして登記する・seed 20261119）。

=== 事前固定 ===
母集団 W' = Part A の W（金曜セッション建玉 ∧ hold≥k_c+1 ∧ entry 推定 OK ∧ clR[k_c] 一致）＝全本 exit=TIME hold=288 の筈（assert して印字）。
再開足 r = ts_c の後の最初の非 flat 足（Part A と同じ）。残り保有予算 = 288 − k_c 本（本番は実足で hold を数える・週末足は無い）。
シミュレーション（エンジン近似・FEED_TOL は記帳にのみ: 紙 SL R=−1・TP R=b と json の慣行に一致）: 足 r から順に
  BUY: open≤SL → SL（実 fill=open・紙=SL）／open≥TP → TP（実=open・紙=TP）／low≤SL ∧ high≥TP → 両到達（SL 優先・件数を印字）／low≤SL → SL（実=紙=SL）／high≥TP → TP／
  予算切れ → TIME（最終足 close・紙=実）。SELL は鏡像。SELL の SL/TP 実 fill に ask 補正（+0.21）の感度。
量: R_paper_carry・R_real_carry・ΔR_carry = R*_paper_carry − cl_kc（scan の引け値 R。TIME は R*=R）・X_SL = R*_paper − R_real（再開足ギャップ SL のみ・≥0）・
  X_TP = R_real − R*_paper（再開足ギャップ TP・≥0）・C = X_SL − X_TP。
判定:
  H_B1（持ち越しの価値）: 在 2013-20 ∧ 外 2021-26H1 で mean ΔR_carry の週末クラスタ bootstrap 95%CI が 0 を含めば「持ち越しは RW 的に中立」＝null 予想。
    正（CI 下限>0 両窓）なら「scan は持ち越し本の R を過小計上」、負なら過大。MDE=2·se_cl。
  H_W（c53 Part A と同一規則）: 在 ∧ 外 とも mean(C|W) ≥ 0.05R ∧ CI 下限 >0 ∧ ΣC/N_all ≥ 0.005R → PASS（重い）／他 null。
  H_W2 は Part A で既に幾何として測定済（D_SL 在 +0.013 [−0.022,+0.045]・外 −0.010 [−0.056,+0.035]）→ 本スクリプトでは再開足での SL/TP 決着率と鏡像で再掲。
陽性対照: 再開足 SL の実 fill を SL の 0.5R 外側に置換 → mean C ≈ 0.5·P(再開足 SL)。
記述: 再開足で決着した比率と exit 内訳・持ち越し後の TIME 率・年別・X_SL p50/p90/max・LOO・受けたギャップ SGN·G/risk・scan の TIME 872 本の内訳（週末 647／平日 225）と
  c25 の「台帳 TIME 0.3% vs scan 2.6%」への含意。
事前の最重大反証: (i) エンジン近似（両到達の順序・FEED_TOL のトリガ・建玉足の扱い）が本番 _simulate と違えば 1〜2% の本で exit が変わる。(ii) Dukascopy bid の再開 open は
  実ブローカーの再開 tick と別物。(iii) 持ち越しの価値 ΔR_carry は再開ドリフト（c17 +2〜3 bp）と側の選択が混ざる＝条件づけとして読まない。(iv) W' は長保有・引け付近建玉に選択。
入力は既存キャッシュのみ・多年 scan 無し・MT5 無し・外部通信無し・書込は data/c53b_* のみ。
"""
import os, json, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c53b_weekend_carry_sim_result.md")
NY = "America/New_York"; rng = np.random.default_rng(20261119)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle53b] 週末持ち越しの再シミュレーション（scan 引け値 TIME vs 本番の持ち越し）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c53b_weekend_carry_sim.py)")

J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
X = pd.DataFrame(J["trades"]).sort_values("entry_time", kind="stable").reset_index(drop=True)
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64); d = np.diff(off) - 1
h = X["hold"].to_numpy().astype(int); et = X["entry_time"].to_numpy()
for t in np.unique(et[pd.Series(et).duplicated(keep=False).to_numpy()]):
    g = np.where(et == t)[0]
    if not np.array_equal(h[g], d[g]):
        perm = [int(g[list(h[g]).index(v)]) for v in d[g]]; X.iloc[g] = X.iloc[perm].to_numpy()
X = X.reset_index(drop=True); N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy(); B = X["b"].to_numpy()
FT = J["frozen"]["FEED_TOL"]; MAXH = J["frozen"]["MAX_HOLD"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
assert np.all(np.diff(off) == HOLD + 1)
P = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); TS = P["ts"].astype(np.int64); O = P["open"]; H = P["high"]; LO = P["low"]; C = P["close"]
def idx_of(ts):
    i = np.searchsorted(TS, ts); i2 = np.minimum(i, len(TS) - 1); return np.where(TS[i2] == ts, i2, -1)

e_ny = pd.to_datetime(ET, unit="s", utc=True).tz_convert(NY)
sess = pd.DatetimeIndex(pd.to_datetime(list((e_ny + pd.Timedelta(hours=6)).date)))
isF = sess.weekday.to_numpy() == 4
ts_c = np.array([pd.Timestamp(dd.year, dd.month, dd.day, 16, 55, tz=NY).value // 10**9 if f else -1 for dd, f in zip(sess, isF)], dtype=np.int64)
k_c = np.where(isF, (ts_c - ET) // 300, -1)
cand = np.where(isF & (HOLD >= k_c + 1))[0]
say(f"- 本 {N}・F {isF.sum()}・引け生存候補 {len(cand)}・候補の exit {dict(pd.Series(EXIT[cand]).value_counts())}・hold=={MAXH} 比率 {np.mean(HOLD[cand]==MAXH)*100:.1f}%")
# entry 推定（候補のみ）
entry = np.full(N, np.nan); rngE = np.full(N, np.nan)
for i in cand:
    ests = []
    for j in (1, 2, 3):
        ii = idx_of(np.array([ET[i] + 300 * j]))[0]
        if ii >= 0: ests.append(C[ii] - SGN[i] * clR[off[i] + j] * RISK[i])
    entry[i] = np.median(ests); rngE[i] = max(ests) - min(ests)
ic = idx_of(np.where(isF, ts_c, TS[0]))
ok = np.zeros(N, bool)
for i in cand:
    ok[i] = (rngE[i] <= 0.02) and ic[i] >= 0 and abs(SGN[i] * clR[off[i] + k_c[i]] * RISK[i] + entry[i] - C[ic[i]]) <= 0.02
W = np.where(ok)[0]
say(f"- W'（entry 推定 OK ∧ clR[k_c] 一致）{len(W)}/{len(cand)}・全本 TIME {np.all(EXIT[W]=='TIME')}・cl_kc と json R の一致 |差|≤0.005: {np.mean([abs(clR[off[i]+k_c[i]]-R[i])<=0.005 for i in W])*100:.1f}%（scan は引け値で畳む）")
# TIME 全体の内訳
T = EXIT == "TIME"; Wset = set(W.tolist())
say(f"- scan の TIME {T.sum()} 本の内訳: 週末引け畳み（F ∧ hold≥k_c+1）{np.sum(T & isF & (HOLD>=k_c+1))}・平日 {np.sum(T & ~(isF & (HOLD>=k_c+1)))}（セッション曜日 {dict(pd.Series(sess.weekday.to_numpy()[T & ~(isF & (HOLD>=k_c+1))]).value_counts())}）"
    f"・scan TIME 率 {T.mean()*100:.2f}%・週末畳みを除く TIME 率 {np.sum(T & ~(isF & (HOLD>=k_c+1)))/N*100:.2f}%")

# 再開足
reo = np.full(N, -1)
for i in W:
    j = ic[i] + 1; lim = min(ic[i] + 288 * 4, len(TS))
    while j < lim and not (H[j] != LO[j] or C[j] != C[j - 1]): j += 1
    if j < lim: reo[i] = j
W = W[reo[W] >= 0]
say(f"- 再開足 検出 {len(W)}・引け→再開 中央値 {np.median((TS[reo[W]]-ts_c[W])/3600):.1f} h")

SLp = entry - SGN * RISK; TPp = entry + SGN * B * RISK
def simulate(i, spread_sell=0.0, sl_gap_override=None):
    """返り値: exit, R_paper, R_real, at_reopen(bool), gap_through(str|None)"""
    s = SGN[i]; sl = SLp[i]; tp = TPp[i]; en = entry[i]; rk = RISK[i]
    budget = MAXH - k_c[i]; j0 = reo[i]; both = 0
    for n, j in enumerate(range(j0, min(j0 + budget, len(TS)))):
        o, hi, lo = O[j], H[j], LO[j]
        if s > 0: hitSL_o, hitTP_o, hitSL, hitTP = o <= sl, o >= tp, lo <= sl, hi >= tp
        else:     hitSL_o, hitTP_o, hitSL, hitTP = o >= sl, o <= tp, hi >= sl, lo <= tp
        if hitSL_o:
            fill = o + (spread_sell if s < 0 else 0.0)
            if sl_gap_override is not None and n == 0: fill = sl - s * sl_gap_override * rk
            return "SL", -1.0, s * (fill - en) / rk, n == 0, "SL" if n == 0 else None, both
        if hitTP_o:
            fill = o + (spread_sell if s < 0 else 0.0)
            return "TP", B[i], s * (fill - en) / rk, n == 0, "TP" if n == 0 else None, both
        if hitSL and hitTP: both = 1
        if hitSL: return "SL", -1.0, -1.0 + (s * spread_sell / rk if s < 0 else 0.0), n == 0, None, both
        if hitTP: return "TP", B[i], B[i] + (s * spread_sell / rk if s < 0 else 0.0), n == 0, None, both
    jl = min(j0 + budget, len(TS)) - 1
    rt = s * (C[jl] - en) / rk
    return "TIME", rt, rt, False, None, both

def run(spread_sell=0.0, override=None):
    out = {k: np.zeros(N) for k in ("Rp", "Rr", "Xs", "Xt")}; ex = np.array([""] * N, dtype=object); atr = np.zeros(N, bool); gt = np.array([None] * N, dtype=object); bo = np.zeros(N, int)
    for i in W:
        e_, rp, rr, a, g, both = simulate(i, spread_sell, override)
        ex[i] = e_; atr[i] = a; gt[i] = g; bo[i] = both
        rps = rp + (ft[i] if e_ in ("SL", "TP") else 0.0)  # R* 記帳
        rrs = rr + (ft[i] if e_ in ("SL", "TP") else 0.0)
        out["Rp"][i] = rps; out["Rr"][i] = rrs
        if g == "SL": out["Xs"][i] = rps - rrs
        if g == "TP": out["Xt"][i] = rrs - rps
    return out, ex, atr, gt, bo
out, ex, atr, gt, bo = run()
Cnet = out["Xs"] - out["Xt"]; dcarry = np.zeros(N); dcarry[W] = out["Rp"][W] - np.array([clR[off[i] + k_c[i]] for i in W])
G = np.full(N, np.nan); G[W] = O[reo[W]] - C[ic[W]]
say(f"- 持ち越し再シミュ exit: {dict(pd.Series(ex[W]).value_counts())}・再開足で決着 {atr[W].sum()}（{atr[W].mean()*100:.1f}%・ギャップ飛越 SL {np.sum(gt[W]=='SL')}／TP {np.sum(gt[W]=='TP')}）・両到達足あり {bo[W].sum()} 本・|G| 中央値 {np.nanmedian(np.abs(G[W])):.2f} USD・|G|/risk 中央値 {np.nanmedian(np.abs(G[W])/RISK[W]):.3f}R")

wk = ts_c
def cl_boot(vals, keys, nb=5000):
    u = np.unique(keys); sums = np.array([vals[keys == k].sum() for k in u]); ns = np.array([np.sum(keys == k) for k in u])
    bs = np.empty(nb)
    for b_ in range(nb):
        pick = rng.integers(0, len(u), len(u)); bs[b_] = sums[pick].sum() / ns[pick].sum()
    return vals.mean(), (np.percentile(bs, 2.5), np.percentile(bs, 97.5)), bs.std()
WIN = {"2010-12(参考)": (2010, 2012), "在 2013-20": (2013, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

say("\n## H_B1: 持ち越しの価値 ΔR_carry = R*_paper(持ち越し) − cl_kc(scan の引け値)（R・W'・週末クラスタ bootstrap 5000）")
say("| 窓 | N_all | W' | mean ΔR_carry | 95%CI | MDE | 持ち越し exit SL/TP/TIME | mean R*_paper carry | mean cl_kc | mean SGN·G/risk | ΣΔ/N_all |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
resB1 = {}
for name, (y0, y1) in WIN.items():
    w = (YEAR >= y0) & (YEAR <= y1); Wi = W[w[W]]
    if len(Wi) == 0: continue
    mu, ci, se = cl_boot(dcarry[Wi], wk[Wi]); resB1[name] = (mu, ci)
    exw = pd.Series(ex[Wi]).value_counts()
    say(f"| {name} | {w.sum()} | {len(Wi)} | {mu:+.4f} | [{ci[0]:+.4f},{ci[1]:+.4f}] | {2*se:.4f} | {exw.get('SL',0)}/{exw.get('TP',0)}/{exw.get('TIME',0)} | {out['Rp'][Wi].mean():+.4f} | {(out['Rp'][Wi]-dcarry[Wi]).mean():+.4f} | {np.mean(SGN[Wi]*G[Wi]/RISK[Wi]):+.4f} | {dcarry[Wi].sum()/w.sum():+.5f} |")
b1 = [resB1.get(k) for k in ("在 2013-20", "外 2021-26H1")]
v = "null（持ち越しは中立・CI が 0 を含む）" if all(r and r[1][0] <= 0 <= r[1][1] for r in b1) else ("正（scan は持ち越し本の R を過小計上）" if all(r and r[1][0] > 0 for r in b1) else ("負（過大計上）" if all(r and r[1][1] < 0 for r in b1) else "split（在外で符号/有意が揃わない）"))
say(f"- **判定 H_B1: {v}**")

say("\n## H_W（Part A と同一規則）: 再開足ギャップの紙実差 C = X_SL − X_TP（R・W'・週末クラスタ bootstrap 5000）")
say("| 窓 | W' | 再開足決着 SL/TP | 飛越 SL/TP | mean C | 95%CI | MDE | p50/p90/max X_SL | ΣX_SL | ΣX_TP | ΣC/N_all | LOO max | 全本換算 /週30本 |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
resW = {}
for name, (y0, y1) in WIN.items():
    w = (YEAR >= y0) & (YEAR <= y1); Wi = W[w[W]]
    if len(Wi) == 0: continue
    mu, ci, se = cl_boot(Cnet[Wi], wk[Wi]); xs = out["Xs"][Wi]
    loo = (Cnet[Wi].sum() - Cnet[Wi].max()) / max(len(Wi) - 1, 1)
    resW[name] = dict(mu=mu, ci=ci, per_all=Cnet[Wi].sum() / w.sum())
    say(f"| {name} | {len(Wi)} | {np.sum(atr[Wi]&(ex[Wi]=='SL'))}/{np.sum(atr[Wi]&(ex[Wi]=='TP'))} | {np.sum(gt[Wi]=='SL')}/{np.sum(gt[Wi]=='TP')} | {mu:+.4f} | [{ci[0]:+.4f},{ci[1]:+.4f}] | {2*se:.4f} | "
        f"{np.percentile(xs,50):.3f}/{np.percentile(xs,90):.3f}/{xs.max():.3f} | {xs.sum():.3f} | {out['Xt'][Wi].sum():.3f} | {Cnet[Wi].sum()/w.sum():+.5f} | {loo:+.4f} | {Cnet[Wi].sum()/w.sum()*30:+.4f}R/週 |")
okW = [resW.get(k) for k in ("在 2013-20", "外 2021-26H1")]
vW = "PASS（重い）" if all(r and r["mu"] >= 0.05 and r["ci"][0] > 0 and r["per_all"] >= 0.005 for r in okW) else "null（軽い／検出不能・MDE 参照）"
say(f"- **判定 H_W: {vW}**")
# 感度
for lab, sp in (("SELL ask +0.21", 0.21),):
    o2, _, _, _, _ = run(sp); C2 = o2["Xs"] - o2["Xt"]
    say("- 感度 " + lab + ": " + "・".join(f"{name} mean C {C2[W[((YEAR>=y0)&(YEAR<=y1))[W]]].mean():+.4f}（ΣSL {o2['Xs'][W[((YEAR>=y0)&(YEAR<=y1))[W]]].sum():.2f}/ΣTP {o2['Xt'][W[((YEAR>=y0)&(YEAR<=y1))[W]]].sum():.2f}）" for name, (y0, y1) in WIN.items()))
# 陽性対照
o3, ex3, atr3, gt3, _ = run(0.0, 0.5); C3 = o3["Xs"] - o3["Xt"]
for name, (y0, y1) in WIN.items():
    Wi = W[((YEAR >= y0) & (YEAR <= y1))[W]]
    if len(Wi): say(f"- 陽性対照 {name}: 再開足 SL を 0.5R 外側で約定 → mean C {C3[Wi].mean():+.4f}（期待 ≈ 0.5·P(再開足 SL) = {0.5*np.mean(atr[Wi]&(ex[Wi]=='SL')):+.4f} − 実 TP 棚ぼた {out['Xt'][Wi].mean():.4f}）")

say("\n## 記述")
for y in range(2010, 2027):
    Wi = W[(YEAR == y)[W]]
    if len(Wi): say(f"  {y}: W' {len(Wi)}・持ち越し exit SL {np.sum(ex[Wi]=='SL')}/TP {np.sum(ex[Wi]=='TP')}/TIME {np.sum(ex[Wi]=='TIME')}・再開足決着 {atr[Wi].sum()}・飛越 SL {np.sum(gt[Wi]=='SL')}/TP {np.sum(gt[Wi]=='TP')}・ΣX_SL {out['Xs'][Wi].sum():.3f}・ΣX_TP {out['Xt'][Wi].sum():.3f}・ΣΔR_carry {dcarry[Wi].sum():+.2f}")
top = [i for i in W[np.argsort(-out["Xs"][W])][:8] if out["Xs"][i] > 0]
say("- X_SL 上位: " + "／".join(f"{pd.to_datetime(ET[i],unit='s').date()} {X['side'][i]} risk {RISK[i]:.2f} G {G[i]:+.2f} USD X_SL {out['Xs'][i]:.3f}R" for i in top))
topt = [i for i in W[np.argsort(-out["Xt"][W])][:5] if out["Xt"][i] > 0]
say("- X_TP 上位: " + "／".join(f"{pd.to_datetime(ET[i],unit='s').date()} {X['side'][i]} risk {RISK[i]:.2f} G {G[i]:+.2f} USD X_TP {out['Xt'][i]:.3f}R" for i in topt))
# 建玉 ET 時刻帯別の W' 比率と ΔR_carry
eh = e_ny.hour.to_numpy()
say("- 建玉 ET 時刻帯別（W'）: " + "／".join(f"ET {h0:02d}-{h0+1:02d} n {np.sum((eh[W]>=h0)&(eh[W]<h0+2))} ΔR̄ {dcarry[W[(eh[W]>=h0)&(eh[W]<h0+2)]].mean():+.3f}" for h0 in range(0, 24, 2) if np.sum((eh[W]>=h0)&(eh[W]<h0+2)) >= 5))
# 含意 c25
say(f"- c25 への含意: scan 2024-26H1 の TIME 率は週末畳み込み。週末畳みを除いた TIME 率（近年）= {np.sum(T & ~(isF & (HOLD>=k_c+1)) & (YEAR>=2024))/np.sum(YEAR>=2024)*100:.2f}% vs 台帳 0.3%（n320 で 1 本）")
say(f"\n- 実行 {time.time()-T0:.1f} s・入力 = refute_c4 json＋refute_c2_fullpaths.npz＋XAU_m5_ohlc.npz・多年 scan 無し・MT5 無し・外部通信無し・seed 20261119")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
