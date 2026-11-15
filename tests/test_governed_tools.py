"""Fail-closed static gates for the incremental, not-yet-deployed backend candidate."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'data/candidates/nursing-needs-v1.4.0.json'
COVERAGE = ROOT / 'data/candidates/reconciliation-coverage-v0.1.0.json'
DDL = (ROOT / 'supabase/candidates/20261115_ce_tools_governed_candidate.sql').read_text()

class GovernedToolsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SEED.read_text())
        cls.coverage = json.loads(COVERAGE.read_text())

    def test_exactly_24_research_demands_without_collisions(self):
        items=self.data['items']; self.assertEqual(24,len(items))
        self.assertEqual(len(items),len({a['capability_key'] for a in items}))
        self.assertEqual(len(items),len({a['slug'] for a in items}))
        self.assertEqual({f'research.nursing.d{i:02d}' for i in range(1,25)},{a['capability_key'] for a in items})

    def test_all_are_nonpublished_and_have_provenance(self):
        for t in self.data['items']:
            self.assertEqual('candidate', t['lifecycle'])
            self.assertEqual('1.4.0',t['provenance']['source_version'])
            self.assertEqual('RESEARCH_CANDIDATE_NOT_APPROVED',t['provenance']['status'])
            self.assertEqual(False,t['payload']['containsPatientData'])
            self.assertIn(t['projection'],['public','subscriber','institutional'])
            self.assertIn(t['risk_level'],['low','medium','high','critical'])
            self.assertTrue(t['payload']['disclaimer'])
            self.assertTrue(all(url.startswith('https://') for url in t['payload']['referenceUrls']))

    def test_reconciled_without_claiming_deduplication(self):
        self.assertEqual(68,len(self.coverage['reused_capability_keys']))
        self.assertEqual(36,len(self.coverage['ux_new_proposals']))
        self.assertEqual(24,len(self.coverage['research_to_existing_candidates']))
        self.assertIn('not a deduplication confirmation',self.coverage['notice'])

    def test_release_gate_in_sql_is_fail_closed(self):
        for clause in ('enable row level security', 'CE_NO_KERNEL_GRANT', 'CE_SOURCE_NOT_REVIEWED',
                       'CE_SHA_MISMATCH', 'CE_SNAPSHOT_MISMATCH', 'CE_RELEASE_IMMUTABLE',
                       'CE_DELETE_FORBIDDEN', 'security_invoker=true', 'kernel_wo_id',
                       'ce_tool_audit', 'ce_tool_revocations', 'CE_REVOCATION_IMMUTABLE', 'not exists(select 1 from public.ce_tool_revocations', 'revoke insert,update,delete on public.ce_tool_releases'):
            self.assertIn(clause,DDL)
        self.assertNotIn('create policy ce_public_releases_insert',DDL)

    def test_public_api_uses_only_releases(self):
        code=(ROOT/'src/lib/ce-tools/db.ts').read_text()
        self.assertIn("from('ce_tool_publications')",code)
        self.assertNotIn('SERVICE_ROLE',code)
        public_page=(ROOT/'src/app/ferramentas/page.tsx').read_text()
        self.assertIn('publicToolList',public_page)
        self.assertNotIn('nursing-needs-v1.4.0.json',public_page)

    def test_no_unsafe_dynamic_eval_in_runner(self):
        code=(ROOT/'src/components/ce-tools/ToolRunner.tsx').read_text()
        self.assertNotIn('dangerouslySetInnerHTML',code)
        self.assertNotIn('eval(',code)
        self.assertNotIn('localStorage',code)
        self.assertNotIn('sessionStorage',code)

    def test_auditor_role_is_explicitly_read_only_at_write_routes(self):
        for route in (
            'src/app/api/admin/ferramentas/route.ts',
            'src/app/api/admin/ferramentas/[key]/route.ts',
            'src/app/api/admin/ferramentas/[key]/enviar-revisao/route.ts',
        ):
            code = (ROOT / route).read_text()
            self.assertIn("['admin','editor'].includes(ctx.role)", code, route)
            self.assertIn("verifyWriteRequest(req)", code, route)
            self.assertNotIn("['admin','editor','auditor'].includes(ctx.role)", code, route)

    def test_actual_body_bytes_limited_on_write_routes(self):
        security=(ROOT/'src/lib/ce-tools/security.ts').read_text()
        self.assertIn('MAX_WRITE_BODY_BYTES = 40_000', security)
        self.assertIn('req.body.getReader()', security)
        self.assertIn('total > MAX_WRITE_BODY_BYTES', security)
        self.assertIn('new WriteBodyTooLargeError()', security)
        self.assertIn("new TextDecoder('utf-8', { fatal: true })", security)
        for route in (
            'src/app/api/admin/ferramentas/route.ts',
            'src/app/api/admin/ferramentas/[key]/route.ts',
        ):
            code=(ROOT/route).read_text()
            self.assertIn('readBoundedJson(req)', code, route)
            self.assertIn('e instanceof WriteBodyTooLargeError', code, route)
            self.assertIn('status:413', code, route)
            self.assertNotIn('req.json()', code, route)

    def test_json_content_type_is_strict_utf8_only(self):
        security=(ROOT/'src/lib/ce-tools/security.ts').read_text()
        self.assertIn("charset", security)
        self.assertIn("utf-8", security)
        self.assertIn("JSON obrigatório (UTF-8)", security)
        self.assertNotIn(".startsWith('application/json')", security)

    def test_seed_does_not_publish(self):
        sql=(ROOT/'supabase/candidates/20261115_ce_tools_research_seed_candidate.sql').read_text().lower()
        self.assertIn('on conflict (capability_key) do nothing',sql)
        self.assertNotIn('insert into public.ce_tool_releases',sql)
        self.assertEqual(24,sql.count('insert into public.ce_tool_drafts'))

if __name__=='__main__': unittest.main()
