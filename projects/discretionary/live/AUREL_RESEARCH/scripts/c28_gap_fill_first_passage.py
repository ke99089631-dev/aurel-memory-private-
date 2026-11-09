# -*- coding: utf-8 -*-
"""
[cycle28 研究レーン 2026-11-10] 【探索・市場構造／行動（ギャップは埋まるか）】
金 XAUUSD の週末ギャップ（金 16:55 ET → 日 18:05 ET）と日次ブレイク・ギャップ（月〜木 16:55 → 18:05 ET・2013+）は、
「埋まる（reversion）」か「続く（continuation）」か。民間伝承「ギャップは埋まる（7 割）」は、無ドリフト RW でも
小さい変位は高確率で再訪されるため、埋まる率の単独値では何も言えない。→ **同じ距離の対称バリアで先着を比べる**。

事前固定（検証前・このまま findings に転記）:
- データ: data/macro/XAU_m5_ohlc.npz（bid・M5・暦時刻の完全格子・2010-01〜2026-06・反証 05:35 が構築）。時刻 America/New_York（ET）。
  格子の穴は ts 一致で参照（⑫）。flat = 終値不変。読込後に min/max・flat 比率（曜日別）を印字（⑩⑪）。
  金 16:55 ET（16:55 足）は Dukascopy の最終印字の沈み（c17: 在 −1.75 bp）→ 参照は **16:50 足の終値**（= 16:55 時点の価格）。
- イベント:
  WKND = 日曜 18:00 ET 足（終値は 18:05 に既知）。参照 = 直前の金曜 16:50 足終値。条件: 日曜 17:00–17:55 の 12 本が flat（クリーン再開）、
         参照足・窓内の格子に穴なし。全年 2010+。
  DAILY = 月〜木 18:00 ET 足・2013+・17:00–17:55 の 12 本 flat（c17 と同じクリーンなブレイク日）。参照 = 同日 16:50 足終値。
- ギャップ G = ln(P0/Pref)·1e4 bp、P0 = 18:00 足終値。|G| < g_min=2 bp は除外（bid ノイズ・半スプレッド 0.2〜0.5 bp の 4 倍以上）。感度 1／5 bp を記述。
- 対称バリア: FILL 水準 = Pref（= P0·e^{−G}）、CONT 水準 = P0·e^{+G}（同じ対数距離・反対側）。
  足 a+1..a+N の高値/安値で先着を判定（s>0: low≤FILL が埋め・high≥CONT が継続。s<0 は逆）。同足で両方到達 = tie（除外・件数印字）。
  D_i = +1（FILL 先着）／−1（CONT 先着）／0（どちらも未到達・tie）。
- 統計: D̄ = mean(D_i)（全イベント・0 を含む）・se = sd/√n（イベント = 週 or 日で独立）。P(FILL 先着 | 決着) − 0.5 と二項 se も併記。
  地平 N: **72 本（6 h）= 主**、12 本（1 h）・276 本（23 h・次のブレイク直前まで）= 副。
  窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2・窓別）。
- 判定（主セル = WKND・N=72・D̄）: PASS_fill = 在 t≥+2.5 ∧ 外 t≥+2.0（伝承どおり埋まる）／PASS_cont = 在 t≤−2.5 ∧ 外 t≤−2.0（情報の継続）／それ以外 null。
  DAILY は同規則の第 2 セル（Bonferroni(2) の名目 |t| 閾値 2.24／2.81 も印字）。
- 副（記述・事後と明記）: |G| の在中央値で大小分割（伝承「小さいギャップは埋まり大きいギャップは続く」）、上下ギャップ別、年別符号、到達までの時間中央値、
  伝承値「N 内に FILL 水準に一度でも触れた割合」（RW でも高い）。
- 帰無校正（プラセボ・アンカー）: 月〜木 12:00 ET 足（12:05 既知）に、同じ週の WKND |G| を距離・符号は乱数で与え、同じ先着判定 → D̄ ≈ 0 のはず。
- 陽性対照（注入）: 外窓の WKND path に「N 本かけて |G| の 25% だけ参照側へ戻る」決定論的ドリフトを足して D̄ の t を印字（検出器の感度）。MDE = 2·se。
- 経済的大きさ: 「埋まりに賭ける対称バリア」の粗損益 = D_i·|G_i| bp（未決着は N 本目終値で評価）。往復スプレッド 0.32 USD を当時価格で bp 化して併記。
- 事前の最重大反証: (i) bid のみ・再開直後はスプレッド拡大で bid が沈む（c16c: US100 −0.36 bp）→ 上ギャップの FILL／下ギャップの CONT を同じ向きに
  わずかに有利にする＝上下別の D̄ の差で見る。(ii) 再開直後 1 時間のボラ構造（アジア帯）が FILL/CONT 対称でも tie を増やす。(iii) 週末ギャップは
  情報（ニュース）とポジション解消の混合で、符号条件なしの平均は 2 成分の打ち消し。(iv) 18:00 足の終値を使うため最初の 5 分の動きは判定に入らない。
- seed 20261110。多年 scan 無し・M5 読込無し・MT5 無し・外部通信無し。書き込みは AUREL_RESEARCH/data のみ。
"""
import os, sys, time, math, io
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
MAC = os.path.join(ROOT, "data", "macro"); OUT = os.path.join(ROOT, "data", "c28_gap_fill_first_passage_result.md")
rng = np.random.default_rng(20261110)
T0 = time.time(); buf = io.StringIO()
def say(s=""):
    print(s, flush=True); buf.write(s + "\n")

W = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
NS = {"N12 (1h)": 12, "N72 (6h) 主": 72, "N276 (23h)": 276}
G_MIN = 2.0

# ---------- load ----------
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64); op = z["open"]; hi = z["high"]; lo = z["low"]; cl = z["close"]
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = r == 0
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert("America/New_York")
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
dts = np.diff(ts); holes = np.where(dts != 300)[0]
say(f"# c28 ギャップの先着（FILL vs CONT・対称バリア）— 実行 {pd.Timestamp.now():%Y-%m-%d %H:%M}")
say(f"- npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）・close {cl.min():.1f}〜{cl.max():.1f}・flat 全体 {flat.mean()*100:.1f}%・曜日別 flat(ET) "
    + " ".join(f"{d}:{flat[wd==i].mean()*100:.0f}%" for i, d in enumerate(["月","火","水","木","金","土","日"])) + f"・格子の穴 {len(holes)}（⑫）")
# Friday close / Sunday reopen hygiene by year
rows = []
for y in sorted(set(yr)):
    m = yr == y
    f1655 = flat[m & (wd == 4) & (h == 16) & (mi == 55)].mean(); f1700 = flat[m & (wd == 4) & (h == 17) & (mi == 0)].mean()
    s17 = flat[m & (wd == 6) & (h == 17)].mean(); s1800 = flat[m & (wd == 6) & (h == 18) & (mi == 0)].mean(); s1805 = flat[m & (wd == 6) & (h == 18) & (mi == 5)].mean()
    rows.append(f"{y}: 金16:55 {f1655*100:.0f}／金17:00 {f1700*100:.0f}／日17時台 {s17*100:.0f}／日18:00 {s1800*100:.0f}／日18:05 {s1805*100:.0f}")
say("- 年別 flat%（金曜の引け・日曜の再開の確認）: " + " ｜ ".join(rows))

def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)
NMAX = max(NS.values())
def window_ok(a):
    a = np.asarray(a); e = a + NMAX
    return (e < len(ts)) & (ts[np.clip(e, 0, len(ts) - 1)] == ts[a] + 300 * NMAX)

def build_events(anchor_idx, ref_idx, label):
    a = anchor_idx; ref = ref_idx
    ok = (ref >= 0) & (a > 0) & window_ok(a)
    brk = np.column_stack([idx_at(ts[a] - 300 * j) for j in range(1, 13)])
    ok &= np.all(brk >= 0, axis=1)
    clean = np.zeros(len(a), bool); clean[ok] = np.all(flat[brk[ok]], axis=1)
    say(f"- {label}: 候補 {len(a)}・参照/窓 OK {ok.sum()}・クリーン（17:00–17:55 flat）{clean.sum()}")
    k = ok & clean
    a, ref = a[k], ref[k]
    G = (lc[a] - lc[ref]) * 1e4
    big = np.abs(G) >= G_MIN
    say(f"  |G|<{G_MIN:.0f} bp 除外 {(~big).sum()}（{(~big).mean()*100:.1f}%）→ n {big.sum()}・|G| 中央値 {np.median(np.abs(G[big])):.1f} bp・USD {np.median(np.abs(cl[a][big]-cl[ref][big])):.2f}・上 {(G[big]>0).mean()*100:.0f}%")
    return a[big], ref[big], G[big]

def first_passage(a, G, N, drift_frac=0.0):
    """D (+1 fill first / -1 cont first / 0), tie flag, touched_fill_any, k_fill, mtm_bp (fade pnl)"""
    n = len(a); s = np.sign(G); ag = np.abs(G) / 1e4
    J = a[:, None] + np.arange(1, N + 1)[None, :]
    lh = np.log(hi[J]) - lc[a][:, None]; ll = np.log(lo[J]) - lc[a][:, None]; lcN = lc[J[:, -1]] - lc[a]
    if drift_frac:  # positive control: deterministic reversion toward reference by drift_frac*|G| over N bars
        d = -s[:, None] * drift_frac * ag[:, None] * (np.arange(1, N + 1)[None, :] / N)
        lh = lh + d; ll = ll + d; lcN = lcN + d[:, -1]
    # fill: move against gap direction by ag ; cont: move with gap direction by ag
    fill_hit = np.where(s[:, None] > 0, ll <= -ag[:, None], lh >= ag[:, None])
    cont_hit = np.where(s[:, None] > 0, lh >= ag[:, None], ll <= -ag[:, None])
    kf = np.where(fill_hit.any(1), fill_hit.argmax(1), N + 1); kc = np.where(cont_hit.any(1), cont_hit.argmax(1), N + 1)
    D = np.zeros(n); D[kf < kc] = 1; D[kc < kf] = -1
    tie = (kf == kc) & (kf <= N)
    pnl = np.where(D != 0, D * np.abs(G), -s * lcN * 1e4)  # fade position pnl in bp (undecided: mark at N)
    return D, tie, fill_hit.any(1), kf, pnl

def ms(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; n = len(x)
    if n < 2: return (np.nan, np.nan, n)
    return (x.mean(), x.std(ddof=1) / math.sqrt(n), n)

def report(label, a, G, N, yrs, extra=True):
    D, tie, anyfill, kf, pnl = first_passage(a, G, N)
    out = {}
    for wn, (y0, y1) in W.items():
        m = (yrs >= y0) & (yrs <= y1)
        if m.sum() < 10: continue
        mean, se, n = ms(D[m]); dec = D[m] != 0; nd = dec.sum()
        pf = (D[m] == 1).sum() / nd if nd else np.nan; se_b = math.sqrt(0.25 / nd) if nd else np.nan
        pm, pse, _ = ms(pnl[m])
        price = np.median(cl[a[m]]); cost_bp = 0.32 / price * 1e4
        out[wn] = dict(mean=mean, se=se, n=n, t=mean / se if se else np.nan)
        say(f"  - {label} {wn}: n {n}・D̄ **{mean:+.3f}**（se {se:.3f}・t {mean/se:+.2f}・MDE {2*se:.3f}）・決着 {nd}（{nd/n*100:.0f}%・tie {tie[m].sum()}）"
            f"・P(FILL 先着|決着) {pf*100:.1f}%（−50 = {(pf-0.5)*100:+.1f} pp・z {(pf-0.5)/se_b:+.2f}）・FILL 水準に一度でも触れた {anyfill[m].mean()*100:.0f}%"
            f"・到達 k 中央値 {np.median(kf[m][kf[m]<=N]) if (kf[m]<=N).any() else float('nan'):.0f} 本"
            f"・fade 粗損益 {pm:+.2f} bp/件（t {pm/pse:+.2f}）vs 往復 0.32 USD = {cost_bp:.2f} bp")
    return out, D, pnl

# ---------- events ----------
iS = np.where((wd == 6) & (h == 18) & (mi == 0))[0]
# Fri 16:50 ET bar: ET 暦で探す（DST 切替の週末は UTC 差が 1 時間ずれるため ts 引き算は使わない）
iF = np.where((wd == 4) & (h == 16) & (mi == 50))[0]
pF = np.searchsorted(iF, iS) - 1
refS = np.where(pF >= 0, iF[np.clip(pF, 0, len(iF) - 1)], -1)
refS = np.where((refS >= 0) & (ts[iS] - ts[np.clip(refS, 0, len(ts) - 1)] <= 3 * 86400), refS, -1)
aW, rW, GW = build_events(iS, refS, "WKND（日 18:00 ET・参照 金 16:50 足終値）")
iD = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]
refD = idx_at(ts[iD] - 70 * 60)
aD, rD, GD = build_events(iD, refD, "DAILY（月〜木 18:00 ET・2013+・参照 同日 16:50）")
yW = yr[aW]; yD = yr[aD]
say(f"- |G| 分布 WKND: p10 {np.percentile(np.abs(GW),10):.1f}／p50 {np.median(np.abs(GW)):.1f}／p90 {np.percentile(np.abs(GW),90):.1f} bp・DAILY: {np.percentile(np.abs(GD),10):.1f}／{np.median(np.abs(GD)):.1f}／{np.percentile(np.abs(GD),90):.1f} bp"
    + "・年別 WKND |G| 中央値 " + " ".join(f"{y}:{np.median(np.abs(GW[yW==y])):.0f}" for y in sorted(set(yW))))

say("\n## 主結果（D̄ = P(FILL 先着) − P(CONT 先着)・0 を含む平均・正 = 埋まる）")
main = {}
for nn, N in NS.items():
    say(f"- 地平 {nn}")
    main[("W", N)], _, _ = report("WKND", aW, GW, N, yW)
    main[("D", N)], _, _ = report("DAILY", aD, GD, N, yD)

# ---------- 判定 ----------
def verdict(res):
    i = res.get("在 2010-20", {}).get("t", np.nan); o = res.get("外 2021-26H1", {}).get("t", np.nan)
    if i >= 2.5 and o >= 2.0: return f"PASS_fill（在 t {i:+.2f}・外 {o:+.2f}）"
    if i <= -2.5 and o <= -2.0: return f"PASS_cont（在 t {i:+.2f}・外 {o:+.2f}）"
    return f"null（在 t {i:+.2f}・外 {o:+.2f}）"
say("\n## 判定（事前固定・N=72）")
say(f"- 主セル WKND: **{verdict(main[('W',72)])}**")
say(f"- 第 2 セル DAILY: **{verdict(main[('D',72)])}**（Bonferroni(2) 名目閾値 在 2.81／外 2.24）")

# ---------- 副（事後・記述） ----------
say("\n## 副（記述・事後と明記）")
medW = np.median(np.abs(GW[(yW >= 2010) & (yW <= 2020)])); medD = np.median(np.abs(GD[(yD >= 2013) & (yD <= 2020)]))
say(f"- 大小分割の閾値（在中央値）WKND {medW:.1f} bp・DAILY {medD:.1f} bp")
for lab, a, G, yrs, med in [("WKND", aW, GW, yW, medW), ("DAILY", aD, GD, yD, medD)]:
    D, tie, anyf, kf, pnl = first_passage(a, G, 72)
    for wn, (y0, y1) in W.items():
        m = (yrs >= y0) & (yrs <= y1)
        parts = []
        for nm, sel in [("小|G|", np.abs(G) < med), ("大|G|", np.abs(G) >= med), ("上", G > 0), ("下", G < 0)]:
            mm = m & sel; mean, se, n = ms(D[mm])
            parts.append(f"{nm} {mean:+.3f} (t {mean/se:+.2f}, n {n})" if n >= 10 else f"{nm} n{n}")
        say(f"  - {lab} {wn} N=72: " + "／".join(parts))
    # yearly sign
    ys = []
    for y in sorted(set(yrs)):
        mm = yrs == y; mean, se, n = ms(D[mm]); ys.append(f"{y}:{mean:+.2f}")
    pos = sum(1 for y in sorted(set(yrs)) if ms(D[yrs == y])[0] > 0)
    say(f"  - {lab} 年別 D̄(N=72): " + " ".join(ys) + f" → 正 {pos}/{len(set(yrs))} 年")
# sensitivity g_min
say("- 感度 g_min（WKND・N=72・D̄ 在/外）:")
for gm in [1.0, 2.0, 5.0]:
    m0 = np.abs((lc[aW] - lc[rW]) * 1e4) >= gm
    # rebuild over all clean weekend events incl. small ones: recompute from full set
    pass
# full set recompute for sensitivity (re-run build without filter)
def build_all(anchor_idx, ref_idx):
    a = anchor_idx; ref = ref_idx
    ok = (ref >= 0) & (a > 0) & window_ok(a)
    brk = np.column_stack([idx_at(ts[a] - 300 * j) for j in range(1, 13)]); ok &= np.all(brk >= 0, axis=1)
    clean = np.zeros(len(a), bool); clean[ok] = np.all(flat[brk[ok]], axis=1)
    k = ok & clean; return a[k], (lc[a[k]] - lc[ref[k]]) * 1e4
aWa, GWa = build_all(iS, refS)
for gm in [1.0, 2.0, 5.0, 10.0]:
    sel = np.abs(GWa) >= gm; D, *_ = first_passage(aWa[sel], GWa[sel], 72); yy = yr[aWa[sel]]
    parts = []
    for wn, (y0, y1) in W.items():
        m = (yy >= y0) & (yy <= y1); mean, se, n = ms(D[m]); parts.append(f"{wn} {mean:+.3f} (t {mean/se:+.2f}, n {n})")
    say(f"  - g_min {gm:.0f} bp: " + "／".join(parts))

# ---------- プラセボ・アンカー（帰無校正） ----------
say("\n## 帰無校正（プラセボ・アンカー: 月〜木 12:00 ET 足・距離 = 同週 WKND |G|・符号乱数）")
iP = np.where((wd <= 3) & (h == 12) & (mi == 0))[0]; iP = iP[window_ok(iP) & ~flat[iP]]
# map each placebo anchor to the preceding Sunday event's |G|
sun_ts = ts[aW]; pos = np.searchsorted(sun_ts, ts[iP], side="right") - 1
okp = pos >= 0; iP = iP[okp]; pos = pos[okp]
gP = np.abs(GW[pos]) * rng.choice([-1.0, 1.0], size=len(iP))
recent = (ts[iP] - sun_ts[pos]) < 6 * 86400; iP = iP[recent]; gP = gP[recent]
yP = yr[iP]
for nn, N in [("N12", 12), ("N72", 72)]:
    D, tie, anyf, kf, pnl = first_passage(iP, gP, N)
    parts = []
    for wn, (y0, y1) in W.items():
        m = (yP >= y0) & (yP <= y1); mean, se, n = ms(D[m]); parts.append(f"{wn} D̄ {mean:+.3f} (t {mean/se:+.2f}, n {n}・決着 {(D[m]!=0).mean()*100:.0f}%)")
    say(f"- プラセボ {nn}: " + "／".join(parts))

# ---------- 陽性対照（注入） ----------
say("\n## 陽性対照（外窓 WKND・N=72 に |G| の 25%／50% を N 本かけて参照側へ戻すドリフトを注入）")
m = (yW >= 2021)
for fr in [0.25, 0.5]:
    D, *_ = first_passage(aW[m], GW[m], 72, drift_frac=fr); mean, se, n = ms(D)
    say(f"- 注入 {fr*100:.0f}%: D̄ {mean:+.3f}（t {mean/se:+.2f}・n {n}）")
m = (yW <= 2020)
for fr in [0.25, 0.5]:
    D, *_ = first_passage(aW[m], GW[m], 72, drift_frac=fr); mean, se, n = ms(D)
    say(f"- 注入 {fr*100:.0f}%（在）: D̄ {mean:+.3f}（t {mean/se:+.2f}・n {n}）")

# ---------- 伝承値の RW 比較（記述） ----------
say("\n## 伝承「ギャップは N 内に埋まる」の率 vs 同距離 CONT 水準への到達率（対称なら同じ）")
for lab, a, G, yrs in [("WKND", aW, GW, yW), ("DAILY", aD, GD, yD)]:
    for nn, N in NS.items():
        s = np.sign(G); ag = np.abs(G) / 1e4; J = a[:, None] + np.arange(1, N + 1)[None, :]
        lh = np.log(hi[J]) - lc[a][:, None]; ll = np.log(lo[J]) - lc[a][:, None]
        fill_any = np.where(s[:, None] > 0, ll <= -ag[:, None], lh >= ag[:, None]).any(1)
        cont_any = np.where(s[:, None] > 0, lh >= ag[:, None], ll <= -ag[:, None]).any(1)
        parts = []
        for wn, (y0, y1) in W.items():
            mm = (yrs >= y0) & (yrs <= y1); d = fill_any[mm].astype(float) - cont_any[mm]; mean, se, n = ms(d)
            parts.append(f"{wn} 埋め {fill_any[mm].mean()*100:.0f}%／継続 {cont_any[mm].mean()*100:.0f}%（差 {mean*100:+.1f} pp t {mean/se:+.2f}）")
        say(f"- {lab} {nn}: " + "／".join(parts))

say(f"\n- 実行時間 {time.time()-T0:.1f} s・scan 無し・MT5 無し・外部通信無し・seed 20261110")
with open(OUT, "w", encoding="utf-8") as f: f.write(buf.getvalue())
print("->", OUT)
