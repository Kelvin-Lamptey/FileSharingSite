#!/usr/bin/env python3
"""Simple file listing + download webserver.

Serves contents of the sibling `files/` directory and prints local + network addresses.
"""
from __future__ import annotations

import argparse
import os
import socket
from pathlib import Path
from typing import List

from flask import Flask, abort, render_template, send_from_directory, url_for


def get_default_ip() -> str:
    """Return one non-loopback IP (best-effort) or 127.0.0.1."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't need to be reachable, just used to pick the outbound interface
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


app = Flask(__name__, template_folder="templates")


@app.template_filter('human_size')
def human_size_filter(value):
    try:
        v = int(value)
    except Exception:
        return ""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if v < 1024:
            return f"{v:.0f} {unit}" if unit == 'B' else f"{v:.1f} {unit}"
        v = v / 1024
    return f"{v:.1f} PB"


# Will be set in __main__ after parsing args
FILES_DIR: Path = Path("files").resolve()
PORT = 8000


def safe_join(base: Path, *parts: str) -> Path:
    """Resolve and ensure path is inside base directory."""
    candidate = (base.joinpath(*parts)).resolve()
    if not str(candidate).startswith(str(base.resolve())):
        raise ValueError("outside of base directory")
    return candidate


@app.route("/download/<path:filename>")
def download(filename: str):
    try:
        # send_from_directory will do safe handling for relative paths
        return send_from_directory(str(FILES_DIR), filename, as_attachment=True)
    except Exception:
        abort(404)


@app.route("/", defaults={"req_path": ""})
@app.route("/<path:req_path>")
def index(req_path: str):
    try:
        target = safe_join(FILES_DIR, req_path)
    except ValueError:
        abort(404)

    if target.is_file():
        # If a file path is requested, send it as download
        rel = os.path.relpath(target, FILES_DIR)
        return send_from_directory(str(FILES_DIR), rel, as_attachment=True)

    # list directory entries
    entries: List[dict] = []
    try:
        for name in sorted(os.listdir(target)):
            p = target / name
            is_file = p.is_file()
            size = p.stat().st_size if p.exists() and is_file else None
            if is_file:
                url = url_for("download", filename=os.path.relpath(p, FILES_DIR))
            else:
                url = url_for("index", req_path=os.path.relpath(p, FILES_DIR))
            entries.append({"name": name, "is_file": is_file, "size": size, "url": url})
    except FileNotFoundError:
        abort(404)

    local_addr = f"http://127.0.0.1:{PORT}"
    network_addr = f"http://{get_default_ip()}:{PORT}"

    return render_template("index.html", entries=entries, req_path=req_path, local_addr=local_addr, network_addr=network_addr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple file listing + download server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--dir", "-d", default="files", help="Directory to serve")
    args = parser.parse_args()

    PORT = args.port
    FILES_DIR = Path(args.dir).resolve()
    if not FILES_DIR.exists():
        print(f"Warning: serving directory does not exist: {FILES_DIR}")

    print("Serving files from:", FILES_DIR)
    print(f"Local:    http://127.0.0.1:{PORT}")
    print(f"Network:  http://{get_default_ip()}:{PORT}")

    # bind to 0.0.0.0 so network devices can reach it
    app.run(host="0.0.0.0", port=PORT, threaded=True)
