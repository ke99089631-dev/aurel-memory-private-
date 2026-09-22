# -*- coding: utf-8 -*-
"""
壁→壁 コックピット: 静的チャートを Tailscale:8793 で配る独立サーバ。
  既存のチャット室サーバ(8792)には一切触れない（別プロセス・別ポート）。
  GET /           → chart.html（無ければ生成）
  GET /r          → 再生成してから chart.html を返す（携帯から最新化ボタン用）
  ※読取のみ・発注なし・金は動かない。Tailscale IP のみにバインド。
"""
import os
import http.server
import socketserver

HOST = "100.73.107.61"     # Tailscale IP のみ（Wi-Fi/インターネットには出さない）
PORT = 8793
HERE = os.path.dirname(os.path.abspath(__file__))
CHART = os.path.join(HERE, "chart.html")


def regen():
    import chart_gen
    payload = chart_gen.build_payload(240)
    html = (chart_gen.HTML
            .replace("__SYMBOL__", payload["symbol"])
            .replace("__GENERATED__", payload["generated"])
            .replace("__DATA_END__", payload["data_end"])
            .replace("__PAYLOAD__", __import__("json").dumps(payload, ensure_ascii=False)))
    with open(CHART, "w", encoding="utf-8") as f:
        f.write(html)


class H(http.server.BaseHTTPRequestHandler):
    def _send_chart(self):
        if not os.path.exists(CHART):
            regen()
        with open(CHART, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            if self.path.startswith("/r"):
                regen()
            self._send_chart()
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(("生成エラー: %s" % e).encode("utf-8"))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), H) as srv:
        print("壁→壁 静的チャート on http://%s:%d/ (最新化は /r)" % (HOST, PORT))
        srv.serve_forever()
