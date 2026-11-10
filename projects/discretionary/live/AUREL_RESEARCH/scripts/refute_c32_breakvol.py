# -*- coding: utf-8 -*-
"""
[REFUTE] 2026-11-10 反証レーン — 対象: cycle32 (18:55) の残存弱信号
  W1「建玉前 1 時間ボラを揃えた SET C で残る壁抜け固有の事後ボラ +0.014〜+0.019（log・3 窓同符号・t 3〜7）＝統計的には有る」
      ＋ 前向きセル「SET C 版 外 ΔL_post（pre 残差控除後）≥ +0.03 ∧ t≥2 なら構造として記述に昇格」
  W2 知識 (1)「壁抜け後のボラは同レンジ足より速く減衰する（Δλ 在 −0.057・t −10.6）」
  W3 知識 (3)「建玉直後 1 時間の方向ドリフトは同 side プラセボ比 −0.02〜−0.05R（t 1.2〜2.3）＝負の期待値は最初の 1 時間に出る／
      本は『同じ地合いで同じ方向に建てたランダム足』より最初の 1 時間が悪い」
  W4 事後 2 セル「mid 壁の抜けは 外/近年 で同レンジ足より静か（−2〜−4%）・outer は荒い（+3〜4%）」
  参考: H_V PASS（規則上・SET B 在 t 8.74／外 t 3.57）

反証の機構仮説（結果を見る前に書く）:
  M1 **near マスクの非対称**: プラセボ候補は「実本の建玉足 ±12 本に入らない」。これにより対照の post 窓 [1,12] には
      トリガー足（＝壁抜け＝大足）が構造的に 1 本も入らないが、本の post 窓には他の本の建玉足が入り得る。
      これは結果窓に対する片側の選択であり、ΔL_post を機械的に正へ偏らせる。本の post 窓に他本の建玉が入る割合を印字し、
      マスク無し（d≠0 のみ）で SET B／SET C を取り直す。
  M2 **一致の片落ち**: SET B はレンジ一致・pre 不一致、SET C は pre 一致・トリガー足レンジ不一致（本 1.37 vs 一般 1.16 USD）。
      5 分足のボラ・クラスタリングは直前 1 本の大きさにも乗るので、SET C の残差 +0.014〜0.019 は「大足の次の 1 時間」で
      説明できる可能性。SET D = pre ボラ ∧ レンジ の両方一致（[0.8,1.25]・<K なら [0.67,1.5]）で ΔL_post・ΔL_pre・Δλ を印字。
      加法性の代替として、SET A（マスク無し）のプラセボ群内回帰 log V_post ~ log V_pre + log range + log V_pre2(−36..−13)
      （群内偏差 OLS・窓別）で β を推定し、本の回帰調整残差 ΔL_post − β·Δx を印字。
  M3 **方向の不一致**: 方向ドリフトの対照は side を貼っただけで、アンカー足の方向はランダム。本の建玉足は side 方向の大足
      （印字で確認）。5 分 lag-1 負（−0.04）はどんな方向足の後にも出るので、SET E = SET D ∧ アンカー足の方向 (close−open の符号)
      = side で対差を取り直す。消えれば「壁抜け固有」ではなく「方向足の後の一般的な反転」。
  M4 **Δλ の正体**: 本は pre が荒い側から選ばれる（壁への接近）ので、レンジだけ揃えた対照より post/pre が小さいのは平均回帰。
      SET D（pre を揃える）で Δλ≈0 になれば知識 (1) は選択の産物。
  M5 **負の対照（プラセボのプラセボ）**: SET D のプラセボ k=0 を擬似本として同じ手続きで一致対照を引き、ΔL_post を印字。
      ≈0 でなければ手続き自体が偏っている。
  M6 **別分割**: (2010-15|2016-26H1)・(偶数年|奇数年) で SET D 調整残差を印字。

判定規則（結果を見る前に固定・変えない）:
  R0 再現: 研究レーンの SET B（ΔL_post 在 +0.0483 t 8.74／外 +0.0215 t 3.57・ΔL_pre 在 +0.1050）と SET C（ΔL_post 在 +0.0368／
      外 +0.0295・ΔL_pre 在 +0.0226・対差 在 −0.0229R）を |Δ| ≤ 0.003 かつ |Δt| ≤ 0.3 で再現。合わなければ以降は保留。
  W1 主統計 = SET D マスク無し の調整残差 res = ΔL_post − ΔL_pre（併記: 回帰調整残差）。
      broken   = 在 res < +0.007 ∨ 在 t < 2 ∨ 外 res < +0.007 ∨ 外 t < 1.5（主張 +0.014〜0.019 の半分未満）。
      survived = 在 res ≥ +0.010 ∧ t ≥ 2 ∧ 外 res ≥ +0.010 ∧ t ≥ 1.5 で、回帰調整残差でも同じ符号・在 t≥2。他 inconclusive。
      前向きセル: SET D マスク無し 外 res と se から「≥+0.03 ∧ t≥2」に要る平均を印字（設計検査）。
  W2 broken   = SET D 在 Δλ > −0.02 ∨ |t| < 2 ∨ 外 Δλ の符号が在と異なる ∨ 外 |t| < 1.5。
      survived = 在 Δλ ≤ −0.02 ∧ t ≤ −2 ∧ 外 Δλ < 0 ∧ t ≤ −1.5。他 inconclusive。
  W3 主統計 = SET E マスク無し の対差（本 − 同 side・同方向プラセボ・R）。
      broken   = 在 対差 > −0.012R ∨ 在 |t| < 1.5。
      survived = 在 対差 ≤ −0.015R ∧ t ≤ −2 ∧ 外 同符号 ∧ t ≤ −1.0。他 inconclusive。
  W4 broken   = SET D マスク無し で mid の ΔL_post の符号が 在と外で異なる ∨ どちらかで |t| < 2。他 描述。
  H_V 参考: SET B マスク無し と SET D マスク無し で規則（在 t≥2 ∧ 外 t≥1.5）を再判定。
  M5 負の対照: |ΔL_post| > 0.01 ∧ |t| ≥ 2 なら「手続きの偏り」を注記し、W1 の survived は出さない。
  費用倍: 取引規則ではないので該当なし（記述）。D2: 窓別・16 年一括は判定に使わない。bid のみ。
入力: data/macro/XAU_m5_ohlc.npz・data/refute_c4_scan_paths_2010_2026.json のみ。scan 無し・MT5 無し・外部通信無し。seed 20261110。
出力: data/refute_c32_breakvol.md・data/refute_c32_breakvol_run.log。
"""
import os, json, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c32_breakvol.md"); NY = "America/New_York"
rng = np.random.default_rng(20261110); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c32] 壁抜け後 1 時間のボラ・ドリフト署名 — near マスク／二重一致／方向一致で壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c32_breakvol.py)")

# ---------- grid (c32 と同一) ----------
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64); C = z["close"].astype(float); O = z["open"].astype(float); H = z["high"].astype(float); Lo = z["low"].astype(float)
NB = len(ts); r = np.zeros(NB); r[1:] = np.diff(C); flat = r == 0.0; RNG = H - Lo; DIR = np.sign(C - O)
dt_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
SLOT = (dt_ny.hour.to_numpy() * 12 + dt_ny.minute.to_numpy() // 5).astype(np.int32); WD = dt_ny.weekday.to_numpy().astype(np.int8)
sess = dt_ny + pd.Timedelta(hours=6); SESS = sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy()
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True)
pos = np.clip(np.searchsorted(ts, T["entry_time"].to_numpy()), 0, NB - 1); ok = ts[pos] == T["entry_time"].to_numpy()
T = T[ok].reset_index(drop=True); I0 = pos[ok]
SGN = np.where(T["side"].to_numpy() == "BUY", 1.0, -1.0); RISK = T["risk"].to_numpy(); YEAR = T["year"].to_numpy()
PRE = np.arange(-12, 0); POST = np.arange(1, 13); POST2 = np.arange(13, 37); PRE2 = np.arange(-36, -12)
okb = (I0 - 36 >= 0) & (I0 + 36 < NB); I2 = np.where(okb, I0, 100)
VAL = okb & (SESS[I2 - 12] == SESS[I2]) & (SESS[I2 + 36] == SESS[I2]) & (flat[I2[:, None] + POST[None, :]].sum(1) <= 3) & (WD[I2] <= 4)
near = np.zeros(NB, dtype=bool)
for d in range(-12, 13): near[np.clip(I0 + d, 0, NB - 1)] = True
isentry = np.zeros(NB, dtype=bool); isentry[I0] = True
IV = I0[VAL]; DAY = (T["entry_time"].to_numpy()[VAL] // 86400); YR = YEAR[VAL]; SG = SGN[VAL]; RK = RISK[VAL]
Tv = T[VAL].reset_index(drop=True)
say(f"- 本 {len(T)}・母数 {len(IV)}（c32 と同じ条件）・読込 {time.time()-T0:.1f}s")

# M1: 本の post 窓に他本の建玉足が入る割合
cnt_post = isentry[IV[:, None] + POST[None, :]].sum(1); cnt_pre = isentry[IV[:, None] + PRE[None, :]].sum(1)
WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
for w, (y0, y1) in WIN.items():
    m = (YR >= y0) & (YR <= y1)
    say(f"- M1 {w}: 本の post 窓 [1,12] に他本の建玉足 ≥1 本 {np.mean(cnt_post[m]>0)*100:.1f}%（平均 {cnt_post[m].mean():.2f} 本）・pre 窓 ≥1 本 {np.mean(cnt_pre[m]>0)*100:.1f}%；プラセボ（マスク有り）は構造的に 0%")
# 建玉足の方向 = side か
dir_ok = DIR[IV] == SG
say(f"- M3 建玉足の方向 (close−open) が side と一致 {dir_ok.mean()*100:.1f}%・同値 {np.mean(DIR[IV]==0)*100:.1f}%；建玉足レンジ 中央値 {np.median(RNG[IV]):.2f} USD・|close−open|/range 中央値 {np.median(np.abs(C[IV]-O[IV])/np.maximum(RNG[IV],1e-9)):.2f}")

# ---------- placebo picker ----------
K = 4; DSH = np.array([d for d in range(-28, 29) if d != 0])
def vwin(I, W): return np.sqrt((r[np.asarray(I)[:, None] + W[None, :]] ** 2).mean(1))
def pick(I, sg=None, m_range=False, m_pre=False, m_dir=False, use_near=True, pre_only=False):
    I = np.asarray(I); n = len(I)
    Dm = DSH[DSH < 0] if pre_only else DSH
    Cd = np.clip(I[:, None] + 288 * Dm[None, :], 37, NB - 37)
    okc = (SLOT[Cd] == SLOT[I][:, None]) & (WD[Cd] <= 4) & (~flat[Cd]) & (SESS[Cd - 12] == SESS[Cd]) & (SESS[Cd + 36] == SESS[Cd])
    okc &= flat[Cd[:, :, None] + POST[None, None, :]].sum(2) <= 3
    if use_near: okc &= ~near[Cd]
    if m_dir: okc &= DIR[Cd] == sg[:, None]
    tight = np.ones_like(okc); wide = np.ones_like(okc)
    if m_range:
        q = RNG[Cd] / np.maximum(RNG[I][:, None], 1e-9); tight &= (q >= 0.8) & (q <= 1.25); wide &= (q >= 0.67) & (q <= 1.5)
    if m_pre:
        Vt = vwin(I, PRE); Vc = np.sqrt((r[Cd[:, :, None] + PRE[None, None, :]] ** 2).mean(2))
        q = Vc / np.maximum(Vt[:, None], 1e-9); tight &= (q >= 0.8) & (q <= 1.25); wide &= (q >= 0.67) & (q <= 1.5)
    ok1 = okc & tight; ok2 = okc & wide
    okc = np.where((ok1.sum(1) >= K)[:, None], ok1, ok2)
    P = np.full((n, K), -1, dtype=np.int64)
    for q_ in range(n):
        c = Cd[q_][okc[q_]]
        if len(c) >= K: P[q_] = rng.choice(c, size=K, replace=False)
    return P, (P >= 0).all(1), np.median(okc.sum(1))

def stats(I):
    I = np.asarray(I); rp = r[I[:, None] + PRE[None, :]]; ro = r[I[:, None] + POST[None, :]]; r2 = r[I[:, None] + POST2[None, :]]; rq = r[I[:, None] + PRE2[None, :]]
    Vp = np.sqrt((rp ** 2).mean(1)); Vo = np.sqrt((ro ** 2).mean(1)); V2 = np.sqrt((r2 ** 2).mean(1)); Vq = np.sqrt((rq ** 2).mean(1))
    return dict(Vp=Vp, Vo=Vo, V2=V2, Vq=Vq, rng=RNG[I], sum_o=ro.sum(1), ro=ro)
def ct(d, day):
    d = np.asarray(d, float); n = len(d); m = d.mean(); s = pd.DataFrame({"d": d - m, "g": day}).groupby("g")["d"].sum().to_numpy()
    se = np.sqrt((s ** 2).sum()) / n; return m, se, (m / se if se > 0 else np.nan)
def lg(x): return np.log(np.maximum(x, 1e-6))

def run(name, P, okP, I=None, sg=None, rk=None, day=None, yr=None, side_lbl=None, beta=None, quiet=False):
    """returns dict[w] of stats; I etc default to trade arrays"""
    if I is None: I, sg, rk, day, yr = IV, SG, RK, DAY, YR
    I = I[okP]; Pk = P[okP]; sg = sg[okP]; rk = rk[okP]; day = day[okP]; yr = yr[okP]
    st = stats(I); pl = [stats(Pk[:, k]) for k in range(K)]
    lVo = np.mean([lg(p["Vo"]) for p in pl], 0); lVp = np.mean([lg(p["Vp"]) for p in pl], 0); lV2 = np.mean([lg(p["V2"]) for p in pl], 0)
    lVq = np.mean([lg(p["Vq"]) for p in pl], 0); lRg = np.mean([lg(p["rng"]) for p in pl], 0)
    drp = np.mean([p["sum_o"] for p in pl], 0)
    dpost = lg(st["Vo"]) - lVo; dpre = lg(st["Vp"]) - lVp; dpre2 = lg(st["Vq"]) - lVq; drg = lg(st["rng"]) - lRg; d2 = lg(st["V2"]) - lV2
    dlam = dpost - dpre; res = dpost - dpre
    out = {}
    if not quiet: say(f"\n## {name}（確保 {okP.sum()}/{len(okP)}）")
    for w, (y0, y1) in WIN.items():
        m = (yr >= y0) & (yr <= y1); d = day[m]
        a = ct(dpost[m], d); b = ct(dpre[m], d); c = ct(d2[m], d); f = ct(dlam[m], d); g = ct(drg[m], d); h = ct(dpre2[m], d)
        dt_ = ct(sg[m] * st["sum_o"][m] / rk[m], d); dp_ = ct(sg[m] * drp[m] / rk[m], d); dd = ct(sg[m] * (st["sum_o"][m] - drp[m]) / rk[m], d)
        row = dict(n=int(m.sum()), post=a, pre=b, post2=c, lam=f, rng=g, pre2=h, drift_t=dt_, drift_p=dp_, pair=dd)
        if beta is not None:
            bb = beta[w]; adj = dpost[m] - bb[0] * dpre[m] - bb[1] * drg[m] - bb[2] * dpre2[m]; row["adj"] = ct(adj, d)
        out[w] = row
        if not quiet:
            say(f"- **{w}** n {m.sum()}: ΔL_pre {b[0]:+.4f} (t {b[2]:+.2f})・Δlog range {g[0]:+.4f}・ΔL_pre2 {h[0]:+.4f} ｜ **ΔL_post {a[0]:+.4f} (se {a[1]:.4f}・t {a[2]:+.2f})**・post−pre 残差 **{res[m].mean():+.4f} (t {ct(res[m], d)[2]:+.2f})**"
                + (f"・回帰調整残差 **{row['adj'][0]:+.4f} (t {row['adj'][2]:+.2f})**" if beta is not None else "")
                + f"・ΔL_post2 {c[0]:+.4f} (t {c[2]:+.2f})・Δλ {f[0]:+.4f} (t {f[2]:+.2f})")
            say(f"  - 方向ドリフト 本 {dt_[0]:+.4f}R (t {dt_[2]:+.2f})／同 side プラセボ {dp_[0]:+.4f}R (t {dp_[2]:+.2f})・**対差 {dd[0]:+.4f}R (t {dd[2]:+.2f})**")
    out["_arrays"] = dict(dpost=dpost, dpre=dpre, drg=drg, dpre2=dpre2, yr=yr, day=day, pl=pl, st=st, I=I, Pk=Pk, sg=sg, rk=rk)
    return out

# ---------- R0 再現 ----------
say("\n# R0 再現（研究レーンと同じ手続き）")
PB, okB, _ = pick(IV, m_range=True); PC, okC, _ = pick(IV, m_pre=True)
rB = run("SET B（レンジ一致・マスク有り・研究レーン主）", PB, okB)
rC = run("SET C（pre ボラ一致・マスク有り・研究レーン補足 b）", PC, okC)
ref = {"B_post_in": (0.0483, 8.74), "B_post_out": (0.0215, 3.57), "B_pre_in": (0.1050, 20.81), "C_post_in": (0.0368, 7.37), "C_post_out": (0.0295, 5.20), "C_pre_in": (0.0226, 20.04), "C_pair_in": (-0.0229, -2.04)}
got = {"B_post_in": rB["在 2010-20"]["post"], "B_post_out": rB["外 2021-26H1"]["post"], "B_pre_in": rB["在 2010-20"]["pre"], "C_post_in": rC["在 2010-20"]["post"], "C_post_out": rC["外 2021-26H1"]["post"], "C_pre_in": rC["在 2010-20"]["pre"], "C_pair_in": rC["在 2010-20"]["pair"]}
R0 = True
for k_, (v, t) in ref.items():
    g = got[k_]; okk = abs(g[0] - v) <= 0.003 and abs(g[2] - t) <= 0.3; R0 &= okk
    say(f"- {k_}: 研究レーン {v:+.4f} (t {t:+.2f}) / 本スクリプト {g[0]:+.4f} (t {g[2]:+.2f}) → {'OK' if okk else 'NG'}")
say(f"- **R0 {'OK' if R0 else 'NG（乱数列の違いによる差は許容幅で吸収されるはず・NG なら以降は保留）'}**")

# ---------- 回帰 β（SET A マスク無し・群内偏差 OLS） ----------
say("\n# M2b 群内回帰 β（SET A マスク無し・プラセボ 4 本の群内偏差・log V_post ~ log V_pre + log range + log V_pre2）")
PA0, okA0, _ = pick(IV, use_near=False)
BETA = {}
pl = [stats(PA0[okA0][:, k]) for k in range(K)]
Y = np.stack([lg(p["Vo"]) for p in pl], 1); X1 = np.stack([lg(p["Vp"]) for p in pl], 1); X2 = np.stack([lg(p["rng"]) for p in pl], 1); X3 = np.stack([lg(p["Vq"]) for p in pl], 1)
yrA = YR[okA0]
for w, (y0, y1) in WIN.items():
    m = (yrA >= y0) & (yrA <= y1)
    def dm(A): return (A[m] - A[m].mean(1, keepdims=True)).ravel()
    Xd = np.stack([dm(X1), dm(X2), dm(X3)], 1); yd = dm(Y)
    b, *_ = np.linalg.lstsq(Xd, yd, rcond=None); BETA[w] = b
    pred = Xd @ b; r2 = 1 - ((yd - pred) ** 2).sum() / (yd ** 2).sum()
    say(f"- {w}: β_pre {b[0]:+.3f}・β_range {b[1]:+.3f}・β_pre2 {b[2]:+.3f}・群内 R² {r2:.3f}（n 群 {m.sum()}）")

# ---------- M1: マスク無し ----------
say("\n# M1 near マスクを外す（プラセボ候補 = d≠0 のみ・他本の近傍も可）")
PB0, okB0, _ = pick(IV, m_range=True, use_near=False); rB0 = run("SET B マスク無し（レンジ一致）", PB0, okB0, beta=BETA)
PC0, okC0, _ = pick(IV, m_pre=True, use_near=False); rC0 = run("SET C マスク無し（pre ボラ一致）", PC0, okC0, beta=BETA)
# 対称条件: 本の post 窓にも他本が無い ∧ マスク有り
sym = cnt_post == 0
rCsym = run("SET C マスク有り ∧ 本も post 窓に他本無し（対称条件・参考）", PC, okC & sym)

# ---------- M2: SET D（pre ∧ range） ----------
say("\n# M2 SET D = pre ボラ ∧ トリガー足レンジ の両方一致")
PD, okD, mdD = pick(IV, m_range=True, m_pre=True); rD = run(f"SET D マスク有り（候補中央値 {mdD:.0f}）", PD, okD, beta=BETA)
PD0, okD0, mdD0 = pick(IV, m_range=True, m_pre=True, use_near=False); rD0 = run(f"SET D マスク無し（候補中央値 {mdD0:.0f}）【W1・W2・W4 主】", PD0, okD0, beta=BETA)
PDp, okDp, _ = pick(IV, m_range=True, m_pre=True, use_near=False, pre_only=True); rDp = run("SET D マスク無し・過去側 d<0 のみ（汚染検査）", PDp, okDp, beta=BETA)

# ---------- M3: SET E（∧ 方向一致） ----------
say("\n# M3 SET E = SET D ∧ アンカー足の方向 = side（方向ドリフトの対照）")
PE0, okE0, mdE0 = pick(IV, sg=SG, m_range=True, m_pre=True, m_dir=True, use_near=False); rE0 = run(f"SET E マスク無し（候補中央値 {mdE0:.0f}）【W3 主】", PE0, okE0, beta=BETA)
PE1, okE1, _ = pick(IV, sg=SG, m_range=True, m_pre=True, m_dir=True, use_near=True); rE1 = run("SET E マスク有り", PE1, okE1)
# 方向だけ一致（レンジ・pre は不一致）: 反転の一般性
PF0, okF0, _ = pick(IV, sg=SG, m_dir=True, use_near=False); rF0 = run("SET F マスク無し・方向のみ一致（記述）", PF0, okF0)
# 累積プロファイル（SET E マスク無し）
A = rE0["_arrays"]
for w, (y0, y1) in WIN.items():
    m = (A["yr"] >= y0) & (A["yr"] <= y1)
    cum_t = np.cumsum((A["sg"][m][:, None] * A["st"]["ro"][m] / A["rk"][m][:, None]).mean(0))
    cum_p = np.cumsum(np.mean([(A["sg"][m][:, None] * p["ro"][m] / A["rk"][m][:, None]).mean(0) for p in A["pl"]], 0))
    say(f"- SET E {w} 累積 対差（本−同方向プラセボ・R）j=1..12: " + " ".join(f"{x:+.3f}" for x in (cum_t - cum_p)) + f"；プラセボ側の累積 j=12 {cum_p[-1]:+.3f}R（方向足の後の一般的反転）")

# ---------- M4: W4 mid/outer（SET D マスク無し） ----------
say("\n# M4 W4 事後 2 セル（SET D マスク無し）")
A = rD0["_arrays"]; wk = Tv["wall_kind"].to_numpy()[okD0]
W4rows = {}
for kind in sorted(np.unique(wk)):
    parts = []
    for w, (y0, y1) in WIN.items():
        m = (A["yr"] >= y0) & (A["yr"] <= y1) & (wk == kind)
        a = ct(A["dpost"][m], A["day"][m]); parts.append(f"{w} n{m.sum()} ΔL_post {a[0]:+.4f} (t {a[2]:+.2f})"); W4rows[(kind, w)] = a
    say(f"- wall {kind}: " + "；".join(parts))

# ---------- M5: 負の対照 ----------
say("\n# M5 負の対照（SET D マスク無し のプラセボ k=0 を擬似本として同じ手続き）")
pseudo = PD0[okD0][:, 0]; psg = SG[okD0]; prk = RK[okD0]; pday = (ts[pseudo] // 86400); pyr = YR[okD0]
PP, okPP, _ = pick(pseudo, sg=psg, m_range=True, m_pre=True, use_near=False)
rP = run("擬似本（SET D プラセボ k=0）vs その SET D 対照", PP, okPP, I=pseudo, sg=psg, rk=prk, day=pday, yr=pyr, beta=BETA)
neg_bias = any(abs(rP[w]["post"][0]) > 0.01 and abs(rP[w]["post"][2]) >= 2 for w in ["在 2010-20", "外 2021-26H1"])

# ---------- M6: 別分割（SET D マスク無し・残差） ----------
say("\n# M6 別分割（SET D マスク無し・post−pre 残差・回帰調整残差）")
A = rD0["_arrays"]; res_all = A["dpost"] - A["dpre"]
def splitrow(label, m):
    a = ct(res_all[m], A["day"][m]); bb = BETA["在 2010-20"]; adj = A["dpost"][m] - bb[0] * A["dpre"][m] - bb[1] * A["drg"][m] - bb[2] * A["dpre2"][m]; c = ct(adj, A["day"][m])
    say(f"- {label}: n {m.sum()} 残差 {a[0]:+.4f} (t {a[2]:+.2f})・回帰調整 {c[0]:+.4f} (t {c[2]:+.2f})・ΔL_post 生 {ct(A['dpost'][m], A['day'][m])[0]:+.4f}")
splitrow("2010-15", (A["yr"] <= 2015)); splitrow("2016-26H1", (A["yr"] >= 2016)); splitrow("偶数年", (A["yr"] % 2 == 0)); splitrow("奇数年", (A["yr"] % 2 == 1))
rows = []
for y in range(2010, 2027):
    m = A["yr"] == y
    if m.sum() < 30: continue
    rows.append(f"{y}: {ct(res_all[m], A['day'][m])[0]:+.3f}")
say("- 年別 残差: " + " | ".join(rows))

# ---------- 判定 ----------
say("\n# 判定（事前固定規則）")
Din, Dout = rD0["在 2010-20"], rD0["外 2021-26H1"]
res_in = Din["post"][0] - Din["pre"][0]; res_out = Dout["post"][0] - Dout["pre"][0]
A = rD0["_arrays"]; m_in = (A["yr"] <= 2020); m_out = (A["yr"] >= 2021)
t_in = ct((A["dpost"] - A["dpre"])[m_in], A["day"][m_in]); t_out = ct((A["dpost"] - A["dpre"])[m_out], A["day"][m_out])
adj_in = Din["adj"]; adj_out = Dout["adj"]
if res_in < 0.007 or t_in[2] < 2 or res_out < 0.007 or t_out[2] < 1.5: W1 = "broken"
elif res_in >= 0.010 and t_in[2] >= 2 and res_out >= 0.010 and t_out[2] >= 1.5 and adj_in[0] > 0 and adj_in[2] >= 2 and adj_out[0] > 0 and not neg_bias: W1 = "survived"
else: W1 = "inconclusive"
need = max(0.03, 2 * t_out[1]); say(f"- W1 SET D マスク無し 残差 在 {res_in:+.4f} (t {t_in[2]:+.2f})／外 {res_out:+.4f} (t {t_out[2]:+.2f})・回帰調整 在 {adj_in[0]:+.4f} (t {adj_in[2]:+.2f})／外 {adj_out[0]:+.4f} (t {adj_out[2]:+.2f}) → **{W1}**；前向きセル「外 ≥+0.03 ∧ t≥2」に要る平均 {need:+.4f}（現状 外 se {t_out[1]:.4f}）")
lam_in, lam_out = Din["lam"], Dout["lam"]
if lam_in[0] > -0.02 or abs(lam_in[2]) < 2 or np.sign(lam_out[0]) != np.sign(lam_in[0]) or abs(lam_out[2]) < 1.5: W2 = "broken"
elif lam_in[0] <= -0.02 and lam_in[2] <= -2 and lam_out[0] < 0 and lam_out[2] <= -1.5: W2 = "survived"
else: W2 = "inconclusive"
say(f"- W2 SET D Δλ 在 {lam_in[0]:+.4f} (t {lam_in[2]:+.2f})／外 {lam_out[0]:+.4f} (t {lam_out[2]:+.2f})（研究レーン SET B 在 −0.0567 t −10.63）→ **{W2}**")
Ein, Eout = rE0["在 2010-20"]["pair"], rE0["外 2021-26H1"]["pair"]
if Ein[0] > -0.012 or abs(Ein[2]) < 1.5: W3 = "broken"
elif Ein[0] <= -0.015 and Ein[2] <= -2 and Eout[0] < 0 and Eout[2] <= -1.0: W3 = "survived"
else: W3 = "inconclusive"
say(f"- W3 SET E マスク無し 対差 在 {Ein[0]:+.4f}R (t {Ein[2]:+.2f})／外 {Eout[0]:+.4f}R (t {Eout[2]:+.2f})（研究レーン SET C 在 −0.0229 t −2.04）→ **{W3}**")
mi, mo = W4rows.get(("mid", "在 2010-20")), W4rows.get(("mid", "外 2021-26H1"))
W4 = "broken" if (mi is None or mo is None or np.sign(mi[0]) != np.sign(mo[0]) or abs(mi[2]) < 2 or abs(mo[2]) < 2) else "描述（符号一致・|t|≥2）"
say(f"- W4 mid ΔL_post 在 {mi[0]:+.4f} (t {mi[2]:+.2f})／外 {mo[0]:+.4f} (t {mo[2]:+.2f}) → **{W4}**")
for nm, rr in [("SET B マスク無し", rB0), ("SET D マスク無し", rD0)]:
    a, b = rr["在 2010-20"]["post"], rr["外 2021-26H1"]["post"]
    say(f"- H_V 規則再判定 {nm}: 在 {a[0]:+.4f} (t {a[2]:+.2f})／外 {b[0]:+.4f} (t {b[2]:+.2f}) → {'PASS' if (a[0]>0 and a[2]>=2 and b[0]>0 and b[2]>=1.5) else 'null'}")
say(f"- M5 負の対照: {'手続きの偏りあり' if neg_bias else '偏りなし（|ΔL_post| ≤0.01 または |t|<2）'}")
say(f"- R0 {'OK' if R0 else 'NG'}")
say(f"\n- 実行 {time.time()-T0:.1f} s・scan 無し・MT5 無し・外部通信無し・seed 20261110")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
