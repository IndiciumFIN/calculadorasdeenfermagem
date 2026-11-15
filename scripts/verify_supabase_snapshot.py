#!/usr/bin/env python3
"""Verifica hashes, arquivos e contagens da extração Supabase, sem conexão externa."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json")

class Hold(Exception):
    pass

def verify_file(path, meta):
    raw = path.read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if len(raw) != meta["bytes"] or sha != meta["git_blob_sha1"]:
        raise Hold("SOURCE_HASH_OR_SIZE_DRIFT: " + str(path))
    try:
        if path.suffix == ".jsonl":
            records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
        else:
            records = json.loads(raw.decode("utf-8"))["rows"]
    except (ValueError, UnicodeError, KeyError) as exc:
        raise Hold("SOURCE_NOT_PARSEABLE: " + str(path)) from exc
    if len(records) != meta["record_count"]:
        raise Hold("ROW_COUNT_DRIFT: " + str(path))
    return records

def verify(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if manifest.get("approval_state") != "HOLD_HUMAN" or manifest.get("database_mutated") is not False:
        raise Hold("UNAUTHORIZED_PROMOTION")
    if manifest.get("snapshot_consistency") != "NON_ATOMIC_ACROSS_QUERIES":
        raise Hold("UNVERIFIED_SNAPSHOT_CONSISTENCY")
    files = manifest.get("files", [])
    if len(files) != manifest["coverage"]["source_file_count"] or len(files) != 22:
        raise Hold("FILE_SET_INCOMPLETE")
    seen = set()
    total_columns = 0
    total_reference = 0
    for meta in files:
        rel = Path(meta["path"])
        if rel.is_absolute() or ".." in rel.parts or str(rel) in seen:
            raise Hold("INVALID_SOURCE_PATH")
        seen.add(str(rel))
        verify_file(root / rel, meta)
        if rel.name.startswith("columns-"):
            total_columns += meta["record_count"]
        if "reference" in rel.parts:
            total_reference += meta["record_count"]
    if total_columns != 7246 or total_reference != 1173:
        raise Hold("COVERAGE_TOTAL_DRIFT")
    return {"status": "INVENTORY_VERIFIED_NO_DB_WRITES",
            "source_files": len(files),
            "columns": total_columns,
            "reference_metadata_rows": total_reference,
            "migration_authorized": False}

if __name__ == "__main__":
    try:
        print(json.dumps(verify(), indent=2))
    except (Hold, ValueError, KeyError, OSError) as exc:
        print("HOLD: " + str(exc))
        raise SystemExit(2)
