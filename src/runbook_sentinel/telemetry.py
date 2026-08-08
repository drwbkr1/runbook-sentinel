from __future__ import annotations

import hashlib
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .errors import TraceIntegrityError


TRACE_SCHEMA = "trace-chain/v1"
GENESIS_PREVIOUS_EVENT_SHA256 = "0" * 64
TRACE_FIELDS = frozenset(
    {
        "schema",
        "sequence",
        "previous_event_sha256",
        "trace_id",
        "timestamp",
        "name",
        "attributes",
        "event_sha256",
    }
)
HASHED_TRACE_FIELDS = TRACE_FIELDS - {"event_sha256"}
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_ANCHOR_UNSET = object()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    """Serialize the exact trace hash input deterministically."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def build_trace_event(
    *,
    sequence: int,
    previous_event_sha256: str,
    trace_id: str,
    timestamp: str,
    name: str,
    attributes: dict,
) -> dict:
    """Build one canonical trace-chain/v1 event."""

    hashed_event = {
        "schema": TRACE_SCHEMA,
        "sequence": sequence,
        "previous_event_sha256": previous_event_sha256,
        "trace_id": trace_id,
        "timestamp": timestamp,
        "name": name,
        "attributes": attributes,
    }
    event_sha256 = hashlib.sha256(canonical_json(hashed_event).encode("utf-8")).hexdigest()
    return {**hashed_event, "event_sha256": event_sha256}


def _error(code: str, *, line: int | None = None, **details: Any) -> dict:
    error = {"code": code}
    if line is not None:
        error["line"] = line
    error.update(details)
    return error


def verify_trace_text(
    text: str,
    *,
    expected_event_count: int | object = _ANCHOR_UNSET,
    expected_final_event_sha256: str | None | object = _ANCHOR_UNSET,
) -> dict:
    """Verify a JSONL trace chain and, when supplied, its complete external anchor."""

    count_supplied = expected_event_count is not _ANCHOR_UNSET
    final_supplied = expected_final_event_sha256 is not _ANCHOR_UNSET
    anchored = count_supplied and final_supplied
    errors: list[dict] = []
    if count_supplied != final_supplied:
        errors.append(_error("incomplete_anchor"))

    records = [(line_number, line) for line_number, line in enumerate(text.splitlines(), 1) if line]
    event_count = len(records)
    expected_sequence = 1
    previous_event_sha256 = GENESIS_PREVIOUS_EVENT_SHA256
    final_event_sha256: str | None = None

    for line_number, line in records:
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(_error("invalid_json", line=line_number, detail=str(exc)))
            expected_sequence += 1
            continue

        if not isinstance(event, dict):
            errors.append(_error("event_not_object", line=line_number))
            expected_sequence += 1
            continue

        actual_fields = frozenset(event)
        if actual_fields != TRACE_FIELDS:
            errors.append(
                _error(
                    "top_level_fields_mismatch",
                    line=line_number,
                    missing=sorted(TRACE_FIELDS - actual_fields),
                    unexpected=sorted(actual_fields - TRACE_FIELDS),
                )
            )
        if event.get("schema") != TRACE_SCHEMA:
            errors.append(_error("schema_mismatch", line=line_number))

        sequence = event.get("sequence")
        if isinstance(sequence, bool) or not isinstance(sequence, int):
            errors.append(_error("sequence_not_integer", line=line_number))
        elif sequence != expected_sequence:
            errors.append(
                _error(
                    "sequence_mismatch",
                    line=line_number,
                    expected=expected_sequence,
                    actual=sequence,
                )
            )

        declared_previous = event.get("previous_event_sha256")
        if not isinstance(declared_previous, str) or not _SHA256_PATTERN.fullmatch(
            declared_previous
        ):
            errors.append(_error("previous_event_sha256_invalid", line=line_number))
        elif declared_previous != previous_event_sha256:
            errors.append(
                _error(
                    "previous_event_sha256_mismatch",
                    line=line_number,
                    expected=previous_event_sha256,
                    actual=declared_previous,
                )
            )

        declared_event_sha256 = event.get("event_sha256")
        if not isinstance(declared_event_sha256, str) or not _SHA256_PATTERN.fullmatch(
            declared_event_sha256
        ):
            errors.append(_error("event_sha256_invalid", line=line_number))
        if HASHED_TRACE_FIELDS.issubset(actual_fields):
            try:
                hash_input = {key: event[key] for key in HASHED_TRACE_FIELDS}
                computed_event_sha256 = hashlib.sha256(
                    canonical_json(hash_input).encode("utf-8")
                ).hexdigest()
            except (TypeError, ValueError) as exc:
                errors.append(
                    _error("event_not_canonicalizable", line=line_number, detail=str(exc))
                )
            else:
                if declared_event_sha256 != computed_event_sha256:
                    errors.append(
                        _error(
                            "event_hash_mismatch",
                            line=line_number,
                            expected=computed_event_sha256,
                            actual=declared_event_sha256,
                        )
                    )

        if isinstance(declared_event_sha256, str) and _SHA256_PATTERN.fullmatch(
            declared_event_sha256
        ):
            previous_event_sha256 = declared_event_sha256
            final_event_sha256 = declared_event_sha256
        expected_sequence += 1

    if anchored:
        if (
            isinstance(expected_event_count, bool)
            or not isinstance(expected_event_count, int)
            or expected_event_count < 0
        ):
            errors.append(_error("expected_event_count_invalid"))
        elif event_count != expected_event_count:
            errors.append(
                _error(
                    "expected_event_count_mismatch",
                    expected=expected_event_count,
                    actual=event_count,
                )
            )
        if event_count == 0:
            if expected_final_event_sha256 is not None:
                errors.append(
                    _error(
                        "expected_final_event_sha256_mismatch",
                        expected=expected_final_event_sha256,
                        actual=None,
                    )
                )
        elif (
            not isinstance(expected_final_event_sha256, str)
            or not _SHA256_PATTERN.fullmatch(expected_final_event_sha256)
            or final_event_sha256 != expected_final_event_sha256
        ):
            errors.append(
                _error(
                    "expected_final_event_sha256_mismatch",
                    expected=expected_final_event_sha256,
                    actual=final_event_sha256,
                )
            )

    return {
        "valid": not errors,
        "anchored": anchored,
        "event_count": event_count,
        "final_event_sha256": final_event_sha256,
        "errors": errors,
    }


def verify_trace_file(
    path: str | Path,
    *,
    expected_event_count: int | object = _ANCHOR_UNSET,
    expected_final_event_sha256: str | None | object = _ANCHOR_UNSET,
) -> dict:
    trace_path = Path(path)
    if not trace_path.is_file():
        return {
            "valid": False,
            "anchored": (
                expected_event_count is not _ANCHOR_UNSET
                and expected_final_event_sha256 is not _ANCHOR_UNSET
            ),
            "event_count": 0,
            "final_event_sha256": None,
            "errors": [_error("trace_file_missing", path=str(trace_path))],
        }
    try:
        content = trace_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return {
            "valid": False,
            "anchored": (
                expected_event_count is not _ANCHOR_UNSET
                and expected_final_event_sha256 is not _ANCHOR_UNSET
            ),
            "event_count": 0,
            "final_event_sha256": None,
            "errors": [_error("trace_not_utf8", detail=str(exc))],
        }
    return verify_trace_text(
        content,
        expected_event_count=expected_event_count,
        expected_final_event_sha256=expected_final_event_sha256,
    )


class TraceWriter:
    def __init__(self, path: str | Path | None):
        self.path = Path(path) if path else None
        self._lock = threading.Lock()
        self._event_count = 0
        self._final_event_sha256: str | None = None
        self._needs_separator = False
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                verification = verify_trace_file(self.path)
                if not verification["valid"]:
                    raise TraceIntegrityError(
                        "Existing trace prefix failed integrity verification: "
                        + canonical_json(verification["errors"])
                    )
                self._event_count = verification["event_count"]
                self._final_event_sha256 = verification["final_event_sha256"]
                self._needs_separator = (
                    self.path.stat().st_size > 0
                    and not self.path.read_bytes().endswith(b"\n")
                )

    def write(self, name: str, attributes: dict) -> dict:
        with self._lock:
            event = build_trace_event(
                sequence=self._event_count + 1,
                previous_event_sha256=(
                    self._final_event_sha256 or GENESIS_PREVIOUS_EVENT_SHA256
                ),
                trace_id=uuid4().hex,
                timestamp=utc_now(),
                name=name,
                attributes=attributes,
            )
            if self.path:
                with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                    if self._needs_separator:
                        handle.write("\n")
                    handle.write(canonical_json(event) + "\n")
                self._needs_separator = False
            self._event_count += 1
            self._final_event_sha256 = event["event_sha256"]
            return event

    def anchor(self) -> dict:
        with self._lock:
            return {
                "schema": TRACE_SCHEMA,
                "event_count": self._event_count,
                "final_event_sha256": self._final_event_sha256,
            }
