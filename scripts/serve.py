"""Serve editable Home sources and proxy the two loopback application backends."""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

HOME_ROOT = Path(__file__).resolve().parents[1]
WORDTXT_DIST = (HOME_ROOT.parent / "Plugin-WordTxT/frontend/dist").resolve()
HOME_FILES = {"/", "/index.html", "/style.css", "/app.js"}
PROXY_HEADERS = {"content-type", "cookie"}
HOP_BY_HOP_HEADERS = {"transfer-encoding", "connection", "server", "date"}


class WorkspaceHandler(SimpleHTTPRequestHandler):
    """Only expose the intended static files, never the repository directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HOME_ROOT), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path

        if path == "/apps.json":
            self.send_local_catalog()
        elif path in {"/leave", "/wordtxt"}:
            self.send_response(308)
            self.send_header("Location", path + "/")
            self.end_headers()
        elif path.startswith("/leave/"):
            self.proxy_request("http://127.0.0.1:8001/", self.path[len("/leave/"):])
        elif path.startswith("/wordtxt/"):
            self.send_wordtxt_file(path)
        elif path.startswith("/api/"):
            self.proxy_request("http://127.0.0.1:8000", self.path)
        elif path in HOME_FILES:
            super().do_GET()
        else:
            self.send_error(404)

    def do_HEAD(self):
        # Do not inherit directory listing or access to non-public repository files.
        path = urlsplit(self.path).path
        if path in HOME_FILES:
            super().do_HEAD()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/leave/"):
            self.proxy_request("http://127.0.0.1:8001/", self.path[len("/leave/"):])
        elif self.path.startswith("/api/"):
            self.proxy_request("http://127.0.0.1:8000", self.path)
        else:
            self.send_error(404)

    def send_local_catalog(self):
        applications = json.loads((HOME_ROOT / "apps.json").read_text())
        for application in applications:
            if application["id"] == "leave":
                application.update(tag="本地演示")
            elif application["id"] == "wordtxt":
                application.update(tag="原项目 · 本地预览")

        content = json.dumps(applications, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def send_wordtxt_file(self, path):
        relative_path = unquote(path[len("/wordtxt/"):]) or "index.html"
        target = (WORDTXT_DIST / relative_path).resolve()
        if not target.is_relative_to(WORDTXT_DIST) or not target.is_file():
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(str(target)))
        self.end_headers()
        self.wfile.write(target.read_bytes())

    def proxy_request(self, backend, path):
        body = None
        if self.command == "POST":
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))

        headers = {
            name: value
            for name, value in self.headers.items()
            if name.lower() in PROXY_HEADERS
        }
        request = Request(backend + path, data=body, headers=headers, method=self.command)

        try:
            response = urlopen(request, timeout=90)
        except HTTPError as error:
            # Forward expected application errors (401, 403, 422, etc.) to the UI.
            response = error
        except URLError:
            self.send_error(502, "Start the corresponding backend on port 8000 or 8001 first")
            return

        with response:
            self.send_response(response.status)
            for name, value in response.headers.items():
                if name.lower() not in HOP_BY_HOP_HEADERS:
                    self.send_header(name, value)
            self.end_headers()
            self.wfile.write(response.read())


if __name__ == "__main__":
    print("路上工作室: http://127.0.0.1:8080/")
    ThreadingHTTPServer(("127.0.0.1", 8080), WorkspaceHandler).serve_forever()
