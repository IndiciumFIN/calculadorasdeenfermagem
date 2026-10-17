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
