# -*- coding: utf-8 -*-
"""
ピンバー×壁 の共通定義（ライブ用）。2026-11-02 会長GO『1、2、3を実行してくれ』。
  10-31 の一次計測 research/wall_to_wall/pinbar_wall.py と同じ事前固定を、そのまま写す（数字は動かさない）。
  使う側: serve_chart.py（チャートに票を描く＝①）/ pinbar_lane.py（反発型の紙レーン＝②）。
  読取のみ・発注なし・金ゼロ。

★事前固定（pinbar_wall.py 冒頭と同一）:
  箱=過去288本(現バー除外)の最高/最安(素の24h高安)。幅<10は除外。
  タッチ=高値(安値)が壁±幅×0.08に入る。終値は壁の内側(実体で抜けた足はブレイク=別クラス)。
  ピンバー=壁側ヒゲ≧実体×2 かつ 壁側ヒゲ≧全長×2/3。
  同じ側で6本以内の連続イベントは最初の1本だけ数える。
  票=その壁(±幅×0.08)に過去288本で出たピンバータッチの数。
会長の線(user_lines)への票: 同じ足の形の定義を「線＝壁」に当てて数える（線は箱の壁でなくてもよい）。
"""
import numpy as np
import pandas as pd

BOX = 288
WIDTH_MIN = 10.0
BAND = 0.08
WICK_BODY = 2.0
WICK_RANGE = 2.0 / 3.0
DEDUP = 6


def _is_pin(o, h, l, c, i, side):
    """side=+1: 上壁側(上ヒゲ) / -1: 下壁側(下ヒゲ)。足iがピンバーの形か。"""
    rng = h[i] - l[i]
    if rng <= 0:
        return False
    body = abs(c[i] - o[i])
    top = max(o[i], c[i]); bot = min(o[i], c[i])
    wick = (h[i] - top) if side == +1 else (bot - l[i])
    return (wick >= WICK_BODY * body) and (wick >= WICK_RANGE * rng)


def scan_pins(o, h, l, c):
    """箱(素の24h高安)の壁へのピンバータッチを全部返す（pinbar_wall.events の touches のうち pin=True だけ）。
       各要素: i / side(+1上壁→売り候補, -1下壁→買い候補) / wall / width / votes(その時点の票) /
               wick_ext(ヒゲ先) / body_edge(実体の内側端) / beyond(ヒゲが壁を越えたか)。
       入力は確定足のみ(形成中は呼ぶ側で除外)。先読みなし。"""
    o = np.asarray(o, float); h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    n = len(c)
    up = pd.Series(h).rolling(BOX).max().shift(1).to_numpy()
    dn = pd.Series(l).rolling(BOX).min().shift(1).to_numpy()
    pins = []
    last_t = {+1: -99, -1: -99}
    pin_hist = {+1: [], -1: []}
    for i in range(BOX + 1, n):
        if not (np.isfinite(up[i]) and np.isfinite(dn[i])):
            continue
        w = up[i] - dn[i]
        if w < WIDTH_MIN:
            continue
        band = w * BAND
        for side, wall in ((+1, up[i]), (-1, dn[i])):
            if side == +1:
                touched = h[i] >= wall - band; inside = c[i] < wall; broke = c[i] > wall
            else:
                touched = l[i] <= wall + band; inside = c[i] > wall; broke = c[i] < wall
            if broke:
                continue
            if touched and inside and (h[i] - l[i]) > 0:
                # pinbar_wall.events と同じ順序: 票は追記前に数える / 記録は6本dedup / 票の履歴はdedupせず全ピンバー
                pin = _is_pin(o, h, l, c, i, side)
                hist = pin_hist[side]
                votes = sum(1 for (j, wj) in hist if i - j <= BOX and abs(wj - wall) <= band)
                if i - last_t[side] > DEDUP and pin:
                    pins.append(dict(
                        i=i, side=side, wall=float(wall), width=float(w), votes=int(votes),
                        wick_ext=float(h[i] if side == +1 else l[i]),
                        body_edge=float(min(o[i], c[i]) if side == +1 else max(o[i], c[i])),
                        beyond=bool(h[i] > wall) if side == +1 else bool(l[i] < wall)))
                last_t[side] = i
                if pin:
                    hist.append((i, wall))
                    if len(hist) > 400:
                        del hist[:200]
    return pins, pin_hist


def votes_now(pin_hist, n, side, wall, band):
    """今(確定足数n)の壁 wall(側side)に入っている票＝過去288本のピンバータッチ数（研究と同じ: dedup前の全ピンバー）。"""
    return sum(1 for (j, wj) in pin_hist[side] if n - 1 - j <= BOX and abs(wj - wall) <= band)


def line_votes(o, h, l, c, price, band, lookback=BOX):
    """会長の線(price)を壁と見なして票を数える。上から当たった上ヒゲ / 下から当たった下ヒゲの両方。
       戻り: (票数, [(i, side), ...])。直近 lookback 本(確定足)だけ。先読みなし。"""
    o = np.asarray(o, float); h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    n = len(c)
    hits = []
    last_t = {+1: -99, -1: -99}
    for i in range(max(1, n - lookback), n):
        for side in (+1, -1):
            if side == +1:
                touched = h[i] >= price - band; inside = c[i] < price and o[i] < price
            else:
                touched = l[i] <= price + band; inside = c[i] > price and o[i] > price
            if touched and inside and _is_pin(o, h, l, c, i, side):
                if i - last_t[side] > DEDUP:
                    hits.append((i, side))
                last_t[side] = i
    return len(hits), hits
