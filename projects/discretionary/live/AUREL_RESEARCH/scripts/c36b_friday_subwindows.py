"""
[cycle36b 研究レーン] 2026-11-11 — 補足（事後・記述・判定に不使用）
c36 の在 金曜 +13.8 bp/日（t 2.83・late 12:00–16:55 ET に局在 t 4.23）が外で消えた（+1.4・t 0.17）ので、
(1) 独立 4 窓 2010-14／2015-20／2021-23／2024-26H1 で 金曜 Δ・金曜 late Δ を印字し「いつ消えたか」を見る（年別は c36 に有り）。
(2) 機構の整合: 週末保険なら「金曜 late の買い」は事象が無ければ週明けに返る → 金曜 late と 翌週末 gap＋月曜 early の相関（在・外）。
    符号が負（反転）なら保険の買い戻し型、0 なら別物。
(3) VIX 既知（前日 FRED 値・avail 規則）で金曜 late を三分位に分ける（恐怖が高い週ほど週末保険が大きいか）＝事後 1 セル・記述。
入力: c36 と同じ npz・暦。VIXCLS.csv。seed 20261111。数秒。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
sys.argv = [sys.argv[0]]; os.environ["SYM"] = "XAU"
T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
# c36 の前半（暦・df）を再利用するため同じコードを exec（OUT 書き込みは行わない）
src = open(os.path.join(HERE, "c36_day_of_week.py"), encoding="utf-8").read()
head = src.split("# ---------------- 決着可能性")[0]
g = {"__file__": os.path.join(HERE, "c36_day_of_week.py"), "__name__": "c36_head"}; exec(compile(head, "c36_head", "exec"), g)
df = g["df"]; welch = g["welch"]; WD = g["WD"]
L = [f"# [cycle36b] 金曜効果の補足（独立窓・反転・VIX）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c36b_friday_subwindows.py)"]
say("")
# (1) 独立 4 窓
say("## (1) 独立 4 窓: 金曜 Δ（セッション）・金曜 late Δ・金曜 early Δ（bp/日・基準 = 火水木・休日明け除外）")
for lab, (y0, y1) in {"2010-14": (2010, 2014), "2015-20": (2015, 2020), "2021-23": (2021, 2023), "2024-26H1": (2024, 2026)}.items():
    d_ = df[(df.year >= y0) & (df.year <= y1) & df.gap.notna()]
    base = d_[d_.wd.isin([1, 2, 3]) & ~d_.posthol]; a = d_[d_.wd == 4]; an = a[~a.nfp]
    s = []
    for comp in ("r", "late", "early", "gap"):
        t, se = welch(a[comp], base[comp]); s.append(f"{comp} Δ {a[comp].mean()-base[comp].mean():+.1f}（t {t:+.2f}・MDE {2*se:.1f}）")
    t, _ = welch(an.late, base.late)
    say(f"- {lab} n 金 {len(a)}: " + " ｜ ".join(s) + f" ｜ NFP 除外 late Δ {an.late.mean()-base.late.mean():+.1f}（t {t:+.2f}）")
# 2010-12 vs 2013-20（事後・年別の形から）
for lab, (y0, y1) in {"2010-12": (2010, 2012), "2013-20": (2013, 2020)}.items():
    d_ = df[(df.year >= y0) & (df.year <= y1) & df.gap.notna()]
    base = d_[d_.wd.isin([1, 2, 3]) & ~d_.posthol]; a = d_[d_.wd == 4]
    t, se = welch(a.r, base.r); tl, sel = welch(a.late, base.late)
    say(f"- {lab}（事後分割）n 金 {len(a)}: r Δ {a.r.mean()-base.r.mean():+.1f}（t {t:+.2f}・MDE {2*se:.1f}）・late Δ {a.late.mean()-base.late.mean():+.1f}（t {tl:+.2f}）")

# (2) 反転: 金曜 late → 翌週末 gap + 月曜 early
say("\n## (2) 金曜 late の買いは週明けに返るか: corr(金曜 late, 翌 月曜 gap＋early)・β（bp/bp）")
fri = df[(df.wd == 4) & df.late.notna()][["ord", "year", "late", "r"]].rename(columns={"late": "fl", "r": "fr"})
mon = df[(df.wd == 0) & df.gap.notna()][["ord", "year", "gap", "early", "late", "r"]].rename(columns={"gap": "mg", "early": "me", "late": "ml", "r": "mr"})
mon["ord_fri"] = mon.ord - 3
pair = fri.merge(mon, left_on="ord", right_on="ord_fri", suffixes=("", "_m"))
pair["wk_end"] = pair.mg + pair.me
for lab, (y0, y1) in {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026)}.items():
    p = pair[(pair.year >= y0) & (pair.year <= y1)]
    for ycol, yl in [("mg", "週末 gap"), ("wk_end", "gap＋月曜 early"), ("mr", "月曜セッション")]:
        x = p.fl.values; y = p[ycol].values; b = np.cov(x, y)[0, 1] / x.var(ddof=1); rho = np.corrcoef(x, y)[0, 1]
        se = math.sqrt((y.var(ddof=1) / x.var(ddof=1) * (1 - rho ** 2)) / (len(x) - 2))
        say(f"- {lab} n {len(p)}: 金曜 late → {yl}: ρ {rho:+.3f}・β {b:+.3f}（t {b/se:+.2f}）")
    # 対照: 木曜 late → 金曜 gap+early（平日の同じ形）
    thu = df[(df.wd == 3) & df.late.notna()][["ord", "year", "late"]].rename(columns={"late": "tl"})
    fr2 = df[(df.wd == 4) & df.gap.notna()][["ord", "gap", "early"]]; fr2["ord_thu"] = fr2.ord - 1
    pc = thu.merge(fr2, left_on="ord", right_on="ord_thu"); pc = pc[(pc.year >= y0) & (pc.year <= y1)]
    x = pc.tl.values; y = (pc.gap + pc.early).values; b = np.cov(x, y)[0, 1] / x.var(ddof=1); rho = np.corrcoef(x, y)[0, 1]
    se = math.sqrt((y.var(ddof=1) / x.var(ddof=1) * (1 - rho ** 2)) / (len(x) - 2))
    say(f"    対照（木曜 late → 金曜 gap＋early）n {len(pc)}: ρ {rho:+.3f}・β {b:+.3f}（t {b/se:+.2f}）")

# (3) VIX 既知（前日値）三分位
say("\n## (3) VIX 既知（FRED・前営業日の値を asof）で金曜 late を三分位（在で閾値・記述）")
vix = pd.read_csv(os.path.join(DATA, "macro", "VIXCLS.csv")); vix.columns = ["date", "v"]
vix["v"] = pd.to_numeric(vix.v, errors="coerce"); vix = vix.dropna(); vix["ord"] = pd.to_datetime(vix.date).map(lambda x: x.toordinal())
vmap = dict(zip(vix.ord, vix.v)); vo = np.array(sorted(vmap))
def vix_known(o):  # 前営業日（暦日 o−1 以前）の VIX 終値
    i = np.searchsorted(vo, o - 1, side="right") - 1
    return vmap[vo[i]] if i >= 0 and o - 1 - vo[i] <= 7 else np.nan
fr = df[(df.wd == 4) & df.late.notna()].copy(); fr["vk"] = [vix_known(int(o)) for o in fr.ord]
fr = fr[fr.vk.notna()]
q1, q2 = fr[(fr.year <= 2020)].vk.quantile([1 / 3, 2 / 3])
say(f"- 在の三分位閾値 VIX {q1:.1f}／{q2:.1f}")
for lab, (y0, y1) in {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026)}.items():
    f_ = fr[(fr.year >= y0) & (fr.year <= y1)]
    lo = f_[f_.vk < q1]; mid = f_[(f_.vk >= q1) & (f_.vk < q2)]; hi = f_[f_.vk >= q2]
    t, se = welch(hi.late, lo.late)
    say(f"- {lab}: 金曜 late 低 {lo.late.mean():+.1f}（n {len(lo)}）／中 {mid.late.mean():+.1f}（{len(mid)}）／高 {hi.late.mean():+.1f}（{len(hi)}）→ 高−低 {hi.late.mean()-lo.late.mean():+.1f}（t {t:+.2f}・MDE {2*se:.1f}）")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(os.path.join(DATA, "c36b_friday_subwindows.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
