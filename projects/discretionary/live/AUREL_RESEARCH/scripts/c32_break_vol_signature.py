# -*- coding: utf-8 -*-
"""
[cycle32 研究レーン 2026-11-10] 【深化・path／機構】壁抜け（再加速トリガー）は「事象」か — 建玉直後 1 時間の価格過程に
ボラ・自己相関の署名があるか（同スロット・同大きさの足に合わせたランダム・アンカーとの対比）
— 深化系統で閉じたのは「F_k 可測の条件づけ（経過時間 c7・時計 c21・含み水準・形 c23）に出口情報なし」。残っているのは
  「壁抜け直後の価格過程そのものが、同じ時刻・同じ大きさの足の後の過程と違うか」（backlog 残存: 壁抜け後 k=1..12 の ρ_1 vs 無条件）。
  これは入口フィルタではない（建玉の有無を変えない・事象の性質の記述）。問い:
  (V) 壁抜け後 1 時間（j=1..12）の実現ボラは、同じ ET スロット・同じ建玉足レンジのランダム足の後より高いか（事象性＝情報到着／注文集積の解消）。
  (A) 壁抜け後 1 時間の 5 分リターンの lag-1 自己相関は、同対照より 正（運動量・逆指値の連鎖）か 負（反転・流動性の戻し）か。
  (D) 記述: 建玉方向への符号つきドリフト（c13 M_flow 棄却の対照つき再掲）・署名の減衰（j=13..36）・bar1 だけの寄与。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/refute_c4_scan_paths_2010_2026.json（19404 本・entry_time/side/risk/b/R/exit/hold/year/atr/jh/wall_kind）、
  data/macro/XAU_m5_ohlc.npz（bid・完全格子・前値埋め・1728576 本）。既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し。
  整合: 本の建玉足 i0 は ts==entry_time で引く（格子の穴 19 → 不一致は除外・件数印字）。refute_c2_fullpaths.npz の clR と
  npz close の k=6 変化を 2000 本で突合し ≤0.02 USD の比率を印字（<95% なら全判定 inconclusive）。
窓（足）: pre = j∈[−12,−1]（トリガー足の前 1 時間）・post = j∈[1,12]（建玉足の次の 1 時間）・post2 = j∈[13,36]。
  r_j = close[i0+j] − close[i0+j−1]（USD・flat 足は 0 のまま・両群同扱い）。
  母数: pre〜post2 が建玉足と同じ ET セッション（(ET+6h) の暦日）∧ post の flat 足 ≤3 ∧ 月〜金。
対照（プラセボ・アンカー）: 本ごとに K=4。
  SET A = 同 ET 5 分スロット・±28 暦日（d≠0）・月〜金・アンカー足 非 flat・同セッション条件・実本の建玉足 ±12 本に入らない。
  SET B（主）= SET A ∧ アンカー足レンジ (high−low) が建玉足レンジの [0.8, 1.25] 倍（候補 <K なら [0.67,1.5] へ拡張・それでも <K なら本を除外・件数印字）。
  SET A は「その時刻の普通の足」、SET B は「その時刻に同じ大きさの足が出た後」＝ボラ・クラスタリングを差し引いた壁抜け固有分。
統計:
  V: 本ごとの対数差 ΔL = log V_post(本) − mean_k log V_post(プラセボ_k)（V = RMS of r）。平均と**建玉 UTC 日クラスタ SE**。
     併記: ΔL_pre・ΔL_post2・λ = log(V_post/V_pre) の差・bar1 を除いた ΔL(j=2..12)。
  A: プール lag-1 相関 ρ_1 = Σ z_j z_{j+1} / Σ z_j²（z = r/V_post・アンカー内標準化・j=1..12 の 11 組）。Δρ = ρ_1(本) − ρ_1(プラセボ)。
     se は**日ブロック bootstrap 1000**（日単位の (分子,分母) を再標本）。併記: pre 窓の ρ_1（両群・無条件の校正）。
  D: 記述。mean(SGN·Σ_{1..12} r)/risk（本）と同 side を付けたプラセボ（背景ドリフト）。
窓: 在 2010-20（判定）／外 2021-26H1（確認）／近年 2024-26H1（記述）。建玉年で切る（D2）。
判定:
  H_V（主・SET B）: PASS = 在 ΔL_post>0 ∧ t≥2 ∧ 外 ΔL_post>0 ∧ t≥1.5。予測: 正（壁抜けは同大きさの足より後が荒い）。
     負で同基準なら「壁抜け後は静まる」（逆向きの構造）。他 null（MDE = 2se）。
  H_A（主・SET B）: PASS = 在 |z|≥2.5 ∧ 外 同符号 |z|≥2。符号は事前に固定しない: + = 運動量／− = 反転。他 null。
  SET A は記述（事象性の素の大きさ・ほぼ確実に正と予想＝ボラ・クラスタリング）。
陽性対照: 在 SET B の本側 post リターンを ×1.10 して H_V の t／ AR(1) φ=+0.05 を注入して H_A の z。
  これで t≥2／z≥2.5 に届かなければ MDE 以下としか言わない。
look-ahead: 窓はすべて建玉後の足（pre は建玉前・記述）。プラセボは建玉時刻の情報を使わない（±28 日の両側＝事後の時刻を含むが
  「同スロットの普通の足」の基準であり予測ではない）。
事前の最重大反証: (i) トリガーは足の途中で起き、建玉足の残りと bar1 がトリガーの動きの続き（同一の動きの分割）→ bar1 を除いた版を併記。
  (ii) レンジ一致は「大きい足」の分布の中心だけ揃え尾部は揃わない（本の建玉足は片方向の大足）→ ΔL_pre を印字し pre でも差があれば
  「一致の残差」として post の差から差し引いた値を併記。(iii) bid のみ（スプレッド拡大の戻しが負の自己相関を作る・両群同配信で相殺）。
  (iv) 壁抜け＝複数本が同時刻に建つ（同日クラスタ）→ 日クラスタ SE。(v) 2026-06 まで。(vi) 多重検定: 判定は H_V・H_A の 2 セル。
seed 20261110。
"""
import os, json, time
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c32_break_vol_signature_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261110)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle32] 壁抜け直後 1 時間のボラ・自己相関の署名（同スロット・同レンジ プラセボ対照）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c32_break_vol_signature.py)")

# ---------- price grid ----------
z = np.load(os.path.join(MAC, "XAU_m5_ohlc.npz"))
ts = z["ts"].astype(np.int64); C = z["close"].astype(float); H = z["high"].astype(float); Lo = z["low"].astype(float)
NB = len(ts); step = int(ts[1] - ts[0]); assert step == 300
r = np.zeros(NB); r[1:] = np.diff(C)
flat = (r == 0.0); rng_bar = H - Lo
idx_full_grid = np.all(np.diff(ts) == 300)
dt_utc = pd.to_datetime(ts, unit="s", utc=True); dt_ny = dt_utc.tz_convert(NY)
SLOT = (dt_ny.hour.to_numpy() * 12 + dt_ny.minute.to_numpy() // 5).astype(np.int32)
WD = dt_ny.weekday.to_numpy().astype(np.int8)
sess = dt_ny + pd.Timedelta(hours=6)
SESS = (sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy())
say(f"- npz {NB} 本 {dt_utc[0]}〜{dt_utc[-1]} UTC（⑩）・完全格子 {idx_full_grid}・flat 全体 {flat.mean()*100:.1f}%（⑪）・読込 {time.time()-T0:.1f}s")

# ---------- trades ----------
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
T = pd.DataFrame(J["trades"]).sort_values("entry_time").reset_index(drop=True)
FT = J["frozen"]["FEED_TOL"]
N0 = len(T)
pos = np.searchsorted(ts, T["entry_time"].to_numpy())
pos = np.clip(pos, 0, NB - 1)
ok_ts = ts[pos] == T["entry_time"].to_numpy()
say(f"- 本 {N0}・ts 一致 {ok_ts.sum()}（不一致 {(~ok_ts).sum()} は除外）・FEED_TOL {FT}")
T = T[ok_ts].reset_index(drop=True); I0 = pos[ok_ts]
SGN = np.where(T["side"].to_numpy() == "BUY", 1.0, -1.0); RISK = T["risk"].to_numpy(); YEAR = T["year"].to_numpy()

# 整合: fullpaths clR vs npz (k=6)
zz = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = zz["clR"].astype(float); off = zz["off"].astype(np.int64)
# fullpaths は c1 の entry_time 昇順 (= T の順・不一致本も含む全 19404) → 元の順序で index を持つ
full_idx = np.arange(N0)[ok_ts]
cand = np.where(T["hold"].to_numpy() >= 6)[0]
smp = rng.choice(cand, size=min(2000, len(cand)), replace=False)
dif = []
for q in smp:
    o = off[full_idx[q]]
    pc = SGN[q] * (C[I0[q] + 6] - C[I0[q]]) / RISK[q]
    dif.append(abs(pc - (clR[o + 6] - clR[o])) * RISK[q])
dif = np.array(dif); agree = (dif <= 0.02).mean()
say(f"- 整合（fullpaths clR k=6 vs npz close・2000 本）: |差|≤0.02 USD {agree*100:.1f}%・中央値 {np.median(dif):.4f} USD → {'OK' if agree>=0.95 else 'INCONCLUSIVE'}")

# ---------- window validity ----------
PRE = np.arange(-12, 0); POST = np.arange(1, 13); POST2 = np.arange(13, 37)
def valid_anchor(I):
    I = np.asarray(I)
    okb = (I - 12 >= 0) & (I + 36 < NB)
    I2 = np.where(okb, I, 100)
    same = (SESS[I2 - 12] == SESS[I2]) & (SESS[I2 + 36] == SESS[I2])
    nflat = flat[I2[:, None] + POST[None, :]].sum(1)
    return okb & same & (nflat <= 3) & (WD[I2] <= 4)
VAL = valid_anchor(I0)
say(f"- 母数: 同セッション ∧ post flat≤3 ∧ 月〜金 → {VAL.sum()}/{len(T)}（除外 {(~VAL).sum()}）")

# near-trade mask (±12 bars of any real entry)
near = np.zeros(NB, dtype=bool)
for d in range(-12, 13):
    near[np.clip(I0 + d, 0, NB - 1)] = True

# ---------- placebo selection ----------
K = 4
D = np.array([d for d in range(-28, 29) if d != 0])
def pick_placebo(I, rng_match):
    """I: anchor indices (valid). returns (K-array of indices or -1, n_cand)"""
    n = len(I)
    Cd = I[:, None] + 288 * D[None, :]            # (n, 56)
    Cd = np.clip(Cd, 13, NB - 37)
    okc = (SLOT[Cd] == SLOT[I][:, None]) & (WD[Cd] <= 4) & (~flat[Cd]) & (~near[Cd])
    okc &= (SESS[Cd - 12] == SESS[Cd]) & (SESS[Cd + 36] == SESS[Cd])
    nfl = flat[Cd[:, :, None] + POST[None, None, :]].sum(2)
    okc &= nfl <= 3
    if rng_match is not None:
        ratio = rng_bar[Cd] / np.maximum(rng_bar[I][:, None], 1e-9)
        ok1 = okc & (ratio >= 0.8) & (ratio <= 1.25)
        ok2 = okc & (ratio >= 0.67) & (ratio <= 1.5)
        enough1 = ok1.sum(1) >= K
        okc = np.where(enough1[:, None], ok1, ok2)
    out = np.full((n, K), -1, dtype=np.int64); ncand = okc.sum(1)
    for q in range(n):
        c = Cd[q][okc[q]]
        if len(c) >= K:
            out[q] = rng.choice(c, size=K, replace=False)
    return out, ncand

IV = I0[VAL]
PA, nA = pick_placebo(IV, None)
PB, nB = pick_placebo(IV, True)
okA = (PA >= 0).all(1); okB = (PB >= 0).all(1)
say(f"- プラセボ SET A: 候補中央値 {np.median(nA):.0f}・K=4 確保 {okA.sum()}/{len(IV)}；SET B（レンジ一致）: 候補中央値 {np.median(nB):.0f}・確保 {okB.sum()}/{len(IV)}")
# range match quality
rr = rng_bar[PB[okB]] / rng_bar[IV[okB]][:, None]
say(f"- SET B レンジ比（プラセボ/本）中央値 {np.median(rr):.3f}・p10 {np.percentile(rr,10):.2f}・p90 {np.percentile(rr,90):.2f}；本の建玉足レンジ 中央値 {np.median(rng_bar[IV]):.2f} USD vs 同スロット一般（SET A）{np.median(rng_bar[PA[okA]]):.2f}")

# ---------- window stats ----------
def win_stats(I):
    """I: (n,) anchor idx → dict of per-anchor arrays"""
    I = np.asarray(I)
    rp = r[I[:, None] + PRE[None, :]]; ro = r[I[:, None] + POST[None, :]]; r2 = r[I[:, None] + POST2[None, :]]
    Vp = np.sqrt((rp ** 2).mean(1)); Vo = np.sqrt((ro ** 2).mean(1)); V2 = np.sqrt((r2 ** 2).mean(1))
    Vo_ex1 = np.sqrt((ro[:, 1:] ** 2).mean(1))
    zo = ro / np.maximum(Vo, 1e-9)[:, None]; zp = rp / np.maximum(Vp, 1e-9)[:, None]
    num_o = (zo[:, :-1] * zo[:, 1:]).sum(1); den_o = (zo[:, :-1] ** 2).sum(1)
    num_p = (zp[:, :-1] * zp[:, 1:]).sum(1); den_p = (zp[:, :-1] ** 2).sum(1)
    return dict(Vp=Vp, Vo=Vo, V2=V2, Vo_ex1=Vo_ex1, num_o=num_o, den_o=den_o, num_p=num_p, den_p=den_p,
                sum_o=ro.sum(1), bar1=np.abs(ro[:, 0]), ro=ro)

def logm(x): return np.log(np.maximum(x, 1e-6))

def cluster_t(d, day):
    d = np.asarray(d, float); n = len(d); m = d.mean()
    df = pd.DataFrame({"d": d - m, "g": day}).groupby("g")["d"].sum()
    se = np.sqrt((df.to_numpy() ** 2).sum()) / n
    return m, se, (m / se if se > 0 else np.nan)

def rho_diff_boot(num_t, den_t, num_p, den_p, day, nb=1000):
    """pooled rho difference with day-block bootstrap"""
    df = pd.DataFrame({"nt": num_t, "dt": den_t, "np": num_p, "dp": den_p, "g": day}).groupby("g").sum()
    A = df.to_numpy(); G = len(A)
    rho_t = A[:, 0].sum() / A[:, 1].sum(); rho_p = A[:, 2].sum() / A[:, 3].sum()
    bs = []
    for _ in range(nb):
        s = A[rng.integers(0, G, G)].sum(0)
        bs.append(s[0] / s[1] - s[2] / s[3])
    bs = np.array(bs)
    return rho_t, rho_p, rho_t - rho_p, bs.std()

WIN = {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026)}
Tv = T[VAL].reset_index(drop=True); SGNv = SGN[VAL]; RISKv = RISK[VAL]; YEARv = YEAR[VAL]
DAY = (Tv["entry_time"].to_numpy() // 86400).astype(np.int64)

def run_set(P, okP, name, inject_vol=None, inject_ar=None):
    say(f"\n## {name}")
    sel = okP
    I = IV[sel]; Pk = P[sel]; day = DAY[sel]; yr = YEARv[sel]; sg = SGNv[sel]; rk = RISKv[sel]
    st = win_stats(I)
    # placebo stats averaged over K
    pl = [win_stats(Pk[:, k]) for k in range(K)]
    ro_t = st["ro"].copy()
    if inject_vol is not None: ro_t = ro_t * inject_vol
    if inject_ar is not None:
        # AR(1) injection: r_j += phi * r_{j-1} (within window)
        ro_t = ro_t.copy(); ro_t[:, 1:] += inject_ar * ro_t[:, :-1]
    Vo_t = np.sqrt((ro_t ** 2).mean(1)); zo = ro_t / np.maximum(Vo_t, 1e-9)[:, None]
    num_t = (zo[:, :-1] * zo[:, 1:]).sum(1); den_t = (zo[:, :-1] ** 2).sum(1)
    Vo_t_ex1 = np.sqrt((ro_t[:, 1:] ** 2).mean(1))
    lp_Vo = np.mean([logm(p["Vo"]) for p in pl], 0); lp_Vp = np.mean([logm(p["Vp"]) for p in pl], 0)
    lp_V2 = np.mean([logm(p["V2"]) for p in pl], 0); lp_Vo_ex1 = np.mean([logm(p["Vo_ex1"]) for p in pl], 0)
    num_pl = np.sum([p["num_o"] for p in pl], 0); den_pl = np.sum([p["den_o"] for p in pl], 0)
    nump_pl = np.sum([p["num_p"] for p in pl], 0); denp_pl = np.sum([p["den_p"] for p in pl], 0)
    drift_pl = np.mean([p["sum_o"] for p in pl], 0)
    res = {}
    for w, (y0, y1) in WIN.items():
        m = (yr >= y0) & (yr <= y1); n = m.sum(); d = day[m]
        dL_post = logm(Vo_t[m]) - lp_Vo[m]; dL_pre = logm(st["Vp"][m]) - lp_Vp[m]
        dL_post2 = logm(st["V2"][m]) - lp_V2[m]; dL_ex1 = logm(Vo_t_ex1[m]) - lp_Vo_ex1[m]
        dLam = (logm(Vo_t[m]) - logm(st["Vp"][m])) - (lp_Vo[m] - lp_Vp[m])
        a = cluster_t(dL_post, d); b = cluster_t(dL_pre, d); c = cluster_t(dL_post2, d); e = cluster_t(dL_ex1, d); f = cluster_t(dLam, d)
        rt, rp_, dr, se_r = rho_diff_boot(num_t[m], den_t[m], num_pl[m], den_pl[m], d)
        rtp, rpp, drp, se_rp = rho_diff_boot(st["num_p"][m], st["den_p"][m], nump_pl[m], denp_pl[m], d)
        dr_t = cluster_t(sg[m] * st["sum_o"][m] / rk[m], d); dr_p = cluster_t(sg[m] * drift_pl[m] / rk[m], d)
        bar1_share_t = (st["bar1"][m] ** 2).sum() / (st["Vo"][m] ** 2 * 12).sum()
        bar1_share_p = np.mean([(p["bar1"][m] ** 2).sum() / (p["Vo"][m] ** 2 * 12).sum() for p in pl])
        say(f"- **{w}** n {n}（日 {len(np.unique(d))}）: V_post 本 中央値 {np.median(Vo_t[m]):.3f} USD／プラセボ {np.median(np.exp(lp_Vo[m])):.3f}")
        say(f"  - ΔL_post（log 比・主）**{a[0]:+.4f}（se {a[1]:.4f}・t {a[2]:+.2f}・MDE {2*a[1]:.4f}）** ＝ 比 {np.exp(a[0]):.3f}；bar1 除外 ΔL(2..12) {e[0]:+.4f}（t {e[2]:+.2f}）")
        say(f"  - ΔL_pre {b[0]:+.4f}（t {b[2]:+.2f}）・ΔL_post2(13..36) {c[0]:+.4f}（t {c[2]:+.2f}）・Δλ=Δlog(post/pre) {f[0]:+.4f}（t {f[2]:+.2f}）・post−pre 差し引き {a[0]-b[0]:+.4f}")
        say(f"  - ρ_1 post 本 {rt:+.4f}／プラセボ {rp_:+.4f} → **Δρ {dr:+.4f}（se {se_r:.4f}・z {dr/se_r:+.2f}・MDE {2*se_r:.4f}）**；pre 窓 ρ_1 本 {rtp:+.4f}／プラセボ {rpp:+.4f}（Δ {drp:+.4f}・z {drp/se_rp:+.2f}）")
        say(f"  - 方向ドリフト Σ_{{1..12}} SGN·r/risk 本 {dr_t[0]:+.4f}R（t {dr_t[2]:+.2f}）／同 side プラセボ {dr_p[0]:+.4f}R（t {dr_p[2]:+.2f}）；bar1 の post 分散シェア 本 {bar1_share_t:.3f}／プラセボ {bar1_share_p:.3f}（一様なら 0.083）")
        res[w] = dict(dL=a, dLpre=b, dL2=c, dLex1=e, dr=(dr, se_r), rt=rt, rp=rp_, n=n)
    return res

resA = run_set(PA, okA, "SET A（同スロット・±28 日・記述）")
resB = run_set(PB, okB, "SET B（同スロット ∧ 建玉足レンジ一致・主）")

# ---------- 判定 ----------
say("\n## 判定（事前固定・SET B）")
a_in = resB["在 2010-20"]["dL"]; a_out = resB["外 2021-26H1"]["dL"]
passV = (a_in[0] > 0 and a_in[2] >= 2 and a_out[0] > 0 and a_out[2] >= 1.5)
negV = (a_in[0] < 0 and a_in[2] <= -2 and a_out[0] < 0 and a_out[2] <= -1.5)
say(f"- H_V: 在 ΔL_post {a_in[0]:+.4f} (t {a_in[2]:+.2f})／外 {a_out[0]:+.4f} (t {a_out[2]:+.2f}) → **{'PASS（壁抜け後は同レンジ足より荒い）' if passV else ('PASS 逆向き（静まる）' if negV else 'null')}**")
d_in, s_in = resB["在 2010-20"]["dr"]; d_out, s_out = resB["外 2021-26H1"]["dr"]
z_in = d_in / s_in; z_out = d_out / s_out
passA = (abs(z_in) >= 2.5 and np.sign(d_in) == np.sign(d_out) and abs(z_out) >= 2)
say(f"- H_A: 在 Δρ {d_in:+.4f} (z {z_in:+.2f})／外 {d_out:+.4f} (z {z_out:+.2f}) → **{('PASS ' + ('運動量（+）' if d_in>0 else '反転（−）')) if passA else 'null'}**")

# ---------- 陽性対照（在・SET B） ----------
say("\n## 陽性対照（在・SET B・注入）")
rV = run_set(PB, okB, "注入 ×1.10（本側 post）", inject_vol=1.10)
rA = run_set(PB, okB, "注入 AR(1) φ=+0.05（本側 post）", inject_ar=0.05)
say(f"- ×1.10 注入 → 在 ΔL_post t {rV['在 2010-20']['dL'][2]:+.2f}（元 {a_in[2]:+.2f}）；φ=0.05 注入 → 在 Δρ z {rA['在 2010-20']['dr'][0]/rA['在 2010-20']['dr'][1]:+.2f}（元 {z_in:+.2f}）")

# ---------- 記述: 側・壁種・jh 帯・年別（SET B・post ΔL と Δρ） ----------
say("\n## 記述（SET B・事後・判定不使用）")
sel = okB; I = IV[sel]; Pk = PB[sel]; day = DAY[sel]; yr = YEARv[sel]
st = win_stats(I); pl = [win_stats(Pk[:, k]) for k in range(K)]
lp_Vo = np.mean([logm(p["Vo"]) for p in pl], 0); dL = logm(st["Vo"]) - lp_Vo
num_pl = np.sum([p["num_o"] for p in pl], 0); den_pl = np.sum([p["den_o"] for p in pl], 0)
Tb = Tv[sel].reset_index(drop=True)
def sub(mask, label):
    out = []
    for w, (y0, y1) in WIN.items():
        m = mask & (yr >= y0) & (yr <= y1)
        if m.sum() < 50: out.append(f"{w} n<50"); continue
        a = cluster_t(dL[m], day[m]); rt, rp_, dr, se_r = rho_diff_boot(st["num_o"][m], st["den_o"][m], num_pl[m], den_pl[m], day[m], nb=400)
        out.append(f"{w} n{m.sum()} ΔL {a[0]:+.3f} (t {a[2]:+.1f}) Δρ {dr:+.3f} (z {dr/se_r:+.1f})")
    say(f"- {label}: " + "；".join(out))
sub(Tb["side"].to_numpy() == "BUY", "BUY"); sub(Tb["side"].to_numpy() == "SELL", "SELL")
for wk in sorted(Tb["wall_kind"].unique()): sub(Tb["wall_kind"].to_numpy() == wk, f"wall {wk}")
jh = Tb["jh"].to_numpy(); sub((jh >= 7) & (jh <= 12), "jh 7-12（本番帯）"); sub(~((jh >= 7) & (jh <= 12)), "jh その他")
ex = Tb["exit"].to_numpy(); sub(ex == "TP", "決着 TP（事後・look-ahead）"); sub(ex == "SL", "決着 SL（事後・look-ahead）")
# 年別
rows = []
for y in range(2010, 2027):
    m = yr == y
    if m.sum() < 30: continue
    a = cluster_t(dL[m], day[m]); rt, rp_, dr, se_r = rho_diff_boot(st["num_o"][m], st["den_o"][m], num_pl[m], den_pl[m], day[m], nb=300)
    rows.append(f"{y}: n{m.sum()} ΔL {a[0]:+.3f} (t {a[2]:+.1f}) ρ本 {rt:+.3f} ρpl {rp_:+.3f} Δρ {dr:+.3f} (z {dr/se_r:+.1f})")
say("- 年別: " + " | ".join(rows))
# ΔL の分布（平均 vs 中央値・正の割合）
for w, (y0, y1) in WIN.items():
    m = (yr >= y0) & (yr <= y1)
    say(f"- {w} ΔL_post 分布: 平均 {dL[m].mean():+.4f}・中央値 {np.median(dL[m]):+.4f}・正の割合 {(dL[m]>0).mean()*100:.1f}%・sd {dL[m].std():.3f}")
# bar-by-bar profile of |r| ratio (trade / placebo) j=1..12 (在/外)
for w, (y0, y1) in WIN.items():
    m = (yr >= y0) & (yr <= y1)
    rt_ = np.sqrt((st["ro"][m] ** 2).mean(0)); rp_ = np.sqrt(np.mean([(p["ro"][m] ** 2).mean(0) for p in pl], 0))
    say(f"- {w} 足別 RMS 比（本/プラセボ・j=1..12）: " + " ".join(f"{x:.2f}" for x in rt_ / rp_))

say(f"\n- 実行時間 {time.time()-T0:.1f}s・scan 無し・MT5 無し・外部通信無し・seed 20261110")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("saved", OUT)
