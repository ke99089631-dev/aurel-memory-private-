# -*- coding: utf-8 -*-
"""
今のエンジン(setup_engine: 動的壁箱 × 戻り待ち再加速 × v1フィルタ × コスト控除)を 16年(2010-2026)で回す。
  会長の問い(2026-10-21)『はじめ俺の型は過去で回した時は優位性がないと言ったが今は違うだろ？』に、
  「今のレシピ」を過去に当てて答える。9/22の16年判定は粗い機械版(backtest/backtest_mm)の話で、再加速版は未実施だった。

設計(事前固定・結果を見て動かさない):
  - 判定ロジックは setup_engine.scan をそのまま呼ぶ(再実装しない)。壁検出だけ高速版(fast_box)に差し替え、
    差し替えの同値性は live 窓で wallbox.dynamic_box と突き合わせて検証する(--verify)。
  - データ = Dukascopy M1 bid → M5 (m5_loader・index UTC)。Vantage とは価格が僅かに違う＝本数は一致しないが型は同じ。
  - コスト = live の cost_model(手数料0.06 + JST時間帯別スプレッド中央値 or 仮値0.25) を typical とし、×2.75/×5 を併記。
  - 関門 = run_gate と同じ(70/30 OOS・日次Sharpe≥0.25・片側p・FDR)。加えて年別表と 2010-23 / 2024-26 の分割。
  - v1 フィルタの時間帯本物率(damashi_hour_jst.json)は過去の機械統計から作った＝in-sample 寄り。その但し書きを結果に残す。
金ゼロ・読取のみ・発注なし。
"""
import os
import sys
import json
import time
import math
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
W2W = r"C:\Users\user\AssetEmpire\empire\research\wall_to_wall"
sys.path.insert(0, W2W)

import wallbox
import walls
import setup_engine as se
import rules_v1
from m5_loader import load_m5

OUT_JSON = os.path.join(HERE, "backtest_reaccel_result.json")
OUT_MD = os.path.join(HERE, "backtest_reaccel_result.md")
COST_SCENARIOS = {"typical": 1.0, "spike x2.75": 2.75, "stress x5": 5.0}
IS_FRAC = 0.70
ANNUALIZE = math.sqrt(252.0)


# ── 高速壁箱: wallbox.dynamic_box と同値(スイングを全系列で一度だけ計算) ─────────────────
class FastBox:
    def __init__(self, m5):
        self.h = m5["high"].to_numpy(); self.l = m5["low"].to_numpy(); self.c = m5["close"].to_numpy()
        self.pos = {int(t.value): i for i, t in enumerate(m5.index)}
        n = len(self.c); k = 3
        self.is_high = np.zeros(n, bool); self.is_low = np.zeros(n, bool)
        # walls._swings と同じ定義: h[i] >= max(h[i-k..i+k]) / l[i] <= min(...)
        hh = pd.Series(self.h).rolling(2 * k + 1, center=True).max().to_numpy()
        ll = pd.Series(self.l).rolling(2 * k + 1, center=True).min().to_numpy()
        self.is_high[k:n - k] = self.h[k:n - k] >= hh[k:n - k]
        self.is_low[k:n - k] = self.l[k:n - k] <= ll[k:n - k]
        self.calls = 0

    def box(self, win):
        """wallbox.dynamic_box(win) と同じ戻り値。win = m5.iloc[w0:i]。"""
        self.calls += 1
        n = len(win)
        if n < 40:
            return None, None
        i_end = self.pos[int(win.index[-1].value)] + 1      # 窓の終端(排他)
        w_all = i_end - n                                   # 窓の先頭
        h, l, c = self.h, self.l, self.c
        atr = float(np.mean(h[max(w_all + 1, i_end - 14):i_end] - l[max(w_all + 1, i_end - 14):i_end])) if n > 15 else 0.0
        w0 = max(w_all, i_end - wallbox.WALL_WIN)
        # find_walls(h[w0:i_end], ...) と同値
        cw = c[w0:i_end]
        tol = max(atr * 0.6, float(np.mean(np.abs(cw))) * 0.0006) if atr > 0 else (cw[-1] * 0.0008 if len(cw) else 1.0)
        k = 3
        a, b = w0 + k, i_end - k
        hi_idx = np.nonzero(self.is_high[a:b])[0] + a
        lo_idx = np.nonzero(self.is_low[a:b])[0] + a
        highs = [(int(j - w0), float(h[j])) for j in hi_idx]
        lows = [(int(j - w0), float(l[j])) for j in lo_idx]
        res = walls._cluster(highs, tol); sup = walls._cluster(lows, tol)
        for w in res: w["kind"] = "res"
        for w in sup: w["kind"] = "sup"
        ws = res + sup
        strong = [x for x in ws if x["touches"] >= 2] or ws
        if len(strong) < 2:
            return None, None
        bb = max(w_all, i_end - wallbox.BAND_WIN)
        rb_hi = float(np.max(h[bb:i_end])); rb_lo = float(np.min(l[bb:i_end]))
        span = rb_hi - rb_lo if rb_hi > rb_lo else max(atr * 3, 1.0)
        pad = wallbox.BAND_PAD_FR * span
        lo_b, hi_b = rb_lo - pad, rb_hi + pad
        cand = [x for x in strong if lo_b <= x["price"] <= hi_b]
        if len(cand) < 2:
            cand = strong
        price0 = float(c[i_end - 1])
        if cand and (price0 < min(x["price"] for x in cand) or price0 > max(x["price"] for x in cand)):
            weak = [x for x in ws if x["touches"] < 2 and lo_b <= x["price"] <= hi_b]
            cand = cand + weak
        resc = [x for x in cand if x["kind"] == "res"]
        supc = [x for x in cand if x["kind"] == "sup"]
        up = (max(resc, key=lambda x: x["price"]) if resc else max(cand, key=lambda x: x["price"]))
        dn = (min(supc, key=lambda x: x["price"]) if supc else min(cand, key=lambda x: x["price"]))
        up_p, dn_p = up["price"], dn["price"]
        if up_p <= dn_p:
            return None, None
        width = up_p - dn_p
        mids = [x for x in cand if dn_p < x["price"] < up_p]
        mid_p = max(mids, key=lambda x: x["touches"])["price"] if mids else (up_p + dn_p) / 2.0
        box = {"up": round(up_p, 3), "dn": round(dn_p, 3), "mid": round(mid_p, 3), "width": round(width, 3),
               "up_touches": int(up.get("touches", 0)), "dn_touches": int(dn.get("touches", 0))}
        return box, None      # brk は scan で未使用


def verify_fastbox(m5, n_check=1500, seed=1):
    fb = FastBox(m5)
    rng = np.random.default_rng(seed)
    n = len(m5); bad = 0; checked = 0
    for i in rng.integers(wallbox.WALL_WIN, n, size=n_check):
        win = m5.iloc[max(0, i - wallbox.WALL_WIN):i]
        b1, _ = wallbox.dynamic_box(win)
        b2, _ = fb.box(win)
        checked += 1
        if (b1 is None) != (b2 is None) or (b1 is not None and any(abs(b1[k] - b2[k]) > 1e-9 for k in ("up", "dn", "mid"))):
            bad += 1
            if bad <= 3:
                print("MISMATCH at", i, b1, b2)
    print("fastbox verify: checked %d mismatches %d" % (checked, bad))
    return bad == 0


# ── コスト ───────────────────────────────────────────────────────────────────────
def cost_model():
    import serve_chart
    return serve_chart._cost_model()


def net_R(R, entry, sl, jh, cm, mult):
    risk = abs(entry - sl)
    sp = cm["spread_by_hour"].get(jh, float(cm["spread_pt_default"]))
    cost = (sp + float(cm["commission_pt"]) + float(cm.get("slippage_pt") or 0.0)) * mult
    return R - cost / risk


# ── 関門(run_gate と同じ) ────────────────────────────────────────────────────────
def one_sided_p(series):
    try:
        from circulation.soldier_screen import one_sided_p as f
        return float(f(series))
    except Exception:
        x = np.asarray(series, float); n = len(x)
        if n < 2 or x.std(ddof=1) == 0:
            return 1.0
        t = x.mean() / (x.std(ddof=1) / math.sqrt(n))
        # 正規近似
        return float(0.5 * math.erfc(t / math.sqrt(2)))


def daily_series(entry_times, r):
    d = pd.DataFrame({"day": pd.to_datetime(entry_times, unit="s", utc=True).date, "r": r})
    g = d.groupby("day")["r"].sum()
    idx = pd.date_range(g.index.min(), g.index.max(), freq="D")
    return g.reindex(idx.date, fill_value=0.0).to_numpy()


def sharpe(series):
    s = np.asarray(series, float)
    sd = s.std(ddof=1)
    return 0.0 if (sd == 0 or len(s) < 2) else float(s.mean() / sd * ANNUALIZE)


def block(label, et, r):
    r = np.asarray(r, float); n = len(r)
    if n == 0:
        return {"label": label, "n": 0}
    ds = daily_series(et, r)
    peak = cum = dd = 0.0
    for x in r:
        cum += x; peak = max(peak, cum); dd = min(dd, cum - peak)
    return {"label": label, "n": n, "win": round(100.0 * float((r > 0).sum()) / n, 1),
            "avgR": round(float(r.mean()), 3), "sumR": round(float(r.sum()), 1), "sd": round(float(r.std(ddof=1)), 2) if n > 1 else 0.0,
            "maxDD": round(dd, 1), "sharpe": round(sharpe(ds), 2), "p": round(one_sided_p(ds), 4)}


def gate_lane(name, rows, cm):
    """rows: dict(entry_time, R, entry, sl, jh, year)。コスト3シナリオ × 全体/IS/OOS、年別(typical)、2010-23/2024-26。"""
    out = {"name": name, "n": len(rows), "scenarios": {}}
    if not rows:
        return out
    rows = sorted(rows, key=lambda x: x["entry_time"])
    et = np.array([x["entry_time"] for x in rows])
    split = int(len(rows) * IS_FRAC)
    for scen, mult in COST_SCENARIOS.items():
        r = np.array([net_R(x["R"], x["entry"], x["sl"], x["jh"], cm, mult) for x in rows])
        blocks = [block("全体", et, r), block("IS(前70%)", et[:split], r[:split]), block("OOS(後30%)", et[split:], r[split:])]
        oos = blocks[-1]
        verdict = bool(oos.get("n", 0) and oos["avgR"] > 0 and oos["sharpe"] >= 0.25 and oos["p"] < 0.05)
        out["scenarios"][scen] = {"blocks": blocks, "verdict": verdict}
        if scen == "typical":
            yrs = {}
            for x, rr in zip(rows, r):
                yrs.setdefault(x["year"], []).append(rr)
            out["by_year"] = {y: {"n": len(v), "avgR": round(float(np.mean(v)), 3), "sumR": round(float(np.sum(v)), 1),
                                  "win": round(100.0 * sum(1 for q in v if q > 0) / len(v), 1)} for y, v in sorted(yrs.items())}
            m1 = [i for i, x in enumerate(rows) if x["year"] <= 2023]
            m2 = [i for i, x in enumerate(rows) if x["year"] >= 2024]
            out["era"] = {"2010-23": block("2010-23", et[m1], r[m1]) if m1 else {"n": 0},
                          "2024-26": block("2024-26", et[m2], r[m2]) if m2 else {"n": 0}}
            hrs = {}
            for x, rr in zip(rows, r):
                hrs.setdefault(x["jh"], []).append(rr)
            out["by_hour"] = {h: {"n": len(v), "avgR": round(float(np.mean(v)), 3)} for h, v in sorted(hrs.items())}
    return out


# ── 本体 ────────────────────────────────────────────────────────────────────────
def load_all(y0, y1, last="2026-07-01"):
    frames = []
    for y in range(y0, y1 + 1):
        a, b = "%d-01-01" % y, "%d-01-01" % (y + 1)
        if a >= last:
            break
        if b > last:
            b = last
        t0 = time.time()
        try:
            m5 = load_m5(a, b)
        except FileNotFoundError as e:
            print("skip", y, e); continue
        frames.append(m5)
        print("  loaded %d: %d bars (%.1fs)" % (y, len(m5), time.time() - t0), flush=True)
    m5 = pd.concat(frames)
    m5 = m5[~m5.index.duplicated(keep="first")].sort_index()
    return m5


def run(y0=2010, y1=2026, verify=True, limit=None):
    print("=== 再加速レシピ 16年ラン (%d-%d) ===" % (y0, y1), flush=True)
    m5 = load_all(y0, y1)
    if limit:
        m5 = m5.iloc[-int(limit):]
    print("M5 bars:", len(m5), m5.index[0], "..", m5.index[-1], flush=True)
    fb = FastBox(m5)
    if verify:
        ok = verify_fastbox(m5.iloc[-60000:] if len(m5) > 60000 else m5)
        if not ok:
            print("!! fastbox が wallbox と不一致。中止。"); return None
        fb = FastBox(m5)   # 検証用に別インスタンスを作ったので作り直し(posが異なる)
    wallbox.dynamic_box = fb.box          # scan 内の壁検出だけ差し替え(判定ロジックは setup_engine のまま)
    dm = se._load_damashi()
    t0 = time.time()
    recs = se.scan(m5, dm)
    print("scan: %d setups in %.0fs (box calls %d)" % (len(recs), time.time() - t0, fb.calls), flush=True)
    # v1 フィルタ(建玉時点の情報だけ): closed_history = 主レーン(戻り目)の決着済み記録(エンジンと同じ)
    closed_hist = [r for r in recs if r.get("status") == "closed"]
    for r in recs:
        r["v1"] = rules_v1.evaluate(r, closed_hist)
    cm = cost_model()
    lanes = {"再加速×外壁(全部)": [], "再加速×外壁×採用(デモの型)": [], "再加速×中壁(全部)": [], "再加速×中壁×採用": [],
             "再加速×外壁+中壁×採用(今デモが撃つ型)": [], "戻り目(主レーン・参考)": [], "飛び乗り(chase・参考)": []}
    st_counts = {}
    for r in recs:
        ra = r.get("reaccel") or {}
        st_counts[ra.get("status")] = st_counts.get(ra.get("status"), 0) + 1
        year = int(pd.Timestamp(r["break_time"], unit="s", tz="UTC").year)
        keep = bool(r["v1"].get("keep"))
        if ra.get("status") == "closed" and ra.get("R") is not None:
            row = {"entry_time": int(ra["entry_time"]), "R": float(ra["R"]), "entry": float(ra["entry"]), "sl": float(ra["sl"]),
                   "jh": int(((int(ra["entry_time"]) // 3600) + 9) % 24), "year": year}
            if r["wall_kind"] == "outer":
                lanes["再加速×外壁(全部)"].append(row)
                if keep:
                    lanes["再加速×外壁×採用(デモの型)"].append(row); lanes["再加速×外壁+中壁×採用(今デモが撃つ型)"].append(row)
            else:
                lanes["再加速×中壁(全部)"].append(row)
                if keep:
                    lanes["再加速×中壁×採用"].append(row); lanes["再加速×外壁+中壁×採用(今デモが撃つ型)"].append(row)
        if r.get("status") == "closed" and r.get("R") is not None:
            lanes["戻り目(主レーン・参考)"].append({"entry_time": int(r["entry_time"]), "R": float(r["R"]), "entry": float(r["entry"]),
                                             "sl": float(r["sl"]), "jh": int(r["jst_hour"]), "year": year})
        ch = r.get("chase") or {}
        if ch.get("status") == "closed" and ch.get("R") is not None:
            lanes["飛び乗り(chase・参考)"].append({"entry_time": int(r["break_time"]) + 300, "R": float(ch["R"]), "entry": float(ch["entry"]),
                                              "sl": float(r["sl"]), "jh": int(r["jst_hour"]), "year": year})
    result = {"period": [str(m5.index[0]), str(m5.index[-1])], "bars": int(len(m5)), "setups": len(recs),
              "reaccel_status": st_counts, "cost_model": {k: v for k, v in cm.items() if k != "spread_samples"},
              "frozen_params": {"RETRACE_BARS": se.RETRACE_BARS, "REACCEL_BARS": se.REACCEL_BARS, "REACCEL_PAD": se.REACCEL_PAD,
                                "MIN_SL_W": se.MIN_SL_W, "MAX_HOLD": se.MAX_HOLD, "WALL_WIN": wallbox.WALL_WIN, "BAND_WIN": wallbox.BAND_WIN,
                                "SL_PAD_FR": wallbox.SL_PAD_FR, "v1": {"RAIN_N": rules_v1.RAIN_N, "RAIN_FAKE_RATE": rules_v1.RAIN_FAKE_RATE,
                                                                        "P_REAL_MIN": rules_v1.P_REAL_MIN, "TIGHT_MAX": rules_v1.TIGHT_MAX}},
              "lanes": {k: gate_lane(k, v, cm) for k, v in lanes.items()},
              "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    write_md(result)
    print_summary(result)
    return result


def print_summary(res):
    print("\n期間 %s .. %s  bars=%d  setups=%d  reaccel状態=%s" % (res["period"][0][:10], res["period"][1][:10], res["bars"], res["setups"], res["reaccel_status"]))
    for name, L in res["lanes"].items():
        if not L.get("n"):
            print("\n[%s] n=0" % name); continue
        print("\n[%s] n=%d" % (name, L["n"]))
        for scen, S in L["scenarios"].items():
            b = S["blocks"]
            print("  %-12s " % scen + " | ".join("%s n=%d 勝率%.0f%% 平均%+.3f 合計%+.0f DD%.0f Sh%+.2f p=%.3f" % (
                x["label"], x["n"], x["win"], x["avgR"], x["sumR"], x["maxDD"], x["sharpe"], x["p"]) for x in b)
                  + "  ⇒ %s" % ("★優位性あり" if S["verdict"] else "優位性なし"))
        e = L.get("era", {})
        print("  時代: " + " / ".join("%s n=%d 平均%+.3f Sh%+.2f" % (k, v.get("n", 0), v.get("avgR", 0), v.get("sharpe", 0)) for k, v in e.items() if v.get("n")))
        print("  年別(typical): " + " ".join("%s:%+.2f(%d)" % (y, v["avgR"], v["n"]) for y, v in L.get("by_year", {}).items()))


def write_md(res):
    L = []
    L.append("# 再加速レシピ 16年ラン（今のエンジンをそのまま過去へ）\n")
    L.append("生成 %s ／ 期間 %s〜%s ／ M5 %d本 ／ セットアップ %d件 ／ 再加速の状態内訳 %s\n" % (
        res["generated_at"], res["period"][0][:10], res["period"][1][:10], res["bars"], res["setups"], json.dumps(res["reaccel_status"], ensure_ascii=False)))
    L.append("前提: 判定=setup_engine.scan そのまま(壁検出のみ同値の高速版)／データ=Dukascopy M1 bid→M5／コスト=live cost_model(手数料%.2f+時間帯スプレッド中央値 or 仮値%.2f)×1/×2.75/×5／関門=70/30 OOS・日次Sharpe≥0.25・片側p<0.05／v1の時間帯本物率は過去統計由来(in-sample寄り)。\n" % (
        res["cost_model"]["commission_pt"], res["cost_model"]["spread_pt_default"]))
    L.append("固定パラメータ: %s\n" % json.dumps(res["frozen_params"], ensure_ascii=False))
    for name, lane in res["lanes"].items():
        L.append("\n## %s（n=%d）\n" % (name, lane.get("n", 0)))
        if not lane.get("n"):
            continue
        L.append("| コスト | 区間 | n | 勝率 | 平均R | 合計R | sd | 最大DD | 年率Sharpe | 片側p | 判定 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for scen, S in lane["scenarios"].items():
            for b in S["blocks"]:
                L.append("| %s | %s | %d | %.1f%% | %+.3f | %+.1f | %.2f | %.1f | %+.2f | %.3f | %s |" % (
                    scen, b["label"], b["n"], b["win"], b["avgR"], b["sumR"], b["sd"], b["maxDD"], b["sharpe"], b["p"],
                    ("★優位性あり" if S["verdict"] else "優位性なし") if b["label"].startswith("OOS") else ""))
        e = lane.get("era", {})
        L.append("\n時代別(typical): " + " ／ ".join("%s n=%d 平均%+.3f 合計%+.1f Sharpe%+.2f p=%.3f" % (k, v["n"], v["avgR"], v["sumR"], v["sharpe"], v["p"]) for k, v in e.items() if v.get("n")))
        L.append("\n年別(typical): " + " ".join("%s:%+.2f(%d)" % (y, v["avgR"], v["n"]) for y, v in lane.get("by_year", {}).items()))
        L.append("\nJST時間帯別(typical・平均R/本数): " + " ".join("%s時:%+.2f(%d)" % (h, v["avgR"], v["n"]) for h, v in lane.get("by_hour", {}).items()))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("wrote", OUT_MD)


if __name__ == "__main__":
    args = sys.argv[1:]
    yrs = [int(a) for a in args if a.isdigit()]
    limit = None
    for a in args:
        if a.startswith("limit="):
            limit = int(a.split("=")[1])
    if "--verify-only" in args:
        m5 = load_all(2026, 2026)
        verify_fastbox(m5, n_check=3000)
    else:
        y0, y1 = (yrs[0], yrs[1]) if len(yrs) >= 2 else (2010, 2026)
        run(y0, y1, verify=("--no-verify" not in args), limit=limit)
