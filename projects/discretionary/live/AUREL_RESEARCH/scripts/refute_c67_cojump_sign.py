# -*- coding: utf-8 -*-
"""
[REFUTE c67 / 2026-11-25 03:40 反証レーン・A] 対象 = cycle67 が null 判定の脇に「得た新しい事実（記述）」として
肯定形で登記した主張 T2:
  「同一足共跳（株と金が同じ 5 分足で 4σ）の符号一致率は 在 2014-20 30%±4 (n 199) → 外 2021-26H1 78%±4 (n 189)
    ＝c20/c38 の 2020 符号レジーム反転が**裾で振幅最大**に出る。振幅は c20 の同時相関 +0.14 より桁違いに大きい」
および副題 T2b「在は共跳の 70% が反対方向（safe haven は裾で最も鮮明）」。

反証の筋（文章でなくコードで）: **「両脚が 4σ を超えた足だけを選ぶ」という条件付けは、線形相関 ρ がほぼ 0 でも
符号一致率を機械的に 0% か 100% に押しやる非線形レンズである。** 2 変量正規なら |x|=a, |y|=b を与えた時の
  同符号オッズ = exp(2ρab/(1−ρ²))  →  P(同符号) = sigmoid(2ρab/(1−ρ²))
共跳足は a·b ≈ 16〜25 なので ρ=±0.03 で既に 27%/73%、ρ=+0.10 で 96%。つまり 30%→78% の「桁違いの振幅」は
裾固有の情報ではなく **sign(ρ) をレンズで拡大した読み出し**である可能性がある。これを数値で詰める。

=== 事前固定（数字を見る前に書いた・この docstring が正本・seed 20261125） ===
データ・検出器・適格足・窓は c67 と**完全同一**（scripts/c67_crossasset_cojump_leadlag.py の load/E/z/ERAS を複製）。
  data/macro/XAU_m5_close.npz・US500_m5_close.npz・FOMC/CPI/NFP 暦。読取専用・MT5 なし・外部通信なし・発注なし。
u_X = r_X/σ_trail,X（符号付き標準化）・u_S 同様・z=|u|・θ=4（感度 3,5）。

R0 複製: c67 の N00（同一足共跳数）と符号一致率を再現する（在 199/30%・外 189/78%・θ=5 で 26%/77%）。
  再現しなければ以降は無効（**複製失敗 = 反証不能**として記録する）。
R2a ρ の測定: 窓別に ρ_all（全適格足）・**ρ_core（両脚 |u|<θ＝ジャンプ足を除く＝予測に共跳自身を使わない）**・
  ρ_wins3（|u| を 3 で winsorize）・局所ボラ状態 decile 別 ρ（共有状態 v_t = (RMS(r_X,直前12)/σ_X + RMS(r_S,直前12)/σ_S)/2
  の decile・ジャンプ足除外）。共跳足が住む decile を印字し、その decile の ρ も レンズ入力に使う（「ストレス時に相関が上がる」
  という対立仮説を潰すため）。
R2b レンズ予測: 観測された共跳足の (a_i,b_i)=(|u_X|,|u_S|) をそのまま使い、予測同符号数 = Σ_i sigmoid(2ρ a_i b_i/(1−ρ²))。
  ρ = ρ_core と ρ_decile。観測同符号数と比較。**逆レンズ**: 観測を再現する ρ* を二分法で解き、ρ* と ρ_core/ρ_decile を比較。
R2c θ 曲線: θ∈{1,1.5,2,3,4,5} で 観測一致率 vs ρ_core レンズ予測。両者が並走すれば機構＝レンズ。
R3a クラスタ: 共跳は日内クラスタする（c67 の ±4 は二項 SE＝独立 199 仮定）。**ET 日クラスタ bootstrap B=2000**で
  一致率の se を取り、二項 se との比（= √(design effect)）を印字。
R3b decluster（コスト倍の代わりの独立性ストレス）: 共跳を「同一 ET 日で最初の 1 本」「12 足(1h)窓で最初の 1 本」に
  間引いて一致率を再計算。
R3c 年別一致率＋BH 補正（15 セル）・2020 を落とした在・在外境界の感度（split 2020/2021/2022）。
R3d 衛生/サバイバーシップ: US500 npz 欠落日 129 日・XAU 穴 23 日の年別分布と、欠落日の XAU 日次 |r|（欠落日 vs 採用日・
  Welch t）。欠落が高ボラ日に偏れば共跳標本は生存バイアス。

判定規則（事前固定・これで T2 を壊す/残す）:
  **T2 broken（＝「裾固有の符号レジーム」ではなく ρ のレンズ読み出し）** ⇔ 在・外の両窓で
     |観測一致率 − ρ_core レンズ予測| < 2·se_cluster  かつ  ρ*_implied が ρ_core と ρ_decile の範囲に入る
     かつ θ 曲線が単調に並走（観測と予測の差が全 θ で 2·se_cluster 未満）。
  **T2 survived** ⇔ どちらかの窓で 観測 − 予測 が +2·se_cluster を超える（裾に余剰の同符号依存がある）。
  **inconclusive** ⇔ 上記いずれでもない／複製失敗／se_cluster が大きすぎて MDE（= 2·se_cluster）が 20 ポイント超。
  なお「共跳の**個数**超過（ρ0 7.6/4.5）」は本スクリプトの反証対象ではない（そちらは共有ボラ状態で c47/c48 と整合・
  レンズは個数を説明しない）。壊しに行くのは**符号**の主張だけ。これは明示的に書いておく。
出力 data/refute_c67_cojump_sign.md ＋ 同名 _run.log。書込は AUREL_RESEARCH/ 配下のみ。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c67_cojump_sign.md"); LOG = os.path.join(DATA, "refute_c67_cojump_sign_run.log"); L = []
NY = "America/New_York"; SEED = 20261125; rng = np.random.default_rng(SEED)
W_SIG = 5520; THETA = 4.0; B_BOOT = 2000
ERAS = [("在 2014-20", 2014, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def say(s=""):
    print(s, flush=True); L.append(s)
def el(): return f"{time.time()-T0:.1f}s"

say(f"# AUREL [REFUTE c67-A] 共跳の符号一致率は「裾の情報」か「ρ のレンズ」か  {dt.datetime.now():%Y-%m-%d %H:%M}")
say(f"- 事前固定 = docstring・seed {SEED}・検出器/適格足/窓は c67 と同一・読取専用")

# ---------- 暦（c67 と同一） ----------
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
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); FOMC_ALL = pd.DatetimeIndex(pd.to_datetime(F["date"]))
CPI = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date))
NFP = nfp_dates_v2()
evdays = pd.DatetimeIndex(sorted(set(list(NFP.normalize()) + list(FOMC_ALL.normalize()) + list(CPI.normalize()))))

# ---------- npz（c67 と同一） ----------
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    r = np.r_[np.nan, np.diff(np.log(cl))] * 1e4
    nf = np.isfinite(r) & (r != 0)
    r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
    idx = np.arange(len(ts)); lo = idx - 1 - W_SIG; hi = idx - 1; valid = lo >= 0
    S2 = np.where(valid, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
    NN = np.where(valid, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
    sig = np.sqrt(np.where(NN >= 1000, S2 / np.maximum(NN, 1), np.nan))
    nf3 = nf.copy()
    for k in (1, 2, 3): nf3 &= np.r_[[False] * k, nf[:-k]]
    return ts, r, nf, nf3, sig
tsX, rX, nfX, nf3X, sigX = load("XAU"); tsS, rS, nfS, nf3S, sigS = load("US500")
tsX_set_n, tsS_n = len(tsX), len(tsS)
ts, iX, iS = np.intersect1d(tsX, tsS, assume_unique=True, return_indices=True)
# 衛生: 落ちた日（R3d 用）
dropX = np.setdiff1d(tsX, ts); dropS = np.setdiff1d(tsS, ts)
rX_full, sigX_full, nfX_full = rX.copy(), sigX.copy(), nfX.copy()  # 欠落日の XAU 日次 |r| に使う
rX, nfX, nf3X, sigX = rX[iX], nfX[iX], nf3X[iX], sigX[iX]; rS, nfS, nf3S, sigS = rS[iS], nfS[iS], nf3S[iS], sigS[iS]
N = len(ts)
tt = pd.to_datetime(ts, unit="s", utc=True); tny = tt.tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); wd = tny.weekday.to_numpy(); yr = tny.year.to_numpy()
etdate = pd.DatetimeIndex(tny.tz_localize(None).normalize()); isev = np.asarray(etdate.isin(evdays))
dayid = etdate.to_numpy().astype("datetime64[D]").astype(np.int64)
assert len(np.unique(dayid)) > 1000, "dayid 退化"
slot = (hr * 12 + mn // 5).astype(np.int64)
trading = (wd <= 4) & ~(hr == 17) & ~((hr == 18) & (mn < 10))
E = nf3X & nf3S & np.isfinite(sigX) & np.isfinite(sigS) & trading & ~isev
uX = rX / sigX; uS = rS / sigS          # 符号付き標準化
zX = np.abs(uX); zS = np.abs(uS)
say(f"- 共通格子 {N} 本・適格足 E {int(E.sum())}・XAU 単独 {tsX_set_n}／US500 単独 {tsS_n}  ({el()})")

def era_mask(lo_, hi_): return (yr >= lo_) & (yr <= hi_)

# 共有ボラ状態 v_t（直前 12 足 RMS / σ_trail・両銘柄平均・足自身を含まない＝look-ahead なし）
def short_rms(r, nf, w=12):
    r2 = np.where(nf, r * r, 0.0); c2 = np.cumsum(r2); cn = np.cumsum(nf.astype(np.int64))
    idx = np.arange(len(r)); lo = idx - 1 - w; hi = idx - 1; ok = lo >= 0
    S2 = np.where(ok, c2[np.clip(hi, 0, None)] - c2[np.clip(lo, 0, None)], np.nan)
    NN = np.where(ok, cn[np.clip(hi, 0, None)] - cn[np.clip(lo, 0, None)], 0)
    return np.sqrt(np.where(NN >= 6, S2 / np.maximum(NN, 1), np.nan))
vX = short_rms(rX, nfX) / sigX; vS = short_rms(rS, nfS) / sigS
vmix = (vX + vS) / 2.0

# ---------- R0 複製 ----------
say("\n## R0 複製（c67 の数字が出るか）")
say("| 窓 | θ | 適格足 | 金 J | 株 J | 同一足共跳 n | 符号一致率（c67 式） | c67 の値 |")
say("|---|---|---|---|---|---|---|---|")
C67 = {("在 2014-20", 4.0): "30% (n 199)", ("外 2021-26H1", 4.0): "78% (n 189)", ("近年 2024-26H1", 4.0): "80%",
       ("在 2014-20", 5.0): "26%", ("外 2021-26H1", 5.0): "77%", ("近年 2024-26H1", 5.0): "70%"}
REP = {}
for th in (4.0, 5.0):
    for name, lo_, hi_ in ERAS:
        bm = era_mask(lo_, hi_) & E
        co = bm & (zX >= th) & (zS >= th)
        ag = (np.sign(rX[co]) == np.sign(rS[co])).mean() if co.sum() else np.nan
        REP[(name, th)] = (int(co.sum()), ag)
        say(f"| {name} | {th:g} | {int(bm.sum())} | {int((bm&(zX>=th)).sum())} | {int((bm&(zS>=th)).sum())} | {int(co.sum())} | "
            f"{ag*100:.0f}% | {C67.get((name,th),'—')} |")
rep_ok = (REP[("在 2014-20", 4.0)][0] == 199 and REP[("外 2021-26H1", 4.0)][0] == 189
          and abs(REP[("在 2014-20", 4.0)][1] - 0.30) < 0.015 and abs(REP[("外 2021-26H1", 4.0)][1] - 0.78) < 0.015)
say(f"- **複製 {'OK' if rep_ok else 'NG（以降は inconclusive 扱い）'}**  ({el()})")

# ---------- R2a ρ の測定 ----------
def pear(a, b, m):
    x = a[m]; y = b[m]; k = np.isfinite(x) & np.isfinite(y); x, y = x[k], y[k]
    if len(x) < 100: return np.nan, len(x)
    return float(np.corrcoef(x, y)[0, 1]), len(x)
say("\n## R2a 窓別の線形相関 ρ（5 分・標準化 u）— レンズの入力")
say("| 窓 | ρ_all (n) | **ρ_core: 両脚 \\|u\\|<4 (n)** | ρ_wins3 | ρ 最上位 vmix decile（ジャンプ除外） | 共跳足の vmix decile 中央 |")
say("|---|---|---|---|---|---|")
RHO = {}
for name, lo_, hi_ in ERAS:
    m = era_mask(lo_, hi_) & E
    r_all, n_all = pear(uX, uS, m)
    core = m & (zX < THETA) & (zS < THETA)
    r_core, n_core = pear(uX, uS, core)
    wx = np.clip(uX, -3, 3); ws = np.clip(uS, -3, 3)
    r_w, _ = pear(wx, ws, m)
    # vmix decile（ジャンプ足を除いた適格足で切る）
    vv = vmix[core]; vv = vv[np.isfinite(vv)]
    if len(vv) > 1000:
        qs = np.nanquantile(vv, np.linspace(0, 1, 11))
        dec = np.clip(np.searchsorted(qs[1:-1], vmix, side="right"), 0, 9)
        r_top, n_top = pear(uX, uS, core & (dec == 9))
        co = m & (zX >= THETA) & (zS >= THETA)
        co_dec = int(np.nanmedian(dec[co])) if co.sum() else -1
        r_codec, n_codec = pear(uX, uS, core & (dec == co_dec)) if co_dec >= 0 else (np.nan, 0)
    else:
        r_top, n_top, co_dec, r_codec, n_codec = np.nan, 0, -1, np.nan, 0
    RHO[name] = dict(all=r_all, core=r_core, wins=r_w, top=r_top, codec=r_codec, co_dec=co_dec)
    say(f"| {name} | {r_all:+.4f} ({n_all}) | **{r_core:+.4f} ({n_core})** | {r_w:+.4f} | {r_top:+.4f} (n {n_top}) | "
        f"decile {co_dec}（その decile の ρ {r_codec:+.4f}・n {n_codec}） |")

# ---------- レンズ ----------
def lens_p(rho, a, b):
    """2 変量正規: P(同符号 | |x|=a,|y|=b) = sigmoid(2ρab/(1−ρ²))"""
    x = 2.0 * rho * a * b / (1.0 - rho * rho)
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))
def implied_rho(a, b, obs_frac):
    """観測一致率を再現する ρ*（二分法・単調）"""
    lo_, hi_ = -0.98, 0.98
    for _ in range(200):
        mid = (lo_ + hi_) / 2
        if lens_p(mid, a, b).mean() < obs_frac: lo_ = mid
        else: hi_ = mid
    return (lo_ + hi_) / 2

def cluster_boot_frac(same, days, B=B_BOOT):
    """ET 日クラスタ bootstrap（共跳を含む日を再抽出）→ 一致率の se"""
    d = np.unique(days); nd = len(d); g = np.searchsorted(d, days)
    S = np.bincount(g, weights=same.astype(float), minlength=nd); Ncl = np.bincount(g, minlength=nd).astype(float)
    out = np.empty(B)
    for i in range(B):
        w = np.bincount(rng.integers(0, nd, nd), minlength=nd).astype(float)
        den = w @ Ncl; out[i] = (w @ S) / den if den > 0 else np.nan
    return float(np.nanstd(out, ddof=1)), nd

say("\n## R2b レンズ予測 vs 観測（θ=4・共跳足の実際の (a,b) を使用）")
say("| 窓 | n 共跳 | 日クラスタ nd | a·b 中央 | **観測 同符号率 (日クラスタ se)** | 二項 se | 設計効果 √DE | "
    "ρ_core レンズ予測 | ρ_codec レンズ予測 | **ρ\\*_implied** | 観測−予測(core) / 2se |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
R2B = {}
for name, lo_, hi_ in ERAS:
    m = era_mask(lo_, hi_) & E
    co = m & (zX >= THETA) & (zS >= THETA)
    a = zX[co]; b = zS[co]; same = (np.sign(rX[co]) == np.sign(rS[co]))
    obs = same.mean(); n = len(a)
    se_cl, nd = cluster_boot_frac(same, dayid[co])
    se_bin = math.sqrt(obs * (1 - obs) / n)
    p_core = lens_p(RHO[name]["core"], a, b).mean()
    p_codec = lens_p(RHO[name]["codec"], a, b).mean() if np.isfinite(RHO[name]["codec"]) else np.nan
    rstar = implied_rho(a, b, obs)
    gap = (obs - p_core) / (2 * se_cl) if se_cl > 0 else np.nan
    R2B[name] = dict(n=n, nd=nd, obs=obs, se_cl=se_cl, se_bin=se_bin, p_core=p_core, p_codec=p_codec, rstar=rstar, gap=gap)
    say(f"| {name} | {n} | {nd} | {np.median(a*b):.1f} | **{obs*100:.1f}% (±{se_cl*100:.1f})** | ±{se_bin*100:.1f} | "
        f"{se_cl/se_bin:.2f} | {p_core*100:.1f}% | {p_codec*100:.1f}% | **{rstar:+.4f}** | {gap:+.2f} |")

say("\n## R2c θ 曲線: 観測一致率 vs ρ_core レンズ予測（並走すれば機構＝レンズ）")
say("| 窓 | θ | n | 観測 | 予測(ρ_core) | 差/2se_cl |")
say("|---|---|---|---|---|---|")
THCURVE = {}
for name, lo_, hi_ in ERAS[:2]:
    m = era_mask(lo_, hi_) & E
    for th in (1.0, 1.5, 2.0, 3.0, 4.0, 5.0):
        co = m & (zX >= th) & (zS >= th)
        if co.sum() < 30: say(f"| {name} | {th:g} | {int(co.sum())} | — | — | — |"); continue
        a = zX[co]; b = zS[co]; same = (np.sign(rX[co]) == np.sign(rS[co])); obs = same.mean()
        se_cl, nd = cluster_boot_frac(same, dayid[co], B=600)
        p = lens_p(RHO[name]["core"], a, b).mean()
        d = (obs - p) / (2 * se_cl) if se_cl > 0 else np.nan
        THCURVE[(name, th)] = (obs, p, se_cl, int(co.sum()))
        say(f"| {name} | {th:g} | {int(co.sum())} | {obs*100:.1f}% (±{se_cl*100:.1f}) | {p*100:.1f}% | {d:+.2f} |")

# ---------- R3b decluster ----------
say("\n## R3b decluster（独立性ストレス）: 共跳を 1 日 1 本 / 1 時間 1 本に間引く")
say("| 窓 | 生 n (一致率) | 1 日 1 本 n (一致率) | 12 足 1 本 n (一致率) |")
say("|---|---|---|---|")
for name, lo_, hi_ in ERAS[:2]:
    m = era_mask(lo_, hi_) & E
    co = np.where(m & (zX >= THETA) & (zS >= THETA))[0]
    same = (np.sign(rX[co]) == np.sign(rS[co]))
    # 1 日 1 本
    _, first_d = np.unique(dayid[co], return_index=True)
    # 12 足窓で最初の 1 本（貪欲）
    keep = []; last = -10**9
    for i, ix in enumerate(co):
        if ix - last >= 12: keep.append(i); last = ix
    keep = np.array(keep, dtype=int)
    say(f"| {name} | {len(co)} ({same.mean()*100:.1f}%) | {len(first_d)} ({same[first_d].mean()*100:.1f}%) | "
        f"{len(keep)} ({same[keep].mean()*100:.1f}%) |")

# ---------- R3c 年別＋BH・2020 除外・境界感度 ----------
say("\n## R3c 年別一致率（θ=4）・50% からの二項 z・BH(15 セル)・ρ_core(年)")
rows = []
pv = []; ynames = []
for y in range(2012, 2027):
    m = (yr == y) & E
    co = m & (zX >= THETA) & (zS >= THETA)
    n = int(co.sum())
    if n == 0: rows.append(f"{y}: n 0"); continue
    same = (np.sign(rX[co]) == np.sign(rS[co])); p = same.mean()
    z = (p - 0.5) / math.sqrt(0.25 / n)
    core = m & (zX < THETA) & (zS < THETA); rc, _ = pear(uX, uS, core)
    rows.append(f"{y}: n {n} 一致 {p*100:.0f}% (z {z:+.1f}) ρ_core {rc:+.3f}")
    pv.append(math.erfc(abs(z) / math.sqrt(2))); ynames.append(y)
say("- " + " ／ ".join(rows))
if pv:
    pv = np.array(pv); o = np.argsort(pv); mtot = len(pv)
    bh = pv[o] * mtot / (np.arange(mtot) + 1)
    bh = np.minimum.accumulate(bh[::-1])[::-1]
    sig = [f"{ynames[o[i]]} q {bh[i]:.3g}" for i in range(mtot) if bh[i] < 0.05]
    say(f"- BH(q<0.05) で 50% と差がある年: {', '.join(sig) if sig else 'なし'}（{mtot} セル）")
say("\n## R3c-2 2020 の寄与と在外境界の感度")
say("| 定義 | n | 一致率 (日クラスタ se) | ρ_core |")
say("|---|---|---|---|")
for lab, m0 in (("在 2014-20（c67）", era_mask(2014, 2020)), ("在 2014-19（2020 除外）", era_mask(2014, 2019)),
                ("2020 のみ", era_mask(2020, 2020)), ("外 2021-26H1（c67）", era_mask(2021, 2026)),
                ("2021-22 のみ", era_mask(2021, 2022)), ("2023-26H1", era_mask(2023, 2026)),
                ("split 2020 前（2014-19）", era_mask(2014, 2019)), ("split 2020 後（2020-26）", era_mask(2020, 2026))):
    m = m0 & E; co = m & (zX >= THETA) & (zS >= THETA)
    if co.sum() < 10: say(f"| {lab} | {int(co.sum())} | — | — |"); continue
    same = (np.sign(rX[co]) == np.sign(rS[co])); se_cl, nd = cluster_boot_frac(same, dayid[co], B=600)
    core = m & (zX < THETA) & (zS < THETA); rc, _ = pear(uX, uS, core)
    say(f"| {lab} | {int(co.sum())} | {same.mean()*100:.1f}% (±{se_cl*100:.1f}・nd {nd}) | {rc:+.4f} |")

# ---------- R3d 衛生・サバイバーシップ ----------
say("\n## R3d 衛生: 共通格子から落ちた足の年別分布と、落ちた日の XAU ボラ（生存バイアス）")
def yearcount(tsarr):
    if len(tsarr) == 0: return "なし"
    d = pd.to_datetime(tsarr, unit="s", utc=True).tz_convert(NY)
    vc = pd.Series(d.year).value_counts().sort_index()
    return " ".join(f"{k}:{v}" for k, v in vc.items())
say(f"- US500 側に無く落ちた XAU 足 {len(dropX)}: {yearcount(dropX)}")
say(f"- XAU 側に無く落ちた US500 足 {len(dropS)}: {yearcount(dropS)}")
# 落ちた日（XAU 側）の日次 |r| 合計 vs 採用日
dX = pd.to_datetime(tsX, unit="s", utc=True).tz_convert(NY)
dayX = pd.DatetimeIndex(dX.tz_localize(None).normalize()).to_numpy().astype("datetime64[D]").astype(np.int64)
absr = np.where(nfX_full, np.abs(rX_full), 0.0)
dfv = pd.DataFrame({"d": dayX, "a": absr, "nf": nfX_full.astype(int)}).groupby("d").agg(s=("a", "sum"), k=("nf", "sum"))
dfv = dfv[dfv["k"] >= 50]
dropdays = set(pd.DatetimeIndex(pd.to_datetime(dropX, unit="s", utc=True).tz_convert(NY).tz_localize(None).normalize())
               .to_numpy().astype("datetime64[D]").astype(np.int64).tolist()) if len(dropX) else set()
isdrop = np.array([d in dropdays for d in dfv.index.to_numpy()])
if isdrop.sum() >= 5:
    x1 = dfv["s"].to_numpy()[isdrop]; x0 = dfv["s"].to_numpy()[~isdrop]
    tstat = (x1.mean() - x0.mean()) / math.sqrt(x1.var(ddof=1) / len(x1) + x0.var(ddof=1) / len(x0))
    say(f"- 落ちた日の XAU 日次 Σ|r| 平均 {x1.mean():.0f} bp (n {len(x1)}) vs 採用日 {x0.mean():.0f} bp (n {len(x0)})・Welch t {tstat:+.2f}")
else:
    say(f"- 落ちた日の判定に足る日数なし（drop 日 {int(isdrop.sum())}）")

# ---------- 判定 ----------
say("\n## 判定（事前固定の規則）")
a_, b_ = R2B["在 2014-20"], R2B["外 2021-26H1"]
cond_gap = (abs(a_["obs"] - a_["p_core"]) < 2 * a_["se_cl"]) and (abs(b_["obs"] - b_["p_core"]) < 2 * b_["se_cl"])
def inrange(rs, rc, rd):
    lo_, hi_ = (min(rc, rd), max(rc, rd)) if np.isfinite(rd) else (rc, rc)
    pad = 0.02
    return (lo_ - pad) <= rs <= (hi_ + pad)
cond_rho = inrange(a_["rstar"], RHO["在 2014-20"]["core"], RHO["在 2014-20"]["codec"]) and \
           inrange(b_["rstar"], RHO["外 2021-26H1"]["core"], RHO["外 2021-26H1"]["codec"])
curve_ok = all(abs(v[0] - v[1]) < 2 * v[2] for k, v in THCURVE.items())
mde_ok = (2 * a_["se_cl"] < 0.20) and (2 * b_["se_cl"] < 0.20)
say(f"- 複製: {'OK' if rep_ok else 'NG'}／レンズ差 2se 以内: {cond_gap}／ρ* が ρ_core〜ρ_codec 帯内: {cond_rho}"
    f"／θ 曲線 並走: {curve_ok}／MDE(2se_cl) < 20pt: {mde_ok}")
if not rep_ok or not mde_ok:
    verdict = "inconclusive"
elif cond_gap and cond_rho:
    verdict = "**T2 broken**（符号一致率は裾固有の情報でなく ρ の符号を a·b≈%.0f のレンズで拡大した読み出し）" % np.median(zX[E & (zX >= THETA) & (zS >= THETA)] * zS[E & (zX >= THETA) & (zS >= THETA)])
elif (a_["obs"] - a_["p_core"]) > 2 * a_["se_cl"] or (b_["obs"] - b_["p_core"]) > 2 * b_["se_cl"]:
    verdict = "**T2 survived**（レンズでは説明できない余剰の同符号依存が裾にある）"
else:
    verdict = "inconclusive"
say(f"- **結論: {verdict}**")
say(f"- 反証対象外として明示: 共跳の**個数**超過（c67 の ρ0 7.6/4.5）は本テストでは壊していない。レンズは個数を説明しない。")
say(f"\n- 実行 {el()}・読取専用・発注/本番編集/MT5/外部通信/プロップ参照 なし・書込は AUREL_RESEARCH/data 配下のみ")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); open(LOG, "w", encoding="utf-8").write("\n".join(L) + "\n")
