# -*- coding: utf-8 -*-
"""
[cycle68 研究レーン] 2026-11-25 — 【深化・出口/path】出口過程の cl_k マルコフ性 vs 「これまでの最悪点」
（running MAE_k）と「これまでの最良点」（running MFE_k）

=== 事前固定（この docstring を書いてから数字を見る・seed 不要） ===
背景: c7（経過時間 k）・c21（ET 時計）・c2（+1.0R 到達後の建値戻り＝MFE 系の規則）・c23（V_k 揺れ・O_k 占有時間）は
      全部 null で「出口過程は cl_k だけのマルコフ」と書いた。だが F_k 可測の主要変数のうち **足内の最悪点 MAE_k =
      min_{1≤j≤k} lo_j（R 単位）** は未検定。伝承は 2 つ逆向き: (a)「逆指値を試されて戻った本は弱い（売り圧力が居る）」→
      深く沈んだ本の残り path は悪い (b)「サポートが試されて守られた＝強い」→ 良い。c61/反証 c61 の「SL 決着後 +0.096」は
      決着“後”の話で、本件は決着“前”の生存本。入口フィルタではない・TP/SL 変更でもない・昇格提案ではない。
データ: data/c1_reaccel_paths_2010_2026.json（19404 本）＋ data/refute_c4_scan_paths（b）＋ data/refute_c2_fullpaths.npz
      （entry_time 昇順・切断なし・index0 = 建玉足・長さ hold+1・hiR/loR/clR）。scan 無し・M5 読込なし・MT5 無し・外部通信なし。
記帳の公正化（方法論 ①②③）: R* = R + ft（SL/TP）・TIME はそのまま。評価足 k は hold>k（決着足と混ぜない）。
      条件は k 終値までに判明する量のみ（足 1..k の高安・look-ahead なし）。建玉足 index0 は約定前レンジ混入のため除外。
状態変数（足 j=1..k・R 単位）:
  MAE_k = min_j lo_j  … これまでの最悪点（≤ cl_k・SL は −(1−ft) 付近）  [主]
  MFE_k = max_j hi_j  … これまでの最良点（≥ cl_k）                       [副・c2 の鏡像]
  （cl_k を揃えた上で MAE_k を切る＝「どれだけ戻したか」D_k = cl_k − MAE_k の三分位とほぼ同義）
格子: k ∈ {24, 12}（主 k=24）× 含み水準ビン B1 ≤−0.5 / B2 (−0.5,−0.2] / B3 (−0.2,+0.2) / B4 [+0.2,+0.5) / B5 ≥+0.5（c7/c23 と同じ）。
      三分位は (窓, k, B) 内で切る。top = MAE_k が高い（浅い＝沈んでいない）・bot = 低い（深く沈んで戻した）。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 長期は幾何の帰無検定のみ・edge 判定に不使用）。
統計: e = R* − cl_k の平均・Welch t（top−bot）・建玉日クラスタ t・プール β（(窓,k,B) 固定効果・z 内 demean・日クラスタ t）。
予測: 両側（伝承が逆向き 2 つ）。
  H_MAE: 主セル (k=24, B3) で ΔMAE = e(top 浅い) − e(bot 深い)。PASS = 在 |t|≥2 ∧ 外 同符号 |t|≥1.5 ∧ β_MAE 在外同符号。
  H_MFE: 主セル (k=24, B3) で ΔMFE = e(top 高い) − e(bot 低い)。PASS 同規則。
  探索格子: 2 変数 × 2 k × 5 B × 3 窓 = 60 セルは Bonferroni |t|≥3.0 で数えるだけ（主セルは 2 つ）。
  追加・事前宣言（記述）: 「逆指値の縁を試した本」= MAE_k ≤ −0.8 の生存本（B2/B3 で）の e vs 同セルの残り（Welch）。
合否: どちらか PASS → 「cl_k 以外に出口情報あり（構造記述・反証レーンへ）」。両方 FAIL → null（MDE 併記）＝マルコフ性は最悪点/最良点でも壊れない。
MDE: 主セル 2·se_Welch・δ=−0.05/−0.10R を top に注入した Welch t。
陽性対照（同じ信頼性クラス）: 公正化しない e_raw = e − ft·1{SL/TP} の既知 −ft シフトが大セルで t≪−2（c7/c23 と同じ）。
ベースライン: マルチンゲール（E[e|F_k]=0 → Δ=β=0）。
衛生（数字を読む前に印字）: ①全 path 点で lo ≤ cl ≤ hi ②SL 本の min lo ≤ −(1−ft)+0.02・TP 本の max hi ≥ b+ft−0.02（記帳規則の整合）
      ③主セル内 ρ(MAE_k, cl_k)・三分位の cl_k 平均差（方法論 ㉓: 0.05R 超なら注記）④三分位の幾何（b・risk・残り保有・決着内訳）。
事前の最重要反証: (1) MAE_k は cl_k と B 内でも相関し三分位が cl_k の水準差を拾う → cl_k 平均差を印字し B 固定効果の β で揃える。
      (2) 深く沈んだのに生きている本は SL が遠い（risk 大・b 小）の選択 → 幾何を印字。マルチンゲールなら幾何は e に効かない。
      (3) 60 セルの事後選択 → Bonferroni・主セル 2。(4) 同時刻重複 → 日クラスタ t。(5) bid のみ・5 分足の高安は ask 側の
      実逆指値到達を 0.1〜0.5 USD ずらす（XAU ask M1 要取得・既出）。
ゲート ㉛: n/a（出口側・入口条件づけではない）。昇格候補ではない。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c68_mae_so_far_markov_result.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)

def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 3: return np.nan, np.nan
    se = d.std(ddof=1) / math.sqrt(n)
    t = d.mean() / se if se > 0 else np.nan
    return t, (2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else np.nan)

def t_cluster(d, g):
    d = np.asarray(d, float); m = d.mean(); r = d - m
    s = pd.Series(r).groupby(np.asarray(g)).sum().to_numpy()
    se = math.sqrt((s ** 2).sum()) / len(d)
    return (m / se if se > 0 else np.nan), len(s)

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    diff = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return diff, (diff / se if se > 0 else np.nan), se

def welch_cluster(a, b, ga, gb):
    """top−bot 差の建玉日クラスタ t（両群の日合計を合わせて）"""
    a = np.asarray(a, float); b = np.asarray(b, float)
    diff = a.mean() - b.mean()
    ra = (a - a.mean()) / len(a); rb = -(b - b.mean()) / len(b)
    s = pd.Series(np.concatenate([ra, rb])).groupby(np.concatenate([ga, gb])).sum().to_numpy()
    se = math.sqrt((s ** 2).sum())
    return diff / se if se > 0 else np.nan

def ols_cluster(y, x, g):
    y = np.asarray(y, float); x = np.asarray(x, float)
    sxx = (x * x).sum()
    if sxx <= 0: return np.nan, np.nan
    beta = (x * y).sum() / sxx
    u = y - beta * x
    s = pd.Series(x * u).groupby(np.asarray(g)).sum().to_numpy()
    se = math.sqrt((s ** 2).sum()) / sxx
    return beta, (beta / se if se > 0 else np.nan)

# ---------- load ----------
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)   # c23 と同じ既定ソート
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
bmap = {t["entry_time"]: t["b"] for t in c4["trades"]}
df["b"] = df.entry_time.map(bmap)
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; hiR = z["hiR"]; loR = z["loR"]; off = z["off"]
n = len(df)
assert len(off) - 1 == n, "npz 本数不一致"
exp_hold = np.diff(off) - 1
if not np.all(exp_hold == df.hold.to_numpy()):
    # 衛生（cycle53）: entry_time 重複組の中を npz の hold 順に並べ替える
    bad_pos = np.nonzero(exp_hold != df.hold.to_numpy())[0]
    et = df.entry_time.to_numpy()
    order = np.arange(n)
    for p in np.unique(et[bad_pos]):
        grp = np.nonzero(et == p)[0]
        want = exp_hold[grp]; have = df.hold.to_numpy()[grp]
        perm = [int(grp[list(have).index(w)]) for w in want]  # 単純一致（重複 hold 組は無い前提・assert で確認）
        assert sorted(perm) == sorted(grp.tolist())
        order[grp] = perm
    df = df.iloc[order].reset_index(drop=True)
    print(f"[hygiene] entry_time 重複組の並べ替え: {len(bad_pos)} 行 → 修正")
    assert np.all(np.diff(off) == df.hold.to_numpy() + 1), "path 長 ≠ hold+1"
risk = df.risk.to_numpy(); ft = FT / risk; R = df.R.to_numpy(); hold = df.hold.to_numpy()
exitr = df.exit_reason.to_numpy()
is_slt = df.exit_reason.isin(["SL", "TP"]).to_numpy()
Rstar = R + ft * is_slt
day = df.entry_time.to_numpy() // 86400
year = df.year.to_numpy()
bb = df.b.to_numpy()
W = {"在2010-20": year <= 2020, "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
KS = (24, 12)
BINS = ["B1 ≤−0.5", "B2 (−0.5,−0.2]", "B3 (−0.2,+0.2)", "B4 [+0.2,+0.5)", "B5 ≥+0.5"]
def binidx(x):
    return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))

say(f"# [cycle68] 出口過程のマルコフ性 vs 最悪点 MAE_k／最良点 MFE_k（running）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c68_mae_so_far_markov.py)")
say(f"n={n} 本 2010-01..2026-06、FEED_TOL={FT}、ft 平均 {ft.mean():.4f}R、SL/TP {is_slt.sum()}・TIME {(~is_slt).sum()}。R* 平均 {Rstar.mean():+.4f}（gross {R.mean():+.4f}）。path 点 {len(clR)}。")
say(f"建玉中本数（hold>k）: " + " / ".join(f"k={k}: {(hold > k).sum()}" for k in KS))
say()

# ---------- 衛生 ----------
say("## 衛生（数字を読む前）")
bad = ((loR > clR + 1e-9) | (clR > hiR + 1e-9)).sum()
say(f"- ① lo ≤ cl ≤ hi 違反 path 点: **{bad}** / {len(clR)}")
# SL 本の min lo（足 1..hold）/ TP 本の max hi
minlo = np.full(n, np.nan); maxhi = np.full(n, np.nan)
for i in range(n):
    a, e_ = off[i] + 1, off[i + 1]
    if e_ > a:
        minlo[i] = loR[a:e_].min(); maxhi[i] = hiR[a:e_].max()
sl = (exitr == "SL") & (hold >= 1); tp = (exitr == "TP") & (hold >= 1)
ok_sl = (minlo[sl] <= -(1 - ft[sl]) + 0.02).mean(); ok_tp = (maxhi[tp] >= (bb[tp] + ft[tp]) - 0.02).mean()
say(f"- ② SL 本（hold≥1・n {sl.sum()}）の min lo ≤ −(1−ft)+0.02: **{100*ok_sl:.2f}%**（min lo 中央値 {np.nanmedian(minlo[sl]):+.3f}）／TP 本（n {tp.sum()}）の max hi ≥ b+ft−0.02: **{100*ok_tp:.2f}%**（max hi 中央値 {np.nanmedian(maxhi[tp]):+.3f}・b 中央値 {np.nanmedian(bb[tp]):.2f}）")
say(f"- 単位の読み: loR/hiR/clR は side 符号つき R 単位（SL = −1 付近・TP = +b 付近）であることを②で確認。")
say()

# ---------- state variables ----------
S = {}
for k in KS:
    alive = np.nonzero(hold > k)[0]
    idx = off[alive][:, None] + np.arange(1, k + 1)[None, :]       # 足 1..k（建玉足 0 は除外）
    P = clR[idx]; LO = loR[idx]; HI = hiR[idx]
    MAE = LO.min(axis=1); MFE = HI.max(axis=1)
    clk = P[:, -1]
    e = Rstar[alive] - clk
    S[k] = dict(alive=alive, clk=clk, e=e, MAE=MAE, MFE=MFE, D=clk - MAE, U=MFE - clk, b=binidx(clk))

# ---------- 0. 記述 ----------
say("## 0. 状態変数の分布（B3 セル）・cl_k との相関・陽性対照（e_raw の既知 −ft シフト）")
say("| 窓 | k | n(B3) | MAE 中央値 (p10/p90) | MFE 中央値 (p10/p90) | ρ(MAE,cl_k) B3 | ρ(MFE,cl_k) B3 | ρ(MAE,MFE) B3 | MAE≤−0.8 率 | e_raw mean / t（B3） | 期待 −ft·P |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    for k in KS:
        s = S[k]; m = wm[s["alive"]] & (s["b"] == 2)
        if m.sum() < 30: continue
        A, F, c, e = s["MAE"][m], s["MFE"][m], s["clk"][m], s["e"][m]
        er = e - ft[s["alive"]][m] * is_slt[s["alive"]][m]
        say(f"| {wn} | {k} | {m.sum()} | {np.median(A):+.3f} ({np.percentile(A,10):+.3f}/{np.percentile(A,90):+.3f}) | {np.median(F):+.3f} ({np.percentile(F,10):+.3f}/{np.percentile(F,90):+.3f}) | {np.corrcoef(A,c)[0,1]:+.2f} | {np.corrcoef(F,c)[0,1]:+.2f} | {np.corrcoef(A,F)[0,1]:+.2f} | {100*(A<=-0.8).mean():.1f}% | {er.mean():+.4f} / {tstat(er)[0]:+.2f} | {-(ft[s['alive']][m]*is_slt[s['alive']][m]).mean():+.4f} |")
say()

# ---------- 1. 三分位 ----------
say("## 1. 三分位（(窓,k,B) 内で切る）: e(top) − e(bottom)（Welch）— 60 セル Bonferroni |t|≥3.0")
say("top = 変数が高い（MAE: 浅い＝沈んでいない／MFE: 高い＝走っていた）・bot = 低い（MAE: 深く沈んで戻した／MFE: 伸びていない）")
cells = []
PRIM = {}
for var in ("MAE", "MFE"):
    say(f"### 変数 {var}: diff / Welch t / 日クラスタ t / n_top:n_bot ／ [top の cl_k 平均 − bot の cl_k 平均]")
    say("| 窓 | k | " + " | ".join(BINS) + " |")
    say("|---|---|" + "---|" * len(BINS))
    for wn, wm in W.items():
        for k in KS:
            s = S[k]; row = []
            for bi, bn in enumerate(BINS):
                m = wm[s["alive"]] & (s["b"] == bi)
                if m.sum() < 60: row.append(f"n={m.sum()}"); continue
                x = s[var][m]; e = s["e"][m]; c = s["clk"][m]; g = day[s["alive"]][m]
                q1, q2 = np.quantile(x, [1/3, 2/3])
                top = x >= q2; bot = x <= q1
                dd, tw, se = welch(e[top], e[bot])
                tc = welch_cluster(e[top], e[bot], g[top], g[bot])
                dcl = c[top].mean() - c[bot].mean()
                cells.append((var, wn, k, bn, dd, tw))
                row.append(f"{dd:+.3f} / {tw:+.2f} / {tc:+.2f} / {top.sum()}:{bot.sum()} [{dcl:+.3f}]")
                if bi == 2:
                    PRIM[(var, wn, k)] = dict(dd=dd, tw=tw, tc=tc, se=se, ntop=top.sum(), nbot=bot.sum(), dcl=dcl,
                                               etop=e[top], ebot=e[bot], top=top, bot=bot, m=m)
            say(f"| {wn} | k={k} | " + " | ".join(row) + " |")
    say()
ts = np.array([c[5] for c in cells if not np.isnan(c[5])])
say(f"セル数 {len(ts)}・名目 |t|>2: **{(np.abs(ts)>2).sum()}**（期待 {0.0455*len(ts):.1f}）・Bonferroni |t|≥3.0: **{(np.abs(ts)>=3.0).sum()}**・max|t| {np.abs(ts).max():.2f}・t の sd {ts.std(ddof=1):.2f}（帰無 ≈1）")
say()

# ---------- 2. プール回帰 ----------
say("## 2. プール回帰: e（(k,B) 内 demean）~ z（(k,B) 内で標準化した MAE または MFE）— β（R / 1sd）・日クラスタ t・n")
say("| 窓 | 変数 | k=24 β / t / n | k=12 β / t / n | k 両方 β / t / n |")
say("|---|---|---|---|---|")
BETA = {}
for wn, wm in W.items():
    for var in ("MAE", "MFE"):
        parts = []; Ys, Xs, Gs = [], [], []
        for k in KS:
            s = S[k]; m = wm[s["alive"]]
            y = s["e"][m].copy(); x = s[var][m].copy(); g = s["b"][m]; dgrp = day[s["alive"]][m]
            for bi in range(5):
                q = g == bi
                if q.sum() < 30: y[q] = np.nan; continue
                y[q] -= y[q].mean(); sd = x[q].std(ddof=1); x[q] = (x[q] - x[q].mean()) / (sd if sd > 0 else 1)
            ok = ~np.isnan(y)
            beta, tb = ols_cluster(y[ok], x[ok], dgrp[ok]); BETA[(wn, var, k)] = (beta, tb)
            parts.append(f"{beta:+.4f} / {tb:+.2f} / {ok.sum()}")
            Ys.append(y[ok]); Xs.append(x[ok]); Gs.append(dgrp[ok])
        beta, tb = ols_cluster(np.concatenate(Ys), np.concatenate(Xs), np.concatenate(Gs)); BETA[(wn, var, "all")] = (beta, tb)
        parts.append(f"{beta:+.4f} / {tb:+.2f} / {sum(len(y) for y in Ys)}")
        say(f"| {wn} | {var} | " + " | ".join(parts) + " |")
say("（k=12 と k=24 は同じ本が重複し得るので「k 両方」は日クラスタ t だけ参照。）")
say()

# ---------- 2b. cl_k を連続で統制した β（反証 (1)） ----------
say("## 2b. 反証 (1): B 内の cl_k を連続で統制（e ~ z(MAE) + cl_k demean・(k,B) 内）— β_MAE の変化")
say("| 窓 | k | β_MAE 単独 / t | β_MAE | cl_k 統制 / t | β_cl / t |")
say("|---|---|---|---|---|")
for wn, wm in W.items():
    for k in KS:
        s = S[k]; m = wm[s["alive"]]
        y = s["e"][m].copy(); x = s["MAE"][m].copy(); c = s["clk"][m].copy(); g = s["b"][m]; dgrp = day[s["alive"]][m]
        for bi in range(5):
            q = g == bi
            if q.sum() < 30: y[q] = np.nan; continue
            y[q] -= y[q].mean(); c[q] -= c[q].mean(); sd = x[q].std(ddof=1); x[q] = (x[q] - x[q].mean()) / (sd if sd > 0 else 1)
        ok = ~np.isnan(y)
        b1, t1 = ols_cluster(y[ok], x[ok], dgrp[ok])
        X = np.column_stack([x[ok], c[ok]]); Y = y[ok]
        beta2 = np.linalg.lstsq(X, Y, rcond=None)[0]
        u = Y - X @ beta2
        # クラスタ頑健 se（sandwich）
        XtX_inv = np.linalg.inv(X.T @ X)
        dfm = pd.DataFrame(X * u[:, None]); dfm["g"] = dgrp[ok]
        Sg = dfm.groupby("g").sum().to_numpy()
        V = XtX_inv @ (Sg.T @ Sg) @ XtX_inv
        se2 = np.sqrt(np.diag(V))
        say(f"| {wn} | {k} | {b1:+.4f} / {t1:+.2f} | {beta2[0]:+.4f} / {beta2[0]/se2[0]:+.2f} | {beta2[1]:+.4f} / {beta2[1]/se2[1]:+.2f} |")
say()

# ---------- 3. 主セルの幾何・MDE・注入 ----------
say("## 3. 主セル (k=24, B3) 三分位の幾何（b・risk・残り保有・決着内訳）・MDE・注入")
say("| 窓 | 変数 | 群 | n | e mean / t | cl_k 平均 | 変数 平均 | b 中央値 | risk 中央値 (USD) | 残り保有 中央値 | SL% / TP% / TIME% |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
s = S[24]
for wn in W:
    for var in ("MAE", "MFE"):
        p = PRIM.get((var, wn, 24))
        if p is None: continue
        al = s["alive"][p["m"]]
        for lab, q in (("top", p["top"]), ("bot", p["bot"])):
            ex = exitr[al][q]; ee = p["etop"] if lab == "top" else p["ebot"]
            say(f"| {wn} | {var} | {lab} | {q.sum()} | {ee.mean():+.4f} / {tstat(ee)[0]:+.2f} | {s['clk'][p['m']][q].mean():+.3f} | {s[var][p['m']][q].mean():+.3f} | {np.nanmedian(bb[al][q]):.2f} | {np.median(risk[al][q]):.2f} | {np.median(hold[al][q]-24):.0f} | {100*(ex=='SL').mean():.0f} / {100*(ex=='TP').mean():.0f} / {100*(ex=='TIME').mean():.0f} |")
say()
say("| 窓 | 変数 | Δ (top−bot) / Welch t / 日cl t | MDE (2·se) | 注入 δ=−0.05R(top) → t | δ=−0.10R → t |")
say("|---|---|---|---|---|---|")
for wn in W:
    for var in ("MAE", "MFE"):
        p = PRIM.get((var, wn, 24))
        if p is None: continue
        t5 = welch(p["etop"] - 0.05, p["ebot"])[1]; t10 = welch(p["etop"] - 0.10, p["ebot"])[1]
        say(f"| {wn} | {var} | {p['dd']:+.4f} / {p['tw']:+.2f} / {p['tc']:+.2f} | {2*p['se']:.3f}R | {t5:+.2f} | {t10:+.2f} |")
say()

# ---------- 4. 事前宣言の記述: 逆指値の縁を試した本 ----------
say("## 4. 記述（事前宣言）: 「逆指値の縁を試した本」MAE_k ≤ −0.8 の生存本 vs 同 (窓,k,B) の残り（B2・B3）— Welch")
say("| 窓 | k | B | n(試した):n(残り) | e(試した) / t | e(残り) / t | Δ / Welch t | cl_k 平均差 | 試した本の TP% vs 残り |")
say("|---|---|---|---|---|---|---|---|---|")
for wn, wm in W.items():
    for k in KS:
        s = S[k]
        for bi in (1, 2):
            m = wm[s["alive"]] & (s["b"] == bi)
            A = s["MAE"][m]; e = s["e"][m]; c = s["clk"][m]; al = s["alive"][m]
            q = A <= -0.8
            if q.sum() < 20 or (~q).sum() < 20: say(f"| {wn} | {k} | {BINS[bi]} | {q.sum()}:{(~q).sum()} | n 不足 | | | | |"); continue
            dd, tw, _ = welch(e[q], e[~q])
            say(f"| {wn} | {k} | {BINS[bi]} | {q.sum()}:{(~q).sum()} | {e[q].mean():+.4f} / {tstat(e[q])[0]:+.2f} | {e[~q].mean():+.4f} / {tstat(e[~q])[0]:+.2f} | {dd:+.4f} / {tw:+.2f} | {c[q].mean()-c[~q].mean():+.3f} | {100*(exitr[al][q]=='TP').mean():.0f}% vs {100*(exitr[al][~q]=='TP').mean():.0f}% |")
say()

# ---------- 5. 記述: 側別 ----------
say("## 5. 記述: 主セルの差の側別（判定不使用）")
side = df.side.to_numpy(); s = S[24]
for wn, wm in W.items():
    parts = []
    for var in ("MAE", "MFE"):
        p = PRIM.get((var, wn, 24))
        if p is None: continue
        al = s["alive"][p["m"]]
        for sd_ in ("BUY", "SELL"):
            q = side[al] == sd_
            dd, tw, _ = welch(p["etop"][q[p["top"]]], p["ebot"][q[p["bot"]]])
            parts.append(f"{var}×{sd_} {dd:+.3f} (t{tw:+.2f}, {q[p['top']].sum()}:{q[p['bot']].sum()})")
    say(f"- {wn}: " + "；".join(parts))
say()

# ---------- verdict ----------
say("## 判定（事前規則）")
res = {}
for var in ("MAE", "MFE"):
    a, b_ = PRIM[(var, "在2010-20", 24)], PRIM[(var, "外2021-26", 24)]
    bi_, bo_ = BETA[("在2010-20", var, "all")], BETA[("外2021-26", var, "all")]
    H = (abs(a["tw"]) >= 2) and (np.sign(a["dd"]) == np.sign(b_["dd"])) and (abs(b_["tw"]) >= 1.5) and (np.sign(bi_[0]) == np.sign(bo_[0]))
    res[var] = H
    say(f"- H_{var}（両側）: 主セル Δ 在 {a['dd']:+.4f} t {a['tw']:+.2f}（日cl {a['tc']:+.2f}）/ 外 {b_['dd']:+.4f} t {b_['tw']:+.2f}（日cl {b_['tc']:+.2f}）；β 在 {bi_[0]:+.4f} (t{bi_[1]:+.2f}) / 外 {bo_[0]:+.4f} (t{bo_[1]:+.2f}) → **{'PASS' if H else 'FAIL'}**")
    say(f"  MDE（主セル 2·se）: 在 {2*a['se']:.3f}R / 外 {2*b_['se']:.3f}R")
say(f"\n**結論: {'cl_k 以外に出口情報あり（構造記述・反証レーンへ）' if any(res.values()) else 'null（最悪点 MAE_k・最良点 MFE_k に出口情報なし・MDE 以下）＝出口過程の cl_k マルコフ性は running MAE/MFE でも壊れない'}**")
say(f"\n実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
