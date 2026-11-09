# -*- coding: utf-8 -*-
"""
[REFUTE c26 補足 b・事後] 2026-11-10 — 本体 R6 で唯一残った反証候補
「00 水準（G=100）帯入り足の終値で接近方向へ建玉・36 本後に手仕舞い → 外 2021-26H1 net(c=0.32) +1.65 USD/件 (日クラスタ t 2.48)・c=0.64 でも t 2.0」
を壊しに行く（規則は本体 docstring の後に書いた事後検査＝記述）:
  (1) 接近方向別（下から=買い／上から=売り）・(2) 年別符号・(3) 上位 10% 件の Σ 寄与・中央値・(4) 2026H1 を除く／2021-23／2024-25・
  (5) 地平 N=12/24/36/48/72 の掃引（外）・(6) 00 水準 vs プラセボの接近方向構成・(7) 月ブロック置換（θ ラベル）で外 N=36 の family-wise p（5 地平）。
入力 data/macro/XAU_m5_close.npz のみ。出力 data/refute_c26_roundnum_b.md。
"""
import os, time, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c26_roundnum_b.md"); rng = np.random.default_rng(20261110); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
keep = ~np.r_[True, P_ALL[1:] == P_ALL[:-1]]; P = P_ALL[keep]; ts = TS[keep]; day = ts // 86400
year = (np.searchsorted(np.array([dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp() for y in range(2010, 2028)]), ts, side="right") + 2009)
month = (year * 12 + np.array([dt.datetime.fromtimestamp(int(t), dt.timezone.utc).month for t in ts[::1]]) ) if False else None
say(f"# [REFUTE c26 b] 00 水準 継続（取引可能形）の事後検査 — {time.strftime('%Y-%m-%d %H:%M')}")

def events(G, th, delta_a, N=12, Nmax=72):
    Ln = np.round((P - th) / G) * G + th; inb = np.abs(P - Ln) <= delta_a
    cand = np.flatnonzero(inb[1:] & ~inb[:-1]) + 1; cand = cand[(cand >= 1) & (cand + Nmax < len(P))]
    kept = []; last = -10**9
    for c in cand:
        if c - last > N: kept.append(c); last = c
    k = np.array(kept, dtype=np.int64); Lk = Ln[k]; toward = np.sign(Lk - P[k - 1])
    out = dict(t=k, day=day[k], year=year[k], toward=toward)
    for n in (12, 24, 36, 48, 72): out[f"post{n}"] = (P[k + n] - P[k]) * toward
    return out
def dclust(x, dd):
    ud, inv = np.unique(dd, return_inverse=True); s = np.bincount(inv, weights=x); n = np.bincount(inv); mu = x.mean()
    se = np.sqrt(((s - mu * n) ** 2).sum()) / len(x); return mu, (mu / se if se > 0 else np.nan)
ev = [events(100, th, 1.0) for th in range(0, 100, 10)]; e0 = ev[0]
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026), "外 2021-25（2026 除く）": (2021, 2025), "2021-23": (2021, 2023), "2024-25": (2024, 2025), "2026H1": (2026, 2026)}
C = 0.32
say("\n## (1)(3)(4) 00 水準 N=36・net(c=0.32)・窓別・方向別・尾部")
for wn, (lo, hi) in WIN.items():
    m = (e0["year"] >= lo) & (e0["year"] <= hi); x = e0["post36"][m] - C; dd = e0["day"][m]
    mu, t = dclust(x, dd); srt = np.sort(x)[::-1]; top = srt[: max(1, len(x) // 10)].sum(); tot = x.sum()
    mb = m & (e0["toward"] > 0); ms = m & (e0["toward"] < 0)
    mub, tb = dclust(e0["post36"][mb] - C, e0["day"][mb]); mus, tss = dclust(e0["post36"][ms] - C, e0["day"][ms])
    xp = np.concatenate([e["post36"][(e["year"] >= lo) & (e["year"] <= hi)] for e in ev[1:]]) - C
    say(f"- {wn}: n {m.sum()}・net {mu:+.3f} USD (t {t:+.2f})・中央値 {np.median(x):+.3f}・正の件 {np.mean(x>0)*100:.1f}%・上位 10% の Σ 寄与 {top/tot*100 if tot else float('nan'):+.0f}%"
        f"／下から（買い）n {mb.sum()} {mub:+.3f} (t {tb:+.2f})／上から（売り）n {ms.sum()} {mus:+.3f} (t {tss:+.2f})／プラセボ同形 net {xp.mean():+.3f}")
say("\n## (2) 年別 net(c=0.32) N=36（00 水準・日クラスタ t）＋プラセボ同形")
rows = []
for y in range(2010, 2027):
    m = e0["year"] == y
    if m.sum() < 20: continue
    mu, t = dclust(e0["post36"][m] - C, e0["day"][m]); xp = np.concatenate([e["post36"][e["year"] == y] for e in ev[1:]]) - C
    rows.append(f"{y}:{mu:+.2f}(t{t:+.1f},n{m.sum()})/pl{xp.mean():+.2f}")
say("- " + " ".join(rows));
pos = sum(1 for r in rows if r.split(":")[1].startswith("+")); say(f"- 年別 net>0 {pos}/{len(rows)} 年")
say("\n## (5) 地平掃引（外 2021-26H1・00 水準・粗 Δ vs プラセボ・net c=0.32 の t）")
m = (e0["year"] >= 2021) & (e0["year"] <= 2026)
for n in (12, 24, 36, 48, 72):
    x = e0[f"post{n}"][m]; mu, t = dclust(x - C, e0["day"][m]); xp = np.concatenate([e[f"post{n}"][(e["year"] >= 2021) & (e["year"] <= 2026)] for e in ev[1:]])
    say(f"- N={n}: 粗 {x.mean():+.3f}・プラセボ {xp.mean():+.3f}・Δ {x.mean()-xp.mean():+.3f}・net(c=0.32) {mu:+.3f} (t {t:+.2f})・net(c=0.64) {mu-0.32:+.3f}")
say("\n## (6) 接近方向の構成（外）: 00 水準 vs プラセボ（下から接近の割合）")
fb0 = np.mean(e0["toward"][m] > 0); fbp = np.mean(np.concatenate([e["toward"][(e["year"] >= 2021) & (e["year"] <= 2026)] for e in ev[1:]]) > 0)
say(f"- 下から接近の割合: 00 水準 {fb0*100:.1f}% vs プラセボ {fbp*100:.1f}%")
say("\n## (7) θ ラベル置換（外・月ブロック・2000 回）: 00 水準の N=36 粗平均が 10 本の θ の中で最大か・5 地平 family-wise")
# 月キー
mon = np.array([dt.datetime.fromtimestamp(int(t), dt.timezone.utc).year * 12 + dt.datetime.fromtimestamp(int(t), dt.timezone.utc).month for t in ts[e0["t"][m]]])
allev = []
for i, e in enumerate(ev):
    mm = (e["year"] >= 2021) & (e["year"] <= 2026); tt = e["t"][mm]
    mo = np.array([dt.datetime.fromtimestamp(int(t), dt.timezone.utc).year * 12 + dt.datetime.fromtimestamp(int(t), dt.timezone.utc).month for t in ts[tt]])
    allev.append(dict(theta=i, mo=mo, **{f"post{n}": e[f"post{n}"][mm] for n in (12, 24, 36, 48, 72)}))
# 観測統計: Δ_n = mean(θ=0) − mean(θ≠0) for each N
def stat(labels_per_ev):
    out = {}
    for n in (12, 24, 36, 48, 72):
        a = np.concatenate([e[f"post{n}"] for e in allev]); lab = np.concatenate(labels_per_ev)
        out[n] = a[lab == 0].mean() - a[lab != 0].mean()
    return out
obs = stat([np.full(len(e["mo"]), e["theta"]) for e in allev])
# 置換: 月ブロックごとに θ ラベルを並べ替え（同月の 10 本の θ イベント集合をシャッフルして「どれが 0 か」を入れ替える）
# 実装: 各月で各 θ のイベント数は違うので、月ごとに θ の恒等置換 π_m を引き、イベントのラベル θ → π_m(θ)
mos = np.unique(np.concatenate([e["mo"] for e in allev])); Bp = 2000
mx = {n: [] for n in (12, 24, 36, 48, 72)}; fam = []
for b in range(Bp):
    perms = {mo_: rng.permutation(10) for mo_ in mos}
    labs = [np.array([perms[mo_][e["theta"]] for mo_ in e["mo"]]) for e in allev]
    st = stat(labs)
    for n in st: mx[n].append(st[n])
    fam.append(max(st[n] / np.std(mx[n] or [1]) if False else 0 for n in st))
pv = {}
for n in (12, 24, 36, 48, 72):
    arr = np.array(mx[n]); pv[n] = np.mean(arr >= obs[n]);
say("- 観測 Δ（00 − プラセボ）と置換 p（片側）: " + "・".join(f"N={n}: Δ {obs[n]:+.3f} p {pv[n]:.3f}" for n in pv))
# family-wise: 各置換で 5 地平の標準化 Δ の最大 vs 観測の最大
sd = {n: np.std(mx[n], ddof=1) for n in mx}; Zobs = max(obs[n] / sd[n] for n in mx)
Zperm = np.max(np.vstack([np.array(mx[n]) / sd[n] for n in mx]), axis=0); say(f"- 5 地平 family-wise: 観測 max z {Zobs:.2f}・置換 p_fw **{np.mean(Zperm >= Zobs):.3f}**（N 別 z: " + " ".join(f"{n}:{obs[n]/sd[n]:+.2f}" for n in mx) + "）")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
