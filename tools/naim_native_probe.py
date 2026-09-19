"""Read-only Naim interface reconnaissance; Python 3.9+, no dependencies.

This does NOT establish native TIDAL playback. It only inventories candidate
interfaces. It never issues playback, input-selection, volume or login commands.
"""
import argparse
import datetime
import ipaddress
import json
import pathlib
import re
import urllib.error
import urllib.request

MAX_BYTES = 1024 * 1024
PATHS = ("/", "/system", "/inputs", "/nowplaying", "/levels/room", "/favourites")
SAFE_FIELDS = {
    "model", "appVer", "version", "class", "type", "name", "title",
    "artist", "artistName", "album", "albumName", "available", "disabled",
    "transportState", "transportPosition", "duration", "codec", "sampleRate",
    "bitDepth", "bitRate", "repeat", "shuffle", "volume", "mute",
}
SENSITIVE = re.compile(r"token|secret|password|credential|session|authorization|cookie|account|email|serial", re.I)


def safe_view(value, key="", depth=0):
    """Default-deny scalar values; retain useful structure and known metadata."""
    if SENSITIVE.search(key):
        return "[omitted]"
    if depth > 7:
        return "[depth limit]"
    if isinstance(value, dict):
        result = {}
        for k, v in list(value.items())[:80]:
            # Some APIs use URLs or opaque identifiers as dictionary keys.
            label = k if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", k) else "[opaque key]"
            result[label] = safe_view(v, k, depth + 1)
        return result
    if isinstance(value, list):
        return {"count": len(value), "sample": [safe_view(v, key, depth + 1) for v in value[:12]]}
    if key in ("ussi", "source") and isinstance(value, str):
        if re.fullmatch(r"/?(?:inputs|favourites)(?:/[A-Za-z0-9_-]+)*", value):
            return value
        return "[reference omitted]"
    if key in SAFE_FIELDS and isinstance(value, (str, int, float, bool, type(None))):
        if isinstance(value, str):
            if "://" in value or "?" in value:
                return "[URL or query omitted]"
            return value[:200]
        return value
    return "[" + type(value).__name__ + "]"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_endpoint(opener, base, path, timeout):
    allowed = {p for prefix in ("", "/naim") for p in (prefix + x for x in PATHS)}
    allowed |= {prefix + "/inputs/" + item for prefix in ("", "/naim") for item in ("tidal", "playqueue")}
    if path not in allowed:
        raise ValueError("Endpoint is not in the read-only allowlist")
    request = urllib.request.Request(base + path, headers={"Accept": "application/json"}, method="GET")
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                return {"path": path, "result": "response too large"}, None
            try:
                data = json.loads(raw)
            except (ValueError, UnicodeError):
                return {"path": path, "status": response.status, "result": "non-JSON; body omitted"}, None
            return {"path": path, "status": response.status, "structure": safe_view(data)}, data
    except urllib.error.HTTPError as exc:
        return {"path": path, "status": exc.code, "result": "HTTP error; body omitted"}, None
    except (urllib.error.URLError, TimeoutError, OSError):
        return {"path": path, "result": "connection failed or timed out"}, None


def advertised_inputs(data):
    found = set()
    def visit(item):
        if isinstance(item, dict):
            ussi = str(item.get("ussi", "")).strip("/")
            if ussi in ("inputs/tidal", "inputs/playqueue"):
                found.add(ussi)
            for value in item.values():
                visit(value)
        elif isinstance(item, list):
            for value in item:
                visit(value)
    visit(data)
    return sorted(found)


def collect(address, timeout=4):
    ip = ipaddress.IPv4Address(address)
    private_ranges = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
    if not any(ip in ipaddress.IPv4Network(net) for net in private_ranges):
        raise ValueError("Use the streamer's private LAN IPv4 address")
    opener = urllib.request.build_opener(NoRedirect())
    base = "http://" + str(ip) + ":15081"
    report = {
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "purpose": "Read-only interface inventory. Native TIDAL feasibility remains UNPROVEN.",
        "device_address": "omitted",
        "requests": [],
    }
    prefix = ""
    root, _ = read_endpoint(opener, base, "/", timeout)
    report["requests"].append(root)
    if root.get("result") == "connection failed or timed out":
        return report
    system, data = read_endpoint(opener, base, "/system", timeout)
    report["requests"].append(system)
    if not isinstance(data, dict):
        alternate, data = read_endpoint(opener, base, "/naim/system", timeout)
        report["requests"].append(alternate)
        if not isinstance(data, dict):
            return report
        prefix = "/naim"
    inputs = None
    for path in PATHS[2:]:
        entry, data = read_endpoint(opener, base, prefix + path, timeout)
        report["requests"].append(entry)
        if path == "/inputs":
            inputs = data
    # Only query these native input descriptions when the device advertises them.
    for item in advertised_inputs(inputs):
        entry, _ = read_endpoint(opener, base, prefix + "/" + item, timeout)
        report["requests"].append(entry)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("address", help="NDX 2 private IPv4 address")
    parser.add_argument("--output", default="naim-interface-report.json")
    args = parser.parse_args()
    try:
        report = collect(args.address)
    except ValueError as exc:
        parser.error(str(exc))
    output = pathlib.Path(args.output)
    # Do not overwrite an earlier snapshot.
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
    print("Saved read-only inventory to", output)
    print("Native TIDAL playback has NOT been tested or established.")


if __name__ == "__main__":
    main()
