# -*- coding: utf-8 -*-
"""
[REFUTE c12] 2026-11-06 — 対象: cycle12 (09:50) が残した反証
  「反証 08:30 の DGS10 Δ80 追い風セル（外 2021-26 +0.125R t4.72・近年 +0.187R t4.77）は、
   長い金利符号区間の中では『その区間の side 差』を拾っているだけかもしれない。
   区別には区間固定効果（区間内 side 差を除いた残り）か区間単位の検定が要る。本レベル t4.72 は非独立を無視している。」
cycle12 は研究レーンの次の深化サイクル向けに「区間ブロック bootstrap 95% 下限 >0」を復活/閉鎖条件として残した。
反証レーンはこれを kill test として既存キャッシュで先に実行する（新データ不要・事後セルを育てるのではなく壊しに行く）。

モデル（事前固定）: 本 j が属する金利符号区間 i（FRED DGS10 営業日行の Δ80 の符号の連続区間）。
  R_j = α_i + β·tail_j + γ·SELL_j + ε_j
  区間内では Δ80 の符号が一定なので tail = SELL（正区間）／tail = BUY（負区間）。
  → 正区間内 (SELL−BUY) = β+γ、負区間内 (BUY−SELL) = β−γ。β = (TH_pos+TH_neg)/2、γ = (TH_pos−TH_neg)/2。
  β が「金利追い風」の効果、γ が「外窓では一般に SELL（or BUY）が良い」という側の効果。
  生の pooled tail−head は β と γ（正区間の比率 66% で重み付き）と区間水準差の混合。

Q0 再現: 08:30 B5 名目 DGS10 N=80: 在 +0.0307 (t1.60)／外 +0.1251 (t4.72)／近年 +0.1867 (t4.77)。
Q1 区間構造: 窓ごとの区間数・本数分布・上位 5 区間の本数シェア・Kish 有効区間数・区間内 side 比。
Q2 分解: TH_pos・TH_neg・β・γ（pooled, Welch）。
Q3 固定効果回帰（within 変換・区間クラスタ頑健 SE）: (a) 区間FE のみ（β_FE）、(b) 区間FE + SELL 主効果（β_FE+side・**主統計量**）、
    (c) 区間FE + SELL×年（側の効果が年で変わっても良い・最も厳しい）、(d) 対照: 年FE + SELL。
Q4 区間ブロック bootstrap（区間を復元抽出・2000 回）: β_FE+side の 95% CI 下限（cycle12 の条件）。感度: 四半期ブロック。
Q5 置換帰無: 参照日の k 週循環シフト（08:30 と同機構・1000 回）で β_FE+side の t を再計算 → p。
Q6 質量区間 vs またぎ区間: 区間長 ≥20 営業日の区間だけ／<20 だけで β。区間内 side 差を区間ごとに印字（外・本数上位 10）。
複製: DFII10 Δ80（実質）で Q2〜Q4。在 2010-20・近年 2024-26 も同じ統計を記述（在は edge 判定に使わない・D2）。

判定規則（事前固定・外 2021-26 の β_FE+side について）:
  broken   = 区間 bootstrap 95% 下限 ≤ 0、または 置換 p ≥ 0.05、または β_FE+side < 0.5×生の +0.125（効果の過半が側/区間の混同）。
  survived = 下限 >0 ∧ 置換 p <0.05 ∧ β_FE+side ≥ 0.5×生 ∧ 近年 β_FE+side 同符号。
  inconclusive = それ以外。
結合規則は cycle10/反証 08:30/cycle12 と同一（avail=(JST−7h).date−1・asof ≤10 日）。入力は既存キャッシュのみ。seed 20261106。
"""
import os, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c12_interval.md")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c12] 金利符号区間の固定効果で DGS10 Δ80 追い風セルを叩く — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c12_interval.py)")

X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv")).sort_values("entry_time").reset_index(drop=True)
X["ts_jst"] = pd.to_datetime(X["entry_time"], unit="s") + pd.Timedelta(hours=9)
X["avail"] = (X["ts_jst"] - pd.Timedelta(hours=7)).dt.normalize() - pd.Timedelta(days=1)
X["quarter"] = X["ts_jst"].dt.to_period("Q").astype(str)
SGN = np.where(X["side"] == "BUY", 1.0, -1.0); R = X["R"].to_numpy(); N = len(X)
SELL = (SGN < 0).astype(float); YEAR = X["year"].to_numpy(); WK = X["wall_kind"].to_numpy()
AVAIL = X["avail"].to_numpy().astype("datetime64[D]").astype(np.int64)
NH = 80
say(f"- 本 {N}（closed 全本・TIME 含む）、entry {X['ts_jst'].min().date()}〜{X['ts_jst'].max().date()} JST（⑩）")

def load(sid):
    m = pd.read_csv(os.path.join(MAC, f"{sid}.csv")); m.columns = ["date", "v"]
    m["v"] = pd.to_numeric(m["v"], errors="coerce"); m = m.dropna().copy(); m["date"] = pd.to_datetime(m["date"]); m = m.sort_values("date").reset_index(drop=True)
    v = m["v"].to_numpy(); D = np.full(len(v), np.nan); D[NH:] = v[NH:] - v[:-NH]
    sg = np.sign(D); # 0 は直前の符号を引き継ぐ（区間を切らない）
    for k in range(1, len(sg)):
        if sg[k] == 0 and np.isfinite(sg[k - 1]): sg[k] = sg[k - 1]
    iv = np.full(len(v), -1); cur = -1
    for k in range(len(v)):
        if not np.isfinite(sg[k]): continue
        if k == 0 or not np.isfinite(sg[k - 1]) or sg[k] != sg[k - 1]: cur += 1
        iv[k] = cur
    say(f"- FRED {sid}: {len(m)} 行 {m['date'].iloc[0].date()}〜{m['date'].iloc[-1].date()}、Δ{NH} 定義行 {np.isfinite(D).sum()}、符号区間 {cur+1}")
    return dict(d=m["date"].to_numpy().astype("datetime64[D]").astype(np.int64), D=D, iv=iv, dates=m["date"].to_numpy())
MD = {sid: load(sid) for sid in ("DGS10", "DFII10")}

def feats(sid, ref, tol=10):
    d = MD[sid]["d"]; i = np.searchsorted(d, ref, side="right") - 1; ok = (i >= 0) & ((ref - d[np.clip(i, 0, None)]) <= tol)
    ii = np.clip(i, 0, len(d) - 1); F = MD[sid]["D"][ii].copy(); IV = MD[sid]["iv"][ii].copy(); F[~ok] = np.nan; IV[~ok] = -1
    IV[~np.isfinite(F)] = -1; return F, IV

W = {"在2010-20": YEAR <= 2020, "外2021-26": YEAR >= 2021, "近年2024-26": YEAR >= 2024}
def welch(a, b):
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, (d / se if se > 0 else np.nan), se
def ols_cluster(y, Z, cl):
    """y ~ Z（定数なし・within 変換済み想定）クラスタ頑健 SE。return beta, se"""
    ZtZi = np.linalg.pinv(Z.T @ Z); beta = ZtZi @ Z.T @ y; e = y - Z @ beta
    meat = np.zeros((Z.shape[1], Z.shape[1])); G = 0
    for c in np.unique(cl):
        idx = cl == c; s = Z[idx].T @ e[idx]; meat += np.outer(s, s); G += 1
    V = ZtZi @ meat @ ZtZi * (G / max(G - 1, 1)); return beta, np.sqrt(np.diag(V)), G
def within(v, g):
    """グループ平均を引く"""
    df = pd.DataFrame({"v": v, "g": g}); return (df["v"] - df.groupby("g")["v"].transform("mean")).to_numpy()
def fe_reg(mask, tail, iv, side_ctl="const", group=None):
    """区間FE（group）＋ tail（＋ side 主効果）。side_ctl: none / const / year"""
    g = iv if group is None else group
    m = mask & (g != -1) if group is None else mask & (g != "-1")
    y = within(R[m], g[m]); cols = [within(tail[m].astype(float), g[m])]
    if side_ctl == "const": cols.append(within(SELL[m], g[m]))
    elif side_ctl == "year":
        for yv in np.unique(YEAR[m]): cols.append(within(SELL[m] * (YEAR[m] == yv), g[m]))
    Z = np.column_stack(cols); beta, se, G = ols_cluster(y, Z, g[m])
    return dict(b=beta[0], se=se[0], t=beta[0] / se[0] if se[0] > 0 else np.nan, G=G, n=int(m.sum()))
def fmt(r): return f"{r['b']:+.4f} (t{r['t']:+.2f}, 区間 {r['G']}, n{r['n']})"

for sid in ("DGS10", "DFII10"):
    F, IV = feats(sid, AVAIL); ok = np.isfinite(F) & (IV >= 0); tail = ok & ((SGN * np.sign(F) * -1) > 0); pos = F > 0
    IVs = np.where(ok, IV, -1)
    say(f"\n# ===== {sid} Δ{NH} =====")
    say("\n## Q0 再現（生の pooled tail−head・Welch）")
    raw = {}
    for wn, wm in W.items():
        m = wm & ok; d, t, se = welch(R[m & tail], R[m & ~tail]); raw[wn] = d
        say(f"- {wn}: {d:+.4f} (t{t:+.2f}, n{(m&tail).sum()}:{(m&~tail).sum()})  正区間本比率 {pos[m].mean():.2f}  SELL 比 {SELL[m].mean():.2f}")

    say("\n## Q1 区間構造（本が属する区間）")
    for wn, wm in W.items():
        m = wm & ok; ivs = IVs[m]; cnt = pd.Series(ivs).value_counts(); top5 = cnt.head(5).sum() / cnt.sum(); kish = cnt.sum() ** 2 / (cnt ** 2).sum()
        both = sum(1 for i_ in cnt.index if (SELL[m][ivs == i_].sum() >= 5) and ((1 - SELL[m][ivs == i_]).sum() >= 5))
        say(f"- {wn}: 区間 {len(cnt)}（両側 n≥5 の区間 {both}）、本/区間 中央値 {cnt.median():.0f}・最大 {cnt.max()}、上位5区間の本シェア {top5:.2f}、Kish 有効区間数 {kish:.1f}、"
            f"区間長(本加重・営業日) 中央値 {np.median([ (MD[sid]['iv']==i_).sum() for i_ in ivs ]):.0f}")

    say("\n## Q2 分解 TH_pos（正区間内 SELL−BUY）・TH_neg（負区間内 BUY−SELL）→ β=(pos+neg)/2・γ=(pos−neg)/2")
    for wn, wm in W.items():
        m = wm & ok; mp = m & pos; mn = m & ~pos
        dp, tp, sp = welch(R[mp & (SELL > 0)], R[mp & (SELL == 0)]); dn, tn, sn = welch(R[mn & (SELL == 0)], R[mn & (SELL > 0)])
        beta = (dp + dn) / 2; gam = (dp - dn) / 2; seb = math.sqrt(sp ** 2 + sn ** 2) / 2 if np.isfinite(sp) and np.isfinite(sn) else np.nan
        say(f"- {wn}: TH_pos {dp:+.4f} (t{tp:+.2f}, n{mp.sum()}) / TH_neg {dn:+.4f} (t{tn:+.2f}, n{mn.sum()}) → **β {beta:+.4f} (t{beta/seb:+.2f})** γ(SELL 優位) {gam:+.4f} (t{gam/seb:+.2f})")

    say("\n## Q3 固定効果回帰（within・区間クラスタ頑健 SE）")
    res = {}
    for wn, wm in W.items():
        m = wm & ok
        a = fe_reg(m, tail, IVs, side_ctl="none"); b = fe_reg(m, tail, IVs, side_ctl="const"); c = fe_reg(m, tail, IVs, side_ctl="year")
        yr = YEAR.astype(str); d = fe_reg(m, tail, IVs, side_ctl="const", group=yr)
        q = X["quarter"].to_numpy(); e = fe_reg(m, tail, IVs, side_ctl="const", group=q)
        res[wn] = b
        say(f"- {wn}: (a) 区間FE のみ {fmt(a)} / **(b) 区間FE+SELL {fmt(b)}** / (c) 区間FE+SELL×年 {fmt(c)} / (d) 年FE+SELL {fmt(d)} / (e) 四半期FE+SELL {fmt(e)}")

    say("\n## Q4 区間ブロック bootstrap（区間を復元抽出・2000 回）: β_FE+side の 95% CI")
    NB = 2000; boot = {}
    for wn, wm in W.items():
        m = wm & ok; ids = np.unique(IVs[m]); idx_by = {i_: np.flatnonzero(m & (IVs == i_)) for i_ in ids}
        bs = np.full(NB, np.nan); tb = time.time()
        for bb in range(NB):
            pick = rng.choice(ids, size=len(ids), replace=True)
            rows = np.concatenate([idx_by[i_] for i_ in pick]); gid = np.concatenate([np.full(len(idx_by[i_]), k) for k, i_ in enumerate(pick)])
            y = within(R[rows], gid); Z = np.column_stack([within(tail[rows].astype(float), gid), within(SELL[rows], gid)])
            beta = np.linalg.pinv(Z.T @ Z) @ Z.T @ y; bs[bb] = beta[0]
        lo, hi = np.nanquantile(bs, [0.025, 0.975]); boot[wn] = (lo, hi, (bs <= 0).mean())
        say(f"- {wn}: β_FE+side 点 {res[wn]['b']:+.4f}、bootstrap 95% CI [{lo:+.4f}, {hi:+.4f}]、P(β≤0) {(bs<=0).mean():.3f}（{time.time()-tb:.0f} s）")
    # 感度: 四半期ブロック bootstrap（区間でなく暦四半期を抽出・FE は区間のまま）
    m = W["外2021-26"] & ok; qs = X["quarter"].to_numpy(); qids = np.unique(qs[m]); idx_q = {q_: np.flatnonzero(m & (qs == q_)) for q_ in qids}
    bs = np.full(NB, np.nan)
    for bb in range(NB):
        pick = rng.choice(qids, size=len(qids), replace=True); rows = np.concatenate([idx_q[q_] for q_ in pick])
        gid = np.concatenate([np.full(len(idx_q[q_]), k) for k, q_ in enumerate(pick)])
        g2 = gid * 100000 + IVs[rows]  # 四半期×区間 を FE 単位
        y = within(R[rows], g2); Z = np.column_stack([within(tail[rows].astype(float), g2), within(SELL[rows], g2)])
        beta = np.linalg.pinv(Z.T @ Z) @ Z.T @ y; bs[bb] = beta[0]
    say(f"- 感度 外: 四半期ブロック抽出（FE=四半期×区間）95% CI [{np.nanquantile(bs,0.025):+.4f}, {np.nanquantile(bs,0.975):+.4f}]、P(β≤0) {(bs<=0).mean():.3f}")

    say("\n## Q5 置換帰無（参照日 k 週循環シフト・1000 回）: 外 β_FE+side の t")
    lo_d = pd.Timestamp("2011-01-03"); hi_d = pd.Timestamp("2026-06-26"); span_w = (hi_d - lo_d).days // 7
    lo_i = int(lo_d.to_datetime64().astype("datetime64[D]").astype(np.int64)); base_off = AVAIL - lo_i
    NP = 1000; nt = np.full((NP, 3), np.nan); nb = np.full((NP, 3), np.nan); tp_ = time.time()
    for p in range(NP):
        k = int(rng.integers(8, span_w - 8)); sh = lo_i + (base_off + 7 * k) % (span_w * 7); Fp, IVp = feats(sid, sh)
        okp = np.isfinite(Fp) & (IVp >= 0); tailp = okp & ((SGN * np.sign(Fp) * -1) > 0); IVps = np.where(okp, IVp, -1)
        for j, (wn, wm) in enumerate(W.items()):
            r = fe_reg(wm & okp, tailp, IVps, side_ctl="const"); nt[p, j] = r["t"]; nb[p, j] = r["b"]
    for j, wn in enumerate(W):
        ot = res[wn]["t"]; say(f"- {wn}: 観測 t {ot:+.2f} → 帰無 sd {np.nanstd(nt[:,j]):.2f}・95%点|t| {np.nanquantile(np.abs(nt[:,j]),0.95):.2f}、**両側 p {(np.abs(nt[:,j])>=abs(ot)).mean():.3f}**、β 帰無 sd {np.nanstd(nb[:,j]):.4f}")
    say(f"  （{time.time()-tp_:.0f} s）")
    perm_p = (np.abs(nt[:, 1]) >= abs(res["外2021-26"]["t"])).mean()

    say("\n## Q6 質量区間（長さ ≥20 営業日）vs またぎ区間（<20）・外の区間別 side 差")
    ivlen = np.array([(MD[sid]["iv"] == i_).sum() if i_ >= 0 else 0 for i_ in range(MD[sid]["iv"].max() + 1)])
    LEN = np.where(IVs >= 0, ivlen[np.clip(IVs, 0, None)], 0)
    for wn, wm in W.items():
        m = wm & ok; rl = fe_reg(m & (LEN >= 20), tail, IVs, "const"); rs = fe_reg(m & (LEN < 20), tail, IVs, "const")
        say(f"- {wn}: 長区間 β_FE+side {fmt(rl)}（本シェア {(m&(LEN>=20)).sum()/m.sum():.2f}） / 短区間 {fmt(rs)}")
    m = W["外2021-26"] & ok; cnt = pd.Series(IVs[m]).value_counts().head(10)
    say("- 外 本数上位 10 区間（開始〜終了・符号・営業日・n BUY:SELL・mean R BUY / SELL・区間内 tail−head）:")
    for i_, c in cnt.items():
        rows_ = MD[sid]["iv"] == i_; d0 = pd.Timestamp(MD[sid]["dates"][rows_][0]).date(); d1 = pd.Timestamp(MD[sid]["dates"][rows_][-1]).date()
        mi = m & (IVs == i_); sgn_i = "+" if pos[mi].mean() > 0.5 else "−"; rb = R[mi & (SELL == 0)]; rs_ = R[mi & (SELL > 0)]
        th = (rs_.mean() - rb.mean()) if sgn_i == "+" else (rb.mean() - rs_.mean())
        say(f"  - {d0}〜{d1} 符号{sgn_i} {rows_.sum():3d}日 n{len(rb)}:{len(rs_)} BUY {rb.mean() if len(rb) else float('nan'):+.3f} / SELL {rs_.mean() if len(rs_) else float('nan'):+.3f} → 区間内 tail−head {th:+.3f}")
    # 区間単位の検定（両側 n≥5 の区間ごとの区間内 tail−head を等重み）
    for wn, wm in W.items():
        m = wm & ok; ths = []
        for i_ in np.unique(IVs[m]):
            mi = m & (IVs == i_); rb = R[mi & (SELL == 0)]; rs_ = R[mi & (SELL > 0)]
            if len(rb) >= 5 and len(rs_) >= 5:
                ths.append((rs_.mean() - rb.mean()) if pos[mi].mean() > 0.5 else (rb.mean() - rs_.mean()))
        ths = np.array(ths)
        if len(ths) >= 3: say(f"- {wn} 区間単位（等重み・両側 n≥5・{len(ths)} 区間）: 平均 {ths.mean():+.4f} (t{ths.mean()/(ths.std(ddof=1)/math.sqrt(len(ths))):+.2f})、正 {int((ths>0).sum())}/{len(ths)}、中央値 {np.median(ths):+.4f}")

    if sid == "DGS10":
        say("\n## 判定（事前固定・外 2021-26・β_FE+side）")
        b = res["外2021-26"]["b"]; lo = boot["外2021-26"][0]; rawo = raw["外2021-26"]; rec = res["近年2024-26"]["b"]
        conds = dict(下限正=lo > 0, 置換p小=perm_p < 0.05, 過半残存=b >= 0.5 * rawo, 近年同符号=np.sign(rec) == np.sign(b) and b > 0)
        if (not conds["下限正"]) or (not conds["置換p小"]) or (not conds["過半残存"]): verdict = "broken"
        elif all(conds.values()): verdict = "survived"
        else: verdict = "inconclusive"
        say(f"- β_FE+side 外 {b:+.4f}（生 {rawo:+.4f} の {b/rawo*100:.0f}%）、bootstrap 下限 {lo:+.4f}、置換 p {perm_p:.3f}、近年 β {rec:+.4f} → 条件 {conds} → **{verdict}**")
        VERDICT = verdict

say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("->", OUT)
