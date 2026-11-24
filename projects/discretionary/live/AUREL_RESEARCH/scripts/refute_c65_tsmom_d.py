# -*- coding: utf-8 -*-
"""
[REFUTE c65 part D 2026-11-24] part C2 で US500 在 2014-20 の VR(2)=0.901 が
**iid ブートストラップ帰無では両側 p 0.000**（帰無中央値 1.000）になった。
c65 は「VR(q) 2〜63 日は 3 窓とも |z|≤1.4 で随機歩行を棄却しない」と結論しており、これと矛盾する。

**ただし iid ブートストラップは VR の正しい帰無ではない**（日次リターンのボラ・クラスタリングを破壊するため
VR 推定量の分散を過小評価する。Lo–MacKinlay の不均一分散頑健 z はまさにそれを補正する統計量）。
→ part D は**正しい帰無**で決着させる。自分の part C の p 0.000 を自分で壊す。

=== 事前固定 ===
D1 **符号ランダム化帰無**: r_t → s_t·r_t（s_t = ±1 iid）。|r_t| の時系列（＝ボラ・クラスタリングと裾）を**完全保存**し
   系列相関のみ消す。VR(q) の帰無分布としてこれが正しい。2000 本・両側 p。
   判定: (a) 符号ランダム化 p が 0.05 以上 → c65 の「区別不能」は正しく、part C2 の p 0.000 は帰無の誤りで**自壊**。
         (b) 0.05 未満のセルが期待数を超える → c65 の null 主張 (4) が broken。
D2 併記: 定常ブロックブートストラップ（平均ブロック 21 日）＝ボラも系列相関も部分保存（保守側の参照）。
D3 直接の自己相関 ρ(1..5)（セッション日次 r_d）と符号ランダム化の 95% 帯。VR(2)−1 ≈ ρ1 の確認。
D4 US500 在 VR(2) が有意だった場合の代替仮説の切り分け（c65 の最重大反証 第 3「bid 1 社・セッション最終足」）:
   (i) NFMIN 100→200（薄い日を落とす）(ii) 年別 ρ1 (iii) 月〜金の曜日別 (iv) 2020 除外。
   ρ1 ≈ −0.1 が薄い日/特定年に集中していれば**マイクロストラクチャー/定義の人工物**で優位ではない。
seed 20261124。書込は AUREL_RESEARCH/data のみ。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c65_tsmom_d.md")
NY = "America/New_York"
rng = np.random.default_rng(20261124)
NFMIN = 100; LOG = []
def say(s=""): print(s, flush=True); LOG.append(s)
say(f"# [REFUTE c65 part D] VR の帰無を正す（part C2 の p 0.000 を自分で壊す） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c65_tsmom_d.py)")

def vr_lm(r, q):
    r = np.asarray(r, float); n = len(r); mu = r.mean(); d = r - mu
    s2 = (d ** 2).sum() / (n - 1)
    rq = np.convolve(r, np.ones(q), mode="valid"); m = (n - q + 1)
    s2q = ((rq - q * mu) ** 2).sum() / (m - 1)
    vr = s2q / (q * s2)
    theta = 0.0
    for k in range(1, q):
        dk = ((d[k:] ** 2) * (d[:-k] ** 2)).sum() / ((d ** 2).sum() ** 2) * n
        theta += (2 * (q - k) / q) ** 2 * dk
    z = (vr - 1) / math.sqrt(theta / n) if theta > 0 else float("nan")
    return vr, z
def vr_only(r, q):
    r = np.asarray(r, float); n = len(r); mu = r.mean()
    s2 = ((r - mu) ** 2).sum() / (n - 1)
    rq = np.convolve(r, np.ones(q), mode="valid")
    return (((rq - q * mu) ** 2).sum() / (len(rq) - 1)) / (q * s2)
def acf(r, k): return float(np.corrcoef(r[k:], r[:-k])[0, 1])

def daily_table(sym, nfmin=NFMIN):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); rr = np.zeros(len(C)); rr[1:] = np.diff(lc); flat = rr == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
    sord = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
    keep = ~flat
    df = pd.DataFrame({"o": sord[keep], "lc": lc[keep]})
    g = df.groupby("o", sort=True)
    D = pd.DataFrame({"lc_last": g["lc"].last(), "nf": g["lc"].size()})
    D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index])
    D["wd"] = D["date"].dt.weekday
    D = D[(D.wd <= 4) & (D.nf >= nfmin)].reset_index()
    D["r"] = np.r_[np.nan, np.diff(D["lc_last"].to_numpy())] * 1e4
    D["year"] = D["date"].dt.year
    return D

def p_signrand(r, q, nrep=2000, seed=20261124):
    """|r_t| の列（ボラ・クラスタリング／裾）を完全保存し系列相関のみ消す帰無。"""
    g = np.random.default_rng(seed)
    v = vr_only(r, q); n = len(r)
    null = np.array([vr_only(r * g.choice([-1.0, 1.0], size=n), q) for _ in range(nrep)])
    p = 2 * min(float((null <= v).mean()), float((null >= v).mean()))
    return v, min(p, 1.0), float(np.median(null)), float(null.std())

def p_statboot(r, q, nrep=1000, mean_blk=21, seed=20261124):
    """定常ブロックブートストラップ（幾何長・平均 21 日）＝系列相関も部分保存（保守側参照）。"""
    g = np.random.default_rng(seed + 7)
    v = vr_only(r, q); n = len(r); pr = 1.0 / mean_blk; null = np.empty(nrep)
    for i in range(nrep):
        idx = np.empty(n, dtype=np.int64); idx[0] = g.integers(0, n)
        cont = g.random(n) >= pr
        for t in range(1, n):
            idx[t] = (idx[t - 1] + 1) % n if cont[t] else g.integers(0, n)
        null[i] = vr_only(r[idx], q)
    p = 2 * min(float((null <= v).mean()), float((null >= v).mean()))
    return min(p, 1.0), float(np.median(null))

TAB = {s: daily_table(s) for s in ["XAU", "US500"]}
WINS = {"XAU": [("在 2011-20", 2011, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)],
        "US500": [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]}

say("\n## D1 符号ランダム化帰無（|r_t| 完全保存・系列相関のみ消す＝VR の正しい帰無）")
nsig = 0; ncell = 0
for sym in ["XAU", "US500"]:
    D = TAB[sym]; r = D["r"].to_numpy(); yr = D["year"].to_numpy()
    for wn, lo, hi in WINS[sym]:
        rr = r[(yr >= lo) & (yr <= hi) & np.isfinite(r)]
        parts = []
        for q in [2, 5, 10, 21, 63]:
            v, p, med, sd = p_signrand(rr, q)
            _, z = vr_lm(rr, q)
            ncell += 1; nsig += p < 0.05
            parts.append(f"VR({q}) {v:.3f}（符号ランダム p **{p:.3f}**・帰無中央値 {med:.3f}・帰無 sd {sd:.3f}・LM z {z:+.2f}）")
        say(f"- {sym} {wn}（n {len(rr)} 日）: " + "・".join(parts))
say(f"- まとめ: {ncell} セル中 p<0.05 は **{nsig}**（期待 {0.05*ncell:.1f}）")

say("\n## D2 定常ブロックブートストラップ（平均 21 日・保守側参照）— 争点のセルのみ")
D = TAB["US500"]; r = D["r"].to_numpy(); yr = D["year"].to_numpy()
r500in = r[(yr >= 2014) & (yr <= 2020) & np.isfinite(r)]
for q in [2, 5, 10]:
    p, med = p_statboot(r500in, q)
    say(f"- US500 在 VR({q}) {vr_only(r500in,q):.3f}: 定常ブロック p {p:.3f}（帰無中央値 {med:.3f}）")

say("\n## D3 直接の自己相関 ρ(k)（セッション日次）と符号ランダム化 95% 帯")
for sym in ["XAU", "US500"]:
    D = TAB[sym]; r = D["r"].to_numpy(); yr = D["year"].to_numpy()
    for wn, lo, hi in WINS[sym]:
        rr = r[(yr >= lo) & (yr <= hi) & np.isfinite(r)]
        g = np.random.default_rng(20261124)
        null = np.array([[acf(rr * g.choice([-1.0, 1.0], size=len(rr)), k) for k in range(1, 6)] for _ in range(1000)])
        obs = [acf(rr, k) for k in range(1, 6)]
        say(f"- {sym} {wn} (n {len(rr)}): " + "・".join(
            f"ρ{k+1} {obs[k]:+.3f}（帰無 95% [{np.quantile(null[:,k],0.025):+.3f},{np.quantile(null[:,k],0.975):+.3f}]"
            f"{'**外**' if obs[k]<np.quantile(null[:,k],0.025) or obs[k]>np.quantile(null[:,k],0.975) else ''}）"
            for k in range(5)))
say(f"- 確認: VR(2)−1 ≈ ρ1 → US500 在 VR(2) {vr_only(r500in,2):.3f} vs 1+ρ1 {1+acf(r500in,1):.3f}")

say("\n## D4 US500 在 ρ1 の代替仮説（bid 1 社・セッション最終足・薄い日）")
D200 = daily_table("US500", nfmin=200)
r200 = D200["r"].to_numpy(); y200 = D200["year"].to_numpy()
rr200 = r200[(y200 >= 2014) & (y200 <= 2020) & np.isfinite(r200)]
say(f"- NFMIN 100: n {len(r500in)}・ρ1 {acf(r500in,1):+.3f}・VR(2) {vr_only(r500in,2):.3f}")
say(f"- NFMIN 200: n {len(rr200)}・ρ1 {acf(rr200,1):+.3f}・VR(2) {vr_only(rr200,2):.3f}")
D = TAB["US500"]; r = D["r"].to_numpy(); yr = D["year"].to_numpy(); wd = D["wd"].to_numpy()
say("- 年別 ρ1（在）: " + "・".join(f"{y} {acf(r[(yr==y)&np.isfinite(r)],1):+.3f} (n {int(((yr==y)&np.isfinite(r)).sum())})" for y in range(2014, 2021)))
m = (yr >= 2014) & (yr <= 2020) & np.isfinite(r) & (yr != 2020)
say(f"- 2020 除外（在）: n {int(m.sum())}・ρ1 {acf(r[m],1):+.3f}・VR(2) {vr_only(r[m],2):.3f}"
    f"・符号ランダム p {p_signrand(r[m],2)[1]:.3f}")
say("- 曜日別 ρ1（在・r_d を曜日で層別して前日比の相関を見る代理）: " + "・".join(
    f"{['月','火','水','木','金'][d]} {acf(r[(yr>=2014)&(yr<=2020)&np.isfinite(r)&(wd==d)],1):+.3f}" for d in range(5)))
say("- 併記: XAU 在 ρ1 " + f"{acf(TAB['XAU']['r'].to_numpy()[(TAB['XAU']['year'].to_numpy()>=2011)&(TAB['XAU']['year'].to_numpy()<=2020)&np.isfinite(TAB['XAU']['r'].to_numpy())],1):+.3f}"
    " ＝ 金では出ない（US500 固有なら指数の非同時取引/bid 定義が第一候補）")

say(f"\n- 実行 {time.time()-T0:.1f} s・seed 20261124・書込 data/refute_c65_tsmom_d.md のみ・MT5 なし・外部通信なし")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(LOG) + "\n")
print("saved", OUT)
