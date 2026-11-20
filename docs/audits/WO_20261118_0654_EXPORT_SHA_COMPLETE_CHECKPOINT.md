# CE / CKO / NCOS — checkpoint 2026-11-18 06:54 BRT

## Baseline and boundaries
Previous versioned checkpoint: WO_20261118_0556_EXPORT_SHA_BATCH3_CHECKPOINT.md (Git blob 4bc257132b450705fb576ca65ac322b4ef8cc624; commit 84655a0060eb0922503feeae4324e6bfc85034ca). MANIFEST.json blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14. Source of physical truth: Supabase Calculadoras-Smart pgsybzggewhinaniybiy only. No Neon, SOT, accounting, DDL/DML, migration, seed, merge, deployment, branch deletion. Export dated 2026-11-15: NON_ATOMIC_ACROSS_QUERIES; HOLD_HUMAN. Inventory: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. This is metadata inventory, not homologation.

## Delta: final seven Git fingerprints verified
All seven files fetched directly on audit/ce-supabase-migration-first-20261115 and returned blob SHA exactly matching MANIFEST.json:
| File | Git blob SHA-1 | Test |
|---|---|---|
| columns-ce.jsonl | 94e5af9a1292bfad2f118d80217aa55e968b7e17 | PASS_HASH |
| columns-cko-1.jsonl | de10d95c13657f5648ffb94d85dfc8a4acdc4caf | PASS_HASH |
| columns-cko-2.jsonl | 37cc1dc51ef299fce26c6521d64117a20a2c7a12 | PASS_HASH |
| columns-other-1.jsonl | cda2cecb67b2bcd7e07ef2bc4f67d11ed7b18885 | PASS_HASH |
| columns-other-2.jsonl | dd6c90a9f2922dc508416ee39578c1811c5291fa | PASS_HASH |
| columns-xlf.jsonl | c7261af3e2be0b10c68be496635371b9f58245c0 | PASS_HASH |
| constraints.jsonl | 83642780302397204b39796e1bd3604a77c68f53 | PASS_HASH |

Previous 15/22 retained as historical PASS_HASH without reprocessing; cumulative 22/22 = 100% Git blob-to-manifest matching. This does NOT independently verify source database state, byte-level backup or provenance. No semantic/clinical approval follows from these hashes.

## Read-only PostgreSQL
SELECT count(*) FROM information_schema.table_constraints WHERE table_schema='cko_governance' returned 1293; repeat confirmation of scoped historical count. Not comparable to 1996 all-schema pg_constraint inventory without identical scope and catalog semantics. No database mutation.

## Versioned work orders
| WO / object | Fingerprint or SHA / delta | Status, risk | Test | Owner / next action | Acceptance criterion |
|---|---|---|---|---|---|
| CE-EXPORT-22 / seven files above | SHA per row; +7 newly verified, cumulative 22/22 | PASS_HASH, medium | 7/7 PASS | Audit: inspect export consistency and provenance | Independent export-to-physical reconciliation and privacy clearance |
| CE-MANIFEST / MANIFEST.json | 8099e3ff225224eb00e8eb5accd6d8365ddfcf14, no delta | HOLD_HUMAN, medium | NOT_RUN beyond Git hashes | Data governance: confirm non-atomic snapshot limitations | Source scope/consistency documented and signed |
| CE-DB-CATALOG / cko_governance | scoped 1293 constraints; no delta | PASS_READ / HOLD_SEMANTIC, high | 1/1 SELECT | Data architecture: align pg_constraint vs export and SQL candidate | PK/FK/dictionary semantic parity with explanations |
| CE-PROVENANCE / artifact_normative_bindings | historical FK ON DELETE CASCADE, no delta verified | HOLD_HUMAN, high | NOT_RUN | Clinical/legal: decide retention policy | Signed legal and clinical approval |
| CE-CI-73 / audit PR #73 | previous commit 84655a0060eb0922503feeae4324e6bfc85034ca; HEAD not revalidated | HOLD_VERIFY, high | NOT_RUN | Engineering: check HEAD and CI, repair failures | All mandatory CI PASS on same HEAD |
| CE-TOOLS-24 / feat/ce-tools-governed-backend-20261115 | HEAD NOT_REVALIDATED | HOLD_VERIFY, high | NOT_RUN | Clinical engineering: inspect 24 contracts | 24/24 approved with clinical gates |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_REVALIDATED | HOLD_VERIFY, high | NOT_RUN | CKO: reconcile dictionary, PK/FK, normative refs | No unexplained semantic delta |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_REVALIDATED | HOLD_PROVENANCE, high | NOT_RUN | Editorial/legal: deduplicate atom fingerprints and check licenses | Every promoted atom traceable and licensed |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | HEAD NOT_REVALIDATED; historical 16 parsers + 5 imports | HOLD_VERIFY, high | NOT_RUN | Engineering: fix confirmed missing dependencies | Zero missing, strict CI PASS |
| CE-WORKSPACE / dev-chatgpt-workspace PR #71 | HEAD NOT_REVALIDATED | HOLD_VERIFY, medium | NOT_RUN | PMO: inspect checks and contamination | Checks PASS, scope clean |

## Measured layer progress
- Export Git SHA matches: **22/22 = 100%**; 7/7 newly checked this run. This layer alone is complete.
- Supabase scoped SELECT: **1/1 PASS_READ**, not a database completion ratio.
- CI: historical **3/4** workflows PASS and canonical FAIL; current HEAD NOT_RUN.
- Clinical tool approvals: **0/24 verified this run**, not a failure count.
- Parser/import corrections: **0/16** and **0/5** this run, historical candidates.
- Priority branch/PR HEADs: **0/6** revalidated this run.
- Global completion estimate: **NOT_ESTIMABLE** (no complete common acceptance denominator).

## Tests, changes, next actions
Git SHA comparisons 7 PASS, 0 FAIL; SQL SELECT 1 PASS; unit/adversarial and CI NOT_RUN. No functional code change this round. Persist this checkpoint on audit branch, then prioritize CI/PR HEAD verification, same-scope catalog reconciliation, candidate SQL and dictionary semantic differences, source-policy contract fixes and parser/import defects. Preserve fail-closed, clinical/legal/security/LGPD/licensing gates; candidate never published. No blocked merge.
