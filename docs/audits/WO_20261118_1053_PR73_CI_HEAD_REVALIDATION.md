# CE / CKO / NCOS — checkpoint 2026-11-18 10:53 BRT

## Verified baseline
Previous checkpoint file `WO_20261118_0956_TACO_CONTRACT_CI_CHECKPOINT.md`, blob `19490ab4d3b4abc0b7641a2e663bb289751da6a5`; prior commit `907ce405942151b3e75415ade4d74268e111e460`. PR #73 HEAD read directly: `907ce405942151b3e75415ade4d74268e111e460`, branch `audit/ce-supabase-migration-first-20261115`, open draft, base main, GitHub mergeable (not approved). Workspace PR #71 open draft, head `1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d`, base `dacfaa6bc29fd213ffc4d63998b4dd669d10854b`. No merges.

## New evidence: CI on exact PR #73 HEAD
GitHub workflow runs for `907ce405...`: 44308853650 provenance PASS; 44308853648 deterministic PASS; 44308853553 validation PASS; 44308853680 canonical invariants FAIL. Canonical job 134817421104: compile and negative tests PASS; canonical source/policy references FAIL at step 7, CLI and policy smoke SKIPPED. Admission job 134817421583: parser/import dependencies FAIL at step 4. Thus TACO static correction did not close canonical gate. No fresh tests launched in this checkpoint; these are verified workflow results on prior HEAD.

## Physical truth — SELECT only
Supabase project `pgsybzggewhinaniybiy`: `pg_constraint` by contype in `cko_governance`: CHECK=61, FK=81, PK=88, UNIQUE=34; total 264. Same aggregate as previous checkpoint, so no reclassification of unchanged fingerprints. Historical export manifest `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` (blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`), 22/22 Git hashes verified in prior checkpoints, NOT_REPROCESSED. Historical inventory 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS. Export NON_ATOMIC_ACROSS_QUERIES, no physical acceptance inferred.

## Work orders (fingerprint, delta, state, risk, test, owner/action, acceptance)
| WO / branch / object | Fingerprint and delta | State / risk | Test | Owner and next action | Acceptance |
|---|---|---|---|---|---|
| CE-PR73 / audit / PR #73 | HEAD `907ce405...`, newly verified | PASS_READ / high | four workflow conclusions read | Engineering: resolve failed steps without weakening gate | 4/4 required workflows PASS on same HEAD |
| CE-CONTRACTS / audit / canonical sources | job `134817421104`, source-policy step FAIL, TACO blob `440de629fb5cf4e0c8e4982945905a9e7b3343e4` prior | FAIL / high | compile PASS; negative PASS; canonical FAIL | Engineering: inspect failing source-policy references and patch only proven mismatch | reference check PASS, CLI smoke executed PASS |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | job `134817421583`, parser/import step FAIL | FAIL / high | admission FAIL | Engineering: compare parser paths/imports and tests | 0 unresolved dependencies |
| CE-WORKSPACE / PR #71 | HEAD `1976da6...` newly verified | HOLD_VERIFY / medium | CI NOT_RUN | Frontend: inspect checks without migration | required checks PASS |
| CE-CATALOG-GOV / Supabase | CHECK 61, FK 81, PK 88, UNIQUE 34; no aggregate delta | PASS_AGGREGATE / HOLD_OBJECT_MAPPING; medium | SELECT PASS | DB architecture: identity/definition PK-FK mapping | zero unexplained object differences |
| CE-EXPORT / 22 files | MANIFEST blob `8099e3ff...`; 22/22 prior PASS | PASS_HASH historical / low | NOT_REPROCESSED | Audit: check only upon delta | fingerprints stable |
| CE-TOOLS / feat/ce-tools-governed-backend-20261115 | 24 tools, HEAD NOT_RUN | HOLD_HUMAN / high | NOT_RUN | Clinical engineering: verify per-tool gates | 24/24 accepted |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_RUN | HOLD_VERIFY / medium | NOT_RUN | Architecture: dictionary and semantic dedup | no duplicate object |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_RUN | HOLD_HUMAN / high | NOT_RUN | Clinical content: license and atom provenance | accepted source for each published atom |
| CE-GLOBAL-CONSTRAINTS / PostgreSQL | 1996 export vs historical 2109 live, +113 numeric only | HOLD_SEMANTIC / high | object mapping NOT_RUN | DB architecture: compare exact identities | classify all genuine deltas |

## Layer coverage and global estimate
Export integrity 22/22 (100% historical Git hashes); governance aggregate 1/1 PASS, object-level 0/1996 reconciled this round; PR heads 2/2 verified; PR #73 workflows 3/4 PASS, global FAIL; canonical blocked jobs 2/2 confirmed; 24 tools 0/24 revalidated this round; parsers 0/16 and imports 0/5 corrected this round; new local/adversarial tests NOT_RUN; PR #71 CI NOT_RUN. These are activity/verification denominators, not homologation rates. **Global completion estimate: NOT_ESTIMABLE** (no unified acceptance denominator).

## Safety
No DDL/DML, migrations, seeds, deployment, merge, branch deletion or candidate publication. Preserve fail-closed, LGPD, copyright, legal, clinical and provenance gates. Sources: connected GitHub PRs, GitHub Actions and Supabase SELECT accessed 2026-11-18. Next independent work: inspect source-policy failures, reconcile parser import paths, review 24 tools and metamodel/corpus; maintain HOLD_HUMAN for unapproved clinical/legal evidence.
