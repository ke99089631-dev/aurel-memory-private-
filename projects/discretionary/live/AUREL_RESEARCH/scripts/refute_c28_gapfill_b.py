# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-10 補足 b・事後・記述] refute_c28 R2b で出た「DAILY 外・アンカー 18:10・N=276 の Δ_r = mean(r_N|上) − mean(r_N|下) = −19.4 bp (t −2.41)
・近年 −37.6 (t −2.77)」（符号版 Δ_dir は −4.1 pp t −1.1）が尾部駆動か・年依存か・|G| に比例するか・地平のどこで出るかを見る。
事後なので判定はしない。記述のみ。入力 XAU_m5_ohlc.npz。scan 無し・MT5 無し・外部通信無し。
"""
import os, time, math, io
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
MAC = os.path.join(ROOT, "data", "macro"); OUT = os.path.join(ROOT, "data", "refute_c28_gapfill_b.md")
T0 = time.time(); buf = io.StringIO()
def say(s=""):
    print(s, flush=True); buf.write(s + "\n")
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64); cl = z["close"]; lc = np.log(cl)
r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = r == 0
t_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert("America/New_York")
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)
NMAX = 288
def build(anchor0, ref0, shift):
    a = anchor0; ref = ref0
    e = a + NMAX; ok = (ref >= 0) & (a > 0) & (e < len(ts)) & (ts[np.clip(e, 0, len(ts) - 1)] == ts[a] + 300 * NMAX)
    brk = np.column_stack([idx_at(ts[a] - 300 * j) for j in range(1, 13)]); ok &= np.all(brk >= 0, axis=1)
    clean = np.zeros(len(a), bool); clean[ok] = np.all(flat[brk[ok]], axis=1)
    k = ok & clean; a = a[k] + shift; ref = ref[k]
    G = (lc[a] - lc[ref]) * 1e4; big = np.abs(G) >= 2.0
    return a[big], G[big]
iD = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]; refD = idx_at(ts[iD] - 70 * 60)
a, G = build(iD, refD, 2); y = yr[a]; s = np.sign(G); ag = np.abs(G)
W = {"在 2013-20": (2013, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026), "外-ex2026": (2021, 2025)}
def welch(x, v):
    d = x.mean() - v.mean(); se = math.sqrt(x.var(ddof=1) / len(x) + v.var(ddof=1) / len(v)); return d, se, d / se
def rN(N): return (lc[a + N] - lc[a]) * 1e4
say(f"# refute_c28_b Δ_r（上ギャップ後 − 下ギャップ後の r_N）の中身・DAILY アンカー 18:10・事後記述 — {pd.Timestamp.now():%Y-%m-%d %H:%M}")
say(f"- n {len(a)}・上 {int((s>0).sum())}／下 {int((s<0).sum())}・|G| 中央値 {np.median(ag):.1f} bp")
say("\n## 地平掃引（Δ_r bp・Welch t・トリム 5% 両側・中央値差・Δ_dir pp）")
for N in [12, 36, 72, 144, 216, 276]:
    rr = rN(N); parts = []
    for wn, (y0, y1) in W.items():
        m = (y >= y0) & (y <= y1); up = m & (s > 0); dn = m & (s < 0)
        d, se, t = welch(rr[up], rr[dn])
        def trim(x, q=0.05):
            lo, hi = np.percentile(x, [q * 100, 100 - q * 100]); return x[(x >= lo) & (x <= hi)]
        dt, _, tt = welch(trim(rr[up]), trim(rr[dn])); dmed = np.median(rr[up]) - np.median(rr[dn])
        dd, _, td = welch((rr[up] > 0).astype(float), (rr[dn] > 0).astype(float))
        parts.append(f"{wn.split()[0]} Δ_r {d:+.1f} (t {t:+.2f})・trim {dt:+.1f} (t {tt:+.2f})・med {dmed:+.1f}・Δ_dir {dd*100:+.1f}pp (t {td:+.2f})")
    say(f"- N={N}: " + "／".join(parts))
say("\n## N=276・外 2021-26H1 の年別 Δ_r と LOYO")
rr = rN(276); m = (y >= 2021)
ys = []
for yy in range(2013, 2027):
    mm = y == yy; up = mm & (s > 0); dn = mm & (s < 0)
    if up.sum() >= 5 and dn.sum() >= 5:
        d, se, t = welch(rr[up], rr[dn]); ys.append(f"{yy}: {d:+.1f} (t {t:+.2f}, {int(up.sum())}/{int(dn.sum())})")
say("- 年別: " + "／".join(ys))
lo = []
for yy in range(2021, 2027):
    mm = m & (y != yy); up = mm & (s > 0); dn = mm & (s < 0); d, se, t = welch(rr[up], rr[dn]); lo.append(f"−{yy}: {d:+.1f} (t {t:+.2f})")
say("- LOYO 外: " + "／".join(lo))
say("\n## N=276・外: |G| 比例か（三分位別 Δ_r）・上位/下位 5% 件の寄与・大きいギャップ日の中身")
up = m & (s > 0); dn = m & (s < 0)
q = np.percentile(ag[m], [33.3, 66.7])
for nm, sel in [("小|G|", ag < q[0]), ("中", (ag >= q[0]) & (ag < q[1])), ("大", ag >= q[1])]:
    d, se, t = welch(rr[up & sel], rr[dn & sel]); say(f"- {nm}（|G| 平均 {ag[m&sel].mean():.1f} bp）: Δ_r {d:+.1f} (t {t:+.2f}, n {int((up&sel).sum())}/{int((dn&sel).sum())})・比 Δ_r/(2·|G|) {d/(2*ag[m&sel].mean()):+.2f}")
# tail contribution
x = rr[up]; v = rr[dn]
def tail_share(x, v):
    d_full = x.mean() - v.mean()
    xs = np.sort(x); vs = np.sort(v); k = max(1, len(x) // 20); kv = max(1, len(v) // 20)
    d_cut = xs[k:-k].mean() - vs[kv:-kv].mean(); return d_full, d_cut
df, dc = tail_share(x, v); say(f"- 両側 5% を落とした Δ_r {dc:+.1f} vs 全 {df:+.1f}")
# 2026H1 and large moves: list top 5 |r_N| days among up-gaps in 外
idx = np.where(up)[0]; top = idx[np.argsort(-np.abs(rr[idx]))[:6]]
say("- 外・上ギャップ日で |r_276| 最大 6 件: " + "／".join(f"{t_ny[a[i]]:%Y-%m-%d} G {G[i]:+.1f} r {rr[i]:+.0f}" for i in top))
idx = np.where(dn)[0]; top = idx[np.argsort(-np.abs(rr[idx]))[:6]]
say("- 外・下ギャップ日で |r_276| 最大 6 件: " + "／".join(f"{t_ny[a[i]]:%Y-%m-%d} G {G[i]:+.1f} r {rr[i]:+.0f}" for i in top))
# unconditional mean r_276 by group and sd, to express as fraction of day vol
say(f"- 外 r_276 平均: 上 {rr[up].mean():+.1f} (sd {rr[up].std(ddof=1):.0f}, n {int(up.sum())})／下 {rr[dn].mean():+.1f} (sd {rr[dn].std(ddof=1):.0f}, n {int(dn.sum())})")
say(f"\n- 実行時間 {time.time()-T0:.1f} s")
with open(OUT, "w", encoding="utf-8") as f: f.write(buf.getvalue())
print("->", OUT)
