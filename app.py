#!/usr/bin/env python3
"""Edge Simulator — server. Local: python3 app.py → http://localhost:8765 | Prod: gunicorn wsgi:application"""
import http.server, socketserver, pathlib, sys, os, threading, webbrowser

PORT = int(os.environ.get("PORT", "8765"))
HOST = os.environ.get("HOST", "0.0.0.0")
ROOT = pathlib.Path(__file__).parent.resolve()
IS_PROD = bool(os.environ.get("RENDER") or os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("VERCEL") or os.environ.get("PORT") and os.environ.get("PORT") != "8765")

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(ROOT), **kw)
    def end_headers(self):
        self.send_header("Cache-Control","no-store")
        # allow embedding check
        self.send_header("X-Content-Type-Options","nosniff")
        super().end_headers()
    def log_message(self, fmt, *a):
        sys.stderr.write(f"  {fmt % a}\n")

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), H) as httpd:
        url = f"http://localhost:{PORT}" if HOST == "0.0.0.0" else f"http://{HOST}:{PORT}"
        print(f"\n  EDGE SIMULATOR  →  {url}")
        print(f"  Serving {ROOT}  (prod={IS_PROD})")
        print(f"  Ctrl+C to stop\n")
        # only auto-open browser locally, not on hosting
        if not IS_PROD:
            try: threading.Timer(0.6, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
            except: pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  bye — bet small, edge big")

# Vercel: expose top-level app/application/handler (re-export wsgi)
try:
    from wsgi import application as app  # noqa: F401
    application = handler = app
except Exception:
    app = application = handler = None  # type: ignore[no-redef]
