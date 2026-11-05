# -*- coding: utf-8 -*-
"""
[cycle9 研究レーン] 2026-11-06 — 【深化・レジーム】連続レジームメーター（金自身の効率比 ER・外部状態・look-ahead なし）は
再加速（壁→壁）の平均R を条件づけるか／「直前 24h 継続」効果（反証 02:30 の残存）はトレンド・レジームにだけ宿るか

=== 事前固定（この docstring を書いてから数字を見る） ===
背景: 反証レーン 02:30 は cycle8 の競合セルの符号を訂正し、「2021-26（質量は 2023H2 以降）の金は、再加速の壁抜けが直前 12〜48h の
      金の向きに乗る時だけ走る（継続）。在 2012-20 は逆符号・2021-22 は 0」を残した。反証レーンの構造的読み＝
      「この継続性は 2023 年以降の一方向相場の産物で、相場が往来に戻れば消える」。これは**客観レジームで検証できる**:
      一方向相場＝価格経路の効率比 ER が高い状態。ER は向きに依らない外部状態（R 自身ではない＝cycle6 の含意を満たす）。
      backlog「連続レジームメーター（ER/ボラ/レンジ尊重度）」を本サイクルの深化項目として選ぶ。入口フィルタの再発明ではない。
問い:
  P1（メーター本体）: ER が高い（トレンド）状態の本は、低い（往来）状態の本より平均R が高いか。予測 diff(top − bottom) > 0
      （壁→壁は継続構造なので、トレンド状態で壁が抜けやすい）。
  P2（相互作用＝反証レーンの構造仮説の検定）: 継続効果 D = mean R(A) − mean R(¬A)、A = sign(side)·ret24h_XAU > 0
      （BUY=+1, SELL=−1・反証 02:30 の訂正後の向き・n の内訳を印字して符号を目で確認）は、ER top で ER bottom より大きいか。
      予測 I = D_top − D_bottom > 0。**構造仮説の読み**: 在 2010-20 でも D_top > 0（t≥1.5）かつ D_bottom ≤ 0 なら
      「継続は時代でなくトレンド・レジームの性質」を支持。在で D_top ≤ 0 なら、継続は 2023 年以降の時代効果であり ER では識別できない。
データ（既存キャッシュのみ・scan 無し・M1/M5 原本読込なし・MT5 なし・外部通信なし）:
  - data/c8_crossasset_features.csv（19404 本・ret24h_XAU は te=entry_time−300 の M5 close まで・100% 利用可）
  - data/macro/XAU_m5_close.npz（M5 close 2010-01〜2026-06）→ 日足 close（擬似日境界 22:00 UTC ≈ NY 17:00・各日の最終 M5 close・
    「既知時刻」= その足の開始+300 s）→ ER_N(d) = |logC_d − logC_{d−N}| / Σ|logC_i − logC_{i−1}|（N=20 主・N=60 複製）。
  - 利用可能時刻（5条）: 本ごとの参照時刻 q = te − 24h（**ret24h の窓と重ならない**ように 24h 遅らせる＝機械的相関を断つ）。
    q 以前に確定した最後の日足の ER を asof backward（許容 5 日）。
  - 閾値: ER_N の直近 500 日（当日を含まない・最低 250 日）パーセンタイル pct → top = pct ≥ 2/3、bottom = pct ≤ 1/3。
窓: 在 2010-20／外 2021-26H1／近年 2024-26H1（D2: 水準は近年窓で語る・16 年プールは使わない）。
統計: Welch t・日クラスタ t（同日の本は ER と ret24h を共有）・MDE 2·se・注入 δ=+0.05R → t。
  family-wise: ER の参照時刻 q を k 週 循環シフト（1000 回・曜日/時刻構造と自己相関を保つ・cycle8 ⑨）で 外窓の主 2 セル
  {P1 t, P2 t_I} の max|t| の帰無分布 → p_max。
主セル = **2 セル**（P1 ER20・P2 ER20）。複製（記述・判定不使用）: ER60 の同 2 セル。競合（記述）: 実現ボラ・メーター
  （直近 20 日の日次 log リターン sd の 500 日 pct・top/bottom）で P1/P2 を同形に出す＝ER がボラの代理でないかを見る。
  記述: ER20 pct 五分位 × 平均R・× D、top 三分位の年組成（レジームが時代の代理かを見る）。
合否（セル単位・c5/c8 と同じ）: 在 t≥2 で予測方向 ∧ 外 同符号 t≥1.5 ∧ p_max<0.05。1 セルでも PASS → 「条件づけあり」。
  それ以外 = null。別に上記「構造仮説の読み」を判定とは別に記す。
事前の最重要反証: (1) ER top が特定の年（2011・2019-20・2023-26）に塊で宿るなら、ER は時代の代理で「レジーム」の説明力は
  時代と分離できない（年組成で見る・年固定効果付きの D_top−D_bot も記述で出す）。(2) ER と |ret24h| の機械的相関（q を 24h 遅らせて断つ）。
  (3) 2 主セル＋複製＋競合の事後選択 → 主 2 セルのみ判定・置換で補正。
昇格候補ではない（レジーム記述）。seed 20261106.
"""
import os, sys, time, math
import numpy as np, pandas as pd

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "c9_er_regime_result.md")
ERCACHE = os.path.join(MAC, "XAU_daily_er.csv")
rng = np.random.default_rng(20261106)
L = []
def say(s=""): print(s, flush=True); L.append(s)

say(f"# [cycle9] ER レジームメーター × 再加速 R／継続効果の相互作用 — {time.strftime('%Y-%m-%d %H:%M')} (scripts/c9_er_regime.py)")
say("## 0. データ")
X = pd.read_csv(os.path.join(DATA, "c8_crossasset_features.csv"))
X = X.sort_values("entry_time").reset_index(drop=True)
X["sgn"] = np.where(X["side"] == "BUY", 1.0, -1.0)
X["A"] = (X["sgn"] * X["ret24h_XAU"]) > 0
X["okA"] = X["ret24h_XAU"].notna() & (X["ret24h_XAU"] != 0)
say(f"- trades n={len(X)} 2010-01..2026-06、R mean {X.R.mean():+.4f}（水準は使わない）")
nb = X[X.okA].groupby(["side", "A"]).size()
say("- A = sign(side)·ret24h_XAU > 0 の内訳（符号確認）: " + ", ".join(f"{s}∧{'同向き' if a else '逆向き'} n={v}" for (s, a), v in nb.items()))

# ---- daily closes from M5 close cache ----
z = np.load(os.path.join(MAC, "XAU_m5_close.npz")); ts = z["ts"].astype(np.int64); cl = z["close"].astype(np.float64)
say(f"- XAU M5 close {len(ts)} 本 {pd.to_datetime(ts[0],unit='s')}..{pd.to_datetime(ts[-1],unit='s')} UTC（min/max 印字・⑩）")
day_id = (ts - 22 * 3600) // 86400
df = pd.DataFrame({"day": day_id, "ts": ts, "lc": np.log(cl)})
D = df.groupby("day").agg(ts_last=("ts", "last"), lc=("lc", "last")).reset_index()
D["known"] = D["ts_last"] + 300
D["dlc"] = D["lc"].diff()
def er(n):
    num = (D["lc"] - D["lc"].shift(n)).abs(); den = D["dlc"].abs().rolling(n).sum()
    return num / den.replace(0, np.nan)
D["er20"] = er(20); D["er60"] = er(60)
D["vol20"] = D["dlc"].rolling(20).std()
def rpct(s, win=500, minp=250):
    a = s.to_numpy(); out = np.full(len(a), np.nan)
    for i in range(len(a)):
        lo = max(0, i - win); w = a[lo:i]; w = w[~np.isnan(w)]
        if len(w) >= minp and not np.isnan(a[i]): out[i] = (w < a[i]).mean()
    return out
for c in ("er20", "er60", "vol20"): D[f"p_{c}"] = rpct(D[c])
D[["day", "ts_last", "known", "lc", "er20", "er60", "vol20", "p_er20", "p_er60", "p_vol20"]].to_csv(ERCACHE, index=False)
say(f"- 日足 {len(D)} 日、ER20 中央値 {D.er20.median():.3f}（RW の期待 ≈ √(2/π)/√20·… 参考）、ER60 中央値 {D.er60.median():.3f}、"
    f"pct あり {D.p_er20.notna().mean()*100:.1f}% → キャッシュ {os.path.basename(ERCACHE)}")

known = D["known"].to_numpy()
def asof(q, col, tol=5 * 86400):
    v = D[col].to_numpy(); i = np.searchsorted(known, q, side="right") - 1
    out = np.full(len(q), np.nan); ok = i >= 0
    vv = v[i[ok]]; age = q[ok] - known[i[ok]]; vv = np.where(age <= tol, vv, np.nan); out[ok] = vv
    return out
q = X["te"].to_numpy() - 86400  # 24h 前（ret24h 窓と非重複）
for c in ("p_er20", "p_er60", "p_vol20", "er20"):
    X[c] = asof(q, c)
say(f"- 本への付与（q = te−24h・asof 許容 5 日）: p_er20 あり {X.p_er20.notna().mean()*100:.1f}%、ER20 と |ret24h| の相関 ρ "
    f"{np.corrcoef(X.loc[X.p_er20.notna() & X.okA, 'er20'], X.loc[X.p_er20.notna() & X.okA, 'ret24h_XAU'].abs())[0,1]:+.3f}（機械的相関の確認）")

W = {"在2010-20": X.year <= 2020, "外2021-26": X.year >= 2021, "近年2024-26": X.year >= 2024}
say("\n## 1. ベースライン（無条件平均R・gross）")
for wn, m in W.items(): say(f"- {wn}: n={m.sum()} mean {X.loc[m,'R'].mean():+.4f} sd {X.loc[m,'R'].std():.3f}")

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return np.nan, np.nan, np.nan
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return d, (d / se if se > 0 else np.nan), se
def cl_se(R, day, groups):
    """groups: list of (mask, sign) ; estimator = Σ sign·mean(R[mask]) ; 日クラスタ se"""
    inf = np.zeros(len(R))
    for m, s in groups:
        if m.sum() < 2: return np.nan
        inf += s * np.where(m, (R - R[m].mean()) / m.sum(), 0.0)
    g = pd.Series(inf).groupby(day).sum(); return math.sqrt((g ** 2).sum())

def p1(df, pc, inject=0.0):
    p = df[pc].to_numpy(); ok = ~np.isnan(p); top = ok & (p >= 2 / 3); bot = ok & (p <= 1 / 3)
    R = df["R"].to_numpy().copy(); R[top] += inject
    d, t, se = welch(R[top], R[bot]); tc = d / cl_se(R, df["day"].to_numpy(), [(top, 1), (bot, -1)]) if top.sum() > 1 and bot.sum() > 1 else np.nan
    return dict(diff=d, t=t, tc=tc, se=se, n1=int(top.sum()), n0=int(bot.sum()))
def cont(df, mask):
    """継続効果 D = mean R(A) − mean R(¬A) within mask"""
    A = df["A"].to_numpy() & df["okA"].to_numpy() & mask; nA = (~df["A"].to_numpy()) & df["okA"].to_numpy() & mask
    R = df["R"].to_numpy(); d, t, se = welch(R[A], R[nA]); return d, t, se, int(A.sum()), int(nA.sum()), A, nA
def p2(df, pc, inject=0.0):
    p = df[pc].to_numpy(); ok = ~np.isnan(p); top = ok & (p >= 2 / 3); bot = ok & (p <= 1 / 3); mid = ok & ~top & ~bot
    dfi = df.copy()
    if inject: dfi["R"] = dfi["R"] + np.where(top & dfi["A"].to_numpy(), inject, 0.0)
    dt, tt, st, n1t, n0t, At, nAt = cont(dfi, top); db, tb, sb, n1b, n0b, Ab, nAb = cont(dfi, bot); dm, tm, sm, *_ = cont(dfi, mid)
    I = dt - db; se = math.sqrt(st ** 2 + sb ** 2) if not (np.isnan(st) or np.isnan(sb)) else np.nan
    sec = cl_se(dfi["R"].to_numpy(), dfi["day"].to_numpy(), [(At, 1), (nAt, -1), (Ab, -1), (nAb, 1)])
    return dict(I=I, t=I / se if se else np.nan, tc=I / sec if sec else np.nan, se=se, Dt=dt, tt=tt, Db=db, tb=tb, Dm=dm, tm=tm,
                n=(n1t, n0t, n1b, n0b))

def run(pc, label):
    say(f"\n## {label}")
    out = {}
    for wn, m in W.items():
        sub = X[m]
        a = p1(sub, pc); ai = p1(sub, pc, 0.05)
        b = p2(sub, pc); bi = p2(sub, pc, 0.05)
        out[wn] = (a, b)
        say(f"- {wn} P1 top−bottom: n={a['n1']}:{a['n0']} diff {a['diff']:+.4f} t {a['t']:+.2f} (cl {a['tc']:+.2f}) MDE {2*a['se']:.3f}R 注入+0.05→t {ai['t']:+.2f}")
        say(f"- {wn} P2 継続 D: top {b['Dt']:+.4f} (t{b['tt']:+.2f}, n{b['n'][0]}:{b['n'][1]}) / mid {b['Dm']:+.4f} (t{b['tm']:+.2f}) / bottom {b['Db']:+.4f} (t{b['tb']:+.2f}, n{b['n'][2]}:{b['n'][3]})"
            f" → I=D_top−D_bot {b['I']:+.4f} t {b['t']:+.2f} (cl {b['tc']:+.2f}) MDE {2*b['se']:.3f}R 注入+0.05→t {bi['t']:+.2f}")
    return out

res20 = run("p_er20", "2. 主セル ER20（P1・P2・判定に使用）")
res60 = run("p_er60", "3. 複製 ER60（記述）")
resv = run("p_vol20", "4. 競合 実現ボラ20 メーター（記述・ER がボラの代理か）")

say("\n## 5. 記述: ER20 pct 五分位 × 平均R・× 継続 D（在/外）、top 三分位の年組成")
for wn in ("在2010-20", "外2021-26"):
    sub = X[W[wn] & X.p_er20.notna()]; qn = np.minimum((sub.p_er20 * 5).astype(int), 4)
    mr = sub.groupby(qn)["R"].mean().reindex(range(5))
    Ds = []
    for k in range(5):
        d, t, *_ = cont(sub, (qn == k).to_numpy()); Ds.append(f"{d:+.3f}(t{t:+.1f})")
    say(f"- {wn} 平均R Q1..Q5: " + " ".join(f"{v:+.3f}" for v in mr) + " ｜ 継続 D Q1..Q5: " + " ".join(Ds))
for wn in ("在2010-20", "外2021-26"):
    sub = X[W[wn] & X.p_er20.notna()]; top = sub[sub.p_er20 >= 2 / 3]
    comp = (top.groupby("year").size() / sub.groupby("year").size()).round(2)
    say(f"- {wn} top 三分位の年別占有率: " + " ".join(f"{y}:{v:.2f}" for y, v in comp.items()))
# 年固定効果付きの相互作用（記述）: 年ごとの I を n 加重平均
say("- 年内相互作用（年ごとに I=D_top−D_bot を出し n 加重平均・時代の代理を除いた残り）:")
for wn in ("在2010-20", "外2021-26"):
    sub = X[W[wn]]; vals = []; ws = []
    for y, g in sub.groupby("year"):
        b = p2(g, "p_er20")
        if not np.isnan(b["t"]): vals.append(b["I"]); ws.append(1 / b["se"] ** 2)
    vals, ws = np.array(vals), np.array(ws); Iw = (vals * ws).sum() / ws.sum(); sew = 1 / math.sqrt(ws.sum())
    say(f"  - {wn}: 年内 I 加重平均 {Iw:+.4f} t {Iw/sew:+.2f}（{len(vals)} 年）")

# ---- family-wise permutation: circular weekly shift of ER lookup time (OOS, 2 main cells) ----
say("\n## 6. family-wise 置換（ER の参照時刻 q を k 週 循環シフト・外窓・主 2 セル max|t|・1000 回）")
NPERM = 1000
oos = X[W["外2021-26"]].copy().reset_index(drop=True); qo = oos["te"].to_numpy() - 86400
lo, hi = known[0] + 600 * 86400, known[-1] - 2 * 86400; span_w = (hi - lo) // 604800
obs = np.array([res20["外2021-26"][0]["t"], res20["外2021-26"][1]["t"]]); obs_max = np.nanmax(np.abs(obs))
null = np.full((NPERM, 2), np.nan); tp = time.time()
for p in range(NPERM):
    k = int(rng.integers(8, span_w - 8)); qq = lo + ((qo - lo + k * 604800) % (span_w * 604800))
    oos["p_er20"] = asof(qq, "p_er20")
    null[p, 0] = p1(oos, "p_er20")["t"]; null[p, 1] = p2(oos, "p_er20")["t"]
    if time.time() - tp > 150: say(f"!! 置換 {p+1} 回で時間上限"); null = null[:p + 1]; break
nmax = np.nanmax(np.abs(null), axis=1); p_max = (nmax >= obs_max).mean()
say(f"- 観測 外 max|t| {obs_max:.2f} → 帰無 中央値 {np.median(nmax):.2f} / 95%点 {np.quantile(nmax,0.95):.2f} / **p_max {p_max:.3f}**（{len(nmax)} 回・{time.time()-tp:.0f} s）")
for j, nm in enumerate(("P1 ER20", "P2 ER20 相互作用")):
    say(f"  - {nm}: 外 t {obs[j]:+.2f} 単セル置換 p {(np.abs(null[:, j]) >= abs(obs[j])).mean():.3f}（帰無 sd {np.nanstd(null[:, j]):.2f}）")

say("\n## 7. 判定（事前規則: 在 t≥2 予測方向 ∧ 外 同符号 t≥1.5 ∧ p_max<0.05）")
npass = 0
a_in, b_in = res20["在2010-20"]; a_out, b_out = res20["外2021-26"]; a_rc, b_rc = res20["近年2024-26"]
for nm, ti, to, tr in (("P1 ER20 top−bottom", a_in["t"], a_out["t"], a_rc["t"]), ("P2 ER20 I=D_top−D_bot", b_in["t"], b_out["t"], b_rc["t"])):
    ok = (ti >= 2.0) and (to >= 1.5) and (p_max < 0.05); npass += ok
    say(f"- {nm}: 在 t {ti:+.2f} / 外 t {to:+.2f} / 近年 t {tr:+.2f} / p_max {p_max:.3f} → {'PASS' if ok else 'FAIL'}")
say(f"\n**PASS {npass}/2 → {'条件づけあり' if npass else 'null'}**")
say("\n## 8. 構造仮説の読み（判定とは別・事前に書いた規則）")
say(f"- 在 D_top {b_in['Dt']:+.4f} (t{b_in['tt']:+.2f}) / 在 D_bottom {b_in['Db']:+.4f} (t{b_in['tb']:+.2f}) → "
    + ("在でも ER top で継続 >0（t≥1.5）かつ bottom ≤0 ＝『継続はトレンド・レジームの性質』を支持" if (b_in["tt"] >= 1.5 and b_in["Db"] <= 0)
       else "在の ER top で継続が立たない ＝『継続は 2023 年以降の時代効果で ER では識別できない』側"))
say(f"- 外 D_top {b_out['Dt']:+.4f} (t{b_out['tt']:+.2f}) / 外 D_bottom {b_out['Db']:+.4f} (t{b_out['tb']:+.2f}) / 近年 D_top {b_rc['Dt']:+.4f} (t{b_rc['tt']:+.2f}) / 近年 D_bottom {b_rc['Db']:+.4f} (t{b_rc['tb']:+.2f})")
say(f"\n実行 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("→", OUT)
