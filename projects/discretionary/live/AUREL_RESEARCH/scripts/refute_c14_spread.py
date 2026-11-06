# -*- coding: utf-8 -*-
"""
[REFUTE c14] 2026-11-06 反証レーン — 対象: cycle14 (15:50) US100 スプレッド構造の 3 つの主張
  C1 「Dukascopy の US100 スプレッドは市場由来でなく配信スケジュール（2022-01〜2025-08 は時間外 3.44 pt／現物 1.44 pt の
      固定 2 層、2025-09 に 24 時刻すべて 1.15 pt の単層へ段差）」
  C2 H_B partial（現物時間は在で US100 が安い 7/7・外で 3/7・時間外は US100 が高い 100%）— ただし cycle14 は DST を無視し
      現物時間を 14–20 UTC に固定した。NYSE 現物は夏 13:30–20:00 UTC・冬 14:30–21:00 UTC なので、ブロックの境目が年の半分ずれる。
  C3 R 換算の投影「最新レジームで US100 0.039 R vs 金 0.020 R ＝ 金の ≈2 倍」（全時刻プール・金の risk/|ΔM5| 比を US100 に当てた投影）

=== 事前固定（この docstring を書いてから数字を見る）===
入力: data/macro/US100_m5_spread.npz（cycle14 の M5 キャッシュ: ts, sp_med[pt], sp_max[pt], n_open[0..5]）、
      data/macro/{US100,XAU}_m5_close.npz、data/refute_c4_scan_paths_2010_2026.json（金 risk・jh）。原本 M1 は読まない。
開場 M5 = n_open ≥ 3（直近 5 分で bid が動いた分足が過半）。bps = sp / close(bid) × 1e4。5 分の動き mv = |Δlog close| bps（flat 足除外 ⑪）。
窓: 在 2022-01-01〜2024-06-30／外 2024-07-01〜2026-06-30（cycle14 と同一）。配信レジーム R1/R2 の境目は Q2 で**データから**決める:
   step = 「時間外ブロック（22–13 UTC）の日次中央値 pt が 2.0 を下回り、その後データ末尾まで一度も 2.0 を超えない最初の日」。

Q0 再現: 在/外の UTC 時刻中央値 bps の max/min（開場 M5 n≥200 の時刻）・Spearman ρ・月別 pt 中央値の値域。cycle14 と ±5% 以内なら再現。
Q1 C1 の検定（配信スケジュール vs 市場由来）: レジーム R1/R2 × ブロック（時間外 22–13 UTC／現物 14–20 UTC・cycle14 の定義）で
   (a) モード占有率 = sp_med がブロックのモード（0.01 pt 丸め）±0.05 pt に入る開場 M5 の比率、IQR、p10/p90
   (b) ボラ応答 = Spearman ρ(sp_med, mv) 同一 M5 内、および 日次中央値 sp を日次中央値 mv の十分位で並べた top−bottom 差（pt・モード比）
   (c) 瞬間拡大 = sp_max（M5 内の分足最大）が 1.5×モード・2×モードを超える開場 M5 の比率
   (d) 2 層の境目が UTC 固定か NYSE 開場（DST で 13:30/14:30 UTC）に追随するか: R1 の月ごとに「時刻中央値が 2 層の中点を下回る最初の M5 時刻」を印字。
   判定規則: **C1 survived** = R1 の両ブロックと R2 でモード占有率 ≥90% ∧ |ρ(sp,mv)| <0.10 ∧ 十分位 top−bottom 差 <5% of モード。
             **C1 broken** = いずれかでモード占有率 <70% または ρ >0.30 または top−bottom 差 >20%。他 inconclusive。
   (d) は記述（境目が DST 追随なら「スケジュールは市場時間に紐づく」と注記するが C1 の判定は変えない）。
Q2 段差の日付: step の日付を印字し、チャンク境界（2025-10-01）との距離、現物ブロックの段差日が同じか、step ±5 日の日次中央値を印字。
   記述（判定なし）。段差がチャンク境界と一致するならデータ結合の疑いを注記。
Q3 C2 の検定（DST 補正）: America/New_York の 09:30–16:00（平日）を現物、他の開場時間を時間外として H_B を再計算。
   cycle14 と同じ道具（時刻別 cf の中央値・US100 が安い/高い時刻の比率）を ET 時刻で。判定規則（cycle14 と同一）: 現物で cf_US100<cf_XAU かつ
   時間外で cf_US100>cf_XAU が在外とも成立 → PASS／片方 → partial／どちらも不成立 → FAIL。
   **C2 broken** = DST 補正で判定が partial から変わる（PASS または FAIL）。**survived** = partial のまま ∧ 在の現物 7/7 と外の現物比率が ±1 時刻以内。他 inconclusive。
Q4 C3 の検定（投影の頑健性・R2 最新レジーム）: 比 = cost_R(US100 投影) / cost_R(金) を 5 変種で:
   V-a 全時刻・median|ΔM5|（cycle14 基準）／V-b 全時刻・mean|ΔM5|／V-c US100 現物（ET）のみ vs 金 全時刻／
   V-d US100 現物（ET）vs 金 本番窓（jh 7–12 の本の risk・UTC 22–03 の |ΔM5|）／V-e 両市場に同じ滑り 0.5×median|ΔM5| を加算。
   判定規則: **C3 survived** = 5 変種中 ≥4 で比 ∈ [1.5, 3.0]。**C3 broken** = ≥2 変種で比 <1.2。他 inconclusive。
   コスト倍（スプレッド 2 倍）は両市場同率で比不変＝適用不能（V-e が実質の「コスト加算」）。
Q5 H_A の再読（記述）: R1 を時間順に 2 分割し cycle14 の H_A 規則（max/min ≥2 ∧ ρ ≥0.8）を R1 内で適用。⑮ のブロック対比（時間外/現物 pt 比）も印字。
   cycle14 の FAIL 判定は変えない（事前固定規則の結果）。R1 内で PASS なら「FAIL は構造の不在でなくレジーム跨ぎ」の読みを支持。
look-ahead: 無関係（本の成績を使わない）。survivorship: 開場 M5 の定義は両市場同じ規則・欠陥除外 0。決定的・seed なし。
scan 無し・M1 原本読込なし・MT5 なし・外部通信なし。
"""
import os, json, time
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from zoneinfo import ZoneInfo

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data"); MAC = os.path.join(DATA, "macro")
OUT = os.path.join(DATA, "refute_c14_spread.md")
L = []
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE c14] US100 スプレッド構造（配信スケジュール／DST 補正 H_B／R 投影の頑健性） — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c14_spread.py)")

IN_LO, IN_HI, OUT_HI = pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2024-07-01", tz="UTC"), pd.Timestamp("2026-07-01", tz="UTC")
OFF_UTC = set(list(range(22, 24)) + list(range(0, 14))); CASH_UTC = set(range(14, 21))
GOLD_SP = 0.16

# ---------- load ----------
z = np.load(os.path.join(MAC, "US100_m5_spread.npz"))
S = pd.DataFrame({"ts": z["ts"].astype(np.int64), "sp": z["sp_med"].astype(float), "spmax": z["sp_max"].astype(float), "nopen": z["n_open"].astype(int)})
def load_close(sym):
    c = np.load(os.path.join(MAC, f"{sym}_m5_close.npz")); ts = c["ts"].astype(np.int64); cl = c["close"].astype(float)
    m = (ts >= int(IN_LO.timestamp())) & (ts < int(OUT_HI.timestamp())); ts, cl = ts[m], cl[m]
    mv = np.full(len(ts), np.nan); mv[1:] = np.abs(np.diff(np.log(cl))) * 1e4
    d = pd.DataFrame({"ts": ts, "close": cl, "mv": mv})
    say(f"- {sym} close npz 2022-26 切出し {len(d)} 本 {pd.to_datetime(ts[0],unit='s')}..{pd.to_datetime(ts[-1],unit='s')} UTC（⑩）・flat 足 {(d['mv']==0).mean():.1%}（⑪）")
    return d
U = load_close("US100"); G = load_close("XAU")
S = S.merge(U, on="ts", how="inner")
S["dt"] = pd.to_datetime(S["ts"], unit="s", utc=True)
S["bps"] = S["sp"] / S["close"] * 1e4
S["hour"] = S["dt"].dt.hour; S["date"] = S["dt"].dt.date; S["month"] = S["dt"].dt.to_period("M")
S["et"] = S["dt"].dt.tz_convert(ZoneInfo("America/New_York")); S["et_hour"] = S["et"].dt.hour; S["et_min"] = S["et"].dt.hour * 60 + S["et"].dt.minute; S["et_dow"] = S["et"].dt.dayofweek
S["open"] = S["nopen"] >= 3
S["win"] = np.where(S["dt"] < IN_HI, "in", "out")
say(f"- spread npz {len(z['ts'])} M5 行 → close と突合 {len(S)}・開場 M5（n_open≥3）{S['open'].mean():.1%}・閉場 M5 の sp 中央値 {S.loc[~S['open'],'sp'].median():.3f} pt vs 開場 {S.loc[S['open'],'sp'].median():.3f} pt")
G["dt"] = pd.to_datetime(G["ts"], unit="s", utc=True); G["hour"] = G["dt"].dt.hour
G["et"] = G["dt"].dt.tz_convert(ZoneInfo("America/New_York")); G["et_min"] = G["et"].dt.hour * 60 + G["et"].dt.minute; G["et_dow"] = G["et"].dt.dayofweek
G["win"] = np.where(G["dt"] < IN_HI, "in", "out"); G["gbps"] = GOLD_SP / G["close"] * 1e4
op = S[S["open"]].copy()

# ---------- Q0 ----------
say("\n## Q0 再現（cycle14: 在 max/min 2.42・外 3.11・ρ 0.765・月別 pt 3.43〜3.44 → 1.15〜1.17）")
def hprof(d, key="hour"):
    g = d.groupby(["date", key])["bps"].median().reset_index()
    p = g.groupby(key)["bps"].agg(["median", "mean", "size"]); p["n5"] = d.groupby(key).size(); return p
res = {}
for w in ["in", "out"]:
    p = hprof(op[op["win"] == w]); p = p[p["n5"] >= 200]
    res[w] = p["median"]; say(f"- {w}: 時刻中央値 max {p['median'].max():.3f} (h{int(p['median'].idxmax()):02d}) / min {p['median'].min():.3f} (h{int(p['median'].idxmin()):02d}) → max/min **{p['median'].max()/p['median'].min():.2f}**")
cm = res["in"].index.intersection(res["out"].index); rho0 = spearmanr(res["in"].loc[cm], res["out"].loc[cm])[0]
say(f"- 在外 Spearman ρ **{rho0:.3f}**（{len(cm)} 時刻）")
mon = op.groupby("month")["sp"].median()
say(f"- 月別 pt 中央値: 2022-01〜2025-08 値域 [{mon[:'2025-08'].min():.3f}, {mon[:'2025-08'].max():.3f}]・2025-09〜 値域 [{mon['2025-09':].min():.3f}, {mon['2025-09':].max():.3f}]")

# ---------- Q2 (先に: レジーム境目をデータから) ----------
say("\n## Q2 段差の日付（時間外ブロック 22–13 UTC の日次中央値 pt が 2.0 を下回り以後超えない最初の日）")
offd = op[op["hour"].isin(OFF_UTC)].groupby("date")["sp"].median()
cashd = op[op["hour"].isin(CASH_UTC)].groupby("date")["sp"].median()
# v0 の規則「以後一度も 2.0 を超えない」は末尾の 1 日（2026-06-30）が 2.0 超で R1 が空になった → 検出器を頑健化（判定規則ではない・v0 の結果は本文に記録）:
# step = 「その日以降の日次中央値の 95% 以上が閾値未満 ∧ 直後 10 日の中央値が閾値未満」を満たす最初の日。閾値未満でない例外日は列挙する。
# v1（95% 規則）も None: step 後 249 日のうち 15 日（6%）が旧水準 3.4 に戻る（2026-06 に 9 日集中）→ v2 = 局所対比: 直前 10 日中央値 > thr ∧ 直後 10 日中央値 < thr の最初の日。
def find_step(ser, thr):
    v = ser.to_numpy()
    for i in range(10, len(v) - 10):
        if np.median(v[i - 10:i]) > thr and np.median(v[i:i + 10]) < thr and v[i] < thr:
            return ser.index[i]
    return None
step_date = find_step(offd, 2.0)
exc = offd[(offd.index >= step_date) & (offd > 2.0)] if step_date else offd.iloc[0:0]
DOW = ["月", "火", "水", "木", "金", "土", "日"]
say(f"- step（時間外・v2 局所対比）= **{step_date}（{DOW[pd.Timestamp(step_date).dayofweek]}）**・チャンク境界 2025-10-01 との差 {(pd.Timestamp(step_date)-pd.Timestamp('2025-10-01')).days} 日・step 以降 {int((offd.index >= step_date).sum())} 日のうち 2.0 超（旧水準へ戻る）の日 **{len(exc)}**: " + " ".join(f"{d}({DOW[pd.Timestamp(d).dayofweek]}):{x:.2f}" for d, x in exc.items()))
say(f"- 旧水準へ戻る日の月別: " + " ".join(f"{k}:{v}" for k, v in pd.Series([pd.Timestamp(d).strftime('%Y-%m') for d in exc.index]).value_counts().sort_index().items()) + f"・曜日別: " + " ".join(f"{DOW[k]}:{v}" for k, v in pd.Series([pd.Timestamp(d).dayofweek for d in exc.index]).value_counts().sort_index().items()))
pre_exc = offd[(offd.index < step_date) & (offd < 2.0)]
say(f"- step 以前で 2.0 未満の日 {len(pre_exc)}（全 {int((offd.index < step_date).sum())} 日中）: " + " ".join(f"{d}:{x:.2f}" for d, x in list(pre_exc.items())[:12]))
step_cash = find_step(cashd, 1.30)
say(f"- step（現物・1.30 閾）= **{step_cash}**（同日なら単一の配信変更）")
sd = pd.Timestamp(step_date)
win5 = [(d, offd.get(d, np.nan), cashd.get(d, np.nan)) for d in offd.index if abs((pd.Timestamp(d) - sd).days) <= 6]
say("- step ±6 日の日次中央値 pt（時間外／現物）: " + " ".join(f"{d}:{a:.2f}/{c:.2f}" for d, a, c in win5))
R1 = op["dt"] < pd.Timestamp(step_date, tz="UTC"); R2 = ~R1
say(f"- レジーム R1 = 2022-01-01〜{step_date}（開場 M5 {R1.sum()}）／R2 = {step_date}〜2026-06-30（{R2.sum()}）")

# ---------- Q1 ----------
say("\n## Q1 C1 配信スケジュール vs 市場由来（レジーム × ブロック・開場 M5）")
say("| レジーム | ブロック | n M5 | モード pt | 占有率 ±0.05 | IQR pt | p10/p90 | ρ(sp,mv) | 十分位 top−bottom（pt・%モード） | sp_max>1.5× | >2× |")
say("|---|---|---|---|---|---|---|---|---|---|---|")
Q1 = []
for rn, rm in [("R1", R1), ("R2", R2)]:
    for bn, hs in [("時間外", OFF_UTC), ("現物", CASH_UTC)]:
        d = op[rm & op["hour"].isin(hs)]
        if len(d) < 1000: continue
        mode = d["sp"].round(2).mode().iloc[0]; share = (np.abs(d["sp"] - mode) <= 0.05).mean()
        q = d["sp"].quantile([.1, .25, .75, .9]); iqr = q[.75] - q[.25]
        dm = d[d["mv"] > 0]; rho = spearmanr(dm["sp"], dm["mv"])[0] if len(dm) > 100 else np.nan
        dd = dm.groupby("date").agg(sp=("sp", "median"), mv=("mv", "median")); dd = dd[dd["mv"] > 0]
        dec = pd.qcut(dd["mv"], 10, labels=False, duplicates="drop"); tb = dd.loc[dec == dec.max(), "sp"].median() - dd.loc[dec == 0, "sp"].median()
        s15 = (d["spmax"] > 1.5 * mode).mean(); s2 = (d["spmax"] > 2 * mode).mean()
        Q1.append(dict(r=rn, b=bn, share=share, rho=rho, tb=tb / mode))
        say(f"| {rn} | {bn} | {len(d)} | {mode:.2f} | **{share:.1%}** | {iqr:.3f} | {q[.1]:.2f}/{q[.9]:.2f} | **{rho:+.3f}** | {tb:+.3f} ({tb/mode:+.1%}) | {s15:.2%} | {s2:.2%} |")
surv = all(r["share"] >= 0.90 and abs(r["rho"]) < 0.10 and abs(r["tb"]) < 0.05 for r in Q1)
brok = any(r["share"] < 0.70 or r["rho"] > 0.30 or abs(r["tb"]) > 0.20 for r in Q1)
C1V = "survived（配信スケジュール）" if surv else ("broken（市場由来の変動あり）" if brok else "inconclusive")
say(f"- **C1 判定: {C1V}**")
# (d) 2 層の境目は UTC 固定か NYSE 開場追随か
say("\n### (d) R1 の月別: 時刻中央値 pt が 2 層の中点（≈2.44）を下回る最初の M5 時刻（UTC）— DST で 13:30/14:30 と動けば市場時間に紐づく")
d1 = op[R1].copy(); d1["tod"] = d1["dt"].dt.hour * 60 + d1["dt"].dt.minute
rows = []
for mth, dmm in d1.groupby("month"):
    prof = dmm.groupby("tod")["sp"].median(); prof = prof.loc[(prof.index >= 12 * 60) & (prof.index <= 16 * 60)]
    below = prof[prof < 2.44]
    rows.append(f"{mth}:{below.index[0]//60:02d}:{below.index[0]%60:02d}" if len(below) else f"{mth}:-")
say("- " + " ".join(rows))

# ---------- Q3 DST 補正 H_B ----------
say("\n## Q3 C2 DST 補正 H_B（現物 = ET 09:30–16:00 平日・時間外 = 他の開場時間・cf = spread_bps ÷ median|ΔM5|_bps）")
def et_block(df):
    cash = (df["et_dow"] <= 4) & (df["et_min"] >= 9 * 60 + 30) & (df["et_min"] < 16 * 60)
    return np.where(cash, "cash", "off")
op["blk"] = et_block(op); G["blk"] = et_block(G)
op["et_h"] = op["et_hour"]; G["et_h"] = G["et"].dt.hour
HB = {}
for w in ["in", "out"]:
    u = op[op["win"] == w]; x = G[(G["win"] == w) & (G["mv"] > 0)]
    # 時刻別（ET）: cash 時刻 = 10..15 全体 + 9（半分）、off = 開場 M5 n≥200 の他時刻
    pu = u.groupby(["date", "et_h"])["bps"].median().reset_index().groupby("et_h")["bps"].median(); nu = u.groupby("et_h").size()
    mvu = u[u["mv"] > 0].groupby("et_h")["mv"].median(); gx = x.groupby("et_h").agg(mv=("mv", "median"), gbps=("gbps", "median"))
    tab = pd.DataFrame({"spu": pu, "mvu": mvu, "n": nu}).join(gx); tab = tab[tab["n"] >= 200].dropna()
    tab["cfu"] = tab["spu"] / tab["mvu"]; tab["cfx"] = tab["gbps"] / tab["mv"]
    cash_h = tab.loc[(tab.index >= 9) & (tab.index <= 15)]; off_h = tab.loc[(tab.index >= 16) | (tab.index <= 8)]
    # ブロック・プール版（M5 行をまとめて中央値）
    cu = u[u["blk"] == "cash"]; ou = u[u["blk"] == "off"]; cx = x[x["blk"] == "cash"]; ox = x[x["blk"] == "off"]
    pool = dict(cash_u=cu["bps"].median() / cu.loc[cu["mv"] > 0, "mv"].median(), cash_x=cx["gbps"].median() / cx["mv"].median(),
                off_u=ou["bps"].median() / ou.loc[ou["mv"] > 0, "mv"].median(), off_x=ox["gbps"].median() / ox["mv"].median())
    HB[w] = dict(cash_u=cash_h["cfu"].median(), cash_x=cash_h["cfx"].median(), off_u=off_h["cfu"].median(), off_x=off_h["cfx"].median(),
                 cash_ok=(cash_h["cfu"] < cash_h["cfx"]).mean(), off_ok=(off_h["cfu"] > off_h["cfx"]).mean(), ncash=len(cash_h), noff=len(off_h), pool=pool)
    say(f"- {w}: ET 時刻別 現物 cf_US100 **{HB[w]['cash_u']:.3f}** vs cf_XAU **{HB[w]['cash_x']:.3f}**（US100 が安い {HB[w]['cash_ok']:.0%}・{HB[w]['ncash']} 時刻）／"
        f"時間外 **{HB[w]['off_u']:.3f}** vs **{HB[w]['off_x']:.3f}**（US100 が高い {HB[w]['off_ok']:.0%}・{HB[w]['noff']} 時刻）｜"
        f"プール版 現物 {pool['cash_u']:.3f} vs {pool['cash_x']:.3f}・時間外 {pool['off_u']:.3f} vs {pool['off_x']:.3f}")
    say("  - ET 時刻別 cf_US100/cf_XAU: " + " ".join(f"h{h:02d}:{r['cfu']:.2f}/{r['cfx']:.2f}" for h, r in tab.iterrows()))
cash_pass = all(HB[w]["cash_u"] < HB[w]["cash_x"] for w in HB); off_pass = all(HB[w]["off_u"] > HB[w]["off_x"] for w in HB)
v_dst = "PASS" if (cash_pass and off_pass) else ("partial" if (cash_pass or off_pass) else "FAIL")
cash_pass_p = all(HB[w]["pool"]["cash_u"] < HB[w]["pool"]["cash_x"] for w in HB); off_pass_p = all(HB[w]["pool"]["off_u"] > HB[w]["pool"]["off_x"] for w in HB)
v_pool = "PASS" if (cash_pass_p and off_pass_p) else ("partial" if (cash_pass_p or off_pass_p) else "FAIL")
C2V = "broken（判定が変わる）" if v_dst != "partial" else ("survived" if (HB["in"]["cash_ok"] >= 6 / 7 and abs(HB["out"]["cash_ok"] - 3 / 7) <= 1 / 7 + 1e-9) else "inconclusive")
say(f"- **DST 補正 H_B: {v_dst}**（現物で US100 安い: {cash_pass}／時間外で US100 高い: {off_pass}）・プール版 {v_pool}。cycle14（UTC 固定）= partial → **C2 判定: {C2V}**")

# ---------- Q4 R 投影の頑健性（R2 最新レジーム） ----------
say(f"\n## Q4 C3 R 投影の頑健性（最新レジーム R2 = {step_date}〜2026-06-30・比 = cost_R(US100 投影)/cost_R(金)）")
sc = json.load(open(os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")))["trades"]
et_ = np.array([r["entry_time"] for r in sc], dtype=np.int64); rk = np.array([r["risk"] for r in sc], dtype=float); jh = np.array([r["jh"] for r in sc])
r2m = et_ >= int(pd.Timestamp(step_date, tz="UTC").timestamp())
risk_all = rk[r2m]; risk_prod = rk[r2m & (jh >= 7) & (jh <= 12)]
say(f"- 金 risk R2: 全時刻 n{len(risk_all)} 中央値 {np.median(risk_all):.2f} USD／本番窓 jh7-12 n{len(risk_prod)} 中央値 {np.median(risk_prod):.2f} USD")
uR2 = op[R2]; gR2 = G[(G["dt"] >= pd.Timestamp(step_date, tz="UTC")) & (G["mv"] > 0)]
def cost_ratio(label, u_sel, g_sel, risk_g, agg="median", slip=0.0):
    f = np.median if agg == "median" else np.mean
    g_mv_usd = f((g_sel["mv"] / 1e4 * g_sel["close"]).to_numpy()); u_mv_pt = f((u_sel.loc[u_sel["mv"] > 0, "mv"] / 1e4 * u_sel.loc[u_sel["mv"] > 0, "close"]).to_numpy())
    k = f(risk_g) / g_mv_usd; risk_proj = k * u_mv_pt
    sp_u = u_sel["sp"].median(); cost_u = (sp_u + slip * u_mv_pt) / risk_proj; cost_g = (GOLD_SP + slip * g_mv_usd) / f(risk_g)
    say(f"- {label}: 金 |ΔM5| {g_mv_usd:.3f} USD・k {k:.1f}・金 cost_R **{cost_g:.4f}**｜US100 |ΔM5| {u_mv_pt:.2f} pt・risk_proj {risk_proj:.1f} pt・sp {sp_u:.2f} pt・cost_R 投影 **{cost_u:.4f}** → 比 **{cost_u/cost_g:.2f}**")
    return cost_u / cost_g
ratios = []
ratios.append(cost_ratio("V-a 全時刻・median（cycle14 基準）", uR2, gR2, risk_all))
ratios.append(cost_ratio("V-b 全時刻・mean", uR2, gR2, risk_all, agg="mean"))
ratios.append(cost_ratio("V-c US100 現物(ET) vs 金 全時刻", uR2[uR2["blk"] == "cash"], gR2, risk_all))
gprod = gR2[gR2["hour"].isin([22, 23, 0, 1, 2, 3])]
ratios.append(cost_ratio("V-d US100 現物(ET) vs 金 本番窓（jh7-12 risk・UTC22-03）", uR2[uR2["blk"] == "cash"], gprod, risk_prod))
ratios.append(cost_ratio("V-e 全時刻 + 両市場に滑り 0.5×|ΔM5|", uR2, gR2, risk_all, slip=0.5))
ratios = np.array(ratios)
C3V = "survived（≈2 倍）" if (np.sum((ratios >= 1.5) & (ratios <= 3.0)) >= 4) else ("broken" if np.sum(ratios < 1.2) >= 2 else "inconclusive")
say(f"- 比の値域 [{ratios.min():.2f}, {ratios.max():.2f}]・[1.5,3.0] 内 {int(np.sum((ratios>=1.5)&(ratios<=3.0)))}/5・<1.2 {int(np.sum(ratios<1.2))}/5 → **C3 判定: {C3V}**")
# 参考: 2022-26 プール（cycle14 の 0.100 R vs 0.039 R）
say("- 参考 2022-26 プール:"); _ = cost_ratio("  V-a' 全期間・median", op, G[G["mv"] > 0], rk[(et_ >= int(IN_LO.timestamp())) & (et_ < int(OUT_HI.timestamp()))])

# ---------- Q5 H_A を R1 内で ----------
say("\n## Q5 H_A の再読（記述）: R1 を時間順 2 分割して cycle14 の規則を R1 内で適用・⑮ ブロック対比")
d1 = op[R1]; mid = d1["dt"].iloc[len(d1) // 2]
P = {}
for nm, dd in [("R1 前半", d1[d1["dt"] < mid]), ("R1 後半", d1[d1["dt"] >= mid]), ("R2", op[R2])]:
    p = hprof(dd); p = p[p["n5"] >= 200]; P[nm] = p["median"]
    offp = dd[dd["hour"].isin(OFF_UTC)]["sp"].median(); cashp = dd[dd["hour"].isin(CASH_UTC)]["sp"].median()
    say(f"- {nm}（{dd['dt'].min().date()}〜{dd['dt'].max().date()}）: max/min {p['median'].max()/p['median'].min():.2f}・⑮ 時間外/現物 pt 比 **{offp/cashp:.2f}**（{offp:.2f}/{cashp:.2f}）")
cm = P["R1 前半"].index.intersection(P["R1 後半"].index); rho1 = spearmanr(P["R1 前半"].loc[cm], P["R1 後半"].loc[cm])[0]
ha_r1 = (P["R1 前半"].max() / P["R1 前半"].min() >= 2) and (P["R1 後半"].max() / P["R1 後半"].min() >= 2) and rho1 >= 0.8
say(f"- R1 前半 vs 後半 Spearman ρ **{rho1:.3f}** → cycle14 規則を R1 内で適用: **{'PASS' if ha_r1 else 'FAIL'}**（cycle14 の在外 FAIL は変えない・読みの補助）")

say(f"\n- 判定まとめ: C1 {C1V}／C2 {C2V}（DST 補正 H_B {v_dst}・プール {v_pool}）／C3 {C3V}・合計 {time.time()-T0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n"); print("wrote", OUT)
