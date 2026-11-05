# -*- coding: utf-8 -*-
"""
c3_tail_power.py — cycle3 [メタ] 尻尾集中度と「合計Rの符号を安定させるのに必要な本数 n*」
読むだけ。入力 = setup_ledger.jsonl（読み取り）＋ AUREL_RESEARCH/data/refute_c4_scan_paths_2010_2026.json（既存キャッシュ）。
scan 無し・M5 読込なし・MT5 接続なし。書き込みは AUREL_RESEARCH/data/c3_tail_power_result.md のみ。

事前固定（コード前に記載・以後動かさない）
 H: 再加速の合計Rは少数の大当たり（fat tail）に依存する。その結果、合計Rの符号が偶然で反転しない本数 n*(95%) は
    現在の前向き紙の closed 本数より大きい（＝今の紙の +R は符号すら未確定）。
 データ:
  A 前向き紙 = setup_ledger.jsonl の setup 行に update 行（target=id）を時系列順に上書き統合し、最終状態の reaccel が
    status=closed かつ R あり の本（R は台帳値＝gross 扱い）。entry_time 昇順で前半=在／後半=外。
  B scan 2024-26 窓（refute_c4 キャッシュ・D2 の近年レジーム）: 全時間フラット（B_flat）と本番帯 jh∈[7,12]（B_prod）。
  C scan 2010-20 = 尻尾の形（幾何/構造）の比較のみ。edge の判定に使わない（CHARTER D2）。
 指標:
  T1 上位10/5/1% 本の合計R ÷ 正R合計、正R本の Gini。
  T2 R 降順に上位 k 本を除くと合計R が負になる最小 k と k/n（合計R≤0 なら k=0）。
  T3 n*(95%) = iid bootstrap（B=4000）で P(Σ_{i≤n} R_i > 0) ≥ 0.95 となる最小 n（grid 25..5000）。解析近似 (1.645·sd/mean)^2 併記。
      反証用: ブロック bootstrap（連続 10 本ブロック・循環）版 n*。
  T4 在→外: 前半分布から後半本数の平均R を 5000 回 bootstrap → 90% 予測区間と P(後半ΣR>0)。後半の実現平均・符号と比較。
  T5 コスト: net R = R − 0.56/risk（risk=|entry−sl| USD、A・B とも）。
 予測（事前）: P1 A で上位10% 本が正R合計の ≥50%。P2 A で上位5% 本の除去で合計R が負へ。P3 A の n*(95%) ≥ 300 > n(A)。
              P4 A 後半平均は前半 90% 予測区間内（一貫）。
 合否: H 支持 = P1 ∧ P3。P4 は一貫性の報告。昇格候補ではない（メタ知識）。
 最も重大な反証（事前）: iid bootstrap は時系列依存（レジーム・D2）を無視し n* を過小評価する → ブロック版で確認。
 look-ahead: 在/外分割は entry_time 中央値。closed 全本（TIME 含む）、選択なし。
"""
import json, os, sys, io, math
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
LIVE = r"C:\Users\user\.aurel\memory\projects\discretionary\live"
LEDGER = os.path.join(LIVE, "setup_ledger.jsonl")
CACHE = os.path.join(LIVE, "AUREL_RESEARCH", "data", "refute_c4_scan_paths_2010_2026.json")
OUT = os.path.join(LIVE, "AUREL_RESEARCH", "data", "c3_tail_power_result.md")
COST_USD = 0.56
rng = np.random.default_rng(20261105)
lines = []
def P(s=""):
    print(s); lines.append(s)

# ---------- A: ledger reconstruction ----------
def load_ledger():
    state = {}
    order = []
    with open(LEDGER, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = r.get("kind")
            if k == "setup" and r.get("id"):
                sid = r["id"]
                if sid not in state:
                    order.append(sid)
                state[sid] = dict(r)
            elif k == "update" and r.get("target"):
                sid = r["target"]
                st = state.setdefault(sid, {"id": sid})
                for kk, vv in r.items():
                    if kk in ("kind", "logged_at", "target"):
                        continue
                    st[kk] = vv
    trades = []
    n_frozen_closed = 0
    for sid in state:
        st = state[sid]
        ra = st.get("reaccel")
        rf = st.get("reaccel_frozen")
        if isinstance(rf, dict) and rf.get("status") == "closed" and rf.get("R") is not None:
            n_frozen_closed += 1
        if isinstance(ra, dict) and ra.get("status") == "closed" and ra.get("R") is not None:
            e, sl = ra.get("entry"), ra.get("sl")
            risk = abs(e - sl) if (e is not None and sl is not None) else np.nan
            trades.append(dict(id=sid, t=ra.get("entry_time") or 0, R=float(ra["R"]), risk=risk,
                               exit=ra.get("exit_reason"), mfe=ra.get("mfe_R"), mae=ra.get("mae_R"),
                               hold=ra.get("hold_bars"), jh=st.get("jst_hour"), wk=st.get("wall_kind")))
    trades.sort(key=lambda d: d["t"])
    return trades, n_frozen_closed, len(state)

# ---------- metrics ----------
def gini(x):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return float("nan")
    cum = np.cumsum(x)
    return float((n + 1 - 2 * np.sum(cum) / cum[-1]) / n)

def tail_shares(R):
    R = np.asarray(R, float)
    pos = R[R > 0]
    pos_sum = pos.sum()
    out = {}
    Rs = np.sort(R)[::-1]
    for q in (0.10, 0.05, 0.01):
        k = max(1, int(math.ceil(q * len(R))))
        out[q] = (k, Rs[:k].sum() / pos_sum if pos_sum > 0 else float("nan"))
    return out, gini(pos), pos_sum, R.sum()

def min_k_flip(R):
    Rs = np.sort(np.asarray(R, float))[::-1]
    tot = Rs.sum()
    if tot <= 0:
        return 0
    cum = np.cumsum(Rs)
    rem = tot - cum  # total after removing top k (k=1..n)
    idx = np.where(rem <= 0)[0]
    return int(idx[0] + 1) if len(idx) else len(Rs)

GRID = [25, 50, 75, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 3000, 5000]
def p_pos(R, n, B, block=None):
    R = np.asarray(R, float)
    N = len(R)
    if block is None:
        s = rng.choice(R, size=(B, n), replace=True).sum(axis=1)
    else:
        nb = int(math.ceil(n / block))
        starts = rng.integers(0, N, size=(B, nb))
        idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % N
        idx = idx.reshape(B, nb * block)[:, :n]
        s = R[idx].sum(axis=1)
    return float((s > 0).mean())

def nstar(R, block=None):
    R = np.asarray(R, float)
    m, sd = R.mean(), R.std(ddof=1)
    approx = (1.645 * sd / m) ** 2 if m > 0 else float("inf")
    rows = []
    found = None
    for n in GRID:
        B = 4000 if n <= 1000 else 1500
        p = p_pos(R, n, B, block)
        rows.append((n, p))
        if found is None and p >= 0.95:
            found = n
    return m, sd, approx, found, rows

def describe(name, R, risk=None):
    R = np.asarray(R, float)
    P(f"\n### {name}  n={len(R)}")
    P(f"- 平均R {R.mean():+.4f}  sd {R.std(ddof=1):.3f}  勝率 {(R>0).mean()*100:.1f}%  合計R {R.sum():+.1f}  中央値 {np.median(R):+.3f}  max {R.max():+.2f}  min {R.min():+.2f}")
    sh, g, pos_sum, tot = tail_shares(R)
    P(f"- T1 尻尾: 上位10% ({sh[0.10][0]}本) = 正R合計の {sh[0.10][1]*100:.1f}% / 上位5% ({sh[0.05][0]}本) {sh[0.05][1]*100:.1f}% / 上位1% ({sh[0.01][0]}本) {sh[0.01][1]*100:.1f}%  正R Gini {g:.3f}  正R合計 {pos_sum:+.1f}")
    k = min_k_flip(R)
    P(f"- T2 符号反転に要る上位除去本数 k = {k} ({k/len(R)*100:.1f}% of n)" + ("  ※合計R≤0 なので k=0" if tot <= 0 else ""))
    m, sd, approx, found, rows = nstar(R)
    P(f"- T3 n*(95%) iid: {found if found else '>5000'}  解析近似 {approx:.0f}  P(ΣR>0) by n: " + " ".join(f"{n}:{p:.2f}" for n, p in rows))
    mb, sdb, apb, foundb, rowsb = nstar(R, block=10)
    P(f"- T3' n*(95%) ブロック10: {foundb if foundb else '>5000'}  P by n: " + " ".join(f"{n}:{p:.2f}" for n, p in rowsb))
    if risk is not None:
        risk = np.asarray(risk, float)
        ok = np.isfinite(risk) & (risk > 0)
        Rn = R[ok] - COST_USD / risk[ok]
        P(f"- T5 net(−0.56USD/risk, risk中央値 {np.median(risk[ok]):.2f}USD, コスト中央値 {np.median(COST_USD/risk[ok]):.3f}R) n={len(Rn)}: 平均 {Rn.mean():+.4f} 合計 {Rn.sum():+.1f} 勝率 {(Rn>0).mean()*100:.1f}%")
        shn, gn, _, _ = tail_shares(Rn)
        kn = min_k_flip(Rn)
        mn, sdn, apn, fn, rn = nstar(Rn)
        P(f"  net: 上位10% share {shn[0.10][1]*100:.1f}%  k_flip {kn}  n*(95%) iid {fn if fn else '>5000'} (近似 {apn:.0f})  P by n: " + " ".join(f"{n}:{p:.2f}" for n, p in rn[:9]))
        return Rn
    return None

def oos(name, R, t=None):
    R = np.asarray(R, float)
    n = len(R); n1 = n // 2
    R1, R2 = R[:n1], R[n1:]
    B = 5000
    means = rng.choice(R1, size=(B, len(R2)), replace=True).mean(axis=1)
    lo, hi = np.quantile(means, [0.05, 0.95])
    p_pos2 = float((means > 0).mean())
    inside = lo <= R2.mean() <= hi
    P(f"- T4 在→外 [{name}] 在 n={n1} 平均 {R1.mean():+.4f} 合計 {R1.sum():+.1f} / 外 n={len(R2)} 平均 {R2.mean():+.4f} 合計 {R2.sum():+.1f}")
    P(f"  在分布からの外平均 90%予測区間 [{lo:+.4f}, {hi:+.4f}] → 外実現 {R2.mean():+.4f} {'区間内' if inside else '区間外'}; 在から予測 P(外ΣR>0)={p_pos2:.2f}, 実際の外符号 {'+' if R2.sum()>0 else '−/0'}")
    # Welch t between halves
    se = math.sqrt(R1.var(ddof=1)/len(R1) + R2.var(ddof=1)/len(R2))
    P(f"  前後半差 (外−在) {R2.mean()-R1.mean():+.4f}  Welch t {(R2.mean()-R1.mean())/se:+.2f}")
    if t is not None:
        import datetime as dt
        f = lambda x: dt.datetime.utcfromtimestamp(int(x)).strftime("%Y-%m-%d")
        P(f"  期間: 在 {f(t[0])}..{f(t[n1-1])} / 外 {f(t[n1])}..{f(t[-1])}")

def main():
    P("# cycle3 [メタ] 尻尾集中度と n*(95%)  — 2026-11-05  (scripts/c3_tail_power.py)")
    trades, n_frozen_closed, n_setups = load_ledger()
    P(f"\n## A 前向き紙（setup_ledger.jsonl 統合）: setups {n_setups}, reaccel closed {len(trades)}, reaccel_frozen closed {n_frozen_closed}")
    import collections
    P(f"- exit 内訳 {dict(collections.Counter(d['exit'] for d in trades))}, wall_kind {dict(collections.Counter(d['wk'] for d in trades))}, jh7-12 本数 {sum(1 for d in trades if d['jh'] is not None and 7 <= d['jh'] <= 12)}")
    RA = np.array([d["R"] for d in trades]); riskA = np.array([d["risk"] for d in trades]); tA = np.array([d["t"] for d in trades])
    RA_net = describe("A 台帳 reaccel closed（gross）", RA, riskA)
    oos("A gross", RA, tA)
    if RA_net is not None and len(RA_net) == len(RA):
        oos("A net", RA_net)
    hold = np.array([d["hold"] if d["hold"] is not None else np.nan for d in trades], float)
    mfe = np.array([d["mfe"] if d["mfe"] is not None else np.nan for d in trades], float)
    P(f"- 補助: hold 中央値 {np.nanmedian(hold):.0f} 本, mfe_R 中央値 {np.nanmedian(mfe):.2f}, 上位10% 本の hold 中央値 {np.nanmedian(hold[np.argsort(-RA)[:max(1,len(RA)//10)]]):.0f}")

    with open(CACHE, "r", encoding="utf-8") as f:
        tr = json.load(f)["trades"]
    def sel(lo, hi, prod=False):
        xs = [d for d in tr if lo <= d["year"] <= hi and (not prod or 7 <= d["jh"] <= 12)]
        xs.sort(key=lambda d: d["entry_time"])
        return np.array([d["R"] for d in xs]), np.array([d["risk"] for d in xs]), np.array([d["entry_time"] for d in xs])
    P("\n## B scan 2024-26（refute_c4 キャッシュ・近年窓 D2）")
    Rb, kb, tb = sel(2024, 2026)
    describe("B_flat 2024-26 全時間", Rb, kb); oos("B_flat", Rb, tb)
    Rp, kp, tp = sel(2024, 2026, prod=True)
    Rp_net = describe("B_prod 2024-26 jh7-12", Rp, kp); oos("B_prod gross", Rp, tp)
    if Rp_net is not None: oos("B_prod net", Rp_net)
    P("\n## C scan 2010-20（尻尾の形の比較のみ・edge 判定に使わない）")
    Rc, kc, _ = sel(2010, 2020)
    sh, g, pos_sum, tot = tail_shares(Rc)
    P(f"- n={len(Rc)} 平均R {Rc.mean():+.4f} sd {Rc.std(ddof=1):.3f} 上位10% share {sh[0.10][1]*100:.1f}% 上位1% {sh[0.01][1]*100:.1f}% 正R Gini {g:.3f}")
    Rcp, _, _ = sel(2010, 2020, prod=True)
    sh, g, _, _ = tail_shares(Rcp)
    P(f"- jh7-12 n={len(Rcp)} 平均R {Rcp.mean():+.4f} sd {Rcp.std(ddof=1):.3f} 上位10% share {sh[0.10][1]*100:.1f}% 正R Gini {g:.3f}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    P(f"\n(written {OUT})")

if __name__ == "__main__":
    main()
