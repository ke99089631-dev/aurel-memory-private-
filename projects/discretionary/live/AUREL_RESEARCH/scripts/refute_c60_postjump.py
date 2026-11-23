# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-23 09:30 反証レーン] 標的 = cycle60（06:40・探索・5σ ジャンプ後の価格は戻るか続くか）

PROMOTED.md は空（昇格候補ゼロ）。c60 の主 2 セル（C1/C2）は null＝「壊す」余地が無い。
よって c59 反証（11-23 03:40）と同じ方針で、**null を支える肯定形の主張**＝「得た知識 (1)〜(4)」と
その数字が載っている補助 c60b の実装・推定子選択・対照設計を攻撃する。
c60 の決着不能点（bid 1 社・XAU ask M1【要取得】・UJ 腕の暦汚染【要取得】）には**寄らない**＝
同じ csv・同じ npz・同じ 5 分格子の数字を全部そのまま受け入れ、
**(a) 排除主張の推定子依存性 (b) 局在説明の多重検定 (c) 検出力の下限 (d) 暦なしでの腕の純化 (e) 対照の較正**
だけで壊しに行く。

=== 標的の文言（c60 findings 2026-11-23 06:40 の「判定」節）===
T1 = 知識(1)「予定外 5σ ジャンプの後 1〜4 時間に反転は無い。**在は 95% 下限 +0.05σ で反転を全排除**」
     （= raw 平均 +0.587σ − 2·se 0.268 = +0.051σ を一方側 95% 下限として使っている）
T2 = 知識(2)「在の継続 +0.59σ は edge でなく**裾と組成の顔**。平均は |D|>3σ の少数事象が作り、
     **ET 08–10（+1.11・t 2.9）と小 |z|（+1.43・t 3.3）に局在**し用量反応なし」
T3 = 知識(3)「事前閾値 0.20σ は**構造的に判定不能**。winsor は se と回収率 a を同率で落とし
     **実効 MDE を変えない（0.42〜0.54σ）**＝候補 92 の適用限界」
T4 = 最重大反証の決着条件「UJ 腕の情報ジャンプ汚染を落とすには**米マクロ公表の全暦【要取得】が必要**」
     （＝暦が無ければ UJ_clean で H_REV を再判定できない、という含み）

=== 事前固定（この docstring を書いてから数字を見る・seed 20261123）===
データ: data/c45_jumps_5sigma_declustered.csv（2166・ts/r_bp/z/sigma_bp/cls/sched_slot/et_*）＋
  data/macro/XAU_m5_close.npz（bid・完全格子）。**c60 と同一**。多年 scan 無し・MT5 無し・外部通信無し・新規データ取得無し。
  σ_trail は c45 で厳密に trailing（bar i を除く W_SIG 窓・コードで確認済み）＝look-ahead 無しを前提に受け入れる。
主統計・対照・窓・クラスタは c60 と同一実装を**写して**使う（D'_K = s·1e4·Δlog cl/σ・アンカー 1 本ずらし shift=1・
  双子 = 同 ET 時:分 D±7 の 2 本平均・自身 |r|≥4σ_event なら除外・SE = 事象 ET 日クラスタ）。

GATE G（これが通らなければ以降の判定を書かない）: c60 の主セルを機械的に再現。
  UJ D'_12 在 +0.587 (se 0.268・n 653/605)／外 −0.131 (se 0.463・n 269/248)／近年 −0.042、C2 在 +0.408 (se 0.703)。
  許容 |Δ D| ≤ 0.002σ ∧ |Δ se| ≤ 0.002。外れたら GATE FAIL と印字して判定は書かない。

A1（T1・排除主張の推定子依存性）: 在/外 UJ D'_12 を 5 推定子で推定 = raw 平均／winsor±3σ／winsor±5σ／
  10% 対称トリム平均／中央値。SE は**事象 ET 日クラスタのブートストラップ（B=600・日クラスタ再抽出・seed 20261123）**、
  併記で raw/winsor の解析 SE（c60b と同じ）。減衰率 a = (est(x) − est(x−0.20))/0.20（c60b と同じ注入法・δ = 事前閾値）。
  補正推定値 θ̂ = est/a・補正 se = se/a。**排除下限 LB = (est − 2·se)/a**（c60 の 2·se 規約に合わせる・1.645·se 版も印字）。
  判定: **BROKEN = 4 つのロバスト推定子（w3/w5/trim10/median）のうち ≥2 個で 在 LB ≤ −0.20σ**
    （＝c60 が「全排除」と書いた経済閾値 0.20σ の反転が、推定子を変えると排除できない）。
  SURVIVED = 4 つ全部で 在 LB > −0.05σ（c60 の下限と同じ桁で頑健）。それ以外 inconclusive。
A2（T2・局在説明の多重検定）: 在 UJ の記述分割族 9 セル（上/下・ET08-10/他・開場/非開場・|z| 下/中/上）の **max |t|** を
  **置換検定**で較正する。帰無 = 「D は共変量（時刻・|z|・符号）と無関係」。実装 = 在 UJ 内で共変量ベクトルを
  **事象間で同時に置換**（D と ET 日は固定＝クラスタ構造を保つ）・B=2000・同じクラスタ SE で t を再計算し max|t| の分布を取る。
  判定: **BROKEN（=c60 の局在説明は雑音と区別できない）= p(max|t| ≥ 観測) ≥ 0.10**。
  SURVIVED = p < 0.02。それ以外 inconclusive。併記（記述）= bp 単位・USD 単位の D、σ_trail 十分位別の寄与、
  最小 σ_trail 十分位を落とした在の D（σ 単位は比推定子＝分母が小さい事象が平均を支配し得る）。
A3（T3・検出力の下限を同じデータで下げに行く）: 在 UJ で 4 設計の**実効 MDE = 2·se/a**（a は ±0.20σ 注入の回収率）:
  (i) 双子 4 本（D±7, ±14）(ii) 双子 8 本（D±7,14,21,28）(iii) 符号検定（P(D>0) の 0.20σ 注入応答）
  (iv) 中央値（A1 のブートストラップ se）。
  判定: **BROKEN = いずれか 1 つで 在 実効 MDE ≤ 0.30σ**（c60 の「0.42〜0.54σ が床」を割る）。
  SURVIVED = 4 設計全部で ≥0.42σ。それ以外 inconclusive。
A4（T4・暦なしで UJ 腕を純化する）: 外部データを一切使わず、**その場で既知の情報だけ**で情報ジャンプを剥がす:
  wake 検出子 = 事象足の直前 3 本（i0−1..i0−3）に「ET 08:00–10:30 の 15 分スロット足（分 %15==0）で |r| ≥ 2·σ_trail」が
  1 本でもあれば **UJ_wake**（公表の第 2 波の疑い）、無ければ **UJ_clean**。look-ahead 無し（全部 i0 以前）。
  副の検出子 = 木曜 ∧ ET 08:30–09:00（新規失業保険申請の尾・暦不要の曜日規則）。
  判定: **BROKEN = (在 UJ の ET08-10 事象の ≥50% が wake で flag される) ∧ (UJ_clean 在 の LB(raw) が全腕 LB から |Δ| ≥ 0.20σ 動く)**
    （＝暦【要取得】を待たずに腕の純化と再判定ができる＝決着条件の前提が崩れる）。
  SURVIVED = flag 率 <20% または |Δ LB| < 0.10σ。それ以外 inconclusive。
A5（対照設計の攻撃・判定補助）: (i) 双子の 4σ 切り落としを外す（**対照だけ片側切断**＝事象は 5σ 必須なのに対照は大きい足を禁止）
  (ii) 双子 2 本必須 (iii) **|z| マッチ対照（RMT 類似）**= 同 ET 時:分・同曜日の d ∈ ±{7,14,…,182} 日から
  v = s·r/σ_event が**最大**の 1 本を選ぶ（候補の将来は選択に使わない＝選択バイアス無し）。達成 v と残差を印字し、
  「この設計では対照を較正できない」ことを定量（c60 自身の最重大反証 (3) の数値化）。
A6（分割汚染・look-ahead・survivorship）: 双子が反対窓に落ちる本数と除去後の主セル・除外率の内訳。
A7（受け取れるか）: 在 raw D'_12 を bp/USD に直し、往復コスト 1×/2× で net。
陽性対照: (a) A1/A3 の注入回収率 a（設計が本物のドリフトを落としていないこと） (b) c60 の 生 C_1 不発（在 −0.007）を再現。
多重検定: 判定は事前固定 4 件（T1〜T4）。族全体は c60 ≈135 ＋ 本反証 ≈90 → M ≈ 225・必要 |z| ≈ 3.7 を印字。
事前の予測: T1 broken（裾が作る点推定で排除を主張している）・T2 inconclusive〜broken・T3 survived（1h sd 7σ は推定子で消えない）・T4 inconclusive。
事前の最重大反証（自分への）: wake 検出子は「大きいスロット足」を情報の代理にするだけで、流動性枯渇でも
  スロット足は大きくなり得る＝UJ_clean は「情報なし」腕ではなく「直前が静かだった」腕に過ぎない。
発注・デモ発注・本番編集・プロセス/執行機/サーバ接触・MT5・プロップ参照・秘密読取 は一切しない。書込は AUREL_RESEARCH/ のみ。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT_MD = os.path.join(DATA, 'refute_c60_postjump.md'); OUT_LOG = os.path.join(DATA, 'refute_c60_postjump_run.log')
LINES = []
def P(s=''):
    print(s); LINES.append(s)
def el(): return f'{time.time()-T0:.1f}s'
SEED = 20261123
rng = np.random.default_rng(SEED)
P(f'# [REFUTE] c60（5σ ジャンプ後の価格）反証レーン  {dt.datetime.now():%Y-%m-%d %H:%M}  seed {SEED}')

# ---------------- load (c60 と同一) ----------------
ev = pd.read_csv(os.path.join(DATA, 'c45_jumps_5sigma_declustered.csv'))
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_close.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); N = len(ts)
lc = np.log(cl); r = np.r_[np.nan, np.diff(lc)] * 1e4; flat = ~(np.isfinite(r) & (r != 0))
NY = ZoneInfo('America/New_York')
tny = pd.to_datetime(ts, unit='s', utc=True).tz_convert(NY); hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy()
brk = (hr == 17) | ((hr == 18) & (mn < 10))
cf = np.concatenate([[0], np.cumsum(flat.astype(np.int64))]); cb = np.concatenate([[0], np.cumsum(brk.astype(np.int64))])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i] == t, i, -1)
i0 = gidx(ev.ts.to_numpy(np.int64)); ok0 = i0 >= 0
r_re = np.where(ok0, r[np.maximum(i0, 0)], np.nan)
mt = np.abs(r_re - ev.r_bp.to_numpy()) <= 0.05
P(f'整合: 事象足 格子一致 {ok0.mean()*100:.2f}%・cache r_bp vs npz 再計算 |差|≤0.05bp 一致 {mt[ok0].mean()*100:.2f}%（n {ok0.sum()}）  ({el()})')
if mt[ok0].mean() < 0.99:
    P('!! 整合 <99% — 停止'); open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(LINES)); sys.exit(1)

s = np.sign(ev.r_bp.to_numpy()); sig = ev.sigma_bp.to_numpy(float); zabs = ev.z.to_numpy(float)
yr = pd.to_datetime(ev.et_date).dt.year.to_numpy(); etd = ev.et_date.to_numpy()
cls = ev.cls.to_numpy(); slot = ev.sched_slot.to_numpy()
arm = np.where(cls == 'UJ', 'UJ', np.where(cls == 'SJ', 'SJ', np.where(slot == 1, 'ANN', 'EVO')))
eh = ev.et_hour.to_numpy(); em = ev.et_min.to_numpy(); ewd = ev.wd.to_numpy()
WIN = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}
KMAIN, SH = 12, 1

def win_ok(i, K=KMAIN, shift=SH):
    a = i + shift; b = i + shift + K
    inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cb[bb] - cb[aa]) == 0) & ((cf[bb] - cf[aa]) <= max(1, int(0.10 * (K + 1))))
def Cm(i, K=KMAIN, shift=SH):
    a = np.clip(i + shift, 0, N-1); b = np.clip(i + shift + K, 0, N-1)
    return s * (lc[b] - lc[a]) * 1e4 / sig
def twins(days=(-7, 7)):
    return [gidx(ev.ts.to_numpy(np.int64) + d * 86400) for d in days]
def twin_bad(it, zcut=4.0):
    rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
    return (it < 0) | ~np.isfinite(rr) | (rr >= zcut * sig)
def paired(K=KMAIN, shift=SH, days=(-7, 7), zcut=4.0, need=1):
    okE = win_ok(i0, K, shift); CE = Cm(i0, K, shift)
    CT = np.zeros(len(ev)); nT = np.zeros(len(ev), int)
    for it in twins(days):
        okT = win_ok(it, K, shift) & ~twin_bad(it, zcut)
        CT += np.where(okT, Cm(it, K, shift), 0.0); nT += okT.astype(int)
    ok = okE & (nT >= need)
    return CE - CT / np.maximum(nT, 1), CE, ok, nT

def clus(x, g):
    n = len(x)
    if n < 3: return np.nan, np.nan, n, 0
    m = x.mean(); e = x - m
    gg = pd.Series(e).groupby(g).sum()
    return m, math.sqrt(float((gg**2).sum())) / n, n, len(gg)

# ---------------- GATE G ----------------
P('\n## GATE G — c60 主セルの機械的再現')
D12, CE12, ok12, nT12 = paired()
gate_rows, gate_ok = [], True
EXP = {'在 2010-20': (0.587, 0.268, 653, 605), '外 2021-26H1': (-0.131, 0.463, 269, 248), '近年 2024-26H1': (-0.042, None, 126, None)}
for w, wm in WIN.items():
    m = ok12 & wm & (arm == 'UJ'); mm, se, n, g = clus(D12[m], etd[m])
    e = EXP[w]; dD = mm - e[0]; dse = (se - e[1]) if e[1] else np.nan
    bad = (abs(dD) > 0.002) or (e[1] and abs(dse) > 0.002) or (n != e[2])
    gate_ok &= not bad
    P(f'- UJ D\'_12 {w:14s}: {mm:+.4f} (se {se:.4f}・t {mm/se:+.2f}・n {n}/{g}) vs c60 {e[0]:+.3f} (se {e[1] if e[1] else float("nan"):.3f}・n {e[2]}) → Δ {dD:+.4f}/{dse:+.4f} {"**FAIL**" if bad else "OK"}')
def diff_cell(w):
    wm = WIN[w]; mu = ok12 & wm & (arm == 'UJ'); ma = ok12 & wm & (arm == 'ANN')
    Du, Da = D12[mu], D12[ma]; m1, m0 = Du.mean(), Da.mean()
    x = np.concatenate([Du, Da]); gg = np.concatenate([etd[mu], etd[ma]]); ind = np.r_[np.ones(len(Du)), np.zeros(len(Da))]
    e = np.where(ind == 1, x - m1, x - m0); inf = np.where(ind == 1, e / len(Du), -e / len(Da))
    return m1 - m0, math.sqrt(float((pd.Series(inf).groupby(gg).sum()**2).sum())), len(Du), len(Da)
di, sdi, n1i, n0i = diff_cell('在 2010-20')
bad2 = abs(di - 0.408) > 0.002 or abs(sdi - 0.703) > 0.002
gate_ok &= not bad2
P(f'- C2 Δ(UJ−ANN) 在: {di:+.4f} (se {sdi:.4f}) vs c60 +0.408 (se 0.703) → {"**FAIL**" if bad2 else "OK"}')
P(f'- **GATE G = {"PASS（以降の判定を書く）" if gate_ok else "FAIL（判定は書かない）"}**  ({el()})')

# ---------------- helpers: estimators / cluster bootstrap ----------------
def est_raw(x): return float(np.mean(x))
def est_w3(x): return float(np.mean(np.clip(x, -3, 3)))
def est_w5(x): return float(np.mean(np.clip(x, -5, 5)))
def est_tr10(x):
    lo, hi = np.quantile(x, [0.10, 0.90]); y = x[(x >= lo) & (x <= hi)]
    return float(np.mean(y)) if len(y) else np.nan
def est_med(x): return float(np.median(x))
ESTS = [('raw 平均', est_raw), ('winsor±3σ', est_w3), ('winsor±5σ', est_w5), ('trim10%', est_tr10), ('中央値', est_med)]
ROBUST = ['winsor±3σ', 'winsor±5σ', 'trim10%', '中央値']

def boot_cells(x, g, B=600, seedoff=0):
    """cluster bootstrap index sets (resample ET-date clusters with replacement)"""
    code, uniq = pd.factorize(g); G = len(uniq)
    order = np.argsort(code, kind='stable'); cnt = np.bincount(code, minlength=G); st = np.r_[0, np.cumsum(cnt)[:-1]]
    rr = np.random.default_rng(SEED + seedoff)
    out = []
    for _ in range(B):
        pick = rr.integers(0, G, G)
        out.append(np.concatenate([order[st[p]:st[p] + cnt[p]] for p in pick]))
    return out
def boot_se(x, idxs, f):
    v = np.array([f(x[ix]) for ix in idxs]); return float(np.nanstd(v, ddof=1))

DELTA = 0.20  # 事前閾値（往復スプレッド相当）

# ---------------- A1 ----------------
P('\n## A1（T1）排除下限の推定子依存性 — 在/外 UJ D\'_12')
P('| 窓 | 推定子 | est | se(boot) | se(解析) | t | a（−0.20σ 注入回収） | θ̂=est/a | 実効 MDE 2se/a | **LB=(est−2se)/a** | LB(1.645se)/a |')
P('|---|---|---|---|---|---|---|---|---|---|---|')
A1 = {}
for w in ['在 2010-20', '外 2021-26H1']:
    m = ok12 & WIN[w] & (arm == 'UJ'); x = D12[m]; g = etd[m]
    idxs = boot_cells(x, g, B=600, seedoff=1)
    for nm, f in ESTS:
        e0 = f(x); e1 = f(x - DELTA); a = (e0 - e1) / DELTA
        seb = boot_se(x, idxs, f)
        sea = clus(np.clip(x, -3, 3) if nm == 'winsor±3σ' else (np.clip(x, -5, 5) if nm == 'winsor±5σ' else x), g)[1] if nm in ('raw 平均', 'winsor±3σ', 'winsor±5σ') else np.nan
        lb2 = (e0 - 2 * seb) / max(a, 1e-9); lb16 = (e0 - 1.645 * seb) / max(a, 1e-9)
        A1[(w, nm)] = dict(est=e0, se=seb, a=a, lb2=lb2, lb16=lb16, mde=2 * seb / max(a, 1e-9))
        P(f'| {w} | {nm} | {e0:+.3f} | {seb:.3f} | {sea:.3f} | {e0/seb:+.2f} | {a:.2f} | {e0/max(a,1e-9):+.3f} | {2*seb/max(a,1e-9):.3f} | **{lb2:+.3f}** | {lb16:+.3f} |')
nbroken = sum(1 for nm in ROBUST if A1[('在 2010-20', nm)]['lb2'] <= -0.20)
nsafe = sum(1 for nm in ROBUST if A1[('在 2010-20', nm)]['lb2'] > -0.05)
T1 = 'BROKEN' if nbroken >= 2 else ('SURVIVED' if nsafe == 4 else 'inconclusive')
P(f'- 在 ロバスト 4 推定子のうち LB ≤ −0.20σ = **{nbroken} 個**・LB > −0.05σ = {nsafe} 個 → **T1 = {T1}**')
P(f'- 参考: c60 の主張「在 95% 下限 +0.05σ」= raw の (est−2se) = {A1[("在 2010-20","raw 平均")]["est"]-2*A1[("在 2010-20","raw 平均")]["se"]:+.3f}σ（補正不要 a=1.00）')

# ---------------- A2 ----------------
P('\n## A2（T2）局在説明（ET08-10・小 |z|）の置換検定')
mU = ok12 & WIN['在 2010-20'] & (arm == 'UJ')
xU = D12[mU]; gU = etd[mU]; code, uq = pd.factorize(gU); G = len(uq)
cov = dict(up=(s[mU] > 0), dn=(s[mU] < 0), morn=((eh[mU] >= 8) & (eh[mU] <= 10)))
cov['other'] = ~cov['morn']
open_slot = np.isin(eh * 100 + em, [820, 825, 935, 940, 300, 305, 2000, 2005])
cov['open'] = open_slot[mU]; cov['noopen'] = ~open_slot[mU]
q = np.quantile(zabs[mU], [1/3, 2/3])
cov['zlo'] = zabs[mU] < q[0]; cov['zmid'] = (zabs[mU] >= q[0]) & (zabs[mU] < q[1]); cov['zhi'] = zabs[mU] >= q[1]
FAM = ['up', 'dn', 'morn', 'other', 'open', 'noopen', 'zlo', 'zmid', 'zhi']
def tfast(x, code, G, mask):
    """mean & cluster-se t for a boolean sub-mask, bincount based"""
    xx = x[mask]; cc = code[mask]
    n = len(xx)
    if n < 10: return np.nan
    m = xx.mean(); e = xx - m
    sg = np.bincount(cc, weights=e, minlength=G)
    se = math.sqrt(float((sg**2).sum())) / n
    return m / se if se > 0 else np.nan
obs = {k: tfast(xU, code, G, cov[k]) for k in FAM}
obs_max = float(np.nanmax([abs(v) for v in obs.values()]))
P('- 観測 t: ' + '・'.join(f'{k} {obs[k]:+.2f}' for k in FAM) + f' → **max|t| = {obs_max:.2f}**')
B2 = 2000; mx = np.empty(B2)
idxall = np.arange(len(xU))
rr2 = np.random.default_rng(SEED + 2)
covmat = np.vstack([cov[k] for k in FAM])
for b in range(B2):
    pm = rr2.permutation(idxall)
    cm = covmat[:, pm]
    mx[b] = np.nanmax([abs(tfast(xU, code, G, cm[j])) for j in range(len(FAM))])
pval = float((mx >= obs_max).mean())
T2 = 'BROKEN' if pval >= 0.10 else ('SURVIVED' if pval < 0.02 else 'inconclusive')
P(f'- 置換 max|t| 分布（B={B2}・共変量同時置換・D と ET 日は固定）: 中央 {np.median(mx):.2f}・90% {np.quantile(mx,0.90):.2f}・95% {np.quantile(mx,0.95):.2f}・99% {np.quantile(mx,0.99):.2f}')
P(f'- **p(max|t| ≥ {obs_max:.2f}) = {pval:.3f} → T2 = {T2}**（BROKEN = 局在は雑音と区別できない）')
# 記述: 単位・σ_trail 十分位
for w in ['在 2010-20', '外 2021-26H1']:
    m = ok12 & WIN[w] & (arm == 'UJ'); x = D12[m]
    bpv = x * sig[m]; px = float(np.median(cl[i0[m]]))
    mb, seb_, _, _ = clus(bpv, etd[m])
    P(f'- {w} 単位: σ 単位 {x.mean():+.3f}σ／bp 単位 {mb:+.2f} bp (t {mb/seb_:+.2f}・MDE {2*seb_:.2f} bp)／USD {mb/1e4*px:+.3f}（価格中央 {px:.0f}）')
    dec = pd.qcut(sig[m], 10, labels=False, duplicates='drop')
    con = [f'{d} {x[dec==d].mean():+.2f}' for d in range(int(np.nanmax(dec)) + 1)]
    P(f'  - σ_trail 十分位別 D（σ 単位）: ' + ' '.join(con))
    k = dec > 0; mm2, se2, n2, g2 = clus(x[k], etd[m][k])
    P(f'  - 最小 σ_trail 十分位を落とす: {mm2:+.3f}σ (t {mm2/se2:+.2f}・n {n2})・σ_trail 中央 {np.median(sig[m]):.2f} bp')

# ---------------- A3 ----------------
P('\n## A3（T3）実効 MDE を同じデータで下げに行く（在 UJ）')
rows = []
for nm, days, need in [('双子 2 本（c60）', (-7, 7), 1), ('双子 4 本（±7,±14）', (-14, -7, 7, 14), 1), ('双子 8 本（±7..±28）', (-28, -21, -14, -7, 7, 14, 21, 28), 1)]:
    Dx, _, okx, nTx = paired(days=days, need=need)
    m = okx & WIN['在 2010-20'] & (arm == 'UJ'); x = Dx[m]
    mm, se, n, g = clus(x, etd[m]); a = 1.0
    rows.append((nm, mm, se, a, 2 * se / a, n, float(np.mean(nTx[m]))))
    P(f'- {nm}: D {mm:+.3f}σ (se {se:.3f}・t {mm/se:+.2f}・n {n}/{g}・双子 平均 {np.mean(nTx[m]):.2f} 本)・a {a:.2f}・実効 MDE **{2*se/a:.3f}σ**')
# sign test
m = ok12 & WIN['在 2010-20'] & (arm == 'UJ'); x = D12[m]; g = etd[m]
code2, uq2 = pd.factorize(g); G2 = len(uq2)
def signrate(v):
    return float((v > 0).mean())
def signrate_se(v, cc, GG):
    p = signrate(v); e = (v > 0).astype(float) - p
    sg = np.bincount(cc, weights=e, minlength=GG); return math.sqrt(float((sg**2).sum())) / len(v)
p0 = signrate(x); p1 = signrate(x - DELTA); a_sign = (p0 - p1) / DELTA
se_sign = signrate_se(x, code2, G2)
mde_sign = 2 * se_sign / max(a_sign, 1e-9)
P(f'- 符号検定: P(D>0) {p0*100:.1f}%・注入 −0.20σ で {p1*100:.1f}%（a {a_sign:.4f}/σ）・se {se_sign*100:.2f}pp → 実効 MDE **{mde_sign:.3f}σ**')
med = A1[('在 2010-20', '中央値')]
P(f'- 中央値（A1 boot）: est {med["est"]:+.3f}・se {med["se"]:.3f}・a {med["a"]:.2f} → 実効 MDE **{med["mde"]:.3f}σ**')
cands = {t[0]: t[4] for t in rows}
cands['符号検定'] = mde_sign; cands['中央値'] = med['mde']
best = min(cands.items(), key=lambda kv: kv[1])
T3 = 'BROKEN' if best[1] <= 0.30 else ('SURVIVED' if min(cands.values()) >= 0.42 else 'inconclusive')
P(f'- 最良 = {best[0]} 実効 MDE {best[1]:.3f}σ（c60 の床 0.42σ・BROKEN 閾 0.30σ）→ **T3 = {T3}**')

# ---------------- A4 ----------------
P('\n## A4（T4）暦なしで UJ 腕を純化する — wake 検出子')
slotbar = (mn % 15 == 0) & (hr >= 8) & ((hr < 10) | ((hr == 10) & (mn <= 30)))
wake = np.zeros(len(ev), bool)
for k in (1, 2, 3):
    j = i0 - k
    good = (i0 >= 0) & (j >= 1)
    jj = np.clip(j, 0, N-1)
    big = np.isfinite(r[jj]) & (np.abs(r[jj]) >= 2.0 * sig)
    wake |= good & slotbar[jj] & big
thu_claims = (ewd == 3) & (eh == 8) & (em >= 30) | (ewd == 3) & (eh == 9) & (em == 0)
mUJ = ok12 & (arm == 'UJ')
for w in ['在 2010-20', '外 2021-26H1']:
    base = mUJ & WIN[w]; morn = base & (eh >= 8) & (eh <= 10)
    P(f'- {w}: UJ n {base.sum()}・wake flag {wake[base].mean()*100:.1f}%（ET08-10 事象の {wake[morn].mean()*100:.1f}%・ET08-10 は UJ の {morn.sum()/base.sum()*100:.0f}%）・木 08:30-09:00 {thu_claims[base].mean()*100:.1f}%')
    for nm, mk in [('UJ_wake', wake), ('UJ_clean', ~wake), ('木claims', thu_claims), ('非木claims', ~thu_claims)]:
        m2 = base & mk
        if m2.sum() < 30: P(f'  - {nm}: n {m2.sum()} <30 スキップ'); continue
        x2 = D12[m2]; mm, se, n, g = clus(x2, etd[m2])
        idxs = boot_cells(x2, etd[m2], B=400, seedoff=3)
        lb_raw = mm - 2 * se
        e0 = est_w3(x2); a3 = (e0 - est_w3(x2 - DELTA)) / DELTA; se3 = boot_se(x2, idxs, est_w3)
        P(f'  - {nm}: raw {mm:+.3f}σ (se {se:.3f}・t {mm/se:+.2f}・n {n}/{g})・LB(raw) **{lb_raw:+.3f}**・winsor±3σ {e0:+.3f} (se {se3:.3f}・a {a3:.2f}・LB {(e0-2*se3)/max(a3,1e-9):+.3f})')
base_i = mUJ & WIN['在 2010-20']
lb_all = clus(D12[base_i], etd[base_i]); lb_all = lb_all[0] - 2 * lb_all[1]
mc = base_i & ~wake; lb_cl = clus(D12[mc], etd[mc]); lb_cl = lb_cl[0] - 2 * lb_cl[1]
mo = base_i & (eh >= 8) & (eh <= 10)
flag_rate = float(wake[mo].mean())
T4 = 'BROKEN' if (flag_rate >= 0.50 and abs(lb_cl - lb_all) >= 0.20) else ('SURVIVED' if (flag_rate < 0.20 or abs(lb_cl - lb_all) < 0.10) else 'inconclusive')
P(f'- 在: ET08-10 の wake flag 率 {flag_rate*100:.1f}%・LB(全腕) {lb_all:+.3f} → LB(UJ_clean) {lb_cl:+.3f}（|Δ| {abs(lb_cl-lb_all):.3f}σ）→ **T4 = {T4}**')

# ---------------- A5 ----------------
P('\n## A5 対照設計の攻撃')
for nm, kw in [('c60 既定（4σ 切り・双子 ≥1）', dict(zcut=4.0, need=1)), ('4σ 切り無し（対照の片側切断を外す）', dict(zcut=1e9, need=1)), ('双子 2 本必須', dict(zcut=4.0, need=2))]:
    Dx, _, okx, _ = paired(**kw)
    out = []
    for w in ['在 2010-20', '外 2021-26H1']:
        m2 = okx & WIN[w] & (arm == 'UJ'); mm, se, n, g = clus(Dx[m2], etd[m2]); out.append(f'{w.split()[0]} {mm:+.3f} (t {mm/se:+.2f}・n {n})')
    P(f'- {nm}: ' + '・'.join(out))
# |z|-matched control (RMT analogue)
offs = [d for k in range(1, 27) for d in (-7 * k, 7 * k)]
vbest = np.full(len(ev), -np.inf); ibest = np.full(len(ev), -1)
for d in offs:
    it = gidx(ev.ts.to_numpy(np.int64) + d * 86400)
    okT = win_ok(it) & (it >= 0)
    rr_ = np.where(it >= 0, r[np.maximum(it, 0)], np.nan)
    v = s * rr_ / sig
    take = okT & np.isfinite(v) & (v > vbest)
    vbest = np.where(take, v, vbest); ibest = np.where(take, it, ibest)
mz = mUJ & (ibest >= 0)
Cmz = np.where(ibest >= 0, s * (lc[np.clip(ibest + SH + KMAIN, 0, N-1)] - lc[np.clip(ibest + SH, 0, N-1)]) * 1e4 / sig, np.nan)
for w in ['在 2010-20', '外 2021-26H1']:
    m2 = mz & WIN[w]
    vev = (s * ev.r_bp.to_numpy() / sig)[m2]
    Dm = (Cm(i0)[m2] - Cmz[m2]); mm, se, n, g = clus(Dm, etd[m2])
    # 通常双子の較正
    vt = []
    for it in twins():
        okT = win_ok(it) & ~twin_bad(it)
        vt.append(np.where(okT, s * r[np.maximum(it, 0)] / sig, np.nan))
    vtw = np.nanmean(np.vstack(vt), axis=0)[m2]
    P(f'- |z| マッチ対照 {w}: 事象 v 平均 {vev.mean():+.2f}σ・マッチ対照 v {vbest[m2].mean():+.2f}σ（残差 {vev.mean()-vbest[m2].mean():+.2f}σ）・通常双子 v {np.nanmean(vtw):+.2f}σ（残差 {vev.mean()-np.nanmean(vtw):+.2f}σ）→ D\'_12 {mm:+.3f}σ (t {mm/se:+.2f}・n {n}/{g})')

# ---------------- A6 ----------------
P('\n## A6 分割汚染・look-ahead・survivorship')
cont = 0
for it in twins():
    okT = win_ok(it) & ~twin_bad(it)
    tyr = np.where(it >= 0, pd.to_datetime(np.where(it >= 0, ts[np.maximum(it, 0)], 0), unit='s', utc=True).tz_convert(NY).year.to_numpy(), -1)
    cont += int(np.sum(mUJ & okT & (((yr <= 2020) & (tyr >= 2021)) | ((yr >= 2021) & (tyr <= 2020)))))
P(f'- 双子が反対窓に落ちる本数（UJ・両双子合計）: {cont} 本')
for w in ['在 2010-20', '外 2021-26H1']:
    base = WIN[w] & (arm == 'UJ')
    P(f'  - {w} 除外内訳: 腕 n {base.sum()} → 窓有効 {np.sum(base & win_ok(i0))}・双子有り {np.sum(base & ok12)}（除外 {(1-np.sum(base & ok12)/base.sum())*100:.1f}%）')
P('- look-ahead: σ_trail は c45 で bar i を除く trailing 窓（コード確認済み・lo=i−1−W, hi=i−1）／本反証の全統計は i0 以降の格子 close のみ／wake 検出子は i0−1..i0−3 の既知足のみ／|z| マッチは候補足の**同時点の r** のみで選択（将来は未使用）。')
P('- survivorship: 単一銘柄・連続 CFD・事象の除外は 窓 flat/ブレイク跨ぎ/双子無し のみ（上記）。')

# ---------------- A7 ----------------
P('\n## A7 受け取れるか（在 raw を額面どおり取った場合）')
m = ok12 & WIN['在 2010-20'] & (arm == 'UJ')
mm, se, n, g = clus(D12[m], etd[m]); bp = mm * np.mean(sig[m]); px = float(np.median(cl[i0[m]])); usd = bp / 1e4 * px
rt = 0.16
P(f'- 在 D\'_12 {mm:+.3f}σ = {bp:+.2f} bp = {usd:+.4f} USD／本・往復コスト {rt} USD → net@1× {usd-rt:+.4f} USD・net@2× {usd-2*rt:+.4f} USD・σ 単位 net@1× {mm-DELTA:+.3f}σ (t {(mm-DELTA)/se:+.2f})・net@2× {mm-2*DELTA:+.3f}σ (t {(mm-2*DELTA)/se:+.2f})')
P(f'- 年間本数: 在 UJ {n} 本 / 11 年 = {n/11:.0f} 本/年 → net@1× {(usd-rt)*n/11:+.2f} USD/年（risk 1 本 ≈ σ_trail 中央 {np.median(sig[m]):.2f} bp ≈ {np.median(sig[m])/1e4*px:.3f} USD）')
# 陽性対照 (b): 生 C_1
D1, _, ok1, _ = paired(K=1, shift=0)
m1 = ok1 & WIN['在 2010-20'] & (arm == 'UJ'); mm1, se1, n1, g1 = clus(D1[m1], etd[m1])
P(f'- 陽性対照 (b) 生 C_1 在 UJ: {mm1:+.3f}σ (t {mm1/se1:+.2f}・n {n1}) vs c60 −0.007 (t −0.1) → {"OK" if abs(mm1+0.007)<0.01 else "差異"}')

# ---------------- verdicts ----------------
P('\n## 判定（事前固定・GATE G PASS が前提）')
P(f'- **T1（在 95% 下限 +0.05σ で反転を全排除）= {T1}**')
P(f'- **T2（継続は ET08-10・小 |z| に局在＝裾と組成の顔）= {T2}**（置換 p {pval:.3f}）')
P(f'- **T3（0.20σ は構造的に判定不能・実効 MDE 0.42σ が床）= {T3}**（最良 {best[0]} {best[1]:.3f}σ）')
P(f'- **T4（UJ 純化には米マクロ全暦【要取得】が必要）= {T4}**（wake flag {flag_rate*100:.0f}%・|Δ LB| {abs(lb_cl-lb_all):.3f}σ）')
P('- 多重検定: c60 ≈135 ＋ 本反証 ≈90 → M ≈ 225・全族 Bonferroni 必要 |z| ≈ 3.68')
P(f'\n実行 {el()}・乱数 = ブートストラップ/置換のみ（seed {SEED}）・MT5 なし・外部通信なし・多年 scan なし')
open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(LINES))
open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(LINES))
print('written', OUT_MD)
