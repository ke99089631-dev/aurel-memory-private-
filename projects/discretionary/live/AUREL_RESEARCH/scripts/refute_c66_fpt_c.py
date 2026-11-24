# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-24 21:30・第 3 走] 第 2 走の B3 の自己訂正。

B3 は累積発生率 CI_a(k) = P(k 足以内に腕 a で決着 | 全本) を使ったが、これは
**「腕 a がどれだけ起きるか（確率）」と「どれだけ速く起きるか（時間）」を混ぜている**。
実際 在 k=192 で 実 TP 43.61% vs 双子 46.34%・実 SL 46.21% vs 双子 44.26% ＝
実本は双子より TP が少なく SL が多い（＝方向の差・c35 の早期赤字の領域）。
この腕確率の差だけで CI_TP(k) は全 k で負・CI_SL(k) は全 k で正になりうるので、
B3 の「k=6 で既に −2.00pp (t −5.01)」は**時間の証拠として使えない**。私の B3 判定は取り下げる。

第 3 走の事前固定（数字を見る前に書いた）:
  C1 腕確率（時間ではない量・混同の大きさを測る）: P(TP | 全本)・P(SL | 全本)・P(TIME) を
     実本・双子・窓別に出し差を pp と日クラスタ bootstrap t で印字。判定なし（記述）。
     ただし ΔP(TP) が有意なら「B3 の符号は腕確率で説明できる」ことの直接証拠として記録。
  C2 打ち切り不変かつ腕確率に不変な形（T1 の大きさの正しい検定）:
     F_a(k) = P(hold ≤ k | 腕 a・288 足以内に決着)。288 打ち切りは両群同一で窓全体が観測されるので
     打ち切りに不変・分母を腕内に取るので腕確率にも不変。k ∈ {3,6,12,24,48,96,192} で差（pp）と se。
     規則（事前）: k ≤ 24 のいずれかで |差| ≥ 2pp ∧ |t| ≥ 3 → **T1 は典型的決着時間の主張として survived**。
       k ≤ 96 のすべてで |差| ≤ 1.5pp ∧ |t| < 2 → **T1 の「10〜15% 速い」は大きさの主張として broken**
       （内容は「>96 足の裾が薄い」だけ）。それ以外は「中間」。
  C3 平均の分解（「10〜15%」がどこから来るか）: mean hold を k ≤ 96 の部分と k > 96 の部分に分解し、
     腕別 log(実/双) への寄与を出す。規則なし（記述）。ただし寄与の >60% が k>96 から来るなら
     C2 の結論を「裾優位」と明記する。
  C4 同じ分解を B1 の完全対称規約（実本も終値建玉）でも実行し、規約を跨いで同じ結論になるか確認。
seed 20261124（双子は c66 と同一再現）。書き込み data/refute_c66_fpt_c.md・同 _run.log のみ。
発注・本番編集・プロセス/MT5/プロップ・外部通信 なし。
"""
import os, json, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c66_fpt_c.md")
rng = np.random.default_rng(20261124); rng2 = np.random.default_rng(20261124 + 0x52)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c66・第 3 走] B3 の自己訂正: 腕確率と決着時間を分離 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c66_fpt_c.py)")

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
CSAT = np.concatenate([[0], np.cumsum((((TS // 86400) + 3) % 7 == 5).astype(np.int64))])
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
        sl_hit = np.where(buy[:, None], ll <= (sl+ft)[:, None], hh >= (sl-ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tpv+ft)[:, None], ll <= (tpv-ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
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
W = {"在2010-20": (yr <= 2020), "外2021-26H1": (yr >= 2021), "近年2024-26H1": (yr >= 2024)}
uday, dinv = np.unique(tr["day"].to_numpy(), return_inverse=True); ND = len(uday)
rows = np.repeat(dinv[:, None], K, 1)
say(f"- 双子再現: 決着率 {100*(RS>=0).mean():.1f}%（c66 94.9）")

def clus(sel_r, sel_t):
    a = np.zeros(ND); np.add.at(a, dinv[sel_r], 1.0)
    b = np.zeros(ND); np.add.at(b, rows[sel_t], 1.0)
    return a, b
def diff_pp(nr, dr_, nt, dt_, B=600):
    M = np.column_stack([nr, dr_, nt, dt_])
    def f(S):
        s = S.sum(0)
        return 100*(s[0]/max(s[1], 1e-9) - s[2]/max(s[3], 1e-9))
    v = f(M); bs = np.array([f(M[rng2.integers(0, ND, ND)]) for _ in range(B)])
    s = M.sum(0)
    return 100*s[0]/max(s[1], 1e-9), 100*s[2]/max(s[3], 1e-9), v, np.nanstd(bs, ddof=1)

# ---------------- C1 腕確率 ----------------
say()
say("## C1 腕確率（時間ではない量・B3 の混同の大きさ）: P(腕 | 全本)")
say("| 窓 | 量 | 実% | 双子% | 差 pp (t) |")
say("|---|---|---|---|---|")
for wn, wm in W.items():
    dr_, dt_ = clus(wm, np.broadcast_to(wm[:, None], (N, K)))
    for lab, sr, st_ in [("P(TP)", wm & dec & tp, dec_tw & wm[:, None] & (RS == 1)),
                         ("P(SL)", wm & dec & ~tp, dec_tw & wm[:, None] & (RS == 0)),
                         ("P(TIME)", wm & ~dec, np.broadcast_to(wm[:, None], (N, K)) & ~dec_tw)]:
        nr, nt = clus(sr, st_)
        pr, pt_, v, se = diff_pp(nr, dr_, nt, dt_)
        say(f"| {wn} | {lab} | {pr:.2f} | {pt_:.2f} | {v:+.2f} ({v/max(se,1e-9):+.2f}) |")
say("\n→ 腕確率の差が有意なら、第 2 走 B3 の CI_a(k) の符号（TP 全 k で負・SL 全 k で正）は腕確率で説明できる。**B3 の判定は取り下げる。**")

# ---------------- C2 腕内の条件付き CDF（打ち切り・腕確率の両方に不変） ----------------
KSET = [3, 6, 12, 24, 48, 96, 192]
def cdf_table(label, hr, tpr, decr, ht, rs, dect):
    say()
    say(f"### {label}")
    res = {}
    for wn, wm in W.items():
        if wn == "近年2024-26H1": continue
        say(f"**{wn}**")
        say("| k | TP 実% | TP 双子% | 差 pp (t) | SL 実% | SL 双子% | 差 pp (t) |")
        say("|---|---|---|---|---|---|---|")
        for arm in [1, 0]:
            pass
        out = {}
        for arm, an in [(1, "TP"), (0, "SL")]:
            selr_all = wm & decr & (hr >= 1) & (tpr if arm == 1 else ~tpr)
            selt_all = dect & wm[:, None] & (rs == arm)
            dr_, dt_ = clus(selr_all, selt_all)
            out[an] = []
            for k in KSET:
                nr, nt = clus(selr_all & (hr <= k), selt_all & (ht <= k))
                out[an].append(diff_pp(nr, dr_, nt, dt_))
        for i, k in enumerate(KSET):
            a = out["TP"][i]; b = out["SL"][i]
            say(f"| {k} | {a[0]:.2f} | {a[1]:.2f} | {a[2]:+.2f} ({a[2]/max(a[3],1e-9):+.2f}) | {b[0]:.2f} | {b[1]:.2f} | {b[2]:+.2f} ({b[2]/max(b[3],1e-9):+.2f}) |")
        res[wn] = out
    return res
say()
say("## C2 F_a(k) = P(hold ≤ k | 腕 a・決着) — 打ち切りにも腕確率にも不変な T1 の大きさの検定")
r_c66 = cdf_table("C2a c66 の規約（実本 = scan そのまま・hold≥1）", hold, tp, dec, KS, RS, dec_tw)

def verdict(res):
    early = False; allsmall = True; mx = {}
    for wn, out in res.items():
        for an, rr in out.items():
            best = max(zip(KSET, rr), key=lambda x: abs(x[1][2])); mx[(wn, an)] = best[0]
            for k, (pr, pt_, v, se) in zip(KSET, rr):
                t_ = abs(v/max(se, 1e-9))
                if k <= 24 and abs(v) >= 2 and t_ >= 3: early = True
                if k <= 96 and (abs(v) > 1.5 or t_ >= 2): allsmall = False
    if early: return "**survived（典型的決着時間の主張として）**", mx
    if allsmall: return "**broken（大きさの主張として・内容は >96 足の裾のみ）**", mx
    return "中間（裾優位だが k≤96 でも無視できない差が残る）", mx
v2a, mx2a = verdict(r_c66)
say(f"\n**C2a 判定: T1 は {v2a}**（|差| 最大の k: " + "・".join(f"{w}/{a}→{k}" for (w, a), k in mx2a.items()) + "）")

# C4: 完全対称規約でも同じか
Rr, Kr = simulate_gen(ie, sgn, risk, bb, C[ie].astype(float), start=1)
sat_r = (CSAT[np.minimum(ie+Kr, NB-1)+1] - CSAT[ie+1]) > 0
dec_sym = (Rr >= 0) & ~sat_r & tail_ok; tp_sym = (Rr == 1)
say()
say("## C4 同じ検定を完全対称規約（実本も終値建玉・第 2 走 B1）で")
r_sym = cdf_table("C4a 完全対称規約", Kr, tp_sym, dec_sym, KS, RS, dec_tw)
v4a, mx4a = verdict(r_sym)
say(f"\n**C4 判定: T1 は {v4a}**（|差| 最大の k: " + "・".join(f"{w}/{a}→{k}" for (w, a), k in mx4a.items()) + "）")

# ---------------- C3 平均の分解 ----------------
say()
say("## C3 平均の分解: log(実/双) のうち k>96 の裾が占める寄与")
say("| 規約 | 窓 | 腕 | 全 log(実/双) | k≤96 に打ち切った log(実/双) | 裾(>96)の寄与 | 裾シェア |")
say("|---|---|---|---|---|---|---|")
for cname, hr, tpr, decr in [("c66 規約", hold, tp, dec & (hold >= 1)), ("完全対称", Kr, tp_sym, dec_sym)]:
    for wn, wm in W.items():
        if wn == "近年2024-26H1": continue
        for arm, an in [(1, "TP"), (0, "SL")]:
            sr = wm & decr & (tpr if arm == 1 else ~tpr)
            st_ = dec_tw & wm[:, None] & (RS == arm)
            full = np.log(hr[sr].mean()/KS[st_].mean())
            cap_r = np.minimum(hr[sr], 96).mean(); cap_t = np.minimum(KS[st_], 96).mean()
            capd = np.log(cap_r/cap_t)
            say(f"| {cname} | {wn} | {an} | {full:+.4f} | {capd:+.4f} | {full-capd:+.4f} | {100*(full-capd)/full if full != 0 else float('nan'):.0f}% |")

say()
say(f"実行 {time.time()-t0:.1f} s・書き込み data/refute_c66_fpt_c.md・同 _run.log のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L)+"\n")
open(os.path.join(DATA, "refute_c66_fpt_c_run.log"), "w", encoding="utf-8").write("\n".join(L)+"\n")
