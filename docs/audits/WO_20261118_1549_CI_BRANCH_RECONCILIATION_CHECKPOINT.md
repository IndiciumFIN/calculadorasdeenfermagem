# CE / CKO / NCOS — checkpoint 2026-11-18 15:49 BRT

## Scope
Repository IndiciumFIN/calculadorasdeenfermagem; audit branch / PR #73. Physical source of truth: Supabase Calculadoras-Smart pgsybzggewhinaniybiy, SELECT only. No Neon, SOT, WU-TRIB, DDL/DML, migrations, seeds, merges, deployments or candidate publication. Clinical/legal/security/LGPD/provenance gates fail closed.

## Work orders and object register
| WO / object | SHA / fingerprint / delta | Status / risk | Evidence / test | Owner / next action | Acceptance |
|---|---|---|---|---|---|
| CE-PR73-CI | preceding HEAD e46c38ad274a8cda67627e5216cac098e3a7380a; runs 44363624926, 44363624954, 44363624919, 44363624908 | FAIL / high | 3/4 workflows PASS; canonical FAIL; failed jobs 135011373747, 135011374125; exact-head logs inspected | Engineering: resolve source/policy and parser/import failures | 4/4 required workflows green on final HEAD |
| CE-SOURCE-CID11 contracts/fontes/cid11.json | blob 8b9af2dcfc80521fb17965f1d2423a3a496c4199; validators scalar cid11_validator; policy KERNEL-POLICY-004 | FAIL_SCHEMA / medium | GitHub read and CI SOURCE_VALIDATOR_SCHEMA; no patch without policy contract | Engineering: locate policy 004, align array with policy and test | Policy-reference and schema PASS |
| CE-SOURCE-REMAINING | CI flags cid11, esavi, fhir_vitais, mesh, sinan, vacinas_cdc; individual SHA NOT_READ | FAIL_SCHEMA / high | CI logs 2026-11-18; SIES previous blob e12669bac624d303e898dd0e83480159f12fceb0 unchanged | Engineering: compare each source with policy before edit | No SOURCE_VALIDATOR_SCHEMA errors |
| CE-PARSERS integration/cko-parsers-catalog-20261114 | ahead main 163, behind 0 at compare; SHA HEAD NOT_READ; 16 missing on audit branch | HOLD_VERIFY / high | Branch comparison and CI MISSING_PARSER x16 | Engineering: inspect available implementations, license/tests, dedup | 0 missing + smoke PASS |
| CE-IMPORTS packages/cli | 5 namespace findings; object SHA NOT_READ | HOLD_VERIFY / high | CI PACKAGE_IMPORT_NAMESPACE x5 | Engineering: test python -m packages.cli.main | 0 namespace blockers |
| CE-TOOLS feat/ce-tools-governed-backend-20261115 | ahead main 15, behind 0; manifest present; HEAD SHA NOT_READ | HOLD_HUMAN / high | Compare branch; 0/24 clinical homologations this round | Clinical engineering: verify tool contracts and safety | 24/24 individually accepted |
| CE-METAMODEL feat/cko-catalog-metamodel-automated-20261114 | ahead main 22, behind 0; SHA NOT_READ | HOLD_VERIFY / medium | Compare branch, no semantic crosswalk executed | Architecture: PK/FK/dictionary comparison | No competing identity |
| CE-CORPUS feat/cko-m08-m09-corpus-atomic-20261114 | ahead main 8, behind 0; SHA NOT_READ | HOLD_HUMAN / high | Compare branch, no license review this round | Clinical/legal: validate provenance | Every published atom licensed |
| CE-EXPORT MANIFEST | blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; 22/22 historical hashes, no demonstrated delta | PASS_HASH historical / low | Manifest read; no rehash | Audit: rehash only on delta | 22/22 stable |
| CE-SUPABASE cko_governance | SELECT pg_constraint c61 f81 p88 u34 =264 | PASS_AGGREGATE / HOLD_OBJECT_MAPPING | SELECT 2026-11-18, no write | DB architecture: compare object identity | Object-level PK/FK reconciliation |
| CE-GLOBAL-CONSTRAINTS | export 1996; previous live count 2109; delta +113 unproven | HOLD_SEMANTIC / high | 0/1996 object matches this round | DB architecture: scoped canonical fingerprints | Every historical object classified |
| CE-WORKSPACE PR #71 | historical HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d; current NOT_READ | HOLD_VERIFY / medium | Not retested this round | Frontend: verify checks and auth/SSR | Required checks PASS |

## Coverage / acceptance
- Historical export Git integrity: 22/22 = 100% PASS_HASH (not reprocessed).
- Current workflow check on previous HEAD: 3/4 = 75%, overall FAIL; new checkpoint HEAD CI NOT_RUN.
- CI failed job diagnosis: 2/2 inspected.
- Priority branches compared to main: 4/4; HEAD SHAs not individually validated.
- Governance aggregate: 1/1 SELECT PASS; object-level constraints: 0/1996 reconciled this round.
- Clinical tools: 0/24 revalidated this round. Parser fixes 0/16; namespace fixes 0/5. Local unit/smoke/adversarial tests NOT_RUN.
- Global completion estimate: NOT_ESTIMABLE (no complete acceptance denominator). Inventory is not homologation.

## Evidence, risk and next steps
GitHub CI: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44363624919 . Logs show source validator schema errors, 16 missing parsers, 5 namespace warnings. CI source/policy job failed and skipped smoke. Branch comparisons confirm independent implementation tracks; do not copy files without semantic and license validation. Supabase SELECT confirms 264 scoped constraints but does not resolve the global historical +113. No external normative sources used. No functional code changes or local tests this round. Next: locate policy 004 and parser branch implementations; patch tested source contracts; rerun exact-head CI; continue PK/FK object mapping independently.
