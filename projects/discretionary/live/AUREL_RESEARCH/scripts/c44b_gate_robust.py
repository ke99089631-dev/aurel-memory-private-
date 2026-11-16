# -*- coding: utf-8 -*-
"""
[cycle44 補足 b 研究レーン 2026-11-17] ゲート ㉛ の外（2021-26H1）で立った「NFP/FOMC 発表後 2 時間に建玉した scan 本 Δμ +0.48R (t 3.2, n 85)」の**事後・記述**の頑健性（判定に使わない）:
  上位 3 本の寄与・中央値・TP 率・種別別（NFP/FOMC）・側別・年別・x0 look-ahead 対照・同時刻対照の在外差。㊶（在 null → 外 t 3）の主型かどうかを読むための数字だけ。
入力: refute_c4 json・FOMC_dates.csv・c24 NFP 規則。scan 無し・外部通信無し。
"""
import os, json, math
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c44b_gate_robust.md"); L = []; NY = "America/New_York"
def say(s=""): print(s, flush=True); L.append(s)
def epoch_et(dates, hour, minute):
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hour, minutes=minute); loc = naive.tz_localize(NY, nonexistent="NaT", ambiguous="NaT")
    return np.asarray((loc.tz_convert("UTC").tz_localize(None) - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1), dtype=float)
def nfp_dates_v2(y0=2009, y1=2026):
    out = []
    for y in range(y0, y1 + 1):
        for mth in range(1, 13):
            d12 = pd.Timestamp(year=y, month=mth, day=12); sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7); rel = sat + pd.Timedelta(days=20)
            if rel.month == 1 and rel.day == 1: rel += pd.Timedelta(days=7)
            if rel.month == 7 and rel.day == 4: rel -= pd.Timedelta(days=1)
            out.append(rel)
    return pd.DatetimeIndex(out)
F = pd.read_csv(os.path.join(MAC, "FOMC_dates.csv")); F["date"] = pd.to_datetime(F["date"]); FOMC = pd.DatetimeIndex(F[(F.scheduled == 1) & (F.date >= "2013-03-20")].date)
NFP = nfp_dates_v2(); t_nfp = epoch_et(NFP, 8, 30); t_fomc = epoch_et(FOMC, 14, 0)
d = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8")); FT = d["frozen"]["FEED_TOL"]
tr = pd.DataFrame(d["trades"]); tr["dec"] = tr["exit"].isin(["SL", "TP"]); tr["Rs"] = tr["R"] + (FT / tr["risk"]) * tr["dec"]
et_ = tr.entry_time.to_numpy(float)
def inwin(t0s):
    t0s = np.sort(t0s[np.isfinite(t0s)]); pos = np.clip(np.searchsorted(t0s, et_, side="right") - 1, 0, len(t0s) - 1); return (et_ >= t0s[pos]) & (et_ < t0s[pos] + 7200)
tr["nfp"] = inwin(t_nfp); tr["fomc"] = inwin(t_fomc); tr["ev"] = tr.nfp | tr.fomc
e_ny = pd.DatetimeIndex(pd.to_datetime(et_.astype(np.int64), unit="s", utc=True)).tz_convert(NY); hh = e_ny.hour.to_numpy() + e_ny.minute.to_numpy() / 60
evdays = pd.DatetimeIndex(list(NFP) + list(FOMC) + list(pd.DatetimeIndex(pd.read_csv(os.path.join(MAC, "CPI_dates.csv")).date)))
isevday = pd.DatetimeIndex(e_ny.tz_localize(None).normalize()).isin(evdays)
tr["ctrl"] = (((hh >= 8.5) & (hh < 10.5)) | ((hh >= 14) & (hh < 16))) & ~isevday & (e_ny.weekday.to_numpy() <= 4)
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); d_ = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d_, d_ / se
say("# [cycle44 補足 b] ゲート ㉛ 外の「発表後 2 時間建玉」Δμ の頑健性（事後・記述）")
say("| 窓 | n ev/ctrl | Δμ (t) | ev 平均 R* | 中央値 ev/ctrl | TP 率 ev/ctrl | 上位 3 本の寄与（ΣR* 正分） | 上位 3 本除去 Δμ (t) | x0 Δ (t) | NFP 群 n/平均 | FOMC 群 n/平均 | BUY n/平均 | SELL n/平均 |")
say("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for lab, lo, hi in [("在 2010-20", 2010, 2020), ("外 2021-26H1", 2021, 2026), ("近年 2024-26H1", 2024, 2026), ("外 ex-近年 2021-23", 2021, 2023)]:
    o = tr[(tr.year >= lo) & (tr.year <= hi)]; A, B = o[o.ev], o[o.ctrl]
    dm, tm = welch(A.Rs, B.Rs); srt = A.Rs.sort_values(ascending=False); top3 = srt.iloc[:3].sum() / max(srt[srt > 0].sum(), 1e-9)
    A3 = A.drop(srt.index[:3]); dm3, tm3 = welch(A3.Rs, B.Rs); d0, t0 = welch(A.x0, B.x0)
    an, af = A[A.nfp], A[A.fomc]; ab, as_ = A[A.side == "BUY"], A[A.side == "SELL"]
    say(f"| {lab} | {len(A)}/{len(B)} | **{dm:+.3f} ({tm:+.2f})** | {A.Rs.mean():+.3f} | {A.Rs.median():+.2f}/{B.Rs.median():+.2f} | {(A.exit=='TP').mean()*100:.0f}/{(B.exit=='TP').mean()*100:.0f}% | {top3*100:.0f}% | {dm3:+.3f} ({tm3:+.2f}) | {d0:+.3f} ({t0:+.2f}) | {len(an)}/{an.Rs.mean():+.2f} | {len(af)}/{af.Rs.mean():+.2f} | {len(ab)}/{ab.Rs.mean():+.2f} | {len(as_)}/{as_.Rs.mean():+.2f} |")
say("- 年別（ev 群 n・平均 R*・ctrl 平均）: " + " ".join(f"{y}:{int((tr.ev&(tr.year==y)).sum())}/{tr[tr.ev&(tr.year==y)].Rs.mean():+.2f}/{tr[tr.ctrl&(tr.year==y)].Rs.mean():+.2f}" for y in range(2013, 2027)))
o = tr[tr.year >= 2021]; A = o[o.ev]
say(f"- 外 ev 群の R* 分布: p10 {A.Rs.quantile(0.1):+.2f}・p50 {A.Rs.median():+.2f}・p90 {A.Rs.quantile(0.9):+.2f}・max {A.Rs.max():+.2f}・>+3R 本 {int((A.Rs>3).sum())}・hold 中央値 {A.hold.median():.0f} 本（ctrl {o[o.ctrl].hold.median():.0f}）・b 中央値 {A.b.median():.2f}（ctrl {o[o.ctrl].b.median():.2f}）")
say(f"- 外 ev 群の建玉 ET 時刻分布: " + " ".join(f"{h}h:{int(((e_ny.hour.to_numpy()==h)&tr.ev.to_numpy()&(tr.year.to_numpy()>=2021)).sum())}" for h in (8, 9, 10, 14, 15)))
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("saved", OUT)
