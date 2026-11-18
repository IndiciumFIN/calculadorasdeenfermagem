# CE / CKO / NCOS — checkpoint 2026-11-18 04:54 BRT

## Scope and controls
Repository IndiciumFIN/calculadorasdeenfermagem; audit branch audit/ce-supabase-migration-first-20261115. Only physical truth: Supabase Calculadoras-Smart pgsybzggewhinaniybiy. Database queried exclusively with SELECT. No Neon/SOT/accounting, DDL/DML, migration, seed, deploy, merge or branch deletion. All clinical, legal, privacy, security, licensing and provenance gates remain fail-closed; candidates not published.

## Verified delta since 03:57 checkpoint
- Read previous checkpoint WO_20261118_0357_MANIFEST_SHA_CI_CHECKPOINT.md and current MANIFEST.json blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14.
- Independently fetched six **previously unvalidated** export source file blobs; each matches its expected Git blob SHA-1 in MANIFEST.json. Together with three previously verified files, total 9/22 PASS_HASH, 13/22 NOT_RUN. No repeated validation of the previous three.
- New matches: migrations.json 9722cf9bf4b8306f0f386314d0a65f5e9032dccd; relations.json cfe39bc8eb73b91b73eb48867fe5bf777bfbf01a; views.jsonl 0ee0e7fc23b3e2c9bc20c03f7bb8a2ddd641d52e; triggers.jsonl 4d04a9f7e747f223afbf1b912e77ef195f59a817; reference/external-binding-metadata.jsonl 17b2d2b5d2d1d69e6f4e8aa1ca9f0504c0e2409e; reference/clinical-tool-metadata.jsonl 8e40a3caaa5c54125629940199845b1e426bfee0.
- Supabase SELECT pg_constraint confirmed four constraints of cko_governance.artifact_normative_bindings: PK binding_id; UNIQUE (artifact_version_ref,normative_ref,binding_role); FK artifact_version_ref to object_versions; FK artifact_id to controlled_artifacts ON DELETE CASCADE. Cascade retention remains HOLD_HUMAN. No SQL writes.
- No new code correction or test execution this round. Historical canonical CI FAIL remains last known state; no claim of current HEAD CI. PR #73 and workspace PR #71 current HEAD/checks NOT_REVALIDATED.
- Manifest metadata as of 2026-11-15: 59 schemas, 678 relations, 255 migration versions, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies; NON_ATOMIC_ACROSS_QUERIES, HOLD_HUMAN. Inventory is not homologation.

## Versioned work-order ledger
| WO / branch or object | Fingerprint / SHA | Verified delta | Status / risk | Test | Responsible / next action | Acceptance criteria |
|---|---|---|---|---|---|---|
| CE-EXPORT-22 / MANIFEST | 8099e3ff225224eb00e8eb5accd6d8365ddfcf14 | 6 additional SHA matches | PASS_HASH 9/22, medium | 6/6 new Git blob matches | CE audit: validate remaining 13 unverified files | 22/22 hash matches, no secrets |
| CE-DB-PROVENANCE / artifact_normative_bindings | 4 SELECT pg_constraint definitions | No observed scoped delta | PASS_READ / HOLD_HUMAN, high | 4/4 SELECT read | Clinical/legal: decide cascade retention, provenance model | Signed review and tested reversible migration before any DDL |
| CE-CI-73 / audit branch | Previous checkpoint 6d9e3a11d25f41f04efdf83b2d1093e3a6b6b7fd | No CI recheck | FAIL historical / HOLD_VERIFY, high | NOT_RUN this round | Engineering: inspect latest checks and fix proven source/policy errors | Required CI PASS at same HEAD |
| CE-TOOLS-24 / feat/ce-tools-governed-backend-20261115 | HEAD NOT_REVALIDATED | No verified delta | HOLD_VERIFY, high | NOT_RUN | Clinical engineering: compare 24 contracts to catalog | 24/24 evidence-based validations and clinical approvals |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_REVALIDATED | No verified delta | HOLD_VERIFY | NOT_RUN | CKO: PK/FK/dictionary semantic diff | No unexplained semantic mismatch |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_REVALIDATED | No verified delta | HOLD_PROVENANCE | NOT_RUN | Content: verify licensing and atom lineage | Every promoted atom traceable and licensed |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | HEAD NOT_REVALIDATED | 16 parsers and 5 imports historically unresolved | FAIL historical / HOLD_VERIFY | NOT_RUN | Engineering: reconcile parser and import contracts | 0 missing parsers/imports; strict CI PASS |
| CE-WORKSPACE / dev-chatgpt-workspace PR #71 | HEAD NOT_REVALIDATED | No verified delta | HOLD_VERIFY | NOT_RUN | PMO: inspect PR checks | Required checks PASS, no cross-project contamination |

## Layer coverage, not homologation
- Export Git blob fingerprint verification: **9/22 = 40.91%**; 13/22 NOT_RUN.
- Scoped physical constraints: **4/4 SELECT read**, not 4/1996 homologated.
- Prior observed CI: **3/4 workflows PASS**, canonical FAIL; current CI NOT_RUN/NOT_VERIFIED.
- Clinical tools: **0/24 approvals verified in this round**; historical status cannot be promoted.
- Parsers/imports: **0/16 and 0/5 fixes this round**, historical backlog.
- Global estimated completion: **NOT_ESTIMABLE**; acceptance denominator across layers unavailable.

## Next independent tasks
Validate the remaining 13 manifest source SHA fingerprints; inspect current PR #73 and #71 HEAD/checks; run targeted negative tests for validator contracts and parser/import integrity; reconcile candidate SQL with PostgreSQL SELECT metadata without schema writes; preserve HOLD_HUMAN on cascade retention. Do not repeat fingerprints with no delta.

## Change and test ledger
GitHub: one documentation-only checkpoint commit requested. Functional changes: NONE. Git blob SHA comparisons 6/6 PASS. PostgreSQL SELECT 1 query PASS. Local unit/adversarial tests NOT_RUN. CI this round NOT_RUN/NOT_VERIFIED. No merge, deploy, DDL/DML, seed or migration.
