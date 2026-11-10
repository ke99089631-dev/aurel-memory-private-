"""
[REFUTE c36 補足 b] 2026-11-11 — 事後（refute_c36_friday_late.py R4 で見えた形）の追試・記述
R4 の発見: 在 金曜 − 基準 の超過は 12–14 +1.3 (t 0.95)／14–16 +3.9 (t 3.55)／16–16:55 +2.6 (t 4.85)。外は 14–16 −4.6 (t −2.74)／16–16:55 +5.2 (t 5.60)。
→ c36 の「late 12:00–16:55 が消えた」は、16:00–16:55 の金曜超過（在外とも正・外の方が大きい）を 12–16 の符号反転が相殺した窓の人工物の疑い。
ここは事後（23 時間セル × 5 曜日 = 115 セルから目で選んだ）なので判定ではなく、研究レーンの前向き事前固定に渡すための記述。
規則（先に書く・記述の読み方）: (i) 曜日ラベル週内シャッフルで 115 セル max|t| の帰無を在/外それぞれ 1000 回 → 16–16:55 金曜 t の p_fw(115)。
  (ii) 独立 4 窓・偶奇年・年別で 16–16:55 金曜 Δ。4/4 窓で Δ>0 ∧ t≥2 なら「前向き候補」と書く（PROMOTED ではない）。
  (iii) bid 人工物の検査: 16:00–16:55 を 5 分足 11 本で金曜 vs 基準（最後の 1〜2 本に集中なら終値の気配人工物を疑う）。
       週末 gap（金 16:55 → 日 18:05）と 平日 gap を比較: 金曜 16:55 の bid が人工的に高ければ週末 gap は平日より低いはず。
  (iv) 15:00–16:00 の外 −2.6 (t −2.2) との関係: 16–16:55 と 15–16 の相関（反転か）。
  (v) 金曜 16:00–16:55 の flat 率と |r| を基準と比べる（薄さ）。NFP 除外・年FE 併記。
入力: XAU_m5_close.npz のみ。seed 20261111。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
sys.argv = [sys.argv[0]]; os.environ["SYM"] = "XAU"
T0 = time.time(); rng = np.random.default_rng(20261111)
src = open(os.path.join(HERE, "c36_day_of_week.py"), encoding="utf-8").read()
head = src.split("# ---------------- 決着可能性")[0]
g = {"__file__": os.path.join(HERE, "c36_day_of_week.py"), "__name__": "c36_head"}; exec(compile(head, "c36_head", "exec"), g)
df = g["df"]; welch = g["welch"]; WD = g["WD"]; P_ALL = g["P_ALL"]; mod = g["mod"]; cal_ord = g["cal_ord"]; flat = g["flat"]
L = [f"# [REFUTE c36 補足 b] 金曜 16:00–16:55 ET の追試（事後・記述）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c36_friday_late_b.py)"]
def say(s=""): print(s, flush=True); L.append(s)
say("")
IN = (2010, 2020); OUT = (2021, 2026); WIN = {"在 2010-20": IN, "外 2021-26H1": OUT}
dfl = df[df.gap.notna()].copy()
def base_mask(d_): return d_.wd.isin([1, 2, 3]) & ~d_.posthol
# 5 分格子（0:00〜16:55 と 18:05, 19:00..23:55）
GR = {}
for m_ in sorted(set(list(range(0, 17 * 60, 5)) + [18 * 60 + 5] + list(range(19 * 60, 24 * 60, 60)))):
    mk = mod == m_; GR[m_] = dict(zip(cal_ord[mk].tolist(), P_ALL[mk].tolist()))
FL = {}
for m_ in range(16 * 60, 17 * 60, 5):
    mk = mod == m_; FL[m_] = dict(zip(cal_ord[mk].tolist(), flat[mk].tolist()))
def seg(o, m0, m1):
    p0 = GR[m0].get(o); p1 = GR[m1].get(o); return math.log(p1 / p0) * 1e4 if (p0 and p1) else np.nan
dfl["r16"] = [seg(o, 16 * 60, 16 * 60 + 55) for o in dfl.ord]
dfl["r15"] = [seg(o, 15 * 60, 16 * 60) for o in dfl.ord]
dfl["r14"] = [seg(o, 14 * 60, 16 * 60) for o in dfl.ord]
dfl["r12"] = [seg(o, 12 * 60, 16 * 60) for o in dfl.ord]
dfl = dfl[dfl.r16.notna()]
def dcell(d_, col):
    b = d_[base_mask(d_)][col]; a = d_[d_.wd == 4][col]; t, se = welch(a, b); return a.mean() - b.mean(), t, se, len(a)

say("## (ii) 16:00–16:55 金曜 − 基準（bp）: 窓別・独立 4 窓・偶奇年・年別・NFP 除外・年FE")
for lab, (y0, y1) in {"在 2010-20": IN, "外 2021-26H1": OUT, "近年 2024-26H1": (2024, 2026), "2010-14": (2010, 2014), "2015-20": (2015, 2020), "2021-23": (2021, 2023), "2024-26H1": (2024, 2026)}.items():
    d_ = dfl[(dfl.year >= y0) & (dfl.year <= y1)]; d16 = dcell(d_, "r16"); d12 = dcell(d_, "r12"); dn = dcell(d_[~d_.nfp], "r16")
    dfe = d_.assign(r16=d_.r16 - d_.groupby("year").r16.transform("mean")); dfe_ = dcell(dfe, "r16")
    say(f"- {lab} n 金 {d16[3]}: 16–16:55 Δ {d16[0]:+.1f}（t {d16[1]:+.2f}・MDE {2*d16[2]:.1f}）・NFP 除外 {dn[0]:+.1f}（t {dn[1]:+.2f}）・年FE {dfe_[0]:+.1f}（t {dfe_[1]:+.2f}） ｜ 12–16 Δ {d12[0]:+.1f}（t {d12[1]:+.2f}）")
for lab, m in {"偶数年": dfl.year % 2 == 0, "奇数年": dfl.year % 2 == 1}.items():
    d_ = dfl[m]; d16 = dcell(d_, "r16"); say(f"- {lab}（2010-26H1）: 16–16:55 Δ {d16[0]:+.1f}（t {d16[1]:+.2f}）")
yl = []
for y in range(2010, 2027):
    dy = dfl[dfl.year == y]
    if (dy.wd == 4).sum() < 20: continue
    d16 = dcell(dy, "r16"); yl.append(f"{y}:{d16[0]:+.1f}(t{d16[1]:.1f})")
say("- 年別: " + " ".join(yl) + f"・Δ>0 の年 {sum(1 for s in yl if '+' in s.split(':')[1][0])}/{len(yl)}")
for wn, w in WIN.items():
    d_ = dfl[(dfl.year >= w[0]) & (dfl.year <= w[1])]
    s = " ".join(f"{WD[d]}{dcell_w:+.1f}({t:+.1f})" for d, (dcell_w, t) in [(d, (lambda a, b: (a.mean() - b.mean(), welch(a, b)[0]))(d_[d_.wd == d].r16, d_[d_.wd.isin([0,1,2,3,4]) & (d_.wd != d) & ~d_.posthol].r16)) for d in range(5)])
    say(f"- {wn} 曜日別 16–16:55（各曜日 − 他 4 曜日）: {s}")

say("\n## (i) 115 セル（23 時間セル × 5 曜日）の週内シャッフル max|t|・1000 回 → 16–16:55 金曜 の p_fw(115)")
cells = [(18 * 60 + 5, 19 * 60, True)] + [(h * 60, (h + 1) * 60, True) for h in range(19, 23)] + [None] + [(h * 60, (h + 1) * 60, False) for h in range(0, 16)] + [(16 * 60, 16 * 60 + 55, False)]
def segp(o, c):
    if c is None: p0 = GR[23 * 60].get(o - 1); p1 = GR[0].get(o)
    else: p0 = GR[c[0]].get(o - 1 if c[2] else o); p1 = GR[c[1]].get(o - 1 if c[2] else o)
    return math.log(p1 / p0) * 1e4 if (p0 and p1) else np.nan
M = np.array([[segp(o, c) for c in cells] for o in dfl.ord.values])
def all_ts(M, wd, ph):
    out = np.empty((5, M.shape[1]))
    for w in range(5):
        if w in (1, 2, 3): ma = (wd == w) & ~ph; mb = np.isin(wd, [1, 2, 3]) & ~ph & (wd != w)
        else: ma = wd == w; mb = np.isin(wd, [1, 2, 3]) & ~ph
        A = M[ma]; B = M[mb]
        for c in range(M.shape[1]):
            x = A[:, c]; y = B[:, c]; x = x[~np.isnan(x)]; y = y[~np.isnan(y)]; out[w, c] = welch(x, y)[0]
    return out
for wn, w in WIN.items():
    m = ((dfl.year >= w[0]) & (dfl.year <= w[1])).values; d_ = dfl[m].reset_index(drop=True); Mw = M[m]
    wd = d_.wd.values; ph = d_.posthol.values; wk = d_.wk.values
    obs = all_ts(Mw, wd, ph); t16 = obs[4, -1]
    mx = np.empty(1000); tf = np.empty(1000)
    for i in range(1000):
        order = np.lexsort((rng.random(len(wd)), wk)); pw = wd[order]; ts_ = all_ts(Mw, pw, ph); mx[i] = np.abs(ts_).max(); tf[i] = ts_[4, -1]
    say(f"- {wn}: 観測 115 セル max|t| {np.abs(obs).max():.2f}（{'月火水木金'[int(np.abs(obs).argmax()//obs.shape[1])]}・セル {int(np.abs(obs).argmax()%obs.shape[1])}）・金曜 16–16:55 t {t16:+.2f} → p_fw(115) {(mx >= abs(t16)).mean():.3f}・帰無 max|t| 中央値 {np.median(mx):.2f}／95% {np.quantile(mx,.95):.2f}・片側 p_cell {(tf >= t16).mean():.3f}")
    say(f"    |t|≥3.1 のセル: " + " ".join(f"{'月火水木金'[w_]}c{c}:{obs[w_,c]:+.1f}" for w_ in range(5) for c in range(obs.shape[1]) if abs(obs[w_, c]) >= 3.1))

say("\n## (iii) 5 分足プロファイル 16:00→16:55（金曜 − 基準・bp・11 本）と 週末 gap vs 平日 gap")
for wn, w in WIN.items():
    d_ = dfl[(dfl.year >= w[0]) & (dfl.year <= w[1])]; a = d_[d_.wd == 4]; b = d_[base_mask(d_)]; s = []
    for m0 in range(16 * 60, 16 * 60 + 55, 5):
        x = np.array([seg(o, m0, m0 + 5) for o in a.ord]); y = np.array([seg(o, m0, m0 + 5) for o in b.ord]); x = x[~np.isnan(x)]; y = y[~np.isnan(y)]; t, _ = welch(x, y)
        s.append(f"{m0//60}:{m0%60:02d}:{x.mean()-y.mean():+.2f}({t:+.1f})")
    say(f"- {wn}: " + " ".join(s))
    x = np.array([seg(o, 16 * 60 + 45, 16 * 60 + 55) for o in a.ord]); y = np.array([seg(o, 16 * 60 + 45, 16 * 60 + 55) for o in b.ord]); x = x[~np.isnan(x)]; y = y[~np.isnan(y)]; t, _ = welch(x, y)
    x2 = np.array([seg(o, 16 * 60, 16 * 60 + 45) for o in a.ord]); y2 = np.array([seg(o, 16 * 60, 16 * 60 + 45) for o in b.ord]); x2 = x2[~np.isnan(x2)]; y2 = y2[~np.isnan(y2)]; t2, _ = welch(x2, y2)
    say(f"    16:00–16:45 Δ {x2.mean()-y2.mean():+.1f}（t {t2:+.2f}）／16:45–16:55 Δ {x.mean()-y.mean():+.1f}（t {t:+.2f}）")
    tg, _ = welch(a.gap, b.gap)
    # 金曜の gap 列は「前営業日→金曜」。週末 gap は翌月曜行の gap。
    mon = dfl[(dfl.year >= w[0]) & (dfl.year <= w[1]) & (dfl.wd == 0)]; tw, _ = welch(mon.gap, b.gap)
    say(f"    週末 gap（月曜行・金 16:55→日 18:05）{mon.gap.mean():+.1f} vs 平日 gap（基準）{b.gap.mean():+.1f}（Δ {mon.gap.mean()-b.gap.mean():+.1f}・t {tw:+.2f}）＝金曜 16:55 の bid が人工的に高ければ負のはず")
    # 金曜 16–16:55 → 週末 gap の相関（反転か）
    fr = a.set_index("ord"); mo = mon.set_index("ord"); j = [(o, o + 3) for o in fr.index if o + 3 in mo.index]
    x = np.array([fr.at[o, "r16"] for o, n in j]); y = np.array([mo.at[n, "gap"] for o, n in j]); xc = x - x.mean(); bta = (xc * (y - y.mean())).sum() / (xc ** 2).sum(); e = y - y.mean() - bta * xc; se = math.sqrt(((xc ** 2) * (e ** 2)).sum()) / (xc ** 2).sum()
    say(f"    金曜 16–16:55 → 週末 gap: β {bta:+.3f}（HC t {bta/se:+.2f}・n {len(x)}）；金曜 15–16 → 16–16:55: ρ {np.corrcoef(a.r15, a.r16)[0,1]:+.3f}・基準 {np.corrcoef(b.r15, b.r16)[0,1]:+.3f}")
    # 薄さ
    fa = np.mean([np.mean([FL[m_].get(o, True) for m_ in range(16 * 60, 17 * 60, 5)]) for o in a.ord]); fb = np.mean([np.mean([FL[m_].get(o, True) for m_ in range(16 * 60, 17 * 60, 5)]) for o in b.ord])
    say(f"    (v) 16:00–16:55 flat 率 金曜 {fa*100:.1f}% vs 基準 {fb*100:.1f}%・|r16| 中央値 金曜 {a.r16.abs().median():.1f} vs 基準 {b.r16.abs().median():.1f}・sd {a.r16.std():.1f} vs {b.r16.std():.1f}")

say(f"\n- 実行 {time.time()-T0:.1f} s")
open(os.path.join(DATA, "refute_c36_friday_late_b.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
