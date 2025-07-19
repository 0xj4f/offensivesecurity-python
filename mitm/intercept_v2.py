# intercept_v2.py
from mitmproxy import http, ctx
from urllib.parse import urlparse, quote
import hashlib, os, datetime

BASE_DIR = "captured_data"

def load(loader):
    loader.add_option("scope", str, "", "Domain scope for interception")

# ---------- Helpers ----------
def safe_filename(s: str, max_len=60) -> str:
    """Return a filesystem-safe chunk."""
    safe = quote(s, safe='')            # url-encode weird chars
    return safe[:max_len]

def uniq_suffix(flow: http.HTTPFlow) -> str:
    """Stable short hash to avoid overwrites."""
    h = hashlib.sha1(flow.request.url.encode()).hexdigest()[:8]
    t = datetime.datetime.utcnow().strftime("%H%M%S")
    return f"{t}_{h}"

def build_dir(flow: http.HTTPFlow) -> str:
    p = urlparse(flow.request.url)
    host = p.hostname.lstrip("www.") if p.hostname else "unknown_host"
    segments = [safe_filename(seg) for seg in p.path.split("/") if seg]
    return os.path.join(BASE_DIR, host, *segments)

def in_scope(host: str) -> bool:
    scope = ctx.options.scope
    return (scope in host) if scope else True

def dump(flow: http.HTTPFlow, is_req: bool):
    if not in_scope(flow.request.host):
        return

    dir_path = build_dir(flow)
    os.makedirs(dir_path, exist_ok=True)

    tag = "request" if is_req else "response"
    fname = f"{flow.request.method}_{uniq_suffix(flow)}_{tag}.txt"
    fpath = os.path.join(dir_path, fname)

    try:
        with open(fpath, "wb") as f:
            if is_req:
                hdr = f"{flow.request.method} {flow.request.path}?{flow.request.query_string} HTTP/{flow.request.http_version}\n"
                hdr += "".join(f"{k}: {v}\n" for k, v in flow.request.headers.items())
                f.write(hdr.encode() + b"\n")
                f.write(flow.request.raw_content or b"")
            else:
                hdr = f"HTTP/{flow.response.http_version} {flow.response.status_code} {flow.response.reason}\n"
                hdr += "".join(f"{k}: {v}\n" for k, v in flow.response.headers.items())
                f.write(hdr.encode() + b"\n")
                f.write(flow.response.raw_content or b"")
        ctx.log.info(f"Saved {fpath}")
    except Exception as e:
        ctx.log.error(f"[!] Failed to save {fpath}: {e}")

# ---------- mitmproxy hooks ----------
def request(flow: http.HTTPFlow):
    dump(flow, is_req=True)

def response(flow: http.HTTPFlow):
    dump(flow, is_req=False)

