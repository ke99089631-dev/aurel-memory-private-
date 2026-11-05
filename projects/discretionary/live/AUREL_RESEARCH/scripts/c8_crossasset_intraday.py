# -*- coding: utf-8 -*-
"""
[cycle8 研究レーン] 2026-11-06 — 【探索・市場横断（イントラデイ）】建玉直前の米株指数（US500・US100 の Dukascopy M1）の
同時刻の動きは、金の再加速（壁→壁）の R を条件づけるか（リスクオフ・ヘッジ需要 → 金への資金移動 の仮説）

=== 事前固定（この docstring を書いてから数字を見る） ===
背景: cycle5（11-05）は日次マクロの「前日の動き」で null（日次粒度の限界と明記）。DATA_MAP §6 の本命は
      「建玉時点の同日イントラデイ共変動」。本サイクルで AssetEmpire dukas/ を棚卸しした結果、
      EURUSD M1 チャンクは 59 本中 57 本が 0 バイト（ドル代理は不可・needs data）、US500/US100 M1 は 2012-01〜2026-06 が実在。
      → 金に効く外部要因のうち「株（リスク選好）」をイントラデイで初めて検証できる。
経済仮説: 金は危機時の安全資産（safe haven は平時でなく尻尾で発現: Baur & Lucey 2010 の条件付き安全資産）。
      直前の株の急落（リスクオフ）→ 金への資金移動 → 金の上方向の壁抜けが走る（BUY が有利）。株の急騰 → 逆。
      対立仮説: (a) 金と株の相関は時代で符号が変わる（流動性危機では同時下落）→ 整合の向きは一定でない。
      (b) 見える効果は金自身の直前リターン（モメンタム）の漏れ → 金自身の整合を競合セルとして同時に出す。
      (c) 株の大きな動き＝ボラ高の時間帯であって、向きに依らず walls が走る/壊れるだけ → 大きさ形（F_M）を分けて見る。
データ（既存ファイルのみ・scan 無し・path 再構築無し・MT5 無し・外部通信無し）:
  - 再加速 closed 19404 本: data/refute_c4_scan_paths_2010_2026.json（entry_time=UTC epoch・建玉足の開始時刻、R gross、side、year、jh）。
  - US500/US100 M1 bid: AssetEmpire/empire/research/dukas/download/usa500idxusd / usatechidxusd -m1-bid-2012-01-01-2026-07-01.csv
    （読取のみ・M5 close に集約し data/macro/<SYM>_m5_close.npz に保存＝再利用キャッシュ）。
  - 金 XAUUSD M1 chunks（m5_loader と同じ入力）→ 同じく M5 close キャッシュ。全読込 ≈20 s 想定（多年 scan ではない）。
特徴量（look-ahead なし）: t_e = entry_time − 300（建玉足の 1 本前の足ラベル＝その close は entry_time に既知）。
  ret_H(S) = log c_S(t_e) − log c_S(t_e − H)、H ∈ {4h, 24h}。asof backward、c_S(t_e) の鮮度 ≤2h（株の閉場帯は NaN で除外）、
  c_S(t_e−H) は tolerance 3 日（週末跨ぎは直前値）。
  F_A 整合: aligned = (BUY ∧ ret<0) ∨ (SELL ∧ ret>0)（リスクオフ→金買い の向き）。予測: diff(aligned − opposed) > 0。
  F_M 大きさ: |ret_H| ≥ 直近 250 日（時間足で計算・当時点まで）の 80% 点。予測: diff(large − rest) > 0（ストレス時に金の壁→壁が走る）。
  主セル: US500 × {F_A, F_M} × {4h, 24h} = **4 セル**（事前固定・増やさない）。
  複製（記述・判定不使用）: US100 の同 4 セル。競合（記述）: 金自身の ret_H の整合（モメンタム）2 セル、および
  株整合 × 金整合 の 2×2（株の情報が金自身のモメンタムを超えるか）。
窓: 在 2012-20（US データは 2012 から・2010-11 の本は除外）／外 2021-26H1／近年 2024-26H1（D2: 水準は近年窓で語る）。
統計: diff・Welch t・日クラスタ t（同日の本は株の動きを共有）。
  family-wise: **週単位の循環シフト置換**（特徴量の参照時刻を k 週ずらす・曜日/時刻構造と自己相関を保つ・1000 回）で
  外窓 4 セルの max|t| の帰無分布 → p_max（cycle5 の日単位シャッフルは自己相関のある特徴量では帰無が狭すぎるため改良）。
  MDE: 各セル 2·se(diff)。注入: aligned/large 群に δ=+0.05R を足した時の t（検出力の実演）。
合否（セル単位・cycle5 と同じ）: 在 t≥2 で予測方向 ∧ 外 同符号 t≥1.5 ∧ p_max<0.05。1 セルでも PASS → 「条件づけあり」。
  それ以外 = null（イントラデイ株の動きは条件づけない／MDE 以下）。
ベースライン: 各窓の無条件平均R（gross・ft 非対称は全セル同一なので差の比較に影響しない）。
事前の最重要反証: (1) 金自身のモメンタム漏れ（競合セルで同時に見る）。(2) 株 CFD の閉場帯（NY 17:00-18:00 ET 等）と
  金の本番時間帯の重なりで有効本数が偏る → 鮮度 2h の NaN 率を記録。(3) 4+4+2+4 セルの事後選択 → 主 4 セルのみ判定・置換で補正。
昇格候補ではない（レジーム記述・DATA_MAP §6 の【要取得】→【実験可】が主目的）。seed 20261106。
"""
import json, os, sys, time, math, glob
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c8_crossasset_intraday_result.md")
FEAT = os.path.join(DATA, "c8_crossasset_features.csv")
DUK = r"C:\Users\user\AssetEmpire\empire\research\dukas"
SRC = {
    # 注: download/ の "2012-01-01-2026-07-01" 結合ファイルは実際には US500 2014-12・US100 2017-05 で切れている（初回実行で判明）。
    #     四半期 chunks/ は 2012-01〜2026-06 が揃っている（US500 58/59 非空・US100 58/58）のでそちらを使う。
    "US500": sorted(glob.glob(os.path.join(DUK, "chunks", "usa500idxusd-m1-bid-*.csv"))),
    "US100": sorted(glob.glob(os.path.join(DUK, "chunks", "usatechidxusd-m1-bid-*.csv"))),
    "XAU": sorted(glob.glob(os.path.join(DUK, "chunks", "xauusd-m1-bid-*.csv"))),
}
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)

def load_m5_close(sym):
    cache = os.path.join(MAC, f"{sym}_m5_close.npz")
    if os.path.exists(cache):
        z = np.load(cache); return pd.Series(z["close"], index=z["ts"])
    t = time.time(); frames = []
    for p in SRC[sym]:
        if os.path.getsize(p) == 0: continue
        frames.append(pd.read_csv(p, usecols=["timestamp", "close"]))
    m1 = pd.concat(frames, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    ts5 = (m1["timestamp"].to_numpy() // 1000) // 300 * 300
    s = pd.Series(m1["close"].to_numpy(), index=ts5)
    s = s.groupby(level=0).last()  # M5 close = last M1 close in the bar
    np.savez(cache, ts=s.index.to_numpy().astype(np.int64), close=s.to_numpy().astype(np.float64))
    say(f"- {sym}: M1 {len(m1)} 行 → M5 {len(s)} 本 {pd.to_datetime(s.index[0],unit='s')}..{pd.to_datetime(s.index[-1],unit='s')} UTC（{time.time()-t:.1f} s・キャッシュ保存）")
    return s

def asof(series_ts, series_v, q, tol):
    """backward asof: value at last ts ≤ q within tol seconds, else nan"""
    i = np.searchsorted(series_ts, q, side="right") - 1
    ok = i >= 0
    v = np.full(len(q), np.nan); age = np.full(len(q), np.nan)
    ii = i[ok]; v_ok = series_v[ii]; age_ok = q[ok] - series_ts[ii]
    v_ok = np.where(age_ok <= tol, v_ok, np.nan)
    v[ok] = v_ok; age[ok] = age_ok
    return v, age

say(f"# [cycle8] イントラデイ株（US500/US100）の直前の動き × 金 再加速 R — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c8_crossasset_intraday.py)")
say("## 0. データ読込")
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
tr = pd.DataFrame(d["trades"]).sort_values("entry_time").reset_index(drop=True)
tr["te"] = tr["entry_time"].to_numpy() - 300
tr["day"] = (tr["entry_time"] + 9 * 3600) // 86400  # JST 日
say(f"- trades n={len(tr)}（2010-01..2026-06）、gross R mean {tr.R.mean():+.4f}")
S = {}
for sym in ("US500", "US100", "XAU"):
    S[sym] = load_m5_close(sym)
    if time.time() - T0 > 200: say("!! 読込が 200 s を超過 → 中止"); sys.exit(1)
say(f"読込 合計 {time.time()-T0:.1f} s")

HORIZ = {"4h": 4 * 3600, "24h": 24 * 3600}
FRESH = 2 * 3600; TOLP = 3 * 86400

def features(sym, te):
    s = S[sym]; ts = s.index.to_numpy().astype(np.int64); v = np.log(s.to_numpy())
    out = {}
    c_now, age = asof(ts, v, te, FRESH)
    for hn, H in HORIZ.items():
        c_prev, _ = asof(ts, v, te - H, TOLP)
        out[f"ret{hn}_{sym}"] = c_now - c_prev
    out[f"age_{sym}"] = age
    return out

def thresholds(sym):
    """時間足グリッドで |ret_H| の直近 250 日（≈ 250*24 時間点）の 80% 点（当時点まで・look-ahead なし）"""
    s = S[sym]; ts = s.index.to_numpy().astype(np.int64); v = np.log(s.to_numpy())
    grid = np.arange(ts[0] + 86400 * 2, ts[-1], 3600)
    c_now, _ = asof(ts, v, grid, FRESH)
    thr = {}
    for hn, H in HORIZ.items():
        c_prev, _ = asof(ts, v, grid - H, TOLP)
        r = pd.Series(np.abs(c_now - c_prev), index=grid)
        q = r.rolling(250 * 24, min_periods=120 * 24).quantile(0.8)
        thr[hn] = (grid, q.to_numpy())
    return thr

te = tr["te"].to_numpy()
F = {}
for sym in ("US500", "US100", "XAU"):
    F.update(features(sym, te))
    th = thresholds(sym)
    for hn in HORIZ:
        g, q = th[hn]
        thr_v, _ = asof(g, q, te, 3 * 3600)
        F[f"thr{hn}_{sym}"] = thr_v
X = pd.concat([tr, pd.DataFrame(F)], axis=1)
X.to_csv(FEAT, index=False)
say(f"- 特徴量 {time.time()-T0:.1f} s → {os.path.basename(FEAT)}（再利用キャッシュ）")
for sym in ("US500", "US100", "XAU"):
    m12 = X.year >= 2012
    ok = X.loc[m12, f"ret4h_{sym}"].notna()
    say(f"- {sym}: 2012 以降 {m12.sum()} 本のうち ret4h あり {ok.mean()*100:.1f}%（鮮度 ≤2h 条件）、age 中央値 {X.loc[m12, f'age_{sym}'].median():.0f} s")

W = {"在2012-20": (X.year >= 2012) & (X.year <= 2020), "外2021-26": X.year >= 2021, "近年2024-26": X.year >= 2024}
say("\n## 1. ベースライン（無条件平均R・gross）")
for wn, m in W.items():
    say(f"- {wn}: n={m.sum()} mean {X.loc[m,'R'].mean():+.4f} sd {X.loc[m,'R'].std():.3f}")

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, np.nan
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, (diff / se if se > 0 else np.nan), se

def cluster_t(R, g, day):
    a = g; b = ~g
    if a.sum() < 2 or b.sum() < 2: return np.nan
    ma, mb = R[a].mean(), R[b].mean(); na, nb = a.sum(), b.sum()
    inf = pd.Series(np.where(a, (R - ma) / na, 0.0) - np.where(b, (R - mb) / nb, 0.0)).groupby(day).sum()
    se = math.sqrt((inf ** 2).sum()); return (ma - mb) / se if se > 0 else np.nan

def cell_mask(df, sym, form, hn):
    r = df[f"ret{hn}_{sym}"].to_numpy(); ok = ~np.isnan(r)
    if form == "F_A":
        side = df["side"].to_numpy()
        g = ((side == "BUY") & (r < 0)) | ((side == "SELL") & (r > 0)); ok = ok & (r != 0)
    else:
        thr = df[f"thr{hn}_{sym}"].to_numpy(); ok = ok & ~np.isnan(thr); g = np.abs(r) >= thr
    return ok, g

def run_cells(sym, label, judge):
    say(f"\n## {label}（diff = 条件群 − 対照群・予測 >0）")
    res = {}
    for form in ("F_A", "F_M"):
        for hn in HORIZ:
            row = {}
            for wn, wm in W.items():
                ok, g = cell_mask(X, sym, form, hn); m = wm.to_numpy() & ok
                R = X.loc[m, "R"].to_numpy(); gg = g[m]; day = X.loc[m, "day"].to_numpy()
                diff, t, se = welch(R[gg], R[~gg]); tc = cluster_t(R, gg, day)
                tin = welch(R[gg] + 0.05, R[~gg])[1]
                row[wn] = dict(diff=diff, t=t, tc=tc, n1=int(gg.sum()), n0=int((~gg).sum()), mde=2 * se, tin=tin)
            res[(form, hn)] = row
            say(f"- **{form} {hn}**: " + " / ".join(
                f"{wn} n={v['n1']}:{v['n0']} diff {v['diff']:+.4f} t {v['t']:+.2f} (cl {v['tc']:+.2f}) MDE {v['mde']:.3f}R 注入+0.05→t {v['tin']:+.2f}"
                for wn, v in row.items()))
    return res

res = run_cells("US500", "2. 主セル US500（4 セル・判定に使用）", True)
res100 = run_cells("US100", "3. 複製 US100（記述・判定不使用）", False)
resx = {}
say("\n## 4. 競合: 金自身の直前リターンの整合（モメンタム・記述）と 株整合 × 金整合 の 2×2（外 2021-26）")
for hn in HORIZ:
    row = {}
    for wn, wm in W.items():
        ok, g = cell_mask(X, "XAU", "F_A", hn); m = wm.to_numpy() & ok
        R = X.loc[m, "R"].to_numpy(); gg = g[m]
        diff, t, se = welch(R[gg], R[~gg]); row[wn] = (diff, t, int(gg.sum()), int((~gg).sum()))
    resx[hn] = row
    say(f"- **金 F_A {hn}**: " + " / ".join(f"{wn} n={v[2]}:{v[3]} diff {v[0]:+.4f} t {v[1]:+.2f}" for wn, v in row.items()))
for hn in HORIZ:
    okE, gE = cell_mask(X, "US500", "F_A", hn); okX, gX = cell_mask(X, "XAU", "F_A", hn)
    for wn in ("在2012-20", "外2021-26"):
        m = W[wn].to_numpy() & okE & okX; R = X.loc[m, "R"].to_numpy(); e = gE[m]; x = gX[m]
        cells = {(ee, xx): R[(e == ee) & (x == xx)] for ee in (True, False) for xx in (True, False)}
        s = " ".join(f"[株{'整' if ee else '逆'}×金{'整' if xx else '逆'}] {v.mean():+.3f} (n{len(v)})" for (ee, xx), v in cells.items())
        d1, t1, _ = welch(cells[(True, True)], cells[(False, True)])
        d2, t2, _ = welch(cells[(True, False)], cells[(False, False)])
        say(f"- {hn} {wn}: {s} ｜ 金整合内の株効果 {d1:+.4f} (t{t1:+.2f})・金逆内の株効果 {d2:+.4f} (t{t2:+.2f})")
    r_e = X.loc[W['外2021-26'] & okE & okX, f"ret{hn}_US500"]; r_x = X.loc[W['外2021-26'] & okE & okX, f"ret{hn}_XAU"]
    say(f"- {hn} 外: 株 ret と金 ret の相関（同時刻・建玉直前） ρ {np.corrcoef(r_e, r_x)[0,1]:+.3f}（在: ρ {np.corrcoef(X.loc[W['在2012-20'] & okE & okX, f'ret{hn}_US500'], X.loc[W['在2012-20'] & okE & okX, f'ret{hn}_XAU'])[0,1]:+.3f}）")

# ---------- family-wise permutation: circular weekly shift of the lookup time ----------
say("\n## 5. family-wise 置換（US500 の参照時刻を k 週 循環シフト・外窓 4 セル max|t|・1000 回）")
NPERM = 1000
oos = X[W["外2021-26"]].copy(); te_o = oos["te"].to_numpy(); side_o = oos["side"].to_numpy(); R_o = oos["R"].to_numpy()
s = S["US500"]; ts = s.index.to_numpy().astype(np.int64); v = np.log(s.to_numpy())
th = thresholds("US500")
lo, hi = ts[0] + 30 * 86400, ts[-1] - 2 * 86400; span_w = (hi - lo) // 604800
cells = [(f, h) for f in ("F_A", "F_M") for h in HORIZ]
obs_t = np.array([res[c]["外2021-26"]["t"] for c in cells]); obs_max = np.nanmax(np.abs(obs_t))
def tstat(R, ok, g):
    a = R[ok & g]; b = R[ok & ~g]
    if len(a) < 2 or len(b) < 2: return np.nan
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return (a.mean() - b.mean()) / se if se > 0 else np.nan
null = np.full((NPERM, len(cells)), np.nan); tp = time.time()
for p in range(NPERM):
    k = int(rng.integers(8, span_w - 8))
    q = lo + ((te_o - lo + k * 604800) % (span_w * 604800))
    c_now, _ = asof(ts, v, q, FRESH)
    for j, (form, hn) in enumerate(cells):
        H = HORIZ[hn]; c_prev, _ = asof(ts, v, q - H, TOLP); r = c_now - c_prev; ok = ~np.isnan(r)
        if form == "F_A":
            g = ((side_o == "BUY") & (r < 0)) | ((side_o == "SELL") & (r > 0)); ok = ok & (r != 0)
        else:
            g_, qv = th[hn]; thr_v, _ = asof(g_, qv, q, 3 * 3600); ok = ok & ~np.isnan(thr_v); g = np.abs(r) >= thr_v
        null[p, j] = tstat(R_o, ok, g)
    if time.time() - tp > 150: say(f"!! 置換 {p+1} 回で時間上限 → ここまでで評価"); null = null[:p + 1]; break
nmax = np.nanmax(np.abs(null), axis=1)
p_max = (nmax >= obs_max).mean()
say(f"- 観測 外 max|t| {obs_max:.2f} → 帰無 中央値 {np.median(nmax):.2f} / 95%点 {np.quantile(nmax,0.95):.2f} / **p_max {p_max:.3f}**（{len(nmax)} 回・{time.time()-tp:.0f} s）")
for j, c in enumerate(cells):
    pj = (np.abs(null[:, j]) >= abs(obs_t[j])).mean()
    say(f"  - {c[0]} {c[1]}: 外 t {obs_t[j]:+.2f} 単セル置換 p {pj:.3f}（帰無 sd {np.nanstd(null[:, j]):.2f}）")

# ---------- verdict ----------
say("\n## 6. 判定（事前規則: 在 t≥2 予測方向 ∧ 外 同符号 t≥1.5 ∧ p_max<0.05）")
npass = 0
for c in cells:
    a = res[c]["在2012-20"]; b = res[c]["外2021-26"]
    ok = (a["t"] >= 2.0) and (b["t"] >= 1.5) and (p_max < 0.05); npass += ok
    say(f"- {c[0]} {c[1]}: 在 t {a['t']:+.2f} / 外 t {b['t']:+.2f} / 近年 t {res[c]['近年2024-26']['t']:+.2f} / p_max {p_max:.3f} → {'PASS' if ok else 'FAIL'}")
say(f"\n**PASS {npass}/4 → {'条件づけあり' if npass else 'null（建玉直前の米株イントラデイの向き・大きさは金 再加速の R を条件づけない／MDE 以下）'}**")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
