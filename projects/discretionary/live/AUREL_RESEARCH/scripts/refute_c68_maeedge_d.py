# -*- coding: utf-8 -*-
"""
[REFUTE c68 — d] 2026-11-25 第 4 走（最後）。T1 の機構に対する決定的 2 本。

a〜c 走で私の機械的攻撃は全部失敗した（閾値の隣・コスト 3 倍・日クラスタ・ブロック boot・1 点抜き・
順位・b 統制・b/risk 三分位マッチ・V_k 統制・年構成の層別調整 → Δ は 92〜104% 残る）。
c 走 A17 で分かったこと: 外 B2 の +0.33R は「決着の混ざり」で 40% しか説明できず、残りは
「TP 本の中で 試した群の b が大きい（+0.599R・t +3.75）」＝高ボラ本が遠い TP まで届いている。

残る 2 つの可能性を分ける。数字を見る前に固定:
H_vol: 「縁を試した」は単に**足 1..k のレンジが大きい本**の別名（c68 の結論 (2)）。
       ⇒ 鏡像の集合「上に +0.8R 行って B2 まで戻した本」（MFE_k ≥ +0.8）**も同じ Δ を出すはず**。
       ⇒ また、総レンジ（MFE − MAE）の三分位**だけ**で同じ Δ が出るはず。
H_stop: 「下の縁を試して守られた」こと自体に方向情報がある（伝承 (b)）。
       ⇒ 鏡像は Δ を出さない（または逆符号）・下側 MAE に固有。

A19 鏡像テスト（決定的・事前固定）: 同じ (外, k=24, B2) セル内で
     (i) MAE_k ≤ −0.8（c68・下の縁）(ii) MFE_k ≥ +0.8（上に行って戻した）(iii) 総レンジ MFE−MAE 上位 1/3
     (iv) MAE≤−0.8 かつ MFE<+0.8（下だけ）(v) MFE≥+0.8 かつ MAE>−0.8（上だけ）の Δ/t。
     **破壊条件 D1: (ii) または (iii) の Δ が (i) の 70% 以上かつ |t| ≥ 1.5** → H_vol 採択 ＝ T1 は
     「レンジの別名」で最悪点固有ではない ＝ c68 の肯定形記述の中身（「逆指値の縁」）が壊れる。

A20 バリア・マルチンゲール対照（c68 §4 に対照が無かった点）: 連続経路の無ドリフト RW では
     P(上バリア先着) = d_down/(d_down+d_up)（ボラに依らない）。各本の cl_k・b・ft から
     d_up = b+ft−cl_k・d_down = (1−ft)+cl_k を計算し、SL/TP 決着本の中で
     観測 TP 率 − 含意 TP 率 = Δp を群別に出す（二項 se）。
     **破壊条件 D2: 「試した」群の Δp が 0 と区別できない（|z| < 1.5）** → +0.33R は
     バリア距離の違いの帰結で、ドリフトではない。

A21 在 の負の対照を同じ 2 本で（在で (ii)(iii) が出るなら私の鏡像テスト自体がノイズ）。

判定: D1 または D2 が発火 → T1 の**機構主張**は broken。両方非発火 → T1 は私の全攻撃を生き延びた
     （＝多重検定の p 0.065〜0.173 と「外は 近年 50 本が担ぐ」という**証拠構造**の弱さだけが残る）。
データ: c68 と同一キャッシュのみ。scan/M5/MT5/外部通信/発注/本番書込 なし。
"""
import json, os, time, math
import numpy as np, pandas as pd

t0 = time.time()
rng = np.random.default_rng(2026112504)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c68_maeedge_d.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se

J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
df = pd.DataFrame([{k: t[k] for k in ("entry_time", "year", "side", "risk", "R", "exit_reason", "hold")} for t in J["trades"]])
df = df.sort_values("entry_time").reset_index(drop=True)
c4 = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
df["b"] = df.entry_time.map({t["entry_time"]: t["b"] for t in c4["trades"]})
FT = J["frozen"]["FEED_TOL"]
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz"))
clR = z["clR"]; hiR = z["hiR"]; loR = z["loR"]; off = z["off"]
n = len(df); exp_hold = np.diff(off) - 1
if not np.all(exp_hold == df.hold.to_numpy()):
    bad = np.nonzero(exp_hold != df.hold.to_numpy())[0]; et = df.entry_time.to_numpy(); order = np.arange(n)
    for p in np.unique(et[bad]):
        grp = np.nonzero(et == p)[0]; want = exp_hold[grp]; have = df.hold.to_numpy()[grp]
        order[grp] = [int(grp[list(have).index(w)]) for w in want]
    df = df.iloc[order].reset_index(drop=True)
risk = df.risk.to_numpy(); ft = FT / risk; R = df.R.to_numpy(); hold = df.hold.to_numpy()
exitr = df.exit_reason.to_numpy(); is_slt = df.exit_reason.isin(["SL", "TP"]).to_numpy()
Rstar = R + ft * is_slt; year = df.year.to_numpy(); bb = df.b.to_numpy(); day = df.entry_time.to_numpy() // 86400
def binidx(x): return np.where(x <= -0.5, 0, np.where(x <= -0.2, 1, np.where(x < 0.2, 2, np.where(x < 0.5, 3, 4))))
W = {"在2010-20": year <= 2020, "外前2021-23": (year >= 2021) & (year <= 2023), "外2021-26": year >= 2021, "近年2024-26": year >= 2024}
S = {}
for k in (24,):
    alive = np.nonzero(hold > k)[0]
    idx = off[alive][:, None] + np.arange(1, k + 1)[None, :]
    LO = loR[idx]; HI = hiR[idx]; clk = clR[idx][:, -1]
    S[k] = dict(alive=alive, clk=clk, e=Rstar[alive] - clk, MAE=LO.min(axis=1), MFE=HI.max(axis=1), b=binidx(clk))
K = 24
say(f"# [REFUTE c68 d] 鏡像テストとバリア・マルチンゲール対照 — {time.strftime('%Y-%m-%d %H:%M')}")
say()

# ===== A19 鏡像 =====
say("## A19 鏡像テスト（H_vol: レンジの別名か／H_stop: 下の縁に固有か）— k=24・B2 (−0.5,−0.2] 内")
say("| 窓 | 集合 | n(群):n(残) | Δ | t | c68 の (i) に対する % |")
say("|---|---|---|---|---|---|")
D1vals = {}
for wn in ("在2010-20", "外前2021-23", "外2021-26", "近年2024-26"):
    s = S[K]; m = W[wn][s["alive"]] & (s["b"] == 1)
    e = s["e"][m]; A = s["MAE"][m]; F = s["MFE"][m]; rng_ = F - A
    base = None; got = {}
    defs = [("(i) MAE≤−0.8（下の縁・c68）", A <= -0.8),
            ("(ii) MFE≥+0.8（上に行って戻した・鏡像）", F >= +0.8),
            ("(iii) 総レンジ MFE−MAE 上位 1/3", rng_ >= np.quantile(rng_, 2/3)),
            ("(iv) 下だけ（MAE≤−0.8 ∧ MFE<+0.8）", (A <= -0.8) & (F < 0.8)),
            ("(v) 上だけ（MFE≥+0.8 ∧ MAE>−0.8）", (F >= 0.8) & (A > -0.8))]
    for dn, q in defs:
        if q.sum() < 10 or (~q).sum() < 10:
            say(f"| {wn} | {dn} | {q.sum()}:{(~q).sum()} | n 不足 | | |"); continue
        dd, tw, _ = welch(e[q], e[~q])
        if base is None: base = dd
        got[dn.split(" ")[0]] = (dd, tw)
        say(f"| {wn} | {dn} | {q.sum()}:{(~q).sum()} | {dd:+.4f} | {tw:+.2f} | {100*dd/base:.0f}% |")
    D1vals[wn] = (base, got)
    say(f"| {wn} | — | | | | |")
bo, gt = D1vals["外2021-26"]
r2 = gt.get("(ii)"); r3 = gt.get("(iii)")
D1_fire = any((r is not None) and (abs(r[0] / bo) >= 0.70) and (abs(r[1]) >= 1.5) for r in (r2, r3))
say(f"\n→ 外: (i) {bo:+.4f}／(ii) {r2[0]:+.4f} (t{r2[1]:+.2f}・{100*r2[0]/bo:.0f}%)／(iii) {r3[0]:+.4f} (t{r3[1]:+.2f}・{100*r3[0]/bo:.0f}%)")
say(f"→ **破壊条件 D1（鏡像 or 総レンジ が 70% 以上 ∧ |t|≥1.5）: {'発火 ＝ H_vol（レンジの別名）' if D1_fire else '非発火 ＝ H_stop 側（下側固有）'}**")
say()

# ===== A20 バリア・マルチンゲール対照 =====
say("## A20 バリア・マルチンゲール対照: 無ドリフト連続 RW の含意 TP 率 = d_down/(d_down+d_up)（ボラ非依存）")
say("d_up = b+ft−cl_k・d_down = (1−ft)+cl_k。SL/TP 決着本のみ（TIME は除外・除外率も印字）。")
say("| 窓 | 群 | n(SL/TP 決着) | TIME 除外 | 観測 TP 率 | 含意 TP 率 | Δp | 二項 z | d_up 平均 | d_down 平均 |")
say("|---|---|---|---|---|---|---|---|---|---|")
D2z = {}
for wn in ("在2010-20", "外前2021-23", "外2021-26", "近年2024-26"):
    s = S[K]; m = W[wn][s["alive"]] & (s["b"] == 1); al = s["alive"][m]
    A = s["MAE"][m]; c = s["clk"][m]
    d_up = bb[al] + ft[al] - c; d_dn = (1 - ft[al]) + c
    pimp = d_dn / (d_dn + d_up)
    ex = exitr[al]; res = (ex == "SL") | (ex == "TP")
    for lab, q in (("試した", A <= -0.8), ("残り", A > -0.8)):
        sl_ = q & res
        if sl_.sum() < 15: say(f"| {wn} | {lab} | {sl_.sum()} | — | n 不足 | | | | | |"); continue
        obs = (ex[sl_] == "TP").mean(); imp = pimp[sl_].mean()
        se = math.sqrt(max(imp * (1 - imp), 1e-9) / sl_.sum())
        zz = (obs - imp) / se
        if lab == "試した": D2z[wn] = zz
        say(f"| {wn} | {lab} | {sl_.sum()} | {100*(q.sum()-sl_.sum())/max(q.sum(),1):.0f}% | {obs:.3f} | {imp:.3f} | **{obs-imp:+.3f}** | **{zz:+.2f}** | {d_up[sl_].mean():.3f} | {d_dn[sl_].mean():.3f} |")
D2_fire = abs(D2z.get("外2021-26", 0)) < 1.5
say(f"\n→ 外「試した」群の Δp z = {D2z.get('外2021-26'):+.2f} → **破壊条件 D2（|z|<1.5）: {'発火 ＝ バリア距離の帰結' if D2_fire else '非発火 ＝ 無ドリフト RW では説明できない'}**")
say()
say("### 対照の健全性: 同じ指標を B3/B1 と MFE 鏡像群でも（対照が常に 0 を返すなら対照が無力）")
say("| 窓 | セル | 群 | n | 観測 − 含意 | z |")
say("|---|---|---|---|---|---|")
for wn in ("在2010-20", "外2021-26"):
    for bi in (0, 1, 2):
        s = S[K]; m = W[wn][s["alive"]] & (s["b"] == bi); al = s["alive"][m]
        if m.sum() < 60: continue
        A = s["MAE"][m]; F = s["MFE"][m]; c = s["clk"][m]
        d_up = bb[al] + ft[al] - c; d_dn = (1 - ft[al]) + c; pimp = d_dn / (d_dn + d_up)
        ex = exitr[al]; res = (ex == "SL") | (ex == "TP")
        for lab, q in (("MAE≤−0.8", A <= -0.8), ("MFE≥+0.8", F >= 0.8), ("全体", np.ones(m.sum(), bool))):
            sl_ = q & res
            if sl_.sum() < 15: continue
            obs = (ex[sl_] == "TP").mean(); imp = pimp[sl_].mean()
            se = math.sqrt(max(imp * (1 - imp), 1e-9) / sl_.sum())
            say(f"| {wn} | {['B1','B2','B3'][bi]} | {lab} | {sl_.sum()} | {obs-imp:+.3f} | {(obs-imp)/se:+.2f} |")
say()
say(f"実行 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("→", OUT)
