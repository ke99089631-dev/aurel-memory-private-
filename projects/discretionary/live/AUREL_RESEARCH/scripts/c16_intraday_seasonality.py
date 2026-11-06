# -*- coding: utf-8 -*-
"""
[cycle16 研究レーン] 2026-11-06 — 【探索・市場構造（制度的な時刻効果）】金の **時刻帯（London 現地時刻）別の平均リターン**
（ロンドン AM/PM フィックス・アジア実需の時間帯）は 2010-20 で存在し 2021-26 で再現するか（H1）。
再現するなら、その「季節ドリフト」は再加速 R を側×時刻で条件づけるか（H2・レジーム記述＝入口フィルタではない・側対称）。

=== 事前固定（この docstring を書いてから数字を見る） ===
背景（文献・機構）: LBMA フィックス（AM 10:30 / PM 15:00 London）は生産者ヘッジ・中銀・精錬のベンチマーク執行が集中する時刻で、
  Caminschi & Heaney (2014, J. Futures Markets) は PM フィックス直前に価格が下がる傾向を報告。アジア時間帯は現物需要（宝飾・小売）の
  買いが入りやすく、ロンドン/NY 時間帯は先物・ETF の売りが出やすいとされる（「夜に上がり昼に下がる」intraday seasonality）。
  いずれも「参加者の制度的な時刻の集中」が源泉＝構造的な優位の候補（DIRECTIVE 2 の「カレンダー効果/マクロ発表前後」の時刻版）。
データ: data/macro/XAU_m5_close.npz（暦格子・前値埋め・⑪ flat 比率を印字）。足 i のリターン r_i = lc_i − lc_{i−1} を足 i の開始時刻
  ts_i の **London 現地時刻**（DST 追随）の時に帰属。土日（London 現地の曜日）は除外。平日の flat 足（維持時間帯の 0）は 0 として残す
  （0 ドリフトは事実）。日 d・時 h の和 S[d,h]（bp）を作り、統計は**日クラスタ**（日ごとの S の平均と SE）。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 16 年一括の水準は使わない）。
H1 主セル（London 現地時刻・予測方向）: A = アジア 01:00–08:00 の和 **>0**／B = AM フィックス帯 10:00–11:00 **<0**／C = PM フィックス帯
  14:00–16:00 **<0**。判定: 在 |t|≥2 予測方向 ∧ 外 同符号 |t|≥1.5 ∧ family-wise p<0.05（帰無＝各日の 24 時ラベルを日内でシャッフル
  1000 回・3 セル max|t|）。1 セルでも通れば「時刻効果あり」、無ければ null。記述: 24 時プロファイル（bp/時・在/外/近年）・
  夜(22–08)/昼(08–22) の分割・スプレッド 0.16 USD の bp 換算との比（取引可能性）。MDE = 2·se（bp/時）。
H2（H1 の結果に依らず実行・レジーム記述）: 在 2010-20 の時別平均 μ_h（bp/5 分）を季節プロファイルとし、本 j（te = entry_time−300）
  の建玉後 **4h（48 スロット）** の季節ドリフト D_j = s_j·Σ μ_{h(slot)}（s=+1 BUY/−1 SELL）を R 単位（×price/risk）に換算。
  主セル: 外 2021-26H1 で D_j の上位三分位（追い風）− 下位三分位（向かい風）の mean R **>0**。合否: 外 t≥2（Welch・日クラスタ t も
  併記）∧ 近年 同符号 ∧ 置換 p<0.05（帰無＝季節プロファイルを 5 分格子上で 1..287 スロット循環回転・全 287 通り）。
  複製: 1h（12 スロット）。記述: OLS 傾き β（R on D_j[R 単位]・ドリフトが完全に通れば ≈1）、在（プロファイル推定と同じ窓なので
  判定に使わない）、MDE 2·se・注入 +0.05R → t。事前の最重要反証: 時刻帯は本番窓 jh7-12（UTC 22–03）と重なるので D_j は
  「どの時間帯に建てたか」の代理（時間帯の組成差）になりうる → 側で符号が割れるかを印字（側対称なら時刻帯の組成ではない）。
look-ahead: μ_h は 2010-20 のみで推定し 2021-26 に適用。te 以降のスロットの時刻だけを使い値は使わない。closed 全本（TIME 含む）。
scan 無し・M5 原本読込なし・MT5 なし・外部通信なし。昇格候補ではない。seed 20261106。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c16_intraday_seasonality_result.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle16] 金の時刻帯（London 現地）別平均リターンと再加速 R の季節ドリフト — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c16_intraday_seasonality.py)")

# ---------- load M5 close ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc)
t_utc = pd.to_datetime(ts, unit="s", utc=True)
t_lon = t_utc.tz_convert("Europe/London")
wd = t_lon.weekday.to_numpy(); hour = t_lon.hour.to_numpy(); slot_lon = (hour * 12 + t_lon.minute.to_numpy() // 5)
day_lon = (t_lon.year.to_numpy() * 10000 + t_lon.month.to_numpy() * 100 + t_lon.day.to_numpy())
year = t_utc.year.to_numpy()
flat = (r == 0)
say(f"- npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）。flat 足比率 曜日別(London 月..日): " +
    " ".join(f"{d}:{flat[wd==d].mean()*100:.1f}%" for d in range(7)) + f"（⑪・土日は除外、平日 flat は 0 ドリフトとして残す）")
keep = wd <= 4
r_bp = r * 1e4

# ---------- S[d,h] 日×時の和（bp） ----------
df = pd.DataFrame({"day": day_lon[keep], "h": hour[keep], "r": r_bp[keep], "yr": year[keep]})
S = df.pivot_table(index="day", columns="h", values="r", aggfunc="sum", fill_value=0.0)
S = S.reindex(columns=range(24), fill_value=0.0)
yr_of_day = pd.Series(df.groupby("day")["yr"].first()).reindex(S.index).to_numpy()
M = S.to_numpy()  # ndays × 24, bp per hour
W = {"在2010-20": (yr_of_day >= 2010) & (yr_of_day <= 2020), "外2021-26H1": yr_of_day >= 2021, "近年2024-26H1": yr_of_day >= 2024}
say(f"- 日×時 行列 {M.shape}（平日 London 現地）、日数 在 {W['在2010-20'].sum()}／外 {W['外2021-26H1'].sum()}／近年 {W['近年2024-26H1'].sum()}")

def cell_stat(Mw, hours):
    x = Mw[:, hours].sum(axis=1); n = len(x); m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
    return m, se, m / se if se > 0 else np.nan, n
CELLS = {"A アジア01-08 (>0)": (list(range(1, 8)), +1), "B AMフィックス10-11 (<0)": ([10], -1), "C PMフィックス14-16 (<0)": ([14, 15], -1)}

say("\n## H1 主セル（London 現地時刻・bp/窓・日クラスタ t）")
H1 = {}
for cn, (hs, sgn) in CELLS.items():
    row = []
    for wn, wm in W.items():
        m, se, t, n = cell_stat(M[wm], hs); H1[(cn, wn)] = (m, se, t, n)
        row.append(f"{wn} **{m:+.2f} bp (t{t:+.2f}, n{n}, MDE {2*se:.2f})**")
    say(f"- {cn}: " + " ｜ ".join(row))
# family-wise: 日内で時ラベルをシャッフル（各日独立）
NP = 1000
def maxabs_t(Mw):
    return max(abs(cell_stat(Mw, hs)[2]) for hs, _ in CELLS.values())
obs_fw = {wn: maxabs_t(M[wm]) for wn, wm in W.items()}
null_fw = {wn: np.empty(NP) for wn in W}
tp = time.time()
for p in range(NP):
    Mp = rng.permuted(M, axis=1)
    for wn, wm in W.items(): null_fw[wn][p] = maxabs_t(Mp[wm])
PFW = {wn: (null_fw[wn] >= obs_fw[wn]).mean() for wn in W}
say(f"- family-wise（日内 24 時ラベルシャッフル {NP} 回・3 セル max|t|・{time.time()-tp:.0f} s）: " +
    " ｜ ".join(f"{wn} 観測 {obs_fw[wn]:.2f} → 帰無 中央値 {np.median(null_fw[wn]):.2f}・95%点 {np.quantile(null_fw[wn],0.95):.2f}・**p {PFW[wn]:.3f}**" for wn in W))
passed = []
for cn, (hs, sgn) in CELLS.items():
    mi, sei, ti, _ = H1[(cn, "在2010-20")]; mo, seo, to, _ = H1[(cn, "外2021-26H1")]
    ok = (sgn * ti >= 2.0) and (sgn * to >= 1.5) and (PFW["外2021-26H1"] < 0.05)
    say(f"  - 判定 {cn}: 在 t{ti:+.2f}（要 {sgn:+d}×≥2）・外 t{to:+.2f}（要 同符号 ≥1.5）・外 p_fw {PFW['外2021-26H1']:.3f} → {'PASS' if ok else 'FAIL'}")
    if ok: passed.append(cn)
say(f"- **H1 判定: {'時刻効果あり ' + str(passed) if passed else 'null（PASS 0）'}**")

say("\n## 記述: 24 時プロファイル（bp/時・日クラスタ t・London 現地）")
hdr = "| h | " + " | ".join(W.keys()) + " |"; say(hdr); say("|---|" + "---|" * len(W))
for h in range(24):
    cells = []
    for wn, wm in W.items():
        m, se, t, n = cell_stat(M[wm], [h]); cells.append(f"{m:+.2f} (t{t:+.1f})")
    say(f"| {h:02d} | " + " | ".join(cells) + " |")
say("\n## 記述: 夜(22–08)/昼(08–22)・スプレッド比")
for wn, wm in W.items():
    mn, sen, tn, n = cell_stat(M[wm], list(range(22, 24)) + list(range(0, 8))); md, sed, td, _ = cell_stat(M[wm], list(range(8, 22)))
    # spread in bp at window median price
    pm = np.median(cl[keep & np.isin(year, np.unique(yr_of_day[wm]))]); sp_bp = 0.16 / pm * 1e4
    say(f"- {wn}: 夜 {mn:+.2f} bp/日 (t{tn:+.2f}) ／ 昼 {md:+.2f} bp/日 (t{td:+.2f}) ／ 夜−昼 {mn-md:+.2f}；中央値価格 {pm:.0f} USD → スプレッド 0.16 USD = {sp_bp:.2f} bp（往復 {2*sp_bp:.2f}）")

# ---------- H2: 季節ドリフトは再加速 R を条件づけるか ----------
say("\n## H2 季節ドリフト（在 2010-20 の時別 μ_h を 2021-26 の本に適用・R 単位・側で符号づけ）")
# μ_h: bp per 5-min slot, in-sample weekdays
ins = keep & (year <= 2020)
mu_h = np.array([r_bp[ins & (hour == h)].mean() for h in range(24)])  # bp per slot
say("- μ_h（bp/5分・在）: " + " ".join(f"{h}:{mu_h[h]:+.3f}" for h in range(24)))
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
TE = X["te"].to_numpy().astype(np.int64); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy()
RISK = X["risk"].to_numpy(); YEAR = X["year"].to_numpy(); EXIT = X["exit"].to_numpy(); JH = X["jh"].to_numpy()
# price at te
i_te = np.searchsorted(ts, TE, side="right") - 1; P0 = cl[np.clip(i_te, 0, len(cl) - 1)]
day_te = (TE // 86400)
# slot hours after te (London) for horizons
def slot_hours(H):
    tt = (TE[:, None] + 300 * np.arange(1, H + 1)[None, :]).ravel()
    th = pd.to_datetime(tt, unit="s", utc=True).tz_convert("Europe/London")
    return th.hour.to_numpy().reshape(len(TE), H), (th.hour.to_numpy() * 12 + th.minute.to_numpy() // 5).reshape(len(TE), H)
WT = {"在2010-20(参考)": YEAR <= 2020, "外2021-26H1": YEAR >= 2021, "近年2024-26H1": YEAR >= 2024}
def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]; d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, se, d / se
def cl_t(y, g, cl_):
    # cluster-robust t for mean difference via regression on indicator, clusters = days
    Z = np.column_stack([np.ones(len(y)), g.astype(float)]); ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((2, 2)); G = 0
    for c in np.unique(cl_):
        idx = cl_ == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G += 1
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta[1] / math.sqrt(V[1, 1])
H2 = {}
for H, lab in ((48, "4h（主）"), (12, "1h（複製）")):
    hh, ss = slot_hours(H)
    D_bp = SGN * mu_h[hh].sum(axis=1)                       # bp over horizon, signed by side
    D_R = D_bp * 1e-4 * P0 / RISK                          # R units
    say(f"\n### 水平線 {lab}: D_j[R] 全本 中央値 {np.median(D_R):+.4f}・p10 {np.quantile(D_R,0.1):+.4f}・p90 {np.quantile(D_R,0.9):+.4f}；BUY 平均 {D_R[SGN>0].mean():+.4f}／SELL {D_R[SGN<0].mean():+.4f}")
    for wn, wm in WT.items():
        q = np.quantile(D_R[wm], [1 / 3, 2 / 3]); top = wm & (D_R > q[1]); bot = wm & (D_R <= q[0])
        d, se, t = welch(R[top], R[bot]); sub = top | bot; tc = cl_t(R[sub], top[sub], day_te[sub])
        # OLS slope
        x = D_R[wm]; y = R[wm]; b1 = np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1); se_b = math.sqrt(((y - y.mean() - b1 * (x - x.mean()))**2).sum() / (len(x) - 2) / ((x - x.mean())**2).sum())
        inj = (d + 0.05) / se
        # side split
        db, _, tb = welch(R[top & (SGN > 0)], R[bot & (SGN > 0)]); ds, _, tsl = welch(R[top & (SGN < 0)], R[bot & (SGN < 0)])
        H2[(H, wn)] = (d, se, t, tc, b1, se_b)
        say(f"- {wn}: 追い風−向かい風 **{d:+.4f}R (t{t:+.2f}, 日cl {tc:+.2f}, n{top.sum()}:{bot.sum()}, MDE {2*se:.3f}, 注入+0.05→t{inj:+.2f})**；"
            f" OLS β {b1:+.3f} (t{b1/se_b:+.2f})；側別 BUY {db:+.4f} (t{tb:+.2f})／SELL {ds:+.4f} (t{tsl:+.2f})；"
            f" 閾値 {q[0]:+.4f}/{q[1]:+.4f}R；追い風群の jh7-12 比率 {np.isin(JH[top],range(7,13)).mean():.2f} vs 向かい風 {np.isin(JH[bot],range(7,13)).mean():.2f}")
    if H == 48:
        # permutation: rotate slot-level profile by k slots (all 287)
        mu_slot = mu_h[np.arange(288) // 12]
        wm = WT["外2021-26H1"]; nt = np.empty(287)
        for k in range(1, 288):
            mr = np.roll(mu_slot, k); Dp = SGN * mr[ss].sum(axis=1) * 1e-4 * P0 / RISK
            q = np.quantile(Dp[wm], [1 / 3, 2 / 3]); top = wm & (Dp > q[1]); bot = wm & (Dp <= q[0]); nt[k - 1] = welch(R[top], R[bot])[2]
        t_obs = H2[(48, "外2021-26H1")][2]; p_perm = (np.abs(nt) >= abs(t_obs)).mean()
        say(f"- 置換（季節プロファイルの 5 分格子循環回転 287 通り・外 4h 主セル）: 帰無 sd {nt.std():.2f}・95%点|t| {np.quantile(np.abs(nt),0.95):.2f}・**両側 p {p_perm:.3f}**")
        t_rec = H2[(48, "近年2024-26H1")][2]
        ok = (t_obs >= 2.0) and (np.sign(t_rec) == np.sign(t_obs)) and (p_perm < 0.05)
        say(f"- **H2 判定（外 4h）: t{t_obs:+.2f}・近年 t{t_rec:+.2f}・置換 p {p_perm:.3f} → {'PASS（季節ドリフトが R を条件づける）' if ok else 'null'}**")

# 記述: 本の建玉時刻（London 現地）分布と、その時刻の季節ドリフト（側非依存）
say("\n## 記述: 再加速の建玉時刻（London 現地・時）分布と在 μ_h（側非依存）")
h_te = pd.to_datetime(TE, unit="s", utc=True).tz_convert("Europe/London").hour.to_numpy()
cnt = np.bincount(h_te, minlength=24)
say("- 建玉本数/時: " + " ".join(f"{h}:{cnt[h]}" for h in range(24)))
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
