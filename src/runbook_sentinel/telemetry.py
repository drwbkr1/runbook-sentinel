from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .errors import TraceIntegrityError


TRACE_SCHEMA = "trace-chain/v1"
TRACE_ANCHOR_SCHEMA = "trace-anchor/v1"
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
TRACE_ANCHOR_FIELDS = frozenset(
    {
        "schema",
        "trace_schema",
        "trace_file_name",
        "event_count",
        "final_event_sha256",
        "anchor_sha256",
    }
)
HASHED_TRACE_ANCHOR_FIELDS = TRACE_ANCHOR_FIELDS - {"anchor_sha256"}
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


def live_trace_anchor_path(trace_path: str | Path) -> Path:
    """Return the explicit sibling endpoint path for one live trace."""

    path = Path(trace_path)
    return path.with_name(path.name + ".anchor.json")


def build_trace_anchor(
    *, trace_path: str | Path, event_count: int, final_event_sha256: str
) -> dict:
    """Build one canonical unkeyed trace-anchor/v1 endpoint."""

    anchor_payload = {
        "schema": TRACE_ANCHOR_SCHEMA,
        "trace_schema": TRACE_SCHEMA,
        "trace_file_name": Path(trace_path).name,
        "event_count": event_count,
        "final_event_sha256": final_event_sha256,
    }
    anchor_sha256 = hashlib.sha256(
        canonical_json(anchor_payload).encode("utf-8")
    ).hexdigest()
    return {**anchor_payload, "anchor_sha256": anchor_sha256}


def verify_trace_anchor_text(text: str, *, trace_path: str | Path) -> dict:
    """Verify one canonical endpoint document without trusting its fields."""

    errors: list[dict] = []
    try:
        anchor = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {
            "valid": False,
            "errors": [_error("anchor_invalid_json", detail=str(exc))],
            "anchor": None,
        }
    if not isinstance(anchor, dict):
        return {
            "valid": False,
            "errors": [_error("anchor_not_object")],
            "anchor": None,
        }

    actual_fields = frozenset(anchor)
    if actual_fields != TRACE_ANCHOR_FIELDS:
        errors.append(
            _error(
                "anchor_fields_mismatch",
                missing=sorted(TRACE_ANCHOR_FIELDS - actual_fields),
                unexpected=sorted(actual_fields - TRACE_ANCHOR_FIELDS),
            )
        )
    if anchor.get("schema") != TRACE_ANCHOR_SCHEMA:
        errors.append(_error("anchor_schema_mismatch"))
    if anchor.get("trace_schema") != TRACE_SCHEMA:
        errors.append(_error("anchor_trace_schema_mismatch"))
    if anchor.get("trace_file_name") != Path(trace_path).name:
        errors.append(
            _error(
                "anchor_trace_file_name_mismatch",
                expected=Path(trace_path).name,
                actual=anchor.get("trace_file_name"),
            )
        )

    event_count = anchor.get("event_count")
    if isinstance(event_count, bool) or not isinstance(event_count, int) or event_count < 1:
        errors.append(_error("anchor_event_count_invalid"))
    final_event_sha256 = anchor.get("final_event_sha256")
    if not isinstance(final_event_sha256, str) or not _SHA256_PATTERN.fullmatch(
        final_event_sha256
    ):
        errors.append(_error("anchor_final_event_sha256_invalid"))
    declared_anchor_sha256 = anchor.get("anchor_sha256")
    if not isinstance(declared_anchor_sha256, str) or not _SHA256_PATTERN.fullmatch(
        declared_anchor_sha256
    ):
        errors.append(_error("anchor_sha256_invalid"))

    if actual_fields.issuperset(HASHED_TRACE_ANCHOR_FIELDS):
        hashed_payload = {
            field: anchor[field] for field in sorted(HASHED_TRACE_ANCHOR_FIELDS)
        }
        expected_anchor_sha256 = hashlib.sha256(
            canonical_json(hashed_payload).encode("utf-8")
        ).hexdigest()
        if declared_anchor_sha256 != expected_anchor_sha256:
            errors.append(
                _error(
                    "anchor_sha256_mismatch",
                    expected=expected_anchor_sha256,
                    actual=declared_anchor_sha256,
                )
            )

    return {"valid": not errors, "errors": errors, "anchor": anchor}


def verify_anchored_trace_files(
    trace_path: str | Path, anchor_path: str | Path
) -> dict:
    """Verify one live trace against its separately persisted endpoint."""

    trace = Path(trace_path)
    anchor_file = Path(anchor_path)
    trace_exists = trace.exists()
    trace_nonempty = trace_exists and trace.stat().st_size > 0
    anchor_exists = anchor_file.exists()
    if not trace_exists and anchor_exists:
        return {
            "valid": False,
            "anchored": True,
            "event_count": 0,
            "final_event_sha256": None,
            "anchor_sha256": None,
            "errors": [_error("trace_missing")],
        }
    if not trace_nonempty and not anchor_exists:
        return {
            "valid": True,
            "anchored": False,
            "event_count": 0,
            "final_event_sha256": None,
            "anchor_sha256": None,
            "errors": [],
        }
    if trace_nonempty and not anchor_exists:
        unanchored = verify_trace_file(trace)
        return {
            **unanchored,
            "anchored": False,
            "anchor_sha256": None,
            "valid": False,
            "errors": [*unanchored["errors"], _error("anchor_missing")],
        }
    if not trace_nonempty and anchor_exists:
        return {
            "valid": False,
            "anchored": True,
            "event_count": 0,
            "final_event_sha256": None,
            "anchor_sha256": None,
            "errors": [_error("trace_missing")],
        }

    try:
        anchor_text = anchor_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        anchor_verification = {
            "valid": False,
            "errors": [_error("anchor_not_utf8", detail=str(exc))],
            "anchor": None,
        }
    else:
        anchor_verification = verify_trace_anchor_text(anchor_text, trace_path=trace)
    if not anchor_verification["valid"]:
        return {
            "valid": False,
            "anchored": True,
            "event_count": 0,
            "final_event_sha256": None,
            "anchor_sha256": None,
            "errors": anchor_verification["errors"],
        }

    anchor = anchor_verification["anchor"]
    trace_verification = verify_trace_file(
        trace,
        expected_event_count=anchor["event_count"],
        expected_final_event_sha256=anchor["final_event_sha256"],
    )
    return {
        **trace_verification,
        "anchor_sha256": anchor["anchor_sha256"],
        "errors": trace_verification["errors"],
    }


def _write_trace_anchor_atomic(anchor_path: Path, anchor: dict) -> None:
    """Durably write canonical endpoint bytes before replacing the sibling path."""

    anchor_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{anchor_path.name}.", suffix=".tmp", dir=anchor_path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json(anchor) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, anchor_path)
    finally:
        temporary_path.unlink(missing_ok=True)


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
    def __init__(
        self,
        path: str | Path | None,
        anchor_path: str | Path | None = None,
    ):
        self.path = Path(path) if path else None
        self.anchor_path = Path(anchor_path) if anchor_path else None
        self._lock = threading.Lock()
        self._event_count = 0
        self._final_event_sha256: str | None = None
        self._needs_separator = False
        self._failed = False
        if self.anchor_path and not self.path:
            raise ValueError("A trace anchor requires a trace path")
        if self.path and self.anchor_path:
            if self.path.parent.resolve() != self.anchor_path.parent.resolve():
                raise ValueError("Trace and anchor must be siblings in the same directory")
            if not self.anchor_path.name.endswith(".anchor.json"):
                raise ValueError("Trace anchor path must end with .anchor.json")
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.anchor_path:
                verification = verify_anchored_trace_files(self.path, self.anchor_path)
                if not verification["valid"]:
                    raise TraceIntegrityError(
                        "Existing anchored trace failed integrity verification: "
                        + canonical_json(verification["errors"])
                    )
                self._event_count = verification["event_count"]
                self._final_event_sha256 = verification["final_event_sha256"]
            elif self.path.exists():
                verification = verify_trace_file(self.path)
                if not verification["valid"]:
                    raise TraceIntegrityError(
                        "Existing trace prefix failed integrity verification: "
                        + canonical_json(verification["errors"])
                    )
                self._event_count = verification["event_count"]
                self._final_event_sha256 = verification["final_event_sha256"]
            if self.path.exists():
                self._needs_separator = (
                    self.path.stat().st_size > 0
                    and not self.path.read_bytes().endswith(b"\n")
                )

    def write(self, name: str, attributes: dict) -> dict:
        with self._lock:
            if self._failed:
                raise TraceIntegrityError(
                    "Trace writer is unavailable after a persistence failure"
                )
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
            try:
                if self.path:
                    with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                        if self._needs_separator:
                            handle.write("\n")
                        handle.write(canonical_json(event) + "\n")
                        handle.flush()
                        os.fsync(handle.fileno())
                    self._needs_separator = False
                    if self.anchor_path:
                        _write_trace_anchor_atomic(
                            self.anchor_path,
                            build_trace_anchor(
                                trace_path=self.path,
                                event_count=self._event_count + 1,
                                final_event_sha256=event["event_sha256"],
                            ),
                        )
            except Exception:
                self._failed = True
                raise
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
