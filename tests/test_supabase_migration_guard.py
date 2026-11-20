import json, pathlib, shutil, tempfile, unittest
from scripts.check_supabase_migration_guard import verify,Hold
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Gate(unittest.TestCase):
    def fixture(self):
        obj=tempfile.TemporaryDirectory()
        root=pathlib.Path(obj.name)
        (root/'docs').mkdir()
        (root/'supabase/migrations').mkdir(parents=True)
        shutil.copy(ROOT/'docs/migration-crosswalk-supabase-ce-20261115.json',root/'docs')
        for f in (ROOT/'supabase/migrations').glob('*.sql'):shutil.copy(f,root/'supabase/migrations')
        return obj,root
    def test_current_sources_have_hold(self):
        x=verify()
        self.assertEqual(x['status'],'HOLD_HUMAN')
        self.assertFalse(x['may_apply'])
        self.assertEqual(x['files_checked'],2)
    def test_changed_sql_blocks(self):
        ctx,root=self.fixture()
        with ctx:
            p=root/'supabase/migrations/20261011120000_registry.sql'
            p.write_text(p.read_text()+'\n-- mutated')
            with self.assertRaisesRegex(Hold,'HOLD_SOURCE_CHANGED'):verify(root)
    def test_promotion_blocks(self):
        ctx,root=self.fixture()
        with ctx:
            p=root/'docs/migration-crosswalk-supabase-ce-20261115.json'
            d=json.loads(p.read_text());d['authorization']='APPROVED';p.write_text(json.dumps(d))
            with self.assertRaisesRegex(Hold,'HOLD_UNAPPROVED_PROMOTION'):verify(root)
    def test_unknown_migration_blocks(self):
        ctx,root=self.fixture()
        with ctx:
            (root/'supabase/migrations/20261115000000_new.sql').write_text('select 1;')
            with self.assertRaisesRegex(Hold,'HOLD_MIGRATION_SET_DRIFT'):verify(root)
if __name__=='__main__':unittest.main()
