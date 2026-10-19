#!/usr/bin/env python3
"""Pinned Git commit -> tree -> independent expected blob manifest verifier."""
import argparse
import json
import pathlib
import re
import sys

HEX40=re.compile(r"^[0-9a-f]{40}$")
def check(commit,tree,manifest):
    errors=[]
    expected_commit=manifest.get("commit_sha")
    expected_tree=manifest.get("tree_sha")
    if not isinstance(expected_commit,str) or not HEX40.fullmatch(expected_commit):
        errors.append("INVALID_PINNED_COMMIT")
    if not isinstance(expected_tree,str) or not HEX40.fullmatch(expected_tree):
        errors.append("INVALID_PINNED_TREE")
    if commit.get("sha")!=expected_commit:
        errors.append("COMMIT_IDENTITY_MISMATCH")
    if not isinstance(commit.get("tree"),dict) or commit["tree"].get("sha")!=expected_tree:
        errors.append("COMMIT_TREE_MISMATCH")
    if tree.get("sha")!=expected_tree:
        errors.append("TREE_IDENTITY_MISMATCH")
    if tree.get("truncated") is not False:
        errors.append("TREE_TRUNCATED_OR_UNKNOWN")
    entries=tree.get("tree")
    expected=manifest.get("blobs")
    if not isinstance(entries,list) or not isinstance(expected,list):
        return {"decision":"FAIL","errors":sorted(set(errors+["MALFORMED_COLLECTION"]))}
    if any(not isinstance(x,dict) or x.get("type") not in ("tree","blob") for x in entries):
        errors.append("UNEXPECTED_GIT_ENTRY_TYPE")
    actual=[x for x in entries if isinstance(x,dict) and x.get("type")=="blob"]
    if any(not isinstance(x.get("path"),str) or not x.get("path") or x["path"].startswith("/") or "\\" in x["path"] or any(z in (".","..","") for z in x["path"].split("/")) for x in actual):
        errors.append("INVALID_TREE_PATH")
    paths=[x.get("path") for x in actual]
    wants=[x.get("path") for x in expected if isinstance(x,dict)]
    if len(wants)!=len(expected) or len(set(wants))!=len(wants):
        errors.append("DUPLICATE_EXPECTED_PATH")
    if len(paths)!=len(set(paths)):
        errors.append("DUPLICATE_GIT_PATH")
    if set(paths)!=set(wants):
        errors.append("POPULATION_MISMATCH")
    index={x.get("path"):x for x in actual}
    for e in expected:
        if not isinstance(e,dict):
            errors.append("INVALID_EXPECTED_OBJECT")
            continue
        p=e.get("path")
        sha=e.get("sha")
        if not isinstance(p,str) or not p or p.startswith("/") or "\\" in p or any(x in (".","..","") for x in p.split("/")):
            errors.append("INVALID_EXPECTED_PATH")
            continue
        if not isinstance(sha,str) or not HEX40.fullmatch(sha):
            errors.append("INVALID_EXPECTED_HASH:"+p)
        item=index.get(p)
        if item:
            if item.get("sha")!=sha:
                errors.append("GIT_BLOB_MISMATCH:"+p)
            if item.get("mode") not in ("100644","100755"):
                errors.append("UNEXPECTED_GIT_MODE:"+p)
    if any(x.get("mode")=="120000" for x in actual):
        errors.append("SYMLINK_BLOB_PRESENT")
    return {"decision":"FAIL" if errors else "PASS_BOUNDED",
            "errors":sorted(set(errors)),"actual_blob_count":len(actual),
            "expected_blob_count":len(expected),
            "scope":"PINNED_GIT_API_OBJECT_CONSISTENCY_ONLY",
            "independent_source_census_proven":False,
            "remote_response_authenticated_outside_cli":False}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--commit-json",required=True)
    p.add_argument("--tree-json",required=True)
    p.add_argument("--manifest",required=True)
    args=p.parse_args(argv)
    try:
        files=[json.loads(pathlib.Path(x).read_text(encoding="utf-8")) for x in
               (args.commit_json,args.tree_json,args.manifest)]
        result=check(*files)
    except (OSError,ValueError,TypeError) as exc:
        result={"decision":"FAIL","errors":["INPUT_ERROR:"+type(exc).__name__]}
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return 0 if result["decision"]=="PASS_BOUNDED" else 2

if __name__=="__main__":
    sys.exit(main())
