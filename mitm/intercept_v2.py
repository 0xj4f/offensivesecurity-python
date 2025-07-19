# intercept_v5.py

from mitmproxy import http, ctx
from urllib.parse import urlparse
import os
import hashlib
import datetime

# Base directory to store requests and responses
BASE_DIR = "captured_data"

def load(loader):
    # Add a command-line option for scope
    loader.add_option(
        name="scope",
        typespec=str,
        default="",
        help="Domain scope for interception"
    )

def request(flow: http.HTTPFlow) -> None:
    if not in_scope(flow.request.host):
        return

    dir_path = build_directory_path(flow.request)
    os.makedirs(dir_path, exist_ok=True)

    method = flow.request.method
    suffix = unique_suffix(flow.request)
    path = os.path.join(dir_path, f"{method}-{suffix}-request.txt")

    with open(path, "w", encoding='utf-8') as f:
        f.write(f"{flow.request.method} {flow.request.path} HTTP/{flow.request.http_version}\n")
        for name, value in flow.request.headers.items():
            f.write(f"{name}: {value}\n")
        f.write("\n")
        if flow.request.content:
            f.write(flow.request.get_text())

def response(flow: http.HTTPFlow) -> None:
    if not in_scope(flow.request.host):
        return

    dir_path = build_directory_path(flow.request)
    os.makedirs(dir_path, exist_ok=True)

    method = flow.request.method
    suffix = unique_suffix(flow.request)
    path = os.path.join(dir_path, f"{method}-{suffix}-response.txt")

    with open(path, "w", encoding='utf-8') as f:
        f.write(f"HTTP/{flow.response.http_version} {flow.response.status_code} {flow.response.reason}\n")
        for name, value in flow.response.headers.items():
            f.write(f"{name}: {value}\n")
        f.write("\n")
        if flow.response.content:
            try:
                flow.response.decode(strict=False)
                f.write(flow.response.get_text(strict=False))
            except Exception as e:
                ctx.log.warn(f"Could not decode response for {flow.request.url}: {e}")

def build_directory_path(request):
    parsed = urlparse(request.url)
    hostname = parsed.hostname or "unknown_host"
    path = parsed.path or "/"

    if hostname.startswith('www.'):
        hostname = hostname[4:]

    path_segments = [segment for segment in path.strip("/").split("/") if segment]
    dir_path = os.path.join(BASE_DIR, hostname, *path_segments)

    return dir_path

def in_scope(host):
    scope = ctx.options.scope
    if scope:
        return scope in host
    else:
        return True

def unique_suffix(request):
    h = hashlib.sha1(request.url.encode()).hexdigest()[:8]
    t = datetime.datetime.utcnow().strftime("%H%M%S")
    return f"{t}-{h}"
