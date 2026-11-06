#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cycle14 研究レーン 2026-11-06 — 【探索・執行コスト／市場横断】US100 の bid/ask スプレッドの時間構造と
「スプレッド ÷ 5 分の動き」で見た執行コストを、金（固定 0.16 USD）と同じ無次元の物差しで並べる。

事前固定（検証前に書いた。実行後に変えない）
--------------------------------------------
データ: Dukascopy M1 bid/ask close（AssetEmpire/empire/research/dukas/chunks/usatechidxusd-m1-{bid,ask}-*.csv・
        2022-01〜2026-06・読取のみ）。spread_pt = ask_close − bid_close（分足末のスナップショット）。
        5 分の動き = data/macro/{US100,XAU}_m5_close.npz の |Δlog close|（flat 足除外・⑪）。
        金のスプレッドは実口座の実測 固定 0.16 USD（DATA_MAP §4・c4）を価格で割って bps 化。
        金の risk は data/refute_c4_scan_paths_2010_2026.json の 2022-01〜2026-06 の本の risk（USD）。
衛生: 読込後に min/max 時刻（⑩）・flat 分足比率を曜日別（⑪）に印字。spread ≤0 または >50 bps は欠陥として除外し件数を印字。
       「開場分足」= 直近 5 分足のうち bid が 1 回以上動いた分足（閉場中の stale 配信を除く・c4 の 0.21/0.22 の教訓）。

H_A（時間構造）: US100 のスプレッド（bps・開場分足）は UTC 時刻で 2 倍以上動く（金は 1.0 で構造なし）。
   統計量 = 24 時刻の中央値スプレッドの max/min（開場分足 n≥1000 の時刻のみ）。
   PASS = 在・外とも max/min ≥ 2.0 ∧ 在外の時刻プロファイルの Spearman ρ ≥ 0.8。
H_B（コスト比・金との比較）: cf(h) = spread_bps(h) ÷ median|Δlog M5|_bps(h)（＝「5 分の動きの何割がスプレッドか」）。
   予測: 米国現物時間（14:30–21:00 UTC・DST は無視して固定）では cf_US100 < cf_XAU、
         それ以外の開場時間（22:00–13:00 UTC）では cf_US100 > cf_XAU。
   PASS = 在・外とも両方向が成立。片方だけなら partial、どちらも不成立なら FAIL。
在/外: 在 = 2022-01-01〜2024-06-30、外 = 2024-07-01〜2026-06-30（時間順・半分）。
不確かさ: 時刻ごとの中央値は「日×時刻」の中央値を日単位の標本として mean±SE（日を独立単位）。
記述（判定外）: 曜日×時刻、p90、年別、R 換算の投影 = 金の risk/median|ΔM5|（USD/USD）を US100 に当てた
   risk_proj(pt) で spread_pt/risk_proj → cost_R（US100 の scan キャッシュが無いので投影と明記・採用提案でない）。
事前の最重要反証: Dukascopy の bid/ask は我々の口座（金は固定 0.16 で Dukascopy の変動スプレッドと別物）の
   US100 ではない。この分析が言えるのは「インターバンク系 CFD 配信の時間構造」であり、口座の実測（MT5 probe・★2）が要る。
昇格候補ではない。seed なし（決定的）。
"""
import os, sys, time, glob, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c14_us100_spread_structure_result.md")
CACHE = os.path.join(MAC, "US100_m5_spread.npz")
DUK = r"C:\Users\user\AssetEmpire\empire\research\dukas\chunks"
L = []
def say(s=""): print(s, flush=True); L.append(s)

IN_LO, IN_HI = pd.Timestamp("2022-01-01"), pd.Timestamp("2024-07-01")
OUT_LO, OUT_HI = pd.Timestamp("2024-07-01"), pd.Timestamp("2026-07-01")
CASH = set(range(15, 21)) | {14}   # 14:30–21:00 UTC ≈ 時刻 14(後半)…20。14 は丸めて含める
OFF = set(list(range(22, 24)) + list(range(0, 14)))
GOLD_SPREAD_USD = 0.16

def load_m1(side):
    files = sorted(glob.glob(os.path.join(DUK, f"usatechidxusd-m1-{side}-20*.csv")))
    files = [f for f in files if os.path.basename(f).split("-")[3] >= "2022"]
    fr = [pd.read_csv(f, usecols=["timestamp", "close"]) for f in files if os.path.getsize(f) > 0]
    m = pd.concat(fr, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    m["ts"] = m["timestamp"] // 1000
    return m.set_index("ts")["close"], len(files)

say(f"# c14 US100 spread structure — run {pd.Timestamp.now():%Y-%m-%d %H:%M}")
t = time.time()
ask, na = load_m1("ask"); bid, nb = load_m1("bid")
say(f"- 読込: ask {len(ask)} 分 ({na} chunks) {pd.to_datetime(ask.index[0],unit='s')}..{pd.to_datetime(ask.index[-1],unit='s')} UTC／"
    f"bid {len(bid)} 分 ({nb} chunks) {pd.to_datetime(bid.index[0],unit='s')}..{pd.to_datetime(bid.index[-1],unit='s')} UTC（{time.time()-t:.1f} s）")
df = pd.concat({"ask": ask, "bid": bid}, axis=1, join="inner")
say(f"- 突合 (inner): {len(df)} 分（ask の {len(df)/len(ask):.1%}）")
df["sp"] = df["ask"] - df["bid"]
df["mid"] = (df["ask"] + df["bid"]) / 2
df["bps"] = df["sp"] / df["mid"] * 1e4
bad = (df["sp"] <= 0) | (df["bps"] > 50)
say(f"- 欠陥除外: sp≤0 {int((df['sp']<=0).sum())} 分・>50 bps {int((df['bps']>50).sum())} 分 → 残 {int((~bad).sum())}")
df = df[~bad].copy()
dt = pd.to_datetime(df.index, unit="s")
df["date"] = dt.date; df["hour"] = dt.hour; df["dow"] = dt.dayofweek; df["year"] = dt.year
# flat / 開場判定（直近 5 分足で bid が動いたか）
mv = (df["bid"].diff() != 0).astype(int)
df["open"] = mv.rolling(5, min_periods=1).max().astype(bool)
flat_dow = (1 - mv).groupby(df["dow"]).mean()
say("- flat 分足比率（bid 不変・曜日 0=月）: " + " ".join(f"{d}:{v:.1%}" for d, v in flat_dow.items()) + f"・全体 {1-mv.mean():.1%}")
say(f"- 開場分足（直近 5 分で bid が動いた）: {df['open'].mean():.1%}・閉場分足の spread 中央値 {df.loc[~df['open'],'bps'].median():.3f} bps vs 開場 {df.loc[df['open'],'bps'].median():.3f} bps")
op = df[df["open"]].copy()
say(f"- 開場分足 全体: spread 中央値 {op['sp'].median():.3f} pt = {op['bps'].median():.3f} bps・p10 {op['bps'].quantile(.1):.3f}・p90 {op['bps'].quantile(.9):.3f}・mean {op['bps'].mean():.3f}")

# ---- 時刻プロファイル（日×時刻の中央値 → 日を標本）
def hour_profile(d):
    g = d.groupby(["date", "hour"])["bps"].median().reset_index()
    cnt = d.groupby("hour")["bps"].size()
    prof = g.groupby("hour")["bps"].agg(["mean", "median", "std", "size"])
    prof["se"] = prof["std"] / np.sqrt(prof["size"])
    prof["n_min"] = cnt
    return prof

op["win"] = np.where(pd.to_datetime(op.index, unit="s") < IN_HI, "in", "out")
P = {w: hour_profile(op[op["win"] == w]) for w in ["in", "out"]}
say("\n## H_A 時刻プロファイル（開場分足・bps・日×時刻中央値の mean±SE）")
say("| UTC h | 在 mean | ±SE | n_min | 外 mean | ±SE | n_min |")
say("|---|---|---|---|---|---|---|")
for h in range(24):
    a = P["in"].loc[h] if h in P["in"].index else None; b = P["out"].loc[h] if h in P["out"].index else None
    say(f"| {h:02d} | {a['mean']:.3f} | {a['se']:.3f} | {int(a['n_min'])} | {b['mean']:.3f} | {b['se']:.3f} | {int(b['n_min'])} |" if a is not None and b is not None else f"| {h:02d} | - | | | - | | |")
res = {}
for w in ["in", "out"]:
    p = P[w]; p = p[p["n_min"] >= 1000]
    res[w] = dict(mx=p["median"].max(), mn=p["median"].min(), hmx=int(p["median"].idxmax()), hmn=int(p["median"].idxmin()), ratio=p["median"].max() / p["median"].min())
    say(f"- {w}: 時刻中央値 max {res[w]['mx']:.3f} bps (h{res[w]['hmx']:02d}) / min {res[w]['mn']:.3f} (h{res[w]['hmn']:02d}) → **max/min {res[w]['ratio']:.2f}**")
common = P["in"].index.intersection(P["out"].index)
rho, pv = spearmanr(P["in"].loc[common, "median"], P["out"].loc[common, "median"])
say(f"- 在外プロファイル Spearman ρ **{rho:.3f}** (p {pv:.2e}, {len(common)} 時刻)")
HA = (res["in"]["ratio"] >= 2 and res["out"]["ratio"] >= 2 and rho >= 0.8)
say(f"- **判定 H_A: {'PASS' if HA else 'FAIL'}**（規則: 在外 max/min ≥2 ∧ ρ ≥0.8）")

# ---- 曜日×時刻（記述）・年別（記述）
say("\n## 記述: 曜日別 中央値 bps（開場分足）・年別")
say("- 曜日: " + " ".join(f"{d}:{v:.3f}" for d, v in op.groupby("dow")["bps"].median().items()))
yr = op.groupby("year")["bps"].agg(["median", lambda x: x.quantile(.9), "size"])
say("- 年別 中央値/p90/n: " + " ".join(f"{y}:{r['median']:.3f}/{r['<lambda_0>']:.3f}/{int(r['size'])}" for y, r in yr.iterrows()))
say("- 時刻別 p90（全期間）: " + " ".join(f"h{h:02d}:{v:.2f}" for h, v in op.groupby("hour")["bps"].quantile(.9).items()))

# ---- H_B コスト比: spread_bps(h) / median|Δlog M5|_bps(h)
def m5_move(sym, lo, hi):
    z = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = z["ts"]; c = z["close"]
    say(f"- {sym} npz: {len(ts)} 本 {pd.to_datetime(ts[0],unit='s')}..{pd.to_datetime(ts[-1],unit='s')} UTC")
    m = (ts >= lo.timestamp()) & (ts < hi.timestamp())
    ts, c = ts[m], c[m]
    dl = np.abs(np.diff(np.log(c))) * 1e4; ts = ts[1:]; c = c[1:]
    keep = dl > 0  # flat 足除外（⑪）
    d = pd.DataFrame({"ts": ts[keep], "mv": dl[keep], "close": c[keep]})
    d["hour"] = pd.to_datetime(d["ts"], unit="s").dt.hour
    d["win"] = np.where(d["ts"] < IN_HI.timestamp(), "in", "out")
    return d

say("\n## H_B コスト比 cf(h) = spread_bps ÷ median|Δlog M5|_bps（flat 足除外）")
mu = m5_move("US100", IN_LO, OUT_HI); mx = m5_move("XAU", IN_LO, OUT_HI)
flat_us = 1 - len(mu) / ((OUT_HI - IN_LO).total_seconds() / 300); say(f"- US100 M5 flat 除外後 {len(mu)} 本（暦格子比 {1-flat_us:.1%}）／XAU {len(mx)} 本")
gold_bps = (GOLD_SPREAD_USD / mx["close"] * 1e4)
mx["gbps"] = gold_bps
HB = {}
say("| win | UTC h | US100 sp bps | US100 mv bps | cf_US100 | XAU sp bps | XAU mv bps | cf_XAU | cf_US100<cf_XAU |")
say("|---|---|---|---|---|---|---|---|---|")
cf_tab = {}
for w in ["in", "out"]:
    u = mu[mu["win"] == w].groupby("hour")["mv"].median(); x = mx[mx["win"] == w].groupby("hour").agg(mv=("mv", "median"), gbps=("gbps", "median"))
    sp = P[w]["median"]
    rows = []
    for h in range(24):
        if h not in sp.index or P[w].loc[h, "n_min"] < 1000: continue
        cfu = sp[h] / u[h]; cfx = x.loc[h, "gbps"] / x.loc[h, "mv"]
        rows.append((h, sp[h], u[h], cfu, x.loc[h, "gbps"], x.loc[h, "mv"], cfx))
        say(f"| {w} | {h:02d} | {sp[h]:.3f} | {u[h]:.2f} | **{cfu:.3f}** | {x.loc[h,'gbps']:.3f} | {x.loc[h,'mv']:.2f} | **{cfx:.3f}** | {'Y' if cfu<cfx else 'n'} |")
    cf_tab[w] = pd.DataFrame(rows, columns=["h", "spu", "mvu", "cfu", "spx", "mvx", "cfx"]).set_index("h")
    cash = cf_tab[w].loc[cf_tab[w].index.isin(CASH)]; off = cf_tab[w].loc[cf_tab[w].index.isin(OFF)]
    HB[w] = dict(cash_u=cash["cfu"].median(), cash_x=cash["cfx"].median(), off_u=off["cfu"].median(), off_x=off["cfx"].median(),
                 cash_ok=(cash["cfu"] < cash["cfx"]).mean(), off_ok=(off["cfu"] > off["cfx"]).mean())
    say(f"- {w}: 現物時間 cf_US100 中央値 **{HB[w]['cash_u']:.3f}** vs cf_XAU **{HB[w]['cash_x']:.3f}**（US100 が安い時刻 {HB[w]['cash_ok']:.0%}）／"
        f"時間外 cf_US100 **{HB[w]['off_u']:.3f}** vs cf_XAU **{HB[w]['off_x']:.3f}**（US100 が高い時刻 {HB[w]['off_ok']:.0%}）")
cash_pass = all(HB[w]["cash_u"] < HB[w]["cash_x"] for w in HB); off_pass = all(HB[w]["off_u"] > HB[w]["off_x"] for w in HB)
verdict = "PASS" if (cash_pass and off_pass) else ("partial" if (cash_pass or off_pass) else "FAIL")
say(f"- **判定 H_B: {verdict}**（現物時間で US100 安い: {cash_pass}／時間外で US100 高い: {off_pass}）")

# ---- 記述: R 換算の投影
say("\n## 記述: R 換算の投影（US100 の scan キャッシュ無し → 金の risk/|ΔM5| 比を当てた投影・採用提案でない）")
sc = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")))["trades"]
k0 = list(sc[0].keys()); say(f"- scan trades keys: {k0[:16]}…")
tk = "entry_time" if "entry_time" in k0 else k0[0]
ev = [r[tk] for r in sc]
et = pd.to_datetime(ev, unit="s", utc=True) if isinstance(ev[0], (int, float)) else pd.to_datetime(ev, utc=True, errors="coerce")
risk = np.array([r.get("risk", np.nan) for r in sc], dtype=float)
m = (et >= IN_LO.tz_localize("UTC")) & (et < OUT_HI.tz_localize("UTC")) & np.isfinite(risk)
risk_sel = risk[m]
say(f"- 金 risk（2022-01〜2026-06・n{m.sum()}）: 中央値 {np.median(risk_sel):.2f} USD・平均 {risk_sel.mean():.2f}・p10 {np.quantile(risk_sel,.1):.2f}・p90 {np.quantile(risk_sel,.9):.2f}")
xau_mv_usd = (mx["mv"] / 1e4 * mx["close"]).median(); us_mv_pt = (mu["mv"] / 1e4 * (mu["close"])).median()
k_ratio = np.median(risk_sel) / xau_mv_usd
say(f"- 金 median|ΔM5| {xau_mv_usd:.3f} USD → risk/|ΔM5| = **{k_ratio:.1f}**；金 cost_R = 0.16/{np.median(risk_sel):.2f} = **{GOLD_SPREAD_USD/np.median(risk_sel):.4f} R**")
risk_proj = k_ratio * us_mv_pt
say(f"- US100 median|ΔM5| {us_mv_pt:.2f} pt → risk_proj = {risk_proj:.1f} pt；spread_pt 中央値 開場 {op['sp'].median():.3f} pt → cost_R 投影 **{op['sp'].median()/risk_proj:.4f} R**")
for lab, hs in [("現物 14-20h", CASH), ("時間外 22-13h", OFF)]:
    s = op[op["hour"].isin(hs)]["sp"].median(); say(f"  - {lab}: spread 中央値 {s:.3f} pt → cost_R 投影 {s/risk_proj:.4f} R")

# ---- キャッシュ保存（M5 中央値スプレッド・float32）
t5 = (df.index.to_numpy() // 300) * 300
g = pd.DataFrame({"t5": t5, "sp": df["sp"].to_numpy(), "open": df["open"].to_numpy()}).groupby("t5").agg(sp_med=("sp", "median"), sp_max=("sp", "max"), n_open=("open", "sum"))
np.savez(CACHE, ts=g.index.to_numpy().astype(np.int64), sp_med=g["sp_med"].to_numpy().astype(np.float32), sp_max=g["sp_max"].to_numpy().astype(np.float32), n_open=g["n_open"].to_numpy().astype(np.int8))
say(f"\n- キャッシュ保存 {os.path.relpath(CACHE, ROOT)}: {len(g)} M5 行（ts, sp_med, sp_max, n_open）・{os.path.getsize(CACHE)/1e6:.1f} MB")
say(f"- 合計 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote", OUT)
