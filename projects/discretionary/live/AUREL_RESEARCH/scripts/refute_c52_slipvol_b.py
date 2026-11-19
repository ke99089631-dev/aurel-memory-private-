# -*- coding: utf-8 -*-
"""
REFUTE c52 — 第 2 走（第 1 走 refute_c52_slipvol.py の自己監査と、設計が甘かった 2 本の作り直し）
=====================================================================================
第 1 走の結果（要点）と、第 2 走で直すこと:
  (1) 自己監査: brk() が BREAK の「条件文」を verdict と無関係に印字した。例: BREAK-8 は not broken なのに
      「置換 p 0.0001 ≥ 0.05」と印字＝偽の文。11-19 03:40 の方法論候補 72（BREAK は 1 条件 1 行・
      文は条件として読める形に）の再発。本走は 条件 / 観測値 / 判定 を別フィールドで印字する。
  (2) A2 の前提（束で帰無 sd が膨らむ）は 外れた: 日ブロック置換の膨張率 1.00×・円環シフト 1.07×・
      日クラスタ bootstrap は 本単位と 1.01× 差。＝SL 3.2 本/日・atr14 の日間分散シェア 0.399 では
      クラスタ補正はほぼ効かない。第 1 走の BREAK-1 は 実質「円環シフト p 0.0510」と「両側 CI が 0 を含む
      （＝片側 p>0.025 の言い換え・BREAK-2 と同じ情報）」だけで立っていた → 過大。本走で分解して言い直す。
  (3) 一方で A2(d)「日平均に潰すと rho +0.0098（p 0.47）」は強い数字だが 第 1 走は検出力を出していない。
      n=49 の MDE を出さずに「消えた」と読むのは 候補 69 と同じ誤り。本走で between/within に分解し、
      それぞれの MDE を併記してから読む。
  (4) 副産物 (b) のラベル置換（p 0.0001）は 無効な検定だった: 「週末持ち越し」は c52 が上位 5 本の外れ値を
      見てから読んだラベルで、最大の 1 本を含む小さなラベルは何であれ極小 p を出す。
      正しい攻撃 = ラベル発見の多重検定（機械的に列挙できるラベル族の中での順位）。本走で実装。
  (5) H_S2 は連言で、第 2 条件が「滑り比の帯 A−B |t| < 2」＝“無い”ことを肯定条件に使っている。
      その検出力（最小検出差 / 比そのものの大きさ）を c52 は出していない → 候補 69 の再発かを検定する。

本走の BREAK（数字を見る前に固定）:
  B-10 ⇔ ラベル族（機械列挙 ≥40 個）の中で「週末持ち越し」の p の順位が上位 5% に入らない、
          または p<0.05 のラベルが 3 個以上ある（＝最大 1 本を含む小ラベルなら何でも光る）。
  B-11 ⇔ H_S2 第 2 条件の最小検出差（2se）が 滑り比そのものの中央値以上（＝“無い”を肯定に使えない）。
  B-12 ⇔ between（日間）rho が 0 近傍で、かつ その検定の MDE が 観測 within rho より小さい
          （＝「日レベルでは無い」と言える検出力がある）。MDE が足りなければ B-12 は不成立＝判定保留。
  B-13 ⇔ atr14 三分位の各層内で rho が 0 以下になる層が 1 つ以上（層内で消えるなら層間比較の産物）。

安全: 読むのは ../setup_ledger.jsonl のみ（読取専用）。書込は AUREL_RESEARCH/data/ のみ。
      発注/デモ発注/本番編集/プロセス・執行機・ライブサーバ接触/MT5/プロップ/秘密 なし。seed 20261119。
"""
import json, time, collections
from datetime import datetime, timezone, timedelta, date
from zoneinfo import ZoneInfo
import numpy as np
from scipy import stats

T0 = time.time()
rng = np.random.default_rng(20261119)
ET = ZoneInfo("America/New_York")
LEDGER = "../setup_ledger.jsonl"
OUT = "data/refute_c52_slipvol_b_result.md"
lines = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

VERD = {}
def brk(key, cond_text, observed, cond):
    """条件 / 観測 / 判定 を分けて印字（第 1 走の欠陥の修正・方法論候補 72）"""
    VERD[key] = bool(cond)
    P(f"  [{key}] 条件: {cond_text}")
    P(f"         観測: {observed}")
    P(f"         判定: {'BREAK' if cond else 'not broken'}")

# ---------- 母集団（c52 と同一・第 1 走と同一 cut） ----------
rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]
st = {r["id"]: dict(r) for r in rows if r.get("kind") == "setup" and "id" in r}
for r in rows:
    if r.get("kind") == "update" and r.get("target") in st:
        for k, v in r.items():
            if k not in ("kind", "target"): st[r["target"]][k] = v
closed = []
for r in st.values():
    ra = r.get("reaccel") or {}
    er = ra.get("exit_reason")
    if not er: continue
    ent, sl, et, en_t = ra.get("entry"), ra.get("sl"), ra.get("exit_time"), ra.get("entry_time")
    if ent is None or sl is None or et is None: continue
    ann_ok = r.get("exit_time") == et
    closed.append(dict(id=r["id"], er=er, R=ra.get("R"), exit_time=int(et),
                       entry_time=int(en_t) if en_t else None, risk=abs(float(ent)-float(sl)),
                       side=r.get("side"), wall_kind=r.get("wall_kind"),
                       atr14=(r.get("features") or {}).get("atr14"),
                       sl_slip=r.get("sl_slip_pt") if ann_ok else None, spread=r.get("spread_pt"),
                       hold=ra.get("hold_bars"), mfe=ra.get("mfe_R")))
sl_all = [c for c in closed if c["er"] == "SL" and c["sl_slip"] is not None]
sl_all.sort(key=lambda c: c["exit_time"])
CUT = sl_all[156]["exit_time"] if len(sl_all) > 157 else sl_all[-1]["exit_time"]
closed = [c for c in closed if c["exit_time"] <= CUT]
for c in closed:
    d = datetime.fromtimestamp(c["exit_time"], timezone.utc).astimezone(ET)
    c["h"], c["wd"], c["et_date"] = d.hour, d.weekday(), d.date()
    if c["entry_time"]:
        di = datetime.fromtimestamp(c["entry_time"], timezone.utc).astimezone(ET)
        c["h_in"], c["in_wd"], c["in_date"] = di.hour, di.weekday(), di.date()
    else:
        c["h_in"] = c["in_wd"] = c["in_date"] = None
sl = [c for c in closed if c["er"] == "SL" and c["sl_slip"] is not None and c["atr14"]]
X = np.array([c["sl_slip"] for c in sl], float)
Y = np.array([c["atr14"] for c in sl], float)
RK = np.array([c["risk"] for c in sl], float)
DAY = np.array([c["et_date"].toordinal() for c in sl])
N = len(sl)
VR = X / RK
P(f"# REFUTE c52 第 2 走（実行 {datetime.now().strftime('%Y-%m-%d %H:%M')}）")
P("")
P(f"母集団 n {N}（第 1 走・c52 と同一 157）  rho {stats.spearmanr(X,Y).statistic:+.4f}")

# ============== B-10 ラベル発見の多重検定（副産物 (b) の正しい攻撃） ==============
P("")
P("## B-10 「尻尾は週末」＝ラベル発見の多重検定（c52 は上位 5 本の外れ値を見てからラベルを読んだ）")
labels = {}
for wd in range(5):
    labels[f"建玉曜日={['月','火','水','木','金'][wd]}"] = np.array([c["in_wd"] == wd for c in sl])
for wd in range(7):
    labels[f"決着曜日={['月','火','水','木','金','土','日'][wd]}"] = np.array([c["wd"] == wd for c in sl])
for h0 in range(0, 24, 2):
    labels[f"決着ET{h0:02d}-{h0+1:02d}"] = np.array([h0 <= c["h"] <= h0+1 for c in sl])
    labels[f"建玉ET{h0:02d}-{h0+1:02d}"] = np.array([c["h_in"] is not None and h0 <= c["h_in"] <= h0+1 for c in sl])
for s in sorted(set(c["side"] for c in sl if c["side"])):
    labels[f"side={s}"] = np.array([c["side"] == s for c in sl])
for w in sorted(set(c["wall_kind"] for c in sl if c["wall_kind"])):
    labels[f"wall={w}"] = np.array([c["wall_kind"] == w for c in sl])
labels["hold=1"] = np.array([c["hold"] == 1 for c in sl])
labels["hold<=2"] = np.array([(c["hold"] or 99) <= 2 for c in sl])
labels["hold>=50"] = np.array([(c["hold"] or 0) >= 50 for c in sl])
labels["atr14 上位10%"] = Y >= np.percentile(Y, 90)
labels["risk 上位10%"] = RK >= np.percentile(RK, 90)
labels["risk 下位10%"] = RK <= np.percentile(RK, 10)
sp = np.array([c["spread"] if c["spread"] is not None else np.nan for c in sl], float)
labels["spread 上位10%"] = sp >= np.nanpercentile(sp, 90)
labels["週末持ち越し"] = np.array([c["in_wd"] == 4 and c["wd"] in (6, 0) and c["in_date"] and c["et_date"] > c["in_date"] for c in sl])
labels["日曜18時ET決着"] = np.array([c["wd"] == 6 and c["h"] == 18 for c in sl])

imax = int(np.argmax(VR))
P(f"- 最大の 1 本 = {sl[imax]['id']}（{VR[imax]:.3f}R・全 SL 滑り {VR.sum():.3f}R の {VR[imax]/VR.sum():.0%}）")
NP = 20000
rec = []
for name, m in labels.items():
    m = np.nan_to_num(m, nan=False).astype(bool)
    n1 = int(m.sum())
    if n1 < 1 or n1 >= N: continue
    obs = VR[m].mean() - VR[~m].mean()
    cnt = 0
    for _ in range(NP):
        pr = rng.permutation(VR)
        cnt += (pr[:n1].mean() - pr[n1:].mean()) >= obs
    p = (cnt + 1) / (NP + 1)
    rec.append((name, n1, obs, p, bool(m[imax])))
rec.sort(key=lambda r: r[3])
P(f"- 機械列挙したラベル {len(rec)} 個・各 {NP} 回のラベル置換（片側・滑り R 平均差）")
P("| 順位 | ラベル | n | Δ R | p | max 本を含む |")
P("|---|---|---|---|---|---|")
for i, (nm, n1, o, p, hm) in enumerate(rec[:12]):
    P(f"| {i+1} | {nm} | {n1} | {o:+.4f} | {p:.4f} | {'はい' if hm else '—'} |")
sig = [r for r in rec if r[3] < 0.05]
sig_max = [r for r in sig if r[4]]
rank_wk = [i for i, r in enumerate(rec) if r[0] == "週末持ち越し"][0] + 1
P(f"- p<0.05 のラベル {len(sig)}/{len(rec)} 個（うち max 本を含む {len(sig_max)} 個 = {len(sig_max)/max(1,len(sig)):.0%}）")
P(f"- 「週末持ち越し」の順位 = {rank_wk}/{len(rec)}（上位 {rank_wk/len(rec):.1%}）")
P(f"- max 本を含むラベル {sum(1 for r in rec if r[4])} 個の p 中央値 {np.median([r[3] for r in rec if r[4]]):.4f}"
  f" vs 含まないラベル {sum(1 for r in rec if not r[4])} 個の p 中央値 {np.median([r[3] for r in rec if not r[4]]):.4f}")
P(f"- Bonferroni（{len(rec)} ラベル）閾値 {0.05/len(rec):.5f} → 週末持ち越しの p "
  f"{[r[3] for r in rec if r[0]=='週末持ち越し'][0]:.5f} は {'通過' if [r[3] for r in rec if r[0]=='週末持ち越し'][0] < 0.05/len(rec) else '不通過'}")
brk("B-10",
    f"週末ラベルの p 順位が上位 5%（{max(1,int(0.05*len(rec)))} 位以内）に入らない、または p<0.05 のラベルが 3 個以上",
    f"順位 {rank_wk}/{len(rec)}・p<0.05 のラベル {len(sig)} 個",
    (rank_wk > max(1, int(0.05*len(rec)))) or (len(sig) >= 3))

# ============== B-11 H_S2 第 2 条件（“無い”を肯定に使う）の検出力 ==============
P("")
P("## B-11 H_S2 の第 2 条件「滑り比 sl_slip/atr14 の帯 A−B |t|<2」の検出力（候補 69 の再発検査）")
ratio = X / Y
Amask = np.array([8 <= c["h"] <= 9 for c in sl])
a, b = ratio[Amask], ratio[~Amask]
d = a.mean() - b.mean()
se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
P(f"- 帯 A n {Amask.sum()}／帯 B n {(~Amask).sum()}；比 平均 A {a.mean():+.5f} / B {b.mean():+.5f}"
  f"  Δ {d:+.5f}  t {d/se:+.2f}  MDE(2se) {2*se:.5f}")
P(f"- 比そのものの大きさ: 全体 中央値 {np.median(ratio):.5f}・平均 {ratio.mean():.5f}")
P(f"- MDE / 比の中央値 = {2*se/np.median(ratio):.2f} 倍  → 「時刻固有分なし」と言えるのは"
  f" 比の {2*se/np.median(ratio):.1f} 倍より大きい差だけ")
# 最小検出倍率 k*（帯 A の比が k 倍なら検出できるか）
kstar = 1 + 2*se/max(1e-12, b.mean())
P(f"- 最小検出倍率 k* = 1 + 2se/平均_B = {kstar:.2f}×（帯 A の滑り比が帯 B の {kstar:.2f} 倍未満なら検出不能）")
brk("B-11",
    "第 2 条件の MDE(2se) が 滑り比の中央値 以上（＝“差が無い”を肯定条件に使えない）",
    f"MDE {2*se:.5f} vs 比の中央値 {np.median(ratio):.5f}（{2*se/np.median(ratio):.2f} 倍）・k* {kstar:.2f}×",
    2*se >= np.median(ratio))

# ============== B-12 between / within 分解（A2(d) の検出力つき言い直し） ==============
P("")
P("## B-12 between（日間）/ within（日内）分解 — 「ボラに追随」は どのレベルの変動か")
rx, ry = stats.rankdata(X), stats.rankdata(Y)
uniq = np.unique(DAY)
bx = np.array([rx[DAY == d].mean() for d in uniq]); by = np.array([ry[DAY == d].mean() for d in uniq])
wx = rx - np.repeat(0.0, N); wy = ry.copy()
for d in uniq:
    m = DAY == d; wx[m] = rx[m] - rx[m].mean(); wy[m] = ry[m] - ry[m].mean()
nb = len(uniq)
r_bet = np.corrcoef(bx, by)[0, 1]
t_bet = r_bet*np.sqrt((nb-2)/max(1e-12, 1-r_bet**2))
mde_bet = stats.t.ppf(0.95, nb-2)/np.sqrt(nb-2+stats.t.ppf(0.95, nb-2)**2)   # 片側 5% で有意になる最小 r
md = nb  # within の自由度は N - 日数
dfw = N - nb
mw = np.sqrt((wx**2).sum()*(wy**2).sum())
r_wit = (wx @ wy)/mw if mw > 0 else np.nan
t_wit = r_wit*np.sqrt(dfw/max(1e-12, 1-r_wit**2))
mde_wit = stats.t.ppf(0.95, dfw)/np.sqrt(dfw+stats.t.ppf(0.95, dfw)**2)
P(f"- between（日平均の順位・n {nb} 日）r = {r_bet:+.4f}  t {t_bet:+.2f}（片側 p {1-stats.t.cdf(t_bet,nb-2):.4f}）"
  f"  最小検出 r*(片側5%) = {mde_bet:+.4f}")
P(f"- within（日内で中心化・df {dfw}）r = {r_wit:+.4f}  t {t_wit:+.2f}（片側 p {1-stats.t.cdf(t_wit,dfw):.4f}）"
  f"  最小検出 r*(片側5%) = {mde_wit:+.4f}")
P(f"- 全体 rho {stats.spearmanr(X,Y).statistic:+.4f} の内訳: 相関は {'within（日内）' if abs(r_wit)>abs(r_bet) else 'between（日間）'} 側に居る")
P(f"- 注意: between の r* {mde_bet:.4f} > within の観測 r {r_wit:+.4f} なら、"
  f"「日レベルでは無い」は {'言えない（検出力不足・判定保留）' if mde_bet > abs(r_wit) else '言える'}")
brk("B-12",
    "between r がほぼ 0 で、かつ between の最小検出 r* が within の観測 r 以下（＝日レベルの不在を主張できる検出力がある）",
    f"between r {r_bet:+.4f}（r* {mde_bet:.4f}）・within r {r_wit:+.4f}（r* {mde_wit:.4f}）",
    abs(r_bet) < 0.05 and mde_bet <= abs(r_wit))

# ============== B-13 atr14 三分位の層内 ==============
P("")
P("## B-13 レジーム部分集合: atr14 三分位の層内で rho は残るか（層間比較の産物か）")
q1, q2 = np.percentile(Y, [33.333, 66.667])
tiers = {"低ボラ(atr14<%.2f)" % q1: Y < q1,
         "中ボラ": (Y >= q1) & (Y < q2),
         "高ボラ(atr14>=%.2f)" % q2: Y >= q2}
rs = []
for nm, m in tiers.items():
    r = stats.spearmanr(X[m], Y[m])
    rs.append(r.statistic)
    P(f"- {nm}: n {int(m.sum())}  rho {r.statistic:+.4f}（両側 p {r.pvalue:.3f}）"
      f"  atr14 範囲 {Y[m].min():.2f}–{Y[m].max():.2f}  滑り中央値 {np.median(X[m]):+.4f} USD")
# Fisher 合成（層内の平均的な関連）
z = np.array([np.arctanh(np.clip(r, -0.999, 0.999)) for r in rs])
ns = np.array([int(m.sum()) for m in tiers.values()])
zc = np.sum((ns-3)*z)/np.sum(ns-3); se_z = 1/np.sqrt(np.sum(ns-3))
P(f"- 層内合成 rho = {np.tanh(zc):+.4f}（z {zc/se_z:+.2f}・片側 p {1-stats.norm.cdf(zc/se_z):.4f}）"
  f" vs 層を跨ぐ全体 rho {stats.spearmanr(X,Y).statistic:+.4f}")
nneg = sum(1 for r in rs if r <= 0)
brk("B-13", "atr14 三分位の層内で rho ≤ 0 になる層が 1 つ以上",
    f"層内 rho = " + ", ".join(f"{r:+.4f}" for r in rs) + f"（≤0 は {nneg} 層）", nneg >= 1)

# ============== 補: 機構の同定（第 1 走 BREAK-4 の確認と経済量） ==============
P("")
P("## 補 機構の同定（第 1 走 BREAK-4 の裏づけ）— 滑りは risk に比例するか")
lo = stats.linregress(RK, X)
P(f"- 回帰 sl_slip = a + b·risk: b {lo.slope:+.5f}（t {lo.slope/lo.stderr:+.2f}）a {lo.intercept:+.4f} R² {lo.rvalue**2:.4f}")
lo2 = stats.linregress(Y, X)
P(f"- 回帰 sl_slip = a + b·atr14: b {lo2.slope:+.5f}（t {lo2.slope/lo2.stderr:+.2f}）R² {lo2.rvalue**2:.4f}")
P(f"- R 単位 滑り（sl_slip/risk）: 中央値 {np.median(VR):.5f}R・平均 {VR.mean():.5f}R"
  f"  rho(·, atr14) {stats.spearmanr(VR,Y).statistic:+.4f}（p {stats.spearmanr(VR,Y).pvalue:.3f}）")
# 経済量: atr14 が 1 sd 上がると R 単位コストはいくら増えるか
sl_r = stats.linregress(Y, VR)
P(f"- 経済量: atr14 +1sd（{Y.std():.2f} USD）→ R 単位 SL 滑り {sl_r.slope*Y.std():+.5f}R"
  f"（t {sl_r.slope/sl_r.stderr:+.2f}）＝ gross {55.4:.1f}R に対し 157 本で {sl_r.slope*Y.std()*157/55.4:+.2%}")

P("")
P("## 第 2 走 判定")
for k in sorted(VERD): P(f"- {k}: {'BREAK' if VERD[k] else 'not broken'}")
P("")
P(f"実行 {time.time()-T0:.1f} s・読んだのは {LEDGER} のみ（読取専用）・書込 {OUT}")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
