# -*- coding: utf-8 -*-
"""
[cycle26 研究レーン] 2026-11-10 — 【探索・マイクロストラクチャー／行動（収益機会の源泉マップ: 注文の集積・心理的障壁）】
金 XAUUSD の「キリ番」（100 USD の倍数・副 50／10／1000）は価格形成に構造として現れるか。
文献: Aggarwal & Lucey (2007, "Psychological barriers in gold prices", Rev. Fin. Econ.) は日次金価格 1980-2000 で
100 の倍数付近の観測頻度が少ない（障壁）と報告。Osler (2003) は為替の指値/逆指値がキリ番に集積し、
指値集積 → 反転（障壁）／逆指値集積 → 突破後の加速（磁石）の 2 機構を示した。機構は正反対なので方向は事前に決めない（両側）。
我々のデータでできること: (A) 市場の構造そのもの（M5 bid close・2010-26H1・スキャン不要）、(B) 本番 path への接続
（scan 19404 本の建玉価格を npz 全足 path から復元 → TP/SL までの道にキリ番が挟まるかで TP/SL 到達率が変わるか）。
入口フィルタではない（建玉の有無を変えない・出口幾何の記述）。

事前固定（検証前に書く・結果を見てから変えない）:
  データ: data/macro/XAU_m5_close.npz（bid・完全格子・前値埋め）→ flat 足（close==前足）を除いた「取引足」のみ。
        窓: 在 2010-01〜2020-12／外 2021-01〜2026-06／近年 2024-01〜2026-06。日クラスタ = UTC 暦日。
  格子: 主 G=100（θ=0 が 00 レベル・θ=10..90 が 9 本のプラセボ水準）。副 G=50（θ=0,5..45・δ 同じ）・G=10（θ=0..9・δ=0.2）・
        G=1000（θ=0,100..900・δ=5）は記述。
  H_O（占有）: 取引足のうち |P − 最近傍水準(θ)| ≤ δ=1.0 USD の割合 f_θ。統計 ρ_O = f_0 / mean_{θ≠0} f_θ。
        日ブロック bootstrap（2000）で se・95%CI。z_O=(ρ_O−1)/se。判定 PASS_O = 在 |z_O|≥2.5 ∧ 外 同符号 |z_O|≥2。
        文献（障壁）の予測は ρ_O<1（キリ番付近に居る時間が短い）。
  H_X（接近後の横断）: 接近イベント = 足 t で |P_t−L| ≤ δ_a=1.0 ∧ |P_{t−1}−L| > δ_a（L = θ 格子の最近傍水準）、
        直前の採用イベントから >12 本（重複除去）。結果 X = 1 if sign(P_{t+12}−L) = −sign(P_{t−1}−L)（1 時間後に反対側）。
        Δ_X = p_X(θ=0) − p_X(θ≠0 プール)。日ブロック bootstrap で se・z_X。判定 PASS_X = 在 |z_X|≥2.5 ∧ 外 同符号 |z_X|≥2。
        障壁なら Δ_X<0（横断しにくい）・磁石なら Δ_X>0。副: 水準への向きの平均移動 cont = (P_{t+12}−P_{t−1})·sign(L−P_{t−1})（USD・記述）。
  H_T（本番 path・出口幾何）: scan 19404 本。建玉価格 = median_{k=1..3} [P(te+300k) − s·cl_k·risk]（s=+1 BUY/−1 SELL・
        k の不一致 >0.10 USD は除外・hold<1 除外）。TP = entry + s·b·risk／SL = entry − s·risk。
        Z_TP(θ)=1 if 格子(100,θ) の水準が entry と TP の間に挟まる（BUY: floor((TP−θ)/100) > floor((entry−θ)/100)・SELL 対称）。
        Z_SL(θ) 同様。効果 D_TP(θ) = Σ_strata w·[P(exit=TP | Z=1) − P(exit=TP | Z=0)]（strata = 窓内の TP 距離 b·risk の十分位）、
        D_SL(θ) は risk 十分位で SL 到達率。se は strata 内 2 比率の合成。
        判定 PASS_T = 在 D_TP(0) <0 ∧ |z|≥2 ∧ 外 同符号 |z|≥1.5 ∧ θ=0 が 10 オフセット中 最小（在・外とも・帰無 1/10 each）。
        SL 側は Bonferroni(2) の副セル。平均 R*（SL/TP は R+ft・TIME は R−ft・ft=0.1/risk）の Z1−Z0 も記述。
  陽性対照（注入）: H_O = θ=0 の帯内足を 20% 間引いて z_O；H_X = θ=0 の X を 10 pt 下げて z_X；H_T = 外 Z=1 の TP 15% を SL に反転して z。
  MDE = 2·se を全セルに併記。seed 20261110。
  事前の最重大反証: (i) bid のみ・Dukascopy 1 社（キリ番は ask/mid でも同じ位置だが帯 δ=1 USD はスプレッド 0.16〜0.4 と同程度）；
        (ii) 価格水準が 1063→5484 と 5 倍 → 100 USD の相対的な「重み」が時代で変わる（2010 の 8% vs 2026 の 2%）＝G=1000 を併記；
        (iii) H_T の Z=1 本は TP 距離が長い本に偏る → 十分位 strata で統制・プラセボ θ で同じ偏りを持たせて比べる；
        (iv) 占有の帰無（θ 一様）はトレンドがあると厳密には成立しないが、日ブロック bootstrap と 9 本のプラセボで吸収。
  D2: 窓別（在/外/近年）・16 年一括の数字は edge 判定に使わない。昇格候補・入口/出口規則の提案ではない。
入力: data/macro/XAU_m5_close.npz・data/c1_reaccel_paths_2010_2026.json・data/refute_c4_scan_paths_2010_2026.json・
      data/refute_c2_fullpaths.npz。scan 無し・M5 読込なし・MT5 無し・外部通信無し。
出力: data/c26_round_number_barriers_result.md・data/c26_run.log。
"""
import os, sys, json, math, time, datetime as dt, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c26_round_number_barriers_result.md")
rng = np.random.default_rng(20261110); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
def utc(x): return dt.datetime.fromtimestamp(int(x), dt.timezone.utc)
say(f"# [cycle26] 金のキリ番（心理的障壁／注文集積）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c26_round_number_barriers.py)")

# ---------------- データ ----------------
z = np.load(os.path.join(DATA, "macro", "XAU_m5_close.npz")); TS = z["ts"].astype(np.int64); P_ALL = z["close"].astype(float)
say(f"- npz {len(TS)} 本 {utc(TS[0])} 〜 {utc(TS[-1])} UTC・close min {P_ALL.min():.1f} max {P_ALL.max():.1f}（⑩）")
flat = np.r_[True, P_ALL[1:] == P_ALL[:-1]]
keep = ~flat
P = P_ALL[keep]; ts = TS[keep]
yr = np.array([utc(t).year for t in ts[::1000]])  # 粗い年ベクトル（印字用）
year_full = (np.searchsorted(np.array([dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp() for y in range(2010, 2028)]), ts, side="right") + 2009)
day = ts // 86400
wd = ((ts // 86400) + 3) % 7  # 1970-01-01 木曜 → 0=月
say(f"- 取引足（flat 除外）{len(P)} 本（flat {flat.mean()*100:.1f}%・曜日別 flat 比率 " +
    ", ".join(f"{n}:{flat[((TS//86400)+3)%7==i].mean()*100:.0f}%" for i, n in enumerate("月火水木金土日")) + "）（⑪）")
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def wmask(lo, hi): return (year_full >= lo) & (year_full <= hi)

# ---------------- H_O 占有 ----------------
def occupancy(G, thetas, delta, name, inject=None):
    say(f"\n## H_O 占有（G={G}・δ={delta} USD・θ={list(thetas)}）{name}")
    res = {}
    # 各 θ の帯内指標（全期間で一度だけ計算）
    inb = {}
    for th in thetas:
        r = np.mod(P - th, G); inb[th] = (r <= delta) | (r >= G - delta)
    for wn, (lo, hi) in WIN.items():
        m = wmask(lo, hi); d = day[m]; ud, inv = np.unique(d, return_inverse=True); nd = len(ud)
        tot = np.bincount(inv, minlength=nd).astype(float)
        cnt = np.vstack([np.bincount(inv, weights=inb[th][m].astype(float), minlength=nd) for th in thetas])  # [θ, day]
        if inject is not None and wn.startswith("外"):
            cnt_inj = cnt.copy(); cnt_inj[0] *= (1 - inject)
        f = cnt.sum(1) / tot.sum(); f0 = f[0]; fpl = f[1:].mean(); rho = f0 / fpl
        B = 2000; idx = rng.integers(0, nd, size=(B, nd))
        bt = cnt[:, idx].sum(2) / tot[idx].sum(1)  # [θ, B]
        rb = bt[0] / bt[1:].mean(0); se = rb.std(ddof=1); lo_, hi_ = np.percentile(rb, [2.5, 97.5]); zz = (rho - 1) / se
        rank = int(1 + (f[1:] < f0).sum())  # f0 が小さい順の順位（1 = 最小）
        line = (f"- {wn}: 取引足 {m.sum()}・日 {nd}・f_0 {f0*100:.3f}% vs プラセボ平均 {fpl*100:.3f}%（期待 {2*delta/G*100:.2f}%）"
                f"・ρ_O {rho:.4f}（95%CI {lo_:.4f}〜{hi_:.4f}・z {zz:+.2f}・MDE(2se) ±{2*se:.4f}）・f_0 の順位 {rank}/{len(thetas)}（1=最小）")
        if inject is not None and wn.startswith("外"):
            fi = cnt_inj.sum(1) / tot.sum(); rhoi = fi[0] / fi[1:].mean(); bti = cnt_inj[:, idx].sum(2) / tot[idx].sum(1); rbi = bti[0] / bti[1:].mean(0)
            line += f"／陽性対照（帯内 −{inject*100:.0f}%）ρ {rhoi:.4f} z {(rhoi-1)/rbi.std(ddof=1):+.2f}"
        say(line)
        say("  θ 別 f（%）: " + " ".join(f"{th}:{v*100:.3f}" for th, v in zip(thetas, f)))
        res[wn] = dict(rho=rho, z=zz, se=se, rank=rank, f=f)
    return res

O100 = occupancy(100, list(range(0, 100, 10)), 1.0, "（主）", inject=0.20)
O50 = occupancy(50, list(range(0, 50, 5)), 1.0, "（副・記述）")
O10 = occupancy(10, list(range(0, 10, 1)), 0.2, "（副・記述）")
O1000 = occupancy(1000, list(range(0, 1000, 100)), 5.0, "（副・記述）")

# ---------------- H_X 接近後の横断 ----------------
def crossing(G, thetas, delta_a, N, name, inject=None):
    say(f"\n## H_X 接近後 {N} 本の横断（G={G}・δ_a={delta_a} USD）{name}")
    res = {}
    ev_all = []
    for th in thetas:
        Lnear = np.round((P - th) / G) * G + th; dist = P - Lnear; inb = np.abs(dist) <= delta_a
        cand = np.flatnonzero(inb[1:] & ~inb[:-1]) + 1  # 帯に入った足
        cand = cand[(cand >= 1) & (cand + N < len(P))]
        # 重複除去: 直前採用から >N 本
        kept = []; last = -10**9
        for c in cand:
            if c - last > N: kept.append(c); last = c
        kept = np.array(kept, dtype=np.int64)
        Lk = Lnear[kept]; before = np.sign(P[kept - 1] - Lk); after = np.sign(P[kept + N] - Lk)
        X = (after == -before) & (before != 0)
        cont = (P[kept + N] - P[kept - 1]) * np.sign(Lk - P[kept - 1])
        ev_all.append(dict(th=th, t=kept, X=X.astype(float), cont=cont, day=day[kept], year=year_full[kept]))
    for wn, (lo, hi) in WIN.items():
        rows = []
        for e in ev_all:
            m = (e["year"] >= lo) & (e["year"] <= hi); rows.append((e["th"], e["day"][m], e["X"][m], e["cont"][m]))
        ud = np.unique(np.concatenate([r[1] for r in rows])); nd = len(ud)
        cntX = np.zeros((len(thetas), nd)); cntN = np.zeros((len(thetas), nd)); cntC = np.zeros((len(thetas), nd))
        for i, (th, dd, X, C) in enumerate(rows):
            inv = np.searchsorted(ud, dd)
            cntX[i] = np.bincount(inv, weights=X, minlength=nd); cntN[i] = np.bincount(inv, minlength=nd); cntC[i] = np.bincount(inv, weights=C, minlength=nd)
        p = cntX.sum(1) / cntN.sum(1); p0 = p[0]; ppl = cntX[1:].sum() / cntN[1:].sum(); dX = p0 - ppl
        c0 = cntC[0].sum() / cntN[0].sum(); cpl = cntC[1:].sum() / cntN[1:].sum()
        B = 2000; idx = rng.integers(0, nd, size=(B, nd))
        bX = cntX[:, idx].sum(2); bN = cntN[:, idx].sum(2)
        bd = bX[0] / bN[0] - bX[1:].sum(0) / bN[1:].sum(0); se = bd.std(ddof=1); zz = dX / se
        rank = int(1 + (p[1:] < p0).sum())
        line = (f"- {wn}: イベント θ=0 {int(cntN[0].sum())}・プラセボ計 {int(cntN[1:].sum())}・p_X(0) {p0*100:.2f}% vs プール {ppl*100:.2f}%"
                f"・Δ_X {dX*100:+.2f} pp（z {zz:+.2f}・MDE ±{2*se*100:.2f} pp）・p_X(0) の順位 {rank}/{len(thetas)}（1=最小）"
                f"・向きの平均移動 cont θ=0 {c0:+.3f} vs プラセボ {cpl:+.3f} USD")
        if inject is not None and wn.startswith("外"):
            bXi = bX.copy(); bXi[0] = bXi[0] - inject * bN[0]
            dXi = (cntX[0].sum() - inject * cntN[0].sum()) / cntN[0].sum() - ppl
            bdi = bXi[0] / bN[0] - bXi[1:].sum(0) / bN[1:].sum(0); line += f"／陽性対照（X −{inject*100:.0f} pp）Δ {dXi*100:+.2f} z {dXi/bdi.std(ddof=1):+.2f}"
        say(line)
        say("  θ 別 p_X（%）: " + " ".join(f"{th}:{v*100:.2f}" for th, v in zip(thetas, p)))
        res[wn] = dict(dX=dX, z=zz, se=se, rank=rank, p=p)
    return res

X100 = crossing(100, list(range(0, 100, 10)), 1.0, 12, "（主）", inject=0.10)
X50 = crossing(50, list(range(0, 50, 5)), 1.0, 12, "（副・記述）")
X1000 = crossing(1000, list(range(0, 1000, 100)), 5.0, 12, "（副・記述・δ_a=5）")

# ---------------- H_T 本番 path（出口幾何）----------------
say("\n## H_T 本番 path: TP/SL までの道にキリ番が挟まるか × 到達率（scan 19404 本・建玉価格は npz 全足 path から復元）")
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); tr = J["trades"]
C1 = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c1tr = C1["trades"] if isinstance(C1, dict) and "trades" in C1 else C1
say(f"- refute_c4 trades {len(tr)}・c1 trades {len(c1tr)}・c1 keys {sorted(list(c1tr[0].keys()))[:12]}")
F = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = F["clR"]; off = F["off"]
# 順序: c1 を entry_time 昇順に並べた順（DATA_MAP §2 規約）。refute_c4 も同じ本の集合のはず → entry_time 列で突合。
c1_sorted = sorted(range(len(c1tr)), key=lambda i: (c1tr[i]["entry_time"], c1tr[i].get("side", "")))
c1_te = np.array([c1tr[i]["entry_time"] for i in c1_sorted], dtype=np.int64)
tr_sorted = sorted(range(len(tr)), key=lambda i: (tr[i]["entry_time"], tr[i].get("side", "")))
tr_te = np.array([tr[i]["entry_time"] for i in tr_sorted], dtype=np.int64)
assert len(c1_te) == len(tr_te) == len(off) - 1, (len(c1_te), len(tr_te), len(off))
assert np.array_equal(c1_te, tr_te), "c1 と refute_c4 の entry_time 列が一致しない"
dup = len(c1_te) - len(np.unique(c1_te)); say(f"- entry_time 突合 OK（{len(tr_te)} 本・重複 entry_time {dup}）・fullpaths 足数 {len(clR)}")
# 格子 index（ts 一致で参照・⑫）
def grid_price(t):
    i = np.searchsorted(TS, t); ok = (i < len(TS)); ok &= (TS[np.minimum(i, len(TS) - 1)] == t); out = np.full(len(t), np.nan); out[ok] = P_ALL[i[ok]]; return out
rec = []
side = np.array([1.0 if tr[i]["side"] == "BUY" else -1.0 for i in tr_sorted]); risk = np.array([tr[i]["risk"] for i in tr_sorted], float)
b = np.array([tr[i]["b"] for i in tr_sorted], float); hold = np.array([tr[i]["hold"] for i in tr_sorted], int)
exitk = np.array([tr[i]["exit"] for i in tr_sorted]); R = np.array([tr[i]["R"] for i in tr_sorted], float); year = np.array([tr[i]["year"] for i in tr_sorted], int)
ents = np.full((len(tr_te), 3), np.nan)
for k in (1, 2, 3):
    okk = hold >= k
    pk = grid_price(tr_te + 300 * k)
    clk = np.full(len(tr_te), np.nan); clk[okk] = clR[off[:-1][okk] + k]
    ents[:, k - 1] = pk - side * clk * risk
spread_k = np.nanmax(ents, 1) - np.nanmin(ents, 1); nval = np.sum(~np.isnan(ents), 1)
entry = np.nanmedian(ents, 1)
good = (nval >= 1) & (np.nan_to_num(spread_k, nan=0.0) <= 0.10) & ~np.isnan(entry)
say(f"- 建玉価格の復元: k=1..3 の不一致 中央値 {np.nanmedian(spread_k):.3f} USD・p90 {np.nanpercentile(spread_k, 90):.3f}・>0.10 USD {int((np.nan_to_num(spread_k)>0.10).sum())} 本・hold<1 {int((hold<1).sum())} 本 → 採用 {int(good.sum())} 本")
# 妥当性: 復元 entry と格子 close(te) の差（建玉足の終値との関係・記述）
p_te = grid_price(tr_te); say(f"- 記述: entry − close(te) 中央値 {np.nanmedian((entry-p_te)[good]):+.3f} USD・|差| p90 {np.nanpercentile(np.abs(entry-p_te)[good], 90):.2f}・risk 中央値 {np.median(risk[good]):.2f}・TP 距離 b·risk 中央値 {np.median((b*risk)[good]):.2f} USD")
TP = entry + side * b * risk; SL = entry - side * risk
ft = 0.1 / risk; Rstar = np.where(exitk == "TIME", R - ft, R + ft)

def strata_effect(Z, Y, dist, m):
    """窓 m 内で dist の十分位 strata × Z の到達率差（Z1−Z0）の重み付き平均と se。"""
    Zm, Ym, dm = Z[m], Y[m].astype(float), dist[m]
    qs = np.quantile(dm, np.linspace(0, 1, 11)); qs[-1] += 1e-9
    num = 0.0; var = 0.0; wsum = 0.0; n1 = 0
    for i in range(10):
        s = (dm >= qs[i]) & (dm < qs[i + 1]); z1 = s & (Zm == 1); z0 = s & (Zm == 0)
        a, c = z1.sum(), z0.sum()
        if a < 5 or c < 5: continue
        p1, p0 = Ym[z1].mean(), Ym[z0].mean(); w = a  # Z=1 の本数で重み（ATT 型）
        num += w * (p1 - p0); var += (w ** 2) * (p1 * (1 - p1) / a + p0 * (1 - p0) / c); wsum += w; n1 += a
    if wsum == 0: return np.nan, np.nan, 0
    return num / wsum, math.sqrt(var) / wsum, n1

def strata_effect_mean(Z, Y, dist, m):
    Zm, Ym, dm = Z[m], Y[m], dist[m]
    qs = np.quantile(dm, np.linspace(0, 1, 11)); qs[-1] += 1e-9
    num = 0.0; var = 0.0; wsum = 0.0
    for i in range(10):
        s = (dm >= qs[i]) & (dm < qs[i + 1]); z1 = s & (Zm == 1); z0 = s & (Zm == 0); a, c = z1.sum(), z0.sum()
        if a < 5 or c < 5: continue
        w = a; num += w * (Ym[z1].mean() - Ym[z0].mean()); var += (w ** 2) * (Ym[z1].var(ddof=1) / a + Ym[z0].var(ddof=1) / c); wsum += w
    return (num / wsum, math.sqrt(var) / wsum) if wsum else (np.nan, np.nan)

def z_between(a_price, b_price, th, G=100.0):
    lo = np.minimum(a_price, b_price); hi = np.maximum(a_price, b_price)
    return (np.floor((hi - th) / G) > np.floor((lo - th) / G)).astype(int)  # lo < L ≤ hi となる水準あり

thetas = list(range(0, 100, 10)); HT = {}
for wn, (lo, hi) in WIN.items():
    m = good & (year >= lo) & (year <= hi)
    say(f"\n### {wn}: 採用 {m.sum()} 本（TP {int((exitk[m]=='TP').sum())}／SL {int((exitk[m]=='SL').sum())}／TIME {int((exitk[m]=='TIME').sum())}）")
    outT = []; outS = []
    for th in thetas:
        ZT = z_between(entry, TP, th); ZS = z_between(entry, SL, th)
        dT, seT, n1T = strata_effect(ZT, exitk == "TP", b * risk, m); dS, seS, n1S = strata_effect(ZS, exitk == "SL", risk, m)
        mT, seMT = strata_effect_mean(ZT, Rstar, b * risk, m)
        outT.append((th, dT, seT, n1T, mT, seMT)); outS.append((th, dS, seS, n1S))
    dT0 = outT[0]; rankT = 1 + sum(1 for o in outT[1:] if o[1] < dT0[1]); dS0 = outS[0]; rankS = 1 + sum(1 for o in outS[1:] if o[1] < dS0[1])
    say(f"- **TP 側 θ=0**: Z=1 {dT0[3]} 本（{dT0[3]/m.sum()*100:.1f}%）・D_TP {dT0[1]*100:+.2f} pp（se {dT0[2]*100:.2f}・z {dT0[1]/dT0[2]:+.2f}・MDE ±{2*dT0[2]*100:.2f} pp）・順位 {rankT}/10（1=最小）"
        f"・平均 R*（Z1−Z0）{dT0[4]:+.3f}R (t {dT0[4]/dT0[5]:+.2f})")
    say("  θ 別 D_TP（pp）: " + " ".join(f"{o[0]}:{o[1]*100:+.1f}" for o in outT) + f"／プラセボ平均 {np.mean([o[1] for o in outT[1:]])*100:+.2f}・sd {np.std([o[1] for o in outT[1:]], ddof=1)*100:.2f}")
    say(f"- **SL 側 θ=0**: Z=1 {dS0[3]} 本・D_SL {dS0[1]*100:+.2f} pp（se {dS0[2]*100:.2f}・z {dS0[1]/dS0[2]:+.2f}・MDE ±{2*dS0[2]*100:.2f} pp）・順位 {rankS}/10（1=最小）")
    say("  θ 別 D_SL（pp）: " + " ".join(f"{o[0]}:{o[1]*100:+.1f}" for o in outS) + f"／プラセボ平均 {np.mean([o[1] for o in outS[1:]])*100:+.2f}・sd {np.std([o[1] for o in outS[1:]], ddof=1)*100:.2f}")
    # 記述: 側別（BUY で上の 00 を越えて TP／SELL で下の 00 を越えて TP）
    for sd_, nm in ((1.0, "BUY"), (-1.0, "SELL")):
        mm = m & (side == sd_); ZT = z_between(entry, TP, 0); dT, seT, n1T = strata_effect(ZT, exitk == "TP", b * risk, mm)
        say(f"  側別 {nm}: Z=1 {n1T}・D_TP {dT*100:+.2f} pp (z {dT/seT:+.2f})" if n1T else f"  側別 {nm}: n 不足")
    HT[wn] = dict(dT=dT0[1], seT=dT0[2], rankT=rankT, dS=dS0[1], seS=dS0[2], rankS=rankS, mT=dT0[4])
    if wn.startswith("外"):
        # 陽性対照: Z=1 の TP の 15% を SL に反転
        ZT = z_between(entry, TP, 0); Y = (exitk == "TP").copy(); flip_idx = np.flatnonzero(m & (ZT == 1) & Y)
        fl = rng.choice(flip_idx, size=int(0.15 * len(flip_idx)), replace=False); Y2 = Y.copy(); Y2[fl] = False
        dTi, seTi, _ = strata_effect(ZT, Y2, b * risk, m); say(f"  陽性対照（外 Z=1 の TP 15% を反転）: D_TP {dTi*100:+.2f} pp・z {dTi/seTi:+.2f}")

# ---------------- 判定 ----------------
say("\n## 判定（事前固定）")
oi, oo = O100["在 2010-20"], O100["外 2021-26H1"]
passO = abs(oi["z"]) >= 2.5 and abs(oo["z"]) >= 2 and np.sign(oi["z"]) == np.sign(oo["z"])
say(f"- H_O（G=100）: 在 ρ_O {oi['rho']:.4f} z {oi['z']:+.2f}／外 ρ_O {oo['rho']:.4f} z {oo['z']:+.2f} → **{'PASS' if passO else 'null'}**")
xi, xo = X100["在 2010-20"], X100["外 2021-26H1"]
passX = abs(xi["z"]) >= 2.5 and abs(xo["z"]) >= 2 and np.sign(xi["z"]) == np.sign(xo["z"])
say(f"- H_X（G=100・N=12）: 在 Δ_X {xi['dX']*100:+.2f} pp z {xi['z']:+.2f}／外 {xo['dX']*100:+.2f} pp z {xo['z']:+.2f} → **{'PASS' if passX else 'null'}**")
ti, to = HT["在 2010-20"], HT["外 2021-26H1"]
passT = (ti["dT"] < 0 and abs(ti["dT"] / ti["seT"]) >= 2 and np.sign(to["dT"]) == np.sign(ti["dT"]) and abs(to["dT"] / to["seT"]) >= 1.5 and ti["rankT"] == 1 and to["rankT"] == 1)
say(f"- H_T（TP 側）: 在 D_TP {ti['dT']*100:+.2f} pp z {ti['dT']/ti['seT']:+.2f} 順位 {ti['rankT']}／外 {to['dT']*100:+.2f} pp z {to['dT']/to['seT']:+.2f} 順位 {to['rankT']} → **{'PASS' if passT else 'null'}**")
say(f"- H_T（SL 側・副）: 在 D_SL {ti['dS']*100:+.2f} pp z {ti['dS']/ti['seS']:+.2f} 順位 {ti['rankS']}／外 {to['dS']*100:+.2f} pp z {to['dS']/to['seS']:+.2f} 順位 {to['rankS']}")
say(f"\n実行 {time.time()-T0:.1f} s・scan 無し・M5 読込なし・MT5 無し・外部通信無し。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
