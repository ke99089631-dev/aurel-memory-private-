"""
[REFUTE c36 補足 c] 2026-11-11 — 金曜 16:00–16:50 ET（終値足 16:50→16:55 を除く）の追試・記述・ホールドアウト
補足 b の raw 5 分足で、16:50→16:55 の沈み（−1.5 bp 前後・気配拡大の疑い）は金曜も平日も同じ＝差で相殺。金曜超過は 16:00–16:50 にある。
規則（先に書く）:
  (1) 16:00–16:50 の 金曜 − 基準 Δ・金曜 raw 平均（＝ロング金曜だけの損益）・per-Friday Sharpe・raw>0 割合・在/外/4 窓。
  (2) DST／STD 分割（GMT 時刻に紐づく事象なら差が出る）。
  (3) コスト: 片道スプレッド（16:00 の ask で買い・16:50 の bid で売り）= 0.22 USD／価格（在）・spread_log 中央値（外・近年）を bp で引いた net。
  (4) ホールドアウト（私の 115 セル選択に触れていないデータ）: spread_log.jsonl（口座の live bid・2026-09〜11）で ET 16:00→16:50 の bid リターンを 金曜 vs 火水木。
      n は数週分＝MDE 大。符号と大きさの参考のみ。spread_pt の 16:00–16:55 ET の中央値を曜日別に印字（金曜の気配が異常か）。
  (5) 月曜〜木曜の同窓 raw（プラセボ・ロングしても取れないことの確認）。
読み方: ここは事後発見の記述。4 窓 4/4 で Δ>0 ∧ t≥2 ∧ ホールドアウト同符号 なら「研究レーンへ前向き事前固定を提案」（PROMOTED ではない）。
入力: XAU_m5_close.npz・spread_log.jsonl（読取のみ）。seed 20261111。
"""
import os, sys, math, json, time, datetime as dt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(ROOT, "data"); LIVE = os.path.dirname(ROOT)
sys.argv = [sys.argv[0]]; os.environ["SYM"] = "XAU"; T0 = time.time()
src = open(os.path.join(HERE, "c36_day_of_week.py"), encoding="utf-8").read(); head = src.split("# ---------------- 決着可能性")[0]
g = {"__file__": os.path.join(HERE, "c36_day_of_week.py"), "__name__": "c36_head"}; exec(compile(head, "c36_head", "exec"), g)
df = g["df"]; welch = g["welch"]; WD = g["WD"]; P_ALL = g["P_ALL"]; mod = g["mod"]; cal_ord = g["cal_ord"]; TS = g["TS"]
L = [f"# [REFUTE c36 補足 c] 金曜 16:00–16:50 ET・コスト・ホールドアウト — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c36_friday_late_c.py)"]
def say(s=""): print(s, flush=True); L.append(s)
say("")
GR = {}
for m_ in (16 * 60, 16 * 60 + 50, 16 * 60 + 55):
    mk = mod == m_; GR[m_] = dict(zip(cal_ord[mk].tolist(), P_ALL[mk].tolist()))
PX = dict(zip(cal_ord[mod == 16 * 60].tolist(), P_ALL[mod == 16 * 60].tolist()))
# DST フラグ（ET 暦日 16:00 の UTC オフセット）
et = pd.to_datetime(TS[mod == 16 * 60], unit="s", utc=True).tz_convert("America/New_York")
DST = dict(zip(cal_ord[mod == 16 * 60].tolist(), ((et.tz_localize(None) - et.tz_convert("UTC").tz_localize(None)) == pd.Timedelta(hours=-4)).tolist()))
def seg(o, m0, m1):
    p0 = GR[m0].get(o); p1 = GR[m1].get(o); return math.log(p1 / p0) * 1e4 if (p0 and p1) else np.nan
d = df[df.gap.notna()].copy(); d["r1650"] = [seg(o, 16 * 60, 16 * 60 + 50) for o in d.ord]; d["r16"] = [seg(o, 16 * 60, 16 * 60 + 55) for o in d.ord]
d["px"] = [PX.get(o, np.nan) for o in d.ord]; d["dst"] = [DST.get(o, np.nan) for o in d.ord]; d = d[d.r1650.notna()]
def base_mask(d_): return d_.wd.isin([1, 2, 3]) & ~d_.posthol
def cell(d_, col="r1650"):
    a = d_[d_.wd == 4][col]; b = d_[base_mask(d_)][col]; t, se = welch(a, b); tr = a.mean() / a.std(ddof=1) * math.sqrt(len(a))
    return dict(dl=a.mean() - b.mean(), t=t, mde=2 * se, raw=a.mean(), traw=tr, sd=a.std(ddof=1), pos=(a > 0).mean(), n=len(a), base=b.mean(), px=d_[d_.wd == 4].px.mean())
say("## (1)(3) 16:00–16:50 ET: 金曜 − 基準 Δ・金曜 raw（ロング金曜のみ）・コスト後 net（片道スプレッド）")
SPR = {"在 2010-20": 0.22, "外 2021-26H1": 0.22, "近年 2024-26H1": 0.16, "2010-14": 0.22, "2015-20": 0.22, "2021-23": 0.22, "2024-26H1": 0.16}
for lab, (y0, y1) in {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026), "近年 2024-26H1": (2024, 2026), "2010-14": (2010, 2014), "2015-20": (2015, 2020), "2021-23": (2021, 2023), "2024-26H1": (2024, 2026)}.items():
    c = cell(d[(d.year >= y0) & (d.year <= y1)]); cost = SPR[lab] / c["px"] * 1e4
    say(f"- {lab} n 金 {c['n']}: Δ {c['dl']:+.2f}（t {c['t']:+.2f}・MDE {c['mde']:.1f}）・基準 raw {c['base']:+.2f} ｜ 金曜 raw {c['raw']:+.2f} bp（t {c['traw']:+.2f}・sd {c['sd']:.1f}・>0 {c['pos']*100:.0f}%・per-Friday Sharpe {c['raw']/c['sd']:.2f}・年率 ×√50 {c['raw']/c['sd']*math.sqrt(50):.2f}）"
        f" ｜ 片道 {SPR[lab]} USD／{c['px']:.0f} = {cost:.2f} bp → net {c['raw']-cost:+.2f} bp/金曜（年 ≈ {(c['raw']-cost)*50/100:+.2f}%・名目）")
say("\n## (2) DST／STD 分割（金曜 − 基準 Δ・16:00–16:50）")
for lab, (y0, y1) in {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026)}.items():
    for ds, dl in [(True, "DST（20:00 GMT）"), (False, "STD（21:00 GMT）")]:
        c = cell(d[(d.year >= y0) & (d.year <= y1) & (d.dst == ds)]); say(f"- {lab} {dl}: Δ {c['dl']:+.2f}（t {c['t']:+.2f}・n {c['n']}）・金曜 raw {c['raw']:+.2f}")
say("\n## (5) 曜日別 raw 16:00–16:50（プラセボ・在／外）")
for lab, (y0, y1) in {"在 2010-20": (2010, 2020), "外 2021-26H1": (2021, 2026)}.items():
    w = d[(d.year >= y0) & (d.year <= y1)]
    say(f"- {lab}: " + " ".join(f"{WD[k]} {w[w.wd==k].r1650.mean():+.2f}(t{w[w.wd==k].r1650.mean()/w[w.wd==k].r1650.std(ddof=1)*math.sqrt((w.wd==k).sum()):+.1f})" for k in range(5)))
say("\n## (4) ホールドアウト: spread_log.jsonl（口座 live bid・読取のみ）ET 16:00→16:50 の bid リターン 金曜 vs 火水木・spread_pt 16:00–16:55")
rows = []
with open(os.path.join(LIVE, "spread_log.jsonl"), encoding="utf-8") as f:
    for ln in f:
        try: j = json.loads(ln); rows.append((int(j["ts"]), float(j["bid"]), float(j.get("spread_pt", np.nan))))
        except Exception: pass
S = pd.DataFrame(rows, columns=["ts", "bid", "sp"]).drop_duplicates("ts").sort_values("ts")
S["et"] = pd.to_datetime(S.ts, unit="s", utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None); S["day"] = S.et.dt.date; S["wd"] = S.et.dt.weekday; S["mod"] = S.et.dt.hour * 60 + S.et.dt.minute
say(f"- spread_log {len(S)} 行 {S.et.min()} 〜 {S.et.max()} ET・サンプル間隔 中央値 {S.ts.diff().median():.0f} s")
def near(sd, m, tol=4):
    x = sd[(sd["mod"] >= m - tol) & (sd["mod"] <= m + tol)]
    return None if x.empty else x.iloc[(x["mod"] - m).abs().argmin()]
hold = []
for day, sd in S.groupby("day"):
    a = near(sd, 16 * 60); b = near(sd, 16 * 60 + 50)
    if a is None or b is None: continue
    sp = sd[(sd["mod"] >= 16 * 60) & (sd["mod"] <= 16 * 60 + 55)].sp.median(); sp15 = sd[(sd["mod"] >= 15 * 60) & (sd["mod"] < 16 * 60)].sp.median()
    hold.append((day, int(sd.wd.iloc[0]), math.log(b.bid / a.bid) * 1e4, sp, sp15, a.bid))
Hd = pd.DataFrame(hold, columns=["day", "wd", "r", "sp16", "sp15", "px"])
for k in range(5):
    h = Hd[Hd.wd == k]
    if len(h): say(f"- {WD[k]} n {len(h)}: r 16:00→16:50 平均 {h.r.mean():+.2f} bp（sd {h.r.std(ddof=1) if len(h)>1 else float('nan'):.1f}・>0 {(h.r>0).mean()*100:.0f}%）・spread 16:xx 中央値 {h.sp16.median():.2f}／15:xx {h.sp15.median():.2f}・個別: " + " ".join(f"{str(dd)[5:]}:{r:+.1f}" for dd, r in zip(h.day, h.r)))
fr = Hd[Hd.wd == 4].r; bs = Hd[Hd.wd.isin([1, 2, 3])].r
if len(fr) > 1 and len(bs) > 1:
    t, se = welch(fr, bs); say(f"- ホールドアウト 金曜 − 火水木 Δ {fr.mean()-bs.mean():+.2f} bp（Welch t {t:+.2f}・MDE {2*se:.1f}・n {len(fr)}/{len(bs)}）・金曜 片道 spread {Hd[Hd.wd==4].sp16.median():.2f} USD／{Hd.px.mean():.0f} = {Hd[Hd.wd==4].sp16.median()/Hd.px.mean()*1e4:.2f} bp")
say(f"\n- 実行 {time.time()-T0:.1f} s")
open(os.path.join(DATA, "refute_c36_friday_late_c.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
