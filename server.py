#!/usr/bin/env python3
"""Research library server with cookie-based auth, filtered manifest, and confidential access control."""

import hashlib
import hmac
import json
import mimetypes
import os
import tempfile
import threading
import time
from http import cookies
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE_DIR = Path(__file__).resolve().parent
MANIFEST = BASE_DIR / 'manifest.json'
AUTH_KEY = 'fermi2026'
HMAC_SECRET = 'research-lib-2026'
COOKIE_NAME = 'research_auth'
COOKIE_MAX_AGE = 86400  # 24h
manifest_lock = threading.Lock()


def make_auth_token(expiry: int) -> str:
    """Create HMAC token encoding expiry timestamp."""
    msg = str(expiry).encode()
    sig = hmac.new(HMAC_SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return f"{expiry}.{sig}"


def verify_auth_token(token: str) -> bool:
    """Verify HMAC token and check expiry."""
    try:
        expiry_str, sig = token.split('.', 1)
        expiry = int(expiry_str)
        expected = hmac.new(HMAC_SECRET.encode(), expiry_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        return time.time() < expiry
    except Exception:
        return False


def load_manifest():
    with open(MANIFEST, 'r') as f:
        return json.load(f)


def is_confidential(manifest_data, filename):
    for r in manifest_data.get('reports', []):
        if r.get('file') == filename:
            return r.get('confidential', False)
    return False


ACCESS_DENIED_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Access Denied</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: oklch(0.14 0.005 260);
    color: oklch(0.92 0 0);
    font-family: 'Manrope', sans-serif;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh;
  }
  .box { text-align: center; max-width: 380px; padding: 40px; }
  .icon { font-size: 3rem; margin-bottom: 20px; }
  h1 { font-size: 1.25rem; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.02em; }
  p { font-size: 0.875rem; color: oklch(0.55 0 0); margin-bottom: 28px;
      font-family: 'JetBrains Mono', monospace; }
  form { display: flex; flex-direction: column; gap: 12px; }
  input {
    width: 100%; padding: 12px 16px;
    background: oklch(0.18 0.005 260); border: 1px solid oklch(0.32 0.005 260);
    color: oklch(0.92 0 0); font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem; outline: none;
  }
  input:focus { border-color: oklch(0.72 0.12 192); }
  button {
    width: 100%; padding: 12px;
    background: oklch(0.72 0.12 192); color: oklch(0.12 0 0);
    border: none; font-family: 'JetBrains Mono', monospace;
    font-weight: 700; font-size: 0.8125rem; cursor: pointer;
    letter-spacing: 0.02em;
  }
  button:hover { background: oklch(0.80 0.12 192); }
  .back { margin-top: 20px; }
  .back a { color: oklch(0.55 0 0); font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; text-decoration: none; }
  .back a:hover { color: oklch(0.72 0.12 192); }
</style>
</head>
<body>
<div class="box">
  <div class="icon">🔒</div>
  <h1>This report is confidential</h1>
  <p>Authentication required to view this document.</p>
  <form id="authform" onsubmit="return doAuth()">
    <input type="password" id="pw" placeholder="Enter password" autofocus>
    <button type="submit">Authenticate</button>
  </form>
  <div class="back"><a href="/">← Back to library</a></div>
</div>
<script>
function doAuth() {
  var pw = document.getElementById('pw').value;
  window.location.href = window.location.pathname + '?key=' + encodeURIComponent(pw);
  return false;
}
</script>
</body>
</html>'''


class ResearchHandler(BaseHTTPRequestHandler):

    def _is_authenticated(self):
        """Check auth cookie."""
        cookie_header = self.headers.get('Cookie', '')
        c = cookies.SimpleCookie()
        try:
            c.load(cookie_header)
        except Exception:
            return False
        morsel = c.get(COOKIE_NAME)
        if morsel and verify_auth_token(morsel.value):
            return True
        return False

    def _check_key_param(self, query_params):
        """If ?key= matches, return a Set-Cookie header value, else None."""
        keys = query_params.get('key', [])
        if keys and keys[0] == AUTH_KEY:
            expiry = int(time.time()) + COOKIE_MAX_AGE
            token = make_auth_token(expiry)
            return f"{COOKIE_NAME}={token}; Path=/; Max-Age={COOKIE_MAX_AGE}; HttpOnly; SameSite=Lax"
        return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        query_params = parse_qs(parsed.query)

        # Check if ?key= param → set cookie and serve as authenticated
        set_cookie = self._check_key_param(query_params)
        if set_cookie:
            self._pending_set_cookie = set_cookie
            authed = True
        else:
            self._pending_set_cookie = None
            authed = self._is_authenticated()

        # Route: /
        if path in ('', '/'):
            self._serve_file('index.html')
            return

        # Route: /manifest.json
        if path == '/manifest.json':
            self._serve_filtered_manifest(authed)
            return

        # Route: /api/auth-check
        if path == '/api/auth-check':
            resp = {'authenticated': authed}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            if getattr(self, '_pending_set_cookie', None):
                self.send_header('Set-Cookie', self._pending_set_cookie)
            body = json.dumps(resp).encode()
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
            return

        # Route: /api/logout
        if path == '/api/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'research_auth=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax')
            self.send_header('Location', '/')
            self.end_headers()
            return

        # Strip leading /
        filepath = path.lstrip('/')

        # Route: /<report>.html — check confidential
        if filepath.endswith('.html'):
            full = BASE_DIR / filepath
            if not full.is_file():
                self.send_error(404)
                return
            if not authed:
                manifest_data = load_manifest()
                if is_confidential(manifest_data, filepath):
                    self._serve_403()
                    return
            self._serve_file(filepath)
            return

        # All other static files
        self._serve_file(filepath)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/toggle-confidential':
            self._handle_toggle()
        else:
            self.send_error(404)

    def _serve_filtered_manifest(self, authed):
        manifest_data = load_manifest()
        if not authed:
            manifest_data = dict(manifest_data)
            manifest_data['reports'] = [r for r in manifest_data.get('reports', []) if not r.get('confidential', False)]
        body = json.dumps(manifest_data, indent=2).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        if getattr(self, '_pending_set_cookie', None):
            self.send_header('Set-Cookie', self._pending_set_cookie)
        self.end_headers()
        self.wfile.write(body)

    def _serve_403(self):
        body = ACCESS_DENIED_HTML.encode()
        self.send_response(403)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, filepath):
        full = BASE_DIR / filepath
        if not full.is_file():
            self.send_error(404)
            return
        # Security: prevent path traversal
        try:
            full.resolve().relative_to(BASE_DIR.resolve())
        except ValueError:
            self.send_error(403)
            return
        content_type, _ = mimetypes.guess_type(str(full))
        if content_type is None:
            content_type = 'application/octet-stream'
        try:
            data = full.read_bytes()
        except Exception:
            self.send_error(500)
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(data))
        if getattr(self, '_pending_set_cookie', None):
            self.send_header('Set-Cookie', self._pending_set_cookie)
        self.end_headers()
        self.wfile.write(data)

    def _handle_toggle(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_error(400, 'Invalid JSON')
            return

        # Auth: accept cookie OR key in body
        if not self._is_authenticated() and body.get('key') != AUTH_KEY:
            self._json_response(403, {'error': 'Forbidden'})
            return

        target_file = body.get('file', '')

        with manifest_lock:
            data = load_manifest()
            report = None
            for r in data.get('reports', []):
                if r.get('file') == target_file:
                    report = r
                    break
            if not report:
                self._json_response(404, {'error': 'Report not found'})
                return
            new_val = not report.get('confidential', False)
            if new_val:
                report['confidential'] = True
            else:
                report.pop('confidential', None)
            # Atomic write
            fd, tmp = tempfile.mkstemp(dir=str(BASE_DIR), suffix='.json')
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump(data, f, indent=2)
                os.replace(tmp, str(MANIFEST))
            except Exception:
                os.unlink(tmp)
                raise

        self._json_response(200, {'ok': True, 'confidential': new_val})

    def _json_response(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # quiet


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True
    allow_reuse_port = True


if __name__ == '__main__':
    os.chdir(str(BASE_DIR))
    server = ReusableHTTPServer(('0.0.0.0', 8899), ResearchHandler)
    print('Research server on http://0.0.0.0:8899')
    server.serve_forever()
