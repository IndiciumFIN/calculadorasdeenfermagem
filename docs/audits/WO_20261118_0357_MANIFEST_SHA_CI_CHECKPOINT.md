# CE / CKO / NCOS — checkpoint 2026-11-18 03:57 BRT

## Scope and immutability
Primary: IndiciumFIN/calculadorasdeenfermagem, branch audit/ce-supabase-migration-first-20261115. Sole physical database: Supabase Calculadoras-Smart pgsybzggewhinaniybiy, SELECT-only. No Neon, SOT, WU-TRIB, DDL/DML, migrations, seeds, deployment, merges or branch deletion. Fail-closed clinical, legal, LGPD, copyright, security and provenance gates. Candidate not published.

## Verified delta since previous checkpoint
- Prior checkpoint commit 448f303659d87b3b15aecf7221163c97ec5f0be7 was fetched and verified.
- Current MANIFEST.json blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; 22 source files; observation 2026-11-15; NON_ATOMIC_ACROSS_QUERIES; HOLD_HUMAN.
- Three source file Git blobs independently checked against manifest: schemas.json 97446ee106eafc9843748ac681b2ae5329f361a7; policies.jsonl 405a3b6e4ef2c8619f2afea6c6dd9202397e0db2; extensions.jsonl ee40200f2094335aa148fd8486154d1af2df48d0. All 3/3 PASS_HASH; 19/22 NOT_RUN. Counts in manifest are historical metadata, not current DB homologation.
- Workflow runs on prior checkpoint commit: canonical 44247577260 FAIL (two jobs: 134610141795, 134610142105); deterministic pipeline 44247577249 PASS; CI validation 44247577248 PASS; migration-first provenance 44247577132 PASS. These are not checks for this new checkpoint commit.
- PostgreSQL SELECT pg_constraint on cko_governance.artifact_normative_bindings reconfirmed 4 definitions: PK binding_id; UNIQUE (artifact_version_ref,normative_ref,binding_role); FK artifact_version_ref -> object_versions; FK artifact_id -> controlled_artifacts ON DELETE CASCADE. No write. Cascade retention is HOLD_HUMAN.
- No source-code delta or functional fix in this round; no new local unit or adversarial tests executed. PR #73 and workspace PR #71 current HEADs NOT_REVALIDATED.

## Versioned work-order ledger
| WO / object | Fingerprint or SHA | Delta | Status / risk | Test | Owner / next action | Acceptance |
|---|---|---|---|---|---|---|
| CE-EXPORT-22 / MANIFEST.json | 8099e3ff225224eb00e8eb5accd6d8365ddfcf14 | 3 individual source blobs verified | PASS_HASH 3/22, medium | 3 GitHub fetch SHA matches; 19 NOT_RUN | CE audit: validate remaining 19 blobs without reprocessing matched fingerprints | 22/22 hash matches, records checked, no secrets |
| CE-CI-73 / prior checkpoint | 448f303659d87b3b15aecf7221163c97ec5f0be7 | New CI result: canonical FAIL, other 3 PASS | FAIL_CI, high | 3/4 workflows PASS, 2 canonical jobs FAIL | CE engineering: inspect latest job logs, fix proven source/policy and parser/import errors, run adversarial tests | All required CI PASS at same HEAD |
| CE-DB-PROVENANCE / artifact_normative_bindings | SELECT pg_constraint 4 named definitions | No delta observed in scoped constraints | PASS_READ / HOLD_HUMAN, high | 4/4 SELECT results | Clinical/legal governance: review cascade retention and provenance requirements | Approved retention model, tested migration and rollback before any DDL |
| CE-TOOLS-24 / feat/ce-tools-governed-backend-20261115 | HEAD NOT_REVALIDATED | No verified delta | HOLD_VERIFY, high | NOT_RUN | CE engineering: reconcile 24 contracts with catalog | 24/24 evidence-based tests and clinical gates |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_REVALIDATED | No verified delta | HOLD_VERIFY | NOT_RUN | CKO engineering: PK/FK/dictionary semantic diff | Zero unexplained semantic mismatches |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_REVALIDATED | No verified delta | HOLD_PROVENANCE | NOT_RUN | CKO content: atom lineage and licensing | 100% candidate atoms traceable and licensed |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | HEAD NOT_REVALIDATED | Historical 16 parsers and 5 imports unresolved | FAIL_CI / HOLD_VERIFY | NOT_RUN locally | CE engineering: restore proven contracts and rerun CI | 0 missing parsers/imports, strict tests PASS |
| CE-WORKSPACE / dev-chatgpt-workspace PR #71 | HEAD NOT_REVALIDATED | No verified delta | HOLD_CI | NOT_RUN | PMO: inspect HEAD/checks and isolate regressions | Required checks PASS; no cross-project contamination |

## Layer coverage, not homologation
Manifest source-file SHA validation: 3/22 = 13.64%. CI on previous checkpoint: 3/4 workflows PASS (75%), overall FAIL. Scoped DB constraints read: 4/4 PASS_READ, not 4/1996 homologated. Clinical tool approvals: 0/24 evidenced this round (NOT_REVALIDATED). Parser resolution this round: 0/16; import resolution: 0/5. PR head validation: 0/2. Unit/adversarial test executions this round: 0. Global completion estimate: NOT_ESTIMABLE; no consolidated acceptance denominator.

## Next actions
Verify remaining 19 manifest blobs; fetch current PR #73 and #71 HEAD/checks; inspect current canonical job logs; reconcile source/policy validator schema and 16 parser/5 import dependencies with strict tests. Continue independent work while human provenance retention gate remains HOLD_HUMAN. No official external normatives used this round.
