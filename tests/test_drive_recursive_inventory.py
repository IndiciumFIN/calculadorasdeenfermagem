"""Offline contract tests for read-only recursive Drive discovery."""
import pytest
from packages.cli.drive_recursive_inventory import crawl, FOLDER


def test_recursive_pagination_and_zip_candidate():
    calls = []
    def fetch(folder, token, page_token=None):
        calls.append((folder, page_token))
        if folder == "root" and page_token is None:
            return {"files": [{"id": "sub", "name": "Normativos", "mimeType": FOLDER}],
                    "nextPageToken": "next"}
        if folder == "root" and page_token == "next":
            return {"files": [{"id": "zip", "name": "lote.ZIP", "mimeType": "application/zip", "size": "17"}]}
        return {"files": [{"id": "doc", "name": "norma.pdf", "mimeType": "application/pdf"}]}
    result = crawl([{"id": "root"}], "dummy", fetch=fetch)
    assert result["items_count"] == 3
    assert result["folders_traversed"] == 2
    assert any(x["is_zip_candidate"] and x["sha256"] is None for x in result["items"])
    assert ("root", "next") in calls


def test_repeated_page_token_fails_closed():
    def fetch(folder, token, page_token=None):
        return {"files": [], "nextPageToken": "same"}
    with pytest.raises(ValueError, match="repeated pagination token"):
        crawl([{"id": "root"}], "dummy", fetch=fetch)


def test_missing_metadata_fails_closed():
    with pytest.raises(ValueError, match="incomplete Drive metadata"):
        crawl([{"id": "root"}], "dummy", fetch=lambda *args: {"files": [{"id": "x"}]})


def test_limits_fail_closed():
    with pytest.raises(ValueError, match="item limit exceeded"):
        crawl([{"id": "root"}], "dummy", fetch=lambda *args: {
            "files": [{"id": "x", "name": "x", "mimeType": "text/plain"}]},
            max_items=0)


def test_overlapping_roots_are_recorded_without_double_traversal():
    def fetch(folder, token, page_token=None):
        if folder == "parent":
            return {"files": [{"id": "child", "name": "Child", "mimeType": FOLDER}]}
        return {"files": []}
    result = crawl([{"id": "parent"}, {"id": "child"}], "dummy", fetch=fetch)
    assert result["folders_traversed"] == 2
    assert len(result["overlapping_folder_references"]) == 1
    assert result["overlapping_folder_references"][0]["folder_id"] == "child"


def test_missing_files_collection_fails_closed():
    with pytest.raises(ValueError, match="missing files list"):
        crawl([{"id": "root"}], "dummy", fetch=lambda *args: {})


def test_folder_limit_fails_closed():
    with pytest.raises(ValueError, match="folder limit exceeded"):
        crawl([{"id": "root"}], "dummy", fetch=lambda *args: {"files": []}, max_folders=0)


def test_path_traversal_like_filename_fails_closed():
    with pytest.raises(ValueError, match="ambiguous Drive filename"):
        crawl([{"id": "root"}], "dummy", fetch=lambda *args: {
            "files": [{"id": "bad", "name": "../file", "mimeType": "text/plain"}]})


def test_metadata_never_claims_sha256():
    result = crawl([{"id": "root"}], "dummy", fetch=lambda *args: {
        "files": [{"id": "doc", "name": "source.json", "mimeType": "application/json",
                   "md5Checksum": "0123456789abcdef0123456789abcdef"}]})
    assert result["items"][0]["sha256"] is None
    assert result["items"][0]["hash_status"] == "BYTES_NOT_ACQUIRED"
    assert result["status"] == "COLLECTED_NOT_KERNEL_APPROVED"
    assert "NO_PUBLICATION" in result["restrictions"]


def test_duplicate_registered_roots_fail_closed():
    with pytest.raises(ValueError, match="roots must be nonempty and unique"):
        crawl([{"id": "root"}, {"id": "root"}], "dummy", fetch=lambda *args: {"files": []})


def test_unexpected_cycle_fails_closed():
    def fetch(folder, token, page_token=None):
        return {"files": [{"id": "root", "name": "Back", "mimeType": FOLDER}]}
    with pytest.raises(ValueError, match="unexpected folder cycle/overlap"):
        crawl([{"id": "root"}], "dummy", fetch=fetch)


def test_overlap_requires_provenance_reconciliation():
    def fetch(folder, token, page_token=None):
        return {"files": [{"id": "child", "name": "Child", "mimeType": FOLDER}]} if folder == "parent" else {"files": []}
    result = crawl([{"id": "parent"}, {"id": "child"}], "dummy", fetch=fetch)
    assert result["root_membership_status"] == "RECONCILED_BY_ROOT_PATH"


def test_shared_root_descendants_preserve_both_paths_and_fetch_once():
    calls = []
    def fetch(folder, token, page_token=None):
        calls.append(folder)
        if folder == "parent":
            return {"files": [{"id": "child", "name": "Child", "mimeType": FOLDER}]}
        if folder == "child":
            return {"files": [{"id": "doc", "name": "data.json", "mimeType": "application/json"}]}
        return {"files": []}
    result = crawl([{"id": "parent"}, {"id": "child"}], "dummy", fetch=fetch)
    paths = {(x["root_id"], x["path"]) for x in result["items"] if x["id"] == "doc"}
    assert paths == {("parent", "Child/data.json"), ("child", "data.json")}
    assert calls.count("child") == 1
    assert result["unique_objects_count"] == 2
    assert result["root_memberships"]["child"] == ["child", "parent"]


def test_shared_nonroot_folder_is_not_mistaken_for_cycle():
    def fetch(folder, token, page_token=None):
        if folder == "root":
            return {"files": [{"id": "a", "name": "A", "mimeType": FOLDER},
                              {"id": "b", "name": "B", "mimeType": FOLDER}]}
        if folder in ("a", "b"):
            return {"files": [{"id": "shared", "name": "Shared", "mimeType": FOLDER}]}
        return {"files": [{"id": "doc", "name": "data.txt", "mimeType": "text/plain"}]}
    result = crawl([{"id": "root"}], "dummy", fetch=fetch)
    paths = {x["path"] for x in result["items"] if x["id"] == "doc"}
    assert paths == {"A/Shared/data.txt", "B/Shared/data.txt"}
    assert result["folders_traversed"] == 4


def test_duplicate_paginated_id_fails_closed():
    def fetch(folder, token, page_token=None):
        record = {"id": "same", "name": "same.txt", "mimeType": "text/plain"}
        return {"files": [record], "nextPageToken": "p2"} if page_token is None else {"files": [record]}
    with pytest.raises(ValueError, match="duplicate folder entry"):
        crawl([{"id": "root"}], "dummy", fetch=fetch)


def test_same_name_different_ids_accepted():
    """Same name in the same folder is valid in Google Drive — accepted by ID deduplication only."""
    def fetch(folder, token, page_token=None):
        return {"files": [
            {"id": "a", "name": "x.txt", "mimeType": "text/plain", "size": "10"},
            {"id": "b", "name": "x.txt", "mimeType": "text/plain", "size": "20"},
        ]}
    result = crawl([{"id": "root"}], "dummy", fetch=fetch)
    assert result["items_count"] == 2
    paths = {x["path"] for x in result["items"]}
    assert paths == {"x.txt"}  # both in same root, same relative path
    ids = {x["id"] for x in result["items"]}
    assert ids == {"a", "b"}
    sizes = {x["size_bytes"] for x in result["items"]}
    assert sizes == {10, 20}
