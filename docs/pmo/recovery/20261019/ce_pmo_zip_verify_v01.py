#!/usr/bin/env python3
"""Read-only ZIP payload/CRC and path safety verifier for CE PMO recovery.

Never extracts files or follows symlinks. Aggregate output omits paths and hashes.
The status is NOT an approval of document content, licenses or custody.
"""
from __future__ import annotations

import argparse
import json
import re
import stat
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

DEFAULT_MAX_MEMBER = 128 * 1024 * 1024
DEFAULT_MAX_ARCHIVE = 512 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


def unsafe_name(name: str) -> bool:
    unified = name.replace("\\", "/")
    parts = PurePosixPath(unified).parts
    return (
        not unified or name.startswith(("/", "\\")) or ".." in parts
        or bool(re.match(r"^[A-Za-z]:", unified)) or "\x00" in unified
    )


def inspect_zip(path: Path, *, max_member: int = DEFAULT_MAX_MEMBER,
                max_archive: int = DEFAULT_MAX_ARCHIVE) -> dict:
    counters = Counter()
    findings: set[str] = set()
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            counters["declared_entries"] = len(members)
            regular = [m for m in members if not m.is_dir()]
            counters["declared_regular_entries"] = len(regular)
            declared_total = sum(m.file_size for m in regular)
            counters["declared_uncompressed_bytes"] = declared_total
            if declared_total > max_archive:
                findings.add("ZIP_ARCHIVE_BUDGET_EXCEEDED")
                return {"counts": dict(counters), "findings": sorted(findings), "status": "HOLD"}
            seen: set[str] = set()
            for member in members:
                norm = member.filename.replace("\\", "/")
                if unsafe_name(member.filename):
                    findings.add("ZIP_PATH_TRAVERSAL")
                if norm in seen:
                    findings.add("ZIP_DUPLICATE_ENTRY_NAME")
                seen.add(norm)
                if stat.S_ISLNK(member.external_attr >> 16):
                    findings.add("ZIP_SYMLINK_ENTRY")
                if member.flag_bits & 1:
                    findings.add("ZIP_ENCRYPTED_MEMBER")
                if member.file_size > max_member:
                    findings.add("ZIP_MEMBER_BUDGET_EXCEEDED")
            # Never decode unsafe archives; this is a gate, not a best-effort extraction.
            if findings:
                return {"counts": dict(counters), "findings": sorted(findings), "status": "HOLD"}
            for member in regular:
                streamed = 0
                try:
                    with archive.open(member) as reader:
                        while True:
                            block = reader.read(CHUNK_SIZE)
                            if not block:
                                break
                            streamed += len(block)
                            if streamed > max_member or streamed > member.file_size:
                                findings.add("ZIP_RUNTIME_BUDGET_EXCEEDED")
                                break
                    if streamed != member.file_size:
                        findings.add("ZIP_LENGTH_MISMATCH")
                    else:
                        counters["payload_crc_verified"] += 1
                        counters["payload_bytes_verified"] += streamed
                except (OSError, EOFError, RuntimeError, ValueError, zipfile.BadZipFile, NotImplementedError):
                    findings.add("ZIP_PAYLOAD_READ_OR_CRC_FAILED")
            status = "PASS_ZIP_INTEGRITY_ONLY" if not findings else "HOLD"
            return {"counts": dict(counters), "findings": sorted(findings), "status": status}
    except (OSError, EOFError, RuntimeError, ValueError, zipfile.BadZipFile, zipfile.LargeZipFile):
        return {"counts": dict(counters), "findings": ["ZIP_OPEN_FAILED"], "status": "HOLD"}


def inspect_tree(root: Path) -> dict:
    totals = Counter()
    failures = Counter()
    paths = sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink() and p.suffix.lower() == ".zip")
    for path in paths:
        result = inspect_zip(path)
        totals.update(result["counts"])
        failures.update(result["findings"])
        if result["status"] == "PASS_ZIP_INTEGRITY_ONLY":
            totals["zip_verified"] += 1
        else:
            totals["zip_hold"] += 1
    return {
        "schema_version": "0.1.0",
        "root_scope": "current_local_workspace_recursive_zip_files_only",
        "zip_count": len(paths),
        "totals": dict(totals),
        "failure_codes": dict(failures),
        "privacy": "AGGREGATE_ONLY_NO_MEMBER_NAMES_PATHS_OR_HASHES",
        "status": "PASS_ZIP_INTEGRITY_ONLY" if not failures and totals["zip_hold"] == 0 else "HOLD",
        "limitations": ["Nested archives are not recursively decompressed", "CRC does not attest clinical, legal, semantic, version or provenance correctness", "No remote source comparison or persistence readback"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    result = inspect_tree(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS_ZIP_INTEGRITY_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
