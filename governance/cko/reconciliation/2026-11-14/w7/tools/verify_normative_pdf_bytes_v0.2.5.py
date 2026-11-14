#!/usr/bin/env python3
"""Fail-closed byte integrity checker for CKO normative-source evidence.

A matching file hash demonstrates only equality with an expected byte digest.
It cannot establish authenticity, current legal effect, reproduction rights, or
clinical approval. Never copies or prints source content.
"""
import argparse
import hashlib
import json
from pathlib import Path

KINDS = {"OFFICIAL_PRIMARY_CANDIDATE", "DERIVED_DOSSIER", "OTHER_REFERENCE"}


def verify(file_path: Path, sha256: str, kind: str, expected_bytes: int | None = None):
    if kind not in KINDS:
        raise ValueError("Unknown source kind: refuse classification")
    if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
        raise ValueError("Expected SHA-256 must be 64 lowercase hex characters")
    result = {
        "schema_version": "CKO_NORM_SOURCE_RECEIPT_1",
        "file_name": file_path.name,
        "source_kind": kind,
        "expected_sha256": sha256,
        "expected_size_bytes": expected_bytes,
        "actual_size_bytes": None,
        "actual_sha256": None,
        "starts_with_pdf_signature": False,
        "status": "HOLD_FILE_MISSING",
        "actual_source_bytes_examined": False,
        "primary_source_approved": False,
        "normative_currentness_approved": False,
        "reuse_rights_approved": False,
        "clinical_review_approved": False,
        "publication_allowed": False,
    }
    if not file_path.is_file():
        return result
    result["actual_source_bytes_examined"] = True
    h = hashlib.sha256()
    size = 0
    with file_path.open("rb") as handle:
        first = handle.read(5)
        result["starts_with_pdf_signature"] = first == b"%PDF-"
        h.update(first)
        size += len(first)
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(block)
            h.update(block)
    result["actual_size_bytes"] = size
    result["actual_sha256"] = h.hexdigest()
    if not result["starts_with_pdf_signature"]:
        result["status"] = "HOLD_NOT_PDF"
    elif result["actual_sha256"] != sha256 or (expected_bytes is not None and size != expected_bytes):
        result["status"] = "HOLD_HASH_OR_SIZE_MISMATCH"
    elif kind == "DERIVED_DOSSIER":
        result["status"] = "DERIVED_DOSSIER_BYTES_MATCH_HOLD_PRIMARY"
    elif kind == "OTHER_REFERENCE":
        result["status"] = "REFERENCE_BYTES_MATCH_HOLD_PRIMARY"
    else:
        result["status"] = "OFFICIAL_CANDIDATE_BYTES_MATCH_HOLD_LEGAL_RIGHTS_CLINICAL"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--kind", required=True, choices=sorted(KINDS))
    parser.add_argument("--expected-bytes", type=int)
    parser.add_argument("--output", type=Path, help="Optional metadata-only receipt")
    args = parser.parse_args()
    receipt = verify(args.input, args.expected_sha256, args.kind, args.expected_bytes)
    message = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(message, encoding="utf-8")
    print(message, end="")
    # Exit 0 is limited to successful candidate *byte-integrity* verification.
    # Derived/secondary evidence must fail closed for a downstream source gate.
    # Even exit 0 never admits legal currentness, rights or clinical publication.
    return 0 if receipt["status"] == "OFFICIAL_CANDIDATE_BYTES_MATCH_HOLD_LEGAL_RIGHTS_CLINICAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
