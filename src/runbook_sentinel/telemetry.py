from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TraceWriter:
    def __init__(self, path: str | Path | None):
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, name: str, attributes: dict) -> dict:
        event = {
            "trace_id": uuid4().hex,
            "timestamp": utc_now(),
            "name": name,
            "attributes": attributes,
        }
        if self.path:
            with self._lock, self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        return event
