# -*- coding: utf-8 -*-
"""
[cycle50 補足 b・事後・判定外] c50 の数字を見た後に書く記述 4 点（新仮説の種・判定には使わない）:
 (1) 文献の主張は「フィックス中の **大きな** 値動きの約 2/3 が下方向」（条件つき・平均ではない）→ |FIX10| 上位十分位の下落日比率（期間別・二項 z）。AM10 も。
 (2) 14:30–15:30 London の 5 分プロファイル（bp/5 分・期間別）＝ PRE30 の平均を含む（c50 は β だけ印字した）。AM 側 10:15–10:50 も。
 (3) 米英 DST 不一致週（15:00 London = 11:00 ET）の FIX10 を全期間プールし、同週のプラセボ時刻窓と比べる（「不一致週の負」が 15:00 固有か週固有か）。
 (4) AM10 の負（P1 −0.94 bp）が c16 の 10–11 時 −2.10 bp/時 のどれだけか（局在率）。
入力は c50 と同じ npz のみ。seed 20261118。
"""
import os, time, math
import numpy as np, pandas as pd
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c50b_fix_window_posthoc.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle50 補足 b・事後] フィックス窓の条件つき方向・5 分プロファイル・DST 不一致週 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c50b_fix_window_posthoc.py)")
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); flat = (r == 0)
t_utc = pd.to_datetime(ts, unit="s", utc=True); t_lon = t_utc.tz_convert("Europe/London"); t_et = t_utc.tz_convert("America/New_York")
wd = t_lon.weekday.to_numpy(); slot = t_lon.hour.to_numpy() * 12 + t_lon.minute.to_numpy() // 5
day = pd.DatetimeIndex(t_lon.tz_localize(None)).normalize(); et_hour = t_et.hour.to_numpy()
def S(h, m): return h * 12 + m // 5
SLOTS = list(range(S(9, 50), S(16, 45))); sel = np.isin(slot, SLOTS) & (wd <= 4)
df = pd.DataFrame({"day": day[sel], "slot": slot[sel], "lc": lc[sel], "flat": flat[sel].astype(int), "eth": et_hour[sel]})
P = df.pivot_table(index="day", columns="slot", values="lc", aggfunc="first").reindex(columns=SLOTS)
F = df.pivot_table(index="day", columns="slot", values="flat", aggfunc="first").reindex(columns=SLOTS)
E = df.pivot_table(index="day", columns="slot", values="eth", aggfunc="first").reindex(columns=SLOTS)
d = pd.DatetimeIndex(P.index); Pv = P.to_numpy(); bp = 1e4
ok = P.notna().all(axis=1).to_numpy() & ((1 - F.loc[:, S(14,30):S(15,25)]).sum(axis=1).to_numpy() >= 8)
et15 = E[S(15, 0)].to_numpy()
def w(h1, m1, h2, m2): return (Pv[:, SLOTS.index(S(h2, m2))] - Pv[:, SLOTS.index(S(h1, m1))]) * bp
FIX10 = w(14, 55, 15, 5); AM10 = w(10, 25, 10, 35)
PER = {"P1 2010-13": (d <= "2013-12-31"), "P2 2014-15/03": (d >= "2014-01-01") & (d <= "2015-03-19"),
       "P3 2015/03-20": (d >= "2015-03-20") & (d <= "2020-12-31"), "P4 2021-26H1": (d >= "2021-01-01")}
PER = {k: v & ok for k, v in PER.items()}

say("\n## (1) 条件つき方向 — |窓リターン| 上位十分位（期間内）の下落日比率（文献の「大きな動きの 2/3 が下」の直接検査・二項 z vs 50%）")
for nm, x in (("FIX10 15:00–15:10", FIX10), ("AM10 10:30–10:40", AM10)):
    for k, m in PER.items():
        xx = x[m]; q = np.quantile(np.abs(xx), 0.9); big = xx[np.abs(xx) >= q]; n = len(big); neg = (big < 0).mean(); zz = (neg - 0.5) / math.sqrt(0.25 / n)
        q75 = np.quantile(np.abs(xx), 0.75); big2 = xx[np.abs(xx) >= q75]; neg2 = (big2 < 0).mean(); z2 = (neg2 - 0.5) / math.sqrt(0.25 / len(big2))
        say(f"- {nm} {k}: 上位 10%（|r|≥{q:.1f} bp・n {n}）下落 **{neg*100:.0f}%** (z {zz:+.2f}) ｜ 上位 25%（≥{q75:.1f}・n {len(big2)}）下落 {neg2*100:.0f}% (z {z2:+.2f})")

say("\n## (2) 5 分プロファイル（bp/5 分・平均・t）— PM 側 14:30–15:30 / AM 側 10:15–10:50 London")
def prof(h0, m0, h1, m1):
    out = []
    s0 = SLOTS.index(S(h0, m0)); s1 = SLOTS.index(S(h1, m1))
    for j in range(s0, s1):
        rr = (Pv[:, j + 1] - Pv[:, j]) * bp  # return of bar opening at SLOTS[j+1]? no: lc diff between consecutive closes = return of bar j+1
        lab = f"{SLOTS[j+1]//12:02d}:{(SLOTS[j+1]%12)*5:02d}"
        row = [lab]
        for k, m in PER.items():
            x = rr[m]; x = x[np.isfinite(x)]; row.append(f"{x.mean():+.2f} ({x.mean()/(x.std(ddof=1)/math.sqrt(len(x))):+.1f})")
        out.append(" | ".join(row))
    return out
say("- 足（開始時刻）| " + " | ".join(PER.keys()) + "  〔値 = 平均 bp (t)〕")
for line in prof(14, 25, 15, 30): say("  - " + line)
say("- AM 側:")
for line in prof(10, 10, 10, 50): say("  - " + line)
PRE30 = w(14, 25, 14, 55)
for k, m in PER.items():
    x = PRE30[m]; say(f"- PRE30 14:30–15:00 {k}: {x.mean():+.2f} bp (t {x.mean()/(x.std(ddof=1)/math.sqrt(len(x))):+.2f}, n {len(x)})")

say("\n## (3) 米英 DST 不一致週（15:00 London = 11:00 ET）— 全期間プール・15:00 窓 vs 同週のプラセボ時刻窓")
mis = ok & (et15 == 11); ali = ok & (et15 == 10)
def st(x):
    x = x[np.isfinite(x)]; return x.mean(), x.mean() / (x.std(ddof=1) / math.sqrt(len(x))), len(x)
for nm, x in (("FIX10 15:00", FIX10), ("11:00", w(10,55,11,5)), ("12:00", w(11,55,12,5)), ("14:00", w(13,55,14,5)), ("16:00", w(15,55,16,5)), ("PRE30 14:30–15:00", PRE30), ("POST20 15:10–15:30", w(15,5,15,25))):
    m1, t1, n1 = st(x[mis]); m0, t0, n0 = st(x[ali])
    say(f"- {nm}: 不一致週 {m1:+.2f} bp (t {t1:+.2f}, n {n1}) ｜ 一致日 {m0:+.2f} (t {t0:+.2f}, n {n0})")
yrs = d.year.to_numpy()
say("- 不一致週 FIX10 年別符号: " + " ".join(f"{y}:{FIX10[mis & (yrs==y)].mean():+.1f}" for y in range(2010, 2027) if (mis & (yrs == y)).sum() >= 5))

say("\n## (4) AM10 の局在率 — P1 の AM10 −0.94 bp vs 同期間 10:00–11:00 London の 1 時間和")
H10 = w(9, 55, 10, 55)
for k, m in PER.items():
    a = AM10[m]; h = H10[m]
    say(f"- {k}: AM10 {a.mean():+.2f} bp ｜ 10–11 時 和 {h.mean():+.2f} bp (t {h.mean()/(h.std(ddof=1)/math.sqrt(len(h))):+.2f}) ｜ 局在率 {a.mean()/h.mean() if abs(h.mean())>0.05 else float('nan'):.2f}（窓は 1 時間の 1/6）")
say("\n## (5) 「オークション直前の 5 分の沈み → 直後の戻し」は bid 人工物か（⑰）— 正味（沈み＋戻し）と他市場・スプレッドの対照")
def net_t(h0, m0, h1, m1, nm):
    x = w(h0, m0, h1, m1)
    for k, m in PER.items():
        xx = x[m]; say(f"- {nm} {k}: 正味 {xx.mean():+.2f} bp (t {xx.mean()/(xx.std(ddof=1)/math.sqrt(len(xx))):+.2f}, n {len(xx)})")
net_t(10, 20, 10, 45, "AM 10:25–10:45（沈み 10:25/10:30 ＋ 戻し 10:35/10:40）")
net_t(14, 50, 15, 15, "PM 14:55–15:15（沈み 14:55/15:00 ＋ 戻し 15:05/15:10）")
say("- 対照 US500 bid（同 London スロット・2012+・P1 は 2012-13 のみ）: 5 分リターン bp (t)")
try:
    zu = np.load(os.path.join(MAC, "US500_m5_close.npz")); tsu = zu["ts"].astype(np.int64); clu = zu["close"].astype(float); lcu = np.log(clu)
    tu = pd.to_datetime(tsu, unit="s", utc=True).tz_convert("Europe/London"); wdu = tu.weekday.to_numpy(); slu = tu.hour.to_numpy() * 12 + tu.minute.to_numpy() // 5
    dayu = pd.DatetimeIndex(tu.tz_localize(None)).normalize(); selu = np.isin(slu, SLOTS) & (wdu <= 4)
    PU = pd.DataFrame({"day": dayu[selu], "slot": slu[selu], "lc": lcu[selu]}).pivot_table(index="day", columns="slot", values="lc", aggfunc="first").reindex(columns=SLOTS)
    du = pd.DatetimeIndex(PU.index); PUv = PU.to_numpy(); yu = du.year.to_numpy()
    PERU = {"P1 2012-13": (du >= "2012-01-01") & (du <= "2013-12-31"), "P2 2014-15/03": (du >= "2014-01-01") & (du <= "2015-03-19"),
            "P3 2015/03-20": (du >= "2015-03-20") & (du <= "2020-12-31"), "P4 2021-26H1": (du >= "2021-01-01")}
    def wu(h1, m1, h2, m2): return (PUv[:, SLOTS.index(S(h2, m2))] - PUv[:, SLOTS.index(S(h1, m1))]) * bp
    for lab, (a, b) in {"10:25 足": ((10, 25), (10, 30)), "10:30 足": ((10, 30), (10, 35)), "10:35 足": ((10, 35), (10, 40)), "14:55 足": ((14, 55), (15, 0)), "15:00 足": ((15, 0), (15, 5)), "15:05 足": ((15, 5), (15, 10))}.items():
        x = wu(a[0], a[1], b[0], b[1]); row = []
        for k, m in PERU.items():
            xx = x[m]; xx = xx[np.isfinite(xx) & (xx != 0)]  # US500 夜間 flat を除く
            row.append(f"{k.split()[0]} {xx.mean():+.2f} ({xx.mean()/(xx.std(ddof=1)/math.sqrt(len(xx))):+.1f}, n{len(xx)})")
        say(f"  - US500 {lab}: " + "・".join(row))
except Exception as e:
    say(f"  - US500 読込失敗: {e}")
say("- 対照 US100 スプレッド（Dukascopy bid/ask M5 中央値・2022-01〜2026-06・pt）: London スロット別の中央値（10:00 ET 公表スロット＝14:55–15:05 London 一致日の拡大の有無）")
try:
    zs = np.load(os.path.join(MAC, "US100_m5_spread.npz")); tss = zs["ts"].astype(np.int64); sp = zs["sp_med"].astype(float)
    tl = pd.to_datetime(tss, unit="s", utc=True).tz_convert("Europe/London"); sls = tl.hour.to_numpy() * 12 + tl.minute.to_numpy() // 5; wds = tl.weekday.to_numpy()
    rows = []
    for (h, m_) in [(10, 15), (10, 20), (10, 25), (10, 30), (10, 35), (10, 40), (14, 45), (14, 50), (14, 55), (15, 0), (15, 5), (15, 10), (15, 15)]:
        mm = (sls == S(h, m_)) & (wds <= 4) & np.isfinite(sp); rows.append(f"{h:02d}:{m_:02d} {np.median(sp[mm]):.2f}")
    say("  - " + "・".join(rows) + "（配信 2 層: 時間外 3.44／現物 1.44・2025-09〜 1.15 ⑮）")
except Exception as e:
    say(f"  - US100 spread 読込失敗: {e}")

say(f"\n- 実行 {time.time()-T0:.1f} s・事後・判定外・npz のみ")
with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
print(f"[written] {OUT}")
