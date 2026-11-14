"""Read-only branch census adverse fixture tests; never connect to GitHub."""
import copy
import unittest
from unittest.mock import patch

from scripts.cko_branch_census import (
    CensusHold, api_json, classify_pair, classify_paths, delta, fingerprint,
    get_all, get_tree, scan,
)


class BranchCensusTests(unittest.TestCase):
    def test_delta_includes_add_remove_and_change(self):
        self.assertEqual(delta({"a": "1", "b": "1"}, {"a": "2", "c": "3"}),
                         {"a": ("MODIFIED", "2"), "b": ("REMOVED", None),
                          "c": ("ADDED", "3")})

    def test_identical_diffs_have_same_fingerprint(self):
        a = {"z": ("MODIFIED", "sha-z"), "a": ("ADDED", "sha-a")}
        b = {"a": ("ADDED", "sha-a"), "z": ("MODIFIED", "sha-z")}
        self.assertEqual(fingerprint(a), fingerprint(b))
        b["z"] = ("MODIFIED", "different")
        self.assertNotEqual(fingerprint(a), fingerprint(b))

    def test_matching_path_is_not_equal_if_blob_differs(self):
        a = {"a": ("MODIFIED", "111"), "b": ("ADDED", "aaa")}
        b = {"a": ("MODIFIED", "222"), "b": ("ADDED", "aaa")}
        compare = classify_pair(a, b)
        self.assertFalse(compare["same_delta"])
        self.assertEqual(compare["shared_paths"], 2)
        self.assertEqual(compare["conflicting_change_paths"], 1)
        self.assertEqual(compare["conflicting_path_sample"], ["a"])

    def test_strict_subset_requires_same_blob(self):
        a = {"a": ("ADDED", "1")}
        b = {"a": ("ADDED", "1"), "b": ("ADDED", "2")}
        self.assertTrue(classify_pair(a, b)["left_subset_right"])
        b["a"] = ("ADDED", "WRONG")
        self.assertFalse(classify_pair(a, b)["left_subset_right"])

    def test_critical_and_sensitive_paths_are_distinct(self):
        c = {
            "packages/cli/kernel/core.py": ("MODIFIED", "a"),
            "config/.env.production": ("ADDED", "b"),
            "docs/README.md": ("MODIFIED", "c"),
        }
        got = classify_paths(c)
        self.assertEqual(got["critical_path_count"], 1)
        self.assertEqual(got["sensitive_path_count"], 1)

    def test_failed_request_has_no_anonymous_fallback(self):
        with self.assertRaises(CensusHold):
            api_json("repo/name", "", "branches")
        with self.assertRaises(CensusHold):
            api_json("bad repo/path", "token", "branches")

    def test_open_pr_pagination_uses_ampersand(self):
        with patch("scripts.cko_branch_census.api_json", return_value=[]) as fake:
            get_all("Org/repo", "token", "pulls?state=open&sort=updated")
            self.assertIn("&per_page=100&page=1", fake.call_args.args[-1])
            self.assertNotIn("?per_page", fake.call_args.args[-1])

    def test_truncated_tree_rejected_not_clean(self):
        with patch("scripts.cko_branch_census.api_json",
                   return_value={"truncated": True, "tree": []}):
            with self.assertRaises(CensusHold):
                get_tree("Org/repo", "token", "a" * 40)

    def test_duplicate_tree_path_rejected(self):
        record = {"type": "blob", "path": "a.json", "sha": "x" * 40}
        with patch("scripts.cko_branch_census.api_json",
                   return_value={"truncated": False, "tree": [record, record]}):
            with self.assertRaises(CensusHold):
                get_tree("Org/repo", "token", "a" * 40)

    def test_scan_reports_same_delta_without_merging(self):
        main = {"name": "main", "commit": {"sha": "a" * 40}}
        left = {"name": "cursor/one", "commit": {"sha": "b" * 40}}
        right = {"name": "cursor/two", "commit": {"sha": "c" * 40}}
        base = {"packages/cli/main.py": "1", "README.md": "2"}
        after = {"packages/cli/main.py": "3", "README.md": "2"}
        def mocked_tree(repo, token, sha):
            return base if sha == "a"*40 else after
        with patch("scripts.cko_branch_census.get_all",
                   side_effect=[[left, main, right], [{
                       "number": 1, "state": "open", "draft": True,
                       "head": {"ref": "cursor/one", "sha": "b"*40},
                       "base": {"ref": "main"}
                   }]]), \
             patch("scripts.cko_branch_census.get_tree",
                   side_effect=mocked_tree), \
             patch("scripts.cko_branch_census.get_comparison",
                   return_value={"relation_to_main": "ahead",
                                 "ahead_by": 1, "behind_by": 0,
                                 "merge_base_sha": "a"*40,
                                 "compare_files_are_complete": False}):
            catalog = scan("Org/repo", "token")
        self.assertEqual(catalog["counts"]["branches"], 3)
        self.assertEqual(catalog["counts"]["exact_duplicate_delta_groups"], 1)
        self.assertEqual(catalog["counts"]["cursor_open_prs"], 1)
        self.assertFalse(catalog["promotion_allowed"])
        self.assertFalse(catalog["delete_allowed"])
        self.assertEqual(catalog["exact_delta_groups"], [["cursor/one", "cursor/two"]])


if __name__ == "__main__":
    unittest.main()
