# intercept.py

from mitmproxy import http, ctx
import os
from urllib.parse import urlparse

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
    # Check if the flow matches the scope
    if not in_scope(flow.request.host):
        return

    # Build directory path based on domain and URL path
    dir_path = build_directory_path(flow.request)
    os.makedirs(dir_path, exist_ok=True)

    # File path for the request
    method = flow.request.method
    path = os.path.join(dir_path, f"{method}_request.txt")

    # Write request data
    with open(path, "w", encoding='utf-8') as f:
        f.write(f"{flow.request.method} {flow.request.path} HTTP/{flow.request.http_version}\n")
        for name, value in flow.request.headers.items():
            f.write(f"{name}: {value}\n")
        f.write("\n")
        if flow.request.content:
            f.write(flow.request.get_text())

def response(flow: http.HTTPFlow) -> None:
    # Check if the flow matches the scope
    if not in_scope(flow.request.host):
        return

    # Build directory path based on domain and URL path
    dir_path = build_directory_path(flow.request)
    os.makedirs(dir_path, exist_ok=True)

    # File path for the response
    method = flow.request.method
    path = os.path.join(dir_path, f"{method}_response.txt")

    # Write response data
    with open(path, "w", encoding='utf-8') as f:
        f.write(f"HTTP/{flow.response.http_version} {flow.response.status_code} {flow.response.reason}\n")
        for name, value in flow.response.headers.items():
            f.write(f"{name}: {value}\n")
        f.write("\n")
        if flow.response.content:
            f.write(flow.response.get_text())

def build_directory_path(request):
    # Parse the URL
    parsed = urlparse(request.url)

    # Get hostname and path
    hostname = parsed.hostname or "unknown_host"
    path = parsed.path or "/"

    # Remove 'www.' prefix for cleaner directory names
    if hostname.startswith('www.'):
        hostname = hostname[4:]

    # Split path into segments, ignoring empty segments
    path_segments = [segment for segment in path.strip("/").split("/") if segment]

    # Build directory path
    dir_path = os.path.join(BASE_DIR, hostname, *path_segments)

    return dir_path

def in_scope(host):
    scope = ctx.options.scope
    if scope:
        # Check if the host contains the scope string
        return scope in host
    else:
        # No scope specified, process all hosts
        return True
