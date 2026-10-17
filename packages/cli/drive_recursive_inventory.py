"""Deterministic, read-only Google Drive metadata crawler.

Discovery only: no bytes downloaded, no ZIP unpacking, no deduplication, no publication.
Requires DRIVE_ACCESS_TOKEN in environment. Output is not a Kernel-approved inventory
until registered by a qualified Work Order and independently checked.
"""
import argparse
import json
import os
import sys
from collections import deque
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://www.googleapis.com/drive/v3/files"
FIELDS = "nextPageToken,files(id,name,mimeType,size,md5Checksum,modifiedTime,parents,trashed)"
FOLDER = "application/vnd.google-apps.folder"


def list_page(folder_id, token, page_token=None):
    params = {"q": f"'{folder_id}' in parents and trashed = false",
              "fields": FIELDS, "pageSize": "1000",
              "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"}
    if page_token:
        params["pageToken"] = page_token
    req = Request(API + "?" + urlencode(params),
                  headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    with urlopen(req, timeout=45) as response:
        return json.load(response)


def crawl(roots, token, fetch=list_page, max_folders=100000, max_items=2000000):
    """Fail closed on API errors, loops, truncation, missing IDs or quota limits."""
    if not roots or len({r["id"] for r in roots}) != len(roots):
        raise ValueError("roots must be nonempty and unique")
    # Cache each physical folder's API listing once, but preserve every root path.
    queue = deque((root["id"], root["id"], "", (root["id"],)) for root in roots)
    cache = {}
    overlaps = []
    items = []
    memberships = {}
    unique_objects = set()
    while queue:
        root_id, folder_id, relative, ancestry = queue.popleft()
        if folder_id not in cache:
            if len(cache) >= max_folders:
                raise ValueError("folder limit exceeded; inventory incomplete")
            collected = []
            page_token = None
            tokens_seen = set()
            while True:
                page = fetch(folder_id, token, page_token)
                if not isinstance(page, dict) or not isinstance(page.get("files"), list):
                    raise ValueError("missing files list")
                collected.extend(page["files"])
                nxt = page.get("nextPageToken")
                if not nxt:
                    break
                if nxt in tokens_seen:
                    raise ValueError("repeated pagination token")
                tokens_seen.add(nxt)
                page_token = nxt
            seen_ids = set()
            seen_names = set()
            for obj in collected:
                if not isinstance(obj, dict) or not obj.get("id") or not obj.get("name"):
                    raise ValueError("incomplete Drive metadata")
                if obj["id"] in seen_ids or obj["name"] in seen_names:
                    raise ValueError("duplicate folder entry id/name; inventory ambiguous")
                seen_ids.add(obj["id"])
                seen_names.add(obj["name"])
            cache[folder_id] = collected
        prior = memberships.setdefault(folder_id, set())
        if prior and root_id not in prior:
            overlaps.append({"folder_id": folder_id, "first_root_id": sorted(prior)[0],
                             "also_reached_from_root_id": root_id, "path": relative})
        prior.add(root_id)
        for obj in cache[folder_id]:
            if not isinstance(obj, dict) or not obj.get("id") or not obj.get("name") or not obj.get("mimeType"):
                raise ValueError("incomplete Drive metadata")
            name = obj["name"]
            if "/" in name or name in (".", ".."):
                raise ValueError("ambiguous Drive filename")
            rel = relative + "/" + name if relative else name
            obj_id = obj["id"]
            if obj_id not in unique_objects:
                if len(unique_objects) >= max_items:
                    raise ValueError("item limit exceeded; inventory incomplete")
                unique_objects.add(obj_id)
            record = {"root_id": root_id, "parent_id": folder_id,
                      "id": obj_id, "path": rel, "mime_type": obj["mimeType"],
                      "size_bytes": int(obj["size"]) if obj.get("size") is not None else None,
                      "md5_provider": obj.get("md5Checksum"),
                      "modified_time": obj.get("modifiedTime"),
                      "sha256": None, "hash_status": "BYTES_NOT_ACQUIRED",
                      "is_zip_candidate": name.lower().endswith(".zip"),
                      "kind": "folder" if obj["mimeType"] == FOLDER else "file"}
            items.append(record)
            if obj["mimeType"] == FOLDER:
                if obj_id in ancestry:
                    raise ValueError("unexpected folder cycle/overlap: " + obj_id)
                queue.append((root_id, obj_id, rel, ancestry + (obj_id,)))
    return {"schema": "CE-DRIVE-RECURSIVE-METADATA-1.0.0",
            "status": "COLLECTED_NOT_KERNEL_APPROVED",
            "complete_pagination": True, "roots": roots,
            "folders_traversed": len(cache), "items_count": len(items),
            "unique_objects_count": len(unique_objects),
            "root_memberships": {k: sorted(v) for k, v in sorted(memberships.items())},
            "overlapping_folder_references": overlaps,
            "root_membership_status": "RECONCILED_BY_ROOT_PATH" if overlaps else "NO_OVERLAPS_DETECTED",
            "items": sorted(items, key=lambda x: (x["root_id"], x["path"], x["id"])),
            "restrictions": ["NO_DELETE", "NO_PUBLICATION", "NO_DEDUP_WITHOUT_SHA256",
                             "ZIP_CONTENTS_NOT_INSPECTED", "RIGHTS_GATE_REQUIRED"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", required=True, help="JSON file containing roots array")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    token = os.environ.get("DRIVE_ACCESS_TOKEN")
    if not token:
        parser.error("DRIVE_ACCESS_TOKEN required")
    roots_doc = json.loads(Path(args.roots).read_text(encoding="utf-8"))
    roots = roots_doc["roots"]
    if not roots or len({r["id"] for r in roots}) != len(roots):
        parser.error("roots must be nonempty and unique")
    result = crawl(roots, token)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(target)
    print(f"METADATA_ONLY items={result['items_count']} folders={result['folders_traversed']} NOT_KERNEL_APPROVED")


if __name__ == "__main__":
    main()
