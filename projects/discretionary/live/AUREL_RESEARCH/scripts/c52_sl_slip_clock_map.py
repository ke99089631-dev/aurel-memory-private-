# -*- coding: utf-8 -*-
"""
cycle52 (2026-11-19) — 【執行・深化】台帳 slippage_sim 注釈の SL 滑りは ET 時刻帯の構造を持つか／ボラで説明されるか
=====================================================================================================
事前固定（数字を見る前に書く・本 docstring が正本）

データ: ../setup_ledger.jsonl（読むだけ）。setup 行に update 行（target=id）を上書きして最終状態を復元（DATA_MAP §3）。
対象 = reaccel closed 本（exit_reason ∈ {SL,TP,TIME}）。SL 滑り = sl_slip_pt（USD・slippage_sim: MT5 tick 履歴・成行 L=1 s・c4 で
中央値 +0.026・正 = 不利 と読む。符号分布を先に印字して確認）。時刻 = exit_time（UTC 秒）→ America/New_York（DST 追随）。
ボラ = features.atr14（setup 時・USD）。risk = |entry − sl|（reaccel dict）。

仮説（c21 の滑りの時刻地図の提案 = 「件数の多い ET 08–10 と SL 比の高い ET 13–14 の 2 帯から」）
  H_S1（主・片側）: SL 決着が ET 08:00–09:59 に落ちる本（帯 A）の sl_slip_pt 平均は、それ以外（帯 B）より大きい。
      機構 = 米国の定時公表（08:30 ET）と NY 寄り直後の 5σ ジャンプ密度（c45: SJ/UJ の 55% が ET 08–10）→ 逆指値のトリガーから
      約定までの 1 s にティックが飛ぶ。
      判定: 在（SL 本を exit_time 昇順で前半）Δ = mean_A − mean_B > 0 ∧ Welch t ≥ 2 ∧ 置換 p(片側) < 0.05、
            外（後半）同符号 ∧ t ≥ 1.5。どちらか欠けば null。MDE = 2·se(Δ) を必ず印字。
  H_S2（副・機構）: 滑りはボラの別名 = Spearman ρ(sl_slip_pt, atr14) > 0（全 SL 本・置換 p<0.05）で、
      atr14 で割った滑り比（sl_slip_pt/atr14）の帯 A−B 差は |t|<2（時刻固有の成分なし）。
      読み: H_S1 PASS ∧ H_S2 の比が 0 → 「時計はボラの顔」（c21 と同形）／ H_S1 PASS ∧ 比も >0 → 時刻固有。
  記述（判定外）: ①ET 時刻別（2 時間帯 12 枡）の SL 滑り 平均/中央値/n ②帯 C = ET 13:00–14:59（c21 SL 偏重帯）
      ③entry slip_pt の帯別（c4: 両側対称の確認）④tp_fill_ok の帯別 False 率 ⑤R 単位の執行コスト
      cost_R = (spread_pt + |slip_pt| + sl_slip_pt·1{SL}) / risk の帯別・全体（n* 計算の入力・c25 0.0306R と比較）
      ⑥「SL 本の何割が帯 A で決着するか」× 帯の滑り = コストの集中度。
  陽性対照: 在の帯 A に +0.10 USD を注入し判定規則の t を印字（検出できなければ null は「0.1 USD 級以下」としか書かない）。
  衛生（必ず印字）: 台帳 closed 本数・exit_reason 内訳・c25（11-09・n320 TP154/SL165/TIME1）との exit_time≤11-09 での一致、
      sl_slip_pt の符号分布・欠落（注釈なし）の本の R 分布（c4: 欠落は高 R に偏る）、slip_src の種類、
      top-level entry と reaccel.entry の差 vs slip_pt（entry が約定値かの確認）。
  予算（数字を見る前）: c4 の SL slip 中央値 0.026・max 0.65 USD → risk 中央値 ≈7 USD で 0.004〜0.09R。帯差が p90 級
      （0.3 USD）でも 0.04R。本サイクルの最大の経済的含意はコスト地図であって優位ではない。昇格候補・入口/出口の提案ではない。
  多重検定: 判定 2 セル（H_S1・H_S2）。12 枡・帯 C・entry slip・tp_fill_ok は記述。
  D2: 台帳は 2026-09〜11 の 1 窓（近年）のみ。16 年一括なし。seed 20261119。
"""
import json, sys, time, collections
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np

T0 = time.time()
rng = np.random.default_rng(20261119)
ET = ZoneInfo("America/New_York")
LEDGER = "../setup_ledger.jsonl"
OUT = "data/c52_sl_slip_clock_map_result.md"
lines = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8") if l.strip()]
setups = [r for r in rows if r.get("kind") == "setup" and "id" in r]
st = {r["id"]: dict(r) for r in setups}
n_upd = 0
for r in rows:
    if r.get("kind") == "update":
        tid = r.get("target")
        if tid in st:
            n_upd += 1
            for k, v in r.items():
                if k not in ("kind", "target"):
                    st[tid][k] = v
fin = list(st.values())
P(f"# c52 SL 滑りの時刻地図（台帳 slippage_sim 注釈）— 実行 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
P(f"rows {len(rows)} setup {len(setups)} update 適用 {n_upd}")

# 母集団 = reaccel dict が closed の本のみ（top-level exit_reason は chase の出口も上書きする＝第 1 走で 480 本に膨れた・衛生）
# 注釈（slip_pt/sl_slip_pt/tp_fill_ok・top-level）は top-level exit_time == reaccel.exit_time の本だけ reaccel の出口に帰属させる
closed = []; n_top_only = 0; n_mismatch = 0; n_noann = 0
for r in fin:
    ra = r.get("reaccel") or {}
    if r.get("exit_reason") and not ra.get("exit_reason"):
        n_top_only += 1
    er = ra.get("exit_reason")
    if not er:
        continue
    ent = ra.get("entry"); sl = ra.get("sl"); et = ra.get("exit_time"); en_t = ra.get("entry_time")
    if ent is None or sl is None or et is None:
        continue
    ann_ok = r.get("exit_time") == et
    if r.get("exit_time") is None: n_noann += 1
    elif not ann_ok: n_mismatch += 1
    closed.append(dict(id=r["id"], er=er, R=ra.get("R"), exit_time=int(et), entry_time=int(en_t) if en_t else None,
                       risk=abs(float(ent) - float(sl)), side=r.get("side"), wall_kind=r.get("wall_kind"),
                       atr14=(r.get("features") or {}).get("atr14"),
                       slip=r.get("slip_pt") if ann_ok else None, sl_slip=r.get("sl_slip_pt") if ann_ok else None,
                       tp_ok=r.get("tp_fill_ok") if ann_ok else None, spread=r.get("spread_pt"), slip_src=r.get("slip_src") if ann_ok else None,
                       entry_top=r.get("entry"), entry_re=ra.get("entry"), mfe=ra.get("mfe_R"), mae=ra.get("mae_R"),
                       hold=ra.get("hold_bars")))
P(f"reaccel closed {len(closed)} 内訳 {dict(collections.Counter(c['er'] for c in closed))}")
P(f"衛生: top-level exit_reason のみ（chase の出口・母集団から除外） {n_top_only} 本／reaccel closed のうち top-level exit_time 無し（注釈なし） {n_noann}・不一致（注釈は別の出口のもの→無効化） {n_mismatch}")
ts = [c["exit_time"] for c in closed]
P("exit_time 範囲", datetime.fromtimestamp(min(ts), timezone.utc).strftime("%Y-%m-%d %H:%M"), "→",
  datetime.fromtimestamp(max(ts), timezone.utc).strftime("%Y-%m-%d %H:%M"), "UTC")
# 衛生: c25 との一致（exit_time ≤ 2026-11-09 23:59 UTC）
cut = int(datetime(2026, 11, 9, 23, 59, tzinfo=timezone.utc).timestamp())
pre = [c for c in closed if c["exit_time"] <= cut]
P(f"衛生: exit_time ≤ 2026-11-09 の closed {len(pre)} 内訳 {dict(collections.Counter(c['er'] for c in pre))}  (c25 11-09: n320 TP154/SL165/TIME1)")
P("slip_src 種類", dict(collections.Counter(str(c["slip_src"]) for c in closed)))
d_ent = np.array([c["entry_top"] - c["entry_re"] for c in closed if c["entry_top"] is not None and c["entry_re"] is not None])
P(f"衛生: top-level entry − reaccel.entry  n {len(d_ent)} 中央値 {np.median(d_ent):+.3f} p10/p90 {np.percentile(d_ent,10):+.3f}/{np.percentile(d_ent,90):+.3f} (0 なら top-level は約定値でない)")

sl_all = [c for c in closed if c["er"] == "SL"]
sl_an = [c for c in sl_all if c["sl_slip"] is not None]
sl_na = [c for c in sl_all if c["sl_slip"] is None]
P(f"SL 本 {len(sl_all)}・sl_slip_pt 注釈あり {len(sl_an)}・なし {len(sl_na)}")
v = np.array([c["sl_slip"] for c in sl_an], float)
P(f"sl_slip_pt 符号: >0 {np.mean(v>0):.2f}  =0 {np.mean(v==0):.2f}  <0 {np.mean(v<0):.2f}；中央値 {np.median(v):+.3f} 平均 {v.mean():+.3f} p90 {np.percentile(v,90):+.3f} max {v.max():+.3f} min {v.min():+.3f} USD")
risk = np.array([c["risk"] for c in sl_an]); P(f"risk 中央値 {np.median(risk):.2f} USD → 滑り中央値 {np.median(v)/np.median(risk):.4f}R・p90 {np.percentile(v,90)/np.median(risk):.4f}R")
if sl_na:
    P(f"注釈なし SL 本 n {len(sl_na)} 平均R {np.mean([c['R'] for c in sl_na if c['R'] is not None]):+.3f} vs 注釈あり {np.mean([c['R'] for c in sl_an if c['R'] is not None]):+.3f}")

def et_hour(ts):
    return datetime.fromtimestamp(ts, timezone.utc).astimezone(ET).hour
for c in closed:
    c["h"] = et_hour(c["exit_time"]); c["h_in"] = et_hour(c["entry_time"]) if c["entry_time"] else None
for c in sl_an:
    c["A"] = 8 <= c["h"] <= 9; c["C"] = 13 <= c["h"] <= 14

def welch(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = a.mean() - b.mean(); se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    return d, (d/se if se > 0 else np.nan), se
def perm_p(a, b, n=5000):
    a = np.asarray(a, float); b = np.asarray(b, float); obs = a.mean() - b.mean()
    pool = np.concatenate([a, b]); na = len(a); cnt = 0
    for _ in range(n):
        rng.shuffle(pool); cnt += (pool[:na].mean() - pool[na:].mean()) >= obs
    return (cnt + 1) / (n + 1)
def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y)); return np.corrcoef(rx, ry)[0, 1]

# ---------- 記述①: ET 2 時間帯 12 枡 ----------
P("\n## 記述① SL 滑り × ET 決着時刻（2 時間帯）")
P("| ET 帯 | n | 平均 USD | 中央値 | p90 | 平均 /atr14 |")
P("|---|---|---|---|---|---|")
for h0 in range(0, 24, 2):
    g = [c for c in sl_an if h0 <= c["h"] <= h0 + 1]
    if not g: P(f"| {h0:02d}–{h0+1:02d} | 0 | | | | |"); continue
    x = np.array([c["sl_slip"] for c in g]); ra = np.array([c["sl_slip"]/c["atr14"] for c in g if c["atr14"]])
    P(f"| {h0:02d}–{h0+1:02d} | {len(g)} | {x.mean():+.3f} | {np.median(x):+.3f} | {np.percentile(x,90):+.3f} | {ra.mean() if len(ra) else float('nan'):+.4f} |")

# ---------- H_S1 ----------
P("\n## H_S1 帯 A（ET 08–09 時決着）vs 帯 B（他）— 在/外 = SL 本 exit_time 昇順 前半/後半")
sl_an.sort(key=lambda c: c["exit_time"])
half = len(sl_an) // 2
res = {}
for name, grp in (("在(前半)", sl_an[:half]), ("外(後半)", sl_an[half:]), ("全体(記述)", sl_an)):
    A = [c["sl_slip"] for c in grp if c["A"]]; B = [c["sl_slip"] for c in grp if not c["A"]]
    if len(A) < 3 or len(B) < 3:
        P(f"- {name}: n_A {len(A)} 不足"); continue
    d, t, se = welch(A, B); p = perm_p(A, B)
    P(f"- {name}: n_A {len(A)} / n_B {len(B)}  mean_A {np.mean(A):+.3f} mean_B {np.mean(B):+.3f}  Δ {d:+.3f} USD  Welch t {t:+.2f}  置換 p(片側) {p:.3f}  MDE(2se) {2*se:.3f} USD  中央値 A/B {np.median(A):+.3f}/{np.median(B):+.3f}")
    res[name] = (d, t, p, se, len(A), len(B))
    if name.startswith("在"):
        Ai = np.array(A) + 0.10; d2, t2, _ = welch(Ai, B)
        P(f"  陽性対照（帯 A に +0.10 USD 注入）: Δ {d2:+.3f} t {t2:+.2f} 置換 p {perm_p(Ai,B):.3f}")
# 判定
ok_in = "在(前半)" in res and res["在(前半)"][0] > 0 and res["在(前半)"][1] >= 2 and res["在(前半)"][2] < 0.05
ok_out = "外(後半)" in res and res["外(後半)"][0] > 0 and res["外(後半)"][1] >= 1.5
P(f"**H_S1 判定: {'PASS' if (ok_in and ok_out) else 'null'}**（在 {ok_in}・外 {ok_out}）")
# 時刻 family（12 枡 one-vs-rest・記述・family max|t|）
tt = []
for h0 in range(0, 24, 2):
    A = [c["sl_slip"] for c in sl_an if h0 <= c["h"] <= h0+1]; B = [c["sl_slip"] for c in sl_an if not (h0 <= c["h"] <= h0+1)]
    if len(A) >= 5: tt.append((h0, welch(A, B)[1], len(A)))
P("時刻 family（全体・2 時間帯 one-vs-rest t）: " + ", ".join(f"{h:02d}:{t:+.2f}(n{n})" for h, t, n in tt) + f"  → max|t| {max(abs(t) for _,t,_ in tt):.2f}・sd {np.std([t for _,t,_ in tt]):.2f}")

# ---------- H_S2 ----------
P("\n## H_S2 滑りはボラの別名か")
xa = [c for c in sl_an if c["atr14"]]
rho = spearman(np.array([c["sl_slip"] for c in xa]), np.array([c["atr14"] for c in xa]))
# 置換
cnt = 0; yv = np.array([c["atr14"] for c in xa]); xv = np.array([c["sl_slip"] for c in xa])
for _ in range(3000):
    cnt += spearman(xv, rng.permutation(yv)) >= rho
P(f"- Spearman ρ(sl_slip_pt, atr14) 全 SL 本 n {len(xa)} = {rho:+.3f}  置換 p(片側) {(cnt+1)/3001:.3f}；ρ(sl_slip, risk) {spearman(xv, np.array([c['risk'] for c in xa])):+.3f}")
for name, grp in (("在(前半)", xa[:len(xa)//2]), ("外(後半)", xa[len(xa)//2:])):
    P(f"  {name} ρ = {spearman(np.array([c['sl_slip'] for c in grp]), np.array([c['atr14'] for c in grp])):+.3f} (n {len(grp)})")
A = [c["sl_slip"]/c["atr14"] for c in xa if c["A"]]; B = [c["sl_slip"]/c["atr14"] for c in xa if not c["A"]]
d, t, se = welch(A, B)
P(f"- 滑り比 sl_slip/atr14 帯 A−B（全体）: Δ {d:+.4f} t {t:+.2f} MDE {2*se:.4f}（A 平均 {np.mean(A):+.4f} / B {np.mean(B):+.4f}）")
# atr14 は帯で違うか
P(f"- atr14 帯 A 中央値 {np.median([c['atr14'] for c in xa if c['A']]):.2f} vs B {np.median([c['atr14'] for c in xa if not c['A']]):.2f} USD")
s2 = rho > 0 and (cnt+1)/3001 < 0.05 and abs(t) < 2
P(f"**H_S2 判定: {'PASS（滑りはボラの顔）' if s2 else ('部分' if rho>0 and (cnt+1)/3001<0.05 else 'null')}**")

# ---------- 記述②〜⑥ ----------
P("\n## 記述② 帯 C（ET 13–14 時決着）")
Cc = [c["sl_slip"] for c in sl_an if c["C"]]; nC = [c["sl_slip"] for c in sl_an if not c["C"]]
if len(Cc) >= 3:
    d, t, se = welch(Cc, nC); P(f"- 帯 C n {len(Cc)} mean {np.mean(Cc):+.3f} vs 他 {np.mean(nC):+.3f} Δ {d:+.3f} t {t:+.2f} MDE {2*se:.3f}")
P("\n## 記述③ entry slip_pt（全 closed・符号つき）× ET 建玉時刻 2 時間帯")
en = [c for c in closed if c["slip"] is not None and c["h_in"] is not None]
ev = np.array([c["slip"] for c in en])
P(f"- 全体 n {len(en)} 中央値 {np.median(ev):+.3f} 平均 {ev.mean():+.3f} |slip| 中央値 {np.median(np.abs(ev)):.3f} p90 {np.percentile(np.abs(ev),90):.3f}  正率 {np.mean(ev>0):.2f}")
P("| ET 建玉帯 | n | 平均 slip | 平均 |slip| |"); P("|---|---|---|---|")
for h0 in range(0, 24, 2):
    g = np.array([c["slip"] for c in en if h0 <= c["h_in"] <= h0+1])
    if len(g): P(f"| {h0:02d}–{h0+1:02d} | {len(g)} | {g.mean():+.3f} | {np.abs(g).mean():.3f} |")
P("\n## 記述④ tp_fill_ok（TP 本）× ET 決着帯")
tp = [c for c in closed if c["er"] == "TP" and c["tp_ok"] is not None]
P(f"- TP 本 {sum(1 for c in closed if c['er']=='TP')}・注釈 {len(tp)}・False 率 {np.mean([not c['tp_ok'] for c in tp]) if tp else float('nan'):.3f}")
fb = collections.defaultdict(list)
for c in tp: fb[(c["h"]//4)*4].append(not c["tp_ok"])
P("  4 時間帯 False 率: " + ", ".join(f"ET{h:02d}–{h+3:02d}: {np.mean(x):.2f}(n{len(x)})" for h, x in sorted(fb.items())))
P("\n## 記述⑤ R 単位 執行コスト cost_R = (spread + |slip| + sl_slip·1{SL}) / risk")
cc = [c for c in closed if c["slip"] is not None and c["spread"] is not None and (c["er"] != "SL" or c["sl_slip"] is not None)]
cr = np.array([(c["spread"] + abs(c["slip"]) + (c["sl_slip"] if c["er"] == "SL" else 0.0)) / c["risk"] for c in cc])
P(f"- n {len(cc)} 中央値 {np.median(cr):.4f}R 平均 {cr.mean():.4f}R p90 {np.percentile(cr,90):.4f}R（c25: 0.0306R 中央値・0.21 USD）；spread 中央値 {np.median([c['spread'] for c in cc]):.3f} USD")
P("| ET 決着帯(4h) | n | cost_R 平均 | 中央値 | SL 比 |"); P("|---|---|---|---|---|")
for h0 in range(0, 24, 4):
    g = [c for c in cc if h0 <= c["h"] <= h0+3]
    if g:
        x = np.array([(c["spread"] + abs(c["slip"]) + (c["sl_slip"] if c["er"]=="SL" else 0.0))/c["risk"] for c in g])
        P(f"| {h0:02d}–{h0+3:02d} | {len(g)} | {x.mean():.4f} | {np.median(x):.4f} | {np.mean([c['er']=='SL' for c in g]):.2f} |")
P("\n## 記述⑥ コストの集中度（SL 本の決着帯シェア × 帯の滑り）")
shA = np.mean([c["A"] for c in sl_an]); mA = np.mean([c["sl_slip"] for c in sl_an if c["A"]]) if any(c["A"] for c in sl_an) else float("nan")
tot = sum(c["sl_slip"] for c in sl_an); totA = sum(c["sl_slip"] for c in sl_an if c["A"])
P(f"- SL 決着の帯 A シェア {shA:.2f}（本数）・帯 A の滑り合計シェア {totA/tot if tot else float('nan'):.2f}；帯 C 本数シェア {np.mean([c['C'] for c in sl_an]):.2f}・滑り合計シェア {sum(c['sl_slip'] for c in sl_an if c['C'])/tot if tot else float('nan'):.2f}")
vr = np.sort(np.array([c['sl_slip']/c['risk'] for c in sl_an]))
P(f"- 全 SL 滑り合計 {tot:+.2f} USD / SL 本 {len(sl_an)}；R 換算 合計 {vr.sum():+.3f}R（上位 1 本除外 {vr[:-1].sum():+.3f}・上位 3 本除外 {vr[:-3].sum():+.3f}・中央値 {np.median(vr):.4f}R/本）（台帳 gross ΣR {sum(c['R'] for c in closed if c['R'] is not None):+.1f}R）")

# ---------- 事後（判定外）: 外れ値・週末再開・頑健版 ----------
P("\n## 事後（判定外） 外れ値の正体・日曜再開の SL・頑健版 H_S1")
top = sorted(sl_an, key=lambda c: -c["sl_slip"])[:5]
for c in top:
    dt_e = datetime.fromtimestamp(c["exit_time"], timezone.utc).astimezone(ET); dt_i = datetime.fromtimestamp(c["entry_time"], timezone.utc).astimezone(ET)
    P(f"- {c['id']} slip {c['sl_slip']:+.3f} USD = {c['sl_slip']/c['risk']:.3f}R  risk {c['risk']:.2f}  建玉 ET {dt_i.strftime('%m-%d %a %H:%M')} → 決着 ET {dt_e.strftime('%m-%d %a %H:%M')}  hold {c['hold']}  {c['side']}  spread {c['spread']}")
def is_sun_reopen(c):
    d = datetime.fromtimestamp(c["exit_time"], timezone.utc).astimezone(ET); return d.weekday() == 6 and d.hour == 18
sun = [c for c in sl_an if is_sun_reopen(c)]; oth = [c for c in sl_an if not is_sun_reopen(c)]
if sun:
    P(f"- 日曜再開 18 時 ET で SL 決着 n {len(sun)}（SL 本の {len(sun)/len(sl_an):.1%}）: 滑り 平均 {np.mean([c['sl_slip'] for c in sun]):+.3f} 中央値 {np.median([c['sl_slip'] for c in sun]):+.3f} max {max(c['sl_slip'] for c in sun):+.3f} USD・R 換算 平均 {np.mean([c['sl_slip']/c['risk'] for c in sun]):+.3f}R  vs 他 平均 {np.mean([c['sl_slip'] for c in oth]):+.3f} 中央値 {np.median([c['sl_slip'] for c in oth]):+.3f}・R 平均 {np.mean([c['sl_slip']/c['risk'] for c in oth]):+.4f}R")
    P(f"  日曜再開 SL の滑り合計 {sum(c['sl_slip']/c['risk'] for c in sun):+.3f}R = 全 SL 滑り（R）の {sum(c['sl_slip']/c['risk'] for c in sun)/vr.sum():.0%}；週末持ち越し closed 本（建玉 金曜 ∧ 決着 日曜以降）{sum(1 for c in closed if datetime.fromtimestamp(c['entry_time'],timezone.utc).astimezone(ET).weekday()==4 and datetime.fromtimestamp(c['exit_time'],timezone.utc).astimezone(ET).date()>datetime.fromtimestamp(c['entry_time'],timezone.utc).astimezone(ET).date()+__import__('datetime').timedelta(days=1))}")
A = np.array([c["sl_slip"] for c in sl_an if c["A"]]); B = np.array([c["sl_slip"] for c in sl_an if not c["A"]])
cap = np.quantile(np.concatenate([A, B]), 0.95); wA, wB = np.minimum(A, cap), np.minimum(B, cap)
d, t, se = welch(wA, wB)
pool = np.concatenate([A, B]); obs = np.median(A) - np.median(B); cnt = 0
for _ in range(5000):
    rng.shuffle(pool); cnt += (np.median(pool[:len(A)]) - np.median(pool[len(A):])) >= obs
P(f"- 頑健版（全体・winsor 95% cap {cap:.3f}）帯 A−B Δ {d:+.3f} t {t:+.2f} MDE {2*se:.3f}；中央値差 {obs:+.3f} 置換 p(片側) {(cnt+1)/5001:.3f}")
P(f"\n実行 {time.time()-T0:.1f} s・読んだのは {LEDGER} のみ・書込 {OUT}")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
