# -*- coding: utf-8 -*-
"""
[REFUTE c17] 2026-11-07 — 対象: cycle17 (00:50) の判定 S「ET 18:00 再開 pop G_5 はトレンド独立の構造」と、その読み
  C1 down 相場でも G_5>0（在 +1.52 t4.8／外 +2.02 t5.4）
  C2 down 側でむしろ大きい（T2 在 −0.96 t−2.2／T1 在 −1.26 t−2.9／D1 外 −1.27 t−2.0）
  C3 昼 70 分プラセボ P_5 は「シェア型」（外 down −2.72 t−3.1・β +0.68 t5.1）、再開窓は違う＝陽性対照
  C4 G_5/sd20 ≈ 0.016〜0.020 で一定 ＝ ボラ比例・ドリフト非依存 → 「ブレイク跨ぎ保有のリスク・プレミアム」と整合
  C5 up 日でも正（外 +1.29 t3.3）＝純粋な戻しではない

=== 事前固定（数字を見る前に書く）===
データ: data/macro/XAU_m5_close.npz（bid M5）のみ。母集合・G_5・T2(r20)・T1(月)・D1(r_day)・P_5・窓(在2013-20／外2021-26H1／近年2024-26H1) は
cycle17 と同一定義（クリーン日＝月〜木 ET 18:00 足で 17:00–17:55 の 12 本 flat・2013+）。時刻 c の価格 = ラベル c−5 の足の close。
攻撃（各々の破壊条件）:
 A1 判定規則 S の識別力: T2 ラベルを日付順に循環シフト（k∈[30,n−30]・全 k）して S の合格率を測る。
     → 合格率 ≥95% なら「S は『G_5>0』の言い換えで、トレンド独立性を検定していない」（S の“検定結果”としての意味を破壊）。
     併せて 在 T2 up−down 差（−0.96）と 在 T1 差（−1.26）のシフト帰無分布 p 値。p≥0.05 なら C2（ex-ante）破壊。
 A2 戻し分解: G_5 = α + β1·r(16:25→16:55) + β2·r(15:55→16:25) + β3·r(09:30→15:55) + β4·r(前日18:05→09:30) （HC1 se）。
     → 統制後の down−up 差が 生の差の 50% 未満に縮むなら C2 は戻し成分。α(外) が t<2 または α<1.0 bp なら「構造」破壊。
     純戻しモデル（α=0, 推定 β）の予測 G_5 が down 日平均で t≥2 なら、S は純戻しでも合格＝識別不能。
 A3 与え返し: F = ln bid(翌日16:55) − ln bid(18:05) を G_5 に回帰（窓別）。18:30 アンカー版（G_5' = 16:55→18:30, F' = 18:30→翌16:55）も。
     → 両窓で β ≤ −0.5 (t≤−2) なら「pop は timing（市場が与え返す）」＝premium 読み破壊。β≈0 なら生存。
 A4 288 窓掃引（陽性対照の妥当性）: 同じ日の全 70 分窓（5 分刻み・ブレイク跨ぎ窓除く）で T2 up−down 差の t を 在/外 で計算。
     → 11:55 窓の |t| 順位が 在・外とも上位 10% なら「陽性対照は事後選択」。全窓の |t| 中央値 <1 なら「シェア型は一般的でない」＝C3 の対照としての価値 低。
 A5 頑健性（S の事実 C1）: 外 down セル LOYO（2021〜2026 各 1 年除去）で t<1.5 が 1 つでも出れば C1(外) 破壊。2026H1 除去・曜日別・DST 別・外半分割
     （2021-23／2024-26H1）・中央値・符号検定・1% winsor を記述。
 A6 C4 の識別力: dip(16:55 足)/sd20・r_pre30/sd20・|P_5|/sd20 も窓で一定か。一定なら「ボラ比例」は premium と戻しを区別しない（C4 破壊）。
判定: C1 事実＝A5 で判定。S の“解釈”（トレンド独立の構造／premium）＝A1〜A4,A6 のうち 2 つ以上が破壊条件を満たせば broken、0 なら survived、1 なら inconclusive。
コスト倍: 外 down セルの net（往復 0.42/0.84 USD・swap 0/2 bp）を 1 行（受け取れない結論の再確認）。seed 20261107。
読取のみ・MT5 無し・外部通信無し・scan 無し。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c17_structure.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c17] 再開 pop「トレンド独立の構造」を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c17_structure.py)")

W = {"在2013-20": (2013, 2020), "外2021-26H1": (2021, 2026), "近年2024-26H1": (2024, 2026)}
def ms(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 2: return (np.nan, np.nan, np.nan, n)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return (m, se, m / se if se > 0 else np.nan, n)
def fmt(x, extra=False):
    m, se, t, n = ms(x); s = f"{m:+.2f} (t{t:+.1f}, n{n})"
    if extra and n > 1:
        xx = np.asarray(x, float); xx = xx[np.isfinite(xx)]
        s += f", 中央値 {np.median(xx):+.2f}, 正 {(xx>0).mean()*100:.0f}%"
    return s
def diff_t(a, b):
    ma, sa, _, na = ms(a); mb, sb, _, nb = ms(b)
    if na < 2 or nb < 2: return (np.nan, np.nan)
    se = math.sqrt(sa**2 + sb**2); return (ma - mb, (ma - mb) / se)
def ols_hc1(y, X):
    X = np.column_stack([np.ones(len(y)), X]); XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y; e = y - X @ b; n, k = X.shape
    V = XtX_inv @ (X.T * (e**2)) @ X @ XtX_inv * n / (n - k)
    return b, np.sqrt(np.diag(V)), e
def sign_p(x):
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x != 0)]; n = len(x); k = int((x > 0).sum())
    # two-sided exact binomial via normal approx with continuity (n large)
    z = (abs(k - n / 2) - 0.5) / math.sqrt(n / 4); return 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))

# ---------- load (cycle17 と同一) ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); r_bp = r * 1e4; flat = r == 0
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert("America/New_York")
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
day = yr * 10000 + t_ny.month.to_numpy() * 100 + t_ny.day.to_numpy(); mon = day // 100
off_s = ts - (t_ny.tz_localize(None).astype("int64").to_numpy() // 10**9); summer_all = off_s == -4 * 3600
dts = np.diff(ts); gap_after = np.where(dts != 300)[0]
valid = np.ones(len(ts), bool); valid[gap_after + 1] = False
r_bp_v = np.where(valid, r_bp, np.nan)
say(f"- XAU npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC、flat {flat.mean()*100:.1f}%、格子の穴 {len(gap_after)}（ts 一致参照）")
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)
def price_at(iGref, off_min):
    """price at clock (18:00 + off_min) of gap day = close of bar labelled (clock − 5) → ts = tG + (off_min − 5)*60 ... bar label L closes at L+5.
    price at clock c ⇔ bar labelled c−5 ⇔ ts_bar = tG + (c−18:00) − 5min. Caller passes off_min = c − 18:00 in minutes."""
    j = idx_at(ts[iGref] + (off_min - 5) * 60); ok = j >= 0
    out = np.full(len(iGref), np.nan); out[ok] = lc[j[ok]]; return out

iG = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]; tG = ts[iG]
i1650 = idx_at(tG - 70 * 60); i1655 = idx_at(tG - 65 * 60)
BRK = np.column_stack([idx_at(tG - 300 * j) for j in range(1, 13)])
i1150 = idx_at(tG - (6 * 3600 + 10 * 60)); i1300 = idx_at(tG - 5 * 3600)
iPrev = idx_at(tG - 86400)
ok = (i1650 >= 0) & (i1655 >= 0) & np.all(BRK >= 0, axis=1) & (i1150 >= 0) & (i1300 >= 0) & valid[iG] & valid[i1650]
iG, i1650, i1655, BRK, i1150, i1300, iPrev = iG[ok], i1650[ok], i1655[ok], BRK[ok], i1150[ok], i1300[ok], iPrev[ok]
clean = np.all(flat[BRK], axis=1)
iG, i1650, i1655, i1150, i1300, iPrev = iG[clean], i1650[clean], i1655[clean], i1150[clean], i1300[clean], iPrev[clean]
yG = yr[iG]; dG = day[iG]; mG = mon[iG]; wdG = wd[iG]; n = len(iG)
# DST: pandas 3 は unit='s' の DatetimeIndex を秒解像度で持つため astype('int64')//1e9 は 0 になる（refute_c16_b (1) の夏/冬行はこのバグで全日が冬扱い）。gap 日だけ utcoffset で判定。
sumG = np.array([x.utcoffset().total_seconds() == -4 * 3600 for x in t_ny[iG]])
say(f"- DST 判定: 夏 {sumG.sum()}・冬 {(~sumG).sum()} 日（旧 off_s 法では夏 {summer_all[iG].sum()} 日＝バグ）")
G5 = (lc[iG] - lc[i1650]) * 1e4; G0 = (lc[iG] - lc[i1655]) * 1e4; P5 = (lc[i1300] - lc[i1150]) * 1e4
DIP = (lc[i1655] - lc[i1650]) * 1e4  # 16:55 足（最終印字）
prev_ok = (iPrev >= 0) & (h[np.clip(iPrev, 0, len(h) - 1)] == 18)
p_prev = np.where(prev_ok, lc[np.clip(iPrev, 0, len(lc) - 1)], np.nan)
p1655 = lc[i1650]; p1625 = price_at(iG, -95); p1555 = price_at(iG, -125); p0930 = price_at(iG, -510)
p1830 = price_at(iG, 30); p1900 = price_at(iG, 60)
# next day 16:55 (next calendar day; Mon-Thu gap → Tue-Fri)
tG = ts[iG]; jN = idx_at(tG + 86400 - 70 * 60); pN = np.where(jN >= 0, lc[np.clip(jN, 0, len(lc) - 1)], np.nan)
r_pre30 = (p1655 - p1625) * 1e4; r_pre60 = (p1625 - p1555) * 1e4; r_sess = (p1555 - p0930) * 1e4; r_on = (p0930 - p_prev) * 1e4
r_day = (p1655 - p_prev) * 1e4
F = (pN - lc[iG]) * 1e4; G5_30 = (p1830 - p1655) * 1e4; F30 = (pN - p1830) * 1e4; POST30 = (p1830 - lc[iG]) * 1e4
say(f"- クリーン日 n{n}（cycle17: 2400）。G_5 全体: " + " ｜ ".join(f"{wn} {fmt(G5[(yG>=a)&(yG<=b)])}" for wn, (a, b) in W.items()))
assert n == 2400, n

# ---------- daily series for T2/T1/sd20 (cycle17 と同一) ----------
iD = np.where((wd <= 4) & (h == 16) & (mi == 50))[0]; iD = iD[valid[iD]]; dD = day[iD]; lcD = lc[iD]
gapbar = ((h == 16) & (mi == 55)) | ((h == 18) & (mi == 0))
df = pd.DataFrame({"d": day, "r": r_bp_v, "rg": np.where(gapbar, 0.0, r_bp_v), "wd": wd}); df = df[df["wd"] <= 4]
dsum = df.groupby("d").agg(tot=("r", "sum"), gapless=("rg", "sum")).reindex(dD)
tot = dsum["tot"].to_numpy(); gapless = dsum["gapless"].to_numpy()
pos = np.searchsorted(dD, dG); assert np.all(dD[np.clip(pos, 0, len(dD) - 1)] == dG)
r20 = np.full(n, np.nan); sd20 = np.full(n, np.nan)
for k in np.where(pos >= 20)[0]:
    p = pos[k]; r20[k] = (lcD[p] - lcD[p - 20]) * 1e4; sd20[k] = np.nanstd(tot[p - 20:p], ddof=1)
mret = pd.Series(gapless, index=dD).groupby(dD // 100).sum().reindex(mG).to_numpy()
down = r20 <= 0; up = r20 > 0
def win(wn): a, b = W[wn]; return (yG >= a) & (yG <= b)

# ---------- A1: S の識別力（T2 ラベル循環シフト） ----------
say("\n## A1 判定規則 S の識別力: T2 ラベル（r20 符号）を日付順に循環シフトして S 合格率と up−down 差の帰無分布")
order = np.argsort(dG); r20_o = r20[order]; mret_o = mret[order]; G5_o = G5[order]; P5_o = P5[order]; yG_o = yG[order]
inW = (yG_o >= 2013) & (yG_o <= 2020); outW = (yG_o >= 2021)
def S_rule(lbl):
    d_in = inW & (lbl <= 0); d_out = outW & (lbl <= 0)
    a = ms(G5_o[d_in]); b = ms(G5_o[d_out]); c = ms(P5_o[d_out])
    return (a[2] >= 2) and (a[0] > 0) and (b[2] >= 1.5) and (b[0] > 0) and (c[2] < 2)
obs_S = S_rule(r20_o); obs_in_T2 = diff_t(G5_o[inW & (r20_o > 0)], G5_o[inW & (r20_o <= 0)])
obs_in_T1 = diff_t(G5_o[inW & (mret_o > 0)], G5_o[inW & (mret_o <= 0)])
obs_out_T1 = diff_t(G5_o[outW & (mret_o > 0)], G5_o[outW & (mret_o <= 0)])
obs_P5_out = diff_t(P5_o[outW & (r20_o > 0)], P5_o[outW & (r20_o <= 0)])
ks = np.arange(30, n - 30); passS = 0; dT2 = []; dT1 = []; dT1o = []; dP5 = []
for k in ks:
    lbl = np.roll(r20_o, k); lblm = np.roll(mret_o, k)
    passS += S_rule(lbl)
    dT2.append(diff_t(G5_o[inW & (lbl > 0)], G5_o[inW & (lbl <= 0)])[0])
    dT1.append(diff_t(G5_o[inW & (lblm > 0)], G5_o[inW & (lblm <= 0)])[0])
    dT1o.append(diff_t(G5_o[outW & (lblm > 0)], G5_o[outW & (lblm <= 0)])[0])
    dP5.append(diff_t(P5_o[outW & (lbl > 0)], P5_o[outW & (lbl <= 0)])[0])
dT2 = np.array(dT2); dT1 = np.array(dT1); dT1o = np.array(dT1o); dP5 = np.array(dP5)
pass_rate = passS / len(ks)
p_T2 = (np.abs(dT2) >= abs(obs_in_T2[0])).mean(); p_T1 = (np.abs(dT1) >= abs(obs_in_T1[0])).mean(); p_T1o = (np.abs(dT1o) >= abs(obs_out_T1[0])).mean()
p_P5 = (np.abs(dP5) >= abs(obs_P5_out[0])).mean()
say(f"- 観測 S = {obs_S}。循環シフト {len(ks)} 通りの S 合格率 **{pass_rate*100:.1f}%**（≥95% なら S はトレンド独立性を検定していない）")
say(f"- 在 T2 up−down 差 観測 {obs_in_T2[0]:+.2f} (t{obs_in_T2[1]:+.1f}) → シフト帰無 両側 p **{p_T2:.3f}**（帰無 sd {dT2.std():.2f}）")
say(f"- 在 T1（月符号）差 観測 {obs_in_T1[0]:+.2f} (t{obs_in_T1[1]:+.1f}) → p **{p_T1:.3f}**；外 T1 差 観測 {obs_out_T1[0]:+.2f} (t{obs_out_T1[1]:+.1f}) → p {p_T1o:.3f}")
say(f"- 外 P_5 up−down 差 観測 {obs_P5_out[0]:+.2f} (t{obs_P5_out[1]:+.1f}) → p **{p_P5:.3f}**（陽性対照のシフト帰無）")
# multiple testing on C2 cells (4 regime defs × 3 windows = 12 diff tests)
say("- C2 の多重検定: up−down 差の t（T2/T2b/T1/D1 × 3 窓 = 12 セル・cycle17 記載値）は |t| max 2.9（T1 在）。Bonferroni 12 セル 5% の閾値 |t|≥2.64 → T1 在のみ通過・ex-ante の T2 は在 −2.2 で不通過・外 −0.3")

# ---------- A2: 戻し分解 ----------
say("\n## A2 戻し分解: G_5 = α + β·[r 16:25→16:55, 15:55→16:25, 09:30→15:55, 前日18:05→09:30]（HC1）")
A2_break = []
for wn in W:
    w = win(wn) & np.isfinite(r_pre30) & np.isfinite(r_pre60) & np.isfinite(r_sess) & np.isfinite(r_on) & np.isfinite(r20)
    X = np.column_stack([r_pre30[w], r_pre60[w], r_sess[w], r_on[w]]); y = G5[w]
    b, se, e = ols_hc1(y, X); names = ["α", "β_pre30", "β_pre60-30", "β_sess", "β_on"]
    say(f"- {wn} n{w.sum()}: " + "・".join(f"{nm} {bb:+.3f} (t{bb/s:+.1f})" for nm, bb, s in zip(names, b, se)) + f"；R² {1 - e.var()/y.var():.3f}")
    # regressor means by regime
    dn = down[w]; upw = up[w]
    say(f"    回帰子平均 down/up: pre30 {r_pre30[w][dn].mean():+.2f}/{r_pre30[w][upw].mean():+.2f}・pre60-30 {r_pre60[w][dn].mean():+.2f}/{r_pre60[w][upw].mean():+.2f}・sess {r_sess[w][dn].mean():+.2f}/{r_sess[w][upw].mean():+.2f}・on {r_on[w][dn].mean():+.2f}/{r_on[w][upw].mean():+.2f} bp")
    raw_d, raw_t = diff_t(y[upw], y[dn]); adj = b[0] + e; adj_d, adj_t = diff_t(adj[upw], adj[dn])
    fitted_rev = X @ b[1:]  # 純戻し（α=0）モデルの予測
    rev_dn = ms(fitted_rev[dn]); rev_up = ms(fitted_rev[upw])
    say(f"    up−down 差: 生 {raw_d:+.2f} (t{raw_t:+.1f}) → 統制後 {adj_d:+.2f} (t{adj_t:+.1f})（残存 {adj_d/raw_d*100 if raw_d!=0 else np.nan:.0f}%）；"
        f"純戻しモデル予測 G_5 down 日 {rev_dn[0]:+.2f} (t{rev_dn[2]:+.1f})・up 日 {rev_up[0]:+.2f}；α+残差 down {fmt(adj[dn])}・up {fmt(adj[upw])}")
    # with down dummy
    b2, se2, _ = ols_hc1(y, np.column_stack([dn.astype(float), X]))
    say(f"    down ダミー係数（統制あり） {b2[1]:+.2f} (t{b2[1]/se2[1]:+.1f})；統制なし {raw_d*-1:+.2f}")
    if wn == "在2013-20": A2_break.append(abs(adj_d) < 0.5 * abs(raw_d))
    if wn == "外2021-26H1": A2_break.append((b[0] / se[0] < 2) or (b[0] < 1.0)); alpha_out = (b[0], b[0] / se[0])
# D1 同日符号も統制後に消えるか（cycle17 の D1 外 −1.27 t−2.0）
for wn in ("在2013-20", "外2021-26H1"):
    w = win(wn) & np.isfinite(r_day) & np.isfinite(r_pre30) & np.isfinite(r_pre60) & np.isfinite(r_sess) & np.isfinite(r_on)
    X = np.column_stack([r_pre30[w], r_pre60[w], r_sess[w], r_on[w]]); y = G5[w]; b, se, e = ols_hc1(y, X); adj = b[0] + e
    dd = r_day[w] <= 0; raw = diff_t(y[~dd], y[dd]); ad = diff_t(adj[~dd], adj[dd])
    say(f"- D1 同日符号 {wn}: 生 up−down {raw[0]:+.2f} (t{raw[1]:+.1f}) → 統制後 {ad[0]:+.2f} (t{ad[1]:+.1f})")

# ---------- A3: 与え返し ----------
say("\n## A3 与え返し: 翌日 16:55 までのリターン F を G_5 に回帰（bid の最初の印字ノイズは β を負に偏らせるので 18:30 アンカー版も）")
A3_hits = 0
for wn in W:
    w = win(wn) & np.isfinite(F) & np.isfinite(F30) & np.isfinite(G5_30)
    b, se, _ = ols_hc1(F[w], G5[w][:, None]); b3, se3, _ = ols_hc1(F30[w], G5_30[w][:, None])
    say(f"- {wn} n{w.sum()}: F(18:05→翌16:55) {fmt(F[w])} bp；β(F on G_5) **{b[1]:+.3f} (t{b[1]/se[1]:+.1f})**・切片 {b[0]:+.2f}；"
        f"18:30 版: G_5' {fmt(G5_30[w])}・18:05→18:30 {fmt(POST30[w])}・β(F' on G_5') **{b3[1]:+.3f} (t{b3[1]/se3[1]:+.1f})**")
    # by regime: F on down days vs up days; and G_5 tercile → F
    q = np.quantile(G5[w], [1/3, 2/3]); g = G5[w]; f = F[w]
    say(f"    G_5 三分位→F: 下 {fmt(f[g<=q[0]])} / 中 {fmt(f[(g>q[0])&(g<=q[1])])} / 上 {fmt(f[g>q[1]])}；F down 日 {fmt(f[down[w]])}・up 日 {fmt(f[up[w]])}")
    if wn in ("在2013-20", "外2021-26H1") and (b[1] <= -0.5) and (b[1]/se[1] <= -2) and (b3[1] <= -0.5) and (b3[1]/se3[1] <= -2): A3_hits += 1
# A3b: 検出力と短い地平（与え返しが早いなら短い地平で見える）・2013-26 プール
p2200 = price_at(iG, 240); pN0930 = price_at(iG, 24 * 60 - 510)
allw = np.isfinite(F) & np.isfinite(p2200) & np.isfinite(pN0930)
for lab, fut in (("18:05→18:30", POST30), ("18:05→19:00", (p1900 - lc[iG]) * 1e4), ("18:05→22:00", (p2200 - lc[iG]) * 1e4),
                 ("18:05→翌09:30", (pN0930 - lc[iG]) * 1e4), ("18:05→翌16:55", F)):
    w = allw & np.isfinite(fut); b, se, _ = ols_hc1(fut[w], G5[w][:, None])
    say(f"- プール 2013-26 {lab} n{w.sum()}: 平均 {fmt(fut[w])} bp・β on G_5 **{b[1]:+.3f} (t{b[1]/se[1]:+.1f}, se {se[1]:.2f})**・切片 {b[0]:+.2f}")
q = np.quantile(G5[allw], [1/3, 2/3]); g = G5[allw]; f = F[allw]
dq, tq = diff_t(f[g > q[1]], f[g <= q[0]])
say(f"- プール 翌16:55 F の G_5 上三分位−下三分位: {dq:+.2f} bp (t{tq:+.1f})；G_5 の上−下三分位平均差 {g[g>q[1]].mean()-g[g<=q[0]].mean():+.2f} bp → 含意 β {dq/(g[g>q[1]].mean()-g[g<=q[0]].mean()):+.2f}")
say(f"- 検出力: β=−1（全部与え返し）を t=2 で退けるには se≤0.5 が要る。現 se から必要 n ≈ {int((se[1]/0.5)**2 * allw.sum())} 日（現 {allw.sum()}）")
# does the pop persist to 18:30 / 19:00 by regime (transient first print?)
for wn in W:
    w = win(wn)
    say(f"- {wn} down 日: G_5(→18:05) {fmt(G5[w&down])}・→18:30 {fmt(G5_30[w&down])}・→19:00 {fmt(((p1900-p1655)*1e4)[w&down])}；up 日: →18:05 {fmt(G5[w&up])}・→18:30 {fmt(G5_30[w&up])}・→19:00 {fmt(((p1900-p1655)*1e4)[w&up])}")

# ---------- A4: 288 窓掃引 ----------
say("\n## A4 288 窓掃引: 同じ日の全 70 分窓（開始 5 分刻み・ET 00:00〜22:50 開始・16:55〜18:05 を跨ぐ窓は除く）で T2 up−down 差の t")
rows = []
for s in range(0, 288 - 14 + 1):
    start_min = 5 * s - 1080  # minutes relative to 18:00 ET
    end_min = start_min + 70
    # exclude windows overlapping the break stretch (16:55..18:05) = [-65, +5]
    if not (end_min <= -65 or start_min >= 5): continue
    pa = price_at(iG, start_min); pb = price_at(iG, end_min); x = (pb - pa) * 1e4
    rec = {"slot": s, "clock": f"{(5*s)//60:02d}:{(5*s)%60:02d}"}
    for wn in ("在2013-20", "外2021-26H1"):
        w = win(wn) & np.isfinite(x) & np.isfinite(r20)
        d, t = diff_t(x[w & up], x[w & down]); rec[wn + "_d"] = d; rec[wn + "_t"] = t
        rec[wn + "_down"] = ms(x[w & down])[0]; rec[wn + "_down_t"] = ms(x[w & down])[2]
    rows.append(rec)
SW = pd.DataFrame(rows)
for wn in ("在2013-20", "外2021-26H1"):
    tt = SW[wn + "_t"].to_numpy(); at = np.abs(tt)
    i1155 = SW.index[SW.clock == "11:55"][0]
    rank_1155 = int((at > at[i1155]).sum()) + 1
    share_sign = ((SW[wn + "_d"] > 0)).mean()
    say(f"- {wn}: 窓 {len(SW)}・up−down 差 t の中央値 {np.median(tt):+.2f}・|t| 中央値 {np.median(at):.2f}・|t|≥2 の窓 {(at>=2).mean()*100:.0f}%・差>0（シェア型の向き）の窓 {share_sign*100:.0f}%；"
        f"11:55 窓 t {tt[i1155]:+.2f} 順位 **{rank_1155}/{len(SW)}**（上位 {rank_1155/len(SW)*100:.0f}%）")
    top = SW.iloc[np.argsort(-at)[:5]]
    say(f"    |t| 上位 5 窓: " + ", ".join(f"{c} {t:+.1f}" for c, t in zip(top.clock, top[wn + "_t"])))
    # down-day mean across windows: where does the reopen G_5 stand? (G_5 itself is excluded; report separately)
    dn_m = SW[wn + "_down"].to_numpy(); g5d = ms(G5[win(wn) & down])[0]
    say(f"    down 日の窓平均: 中央値 {np.median(dn_m):+.2f} bp・最大 {dn_m.max():+.2f}（{SW.clock[np.argmax(dn_m)]}）・G_5 down {g5d:+.2f} は全窓より {'大' if g5d > dn_m.max() else '小'}；down 日で t≥2 正の窓 {(SW[wn+'_down_t']>=2).sum()} 個")
A4_break = False
r_in = int((np.abs(SW["在2013-20_t"]) > abs(SW.loc[SW.clock == "11:55", "在2013-20_t"].iloc[0])).sum()) + 1
r_out = int((np.abs(SW["外2021-26H1_t"]) > abs(SW.loc[SW.clock == "11:55", "外2021-26H1_t"].iloc[0])).sum()) + 1
A4_cherry = (r_in <= 0.1 * len(SW)) and (r_out <= 0.1 * len(SW))
A4_notgeneric = (np.median(np.abs(SW["在2013-20_t"])) < 1) and (np.median(np.abs(SW["外2021-26H1_t"])) < 1)
A4_break = A4_cherry or A4_notgeneric

# ---------- A5: 頑健性（C1 事実） ----------
say("\n## A5 C1（down 相場で G_5>0）の頑健性")
outw = win("外2021-26H1"); inw = win("在2013-20")
say(f"- 外 down: {fmt(G5[outw&down], True)}・符号検定 p {sign_p(G5[outw&down]):.4f}・1% winsor 平均 {np.mean(np.clip(G5[outw&down], *np.quantile(G5[outw&down],[0.01,0.99]))):+.2f}")
say(f"- 在 down: {fmt(G5[inw&down], True)}・符号検定 p {sign_p(G5[inw&down]):.4f}・1% winsor 平均 {np.mean(np.clip(G5[inw&down], *np.quantile(G5[inw&down],[0.01,0.99]))):+.2f}")
loyo_fail = []
for y in range(2021, 2027):
    w = outw & down & (yG != y); m, se, t, nn = ms(G5[w]); say(f"- 外 down LOYO −{y}: {m:+.2f} (t{t:+.1f}, n{nn})" + ("  ← t<1.5" if t < 1.5 else "")); loyo_fail.append(t < 1.5)
for y in range(2013, 2021):
    w = inw & down & (yG != y); m, se, t, nn = ms(G5[w]); loyo_fail.append(False)
    say(f"- 在 down LOYO −{y}: {m:+.2f} (t{t:+.1f}, n{nn})" + ("  ← t<2" if t < 2 else ""))
say(f"- 外 半分割 down: 2021-23 {fmt(G5[(yG>=2021)&(yG<=2023)&down])} ｜ 2024-26H1 {fmt(G5[(yG>=2024)&down])} ｜ 2024-25 (2026H1 除去) {fmt(G5[(yG>=2024)&(yG<=2025)&down])}")
say(f"- 在 半分割 down: 2013-16 {fmt(G5[(yG>=2013)&(yG<=2016)&down])} ｜ 2017-20 {fmt(G5[(yG>=2017)&(yG<=2020)&down])}")
say("- 曜日別 down（外）: " + " ｜ ".join(f"{nm} {fmt(G5[outw&down&(wdG==k)])}" for k, nm in enumerate("月火水木")))
say("- 曜日別 down（在）: " + " ｜ ".join(f"{nm} {fmt(G5[inw&down&(wdG==k)])}" for k, nm in enumerate("月火水木")))
say(f"- DST 別 down: 在 夏 {fmt(G5[inw&down&sumG])}・冬 {fmt(G5[inw&down&~sumG])} ｜ 外 夏 {fmt(G5[outw&down&sumG])}・冬 {fmt(G5[outw&down&~sumG])}")
say(f"- 別トレンド尺度 down（r5/r60 の符号・16:55 既知）:")
for Lh in (5, 60):
    rL = np.full(n, np.nan)
    for k in np.where(pos >= Lh)[0]: p = pos[k]; rL[k] = (lcD[p] - lcD[p - Lh]) * 1e4
    say(f"    r{Lh}: 在 up {fmt(G5[inw&(rL>0)])}・down {fmt(G5[inw&(rL<=0)])} ｜ 外 up {fmt(G5[outw&(rL>0)])}・down {fmt(G5[outw&(rL<=0)])}")
# cost doubling for out down cell
px_med = np.median(np.exp(lc[iG[outw & down]]))
for rt in (0.42, 0.84):
    for sw in (0, 2):
        net = G5[outw & down] - rt / px_med * 1e4 - sw
        say(f"- 外 down net（往復 {rt} USD・swap {sw} bp/日・中央値価格 {px_med:.0f}）: {fmt(net)} bp")
A5_break = any(loyo_fail)

# ---------- A6: C4 の識別力 ----------
say("\n## A6 「G_5/sd20 一定＝premium」の識別力: 他の成分も sd20 比で一定か")
for wn in W:
    w = win(wn) & np.isfinite(sd20) & (sd20 > 0)
    say(f"- {wn}: G_5/sd20 {np.nanmean(G5[w]/sd20[w]):+.4f} ｜ dip(16:55 足)/sd20 {np.nanmean(DIP[w]/sd20[w]):+.4f} ｜ r_pre30/sd20 {np.nanmean(r_pre30[w]/sd20[w]):+.4f} ｜ |P_5|/sd20 {np.nanmean(np.abs(P5[w])/sd20[w]):+.4f} ｜ |G_5|/sd20 {np.nanmean(np.abs(G5[w])/sd20[w]):+.4f} ｜ sd20 中央値 {np.nanmedian(sd20[w]):.0f} bp")
    q = np.nanquantile(sd20[w], [1/3, 2/3]); s = sd20[w]; g = G5[w]; d_ = DIP[w]
    say(f"    sd20 三分位（低/中/高）: G_5 {fmt(g[s<=q[0]])} / {fmt(g[(s>q[0])&(s<=q[1])])} / {fmt(g[s>q[1]])}；dip {ms(d_[s<=q[0]])[0]:+.2f} / {ms(d_[(s>q[0])&(s<=q[1])])[0]:+.2f} / {ms(d_[s>q[1]])[0]:+.2f}")
    b, se, _ = ols_hc1(G5[w], sd20[w][:, None]); say(f"    OLS G_5 = a + b·sd20: a {b[0]:+.2f} (t{b[0]/se[0]:+.1f})・b {b[1]*100:+.3f} bp per 100bp sd (t{b[1]/se[1]:+.1f})")
A6_break = True  # set below from numbers: dip/sd20 窓間変動が G_5/sd20 と同程度に小さいなら非識別
rat = [(np.nanmean((G5/sd20)[win(wn)&(sd20>0)]), np.nanmean((DIP/sd20)[win(wn)&(sd20>0)])) for wn in ("在2013-20", "外2021-26H1", "近年2024-26H1")]
say(f"- 窓間レンジ: G_5/sd20 {min(r[0] for r in rat):+.4f}〜{max(r[0] for r in rat):+.4f}・dip/sd20 {min(r[1] for r in rat):+.4f}〜{max(r[1] for r in rat):+.4f}（dip は最終印字の戻し成分の源＝premium ではない。それも『ボラ比例』なら C4 は識別しない）")
A6_break = (max(r[1] for r in rat) - min(r[1] for r in rat)) < 0.02

# ---------- verdict ----------
say("\n## 判定（事前固定）")
A1_break = pass_rate >= 0.95
A2b = any(A2_break)
A3_break = A3_hits == 2
hits = [("A1 S 非識別", A1_break), ("A2 戻し/α", A2b), ("A3 与え返し", A3_break), ("A4 対照の事後性/非一般性", A4_break), ("A6 C4 非識別", A6_break)]
nh = sum(v for _, v in hits)
say("- " + "・".join(f"{k}: {'破壊' if v else '不発'}" for k, v in hits))
say(f"- C1 事実（外 down LOYO 全部 t≥1.5）: {'破壊' if A5_break else '生存'}")
say(f"- S の解釈（トレンド独立の構造／premium）: 破壊条件 {nh}/5 → **{'broken' if nh >= 2 else ('inconclusive' if nh == 1 else 'survived')}**")
say(f"- A1 合格率 {pass_rate*100:.1f}%・p(T2 在差) {p_T2:.3f}・p(T1 在差) {p_T1:.3f}・p(P_5 外差) {p_P5:.3f}；A2 α(外) {alpha_out[0]:+.2f} (t{alpha_out[1]:+.1f})；A4 11:55 順位 在 {r_in}/{len(SW)}・外 {r_out}/{len(SW)}")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
