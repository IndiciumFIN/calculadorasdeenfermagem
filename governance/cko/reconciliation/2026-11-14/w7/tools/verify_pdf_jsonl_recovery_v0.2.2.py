#!/usr/bin/env python3
"""Offline, fail-closed byte/hash checker for W7 PDF JSONL recovery. No upload."""
import argparse
import hashlib
import json
from pathlib import Path

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def verify(manifest, directory):
    entries = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(entries) != 17:
        raise ValueError("Expected exactly 17 recovery manifest records")
    results = []
    for record in entries:
        name = record["expected_jsonl_filename"]
        expected = record["expected_jsonl_sha256"]
        if Path(name).name != name or not name.endswith(".jsonl"):
            raise ValueError("Untrusted manifest filename")
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise ValueError("Invalid expected SHA256")
        path = directory / name
        if not path.is_file():
            results.append({"filename": name, "status": "MISSING"})
            continue
        actual = sha256_file(path)
        if actual != expected:
            results.append({"filename": name, "status": "HASH_MISMATCH"})
            continue
        try:
            count = 0
            with path.open(encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        json.loads(line)
                        count += 1
            results.append({"filename": name, "status": "HASH_MATCH_JSONL_PARSE_OK", "jsonl_records": count})
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            results.append({"filename": name, "status": "INVALID_JSONL"})
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, required=True, help="Local authorized folder with recovered JSONL files")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parent.parent / "audit" / "PDF_JSONL_RECOVERY_INVENTORY_v0.2.2.jsonl")
    args = parser.parse_args()
    results = verify(args.manifest, args.dir)
    print(json.dumps({"results": results, "no_publication_approval": True}, ensure_ascii=False, indent=2))
    return 0 if all(x["status"] == "HASH_MATCH_JSONL_PARSE_OK" for x in results) else 2

if __name__ == "__main__":
    raise SystemExit(main())
