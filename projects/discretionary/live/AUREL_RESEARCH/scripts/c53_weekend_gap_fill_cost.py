# -*- coding: utf-8 -*-
"""
[cycle53 研究レーン 2026-11-19] 【深化・執行・path】週末をまたいで生きた本（金曜 16:55 ET 引けで未決着 → 日曜再開足で決着）の
「紙の R」と「実の R（再開足 open で約定）」の差 ＝ 週末ギャップの執行コスト（SL 側の超過損）と窓（TP 側の棚ぼた）を、
scan キャッシュ 19404 本（refute_c4 json＋refute_c2_fullpaths.npz）と XAU_m5_ohlc.npz だけで測る。
c52 (11-19 06:40) 次の枝 (a)・反証 09:30 が「唯一の決着路・優先度 上げ」とした問い。入口/出口規則の提案ではなくコストの計上。

=== 事前固定（この docstring を書いてから数字を見る・seed 20261119）===
データ: data/refute_c4_scan_paths_2010_2026.json（trades・entry_time 昇順に sort）、data/refute_c2_fullpaths.npz（hiR/loR/clR/off・足 j の時刻 = entry_time+300j
  は同セッション内で厳密・c18/c21 で 100% 確認）、data/macro/XAU_m5_ohlc.npz（bid・完全格子・穴 19 → ts 一致で参照 ⑫）。
母集団 F（金曜セッション建玉）: 建玉の ET セッション日 = (ET+6h) の暦日 が金曜。金曜 16:55 ET 足（最終取引足・c17）の ts を ts_c、k_c = (ts_c − entry_time)/300。
  W（週末横断本）= F ∧ hold ≥ k_c + m（m = m5_loader 格子が金曜引け後に持つ足数のオフセット・下記で実測）。
  **整合（⑩⑫・必須）**: (i) 建玉価格 entry は json に無い → 同セッション足 j=1..3 の clR と npz close から entry = close_j − SGN·clR_j·risk を推定し、3 本の範囲 ≤0.02 USD を要求。
  (ii) clR[k_c] と npz 16:55 足 close の一致率（|差|≤0.02 USD）を印字。(iii) 再開足 = ts_c の後で最初に high≠low または close≠前 close の足。
  m ∈ {1,2,3,12,13,14} について hold>k_c+m の本で clR[k_c+m] と再開足 close の一致率を印字し、最大の m を採用。採用 m の一致率 <95% なら全判定 inconclusive
  （needs cache: 時刻索引つき path）。
量（本 i ∈ W・SGN=+1 BUY/−1 SELL・ft = FEED_TOL/risk・R* = R + ft·1{SL,TP}）:
  SL 価格 = entry − SGN·risk、TP 価格 = entry + SGN·b·risk。再開足 open = O_r。
  決着が再開足（hold == k_c+m）∧ exit=SL ∧ SGN·(O_r − SL) < 0（ギャップが SL を飛び越えた）→ 実 R_real = SGN·(O_r − entry)/risk、超過損 X_SL = R* − R_real (≥0)。
  決着が再開足 ∧ exit=TP ∧ SGN·(O_r − TP) > 0 → 実 R_real = SGN·(O_r − entry)/risk、棚ぼた X_TP = R_real − R* (≥0)。
  それ以外 X = 0。純コスト C_i = X_SL − X_TP（正 = 実が紙より悪い）。
  **紙の記帳の確認（判定の前提）**: 再開足 SL の json R が −(1−ft) 近傍に張り付いているか（＝scan はギャップを無視して SL 価格で記帳）を分布で印字。
  もし R がギャップ分を既に反映していれば X_SL は定義上 0 となり本サイクルの問いは消える（その場合は「scan は既にギャップを計上」と記録して終える）。
窓（建玉年・D2・16 年一括なし）: 在 2013-20（c28/c17 の衛生: 日曜再開 18:00 ET が安定するのは 2013+）／外 2021-26H1／近年 2024-26H1。2010-12 は参考列。
判定（主・H_W）: 「週末ギャップの純コストは本番の n* を動かす大きさか」。
  PASS（コストは実在し重い）= 在 ∧ 外 とも mean(C | W) ≥ 0.05R ∧ **週末クラスタ bootstrap（同じ週末の本は同じギャップを受ける・5000）95% 下限 > 0**
  ∧ 全本当たり ΣC/N_all ≥ 0.005R（実測コスト 0.03R/本 の 1/6）。
  null（軽い）= いずれか不成立。どちらでも MDE（2·se_cluster）を R で添える。
副（H_W2・非対称の検査＝最有力の反対仮説）: 週末横断本の「SL を飛ばされる確率」は幾何（SL 距離 d_SL = SGN·(C_fri − SL)、TP 距離 d_TP）で決まる無情報ギャップの
  鏡像確率と同じか。D = P(−SGN·G > d_SL) − P(+SGN·G > d_SL)（G = O_r − C_fri・同距離の鏡像）。|D| の 95% クラスタ CI が 0 を含めば「ギャップは本の側に無差別」。
  同様に TP 側 D_TP。
記述: 横断率 |W|/|F|・|W|/N・建玉 ET 時刻帯別横断率、再開足決着率とその exit 内訳、ギャップ飛び越え率、G の分布（bp・R）、受け取ったドリフト mean(SGN·G/risk)、
  C の分布（p50/p90/max）、年別 ΣC、SL 超過 vs TP 棚ぼた の内訳、金曜 16:55 足で決着した本（最終印字の疑い・c18）の数、SELL 側 ask 補正（スプレッド 0.21 を SL fill に加算）の感度。
陽性対照（⑦）: W の再開足 open を全本 SL の 0.5R 外側に置き換え → 推定器が mean C ≈ +0.5·P(exit=SL at reopen) を返すこと。
ゲート ㉛（記述のみ）: W vs F∖W の R* 差は「生存選択」（hold 長い本）で定義上バイアス → 条件づけとして読まない・印字のみ。
事前の最重大反証（数字を見る前）: (i) Dukascopy bid の再開足 open は実ブローカーの再開 tick と別物（stale 0.21・ギャップ時の約定規則）。(ii) 2010-12 は再開が早い（除外列）。
  (iii) SL 側のみ数えると片手落ち → TP 棚ぼたを同時に計上（H_W2）。(iv) 週末横断本は長保有に選択されており、n が小さく 1〜2 本の大ギャップが平均を支配し得る
  → p50/p90/max と LOO 最大 1 本除外を併記。(v) 再開足の 2 本は bid 正常化の人工物（c28 ②）→ open でなく「再開足 close」で埋めた感度も併記。
入力は既存キャッシュのみ・多年 scan 無し・M5 原本読込なし・MT5 無し・外部通信無し・書込は data/c53_* のみ。
"""
import os, json, time, sys
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c53_weekend_gap_fill_cost_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261119)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle53] 週末横断本の紙実差（週末ギャップの執行コスト）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c53_weekend_gap_fill_cost.py)")

# ---------- trades ----------
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
X = pd.DataFrame(J["trades"]).sort_values("entry_time", kind="stable").reset_index(drop=True)
# 同時刻の本（entry_time 重複 4 組）は npz の off 順と stable sort が食い違い得る → off の hold 列に合わせて組内を並べ替える（⑫）
_z0 = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); _d = np.diff(_z0["off"].astype(np.int64)) - 1
_h = X["hold"].to_numpy().astype(int); _et = X["entry_time"].to_numpy()
_fix = 0
for _t in np.unique(_et[pd.Series(_et).duplicated(keep=False).to_numpy()]):
    _g = np.where(_et == _t)[0]
    if not np.array_equal(_h[_g], _d[_g]):
        _perm = [int(_g[list(_h[_g]).index(v)]) for v in _d[_g]]; X.iloc[_g] = X.iloc[_perm].to_numpy(); _fix += 1
X = X.reset_index(drop=True)
N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy(); B = X["b"].to_numpy()
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; hiR = z["hiR"]; loR = z["loR"]; off = z["off"].astype(np.int64)
assert len(off) - 1 == N and np.all(np.diff(off) == HOLD + 1), "fullpaths 規約不一致"
P = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz")); TS = P["ts"].astype(np.int64); O = P["open"]; H = P["high"]; LO = P["low"]; C = P["close"]
say(f"- 本 {N}・entry {pd.to_datetime(ET[0],unit='s').date()}〜{pd.to_datetime(ET[-1],unit='s').date()}・FEED_TOL {FT}・exit {dict(pd.Series(EXIT).value_counts())}・同時刻組の並べ替え {_fix} 組（off 規約 assert 通過）")
say(f"- npz {len(TS)} 足 {pd.to_datetime(TS[0],unit='s')}〜{pd.to_datetime(TS[-1],unit='s')} UTC・格子連続率 {np.mean(np.diff(TS)==300)*100:.3f}%（⑩⑫）")

def idx_of(ts):
    """ts 一致で index を返す（穴は −1）"""
    i = np.searchsorted(TS, ts); ok = (i < len(TS)) & (TS[np.minimum(i, len(TS)-1)] == ts)
    return np.where(ok, i, -1)

# ---------- 金曜セッション建玉 F ----------
e_ny = pd.to_datetime(ET, unit="s", utc=True).tz_convert(NY)
sess = (e_ny + pd.Timedelta(hours=6)).date  # セッション日
sess_wd = pd.DatetimeIndex(pd.to_datetime(list(sess))).weekday.to_numpy()
isF = sess_wd == 4
# 金曜 16:55 ET の ts（セッション日 = 金曜の暦日）
fri = pd.DatetimeIndex(pd.to_datetime(list(sess)))
ts_c = np.array([pd.Timestamp(d.year, d.month, d.day, 16, 55, tz=NY).value // 10**9 if f else -1 for d, f in zip(fri, isF)], dtype=np.int64)
k_c = np.where(isF, (ts_c - ET) // 300, -1)
assert np.all(((ts_c - ET) % 300 == 0) | ~isF)
say(f"- 金曜セッション建玉 F: {isF.sum()}（{isF.mean()*100:.1f}%）・k_c 中央値 {np.median(k_c[isF]):.0f} 本・hold 中央値 F {np.median(HOLD[isF]):.0f}")

# ---------- entry 推定（整合 i） ----------
entry = np.full(N, np.nan); ent_rng = np.full(N, np.nan)
for i in range(N):
    js = [j for j in (1, 2, 3) if j <= HOLD[i]]
    ests = []
    for j in js:
        ii = idx_of(np.array([ET[i] + 300 * j]))[0]
        if ii >= 0: ests.append(C[ii] - SGN[i] * clR[off[i] + j] * RISK[i])
    if ests: entry[i] = np.median(ests); ent_rng[i] = max(ests) - min(ests)
okE = np.isfinite(entry) & (ent_rng <= 0.02)
say(f"- entry 推定: 可 {np.isfinite(entry).sum()}・3 本範囲 ≤0.02 USD {okE.sum()}（{okE.mean()*100:.1f}%）・範囲 中央値 {np.nanmedian(ent_rng):.4f} USD")

# ---------- 整合 ii/iii: 金曜引け足・再開足 ----------
cand = isF & (HOLD >= k_c + 1) & okE
ic = idx_of(np.where(cand, ts_c, TS[0]))
m_close = np.zeros(N, bool)
for i in np.where(cand & (ic >= 0))[0]:
    m_close[i] = abs(SGN[i] * clR[off[i] + k_c[i]] * RISK[i] + entry[i] - C[ic[i]]) <= 0.02
say(f"- 引け生存候補 (hold≥k_c+1): {cand.sum()}・16:55 足 clR 一致 {m_close[cand].sum()}/{cand.sum()}（{m_close[cand].mean()*100:.1f}%）")
# 再開足
reo = np.full(N, -1)
for i in np.where(cand & (ic >= 0))[0]:
    j = ic[i] + 1; lim = ic[i] + 288 * 4
    while j < lim and j < len(TS) and not (H[j] != LO[j] or C[j] != C[j - 1]): j += 1
    if j < lim and j < len(TS): reo[i] = j
hasR = reo >= 0
gap_h = np.where(hasR, (TS[np.maximum(reo, 0)] - ts_c) / 3600.0, np.nan)
say(f"- 再開足 検出 {hasR[cand].sum()}/{cand.sum()}・引け→再開 時間 中央値 {np.nanmedian(gap_h[cand]):.1f} h・p10 {np.nanpercentile(gap_h[cand],10):.1f}・p90 {np.nanpercentile(gap_h[cand],90):.1f}")
reo_ny = pd.to_datetime(TS[np.maximum(reo, 0)], unit="s", utc=True).tz_convert(NY)
rh = pd.Series(np.where(hasR, reo_ny.hour * 60 + reo_ny.minute, -1))
say(f"- 再開足 ET 時刻（分）上位: {dict(rh[cand & hasR].value_counts().head(6))}")
# m の実測
best_m, best_rate = None, -1
for m in (1, 2, 3, 12, 13, 14):
    sel = np.where(cand & hasR & (HOLD > k_c + m))[0]
    if len(sel) == 0: say(f"  m={m}: n 0"); continue
    hit = np.array([abs(SGN[i] * clR[off[i] + k_c[i] + m] * RISK[i] + entry[i] - C[reo[i]]) <= 0.02 for i in sel])
    say(f"  m={m}: hold>k_c+m の本 {len(sel)}・clR[k_c+m] と再開足 close 一致 {hit.mean()*100:.1f}%")
    if hit.mean() > best_rate: best_rate, best_m = hit.mean(), m
m = best_m
say(f"- 採用 m = {m}（一致率 {best_rate*100:.1f}%）{'' if best_rate >= 0.95 else ' → **<95%・以降は inconclusive**'}")
INCONC = best_rate < 0.95

# ---------- W と再開足決着 ----------
W = cand & hasR & m_close & (HOLD >= k_c + m)
at_reo = W & (HOLD == k_c + m)
# 決着足の hiR/loR と再開足 high/low の整合（決着本）
chk = []
for i in np.where(at_reo)[0]:
    hi_p = entry[i] + SGN[i] * hiR[off[i] + HOLD[i]] * RISK[i]; lo_p = entry[i] + SGN[i] * loR[off[i] + HOLD[i]] * RISK[i]
    hi_p, lo_p = max(hi_p, lo_p), min(hi_p, lo_p)
    chk.append(abs(hi_p - H[reo[i]]) <= 0.05 and abs(lo_p - LO[reo[i]]) <= 0.05)
chk = np.array(chk, bool)
say(f"- W（週末横断本）{W.sum()}・うち再開足で決着 {at_reo.sum()}・exit 内訳 {dict(pd.Series(EXIT[at_reo]).value_counts())}・決着足 hi/lo と再開足 high/low 一致 {chk.mean()*100 if len(chk) else float('nan'):.1f}%")
say(f"- 横断率: |W|/|F| {W.sum()/max(isF.sum(),1)*100:.2f}%・|W|/N {W.sum()/N*100:.3f}%・F∖W の決着 exit {dict(pd.Series(EXIT[isF & ~W]).value_counts())}")
# 金曜 16:55 足で決着した本（最終印字の疑い）
at_close = isF & okE & (HOLD == k_c)
say(f"- 金曜 16:55 足（最終印字）で決着した本 {at_close.sum()}・exit×side {dict(pd.Series(list(zip(EXIT[at_close], X['side'][at_close]))).value_counts())}")

# ---------- 紙の記帳確認 ----------
slr = at_reo & (EXIT == "SL"); tpr = at_reo & (EXIT == "TP")
say(f"- 紙の記帳: 再開足 SL の json R 分布 n {slr.sum()}: 中央値 {np.median(R[slr]) if slr.sum() else float('nan'):.3f}・min {R[slr].min() if slr.sum() else float('nan'):.3f}・max {R[slr].max() if slr.sum() else float('nan'):.3f}・"
    f"−(1−ft) 中央値 {np.median(-(1-ft[slr])) if slr.sum() else float('nan'):.3f}・|R+(1−ft)|≤0.01 の比率 {np.mean(np.abs(R[slr]+(1-ft[slr]))<=0.01)*100 if slr.sum() else float('nan'):.1f}%")
say(f"- 紙の記帳: 再開足 TP の json R − (b+ft): 中央値 {np.median(R[tpr]-(B[tpr]+ft[tpr])) if tpr.sum() else float('nan'):.3f}・|差|≤0.01 比率 {np.mean(np.abs(R[tpr]-(B[tpr]+ft[tpr]))<=0.01)*100 if tpr.sum() else float('nan'):.1f}%")
# 全 SL の記帳も参考
allSL = EXIT == "SL"
say(f"- 参考: 全 SL の |R+(1−ft)|≤0.01 比率 {np.mean(np.abs(R[allSL]+(1-ft[allSL]))<=0.01)*100:.1f}%（scan は SL 価格で記帳＝ギャップ無視 なら ≈100%）")

# ---------- 紙実差 ----------
SLp = entry - SGN * RISK; TPp = entry + SGN * B * RISK
Or = np.where(hasR, O[np.maximum(reo, 0)], np.nan); Cr = np.where(hasR, C[np.maximum(reo, 0)], np.nan)
Cf = np.where(ic >= 0, C[np.maximum(ic, 0)], np.nan)
G = Or - Cf  # 週末ギャップ（USD・open 基準）
def xcost(fill, spread_sell=0.0):
    """fill = 再開足の約定価格系列（open or close）。SELL の SL は ask で約定 → +spread"""
    Xs = np.zeros(N); Xt = np.zeros(N)
    f_sl = fill + np.where(SGN < 0, spread_sell, 0.0)
    g_sl = slr & (SGN * (f_sl - SLp) < 0)
    Xs[g_sl] = RSTAR[g_sl] - SGN[g_sl] * (f_sl[g_sl] - entry[g_sl]) / RISK[g_sl]
    g_tp = tpr & (SGN * (fill - TPp) > 0)
    Xt[g_tp] = SGN[g_tp] * (fill[g_tp] - entry[g_tp]) / RISK[g_tp] - RSTAR[g_tp]
    return Xs, Xt, g_sl, g_tp
Xs, Xt, g_sl, g_tp = xcost(Or)
Cnet = Xs - Xt
say(f"- ギャップ飛び越え: SL 側 {g_sl.sum()}/{slr.sum()}・TP 側 {g_tp.sum()}/{tpr.sum()}・W の |G| 中央値 {np.nanmedian(np.abs(G[W])):.2f} USD（{np.nanmedian(np.abs(G[W])/Cf[W])*1e4:.1f} bp）・G/risk 中央値 {np.nanmedian(np.abs(G[W])/RISK[W]):.3f}R")

# 週末キー（クラスタ）
wk = np.where(W, ts_c, -1)
def cl_boot(vals, keys, nb=5000):
    """週末クラスタ bootstrap の mean と 95%CI・クラスタ se"""
    u = np.unique(keys); groups = [vals[keys == k] for k in u]
    if len(u) < 2: return np.nan, (np.nan, np.nan), np.nan
    sums = np.array([g.sum() for g in groups]); ns = np.array([len(g) for g in groups])
    bs = np.empty(nb)
    for b in range(nb):
        pick = rng.integers(0, len(u), len(u)); bs[b] = sums[pick].sum() / ns[pick].sum()
    return vals.mean(), (np.percentile(bs, 2.5), np.percentile(bs, 97.5)), bs.std()

WIN = {"2010-12(参考)": (2010, 2012), "在 2013-20": (2013, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
say("\n## 主 H_W: 週末ギャップの純コスト C = X_SL − X_TP（R・W の本・週末クラスタ bootstrap 5000）")
say("| 窓 | N_all | F | W | 再開足決着 SL/TP | SL 飛越/TP 飛越 | mean C\\|W | 95%CI | se_cl | MDE | p50/p90/max X_SL | ΣX_SL | ΣX_TP | ΣC/N_all | LOO max |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
res = {}
for name, (y0, y1) in WIN.items():
    w = (YEAR >= y0) & (YEAR <= y1); Wi = W & w; Ni = w.sum()
    if Wi.sum() == 0: say(f"| {name} | {Ni} | {(isF&w).sum()} | 0 | | | | | | | | | | | |"); continue
    mu, ci, se = cl_boot(Cnet[Wi], wk[Wi])
    sl_i = slr & w; tp_i = tpr & w
    xs = Xs[Wi]; loo = (Cnet[Wi].sum() - Cnet[Wi].max()) / max(Wi.sum() - 1, 1)
    res[name] = dict(n=int(Wi.sum()), mu=mu, ci=ci, se=se, per_all=Cnet[Wi].sum() / Ni, sumSL=Xs[Wi].sum(), sumTP=Xt[Wi].sum())
    say(f"| {name} | {Ni} | {(isF&w).sum()} | {Wi.sum()} | {sl_i.sum()}/{tp_i.sum()} | {(g_sl&w).sum()}/{(g_tp&w).sum()} | {mu:+.4f} | [{ci[0]:+.4f},{ci[1]:+.4f}] | {se:.4f} | {2*se:.4f} | "
        f"{np.percentile(xs,50):.3f}/{np.percentile(xs,90):.3f}/{xs.max():.3f} | {Xs[Wi].sum():.3f} | {Xt[Wi].sum():.3f} | {Cnet[Wi].sum()/Ni:+.5f} | {loo:+.4f} |")
def verdict():
    ok = []
    for k in ("在 2013-20", "外 2021-26H1"):
        r = res.get(k)
        if r is None: return "inconclusive（窓に W 無し）"
        ok.append(r["mu"] >= 0.05 and r["ci"][0] > 0 and r["per_all"] >= 0.005)
    return "PASS（コストは実在し重い）" if all(ok) else "null（軽い／検出不能・MDE 参照）"
say(f"- **判定 H_W: {verdict()}**{'（整合 <95% → inconclusive）' if INCONC else ''}")

# 感度: 再開足 close で埋める／SELL の ask 補正 0.21
for lab, fill, sp in (("close 埋め", Cr, 0.0), ("open・SELL ask +0.21", Or, 0.21)):
    Xs2, Xt2, _, _ = xcost(fill, sp); C2 = Xs2 - Xt2
    row = []
    for name, (y0, y1) in WIN.items():
        Wi = W & (YEAR >= y0) & (YEAR <= y1)
        row.append(f"{name} {C2[Wi].mean():+.4f} (ΣSL {Xs2[Wi].sum():.2f}/ΣTP {Xt2[Wi].sum():.2f})" if Wi.sum() else f"{name} —")
    say(f"- 感度 {lab}: " + "・".join(row))

# ---------- 陽性対照 ----------
Of = Or.copy(); sel = slr
Of[sel] = SLp[sel] - SGN[sel] * 0.5 * RISK[sel]
Xs3, Xt3, _, _ = xcost(Of); C3 = Xs3 - Xt3
for name, (y0, y1) in WIN.items():
    Wi = W & (YEAR >= y0) & (YEAR <= y1)
    if Wi.sum():
        exp = 0.5 * (slr & Wi).sum() / Wi.sum() + (ft[slr & Wi].sum() - 0) / Wi.sum() * 0  # 期待 ≈ 0.5·P(SL at reopen)（ft 分は R* で相殺）
        say(f"- 陽性対照 {name}: 全再開 SL を 0.5R 外側で約定 → mean C {C3[Wi].mean():+.4f}（期待 ≈ {exp:+.4f} + 実 TP 棚ぼた分 −{Xt[Wi].sum()/Wi.sum():.4f}）")

# ---------- H_W2 非対称 ----------
say("\n## 副 H_W2: ギャップは本の側に無差別か（鏡像確率との差 D・週末クラスタ bootstrap）")
dSL = SGN * (Cf - SLp); dTP = SGN * (TPp - Cf)
thr_sl = (-SGN * G > dSL); mir_sl = (SGN * G > dSL)
thr_tp = (SGN * G > dTP); mir_tp = (-SGN * G > dTP)
say("| 窓 | W | P(SL 飛越) | P(鏡像) | D_SL | 95%CI | P(TP 飛越) | P(鏡像) | D_TP | 95%CI | mean SGN·G/risk | 95%CI | d_SL 中央値 R | d_TP 中央値 R |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for name, (y0, y1) in WIN.items():
    Wi = W & (YEAR >= y0) & (YEAR <= y1)
    if Wi.sum() < 5: continue
    d1 = (thr_sl[Wi].astype(float) - mir_sl[Wi].astype(float)); mu1, ci1, _ = cl_boot(d1, wk[Wi], 3000)
    d2 = (thr_tp[Wi].astype(float) - mir_tp[Wi].astype(float)); mu2, ci2, _ = cl_boot(d2, wk[Wi], 3000)
    drift = SGN[Wi] * G[Wi] / RISK[Wi]; mu3, ci3, _ = cl_boot(drift, wk[Wi], 3000)
    say(f"| {name} | {Wi.sum()} | {thr_sl[Wi].mean():.3f} | {mir_sl[Wi].mean():.3f} | {mu1:+.3f} | [{ci1[0]:+.3f},{ci1[1]:+.3f}] | {thr_tp[Wi].mean():.3f} | {mir_tp[Wi].mean():.3f} | {mu2:+.3f} | [{ci2[0]:+.3f},{ci2[1]:+.3f}] | "
        f"{mu3:+.4f} | [{ci3[0]:+.4f},{ci3[1]:+.4f}] | {np.median(dSL[Wi]/RISK[Wi]):.3f} | {np.median(dTP[Wi]/RISK[Wi]):.3f} |")
say("- 注: thr/mir は open 基準のギャップが Friday close からの SL/TP 距離を超えるか（決着の記帳とは独立の幾何・SL/TP に到達した本の定義とは別）")

# ---------- 記述 ----------
say("\n## 記述")
# 建玉 ET 時刻帯別の横断率（F 内）
eh = e_ny.hour.to_numpy()
rows = []
for h0 in range(0, 24, 2):
    s = isF & (eh >= h0) & (eh < h0 + 2)
    if s.sum(): rows.append(f"ET {h0:02d}-{h0+1:02d}: F {s.sum()}・W {(W&s).sum()}（{(W&s).sum()/s.sum()*100:.1f}%）")
say("- 建玉 ET 時刻帯別 横断率: " + "／".join(rows))
# 年別
say("- 年別 W・再開 SL・ΣX_SL・ΣX_TP・ΣC:")
for y in range(2010, 2027):
    Wi = W & (YEAR == y)
    if Wi.sum(): say(f"  {y}: W {Wi.sum()}・再開決着 {(at_reo&Wi).sum()}（SL {(slr&Wi).sum()}/TP {(tpr&Wi).sum()}）・飛越 SL {(g_sl&Wi).sum()}/TP {(g_tp&Wi).sum()}・ΣX_SL {Xs[Wi].sum():.3f}・ΣX_TP {Xt[Wi].sum():.3f}・ΣC {Cnet[Wi].sum():+.3f}")
# 大きい本
top = np.argsort(-Xs)[:8]
say("- X_SL 上位 8 本: " + "／".join(f"{pd.to_datetime(ET[i],unit='s').date()} {X['side'][i]} risk {RISK[i]:.2f} G {G[i]:+.2f} USD X_SL {Xs[i]:.3f}R" for i in top if Xs[i] > 0))
topt = np.argsort(-Xt)[:5]
say("- X_TP 上位 5 本: " + "／".join(f"{pd.to_datetime(ET[i],unit='s').date()} {X['side'][i]} risk {RISK[i]:.2f} G {G[i]:+.2f} USD X_TP {Xt[i]:.3f}R" for i in topt if Xt[i] > 0))
# 残り path（記述・選択バイアス明記）
for name, (y0, y1) in WIN.items():
    w = (YEAR >= y0) & (YEAR <= y1)
    if (W & w).sum() == 0: continue
    e_W = RSTAR[W & w] - np.array([clR[off[i] + k_c[i]] for i in np.where(W & w)[0]])
    say(f"- {name}: W の R* 平均 {RSTAR[W&w].mean():+.3f}（n {(W&w).sum()}）vs F∖W {RSTAR[isF&~W&w].mean():+.3f}（n {(isF&~W&w).sum()}）vs 全 {RSTAR[w].mean():+.3f}・W の引け以降の残り path e 平均 {e_W.mean():+.3f}（cl_kc 平均 {(RSTAR[W&w]-e_W).mean():+.3f}）＝生存選択つき記述・条件づけとして読まない")
# 本番換算
for name in ("外 2021-26H1", "近年 2024-26H1"):
    r = res.get(name)
    if r: say(f"- {name} 本番換算: 全本当たり純コスト {r['per_all']:+.5f}R/本 → 週 30 本で {r['per_all']*30:+.4f}R/週・年 {r['per_all']*30*52:+.3f}R（実測コスト 0.03R/本 の {abs(r['per_all'])/0.03*100:.1f}%）")

say(f"\n- 実行 {time.time()-T0:.1f} s・入力 = refute_c4 json＋refute_c2_fullpaths.npz＋XAU_m5_ohlc.npz のみ・多年 scan 無し・MT5 無し・外部通信無し・seed 20261119")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
