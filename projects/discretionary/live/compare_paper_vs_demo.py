# -*- coding: utf-8 -*-
"""
会長Q(2026-10-22): AI再加速の前向き「紙」は本物か=デモ実射との乖離を測る。
  demo_exec_ledger の live(実約定) 各件を、実約定値×実時刻からM5でSL/TP到達を再現して実R化し、
  同じ setup の紙R(reaccel)と突合。入りの late fill / 滑りが優位をどれだけ削るかを可視化。
  読取のみ・発注なし。価格はコックピット8793(=紙と同じ土俵)のM5。
"""
import os, json
import numpy as np, pandas as pd
import datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, HERE)
import setup_engine as se

DEMO_LED = os.path.join(HERE, "demo_exec_ledger.jsonl")
SET_LED = os.path.join(HERE, "setup_ledger.jsonl")


def fold_setups():
    recs = {}
    for ln in open(SET_LED, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if r.get("kind") == "setup":
            recs[r["id"]] = dict(r)
        elif r.get("kind") == "update":
            sid = r.get("target")
            if sid in recs:
                for k in ("reaccel", "chase", "status"):
                    if k in r:
                        recs[sid][k] = r[k]
    return recs


def main():
    recs = fold_setups()
    live = []
    for ln in open(DEMO_LED, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if r.get("kind") == "live" and r.get("ok") and r.get("fill_price"):
            live.append(r)
    m5 = se._fetch_bars(3000)
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    idx = m5.index; n = len(c)
    rows = []
    for r in live:
        sid = r["sid"]; side = r["side"]
        sl = float(r["sl"]); tp = float(r["tp"]); fill = float(r["fill_price"]); ref = float(r.get("entry_ref") or 0)
        # 実約定時刻(logメッセージはJST naive)→UTC
        ft = pd.Timestamp(r["logged_at"]).tz_localize("Asia/Tokyo").tz_convert("UTC")
        ie = int(idx.searchsorted(ft))
        if ie >= n:
            continue
        # 実約定値を建値にM5でSL/TP再現(紙と同じ_simulate)
        sim = se._simulate(o, h, l, c, ie, side, fill, sl, tp, n)
        # 入りの不利方向ギャップ(建値が紙よりどれだけ悪い方へ)
        gap = (ref - fill) if side == "SELL" else (fill - ref)   # +なら不利(紙より悪い入り)
        ra = (recs.get(sid) or {}).get("reaccel") or {}
        rp = ra.get("R")
        risk_real = abs(fill - sl)
        rows.append({"sid": sid, "side": side, "ref": ref, "fill": fill, "gap_adv": round(gap, 2),
                     "sl": sl, "tp": tp, "risk_real": round(risk_real, 2),
                     "R_paper": None if rp is None else round(float(rp), 3),
                     "R_real": None if sim.get("R") is None else round(float(sim["R"]), 3),
                     "exit_real": sim.get("exit_reason"), "kind": (recs.get(sid) or {}).get("wall_kind")})
    df = pd.DataFrame(rows)
    L = ["# 紙 vs デモ実射 乖離（%s）" % pd.Timestamp.now(), "",
         "実射live(ok) = %d件。実約定値×実時刻からM5でSL/TP再現し実R化。" % len(df), ""]
    for _, x in df.iterrows():
        L.append("  %-7s %-4s 紙入%.2f→実約定%.2f 不利ギャップ%+.2f risk実%.2f  紙R%s 実R%s(%s) %s" % (
            x["sid"], x["side"], x["ref"], x["fill"], x["gap_adv"], x["risk_real"],
            x["R_paper"], x["R_real"], x["exit_real"], x["kind"]))
    dd = df.dropna(subset=["R_paper", "R_real"])
    L.append("")
    if len(dd):
        L.append("突合 %d件: 紙 平均R%+.3f / 実(再現) 平均R%+.3f / 差%+.3f" % (
            len(dd), dd["R_paper"].mean(), dd["R_real"].mean(), dd["R_real"].mean() - dd["R_paper"].mean()))
        L.append("入り不利ギャップ 平均%+.2f$ 中央%+.2f$ 最大%+.2f$ (建値が紙よりどれだけ悪い方へ約定したか)" % (
            df["gap_adv"].mean(), df["gap_adv"].median(), df["gap_adv"].max()))
        L.append("実R勝率%.0f%% / 紙R勝率%.0f%%" % (100*(dd["R_real"] > 0).mean(), 100*(dd["R_paper"] > 0).mean()))
    else:
        L.append("突合可能な決着ペアなし(実射が新しく未決着 or 紙R欠落)")
    for ln in L:
        print(ln, flush=True)
    open(os.path.join(HERE, "RESULTS_compare_paper_vs_demo.md"), "w", encoding="utf-8").write("\n".join(L)+"\n")


if __name__ == "__main__":
    main()
