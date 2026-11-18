# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-18 15:40 反証レーン] 対象 = **cycle40 (2026-11-11 18:50) の「未反証の正の持ち越し」**
（c49 判定 (1) と提案 (b) が名指しした唯一の件: cells.csv の c40 C2・forward=yes・verdict 列に反証の記入なし）

=== 対象の主張（c40 の本文から逐語・ここを壊しに行く）===
T1【統計】XAU（Dukascopy bid M5）で LAST(15:30→16:00 ET) ~ FIRST_B(前営業日 16:00 → D 10:00 ET) は
   外 2021-26H1 **β +0.026・HC1 t +3.95・NW +2.97・R² 3.7%・MDE 0.013**／近年 2024-26H1 +0.031 t +3.27。
   （在 2012-20 は +0.009 t +1.99 で c40 自身が「規則上 null」と書いた＝㊶ 型「外のみで立つ」）
T2【機構・事後】予測子は純日内の最初の半時間ではなく **ON（前日 16:00 → 09:30・17.5 h）** b +0.029 (t 3.96)
   で FIRST_A は −0.004 (t −0.20)。半時間プロファイル 12 スロット中 **外は 16:00 スロットだけ t 4.0**
   （他 11 スロット |t| ≤1.8）＝「**引け固有**」。
T3【経済】符号戦略 S = mean(sign(FIRST_B)·LAST) は 外 **+1.07 bp/日 (t 3.22・正 55%)**・近年 +1.56 (t 2.62)、
   往復 0.16 USD = 0.5〜0.9 bp を引いて **net +0.2〜+0.6 bp/日・年 0.5〜1.5%（無レバ）＝薄いが受け取れる**。
T4【前向き事前固定】c40 が cells.csv に登記した復活条件: 「金 LAST ~ ON の β>0 ∧ HC1 t≥2 ∧ 符号反転 p<0.025
   ∧ 符号戦略 net（往復 0.16 USD 控除）>0 かつ t≥1.5」。→ **この 4 条件を、c40 が既に持っていた 外 のデータに
   そのまま当てて通るか**（新データを待たずに測れる部分＝net と t の整合）も検査する。

=== 事前固定（この docstring を全部書いてから数字を見る・数字を見た後の変更は「事後」と明記する）===
データ: data/macro/XAU_m5_close.npz（bid・2012-01〜2026-06）・XAU_m5_ohlc.npz（第 2 測定）・US500_m5_close.npz（プラセボ signal）。
  既存キャッシュのみ。scan 無し・MT5 無し・外部通信無し・本番ファイルは読まない（コスト校正は既存 data/c4_spread_structure_result.md の
  観測値 中央値 0.160／平均 0.176／p90 0.22 USD を**数値としてハードコード**し spread_log 本体は読まない）。
格子・時計・窓の定義・有効日の定義は **c40 と 1 文字も変えない**（price_at は ts == T−300 の close・ET 平日暦）。
推定器: OLS・HC1・NW(5) は c40 と同じ。追加 = 年クラスタ CR1・月クラスタ CR1・**wild cluster bootstrap（帰無を課す・
  Rademacher・9999 回・年／月）**・符号反転置換（c40 の方法論 ㊷ が指定した正しい帰無・9999 回）。
窓: 在 2012-20／外 2021-26H1（**判定の主**＝対象の主張が立っているセル）／近年 2024-26H1。D2 遵守: 16 年一括は使わない・
  判定は窓別。16 年一括の数字は一切出さない。

--- 攻撃 A: 人工物（測定・選択・機械項）---
A1 複製: c40 の β/t を 4 桁で再現（在 +0.009 t 1.99／外 +0.026 t 3.95／近年 +0.031 t 3.27・ON 分解 +0.029 t 3.96）。
A2 **被説明変数での選択**: c40 の有効日は「LAST ≠ 0」を要求＝**被説明変数の値で日を落としている**（㉒ の 0 比率対策
   として入れた条件だが、|y|>0 の選択は高ボラ日への偏り）。LAST==0 の日を 0 として戻した標本で再推定。
A3 stale 監査: 外の有効日のうち 15:30／16:00 の足が直前足と同値（flat）の比率。LAST が stale 気配で作られていれば
   「受け取れる半時間リターン」ではない。
A4 **第 2 測定（方法論 63 の EIV 検査の同型）**: LAST の窓を ±1 足（5 分）ずらした 4 本（15:25→15:55／15:35→16:05／
   15:30→16:05／15:25→16:00）と、ON の始点を ±1 足ずらした 2 本で β を再推定。
A5 機械項: 予測子と被説明変数が価格を共有するか（FIRST_B の始点 = 前日 LAST の終点 → 1 期ずれで**負**の機械項が
   入るはず）。対照として LAST(D−1) ~ FIRST_B(D) を推定し、符号が負であることを確認（正なら測定誤差では説明不能）。

--- 攻撃 B: 期間・クラスタ・多重検定 ---
B1 **外 ex-2026H1**（c40 自身の最重大反証 (ii)「2026H1 +0.060 t 3.8 が外を押し上げる・未計算」を実行）。
B2 leave-one-year-out（2021・2022・2023・2024・2025・2026H1 を 1 つずつ落として外を再推定）。
B3 年クラスタ CR1／月クラスタ CR1／wild cluster bootstrap p（年・月）。c43 W-FRI を壊したのと同じ攻撃。
B4 外の前半・後半 2 分割（2021-2023H1／2023H2-2026H1）・曜日別。
B5 **符号反転置換 p**（c40 の前向き条件に入っている帰無・9999 回）。

--- 攻撃 C: 「引け固有」（T2）---
C1 **プロファイルを 16:00 で切らずに金のセッション終端まで延長**（16:30・17:00・17:30 ET・NaN 率を併記）。
   c40b のプロファイルは米株の格子に合わせて 16:00 で**打ち切られて**おり、「16:00 スロットだけ」は
   打ち切りの産物かもしれない（金は 24h 近く動く）。
C2 延長スロット族（10:30〜17:30）に **BH(0.05) と Holm** を当て、16:00 スロットが族内で生き残るか。
C3 ON は残り 1 日全体（10:00→16:00）を予測するか＝半時間あたりに直すと 16:00 が本当に突出するか。

--- 攻撃 D: 経済（T3・T4）---
D1 符号戦略の net を **日次価格に基づく bp コスト** c/price·1e4 で引く。コスト 3 水準:
   ①0.16 USD（c4 の観測中央値・c40 が使った 1×）②0.22 USD（c4 の観測 p90＝悪条件だが実測）③0.32 USD（**2×**）。
   各について mean・se・t・年別。**c40 の前向き条件「net>0 ∧ t≥1.5」を 外 のデータに当てる**。
D2 **ドリフト交絡（新しい攻撃）**: 2021-26H1 は金の強い上昇期。mean(LAST) ≠ 0 かつ sign(ON)>0 の比率が
   50% から外れていれば、S = mean(sign(ON)·LAST) は**買い持ちのドリフトを拾っているだけ**で予測ではない。
   mean(LAST)・P(ON>0)・ドリフト項の寄与 P(ON>0)·mean(LAST) − ... を分解し、**LAST を窓内平均で除去した
   S_demeaned**（＝純粋な条件づけ部分）を出す。
D3 プラセボ signal: ①sign(ON) を 5 日前の値に置換（ボラ構造を保ったまま情報を壊す）②US500 の ON の符号
   ③固定ロング（常に +1）。①②が S と同程度を稼ぐならドリフト／一般性質。
D4 Sharpe（年率）・年別 net・最悪年。

=== 破壊条件（事前・判定語はこの規則で決める）===
BREAK-A（人工物）: A4 の 6 本のうち **≥3 本で 外 |t| <2.0**、または A1 の複製が β で 0.003 超ずれる。
BREAK-B（期間・推論）: B1 で 外 ex-2026H1 の **t <2.0 かつ β <0.015**、または B2 の LOYO 最小 |t| <2.0、
   または B3 の wild cluster bootstrap p（年）>0.05、または B5 の符号反転 p ≥0.025。
BREAK-C（機構 T2）: C1 で **16:00 より後のスロットが 2 本以上 同符号で |t| ≥2.0**（＝引け固有でなく遅い時間帯全体）、
   または C2 で 16:00 スロットが族内 BH(0.05) を通らない。
BREAK-D（経済 T3/T4）: コスト 2×（0.32 USD）で **net ≤0 または t <1.5**（＝c40 自身の前向き条件を落とす）、
   または D2 で S_demeaned が 外 で t <1.5、または D3 のプラセボが S の 50% 以上を稼ぐ。
判定語: BREAK-A または BREAK-B が立てば **broken（統計的主張 T1 ごと）**／T1 が残り BREAK-C だけなら
   **T2 broken・T1 survived**／T1 残存で BREAK-D なら **T3/T4 broken（受取り不能）**／どれも立たなければ **survived**／
   MDE が差を判別できない所は **inconclusive** と書く（「効果なし」とは書かない）。
事前に認める自分の弱点: (α) 外 n ≈1362 日の 1 セルに対し攻撃を 20 本以上当てる＝**反証側の多重検定**で
   「どれか 1 本が壊す」確率は高い → 破壊条件は「複数本の一致」か「c40 自身の事前条件の不通過」に限り、
   単発の p<0.05 を破壊と呼ばない。(β) A2/A4 は c40 の定義を変える＝「別の定義では立たない」は脆さの証拠だが
   「元の定義が誤り」の証明ではない。(γ) D2 のドリフト除去は未来平均を使う（look-ahead）＝**分解の読みにだけ使い
   受取り可能性の判定には使わない**（判定は D1 の net のみ）。(δ) 在 2012-20 は c40 が既に null と書いており壊す余地なし。
seed 20261118。読取りと分析のみ・発注なし・本番編集なし・書込みは AUREL_RESEARCH 配下のみ。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c40_intraday_momentum.md"); L = []
NY = "America/New_York"; SEED = 20261118; rng = np.random.default_rng(SEED); NB = 9999
def say(s=""):
    print(s, flush=True); L.append(s)

say(f"# [REFUTE c40] 金 日内モメンタム（LAST~FIRST_B/ON）の反証 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c40_intraday_momentum.py)")
say("対象 = c40 C2（cells.csv forward=yes・未反証）。破壊条件は docstring に事前固定。")

# ---------- c40 と同一のローダ・時計・窓 ----------
def load(sym, key="close"):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_{'close' if key=='close' else 'ohlc'}.npz"))
    ts = zz["ts"].astype(np.int64)
    if key == "close":
        return ts, zz["close"].astype(float)
    return ts, {k: zz[k].astype(float) for k in zz.files if k != "ts"}

def epoch_et(dates, hour, minute):
    naive = dates + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)

def price_at(ts, cl, T, off=0):
    """c40 と同一: ts == T-300 の足の close。off は分単位のずらし（A4 用）。"""
    out = np.full(len(T), np.nan); ok = np.isfinite(T)
    key = (T[ok] - 300 + off * 60).astype(np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan)
    return out

dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy(); mo = dates.month.to_numpy(); wd = dates.weekday.to_numpy()
lg = np.log
ERAS = [("在 2012-20", 2012, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

ts_x, cl_x = load("XAU")
say(f"- XAU npz: {len(ts_x)} 本 {pd.to_datetime(ts_x[0],unit='s')}〜{pd.to_datetime(ts_x[-1],unit='s')} UTC・取引日候補 {N}")

P = lambda h, m, off=0: price_at(ts_x, cl_x, epoch_et(dates, h, m), off)
p16 = P(16, 0); p16p = np.r_[np.nan, p16[:-1]]
p1530 = P(15, 30); p0930 = P(9, 30); p10 = P(10, 0)
FB = (lg(p10) - lg(p16p)) * 1e4
FA = (lg(p10) - lg(p0930)) * 1e4
ON = (lg(p0930) - lg(p16p)) * 1e4
LAST = (lg(p16) - lg(p1530)) * 1e4
SECOND = (lg(P(10, 30)) - lg(p10)) * 1e4
MID = (lg(P(12, 30)) - lg(P(12, 0))) * 1e4
TWELFTH = (lg(p1530) - lg(P(15, 0))) * 1e4

# c40 と同一の有効日（6 窓有限 ∧ LAST≠0 ∧ FIRST≠0）
valid = np.isfinite(FB) & np.isfinite(FA) & np.isfinite(SECOND) & np.isfinite(MID) & np.isfinite(TWELFTH) & np.isfinite(LAST)
valid &= (LAST != 0) & (FB != 0) & (FA != 0)

# ---------- 推定器 ----------
def ols(y, x, clus=None):
    m = np.isfinite(y) & np.isfinite(x)
    if clus is not None: m = m & np.isfinite(clus.astype(float))
    y2, x2 = y[m], x[m]; n = len(y2)
    if n < 30: return dict(n=n, b=np.nan, t=np.nan, tnw=np.nan, se=np.nan, r2=np.nan, tcl=np.nan, G=0)
    xc = x2 - x2.mean(); yc = y2 - y2.mean(); sxx = xc @ xc
    b = (xc @ yc) / sxx; e = yc - b * xc
    se = math.sqrt((xc ** 2 @ e ** 2) / sxx ** 2 * n / (n - 2))
    g = xc * e; s = g @ g / n
    for l in range(1, 6): s += 2 * (1 - l / 6) * (g[l:] @ g[:-l]) / n
    senw = math.sqrt(max(s, 1e-18) / n) * n / sxx
    r2 = 1 - (e @ e) / (yc @ yc)
    tcl = np.nan; G = 0
    if clus is not None:
        cv = clus[m]; G = len(np.unique(cv)); acc = 0.0
        for c in np.unique(cv):
            k = cv == c; acc += (g[k].sum()) ** 2
        secl = math.sqrt(acc / sxx ** 2 * G / max(G - 1, 1) * (n - 1) / (n - 2))
        tcl = b / secl
    return dict(n=n, b=b, t=b / se, tnw=b / senw, se=se, r2=r2, tcl=tcl, G=G)

def fo(o):
    if not np.isfinite(o["b"]): return f"—(n{o['n']})"
    return f"β {o['b']:+.4f} (HC1 t {o['t']:+.2f}, NW {o['tnw']:+.2f}, MDE {2*o['se']:.4f}, R² {o['r2']*100:.1f}%, n{o['n']})"

def wild_cluster_p(y, x, m, clus, nb=NB, seed=SEED):
    """帰無 β=0 を課した wild cluster bootstrap（Rademacher）。"""
    mm = m & np.isfinite(y) & np.isfinite(x)
    y2, x2, c2 = y[mm], x[mm], clus[mm]
    n = len(y2); xc = x2 - x2.mean(); sxx = xc @ xc
    b0 = (xc @ (y2 - y2.mean())) / sxx
    e0 = y2 - y2.mean()                      # 帰無モデル y = α のみ
    uc, inv = np.unique(c2, return_inverse=True); G = len(uc)
    r = np.random.default_rng(seed)
    W = r.choice([-1.0, 1.0], size=(nb, G))[:, inv]      # (nb, n)
    ys = e0[None, :] * W
    bs = (ys - ys.mean(axis=1, keepdims=True)) @ xc / sxx
    return (np.abs(bs) >= abs(b0)).mean(), G, b0

def signflip_p(y, x, m, nb=NB, seed=SEED + 1):
    mm = m & np.isfinite(y) & np.isfinite(x)
    y2, x2 = y[mm], x[mm]; yc = y2 - y2.mean()
    xc0 = x2 - x2.mean(); b0 = (xc0 @ yc) / (xc0 @ xc0)
    r = np.random.default_rng(seed)
    S = r.choice([-1.0, 1.0], size=(nb, len(x2)))
    XS = x2[None, :] * S
    XC = XS - XS.mean(axis=1, keepdims=True)
    bs = (XC @ yc) / (XC * XC).sum(axis=1)
    return (bs >= b0).mean(), (np.abs(bs) >= abs(b0)).mean(), b0, bs.std()

def strat(sig, y, m, cost_bp=None):
    """符号戦略。sig の符号で y を取る。cost_bp は日次 bp コスト配列。"""
    mm = m & np.isfinite(y) & np.isfinite(sig) & (sig != 0)
    s = np.sign(sig[mm]) * y[mm]
    if cost_bp is not None: s = s - cost_bp[mm]
    n = len(s)
    if n < 30: return dict(n=n, mean=np.nan, t=np.nan, pos=np.nan, se=np.nan)
    se = s.std(ddof=1) / math.sqrt(n)
    return dict(n=n, mean=s.mean(), t=s.mean() / se, pos=(s > 0).mean(), se=se, sd=s.std(ddof=1))

# ============================================================ A1 複製
say("\n## A1 複製（c40 の数字を再現できるか）")
say("| セル | n | LAST~FIRST_B | LAST~ON(2変数の単回帰) | 対照 SECOND~FB | プラセボ MID~FB |")
say("|---|---|---|---|---|---|")
REP = {}
for lab, lo, hi in ERAS:
    m = valid & (yr >= lo) & (yr <= hi)
    o = ols(LAST, FB, None); o = ols(LAST[m], FB[m])
    oon = ols(LAST[m], ON[m]); o2 = ols(SECOND[m], FB[m]); o3 = ols(MID[m], FB[m])
    REP[lab] = o
    say(f"| {lab} | {o['n']} | {fo(o)} | {fo(oon)} | β {o2['b']:+.4f} (t {o2['t']:+.2f}) | β {o3['b']:+.4f} (t {o3['t']:+.2f}) |")

def ols2(y, x1, x2):
    m = np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2)
    y2, a, b_ = y[m], x1[m], x2[m]; n = len(y2)
    X = np.c_[np.ones(n), a, b_]; XtXi = np.linalg.inv(X.T @ X)
    bb = XtXi @ X.T @ y2; e = y2 - X @ bb
    V = XtXi @ (X.T * e ** 2) @ X @ XtXi * n / (n - 3); se = np.sqrt(np.diag(V))
    return bb, bb / se, n

say("\nFIRST_B の分解（c40b の再現）: LAST = a + b1·ON + b2·FIRST_A")
for lab, lo, hi in ERAS:
    m = valid & (yr >= lo) & (yr <= hi)
    bb, tt, n = ols2(LAST[m], ON[m], FA[m])
    say(f"- {lab}: b_ON {bb[1]:+.4f} (t {tt[1]:+.2f})・b_FA {bb[2]:+.4f} (t {tt[2]:+.2f})・n {n}")

M_OUT = valid & (yr >= 2021)
M_IN = valid & (yr <= 2020)
M_REC = valid & (yr >= 2024)

# ============================================================ A2 被説明変数での選択
say("\n## A2 被説明変数での選択（c40 の有効日は LAST≠0 を要求）")
valid_noy = np.isfinite(FB) & np.isfinite(FA) & np.isfinite(SECOND) & np.isfinite(MID) & np.isfinite(TWELFTH) & np.isfinite(LAST) & (FB != 0) & (FA != 0)
for lab, lo, hi in ERAS:
    m0 = valid & (yr >= lo) & (yr <= hi); m1 = valid_noy & (yr >= lo) & (yr <= hi)
    o0 = ols(LAST[m0], FB[m0]); o1 = ols(LAST[m1], FB[m1])
    say(f"- {lab}: LAST≠0 要求 {fo(o0)} → **0 の日も含める** {fo(o1)}（戻した日数 {int(m1.sum()-m0.sum())}）")

# ============================================================ A3 stale 監査
say("\n## A3 stale 監査（15:30／16:00 の足が直前足と同値の比率）")
def flat_rate(h, mi, m):
    cur = P(h, mi); prv = P(h, mi, off=-5)
    k = m & np.isfinite(cur) & np.isfinite(prv)
    return (cur[k] == prv[k]).mean() * 100, int(k.sum())
for lab, mm in (("在", M_IN), ("外", M_OUT), ("近年", M_REC)):
    r1, n1 = flat_rate(15, 30, mm); r2, n2 = flat_rate(16, 0, mm)
    say(f"- {lab}: 15:30 足 flat {r1:.1f}%（n{n1}）・16:00 足 flat {r2:.1f}%（n{n2}）・LAST の厳密 0 比率（有効日前）"
        f" {np.mean(np.isfinite(LAST[(yr>=2021) if lab=='外' else (yr<=2020) if lab=='在' else (yr>=2024)]) & (LAST[(yr>=2021) if lab=='外' else (yr<=2020) if lab=='在' else (yr>=2024)]==0))*100:.1f}%")

# ============================================================ A4 第 2 測定（窓を 5 分ずらす）
say("\n## A4 第 2 測定: LAST／ON の窓を ±1 足（5 分）ずらす（方法論 63 の EIV 検査の同型）")
say("| 定義 | 在 | 外 | 近年 |")
say("|---|---|---|---|")
VARIANTS = []
def mk(lastdef, ondef, name):
    (h1, m1, o1), (h2, m2, o2) = lastdef
    y = (lg(P(h2, m2, o2)) - lg(P(h1, m1, o1))) * 1e4
    if ondef is None:
        x = FB
    else:
        (g1, n1_, f1), (g2, n2_, f2) = ondef
        pa = P(g1, n1_, f1); pa = np.r_[np.nan, pa[:-1]] if f1 == "prev" else pa
        x = None
    return name, y, x
# LAST 側 4 本（予測子は FIRST_B 固定）
last_defs = [
    ("LAST 15:30→16:00（原型）", (15, 30, 0), (16, 0, 0)),
    ("LAST 15:25→15:55（−5分）", (15, 30, -5), (16, 0, -5)),
    ("LAST 15:35→16:05（+5分）", (15, 30, 5), (16, 0, 5)),
    ("LAST 15:30→16:05（終端+5）", (15, 30, 0), (16, 0, 5)),
    ("LAST 15:25→16:00（始点−5）", (15, 30, -5), (16, 0, 0)),
]
A4t = {}
for nm, (ha, ma, oa), (hb, mb, ob) in last_defs:
    y = (lg(P(hb, mb, ob)) - lg(P(ha, ma, oa))) * 1e4
    row = []
    for lab, lo, hi in ERAS:
        m = np.isfinite(y) & np.isfinite(FB) & (FB != 0) & (yr >= lo) & (yr <= hi)
        o = ols(y[m], FB[m]); row.append(f"β {o['b']:+.4f} (t {o['t']:+.2f}, n{o['n']})")
        if lab.startswith("外"): A4t[nm] = o
    say(f"| {nm} | " + " | ".join(row) + " |")
# ON 側 2 本（被説明変数は原型 LAST 固定）
on_defs = [("ON 前日16:00→09:30（原型）", 0, 0), ("ON 前日16:05→09:30", 5, 0), ("ON 前日16:00→09:25", 0, -5)]
for nm, offp, offa in on_defs:
    pp = P(16, 0, offp); pp = np.r_[np.nan, pp[:-1]]
    x = (lg(P(9, 30, offa)) - lg(pp)) * 1e4
    row = []
    for lab, lo, hi in ERAS:
        m = valid & np.isfinite(x) & (yr >= lo) & (yr <= hi)
        o = ols(LAST[m], x[m]); row.append(f"β {o['b']:+.4f} (t {o['t']:+.2f}, n{o['n']})")
        if lab.startswith("外"): A4t[nm] = o
    say(f"| {nm} | " + " | ".join(row) + " |")

# ============================================================ A5 機械項
say("\n## A5 機械項（FIRST_B の始点 = 前日 LAST の終点 → 1 期ずれで負が入るはず）")
LASTm1 = np.r_[np.nan, LAST[:-1]]
for lab, lo, hi in ERAS:
    m = valid & np.isfinite(LASTm1) & (yr >= lo) & (yr <= hi)
    o = ols(LASTm1[m], FB[m]); say(f"- {lab}: LAST(D−1) ~ FIRST_B(D) {fo(o)}（負が機械項の予測・正なら測定誤差では説明不能）")
for lab, lo, hi in ERAS:
    m = valid & np.isfinite(LASTm1) & (yr >= lo) & (yr <= hi)
    o = ols(LAST[m], LASTm1[m]); say(f"- {lab}: LAST(D) ~ LAST(D−1) {fo(o)}（LAST 自身の自己相関）")

# ============================================================ B 期間・クラスタ
say("\n## B1 外 ex-2026H1（c40 自身の最重大反証 (ii)・未計算だったもの）")
for nm, m in (("外 2021-26H1（原型）", M_OUT),
              ("外 ex-2026H1 = 2021-2025", valid & (yr >= 2021) & (yr <= 2025)),
              ("外 ex-2026H1 ex-2021", valid & (yr >= 2022) & (yr <= 2025)),
              ("2026H1 のみ", valid & (yr == 2026))):
    o = ols(LAST[m], FB[m]); oon = ols(LAST[m], ON[m])
    say(f"- {nm}: FIRST_B {fo(o)}／ON {fo(oon)}")

say("\n## B2 leave-one-year-out（外・FIRST_B と ON）")
say("| 落とした年 | n | LAST~FIRST_B | LAST~ON |")
say("|---|---|---|---|")
loyo = []
for y0 in range(2021, 2027):
    m = M_OUT & (yr != y0); o = ols(LAST[m], FB[m]); oo = ols(LAST[m], ON[m])
    loyo.append((y0, o, oo))
    say(f"| −{y0} | {o['n']} | β {o['b']:+.4f} (t {o['t']:+.2f}) | β {oo['b']:+.4f} (t {oo['t']:+.2f}) |")
say("\n年別（外・記述）: " + "・".join(
    f"{y0} β {ols(LAST[M_OUT&(yr==y0)], FB[M_OUT&(yr==y0)])['b']:+.4f} (t {ols(LAST[M_OUT&(yr==y0)], FB[M_OUT&(yr==y0)])['t']:+.2f}, n{int((M_OUT&(yr==y0)).sum())})"
    for y0 in range(2021, 2027)))

say("\n## B3 クラスタ推論（年・月）と wild cluster bootstrap（帰無を課す・9999）")
ym = yr * 100 + mo
for lab, m in (("在", M_IN), ("外", M_OUT), ("近年", M_REC)):
    oy = ols(LAST[m], FB[m], clus=yr[m] if False else None)
    # クラスタは mask 後に渡す必要があるので個別に
    def _cl(cv):
        mm = m & np.isfinite(LAST) & np.isfinite(FB)
        yy, xx, cc = LAST[mm], FB[mm], cv[mm]
        n = len(yy); xc = xx - xx.mean(); yc = yy - yy.mean(); sxx = xc @ xc
        b = (xc @ yc) / sxx; e = yc - b * xc; g = xc * e
        uc = np.unique(cc); G = len(uc)
        acc = sum((g[cc == c].sum()) ** 2 for c in uc)
        secl = math.sqrt(acc / sxx ** 2 * G / max(G - 1, 1) * (n - 1) / (n - 2))
        return b, b / secl, G
    by, tcy, Gy = _cl(yr); bm_, tcm, Gm = _cl(ym)
    py, Gp, b0 = wild_cluster_p(LAST, FB, m, yr)
    pm, Gpm, _ = wild_cluster_p(LAST, FB, m, ym, seed=SEED + 7)
    say(f"- {lab}: β {by:+.4f}・HC1 t {ols(LAST[m],FB[m])['t']:+.2f}・**年クラスタ t {tcy:+.2f}（G {Gy}）**・月クラスタ t {tcm:+.2f}（G {Gm}）"
        f"・wild cluster p 年 **{py:.4f}**／月 {pm:.4f}")

say("\n## B4 外の 2 分割・曜日別")
for nm, m in (("外 前半 2021-2023H1", M_OUT & ((yr <= 2022) | ((yr == 2023) & (mo <= 6)))),
              ("外 後半 2023H2-2026H1", M_OUT & ((yr >= 2024) | ((yr == 2023) & (mo >= 7))))):
    o = ols(LAST[m], FB[m]); say(f"- {nm}: {fo(o)}")
say("- 外 曜日別: " + "・".join(
    f"{'月火水木金'[w]} β {ols(LAST[M_OUT&(wd==w)], FB[M_OUT&(wd==w)])['b']:+.4f} (t {ols(LAST[M_OUT&(wd==w)], FB[M_OUT&(wd==w)])['t']:+.2f})"
    for w in range(5)))

say("\n## B5 符号反転置換 p（c40 の前向き条件に入っている帰無・9999 回）")
for lab, m in (("在", M_IN), ("外", M_OUT), ("近年", M_REC)):
    p1, p2, b0, sd = signflip_p(LAST, FB, m)
    p1o, p2o, b0o, sdo = signflip_p(LAST, ON, m)
    say(f"- {lab}: FIRST_B 片側 p {p1:.4f}／両側 {p2:.4f}（帰無 sd {sd:.4f}）・ON 片側 p {p1o:.4f}／両側 {p2o:.4f}")

# ============================================================ C 機構（引け固有か）
say("\n## C1 半時間プロファイルを**金のセッション終端まで延長**（c40b は 16:00 で打ち切り）")
slots = [(10, 30), (11, 0), (11, 30), (12, 0), (12, 30), (13, 0), (13, 30), (14, 0), (14, 30),
         (15, 0), (15, 30), (16, 0), (16, 30), (17, 0), (17, 30), (18, 30), (19, 0)]
prev_h, prev_m = 10, 0
H = {}
for (h, mi) in slots:
    cur = P(h, mi); pr = P(prev_h, prev_m)
    H[f"{h:02d}:{mi:02d}"] = (lg(cur) - lg(pr)) * 1e4
    prev_h, prev_m = h, mi
say("| スロット | NaN% (外) | 在 β(t) | 外 β(t) | 近年 β(t) |")
say("|---|---|---|---|---|")
Cout = {}
for k, v in H.items():
    nanp = np.mean(~np.isfinite(v[(yr >= 2021)])) * 100
    cells = []
    for lab, lo, hi in ERAS:
        m = np.isfinite(v) & np.isfinite(FB) & (FB != 0) & (yr >= lo) & (yr <= hi)
        o = ols(v[m], FB[m]); cells.append(f"{o['b']:+.4f} ({o['t']:+.2f}, n{o['n']})")
        if lab.startswith("外"): Cout[k] = o
    say(f"| {k} | {nanp:.1f}% | " + " | ".join(cells) + " |")

say("\n## C2 スロット族への多重検定補正（外・BH 0.05 と Holm）")
from math import erfc
def p2(t): return erfc(abs(t) / math.sqrt(2))
ks = [k for k in Cout if np.isfinite(Cout[k]["t"]) and Cout[k]["n"] >= 100]
ps = np.array([p2(Cout[k]["t"]) for k in ks]); order = np.argsort(ps); mN = len(ks)
bh_thr = np.nan
for i, oi in enumerate(order):
    if ps[oi] <= (i + 1) / mN * 0.05: bh_thr = ps[oi]
say(f"- 族 n {mN}（NaN 率の高いスロットを除く）・BH(0.05) 閾値 p ≤ {bh_thr if np.isfinite(bh_thr) else float('nan'):.5f}")
for i, oi in enumerate(order[:8]):
    k = ks[oi]
    say(f"  - {i+1}. {k}: t {Cout[k]['t']:+.2f}・p {ps[oi]:.2e}・BH 通過 {'YES' if np.isfinite(bh_thr) and ps[oi]<=bh_thr else 'no'}"
        f"・Holm 通過 {'YES' if ps[oi] <= 0.05/(mN-i) else 'no'}")

say("\n## C3 ON は残りの 1 日全体を予測するか（半時間あたりに直すと 16:00 は突出するか）")
for nm, (ha, ma), (hb, mb) in (("10:00→15:30（13 半時間）", (10, 0), (15, 30)),
                               ("10:00→16:00（12+1）", (10, 0), (16, 0)),
                               ("16:00→17:00（引け後 2 半時間）", (16, 0), (17, 0))):
    y = (lg(P(hb, mb)) - lg(P(ha, ma))) * 1e4
    for lab, lo, hi in (("外 2021-26H1", 2021, 2026),):
        m = np.isfinite(y) & np.isfinite(FB) & (FB != 0) & (yr >= lo) & (yr <= hi)
        o = ols(y[m], FB[m]); say(f"- {nm} ~ FIRST_B（{lab}）: {fo(o)}")

# ============================================================ D 経済
say("\n## D1 符号戦略の net（コスト 3 水準・c4 の観測値をハードコード）")
price = np.where(np.isfinite(p1530), p1530, np.nan)
COSTS = [("1× 0.16 USD（c4 中央値・c40 が使った値）", 0.16), ("観測 p90 0.22 USD", 0.22), ("**2× 0.32 USD**", 0.32)]
say("| セル | gross S bp/日 (t, 正%) | " + " | ".join(f"net {nm}" for nm, _ in COSTS) + " |")
say("|---|---|---|---|---|")
D1 = {}
for lab, m in (("在 2012-20", M_IN), ("外 2021-26H1", M_OUT), ("近年 2024-26H1", M_REC)):
    g = strat(FB, LAST, m)
    row = [f"{g['mean']:+.3f} (t {g['t']:+.2f}, {g['pos']*100:.0f}%, n{g['n']})"]
    for nm, c in COSTS:
        cb = c / price * 1e4
        s = strat(FB, LAST, m, cost_bp=cb)
        row.append(f"{s['mean']:+.3f} (t {s['t']:+.2f})")
        D1[(lab, c)] = s
    say(f"| {lab} | " + " | ".join(row) + " |")
say(f"- 外のコスト bp（0.16 USD 換算）: 中央値 {np.nanmedian((0.16/price*1e4)[M_OUT]):.3f} bp・"
    f"2021 {np.nanmedian((0.16/price*1e4)[M_OUT&(yr==2021)]):.3f}・2026H1 {np.nanmedian((0.16/price*1e4)[M_OUT&(yr==2026)]):.3f}")
say("- 【c40 の前向き条件 T4 を 外 のデータに当てる】net>0 ∧ t≥1.5: "
    + "・".join(f"{c} USD → net {D1[('外 2021-26H1', c)]['mean']:+.3f} t {D1[('外 2021-26H1', c)]['t']:+.2f} "
                f"{'通過' if (D1[('外 2021-26H1', c)]['mean']>0 and D1[('外 2021-26H1', c)]['t']>=1.5) else '**不通過**'}" for _, c in COSTS))

say("\n## D2 ドリフト交絡（新しい攻撃）: S は「予測」か「買い持ちのドリフト」か")
for lab, m in (("在 2012-20", M_IN), ("外 2021-26H1", M_OUT), ("近年 2024-26H1", M_REC)):
    mm = m & np.isfinite(LAST) & np.isfinite(FB) & (FB != 0)
    mL = LAST[mm].mean(); seL = LAST[mm].std(ddof=1) / math.sqrt(mm.sum())
    pfb = (FB[mm] > 0).mean()
    # 分解: E[sign(x)y] = E[y]·(2P(x>0)−1) + cov 部分
    drift_term = mL * (2 * pfb - 1)
    ydm = LAST - np.nan_to_num(np.where(mm, mL, np.nan))  # 窓内平均を除去（look-ahead・読みにだけ使う）
    sdm = strat(FB, np.where(mm, LAST - mL, np.nan), mm)
    say(f"- {lab}: mean(LAST) {mL:+.3f} bp (t {mL/seL:+.2f})・P(FIRST_B>0) {pfb*100:.1f}%・"
        f"ドリフト項 (2P−1)·mean(LAST) {drift_term:+.3f} bp／観測 S {strat(FB,LAST,mm)['mean']:+.3f} bp・"
        f"**S_demeaned {sdm['mean']:+.3f} (t {sdm['t']:+.2f})**")

say("\n## D3 プラセボ signal（外・gross と 2× net）")
FB5 = np.r_[np.full(5, np.nan), FB[:-5]]
ts_s, cl_s = load("US500")
Ps = lambda h, m: price_at(ts_s, cl_s, epoch_et(dates, h, m))
p16s = Ps(16, 0); p16sp = np.r_[np.nan, p16s[:-1]]
FBs = (lg(Ps(10, 0)) - lg(p16sp)) * 1e4
cb2 = 0.32 / price * 1e4
for nm, sig in (("本物 sign(FIRST_B)", FB), ("プラセボ① 5 日前の FIRST_B", FB5),
                ("プラセボ② US500 の FIRST_B の符号", FBs), ("プラセボ③ 常にロング", np.ones(N))):
    g = strat(sig, LAST, M_OUT); nn = strat(sig, LAST, M_OUT, cost_bp=cb2)
    say(f"- {nm}: gross {g['mean']:+.3f} (t {g['t']:+.2f}, n{g['n']})／2× net {nn['mean']:+.3f} (t {nn['t']:+.2f})")

say("\n## D4 年別 net（2× 0.32 USD）と年率（無レバ・1 日 1 往復・30 分保有）")
rows = []
for y0 in range(2021, 2027):
    m = M_OUT & (yr == y0); g = strat(FB, LAST, m); nn = strat(FB, LAST, m, cost_bp=cb2)
    n1 = strat(FB, LAST, m, cost_bp=0.16 / price * 1e4)
    rows.append((y0, g, n1, nn))
    say(f"- {y0}: gross {g['mean']:+.3f} bp/日 (t {g['t']:+.2f}, n{g['n']})・1× net {n1['mean']:+.3f}・2× net {nn['mean']:+.3f}"
        f"・年換算 2× {nn['mean']*g['n']/1e4*100:+.2f}%")
gO = strat(FB, LAST, M_OUT); nO = strat(FB, LAST, M_OUT, cost_bp=cb2)
if np.isfinite(gO["mean"]):
    say(f"- 外 全体: gross Sharpe（年率・252 日）{gO['mean']/gO['sd']*math.sqrt(252):+.2f}・2× net Sharpe {nO['mean']/nO['sd']*math.sqrt(252):+.2f}")

# ============================================================ 破壊条件の自動判定
say("\n## 破壊条件の機械判定（docstring の事前固定をそのまま当てる）")
o_out = ols(LAST[M_OUT], FB[M_OUT])
rep_ok = abs(o_out["b"] - 0.026) <= 0.003
a4_fail = sum(1 for k, o in A4t.items() if "原型" not in k and abs(o["t"]) < 2.0)
BA = (not rep_ok) or (a4_fail >= 3)
o_ex26 = ols(LAST[valid & (yr >= 2021) & (yr <= 2025)], FB[valid & (yr >= 2021) & (yr <= 2025)])
loyo_min = min(abs(o["t"]) for _, o, _ in loyo)
pw, _, _ = wild_cluster_p(LAST, FB, M_OUT, yr)
p1_out, _, _, _ = signflip_p(LAST, FB, M_OUT)
BB = ((abs(o_ex26["t"]) < 2.0 and o_ex26["b"] < 0.015) or (loyo_min < 2.0) or (pw > 0.05) or (p1_out >= 0.025))
post = [k for k in Cout if k >= "16:30" and np.isfinite(Cout[k]["t"]) and Cout[k]["n"] >= 100]
post_hit = [k for k in post if abs(Cout[k]["t"]) >= 2.0 and np.sign(Cout[k]["b"]) == np.sign(Cout["16:00"]["b"])]
bh16 = np.isfinite(bh_thr) and p2(Cout["16:00"]["t"]) <= bh_thr
BC = (len(post_hit) >= 2) or (not bh16)
d2 = D1[("外 2021-26H1", 0.32)]
sdm_out = strat(FB, np.where(M_OUT & np.isfinite(LAST) & np.isfinite(FB), LAST - LAST[M_OUT & np.isfinite(LAST) & np.isfinite(FB)].mean(), np.nan), M_OUT)
plac_best = max(strat(FB5, LAST, M_OUT)["mean"], strat(FBs, LAST, M_OUT)["mean"], strat(np.ones(N), LAST, M_OUT)["mean"])
BD = (d2["mean"] <= 0 or d2["t"] < 1.5) or (sdm_out["t"] < 1.5) or (plac_best >= 0.5 * gO["mean"])
say(f"- BREAK-A（人工物）: 複製 β {o_out['b']:+.4f}（±0.003 以内 {rep_ok}）・A4 で |t|<2 の変種 {a4_fail}/7 → **{'成立' if BA else '不成立'}**")
say(f"- BREAK-B（期間・推論）: ex-2026H1 β {o_ex26['b']:+.4f} t {o_ex26['t']:+.2f}・LOYO 最小|t| {loyo_min:.2f}・"
    f"wild cluster p(年) {pw:.4f}・符号反転 片側 p {p1_out:.4f} → **{'成立' if BB else '不成立'}**")
say(f"- BREAK-C（機構 T2）: 16:00 以降で同符号 |t|≥2 のスロット {post_hit}・16:00 の BH 通過 {bh16} → **{'成立' if BC else '不成立'}**")
say(f"- BREAK-D（経済 T3/T4）: 2× net {d2['mean']:+.3f} (t {d2['t']:+.2f})・S_demeaned t {sdm_out['t']:+.2f}・"
    f"最良プラセボ {plac_best:+.3f} vs gross {gO['mean']:+.3f} → **{'成立' if BD else '不成立'}**")
verdict = "broken" if (BA or BB) else ("T2 broken / T1 survived" if BC and not BD else ("T3/T4 broken（受取り不能）" if BD else "survived"))
say(f"- **判定語（事前の規則から機械的に）: {verdict}**" + ("（BREAK-C も成立）" if BC and (BA or BB or BD) else ""))

say(f"\n- 実行 {time.time()-T0:.1f} s・seed {SEED}・bootstrap {NB}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("->", OUT)
