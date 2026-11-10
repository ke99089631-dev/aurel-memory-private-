# -*- coding: utf-8 -*-
"""
[REFUTE c32 補足 b] R0 の決着 — 研究レーン c32b と同じ乱数列（rng(20261110) で SET C を最初に引く）で ΔL_post 在/外 を再現し、
さらに K=4 の抽選 seed を 12 通り変えて SET C（マスク有り）と SET D（マスク無し）の ΔL_post・残差の抽選ばらつき（sd）を印字する。
研究レーンの t は抽選のばらつきを含まない（本ごとの対数差の日クラスタ se のみ）。seed 20261110 + 12 seeds。
出力: data/refute_c32_breakvol_b.md
"""
import os, json, time
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c32_breakvol_b.md"); NY = "America/New_York"; L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c32 補足 b] R0 決着（同一乱数列）＋抽選ばらつき — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c32_breakvol_b.py)")
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float); H = z["high"].astype(float); Lo = z["low"].astype(float)
NB = len(ts); r = np.zeros(NB); r[1:] = np.diff(C); flat = r == 0.0; RNG = H - Lo
dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
SLOT = (dt_ny.hour.to_numpy() * 12 + dt_ny.minute.to_numpy() // 5).astype(np.int32); WD = dt_ny.weekday.to_numpy().astype(np.int8)
sess = dt_ny + pd.Timedelta(hours=6); SESS = sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy()
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True)
pos = np.clip(np.searchsorted(ts, T["entry_time"].to_numpy()), 0, NB - 1); ok = ts[pos] == T["entry_time"].to_numpy()
T = T[ok].reset_index(drop=True); I0 = pos[ok]; YEAR = T["year"].to_numpy()
PRE = np.arange(-12, 0); POST = np.arange(1, 13)
okb = (I0 - 12 >= 0) & (I0 + 36 < NB); I2 = np.where(okb, I0, 100)
VAL = okb & (SESS[I2 - 12] == SESS[I2]) & (SESS[I2 + 36] == SESS[I2]) & (flat[I2[:, None] + POST[None, :]].sum(1) <= 3) & (WD[I2] <= 4)
near = np.zeros(NB, dtype=bool)
for d in range(-12, 13): near[np.clip(I0 + d, 0, NB - 1)] = True
IV = I0[VAL]; DAY = (T["entry_time"].to_numpy()[VAL] // 86400); YR = YEAR[VAL]
K = 4; D = np.array([d for d in range(-28, 29) if d != 0])
Cd = np.clip(IV[:, None] + 288 * D[None, :], 13, NB - 37)
base = (SLOT[Cd] == SLOT[IV][:, None]) & (WD[Cd] <= 4) & (~flat[Cd]) & (SESS[Cd - 12] == SESS[Cd]) & (SESS[Cd + 36] == SESS[Cd])
base &= flat[Cd[:, :, None] + POST[None, None, :]].sum(2) <= 3
def vwin(I, W): return np.sqrt((r[np.asarray(I)[:, None] + W[None, :]] ** 2).mean(1))
Vp_t = vwin(IV, PRE); Vp_c = np.sqrt((r[Cd[:, :, None] + PRE[None, None, :]] ** 2).mean(2)); qp = Vp_c / np.maximum(Vp_t[:, None], 1e-9)
qr = RNG[Cd] / np.maximum(RNG[IV][:, None], 1e-9)
def okmat(m_pre, m_range, use_near):
    okc = base & (~near[Cd] if use_near else True)
    t_ = np.ones_like(okc); w_ = np.ones_like(okc)
    if m_pre: t_ &= (qp >= 0.8) & (qp <= 1.25); w_ &= (qp >= 0.67) & (qp <= 1.5)
    if m_range: t_ &= (qr >= 0.8) & (qr <= 1.25); w_ &= (qr >= 0.67) & (qr <= 1.5)
    ok1 = okc & t_; ok2 = okc & w_
    return np.where((ok1.sum(1) >= K)[:, None], ok1, ok2)
def draw(okc, rng):
    P = np.full((len(IV), K), -1, dtype=np.int64)
    for q in range(len(IV)):
        c = Cd[q][okc[q]]
        if len(c) >= K: P[q] = rng.choice(c, size=K, replace=False)
    return P, (P >= 0).all(1)
def lg(x): return np.log(np.maximum(x, 1e-6))
def ct(d, day):
    d = np.asarray(d, float); n = len(d); m = d.mean(); s = pd.DataFrame({"d": d - m, "g": day}).groupby("g")["d"].sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / n; return m, se, m / se
def evalset(P, okP):
    I = IV[okP]; Pk = P[okP]; yr = YR[okP]; day = DAY[okP]
    Vo = vwin(I, POST); Vp = vwin(I, PRE)
    lVo = np.mean([lg(vwin(Pk[:, k], POST)) for k in range(K)], 0); lVp = np.mean([lg(vwin(Pk[:, k], PRE)) for k in range(K)], 0)
    dpost = lg(Vo) - lVo; dpre = lg(Vp) - lVp; out = {}
    for w, (y0, y1) in {"在": (2010, 2020), "外": (2021, 2026)}.items():
        m = (yr >= y0) & (yr <= y1); out[w] = (ct(dpost[m], day[m]), ct(dpre[m], day[m]), ct(dpost[m] - dpre[m], day[m]))
    return out
# (1) 研究レーンと同一の乱数列: c32b は rng(20261110) で最初に SET C を引く
okC = okmat(True, False, True); P, okP = draw(okC, np.random.default_rng(20261110)); e = evalset(P, okP)
say(f"- 同一乱数列 SET C: 在 ΔL_post {e['在'][0][0]:+.4f} (t {e['在'][0][2]:+.2f})・ΔL_pre {e['在'][1][0]:+.4f} (t {e['在'][1][2]:+.2f})／外 ΔL_post {e['外'][0][0]:+.4f} (t {e['外'][0][2]:+.2f})・ΔL_pre {e['外'][1][0]:+.4f}；研究レーン 在 +0.0368 (t 7.37)・+0.0226 (t 20.04)／外 +0.0295 (t 5.20)・+0.0119 → {'一致' if abs(e['在'][0][0]-0.0368)<0.0005 and abs(e['在'][0][2]-7.37)<0.05 else '不一致'}")
# (2) 抽選ばらつき
okD0 = okmat(True, True, False)
rowsC = []; rowsD = []
for s in range(12):
    P, okP = draw(okC, np.random.default_rng(1000 + s)); e = evalset(P, okP); rowsC.append([e['在'][0][0], e['在'][2][0], e['外'][0][0], e['外'][2][0]])
    P, okP = draw(okD0, np.random.default_rng(1000 + s)); e = evalset(P, okP); rowsD.append([e['在'][0][0], e['在'][2][0], e['外'][0][0], e['外'][2][0]])
rowsC = np.array(rowsC); rowsD = np.array(rowsD)
for nm, A in [("SET C マスク有り（研究レーン補足 b）", rowsC), ("SET D マスク無し（反証 主）", rowsD)]:
    say(f"- {nm} 12 抽選: 在 ΔL_post 平均 {A[:,0].mean():+.4f} sd {A[:,0].std(ddof=1):.4f}［範囲 {A[:,0].min():+.4f}〜{A[:,0].max():+.4f}］・在 残差 平均 {A[:,1].mean():+.4f} sd {A[:,1].std(ddof=1):.4f}［{A[:,1].min():+.4f}〜{A[:,1].max():+.4f}］"
        f"／外 ΔL_post 平均 {A[:,2].mean():+.4f} sd {A[:,2].std(ddof=1):.4f}・外 残差 平均 {A[:,3].mean():+.4f} sd {A[:,3].std(ddof=1):.4f}［{A[:,3].min():+.4f}〜{A[:,3].max():+.4f}］")
say(f"- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
