# CE/CKO/NCOS — checkpoint 2026-11-17 20:57 BRT

## Scope, authority, and previous checkpoint
- Database sole physical authority: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; one SELECT only. No Neon, SOT, accounting or WU-TRIB.
- Previous checkpoint: `docs/audits/WO_20261117_1957_VERIFIER_BRANCH_SEMANTIC_DELTA.md`, Git blob `9c45b048c4a29c91cd6127293843cea774ae208b`.
- Work branch: `audit/ce-supabase-migration-first-20261115`; no main merge, deployment, migration, DDL/DML, seed or deletion.

## Verified code change (actual commits)
1. `b721fa38b0f6d997e05f28a26e8792e2817a5e16`: replaced `scripts/verify_repository_integrity.py` (old Git blob `f6e74d988cfbe623e4a5f903b555c314482cbf40`) with the reviewed implementation from `integration/cko-parsers-catalog-20261114` (new Git blob `f6d72d91455c530d5bc3f9fbed283b389851b151`; +1044 characters). Adds canonical validator ID regex/uniqueness, source validator schema checks and ordered source-policy parity, preserving fail-closed.
2. `ca9a7830256e39de8b32d0227e11bbc2eaab62a1`: created `tests/test_ce_canonical_validator_parity.py` with five isolated fixture tests (valid structural contract; duplicate policy IDs; invalid policy IDs; duplicate source IDs; mismatched order).
- No validated fingerprint was reprocessed without observed delta. This is a functional change and a regression test addition, **not** a declaration of green tests.
- Query for GitHub Actions runs on test commit returned `[]`; **CI NOT_RUN / NOT_OBSERVED**, not PASS. Local tests NOT_RUN; require `python -m unittest discover -s tests -p 'test_ce_canonical_validator_parity.py' -v` and canonical workflows before merge.

## Supabase SELECT evidence
Read `pg_constraint` via SELECT for `cko_governance.architecture_layer_bindings` and `artifact_normative_bindings`: 5 rows, including triple PK and normative FK `ON DELETE CASCADE`. No schema mutation. Repeated selected records, not new comparison against JSONL. Normative provenance retention remains HOLD_HUMAN.

## Work orders / fingerprint registry
| WO | Object / fingerprint | Delta | Status | Risk | Test / acceptance | Owner and next action |
|---|---|---|---|---|---|---|
| CE-VERIFY-DELTA | verifier blob `f6e74d98` -> `f6d72d91` | canonical validator parity enforced | HOLD_TEST | high | five fixtures PASS; structural/strict CI; no weakening | Engineering: run tests and repair failures |
| CE-VERIFY-TEST | new `tests/test_ce_canonical_validator_parity.py`, commit `ca9a7830` | five fixtures added | NOT_RUN | medium | 5/5 tests PASS on current HEAD | Engineering: execute isolated suite |
| CE-LEGACY-DIR | `contracts/fonts` vs `contracts/fontes` | no new inventory | HOLD_VERIFY | high | enumerate contents and consumers before removal | Engineering |
| CE-PARSER-16 | 16 parser dependencies, prior CI | no new SHA checked | HOLD_VERIFY | high | 16/16 implementation, provenance and smoke | Parsers team |
| CE-IMPORT-5 | 5 import paths, prior CI | no new SHA checked | HOLD_VERIFY | medium | 5/5 import smoke | Engineering |
| CE-DB-PROV | `cko_governance.artifact_normative_bindings` FK | no observed definition delta | HOLD_HUMAN | high | demonstrate retention, rollback idempotence | DB governance |
| CE-PR73 | `IndiciumFIN/calculadorasdeenfermagem` PR #73 | new commits on work branch; HEAD/checks not revalidated | HOLD_CI | high | current HEAD checks green, security review | Engineering |
| CE-PR71 | `IndiciumFIN/dev-chatgpt-workspace` PR #71 | not inspected this round | HOLD_CI | high | resolve PMO regressions and Vercel limits | Workspace team |
| CE-META | `feat/cko-catalog-metamodel-automated-20261114` | not inspected this round | HOLD_VERIFY | high | dictionary/PK/FK parity and semantic dedup | CKO team |
| CE-CORPUS | `feat/cko-m08-m09-corpus-atomic-20261114` | not inspected this round | HOLD_VERIFY | high | source provenance, rights, atomic identity | Content team |
| CE-TOOLS | `feat/ce-tools-governed-backend-20261115` | not inspected this round | HOLD_HUMAN | critical | 24/24 tool gates, clinical validation | Clinical team |

## Measured progress (not homologation)
- Targeted database read: 1/1 SELECT PASS_READ; 5 returned constraints; historical full semantic comparison 5/1996 = 0.25% **not re-run**.
- Verifier parity code port: 1/1 targeted file committed, **HOLD_TEST**.
- Regression test cases authored: 5/5; executed: 0/5, **NOT_RUN**.
- CI workflows on latest test commit: 0 observed; **NOT_RUN/UNKNOWN**.
- Clinical tools: historical 0/24 homologated, not revalidated; parsers 0/16 verified this round; imports 0/5 tested.
- Global completion estimate: **NOT ESTIMABLE**, no consolidated denominator of acceptance criteria.

## Gates and next execution
Run five isolated tests and required CI, inspect fresh PR HEADs, enumerate legacy source directories, reconcile parser/import paths and proceed with independent semantic catalog/export comparisons. Keep candidate unpublished; preserve LGPD, copyright, primary provenance, clinical/legal/security gates. No official external normative sources consulted this round.
