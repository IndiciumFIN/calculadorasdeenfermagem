# WO — 2026-11-16 01:53 BRT — regressão fail-closed do gate canônico

## Origem e escopo
- Repo: IndiciumFIN/calculadorasdeenfermagem; branch: audit/ce-supabase-migration-first-20261115 (PR #73).
- Baseline anterior: commit 2154661c2691fb3c2ec1fae859016687f6784bee; run https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43783129926.
- Snapshot: docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json, Git blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; NON_ATOMIC_ACROSS_QUERIES; HOLD_HUMAN.
- Verifier: scripts/verify_repository_integrity.py, Git blob f6e74d988cfbe623e4a5f903b555c314482cbf40.
- New test: tests/test_repository_integrity_fail_closed.py, commit cfee6ee5f4f63db0ee418c057f4f1314c085a471.

## Mudança técnica
Three synthetic, isolated pytest regressions assert that (1) a missing parser remains strict HOLD, (2) legacy contracts/fonts fails structural admission, and (3) resolving a parser cannot silently clear a top-level import namespace HOLD. No validator suppression or production SQL.

## Evidence
- GitHub fetch of MANIFEST and verifier: PASS.
- GitHub creation of regression test: PASS (commit above).
- Supabase project pgsybzggewhinaniybiy: SELECT-only pg_catalog.pg_class confirms cko_governance.change_audit_ledger, change_control_state, controlled_artifacts are ordinary persistent tables (3/3); no schema mutation.
- pytest execution / Actions for new commit: NOT_RUN, not claimed PASS.
- CI blockers inherited: 1 LEGACY_SOURCE_DIR FAIL, 16 MISSING_PARSER HOLD, 5 PACKAGE_IMPORT_NAMESPACE HOLD; 0/22 remediated by this test-only commit.
- Snapshot coverage: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. These are baseline counts, not fresh object-by-object validation.
- Clinical tools homologated: 0/24. Merge: HOLD_HUMAN.

## Incremental registry / next action
| Object | Fingerprint | Last commit | State | Delta | Next action |
|---|---|---|---|---|---|
| scripts/verify_repository_integrity.py | blob f6e74d988cfbe623e4a5f903b555c314482cbf40 | unchanged | FAIL inherited | 0 | Preserve gate, reconcile legacy source directory |
| tests/test_repository_integrity_fail_closed.py | commit cfee6ee5f4f63db0ee418c057f4f1314c085a471 | cfee6ee5 | ADDED / NOT_RUN | +3 cases | Run pytest and inspect Actions |
| packages/cli/parsers | 16 MISSING_PARSER from run 43783129926 | unchanged | HOLD | 0/16 | Compare integration/cko-parsers-catalog-20261114 by code, provenance and licensing |
| packages/cli imports | 5 PACKAGE_IMPORT_NAMESPACE from run 43783129926 | unchanged | HOLD | 0/5 | Import smoke tests, repair namespace without bypass |
| cko_governance selected tables | pg_catalog SELECT 2026-11-16 | database unchanged | PASS metadata | 3/3 existence | Continue PK/FK/privilege and semantic reconciliation |

Rollback for test-only change: revert commit cfee6ee5 on integration branch; no DB rollback required. No merges, migrations, DDL/DML, seeds, or publication. Do not infer release readiness from tests alone.
