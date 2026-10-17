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
    queue = deque((root["id"], root["id"], "") for root in roots)
    visited = {}
    overlaps = []
    items = []
    folders_seen = 0
    while queue:
        root_id, folder_id, relative = queue.popleft()
        if folder_id in visited:
            overlaps.append({"folder_id": folder_id, "first_root_id": visited[folder_id],
                             "also_reached_from_root_id": root_id, "path": relative})
            continue
        visited[folder_id] = root_id
        folders_seen += 1
        if folders_seen > max_folders:
            raise ValueError("folder limit exceeded; inventory incomplete")
        page_token = None
        tokens_seen = set()
        while True:
            page = fetch(folder_id, token, page_token)
            if not isinstance(page.get("files"), list):
                raise ValueError("missing files list")
            for obj in page["files"]:
                if not obj.get("id") or not obj.get("name") or not obj.get("mimeType"):
                    raise ValueError("incomplete Drive metadata")
                name = obj["name"]
                if "/" in name or name in (".", ".."):
                    raise ValueError("ambiguous Drive filename")
                rel = relative + "/" + name if relative else name
                record = {"root_id": root_id, "parent_id": folder_id,
                          "id": obj["id"], "path": rel, "mime_type": obj["mimeType"],
                          "size_bytes": int(obj["size"]) if obj.get("size") is not None else None,
                          "md5_provider": obj.get("md5Checksum"),
                          "modified_time": obj.get("modifiedTime"),
                          "sha256": None, "hash_status": "BYTES_NOT_ACQUIRED",
                          "is_zip_candidate": name.lower().endswith(".zip"),
                          "kind": "folder" if obj["mimeType"] == FOLDER else "file"}
                items.append(record)
                if len(items) > max_items:
                    raise ValueError("item limit exceeded; inventory incomplete")
                if obj["mimeType"] == FOLDER:
                    queue.append((root_id, obj["id"], rel))
            nxt = page.get("nextPageToken")
            if not nxt:
                break
            if nxt in tokens_seen:
                raise ValueError("repeated pagination token")
            tokens_seen.add(nxt)
            page_token = nxt
    return {"schema": "CE-DRIVE-RECURSIVE-METADATA-1.0.0",
            "status": "COLLECTED_NOT_KERNEL_APPROVED",
            "complete_pagination": True, "roots": roots,
            "folders_traversed": folders_seen, "items_count": len(items),
            "overlapping_folder_references": overlaps,
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
