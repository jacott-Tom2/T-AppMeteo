#!/usr/bin/env python3
"""Private JSON sync endpoint for T-AppMeteo V3 (Python standard library only)."""
from __future__ import annotations

import hmac
import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

TOKEN = os.environ.get("TAPPMETEO_SYNC_TOKEN", "")
STATE_PATH = Path(os.environ.get("TAPPMETEO_SYNC_FILE", "./t-appmeteo-sync.json")).resolve()
HOST = os.environ.get("TAPPMETEO_SYNC_HOST", "127.0.0.1")
PORT = int(os.environ.get("TAPPMETEO_SYNC_PORT", "8765"))
MAX_BODY = 64 * 1024 * 1024
STATE_LOCK = threading.Lock()


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
        self.send_header("Access-Control-Allow-Methods", "PUT, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "PUT, OPTIONS")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

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
