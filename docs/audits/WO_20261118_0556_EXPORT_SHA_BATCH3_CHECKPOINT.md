# CE / CKO / NCOS — checkpoint 2026-11-18 05:56 BRT

## Scope / baseline
Only Supabase Calculadoras-Smart pgsybzggewhinaniybiy is physical source of truth. GitHub audit branch audit/ce-supabase-migration-first-20261115. Read-only SQL SELECT, no Neon/SOT, accounting, migrations, DDL/DML, seed, deployment, merge or branch deletion. Clinical/legal/security/LGPD/provenance/licensing gates fail closed.

Baseline checkpoint: WO_20261118_0454_EXPORT_SHA_BATCH2_CHECKPOINT.md (blob 2c4c87c20e0bd0118c195e251742885953de26f9); MANIFEST.json Git blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14. Export date 2026-11-15, NON_ATOMIC_ACROSS_QUERIES and HOLD_HUMAN. Inventory: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. Inventory is not homologation.

## New verified delta
Six previously unchecked Git blob SHA-1 values independently fetched from export and compared with MANIFEST.json, all PASS_HASH:
- reference/canonical-object-metadata.jsonl: 70e2833eca68309ff3c5d13915e61e3ca011cc71
- reference/evidence-source-metadata.jsonl: bd7986a30102108d895faf5653aa0d23ab76d449
- reference/normative-reference-metadata.jsonl: 2b55d69c98a8a0b9f6fe78f74682aeccf415001a
- reference/source-mapping-metadata.jsonl: cf127ef02e4dfec885d023d6503b2827237c1247
- routines.jsonl: e889df4e2d03d62a6a57fb1c046cce2b22f21d5c
- indexes.jsonl: 266e3edc1dbd5b1a797de3bebe4d06421a09d9ba

Previous 9/22 hashes were not reprocessed; cumulative 15/22 PASS_HASH = 68.18%, seven NOT_RUN (six columns partitions and constraints.jsonl). Git SHA matching is repository fingerprint verification only, not byte-level independent backup integrity or physical database homologation.

Supabase SELECT on information_schema.table_constraints WHERE table_schema='cko_governance' returned 1293 rows; this is scoped to one schema and a different catalog projection than the historical 1996 pg_constraint total, so do not compare counts as a delta without aligning query scope. No write occurred. Retention/cascade question remains HOLD_HUMAN.

## Versioned work orders
| WO / object | Fingerprint / SHA | Delta / status / risk | Tests | Responsible and next action | Acceptance |
|---|---|---|---|---|---|
| CE-EXPORT-22 / MANIFEST | 8099e3ff225224eb00e8eb5accd6d8365ddfcf14 | +6 verified, 15/22 PASS_HASH, medium | 6/6 SHA match | Audit: validate 7 remaining files | 22/22 matches; privacy review |
| CE-DB-CATALOG / cko_governance | SELECT information_schema.table_constraints count=1293 | PASS_READ; catalog scope mismatch, medium | 1/1 SELECT | Data architecture: compare same-scope pg_constraint and export | Explained PK/FK/index/constraint semantic delta |
| CE-DB-PROVENANCE / artifact_normative_bindings | Previous 4 scoped pg_constraint definitions | No new delta, HOLD_HUMAN high | NOT_RUN this round | Clinical/legal: decide cascade retention | Signed provenance/retention decision |
| CE-CI-73 / audit branch PR #73 | previous checkpoint c9f3f55884fecefe1b022120b2af8c4578a9afd8 | CI historical FAIL, current HEAD not revalidated, high | NOT_RUN | Engineering: inspect current checks, fix validated contract errors | All required checks PASS same HEAD |
| CE-TOOLS-24 / feat/ce-tools-governed-backend-20261115 | HEAD NOT_REVALIDATED | HOLD_VERIFY high | NOT_RUN | Clinical engineering: 24 contracts and clinical evidence | 24/24 approved |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_REVALIDATED | HOLD_VERIFY high | NOT_RUN | CKO: PK/FK/dictionary comparison | No unexplained semantic delta |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_REVALIDATED | HOLD_PROVENANCE high | NOT_RUN | Editorial/legal: atom lineage and licensing | Every promoted atom traceable |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | HEAD NOT_REVALIDATED | historical 16 parsers and 5 imports, HOLD_VERIFY high | NOT_RUN | Engineering: resolve strict contracts | 0 missing; strict CI PASS |
| CE-WORKSPACE / dev-chatgpt-workspace PR #71 | HEAD NOT_REVALIDATED | HOLD_VERIFY | NOT_RUN | PMO: inspect HEAD/checks | Checks PASS and no contamination |

## Layer metrics and decision
- Export SHA verification: **15/22 = 68.18%**; remaining 7/22 = 31.82%.
- Scoped catalog query: **1/1 SELECT successful**, 1293 rows observed; NOT a completion ratio for database audit.
- CI: historical 3/4 workflows PASS, canonical FAIL; current NOT_RUN/NOT_VERIFIED.
- Clinical tools: **0/24 approvals verified this round**, not an assertion that 24 failed.
- Parsers/imports: **0/16 and 0/5 resolved this round**, historical unresolved candidates.
- Branch/PR current HEAD verification: **0/6** (four feature branches, two PRs); NOT_RUN.
- Global completion estimate: **NOT_ESTIMABLE**; no common denominator of accepted controls.

## Tests, commits, next actions
This round: six Git blob comparisons PASS; one PostgreSQL SELECT PASS; unit/adversarial tests NOT_RUN; CI NOT_RUN; functional code changes NONE. This document is the only intended commit. Next: validate 7 remaining hashes; inspect PR #73/#71 HEAD/checks; reconcile candidate SQL to same-scope physical PK/FK metadata; repair proven source-policy/parser deltas with tests before merging. No candidate publication or blocked merge.
