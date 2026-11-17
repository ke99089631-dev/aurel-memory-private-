# -*- coding: utf-8 -*-
"""
[REFUTE cycle44 第2段 / 2026-11-17] 第1段（refute_c44_gate_ev2h.py）で landed した 2 本を決着させる:
  R5 幾何マッチ: Δμ +0.481 → +0.352 (t 1.98)。ただし対照プールが 1440 → 76 本に落ちたので
      「点推定が縮んだ」のか「se が機械的に膨らんだ」のかが分離できていない。
  R10 機構: 0-30 分 Δμ **−0.123**（近年 −0.626 t −2.57）・30-60 +0.565・60-120 +0.685、
      かつ**発表後 2-4 時間 +0.514 (t 2.25)** ＝ 発表からの距離で減衰しない。
      → 対立仮説 H_VOL: 「発表後 2 時間」ではなく「**発表日＝高ボラ日**で、金 scan の壁抜けは高ボラ日に強い」。
         ev の atr 平均 5.40 vs ctrl 2.99（SMD +0.69）はこの仮説と整合。

=== 事前固定（第2段・結果を見る前） ===
B1 窓 vs 日: 発表日の**全時間帯**本 vs 非発表日の全時間帯本。窓効果なら日全体では薄まるはず。
B2 回帰調整（対照プールを保ったまま幾何を落とす）: Rs ~ ev + log atr + log risk + b + am、
   HC1 と 日クラスタ se。ev 係数が t<2 なら R5 landed 確定。
B3 atr 層別: 外の atr 五分位内で Δμ（対照プール 全量）。全層で正かつ t≥2 が 1 層でもあれば H_VOL だけでは説明不可。
B4 1:5 復元マッチ（対照プールを戻す）＋日クラスタ se。
B5 **ボラ一致プラセボ（決定的）**: 非発表日のうち day 中央 atr 上位 N 日（N = ev 日数）を偽イベント日とし、
   同じ時間窓で Δμ。これが +0.48 を再現したら「発表」ではなく「高ボラ日」＝H_VOL が勝ち、発表の枠組みは broken。
   2000 回のランダム版（atr 上位 30% の非発表日から N 日抽出）で経験分布も出す。
B6 距離別: 0-2h / 2-4h / 4-6h / 発表日の窓外 で Δμ。
B7 日単位集計（1 日 1 観測）＋順位検定（Mann-Whitney）で fat tail に依存しない確認。
B8 多重検定: 第1段 R8 の経験帰無（2000 組で t≥3.23 が 0 回）→ p<5e-4。family 45/72 で Bonferroni。
出力 data/refute_c44_gate_ev2h_b.md。読取専用・seed 20261117.
"""
import os, json, math
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c44_gate_ev2h_b.md"); L = []
NY = "America/New_York"; SEED = 20261117; rng = np.random.default_rng(SEED)
def say(s=""): print(s, flush=True); L.append(s)

def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
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
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
def inwin(t0s, span=7200.0, off=0.0):
    t0s = np.sort(t0s[np.isfinite(t0s)]) + off
    pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1)
    return (et_ >= t0s[pos]) & (et_ < t0s[pos] + span)
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY)
hh = e_ny.hour.to_numpy() + e_ny.minute.to_numpy() / 60
tr["day"] = pd.DatetimeIndex(e_ny.tz_localize(None).normalize()); tr["hh"] = hh; tr["wd"] = e_ny.weekday.to_numpy()
tr["nfp"] = inwin(t_nfp); tr["fomc"] = inwin(t_fomc); tr["ev"] = tr.nfp | tr.fomc
evdays = pd.DatetimeIndex(list(NFP) + list(FOMC) + list(CPI)); tr["isevday"] = tr.day.isin(evdays)
tr["am"] = (hh >= 8.5) & (hh < 10.5); tr["pm"] = (hh >= 14) & (hh < 16); tr["inh"] = tr.am | tr.pm
tr["ctrl"] = tr.inh & ~tr.isevday & (tr.wd <= 4)
# NFP/FOMC 日（CPI 単独日は ev 対象外なので「発表日」の定義は NFP|FOMC）
nf_days = pd.DatetimeIndex(list(NFP.normalize()) + list(FOMC.normalize()))
tr["nfday"] = tr.day.isin(nf_days)

def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan
    dm = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    return dm, (dm/se if se > 0 else np.nan)
def cl_t(A, B, kA, kB):
    def se1(x, k):
        x = np.asarray(x, float); n = len(x); m = x.mean()
        s = pd.DataFrame({"x": x - m, "k": np.asarray(k)}).groupby("k").x.sum()
        G = len(s)
        return (math.sqrt((s.pow(2).sum())/(n**2)*(G/(G-1.0))) if G > 1 else np.nan), G
    sa, Ga = se1(A, kA); sb, Gb = se1(B, kB)
    dm = np.mean(A) - np.mean(B); se = math.sqrt(sa**2 + sb**2)
    return dm, (dm/se if se > 0 else np.nan), Ga
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
def sub(lo, hi): return tr[(tr.year >= lo) & (tr.year <= hi)]

say("# [REFUTE cycle44 第2段] 「発表後 2 時間」 vs 「高ボラ日」の分離・幾何調整の se 分解")
say("")

# ---------- B1 窓 vs 日 ----------
say("## B1 窓 vs 日（発表日の全時間帯 vs 非発表日の全時間帯）")
say("| 窓 | 発表窓(0-2h) Δμ(t) n | 発表日・窓外 Δμ(t) n | 発表日・全日 Δμ(t) n | 対照 n |")
say("|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    B = o[~o.isevday & (o.wd <= 4)]        # 非発表日・全時間帯
    Bw = o[o.ctrl]                          # 非発表日・同時刻窓
    a1 = o[o.ev]; a2 = o[o.nfday & ~o.ev]; a3 = o[o.nfday]
    d1, t1 = welch(a1.Rs, Bw.Rs); d2, t2 = welch(a2.Rs, B.Rs); d3, t3 = welch(a3.Rs, B.Rs)
    say(f"| {lab} | {d1:+.3f}({t1:+.2f}) {len(a1)} | {d2:+.3f}({t2:+.2f}) {len(a2)} | {d3:+.3f}({t3:+.2f}) {len(a3)} | {len(B)} |")
say("")

# ---------- B2 回帰調整 ----------
say("## B2 回帰調整（対照プール全量・幾何を共変量に）")
def ols(y, X, clu=None):
    XtX = np.linalg.pinv(X.T @ X); bet = XtX @ (X.T @ y); r = y - X @ bet
    n, k = X.shape
    S = (X * r[:, None]); V = XtX @ (S.T @ S) @ XtX * (n/(n-k))
    hc1 = np.sqrt(np.diag(V))
    out = [bet, hc1, None]
    if clu is not None:
        df = pd.DataFrame(S); df["k"] = np.asarray(clu)
        M = df.groupby("k").sum().to_numpy(); G = M.shape[0]
        Vc = XtX @ (M.T @ M) @ XtX * (G/(G-1.0)) * ((n-1)/(n-k))
        out[2] = (np.sqrt(np.diag(Vc)), G)
    return out
say("| 窓 | 仕様 | ev 係数 | HC1 t | 日クラスタ t (G) |")
say("|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); s = o[o.ev | o.ctrl].copy()
    y = s.Rs.to_numpy(float)
    base = np.column_stack([np.ones(len(s)), s.ev.to_numpy(float)])
    geo = np.column_stack([base, np.log(s.atr.to_numpy()), np.log(s.risk.to_numpy()), s.b.to_numpy(), s.am.to_numpy(float)])
    for nm, X in [("ev のみ", base), ("ev + log atr + log risk + b + am", geo)]:
        bet, hc1, cl = ols(y, X, s.day.to_numpy())
        say(f"| {lab} | {nm} | {bet[1]:+.3f} | {bet[1]/hc1[1]:+.2f} | {bet[1]/cl[0][1]:+.2f} ({cl[1]}) |")
say("")

# ---------- B3 atr 層別 ----------
say("## B3 atr 五分位内 Δμ（対照プール全量）")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); s = o[o.ev | o.ctrl].copy()
    q = pd.qcut(s.atr, 5, labels=False, duplicates="drop"); s["q"] = q
    cells = []
    for k in sorted(s.q.dropna().unique()):
        g = s[s.q == k]; a, b = g[g.ev], g[g.ctrl]
        dm, t = welch(a.Rs, b.Rs)
        cells.append(f"Q{int(k)+1} n{len(a)}/{len(b)} {dm:+.3f}({t:+.2f})")
    say(f"- {lab}: " + " · ".join(cells))
    # 最上位層のみ（ev と同じボラ帯）
    g = s[s.q == sorted(s.q.dropna().unique())[-1]]
    a, b = g[g.ev], g[g.ctrl]
    dm, t, G = cl_t(a.Rs.to_numpy(), b.Rs.to_numpy(), a.day.to_numpy(), b.day.to_numpy())
    say(f"  - 最上位 atr 層のみ 日クラスタ: Δμ {dm:+.3f} t {t:+.2f} (G_ev {G}) / ev 本の {len(a)/max((s.ev).sum(),1)*100:.0f}% がこの層")
say("")

# ---------- B4 1:5 復元マッチ ----------
say("## B4 1:5 復元マッチ（同 side/wall_kind/窓・log atr/log risk/b 最近傍）")
say("| 窓 | ev n | Δμ_1:5 (t) | 日クラスタ t | 残存 SMD atr/risk |")
say("|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A = o[o.ev].reset_index(drop=True); B = o[o.ctrl].reset_index(drop=True)
    X = np.column_stack([np.log(A.atr), np.log(A.risk), A.b]); Y = np.column_stack([np.log(B.atr), np.log(B.risk), B.b])
    sd = np.std(np.vstack([X, Y]), 0, ddof=1); sd[sd == 0] = 1; Xs, Ys = X/sd, Y/sd
    sA = (A.side.astype(str)+"|"+A.wall_kind.astype(str)+"|"+np.where(A.am, "AM", "PM")).to_numpy()
    sB = (B.side.astype(str)+"|"+B.wall_kind.astype(str)+"|"+np.where(B.am, "AM", "PM")).to_numpy()
    pa, pb, w = [], [], []
    for i in range(len(A)):
        cand = np.where(sB == sA[i])[0]
        if len(cand) == 0: continue
        dist = np.sqrt(((Ys[cand]-Xs[i])**2).sum(1)); k = min(5, len(cand))
        sel = cand[np.argsort(dist)[:k]]
        pa.append(i); pb.extend(sel.tolist()); w.extend([1.0/k]*k)
    a = A.iloc[pa]; b = B.iloc[pb]; w = np.array(w)
    mb = np.average(b.Rs.to_numpy(), weights=w)
    # 重み付き分散の se（近似）
    vb = np.average((b.Rs.to_numpy()-mb)**2, weights=w) / (w.sum())
    dm = a.Rs.mean() - mb; se = math.sqrt(a.Rs.var(ddof=1)/len(a) + vb)
    _, tc, _ = cl_t(a.Rs.to_numpy(), b.Rs.to_numpy(), a.day.to_numpy(), b.day.to_numpy())
    spa = math.sqrt((a.atr.var(ddof=1)+b.atr.var(ddof=1))/2); spr = math.sqrt((a.risk.var(ddof=1)+b.risk.var(ddof=1))/2)
    say(f"| {lab} | {len(a)} | {dm:+.3f} ({dm/se:+.2f}) | {tc:+.2f} | {(a.atr.mean()-b.atr.mean())/spa:+.3f}/{(a.risk.mean()-b.risk.mean())/spr:+.3f} |")
say("")

# ---------- B5 ボラ一致プラセボ（決定的） ----------
say("## B5 ボラ一致プラセボ（非発表日の高 atr 日を偽イベント日に）")
# 日レベル atr = その日の窓内本の中央 atr
dayatr = tr[tr.inh & (tr.wd <= 4)].groupby("day").atr.median()
daycnt = tr[tr.inh & (tr.wd <= 4)].groupby("day").size()
for lab, lo, hi in ERAS:
    o = sub(lo, hi)
    evd = pd.DatetimeIndex(o[o.ev].day.unique()); N = len(evd)
    cands = [x for x in dayatr.index if (x not in set(evdays)) and (x.year >= lo) and (x.year <= hi) and x.weekday() <= 4]
    da = dayatr.loc[cands].sort_values(ascending=False)
    top = pd.DatetimeIndex(da.index[:N])
    A = o[o.day.isin(top) & o.inh]; B = o[o.ctrl & ~o.day.isin(top)]
    dm, t = welch(A.Rs, B.Rs); _, tc, _ = cl_t(A.Rs.to_numpy(), B.Rs.to_numpy(), A.day.to_numpy(), B.day.to_numpy())
    say(f"- {lab}: 高 atr 非発表日 上位 {N} 日 → n {len(A)}・Δμ **{dm:+.3f} (t {t:+.2f}・日クラスタ {tc:+.2f})**・"
        f"day atr 中央 偽 {da.iloc[:N].median():.2f} vs 実発表日 {dayatr.reindex(evd).median():.2f}")
# ランダム版（atr 上位 30% の非発表日から N 日・2000 回）: 外のみ
o = sub(2021, 2026); evd = pd.DatetimeIndex(o[o.ev].day.unique()); N = len(evd)
cands = [x for x in dayatr.index if (x not in set(evdays)) and (2021 <= x.year <= 2026) and x.weekday() <= 4]
da = dayatr.loc[cands].sort_values(ascending=False); pool = pd.DatetimeIndex(da.index[:max(int(len(da)*0.30), N)])
Rs = o.Rs.to_numpy(); dyo = o.day.to_numpy(); inh = o.inh.to_numpy(); ctrlm = o.ctrl.to_numpy()
pl = np.empty(1500)
for r in range(1500):
    pick = set(np.asarray(pool)[rng.choice(len(pool), N, replace=False)])
    m = np.isin(dyo, list(pick)) & inh
    c = ctrlm & ~np.isin(dyo, list(pick))
    dm, t = welch(Rs[m], Rs[c]); pl[r] = dm
say(f"- ランダム高ボラ版（atr 上位 30% の非発表日 {len(pool)} 日から {N} 日・1500 回）: "
    f"Δμ 平均 {np.nanmean(pl):+.3f}・sd {np.nanstd(pl, ddof=1):.3f}・p90 {np.nanpercentile(pl,90):+.3f}・max {np.nanmax(pl):+.3f}・"
    f"実測 +0.481 以上 **{int((pl>=0.481).sum())}/1500**")
say("")

# ---------- B6 距離別 ----------
say("## B6 発表からの距離別 Δμ（外 2021-26H1 / 近年）")
offs = [(0, "0-2h"), (7200, "2-4h"), (14400, "4-6h")]
say("| 窓 | " + " | ".join(n for _, n in offs) + " | 発表日・窓外 |")
say("|---|" + "---|"*(len(offs)+1))
for lab, lo, hi in ERAS:
    o = sub(lo, hi); B = o[o.ctrl]; cells = []
    for off, nm in offs:
        m = (inwin(t_nfp, off=off) | inwin(t_fomc, off=off))
        a = tr[m & (tr.year >= lo) & (tr.year <= hi)]
        if off > 0: a = a[~a.ev]
        dm, t = welch(a.Rs, B.Rs); cells.append(f"n{len(a)} {dm:+.3f}({t:+.2f})")
    a = o[o.nfday & ~o.ev]; dm, t = welch(a.Rs, B.Rs); cells.append(f"n{len(a)} {dm:+.3f}({t:+.2f})")
    say(f"| {lab} | " + " | ".join(cells) + " |")
say("")

# ---------- B7 日単位・順位検定 ----------
say("## B7 日単位集計（1 日 1 観測）＋順位検定")
def mwu(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    allv = np.concatenate([a, b]); rk = pd.Series(allv).rank().to_numpy()
    n1, n2 = len(a), len(b); U = rk[:n1].sum() - n1*(n1+1)/2
    mu = n1*n2/2; sg = math.sqrt(n1*n2*(n1+n2+1)/12)
    z = (U-mu)/sg; return z, 2*(1-0.5*(1+math.erf(abs(z)/math.sqrt(2))))
say("| 窓 | 日数 ev/ctrl | 日平均 ev/ctrl | Δ (t) | MWU z (p) |")
say("|---|---|---|---|---|")
for lab, lo, hi in ERAS:
    o = sub(lo, hi); A = o[o.ev].groupby("day").Rs.mean(); B = o[o.ctrl].groupby("day").Rs.mean()
    dm, t = welch(A, B); z, p = mwu(A, B)
    say(f"| {lab} | {len(A)}/{len(B)} | {A.mean():+.3f}/{B.mean():+.3f} | {dm:+.3f} ({t:+.2f}) | {z:+.2f} ({p:.4f}) |")
say("")

# ---------- B8 多重検定 ----------
say("## B8 多重検定（第1段 R8 の経験帰無を使う）")
p_emp = 1.0/2000
for fam in (36, 45, 72, 100):
    say(f"- 経験 p < {p_emp:.1e}（t≥3.23 が 2000 組で 0 回）→ Bonferroni({fam}) < {min(p_emp*fam,1):.3f}")
say("- ゲート通過率 67%（＝在 |Δμ|≥0.048 はほぼ無条件）だが、通過組の外 t の sd は 1.03 ＝ 名目 t は校正済み。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
