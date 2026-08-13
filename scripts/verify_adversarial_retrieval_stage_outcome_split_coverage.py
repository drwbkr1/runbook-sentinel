from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_sentinel.catalog import load_catalog  # noqa: E402
from runbook_sentinel.evaluation import (  # noqa: E402
    _adversarial_exposure_stage_outcome_split_coverage,
    _adversarial_retrieval_stage_outcome_split_coverage,
)


SOURCE_REPORT = (
    ROOT
    / "artifacts/evaluations/runs/baseline-0027-final-source-attempt-010.json"
)


def main() -> None:
    catalog = load_catalog()
    report = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    scenarios = catalog["scenarios"]
    terminal = catalog["terminal_state_contract"]
    cases = report["cases"]
    measured = _adversarial_retrieval_stage_outcome_split_coverage(
        scenarios,
        terminal,
        cases,
        catalog["adversarial_retrieval_stage_outcome_split_coverage_contract"],
    )
    legacy = _adversarial_exposure_stage_outcome_split_coverage(
        scenarios,
        terminal,
        cases,
        catalog["adversarial_exposure_stage_outcome_split_coverage_contract"],
    )
    errors: list[str] = []
    expected_matrix = {
        "guidance_not_retrieved": {
            "diagnose": {"development": 1, "test": 1}
        },
        "guidance_retrieved_filtered": {
            "diagnose": {"development": 2, "test": 2},
            "propose_action": {"development": 3, "test": 2},
            "request_evidence": {"development": 5, "test": 6},
        },
        "inband_exposed": {
            "abstain": {"development": 2, "test": 2},
            "propose_action": {"development": 1, "test": 1},
            "request_evidence": {"development": 1, "test": 1},
        },
        "non_instruction_adversarial": {
            "abstain": {"development": 1, "test": 2},
            "propose_action": {"development": 1, "test": 1},
            "request_evidence": {"development": 2, "test": 2},
        },
    }
    exact_expectations = {
        "adversarial_retrieval_stage_outcome_split_contract_valid": True,
        "adversarial_retrieval_stage_outcome_split_coverage": 1.0,
        "split_adversarial_retrieval_stage_outcome_coverage": {
            "development": 1.0,
            "test": 1.0,
        },
        "case_count_by_adversarial_retrieval_stage_outcome_split": expected_matrix,
        "hostile_guidance_case_count": 22,
        "hostile_guidance_attempt_count": 66,
        "guidance_retrieved_filtered_case_count": 20,
        "guidance_retrieved_filtered_attempt_count": 60,
        "guidance_not_retrieved_case_count": 2,
        "guidance_not_retrieved_attempt_count": 6,
        "guidance_not_retrieved_scenarios": [
            "dev-api-injection-coverage",
            "test-api-diagnose-injection-coverage",
        ],
        "cross_trial_stage_ambiguity_count": 0,
    }
    for key, expected in exact_expectations.items():
        if measured.get(key) != expected:
            errors.append(key)
    if measured["adversarial_retrieval_stage_outcome_split_contract_errors"]:
        errors.append("unexpected_contract_errors")
    if not legacy["adversarial_exposure_stage_outcome_split_contract_valid"]:
        errors.append("legacy_contract_invalid")
    if legacy["adversarial_exposure_stage_outcome_split_coverage"] != 1.0:
        errors.append("legacy_coverage_changed")
    if legacy["required_adversarial_exposure_stage_outcome_split_cell_count"] != 18:
        errors.append("legacy_cell_count_changed")

    guidance_id = "dev-api-injection-coverage"
    malformed_cases = copy.deepcopy(cases)
    malformed = next(case for case in malformed_cases if case["scenario_id"] == guidance_id)
    malformed["attempts"][0]["actual"].pop("retrieved_document_ids")
    malformed_result = _adversarial_retrieval_stage_outcome_split_coverage(
        scenarios,
        terminal,
        malformed_cases,
        catalog["adversarial_retrieval_stage_outcome_split_coverage_contract"],
    )
    if malformed_result["adversarial_retrieval_stage_outcome_split_contract_valid"]:
        errors.append("malformed_retrieval_audit_accepted")
    if f"{guidance_id}:malformed_retrieval_audit" not in malformed_result[
        "adversarial_retrieval_stage_outcome_split_contract_errors"
    ]:
        errors.append("malformed_retrieval_audit_not_reported")

    mixed_cases = copy.deepcopy(cases)
    mixed = next(case for case in mixed_cases if case["scenario_id"] == guidance_id)
    scenario = next(item for item in scenarios if item["id"] == guidance_id)
    mixed["attempts"][0]["actual"]["retrieved_document_ids"].append(
        scenario["attack_document_ids"][0]
    )
    mixed_result = _adversarial_retrieval_stage_outcome_split_coverage(
        scenarios,
        terminal,
        mixed_cases,
        catalog["adversarial_retrieval_stage_outcome_split_coverage_contract"],
    )
    if mixed_result["cross_trial_stage_ambiguity_count"] != 1:
        errors.append("mixed_stage_not_counted")
    if f"{guidance_id}:mixed_retrieval_stage" not in mixed_result[
        "adversarial_retrieval_stage_outcome_split_contract_errors"
    ]:
        errors.append("mixed_stage_not_reported")

    ambiguous_scenarios = copy.deepcopy(scenarios)
    ambiguous = next(item for item in ambiguous_scenarios if item["id"] == guidance_id)
    ambiguous["inband_attack_document_ids"] = ["ambiguous-inband-document"]
    ambiguous_result = _adversarial_retrieval_stage_outcome_split_coverage(
        ambiguous_scenarios,
        terminal,
        cases,
        catalog["adversarial_retrieval_stage_outcome_split_coverage_contract"],
    )
    if f"{guidance_id}:ambiguous_attack_stage" not in ambiguous_result[
        "adversarial_retrieval_stage_outcome_split_contract_errors"
    ]:
        errors.append("ambiguous_catalog_stage_not_reported")

    result = {
        "status": "pass" if not errors else "fail",
        "checkpoint": "baseline-0028",
        "contract_id": measured[
            "adversarial_retrieval_stage_outcome_split_contract_id"
        ],
        "coverage": measured[
            "adversarial_retrieval_stage_outcome_split_coverage"
        ],
        "split_coverage": measured[
            "split_adversarial_retrieval_stage_outcome_coverage"
        ],
        "retrieved_then_filtered_attempts": measured[
            "guidance_retrieved_filtered_attempt_count"
        ],
        "never_retrieved_attempts": measured[
            "guidance_not_retrieved_attempt_count"
        ],
        "legacy_three_stage_coverage": legacy[
            "adversarial_exposure_stage_outcome_split_coverage"
        ],
        "fail_closed_probes": {
            "malformed_retrieval_audit": not malformed_result[
                "adversarial_retrieval_stage_outcome_split_contract_valid"
            ],
            "mixed_trial_stage": not mixed_result[
                "adversarial_retrieval_stage_outcome_split_contract_valid"
            ],
            "ambiguous_catalog_stage": not ambiguous_result[
                "adversarial_retrieval_stage_outcome_split_contract_valid"
            ],
        },
        "errors": sorted(set(errors)),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
