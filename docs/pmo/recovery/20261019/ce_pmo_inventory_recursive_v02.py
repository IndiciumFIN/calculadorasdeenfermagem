#!/usr/bin/env python3
"""Read-only deterministic recursive evidence inventory and privacy-safe summary.

No external persistence is inferred from a filename. Detailed paths and hashes
remain local by default, since upload names can contain private information.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "CE_PMO_INVENTARIO_RECURSIVO_LOCAL_20261019_PRIVATE.json"
DEFAULT_SUMMARY = ROOT / "CE_PMO_INVENTARIO_RECURSIVO_RESUMO_20261019_CANDIDATE.json"


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def group(path: Path) -> str:
    relative = path.relative_to(ROOT)
    first = relative.parts[0]
    if first == "upload":
        return "user_upload"
    if first == "admin_project_review":
        return "admin_project_review"
    if first == "cko_val_001":
        return "cko_val_001"
    if first == "ce_lib_helpers_20261019":
        return "ce_lib_helpers_20261019"
    if len(relative.parts) == 1:
        return "workspace_root"
    return "other_nested"


def atomic_json(path: Path, data: dict) -> None:
    handle, scratch = tempfile.mkstemp(prefix=".ce_pmo_", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as output:
            json.dump(data, output, ensure_ascii=False, sort_keys=True, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(scratch, path)
    finally:
        if os.path.exists(scratch):
            os.unlink(scratch)


def inventory(manifest_path: Path, summary_path: Path) -> tuple[dict, dict]:
    excluded = {manifest_path.resolve(), summary_path.resolve()}
    items = []
    symlink_count = 0
    zip_files = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_symlink():
            symlink_count += 1
            continue
        if not path.is_file() or path.resolve() in excluded:
            continue
        stat = path.stat()
        row = {
            "relative_path": path.relative_to(ROOT).as_posix(),
            "group": group(path),
            "bytes": stat.st_size,
            "sha256": digest_file(path),
            "external_persistence": "NOT_PROVEN_BY_LOCAL_SCAN",
        }
        items.append(row)
        if path.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(path) as archive:
                    infos = archive.infolist()
                    zip_files.append({
                        "relative_path": row["relative_path"],
                        "entry_count": len(infos),
                        "regular_entries": sum(not info.is_dir() for info in infos),
                        "uncompressed_bytes_declared": sum(info.file_size for info in infos if not info.is_dir()),
                        "zip_status": "CENTRAL_DIRECTORY_READABLE_NOT_FULL_CONTENT_VERIFIED",
                    })
            except (OSError, zipfile.BadZipFile) as error:
                zip_files.append({"relative_path": row["relative_path"], "zip_status": "INVALID_OR_UNREADABLE", "error_type": type(error).__name__})

    counts = Counter(item["group"] for item in items)
    sizes = Counter()
    by_hash = defaultdict(list)
    for item in items:
        sizes[item["group"]] += item["bytes"]
        by_hash[item["sha256"]].append(item["relative_path"])
    duplicate_groups = [paths for paths in by_hash.values() if len(paths) > 1]
    summary = {
        "schema_version": "0.2.0",
        "scope": "all regular files recursively below workspace root; symlinks skipped; two report files excluded",
        "privacy": "AGGREGATE_ONLY_NO_FILENAMES_OR_HASHES",
        "file_count": len(items),
        "bytes_total": sum(item["bytes"] for item in items),
        "symlink_count_skipped": symlink_count,
        "groups": {name: {"files": counts[name], "bytes": sizes[name]} for name in sorted(counts)},
        "unique_file_sha256": len(by_hash),
        "exact_duplicate_hash_groups": len(duplicate_groups),
        "files_in_duplicate_groups": sum(len(paths) for paths in duplicate_groups),
        "zip_count": len(zip_files),
        "zip_invalid_or_unreadable": sum(z["zip_status"] == "INVALID_OR_UNREADABLE" for z in zip_files),
        "zip_regular_entries_declared": sum(z.get("regular_entries", 0) for z in zip_files),
        "caveats": [
            "ZIP listings are not proof of decompression, semantic validity or canonical admission",
            "Local hashes are not proof of GitHub, Library or Supabase persistence",
            "Nested dependency trees are included and require separate classification",
            "Completeness beyond this workspace requires external manifests and independent readback",
        ],
        "pmo_gate": "HOLD",
    }
    manifest = {
        "schema_version": "0.2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root_scope": "recursive_workspace_only",
        "files": items,
        "zip_containers": zip_files,
        "exact_duplicate_paths": duplicate_groups,
    }
    return manifest, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true", help="print aggregate summary without creating any file")
    options = parser.parse_args()
    manifest, summary = inventory(DEFAULT_MANIFEST, DEFAULT_SUMMARY)
    if not options.no_write:
        atomic_json(DEFAULT_MANIFEST, manifest)
        atomic_json(DEFAULT_SUMMARY, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
