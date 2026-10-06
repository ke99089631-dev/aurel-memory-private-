# -*- coding: utf-8 -*-
"""ルールセット v1（会長GO 2026-10-06・「雨の日ルール」）。読取のみ・発注なし。

目的: AI(setup_engine)の各セットアップに「v1 採用/除外」フラグを建玉時点で付け、
      全件と採用側を並走(shadow)させて前向きに検証する。過去の負けを除くのではなく、
      同じ基準で未来の負けに入らないことを確かめる。

しきい値は 2026-10-06 時点の主レーン120本で決めた(in-sample)。以後は触らない。
再判定は採用側30本到達時（会長と同じ物差し）。

根拠(episodic/2026-10-06.md):
  - 雨(直前10本の決着のうちダマシ≧80%): 10月の40本中34本を除外(-22.5R回避)。9月は+17Rも削る＝ブレーキであって入り方の信号ではない。
  - 時間帯(p_real≧21.1 / 下位1/3除外): 除外側は9月-1.0R・10月-9.2R＝両期間で負け側だけ切る。最も頑健。
  - 箱の締まり(tightness_pct<0.159 / 上位1/3除外): 除外側は9月-7.2R・10月-6.7R＝両期間で負け。
"""

VERSION = "v1"
FROZEN_AT = "2026-10-06"

RAIN_N = 10            # 直前この本数の決着(exit_time ≦ ブレイク時刻)でダマシ率を見る
RAIN_MIN_N = 8         # これ未満しか履歴が無ければ雨判定は保留(None)＝採用側に残す
RAIN_FAKE_RATE = 0.80  # ダマシ率がこれ以上なら「雨」＝入らない
P_REAL_MIN = 21.1      # 時間帯の本物率予測(pred.p_real)がこれ未満なら除外
TIGHT_MAX = 0.159      # 箱の締まり(features.tightness_pct)がこれ以上なら除外


def rain_rate(break_time, closed_history, n=RAIN_N, min_n=RAIN_MIN_N):
    """break_time 以前に決着していた直近n本のダマシ率。履歴不足なら None。
       closed_history: status=closed の記録(dict)の列。exit_time/outcome を使う。"""
    prev = [r for r in closed_history
            if r.get("status") == "closed" and r.get("exit_time") is not None
            and int(r["exit_time"]) <= int(break_time)]
    prev.sort(key=lambda r: int(r["exit_time"]))
    prev = prev[-n:]
    if len(prev) < min_n:
        return None, len(prev)
    fakes = sum(1 for r in prev if r.get("outcome") == "ダマシ")
    return round(fakes / len(prev), 3), len(prev)


def evaluate(setup, closed_history):
    """セットアップ1件に v1 判定を付ける。結果は setup["v1"] に入れる想定の dict。
       建玉時点で知り得る情報(ブレイク時刻・時間帯予測・箱の特徴・過去の決着)だけを使う。"""
    rr, nprev = rain_rate(setup.get("break_time"), closed_history)
    rain = (rr is not None and rr >= RAIN_FAKE_RATE)
    p_real = (setup.get("pred") or {}).get("p_real")
    hour_ok = (p_real is not None and float(p_real) >= P_REAL_MIN)
    tight = (setup.get("features") or {}).get("tightness_pct")
    tight_ok = (tight is not None and float(tight) < TIGHT_MAX)
    reasons = []
    if rain:
        reasons.append("雨(直前%d本ダマシ%.0f%%)" % (nprev, rr * 100))
    if not hour_ok:
        reasons.append("時間帯(本物率%s<%.1f)" % (("%.1f" % p_real) if p_real is not None else "?", P_REAL_MIN))
    if not tight_ok:
        reasons.append("箱の締まり(%s≧%.3f)" % (("%.3f" % tight) if tight is not None else "?", TIGHT_MAX))
    return {
        "version": VERSION, "frozen_at": FROZEN_AT,
        "rain_rate": rr, "rain_n": nprev, "rain": rain,
        "hour_ok": hour_ok, "tight_ok": tight_ok,
        "keep": (not rain) and hour_ok and tight_ok,
        "drop_reasons": reasons,
    }


def current_weather(closed_history, now_epoch):
    """今の雨判定（次に出るセットアップがどう扱われるか）。携帯/チャート表示用。"""
    rr, nprev = rain_rate(now_epoch, closed_history)
    return {"rain_rate": rr, "rain_n": nprev,
            "rain": (rr is not None and rr >= RAIN_FAKE_RATE),
            "threshold": RAIN_FAKE_RATE, "version": VERSION}
