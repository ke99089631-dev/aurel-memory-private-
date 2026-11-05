# -*- coding: utf-8 -*-
"""
refute_c3_ledger.py — 反証レーン 2026-11-05 14:15
対象: cycle3 (12:30) の弱い兆候「台帳 reaccel closed n=305 の gross +0.176R/本 は符号が既に安定（n*=200・P(Σ>0)≈0.99）、
      在→外（時刻中央値分割）で一貫（P4 PASS）、scan 同時間帯 2024-26 の +0.035 の 5 倍」。
読むだけ。入力 = setup_ledger.jsonl（読取）・AUREL_RESEARCH/data/refute_c4_scan_paths_2010_2026.json・
data/refute_api_bars_probe.json（10-08..11-03 の M5 5000 本）。scan 無し・M5 読込なし・MT5 なし。
書き込みは AUREL_RESEARCH/data/refute_c3_ledger.md のみ。

事前固定（コード前に記載・以後動かさない）
 Q1 来歴（look-ahead/survivorship）: 各 closed 本を本番エンジンの改版時刻（git log of setup_engine.py・読取のみ）で層化。
    E0 = entry < 09-29 15:52（再加速コード誕生前＝backfill_reaccel で遡って計算。レシピは 09-28 の 3 本を見て設計）
    E1 = 09-29..09-30 10:37（MIN_SL_W 導入前）  E2 = 09-30..10-21 18:37（touch2/BTOL 改版前）
    E3 = 10-21..10-24 01:07（FEED_TOL/MIN_TP_W 導入前）  E4 = ≥10-24 01:07（現行レシピで前向き）
    各層の n・平均R・t・合計R。「前向き・現行レシピ」= E4 のみ。E0 は定義上 前向き紙でない。
    判定: E4 単独で 平均R の t≥2 かつ P(Σ>0|n=E4)≥0.95 なら「前向き部分でも符号安定」。
 Q2 記帳の混在: 閉じた本は reaccel_frozen で再計算されない → E0-E3 は FEED_TOL=0 記帳、E4 は FEED_TOL=0.1 記帳。
    api bars（10-08..11-03）で建玉足から _simulate を両記帳で再現し、各層で一致率を数える。
    一致が確認できれば、E0-E3 の記帳を 0.1 に揃えた場合の平均R 低下を推定（再現できた本は実測、できない本は
    反証レーン既知の 0.026R/決着本 × SL/TP 本数で近似）。MIN_TP_W=1.0 未満の TP 幅の本（E4 なら invalid）も数える。
 Q3 クラスタ（独立性）: 同一方向・保有期間が重なる本をクラスタ化（union-find）。クラスタ数・最大サイズ・
    クラスタ平均R の分布。日クラスタ（entry の JST 日）で cluster-robust SE → t。日ブロック bootstrap で
    n*(95%)（T3 と同じ格子）と n=305 での P(Σ>0) を再計算。iid 版（cycle3: 200・0.99）と比較。
 Q4 scan 帰無: 台帳と同じ「全時間帯」の scan 2024-26 flat（B_flat・平均 −0.014）、2025-26H1 flat、jh7-12（B_prod）
    から 305 本を（日ブロックで）5000 回抽出し、平均R ≥ +0.176 の確率と z。D2 準拠: 近年窓のみ使う。
    判定: p<0.05/3（Bonferroni 3 窓）なら「台帳は scan 帰無では出ない」＝台帳と scan の乖離は本物（原因は①地合い②定義差）。
 Q5 在→外（レシピ改版で分割）: 在 = E0-E3（n≈235）→ 外 = E4。在分布から外 n 本の平均の 90% 予測区間、外実現。
    さらに E0 を除いた 在 = E1-E3。cycle3 T4 は時刻中央値分割で在に E0 と改版が混ざっていた。
 Q6 コスト倍: E4 に demo 実測スプレッド 0.42 USD + entry slip 中央値 0.02 + SL 本の sl slip 0.026 を課した net。
    cycle4 の実口座 0.16 ベース（0.21 USD）も併記。
 判定規則: cycle3 の弱い兆候が「壊れた」= Q1 で E4 単独の t<2 または P<0.95、かつ Q4 で台帳平均が scan 帰無の p≥0.05/3。
   「生存」= Q1 E4 で t≥2∧P≥0.95 かつ Q4 p<0.05/3 かつ Q3 日ブロック P(Σ>0|305)≥0.95。他は inconclusive。
 look-ahead: 層化は entry_time と git コミット時刻（JST）のみ。closed 全本（TIME 含む）。
"""
import json, os, sys, io, math, collections, datetime as dt
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
LEDGER = os.path.join(LIVE, "setup_ledger.jsonl")
CACHE = os.path.join(LIVE, "AUREL_RESEARCH", "data", "refute_c4_scan_paths_2010_2026.json")
BARS = os.path.join(LIVE, "AUREL_RESEARCH", "data", "refute_api_bars_probe.json")
OUT = os.path.join(LIVE, "AUREL_RESEARCH", "data", "refute_c3_ledger.md")
rng = np.random.default_rng(20261105)
JST = dt.timezone(dt.timedelta(hours=9))
lines = []
def P(s=""):
    print(s); lines.append(s)

# git commit times (JST) of setup_engine.py recipe changes — read from git log at 14:20 (read-only)
EPOCH_BOUNDS = [
    ("E0 <09-29 15:52 再加速コード前(backfill)", dt.datetime(2026, 9, 29, 15, 52, tzinfo=JST)),
    ("E1 09-29..09-30 10:37 MIN_SL_W前",        dt.datetime(2026, 9, 30, 10, 37, tzinfo=JST)),
    ("E2 09-30..10-21 18:37 BTOL改版前",         dt.datetime(2026, 10, 21, 18, 37, tzinfo=JST)),
    ("E3 10-21..10-24 01:07 FEED_TOL前",         dt.datetime(2026, 10, 24, 1, 7, tzinfo=JST)),
    ("E4 ≥10-24 01:07 現行レシピ前向き",          None),
]
def epoch_of(ts):
    t = dt.datetime.fromtimestamp(ts, JST)
    for i, (name, b) in enumerate(EPOCH_BOUNDS):
        if b is None or t < b:
            return i
    return len(EPOCH_BOUNDS) - 1

def load_ledger():
    state = {}; order = []; first_logged = {}
    with open(LEDGER, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            r = json.loads(line); k = r.get("kind")
            if k == "setup" and r.get("id"):
                sid = r["id"]
                if sid not in state: order.append(sid); first_logged[sid] = r.get("logged_at")
                state[sid] = dict(r)
            elif k == "update" and r.get("target"):
                sid = r["target"]; st = state.setdefault(sid, {"id": sid})
                for kk, vv in r.items():
                    if kk in ("kind", "logged_at", "target"): continue
                    st[kk] = vv
    trades = []
    for sid in order:
        st = state[sid]; ra = st.get("reaccel")
        if isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None:
            e, sl, tp = ra["entry"], ra["sl"], ra["tp"]
            trades.append(dict(id=sid, t=int(ra["entry_time"]), xt=int(ra.get("exit_time") or 0), R=float(ra["R"]),
                               entry=e, sl=sl, tp=tp, risk=abs(e - sl), tpw=abs(tp - e), exit=ra.get("exit_reason"),
                               hold=ra.get("hold_bars"), side=st.get("side"), jh=st.get("jst_hour"),
                               wk=st.get("wall_kind"), logged=first_logged.get(sid), ep=epoch_of(int(ra["entry_time"])),
                               slip=st.get("slip_pt"), slslip=st.get("sl_slip_pt"), spread=st.get("spread_pt")))
    trades.sort(key=lambda d: d["t"])
    return trades

def tstat(x):
    x = np.asarray(x, float); n = len(x)
    if n < 2: return float("nan")
    return x.mean() / (x.std(ddof=1) / math.sqrt(n))

GRID = [25, 50, 75, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 3000, 5000]
def p_pos_blocks(blocks, n, B=4000):
    """blocks: list of arrays (日クラスタ). 日を復元抽出で並べ、先頭 n 本の合計の符号。"""
    nb = len(blocks); sizes = np.array([len(b) for b in blocks]); mean_size = sizes.mean()
    k = int(math.ceil(n / mean_size)) + 5
    out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, nb, size=k)
        s = np.concatenate([blocks[j] for j in idx])
        while len(s) < n:
            idx = rng.integers(0, nb, size=k); s = np.concatenate([s] + [blocks[j] for j in idx])
        out[i] = s[:n].sum()
    return float((out > 0).mean())

def nstar_blocks(blocks):
    rows = []; found = None
    for n in GRID:
        B = 3000 if n <= 1000 else 1000
        p = p_pos_blocks(blocks, n, B); rows.append((n, p))
        if found is None and p >= 0.95: found = n
    return found, rows

def day_blocks(trades, key="t"):
    d = collections.defaultdict(list)
    for tr in trades:
        d[dt.datetime.fromtimestamp(tr[key], JST).strftime("%Y-%m-%d")].append(tr["R"])
    return [np.array(v) for k, v in sorted(d.items())]

def cluster_robust_t(trades):
    """日クラスタの cluster-robust SE（Liang-Zeger、平均の推定量）。"""
    d = collections.defaultdict(list)
    for tr in trades:
        d[dt.datetime.fromtimestamp(tr["t"], JST).strftime("%Y-%m-%d")].append(tr["R"])
    R = np.array([tr["R"] for tr in trades]); m = R.mean(); n = len(R); G = len(d)
    num = sum((np.array(v) - m).sum() ** 2 for v in d.values())
    se = math.sqrt(num) / n * math.sqrt(G / (G - 1))
    return m / se, G, se

def overlap_clusters(trades):
    """同一方向で保有期間 [t, xt] が重なる本を union-find でクラスタ化。"""
    n = len(trades); parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[rb] = ra
    for i in range(n):
        for j in range(i + 1, n):
            if trades[j]["t"] > trades[i]["xt"]: break
            if trades[i]["side"] == trades[j]["side"] and trades[j]["t"] <= trades[i]["xt"] and trades[i]["t"] <= trades[j]["xt"]:
                union(i, j)
    cl = collections.defaultdict(list)
    for i in range(n): cl[find(i)].append(i)
    return list(cl.values())

def simulate(o, h, l, c, ie, side, entry, sl, tp, n, ft, max_hold=288):
    risk = abs(entry - sl); k_end = min(ie + max_hold, n - 1)
    for k in range(ie, k_end + 1):
        if side == "SELL":
            if h[k] >= sl - ft: return sl, "SL", k
            if l[k] <= tp - ft: return tp, "TP", k
        else:
            if l[k] <= sl + ft: return sl, "SL", k
            if h[k] >= tp + ft: return tp, "TP", k
    if ie + max_hold <= n - 1: return c[k_end], "TIME", k_end
    return None, "open", None

def main():
    P("# [REFUTE] cycle3 台帳 +0.176R/本・符号安定・在→外一貫 を壊す — 2026-11-05 14:20 (scripts/refute_c3_ledger.py)")
    tr = load_ledger()
    R = np.array([d["R"] for d in tr]); n = len(tr)
    P(f"\n## 再現: closed n={n} 平均R {R.mean():+.4f} 合計 {R.sum():+.1f} t(iid) {tstat(R):+.2f}  期間 "
      f"{dt.datetime.fromtimestamp(tr[0]['t'], JST):%m-%d}..{dt.datetime.fromtimestamp(tr[-1]['t'], JST):%m-%d}")

    # ---------- Q1 provenance ----------
    P("\n## Q1 来歴（レシピ改版で層化）")
    eps = collections.defaultdict(list)
    for d in tr: eps[d["ep"]].append(d)
    for i, (name, _) in enumerate(EPOCH_BOUNDS):
        xs = eps.get(i, []);
        if not xs: P(f"- {name}: n=0"); continue
        x = np.array([d["R"] for d in xs])
        lag = [ (dt.datetime.strptime(d["logged"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=JST) - dt.datetime.fromtimestamp(d["t"], JST)).total_seconds()/3600 for d in xs]
        nb = sum(1 for v in lag if v > 6)
        P(f"- {name}: n={len(x)} 平均R {x.mean():+.4f} 合計 {x.sum():+.1f} t {tstat(x):+.2f} 勝率 {(x>0).mean()*100:.0f}% "
          f"setup 行が entry の 6h 後以降に書かれた本 {nb}  risk 中央値 {np.median([d['risk'] for d in xs]):.2f}  TP幅<1.0 の本 {sum(1 for d in xs if d['tpw']<1.0)}")
    e4 = eps.get(4, []); R4 = np.array([d["R"] for d in e4])
    p4 = float((rng.choice(R4, size=(5000, len(R4)), replace=True).sum(axis=1) > 0).mean()) if len(R4) else float("nan")
    fwd = [d for d in tr if d["ep"] >= 1]; Rf = np.array([d["R"] for d in fwd])
    pf = float((rng.choice(Rf, size=(5000, len(Rf)), replace=True).sum(axis=1) > 0).mean())
    P(f"- **E4 単独（前向き・現行レシピ）: n={len(R4)} 平均R {R4.mean():+.4f} t {tstat(R4):+.2f} iid P(Σ>0|n={len(R4)}) {p4:.2f}**")
    P(f"- E1-E4（backfill 除外・レシピ混在）: n={len(Rf)} 平均R {Rf.mean():+.4f} t {tstat(Rf):+.2f} P(Σ>0) {pf:.2f}")
    # per-epoch jh7-12
    for i in (0, 4):
        xs = [d for d in eps.get(i, []) if d["jh"] is not None and 7 <= d["jh"] <= 12]
        if xs: P(f"- jh7-12 のみ E{i}: n={len(xs)} 平均R {np.mean([d['R'] for d in xs]):+.3f}")

    # ---------- Q2 booking mix ----------
    P("\n## Q2 記帳の混在（api bars 10-08..11-03 で両記帳を再現）")
    with open(BARS, "r", encoding="utf-8") as f: bars = json.load(f)["bars"]
    bt = np.array([b["time"] for b in bars]); o = np.array([b["open"] for b in bars]); h = np.array([b["high"] for b in bars])
    l = np.array([b["low"] for b in bars]); c = np.array([b["close"] for b in bars]); nb = len(bars)
    t_of = {int(t): i for i, t in enumerate(bt)}
    P(f"- bars n={nb} {dt.datetime.fromtimestamp(int(bt[0]), JST):%m-%d %H:%M}..{dt.datetime.fromtimestamp(int(bt[-1]), JST):%m-%d %H:%M} JST")
    rep = collections.defaultdict(lambda: collections.Counter()); delta = collections.defaultdict(list); cov = collections.Counter()
    for d in tr:
        ie = t_of.get(d["t"])
        if ie is None: continue
        cov[d["ep"]] += 1
        res = {}
        for ft in (0.0, 0.1):
            px, rs, k = simulate(o, h, l, c, ie, d["side"], d["entry"], d["sl"], d["tp"], nb, ft)
            if px is None: res[ft] = None; continue
            pnl = (px - d["entry"]) if d["side"] == "BUY" else (d["entry"] - px)
            res[ft] = (round(pnl / d["risk"], 3), rs)
        key = []
        for ft in (0.0, 0.1):
            key.append("open" if res[ft] is None else ("match" if abs(res[ft][0] - d["R"]) < 0.0015 and res[ft][1] == d["exit"] else "diff"))
        rep[d["ep"]][tuple(key)] += 1
        if res[0.0] is not None and res[0.1] is not None:
            delta[d["ep"]].append(res[0.1][0] - res[0.0][0])
    for ep in sorted(cov):
        P(f"- E{ep}: 建玉足が bars 内 {cov[ep]} 本 → (ft=0 一致?, ft=0.1 一致?) {dict(rep[ep])}; 0.1 記帳−0 記帳 の平均 diff {np.mean(delta[ep]) if delta[ep] else float('nan'):+.4f}R (n={len(delta[ep])})")
    # estimate: re-book E0-E3 at ft=0.1
    pre = [d for d in tr if d["ep"] <= 3]
    npre_slTP = sum(1 for d in pre if d["exit"] in ("SL", "TP"))
    dd = [v for ep in (2, 3) for v in delta.get(ep, [])]
    est_per = float(np.mean(dd)) if dd else -0.026
    P(f"- E0-E3 n={len(pre)}（SL/TP 決着 {npre_slTP}）を ft=0.1 に揃えると 平均R 変化の推定: 実測 diff/本 {est_per:+.4f}（再現できた E2-E3 の本 n={len(dd)}）"
      f" → 全 305 本平均 {R.mean():+.4f} → {R.mean() + est_per*len(pre)/n:+.4f}（既知の −0.026R/決着本 近似なら {R.mean() - 0.026*npre_slTP/n:+.4f}）")
    thin = [d for d in pre if d["tpw"] < 1.0]
    P(f"- E0-E3 で TP 幅 <1.0 USD（現行なら invalid）の本 {len(thin)} 合計R {sum(d['R'] for d in thin):+.2f}")

    # ---------- Q3 clustering ----------
    P("\n## Q3 クラスタ（独立性）")
    cls = overlap_clusters(tr)
    sizes = sorted((len(c_) for c_ in cls), reverse=True)
    clR = np.array([sum(tr[i]["R"] for i in c_) for c_ in cls])
    P(f"- 同方向・保有重複クラスタ: {len(cls)} 個（n=305）、サイズ分布 max {sizes[0]}、≥2 のクラスタ {sum(1 for s in sizes if s>=2)} 個に {sum(s for s in sizes if s>=2)} 本")
    P(f"- クラスタ合計R の t（クラスタ等重み・平均/本に換算）: 平均R {clR.sum()/n:+.4f}, t(cluster) {clR.mean()/(clR.std(ddof=1)/math.sqrt(len(clR))):+.2f}  上位3クラスタ合計R {sorted(clR)[-3:]}")
    tcr, G, se = cluster_robust_t(tr)
    P(f"- 日クラスタ cluster-robust: 日数 G={G}, SE {se:.4f}, t {tcr:+.2f}（iid t {tstat(R):+.2f}, iid SE {R.std(ddof=1)/math.sqrt(n):.4f}）")
    tcr4, G4, se4 = cluster_robust_t(e4)
    P(f"- E4 日クラスタ: G={G4}, t {tcr4:+.2f}（iid {tstat(R4):+.2f}）")
    blocks = day_blocks(tr)
    found, rows = nstar_blocks(blocks)
    P(f"- 日ブロック bootstrap n*(95%): {found if found else '>5000'}  P(Σ>0) by n: " + " ".join(f"{a}:{b:.2f}" for a, b in rows[:9]))
    daily = np.array([b.sum() for b in blocks])
    P(f"- 日合計R: 日数 {len(daily)}, 正の日 {(daily>0).sum()}, 平均 {daily.mean():+.2f}, sd {daily.std(ddof=1):.2f}, max {daily.max():+.1f}, min {daily.min():+.1f}; 上位3日の合計 {np.sort(daily)[-3:].sum():+.1f} = 合計R の {np.sort(daily)[-3:].sum()/R.sum()*100:.0f}%")
    # 週ブロック
    wk = collections.defaultdict(list)
    for d in tr: wk[dt.datetime.fromtimestamp(d["t"], JST).strftime("%G-W%V")].append(d["R"])
    wkb = [np.array(v) for k, v in sorted(wk.items())]
    pw = p_pos_blocks(wkb, n, 4000)
    P(f"- 週ブロック（{len(wkb)} 週）: 週合計R {[round(float(b.sum()),1) for b in wkb]}  P(Σ>0|n=305) {pw:.2f}")

    # ---------- Q4 scan null ----------
    P("\n## Q4 scan 帰無（近年窓 D2・日ブロック）")
    with open(CACHE, "r", encoding="utf-8") as f: sc = json.load(f)["trades"]
    def sel(lo, hi, prod=False, h1=False):
        xs = [d for d in sc if lo <= d["year"] <= hi and (not prod or 7 <= d["jh"] <= 12)]
        if h1: xs = [d for d in xs if d["year"] <= 2024 or (d["year"] == 2025) or (d["year"] == 2026 and dt.datetime.fromtimestamp(d["entry_time"], JST).month <= 6)]
        xs.sort(key=lambda d: d["entry_time"])
        return xs
    def null_test(name, xs, target, nn=n, B=5000):
        d = collections.defaultdict(list)
        for x in xs: d[dt.datetime.fromtimestamp(x["entry_time"], JST).strftime("%Y-%m-%d")].append(x["R"])
        bl = [np.array(v) for k, v in sorted(d.items())]
        Rs = np.array([x["R"] for x in xs])
        means = np.empty(B); nb_ = len(bl); ms = np.mean([len(b) for b in bl]); k = int(math.ceil(nn / ms)) + 5
        for i in range(B):
            s = np.concatenate([bl[j] for j in rng.integers(0, nb_, size=k)])
            while len(s) < nn: s = np.concatenate([s] + [bl[j] for j in rng.integers(0, nb_, size=k)])
            means[i] = s[:nn].mean()
        p = float((means >= target).mean()); z_iid = (target - Rs.mean()) / (Rs.std(ddof=1) / math.sqrt(nn))
        p_iid = float((rng.choice(Rs, size=(B, nn), replace=True).mean(axis=1) >= target).mean())
        P(f"- {name}: n={len(Rs)} 平均 {Rs.mean():+.4f} sd {Rs.std(ddof=1):.3f} → P(平均{nn}本 ≥ {target:+.3f}) 日ブロック **{p:.4f}**（iid {p_iid:.4f}, z_iid {z_iid:+.2f}）; 帰無 95%点 {np.quantile(means,0.95):+.3f} 99%点 {np.quantile(means,0.99):+.3f}")
        return p
    ps = []
    ps.append(null_test("B_flat 2024-26 全時間", sel(2024, 2026), R.mean()))
    ps.append(null_test("flat 2025-26H1 全時間", [d for d in sel(2025, 2026)], R.mean()))
    ps.append(null_test("B_prod 2024-26 jh7-12", sel(2024, 2026, prod=True), R.mean()))
    P(f"- Bonferroni α=0.05/3={0.05/3:.4f}: 有意 {sum(1 for p in ps if p < 0.05/3)}/3")
    P("- E4 のみ（n=%d・平均 %+.4f）を同じ帰無で:" % (len(R4), R4.mean()))
    ps4 = [null_test("  B_flat 2024-26", sel(2024, 2026), R4.mean(), nn=len(R4)),
           null_test("  flat 2025-26", sel(2025, 2026), R4.mean(), nn=len(R4))]
    P("- 2026 上半期 flat 単独（最も近い地合い）:")
    x26 = [d for d in sc if d["year"] == 2026]
    null_test("  flat 2026H1", x26, R.mean())

    # ---------- Q5 in→out by recipe epochs ----------
    P("\n## Q5 在→外（レシピ改版で分割）")
    def oos(name, R1, R2):
        B = 5000; means = rng.choice(R1, size=(B, len(R2)), replace=True).mean(axis=1)
        lo, hi = np.quantile(means, [0.05, 0.95]); se = math.sqrt(R1.var(ddof=1)/len(R1) + R2.var(ddof=1)/len(R2))
        P(f"- {name}: 在 n={len(R1)} {R1.mean():+.4f} / 外 n={len(R2)} {R2.mean():+.4f}  90%区間 [{lo:+.4f},{hi:+.4f}] {'内' if lo<=R2.mean()<=hi else '外'}  P(外Σ>0|在) {(means>0).mean():.2f}  Welch t {(R2.mean()-R1.mean())/se:+.2f}")
    Rpre = np.array([d["R"] for d in tr if d["ep"] <= 3]); R13 = np.array([d["R"] for d in tr if 1 <= d["ep"] <= 3])
    oos("在 E0-E3 → 外 E4", Rpre, R4); oos("在 E1-E3 → 外 E4", R13, R4)
    oos("在 E0(backfill) → 外 E1-E4", np.array([d["R"] for d in tr if d["ep"] == 0]), Rf)
    # E4 split in half by time
    h4 = len(R4) // 2; oos("E4 前半 → E4 後半", R4[:h4], R4[h4:])

    # ---------- Q6 cost ----------
    P("\n## Q6 コスト（E4・全本）")
    for name, xs in (("E4", e4), ("全 305", tr)):
        x = np.array([d["R"] for d in xs]); risk = np.array([d["risk"] for d in xs])
        for lab, usd in (("実口座 0.16+slip≈0.21", 0.21), ("デモ 0.42+slip≈0.47", 0.47), ("0.56 仮定", 0.56)):
            net = x - usd / risk
            P(f"- {name} net({lab}): 平均 {net.mean():+.4f} t {tstat(net):+.2f} 合計 {net.sum():+.1f}")
    with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")
    P(f"\n(written {OUT})")

if __name__ == "__main__":
    main()
