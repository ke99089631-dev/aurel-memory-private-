# -*- coding: utf-8 -*-
"""
会長Q(2026-10-22): コックピットの「AI再加速」前向き成績が異常に良い。なぜこの数字か、まず作られ方を見る。
  setup_ledger の reaccel(status=closed)を畳んで: 期間・本数・勝率・gross/net平均R・出口内訳(TP/SL/TIME)・
  壁種別(外壁/中間)・時代分布・コスト前提 を素で出す。読取のみ・発注なし。
"""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
LED = os.path.join(HERE, "setup_ledger.jsonl")


def fold():
    recs = {}
    for ln in open(LED, encoding="utf-8"):
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
    recs = fold()
    rows = []
    for sid, r in recs.items():
        ra = r.get("reaccel") if isinstance(r.get("reaccel"), dict) else None
        if not ra or ra.get("status") != "closed" or ra.get("R") is None:
            continue
        et = ra.get("entry_time") or r.get("break_time")
        rows.append({"id": sid, "R": float(ra["R"]), "entry": ra.get("entry"), "sl": ra.get("sl"),
                     "exit_reason": ra.get("exit_reason"), "kind": r.get("wall_kind"),
                     "entry_time": int(et) if et else 0,
                     "risk": abs((ra.get("entry") or 0) - (ra.get("sl") or 0))})
    df = pd.DataFrame(rows)
    L = ["# AI再加速 前向き紙の作られ方（setup_ledger実物・%s）" % pd.Timestamp.now(), ""]
    L.append("総reaccel closed = %d本" % len(df))
    if len(df):
        et = pd.to_datetime(df["entry_time"].to_numpy(), unit="s", utc=True)
        L.append("期間 = %s 〜 %s (%d日)" % (et.min().strftime("%Y-%m-%d"), et.max().strftime("%Y-%m-%d"),
                                            (et.max() - et.min()).days))
        yr = pd.Series(et.year)
        L.append("年分布 = " + ", ".join("%d:%d本" % (y, c) for y, c in yr.value_counts().sort_index().items()))
        g = df["R"]
        L.append("")
        L.append("gross 勝率%.0f%% 平均R%+.3f 合計%+.1f (TP手前・コスト控除前)" % (100*(g > 0).mean(), g.mean(), g.sum()))
        rr = df[df["risk"] > 0]
        net = rr["R"] - 0.56 / rr["risk"]
        L.append("net(簡易・0.56/risk) 勝率%.0f%% 平均R%+.3f 合計%+.1f n%d" % (100*(net > 0).mean(), net.mean(), net.sum(), len(rr)))
        L.append("")
        L.append("出口内訳 = " + ", ".join("%s:%d本" % (k, v) for k, v in df["exit_reason"].value_counts().items()))
        L.append("壁種別 = " + ", ".join("%s:%d本" % (k, v) for k, v in df["kind"].value_counts().items()))
        L.append("リスク幅(建値-SL) 中央値%.2f 平均%.2f 最小%.2f 最大%.2f" % (
            df["risk"].median(), df["risk"].mean(), df["risk"].min(), df["risk"].max()))
        # 外壁のみ(本命の物差し)
        o = df[df["kind"] == "outer"]["R"]
        m = df[df["kind"] == "mid"]["R"]
        L.append("")
        L.append("外壁のみ gross 勝率%.0f%% 平均R%+.3f n%d" % (100*(o > 0).mean(), o.mean(), len(o)) if len(o) else "外壁0")
        L.append("中間のみ gross 勝率%.0f%% 平均R%+.3f n%d" % (100*(m > 0).mean(), m.mean(), len(m)) if len(m) else "中間0")
        # 勝ち負けの非対称(TP手前の構造)
        wins = g[g > 0]; losses = g[g < 0]
        L.append("")
        L.append("勝ち平均R %+.3f(n%d) / 負け平均R %+.3f(n%d) = 利小リスク小の形か確認" % (
            wins.mean(), len(wins), losses.mean(), len(losses)))
        # 週別（安定か・ホット streak か）
        df2 = df.copy(); df2["et"] = et.tz_convert("Asia/Tokyo")
        df2["week"] = df2["et"].dt.isocalendar().week.to_numpy()
        L.append("")
        L.append("── 週別 gross（安定か streak か）──")
        for wk, s in df2.groupby("week"):
            L.append("  W%d n%3d 勝率%3.0f%% 平均R%+.3f 合計%+6.1f" % (
                wk, len(s), 100*(s["R"] > 0).mean(), s["R"].mean(), s["R"].sum()))
        # 時間帯（本物帯JST7-12 vs 時間外）。コックピットの数字は全時間含む。
        df2["jh"] = df2["et"].dt.hour.to_numpy()
        hon = df2[(df2["jh"] >= 7) & (df2["jh"] < 12)]["R"]
        off = df2[(df2["jh"] < 7) | (df2["jh"] >= 12)]["R"]
        L.append("")
        L.append("── 時間帯 gross ──")
        L.append("  本物帯JST7-12 n%3d 勝率%3.0f%% 平均R%+.3f" % (len(hon), 100*(hon > 0).mean(), hon.mean()) if len(hon) else "  本物帯0")
        L.append("  時間外       n%3d 勝率%3.0f%% 平均R%+.3f" % (len(off), 100*(off > 0).mean(), off.mean()) if len(off) else "  時間外0")
        # 外壁×本物帯（本命の物差し）
        ob = df2[(df2["kind"] == "outer") & (df2["jh"] >= 7) & (df2["jh"] < 12)]["R"]
        L.append("  外壁×本物帯 n%3d 勝率%3.0f%% 平均R%+.3f" % (len(ob), 100*(ob > 0).mean(), ob.mean()) if len(ob) else "  外壁×本物帯0")
    for ln in L:
        print(ln, flush=True)
    open(os.path.join(HERE, "RESULTS_analyze_reaccel_forward.md"), "w", encoding="utf-8").write("\n".join(L)+"\n")


if __name__ == "__main__":
    main()
