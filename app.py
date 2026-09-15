#!/usr/bin/env python3
"""Gamble Terminal — localhost server.  python3 app.py  →  http://localhost:8765"""
import http.server, socketserver, pathlib, sys, threading, webbrowser

PORT = 8765
ROOT = pathlib.Path(__file__).parent.resolve()

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(ROOT), **kw)
    def end_headers(self):
        self.send_header("Cache-Control","no-store")
        super().end_headers()
    def log_message(self, fmt, *a):
        sys.stderr.write(f"  {fmt % a}\n")

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), H) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n  GAMBLE TERMINAL  →  {url}")
        print(f"  Serving {ROOT}")
        print(f"  Ctrl+C to stop\n")
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  bye — bet small, edge big")
