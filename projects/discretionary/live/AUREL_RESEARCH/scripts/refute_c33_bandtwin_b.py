# -*- coding: utf-8 -*-
"""
[反証レーン 2026-11-10 補足 b・事後・記述] refute_c33_bandtwin.py の結果を見た後の追加検査（判定には使わない）
  (1) 帯 SELL（外 p_fw 0.042）の年別・半期別・基準別（S／T／TC）＝ 1 期間が作っているか・設計依存か
  (2) 帯外の負の時刻局在（jh1-3 が 3 窓とも −4〜−5 pp）を基準別（S／T／TC）・4 窓で再印字
  (3) 帯の x̄_emp が基準で符号を変える（在 S +0.50／T −0.64／TC +0.65）＝帯の「0 ± 1 pp」の設計依存幅
双子は本体と同じ seed・同じ乱数消費順で再生成（本体と同一の JS／JSC／JT／JTC）。書き込み data/refute_c33_bandtwin_b.md のみ。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c33_bandtwin_b.md")
rng = np.random.default_rng(20261110)
L = []
def say(s=""): print(s, flush=True); L.append(s)

d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = float(d["frozen"]["FEED_TOL"]); MAXH = int(d["frozen"]["MAX_HOLD"])
tr = pd.DataFrame(d["trades"])
tr["ts"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True).dt.tz_convert(None)
tr["day"] = tr["ts"].dt.floor("D")
tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["tp"] = (tr["exit"] == "TP").astype(float)
tr["sgn"] = np.where(tr["side"] == "BUY", 1.0, -1.0)
tr["band"] = tr["jh"].between(7, 12)
N = len(tr)
z = np.load(os.path.join(DATA, "macro", "XAU_m5_ohlc.npz"))
TS = z["ts"].astype(np.int64); H, Lo, C = z["high"], z["low"], z["close"]
NB = len(TS)
ie = np.searchsorted(TS, tr["entry_time"].to_numpy(np.int64))
AR = np.arange(1, MAXH + 1)
def simulate(j, sgn, risk, b, ft=FT, chunk=1200):
    M = len(j); out = np.full(M, -1, np.int8)
    for s in range(0, M, chunk):
        sl_ = slice(s, min(M, s + chunk)); jj = j[sl_]; sg = sgn[sl_]; rk = risk[sl_]; bb = b[sl_]
        idx = jj[:, None] + AR[None, :]; hh = H[idx]; ll = Lo[idx]; ent = C[jj]
        sl = ent - sg * rk; tp = ent + sg * bb * rk; buy = sg > 0
        sl_hit = np.where(buy[:, None], ll <= (sl + ft)[:, None], hh >= (sl - ft)[:, None])
        tp_hit = np.where(buy[:, None], hh >= (tp + ft)[:, None], ll <= (tp - ft)[:, None])
        ks = np.where(sl_hit.any(1), sl_hit.argmax(1), 10**6); kt = np.where(tp_hit.any(1), tp_hit.argmax(1), 10**6)
        res = np.full(len(jj), -1, np.int8); res[(kt < ks)] = 1; res[(ks <= kt) & (ks < 10**6)] = 0; out[sl_] = res
    return out
K = 16; SPAN_S = 28 * 288; SPAN_A = 5760
sgn = tr["sgn"].to_numpy(); risk = tr["risk"].to_numpy(float); bb = tr["b"].to_numpy(float); jh = tr["jh"].to_numpy(int)
FLAT = (H == Lo); ATR = pd.Series(H - Lo).rolling(14).mean().shift(1).to_numpy(); RNG_BAR = H - Lo
HOUR = ((TS // 3600) + 9) % 24
valid = ~FLAT & (np.arange(NB) <= NB - MAXH - 2); NF = np.flatnonzero(valid)
JS = np.empty((N, K), np.int64); JSC = np.empty((N, K), np.int64); a_e = ATR[ie]; CANDS = [None] * N
for h in range(24):
    NFh = NF[HOUR[NF] == h]; ii = np.flatnonzero(jh == h)
    lo = np.searchsorted(NFh, np.maximum(ie[ii] - SPAN_S, 0)); hi = np.searchsorted(NFh, ie[ii] + SPAN_S)
    for t_, i in enumerate(ii):
        cand = NFh[lo[t_]:hi[t_]]; cand = cand[cand != ie[i]]
        if len(cand) == 0: cand = NFh[max(lo[t_]-50,0):hi[t_]+50]; cand = cand[cand != ie[i]]
        CANDS[i] = cand; JS[i] = cand[rng.integers(0, len(cand), K)]
        la = np.log(np.where(ATR[cand] > 0, ATR[cand], np.nan) / a_e[i]) if a_e[i] > 0 else np.full(len(cand), np.nan)
        m = np.abs(la) < 0.2
        if m.sum() < K: m = np.abs(la) < 0.4
        if m.sum() < 1: m = np.ones(len(cand), bool)
        cc = cand[m]; JSC[i] = cc[rng.integers(0, len(cc), K)]
pa_lo = np.searchsorted(NF, np.maximum(ie - SPAN_A, 0)); pa_hi = np.maximum(np.searchsorted(NF, ie + SPAN_A), pa_lo + 1)
_JA = NF[np.minimum((pa_lo[:, None] + rng.random((N, K)) * (pa_hi - pa_lo)[:, None]).astype(np.int64), len(NF) - 1)]
JT = np.empty((N, K), np.int64); JTC = np.empty((N, K), np.int64); r_e = RNG_BAR[ie]
for i in range(N):
    cand = CANDS[i]
    lr = np.log(np.where(RNG_BAR[cand] > 0, RNG_BAR[cand], np.nan) / r_e[i]) if r_e[i] > 0 else np.full(len(cand), np.nan)
    m = np.abs(lr) < 0.2
    if m.sum() < K: m = np.abs(lr) < 0.4
    if m.sum() < 1: m = np.ones(len(cand), bool)
    cc = cand[m]; JT[i] = cc[rng.integers(0, len(cc), K)]
    la = np.log(np.where(ATR[cand] > 0, ATR[cand], np.nan) / a_e[i]) if a_e[i] > 0 else np.full(len(cand), np.nan)
    m2 = m & (np.abs(la) < 0.3)
    if m2.sum() < K: m2 = m & (np.abs(la) < 0.6)
    if m2.sum() < 1: m2 = m
    cc = cand[m2]; JTC[i] = cc[rng.integers(0, len(cc), K)]
def rep(a): return np.repeat(a, K)
R = {nm: simulate(J.ravel(), rep(sgn), rep(risk), rep(bb)).reshape(N, K) for nm, J in (("S", JS), ("SC", JSC), ("T", JT), ("TC", JTC))}
def qemp(Rm):
    ntp = (Rm == 1).sum(1); nsl = (Rm == 0).sum(1); dec_ = ntp + nsl
    return np.where(dec_ > 0, ntp / np.maximum(dec_, 1), np.nan)
QE = {nm: qemp(R[nm]) for nm in R}
def clus(vals, days, nboot=1000):
    s = pd.DataFrame({"v": vals, "d": days}).groupby("d")["v"].agg(["sum", "size"])
    S = s["sum"].to_numpy(float); Nn = s["size"].to_numpy(float); G = len(S)
    if G < 2: return (vals.mean() if len(vals) else np.nan), np.nan, np.nan
    m = S.sum() / Nn.sum(); pick = rng.integers(0, G, (nboot, G)); bs = S[pick].sum(1) / Nn[pick].sum(1)
    se = bs.std(ddof=1); return m, se, (m / se if se > 0 else np.nan)
dec = tr["dec"].to_numpy(); tp = tr["tp"].to_numpy(); days = tr["day"].to_numpy(); band = tr["band"].to_numpy()
side = tr.side.to_numpy(); year = tr.year.to_numpy()
say(f"# [反証 cycle33 補足 b・事後・記述] 帯 SELL の年別／基準別・帯外の時刻局在・帯の設計依存幅 — {time.strftime('%Y-%m-%d %H:%M')}")
say(f"再現確認: 外 帯 SELL S {100*(tp - QE['S'])[(year>=2021)&band&dec&(side=='SELL')&~np.isnan(QE['S'])].mean():+.2f} pp（本体 +5.05）")
say()
say("## (1) 帯 SELL x̄_emp pp (t) n — 年別（S）と 期間別×基準別")
rows = []
for y in range(2010, 2027):
    m = (year == y) & band & dec & (side == "SELL") & ~np.isnan(QE["S"]); x, se, t = clus(tp[m] - QE["S"][m], days[m], 400); rows.append(f"{y}: {100*x:+.1f} ({t:+.1f}) n{m.sum()}")
say("年別 S: " + "; ".join(rows))
say("| 期間 | side | S | T | TC | SC |"); say("|---|---|---|---|---|---|")
PER = {"在2010-20": year <= 2020, "2021-23": (year >= 2021) & (year <= 2023), "2024-25": (year >= 2024) & (year <= 2025), "2026H1": year == 2026, "外2021-26": year >= 2021, "外 ex-2026": (year >= 2021) & (year <= 2025)}
for pn, pm in PER.items():
    for sd_ in ("SELL", "BUY"):
        cells = []
        for nm in ("S", "T", "TC", "SC"):
            m = pm & band & dec & (side == sd_) & ~np.isnan(QE[nm]); x, se, t = clus(tp[m] - QE[nm][m], days[m]); cells.append(f"{100*x:+.2f} ({t:+.2f}) n{m.sum()}")
        say(f"| {pn} | {sd_} | " + " | ".join(cells) + " |")
say()
say("## (2) 帯外の時刻ブロック x̄_emp pp (t) — 基準別（S／T／TC）・3 窓＋4 窓")
BLK = {"jh13-15": (13, 15), "jh16-18": (16, 18), "jh19-21": (19, 21), "jh22-24": (22, 24), "jh1-3": (1, 3), "jh4-6": (4, 6)}
WIN = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024, "2010-14": (year <= 2014), "2015-20": (year >= 2015) & (year <= 2020), "2021-23": (year >= 2021) & (year <= 2023)}
say("| 窓 | 基準 | " + " | ".join(BLK) + " |"); say("|---|---|" + "---|" * len(BLK))
for wn, wm in WIN.items():
    for nm in ("S", "T", "TC"):
        cells = []
        for bn, (a, b_) in BLK.items():
            hm = ((jh >= a) & (jh <= b_)) | ((b_ == 24) & (jh == 0))
            m = wm & hm & dec & ~np.isnan(QE[nm]); x, se, t = clus(tp[m] - QE[nm][m], days[m], 600); cells.append(f"{100*x:+.2f} ({t:+.2f})")
        say(f"| {wn} | {nm} | " + " | ".join(cells) + " |")
say()
# jh1-3 を side 別・wall 別で（記述）
say("jh1-3（3 窓同符号の塊）を side／wall で（S・pp (t) n）:")
hm13 = (jh >= 1) & (jh <= 3)
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    wm = WIN[wn]; cells = []
    for lab, mm in (("BUY", side == "BUY"), ("SELL", side == "SELL"), ("mid", tr.wall_kind.to_numpy() == "mid"), ("outer", tr.wall_kind.to_numpy() == "outer")):
        m = wm & hm13 & mm & dec & ~np.isnan(QE["S"]); x, se, t = clus(tp[m] - QE["S"][m], days[m], 600); cells.append(f"{lab} {100*x:+.2f} ({t:+.2f}) n{m.sum()}")
    say(f"- {wn}: " + "・".join(cells))
say()
say("## (3) 帯の x̄_emp の設計依存幅（S／T／TC／SC・pp (t)）と 4 基準の範囲")
for wn in ("在2010-20", "外2021-26", "近年2024-26"):
    wm = WIN[wn]; vals = []
    for nm in ("S", "T", "TC", "SC"):
        m = wm & band & dec & ~np.isnan(QE[nm]); x, se, t = clus(tp[m] - QE[nm][m], days[m]); vals.append((nm, x, t))
    say(f"- {wn}: " + "・".join(f"{nm} {100*x:+.2f} ({t:+.2f})" for nm, x, t in vals) + f" → 範囲 {100*(max(v[1] for v in vals)-min(v[1] for v in vals)):.2f} pp")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
