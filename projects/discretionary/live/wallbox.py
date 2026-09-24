# -*- coding: utf-8 -*-
"""
壁→壁 動的ボックス（①壁の動的組み直し）。
  狙い: 「効いてる固定壁」を保ちつつ、価格がトレンドで離れても箱が置いてけぼりにならず、
        ブレイク/だらだら下げで壁が段階的に乗り換わる（中間壁も入れ替わる）ようにする。
  方式（先読みなし・スナップショット毎に確定的）:
    1. 直近~200本からスイング＋タッチで「効いてる壁レベル」を検出（touch>=2優先）。
    2. 直近~48本(4h)の値動きレンジ±余白で「今いる帯」を作り、その帯にかかる壁だけを候補に。
       → 価格が下へ流れれば候補も下の壁群に移り、箱が段階的に再アンカーされる。
    3. 上壁=候補の最高レジ / 下壁=候補の最安サポ / 中間=間で一番強い壁(無ければ中点)。
    4. 価格が上/下壁の外なら break(メジャードムーブ目標つき)。
金ゼロ・読取のみ・発注なし。
"""
import numpy as np
from walls import find_walls

WALL_WIN = 200      # 壁検出・タッチ数カウント窓（M5本 ≈16h）
BAND_WIN = 48       # 「今いる帯」を作る直近窓（M5本 ≈4h）
BAND_PAD_FR = 0.45  # 帯の上下パディング（帯幅×）
SL_PAD_FR = 0.33


def dynamic_box(m5):
    h = m5["high"].to_numpy(); l = m5["low"].to_numpy(); c = m5["close"].to_numpy()
    n = len(c)
    if n < 40:
        return None, None
    atr = float(np.mean(h[max(1, n - 14):n] - l[max(1, n - 14):n])) if n > 15 else 0.0
    w0 = max(0, n - WALL_WIN)
    ws = find_walls(h[w0:n], l[w0:n], c[w0:n], atr)
    strong = [x for x in ws if x["touches"] >= 2] or ws
    if len(strong) < 2:
        return None, None

    # 今いる帯（直近BAND_WIN本のレンジ±パディング）
    b = max(0, n - BAND_WIN)
    rb_hi = float(np.max(h[b:n])); rb_lo = float(np.min(l[b:n]))
    span = rb_hi - rb_lo if rb_hi > rb_lo else max(atr * 3, 1.0)
    pad = BAND_PAD_FR * span
    lo_b, hi_b = rb_lo - pad, rb_hi + pad
    cand = [x for x in strong if lo_b <= x["price"] <= hi_b]
    if len(cand) < 2:
        cand = strong
    # ★急なトレンドで価格が「効いてる壁」の外に出たまま（新安値/新高値を更新中）の時は、
    #   直近のスイング（タッチ1回）も候補に入れて箱を価格側へ乗り換えさせる＝置いてけぼり防止。
    price0 = float(c[-1])
    if cand and (price0 < min(x["price"] for x in cand) or price0 > max(x["price"] for x in cand)):
        weak = [x for x in ws if x["touches"] < 2 and lo_b <= x["price"] <= hi_b]
        cand = cand + weak

    res = [x for x in cand if x["kind"] == "res"]
    sup = [x for x in cand if x["kind"] == "sup"]
    # レジ/サポが片方無ければ、候補全体の最高/最安で代用（帯の上下端）
    up = (max(res, key=lambda x: x["price"]) if res else max(cand, key=lambda x: x["price"]))
    dn = (min(sup, key=lambda x: x["price"]) if sup else min(cand, key=lambda x: x["price"]))
    up_p, dn_p = up["price"], dn["price"]
    if up_p <= dn_p:
        return None, None
    width = up_p - dn_p
    mids = [x for x in cand if dn_p < x["price"] < up_p]
    mid_p = max(mids, key=lambda x: x["touches"])["price"] if mids else (up_p + dn_p) / 2.0

    box = {"up": round(up_p, 3), "dn": round(dn_p, 3), "mid": round(mid_p, 3),
           "width": round(width, 3),
           "up_touches": int(up.get("touches", 0)), "dn_touches": int(dn.get("touches", 0))}

    price = float(c[-1])
    brk = None
    # ★TPは会長ルール「溜まり幅＝壁と中間線の間」（箱全幅ではない）。SLは壁の内側(ブレイク失敗の位置)。
    if price < dn_p:
        pool = pool_width(dn_p, mid_p, up_p, "DOWN")
        brk = {"dir": "DOWN", "wall": round(dn_p, 3), "width": round(pool, 3),
               "tp": round(dn_p - pool, 3), "sl": round(dn_p + pool * SL_PAD_FR, 3)}
    elif price > up_p:
        pool = pool_width(dn_p, mid_p, up_p, "UP")
        brk = {"dir": "UP", "wall": round(up_p, 3), "width": round(pool, 3),
               "tp": round(up_p + pool, 3), "sl": round(up_p - pool * SL_PAD_FR, 3)}
    return box, brk


def pool_width(dn_p, mid_p, up_p, direction):
    """溜まり幅: 下抜けなら (中間−下壁)、上抜けなら (上壁−中間)。中間が壁に貼り付いて極端に細い時は半幅で代用。"""
    full = up_p - dn_p
    pool = (mid_p - dn_p) if direction == "DOWN" else (up_p - mid_p)
    if pool < full * 0.2:
        pool = full / 2.0
    return pool
