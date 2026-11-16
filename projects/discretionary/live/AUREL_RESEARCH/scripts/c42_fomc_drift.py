# -*- coding: utf-8 -*-
"""
[cycle42 研究レーン 2026-11-16] 【探索・マクロ発表（FOMC）＝収益機会の源泉マップ §8「マクロ発表（CPI/FOMC/入札）」行を 要取得 → 済 へ】
文献: Lucca & Moench (2015 JF) "The Pre-FOMC Announcement Drift" — 米株は**予定された FOMC 声明の前 24 時間（前日 14:00 ET → 声明 14:00 ET）に
平均 +49 bp**（1994-2011・年間株式プレミアムの約 8 割がこの 8 日に集中）・ボラは低い（calm before the storm）・債券/為替/金には無い（と報告）。
後続（Kurov et al. 2021・Cieslak–Morse–Vissing-Jorgensen 2019 "Stock returns over the FOMC cycle"）は 2011 以降の減衰を報告。
機構候補: ①発表前の不確実性プレミアムの解消（リスク負担の対価を前倒しで受け取る）②情報漏洩/先回り（Cieslak et al.）③流動性供給者の在庫調整。
金への含意（AI らしい角度）: 金は「安全資産」なら発表前のリスクプレミアム解消で**逆符号（または 0）**が予想される（文献: 金は無し）。
しかし c38（2021+ の金は極端日に株と同方向）が正しければ **2021+ の金は株と同符号の pre-FOMC drift を持つ**はず（H_FLIP 型の予測・c41 と同型）。
方法論 ㉝: 本拠（US500 bid M5）で先に当てる。入口フィルタではない・市場構造の記述。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/FOMC_dates.csv（本サイクル取得・federalreserve.gov・scheduled のみ主）・US500_m5_close.npz（2012-01〜2026-06-09・bid）・
  XAU_m5_close.npz（bid）・refute_c4 json（ゲート ㉛）・NFP 暦（c24 nfp_dates_v2 を複製）。scan 無し・M5 読込なし・MT5 無し。
**暦の妥当性検定（判定の前提・数字を見る前に規則）**: 2013-03-20 以降の声明日 D で |r(14:00→14:05 ET)| が同スロットの対照日 90% 点を超える率 J。
  US500 と XAU のどちらかで J ≥ 0.40 なら暦は正しいと見る（c24 の NFP は 58〜61%）。J < 0.40 → 暦が疑わしい＝全判定 void（走らせない）。
価格の時計: c40 と同じ P(T) = ts == T−300 の足の close（格子の穴は NaN・⑫）。取引日 D = ET 現地の月〜金。
窓（bp・対数差・ET）: **PRE = 前営業日 14:00 → D 12:00**（22 h・全年で声明時刻 12:30/14:00/14:15 のどれよりも前に終わる・主）
  PRE24 = 前営業日 14:00 → D 13:55（文献定義・2013-03-20 以降のみ・副）／JUMP = 14:00 → 14:05（暦検定）／J30 = 14:00 → 14:30／
  POST = 14:30 → 16:00（声明後の続き・2013-03-20 以降）／NEXT = 16:00 → 翌営業日 10:00（翌日持ち越し）／PLACEBO_MID = 前営業日 14:00 → 前営業日 16:00（声明 2 日前の午後＝被説明変数のプラセボではなく時刻対照）。
対照日: 同じ時代窓の平日 D で、FOMC 声明日でも その ±1 営業日でも NFP 日でもない日。**曜日一致**（声明日は水曜 9 割）: δ = mean_F(y) − Σ_w s_w·mean_{C,w}(y)（s_w = 声明日の曜日構成）・
  se² = var_F/n_F + Σ s_w² var_{C,w}/n_{C,w}（Welch 型）。有効日 = 窓が有限 ∧ 窓 ≠ 0（stale・祝日）。窓×時代の厳密 0 比率を印字（>20% は判定不可・㉒）。
置換帰無（⑨の暦版）: ①シフト・プラセボ = 声明日を ±7/±14/±21/±28 日ずらした 8 集合（同曜日・他の声明 ±1 日に重なる日は除く）の δ 分布、
  ②無作為 = 対照日から n_F 日を曜日構成を保って引く 2000 回 → 両側 p と帰無 sd。
窓: 在 2010-20（US500 は 2012-20）／外 2021-26H1／近年 2024-26H1（D2・窓別・16 年一括は使わない）。判定は在で決め外で確認。年別 δ も印字（記述）。
判定（Bonferroni(2)・名目 0.025・主 2 セル）:
  C1 US500（本拠）PASS = PRE δ>0 ∧ 在 t≥2 ∧ 無作為置換 p<0.025 ∧ 外 同符号 t≥1.5。
  C2 XAU（金・同じ PRE 窓）: H_SAFE（文献・安全資産）= 在 δ≤0 または |t|<2 かつ外も同様 → 「金には無い」（null の確認）；
     H_FLIP（c38 由来の予測）= 在 |t|<2 ∧ **外 δ>0 ∧ t≥2 ∧ p<0.025**（2021+ の金が株と同符号で立つ）；H_SAME = 在外とも δ>0 t≥2／1.5。
     **C1 が null なら C2 は記述のみ（㉝）**。
副（記述・判定に使わない）: ボラ比（PRE の |y| 中央値・分散 F/C・文献 calm）、POST 継続 β（POST on J30・HC1・MDE・c24 型）、NEXT on J30、年別 δ、PLACEBO_MID、unscheduled の別記。
決着可能性（㉝・数字を見る前）: 22 h 窓 sd ≈ US500 90〜110 bp／XAU 90〜100 bp。在 n_F ≈ US500 72（2012-20）／XAU 88（2010-20）→ se ≈ 11〜12 bp → 文献級 +49 bp は t ≈ 4〜4.5＝決着可能。
  半減した +25 bp は t ≈ 2.2（境界）・外 n_F ≈ 44 → se ≈ 15 bp＝外の確認は +25 bp で t 1.7＝「消えた／続く」は文献級でしか分離できない（㊳ の型）。
陽性対照: 在 US500 の声明日 PRE に +30 bp を注入して t が ≥2 増えること（検出力）。
経済的大きさ（事前）: δ bp/回 × 8 回/年 vs 往復コスト US500 0.4〜1 bp・金 0.16 USD ≈ 0.4〜0.9 bp・22 h 保有の swap 1 晩【要取得】。
ゲート ㉛（本番接続・在のみ印字）: scan 本（refute_c4）で建玉 entry_time が声明日 D の PRE 窓（前営業日 14:00 ET → D 12:00 ET）にある本 vs 他の本:
  Δμ(R*)・Δx（pp）・x0 look-ahead 対照・声明 14:00 ET を生きて跨ぐ本数。在 |Δμ|<0.048R → 「決着不能・外は走らせない」。
事前の最重大反証: (1) 文献効果は 1994-2011 に集中し 2011 以降減衰＝在 2012-20 で既に薄い可能性 → null は時代効果と読む（決着は文献級のみ）。
  (2) bid のみ・Dukascopy CFD（SPX 現物/ES ではない）・1 社。(3) US500 2020 夏 68 営業日欠落（㊵）＝2020 の声明 2 回が落ちる可能性。
  (4) 対照日に CPI/PCE 等の他発表が混在（暦【要取得】）＝δ は「FOMC 前 − 平均的な日」であって「FOMC 前 − 静かな日」ではない。
  (5) 声明時刻の年次差（12:30/14:15/14:00）＝PRE は 12:00 で終えて回避・POST/PRE24 は 2013-03-20 以降のみ。(6) 声明日は水曜に集中＝曜日一致で処理するが
  水曜固有の他の季節性（EIA 在庫 10:30 ET 等）は残る。(7) 多重: 主 2 セルのみ判定・副は記述。(8) 暦は Fed 公表ページの機械抽出＝J 検定で妥当性を確認。
  昇格候補・入口/出口規則の提案ではない。seed 20261116。
"""
import os, time, math, json
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c42_fomc_drift_result.md"); L = []
NY = "America/New_York"; SEED = 20261116; rng = np.random.default_rng(SEED); NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle42] FOMC 声明前ドリフト（Lucca–Moench 2015）US500 本拠 → 金 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c42_fomc_drift.py)")
WD = ['月','火','水','木','金','土','日']
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True); r = np.diff(np.log(cl)); fl = np.r_[False, r == 0]; wd = t.weekday.to_numpy()
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%・曜日別 " + " ".join(f"{WD[w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
    return ts, cl
def epoch_et(dates, hour, minute, day_offset=0):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT"); utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T); key = (T[ok] - 300).astype(np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1); out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)

# ---------- calendar ----------
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"])
FS = F[F.scheduled == 1]; FU = F[F.scheduled == 0]
say(f"- FOMC 暦: {len(F)} 行（scheduled {len(FS)}・unscheduled {len(FU)}）{F.date.min().date()}〜{F.date.max().date()}・年別 scheduled " + " ".join(f"{y}:{int((FS.date.dt.year==y).sum())}" for y in range(2010, 2027)))
say(f"- scheduled 声明日の曜日: " + " ".join(f"{WD[w]}{int((FS.date.dt.weekday==w).sum())}" for w in range(5)) + f"・unscheduled: {', '.join(d.strftime('%Y-%m-%d') for d in FU.date)}")
dates = pd.date_range("2010-01-04", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]; N = len(dates); yr = dates.year.to_numpy(); wdy = dates.weekday.to_numpy()
POST_OK = dates >= pd.Timestamp("2013-03-20")
isF = np.isin(dates, FS.date); isU = np.isin(dates, FU.date); isNFP = np.isin(dates, nfp_dates_v2())
nearF = isF.copy(); nearF[1:] |= isF[:-1]; nearF[:-1] |= isF[1:]   # ±1 weekday
isC = ~nearF & ~isU & ~isNFP
say(f"- 取引日候補 {N}・声明日 {isF.sum()}・対照候補 {isC.sum()}（声明 ±1 営業日・臨時・NFP を除く）")
lg = np.log
def windows(ts, cl):
    P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
    p14 = P(14, 0); p14_prev = np.r_[np.nan, p14[:-1]]; p16 = P(16, 0); p16_prev = np.r_[np.nan, p16[:-1]]; p10_next = np.r_[P(10, 0)[1:], np.nan]
    W = {}
    W["PRE"] = (lg(P(12, 0)) - lg(p14_prev)) * 1e4
    W["PRE24"] = (lg(P(13, 55)) - lg(p14_prev)) * 1e4
    W["JUMP"] = (lg(P(14, 5)) - lg(p14)) * 1e4
    W["J30"] = (lg(P(14, 30)) - lg(p14)) * 1e4
    W["POST"] = (lg(p16) - lg(P(14, 30))) * 1e4
    W["NEXT"] = (lg(p10_next) - lg(p16)) * 1e4
    W["PLACEBO_MID"] = (lg(p16_prev) - lg(p14_prev)) * 1e4
    return W
ERAS = {"US500": [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)],
        "XAU": [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]}

def wmatch(y, mF, mC):
    """weekday-matched mean difference F − C; Welch-type se; returns dict"""
    yF = y[mF]; yF = yF[np.isfinite(yF)]; nF = len(yF)
    if nF < 8: return dict(d=np.nan, t=np.nan, se=np.nan, nF=nF, nC=0, mF=np.nan, mC=np.nan)
    wF = wdy[mF][np.isfinite(y[mF])]; shares = np.array([(wF == w).mean() for w in range(5)])
    mu_c = 0.0; var_c = 0.0; nC = 0
    for w in range(5):
        if shares[w] == 0: continue
        yc = y[mC & (wdy == w)]; yc = yc[np.isfinite(yc)]
        if len(yc) < 5: return dict(d=np.nan, t=np.nan, se=np.nan, nF=nF, nC=0, mF=np.nan, mC=np.nan)
        mu_c += shares[w] * yc.mean(); var_c += shares[w] ** 2 * yc.var(ddof=1) / len(yc); nC += len(yc)
    d = yF.mean() - mu_c; se = math.sqrt(yF.var(ddof=1) / nF + var_c)
    return dict(d=d, t=d / se, se=se, nF=nF, nC=nC, mF=yF.mean(), mC=mu_c)
def perm_random(y, mF, mC, obs):
    """draw n_F control days preserving weekday composition, 2000x -> two-sided p, null sd"""
    wF = wdy[mF][np.isfinite(y[mF])]; cnt = [(wF == w).sum() for w in range(5)]
    pools = [np.where(mC & (wdy == w) & np.isfinite(y))[0] for w in range(5)]
    mu_c = sum((cnt[w] / len(wF)) * y[pools[w]].mean() for w in range(5) if cnt[w] > 0)
    out = np.empty(NPERM)
    for j in range(NPERM):
        pick = np.concatenate([rng.choice(pools[w], cnt[w], replace=False) for w in range(5) if cnt[w] > 0])
        out[j] = y[pick].mean() - mu_c
    return (np.abs(out) >= abs(obs)).mean(), out.std()
def shift_placebo(y, mF, mC):
    ds = []
    for k in (-28, -21, -14, -7, 7, 14, 21, 28):
        sh = np.zeros(N, bool); idx = np.where(mF)[0]
        shifted = dates[idx] + pd.Timedelta(days=k); pos = np.searchsorted(dates, shifted); pos = pos[(pos < N)]
        pos = pos[(dates[pos] == shifted[: len(pos)]) if len(pos) == len(shifted) else np.isin(dates[pos], shifted)]
        sh[pos] = True; sh &= isC  # must be clean control days
        o = wmatch(y, sh, mC & ~sh); ds.append(o["d"])
    ds = np.array(ds); return ds
def ols(y, x):
    m = np.isfinite(y) & np.isfinite(x); y, x = y[m], x[m]; n = len(y)
    if n < 20: return dict(n=n, b=np.nan, t=np.nan, se=np.nan)
    xc = x - x.mean(); yc = y - y.mean(); sxx = xc @ xc; b = (xc @ yc) / sxx; e = yc - b * xc
    se = math.sqrt((xc ** 2 @ e ** 2) / sxx ** 2 * n / (n - 2)); return dict(n=n, b=b, t=b / se, se=se)
def fo(o): return f"δ {o['d']:+.1f} bp (t {o['t']:+.2f}, se {o['se']:.1f}, MDE {2*o['se']:.1f}, nF {o['nF']}/nC {o['nC']})" if np.isfinite(o["d"]) else f"—(nF {o['nF']})"

RES = {}; WALL = {}
for sym in ("US500", "XAU"):
    say(f"\n## {sym}")
    ts, cl = load(sym); W = windows(ts, cl); WALL[sym] = W
    valid = np.isfinite(W["PRE"]) & (W["PRE"] != 0)
    say("- 窓の厳密 0 比率／NaN（候補日中・㉒）: " + "・".join(f"{k} {np.mean(np.isfinite(W[k]) & (W[k]==0))*100:.1f}%/{np.mean(~np.isfinite(W[k]))*100:.1f}%" for k in W))
    say(f"- 声明日のうち PRE 有効 {int((isF&valid).sum())}/{int(isF.sum())}・年別 " + " ".join(f"{y}:{int((isF&valid&(yr==y)).sum())}" for y in range(2010, 2027)))
    # --- calendar validity J ---
    vj = np.isfinite(W["JUMP"]) & POST_OK
    aj = np.abs(W["JUMP"]); q90 = np.nanquantile(aj[vj & isC], 0.90); J = np.mean(aj[vj & isF] > q90)
    med_f = np.nanmedian(aj[vj & isF]); med_c = np.nanmedian(aj[vj & isC])
    say(f"- **暦検定 J（2013-03-20 以降・|r 14:00→14:05|）**: 声明日 中央値 {med_f:.1f} bp vs 対照 {med_c:.1f}（比 {med_f/max(med_c,1e-9):.1f}）・対照 90% 点 {q90:.1f}・**J = {J:.2f}**（n {int((vj&isF).sum())}）・|J30| 中央値 {np.nanmedian(np.abs(W['J30'][vj&isF])):.1f} vs {np.nanmedian(np.abs(W['J30'][vj&isC])):.1f}")
    # non-jump days list (descriptive)
    nj = np.where(vj & isF & (aj <= q90))[0]
    say(f"  - J 不成立の声明日 {len(nj)}: " + ", ".join(dates[i].strftime('%Y-%m-%d') for i in nj[:40]) + (" …" if len(nj) > 40 else ""))
    # pre-2013 descriptive: which slot jumps
    v0 = np.isfinite(W["JUMP"]) & ~POST_OK & isF
    say(f"  - 2013-03-20 より前の声明日（記述）: |14:00→14:05| 中央値 {np.nanmedian(aj[v0]):.1f} bp（n {int(v0.sum())}）＝声明時刻が 12:30/14:15 の年は JUMP 窓では捕まらない（PRE は 12:00 で終える）")
    RES[(sym, "J")] = J
    say(f"\n| 期間 | PRE δ（主・曜日一致） | 無作為 p / 帰無 sd | シフト・プラセボ 8 集合 δ 平均±sd | PRE24（2013-03+） | PLACEBO_MID（2 日前 14→16 時） | 声明日 PRE \\|y\\| 中央値 / 対照（ボラ比） | 年別 δ |")
    say("|---|---|---|---|---|---|---|---|")
    for lab, lo, hi in ERAS[sym]:
        era = (yr >= lo) & (yr <= hi); mF = isF & era & valid; mC = isC & era & valid
        o = wmatch(W["PRE"], mF, mC)
        p, sdp = perm_random(W["PRE"], mF, mC, o["d"]) if np.isfinite(o["d"]) else (np.nan, np.nan)
        sp = shift_placebo(W["PRE"], mF, mC)
        v24 = np.isfinite(W["PRE24"]) & POST_OK; o24 = wmatch(W["PRE24"], isF & era & v24, isC & era & v24)
        vm = np.isfinite(W["PLACEBO_MID"]) & (W["PLACEBO_MID"] != 0); om = wmatch(W["PLACEBO_MID"], isF & era & vm, isC & era & vm)
        aF = np.nanmedian(np.abs(W["PRE"][mF])); aC = np.nanmedian(np.abs(W["PRE"][mC])); vr = np.nanvar(W["PRE"][mF]) / np.nanvar(W["PRE"][mC])
        yrs = " ".join(f"{y}:{wmatch(W['PRE'], isF&valid&(yr==y), isC&valid&(yr==y))['d']:+.0f}" for y in range(lo, hi + 1))
        RES[(sym, lab)] = dict(o=o, p=p, sdp=sdp, sp=sp)
        say(f"| {lab} | **{fo(o)}** | {p:.3f} / {sdp:.1f} | {np.nanmean(sp):+.1f}±{np.nanstd(sp):.1f} (max {np.nanmax(np.abs(sp)):.1f}) | {fo(o24)} | {fo(om)} | {aF:.0f} / {aC:.0f} bp（分散比 {vr:.2f}） | {yrs} |")
    # positive control
    lab0, lo, hi = ERAS[sym][0]; era = (yr >= lo) & (yr <= hi); mF = isF & era & valid; mC = isC & era & valid
    yinj = W["PRE"].copy(); yinj[mF] += 30.0; oi = wmatch(yinj, mF, mC)
    say(f"- 陽性対照（在・声明日 PRE に +30 bp 注入）: t {RES[(sym, lab0)]['o']['t']:+.2f} → {oi['t']:+.2f}")
    # secondary: post-announcement continuation (2013-03-20+)
    say("- 副（記述・2013-03-20 以降の声明日）: POST(14:30→16:00) on J30(14:00→14:30) ／ NEXT(16:00→翌 10:00) on J30 ／ 声明日 POST δ・NEXT δ（曜日一致）")
    for lab, lo, hi in ERAS[sym]:
        era = (yr >= lo) & (yr <= hi); m = isF & era & POST_OK
        o1 = ols(W["POST"][m], W["J30"][m]); o2 = ols(W["NEXT"][m], W["J30"][m])
        vP = np.isfinite(W["POST"]) & (W["POST"] != 0); vN = np.isfinite(W["NEXT"]) & (W["NEXT"] != 0)
        dP = wmatch(W["POST"], isF & era & vP & POST_OK, isC & era & vP & POST_OK); dN = wmatch(W["NEXT"], isF & era & vN & POST_OK, isC & era & vN & POST_OK)
        say(f"  - {lab}: POST~J30 β {o1['b']:+.3f} (t {o1['t']:+.2f}, MDE {2*o1['se'] if np.isfinite(o1['se']) else float('nan'):.3f}, n {o1['n']})／NEXT~J30 β {o2['b']:+.3f} (t {o2['t']:+.2f}, MDE {2*o2['se'] if np.isfinite(o2['se']) else float('nan'):.3f})／POST δ {dP['d']:+.1f} (t {dP['t']:+.2f})／NEXT δ {dN['d']:+.1f} (t {dN['t']:+.2f})・|J30| 声明日 中央値 {np.nanmedian(np.abs(W['J30'][m])):.0f} bp")
    # unscheduled (descriptive)
    mu = isU & np.isfinite(W["PRE"])
    if mu.sum() > 0: say(f"- unscheduled（記述・n {int(mu.sum())}）: PRE " + ", ".join(f"{dates[i].strftime('%Y-%m-%d')} {W['PRE'][i]:+.0f}" for i in np.where(mu)[0]))

# ---------- gate ㉛ ----------
say("\n## ゲート ㉛（本番接続・在 2010-20 のみ印字）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["ft"] = FT / tr["risk"]
tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]; tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = (tr["exit"] == "TP").astype(float) - tr["q"]
et_ = tr["entry_time"].to_numpy(float); t12 = epoch_et(dates, 12, 0); t14 = epoch_et(dates, 14, 0); t14_prev = np.r_[np.nan, t14[:-1]]
# trade is in PRE window of statement day D if t14_prev[D] <= entry < t12[D]
pos = np.searchsorted(t12, et_, side="left"); pos = np.clip(pos, 0, N - 1)   # first D with t12[D] > entry
inpre = isF[pos] & np.isfinite(t14_prev[pos]) & (et_ >= t14_prev[pos]) & (et_ < t12[pos])
tr["inpre"] = inpre
# alive across 14:00 ET of statement day: entry < t14[D] <= entry + 300*hold, D statement day
posd = np.clip(np.searchsorted(t14, et_, side="left"), 0, N - 1); alive = isF[posd] & (et_ + 300 * tr["hold"].to_numpy(float) >= t14[posd]) & (et_ < t14[posd])
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); d_ = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d_, d_ / se, se
ins = tr[(tr.year >= 2010) & (tr.year <= 2020)]; A, B = ins[ins.inpre], ins[~ins.inpre]
dm, tm, sem = welch(A.Rs, B.Rs); dx, tx, _ = welch(A[A.dec].x, B[B.dec].x); d0, t0, _ = welch(A.x0, B.x0)
say(f"- 在 2010-20 の scan 本: 声明日 PRE 窓（前営業日 14:00 → D 12:00 ET）に建玉 {len(A)}／他 {len(B)}（全年 PRE 建玉 {int(inpre.sum())}・声明 14:00 ET を生きて跨ぐ本 全年 {int(alive.sum())}・在 {int((alive&(tr.year<=2020)).sum())}／外 {int((alive&(tr.year>=2021)).sum())}）")
say(f"- PRE−他: Δμ(R*) **{dm:+.3f}R (t {tm:+.2f}, se {sem:.3f}, MDE {2*sem:.3f})**・Δx {dx*100:+.2f} pp (t {tx:+.2f})・look-ahead 対照 x0 Δ {d0:+.3f} (t {t0:+.2f})・PRE 本の TP 率 {(A.exit=='TP').mean()*100:.1f}% vs {(B.exit=='TP').mean()*100:.1f}%")
gate = "通過（外を印字）" if abs(dm) >= 0.048 else "**不通過（在 |Δμ| <0.048R → 決着不能・外は走らせない）**"
say(f"- ゲート ㉛: {gate}")
if abs(dm) >= 0.048:
    for lab, lo, hi in ERAS["XAU"][1:]:
        o = tr[(tr.year >= lo) & (tr.year <= hi)]; a_, b_ = o[o.inpre], o[~o.inpre]
        if len(a_) >= 20: dm2, tm2, se2 = welch(a_.Rs, b_.Rs); say(f"  - {lab}: Δμ {dm2:+.3f}R (t {tm2:+.2f}, n {len(a_)}/{len(b_)})")
# side-signed (descriptive): BUY in PRE vs SELL in PRE
for s in ("BUY", "SELL"):
    a_ = A[A.side == s]
    if len(a_) >= 10: say(f"  - 記述: PRE 建玉 {s} n {len(a_)} 平均 R* {a_.Rs.mean():+.3f}（他 {s} {B[B.side==s].Rs.mean():+.3f}）")

# ---------- verdict ----------
say("\n## 判定（事前固定の規則で機械的に・Bonferroni(2)・名目 0.025）")
Jok = max(RES[("US500", "J")], RES[("XAU", "J")]) >= 0.40
say(f"- 暦検定: J US500 {RES[('US500','J')]:.2f}／XAU {RES[('XAU','J')]:.2f} → {'**暦は妥当（判定を進める）**' if Jok else '**J < 0.40 → 暦が疑わしい・全判定 void**'}")
def cell(sym, lab_in):
    i = RES[(sym, lab_in)]; o = RES[(sym, "外 2021-26H1")]; return i["o"], i["p"], o["o"]
oi, pi, oo = cell("US500", "在 2012-20")
c1 = Jok and np.isfinite(oi["d"]) and oi["d"] > 0 and oi["t"] >= 2 and pi < 0.025 and np.isfinite(oo["d"]) and oo["d"] > 0 and oo["t"] >= 1.5
say(f"- C1 US500（本拠）: 在 δ {oi['d']:+.1f} t {oi['t']:+.2f} p {pi:.3f}／外 δ {oo['d']:+.1f} t {oo['t']:+.2f} → **{'PASS' if c1 else 'null'}**")
xi, pxi, xo = cell("XAU", "在 2010-20")
same = Jok and xi["d"] > 0 and xi["t"] >= 2 and pxi < 0.025 and xo["d"] > 0 and xo["t"] >= 1.5
flip = Jok and abs(xi["t"]) < 2 and xo["d"] > 0 and xo["t"] >= 2 and RES[("XAU", "外 2021-26H1")]["p"] < 0.025
safe = Jok and (not same) and (not flip)
tag = "H_SAME（在外とも正）" if same else ("H_FLIP（在 null → 外 正＝c38 の予測）" if flip else "H_SAFE／null（金には無い・MDE 付き）")
say(f"- C2 XAU: 在 δ {xi['d']:+.1f} t {xi['t']:+.2f} p {pxi:.3f}／外 δ {xo['d']:+.1f} t {xo['t']:+.2f} p {RES[('XAU','外 2021-26H1')]['p']:.3f} → **{tag}**" + ("" if c1 else "（C1 null → ㉝ 記述のみ）"))
say(f"\n- 実行 {time.time()-T0:.1f} s・npz 2 本＋json＋FOMC_dates.csv・scan 無し・MT5 無し・外部通信無し（暦取得は scripts/c42_fomc_dates.py で別に実施）。seed {SEED}。")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
