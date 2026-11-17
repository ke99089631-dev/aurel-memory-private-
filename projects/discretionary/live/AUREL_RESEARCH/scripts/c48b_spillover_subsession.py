# -*- coding: utf-8 -*-
"""
[cycle48 補足 b・事後・記述] c48 主セル H_SPILL PASS（γ_S 在 +0.104 t 4.4／外 +0.052 t 2.4）の**最重大反証の検査**:
金のセッション d+1（18:00 ET d → 17:00 ET d+1）は米株現物時間（09:30–16:00 ET d+1）を含む。株ボラは持続し（φ_S ≈0.3〜0.5）、
金の NY 時間ボラは株ボラと同時に動く（c20 ρ(0) 外 +15%）→ γ_S>0 は「株ボラの自己持続が金の NY 時間を通して見えているだけ」
（先行ではない）かもしれない。判別: 翌セッションの金 RV を **pre-US（18:00 ET d → 08:00 ET d+1・米株が現物で動く前）** と
**US（08:00 → 17:00 ET d+1）** に分け、同じ M2 統制で γ_S^pre と γ_S^US を印字する。
  - γ_S^pre >0 が立つ → 株ボラ・ショックは米株が再び動く前の金（アジア・ロンドン）に伝わる＝時間帯を跨ぐ伝播（meteor shower）。
  - γ_S^pre ≈0 ∧ γ_S^US >0 → 株ボラの持続の別名（heat wave）＝市場横断の先行ではない。
  - 追加（look-ahead・機構分解のみ）: US 部分に同日の US500 現物 RV_{d+1} を同時に入れると γ_S^US が消えるか。
事後・判定外・記述。seed 20261118。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c48b_spillover_subsession.md")
NY = "America/New_York"; NWLAG = 5
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle48 補足 b・事後] 翌セッション金 RV の時間帯分解（pre-US 18–08 ET vs US 08–17 ET）× 株ボラ・ショック — {time.strftime('%Y-%m-%d %H:%M')}")

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
NFP = {d.date().toordinal() for d in nfp_dates_v2()}
FO = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); FOMC = {pd.Timestamp(d).date().toordinal() for d in FO[FO["scheduled"] == 1]["date"]}
CP = pd.read_csv(os.path.join(MAC, "CPI_dates.csv")); CPI = {pd.Timestamp(d).date().toordinal() for d in CP["date"]}
EVT = NFP | FOMC | CPI

def nw_ols(y, X, lag=NWLAG):
    y = np.asarray(y, float); X = np.asarray(X, float)
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b; Zu = Z * u[:, None]; S = Zu.T @ Zu
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = Zu[l:].T @ Zu[:-l]; S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    return dict(b=b, se=np.sqrt(np.diag(V)), n=n, r2=1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum())

def load_npz(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    return ts, lc, r, flat, pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)

# gold: full session + sub-sessions
ts, lc, r, flat, dt_ny = load_npz("XAU")
sess = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]"); o = sess.astype("int64") + dt.date(1970, 1, 1).toordinal()
hr = dt_ny.hour.to_numpy(); pre = (hr >= 18) | (hr < 8); us = (hr >= 8) & (hr < 17)
keep = ~flat
df = pd.DataFrame({"o": o[keep], "r2": r[keep] ** 2, "pre": pre[keep], "us": us[keep]})
g = df.groupby("o", sort=True)
D = pd.DataFrame({"rv": g["r2"].sum(), "nf": g["r2"].size(),
                  "rv_pre": df[df.pre].groupby("o")["r2"].sum(), "nf_pre": df[df.pre].groupby("o")["r2"].size(),
                  "rv_us": df[df.us].groupby("o")["r2"].sum(), "nf_us": df[df.us].groupby("o")["r2"].size()})
D["date"] = pd.to_datetime([dt.date.fromordinal(int(x)) for x in D.index]); D["wd"] = D["date"].dt.weekday
D = D[(D.wd <= 4) & (D.nf >= 100)].reset_index()
D["lrv"] = np.log(D.rv); D["lrv5"] = D.lrv.rolling(5).mean(); D["gap"] = np.r_[np.nan, np.diff(D.o.to_numpy())]
D["lpre"] = np.where(D.nf_pre >= 60, np.log(D.rv_pre), np.nan); D["lus"] = np.where(D.nf_us >= 40, np.log(D.rv_us), np.nan)
D["year"] = D.date.dt.year; D["evt"] = D.o.isin(EVT)
say(f"- XAU 有効日 {len(D)}・pre-US 有効（nf≥60） {int(np.isfinite(D.lpre).sum())}・US 有効（nf≥40） {int(np.isfinite(D.lus).sum())}・RV シェア 中央値 pre {np.nanmedian(D.rv_pre/D.rv)*100:.0f}%／US {np.nanmedian(D.rv_us/D.rv)*100:.0f}%")

# US500 cash
ts, lc, r, flat, dt_ny = load_npz("US500")
mins = dt_ny.hour.to_numpy() * 60 + dt_ny.minute.to_numpy(); cash = (mins >= 570) & (mins < 960)
day = dt_ny.tz_localize(None).values.astype("datetime64[D]"); oS = day.astype("int64") + dt.date(1970, 1, 1).toordinal()
keep = cash & ~flat; dfs = pd.DataFrame({"o": oS[keep], "r2": r[keep] ** 2}); gs = dfs.groupby("o", sort=True)
S = pd.DataFrame({"rv": gs["r2"].sum(), "nf": gs["r2"].size()}); S["date"] = pd.to_datetime([dt.date.fromordinal(int(x)) for x in S.index])
S = S[(S.date.dt.weekday <= 4) & (S.nf >= 60)].reset_index(); S["lrvS"] = np.log(S.rv); S["lrv5S"] = S.lrvS.rolling(5).mean()
GV = pd.read_csv(os.path.join(MAC, "GVZCLS.csv"), na_values="."); GV.columns = ["date", "gvz"]; GV["date"] = pd.to_datetime(GV.date); GV = GV.dropna()
D = D.merge(S[["date", "lrvS", "lrv5S"]], on="date", how="left").merge(GV, on="date", how="left"); D["lgvz"] = np.log(D.gvz)

# frame: predictors at d, outcomes at d+1 ; also US500 contemporaneous at d+1 (look-ahead, mechanism only)
F = pd.DataFrame({"y": D.lrv.to_numpy()[1:], "ypre": D.lpre.to_numpy()[1:], "yus": D.lus.to_numpy()[1:],
                  "lrv": D.lrv.to_numpy()[:-1], "lrv5": D.lrv5.to_numpy()[:-1], "lpre": D.lpre.to_numpy()[:-1], "lus": D.lus.to_numpy()[:-1],
                  "lgvz": D.lgvz.to_numpy()[:-1], "lrvS": D.lrvS.to_numpy()[:-1], "lrv5S": D.lrv5S.to_numpy()[:-1], "lrvS1": D.lrvS.to_numpy()[1:],
                  "evt0": D.evt.to_numpy()[:-1].astype(float), "evt1": D.evt.to_numpy()[1:].astype(float), "brk": (D.gap.to_numpy()[1:] > 1).astype(float),
                  "year": D.year.to_numpy()[:-1]})
F = F[np.isfinite(F[["y", "ypre", "yus", "lrv", "lrv5", "lpre", "lus", "lgvz", "lrvS", "lrv5S"]].to_numpy()).all(1) & (F.year >= 2012)].reset_index(drop=True)
say(f"- フレーム {len(F)} 行（c48 主 3437 行のうち pre/US 両方の有効日）")
WIN = {"在 2012-20": (2012, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
BASE = ["lrv", "lrv5", "evt0", "evt1", "brk", "lgvz"]
say("\n| 窓 | n | 全セッション γ_S (NW t) | **pre-US γ_S^pre (t)** [own lpre 統制] | **US γ_S^US (t)** [own lus 統制] | US + 同日 US500 RV_(d+1)（look-ahead）: γ_S^US (t)・β_contemp (t) | 全 + 同日 US500 RV_(d+1): γ_S (t) |")
say("|---|---|---|---|---|---|---|")
for wn, (y0, y1) in WIN.items():
    v = F[(F.year >= y0) & (F.year <= y1)].reset_index(drop=True)
    cols = BASE + ["lrvS", "lrv5S"]; i = len(cols) - 1  # lrvS index in b = i (since const at 0 → index i)
    m_all = nw_ols(v.y, v[cols].to_numpy()); mp = nw_ols(v.ypre, v[cols + ["lpre"]].to_numpy()); mu = nw_ols(v.yus, v[cols + ["lus"]].to_numpy())
    vc = v[np.isfinite(v.lrvS1)].reset_index(drop=True)
    muc = nw_ols(vc.yus, vc[cols + ["lus", "lrvS1"]].to_numpy()); mac = nw_ols(vc.y, vc[cols + ["lrvS1"]].to_numpy())
    say(f"| {wn} | {m_all['n']} | {m_all['b'][i]:+.4f} ({m_all['b'][i]/m_all['se'][i]:+.2f}) | **{mp['b'][i]:+.4f} ({mp['b'][i]/mp['se'][i]:+.2f})** | **{mu['b'][i]:+.4f} ({mu['b'][i]/mu['se'][i]:+.2f})** | {muc['b'][i]:+.4f} ({muc['b'][i]/muc['se'][i]:+.2f})・β {muc['b'][-1]:+.3f} ({muc['b'][-1]/muc['se'][-1]:+.1f}) | {mac['b'][i]:+.4f} ({mac['b'][i]/mac['se'][i]:+.2f}) |")
# pre-US gold vol vs contemporaneous US500 *overnight* (18–08 ET) vol at d+1 (look-ahead・機構のみ・US500 夜間配信 2014+ ㉒)
ts, lc, r, flat, dt_ny = load_npz("US500")
hr = dt_ny.hour.to_numpy(); night = (hr >= 18) | (hr < 8)
sessS = (dt_ny + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]"); oN = sessS.astype("int64") + dt.date(1970, 1, 1).toordinal()
keep = night & ~flat; dfn = pd.DataFrame({"o": oN[keep], "r2": r[keep] ** 2}); gn = dfn.groupby("o", sort=True)
N = pd.DataFrame({"rv_n": gn["r2"].sum(), "nf_n": gn["r2"].size()}); N = N[N.nf_n >= 30]; N["lnightS"] = np.log(N.rv_n)
D3 = D.merge(N[["lnightS"]], left_on="o", right_index=True, how="left")
F3 = pd.DataFrame({"ypre": D3.lpre.to_numpy()[1:], "lpre": D3.lpre.to_numpy()[:-1], "lrv": D3.lrv.to_numpy()[:-1], "lrv5": D3.lrv5.to_numpy()[:-1], "lgvz": D3.lgvz.to_numpy()[:-1],
                   "lrvS": D3.lrvS.to_numpy()[:-1], "lrv5S": D3.lrv5S.to_numpy()[:-1], "lnightS1": D3.lnightS.to_numpy()[1:],
                   "evt0": D3.evt.to_numpy()[:-1].astype(float), "evt1": D3.evt.to_numpy()[1:].astype(float), "brk": (D3.gap.to_numpy()[1:] > 1).astype(float), "year": D3.year.to_numpy()[:-1]})
F3 = F3[np.isfinite(F3.to_numpy()).all(1) & (F3.year >= 2014)].reset_index(drop=True)
say("\n- pre-US 金 RV_(d+1) に **同時刻の US500 夜間 RV_(d+1)（18–08 ET・look-ahead・機構のみ・2014+）** を足す: γ_S^pre が残るか（残れば株自身の夜間ボラとの同時共変動では説明できない先行）")
for wn, (y0, y1) in {"在 2014-20": (2014, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}.items():
    v = F3[(F3.year >= y0) & (F3.year <= y1)].reset_index(drop=True); cols = BASE + ["lrvS", "lrv5S"]; i = len(cols) - 1
    m0 = nw_ols(v.ypre, v[cols + ["lpre"]].to_numpy()); m1 = nw_ols(v.ypre, v[cols + ["lpre", "lnightS1"]].to_numpy())
    say(f"  - {wn} n{m0['n']}: γ_S^pre 無統制 {m0['b'][i]:+.4f} (t {m0['b'][i]/m0['se'][i]:+.2f}) → US500 夜間 RV_(d+1) 統制 **{m1['b'][i]:+.4f} (t {m1['b'][i]/m1['se'][i]:+.2f})**・β_night {m1['b'][-1]:+.3f} (t {m1['b'][-1]/m1['se'][-1]:+.1f})・R² {m0['r2']:.3f}→{m1['r2']:.3f}")
# finer: pre-US split into Asia (18–02 ET) and London (02–08 ET) in-sample/out
say("\n- pre-US をさらに アジア 18–02 ET／ロンドン 02–08 ET に分けた γ_S（own 同窓 lag 統制・記述）:")
ts, lc, r, flat, dt_ny = load_npz("XAU")
hr = dt_ny.hour.to_numpy(); asia = (hr >= 18) | (hr < 2); lon = (hr >= 2) & (hr < 8)
keep = ~flat; dfa = pd.DataFrame({"o": o[keep], "r2": r[keep] ** 2, "a": asia[keep], "l": lon[keep]})
A = pd.DataFrame({"rv_a": dfa[dfa.a].groupby("o")["r2"].sum(), "nf_a": dfa[dfa.a].groupby("o")["r2"].size(), "rv_l": dfa[dfa.l].groupby("o")["r2"].sum(), "nf_l": dfa[dfa.l].groupby("o")["r2"].size()})
D2 = D.merge(A, left_on="o", right_index=True, how="left")
D2["la"] = np.where(D2.nf_a >= 30, np.log(D2.rv_a), np.nan); D2["ll"] = np.where(D2.nf_l >= 30, np.log(D2.rv_l), np.nan)
F2 = pd.DataFrame({"ya": D2.la.to_numpy()[1:], "yl": D2.ll.to_numpy()[1:], "la": D2.la.to_numpy()[:-1], "ll": D2.ll.to_numpy()[:-1],
                   "lrv": D2.lrv.to_numpy()[:-1], "lrv5": D2.lrv5.to_numpy()[:-1], "lgvz": D2.lgvz.to_numpy()[:-1], "lrvS": D2.lrvS.to_numpy()[:-1], "lrv5S": D2.lrv5S.to_numpy()[:-1],
                   "evt0": D2.evt.to_numpy()[:-1].astype(float), "evt1": D2.evt.to_numpy()[1:].astype(float), "brk": (D2.gap.to_numpy()[1:] > 1).astype(float), "year": D2.year.to_numpy()[:-1]})
F2 = F2[np.isfinite(F2[["ya", "yl", "la", "ll", "lrv", "lrv5", "lgvz", "lrvS", "lrv5S"]].to_numpy()).all(1) & (F2.year >= 2012)].reset_index(drop=True)
for wn, (y0, y1) in WIN.items():
    v = F2[(F2.year >= y0) & (F2.year <= y1)].reset_index(drop=True); cols = BASE + ["lrvS", "lrv5S"]; i = len(cols) - 1
    ma = nw_ols(v.ya, v[cols + ["la"]].to_numpy()); ml = nw_ols(v.yl, v[cols + ["ll"]].to_numpy())
    say(f"  - {wn} n{ma['n']}: アジア 18–02 γ_S {ma['b'][i]:+.4f} (t {ma['b'][i]/ma['se'][i]:+.2f})・ロンドン 02–08 γ_S {ml['b'][i]:+.4f} (t {ml['b'][i]/ml['se'][i]:+.2f})")
say(f"\n所要 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
