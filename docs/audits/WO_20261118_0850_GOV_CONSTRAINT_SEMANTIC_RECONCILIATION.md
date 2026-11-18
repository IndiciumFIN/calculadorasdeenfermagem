# CE / CKO / NCOS — checkpoint 2026-11-18 08:50 BRT

## Baseline and provenance
Previous checkpoint commit `58252780551aae1f92749a7e888156a63fc90261` (07:53). Git export manifest blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`, 22/22 hashes previously PASS; no delta demonstrated, not reprocessed. Historical export 2026-11-15: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. This is historical inventory, not physical/clinical approval.

## New substantive semantic reconciliation (SELECT-only, 2026-11-18)
`pg_constraint` for schema `cko_governance`: CHECK 61, FK 81, PK 88, UNIQUE 34 = **264**.
`information_schema.table_constraints` for same schema: CHECK **1090**, FK **81**, PK **88**, UNIQUE **34** = **1293**.
`information_schema.columns` same schema: `is_nullable='NO'` **1029** of **1295** columns.
**Exact numerical reconciliation:** 1090 CHECK - 61 pg_constraint CHECK = **1029**, exactly the NOT NULL column count. Therefore the 1293-vs-264 discrepancy is explained at aggregate/type level by information_schema's NOT NULL CHECK representation. This is aggregate evidence only; object-level 1:1 mapping and catalog definitions remain unverified. Do not infer physical migration. The historical 1996 vs live global 2109 (+113 numeric) remains HOLD_SEMANTIC until scope/identity comparison.

## PR verification
PR #73 (IndiciumFIN/calculadorasdeenfermagem): OPEN, DRAFT, mergeable reported true, head branch `audit/ce-supabase-migration-first-20261115`, base `main`, updated 2026-11-18T10:54:17Z; HEAD SHA/checks NOT_VERIFIED.
PR #71 (IndiciumFIN/dev-chatgpt-workspace): OPEN, DRAFT, mergeable reported true, head `fix/ce-tanstack-vercel-build-no-migrations-20261114`, base `main`, updated 2026-11-15T06:56:23Z; HEAD SHA/checks NOT_VERIFIED. Mergeable flag does not supersede gates.

## Versioned work orders
| WO / object | Fingerprint / SHA / delta | Status and risk | Tests | Owner / next action | Acceptance |
|---|---|---|---|---|---|
| CE-CATALOG-GOV / aggregate | 264 pg_constraint vs 1293 information_schema; CHECK difference 1029 = NOT NULL 1029 | PASS_AGGREGATE / medium; HOLD_OBJECT_MAPPING | 3 SELECT queries PASS | DB architecture: sample per-column constraint identity and compare PG definitions | exact 1:1 explanation without unexplained PK/FK |
| CE-CATALOG-GLOBAL / 1996 export vs 2109 live | +113 numerical only; export manifest blob 8099e3ff | HOLD_SEMANTIC / high | NOT_RUN identity matching | DB architecture: reconcile same scope by schema/table/name/type/definition | classify each genuine delta |
| CE-EXPORT / 22 files | 22/22 prior PASS_HASH, unchanged evidence | PASS_HASH historical / low | NOT_REPROCESSED | Audit: rerun only if delta | stable fingerprints |
| CE-CI / PR #73 | previous 3/4 workflows PASS; canonical FAIL; branch head SHA not rechecked | FAIL / high | NOT_RUN current HEAD | Engineering: contracts/parsers and required CI | all mandatory jobs PASS on same HEAD |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | historical 16 missing parsers and 5 imports, fingerprints pending | HOLD_VERIFY / high | NOT_RUN | Engineering: compare imports to file paths, fix with tests | zero unresolved dependencies |
| CE-TOOLS / feat/ce-tools-governed-backend-20261115 | 24 tools; HEAD not checked | HOLD_HUMAN / high | NOT_RUN | Clinical engineering: verify each contract and safety gate | 24/24 individual homologations |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD not checked | HOLD_VERIFY / medium | NOT_RUN | Architecture: compare dictionary/PK/FK with physical catalog | no duplicate semantic objects |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD not checked | HOLD_VERIFY / high | NOT_RUN | Clinical content: provenance/license checks | approved atom-level sources |
| CE-WORKSPACE / PR #71 | OPEN DRAFT; HEAD SHA unverified | HOLD_VERIFY / medium | NOT_RUN | Frontend: verify checks and build without migrations | CI PASS, no unauthorized SQL |

## Layer numerators / denominators
Export Git hashes 22/22 (100% historical integrity); governance aggregate count reconciliation 1/1 (100% aggregate ONLY, not object-level); individual global constraint reconciliation 0/1996 this run; tools clinical approval 0/24 revalidated this run (not evidence that all are unapproved); parser fixes 0/16 this run; imports 0/5 this run; PR metadata fetched 2/2, HEAD/checks 0/2; CI current HEAD NOT_RUN; new unit/adversarial tests NOT_RUN. **Global completion estimate: NOT_ESTIMABLE**, missing common acceptance denominator.

## Safety and next actions
No DDL/DML, migrations, seeds, merges, deploys, branch deletions, or publication. Only SELECT reads and GitHub documentation. Preserve fail-closed, LGPD, clinical/legal/copyright and provenance gates. Next: check PR HEAD SHAs and checks, inspect canonical failed job logs, fix validated code issue with tests; reconcile global constraint identities and 24 tools independently. Sources: connected GitHub PR metadata and connected Supabase PostgreSQL catalog, queried 2026-11-18.
