# -*- coding: utf-8 -*-
"""
[REFUTE 2026-11-24 03:30] 反証レーン — 対象: cycle63 (00:40) が **肯定形で「確定」と書いた唯一の主張**
  T1: 「分布の形の変化は z 3.8〜4.0 で確定」= 在 UJ の ヒンジ λ_lo 1.091 / λ_hi 1.685（差 +0.594・findings の「差 z ≈3.8」）
      ＝「ジャンプ後 1h は上側（継続方向）の尺度が下側の 1.5〜1.7 倍に広がる非対称拡大」
  T2: 「模型 A は事象分布を記述していない（残差 U 字・端点 z 4.0）」→ 「事象分布は双子の位置・尺度族の中に無い」
  T3: 「位置母数は識別されない（μ は −0.29〜+0.63σ）」（c63 の主知見・ただし underpowered 判定なので破る余地は小）
  T4: 「λ_A > 1（尺度拡大 1.25〜1.45×）は c47 の分散拡大の確認」

PROMOTED.md は空＝昇格候補ゼロ。c63 の主判定は underpowered（＝破る余地なし）なので、
**c63 が「確定」と断言した形の主張（T1/T2）を攻撃する**。c63 自身が最重大反証として登記した決着条件
（「独立データで同じ U 字と λ_hi/λ_lo >1.4 が出るか = US500 の 5σ ジャンプで事前固定し直す」）も走らせる。
US500_m5_close.npz は data/macro に存在する（c63 が「US500 npz は close のみ」と書いたのは
ヒゲ/レンジ共変量の話で、close だけで作れる λ_hi/λ_lo の形テストには効かない＝c63 の見送り理由は本テストには当たらない）。

=== 事前固定（この docstring を数字を見る前に書いた・seed 20261124・乱数はブートストラップ/置換のみ）===
GATE: c63 の主セル（在 2010-20・UJ・K=12・双子 ±7 の 2 本・p 格子 5..95）を点推定で再現する。
  μ_A +0.495 / λ_A 1.377 / μ_B −0.289 / λ_lo 1.091 / λ_hi 1.685 を |Δ| ≤ 0.005 で再現できなければ停止（数字を一切報告しない）。

攻撃 A（差の se を正しく出す）: c63 の「差 z ≈3.8」は λ_hi(se .133) と λ_lo(se .084) の se を独立合成した値
  （sqrt(.133²+.084²)=.157 → 3.78）に一致する。λ_lo と λ_hi は**同一回帰・同一 19 分位点・同一 bootstrap 反復**の
  関数なので共分散を無視できない。同一反復内の差 (λ_hi−λ_lo) を直接 bootstrap して se_joint と corr を出す。
  判定: z_joint を正とする。|z_joint| < 2.0 → T1 broken。2.0〜3.7 → 多重検定（攻撃 H）で再判定。

攻撃 B（プラセボ①: 符号ランダム化）: C' は事象側・双子側ともジャンプ符号 s で符号づけされている。
  s を事象ごとに独立な ±1（ET 日単位で振る・B=400）に置換して λ_hi−λ_lo を再計算。
  T1 が「継続方向の非対称」なら置換で消えるべき。置換分布の 97.5 分位 ≥ 観測 +0.594 なら **T1 broken**
  （＝符号と無関係に出る＝「継続方向」という解釈が成り立たない）。消えるなら T1 はこの攻撃を survive。

攻撃 C（プラセボ②: 非ジャンプアンカー）: 事象の σ・s・ET 分（つまり設計と正規化）をそのまま使い、
  アンカーだけを i0 から Δ ∈ {+1d, +2d, +3d} ずらした「ジャンプでない足」（|r| < 4σ を要求）に置換し、
  その双子（±7d）に対して同じヒンジを当てる。λ_hi−λ_lo が観測と同程度に出るなら
  **非対称は「ジャンプ後」の性質でなく設計（s 符号づけ＋σ 正規化＋無条件双子）の性質＝T1 broken**。
  判定: 3 つの Δ のうち 2 つ以上で (λ_hi−λ_lo) ≥ 0.594·0.5 かつ z_joint ≥ 2.0 → broken。

攻撃 D（推定子の帰無校正・T1 と T2 の共通の帰無）: 「事象 = 双子を純粋に位置・尺度変換したもの」
  （x = μ̂_A + λ̂_A·(双子からの ET 日クラスタ再抽出)）から合成事象を n_E 本作り、同じヒンジ/模型 A を当てる（B=1000）。
  母集団では λ_lo = λ_hi = λ_A・残差 ≡ 0。この帰無で
   (i) (λ̂_hi − λ̂_lo) の平均（バイアス）と sd → 観測 +0.594 の経験 p
   (ii) 残差端点 z（p5/p95）の |z| の分布 → 観測 4.0 / 2.4 の経験 p
  判定: 経験 p ≥ 0.05 なら該当主張 broken（推定子が有限 n・肥大裾で勝手に作る量）。
  ※この帰無は「事象分布が双子の位置尺度族に属する」という T2 の帰無そのものなので、T2 の正しい検定でもある。

攻撃 E（裾を抜く・格子感度）: p 格子 10..90／15..85／25..75 で λ_lo/λ_hi と z_joint。
  p5/p95 を抜いて非対称が消えるなら T1 は「両端の 5% 分位 2 点」＝在 n 655 の上下 33 本に載った主張。

攻撃 F（影響度）: 事象側の上位 1/3/5 本（C' 最大）を落とす・下位 5 本を落とす・ET 日 drop-one の最大影響。
  上位 5 本（n の 0.8%）の除去で (λ_hi−λ_lo) が半分未満になるなら T1 は数本の事象の主張。

攻撃 G（在/外・D2）: 外 2021-26H1・近年 2024-26H1 の z_joint。外で |z_joint| < 2.0 なら
  「確定」は在限定＝T1 は「在 2010-20 の記述」に格下げ（D2 に従い在→外の順で読む）。

攻撃 H（多重検定）: c63 自身が「記述 ≈40 セル・全族 c60∪反証∪本 ≈265 → 必要 |z| 3.7」と書いた。
  z_joint に対し Bonferroni（40・265）と Holm を当てる。c63 は「通るのは λ_hi−λ_lo の形セルのみ」と主張したので、
  形セルが 265 族で生き残るかを数字で確認する。

攻撃 I（独立市場・c63 登記の決着条件）: US500_m5_close.npz（および比較のため XAU_m5_close.npz）で
  **c45 仕様の近似**（σ_trail = 直前 288 本の非 flat r の std・厳密 trailing／|r| ≥ 5σ_trail／±288 本デクラスタ）で
  5σ ジャンプを作り、同じ C'（s 符号・σ 正規化・K=12・アンカー i0+1）・同じ双子（±7d・同 ET 時分・|r|<4σ）で
  ヒンジを当てる。UJ/ANN 分類（米マクロ暦）は使えないので**全ジャンププール**（＝c63 の UJ セルより広い）。
  まず XAU-近似が c63 の非対称（λ_hi/λ_lo ≥ 1.4）を再現するかを確認（＝近似の妥当性ゲート）。
  判定: XAU-近似で再現し US500-近似で λ_hi/λ_lo < 1.2 かつ z_joint < 2 → T1 は「金固有」＝c63 の
  「形が変わる」という一般形の主張は broken（金限定に格下げ）。両方で出れば T1 survived（強化）。

攻撃 J（双子の切断がもたらす λ の機械項・T4）: 双子は |r[anchor]| < 4σ で切断されている（事象側は無制限）。
  ボラ・クラスタリング下でこの切断は双子の窓リターンの裾を削る＝λ_A > 1 の一部は機械項。
  切断を外した双子で λ_A・λ_lo・λ_hi を再計算し、機械項の大きさを書く。
  判定: 切断除去で λ_A が 1.0 の側に 50% 以上動くなら T4（「λ>1 は c47 の分散拡大」）の大きさは broken。

事前の予測（数字を見る前）: A の z_joint は 3.5〜4.5（corr>0 なので c63 の naive より大きい）＝A では壊れない。
  B は消える（符号づけに依存する）。C は Δ=+1d で部分的に出る（c47 のボラ減衰の残り）が +3d では消える。
  D は (λ_hi−λ_lo) の帰無 sd ≈ 0.15・バイアス ≈ 0 → 経験 p < 0.01（T1 は D を survive）だが
  残差端点 |z| の帰無分布は 2〜3 まで伸びる（＝T2 の「z 4.0 は誤特定の証拠」は弱まる）。
  E は p25..75 で消える（裾の主張）。F は上位 5 本で 3 割縮む。G は外 z_joint ≈ 1.2（在限定）。
  I は US500 でも λ_hi > λ_lo が出る（公的な非対称ボラの一般形）。J は λ_A が 1.377 → 1.30 程度（機械項 ≈2 割）。
  総合の事前予測 = T1 は「在限定・裾由来・符号依存」に縮むが完全には壊れない＝inconclusive 寄り。

書き込みは AUREL_RESEARCH/ 配下のみ（scripts/refute_c63_shapeasym.py・data/refute_c63_shapeasym.md・同 _run.log）。
発注なし・本番ファイル編集なし・プロセス/執行機/ライブサーバ/schtask 接触なし・MT5 なし・外部通信なし・プロップ参照なし・秘密読取なし。
"""
import os, sys, math, time, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass

T0 = time.time(); SEED = 20261124
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT_MD = os.path.join(DATA, 'refute_c63_shapeasym.md'); OUT_LOG = os.path.join(DATA, 'refute_c63_shapeasym_run.log')
L = []
def P(s=''):
    print(s); L.append(s)
def el(): return f'{time.time()-T0:.1f}s'
def flush():
    open(OUT_LOG, 'w', encoding='utf-8').write('\n'.join(L)); open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L))

P(f'# [REFUTE] c63 の「形の非対称拡大は z 3.8〜4.0 で確定」を壊しにいく  {dt.datetime.now():%Y-%m-%d %H:%M}')
P('対象 = 在 UJ K=12 双子2本 p5..95 の λ_lo 1.091 / λ_hi 1.685（差 +0.594・c63 の「差 z ≈3.8」）＋残差端点 z 4.0')
P('')

# ============================ 共通基盤（c63 と同一構成） ============================
ev = pd.read_csv(os.path.join(DATA, 'c45_jumps_5sigma_declustered.csv'))
z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_close.npz')); ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); N = len(ts)
lc = np.log(cl); r = np.r_[np.nan, np.diff(lc)] * 1e4; flat = ~(np.isfinite(r) & (r != 0))
NY = ZoneInfo('America/New_York'); tny = pd.to_datetime(ts, unit='s', utc=True).tz_convert(NY)
hr = tny.hour.to_numpy(); mn = tny.minute.to_numpy(); brk = (hr == 17) | ((hr == 18) & (mn < 10))
cf = np.concatenate([[0], np.cumsum(flat.astype(np.int64))]); cb = np.concatenate([[0], np.cumsum(brk.astype(np.int64))])
def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N-1); return np.where(ts[i] == t, i, -1)
tsev = ev.ts.to_numpy(np.int64); i0 = gidx(tsev); s = np.sign(ev.r_bp.to_numpy()); sig = ev.sigma_bp.to_numpy(float)
yr = pd.to_datetime(ev.et_date).dt.year.to_numpy(); etd = ev.et_date.to_numpy(); cls = ev.cls.to_numpy(); slot = ev.sched_slot.to_numpy()
arm = np.where(cls == 'UJ', 'UJ', np.where(cls == 'SJ', 'SJ', np.where(slot == 1, 'ANN', 'EVO')))
WIN = {'在 2010-20': (yr <= 2020), '外 2021-26H1': (yr >= 2021), '近年 2024-26H1': (yr >= 2024)}
P(f'c45 cache {len(ev)} 事象・XAU npz {N} 本・flat {flat.mean()*100:.1f}%・格子一致 {np.mean(i0>=0)*100:.2f}%  ({el()})')

def win_ok(i, K, sh=1):
    a = i + sh; b = i + sh + K; inr = (i >= 0) & (b < N) & (a >= 1)
    aa = np.clip(a, 0, N); bb = np.clip(b + 1, 0, N)
    return inr & ((cb[bb] - cb[aa]) == 0) & ((cf[bb] - cf[aa]) <= max(1, int(0.10 * (K + 1))))
def Cm(i, K, sh=1, sgn=None, sg=None):
    sgn = s if sgn is None else sgn; sg = sig if sg is None else sg
    a = np.clip(i + sh, 0, N-1); b = np.clip(i + sh + K, 0, N-1); return sgn * (lc[b] - lc[a]) * 1e4 / sg
def twins_at(base_ts, days, K, sgn=None, sg=None, trunc=True):
    sgn = s if sgn is None else sgn; sg = sig if sg is None else sg
    out = []
    for d in days:
        it = gidx(base_ts + d * 86400); rr = np.where(it >= 0, np.abs(r[np.maximum(it, 0)]), np.inf)
        okT = win_ok(it, K) & (it >= 0) & np.isfinite(rr)
        if trunc: okT = okT & (rr < 4 * sg)
        out.append((Cm(it, K, sgn=sgn, sg=sg), okT))
    return out

PS_MAIN = np.arange(5, 96, 5)
def qfit(xe, xt, ps):
    qE = np.percentile(xe, ps); qT = np.percentile(xt, ps)
    X = np.c_[np.ones(len(ps)), qT]; bA = np.linalg.lstsq(X, qE, rcond=None)[0]
    resA = qE - X @ bA
    mT = np.percentile(xt, 50); dq = qT - mT
    XB = np.c_[np.ones(len(ps)), np.minimum(dq, 0), np.maximum(dq, 0)]; bB = np.linalg.lstsq(XB, qE, rcond=None)[0]
    return dict(muA=bA[0], lamA=bA[1], resA=resA, muB=bB[0], lam_lo=bB[1], lam_hi=bB[2], qE=qE, qT=qT, mT=mT)

rng = np.random.default_rng(SEED)
def cluster_prep(g):
    code, uq = pd.factorize(g); G = len(uq); order = np.argsort(code, kind='stable')
    cnt = np.bincount(code, minlength=G); st = np.r_[0, np.cumsum(cnt)[:-1]]
    return order, cnt, st, G
def boot_idx(g, B):
    order, cnt, st, G = cluster_prep(g)
    for _ in range(B):
        pick = rng.integers(0, G, G)
        yield np.concatenate([order[st[p]:st[p]+cnt[p]] for p in pick])

def analyse(xe, ge, xt, gt, ps=PS_MAIN, B=1000):
    """returns point fit + bootstrap matrix (joint per-replicate)."""
    f = qfit(xe, xt, ps)
    rows = []
    for ie, it in zip(boot_idx(ge, B), boot_idx(gt, B)):
        g = qfit(xe[ie], xt[it], ps)
        rows.append([g['muA'], g['lamA'], g['muB'], g['lam_lo'], g['lam_hi'], g['lam_hi'] - g['lam_lo']] + list(g['resA']))
    M = np.array(rows)
    f['bs'] = M; f['se'] = M.std(axis=0, ddof=1); f['nE'] = len(xe); f['nT'] = len(xt)
    f['dlam'] = f['lam_hi'] - f['lam_lo']
    f['se_dlam_joint'] = float(M[:, 5].std(ddof=1))
    f['se_dlam_naive'] = float(math.sqrt(M[:, 3].var(ddof=1) + M[:, 4].var(ddof=1)))
    f['corr_lohi'] = float(np.corrcoef(M[:, 3], M[:, 4])[0, 1])
    f['z_joint'] = f['dlam'] / f['se_dlam_joint'] if f['se_dlam_joint'] > 0 else np.nan
    f['z_naive'] = f['dlam'] / f['se_dlam_naive'] if f['se_dlam_naive'] > 0 else np.nan
    f['pc_dlam'] = np.percentile(M[:, 5], [2.5, 97.5])
    return f
def pool(a, wm, K, twl, sgn=None):
    sgn = s if sgn is None else sgn
    okE = win_ok(i0, K); CE = Cm(i0, K, sgn=sgn); base = okE & wm & (arm == a)
    xe = CE[base]; ge = etd[base]
    xt = np.concatenate([c[okT & wm & (arm == a)] for c, okT in twl]); gt = np.concatenate([etd[okT & wm & (arm == a)] for c, okT in twl])
    return xe, ge, xt, gt
def fline(tag, f):
    P(f'- {tag}: λ_lo {f["lam_lo"]:.3f} (se {f["se"][3]:.3f})／λ_hi {f["lam_hi"]:.3f} (se {f["se"][4]:.3f})・'
      f'**差 {f["dlam"]:+.3f} (se_joint {f["se_dlam_joint"]:.3f}・z_joint {f["z_joint"]:+.2f}'
      f'・se_naive {f["se_dlam_naive"]:.3f}・z_naive {f["z_naive"]:+.2f}・corr(λlo,λhi) {f["corr_lohi"]:+.2f})**・'
      f'λ_hi/λ_lo {f["lam_hi"]/f["lam_lo"]:.2f}・λ_A {f["lamA"]:.3f}・μ_A {f["muA"]:+.3f}・μ_B {f["muB"]:+.3f}・n {f["nE"]}/{f["nT"]}')

# ============================ GATE ============================
P('\n## 0. GATE — c63 主セルの点推定を再現（|Δ| ≤ 0.005・合わなければ停止）')
tw2 = twins_at(tsev, (-7, 7), 12)
xe0, ge0, xt0, gt0 = pool('UJ', WIN['在 2010-20'], 12, tw2)
g0 = qfit(xe0, xt0, PS_MAIN)
TGT = dict(muA=0.495, lamA=1.377, muB=-0.289, lam_lo=1.091, lam_hi=1.685)
dmax = 0.0
for k, v in TGT.items():
    d = abs(g0[k] - v); dmax = max(dmax, d)
    P(f'- {k}: 本レーン {g0[k]:+.4f} vs c63 {v:+.4f}  |Δ| {d:.4f}')
P(f'- n 事象 {len(xe0)}（c63 655）・n 双子 {len(xt0)}（c63 1252）')
if dmax > 0.005 or abs(len(xe0) - 655) > 1:
    P('!! GATE FAIL — c63 の主セルを再現できない。数字を報告せず停止'); flush(); sys.exit(1)
P(f'**GATE PASS**（max|Δ| {dmax:.4f}）  ({el()})')

# ============================ A: 差の se を正しく出す ============================
P('\n## A. 攻撃A — 「差 z ≈3.8」の se を同一 bootstrap 反復で正しく出す（B=1000・ET 日クラスタ）')
fA = analyse(xe0, ge0, xt0, gt0, PS_MAIN, B=1000)
fline('在 2010-20 UJ K=12 p5..95（主セル）', fA)
P(f'  - c63 の naive 合成 sqrt(.133²+.084²)=0.157 → z 3.78。本レーンの se_naive {fA["se_dlam_naive"]:.3f}（再現）・'
  f'**正しい se_joint {fA["se_dlam_joint"]:.3f} → z_joint {fA["z_joint"]:+.2f}**・百分位 CI95 [{fA["pc_dlam"][0]:+.3f},{fA["pc_dlam"][1]:+.3f}]')
vA = 'broken' if abs(fA['z_joint']) < 2.0 else ('攻撃H へ' if abs(fA['z_joint']) < 3.7 else 'survived（A では壊れない）')
P(f'  - 攻撃A 判定: **{vA}**（事前規則 |z_joint|<2.0→broken・2.0〜3.7→多重検定で再判定）')
flush()

# ============================ B: プラセボ① 符号ランダム化 ============================
P('\n## B. 攻撃B — プラセボ①: ジャンプ符号 s を独立 ±1 に置換（ET 日単位・B=400）')
BB = 400
rng_b = np.random.default_rng(SEED + 1)
code_d, uq_d = pd.factorize(etd)
obs = fA['dlam']; perm = []
for _ in range(BB):
    flip = rng_b.choice([-1.0, 1.0], size=len(uq_d))[code_d]
    sp = s * flip
    twp = twins_at(tsev, (-7, 7), 12, sgn=sp)
    xe, ge, xt, gt = pool('UJ', WIN['在 2010-20'], 12, twp, sgn=sp)
    gq = qfit(xe, xt, PS_MAIN); perm.append(gq['lam_hi'] - gq['lam_lo'])
perm = np.array(perm)
p_B = float(np.mean(perm >= obs))
P(f'- 置換分布 (λ_hi−λ_lo): 平均 {perm.mean():+.3f}・sd {perm.std(ddof=1):.3f}・'
  f'[p2.5 {np.percentile(perm,2.5):+.3f}, p50 {np.percentile(perm,50):+.3f}, p97.5 {np.percentile(perm,97.5):+.3f}]')
P(f'- 観測 {obs:+.3f} の片側経験 p = **{p_B:.4f}**（{int(np.sum(perm>=obs))}/{BB}）')
vB = 'broken（符号と無関係に出る）' if np.percentile(perm, 97.5) >= obs else 'survived（符号づけ依存＝「継続方向の非対称」と整合）'
P(f'- 攻撃B 判定: **{vB}**  ({el()})')
flush()

# ============================ C: プラセボ② 非ジャンプアンカー ============================
P('\n## C. 攻撃C — プラセボ②: 設計（s 符号・σ 正規化・無条件双子）はそのまま、アンカーを +Δ 日ずらした非ジャンプ足に置換')
P('   （要求: その足が格子に存在・|r| < 4σ_event・窓 ok。双子は ずらしたアンカーの ±7d）')
rowsC = []
for dd in (1, 2, 3, 5):
    tsp = tsev + dd * 86400
    ip = gidx(tsp)
    rr = np.where(ip >= 0, np.abs(r[np.maximum(ip, 0)]), np.inf)
    okA = (ip >= 0) & np.isfinite(rr) & (rr < 4 * sig) & win_ok(ip, 12)
    twp = twins_at(tsp, (-7, 7), 12)
    okE = okA; CE = Cm(ip, 12)
    base = okE & WIN['在 2010-20'] & (arm == 'UJ')
    xe = CE[base]; ge = etd[base]
    xt = np.concatenate([c[okT & WIN['在 2010-20'] & (arm == 'UJ')] for c, okT in twp])
    gt = np.concatenate([etd[okT & WIN['在 2010-20'] & (arm == 'UJ')] for c, okT in twp])
    if len(xe) < 100: P(f'- Δ=+{dd}d: n {len(xe)} <100 skip'); continue
    f = analyse(xe, ge, xt, gt, PS_MAIN, B=400)
    fline(f'プラセボ Δ=+{dd}d（非ジャンプアンカー）', f); rowsC.append((dd, f))
nC = sum(1 for dd, f in rowsC if f['dlam'] >= 0.5 * obs and f['z_joint'] >= 2.0)
vC = f'broken（{nC}/{len(rowsC)} の Δ でジャンプ無しでも観測の半分以上＋z≥2）' if nC >= 2 else f'survived（{nC}/{len(rowsC)} のみ・ジャンプ固有）'
P(f'- 攻撃C 判定: **{vC}**（事前規則 2 つ以上で broken）  ({el()})')
flush()

# ============================ D: 推定子の帰無校正 ============================
P('\n## D. 攻撃D — 推定子の帰無校正: 「事象 = 双子の純粋な位置・尺度変換」から合成（母集団で λ_lo=λ_hi・残差≡0）')
BD = 1000
rng_d = np.random.default_rng(SEED + 2)
mu_hat, lam_hat = g0['muA'], g0['lamA']
orderE, cntE, stE, GE = cluster_prep(ge0)
orderT, cntT, stT, GT = cluster_prep(gt0)
dl_null = np.zeros(BD); z_rel = np.zeros((BD, len(PS_MAIN)))
res_null = np.zeros((BD, len(PS_MAIN)))
for b in range(BD):
    # 合成事象: 双子からクラスタ再抽出 → 位置尺度変換
    pickT = rng_d.integers(0, GT, GT)
    idxT = np.concatenate([orderT[stT[p]:stT[p]+cntT[p]] for p in pickT])
    draw = xt0[idxT]
    sel = rng_d.integers(0, len(draw), len(xe0))
    xe_syn = mu_hat + lam_hat * draw[sel]
    ge_syn = gt0[idxT][sel]
    gq = qfit(xe_syn, xt0, PS_MAIN)
    dl_null[b] = gq['lam_hi'] - gq['lam_lo']; res_null[b] = gq['resA']
p_D = float(np.mean(dl_null >= obs))
P(f'- 帰無 (λ_hi−λ_lo): 平均 {dl_null.mean():+.4f}（バイアス）・sd {dl_null.std(ddof=1):.4f}・'
  f'[p2.5 {np.percentile(dl_null,2.5):+.3f}, p97.5 {np.percentile(dl_null,97.5):+.3f}, p99.9 {np.percentile(dl_null,99.9):+.3f}]')
P(f'- 観測 {obs:+.3f} の経験 p = **{p_D:.4f}**（{int(np.sum(dl_null>=obs))}/{BD}）・帰無 sd 換算 z = {(obs-dl_null.mean())/dl_null.std(ddof=1):+.2f}')
# 残差端点: 観測の z（c63 と同じ se = bootstrap se）と、帰無での |z| 分布
se_res = fA['se'][6:]
res_obs = g0['resA']; z_obs = res_obs / np.where(se_res > 0, se_res, np.nan)
z_null = res_null / np.where(se_res > 0, se_res, np.nan)
P(f'- 残差 e(p) 観測 z: ' + ' '.join(f'p{p} {zz:+.1f}' for p, zz in zip(PS_MAIN, z_obs) if p in (5, 25, 50, 75, 95)) + f'・max|z| {np.nanmax(np.abs(z_obs)):.1f}')
for p_i, p_lab in ((0, 'p5'), (len(PS_MAIN)-1, 'p95')):
    zz = z_null[:, p_i]; pe = float(np.mean(np.abs(zz) >= abs(z_obs[p_i])))
    P(f'- 帰無での |z({p_lab})|: 平均 {np.abs(zz).mean():.2f}・p95 {np.percentile(np.abs(zz),95):.2f}・'
      f'観測 |{z_obs[p_i]:+.2f}| の経験 p = **{pe:.4f}**')
mx_null = np.nanmax(np.abs(z_null), axis=1); pe_mx = float(np.mean(mx_null >= np.nanmax(np.abs(z_obs))))
P(f'- 帰無での max_p|z|: 平均 {mx_null.mean():.2f}・p95 {np.percentile(mx_null,95):.2f}・観測 {np.nanmax(np.abs(z_obs)):.2f} の経験 p = **{pe_mx:.4f}**')
vD1 = 'survived' if p_D < 0.05 else 'broken（有限 n・肥大裾で推定子が勝手に作る）'
vD2 = 'survived（T2 の誤特定は帰無でも説明できない）' if pe_mx < 0.05 else 'broken（T2 の「端点 z 4.0 = 位置尺度族に属さない証拠」は帰無でも出る）'
P(f'- 攻撃D 判定: T1 **{vD1}**（p {p_D:.4f}）／T2 **{vD2}**（max|z| p {pe_mx:.4f}）  ({el()})')
flush()

# ============================ E: 格子感度（裾を抜く） ============================
P('\n## E. 攻撃E — 格子から裾を抜く（p5/p95 を落とす）')
for nm, ps in [('p 5..95（主）', np.arange(5, 96, 5)), ('p 10..90', np.arange(10, 91, 5)),
               ('p 15..85', np.arange(15, 86, 5)), ('p 25..75', np.arange(25, 76, 5))]:
    f = analyse(xe0, ge0, xt0, gt0, ps, B=400); fline(f'在 UJ {nm}', f)
f2575 = analyse(xe0, ge0, xt0, gt0, np.arange(25, 76, 5), B=400)
vE = 'broken（裾 2 点の主張）' if abs(f2575['z_joint']) < 2.0 else 'survived（裾を抜いても残る）'
P(f'- 攻撃E 判定: **{vE}**（p25..75 の z_joint {f2575["z_joint"]:+.2f}）  ({el()})')
flush()

# ============================ F: 影響度 ============================
P('\n## F. 攻撃F — 影響度（事象側の極値除去・ET 日 drop-one）')
ordE = np.argsort(xe0)
for k in (1, 3, 5, 10):
    keep = np.ones(len(xe0), bool); keep[ordE[-k:]] = False
    gq = qfit(xe0[keep], xt0, PS_MAIN)
    P(f'- 上位 {k} 本除去（{k/len(xe0)*100:.1f}%）: λ_lo {gq["lam_lo"]:.3f}／λ_hi {gq["lam_hi"]:.3f}・差 {gq["lam_hi"]-gq["lam_lo"]:+.3f}（観測比 {(gq["lam_hi"]-gq["lam_lo"])/obs:.2f}）・μ_A {gq["muA"]:+.3f}')
for k in (1, 5):
    keep = np.ones(len(xe0), bool); keep[ordE[:k]] = False
    gq = qfit(xe0[keep], xt0, PS_MAIN)
    P(f'- 下位 {k} 本除去: λ_lo {gq["lam_lo"]:.3f}／λ_hi {gq["lam_hi"]:.3f}・差 {gq["lam_hi"]-gq["lam_lo"]:+.3f}（観測比 {(gq["lam_hi"]-gq["lam_lo"])/obs:.2f}）')
uq_e = pd.unique(ge0); jk = []
for d in uq_e:
    keep = ge0 != d
    if keep.sum() < 100: continue
    gq = qfit(xe0[keep], xt0, PS_MAIN); jk.append((d, gq['lam_hi'] - gq['lam_lo']))
jk_v = np.array([v for _, v in jk]); i_mn = int(np.argmin(jk_v))
P(f'- ET 日 drop-one（{len(jk)} 日）: 差の min {jk_v.min():+.3f}（{jk[i_mn][0]}・観測比 {jk_v.min()/obs:.2f}）・max {jk_v.max():+.3f}・sd {jk_v.std(ddof=1):.4f}')
keep5 = np.ones(len(xe0), bool); keep5[ordE[-5:]] = False
g5 = qfit(xe0[keep5], xt0, PS_MAIN)
vF = 'broken（数本の事象の主張）' if (g5['lam_hi'] - g5['lam_lo']) < 0.5 * obs else 'survived（極値除去に耐える）'
P(f'- 攻撃F 判定: **{vF}**（上位 5 本除去で観測比 {(g5["lam_hi"]-g5["lam_lo"])/obs:.2f}・事前規則 <0.50 で broken）  ({el()})')
flush()

# ============================ G: 在/外/近年 ============================
P('\n## G. 攻撃G — D2（在→外）: 外 2021-26H1・近年 2024-26H1 の z_joint')
fw = {}
for w in ['在 2010-20', '外 2021-26H1', '近年 2024-26H1']:
    xe, ge, xt, gt = pool('UJ', WIN[w], 12, tw2)
    f = analyse(xe, ge, xt, gt, PS_MAIN, B=600); fw[w] = f; fline(f'UJ {w}', f)
vG = 'broken（在限定の記述に格下げ）' if abs(fw['外 2021-26H1']['z_joint']) < 2.0 else 'survived（外でも有意）'
P(f'- 攻撃G 判定: **{vG}**（外 z_joint {fw["外 2021-26H1"]["z_joint"]:+.2f}・近年 {fw["近年 2024-26H1"]["z_joint"]:+.2f}）  ({el()})')
flush()

# ============================ H: 多重検定 ============================
P('\n## H. 攻撃H — 多重検定（c63 自身の族サイズ 40 / 265・必要 |z| 3.7）')
from math import erfc
def p2(zv): return erfc(abs(zv) / math.sqrt(2))
zj = fA['z_joint']
for M in (1, 40, 265):
    pv = p2(zj); P(f'- 族 M={M}: 素 p {pv:.3e}・Bonferroni p {min(1.0, pv*M):.4f}・{"PASS" if pv*M < 0.05 else "FAIL"} (α=0.05)')
P(f'- 経験帰無（攻撃D）由来の p {p_D:.4f} に Bonferroni: M=40 → {min(1.0,p_D*40):.4f}・M=265 → {min(1.0,p_D*265):.4f}')
P(f'- 置換（攻撃B）由来の p {p_B:.4f} に Bonferroni: M=40 → {min(1.0,p_B*40):.4f}・M=265 → {min(1.0,p_B*265):.4f}')
P(f'- c63 の必要 |z| 3.7 に対し z_joint {zj:+.2f} → {"通る" if abs(zj) >= 3.7 else "通らない"}')
flush()

# ============================ I: 独立市場（c63 登記の決着条件） ============================
P('\n## I. 攻撃I — 独立市場（c63 が登記した決着条件）: c45 仕様の近似で XAU / US500 / US100 の 5σ ジャンプを作り同じヒンジ')
P('   近似仕様: σ_trail = 直前 288 本の非 flat r の std（厳密 trailing・有効 ≥200 本要求）／|r| ≥ 5σ_trail／±288 本デクラスタ（|r|/σ 降順 greedy）')
P('   窓 = アンカー i+1 から K=12・13 本すべて非 flat（厳密）／双子 = ±7 日 同 ET 時分・同条件・|r[anchor]| < 4σ_event／UJ 分類なし（全ジャンププール）')

def build_market(path, label):
    zz = np.load(path); k = list(zz.keys())
    tsm = zz['ts'].astype(np.int64); clm = zz['close'].astype(float) if 'close' in k else zz[k[1]].astype(float)
    o = np.argsort(tsm); tsm, clm = tsm[o], clm[o]
    Nm = len(tsm); lcm = np.log(clm); rm = np.r_[np.nan, np.diff(lcm)] * 1e4
    flm = ~(np.isfinite(rm) & (rm != 0))
    rv = np.where(flm, np.nan, rm)
    sr = pd.Series(rv)
    sd = sr.rolling(288, min_periods=200).std().shift(1).to_numpy()
    cnt_ok = sr.notna().rolling(288, min_periods=1).sum().shift(1).to_numpy()
    sg = np.where((cnt_ok >= 200) & np.isfinite(sd) & (sd > 0), sd, np.nan)
    cand = np.where(np.isfinite(rm) & np.isfinite(sg) & (np.abs(rm) >= 5 * sg))[0]
    if len(cand) == 0: return None
    ratio = np.abs(rm[cand]) / sg[cand]; ordr = cand[np.argsort(-ratio)]
    kept = []; taken = np.zeros(Nm, bool)
    for i in ordr:
        a, b = max(0, i-288), min(Nm, i+289)
        if taken[a:b].any(): continue
        kept.append(i); taken[i] = True
    kept = np.array(sorted(kept))
    cfm = np.concatenate([[0], np.cumsum(flm.astype(np.int64))])
    def gidxm(t):
        i = np.clip(np.searchsorted(tsm, t), 0, Nm-1); return np.where(tsm[i] == t, i, -1)
    def wokm(i, K=12, sh=1):
        a = i + sh; b = i + sh + K; inr = (i >= 0) & (b < Nm) & (a >= 1)
        aa = np.clip(a, 0, Nm); bb = np.clip(b + 1, 0, Nm)
        return inr & ((cfm[bb] - cfm[aa]) == 0)
    def Cmm(i, sgn, sgv, K=12, sh=1):
        a = np.clip(i + sh, 0, Nm-1); b = np.clip(i + sh + K, 0, Nm-1); return sgn * (lcm[b] - lcm[a]) * 1e4 / sgv
    sgn = np.sign(rm[kept]); sgv = sg[kept]; tsk = tsm[kept]
    yk = pd.to_datetime(tsk, unit='s', utc=True).year.to_numpy()
    dk = pd.to_datetime(tsk, unit='s', utc=True).strftime('%Y-%m-%d').to_numpy()
    okE = wokm(kept); CE = Cmm(kept, sgn, sgv)
    TW = []
    for d in (-7, 7):
        it = gidxm(tsk + d * 86400); rr = np.where(it >= 0, np.abs(rm[np.maximum(it, 0)]), np.inf)
        okT = wokm(it) & (it >= 0) & np.isfinite(rr) & (rr < 4 * sgv)
        TW.append((Cmm(it, sgn, sgv), okT))
    P(f'- [{label}] npz {Nm} 本 {dt.datetime.fromtimestamp(int(tsm[0]), dt.UTC):%Y-%m}..{dt.datetime.fromtimestamp(int(tsm[-1]), dt.UTC):%Y-%m}・'
      f'flat {flm.mean()*100:.1f}%・5σ 候補 {len(cand)}・デクラスタ後 {len(kept)}・窓 ok {int(okE.sum())}')
    return dict(label=label, CE=CE, okE=okE, TW=TW, yk=yk, dk=dk)

mk = {}
for lab, fn in (('XAU-近似', 'XAU_m5_close.npz'), ('US500-近似', 'US500_m5_close.npz'), ('US100-近似', 'US100_m5_close.npz')):
    pth = os.path.join(DATA, 'macro', fn)
    if not os.path.exists(pth): P(f'- {lab}: {fn} 無し skip'); continue
    m = build_market(pth, lab)
    if m is not None: mk[lab] = m
    flush()

P('')
mres = {}
for lab, m in mk.items():
    for wn, wmask in (('在 ≤2020', m['yk'] <= 2020), ('外 ≥2021', m['yk'] >= 2021), ('全期間', np.ones(len(m['yk']), bool))):
        base = m['okE'] & wmask
        if base.sum() < 80: P(f'- {lab} {wn}: n {int(base.sum())} <80 skip'); continue
        xe = m['CE'][base]; ge = m['dk'][base]
        xt = np.concatenate([c[okT & wmask] for c, okT in m['TW']]); gt = np.concatenate([m['dk'][okT & wmask] for c, okT in m['TW']])
        if len(xt) < 80: P(f'- {lab} {wn}: 双子 n {len(xt)} <80 skip'); continue
        f = analyse(xe, ge, xt, gt, PS_MAIN, B=400); mres[(lab, wn)] = f
        fline(f'{lab} {wn}', f)
    flush()
gate_I = mres.get(('XAU-近似', '在 ≤2020'))
us = mres.get(('US500-近似', '全期間'))
if gate_I is not None and us is not None:
    rep = (gate_I['lam_hi'] / gate_I['lam_lo']) >= 1.4
    if not rep:
        vI = f'近似ゲート FAIL（XAU-近似 在 λ_hi/λ_lo {gate_I["lam_hi"]/gate_I["lam_lo"]:.2f} <1.4）＝攻撃I は不成立（近似が c63 の非対称を再現できない）'
    elif (us['lam_hi'] / us['lam_lo']) < 1.2 and abs(us['z_joint']) < 2.0:
        vI = f'broken（金固有に格下げ: US500 λ_hi/λ_lo {us["lam_hi"]/us["lam_lo"]:.2f}・z_joint {us["z_joint"]:+.2f}）'
    else:
        vI = f'survived・強化（市場横断で再現: US500 λ_hi/λ_lo {us["lam_hi"]/us["lam_lo"]:.2f}・z_joint {us["z_joint"]:+.2f}）'
else:
    vI = '判定不能（セル不足）'
P(f'- 攻撃I 判定: **{vI}**  ({el()})')
flush()

# ============================ J: 双子切断の機械項（T4） ============================
P('\n## J. 攻撃J — 双子の |r|<4σ 切断が λ に作る機械項（T4「λ>1 = c47 の分散拡大」の大きさ）')
tw2_nt = twins_at(tsev, (-7, 7), 12, trunc=False)
xeN, geN, xtN, gtN = pool('UJ', WIN['在 2010-20'], 12, tw2_nt)
fJ = analyse(xeN, geN, xtN, gtN, PS_MAIN, B=400)
fline('在 UJ 双子切断なし', fJ)
mv = (g0['lamA'] - fJ['lamA']) / max(1e-9, (g0['lamA'] - 1.0))
P(f'- λ_A 1.377（切断あり） → {fJ["lamA"]:.3f}（切断なし）: 1.0 に向かって {mv*100:.1f}% 移動（双子 n {len(xt0)} → {len(xtN)}）')
vJ = 'broken（λ>1 の過半は双子切断の機械項）' if mv >= 0.5 else 'survived（切断の寄与は小）'
P(f'- 攻撃J 判定: **{vJ}**  ({el()})')

# ============================ 総合 ============================
P('\n## 総合')
P(f'- A（差の se 修正）: z_naive {fA["z_naive"]:+.2f} → z_joint {fA["z_joint"]:+.2f}（corr {fA["corr_lohi"]:+.2f}）→ {vA}')
P(f'- B（符号置換プラセボ）: p {p_B:.4f} → {vB}')
P(f'- C（非ジャンプアンカープラセボ）: → {vC}')
P(f'- D（推定子の帰無校正）: T1 p {p_D:.4f} → {vD1}／T2 max|z| p {pe_mx:.4f} → {vD2}')
P(f'- E（裾抜き）: → {vE}')
P(f'- F（影響度）: → {vF}')
P(f'- G（外）: → {vG}')
P(f'- H（多重検定）: Bonferroni M=265 で {"PASS" if p2(zj)*265 < 0.05 else "FAIL"}')
P(f'- I（独立市場）: → {vI}')
P(f'- J（双子切断）: → {vJ}')
P(f'\n実行 {el()}')
flush()
print('written', OUT_MD)
