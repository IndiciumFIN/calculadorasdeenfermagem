"""Inventário determinístico e somente leitura de ZIPs e diretórios locais.

Uso: python -m packages.cli.archive_audit CAMINHO --output data/grc/archive_audit.json
Não extrai membros, não altera originais, não apaga duplicatas.
"""
import argparse
import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path, PurePosixPath

BLOCK = 1024 * 1024
MAX_RATIO = 1000


def digest_stream(handle):
    h = hashlib.sha256()
    size = 0
    while True:
        block = handle.read(BLOCK)
        if not block:
            break
        h.update(block)
        size += len(block)
    return h.hexdigest(), size


def zip_scan(path):
    result = {"file": str(path), "kind": "zip", "members": [], "findings": []}
    with path.open("rb") as stream:
        result["sha256"], result["bytes"] = digest_stream(stream)
    with zipfile.ZipFile(path) as z:
        seen = set()
        for info in z.infolist():
            p = PurePosixPath(info.filename.replace("\\", "/"))
            is_symlink = stat.S_ISLNK((info.external_attr >> 16) & 0xFFFF)
            unsafe = p.is_absolute() or ".." in p.parts or "\\x00" in info.filename or is_symlink or (len(p.parts) > 0 and ":" in p.parts[0])
            ratio = info.file_size / max(info.compress_size, 1)
            item = {"path": info.filename, "bytes": info.file_size, "compressed": info.compress_size, "crc32": f"{info.CRC:08x}", "unsafe": unsafe, "compression_ratio": round(ratio, 2), "sha256": None}
            if info.filename in seen:
                result["findings"].append({"type": "DUPLICATED_MEMBER_NAME", "member": info.filename})
            seen.add(info.filename)
            if unsafe:
                result["findings"].append({"type": "UNSAFE_MEMBER", "member": info.filename})
            elif ratio > MAX_RATIO:
                result["findings"].append({"type": "EXTREME_COMPRESSION_RATIO", "member": info.filename})
            elif not info.is_dir():
                # Streaming member hash; may be expensive, never loads whole file.
                with z.open(info, "r") as stream:
                    item["sha256"], observed = digest_stream(stream)
                if observed != info.file_size:
                    result["findings"].append({"type": "SIZE_MISMATCH", "member": info.filename})
            result["members"].append(item)
    return result


def audit(paths):
    files = []
    for root in paths:
        p = Path(root)
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(x for x in p.rglob("*") if x.is_file() and not x.is_symlink())
        else:
            raise FileNotFoundError(root)
    results = []
    groups = {}
    members = {}
    for p in sorted(set(files), key=str):
        try:
            if zipfile.is_zipfile(p):
                item = zip_scan(p)
            else:
                with p.open("rb") as handle:
                    digest, n = digest_stream(handle)
                item = {"file": str(p), "kind": "file", "bytes": n, "sha256": digest, "members": [], "findings": []}
            results.append(item)
            groups.setdefault(item["sha256"], []).append(item["file"])
            for member in item["members"]:
                if member["sha256"]:
                    members.setdefault(member["sha256"], []).append({"archive": item["file"], "member": member["path"]})
        except Exception as exc:
            results.append({"file": str(p), "status": "HOLD_HUMAN", "error": str(exc)})
    return {"schema_version": "1.0.0", "mode": "READ_ONLY", "files": results,
            "identical_file_groups": [v for v in groups.values() if len(v) > 1],
            "identical_member_groups": [v for v in members.values() if len(v) > 1],
            "deletion_authorized": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = audit(args.paths)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, out)
    print(json.dumps({"files": len(result["files"]), "identical_files": len(result["identical_file_groups"]), "identical_members": len(result["identical_member_groups"]), "output": str(out)}))


if __name__ == "__main__":
    main()
