# -*- coding: utf-8 -*-
"""
[REFUTE] 2026-11-10 反証レーン — 対象: cycle26 (00:55) の事後「弱信号」
  W1 占有: G=50（00+50 水準）±1 USD に居る時間が 21〜25% 少ない（ρ_O 0.768/0.788/0.754・日ブロック z −6.7/−5.7/−6.0・順位 1/10・年別 15/17 年 <1）
  W2 横断: 接近後 12 本で反対側へ抜ける確率 +2.6〜+3.2 pp（z 2.8/3.4/2.5・順位 10/10・年別 16/17 年 >0）＝「磁石（加速通過）」
  W3 継続: 00 水準のみ Δcont(t−1→t+12) 在 +0.29 (z2.9)/外 +1.09 (z2.9)/近年 +1.67 (z2.6)・Δcont2 外 +1.21 (z2.3)＝「紙の上では費用を超える」
  W4 前向き条件（3 条件・≥250 取引日）の検出力

判定規則（数字を見る前に固定）:
  R1 校正（プラセボを標的に）: 各セル（G=50 占有／G=50 横断／G=100 占有／G=100 横断／G=10 占有）で θ_j≠0 を標的・残り 8 本（θ=0 除外）を
     プラセボとして ρ/Δ と日ブロック z を 在・外 で計算。研究レーンの規則「在 |z|≥2.5 ∧ 外 同符号 |z|≥2」を通る標的の本数 / 45。
     → 通過 ≥5/45 なら日ブロック z は校正不良（W1/W2 の z は証拠にならず順位のみ）。≤1/45 なら校正 OK。
     併記: プラセボ分布 z_pl = (f_0 − mean f_θ)/sd f_θ（9 本）。
  R2 細格子（G=50・θ=0..49 step 1・δ=1）: 在・外 の f(θ) 曲線・argmin・f_0 の順位 /50・z_fine（θ∈[5,45] の平均/sd 基準）。
     → W1 survive 条件: 在・外とも 順位 1/50 ∧ argmin∈{49,0,1}。argmin が |2| 以上ずれたら「水準は丸い数ではない／bid オフセット」フラグ。
  R3 分解（G=50 横断・N=12）: (a) |P_{t+12}−P_{t−1}| と RV の θ=0 − プラセボ差（z）＝ボラ成分。
     (b) |移動| 五分位内で層化した Δ_X（日ブロック z）＝方向成分。(c) 観測後 Δ_X_post: 帯入り足 t の側→t+12 の側（取引者が見られる形）。
     (d) 帯入り足で既に抜けた割合（jump-through）の差。
     → W2 の「磁石（方向つき加速）」は 層化 Δ_X が raw の <50% かつ 在・外 |z|<2 なら broken（＝両側ボラ）。層化 Δ_X 在 z≥2 ∧ 外 z≥1.5 なら survive。
  R4 bid 配信アーティファクト（口座 spread_log.jsonl・2026-09-25〜・MT5 ブローカー bid・npz とは別配信・別期間）:
     bid の最近傍 50 水準からの距離 |d| ビン（≤1／1-2／2-5／5-25）別 spread 平均/中央値。≤1 ビンが 5-25 ビンより 20% 以上広ければ配信疑いフラグ。
     併記: 同ログ（5 分 last 再標本）の G=50/100 占有 ρ_O と順位（新データ・別配信・46 日≝検出力低・記述）。
  R5 別分割: 4 独立窓 2010-14／2015-20／2021-23／2024-26H1 ＋ 偶数年／奇数年。G=50 の ρ_O 順位（1=最小）と Δ_X 順位（10=最大）。
     → 4 窓中 ≥3 で順位 1（占有）／10（横断）なら replicate（帰無 p≈0.0037）。≤2 なら不発。
  R6 W3 の分解と費用（G=100 θ=0 vs θ≠0・00 水準・δ_a=1）: cont を 帯入り足（t−1→t）と 観測後（t→t+12, t→t+36）に分解。
     取引可能形 = 帯入り足の終値で接近方向へ建玉・12/36 本後に終値で手仕舞い。費用 c∈{0.16, 0.32, 0.64} USD。
     → W3 broken 条件: 観測後 net（c=0.32・t→t+12）の日クラスタ t<2 in 外、または c=0.64 で負。
  R7 多重検定: R1 のセル別プラセボ通過率から「5 セルのどれかが通る」帰無確率を概算。
  R8 年別符号の帰無: 各プラセボ標的 θ_j の年別 ρ_j<1 本数・Δ_X>0 本数（17 年）。θ=0 の 15/17・16/17 が最大か。
  W4: 在/外の年別 ρ_O の sd（θ=0 と プラセボ標的）から 1 年の se を実測し 3 条件の MDE を並べる。
入力: data/macro/XAU_m5_close.npz・../spread_log.jsonl（読取のみ）。scan 無し・MT5 無し・外部通信無し。seed 20261110。
出力: data/refute_c26_roundnum.md・data/refute_c26_roundnum_run.log。
"""
import os, sys, json, time, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
LIVE = os.path.dirname(ROOT)
OUT = os.path.join(DATA, "refute_c26_roundnum.md")
rng = np.random.default_rng(20261110); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
def utc(x): return dt.datetime.fromtimestamp(int(x), dt.timezone.utc)
say(f"# [REFUTE c26] キリ番 弱信号の反証 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c26_roundnum.py)")

z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
keep = ~np.r_[True, P_ALL[1:] == P_ALL[:-1]]; P = P_ALL[keep]; ts = TS[keep]; day = ts // 86400
year = (np.searchsorted(np.array([dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp() for y in range(2010, 2028)]), ts, side="right") + 2009)
absdP = np.r_[0.0, np.abs(np.diff(P))]; cumAbs = np.cumsum(absdP)
say(f"- 取引足 {len(P)} 本 {utc(ts[0]).date()}〜{utc(ts[-1]).date()}・価格小数: 0.1 刻み比率 {np.mean(np.abs(P*10-np.round(P*10))<1e-6)*100:.1f}%・0.01 刻み比率 {np.mean(np.abs(P*100-np.round(P*100))<1e-6)*100:.1f}%")
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
WIN4 = {"2010-14": (2010, 2014), "2015-20": (2015, 2020), "2021-23": (2021, 2023), "2024-26H1": (2024, 2026)}
def wmask(lo, hi, yv=None): yv = year if yv is None else yv; return (yv >= lo) & (yv <= hi)

# ---------------- 占有の日別カウント ----------------
def occ_counts(G, thetas, delta):
    inb = {}
    for th in thetas:
        r = np.mod(P - th, G); inb[th] = (r <= delta) | (r >= G - delta)
    return inb

def occ_stats(inb, thetas, m, target_idx=0, exclude_zero=False, B=1000):
    d = day[m]; ud, inv = np.unique(d, return_inverse=True); nd = len(ud)
    tot = np.bincount(inv, minlength=nd).astype(float)
    cnt = np.vstack([np.bincount(inv, weights=inb[th][m].astype(float), minlength=nd) for th in thetas])
    f = cnt.sum(1) / tot.sum()
    pool = [i for i in range(len(thetas)) if i != target_idx and not (exclude_zero and i == 0)]
    rho = f[target_idx] / f[pool].mean()
    idx = rng.integers(0, nd, size=(B, nd)); bt = cnt[:, idx].sum(2) / tot[idx].sum(1)
    rb = bt[target_idx] / bt[pool].mean(0); se = rb.std(ddof=1); zz = (rho - 1) / se
    rank = int(1 + (f[pool] < f[target_idx]).sum())
    zpl = (f[target_idx] - f[pool].mean()) / f[pool].std(ddof=1)
    return dict(f=f, rho=rho, z=zz, se=se, rank=rank, zpl=zpl, nd=nd)

# ---------------- 横断イベント ----------------
def events(G, th, delta_a, N, Nmax=36):
    Lnear = np.round((P - th) / G) * G + th; dist = P - Lnear; inb = np.abs(dist) <= delta_a
    cand = np.flatnonzero(inb[1:] & ~inb[:-1]) + 1; cand = cand[(cand >= 1) & (cand + Nmax < len(P))]
    kept = []; last = -10**9
    for c in cand:
        if c - last > N: kept.append(c); last = c
    k = np.array(kept, dtype=np.int64); Lk = Lnear[k]
    before = np.sign(P[k - 1] - Lk); at = np.sign(P[k] - Lk); after = np.sign(P[k + N] - Lk); after36 = np.sign(P[k + 36] - Lk)
    toward = np.sign(Lk - P[k - 1])
    return dict(t=k, L=Lk, day=day[k], year=year[k], level_mod100=np.mod(Lk, 100),
                X=((after == -before) & (before != 0)).astype(float),
                Xpost=((after == -at) & (at != 0)).astype(float), at_known=(at != 0).astype(float),
                jump=((at == -before) & (before != 0)).astype(float),
                absmove=np.abs(P[k + N] - P[k - 1]), rv=cumAbs[k + N] - cumAbs[k - 1],
                cont=(P[k + N] - P[k - 1]) * toward, cont_entry=(P[k] - P[k - 1]) * toward,
                cont_post=(P[k + N] - P[k]) * toward, cont_post36=(P[k + 36] - P[k]) * toward,
                cont2=(P[k + 3 * N] - P[k + N]) * toward)

def day_stat(ev_list, m_list, key, target_idx=0, pool=None, B=1000, kind="mean", denom_key=None):
    """θ 標的 vs プール（イベント平均の差）の日ブロック bootstrap。kind=mean: 差の平均。"""
    K = len(ev_list); pool = [i for i in range(K) if i != target_idx] if pool is None else pool
    ud = np.unique(np.concatenate([e["day"][mm] for e, mm in zip(ev_list, m_list)])); nd = len(ud)
    S = np.zeros((K, nd)); Nn = np.zeros((K, nd))
    for i, (e, mm) in enumerate(zip(ev_list, m_list)):
        inv = np.searchsorted(ud, e["day"][mm]); w = e[key][mm]
        if denom_key is not None:
            dn = e[denom_key][mm]; S[i] = np.bincount(inv, weights=w * dn, minlength=nd); Nn[i] = np.bincount(inv, weights=dn, minlength=nd)
        else:
            S[i] = np.bincount(inv, weights=w, minlength=nd); Nn[i] = np.bincount(inv, minlength=nd)
    d = S[target_idx].sum() / Nn[target_idx].sum() - S[pool].sum() / Nn[pool].sum()
    idx = rng.integers(0, nd, size=(B, nd))
    bd = S[target_idx][idx].sum(1) / Nn[target_idx][idx].sum(1) - S[pool][:, idx].sum((0, 2)) / Nn[pool][:, idx].sum((0, 2))
    se = bd.std(ddof=1)
    means = S.sum(1) / Nn.sum(1)
    return dict(d=d, se=se, z=d / se if se > 0 else np.nan, n0=int(Nn[target_idx].sum()), means=means, nd=nd)

# ================= R1 校正 =================
say("\n## R1 校正: プラセボ θ_j を標的にして研究レーンの規則（在 |z|≥2.5 ∧ 外 同符号 |z|≥2）を適用")
cells = {}
inb50 = occ_counts(50, list(range(0, 50, 5)), 1.0); inb100 = occ_counts(100, list(range(0, 100, 10)), 1.0); inb10 = occ_counts(10, list(range(0, 10, 1)), 0.2)
ev50 = [events(50, th, 1.0, 12) for th in range(0, 50, 5)]; ev100 = [events(100, th, 1.0, 12) for th in range(0, 100, 10)]
r1_pass = {}; r1_in25 = {}
for cname, kind, obj, thetas in (("G50 占有", "occ", inb50, list(range(0, 50, 5))), ("G100 占有", "occ", inb100, list(range(0, 100, 10))),
                                  ("G10 占有", "occ", inb10, list(range(0, 10))), ("G50 横断", "x", ev50, list(range(0, 50, 5))), ("G100 横断", "x", ev100, list(range(0, 100, 10)))):
    rows = []
    for j in range(len(thetas)):
        zs = {}
        for wn in ("在 2010-20", "外 2021-26H1"):
            lo, hi = WIN[wn]
            if kind == "occ":
                st = occ_stats(obj, thetas, wmask(lo, hi), target_idx=j, exclude_zero=(j != 0), B=600); zs[wn] = (st["rho"], st["z"], st["zpl"], st["rank"])
            else:
                ml = [wmask(lo, hi, e["year"]) for e in obj]; pool = [i for i in range(len(thetas)) if i != j and (j == 0 or i != 0)]
                st = day_stat(obj, ml, "X", target_idx=j, pool=pool, B=600)
                zpl = (st["means"][j] - st["means"][pool].mean()) / st["means"][pool].std(ddof=1); rank = int(1 + (st["means"][pool] < st["means"][j]).sum())
                zs[wn] = (st["d"] * 100, st["z"], zpl, rank)
        zi, zo = zs["在 2010-20"][1], zs["外 2021-26H1"][1]
        ok = abs(zi) >= 2.5 and abs(zo) >= 2 and np.sign(zi) == np.sign(zo)
        rows.append((thetas[j], zs, ok))
    npass = sum(1 for r in rows[1:] if r[2]); nin = sum(1 for r in rows[1:] if abs(r[1]["在 2010-20"][1]) >= 2.5)
    r1_pass[cname] = npass; r1_in25[cname] = nin
    say(f"- **{cname}**: θ=0 → 在 {rows[0][1]['在 2010-20'][0]:+.3f} z {rows[0][1]['在 2010-20'][1]:+.2f} (z_pl {rows[0][1]['在 2010-20'][2]:+.2f}・順位 {rows[0][1]['在 2010-20'][3]})／外 {rows[0][1]['外 2021-26H1'][0]:+.3f} z {rows[0][1]['外 2021-26H1'][1]:+.2f} (z_pl {rows[0][1]['外 2021-26H1'][2]:+.2f}・順位 {rows[0][1]['外 2021-26H1'][3]}) → {'PASS' if rows[0][2] else 'fail'}；"
        f"プラセボ標的 9 本中 規則通過 **{npass}**・在 |z|≥2.5 のみ {nin}")
    say("  プラセボ標的 θ: " + " ".join(f"{r[0]}:[在 {r[1]['在 2010-20'][0]:+.2f}/z{r[1]['在 2010-20'][1]:+.1f}, 外 {r[1]['外 2021-26H1'][0]:+.2f}/z{r[1]['外 2021-26H1'][1]:+.1f}]{'★' if r[2] else ''}" for r in rows[1:]))
tot_pass = sum(r1_pass.values()); say(f"- 合計: 45 本のプラセボ標的中 規則通過 **{tot_pass}**（≥5 で校正不良）・在 |z|≥2.5 {sum(r1_in25.values())}/45（帰無 5% 期待 ≈2.3）")
R1_OK = tot_pass <= 1

# ================= R2 細格子 =================
say("\n## R2 細格子 G=50・θ=0..49（δ=1 USD）")
inbF = occ_counts(50, list(range(0, 50)), 1.0); r2 = {}
for wn, (lo, hi) in WIN.items():
    m = wmask(lo, hi); f = np.array([inbF[th][m].mean() for th in range(50)])
    ref = np.r_[f[5:46]]; zf = (f[0] - ref.mean()) / ref.std(ddof=1); rank = int(1 + (f < f[0]).sum() - 0); argmin = int(np.argmin(f))
    r2[wn] = dict(rank=rank, argmin=argmin, zf=zf)
    say(f"- {wn}: f_0 {f[0]*100:.3f}%・θ∈[5,45] 平均 {ref.mean()*100:.3f} sd {ref.std(ddof=1)*100:.3f}・z_fine {zf:+.2f}・f_0 順位 {rank}/50・argmin θ={argmin}（f {f[argmin]*100:.3f}）・近傍 θ=48,49,1,2: {f[48]*100:.3f} {f[49]*100:.3f} {f[1]*100:.3f} {f[2]*100:.3f}")
    say("  f(θ)%: " + " ".join(f"{th}:{v*100:.2f}" for th, v in enumerate(f)))
R2_OK = all(r2[w]["rank"] == 1 and r2[w]["argmin"] in (49, 0, 1) for w in ("在 2010-20", "外 2021-26H1"))

# ================= R3 分解 =================
say("\n## R3 横断の分解（G=50・N=12・θ=0 vs θ≠0）")
r3 = {}
for wn, (lo, hi) in WIN.items():
    ml = [wmask(lo, hi, e["year"]) for e in ev50]
    sX = day_stat(ev50, ml, "X"); sA = day_stat(ev50, ml, "absmove"); sRV = day_stat(ev50, ml, "rv"); sC = day_stat(ev50, ml, "cont")
    sJ = day_stat(ev50, ml, "jump"); sPost = day_stat(ev50, ml, "Xpost", denom_key="at_known"); sCE = day_stat(ev50, ml, "cont_entry"); sCP = day_stat(ev50, ml, "cont_post")
    # 層化 Δ_X（|移動| 五分位・プール基準）
    allA = np.concatenate([e["absmove"][mm] for e, mm in zip(ev50, ml)]); qs = np.quantile(allA, [0, .2, .4, .6, .8, 1.0]); qs[-1] += 1e-9
    ud = np.unique(np.concatenate([e["day"][mm] for e, mm in zip(ev50, ml)])); nd = len(ud)
    SX = np.zeros((10, 5, nd)); SN = np.zeros((10, 5, nd))
    for i, (e, mm) in enumerate(zip(ev50, ml)):
        inv = np.searchsorted(ud, e["day"][mm]); q = np.clip(np.searchsorted(qs, e["absmove"][mm], side="right") - 1, 0, 4)
        for s in range(5):
            sel = q == s; SX[i, s] = np.bincount(inv[sel], weights=e["X"][mm][sel], minlength=nd); SN[i, s] = np.bincount(inv[sel], minlength=nd)
    def strat(SX, SN):
        n0s = SN[0].sum(-1); p0 = SX[0].sum(-1) / np.maximum(n0s, 1); pp = SX[1:].sum((0, -1)) / np.maximum(SN[1:].sum((0, -1)), 1)
        return float(((p0 - pp) * n0s).sum() / n0s.sum()), p0, pp, n0s
    dS, p0s, pps, n0s = strat(SX, SN)
    idx = rng.integers(0, nd, size=(800, nd)); bs = np.array([strat(SX[:, :, ix], SN[:, :, ix])[0] for ix in idx]); seS = bs.std(ddof=1)
    r3[wn] = dict(raw=sX["d"], rawz=sX["z"], strat=dS, stratz=dS / seS, post=sPost["d"], postz=sPost["z"])
    say(f"- {wn}: n0 {sX['n0']}・raw Δ_X {sX['d']*100:+.2f} pp (z {sX['z']:+.2f})／**層化 Δ_X {dS*100:+.2f} pp (z {dS/seS:+.2f})**＝raw の {dS/sX['d']*100:.0f}%"
        f"／Δ|移動| {sA['d']:+.3f} USD (z {sA['z']:+.2f}・プール {sA['means'][1:].mean():.2f})／ΔRV {sRV['d']:+.3f} (z {sRV['z']:+.2f}・プール {sRV['means'][1:].mean():.2f})"
        f"／Δjump(帯入り足で既に反対側) {sJ['d']*100:+.2f} pp (z {sJ['z']:+.2f}・プール {sJ['means'][1:].mean()*100:.1f}%)"
        f"／**観測後 Δ_X_post {sPost['d']*100:+.2f} pp (z {sPost['z']:+.2f})**／Δcont {sC['d']:+.3f} (z {sC['z']:+.2f}) = 帯入り足 {sCE['d']:+.3f} (z {sCE['z']:+.2f}) + 観測後 {sCP['d']:+.3f} (z {sCP['z']:+.2f})")
    say("  五分位別 p_X θ=0 vs プール（%）・n0: " + " ".join(f"Q{s+1}[{qs[s]:.1f}-{qs[s+1]:.1f}]:{p0s[s]*100:.1f}/{pps[s]*100:.1f}(n{int(n0s[s])})" for s in range(5)))
# 00 のみ・50 のみ（θ=0 を水準で分割・プールはそのまま）
def split_events(ev, lv):
    sel = np.isclose(ev["level_mod100"], lv); return {k: (v[sel] if isinstance(v, np.ndarray) else v) for k, v in ev.items()}
for lv, nm in ((0, "00 のみ"), (50, "50 のみ")):
    e0 = split_events(ev50[0], lv); evs = [e0] + ev50[1:]
    for wn, (lo, hi) in WIN.items():
        ml = [wmask(lo, hi, e["year"]) for e in evs]
        sX = day_stat(evs, ml, "X"); sPost = day_stat(evs, ml, "Xpost", denom_key="at_known"); sA = day_stat(evs, ml, "absmove"); sCE = day_stat(evs, ml, "cont_entry"); sCP = day_stat(evs, ml, "cont_post"); sC36 = day_stat(evs, ml, "cont_post36")
        say(f"- {nm} {wn}: n0 {sX['n0']}・raw Δ_X {sX['d']*100:+.2f} (z {sX['z']:+.2f})・観測後 Δ_X_post {sPost['d']*100:+.2f} (z {sPost['z']:+.2f})・Δ|移動| {sA['d']:+.3f} (z {sA['z']:+.2f})"
            f"・Δcont 帯入り足 {sCE['d']:+.3f} (z {sCE['z']:+.2f})・観測後 t→t+12 {sCP['d']:+.3f} (z {sCP['z']:+.2f})・t→t+36 {sC36['d']:+.3f} (z {sC36['z']:+.2f})")

# ================= R4 口座 spread_log =================
say("\n## R4 口座 spread_log.jsonl（MT5 ブローカー bid・別配信・新期間）: キリ番近傍で spread は広がるか／占有は再現するか")
r4_flag = None
try:
    rows = []
    with open(os.path.join(LIVE, "spread_log.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            try:
                o = json.loads(ln); rows.append((int(o["ts"]), float(o["spread_pt"]), float(o["bid"])))
            except Exception: pass
    A = np.array(rows, float); A = A[np.argsort(A[:, 0])]; tsl, spl, bidl = A[:, 0].astype(np.int64), A[:, 1], A[:, 2]
    say(f"- 標本 {len(A)}・{utc(tsl[0])}〜{utc(tsl[-1])} UTC・bid {bidl.min():.0f}〜{bidl.max():.0f}・spread 中央値 {np.median(spl):.3f} p90 {np.percentile(spl,90):.3f}・暦日 {len(np.unique(tsl//86400))}")
    d50 = np.abs(bidl - np.round(bidl / 50) * 50)
    bins = [(0, 1), (1, 2), (2, 5), (5, 25)]; sp = {}
    for a, b_ in bins:
        s = (d50 >= a) & (d50 < b_); sp[(a, b_)] = (s.sum(), spl[s].mean(), np.median(spl[s]), np.mean(spl[s] > 0.3))
    say("- |bid−最近傍 50 水準| ビン別 spread: " + "／".join(f"[{a},{b_}) n{sp[(a,b_)][0]} 平均 {sp[(a,b_)][1]:.4f} 中央値 {sp[(a,b_)][2]:.3f} P(>0.3) {sp[(a,b_)][3]*100:.1f}%" for a, b_ in bins))
    ratio = sp[(0, 1)][1] / sp[(5, 25)][1]; r4_flag = ratio > 1.2 or ratio < 0.8
    say(f"- ≤1 ビン / 5-25 ビン の平均 spread 比 **{ratio:.3f}**（>1.2 で配信疑いフラグ）→ {'フラグ' if r4_flag else 'フラグ無し'}")
    # 00 水準だけ
    d100 = np.abs(bidl - np.round(bidl / 100) * 100); s1 = d100 < 1; s2 = (d100 >= 5) & (d100 < 45)
    say(f"- 100 水準 ±1: n{s1.sum()} 平均 spread {spl[s1].mean():.4f} vs 5-45 {spl[s2].mean():.4f}（比 {spl[s1].mean()/spl[s2].mean():.3f}）")
    # 5 分 last 再標本 → 占有
    b5 = tsl // 300; ub, first = np.unique(b5[::-1], return_index=True); lastidx = len(b5) - 1 - first; P5 = bidl[lastidx]; P5 = P5[np.r_[True, P5[1:] != P5[:-1]]]
    for G, ths, dl in ((50, list(range(0, 50, 5)), 1.0), (100, list(range(0, 100, 10)), 1.0)):
        f = np.array([np.mean(((np.mod(P5 - th, G)) <= dl) | ((np.mod(P5 - th, G)) >= G - dl)) for th in ths])
        say(f"- 占有 G={G}（5 分 last・{len(P5)} 本・新データ 別配信）: f_0 {f[0]*100:.3f}% vs プラセボ {f[1:].mean()*100:.3f}%・ρ_O **{f[0]/f[1:].mean():.3f}**・順位 {1+(f[1:]<f[0]).sum()}/10・θ別 " + " ".join(f"{th}:{v*100:.2f}" for th, v in zip(ths, f)))
    # 横断（5 分 last・N=12）
    Pbak = P
    P_tmp = P5;
    def ev_simple(Pv, G, th, dl, N):
        Ln = np.round((Pv - th) / G) * G + th; inb = np.abs(Pv - Ln) <= dl; cand = np.flatnonzero(inb[1:] & ~inb[:-1]) + 1; cand = cand[cand + N < len(Pv)]
        kept = []; last = -10**9
        for c in cand:
            if c - last > N: kept.append(c); last = c
        k = np.array(kept, int)
        if len(k) == 0: return np.array([]), np.array([])
        Lk = Ln[k]; bf = np.sign(Pv[k-1] - Lk); af = np.sign(Pv[k+N] - Lk); return ((af == -bf) & (bf != 0)).astype(float), (Pv[k+N] - Pv[k-1]) * np.sign(Lk - Pv[k-1])
    xs = [ev_simple(P5, 50, th, 1.0, 12) for th in range(0, 50, 5)]
    x0 = xs[0][0]; xp = np.concatenate([x[0] for x in xs[1:]]); c0 = xs[0][1]; cp = np.concatenate([x[1] for x in xs[1:]])
    if len(x0) > 0:
        say(f"- 横断 G=50 N=12（新データ 別配信）: n0 {len(x0)}・p_X(0) {x0.mean()*100:.1f}% vs プール {xp.mean()*100:.1f}%（Δ {((x0.mean()-xp.mean())*100):+.1f} pp・二項 se ±{np.sqrt(x0.mean()*(1-x0.mean())/len(x0))*100:.1f}）・cont {c0.mean():+.2f} vs {cp.mean():+.2f} USD")
except Exception as ex:
    say(f"- spread_log 読取失敗: {ex!r}")

# ================= R5 別分割 =================
say("\n## R5 別分割（G=50）: 4 独立窓＋偶数/奇数年")
th50 = list(range(0, 50, 5)); r5o = 0; r5x = 0
for wn, (lo, hi) in WIN4.items():
    st = occ_stats(inb50, th50, wmask(lo, hi), B=400); ml = [wmask(lo, hi, e["year"]) for e in ev50]; sx = day_stat(ev50, ml, "X", B=400)
    rx = int(1 + (sx["means"][1:] < sx["means"][0]).sum()); r5o += (st["rank"] == 1); r5x += (rx == 10)
    say(f"- {wn}: 占有 ρ_O {st['rho']:.3f} (z {st['z']:+.2f}・z_pl {st['zpl']:+.2f}) 順位 {st['rank']}/10／横断 Δ_X {sx['d']*100:+.2f} pp (z {sx['z']:+.2f}) 順位 {rx}/10（10=最大）")
for nm, par in (("偶数年", 0), ("奇数年", 1)):
    m = (year % 2) == par; st = occ_stats(inb50, th50, m, B=400); ml = [(e["year"] % 2) == par for e in ev50]; sx = day_stat(ev50, ml, "X", B=400)
    say(f"- {nm}: 占有 ρ_O {st['rho']:.3f} (z {st['z']:+.2f}) 順位 {st['rank']}/10／横断 Δ_X {sx['d']*100:+.2f} pp (z {sx['z']:+.2f}) 順位 {int(1+(sx['means'][1:]<sx['means'][0]).sum())}/10")
say(f"- 4 独立窓で 順位 1（占有）**{r5o}/4**・順位 10（横断）**{r5x}/4**（≥3 で replicate・帰無 p≈0.0037）")
R5_O = r5o >= 3; R5_X = r5x >= 3

# ================= R6 W3 分解と費用 =================
say("\n## R6 W3（00 水準・G=100 θ=0 vs θ≠0）: cont の分解と取引可能形の費用後")
r6 = {}
for wn, (lo, hi) in WIN.items():
    ml = [wmask(lo, hi, e["year"]) for e in ev100]
    sC = day_stat(ev100, ml, "cont"); sCE = day_stat(ev100, ml, "cont_entry"); sCP = day_stat(ev100, ml, "cont_post"); sC36 = day_stat(ev100, ml, "cont_post36")
    e0 = ev100[0]; m0 = ml[0]; dd = e0["day"][m0]
    def dclust(x, dd):
        ud, inv = np.unique(dd, return_inverse=True); s = np.bincount(inv, weights=x); n = np.bincount(inv); mu = x.mean()
        resid = s - mu * n; se = np.sqrt((resid ** 2).sum()) / len(x); return mu, mu / se
    line = f"- {wn}: n0 {sC['n0']}・Δcont(t−1→t+12) {sC['d']:+.3f} (z {sC['z']:+.2f}) = 帯入り足 {sCE['d']:+.3f} (z {sCE['z']:+.2f}) + 観測後 t→t+12 {sCP['d']:+.3f} (z {sCP['z']:+.2f})／観測後 t→t+36 {sC36['d']:+.3f} (z {sC36['z']:+.2f})"
    say(line)
    for key, lab in (("cont_post", "t→t+12"), ("cont_post36", "t→t+36")):
        x = e0[key][m0]; mu, t0 = dclust(x, dd); parts = []
        for c in (0.16, 0.32, 0.64):
            mu_c, t_c = dclust(x - c, dd); parts.append(f"c={c}: {mu_c:+.3f} (t {t_c:+.2f})")
        xp = np.concatenate([e[key][mm] for e, mm in zip(ev100[1:], ml[1:])])
        say(f"  取引可能形 {lab}（帯入り足終値で接近方向へ・終値手仕舞い）: 粗 {mu:+.3f} USD (日クラスタ t {t0:+.2f})・プラセボ同形 {xp.mean():+.3f}／費用後 " + "・".join(parts))
        r6[(wn, key)] = [dclust(x - c, dd) for c in (0.16, 0.32, 0.64)]
W3_broken = (r6[("外 2021-26H1", "cont_post")][1][1] < 2) or any(v[2][0] < 0 for v in r6.values())

# ================= R7 多重検定 =================
say("\n## R7 多重検定（研究レーンの 7 セル×3 窓のうち 5 セル・R1 のプラセボ通過率から）")
rates = {k: (v + 0.5) / 10 for k, v in r1_pass.items()}  # 0 通過でも 0.05 の下限（9 本の分解能）
p_any = 1 - np.prod([1 - r for r in rates.values()])
say(f"- セル別 帰無通過率（(通過+0.5)/10）: " + "・".join(f"{k} {v:.2f}" for k, v in rates.items()) + f" → 5 セルのどれかが通る帰無確率 ≈ **{p_any:.2f}**（分解能 1/9 の粗い推定）")

# ================= R8 年別符号の帰無 =================
say("\n## R8 年別符号の帰無（G=50）: プラセボ標的 θ_j の『17 年中 ρ_j<1 の本数』『Δ_X>0 の本数』")
yrs = list(range(2010, 2027)); cnt_o = []; cnt_x = []
for j in range(10):
    pool = [i for i in range(10) if i != j and (j == 0 or i != 0)]
    co = 0; cx = 0
    for y in yrs:
        m = year == y; f = np.array([inb50[th][m].mean() for th in th50]); co += f[j] < f[pool].mean()
        mx = [e["year"] == y for e in ev50]; p = np.array([e["X"][mm].mean() if mm.sum() else np.nan for e, mm in zip(ev50, mx)]); cx += p[j] > np.nanmean(p[pool])
    cnt_o.append(co); cnt_x.append(cx)
say(f"- ρ<1 の年数: θ=0 **{cnt_o[0]}/17**・プラセボ標的 {cnt_o[1:]}（最大 {max(cnt_o[1:])}）／Δ_X>0 の年数: θ=0 **{cnt_x[0]}/17**・プラセボ標的 {cnt_x[1:]}（最大 {max(cnt_x[1:])}）")
R8_O = cnt_o[0] > max(cnt_o[1:]); R8_X = cnt_x[0] > max(cnt_x[1:])

# ================= W4 前向き条件の MDE =================
say("\n## W4 前向き 3 条件（新データ ≥250 取引日・1 セル）の検出力")
ry = []
for y in yrs:
    m = year == y; f = np.array([inb50[th][m].mean() for th in th50]); ry.append(f[0] / f[1:].mean())
ry = np.array(ry); pl_sd = []
for j in range(1, 10):
    pool = [i for i in range(1, 10) if i != j]; v = []
    for y in yrs:
        m = year == y; f = np.array([inb50[th][m].mean() for th in th50]); v.append(f[j] / f[pool].mean())
    pl_sd.append(np.std(v, ddof=1))
say(f"- 年別 ρ_O（θ=0）sd {ry.std(ddof=1):.3f}（平均 {ry.mean():.3f}）／プラセボ標的の年別 ρ sd 平均 {np.mean(pl_sd):.3f}（＝1 年の se の実測）→ 条件1『ρ_O<1 ∧ z≤−2』は 1 年で効果 ≥{2*np.mean(pl_sd):.2f} が要る（観測 0.23〜0.25）→ {'通る見込み' if 2*np.mean(pl_sd) < 0.22 else '通らない見込み'}")
# 条件3: 00 水準 Δcont(t−1→t+12) z≥1.5 の 1 年 se
e0 = ev100[0]; v = []
for y in yrs:
    m0 = e0["year"] == y; mp = [e["year"] == y for e in ev100[1:]]
    if m0.sum() < 30: continue
    v.append(e0["cont"][m0].mean() - np.concatenate([e["cont"][mm] for e, mm in zip(ev100[1:], mp)]).mean())
v = np.array(v); say(f"- 条件3 00 水準 Δcont(t−1→t+12) 年別: 平均 {v.mean():+.3f} sd {v.std(ddof=1):.3f}（{len(v)} 年）→ 1 年で z≥1.5 には ≥{1.5*v.std(ddof=1):.2f} USD が要る（在 +0.29／外 +1.09）；うち帯入り足の分は取引不能（R6）")

# ================= 判定 =================
say("\n## 判定（docstring の規則どおり）")
say(f"- R1 校正: 45 本中 {tot_pass} 通過 → {'OK（日ブロック z は校正内）' if R1_OK else '校正不良（z は証拠にならない・順位のみ）'}")
say(f"- R2 細格子: 在 順位 {r2['在 2010-20']['rank']}/50 argmin {r2['在 2010-20']['argmin']}／外 順位 {r2['外 2021-26H1']['rank']}/50 argmin {r2['外 2021-26H1']['argmin']} → {'OK' if R2_OK else 'fail'}")
r3i, r3o = r3["在 2010-20"], r3["外 2021-26H1"]
W2_dir_broken = (r3i["strat"] < 0.5 * r3i["raw"] and abs(r3i["stratz"]) < 2) and (r3o["strat"] < 0.5 * r3o["raw"] and abs(r3o["stratz"]) < 2)
W2_dir_surv = r3i["stratz"] >= 2 and r3o["stratz"] >= 1.5
say(f"- R3 方向成分: 層化 Δ_X 在 {r3i['strat']*100:+.2f} (z {r3i['stratz']:+.2f}・raw の {r3i['strat']/r3i['raw']*100:.0f}%)／外 {r3o['strat']*100:+.2f} (z {r3o['stratz']:+.2f}・{r3o['strat']/r3o['raw']*100:.0f}%)；観測後 Δ_X_post 在 {r3i['post']*100:+.2f} (z {r3i['postz']:+.2f})／外 {r3o['post']*100:+.2f} (z {r3o['postz']:+.2f}) → 磁石（方向つき）読み {'broken' if W2_dir_broken else ('survived' if W2_dir_surv else 'inconclusive')}")
say(f"- R4 配信: {'フラグ（spread が水準近傍で違う）' if r4_flag else ('フラグ無し' if r4_flag is not None else '未実施')}")
say(f"- R5 独立 4 窓: 占有 {r5o}/4・横断 {r5x}/4 → 占有 {'replicate' if R5_O else '不発'}／横断 {'replicate' if R5_X else '不発'}")
say(f"- R8 年別: 占有 θ=0 {cnt_o[0]} vs プラセボ最大 {max(cnt_o[1:])} → {'θ=0 が最大' if R8_O else 'プラセボに並ばれる'}／横断 θ=0 {cnt_x[0]} vs {max(cnt_x[1:])} → {'θ=0 が最大' if R8_X else 'プラセボに並ばれる'}")
W1 = "survived" if (R1_OK and R2_OK and R5_O and not r4_flag) else ("broken" if (not R1_OK and (not R2_OK or not R5_O)) else "inconclusive")
W2a = "survived" if (R1_OK and R5_X) else ("broken" if (not R1_OK and not R5_X) else "inconclusive")
say(f"- **W1 占有低下（構造として）: {W1}**／**W2a 横断率上昇（構造として）: {W2a}**／**W2b 磁石＝方向つき加速: {'broken' if W2_dir_broken else ('survived' if W2_dir_surv else 'inconclusive')}**")
say(f"- **W3 00 水準の継続が費用を超える（取引可能形）: {'broken' if W3_broken else 'survived'}**（外 t→t+12 c=0.32 t {r6[('外 2021-26H1','cont_post')][1][1]:+.2f}）")
say(f"\n実行 {time.time()-T0:.1f} s・scan 無し・MT5 無し・外部通信無し・spread_log は読取のみ。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
