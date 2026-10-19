#!/usr/bin/env python3
"""Read-only local regular-file vs ZIP member reconciliation by exact SHA256.

No filenames, member names or content are emitted; no extraction to disk.
Only safe ZIP containers that pass the ZIP integrity gate are read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from ce_pmo_inventory_recursive_v02 import DEFAULT_MANIFEST, DEFAULT_SUMMARY, inventory
from ce_pmo_zip_verify_v01 import inspect_zip

CHUNK = 1024 * 1024


def payload_hash(reader) -> str:
    hash_obj = hashlib.sha256()
    for block in iter(lambda: reader.read(CHUNK), b""):
        hash_obj.update(block)
    return hash_obj.hexdigest()


def reconcile(root: Path) -> dict:
    # To keep this scanner aligned with current local inventory v0.2, root is fixed.
    if root.resolve() != Path(__file__).resolve().parent:
        raise ValueError("root must be this script's workspace; no inferred arbitrary scope")
    manifest, snapshot = inventory(DEFAULT_MANIFEST, DEFAULT_SUMMARY)
    local_by_hash = defaultdict(list)
    for item in manifest["files"]:
        local_by_hash[item["sha256"]].append(item["group"])

    zip_by_hash = defaultdict(set)
    zip_member_count = 0
    zip_member_bytes = 0
    holds = []
    zipped = sorted(path for path in root.rglob("*") if path.is_file() and not path.is_symlink() and path.suffix.lower() == ".zip")
    for n, path in enumerate(zipped):
        check = inspect_zip(path)
        if check["status"] != "PASS_ZIP_INTEGRITY_ONLY":
            holds.append("ZIP_CONTAINER_FAILED_AT_INDEX_" + str(n))
            continue
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                with archive.open(member) as contents:
                    checksum = payload_hash(contents)
                zip_by_hash[checksum].add(n)
                zip_member_count += 1
                zip_member_bytes += member.file_size

    local_hashes = set(local_by_hash)
    zip_hashes = set(zip_by_hash)
    matched = local_hashes & zip_hashes
    matched_paths = sum(len(local_by_hash[checksum]) for checksum in matched)
    categories = Counter()
    for checksum in matched:
        categories.update(local_by_hash[checksum])
    result = {
        "schema_version": "0.1.0",
        "scope": "same_run_local_regular_files_vs_outer_zip_regular_members_SHA256",
        "privacy": "AGGREGATE_ONLY_NO_MEMBER_NAMES_OR_HASHES",
        "local_file_count": snapshot["file_count"],
        "local_unique_hashes": len(local_hashes),
        "zip_containers_scanned": len(zipped),
        "zip_member_count": zip_member_count,
        "zip_member_declared_bytes": zip_member_bytes,
        "zip_unique_member_hashes": len(zip_hashes),
        "unique_sha256_present_in_both": len(matched),
        "local_paths_with_content_in_zip": matched_paths,
        "local_unique_hashes_not_in_zip": len(local_hashes - zip_hashes),
        "zip_unique_hashes_not_local_files": len(zip_hashes - local_hashes),
        "local_match_categories": dict(sorted(categories.items())),
        "zip_unique_hashes_in_multiple_containers": sum(len(containers) > 1 for containers in zip_by_hash.values()),
        "zip_failure_count": len(holds),
        "status": "HOLD" if holds else "PASS_EXACT_HASH_RECONCILIATION_ONLY",
        "limitations": [
            "No filename or title similarity used; equal hash proves only byte equality",
            "ZIP-to-ZIP member multiplicity within one container not represented by container-level set",
            "Current workspace is mutable; result needs immutable cutoff and private manifest for replay",
            "No GitHub branch-tree comparison, canonical admission, ownership or legal approval",
        ],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    result = reconcile(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS_EXACT_HASH_RECONCILIATION_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
