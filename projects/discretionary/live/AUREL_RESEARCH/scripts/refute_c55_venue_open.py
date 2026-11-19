# -*- coding: utf-8 -*-
"""
[REFUTE c55] 2026-11-20 — 反証レーン（補遺C: 文章でなくコードで壊す）。seed 20261120。

標的（c55 / findings 2026-11-20 01:05）:
  T1 (§7 の正形主張・本サイクル唯一の positive):
      「c45 の UJ 937 本の 18.7%(在)/20.4%(外) が 4 会場の開場窓（足占有 4.10%）に落ちる
        ＝濃縮 4.6×/5.0×（z +19.0/+13.6）・会場別 COMEX 08:20 ET 92・NYSE 70・SGE 8・London 10」
      および派生の読み「UJ は『米国朝の vol 段差＋08:30/10:00 の第2波』でほぼ尽きる」。
  T2 (§1 の主判定 null):
      「H_OPEN 4 会場とも null。開場足は生 |r| で 1.4〜1.9× の段差だが季節標準化した裾は
        近傍と同じか軽い（COMEX 外 ρ0.56・NYSE 0.82/0.77）＝開場の高ボラは拡散的」

事前固定（結果を見る前に凍結・本 docstring が正本）:

 A0 複製: c45 の declustered 5σ 事象集合（2166・SJ 786・UJ 937）と c55 §7 の 12 セル・§1 の主 ρ4 本を再現。
          不一致なら以降の判定を出さず「複製失敗」で終える。
 A1 【分母の整合（T1）】c55 の足占有率 4.10% は base_ok（非 flat ∧ ET17:00-18:10 除外 ∧ UTC 平日）の全 288 スロット
    上で計算されている。しかし UJ の母集団は c45 の定義で
      cand = 非 flat ∧ 直前 3 本も非 flat(nf3) ∧ ET 平日 ∧ ~ET17:00-18:10 ∧ σ_trail 有限
      ∧ 非 EVDAY(NFP/FOMC/CPI 日) ∧ **ET 分 ∈ {05,10,20,25,35,40,50,55}（分 %15≠0）**
    の 3 重に狭い集合。開場窓 11 足のうち 3 足（SGE 01:00 UTC・London 08:00・NYSE 09:30）は分 %15=0 で
    構造的に UJ になれない一方、分母にはそれらを含む全スロットが入っている。
    → UJ 母集団上で測り直した占有率 occ* と濃縮 share/occ* を出す。
    BREAK = occ* が 4.10% から相対 20% 以上ずれる、または補正後の濃縮が 3.0× を下回る。
 A2 【会場分解（T1）】会場ごとに occ* 整合の濃縮と Poisson 95%CI。
    BREAK（「4 会場」という括り方の）= 4 会場のうち 2 つ以上の 95%CI が 1.0 を含む。
 A3 【位置プラセボ（T1・§7 には存在しない）】各会場の窓を近傍 ±12 足に滑らせ、UJ/eligible 率で真の位置を順位づけ。
    BREAK = W 事象の 25% 以上を出している会場の順位が 3 位より下。
 A4 【季節 vol 段差で説明できるか（T1）】UJ eligible な 192 スロット全体で、スロットの検出器段差
    x_s = median(|r|/σ_trail) に対する UJ 率 y_s を回帰（log-log・重み N）。開場 8 スロットの
    観測/予測比の 95%CI が 1.0 を含めば「開場という標識は vol 段差を超える情報を持たない」。
 A5 【decluster 感度（T1）】decluster 無し / 1h / 4h(本番) の 3 通りで UJ 集合を作り直し濃縮を再計算。
    BREAK = 濃縮が本番値から相対 25% 以上動く。
 A6 【年・曜日の安定性（T1）】08:20 ET の UJ 件数の年別推移と pre/post 2016（COMEX 立会廃止）、
    および 08:20 ET UJ の曜日分布（木曜偏重 = 08:30 新規失業保険申請の「発表前」仮説）。
    参考: 08:20 は 08:30 公表の 10 分前であり「開場」と「公表前」は同一足では分離できない。
 A7 【null への攻撃（T2）】c55 の対照 C = [−60,−5]∪[+15,+70] は vol 段差をまたぐため、
    裾率がスロット vol と系統的に関係するなら W（最高 vol）対 C（段差の両側）は like-for-like でない。
    (i) 288 スロットで裾率 J4/N を log(median|r|) に回帰し勾配の有無と符号を出す。
    (ii) 対照を **vol 整合**（同じ時計で |log(v_s)−log(v̄_W)| ≤ log 1.075・W と公表足と W±2 足を除く）に
         置き換えて ρ_matched を再計算。
    H_OPEN 再開 = ある会場で 在 ρ_matched ≥ 1.3 ∧ z ≥ 2.0 ∧ p ≤ 0.0125（Bonferroni 4）∧ 外 ρ_matched > 1。
 A8 多重検定: 本走で判定に使うセルは A1(2)・A2(4)・A3(4)・A5(2)・A7(4) = 16 → Holm。記述セルは判定外。

判定規則（事前）:
  T1 broken        = A1 または A5 が BREAK。
  T1 partial       = 合成の算術は残るが A2 または A3 が BREAK（= 「4 会場の開場」という括りが壊れる）。
  T1 survived      = A1/A2/A3/A5 いずれも BREAK せず。
  T2 broken(再開)  = A7 の再開条件成立。そうでなければ T2 survived（null は vol 勾配の人工物ではない）。

読むのは data/macro/XAU_m5_close.npz・FOMC_dates.csv・CPI_dates.csv・data/c45_jumps_5sigma_declustered.csv のみ。
scan 無し・MT5 無し・外部通信無し・発注なし。書込は AUREL_RESEARCH/ 配下のみ。
"""
import os, sys, time, math
import numpy as np, pandas as pd
from scipy.stats import norm

T0 = time.time(); SEED = 20261120
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c55_venue_open.md")
NY = "America/New_York"
L = []
def say(s=""):
    print(s, flush=True); L.append(s)

def S(h, m): return h * 12 + m // 5

say(f"# [REFUTE c55] 会場開場ジャンプ — 反証 {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c55_venue_open.py・事前固定=docstring・seed {SEED})")

# ================= 暦（c45 と同一） =================
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC_ALL = pd.DatetimeIndex(F.date)
NFP = nfp_dates_v2()
CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

# ================= npz（c45 と同一の前処理） =================
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize())
year = tt.year.to_numpy()
r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
nf = np.isfinite(r) & (r != 0)

W_SIG = 5520; DECL = 14400.0; ZMAIN = 5.0
r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = (lo >= 0)
S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
nf3 = nf.copy()
for k in (1, 2, 3): nf3 &= np.r_[[False] * k, nf[:-k]]
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
cand = nf3 & trading & np.isfinite(sig)
zabs = np.abs(r) / sig
isevbar = np.asarray(etdate.isin(evdays))
uj_slot = (mn % 15 != 0)                      # c45: UJ は分 ∈ {05,10,20,25,35,40,50,55}

def decluster(mask, decl=DECL):
    ii = np.where(mask)[0]; keep = []; last = -1e18
    for i in ii:
        if ts[i] - last >= decl: keep.append(i); last = ts[i]
    return np.array(keep, int)

J5 = decluster(cand & (zabs >= ZMAIN))
UJ = J5[(~isevbar[J5]) & uj_slot[J5]]
SJ = J5[(~isevbar[J5]) & (~uj_slot[J5])]
say(f"- npz {len(ts)} 本 {tt[0]}〜{tt[-1]}・cand {int(cand.sum())}・σ_trail 中央値 {np.nanmedian(sig[cand]):.2f} bp")
say(f"- **A0 複製**: declustered 5σ {len(J5)}（c45: 2166）・SJ {len(SJ)}（786）・UJ {len(UJ)}（937）")
j45 = pd.read_csv(os.path.join(DATA, "c45_jumps_5sigma_declustered.csv"))
same = set(j45["ts"].astype(np.int64)) == set(ts[J5].tolist())
say(f"- A0 c45 csv の ts 集合と一致: {same}（csv {len(j45)} 行）")
REP_OK = (len(J5) == 2166) and (len(SJ) == 786) and (len(UJ) == 937) and same
if not REP_OK:
    say("- **複製失敗 → 判定を出さず終了**"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); sys.exit(1)

PERIODS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

# ================= 時計とスロット =================
CLK = {}
def clockslots(name):
    if name in CLK: return CLK[name]
    tl = tt if name == "UTC" else tt.tz_convert(name)
    CLK[name] = (tl.hour * 12 + tl.minute // 5).to_numpy()
    return CLK[name]

VENUES = [("SGE 01:00 UTC",   "UTC",            S(1, 0),  3),
          ("London 08:00",    "Europe/London",  S(8, 0),  3),
          ("COMEX 08:20 ET",  NY,               S(8, 20), 2),
          ("NYSE 09:30 ET",   NY,               S(9, 30), 3)]

def wmask(ck, osl, wl):
    sl = clockslots(ck); return np.isin(sl, [(osl + k) % 288 for k in range(wl)])

# ================= A1/A2: 分母整合 =================
say("\n## A1 分母の整合: c55 の占有率 4.10% は UJ の母集団ではない")
etslot = clockslots(NY)
base_ok_c55 = nf & ~((etslot >= S(17, 0)) & (etslot <= S(18, 5))) & (tt.weekday.to_numpy() <= 4)   # c55 の base_ok
pool_uj = cand & (~isevbar) & uj_slot                                                              # UJ の真の母集団
Wall = np.zeros(len(ts), bool); PERV = {}
for vn, ck, osl, wl in VENUES:
    m = wmask(ck, osl, wl); PERV[vn] = m; Wall |= m
occ_c55 = Wall[base_ok_c55].mean()
occ_star = Wall[pool_uj].mean()
say(f"- c55 の分母で再現した占有率 occ(base_ok) = **{occ_c55*100:.2f}%**（c55 印字 4.10%）")
say(f"- UJ 母集団（cand ∧ 非EVDAY ∧ 分%15≠0）での占有率 occ* = **{occ_star*100:.2f}%** → 相対差 {(occ_star/occ_c55-1)*100:+.1f}%")
say(f"- 内訳: 開場窓 11 足のうち分%15=0 で UJ になれない足 = SGE 01:00・London 08:00・NYSE 09:30 の 3 足（残 8 足）。"
    f"nf3(直前3本非flat) 通過率 = 窓 {nf3[Wall & trading].mean()*100:.1f}% vs 全体 {nf3[trading].mean()*100:.1f}%")

def enrich(evt_idx, mW, pool, label, occ):
    n = len(evt_idx); k = int(mW[evt_idx].sum()); share = k / max(n, 1)
    se_b = math.sqrt(occ * (1 - occ) / max(n, 1)); zb = (share - occ) / se_b if se_b > 0 else np.nan
    e = share / occ if occ > 0 else np.nan
    selog = math.sqrt(1.0 / max(k, 1))
    return dict(label=label, n=n, k=k, share=share, occ=occ, e=e, z=zb,
                lo=e * math.exp(-1.96 * selog), hi=e * math.exp(1.96 * selog))

say("\n### A1 結果: 合成（4 会場合算）")
rows = []
for pname, y0, y1 in PERIODS:
    for dn, occ in (("c55 分母", occ_c55), ("整合 occ*", occ_star)):
        ev = UJ[(year[UJ] >= y0) & (year[UJ] <= y1)]
        # occ* は期間別に測り直す
        if dn == "整合 occ*":
            pm = pool_uj & (year >= y0) & (year <= y1); occu = Wall[pm].mean()
        else:
            pm = base_ok_c55 & (year >= y0) & (year <= y1); occu = Wall[pm].mean()
        d = enrich(ev, Wall, pm, f"{pname}/{dn}", occu); rows.append(d)
        say(f"- {pname} {dn}: {d['k']}/{d['n']} = {d['share']*100:.1f}%・占有 {d['occ']*100:.2f}% → "
            f"濃縮 **{d['e']:.2f}×** [95%CI {d['lo']:.2f}, {d['hi']:.2f}]・z {d['z']:+.1f}")
E_IN = [x for x in rows if x["label"].startswith("在") and "整合" in x["label"]][0]
E_OUT = [x for x in rows if x["label"].startswith("外") and "整合" in x["label"]][0]
A1_BREAK = (abs(occ_star / occ_c55 - 1) >= 0.20) or (E_IN["e"] < 3.0)
say(f"- **A1 判定**: 占有率の相対ずれ {abs(occ_star/occ_c55-1)*100:.1f}%（閾 20%）・補正後 在 濃縮 {E_IN['e']:.2f}×（閾 3.0×）"
    f" → {'BREAK' if A1_BREAK else 'not broken'}")

say("\n## A2 会場分解（整合分母・在/外）")
A2_cover1 = 0; PV = {}
for vn, ck, osl, wl in VENUES:
    mv = PERV[vn]; line = []
    for pname, y0, y1 in PERIODS[:2]:
        ev = UJ[(year[UJ] >= y0) & (year[UJ] <= y1)]; pm = pool_uj & (year >= y0) & (year <= y1)
        occv = mv[pm].mean(); d = enrich(ev, mv, pm, vn, occv)
        line.append(f"{pname} {d['k']}/{d['n']}・占有 {occv*100:.2f}% → **{d['e']:.2f}×** [{d['lo']:.2f}, {d['hi']:.2f}] z {d['z']:+.1f}")
        if pname.startswith("在"): PV[vn] = d
    say(f"- **{vn}**: " + " ／ ".join(line))
    if PV[vn]["lo"] <= 1.0 <= PV[vn]["hi"] or PV[vn]["k"] == 0: A2_cover1 += 1
tot_in = sum(PV[v]["k"] for v in PV)
say(f"- 在 W 事象の会場別シェア: " + " / ".join(f"{v.split(' ')[0]} {PV[v]['k']}（{PV[v]['k']/max(tot_in,1)*100:.0f}%）" for v in PV))
A2_BREAK = A2_cover1 >= 2
say(f"- **A2 判定**: 95%CI が 1.0 を含む会場 {A2_cover1}/4（閾 ≥2）→ {'BREAK（「4 会場の開場」の括りは成立しない）' if A2_BREAK else 'not broken'}")

# ================= A3: 位置プラセボ =================
say("\n## A3 位置プラセボ（各会場の窓を近傍 ±12 足に滑らせた順位・在 2010-20・UJ/eligible 率）")
A3_BREAK = False; A3_NOTE = []
for vn, ck, osl, wl in VENUES:
    sl = clockslots(ck); y0, y1 = 2010, 2020
    ev = UJ[(year[UJ] >= y0) & (year[UJ] <= y1)]; pm = pool_uj & (year >= y0) & (year <= y1)
    rates = []
    for shift in range(-12, 13):
        slots = [(osl + shift + k) % 288 for k in range(wl)]
        mv = np.isin(sl, slots); nW = int(mv[pm].sum()); kW = int(mv[ev].sum())
        rates.append((shift, kW / max(nW, 1) * 1e4, kW, nW))
    true_rate = [x for x in rates if x[0] == 0][0]
    rr = sorted(rates, key=lambda x: -x[1]); rank = [i for i, x in enumerate(rr) if x[0] == 0][0] + 1
    best = rr[0]
    shr = PV[vn]["k"] / max(tot_in, 1)
    brk = (shr >= 0.25) and (rank > 3)
    A3_BREAK |= brk
    say(f"- **{vn}**: 真位置 率 {true_rate[1]:.1f}/万（{true_rate[2]}/{true_rate[3]}）・順位 **{rank}/25**・"
        f"family 最良 shift {best[0]*5:+d} 分 率 {best[1]:.1f}（{best[2]}）・W シェア {shr*100:.0f}% → {'BREAK' if brk else 'ok'}")
    A3_NOTE.append((vn, rank, best[0]))
say(f"- **A3 判定**: {'BREAK' if A3_BREAK else 'not broken'}")

# ================= A4: 季節 vol 段差で説明できるか =================
say("\n## A4 開場という標識は検出器の季節段差を超える情報を持つか（UJ eligible 192 スロット・在+外 全期間）")
step = np.where(np.isfinite(sig) & nf, np.abs(r) / sig, np.nan)          # 検出器そのもの
rows4 = []
for s in range(288):
    m = pool_uj & (etslot == s)
    if m.sum() < 200: continue
    k = int(((etslot[UJ] == s)).sum())
    rows4.append((s, int(m.sum()), k, float(np.nanmedian(step[m]))))
D4 = pd.DataFrame(rows4, columns=["s", "N", "k", "x"])
D4 = D4[D4.x > 0]
# 重み付き log-log 回帰 log(rate) ~ a + b log(x)
rate = (D4.k + 0.5) / D4.N
X = np.c_[np.ones(len(D4)), np.log(D4.x.to_numpy())]; yv = np.log(rate.to_numpy()); w = D4.N.to_numpy().astype(float)
XtW = X.T * w; beta = np.linalg.solve(XtW @ X, XtW @ yv)
pred = np.exp(X @ beta)
D4["pred_k"] = pred * D4.N
open_et = sorted(set(etslot[Wall & uj_slot & trading]))
sub = D4[D4.s.isin(open_et)]
obs = int(sub.k.sum()); exp4 = float(sub.pred_k.sum())
ratio4 = obs / exp4 if exp4 > 0 else np.nan
se4 = math.sqrt(1.0 / max(obs, 1))
say(f"- 回帰 log(UJ率) = {beta[0]:.2f} + **{beta[1]:.2f}**·log(median |r|/σ_trail)（{len(D4)} スロット・N 重み）"
    f"・勾配の符号 {'正（段差の大きいスロットほど UJ が出やすい）' if beta[1]>0 else '負'}")
say(f"- 開場の UJ eligible スロット {sorted(f'{s//12:02d}:{(s%12)*5:02d}' for s in open_et)}")
say(f"- 観測 {obs} 事象 vs 段差回帰の予測 {exp4:.1f} → **観測/予測 {ratio4:.2f}×** "
    f"[95%CI {ratio4*math.exp(-1.96*se4):.2f}, {ratio4*math.exp(1.96*se4):.2f}]")
A4_RESID = not (ratio4 * math.exp(-1.96 * se4) <= 1.0 <= ratio4 * math.exp(1.96 * se4))
say(f"- **A4 判定**: 段差を超える残差 = {'あり（開場標識に固有の上乗せ）' if A4_RESID else 'なし（開場標識は vol 段差の言い換え）'}")
say("- 最も UJ 率の高い 10 スロット（ET・在+外）: " + ", ".join(
    f"{int(s)//12:02d}:{(int(s)%12)*5:02d} {int(k)}/{int(n)}" for s, n, k in
    D4.assign(rate=D4.k / D4.N).sort_values("rate", ascending=False)[["s", "N", "k"]].head(10).to_numpy()))

# ================= A5: decluster 感度 =================
say("\n## A5 decluster 感度（濃縮の安定性・整合分母・在 2010-20）")
A5_BREAK = False
base_e = E_IN["e"]
for nm, decl in (("decluster 無し", 0.0), ("1h", 3600.0), ("4h(本番)", 14400.0)):
    Jx = decluster(cand & (zabs >= ZMAIN), decl) if decl > 0 else np.where(cand & (zabs >= ZMAIN))[0]
    UJx = Jx[(~isevbar[Jx]) & uj_slot[Jx]]
    ev = UJx[(year[UJx] >= 2010) & (year[UJx] <= 2020)]; pm = pool_uj & (year >= 2010) & (year <= 2020)
    occu = Wall[pm].mean(); d = enrich(ev, Wall, pm, nm, occu)
    dev = abs(d["e"] / base_e - 1)
    if nm != "4h(本番)": A5_BREAK |= (dev >= 0.25)
    say(f"- {nm}: UJ {len(UJx)} 事象・{d['k']}/{d['n']} = {d['share']*100:.1f}% → 濃縮 **{d['e']:.2f}×**（本番比 {dev*100:+.0f}%）")
say(f"- **A5 判定**: {'BREAK' if A5_BREAK else 'not broken'}")

# ================= A6: 年・曜日 =================
say("\n## A6 08:20 ET の安定性（記述・判定外）")
m820 = (etslot == S(8, 20))
uj820 = UJ[m820[UJ]]
yc = pd.Series(year[uj820]).value_counts().sort_index()
say("- 08:20 ET UJ の年別: " + " ".join(f"{int(y)}:{int(c)}" for y, c in yc.items()))
pre = int(((year[uj820] >= 2010) & (year[uj820] <= 2015)).sum()); post = int((year[uj820] >= 2016).sum())
npre = int((pool_uj & m820 & (year <= 2015)).sum()); npost = int((pool_uj & m820 & (year >= 2016)).sum())
say(f"- pre 2010-15 {pre}/{npre} = {pre/max(npre,1)*1e4:.1f}/万 vs post 2016-26H1 {post}/{npost} = {post/max(npost,1)*1e4:.1f}/万")
WDN = "月火水木金"
wd820 = pd.Series(wd[uj820]).value_counts().sort_index()
wdall = pd.Series(wd[pool_uj & m820]).value_counts().sort_index()
say("- 08:20 ET UJ の曜日: " + " ".join(f"{WDN[int(k)]}{int(v)}（{v/max(int(wdall.get(k,1)),1)*1e4:.0f}/万）" for k, v in wd820.items()))
wdUJ = pd.Series(wd[UJ]).value_counts().sort_index()
say("- 参考 全 UJ の曜日: " + " ".join(f"{WDN[int(k)]}{int(v)}" for k, v in wdUJ.items() if int(k) <= 4))

# ================= A7: null への攻撃（vol 整合対照） =================
say("\n## A7 T2（H_OPEN null）への攻撃: 対照を vol 整合に置き換える")

def c55_z(clockname):
    sl = clockslots(clockname)
    ok = nf & ~((etslot >= S(17, 0)) & (etslot <= S(18, 5)))
    tl = tt if clockname == "UTC" else tt.tz_convert(clockname)
    wdl = tl.weekday.to_numpy(); ok = ok & (wdl <= 4)
    df = pd.DataFrame({"y": year[ok], "s": sl[ok], "r": r[ok]})
    g = df.groupby(["y", "s"])["r"]
    med = g.transform("median")
    mad = (df["r"] - med).abs().groupby([df["y"], df["s"]]).transform("median")
    n = g.transform("size")
    sg = 1.4826 * mad.to_numpy(); sg[n.to_numpy() < 100] = np.nan
    zc = np.full(len(r), np.nan); zc[ok] = df["r"].to_numpy() / sg
    return sl, zc, ok & np.isfinite(zc)

def ann_excl(clockname):
    ex = set()
    if clockname == NY:
        for h, m in [(8, 30), (8, 35), (10, 0), (10, 5), (14, 0), (14, 5)]: ex.add(S(h, m))
    if clockname == "Europe/London":
        for h, m in [(7, 0), (7, 5)]: ex.add(S(h, m))
    if clockname == "UTC":
        for h, m in [(1, 15), (1, 20)]: ex.add(S(h, m))
    return ex

def rate_pair(mW, mC, jump, msk):
    JW = int((msk & mW & jump).sum()); NW = int((msk & mW).sum())
    JC = int((msk & mC & jump).sum()); NC = int((msk & mC).sum())
    rW = JW / max(NW, 1); rC = JC / max(NC, 1); rho = rW / rC if rC > 0 else np.nan
    se = math.sqrt(1 / max(JW, 0.5) + 1 / max(JC, 0.5)); zst = math.log(rho) / se if rho and rho > 0 else np.nan
    return dict(JW=JW, NW=NW, JC=JC, NC=NC, rho=rho, z=zst, p=(1 - norm.cdf(zst)) if np.isfinite(zst) else np.nan)

say("\n### A7(i) 裾率 ρ はスロット vol と関係するか（ET 時計・在 2010-20・288 スロット）")
sl_ny, z_ny, ok_ny = c55_z(NY)
m_in = ok_ny & (year >= 2010) & (year <= 2020)
tab = []
for s in range(288):
    m = m_in & (sl_ny == s)
    if m.sum() < 300: continue
    tab.append((s, int(m.sum()), int((m & (np.abs(z_ny) >= 4)).sum()), float(np.median(np.abs(r[m])))))
T = pd.DataFrame(tab, columns=["s", "N", "J", "v"])
tr_ = (T.J + 0.5) / T.N
Xa = np.c_[np.ones(len(T)), np.log(T.v.to_numpy())]; ya = np.log(tr_.to_numpy()); wa = T.N.to_numpy().astype(float)
XtWa = Xa.T * wa; b2 = np.linalg.solve(XtWa @ Xa, XtWa @ ya)
resid = ya - Xa @ b2; sse = float((wa * resid ** 2).sum()); sst = float((wa * (ya - np.average(ya, weights=wa)) ** 2).sum())
say(f"- 回帰 log(|z|≥4 率) = {b2[0]:.3f} + **{b2[1]:+.3f}**·log(median |r| bp)（{len(T)} スロット）・R² {1-sse/sst:.3f}")
say(f"- 低 vol 四分位 平均率 {T[T.v<=T.v.quantile(.25)].eval('J/N').mean()*1e4:.0f}/万 vs "
    f"高 vol 四分位 {T[T.v>=T.v.quantile(.75)].eval('J/N').mean()*1e4:.0f}/万"
    f" → 勾配は {'負（高 vol スロットほど裾が軽い＝c55 の W<C は構造的に出やすい）' if b2[1]<0 else '正'}")

say("\n### A7(ii) vol 整合対照での ρ（在/外・Bonferroni 4 → 在 p≤0.0125）")
A7_REOPEN = False; A7ROWS = []
for vn, ck, osl, wl in VENUES:
    sl, zc, okc = c55_z(ck); ex = ann_excl(ck)
    Wslots = [(osl + k) % 288 for k in range(wl) if ((osl + k) % 288) not in ex]
    mW = np.isin(sl, Wslots)
    m_in_v = okc & (year >= 2010) & (year <= 2020)
    vW = float(np.median(np.abs(r[m_in_v & mW])))
    # 候補対照スロット: vol 整合 ±7.5%・W と公表足と W±2 足を除外
    near = set((osl + k) % 288 for k in range(-2, wl + 2))
    cslots = []
    for s in range(288):
        if s in near or s in ex: continue
        m = m_in_v & (sl == s)
        if m.sum() < 300: continue
        v = float(np.median(np.abs(r[m])))
        if v > 0 and abs(math.log(v / vW)) <= math.log(1.075): cslots.append(s)
    mC = np.isin(sl, cslots)
    jump = np.abs(zc) >= 4
    res = {}
    for pname, y0, y1 in PERIODS:
        msk = okc & (year >= y0) & (year <= y1)
        res[pname] = rate_pair(mW, mC, jump, msk)
    a = res["在 2010-20"]; b = res["外 2021-26H1"]
    reopen = (a["rho"] >= 1.3) and (a["z"] >= 2.0) and (a["p"] <= 0.0125) and (b["rho"] > 1)
    A7_REOPEN |= reopen
    A7ROWS.append((vn, a, b, res["近年 2024-26H1"], len(cslots), vW, reopen))
    say(f"- **{vn}**: W {len(Wslots)} 足 median|r| {vW:.2f} bp・vol 整合対照 {len(cslots)} スロット")
    for pname in [p[0] for p in PERIODS]:
        d = res[pname]
        say(f"  - {pname}: W {d['JW']}/{d['NW']} vs C {d['JC']}/{d['NC']} → **ρ_matched {d['rho']:.2f}**（z {d['z']:+.2f}・p {d['p']:.4f}）")
    say(f"  - 再開条件（在 ρ≥1.3 ∧ z≥2 ∧ p≤0.0125 ∧ 外 ρ>1）: {'成立' if reopen else '不成立'}")
say(f"- **A7 判定**: {'H_OPEN 再開（null は vol 勾配の人工物）' if A7_REOPEN else 'H_OPEN null は vol 整合対照でも生き残る'}")

# ================= 判定 =================
say("\n## 判定（事前規則）")
if A1_BREAK or A5_BREAK: v1 = "broken"
elif A2_BREAK or A3_BREAK: v1 = "partial（算術は残り「4 会場の開場」の括りが壊れる）"
else: v1 = "survived"
v2 = "broken（再開）" if A7_REOPEN else "survived"
say(f"- A1 {'BREAK' if A1_BREAK else 'ok'} / A2 {'BREAK' if A2_BREAK else 'ok'} / A3 {'BREAK' if A3_BREAK else 'ok'} / "
    f"A5 {'BREAK' if A5_BREAK else 'ok'} / A4 残差 {'あり' if A4_RESID else 'なし'} / A7 {'REOPEN' if A7_REOPEN else 'ok'}")
say(f"- **T1（§7 の UJ 開場濃縮）: {v1}**")
say(f"- **T2（H_OPEN null）: {v2}**")
say(f"\n- 実行 {time.time()-T0:.1f} s・seed {SEED}・読んだのは XAU_m5_close.npz・FOMC/CPI csv・c45 csv のみ（scan 無し・MT5 無し・外部通信無し）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", OUT)
