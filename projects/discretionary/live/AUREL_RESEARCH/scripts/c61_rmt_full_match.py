# -*- coding: utf-8 -*-
"""
[cycle61 研究レーン・深化・出口／path] 2026-11-23  seed 20261123（乱数未使用・決定論）
RMT（収益率マッチ双子）の完全マッチ版 — 「SL 決着後の反転」は取引と無関係な
「大きな逆行足の後の戻り（微細構造）」に完全に還元されるか。

--- 背景（数字を見る前に書く） ---
c59 (11-23 00:40): 決着後 1 時間の側符号つきドリフト D_12 は TP/SL 両腕 null。しかし SL 腕の先着 F'(±0.5R,48 本) と
符号率は在で z 3〜6 で立つ。c59 は「決着足アンカーの条件づけ＋在の lag1 負」の顔と読み、1 本ずらしを主にした（候補 91）。
反証 11-23 03:40: 在は 3 本ずらしても落ちない（sh0 +0.073 z 4.1 → sh3 +0.065 z 3.8）。外を落とすのはアンカーずらしではなく
対照の較正（RMT: 決着足の符号つき収益率 v = s·Δcl_x/risk を事象に合わせた双子）。ただし RMT は ±{7..42} 日の 12 候補から
最近傍 1 本を選ぶだけで **65% しか較正できず**（SL 在 事象 v −0.365R / RMT −0.237 / 残差 0.158R）、残差は在の効果を
水増しする向き。反証自身の最重大反証の決着条件 = **v を ±0.02R 以内で合わせる完全マッチ（候補 ±7〜±182 日）で在の F' が
+0.03 未満に落ちるか**。落ちれば「SL 後の反転」は全窓で微細構造に還元され、出口系統（決着前 c7/c21/c23/c2・決着後 c59）
は完全に閉じる。

--- 事前固定（判定規則はこの docstring が正本） ---
入力: data/refute_c4_scan_paths_2010_2026.json（再加速 closed 19404 本）・data/macro/XAU_m5_ohlc.npz（bid・完全格子）。
事象: exit ∈ {TP, SL}・決着足 ix = gidx(entry_time+300·hold)・ix 非 flat・前向き 48 本（sh 以降）非 flat。
対照（完全マッチ RMT）: 候補 = 事象の決着足から d = ±7k 日（k=1..26・同曜日・同 UTC 時刻）の格子足で、
  (a) 非 flat・cand−1 存在・前向き 48 本 非 flat・**米 DST 状態が事象と同じ**（UTC 固定ずらしで ET 時刻が 1 時間ずれるのを防ぐ）
  (b) v_c = s·(cl[c]−cl[c−1])/risk_E が |v_c − v_E| ≤ 0.02R。
  → 条件を満たす候補から |v_c − v_E| 最小の 1 本（M1・主）。候補が無い事象は落とす（脱落率を印字・脱落事象の生 F' も印字＝選択の検査）。
  M2（副）: M1 ∧ 決着足レンジ (hi−lo)/risk が事象の ×[0.8, 1.25] 以内。
  M3（副）: M1 ∧ 終値位置 cloc = s·(cl−(hi+lo)/2)/(hi−lo) が事象 ±0.15 以内（SL 足は定義上 安値寄りで閉じる＝その形も揃える）。
統計（事象 − 対照の対差・決着日クラスタ SE・MDE = 2SE）:
  S1 先着 F'(a=0.5R, 48 本) = P(+0.5R 先着) − P(−0.5R 先着)（sh=1 主・sh=0 併記）
  S2 符号率 P(C'_12 > 0)（sh=1）
  S3 水準 D_12 = C'_12 の対差（sh=1）
  S4 中央値差（記述）
較正ゲート: mean|v_R − v_E| ≤ 0.02R かつ |mean v_R − mean v_E| ≤ 0.01R を満たさなければ「較正失敗」として判定を保留。
プラセボ（機械の検査）: マッチ対照 R1 を擬似事象とし、同条件の 2 番目に近い候補 R2 を対照にした S1〜S3（0 のはず）。
陽性対照: SL 在 M1 sh1 の事象 path に δ=0.05R/時 の線形ドリフトを注入し ΔF' を印字（反証 sh1 +0.074 と同程度のはず）。
主セル: **SL 在 2010-20・M1・sh1・S1**（1 セル・Bonferroni なし）。
判定:
  H_RED（微細構造へ還元）  ⇔ 主セル D < +0.03 ∧ |z| < 2.0  → 「SL 後の反転」は取引と無関係・出口系統を完全に閉じる。
  H_TRADE（取引固有の残差）⇔ 主セル D ≥ +0.03 ∧ z ≥ 2.5 → 外（2021-26H1）で D > 0 ∧ z ≥ 1.5 なら在→外 再現・そうでなければ在のみ。
  それ以外 → inconclusive（数字を書いて残す）。
副（記述）: TP 腕（鏡像）・外/近年・M2/M3・sh0・a=0.25/1.0 バリア・符号率・水準。家族 ≈ 2 腕×3 窓×3 マッチ×2 sh×3 統計 = 108 セル
  → 記述セルの名目 |z| ≥ 2 は Bonferroni 必要 |z| 3.45 と並べて読む。
事前の予測: H_RED（反証の RMT 65% で在 F' +0.064 → 完全マッチで +0.03 未満）。根拠 = 3 窓すべてで「決着足が小さいほど F' が大きい」
  （反証 E3 再実施）は、決着足の形で説明される側に傾く。
事前の最重大反証候補: (1) 完全マッチは「同じ大きさの足」を揃えるが「その足が壁（SL 水準）で止められた足」であることは揃えない
  → 残差があれば壁の存在そのものの効果かもしれない（SL 水準に指値/逆指値が集積している Osler 型）。(2) bid 1 社。
  (3) 候補を ±182 日に広げると地合い（ボラ水準）が事象とずれる → M2（レンジ一致）で検査。
D2: 在/外/近年 窓別・16 年一括なし。
副作用: 書き込みは data/c61_rmt_full_match_result.md のみ。MT5 なし・外部通信なし・多年 scan なし。
"""
import os, json, math, time, datetime as dt
import numpy as np

T0 = time.time()
SEED = 20261123
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'c61_rmt_full_match_result.md')
L = []
def P(s=''):
    print(s); L.append(s)

# ---------- load (identical inputs to c59 / refute_c59) ----------
j = json.load(open(os.path.join(DATA, 'refute_c4_scan_paths_2010_2026.json'), encoding='utf-8'))['trades']
et   = np.array([t['entry_time'] for t in j], np.int64)
hold = np.array([t['hold'] for t in j], np.int64)
side = np.array([1 if t['side'] == 'BUY' else -1 for t in j])
risk = np.array([t['risk'] for t in j], float)
exitk= np.array([t['exit'] for t in j])
year = np.array([t['year'] for t in j])

z = np.load(os.path.join(DATA, 'macro', 'XAU_m5_ohlc.npz'))
ts = z['ts'].astype(np.int64); cl = z['close'].astype(float); hi = z['high'].astype(float); lo = z['low'].astype(float)
N = len(ts)
flat = np.zeros(N, bool); flat[1:] = (cl[1:] == cl[:-1]) & (hi[1:] == lo[1:])
cf = np.concatenate([[0], np.cumsum(flat)])

def gidx(t):
    i = np.clip(np.searchsorted(ts, t), 0, N - 1)
    return np.where(ts[i] == t, i, -1)

ix = gidx(et + 300 * hold)
day_x = np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] // 86400, -1)
base = (ix >= 1) & np.isin(exitk, ['TP', 'SL'])

def fwd_ok(i0, K, sh):
    iend = i0 + sh + K
    okr = (i0 >= 1) & (iend < N) & (i0 + sh >= 0)
    a = np.clip(i0 + sh, 0, N); b = np.clip(iend + 1, 0, N)
    return okr & ((cf[b] - cf[a]) == 0)

def cprime(i0, s, rk, K, sh):
    a = np.clip(i0 + sh, 0, N - 1); b = np.clip(i0 + sh + K, 0, N - 1)
    return s * (cl[b] - cl[a]) / rk

def fpass(i0, s, rk, K, lev, sh, drift=None):
    bas = cl[np.clip(i0 + sh, 0, N - 1)]
    idx = np.clip(i0[:, None] + sh + np.arange(1, K + 1)[None, :], 0, N - 1)
    path = s[:, None] * (cl[idx] - bas[:, None]) / rk[:, None]
    if drift is not None: path = path + drift[None, :]
    up = path >= lev; dn = path <= -lev
    fu = np.where(up.any(1), up.argmax(1), K + 5)
    fd = np.where(dn.any(1), dn.argmax(1), K + 5)
    r = np.zeros(len(i0), float); r[fu < fd] = 1; r[fd < fu] = -1
    return r

def cl_t(x, g):
    x = np.asarray(x, float); n = len(x)
    if n < 3: return float('nan'), float('nan'), float('nan')
    mu = x.mean(); r = x - mu
    _, inv = np.unique(g, return_inverse=True)
    gs = np.bincount(inv, weights=r)
    se = math.sqrt((gs ** 2).sum()) / n
    return mu, se, (mu / se if se > 0 else float('nan'))

# ---------- US DST state per bar (2nd Sun Mar 07:00 UTC -> 1st Sun Nov 06:00 UTC) ----------
dst = np.zeros(N, bool)
for y in range(2009, 2028):
    d = dt.date(y, 3, 1); first_sun = d + dt.timedelta(days=(6 - d.weekday()) % 7); second_sun = first_sun + dt.timedelta(days=7)
    n = dt.date(y, 11, 1); first_sun_nov = n + dt.timedelta(days=(6 - n.weekday()) % 7)
    t0 = int(dt.datetime(second_sun.year, second_sun.month, second_sun.day, 7, tzinfo=dt.timezone.utc).timestamp())
    t1 = int(dt.datetime(first_sun_nov.year, first_sun_nov.month, first_sun_nov.day, 6, tzinfo=dt.timezone.utc).timestamp())
    dst |= (ts >= t0) & (ts < t1)

WINS = [('在 2010-20', (year >= 2010) & (year <= 2020)),
        ('外 2021-26H1', year >= 2021),
        ('近年 2024-26H1', year >= 2024)]
OFFS = [sg * 7 * k for k in range(1, 27) for sg in (1, -1)]   # 52 candidates, same weekday
TOL_V = 0.02

def v_of(idx, s, rk):
    a = np.clip(idx, 1, N - 1)
    return s * (cl[a] - cl[a - 1]) / rk
def rng_of(idx, rk):
    a = np.clip(idx, 0, N - 1); return (hi[a] - lo[a]) / rk
def cloc_of(idx, s):
    a = np.clip(idx, 0, N - 1); r = hi[a] - lo[a]
    return np.where(r > 0, s * (cl[a] - (hi[a] + lo[a]) / 2) / np.where(r > 0, r, 1), 0.0)

def full_match(i0, s, rk, K, sh, mode):
    """returns best idx, second-best idx (same conditions), per event (-1 if none)"""
    vE = v_of(i0, s, rk); rE = rng_of(i0, rk); cE = cloc_of(i0, s); dE = dst[i0]
    best_d = np.full(len(i0), np.inf); bestI = np.full(len(i0), -1, np.int64)
    sec_d = np.full(len(i0), np.inf); secI = np.full(len(i0), -1, np.int64)
    for d in OFFS:
        cand = gidx(ts[i0] + d * 86400)
        okc = (cand >= 1) & fwd_ok(cand, K, sh) & (~flat[np.clip(cand, 0, N - 1)]) & (dst[np.clip(cand, 0, N - 1)] == dE)
        v = v_of(cand, s, rk); dv = np.abs(v - vE)
        cond = okc & (dv <= TOL_V)
        if mode == 'M2':
            rc = rng_of(cand, rk); cond &= (rE > 0) & (rc > 0) & (np.abs(np.log(np.where(rc > 0, rc, 1) / np.where(rE > 0, rE, 1))) <= math.log(1.25))
        if mode == 'M3':
            cond &= np.abs(cloc_of(cand, s) - cE) <= 0.15
        dd = np.where(cond, dv, np.inf)
        upd = dd < best_d
        upd2 = (~upd) & (dd < sec_d)
        # demote current best to second when a new best arrives; else maybe update second
        new_sec_d = np.where(upd, best_d, np.where(upd2, dd, sec_d))
        new_secI = np.where(upd, bestI, np.where(upd2, cand, secI))
        sec_d, secI = new_sec_d, new_secI
        best_d = np.where(upd, dd, best_d); bestI = np.where(upd, cand, bestI)
    return bestI, secI

def stats_block(iE, iR, s, rk, g, sh, lev=0.5):
    fE = fpass(iE, s, rk, 48, lev, sh); fR = fpass(iR, s, rk, 48, lev, sh)
    muF, seF, zF = cl_t(fE - fR, g)
    cE = cprime(iE, s, rk, 12, sh); cR = cprime(iR, s, rk, 12, sh)
    muS, seS, zS = cl_t((cE > 0).astype(float) - (cR > 0).astype(float), g)
    muL, seL, tL = cl_t(cE - cR, g)
    med = float(np.median(cE) - np.median(cR))
    return dict(F=(muF, seF, zF, fE.mean(), fR.mean()), S=(muS * 100, seS * 100, zS), Lv=(muL, seL, tL), med=med)

P(f'# [cycle61 研究レーン] RMT 完全マッチ版 — SL 後の反転は微細構造に還元されるか  {dt.datetime.now():%Y-%m-%d %H:%M}  seed {SEED}')
P(f'入力: refute_c4 json n {len(j)} (TP {int((exitk=="TP").sum())} SL {int((exitk=="SL").sum())} TIME {int((exitk=="TIME").sum())}) / XAU_m5_ohlc.npz {N} 本 flat {flat.mean()*100:.1f}% / DST 足比率 {dst.mean()*100:.1f}%')
P(f'事象母数（TP/SL・格子あり・ix>=1）{int(base.sum())} / 候補オフセット {len(OFFS)}（±7..±182 日・同曜日・同 DST）/ 許容 |Δv| ≤ {TOL_V}R')

RES = {}
# ============================================================ main grid
for mode in ['M1', 'M2', 'M3']:
    P(f'\n## {mode}: ' + {'M1': 'v のみ（主）', 'M2': 'v ∧ 決着足レンジ ×[0.8,1.25]', 'M3': 'v ∧ 終値位置 ±0.15'}[mode])
    for arm in ['SL', 'TP']:
        for wn, wm in WINS:
            for sh in [1, 0]:
                m = base & (exitk == arm) & wm & fwd_ok(ix, 48, sh) & (~flat[np.clip(ix, 0, N - 1)])
                i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]
                bI, sI = full_match(i0, s, rk, 48, sh, mode)
                ok = bI >= 1
                nE = len(i0); nM = int(ok.sum())
                vE = v_of(i0, s, rk); vR = np.where(ok, v_of(np.where(ok, bI, 1), s, rk), np.nan)
                cal_abs = float(np.nanmean(np.abs(vR - vE)[ok])); cal_mean = float(np.nanmean(vR[ok]) - np.mean(vE[ok]))
                cal_ok = (cal_abs <= TOL_V) and (abs(cal_mean) <= 0.01)
                st = stats_block(i0[ok], bI[ok], s[ok], rk[ok], g[ok], sh)
                # selection check: raw event F' on matched vs unmatched
                fAll = fpass(i0, s, rk, 48, 0.5, sh)
                fm = fAll[ok].mean(); fu = fAll[~ok].mean() if (~ok).sum() > 0 else float('nan')
                # descriptive shape calibration
                rE = rng_of(i0, rk); rR = np.where(ok, rng_of(np.where(ok, bI, 1), rk), np.nan)
                cE = cloc_of(i0, s); cR = np.where(ok, cloc_of(np.where(ok, bI, 1), s), np.nan)
                RES[(mode, arm, wn, sh)] = dict(nE=nE, nM=nM, cal_abs=cal_abs, cal_mean=cal_mean, cal_ok=cal_ok, st=st, fm=fm, fu=fu,
                                                vE=float(np.mean(vE[ok])), vR=float(np.nanmean(vR[ok])), rE=float(np.mean(rE[ok])), rR=float(np.nanmean(rR[ok])),
                                                cE=float(np.mean(cE[ok])), cR=float(np.nanmean(cR[ok])), bI=bI, sI=sI, mask=m, ok=ok)
                F = st['F']; S = st['S']; Lv = st['Lv']
                P(f"  - {arm} {wn} sh{sh}: n {nE} → マッチ {nM} ({nM/max(nE,1)*100:.1f}%) | 較正 v 事象 {np.mean(vE[ok]):+.3f} / RMT {np.nanmean(vR[ok]):+.3f} (mean|Δv| {cal_abs:.4f}・平均差 {cal_mean:+.4f}) {'OK' if cal_ok else 'FAIL'} | レンジ/risk 事象 {np.mean(rE[ok]):.3f} RMT {np.nanmean(rR[ok]):.3f} | 終値位置 事象 {np.mean(cE[ok]):+.3f} RMT {np.nanmean(cR[ok]):+.3f}")
                P(f"      F'(a0.5,48) 事象 {F[3]:+.4f} RMT {F[4]:+.4f} **D {F[0]:+.4f} (cl-se {F[1]:.4f} z {F[2]:+.2f} MDE {2*F[1]:.4f})** | 符号率 D {S[0]:+.2f} pp (z {S[2]:+.2f}) | 水準 D_12 {Lv[0]:+.4f}R (t {Lv[2]:+.2f}) | 中央値差 {st['med']:+.4f} | 選択検査: 事象の生 F' マッチ済 {fm:+.4f} vs 脱落 {fu:+.4f}")

# ============================================================ placebo: R1 as pseudo-event vs R2
P('\n## プラセボ（機械の検査）: マッチ対照 R1 を擬似事象とし、2 番目に近い候補 R2 を対照（M1・sh1）→ 0 のはず')
for arm in ['SL', 'TP']:
    for wn, wm in WINS:
        r = RES[('M1', arm, wn, 1)]
        m = r['mask']; ok = r['ok'] & (r['sI'] >= 1)
        i0 = ix[m][ok]; s = side[m][ok]; rk = risk[m][ok]; g = day_x[m][ok]
        R1 = r['bI'][ok]; R2 = r['sI'][ok]
        st = stats_block(R1, R2, s, rk, g, 1)
        F = st['F']; S = st['S']; Lv = st['Lv']
        v1 = v_of(R1, s, rk); v2 = v_of(R2, s, rk)
        P(f"  - {arm} {wn}: n {len(i0)} | v R1 {v1.mean():+.3f} R2 {v2.mean():+.3f} | F' D {F[0]:+.4f} (z {F[2]:+.2f}) | 符号率 D {S[0]:+.2f} pp (z {S[2]:+.2f}) | 水準 D_12 {Lv[0]:+.4f} (t {Lv[2]:+.2f})")

# ============================================================ positive control: inject drift into event path
P('\n## 陽性対照（注入）: SL 在 M1 sh1 の事象 path に δ=0.05 / 0.10 R/時 の線形ドリフトを注入 → ΔF\'')
r = RES[('M1', 'SL', '在 2010-20', 1)]
m = r['mask']; ok = r['ok']; i0 = ix[m][ok]; s = side[m][ok]; rk = risk[m][ok]; g = day_x[m][ok]; R1 = r['bI'][ok]
f0 = fpass(i0, s, rk, 48, 0.5, 1)
for delta in [0.05, 0.10]:
    drift = delta * (np.arange(1, 49) / 12.0)
    f1 = fpass(i0, s, rk, 48, 0.5, 1, drift=drift)
    P(f"  - δ={delta}R/h: ΔF' {f1.mean()-f0.mean():+.4f}  （反証 11-23 sh1 の +0.074 / +0.153 と同程度なら検出力は保たれている）")

# ============================================================ barrier variants (M1, sh1, SL)
P('\n## バリア幅の変種（M1・sh1・SL 腕・事象 − RMT）: a = 0.25 / 0.5 / 1.0 R')
for wn, wm in WINS:
    r = RES[('M1', 'SL', wn, 1)]
    m = r['mask']; ok = r['ok']; i0 = ix[m][ok]; s = side[m][ok]; rk = risk[m][ok]; g = day_x[m][ok]; R1 = r['bI'][ok]
    row = []
    for lev in [0.25, 0.5, 1.0]:
        fE = fpass(i0, s, rk, 48, lev, 1); fR = fpass(R1, s, rk, 48, lev, 1)
        mu, se, zz = cl_t(fE - fR, g)
        row.append(f'a{lev}: D {mu:+.4f} (z {zz:+.2f})')
    P(f'  - SL {wn}: ' + ' | '.join(row))

# ============================================================ comparison ladder: plain ±7 twin -> refute RMT(12) -> full match
P('\n## 較正の梯子（SL 腕・sh1・F\'(a0.5)）: 通常双子 ±7 → 反証 RMT（12 候補・許容なし）→ 完全マッチ M1 → M2 → M3')
TWP = gidx(np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] + 7 * 86400, -10 ** 12))
TWM = gidx(np.where(ix >= 0, ts[np.clip(ix, 0, N - 1)] - 7 * 86400, -10 ** 12))
OFF12 = [7, -7, 14, -14, 21, -21, 28, -28, 35, -35, 42, -42]
for wn, wm in WINS:
    m = base & (exitk == 'SL') & wm & fwd_ok(ix, 48, 1) & (~flat[np.clip(ix, 0, N - 1)])
    i0 = ix[m]; s = side[m]; rk = risk[m]; g = day_x[m]
    # plain twins (±7 2-avg)
    okp = (TWP[m] >= 1) & fwd_ok(TWP[m], 48, 1); okm = (TWM[m] >= 1) & fwd_ok(TWM[m], 48, 1)
    use = okp | okm
    fE = fpass(i0[use], s[use], rk[use], 48, 0.5, 1)
    nT = okp[use].astype(float) + okm[use].astype(float)
    fTp = np.where(okp[use], fpass(np.where(okp[use], TWP[m][use], 1), s[use], rk[use], 48, 0.5, 1), 0.0)
    fTm = np.where(okm[use], fpass(np.where(okm[use], TWM[m][use], 1), s[use], rk[use], 48, 0.5, 1), 0.0)
    muP, seP, zP = cl_t(fE - (fTp + fTm) / nT, g[use])
    vP = np.nanmean(np.where(okp[use], v_of(np.where(okp[use], TWP[m][use], 1), s[use], rk[use]), np.nan))
    # refute-style RMT (12 offsets, nearest, no tolerance)
    vE = v_of(i0, s, rk); bd = np.full(len(i0), np.inf); bI = np.full(len(i0), -1, np.int64)
    for d in OFF12:
        cand = gidx(ts[i0] + d * 86400)
        okc = (cand >= 1) & fwd_ok(cand, 48, 1) & (~flat[np.clip(cand, 0, N - 1)])
        dv = np.where(okc, np.abs(v_of(cand, s, rk) - vE), np.inf)
        upd = dv < bd; bd = np.where(upd, dv, bd); bI = np.where(upd, cand, bI)
    okr = bI >= 1
    fE2 = fpass(i0[okr], s[okr], rk[okr], 48, 0.5, 1); fR2 = fpass(bI[okr], s[okr], rk[okr], 48, 0.5, 1)
    muR, seR, zR = cl_t(fE2 - fR2, g[okr]); vR12 = v_of(bI[okr], s[okr], rk[okr]).mean()
    row = [f'通常双子 v {vP:+.3f} D {muP:+.4f} (z {zP:+.2f}, n {int(use.sum())})', f'RMT12 v {vR12:+.3f} D {muR:+.4f} (z {zR:+.2f}, n {int(okr.sum())})']
    for mode in ['M1', 'M2', 'M3']:
        r = RES[(mode, 'SL', wn, 1)]; F = r['st']['F']
        row.append(f'{mode} v {r["vR"]:+.3f} D {F[0]:+.4f} (z {F[2]:+.2f}, n {r["nM"]})')
    P(f'  - SL {wn} (事象 v {vE.mean():+.3f}): ' + ' | '.join(row))

# ============================================================ verdict
P('\n## 判定（事前規則・主セル = SL 在 2010-20・M1・sh1・F\'(a0.5,48)）')
r = RES[('M1', 'SL', '在 2010-20', 1)]; F = r['st']['F']
D, se, zz = F[0], F[1], F[2]
if not r['cal_ok']:
    verdict = '較正失敗 → 判定保留'
elif D < 0.03 and abs(zz) < 2.0:
    verdict = 'H_RED（微細構造へ還元）'
elif D >= 0.03 and zz >= 2.5:
    ro = RES[('M1', 'SL', '外 2021-26H1', 1)]; Fo = ro['st']['F']
    verdict = 'H_TRADE（取引固有の残差）' + ('・外で再現' if (Fo[0] > 0 and Fo[2] >= 1.5) else '・在のみ（外 不再現）')
else:
    verdict = 'inconclusive'
P(f"  主セル D {D:+.4f} (cl-se {se:.4f} z {zz:+.2f} MDE {2*se:.4f}) 較正 {'OK' if r['cal_ok'] else 'FAIL'} (mean|Δv| {r['cal_abs']:.4f}・平均差 {r['cal_mean']:+.4f}) n {r['nM']}/{r['nE']}")
P(f"  → **{verdict}**")
# descriptive family nominal count
cells = [(k, RES[k]['st']) for k in RES]
nom = []
for k, st in cells:
    for nm, zv in [('F', st['F'][2]), ('S', st['S'][2]), ('L', st['Lv'][2])]:
        if not math.isnan(zv) and abs(zv) >= 2.0: nom.append((k, nm, zv))
P(f"  記述家族 {len(cells)*3} セル中 名目 |z|≥2: {len(nom)} 件（Bonferroni 必要 |z| 3.45）: " + '; '.join(f'{k[0]} {k[1]} {k[2][:1]} sh{k[3]} {nm} {zv:+.2f}' for k, nm, zv in nom))

P(f'\n実行 {time.time()-T0:.1f}s  seed {SEED}  乱数未使用（決定論）・外部通信なし・MT5 なし・多年 scan なし')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('written', OUT)
