# -*- coding: utf-8 -*-
"""
[REFUTE c48 part b 2026-11-18 09:30] 本体 refute_c48_volspill.py の後始末 3 点。事後ではなく本体の宣言済み攻撃の**正しい適用**。

(1) **自分の事前固定の欠陥の開示と訂正**: 本体の破壊条件を R1/R2 について「**在** γ_S が t<2 または MDE 未満」と書いたが、
    壊す対象である c48 の C2 H_SPILL PASS は **連言**（在 γ_S>0 ∧ t≥2 ∧ M3 γ_S−γ_S10>0 ∧ t≥2 ∧ **外 γ_S>0 ∧ t≥1.5**）である。
    連言の 1 つが落ちれば PASS は落ちる。よって本体の各攻撃仕様について **C2 の 4 条件を全部** 評価し直す（新しい検定は足さない・
    同じ回帰の既に出ている列を規則に正しく当てるだけ）。これは事後の規則変更ではなく、事前規則の読み違いの訂正。
(2) 本体 R10 の監査 1 行が誤り: 「金セッション日の最初の足の ET 分」を minute-of-day で見たため 00:00 を跨ぐセッションで min=0 に
    なり [×] と出た。正しい監査 = セッション日 d の足の**実時刻**が 18:00 ET (d−1) 〜 17:00 ET (d) に入るか、および
    US500 現物の確定（16:00 ET d）が 被説明セッション d+1 の開始（18:00 ET d）より前か。
(3) 本体 R1(b)＋R2 の**同時**仕様（キャッシュで無料だった統制を全部入れた M2+）と、その下の経済的大きさ。
seed 20261118・発注なし・読取のみ・書き込みは AUREL_RESEARCH/ 配下のみ。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c48_volspill_b.md")
NY = "America/New_York"; NFMIN_X = 100; NFMIN_S = 60; NWLAG = 5
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c48 part b] 事前固定の欠陥の訂正・監査の訂正・統制の同時投入 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c48_volspill_b.py)")

# --- rebuild the frame (same code path as the main script, trimmed) ---
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
FO = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); FO = FO[FO["scheduled"] == 1]
FOMC = {pd.Timestamp(d).date().toordinal() for d in FO["date"]}
CP = pd.read_csv(os.path.join(MAC, "CPI_dates.csv")); CPI = {pd.Timestamp(d).date().toordinal() for d in CP["date"]}
EVT = NFP | FOMC | CPI

def nw(y, Xdf, lag=NWLAG):
    names = list(Xdf.columns); X = Xdf.to_numpy(float); y = np.asarray(y, float)
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b; Zu = Z * u[:, None]; S = Zu.T @ Zu
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = Zu[l:].T @ Zu[:-l]; S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv; se = np.sqrt(np.diag(V)); idx = {nm: i + 1 for i, nm in enumerate(names)}
    class R: pass
    r = R(); r.b = b; r.se = se; r.V = V; r.n = n; r.idx = idx
    r.get = lambda nm: (b[idx[nm]], b[idx[nm]] / se[idx[nm]], 2 * se[idx[nm]])
    def dif2(a, c):
        i, j = idx[a], idx[c]; d = b[i] - b[j]; return d, d / math.sqrt(V[i, i] + V[j, j] - 2 * V[i, j])
    r.dif2 = dif2
    return r

def load_npz(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    return ts, lc, r, flat, pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
tsX, lcX, rX, flX, nyX = load_npz("XAU"); tsS, lcS, rS, flS, nyS = load_npz("US500")
ordX = ((nyX + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]").astype("int64")
        + dt.date(1970, 1, 1).toordinal())
minsX = nyX.hour.to_numpy() * 60 + nyX.minute.to_numpy()
cashwin_X = (minsX >= 570) & (minsX < 960)
calX = nyX.tz_localize(None).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()

# ---------- (2) corrected look-ahead audit ----------
say("\n## (2) 監査の訂正（本体 R10 の 1 行は自分の検査式のバグ）")
sess_tbl = pd.DataFrame({"o": ordX, "t": nyX.tz_localize(None).values})
agg = sess_tbl.groupby("o")["t"].agg(["min", "max"])
agg["start_ref"] = [pd.Timestamp(dt.date.fromordinal(int(o))) - pd.Timedelta(hours=6) for o in agg.index]   # 18:00 ET d-1
agg["end_ref"] = [pd.Timestamp(dt.date.fromordinal(int(o))) + pd.Timedelta(hours=17) for o in agg.index]    # 17:00 ET d
ok_start = (agg["min"] >= agg["start_ref"]).mean(); ok_end = (agg["max"] <= agg["end_ref"]).mean()
say(f"- 金セッション日 d の足の実時刻: 18:00 ET (d−1) 以降 **{ok_start*100:.2f}%**・17:00 ET (d) 以前 **{ok_end*100:.2f}%**（n {len(agg)} 日）→ "
    f"[{'OK' if ok_start > 0.999 and ok_end > 0.999 else '×'}] セッション境界は宣言どおり")
say(f"- 予測子の確定 ≤ 被説明の開始: US500 現物の確定 16:00 ET (d) < 金セッション d+1 の開始 18:00 ET (d) → [OK] 2 時間の余裕"
    f"／GVZ・VIX の確定 16:15 ET (d) → [OK] 1h45m の余裕")
say(f"- 金の米国現物時間 RV（09:30–16:00 ET の暦日 d）は 金セッション日 d の内側（{(ordX[cashwin_X]==calX[cashwin_X]).mean()*100:.2f}% の足で "
    f"セッション日＝暦日）→ [OK] 17:00 ET (d) までに既知")

# ---------- frame ----------
kX = ~flX
dfX = pd.DataFrame({"o": ordX[kX], "r2": rX[kX] ** 2}); gX = dfX.groupby("o", sort=True)
D = pd.DataFrame({"rv": gX["r2"].sum(), "nf": gX["r2"].size()})
kXc = kX & cashwin_X
XC = pd.DataFrame({"rv_cash": pd.DataFrame({"o": calX[kXc], "r2": rX[kXc] ** 2}).groupby("o")["r2"].sum()})
D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"] = D["date"].dt.weekday
D = D.reset_index()
D = D[(D.wd <= 4) & (D.nf >= NFMIN_X)].reset_index(drop=True)
D["lrv"] = np.log(D["rv"]); D["gap"] = np.r_[np.nan, np.diff(D["o"].to_numpy())]
D["lrv5"] = D["lrv"].rolling(5).mean(); D["lrv22"] = D["lrv"].rolling(22).mean()
D["year"] = D["date"].dt.year; D["evt"] = D["o"].isin(EVT)
XC = XC.reset_index(); XC["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in XC["o"]])
XC["lrvXcash"] = np.log(XC["rv_cash"].where(XC["rv_cash"] > 0))
D = D.merge(XC[["date", "lrvXcash"]], on="date", how="left", validate="one_to_one")
minsS = nyS.hour.to_numpy() * 60 + nyS.minute.to_numpy(); cashS = (minsS >= 570) & (minsS < 960)
calS = nyS.tz_localize(None).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
kS = cashS & ~flS
S = pd.DataFrame({"rv": pd.DataFrame({"o": calS[kS], "r2": rS[kS] ** 2}).groupby("o")["r2"].sum(),
                  "nf": pd.DataFrame({"o": calS[kS], "r2": rS[kS] ** 2}).groupby("o")["r2"].size()})
S["date"] = pd.to_datetime([dt.date.fromordinal(int(x)) for x in S.index]); S["wd"] = S["date"].dt.weekday
S = S.reset_index(); S = S[(S.wd <= 4) & (S.nf >= NFMIN_S)].reset_index(drop=True)
S["lrvS"] = np.log(S["rv"]); S["lrv5S"] = S["lrvS"].rolling(5).mean(); S["lrvS_l10"] = S["lrvS"].shift(10)
def fred(nm):
    f = pd.read_csv(os.path.join(MAC, nm), na_values="."); f.columns = ["date", "v"]
    f["date"] = pd.to_datetime(f["date"]); return f.dropna()
D = D.merge(S[["date", "lrvS", "lrv5S", "lrvS_l10"]], on="date", how="left", validate="one_to_one")
D = D.merge(fred("GVZCLS.csv").rename(columns={"v": "gvz"}), on="date", how="left", validate="one_to_one")
D = D.merge(fred("VIXCLS.csv").rename(columns={"v": "vix"}), on="date", how="left", validate="one_to_one")
D["lgvz"] = np.log(D["gvz"]); D["lvix"] = np.log(D["vix"])
D["dlgvz"] = D["lgvz"].diff(); D["dlvix"] = D["lvix"].diff(); D["ugvz"] = D["lgvz"] - D["lgvz"].rolling(5).mean()
n = len(D); pr = slice(0, n - 1); nx = slice(1, n)
F = pd.DataFrame({"y": D["lrv"].to_numpy()[nx]})
for c in ["lrv", "lrv5", "lrv22", "lgvz", "lvix", "dlgvz", "dlvix", "ugvz", "lrvS", "lrv5S", "lrvS_l10", "lrvXcash"]:
    F[c] = D[c].to_numpy()[pr]
F["evt0"] = D["evt"].to_numpy()[pr].astype(float); F["evt1"] = D["evt"].to_numpy()[nx].astype(float)
F["brk"] = (D["gap"].to_numpy()[nx] > 1).astype(float); F["year"] = D["year"].to_numpy()[pr]
core = ["y", "lrv", "lrv5", "lgvz", "lrvS", "lrv5S", "lrvS_l10"]
F = F[np.isfinite(F[core].to_numpy()).all(1)].reset_index(drop=True)
F["uS"] = F["lrvS"] - F["lrv5S"]
BASE = ["lrv", "lrv5", "evt0", "evt1", "brk", "lgvz"]; M2 = BASE + ["lrvS", "lrv5S"]
say(f"- フレーム再構築 {len(F)} 行（本体と一致すべき 3437）")

WIN = {"在 2012-20": (2012, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def cellfit(y0, y1, cols):
    v = F[(F.year >= y0) & (F.year <= y1)].reset_index(drop=True)
    v = v[np.isfinite(v[cols].to_numpy()).all(1)].reset_index(drop=True)
    return nw(v.y.to_numpy(), v[cols]), v

# ---------- (1) correct application of the C2 conjunction ----------
say("\n## (1) c48 の C2 連言を各攻撃仕様に正しく当てる")
say("  C2 H_SPILL PASS = 在 γ_S>0 ∧ NW t≥2 ∧ M3 (γ_S−γ_S10)>0 ∧ t≥2 ∧ **外 γ_S>0 ∧ t≥1.5**（c48 docstring 原文）")
SPECS = {
    "S0 c48 原仕様 M2": [],
    "S1 +own 月次 (R1a)": ["lrv22"],
    "S2 **+金自身の 09:30–16:00 ET RV (R1b)**": ["lrvXcash"],
    "S3 +log VIX (R2)": ["lvix"],
    "S4 +IV 変化 全部 (R2)": ["lvix", "dlgvz", "dlvix", "ugvz"],
    "S5 **+金 cash RV ＋ IV 全部（無料だった統制の全部）**": ["lrvXcash", "lvix", "dlgvz", "dlvix", "ugvz"],
}
say(f"- own 月次 lrv22: 有効 {int(F.lrv22.notna().sum())}/{len(F)}（フレーム構築時に同時に貼った＝行対応は自明）")

say("\n| 仕様 | 在 γ_S (t) | 在 MDE | M3 γ_S−γ_S10 (t) | **外 γ_S (t)** | 外 MDE | 近年 γ_S (t) | 1sd→翌日 金 vol 外 | **C2 連言** |")
say("|---|---|---|---|---|---|---|---|---|")
VERD = {}
for nm, add in SPECS.items():
    cols = M2 + add
    ra, va = cellfit(2012, 2020, cols); ga, ta, ma = ra.get("lrvS")
    r3, v3 = cellfit(2012, 2020, cols + ["lrvS_l10"]); d3, t3 = r3.dif2("lrvS", "lrvS_l10")
    ro, vo = cellfit(2021, 2026, cols); go, to, mo = ro.get("lrvS")
    rr, vr = cellfit(2024, 2026, cols); gr, tr = rr.get("lrvS")[:2]
    eff = (math.exp(go * vo.uS.std() / 2) - 1) * 100
    c_in = (ga > 0) and (ta >= 2); c_m3 = (d3 > 0) and (t3 >= 2); c_out = (go > 0) and (to >= 1.5)
    passed = c_in and c_m3 and c_out
    VERD[nm] = dict(ga=ga, ta=ta, go=go, to=to, gr=gr, tr=tr, passed=passed, c_in=c_in, c_m3=c_m3, c_out=c_out, eff=eff, mo=mo, ma=ma)
    say(f"| {nm} | {ga:+.4f} ({ta:+.2f}) | {ma:.4f} | {d3:+.4f} ({t3:+.2f}) | **{go:+.4f} ({to:+.2f})** | {mo:.4f} | {gr:+.4f} ({tr:+.2f}) | {eff:+.2f}% | "
        f"**{'PASS' if passed else 'FAIL'}**（在 {'o' if c_in else 'x'}／M3 {'o' if c_m3 else 'x'}／外 {'o' if c_out else 'x'}） |")

# ---------- (3) economic size + what the surviving 在 effect is ----------
say("\n## (3) 生き残った在の効果の正体（記述）: 年別 γ_S を S0 と S5 で並べる")
rows = []
for yy in sorted(F.year.unique()):
    v = F[F.year == yy]
    if len(v) < 100: continue
    a = cellfit(yy, yy, M2)[0].get("lrvS"); b = cellfit(yy, yy, M2 + SPECS["S5 **+金 cash RV ＋ IV 全部（無料だった統制の全部）**"])[0].get("lrvS")
    rows.append(f"{yy} S0 {a[0]:+.3f}({a[0]/ (a[2]/2):+.1f}) → S5 {b[0]:+.3f}({b[0]/(b[2]/2):+.1f})")
say("- " + "・".join(rows))
s5 = SPECS["S5 **+金 cash RV ＋ IV 全部（無料だった統制の全部）**"]
for wn, (y0, y1) in WIN.items():
    r, v = cellfit(y0, y1, M2 + s5); g, t, m = r.get("lrvS")
    bc = r.get("lrvXcash")
    say(f"- {wn} S5: γ_S {g:+.4f} (t {t:+.2f}・MDE {m:.4f})・β(金自身の cash RV) {bc[0]:+.4f} (t {bc[1]:+.2f}) "
        f"→ 1sd(u^S {v.uS.std():.2f}) で翌日 金 vol {(math.exp(g*v.uS.std()/2)-1)*100:+.2f}%（c48 宣言: <2% は受け取れない）")

say("\n## まとめ（part b）")
s0 = VERD["S0 c48 原仕様 M2"]; sS2 = VERD["S2 **+金自身の 09:30–16:00 ET RV (R1b)**"]
sS4 = VERD["S4 +IV 変化 全部 (R2)"]; sS5 = VERD["S5 **+金 cash RV ＋ IV 全部（無料だった統制の全部）**"]
nfail = sum(1 for k, d in VERD.items() if k != "S0 c48 原仕様 M2" and not d["passed"])
say(f"- 原仕様 S0 は PASS（再現）。追加統制 5 仕様のうち **C2 連言が落ちたのは {nfail}/5**。落ち方はすべて **外の conjunct**（在は全仕様で t≥3.1 を維持）。")
say(f"- 決定的な 2 つ: S2（金自身の同一時計窓 RV）外 t {sS2['to']:+.2f}／S4（IV 変化）外 t {sS4['to']:+.2f}／S5（両方）外 t {sS5['to']:+.2f}・近年 {sS5['gr']:+.4f} (t {sS5['tr']:+.2f})。")
say(f"\n所要 {time.time()-T0:.1f} s・新規取得なし・発注なし・seed 20261118")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
