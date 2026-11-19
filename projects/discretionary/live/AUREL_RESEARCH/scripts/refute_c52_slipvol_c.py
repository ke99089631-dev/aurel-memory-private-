# -*- coding: utf-8 -*-
"""
REFUTE c52 — 第 3 走（第 2 走 B-13 の校正：層化は構造的に |rho| を縮める＝符号反転を主張する前に校正する）
=========================================================================================
第 2 走 B-13: atr14 三分位の層内 rho = −0.1943 / −0.1657 / −0.1236（3 層すべて負・合成 −0.1613・z −1.98）
  に対し 全体 rho +0.1415。これは Simpson 型の反転に見えるが、**Y で層化すると Y の分散が切られ
  （range restriction）|rho| は構造的に 0 へ縮む**。縮むだけなら符号は変わらないはずだが、
  縮小 + 標本誤差で 3 層とも負になる確率は 0 ではない。主張する前に帰無/対立の両方で校正する。

  C1 校正（対立仮説のもとで）: 「母集団に単調な rho = +0.1415 が本当にある」世界を生成し、
      同じ n・同じ atr14 の分布で三分位層化し、層内 rho 3 本と合成 z の分布を出す。
      観測（3 層すべて負・合成 −0.1613）が その分布の下側 5% 未満なら、
      「単調な正の関連」という読みは層内で再現されない＝BREAK。
  C2 校正（帰無のもとで）: rho = 0 の世界で同じことをし、観測が帰無でも普通に出るかを確認（過剰主張の防止）。
  C3 全体 rho +0.1415 の正体: 三分位インデックス（3 値）だけで rho を再現できるか・十分位プロファイルの単調性。
  C4 水準（USD）での関係: 第 2 走の回帰は b(atr14) = −0.0016（t −0.06・R² 0.0000）＝水準では関係ゼロ。
      頑健回帰（Theil-Sen・中央値回帰相当）と winsor で、順位だけの現象かを確認。

  BREAK（数字を見る前に固定）:
    C-14 ⇔ C1 の対立仮説分布で 観測の合成 z（−1.98）以下が 5% 未満（＝真の単調正では層内がこうならない）
    C-15 ⇔ C3 で 十分位プロファイルが単調でない（Spearman(十分位index, 十分位内の滑り中央値) が 0.6 未満）
    C-16 ⇔ C4 で winsor/頑健回帰のいずれでも atr14 の係数の |t| < 1（＝水準では経済関係なし・順位のみ）

安全: 読むのは ../setup_ledger.jsonl のみ（読取専用）。書込は AUREL_RESEARCH/data/ のみ。seed 20261119。
"""
import json, time, collections
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np
from scipy import stats

T0 = time.time()
rng = np.random.default_rng(20261119)
ET = ZoneInfo("America/New_York")
LEDGER = "../setup_ledger.jsonl"
OUT = "data/refute_c52_slipvol_c_result.md"
lines = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)
VERD = {}
def brk(key, cond_text, observed, cond):
    VERD[key] = bool(cond)
    P(f"  [{key}] 条件: {cond_text}")
    P(f"         観測: {observed}")
    P(f"         判定: {'BREAK' if cond else 'not broken'}")

rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]
st = {r["id"]: dict(r) for r in rows if r.get("kind") == "setup" and "id" in r}
for r in rows:
    if r.get("kind") == "update" and r.get("target") in st:
        for k, v in r.items():
            if k not in ("kind", "target"): st[r["target"]][k] = v
cl = []
for r in st.values():
    ra = r.get("reaccel") or {}
    if not ra.get("exit_reason"): continue
    ent, sl_, et = ra.get("entry"), ra.get("sl"), ra.get("exit_time")
    if ent is None or sl_ is None or et is None: continue
    ann = r.get("exit_time") == et
    cl.append(dict(id=r["id"], er=ra["exit_reason"], exit_time=int(et), risk=abs(float(ent)-float(sl_)),
                   atr14=(r.get("features") or {}).get("atr14"),
                   sl_slip=r.get("sl_slip_pt") if ann else None))
s0 = sorted([c for c in cl if c["er"] == "SL" and c["sl_slip"] is not None], key=lambda c: c["exit_time"])
CUT = s0[156]["exit_time"] if len(s0) > 157 else s0[-1]["exit_time"]
sl = [c for c in s0 if c["exit_time"] <= CUT and c["atr14"]]
X = np.array([c["sl_slip"] for c in sl], float)
Y = np.array([c["atr14"] for c in sl], float)
RK = np.array([c["risk"] for c in sl], float)
N = len(sl)
RHO = stats.spearmanr(X, Y).statistic
P(f"# REFUTE c52 第 3 走 — B-13 の校正（実行 {datetime.now().strftime('%Y-%m-%d %H:%M')}）")
P("")
P(f"n {N}  全体 rho {RHO:+.4f}")

def tier_rhos(x, y):
    q1, q2 = np.percentile(y, [100/3, 200/3])
    out = []
    for m in (y < q1, (y >= q1) & (y < q2), y >= q2):
        if m.sum() < 5 or len(np.unique(x[m])) < 3: out.append(np.nan); continue
        out.append(stats.spearmanr(x[m], y[m]).statistic)
    return np.array(out)
def fisher_z(rs, ns):
    ok = ~np.isnan(rs)
    z = np.arctanh(np.clip(rs[ok], -0.999, 0.999)); w = (ns[ok] - 3)
    zc = np.sum(w*z)/np.sum(w); se = 1/np.sqrt(np.sum(w))
    return np.tanh(zc), zc/se

q1o, q2o = np.percentile(Y, [100/3, 200/3])
nso = np.array([(Y < q1o).sum(), ((Y >= q1o) & (Y < q2o)).sum(), (Y >= q2o).sum()])
rs_obs = tier_rhos(X, Y)
r_comb_obs, z_comb_obs = fisher_z(rs_obs, nso)
P(f"観測 層内 rho {np.round(rs_obs,4)}  n {nso}  合成 rho {r_comb_obs:+.4f}  z {z_comb_obs:+.2f}")

# ---------- C1 対立仮説（真に単調な rho = +0.1415）のもとでの校正 ----------
P("")
P("## C1 校正（対立仮説）: 母集団に単調な rho = +0.1415 が本当にある世界で、層内 rho はどうなるか")
NS = 4000
ry = stats.rankdata(Y); ryz = (ry - ry.mean())/ry.std()
rho_t = RHO
# 正規コピュラで Spearman ≈ rho_t を作る（Pearson r = 2 sin(pi*rho_s/6)）
r_pear = 2*np.sin(np.pi*rho_t/6)
zc_sim = np.empty(NS); allneg = 0; sim_rs = np.empty((NS, 3))
for i in range(NS):
    e = rng.standard_normal(N)
    lat = r_pear*ryz + np.sqrt(max(1e-9, 1-r_pear**2))*e
    # 観測 X の周辺分布を保ったまま、潜在順位に従って並べ替え（周辺分布=実データ・関連=既知）
    xi = np.sort(X)[np.argsort(np.argsort(lat))]
    rs = tier_rhos(xi, Y); sim_rs[i] = rs
    _, zc = fisher_z(rs, nso); zc_sim[i] = zc
    if np.all(rs[~np.isnan(rs)] < 0): allneg += 1
P(f"- 生成 {NS} 回（周辺分布は実データの X・Y を保持・真の Spearman {rho_t:+.4f}）")
P(f"- 対立仮説のもとでの 層内合成 z 分布: 中央値 {np.median(zc_sim):+.2f}・5 パーセンタイル {np.percentile(zc_sim,5):+.2f}"
  f"・1 パーセンタイル {np.percentile(zc_sim,1):+.2f}")
P(f"- 対立仮説のもとで 層内 rho の平均 = {np.nanmean(sim_rs,axis=0).round(4)}"
  f"（＝層化による縮小後も正が残るのが「単調な正」の姿）")
p_alt = np.mean(zc_sim <= z_comb_obs)
P(f"- 観測 z {z_comb_obs:+.2f} 以下が出る確率（対立仮説のもと）= {p_alt:.4f}")
P(f"- 対立仮説のもとで 3 層すべて負になる確率 = {allneg/NS:.4f}（観測は 3 層すべて負）")
brk("C-14", "真に単調な rho=+0.1415 の世界で 観測の層内合成 z 以下が 5% 未満",
    f"P(z ≤ {z_comb_obs:+.2f} | 単調正) = {p_alt:.4f}・3 層全負の確率 {allneg/NS:.4f}", p_alt < 0.05)

# ---------- C2 帰無のもとで ----------
P("")
P("## C2 校正（帰無 rho=0）: 観測は帰無でも普通に出るか（過剰主張の防止）")
zc0 = np.empty(NS); allneg0 = 0
for i in range(NS):
    xi = rng.permutation(X)
    rs = tier_rhos(xi, Y); _, zc = fisher_z(rs, nso); zc0[i] = zc
    if np.all(rs[~np.isnan(rs)] < 0): allneg0 += 1
P(f"- 帰無のもとでの 層内合成 z: 中央値 {np.median(zc0):+.2f}・5/95 パーセンタイル"
  f" {np.percentile(zc0,5):+.2f}/{np.percentile(zc0,95):+.2f}；3 層全負の確率 {allneg0/NS:.4f}")
P(f"- 観測 z {z_comb_obs:+.2f} の 帰無での片側 p（負側）= {np.mean(zc0 <= z_comb_obs):.4f}")
P(f"→ 読み: 観測の層内は 帰無とは {'区別できない（＝「層内で負」も主張しない）' if np.mean(zc0<=z_comb_obs) > 0.05 else '区別できる'}"
  f"／対立（単調正）とは {'区別できる' if p_alt < 0.05 else '区別できない'}")

# ---------- C3 全体 rho の正体 ----------
P("")
P("## C3 全体 rho +0.1415 の正体（三分位の段差か・十分位は単調か）")
ti = np.digitize(Y, [q1o, q2o])
P(f"- 三分位インデックス（3 値）だけとの rho = {stats.spearmanr(X, ti).statistic:+.4f}"
  f"（全体 {RHO:+.4f} の {stats.spearmanr(X,ti).statistic/RHO:.2f} 倍）")
dec = np.minimum((stats.rankdata(Y)/ (N+1) * 10).astype(int), 9)
P("| atr14 十分位 | n | atr14 中央値 | 滑り 中央値 USD | 滑り 平均 | 滑り/risk 中央値 R |")
P("|---|---|---|---|---|---|")
meds = []
for d in range(10):
    m = dec == d
    if m.sum() == 0: continue
    meds.append(np.median(X[m]))
    P(f"| {d+1} | {int(m.sum())} | {np.median(Y[m]):.2f} | {np.median(X[m]):+.4f} | {X[m].mean():+.4f} | {np.median(X[m]/RK[m]):.5f} |")
meds = np.array(meds)
r_mono = stats.spearmanr(np.arange(len(meds)), meds).statistic
P(f"- 十分位の単調性: Spearman(十分位index, 十分位内の滑り中央値) = {r_mono:+.4f}"
  f"；中央値の範囲 {meds.min():+.4f}–{meds.max():+.4f} USD（幅 {meds.max()-meds.min():.4f} USD = risk 中央値 {np.median(RK):.2f} の {(meds.max()-meds.min())/np.median(RK):.4f}R）")
brk("C-15", "十分位プロファイルの単調性 Spearman < 0.6（＝単調な「ボラに追随」の形をしていない）",
    f"Spearman(十分位index, 中央値) = {r_mono:+.4f}", r_mono < 0.6)

# ---------- C4 水準での関係 ----------
P("")
P("## C4 水準（USD）での関係 — 順位だけの現象か")
ols = stats.linregress(Y, X)
P(f"- OLS  sl_slip ~ atr14: b {ols.slope:+.5f} t {ols.slope/ols.stderr:+.2f} R² {ols.rvalue**2:.5f}")
cap = np.percentile(X, 95); Xw = np.minimum(X, cap)
olw = stats.linregress(Y, Xw)
P(f"- winsor95（cap {cap:.3f} USD）: b {olw.slope:+.5f} t {olw.slope/olw.stderr:+.2f} R² {olw.rvalue**2:.5f}")
ts = stats.theilslopes(X, Y, 0.95)
P(f"- Theil-Sen（頑健）: 傾き {ts.slope:+.5f} USD/USD  95%CI [{ts.low_slope:+.5f}, {ts.high_slope:+.5f}]"
  f"  → CI は 0 を {'含む' if ts.low_slope <= 0 <= ts.high_slope else '含まない'}")
qr = []
for q in (0.5, 0.75, 0.9):
    # 分位回帰の代用: atr14 の十分位ごとの分位点の傾き
    yy = np.array([np.quantile(X[dec == d], q) for d in range(10) if (dec == d).sum() > 2])
    xx = np.array([np.median(Y[dec == d]) for d in range(10) if (dec == d).sum() > 2])
    lr = stats.linregress(xx, yy); qr.append((q, lr.slope, lr.slope/lr.stderr if lr.stderr else np.nan))
    P(f"- 十分位の {int(q*100)} パーセンタイルの傾き: {lr.slope:+.5f} USD/USD（t {lr.slope/lr.stderr if lr.stderr else float('nan'):+.2f}）")
maxt = max(abs(ols.slope/ols.stderr), abs(olw.slope/olw.stderr))
brk("C-16", "winsor/OLS いずれでも atr14 係数の |t| < 1（＝水準では経済関係なし・順位のみの現象）",
    f"OLS |t| {abs(ols.slope/ols.stderr):.2f}・winsor95 |t| {abs(olw.slope/olw.stderr):.2f}", maxt < 1.0)

P("")
P("## 第 3 走 判定")
for k in sorted(VERD): P(f"- {k}: {'BREAK' if VERD[k] else 'not broken'}")
P("")
P(f"実行 {time.time()-T0:.1f} s・読んだのは {LEDGER} のみ（読取専用）・書込 {OUT}")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
