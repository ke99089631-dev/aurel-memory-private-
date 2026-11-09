# -*- coding: utf-8 -*-
"""
[cycle25 研究レーン] 2026-11-09 — 【深化・path 幾何／前向き検証（backlog ★1「台帳 vs scan の照合」の M5 不要部分）】
台帳（setup_ledger.jsonl・再加速 closed・2026-09-15〜11-09・本番エンジンの前向き紙）と scan キャッシュ
（refute_c4_scan_paths_2010_2026.json・同じ setup_engine._simulate の定義・〜2026-06-30）は時間的に重ならないので
本ごとの突合は M5 延長待ち（needs data）。しかし **path 幾何の分布**（保有本数・SL 本の MFE・TP 本の MAE・b・決着種別の比率）は
台帳が mfe_R/mae_R/hold_bars を本ごとに持つので今すぐ比べられる。幾何が一致すれば「台帳 +0.18R vs scan 近年 ≈0 の差」は
地合い（＋標本ノイズ）側、幾何が違えば本番エンジンの定義差（retest/chase/zone/v1・FEED_TOL 変更 2026-10-24）側に分離できる。

事前固定（検証前に書く・結果を見てから変えない）:
  対象: 台帳 = 最終状態の reaccel が status=closed ∧ R あり（update 行を setup 行に上書き復元・c3/c12 と同じ）。
        scan 近年 = 2024-01〜2026-06（全時間帯・台帳も全時間帯なので揃える）。補助: scan 2026H1（最も近い半年）・jh7-12 同士。
  定義の一致: 台帳 mfe_R/mae_R は建玉足込み（_simulate）＝ scan の mfe0/mae0、hold_bars = hold（exit_k − ie）。b = |tp−entry|/|entry−sl|。
  H_G（幾何の移転）: 6 統計の 2 標本検定 family（Bonferroni 6 → 単セル p<0.0083 で差あり）
     S1 hold（全 closed）KS／S2 mfe0 | exit=SL KS／S3 mae0 | exit=TP KS／S4 b KS／S5 TP 率 = TP/(TP+SL) 2 比率 z／S6 TIME 率 2 比率 z。
     PASS（幾何は移転する）= 6 セルすべて p ≥ 0.0083。FAIL = 1 セルでも p < 0.0083（どの統計かを記録）。
  H_R（水準・D2 近年窓）: 台帳 gross 平均R − scan 2024-26H1 平均R の Welch t。PASS（台帳は scan 近年と区別できる）= t ≥ 2.0。
     予測（事前）: 台帳 n≈320・sd≈1.4 → se≈0.08 → 差 +0.19 でも t≈2 前後＝境界。区別できなければ「台帳の +0.18R は近年 scan の
     標本ノイズの範囲」と記す（D2: 16 年一括は使わない）。
  校正（同じ 6 統計を scan 内で）: (a) 隣接レジーム 2021-23 vs 2024-26H1（レジーム間の幾何ドリフトの大きさの参照）、
     (b) プラセボ = 2024-26H1 を無作為 2 分割（seed 固定）→ 帰無では p 一様（min p の期待 ≈ 1/7）。
  陽性対照・MDE: 台帳の S1 に +2 本・S2 に +0.10R・S4 に ×1.1 を注入して KS p<0.0083 になるか（検出できる差の規模）。
  記述（判定に使わない）: risk（USD と 価格比 bp）・risk/atr14（台帳 features.atr14・scan atr）・側/壁種の構成・
     scan の frozen パラメタ（FEED_TOL/MAX_HOLD）と setup_engine.py 現行値の文字列比較（読取のみ・import しない）。
  ★ backlog 3（数秒）: n*(95%) を実測コストで再計算 = net R = R − 0.21 USD/risk と R − 0.0325R（cycle4 実測）。
     iid bootstrap B=4000・grid 25..5000（c3 と同じ）。gross 200／net(0.56) 750 の間のどこか。
  事前の最重大反証: (i) 幾何が一致しても R の差は「地合い」と「標本ノイズ」を分離できない（7 週 n320 の se 0.08R）。
     (ii) 幾何の差が出ても「価格水準（2026 年秋 ≈4000 USD vs 2024-26 平均 ≈2800）による risk/b の尺度変化」と「定義差」は
     KS では区別できない → risk を bp 化・b は無次元なので b と TP 率を主に読む。(iii) 台帳の 1 行目〜10-24 は旧 FEED_TOL 規則
     の可能性（2026-10-24 会長GO で保守側へ）→ 台帳を 10-24 前後で 2 分し S5 TP 率を併記。
  D2: scan 2010-20 は使わない（幾何の参照にも不要）。昇格候補・入口/出口の提案ではない。
入力: setup_ledger.jsonl（読取のみ）・data/refute_c4_scan_paths_2010_2026.json・setup_engine.py（定数の文字列読取のみ）。
scan 無し・M5 読込なし・MT5 無し・外部通信無し。出力 data/c25_ledger_vs_scan_geometry_result.md・data/c25_run.log。
"""
import os, re, sys, json, math, time, collections
import numpy as np
from scipy.stats import ks_2samp, norm

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "data")
LEDGER = os.path.join(LIVE, "setup_ledger.jsonl"); CACHE = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
ENGINE = os.path.join(LIVE, "setup_engine.py")
OUT = os.path.join(DATA, "c25_ledger_vs_scan_geometry_result.md")
rng = np.random.default_rng(20261109); t0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle25] 台帳 vs scan の path 幾何の照合（M5 不要部分）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c25_ledger_vs_scan_geometry.py)")

# ---- 台帳復元（c3/c12 と同じ規則）----
state = {}; order = []
with open(LEDGER, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
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
    if risk <= 0: continue
    feat = st.get("features") if isinstance(st.get("features"), dict) else {}
    A.append(dict(t=int(ra["entry_time"]), R=float(ra["R"]), exit=ra.get("exit_reason"), hold=ra.get("hold_bars"),
                  mfe=ra.get("mfe_R"), mae=ra.get("mae_R"), risk=risk, b=abs(tp - e) / risk, entry=e,
                  jh=st.get("jst_hour"), side=st.get("side"), wk=st.get("wall_kind"), atr=feat.get("atr14")))
A.sort(key=lambda d: d["t"])
import datetime as dt
f_ = lambda x: dt.datetime.fromtimestamp(int(x), dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
say(f"- 台帳 再加速 closed n={len(A)}、entry {f_(A[0]['t'])} 〜 {f_(A[-1]['t'])} UTC。exit {dict(collections.Counter(d['exit'] for d in A))}、"
    f"side {dict(collections.Counter(d['side'] for d in A))}、wall {dict(collections.Counter(d['wk'] for d in A))}、jh7-12 {sum(1 for d in A if d['jh'] is not None and 7 <= d['jh'] <= 12)}")

# ---- scan キャッシュ ----
J = json.load(open(CACHE, encoding="utf-8")); tr = J["trades"]
say(f"- scan キャッシュ generated {J.get('generated')}・bars {J.get('bars')}・frozen {J.get('frozen')}・trades {len(tr)}（{f_(min(t['entry_time'] for t in tr))} 〜 {f_(max(t['entry_time'] for t in tr))} UTC・⑩）")
# setup_engine 現行定数（文字列のみ・import しない）
src = open(ENGINE, encoding="utf-8", errors="replace").read()
cur = {k: (re.search(rf"^{k}\s*=\s*([^\n#]+)", src, re.M).group(1).strip() if re.search(rf"^{k}\s*=\s*([^\n#]+)", src, re.M) else "n/a") for k in ("FEED_TOL", "MAX_HOLD", "MIN_SL_W", "TRIG_SPREAD")}
say(f"- setup_engine.py 現行定数（読取のみ）: {cur} vs scan frozen {J.get('frozen')}")

def sel(lo, hi, prod=None):
    xs = [d for d in tr if lo <= d["year"] <= hi]
    if prod: xs = [d for d in xs if 7 <= d["jh"] <= 12]
    return xs
def arr(xs, key): return np.array([d[key] for d in xs if d.get(key) is not None], float)
def cond(xs, key, ex): return np.array([d[key] for d in xs if d.get("exit") == ex and d.get(key) is not None], float)
def ptest(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; p = (k1 + k2) / (n1 + n2); se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se > 0 else np.nan; return p1, p2, z, 2 * (1 - norm.cdf(abs(z)))
def exit_counts(xs):
    c = collections.Counter(d["exit"] for d in xs); return c.get("TP", 0), c.get("SL", 0), c.get("TIME", 0)

def family(name, X, Y, keyX, keyY, verbose=True):
    """X, Y: 本のリスト。keyX/keyY: (hold, mfe, mae) のキー名。6 統計の p を返す。"""
    hx, mfx, max_, bx = keyX; hy, mfy, may, by = keyY
    res = {}
    def ks(a, b):
        if len(a) < 5 or len(b) < 5: return np.nan, np.nan, np.nan
        r = ks_2samp(a, b); return r.statistic, r.pvalue, (np.median(a), np.median(b))
    s1 = ks(arr(X, hx), arr(Y, hy)); s2 = ks(cond(X, mfx, "SL"), cond(Y, mfy, "SL")); s3 = ks(cond(X, max_, "TP"), cond(Y, may, "TP")); s4 = ks(arr(X, bx), arr(Y, by))
    tx, sx, mx = exit_counts(X); ty, sy, my = exit_counts(Y)
    s5 = ptest(tx, tx + sx, ty, ty + sy); s6 = ptest(mx, len(X), my, len(Y))
    res = dict(S1=s1[1], S2=s2[1], S3=s3[1], S4=s4[1], S5=s5[3], S6=s6[3])
    if verbose:
        say(f"\n### {name}  nX={len(X)} nY={len(Y)}")
        say(f"- S1 hold KS D {s1[0]:.3f} p {s1[1]:.4f}（中央値 {s1[2][0]:.0f} vs {s1[2][1]:.0f} 本）")
        say(f"- S2 mfe|SL KS D {s2[0]:.3f} p {s2[1]:.4f}（中央値 {s2[2][0]:.2f} vs {s2[2][1]:.2f} R・n {len(cond(X, mfx, 'SL'))}:{len(cond(Y, mfy, 'SL'))}）")
        say(f"- S3 mae|TP KS D {s3[0]:.3f} p {s3[1]:.4f}（中央値 {s3[2][0]:.2f} vs {s3[2][1]:.2f} R・n {len(cond(X, max_, 'TP'))}:{len(cond(Y, may, 'TP'))}）")
        say(f"- S4 b KS D {s4[0]:.3f} p {s4[1]:.4f}（中央値 {s4[2][0]:.2f} vs {s4[2][1]:.2f}）")
        say(f"- S5 TP 率 {s5[0]*100:.1f}% vs {s5[1]*100:.1f}%  z {s5[2]:+.2f} p {s5[3]:.4f}")
        say(f"- S6 TIME 率 {s6[0]*100:.1f}% vs {s6[1]*100:.1f}%  z {s6[2]:+.2f} p {s6[3]:.4f}（TIME {mx}:{my}）")
        bad = [k for k, v in res.items() if np.isfinite(v) and v < 0.05 / 6]
        say(f"- min p {min(v for v in res.values() if np.isfinite(v)):.4f} → Bonferroni(6) 差あり: {bad if bad else 'なし'}")
    return res

KA = ("hold", "mfe", "mae", "b"); KS_ = ("hold", "mfe0", "mae0", "b")
Y_recent = sel(2024, 2026); Y_26 = [d for d in tr if d["year"] == 2026]; Y_2123 = sel(2021, 2023)
say("\n## H_G 幾何の移転（主: 台帳 vs scan 2024-26H1・全時間帯）")
main = family("主セル 台帳 vs scan 2024-26H1", A, Y_recent, KA, KS_)
aux26 = family("補助 台帳 vs scan 2026H1", A, Y_26, KA, KS_)
Ap = [d for d in A if d["jh"] is not None and 7 <= d["jh"] <= 12]
auxp = family("補助 台帳 jh7-12 vs scan 2024-26H1 jh7-12", Ap, sel(2024, 2026, prod=True), KA, KS_)

say("\n## 校正（scan 内・同じ 6 統計）")
cal = family("(a) 隣接レジーム scan 2021-23 vs 2024-26H1", Y_2123, Y_recent, KS_, KS_)
idx = rng.permutation(len(Y_recent)); h = len(idx) // 2
plc = family("(b) プラセボ scan 2024-26H1 無作為 2 分割", [Y_recent[i] for i in idx[:h]], [Y_recent[i] for i in idx[h:]], KS_, KS_)
# プラセボを台帳サイズ n=len(A) で 200 回 → min p の分布
mins = []
for _ in range(200):
    ii = rng.permutation(len(Y_recent)); X_ = [Y_recent[i] for i in ii[:len(A)]]; Y_ = [Y_recent[i] for i in ii[len(A):]]
    r = family("", X_, Y_, KS_, KS_, verbose=False); mins.append(min(v for v in r.values() if np.isfinite(v)))
mins = np.array(mins)
say(f"- (b') プラセボ 200 回（scan 2024-26H1 から台帳サイズ n={len(A)} を無作為抽出 vs 残り）: min p の 5% 点 {np.quantile(mins, 0.05):.4f}・中央値 {np.median(mins):.3f}・P(min p<0.0083) {(mins < 0.05/6).mean():.3f}（帰無での偽 FAIL 率）")

say("\n## 陽性対照・MDE（台帳側に注入して主セルの KS p）")
def inj(key, fn, ex=None):
    X_ = [dict(d) for d in A]
    for d in X_:
        if d.get(key) is not None and (ex is None or d["exit"] == ex): d[key] = fn(d[key])
    return X_
r = family("", inj("hold", lambda v: v + 2), Y_recent, KA, KS_, verbose=False); say(f"- S1 hold +2 本 → p {r['S1']:.4f}")
r = family("", inj("hold", lambda v: v + 1), Y_recent, KA, KS_, verbose=False); say(f"- S1 hold +1 本 → p {r['S1']:.4f}")
r = family("", inj("mfe", lambda v: v + 0.10, "SL"), Y_recent, KA, KS_, verbose=False); say(f"- S2 mfe|SL +0.10R → p {r['S2']:.4f}")
r = family("", inj("mfe", lambda v: v + 0.05, "SL"), Y_recent, KA, KS_, verbose=False); say(f"- S2 mfe|SL +0.05R → p {r['S2']:.4f}")
r = family("", inj("b", lambda v: v * 1.10), Y_recent, KA, KS_, verbose=False); say(f"- S4 b ×1.10 → p {r['S4']:.4f}")
r = family("", inj("b", lambda v: v * 1.05), Y_recent, KA, KS_, verbose=False); say(f"- S4 b ×1.05 → p {r['S4']:.4f}")

say("\n## H_R 水準（D2 近年窓・gross）")
RA = arr(A, "R")
def welch(a, b):
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se, se
for nm, Y in (("scan 2024-26H1", Y_recent), ("scan 2026H1", Y_26), ("scan 2025-26H1", sel(2025, 2026))):
    RY = arr(Y, "R"); d, t, se = welch(RA, RY)
    say(f"- 台帳 {RA.mean():+.4f} (n{len(RA)}, sd {RA.std(ddof=1):.3f}) − {nm} {RY.mean():+.4f} (n{len(RY)}) = {d:+.4f}  Welch t {t:+.2f}  se {se:.3f}  勝率 {(RA>0).mean()*100:.1f}% vs {(RY>0).mean()*100:.1f}%")
RYp = arr(sel(2024, 2026, prod=True), "R"); RAp = arr(Ap, "R")
if len(RAp) > 5:
    d, t, se = welch(RAp, RYp); say(f"- jh7-12 同士: 台帳 {RAp.mean():+.4f} (n{len(RAp)}) − scan 2024-26H1 jh7-12 {RYp.mean():+.4f} (n{len(RYp)}) = {d:+.4f}  t {t:+.2f}")
# 台帳 10-24 前後（FEED_TOL 変更日）
cut = int(dt.datetime(2026, 10, 24, tzinfo=dt.timezone.utc).timestamp())
A1 = [d for d in A if d["t"] < cut]; A2 = [d for d in A if d["t"] >= cut]
for nm, X in (("台帳 〜10-23", A1), ("台帳 10-24〜", A2)):
    tx, sx, mx = exit_counts(X); R_ = arr(X, "R")
    say(f"- {nm}: n{len(X)} 平均R {R_.mean():+.4f} TP 率 {tx/max(tx+sx,1)*100:.1f}% TIME {mx} hold 中央値 {np.median(arr(X,'hold')):.0f} b 中央値 {np.median(arr(X,'b')):.2f} mfe|SL 中央値 {np.median(cond(X,'mfe','SL')) if len(cond(X,'mfe','SL')) else float('nan'):.2f}")

say("\n## 記述（判定に使わない）")
for nm, X, kr in (("台帳", A, "risk"), ("scan 2024-26H1", Y_recent, "risk"), ("scan 2026H1", Y_26, "risk")):
    rk = arr(X, kr)
    if nm == "台帳":
        px = arr(X, "entry"); bp = rk / px * 1e4; at = np.array([d["atr"] if d.get("atr") else np.nan for d in X], float); ra_ = rk / at
        say(f"- {nm} risk 中央値 {np.median(rk):.2f} USD・価格比 {np.median(bp):.1f} bp（価格中央値 {np.median(px):.0f}）・risk/atr14 中央値 {np.nanmedian(ra_):.2f}（atr あり {np.isfinite(ra_).sum()}）")
    else:
        at = np.array([d["atr"] if d.get("atr") else np.nan for d in X], float); ra_ = rk / at
        say(f"- {nm} risk 中央値 {np.median(rk):.2f} USD・risk/atr 中央値 {np.nanmedian(ra_):.2f}・年別 risk 中央値 " + " ".join(f"{y}:{np.median(arr([d for d in X if d['year']==y],'risk')):.2f}" for y in sorted(set(d['year'] for d in X))))
say(f"- 側/壁の構成: 台帳 BUY {sum(1 for d in A if d['side']=='BUY')/len(A)*100:.0f}%・outer {sum(1 for d in A if d['wk']=='outer')/len(A)*100:.0f}%；scan 2024-26H1 BUY {sum(1 for d in Y_recent if d['side']=='BUY')/len(Y_recent)*100:.0f}%・outer {sum(1 for d in Y_recent if d['wall_kind']=='outer')/len(Y_recent)*100:.0f}%")
# hold 分布の形（分位）
for nm, X, kh in (("台帳", A, "hold"), ("scan 2024-26H1", Y_recent, "hold")):
    hh = arr(X, kh); say(f"- {nm} hold 分位 p10/25/50/75/90/max = " + "/".join(f"{np.quantile(hh,q):.0f}" for q in (0.1,0.25,0.5,0.75,0.9)) + f"/{hh.max():.0f}・hold≥48 {(hh>=48).mean()*100:.1f}%・hold=0 {(hh==0).mean()*100:.1f}%")
for nm, X, km in (("台帳", A, "mfe"), ("scan 2024-26H1", Y_recent, "mfe0")):
    m = cond(X, km, "SL"); say(f"- {nm} SL 本の mfe 分位 p25/50/75/90 = " + "/".join(f"{np.quantile(m,q):.2f}" for q in (0.25,0.5,0.75,0.9)) + f"・mfe≥0.5R の SL 本 {(m>=0.5).mean()*100:.1f}%")
for nm, X, km in (("台帳", A, "mae"), ("scan 2024-26H1", Y_recent, "mae0")):
    m = cond(X, km, "TP"); say(f"- {nm} TP 本の mae 分位 p25/50/75/90 = " + "/".join(f"{np.quantile(m,q):.2f}" for q in (0.25,0.5,0.75,0.9)) + f"・mae≥0.5R の TP 本 {(m>=0.5).mean()*100:.1f}%")

say("\n## ★ backlog 3: n*(95%) を実測コストで再計算（台帳 gross・iid bootstrap B=4000・c3 と同じ grid）")
GRID = [25, 50, 75, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 3000, 5000]
def nstar(R):
    R = np.asarray(R, float); m, sd = R.mean(), R.std(ddof=1); found = None; rows = []
    for n in GRID:
        B = 4000 if n <= 1000 else 1500; p = float((rng.choice(R, size=(B, n), replace=True).sum(axis=1) > 0).mean()); rows.append((n, p))
        if found is None and p >= 0.95: found = n
    return m, sd, (1.645 * sd / m) ** 2 if m > 0 else float("inf"), found, rows
risk = arr(A, "risk")
for nm, Rn in (("gross", RA), ("net −0.21 USD/risk（spread 0.16＋slip 中央値・cycle4）", RA - 0.21 / risk), ("net −0.0325R（cycle4 実コスト 26%）", RA - 0.0325),
               ("net −0.56 USD/risk（旧仮定・c3）", RA - 0.56 / risk)):
    m, sd, ap, fd, rows = nstar(Rn)
    say(f"- {nm}: 平均 {m:+.4f} sd {sd:.3f} 合計 {Rn.sum():+.1f} → n*(95%) {fd if fd else '>5000'}（解析近似 {ap:.0f}）  P(ΣR>0): " + " ".join(f"{n}:{p:.2f}" for n, p in rows[:10]))
say(f"- コスト中央値 0.21/risk = {np.median(0.21/risk):.4f}R（risk 中央値 {np.median(risk):.2f} USD）")

say("\n## 判定（事前固定）")
bad = [k for k, v in main.items() if np.isfinite(v) and v < 0.05 / 6]
say(f"- H_G 主セル: {'FAIL（幾何に差）: ' + str(bad) if bad else 'PASS（6 統計とも Bonferroni 後に差なし）'}  min p {min(main.values()):.4f}")
bad26 = [k for k, v in aux26.items() if np.isfinite(v) and v < 0.05 / 6]
say(f"- 補助 2026H1: {'差あり ' + str(bad26) if bad26 else '差なし'}  min p {min(aux26.values()):.4f}；jh7-12 同士 min p {min(v for v in auxp.values() if np.isfinite(v)):.4f}")
d, t, se = welch(RA, arr(Y_recent, "R"))
say(f"- H_R: {'PASS（台帳は scan 近年と区別できる）' if t >= 2 else 'FAIL（区別できない＝標本ノイズの範囲）'}  diff {d:+.4f} t {t:+.2f} se {se:.3f}")
say(f"\n所要 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
