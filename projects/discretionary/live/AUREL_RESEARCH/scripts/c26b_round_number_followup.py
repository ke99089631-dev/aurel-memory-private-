# -*- coding: utf-8 -*-
"""
[cycle26 補足 b・事後・記述] 2026-11-10 — c26 の副セル（G=50 の占有低下・接近後の横断率上昇）の頑健性を数字で置く。
判定には使わない（事前固定は c26 本体）。ここで出た形は「新データ 2026-07 以降で再評価する新仮説」の事前固定文に使う。
項目: (1) cont（水準へ向かう平均移動）差の日ブロック bootstrap se／(2) 年別 Δ_X・ρ_O（符号の一貫性）／(3) 地平 N=6/24／
(4) 帯 δ_a=0.5／(5) 下から接近（BUY 側）vs 上から接近（SELL 側）／(6) 00 水準と 50 水準を分ける／(7) 横断後の継続（t+12→t+36 の追加移動）。
入力 data/macro/XAU_m5_close.npz のみ。出力 data/c26b_round_number_followup.md。
"""
import os, time, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c26b_round_number_followup.md"); rng = np.random.default_rng(20261110); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
def utc(x): return dt.datetime.fromtimestamp(int(x), dt.timezone.utc)
say(f"# [cycle26b] キリ番 補足（事後・記述）— {time.strftime('%Y-%m-%d %H:%M')}")
z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
keep = ~np.r_[True, P_ALL[1:] == P_ALL[:-1]]; P = P_ALL[keep]; ts = TS[keep]; day = ts // 86400
year = (np.searchsorted(np.array([dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp() for y in range(2010, 2028)]), ts, side="right") + 2009)
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}

def events(G, th, delta_a, N, only_levels=None, side=None):
    Lnear = np.round((P - th) / G) * G + th; dist = P - Lnear; inb = np.abs(dist) <= delta_a
    cand = np.flatnonzero(inb[1:] & ~inb[:-1]) + 1; cand = cand[(cand >= 1) & (cand + 3 * N < len(P))]
    kept = []; last = -10**9
    for c in cand:
        if c - last > N: kept.append(c); last = c
    kept = np.array(kept, dtype=np.int64); Lk = Lnear[kept]
    if only_levels is not None and th == 0:  # θ=0 の水準を 00 だけ / 50 だけに絞る（プラセボ θ≠0 はそのまま）
        sel = np.isclose(np.mod(Lk, 100), only_levels); kept, Lk = kept[sel], Lk[sel]
    before = np.sign(P[kept - 1] - Lk)
    if side is not None:  # side=-1: 下から接近（before<0）
        sel = before == side; kept, Lk, before = kept[sel], Lk[sel], before[sel]
    after = np.sign(P[kept + N] - Lk); X = ((after == -before) & (before != 0)).astype(float)
    toward = np.sign(Lk - P[kept - 1])
    cont = (P[kept + N] - P[kept - 1]) * toward; cont2 = (P[kept + 3 * N] - P[kept + N]) * toward
    return dict(day=day[kept], year=year[kept], X=X, cont=cont, cont2=cont2)

def compare(G, thetas, delta_a, N, label, only_levels=None, side=None, by_year=False):
    ev = [events(G, th, delta_a, N, only_levels, side) for th in thetas]
    for wn, (lo, hi) in WIN.items():
        rows = [(e["day"][(e["year"] >= lo) & (e["year"] <= hi)], e["X"][(e["year"] >= lo) & (e["year"] <= hi)],
                 e["cont"][(e["year"] >= lo) & (e["year"] <= hi)], e["cont2"][(e["year"] >= lo) & (e["year"] <= hi)]) for e in ev]
        ud = np.unique(np.concatenate([r[0] for r in rows])); nd = len(ud); K = len(thetas)
        A = {k: np.zeros((K, nd)) for k in ("X", "N", "C", "C2")}
        for i, (dd, X, C, C2) in enumerate(rows):
            inv = np.searchsorted(ud, dd); A["X"][i] = np.bincount(inv, weights=X, minlength=nd); A["N"][i] = np.bincount(inv, minlength=nd)
            A["C"][i] = np.bincount(inv, weights=C, minlength=nd); A["C2"][i] = np.bincount(inv, weights=C2, minlength=nd)
        n0, npl = A["N"][0].sum(), A["N"][1:].sum()
        dX = A["X"][0].sum() / n0 - A["X"][1:].sum() / npl; dC = A["C"][0].sum() / n0 - A["C"][1:].sum() / npl; dC2 = A["C2"][0].sum() / n0 - A["C2"][1:].sum() / npl
        idx = rng.integers(0, nd, size=(1500, nd))
        def bse(key):
            b0 = A[key][0][idx].sum(1) / A["N"][0][idx].sum(1); bp = A[key][1:][:, idx].sum((0, 2)) / A["N"][1:][:, idx].sum((0, 2)); return (b0 - bp).std(ddof=1)
        sX, sC, sC2 = bse("X"), bse("C"), bse("C2")
        say(f"- {label} {wn}: n0 {int(n0)}・Δ_X {dX*100:+.2f} pp (z {dX/sX:+.2f})・Δcont(t−1→t+{N}) {dC:+.3f} USD (z {dC/sC:+.2f})・Δcont2(t+{N}→t+{3*N}) {dC2:+.3f} USD (z {dC2/sC2:+.2f})")
        if by_year:
            ys = sorted(set(range(lo, hi + 1)))
            out = []
            for y in ys:
                m0 = ev[0]["year"] == y; mp = np.concatenate([e["year"] == y for e in ev[1:]])
                Xp = np.concatenate([e["X"] for e in ev[1:]]); Cp = np.concatenate([e["cont"] for e in ev[1:]])
                if m0.sum() < 30: continue
                out.append(f"{y}:{(ev[0]['X'][m0].mean()-Xp[mp].mean())*100:+.1f}pp/{ev[0]['cont'][m0].mean()-Cp[mp].mean():+.2f}$ (n{m0.sum()})")
            say("  年別 Δ_X／Δcont: " + " ".join(out))

say("\n## (1)(2) G=50 主形（δ_a=1・N=12）＋年別")
compare(50, list(range(0, 50, 5)), 1.0, 12, "G50", by_year=True)
say("\n## (6) 00 水準だけ／50 水準だけ（G=50 格子の θ=0 を分割・プラセボは θ≠0 全部）")
compare(50, list(range(0, 50, 5)), 1.0, 12, "G50 00のみ", only_levels=0)
compare(50, list(range(0, 50, 5)), 1.0, 12, "G50 50のみ", only_levels=50)
say("\n## (3) 地平 N=6／24（G=50）")
compare(50, list(range(0, 50, 5)), 1.0, 6, "G50 N6")
compare(50, list(range(0, 50, 5)), 1.0, 24, "G50 N24")
say("\n## (4) 帯 δ_a=0.5／2.0（G=50・N=12）")
compare(50, list(range(0, 50, 5)), 0.5, 12, "G50 δ0.5")
compare(50, list(range(0, 50, 5)), 2.0, 12, "G50 δ2.0")
say("\n## (5) 下から接近（上抜け候補）vs 上から接近（下抜け候補）（G=50・δ_a=1・N=12）")
compare(50, list(range(0, 50, 5)), 1.0, 12, "G50 下から", side=-1)
compare(50, list(range(0, 50, 5)), 1.0, 12, "G50 上から", side=+1)
say("\n## 年別 占有 ρ_O（G=50・δ=1）")
for th in [0]:
    pass
inb = {th: ((np.mod(P - th, 50) <= 1.0) | (np.mod(P - th, 50) >= 49.0)) for th in range(0, 50, 5)}
out = []
for y in range(2010, 2027):
    m = year == y; f = np.array([inb[th][m].mean() for th in range(0, 50, 5)]); out.append(f"{y}:{f[0]/f[1:].mean():.3f}")
say("- " + " ".join(out))
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
