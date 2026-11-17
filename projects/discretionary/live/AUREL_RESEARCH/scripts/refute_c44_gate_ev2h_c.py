# -*- coding: utf-8 -*-
"""
[REFUTE cycle44 第3段 / 2026-11-17] 第1-2段で 10 規則のうち実質 1 つ（R10 窓の特定）しか landed せず、
対立仮説 H_VOL（高ボラ日）も B5 で死んだ。残る攻め口は 2 つだけ:
  (I) 多重検定の family: 第1段 R8 の経験 p は 0/2000 ＝ p<5e-4 しか言えない。
      family 72 なら Bonferroni 0.036 で生き残るが family 200 なら 0.12 で死ぬ。p を 20000 回で詰める。
  (II) 41（在 null → 外 t 3）の型そのものの校正: R8 は「外 t の帰無分布」を見ただけで、
      **「在で null かつゲート通過 → 外 t≥3.23」の同時確率**を見ていない。これが 41 の正しい帰無。
事前固定（第3段）:
  C1 高速校正 20000 回（偽イベント日集合・朝 192/午後 105 日・非発表日から）→ 片側経験 p と
     「在 |Δμ|≥0.048 ∧ 在 |t|<2（＝在 null）」で条件づけた外 t≥3.23 の割合（41 の帰無）。
     landed = 条件づけ後の割合 ≥ 0.05/72（family 72 で Bonferroni 生存できない）。
  C2 発表後 0-30 分の負（近年 −0.626・t −2.57）が本物か: 日クラスタ・符号検定・
     C1 の偽イベント分布で 0-30 分 Δμ の片側 p。landed（＝c44 の「継続」枠組みの反証として成立）= p<0.05。
  C3 前向き決着可能性: 日クラスタ se から必要な発表日数（t≥2 / t≥3）。
出力 data/refute_c44_gate_ev2h_c.md。読取専用・seed 20261117.
"""
import os, json, math
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c44_gate_ev2h_c.md"); L = []
NY = "America/New_York"; rng = np.random.default_rng(20261117)
def say(s=""): print(s, flush=True); L.append(s)
def epoch_et(dd, h, m):
    naive = pd.DatetimeIndex(dd) + pd.Timedelta(hours=h, minutes=m)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1+1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5-d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FOMC = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
NFP = nfp_dates_v2(); CPI = pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)
t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC, 14, 0)
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT/tr["risk"])*tr["dec"]
et_ = tr.entry_time.to_numpy(float)
def inwin(t0s, off=0.0, span=7200.0):
    s = np.sort(t0s[np.isfinite(t0s)]) + off
    pos = np.clip(np.searchsorted(s, et_, side="right")-1, 0, len(s)-1)
    return (et_ >= s[pos]) & (et_ < s[pos]+span), s[pos]
m_n, p_n = inwin(t_nfp); m_f, p_f = inwin(t_fomc)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
hh = e_ny.hour.to_numpy()+e_ny.minute.to_numpy()/60
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize()); tr["wd"] = e_ny.weekday.to_numpy()
tr["ev"] = m_n | m_f
tr["mins"] = np.where(m_n, (et_-p_n)/60.0, np.where(m_f, (et_-p_f)/60.0, np.nan))
evdays = pd.DatetimeIndex(list(NFP)+list(FOMC)+list(CPI)); tr["isevday"] = tr.day.isin(evdays)
tr["am"] = (hh >= 8.5) & (hh < 10.5); tr["pm"] = (hh >= 14) & (hh < 16)
tr["ctrl"] = (tr.am | tr.pm) & ~tr.isevday & (tr.wd <= 4)

def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    dm = a.mean()-b.mean(); se = math.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
    return dm, (dm/se if se > 0 else np.nan)
def cl_t(A, B, kA, kB):
    def se1(x, k):
        x = np.asarray(x, float); n = len(x); m = x.mean()
        s = pd.DataFrame({"x": x-m, "k": np.asarray(k)}).groupby("k").x.sum(); G = len(s)
        return (math.sqrt(s.pow(2).sum()/(n**2)*(G/(G-1.0))) if G > 1 else np.nan), G
    sa, Ga = se1(A, kA); sb, _ = se1(B, kB); dm = np.mean(A)-np.mean(B); se = math.sqrt(sa**2+sb**2)
    return dm, (dm/se if se > 0 else np.nan), se, Ga

say("# [REFUTE cycle44 第3段] 多重検定 family の詰め・41 型の同時確率・0-30 分の負")
say("")
# ---------- C1 高速校正 20000 回 ----------
daycode, dayuniq = pd.factorize(tr.day)
tr["dc"] = daycode
yr = tr.year.to_numpy(); Rs = tr.Rs.to_numpy(); amm = tr.am.to_numpy(); pmm = tr.pm.to_numpy()
ctrlm = tr.ctrl.to_numpy(); dcm = daycode
M_IN = (yr >= 2010) & (yr <= 2020); M_OUT = (yr >= 2021) & (yr <= 2026)
isevd_day = pd.Series(dayuniq).isin(evdays).to_numpy()
wd_day = pd.DatetimeIndex(dayuniq).weekday.to_numpy()
yr_day = pd.DatetimeIndex(dayuniq).year.to_numpy()
cand = np.where((~isevd_day) & (wd_day <= 4))[0]
n_am = int(pd.Series(NFP.normalize()).isin(pd.DatetimeIndex(dayuniq)).sum())
n_pm = int(pd.Series(FOMC.normalize()).isin(pd.DatetimeIndex(dayuniq)).sum())
REPS = 20000
res = np.full((REPS, 6), np.nan)   # dm_in,t_in,dm_out,t_out, dm30_out, t30_out
mask_am_day = np.zeros(len(dayuniq), bool); mask_pm_day = np.zeros(len(dayuniq), bool)
mins = tr["mins"].to_numpy()
for r in range(REPS):
    mask_am_day[:] = False; mask_pm_day[:] = False
    mask_am_day[cand[rng.choice(len(cand), n_am, replace=False)]] = True
    mask_pm_day[cand[rng.choice(len(cand), n_pm, replace=False)]] = True
    pev = (mask_am_day[dcm] & amm) | (mask_pm_day[dcm] & pmm)
    pany = mask_am_day[dcm] | mask_pm_day[dcm]
    for j, era in ((0, M_IN), (2, M_OUT)):
        e = pev & era; c = ctrlm & era & ~pany
        if e.sum() < 5: continue
        dm, t = welch(Rs[e], Rs[c]); res[r, j] = dm; res[r, j+1] = t
G = pd.DataFrame(res[:, :4], columns=["dm_in", "t_in", "dm_out", "t_out"]).dropna()
say(f"## C1 校正 {len(G)} 組（朝 {n_am} 日 + 午後 {n_pm} 日・非発表日から復元なし抽出）")
say(f"- 外 t 帰無分布: 平均 {G.t_out.mean():+.3f}・sd {G.t_out.std(ddof=1):.3f}・p99 {G.t_out.quantile(0.99):+.2f}・max {G.t_out.max():+.2f}")
k = int((G.t_out >= 3.23).sum()); p1 = (k+1)/(len(G)+1)
say(f"- **片側経験 p（t_out ≥ +3.23）= {k}/{len(G)} → p ≤ {p1:.2e}**（+1 補正）")
k2 = int((G.dm_out >= 0.481).sum()); p2 = (k2+1)/(len(G)+1)
say(f"- 片側経験 p（Δμ_out ≥ +0.481）= {k2}/{len(G)} → p ≤ {p2:.2e}")
gate = G[G.dm_in.abs() >= 0.048]
pat = gate[gate.t_in.abs() < 2.0]
say(f"- ゲート通過（在 |Δμ|≥0.048）{len(gate)}/{len(G)} = {len(gate)/len(G)*100:.1f}%  "
    f"／そのうち **在 null（|t_in|<2）= {len(pat)} 組 = 全体の {len(pat)/len(G)*100:.1f}%**")
k3 = int((pat.t_out >= 3.23).sum()); p3 = (k3+1)/(len(pat)+1)
say(f"- **41 型の帰無（ゲート通過 ∧ 在 null に条件づけた 外 t ≥ +3.23）= {k3}/{len(pat)} → p ≤ {p3:.2e}**")
say(f"- 条件づけ後の 外 t: 平均 {pat.t_out.mean():+.3f}・sd {pat.t_out.std(ddof=1):.3f}・p99 {pat.t_out.quantile(0.99):+.2f}・max {pat.t_out.max():+.2f}")
say("")
say("| family | Bonferroni（41 型 p）| 生存 |")
say("|---|---|---|")
for fam in (36, 45, 72, 100, 200, 500):
    pb = min(p3*fam, 1.0)
    say(f"| {fam} | {pb:.3f} | {'生存' if pb < 0.05 else '**死亡**'} |")
say("")
# ---------- C2 0-30 分の負 ----------
say("## C2 発表後 0-30 分の負（c44 の「継続」枠組みへの反証）")
say("| 窓 | n | Δμ (Welch t) | 日クラスタ t | R*>0 の割合 ev/ctrl | 符号検定 p |")
say("|---|---|---|---|---|---|")
for lab, lo, hi in [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]:
    o = tr[(tr.year >= lo) & (tr.year <= hi)]; B = o[o.ctrl]
    a = o[o.ev & (o.mins >= 0) & (o.mins < 30)]
    if len(a) < 3: say(f"| {lab} | {len(a)} | n/a | | | |"); continue
    dm, t = welch(a.Rs, B.Rs); _, tc, _, Gc = cl_t(a.Rs.to_numpy(), B.Rs.to_numpy(), a.day.to_numpy(), B.day.to_numpy())
    pw = (a.Rs > 0).mean(); pc = (B.Rs > 0).mean()
    nn = len(a); kk = int((a.Rs > 0).sum())
    z = (kk - nn*pc)/math.sqrt(nn*pc*(1-pc)); sp = 2*(1-0.5*(1+math.erf(abs(z)/math.sqrt(2))))
    say(f"| {lab} | {nn} | {dm:+.3f} ({t:+.2f}) | {tc:+.2f} (G {Gc}) | {pw*100:.0f}%/{pc*100:.0f}% | {sp:.3f} |")
say("")
# ---------- C3 前向き決着可能性 ----------
say("## C3 前向き決着可能性（日クラスタ se から）")
o = tr[(tr.year >= 2021) & (tr.year <= 2026)]; A, B = o[o.ev], o[o.ctrl]
dm, tc, se, Ga = cl_t(A.Rs.to_numpy(), B.Rs.to_numpy(), A.day.to_numpy(), B.day.to_numpy())
say(f"- 外: Δμ {dm:+.3f}・日クラスタ se {se:.3f}・G_ev {Ga} 日・se ∝ 1/sqrt(日数)")
for tgt in (2.0, 3.0):
    for eff in (dm, 0.598, 0.305):
        need = Ga * (tgt*se/eff)**2
        say(f"  - t≥{tgt:.0f} を Δμ={eff:+.3f} で達成に必要な発表日数 ≈ {need:.0f} 日（年 ~28 日 → {need/28:.1f} 年）")
open(OUT, "w", encoding="utf-8").write("\n".join(L)+"\n"); print("saved", OUT)
