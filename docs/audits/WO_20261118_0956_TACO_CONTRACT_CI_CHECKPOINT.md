# CE / CKO / NCOS — checkpoint 2026-11-18 09:56 BRT

## Baseline / identity
Previous verified checkpoint commit: `2ffc46a36d0c19049511b3b993c497a0034e3de6`; previous file blob `2f9691091c78d179532abfb254a92a52a80bd58e`. Current code correction commit: `587f1e84169c637f0f910e8c304edac5fd1fe08b`, TACO blob `440de629fb5cf4e0c8e4982945905a9e7b3343e4`, previous blob `3175d5620d9165568680b45df9def786651278bc`. Change: validators string -> array, exact policy match; no weakening of gate.

## Evidence and tests
- GitHub CI run 44280367820, jobs 134719123570 and 134719124058, both FAIL. Confirmed steps: unresolved parser/import dependencies; canonical source/policy verification. Logs explicitly identify TACO SOURCE_VALIDATOR_SCHEMA, 16 missing parsers and 5 import namespace concerns. Historic run, not current post-fix CI.
- TACO policy `contracts/policies/KERNEL-POLICY-010.json`, blob `4410342cde1dcf6a0014375c411a82ffd466f327`, requires validators array `["schema_validator"]`. TACO source contract original blob `3175d5620d9165568680b45df9def786651278bc` contained string; corrected with exact policy array. Static cross-file schema comparison PASS; runtime tests and CI on corrected HEAD NOT_RUN.
- Supabase project `pgsybzggewhinaniybiy` SELECT-only revalidated `cko_governance` pg_constraint counts: CHECK 61, FK 81, PK 88, UNIQUE 34 (total 264), matching previous aggregate. No DDL/DML.
- Git comparison `main...audit/ce-supabase-migration-first-20261115`: ahead 94, behind 0, 105 changed files **before** this round's code commit. Workspace `main...fix/ce-tanstack-vercel-build-no-migrations-20261114`: ahead 17, behind 0, 12 files. These are Git diff metrics, not approval.
- Export `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` read, historical 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. Manifest says NON_ATOMIC_ACROSS_QUERIES and HOLD_HUMAN. Previous 22/22 hash PASS retained, NOT_REPROCESSED (no delta established).

## Versioned work orders
| WO / branch / object | SHA or fingerprint / delta | Status; risk | Test | Owner / next action | Acceptance |
|---|---|---|---|---|---|
| CE-SOURCE-TACO / audit branch / contracts/fontes/taco.json | 3175d562 -> 440de629; string to one-element array; policy 010 blob 4410342 | PASS_CODE, HOLD_CI; medium | Static policy match PASS, new CI NOT_RUN | Engineering: verify new HEAD CI and parser | canonical validator PASS, all mandatory checks PASS |
| CE-CI / PR #73 | historical run 44280367820, 2 failed jobs | FAIL; high | Logs READ PASS; post-fix NOT_RUN | Engineering: isolate remaining source contracts, 16 parsers and 5 imports | all mandatory CI PASS on same HEAD |
| CE-CATALOG-GOV / PostgreSQL | c=61 f=81 p=88 u=34; unchanged aggregate | PASS_AGGREGATE, HOLD_OBJECT_MAPPING; medium | SELECT PASS | DB architecture: match constraint identity and definitions | zero unexplained PK/FK |
| CE-CATALOG-GLOBAL | 1996 export vs historical live 2109, +113 numeric only | HOLD_SEMANTIC; high | object match NOT_RUN | DB architecture: scoped per-object reconciliation | classify genuine deltas by identity/definition |
| CE-EXPORT / MANIFEST | blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; prior 22/22 | PASS_HASH historical; low | NOT_REPROCESSED | Audit: check only upon delta | unchanged fingerprints |
| CE-TOOLS / feat/ce-tools-governed-backend-20261115 | 24 tools; HEAD NOT_VERIFIED | HOLD_HUMAN; high | NOT_RUN | Clinical engineering: contract-by-contract | 24/24 accepted gates |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_VERIFIED | HOLD_VERIFY; medium | NOT_RUN | Architecture: dictionary/PK/FK reconciliation | no duplicate objects |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_VERIFIED | HOLD_HUMAN; high | NOT_RUN | Clinical content: source/licensing/provenance | atom-level source approvals |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | 16 missing and 5 namespace warnings in historical logs | FAIL/HOLD_VERIFY; high | NOT_RUN corrected HEAD | Engineering: compare file paths/imports before integrating | 0 unresolved |
| CE-WORKSPACE / PR #71 | comparison ahead 17, behind 0, 12 files; HEAD/checks NOT_VERIFIED | HOLD_VERIFY; medium | NOT_RUN | Frontend: build CI without migrations | required checks PASS |

## Layer coverage and global estimate
Git export hash 22/22 (100% historical integrity only). TACO contract change 1/1 (100% static code fix, not CI). Governance aggregate 1/1 (100% aggregate only); object reconciliation 0/1996 this run. CI historical 3/4 workflows PASS, global FAIL; current CI NOT_RUN. Tools 0/24 revalidated this run (not proof none are approved). Parsers 0/16 and imports 0/5 fixed this run. PR current HEAD/checks 0/2. Unit/adversarial tests NOT_RUN. **Global completion estimate: NOT_ESTIMABLE** (no unified acceptance denominator).

## Safety / next actions
No migrations, DDL/DML, seeds, deploys, merges, branch deletions or candidate publication. Fail-closed, LGPD, clinical, legal, copyright and provenance gates remain. Next: run CI on corrected HEAD, resolve next proven contract mismatch, compare parser imports with integration branch, object-level PK/FK reconciliation, review tools/metamodel/corpus and PR #71. Sources: connected GitHub and Supabase queried 2026-11-18.
