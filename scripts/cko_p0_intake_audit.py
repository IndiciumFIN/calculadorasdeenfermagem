#!/usr/bin/env python3
"""CKO/NCOS: deterministic, read-only intake inventory for ZIP and individual files.

No remote access, extraction, external packages or execution of source code.
SHA-256 proves byte identity only, never clinical assurance or publication rights.
"""
import argparse
import collections
import hashlib
import io
import json
import pathlib
import stat
import zipfile

LIMIT_FILE = 100 * 1024 * 1024
LIMIT_NESTED = 200 * 1024 * 1024
MAX_DEPTH = 4

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def nested_zip(blob, depth=0):
    result = {"entries": [], "issues": []}
    if depth >= MAX_DEPTH:
        result["issues"].append("NESTED_DEPTH_LIMIT")
        return result
    if not zipfile.is_zipfile(io.BytesIO(blob)):
        result["issues"].append("INVALID_NESTED_ZIP")
        return result
    seen = set()
    total = 0
    with zipfile.ZipFile(io.BytesIO(blob)) as source:
        for info in source.infolist():
            if info.is_dir():
                continue
            parts = info.filename.replace("\\", "/").split("/")
            if info.filename.startswith("/") or ".." in parts or "" in parts:
                result["issues"].append("UNSAFE_PATH")
                continue
            if info.filename in seen:
                result["issues"].append("DUPLICATE_NAME")
                continue
            seen.add(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                result["issues"].append("SYMLINK")
                continue
            total += info.file_size
            if info.file_size > LIMIT_FILE or total > LIMIT_NESTED:
                result["issues"].append("ZIP_BOMB_LIMIT")
                break
            try:
                data = source.read(info)
            except Exception:
                result["issues"].append("CRC_ERROR")
                continue
            entry = {"path": info.filename, "bytes": len(data), "sha256": digest(data)}
            if info.filename.lower().endswith(".zip"):
                entry["nested"] = nested_zip(data, depth + 1)
                if entry["nested"]["issues"]:
                    result["issues"].append("NESTED_ISSUES")
            result["entries"].append(entry)
    result["entries"].sort(key=lambda r: r["path"])
    result["issues"] = sorted(set(result["issues"]))
    return result

def scan_one(path):
    source = pathlib.Path(path)
    if not source.is_file():
        raise ValueError("Unreadable source file")
    data = source.read_bytes()
    result = {"name": source.name, "bytes": len(data), "sha256": digest(data),
              "issues": [], "entries": [], "nested_archives": []}
    if source.suffix.lower() == ".zip" and not zipfile.is_zipfile(io.BytesIO(data)):
        result["issues"].append("INVALID_ZIP")
    elif zipfile.is_zipfile(io.BytesIO(data)):
        checked = nested_zip(data)
        result["entries"] = checked["entries"]
        result["issues"].extend(checked["issues"])
        result["nested_archives"] = [
            {"path": e["path"], **e["nested"]} for e in checked["entries"] if "nested" in e
        ]
        result["logical_sha256"] = digest(json.dumps(
            [(e["path"], e["sha256"]) for e in checked["entries"]],
            ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    result["entry_count"] = len(result["entries"])
    result["issues"] = sorted(set(result["issues"]))
    return result

def scan(paths):
    files = [scan_one(p) for p in paths]
    if len({f["name"] for f in files}) != len(files):
        raise ValueError("Duplicate input basenames")
    groups = collections.defaultdict(list)
    seen_path = collections.defaultdict(set)
    for f in files:
        if "logical_sha256" in f:
            groups[f["logical_sha256"]].append(f["name"])
        for e in f["entries"]:
            seen_path[e["path"]].add(e["sha256"])
    return {
        "schema_version": "1.0.0",
        "kind": "P0_SOURCE_INTAKE_READ_ONLY",
        "clinical_approval": False,
        "release_allowed": False,
        "inputs": files,
        "count": len(files),
        "duplicate_groups": sorted(sorted(v) for v in groups.values() if len(v) > 1),
        "same_path_different_bytes": sorted(k for k, v in seen_path.items() if len(v) > 1),
        "integrity": "PASS" if all(not f["issues"] for f in files) else "HOLD",
        "p0_release": "HOLD",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args()
    report = scan(args.inputs)
    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"inputs": report["count"], "duplicate_groups": report["duplicate_groups"],
                      "integrity": report["integrity"], "p0_release": report["p0_release"]},
                     ensure_ascii=False))
    if report["integrity"] != "PASS":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
