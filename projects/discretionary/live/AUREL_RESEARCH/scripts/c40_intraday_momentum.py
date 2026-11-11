# -*- coding: utf-8 -*-
"""
[cycle40 研究レーン 2026-11-11] 【探索・参加者行動／日内の資金移動（収益機会の源泉マップ §8 新行: 日内モメンタム＝引け前の遅い参加者）】
公開文献「Market intraday momentum」（Gao–Han–Li–Zhou 2018 JFE）: 米株 ETF の**最初の半時間リターン（前日引け → 10:00 ET）が最後の半時間
（15:30 → 16:00 ET）を正に予測**する（SPY 1993-2013 β ≈ 0.07〜0.09・t ≈ 4）。機構 = ①朝の情報に**遅れて反応する参加者**（infrequent
rebalancing・Bogousslavsky 2016）②引けに集中する**レバレッジ ETF／ポートフォリオ保険の機械的リバランス**（朝が上げた日ほど引けで買う）
③MOC（引け成行）注文の集中。文献は株式が本拠。金では GLD／レバレッジ金 ETP（UGL/GLL）の引け 16:00 ET リバランスと COMEX 決済 13:30 ET
が同じ機構の候補。方法論 ㉝（本拠市場で先に当てる）: **US500 で立たなければ金で探さない**。入口フィルタではない・本番とは独立の市場記述。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/US500_m5_close.npz（2012-01〜2026-06-09・bid）・US100（複製・記述）・XAU_m5_close.npz（bid）・refute_c4 json（ゲート ㉛）。
  既存キャッシュのみ・scan 無し・M5 読込なし・MT5 無し・外部通信無し。読込後に min/max 時刻（⑩）・曜日別 flat 比率（⑪）を印字。
価格の時計: c22/c38 と同じ P(T) = ts == T−300 の足の close（格子の穴は NaN・⑫）。取引日 D = ET 現地の月〜金（暦）。
窓（bp・対数差・ET）: FIRST_B = 前営業日 16:00 → D 10:00（文献定義・夜間込み・主）／FIRST_A = 09:30 → 10:00（純日内・副）／
  SECOND = 10:00 → 10:30（負の対照: 文献では予測されない）／MID = 12:00 → 12:30（プラセボ被説明変数）／TWELFTH = 15:00 → 15:30（文献の第 2 予測子・副）／
  LAST = 15:30 → 16:00（被説明変数・主）。金の代替（記述）: COMEX 窓 CFIRST = 08:20 → 08:50／CLAST = 13:00 → 13:30（決済 13:30 ET）。
有効日 = 使う窓が全部有限 ∧ LAST ≠ 0 ∧ FIRST ≠ 0（stale・祝日・13:00 早引けを除く）。窓×期間の厳密 0 比率を印字（>20% は判定不可・㉒）。
統計: OLS LAST = α + β·FIRST（bp/bp）・HC1 t・Newey–West(5) t・MDE = 2·se_HC1・R²。置換帰無（⑨）= FIRST を**週循環シフト**（平日索引 5k・2000 回・窓内循環）
  → 片側 p（β ≥ 観測）と帰無 sd。符号戦略 S = mean(sign(FIRST)·LAST) bp/日（t・正の日比率）＝受取りの大きさ。|FIRST| 上位三分位の β も印字（文献: 大きい朝ほど強い）。
窓: 在 2012-20／外 2021-26H1／近年 2024-26H1（D2・窓別・16 年一括は使わない）。判定は在で決め外で確認。年別 β も印字（記述）。
判定（Bonferroni(2)・名目 0.025・主 2 セル）:
  C1 US500（本拠）PASS = β_B >0 ∧ 在 HC1 t≥2 ∧ 置換 p<0.025 ∧ 外 同符号 t≥1.5。
  C2 XAU（金・同じ ET 窓）PASS = 同条件。**C1 が null なら C2 は「本拠で立たない効果を金で探さない」（㉝）＝記述のみ**。
  負の対照: FIRST_B → SECOND・FIRST_B → MID は |t|<2 が期待（立てば「朝の続き（日内トレンド）」であって引け固有ではない）。
決着可能性（㉝・数字を見る前）: 半時間 sd ≈ 25〜35 bp・FIRST_B sd ≈ 60〜80 bp・在 n ≈ 2100 日 → se_β ≈ sd_L/(sd_F·√n) ≈ 0.01 → 文献級 β 0.07 は 在 t ≈ 6・外 (n≈1300) t ≈ 4.5＝決着可能。
  金は半時間 sd ≈ 20〜30 bp・FIRST_B（18 時間）sd ≈ 70〜90 bp で同程度。
陽性対照: 在 US500 の LAST に 0.05·FIRST_B を注入して β の t が ≥2 増えること（検出力）。会計対照: FIRST_A + SECOND + … の分解は使わない（窓は非重複だが全日を覆わない）。
経済的大きさ（事前に書く）: 符号戦略 S（bp/日）vs 往復コスト = US500 現物時間 spread ≈ 0.4〜1 bp（c14 US100 1.44 pt の桁・US500 口座値は要取得）・金 0.16 USD ≈ 0.4〜0.9 bp。swap 無し（日内）。
ゲート ㉛（本番接続・在 2012-20 のみ印字）: scan 本（refute_c4）で建玉が D の [10:00, 15:30) ET にある本を、金の FIRST_B(D) の符号と side の整合（ALIGNED = BUY∧FIRST>0 or SELL∧FIRST<0）で分け
  Δμ(R*)（ALIGNED − AGAINST・Welch t）・Δx（pp）・x0 look-ahead 対照を印字。在 |Δμ| <0.048R → 「決着不能・外は走らせない」。
事前の最重大反証: (1) 文献の効果は 2008-09 危機期に集中し 2013 以降は弱い（後続研究）→ 在 2012-20 でも既に薄い可能性＝null は「文献の時代効果」と読む。
  (2) bid のみ・Dukascopy 1 社・US500 は CFD（SPY/ES ではない・MOC の板は無い）。(3) 2020 夏 68 営業日欠落（㊵）。(4) FIRST_B は夜間込み＝「夜間ドリフトの続き」と
  「朝の反応の遅れ」を分けられない → FIRST_A（純日内）を併記。(5) 引け前半時間はボラが高い（ハザード地図 c21）＝β の分散は大きいが se に織込み済み。
  (6) 金の 16:00 ET は現物の引けではない（COMEX 決済 13:30・LBMA PM 10:00）→ COMEX 窓を併記。昇格候補・入口/出口規則の提案ではない。seed 20261111。
"""
import os, time, math, json
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c40_intraday_momentum_result.md"); L = []
NY = "America/New_York"; SEED = 20261111; rng = np.random.default_rng(SEED); NPERM = 2000
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle40] 日内モメンタム（最初の半時間 → 最後の半時間・Gao et al. 2018）US500 本拠 → 金 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c40_intraday_momentum.py)")

WD = ['月','火','水','木','金','土','日']
def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
    t = pd.to_datetime(ts, unit="s", utc=True)
    r = np.diff(np.log(cl)); fl = np.r_[False, r == 0]; wd = t.weekday.to_numpy()
    say(f"- {sym}: {len(ts)} 本 {t[0]}〜{t[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {fl.mean()*100:.1f}%・曜日別 " + " ".join(f"{WD[w]}{fl[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
    return ts, cl
def epoch_et(dates, hour, minute, day_offset=0):
    naive = dates + pd.Timedelta(days=day_offset) + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300).astype(np.int64); pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out

dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy(); lg = np.log
ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

def windows(ts, cl):
    P = lambda h, m: price_at(ts, cl, epoch_et(dates, h, m))
    p16 = P(16, 0); p16_prev = np.r_[np.nan, p16[:-1]]
    W = {}
    W["FIRST_B"] = (lg(P(10, 0)) - lg(p16_prev)) * 1e4
    W["FIRST_A"] = (lg(P(10, 0)) - lg(P(9, 30))) * 1e4
    W["SECOND"] = (lg(P(10, 30)) - lg(P(10, 0))) * 1e4
    W["MID"] = (lg(P(12, 30)) - lg(P(12, 0))) * 1e4
    W["TWELFTH"] = (lg(P(15, 30)) - lg(P(15, 0))) * 1e4
    W["LAST"] = (lg(p16) - lg(P(15, 30))) * 1e4
    W["CFIRST"] = (lg(P(8, 50)) - lg(P(8, 20))) * 1e4
    W["CLAST"] = (lg(P(13, 30)) - lg(P(13, 0))) * 1e4
    return W

def ols(y, x):
    """OLS y = a + b x ; HC1 t, NW(5) t, se_HC1, R2, n"""
    m = np.isfinite(y) & np.isfinite(x); y, x = y[m], x[m]; n = len(y)
    if n < 30: return dict(n=n, b=np.nan, t=np.nan, tnw=np.nan, se=np.nan, r2=np.nan)
    xc = x - x.mean(); yc = y - y.mean(); sxx = xc @ xc; b = (xc @ yc) / sxx; e = yc - b * xc
    se = math.sqrt((xc ** 2 @ e ** 2) / sxx ** 2 * n / (n - 2))
    g = xc * e; s = g @ g / n
    for l in range(1, 6): s += 2 * (1 - l / 6) * (g[l:] @ g[:-l]) / n
    senw = math.sqrt(max(s, 1e-18) / n) * n / sxx
    r2 = 1 - (e @ e) / (yc @ yc)
    return dict(n=n, b=b, t=b / se, tnw=b / senw, se=se, r2=r2)
def fo(o, mde=True):
    if not np.isfinite(o["b"]): return f"—(n{o['n']})"
    return f"β {o['b']:+.3f} (t {o['t']:+.2f}, NW {o['tnw']:+.2f}" + (f", MDE {2*o['se']:.3f}" if mde else "") + f", R² {o['r2']*100:.1f}%, n{o['n']})"
def perm_p(y, x, m, obs):
    idx = np.where(m)[0]; xv = x[idx]; yv = y[idx]; nweeks = len(idx) // 5
    ks = rng.integers(1, max(2, nweeks), size=NPERM); out = np.empty(NPERM)
    for j, k in enumerate(ks):
        xs = np.roll(xv, 5 * int(k)); mm = np.isfinite(xs) & np.isfinite(yv)
        xc = xs[mm] - xs[mm].mean(); yc = yv[mm] - yv[mm].mean(); out[j] = (xc @ yc) / (xc @ xc)
    return (out >= obs).mean(), np.std(out)
def sign_strat(y, x, m):
    mm = m & np.isfinite(y) & np.isfinite(x) & (x != 0); s = np.sign(x[mm]) * y[mm]; n = len(s)
    return dict(n=n, mean=s.mean(), t=s.mean() / (s.std(ddof=1) / math.sqrt(n)), pos=(s > 0).mean(), absmean=np.abs(y[mm]).mean())

RES = {}
for sym in ("US500", "US100", "XAU"):
    say(f"\n## {sym}")
    ts, cl = load(sym); W = windows(ts, cl)
    valid = np.ones(N, bool)
    for k in ("FIRST_B", "FIRST_A", "SECOND", "MID", "TWELFTH", "LAST"): valid &= np.isfinite(W[k])
    valid &= (W["LAST"] != 0) & (W["FIRST_B"] != 0) & (W["FIRST_A"] != 0)
    say(f"- 取引日候補 {N}・有効日 {valid.sum()}（6 窓有限 ∧ LAST≠0 ∧ FIRST≠0）・年別有効日 " + " ".join(f"{y}:{int((valid&(yr==y)).sum())}" for y in range(2012, 2027)))
    say("- 窓の厳密 0 比率（候補日中・㉒）: " + "・".join(f"{k} {np.mean(np.isfinite(W[k]) & (W[k]==0))*100:.1f}%/NaN {np.mean(~np.isfinite(W[k]))*100:.1f}%" for k in ("FIRST_B","FIRST_A","SECOND","MID","TWELFTH","LAST","CLAST")))
    say("- 窓 sd（在 有効日・bp）: " + "・".join(f"{k} {np.nanstd(W[k][valid&(yr<=2020)]):.0f}" for k in ("FIRST_B","FIRST_A","SECOND","MID","TWELFTH","LAST")))
    n_in = int((valid & (yr <= 2020)).sum()); n_out = int((valid & (yr >= 2021)).sum())
    sdL = np.nanstd(W["LAST"][valid & (yr <= 2020)]); sdF = np.nanstd(W["FIRST_B"][valid & (yr <= 2020)])
    say(f"- 決着可能性（㉝・事前の近似）: se_β ≈ sd_L/(sd_F·√n) 在 {sdL/(sdF*math.sqrt(max(n_in,1))):.4f}／外 {sdL/(sdF*math.sqrt(max(n_out,1))):.4f} → 文献級 β 0.07 の期待 t 在 {0.07/(sdL/(sdF*math.sqrt(max(n_in,1)))):.1f}／外 {0.07/(sdL/(sdF*math.sqrt(max(n_out,1)))):.1f}")
    say("\n| 期間 | n | 主 LAST~FIRST_B | 副 LAST~FIRST_A | 副 LAST~TWELFTH | 負の対照 SECOND~FIRST_B | プラセボ MID~FIRST_B | 符号戦略 S bp/日 (t, 正%) | |FIRST_B| 上位 1/3 の β | 置換 p / 帰無 sd |")
    say("|---|---|---|---|---|---|---|---|---|---|")
    for lab, lo, hi in ERAS:
        m = valid & (yr >= lo) & (yr <= hi)
        o1 = ols(W["LAST"][m], W["FIRST_B"][m]); oa = ols(W["LAST"][m], W["FIRST_A"][m]); o12 = ols(W["LAST"][m], W["TWELFTH"][m])
        on = ols(W["SECOND"][m], W["FIRST_B"][m]); om = ols(W["MID"][m], W["FIRST_B"][m])
        ss = sign_strat(W["LAST"], W["FIRST_B"], m)
        thr = np.nanquantile(np.abs(W["FIRST_B"][m]), 2 / 3); mt = m & (np.abs(W["FIRST_B"]) >= thr); ot = ols(W["LAST"][mt], W["FIRST_B"][mt])
        p1, sdp = perm_p(W["LAST"], W["FIRST_B"], m, o1["b"])
        RES[(sym, lab)] = dict(o1=o1, oa=oa, p1=p1, ss=ss, m=m)
        say(f"| {lab} | {m.sum()} | **{fo(o1)}** | {fo(oa, False)} | {fo(o12, False)} | {fo(on, False)} | {fo(om, False)} | {ss['mean']:+.2f} (t {ss['t']:+.2f}, {ss['pos']*100:.0f}%, |LAST| {ss['absmean']:.1f}) | {fo(ot, False)} | {p1:.3f} / {sdp:.3f} |")
    # positive control (in-sample)
    m = valid & (yr <= 2020); yinj = W["LAST"].copy(); yinj[m] += 0.05 * W["FIRST_B"][m]; oinj = ols(yinj[m], W["FIRST_B"][m])
    say(f"- 陽性対照（在・LAST に 0.05·FIRST_B を注入）: t {RES[(sym,'在 2012-20')]['o1']['t']:+.2f} → {oinj['t']:+.2f}")
    # yearly
    say("- 年別 β(LAST~FIRST_B) (HC1 t): " + " ".join(f"{y}:{ols(W['LAST'][valid&(yr==y)], W['FIRST_B'][valid&(yr==y)])['b']:+.3f}({ols(W['LAST'][valid&(yr==y)], W['FIRST_B'][valid&(yr==y)])['t']:+.1f})" for y in range(2012, 2027)))
    if sym == "XAU":
        say("\n### 金の COMEX 窓（記述）: CLAST 13:00→13:30 ~ CFIRST 08:20→08:50／CLAST ~ FIRST_B（前日 16:00 → 10:00）")
        vc = np.isfinite(W["CFIRST"]) & np.isfinite(W["CLAST"]) & (W["CLAST"] != 0) & (W["CFIRST"] != 0)
        for lab, lo, hi in ERAS:
            m = vc & (yr >= lo) & (yr <= hi); mb = m & np.isfinite(W["FIRST_B"])
            say(f"- {lab}: CLAST~CFIRST {fo(ols(W['CLAST'][m], W['CFIRST'][m]))}／CLAST~FIRST_B {fo(ols(W['CLAST'][mb], W['FIRST_B'][mb]), False)}／符号戦略 {sign_strat(W['CLAST'], W['CFIRST'], m)['mean']:+.2f} bp/日")
        WX = W
    if sym == "US500": WE = W

# ---------- gate ㉛ ----------
say("\n## ゲート ㉛（本番接続・在 2012-20 のみ印字）")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["ft"] = FT / tr["risk"]
tr["Rs"] = tr["R"] + tr["ft"] * tr["dec"]; tr["q"] = (1 - tr["ft"]) / (1 + tr["b"]); tr["x"] = (tr["exit"] == "TP").astype(float) - tr["q"]
t10 = epoch_et(dates, 10, 0); t1530 = epoch_et(dates, 15, 30); et_ = tr["entry_time"].to_numpy(float)
pos = np.searchsorted(t10, et_, side="right") - 1; ok = (pos >= 0) & np.isfinite(t1530[np.clip(pos, 0, N - 1)]) & (et_ < t1530[np.clip(pos, 0, N - 1)]) & (et_ >= t10[np.clip(pos, 0, N - 1)])
fb = WX["FIRST_B"][np.clip(pos, 0, N - 1)]; ok &= np.isfinite(fb) & (fb != 0)
tr["ok"] = ok; tr["fb"] = fb
tr["aligned"] = np.where(ok, ((tr["side"] == "BUY") & (tr["fb"] > 0)) | ((tr["side"] == "SELL") & (tr["fb"] < 0)), False)
ins = tr[tr.ok & (tr.year >= 2012) & (tr.year <= 2020)]
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); d_ = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d_, d_ / se, se
A, B = ins[ins.aligned], ins[~ins.aligned]
dm, tm, sem = welch(A.Rs, B.Rs); dx, tx, _ = welch(A[A.dec].x, B[B.dec].x); d0, t0, _ = welch(A.x0, B.x0)
say(f"- 在 2012-20 の scan 本で建玉が D の [10:00,15:30) ET: {len(ins)}（ALIGNED {len(A)}／AGAINST {len(B)}・全 scan 本中 付与 {tr.ok.mean()*100:.1f}%）")
say(f"- ALIGNED−AGAINST: Δμ(R*) **{dm:+.3f}R (t {tm:+.2f}, se {sem:.3f}, MDE {2*sem:.3f})**・Δx {dx*100:+.2f} pp (t {tx:+.2f})・look-ahead 対照 x0 Δ {d0:+.3f} (t {t0:+.2f})")
gate = "通過（外を印字）" if abs(dm) >= 0.048 else "**不通過（在 |Δμ| <0.048R → 決着不能・外は走らせない）**"
say(f"- ゲート ㉛: {gate}")
if abs(dm) >= 0.048:
    for lab, lo, hi in ERAS[1:]:
        o = tr[tr.ok & (tr.year >= lo) & (tr.year <= hi)]; a_, b_ = o[o.aligned], o[~o.aligned]
        if len(a_) >= 20: dm2, tm2, se2 = welch(a_.Rs, b_.Rs); say(f"  - {lab}: Δμ {dm2:+.3f}R (t {tm2:+.2f}, n {len(a_)}/{len(b_)})")

# ---------- verdict ----------
say("\n## 判定（事前固定の規則で機械的に・Bonferroni(2)）")
def verdict(sym):
    i, o = RES[(sym, "在 2012-20")], RES[(sym, "外 2021-26H1")]
    ok_ = (i["o1"]["b"] > 0) and (i["o1"]["t"] >= 2) and (i["p1"] < 0.025) and (o["o1"]["b"] > 0) and (o["o1"]["t"] >= 1.5)
    return ok_, i, o
c1, i1, o1 = verdict("US500")
say(f"- C1 US500（本拠）: 在 {fo(i1['o1'])} 置換 p {i1['p1']:.3f}／外 {fo(o1['o1'])} → **{'PASS' if c1 else 'null'}**")
c2, i2, o2 = verdict("XAU")
note = "" if c1 else "（㉝: 本拠 null → 金の結果は記述のみ・PASS と呼ばない）"
say(f"- C2 XAU（同じ ET 窓）: 在 {fo(i2['o1'])} 置換 p {i2['p1']:.3f}／外 {fo(o2['o1'])} → **{'PASS' if (c2 and c1) else ('規則上 PASS だが ㉝ で記述' if c2 else 'null')}**{note}")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
