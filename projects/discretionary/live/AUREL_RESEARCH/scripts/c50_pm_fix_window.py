# -*- coding: utf-8 -*-
"""
[cycle50 研究レーン] 2026-11-18 — 【探索・市場構造（ベンチマーク執行の集中・制度変更が優位を殺す例）】
London PM 金フィックス（15:00 London）の **10 分窓** に、2010-13（操作疑惑期・電話フィックス）だけ負のドリフトが有り、
2014 の規制精査〜2015-03-20 の電子オークション移行で消えたか（H_SUPP）。c16 は「14-16 時の 2 時間」を 2010-20 一括で見て null。
本件は窓を 10 分・期間を制度日付で切り直す（文献・制度に由来する別仮説＝c16 の結果からの変形ではない）。

=== 事前固定（この docstring を書いてから数字を見る） ===
背景（記憶・外部通信なし）: LBMA 金 PM フィックスは 2015-03-19 まで 4〜5 行の電話による価格決定（15:00 London 開始・平均 10 分）、
  2015-03-20 から ICE Benchmark Administration の電子オークション（LBMA Gold Price）。2014-02 Bloomberg が Abrantes-Metz & Metz の
  分析（2004-13 の PM フィックス中の大きな値動きの約 2/3 が下方向・2010 以降に頻度上昇）を報じ、2014-05 FCA が Barclays を 2012-06-28 の
  フィックス操作で処分、Deutsche は 2014-01 にパネル離脱を表明。Caminschi & Heaney (2014, JFM) はフィックス中の値動きが情報を持ち
  ボラとスプレッドが上がると報告。機構: フィックス価格で執行される顧客注文（生産者ヘッジ・ETF・精錬）をディーラーが事前に捌く/
  価格を誘導する → 15:00 直後に方向性のある動き。制度変更（電子化・監視）で消えるはずの優位＝「何が起これば成立しなくなるか」が
  日付で特定できる珍しい例。
データ: data/macro/XAU_m5_close.npz（bid・暦格子・前値埋め・⑪ flat 比率印字）。足は開始時刻ラベル。C(t) = 開始時刻 t の足の終値。
  London 現地時刻（DST 追随）で日 d ごとに 10:00–16:40 のスロットの log close を並べる。
窓（London 現地）: FIX10 = lnC(15:05) − lnC(14:55)〔15:00–15:10〕／PRE30 = lnC(14:55) − lnC(14:25)〔14:30–15:00〕／
  POST20 = lnC(15:25) − lnC(15:05)〔15:10–15:30〕／隣接 N1 = lnC(14:55)−lnC(14:45)・N2 = lnC(15:25)−lnC(15:15)／AM10 = lnC(10:35)−lnC(10:25)。
  プラセボ時刻窓（同じ「時の頭 10 分」）: 11:00・12:00・14:00・16:00 London（13:00 は 08:30 ET 公表の 30 分後なので外す）。
有効日: London 月〜金 ∧ 14:30–15:30 の 12 足のうち非 flat ≥8（英国祝日・停止日を落とす）∧ 必要スロットが格子に存在。
期間（制度日付で事前固定・London 日付）: P1 2010-01-01〜2013-12-31（疑惑期）／P2 2014-01-01〜2015-03-19（精査・電話）／
  P3 2015-03-20〜2020-12-31（電子）／P4 2021-01-01〜2026-06（外）。
主セル C1 H_SUPP（1 セル・方向つき）: PASS = mean FIX10(P1) < 0 ∧ t ≤ −2 ∧ |t(P3∪P4)| < 1.5 ∧ 差 (P1 − P3∪P4) の t ≥ 2。
  P1 t ≤ −2 ∧ P3∪P4 t ≤ −1.5 なら「制度非依存の負ドリフト」（別の読み・PASS ではない）。他は null（MDE = 2·se を添える）。
  帰無校正: 同じ統計を 4 つのプラセボ時刻窓で出し、P1 で |t| ≥ 2 になるプラセボ数を印字（時の頭 10 分の一般的な癖の対照）。
  符号検定（下落日の割合・二項 z）を併記（裾に強い第 2 計器）。
C2 H_VOL（構造・記述）: V = mean FIX10² ÷ 平均(mean N1², mean N2²)（隣接 10 分比・ブートストラップ 95% CI 1000 回）。期間別と
  プラセボ時刻窓。**混同**: 15:00 London ≈ 10:00 ET（米 10:00 公表スロット）→ 分離は (a) 米英 DST 不一致週（15:00 London = 11:00 ET）
  の日だけで V を再計算・(b) c45 5σ キャッシュで ET 10:00–10:05 にジャンプがある日を除外。
C3 H_REV（記述・両側）: β(POST20 on FIX10)・β(FIX10 on PRE30)・期間別・HC1 t。方向の事前予測は置かない（文献は継続・操作仮説は反転）。
ゲート ㉛（印字のみ・証拠ではない）: scan 本（refute_c4）で London 14:00–14:55 建玉の SELL − BUY の平均 R*（P1・P3∪P4）と、
  全時刻の同差。在 |Δμ| の印字。
経済的大きさ: bp/日 と往復スプレッド（口座 0.16 USD を当該期の価格で bp 化・P1 のスプレッドは【要取得】）の比。
look-ahead なし（窓はすべて事後の記述・条件づけは時刻のみ）。多重検定: 判定は C1 の 1 セル。C2/C3/AM10/年別は記述。
D2: 期間別・16 年一括の水準は edge 判定に使わない。scan 無し・M5 原本読込なし・MT5 なし・外部通信なし。seed 20261118。
事前の最重大反証候補: ①bid のみ（1 社 CFD）＝15:00 のスプレッド拡大で bid が沈むと負に偏る（US100 再開足で bid −0.4 bp の前例）→
  P3/P4 でも同じ人工物が出るはずなので「P1 だけ負」なら人工物では説明しにくい、逆に全期間負なら人工物の疑い。②10:00 ET 公表との
  混同（方向には中立・ボラには正）。③P1 は 4 年 ≈1000 日・MDE ≈ 2·sd/√n ≈ 2·7 bp/32 ≈ 0.45 bp＝文献の「大きな動きの 2/3 が下」は
  平均で 0.3〜0.5 bp 相当なら境界。④期間境界は制度日付だが「疑惑期 = 2010-13」は報道の分析期間に依存（2004-13）。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c50_pm_fix_window_result.md")
SEED = 20261118; rng = np.random.default_rng(SEED)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle50] London PM フィックス 10 分窓（15:00–15:10 London）の方向・ボラ・制度変更 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c50_pm_fix_window.py)")

# ---------- load ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = (r == 0)
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_lon = t_utc.tz_convert("Europe/London"); t_et = t_utc.tz_convert("America/New_York")
wd = t_lon.weekday.to_numpy(); hour = t_lon.hour.to_numpy(); minute = t_lon.minute.to_numpy()
slot = hour * 12 + minute // 5
day = pd.DatetimeIndex(t_lon.tz_localize(None)).normalize()
et_hour = t_et.hour.to_numpy()
WDN = ['月','火','水','木','金','土','日']
say(f"- npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {flat.mean()*100:.1f}%・曜日別(London) "
    + " ".join(f"{WDN[w]}{flat[wd==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")

def S(h, m): return h * 12 + m // 5
SLOTS = list(range(S(10, 0), S(16, 45)))  # 10:00 .. 16:40
sel = np.isin(slot, SLOTS) & (wd <= 4)
df = pd.DataFrame({"day": day[sel], "slot": slot[sel], "lc": lc[sel], "flat": flat[sel].astype(int), "eth": et_hour[sel]})
P = df.pivot_table(index="day", columns="slot", values="lc", aggfunc="first")
F = df.pivot_table(index="day", columns="slot", values="flat", aggfunc="first")
E = df.pivot_table(index="day", columns="slot", values="eth", aggfunc="first")
P = P.reindex(columns=SLOTS); F = F.reindex(columns=SLOTS); E = E.reindex(columns=SLOTS)
days = P.index
need = [S(10,25), S(10,35), S(14,25), S(14,45), S(14,55), S(15,5), S(15,15), S(15,25)] + [S(h,55) for h in (10,11,13,15)] + [S(h,5) for h in (11,12,14,16)]
ok_grid = P[need].notna().all(axis=1).to_numpy()
nf_win = (1 - F.loc[:, S(14,30):S(15,25)]).sum(axis=1).to_numpy()   # non-flat count in 14:30..15:25 (12 bars)
ok = ok_grid & (nf_win >= 8)
et_at_15 = E[S(15, 0)].to_numpy()
say(f"- London 平日 {len(days)} 日 → 格子 OK {ok_grid.sum()}・14:30–15:30 非 flat ≥8 {ok.sum()} 日（落とした {(~ok).sum()} 日 = 英国祝日/停止/格子穴）")
say(f"- 15:00 London の ET 時: " + "・".join(f"{int(k)} 時 {int(v)} 日" for k, v in pd.Series(et_at_15[ok]).value_counts().sort_index().items()) + "（11 時 = 米英 DST 不一致週）")

Pv = P.to_numpy(); bp = 1e4
def w(h1, m1, h2, m2): return (Pv[:, SLOTS.index(S(h2, m2))] - Pv[:, SLOTS.index(S(h1, m1))]) * bp
FIX10 = w(14, 55, 15, 5); PRE30 = w(14, 25, 14, 55); POST20 = w(15, 5, 15, 25)
N1 = w(14, 45, 14, 55); N2 = w(15, 15, 15, 25); AM10 = w(10, 25, 10, 35)
PLAC = {h: w(h - 1, 55, h, 5) for h in (11, 12, 14, 16)}
PLAC_N = {h: (w(h - 1, 45, h - 1, 55), w(h, 15, h, 25)) for h in (11, 12, 14, 16)}

d = pd.DatetimeIndex(days)
PER = {"P1 2010-13 疑惑期": (d >= "2010-01-01") & (d <= "2013-12-31"),
       "P2 2014-15/03 精査": (d >= "2014-01-01") & (d <= "2015-03-19"),
       "P3 2015/03-20 電子": (d >= "2015-03-20") & (d <= "2020-12-31"),
       "P4 2021-26H1 外": (d >= "2021-01-01")}
P34 = PER["P3 2015/03-20 電子"] | PER["P4 2021-26H1 外"]
for k in PER: PER[k] = PER[k] & ok
P34 = P34 & ok

def stat(x):
    x = x[np.isfinite(x)]; n = len(x); m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); t = m / se if se > 0 else np.nan
    neg = (x < 0).mean(); pos = (x > 0).mean(); zs = ((x < 0).sum() - (x != 0).sum() / 2) / math.sqrt((x != 0).sum() / 4) if (x != 0).sum() > 0 else np.nan
    return dict(n=n, m=m, se=se, t=t, mde=2 * se, neg=neg, pos=pos, zsign=zs, med=np.median(x), sd=x.std(ddof=1))
def diff_t(a, b):
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    return (a.mean() - b.mean()) / math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
def fmt(s): return f"**{s['m']:+.2f} bp (t {s['t']:+.2f}, n {s['n']}, MDE {s['mde']:.2f})** 下落日 {s['neg']*100:.1f}% (符号 z {s['zsign']:+.2f}) 中央値 {s['med']:+.2f} sd {s['sd']:.1f}"

say("\n## C1 H_SUPP 主セル — FIX10 = lnC(15:05) − lnC(14:55)〔15:00–15:10 London〕の平均（bp/日・日 = 独立観測）")
ST = {}
for k, m in PER.items():
    ST[k] = stat(FIX10[m]); say(f"- {k}: {fmt(ST[k])}")
s34 = stat(FIX10[P34]); say(f"- P3∪P4 2015/03-20〜2026H1: {fmt(s34)}")
t_diff = diff_t(FIX10[PER['P1 2010-13 疑惑期']], FIX10[P34])
s1 = ST['P1 2010-13 疑惑期']
pass_c1 = (s1['m'] < 0) and (s1['t'] <= -2) and (abs(s34['t']) < 1.5) and (t_diff >= 2)
alt = (s1['t'] <= -2) and (s34['t'] <= -1.5)
say(f"- 差 P1 − (P3∪P4): {s1['m']-s34['m']:+.2f} bp・Welch t {t_diff:+.2f}")
verdict = "PASS（制度依存の負ドリフト）" if pass_c1 else ("制度非依存の負ドリフト（PASS ではない）" if alt else "null")
say(f"- **判定 C1: {verdict}**（規則: P1 m<0 ∧ t≤−2 ∧ |t(P3∪P4)|<1.5 ∧ 差 t≥2）")

say("\n### C1 帰無校正 — プラセボ時刻窓（時の頭 10 分・同じ日集合）")
for h, x in PLAC.items():
    row = []
    for k, m in PER.items():
        s = stat(x[m]); row.append(f"{k.split()[0]} {s['m']:+.2f} (t {s['t']:+.2f})")
    s34p = stat(x[P34]); row.append(f"P3∪P4 {s34p['m']:+.2f} (t {s34p['t']:+.2f})")
    say(f"- {h:02d}:00–{h:02d}:10 London: " + "・".join(row) + f"・差 P1−P34 t {diff_t(x[PER['P1 2010-13 疑惑期']], x[P34]):+.2f}")
n_pl = sum(abs(stat(x[PER['P1 2010-13 疑惑期']])['t']) >= 2 for x in PLAC.values())
say(f"- P1 で |t|≥2 のプラセボ時刻窓: {n_pl}/4（FIX10 の P1 t {s1['t']:+.2f} と比べる）")

say("\n### C1 記述 — 年別 FIX10（bp/日・t・下落日%）と AM10（10:30 AM オークション窓 lnC(10:35)−lnC(10:25)）")
yrs = d.year.to_numpy()
for y in range(2010, 2027):
    m = ok & (yrs == y)
    if m.sum() < 20: continue
    s = stat(FIX10[m]); a = stat(AM10[m])
    say(f"- {y}: FIX10 {s['m']:+.2f} (t {s['t']:+.2f}, n {s['n']}, 下落 {s['neg']*100:.0f}%) ｜ AM10 {a['m']:+.2f} (t {a['t']:+.2f})")
for k, m in PER.items():
    a = stat(AM10[m]); say(f"- AM10 {k}: {fmt(a)}")
say("- 感度（NFP 日除外・13:30 London 公表の 90 分後）:")
def nfp_dates_v2(y0=2009, y1=2026):
    """c24 の BLS 規則をそのまま複製（import すると c24 本体が走るため）: 参照週 = 前月 12 日を含む日〜土・公表 = その土曜 + 20 日・1/1 → +7・7/4 → −1。"""
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
            rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
nfp = set(pd.DatetimeIndex(nfp_dates_v2(2009, 2026)).normalize())
is_nfp = np.array([dd in nfp for dd in d])
for k, m in PER.items():
    s = stat(FIX10[m & ~is_nfp]); say(f"  - {k} NFP 除外: {s['m']:+.2f} bp (t {s['t']:+.2f}, n {s['n']})")

# ---------- C2 vol ----------
say("\n## C2 H_VOL — 隣接 10 分比 V = mean FIX10² ÷ 平均(mean N1², mean N2²)（N1 14:50–15:00・N2 15:20–15:30）・bootstrap 95% CI")
def vratio(x, n1, n2, m, nb=1000):
    x = x[m]; n1 = n1[m]; n2 = n2[m]; good = np.isfinite(x) & np.isfinite(n1) & np.isfinite(n2); x, n1, n2 = x[good], n1[good], n2[good]
    v = np.mean(x**2) / (0.5 * (np.mean(n1**2) + np.mean(n2**2)))
    idx = rng.integers(0, len(x), size=(nb, len(x)))
    vb = np.mean(x[idx]**2, axis=1) / (0.5 * (np.mean(n1[idx]**2, axis=1) + np.mean(n2[idx]**2, axis=1)))
    med = np.median(np.abs(x)) / (0.5 * (np.median(np.abs(n1)) + np.median(np.abs(n2))))
    return v, np.quantile(vb, 0.025), np.quantile(vb, 0.975), med, len(x)
for k, m in PER.items():
    v, lo, hi, med, n = vratio(FIX10, N1, N2, m)
    say(f"- {k}: V **{v:.2f}** [{lo:.2f}, {hi:.2f}]・|中央値| 比 {med:.2f}・n {n}")
say("- プラセボ時刻窓の V（同形）:")
for h, x in PLAC.items():
    n1, n2 = PLAC_N[h]
    row = [f"{k.split()[0]} {vratio(x, n1, n2, m, 300)[0]:.2f}" for k, m in PER.items()]
    say(f"  - {h:02d}:00: " + "・".join(row))
say("- 混同の分離 (a) 米英 DST 不一致週（15:00 London = 11:00 ET・米 10:00 公表と分離）vs 一致日:")
mis = ok & (et_at_15 == 11); ali = ok & (et_at_15 == 10)
for k, m in PER.items():
    if (m & mis).sum() >= 15:
        v1 = vratio(FIX10, N1, N2, m & mis, 500); v0 = vratio(FIX10, N1, N2, m & ali, 500)
        s1m = stat(FIX10[m & mis]); s0m = stat(FIX10[m & ali])
        say(f"  - {k}: 不一致 V {v1[0]:.2f} [{v1[1]:.2f},{v1[2]:.2f}] (n {v1[4]}・平均 {s1m['m']:+.2f} bp t {s1m['t']:+.2f}) ｜ 一致 V {v0[0]:.2f} [{v0[1]:.2f},{v0[2]:.2f}] (n {v0[4]}・平均 {s0m['m']:+.2f} t {s0m['t']:+.2f})")
    else:
        say(f"  - {k}: 不一致日 {(m & mis).sum()} 日 <15 → 省略")
say("- 混同の分離 (b) c45 5σ キャッシュで ET 10:00–10:05 にジャンプのある日を除外:")
try:
    J = pd.read_csv(os.path.join(DATA, "c45_jumps_5sigma_declustered.csv"))
    jd = set(pd.to_datetime(J.loc[(J.et_hour == 10) & (J.et_min <= 5), "et_date"]).dt.normalize())
    # ET 日付と London 日付は 10-11 時 ET では同日
    is_j10 = np.array([dd in jd for dd in d])
    say(f"  - 10:00–10:05 ET に 5σ ジャンプのある日 {is_j10.sum()}（有効日中 {(is_j10 & ok).sum()}）")
    for k, m in PER.items():
        v, lo, hi, med, n = vratio(FIX10, N1, N2, m & ~is_j10, 500); s = stat(FIX10[m & ~is_j10])
        say(f"  - {k} 除外後: V {v:.2f} [{lo:.2f},{hi:.2f}]・平均 {s['m']:+.2f} bp (t {s['t']:+.2f}, n {n})")
except Exception as e:
    say(f"  - c45 キャッシュ読込失敗: {e}")

# ---------- C3 reversal / continuation ----------
say("\n## C3 H_REV（記述・両側）— β(POST20 on FIX10)・β(FIX10 on PRE30)・HC1 t")
def ols_hc1(y, x):
    g = np.isfinite(y) & np.isfinite(x); y, x = y[g], x[g]; X = np.column_stack([np.ones(len(x)), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b; XtXi = np.linalg.inv(X.T @ X)
    V = XtXi @ (X.T * (e**2)) @ X @ XtXi; se = math.sqrt(V[1, 1]); return b[1], b[1] / se, len(y), np.corrcoef(x, y)[0, 1]
for k, m in PER.items():
    b1, t1, n1_, rho1 = ols_hc1(POST20[m], FIX10[m]); b2, t2, n2_, rho2 = ols_hc1(FIX10[m], PRE30[m])
    say(f"- {k}: POST20~FIX10 β {b1:+.3f} (t {t1:+.2f}, ρ {rho1:+.3f}) ｜ FIX10~PRE30 β {b2:+.3f} (t {t2:+.2f}, ρ {rho2:+.3f})・n {n1_}")
say("- プラセボ時刻窓（14:00）の同形: " + "・".join(f"{k.split()[0]} β_post {ols_hc1(w(14,5,14,25)[m], PLAC[14][m])[0]:+.3f} (t {ols_hc1(w(14,5,14,25)[m], PLAC[14][m])[1]:+.2f})" for k, m in PER.items()))

# ---------- economic size ----------
say("\n## 経済的大きさ — 期間別 平均価格と 0.16 USD 往復の bp 換算（P1 の実スプレッドは【要取得】・口座 0.16 は 2026 の値）")
for k, m in PER.items():
    pr = np.exp(Pv[m][:, SLOTS.index(S(15, 0))]).mean(); say(f"- {k}: 平均価格 {pr:.0f} USD・0.16 USD = {0.16/pr*1e4:.2f} bp（往復）・FIX10 平均 {ST[k]['m']:+.2f} bp・比 {abs(ST[k]['m'])/(0.16/pr*1e4):.2f}")

# ---------- gate ㉛ ----------
say("\n## ゲート ㉛（印字のみ・証拠ではない）— scan 本（refute_c4）London 14:00–14:55 建玉の SELL − BUY 平均 R*")
try:
    with open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), "r", encoding="utf-8") as f: TR = json.load(f)["trades"]
    tr = pd.DataFrame(TR); te = pd.to_datetime(tr.entry_time, unit="s", utc=True).dt.tz_convert("Europe/London")
    tr["lh"] = te.dt.hour.to_numpy(); tr["ld"] = pd.DatetimeIndex(te.dt.tz_localize(None)).normalize()
    tr["per"] = np.select([(tr.ld <= "2013-12-31"), (tr.ld <= "2015-03-19"), (tr.ld <= "2020-12-31")], ["P1", "P2", "P3"], "P4")
    tr["R"] = tr["R"].astype(float)
    for per in ("P1", "P2", "P3", "P4"):
        a = tr[(tr.per == per) & (tr.lh == 14)]; b = tr[(tr.per == per)]
        def sb(x):
            s_ = x[x.side == "SELL"].R; b_ = x[x.side == "BUY"].R
            if len(s_) < 5 or len(b_) < 5: return "n 不足"
            dm = s_.mean() - b_.mean(); se = math.sqrt(s_.var(ddof=1) / len(s_) + b_.var(ddof=1) / len(b_)); return f"{dm:+.3f}R (t {dm/se:+.2f}, SELL {len(s_)}/BUY {len(b_)})"
        say(f"- {per}: 14 時 London 建玉 SELL−BUY {sb(a)} ｜ 全時刻 {sb(b)}")
    a1 = tr[(tr.per == "P1") & (tr.lh == 14)]; say(f"- 在ゲート |Δμ|（P1 14 時 SELL−BUY − 全時刻 SELL−BUY）= {abs((a1[a1.side=='SELL'].R.mean()-a1[a1.side=='BUY'].R.mean()) - (tr[(tr.per=='P1')&(tr.side=='SELL')].R.mean()-tr[(tr.per=='P1')&(tr.side=='BUY')].R.mean())):.3f}R（規則 0.048・印字のみ）")
except Exception as e:
    say(f"- scan json 読込失敗: {e}")

say(f"\n- 実行 {time.time()-T0:.1f} s・seed {SEED}・入力 XAU_m5_close.npz＋c45 csv＋refute_c4 json・多年 scan 無し・外部通信無し")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
print(f"[written] {OUT}")
