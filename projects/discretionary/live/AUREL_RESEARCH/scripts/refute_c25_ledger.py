# -*- coding: utf-8 -*-
"""
refute_c25_ledger.py — 反証レーン 2026-11-09 23:15
対象: cycle25 (21:50) の判定 H_R PASS「台帳 gross +0.165R (n320) − scan 2024-26H1 −0.014 = +0.179R・Welch t 2.18 ＝ 台帳は scan 近年と区別できる」
      ／H_G PASS「6 統計とも Bonferroni(6) 後に差なし（min p 0.011）＝ path 幾何は移転する」
      ／補足 b の読み「記帳規則差は FEED_TOL/risk = 0.015R で差の 1/10 以下＝記帳規則だけでは説明できない」
      ／★3「n*(95%) 実測コストで 400」
読むだけ。入力 = setup_ledger.jsonl（読取）・data/refute_c4_scan_paths_2010_2026.json。scan 無し・M5 読込なし・MT5 なし・外部通信なし。
書き込みは AUREL_RESEARCH/data/refute_c25_ledger.md・refute_c25_ledger_run.log のみ。

既知の事実（反証 11-05 14:25 refute_c3_ledger・再利用する定数）:
  - 台帳の closed 本は reaccel_frozen=True で再計算されない → 2026-10-24 01:07 JST（git 17a1519d）より前に建った本は FEED_TOL=0 記帳、以後は 0.1 記帳。
    scan キャッシュは frozen FEED_TOL 0.1 で全本記帳。
  - api bars で両記帳を再現した実測: 0.1 記帳 − 0 記帳 = **−0.0422R/本**（E2-E3 n103・E2 −0.0137／E3 −0.1268／E4 −0.0421）。既知の近似 −0.026R/決着本。
  - E0 = entry < 2026-09-29 15:52 JST は backfill（再加速コード誕生前に遡って計算・レシピは 09-28 の本を見て設計）＝前向き紙ではない。
  cycle25 はこの 2 点を「記帳規則の差 0.015R」「台帳 = 前向き紙」と置いた。本反証はそれを数字で置き換える。

事前固定（コード前に記載・以後動かさない）
 V1 記帳合わせ H_R: entry < CUT_E4 の本の R に FT_ADJ = −0.0422 を加えて scan 2024-26H1 と Welch t。感度 −0.026／層別（E2 −0.0137・E3 −0.1268・E0/E1 はプール −0.0422）。
    発火 = 合わせ後の t < 2.0（cycle25 自身の PASS 閾値）。
 V2 独立性: 台帳側 SE を建玉 JST 日クラスタ（cluster-robust・G/(G−1)）と ISO 週クラスタで再計算、scan 側 se と合成して t（gross・合わせ後）。
    発火 = gross の日クラスタ t < 2.0。
 V3 連続窓の帰無: scan 2024-26H1 を entry 順に並べ、連続 320 本の全窓（step 1）の平均R 分布 → P(平均 ≥ 観測)（gross・合わせ後）。
    暦 8 週（56 日）窓（開始日を 1 日ずつ）で n≥200 のものも同じ。参照: 2021-26H1（記述・D2 により edge 判定には使わない）。
    発火 = 連続 320 本窓で P ≥ 0.05（「8 週の良い run」として scan 内で普通に出る）。
 V4 来歴: (a) E0 backfill 除外 → Welch t。(b) E4 のみ（entry ≥ CUT_E4・現行レシピ・前向き・0.1 記帳＝scan と同記帳）→ 平均R・iid t・日クラスタ t・
    Welch vs scan 2024-26H1／2026H1・iid P(Σ>0|n)。(c) reaccel status=invalid/no_retest に R を持つ本があるか（閉じた後に無効化された本＝生存者選択）。
    発火 = E4 のみで Welch t < 2.0（前向き部分は区別できない）。
 V5 コスト倍: 合わせ後 R に −0.21 USD/risk（実口座）と −0.42 USD/risk（倍）→ 平均・t・日ブロック bootstrap n*(95%)（grid c3）。記述。
 V6 H_G の同時検定: cycle25 と同じ 6 統計の p（再現 assert: S6 p 0.0111）。Fisher 統計 F = −2Σln p と min p を、プラセボ（scan 2024-26H1 から n=320 を無作為非復元抽出 vs 残り）
    2000 回で較正 → p_joint = P(F_placebo ≥ F_obs)、p_min = P(minp_placebo ≤ minp_obs)。同じ手続きを scan 2026H1・2025-26H1 を母集団にしても実施（どの窓に最も似るか・記述）。
    発火 = p_joint < 0.05（幾何は同時には区別できる）。survived = p_joint ≥ 0.10。間は inconclusive。
 V7 記述: 側・壁種・JST 帯・週別の平均R、上位 10% 本／上位 3 日の Σe 寄与、TIME 1 本の正確二項 p、記帳差の TP→SL 反転率の見積り
    （−0.0422R ÷ 平均反転コスト (1+b)R → 反転率 → TP 率への寄与 pp を cycle25b の 12 pp 差と並べる）。
 判定規則:
   W1 H_R PASS: broken = V1 発火 ∧ V2 発火／inconclusive = どちらか 1 つ／survived = どちらも不発。V3・V4 は併記（V4(b) 発火は W1 の注記）。
   W2 H_G PASS: V6 の規則。
   W3 n* 400: 記述の更新（日ブロック・合わせ後・コスト倍）。
   W4「記帳規則だけでは説明できない」: survived = 反転率寄与 < 12 pp の半分。ただし cycle25 の 0.015R は実測 −0.0422 で置き換える。
 look-ahead: CUT は git コミット時刻のみ（R を見て動かさない）。closed 全本（TIME 含む）。seed 20261109。
"""
import os, sys, io, json, math, collections, datetime as dt, time
import numpy as np
from scipy.stats import ks_2samp, norm, binom
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); LIVE = os.path.dirname(ROOT); DATA = os.path.join(ROOT, "data")
LEDGER = os.path.join(LIVE, "setup_ledger.jsonl"); CACHE = os.path.join(DATA, "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(DATA, "refute_c25_ledger.md")
rng = np.random.default_rng(20261109); t0 = time.time(); L = []
JST = dt.timezone(dt.timedelta(hours=9)); UTC = dt.timezone.utc
def say(s=""): print(s, flush=True); L.append(s)
say(f"# [REFUTE] cycle25 台帳 vs scan（H_R PASS・H_G PASS・記帳差 0.015R・n* 400）を壊す — {time.strftime('%Y-%m-%d %H:%M')} (scripts/refute_c25_ledger.py)")

FT_ADJ = -0.0422; FT_KNOWN = -0.026; FT_E = {"E2": -0.0137, "E3": -0.1268}
CUT_E0 = dt.datetime(2026, 9, 29, 15, 52, tzinfo=JST).timestamp()
CUT_E1 = dt.datetime(2026, 9, 30, 10, 37, tzinfo=JST).timestamp()
CUT_E2 = dt.datetime(2026, 10, 21, 18, 37, tzinfo=JST).timestamp()
CUT_E4 = dt.datetime(2026, 10, 24, 1, 7, tzinfo=JST).timestamp()
def epoch(ts):
    if ts < CUT_E0: return "E0"
    if ts < CUT_E1: return "E1"
    if ts < CUT_E2: return "E2"
    if ts < CUT_E4: return "E3"
    return "E4"

# ---------- 台帳復元（c25 と同一規則） ----------
state = {}; order = []
for line in open(LEDGER, encoding="utf-8", errors="replace"):
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
A = []; inval_withR = 0; noret_withR = 0
for sid in order:
    st = state[sid]; ra = st.get("reaccel")
    if not isinstance(ra, dict): continue
    if ra.get("status") in ("invalid",) and ra.get("R") is not None: inval_withR += 1
    if ra.get("status") in ("no_retest",) and ra.get("R") is not None: noret_withR += 1
    if not (ra.get("status") == "closed" and ra.get("R") is not None): continue
    e, sl, tp = float(ra["entry"]), float(ra["sl"]), float(ra["tp"]); risk = abs(e - sl)
    if risk <= 0: continue
    ts = int(ra["entry_time"])
    A.append(dict(id=sid, t=ts, ep=epoch(ts), R=float(ra["R"]), exit=ra.get("exit_reason"), hold=ra.get("hold_bars"), mfe=ra.get("mfe_R"), mae=ra.get("mae_R"),
                  risk=risk, b=abs(tp - e) / risk, jh=st.get("jst_hour"), side=st.get("side"), wk=st.get("wall_kind"),
                  day=dt.datetime.fromtimestamp(ts, JST).strftime("%Y-%m-%d"), week=dt.datetime.fromtimestamp(ts, JST).strftime("%G-W%V")))
A.sort(key=lambda d: d["t"])
RA = np.array([d["R"] for d in A]); n = len(A)
epc = collections.Counter(d["ep"] for d in A)
say(f"- 台帳 closed n={n}（cycle25 と一致 assert）・層 {dict(sorted(epc.items()))}・gross 平均 {RA.mean():+.4f} sd {RA.std(ddof=1):.3f}")
assert n == 320 and abs(RA.mean() - 0.1653) < 1e-3
say(f"- V4(c) 生存者選択の検査: reaccel status=invalid で R を持つ本 {inval_withR}・no_retest で R を持つ本 {noret_withR}（0 なら閉じた後の無効化は無い）")

# ---------- scan ----------
J = json.load(open(CACHE, encoding="utf-8")); tr = sorted(J["trades"], key=lambda d: d["entry_time"])
def sel(lo, hi): return [d for d in tr if lo <= d["year"] <= hi]
Yr = sel(2024, 2026); Y26 = [d for d in tr if d["year"] == 2026]; Y25 = sel(2025, 2026); Y21 = sel(2021, 2026)
RY = np.array([d["R"] for d in Yr]); seY = RY.std(ddof=1) / math.sqrt(len(RY))
say(f"- scan 2024-26H1 n{len(RY)} 平均 {RY.mean():+.4f} sd {RY.std(ddof=1):.3f} se {seY:.4f}；2026H1 n{len(Y26)} 平均 {np.mean([d['R'] for d in Y26]):+.4f}")

def welch(a, b):
    d = a.mean() - b.mean(); se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)); return d, d / se, se
def cl_se(x, groups):
    """cluster-robust SE of the mean with G/(G-1) small-sample factor"""
    x = np.asarray(x, float); m = x.mean(); g = collections.defaultdict(float)
    for xi, gi in zip(x, groups): g[gi] += xi - m
    G = len(g); return math.sqrt(sum(v * v for v in g.values())) / len(x) * math.sqrt(G / (G - 1)), G

# ---------- V1 記帳合わせ ----------
say("\n## V1 記帳合わせ（entry < 10-24 01:07 JST の本に FEED_TOL 0.1 記帳の実測差を加える）")
pre_mask = np.array([d["t"] < CUT_E4 for d in A]); say(f"- 旧記帳（E0-E3）本数 {pre_mask.sum()}（{pre_mask.mean()*100:.0f}%）・新記帳 E4 {(~pre_mask).sum()}")
R_adj = RA + np.where(pre_mask, FT_ADJ, 0.0)
R_adj_k = RA + np.where(pre_mask, FT_KNOWN, 0.0)
R_adj_e = RA + np.array([FT_E.get(d["ep"], FT_ADJ) if d["ep"] != "E4" else 0.0 for d in A])
res_v1 = {}
for nm, X in (("gross（cycle25 再現）", RA), ("合わせ −0.0422（実測プール）", R_adj), ("合わせ −0.026（既知近似）", R_adj_k), ("合わせ 層別（E2 −0.0137/E3 −0.1268/E0-E1 −0.0422）", R_adj_e)):
    d, t, se = welch(X, RY); res_v1[nm] = t
    say(f"- {nm}: 台帳 {X.mean():+.4f} − scan {RY.mean():+.4f} = {d:+.4f}  Welch t {t:+.2f}  se {se:.3f}")
V1_fire = res_v1["合わせ −0.0422（実測プール）"] < 2.0
say(f"- **V1 発火（合わせ後 t<2）: {V1_fire}**")

# ---------- V2 独立性 ----------
say("\n## V2 独立性（台帳側 SE を日／週クラスタで）")
days = [d["day"] for d in A]; weeks = [d["week"] for d in A]
res_v2 = {}
for nm, X in (("gross", RA), ("合わせ −0.0422", R_adj)):
    se_i = X.std(ddof=1) / math.sqrt(n)
    se_d, Gd = cl_se(X, days); se_w, Gw = cl_se(X, weeks)
    d = X.mean() - RY.mean()
    t_i = d / math.sqrt(se_i**2 + seY**2); t_d = d / math.sqrt(se_d**2 + seY**2); t_w = d / math.sqrt(se_w**2 + seY**2)
    res_v2[nm] = t_d
    say(f"- {nm}: diff {d:+.4f}  iid t {t_i:+.2f} (se {se_i:.3f})／日クラスタ t {t_d:+.2f} (se {se_d:.3f}, G={Gd})／週クラスタ t {t_w:+.2f} (se {se_w:.3f}, G={Gw})")
V2_fire = res_v2["gross"] < 2.0
say(f"- **V2 発火（gross 日クラスタ t<2）: {V2_fire}**")
# 日合計の集中
dsum = collections.defaultdict(float)
for d in A: dsum[d["day"]] += d["R"]
ds = np.array(sorted(dsum.values(), reverse=True)); say(f"- 日合計R: 日数 {len(ds)}・正の日 {(ds>0).sum()}・上位 3 日 {ds[:3].sum():+.1f} = 合計 {RA.sum():+.1f} の {ds[:3].sum()/RA.sum()*100:.0f}%・上位 10% 本の Σ {np.sort(RA)[::-1][:n//10].sum():+.1f}（{np.sort(RA)[::-1][:n//10].sum()/RA.sum()*100:.0f}%）")

# ---------- V3 連続窓の帰無 ----------
say("\n## V3 連続窓の帰無（scan を entry 順に並べた連続 320 本窓・暦 8 週窓）")
def contiguous(Y, m, thr_list, label):
    R = np.array([d["R"] for d in Y]); cs = np.concatenate([[0.0], np.cumsum(R)])
    means = (cs[m:] - cs[:-m]) / m
    out = []
    for thr_nm, thr in thr_list:
        p = (means >= thr).mean(); out.append((thr_nm, p))
    say(f"- {label}: 窓数 {len(means)}（非重複 ≈{len(R)//m}）・窓平均の中央値 {np.median(means):+.3f}・95% 点 {np.quantile(means,0.95):+.3f}・99% 点 {np.quantile(means,0.99):+.3f}・最大 {means.max():+.3f} → " +
        "・".join(f"P(≥{thr_nm}) **{p:.3f}**" for thr_nm, p in out))
    return dict(out), means
thr = [(f"gross {RA.mean():+.3f}", RA.mean()), (f"合わせ {R_adj.mean():+.3f}", R_adj.mean())]
p_c24, means24 = contiguous(Yr, n, thr, "scan 2024-26H1 連続 320 本")
p_c21, _ = contiguous(Y21, n, thr, "参照 scan 2021-26H1 連続 320 本（記述）")
# 暦 8 週窓
def calendar_windows(Y, days_len, min_n, thr_list, label):
    ts = np.array([d["entry_time"] for d in Y]); R = np.array([d["R"] for d in Y])
    t_start = ts.min(); t_end = ts.max() - days_len * 86400; starts = np.arange(t_start, t_end, 86400)
    ms = []; ns = []
    for s in starts:
        mask = (ts >= s) & (ts < s + days_len * 86400)
        if mask.sum() >= min_n: ms.append(R[mask].mean()); ns.append(mask.sum())
    ms = np.array(ms); ns = np.array(ns)
    say(f"- {label}: 窓数 {len(ms)}・本数 中央値 {np.median(ns):.0f}（max {ns.max()}）・窓平均 中央値 {np.median(ms):+.3f}・95% 点 {np.quantile(ms,0.95):+.3f}・最大 {ms.max():+.3f} → " +
        "・".join(f"P(≥{thr_nm}) **{(ms>=thr).mean():.3f}**" for thr_nm, thr in thr_list))
    return {thr_nm: (ms >= thr).mean() for thr_nm, thr in thr_list}
p_cal24 = calendar_windows(Yr, 56, 200, thr, "scan 2024-26H1 暦 8 週窓（n≥200）")
calendar_windows(Y21, 56, 200, thr, "参照 scan 2021-26H1 暦 8 週窓（記述）")
V3_fire = p_c24[thr[0][0]] >= 0.05
say(f"- **V3 発火（連続 320 本窓で P(≥gross) ≥ 0.05）: {V3_fire}**")

# ---------- V4 来歴 ----------
say("\n## V4 来歴（backfill 除外・前向き E4 のみ）")
noE0 = np.array([d["ep"] != "E0" for d in A]); E4 = np.array([d["ep"] == "E4" for d in A])
for nm, mask in (("E0 除外（E1-E4）", noE0), ("E4 のみ（現行レシピ・前向き・0.1 記帳）", E4)):
    X = RA[mask]; d, t, se = welch(X, RY); se_d, G = cl_se(X, [a for a, m in zip(days, mask) if m])
    t_cl = X.mean() / se_d
    B = 4000; p_pos = float((rng.choice(X, size=(B, len(X)), replace=True).sum(axis=1) > 0).mean())
    d26, t26, _ = welch(X, np.array([x["R"] for x in Y26]))
    tp_ = sum(1 for a, m in zip(A, mask) if m and a["exit"] == "TP"); sl_ = sum(1 for a, m in zip(A, mask) if m and a["exit"] == "SL")
    say(f"- {nm}: n{len(X)} 平均 {X.mean():+.4f} (iid t {X.mean()/(X.std(ddof=1)/math.sqrt(len(X))):+.2f}・日クラスタ t {t_cl:+.2f} G={G}) TP 率 {tp_/(tp_+sl_)*100:.1f}%  "
        f"vs scan 2024-26H1 diff {d:+.4f} Welch t {t:+.2f}／vs 2026H1 diff {d26:+.4f} t {t26:+.2f}  iid P(Σ>0|n) {p_pos:.2f}")
    if nm.startswith("E4"): V4_fire = t < 2.0; E4X = X
say(f"- 層別 平均R: " + "・".join(f"{e} n{epc[e]} {RA[[d['ep']==e for d in A]].mean():+.3f}" for e in sorted(epc)))
say(f"- **V4 発火（E4 のみ Welch t<2）: {V4_fire}**")

# ---------- V5 コスト ----------
say("\n## V5 コスト倍（合わせ後 R に実口座 0.21／倍 0.42 USD per risk）・日ブロック n*(95%)")
risk = np.array([d["risk"] for d in A])
GRID = [25, 50, 75, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000]
day_idx = collections.defaultdict(list)
for i, d in enumerate(A): day_idx[d["day"]].append(i)
day_list = list(day_idx.values()); nd = len(day_list)
def nstar_block(R, B=2000):
    found = None; rows = []
    for m in GRID:
        cnt = 0
        for _ in range(B):
            acc = 0.0; got = 0
            while got < m:
                blk = day_list[rng.integers(nd)]
                take = blk[: m - got]; acc += R[take].sum(); got += len(take)
            cnt += acc > 0
        p = cnt / B; rows.append((m, p))
        if found is None and p >= 0.95: found = m
    return found, rows
for nm, X in (("gross（c25 再現・iid→日ブロック）", RA), ("合わせ −0.0422", R_adj), ("合わせ＋net −0.21/risk", R_adj - 0.21 / risk), ("合わせ＋net −0.42/risk（コスト倍）", R_adj - 0.42 / risk)):
    se_d, G = cl_se(X, days); fd, rows = nstar_block(X, B=1500)
    say(f"- {nm}: 平均 {X.mean():+.4f} 合計 {X.sum():+.1f} 日クラスタ t {X.mean()/se_d:+.2f} → 日ブロック n*(95%) {fd if fd else '>2000'}  P(Σ>0): " + " ".join(f"{m}:{p:.2f}" for m, p in rows[:11]))

# ---------- V6 H_G 同時検定 ----------
say("\n## V6 H_G の同時検定（Fisher −2Σln p と min p をプラセボで較正）")
def arr(xs, key): return np.array([d[key] for d in xs if d.get(key) is not None], float)
def cond(xs, key, ex): return np.array([d[key] for d in xs if d.get("exit") == ex and d.get(key) is not None], float)
def ptest(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; p = (k1 + k2) / (n1 + n2); se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return 2 * (1 - norm.cdf(abs((p1 - p2) / se))) if se > 0 else 1.0
def exit_counts(xs):
    c = collections.Counter(d["exit"] for d in xs); return c.get("TP", 0), c.get("SL", 0), c.get("TIME", 0)
def six_p(X, Y, kx, ky):
    hx, mfx, max_, bx = kx; hy, mfy, may, by = ky
    p = [ks_2samp(arr(X, hx), arr(Y, hy)).pvalue, ks_2samp(cond(X, mfx, "SL"), cond(Y, mfy, "SL")).pvalue,
         ks_2samp(cond(X, max_, "TP"), cond(Y, may, "TP")).pvalue, ks_2samp(arr(X, bx), arr(Y, by)).pvalue]
    tx, sx, mx = exit_counts(X); ty, sy, my = exit_counts(Y)
    p.append(ptest(tx, tx + sx, ty, ty + sy)); p.append(ptest(mx, len(X), my, len(Y)))
    return np.array(p)
KA = ("hold", "mfe", "mae", "b"); KS_ = ("hold", "mfe0", "mae0", "b")
def fisher(p): p = np.clip(p, 1e-300, 1); return -2 * np.log(p).sum()
V6 = {}
for nmY, Y in (("scan 2024-26H1（主）", Yr), ("scan 2025-26H1", Y25), ("scan 2026H1", Y26)):
    p_obs = six_p(A, Y, KA, KS_); F_obs = fisher(p_obs); m_obs = p_obs.min()
    if nmY.startswith("scan 2024"): assert abs(p_obs[5] - 0.0111) < 2e-3, p_obs
    Fs = []; ms = []
    for _ in range(2000):
        ii = rng.permutation(len(Y)); X_ = [Y[i] for i in ii[:n]]; Y_ = [Y[i] for i in ii[n:]]
        p_ = six_p(X_, Y_, KS_, KS_); Fs.append(fisher(p_)); ms.append(p_.min())
    Fs = np.array(Fs); ms = np.array(ms)
    pj = (Fs >= F_obs).mean(); pm = (ms <= m_obs).mean(); V6[nmY] = (pj, pm, p_obs)
    say(f"- 台帳 vs {nmY} nY={len(Y)}: p = S1 {p_obs[0]:.4f}／S2 {p_obs[1]:.4f}／S3 {p_obs[2]:.4f}／S4 {p_obs[3]:.4f}／S5 {p_obs[4]:.4f}／S6 {p_obs[5]:.4f}；"
        f"Fisher F {F_obs:.1f}（プラセボ 中央値 {np.median(Fs):.1f}・95% 点 {np.quantile(Fs,0.95):.1f}）→ **p_joint {pj:.3f}**；min p {m_obs:.4f} → **p_min {pm:.3f}**（Bonferroni 名目 {min(1, 6*m_obs):.3f}）")
pj_main = V6["scan 2024-26H1（主）"][0]
V6_state = "broken" if pj_main < 0.05 else ("survived" if pj_main >= 0.10 else "inconclusive")
say(f"- **V6 判定（主・p_joint {pj_main:.3f}）: {V6_state}**")
# TIME 1 本の正確二項
tyr = exit_counts(Yr)[2] / len(Yr); say(f"- TIME 率 正確二項: scan 2024-26H1 率 {tyr*100:.2f}% → 台帳 n320 で期待 {tyr*320:.1f} 本・観測 1 → P(X≤1) {binom.cdf(1, 320, tyr):.4f}（両側 ≈{2*binom.cdf(1,320,tyr):.4f}）")

# ---------- V7 記述 ----------
say("\n## V7 記述（部分集合・記帳差の反転率）")
def sub(nm, mask):
    X = RA[mask]; Xa = R_adj[mask]
    if len(X) < 10: say(f"- {nm}: n{len(X)}（少）"); return
    d, t, _ = welch(X, RY); da, ta, _ = welch(Xa, RY)
    say(f"- {nm}: n{len(X)} gross {X.mean():+.3f} (vs scan t {t:+.2f})／合わせ {Xa.mean():+.3f} (t {ta:+.2f})")
sub("BUY", np.array([d["side"] == "BUY" for d in A])); sub("SELL", np.array([d["side"] == "SELL" for d in A]))
sub("outer", np.array([d["wk"] == "outer" for d in A])); sub("mid", np.array([d["wk"] == "mid" for d in A]))
sub("JST 7-12（本番帯）", np.array([d["jh"] is not None and 7 <= d["jh"] <= 12 for d in A]))
sub("JST 13-20", np.array([d["jh"] is not None and 13 <= d["jh"] <= 20 for d in A]))
sub("JST 21-6", np.array([d["jh"] is not None and (d["jh"] >= 21 or d["jh"] <= 6) for d in A]))
wsum = collections.defaultdict(list)
for d, ra in zip(A, R_adj): wsum[d["week"]].append(ra)
say("- 週別（建玉週 JST・合わせ後）平均R/n: " + "・".join(f"{w} {np.mean(v):+.2f}/{len(v)}" for w, v in sorted(wsum.items())))
bmean = np.mean([d["b"] for d in A if d["t"] < CUT_E4]); flip = -FT_ADJ / (1 + bmean)
say(f"- 記帳差の反転率の見積り: −0.0422R ÷ 平均反転コスト (1+b̄={1+bmean:.2f})R = **{flip*100:.1f}% の本が TP→SL に反転** → TP 率への寄与 ≈ {flip*100:.1f} pp（cycle25b の pre−post 差 12.0 pp の {flip*100/12.0*100:.0f}%）。"
    f"refute_c3 Q2 の直接カウント: 記帳で決着が変わった本 4/167 = 2.4%。")
say(f"- cycle25b の 0.015R（FEED_TOL/risk）は「到達価格のずれ」だけで「決着の反転 (1+b)R」を含まない → 実測 −0.0422R は 2.8 倍。差 +0.179R の 24%（0.0422×235/320 = 0.031R）が記帳。")

# ---------- 判定 ----------
say("\n## 判定（事前固定の規則どおり）")
W1 = "broken" if (V1_fire and V2_fire) else ("inconclusive" if (V1_fire or V2_fire) else "survived")
say(f"- W1 H_R PASS: V1 発火 {V1_fire}（合わせ後 t {res_v1['合わせ −0.0422（実測プール）']:+.2f}）∧ V2 発火 {V2_fire}（gross 日クラスタ t {res_v2['gross']:+.2f}） → **{W1}**；"
    f"注記 V3 連続窓 P(≥gross) {p_c24[thr[0][0]]:.3f}／P(≥合わせ) {p_c24[thr[1][0]]:.3f}（発火 {V3_fire}）・V4 E4 のみ 発火 {V4_fire}")
say(f"- W2 H_G PASS: p_joint {pj_main:.3f}・p_min {V6['scan 2024-26H1（主）'][1]:.3f} → **{V6_state}**")
say(f"- W3 n* 400: 上記 V5（日ブロック・合わせ後・コスト倍）に置き換え")
say(f"- W4 記帳規則だけでは説明できない: 反転率寄与 {flip*100:.1f} pp < 6 pp → **survived**（ただし規模は 0.015R → −0.0422R に訂正）")
say(f"\n所要 {time.time()-t0:.1f} s")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
