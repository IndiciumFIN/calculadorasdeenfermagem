"""Fail-closed M24 five-source identity check. Not a Kernel admission."""
import argparse
import json
from pathlib import Path


def validate_m24(register):
    findings = []
    if register.get("population_id") != "POP-M24-HOLD":
        findings.append("M24_WRONG_POPULATION")
    records = register.get("records", [])
    if not isinstance(records, list) or len(records) != 5:
        return findings + ["M24_EXACT_FIVE_IDENTITIES_REQUIRED"]
    paths = []
    for i, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"M24_RECORD_NOT_OBJECT:{i}")
            continue
        path, sha, evidence = (item.get(k) for k in ("git_path", "source_sha256", "identity_evidence"))
        if not isinstance(path, str) or not path.startswith("data/legado/extracao_bruta/atomizado/") or not path.endswith(".jsonl"):
            findings.append(f"M24_PATH_UNVERIFIED:{i}")
        else:
            paths.append(path)
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            findings.append(f"M24_SHA_UNVERIFIED:{i}")
        if not isinstance(evidence, str) or not evidence.strip():
            findings.append(f"M24_IDENTITY_EVIDENCE_MISSING:{i}")
        if item.get("state") != "HOLD_ENVIRONMENT":
            findings.append(f"M24_PREMATURE_RELEASE:{i}")
    if len(paths) != len(set(paths)):
        findings.append("M24_DUPLICATE_PATH")
    return findings


def main():
    parser = argparse.ArgumentParser(description="Validate exact five M24 file identities; never admit execution")
    parser.add_argument("register", type=Path)
    args = parser.parse_args()
    issues = validate_m24(json.loads(args.register.read_text(encoding="utf-8")))
    print(json.dumps({"decision": "HOLD" if issues else "IDENTITY_DOCUMENTED_ONLY", "findings": issues}, ensure_ascii=False))
    raise SystemExit(2 if issues else 0)


if __name__ == "__main__":
    main()
