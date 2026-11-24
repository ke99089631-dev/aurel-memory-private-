# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-24 21:30・第 4 走] 自分の A9(ii) 判定への最重大反証を自分で潰す。

A9(ii) は「腕別 log(実/双) が b 三分位で −0.19〜0 の勾配を持つ ⇒ 『方向を問わないボラ状態』だけでは
説明できない」と判定した。論拠は「mean hold ∝ 1/σ² なら log 比 = −2Δlogσ で b は約分して消える」。
**最重大反証: Δlogσ 自身が b と相関しているなら勾配はボラで説明できる**（b = TP距離/risk で
risk は壁幅≒ボラに紐づくので、高 b の本が高ボラ状態に偏ることは十分ありうる）。
第 1〜3 走は Δσ を窓別にしか測っておらず、b 三分位内では測っていない＝A9(ii) は未検証のまま。

事前固定（数字を見る前）:
  D1 b 三分位 × 窓ごとに Δ_post = log(σ_post 実／双子) と予測 −2Δ_post を出し、観測の腕別
     （c66 規約・完全対称規約の両方）と並べる。
  判定規則:
    (a) 予測 −2Δ_post が b 三分位で観測と同じ勾配（b 上 − b 下 の予測差の符号が観測差と一致し、
        大きさが観測差の 50% 以上）→ **A9(ii) は取り下げ（勾配はボラ勾配で説明できる）**。
    (b) 予測の b 勾配が観測勾配の 50% 未満 → **A9(ii) は維持**（ボラでは説明できない b 依存が残る）。
  D2 併せて b 三分位内の 観測/予測 比（T2 の算術を b で分解）を出す。
     規則: 9 セル中 ≥6 が [0.5, 2.0] の外なら T2 broken は b 分解でも維持。
seed 20261124。書き込み data/refute_c66_fpt_d.md・同 _run.log のみ。外部通信・本番編集なし。
"""
import os, json, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c66_fpt_d.md")
rng = np.random.default_rng(20261124); rng2 = np.random.default_rng(20261124 + 0x52)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c66・第 4 走] A9(ii) への自己反証: Δσ は b と相関するか — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c66_fpt_d.py)")

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["day"] = tr["ts"].dt.floor("D")
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP")
tr["sgn"] = np.where(tr["side"] == "BUY", 1.0, -1.0)
z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H, Lo, C = z["high"], z["low"], z["close"]
NB = len(TS); FLAT = (H == Lo)
CSAT = np.concatenate([[0], np.cumsum(((((TS // 86400) + 3) % 7) == 5).astype(np.int64))])
CNF = np.concatenate([[0], np.cumsum((~FLAT).astype(np.int64))])
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
ok = (ie < NB) & (TS[np.minimum(ie, NB-1)] == tr["entry_time"].to_numpy(np.int64))
tr = tr[ok].reset_index(drop=True); ie = ie[ok]; N = len(tr)
hold = tr["hold"].to_numpy(int); dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy()
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); jh = tr["jh"].to_numpy(int)
yr = tr["year"].to_numpy(int); tail_ok = ie <= NB - MAXH - 2

def simulate_gen(j, sg, rk, b, ent, start=1, ft=FT, chunk=1200):
    M = len(j); res = np.full(M, -1, np.int8); kk = np.full(M, MAXH, np.int32)
    AR = np.arange(start, start+MAXH)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s+chunk)); jj = j[sl_]; sgx = sg[sl_]; rkx = rk[sl_]; bx = b[sl_]; ex = ent[sl_]
        idx = np.minimum(jj[:, None] + AR[None, :], NB-1)
        hh = H[idx]; ll = Lo[idx]
        sl = ex - sgx*rkx; tpv = ex + sgx*bx*rkx; buy = sgx > 0
        sh = np.where(buy[:, None], ll <= (sl+ft)[:, None], hh >= (sl-ft)[:, None])
        th = np.where(buy[:, None], hh >= (tpv+ft)[:, None], ll <= (tpv-ft)[:, None])
        ks = np.where(sh.any(1), sh.argmax(1), 10**6); kt = np.where(th.any(1), th.argmax(1), 10**6)
        r = np.full(len(jj), -1, np.int8); r[kt < ks] = 1; r[(ks <= kt) & (ks < 10**6)] = 0
        k = np.minimum(ks, kt); k = np.where(k < 10**6, k+start, MAXH).astype(np.int32)
        res[sl_] = r; kk[sl_] = k
    return res, kk

K = 16; SPAN_S = 28*288
HOUR = ((TS // 3600) + 9) % 24
NF = np.flatnonzero(~FLAT & (np.arange(NB) <= NB - MAXH - 2))
JS = np.empty((N, K), np.int64)
for h in range(24):
    NFh = NF[HOUR[NF] == h]; ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii]-SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii]+SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_]-50, 0):hi[t_]+50]; cand = cand[cand != ie[i]]
        JS[i] = cand[rng.integers(0, len(cand), K)]
def rep(a): return np.repeat(a, K)
JSf = JS.ravel()
RS, KS = simulate_gen(JSf, rep(sgn), rep(risk), rep(bb), C[JSf].astype(float), start=1)
RS = RS.reshape(N, K); KS = KS.reshape(N, K)
dec_tw = (RS >= 0) & ~(((CSAT[np.minimum(JSf+KS.ravel(), NB-1)+1] - CSAT[JSf+1]) > 0).reshape(N, K))
Rr, Kr = simulate_gen(ie, sgn, risk, bb, C[ie].astype(float), start=1)
dec_sym = (Rr >= 0) & ~((CSAT[np.minimum(ie+Kr, NB-1)+1] - CSAT[ie+1]) > 0) & tail_ok; tp_sym = (Rr == 1)
say(f"- 双子再現 決着率 {100*(RS>=0).mean():.1f}%（c66 94.9）")

ret = np.zeros(NB); ret[1:] = np.log(np.maximum(C[1:], 1e-9)/np.maximum(C[:-1], 1e-9)); ret[FLAT] = 0.0
CR2 = np.concatenate([[0.0], np.cumsum(ret**2)])
def sig_win(j, a, b_):
    lo_ = np.minimum(j+a, NB-1); hi_ = np.minimum(j+b_, NB-1)
    return np.sqrt((CR2[hi_+1]-CR2[lo_+1]) / np.maximum(CNF[hi_+1]-CNF[lo_+1], 1))
sp_r = sig_win(ie, 0, 12); sp_t = sig_win(JSf, 0, 12).reshape(N, K)
qb = np.quantile(bb[dec], [1/3, 2/3]); bt = np.digitize(bb, qb)
W = {"在2010-20": (yr <= 2020), "外2021-26H1": (yr >= 2021), "近年2024-26H1": (yr >= 2024)}
uday, dinv = np.unique(tr["day"].to_numpy(), return_inverse=True); ND = len(uday)
rows = np.repeat(dinv[:, None], K, 1)

def armlog(sr, st_, hr, ht, B=300):
    a = np.zeros((ND, 4))
    np.add.at(a[:, 0], dinv[sr], hr[sr]); np.add.at(a[:, 1], dinv[sr], 1.0)
    np.add.at(a[:, 2], rows[st_], ht[st_]); np.add.at(a[:, 3], rows[st_], 1.0)
    def f(S):
        s = S.sum(0)
        with np.errstate(divide="ignore", invalid="ignore"): return np.log((s[0]/s[1])/(s[2]/s[3]))
    v = f(a); use = np.flatnonzero(a[:, [1, 3]].sum(1) > 0)
    bs = np.array([f(a[use[rng2.integers(0, len(use), len(use))]]) for _ in range(B)])
    return v, np.nanstd(bs, ddof=1)

say()
say("## D1 b 三分位 × 窓: Δ_post = log(σ_post 実／双子) と 予測 −2Δ vs 観測 腕別")
say("| 窓 | b 三分位 | b̄ | Δ_post | 予測 −2Δ | 観測 TP (c66規約) | 観測 SL (c66規約) | 観測 TP (対称) | 観測 SL (対称) | 観測平均/予測 |")
say("|---|---|---|---|---|---|---|---|---|---|")
res = {}
for wn, wm in W.items():
    for btv, lab in [(0, "下"), (1, "中"), (2, "上")]:
        mb = (bt == btv)
        mr = wm & dec & (hold >= 1) & mb; mt = dec_tw & (wm & mb)[:, None]
        dlt = np.log(sp_r[mr].mean()/sp_t[mt].mean()); pred = -2*dlt
        aT, _ = armlog(mr & tp, mt & (RS == 1), hold.astype(float), KS.astype(float))
        aS, _ = armlog(mr & ~tp, mt & (RS == 0), hold.astype(float), KS.astype(float))
        sT, _ = armlog(dec_sym & wm & mb & tp_sym, mt & (RS == 1), Kr.astype(float), KS.astype(float))
        sS, _ = armlog(dec_sym & wm & mb & ~tp_sym, mt & (RS == 0), Kr.astype(float), KS.astype(float))
        obs = (aT + aS)/2
        res[(wn, btv)] = dict(dlt=dlt, pred=pred, aT=aT, aS=aS, sT=sT, sS=sS, obs=obs)
        say(f"| {wn} | {lab} | {bb[mr].mean():.2f} | {dlt:+.4f} | {pred:+.4f} | {aT:+.4f} | {aS:+.4f} | {sT:+.4f} | {sS:+.4f} | {obs/pred if pred!=0 else float('nan'):.2f} |")

say()
say("## 判定")
for wn in W:
    g_pred = res[(wn, 2)]['pred'] - res[(wn, 0)]['pred']
    g_obsT = res[(wn, 2)]['aT'] - res[(wn, 0)]['aT']
    g_obsS = res[(wn, 2)]['aS'] - res[(wn, 0)]['aS']
    g_symT = res[(wn, 2)]['sT'] - res[(wn, 0)]['sT']
    share = g_pred/g_obsT if g_obsT != 0 else float('nan')
    say(f"- **{wn}**: b 上−下 の **予測勾配 {g_pred:+.4f}** vs **観測勾配 TP {g_obsT:+.4f}／SL {g_obsS:+.4f}（対称規約 TP {g_symT:+.4f}）** "
        f"→ ボラ勾配が観測勾配の {100*share:.0f}% を説明・符号一致 {np.sign(g_pred)==np.sign(g_obsT)}")
g_pred_in = res[("在2010-20", 2)]['pred'] - res[("在2010-20", 0)]['pred']
g_obs_in = res[("在2010-20", 2)]['aT'] - res[("在2010-20", 0)]['aT']
frac = g_pred_in/g_obs_in if g_obs_in != 0 else 0
v = "**A9(ii) 取り下げ（b 勾配はボラ勾配で説明できる）**" if (np.sign(g_pred_in) == np.sign(g_obs_in) and abs(frac) >= 0.5) \
    else "**A9(ii) 維持（ボラでは説明できない b 依存が残る）**"
say(f"\n**D1 判定（在・事前規則 符号一致 ∧ |予測/観測| ≥ 0.50）: 予測/観測 = {frac:+.2f} → {v}**")
out = sum(1 for k_, r in res.items() if not (0.5 <= abs(r['obs']/r['pred']) <= 2.0) if r['pred'] != 0)
say(f"**D2 判定: 観測平均/予測 が [0.5, 2.0] の外 = {out}/9 セル（規則 ≥6 で T2 broken を b 分解でも維持）→ "
    f"{'T2 broken は b 分解でも維持' if out >= 6 else 'b 分解では T2 broken を支持しきれない'}**")
say()
say(f"実行 {time.time()-t0:.1f} s・書き込み data/refute_c66_fpt_d.md・同 _run.log のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L)+"\n")
open(os.path.join(DATA, "refute_c66_fpt_d_run.log"), "w", encoding="utf-8").write("\n".join(L)+"\n")
