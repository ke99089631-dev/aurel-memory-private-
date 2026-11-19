# -*- coding: utf-8 -*-
"""
[反証レーン] 2026-11-19 21:30 — 対象: cycle54 (18:50) SGE ベンチマーク・オークション

PROMOTED.md は空＝昇格候補ゼロ。H_DIP は AM/PM とも null・H_REB PM も null＝規則上壊す余地なし。
攻撃するのは c54 が **肯定形で登記した 3 つ**（うち T1 は c54 自身が「最も重大な反証 (i)」で
「市場の事実として相当に強く」と書いた＝本レーンが裁くべき最大の標的）:

  T1「2016-20 の 4.7 年に SGE オークション直後 5 分 +0.5 bp が有った」
     根拠 = ①AM P1 生 +0.516 (t 5.40)・隣接超過 +0.521 (t 4.83)・DiD P1−P0 +0.415 (t 2.72)
            ②PM P1 生 +0.504 (t 3.84)・超過 +0.543 (t 4.00)・DiD +0.655 (t 3.45)
            ③「2 つの独立な時計が同じ 2016-20 に同じ大きさで点灯＝偶然なら 2 本同時は確率 ≈0.3%」
            ④2021+ は半減〜消滅・近年 ≈0 ＝ ㊶ 型「2010 年代に有り 2021+ で消えた」6 例目候補
  T2「c50 の LBMA 直前 5 分の沈み（−0.65〜−1.34 bp・t −5.7〜−7.9）は
      ベンチマーク・オークション一般ではなく **ロンドン固有**（ディーラーの事前捌き or bid 人工物）」
     根拠 = SGE 2 会場の PRE 足が P1 +0.260（符号逆）/−0.097・P2 −0.012/−0.039（MDE 0.23〜0.32）
  T3「ゲート ㉛ の P1 正（side 符号つき Δcl +0.0181R・t +2.01）は
      **BUY 比 56% × +0.78 bp の別名**＝方向無差別の直後の正が side 符号で打ち消し損なったもの」

c54 の決着不能点（bid 1 社・XAUUSD は SGE 現物 RMB の測定点でない・XAU ask M1【要取得】）には寄らない。
npz の数字を全部そのまま受け入れ、**family 校正・制度日付の帰属・AM/PM の独立性・年次層・推定子の頑健性**だけで壊しに行く。

=== 事前固定（私の攻撃条件・走る前に確定・方法論候補 72/75 に従い 条件/観測/判定 を 1 行ずつ印字） ===
A  複製: c54/c54b の 20 セル（AM/PM × P0/P1/P2/近年 × 生 PRE/生 POST/超過 POST）を ±0.002 bp で再現。
   18/20 未満なら以降の攻撃は無効（私の読込が違う）＝ INCONCLUSIVE で終える。

B  【family 校正・最大の攻撃】c54 の family は「判定 4 セル＋プラセボ 4 時刻」。真の探索空間は
   **UTC 1 日の全 288 スロット**（「どこかの 5 分足が点灯する」の母数）。全 288 スロットで P1 の
   隣接超過 t を計算し、02:15／06:15 の順位と、オークション以外のスロットの t 分布を出す。
   BREAK-B1: オークション 2 枠を除く非オークション・スロットのうち t ≥ +2.72（c54 の DiD t）の
             割合 f が **f ≥ 0.05**（名目片側 0.33% の 15 倍以上）→「2 本同時 ≈0.3%」は校正されていない。
   BREAK-B2: 非オークション・スロットの max t ≥ **+4.83**（AM 超過の t）→ 02:15 は最大でない。
   BREAK-B3: 02:15 の順位が非オークション 276 枠中 **4 位以下**（=3 枠以上が上）→ 局在していない。
   （アジア帯 UTC 22:00–08:00 の 120 枠に限った版も印字＝母数の取り方に依存しないか）

C  【「2 つの独立な時計」の独立性】同一日の AM 超過と PM 超過の対応相関。
   BREAK-C1: P1 で corr(AM,PM) の |t| ≥ 2 → 2 本は独立でない＝③の確率計算が壊れる。
   BREAK-C2: 日ペア保存ブートストラップ 4000 回で「AM DiD t≥2.72 ∧ PM DiD t≥3.45」の
             同時 p を直接推定（permute 版）。推定 p が **≥ 0.03**（0.3% の 10 倍）→ ③は壊れる。
   年次 AM 超過 vs PM 超過 の相関（n=17）も印字（機構が共通なら年次で揃うはず）。

D  【制度日付の帰属＝ばらし（sup-t）】2016-04-19 が特別かを、候補分割日を月次グリッドで走らせて検定。
   各候補 d（2012-01〜2021-06）につき 前 56 か月 vs 後 56 か月 の超過 DiD Welch t を 02:15／06:15 で計算。
   BREAK-D1: t ≥ 2.72 となる候補 d の割合が **≥ 0.20** → 任意の分割日でも出る＝制度日付への帰属が崩れる。
   BREAK-D2: argmax d が 2016-04 から **18 か月以上** 離れる → 構造変化点は開始日でない。

E  【年次層＝「2021+ で消えた」(㊶) の検定】年平均超過で P1 全年（2016-20）vs P2 全年（2021-25）の
   Mann-Whitney（両側・正確分布 n=5,5）。
   BREAK-E1: p ≥ 0.10 → 年レベルでは P1 と P2 を分離できていない＝「消えた優位 6 例目」の分類は支持されない。
   （2026H1 は部分年なので除く版と含む版の両方を印字）

F  【P0 ベースラインの脆さ】PM の DiD（+0.655・t 3.45）は P0 が負（−0.112・2013 年 −0.85 t −2.3）に依存。
   P0 の 1 年ずつ抜く LODO。BREAK-F1: いずれか 1 年を抜くと PM DiD t が事前固定閾値 **2.24 未満** → 脆い。
   AM 側も同形で印字。

G  【推定子の頑健性】P1 AM 超過 +0.521 を 日ブートストラップ CI・10% 刈り込み平均・中央値・
   winsorize(1%)・年 LODO・符号検定で割る。
   BREAK-G1: 10% 刈り込み平均 < **+0.26**（点推定の半分）または t < 2 → 少数の大当たりに乗っている。

H  【コスト倍】02:15 足を丸ごと取る仮想取引（足頭→足尾）の 往復スプレッド 1 倍・2 倍 後の純 bp。
   CONFIRM-H1: 1 倍で既に負 → c54 の「受取り不可」は壊せない（＝c54 の結論が強くなる側）。

I  【ふるいの感度】非 flat 閾値 ∈ {4,6,8,10,12,13}・隣接窓 ∈ {±15,±30,±60} 分。
   BREAK-I1: P1 AM 超過が ±50% を超えて動く、または t<2 になる設定が有る → 推定子依存。

J  【プラセボ／ランダム化】(i) 期間ラベルの日単位置換 4000 回 → DiD t の帰無分布
   (ii) スロット・ランダム化（毎日ランダムな 1 スロットを「オークション」とする）4000 回
   BREAK-J1: 観測 DiD t が置換分布の上側 **5% 内に入らない** → 偶然で説明できる。

K  【T2 への攻撃＝c50 の沈みは「会場」でなく「時計」の人工物か】
   c50 の PRE 足は London 10:25／14:55 ＝ **分 :25 と :55**。London 帯（UTC 07–16）の
   分-of-hour 12 ビン平均 r を期間別に印字。
   BREAK-K1: :25 と :55 が 12 ビンの最も負の 2 つに入る（期間 ≥2 つで）→ 沈みは半時間周期の
             時計人工物＝「ロンドンのディーラー慣行」への帰属が壊れる（「一般でない」は残る）。
   加えて T2 の同値検定（TOST）: SGE の PRE が排除できる沈みの最大の大きさを印字。
   BREAK-K2: P2 で **−0.33 bp（c50 の下限 −0.65 の半分）が 95% で排除できない** →
             「沈みが無い」は「半分の沈みが無い」までしか言えない（c54 の留保 (ii) の定量化）。

L  【survivorship】AM 窓で落ちた日のうち POST 足自体が有限な日の生 POST r を、残った日と比較（Welch・MW）。
   BREAK-L1: |t| ≥ 2 → ふるいが価格依存＝落とし方が結果を作っている。

M  【穴（19 か所）の影響】13 足窓が ts の穴を跨ぐ事象を除いた版で B/G を再計算（印字のみ）。

seed 20261119。読取り専用・npz と c54 の出力のみ・MT5 なし・scan なし・発注なし。
"""
import os, sys, math, time, json
import numpy as np, pandas as pd
from itertools import combinations

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c54_sge_result.md")
SEED = 20261119; rng = np.random.default_rng(SEED)
L = []
def say(s=""):
    print(s, flush=True); L.append(s)

BREAKS = []
def brk(tag, cond_text, obs_text, broken):
    """方法論候補 75: 条件/観測/判定 を別フィールドで印字（判定語は必ず boolean から）"""
    say(f"- [{tag}] 条件: {cond_text}")
    say(f"  - 観測: {obs_text}")
    say(f"  - 判定: {'BROKEN' if broken else 'not broken'}")
    BREAKS.append((tag, bool(broken)))

say(f"# [REFUTE c54] SGE ベンチマーク・オークション（02:15／06:15 UTC・2016-04-19 開始）を壊しに行く — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c54_sge.py)")

# ================= load: replicate c54's return series exactly, then put on a full calendar grid =========
z = np.load(os.path.join(MAC, "XAU_m5_close.npz"))
ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r_raw = np.zeros(len(lc)); r_raw[1:] = np.diff(lc); r_raw *= 1e4   # bp
flat_raw = (r_raw == 0)
holes = np.flatnonzero(np.diff(ts) != 300)
say(f"- npz {len(ts)} 本 {pd.to_datetime(ts[0],unit='s',utc=True)}〜{pd.to_datetime(ts[-1],unit='s',utc=True)}・格子の穴 {len(holes)}・flat 全体 {flat_raw.mean()*100:.1f}%")

# full regular grid, 288 bars/day, starting at a day boundary
t0 = (ts[0] // 86400) * 86400
t1 = ((ts[-1] // 86400) + 1) * 86400 - 300
N = (t1 - t0) // 300 + 1
ND = N // 288
assert N % 288 == 0, (N, ND)
G = np.full(N, np.nan); FL = np.zeros(N, dtype=bool); PRESENT = np.zeros(N, dtype=bool)
gi = (ts - t0) // 300
G[gi] = r_raw; FL[gi] = flat_raw; PRESENT[gi] = True
# bars whose own return spans a grid hole (first bar after a gap)
SPAN = np.zeros(N, dtype=bool); SPAN[gi[holes + 1]] = True
ORIG_OF_GRID = np.full(N, -1, dtype=np.int64); ORIG_OF_GRID[gi] = np.arange(len(ts))
day_start = t0 + np.arange(ND) * 288 * 300
dday = pd.to_datetime(day_start, unit="s", utc=True)
dwd = dday.weekday.to_numpy(); dyear = dday.year.to_numpy()
dnorm = pd.DatetimeIndex(dday.tz_localize(None))
say(f"- 整格子 {N} スロット = {ND} 日 × 288・存在 {PRESENT.mean()*100:.1f}%（欠落 = 週末/停止）")

Gm = G.reshape(ND, 288); FLm = FL.reshape(ND, 288); PRm = PRESENT.reshape(ND, 288); SPm = SPAN.reshape(ND, 288)

def S(h, m): return h * 12 + m // 5
AMS, PMS = S(2, 15), S(6, 15)

# ---------- generic estimator: for slot s, raw bar / pre bar / neighbour-excess, with c54b's filter -----
def slot_series(s, half=6, nf_min=8, exclude_span=False):
    """Return (ok, raw_post, raw_pre, ex_post, ex_pre) arrays of length ND, using a continuous
    +/-half window centred on slot s (may cross midnight), c54b's neighbour set (window minus {s-1,s})."""
    base = np.arange(ND) * 288 + s
    offs = np.arange(-half, half + 1)
    idx = base[:, None] + offs[None, :]
    good_row = (idx[:, 0] >= 0) & (idx[:, -1] < N)
    idx_c = np.clip(idx, 0, N - 1)
    W = G[idx_c]; WF = FL[idx_c]; WP = PRESENT[idx_c]; WS = SPAN[idx_c]
    ok = good_row & WP.all(axis=1) & (((~WF) & WP).sum(axis=1) >= nf_min) & (dwd <= 4)
    if exclude_span:
        ok = ok & (~WS.any(axis=1))
    cpost = half; cpre = half - 1
    nb = [j for j in range(2 * half + 1) if j not in (cpre, cpost)]
    nbm = W[:, nb].mean(axis=1)
    raw_post = W[:, cpost].copy(); raw_pre = W[:, cpre].copy()
    ex_post = raw_post - nbm; ex_pre = raw_pre - nbm
    for a in (raw_post, raw_pre, ex_post, ex_pre):
        a[~ok] = np.nan
    return ok, raw_post, raw_pre, ex_post, ex_pre

def stat(x):
    x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return dict(n=n, m=np.nan, se=np.nan, t=np.nan, mde=np.nan, med=np.nan, neg=np.nan, z=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); t = m / se if se > 0 else np.nan
    nz = (x != 0).sum(); zs = ((x < 0).sum() - nz / 2) / math.sqrt(nz / 4) if nz > 0 else np.nan
    return dict(n=n, m=m, se=se, t=t, mde=2 * se, med=np.median(x), neg=(x < 0).mean(), z=zs)

def welch(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3: return np.nan, np.nan
    d = a.mean() - b.mean()
    return d, d / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))

P0 = (dnorm >= "2010-01-01") & (dnorm <= "2016-04-18")
P1 = (dnorm >= "2016-04-19") & (dnorm <= "2020-12-31")
P2 = (dnorm >= "2021-01-01")
PR = (dnorm >= "2024-01-01")
PERS = [("P0", P0), ("P1", P1), ("P2", P2), ("近年", PR)]

okAM, rpoAM, rprAM, expoAM, exprAM = slot_series(AMS)
okPM, rpoPM, rprPM, expoPM, exprPM = slot_series(PMS)
say(f"- AM 窓 OK {int(okAM.sum())} 日（c54: 4242）・PM 窓 OK {int(okPM.sum())} 日（c54: 4243）"
    f"・P0/P1/P2/近年 = {int((P0&okAM).sum())}/{int((P1&okAM).sum())}/{int((P2&okAM).sum())}/{int((PR&okAM).sum())}（c54: 1614/1215/1413/641）")

# ===================================== A. replication ==================================================
say("\n## A 複製（c54 主走 + c54b の 20 セル・許容 ±0.002 bp）")
REF = {
    ("AM", "P0", "raw_pre"): +0.138, ("AM", "P1", "raw_pre"): +0.260, ("AM", "P2", "raw_pre"): -0.012, ("AM", "近年", "raw_pre"): -0.276,
    ("AM", "P0", "raw_post"): +0.235, ("AM", "P1", "raw_post"): +0.516, ("AM", "P2", "raw_post"): +0.267, ("AM", "近年", "raw_post"): +0.048,
    ("PM", "P0", "raw_pre"): +0.076, ("PM", "P1", "raw_pre"): -0.097, ("PM", "P2", "raw_pre"): -0.039,
    ("PM", "P0", "raw_post"): -0.061, ("PM", "P1", "raw_post"): +0.504, ("PM", "P2", "raw_post"): +0.095,
    ("AM", "P0", "ex_post"): +0.106, ("AM", "P1", "ex_post"): +0.521, ("AM", "P2", "ex_post"): +0.284, ("AM", "近年", "ex_post"): +0.091,
    ("PM", "P1", "ex_post"): +0.543, ("PM", "P2", "ex_post"): +0.095,
}
series = {("AM", "raw_pre"): rprAM, ("AM", "raw_post"): rpoAM, ("AM", "ex_post"): expoAM,
          ("PM", "raw_pre"): rprPM, ("PM", "raw_post"): rpoPM, ("PM", "ex_post"): expoPM}
hit = 0
for (clk, per, kind), ref in sorted(REF.items()):
    msk = dict(PERS)[per]
    s = stat(series[(clk, kind)][msk])
    ok_ = abs(s["m"] - ref) <= 0.002
    hit += ok_
    say(f"- {clk} {per} {kind}: 私 {s['m']:+.3f} (t {s['t']:+.2f}, n {s['n']}) vs c54 {ref:+.3f} → {'一致' if ok_ else '**不一致**'}")
say(f"- **複製 {hit}/20**")
if hit < 18:
    say("- 複製不足 → 以降の攻撃は無効（INCONCLUSIVE）"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); sys.exit(0)

# ===================================== B. 288-slot family calibration ==================================
say("\n## B family 校正 — UTC 1 日の全 288 スロットで P1 の隣接超過 t を計算（c54 の family は 4 セル + プラセボ 4 時刻）")
tP1 = np.full(288, np.nan); mP1 = np.full(288, np.nan); nP1 = np.zeros(288, int)
tDiD = np.full(288, np.nan); mDiD = np.full(288, np.nan)
tP0 = np.full(288, np.nan); tP2 = np.full(288, np.nan)
for s in range(288):
    ok, _, _, ex, _ = slot_series(s)
    s1 = stat(ex[P1]); tP1[s] = s1["t"]; mP1[s] = s1["m"]; nP1[s] = s1["n"]
    tP0[s] = stat(ex[P0])["t"]; tP2[s] = stat(ex[P2])["t"]
    d, t = welch(ex[P1], ex[P0]); mDiD[s] = d; tDiD[s] = t
usable = np.isfinite(tP1) & (nP1 >= 200)
say(f"- 使えるスロット {int(usable.sum())}/288（n≥200 日・窓が存在）")
AUX = np.zeros(288, bool); AUX[[AMS, PMS]] = True
nonauc = usable & (~AUX)

def rank_of(arr, s, pool):
    return int((arr[pool] >= arr[s]).sum()) + (0 if pool[s] else 1)

say(f"- 02:15: P1 超過 t **{tP1[AMS]:+.2f}** (m {mP1[AMS]:+.3f})・DiD t **{tDiD[AMS]:+.2f}**"
    f"／06:15: P1 t **{tP1[PMS]:+.2f}** (m {mP1[PMS]:+.3f})・DiD t **{tDiD[PMS]:+.2f}**")
pool = nonauc
tn = tP1[pool]; dn = tDiD[pool]
say(f"- 非オークション {int(pool.sum())} 枠の P1 超過 t: 平均 {tn.mean():+.2f}・sd {tn.std(ddof=1):.2f}"
    f"・max {tn.max():+.2f} (スロット {int(np.flatnonzero(pool)[np.argmax(tn)])} = {int(np.flatnonzero(pool)[np.argmax(tn)])//12:02d}:{(int(np.flatnonzero(pool)[np.argmax(tn)])%12)*5:02d})"
    f"・min {tn.min():+.2f}")
say(f"- 非オークション枠の DiD t: 平均 {dn.mean():+.2f}・sd {dn.std(ddof=1):.2f}・max {dn.max():+.2f}")
top = np.flatnonzero(usable)[np.argsort(-tP1[usable])][:12]
say("- P1 超過 t 上位 12 スロット: " + " ".join(f"{s//12:02d}:{(s%12)*5:02d}({tP1[s]:+.1f})" + ("★" if AUX[s] else "") for s in top))
topd = np.flatnonzero(usable)[np.argsort(-tDiD[usable])][:12]
say("- DiD(P1−P0) t 上位 12 スロット: " + " ".join(f"{s//12:02d}:{(s%12)*5:02d}({tDiD[s]:+.1f})" + ("★" if AUX[s] else "") for s in topd))

f_272 = float((dn >= 2.72).mean()); f_272_p1 = float((tn >= 2.72).mean())
brk("BREAK-B1", "非オークション枠で DiD t ≥ +2.72 の割合 f ≥ 0.05（名目片側 0.33% の 15 倍）",
    f"f(DiD) = {f_272*100:.1f}% ({int((dn>=2.72).sum())}/{int(pool.sum())})・f(P1 生 t) = {f_272_p1*100:.1f}%"
    f"・名目期待 0.33% → 実測は {f_272/0.0033:.1f}×", f_272 >= 0.05)
brk("BREAK-B2", "非オークション枠の P1 超過 max t ≥ +4.83（02:15 の値）",
    f"max t = {tn.max():+.2f}（02:15 は {tP1[AMS]:+.2f}）", tn.max() >= 4.83)
r_am = rank_of(tP1, AMS, usable); r_pm = rank_of(tP1, PMS, usable)
brk("BREAK-B3", "02:15 の P1 超過 t 順位が使えるスロット中 4 位以下",
    f"02:15 順位 {r_am}/{int(usable.sum())}・06:15 順位 {r_pm}/{int(usable.sum())}", r_am >= 4)
asia = usable & np.isin(np.arange(288), list(range(S(22, 0), 288)) + list(range(0, S(8, 0) + 1)))
asia_na = asia & (~AUX)
say(f"- アジア帯限定（UTC 22:00–08:00・{int(asia_na.sum())} 枠）: max P1 t {tP1[asia_na].max():+.2f}"
    f"・DiD t≥2.72 割合 {float((tDiD[asia_na]>=2.72).mean())*100:.1f}%・02:15 順位 {rank_of(tP1, AMS, asia)}/{int(asia.sum())}")

# ===================================== C. AM/PM independence ===========================================
say("\n## C 「2 つの独立な時計」— 独立性の検定")
both = okAM & okPM
for nm, msk in PERS:
    m = msk & both
    a = expoAM[m]; b = expoPM[m]
    g = np.isfinite(a) & np.isfinite(b); a, b = a[g], b[g]
    rho = np.corrcoef(a, b)[0, 1]; n = len(a)
    tr = rho * math.sqrt((n - 2) / max(1e-12, 1 - rho ** 2))
    say(f"- {nm} 同一日 corr(AM 超過, PM 超過) = {rho:+.4f} (t {tr:+.2f}, n {n})")
    if nm == "P1": rho1, tr1, n1 = rho, tr, n
brk("BREAK-C1", "P1 の 同一日 corr(AM 超過, PM 超過) の |t| ≥ 2（＝2 本は独立でない）",
    f"P1 ρ {rho1:+.4f} (t {tr1:+.2f}, n {n1})", abs(tr1) >= 2)

# year-level agreement of the two clocks
yrs = sorted(set(dyear[okAM]))
yam = []; ypm = []
for y in yrs:
    m = (dyear == y)
    sa = stat(expoAM[m & okAM]); sp = stat(expoPM[m & okPM])
    if sa["n"] > 50 and sp["n"] > 50: yam.append(sa["m"]); ypm.append(sp["m"])
yam = np.array(yam); ypm = np.array(ypm)
ry = np.corrcoef(yam, ypm)[0, 1]
say(f"- 年次 AM 超過 vs PM 超過 の相関 ρ {ry:+.3f} (n {len(yam)} 年)"
    f"（機構が共通なら年次で揃うはず・揃わなければ『2 本同時』は機構の証拠でなく偶然の一致）")

# C2: joint-significance null by day-paired label permutation (preserves AM/PM same-day pairing)
NPERM = 4000
mboth = both & (P0 | P1)
A = expoAM[mboth]; B = expoPM[mboth]; lab = P1[mboth]
g = np.isfinite(A) & np.isfinite(B); A, B, lab = A[g], B[g], lab[g]
n1_ = int(lab.sum()); nn = len(lab)
obs_ta = welch(A[lab], A[~lab])[1]; obs_tb = welch(B[lab], B[~lab])[1]
say(f"- 日ペア保存の母数 n {nn}（P1 {n1_}）・観測 DiD t: AM {obs_ta:+.2f}・PM {obs_tb:+.2f}（c54: +2.72／+3.45）")
cnt_a = cnt_b = cnt_both = 0
for _ in range(NPERM):
    p = rng.permutation(nn); m1 = np.zeros(nn, bool); m1[p[:n1_]] = True
    ta = welch(A[m1], A[~m1])[1]; tb = welch(B[m1], B[~m1])[1]
    a_hit = ta >= 2.72; b_hit = tb >= 3.45
    cnt_a += a_hit; cnt_b += b_hit; cnt_both += (a_hit and b_hit)
pa = cnt_a / NPERM; pb = cnt_b / NPERM; pboth = cnt_both / NPERM
say(f"- 置換 {NPERM} 回（日ペア保存・期間ラベルのみ入替）: P(AM t≥2.72) {pa*100:.2f}%"
    f"・P(PM t≥3.45) {pb*100:.2f}%・**P(同時) {pboth*100:.2f}%**（独立なら積 {pa*pb*100:.3f}%）")
brk("BREAK-C2", "日ペア保存置換で推定した同時 p ≥ 0.03（c54 の ≈0.3% の 10 倍）",
    f"同時 p = {pboth*100:.2f}%（c54 主張 ≈0.3%）", pboth >= 0.03)

# the honest family-wide version of the joint claim: how often do ANY two usable slots co-light?
co = int(((tDiD[nonauc] >= 2.72)).sum())
npool = int(nonauc.sum())
say(f"- family 版の『2 本同時』: 非オークション {npool} 枠のうち DiD t≥2.72 は {co} 枠 → "
    f"任意の 2 枠が同時に点灯する組は C({co},2) = {co*(co-1)//2} 通り存在（『2 本同時は ≈0.3%』は "
    f"2 枠だけを見た場合の確率で、288 枠から 2 枠を選べる探索では同時点灯は {'珍しくない' if co >= 10 else 'なお珍しい'}）")

# ===================================== D. breakpoint sup-t ============================================
say("\n## D 制度日付（2016-04-19）への帰属 — 候補分割日を月次で走らせる sup-t（前 56 か月 vs 後 56 か月）")
W = 56  # months, 4.7y
cands = pd.period_range("2012-01", "2021-06", freq="M")
res = {}
for lab_, ex, ok in [("AM 02:15", expoAM, okAM), ("PM 06:15", expoPM, okPM)]:
    tt = []; dd = []
    for p in cands:
        d0 = p.to_timestamp(); dm = (d0 - pd.DateOffset(months=W)); dp = (d0 + pd.DateOffset(months=W))
        pre = (dnorm >= dm) & (dnorm < d0) & ok
        post = (dnorm >= d0) & (dnorm < dp) & ok
        if pre.sum() < 300 or post.sum() < 300: tt.append(np.nan); dd.append(np.nan); continue
        _d, _t = welch(ex[post], ex[pre]); tt.append(_t); dd.append(_d)
    tt = np.array(tt); dd = np.array(dd); fin = np.isfinite(tt)
    i_at = list(cands).index(pd.Period("2016-04", "M"))
    imax = int(np.nanargmax(tt))
    frac = float((tt[fin] >= 2.72).mean())
    off = abs((cands[imax] - pd.Period("2016-04", "M")).n)
    pct = float((tt[fin] <= tt[i_at]).mean())
    say(f"- {lab_}: 候補 {int(fin.sum())} か月・2016-04 の t {tt[i_at]:+.2f} (Δ {dd[i_at]:+.3f})"
        f"・**候補分布中の分位 {pct*100:.0f}%**"
        f"・max t {tt[imax]:+.2f} @ {cands[imax]}（2016-04 から {off} か月）"
        f"・t≥2.72 の割合 {frac*100:.1f}%・t の 95 パーセンタイル {np.nanpercentile(tt,95):+.2f}")
    res[lab_] = (tt[i_at], tt[imax], cands[imax], frac, off, pct)
    # print the whole curve coarsely (every 6 months) so the shape is visible
    say("  - 曲線（6 か月刻み・t）: " + " ".join(f"{cands[i]}:{tt[i]:+.1f}" for i in range(0, len(cands), 6) if np.isfinite(tt[i])))
fa = res["AM 02:15"][3]; fp = res["PM 06:15"][3]
brk("BREAK-D1", "任意の候補分割日でも DiD t≥2.72 が出る割合 ≥ 0.20（AM または PM）",
    f"AM {fa*100:.1f}%・PM {fp*100:.1f}%", (fa >= 0.20) or (fp >= 0.20))
oa = res["AM 02:15"][4]; op = res["PM 06:15"][4]
brk("BREAK-D2", "sup-t の argmax が 2016-04 から 18 か月以上 離れる（AM かつ PM）",
    f"AM argmax {res['AM 02:15'][2]}（{oa} か月）・PM argmax {res['PM 06:15'][2]}（{op} か月）",
    (oa >= 18) and (op >= 18))
qa = res['AM 02:15'][5]; qp = res['PM 06:15'][5]
brk("BREAK-D3", "整合窓（前 56 か月 vs 後 56 か月）での 2016-04 の DiD t が候補分割日分布の上側 25% に入らない（AM または PM）",
    f"AM 分位 {qa*100:.0f}%（t {res['AM 02:15'][0]:+.2f}）・PM 分位 {qp*100:.0f}%（t {res['PM 06:15'][0]:+.2f}）"
    f"／c54 は P0 全 76 か月を比較対象にしていた（AM t +2.72）",
    (qa < 0.75) or (qp < 0.75))

# ===================================== E. year strata / the "vanished" claim ===========================
say("\n## E 年次層 — 「2021+ で半減〜消滅（㊶ 型・消えた優位 6 例目）」の検定")
def year_means(ex, ok, y0, y1):
    out = []
    for y in range(y0, y1 + 1):
        s = stat(ex[(dyear == y) & ok])
        if s["n"] > 50: out.append((y, s["m"], s["t"], s["n"]))
    return out
for lab_, ex, ok in [("AM", expoAM, okAM), ("PM", expoPM, okPM)]:
    ys = year_means(ex, ok, 2010, 2026)
    say(f"- {lab_} 年別超過: " + " ".join(f"{y} {m:+.2f}({t:+.1f})" for y, m, t, n in ys))
    a = [m for y, m, t, n in ys if 2016 <= y <= 2020]
    b = [m for y, m, t, n in ys if 2021 <= y <= 2025]
    b26 = [m for y, m, t, n in ys if 2021 <= y <= 2026]
    # exact Mann-Whitney two-sided for small n
    def mw_p(a, b):
        na, nb = len(a), len(b); allv = a + b
        ra = sum(sorted(allv).index(v) + 1 for v in a)  # ties unlikely in floats
        U = ra - na * (na + 1) / 2
        # exact null by enumeration
        idx = list(range(na + nb)); cnt = 0; tot = 0
        sv = sorted(allv)
        rank = {v: sv.index(v) + 1 for v in allv}
        for comb in combinations(idx, na):
            rr = sum(rank[allv[i]] for i in comb); UU = rr - na * (na + 1) / 2
            tot += 1
            if abs(UU - na * nb / 2) >= abs(U - na * nb / 2): cnt += 1
        return U, cnt / tot
    U, p = mw_p(a, b); U2, p2 = mw_p(a, b26)
    say(f"  - P1 全年 {['%+.2f'%v for v in a]} (平均 {np.mean(a):+.3f}) vs P2 全年 2021-25 {['%+.2f'%v for v in b]} (平均 {np.mean(b):+.3f})"
        f" → Mann-Whitney U {U:.0f}・**正確両側 p {p:.3f}**")
    say(f"  - 2026H1 を含めた P2 {['%+.2f'%v for v in b26]} (平均 {np.mean(b26):+.3f}) → p {p2:.3f}")
    # how many P2 years exceed the P1 median?
    medp1 = float(np.median(a)); exc = sum(1 for v in b if v > medp1)
    say(f"  - P1 の年中央値 {medp1:+.3f} を上回る P2 年 {exc}/{len(b)}")
    if lab_ == "AM": pAM_mw, pAM_mw26 = p, p2
    else: pPM_mw, pPM_mw26 = p, p2
brk("BREAK-E1", "年平均超過の P1(2016-20) vs P2(2021-25) Mann-Whitney 正確 p ≥ 0.10（AM）＝年レベルで分離できない",
    f"AM p {pAM_mw:.3f}（2026H1 込み {pAM_mw26:.3f}）・PM p {pPM_mw:.3f}（込み {pPM_mw26:.3f}）", pAM_mw >= 0.10)

# ===================================== F. P0 baseline fragility (LODO on the comparator) ==============
say("\n## F P0 ベースラインの脆さ — P0 の 1 年ずつ抜いて DiD を再計算（PM の +0.655 は P0 の負に依存）")
for lab_, ex, ok in [("AM", expoAM, okAM), ("PM", expoPM, okPM)]:
    base_d, base_t = welch(ex[P1 & ok], ex[P0 & ok])
    rows = []
    for y in range(2010, 2017):
        m0 = P0 & ok & (dyear != y)
        if m0.sum() < 300: continue
        d_, t_ = welch(ex[P1 & ok], ex[m0]); rows.append((y, d_, t_))
    worst = min(rows, key=lambda z_: z_[2])
    say(f"- {lab_} DiD 全 P0 {base_d:+.3f} (t {base_t:+.2f})・P0 から年を 1 つ抜く: "
        + " ".join(f"−{y} {t_:+.2f}" for y, d_, t_ in rows)
        + f" → 最小 t {worst[2]:+.2f}（−{worst[0]}）")
    if lab_ == "PM": pm_worst = worst
    else: am_worst = worst
brk("BREAK-F1", "P0 から 1 年抜くと PM の DiD t が 事前固定閾値 2.24 を下回る",
    f"PM 最小 t {pm_worst[2]:+.2f}（{pm_worst[0]} 年を抜いた時）・AM 最小 t {am_worst[2]:+.2f}（{am_worst[0]}）",
    pm_worst[2] < 2.24)

# ===================================== G. estimator robustness on P1 AM ===============================
say("\n## G P1 AM 超過 +0.521 の頑健性（刈り込み・中央値・ブートストラップ・年 LODO・符号）")
x = expoAM[P1 & okAM]; x = x[np.isfinite(x)]
s = stat(x)
say(f"- 素: m {s['m']:+.4f} (t {s['t']:+.2f}, n {s['n']}, MDE {s['mde']:.3f})・中央値 {s['med']:+.4f}"
    f"・下落足 {s['neg']*100:.1f}%・符号 z {s['z']:+.2f}")
def trimmed(x, q):
    lo, hi = np.percentile(x, [q, 100 - q]); y = x[(x >= lo) & (x <= hi)]
    sy = stat(y); return sy
for q in (1, 5, 10):
    sy = trimmed(x, q); say(f"- {q}% 刈り込み平均 {sy['m']:+.4f} (t {sy['t']:+.2f}, n {sy['n']})")
tr10 = trimmed(x, 10)
w = x.copy(); lo, hi = np.percentile(x, [1, 99]); w = np.clip(w, lo, hi); sw = stat(w)
say(f"- winsorize 1%: {sw['m']:+.4f} (t {sw['t']:+.2f})")
bs = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(4000)])
say(f"- 日ブートストラップ 4000: 95% CI [{np.percentile(bs,2.5):+.4f}, {np.percentile(bs,97.5):+.4f}]・P(≤0) {float((bs<=0).mean())*100:.2f}%")
lod = []
for y in range(2016, 2021):
    sy = stat(expoAM[P1 & okAM & (dyear != y)]); lod.append((y, sy["m"], sy["t"]))
say("- 年 LODO（P1 内）: " + " ".join(f"−{y} {m:+.3f}({t:+.1f})" for y, m, t in lod)
    + f" → 符号反転 {sum(1 for _,m,_ in lod if m<=0)}/5・t<2 {sum(1 for _,_,t in lod if t<2)}/5")
# single-day influence
k = 5; srt = np.argsort(-np.abs(x))
say(f"- 絶対値上位 {k} 日を抜く: {stat(np.delete(x, srt[:k]))['m']:+.4f} (t {stat(np.delete(x, srt[:k]))['t']:+.2f})"
    f"・上位 {k} 日の値 {['%+.1f'%v for v in x[srt[:k]]]}")
brk("BREAK-G1", "10% 刈り込み平均 < +0.26（点推定の半分）または t < 2",
    f"10% 刈り込み {tr10['m']:+.4f} (t {tr10['t']:+.2f})・中央値 {s['med']:+.4f}・符号 z {s['z']:+.2f}",
    (tr10["m"] < 0.26) or (tr10["t"] < 2))

# ===================================== H. cost ========================================================
say("\n## H コスト — 02:15 足を丸ごと取る仮想取引（足頭→足尾・往復スプレッド 1 倍／2 倍）")
zc = np.load(os.path.join(MAC, "XAU_m5_close.npz")); cl2 = zc["close"].astype(float)
for nm, msk in [("P1", P1), ("P2", P2)]:
    idxs = np.flatnonzero(msk & okAM) * 288 + AMS
    oo = ORIG_OF_GRID[idxs]
    px = np.where(oo >= 0, cl[np.clip(oo, 0, len(cl) - 1)], np.nan)
    med_px = np.nanmedian(px)
    sp_bp = 0.16 / med_px * 1e4
    gross = stat(rpoAM[msk & okAM])["m"]
    say(f"- {nm}: 価格中央値 {med_px:.1f}・片道スプレッド 0.16 USD = {sp_bp:.2f} bp・往復 {2*sp_bp:.2f} bp"
        f"・gross {gross:+.3f} bp → 純 1 倍 **{gross-2*sp_bp:+.3f} bp**・2 倍 **{gross-4*sp_bp:+.3f} bp**"
        f"（gross / 往復 = {gross/(2*sp_bp)*100:.0f}%）")
    if nm == "P1": net1 = gross - 2 * sp_bp
brk("CONFIRM-H1", "P1 で往復スプレッド 1 倍を引いた純 bp が既に負（＝c54 の『受取り不可』を壊せない）",
    f"P1 純 1 倍 {net1:+.3f} bp", False if net1 < 0 else True)

# ===================================== I. filter / window sensitivity =================================
say("\n## I ふるい・窓の感度（P1 AM 超過）")
rows = []
for half in (3, 6, 12):
    for nf in (4, 6, 8, 10, 12):
        nf_eff = min(nf, 2 * half + 1)
        ok_, _, _, ex_, _ = slot_series(AMS, half=half, nf_min=nf_eff)
        s_ = stat(ex_[P1])
        rows.append((half, nf_eff, s_["m"], s_["t"], s_["n"]))
        say(f"- ±{half*5} 分窓・非flat≥{nf_eff}: m {s_['m']:+.4f} (t {s_['t']:+.2f}, n {s_['n']})")
ms = np.array([r[2] for r in rows]); ts_ = np.array([r[3] for r in rows])
rel = (ms.max() - ms.min()) / 0.521
brk("BREAK-I1", "設定を変えると P1 AM 超過が点推定の ±50% を超えて動く、または t<2 の設定が有る",
    f"m レンジ {ms.min():+.3f}〜{ms.max():+.3f}（幅 = 点推定の {rel*100:.0f}%）・min t {ts_.min():+.2f}"
    f"・t<2 の設定 {int((ts_<2).sum())}/{len(rows)}", (rel > 0.5) or bool((ts_ < 2).any()))

# ===================================== J. placebo / randomization =====================================
say("\n## J プラセボ・ランダム化")
# (i) day-level period-label permutation on AM
m01 = (P0 | P1) & okAM
xa = expoAM[m01]; la = P1[m01]; g = np.isfinite(xa); xa, la = xa[g], la[g]
n1_ = int(la.sum()); nn = len(la)
obs = welch(xa[la], xa[~la])[1]
null = np.empty(NPERM)
for i in range(NPERM):
    p = rng.permutation(nn); m1 = np.zeros(nn, bool); m1[p[:n1_]] = True
    null[i] = welch(xa[m1], xa[~m1])[1]
p_perm = float((null >= obs).mean())
say(f"- (i) 期間ラベル置換 {NPERM}: 観測 DiD t {obs:+.2f}・帰無 95% 分位 {np.percentile(null,95):+.2f}"
    f"・片側 p **{p_perm:.4f}**")
# (ii) slot randomization: pick a random usable slot per replicate, compute its DiD t
us = np.flatnonzero(usable & (~AUX))
draw = tDiD[us]; draw = draw[np.isfinite(draw)]
p_slot = float((draw >= tDiD[AMS]).mean())
say(f"- (ii) スロット・ランダム化（非オークション {len(draw)} 枠を帰無標本とする）: "
    f"観測 02:15 DiD t {tDiD[AMS]:+.2f}・帰無 95% 分位 {np.percentile(draw,95):+.2f}・p {p_slot:.4f}"
    f"／06:15 t {tDiD[PMS]:+.2f}・p {float((draw>=tDiD[PMS]).mean()):.4f}")
brk("BREAK-J1", "観測 DiD t が置換分布の上側 5% に入らない（ラベル置換 または スロット・ランダム化）",
    f"ラベル置換 p {p_perm:.4f}・スロット・ランダム化 p {p_slot:.4f}", (p_perm > 0.05) or (p_slot > 0.05))

# ===================================== K. T2 — is c50's dip a clock artefact? =========================
say("\n## K T2（沈みはロンドン固有）への攻撃")
say("### K-1 分-of-hour プロファイル（London 帯 UTC 07–16・c50 の PRE 足は 分 :25 と :55）")
minute_of_hour = (np.arange(288) % 12) * 5
lon = np.isin(np.arange(288) // 12, list(range(7, 16)))
for nm, msk in PERS:
    means = []
    for mo in range(12):
        cols = np.flatnonzero(lon & (minute_of_hour == mo * 5))
        v = Gm[np.ix_(msk & (dwd <= 4), cols)]
        v = v[np.isfinite(v)]
        means.append(v.mean() if len(v) else np.nan)
    means = np.array(means)
    order = np.argsort(means)
    rank25 = int(np.flatnonzero(order == 5)[0]) + 1   # minute 25 -> index 5
    rank55 = int(np.flatnonzero(order == 11)[0]) + 1  # minute 55 -> index 11
    say(f"- {nm}: " + " ".join(f":{mo*5:02d} {means[mo]:+.3f}" for mo in range(12))
        + f" → :25 の負順位 {rank25}/12・:55 の負順位 {rank55}/12")
    if nm == "P0": r0 = (rank25, rank55)
    if nm == "P1": r1 = (rank25, rank55)
    if nm == "P2": r2 = (rank25, rank55)
nper_hit = sum(1 for rr in (r0, r1, r2) if max(rr) <= 2)
brk("BREAK-K1", ":25 と :55 がともに London 帯 12 ビンの最も負の 2 つに入る期間が 2 つ以上（＝半時間周期の時計人工物）",
    f"P0 (:25 {r0[0]}/12, :55 {r0[1]}/12)・P1 ({r1[0]}, {r1[1]})・P2 ({r2[0]}, {r2[1]}) → 該当期間 {nper_hit}/3",
    nper_hit >= 2)

say("### K-2 TOST（同値検定）— SGE の PRE 足が排除できる「沈み」の最大の大きさ")
for lab_, ex, ok in [("AM 02:10", exprAM, okAM), ("PM 06:10", exprPM, okPM)]:
    for nm in ("P1", "P2"):
        msk = dict(PERS)[nm]
        s_ = stat(ex[msk & ok])
        # one-sided 95% lower bound on the mean; a dip of size d is excluded if d < lower bound
        lowb = s_["m"] - 1.645 * s_["se"]
        say(f"- {lab_} {nm}: m {s_['m']:+.3f}・se {s_['se']:.3f}・片側 95% 下限 {lowb:+.3f} bp"
            f" → これより負の沈みは排除。c50 の −0.65 排除 {'YES' if -0.65 < lowb else 'NO'}"
            f"・半分 −0.33 排除 {'YES' if -0.33 < lowb else 'NO'}"
            f"・1/4 −0.16 排除 {'YES' if -0.16 < lowb else 'NO'}")
        if lab_.startswith("PM") and nm == "P2": pm_p2_lb = lowb
        if lab_.startswith("AM") and nm == "P2": am_p2_lb = lowb
brk("BREAK-K2", "P2 で −0.33 bp（c50 の下限 −0.65 の半分）が片側 95% で排除できない（AM または PM）",
    f"AM P2 下限 {am_p2_lb:+.3f}・PM P2 下限 {pm_p2_lb:+.3f}（−0.33 排除は "
    f"AM {'YES' if -0.33 < am_p2_lb else 'NO'}／PM {'YES' if -0.33 < pm_p2_lb else 'NO'}）",
    (not (-0.33 < am_p2_lb)) or (not (-0.33 < pm_p2_lb)))

# ===================================== L. survivorship of the day filter ==============================
say("\n## L survivorship — AM 窓で落ちた日のうち POST 足自体が有限な日")
base = np.arange(ND) * 288 + AMS
post_all = np.where(PRESENT[base], G[base], np.nan)
dropped = (~okAM) & (dwd <= 4) & np.isfinite(post_all)
for nm, msk in PERS:
    a = post_all[msk & dropped]; b = post_all[msk & okAM]
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if len(a) < 5: say(f"- {nm}: 落ちた日で POST 有限 {len(a)} 本（検定不能）"); continue
    d_, t_ = welch(a, b)
    say(f"- {nm}: 落ちた日 n {len(a)} m {a.mean():+.3f}／残った日 n {len(b)} m {b.mean():+.3f}・差 {d_:+.3f} (Welch t {t_:+.2f})")
    if nm == "P1": l_t = t_; l_n = len(a)
brk("BREAK-L1", "P1 で 落ちた日 vs 残った日 の生 POST 足の |Welch t| ≥ 2（＝ふるいが価格依存）",
    f"P1 落ちた日 n {l_n}・Welch t {l_t:+.2f}", abs(l_t) >= 2)

# ===================================== M. hole sensitivity ============================================
say("\n## M 格子の穴（19 か所）を跨ぐ事象を除いた版（印字のみ）")
for lab_, s_slot in [("AM 02:15", AMS), ("PM 06:15", PMS)]:
    ok_, _, _, ex_, _ = slot_series(s_slot, exclude_span=True)
    a = stat(ex_[P1]); b = stat(ex_[P0]); d_, t_ = welch(ex_[P1], ex_[P0])
    say(f"- {lab_}: P1 {a['m']:+.4f} (t {a['t']:+.2f}, n {a['n']})・P0 {b['m']:+.4f} (t {b['t']:+.2f})・DiD {d_:+.3f} (t {t_:+.2f})")

# ===================================== summary ========================================================
say("\n## まとめ（旗から機械的に合成）")
nb = sum(1 for _, v in BREAKS if v)
for tag, v in BREAKS:
    say(f"- {tag}: {'BROKEN' if v else 'not broken'}")
say(f"- **BROKEN {nb}/{len(BREAKS)}**")
say(f"- 実行 {time.time()-T0:.1f} s・seed {SEED}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\nwrote {OUT}")
