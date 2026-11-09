# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-09 反証レーン] 対象: cycle22 (12:55)「米株指数の夜間ドリフト」の残存弱信号
  W1: 「US100 EU 02–04 ET ブロックは 在 2012-20 (t2.76)・外 2021-26H1 (t1.44) とも 11 ブロック中 順位 1・近年 +2.75 (t2.6)
       ＝『形』は残っており null は t 閾値 1 本で決まった」→ 前向き事前固定セル（backlog）に採用された。
  W2: 「配信レジーム 2（2025-09〜2026-06・n214）では ON net +6.43／EU net +3.55 bp/日（swap 0）＝紙の net は正」
  W3（記述）: 在 2014-20 の US100 02 ET セル +2.06 (t3.3) が 23 セル中 唯一の Bonferroni(24) 有意＝文献の 02–03 ET 集中と一致。
  W4（記述・測定）: bid のみ。US100 の spread は 09:30 ET に 3.45→1.45 pt へ段差（R1）＝窓端点の spread が異なる窓（CASH・gap）の
       bid→bid リターンには ±(Δspread/2)/level の機械的偏りが入る。ON−CASH の第 3 条件に影響するか。

判定規則（検証前に書く・結果を見て変えない）
  R1 在の選択は雑音か: 日単位の符号反転（sign-flip・同じ日は US500/US100 の全ブロックで同符号）4000 回で、在 2012-20 の
     22 ブロック（2 指数 × 11）の max t の帰無分布を作り、観測 US100 EU t2.76 の family-wise p を出す。p_fw>0.05 で発火。
     補助: 日内ブロックラベル置換（時刻構造の帰無・日次ドリフトは保存）2000 回の max t でも p_fw を出す。
  R2 外の証拠は雑音か: 外 2021-26H1 で日内ラベル置換 2000 回。P(EU ラベルの t ≥ 1.44 ∧ 順位 1) を出す。>0.05 で発火。
     （順位 1 単独の帰無確率は交換可能性から 1/11=0.091、順位 ≤3 は 0.273＝cycle22 の第 3 条件の緩さを数字で置く）
  R3 別の在/外分割: (2014-17|2018-26H1)・(2014-19|2020-26H1)・(2014-22|2023-26H1)・(偶数年|奇数年) の 4 分割で、外半分が
     EU t≥2 ∧ 順位 ≤3 を満たす数。<2 で発火。補助: 3 年（756 取引日）ローリング窓で t≥2 の割合・順位 1 の割合。
  R4 尾部: 外 EU の上位 5% の日を除いた平均が符号反転したら発火。winsor 1%・中央値・符号検定・DST 夏/冬・前日 VIX 三分位・
     直前夜間(18:05→02:00) 符号・上げ/下げ年 を記述。
  W1 判定: R1∧R2∧R3 発火 → broken／R1〜R3 すべて不発 → survived／他 inconclusive。R4 は旗（記述）。
  R5 W2 の窓は特別か: US100 2014-01〜2026-06 の 214 取引日ローリング窓で EU t≥2.4 の割合。≥0.10 で発火。
  R6 持続: EU t≥2.4 の窓の直後 214 日の EU 平均（非重複に間引き・プール t）。t<2 で発火。
     コスト倍: R2 の spread 0.46 bp を ×1・×2・×4 で net。swap は EU 02–04・ON 18:05–09:30 とも 17:00 ET ロールオーバーを跨がない
     （口座のロール時刻が 17:00 ET なら不課金＝要確認・needs data）。
  W2 判定: R5∧R6 発火 → broken／どちらも不発 → survived／他 inconclusive。
  A5 W3: 在 2012-20 の 46 セル（2 指数 × 23 時間）sign-flip max|t| の帰無で US100 02 ET セル |t|3.3 の p_fw。>0.05 なら
     「唯一の Bonferroni 有意」は 2 指数同時の family では立たない（記述）。
  A6 W4: R1 期間（2022-01〜2025-08）の各日で窓端点足の sp_med から bid 偏り (sp_start − sp_end)/(2·level) を計算し、
     CASH・gap・ON・EU の偏り平均と、偏り補正後の ON−CASH を印字（記述）。
入力: data/macro/US500_m5_close.npz・US100_m5_close.npz・US100_m5_spread.npz・VIXCLS.csv のみ。scan 無し・MT5 無し・外部通信無し。
seed 20261109
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c22_overnight.md"); L = []
NY = "America/New_York"; SEED = 20261109; rng = np.random.default_rng(SEED)
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c22] 夜間ドリフト弱信号 W1(US100 EU 02–04)・W2(2025-09+ net)・W3(02 ET セル)・W4(bid 段差) — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c22_overnight.py)")

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    return ts, cl
def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
def stats(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 20: return dict(n=n, mean=np.nan, se=np.nan, t=np.nan, med=np.nan, pos=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
    return dict(n=n, mean=m, se=se, t=m / se, med=np.median(x), pos=(x > 0).mean())
def f(s): return f"{s['mean']:+.2f} bp (t{s['t']:+.2f}, n{s['n']})" if s["n"] >= 20 else f"n{s['n']} —"

DATES = pd.date_range("2012-01-02", "2026-06-30", freq="D"); DATES = DATES[DATES.weekday <= 4]
YR = DATES.year.to_numpy()
BLK = ["18-20", "20-22", "22-00", "00-02", "02-04", "04-06", "06-08", "08-10", "10-12", "12-14", "14-16"]
def build(sym):
    ts, cl = load(sym); P = lambda h, m, off=0: price_at(ts, cl, epoch_et(DATES, h, m, off)); lg = np.log
    p_pre = P(17, 0, -1); p_re = P(18, 5, -1); p_0930 = P(9, 30); p_1600 = P(16, 0); p_1700 = P(17, 0)
    W = {"gap": (lg(p_re) - lg(p_pre)) * 1e4, "ON": (lg(p_0930) - lg(p_re)) * 1e4, "EU": (lg(P(4, 0)) - lg(P(2, 0))) * 1e4,
         "CASH": (lg(p_1600) - lg(p_0930)) * 1e4, "LATE": (lg(p_1700) - lg(p_1600)) * 1e4, "C2C": (lg(p_1700) - lg(p_pre)) * 1e4,
         "preEU": (lg(P(2, 0)) - lg(p_re)) * 1e4}
    H = {18: (lg(P(19, 0, -1)) - lg(p_re)) * 1e4}
    for h in range(19, 24): H[h] = (lg(P(h + 1 if h < 23 else 0, 0, -1 if h < 23 else 0)) - lg(P(h, 0, -1))) * 1e4
    for h in range(0, 17): H[h] = (lg(P(h + 1, 0)) - lg(P(h, 0))) * 1e4
    B = {"18-20": H[18] + H[19], "20-22": H[20] + H[21], "22-00": H[22] + H[23]}
    for a in range(0, 16, 2): B[f"{a:02d}-{a+2:02d}"] = H[a] + H[a + 1]
    valid = np.isfinite(W["CASH"]) & (W["CASH"] != 0) & np.isfinite(W["ON"])
    return dict(W=W, H=H, B=B, valid=valid, lvl=p_0930)
D = {s: build(s) for s in ("US500", "US100")}
say(f"- 読込 {time.time()-T0:.1f} s・有効日 US500 {D['US500']['valid'].sum()}／US100 {D['US100']['valid'].sum()}")

# ---- reproduction assert (cycle22 numbers) ----
def era(sym, lo, hi): return D[sym]["valid"] & (YR >= lo) & (YR <= hi)
def rank_eu(sym, m):
    means = {k: np.nanmean(D[sym]["B"][k][m]) for k in BLK}; return 1 + sum(1 for k in BLK if means[k] > means["02-04"]), means
I = era("US100", 2012, 2020); O = era("US100", 2021, 2026); N = era("US100", 2024, 2026)
sI, sO, sN = stats(D["US100"]["W"]["EU"][I]), stats(D["US100"]["W"]["EU"][O]), stats(D["US100"]["W"]["EU"][N])
rI, _ = rank_eu("US100", I); rO, _ = rank_eu("US100", O); rN, _ = rank_eu("US100", N)
say(f"- 再現（cycle22 と一致すること）: US100 EU 在 {f(sI)} 順位 {rI}／外 {f(sO)} 順位 {rO}／近年 {f(sN)} 順位 {rN}")
assert abs(sI["mean"] - 2.10) < 0.02 and abs(sO["mean"] - 1.14) < 0.02 and rI == 1 and rO == 1, "cycle22 の再現に失敗"

say("\n## R1 在 2012-20 の選択（US100 EU t2.76）は 2 指数×11 ブロックの family で雑音と区別できるか")
# matrix of blocks for both indices on common valid days (在)
mI = era("US500", 2012, 2020) & era("US100", 2012, 2020)
X = np.column_stack([D[s]["B"][k] for s in ("US500", "US100") for k in BLK])[mI]
ok = np.all(np.isfinite(X), axis=1); X = X[ok]; n = len(X)
mu = X.mean(0); sd = X.std(0, ddof=1); t_obs = mu / (sd / math.sqrt(n))
labels = [f"{s}:{k}" for s in ("US500", "US100") for k in BLK]
say(f"- 在 共通有効日 {n}（全 22 ブロック有限）・観測 t: " + " ".join(f"{l}={t:+.2f}" for l, t in zip(labels, t_obs)))
tEU = t_obs[labels.index("US100:02-04")]
Bperm = 4000; S = rng.choice([-1.0, 1.0], size=(Bperm, n))
sumsq = (X ** 2).sum(0)
mp = (S @ X) / n; varp = (sumsq / n - mp ** 2) * n / (n - 1); tp = mp / np.sqrt(varp / n)
maxt = tp.max(1); p_fw_sf = (maxt >= tEU).mean(); p_single_sf = (tp[:, labels.index("US100:02-04")] >= tEU).mean()
say(f"- sign-flip {Bperm} 回: max t 帰無 中央値 {np.median(maxt):.2f}・95% 点 {np.quantile(maxt, .95):.2f}・**p_fw(US100 EU t{tEU:.2f}) = {p_fw_sf:.3f}**・単セル p {p_single_sf:.4f}")
# US100 only 11 blocks
m11 = [labels.index(f"US100:{k}") for k in BLK]; maxt11 = tp[:, m11].max(1); p_fw11 = (maxt11 >= tEU).mean()
say(f"- US100 の 11 ブロックだけの family: p_fw = {p_fw11:.3f}（95% 点 {np.quantile(maxt11, .95):.2f}）")
# within-day label shuffle (time-of-day null, preserves daily drift) for US100 blocks
def label_shuffle_null(Xb, B=2000):
    nd, nb = Xb.shape; out_t = np.empty((B, nb)); out_rank_eu = np.empty(B, dtype=int)
    eu = BLK.index("02-04"); rows = np.arange(nd)[:, None]
    for b in range(B):
        perm = rng.random((nd, nb)).argsort(1); Xp = Xb[rows, perm]
        m_ = Xp.mean(0); s_ = Xp.std(0, ddof=1) / math.sqrt(nd); out_t[b] = m_ / s_
        out_rank_eu[b] = 1 + (m_ > m_[eu]).sum()
    return out_t, out_rank_eu
XI = np.column_stack([D["US100"]["B"][k] for k in BLK])[era("US100", 2012, 2020)]; XI = XI[np.all(np.isfinite(XI), 1)]
tI_obs = XI.mean(0) / (XI.std(0, ddof=1) / math.sqrt(len(XI)))
tls, rls = label_shuffle_null(XI); p_fw_ls = (tls.max(1) >= tI_obs[BLK.index("02-04")]).mean()
say(f"- 日内ラベル置換 2000 回（在 US100・n{len(XI)}）: EU 観測 t{tI_obs[BLK.index('02-04')]:+.2f}・max t 帰無 95% 点 {np.quantile(tls.max(1), .95):.2f}・**p_fw = {p_fw_ls:.3f}**・P(EU 順位 1) = {(rls==1).mean():.3f}")
R1_fire = p_fw_sf > 0.05
say(f"- **R1 {'発火' if R1_fire else '不発'}**（sign-flip p_fw {p_fw_sf:.3f} {'>' if R1_fire else '≤'} 0.05）")

say("\n## R2 外 2021-26H1 の証拠（US100 EU t1.44・順位 1）は時刻の帰無で何回出るか")
XO = np.column_stack([D["US100"]["B"][k] for k in BLK])[era("US100", 2021, 2026)]; XO = XO[np.all(np.isfinite(XO), 1)]
tO_obs = XO.mean(0) / (XO.std(0, ddof=1) / math.sqrt(len(XO))); eu = BLK.index("02-04")
tlo, rlo = label_shuffle_null(XO)
p_joint = ((tlo[:, eu] >= tO_obs[eu]) & (rlo == 1)).mean(); p_t = (tlo[:, eu] >= tO_obs[eu]).mean(); p_r1 = (rlo == 1).mean(); p_r3 = (rlo <= 3).mean()
say(f"- 外 US100 n{len(XO)}・EU 観測 t{tO_obs[eu]:+.2f} 順位 {1+(tO_obs*0+XO.mean(0) > XO.mean(0)[eu]).sum()}")
say(f"- 日内ラベル置換 2000 回: P(EU t≥{tO_obs[eu]:.2f}) = {p_t:.3f}・P(順位 1) = {p_r1:.3f}（理論 1/11=0.091）・P(順位 ≤3) = {p_r3:.3f}（理論 0.273）・**P(t≥obs ∧ 順位 1) = {p_joint:.3f}**")
# sign-flip single-cell one-sided p for OOS EU
S2 = rng.choice([-1.0, 1.0], size=(Bperm, len(XO))); xo = XO[:, eu]; mp2 = (S2 @ xo) / len(xo); tp2 = mp2 / (np.sqrt((xo**2).sum()/len(xo) - mp2**2) / math.sqrt(len(xo) - 1))
say(f"- 外 EU 単セル sign-flip 片側 p = {(tp2 >= tO_obs[eu]).mean():.3f}")
R2_fire = p_joint > 0.05
say(f"- **R2 {'発火' if R2_fire else '不発'}**（P(t≥obs ∧ 順位 1) {p_joint:.3f} {'>' if R2_fire else '≤'} 0.05）")

say("\n## R3 別の在/外分割（US100 EU）")
splits = [("2014-17|2018-26H1", (2014, 2017), (2018, 2026)), ("2014-19|2020-26H1", (2014, 2019), (2020, 2026)), ("2014-22|2023-26H1", (2014, 2022), (2023, 2026))]
passes = 0
for lab, (a, b), (c, d) in splits:
    mi, mo = era("US100", a, b), era("US100", c, d); si, so = stats(D["US100"]["W"]["EU"][mi]), stats(D["US100"]["W"]["EU"][mo]); ri, _ = rank_eu("US100", mi); ro, _ = rank_eu("US100", mo)
    ok_ = (so["t"] >= 2) and (ro <= 3); passes += ok_
    say(f"- {lab}: 在 {f(si)} 順位 {ri}／外 {f(so)} 順位 {ro} → 外 t≥2∧順位≤3 {'PASS' if ok_ else 'FAIL'}")
me, mo_ = era("US100", 2014, 2026) & (YR % 2 == 0), era("US100", 2014, 2026) & (YR % 2 == 1)
se_, so_ = stats(D["US100"]["W"]["EU"][me]), stats(D["US100"]["W"]["EU"][mo_]); re_, _ = rank_eu("US100", me); ro_, _ = rank_eu("US100", mo_)
ok_ = (so_["t"] >= 2) and (ro_ <= 3); passes += ok_
say(f"- 偶数年|奇数年 (2014+): 偶数 {f(se_)} 順位 {re_}／奇数 {f(so_)} 順位 {ro_} → 奇数 t≥2∧順位≤3 {'PASS' if ok_ else 'FAIL'}")
# rolling 3y
m14 = era("US100", 2014, 2026); idx = np.where(m14)[0]; Xr = np.column_stack([D["US100"]["B"][k] for k in BLK])[idx]; eu_w = D["US100"]["W"]["EU"][idx]
win = 756; cnt = 0; c_t2 = 0; c_r1 = 0; c_neg = 0
for s0 in range(0, len(idx) - win + 1, 21):
    seg = Xr[s0:s0 + win]; segok = np.all(np.isfinite(seg), 1); seg = seg[segok]
    m_ = seg.mean(0); t_ = m_[eu] / (seg[:, eu].std(ddof=1) / math.sqrt(len(seg))); cnt += 1; c_t2 += t_ >= 2; c_r1 += (1 + (m_ > m_[eu]).sum()) == 1; c_neg += m_[eu] < 0
say(f"- 3 年ローリング窓（2014+・21 日刻み・{cnt} 窓）: EU t≥2 の割合 {c_t2/cnt:.2f}・順位 1 の割合 {c_r1/cnt:.2f}・EU<0 の割合 {c_neg/cnt:.2f}")
R3_fire = passes < 2
say(f"- **R3 {'発火' if R3_fire else '不発'}**（4 分割中 PASS {passes}）")

say("\n## R4 尾部・レジーム（外 US100 EU）")
x = D["US100"]["W"]["EU"][O]; x = x[np.isfinite(x)]; xs = np.sort(x); k5 = int(round(0.05 * len(x)))
top_removed = xs[:-k5].mean(); lo_removed = xs[k5:].mean(); wz = np.clip(x, np.quantile(x, .01), np.quantile(x, .99))
say(f"- 外 EU 全体 {f(stats(x))}・中央値 {np.median(x):+.2f}・正の日 {(x>0).mean()*100:.1f}%・winsor1% {wz.mean():+.2f}・上位 5% 除去 {top_removed:+.2f}・下位 5% 除去 {lo_removed:+.2f}・上位 5% の寄与 {xs[-k5:].sum()/x.sum()*100:.0f}%")
R4_fire = top_removed < 0
say(f"- **R4 {'発火（上位 5% 除去で符号反転）' if R4_fire else '不発'}**")
# DST
et02 = pd.to_datetime(epoch_et(DATES, 2, 0), unit="s", utc=True).tz_convert(NY); summer = np.array([ (v.utcoffset().total_seconds() == -4*3600) if pd.notna(v) else False for v in et02])
for lab, mm in (("夏 (EDT)", O & summer), ("冬 (EST)", O & ~summer)):
    say(f"  - DST {lab}: EU {f(stats(D['US100']['W']['EU'][mm]))}")
# prior overnight sign
pre = D["US100"]["W"]["preEU"]
for lab, mm in (("直前夜間 18:05→02:00 >0", O & (pre > 0)), ("直前夜間 ≤0", O & (pre <= 0))):
    say(f"  - {lab}: EU {f(stats(D['US100']['W']['EU'][mm]))}")
# VIX terciles (prior close)
try:
    vx = pd.read_csv(os.path.join(MAC, "VIXCLS.csv")); vx.columns = [c.lower() for c in vx.columns]
    dcol = [c for c in vx.columns if "date" in c][0]; vcol = [c for c in vx.columns if c != dcol][0]
    vx[dcol] = pd.to_datetime(vx[dcol]); vx[vcol] = pd.to_numeric(vx[vcol], errors="coerce"); vx = vx.dropna().set_index(dcol)[vcol].sort_index()
    prior = vx.reindex(DATES - pd.Timedelta(days=1), method="ffill").to_numpy()
    q = np.nanquantile(prior[O], [1/3, 2/3])
    for lab, mm in (("VIX 前日 下位 1/3", O & (prior <= q[0])), ("中位", O & (prior > q[0]) & (prior <= q[1])), ("上位 1/3", O & (prior > q[1]))):
        say(f"  - {lab}: EU {f(stats(D['US100']['W']['EU'][mm]))}")
except Exception as e:
    say(f"  - VIX 読込失敗（記述省略）: {e}")
# up/down years
c2c_y = {y: np.nansum(D["US100"]["W"]["C2C"][D["US100"]["valid"] & (YR == y)]) for y in range(2021, 2027)}
down = [y for y, v in c2c_y.items() if v < 0]
say(f"  - 外 下げ年 {down}: EU {f(stats(D['US100']['W']['EU'][O & np.isin(YR, down)]))}／上げ年: EU {f(stats(D['US100']['W']['EU'][O & ~np.isin(YR, down)]))}")
for y in range(2021, 2027):
    say(f"  - {y}: EU {f(stats(D['US100']['W']['EU'][D['US100']['valid'] & (YR == y)]))}・02 時セル {np.nanmean(D['US100']['H'][2][D['US100']['valid'] & (YR == y)]):+.2f}・03 時セル {np.nanmean(D['US100']['H'][3][D['US100']['valid'] & (YR == y)]):+.2f}")

W1 = "broken" if (R1_fire and R2_fire and R3_fire) else ("survived" if not (R1_fire or R2_fire or R3_fire) else "inconclusive")
say(f"\n### W1 判定: **{W1}**（R1 {'発火' if R1_fire else '不発'}／R2 {'発火' if R2_fire else '不発'}／R3 {'発火' if R3_fire else '不発'}／R4 旗 {'あり' if R4_fire else 'なし'}）")

say("\n## R5/R6 W2: 2025-09〜2026-06（n214）の EU t2.4／ON t1.4 は 214 日窓として特別か・持続するか")
idx14 = np.where(era("US100", 2014, 2026))[0]; eu14 = D["US100"]["W"]["EU"][idx14]; on14 = D["US100"]["W"]["ON"][idx14]
ok14 = np.isfinite(eu14) & np.isfinite(on14); idx14 = idx14[ok14]; eu14 = eu14[ok14]; on14 = on14[ok14]
wl = 214; tE = []; tO_ = []; starts = list(range(0, len(eu14) - wl + 1))
for s0 in starts:
    e = eu14[s0:s0 + wl]; o = on14[s0:s0 + wl]; tE.append(e.mean() / (e.std(ddof=1) / math.sqrt(wl))); tO_.append(o.mean() / (o.std(ddof=1) / math.sqrt(wl)))
tE = np.array(tE); tO_ = np.array(tO_)
frac_e = (tE >= 2.4).mean(); frac_o = (tO_ >= 1.4).mean(); frac_both = ((tE >= 2.4) & (tO_ >= 1.4)).mean()
say(f"- 214 日窓 {len(starts)} 本（2014-01〜2026-06・日刻み）: EU t≥2.4 の割合 **{frac_e:.3f}**・ON t≥1.4 の割合 {frac_o:.3f}・両方 {frac_both:.3f}・EU t の中央値 {np.median(tE):+.2f}・最大 {tE.max():+.2f}")
R5_fire = frac_e >= 0.10
# persistence: non-overlapping selection of windows with tE>=2.4, next 214 days
sel = []; last_end = -1
for s0 in starts:
    if tE[s0] >= 2.4 and s0 > last_end and s0 + 2 * wl <= len(eu14):
        sel.append(s0); last_end = s0 + wl - 1
post = np.array([eu14[s0 + wl:s0 + 2 * wl].mean() for s0 in sel]); pre_ = np.array([eu14[s0:s0 + wl].mean() for s0 in sel])
if len(sel) >= 2:
    pooled = np.concatenate([eu14[s0 + wl:s0 + 2 * wl] for s0 in sel]); sp_ = stats(pooled)
    say(f"- EU t≥2.4 の非重複窓 {len(sel)} 本（開始年 {sorted(set(int(YR[idx14[s0]]) for s0 in sel))}）: 窓内平均 {pre_.mean():+.2f} → 直後 214 日平均 {post.mean():+.2f}（窓別 " + " ".join(f"{v:+.1f}" for v in post) + f"）・プール {f(sp_)}")
    R6_fire = sp_["t"] < 2
else:
    say(f"- EU t≥2.4 の非重複窓は {len(sel)} 本＝持続の検定不能"); R6_fire = True
uncond = stats(eu14); say(f"- 参照: 2014-26H1 無条件 EU {f(uncond)}")
# cost multiples for R2 window
mR2 = D["US100"]["valid"] & ((YR * 100 + DATES.month.to_numpy()) >= 202509) & ((YR * 100 + DATES.month.to_numpy()) <= 202606)
sE2 = stats(D["US100"]["W"]["EU"][mR2]); sO2 = stats(D["US100"]["W"]["ON"][mR2]); sC2 = stats(D["US100"]["W"]["CASH"][mR2])
sp_bp = 0.46
say(f"- R2 窓 n{sE2['n']}: EU {f(sE2)}／ON {f(sO2)}／CASH {f(sC2)}・spread 往復 {sp_bp:.2f} bp → EU net ×1 {sE2['mean']-sp_bp:+.2f}・×2 {sE2['mean']-2*sp_bp:+.2f}・×4 {sE2['mean']-4*sp_bp:+.2f}／ON net ×1 {sO2['mean']-sp_bp:+.2f}・×2 {sO2['mean']-2*sp_bp:+.2f}・×4 {sO2['mean']-4*sp_bp:+.2f} bp/日")
# half split of R2 window
ymv = YR * 100 + DATES.month.to_numpy()
hA = D["US100"]["valid"] & (ymv >= 202509) & (ymv <= 202601); hB = D["US100"]["valid"] & (ymv >= 202602) & (ymv <= 202606)
say(f"- R2 半分割: 2025-09〜2026-01 EU {f(stats(D['US100']['W']['EU'][hA]))}／2026-02〜06 EU {f(stats(D['US100']['W']['EU'][hB]))}；ON {f(stats(D['US100']['W']['ON'][hA]))}／{f(stats(D['US100']['W']['ON'][hB]))}")
say(f"- swap: EU 02–04 ET・ON 18:05→09:30 ET はどちらも 17:00 ET のロールオーバーを跨がない＝口座のロール時刻が 17:00 ET（Dukascopy 21/22:00 GMT 相当）なら swap は 0。MT5 口座は server 00:00 がロール＝要確認（needs data）。")
W2 = "broken" if (R5_fire and R6_fire) else ("survived" if not (R5_fire or R6_fire) else "inconclusive")
say(f"\n### W2 判定: **{W2}**（R5 {'発火' if R5_fire else '不発'}: 割合 {frac_e:.3f}／R6 {'発火' if R6_fire else '不発'}）")

say("\n## A5 W3: 在 2012-20 の US100 02 ET セル |t|3.3 は 2 指数×23 セルの family で立つか")
mI2 = era("US500", 2012, 2020) & era("US100", 2012, 2020); order = [18, 19, 20, 21, 22, 23] + list(range(0, 17))
XH = np.column_stack([D[s]["H"][h] for s in ("US500", "US100") for h in order])[mI2]; okh = np.all(np.isfinite(XH), 1); XH = XH[okh]; nh = len(XH)
th = XH.mean(0) / (XH.std(0, ddof=1) / math.sqrt(nh)); lab_h = [f"{s}:{h:02d}" for s in ("US500", "US100") for h in order]; t02 = th[lab_h.index("US100:02")]
S3 = rng.choice([-1.0, 1.0], size=(Bperm, nh)); mp3 = (S3 @ XH) / nh; var3 = ((XH**2).sum(0) / nh - mp3**2) * nh / (nh - 1); tp3 = mp3 / np.sqrt(var3 / nh)
maxabs = np.abs(tp3).max(1); p_fw_h = (maxabs >= abs(t02)).mean()
m23 = [lab_h.index(f"US100:{h:02d}") for h in order]; p_fw_h23 = (np.abs(tp3[:, m23]).max(1) >= abs(t02)).mean()
say(f"- 共通有効日 {nh}・US100 02 ET 観測 t{t02:+.2f}（在 2012-20）・sign-flip max|t| 帰無 95% 点 46 セル {np.quantile(maxabs, .95):.2f}／23 セル {np.quantile(np.abs(tp3[:, m23]).max(1), .95):.2f}・**p_fw 46 セル {p_fw_h:.3f}／23 セル {p_fw_h23:.3f}**")
# 2014-20 version and OOS cells
m1420 = era("US100", 2014, 2020)
say(f"- US100 02 ET セル 在 2014-20 {f(stats(D['US100']['H'][2][m1420]))}／外 {f(stats(D['US100']['H'][2][O]))}・03 ET 在 {f(stats(D['US100']['H'][3][m1420]))}／外 {f(stats(D['US100']['H'][3][O]))}")

say("\n## A6 W4: bid→bid の窓端点 spread 段差による機械的偏り（R1 期間 2022-01〜2025-08・US100）")
zz = np.load(os.path.join(MAC, "US100_m5_spread.npz")); sts = zz["ts"].astype(np.int64); spm = zz["sp_med"].astype(float)
def sp_at(T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T); key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(sts, key), 0, len(sts) - 1)
    out[ok] = np.where(sts[pos] == key, spm[pos], np.nan); return out
E = lambda h, m, off=0: sp_at(epoch_et(DATES, h, m, off))
sp_pre, sp_re, sp_0930, sp_1600, sp_1700, sp_02, sp_04 = E(17, 0, -1), E(18, 5, -1), E(9, 30), E(16, 0), E(17, 0), E(2, 0), E(4, 0)
lvl = D["US100"]["lvl"]
bias = lambda a, b: (a - b) / (2 * lvl) * 1e4   # bid return = mid return + (sp_start − sp_end)/(2·level)
mR1 = D["US100"]["valid"] & (ymv >= 202201) & (ymv <= 202508)
bC, bG, bO, bE, bL = bias(sp_0930, sp_1600), bias(sp_pre, sp_re), bias(sp_re, sp_0930), bias(sp_02, sp_04), bias(sp_1600, sp_1700)
for lab, b in (("CASH 09:30→16:00", bC), ("gap 17:00→18:05", bG), ("ON 18:05→09:30", bO), ("EU 02→04", bE), ("LATE 16→17", bL)):
    bb = b[mR1]; bb = bb[np.isfinite(bb)]; say(f"- {lab} の bid 偏り: 平均 {bb.mean():+.3f} bp・中央値 {np.median(bb):+.3f}（n{len(bb)}）")
onc = (D["US100"]["W"]["ON"] - D["US100"]["W"]["CASH"])[mR1]; onc_c = ((D["US100"]["W"]["ON"] - bO) - (D["US100"]["W"]["CASH"] - bC))[mR1]
say(f"- R1 期間 ON−CASH: bid のまま {f(stats(onc))} → 偏り補正後 {f(stats(onc_c))}；ON 補正後 {f(stats((D['US100']['W']['ON']-bO)[mR1]))}／CASH 補正後 {f(stats((D['US100']['W']['CASH']-bC)[mR1]))}／gap 補正後 {f(stats((D['US100']['W']['gap']-bG)[mR1]))}")
say(f"- 含意: 在 2014-20 の spread 表は無い。夜/昼の段差が R1 と同程度以上なら、在の CASH は +0.6 bp/日 級に過大・gap は過小で、ON−CASH（在 +2.14）は実態より小さく出ている＝この偏りは W1/W2 には効かず（EU は両端同 spread）、むしろ H_ON の第 3 条件を厳しくする向き。")

say(f"\n実行 {time.time()-T0:.1f} s・seed {SEED}・入力 npz 3 本＋VIXCLS.csv・scan 無し・MT5 無し・外部通信無し")
say(f"\n### 総合: W1 {W1}／W2 {W2}／W3 p_fw(46) {p_fw_h:.3f}／W4 記述")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
