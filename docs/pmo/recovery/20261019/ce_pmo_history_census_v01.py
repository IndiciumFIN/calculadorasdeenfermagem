#!/usr/bin/env python3
"""Read-only CE history evidence census; hash local report bytes and archive members.

The output is an evidence index, NOT an execution completion or Kernel ledger.
ZIP paths are represented by stable hashed locators; no extraction to disk.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "upload" / "CE_MASTER_CONTINUITY_20261018(1).zip"
MILESTONE = re.compile(r"^CE_M(\d{2})[A-Z_].*\.md$")
ROUND = re.compile(r"CE_R(\d+)/")
CE = re.compile(r"(?:^|[/_])CE(0[0-6])(?:[/_\-.]|$)", re.IGNORECASE)
CHUNK = 1024 * 1024


def sha_stream(reader) -> str:
    digest = hashlib.sha256()
    while True:
        part = reader.read(CHUNK)
        if not part:
            break
        digest.update(part)
    return digest.hexdigest()


def build() -> dict:
    rows = []
    for path in sorted(ROOT.iterdir(), key=lambda x: x.name):
        match = MILESTONE.fullmatch(path.name)
        if not match or path.is_symlink() or not path.is_file():
            continue
        with path.open("rb") as stream:
            digest = sha_stream(stream)
        rows.append({"record_id": "M-" + digest[:20], "domain": "M" + match.group(1), "evidence_type": "LOCAL_MILESTONE_REPORT", "locator": path.name, "sha256": digest, "bytes": path.stat().st_size, "execution_state": "ARTIFACT_OBSERVED_NOT_EXECUTION_CERTIFIED"})

    archived = []
    with zipfile.ZipFile(ARCHIVE) as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            name = member.filename
            normalized = name.replace("\\", "/")
            parts = PurePosixPath(normalized).parts
            if normalized.startswith("/") or ".." in parts or re.match(r"^[A-Za-z]:", normalized) or stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError("unsafe archive member; census fails closed")
            with z.open(member, "r") as stream:
                digest = sha_stream(stream)
            scope = CE.search(normalized)
            round_match = ROUND.search(normalized)
            label = ("CE" + scope.group(1)) if scope else (("R" + round_match.group(1)) if round_match else "HISTORICAL_UNCLASSIFIED")
            locator_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            archived.append({"record_id": "ZIP-" + locator_hash[:20], "domain": label, "evidence_type": "ARCHIVE_MEMBER_VERIFIED_BYTES", "locator_sha256": locator_hash, "sha256": digest, "bytes": member.file_size, "container": ARCHIVE.name, "execution_state": "ARCHIVE_EVIDENCE_NOT_EXECUTION_CERTIFIED"})

    rounds = sorted({int(m.group(1)) for member in zipfile.ZipFile(ARCHIVE).namelist() if (m := ROUND.search(member))})
    by_class = Counter(r["domain"] for r in archived)
    by_milestone = Counter(r["domain"] for r in rows)
    return {
        "schema_version": "0.1.0", "kind": "HISTORICAL_EVIDENCE_INDEX_NOT_EXECUTION_LEDGER",
        "cutoff": "2026-10-19", "privacy": "ARCHIVE_MEMBER_NAMES_HASHED_NO_PRIVATE_PATH_EXPORT",
        "source_container": ARCHIVE.name,
        "counts": {"local_milestone_reports": len(rows), "local_milestone_ids": len(by_milestone), "archive_members_read_and_sha256_verified": len(archived), "archived_rounds_observed": len(rounds), "min_round": min(rounds) if rounds else None, "max_round": max(rounds) if rounds else None, "archive_members_by_domain": dict(sorted(by_class.items())), "milestone_reports_by_id": dict(sorted(by_milestone.items()))},
        "historical_execution_certification": "NOT_INFERRED_FROM_EVIDENCE_INDEX",
        "local_reports": rows,
        "archive_evidence": archived,
        "missing_coverage": ["Full Git commit/task/WO execution receipts by semantic identity", "CE01-CE06 approvals vs plans", "Kernel admission and independent auditing", "Non-continuity ZIP corpora and previous unsurfaced conversations"]
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
