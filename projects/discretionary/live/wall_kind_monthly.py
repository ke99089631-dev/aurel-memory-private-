# -*- coding: utf-8 -*-
"""外壁 vs 中壁を毎月並べて出す(観測のみ・読取のみ・発注なし)。

なぜ必要か(2026-11-28 会長):
  中壁は9回も「良い/悪い」を往復した。原因の一つは、中壁の数字が普段どこにも
  表示されず、ふいに目に入ったときだけ驚いて議論が再発すること。
  常に見えていれば驚きが起きない。だから毎日このレポートに載せる。

処分は固定(REACCEL-INVENTORY.md 1d):
  中壁は撃たない。理由は成績ではなく「測定が再現しない」こと(scan +0.087 vs 台帳 +0.337)。
  この表の数字が良く見えても、ゲートA(壁の引き方を素の24h高安に直して再現性が外壁並みになる)
  が開くまで採用の議論はしない。表は観測用。
"""
import sys
import os
import math
import datetime as dt
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import danger_gauge as dg

# 会長のカード初弾(=WEBチャートの窓の始まり)
CARD_FIRST = dt.datetime(2026, 9, 22, 4, 49,
                         tzinfo=dt.timezone(dt.timedelta(hours=9))).timestamp()


def load():
    cm = dg._cost_model()
    out = []
    for r in dg._load():
        ra = r.get("reaccel") if isinstance(r.get("reaccel"), dict) else None
        if not ra or ra.get("status") != "closed" or ra.get("R") is None:
            continue
        bt = int(r.get("break_time") or 0)
        if not bt:
            continue
        out.append({
            "bt": bt,
            "R": dg._net_R(ra, r.get("jst_hour"), cm),
            "wk": r.get("wall_kind"),
            "m": dt.datetime.fromtimestamp(
                bt, dt.timezone(dt.timedelta(hours=9))).strftime("%Y-%m"),
        })
    out.sort(key=lambda x: x["bt"])
    return out


def agg(xs):
    if not xs:
        return None
    rs = [x["R"] for x in xs]
    n = len(rs)
    s = sum(rs)
    m = s / n
    sd = st.stdev(rs) if n > 1 else 0.0
    t = (m / (sd / math.sqrt(n))) if sd else float("nan")
    w = sum(1 for v in rs if v > 0)
    c = p = 0.0
    dd = 0.0
    for v in rs:
        c += v
        p = max(p, c)
        dd = min(dd, c - p)
    return dict(n=n, s=s, m=m, t=t, wr=100.0 * w / n, dd=dd)


def fmt(a):
    if not a:
        return "%22s" % "0本"
    return "%4d本 %+7.2fR 1本%+.4f t=%5.2f 勝率%3.0f%% 谷%+7.2fR" % (
        a["n"], a["s"], a["m"], a["t"], a["wr"], a["dd"])


def main():
    tr = load()
    win = [x for x in tr if x["bt"] >= CARD_FIRST]
    print("")
    print("=" * 112)
    print("[%s] 外壁 vs 中壁 月次(紙・正味R・会長のカード初弾 2026-09-22 以降)" %
          dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("  ※中壁は撃たない(再現性が直るまで)。この表は観測用。良く見えてもゲートAが開くまで採用しない。")
    print("=" * 112)
    for m in sorted(set(x["m"] for x in win)):
        xs = [x for x in win if x["m"] == m]
        o = agg([x for x in xs if x["wk"] == "outer"])
        d = agg([x for x in xs if x["wk"] == "mid"])
        print("  %s  外壁 %s" % (m, fmt(o)))
        print("           中壁 %s" % fmt(d))
    print("  " + "-" * 108)
    o = agg([x for x in win if x["wk"] == "outer"])
    d = agg([x for x in win if x["wk"] == "mid"])
    print("  合計     外壁 %s" % fmt(o))
    print("           中壁 %s" % fmt(d))
    if o and d:
        print("  差(中壁-外壁) 1本あたり %+.4fR" % (d["m"] - o["m"]))
    print("  近年バックテスト参考(2024-26・箱の引き方が優位を殺すので絶対値は使えない・順位のみ):")
    print("    外壁 -0.006R(2987本) / 中壁 -0.068R(1380本) ... 近年で切り直しても中壁は改善していない")


if __name__ == "__main__":
    main()
