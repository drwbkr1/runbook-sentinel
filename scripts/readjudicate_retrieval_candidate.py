from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_retrieval_candidate_admissibility_contract as verifier  # noqa: E402


CONTRACT_PATH = verifier.CONTRACT_PATH
RESULT_PATH = verifier.RESULT_PATH
IMPLEMENTATION_PATH = Path(__file__).resolve()


class AdjudicationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdjudicationError(f"{label}_json") from exc
    if not isinstance(value, dict):
        raise AdjudicationError(f"{label}_object")
    return value


def _retained_paths(contract: dict[str, Any]) -> dict[str, Path]:
    retained = contract["retained_comparison"]
    return {
        "control_report": ROOT / retained["control_report_path"],
        "control_trace": ROOT / retained["control_trace_path"],
        "candidate_report": ROOT / retained["candidate_report_path"],
        "candidate_trace": ROOT / retained["candidate_trace_path"],
        "comparison": ROOT / retained["comparison_path"],
        "original_contract": ROOT / retained["original_contract_path"],
        "original_result_verifier": ROOT
        / retained["original_result_verifier_path"],
    }


def _input_identities(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    retained = contract["retained_comparison"]
    identities: dict[str, dict[str, Any]] = {}
    for label, path in _retained_paths(contract).items():
        expected_bytes = retained[f"{label}_bytes"]
        expected_sha256 = retained[f"{label}_sha256"]
        if (
            not path.is_file()
            or path.stat().st_size != expected_bytes
            or sha256(path) != expected_sha256
        ):
            raise AdjudicationError(f"{label}_identity")
        identities[label] = {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": expected_bytes,
            "sha256": expected_sha256,
        }
    return identities


def _source_snapshot(contract: dict[str, Any]) -> dict[str, str]:
    paths = {
        "contract": CONTRACT_PATH,
        "implementation": IMPLEMENTATION_PATH,
        "contract_verifier": Path(verifier.__file__).resolve(),
        **_retained_paths(contract),
    }
    return {label: sha256(path) for label, path in paths.items()}


def assemble_result(
    contract: dict[str, Any],
    candidate: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    classification = verifier.classify_candidate(contract, candidate, comparison)
    if classification["errors"] or not classification["candidate_evidence_admissible"]:
        raise AdjudicationError(
            "candidate_evidence_inadmissible:"
            + ",".join(sorted(classification["errors"]))
        )

    expected = contract["frozen_expected_readjudication"]
    retained = contract["retained_comparison"]
    weakness = contract["measured_weakness"]
    identities = _input_identities(contract)

    result: dict[str, Any] = {
        "schema_version": "1.0",
        "checkpoint": "baseline-0033",
        "contract_id": contract["contract_id"],
        "contract_schema_version": contract["schema_version"],
        **expected,
        "source_contract_sha256": sha256(CONTRACT_PATH),
        "source_implementation_sha256": sha256(IMPLEMENTATION_PATH),
        "source_contract_verifier_sha256": sha256(Path(verifier.__file__).resolve()),
        "source_control_report_sha256": retained["control_report_sha256"],
        "source_control_trace_sha256": retained["control_trace_sha256"],
        "source_candidate_report_sha256": retained["candidate_report_sha256"],
        "source_candidate_trace_sha256": retained["candidate_trace_sha256"],
        "source_comparison_sha256": retained["comparison_sha256"],
        "input_identities": identities,
        "candidate_boolean_gate_count": classification[
            "candidate_boolean_gate_count"
        ],
        "candidate_false_gates": classification["candidate_false_gates"],
        "safe_superset_pairs": classification["safe_superset_pairs"],
        "focus_observations": {
            "control_extra_document_count": weakness["control_extra_document_count"],
            "candidate_extra_document_count": weakness[
                "candidate_extra_document_count"
            ],
            "control_expected_document_share_mean": weakness[
                "control_expected_document_share_mean"
            ],
            "candidate_expected_document_share_mean": weakness[
                "candidate_expected_document_share_mean"
            ],
            "held_out_control_expected_document_share_mean": weakness[
                "held_out_control_expected_document_share_mean"
            ],
            "held_out_candidate_expected_document_share_mean": weakness[
                "held_out_candidate_expected_document_share_mean"
            ],
            "held_out_control_extra_document_count": weakness[
                "held_out_control_extra_document_count"
            ],
            "held_out_candidate_extra_document_count": weakness[
                "held_out_candidate_extra_document_count"
            ],
        },
        "latency_selection": {
            "control_median_latency_ms": weakness["control_median_latency_ms"],
            "candidate_median_latency_ms": weakness[
                "candidate_median_latency_ms"
            ],
            "median_latency_non_inferior": weakness[
                "median_latency_non_inferior"
            ],
        },
        "original_comparison": {
            "status": retained["original_status"],
            "selected_configuration": retained[
                "original_selected_configuration"
            ],
            "candidate_disposition": retained["original_candidate_disposition"],
        },
        "boundaries": {
            "candidate_admissible_is_not_candidate_selected": True,
            "default_release_gates_unchanged": True,
            "historical_reports_and_dispositions_immutable": True,
            "runtime_or_default_changed": False,
            "security_boundary_changed": False,
            "held_out_used_for_tuning": False,
            "broad_pareto_claimed": False,
            "production_readiness_claimed": False,
            "universal_safety_claimed": False,
        },
        "time_basis": {
            "contract_frozen_at_utc": contract["frozen_at_utc"],
            "lifecycle_corrected_at_utc": contract["lifecycle_correction"][
                "corrected_at_utc"
            ],
            "wall_clock_time_used": False,
        },
    }
    return result


def build_result() -> dict[str, Any]:
    lifecycle = verifier.validate("implementation_sealed_no_result")
    if lifecycle["status"] != "pass":
        raise AdjudicationError(
            "implementation_seal_invalid:" + ",".join(lifecycle["errors"])
        )

    contract = _load_object(CONTRACT_PATH, "contract")
    paths = _retained_paths(contract)
    before = _source_snapshot(contract)
    candidate = _load_object(paths["candidate_report"], "candidate_report")
    comparison = _load_object(paths["comparison"], "comparison")
    result = assemble_result(contract, candidate, comparison)
    after = _source_snapshot(contract)
    if before != after:
        raise AdjudicationError("source_input_mutated")
    return result


def canonical_bytes(result: dict[str, Any]) -> bytes:
    return (
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def write_result(output: Path = RESULT_PATH) -> dict[str, Any]:
    output = output.resolve()
    if output != RESULT_PATH.resolve():
        raise AdjudicationError("output_path_not_frozen")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    if not output.parent.is_dir():
        raise AdjudicationError("output_parent_missing")

    result = build_result()
    payload = canonical_bytes(result)
    with output.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())

    validation = verifier.validate("implemented_overlay")
    if validation["status"] != "pass":
        raise AdjudicationError(
            "written_result_invalid:" + ",".join(validation["errors"])
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Readjudicate the exact retained retrieval candidate under the frozen "
            "candidate-admissibility overlay."
        )
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the one frozen successor result; default is read-only in-memory evaluation.",
    )
    args = parser.parse_args()

    result = write_result() if args.write else build_result()
    summary = {
        "status": result["status"],
        "candidate_evidence_admissible": result[
            "candidate_evidence_admissible"
        ],
        "candidate_selected": result["candidate_selected"],
        "selected_configuration": result["selected_configuration"],
        "result_written": args.write,
        "result_path": RESULT_PATH.relative_to(ROOT).as_posix() if args.write else None,
        "result_sha256": sha256(RESULT_PATH) if args.write else None,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
