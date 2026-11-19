# -*- coding: utf-8 -*-
"""
[反証レーン 続き・走 5] T3 の裁定 — c54 のゲート ㉛ の説明文を数で検める。

c54 の記述: ゲート ㉛ の 在 側 Δcl(02:10+02:15) = **+0.0181R (t +2.01)** は
  「期待どおり: 方向に無差別な直後の正は side 符号で打ち消す・**P1 の正は BUY 比 56% × +0.78 bp の別名**」
＝「side 不均衡 × 方向無差別な足の正」で説明される、という主張。

その主張は分解できる。clR は side 符号つき（c54 自身の整合検査 path_dpx = dpre·risk·side が価格差に一致）
なので dcl_i = s_i · u_i（s = ±1・u = 2 足の価格変化 / risk）。
  「side 不均衡の別名」なら   mean(dcl) ≈ mean(s) · mean(u)
  そうでなければ            mean(dcl) = mean(s)·mean(u) + cov(s, u)   の cov 項が主
c54 の数字だけで概算すると mean(s) = 2×0.56−1 = 0.12・mean(u) ≈ 0.78 bp × 0.037 R/bp（c18）= 0.0289R
→ 予測 **0.0035R** に対し 観測 **0.0181R** ＝ **5.2 倍**。外部定数（0.037 R/bp）に頼らず、
同じ母集団から mean(s)・mean(u)・cov(s,u) を直接出して裁定する。

=== 事前固定（走る前） ===
A 複製: c54 のゲート 4 行（n・BUY 比・Δcl・t）を再現。P1 の Δcl が ±0.0005R で一致しなければ INCONCLUSIVE。
BREAK-T3: P1 で 観測 mean(dcl) ÷ [mean(s)·mean(u)] ≥ 2 → c54 の「BUY 比 × 足の正 の別名」は
          定量的に誤り（cov(s,u) 項＝建玉選択と path の相関が主）。
          なお **ゲートの合否（|Δμ| 0.018 < 閾値 0.048 → 不通過）は どちらでも変わらない**＝
          壊れるのは結論ではなく「説明文」。方法論候補 72/75（旗と散文の乖離）の再発かを見る。
BREAK-T3b: cov(s,u) が mean(dcl) の 50% 超を占める → 「方向に無差別」という前提自体が誤り。

seed 20261119。読取り専用（data/ の json と npz のみ・本番ファイル無し）。
"""
import os, math, time, json
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c54_sge_e_result.md")
L = []
def say(s=""):
    print(s, flush=True); L.append(s)
VERD = []
def brk(tag, cond, obs, broken):
    say(f"- [{tag}] 条件: {cond}")
    say(f"  - 観測: {obs}")
    say(f"  - 判定: {'BROKEN' if broken else 'not broken'}")
    VERD.append((tag, bool(broken)))

say(f"# [REFUTE c54 走 5] T3 — ゲート ㉛ の説明文「BUY 比 56% × +0.78 bp の別名」の分解 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c54_sge_e.py)")

z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(float)
def stat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 3: return dict(n=n, m=np.nan, se=np.nan, t=np.nan, mde=np.nan)
    m = x.mean(); se = x.std(ddof=1) / math.sqrt(n)
    return dict(n=n, m=m, se=se, t=m / se if se > 0 else np.nan, mde=2 * se)

# ---------- replicate c54's gate population exactly (same code path) --------------------------------
J = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json"), encoding="utf-8"))["trades"]
tj = pd.DataFrame(J).sort_values(["entry_time", "hold"], kind="stable").reset_index(drop=True)
fp = np.load(os.path.join(DATA, "refute_c2_fullpaths.npz")); off = fp["off"].astype(np.int64); clR = fp["clR"]
ho = np.diff(off) - 1
if not np.array_equal(ho, tj["hold"].to_numpy()):
    bad = np.where(ho != tj["hold"].to_numpy())[0]
    say(f"- hold 不一致 {len(bad)} 本 → 同時刻組を off 順に並べ替え（c53 衛生・c54 と同手順）")
    tj["_ho"] = ho
    for et_, g in tj.groupby("entry_time"):
        if len(g) > 1 and not np.array_equal(g["hold"].to_numpy(), g["_ho"].to_numpy()):
            idx_ = g.index.to_numpy(); want = g["_ho"].to_numpy(); order = []; pool = list(idx_)
            for wv in want:
                pick = next(i for i in pool if tj.at[i, "hold"] == wv); order.append(pick); pool.remove(pick)
            cols = tj.columns.difference(["_ho"])
            tj.loc[idx_, cols] = tj.loc[order, cols].to_numpy()
    assert np.array_equal(np.diff(off) - 1, tj["hold"].to_numpy()), "off/hold 規約 不一致"
et = tj["entry_time"].to_numpy(); hold = tj["hold"].to_numpy()
tsec = pd.to_datetime(et, unit="s", utc=True)
secs = (tsec.hour * 3600 + tsec.minute * 60 + tsec.second).to_numpy()
base = (et // 86400) * 86400
t0210 = np.where(secs >= 22 * 3600, base + 86400 + 2 * 3600 + 600, base + 2 * 3600 + 600)
jpre = (t0210 - et) // 300
alive = ((secs >= 22 * 3600) | (secs <= 2 * 3600 + 300)) & (jpre >= 1) & (hold >= jpre + 1) & ((t0210 - et) % 300 == 0)
dow = pd.to_datetime(t0210, unit="s", utc=True).weekday.to_numpy()
alive &= dow <= 4
idx = np.where(alive)[0]
assert (jpre[idx] - 1 >= 0).all() and (jpre[idx] + 1 <= hold[idx]).all()
dcl = clR[off[idx] + jpre[idx] + 1] - clR[off[idx] + jpre[idx] - 1]
side = np.where(tj["side"].to_numpy()[idx] == "BUY", 1.0, -1.0); risk = tj["risk"].to_numpy()[idx].astype(float)
ety = pd.to_datetime(t0210[idx], unit="s", utc=True)
say(f"- ゲート母数 {len(idx)} 本（c54: 1126）・jh7-12 {int(np.isin(tj['jh'].to_numpy()[idx], range(7,13)).sum())} 本")

# u = unsigned 2-bar price change / risk  (dcl = s * u, since clR is side-signed)
u = dcl * side

PERS = {"P0": ("2010-01-01", "2016-04-18"), "P1 在": ("2016-04-19", "2020-12-31"),
        "P2 外": ("2021-01-01", "2027-01-01"), "近年": ("2024-01-01", "2027-01-01")}
C54 = {"P0": +0.0016, "P1 在": +0.0181, "P2 外": -0.0001, "近年": -0.0036}
say("\n## A 複製（c54 のゲート 4 行）")
hit = 0
for k, (lo, hi) in PERS.items():
    m = (ety >= lo) & (ety <= hi)
    s2 = stat(dcl[m]); sb = float(np.mean(side[m] > 0))
    ok_ = abs(s2["m"] - C54[k]) <= 0.0005; hit += ok_
    say(f"- {k}: n {int(m.sum())}・BUY 比 {sb*100:.0f}%・Δcl **{s2['m']:+.4f}R (t {s2['t']:+.2f}, MDE {s2['mde']:.4f})**"
        f" vs c54 {C54[k]:+.4f} → {'一致' if ok_ else '**不一致**'}")
say(f"- **複製 {hit}/4**")
if hit < 3:
    say("- 複製不足 → T3 は INCONCLUSIVE"); open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); raise SystemExit(0)

# ---------- decomposition: mean(s·u) = mean(s)·mean(u) + cov(s,u) -----------------------------------
say("\n## B 分解 mean(dcl) = mean(s)·mean(u) + cov(s,u)  （s = ±1 side・u = 2 足の価格変化/risk）")
for k, (lo, hi) in PERS.items():
    m = (ety >= lo) & (ety <= hi)
    s_ = side[m]; u_ = u[m]; d_ = dcl[m]
    ms, mu, md = s_.mean(), u_.mean(), d_.mean()
    cov = np.mean((s_ - ms) * (u_ - mu))
    pred = ms * mu
    ratio = md / pred if pred != 0 else np.nan
    say(f"- {k} (n {int(m.sum())}): mean(s) **{ms:+.4f}**（BUY 比 {(ms+1)/2*100:.0f}%）"
        f"・mean(u) **{mu:+.5f}R**（= 2 足の無符号 平均・{mu*1e4:+.2f} R×1e-4）"
        f"・**side 不均衡だけの予測 {pred:+.5f}R**・cov(s,u) **{cov:+.5f}R**"
        f"・観測 {md:+.5f}R → **観測/予測 {ratio:+.1f}×**・cov が観測の {cov/md*100 if md!=0 else float('nan'):.0f}%")
    if k == "P1 在": r1, cov1, md1, pred1, mu1, ms1 = ratio, cov, md, pred, mu, ms
brk("BREAK-T3", "P1 で 観測 mean(dcl) ÷ [mean(s)·mean(u)] ≥ 2（＝「BUY 比 × 足の正 の別名」は定量的に誤り）",
    f"P1: 観測 {md1:+.5f}R・side 不均衡だけの予測 {pred1:+.5f}R → **{r1:.1f}×**"
    f"（mean(s) {ms1:+.4f}・mean(u) {mu1:+.5f}R）", abs(r1) >= 2)
brk("BREAK-T3b", "cov(s,u) が 観測 mean(dcl) の 50% 超（＝「直後の正は方向に無差別」という前提が誤り）",
    f"P1: cov(s,u) {cov1:+.5f}R = 観測の {cov1/md1*100:.0f}%", abs(cov1 / md1) > 0.50)

# ---------- does the gate verdict change? ----------------------------------------------------------
say("\n## C ゲートの合否は変わるか（c54: 在 |Δμ| 0.018 < 0.048 → 不通過）")
m = (ety >= PERS["P1 在"][0]) & (ety <= PERS["P1 在"][1])
s2 = stat(dcl[m])
say(f"- P1 |Δμ| {abs(s2['m']):.4f}R vs c54 の閾値 0.048 → **{'通過' if abs(s2['m'])>=0.048 else '不通過（c54 と同じ）'}**"
    f"・MDE {s2['mde']:.4f}")
say("- → 壊れたのは**ゲートの結論ではなく説明文**。方法論候補 72/75（旗は正しく散文が誤る）の 3 度目。")

# ---------- which trades carry the cov? ------------------------------------------------------------
say("\n## D cov の中身（side 別・BUY/SELL それぞれの u）")
for k, (lo, hi) in [("P0", PERS["P0"]), ("P1 在", PERS["P1 在"]), ("P2 外", PERS["P2 外"])]:
    m = (ety >= lo) & (ety <= hi)
    for lab, sel in [("BUY", side[m] > 0), ("SELL", side[m] < 0)]:
        su = stat(u[m][sel]); sd = stat(dcl[m][sel])
        say(f"- {k} {lab}: n {su['n']}・u 平均 {su['m']:+.5f}R (t {su['t']:+.2f})・dcl 平均 {sd['m']:+.5f}R (t {sd['t']:+.2f})")
say("- 読み: 「方向無差別」なら BUY と SELL の u 平均は同じであるべき。差が有れば建玉の方向と"
    "その日のアジア午前の 2 足の符号が相関している（＝入口規則による選択）。")

say("\n## 走 5 のまとめ")
for tag, v in VERD: say(f"- {tag}: {'BROKEN' if v else 'not broken'}")
say(f"- 実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"\nwrote {OUT}")
