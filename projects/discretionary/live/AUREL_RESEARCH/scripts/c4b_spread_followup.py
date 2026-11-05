# -*- coding: utf-8 -*-
"""
c4b_spread_followup.py — cycle4 追補（結果を見た後の追加・事前固定ではない＝記述のみ・判定に使わない）
 目的: c4 の P3 が強い負（ρ −0.77）で出た原因が「市場クローズ（週末・日次メンテ JST5-7）の広い固定スプレッド 0.21/0.22」か確認。
       ＋ 台帳の tick-sim 滑り（slip_pt / sl_slip_pt / tp_fill_ok）を集計し、spread+slip の実コストを 0.56 仮定と比べる。
 読むだけ。出力は data/c4_spread_structure_result.md に追記。
"""
import json, os, sys, io, collections
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c4_spread_structure as c4  # c4 が stdout を UTF-8 に包む（ここで二重に包まない）
lines = []
def P(s=""):
    print(s); lines.append(s)

df = c4.load_spread()
P("\n---\n## 追補（結果を見た後・判定不使用）A: 「広い状態」はいつか")
wide = df.spread_pt >= 0.20
df["stale12"] = df.bid.diff().abs().rolling(12, min_periods=6).sum().shift(1) == 0
P(f"- 全体 wide(≥0.20) 割合 {wide.mean()*100:.1f}%  / 週末(土日 JST) {wide[df.wd>=5].mean()*100:.1f}%  / 平日 JST5-7 {wide[(df.wd<5)&df.jh.between(5,7)].mean()*100:.1f}%  / 平日 JST8-4 {wide[(df.wd<5)&~df.jh.between(5,7)].mean()*100:.2f}%")
P(f"- 直前 12 行 bid 不変(stale) の割合: 週末 {df.stale12[df.wd>=5].mean()*100:.0f}%  平日5-7 {df.stale12[(df.wd<5)&df.jh.between(5,7)].mean()*100:.0f}%  平日8-4 {df.stale12[(df.wd<5)&~df.jh.between(5,7)].mean()*100:.1f}%")
P(f"- stale 行の wide 割合 {wide[df.stale12==True].mean()*100:.1f}% / 非 stale 行の wide 割合 {wide[df.stale12==False].mean()*100:.2f}%")
# open-market subset: weekday, not 5-7, not stale
op = df[(df.wd < 5) & ~df.jh.between(5, 7) & (df.stale12 == False)].copy()
op = op[op.ts.diff().fillna(0) <= 600].dropna(subset=["rv_lag"])
P(f"- 開場サブセット n={len(op)}: spread 中央値 {op.spread_pt.median():.3f} 平均 {op.spread_pt.mean():.4f} p90 {op.spread_pt.quantile(.9):.2f} p99 {op.spread_pt.quantile(.99):.2f} max {op.spread_pt.max():.2f}  値の分布 {dict(sorted(collections.Counter(op.spread_pt.round(2)).items()))}")
rho = c4.spearman(op.spread_pt, op.rv_lag)
q = pd.qcut(op.rv_lag.rank(method="first"), 5, labels=False)
P(f"- 開場サブセット Spearman(spread, rv_lag) = {rho:.3f}  rv 五分位の spread 平均 " + " ".join(f"{m:.4f}" for m in op.groupby(q).spread_pt.mean()) + "  → ボラ依存はほぼ無い（固定スプレッド）")
hm = op.groupby("jh").spread_pt.agg(["mean", lambda s: (s >= 0.20).mean()*100]); hm.columns = ["mean", "wide%"]
P("- 開場サブセット JST 時別 平均/wide%: " + " ".join(f"{h:02d}:{r['mean']:.3f}/{r['wide%']:.1f}" for h, r in hm.iterrows()))

P("\n## 追補 B: 台帳の tick-sim 滑り（slippage_sim L=1s・spread とは別勘定）")
state = {}
with open(c4.LEDGER, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        r = json.loads(line); k = r.get("kind")
        if k == "setup" and r.get("id"): state[r["id"]] = dict(r)
        elif k == "update" and r.get("target"):
            st = state.setdefault(r["target"], {"id": r["target"]})
            for kk, vv in r.items():
                if kk not in ("kind", "logged_at", "target"): st[kk] = vv
rows = []
for sid, st in state.items():
    ra = st.get("reaccel")
    if not (isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None): continue
    e, sl = ra.get("entry"), ra.get("sl"); risk = abs(e - sl)
    def g(key):
        v = ra.get(key, st.get(key)); return v
    rows.append(dict(id=sid, t=ra.get("entry_time"), R=float(ra["R"]), risk=risk, exit=ra.get("exit_reason"),
                     sp=g("spread_pt"), slip=g("slip_pt"), sl_slip=g("sl_slip_pt"), tp_ok=g("tp_fill_ok"), jh=st.get("jst_hour")))
tr = pd.DataFrame(rows).sort_values("t").reset_index(drop=True)
tr["band"] = tr.jh.map(c4.band_of)
P(f"- n={len(tr)}  slip_pt あり {int(tr.slip.notna().sum())}  sl_slip_pt あり {int(tr.sl_slip.notna().sum())}  tp_fill_ok あり {int(tr.tp_ok.notna().sum())}")
s = tr.slip.dropna().astype(float)
P(f"- slip_pt(entry, USD, +=不利): 中央値 {s.median():+.3f} 平均 {s.mean():+.3f} p75 {s.quantile(.75):+.3f} p90 {s.quantile(.9):+.3f} max {s.max():+.2f} min {s.min():+.2f}  >0 {(s>0).mean()*100:.0f}% =0 {(s==0).mean()*100:.0f}% <0 {(s<0).mean()*100:.0f}%")
ss = tr.sl_slip.dropna().astype(float)
if len(ss):
    P(f"- sl_slip_pt(USD): 中央値 {ss.median():+.3f} 平均 {ss.mean():+.3f} p90 {ss.quantile(.9):+.3f} max {ss.max():+.2f}  n={len(ss)}  (SL 決着本のみ: " + (f"中央値 {tr[tr.exit=='SL'].sl_slip.dropna().astype(float).median():+.3f} 平均 {tr[tr.exit=='SL'].sl_slip.dropna().astype(float).mean():+.3f} n={int(tr[tr.exit=='SL'].sl_slip.notna().sum())}" if tr[tr.exit=='SL'].sl_slip.notna().any() else "none") + ")")
to = tr.tp_ok.dropna()
if len(to):
    tpo = tr[tr.exit == "TP"].tp_ok.dropna()
    P(f"- tp_fill_ok: 全体 {dict(collections.Counter(to.astype(str)))}  TP 決着本のみ {dict(collections.Counter(tpo.astype(str)))}  → 紙 TP のうち実約定不成立 {((tpo==False)|(tpo==0)).mean()*100:.1f}% (n={len(tpo)})")
# full cost model: spread(entry) + slip(entry) + sl_slip (if SL)
has = tr.dropna(subset=["sp", "slip"]).copy()
has["sp"] = has.sp.astype(float); has["slip"] = has.slip.astype(float)
has["sls"] = has.sl_slip.astype(float).fillna(0.0).where(has.exit == "SL", 0.0)
has["cost_usd"] = has.sp + has.slip.clip(lower=None) + has.sls
has["cost_R"] = has.cost_usd / has.risk
has["netR"] = has.R - has.cost_R
has["netR_056"] = has.R - 0.56 / has.risk
P(f"- 実コスト(spread+entry slip+SL slip) n={len(has)}: USD 中央値 {has.cost_usd.median():.3f} 平均 {has.cost_usd.mean():.3f} p90 {has.cost_usd.quantile(.9):.2f} max {has.cost_usd.max():.2f}  → cost_R 中央値 {has.cost_R.median():.4f} 平均 {has.cost_R.mean():.4f}")
P(f"- gross 平均R {has.R.mean():+.4f} → net(実測 spread+slip) {has.netR.mean():+.4f}（食う割合 {has.cost_R.mean()/has.R.mean()*100:.0f}%） vs net(0.56 仮定) {has.netR_056.mean():+.4f}; 仮定 0.56 は実測コスト平均の {0.56/has.cost_usd.mean():.1f} 倍")
P("| 帯 | n | gross | 実測 cost USD 平均 | cost_R 平均 | net 実測 | net 0.56 |")
P("|---|---|---|---|---|---|---|")
for b in list(c4.BANDS) + ["jh7-12"]:
    g = has[has.jh.between(7, 12)] if b == "jh7-12" else has[has.band == b]
    if len(g) == 0: continue
    P(f"| {b} | {len(g)} | {g.R.mean():+.3f} | {g.cost_usd.mean():.3f} | {g.cost_R.mean():.4f} | {g.netR.mean():+.3f} | {g.netR_056.mean():+.3f} |")
# tp_fill_ok adjusted: paper TP that would not fill → treat conservatively as 0R? (report only)
if len(to):
    tpf = has[(has.exit == "TP") & ((has.tp_ok == False) | (has.tp_ok == 0))]
    P(f"- 参考: TP 不成立本 n={len(tpf)} の R 合計 {tpf.R.sum():+.1f}（全体合計 {has.R.sum():+.1f} の {tpf.R.sum()/has.R.sum()*100 if has.R.sum() else float('nan'):.0f}%）— これらを 0R にすると平均R {((has.R.sum()-tpf.R.sum())/len(has)):+.4f}（上限側の目安・実際は一部が後で約定/一部が反転 SL）")
with open(c4.OUT, "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("(appended)")
