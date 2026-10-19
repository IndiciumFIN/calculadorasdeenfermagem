#!/usr/bin/env python3
"""P1 immutable snapshot filesystem crosswalk; standard library, read-only."""
import argparse
import hashlib
import json
import os
import pathlib
import stat
import sys

MAX_FILES=200000
MAX_BYTES=4*1024*1024*1024
CHUNK=1024*1024

def _object_hash(path):
    s=path.lstat()
    if not stat.S_ISREG(s.st_mode):
        raise ValueError("NONREGULAR_FILE")
    if s.st_size>MAX_BYTES:
        raise ValueError("FILE_TOO_LARGE")
    prefix=b"blob "+str(s.st_size).encode()+b"\0"
    h1=hashlib.sha1(prefix)
    h2=hashlib.sha256()
    count=0
    with open(path,"rb") as f:
        for part in iter(lambda:f.read(CHUNK),b""):
            count+=len(part)
            if count>MAX_BYTES or count>s.st_size:
                raise ValueError("FILE_CHANGED_DURING_READ")
            h1.update(part)
            h2.update(part)
    after=path.lstat()
    if count!=s.st_size or after.st_size!=s.st_size or after.st_mtime_ns!=s.st_mtime_ns or after.st_ino!=s.st_ino:
        raise ValueError("FILE_CHANGED_DURING_READ")
    return {"git_blob_sha1":h1.hexdigest(),"sha256":h2.hexdigest(),"byte_length":count}

def audit(root,manifest):
    root=pathlib.Path(root)
    failures=[]
    if not root.exists() or not root.is_dir() or root.is_symlink():
        return {"decision":"FAIL","errors":["INVALID_ROOT"]}
    expected=manifest.get("files")
    if not isinstance(expected,list) or any(not isinstance(e,dict) or not all(k in e for k in ("path","sha256","git_blob_sha1","byte_length")) for e in expected):
        return {"decision":"FAIL","errors":["MALFORMED_EXPECTATION"]}
    ids=[e["path"] for e in expected]
    if len(set(ids))!=len(ids):
        failures.append("DUPLICATE_MANIFEST")
    actual=[]
    for base, dirs, files in os.walk(root,followlinks=False):
        for directory in dirs[:]:
            if (pathlib.Path(base)/directory).is_symlink():
                failures.append("SYMLINK_DIRECTORY:"+directory)
                dirs.remove(directory)
        for f in files:
            path=pathlib.Path(base)/f
            rel=path.relative_to(root).as_posix()
            if path.is_symlink():
                failures.append("SYMLINK_FILE:"+rel)
                continue
            actual.append(rel)
            if len(actual)>MAX_FILES:
                failures.append("FILE_COUNT_LIMIT")
                break
        if len(actual)>MAX_FILES:
            break
    if len(set(actual))!=len(actual) or set(actual)!=set(ids):
        failures.append("POPULATION_MISMATCH")
    observed=set(actual)
    for e in expected:
        rel=e["path"]
        if not isinstance(rel,str) or not rel or rel.startswith("/") or "\\" in rel or ":" in rel or any(x in ("..",".","") for x in rel.split("/")):
            failures.append("INVALID_PATH")
            continue
        if rel not in observed:
            continue
        try:
            values=_object_hash(root/rel)
            for key in ("git_blob_sha1","sha256","byte_length"):
                if values[key]!=e[key]:
                    failures.append("MISMATCH:"+key+":"+rel)
        except (ValueError,OSError) as exc:
            failures.append("READ_ERROR:"+type(exc).__name__+":"+rel)
    return {"decision":"FAIL" if failures else "PASS_BOUNDED","errors":sorted(set(failures)),
            "expected_count":len(ids),"observed_count":len(actual),
            "scope":"FILESYSTEM_BYTES_VS_DECLARED_MANIFEST_ONLY",
            "git_tree_authenticity_verified":False,"snapshot_provenance_verified":False}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--manifest",required=True)
    a=p.parse_args(argv)
    try:
        m=json.loads(pathlib.Path(a.manifest).read_text(encoding="utf-8"))
        result=audit(a.root,m)
    except (ValueError,OSError) as exc:
        result={"decision":"FAIL","errors":["INPUT_ERROR:"+type(exc).__name__]}
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return 0 if result["decision"]=="PASS_BOUNDED" else 2

if __name__=="__main__":
    sys.exit(main())
