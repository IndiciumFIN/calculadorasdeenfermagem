import copy
import unittest
from ce_p1_pinned_tree_guard import check

C="a"*40
T="b"*40
B="c"*40
COMMIT={"sha":C,"tree":{"sha":T}}
TREE={"sha":T,"truncated":False,"tree":[{"path":"folder/a.txt","sha":B,"mode":"100644","type":"blob"},{"path":"folder","mode":"040000","type":"tree"}]}
MAN={"commit_sha":C,"tree_sha":T,"blobs":[{"path":"folder/a.txt","sha":B}]}

class GitTreeTests(unittest.TestCase):
    def case(self,c=None,t=None,m=None):
        return check(copy.deepcopy(c or COMMIT),copy.deepcopy(t or TREE),copy.deepcopy(m or MAN))
    def test_pass_delimited(self):
        x=self.case()
        self.assertEqual(x["decision"],"PASS_BOUNDED")
        self.assertFalse(x["independent_source_census_proven"])
    def test_wrong_commit(self):
        c=dict(COMMIT,sha="d"*40)
        self.assertIn("COMMIT_IDENTITY_MISMATCH",self.case(c=c)["errors"])
    def test_wrong_commit_tree(self):
        c=dict(COMMIT,tree={"sha":"e"*40})
        self.assertIn("COMMIT_TREE_MISMATCH",self.case(c=c)["errors"])
    def test_wrong_tree(self):
        t=dict(TREE,sha="e"*40)
        self.assertIn("TREE_IDENTITY_MISMATCH",self.case(t=t)["errors"])
    def test_truncated(self):
        t=dict(TREE,truncated=True)
        self.assertIn("TREE_TRUNCATED_OR_UNKNOWN",self.case(t=t)["errors"])
    def test_missing_blob(self):
        m=dict(MAN,blobs=[])
        self.assertIn("POPULATION_MISMATCH",self.case(m=m)["errors"])
    def test_blob_changed(self):
        t=copy.deepcopy(TREE);t["tree"][0]["sha"]="e"*40
        self.assertIn("GIT_BLOB_MISMATCH:folder/a.txt",self.case(t=t)["errors"])
    def test_symlink(self):
        t=copy.deepcopy(TREE);t["tree"][0]["mode"]="120000"
        self.assertIn("SYMLINK_BLOB_PRESENT",self.case(t=t)["errors"])
    def test_duplicate_manifest(self):
        m=dict(MAN,blobs=MAN["blobs"]*2)
        self.assertIn("DUPLICATE_EXPECTED_PATH",self.case(m=m)["errors"])
    def test_invalid_path(self):
        m=dict(MAN,blobs=[{"path":"../escape","sha":B}])
        self.assertIn("INVALID_EXPECTED_PATH",self.case(m=m)["errors"])
    def test_unexpected_git_entry_type(self):
        t=copy.deepcopy(TREE);t["tree"].append({"path":"submodule","type":"commit","sha":"d"*40,"mode":"160000"})
        self.assertIn("UNEXPECTED_GIT_ENTRY_TYPE",self.case(t=t)["errors"])
    def test_surprise_seeded_blob_mutations(self):
        import random
        rnd=random.Random(20261019)
        for _ in range(50):
            t=copy.deepcopy(TREE)
            t["tree"][0]["sha"]=format(rnd.getrandbits(160),"040x")
            self.assertEqual(self.case(t=t)["decision"],"FAIL")
if __name__=="__main__":
    unittest.main()
