# -*- coding: utf-8 -*-
"""
壁→壁 コックピット: 動くライブチャートを Tailscale:8793 で配る独立サーバ。
  既存のチャット室サーバ(8792)・司令室(7878)には一切触れない（別プロセス・別ポート）。
  ブラウザ側で TradingView Lightweight Charts が描く＝ズーム/パン/スクロール/リアルタイム更新。
  サーバはデータ(JSON)を配るだけ:
    GET /                       → chart_live.html（対話チャート本体）
    GET /lightweight-charts.js  → 取り込んだ描画ライブラリ（ローカル・ネット非依存）
    GET /api/data?n=1500        → 直近n本のM5 + 現在tick + 壁(箱/中間/直近ブレイクのTP/SL) を JSON
  MT5接続は開いたまま保持し、リクエスト毎に読むだけ（読取専用・発注なし・金は動かない）。
  Tailscale IP のみにバインド。
"""
import os
import sys
import json
import time
import http.server
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chart_gen  # current_box / detect_last_break / latest_m5 を再利用

HOST = "100.73.107.61"     # Tailscale IP のみ（Wi-Fi/インターネットには出さない）
PORT = 8793
PAGE = os.path.join(HERE, "chart_live.html")
LIB = os.path.join(HERE, "lightweight-charts.js")

# ── MT5接続をプロセス内で保持（都度 initialize/shutdown しない）──────────
_MT5 = None


def _get_mt5():
    """保持中の接続を返す。無ければ張り直す。失敗時は None を返して履歴にフォールバックさせる。"""
    global _MT5
    if _MT5 is not None:
        return _MT5
    try:
        import mt5_bridge
        _MT5 = mt5_bridge.connect()   # 口座27972608限定・発注なし・安全弁つき
    except Exception as e:
        sys.stderr.write("[MT5接続不可→履歴] %s\n" % (e,))
        _MT5 = None
    return _MT5


def _live_df_tick(n):
    """保持接続から M5(UTC index) と tick。失敗したら接続を破棄して例外。"""
    global _MT5
    import mt5_bridge
    mt5 = _get_mt5()
    if mt5 is None:
        raise RuntimeError("no MT5")
    try:
        df = mt5_bridge.m5_bars(mt5, n)
        tick = mt5_bridge.live_tick(mt5)
    except Exception:
        try:
            mt5.shutdown()
        except Exception:
            pass
        _MT5 = None
        raise
    df = df.set_index("dt")
    return df[["open", "high", "low", "close"]], tick


def build_data(n=1500):
    """チャート用データ一式（bars/tick/walls/source）。live優先→hist フォールバック。"""
    tick = None
    source = "live"
    try:
        m5, tick = _live_df_tick(n)
        if len(m5) == 0:
            raise RuntimeError("live 0本")
    except Exception:
        source = "hist"
        m5 = chart_gen.latest_m5(n)

    import pandas as pd
    o = m5["open"].to_numpy(); h = m5["high"].to_numpy()
    l = m5["low"].to_numpy();  c = m5["close"].to_numpy()
    idx = m5.index
    bars = [{"time": int(pd.Timestamp(idx[k]).timestamp()),
             "open": round(float(o[k]), 3), "high": round(float(h[k]), 3),
             "low": round(float(l[k]), 3), "close": round(float(c[k]), 3)}
            for k in range(len(m5))]
    box = chart_gen.current_box(m5)
    brk = chart_gen.detect_last_break(m5)
    return {
        "symbol": "XAUUSD (金) M5",
        "source": source,
        "ts": int(time.time()),
        "tick": tick,
        "bars": bars,
        "box": {k: round(v, 3) for k, v in box.items()},
        "break": ({k: (round(v, 3) if isinstance(v, float) else v)
                   for k, v in brk.items()} if brk else None),
        "range_w": chart_gen.RANGE_W,
    }


class H(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            p = self.path.split("?")[0]
            if p == "/" or p == "/index.html":
                with open(PAGE, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif p == "/lightweight-charts.js":
                with open(LIB, "rb") as f:
                    self._send(200, f.read(), "application/javascript; charset=utf-8")
            elif p == "/api/data":
                from urllib.parse import urlparse, parse_qs
                q = parse_qs(urlparse(self.path).query)
                n = int((q.get("n") or ["1500"])[0])
                n = max(50, min(5000, n))
                data = build_data(n)
                self._send(200, json.dumps(data, ensure_ascii=False), "application/json; charset=utf-8")
            else:
                self._send(404, "not found", "text/plain; charset=utf-8")
        except Exception as e:
            self._send(500, "err: %s" % e, "text/plain; charset=utf-8")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    # allow_reuse_address は Windows では同一ポート二重バインドを許してしまい配信が不安定に
    # なるため使わない（二重起動時は2つ目が明確に失敗して気づける）。
    with socketserver.TCPServer((HOST, PORT), H) as srv:
        print("壁→壁 ライブチャート on http://%s:%d/ (API: /api/data?n=1500)" % (HOST, PORT))
        srv.serve_forever()
