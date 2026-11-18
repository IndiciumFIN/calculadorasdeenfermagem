# CE / CKO / NCOS — checkpoint 2026-11-18 02:54 BRT

## Scope
GitHub IndiciumFIN/calculadorasdeenfermagem, audit/ce-supabase-migration-first-20261115; Supabase Calculadoras-Smart pgsybzggewhinaniybiy SELECT only. No Neon, SOT, WU-TRIB, DDL/DML, migration, seed, deploy, merge, branch deletion or candidate promotion. All clinical/legal/security/LGPD/copyright/provenance gates fail-closed.

## New verified delta
The export manifest was previously searched as lowercase manifest.json (404). The canonical file is uppercase `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json`, fetched successfully, blob SHA `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`, observation 2026-11-15, 22 source files, NON_ATOMIC_ACROSS_QUERIES, HOLD_HUMAN. Its coverage reports 59 schemas, 678 relations, 255 migration versions, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. This is metadata extraction, not full dump, atomic snapshot or homologation. README blob `a0e074bf9da401a3d50dd761536bcad3a9b96150` confirms limitations. Individual 22 source-file hashes NOT revalidated this round.

CATMAT source contract blob `fd9b62b9e9ca7e9335e1eb71b23b842a93573a28` equals the parser-integration branch blob, and policy 013 blob `1a1d144fd965833ee90d56acea6b8bb4c63b3c0f` requires exactly schema_validator and catmat_validator. No delta; fingerprint reused, not reprocessed.

Workflow runs for correction commit `ca325d75dd53c024551741e180f072d74dfa6458`: provenance 44240351572 PASS, pipeline 44240351582 PASS, validation 44240351690 PASS, canonical 44240351681 FAIL. Canonical jobs 134586448195 and 134586448467 FAIL, respectively canonical source/policy references and unresolved parser/import dependencies. Deterministic negative tests PASS, compilation PASS; CLI and registry smoke SKIPPED. No new test run initiated.

Supabase SELECT pg_constraint on cko_governance.artifact_normative_bindings returned 4 constraints: artifact_id FK ON DELETE CASCADE, artifact_version_ref FK, UNIQUE (artifact_version_ref,normative_ref,binding_role), PK(binding_id). No change evidenced in these selected definitions; provenance retention remains HOLD_HUMAN.

## Work orders and object ledger
| WO | Object / fingerprint | Delta | Status / risk | Test | Responsible / next action | Acceptance |
|---|---|---|---|---|---|---|
| CE-EXPORT-MANIFEST | MANIFEST.json blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14 | Corrected path casing; recovered canonical inventory metadata | PASS_READ / medium | GitHub fetch PASS; 22 underlying hashes NOT_RUN | CE audit: run verify_supabase_snapshot.py and validate each blob | 22/22 hashes and records match; no sensitive export |
| CE-CATMAT-013 | catmat.json blob fd9b62b9e9ca7e9335e1eb71b23b842a93573a28; policy 013 blob 1a1d144fd965833ee90d56acea6b8bb4c63b3c0f | No delta from prior checkpoint | PASS_CODE / HOLD_CI, medium | 2 branch blobs match; current canonical CI FAIL | CE engineering: isolate remaining contracts | Strict verifier and adversarial tests PASS |
| CE-CI-73 | commit ca325d75dd53c024551741e180f072d74dfa6458 | Four runs retrieved; 3 PASS, 1 FAIL | FAIL_CI / high | canonical run 44240351681 two failed jobs | CE engineering: inspect job logs and remediate actual discrepancies | All required jobs PASS on current PR HEAD |
| CE-DB-PROVENANCE | cko_governance.artifact_normative_bindings, four constraint definitions | No observed delta | HOLD_HUMAN / high | SELECT PASS_READ | Legal/clinical data steward: evaluate CASCADE retention | Approved provenance policy and rollback |
| CE-TOOLS-24 | feat/ce-tools-governed-backend-20261115 | Not refreshed | HOLD_VERIFY / high | NOT_RUN | CE engineering: verify 24 tools and SHA | 24/24 gated and tested |
| CE-METAMODEL | feat/cko-catalog-metamodel-automated-20261114 | Not refreshed | HOLD_VERIFY / high | NOT_RUN | CKO ontology: reconcile PK/FK dictionary | Zero unresolved semantic conflicts |
| CE-CORPUS | feat/cko-m08-m09-corpus-atomic-20261114 | Not refreshed | HOLD_VERIFY / high | NOT_RUN | CKO content: license/provenance audit | All admitted atoms traceable |
| CE-PARSERS | integration/cko-parsers-catalog-20261114 | CATMAT parity confirmed; others not refreshed | HOLD_VERIFY / high | 16 parsers and 5 imports historical unresolved; no fresh enumeration | CE engineering: compare and smoke test | Zero unresolved dependencies |
| CE-WORKSPACE-71 | IndiciumFIN/dev-chatgpt-workspace PR #71 | Not refreshed | HOLD_VERIFY / high | NOT_RUN | Workspace owner: diagnose CI | Required checks PASS |

## Quantitative controls
- Export manifest located: 1/1 PASS_READ; source blobs validated against manifest this round 0/22 NOT_RUN.
- CATMAT two branch variants compared: 2/2 equal; strict CI approval 0/1 (FAIL).
- Four workflow runs for specified correction commit: 3/4 PASS (75%), 1/4 FAIL.
- Canonical failed jobs inspected: 2/2 by steps (100% inspection, not remediation).
- Physical constraints inspected: 4/4 PASS_READ; historical export comparison 5/1996 (0.25%) not revalidated.
- Clinical tools: 0/24 historically homologated, not revalidated. Parsers 0/16 and imports 0/5 corrected this round.
- PR #73 HEAD and workspace PR #71 HEAD NOT_VERIFIED; no claim of merge readiness.
- Global completion estimate: NOT ESTIMABLE without complete acceptance denominator. Counts are inventory, not homologation.

## Next steps
Check PR #73 current HEAD, extract canonical job logs, repair next demonstrable source/policy mismatch, run local/adversarial tests and CI; compare parser imports; validate 22 manifest blobs; reconcile physical SQL/code/dictionary/atoms via SELECT only. Independent HOLD tasks continue. No merge until explicit authorization and full gates.
