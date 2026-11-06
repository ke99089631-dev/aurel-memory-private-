# -*- coding: utf-8 -*-
"""
[cycle18 研究レーン 2026-11-07] 【深化・path】壁→壁(再加速)の本は ET 17:00 日次ブレイクをまたぐとき再開 pop を「受け取る」のか「払う」のか
— cycle16/17・反証 23:35/02:30 で確定した市場構造（2013+ クリーン日の G_5 = ln(18:00足close)−ln(16:50足close) が 外 +1.91 bp t6.0）を、
本番の path（refute_c2_fullpaths.npz）に当てて、戦略の側（BUY/SELL）と生存選択が pop とどう噛み合うかを測る。入口フィルタ提案ではない。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/c8_crossasset_features.csv（19404 本・entry_time 昇順）、data/c1_reaccel_paths_2010_2026.json（FEED_TOL・順序 assert）、
  data/refute_c2_fullpaths.npz（全足 clR・off・規約: 足 j の開始時刻 = entry_time+300·j、index hold = 決着足）、data/macro/XAU_m5_close.npz（bid・格子）。
母集合（横断本 C）: 建玉後最初の ET 16:50 足（アンカー k_b・16:55 の close）が **同じ ET 日**（または建玉 ET 時 ≥18 時で翌暦日）にあり、途中に週末が無く、
  アンカー日が **月〜木・2013 年以降・クリーンなブレイク日**（17:00–17:55 ET の 12 本 flat・c17 と同定義）で、hold > k_b（アンカー足で生存）。
  **整合性検査（⑩⑫）**: path の k_b−6→k_b の価格変化（SGN·ΔclR·risk）と npz 16:20→16:50 足 close の差を突合し、|差| ≤0.02 USD の比率を先に印字。
  <90% なら「path 足番号と暦時刻が整合しない」として判定を全部 inconclusive にし needs cache（時刻索引つき path）を記録する。
量（1 本 = 1 観測・**日クラスタ SE**＝同じ日の横断本は同じ pop を受けるので有効 n は日数）:
  e = R* − cl_{k_b}（残り path・R* = R + ft·1{SL,TP} で記帳を揃える ①）。
  pop_R = SGN·G_5(d)·P(16:50 close)/risk（その日の pop を本の R 単位に換算・BUY 正／SELL 負）。|pop|_R = G_5·P/risk（側非依存）。
窓: 在 2013-20／外 2021-26H1／近年 2024-26H1（建玉年・D2）。判定は外。
統計:
  J1 受取り（機構的に ≈1 が期待・外れたら出口が割り込む）: e ~ 1 + pop_R（日クラスタ）。PASS = 外 b ∈ [0.5, 1.5] ∧ t ≥ 2。
  J2 **選択（主・新規）**: |pop|_R ~ 1 + SGN（日クラスタ）→ c = (BUY 生存本の pop 大きさ − SELL 生存本の pop 大きさ)/2。
     予測（cycle17 D1: 日中下げ日に pop が大きい × 下げ日に生存するのは SELL）: **c < 0**。
     判定: 払う側 = 外 c<0 ∧ t≤−2 ／ 受け取る側 = 外 c>0 ∧ t≥2 ／ それ以外 null（MDE 2·se を bp と R で添える ⑦）。
  J3 記録: 受取り実額 mean(pop_R)（日クラスタ t）と、独立なら mean(SGN)·mean(|pop|_R) の反実仮想、横断本の e 合計に占める割合、
     外の全本 R* 合計に占める割合。D_break = e の BUY−SELL（= 2×SGN 係数）。
プラセボ（陽性対照・⑱）: 同じ日の ET 11:50 足アンカー（c17 の P_5 窓 11:55→13:05 と同一・ブレイク無し）で同じ J1/J2/D を出す。
  J1 の b≈1 は普通の窓でも出る筈（陽性対照）。J2 の c は普通の窓でも「生存選択×同時期の動き」で非 0 になり得る → ブレイク固有かの対照。
副次（記述）: 16:55 足アンカー版（G_0・最終印字込み）、決着足がアンカー直後（k_b+1・k_b+2＝再開足）の本の比率と exit 内訳・側別 R*（ギャップ抜け）、
  年別 n、建玉 ET 時刻帯別の横断率。
look-ahead: アンカー時点の cl_{k_b} と SGN は既知。G_5 は事後（受取りの測定にだけ使う・予測には使わない）。
事前の最重大反証: (i) 日クラスタでも同じ週の pop は相関し得る（週クラスタで感度）。(ii) 横断本は長保有に選択されている（hold>k_b）＝
  母集団が全本と違うので「全本の R への寄与」は横断率で薄まる。(iii) bid のみ（反証 Q2・偏り +0.01 bp）。(iv) 2026-06-30 まで・2026H1 の +8.5 bp
  が外を押し上げる → LOYO 2026 を併記。閉場中の往復コスト 0.42 USD・swap【要取得】は本サイクルでは不変（運用の問いにはしない）。
入力は既存キャッシュのみ・scan 無し・M5 原本読込なし・MT5 無し・外部通信無し。seed 20261107。
"""
import os, json, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c18_break_crossing_result.md")
NY = "America/New_York"
rng = np.random.default_rng(20261107)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle18] ブレイク横断本は再開 pop を受け取るか払うか — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c18_break_crossing.py)")

# ---------- trades ----------
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
N = len(X); ET = X["entry_time"].to_numpy().astype(np.int64)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); YEAR = X["year"].to_numpy()
HOLD = X["hold"].to_numpy().astype(int); RISK = X["risk"].to_numpy(); EXIT = X["exit"].to_numpy()
J = json.load(open(os.path.join(DATA, "c1_reaccel_paths_2010_2026.json"), encoding="utf-8"))
c1_et = np.sort(np.array([t["entry_time"] for t in J["trades"]])); assert np.array_equal(c1_et, ET)
FT = J["frozen"]["FEED_TOL"]; ft = FT / RISK; RSTAR = R + ft * np.isin(EXIT, ["SL", "TP"])
z = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); clR = z["clR"]; off = z["off"].astype(np.int64)
assert len(off) - 1 == N and np.all(np.diff(off) == HOLD + 1)
e_utc = pd.to_datetime(ET, unit="s", utc=True); e_ny = e_utc.tz_convert(NY)
E_H = e_ny.hour.to_numpy(); E_M = e_ny.minute.to_numpy(); E_WD = e_ny.weekday.to_numpy()
say(f"- 本 {N}、entry {e_utc[0].date()}〜{e_utc[-1].date()} UTC（⑩）、npz 規約 OK、FEED_TOL {FT}、exit {dict(pd.Series(EXIT).value_counts())}")

# ---------- XAU grid ----------
zz = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = zz["ts"].astype(np.int64); cl = zz["close"].astype(float); lc = np.log(cl)
r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = r == 0
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert(NY)
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
day = yr * 10000 + t_ny.month.to_numpy() * 100 + t_ny.day.to_numpy()
gap_after = np.where(np.diff(ts) != 300)[0]; valid = np.ones(len(ts), bool); valid[gap_after + 1] = False
say(f"- XAU npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）、flat {flat.mean()*100:.1f}%（⑪）、格子の穴 {len(gap_after)}（⑫・ts 一致参照）")
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)
# clean break days (Mon-Thu, 2013+)
iG = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]; tG = ts[iG]
i1650 = idx_at(tG - 70 * 60); i1655 = idx_at(tG - 65 * 60); i1620 = idx_at(tG - 100 * 60)
BRK = np.column_stack([idx_at(tG - 300 * j) for j in range(1, 13)])
i1150 = idx_at(tG - (6 * 3600 + 10 * 60)); i1300 = idx_at(tG - 5 * 3600); i1120 = idx_at(tG - (6 * 3600 + 40 * 60))
ok = (i1650 >= 0) & (i1655 >= 0) & (i1620 >= 0) & np.all(BRK >= 0, axis=1) & (i1150 >= 0) & (i1300 >= 0) & (i1120 >= 0) & valid[iG] & valid[i1650]
iG, i1650, i1655, i1620, BRK, i1150, i1300, i1120 = iG[ok], i1650[ok], i1655[ok], i1620[ok], BRK[ok], i1150[ok], i1300[ok], i1120[ok]
clean = np.all(flat[BRK], axis=1)
say(f"- ET 18:00 足 候補日（月〜木・2013+）{len(iG)}、クリーン日 {clean.sum()}（{clean.mean()*100:.1f}%）")
iG, i1650, i1655, i1620, i1150, i1300, i1120 = iG[clean], i1650[clean], i1655[clean], i1620[clean], i1150[clean], i1300[clean], i1120[clean]
dG = day[iG]
DAY = pd.DataFrame({"d": dG, "ts1650": ts[i1650], "ts1150": ts[i1150], "G5": lc[iG] - lc[i1650], "G0": lc[iG] - lc[i1655],
                    "P5": lc[i1300] - lc[i1150], "P1650": cl[i1650], "P1150": cl[i1150],
                    "d1620_1650": cl[i1650] - cl[i1620], "d1120_1150": cl[i1150] - cl[i1120]}).set_index("d")
say(f"- G_5 日次（bp）: " + " ｜ ".join(f"{wn} {DAY.G5[(DAY.index//10000>=a)&(DAY.index//10000<=b)].mean()*1e4:+.2f} (n{((DAY.index//10000>=a)&(DAY.index//10000<=b)).sum()})"
    for wn, (a, b) in {"在2013-20": (2013, 2020), "外2021-26H1": (2021, 2026), "近年2024-26H1": (2024, 2026)}.items()) + "  （c17: +1.02／+1.91／+2.85）")

# ---------- anchor day per trade ----------
# same ET date if entry before 16:50 ET; next calendar date if entry hour >= 18; 17:xx impossible/excluded
e_date = e_ny.normalize()
before = (E_H < 16) | ((E_H == 16) & (E_M < 50)); after = E_H >= 18
anc_date = e_date.where(before, e_date + pd.Timedelta(days=1))
anc_day = (anc_date.year * 10000 + anc_date.month * 100 + anc_date.day).to_numpy()
use = (before | after)
# entry weekday: no weekend between entry and anchor -> same-day entries on Mon-Thu, or evening entries Sun-Wed (anchor Mon-Thu)
use &= np.where(before, E_WD <= 3, (E_WD <= 2) | (E_WD == 6))
in_day = np.isin(anc_day, DAY.index.to_numpy())
use &= in_day
dd = DAY.reindex(anc_day)
TS1650 = dd["ts1650"].to_numpy(); TS1150 = dd["ts1150"].to_numpy()
def anchor(TSa):
    kk = np.full(N, -1)
    m = use & np.isfinite(TSa)
    dt = np.where(m, TSa - ET, np.nan)
    good = m & (dt > 0) & (np.mod(dt, 300) == 0)
    kk[good] = (dt[good] // 300).astype(int)
    alive = good & (HOLD > kk) & (kk >= 1)
    return kk, alive
KB, CB = anchor(TS1650); KP, CP = anchor(TS1150)
say(f"- 候補（月〜木クリーン日にアンカー日がある本）{use.sum()}、ブレイク横断本（hold>k_b）**{CB.sum()}**、プラセボ 11:50 生存本 {CP.sum()}")

# ---------- alignment check (⑩⑫) ----------
def align(C, K, dcol):
    m = C & (K >= 6); i = np.flatnonzero(m)
    dpath = SGN[i] * (clR[off[i] + K[i]] - clR[off[i] + K[i] - 6]) * RISK[i]
    dnpz = dd[dcol].to_numpy()[i]
    diff = np.abs(dpath - dnpz)
    return (diff <= 0.02).mean(), np.median(diff), len(i), np.corrcoef(dpath, dnpz)[0, 1]
fr, md, na, cc = align(CB, KB, "d1620_1650")
say(f"- **整合性（ブレイク）**: path k_b−6→k_b vs npz 16:20→16:50 足 close、|差|≤0.02 USD の比率 **{fr*100:.1f}%**（中央値 |差| {md:.4f} USD・ρ {cc:.4f}・n{na}）")
frp, mdp, nap, ccp = align(CP, KP, "d1120_1150")
say(f"- 整合性（プラセボ）: |差|≤0.02 USD **{frp*100:.1f}%**（中央値 {mdp:.4f}・ρ {ccp:.4f}・n{nap}）")
ALIGN_OK = fr >= 0.9

# ---------- stats ----------
W = {"在2013-20": (YEAR >= 2013) & (YEAR <= 2020), "外2021-26H1": YEAR >= 2021, "近年2024-26H1": YEAR >= 2024}
def ols_cluster(y, Z, cl_):
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); G = 0
    for c in np.unique(cl_):
        idx = cl_ == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G += 1
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G
def cmean(y, cl_):
    b, se, G = ols_cluster(y, np.ones((len(y), 1)), cl_); return b[0], se[0], b[0] / se[0] if se[0] > 0 else np.nan, G
def creg(y, x, cl_):
    Z = np.column_stack([np.ones(len(y)), x]); b, se, G = ols_cluster(y, Z, cl_); return b[1], se[1], b[1] / se[1] if se[1] > 0 else np.nan, G

def block(label, C, K, gcol, pcol, is_break):
    say(f"\n## {label}")
    res = {}
    for wn, wm in W.items():
        m = C & wm; i = np.flatnonzero(m)
        if len(i) < 30: say(f"- {wn}: n{len(i)} 不足"); continue
        clk = clR[off[i] + K[i]]; e = RSTAR[i] - clk; sg = SGN[i]; rk = RISK[i]
        G = dd[gcol].to_numpy()[i]; P = dd[pcol].to_numpy()[i]; dday = anc_day[i]
        wk = (pd.to_datetime(dday.astype(str), format="%Y%m%d").isocalendar().year * 100 + pd.to_datetime(dday.astype(str), format="%Y%m%d").isocalendar().week).to_numpy()
        popR = sg * G * P / rk; absR = G * P / rk; pr = P / rk
        nd = len(np.unique(dday)); buy = (sg > 0).mean()
        say(f"- {wn}: n{len(i)}（日 {nd}・週 {len(np.unique(wk))}）BUY 比 {buy:.2f}、mean P/risk {pr.mean():.0f}、1 bp = {pr.mean()*1e-4:.4f}R、日 pop 平均 {G.mean()*1e4:+.2f} bp、"
            f"hold 中央値 {np.median(HOLD[i]):.0f}・k 中央値 {np.median(K[i]):.0f}、exit {dict(pd.Series(EXIT[i]).value_counts())}")
        # J1 receipt
        b1, se1, t1, _ = creg(e, popR, dday)
        # D = BUY-SELL in e
        bs, ses, tsg, _ = creg(e, sg, dday); D = 2 * bs; seD = 2 * ses
        # J2 selection
        c2, se2, t2, _ = creg(absR, sg, dday); c2w, se2w, t2w, _ = creg(absR, sg, wk)
        cbp, sebp, tbp, _ = creg(G * 1e4, sg, dday)
        # J3 received
        m3, se3, t3, _ = cmean(popR, dday); cf = sg.mean() * absR.mean()
        me, see, te_, _ = cmean(e, dday)
        tot_e = e.sum(); tot_pop = popR.sum(); tot_R_win = RSTAR[wm].sum()
        say(f"  - J1 受取り b(e on pop_R) **{b1:+.3f} (t{t1:+.2f})**、D_e(BUY−SELL) {D:+.4f}R (t{D/seD:+.2f})、e 平均 {me:+.4f}R (t{te_:+.2f})")
        say(f"  - J2 選択 c=(|pop|_R BUY−SELL)/2 **{c2:+.4f}R (t{t2:+.2f}, MDE {2*se2:.4f}R)**・週クラスタ t{t2w:+.2f}・bp 単位 {cbp:+.3f} bp (t{tbp:+.2f}, MDE {2*sebp:.3f} bp)")
        say(f"  - J3 受取り実額 mean(pop_R) **{m3:+.4f}R (t{t3:+.2f})** vs 独立反実仮想 mean(SGN)·mean(|pop|_R) {cf:+.4f}R（差 {m3-cf:+.4f}R）、"
            f"受取り合計 {tot_pop:+.1f}R／横断本 e 合計 {tot_e:+.1f}R／窓の全本 R* 合計 {tot_R_win:+.1f}R（比 {tot_pop/tot_R_win*100 if tot_R_win else float('nan'):+.1f}%）")
        if is_break:
            # exits right after anchor
            nx1 = (HOLD[i] == K[i] + 1); nx2 = (HOLD[i] == K[i] + 2)
            for nm, mm in (("k_b+1（16:55 足）", nx1), ("k_b+2（18:00 再開足）", nx2)):
                if mm.sum() >= 5:
                    say(f"  - 決着 {nm}: {mm.sum()} 本（{mm.mean()*100:.1f}%）exit {dict(pd.Series(EXIT[i][mm]).value_counts())}、R* BUY {RSTAR[i][mm & (sg>0)].mean() if (mm&(sg>0)).sum() else float('nan'):+.3f} (n{(mm&(sg>0)).sum()}) / SELL {RSTAR[i][mm & (sg<0)].mean() if (mm&(sg<0)).sum() else float('nan'):+.3f} (n{(mm&(sg<0)).sum()})")
                else: say(f"  - 決着 {nm}: {mm.sum()} 本")
            # by-side pop size and same-day move (why selection): mean G5 for BUY-alive vs SELL-alive days
            say(f"  - 側別 日 pop（bp）: BUY 生存 {G[sg>0].mean()*1e4:+.2f} (n{(sg>0).sum()}) / SELL 生存 {G[sg<0].mean()*1e4:+.2f} (n{(sg<0).sum()})、側別 cl_k: BUY {clk[sg>0].mean():+.3f} / SELL {clk[sg<0].mean():+.3f}")
        res[wn] = dict(b1=b1, t1=t1, c2=c2, t2=t2, se2=se2, m3=m3, t3=t3, D=D, seD=seD, n=len(i))
    return res

RB = block("ブレイク横断（アンカー 16:50 足・G_5）", CB, KB, "G5", "P1650", True)
RP = block("プラセボ（アンカー 11:50 足・P_5 11:55→13:05）", CP, KP, "P5", "P1150", False)
# 16:55 anchor robustness (k_b+1, G0)
KB1 = np.where(KB >= 0, KB + 1, -1); CB1 = CB & (HOLD > KB1)
RB1 = block("頑健性: アンカー 16:55 足（k_b+1・G_0・最終印字込み）", CB1, KB1, "G0", "P1650", False)

# ---------- DiD and LOYO ----------
say("\n## DiD（ブレイク − プラセボ）と LOYO 2026（外）")
for wn in W:
    if wn in RB and wn in RP:
        dD = RB[wn]["D"] - RP[wn]["D"]; seDD = math.sqrt(RB[wn]["seD"] ** 2 + RP[wn]["seD"] ** 2)
        dc = RB[wn]["c2"] - RP[wn]["c2"]; sec = math.sqrt(RB[wn]["se2"] ** 2 + RP[wn]["se2"] ** 2)
        say(f"- {wn}: D_e 差 {dD:+.4f}R (t{dD/seDD:+.2f})、選択 c 差 {dc:+.4f}R (t{dc/sec:+.2f})")
m = CB & (YEAR >= 2021) & (YEAR <= 2025); i = np.flatnonzero(m)
if len(i) >= 30:
    clk = clR[off[i] + KB[i]]; e = RSTAR[i] - clk; sg = SGN[i]; G = dd["G5"].to_numpy()[i]; P = dd["P1650"].to_numpy()[i]; rk = RISK[i]; dday = anc_day[i]
    c2, se2, t2, _ = creg(G * P / rk, sg, dday); m3, se3, t3, _ = cmean(sg * G * P / rk, dday); b1, se1, t1, _ = creg(e, sg * G * P / rk, dday)
    say(f"- 外 LOYO −2026（2021-25・n{len(i)}）: J1 b {b1:+.3f} (t{t1:+.2f})、J2 c {c2:+.4f}R (t{t2:+.2f})、J3 受取り {m3:+.4f}R (t{t3:+.2f})")
# yearly
say("\n## 年別（横断本 n・BUY 比・日 pop bp・受取り R・選択 c）")
for y_ in range(2013, 2027):
    i = np.flatnonzero(CB & (YEAR == y_))
    if len(i) < 10: say(f"- {y_}: n{len(i)}"); continue
    sg = SGN[i]; G = dd["G5"].to_numpy()[i]; P = dd["P1650"].to_numpy()[i]; rk = RISK[i]; dday = anc_day[i]
    c2, se2, t2, _ = creg(G * P / rk, sg, dday); m3, se3, t3, _ = cmean(sg * G * P / rk, dday)
    say(f"- {y_}: n{len(i)} BUY {(sg>0).mean():.2f} pop {G.mean()*1e4:+.2f} bp 受取り {m3:+.4f}R (t{t3:+.1f}) c {c2:+.4f}R (t{t2:+.1f})")
# crossing rate by entry ET hour (外)
say("\n## 建玉 ET 時刻帯別の横断率（外・候補本のうち hold>k_b）")
m = use & (YEAR >= 2021) & np.isfinite(TS1650) & (TS1650 > ET)
for hh in range(0, 24):
    mm = m & (E_H == hh)
    if mm.sum() >= 50: say(f"- ET {hh:02d} 時: 候補 {mm.sum()}、横断 {(mm & CB).sum()}（{(mm & CB).sum()/mm.sum()*100:.1f}%）、k_b 中央値 {np.median(KB[mm & CB]) if (mm&CB).sum() else float('nan'):.0f}")

# ---------- verdict ----------
say("\n## 判定（事前固定・外 2021-26H1）")
if not ALIGN_OK:
    say(f"- 整合性 {fr*100:.1f}% <90% → **inconclusive（path 足番号と暦時刻が整合しない・needs cache: 時刻索引つき path）**")
else:
    o = RB["外2021-26H1"]; p = RP["外2021-26H1"]
    j1 = "PASS（受け取る）" if (0.5 <= o["b1"] <= 1.5 and o["t1"] >= 2) else "FAIL（出口が割り込む／受け取らない）"
    if o["c2"] < 0 and o["t2"] <= -2: j2 = "払う側（SELL が大 pop 日に生存）"
    elif o["c2"] > 0 and o["t2"] >= 2: j2 = "受け取る側（BUY が大 pop 日に生存）"
    else: j2 = f"null（選択なし・MDE {2*o['se2']:.4f}R）"
    say(f"- J1 b {o['b1']:+.3f} (t{o['t1']:+.2f}) → **{j1}**（プラセボ b {p['b1']:+.3f} t{p['t1']:+.2f}）")
    say(f"- J2 c {o['c2']:+.4f}R (t{o['t2']:+.2f}) → **{j2}**（プラセボ c {p['c2']:+.4f} t{p['t2']:+.2f}）")
    say(f"- J3 受取り実額 {o['m3']:+.4f}R/横断本 (t{o['t3']:+.2f})、D_e {o['D']:+.4f}R (t{o['D']/o['seD']:+.2f}) vs プラセボ D_e {p['D']:+.4f}R")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
