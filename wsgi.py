"""WSGI entry for hosting (Render/Railway/Fly.io): gunicorn wsgi:application"""
import pathlib

ROOT = pathlib.Path(__file__).parent.resolve()

# Serve static files via WhiteNoise (no Flask needed) — falls back to wsgiref if not installed
try:
    from whitenoise import WhiteNoise
    from wsgiref.simple_server import demo_app

    # WhiteNoise wraps a dummy app and serves files from ROOT
    # Requests for / → index.html, /anything → file in ROOT
    def _app(environ, start_response):
        from wsgiref.util import request_uri
        path = environ.get("PATH_INFO", "/") or "/"
        if path == "/":
            path = "/index.html"
        # let WhiteNoise handle it
        environ["PATH_INFO"] = path
        return demo_app(environ, start_response)

    application = WhiteNoise(_app, root=str(ROOT), index_file=True)
    # also serve at / explicitly
    application.add_files(str(ROOT))

except ImportError:
    # fallback: stdlib only — gunicorn can still run this
    import mimetypes, os

    def application(environ, start_response):
        path = environ.get("PATH_INFO", "/") or "/"
        if path == "/":
            path = "/index.html"
        # prevent directory traversal
        safe = os.path.normpath(path).lstrip("/")
        full = ROOT / safe
        if not str(full).startswith(str(ROOT)):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Forbidden"]
        if not full.exists() or full.is_dir():
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Not Found"]
        ctype, _ = mimetypes.guess_type(str(full))
        ctype = ctype or "application/octet-stream"
        data = full.read_bytes()
        start_response("200 OK", [("Content-Type", ctype), ("Content-Length", str(len(data))), ("Cache-Control", "no-store")])
        return [data]

# Vercel: unconditional top-level aliases (detected via static analysis)
app = application
handler = application
