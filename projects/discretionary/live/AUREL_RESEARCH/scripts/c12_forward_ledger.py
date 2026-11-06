# -*- coding: utf-8 -*-
"""
[cycle12 研究レーン] 2026-11-06 — 【深化・レジーム／前向き検証】
反証レーン 02:30 / 08:30 が「研究レーンが事前固定し直すまで触らない」と残した 2 つの残存条件づけを、
scan キャッシュ（2010-01〜2026-06）の**外**にある台帳（setup_ledger.jsonl・再加速 closed・2026-09-15〜）で
前向き 1 回限りに見る。台帳は本番エンジンの前向き紙で、c0〜c10 のどの条件づけ実験にも使われていない＝純粋な新データ。

事前固定（検証前に書く・結果を見てから変えない）:
  H1（金利トレンド・反証 08:30 の提案セル）: DGS10（米 10y 名目・FRED 日次）Δ80 = 80 営業日行前との差。
     tail = (BUY ∧ Δ80<0) ∨ (SELL ∧ Δ80>0)。予測 diff = mean R(tail) − mean R(head) > 0。
     利用可能時刻 = cycle5/10 と同じ: FRED 日付 D は JST D+1 07:00 以降の本のみ（avail=(entry_JST−7h).date−1 日・asof backward・≤10 日）。
     反証 08:30 の外 2021-26 推定 +0.125R（t4.72）・近年 +0.187R が「真」なら台帳でも同符号を予測。
     複製（記述）: DFII10 Δ80（実質）。
  H2（直前 24h 継続・反証 02:30 の残存セル）: ret24h = log c(te) − log c(te−24h)、te = entry_time−300、
     c(te) の鮮度 ≤2h・c(te−24h) は許容 3 日（c8 と同一定義）。A = sign(side)·ret24h > 0。予測 diff = mean R(A) − mean R(¬A) > 0。
     価格は data/bars_m5_merged_1008_1105.json（live /api の M5・2026-10-08 13:50 UTC〜11-05 23:35 UTC）→ 10-09 14:00 UTC 以降の本のみ付与可。
     反証 02:30 の推定 外 +0.078・近年 +0.124・2025-26H1 +0.166。記述: outer 壁のみ（反証の「outer で顕著・mid で無し」）。
  統計: Welch t・建玉日クラスタ t・MDE = 2·se・注入（H1 +0.125R／H2 +0.10R を tail/A 群に加えて t を再計算）。
  判定（Bonferroni 2 セル・一方向）: PASS = 予測符号 ∧ t ≥ 2.0。FAIL（符号反転）= t ≤ −1.5。それ以外 = inconclusive（MDE を添えて記録・
     「無い」とは言わない）。n≈300 では MDE ≈0.25〜0.3R と甘く、反証の点推定 0.08〜0.19R は検出力不足で inconclusive が既定の期待値。
  事前の最重大反証（H1）: 台帳 7 週の窓では Δ80 の符号がほぼ一定 → tail/head が BUY/SELL と一致し、セルは「側の差」に退化する。
     そのため tail×side の 2×2 の n 内訳と、無条件 BUY−SELL を必ず並べ、Δ80 の符号の推移を週別に印字する。
  事前の最重大反証（H2）: 台帳の定義（retest/chase/zone・FEED_TOL 記帳）は scan と違う → 水準は比較しない（diff だけ）。
  受け皿: 本ごとの特徴量を data/c12_forward_features.csv に保存し、台帳が増えた将来サイクルで同じ 2 セルを追記検証できる形にする。
  D2: 水準（台帳の平均R）は edge 判定に使わない。昇格候補ではない（レジーム記述の前向き確認）。入口フィルタの提案はしない。
入力: setup_ledger.jsonl（読取のみ）・data/macro/DGS10.csv・DFII10.csv・data/bars_m5_merged_1008_1105.json。scan 無し・MT5 無し・外部通信無し。
"""
import os, sys, json, math, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
LEDGER = os.path.join(LIVE, "setup_ledger.jsonl"); BARS = os.path.join(DATA, "bars_m5_merged_1008_1105.json")
OUT = os.path.join(DATA, "c12_forward_ledger_result.md"); FEAT = os.path.join(DATA, "c12_forward_features.csv")
t0 = time.time(); L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [cycle12] 台帳 前向き 2 セル（DGS10 Δ80 追い風／直前 24h 継続）— {time.strftime('%Y-%m-%d %H:%M')} (scripts/c12_forward_ledger.py)")

# ---- 台帳（refute_c3_ledger.load_ledger と同じ復元規則）----
state = {}; order = []
with open(LEDGER, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        r = json.loads(line); k = r.get("kind")
        if k == "setup" and r.get("id"):
            sid = r["id"]
            if sid not in state: order.append(sid)
            state[sid] = dict(r)
        elif k == "update" and r.get("target"):
            st = state.setdefault(r["target"], {"id": r["target"]})
            for kk, vv in r.items():
                if kk in ("kind", "logged_at", "target"): continue
                st[kk] = vv
rows = []
for sid in order:
    st = state[sid]; ra = st.get("reaccel")
    if isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None:
        rows.append(dict(id=sid, entry_time=int(ra["entry_time"]), R=float(ra["R"]), side=st.get("side"), wall_kind=st.get("wall_kind"),
                         exit=ra.get("exit_reason"), hold=ra.get("hold_bars"), jh=st.get("jst_hour")))
X = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True); N = len(X)
X["ts_utc"] = pd.to_datetime(X["entry_time"], unit="s"); X["ts_jst"] = X["ts_utc"] + pd.Timedelta(hours=9)
X["day"] = X["ts_jst"].dt.date.astype(str); X["week"] = X["ts_jst"].dt.to_period("W").astype(str)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
R = X["R"].to_numpy(); SGN = np.where(X["side"] == "BUY", 1.0, -1.0); BUY = SGN > 0; WK = X["wall_kind"].to_numpy()
say(f"- 台帳 再加速 closed n={N}、entry {X['ts_jst'].min()} 〜 {X['ts_jst'].max()} JST（scan キャッシュは 2026-06-30 で終了＝全本が外）")
say(f"- gross 平均R {R.mean():+.4f}（水準は使わない・D2）、BUY {BUY.sum()}／SELL {(~BUY).sum()}、outer {(WK=='outer').sum()}／mid {(WK=='mid').sum()}、"
    f"exit TP {(X['exit']=='TP').sum()}／SL {(X['exit']=='SL').sum()}／他 {(~X['exit'].isin(['TP','SL'])).sum()}")

# ---- 統計 ----
def welch(a, b):
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, (d / se if se > 0 else np.nan), se
def cluster_t(y, g, cl):
    """y ~ 1 + g の OLS、建玉日クラスタ頑健 SE で g の t"""
    m = np.isfinite(y); y = y[m]; g = g[m].astype(float); cl = np.asarray(cl)[m]
    if len(y) < 4 or g.sum() < 2 or (1 - g).sum() < 2: return np.nan
    Xm = np.column_stack([np.ones(len(y)), g]); XtX_inv = np.linalg.inv(Xm.T @ Xm); beta = XtX_inv @ Xm.T @ y; e = y - Xm @ beta
    meat = np.zeros((2, 2))
    for c in np.unique(cl):
        idx = cl == c; s = Xm[idx].T @ e[idx]; meat += np.outer(s, s)
    V = XtX_inv @ meat @ XtX_inv; G = len(np.unique(cl)); V *= G / (G - 1)
    return beta[1] / math.sqrt(V[1, 1]) if V[1, 1] > 0 else np.nan
def cell(mask_ok, grp, inject=0.0, label=""):
    ok = mask_ok & np.isfinite(R); a = R[ok & grp].copy(); b = R[ok & ~grp]
    d, t, se = welch(a + inject, b); ct = cluster_t(np.where(grp, R + inject, R)[ok], grp[ok], X["day"].to_numpy()[ok])
    return dict(diff=d, t=t, se=se, cl=ct, n1=len(a), n0=len(b), mde=2 * se if np.isfinite(se) else np.nan, label=label)
def fmt(r): return f"{r['diff']:+.4f} (t{r['t']:+.2f}, 日cl{r['cl']:+.2f}, n{r['n1']}:{r['n0']}, MDE {r['mde']:.3f}R)"

# ---- H1: FRED Δ80 ----
def load_fred(sid, n=80):
    m = pd.read_csv(os.path.join(MAC, f"{sid}.csv")); m.columns = ["date", "v"]; m["v"] = pd.to_numeric(m["v"], errors="coerce")
    m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    v = m["v"].to_numpy(); D = np.full(len(v), np.nan); D[n:] = v[n:] - v[:-n]
    say(f"- FRED {sid}: {len(m)} 行、最終 {m['date'].iloc[-1].date()}、最終値 {v[-1]:.2f}、最終 Δ80 {D[-1]:+.3f}（⑩ 期間印字）")
    return m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), D
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
def feats(d, D, ref, tol=10):
    i = np.searchsorted(d, ref, side="right") - 1; ok = (i >= 0) & ((ref - d[np.clip(i, 0, None)]) <= tol)
    F = D[np.clip(i, 0, len(d) - 1)].copy(); F[~ok] = np.nan; return F
dN, DN = load_fred("DGS10"); dR, DR = load_fred("DFII10")
X["d80_dgs10"] = feats(dN, DN, AVAIL); X["d80_dfii10"] = feats(dR, DR, AVAIL)
d80 = X["d80_dgs10"].to_numpy(); okN = np.isfinite(d80) & (d80 != 0)
tailN = okN & ((SGN * np.sign(d80) * -1) > 0)  # 金利低下×BUY / 金利上昇×SELL
say(f"- H1 付与 {okN.mean()*100:.1f}%、Δ80 の符号: 負 {(d80[okN]<0).mean()*100:.1f}%／正 {(d80[okN]>0).mean()*100:.1f}%、Δ80 範囲 [{np.nanmin(d80):+.3f}, {np.nanmax(d80):+.3f}]")
say("- Δ80 の週別（本加重 中央値・負比率）: " + " | ".join(f"{w[-10:]}: {np.nanmedian(d80[X['week']==w]):+.2f} ({(d80[(X['week']==w)&okN]<0).mean():.2f})" for w in sorted(X["week"].unique())))
ct = pd.crosstab(np.where(tailN, "tail", np.where(okN, "head", "na")), np.where(BUY, "BUY", "SELL"))
say("- 2×2 tail/head × side（事前の最重大反証: 一致していれば側の差に退化）:\n" + ct.to_string())

say("\n## H1 主セル DGS10 Δ80 tail−head（予測 >0）")
r1 = cell(okN, tailN); say(f"- 全本: {fmt(r1)}")
r1i = cell(okN, tailN, inject=0.125); say(f"- 注入 +0.125R（反証 08:30 の外推定）→ t {r1i['t']:+.2f}（日cl {r1i['cl']:+.2f}）")
say(f"- 記述 outer のみ: {fmt(cell(okN & (WK=='outer'), tailN))}／mid のみ: {fmt(cell(okN & (WK=='mid'), tailN))}")
rbs = cell(okN, BUY); say(f"- 混同対照 無条件 BUY−SELL: {fmt(rbs)}")
for s_, m_ in (("BUY 内", BUY), ("SELL 内", ~BUY)):
    rr = cell(okN & m_, tailN); say(f"- 側内 {s_} tail−head: {fmt(rr)}" if min(rr['n1'], rr['n0']) >= 2 else f"- 側内 {s_}: 片群 n<2（tail={rr['n1']}, head={rr['n0']}）＝側と Δ80 が一致")
dR80 = X["d80_dfii10"].to_numpy(); okR = np.isfinite(dR80) & (dR80 != 0); tailR = okR & ((SGN * np.sign(dR80) * -1) > 0)
say(f"- 複製 DFII10 Δ80: {fmt(cell(okR, tailR))}（Δ80 負比率 {(dR80[okR]<0).mean():.2f}）")
# 用量反応（符号付き追い風量 = −SGN·Δ80）
dose = -SGN * d80; m = okN
from scipy.stats import spearmanr
rho, p = spearmanr(dose[m], R[m]); say(f"- 用量反応 Spearman ρ(−side·Δ80, R) {rho:+.3f} (p {p:.3f})")

# ---- H2: ret24h ----
B = json.load(open(BARS, encoding="utf-8"))["bars"]; bts = np.array([b["time"] for b in B], dtype=np.int64); bcl = np.log(np.array([b["close"] for b in B], float))
o = np.argsort(bts); bts = bts[o]; bcl = bcl[o]; bts, ui = np.unique(bts, return_index=True); bcl = bcl[ui]
gap = np.diff(bts); say(f"\n- bars: {len(bts)} 本、{pd.to_datetime(bts[0], unit='s')} 〜 {pd.to_datetime(bts[-1], unit='s')} UTC、5 分格子連続率 {(gap==300).mean()*100:.1f}%、flat 足 {(np.diff(bcl)==0).mean()*100:.1f}%（⑩⑪ 印字・前値埋め無し＝取引足のみ）")
def asof(ts, v, q, tol):
    i = np.searchsorted(ts, q, side="right") - 1; ok = i >= 0; out = np.full(len(q), np.nan); ii = np.clip(i, 0, None)
    age = q - ts[ii]; good = ok & (age <= tol); out[good] = v[ii[good]]; return out
te = X["entry_time"].to_numpy() - 300
c_now = asof(bts, bcl, te, 2 * 3600); c_prev = asof(bts, bcl, te - 86400, 3 * 86400)
X["ret24h"] = c_now - c_prev; ret = X["ret24h"].to_numpy(); okA = np.isfinite(ret) & (ret != 0); A = okA & (SGN * ret > 0)
say(f"- H2 付与 {okA.sum()}/{N} 本（{okA.mean()*100:.1f}%・bars 期間内のみ）。n 内訳 BUY∧同向き {int((A&BUY).sum())}／BUY∧逆 {int((okA&~A&BUY).sum())}／SELL∧同向き {int((A&~BUY).sum())}／SELL∧逆 {int((okA&~A&~BUY).sum())}（符号を目で確認・反証 02:30 の教訓）")
say("\n## H2 主セル 直前 24h 継続 A−¬A（予測 >0）")
r2 = cell(okA, A); say(f"- 付与本: {fmt(r2)}")
r2i = cell(okA, A, inject=0.10); say(f"- 注入 +0.10R → t {r2i['t']:+.2f}（日cl {r2i['cl']:+.2f}）")
say(f"- 記述 outer のみ: {fmt(cell(okA & (WK=='outer'), A))}／mid のみ: {fmt(cell(okA & (WK=='mid'), A))}")
say(f"- 側別 BUY 内: {fmt(cell(okA & BUY, A))}／SELL 内: {fmt(cell(okA & ~BUY, A))}")
say(f"- 混同対照 付与本の無条件 BUY−SELL: {fmt(cell(okA, BUY))}")
rho2, p2 = spearmanr((SGN * ret)[okA], R[okA]); say(f"- 用量反応 Spearman ρ(side·ret24h, R) {rho2:+.3f} (p {p2:.3f})")
# 水平線掃引（記述・反証 02:30 Q3 と同じ）
say("- 水平線掃引（記述・A−¬A の t）: " + " | ".join(
    (lambda H: (lambda cp: (lambda rr, okh: f"{H//3600}h {rr['diff']:+.3f} (t{rr['t']:+.2f}, n{rr['n1']}:{rr['n0']})")(
        cell((okh := np.isfinite(c_now - cp) & ((c_now - cp) != 0)), okh & (SGN * (c_now - cp) > 0)), None))(asof(bts, bcl, te - H, 3 * 86400)))(H)
    for H in (4 * 3600, 8 * 3600, 12 * 3600, 24 * 3600, 48 * 3600)))

# ---- 判定 ----
def judge(r):
    if not np.isfinite(r["t"]): return "n/a"
    if r["diff"] > 0 and r["t"] >= 2.0: return "PASS"
    if r["t"] <= -1.5: return "FAIL（符号反転）"
    return "inconclusive"
say("\n## 判定（事前固定・Bonferroni 2・一方向）")
say(f"- H1 DGS10 Δ80: {judge(r1)}  diff {r1['diff']:+.4f} t{r1['t']:+.2f} MDE {r1['mde']:.3f}R")
say(f"- H2 継続 24h: {judge(r2)}  diff {r2['diff']:+.4f} t{r2['t']:+.2f} MDE {r2['mde']:.3f}R")

# ---- 受け皿 ----
X[["id", "entry_time", "ts_jst", "side", "wall_kind", "exit", "hold", "R", "d80_dgs10", "d80_dfii10", "ret24h"]].to_csv(FEAT, index=False)
say(f"\n- 受け皿 {os.path.relpath(FEAT, ROOT)} に {N} 本を保存（将来サイクルで台帳が増えたら同 2 セルを追記検証）。所要 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
