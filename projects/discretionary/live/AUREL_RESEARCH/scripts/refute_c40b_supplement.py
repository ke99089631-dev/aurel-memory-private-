# -*- coding: utf-8 -*-
"""
[REFUTE c40 補足 b・2026-11-18] **事後・記述専用**（判定語は本体 refute_c40_intraday_momentum.py の
事前固定で既に機械的に決まっている＝T1 survived／T3-T4 broken。本補足は判定を動かさない）。
本体の結果が答えを要求した 5 点だけを測る:
 S1 2026H1 の寄与: β 外 +0.0262 → ex-2026H1 +0.0106（−60%・落とした日数 123／1362 = 9%）。
    交互作用（D_2026 × FIRST_B）で β_2026H1 と β_2021-25 の差が有意か。前向きセルに書くべき β はどちらか。
 S2 プラセボ② の意味: US500 の FIRST_B の符号が gross の 59% を稼いだ。符号一致率・2 変数回帰（金 FB | US500 FB）・
    「両者が不一致の日」だけの金 FB の β と戦略 → 金固有の情報か「一般的な夜間リスク方向」か。
 S3 反転: プロファイルの 16:30 スロットは 外 β −0.0110 (t −2.03)。16:00 の利得がどれだけ戻るか（累積 β）と、
    **16:00 ちょうどで降りられなかった場合**（出口 16:30／17:00）の net（1×／2×）。
 S4 2026H1 の gross +5.76 bp/日 は予測かドリフトか（mean(LAST)・P(ON>0)・S_demeaned）。
 S5 fat tail（憲章 D）: 外 gross の中央値・上位 1%／5% の日を除いた gross。
コスト: data/c4_spread_structure_result.md の観測値をハードコード（0.16 中央値／0.22 p90／0.32 = 2×）。
読取りと分析のみ・書込みは AUREL_RESEARCH/data 配下のみ。seed 20261118。
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c40b_supplement.md"); L = []
NY = "America/New_York"
def say(s=""):
    print(s, flush=True); L.append(s)
say(f"# [REFUTE c40 補足 b] 事後・記述（判定は本体で確定） — {time.strftime('%Y-%m-%d %H:%M')}")

def load(sym):
    zz = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); return zz["ts"].astype(np.int64), zz["close"].astype(float)
def epoch_et(dates, hour, minute):
    naive = dates + pd.Timedelta(hours=hour, minutes=minute)
    loc = pd.DatetimeIndex(naive).tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    utc = loc.tz_convert("UTC").tz_localize(None)
    return np.asarray((utc - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def price_at(ts, cl, T):
    out = np.full(len(T), np.nan); ok = np.isfinite(T); key = (T[ok] - 300).astype(np.int64)
    pos = np.clip(np.searchsorted(ts, key), 0, len(ts) - 1)
    out[ok] = np.where(ts[pos] == key, cl[pos], np.nan); return out
dates = pd.date_range("2012-01-02", "2026-06-30", freq="D"); dates = dates[dates.weekday <= 4]
N = len(dates); yr = dates.year.to_numpy(); lg = np.log

ts_x, cl_x = load("XAU"); P = lambda h, m: price_at(ts_x, cl_x, epoch_et(dates, h, m))
p16 = P(16, 0); p16p = np.r_[np.nan, p16[:-1]]; p1530 = P(15, 30); p0930 = P(9, 30); p10 = P(10, 0)
FB = (lg(p10) - lg(p16p)) * 1e4; FA = (lg(p10) - lg(p0930)) * 1e4
LAST = (lg(p16) - lg(p1530)) * 1e4
L1630 = (lg(P(16, 30)) - lg(p1530)) * 1e4
L1700 = (lg(P(17, 0)) - lg(p1530)) * 1e4
SECOND = (lg(P(10, 30)) - lg(p10)) * 1e4; MID = (lg(P(12, 30)) - lg(P(12, 0))) * 1e4
TWELFTH = (lg(p1530) - lg(P(15, 0))) * 1e4
valid = np.isfinite(FB) & np.isfinite(FA) & np.isfinite(SECOND) & np.isfinite(MID) & np.isfinite(TWELFTH) & np.isfinite(LAST)
valid &= (LAST != 0) & (FB != 0) & (FA != 0)
M_OUT = valid & (yr >= 2021)
price = p1530

def ols(y, x):
    m = np.isfinite(y) & np.isfinite(x); y2, x2 = y[m], x[m]; n = len(y2)
    if n < 30: return dict(n=n, b=np.nan, t=np.nan, se=np.nan, r2=np.nan)
    xc = x2 - x2.mean(); yc = y2 - y2.mean(); sxx = xc @ xc; b = (xc @ yc) / sxx; e = yc - b * xc
    se = math.sqrt((xc ** 2 @ e ** 2) / sxx ** 2 * n / (n - 2))
    return dict(n=n, b=b, t=b / se, se=se, r2=1 - (e @ e) / (yc @ yc))
def olsk(y, X):
    m = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    y2, X2 = y[m], X[m]; n = len(y2); k = X2.shape[1] + 1
    Z = np.c_[np.ones(n), X2]; ZtZi = np.linalg.inv(Z.T @ Z); b = ZtZi @ Z.T @ y2; e = y2 - Z @ b
    V = ZtZi @ (Z.T * e ** 2) @ Z @ ZtZi * n / (n - k); se = np.sqrt(np.diag(V))
    return b, b / se, n
def strat(sig, y, m, cost=None):
    mm = m & np.isfinite(y) & np.isfinite(sig) & (sig != 0)
    if cost is not None: mm = mm & np.isfinite(price)
    s = np.sign(sig[mm]) * y[mm]
    if cost is not None: s = s - cost / price[mm] * 1e4
    n = len(s); se = s.std(ddof=1) / math.sqrt(n)
    return dict(n=n, mean=s.mean(), t=s.mean() / se, med=np.median(s), pos=(s > 0).mean(), s=s)

# ---------------- S1 2026H1 の寄与 ----------------
say("\n## S1 2026H1（123 日 = 外の 9%）が β の 60% を作っている")
D26 = (yr == 2026).astype(float)
b, t, n = olsk(LAST, np.c_[FB, D26, FB * D26][:, :3] * 1.0) if False else olsk(np.where(M_OUT, LAST, np.nan), np.c_[FB, D26, FB * D26])
say(f"- 外 交互作用: LAST = a + b1·FB + b2·D2026 + b3·FB×D2026 → b1 **{b[1]:+.4f} (t {t[1]:+.2f})**・"
    f"b3 **{b[3]:+.4f} (t {t[3]:+.2f})**・n {n}")
say(f"  → 2021-25 の β は {b[1]:+.4f}・2026H1 は {b[1]+b[3]:+.4f}。差の t {t[3]:+.2f}"
    f"（{'有意に違う' if abs(t[3])>=2 else '差は有意でない＝2026H1 は外れ値だが統計的には同一母数と両立'}）")
o25 = ols(np.where(valid & (yr >= 2021) & (yr <= 2025), LAST, np.nan), FB)
say(f"- 前向きセルに書くべき β の候補: 外 全体 +0.0262（MDE 0.0133）vs ex-2026H1 **{o25['b']:+.4f}（MDE {2*o25['se']:.4f}・t {o25['t']:+.2f}）**"
    f" → ex-2026H1 の β は MDE とほぼ同じ大きさ＝**1 窓での分解能の限界**")
# 1 日ずつの影響（jackknife の最大）
mm = M_OUT & np.isfinite(LAST) & np.isfinite(FB)
yv, xv = LAST[mm], FB[mm]; nb = len(yv)
xc = xv - xv.mean(); yc = yv - yv.mean(); b0 = (xc @ yc) / (xc @ xc)
jk = np.empty(nb)
for i in range(nb):
    k = np.ones(nb, bool); k[i] = False
    xcj = xv[k] - xv[k].mean(); ycj = yv[k] - yv[k].mean(); jk[i] = (xcj @ ycj) / (xcj @ xcj)
say(f"- 1 日 jackknife（外 n{nb}）: β {b0:+.4f}・最大影響日の除去で {jk.min():+.4f}〜{jk.max():+.4f}"
    f"（最も効く 1 日で {abs(b0-jk.min())/b0*100:.0f}% 動く）・上位 10 日除去 {np.sort(jk)[:10].mean():+.4f}")

# ---------------- S2 US500 プラセボの意味 ----------------
say("\n## S2 プラセボ②（US500 の夜間方向）が gross の 59% を稼いだのは何を意味するか")
ts_s, cl_s = load("US500"); Ps = lambda h, m: price_at(ts_s, cl_s, epoch_et(dates, h, m))
p16s = Ps(16, 0); p16sp = np.r_[np.nan, p16s[:-1]]
FBs = (lg(Ps(10, 0)) - lg(p16sp)) * 1e4
m2 = M_OUT & np.isfinite(FBs) & (FBs != 0)
agree = (np.sign(FB[m2]) == np.sign(FBs[m2])).mean()
say(f"- 外 符号一致率 sign(FB_金) == sign(FB_US500): **{agree*100:.1f}%**（n {int(m2.sum())}）・"
    f"相関 r(FB_金, FB_US500) {np.corrcoef(FB[m2], FBs[m2])[0,1]:+.3f}")
b, t, n = olsk(np.where(m2, LAST, np.nan), np.c_[FB, FBs])
say(f"- 2 変数回帰 LAST ~ FB_金 + FB_US500: **b_金 {b[1]:+.4f} (t {t[1]:+.2f})**・b_US500 {b[2]:+.4f} (t {t[2]:+.2f})・n {n}")
mdis = m2 & (np.sign(FB) != np.sign(FBs)); magr = m2 & (np.sign(FB) == np.sign(FBs))
for nm, mk in (("一致日のみ", magr), ("**不一致日のみ**", mdis)):
    o = ols(np.where(mk, LAST, np.nan), FB); g = strat(FB, LAST, mk); n1 = strat(FB, LAST, mk, cost=0.16)
    say(f"- {nm}: β {o['b']:+.4f} (t {o['t']:+.2f}, n{o['n']})・gross S {g['mean']:+.3f} (t {g['t']:+.2f})・1× net {n1['mean']:+.3f} (t {n1['t']:+.2f})")

# ---------------- S3 反転と出口の knife-edge ----------------
say("\n## S3 16:00 の利得は直後に戻る（出口が 16:00 ちょうどである必要があるか）")
for nm, y in (("15:30→16:00（原型）", LAST), ("15:30→16:30", L1630), ("15:30→17:00", L1700)):
    o = ols(np.where(M_OUT, y, np.nan), FB)
    say(f"- 外 {nm} ~ FIRST_B: β {o['b']:+.4f} (t {o['t']:+.2f}, R² {o['r2']*100:.1f}%, n{o['n']})")
say("- 出口別の戦略（外・1 日 1 往復）:")
for nm, y in (("出口 16:00", LAST), ("出口 16:30", L1630), ("出口 17:00", L1700)):
    g = strat(FB, y, M_OUT); n1 = strat(FB, y, M_OUT, cost=0.16); n2 = strat(FB, y, M_OUT, cost=0.32)
    say(f"  - {nm}: gross {g['mean']:+.3f} (t {g['t']:+.2f})・1× net {n1['mean']:+.3f} (t {n1['t']:+.2f})・2× net {n2['mean']:+.3f} (t {n2['t']:+.2f})")
o16 = ols(np.where(M_OUT, LAST, np.nan), FB); o30 = ols(np.where(M_OUT, L1630, np.nan), FB)
say(f"- 16:00 の β {o16['b']:+.4f} → 16:30 までの累積 {o30['b']:+.4f} = **{(1-o30['b']/o16['b'])*100:.0f}% が 30 分で戻る**"
    f"（＝一過性の価格圧力／気配の性質と整合・持続的な再評価ではない）")

# ---------------- S4 2026H1 の中身 ----------------
say("\n## S4 2026H1 の gross +5.76 bp/日 は予測かドリフトか")
for nm, mk in (("2026H1", M_OUT & (yr == 2026)), ("2021-25", M_OUT & (yr <= 2025))):
    k = mk & np.isfinite(LAST) & np.isfinite(FB) & (FB != 0)
    mL = LAST[k].mean(); seL = LAST[k].std(ddof=1) / math.sqrt(k.sum()); p = (FB[k] > 0).mean()
    g = strat(FB, LAST, k); sdm = strat(FB, np.where(k, LAST - mL, np.nan), k)
    say(f"- {nm}: n {int(k.sum())}・mean(LAST) {mL:+.3f} bp (t {mL/seL:+.2f})・P(FB>0) {p*100:.1f}%・"
        f"ドリフト項 {(2*p-1)*mL:+.3f}／gross S {g['mean']:+.3f} (t {g['t']:+.2f})・S_demeaned {sdm['mean']:+.3f} (t {sdm['t']:+.2f})・"
        f"|LAST| 平均 {np.abs(LAST[k]).mean():.2f} bp・価格 中央値 {np.nanmedian(price[k]):.0f}")

# ---------------- S5 fat tail ----------------
say("\n## S5 fat tail（憲章 D「優位は少数の大当たりに乗る」）")
g = strat(FB, LAST, M_OUT); s = np.sort(g["s"])
for q, lab in ((0.01, "上位 1%"), (0.05, "上位 5%")):
    kk = int(len(s) * (1 - q))
    say(f"- 外 gross {g['mean']:+.3f} bp/日・中央値 {g['med']:+.3f}・{lab}（{len(s)-kk} 日）を除くと {s[:kk].mean():+.3f} bp/日"
        f"（1× コスト 0.81 bp を{'上回る' if s[:kk].mean()>0.81 else '**下回る**'}）")
say(f"- 正の日 {g['pos']*100:.1f}%・歪度 {float(pd.Series(g['s']).skew()):+.2f}・最大 1 日 {s[-1]:+.1f} bp／最小 {s[0]:+.1f} bp")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
