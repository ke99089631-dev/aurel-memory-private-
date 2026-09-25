# -*- coding: utf-8 -*-
"""
滑り(slippage)の実測シミュレータ — AI紙トレードの「もしEAで発注していたら」の約定を MT5 ティック履歴で再現する。
  読取のみ・発注なし・金ゼロ。mt5_bridge 経由(口座検証あり)。
  会長 2026-09-25「その滑りを詰めよう」。

  測るもの（1本のAI記録につき）:
    entry: 紙は「戻り目の次足の始値(bid)」で入った想定。実際は成行を投げて L 秒後に約定 →
           slip_entry(L) = 逆行分（BUY: bid(t0+L)−bid(t0) / SELL: bid(t0)−bid(t0+L)、プラス=不利）。
           スプレッド分は別勘定(cost_model)なので二重に引かない。t0 の実測スプレッドも記録して仮値を置き換える。
    chase: 抜け足の終値で即エントリーの変種。次足始値 + L 秒での bid 差。
    SL:    紙は「bid が SL に触れた瞬間にSL価格で決済」。実際の逆指値は SELL=ask で発動/BUY=bid で発動し、
           その時のレートで約定 → slip_sl = 約定と SL 価格の差（プラス=不利。窓開け・急変で大きくなる）。
    TP:    紙は bid の足が TP に触れれば利確。実際の指値は SELL=ask≤TP / BUY=bid≥TP が必要 →
           その足のティックで条件を満たしたか(tp_fill_ok)。満たさない＝紙が甘かった本数を数える。
  latency L は複数で測る: 0.3s / 1s / 3s（EA想定）と 120s（今の紙エンジンの巡回周期＝もし2分遅れで投げたら）。
  採用値(cost_model で控除する slip_pt)= L_ADOPT 秒。
  出力: --report で集計表示のみ。--apply で setup_ledger.jsonl に kind=update(spread_pt/slip_pt/sl_slip_pt/tp_fill_ok) を追記。
"""
import os
import sys
import json
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mt5_bridge

LEDGER = os.path.join(HERE, "setup_ledger.jsonl")
REPORT = os.path.join(HERE, "slippage_report.json")
OFF = mt5_bridge.SERVER_UTC_OFFSET_H * 3600
LATENCIES = (0.3, 1.0, 3.0, 120.0)
L_ADOPT = 1.0
UTC = dt.timezone.utc


def _load():
    recs, order = {}, []
    for line in open(LEDGER, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("kind") == "setup":
            recs[r["id"]] = r; order.append(r["id"])
        elif r.get("kind") == "update":
            t = recs.get(r.get("target"))
            if t:
                for k, v in r.items():
                    if k not in ("kind", "target", "logged_at"):
                        t[k] = v
    return [recs[i] for i in order]


def _ticks(mt5, t_utc, before, after):
    """真UTC秒 t_utc の前後のティック。MT5 python は tz-aware UTC で渡すと素直。サーバ時刻=GMT+3 補正。"""
    a = dt.datetime.fromtimestamp(t_utc - before + OFF, tz=UTC)
    b = dt.datetime.fromtimestamp(t_utc + after + OFF, tz=UTC)
    tk = mt5.copy_ticks_range(mt5_bridge.SYMBOL, a, b, mt5.COPY_TICKS_ALL)
    if tk is None or len(tk) == 0:
        return []
    out = []
    for t in tk:
        ms = int(t["time_msc"]) / 1000.0 - OFF
        out.append((ms, float(t["bid"]), float(t["ask"])))
    return out


def _at(ticks, t):
    """時刻 t 以降の最初のティック（無ければ None）。"""
    for x in ticks:
        if x[0] >= t:
            return x
    return None


def _entry_slip(ticks, t0, side):
    """t0=足の始値時刻。L 秒後の bid で逆行分を測る。"""
    base = _at(ticks, t0)
    if base is None:
        return None
    res = {"bid0": base[1], "spread_pt": round(base[2] - base[1], 3)}
    for L in LATENCIES:
        x = _at(ticks, t0 + L)
        if x is None:
            res["slip_%g" % L] = None
            continue
        slip = (x[1] - base[1]) if side == "BUY" else (base[1] - x[1])
        res["slip_%g" % L] = round(slip, 3)
    return res


def _sl_slip(ticks, side, sl):
    """逆指値の実発動: SELL は ask>=SL で買い戻し(約定=ask) / BUY は bid<=SL で手仕舞い(約定=bid)。"""
    for ms, bid, ask in ticks:
        if side == "SELL" and ask >= sl:
            return round(ask - sl, 3)
        if side == "BUY" and bid <= sl:
            return round(sl - bid, 3)
    return None          # その足のティックでは発動条件に届かず（紙は bid の高安で判定していた）


def _tp_ok(ticks, side, tp):
    for ms, bid, ask in ticks:
        if side == "SELL" and ask <= tp:
            return True
        if side == "BUY" and bid >= tp:
            return True
    return False


def measure(recs, mt5, only_missing=True):
    rows = []
    for r in recs:
        if r.get("status") != "closed" or not r.get("entry_time"):
            continue
        if only_missing and r.get("slip_pt") is not None:
            continue
        side = r["side"]
        t0 = int(r["entry_time"])
        tk = _ticks(mt5, t0, 5, 130)
        e = _entry_slip(tk, t0, side) if tk else None
        row = {"id": r["id"], "side": side, "risk": abs(float(r["entry"]) - float(r["sl"])),
               "exit_reason": r.get("exit_reason"), "R": r.get("R")}
        if e:
            row.update(e)
            row["open_vs_tick"] = round(float(r["entry"]) - e["bid0"], 3)   # 紙の始値と最初のティックの差(整合チェック)
        # chase: 抜け足の終値 = 次足始値の時刻 (break_time+300) を t0 とみなす
        ch = r.get("chase") or {}
        if ch.get("status") == "closed" and r.get("break_time"):
            tc = int(r["break_time"]) + 300
            tkc = _ticks(mt5, tc, 5, 130)
            ec = _entry_slip(tkc, tc, side) if tkc else None
            if ec:
                # 紙の建値 = 抜け足の終値。実際は次足始値+L の bid → 終値との差を滑りとする
                for L in LATENCIES:
                    x = _at(tkc, tc + L)
                    if x is not None:
                        row["chase_slip_%g" % L] = round((x[1] - float(ch["entry"])) if side == "BUY"
                                                         else (float(ch["entry"]) - x[1]), 3)
        # 決済足
        if r.get("exit_time"):
            tx = int(r["exit_time"])
            tkx = _ticks(mt5, tx, 0, 300)
            if tkx:
                if r.get("exit_reason") == "SL":
                    row["sl_slip"] = _sl_slip(tkx, side, float(r["sl"]))
                elif r.get("exit_reason") == "TP":
                    row["tp_fill_ok"] = _tp_ok(tkx, side, float(r["tp"]))
        rows.append(row)
    return rows


def _q(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return round(xs[min(len(xs) - 1, int(p * len(xs)))], 3)


def summarize(rows):
    s = {"n": len(rows)}
    for L in LATENCIES:
        xs = [r.get("slip_%g" % L) for r in rows]
        s["entry_slip_%g" % L] = {"n": sum(1 for x in xs if x is not None), "median": _q(xs, 0.5),
                                  "mean": round(sum(x for x in xs if x is not None) / max(1, sum(1 for x in xs if x is not None)), 3),
                                  "p90": _q(xs, 0.9), "adverse_share": round(100.0 * sum(1 for x in xs if x is not None and x > 0) / max(1, sum(1 for x in xs if x is not None)), 1)}
        xc = [r.get("chase_slip_%g" % L) for r in rows]
        if any(x is not None for x in xc):
            s["chase_slip_%g" % L] = {"n": sum(1 for x in xc if x is not None), "median": _q(xc, 0.5), "p90": _q(xc, 0.9)}
    sl = [r.get("sl_slip") for r in rows if r.get("exit_reason") == "SL"]
    s["sl"] = {"n": len(sl), "measured": sum(1 for x in sl if x is not None),
               "not_triggered_on_tick": sum(1 for x in sl if x is None),
               "median": _q(sl, 0.5), "p90": _q(sl, 0.9), "max": _q(sl, 1.0)}
    tp = [r.get("tp_fill_ok") for r in rows if r.get("exit_reason") == "TP"]
    s["tp"] = {"n": len(tp), "fill_ok": sum(1 for x in tp if x), "fill_miss": sum(1 for x in tp if x is False)}
    sp = [r.get("spread_pt") for r in rows]
    s["spread_at_entry"] = {"median": _q(sp, 0.5), "p90": _q(sp, 0.9), "max": _q(sp, 1.0)}
    ov = [abs(r["open_vs_tick"]) for r in rows if r.get("open_vs_tick") is not None]
    s["open_vs_tick_abs_median"] = _q(ov, 0.5)
    s["adopt_latency_s"] = L_ADOPT
    return s


def apply(rows):
    """setup_ledger.jsonl に update を追記（追記のみ・元行は触らない）。"""
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    n = 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for r in rows:
            upd = {"kind": "update", "target": r["id"], "logged_at": now, "slip_src": "tick-sim L=%gs" % L_ADOPT}
            if r.get("spread_pt") is not None:
                upd["spread_pt"] = r["spread_pt"]
            if r.get("slip_%g" % L_ADOPT) is not None:
                upd["slip_pt"] = r["slip_%g" % L_ADOPT]      # 符号付き＝実際の約定差（有利な滑りもそのまま。実測なので両方向を採る）
            if r.get("sl_slip") is not None:
                upd["sl_slip_pt"] = max(0.0, r["sl_slip"])
            if r.get("tp_fill_ok") is not None:
                upd["tp_fill_ok"] = bool(r["tp_fill_ok"])
            if len(upd) > 4:
                f.write(json.dumps(upd, ensure_ascii=False) + "\n"); n += 1
    return n


def run(apply_updates=False, only_missing=True):
    mt5 = mt5_bridge.connect()
    try:
        rows = measure(_load(), mt5, only_missing=only_missing)
    finally:
        mt5.shutdown()
    s = summarize(rows)
    s["generated"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump({"summary": s, "rows": rows}, f, ensure_ascii=False, indent=1)
    n = apply(rows) if apply_updates else 0
    return s, n


if __name__ == "__main__":
    s, n = run(apply_updates=("--apply" in sys.argv), only_missing=("--all" not in sys.argv))
    print(json.dumps(s, ensure_ascii=False, indent=1))
    if n:
        print("台帳へ update 追記:", n)
