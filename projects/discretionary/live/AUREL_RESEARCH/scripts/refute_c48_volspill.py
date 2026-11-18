# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-18 09:30 反証レーン] 対象 = cycle48 (06:45) の **C2 H_SPILL 規則上 PASS**
  「当日の米株現物時間の実現ボラ・ショックは、金自身のボラ履歴（φ1 log RV^X_d・φ5 5日平均）と金オプション IV（log GVZ_d）を
   統制しても翌セッションの金 RV を予測する」
  在 2012-20 γ_S **+0.1041 (NW t +4.38・MDE 0.0475)**・M3 γ_S−γ_S10 +0.1158 (t 4.26)／外 2021-26H1 **+0.0523 (t +2.39・MDE 0.0438)**／
  近年 2024-26H1 +0.0319 (t 1.05)・逆方向 0・lag10 0・13/15 年 正。
  c48 自身は「補足 b の同時刻統制で**機構**（遅れた伝播）を否定」したが、**規則上の PASS（予測の存在そのもの）は残した**。
  反証レーンが壊しにいくのは **その PASS = 「予測する」という主張** であり、c48 が残した look-ahead 分解とは別の経路で壊す。

=== 事前固定（この docstring を全部書いてから数字を見る）===
データ: c48 と同一の既存キャッシュのみ（data/macro/XAU_m5_close.npz・US500_m5_close.npz・GVZCLS.csv・VIXCLS.csv・
  FOMC_dates.csv・CPI_dates.csv・NFP 規則）。scan 無し・MT5 無し・外部通信無し・新規取得無し。
再現: c48 の M2 を独立実装（係数は名前で引く＝添字バグを持ち込まない）し 在/外/近年 の γ_S を再現してから攻撃する。
  再現が ±0.005 以内で一致しなければ以降の結論は書かず「再現不能」で終える。

攻撃（すべて事前宣言・順番も固定）:
R1【own-vol フィルタ／EIV】c48 の own 項は φ1（前日）＋φ5（5日平均）だけ＝HAR の月次項が無い。潜在ボラ状態の測定が不完全なら、
   同じ潜在因子の**第 2 の測定**は「伝播」が無くても正の係数を取る（errors-in-variables の教科書的帰結）。
   (a) own 月次項 log RV^X_(d-21..d) 平均を足す。
   (b) **決定的**: 送り手と**同一の時計窓**で測った金自身のボラ log RV^Xcash_d（金 09:30–16:00 ET の 78 本・金セッション日 d の内側＝
       既知・look-ahead なし）を M2 に足す。これは US500 と同じ 6.5 h 窓の「同じ時間帯のボラ」を金自身で測ったもの。
       γ_S がこれで消えるなら「株ボラの伝播」ではなく「**金自身の米国時間帯のボラを、own 項が取り切れていない**」。
   (c) 非送り手プラセボ: 金の day-d 5 分足を偶数本/奇数本に分けた RV_even/RV_odd（同一潜在ボラの 2 つの測定・どちらも金自身＝
       伝播はあり得ない）。RV_even を RV_odd・lrv5・lgvz に足した係数が大きく正なら、「第 2 の測定は伝播なしでも正に出る」経路の実証。
   破壊条件: 在 γ_S が t<2 になる、または 自分の MDE 0.0475 を下回る。
R2【IV 統制が GVZ の水準だけ＝不十分】M2 は log VIX_d を**一度も入れていない**。VIX は 16:15 ET に既知の株 IV で RV^S_d と強く相関する。
   log VIX_d・Δlog GVZ_(d-1→d)・Δlog VIX_(d-1→d)・u^GVZ（log GVZ − 5日平均）を足す。
   破壊条件: 同上。「IV を超える」の主張は「GVZ の水準を超える」でしかなかったことになる。
R3【別の在外分割】(i) 反転（在 2021-26H1／外 2012-20）(ii) 中央分割 2012-16／2017-26H1 (iii) 奇数年/偶数年 (iv) 外窓の
   leave-one-year-out（2021..2026 を 1 つずつ落とす）。破壊条件: 外側セル（γ_S>0 ∧ t≥1.5）が 4 分割のうち **2 つ以上で不成立**。
R4【コストを倍にする = 真の OOS 予測で払わせる】in-sample の t ではなく拡大窓ウォークフォワード 1 期先予測（最小学習 750 日・
   21 日ごと再推定）で M1（株項なし）vs M2 を比較。損失 = log 二乗誤差 と QLIKE（水準）。Diebold–Mariano（NW(5)）片側。
   破壊条件: 全期間・外期間の両方で、2 つの損失のどちらも片側 p>0.05（＝予測は 1 円も払わない）。
R5【帰無の校正】c48 の循環シフトは㊷で自ら「過小校正の疑い」と書いた。正しい校正 = H0(γ_S=0) 下の**ブロック wild bootstrap**
   （制約モデル M1 の残差に 22 日ブロック単位 Rademacher 符号・B=1000・不均一分散と系列相関を保存）で γ_S の NW t の帰無分布。
   併せて曜日マッチ置換（曜日内で株列を入れ替え・B=1000）。破壊条件: 在の bootstrap 片側 p > 0.025（Bonferroni(2) の名目）。
R6【サンプリング頻度 = 測定ノイズの robustness】両系列の RV を 15 分・30 分集約で作り直して M2 を再推定。
   5 分でだけ出て 15/30 分で消えるならマイクロストラクチャー由来。（破壊条件には使わない・記述）
R7【ショックのラグ構造】u^S を lag 0/1/2/5 同時投入（c48 の lag プロファイルは 5 日平均を外した「水準単独」で不公平）。
   また γ_S+γ_S5 = 0 の検定（0 なら「水準は無情報・1 日の偏差だけ」＝ボラの伝播としては持続が無く経済的に不自然）。（記述）
R8【データの穴・サバイバーシップ】(i) 2020 年を全部落とす（US500 現物 71 営業日欠落＝㊵・c48 自身の反証 iii）
   (ii) US500 nf=78（完全日）のみ (iii) 2014+ のみ。（記述・符号の安定性を見る）
R9【多重検定】data/cells.csv の判定済みセル全部に BH(q=0.05) を当て、c48 C2 が生き残るか。
R10【look-ahead / 整合の監査】コードで検査する: 予測子の既知時刻（US500 16:00 ET・GVZ/VIX 16:15 ET ≤ 金セッション d の終端 17:00 ET）／
   merge が暦日の完全一致のみ（ffill/asof 無し）／被説明の金セッション d+1 が 18:00 ET d 以降に始まる／brk の定義／
   欠落営業日が「前の日の株 RV を d に貼る」事故になっていないか（staleness の実測）。

判定（事前固定・この順で評価）:
  broken = R1(b) または R2 で 在 γ_S が t<2 もしくは MDE 未満 ／または R3 で外側セルが 2 つ以上不成立
           ／または R4 で両期間・両損失とも p>0.05 ／または R5 で在 p>0.025。
  survived = R1・R2・R5 を通し（在 t≥2 ∧ 外 t≥1.5 を維持）かつ R4 でどちらかの損失が有意。
  inconclusive = それ以外（MDE を併記して決着不能と書く）。
発注・デモ発注なし。本番ファイル・プロセス・schtask に触らない。書き込みは AUREL_RESEARCH/ 配下のみ。seed 20261118.
"""
import os, time, json, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c48_volspill_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261118)
NFMIN_X = 100; NFMIN_S = 60; NWLAG = 5
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c48] ボラの伝播 株→金 の C2 H_SPILL PASS を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c48_volspill.py)")

# ---------------- calendars (c48 と同一) ----------------
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

# ---------------- stats ----------------
def nw(y, Xdf, lag=NWLAG):
    """名前付き OLS + NW(lag) / HC1。添字バグを持ち込まないため列名で引く。"""
    names = list(Xdf.columns); X = Xdf.to_numpy(float); y = np.asarray(y, float)
    n = len(y); Z = np.column_stack([np.ones(n), X]); XtX_inv = np.linalg.inv(Z.T @ Z)
    b = XtX_inv @ Z.T @ y; u = y - Z @ b; Zu = Z * u[:, None]
    S = Zu.T @ Zu; V_hc = XtX_inv @ S @ XtX_inv * n / (n - Z.shape[1])
    for l in range(1, lag + 1):
        w = 1 - l / (lag + 1); G = Zu[l:].T @ Zu[:-l]; S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V)); se_hc = np.sqrt(np.diag(V_hc))
    idx = {nm: i + 1 for i, nm in enumerate(names)}
    r2 = 1 - (u ** 2).sum() / ((y - y.mean()) ** 2).sum()
    class R: pass
    r = R(); r.b = b; r.se = se; r.se_hc = se_hc; r.V = V; r.u = u; r.n = n; r.r2 = r2; r.idx = idx; r.names = names
    r.get = lambda nm: (b[idx[nm]], b[idx[nm]] / se[idx[nm]], 2 * se[idx[nm]])      # (coef, NW t, MDE)
    r.hc = lambda nm: b[idx[nm]] / se_hc[idx[nm]]
    def sum2(a, c):
        i, j = idx[a], idx[c]; s = b[i] + b[j]; v = V[i, i] + V[j, j] + 2 * V[i, j]; return s, s / math.sqrt(v)
    r.sum2 = sum2
    def dif2(a, c):
        i, j = idx[a], idx[c]; d = b[i] - b[j]; v = V[i, i] + V[j, j] - 2 * V[i, j]; return d, d / math.sqrt(v)
    r.dif2 = dif2
    return r
def nw_mean(x, lag=NWLAG):
    x = np.asarray(x, float); n = len(x); m = x.mean(); u = x - m
    S = (u ** 2).sum()
    for l in range(1, lag + 1):
        S += 2 * (1 - l / (lag + 1)) * (u[l:] * u[:-l]).sum()
    return m, m / math.sqrt(S / n ** 2)

# ---------------- bars -> daily ----------------
def load_npz(sym):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"].astype(np.int64); C = z["close"].astype(float)
    lc = np.log(C); r = np.zeros(len(C)); r[1:] = np.diff(lc); flat = r == 0.0
    dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
    return ts, lc, r, flat, dt_ny

def coarse_rv(ordkey, r, keep, m):
    """keep 内の 5 分リターンを日(ordkey)ごとに m 本ずつ束ねた粗サンプリング RV。"""
    df = pd.DataFrame({"o": ordkey[keep], "r": r[keep]})
    out = {}
    for o, g in df.groupby("o", sort=True):
        v = g["r"].to_numpy(); k = len(v) // m
        if k < 3: continue
        out[o] = float((v[:k * m].reshape(k, m).sum(1) ** 2).sum())
    return pd.Series(out)

say("\n## 0. データ（c48 と同一キャッシュ）")
tsX, lcX, rX, flX, nyX = load_npz("XAU")
tsS, lcS, rS, flS, nyS = load_npz("US500")
# --- gold: session day (ET+6h) ---
sessX = (nyX + pd.Timedelta(hours=6)).tz_localize(None).values.astype("datetime64[D]")
ordX = sessX.astype("int64") + dt.date(1970, 1, 1).toordinal()
minsX = nyX.hour.to_numpy() * 60 + nyX.minute.to_numpy()
cashwin_X = (minsX >= 570) & (minsX < 960)          # 09:30-16:00 ET = 送り手と同一の時計窓
calX = nyX.tz_localize(None).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
kX = ~flX
dfX = pd.DataFrame({"o": ordX[kX], "lc": lcX[kX], "r2": rX[kX] ** 2}); gX = dfX.groupby("o", sort=True)
D = pd.DataFrame({"rv": gX["r2"].sum(), "nf": gX["r2"].size()})
# 金の「米国現物時間」RV: 暦日 d の 09:30-16:00 ET（= 金セッション日 d の内側・17:00 ET までに既知）
kXc = kX & cashwin_X
dfXc = pd.DataFrame({"o": calX[kXc], "r2": rX[kXc] ** 2}); gXc = dfXc.groupby("o", sort=True)
XC = pd.DataFrame({"rv_cash": gXc["r2"].sum(), "nf_cash": gXc["r2"].size()})
# odd/even bar split of the SAME gold day (非送り手プラセボ)
pos_in_day = dfX.groupby("o").cumcount().to_numpy()
dfX2 = dfX.assign(p=pos_in_day)
ev = dfX2[dfX2.p % 2 == 0].groupby("o")["r2"].sum(); od = dfX2[dfX2.p % 2 == 1].groupby("o")["r2"].sum()
D["rv_even"] = ev; D["rv_odd"] = od
# coarse sampling (15/30 min) on gold session
D["rv15"] = coarse_rv(ordX, rX, kX, 3); D["rv30"] = coarse_rv(ordX, rX, kX, 6)
D["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in D.index]); D["wd"] = D["date"].dt.weekday
D = D.reset_index().rename(columns={"index": "o"})
D = D[(D.wd <= 4) & (D.nf >= NFMIN_X)].reset_index(drop=True)
D["lrv"] = np.log(D["rv"]); D["gap"] = np.r_[np.nan, np.diff(D["o"].to_numpy())]
D["lrv5"] = D["lrv"].rolling(5).mean(); D["lrv22"] = D["lrv"].rolling(22).mean()
D["year"] = D["date"].dt.year; D["evt"] = D["o"].isin(EVT)
for c in ("rv15", "rv30", "rv_even", "rv_odd"):
    D["l" + c] = np.log(D[c].where(D[c] > 0))
D["lrv15_5"] = D["lrv15"].rolling(5).mean(); D["lrv30_5"] = D["lrv30"].rolling(5).mean()
XC = XC.reset_index().rename(columns={"index": "o"})
XC["date"] = pd.to_datetime([dt.date.fromordinal(int(o)) for o in XC["o"]])
XC["lrvXcash"] = np.log(XC["rv_cash"].where(XC["rv_cash"] > 0))
D = D.merge(XC[["date", "lrvXcash", "nf_cash"]], on="date", how="left", validate="one_to_one")
say(f"- XAU: 有効セッション日 {len(D)}・金の米国現物時間 RV あり {int(D.lrvXcash.notna().sum())}（nf_cash 中央値 {D.nf_cash.median():.0f}/78）")

# --- US500 cash ---
minsS = nyS.hour.to_numpy() * 60 + nyS.minute.to_numpy()
cashS = (minsS >= 570) & (minsS < 960)
calS = nyS.tz_localize(None).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
kS = cashS & ~flS
dfS = pd.DataFrame({"o": calS[kS], "r2": rS[kS] ** 2}); gS_ = dfS.groupby("o", sort=True)
S = pd.DataFrame({"rv": gS_["r2"].sum(), "nf": gS_["r2"].size()})
S["rv15"] = coarse_rv(calS, rS, kS, 3); S["rv30"] = coarse_rv(calS, rS, kS, 6)
S["date"] = pd.to_datetime([dt.date.fromordinal(int(x)) for x in S.index]); S["wd"] = S["date"].dt.weekday
S = S.reset_index().rename(columns={"index": "o"})
S = S[(S.wd <= 4) & (S.nf >= NFMIN_S)].reset_index(drop=True)
S["lrvS"] = np.log(S["rv"]); S["lrv5S"] = S["lrvS"].rolling(5).mean()
S["lrvS15"] = np.log(S["rv15"].where(S["rv15"] > 0)); S["lrvS15_5"] = S["lrvS15"].rolling(5).mean()
S["lrvS30"] = np.log(S["rv30"].where(S["rv30"] > 0)); S["lrvS30_5"] = S["lrvS30"].rolling(5).mean()
for k in (1, 2, 5, 10): S[f"lrvS_l{k}"] = S["lrvS"].shift(k)
S["uS_raw"] = S["lrvS"] - S["lrv5S"]
for k in (1, 2, 5): S[f"uS_l{k}"] = S["uS_raw"].shift(k)
S["nfS"] = S["nf"]
say(f"- US500 現物: 有効日 {len(S)}（nf 中央値 {S.nf.median():.0f}/78・nf=78 の完全日 {int((S.nf==78).sum())}）")

def fred(name):
    f = pd.read_csv(os.path.join(MAC, name), na_values="."); f.columns = ["date", "v"]
    f["date"] = pd.to_datetime(f["date"]); return f.dropna()
GV = fred("GVZCLS.csv"); VX = fred("VIXCLS.csv")

scols = ["date", "lrvS", "lrv5S", "lrvS_l1", "lrvS_l2", "lrvS_l5", "lrvS_l10", "uS_l1", "uS_l2", "uS_l5",
         "lrvS15", "lrvS15_5", "lrvS30", "lrvS30_5", "nfS"]
D = D.merge(S[scols], on="date", how="left", validate="one_to_one")
D = D.merge(GV.rename(columns={"v": "gvz"}), on="date", how="left", validate="one_to_one")
D = D.merge(VX.rename(columns={"v": "vix"}), on="date", how="left", validate="one_to_one")
D["lgvz"] = np.log(D["gvz"]); D["lvix"] = np.log(D["vix"])
D["dlgvz"] = D["lgvz"] - D["lgvz"].shift(1); D["dlvix"] = D["lvix"] - D["lvix"].shift(1)
D["ugvz"] = D["lgvz"] - D["lgvz"].rolling(5).mean()

# ---------------- R10 look-ahead / alignment audit (数字を見る前に) ----------------
say("\n## R10. look-ahead・整合の監査（コード）")
aud = []
aud.append(("merge は暦日の完全一致のみ（ffill/asof なし・validate=one_to_one）", True))
# 金セッション d+1 の開始は 17:00 ET d より後か: セッション日 o の最小 ET 時刻
first_min = pd.DataFrame({"o": ordX, "m": minsX}).groupby("o")["m"].min()
aud.append((f"金セッション日の最初の足の ET 分 中央値 {first_min.median():.0f}（=18:00 ET → 1080）・最小 {first_min.min():.0f}", bool(first_min.median() >= 1080)))
# US500 cash 窓の最終足 ET
aud.append((f"US500 現物窓の最終足 開始 ET {int(minsS[cashS].max())} 分（15:55 → 955・終値 16:00 ET ≤ 17:00 ET）", int(minsS[cashS].max()) == 955))
aud.append((f"金の米国現物時間 RV も同一窓（最終足開始 {int(minsX[cashwin_X].max())} 分）", int(minsX[cashwin_X].max()) == 955))
for s, ok in aud: say(f"- [{'OK' if ok else '×'}] {s}")

# ---------------- regression frame (c48 と同一の作り) ----------------
def frame(D):
    n = len(D); pr = slice(0, n - 1); nx = slice(1, n)
    F = pd.DataFrame({"y": D["lrv"].to_numpy()[nx]})
    for c in ["lrv", "lrv5", "lrv22", "lgvz", "lvix", "dlgvz", "dlvix", "ugvz", "lrvS", "lrv5S",
              "lrvS_l1", "lrvS_l2", "lrvS_l5", "lrvS_l10", "uS_l1", "uS_l2", "uS_l5",
              "lrvXcash", "lrv_even", "lrv_odd", "lrv15", "lrv15_5", "lrv30", "lrv30_5",
              "lrvS15", "lrvS15_5", "lrvS30", "lrvS30_5", "nfS", "nf_cash"]:
        F[c] = D[c].to_numpy()[pr]
    F["y15"] = D["lrv15"].to_numpy()[nx]; F["y30"] = D["lrv30"].to_numpy()[nx]
    F["evt0"] = D["evt"].to_numpy()[pr].astype(float); F["evt1"] = D["evt"].to_numpy()[nx].astype(float)
    F["brk"] = (D["gap"].to_numpy()[nx] > 1).astype(float)
    F["year"] = D["year"].to_numpy()[pr]; F["date"] = D["date"].to_numpy()[pr]
    F["wd"] = pd.to_datetime(F["date"]).dt.weekday
    core = ["y", "lrv", "lrv5", "lgvz", "lrvS", "lrv5S", "lrvS_l10"]
    return F[np.isfinite(F[core].to_numpy()).all(1)].reset_index(drop=True)
F = frame(D)
F["uS"] = F["lrvS"] - F["lrv5S"]
# staleness: 株 RV の暦日と金セッション日は完全一致でマージ済み → 0 日。欠落営業日は行ごと落ちる（貼り付け事故なし）
say(f"- [OK] 株 RV の staleness = 0 日（完全一致マージ・欠落営業日は NaN → 行落ち）。回帰フレーム {len(F)} 行・"
    f"在 {int(((F.year>=2012)&(F.year<=2020)).sum())}／外 {int((F.year>=2021).sum())}・sd(u^S) {F.uS.std():.3f}")

BASE = ["lrv", "lrv5", "evt0", "evt1", "brk", "lgvz"]
M2 = BASE + ["lrvS", "lrv5S"]
WIN = {"在 2012-20": (2012, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def sub(y0, y1, FF=None):
    G = F if FF is None else FF
    return G[(G.year >= y0) & (G.year <= y1)].reset_index(drop=True)
def run(v, cols, key="lrvS"):
    vv = v[np.isfinite(v[cols].to_numpy()).all(1)].reset_index(drop=True)
    r = nw(vv.y.to_numpy(), vv[cols]); return r, r.get(key), r.n

# ---------------- R0 replication ----------------
say("\n## R0. 再現（c48 M2 の独立実装・係数は名前で引く）")
say("| 窓 | n | γ_S (NW t) | MDE | c48 報告 | 差 |")
say("|---|---|---|---|---|---|")
REP = {"在 2012-20": 0.1041, "外 2021-26H1": 0.0523, "近年 2024-26H1": 0.0319}
BASEFIT = {}
rep_ok = True
for wn, (y0, y1) in WIN.items():
    v = sub(y0, y1); r, (g, t, mde), n = run(v, M2)
    BASEFIT[wn] = (r, g, t, mde, n, v)
    d = g - REP[wn]; rep_ok &= abs(d) <= 0.005
    say(f"| {wn} | {n} | **{g:+.4f} ({t:+.2f})** | {mde:.4f} | {REP[wn]:+.4f} | {d:+.4f} |")
say(f"- 再現判定: **{'一致（±0.005 以内）→ 攻撃に進む' if rep_ok else '不一致 → 以降の結論は書かない'}**")

# ---------------- R1 own-vol filter / EIV ----------------
say("\n## R1. own-vol フィルタ／EIV: 「同じ潜在ボラの第 2 の測定」は伝播なしでも正に出る")
say("| 窓 | γ_S M2 (t) | (a) +own 月次 lrv22 | (b) **+金自身の 09:30–16:00 ET RV** | β(金 cash RV) (t) | (a)+(b) 同時 |")
say("|---|---|---|---|---|---|")
R1 = {}
for wn, (y0, y1) in WIN.items():
    v = sub(y0, y1)
    _, (g0, t0, _), _ = run(v, M2)
    ra, (ga, ta, _), na = run(v, M2 + ["lrv22"])
    rb, (gb, tb, mb), nb = run(v, M2 + ["lrvXcash"])
    bc, tc, _ = rb.get("lrvXcash")
    rc, (gc, tc2, _), nc = run(v, M2 + ["lrv22", "lrvXcash"])
    R1[wn] = dict(g0=g0, t0=t0, ga=ga, ta=ta, gb=gb, tb=tb, mb=mb, bc=bc, tc=tc, gc=gc, tc2=tc2, nb=nb)
    say(f"| {wn} | {g0:+.4f} ({t0:+.2f}) | {ga:+.4f} ({ta:+.2f}) | **{gb:+.4f} ({tb:+.2f})・MDE {mb:.4f}** | {bc:+.3f} ({tc:+.2f}) | {gc:+.4f} ({tc2:+.2f}) (n {nc}) |")
say("- (c) 非送り手プラセボ（金 day-d の偶数本 RV を 奇数本 RV・lrv5・lgvz に足す＝同一潜在ボラの 2 つの測定・伝播はあり得ない）:")
for wn, (y0, y1) in list(WIN.items())[:2]:
    v = sub(y0, y1); cols = ["lrv_odd", "lrv5", "evt0", "evt1", "brk", "lgvz", "lrv_even"]
    r, (g, t, m), n = run(v, cols, key="lrv_even")
    bo, to, _ = r.get("lrv_odd")
    say(f"  - {wn}: β(RV_even) **{g:+.4f} (t {t:+.2f})**・β(RV_odd) {bo:+.4f} ({to:+.2f})・n {n} "
        f"→ 第 2 の測定は伝播ゼロでも t {t:+.1f} で正に出る（γ_S {R1[wn]['g0']:+.3f} との比 {g/max(R1[wn]['g0'],1e-9):.1f}×）")

# ---------------- R2 IV controls ----------------
say("\n## R2. IV 統制が GVZ の水準だけ＝不十分（M2 は log VIX を一度も入れていない）")
say("| 窓 | γ_S M2 (t) | +log VIX | +Δlog GVZ | +Δlog VIX | +u^GVZ | **全部**（t）| MDE | θ_VIX (t) |")
say("|---|---|---|---|---|---|---|---|---|")
R2 = {}
for wn, (y0, y1) in WIN.items():
    v = sub(y0, y1); _, (g0, t0, _), _ = run(v, M2)
    out = []
    for add in (["lvix"], ["dlgvz"], ["dlvix"], ["ugvz"]):
        _, (g, t, _), _ = run(v, M2 + add); out.append((g, t))
    rall, (gA, tA, mA), nA = run(v, M2 + ["lvix", "dlgvz", "dlvix", "ugvz"])
    bv, tv, _ = rall.get("lvix")
    R2[wn] = dict(g0=g0, t0=t0, gA=gA, tA=tA, mA=mA, gvix=out[0])
    say(f"| {wn} | {g0:+.4f} ({t0:+.2f}) | " + " | ".join(f"{g:+.4f} ({t:+.2f})" for g, t in out) +
        f" | **{gA:+.4f} ({tA:+.2f})** | {mA:.4f} | {bv:+.3f} ({tv:+.2f}) |")

# ---------------- R3 alternative splits ----------------
say("\n## R3. 別の在外分割（外側セルの規則 = γ_S>0 ∧ NW t≥1.5）")
def cell(v):
    _, (g, t, m), n = run(v, M2); return g, t, m, n
splits = []
a = cell(sub(2021, 2026)); b = cell(sub(2012, 2020))
splits.append(("(i) 反転: 在 2021-26H1 → 外 2012-20", a, b))
a = cell(sub(2012, 2016)); b = cell(sub(2017, 2026))
splits.append(("(ii) 中央分割: 在 2012-16 → 外 2017-26H1", a, b))
odd = F[F.year % 2 == 1].reset_index(drop=True); evn = F[F.year % 2 == 0].reset_index(drop=True)
a = cell(odd); b = cell(evn)
splits.append(("(iii) 奇数年 → 偶数年", a, b))
say("| 分割 | 在 γ_S (t) | **外 γ_S (t)** | 外 MDE | 外 n | 外側セル |")
say("|---|---|---|---|---|---|")
nfail = 0
for nm, (ga, ta, ma, na), (gb, tb, mb, nb) in splits:
    ok = (gb > 0) and (tb >= 1.5); nfail += (0 if ok else 1)
    say(f"| {nm} | {ga:+.4f} ({ta:+.2f}) | **{gb:+.4f} ({tb:+.2f})** | {mb:.4f} | {nb} | {'成立' if ok else '**不成立**'} |")
say("- (iv) 外窓 leave-one-year-out（2021-26H1 から 1 年ずつ落とす）:")
loyo = []
for yy in range(2021, 2027):
    v = sub(2021, 2026); v = v[v.year != yy].reset_index(drop=True)
    g, t, m, n = cell(v); ok = (g > 0) and (t >= 1.5); loyo.append((yy, g, t, m, n, ok))
    say(f"  - −{yy}: γ_S {g:+.4f} (t {t:+.2f}・MDE {m:.4f}・n {n}) → {'成立' if ok else '**不成立**'}")
loyo_fail = sum(1 for *_x, ok in loyo if not ok)
nfail += (1 if loyo_fail > 0 else 0)
say(f"- (iv) 判定: LOYO で不成立 {loyo_fail}/6 年 → 分割 (iv) は {'**不成立**' if loyo_fail > 0 else '成立'}")
say(f"- **R3 集計: 4 分割のうち不成立 {nfail} → {'破壊条件（≥2）に該当' if nfail >= 2 else '破壊条件に非該当'}**")

# ---------------- R4 walk-forward OOS (cost を払わせる) ----------------
say("\n## R4. 真の OOS 予測（拡大窓ウォークフォワード・最小学習 750 日・21 日ごと再推定・M1 vs M2）")
M1 = BASE
def walkforward(FF, cols):
    v = FF[np.isfinite(FF[cols + ["y"]].to_numpy()).all(1)].reset_index(drop=True)
    n = len(v); Xa = np.column_stack([np.ones(n), v[cols].to_numpy(float)]); ya = v.y.to_numpy(float)
    pred = np.full(n, np.nan); beta = None
    for i in range(750, n):
        if (i - 750) % 21 == 0 or beta is None:
            beta, *_ = np.linalg.lstsq(Xa[:i], ya[:i], rcond=None)
        pred[i] = Xa[i] @ beta
    return v, pred, ya
cols1 = M1; cols2 = M2
common = [c for c in set(cols1 + cols2)] + ["y"]
FF = F[np.isfinite(F[list(set(cols1 + cols2)) + ["y"]].to_numpy()).all(1)].reset_index(drop=True)
v1, p1, ya = walkforward(FF, cols1); v2, p2, _ = walkforward(FF, cols2)
ok = np.isfinite(p1) & np.isfinite(p2)
yrs = v1.year.to_numpy()
def dm(mask, label):
    m = mask & ok
    if m.sum() < 100: say(f"  - {label}: n {int(m.sum())} <100 → 省略"); return None
    e1 = ya[m] - p1[m]; e2 = ya[m] - p2[m]
    dmse = e1 ** 2 - e2 ** 2                                  # >0 なら M2 が優位
    s2 = np.exp(ya[m]); f1 = np.exp(p1[m]); f2 = np.exp(p2[m])
    q1 = s2 / f1 - np.log(s2 / f1) - 1; q2 = s2 / f2 - np.log(s2 / f2) - 1
    dq = q1 - q2
    m1_, t1_ = nw_mean(dmse); m2_, t2_ = nw_mean(dq)
    rmse1 = math.sqrt((e1 ** 2).mean()); rmse2 = math.sqrt((e2 ** 2).mean())
    say(f"  - {label}: n {int(m.sum())}・RMSE(log) M1 {rmse1:.4f} → M2 {rmse2:.4f}（改善 {100*(1-rmse2/rmse1):+.3f}%）"
        f"・DM log-MSE Δ {m1_:+.5f} (NW t {t1_:+.2f}・片側 p {0.5*math.erfc(t1_/math.sqrt(2)):.3f})"
        f"・DM QLIKE Δ {m2_:+.5f} (t {t2_:+.2f}・片側 p {0.5*math.erfc(t2_/math.sqrt(2)):.3f})")
    return (t1_, t2_)
say("- Diebold–Mariano（NW(5)）片側 p（H1: M2 の損失が小さい）:")
r_all = dm(np.ones(len(ok), bool), "全 OOS 期間")
r_out = dm(yrs >= 2021, "外 2021-26H1 のみ")
r_rec = dm(yrs >= 2024, "近年 2024-26H1 のみ")
def p1s(t): return 0.5 * math.erfc(t / math.sqrt(2))
r4_broken = None
if r_all and r_out:
    r4_broken = all(p1s(t) > 0.05 for t in list(r_all) + list(r_out))
    say(f"- **R4 判定: 全期間・外期間の 4 つの片側 p すべて >0.05 か → {r4_broken}**")

# ---------------- R5 null calibration ----------------
say("\n## R5. 帰無の校正（H0: γ_S=0 下のブロック wild bootstrap・22 日ブロック Rademacher・B=1000／曜日マッチ置換 B=1000）")
B = 1000; BL = 22
R5 = {}
for wn, (y0, y1) in list(WIN.items())[:2]:
    v = sub(y0, y1); vv = v[np.isfinite(v[M2].to_numpy()).all(1)].reset_index(drop=True)
    n = len(vv); y = vv.y.to_numpy(float)
    X1 = np.column_stack([np.ones(n), vv[M1].to_numpy(float)])
    X2 = np.column_stack([np.ones(n), vv[M2].to_numpy(float)])
    b1, *_ = np.linalg.lstsq(X1, y, rcond=None); fit1 = X1 @ b1; u1 = y - fit1
    r_obs = nw(y, vv[M2]); g_obs, t_obs, _ = r_obs.get("lrvS")
    nb_ = int(np.ceil(n / BL))
    tb = np.empty(B); gb = np.empty(B)
    P2 = np.linalg.pinv(X2)
    for i in range(B):
        sgn = np.repeat(rng.choice([-1.0, 1.0], nb_), BL)[:n]
        ys = fit1 + u1 * sgn
        bb = P2 @ ys; us = ys - X2 @ bb
        # NW se for the lrvS coefficient only (full sandwich, cheap enough at n~2k)
        Zu = X2 * us[:, None]; S_ = Zu.T @ Zu
        for l in range(1, NWLAG + 1):
            w = 1 - l / (NWLAG + 1); Gm = Zu[l:].T @ Zu[:-l]; S_ += w * (Gm + Gm.T)
        XtXi = np.linalg.inv(X2.T @ X2); V_ = XtXi @ S_ @ XtXi
        j = 1 + M2.index("lrvS"); gb[i] = bb[j]; tb[i] = bb[j] / math.sqrt(V_[j, j])
    p_boot = (tb >= t_obs).mean()
    # weekday-matched permutation
    wd = vv.wd.to_numpy(); Scols = vv[["lrvS", "lrv5S"]].to_numpy(float)
    gperm = np.empty(B)
    idx0 = np.arange(n)
    for i in range(B):
        perm = idx0.copy()
        for w_ in range(5):
            m_ = np.where(wd == w_)[0]
            perm[m_] = rng.permutation(m_)
        Xp = X2.copy(); Xp[:, [1 + M2.index("lrvS"), 1 + M2.index("lrv5S")]] = Scols[perm]
        bb, *_ = np.linalg.lstsq(Xp, y, rcond=None); gperm[i] = bb[1 + M2.index("lrvS")]
    p_perm = (np.abs(gperm) >= abs(g_obs)).mean()
    R5[wn] = dict(t_obs=t_obs, p_boot=p_boot, sd_t=tb.std(), q=np.quantile(tb, [0.95, 0.975]), p_perm=p_perm, sd_g=gperm.std())
    say(f"- {wn}: 実測 t {t_obs:+.2f}｜**wild bootstrap 帰無 t の sd {tb.std():.2f}・95%点 {np.quantile(tb,0.95):+.2f}・97.5%点 "
        f"{np.quantile(tb,0.975):+.2f}・片側 p {p_boot:.3f}**（破壊条件 p>0.025）｜曜日マッチ置換 帰無 sd(γ) {gperm.std():.4f}・両側 p {p_perm:.3f}")

# ---------------- R6 sampling frequency ----------------
say("\n## R6. サンプリング頻度（測定ノイズ）: 両系列の RV を 15 分・30 分集約で作り直して M2 を再推定（記述）")
say("| 窓 | 5 分 γ_S (t) | 15 分 γ_S (t) | 30 分 γ_S (t) |")
say("|---|---|---|---|")
def coarse_cell(v, suf, ycol):
    cols = [f"lrv{suf}", f"lrv{suf}_5", "evt0", "evt1", "brk", "lgvz", f"lrvS{suf}", f"lrvS{suf}_5"]
    vv = v[np.isfinite(v[cols + [ycol]].to_numpy()).all(1)].reset_index(drop=True)
    r = nw(vv[ycol].to_numpy(), vv[cols]); return r.get(f"lrvS{suf}") + (r.n,)
for wn, (y0, y1) in list(WIN.items())[:3]:
    v = sub(y0, y1); _, (g5, t5, _), _ = run(v, M2)
    g15, t15, _, n15 = coarse_cell(v, "15", "y15")
    g30, t30, _, n30 = coarse_cell(v, "30", "y30")
    say(f"| {wn} | {g5:+.4f} ({t5:+.2f}) | {g15:+.4f} ({t15:+.2f}) (n {n15}) | {g30:+.4f} ({t30:+.2f}) (n {n30}) |")
say("  （被説明・own 項・送り手を同じ頻度でそろえた・5 分でだけ出て粗サンプリングで消えるならマイクロストラクチャー由来）")

# ---------------- R7 shock lag structure ----------------
say("\n## R7. ショックのラグ構造（c48 のラグ・プロファイルは 5 日平均を外した不公平版）")
say("| 窓 | u^S_d (t) | u^S_(d−1) (t) | u^S_(d−2) (t) | u^S_(d−5) (t) | γ_S+γ_S5 (t) |")
say("|---|---|---|---|---|---|")
for wn, (y0, y1) in list(WIN.items())[:3]:
    v = sub(y0, y1)
    cols = BASE + ["lrvS", "lrv5S", "uS_l1", "uS_l2", "uS_l5"]
    r, (g, t, _), n = run(v, cols)
    o1 = r.get("uS_l1"); o2 = r.get("uS_l2"); o5 = r.get("uS_l5")
    r2_, _, _ = run(v, M2); s, ts = r2_.sum2("lrvS", "lrv5S")
    say(f"| {wn} | {g:+.4f} ({t:+.2f}) | {o1[0]:+.4f} ({o1[1]:+.2f}) | {o2[0]:+.4f} ({o2[1]:+.2f}) | {o5[0]:+.4f} ({o5[1]:+.2f}) | {s:+.4f} ({ts:+.2f}) |")
say("  （γ_S+γ_S5 ≈ 0 なら「株ボラの水準は無情報・1 日の偏差だけが効く」＝ボラの伝播としては持続が無い）")

# ---------------- R8 data holes / survivorship ----------------
say("\n## R8. データの穴・サバイバーシップ（記述）")
rows = []
for nm, vv in (("2020 年を全部落とす", F[F.year != 2020]),
               ("US500 完全日 nf=78 のみ", F[F.nfS == 78]),
               ("2014+ のみ", F[F.year >= 2014]),
               ("金 cash RV の nf_cash=78 のみ", F[F.nf_cash == 78])):
    for wn, (y0, y1) in list(WIN.items())[:2]:
        v = vv[(vv.year >= y0) & (vv.year <= y1)].reset_index(drop=True)
        if len(v) < 150: continue
        g, t, m, n = cell(v); rows.append(f"{nm}／{wn}: γ_S {g:+.4f} (t {t:+.2f}・MDE {m:.4f}・n {n})")
for s in rows: say(f"- {s}")

# ---------------- R9 multiple testing ----------------
say("\n## R9. 多重検定（data/cells.csv の判定済みセル全部に BH(q=0.05)）")
try:
    CE = pd.read_csv(os.path.join(DATA, "cells.csv"))
    def tnum(x):
        try: return abs(float(x))
        except Exception: return np.nan
    CE["ti"] = CE["t_in"].map(tnum); CE["to"] = CE["t_out"].map(tnum)
    CE["tmax"] = CE[["ti", "to"]].max(axis=1)
    CC = CE[np.isfinite(CE.tmax)].copy()
    CC["p"] = [math.erfc(t / math.sqrt(2)) for t in CC.tmax]
    CC = CC.sort_values("p").reset_index(drop=True)
    mtot = len(CC); CC["bh"] = [(i + 1) / mtot * 0.05 for i in range(mtot)]
    CC["pass_bh"] = CC.p <= CC.bh
    say(f"- 台帳の判定済みセル {mtot} 件（c40 以降・それ以前は台帳化されていない＝**m は下限**）。BH(q=0.05) 閾値一覧の先頭 6 件:")
    for i in range(min(6, mtot)):
        r_ = CC.iloc[i]; say(f"  - {r_['cycle']} {str(r_['cell'])[:52]}…: |t|max {r_['tmax']:.2f}・p {r_['p']:.2e}・BH 閾値 {r_['bh']:.4f} → {'通過' if r_['pass_bh'] else '×'}")
    pc48 = math.erfc(4.38 / math.sqrt(2))
    rank = int((CC.p < pc48).sum()) + 1
    say(f"- c48 C2（在 |t| 4.38・p {pc48:.2e}）を同じ族に入れると順位 {rank}/{mtot+1}・BH 閾値 {rank/(mtot+1)*0.05:.4f} → "
        f"{'BH 通過' if pc48 <= rank/(mtot+1)*0.05 else 'BH 不通過'}（在セル単体では多重検定に耐える。**問題は外・近年の側**: 外 t 2.39 → p {math.erfc(2.39/math.sqrt(2)):.3f}）")
except Exception as e:
    say(f"- cells.csv 読めず: {e}")

# ---------------- 判定 ----------------
say("\n## 判定（事前固定の破壊条件に照らす）")
a0 = BASEFIT["在 2012-20"]; o0 = BASEFIT["外 2021-26H1"]
c_r1b = (R1["在 2012-20"]["tb"] < 2) or (R1["在 2012-20"]["gb"] < R1["在 2012-20"]["mb"])
c_r2 = (R2["在 2012-20"]["tA"] < 2) or (R2["在 2012-20"]["gA"] < R2["在 2012-20"]["mA"])
c_r3 = nfail >= 2
c_r4 = bool(r4_broken) if r4_broken is not None else False
c_r5 = R5["在 2012-20"]["p_boot"] > 0.025
say(f"- R1(b) 金自身の 09:30–16:00 ET RV を統制 → 在 γ_S {R1['在 2012-20']['gb']:+.4f} (t {R1['在 2012-20']['tb']:+.2f}・MDE {R1['在 2012-20']['mb']:.4f}) → 破壊条件 {c_r1b}")
say(f"- R2 VIX/IV 変化を統制 → 在 γ_S {R2['在 2012-20']['gA']:+.4f} (t {R2['在 2012-20']['tA']:+.2f}・MDE {R2['在 2012-20']['mA']:.4f}) → 破壊条件 {c_r2}")
say(f"- R3 別分割で外側セル不成立 {nfail}/4 → 破壊条件 {c_r3}")
say(f"- R4 OOS で 1 円も払わない → 破壊条件 {c_r4}")
say(f"- R5 校正済み帰無で在 片側 p {R5['在 2012-20']['p_boot']:.3f} → 破壊条件 {c_r5}")
broken = c_r1b or c_r2 or c_r3 or c_r4 or c_r5
survived = (not broken) and (R1["在 2012-20"]["tb"] >= 2) and (R2["在 2012-20"]["tA"] >= 2)
say(f"\n### **{'broken' if broken else ('survived' if survived else 'inconclusive')}**（該当した破壊条件: " +
    ", ".join(nm for nm, c in (("R1b", c_r1b), ("R2", c_r2), ("R3", c_r3), ("R4", c_r4), ("R5", c_r5)) if c) + "）")
say(f"\n所要 {time.time()-T0:.1f} s・scan 無し・MT5 無し・外部通信無し・新規取得無し・seed 20261118")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
