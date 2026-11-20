# CE / CKO / NCOS — checkpoint 2026-11-18 14:52 BRT

## Scope and safety
Main repository IndiciumFIN/calculadorasdeenfermagem, PR #73, branch audit/ce-supabase-migration-first-20261115. Sole physical database Supabase Calculadoras-Smart pgsybzggewhinaniybiy. SELECT only; no DDL/DML/migrations/seeds/merges/deploy. Fail-closed clinical, security, LGPD, licensing and provenance gates remain active. Candidate is not published.

## Work orders / evidence
| WO / object | Fingerprint / SHA and delta | Status / risk | Test and evidence | Responsible / next action | Acceptance |
|---|---|---|---|---|---|
| CE-SIES contracts/fontes/sies.json | blob 97d91f8f4df6f83a6f848cb4df5caefe0a1971ae -> e12669bac624d303e898dd0e83480159f12fceb0; validators scalar -> array; policy 016 blob 93985a7c3b1859a7b14e8f142f2230790f2d5a32 | PASS_STATIC / medium, global admission FAIL | Direct GitHub reads and policy comparison; code commit 29485c77dc6699ca20e8700db59a747327ff54b3; post-fix CI NOT_RUN | Engineering: verify exact-HEAD CI, source/policy checks | Canonical CI green |
| CE-CI-PR73 | previous HEAD 0f5e77d5db1040ecb3a3a891d19c4df5bd738251; workflow IDs 44353293714, 44353293722, 44353294293, 44353293467 | FAIL / high | 3/4 PASS; canonical FAIL; jobs 134974519261 and 134974519986 | Engineering: fix remaining source references, parser/import dependencies | 4/4 required workflows PASS on final HEAD |
| CE-PARSERS integration/cko-parsers-catalog-20261114 | prior finding 16 absent; HEAD/fingerprint NOT_READ | HOLD_VERIFY / high | Current admission step FAIL; no parser patch | Engineering: inspect branch and port tested implementations only | 0 missing, smoke PASS |
| CE-IMPORTS packages/cli | prior finding 5; SHA NOT_READ | HOLD_VERIFY / high | Admission step FAIL | Engineering: compare namespace paths, test imports | 0 unresolved imports |
| CE-EXPORT docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json | blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; historical 22/22 hashes | PASS_HASH historical / low | Manifest directly read; no delta demonstrated, no rehash | Audit: only rehash on delta | 22/22 stable |
| CE-SUPABASE cko_governance | pg_constraint c61 f81 p88 u34 = 264 | PASS_AGGREGATE / HOLD_OBJECT_MAPPING | SELECT current, no write | DB architecture: per-object PK/FK/definition matching | No unexplained identity changes |
| CE-GLOBAL-CONSTRAINTS | 1996 export vs historical live 2109; delta +113 unproven | HOLD_SEMANTIC / high | 0/1996 individually reconciled this round | DB architecture: canonical fingerprints | 1996 classified |
| CE-TOOLS feat/ce-tools-governed-backend-20261115 | 24 candidates; HEAD NOT_READ | HOLD_HUMAN / high | 0/24 clinical homologations revalidated | Clinical engineering: provenance and safety per tool | 24/24 individually accepted |
| CE-METAMODEL feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_READ | HOLD_VERIFY / medium | Dictionary and PK/FK crosswalk NOT_RUN | Architecture: semantic deduplication | No competing identities |
| CE-CORPUS feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_READ | HOLD_HUMAN / high | License/provenance NOT_RUN | Clinical/legal: validate atom/source | Every accepted atom licensed |
| CE-WORKSPACE PR #71 | historical HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d; current NOT_READ | HOLD_VERIFY / high | CI NOT_RUN | Frontend: SSR/auth/preview/no migration | Required checks pass |

## Measured coverage and global estimate
- Export integrity: historical 22/22 = 100% PASS_HASH, not reprocessed.
- SIES selected static contract: 1/1 PASS_STATIC; denominator of all contracts unknown.
- CI on preceding HEAD: 3/4 = 75%, global FAIL; after correction NOT_RUN.
- Governance aggregate SELECT: 1/1 PASS_AGGREGATE; global constraint identity 0/1996 this round.
- Clinical tools 0/24 revalidated; parsers 0/16 fixed this round; imports 0/5 fixed this round.
- Local unit/adversarial/smoke: NOT_RUN. Priority branch HEADs and workspace PR #71: NOT_READ this round.
- **Global completion estimate: NOT_ESTIMABLE**; acceptance denominator is not established. Inventory counts are not homologation.

## Evidence and next sequence
GitHub Actions canonical run https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44353294293; three other workflow runs passed on prior HEAD. SIES source and policy 016 directly compared. Supabase SELECT grouping on pg_constraint, project pgsybzggewhinaniybiy, 2026-11-18. Next: verify CI after code and checkpoint commits; inspect parser integration branch and imports; reconcile PostgreSQL object identities; continue independent tools/metamodel/corpus tracks. No external official normative source consulted. No database mutation or blocked merge.
