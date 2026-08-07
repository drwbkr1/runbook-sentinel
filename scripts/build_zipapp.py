from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "eval/package-contract-0014.json"
PACKAGE_MANIFEST_PATH = "runbook_sentinel/data/package-manifest.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def generated_package_manifest(contract: dict, contract_raw: bytes, entries: dict[str, bytes]) -> bytes:
    package_contract = contract["package_manifest"]
    frozen_path = "runbook_sentinel/data/eval-manifest.json"
    payload = {
        "schema_version": package_contract["schema_version"],
        "project": package_contract["project"],
        "version": package_contract["version"],
        "checkpoint": package_contract["checkpoint"],
        "format": "python-zipapp",
        "python_requires": package_contract["python_requires"],
        "package_contract_sha256": sha256_bytes(contract_raw),
        "frozen_evaluation_manifest": {
            "archive_path": frozen_path,
            "sha256": sha256_bytes(entries[frozen_path]),
        },
        "entries": {name: sha256_bytes(value) for name, value in sorted(entries.items())},
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_entries(contract: dict, source_root: Path, contract_raw: bytes) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    generated_entry: dict | None = None
    for entry in contract["entries"]:
        archive_path = entry["archive_path"]
        if entry["source_kind"] == "generated_package_manifest":
            generated_entry = entry
            continue
        entries[archive_path] = (source_root / entry["source_path"]).read_bytes()
    if generated_entry is None or generated_entry["archive_path"] != PACKAGE_MANIFEST_PATH:
        raise ValueError("The frozen contract has no canonical generated package manifest")
    entries[PACKAGE_MANIFEST_PATH] = generated_package_manifest(contract, contract_raw, entries)
    expected_order = [entry["archive_path"] for entry in contract["entries"]]
    if list(sorted(entries)) != expected_order:
        raise ValueError("Loaded entries differ from the frozen ordered allowlist")
    return entries


def write_archive(output: Path, contract: dict, entries: dict[str, bytes]) -> None:
    metadata = contract["archive_metadata"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_STORED) as archive:
        archive.comment = b""
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=tuple(metadata["timestamp"]))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = metadata["create_system"]
            info.external_attr = metadata["external_attr"]
            info.extra = b""
            info.comment = b""
            archive.writestr(info, entries[name])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the frozen deterministic Runbook Sentinel zipapp.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    contract_path = args.contract.resolve()
    source_root = args.source_root.resolve()
    contract_raw = contract_path.read_bytes()
    contract = json.loads(contract_raw)
    output = (args.output or source_root / contract["candidate"]["artifact"]).resolve()
    checksum = output.with_name(output.name + ".sha256")
    if output.exists() or checksum.exists():
        raise FileExistsError(f"Package attempt is immutable and already exists: {output}")

    entries = load_entries(contract, source_root, contract_raw)
    write_archive(output, contract, entries)
    archive_sha256 = sha256_file(output)
    checksum.write_text(f"{archive_sha256}  {output.name}\n", encoding="ascii", newline="\n")
    print(
        json.dumps(
            {
                "status": "built",
                "checkpoint": contract["checkpoint"],
                "archive": str(output),
                "archive_bytes": output.stat().st_size,
                "archive_sha256": archive_sha256,
                "checksum": str(checksum),
                "entry_count": len(entries),
                "runtime_dependencies": contract["candidate"]["runtime_dependencies"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
