# -*- coding: utf-8 -*-
"""
[cycle69 研究レーン 2026-11-25] 【探索・マイクロストラクチャー／流動性供給リターン（自然実験: 米国祝日の“薄い”金セッション）】
源泉（憲章 3 条）: 流動性供給者（ディーラー・HFT）は在庫リスクの対価として短期の平均回帰（負の自己相関）を受け取る（Nagel 2012 "Evaporating
liquidity"・Grossman–Miller 1988）。供給の対価は**需要側の参加者が減って板が薄い時**に上がる（流動性プレミアムの時間変動）。金 CFD は米国祝日
（MLK・大統領の日・戦没者追悼・ジューンティーンス 2022+・独立記念日・労働者の日・感謝祭）に**取引されるが米株・米債の参加者が居ない**
（NYSE 休場・SIFMA 休場・COMEX は短縮）＝「同じ資産・同じ時計・参加者だけ抜ける」自然実験。c21 の「流動性プレミアム 済 部分」・c60 の
「流動性ジャンプの反転 underpowered」に対し、ジャンプを待たず**制度的に薄い日を外生的に選ぶ**ことで識別する（§8 新行）。
入口フィルタではない・本番とは独立の市場記述。既存キャッシュのみ（XAU_m5_close.npz・US500_m5_close.npz・暦 csv・refute_c4 json）・
scan 無し・M5 読込なし・MT5 無し・外部通信無し。

=== 事前固定（この docstring を書いてから数字を見る）===
暦（ET 暦日・規則導出・c30 の HOL 関数と同じ規則）:
  THIN（主・米株＋米債 休場・金 取引あり）= MLK 1 月第 3 月／大統領の日 2 月第 3 月／戦没者追悼 5 月最終月／ジューンティーンス 6/19 observed（2022+）／
    独立記念日 7/4 observed（土→金・日→月）／労働者の日 9 月第 1 月／感謝祭 11 月第 4 木。
  FULL（金の配信も止まる疑い・除外・flat 比率だけ印字）= 元日（日→月のみ）／聖金曜日／クリスマス observed。
  BOND（勾配腕・記述: NYSE 開・SIFMA 休）= コロンブス 10 月第 2 月／退役軍人 11/11 observed。
  HALF（勾配腕・記述: NYSE 13:00 ET 早引け）= 感謝祭翌日／7/3（平日 ∧ 非 HOL）／12/24（平日 ∧ 非 HOL）。窓は AFT 13:00→16:00 ET。
  暦の陽性対照 = THIN 日の US500 CASH 09:30→16:00 ET 非 flat 比率（2012+）が ≤0.2（NYSE 休場の確認）。>10% の日が破れば暦は疑う（判定を void）。
  金の適格 = 窓の非 flat 比率 ≥0.5（配信がある）。NFP/FOMC/CPI 日は THIN からも対照からも除外。
窓（ET・5 分 bid close の対数差・bp）: **TW = 08:00→13:00（60 本・主）**＝米国朝〜COMEX 早引け前。**PL = 03:00→08:00（60 本・同日プラセボ）**＝ロンドンは開いており
  参加者は概ね居る → 差は立たないことが期待（立てば「祝日の日そのものの状態」であって参加者欠落ではない）。
対照 C = 同曜日 D±7/14/21/28 日（最大 8）∧ 非 HOL 全種 ∧ 非 NFP/FOMC/CPI ∧ 適格。ALL = 全平日 非事象 適格（背景）。
統計（群レベル・日クラスタ bootstrap B=2000・seed 20261125）: 日ごとに a_d=Σ_j r_j r_{j−1}（窓内の隣接対）・b_d=Σ r_j²・15 分集約（3 本和）の a15/b15・
  30 分和の v30=Σ R30²・契約回帰の π_d = mean(−sign(r_{j−1})·r_j)（r_{j−1}≠0）。群の ρ1 = Σa/Σb・ρ1_15 = Σa15/Σb15・VR6 = (Σv30/n30)/(6·Σb/n5)・
  π = mean_d π_d。差 D = HS − C（HS/C を独立に日再抽出）。log RV 比 = mean_d log b_d の差（Welch t）。
判定（在 2010-20 で決め 外 2021-26H1 で確認・近年 2024-26H1 は記述・D2）:
  PC（薄さの陽性対照）: TW の log RV 差 在 <0 ∧ t≤−2。不成立なら本件 void（薄くない）。
  H1（流動性供給 = 平均回帰の増加）PASS = D_ρ1(TW) 在 <0 ∧ z≤−2 ∧ 外 同符号 z≤−1.5。MDE = 2·se。
  H1 の読み分け（事前）: D_ρ1 が負でも ρ1_15・VR6 の差が 0 なら「気配レベルの人工物（bid フリッカー）」、VR6 差も負（z≤−1.5）なら「価格水準の平均回帰」。
  PL（プラセボ）: D_ρ1(PL) |z|<2 が期待。
  H2（経済）: π_HS（bp/本）が往復コスト（口座 0.16 USD ÷ 08:00 ET 価格・bp）を上回る在/外。事前の期待 = 上回らない（ρ1 −0.05 でも π ≈ 0.05·E|r| ≈ 0.3 bp < 0.5〜1.3 bp）。
  決着可能性（数字を見る前）: 在 THIN ≈ 65 日 × 59 対 ≈ 3800 対 → se(ρ1) ≈ 0.016・C ≈ 8 倍 → se(D) ≈ 0.018・MDE ≈ 0.036。c19 の全体 ρ1 −0.019（2014-20）に対し
    「薄い日は 2 倍以上負」級しか見えない。外は THIN ≈ 35 日 → MDE ≈ 0.05。
  勾配（記述）: BOND 腕（債券だけ休み）・HALF 腕（午後だけ薄い）・祝日種別 7 行・年別 D_ρ1 の符号。
ゲート ㉛（本番接続・在 2010-20 のみ印字）: scan 本（refute_c4）で建玉 entry_time が THIN 日の TW にある本 vs 対照日の TW にある本の Δμ(R*)・Welch・MDE・x0 look-ahead 対照。
  在 |Δμ| <0.048R → 決着不能・外は走らせない（期待: n ≈ 100〜200 で MDE ≈ 0.3R＝決着不能）。
事前の最重大反証: (1) **bid のみ**: 薄い日はベンダーの気配が広がり bid の往復（フリッカー）が負の ρ1 を作る → 流動性供給リターンと区別できない。15 分集約・VR6 で
  人工物の減衰を見る（人工物は 1/h で消える）が、完全な分離は XAU ask M1【要取得】。(2) 祝日は月曜に集中（7 種中 4 種）→ 同曜日対照で曜日は揃うが「連休明けの月曜」ではなく
  「連休の月曜」である点（週末 49 h ＋ 24 h の情報が再開に溜まる）は窓 TW（再開から 14 時間後）には薄い。(3) n 小（在 ≈65 日）・祝日種別で参加者欠落の程度が違う
  （感謝祭は欧州も薄い・MLK は欧州通常）。(4) 金は祝日に COMEX が 13:30 ET で早引け → TW の終端 13:00 で切るが「引け前の在庫調整」が窓内に入り得る。
昇格候補・入口/出口規則の提案ではない。seed 20261125。
"""
import os, time, math, json, datetime as dt
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c69_us_holiday_thin_session_result.md"); L = []
NY = "America/New_York"; SEED = 20261125; rng = np.random.default_rng(SEED); NB = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle69] 米国祝日の薄い金セッション（TW 08:00→13:00 ET）vs 同曜日対照 — 流動性供給リターン（ρ1・VR6・契約回帰 π）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c69_us_holiday_thin_session.py)")

WD = ['月','火','水','木','金','土','日']
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    r = np.zeros(len(cl)); r[1:] = np.diff(np.log(cl)) * 1e4; fl = r == 0; wd = t.weekday.to_numpy()
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%・曜日別 " + " ".join(f"{WD[w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
    return ts, cl, r
def epoch_et(dates, hour, minute, day_offset=0):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

# ---------------- 暦 ----------------
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d
THIN, FULL, BOND, HALF = {}, set(), set(), set()
for y in range(2010, 2027):
    THIN[nth_weekday(y, 1, 0, 3)] = "MLK"; THIN[nth_weekday(y, 2, 0, 3)] = "大統領"; THIN[last_weekday(y, 5, 0)] = "戦没者"
    if y >= 2022: THIN[observed(dt.date(y, 6, 19))] = "Juneteenth"
    THIN[observed(dt.date(y, 7, 4))] = "独立"; THIN[nth_weekday(y, 9, 0, 1)] = "労働者"; THIN[nth_weekday(y, 11, 3, 4)] = "感謝祭"
    for h in (observed(dt.date(y, 1, 1), sat_to_fri=False), easter(y) - dt.timedelta(days=2), observed(dt.date(y, 12, 25))):
        if h is not None: FULL.add(h)
    BOND.add(nth_weekday(y, 10, 0, 2)); BOND.add(observed(dt.date(y, 11, 11)))
    HALF.add(nth_weekday(y, 11, 3, 4) + dt.timedelta(days=1))
    for d in (dt.date(y, 7, 3), dt.date(y, 12, 24)):
        if d.weekday() < 5 and d not in FULL and d not in THIN: HALF.add(d)
HOL_ALL = set(THIN) | FULL | BOND | HALF
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
EV = set(d.date() for d in nfp_dates_v2()) | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")).date).dt.date) | set(pd.to_datetime(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date).dt.date)
say(f"- 暦: THIN {len(THIN)}（種別 " + "・".join(f"{k} {sum(1 for v in THIN.values() if v==k)}" for k in dict.fromkeys(THIN.values())) + f"）・FULL {len(FULL)}・BOND {len(BOND)}・HALF {len(HALF)}・事象日（NFP/FOMC/CPI）{len(EV)}（㉔ 年別 THIN " + " ".join(f"{y}:{sum(1 for d in THIN if d.year==y)}" for y in range(2010, 2027)) + "）")

# ---------------- 日 × 窓の行列 ----------------
dates = pd.date_range("2010-01-04", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]; N = len(dates)
ddate = np.array([d.date() for d in dates]); yr = dates.year.to_numpy(); wdy = dates.weekday.to_numpy()
def win_matrix(ts, r, h0, m0, h1, m1):
    """各日の ET [h0:m0, h1:m1) 開始足の r 行列（n 本 × N）。格子の穴/DST NaT は NaN 行。"""
    T0_ = epoch_et(dates, h0, m0); T1_ = epoch_et(dates, h1, m1); nb = int(round(np.nanmedian((T1_ - T0_) / 300)))
    M = np.full((N, nb), np.nan); ok = np.isfinite(T0_) & np.isfinite(T1_) & ((T1_ - T0_) == nb * 300)
    i0 = np.searchsorted(ts, T0_[ok].astype(np.int64)); i0 = np.clip(i0, 0, len(ts) - nb)
    good = (ts[i0] == T0_[ok].astype(np.int64)) & (ts[np.minimum(i0 + nb - 1, len(ts) - 1)] == T0_[ok].astype(np.int64) + (nb - 1) * 300)
    idx = i0[good][:, None] + np.arange(nb)[None, :]
    rows = np.where(ok)[0][good]; M[rows] = r[idx]
    return M, nb
tsX, clX, rX = load("XAU"); tsS, clS, rS = load("US500")
TW, nTW = win_matrix(tsX, rX, 8, 0, 13, 0); PL, nPL = win_matrix(tsX, rX, 3, 0, 8, 0); AFT, nAFT = win_matrix(tsX, rX, 13, 0, 16, 0)
CASH_S, nCS = win_matrix(tsS, rS, 9, 30, 16, 0)
p08 = np.full(N, np.nan); T08 = epoch_et(dates, 8, 0); okp = np.isfinite(T08); pos = np.clip(np.searchsorted(tsX, (T08[okp] - 300).astype(np.int64)), 0, len(tsX) - 1)
p08[okp] = np.where(tsX[pos] == (T08[okp] - 300).astype(np.int64), clX[pos], np.nan)
nf = lambda M: np.nanmean(M != 0, axis=1) if M.ndim == 2 else np.nan
nfTW = np.where(np.isfinite(TW).all(1), np.mean(TW != 0, axis=1), np.nan); nfPL = np.where(np.isfinite(PL).all(1), np.mean(PL != 0, axis=1), np.nan)
nfAFT = np.where(np.isfinite(AFT).all(1), np.mean(AFT != 0, axis=1), np.nan); nfCS = np.where(np.isfinite(CASH_S).all(1), np.mean(CASH_S != 0, axis=1), np.nan)
is_thin = np.array([d in THIN for d in ddate]); is_full = np.array([d in FULL for d in ddate]); is_bond = np.array([d in BOND for d in ddate]); is_half = np.array([d in HALF for d in ddate])
is_hol = np.array([d in HOL_ALL for d in ddate]); is_ev = np.array([d in EV for d in ddate])
say(f"- 日格子 {N} 平日（2010-01-04〜2026-06-30）・TW {nTW} 本／PL {nPL}／AFT {nAFT}／US500 CASH {nCS} 本・TW 行が揃った日 {np.isfinite(TW).all(1).sum()}（穴/DST で欠け {N-np.isfinite(TW).all(1).sum()}）")
say(f"- 配信の確認（金 窓の非 flat 比率 中央値）: 通常平日 TW {np.nanmedian(nfTW[~is_hol]):.3f}／PL {np.nanmedian(nfPL[~is_hol]):.3f}／AFT {np.nanmedian(nfAFT[~is_hol]):.3f}；THIN TW {np.nanmedian(nfTW[is_thin]):.3f}（p10 {np.nanquantile(nfTW[is_thin],0.1):.2f}）／AFT {np.nanmedian(nfAFT[is_thin]):.3f}；FULL TW {np.nanmedian(nfTW[is_full]):.3f}（除外の根拠）；BOND TW {np.nanmedian(nfTW[is_bond]):.3f}；HALF AFT {np.nanmedian(nfAFT[is_half]):.3f}")
# THIN の時刻別 flat（早引けの位置・記述）
m5 = np.array([d.year >= 2013 for d in ddate])
prof = np.nanmean((AFT[is_thin & m5] == 0), axis=0); say("- THIN 日の AFT 13:00→16:00 ET 足別 flat 比率（2013+・15 分ごと）: " + " ".join(f"{13+ (j*5)//60:02d}:{(j*5)%60:02d} {prof[j]*100:.0f}%" for j in range(0, nAFT, 3)))
# 暦の陽性対照（US500 CASH flat on THIN・2012+）
m12 = (yr >= 2012) & is_thin & np.isfinite(nfCS); bad = m12 & (nfCS > 0.2)
say(f"- 暦の陽性対照（US500 CASH 09:30→16:00 非 flat 比率 ≤0.2・2012+）: THIN {m12.sum()} 日中 破れ {bad.sum()}（{bad.sum()/max(m12.sum(),1)*100:.1f}%）" + ("" if bad.sum() == 0 else "・破れ日 " + " ".join(str(ddate[i]) for i in np.where(bad)[0][:12])) + f"；通常平日の非 flat 比率 中央値 {np.nanmedian(nfCS[(yr>=2012)&~is_hol]):.3f}・BOND 日 {np.nanmedian(nfCS[(yr>=2012)&is_bond]):.3f}（NYSE 開の確認）・HALF 日 {np.nanmedian(nfCS[(yr>=2012)&is_half]):.3f}")
CAL_OK = bad.sum() / max(m12.sum(), 1) <= 0.10

# ---------------- 群の構成 ----------------
elig = lambda nfw: np.isfinite(nfw) & (nfw >= 0.5)
def controls_for(i, elig_mask):
    out = []
    for k in (7, 14, 21, 28):
        for s in (-1, 1):
            j = i + s * (k // 7) * 5  # 同曜日 = 5 平日先
            if 0 <= j < N and ddate[j] == ddate[i] + dt.timedelta(days=s * k) and not is_hol[j] and not is_ev[j] and elig_mask[j]: out.append(j)
    return out
def groups(treat_mask, nfw):
    e = elig(nfw); hs = np.where(treat_mask & e & ~is_ev)[0]; cs = sorted(set(j for i in hs for j in controls_for(i, e)))
    allm = np.where(~is_hol & ~is_ev & e)[0]
    return hs, np.array(cs, int), allm

# ---------------- 統計 ----------------
def day_sums(M, rows):
    X = M[rows]; a = np.nansum(X[:, 1:] * X[:, :-1], axis=1); b = np.nansum(X[:, 1:] ** 2, axis=1)
    nb = X.shape[1]; k = nb // 3; X3 = X[:, :3 * k].reshape(len(rows), k, 3).sum(2); a15 = np.sum(X3[:, 1:] * X3[:, :-1], axis=1); b15 = np.sum(X3[:, 1:] ** 2, axis=1)
    k6 = nb // 6; X6 = X[:, :6 * k6].reshape(len(rows), k6, 6).sum(2); v30 = np.sum(X6 ** 2, axis=1); b5 = np.sum(X ** 2, axis=1)
    prev = X[:, :-1]; nxt = X[:, 1:]; mk = prev != 0; pi = np.where(mk.sum(1) > 0, np.sum(np.where(mk, -np.sign(prev) * nxt, 0), axis=1) / np.maximum(mk.sum(1), 1), np.nan)
    rv = np.sum(X ** 2, axis=1); mean = np.sum(X, axis=1)
    return dict(a=a, b=b, a15=a15, b15=b15, v30=v30, b5=b5, n30=k6, n5=nb, pi=pi, rv=rv, mean=mean, n=len(rows))
def ratios(S, idx=None):
    g = (lambda v: v if idx is None else v[idx])
    rho = g(S["a"]).sum() / g(S["b"]).sum(); rho15 = g(S["a15"]).sum() / g(S["b15"]).sum()
    vr6 = (g(S["v30"]).sum() / (len(g(S["v30"])) * S["n30"])) / (6 * g(S["b5"]).sum() / (len(g(S["b5"])) * S["n5"]))
    return rho, rho15, vr6, np.nanmean(g(S["pi"]))
def boot_diff(SH, SC):
    oh = np.array(ratios(SH)); oc = np.array(ratios(SC)); D = oh - oc
    ih = rng.integers(0, SH["n"], size=(NB, SH["n"])); ic = rng.integers(0, SC["n"], size=(NB, SC["n"]))
    bh = np.array([ratios(SH, ih[k]) for k in range(NB)]); bc = np.array([ratios(SC, ic[k]) for k in range(NB)])
    se = np.std(bh - bc, axis=0, ddof=1); se_h = np.std(bh, axis=0, ddof=1)
    return D, se, oh, oc, se_h
def welch(a, b):
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]; d_ = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d_, d_ / se, se
ERAS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
RES = {}
def run_arm(name, treat_mask, M, nfw, label_win):
    say(f"\n## {name}（窓 {label_win}）")
    hs_all, cs_all, all_all = groups(treat_mask, nfw)
    say(f"- 適格 処置日 {len(hs_all)}（候補 {int((treat_mask & ~is_ev).sum())}・非 flat<0.5 で落ち {int((treat_mask & ~is_ev).sum())-len(hs_all)}）・対照日 {len(cs_all)}（処置日あたり {len(cs_all)/max(len(hs_all),1):.1f}）・背景 ALL {len(all_all)}")
    say("\n| 期間 | n_HS/n_C | log RV 差 (Welch t) [PC] | ρ1 HS／C／ALL | **D_ρ1 (z・MDE)** | D_ρ1_15 分 (z) | VR6 HS／C | D_VR6 (z) | π_HS bp/本 (z)／π_C | 往復コスト bp（中央値） | 平均 bp/窓 HS／C |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    for lab, lo, hi in ERAS:
        hs = hs_all[(yr[hs_all] >= lo) & (yr[hs_all] <= hi)]; cs = cs_all[(yr[cs_all] >= lo) & (yr[cs_all] <= hi)]; al = all_all[(yr[all_all] >= lo) & (yr[all_all] <= hi)]
        if len(hs) < 5 or len(cs) < 10: say(f"| {lab} | {len(hs)}/{len(cs)} | n 不足 |"); continue
        SH, SC, SA = day_sums(M, hs), day_sums(M, cs), day_sums(M, al)
        D, se, oh, oc, se_h = boot_diff(SH, SC); ra = ratios(SA)
        lrv, tl, _ = welch(np.log(np.maximum(SH["rv"], 1e-9)), np.log(np.maximum(SC["rv"], 1e-9)))
        cost = np.nanmedian(0.16 / p08[hs] * 1e4)
        mh, th, _ = welch(SH["mean"], SC["mean"])
        RES[(name, lab)] = dict(n_hs=len(hs), n_c=len(cs), lrv=lrv, tl=tl, D=D, se=se, oh=oh, oc=oc, cost=cost, pi_z=oh[3] / se_h[3] if se_h[3] > 0 else np.nan, mean_d=mh, mean_t=th)
        say(f"| {lab} | {len(hs)}/{len(cs)} | {lrv:+.3f} (t {tl:+.2f}) | {oh[0]:+.3f}／{oc[0]:+.3f}／{ra[0]:+.3f} | **{D[0]:+.3f} (z {D[0]/se[0]:+.2f}・MDE {2*se[0]:.3f})** | {D[1]:+.3f} (z {D[1]/se[1]:+.2f}) | {oh[2]:.3f}／{oc[2]:.3f} | {D[2]:+.3f} (z {D[2]/se[2]:+.2f}) | {oh[3]:+.3f} (z {oh[3]/se_h[3]:+.2f})／{oc[3]:+.3f} | {cost:.2f} | {SH['mean'].mean():+.1f}／{SC['mean'].mean():+.1f} (t {th:+.2f}) |")
    return hs_all, cs_all

hsT, csT = run_arm("THIN（主・米株＋米債 休場）", is_thin, TW, nfTW, "TW 08:00→13:00 ET")
say("\n### 同日プラセボ窓 PL 03:00→08:00 ET（ロンドン時間・参加者は概ね居る → 差は立たないことが期待）")
hsP, csP = run_arm("THIN・プラセボ窓", is_thin, PL, nfPL, "PL 03:00→08:00 ET")
say("\n### 勾配腕（記述）")
run_arm("BOND（NYSE 開・SIFMA 休）", is_bond, TW, nfTW, "TW 08:00→13:00 ET")
run_arm("HALF（NYSE 13:00 早引け・午後）", is_half, AFT, nfAFT, "AFT 13:00→16:00 ET")

# ---------------- 祝日種別・年別（記述・THIN TW） ----------------
say("\n## 祝日種別（THIN・TW・全期間 2010-26H1・記述）")
say("| 種別 | n_HS | ρ1 HS | ρ1 C | D_ρ1 (z) | log RV 差 (t) | π_HS |"); say("|---|---|---|---|---|---|---|")
kinds = {}
for i in hsT: kinds.setdefault(THIN[ddate[i]], []).append(i)
e_tw = elig(nfTW)
for k, rows in kinds.items():
    rows = np.array(rows); cs = np.array(sorted(set(j for i in rows for j in controls_for(i, e_tw))), int)
    if len(rows) < 5: say(f"| {k} | {len(rows)} | n 不足 |"); continue
    SH, SC = day_sums(TW, rows), day_sums(TW, cs); D, se, oh, oc, _ = boot_diff(SH, SC); lrv, tl, _ = welch(np.log(SH["rv"]), np.log(SC["rv"]))
    say(f"| {k} | {len(rows)} | {oh[0]:+.3f} | {oc[0]:+.3f} | {D[0]:+.3f} (z {D[0]/se[0]:+.2f}) | {lrv:+.3f} (t {tl:+.2f}) | {oh[3]:+.3f} |")
say("- 年別 D_ρ1（THIN TW・HS − 同年の対照・点推定のみ）: " + " ".join(f"{y}:{(lambda h,c: f'{ratios(day_sums(TW,h))[0]-ratios(day_sums(TW,c))[0]:+.3f}' if len(h)>=3 and len(c)>=6 else '—')(hsT[yr[hsT]==y], csT[yr[csT]==y])}" for y in range(2010, 2027)))

# ---------------- ゲート ㉛ ----------------
say("\n## ゲート ㉛（本番接続・在 2010-20 のみ印字）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["ft"] = FT / tr["risk"]; tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]
et_ = tr["entry_time"].to_numpy(float); T0_tw = epoch_et(dates, 8, 0); T1_tw = epoch_et(dates, 13, 0)
pos = np.searchsorted(T0_tw, et_, side="right") - 1; pos = np.clip(pos, 0, N - 1); in_tw = (et_ >= T0_tw[pos]) & (et_ < T1_tw[pos])
day_of = np.where(in_tw, pos, -1); hs_set = set(hsT.tolist()); cs_set = set(csT.tolist())
tr["grp"] = ["HS" if dd in hs_set else ("C" if dd in cs_set else "") for dd in day_of]
ins = tr[(tr.grp != "") & (tr.year >= 2010) & (tr.year <= 2020)]; A, B = ins[ins.grp == "HS"], ins[ins.grp == "C"]
if len(A) >= 10 and len(B) >= 10:
    dm, tm, sem = welch(A.Rs.to_numpy(), B.Rs.to_numpy()); d0, t0, _ = welch(A.x0.to_numpy(float), B.x0.to_numpy(float))
    say(f"- 在 2010-20・TW 建玉の scan 本: THIN 日 {len(A)}（TP 率 {(A.exit=='TP').mean()*100:.0f}%）／対照日 {len(B)}（{(B.exit=='TP').mean()*100:.0f}%）・Δμ(R*) **{dm:+.3f}R (t {tm:+.2f}・MDE {2*sem:.3f})**・x0 look-ahead 対照 Δ {d0:+.3f} (t {t0:+.2f})")
    gate = "通過（外を印字）" if abs(dm) >= 0.048 else "**不通過（在 |Δμ| <0.048R → 決着不能・外は走らせない）**"
    if abs(dm) >= 0.048 and 2 * sem > 0.2: gate += "（ただし MDE >0.2R＝通過は雑音・決着不能）"
    say(f"- ゲート ㉛: {gate}")
    if abs(dm) >= 0.048:
        o = tr[(tr.grp != "") & (tr.year >= 2021)]; a_, b_ = o[o.grp == "HS"], o[o.grp == "C"]
        if len(a_) >= 10: dm2, tm2, se2 = welch(a_.Rs.to_numpy(), b_.Rs.to_numpy()); say(f"  - 外 2021-26H1: Δμ {dm2:+.3f}R (t {tm2:+.2f}・n {len(a_)}/{len(b_)}・MDE {2*se2:.3f})")
else: say(f"- 在 TW 建玉の scan 本 THIN {len(A)}／対照 {len(B)}＝母数不足（ゲート n/a）")

# ---------------- 判定 ----------------
say("\n## 判定（事前固定の規則で機械的に）")
nm = "THIN（主・米株＋米債 休場）"; I, O = RES.get((nm, "在 2010-20")), RES.get((nm, "外 2021-26H1")); P_I, P_O = RES.get(("THIN・プラセボ窓", "在 2010-20")), RES.get(("THIN・プラセボ窓", "外 2021-26H1"))
say(f"- 暦の陽性対照: {'OK' if CAL_OK else '**破れ >10% → void**'}")
pc = I is not None and I["lrv"] < 0 and I["tl"] <= -2
say(f"- PC（薄さ）: 在 log RV 差 {I['lrv']:+.3f} (t {I['tl']:+.2f}) → {'PASS（薄い）' if pc else '**FAIL → 本件 void（薄くない）**'}；外 {O['lrv']:+.3f} (t {O['tl']:+.2f})")
zi, zo = I["D"][0] / I["se"][0], O["D"][0] / O["se"][0]
h1 = pc and CAL_OK and I["D"][0] < 0 and zi <= -2 and O["D"][0] < 0 and zo <= -1.5
say(f"- H1（D_ρ1 TW）: 在 {I['D'][0]:+.3f} (z {zi:+.2f}・MDE {2*I['se'][0]:.3f})／外 {O['D'][0]:+.3f} (z {zo:+.2f}・MDE {2*O['se'][0]:.3f}) → **{'PASS' if h1 else 'FAIL → null'}**")
say(f"- 読み分け: D_ρ1_15 在 {I['D'][1]:+.3f} (z {I['D'][1]/I['se'][1]:+.2f})／外 {O['D'][1]:+.3f}・D_VR6 在 {I['D'][2]:+.3f} (z {I['D'][2]/I['se'][2]:+.2f})／外 {O['D'][2]:+.3f} (z {O['D'][2]/O['se'][2]:+.2f})")
if P_I is not None and P_O is not None: say(f"- プラセボ PL: 在 D_ρ1 {P_I['D'][0]:+.3f} (z {P_I['D'][0]/P_I['se'][0]:+.2f})／外 {P_O['D'][0]:+.3f} (z {P_O['D'][0]/P_O['se'][0]:+.2f})・PL の log RV 差 在 {P_I['lrv']:+.3f} (t {P_I['tl']:+.2f})／外 {P_O['lrv']:+.3f} (t {P_O['tl']:+.2f})")
say(f"- H2（経済）: π_HS 在 {I['oh'][3]:+.3f} bp/本 vs 往復コスト {I['cost']:.2f} bp／外 {O['oh'][3]:+.3f} vs {O['cost']:.2f} → {'受取り可の形' if (I['oh'][3] > I['cost'] and O['oh'][3] > O['cost']) else '**受取り不可**'}")
say(f"\n_実行 {time.time()-T0:.1f} s・seed {SEED}・NB {NB}_")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
