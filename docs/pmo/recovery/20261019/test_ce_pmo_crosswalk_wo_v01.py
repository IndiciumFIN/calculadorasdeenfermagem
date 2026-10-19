"""Read-only metadata reconciliation tests, not Kernel or WO admission."""
import json
import unittest
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
FILE = BASE / "CE_PMO_CROSSWALK_CE04_38_PR2_WO164_20261019_CANDIDATE.json"


class CrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text(encoding="utf-8"))

    def test_counts(self):
        self.assertEqual(38, len(self.data["ce04_tasks"]))
        self.assertEqual(164, len(self.data["pr2_work_orders"]))
        self.assertEqual(0, len(self.data["errors"]))

    def test_unique_ids(self):
        for key, field in (("ce04_tasks", "id"), ("pr2_work_orders", "id"), ("pr2_work_orders", "blob_sha")):
            values = [r[field] for r in self.data[key]]
            self.assertEqual(len(values), len(set(values)))

    def test_38_ce04_not_closed(self):
        self.assertEqual(38, sum(row["closed_at"] is None and row["completion_evidence_count"] == 0 for row in self.data["ce04_tasks"]))

    def test_wo_authority_not_implied(self):
        states = Counter(row["state"] for row in self.data["pr2_work_orders"])
        self.assertEqual(161, states["PREAUTHORIZED"])
        self.assertEqual(3, states["UNSPECIFIED"])
        self.assertNotIn("KERNEL_ADMITTED", states)

    def test_no_conflated_id_namespace(self):
        ids = {row["id"] for row in self.data["ce04_tasks"]}
        self.assertEqual(0, sum(row["task_id"] in ids for row in self.data["pr2_work_orders"]))

    def test_date_groups_not_claimed_as_102_historical(self):
        names = [row["file"] for row in self.data["pr2_work_orders"]]
        self.assertEqual(102, sum(x.startswith("WO-2026_10_15_") for x in names))
        self.assertEqual(59, sum(x.startswith("WO-2026_10_16_") for x in names))
        self.assertEqual(3, sum(not x.startswith("WO-2026_") for x in names))


if __name__ == "__main__":
    unittest.main()
