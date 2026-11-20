# CE / CKO / NCOS — checkpoint 2026-11-19 11:52 BRT

## Scope and immutable references
- Repository: IndiciumFIN/calculadorasdeenfermagem; PR #73 (DRAFT/NO-GO); branch audit/ce-supabase-migration-first-20261115.
- Baseline prior checkpoint commit: 60307e5fc5f61d0637b5ecb2d1dfdbd5863b02f4.
- Baseline workflow run IDs: 44537810288 (Pipeline PASS), 44537810256 (provenance PASS), 44537810106 (CI validation PASS), 44537810330 (canonical invariants FAIL).
- Failed job IDs: 135607806707 (dependency guard) and 135607807181 (contracts/CLI smoke).
- Manifest docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json blob SHA 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; 22 files; NON_ATOMIC_ACROSS_QUERIES / HOLD_HUMAN.
- Physical source exclusively Supabase Calculadoras-Smart pgsybzggewhinaniybiy. SELECT-only catalog counts: ce_platform=252, cko_governance=264, public=197 constraints; selected total=713. These counts are NOT object-level reconciliation.
- Workspace PR #71: DRAFT.
- CLI files inspected: packages/cli/main.py blob bec5bfa0db972988495dd847c4a4df4c7887a2ee; packages/cli/kernel/cli.py blob 66c9efb6e6e47c228d1a261f82af6b47e53c84c3.

## Delta and admission
- The two jobs remain FAIL; canonical guard returns exit code 2, intentionally fail-closed.
- Guard reports 1 legacy contracts/fonts directory, 16 missing parsers, and namespace/import findings. Do not equate the five historical import findings with five verified unresolved source files: after two prior code edits, guard output must be mapped to exact source lines and checked for stale detection.
- Compile and deterministic negative tests PASS in job 135607807181; CLI and kernel smoke SKIPPED due to earlier guard failure.
- No new object-level semantic matches; historical crosswalk 8/1996 = 0.40% (prior checkpoint only). No fingerprint reprocessing.
- No functional code changes, migration, seed, DDL, DML, merge, branch deletion or candidate publication in this run.

## Work orders / acceptance registry
| WO | Object / fingerprint or SHA | Delta | Status | Risk | Test | Owner / next action | Acceptance |
|---|---|---|---|---|---|---|---|
| CE-CI-01 | run 44537810330, jobs 135607806707/135607807181 | FAIL persists | FAIL | high | compile/negative PASS; smoke SKIPPED | engineering: map each guard finding to current file and fix minimal root cause | guard PASS and smoke PASS on same SHA |
| CE-CLI-02 | main.py bec5bfa0db972988495dd847c4a4df4c7887a2ee; kernel/cli.py 66c9efb6e6e47c228d1a261f82af6b47e53c84c3 | previous edits present; unvalidated smoke | HOLD_HUMAN | high | negative PASS, smoke NOT_RUN | engineering: targeted namespace smoke and test guard detection | imports and negative exits PASS |
| CE-PARSER-03 | integration/cko-parsers-catalog-20261114; 16 expected parser paths | no port this run | FAIL | high | NOT_RUN | engineering: verify source provenance/license and port one-by-one | 16/16 implemented and tested, no stubs |
| CE-TOOLS-04 | feat/ce-tools-governed-backend-20261115; 24 tools | no delta validated | HOLD_HUMAN | clinical | NOT_RUN | clinical/engineering: contract + safety tests | 24/24 accepted |
| CE-META-05 | feat/cko-catalog-metamodel-automated-20261114 | no delta validated | HOLD_HUMAN | high | NOT_RUN | data governance: dictionary/PK/FK crosswalk | complete documented criteria |
| CE-CORPUS-06 | feat/cko-m08-m09-corpus-atomic-20261114 | no delta validated | HOLD_HUMAN | clinical/legal | NOT_RUN | editorial/legal: provenance and licensing | all published atoms source-backed |
| CE-DB-07 | MANIFEST blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; 1996 constraints | physical sample 713 counts unchanged | HOLD_HUMAN | high | SELECT PASS_READ | data engineering: compare individual PK/FK fingerprints without repeat | 1996/1996 with delta records |
| CE-WS-08 | dev-chatgpt-workspace PR #71 | DRAFT | HOLD_HUMAN | medium | NOT_RUN | workspace engineering: independent CI | gated preview/build PASS |
| CE-GOV-09 | PR #73 | draft NO-GO | HOLD_HUMAN | critical | 3/4 workflows PASS | governance: preserve fail-closed | all gates and human approvals |

## Measured coverage (not platform completion)
- Workflow pass: 3/4 (75%) on baseline SHA; global FAIL.
- Historical semantic constraint crosswalk: 8/1996 (0.40%); no new checks.
- Parsers accepted: 0/16; tools accepted: 0/24; import issues independently accepted: 0/5.
- Global completion estimate: NOT_AFFIRMED / denominator not established.
- New commit CI: NOT_RUN at checkpoint creation.
- Primary source: GitHub Actions 2026-11-19, Supabase SELECT 2026-11-19; export observation 2026-11-15.

## Next independent steps
1. Diagnose exact namespace guard findings against current CLI source; distinguish actual import failure from stale static guard.
2. Validate candidate parsers individually against integration branch and add focused tests, not stubs.
3. Continue selective SELECT-only PK/FK crosswalk against export; retain non-atomic snapshot HOLD.
4. Never promote candidate content or mutate physical database without separate authorization, rollback and security assessment.
