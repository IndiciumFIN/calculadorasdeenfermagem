#!/usr/bin/env python3
"""Read-only local/ZIP content index in Git-blob SHA1 object namespace.

Default output is aggregate only. --emit-private-index writes *nothing* but
prints a JSON set of content fingerprints for in-memory reconciliation by the
orchestrator. Never publish that raw index without privacy/security triage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

from ce_pmo_inventory_recursive_v02 import DEFAULT_MANIFEST, DEFAULT_SUMMARY, inventory
from ce_pmo_zip_verify_v01 import inspect_zip

ROOT = Path(__file__).resolve().parent
CHUNK = 1024 * 1024


def git_blob_hash(stream, size: int) -> str:
    obj = hashlib.sha1(b"blob " + str(size).encode("ascii") + b"\0")
    seen = 0
    while True:
        block = stream.read(CHUNK)
        if not block:
            break
        seen += len(block)
        if seen > size:
            raise ValueError("bytes exceed declared object size")
        obj.update(block)
    if seen != size:
        raise ValueError("declared object size mismatch")
    return obj.hexdigest()


def content_index() -> dict:
    private_manifest, _ = inventory(DEFAULT_MANIFEST, DEFAULT_SUMMARY)
    local = set()
    for item in private_manifest["files"]:
        path = ROOT / item["relative_path"]
        with path.open("rb") as handle:
            local.add(git_blob_hash(handle, item["bytes"]))

    zipped = set()
    total = Counter()
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() != ".zip":
            continue
        check = inspect_zip(path)
        if check["status"] != "PASS_ZIP_INTEGRITY_ONLY":
            raise ValueError("ZIP safety/integrity gate failed")
        total["zip_containers"] += 1
        with zipfile.ZipFile(path) as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                with archive.open(entry) as handle:
                    zipped.add(git_blob_hash(handle, entry.file_size))
                total["zip_members"] += 1
    return {"local": sorted(local), "zip": sorted(zipped), "summary": {
        "local_unique_git_blob_objects": len(local),
        "zip_unique_git_blob_objects": len(zipped),
        "local_zip_common_git_blob_objects": len(local & zipped),
        "zip_containers": total["zip_containers"],
        "zip_members": total["zip_members"],
    }}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-private-index", action="store_true", help="stdout hashes for orchestrator; do not publish")
    args = parser.parse_args()
    data = content_index()
    if args.emit_private_index:
        print(json.dumps(data, separators=(",", ":")))
    else:
        print(json.dumps({"status": "CONTENT_INDEX_BUILT_LOCAL_ONLY", "summary": data["summary"], "privacy": "NO_HASH_VALUES_EMITTED", "release": "HOLD"}, sort_keys=True))


if __name__ == "__main__":
    main()
