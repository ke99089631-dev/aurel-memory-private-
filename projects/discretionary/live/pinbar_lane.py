# -*- coding: utf-8 -*-
"""
②ピンバー反発型 紙レーン（会長GO 2026-11-02『1、2、3を実行してくれ』）。発注なし・金ゼロ・読取のみ。
  10-31 一次計測(research/wall_to_wall/pinbar_wall.py (C))を、ライブ足でそのまま前向きに流す。会長の裁量台帳とは絶対に混ぜない。

★事前固定（結果を見て動かさない。関門まで中身は触らない）:
  定義=pinbar_live.py(=10-31計測と同一): 箱=直近288本(現バー除外)の高安・幅<10除外・タッチ=壁±幅8%・
       ピンバー=壁側ヒゲ≧実体2倍かつ全長2/3・同側6本以内は最初の1本・票=その壁に過去288本で出たピンバー数
  絞らない: 全ピンバーを記録し 票0/票1/票2+・帯(本物帯/中立/ダマシ巣)・上下 をラベルで貼る(会長『票0に絞るかは会長が決める』→先に全部)
  確認=ピンバーの後3本以内に、終値がピンバー実体の内側端(body_edge)を抜けたら。その前に終値で壁を抜けたら不成立(invalid_wallbreak)
  入り=確認足の次の足の始値 / SL=ヒゲ先の外0.20 / TP=反対壁の手前(壁∓幅×0.85) / リスク<3は不成立(skip_risk) / 利幅≤0は不成立(skip_reward)
  決着=高安で判定・同足SL/TP同時はSL優先・時間切れ288本(終値)・netR=R−0.56/リスク(研究と同じ固定コスト)。実測spreadも別に記録
  関門=確定30本で報告(平均netR・票別・帯別)。採用/不採用/絞りは会長。30本未満は常に「サンプル不足」。
  10-31の数字(参考・近年n111): 平均+0.378R・勝率28%・p0.097・年ぶれ・票0が最良(+0.57)/票1は負(-0.37)。未証明。
データ源=8793 /api/data(形成中の最終バーは除外)。台帳 pinbar_ledger.jsonl 追記のみ(kind=pin / kind=update)。
"""
import os
import sys
import json
import time
import datetime as dt
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import pandas as pd
import pinbar_live as pl

API = "http://100.73.107.61:8793/api/data?n=2000"
TICK_API = "http://100.73.107.61:8793/api/tick"
LEDGER = os.path.join(HERE, "pinbar_ledger.jsonl")
STATE = os.path.join(HERE, "pinbar_state.json")
INTERVAL = 30          # 秒。足は5分なので十分(確認足の直後に拾える)
CONF_BARS = 3
SL_PAD = 0.20
TP_FRAC = 0.85
MAX_HOLD = 288
RISK_MIN = 3.0
COST = 0.56
TARGET = 30
JST = dt.timezone(dt.timedelta(hours=9))


def _now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _fetch_bars():
    with urllib.request.urlopen(API, timeout=25) as r:
        d = json.loads(r.read().decode("utf-8"))
    bars = d.get("bars", [])
    if len(bars) < pl.BOX + 10:
        return None
    bars = bars[:-1]                       # 形成中の最終バーは使わない
    df = pd.DataFrame(bars)
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    return df.set_index("dt")[["time", "open", "high", "low", "close"]]


def _fetch_spread():
    try:
        with urllib.request.urlopen(TICK_API, timeout=10) as r:
            d = json.loads(r.read().decode("utf-8"))
        t = d.get("tick") or {}
        return t.get("spread_pt")
    except Exception:
        return None


def _jst(epoch):
    return dt.datetime.fromtimestamp(int(epoch), JST).strftime("%Y-%m-%d %H:%M")


def _zone(epoch):
    jh = dt.datetime.fromtimestamp(int(epoch), JST).hour
    return "本物帯" if 7 <= jh < 12 else ("ダマシ巣" if 0 <= jh < 5 else "中立"), jh


def load_ledger():
    recs, order = {}, []
    if os.path.exists(LEDGER):
        for ln in open(LEDGER, encoding="utf-8"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("kind") == "pin":
                recs[r["id"]] = r; order.append(r["id"])
            elif r.get("kind") == "update":
                t = recs.get(r.get("target"))
                if t:
                    for k, v in r.items():
                        if k not in ("kind", "target", "logged_at"):
                            t[k] = v
    return recs, order


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {"last_pin_time": 0}


def save_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"))


def _write(f, rec):
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _update(f, rec, **fields):
    upd = {"kind": "update", "target": rec["id"], "logged_at": _now()}
    upd.update(fields)
    _write(f, upd)
    rec.update(fields)


def advance(rec, m5, pos, o, h, l, c, t, f):
    """1記録を今の足まで前進させる。waiting→(open|no_confirm|invalid_wallbreak|skip_*)、open→closed。"""
    n = len(c)
    k0 = pos.get(int(rec["pin_time"]))
    if k0 is None:
        if rec.get("status") in ("waiting", "open"):
            _update(f, rec, status="lost", note="ピンバー足が取得窓から外れた")
        return
    side = rec["side_num"]; wall = rec["wall"]
    if rec.get("status") == "waiting":
        conf = None
        for k in range(k0 + 1, min(n, k0 + 1 + CONF_BARS)):
            if (side == +1 and c[k] > wall) or (side == -1 and c[k] < wall):
                _update(f, rec, status="invalid_wallbreak", resolved_time=int(t[k]), resolved_jst=_jst(t[k]))
                return
            if (side == +1 and c[k] < rec["body_edge"]) or (side == -1 and c[k] > rec["body_edge"]):
                conf = k; break
        if conf is None:
            if n - 1 >= k0 + CONF_BARS:
                _update(f, rec, status="no_confirm", resolved_time=int(t[min(n - 1, k0 + CONF_BARS)]))
            return
        if conf + 1 >= n:
            return                                  # 確認は出たが入る足がまだ確定していない→次回
        ent = conf + 1
        entry = float(o[ent])
        sl = (rec["wick_ext"] + SL_PAD) if side == +1 else (rec["wick_ext"] - SL_PAD)
        risk = (sl - entry) if side == +1 else (entry - sl)
        tp = (wall - TP_FRAC * rec["width"]) if side == +1 else (wall + TP_FRAC * rec["width"])
        reward = (entry - tp) if side == +1 else (tp - entry)
        base = dict(confirm_time=int(t[conf]), confirm_jst=_jst(t[conf]), entry_time=int(t[ent]), entry_jst=_jst(t[ent]),
                    entry=round(entry, 3), sl=round(sl, 3), tp=round(tp, 3), risk=round(risk, 3),
                    rr=round(reward / risk, 2) if risk > 0 else None)
        if risk < RISK_MIN:
            _update(f, rec, status="skip_risk", **base); return
        if reward <= 0:
            _update(f, rec, status="skip_reward", **base); return
        sp = _fetch_spread()
        _update(f, rec, status="open", spread_pt=sp, mfe_R=0.0, mae_R=0.0, hold_bars=0, **base)
    if rec.get("status") == "open":
        ent = pos.get(int(rec["entry_time"]))
        if ent is None:
            _update(f, rec, status="lost", note="建玉の足が取得窓から外れた"); return
        entry = rec["entry"]; sl = rec["sl"]; tp = rec["tp"]; risk = rec["risk"]
        mfe = rec.get("mfe_R", 0.0); mae = rec.get("mae_R", 0.0)
        exit_px = None; reason = None; kx = None
        for k in range(ent, n):
            fav = ((entry - l[k]) if side == +1 else (h[k] - entry)) / risk
            adv = ((h[k] - entry) if side == +1 else (entry - l[k])) / risk
            mfe = max(mfe, fav); mae = max(mae, adv)
            if side == +1:
                if h[k] >= sl: exit_px, reason, kx = sl, "SL", k; break
                if l[k] <= tp: exit_px, reason, kx = tp, "TP", k; break
            else:
                if l[k] <= sl: exit_px, reason, kx = sl, "SL", k; break
                if h[k] >= tp: exit_px, reason, kx = tp, "TP", k; break
            if k - ent + 1 >= MAX_HOLD:
                exit_px, reason, kx = float(c[k]), "TIME", k; break
        hold = (kx - ent + 1) if kx is not None else (n - ent)
        if exit_px is None:
            if hold != rec.get("hold_bars") or round(mfe, 2) != rec.get("mfe_R") or round(mae, 2) != rec.get("mae_R"):
                _update(f, rec, mfe_R=round(mfe, 2), mae_R=round(mae, 2), hold_bars=int(hold))
            return
        R = ((entry - exit_px) if side == +1 else (exit_px - entry)) / risk
        _update(f, rec, status="closed", exit=round(float(exit_px), 3), exit_reason=reason, exit_time=int(t[kx]),
                exit_jst=_jst(t[kx]), hold_bars=int(hold), mfe_R=round(mfe, 2), mae_R=round(mae, 2),
                R=round(R, 3), netR=round(R - COST / risk, 3))


def sync_once():
    m5 = _fetch_bars()
    if m5 is None:
        return 0, 0
    o = m5["open"].to_numpy(float); h = m5["high"].to_numpy(float)
    l = m5["low"].to_numpy(float); c = m5["close"].to_numpy(float)
    t = m5["time"].to_numpy()
    pos = {int(t[i]): i for i in range(len(t))}
    recs, order = load_ledger()
    st = load_state()
    pins, _hist = pl.scan_pins(o, h, l, c)
    added = 0
    maxn = 0
    for rid in order:
        try:
            maxn = max(maxn, int(rid.split("-")[1]))
        except Exception:
            pass
    with open(LEDGER, "a", encoding="utf-8") as f:
        for p in pins:
            pt = int(t[p["i"]])
            if pt <= int(st.get("last_pin_time", 0)):
                continue
            maxn += 1
            zone, jh = _zone(pt)
            rec = {"id": "P-%04d" % maxn, "kind": "pin", "lane": "pinbar", "logged_at": _now(),
                   "pin_time": pt, "pin_jst": _jst(pt), "side_num": p["side"],
                   "side": "SELL" if p["side"] == +1 else "BUY",
                   "wall": round(p["wall"], 3), "width": round(p["width"], 3), "votes": p["votes"],
                   "votes_lab": "票0" if p["votes"] == 0 else ("票1" if p["votes"] == 1 else "票2+"),
                   "wick_ext": round(p["wick_ext"], 3), "body_edge": round(p["body_edge"], 3), "beyond": p["beyond"],
                   "zone": zone, "jst_hour": jh, "status": "waiting"}
            _write(f, rec)
            recs[rec["id"]] = rec; order.append(rec["id"]); added += 1
            st["last_pin_time"] = max(int(st.get("last_pin_time", 0)), pt)
        before = {rid: recs[rid].get("status") for rid in order}
        for rid in order:
            r = recs[rid]
            if r.get("status") in ("waiting", "open"):
                try:
                    advance(r, m5, pos, o, h, l, c, t, f)
                except Exception as e:
                    sys.stderr.write("advance %s err: %s\n" % (rid, e))
        changed = sum(1 for rid in order if recs[rid].get("status") != before.get(rid))
    save_state(st)
    return added, changed


def summary():
    recs, order = load_ledger()
    closed = [recs[i] for i in order if recs[i].get("status") == "closed" and recs[i].get("netR") is not None]
    if not closed:
        return "決着0本"
    r = np.array([x["netR"] for x in closed])
    return "決着%d/%d 勝率%.0f%% 平均net%+.3f 合計%+.2f" % (len(closed), TARGET, 100 * (r > 0).mean(), r.mean(), r.sum())


def main():
    print("ピンバー反発型 紙レーン起動（%d秒ごと・発注なし・金ゼロ・関門=確定%d本）" % (INTERVAL, TARGET), flush=True)
    if "--once" in sys.argv:
        a, u = sync_once(); print("once: +%d 新規 / %d 状態変化 / %s" % (a, u, summary()), flush=True); return
    while True:
        try:
            a, u = sync_once()
            if a or u:
                print("%s +%d 新規 / %d 状態変化 / %s" % (dt.datetime.now().strftime("%H:%M:%S"), a, u, summary()), flush=True)
        except Exception as e:
            sys.stderr.write("sync err: %s\n" % e)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
