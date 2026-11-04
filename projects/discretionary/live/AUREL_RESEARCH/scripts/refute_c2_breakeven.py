# -*- coding: utf-8 -*-
"""
AUREL 反証レーン — cycle2「建値トレール（MFE が +X に到達後、終値R≤0 で 0R 決済）」を壊す。
読取りのみ・発注なし・書き込みは AUREL_RESEARCH/data のみ。setup_engine は import せず、_simulate の規則だけを再実装（L148-154 読むだけ）。

対象の主張（data/c2_breakeven_trail_result.md 21:31）: X=1.0 在 diff +0.011 t4.5 / 外 +0.025 t6.0 / 2024-26 +0.037 t5.6、大当たり残存 ~90%。

機械仮説 H0（コードを書く前に固定）:
  (a) 約定価格の水増し: 研究ルールは「終値R≤0 を見てから 0R で約定」。終値が cl≤0 の時点で 0R は現実の価格より良い。
      決済 1 本あたり (0 − cl) ≥ 0 の“贈り物”。成行なら cl、建値の逆指値なら 0 に触れた時点で約定（終値を待たない）。
  (b) 記帳の非対称: 原型の SL/TP は FEED_TOL(0.1USD) 分不利に記帳される（20:25 [REFUTE] 既証）。建値決済にこの shortfall を課していない。
  (c) 48 本切断: path は PATH_MAX=48 まで。hold>48 の 4601 本（23.7%）は 48 本以降の建値戻りを見ていない。
  (d) 建値の逆指値を実際に置くと、終値を待たずに安値が 0+FEED_TOL に触れた時点で発動 → 研究ルールより多くの runner を殺す。
  価格がマルチンゲールなら、公正に記帳したどんな出口規則も E[diff]=0。

事前固定の検定（全部 paired diff = R_new − R_orig、t は paired）:
  P0 再現: キャッシュ・研究ルールそのまま X=1.0 在/外（+0.011/+0.025 に一致するか）。
  P1 約定価格: 同じトリガ集合で 0R でなく終値 cl_k で約定。贈り物 (0−cl_k) の平均も出す。
  P2 記帳公正化: P1 の約定にさらに滑り s∈{0, 0.10, 0.22}USD を課す（s=0.10 = 原型 SL/TP の shortfall と同額）。
  P3 本物の建値逆指値（M5 から全 path を再構築・切断なし）: 高値が entry+X·risk に触れた足 k で武装。
      A: k+1 以降で 安値 ≤ entry+FEED_TOL なら entry で約定（_simulate の SL 規則と同じ記帳）。
      B: 同足 SL 優先の規則どおり k 本目から（保守側）。
      いずれも 原型 SL/TP/BE が同じ shortfall を持つので比較は公正。s∈{0,0.10,0.22} も併記。
      併せて「研究ルールを 48 本以降まで延長」で (c) の寄与を単離。
  P4 窓: 在 2010-20 / 外 2021-26 / 2021-23 / 2024-26 / 2025-26H1 / 本番窓 JST7-12×outer / JST7-12×mid / BUY / SELL。
  P5 X 格子 {0.5,0.75,1.0,1.25,1.5} × 在/外 に Bonferroni α=0.05/10（P3A s=0 で採点）。
  P6 プラセボ: 武装足を「同じ本・同じ保有内の一様ランダム足」に置換（200 回）し P3A を再計算。情報ゼロの武装でも同じ diff が出るか。
  P7 尻尾: 原型上位10% 合計R の残存率（P3A）。
  P8 look-ahead: 武装は足 k の高値、発動は k+1 以降の安値（A）。bar0 の約定前レンジは逆指値エントリでは entry の逆側なので武装できない（確認値を出す）。
判定（事前固定）:
  broken     = P3A（s=0）の diff が 在・外 の両方で Bonferroni(0.005) 有意な正にならない、または P1+P2(s=0.10) で研究 diff が ≤0 に落ちる。
  survived   = P3A s=0 が 在・外・2024-26 で Bonferroni 有意な正、P3A s=0.10 でも 外 t≥2、尻尾残存 ≥90%、P6 プラセボ超過 p<0.005。
  それ以外   = inconclusive。
入力: data/c1_reaccel_paths_2010_2026.json ＋ data/refute_c4_scan_paths_2010_2026.json（b を結合）＋ 金M5（m5_loader・読むだけ）
出力: data/refute_c2_breakeven.md、data/refute_c2_fullpaths.npz（再構築 path のキャッシュ・再利用可）
"""
import os, sys, json, math, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(HERE)
DATA = os.path.join(RES, "data")
C1 = os.path.join(DATA, "c1_reaccel_paths_2010_2026.json")
C4 = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
NPZ = os.path.join(DATA, "refute_c2_fullpaths.npz")
OUT = os.path.join(DATA, "refute_c2_breakeven.md")
W2W = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
if W2W not in sys.path: sys.path.insert(0, W2W)
X0 = 1.0
XS = (0.5, 0.75, 1.0, 1.25, 1.5)
ALPHA = 0.05 / 10
L = []
def say(s=""):
    print(s, flush=True); L.append(s)


def tstat(d):
    d = np.asarray(d, float); n = len(d)
    if n < 2: return float("nan"), float("nan")
    se = d.std(ddof=1) / math.sqrt(n)
    t = d.mean() / se if se > 0 else float("nan")
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))) if not np.isnan(t) else float("nan")
    return t, p


def top_ret(R0, R1):
    top = np.argsort(R0)[-max(1, len(R0) // 10):]
    return 100 * R1[top].sum() / R0[top].sum() if R0[top].sum() != 0 else 100.0


# ---------------- load ----------------
def load():
    J = json.load(open(C1, encoding="utf-8")); c4 = json.load(open(C4, encoding="utf-8"))
    aux = {t["entry_time"]: t for t in c4["trades"]}
    rows = []
    for t in J["trades"]:
        a = aux.get(t["entry_time"])
        rows.append({**{k: t[k] for k in ("entry_time", "year", "jh", "wall_kind", "side", "risk", "R", "exit_reason", "hold")},
                     "mfe": t["mfe"], "cl": t["cl"], "b": a["b"] if a else np.nan})
    df = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)
    FT = J["frozen"]["FEED_TOL"]
    df["ft"] = FT / df.risk
    return df, J, FT


# ---------------- research rule on cache ----------------
def research_rule(mfe, cl, X, fill_close=False, kmax=None):
    """返り値 (triggered, k_trigger, fill_R)。研究ルール: mfe[k]>=X で武装 → k+1 以降の cl<=0 で決済。"""
    n = len(mfe) if kmax is None else min(len(mfe), kmax + 1)
    armed = None
    for k in range(n):
        if mfe[k] >= X: armed = k; break
    if armed is None: return False, -1, None
    for k in range(armed + 1, n):
        if cl[k] <= 0.0:
            return True, k, (cl[k] if fill_close else 0.0)
    return False, armed, None


# ---------------- full path rebuild ----------------
def rebuild(df, FT):
    if os.path.exists(NPZ):
        z = np.load(NPZ)
        say("再構築 path キャッシュ読込: %s (%d 本)" % (NPZ, len(z["off"]) - 1))
        return z["hiR"], z["loR"], z["clR"], z["off"], z["chk"]
    from m5_loader import load_m5
    t0 = time.time(); frames = []
    for y in range(2010, 2027):
        a, b = "%d-01-01" % y, "%d-01-01" % (y + 1)
        if a >= "2026-07-01": break
        if b > "2026-07-01": b = "2026-07-01"
        try: frames.append(load_m5(a, b))
        except FileNotFoundError as e: say("skip %d %s" % (y, e))
    m5 = pd.concat(frames); m5 = m5[~m5.index.duplicated(keep="first")].sort_index()
    say("金M5 %d bars %s..%s (%.0fs)" % (len(m5), m5.index[0], m5.index[-1], time.time() - t0))
    h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    pos = {int(pd.Timestamp(t).timestamp()): i for i, t in enumerate(m5.index)}
    hiR, loR, clR, off, chk = [], [], [], [0], []
    for r in df.itertuples():
        ie = pos[int(r.entry_time)]; sgn = 1.0 if r.side == "BUY" else -1.0
        entry = c[ie] - sgn * r.cl[0] * r.risk           # cl[0] = sgn*(c[ie]-entry)/risk を逆算（丸め誤差 ≤0.0005R）
        ek = ie + int(r.hold)
        seg_h = h[ie:ek + 1]; seg_l = l[ie:ek + 1]; seg_c = c[ie:ek + 1]
        fav = sgn * (np.where(sgn > 0, seg_h, seg_l) - entry) / r.risk      # 有利方向の極値 (R)
        adv = sgn * (np.where(sgn > 0, seg_l, seg_h) - entry) / r.risk      # 不利方向の極値 (R, 符号付き・負=含み損)
        hiR.append(fav); loR.append(adv); clR.append(sgn * (seg_c - entry) / r.risk); off.append(off[-1] + len(fav))
        # 整合チェック: 再構築 cl と cache cl の最大差（48本まで）
        m = min(len(r.cl), len(fav)); chk.append(float(np.max(np.abs(np.asarray(r.cl[:m]) - clR[-1][:m]))))
    hiR = np.concatenate(hiR); loR = np.concatenate(loR); clR = np.concatenate(clR); off = np.asarray(off); chk = np.asarray(chk)
    np.savez_compressed(NPZ, hiR=hiR, loR=loR, clR=clR, off=off, chk=chk)
    say("再構築 %d 本・%d 足 → %s" % (len(off) - 1, len(hiR), NPZ))
    return hiR, loR, clR, off, chk


def be_stop(fav, adv, cl, ft, X, same_bar=False):
    """本物の建値逆指値。武装=fav[k]>=X。発動=adv[j]<=ft（安値が entry+FEED_TOL に触れる・_simulate SL 規則）→ 0R 約定。
    返り値 (triggered, k_arm, k_fire)。same_bar=True なら武装足も発動対象（同足 SL 優先・保守側）。"""
    armed = np.nonzero(fav >= X)[0]
    if len(armed) == 0: return False, -1, -1
    k = int(armed[0]); start = k if same_bar else k + 1
    if start >= len(adv): return False, k, -1
    hit = np.nonzero(adv[start:] <= ft)[0]
    if len(hit) == 0: return False, k, -1
    return True, k, start + int(hit[0])


def verify_original(df, hiR, loR, off, FT):
    """再構築 path で原型 SL/TP の決着足を再現できるか（b を使う）。exit 足 = hold、理由一致を数える。"""
    ok = bad = 0; bad_ex = []
    for i, r in enumerate(df.itertuples()):
        if np.isnan(r.b): continue
        fav = hiR[off[i]:off[i + 1]]; adv = loR[off[i]:off[i + 1]]; ft = FT / r.risk
        reason = None; k_exit = None
        for k in range(len(fav)):
            if adv[k] <= -1.0 + ft: reason, k_exit = "SL", k; break
            if fav[k] >= r.b + ft: reason, k_exit = "TP", k; break
        if reason is None: reason, k_exit = "TIME", len(fav) - 1
        if reason == r.exit_reason and k_exit == r.hold: ok += 1
        else:
            bad += 1
            if len(bad_ex) < 5: bad_ex.append((r.entry_time, r.exit_reason, r.hold, reason, k_exit))
    return ok, bad, bad_ex


def windows(df):
    jm = (df.jh >= 7) & (df.jh <= 12)
    return (("在 2010-20", df.year <= 2020), ("外 2021-26", df.year >= 2021), ("2021-23", (df.year >= 2021) & (df.year <= 2023)),
            ("2024-26", df.year >= 2024), ("2025-26H1", df.year >= 2025),
            ("本番窓 JST7-12×outer", jm & (df.wall_kind == "outer")), ("本番窓 JST7-12×mid", jm & (df.wall_kind == "mid")),
            ("BUY", df.side == "BUY"), ("SELL", df.side == "SELL"))


def main():
    df, J, FT = load()
    n = len(df); R0 = df.R.to_numpy(); risk = df.risk.to_numpy(); ft = df.ft.to_numpy()
    say("# AUREL [REFUTE] cycle2 建値トレール（+X 到達後 終値R≤0 → 0R）  入力 %d 本 (c1 生成 %s)  %s" % (n, J["generated"], time.strftime("%Y-%m-%d %H:%M")))
    say("FEED_TOL=%.2f USD、ft=0.1/risk 平均 %.4fR。hold>48（path 切断）%d 本 (%.1f%%)。TIME %d 本。" % (
        FT, ft.mean(), (df.hold > 48).sum(), 100 * (df.hold > 48).mean(), (df.exit_reason == "TIME").sum()))
    say()
    masks = windows(df)

    # ---------- P0 / P1 / P2 ----------
    say("## P0〜P2. 研究ルール（キャッシュ・48 本まで）: 再現 → 約定を終値に → 滑り s を課す。X=%.2f" % X0)
    trig = np.zeros(n, bool); ktr = np.full(n, -1); fill0 = R0.copy(); fillc = R0.copy()
    for i, r in enumerate(df.itertuples()):
        tg, k, f = research_rule(r.mfe, r.cl, X0)
        if tg:
            trig[i] = True; ktr[i] = k; fill0[i] = 0.0; fillc[i] = r.cl[k]
    gift = (0.0 - fillc[trig])
    say("トリガ %d 本 (%.1f%%)。トリガ時の終値 cl_k: 平均 %+.3fR・中央値 %+.3fR・10%%点 %+.3fR → 「0R で約定」の贈り物 平均 %+.4fR/トリガ本。" % (
        trig.sum(), 100 * trig.mean(), fillc[trig].mean(), np.median(fillc[trig]), np.percentile(fillc[trig], 10), gift.mean()))
    say("トリガ本の原型決着: SL %d / TP %d / TIME %d（原型 平均R %+.3f）。" % (
        (df.exit_reason[trig] == "SL").sum(), (df.exit_reason[trig] == "TP").sum(), (df.exit_reason[trig] == "TIME").sum(), R0[trig].mean()))
    say()
    say("| 窓 | n | トリガ | P0 研究 diff / t | P1 終値約定 diff / t | P2 s=0.10 diff / t | P2 s=0.22 diff / t | 贈り物+ft の全本換算 |")
    say("|---|---|---|---|---|---|---|---|")
    P012 = {}
    for lab, m in masks:
        m = m.to_numpy(); d0 = fill0[m] - R0[m]; dc = fillc[m] - R0[m]
        d10 = np.where(trig[m], fillc[m] - 0.10 / risk[m], R0[m]) - R0[m]; d22 = np.where(trig[m], fillc[m] - 0.22 / risk[m], R0[m]) - R0[m]
        mech = ((0.0 - fillc[m & trig]) + ft[m & trig]).sum() / m.sum()
        P012[lab] = (d0.mean(), tstat(d0)[0], dc.mean(), tstat(dc)[0], d10.mean(), tstat(d10)[0])
        say("| %s | %d | %d | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f |" % (
            lab, m.sum(), (m & trig).sum(), d0.mean(), tstat(d0)[0], dc.mean(), tstat(dc)[0], d10.mean(), tstat(d10)[0], d22.mean(), tstat(d22)[0], mech))
    say()

    # ---------- rebuild ----------
    say("## P3 準備. M5 から全 path を再構築（切断なし）・整合チェック")
    hiR, loR, clR, off, chk = rebuild(df, FT)
    say("再構築 cl vs cache cl の最大差: 全本最大 %.4fR・99%%点 %.4fR（丸め 0.0005R 以内なら整合）。" % (chk.max(), np.percentile(chk, 99)))
    ok, bad, bad_ex = verify_original(df, hiR, loR, off, FT)
    say("原型 SL/TP/TIME の決着足・理由を再構築 path で再現: 一致 %d / 不一致 %d。%s" % (ok, bad, ("例: %s" % bad_ex) if bad else ""))
    # bar0 pre-fill: 建玉足で武装できた本の数と、建玉足の fav が X 以上の本（約定前レンジ混入の上限）
    fav0 = hiR[off[:-1]]
    say("bar0 の有利極値 ≥ X=1.0 の本（建玉足だけで武装）: %d 本 (%.1f%%) ← 逆指値エントリでは約定後の値動きのみ（約定前は entry の逆側）。" % ((fav0 >= X0).sum(), 100 * (fav0 >= X0).mean()))
    say()

    # ---------- P3 ----------
    def run_be(X, same_bar=False, s=0.0, ext_close=False):
        R1 = R0.copy(); tg = np.zeros(n, bool); kf = np.full(n, -1); ka = np.full(n, -1)
        for i in range(n):
            fav = hiR[off[i]:off[i + 1]]; adv = loR[off[i]:off[i + 1]]; cl = clR[off[i]:off[i + 1]]
            if ext_close:
                armed = np.nonzero(fav >= X)[0]
                if len(armed) == 0: continue
                k = int(armed[0]); hit = np.nonzero(cl[k + 1:] <= 0.0)[0]
                if len(hit) == 0: continue
                tg[i] = True; ka[i] = k; kf[i] = k + 1 + int(hit[0]); R1[i] = 0.0 - s / risk[i]
            else:
                t_, k, j = be_stop(fav, adv, cl, ft[i], X, same_bar)
                ka[i] = k
                if t_: tg[i] = True; kf[i] = j; R1[i] = 0.0 - s / risk[i]
        return R1, tg, ka, kf

    say("## P3. 本物の建値逆指値（全 path・_simulate と同じ記帳: 安値 ≤ entry+FEED_TOL で entry 約定）X=%.2f" % X0)
    R_A, tgA, kaA, kfA = run_be(X0, False, 0.0)
    R_B, tgB, _, _ = run_be(X0, True, 0.0)
    R_A10, _, _, _ = run_be(X0, False, 0.10)
    R_A22, _, _, _ = run_be(X0, False, 0.22)
    R_ext, tgE, _, _ = run_be(X0, False, 0.0, ext_close=True)
    say("発動本数: A（翌足以降） %d / B（同足含む） %d ／ 研究ルール 48 本延長（終値≤0・0R 約定） %d ／ 研究ルール 48 本まで %d。" % (tgA.sum(), tgB.sum(), tgE.sum(), trig.sum()))
    say("A の発動本の原型決着: SL %d / TP %d / TIME %d（原型 平均R %+.3f）。発動本のうち原型 TP だった本＝殺した runner。" % (
        (df.exit_reason[tgA] == "SL").sum(), (df.exit_reason[tgA] == "TP").sum(), (df.exit_reason[tgA] == "TIME").sum(), R0[tgA].mean()))
    say()
    say("| 窓 | n | 発動A | **A s=0 diff / t / p** | A s=0.10 diff / t | A s=0.22 diff / t | B s=0 diff / t | 研究延長(終値≤0→0R) diff / t | 上位10%残存 A | 勝率 原→A |")
    say("|---|---|---|---|---|---|---|---|---|---|")
    P3 = {}
    for lab, m in masks:
        m = m.to_numpy()
        dA = R_A[m] - R0[m]; tA, pA = tstat(dA)
        d10 = R_A10[m] - R0[m]; d22 = R_A22[m] - R0[m]; dB = R_B[m] - R0[m]; dE = R_ext[m] - R0[m]
        P3[lab] = (dA.mean(), tA, pA, d10.mean(), tstat(d10)[0], top_ret(R0[m], R_A[m]))
        say("| %s | %d | %d | **%+.4f / %+.2f / %.4f** | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %+.4f / %+.2f | %.0f%% | %.1f→%.1f%% |" % (
            lab, m.sum(), (m & tgA).sum(), dA.mean(), tA, pA, d10.mean(), tstat(d10)[0], d22.mean(), tstat(d22)[0], dB.mean(), tstat(dB)[0],
            dE.mean(), tstat(dE)[0], top_ret(R0[m], R_A[m]), 100 * (R0[m] > 0).mean(), 100 * (R_A[m] > 0).mean()))
    say()
    say("### P3b. 分解（全本）: 研究 diff → 終値約定 → 48 本延長 → 逆指値（安値発動）")
    dres = fill0 - R0; dcl = fillc - R0
    say("研究ルール(0R 約定・48本) %+.4f (t%+.2f) → 同トリガ・終値約定 %+.4f (t%+.2f) → 研究ルール 48 本延長・0R 約定 %+.4f (t%+.2f) → 逆指値 A・s=0 %+.4f (t%+.2f) → A・s=0.10 %+.4f (t%+.2f)" % (
        dres.mean(), tstat(dres)[0], dcl.mean(), tstat(dcl)[0], (R_ext - R0).mean(), tstat(R_ext - R0)[0], (R_A - R0).mean(), tstat(R_A - R0)[0], (R_A10 - R0).mean(), tstat(R_A10 - R0)[0]))
    # 研究ルールのトリガ本で、A はいつ発動していたか
    both = trig & tgA
    say("研究トリガ %d 本のうち逆指値 A も発動 %d 本。A の発動足が研究の決済足より早い %d 本（終値を待つ間に 0 を踏んでいた）。" % (
        trig.sum(), both.sum(), (kfA[both] < ktr[both]).sum()))
    say()

    # ---------- P5 grid ----------
    say("## P5. X 格子 × 在/外（P3A s=0 と s=0.10）— Bonferroni α=%.4f" % ALPHA)
    say("| X | 在 発動 / diff / t / p | 外 発動 / diff / t / p | 在 s=0.10 diff / t | 外 s=0.10 diff / t | 上位10%残存 在/外 | 研究ルール(参考) 在/外 diff |")
    say("|---|---|---|---|---|---|---|")
    IS = (df.year <= 2020).to_numpy(); OOS = ~IS
    P5 = {}
    for X in XS:
        RX, tgX, _, _ = run_be(X, False, 0.0); RX10, _, _, _ = run_be(X, False, 0.10)
        res = []
        for i_, r in enumerate(df.itertuples()):
            tg_, k_, f_ = research_rule(r.mfe, r.cl, X); res.append(0.0 if tg_ else r.R)
        res = np.asarray(res)
        cells = []
        for m in (IS, OOS):
            d = RX[m] - R0[m]; t, p = tstat(d); cells.append((m & tgX).sum(), d.mean(), t, p)
        d10i = RX10[IS] - R0[IS]; d10o = RX10[OOS] - R0[OOS]
        P5[X] = (cells[0][3], cells[0][1], cells[1][3], cells[1][1])
        say("| %.2f | %d / %+.4f / %+.2f / %.4f | %d / %+.4f / %+.2f / %.4f | %+.4f / %+.2f | %+.4f / %+.2f | %.0f%% / %.0f%% | %+.4f / %+.4f |" % (
            X, *cells[0], *cells[1], d10i.mean(), tstat(d10i)[0], d10o.mean(), tstat(d10o)[0],
            top_ret(R0[IS], RX[IS]), top_ret(R0[OOS], RX[OOS]), (res[IS] - R0[IS]).mean(), (res[OOS] - R0[OOS]).mean()))
    say()

    # ---------- P6 placebo ----------
    say("## P6. プラセボ: 武装足を同じ本の保有内一様ランダム足に置換（200 回）、以後は P3A と同じ安値発動・0R 約定。X=%.2f の実武装本のみ対象" % X0)
    rng = np.random.default_rng(20261104)
    idx_armed = np.nonzero(kaA >= 0)[0]
    obs = {lab: (R_A[m.to_numpy()] - R0[m.to_numpy()]).mean() for lab, m in masks}
    plc = {lab: [] for lab, _ in masks}
    for rep in range(200):
        R1 = R0.copy()
        for i in idx_armed:
            adv = loR[off[i]:off[i + 1]]; k = int(rng.integers(0, len(adv)))
            if k + 1 < len(adv):
                hit = np.nonzero(adv[k + 1:] <= ft[i])[0]
                if len(hit): R1[i] = 0.0
        for lab, m in masks:
            m = m.to_numpy(); plc[lab].append((R1[m] - R0[m]).mean())
    say("| 窓 | 観測 diff (P3A) | プラセボ diff 平均 | プラセボ 2.5–97.5% | 観測 ≥ の確率 | 観測 − プラセボ平均 |"); say("|---|---|---|---|---|---|")
    P6 = {}
    for lab, _ in masks:
        a = np.asarray(plc[lab]); pge = (a >= obs[lab]).mean()
        P6[lab] = (obs[lab] - a.mean(), pge)
        say("| %s | %+.4f | %+.4f | [%+.4f, %+.4f] | %.3f | %+.4f |" % (lab, obs[lab], a.mean(), np.percentile(a, 2.5), np.percentile(a, 97.5), pge, obs[lab] - a.mean()))
    say("（ランダム武装は実武装より早い足で武装することが多く、SL 前に 0 を踏む機会が増える。プラセボ diff が観測と同程度以上なら「+X 到達」という条件に情報は無い。）")
    say()

    # ---------- P7 tail detail ----------
    say("## P7. 尻尾（原型上位10%・上位1%）A s=0・全本")
    top10 = np.argsort(R0)[-max(1, n // 10):]; top1 = np.argsort(R0)[-max(1, n // 100):]
    say("上位10%% 合計R 原 %+.0f → A %+.0f（残存 %.0f%%、発動 %d/%d 本）／上位1%% 原 %+.0f → A %+.0f（発動 %d/%d）。研究ルール: 上位10%% 残存 %.0f%%。" % (
        R0[top10].sum(), R_A[top10].sum(), top_ret(R0, R_A), tgA[top10].sum(), len(top10), R0[top1].sum(), R_A[top1].sum(), tgA[top1].sum(), len(top1), top_ret(R0, fill0)))
    say()

    # ---------- 判定 ----------
    say("## 判定（事前固定の規則）")
    sigA = {w: (P3[w][2] < ALPHA and P3[w][0] > 0) for w in ("在 2010-20", "外 2021-26", "2024-26")}
    say("- P3A s=0 Bonferroni 有意(+): 在 %s / 外 %s / 2024-26 %s" % (sigA["在 2010-20"], sigA["外 2021-26"], sigA["2024-26"]))
    say("- P3A s=0.10 外 t = %+.2f（≥2 必要）" % P3["外 2021-26"][4])
    say("- 尻尾残存 A 在/外 = %.0f%% / %.0f%%（≥90 必要）" % (P3["在 2010-20"][5], P3["外 2021-26"][5]))
    say("- P6 プラセボ超過 p: 在 %.3f / 外 %.3f" % (P6["在 2010-20"][1], P6["外 2021-26"][1]))
    say("- P1+P2(s=0.10) 研究 diff: 在 %+.4f→%+.4f (t%+.2f) / 外 %+.4f→%+.4f (t%+.2f)" % (
        P012["在 2010-20"][0], P012["在 2010-20"][4], P012["在 2010-20"][5], P012["外 2021-26"][0], P012["外 2021-26"][4], P012["外 2021-26"][5]))
    if sigA["在 2010-20"] and sigA["外 2021-26"] and sigA["2024-26"] and P3["外 2021-26"][4] >= 2 and P3["在 2010-20"][5] >= 90 and P3["外 2021-26"][5] >= 90 and P6["在 2010-20"][1] < 0.005 and P6["外 2021-26"][1] < 0.005:
        v = "survived"
    elif not (sigA["在 2010-20"] and sigA["外 2021-26"]) or (P012["在 2010-20"][4] <= 0 and P012["外 2021-26"][4] <= 0):
        v = "broken"
    else:
        v = "inconclusive"
    say("- 機械判定: **%s**" % v)
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("→", OUT)


if __name__ == "__main__":
    main()
