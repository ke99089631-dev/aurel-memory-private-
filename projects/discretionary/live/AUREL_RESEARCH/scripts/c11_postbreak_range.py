# -*- coding: utf-8 -*-
"""
c11: 会長仮説(2026-11-06)「ブレイク終了→止まって反発→レンジ=負けゾーン／レンジを綺麗に抜けた後の第二波=稼ぎどき／
     溜まり(横×縦)が大きいほど次の動きが大きい(地震の原理)」の一次計測。
読むだけ。入力 = setup_ledger.jsonl(読取) + data/bars_m5_merged_1008_1105.json(M5 10-08..11-05)。MT5なし・発注なし。
定義(事前固定 v1・測るための固定):
  大波   = 1時間(12本)の値幅 |close_i - close_{i-12}| >= 0.5 x 直前24h箱の高さ
  大波齢 = ブレイク足から直前の大波の終端までの時間(時間)。小さい=ブレイク直後のレンジ
  溜まりD= ブレイク足の直前で、高安の幅が 0.5x24h箱 以内に収まり続けた本数(横)
  溜まりH= その帯の高さ(縦・pt)   エネルギー = D x H
  帯内壁 = 壊した壁が溜まり帯の内側にある(=レンジ内の壁を抜けた)か
  事後の動き = 壁から順方向に4時間(48本)で伸びた最大幅(pt)・トレードと独立
"""
import json, os, sys, io, math, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, LIVE)
import serve_chart as sc  # _load_setups/_net_R/_cost_model (読取のみ)

BARS = os.path.join(LIVE, "AUREL_RESEARCH", "data", "bars_m5_merged_1008_1105.json")
OUT = os.path.join(LIVE, "AUREL_RESEARCH", "data", "c11_postbreak_range_result.md")
LEG_FR, BAND_FR, LOOK, FWD = 0.5, 0.5, 288, 48
JST = dt.timezone(dt.timedelta(hours=9))

bars = json.load(open(BARS, encoding="utf-8"))["bars"]
T = [b["time"] for b in bars]; H = [b["high"] for b in bars]; L = [b["low"] for b in bars]; C = [b["close"] for b in bars]
idx = {t: i for i, t in enumerate(T)}

def box_h(i):
    return max(H[i-LOOK:i]) - min(L[i-LOOK:i])

def leg_age(i):
    """直前の大波の終端(本数)と向き。見つからなければ None"""
    bh = box_h(i)
    for j in range(i-1, LOOK+12, -1):
        mv = C[j] - C[j-12]
        if abs(mv) >= LEG_FR * bh:
            return (i - j) * 5 / 60.0, (1 if mv > 0 else -1)
    return None, 0

def band(i):
    bh = box_h(i); lim = BAND_FR * bh
    hi, lo, d = H[i-1], L[i-1], 1
    while i-1-d >= 0 and d < LOOK:
        nh, nl = max(hi, H[i-1-d]), min(lo, L[i-1-d])
        if nh - nl > lim: break
        hi, lo, d = nh, nl, d+1
    return d, hi - lo, lo, hi

def fwd_move(i, direction, wall):
    seg = range(i, min(len(T), i+FWD))
    if direction > 0: return max(H[k] for k in seg) - wall
    return wall - min(L[k] for k in seg)

recs = sc._load_setups(); cm = sc._cost_model()
rows = []
for r in recs:
    bt = r.get("break_time"); i = idx.get(bt)
    if i is None or i < LOOK + 13: continue
    d = 1 if r.get("dir") == "UP" else -1
    age, legdir = leg_age(i)
    D, bandH, blo, bhi = band(i)
    wall = float(r["wall"]); m = 0.1 * bandH
    in_band = (blo + m) < wall < (bhi - m)
    row = {"id": r["id"], "kind": r.get("wall_kind"), "dir": d, "age_h": age, "legdir": legdir,
           "D": D, "bandH": round(bandH, 2), "energy": D * bandH, "in_band": in_band,
           "boxH": round(box_h(i), 2), "fwd": round(fwd_move(i, d, wall), 2), "bt": bt}
    ra = r.get("reaccel") if isinstance(r.get("reaccel"), dict) else None
    if ra and ra.get("status") == "closed" and ra.get("R") is not None:
        fake = {"R": ra["R"], "entry": ra.get("entry"), "sl": ra.get("sl"), "entry_time": ra.get("entry_time"),
                "jst_hour": r.get("jst_hour"), "exit_reason": ra.get("exit_reason")}
        row["R_re"] = sc._net_R(fake, cm)[0]
    if r.get("status") == "closed" and r.get("R") is not None and r.get("tp_fill_ok") is not False:
        row["R_main"] = sc._net_R(r, cm)[0]
    rows.append(row)

out = []
def P(s=""): out.append(s); print(s)

def st(rs, key):
    xs = [x[key] for x in rs if x.get(key) is not None]
    if not xs: return "n=0"
    n = len(xs); w = sum(1 for v in xs if v > 0); s = sum(xs)
    return f"n={n:3d} 勝率{100*w/n:3.0f}% 合計{s:+6.2f}R 平均{s/n:+.3f}"

def terciles(rs, feat, key, labels=None):
    rs = [x for x in rs if x.get(key) is not None and x.get(feat) is not None]
    if len(rs) < 9: P(f"  {feat}: n不足"); return
    v = sorted(x[feat] for x in rs); q1, q2 = v[len(v)//3], v[2*len(v)//3]
    for name, sel in (("低", lambda x: x[feat] <= q1), ("中", lambda x: q1 < x[feat] <= q2), ("高", lambda x: x[feat] > q2)):
        g = [x for x in rs if sel(x)]
        P(f"  {feat} {name}({min(x[feat] for x in g):.1f}〜{max(x[feat] for x in g):.1f}): {st(g, key)}")

def spearman(xs, ys):
    def rk(a):
        o = sorted(range(len(a)), key=lambda k: a[k]); r = [0]*len(a)
        for p, k in enumerate(o): r[k] = p
        return r
    rx, ry = rk(xs), rk(ys); n = len(xs)
    if n < 3: return float("nan")
    d2 = sum((a-b)**2 for a, b in zip(rx, ry)); return 1 - 6*d2/(n*(n*n-1))

P(f"# c11 ブレイク後レンジ仮説 一次計測  窓={dt.datetime.fromtimestamp(T[LOOK],JST):%m-%d}〜{dt.datetime.fromtimestamp(T[-1],JST):%m-%d} JST  セットアップ{len(rows)}本")
P(f"大波=1hで24h箱の{LEG_FR:.0%}以上 / 溜まり帯=幅が箱の{BAND_FR:.0%}以内 / 事後の動き=壁から4h順方向の最大幅")
for key, lane in (("R_re", "再加速レーン(AIの今のレシピ)"), ("R_main", "戻り目レーン(旧)")):
    rs = [x for x in rows if x.get(key) is not None]
    P(f"\n## {lane}  {st(rs, key)}")
    P("### 直前の大波からの経過時間(時間)  ※小さい=ブレイク直後の止まり場")
    terciles(rs, "age_h", key)
    noleg = [x for x in rs if x.get("age_h") is None]
    if noleg: P(f"  24h以内に大波なし: {st(noleg, key)}")
    P("### 大波と同じ向きのブレイク(第二波)か逆向きか")
    P(f"  同方向(第二波候補): {st([x for x in rs if x['legdir']==x['dir']], key)}")
    P(f"  逆方向(反発側):     {st([x for x in rs if x['legdir']==-x['dir']], key)}")
    P("### 溜まりの横(本数D)・縦(帯の高さH pt)・エネルギーD×H")
    terciles(rs, "D", key); terciles(rs, "bandH", key); terciles(rs, "energy", key)
    P("### 壊した壁が溜まり帯の内側か(=レンジ内の壁)")
    P(f"  帯内の壁: {st([x for x in rs if x['in_band']], key)}")
    P(f"  帯の縁/外の壁: {st([x for x in rs if not x['in_band']], key)}")
    P("### 大波齢 × 帯内壁 (負けゾーン候補=齢が短い×帯内)")
    aged = [x for x in rs if x.get("age_h") is not None]
    if aged:
        med = sorted(x["age_h"] for x in aged)[len(aged)//2]
        for nm, sel in (("齢短×帯内", lambda x: x["age_h"] <= med and x["in_band"]), ("齢短×帯外", lambda x: x["age_h"] <= med and not x["in_band"]),
                        ("齢長×帯内", lambda x: x["age_h"] > med and x["in_band"]), ("齢長×帯外", lambda x: x["age_h"] > med and not x["in_band"])):
            P(f"  {nm}(中央値{med:.1f}h): {st([x for x in aged if sel(x)], key)}")

P("\n## 地震仮説: 溜まり(D×H) と 事後の動き(壁から4hの順方向最大幅・トレードと独立) の相関(スピアマン)")
for kind in ("outer", "mid", None):
    rs = [x for x in rows if kind is None or x["kind"] == kind]
    if len(rs) < 10: continue
    e = [x["energy"] for x in rs]; f = [x["fwd"] for x in rs]; fb = [x["fwd"]/x["boxH"] for x in rs]
    P(f"  {kind or '全部'} n={len(rs)}  D×H vs 動き(pt) ρ={spearman(e,f):+.2f} / D vs 動き ρ={spearman([x['D'] for x in rs],f):+.2f} / H vs 動き ρ={spearman([x['bandH'] for x in rs],f):+.2f} / D×H vs 動き(箱比) ρ={spearman(e,fb):+.2f}")
    v = sorted(e); q1, q2 = v[len(v)//3], v[2*len(v)//3]
    for nm, sel in (("低", lambda x: x["energy"] <= q1), ("中", lambda x: q1 < x["energy"] <= q2), ("高", lambda x: x["energy"] > q2)):
        g = [x for x in rs if sel(x)]; mf = sorted(x["fwd"] for x in g)[len(g)//2]
        P(f"    エネルギー{nm}: n={len(g)} 事後の動き中央値 {mf:.1f}pt  箱比中央値 {sorted(x['fwd']/x['boxH'] for x in g)[len(g)//2]:.2f}")

P("\n注: 窓は約4週間・サンプル不足。定義v1は測るための固定で永続でない。レシピは不変・フィルタに使わない。")
open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("saved:", OUT)
