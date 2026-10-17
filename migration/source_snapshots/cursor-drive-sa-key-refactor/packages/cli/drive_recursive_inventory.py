"""Recursive read-only Drive inventory — no write, no delete, no publish."""
import argparse
import json
import os
from collections import deque
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://www.googleapis.com/drive/v3/files"
FIELDS = "nextPageToken,files(id,name,mimeType,size,md5Checksum,modifiedTime,parents,trashed)"
FOLDER = "application/vnd.google-apps.folder"
SCOPE_READONLY = "https://www.googleapis.com/auth/drive.readonly"


class CredentialError(RuntimeError):
    """Raised when neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is available."""
    pass


def _build_sa_refresher(sa_key_json):
    """Build a token-refresher for a Google service-account key (JSON)."""
    try:
        info = json.loads(sa_key_json)
    except json.JSONDecodeError as exc:
        raise CredentialError(
            f"GDRIVE_SA_KEY is set but is not valid JSON: {exc}"
        ) from exc
    if not isinstance(info, dict) or "client_email" not in info or "private_key" not in info:
        raise CredentialError(
            "GDRIVE_SA_KEY is missing required service-account fields "
            "('client_email' and 'private_key' are mandatory)."
        )
    try:
        from google.oauth2 import service_account  # noqa: F401
        import google.auth.transport.requests as g_requests
    except ImportError as exc:
        raise CredentialError(
            "GDRIVE_SA_KEY is set but google-auth is not installed. "
            "Add 'google-auth' to packages/cli/requirements.txt and reinstall."
        ) from exc
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=[SCOPE_READONLY]
    )
    request = g_requests.Request()

    def refresh():
        creds.refresh(request)
        if not creds.token:
            raise CredentialError(
                "GDRIVE_SA_KEY refresh returned no token; "
                "check the service account's IAM and Drive sharing."
            )
        return creds.token

    try:
        refresh()
    except CredentialError:
        raise
    except Exception as exc:
        raise CredentialError(
            f"GDRIVE_SA_KEY is configured but the initial refresh failed: {exc}"
        ) from exc
    return refresh


def load_token():
    """Return a callable that yields a valid Drive access token.

    Resolution order:
      1. GDRIVE_SA_KEY  → callable that auto-refreshes via service-account
      2. DRIVE_ACCESS_TOKEN → static callable (manual rotation required)
      3. neither → CredentialError (fail-closed)
    """
    sa_key = os.environ.get("GDRIVE_SA_KEY")
    if sa_key:
        return _build_sa_refresher(sa_key)
    bearer = os.environ.get("DRIVE_ACCESS_TOKEN")
    if bearer:
        return lambda: bearer
    raise CredentialError(
        "Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed."
    )


def _resolve(token):
    """Coerce token to a no-arg callable."""
    if callable(token):
        return token
    if isinstance(token, str):
        return lambda: token
    raise TypeError(
        f"token must be a string or a callable, got {type(token).__name__}"
    )


def list_page(folder_id, token, page_token=None):
    """Fetch one page of Drive children for folder_id.

    token: string or callable returning a Bearer string.
    """
    get_token = _resolve(token)
    params = {
        "q": f"'{folder_id}' in parents and trashed = false",
        "fields": FIELDS,
        "pageSize": "1000",
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    }
    if page_token:
        params["pageToken"] = page_token
    req = Request(
        API + "?" + urlencode(params),
        headers={"Authorization": "Bearer " + get_token(), "Accept": "application/json"},
    )
    with urlopen(req, timeout=45) as response:
        return json.load(response)


def crawl(roots, token, fetch=None, max_folders=100_000, max_items=2_000_000):
    """Recursively collect Drive object metadata for each root.

    Arguments
    ---------
    roots : list[dict]
        [{"id": "<drive-id>", "name": "<display-name>"}, ...]
    token : str | callable | None
        Passed through to fetch().  When None the process-level environment
        is consulted (load_token()).
    fetch : callable | None
        Override for list_page — used by tests.
    max_folders : int
        Hard cap on unique folders visited.
    max_items : int
        Hard cap on unique objects collected.

    Returns
    -------
    dict  — CE-DRIVE-RECURSIVE-METADATA-1.0.0 schema
    """
    if fetch is None:
        fetch = list_page
    get_token = _resolve(token)
    if not roots or len({r["id"] for r in roots}) != len(roots):
        raise ValueError("roots must be nonempty and unique")

    queue = deque((root["id"], root["id"], "", (root["id"],)) for root in roots)
    cache: dict[str, list] = {}
    overlaps: list[dict] = []
    items: list[dict] = []
    memberships: dict[str, set] = {}
    unique_objects: set[str] = set()

    while queue:
        root_id, folder_id, relative, ancestry = queue.popleft()

        # --- fetch + cache folder children ---
        if folder_id not in cache:
            if len(cache) >= max_folders:
                raise ValueError("folder limit exceeded; inventory incomplete")
            collected: list = []
            page_token: str | None = None
            tokens_seen: set = set()
            while True:
                page = fetch(folder_id, get_token, page_token)
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

            # Validate each entry
            seen_ids: set = set()
            for obj in collected:
                if not isinstance(obj, dict) or not obj.get("id") or not obj.get("name"):
                    raise ValueError("incomplete Drive metadata")
                if obj["id"] in seen_ids:
                    raise ValueError("duplicate folder entry id; inventory ambiguous")
                seen_ids.add(obj["id"])
            cache[folder_id] = collected

        # --- track root membership (for overlap detection) ---
        prior = memberships.setdefault(folder_id, set())
        if prior and root_id not in prior:
            overlaps.append({
                "folder_id": folder_id,
                "first_root_id": sorted(prior)[0],
                "also_reached_from_root_id": root_id,
                "path": relative,
            })
        prior.add(root_id)

        # --- emit one record per child ---
        for obj in cache[folder_id]:
            if not (isinstance(obj, dict) and obj.get("id") and obj.get("name") and obj.get("mimeType")):
                raise ValueError("incomplete Drive metadata")

            name = obj["name"]
            if "/" in name or name in (".", ".."):
                raise ValueError("ambiguous Drive filename")

            rel = (relative + "/" + name) if relative else name
            obj_id = obj["id"]

            if obj_id not in unique_objects:
                if len(unique_objects) >= max_items:
                    raise ValueError("item limit exceeded; inventory incomplete")
                unique_objects.add(obj_id)

            record = {
                "root_id": root_id,
                "parent_id": folder_id,
                "id": obj_id,
                "path": rel,
                "mime_type": obj["mimeType"],
                "size_bytes": int(obj["size"]) if obj.get("size") is not None else None,
                "md5_provider": obj.get("md5Checksum"),
                "modified_time": obj.get("modifiedTime"),
                "sha256": None,
                "hash_status": "BYTES_NOT_ACQUIRED",
                "is_zip_candidate": name.lower().endswith(".zip"),
                "kind": "folder" if obj["mimeType"] == FOLDER else "file",
            }
            items.append(record)

            if obj["mimeType"] == FOLDER:
                if obj_id in ancestry:
                    raise ValueError(
                        "unexpected folder cycle/overlap: " + obj_id
                    )
                queue.append((root_id, obj_id, rel, ancestry + (obj_id,)))

    return {
        "schema": "CE-DRIVE-RECURSIVE-METADATA-1.0.0",
        "status": "COLLECTED_NOT_KERNEL_APPROVED",
        "complete_pagination": True,
        "roots": roots,
        "folders_traversed": len(cache),
        "items_count": len(items),
        "unique_objects_count": len(unique_objects),
        "root_memberships": {k: sorted(v) for k, v in sorted(memberships.items())},
        "overlapping_folder_references": overlaps,
        "root_membership_status": (
            "RECONCILED_BY_ROOT_PATH" if overlaps else "NO_OVERLAPS_DETECTED"
        ),
        "items": sorted(items, key=lambda x: (x["root_id"], x["path"], x["id"])),
        "restrictions": [
            "NO_DELETE",
            "NO_PUBLICATION",
            "NO_DEDUP_WITHOUT_SHA256",
            "ZIP_CONTENTS_NOT_INSPECTED",
            "RIGHTS_GATE_REQUIRED",
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Recursively inventory a list of Drive root folders (read-only)."
    )
    parser.add_argument(
        "--roots", required=True, help="JSON file with a 'roots' list of Drive folders."
    )
    parser.add_argument(
        "--output", required=True, help="Path to write the JSON inventory."
    )
    args = parser.parse_args()

    try:
        token_fn = load_token()
    except CredentialError as exc:
        parser.error(str(exc))

    roots_doc = json.loads(Path(args.roots).read_text(encoding="utf-8"))
    roots = roots_doc["roots"]
    if not roots or len({r["id"] for r in roots}) != len(roots):
        parser.error("roots must be nonempty and unique")

    result = crawl(roots, token_fn)

    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(target)
    print(
        f"METADATA_ONLY items={result['items_count']} "
        f"folders={result['folders_traversed']} NOT_KERNEL_APPROVED"
    )


if __name__ == "__main__":
    main()
