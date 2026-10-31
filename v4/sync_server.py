#!/usr/bin/env python3
"""Private JSON sync endpoint for T-AppMeteo V3 (Python standard library only)."""
from __future__ import annotations

import hmac
import html
import json
import os
import re
import tempfile
import threading
from datetime import datetime, timezone
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

TOKEN = os.environ.get("TAPPMETEO_SYNC_TOKEN", "")
STATE_PATH = Path(os.environ.get("TAPPMETEO_SYNC_FILE", "./t-appmeteo-sync.json")).resolve()
HOST = os.environ.get("TAPPMETEO_SYNC_HOST", "127.0.0.1")
PORT = int(os.environ.get("TAPPMETEO_SYNC_PORT", "8765"))
MAX_BODY = 64 * 1024 * 1024
STATE_LOCK = threading.Lock()
YVBEACH_URL = "https://www.yvbeach.com/yvmeteo.htm"
MAX_YVBEACH_BYTES = 1_000_000


def load_state() -> dict:
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if isinstance(state, dict):
            result = {key: state.get(key, []) for key in ("trips", "baits", "gear", "photos")}
            result["customOptions"] = state.get("customOptions", {}) if isinstance(state.get("customOptions", {}), dict) else {}
            return result
    except (OSError, json.JSONDecodeError):
        pass
    return {**{key: [] for key in ("trips", "baits", "gear", "photos")}, "customOptions": {}}


def merge_custom_options(old: dict, incoming: dict) -> dict:
    """Merge user-created dropdown labels without accepting non-string values."""
    merged: dict[str, list[str]] = {}
    for source in (old, incoming):
        if not isinstance(source, dict):
            continue
        for name, values in source.items():
            if not isinstance(name, str) or not isinstance(values, list):
                continue
            target = merged.setdefault(name, [])
            known = {value.casefold() for value in target}
            for value in values:
                if isinstance(value, str) and value.strip() and value.strip().casefold() not in known:
                    clean = value.strip()[:100]
                    target.append(clean)
                    known.add(clean.casefold())
    return merged


def saved_at(row: dict) -> str:
    return str(row.get("updatedAt") or row.get("date") or "1970-01-01T00:00:00Z")


def merge_rows(old: list, incoming: list) -> list:
    merged: dict[str, dict] = {}
    for row in [*old, *incoming]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        previous = merged.get(row["id"])
        if previous is None or saved_at(row) >= saved_at(previous):
            merged[row["id"]] = row
    return list(merged.values())


def persist(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="t-appmeteo-", suffix=".tmp", dir=STATE_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, STATE_PATH)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


class PlainTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def parse_yvbeach(html_text: str) -> dict:
    parser = PlainTextParser()
    parser.feed(html_text)
    text = re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts)))

    def match(pattern: str, group: int = 1):
        found = re.search(pattern, text, re.IGNORECASE)
        return found.group(group).replace(",", ".").strip() if found else None

    report = match(r"RELEVE\s+DU\s+(\d{2}/\d{2}/\d{4})\s+A\s+(\d{1,2}h\d{2})", 0)
    if not report:
        raise ValueError("YvBeach n’a pas fourni de date et heure de mesure reconnues.")
    stamp_match = re.search(r"RELEVE\s+DU\s+(\d{2}/\d{2}/\d{4})\s+A\s+(\d{1,2})h(\d{2})", text, re.IGNORECASE)
    measured_at = datetime.strptime(
        f"{stamp_match.group(1)} {stamp_match.group(2)}:{stamp_match.group(3)}", "%d/%m/%Y %H:%M"
    ).replace(tzinfo=ZoneInfo("Europe/Zurich"))
    result = {
        "source": "YvBeach · station d’Yvonand",
        "sourceUrl": YVBEACH_URL,
        "measuredAt": measured_at.isoformat(),
        "pressureMb": match(r"PRESSION\s*:\s*([+-]?\d+(?:[.,]\d+)?)\s*mb"),
        "pressureTrendMbH": match(r"PRESSION\s*:\s*[+-]?\d+(?:[.,]\d+)?\s*mb\s*([+-]?\d+(?:[.,]\d+)?)\s*mb/h"),
        "gustKmh": match(r"RAFALE\s+max/1h\s*:\s*([\d.,]+)\s*km/h"),
        "windKmh": match(r"VENT\s+moy/10min\s*:\s*([\d.,]+)\s*km/h"),
        "direction": match(r"DIRECTION\s+moy/10min\s*:\s*([A-Z]+)"),
        "directionDegrees": match(r"DIRECTION\s+moy/10min\s*:\s*[A-Z]+\s*-\s*(\d{1,3})\s*[°º]"),
        "airTemperatureC": match(r"TEMPERATURE\s*:\s*([+-]?[\d.,]+)\s*[°º]C"),
        "airTrendCPerH": match(r"TEMPERATURE\s*:\s*[+-]?[\d.,]+\s*[°º]C\s*([+-]?[\d.,]+)\s*[°º]C/h"),
        "lakeTemperatureC": match(r"TEMP\s+DU\s+LAC\s*:\s*([+-]?[\d.,]+)\s*[°º]C"),
        "humidityPercent": match(r"HUMIDITE\s*:\s*([\d.,]+)\s*%"),
        "dewPointC": match(r"POINT\s+DE\s+ROSEE\s*:\s*([+-]?[\d.,]+)\s*[°º]C"),
        "rainMm": match(r"PLUIE\s+DU\s+JOUR\s*:\s*([\d.,]+)\s*mm"),
    }
    if not result["pressureMb"] or not result["airTemperatureC"]:
        raise ValueError("Le format du relevé YvBeach a changé ou les mesures sont incomplètes.")
    return result


class SyncHandler(BaseHTTPRequestHandler):
    server_version = "T-AppMeteoSync/1.0"

    def log_message(self, fmt: str, *args) -> None:
        # Do not write auth headers or photo data into standard logs.
        super().log_message(fmt, *args)

    def send_json(self, status: int, payload: dict) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self) -> None:
        if urlparse(self.path).path != "/api/yvbeach":
            self.send_json(404, {"error": "not found"})
            return
        if not TOKEN:
            self.send_json(503, {"error": "TAPPMETEO_SYNC_TOKEN is not configured"})
            return
        supplied = self.headers.get("Authorization", "")
        if not hmac.compare_digest(supplied, f"Bearer {TOKEN}"):
            self.send_json(401, {"error": "unauthorized"})
            return
        try:
            request = Request(YVBEACH_URL, headers={"User-Agent": "T-AppMeteo-V4/1.0", "Accept": "text/html"})
            with urlopen(request, timeout=12) as response:
                raw = response.read(MAX_YVBEACH_BYTES + 1)
                charset = response.headers.get_content_charset() or "iso-8859-1"
            if len(raw) > MAX_YVBEACH_BYTES:
                raise ValueError("La page YvBeach dépasse la taille autorisée.")
            self.send_json(200, parse_yvbeach(raw.decode(charset, errors="replace")))
        except Exception as exc:
            self.send_json(502, {"error": str(exc)[:240] or "YvBeach est momentanément indisponible."})

    def do_PUT(self) -> None:
        if urlparse(self.path).path != "/api/sync":
            self.send_json(404, {"error": "not found"})
            return
        if not TOKEN:
            self.send_json(503, {"error": "TAPPMETEO_SYNC_TOKEN is not configured"})
            return
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {TOKEN}"
        if not hmac.compare_digest(supplied, expected):
            self.send_json(401, {"error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 2 or length > MAX_BODY:
                self.send_json(413, {"error": "payload size is outside the allowed range"})
                return
            incoming = json.loads(self.rfile.read(length))
            if not isinstance(incoming, dict):
                raise ValueError("JSON object expected")
            with STATE_LOCK:
                state = load_state()
                for key in ("trips", "baits", "gear", "photos"):
                    rows = incoming.get(key, [])
                    if not isinstance(rows, list):
                        raise ValueError(f"{key} must be an array")
                    state[key] = merge_rows(state[key], rows)
                options = incoming.get("customOptions", {})
                if not isinstance(options, dict):
                    raise ValueError("customOptions must be an object")
                state["customOptions"] = merge_custom_options(state.get("customOptions", {}), options)
                active_trips = {row["id"] for row in state["trips"] if not row.get("deletedAt")}
                active_baits = {row.get("photoId") for row in state["baits"] if not row.get("deletedAt") and row.get("photoId")}
                state["photos"] = [photo for photo in state["photos"] if photo.get("id") in active_baits or photo.get("tripId") in active_trips]
                state["updatedAt"] = datetime.now(timezone.utc).isoformat()
                persist(state)
            self.send_json(200, state)
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            self.send_json(400, {"error": str(exc)[:240]})


if __name__ == "__main__":
    if not TOKEN or len(TOKEN) < 24:
        raise SystemExit("Configure TAPPMETEO_SYNC_TOKEN avec au moins 24 caractères aléatoires.")
    print(f"T-AppMeteo sync listening on {HOST}:{PORT}; state file: {STATE_PATH}")
    ThreadingHTTPServer((HOST, PORT), SyncHandler).serve_forever()
