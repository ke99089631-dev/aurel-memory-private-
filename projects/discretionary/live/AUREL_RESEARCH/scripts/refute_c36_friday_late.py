"""
[REFUTE] 2026-11-11 反証レーン — 対象: cycle36 (06:50) の残存弱信号
  W1 知識 (1)「金曜の正は NY 午後 12:00–16:55 ET に局在（在 late Δ +7.8 bp・t 4.23）し 2010-14 → 24-26H1 で +11 → +5 → +5 → −7 と単調に消えた
     （late の在外差 t ≈2.6 ＝『消えた』が言える）」
  W2 次の枝 (c)「NY 午後は翌朝に反転する: 木→金 外 β −0.553 (t −3.39)・金→月は継続 (t +2.0)」（新仮説候補）
  W3 補足 b (3)「VIX が高い週ほど金曜 late が大きい（在 +7.9 t 2.06・外 +7.2 t 1.3）」
  W4 補足 b「late は 2013-20 でも立つ（t 3.5）＝ 2010-12 だけの事象ではない」
H_FRI null・H_MON null・US500 null・ゲート不通過は争わない（研究レーンの自己申告どおり）。

規則（数字を見る前に確定・判定 3 標的 R1/R2/R3・Bonferroni(3) 名目 |t| 2.39 併記・R4〜R6 は記述）:
  R0 再現: c36 の head を同じコードで exec し、在 金曜 late Δ +7.8／t 4.23・外 −0.6／t −0.23 が ±0.05 で一致すること。
  R1 窓選択の補正（主）: late は 3 成分 × 金/月 の 6 セルから数字を見て選ばれた。曜日ラベルを同じ週の中でシャッフル（2000 回）し
     「5 曜日 × 3 成分 = 15 セルの max|t|」の帰無分布で 在 金曜 late t 4.23 の p_fw(15) を出す。
     survived = p_fw(15) < 0.05 ∧ Bonferroni(15) 名目 |t| 2.94 以上。broken = p_fw(15) ≥ 0.10。他は inconclusive。
  R2 外れ値・分布: 在 金曜 late Δ を winsor 5%／trim 10%／中央値差（bootstrap 2000）／符号（late>0 の割合の 2 標本 z）／leave-one-year-out（11 通り）で再計算。
     survived = winsor 5% の t ≥ 2.39 ∧ LOYO の min t ≥ 2.0 ∧ 符号 z ≥ 2.0。broken = winsor t < 2.0 ∨ LOYO min t < 1.5。他は inconclusive。
  R3 「消えた」: (a) 分割年 b=2013..2024 の全てで DiD = Δ_late(2010..b−1) − Δ_late(b..2026H1) と t（Welch se の合成）を印字（2021 が選ばれた分割か）。
     (b) 年別 Δ_late_y（17 点）の重み付き回帰 slope（bp/年）と t・年クラスタ（等重み）の pre/post t。
     (c) 17 年を無作為に 11/6 に分けた 2000 分割で「在 t ≥ 2.39 ∧ 外 Δ ≤ 0」が出る割合＝時代順でない分割が『消えた』を何回出すか。
     survived = DiD(2021) t ≥ 2.0 ∧ slope t ≤ −2.0。broken = DiD(2021) t < 1.5 ∧ slope |t| < 1.5。他は inconclusive。
  R4（記述）: late を 12–14／14–16／16–16:55 ET に分け、さらに時間別 23 セル（前夜 18:05→19 … 16→16:55）の 金曜 − 基準 を在で印字（Bonferroni(23) 名目 |t| 3.1）。
     12:00 は『選ばれた境界』か＝金曜の超過が最大の連続帯を探す（事後・形の確認）。
  R5（記述・W2）: 5 曜日ペア全部（late(d) → 翌営業日 gap＋early）の β・HC t・Spearman ρ・winsor 5% β を在/外で印字（Bonferroni(5) 名目 |t| 2.58）。
     プラセボ: late(d) → 翌日 late、early(d) → 同日 late。研究レーンの前向き規則（在 t≤−2 ∧ 外 t≤−1.5）を既存データに当てて何ペア通るか。
  R6（記述・W3）: VIX 既知 三分位の 高−低 を 5 曜日の late 全部で印字（金曜だけか・ボラ地合いの全曜日ドリフトか）。
  コスト: 取引規則ではないが参考に 往復スプレッド（0.22 USD／価格）を bp で印字（在 +7.8 bp と比較）。
look-ahead: リターンのみ・VIX は前営業日 asof（c36b と同じ）。survivorship: 該当なし。D2: 窓別・16 年一括は使わず。seed 20261111。
入力: XAU_m5_close.npz・VIXCLS.csv（既存）のみ・scan 無し・MT5 無し・外部通信無し。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
sys.argv = [sys.argv[0]]; os.environ["SYM"] = "XAU"
T0 = time.time(); rng = np.random.default_rng(20261111)
src = open(os.path.join(HERE, "c36_day_of_week.py"), encoding="utf-8").read()
head = src.split("# ---------------- 決着可能性")[0]
g = {"__file__": os.path.join(HERE, "c36_day_of_week.py"), "__name__": "c36_head"}; exec(compile(head, "c36_head", "exec"), g)
df = g["df"]; welch = g["welch"]; WD = g["WD"]; P_ALL = g["P_ALL"]; mod = g["mod"]; cal_ord = g["cal_ord"]; BDAYS = g["BDAYS"]
L = [f"# [REFUTE c36] 金曜 late 窓・反転・VIX の反証 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c36_friday_late.py)"]
def say(s=""): print(s, flush=True); L.append(s)
say("")
IN = (2010, 2020); OUT = (2021, 2026); WIN = {"在 2010-20": IN, "外 2021-26H1": OUT}
def win(d_, w): return d_[(d_.year >= w[0]) & (d_.year <= w[1])]
def base_mask(d_): return d_.wd.isin([1, 2, 3]) & ~d_.posthol

# ---------------- R0 再現 ----------------
say("## R0 再現（c36 と同じ head・金曜 late Δ）")
for wn, w in WIN.items():
    d_ = win(df[df.gap.notna()], w); b = d_[base_mask(d_)]; a = d_[d_.wd == 4]
    t, se = welch(a.late, b.late); say(f"- {wn}: 金曜 late {a.late.mean():+.1f} vs 基準 {b.late.mean():+.1f} → Δ {a.late.mean()-b.late.mean():+.1f}（t {t:+.2f}・MDE {2*se:.1f}）n 金 {len(a)}／基準 {len(b)}")
c36_in = (7.8, 4.23)

# ---------------- R1 15 セルの family-wise ----------------
say("\n## R1 窓選択の補正: 曜日ラベル週内シャッフル 2000 回・5 曜日 × 3 成分 = 15 セル max|t|")
def cell_ts(r3, wd, ph):
    # r3: (n,3) gap/early/late; returns 15 t values
    out = []
    for w in range(5):
        if w in (1, 2, 3):
            ma = (wd == w) & ~ph; mb = np.isin(wd, [1, 2, 3]) & ~ph & (wd != w)
        else:
            ma = wd == w; mb = np.isin(wd, [1, 2, 3]) & ~ph
        for c in range(3):
            out.append(welch(r3[ma, c], r3[mb, c])[0])
    return np.array(out)
NREP = 2000
for wn, w in WIN.items():
    d_ = win(df[df.gap.notna()], w).sort_values(["wk", "ord"]).reset_index(drop=True)
    r3 = d_[["gap", "early", "late"]].values; wd = d_.wd.values; ph = d_.posthol.values; wk = d_.wk.values
    obs = cell_ts(r3, wd, ph); t_fl = obs[4 * 3 + 2]
    mx = np.empty(NREP); tfl = np.empty(NREP)
    for i in range(NREP):
        order = np.lexsort((rng.random(len(wd)), wk)); pw = wd[order]
        ts_ = cell_ts(r3, pw, ph); mx[i] = np.abs(ts_).max(); tfl[i] = ts_[14]
    say(f"- {wn}: 観測 15 セル max|t| {np.abs(obs).max():.2f}（{'月火水木金'[int(np.abs(obs).argmax()//3)]}・{['gap','early','late'][int(np.abs(obs).argmax()%3)]}）・金曜 late t {t_fl:+.2f} → "
        f"p_fw(15) {(mx >= abs(t_fl)).mean():.4f}・帰無 max|t| 中央値 {np.median(mx):.2f}／95% {np.quantile(mx, .95):.2f}・片側 p_cell {(tfl >= t_fl).mean():.4f}・Bonferroni(15) 名目 2.94")
    say("    15 セル t: " + " ".join(f"{'月火水木金'[k//3]}{['g','e','l'][k%3]}{obs[k]:+.1f}" for k in range(15)))
    if wn.startswith("在"): R1_p = (mx >= abs(t_fl)).mean(); R1_t = t_fl

# ---------------- R2 外れ値・分布 ----------------
say("\n## R2 外れ値・分布（在 金曜 late Δ）")
d_ = win(df[df.gap.notna()], IN); b = d_[base_mask(d_)].late.values; a = d_[d_.wd == 4].late.values
def wins(x, q): lo, hi = np.quantile(x, [q, 1 - q]); return np.clip(x, lo, hi)
allv = np.r_[a, b]
for q in (0.01, 0.05):
    lo, hi = np.quantile(allv, [q, 1 - q]); aw = np.clip(a, lo, hi); bw = np.clip(b, lo, hi); t, se = welch(aw, bw)
    say(f"- winsor {q*100:.0f}%（両群共通の分位 [{lo:+.0f},{hi:+.0f}]）: Δ {aw.mean()-bw.mean():+.1f}（t {t:+.2f}）")
    if q == 0.05: R2_w = t
def trim(x, p): x = np.sort(x); k = int(len(x) * p); return x[k:len(x) - k]
ta, tb = trim(a, 0.10), trim(b, 0.10); t, _ = welch(ta, tb); say(f"- trim 10%: Δ {ta.mean()-tb.mean():+.1f}（t {t:+.2f}）")
md = np.median(a) - np.median(b); bs = np.array([np.median(rng.choice(a, len(a))) - np.median(rng.choice(b, len(b))) for _ in range(2000)])
say(f"- 中央値差 {md:+.1f}（bootstrap se {bs.std():.1f}・t {md/bs.std():+.2f}）・金曜 中央値 {np.median(a):+.1f}／基準 {np.median(b):+.1f}")
pa, pb = (a > 0).mean(), (b > 0).mean(); pp = (np.r_[a > 0, b > 0]).mean(); z = (pa - pb) / math.sqrt(pp * (1 - pp) * (1 / len(a) + 1 / len(b)))
say(f"- 符号: late>0 の割合 金曜 {pa*100:.1f}% vs 基準 {pb*100:.1f}% → z {z:+.2f}"); R2_z = z
say(f"- 上位 5 金曜 late: {np.sort(a)[-5:].round(0).tolist()}・下位 5: {np.sort(a)[:5].round(0).tolist()}・金曜 sd {a.std():.0f} vs 基準 {b.std():.0f}")
loyo = []
for y in range(2010, 2021):
    dd = d_[d_.year != y]; t, _ = welch(dd[dd.wd == 4].late, dd[base_mask(dd)].late); loyo.append((y, dd[dd.wd == 4].late.mean() - dd[base_mask(dd)].late.mean(), t))
say("- leave-one-year-out: " + " ".join(f"除{y}:{dl:+.1f}(t{t:.2f})" for y, dl, t in loyo) + f" → min t {min(t for _,_,t in loyo):.2f}"); R2_loyo = min(t for _, _, t in loyo)
# 週クラスタ se（同じ週の金曜と基準は相関し得る）
wkd = d_.copy(); wkd["e"] = np.where(wkd.wd == 4, wkd.late, np.nan)
fri_w = d_[d_.wd == 4].groupby("wk").late.mean(); base_w = d_[base_mask(d_)].groupby("wk").late.mean(); j = fri_w.index.intersection(base_w.index)
dw = (fri_w[j] - base_w[j]).values; say(f"- 週ペア差（同週の金曜 − 同週の火水木平均・n {len(dw)}）: {dw.mean():+.1f}（t {dw.mean()/dw.std(ddof=1)*math.sqrt(len(dw)):+.2f}）")

# ---------------- R3 「消えた」 ----------------
say("\n## R3 「消えた」の検証")
def dlate(d_):
    b = d_[base_mask(d_)].late; a = d_[d_.wd == 4].late; t, se = welch(a, b); return a.mean() - b.mean(), se, t, len(a)
dfl = df[df.gap.notna()]
say("- (a) 分割年 b の DiD = Δ(2010..b−1) − Δ(b..2026H1)・t = DiD / sqrt(se²+se²):")
rows = []
for bb in range(2013, 2025):
    pre = dlate(dfl[(dfl.year >= 2010) & (dfl.year < bb)]); post = dlate(dfl[dfl.year >= bb])
    did = pre[0] - post[0]; tt = did / math.sqrt(pre[1] ** 2 + post[1] ** 2); rows.append((bb, pre[0], pre[2], post[0], post[2], did, tt))
say("    " + " ".join(f"b{bb}:pre{p:+.1f}(t{tp:.1f})/post{q:+.1f}(t{tq:.1f})→DiD{d:+.1f}(t{tt:.2f})" for bb, p, tp, q, tq, d, tt in rows))
R3_did_t = [r[6] for r in rows if r[0] == 2021][0]; R3_did = [r[5] for r in rows if r[0] == 2021][0]
say(f"    DiD(2021) {R3_did:+.1f}（t {R3_did_t:+.2f}）・12 分割中の順位 {sorted([r[6] for r in rows], reverse=True).index(R3_did_t)+1} 位・max t {max(r[6] for r in rows):.2f}（b{[r[0] for r in rows if r[6]==max(x[6] for x in rows)][0]}）")
yrs = [];
for y in range(2010, 2027):
    dy = dfl[dfl.year == y]
    if (dy.wd == 4).sum() < 20: continue
    dl, se, t, n = dlate(dy); yrs.append((y, dl, se, n))
Y = np.array([r[0] for r in yrs], float); D = np.array([r[1] for r in yrs]); S = np.array([r[2] for r in yrs])
say("- (b) 年別 late Δ: " + " ".join(f"{int(y)}:{d:+.1f}±{s:.1f}" for y, d, s in zip(Y, D, S)))
w_ = 1 / S ** 2; X = np.c_[np.ones_like(Y), Y - 2010]; W = np.diag(w_); beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ D); cov = np.linalg.inv(X.T @ W @ X)
res = D - X @ beta; chi2 = (res ** 2 * w_).sum(); say(f"    重み付き回帰 slope {beta[1]:+.2f} bp/年（t {beta[1]/math.sqrt(cov[1,1]):+.2f}）・切片 {beta[0]:+.1f}・残差 χ² {chi2:.1f}/df {len(Y)-2}（過分散 {chi2/(len(Y)-2):.2f}）")
R3_slope_t = beta[1] / math.sqrt(cov[1, 1])
pre = D[Y <= 2020]; post = D[Y >= 2021]; tt = (pre.mean() - post.mean()) / math.sqrt(pre.var(ddof=1) / len(pre) + post.var(ddof=1) / len(post))
say(f"    年クラスタ（等重み）pre 11 年 {pre.mean():+.1f}（sd {pre.std(ddof=1):.1f}）vs post 6 年 {post.mean():+.1f}（sd {post.std(ddof=1):.1f}）→ t {tt:+.2f}；post 6 年中 Δ≤0 は {(post<=0).sum()}")
# 2 年窓
say("    2 年窓: " + " ".join(f"{y0}-{str(y0+1)[2:]}:{dlate(dfl[(dfl.year>=y0)&(dfl.year<=y0+1)])[0]:+.1f}(t{dlate(dfl[(dfl.year>=y0)&(dfl.year<=y0+1)])[2]:.1f})" for y0 in range(2010, 2026, 2)))
# (c) 無作為 11/6 分割
yl = [int(y) for y in Y]; cnt = 0; cnt_strict = 0; tin = []; dout = []
by_year = {y: dfl[dfl.year == y] for y in yl}
for i in range(2000):
    sel = rng.choice(yl, 11, replace=False); din = pd.concat([by_year[y] for y in sel]); dout_ = pd.concat([by_year[y] for y in yl if y not in sel])
    a_, b_ = dlate(din), dlate(dout_); tin.append(a_[2]); dout.append(b_[0])
    if a_[2] >= 2.39 and b_[0] <= 0: cnt += 1
    if a_[2] >= 2.39 and b_[2] <= -1.5: cnt_strict += 1
tin = np.array(tin); dout = np.array(dout)
say(f"- (c) 無作為 11/6 年分割 2000 回: 在 t ≥2.39 の割合 {(tin>=2.39).mean()*100:.1f}%・外 Δ ≤0 の割合 {(dout<=0).mean()*100:.1f}%・両方 {cnt/20:.1f}%・（在 t≥2.39 ∧ 外 t≤−1.5）{cnt_strict/20:.1f}%；時代順の外 Δ {dlate(win(dfl, OUT))[0]:+.1f} は無作為外 Δ の下位 {(dout<=dlate(win(dfl, OUT))[0]).mean()*100:.1f}% 点")

# ---------------- R4 窓の形（記述） ----------------
say("\n## R4 late 窓の形（記述・在）: 12–14／14–16／16–16:55 と 時間別 23 セル（Bonferroni(23) 名目 |t| 3.1）")
GR = {}
for m_ in list(range(0, 17 * 60, 60)) + [16 * 60 + 55, 18 * 60 + 5] + list(range(19 * 60, 24 * 60, 60)) + [14 * 60]:
    mk = mod == m_; GR[m_] = dict(zip(cal_ord[mk].tolist(), P_ALL[mk].tolist()))
def seg(o, m0, m1, prev_day=False):
    p0 = GR[m0].get(o - 1 if prev_day else o); p1 = GR[m1].get(o - 1 if prev_day and m1 >= 18 * 60 else o)
    return math.log(p1 / p0) * 1e4 if (p0 and p1) else np.nan
cells = [("18:05→19", (18 * 60 + 5, 19 * 60, True))] + [(f"{h}→{h+1}", (h * 60, (h + 1) * 60, True)) for h in range(19, 23)] + [("23→00", None)] + \
        [(f"{h:02d}→{h+1:02d}", (h * 60, (h + 1) * 60, False)) for h in range(0, 16)] + [("16→16:55", (16 * 60, 16 * 60 + 55, False))]
rows = {}
for o in dfl.ord.values:
    v = []
    for lab, sp in cells:
        if sp is None:
            p0 = GR[23 * 60].get(o - 1); p1 = GR[0].get(o); v.append(math.log(p1 / p0) * 1e4 if (p0 and p1) else np.nan)
        else: v.append(seg(o, sp[0], sp[1], sp[2]))
    rows[o] = v
H = pd.DataFrame.from_dict(rows, orient="index", columns=[c[0] for c in cells]); H["wd"] = dfl.set_index("ord").wd; H["ph"] = dfl.set_index("ord").posthol; H["year"] = dfl.set_index("ord").year
for wn, w in WIN.items():
    h_ = H[(H.year >= w[0]) & (H.year <= w[1])]; bm = h_.wd.isin([1, 2, 3]) & ~h_.ph; a = h_[h_.wd == 4]; b = h_[bm]
    s = []
    for lab in H.columns[:-3]:
        x = a[lab].dropna(); y = b[lab].dropna(); t, _ = welch(x, y); s.append((lab, x.mean() - y.mean(), t))
    say(f"- {wn} 金曜 − 基準 時間別: " + " ".join(f"{lab}:{d:+.1f}({t:+.1f})" for lab, d, t in s))
    # 3 分割
    for lab, (m0, m1) in {"12–14": (12 * 60, 14 * 60), "14–16": (14 * 60, 16 * 60), "16–16:55": (16 * 60, 16 * 60 + 55)}.items():
        x = np.array([seg(o, m0, m1) for o in a.index]); y = np.array([seg(o, m0, m1) for o in b.index]); x = x[~np.isnan(x)]; y = y[~np.isnan(y)]; t, se = welch(x, y)
        say(f"    {lab}: 金曜 {x.mean():+.1f} vs 基準 {y.mean():+.1f} → Δ {x.mean()-y.mean():+.1f}（t {t:+.2f}・MDE {2*se:.1f}）")
    # 最大連続帯（在のみ・日中 00→16:55 の 17 セル）
    if wn.startswith("在"):
        dv = np.array([d for lab, d, t in s]); labs = [lab for lab, d, t in s]; best = (None, -1e9)
        for i in range(len(dv)):
            for j in range(i, len(dv)):
                sm = dv[i:j + 1].sum()
                if sm > best[1]: best = ((i, j), sm)
        say(f"    金曜超過の最大連続帯（事後）: {labs[best[0][0]]} 〜 {labs[best[0][1]]} 合計 {best[1]:+.1f} bp（12:00→16:55 の合計 {dv[-5:].sum():+.1f}）")

# ---------------- R5 反転（W2・5 ペア） ----------------
say("\n## R5 NY 午後 → 翌朝の反転: 5 曜日ペア全部（late(d) → 翌営業日 gap＋early）・Bonferroni(5) 名目 |t| 2.58")
dfo = df[df.gap.notna()].set_index("ord")
ords = np.array(sorted(dfo.index)); nxt = {ords[i]: ords[i + 1] for i in range(len(ords) - 1)}
def hc_beta(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); xc = x - x.mean(); b = (xc * (y - y.mean())).sum() / (xc ** 2).sum(); e = y - y.mean() - b * xc
    se = math.sqrt(((xc ** 2) * (e ** 2)).sum()) / (xc ** 2).sum(); return b, b / se
def spear(x, y): return pd.Series(x).corr(pd.Series(y), method="spearman")
R5 = {}
for wn, w in WIN.items():
    s = []; pooled_x = []; pooled_y = []
    for d in range(5):
        pr = [(o, nxt[o]) for o in ords if o in nxt and dfo.at[o, "wd"] == d and w[0] <= dfo.at[o, "year"] <= w[1]]
        pr = [(o, n) for o, n in pr if (dfo.at[n, "wd"] == (d + 1) % 5) and (n - o) <= (3 if d == 4 else 1)]  # 連続営業日のみ（休日跨ぎ除外）
        x = np.array([dfo.at[o, "late"] for o, n in pr]); y = np.array([dfo.at[n, "gap"] + dfo.at[n, "early"] for o, n in pr])
        b, t = hc_beta(x, y); rho = spear(x, y); lo, hi = np.quantile(x, [.05, .95]); bw, tw = hc_beta(np.clip(x, lo, hi), y)
        pl = np.array([dfo.at[n, "late"] for o, n in pr]); bp_, tp_ = hc_beta(x, pl)
        s.append(f"{WD[d]}→{WD[(d+1)%5]} n{len(x)} β{b:+.3f}(t{t:+.2f}) ρs{rho:+.3f} winsβ{bw:+.3f}(t{tw:+.2f}) ｜ 翌late β{bp_:+.3f}(t{tp_:+.1f})")
        R5[(wn, d)] = (b, t); pooled_x.append(x); pooled_y.append(y)
    say(f"- {wn}:\n    " + "\n    ".join(s))
    x = np.concatenate(pooled_x); y = np.concatenate(pooled_y); b, t = hc_beta(x, y); say(f"    5 ペア合算 n{len(x)} β {b:+.3f}（t {t:+.2f}）")
    # 同日 early → late（c19 の RW 対照）
    d_ = win(df[df.gap.notna()], w); b2, t2 = hc_beta(d_.early, d_.late); say(f"    対照 同日 early → late: β {b2:+.3f}（t {t2:+.2f}）")
passes = [d for d in range(5) if R5[("在 2010-20", d)][1] <= -2 and R5[("外 2021-26H1", d)][1] <= -1.5 and R5[("在 2010-20", d)][0] < 0 and R5[("外 2021-26H1", d)][0] < 0]
say(f"- 研究レーンの前向き規則（β<0・在 t≤−2 ∧ 外 t≤−1.5）を既存データに当てると通るペア: {[WD[d]+'→'+WD[(d+1)%5] for d in passes] or 'なし'}；木→金 在 t {R5[('在 2010-20',3)][1]:+.2f}・外 t {R5[('外 2021-26H1',3)][1]:+.2f}")

# ---------------- R6 VIX 三分位（W3・全曜日） ----------------
say("\n## R6 VIX 既知 三分位 高−低（late・5 曜日全部・在で閾値）")
vix = pd.read_csv(os.path.join(DATA, "macro", "VIXCLS.csv")); vix.columns = ["date", "v"]; vix["v"] = pd.to_numeric(vix.v, errors="coerce"); vix = vix.dropna()
vix["ord"] = pd.to_datetime(vix.date).map(lambda x: x.toordinal()); vmap = dict(zip(vix.ord, vix.v)); vo = np.array(sorted(vmap))
def vix_known(o):
    i = np.searchsorted(vo, o - 1, side="right") - 1; return vmap[vo[i]] if i >= 0 and o - 1 - vo[i] <= 7 else np.nan
dv = df[df.late.notna()].copy(); dv["vk"] = [vix_known(int(o)) for o in dv.ord]; dv = dv[dv.vk.notna()]
q1, q2 = dv[(dv.year <= 2020) & (dv.wd == 4)].vk.quantile([1 / 3, 2 / 3]); say(f"- 閾値（在 金曜）VIX {q1:.1f}／{q2:.1f}")
for wn, w in WIN.items():
    s = []
    for d in range(5):
        f_ = win(dv[dv.wd == d], w); lo = f_[f_.vk < q1].late; hi = f_[f_.vk >= q2].late; t, se = welch(hi, lo) if len(lo) > 5 and len(hi) > 5 else (np.nan, np.nan)
        s.append(f"{WD[d]} 高−低 {hi.mean()-lo.mean():+.1f}(t{t:+.2f}・n{len(lo)}/{len(hi)})")
    say(f"- {wn}: " + " ｜ ".join(s))
    f_ = win(dv, w); lo = f_[f_.vk < q1].late; hi = f_[f_.vk >= q2].late; t, _ = welch(hi, lo); say(f"    全曜日 late 高−低 {hi.mean()-lo.mean():+.1f}（t {t:+.2f}）")

# ---------------- コスト参考 ----------------
d_ = win(df, IN); px = P_ALL[(cal_ord >= dt.date(2010, 1, 1).toordinal()) & (cal_ord <= dt.date(2020, 12, 31).toordinal())].mean()
say(f"\n- コスト参考: 往復スプレッド 0.22 USD ／ 在 平均価格 {px:.0f} = {0.22/px*1e4:.1f} bp（実射 ask 0.22 を往復 2 回なら {2*0.22/px*1e4:.1f} bp）vs 在 金曜 late Δ +7.8 bp／外 −0.6")

# ---------------- 判定 ----------------
say("\n## 判定（docstring の規則）")
v1 = "survived" if (R1_p < 0.05 and abs(R1_t) >= 2.94) else ("broken" if R1_p >= 0.10 else "inconclusive")
say(f"- R1 窓選択: p_fw(15) {R1_p:.4f}・t {R1_t:+.2f} → **{v1}**")
v2 = "survived" if (R2_w >= 2.39 and R2_loyo >= 2.0 and R2_z >= 2.0) else ("broken" if (R2_w < 2.0 or R2_loyo < 1.5) else "inconclusive")
say(f"- R2 外れ値: winsor5% t {R2_w:+.2f}・LOYO min t {R2_loyo:.2f}・符号 z {R2_z:+.2f} → **{v2}**")
v3 = "survived" if (R3_did_t >= 2.0 and R3_slope_t <= -2.0) else ("broken" if (R3_did_t < 1.5 and abs(R3_slope_t) < 1.5) else "inconclusive")
say(f"- R3 消えた: DiD(2021) t {R3_did_t:+.2f}・年 slope t {R3_slope_t:+.2f} → **{v3}**")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(os.path.join(DATA, "refute_c36_friday_late.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
