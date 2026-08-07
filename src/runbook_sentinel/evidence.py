from __future__ import annotations

from datetime import datetime, timezone


FRESHNESS_SECONDS = 3600
PROJECT_EVIDENCE_KINDS = {"telemetry", "status"}


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def is_fresh_project_evidence(document: dict, as_of: object) -> bool:
    if document.get("kind") not in PROJECT_EVIDENCE_KINDS:
        return False
    reference_time = parse_timestamp(as_of)
    observed_at = parse_timestamp(document.get("observed_at"))
    if reference_time is None or observed_at is None:
        return False
    age_seconds = (reference_time - observed_at).total_seconds()
    return 0 <= age_seconds <= FRESHNESS_SECONDS
