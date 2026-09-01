"""Static server + control channel for the live player.

Serves the repo root (player + runs) and accepts POST /control with
{"run": "runs/...", "dive_to": "<node id>"} — written to
<run>/control.json for the engine to pick up.

Usage: uv run python scripts/serve.py [port]
"""

from __future__ import annotations

import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ALLOWED_PREFIXES = ("/web/", "/runs/")


class Handler(SimpleHTTPRequestHandler):
    # Serve only the player and run artifacts — never .git or the rest
    # of the working tree.
    def send_head(self):
        if not self.path.startswith(ALLOWED_PREFIXES):
            self.send_error(404)
            return None
        return super().send_head()

    def do_POST(self):
        if self.path != "/control":
            self.send_error(404)
            return
        try:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            run_dir = Path(body["run"]).resolve()
            if not run_dir.is_relative_to(Path.cwd()) or not run_dir.is_dir():
                raise ValueError("bad run dir")
            tmp = run_dir / "control.json.tmp"
            tmp.write_text(json.dumps({"dive_to": str(body["dive_to"])}))
            tmp.replace(run_dir / "control.json")  # atomic: engine never reads a torn file
            self.send_response(204)
            self.end_headers()
        except Exception as exc:
            self.send_error(400, str(exc))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8642
    print(f"serving on http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
