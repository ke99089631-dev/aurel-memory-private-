# -*- coding: utf-8 -*-
"""
[REFUTE c12 事後フォロー b] 2026-11-06 — 本編（refute_c12_interval.py）で cycle12 の「区間内 side 差」攻撃は外れた
（β_FE+side 外 +0.134・bootstrap 下限 +0.049・置換 p 0.009）。判定規則は変えない。
ここでは残る混同を同じ区間FE の中で同時に統制して、数字を追加する:
  B1 区間FE + SELL + 金自身 g80×side（tail_gold）+ 直前 24h 継続 A（c8 ret24h_XAU）: β が残るか。
  B2 水平線を区間FE の中で掃く N∈{20,40,60,80,100,120}（各 N の自分の符号区間で FE）: FE が効果を作っていないか（N=20 は cycle10 の null）。
  B3 区間単位（等重み）の検定を「長区間 ≥20 営業日・両側 n≥5」に限って再計算（本編 Q6 の等重みはまたぎ区間の雑音が支配）。
  B4 在 2010-20 を 2010-15／2016-20 に分けて β_FE+side（08:30 B2 の 2016-20 負が側の効果か）。
入力・結合規則は本編と同一。置換なし（数十秒）。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c12_interval_b.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c12 b] 区間FE の中で混同を同時統制 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c12_interval_b.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); N = len(X)
SELL = (SGN < 0).astype(float); YEAR = X["year"].to_numpy()
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
ret24 = X["ret24h_XAU"].to_numpy(); A24 = np.where(np.isfinite(ret24) & (ret24 != 0), (SGN * ret24 > 0).astype(float), np.nan)

def load(sid, NH):
    m = pd.read_csv(os.path.join(MAC, f"{sid}.csv")); m.columns = ["date", "v"]
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    v = m["v"].to_numpy(); D = np.full(len(v), np.nan); D[NH:] = v[NH:] - v[:-NH]
    sg = np.sign(D)
    for k in range(1, len(sg)):
        if sg[k] == 0 and np.isfinite(sg[k - 1]): sg[k] = sg[k - 1]
    iv = np.full(len(v), -1); cur = -1
    for k in range(len(v)):
        if not np.isfinite(sg[k]): continue
        if k == 0 or not np.isfinite(sg[k - 1]) or sg[k] != sg[k - 1]: cur += 1
        iv[k] = cur
    ln = np.bincount(iv[iv >= 0])
    return dict(d=m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), D=D, iv=iv, ln=ln)
def feats(md, ref, tol=10):
    d = md["d"]; i = np.searchsorted(d, ref, side="right") - 1; ok = (i >= 0) & ((ref - d[np.clip(i, 0, None)]) <= tol)
    ii = np.clip(i, 0, len(d) - 1); F = md["D"][ii].copy(); IV = md["iv"][ii].copy(); ok &= np.isfinite(F); F[~ok] = np.nan; IV[~ok] = -1
    LEN = np.where(IV >= 0, md["ln"][np.clip(IV, 0, None)], 0); return F, IV, LEN

# 金自身 g80（08:30 B4 と同じ: XAU_daily_er.csv 土日除外・known ≤ te・許容 5 日）
G = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv")); G["dt"] = pd.to_datetime(G["ts_last"], unit="s")
G = G[~G["dt"].dt.dayofweek.isin([5, 6])].reset_index(drop=True); G["g80"] = G["lc"] - G["lc"].shift(80)
kn = G["known"].to_numpy(); te = X["te"].to_numpy(); gi = np.searchsorted(kn, te, side="right") - 1; gok = gi >= 0
g80 = np.full(N, np.nan); g80[gok] = G["g80"].to_numpy()[gi[gok]]; g80[gok & ((te - kn[np.clip(gi, 0, None)]) > 5 * 86400)] = np.nan
TG = np.where(np.isfinite(g80) & (g80 != 0), (SGN * g80 > 0).astype(float), np.nan)  # 金自身のトレンドに乗る本

W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024, "2010-15": (YEAR <= 2015), "2016-20": (YEAR >= 2016) & (YEAR <= 2020)}
def within(v, g):
    df = pd.DataFrame({"v": v, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def ols_cluster(y, Z, cl):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); G_ = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G_ += 1
    V = ZtZi @ meat @ ZtZi * (G_ / max(G_ - 1, 1)); return beta, np.sqrt(np.diag(V)), G_
def fe(mask, iv, cols):
    m = mask & (iv >= 0)
    for c in cols: m &= np.isfinite(c)
    y = within(R[m], iv[m]); Z = np.column_stack([within(c[m], iv[m]) for c in cols]); b, se, G_ = ols_cluster(y, Z, iv[m])
    return b, b / np.where(se > 0, se, np.nan), G_, int(m.sum())

for sid in ("DGS10", "DFII10"):
    md = load(sid, 80); F, IV, LEN = feats(md, AVAIL); ok = IV >= 0; tail = np.where(ok, ((SGN * np.sign(F) * -1) > 0).astype(float), np.nan)
    say(f"\n# ===== {sid} =====")
    say("\n## B1 区間FE + SELL + 金自身 g80×side + 直前 24h 継続（係数: tail_rate / SELL / tail_gold / A24）")
    for wn in ("在2010-20", "外2021-26", "近年2024-26"):
        wm = W[wn]
        b0, t0, G0, n0 = fe(wm & ok, IV, [tail, SELL])
        b1, t1, G1, n1 = fe(wm & ok, IV, [tail, SELL, TG])
        b2, t2, G2, n2 = fe(wm & ok, IV, [tail, SELL, TG, A24])
        say(f"- {wn}: 基準 tail {b0[0]:+.4f} (t{t0[0]:+.2f}, n{n0}) | +g80: tail **{b1[0]:+.4f} (t{t1[0]:+.2f})** tail_gold {b1[2]:+.4f} (t{t1[2]:+.2f}) n{n1} | "
            f"+g80+A24: tail **{b2[0]:+.4f} (t{t2[0]:+.2f})** tail_gold {b2[2]:+.4f} (t{t2[2]:+.2f}) A24 {b2[3]:+.4f} (t{t2[3]:+.2f}) n{n2}")
        mm = wm & ok & np.isfinite(TG); say(f"    ρ(tail_rate, tail_gold) {np.corrcoef(tail[mm], TG[mm])[0,1]:+.3f}")

    say("\n## B2 水平線を各 N の自分の符号区間で FE（区間FE+SELL・tail 係数）")
    for NH in (20, 40, 60, 80, 100, 120, 180):
        mdn = load(sid, NH); Fn, IVn, _ = feats(mdn, AVAIL); okn = IVn >= 0; tn = np.where(okn, ((SGN * np.sign(Fn) * -1) > 0).astype(float), np.nan)
        row = []
        for wn in ("在2010-20", "外2021-26", "近年2024-26"):
            b, t, G_, n = fe(W[wn] & okn, IVn, [tn, SELL]); row.append(f"{wn} {b[0]:+.4f} (t{t[0]:+.2f}, 区間 {G_})")
        say(f"- N={NH:3d}: " + " / ".join(row))

    say("\n## B3 区間単位・等重み（長区間 ≥20 営業日 ∧ 両側 n≥5）: 区間内 tail−head")
    for wn in ("在2010-20", "外2021-26", "近年2024-26"):
        m = W[wn] & ok & (LEN >= 20); ths = []; ns = []
        for i_ in np.unique(IV[m]):
            mi = m & (IV == i_); rb = R[mi & (SELL == 0)]; rs = R[mi & (SELL > 0)]
            if len(rb) >= 5 and len(rs) >= 5:
                ths.append((rs.mean() - rb.mean()) if F[mi].mean() > 0 else (rb.mean() - rs.mean())); ns.append(mi.sum())
        ths = np.array(ths); ns = np.array(ns)
        if len(ths) >= 3:
            tw = (ths * ns).sum() / ns.sum()
            say(f"- {wn}: {len(ths)} 区間、等重み平均 {ths.mean():+.4f} (t{ths.mean()/(ths.std(ddof=1)/math.sqrt(len(ths))):+.2f})、正 {int((ths>0).sum())}/{len(ths)}（二項 両側 p {2*min(sum(math.comb(len(ths),k) for k in range(int((ths>0).sum()), len(ths)+1)), sum(math.comb(len(ths),k) for k in range(0, int((ths>0).sum())+1)))/2**len(ths):.3f}）、本加重 {tw:+.4f}、中央値 {np.median(ths):+.4f}")

    say("\n## B4 在の 2 分割（区間FE+SELL）")
    for wn in ("2010-15", "2016-20"):
        b, t, G_, n = fe(W[wn] & ok, IV, [tail, SELL]); say(f"- {wn}: tail {b[0]:+.4f} (t{t[0]:+.2f}, 区間 {G_}, n{n}) SELL {b[1]:+.4f} (t{t[1]:+.2f})")

say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
