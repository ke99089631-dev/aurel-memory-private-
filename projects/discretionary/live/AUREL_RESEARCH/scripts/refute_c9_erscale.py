# -*- coding: utf-8 -*-
"""
AUREL 反証レーン 2026-11-06 05:20 — 対象: cycle9 (03:50) の構造的読み＋弱信号
  cycle9 の判定 null（ER20 P1/P2 FAIL・p_max 0.60）は再現して争わない。壊しに行くのは
  (i) 構造的読み「継続効果（A=直前24hと同向き・2021-26）は ER では識別できない『時代』の性質で、
      次の時代の符号を ER で先読みできない」
  (ii) 弱信号「近年 2024-26 の ER20 top で D_top +0.206 (t3.07)・I=D_top−D_bot +0.149 (t1.55)・ER60/vol20 では消える」
  cycle9 自身が挙げた最重大反証＝「ER の尺度（20〜60 日）と継続効果の尺度（8〜120h）が 1 桁ずれている」。
  研究レーンは ER_5d を 1 回限りで試す復活条件を残した。反証レーンはそれを**掃引＋family-wise**で先に潰す/立てる。

読取りのみ・発注なし・scan なし・M1/M5 原本読込なし・MT5 なし・外部通信なし。入力は既存キャッシュのみ
  data/c8_crossasset_features.csv（19404 本）・data/macro/XAU_m5_close.npz・data/macro/XAU_daily_er.csv（c9 の再現確認用）。
書き込みは data/refute_c9_erscale.md のみ。

=== 事前固定（この docstring を書いてから数字を見る・以後動かさない） ===
記帳: cycle9 と同一（R gross・closed 全本 TIME 含む・A = sign(side)·ret24h_XAU > 0・参照時刻 q = te − 24h で ret24h 窓と非重複）。
ER の定義: ER_N(t) = |lc_t − lc_{t−N}| / Σ_{i=t−N+1..t} |lc_i − lc_{i−1}|。
  短尺度 N ∈ {1d, 2d, 3d, 5d, 10d} は**時間足 close**（各 UTC 時の最後の M5 close・既知時刻 = 足開始+300 s）から N·24 本で計算。
  長尺度 N ∈ {20d, 60d, 120d, 250d} は**日足 close**（擬似日境界 22:00 UTC・cycle9 と同一）から計算。20d/60d は c9 と一致するはず。
  閾値: 各 ER_N の「直近 500 日・当日を含まない日次サンプル」のパーセンタイル（最低 250 日）→ top ≥2/3・bottom ≤1/3（c9 と同じ形）。
  時間足 ER のパーセンタイルも、同じ ER_N の**日次サンプル**（22:00 境界の値）500 日分を参照分布にする（分布の時間変化を揃える）。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 水準は使わない）。
統計: Welch t・日クラスタ t・MDE 2·se。

Q0 再現: c9 の ER20/ER60 の P1・P2（D_top/D_mid/D_bot/I）を日足キャッシュから再計算し一致を確認（1e-6）。
Q1 尺度掃引（主検定）: 9 尺度 × {P1 top−bot, P2 I=D_top−D_bot} × 3 窓。
  cycle9 自身の「構造仮説の読み」の規則を各尺度に適用: 在 D_top>0 (t≥1.5) ∧ 在 D_bottom≤0 なら「レジームの性質」側。
  family-wise: q を k 週 循環シフト（1000 回・全尺度に同じ k）で
    S1 = 外 9 尺度の max|t_I|、S2 = 近年 9 尺度の max|t_I|、S3 = 在 9 尺度の max t_Dtop（片側・レジーム側のみ）、
    S4 = 外 9 尺度の max|t_P1|。それぞれ p_fw。
Q2 弱信号（近年 ER20 D_top/I）の頑健性: 定義の揺らぎ 8 変種で t_I（近年）と t_Dtop（近年）を再計算:
    (a) 擬似日境界 22:00 → 00:00 / 12:00 / 17:00 UTC、(b) 閾値 rolling pct → 絶対値（ER20 ≥ 中央値+0.1 / ≤ 中央値−0.1 の固定）、
    (c) 参照ラグ 24h → 48h / 0h、(d) 近年から 1 年ずつ除く LOYO（2024/2025/2026 除外）。
    「t_I ≥ 1.5 を保つ変種の数 / 全変種数」を出す。半数未満なら弱信号は定義の揺れで消える。
Q3 時代 vs レジームの分解: 半年ごと（2010H1..2026H1・33 半期）に D（継続効果）と top 比率（各尺度）を出し、
    半期横断の Spearman ρ(D_半期, top比率_半期) を 9 尺度で出す。レジームが D を駆動していれば ρ>0 がいくつかの尺度で立つ。
    併せて外 2021-26 内の半期固定効果つき I（半期ごとの I の n 加重平均）を 9 尺度で出す。
Q4 look-ahead / survivorship: 全尺度で max(known) ≤ q を assert、本の付与率を印字、closed 全本（TIME 含む）。
    コスト: フィルタ型でなくレジーム記述なので両群同額＝コスト倍は diff を変えない（数字は出さない・理由を記す）。
判定（事前固定・「cycle9 の読み」に対して）:
  broken（cycle9 の null/読みが壊れる＝ER レジーム識別子が存在する）
      = ある尺度 N で 在 D_top t≥1.5 ∧ 在 D_bot≤0 ∧ 外 I t≥1.5 ∧ 近年 I>0 ∧ S1 p_fw<0.05。
  survived（cycle9 の読みが生き残る）
      = 全尺度で（在 D_top t<1.5 ∨ 在 D_bot>0）∧ S1 p_fw>0.05 ∧ S2 p_fw>0.05 ∧ Q2 で t_I≥1.5 を保つ変種が半数未満 ∧ Q3 で ρ≥0.3 の尺度が 0。
  それ以外 = inconclusive。
seed 20261106。
"""
import os, math, time
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c9_erscale.md")
NPERM = 1000; rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se
def cl_se(R, day, groups):
    inf = np.zeros(len(R))
    for m, s in groups:
        if m.sum() < 2: return np.nan
        inf += s * np.where(m, (R - R[m].mean()) / m.sum(), 0.0)
    g = pd.Series(inf).groupby(day).sum(); return math.sqrt((g ** 2).sum())
def asof(ts, v, q, tol):
    i = np.searchsorted(ts, q, side="right") - 1; ok = i >= 0
    out = np.full(len(q), np.nan); ii = i[ok]; age = q[ok] - ts[ii]
    out[ok] = np.where(age <= tol, v[ii], np.nan); return out

say(f"# [REFUTE c9 erscale] ER 尺度掃引で『継続は時代でありレジームでない』を叩く — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c9_erscale.py)")
say("## 0. データ")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["sgn"] = np.where(X["side"] == "BUY", 1.0, -1.0)
X["okA"] = X["ret24h_XAU"].notna() & (X["ret24h_XAU"] != 0)
X["A"] = (X["sgn"] * X["ret24h_XAU"]) > 0
X["half"] = X["year"].astype(str) + np.where(pd.to_datetime(X["entry_time"], unit="s").dt.month <= 6, "H1", "H2")
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); lc = np.log(z["close"].astype(np.float64))
say(f"- trades n={len(X)}（closed 全本・TIME 含む）、okA {X.okA.mean()*100:.2f}%、XAU M5 {len(ts)} 本 {pd.to_datetime(ts[0],unit='s')}..{pd.to_datetime(ts[-1],unit='s')} UTC（min/max 印字）")
nb = X[X.okA].groupby(["side", "A"]).size()
say("- A 内訳: " + ", ".join(f"{s}∧{'同向き' if a else '逆向き'} n={v}" for (s, a), v in nb.items()))

# ---- grids ----
def last_close_grid(ts, lc, step, offset, strip_flat=False):
    gid = (ts - offset) // step
    df = pd.DataFrame({"g": gid, "ts": ts, "lc": lc}).groupby("g").agg(ts_last=("ts", "last"), lc=("lc", "last")).reset_index()
    df["known"] = df["ts_last"] + 300
    if strip_flat:
        # 事後の データ修正（判定規則は不変）: XAU_m5_close.npz は週末も前値で埋めた完全格子（土 99.9%・日 93% が flat）。
        # 時間足 ER の分母 Σ|Δ| が週末で 0 になり（NaN）、週明けは分母が薄く ER が膨らむ → flat な時間足を落として「取引時間」だけで数える。
        keep = df["lc"].diff().fillna(1.0) != 0.0; df = df[keep].reset_index(drop=True)
    return df
def er_series(lcv, n):
    s = pd.Series(lcv); num = (s - s.shift(n)).abs(); den = s.diff().abs().rolling(n).sum()
    return (num / den.replace(0, np.nan)).to_numpy()

DAY = last_close_grid(ts, lc, 86400, 22 * 3600)        # 擬似日 22:00 UTC（c9 と同一）
HR = last_close_grid(ts, lc, 3600, 0, strip_flat=True)  # 時間足（flat=週末/休場の時間足を除いた取引時間のみ・v1 修正）
say(f"- 日足 {len(DAY)} 日（c9 と同一・週末行を含む＝ER_20d は約 14 取引日）・時間足 {len(HR)} 本（flat 時間足を除外済み・{time.time()-t0:.1f} s）")

SCALES = [("1d", "H", 24), ("2d", "H", 48), ("3d", "H", 72), ("5d", "H", 120), ("10d", "H", 240),
          ("20d", "D", 20), ("60d", "D", 60), ("120d", "D", 120), ("250d", "D", 250)]

def daily_pct_ref(day_known, day_vals, win=500, minp=250):
    """各日 i について、直近 win 日（当日除く）の非 NaN サンプルをソートして返す（参照分布）"""
    refs = []
    for i in range(len(day_vals)):
        lo = max(0, i - win); w = day_vals[lo:i]; w = w[~np.isnan(w)]
        refs.append(np.sort(w) if len(w) >= minp else None)
    return refs
def pct_against_daily(q_known_idx, vals, refs):
    """vals の各値を、その時点で最後に確定した日 i の参照分布 refs[i] 内の pct に変換"""
    out = np.full(len(vals), np.nan)
    for j in range(len(vals)):
        i = q_known_idx[j]; r = refs[i] if i >= 0 else None
        if r is None or np.isnan(vals[j]): continue
        out[j] = np.searchsorted(r, vals[j], side="left") / len(r)
    return out

def build_scale(name, kind, n, DAYg=DAY, HRg=HR):
    """returns dict(known, p, er) : 既知時刻でソートされた pct 系列（asof 用）"""
    if kind == "D":
        er = er_series(DAYg["lc"].to_numpy(), n); known = DAYg["known"].to_numpy()
        refs = daily_pct_ref(known, er)
        p = np.full(len(er), np.nan)
        for i in range(len(er)):
            r = refs[i]
            if r is not None and not np.isnan(er[i]): p[i] = np.searchsorted(r, er[i], side="left") / len(r)
        return dict(known=known, p=p, er=er)
    else:
        er = er_series(HRg["lc"].to_numpy(), n); known = HRg["known"].to_numpy()
        # 日次サンプル（22:00 境界の既知時刻以前の最後の時間足値）を参照分布に
        dk = DAYg["known"].to_numpy(); idx = np.searchsorted(known, dk, side="right") - 1
        dvals = np.where(idx >= 0, er[np.clip(idx, 0, None)], np.nan)
        refs = daily_pct_ref(dk, dvals)
        di = np.searchsorted(dk, known, side="right") - 1   # 各時間足で最後に確定した日（当日除く）
        p = pct_against_daily(di, er, refs)
        return dict(known=known, p=p, er=er)

say("\n## 1. 尺度の構築（9 尺度・pct は 500 日次サンプル・当日除く）")
SC = {}
for name, kind, n in SCALES:
    SC[name] = build_scale(name, kind, n)
    v = SC[name]["er"]; say(f"- ER_{name} ({'時間足' if kind=='H' else '日足'}×{n}): 中央値 {np.nanmedian(v):.3f}、pct あり {np.mean(~np.isnan(SC[name]['p']))*100:.1f}%")
say(f"- 構築 {time.time()-t0:.1f} s")

LAG = 86400
def attach(df, sc, q):
    return asof(sc["known"], sc["p"], q, 5 * 86400)

W = {"在2010-20": (X.year <= 2020).to_numpy(), "外2021-26": (X.year >= 2021).to_numpy(), "近年2024-26": (X.year >= 2024).to_numpy()}
R_all = X["R"].to_numpy(); A_all = X["A"].to_numpy(); okA_all = X["okA"].to_numpy(); day_all = X["day"].to_numpy()

def p1p2(p, m, R=R_all, A=A_all, okA=okA_all, day=day_all, want_cl=True):
    ok = ~np.isnan(p) & m; top = ok & (p >= 2 / 3); bot = ok & (p <= 1 / 3); mid = ok & ~top & ~bot
    d1, t1, se1 = welch(R[top], R[bot])
    def cont(mm):
        a = mm & okA & A; b = mm & okA & ~A; d, t, se = welch(R[a], R[b]); return d, t, se, a, b
    dt, tt, st, At, nAt = cont(top); db, tb, sb, Ab, nAb = cont(bot); dm, tm, sm, _, _ = cont(mid)
    I = dt - db; seI = math.sqrt(st ** 2 + sb ** 2) if not (np.isnan(st) or np.isnan(sb)) else np.nan
    tI = I / seI if seI and seI > 0 else np.nan
    tcI = np.nan
    if want_cl and not np.isnan(tI):
        sec = cl_se(R, day, [(At, 1), (nAt, -1), (Ab, -1), (nAb, 1)]); tcI = I / sec if sec and sec > 0 else np.nan
    return dict(d1=d1, t1=t1, se1=se1, n_top=int(top.sum()), n_bot=int(bot.sum()), Dt=dt, tt=tt, Db=db, tb=tb, Dm=dm, tm=tm, I=I, tI=tI, tcI=tcI, seI=seI,
                nA=(int(At.sum()), int(nAt.sum()), int(Ab.sum()), int(nAb.sum())))

# ---- Q0 reproduce c9 ----
say("\n## Q0 再現（c9 ER20/ER60・日足キャッシュとの一致）")
C9 = pd.read_csv(os.path.join(MAC, "XAU_daily_er.csv"))
for nm, col in (("20d", "p_er20"), ("60d", "p_er60")):
    mine = SC[nm]["p"]; theirs = C9[col].to_numpy()
    both = ~np.isnan(mine) & ~np.isnan(theirs)
    say(f"- ER_{nm} pct: c9 キャッシュとの最大差 {np.nanmax(np.abs(mine[both]-theirs[both])):.2e}（{both.sum()} 日）")
q = X["te"].to_numpy() - LAG
RES = {}
for name, _, _ in SCALES:
    p = attach(X, SC[name], q); RES[name] = {"p": p}
    for wn, m in W.items(): RES[name][wn] = p1p2(p, m)
r = RES["20d"]
say(f"- ER_20d 在 P2: top {r['在2010-20']['Dt']:+.4f} (t{r['在2010-20']['tt']:+.2f}) / bot {r['在2010-20']['Db']:+.4f} → I {r['在2010-20']['I']:+.4f}（c9: −0.0257 / −0.0252 / −0.0005）")
say(f"- ER_20d 外 P2: top {r['外2021-26']['Dt']:+.4f} (t{r['外2021-26']['tt']:+.2f}) / bot {r['外2021-26']['Db']:+.4f} → I {r['外2021-26']['I']:+.4f} t {r['外2021-26']['tI']:+.2f}（c9: +0.1020 / +0.0408 / +0.0612 t0.94）")
say(f"- ER_20d 近年 P2: top {r['近年2024-26']['Dt']:+.4f} (t{r['近年2024-26']['tt']:+.2f}) / bot {r['近年2024-26']['Db']:+.4f} → I {r['近年2024-26']['I']:+.4f} t {r['近年2024-26']['tI']:+.2f}（c9: +0.2064 t3.07 / +0.0576 / +0.1488 t1.55）")
say(f"- ER_20d 外 P1: {r['外2021-26']['d1']:+.4f} t {r['外2021-26']['t1']:+.2f}（c9: +0.0002 t0.00）")

# ---- Q4 look-ahead assert ----
for name, _, _ in SCALES:
    kn = SC[name]["known"]; i = np.searchsorted(kn, q, side="right") - 1; ok = i >= 0
    assert np.all(kn[i[ok]] <= q[ok]), name
say("- look-ahead: 全 9 尺度で 付与した ER の既知時刻 ≤ q = te−24h を assert 済み")

# ---- Q1 sweep ----
say("\n## Q1 尺度掃引（P1 top−bot・P2 D_top/D_mid/D_bot・I=D_top−D_bot・3 窓）")
say("| 尺度 | 付与% | 在 P1 t | 在 D_top (t) | 在 D_bot (t) | 在 I t | 外 P1 t | 外 D_top (t) | 外 D_bot (t) | 外 I t (cl) | 近年 D_top (t) | 近年 D_bot (t) | 近年 I t (cl) | c9 読み規則(在) |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
regime_side = []
for name, _, _ in SCALES:
    a, o, c = RES[name]["在2010-20"], RES[name]["外2021-26"], RES[name]["近年2024-26"]
    cov = np.mean(~np.isnan(RES[name]["p"])) * 100
    rule = (a["tt"] >= 1.5) and (a["Db"] <= 0); regime_side.append((name, rule))
    say(f"| {name} | {cov:.1f} | {a['t1']:+.2f} | {a['Dt']:+.3f} ({a['tt']:+.2f}) | {a['Db']:+.3f} ({a['tb']:+.2f}) | {a['tI']:+.2f} | {o['t1']:+.2f} | {o['Dt']:+.3f} ({o['tt']:+.2f}) | {o['Db']:+.3f} ({o['tb']:+.2f}) | {o['tI']:+.2f} ({o['tcI']:+.2f}) | {c['Dt']:+.3f} ({c['tt']:+.2f}) | {c['Db']:+.3f} ({c['tb']:+.2f}) | {c['tI']:+.2f} ({c['tcI']:+.2f}) | {'レジーム側' if rule else '時代側'} |")
say(f"- 在で c9 規則（D_top t≥1.5 ∧ D_bot≤0）を満たす尺度: {[n for n, r in regime_side if r]}")
say("- MDE(I) 外: " + ", ".join(f"{n} {2*RES[n]['外2021-26']['seI']:.3f}R" for n, _, _ in SCALES))

# ---- family-wise permutation ----
say(f"\n## Q1b family-wise 置換（q を k 週 循環シフト・全 9 尺度に同じ k・{NPERM} 回）")
lo = SC["250d"]["known"][~np.isnan(SC["250d"]["p"])][0]; hi = ts[-1] - 2 * 86400; span_w = (hi - lo) // 604800
obs_S1 = np.nanmax(np.abs([RES[n]["外2021-26"]["tI"] for n, _, _ in SCALES]))
obs_S2 = np.nanmax(np.abs([RES[n]["近年2024-26"]["tI"] for n, _, _ in SCALES]))
obs_S3 = np.nanmax([RES[n]["在2010-20"]["tt"] for n, _, _ in SCALES])
obs_S4 = np.nanmax(np.abs([RES[n]["外2021-26"]["t1"] for n, _, _ in SCALES]))
nullS = np.full((NPERM, 4), np.nan); null_tI_o = np.full((NPERM, 9), np.nan); null_tI_r = np.full((NPERM, 9), np.nan)
tp = time.time()
mO, mR, mI = W["外2021-26"], W["近年2024-26"], W["在2010-20"]
for pp in range(NPERM):
    k = int(rng.integers(8, span_w - 8)); qq = lo + ((q - lo + k * 604800) % (span_w * 604800))
    tIo = []; tIr = []; tDi = []; tP1o = []
    for j, (name, _, _) in enumerate(SCALES):
        p = attach(X, SC[name], qq)
        ro = p1p2(p, mO, want_cl=False); rr = p1p2(p, mR, want_cl=False); ri = p1p2(p, mI, want_cl=False)
        tIo.append(ro["tI"]); tIr.append(rr["tI"]); tDi.append(ri["tt"]); tP1o.append(ro["t1"])
    null_tI_o[pp] = tIo; null_tI_r[pp] = tIr
    nullS[pp] = [np.nanmax(np.abs(tIo)), np.nanmax(np.abs(tIr)), np.nanmax(tDi), np.nanmax(np.abs(tP1o))]
    if time.time() - tp > 300: say(f"!! 置換 {pp+1} 回で時間上限"); nullS = nullS[:pp + 1]; null_tI_o = null_tI_o[:pp + 1]; null_tI_r = null_tI_r[:pp + 1]; break
pS1 = (nullS[:, 0] >= obs_S1).mean(); pS2 = (nullS[:, 1] >= obs_S2).mean(); pS3 = (nullS[:, 2] >= obs_S3).mean(); pS4 = (nullS[:, 3] >= obs_S4).mean()
say(f"- S1 外 9 尺度 max|t_I| 観測 {obs_S1:.2f} → 帰無 中央値 {np.median(nullS[:,0]):.2f} / 95%点 {np.quantile(nullS[:,0],0.95):.2f} / **p_fw {pS1:.3f}**（{len(nullS)} 回・{time.time()-tp:.0f} s）")
say(f"- S2 近年 9 尺度 max|t_I| 観測 {obs_S2:.2f} → 帰無 中央値 {np.median(nullS[:,1]):.2f} / 95%点 {np.quantile(nullS[:,1],0.95):.2f} / **p_fw {pS2:.3f}**")
say(f"- S3 在 9 尺度 max t_Dtop（片側）観測 {obs_S3:.2f} → 帰無 中央値 {np.median(nullS[:,2]):.2f} / 95%点 {np.quantile(nullS[:,2],0.95):.2f} / **p_fw {pS3:.3f}**")
say(f"- S4 外 9 尺度 max|t_P1| 観測 {obs_S4:.2f} → 帰無 中央値 {np.median(nullS[:,3]):.2f} / 95%点 {np.quantile(nullS[:,3],0.95):.2f} / **p_fw {pS4:.3f}**")
say("- 単尺度置換 p（外 t_I）: " + ", ".join(f"{n} {(np.abs(null_tI_o[:,j]) >= abs(RES[n]['外2021-26']['tI'])).mean():.3f}(sd {np.nanstd(null_tI_o[:,j]):.2f})" for j, (n, _, _) in enumerate(SCALES)))
say("- 単尺度置換 p（近年 t_I）: " + ", ".join(f"{n} {(np.abs(null_tI_r[:,j]) >= abs(RES[n]['近年2024-26']['tI'])).mean():.3f}(sd {np.nanstd(null_tI_r[:,j]):.2f})" for j, (n, _, _) in enumerate(SCALES)))

# ---- Q2 weak-signal robustness (ER20 recent) ----
say("\n## Q2 弱信号（近年 ER20 D_top +0.206 / I +0.149）の定義揺らぎ 8 変種")
variants = []
def report_variant(label, p, m=W["近年2024-26"]):
    r = p1p2(p, m); variants.append((label, r["tt"], r["tI"]))
    say(f"- {label}: D_top {r['Dt']:+.4f} (t{r['tt']:+.2f}, n{r['nA'][0]}:{r['nA'][1]}) / D_bot {r['Db']:+.4f} (t{r['tb']:+.2f}) → I {r['I']:+.4f} t {r['tI']:+.2f} (cl {r['tcI']:+.2f})")
report_variant("基準（22:00 境界・pct・ラグ 24h）", RES["20d"]["p"])
for off_h in (0, 12, 17):
    DAYv = last_close_grid(ts, lc, 86400, off_h * 3600); scv = build_scale("20d", "D", 20, DAYg=DAYv)
    report_variant(f"(a) 擬似日境界 {off_h:02d}:00 UTC", asof(scv["known"], scv["p"], q, 5 * 86400))
erv = SC["20d"]["er"]; med = np.nanmedian(erv)
p_abs = np.where(np.isnan(erv), np.nan, np.where(erv >= med + 0.1, 1.0, np.where(erv <= med - 0.1, 0.0, 0.5)))
report_variant(f"(b) 絶対閾値 ER20 ≥{med+0.1:.3f} / ≤{med-0.1:.3f}", asof(SC["20d"]["known"], p_abs, q, 5 * 86400))
for lag_h, lab in ((48, "(c) 参照ラグ 48h"), (0, "(c) 参照ラグ 0h（te 直前）")):
    report_variant(lab, asof(SC["20d"]["known"], SC["20d"]["p"], X["te"].to_numpy() - lag_h * 3600, 5 * 86400))
for y in (2024, 2025, 2026):
    report_variant(f"(d) 近年 LOYO 除{y}", RES["20d"]["p"], m=W["近年2024-26"] & (X.year != y).to_numpy())
keep = sum(1 for lab, tt, tI in variants[1:] if tI >= 1.5); nv = len(variants) - 1
keep_top = sum(1 for lab, tt, tI in variants[1:] if tt >= 2.0)
say(f"- **t_I ≥ 1.5 を保つ変種 {keep}/{nv}**・D_top t≥2 を保つ変種 {keep_top}/{nv}")

# ---- Q3 era vs regime decomposition ----
say("\n## Q3 時代 vs レジーム: 半期ごとの D と top 比率の横断相関（33 半期）・外の半期固定効果つき I")
halves = sorted(X["half"].unique())
Dh = []; nh = []
for h in halves:
    m = (X["half"] == h).to_numpy() & okA_all
    d, t, se = welch(R_all[m & A_all], R_all[m & ~A_all]); Dh.append(d); nh.append(int(m.sum()))
Dh = np.array(Dh)
say("- 半期別 D: " + " ".join(f"{h}:{d:+.2f}" for h, d in zip(halves, Dh)))
rhos = []
for name, _, _ in SCALES:
    p = RES[name]["p"]; frac = []
    for h in halves:
        m = (X["half"] == h).to_numpy() & ~np.isnan(p); frac.append(np.mean(p[m] >= 2 / 3) if m.sum() else np.nan)
    frac = np.array(frac); ok = ~np.isnan(frac) & ~np.isnan(Dh)
    rho = pd.Series(frac[ok]).corr(pd.Series(Dh[ok]), method="spearman")
    ok2 = ok & np.array([h >= "2021" for h in halves]); rho2 = pd.Series(frac[ok2]).corr(pd.Series(Dh[ok2]), method="spearman")
    rhos.append((name, rho, rho2))
say("- Spearman ρ(top 比率_半期, D_半期): " + ", ".join(f"{n} 全期 {r:+.2f} / 2021- {r2:+.2f}" for n, r, r2 in rhos))
say(f"- ρ ≥ 0.3（全期）の尺度: {[n for n, r, r2 in rhos if r >= 0.3]}")
# half-year fixed-effect I within OOS
row = []
for name, _, _ in SCALES:
    p = RES[name]["p"]; vals = []; ws = []
    for h in halves:
        if h < "2021": continue
        m = (X["half"] == h).to_numpy(); r = p1p2(p, m, want_cl=False)
        if not np.isnan(r["tI"]) and r["seI"] > 0: vals.append(r["I"]); ws.append(1 / r["seI"] ** 2)
    vals, ws = np.array(vals), np.array(ws); Iw = (vals * ws).sum() / ws.sum(); row.append(f"{name} {Iw:+.3f} (t{Iw*math.sqrt(ws.sum()):+.2f})")
say("- 外 2021-26 半期固定効果つき I（n 加重）: " + ", ".join(row))
# pooled I vs within: how much of OOS I is between-half-year?
say("- 参考: 外 pooled I: " + ", ".join(f"{n} {RES[n]['外2021-26']['I']:+.3f}" for n, _, _ in SCALES))

# ---- verdict ----
say("\n## 判定（事前固定・対象 = cycle9 の読み『継続は時代・ER では識別不能』）")
broken = False; broken_at = []
for name, _, _ in SCALES:
    a, o, c = RES[name]["在2010-20"], RES[name]["外2021-26"], RES[name]["近年2024-26"]
    if (a["tt"] >= 1.5) and (a["Db"] <= 0) and (o["tI"] >= 1.5) and (c["I"] > 0) and (pS1 < 0.05): broken = True; broken_at.append(name)
no_regime_in = all(not r for _, r in regime_side)
surv = no_regime_in and (pS1 > 0.05) and (pS2 > 0.05) and (keep < nv / 2) and (len([n for n, r, r2 in rhos if r >= 0.3]) == 0)
verdict = "broken" if broken else ("survived" if surv else "inconclusive")
say(f"- 在でレジーム側の尺度 0: {no_regime_in} / S1 p_fw {pS1:.3f} / S2 p_fw {pS2:.3f} / Q2 保持 {keep}/{nv} / Q3 ρ≥0.3 の尺度 {len([n for n, r, r2 in rhos if r >= 0.3])}")
say(f"\n**VERDICT: {verdict}**" + (f"（broken at {broken_at}）" if broken_at else ""))
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
