"""Koyebヘルスチェック用HTTPサーバー"""
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from config import PORT


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        pass  # ログを抑制


def start_health_server():
    """ヘルスチェックサーバーをバックグラウンドで起動"""
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
