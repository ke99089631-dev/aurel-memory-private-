# -*- coding: utf-8 -*-
"""
[cycle21 研究レーン 2026-11-07] 【深化・path】建玉中の壁→壁(再加速)の本にとって「時計」（ET 現地時刻）は出口情報を持つか
— cycle7 は「経過時間 k」は含み水準 cl_k を超える情報を持たない（マルコフ性）と確定した。本件は時計を k の代わりに置く:
  (A) 側非依存: ET h 時に生きている本の残り path e = R* − cl_k は 0 か（RW 帰無・時刻のどこかで出口情報が立つか）。
  (B) 側×時計: D_e(h) = e(BUY) − e(SELL) の 24 時間プロファイル。cycle16 の夜間ドリフト（London 22–08 時＝ET 17–03 時 外 +6.09 bp/日）と
      cycle18/反証 05:30 K8 の「D_e(16:50 アンカー) 外 +0.37R は側非依存の夜間ドリフト」を**時計の形**として検定する:
      純夜間ドリフト型なら D_e は夜の直前（ET 18–20 時アンカー・夜が丸ごと先にある）で最大、夜を消費した朝（ET 03–08 時アンカー・
      先に昼の負ドリフトがある）で最小になる筈。
  (C) 記述: SL/TP 決着の時刻別ハザード（bars-at-risk 正規化・同時刻帯の |Δ| ボラで割った比）＝「滑り・執行が起きる時刻の地図」
      （DATA_MAP §4 の滑り実測への接続・出口提案ではない）。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/c8_crossasset_features.csv（19404 本・entry_time 昇順）、data/c1_reaccel_paths_2010_2026.json（FEED_TOL・順序 assert）、
  data/refute_c2_fullpaths.npz（全足 clR・off・規約: 足 j の開始時刻 = entry_time+300·j、index hold = 決着足）、
  data/macro/XAU_m5_close.npz（整合性検査とボラ・プロファイルのみ）。既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し。
時刻付与の母集合: 足 j が建玉と**同じセッション**（セッション日 = (ET 現地 + 6h) の暦日・18:00 ET 始まり）にある足だけ
  （cycle18 で日内整合 100% を確認・ブレイク・週末を跨いだ足番号は使わない）。
  **整合性検査（⑩⑫）**: アンカー（k≥6）の path k−6→k の価格変化（SGN·ΔclR·risk）と npz 同時刻 close 差を突合し、|差| ≤0.02 USD の比率を先に印字。
  <90% なら全判定 inconclusive。
アンカー: ET h:00 ちょうどの足（h = 0..23・17 を除く）で生きている本（hold > k ≥ 1）。1 本 1 観測/アンカー。
  e = R* − cl_k（R* = R + ft·1{SL,TP} ①・cl_k は side 符号つき R 単位）。**セッション日クラスタ SE**（同日の本は同じ値動きを共有）。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（建玉年・D2・判定は外・在は記述）。
判定:
  H_A（時計の出口情報・側非依存）: 外 23 アンカーの e 平均。PASS（時計に情報あり）= いずれかの h で |t_cl| ≥ 2.99（Bonferroni 23・α 0.05）
     ∧ 在 同符号 |t| ≥ 1.5。他 null（各 h の MDE 2se・t の sd（帰無 ≈1）を印字）。予測: null（cycle7 のマルコフ性の時計版）。
     陽性対照: 公正化しない e_raw = R − cl_k は既知の −ft·P(SL/TP) シフトを持つ → 外 プールで t ≤ −2 なら方法は検出する。
  H_B（側×時計の形・主）: ブロック N = アンカー ET 18/19/20 時（本ごとに最初のアンカー 1 つ）、ブロック D = ET 03〜08 時（同）。
     D_e(block) = 2×（e ~ 1 + SGN の SGN 係数・日クラスタ）。対比 C = D_e(N) − D_e(D)（独立ブロック・se を合成）。
     予測: C > 0 ∧ D_e(N) > 0。PASS = 外 C>0 (t≥2) ∧ 外 D_e(N)>0 (t≥2) ∧ 近年 C>0 (t≥1.5)。
     反対の形（D_e(D) > D_e(N)・t≤−2）なら「夜間ドリフト型ではない」。他 null（MDE）。
     陽性対照（同じ信頼性クラス）: アンカー ET 16:00 の D_e は cycle18 の 16:50 アンカー 外 +0.369R (t4.0) に近い値を返す筈。
     注入: 外 N ブロックの e に +0.05·SGN を注入して t を印字（MDE の実測）。
  記述（判定不使用）: 24 時間 D_e(h)・e(h) プロファイル、各 h の BUY 比・k 中央値・建玉 ET 時刻の組成（反証 (i) 用）、
     時刻別 SL/TP ハザード（bars-at-risk・同セッション足のみ・j≥1）とボラ比、flat 足比率。
look-ahead: アンカー時点で cl_k・side・時刻は既知。R* は事後（残り path の測定のみ）。
事前の最重大反証: (i) D_e(h) の形は「時計」でなく**建玉時刻の組成**（夜アンカーで生きている本は ET 13–16 時建玉の長保有に選択され、
  side 組成も違う）で作れる → 各ブロックの建玉時刻分布と、建玉ブロックを固定した部分集合の D_e を併記。(ii) 生存選択は F_k 可測なので
  RW 帰無の下で e は martingale（選択で偏らない）だが、side と同日の動きの相関（反証 05:30 K3）は D_e を機械的に作り得る → 同日
  リターンで統制した版を記述。(iii) 2026H1 の押し上げ（LOYO −2026 を併記）。(iv) bid のみ・2026-06 まで。(v) 多重検定: 判定は
  H_A（Bonferroni 23）と H_B（2 セル）のみ。seed 20261107。
"""
import os, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c21_clock_hazard_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261107)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle21] 時計は出口情報を持つか（ET 時刻別 残り path e・D_e(h)・決着ハザード）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c21_clock_hazard.py)")

# ---------- trades ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy()
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c1_et = np.sort(np.array([t["entry_time"] for t in J["trades"]])); assert np.array_equal(c1_et, ET)
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK; ISLT = np.isin(EXIT, ["SL", "TP"]); RSTAR = R + ft * ISLT
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"].astype(float); off = z["off"].astype(np.int64)
assert len(off) - 1 == N and np.all(np.diff(off) == HOLD + 1)
M = len(clR)
e_utc = pd.to_datetime(ET, unit="s", utc=True); e_ny = e_utc.tz_convert(NY)
E_H = e_ny.hour.to_numpy()
say(f"- 本 {N}、entry {e_utc[0].date()}〜{e_utc[-1].date()} UTC（⑩）、path 足 {M}、FEED_TOL {FT}、exit {dict(pd.Series(EXIT).value_counts())}")

# ---------- per-bar clock ----------
TID = np.repeat(np.arange(N), HOLD + 1); JJ = np.arange(M) - off[TID]
TS = ET[TID] + 300 * JJ
b_utc = pd.to_datetime(TS, unit="s", utc=True); b_ny = b_utc.tz_convert(NY)
B_H = b_ny.hour.to_numpy(); B_MI = b_ny.minute.to_numpy()
sess = b_ny + pd.Timedelta(hours=6)
B_SESS = (sess.year.to_numpy().astype(np.int64) * 10000 + sess.month.to_numpy() * 100 + sess.day.to_numpy())
E_SESS = B_SESS[off[:-1]]  # j=0 bar's session
SAME = B_SESS == E_SESS[TID]
# within-session continuity: the first bar leaving the session invalidates all later bars of that trade (weekend/break)
# (session equality already excludes later bars since session key only increases along the path)
ALIVE = JJ < HOLD[TID]  # bar j < hold => trade still open at bar j (settles at bar hold)
say(f"- 同セッション足 {SAME.mean()*100:.1f}%（{SAME.sum()}）、うち建玉中（j<hold）{(SAME & ALIVE).sum()}、j=0 建玉足 {N}")

# ---------- XAU grid (alignment + vol profile) ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float)
t_ny = pd.to_datetime(ts, unit="s", utc=True).tz_convert(NY)
g_h = t_ny.hour.to_numpy(); g_yr = t_ny.year.to_numpy(); g_wd = t_ny.weekday.to_numpy()
lc = np.log(cl); dr = np.zeros(len(lc)); dr[1:] = np.diff(lc)
say(f"- XAU npz {len(ts)} 本 {t_ny[0]}〜{t_ny[-1]}（⑩）、flat {np.mean(dr==0)*100:.1f}%（⑪）")
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)

# anchors: ET h:00 bars, same session, alive, k>=1
ANC = SAME & ALIVE & (B_MI == 0) & (JJ >= 1)
# alignment check on anchors with k>=6 (random 6000)
ai = np.flatnonzero(ANC & (JJ >= 6))
ai = rng.choice(ai, size=min(6000, len(ai)), replace=False)
i_now = idx_at(TS[ai]); i_prev = idx_at(TS[ai] - 1800)
okk = (i_now >= 0) & (i_prev >= 0)
dpath = SGN[TID[ai]] * (clR[ai] - clR[ai - 6]) * RISK[TID[ai]]
dnpz = cl[i_now] - cl[i_prev]
diff = np.abs(dpath[okk] - dnpz[okk])
fr = (diff <= 0.02).mean(); cc = np.corrcoef(dpath[okk], dnpz[okk])[0, 1]
say(f"- **整合性（⑩⑫）**: アンカー k−6→k の path 価格変化 vs npz 同時刻 close 差、|差|≤0.02 USD **{fr*100:.1f}%**（中央値 {np.median(diff):.4f} USD・ρ {cc:.4f}・n{okk.sum()}・格子欠け {(~okk).sum()}）")
ALIGN_OK = fr >= 0.9

# ---------- stats helpers (cluster SE via bincount) ----------
def ols_cluster(y, Z, cl_):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    _, inv = np.unique(cl_, return_inverse=True); G = inv.max() + 1
    S = np.zeros((G, Z.shape[1]))
    for p in range(Z.shape[1]): S[:, p] = np.bincount(inv, weights=Z[:, p] * e, minlength=G)
    V = ZtZi @ (S.T @ S) @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G
def cmean(y, cl_):
    b, se, G = ols_cluster(y, np.ones((len(y), 1)), cl_); return b[0], se[0], (b[0] / se[0] if se[0] > 0 else np.nan), G
def creg(y, x, cl_):
    Z = np.column_stack([np.ones(len(y)), x]); b, se, G = ols_cluster(y, Z, cl_); return b[1], se[1], (b[1] / se[1] if se[1] > 0 else np.nan), G

W = {"在2010-20": (YEAR >= 2010) & (YEAR <= 2020), "外2021-26H1": YEAR >= 2021, "近年2024-26H1": YEAR >= 2024}
HOURS = [h for h in range(24) if h != 17]

# ---------- (A)(B) hourly anchors ----------
say("\n## 1. ET h:00 アンカーの残り path（e 平均・D_e = BUY−SELL・日クラスタ t）")
PROF = {}
for wn, wm in W.items():
    say(f"\n### {wn}")
    say("| h | n | 日 | BUY比 | k中央 | e 平均 | t | MDE | D_e | t | MDE | e_raw t |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = {}
    for h in HOURS:
        m = ANC & (B_H == h) & wm[TID]
        i = np.flatnonzero(m)
        if len(i) < 100: say(f"| {h:02d} | {len(i)} | | | | 不足 | | | | | | |"); continue
        t_ = TID[i]; k = JJ[i]; e = RSTAR[t_] - clR[i]; sg = SGN[t_]; d = B_SESS[i]
        me, se, te, G = cmean(e, d); bs, ses, tsg, _ = creg(e, sg, d); De = 2 * bs; seD = 2 * ses
        eraw = R[t_] - clR[i]; mr, ser, tr, _ = cmean(eraw, d)
        rows[h] = dict(n=len(i), G=G, buy=(sg > 0).mean(), k=np.median(k), me=me, se=se, te=te, De=De, seD=seD, tD=De / seD, tr=tr)
        say(f"| {h:02d} | {len(i)} | {G} | {(sg>0).mean():.2f} | {np.median(k):.0f} | {me:+.4f} | {te:+.2f} | {2*se:.3f} | {De:+.4f} | {De/seD:+.2f} | {2*seD:.3f} | {tr:+.2f} |")
    PROF[wn] = rows
    tl = np.array([r["te"] for r in rows.values()]); tD = np.array([r["tD"] for r in rows.values()])
    say(f"- e の t: max|t| {np.max(np.abs(tl)):.2f}（h {list(rows)[int(np.argmax(np.abs(tl)))]:02d}）・sd {tl.std():.2f}（帰無 ≈1）・|t|≥2 {int((np.abs(tl)>=2).sum())}/{len(tl)}（期待 {0.046*len(tl):.1f}）；"
        f" D_e の t: max|t| {np.max(np.abs(tD)):.2f}（h {list(rows)[int(np.argmax(np.abs(tD)))]:02d}）・sd {tD.std():.2f}・|t|≥2 {int((np.abs(tD)>=2).sum())}/{len(tD)}")

# ---------- (B) blocks ----------
say("\n## 2. ブロック対比（H_B）: N = ET 18/19/20 時アンカー vs D = ET 03〜08 時アンカー（本ごとに最初のアンカー）")
def first_anchor(hours_set, wm):
    m = ANC & np.isin(B_H, hours_set) & wm[TID]
    i = np.flatnonzero(m)
    # first per trade: paths are contiguous and increasing in j => first occurrence per TID
    _, first = np.unique(TID[i], return_index=True)
    return i[first]
def block_stats(i, inject=0.0):
    t_ = TID[i]; e = RSTAR[t_] - clR[i] + inject * SGN[t_]; sg = SGN[t_]; d = B_SESS[i]
    bs, ses, tsg, G = creg(e, sg, d); me, se, te, _ = cmean(e, d)
    return dict(n=len(i), G=G, De=2 * bs, seD=2 * ses, tD=bs / ses, me=me, te=te, buy=(sg > 0).mean(),
                k=np.median(JJ[i]), hold=np.median(HOLD[t_]), eh=E_H[t_])
BLK = {}
for wn, wm in W.items():
    iN = first_anchor([18, 19, 20], wm); iD = first_anchor([3, 4, 5, 6, 7, 8], wm); i16 = first_anchor([16], wm)
    bN = block_stats(iN); bD = block_stats(iD); b16 = block_stats(i16)
    C = bN["De"] - bD["De"]; seC = math.sqrt(bN["seD"] ** 2 + bD["seD"] ** 2)
    BLK[wn] = dict(bN=bN, bD=bD, b16=b16, C=C, seC=seC)
    say(f"\n### {wn}")
    for nm, b in (("N 18–20", bN), ("D 03–08", bD), ("対照 16:00", b16)):
        eh = pd.Series(b["eh"]).value_counts().sort_index()
        top = ", ".join(f"ET{h:02d}:{int(c)}" for h, c in eh.sort_values(ascending=False).head(5).items())
        say(f"- {nm}: n{b['n']}（日 {b['G']}）BUY 比 {b['buy']:.2f}・k 中央値 {b['k']:.0f}・hold 中央値 {b['hold']:.0f}・e 平均 {b['me']:+.4f} (t{b['te']:+.2f})・"
            f"**D_e {b['De']:+.4f}R (t{b['tD']:+.2f}, MDE {2*b['seD']:.4f})**・建玉 ET 時刻 上位 [{top}]")
    say(f"- **対比 C = D_e(N) − D_e(D) = {C:+.4f}R (t{C/seC:+.2f}, MDE {2*seC:.4f})**")
    # entry-block fixed subsets (counter (i)): N-block anchors restricted to entries at ET 13-16; D-block anchors restricted to entries ET 18-23
    for nm, i_, hs in (("N・建玉 ET13–16 のみ", iN, range(13, 17)), ("N・建玉 ET18–20 のみ（同ブロック内建玉）", iN, range(18, 21)),
                       ("D・建玉 ET18–23 のみ", iD, range(18, 24)), ("D・建玉 ET00–08 のみ", iD, range(0, 9))):
        sub = i_[np.isin(E_H[TID[i_]], list(hs))]
        if len(sub) >= 60:
            b = block_stats(sub); say(f"  - {nm}: n{b['n']} BUY {b['buy']:.2f} D_e {b['De']:+.4f}R (t{b['tD']:+.2f})")
        else: say(f"  - {nm}: n{len(sub)} 不足")
    if wn == "外2021-26H1":
        bI = block_stats(iN, inject=0.05); say(f"- 注入 +0.05R·SGN（N ブロック）→ D_e {bI['De']:+.4f}R (t{bI['tD']:+.2f})")
        # LOYO -2026
        iN2 = iN[YEAR[TID[iN]] <= 2025]; iD2 = iD[YEAR[TID[iD]] <= 2025]
        b1 = block_stats(iN2); b2 = block_stats(iD2); C2 = b1["De"] - b2["De"]; se2 = math.sqrt(b1["seD"] ** 2 + b2["seD"] ** 2)
        say(f"- LOYO −2026（2021-25）: D_e(N) {b1['De']:+.4f} (t{b1['tD']:+.2f}, n{b1['n']})・D_e(D) {b2['De']:+.4f} (t{b2['tD']:+.2f}, n{b2['n']})・C {C2:+.4f} (t{C2/se2:+.2f})")
        # same-day move control (counter (ii)): regress e on SGN + SGN*r_sofar (session return from 18:00 to anchor)
        for nm, i_ in (("N", iN), ("D", iD)):
            t_ = TID[i_]; d = B_SESS[i_]
            i_now = idx_at(TS[i_]); i_open = idx_at(TS[i_] - 300 * ((B_H[i_] - 18) % 24) * 12 - 300 * (B_MI[i_] // 5))
            ok2 = (i_now >= 0) & (i_open >= 0)
            if ok2.sum() >= 60:
                rso = (lc[i_now[ok2]] - lc[i_open[ok2]]) * 1e4
                e = RSTAR[t_[ok2]] - clR[i_[ok2]]; sg = SGN[t_[ok2]]
                Z = np.column_stack([np.ones(ok2.sum()), sg, sg * rso, rso]); b, se, G = ols_cluster(e, Z, d[ok2])
                say(f"- {nm} ブロック 同セッション既経過リターン統制: D_e(統制後) {2*b[1]:+.4f}R (t{b[1]/se[1]:+.2f})・SGN×r 係数 {b[2]:+.5f}R/bp (t{b[2]/se[2]:+.2f})・n{ok2.sum()}・BUY 側 r 平均 {rso[sg>0].mean():+.1f} bp／SELL 側 {rso[sg<0].mean():+.1f} bp")

# ---------- (C) hazard map ----------
say("\n## 3. 記述: 時刻別 SL/TP 決着ハザード（同セッション足・j≥1・bars-at-risk 正規化）とボラ比")
HB = SAME & (JJ >= 1) & (JJ <= HOLD[TID])  # bars 1..hold within session (bar hold = settlement bar)
SETTLE = (JJ == HOLD[TID]) & HB
for wn, wm in W.items():
    m = HB & wm[TID]
    yrs = (g_yr >= (2010 if wn.startswith("在") else 2021 if wn.startswith("外") else 2024)) & (g_yr <= (2020 if wn.startswith("在") else 2026))
    trading = yrs & (dr != 0) & ~((g_wd == 5) | ((g_wd == 6) & (g_h < 18)) | ((g_wd == 4) & (g_h >= 17)) | ((g_wd <= 3) & (g_h == 17)))
    vol_h = np.array([np.median(np.abs(dr[trading & (g_h == h)])) * 1e4 if (trading & (g_h == h)).sum() > 100 else np.nan for h in range(24)])
    vol_mean = np.nanmean(vol_h)
    say(f"\n### {wn}（bars-at-risk {m.sum()}・決着 {(SETTLE & wm[TID]).sum()}・npz 取引足の時刻別 中央値|Δ| 全日平均 {vol_mean:.2f} bp）")
    say("| h | bars | flat% | SL | TP | TIME | h_SL% | h_TP% | TP share | vol bp | (h_SL+h_TP)/vol |")
    say("|---|---|---|---|---|---|---|---|---|---|---|")
    hz = []
    for h in HOURS:
        mh = m & (B_H == h); nb = mh.sum()
        if nb < 500: say(f"| {h:02d} | {nb} | 不足 | | | | | | | | |"); continue
        st = mh & SETTLE; ex = EXIT[TID[st]]
        nSL = (ex == "SL").sum(); nTP = (ex == "TP").sum(); nTM = (ex == "TIME").sum()
        flat = np.mean(clR[np.flatnonzero(mh)] == clR[np.flatnonzero(mh) - 1])
        hSL = nSL / nb * 100; hTP = nTP / nb * 100; share = nTP / max(nSL + nTP, 1)
        ratio = (hSL + hTP) / (vol_h[h] / vol_mean) if np.isfinite(vol_h[h]) else np.nan
        hz.append((h, hSL + hTP, vol_h[h] / vol_mean, share))
        say(f"| {h:02d} | {nb} | {flat*100:.1f} | {nSL} | {nTP} | {nTM} | {hSL:.2f} | {hTP:.2f} | {share:.2f} | {vol_h[h]:.2f} | {ratio:.2f} |")
    hz = np.array(hz)
    if len(hz) > 5:
        rho = pd.Series(hz[:, 1]).corr(pd.Series(hz[:, 2]), method="spearman")
        say(f"- 時刻別 総ハザード vs ボラ（Spearman）{rho:+.2f}；総ハザード 最大 h {int(hz[np.argmax(hz[:,1]),0]):02d}（{hz[:,1].max():.2f}%/足）・最小 h {int(hz[np.argmin(hz[:,1]),0]):02d}（{hz[:,1].min():.2f}%）；TP share 範囲 {hz[:,3].min():.2f}〜{hz[:,3].max():.2f}")

# ---------- verdict ----------
say("\n## 判定（事前固定・外 2021-26H1）")
if not ALIGN_OK:
    say(f"- 整合性 {fr*100:.1f}% <90% → **inconclusive（path 足番号と暦時刻が整合しない）**")
else:
    o = PROF["外2021-26H1"]; a = PROF["在2010-20"]
    hits = [h for h, r in o.items() if abs(r["te"]) >= 2.99 and h in a and np.sign(a[h]["te"]) == np.sign(r["te"]) and abs(a[h]["te"]) >= 1.5]
    cand = [h for h, r in o.items() if abs(r["te"]) >= 2.99]
    tl = np.array([r["te"] for r in o.values()])
    say(f"- H_A: 外 Bonferroni(23) |t|≥2.99 のセル {cand}・在 同符号 |t|≥1.5 も満たす {hits} → **{'PASS（時計に出口情報あり）' if hits else 'null（時計は出口情報を持たない）'}**・外 t の sd {tl.std():.2f}・MDE 範囲 {min(2*r['se'] for r in o.values()):.3f}〜{max(2*r['se'] for r in o.values()):.3f}R")
    # positive control for H_A: pooled e_raw
    m = ANC & W["外2021-26H1"][TID]; i = np.flatnonzero(m); mr, ser, tr, _ = cmean(R[TID[i]] - clR[i], B_SESS[i])
    me_, se_, te_, _ = cmean(RSTAR[TID[i]] - clR[i], B_SESS[i])
    say(f"  - 陽性対照 外 全アンカー プール: e_raw 平均 {mr:+.4f}R (t{tr:+.2f}・期待 ≈ −ft·P(SL/TP) {-(ft[TID[i]]*ISLT[TID[i]]).mean():+.4f})／公正化 e 平均 {me_:+.4f}R (t{te_:+.2f})")
    B = BLK["外2021-26H1"]; Bn = BLK["近年2024-26H1"]
    tC = B["C"] / B["seC"]; tCn = Bn["C"] / Bn["seC"]
    if B["C"] > 0 and tC >= 2 and B["bN"]["De"] > 0 and B["bN"]["tD"] >= 2 and Bn["C"] > 0 and tCn >= 1.5: vb = "PASS（夜間ドリフト型の時計の形）"
    elif B["C"] < 0 and tC <= -2: vb = "反対の形（夜間ドリフト型ではない）"
    else: vb = f"null（MDE C {2*B['seC']:.4f}R）"
    say(f"- H_B: 外 C {B['C']:+.4f}R (t{tC:+.2f})・D_e(N) {B['bN']['De']:+.4f} (t{B['bN']['tD']:+.2f})・近年 C {Bn['C']:+.4f} (t{tCn:+.2f}) → **{vb}**")
    say(f"  - 陽性対照 16:00 アンカー D_e: 外 {B['b16']['De']:+.4f}R (t{B['b16']['tD']:+.2f}, n{B['b16']['n']})（cycle18 16:50 アンカー +0.369 t4.0）／在 {BLK['在2010-20']['b16']['De']:+.4f} (t{BLK['在2010-20']['b16']['tD']:+.2f})（cycle18 +0.101 t1.4）")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
