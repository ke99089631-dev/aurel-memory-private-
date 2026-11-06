# -*- coding: utf-8 -*-
"""
[cycle17 研究レーン 2026-11-07] 【探索・市場構造】日次ブレイク明け（ET 18:00）の再開 pop は「トレンドと独立な構造」か
「上昇相場の夜間シェア」か — 反証 23:35 の手渡し (c) を既存キャッシュで事前固定して解く。

背景（反証 23:35 で確定）: ET 18:00 再開足の正は、在 2013-20 は 7 割が Dukascopy 最終印字（16:55–16:56 ET）の戻り、
外 2021-26H1 には戻りで説明できない切片 +2.16 bp (t7.2)・G_5 +1.91 (t6.0) が残る。半期別 G_0 は上昇期 2025H2 +5.2／2026H1 +9.1
に塊状 → 反証レーン (c)「ギャップの大きさが上昇相場の強さに追随するなら『夜間に上がる相場』の一部でしかない」。

=== 事前固定（この docstring を書いてから数字を見る）===
データ: data/macro/XAU_m5_close.npz（bid・M5・2010-01〜2026-06）。時刻は America/New_York（ET）。格子の穴は ts 一致で回避（⑫）。
母集合: 月〜木の ET 18:00 足で 17:00–17:55 ET の 12 本が全部 flat の「クリーンなブレイク日」、**2013 年以降**（2010-12 はブレイク無し・反証 23:35）。
主変数 G_5 = ln bid(18:05 ET) − ln bid(16:55 ET)（最終印字 16:55 足を除く・反証レーン推奨）。複製 G_0（16:55 足込み）。
窓: 在 2013-20／外 2021-26H1／近年 2024-26H1（D2・16 年プール不使用）。日クラスタ（1 日 1 観測）・bp。

レジーム（トレンド）の切り方:
  T2（主・F_t 可測）: 直近 20 営業日リターン r20 = ln bid(16:55 ET 当日) − ln bid(16:55 ET 20 営業日前)（月〜金の 16:50 足 close）。
      符号で up／down。16:55 時点で既知＝前向きに使える識別子。
  T2b（複製）: 同じ 20 営業日だが各日の 16:55 足＋18:00 足（＝ギャップ区間）を除いた「ギャップ抜き」r20。過去ギャップの寄与を外す。
  T1（記述・反証 (c) への直接回答・同時期＝前向き不可）: 当該暦月の「ギャップ抜き」月次リターンの符号で up 月／down 月。
  D1（記述・機構 (a) 用）: 同日 r_day = ln bid(16:55 ET 当日) − ln bid(18:05 ET 前日) の符号（当日の日中が下げた日に pop が大きいか）。
プラセボ窓 P_5: 同じ日の **11:55 → 13:05 ET**（ブレイクを含まない 70 分・NY 昼）を G_5 と同じ条件で切る。
   「トレンドの夜間シェア」なら普通の 70 分窓も up で正・down で負になる筈。
288 スロット プラセボ: 外 down 日だけで ET 288 スロットの単足平均を取り、18:00 スロットの順位（1/288 なら down 相場でも再開足が最大）。

予測（構造説 S）: down 相場でも G_5 > 0。予測（夜間シェア説 T）: down 相場で G_5 ≤ 0、up 相場だけ正。
判定（事前固定・主セル = T2 down の G_5・在と外の 2 セル）:
  S（トレンド独立の構造）: 在 G_5(down) > 0 (t≥2) ∧ 外 G_5(down) > 0 (t≥1.5) ∧ 外 P_5(down) の t < 2（普通の窓は down で立たない）。
  T（夜間シェア）: 外 G_5(down) の t ≤ 0.5 ∧ 外 G_5(up) t≥2。
  それ以外 inconclusive。null には MDE（2·se）を添える（⑦）。
副次（記述）: up−down 差とその t・r20 三分位・年別 G_5 vs 年間ギャップ抜きドリフトの Spearman（14 年）・G_5 の年間ドリフト占有率・
  G_5／直近 20 日 日次 sd（Sharpe 型の定常性）・G_0 複製・T1 月符号・D1 同日符号。
事前の最重要反証: (i) T2 の up/down は 2021-26 で up が多数（片符号 >90% なら識別不能 ⑬・比率を先に印字）、(ii) down 日の G_5 正は
  「下げ相場の引けに売られ再開で戻る」機構 (a) と区別がつかない → D1 で同日下げ日／上げ日に分けて併記、(iii) bid のみ（反証 Q2 で偏り +0.01 bp・無視）。
昇格候補ではない（受け取れない: 反証 Q7）。入力は既存キャッシュのみ・scan 無し・MT5 無し・外部通信無し。seed 20261107。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c17_gap_trend_conditioning_result.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle17] 再開 pop（ET 18:00・G_5・2013+）はトレンド独立か夜間シェアか — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c17_gap_trend_conditioning.py)")

W = {"在2013-20": (2013, 2020), "外2021-26H1": (2021, 2026), "近年2024-26H1": (2024, 2026)}
def ms(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 2: return (np.nan, np.nan, np.nan, n)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n); return (m, se, m / se if se > 0 else np.nan, n)
def fmt(x, mde=False):
    m, se, t, n = ms(x); s = f"{m:+.2f} (t{t:+.1f}, n{n})"
    if mde and n > 1: s += f", MDE {2*se:.2f}"
    return s
def diff_t(a, b):
    ma, sa, _, na = ms(a); mb, sb, _, nb = ms(b)
    if na < 2 or nb < 2: return (np.nan, np.nan)
    se = math.sqrt(sa**2 + sb**2); return (ma - mb, (ma - mb) / se)

# ---------- load ----------
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); r_bp = r * 1e4; flat = r == 0
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_ny = t_utc.tz_convert("America/New_York")
h = t_ny.hour.to_numpy(); mi = t_ny.minute.to_numpy(); wd = t_ny.weekday.to_numpy(); yr = t_ny.year.to_numpy()
day = yr * 10000 + t_ny.month.to_numpy() * 100 + t_ny.day.to_numpy(); mon = day // 100
dts = np.diff(ts); gap_after = np.where(dts != 300)[0]
valid = np.ones(len(ts), bool); valid[gap_after + 1] = False
r_bp_v = np.where(valid, r_bp, np.nan)
say(f"- XAU npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）、flat 全体 {flat.mean()*100:.1f}%（⑪）、格子の穴 {len(gap_after)} 箇所（⑫・ts 一致で参照）")
def idx_at(target):
    j = np.clip(np.searchsorted(ts, target), 0, len(ts) - 1); return np.where(ts[j] == target, j, -1)

# ---------- gap days ----------
iG = np.where((wd <= 3) & (h == 18) & (mi == 0) & (yr >= 2013))[0]; tG = ts[iG]
i1650 = idx_at(tG - 70 * 60); i1655 = idx_at(tG - 65 * 60)
BRK = np.column_stack([idx_at(tG - 300 * j) for j in range(1, 13)])
i1150 = idx_at(tG - (6 * 3600 + 10 * 60)); i1300 = idx_at(tG - 5 * 3600)
iPrev = idx_at(tG - 86400)
ok = (i1650 >= 0) & (i1655 >= 0) & np.all(BRK >= 0, axis=1) & (i1150 >= 0) & (i1300 >= 0) & valid[iG] & valid[i1650]
iG, i1650, i1655, BRK, i1150, i1300, iPrev = iG[ok], i1650[ok], i1655[ok], BRK[ok], i1150[ok], i1300[ok], iPrev[ok]
clean = np.all(flat[BRK], axis=1)
say(f"- ET 18:00 足 候補日（月〜木・2013+・参照実在）{len(iG)}、クリーン日 {clean.sum()}（{clean.mean()*100:.1f}%）")
iG, i1650, i1655, i1150, i1300, iPrev = iG[clean], i1650[clean], i1655[clean], i1150[clean], i1300[clean], iPrev[clean]
yG = yr[iG]; dG = day[iG]; mG = mon[iG]
G5 = (lc[iG] - lc[i1650]) * 1e4; G0 = (lc[iG] - lc[i1655]) * 1e4
P5 = (lc[i1300] - lc[i1150]) * 1e4
prev_ok = (iPrev >= 0) & (h[np.clip(iPrev, 0, len(h) - 1)] == 18)
r_day = np.where(prev_ok, (lc[i1650] - lc[np.clip(iPrev, 0, len(lc) - 1)]) * 1e4, np.nan)
say(f"- G_5 全体: " + " ｜ ".join(f"{wn} {fmt(G5[(yG>=a)&(yG<=b)])}" for wn, (a, b) in W.items()) + "  （反証 23:35: 在2010-20 +1.03／外 +1.91／近年 +2.86）")
say(f"- P_5 プラセボ窓 11:55→13:05 ET 全体: " + " ｜ ".join(f"{wn} {fmt(P5[(yG>=a)&(yG<=b)])}" for wn, (a, b) in W.items()))

# ---------- daily series (Mon-Fri) ----------
# 16:50 bar close = price at 16:55 ET
iD = np.where((wd <= 4) & (h == 16) & (mi == 50))[0]; iD = iD[valid[iD]]
dD = day[iD]; lcD = lc[iD]
# daily sums: total and gap-less (exclude 16:55 and 18:00 ET bars of each day)
gapbar = ((h == 16) & (mi == 55)) | ((h == 18) & (mi == 0))
df = pd.DataFrame({"d": day, "r": r_bp_v, "rg": np.where(gapbar, 0.0, r_bp_v), "wd": wd})
df = df[df["wd"] <= 4]
dsum = df.groupby("d").agg(tot=("r", "sum"), gapless=("rg", "sum"))
dsum = dsum.reindex(dD)  # align to days having a 16:50 bar
tot = dsum["tot"].to_numpy(); gapless = dsum["gapless"].to_numpy()
pos = np.searchsorted(dD, dG); assert np.all(dD[np.clip(pos, 0, len(dD) - 1)] == dG), "gap day missing in daily series"
okp = pos >= 20
r20 = np.full(len(pos), np.nan); r20b = np.full(len(pos), np.nan); sd20 = np.full(len(pos), np.nan)
cg = np.concatenate([[0.0], np.nancumsum(gapless)])
for k in np.where(okp)[0]:
    p = pos[k]
    r20[k] = (lcD[p] - lcD[p - 20]) * 1e4                  # 20 営業日前の 16:55 → 当日 16:55（既知）
    r20b[k] = cg[p + 1] - cg[p - 19] - gapless[p]          # 直近 20 日の gapless 和（当日分は 16:55 まで未確定なので当日を除く＝19 日分+前日まで）
    r20b[k] = cg[p] - cg[p - 20]                           # 前日までの 20 日 gapless 和（当日の日中は含めない・保守）
    w = tot[p - 20:p]; sd20[k] = np.nanstd(w, ddof=1)
# monthly gap-less return (contemporaneous, descriptive)
msum = pd.Series(gapless, index=dD).groupby(dD // 100).sum()
mret = msum.reindex(mG).to_numpy()

for lab, x in (("T2 r20（既知）", r20), ("T2b r20 gapless", r20b), ("T1 月 gapless", mret), ("D1 同日 r_day", r_day)):
    say(f"- {lab} の up 比率（⑬）: " + " ｜ ".join(f"{wn} up {np.nanmean(x[(yG>=a)&(yG<=b)]>0)*100:.0f}% (n{np.isfinite(x[(yG>=a)&(yG<=b)]).sum()})" for wn, (a, b) in W.items()))

# ---------- main cells ----------
def cells(var, cond, name, mde=True):
    say(f"\n### {name}")
    for wn, (a, b) in W.items():
        w = (yG >= a) & (yG <= b) & np.isfinite(cond)
        up = var[w & (cond > 0)]; dn = var[w & (cond <= 0)]
        d, td = diff_t(up, dn)
        say(f"- {wn}: all {fmt(var[w])} ｜ **up {fmt(up, mde)}** ｜ **down {fmt(dn, mde)}** ｜ up−down {d:+.2f} (t{td:+.1f})")
say("\n## 1. 主セル: G_5 を T2（直近 20 営業日の符号・16:55 既知）で切る")
cells(G5, r20, "G_5 × T2 r20 符号（主）")
cells(P5, r20, "P_5 プラセボ窓（11:55→13:05 ET）× T2 r20 符号")
cells(G0, r20, "G_0 複製（16:55 足込み）× T2 r20 符号", mde=False)
say("\n## 2. 複製・記述")
cells(G5, r20b, "G_5 × T2b r20 gapless（過去ギャップ寄与を除いた 20 日）", mde=False)
cells(G5, mret, "G_5 × T1 当該月 gapless 月次リターン符号（同時期・記述＝反証 (c) への直接回答）", mde=False)
cells(P5, mret, "P_5 プラセボ × T1 月符号", mde=False)
cells(G5, r_day, "G_5 × D1 同日 r_day 符号（前日 18:05 → 当日 16:55・機構 (a) 用）", mde=False)
# terciles of r20 (window-wise)
say("\n### G_5 の r20 三分位（窓内三分位・下/中/上）と OLS 傾き β (bp per 100 bp of r20)")
for wn, (a, b) in W.items():
    w = (yG >= a) & (yG <= b) & np.isfinite(r20); x = r20[w]; y = G5[w]
    qa, qb = np.quantile(x, [1 / 3, 2 / 3]); ter = [x <= qa, (x > qa) & (x <= qb), x > qb]
    beta = np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1); res = y - y.mean() - beta * (x - x.mean())
    se_b = math.sqrt((res**2).sum() / (len(x) - 2) / ((x - x.mean())**2).sum())
    say(f"- {wn}: " + " / ".join(fmt(y[m_]) for m_ in ter) + f"；β {beta*100:+.3f} bp/100bp (t{beta/se_b:+.1f})；r20 三分位境界 {qa:+.0f}/{qb:+.0f} bp")
    xp = P5[w]; betap = np.cov(x, xp, ddof=1)[0, 1] / x.var(ddof=1); resp = xp - xp.mean() - betap * (x - x.mean())
    se_p = math.sqrt((resp**2).sum() / (len(x) - 2) / ((x - x.mean())**2).sum())
    say(f"  P_5 プラセボ 三分位: " + " / ".join(fmt(xp[m_]) for m_ in ter) + f"；β {betap*100:+.3f} bp/100bp (t{betap/se_p:+.1f})")

# ---------- 288-slot placebo on down days ----------
say("\n## 3. 288 スロット プラセボ: down 日（T2 r20≤0）だけの ET 単足平均で 18:00 スロットの順位")
slot = h * 12 + mi // 5
dayset = {}
for wn, (a, b) in W.items():
    for lab, cond in (("down", r20 <= 0), ("up", r20 > 0)):
        days_sel = set(dG[(yG >= a) & (yG <= b) & np.isfinite(r20) & cond])
        msk = np.isin(day, list(days_sel)) & (wd <= 3)
        dfs = pd.DataFrame({"s": slot[msk], "r": r_bp_v[msk]}).dropna(); g = dfs.groupby("s")["r"]
        m_s = g.mean().reindex(range(288)).to_numpy(); se_s = (g.std(ddof=1) / np.sqrt(g.size())).reindex(range(288)).to_numpy()
        t_s = m_s / se_s; s18 = 216; s1655 = 16 * 12 + 11
        rank_m = int((m_s > m_s[s18]).sum()) + 1; rank_t = int((t_s > t_s[s18]).sum()) + 1
        top = np.argsort(-m_s)[:3]
        say(f"- {wn} {lab} 日 n{len(days_sel)}: 18:00 スロット {m_s[s18]:+.2f} bp (t{t_s[s18]:+.1f}) 順位 平均 {rank_m}/288・t {rank_t}/288；16:55 スロット {m_s[s1655]:+.2f} (t{t_s[s1655]:+.1f})；"
            f"上位 3: " + ", ".join(f"{s//12:02d}:{(s%12)*5:02d} {m_s[s]:+.2f}" for s in top) + f"；日中 09:30–16:00 の和 {np.nansum(m_s[114:192]):+.1f} bp/日")

# ---------- yearly ----------
say("\n## 4. 年別: G_5 平均 vs 年間 gapless ドリフト（bp/日）・G_5 の年間ドリフト占有・G_5/sd20")
ysum = pd.Series(gapless, index=dD).groupby(dD // 10000).sum(); ycnt = pd.Series(gapless, index=dD).groupby(dD // 10000).size()
ytot = pd.Series(tot, index=dD).groupby(dD // 10000).sum()
rows = []
for y in range(2013, 2027):
    w = yG == y
    if w.sum() < 20: continue
    m, se, t, n = ms(G5[w]); drift = ysum.get(y, np.nan) / ycnt.get(y, np.nan); share = G5[w].sum() / ytot.get(y, np.nan) * 100
    ratio = np.nanmean(G5[w] / sd20[w])
    rows.append((y, m, drift, share, ratio))
    say(f"- {y}: G_5 {m:+.2f} bp (t{t:+.1f}, n{n}) ｜ gapless ドリフト {drift:+.2f} bp/日 ｜ 年間総リターン {ytot.get(y, np.nan):+.0f} bp のうち G_5 合計 {G5[w].sum():+.0f} bp（{share:+.0f}%） ｜ G_5/sd20 {ratio:+.3f}")
A = np.array(rows)
def spear(a, b):
    ra = pd.Series(a).rank().to_numpy(); rb = pd.Series(b).rank().to_numpy(); return np.corrcoef(ra, rb)[0, 1]
say(f"- 年横断 Spearman ρ(G_5 平均, gapless ドリフト) = {spear(A[:,1], A[:,2]):+.2f}（n{len(A)} 年）；ρ(G_5, 年間総リターン) = {spear(A[:,1], [ytot.get(int(y), np.nan) for y in A[:,0]]):+.2f}")
say(f"- G_5/sd20 窓別: " + " ｜ ".join(f"{wn} {np.nanmean((G5/sd20)[(yG>=a)&(yG<=b)]):+.3f} (t{ms((G5/sd20)[(yG>=a)&(yG<=b)])[2]:+.1f})" for wn, (a, b) in W.items()))

# ---------- verdict ----------
say("\n## 判定（事前固定）")
def cell(var, cond, a, b, up):
    w = (yG >= a) & (yG <= b) & np.isfinite(cond); return ms(var[w & ((cond > 0) if up else (cond <= 0))])
inD = cell(G5, r20, 2013, 2020, False); outD = cell(G5, r20, 2021, 2026, False); outU = cell(G5, r20, 2021, 2026, True); outPD = cell(P5, r20, 2021, 2026, False)
S = (inD[2] >= 2) and (inD[0] > 0) and (outD[2] >= 1.5) and (outD[0] > 0) and (outPD[2] < 2)
T = (outD[2] <= 0.5) and (outU[2] >= 2)
say(f"- 在 G_5(down) {inD[0]:+.2f} (t{inD[2]:+.1f}, n{inD[3]})・外 G_5(down) {outD[0]:+.2f} (t{outD[2]:+.1f}, n{outD[3]})・外 G_5(up) {outU[0]:+.2f} (t{outU[2]:+.1f}, n{outU[3]})・外 P_5(down) {outPD[0]:+.2f} (t{outPD[2]:+.1f})")
say("- → " + ("**S: トレンド独立の構造**" if S else ("**T: 夜間シェア（トレンド依存）**" if T else "**inconclusive**")))
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
