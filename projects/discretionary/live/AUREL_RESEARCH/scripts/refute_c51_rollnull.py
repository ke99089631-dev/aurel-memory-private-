"""
[REFUTE c51] 2026-11-19 — 反証レーン。対象 = cycle51 (00:40) の**生き残った正の主張**。

c51 の判定は H_ROLL null・H_REV null（＝主セルに壊す余地なし）・PROMOTED.md は空。
よって壊しに行くのは、c51 が null の副産物として**肯定形で登記した 3 つ**＝今後のサイクルに伝播するもの:

  K5【道具】知識(5)・枝(d)「月パリティ対照は曜日に無差別（T vs C_A = 20/20/20/20/20）＝c31 の TOM が
      苦しんだ曜日組成の罠を自動で避ける → 月央の制度日付の対照設計として DATA_MAP §6 に再利用登録」
  K4【方法論 69】知識(4)・枝(c)「機械的フローの事象研究は価格ドリフトより先に執行窓の**ボラ比**を印字し、
      ≤1 なら『フローが見えない市場で圧力を探している』＝null の読みを『経路の否定』に限定する」
      （c51 は |PRE60| 比 在 1.019／外 0.933／近年 0.743 を「ロールが居る痕跡が無い」と読んだ）
  R1【多重検定の会計】「約 40 セルで名目 |t|≥2 は 4 本＝期待 2 本・符号も揃わない」で
      在 SET30 +3.26 (t +2.55)／在 DAY −15.24 (−2.04)／BD10-14 −3.69 (−2.20)／ET10 時 −2.96 を棄却した会計。
  R2【null の強さ】「在 MDE 3.39 bp・外 4.97 bp/時」＝Welch iid se の 2 倍。この MDE が
      「GC 当限 M5 の価値はスプレッド次元にだけある／スポット経路は否定された」という**取得優先度の結論**を支えている。
      se が小さすぎれば null は「無い」でなく「測れていない」に落ちる。

事前固定（数字を見る前に確定・本 docstring が正本・seed 20261119）:

  データ = c51 と同一（data/macro/XAU_m5_close.npz・US500_m5_close.npz・bid・ET 格子・端点 flat2 除外）。
  追加列 = FIRST30（12:30→13:00 ET）＝PRE60 の前半（SET30 との入れ子を測るため）。
  窓期 = 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 窓別・16 年一括を edge 判定に使わない）。

  A0 複製: c51 の PRE60／POST60／SET30／DAY／|PRE60| 比を 2 桁一致で再現。外れたら以降は無効。

  A1 → BREAK-K5（道具の一般性）: BD 帯ごとに曜日組成を奇数月 vs 偶数月で出す。
      BREAK-K5 = 次のどちらかが成り立つとき K5 は「一般の道具」として **broken**:
        (a) c51 のプラセボ ② で使った 5 帯のいずれかで、奇数−偶数の曜日シェア差が **いずれかの曜日で ≥5 pt**、または
        (b) 20/20/20/20/20 が「月パリティ」の性質でなく「**帯幅がちょうど 5 営業日**」の機械的帰結である
            （検定: 5 営業日帯 BD5-9／10-14／15-19 は一様、4 営業日帯 BD1-4／20-23 は一様でない、を印字）。
      さらに偏りの**実害**を bp で予算化: bias = Σ_w (p_T(w) − p_C(w))·μ_PRE60(w)。|bias| ≥1 bp の帯は交絡。

  A2 → BREAK-K4（ボラ比という道具の検出力）: |PRE60| 中央値比 T/C_A の day-level ブートストラップ（5000・seed 固定）で 95% CI。
      BREAK-K4 = CI の半幅 ≥ 0.05（±5%）のとき、「比 1.02 ＝ フローが居ない」は証拠力を持たない＝規則は
        「比 ± CI を印字し、検出可能な最小フロー倍率を併記する」へ**改訂必須＝broken as written**。
      併せて陽性対照: T 日の PRE60 を k 倍（k=1.05,1.1,1.2,1.3,1.5）して、比の 95% CI が 1 を外す最小 k を印字
        （＝このテストが検出できる最小のボラ増幅）。

  A3 → BREAK-R1（セル独立性）: (i) PRE60 = FIRST30 + SET30 の分解を印字。
        (ii) 記述 family（PRE60/SET30/FIRST30/POST60/DAY + ET 24 窓）の相関行列から
             Cheverud–Nyholt の実効検定数 M_eff = 1 + (M−1)(1 − var(λ)/M) を計算。
        BREAK-R1 = 「名目 |t|≥2 が 4 本 / 約 40 セル ＝ 期待 2 本」の会計が、実効検定数または
          入れ子構造（SET30 ⊂ PRE60 ⊂ DAY・同一日）によって **±50% 以上ずれる**とき broken（どちら向きかを明記）。

  A4 → BREAK-R2（null の推論妥当性）: 月パリティのラベルを**月単位ブロック置換**（year-month を 1 ブロックとし、
        各年で 6 ブロックを T に割り当て直す・5000 draw）して Δ_PRE60 の帰無分布を作る。
      BREAK-R2 = perm_sd > 1.25 × Welch_se のとき、c51 の MDE（在 3.39／外 4.97）は過小＝null は
        宣言より弱い → 「スポット経路は 3〜5 bp/時 以上の圧力なし」は「〜 perm_MDE 以上」に後退（broken）。
      併せて主セル・SET30 セルの置換 two-sided p を印字（iid t に依らない p）。

  A5 プラセボ（処置定義そのもの・c51 未実施）: 12 か月から 6 か月を選ぶ 924 通りの分割すべてで
        T = 選択月 ∧ BD5-9／C = 非選択月 ∧ BD5-9 の Welch t を計算し、**実際の奇数月分割の順位**を出す。
      読み: 順位が上位 5% なら「奇数/偶数の分割は特別」＝c51 の「格子に構造なし」に反する弱信号（逆符号だが要記録）。
        中位なら null は補強。これは c51 の時刻 family（sd≈1 の目分量）より正しい family。

  A6 データ衛生・look-ahead: (i) 端点 flat 除外の T/C_A 非対称（495→492 / 495→493）を年別に印字。
        (ii) **早引け（13:00 ET 終了）日**の一覧と BD 位置・月パリティ（7/3・感謝祭翌日・12/24 は月パリティに偏る）。
             BD5-9 に落ちる早引けが T 側にだけあれば 12:30→13:30 窓は構造的に欠ける。
        (iii) 12:30／13:30 スロットの flat 率を T/C_A 別。

  A7 LOYO（在 +3.20 の年集中・コスト倍）: 在の主セルを 1 年抜きで 11 回・符号と |t| の振れ。
        ゲート ㉛ は **コスト倍**（ft = 0.2/risk）で再計算し、c51 の「決着不能」が費用側に動くかを見る。

  予定する自己反証: (1) A5 の 924 family は月が 12 個しかないので分割どうしが強く重複＝独立な 924 検定ではない
        （順位は保守的に読む）。(2) A2 の「検出可能な最小 k」は**乗法的**増幅のモデルであり、ロールが
        平均回帰的な圧力＋戻しなら |r| 中央値は上がらない形もある＝ボラ比の低検出力は K4 の規則を
        壊すが「ロールが居る」ことの証拠にはならない。(3) 置換検定は月パリティという**固定暦**を壊すので、
        もし真の交絡が「暦そのもの」（季節性）なら置換 sd は過大になりうる＝BREAK-R2 は保守側。

  読取専用: 発注なし・本番編集なし・プロセス/schtask/MT5 接触なし・外部通信なし・プロップ参照なし。
  書き込みは AUREL_RESEARCH/scripts/ と data/ と findings/ のみ。
"""
import os, sys, json, math, time, datetime as dt, itertools
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "refute_c51_rollnull_result.md")
rng = np.random.default_rng(20261119); T0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c51] 商品指数ロール null の“生き残った正の主張”を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c51_rollnull.py)")

# ---------------- 暦（c51/c30/c31 と同一コード） ----------------
def easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, month, day)
def nth_weekday(y, m, wd, n):
    d = dt.date(y, m, 1); return d + dt.timedelta(days=(wd - d.weekday()) % 7 + 7 * (n - 1))
def last_weekday(y, m, wd):
    d = dt.date(y, 12, 31) if m == 12 else dt.date(y, m + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)
def observed(d, sat_to_fri=True):
    if d.weekday() == 5: return d - dt.timedelta(days=1) if sat_to_fri else None
    if d.weekday() == 6: return d + dt.timedelta(days=1)
    return d
HOL = set()
for y in range(2009, 2028):
    for h in [observed(dt.date(y, 1, 1), sat_to_fri=False), nth_weekday(y, 1, 0, 3), nth_weekday(y, 2, 0, 3),
              easter(y) - dt.timedelta(days=2), last_weekday(y, 5, 0), observed(dt.date(y, 7, 4)),
              nth_weekday(y, 9, 0, 1), nth_weekday(y, 11, 3, 4), observed(dt.date(y, 12, 25))] + \
             ([observed(dt.date(y, 6, 19))] if y >= 2022 else []):
        if h is not None: HOL.add(h)
# 早引け（CME 金属 13:00 ET 近辺で終わる日・A6(ii) 用・規則で生成）: 7/3（7/4 が平日のとき）・感謝祭翌日・12/24
HALF = set()
for y in range(2010, 2027):
    j4 = dt.date(y, 7, 4)
    if j4.weekday() < 5 and j4 - dt.timedelta(days=1) not in HOL and (j4 - dt.timedelta(days=1)).weekday() < 5:
        HALF.add(j4 - dt.timedelta(days=1))
    HALF.add(nth_weekday(y, 11, 3, 4) + dt.timedelta(days=1))      # 感謝祭翌日（金）
    d = dt.date(y, 12, 24)
    if d.weekday() < 5: HALF.add(d)
d0 = dt.date(2009, 11, 1); d1 = dt.date(2026, 12, 31)
ALLD = [d0 + dt.timedelta(days=i) for i in range((d1 - d0).days + 1)]
BDAYS = [d for d in ALLD if d.weekday() < 5 and d not in HOL]
BD = {}; NBD = {}
for (y, m) in sorted({(d.year, d.month) for d in BDAYS}):
    bm = [d for d in BDAYS if d.year == y and d.month == m]
    for j, d in enumerate(bm): BD[d.toordinal()] = j + 1
    NBD[(y, m)] = len(bm)
GSCI_MONTHS = {1, 3, 5, 7, 9, 11}; GSCI_BD = (5, 9)

# ---------------- 価格格子（c51 と同一） ----------------
def load_grid(sym):
    z = np.load(os.path.join(DATA, "macro", f"{sym}_m5_close.npz")); TS = z["ts"].astype(np.int64); P = z["close"].astype(float)
    flat1 = np.r_[True, P[1:] == P[:-1]]; flat2 = flat1 & np.r_[True, flat1[:-1]]
    et = pd.to_datetime(TS, unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
    day = et.normalize().values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
    slot = (et.hour * 12 + et.minute // 5).values
    days = np.unique(day); di = {o: i for i, o in enumerate(days.tolist())}
    G = np.full((len(days), 288), np.nan); F = np.ones((len(days), 288), bool)
    rows = np.array([di[o] for o in day.tolist()])
    G[rows, slot] = np.log(P); F[rows, slot] = flat2
    sess = ((et + pd.Timedelta(hours=6)).values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal())
    keep = ~flat1; so = sess[keep]; pc = P[keep]
    u, li = np.unique(so[::-1], return_index=True); li = len(so) - 1 - li
    cbd = dict(zip(u.tolist(), pc[li].tolist()))
    say(f"- {sym} npz {len(TS)} 本・flat {flat1.mean()*100:.1f}%・日 {len(days)}")
    return days, di, G, F, cbd

def win(G, F, di, o, s0, s1):
    i = di.get(o)
    if i is None: return np.nan
    if F[i, s0] or F[i, s1] or not (np.isfinite(G[i, s0]) and np.isfinite(G[i, s1])): return np.nan
    return (G[i, s1] - G[i, s0]) * 1e4

def build(sym):
    days, di, G, F, cbd = load_grid(sym)
    rows = []; prev = None
    for d in BDAYS:
        o = d.toordinal()
        if o < dt.date(2010, 1, 1).toordinal() or o > dt.date(2026, 6, 30).toordinal(): continue
        bd = BD[o]; m = d.month
        rec = dict(ord=o, year=d.year, month=m, wd=d.weekday(), bd=bd, odd=(m % 2 == 1), half=(d in HALF),
                   TR=(m in GSCI_MONTHS and GSCI_BD[0] <= bd <= GSCI_BD[1]),
                   CA=((m not in GSCI_MONTHS) and GSCI_BD[0] <= bd <= GSCI_BD[1]),
                   PRE60=win(G, F, di, o, 12 * 12 + 6, 13 * 12 + 6),
                   FIRST30=win(G, F, di, o, 12 * 12 + 6, 13 * 12),
                   SET30=win(G, F, di, o, 13 * 12, 13 * 12 + 6),
                   POST60=win(G, F, di, o, 13 * 12 + 6, 14 * 12 + 6))
        i = di.get(o)
        rec["f1230"] = bool(F[i, 12 * 12 + 6]) if i is not None else True
        rec["f1330"] = bool(F[i, 13 * 12 + 6]) if i is not None else True
        for h in range(24): rec[f"H{h:02d}"] = win(G, F, di, o, h * 12, min(h * 12 + 12, 287))
        rec["DAY"] = (math.log(cbd[o] / cbd[prev]) * 1e4) if (prev is not None and o in cbd and prev in cbd) else np.nan
        if o in cbd: prev = o
        rows.append(rec)
    return pd.DataFrame(rows)

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
def welch(a, b):
    a = np.asarray(a, float); a = a[np.isfinite(a)]; b = np.asarray(b, float); b = b[np.isfinite(b)]
    if len(a) < 5 or len(b) < 5: return np.nan, np.nan, np.nan, len(a), len(b)
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); d = a.mean() - b.mean()
    return d, d / se, se, len(a), len(b)

df = build("XAU")
sub = {wn: df[(df.year >= y0) & (df.year <= y1)] for wn, (y0, y1) in WIN.items()}

# ================= A0 複製 =================
say("\n## A0 複製（c51 の数字と 2 桁一致か）")
REP = {}
for col, ref in [("PRE60", {"在 2010-20": +3.20, "外 2021-26H1": +0.49, "近年 2024-26H1": -1.06}),
                 ("POST60", {"在 2010-20": -1.03, "外 2021-26H1": -2.11, "近年 2024-26H1": -1.03}),
                 ("SET30", {"在 2010-20": +3.26, "外 2021-26H1": -1.31, "近年 2024-26H1": -2.10}),
                 ("DAY", {"在 2010-20": -15.24, "外 2021-26H1": +0.14, "近年 2024-26H1": -9.23})]:
    out = []
    for wn in WIN:
        d, t, se, na, nb = welch(sub[wn].loc[sub[wn].TR, col], sub[wn].loc[sub[wn].CA, col])
        REP[(col, wn)] = dict(d=d, t=t, se=se, na=na, nb=nb)
        ok = "OK" if abs(d - ref[wn]) <= 0.02 else f"MISMATCH(c51 {ref[wn]:+.2f})"
        out.append(f"{wn} Δ {d:+.2f} (t {t:+.2f}・MDE {2*se:.2f}・n {na}/{nb}) {ok}")
    say(f"- {col}: " + " | ".join(out))
for wn in WIN:
    d_ = sub[wn]; r1 = d_.loc[d_.TR, "PRE60"].abs().median() / d_.loc[d_.CA, "PRE60"].abs().median()
    say(f"- |PRE60| 中央値比 {wn}: {r1:.3f}（c51: 在 1.019／外 0.933／近年 0.743）")

# ================= A1 BREAK-K5 =================
say("\n## A1 → BREAK-K5: 「月パリティ対照は曜日に無差別」は月パリティの性質か、帯幅 5 営業日の機械的帰結か")
BANDS = [(1, 4), (5, 9), (10, 14), (15, 19), (20, 23)]
say("- BD 帯別 曜日組成（奇数月 T / 偶数月 C・月〜金 %）と最大シェア差:")
K5_break_a = False; K5_break_b_ok = True; BIAS = {}
mu_wd = {w: df.loc[df.wd == w, "PRE60"].mean() for w in range(5)}
say("  - 参考 全期間 曜日別 μ(PRE60) bp: " + " ".join(f"{'月火水木金'[w]}{mu_wd[w]:+.2f}" for w in range(5)))
for lo, hi in BANDS:
    m = df.bd.between(lo, hi)
    pt = np.array([(df[m & df.odd].wd == w).mean() for w in range(5)]) * 100
    pc = np.array([(df[m & ~df.odd].wd == w).mean() for w in range(5)]) * 100
    dmax = np.abs(pt - pc).max()
    bias = sum((pt[w] - pc[w]) / 100 * mu_wd[w] for w in range(5))
    BIAS[(lo, hi)] = bias
    unif_t = np.abs(pt - 100 / 5).max(); unif_c = np.abs(pc - 100 / 5).max()
    width = hi - lo + 1
    if dmax >= 5: K5_break_a = True
    if width == 5 and max(unif_t, unif_c) > 2.0: K5_break_b_ok = False
    say(f"  - BD{lo}-{hi}（幅 {width} 営業日）: T " + "/".join(f"{x:.1f}" for x in pt) + " vs C " + "/".join(f"{x:.1f}" for x in pc) +
        f" → 最大差 {dmax:.1f} pt・一様からの最大乖離 T {unif_t:.1f}/C {unif_c:.1f} pt・曜日偏りが作る bias {bias:+.2f} bp")
say(f"- BREAK-K5 (a) いずれかの帯で曜日シェア差 ≥5 pt: {K5_break_a}")
say(f"- BREAK-K5 (b) 5 営業日帯は（パリティに関係なく）ほぼ一様: {K5_break_b_ok}（＝一様性の出所は帯幅 5）")
say("- 4 営業日帯（BD1-4・BD20-23）は 5 営業日の整数倍でないので一様になり得ない → c51 のプラセボ ② のうち"
    " BD1-4／BD20-23 は曜日交絡を含む。実害 bp = 上の bias 列。")

# ================= A2 BREAK-K4 =================
say("\n## A2 → BREAK-K4: ボラ比という“フローの存在痕跡”テストの検出力（ブートストラップ CI と最小検出倍率）")
def med_ratio_boot(a, b, nb_=5000):
    a = np.asarray(a, float); a = np.abs(a[np.isfinite(a)]); b = np.asarray(b, float); b = np.abs(b[np.isfinite(b)])
    ia = rng.integers(0, len(a), (nb_, len(a))); ib = rng.integers(0, len(b), (nb_, len(b)))
    r = np.median(a[ia], axis=1) / np.median(b[ib], axis=1)
    return np.median(a) / np.median(b), np.percentile(r, 2.5), np.percentile(r, 97.5)
K4_break = False
for wn in WIN:
    d_ = sub[wn]; a = d_.loc[d_.TR, "PRE60"].values; b = d_.loc[d_.CA, "PRE60"].values
    r, lo_, hi_ = med_ratio_boot(a, b)
    half = (hi_ - lo_) / 2
    if half >= 0.05: K4_break = True
    say(f"- {wn}: |PRE60| 比 {r:.3f}・95% CI [{lo_:.3f}, {hi_:.3f}]（半幅 {half:.3f}）→ ±{half*100:.1f}% 未満のフロー痕跡は検出不能")
    ks = []
    for k in [1.05, 1.10, 1.20, 1.30, 1.50]:
        _, l2, h2 = med_ratio_boot(a * k, b)
        ks.append(f"k={k:.2f}→CI[{l2:.2f},{h2:.2f}]{'*' if l2 > 1 else ''}")
    say(f"  - 陽性対照（T 日の |PRE60| を k 倍）: " + " ".join(ks) + "  (* = CI が 1 を外す＝検出できる)")
say(f"- BREAK-K4（CI 半幅 ≥0.05 がいずれかの窓期で成立）: {K4_break}")

# ================= A3 BREAK-R1 =================
say("\n## A3 → BREAK-R1: セルの入れ子・実効検定数")
for wn in WIN:
    d_ = sub[wn]
    f30, tf, _, nf, nc = welch(d_.loc[d_.TR, "FIRST30"], d_.loc[d_.CA, "FIRST30"])
    s30 = REP[("SET30", wn)]; p60 = REP[("PRE60", wn)]
    say(f"- {wn} 分解: FIRST30 12:30→13:00 Δ {f30:+.2f} (t {tf:+.2f}) + SET30 13:00→13:30 Δ {s30['d']:+.2f} (t {s30['t']:+.2f})"
        f" ≈ PRE60 Δ {p60['d']:+.2f} (t {p60['t']:+.2f})  [合計 {f30+s30['d']:+.2f}]")
cols = ["PRE60", "SET30", "FIRST30", "POST60", "DAY"] + [f"H{h:02d}" for h in range(24)]
C = df[cols].corr().values
C = np.nan_to_num(C, nan=0.0); np.fill_diagonal(C, 1.0)
lam = np.linalg.eigvalsh(C); M = len(cols)
Meff = 1 + (M - 1) * (1 - np.var(lam, ddof=1) / M)
say(f"- 記述 family {M} 列（PRE60/SET30/FIRST30/POST60/DAY + ET 24 窓）の Cheverud–Nyholt 実効検定数 M_eff = {Meff:.1f}")
say(f"  - 相関の実例: corr(PRE60, SET30) {np.corrcoef(df.PRE60.fillna(0), df.SET30.fillna(0))[0,1]:.2f}・"
    f"corr(PRE60, H12) {df[['PRE60','H12']].corr().iloc[0,1]:.2f}・corr(PRE60, DAY) {df[['PRE60','DAY']].corr().iloc[0,1]:.2f}")
say(f"- c51 の会計「約 40 セル・期待 2 本」vs 実効 {Meff:.1f} 列 ×（窓期は在/外/近年で重複あり）→ 期待本数の見直しは下記 A4 の置換で直接出す")

# ================= A4 BREAK-R2 =================
say("\n## A4 → BREAK-R2: 月単位ブロック置換による帰無分布（Welch se が正しいか）")
NPERM = 5000
R2_break = False
for wn, (y0, y1) in WIN.items():
    d_ = sub[wn]
    band = d_[d_.bd.between(*GSCI_BD)].copy()
    band["ym"] = band.year * 100 + band.month
    # ブロック = year-month。各年で「T 月」を 6 個（年内に存在する月数の半分）ランダム選択
    stats = {"PRE60": [], "SET30": []}
    yms = band.groupby("year")["month"].unique().to_dict()
    vals = {c: {ym: band.loc[band.ym == ym, c].values for ym in band.ym.unique()} for c in ["PRE60", "SET30"]}
    for _ in range(NPERM):
        tsel = set()
        for y, ms in yms.items():
            k = max(1, len(ms) // 2)
            pick = rng.choice(ms, size=k, replace=False)
            tsel |= {y * 100 + int(m) for m in pick}
        for c in ["PRE60", "SET30"]:
            A = np.concatenate([vals[c][ym] for ym in band.ym.unique() if ym in tsel]) if tsel else np.array([])
            B = np.concatenate([vals[c][ym] for ym in band.ym.unique() if ym not in tsel])
            A = A[np.isfinite(A)]; B = B[np.isfinite(B)]
            stats[c].append(A.mean() - B.mean() if len(A) > 4 and len(B) > 4 else np.nan)
    for c in ["PRE60", "SET30"]:
        s = np.array(stats[c], float); s = s[np.isfinite(s)]
        obs = REP[(c, wn)]["d"]; we = REP[(c, wn)]["se"]
        psd = s.std(ddof=1); p2 = float((np.abs(s) >= abs(obs)).mean())
        flag = "BREAK" if psd > 1.25 * we else "ok"
        if c == "PRE60" and psd > 1.25 * we: R2_break = True
        say(f"- {wn} {c}: 観測 Δ {obs:+.2f}・Welch se {we:.2f}（MDE {2*we:.2f}）vs 置換 sd {psd:.2f}（MDE {2*psd:.2f}）"
            f"・比 {psd/we:.2f} [{flag}]・置換 two-sided p {p2:.3f}")
say(f"- BREAK-R2（主セル 在 で 置換 sd > 1.25×Welch se）: {R2_break}")

# ================= A5 処置定義のプラセボ（924 分割） =================
say("\n## A5 プラセボ（c51 未実施・処置定義そのもの）: 12 か月から 6 か月を選ぶ 924 分割の中で「奇数月」は何位か")
for wn in WIN:
    d_ = sub[wn]; band = d_[d_.bd.between(*GSCI_BD)]
    per_m = {m: band.loc[band.month == m, "PRE60"].values for m in range(1, 13)}
    per_m = {m: v[np.isfinite(v)] for m, v in per_m.items()}
    recs = []
    for S in itertools.combinations(range(1, 13), 6):
        A = np.concatenate([per_m[m] for m in S]); B = np.concatenate([per_m[m] for m in range(1, 13) if m not in S])
        if len(A) < 5 or len(B) < 5: continue
        se = math.sqrt(A.var(ddof=1) / len(A) + B.var(ddof=1) / len(B)); d = A.mean() - B.mean()
        recs.append((S, d, d / se))
    tt = np.array([abs(r[2]) for r in recs]); real = [r for r in recs if set(r[0]) == GSCI_MONTHS][0]
    rank = int((tt > abs(real[2])).sum()) + 1
    best = max(recs, key=lambda r: abs(r[2]))
    say(f"- {wn}: 奇数月分割 Δ {real[1]:+.2f} (t {real[2]:+.2f}) の順位 **{rank}/{len(recs)}**（上位 {100*rank/len(recs):.0f}%）"
        f"・family max|t| {best[2]:+.2f} @ 月 {sorted(best[0])}・|t| sd {tt.std(ddof=1):.2f}")

# ================= A6 データ衛生 =================
say("\n## A6 データ衛生・look-ahead")
for wn in WIN:
    d_ = sub[wn]
    say(f"- {wn}: T 日 {int(d_.TR.sum())}（PRE60 有効 {int(d_.loc[d_.TR,'PRE60'].notna().sum())}・12:30 flat {d_.loc[d_.TR,'f1230'].mean()*100:.1f}%・13:30 flat {d_.loc[d_.TR,'f1330'].mean()*100:.1f}%）"
        f" / C_A {int(d_.CA.sum())}（有効 {int(d_.loc[d_.CA,'PRE60'].notna().sum())}・{d_.loc[d_.CA,'f1230'].mean()*100:.1f}%・{d_.loc[d_.CA,'f1330'].mean()*100:.1f}%）")
hb = df[df.half]
say(f"- 早引け候補日 {len(hb)} 日（規則生成: 7/3・感謝祭翌日・12/24）の BD 位置: " +
    " ".join(f"{int(r.year)}-{int(r.month):02d}BD{int(r.bd)}" for r in hb.itertuples()) )
hin = hb[hb.bd.between(*GSCI_BD)]
say(f"- うち BD5-9 に落ちるもの: {len(hin)} 日" + ("（" + " ".join(f"{int(r.year)}-{int(r.month):02d}(奇数月={bool(r.odd)})" for r in hin.itertuples()) + "）" if len(hin) else "＝なし → 12:30–13:30 窓は早引けに汚染されない"))

# ================= A7 LOYO + コスト倍 =================
say("\n## A7 LOYO（在 Δ_PRE60 の年集中）とゲート ㉛ のコスト倍")
d_ = sub["在 2010-20"]; outs = []
for y in range(2010, 2021):
    e = d_[d_.year != y]
    d, t, se, na, nb = welch(e.loc[e.TR, "PRE60"], e.loc[e.CA, "PRE60"]); outs.append((y, d, t))
say("- 在 LOYO: " + " ".join(f"-{y}:{d:+.2f}(t{t:+.2f})" for y, d, t in outs))
say(f"  - 符号が負に転じる年抜き: {[y for y,d,t in outs if d<0] or 'なし'}・|t|≥2 を保つ年抜き: {[y for y,d,t in outs if abs(t)>=2] or 'なし'}")
try:
    dj = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"))); TRD = dj["trades"]
    et_e = pd.to_datetime([t["entry_time"] for t in TRD], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None)
    eo = et_e.normalize().values.astype("datetime64[D]").astype("int64") + dt.date(1970, 1, 1).toordinal()
    hh = et_e.hour.values + et_e.minute.values / 60.0
    Tset = set(df.ord[df.TR].tolist()); Cset = set(df.ord[df.CA].tolist())
    yr = np.array([t["year"] for t in TRD]); R = np.array([t["R"] for t in TRD]); risk = np.array([t["risk"] for t in TRD]); ex = np.array([t["exit"] for t in TRD])
    inT = np.array([o in Tset for o in eo.tolist()]); inC = np.array([o in Cset for o in eo.tolist()]); tw = (hh >= 9.0) & (hh < 13.5)
    for mult, tag in [(0.1, "1× cost"), (0.2, "2× cost")]:
        ft = mult / risk; Rs = np.where(ex == "TIME", R - ft, R + ft)
        row = []
        for wn, (y0, y1) in WIN.items():
            w = (yr >= y0) & (yr <= y1) & tw
            d, t, se, na, nb = welch(Rs[w & inT], Rs[w & inC])
            row.append(f"{wn} Δμ {d:+.3f} (t {t:+.2f}・MDE {2*se:.3f}R・n {na}/{nb})")
        say(f"- ゲート ㉛ {tag}: " + " | ".join(row))
except Exception as e:
    say(f"- ゲート ㉛: scan json 読込不可 ({e}) → 未実施")

say(f"\n（経過 {time.time()-T0:.1f}s・置換 {NPERM}・ブートストラップ 5000・seed 20261119・外部通信なし・MT5 なし）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\n[written] {OUT}")
