from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "eval/package-contract-0033.json"
CURRENT_CONTRACT = ROOT / "eval/package-contract.json"
PACKAGE_MANIFEST_PATH = "runbook_sentinel/data/package-manifest.json"
ALLOWED_SOURCE_KINDS = {
    "project_file",
    "frozen_evaluation_manifest",
    "generated_package_manifest",
}
ALLOWED_CONTRACT_STATUSES = {
    "frozen_before_implementation",
    "frozen_before_archive_build",
}
PACKAGE_MANIFEST_KEYS = {
    "schema_version",
    "project",
    "version",
    "checkpoint",
    "format",
    "python_requires",
    "package_contract_sha256",
    "frozen_evaluation_manifest",
    "entries",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value, raw


def expect(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def safe_relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def validate_contract(contract: dict, source_root: Path) -> list[str]:
    errors: list[str] = []
    expect(contract.get("schema_version") == "1.0", "contract schema_version must be 1.0", errors)
    checkpoint = contract.get("checkpoint")
    expect(
        isinstance(checkpoint, str) and checkpoint.startswith("baseline-"),
        "contract checkpoint must be a baseline identity",
        errors,
    )
    expect(
        contract.get("contract_status") in ALLOWED_CONTRACT_STATUSES,
        "contract must be frozen before implementation or archive build",
        errors,
    )

    candidate = contract.get("candidate")
    expect(isinstance(candidate, dict), "candidate must be an object", errors)
    if isinstance(candidate, dict):
        expect(candidate.get("format") == "python-zipapp", "candidate format must be python-zipapp", errors)
        expect(candidate.get("python_requires") == ">=3.12", "candidate must require Python >=3.12", errors)
        expect(candidate.get("runtime_dependencies") == [], "runtime dependencies must remain empty", errors)

    package_manifest = contract.get("package_manifest")
    expect(isinstance(package_manifest, dict), "package_manifest must be an object", errors)
    if isinstance(candidate, dict) and isinstance(package_manifest, dict):
        expect(candidate.get("version") == package_manifest.get("version"), "candidate and package manifest versions differ", errors)
        expect(checkpoint == package_manifest.get("checkpoint"), "contract and package manifest checkpoints differ", errors)
        expect(
            candidate.get("python_requires") == package_manifest.get("python_requires"),
            "candidate and package manifest Python requirements differ",
            errors,
        )

    metadata = contract.get("archive_metadata")
    expect(isinstance(metadata, dict), "archive_metadata must be an object", errors)
    if isinstance(metadata, dict):
        expect(metadata.get("compression") == "stored", "archive compression must be stored", errors)
        expect(
            metadata.get("entry_order") == "archive_path_ascending",
            "archive entries must be sorted by archive path",
            errors,
        )
        expect(metadata.get("timestamp") == [1980, 1, 1, 0, 0, 0], "archive timestamp must be fixed", errors)
        expect(metadata.get("create_system") == 3, "archive create_system must be 3", errors)
        expect(metadata.get("external_attr") == 2175008768, "archive external_attr must encode 100644", errors)
        expect(metadata.get("archive_comment") == "", "archive comment must be empty", errors)
        expect(metadata.get("entry_extra") == "", "archive entry extra fields must be empty", errors)

    entries = contract.get("entries")
    expect(isinstance(entries, list) and bool(entries), "entries must be a non-empty list", errors)
    archive_paths: list[str] = []
    generated_count = 0
    if isinstance(entries, list):
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"entry {index} must be an object")
                continue
            archive_path = entry.get("archive_path")
            source_kind = entry.get("source_kind")
            expect(safe_relative_path(archive_path), f"entry {index} has unsafe archive_path", errors)
            if isinstance(archive_path, str):
                archive_paths.append(archive_path)
            expect(source_kind in ALLOWED_SOURCE_KINDS, f"entry {index} has invalid source_kind", errors)
            if source_kind == "generated_package_manifest":
                generated_count += 1
                expect(archive_path == PACKAGE_MANIFEST_PATH, "generated manifest path is not canonical", errors)
                expect("source_path" not in entry, "generated manifest must not declare source_path", errors)
            else:
                source_path = entry.get("source_path")
                expect(safe_relative_path(source_path), f"entry {index} has unsafe source_path", errors)
                if safe_relative_path(source_path):
                    expect((source_root / str(source_path)).is_file(), f"source file is missing: {source_path}", errors)

    expect(len(archive_paths) == len(set(archive_paths)), "archive paths must be unique", errors)
    expect(archive_paths == sorted(archive_paths), "contract entries must be sorted by archive path", errors)
    expect(archive_paths and archive_paths[0] == "__main__.py", "archive must begin with __main__.py", errors)
    expect(generated_count == 1, "archive must contain exactly one generated package manifest", errors)
    expect("runbook_sentinel/data/eval-manifest.json" in archive_paths, "frozen evaluation manifest is missing", errors)
    expect("runbook_sentinel/data/scenarios.json" in archive_paths, "scenario catalog is missing", errors)

    exclusions = contract.get("content_exclusions")
    expect(isinstance(exclusions, dict), "content_exclusions must be an object", errors)
    if isinstance(exclusions, dict):
        fragments = exclusions.get("forbidden_path_fragments")
        expect(isinstance(fragments, list) and bool(fragments), "forbidden path fragments must be declared", errors)
        if isinstance(fragments, list):
            for archive_path in archive_paths:
                for fragment in fragments:
                    if isinstance(fragment, str):
                        expect(fragment not in archive_path, f"forbidden path fragment in contract entry: {archive_path}", errors)

    held_out = contract.get("held_out_surfaces")
    expect(isinstance(held_out, dict), "held_out_surfaces must be an object", errors)
    if isinstance(held_out, dict):
        expect(held_out.get("sealed_until_generic_candidate_complete") is True, "held-out surfaces must be sealed", errors)
        expect(
            held_out.get("candidate_or_contract_change_after_reveal_allowed") is False,
            "candidate changes after held-out reveal must be forbidden",
            errors,
        )

    parity = contract.get("parity_contract")
    expect(isinstance(parity, dict), "parity_contract must be an object", errors)
    if isinstance(parity, dict):
        expect(parity.get("security_boundaries_may_change") is False, "security boundary changes must be forbidden", errors)
        expect(parity.get("scenario_expectations_may_change") is False, "scenario expectation changes must be forbidden", errors)
        expect(parity.get("graders_may_change_after_freeze") is False, "grader changes must be forbidden", errors)

    gates = contract.get("release_gates")
    expect(isinstance(gates, dict) and gates and all(value is True for value in gates.values()), "every release gate must be mandatory", errors)
    expect(contract.get("no_go_boundaries") and isinstance(contract.get("no_go_boundaries"), list), "no-go boundaries are required", errors)
    return errors


def secret_matches(raw: bytes, patterns: list[object]) -> list[str]:
    text = raw.decode("utf-8", errors="ignore")
    matches: list[str] = []
    for pattern in patterns:
        if not isinstance(pattern, str):
            continue
        if pattern == "sk-":
            found = re.search(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}", text)
        elif pattern in {"ghp_", "github_pat_"}:
            found = re.search(re.escape(pattern) + r"[A-Za-z0-9_]{16,}", text)
        else:
            found = re.search(re.escape(pattern), text)
        if found:
            matches.append(pattern)
    return matches


def verify_archive(contract: dict, contract_raw: bytes, archive: Path, source_root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    metadata = contract["archive_metadata"]
    expected_entries = contract["entries"]
    expected_names = [entry["archive_path"] for entry in expected_entries]
    expected_by_name = {entry["archive_path"]: entry for entry in expected_entries}
    exclusions = contract["content_exclusions"]
    archive_sha256 = sha256_file(archive)

    with zipfile.ZipFile(archive, "r") as handle:
        infos = handle.infolist()
        names = [info.filename for info in infos]
        expect(names == expected_names, "archive entries do not exactly match the frozen ordered allowlist", errors)
        expect(len(names) == len(set(names)), "archive contains duplicate entries", errors)
        expect(handle.comment == b"", "archive comment is not empty", errors)

        entry_bytes: dict[str, bytes] = {}
        fixed_timestamp = tuple(metadata["timestamp"])
        for info in infos:
            expect(info.date_time == fixed_timestamp, f"entry timestamp differs: {info.filename}", errors)
            expect(info.compress_type == zipfile.ZIP_STORED, f"entry is not ZIP_STORED: {info.filename}", errors)
            expect(info.create_system == metadata["create_system"], f"entry create_system differs: {info.filename}", errors)
            expect(info.external_attr == metadata["external_attr"], f"entry permissions differ: {info.filename}", errors)
            expect(info.extra == b"", f"entry has extra metadata: {info.filename}", errors)
            expect(info.comment == b"", f"entry has a comment: {info.filename}", errors)
            entry_bytes[info.filename] = handle.read(info)

        for name, entry in expected_by_name.items():
            if name not in entry_bytes:
                continue
            if entry["source_kind"] != "generated_package_manifest":
                source = source_root / entry["source_path"]
                expect(entry_bytes[name] == source.read_bytes(), f"archive content differs from source: {name}", errors)

        forbidden_fragments = exclusions["forbidden_path_fragments"]
        forbidden_extensions = exclusions["forbidden_runtime_state_extensions"]
        secret_patterns = exclusions["forbidden_secret_patterns"]
        for name, raw in entry_bytes.items():
            expect(not any(fragment in name for fragment in forbidden_fragments), f"forbidden path is packaged: {name}", errors)
            expect(not any(name.endswith(extension) for extension in forbidden_extensions), f"runtime state is packaged: {name}", errors)
            for match in secret_matches(raw, secret_patterns):
                errors.append(f"forbidden secret pattern {match!r} found in {name}")

        package_manifest_raw = entry_bytes.get(PACKAGE_MANIFEST_PATH)
        package_manifest: dict = {}
        if package_manifest_raw is None:
            errors.append("generated package manifest is missing")
        else:
            try:
                parsed = json.loads(package_manifest_raw)
                if isinstance(parsed, dict):
                    package_manifest = parsed
                else:
                    errors.append("package manifest root must be an object")
            except json.JSONDecodeError as exc:
                errors.append(f"package manifest is invalid JSON: {exc}")

        if package_manifest:
            package_contract = contract["package_manifest"]
            expect(set(package_manifest) == PACKAGE_MANIFEST_KEYS, "package manifest keys differ from the frozen schema", errors)
            for key in ("schema_version", "project", "version", "checkpoint", "python_requires"):
                expect(package_manifest.get(key) == package_contract[key], f"package manifest {key} differs", errors)
            expect(package_manifest.get("format") == "python-zipapp", "package manifest format differs", errors)
            expect(
                package_manifest.get("package_contract_sha256") == sha256_bytes(contract_raw),
                "package manifest does not bind the frozen package contract",
                errors,
            )
            frozen = package_manifest.get("frozen_evaluation_manifest")
            expected_frozen_path = "runbook_sentinel/data/eval-manifest.json"
            expected_frozen_sha = sha256_bytes(entry_bytes.get(expected_frozen_path, b""))
            expect(
                frozen == {"archive_path": expected_frozen_path, "sha256": expected_frozen_sha},
                "package manifest frozen evaluation identity differs",
                errors,
            )
            expected_hashes = {
                name: sha256_bytes(raw)
                for name, raw in entry_bytes.items()
                if name != PACKAGE_MANIFEST_PATH
            }
            expect(package_manifest.get("entries") == expected_hashes, "package manifest entry hashes differ", errors)

    return errors, {
        "archive": str(archive),
        "archive_sha256": archive_sha256,
        "archive_bytes": archive.stat().st_size,
        "entry_count": len(expected_names),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the frozen zipapp contract and an optional candidate archive.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    args = parser.parse_args()

    contract_path = args.contract.resolve()
    source_root = args.source_root.resolve()
    contract, contract_raw = load_json(contract_path)
    errors = validate_contract(contract, source_root)
    if contract_path == DEFAULT_CONTRACT.resolve():
        expect(CURRENT_CONTRACT.read_bytes() == contract_raw, "current and versioned package contracts differ", errors)
    result = {
        "status": "pass" if not errors else "fail",
        "checkpoint": contract.get("checkpoint"),
        "contract": str(contract_path),
        "contract_sha256": sha256_bytes(contract_raw),
        "contract_status": contract.get("contract_status"),
        "contract_frozen_before_implementation": contract.get("contract_status") == "frozen_before_implementation",
        "contract_frozen_before_archive_build": contract.get("contract_status")
        in ALLOWED_CONTRACT_STATUSES,
        "archive_checked": args.archive is not None,
        "errors": errors,
    }
    if args.archive is not None and not errors:
        archive = args.archive.resolve()
        if not archive.is_file():
            errors.append(f"archive is missing: {archive}")
        else:
            archive_errors, archive_result = verify_archive(contract, contract_raw, archive, source_root)
            errors.extend(archive_errors)
            result.update(archive_result)
    result["status"] = "pass" if not errors else "fail"
    result["errors"] = errors
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
