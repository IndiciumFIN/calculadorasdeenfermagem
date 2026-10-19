#!/usr/bin/env python3
"""P1 ZIP integrity and completeness guard. Read-only, no extraction."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import stat
import sys
import zipfile

CHUNK = 1024 * 1024
MAX_FILES = 10000
MAX_TOTAL = 2 * 1024 * 1024 * 1024
MAX_MEMBER = 512 * 1024 * 1024
MAX_RATIO = 1000

def _safe_name(name):
    p = pathlib.PurePosixPath(name)
    return isinstance(name,str) and bool(name) and not p.is_absolute() and all(
        x not in ("", ".", "..") for x in name.split("/")
    ) and "\\" not in name and ":" not in name and "\x00" not in name

def audit_zip(archive, manifest):
    errors, holds = [], []
    expected = manifest.get("members")
    if not isinstance(expected,list):
        return {"decision":"FAIL","errors":["MISSING_EXPECTED_MEMBERS"],"holds":[]}
    if any(not isinstance(e,dict) or not all(k in e for k in ("path","sha256","byte_length")) for e in expected):
        return {"decision":"FAIL","errors":["MALFORMED_EXPECTATION"],"holds":[]}
    expected_names = [e["path"] for e in expected]
    if len(set(expected_names)) != len(expected_names):
        errors.append("DUPLICATE_MANIFEST")
    if any(not _safe_name(p) for p in expected_names):
        errors.append("UNSAFE_EXPECTED_PATH")
    if manifest.get("archive_sha256"):
        dig = hashlib.sha256()
        with open(archive,"rb") as stream:
            for part in iter(lambda:stream.read(CHUNK),b""):
                dig.update(part)
        if dig.hexdigest() != manifest["archive_sha256"]:
            errors.append("ARCHIVE_SHA_MISMATCH")
    try:
        with zipfile.ZipFile(archive) as z:
            all_infos=z.infolist()
            if any(not _safe_name(i.filename.rstrip("/")) for i in all_infos):
                errors.append("ZIP_SLIP_PATH")
            infos=[i for i in all_infos if not i.is_dir()]
            names=[i.filename for i in infos]
            if len(infos)>MAX_FILES:
                errors.append("ENTRY_LIMIT")
            if len(set(names))!=len(names) or len(set(n.casefold() for n in names))!=len(names):
                errors.append("DUPLICATE_OR_CASE_COLLISION")
            if set(names)!=set(expected_names):
                errors.append("POPULATION_MISMATCH")
            if any(not _safe_name(n) for n in names):
                errors.append("ZIP_SLIP_PATH")
            total=sum(i.file_size for i in infos)
            if total>MAX_TOTAL:
                errors.append("TOTAL_SIZE_LIMIT")
            lookup={e["path"]:e for e in expected}
            scanned=0
            for info in infos:
                n=info.filename
                mode=(info.external_attr >> 16)
                if stat.S_ISLNK(mode):
                    errors.append("SYMLINK_MEMBER:"+n)
                    continue
                if info.flag_bits & 1:
                    errors.append("ENCRYPTED_MEMBER:"+n)
                    continue
                if not _safe_name(n) or n not in lookup:
                    continue
                if info.file_size>MAX_MEMBER or info.file_size/max(info.compress_size,1)>MAX_RATIO:
                    errors.append("DECOMPRESSION_LIMIT:"+n)
                    continue
                dig=hashlib.sha256()
                count=0
                try:
                    with z.open(info) as stream:
                        for part in iter(lambda:stream.read(CHUNK),b""):
                            count+=len(part)
                            if count>MAX_MEMBER or count>info.file_size:
                                raise ValueError("SIZE_EXCEEDED")
                            dig.update(part)
                except (RuntimeError, OSError, ValueError, zipfile.BadZipFile, NotImplementedError) as exc:
                    errors.append("CORRUPT_MEMBER:"+n+":"+type(exc).__name__)
                    continue
                scanned+=1
                e=lookup[n]
                if count!=info.file_size or count!=e["byte_length"]:
                    errors.append("MEMBER_LENGTH_MISMATCH:"+n)
                if dig.hexdigest()!=e["sha256"]:
                    errors.append("MEMBER_SHA_MISMATCH:"+n)
                if n.lower().endswith((".zip",".7z",".rar",".tar",".gz")):
                    holds.append("NESTED_ARCHIVE_REQUIRES_SEPARATE_AUDIT:"+n)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        errors.append("INVALID_ARCHIVE:"+type(exc).__name__)
        scanned=0
        names=[]
    return {"decision":"FAIL" if errors else "HOLD" if holds else "PASS_BOUNDED",
            "errors":sorted(set(errors)),"holds":sorted(set(holds)),
            "entries_declared":len(expected),"entries_observed":len(names),
            "entries_scanned":scanned,
            "scope":"P1_ZIP_MEMBER_INTEGRITY_AND_MANIFEST_COMPLETENESS_ONLY",
            "source_universe_verified":False,"semantic_precision_verified":False}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--manifest",required=True)
    a=p.parse_args(argv)
    try:
        m=json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
        result=audit_zip(a.archive,m)
    except (OSError,ValueError,TypeError) as exc:
        result={"decision":"FAIL","errors":["INPUT_ERROR:"+type(exc).__name__],"holds":[]}
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return {"PASS_BOUNDED":0,"HOLD":78}.get(result["decision"],2)

if __name__=="__main__":
    sys.exit(main())
