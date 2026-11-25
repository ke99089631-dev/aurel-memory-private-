# -*- coding: utf-8 -*-
"""
[REFUTE c69 / 反証レーン 2026-11-25] 対象 = cycle69 (12:55) が「規則上 void」の脇に**肯定形で登記した 3 つ**。
c69 の主判定は暦の陽性対照の設計ミスで void＝主判定に破る余地は無い。よって c69 が「記述として実在」「得た知識」と
書いた部分だけを狙う。

--- 攻撃対象（c69 の本文からの引用値・これを再現してから壊す）---
T1 「薄い日の負の ρ1 は実在」: D_ρ1(TW 08:00→13:00 ET) = ρ1(THIN) − ρ1(同曜日±7/14/21/28 対照)
    在 2010-20 −0.082 (z −3.62)／外 2021-26H1 −0.111 (z −2.72)／近年 −0.127 (z −2.30)。
    読み分けの根拠 = ρ1_15 在 −0.142 (z −3.47)・D_VR6 在 −0.181 (z −2.36)＝「気配フリッカーなら 1/3・1/6 に
    減衰するはずが拡大 ⇒ 価格水準の平均回帰」。
T2 「得た知識 (1): 金の 5 分自己相関はボラ状態に単調依存する」（c69b・事後）: 通常平日の TW RV 5 分位で群 ρ1 が
    在 Q1 −0.057 → Q5 −0.003・外 −0.029 → +0.012・近年 −0.027 → +0.013、日次回帰 β(log RV_d) 在 +0.0259 (t 6.83)／
    外 +0.0186 (t 3.14)。さらに「Q1 の ρ1_15 −0.059 ≈ ρ1_5 −0.057＝1/3 に減衰しない ⇒ 価格水準の構造」。
    c69 はこれを c19 の訂正（「5 分 lag1 負の 2021+ 消滅は部分的に組成」）にまで使っている＝射程が広い。
T3 「祝日固有の残差」: RV 一致最近傍 4 日対照に対する D_ρ1 在 −0.043 (z −1.75)／外 −0.132 (z −2.38)、
    log RV 統制の γ_THIN 在 −0.037 (t −2.07)／外 −0.036 (t −1.30)。c69 自身が「決着不能」と書いたが、
    在 t −2.07 は名目有意として本文に残っている。

=== 事前固定（数字を見る前にこの docstring を書いた・seed 20261125・以後書き換えない）===
A1 再現: 自分の loader・自分の暦で c69/c69b の印字セルを独立に再計算。Δ|ρ1| > 0.005 または符号相違が出たら
   「数字が再現しない」として先に報告する（攻撃の前提が崩れるため）。

A2 【T2 への主攻撃・同一標本条件付け = look-ahead の一種】c69b は ρ1_d を計算した**同じ 60 本**から RV_d を作って
   分位に切っている。気配雑音モデル p=m+u では観測 RV が雑音実現を含むため、最下位分位は「雑音が相対的に大きく
   出た日」を過剰選択する ⇒ 機械的に ρ1 が負に出る。分離標本で再検定する:
     (a) 窓内分割: RV を 08:00–10:30（前半 30 本）、ρ1 を 10:30–13:00（後半 30 本・29 対）から＝共有足ゼロ。
     (b) 前日条件付け（事前情報・実装可能な唯一の形）: 前営業日の TW RV で分位・回帰。
   事前の合否規則: **T2 が survive する条件 = (a)(b) 両方で β の符号が同じ ∧ 在 |t| ≥ 2 ∧ |β| が同一標本版の
   50% 以上。|β| が 50% を下回る、または 在 |t| < 2 なら T2 は「同一標本条件付けの産物」として broken。**

A3 【T2 への機構攻撃・帰無シミュレーション】自己相関を一切持たない合成パネルで c69b の手続きをそのまま走らせる:
   効率価格 = 日別 σ_e,d の RW ＋ **定数** σ_u の iid 気配雑音。σ_u² = −ρ1_all·V（V = 全体の 1 本分散）、
   σ_e,d² = max(b_d/59 − 2σ_u², 0) で校正（観測 RV 分布をそのまま使う）。200 本の sim で分位プロファイル・
   β・ρ1_15 を印字。事前の合否規則: **sim の β が観測 β の 70〜130% を再現したら、T2 の「単調依存」は
   「定数雑音＋変動する信号」の恒等式 ρ1 = −σ_u²/(σ_e²+2σ_u²) の読み替えに過ぎず、流動性供給の証拠では
   ない ⇒ T2 の因果・経済解釈は broken（記述としての単調性は残る）。** sim が ρ1_15 の平坦性を再現しなければ
   そこだけは T2 に残す。

A4 【c69 自身が「閉じられない」と書いた穴を閉じに行く】雑音が iid でなく AR(1)（φ）なら 15 分でも残る。
   φ グリッド 0.0〜0.9 で sim し、**観測の (ρ1_5, ρ1_15) の組を同時に再現する φ が (0,1) に存在するか**を判定。
   事前の合否規則: **存在すれば「15 分で減衰しない ⇒ 価格水準の構造」という T1/T2 の読み分けは bid 単系列では
   成立しない ⇒ 読み分け broken（ask M1 無しでは決着不能）。存在しなければ読み分けは survived。**

A5 【T1/T3 へのランダム化・プラセボ】THIN ラベルの置換検定 B=20000。擬似 THIN は 適格 ∧ 非 HOL 全種 ∧ 非事象 の
   平日から抽出し、対照はその擬似 THIN の同曜日±7/14/21/28 で**同じ規則**で組む。3 つの帰無:
     (a) 無制限、(b) 曜日構成を保存（THIN 7 種中 4 種が月曜＝月曜効果との交絡）、
     (c) 曜日 × log RV 十分位の構成を保存（T3 の「RV を揃えた残差」に対する正しい帰無）。
   統計量 = D_ρ1 と γ_THIN。事前の合否規則: **(a) で p<0.05 でも (b)(c) で p≥0.05 なら、T1 は「月曜/静けさの
   構成」で説明され固有性は broken。(c) で p<0.05 なら T3 は survived。**

A6 多重検定: 本件の肯定形主張を生んだ族を列挙（窓 3 × {D_ρ1, ρ1_15, D_VR6, π} ＝12、祝日種別 7、
   RV 分位 5×3、γ 3）。Bonferroni と BH(q=0.05) をかけ、何本残るかを印字。c69 は「記述だから Bonferroni 不適用」と
   書いたが、**その記述が「得た知識」として登記された時点で族の一員**という立場で当てる。

A7 コスト倍・地平延長（T1 の経済的読みへの唯一の救済路の検査）: c69 は h=1 本の契約回帰 π しか測っていない。
   h = 1/2/3/6 本保有（往復は 1 回）の π(h) を THIN・対照で出し、往復コスト ×1/×2/×3 と比較。
   事前の期待 = どの h でも不可（平均回帰の振幅 ≈ ρ1·σ は 5 分 σ ≈ 4 bp に対し 0.2〜0.3 bp）。

A8 早引け汚染（T1）: 祝日の金は 13:00〜14:30 ET で早引け（c69 の flat プロファイル）。TW 終端 13:00 は
   「引け前の在庫調整」を含み得る（c69 の事前反証 (4)）。TW を 08:00→12:00（48 本）・08:00→11:00（36 本）に
   切り詰めて D_ρ1 を再計算。事前の合否規則: **切り詰めで |D| が半分以下 or 在 |z|<2 になれば T1 は
   「引け前 1 時間の artifact」として broken。**

A9 ティック格子・stale 気配（T1/T2 の共通の機械項）: 静かな日は bid が隣接ティックを往復するだけで ρ1 が負に出る。
   close の USD 差分の最小刻み（最頻 |Δp|）を期間別に出し、(i) |Δp| が 1 ティックの手のみの ρ1、
   (ii) 隣接対のどちらかが 0 の対を除いた ρ1、(iii) 同値連（stale run）を 1 本に潰した後の ρ1 を印字。
   事前の合否規則: **(iii) で 在 Q1 の ρ1 が 半分以下になれば T2 の「価格水準の構造」は broken。**

A10 レジーム部分集合・survivorship: 年別 D_ρ1（17 年）、祝日種別（7）、2020 除外、D2 に従い在/外/近年 別。
   適格条件（非 flat ≥0.5）で落ちた日・FULL 日（配信ゼロ）を印字＝「取引できない日が落ちている」方向の偏りを確認。

読むのは AUREL_RESEARCH/ 配下のみ。発注なし・デモ発注なし・本番ファイル編集なし・プロセス/執行機/ライブサーバ接触なし・
MT5 なし・プロップ（g4_/FundingPips）参照なし・秘密の読取出力なし・外部通信なし・多年 scan なし。
書き込みは AUREL_RESEARCH/data/refute_c69_thinday*.md のみ。seed 20261125。
"""
import os, time, math, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c69_thinday.md"); L = []
NY = "America/New_York"; SEED = 20261125
rng = np.random.default_rng(SEED); NB = 2000; NPERM = 20000
def say(s=""):
    print(s, flush=True); L.append(s)

say(f"# [REFUTE c69] 米国祝日の薄い金セッション — T1「薄い日の負 ρ1」/ T2「ρ1 の RV 単調依存」/ T3「祝日固有残差」を壊しにいく — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c69_thinday.py)")
say("")

# ================= データ =================
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)) * 1e4          # bp
dp = np.zeros(len(cl)); dp[1:] = np.diff(cl)                       # USD
say(f"- XAU M5 bid close: {len(ts)} 本・{pd.to_datetime(ts[0],unit='s')}〜{pd.to_datetime(ts[-1],unit='s')} UTC・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {(r[1:]==0).mean()*100:.2f}%")

def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

# ================= 暦（c69 と同一規則・import せず複製） =================
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451; month = (h + l - 7*m + 114) // 31; day = ((h + l - 7*m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7*(n-1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m+1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d

THIN, FULL, BOND, HALF = {}, set(), set(), set()
for y in range(2010, 2027):
    THIN[nth_weekday(y,1,0,3)] = "MLK"; THIN[nth_weekday(y,2,0,3)] = "Presidents"; THIN[last_weekday(y,5,0)] = "Memorial"
    if y >= 2022: THIN[observed(dt.date(y,6,19))] = "Juneteenth"
    THIN[observed(dt.date(y,7,4))] = "July4"; THIN[nth_weekday(y,9,0,1)] = "Labor"; THIN[nth_weekday(y,11,3,4)] = "Thanksgiving"
    for h in (observed(dt.date(y,1,1), sat_to_fri=False), easter(y) - dt.timedelta(days=2), observed(dt.date(y,12,25))):
        if h is not None: FULL.add(h)
    BOND.add(nth_weekday(y,10,0,2)); BOND.add(observed(dt.date(y,11,11)))
    HALF.add(nth_weekday(y,11,3,4) + dt.timedelta(days=1))
    for d in (dt.date(y,7,3), dt.date(y,12,24)):
        if d.weekday() < 5 and d not in FULL and d not in THIN: HALF.add(d)
HOL_ALL = set(THIN) | FULL | BOND | HALF

def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1+1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12)
            sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
EV = (set(d.date() for d in nfp_dates_v2())
      | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")).date).dt.date)
      | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date).dt.date))

dates = pd.date_range("2010-01-04", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); ddate = np.array([d.date() for d in dates]); yr = dates.year.to_numpy(); wdy = dates.weekday.to_numpy()
di = {d: i for i, d in enumerate(ddate)}

def win_matrix(h0, m0, nb):
    T = epoch_et(dates, h0, m0); M = np.full((N, nb), np.nan); P = np.full((N, nb), np.nan)
    ok = np.isfinite(T)
    i0 = np.clip(np.searchsorted(ts, T[ok].astype(np.int64)), 0, len(ts) - nb)
    good = (ts[i0] == T[ok].astype(np.int64)) & (ts[i0 + nb - 1] == T[ok].astype(np.int64) + (nb-1)*300)
    idx = i0[good][:, None] + np.arange(nb)[None, :]
    rows = np.where(ok)[0][good]; M[rows] = r[idx]; P[rows] = dp[idx]
    return M, P

M, DP = win_matrix(8, 0, 60)                      # TW 08:00->13:00 ET, 60 bars of 5-min log-return (bp)
is_thin = np.array([d in THIN for d in ddate]); is_hol = np.array([d in HOL_ALL for d in ddate])
is_ev = np.array([d in EV for d in ddate]); is_full = np.array([d in FULL for d in ddate])
full_row = np.isfinite(M).all(1)
nfw = np.where(full_row, np.mean(M != 0, axis=1), np.nan)
elig = full_row & (nfw >= 0.5) & ~is_ev

WINS = [("在 2010-20", (yr >= 2010) & (yr <= 2020)), ("外 2021-26H1", yr >= 2021), ("近年 2024-26H1", yr >= 2024)]

def cells(Mx):
    """per-day sufficient statistics on a (N x nb) return matrix"""
    a = np.nansum(Mx[:, 1:] * Mx[:, :-1], 1); b = np.nansum(Mx[:, 1:]**2, 1); rv = np.nansum(Mx**2, 1)
    nb = Mx.shape[1]; k3 = nb // 3; k6 = nb // 6
    X3 = Mx[:, :k3*3].reshape(len(Mx), k3, 3).sum(2); a15 = np.nansum(X3[:, 1:]*X3[:, :-1], 1); b15 = np.nansum(X3[:, 1:]**2, 1)
    X6 = Mx[:, :k6*6].reshape(len(Mx), k6, 6).sum(2); v30 = np.nansum(X6**2, 1)
    return a, b, rv, a15, b15, v30, nb

a_d, b_d, rv_d, a15_d, b15_d, v30_d, NBAR = cells(M)
lrv = np.where(elig & (rv_d > 0), np.log(np.maximum(rv_d, 1e-12)), np.nan)

def rho(mask, a=a_d, b=b_d):
    sb = np.nansum(b[mask]); return np.nansum(a[mask]) / sb if sb > 0 else np.nan
def vr6(mask):
    n30 = (NBAR // 6); return (np.nansum(v30_d[mask]) / n30) / (6.0 * np.nansum(b_d[mask]) / (NBAR - 1))

# ---- control map: same weekday D +/- 7/14/21/28 ----
OFF = [-28, -21, -14, -7, 7, 14, 21, 28]
NEI = np.full((N, len(OFF)), -1, dtype=np.int64)
for j, o in enumerate(OFF):
    for i in range(N):
        d2 = ddate[i] + dt.timedelta(days=o); k = di.get(d2, -1)
        NEI[i, j] = k
ctrl_ok = elig & ~is_hol                      # eligible, no holiday of any kind, no event
def controls_of(tmask, exclude=None):
    nn = NEI[tmask].ravel(); nn = nn[nn >= 0]
    m = np.zeros(N, bool); m[nn] = True
    m &= ctrl_ok
    if exclude is not None: m &= ~exclude
    return m

def boot_D(tm, cm, a=a_d, b=b_d, B=NB, seed=SEED):
    g = np.random.default_rng(seed)
    ti = np.where(tm)[0]; ci = np.where(cm)[0]
    if len(ti) < 3 or len(ci) < 3: return np.nan, np.nan
    obs = (np.nansum(a[ti])/np.nansum(b[ti])) - (np.nansum(a[ci])/np.nansum(b[ci]))
    out = np.empty(B)
    for k in range(B):
        t2 = g.choice(ti, len(ti), True); c2 = g.choice(ci, len(ci), True)
        out[k] = (np.nansum(a[t2])/np.nansum(b[t2])) - (np.nansum(a[c2])/np.nansum(b[c2]))
    s = np.nanstd(out, ddof=1); return obs, (obs/s if s > 0 else np.nan)

# ======================================================================
say("## A1 再現 — c69/c69b の印字セルを独立 loader で再計算")
say(f"- 日格子 {N} 平日・TW 行揃い {full_row.sum()}・適格 {elig.sum()}・THIN 暦 {is_thin.sum()}・THIN 適格 {(is_thin&elig).sum()}・FULL {is_full.sum()}（TW 非 flat 平均 {np.nanmean(nfw[is_full]) if np.isfinite(nfw[is_full]).any() else float('nan'):.3f}）")
say("")
say("| 窓 | n(THIN) | n(C) | ρ1 THIN | ρ1 C | D_ρ1 | z | c69 の値 | ρ1_15 D | z | D_VR6 | z |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|")
C69_D = {"在 2010-20": (-0.082, -3.62), "外 2021-26H1": (-0.111, -2.72), "近年 2024-26H1": (-0.127, -2.30)}
REP = {}
for nm, wm in WINS:
    tm = is_thin & elig & wm; cm = controls_of(tm, exclude=is_thin)
    D, z = boot_D(tm, cm)
    D15, z15 = boot_D(tm, cm, a=a15_d, b=b15_d)
    # VR6 difference, day-bootstrap
    g = np.random.default_rng(SEED + 1); ti = np.where(tm)[0]; ci = np.where(cm)[0]
    obsv = vr6(tm) - vr6(cm); bv = np.empty(NB)
    n30 = NBAR // 6
    for k in range(NB):
        t2 = g.choice(ti, len(ti), True); c2 = g.choice(ci, len(ci), True)
        f = lambda ix: (np.nansum(v30_d[ix])/n30) / (6.0*np.nansum(b_d[ix])/(NBAR-1))
        bv[k] = f(t2) - f(c2)
    zv = obsv/np.nanstd(bv, ddof=1)
    REP[nm] = dict(n=int(tm.sum()), nc=int(cm.sum()), D=D, z=z, D15=D15, z15=z15, DV=obsv, zv=zv,
                   rt=rho(tm), rc=rho(cm), tm=tm, cm=cm)
    c = C69_D[nm]
    say(f"| {nm} | {tm.sum()} | {cm.sum()} | {rho(tm):+.4f} | {rho(cm):+.4f} | **{D:+.4f}** | {z:+.2f} | {c[0]:+.3f} (z {c[1]:+.2f}) | {D15:+.4f} | {z15:+.2f} | {obsv:+.4f} | {zv:+.2f} |")
say("")

# ---- c69b replication: quintiles on same-sample RV ----
say("### A1b c69b（RV 5 分位・同一標本条件付け）の再現")
norm = elig & ~is_hol
say("| 窓 | Q1 ρ1 | Q2 | Q3 | Q4 | Q5 | c69b Q1→Q5 | β(log RV) | t | c69b β (t) |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
C69B = {"在 2010-20": ("-0.057 → -0.003", "+0.0259 (6.83)"), "外 2021-26H1": ("-0.029 → +0.012", "+0.0186 (3.14)"),
        "近年 2024-26H1": ("-0.027 → +0.013", "+0.0134 (1.90)")}
def ols_hc1(X, y):
    XtXi = np.linalg.pinv(X.T @ X); bhat = XtXi @ (X.T @ y); e = y - X @ bhat
    n, k = X.shape; S = (X * e[:, None]).T @ (X * e[:, None]); V = XtXi @ S @ XtXi * (n/(n-k))
    return bhat, np.sqrt(np.diag(V))
def quintile_profile(selmask, lrv_vec, a=a_d, b=b_d):
    ix = np.where(selmask & np.isfinite(lrv_vec))[0]
    if len(ix) < 50: return [np.nan]*5, np.nan, np.nan, len(ix)
    q = np.quantile(lrv_vec[ix], [.2, .4, .6, .8]); bk = np.digitize(lrv_vec[ix], q)
    prof = [ (np.nansum(a[ix[bk==k]])/np.nansum(b[ix[bk==k]])) if (bk==k).sum() > 3 else np.nan for k in range(5)]
    rho_d = np.where(b[ix] > 0, a[ix]/b[ix], np.nan); ok = np.isfinite(rho_d)
    X = np.column_stack([np.ones(ok.sum()), lrv_vec[ix][ok]])
    bh, se = ols_hc1(X, rho_d[ok])
    return prof, bh[1], bh[1]/se[1], len(ix)
BASE_BETA = {}
for nm, wm in WINS:
    prof, beta, tb, nn = quintile_profile(norm & wm, lrv)
    BASE_BETA[nm] = (beta, tb)
    c = C69B[nm]
    say(f"| {nm} (n={nn}) | {prof[0]:+.4f} | {prof[1]:+.4f} | {prof[2]:+.4f} | {prof[3]:+.4f} | {prof[4]:+.4f} | {c[0]} | **{beta:+.4f}** | {tb:+.2f} | {c[1]} |")
say("")

# ======================================================================
say("## A2 【T2 への主攻撃】同一標本条件付け vs 分離標本（窓内分割・前日 RV）")
# (a) split window: RV from bars 0..29, rho1 from bars 30..59
M_h1 = M[:, :30]; M_h2 = M[:, 30:]
rv_h1 = np.nansum(M_h1**2, 1); a_h2 = np.nansum(M_h2[:, 1:]*M_h2[:, :-1], 1); b_h2 = np.nansum(M_h2[:, 1:]**2, 1)
rv_h2 = np.nansum(M_h2**2, 1); a_h1 = np.nansum(M_h1[:, 1:]*M_h1[:, :-1], 1); b_h1 = np.nansum(M_h1[:, 1:]**2, 1)
lrv_h1 = np.where(elig & (rv_h1 > 0), np.log(np.maximum(rv_h1, 1e-12)), np.nan)
lrv_h2 = np.where(elig & (rv_h2 > 0), np.log(np.maximum(rv_h2, 1e-12)), np.nan)
# (b) previous trading day's TW RV
lrv_prev = np.full(N, np.nan); lrv_prev[1:] = lrv[:-1]

say("### (i) 同一標本（c69b・参照）／(ii) 窓内分割 RV=前半→ρ1=後半（共有足ゼロ）／(iii) 分割の逆向き／(iv) 前日 RV")
say("| 窓 | 条件付け | Q1 ρ1 | Q5 ρ1 | Q1−Q5 | β(log RV) | t | 同一標本 β 比 |")
say("|---|---|---|---|---|---|---|---|")
A2 = {}
for nm, wm in WINS:
    rows = []
    # (i) same-sample, but on the SECOND half only so magnitudes are comparable with (ii)
    p_s, b_s, t_s, _ = quintile_profile(norm & wm, lrv_h2, a=a_h2, b=b_h2)
    rows.append(("(i) 同一標本[後半 RV→後半 ρ1]", p_s, b_s, t_s))
    p_x, b_x, t_x, _ = quintile_profile(norm & wm, lrv_h1, a=a_h2, b=b_h2)
    rows.append(("(ii) 分割[前半 RV→後半 ρ1]", p_x, b_x, t_x))
    p_y, b_y, t_y, _ = quintile_profile(norm & wm, lrv_h2, a=a_h1, b=b_h1)
    rows.append(("(iii) 分割[後半 RV→前半 ρ1]", p_y, b_y, t_y))
    p_p, b_p, t_p, _ = quintile_profile(norm & wm, lrv_prev, a=a_d, b=b_d)
    rows.append(("(iv) 前日 RV→当日 ρ1(全 60)", p_p, b_p, t_p))
    ref = rows[0][2]
    A2[nm] = rows
    for lab, pr, bb, tt in rows:
        ratio = (bb/ref*100) if (ref and np.isfinite(ref) and ref != 0) else np.nan
        say(f"| {nm} | {lab} | {pr[0]:+.4f} | {pr[4]:+.4f} | {pr[0]-pr[4]:+.4f} | **{bb:+.4f}** | {tt:+.2f} | {ratio:.0f}% |")
say("")

# ======================================================================
say("## A3 【T2 への機構攻撃】自己相関ゼロ＋定数 iid 気配雑音の帰無 sim で c69b の手続きを走らせる")
V_all = np.nansum(b_d[norm]) / max((np.isfinite(b_d) & norm).sum() * (NBAR-1), 1)
rho_all = rho(norm)
sig_u2 = max(-rho_all * V_all, 1e-9)
say(f"- 校正: 全体 ρ1 = {rho_all:+.5f}・1 本分散 V = {V_all:.3f} bp² → σ_u² = −ρ1·V = {sig_u2:.4f} bp²（σ_u = {math.sqrt(sig_u2):.3f} bp）")
say(f"- 日別 σ_e,d² = max(b_d/{NBAR-1} − 2σ_u², 0)：0 にクリップされた適格日 = {int(((np.where(norm, b_d/(NBAR-1), np.nan) - 2*sig_u2) <= 0).sum())}/{int(norm.sum())}")

def simulate(sel_idx, se2, phi=0.0, nsim=200, nb=60, seed=SEED):
    """returns arrays of (prof5, beta, t, rho1_5, rho1_15) over nsim draws, zero true autocorrelation"""
    g = np.random.default_rng(seed)
    nd = len(sel_idx); out = []
    for s in range(nsim):
        eff = g.standard_normal((nd, nb)) * np.sqrt(se2)[:, None]
        if phi <= 0:
            u = g.standard_normal((nd, nb+1)) * math.sqrt(sig_u2)
        else:
            eps = g.standard_normal((nd, nb+1)) * math.sqrt(sig_u2 * (1 - phi**2))
            u = np.empty((nd, nb+1)); u[:, 0] = g.standard_normal(nd) * math.sqrt(sig_u2)
            for j in range(1, nb+1): u[:, j] = phi*u[:, j-1] + eps[:, j]
        Ms = eff + np.diff(u, axis=1)
        aa = np.sum(Ms[:, 1:]*Ms[:, :-1], 1); bb = np.sum(Ms[:, 1:]**2, 1); rvs = np.sum(Ms**2, 1)
        X3 = Ms[:, :(nb//3)*3].reshape(nd, nb//3, 3).sum(2)
        a15s = np.sum(X3[:, 1:]*X3[:, :-1], 1); b15s = np.sum(X3[:, 1:]**2, 1)
        lr = np.log(np.maximum(rvs, 1e-12))
        q = np.quantile(lr, [.2, .4, .6, .8]); bk = np.digitize(lr, q)
        prof = [np.sum(aa[bk==k])/np.sum(bb[bk==k]) for k in range(5)]
        rd = aa/bb; X = np.column_stack([np.ones(nd), lr]); bh, se_ = ols_hc1(X, rd)
        out.append((prof, bh[1], bh[1]/se_[1], np.sum(aa)/np.sum(bb), np.sum(a15s)/np.sum(b15s)))
    return out

say("")
say("| 窓 | 量 | 観測 | sim(iid 雑音・自己相関ゼロ) 平均 [p5,p95] | 観測/sim |")
say("|---|---|---|---|---|")
SIM = {}
for nm, wm in WINS:
    ix = np.where(norm & wm & np.isfinite(b_d) & (b_d > 0))[0]
    se2 = np.maximum(b_d[ix]/(NBAR-1) - 2*sig_u2, 1e-9)
    res = simulate(ix, se2, phi=0.0, nsim=200)
    prof = np.array([x[0] for x in res]); bet = np.array([x[1] for x in res]); r5 = np.array([x[3] for x in res]); r15 = np.array([x[4] for x in res])
    ob, otb = BASE_BETA[nm]
    o_prof, _, _, _ = quintile_profile(norm & wm, lrv)
    o_r5 = rho(norm & wm); o_r15 = np.nansum(a15_d[norm & wm])/np.nansum(b15_d[norm & wm])
    SIM[nm] = dict(beta=bet, r5=r5, r15=r15, prof=prof)
    for lab, o, sv in [("β(log RV)", ob, bet), ("Q1 ρ1", o_prof[0], prof[:, 0]), ("Q5 ρ1", o_prof[4], prof[:, 4]),
                       ("全体 ρ1(5分)", o_r5, r5), ("全体 ρ1(15分)", o_r15, r15)]:
        m = np.mean(sv); lo, hi = np.percentile(sv, [5, 95])
        ratio = (o/m) if (m != 0) else np.nan
        say(f"| {nm} | {lab} | {o:+.4f} | {m:+.4f} [{lo:+.4f},{hi:+.4f}] | {ratio:.2f}× |")
say("")

# ======================================================================
say("## A4 【c69 が「閉じられない」と書いた穴】AR(1) 気配雑音で (ρ1_5, ρ1_15) を同時に再現する φ は存在するか")
say("- 期待（c69 の読み分け）: iid 雑音なら ρ1_15 ≈ ρ1_5/3。観測は 在 ρ1_15 ≈ ρ1_5（減衰しない）＝「価格水準の構造」。")
say("- 攻撃: 雑音が AR(1) なら Δu は数分幅で往復し 15 分でも残る。φ グリッドで sim し観測の組に当てる。")
say("")
say("| 窓 | 観測 ρ1_5 | 観測 ρ1_15 | 観測比 15/5 | φ=0.0 比 | φ=0.3 | φ=0.5 | φ=0.7 | φ=0.85 | 一致する φ |")
say("|---|---|---|---|---|---|---|---|---|---|")
PHIS = [0.0, 0.3, 0.5, 0.7, 0.85]
A4 = {}
for nm, wm in WINS:
    ix = np.where(norm & wm & np.isfinite(b_d) & (b_d > 0))[0]
    o_r5 = rho(norm & wm); o_r15 = np.nansum(a15_d[norm & wm])/np.nansum(b15_d[norm & wm])
    o_ratio = o_r15/o_r5 if o_r5 != 0 else np.nan
    rr = []
    for phi in PHIS:
        se2 = np.maximum(b_d[ix]/(NBAR-1) - 2*sig_u2, 1e-9)
        res = simulate(ix, se2, phi=phi, nsim=40, seed=SEED+int(phi*100))
        s5 = np.mean([x[3] for x in res]); s15 = np.mean([x[4] for x in res])
        rr.append(s15/s5 if s5 != 0 else np.nan)
    hit = [f"{PHIS[i]:.2f}" for i in range(len(PHIS)) if np.isfinite(rr[i]) and abs(rr[i] - o_ratio) < 0.15]
    A4[nm] = (o_ratio, rr, hit)
    say(f"| {nm} | {o_r5:+.4f} | {o_r15:+.4f} | **{o_ratio:.2f}** | {rr[0]:.2f} | {rr[1]:.2f} | {rr[2]:.2f} | {rr[3]:.2f} | {rr[4]:.2f} | {'・'.join(hit) if hit else 'なし'} |")
say("")

# ======================================================================
say("## A5 【T1/T3 へのランダム化】THIN ラベルの置換検定 B=20000（3 つの帰無）")
pool = np.where(elig & ~is_hol)[0]
dec = np.full(N, -1)
for nm, wm in WINS:
    ixw = np.where(elig & wm & np.isfinite(lrv))[0]
    if len(ixw) > 20:
        qs = np.quantile(lrv[ixw], np.linspace(.1, .9, 9)); dec[ixw] = np.digitize(lrv[ixw], qs)

def perm_p(tm_real, wm, mode, B=NPERM, seed=SEED):
    g = np.random.default_rng(seed)
    treal = np.where(tm_real)[0]; n_t = len(treal)
    cm_real = controls_of(tm_real, exclude=is_thin)
    obs = rho(tm_real) - rho(cm_real)
    cand = np.where(elig & ~is_hol & wm)[0]
    if mode == "wd":
        groups = {w: cand[wdy[cand] == w] for w in range(5)}
        need = {w: int((wdy[treal] == w).sum()) for w in range(5)}
    elif mode == "wd_rv":
        groups = {}; need = {}
        for w in range(5):
            for dq in range(10):
                k = (w, dq); groups[k] = cand[(wdy[cand] == w) & (dec[cand] == dq)]
                need[k] = int(((wdy[treal] == w) & (dec[treal] == dq)).sum())
    else:
        groups = {0: cand}; need = {0: n_t}
    skipped = 0
    out = np.empty(B); out[:] = np.nan
    for k in range(B):
        pick = []
        for key, nn in need.items():
            if nn == 0: continue
            pooln = groups[key]
            if len(pooln) < nn: skipped += 1; pick.append(g.choice(pooln, min(nn, len(pooln)), False)) if len(pooln) else None; continue
            pick.append(g.choice(pooln, nn, False))
        if not pick: continue
        pt = np.concatenate(pick)
        tmp = np.zeros(N, bool); tmp[pt] = True
        cmp_ = controls_of(tmp, exclude=tmp | is_thin)
        if cmp_.sum() < 10: continue
        out[k] = rho(tmp) - rho(cmp_)
    out = out[np.isfinite(out)]
    p = (np.sum(np.abs(out) >= abs(obs)) + 1) / (len(out) + 1)
    return obs, p, len(out), np.mean(out), np.std(out, ddof=1)

say("| 窓 | 観測 D_ρ1 | 帰無(a) 無制限 p | (b) 曜日保存 p | (c) 曜日×RV十分位保存 p | 帰無の sd (c) |")
say("|---|---|---|---|---|---|")
A5 = {}
for nm, wm in WINS:
    tm = is_thin & elig & wm
    o1, p1, n1, m1, s1 = perm_p(tm, wm, "free", B=4000)
    o2, p2, n2, m2, s2 = perm_p(tm, wm, "wd", B=4000, seed=SEED+7)
    o3, p3, n3, m3, s3 = perm_p(tm, wm, "wd_rv", B=4000, seed=SEED+13)
    A5[nm] = dict(obs=o1, p_free=p1, p_wd=p2, p_wdrv=p3, sd=s3, mean_wdrv=m3)
    say(f"| {nm} | {o1:+.4f} | {p1:.4f} (n={n1}) | {p2:.4f} | **{p3:.4f}** | {s3:.4f}（帰無平均 {m3:+.4f}） |")
say("")

# gamma_THIN regression with log RV control + permutation
say("### A5b γ_THIN（log RV 統制の祝日ダミー）と、そのダミーの置換分布")
say("| 窓 | γ_THIN | HC1 t | c69 の値 | 置換 p（曜日保存） | 置換 p（曜日×RV十分位保存） |")
say("|---|---|---|---|---|---|")
C69G = {"在 2010-20": "-0.037 (t -2.07)", "外 2021-26H1": "-0.036 (t -1.30)", "近年 2024-26H1": "-0.032 (t -0.85)"}
A5B = {}
for nm, wm in WINS:
    sel = elig & wm & np.isfinite(lrv) & (b_d > 0) & (~is_hol | is_thin)
    ix = np.where(sel)[0]
    rho_dd = a_d[ix]/b_d[ix]
    X = np.column_stack([np.ones(len(ix)), lrv[ix], is_thin[ix].astype(float)])
    bh, se = ols_hc1(X, rho_dd); g_obs = bh[2]; t_obs = bh[2]/se[2]
    # permutation of the dummy
    def perm_gamma(mode, B=4000, seed=SEED+21):
        g = np.random.default_rng(seed); n_t = int(is_thin[ix].sum()); res = np.empty(B)
        wdl = wdy[ix]; decl = dec[ix]
        if mode == "wd":
            keys = [(w,) for w in range(5)]; memb = {(w,): np.where(wdl == w)[0] for w in range(5)}
            need = {(w,): int((wdl[is_thin[ix]] == w).sum()) for w in range(5)}
        else:
            memb = {}; need = {}
            for w in range(5):
                for dq in range(10):
                    memb[(w,dq)] = np.where((wdl == w) & (decl == dq))[0]
                    need[(w,dq)] = int(((wdl[is_thin[ix]] == w) & (decl[is_thin[ix]] == dq)).sum())
        for k in range(B):
            pick = []
            for key, nn in need.items():
                if nn == 0: continue
                pl = memb[key]
                if len(pl) < nn: pick.append(pl); continue
                pick.append(g.choice(pl, nn, False))
            dmy = np.zeros(len(ix));
            if pick: dmy[np.concatenate(pick)] = 1.0
            Xp = np.column_stack([np.ones(len(ix)), lrv[ix], dmy])
            bp, _ = ols_hc1(Xp, rho_dd); res[k] = bp[2]
        return (np.sum(np.abs(res) >= abs(g_obs)) + 1) / (B + 1)
    pw = perm_gamma("wd"); pr = perm_gamma("wd_rv", seed=SEED+29)
    A5B[nm] = dict(g=g_obs, t=t_obs, pw=pw, pr=pr)
    say(f"| {nm} | **{g_obs:+.4f}** | {t_obs:+.2f} | {C69G[nm]} | {pw:.4f} | **{pr:.4f}** |")
say("")

# ======================================================================
say("## A7 コスト倍・地平延長（T1 の経済的読み）")
say("- π(h) = mean over bars of [−sign(r_{j−1}) · (h 本先までの累積リターン)]・往復は 1 回だけ払う。")
px8 = np.full(N, np.nan)
T8 = epoch_et(dates, 8, 0); ok8 = np.isfinite(T8)
i08 = np.clip(np.searchsorted(ts, T8[ok8].astype(np.int64)), 0, len(ts)-1)
g8 = ts[i08] == T8[ok8].astype(np.int64); px8[np.where(ok8)[0][g8]] = cl[i08[g8]]
cost_bp = 0.16 / px8 * 1e4
say("")
say("| 窓 | 群 | π(1) | π(2) | π(3) | π(6) | 往復×1 | ×2 | ×3 | 最良 π/コスト |")
say("|---|---|---|---|---|---|---|---|---|---|")
for nm, wm in WINS:
    for lab, mk in [("THIN", is_thin & elig & wm), ("対照", REP[nm]["cm"])]:
        pis = []
        for h in (1, 2, 3, 6):
            cum = np.full((N, 60-h), np.nan)
            for j in range(60-h): cum[:, j] = np.nansum(M[:, j+1:j+1+h], 1)
            prev = M[:, :60-h]; mkz = (prev != 0) & np.isfinite(cum)
            v = np.where(mkz, -np.sign(prev)*cum, np.nan)
            pd_ = np.nanmean(v, 1)
            pis.append(np.nanmean(pd_[mk]))
        c1 = np.nanmedian(cost_bp[mk])
        best = max(pis);
        say(f"| {nm} | {lab} | {pis[0]:+.3f} | {pis[1]:+.3f} | {pis[2]:+.3f} | {pis[3]:+.3f} | {c1:.2f} | {2*c1:.2f} | {3*c1:.2f} | {best/c1*100:.0f}% |")
say("")

# ======================================================================
say("## A8 早引け汚染（T1）: TW を切り詰めて D_ρ1 を再計算")
say("| 窓 | TW 08:00→13:00 (60) | →12:00 (48) | →11:00 (36) | 10:00→13:00 (36) |")
say("|---|---|---|---|---|")
A8 = {}
for nm, wm in WINS:
    tm = REP[nm]["tm"]; cm = REP[nm]["cm"]; row = []
    for lab, sl in [("60", slice(0, 60)), ("48", slice(0, 48)), ("36", slice(0, 36)), ("last36", slice(24, 60))]:
        Mx = M[:, sl]; aa = np.nansum(Mx[:, 1:]*Mx[:, :-1], 1); bb = np.nansum(Mx[:, 1:]**2, 1)
        D, z = boot_D(tm, cm, a=aa, b=bb, B=1000, seed=SEED+3)
        row.append((D, z))
    A8[nm] = row
    say(f"| {nm} | {row[0][0]:+.4f} (z {row[0][1]:+.2f}) | {row[1][0]:+.4f} (z {row[1][1]:+.2f}) | {row[2][0]:+.4f} (z {row[2][1]:+.2f}) | {row[3][0]:+.4f} (z {row[3][1]:+.2f}) |")
say("")

# ======================================================================
say("## A9 ティック格子・stale 気配（T1/T2 の共通機械項）")
absdp = np.abs(DP[np.isfinite(DP)]); nz = absdp[absdp > 1e-9]
qs = np.percentile(nz, [1, 5, 25, 50])
say(f"- TW の |Δprice| 非ゼロ分位: p1 {qs[0]:.4f}・p5 {qs[1]:.4f}・p25 {qs[2]:.4f}・p50 {qs[3]:.4f} USD。最小非ゼロ {nz.min():.5f}")
tick = np.round(np.median(np.diff(np.sort(np.unique(np.round(nz, 5)))[:50])), 5) if len(nz) > 60 else np.nan
TICK = max(np.min(nz), 1e-5)
say(f"- 最小刻み推定 {TICK:.5f} USD。|Δp| ≤ 2 ティックの手の割合（適格 TW 全体）= {np.mean(np.abs(DP[elig]) <= 2*TICK + 1e-9)*100:.1f}%")
# (ii) drop pairs where either leg is zero ; (iii) collapse stale runs
def rho_nozero(Mx, mask):
    p, n = Mx[:, :-1], Mx[:, 1:]
    mk = (p != 0) & (n != 0) & np.isfinite(p) & np.isfinite(n)
    aa = np.nansum(np.where(mk, p*n, 0), 1); bb = np.nansum(np.where(mk, n*n, 0), 1)
    sb = np.nansum(bb[mask]); return np.nansum(aa[mask])/sb if sb > 0 else np.nan
def rho_collapsed(mask):
    """collapse runs of identical price into a single move (removes stale-quote zeros entirely)"""
    ix = np.where(mask)[0]; A = 0.0; B = 0.0
    for i in ix:
        v = M[i][np.isfinite(M[i])]; v = v[v != 0]
        if len(v) < 3: continue
        A += np.sum(v[1:]*v[:-1]); B += np.sum(v[1:]**2)
    return A/B if B > 0 else np.nan
say("")
say("| 窓 | 群 | ρ1 生 | ρ1 ゼロ脚を除く | ρ1 同値連を潰す | 潰した後/生 |")
say("|---|---|---|---|---|---|")
for nm, wm in WINS:
    for lab, mk in [("THIN", REP[nm]["tm"]), ("対照", REP[nm]["cm"]), ("通常 Q1(最静)", None)]:
        if mk is None:
            ixw = np.where(norm & wm & np.isfinite(lrv))[0]
            q = np.quantile(lrv[ixw], .2); mk = np.zeros(N, bool); mk[ixw[lrv[ixw] <= q]] = True
        r1 = rho(mk); r2 = rho_nozero(M, mk); r3 = rho_collapsed(mk)
        say(f"| {nm} | {lab} | {r1:+.4f} | {r2:+.4f} | {r3:+.4f} | {(r3/r1*100) if r1 else float('nan'):.0f}% |")
say("")

# ======================================================================
say("## A10 レジーム部分集合・年別・種別・survivorship")
say("### 年別 D_ρ1")
rows = []
for y in range(2010, 2027):
    wm = yr == y; tm = is_thin & elig & wm
    if tm.sum() < 3: rows.append((y, tm.sum(), np.nan)); continue
    cm = controls_of(tm, exclude=is_thin)
    rows.append((y, int(tm.sum()), rho(tm) - rho(cm)))
say("| 年 | " + " | ".join(str(x[0]) for x in rows) + " |")
say("|---|" + "---|"*len(rows))
say("| n | " + " | ".join(str(x[1]) for x in rows) + " |")
say("| D_ρ1 | " + " | ".join(f"{x[2]:+.3f}" if np.isfinite(x[2]) else "—" for x in rows) + " |")
neg = sum(1 for x in rows if np.isfinite(x[2]) and x[2] < 0); tot = sum(1 for x in rows if np.isfinite(x[2]))
say(f"- 負の年 {neg}/{tot}（符号検定 two-sided p = {2*sum(math.comb(tot,k) for k in range(neg,tot+1))/2**tot:.4f}）")
say("")
say("### 2020 除外（c20/c38 の符号レジーム反転の年）と祝日種別")
for nm, wm in WINS:
    tm = is_thin & elig & wm & (yr != 2020); cm = controls_of(tm, exclude=is_thin)
    D, z = boot_D(tm, cm, B=1000, seed=SEED+5)
    say(f"- {nm} 2020 除外: D_ρ1 {D:+.4f} (z {z:+.2f}・n {tm.sum()}) vs 全体 {REP[nm]['D']:+.4f} (z {REP[nm]['z']:+.2f})")
say("")
say("| 祝日種別 | n(適格) | ρ1 | D_ρ1 | z |")
say("|---|---|---|---|---|")
TYPE_Z = {}
for k in dict.fromkeys(THIN.values()):
    tm = np.array([ddate[i] in THIN and THIN[ddate[i]] == k for i in range(N)]) & elig
    if tm.sum() < 4: continue
    cm = controls_of(tm, exclude=is_thin); D, z = boot_D(tm, cm, B=1000, seed=SEED+11)
    TYPE_Z[k] = z
    say(f"| {k} | {tm.sum()} | {rho(tm):+.4f} | {D:+.4f} | {z:+.2f} |")
say("")
say("### survivorship")
drop = is_thin & full_row & (nfw < 0.5)
say(f"- 適格落ち（非 flat <0.5）: THIN {int(drop.sum())} 日・通常 {int((~is_thin & ~is_hol & full_row & (nfw<0.5)).sum())} 日")
say(f"- TW 行が揃わない日: 全体 {int((~full_row).sum())}・THIN {int((is_thin & ~full_row).sum())}・FULL {int((is_full & ~full_row).sum())}")
say(f"- FULL（配信ゼロ想定）: 行揃い {int((is_full & full_row).sum())}/{int(is_full.sum())}・非 flat 平均 {np.nanmean(np.where(is_full & full_row, nfw, np.nan)):.3f}")

# ======================================================================
say("")
say("## A6 多重検定補正（本件の肯定形主張を生んだ族）")
zs = []
for nm, _ in WINS:
    zs += [(f"D_ρ1 {nm}", REP[nm]["z"]), (f"D_ρ1_15 {nm}", REP[nm]["z15"]), (f"D_VR6 {nm}", REP[nm]["zv"]),
           (f"β(logRV) {nm}", BASE_BETA[nm][1]), (f"γ_THIN {nm}", A5B[nm]["t"])]
for k, z in TYPE_Z.items(): zs.append((f"種別 {k}", z))
from math import erfc
pv = [(nm, 2*0.5*erfc(abs(z)/math.sqrt(2))) for nm, z in zs if np.isfinite(z)]
pv_sorted = sorted(pv, key=lambda x: x[1]); m = len(pv_sorted)
bonf = [x for x in pv_sorted if x[1] < 0.05/m]
bh = []
for i, (nm, p) in enumerate(pv_sorted, 1):
    if p <= 0.05*i/m: bh = pv_sorted[:i]
say(f"- 族サイズ m = {m}。Bonferroni 0.05/m = {0.05/m:.5f} を下回る: {len(bonf)} 本 → " + ("・".join(f"{n} (p {p:.2g})" for n, p in bonf) if bonf else "なし"))
say(f"- BH(q=0.05) で残る: {len(bh)} 本 → " + ("・".join(f"{n} (p {p:.2g})" for n, p in bh) if bh else "なし"))
say("")
say(f"（実行 {time.time()-T0:.1f}s・seed {SEED}・B={NB}・perm 4000/cell）")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\n--> {OUT}")
