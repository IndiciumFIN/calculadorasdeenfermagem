#!/usr/bin/env python3
"""Read-only source inventory; writes only a new PMO candidate report.

No source file is modified, removed or moved. A local presence is not evidence
of a GitHub commit or durable Library version.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "CE_PMO_INVENTARIO_LOCAL_20261019_CANDIDATE.json"


def included(path: Path) -> bool:
    if not path.is_file() or path.name == OUTPUT.name:
        return False
    if path.parent == ROOT / "upload":
        return True
    if path.parent != ROOT:
        return False
    name = path.name
    return (
        name.startswith("CE_")
        or name.startswith("ce_m") and name.endswith(".py")
        or name.startswith("test_ce_m") and name.endswith(".py")
    )


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def category(path: Path) -> str:
    if path.parent == ROOT / "upload":
        return "USER_INPUT_PRESERVED_LOCAL"
    if path.name.endswith(".zip"):
        return "ARCHIVE_OR_CHECKPOINT"
    if path.name.startswith("test_ce_m"):
        return "LOCAL_TEST"
    if path.name.startswith("ce_m"):
        return "LOCAL_EXECUTOR"
    if path.suffix == ".md":
        return "REPORT_OR_HANDOFF_CANDIDATE"
    return "OTHER_LOCAL_CONTROL_OR_DATA"


def main() -> None:
    paths = [p for p in ROOT.iterdir() if included(p)]
    upload = ROOT / "upload"
    if upload.exists():
        paths.extend(p for p in upload.iterdir() if included(p))
    entries = [
        {
            "relative_path": str(path.relative_to(ROOT)),
            "category": category(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "local_state": "PRESENT_BYTES_HASHED",
            "remote_persistence": "NOT_VERIFIED_IN_THIS_INVENTORY",
            "canonical_git_admission": "NOT_VERIFIED_IN_THIS_INVENTORY",
        }
        for path in sorted(paths, key=lambda item: str(item.relative_to(ROOT)))
    ]
    report = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "current scratch root CE_*, ce_m*.py, test_ce_m*.py and upload/ immediate files",
        "disclaimer": "Presence and SHA256 confirm only local bytes; provenance, authorship, canonical admission and Library persistence require independent readback",
        "total_files": len(entries),
        "total_bytes": sum(item["bytes"] for item in entries),
        "files": entries,
    }
    # Atomic replacement; a failed run must not leave a truncated candidate.
    fd, temp_name = tempfile.mkstemp(prefix=".ce_pmo_inventory_", suffix=".json", dir=ROOT)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as target:
            json.dump(report, target, ensure_ascii=False, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temp_name, OUTPUT)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(json.dumps({"output": OUTPUT.name, "files": len(entries), "bytes": report["total_bytes"]}))


if __name__ == "__main__":
    main()
