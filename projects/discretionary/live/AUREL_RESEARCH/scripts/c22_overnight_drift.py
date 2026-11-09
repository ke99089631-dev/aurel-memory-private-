# -*- coding: utf-8 -*-
"""
[cycle22 研究レーン 2026-11-09] 【探索・市場構造（株式指数・時刻効果）】米株指数（US500 主・US100 複製）のリターンは「夜間（ET 18:05→09:30）」に
集中し、欧州寄り付き（ET 02–04）に偏るか ＝ 公開文献の構造（Lou–Polk–Skouras 2019 "A tug of war: overnight vs intraday"／
Boyarchenko–Larsen–Whelan 2020 "The overnight drift"）を**我々のデータで**在/外に分けて検証し、コスト（US100 spread キャッシュ）で受け取れるかを測る。
金（XAU）も同じ格子で並べ、cycle16 の「夜 22–08 London 正・昼 負」が市場横断（CFD/指数と共通の構造）かを記述する。
入口フィルタではない・本番の壁→壁とは独立の市場記述。既存キャッシュ 4 本のみ・scan 無し・MT5 無し・外部通信無し。

事前固定（検証前に書く・結果を見て変えない）
- データ: data/macro/US500_m5_close.npz・US100_m5_close.npz・XAU_m5_close.npz（Dukascopy bid close・暦時刻の完全格子・前値埋め・ts=足の開始 UTC 秒）
  ＋ data/macro/US100_m5_spread.npz（sp_med pt・2022-01〜2026-06）。読込後に min/max 時刻（⑩）・曜日別 flat 比率（⑪）を印字。
- 価格の時計: 時刻 T の価格 P(T) = ts == T−300 の足の close（足の開始 ts・close はその 5 分後）。格子の穴は NaN（⑫: index でなく ts 一致）。
- 取引日 D（ET 現地・月〜金）: セッション = (D−1) 18:00 → D 17:00。窓（ET）:
    gap  = (D−1) 17:00 → (D−1) 18:05   （ブレイク跨ぎ＝再開 pop。16:55 足 close → 18:00 足 close）
    ON   = (D−1) 18:05 → D 09:30      （夜間・再開足を除く）
    EU   = D 02:00 → D 04:00           （欧州寄り付き 2 時間ブロック・Boyarchenko らの 02–03 ET 集中を含む）
    CASH = D 09:30 → D 16:00           （米国現物時間）
    LATE = D 16:00 → D 17:00
    1 時間セル h→h+1（(D−1) 18:05→19:00・19〜23・0〜16 時）＝記述・24 セル Bonferroni。2 時間ブロック 11 個（18–20…14–16・16–18 ブレイクは除く）＝EU の順位用。
- 除外: CASH の対数リターンが NaN または **厳密に 0**（祝日・無配信）の日。DST で存在しない/曖昧な時刻（02:00 の春・01:00 の秋）はその窓だけ NaN。
- 衛生（事前）: 各窓の「リターン厳密 0 の日の割合」（stale 端点）を窓×期間で印字し、>20% の窓は判定に使わない（inconclusive）。
- 統計: 1 日 1 観測（非重複）。平均 bp・se（日 iid・補助に Newey–West lag5）・t・中央値・正の日比率・MDE=2se。
- 窓: 在 2012-20／外 2021-26H1／近年 2024-26H1（判定は在∧外）。年別も印字。
- 判定（US500 が主・2 セル）:
    H_ON  PASS = 在 ON >0 (t≥2) ∧ 外 ON >0 (t≥2) ∧ 外 (ON − CASH) >0 (t≥1.5)。
    H_EU  PASS = 在 EU >0 (t≥2) ∧ 外 EU >0 (t≥2) ∧ 外で EU ブロックが 11 ブロック中 上位 3 位以内。
    他 null（MDE 併記）。US100 は複製（同規則・記述）。XAU は記述のみ（cycle16 との整合: 夜 London 22–08 = ET 17–03 正・昼 負）。
- 陽性対照: (i) 会計恒等式 gap+ON+CASH+LATE = ln P(D 17:00) − ln P((D−1) 17:00)（|差| 中央値 <1e-6）。(ii) 外 EU に +1.0 bp/日 を注入して t が ≥2 増えること（検出力）。
- 経済的大きさ（記述・事前に書く）: US100 の夜間 spread 中央値（pt・2022-01〜2025-08 と 2025-09〜 の 2 配信レジーム別）を同期間の指数中央値で bp 化し、
  往復 1 spread を ON（または EU）の 1 日平均 bp と比べる。**swap（夜間金利調整）は記録が無い＝【要取得】**として net の上限だけ書く。US500 の口座 spread は無い＝要取得。
- 事前の最重大反証: (i) bid のみ: 再開足で bid が沈む（c16c: US100 18:00 足 −0.36 bp）→ gap 窓を ON から分離して影響を局所化。ON 自体は 18:05 以降なので影響小。
  (ii) 夜間 CFD は flat 2 割（配信が薄い）→ 端点 stale は「厳密 0 比率」で検出。(iii) 2012-26 の株は強い上昇相場＝「夜間に正」は「全時間正」の時間シェアかも
  しれない → CASH と差で見る（H_ON の第 3 条件）し、下げ年（2015/2018/2022）の ON を別に印字。(iv) 24 セル・11 ブロックの事後探索は Bonferroni。
seed 20261109
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c22_overnight_drift_result.md"); L = []
NY = "America/New_York"; SEED = 20261109; rng = np.random.default_rng(SEED)
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle22] 米株指数の夜間ドリフト（ON／EU 02–04 ET）在外検証＋コスト・金との横並び — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c22_overnight_drift.py)")

WD = ['月','火','水','木','金','土','日']
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    r = np.diff(np.log(cl)); fl = np.r_[False, r == 0]; wd = t.weekday.to_numpy()
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%・曜日別 " + " ".join(f"{WD[w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
    return ts, cl, t

def epoch_et(dates, hour, minute, day_offset=0):
    """ET 暦日 dates（DatetimeIndex, naive）+ offset 日 の hour:minute を UTC 秒へ。DST で存在しない/曖昧は NaN。"""
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    ep = (utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1)
    return np.asarray(ep, dtype=float)

def price_at(ts, cl, T):
    """P(T) = close of bar with ts == T-300 ; NaN if hole/NaN T"""
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64); pos = np.searchsorted(ts, key); pos = np.clip(pos, 0, len(ts) - 1)
    hit = ts[pos] == key; vals = np.where(hit, cl[pos], np.nan); out[ok] = vals
    return out

def stats(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 30: return dict(n=n, mean=np.nan, se=np.nan, t=np.nan, med=np.nan, pos=np.nan, zero=np.nan, tnw=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
    # Newey-West lag 5
    e = x - m; g = e @ e / n
    for l in range(1, 6): g += 2 * (1 - l / 6) * (e[l:] @ e[:-l]) / n
    tnw = m / math.sqrt(max(g, 1e-18) / n)
    return dict(n=n, mean=m, se=se, t=m / se, med=np.median(x), pos=(x > 0).mean(), zero=(x == 0).mean(), tnw=tnw)
def fmt(s, mde=False):
    if s["n"] < 30 or not np.isfinite(s["mean"]): return f"n{s['n']} —"
    base = f"{s['mean']:+.2f} bp (t{s['t']:+.1f}, n{s['n']}, 0比率{s['zero']*100:.0f}%)"
    return base + (f" MDE {2*s['se']:.2f}" if mde else "")

def build(sym, ts, cl):
    dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
    P = lambda h, m, off=0: price_at(ts, cl, epoch_et(dates, h, m, off))
    p_pre_close = P(17, 0, -1)      # close of 16:55 bar (D-1)
    p_reopen = P(18, 5, -1)         # close of 18:00 bar (D-1)
    p_0930 = P(9, 30); p_1600 = P(16, 0); p_1700 = P(17, 0)
    lg = np.log
    W = {}
    W["gap"] = (lg(p_reopen) - lg(p_pre_close)) * 1e4
    W["ON"] = (lg(p_0930) - lg(p_reopen)) * 1e4
    W["EU"] = (lg(P(4, 0)) - lg(P(2, 0))) * 1e4
    W["CASH"] = (lg(p_1600) - lg(p_0930)) * 1e4
    W["LATE"] = (lg(p_1700) - lg(p_1600)) * 1e4
    W["C2C"] = (lg(p_1700) - lg(p_pre_close)) * 1e4
    # hourly cells (session order): 18(18:05->19), 19..23 on D-1, 0..16 on D
    H = {}
    H[18] = (lg(P(19, 0, -1)) - lg(p_reopen)) * 1e4
    for h in range(19, 24): H[h] = (lg(P(h + 1 if h < 23 else 0, 0, -1 if h < 23 else 0)) - lg(P(h, 0, -1))) * 1e4
    for h in range(0, 17): H[h] = (lg(P(h + 1, 0)) - lg(P(h, 0))) * 1e4
    # 2h blocks
    B = {}
    B["18-20"] = H[18] + H[19]; B["20-22"] = H[20] + H[21]; B["22-00"] = H[22] + H[23]
    for a in range(0, 16, 2): B[f"{a:02d}-{a+2:02d}"] = H[a] + H[a + 1]
    valid = np.isfinite(W["CASH"]) & (W["CASH"] != 0) & np.isfinite(W["ON"])
    yr = dates.year.to_numpy()
    # price level for bp conversion
    lvl = p_0930
    return dict(dates=dates, yr=yr, valid=valid, W=W, H=H, B=B, lvl=lvl)

ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]
def era_mask(D, lo, hi): return D["valid"] & (D["yr"] >= lo) & (D["yr"] <= hi)

RESULTS = {}
for sym in ("US500", "US100", "XAU"):
    say(f"\n## {sym}")
    ts, cl, t = load(sym); D = build(sym, ts, cl); RESULTS[sym] = D
    v = D["valid"]; say(f"- 取引日候補 {len(D['dates'])}・有効日 {v.sum()}（CASH≠0 かつ ON 有限）・除外 {(~v).sum()}（祝日/無配信/データ末尾）・有効日の範囲 {D['dates'][v][0].date()}〜{D['dates'][v][-1].date()}")
    # accounting identity
    acc = D["W"]["gap"] + D["W"]["ON"] + D["W"]["CASH"] + D["W"]["LATE"] - D["W"]["C2C"]
    say(f"- 陽性対照 (i) 会計恒等式 |gap+ON+CASH+LATE − C2C| 中央値 {np.nanmedian(np.abs(acc[v])):.2e} bp・最大 {np.nanmax(np.abs(acc[v])):.2e}")
    say("\n| 期間 | gap 17:00→18:05 | ON 18:05→09:30 | EU 02→04 | CASH 09:30→16:00 | LATE 16→17 | C2C 17→17 | ON−CASH |")
    say("|---|---|---|---|---|---|---|---|")
    for lab, lo, hi in ERAS:
        m = era_mask(D, lo, hi); S = {k: stats(D["W"][k][m]) for k in D["W"]}; dif = stats((D["W"]["ON"] - D["W"]["CASH"])[m])
        RESULTS[(sym, lab)] = dict(S=S, dif=dif)
        say(f"| {lab} | {fmt(S['gap'])} | {fmt(S['ON'], True)} | {fmt(S['EU'], True)} | {fmt(S['CASH'])} | {fmt(S['LATE'])} | {fmt(S['C2C'])} | {fmt(dif)} |")
    # NW t and medians / pos ratio for ON & EU
    for lab, lo, hi in ERAS:
        S = RESULTS[(sym, lab)]["S"]
        say(f"- {lab} ON: NW t{S['ON']['tnw']:+.1f}・中央値 {S['ON']['med']:+.2f}・正の日 {S['ON']['pos']*100:.1f}%／EU: NW t{S['EU']['tnw']:+.1f}・中央値 {S['EU']['med']:+.2f}・正の日 {S['EU']['pos']*100:.1f}%／CASH 正の日 {S['CASH']['pos']*100:.1f}%")
    # 2h blocks ranking
    say("\n| 期間 | " + " | ".join(D["B"].keys()) + " |"); say("|---|" + "---|" * len(D["B"]))
    for lab, lo, hi in ERAS:
        m = era_mask(D, lo, hi); row = []; means = {}
        for k, x in D["B"].items():
            s = stats(x[m]); means[k] = s["mean"]; row.append(f"{s['mean']:+.2f} (t{s['t']:+.1f})")
        rank = 1 + sum(1 for k, mv in means.items() if mv > means["02-04"]); RESULTS[(sym, lab)]["eu_rank"] = rank
        say(f"| {lab} | " + " | ".join(row) + f" | EU 順位 {rank}/11")
    # hourly cells with Bonferroni(24)
    say("\n- 1 時間セル（bp・t）: Bonferroni(24) 5% の |t| 閾値 3.02")
    order = [18, 19, 20, 21, 22, 23] + list(range(0, 17))
    for lab, lo, hi in ERAS:
        m = era_mask(D, lo, hi)
        cells = []; nsig = 0
        for h in order:
            s = stats(D["H"][h][m]); cells.append(f"{h:02d}:{s['mean']:+.2f}({s['t']:+.1f})"); nsig += abs(s["t"]) >= 3.02 if np.isfinite(s["t"]) else 0
        say(f"  - {lab}: " + " ".join(cells) + f" ｜ |t|≥3.02 のセル {nsig}/23")
    # yearly
    say("\n| 年 | n | gap | ON | EU | CASH | C2C | ON−CASH |"); say("|---|---|---|---|---|---|---|---|")
    for y in range(2012, 2027):
        m = D["valid"] & (D["yr"] == y)
        if m.sum() < 30: continue
        S = {k: stats(D["W"][k][m]) for k in ("gap", "ON", "EU", "CASH", "C2C")}; dif = stats((D["W"]["ON"] - D["W"]["CASH"])[m])
        say(f"| {y}{'H1' if y==2026 else ''} | {m.sum()} | {S['gap']['mean']:+.2f} | {S['ON']['mean']:+.2f} (t{S['ON']['t']:+.1f}) | {S['EU']['mean']:+.2f} (t{S['EU']['t']:+.1f}) | {S['CASH']['mean']:+.2f} (t{S['CASH']['t']:+.1f}) | {S['C2C']['mean']:+.2f} | {dif['mean']:+.2f} |")
    # down years
    yrs = [y for y in range(2012, 2027) if (D["valid"] & (D["yr"] == y)).sum() >= 30]
    c2c_y = {y: np.nansum(D["W"]["C2C"][D["valid"] & (D["yr"] == y)]) for y in yrs}
    down = [y for y in yrs if c2c_y[y] < 0]
    if down:
        m = D["valid"] & np.isin(D["yr"], down); S = {k: stats(D["W"][k][m]) for k in ("ON", "EU", "CASH")}
        say(f"- 下げ年 {down}（年間 C2C<0）だけ: ON {fmt(S['ON'])}／EU {fmt(S['EU'])}／CASH {fmt(S['CASH'])}")
    up = [y for y in yrs if c2c_y[y] >= 0]
    m = D["valid"] & np.isin(D["yr"], up); S = {k: stats(D["W"][k][m]) for k in ("ON", "EU", "CASH")}
    say(f"- 上げ年 {len(up)} 年だけ: ON {fmt(S['ON'])}／EU {fmt(S['EU'])}／CASH {fmt(S['CASH'])}")
    say(f"- 年別 ON>0 の年 {sum(1 for y in yrs if np.nanmean(D['W']['ON'][D['valid']&(D['yr']==y)])>0)}/{len(yrs)}・EU>0 の年 {sum(1 for y in yrs if np.nanmean(D['W']['EU'][D['valid']&(D['yr']==y)])>0)}/{len(yrs)}・CASH>0 の年 {sum(1 for y in yrs if np.nanmean(D['W']['CASH'][D['valid']&(D['yr']==y)])>0)}/{len(yrs)}")

# ---------- judgments ----------
say("\n## 判定（事前固定）")
VERD = {}
for sym in ("US500", "US100"):
    I = RESULTS[(sym, "在 2012-20")]; O = RESULTS[(sym, "外 2021-26H1")]
    zero_ok = all(RESULTS[(sym, lab)]["S"][k]["zero"] <= 0.20 for lab in ("在 2012-20", "外 2021-26H1") for k in ("ON", "EU", "CASH"))
    h_on = (I["S"]["ON"]["t"] >= 2) and (O["S"]["ON"]["t"] >= 2) and (O["dif"]["t"] >= 1.5)
    h_eu = (I["S"]["EU"]["t"] >= 2) and (O["S"]["EU"]["t"] >= 2) and (O["eu_rank"] <= 3)
    VERD[sym] = ("inconclusive（stale>20%）" if not zero_ok else ("PASS" if h_on else "null"), "inconclusive（stale>20%）" if not zero_ok else ("PASS" if h_eu else "null"))
    say(f"- {sym} H_ON: 在 ON t{I['S']['ON']['t']:+.2f}／外 ON t{O['S']['ON']['t']:+.2f}／外 ON−CASH t{O['dif']['t']:+.2f} → **{VERD[sym][0]}**（外 MDE {2*O['S']['ON']['se']:.2f} bp/日）")
    say(f"- {sym} H_EU: 在 EU t{I['S']['EU']['t']:+.2f}／外 EU t{O['S']['EU']['t']:+.2f}／外 EU 順位 {O['eu_rank']}/11 → **{VERD[sym][1]}**（外 MDE {2*O['S']['EU']['se']:.2f} bp/日）")

# positive control (ii): injection +1 bp/day into OOS EU of US500
D = RESULTS["US500"]; m = era_mask(D, 2021, 2026); x = D["W"]["EU"][m]; x = x[np.isfinite(x)]
s0 = stats(x); s1 = stats(x + 1.0)
say(f"- 陽性対照 (ii) US500 外 EU に +1.0 bp/日 注入: t {s0['t']:+.2f} → {s1['t']:+.2f}（Δt {s1['t']-s0['t']:+.2f}・{'検出可' if s1['t']-s0['t']>=2 else '検出不可'}）")

# ---------- cost: US100 spread ----------
say("\n## 経済的大きさ（US100・Dukascopy spread キャッシュ）")
zz = np.load(os.path.join(MAC, "US100_m5_spread.npz")); sts = zz["ts"].astype(np.int64); sp = zz["sp_med"].astype(float)
st = pd.to_datetime(sts, unit="s", utc=True).tz_convert(NY); sh = st.hour.to_numpy(); swd = st.weekday.to_numpy(); syr = st.year.to_numpy(); smo = st.month.to_numpy()
say(f"- spread npz {len(sts)} 行 {st[0]}〜{st[-1]} ET（⑩）")
tsU, clU, tU = load("US100")
# index level by ym
def med_level(lo_ym, hi_ym):
    ym = tU.year.to_numpy() * 100 + tU.month.to_numpy(); mm = (ym >= lo_ym) & (ym <= hi_ym); return np.nanmedian(clU[mm])
night = ((sh >= 18) | (sh < 9)) & (swd <= 4); eu = (sh >= 2) & (sh < 4) & (swd <= 4); cash_h = (sh >= 10) & (sh < 16) & (swd <= 4)
for lab, lo, hi in (("配信レジーム 1: 2022-01〜2025-08", 202201, 202508), ("配信レジーム 2: 2025-09〜2026-06", 202509, 202606)):
    ym = syr * 100 + smo; mm = (ym >= lo) & (ym <= hi) & np.isfinite(sp)
    lvl = med_level(lo, hi)
    spn = np.nanmedian(sp[mm & night]); spe = np.nanmedian(sp[mm & eu]); spc = np.nanmedian(sp[mm & cash_h])
    say(f"- {lab}: 指数中央値 {lvl:.0f}・spread 中央値 夜間 {spn:.2f} pt (= 往復 {spn/lvl*1e4:.2f} bp)／EU 02–04 {spe:.2f} pt ({spe/lvl*1e4:.2f} bp)／現物 {spc:.2f} pt ({spc/lvl*1e4:.2f} bp)")
    # same-period ON/EU mean for US100
    DU = RESULTS["US100"]; ymd = DU["dates"].year.to_numpy() * 100 + DU["dates"].month.to_numpy(); md = DU["valid"] & (ymd >= lo) & (ymd <= hi)
    so = stats(DU["W"]["ON"][md]); se_ = stats(DU["W"]["EU"][md]); sc = stats(DU["W"]["CASH"][md])
    say(f"  同期間 US100: ON {fmt(so)}／EU {fmt(se_)}／CASH {fmt(sc)} → ON net（往復 1 spread・swap 0）{so['mean']-spn/lvl*1e4:+.2f} bp/日・EU net {se_['mean']-spe/lvl*1e4:+.2f} bp/日（**swap は未記録＝【要取得】・net は上限**）")

say(f"\n実行 {time.time()-T0:.1f} s・seed {SEED}・入力 4 npz のみ・scan 無し・MT5 無し・外部通信無し")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
