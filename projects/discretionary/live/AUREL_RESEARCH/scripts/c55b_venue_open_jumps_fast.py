# -*- coding: utf-8 -*-
"""
[cycle55 研究レーン] 2026-11-20 — c55 の高速版（同じ事前固定・同じ定義・per-slot 計数表で窓/プラセボを配列和にする）。
c55_venue_open_jumps.py（docstring = 事前固定の正本）の第 1 走は主判定（§1）を印字した後に時間予算（3 分）を超えたため停止した。
本スクリプトは §1 を複製（2 桁一致を確認）し §2〜§8 を同じ定義で出す。定義の変更は無い。
"""
import os, sys, json, time, math
import numpy as np, pandas as pd
from scipy.stats import norm

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c55_venue_open_jumps_result.md")
SEED = 20261120
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle55] 会場の開場直後 15 分のジャンプ集中（季節ボラ標準化）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c55b_venue_open_jumps_fast.py・事前固定は c55_venue_open_jumps.py docstring)")

z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
lc = np.log(cl); r = np.zeros(len(lc)); r[1:] = np.diff(lc); r *= 1e4; flat = (r == 0)
t_utc = pd.to_datetime(ts, unit="s", utc=True); year = t_utc.year.to_numpy(); wd_u = t_utc.weekday.to_numpy()
WDN = ['月','火','水','木','金','土','日']
say(f"- npz {len(ts)} 本 {t_utc[0]}〜{t_utc[-1]} UTC（⑩）・格子の穴 {(np.diff(ts)!=300).sum()}・flat 全体 {flat.mean()*100:.1f}%・曜日別(UTC) "
    + " ".join(f"{WDN[w]}{flat[wd_u==w].mean()*100:.1f}%" for w in range(7)) + "（⑪）")
t_et = t_utc.tz_convert("America/New_York")
et_slot = (t_et.hour * 12 + t_et.minute // 5).to_numpy()
def S(h, m): return h * 12 + m // 5
excl_reopen = (et_slot >= S(17, 0)) & (et_slot <= S(18, 5))
base_ok = (~flat) & (~excl_reopen)
say(f"- ET 17:00–18:10 除外 {excl_reopen.sum()} 本・非 flat ∧ 除外後 {base_ok.sum()} 本")
PERIODS = [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026)]

CLOCKS = {}
def clock(name):
    if name in CLOCKS: return CLOCKS[name]
    tl = t_utc if name == "UTC" else t_utc.tz_convert(name)
    slot = (tl.hour * 12 + tl.minute // 5).to_numpy(); wd = tl.weekday.to_numpy()
    dayi = (tl.tz_localize(None).normalize().to_numpy().astype("datetime64[D]").astype(np.int64))
    ok = base_ok & (wd <= 4)
    df = pd.DataFrame({"y": year[ok], "s": slot[ok], "r": r[ok]})
    g = df.groupby(["y", "s"])["r"]
    med = g.transform("median"); mad = (df["r"] - med).abs().groupby([df["y"], df["s"]]).transform("median"); n = g.transform("size")
    sig = 1.4826 * mad.to_numpy(); sig[n.to_numpy() < 100] = np.nan
    zz = np.full(len(r), np.nan); zz[ok] = df["r"].to_numpy() / sig
    okz = ok & np.isfinite(zz)
    # per (period, slot) tables: N, J4, J5 ; and per day-slot jump indicator for day-level stats
    tabs = {}
    for pname, y0, y1 in PERIODS:
        m = okz & (year >= y0) & (year <= y1)
        N = np.bincount(slot[m], minlength=288)
        J4 = np.bincount(slot[m & (np.abs(zz) >= 4)], minlength=288)
        J5 = np.bincount(slot[m & (np.abs(zz) >= 5)], minlength=288)
        tabs[pname] = dict(N=N, J4=J4, J5=J5, m=m)
    CLOCKS[name] = dict(slot=slot, z=zz, okz=okz, dayi=dayi, tabs=tabs, small=int((g.size() < 100).sum()))
    say(f"- 時計 {name}: 標準化セル n<100 で NaN {CLOCKS[name]['small']} 個・|z| 中央値 {np.nanmedian(np.abs(zz[ok])):.3f}（正規 0.674）・|z|≥4 {np.nanmean(np.abs(zz[ok])>=4)*100:.3f}%・|z|≥5 {np.nanmean(np.abs(zz[ok])>=5)*100:.3f}%")
    return CLOCKS[name]

def excluded_slots(clockname):
    ex = set()
    if clockname == "America/New_York":
        for h, m in [(8, 30), (8, 35), (10, 0), (10, 5), (14, 0), (14, 5)]: ex.add(S(h, m))
    if clockname == "Europe/London":
        for h, m in [(7, 0), (7, 5)]: ex.add(S(h, m))
    if clockname == "UTC":
        for h, m in [(1, 15), (1, 20)]: ex.add(S(h, m))
    return ex

def ratio(tab, W, Cb, key):
    JW = int(tab[key][W].sum()); NW = int(tab["N"][W].sum()); JC = int(tab[key][Cb].sum()); NC = int(tab["N"][Cb].sum())
    rW = JW / max(NW, 1); rC = JC / max(NC, 1); rho = rW / rC if rC > 0 else np.nan
    se = math.sqrt(1 / max(JW, 0.5) + 1 / max(JC, 0.5)); zst = math.log(rho) / se if rho > 0 else np.nan
    p1 = 1 - norm.cdf(zst) if np.isfinite(zst) else np.nan
    mde = math.exp(2.8 * math.sqrt(1 / max(rC * NW, 0.5) + 1 / max(JC, 0.5)))
    return dict(JW=JW, NW=NW, JC=JC, NC=NC, rW=rW, rC=rC, rho=rho, se=se, z=zst, p=p1, mde=mde)

def analyze(clockname, open_slot, wlen=3, thr=4, extra_excl=(), verbose=True, use_excl=True, periods=PERIODS):
    C = clock(clockname); ex = (excluded_slots(clockname) if use_excl else set()) | set(extra_excl)
    key = f"J{thr}"
    W = [open_slot + k for k in range(wlen) if (open_slot + k) not in ex]
    Cb = [s for s in [open_slot + k for k in range(-12, 0)] + [open_slot + k for k in range(3, 15)] if s not in ex and s not in W]
    res = {}
    for pname, y0, y1 in periods:
        tab = C["tabs"][pname]; R = ratio(tab, W, Cb, key)
        # day-level
        m = tab["m"] & np.isin(C["slot"], W); jump = np.abs(C["z"]) >= thr
        dW = pd.Series(jump[m]).groupby(C["dayi"][m]).max(); dC_rate = 1 - (1 - R["rC"]) ** len(W)
        R["rho_day"] = dW.mean() / dC_rate if dC_rate > 0 else np.nan; R["nday"] = int(len(dW))
        cand = []
        for st in range(open_slot - 12, open_slot + 15 - wlen + 1):
            Wp = [st + k for k in range(wlen)]
            if any(s in ex for s in Wp): continue
            Cp = [s for s in [st + k for k in range(-12, 0)] + [st + k for k in range(wlen, wlen + 12)] if s not in ex and s not in Wp]
            cand.append(ratio(tab, Wp, Cp, key)["rho"])
        rhos = np.array(cand); R["rank"] = int((rhos > R["rho"]).sum() + 1); R["nfam"] = len(cand); R["fam_max"] = float(np.nanmax(rhos))
        res[pname] = R
        if verbose:
            say(f"  - {pname}: W {len(W)} 足 J/N {R['JW']}/{R['NW']}（率 {R['rW']*1e4:.2f}/万）・C {len(Cb)} 足 {R['JC']}/{R['NC']}（{R['rC']*1e4:.2f}/万）→ **ρ {R['rho']:.2f}**（ln se {R['se']:.3f}・z {R['z']:+.2f}・片側 p {R['p']:.4f}・MDE ρ* {R['mde']:.2f}）・日単位 ρ_day {R['rho_day']:.2f}（日 {R['nday']}）・プラセボ位置 順位 {R['rank']}/{R['nfam']}（family max ρ {R['fam_max']:.2f}）")
    return res

VENUES = [("SGE 09:00 CST (01:00 UTC)", "UTC", S(1, 0), 3),
          ("London 08:00 (Europe/London)", "Europe/London", S(8, 0), 3),
          ("COMEX 08:20 ET (2 足・08:30 公表足除外)", "America/New_York", S(8, 20), 2),
          ("NYSE 09:30 ET", "America/New_York", S(9, 30), 3)]

say("\n## 1. 主判定 H_OPEN（|z|≥4・W = 開場 3 足・C = ±1 時間 24 足 − 公表足）— c55 第 1 走の複製")
MAIN = {}
for vn, ck, osl, wl in VENUES:
    say(f"- **{vn}**"); MAIN[vn] = analyze(ck, osl, wlen=wl, thr=4)
say("\n### 判定（条件 1 行ずつ・Bonferroni 4 → 在 p≤0.0125）")
for vn in MAIN:
    a = MAIN[vn]["在 2010-20"]; b = MAIN[vn]["外 2021-26H1"]
    ca = (a["rho"] > 1) and (a["p"] <= 0.0125); cb = (b["rho"] > 1) and (b["p"] <= 0.10); cc = (a["rank"] == 1)
    v = "PASS" if (ca and cb and cc) else "null"
    say(f"- {vn}: (a) 在 ρ>1 ∧ p≤0.0125: {'成立' if ca else '不成立'}（ρ {a['rho']:.2f} p {a['p']:.4f}）／(b) 外 ρ>1 ∧ p≤0.10: {'成立' if cb else '不成立'}（ρ {b['rho']:.2f} p {b['p']:.4f}）／(c) 在 順位 1: {'成立' if cc else '不成立'}（{a['rank']}/{a['nfam']}）→ **{v}**")

say("\n## 2. 副（|z|≥5）")
for vn, ck, osl, wl in VENUES:
    say(f"- **{vn}**"); analyze(ck, osl, wlen=wl, thr=5)

say("\n## 3. 陽性対照（ET 08:30 公表 2 足 {08:30,08:35}・対照は近傍 24 足・公表足除外なし）")
for thr in (4, 5):
    say(f"- |z|≥{thr}:"); analyze("America/New_York", S(8, 30), wlen=2, thr=thr, use_excl=False)
say("- 参考: FOMC 14:00 ET 2 足（全平日・声明日は年 8 日のみ＝希釈）")
analyze("America/New_York", S(14, 0), wlen=2, thr=4, use_excl=False)

say("\n## 4. 負の対照（偽の開場: 05:00 UTC・11:00 London・12:00 ET・3 足・|z|≥4）")
for vn, ck, osl in [("05:00 UTC", "UTC", S(5, 0)), ("11:00 London", "Europe/London", S(11, 0)), ("12:00 ET", "America/New_York", S(12, 0))]:
    say(f"- **{vn}**"); analyze(ck, osl, wlen=3, thr=4)

say("\n## 5. 記述: 東京 08:45 JST（23:45 UTC・JPX/TOCOM 日中立会・開始時刻の履歴は記憶・08:50 JST 公表足が W 内）")
analyze("UTC", S(23, 45), wlen=3, thr=4)
say("- 23:50 UTC（08:50 JST 公表足）を W から除いた版:")
analyze("UTC", S(23, 45), wlen=3, thr=4, extra_excl=(S(23, 50),))

say("\n## 6. 記述: 開場 ±1 時間の 5 分プロファイル（|z|≥4 率 /万足・在／外）と 生ボラ（|r| 中央値 bp・在）")
def profile(name, clockname, open_slot):
    C = clock(clockname); rows = []
    for k in range(-12, 15):
        s = open_slot + k
        a = C["tabs"]["在 2010-20"]; b = C["tabs"]["外 2021-26H1"]
        ra = a["J4"][s] / max(a["N"][s], 1) * 1e4; rb = b["J4"][s] / max(b["N"][s], 1) * 1e4
        rows.append(f"[{k*5:+d}:{ra:.0f}/{rb:.0f}]")
    say(f"- {name}: " + " ".join(rows))
    # raw vol step (in-sample): median |r| per slot
    m = C["tabs"]["在 2010-20"]["m"]; sl = C["slot"]
    med = [np.median(np.abs(r[m & (sl == open_slot + k)])) for k in (-6, -3, -1, 0, 1, 2, 3, 6)]
    say(f"  生 |r| 中央値 bp（在・開場 −30/−15/−5/0/+5/+10/+15/+30 分）: " + "/".join(f"{x:.2f}" for x in med))
for vn, ck, osl, wl in VENUES: profile(vn, ck, osl)

say("\n## 7. c45 の精錬: UJ（予定外・非定時分）のうち開場 W に落ちる率 vs 平日非 flat 足の W 占有率")
j45 = pd.read_csv(os.path.join(DATA, "c45_jumps_5sigma_declustered.csv"))
j45_t = pd.DatetimeIndex(pd.to_datetime(j45["ts"], unit="s", utc=True))
def in_window(tt, clockname, open_slot, wlen):
    tl = tt if clockname == "UTC" else tt.tz_convert(clockname)
    sl = (tl.hour * 12 + tl.minute // 5).to_numpy(); return (sl >= open_slot) & (sl < open_slot + wlen)
Wmask45 = np.zeros(len(j45), bool); Wmask_all = np.zeros(len(ts), bool); per_venue = {}
for vn, ck, osl, wl in VENUES:
    mv = in_window(j45_t, ck, osl, wl); per_venue[vn] = mv; Wmask45 |= mv
    Wmask_all |= np.isin(clock(ck)["slot"], [osl + k for k in range(wl)])
occ = Wmask_all[base_ok & (wd_u <= 4)].mean()
yy45 = j45_t.year.to_numpy()
for cls in ["UJ", "SJ", "EVDAY"]:
    mm = (j45["cls"] == cls).to_numpy()
    for pname, y0, y1 in PERIODS[:2]:
        mp = mm & (yy45 >= y0) & (yy45 <= y1); k = int((Wmask45 & mp).sum()); n = int(mp.sum())
        share = k / max(n, 1); se = math.sqrt(occ * (1 - occ) / max(n, 1))
        say(f"- {cls} {pname}: 開場 W に {k}/{n} = {share*100:.1f}%（足占有率 {occ*100:.2f}% → 濃縮 {share/occ:.1f}×・z {(share-occ)/se:+.1f}）")
uj = (j45["cls"] == "UJ").to_numpy()
say("- UJ の会場別（全期間）: " + " / ".join(f"{vn.split(' ')[0]} {int((per_venue[vn] & uj).sum())}" for vn in per_venue))
# where do UJ actually sit? top ET 5-min slots
sl_et45 = (j45_t.tz_convert('America/New_York').hour * 12 + j45_t.tz_convert('America/New_York').minute // 5).to_numpy()
vc = pd.Series(sl_et45[uj]).value_counts().head(8)
say("- UJ の ET スロット上位 8: " + ", ".join(f"{s//12:02d}:{(s%12)*5:02d} {c}" for s, c in vc.items()))

say("\n## 8. ゲート ㉛（印字のみ）: scan 本の SGE 開場窓建玉（UTC 01:00–01:10）vs 対照建玉（00:00–00:55 ∪ 01:15–02:10）の R*")
sc = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))
sc = pd.DataFrame(sc if isinstance(sc, list) else sc.get("rows", sc))
say(f"- scan json n {len(sc)}・列 {list(sc.columns)[:14]} …")
etc = sc["entry_time"]
tt = pd.to_datetime(etc, utc=True, errors="coerce") if etc.dtype == object else pd.to_datetime(etc, unit="s", utc=True)
sl_u = (tt.dt.hour * 12 + tt.dt.minute // 5).to_numpy(); yy = tt.dt.year.to_numpy()
ft = 0.1 / sc["risk"].astype(float).to_numpy()
Rstar = sc["R"].astype(float).to_numpy() + np.where(sc["exit"].astype(str).isin(["SL", "TP"]), 0.0, ft)
inW = np.isin(sl_u, [S(1, 0), S(1, 5)]); inC = np.isin(sl_u, list(range(S(0, 0), S(0, 55) + 1)) + list(range(S(1, 15), S(2, 10) + 1)))
for pname, y0, y1 in PERIODS:
    m = (yy >= y0) & (yy <= y1); a = Rstar[m & inW]; b = Rstar[m & inC]
    if len(a) > 5 and len(b) > 5:
        d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        say(f"- {pname}: W n {len(a)} R̄* {a.mean():+.3f} vs C n {len(b)} {b.mean():+.3f} → Δμ {d:+.3f}R（t {d/se:+.2f}・MDE {2*se:.3f}）")
    else:
        say(f"- {pname}: n 不足（W {len(a)}・C {len(b)}）")

say(f"\n- 実行時間 {time.time()-T0:.1f} s・seed {SEED}・読んだのは XAU_m5_close.npz・c45 csv・refute_c4 json のみ（多年 scan 無し・MT5 無し）")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", OUT)
