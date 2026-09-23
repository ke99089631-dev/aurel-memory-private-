# -*- coding: utf-8 -*-
"""
壁検出（車線3 v3a の急所）: 「過去100本高安」の粗い代理をやめ、
  会長のように『何度もタッチ＆反発して効いている価格』を壁として選ぶ。
  - スイング高安を検出 → 価格が近いものを1本の壁レベルに集約 → タッチ回数=強度。
  - 箱の上下壁（外側=黄）と中間壁（青）を、現在価格を挟む強い壁から決める。
金ゼロ・読取のみ・先読みなし（渡された窓＝過去バーだけで計算）。
"""
import numpy as np


def _swings(h, l, k=3):
    """k本両側より高い/低いバー=スイング高/安。(idx, price) のリスト。"""
    highs, lows = [], []
    n = len(h)
    for i in range(k, n - k):
        seg_h = h[i - k:i + k + 1]; seg_l = l[i - k:i + k + 1]
        if h[i] >= seg_h.max():
            highs.append((i, float(h[i])))
        if l[i] <= seg_l.min():
            lows.append((i, float(l[i])))
    return highs, lows


def _cluster(points, tol):
    """価格が tol 以内のスイングを1レベルに集約。強い順(タッチ数)で返す。"""
    if not points:
        return []
    pts = sorted(points, key=lambda x: x[1])
    levels = []
    cur = [pts[0]]
    for idx, price in pts[1:]:
        if abs(price - cur[-1][1]) <= tol:
            cur.append((idx, price))
        else:
            levels.append(cur); cur = [(idx, price)]
    levels.append(cur)
    out = []
    for grp in levels:
        prices = [p for _, p in grp]
        idxs = [i for i, _ in grp]
        out.append({"price": round(float(np.mean(prices)), 3),
                    "touches": len(grp), "last_idx": max(idxs)})
    return out


def find_walls(h, l, c, atr):
    """窓(過去バー配列)から壁レベル群を返す。tol は ATR 基準。"""
    tol = max(atr * 0.6, float(np.mean(np.abs(c))) * 0.0006) if atr > 0 else \
        (c[-1] * 0.0008 if len(c) else 1.0)
    highs, lows = _swings(h, l, k=3)
    res = _cluster(highs, tol)   # 上値抵抗(レジ)
    sup = _cluster(lows, tol)    # 下値支持(サポ)
    for w in res:
        w["kind"] = "res"
    for w in sup:
        w["kind"] = "sup"
    return res + sup


def pick_box(walls, price, max_dist, min_touches=2):
    """現在価格を挟む『効いている壁』で箱を決める。上壁/下壁(黄)＋中間(青)。
       強い壁が無ければ None を返す（=見送り材料）。"""
    res = [w for w in walls if w["kind"] == "res" and w["price"] > price
           and w["price"] - price <= max_dist]
    sup = [w for w in walls if w["kind"] == "sup" and w["price"] < price
           and price - w["price"] <= max_dist]
    # 近くて強い順（タッチ数優先、近さ次点）
    res.sort(key=lambda w: (-w["touches"], w["price"] - price))
    sup.sort(key=lambda w: (-w["touches"], price - w["price"]))
    up = next((w for w in res if w["touches"] >= min_touches), res[0] if res else None)
    dn = next((w for w in sup if w["touches"] >= min_touches), sup[0] if sup else None)
    if up is None or dn is None:
        return None
    # 中間壁(青): 上下の間にある最も強い壁、無ければ中点
    mids = [w for w in walls if dn["price"] < w["price"] < up["price"]]
    mids.sort(key=lambda w: -w["touches"])
    mid = mids[0]["price"] if mids else round((up["price"] + dn["price"]) / 2.0, 3)
    return {"up": up["price"], "dn": dn["price"], "mid": mid,
            "up_touches": up["touches"], "dn_touches": dn["touches"],
            "width": round(up["price"] - dn["price"], 3)}
