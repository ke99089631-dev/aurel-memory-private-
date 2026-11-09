# -*- coding: utf-8 -*-
"""
[cycle25 補足 b・事後・記述] 台帳を FEED_TOL 保守規則の導入日（2026-10-24 会長GO・setup_engine._simulate のコメント）で
**決着時刻**（exit_time）により 2 分し、scan（frozen FEED_TOL 0.1＝保守規則・2026-11-04 生成）と TP 率・平均R・6 統計を比べる。
主結果を見た後の分解なので判定には使わない（記述）。問い: 台帳 +0.18R と scan 近年 ≈0 の差のうち、記帳規則の差で説明できる部分はどれだけか。
入力: setup_ledger.jsonl（読取のみ）・data/refute_c4_scan_paths_2010_2026.json。scan 無し・MT5 無し・外部通信無し。
"""
import os, json, math, time, collections, datetime as dt
import numpy as np
from scipy.stats import ks_2samp, norm
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT); DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "c25b_feedtol_split_result.md"); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle25 補足 b] 台帳の FEED_TOL 規則 前/後（exit_time 2026-10-24 UTC 0:00 で分割）vs scan — {time.strftime('%Y-%m-%d %H:%M')}")
state = {}; order = []
for line in open(os.path.join(LIVE, "setup_ledger.jsonl"), encoding="utf-8", errors="replace"):
    line = line.strip()
    if not line: continue
    r = json.loads(line); k = r.get("kind")
    if k == "setup" and r.get("id"):
        if r["id"] not in state: order.append(r["id"])
        state[r["id"]] = dict(r)
    elif k == "update" and r.get("target"):
        st = state.setdefault(r["target"], {"id": r["target"]})
        for kk, vv in r.items():
            if kk in ("kind", "logged_at", "target"): continue
            st[kk] = vv
A = []
for sid in order:
    st = state[sid]; ra = st.get("reaccel")
    if not (isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None): continue
    e, sl, tp = float(ra["entry"]), float(ra["sl"]), float(ra["tp"]); risk = abs(e - sl)
    A.append(dict(t=int(ra["entry_time"]), xt=int(ra.get("exit_time") or 0), R=float(ra["R"]), exit=ra.get("exit_reason"), hold=ra.get("hold_bars"),
                  mfe=ra.get("mfe_R"), mae=ra.get("mae_R"), b=abs(tp - e) / risk, side=st.get("side"), jh=st.get("jst_hour")))
cut = int(dt.datetime(2026, 10, 24, tzinfo=dt.timezone.utc).timestamp())
pre = [d for d in A if d["xt"] and d["xt"] < cut]; post = [d for d in A if d["xt"] and d["xt"] >= cut]
tr = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))["trades"]
Y26 = [d for d in tr if d["year"] == 2026]; Yr = [d for d in tr if d["year"] >= 2024]; Y25 = [d for d in tr if d["year"] >= 2025]
def arr(xs, k): return np.array([d[k] for d in xs if d.get(k) is not None], float)
def cond(xs, k, ex): return np.array([d[k] for d in xs if d.get("exit") == ex and d.get(k) is not None], float)
def cnt(xs): c = collections.Counter(d["exit"] for d in xs); return c.get("TP", 0), c.get("SL", 0), c.get("TIME", 0)
def ptest(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; p = (k1 + k2) / (n1 + n2); se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)); z = (p1 - p2) / se
    return p1, p2, z, 2 * (1 - norm.cdf(abs(z)))
def welch(a, b):
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se, se
say(f"- 台帳 closed n={len(A)}・exit_time 欠損 {sum(1 for d in A if not d['xt'])}。pre（決着 <10-24）n={len(pre)}・post（決着 ≥10-24）n={len(post)}")
for nm, X in (("pre", pre), ("post", post)):
    tp_, sl_, tm_ = cnt(X); R = arr(X, "R")
    say(f"- {nm}: 平均R {R.mean():+.4f} (sd {R.std(ddof=1):.3f}, se {R.std(ddof=1)/math.sqrt(len(R)):.3f}) 勝率 {(R>0).mean()*100:.1f}% TP 率 {tp_/(tp_+sl_)*100:.1f}% (TP {tp_}/SL {sl_}/TIME {tm_}) "
        f"hold 中央値 {np.median(arr(X,'hold')):.0f} b 中央値 {np.median(arr(X,'b')):.2f} mfe|SL 中央値 {np.median(cond(X,'mfe','SL')):.2f} mae|TP 中央値 {np.median(cond(X,'mae','TP')):.2f} BUY {sum(1 for d in X if d['side']=='BUY')/len(X)*100:.0f}%")
a, b_, z, p = ptest(cnt(pre)[0], cnt(pre)[0] + cnt(pre)[1], cnt(post)[0], cnt(post)[0] + cnt(post)[1]); say(f"- TP 率 pre − post: {a*100:.1f}% − {b_*100:.1f}% z {z:+.2f} p {p:.4f}")
d, t, se = welch(arr(pre, "R"), arr(post, "R")); say(f"- 平均R pre − post: {d:+.4f} Welch t {t:+.2f}")
say("\n## scan との比較（TP 率 z・平均R Welch t）")
for nmY, Y in (("scan 2026H1", Y26), ("scan 2025-26H1", Y25), ("scan 2024-26H1", Yr)):
    ty, sy, my = cnt(Y); RY = arr(Y, "R")
    for nm, X in (("pre", pre), ("post", post), ("全体", A)):
        tx, sx, mx = cnt(X); a, b_, z, p = ptest(tx, tx + sx, ty, ty + sy); d, t, se = welch(arr(X, "R"), RY)
        say(f"- 台帳 {nm} vs {nmY}: TP 率 {a*100:.1f}% vs {b_*100:.1f}% (z {z:+.2f}, p {p:.4f})；平均R {arr(X,'R').mean():+.4f} vs {RY.mean():+.4f} diff {d:+.4f} (t {t:+.2f}, se {se:.3f})")
say("\n## post（保守規則・同じ記帳）vs scan 2026H1 の 6 統計")
def fam(X, Y, kx, ky):
    hx, mfx, max_, bx = kx; hy, mfy, may, by = ky
    for nm, a_, b__ in (("S1 hold", arr(X, hx), arr(Y, hy)), ("S2 mfe|SL", cond(X, mfx, "SL"), cond(Y, mfy, "SL")), ("S3 mae|TP", cond(X, max_, "TP"), cond(Y, may, "TP")), ("S4 b", arr(X, bx), arr(Y, by))):
        r = ks_2samp(a_, b__); say(f"- {nm} KS D {r.statistic:.3f} p {r.pvalue:.4f}（中央値 {np.median(a_):.2f} vs {np.median(b__):.2f}・n {len(a_)}:{len(b__)}）")
    tx, sx, mx = cnt(X); ty, sy, my = cnt(Y); a, b_, z, p = ptest(tx, tx + sx, ty, ty + sy); say(f"- S5 TP 率 {a*100:.1f}% vs {b_*100:.1f}% z {z:+.2f} p {p:.4f}")
    a, b_, z, p = ptest(mx, len(X), my, len(Y)); say(f"- S6 TIME 率 {a*100:.1f}% vs {b_*100:.1f}% z {z:+.2f} p {p:.4f}")
fam(post, Y26, ("hold", "mfe", "mae", "b"), ("hold", "mfe0", "mae0", "b"))
say("\n## 記帳規則の差の大きさの見積り（記述）: pre の TP/SL 本で『TP 到達が TP−FEED_TOL ぎりぎり』は台帳からは再現できない（M5 が無い）→ 差の上限は TP 率差 × (1+b) で近似")
tp_pre = cnt(pre)[0] / (cnt(pre)[0] + cnt(pre)[1]); tp_post = cnt(post)[0] / (cnt(post)[0] + cnt(post)[1]); bmed = np.median(arr(pre, "b"))
say(f"- TP 率差 {tp_pre-tp_post:+.3f} × (1 + b 中央値 {bmed:.2f}) ≈ {(tp_pre-tp_post)*(1+bmed):+.3f}R/本（pre 平均R {arr(pre,'R').mean():+.3f} − post {arr(post,'R').mean():+.3f} = {arr(pre,'R').mean()-arr(post,'R').mean():+.3f}）")
say("\n## 週別（決着週・JST）TP 率・平均R（レジームか規則かを目で見る）")
wk = collections.defaultdict(list)
for d in A:
    if d["xt"]: wk[(dt.datetime.fromtimestamp(d["xt"], dt.timezone.utc) + dt.timedelta(hours=9)).strftime("%G-W%V")].append(d)
for w in sorted(wk):
    X = wk[w]; tx, sx, mx = cnt(X); say(f"- {w}: n{len(X)} TP 率 {tx/max(tx+sx,1)*100:.0f}% 平均R {arr(X,'R').mean():+.3f} 合計 {arr(X,'R').sum():+.1f}")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
