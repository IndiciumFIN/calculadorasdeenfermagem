# CE / CKO / NCOS — checkpoint 2026-11-18 16:49 BRT

## Scope and safety
Primary GitHub repository IndiciumFIN/calculadorasdeenfermagem; PR #73, audit branch audit/ce-supabase-migration-first-20261115. Only physical database pgsybzggewhinaniybiy (Calculadoras-Smart), SELECT-only. No DDL/DML, migration, seed, merge, deploy or publication. Clinical, legal, LGPD, copyright, provenance and security gates fail closed. No external normative source consulted.

## Verified delta
- CID11 source contract `contracts/fontes/cid11.json`: previous Git blob `8b9af2dcfc80521fb17965f1d2423a3a496c4199`; policy `contracts/policies/KERNEL-POLICY-004.json` blob `043acbc532ff298bd9a4ab720ddd382890d19c15`; previous validators scalar `cid11_validator`; policy requires array `["cid11_validator","schema_validator"]`. Applied only this field; new blob `96f89cf868c664491a98daf6facd5929cacc6812`, commit `efde46b98b208c01823d51bc5d39fe3169ecc9a7`. Static contract-to-policy match PASS; CI NOT_RUN on new HEAD.
- SELECT pg_constraint in cko_governance on 2026-11-18: CHECK 61, FK 81, PK 88, UNIQUE 34 = 264. Aggregate PASS_READ, no object-level reconciliation.
- Previous checkpoint `ba40cad40d126396f1a377687dc479319e17f9b4` and `WO_20261118_1549_CI_BRANCH_RECONCILIATION_CHECKPOINT.md` consulted. Prior export fingerprints 22/22 PASS_HASH historical, no delta established, not rehashed.

## Versioned work orders / object register
| WO / object | SHA / fingerprint / delta | Status / risk | Test evidence | Owner / next action | Acceptance |
|---|---|---|---|---|---|
| CE-CID11 | old blob 8b9af2dc; policy 043acbc5; new blob 96f89cf8; validators scalar -> canonical array | PASS_STATIC / medium; CI pending | GitHub source/policy exact read and deterministic field comparison | Engineering: verify exact-head CI | Source-policy validator check PASS and full CI green |
| CE-PR73 | preceding checkpoint ba40cad40; correction efde46b98 | FAIL historical / high | prior canonical workflow FAIL; new CI NOT_RUN | Engineering: inspect latest workflow | 4/4 required workflows PASS |
| CE-OTHER-SOURCES | esavi, fhir_vitais, mesh, sinan, vacinas_cdc; individual SHAs NOT_READ | HOLD_VERIFY / high | historical SOURCE_VALIDATOR_SCHEMA | Engineering: read each source and matching policy before patch | zero schema failures |
| CE-PARSERS | integration/cko-parsers-catalog-20261114; historical ahead main 163, behind 0; HEAD NOT_READ | HOLD_VERIFY / high | historical 16 missing; no new parser tests | Engineering: reconcile imports/implementations, licenses | 0 missing; smoke PASS |
| CE-IMPORTS | packages/cli; SHA NOT_READ | HOLD_VERIFY / high | historical 5 namespace issues | Engineering: import tests | 0 blockers |
| CE-TOOLS | feat/ce-tools-governed-backend-20261115; HEAD NOT_READ | HOLD_HUMAN / high | 0/24 homologated this run | Clinical engineering: inspect contracts | 24/24 approved with evidence |
| CE-METAMODEL | feat/cko-catalog-metamodel-automated-20261114; HEAD NOT_READ | HOLD_VERIFY / medium | no object crosswalk this run | Architecture: compare PK/FK/dictionary | no competing identity |
| CE-CORPUS | feat/cko-m08-m09-corpus-atomic-20261114; HEAD NOT_READ | HOLD_HUMAN / high | no licensing review this run | Clinical/legal: atom provenance | all published atoms licensed |
| CE-WORKSPACE | PR #71 historical HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d; current NOT_READ | HOLD_VERIFY / medium | CI NOT_RUN | Frontend: verify latest checks | required checks PASS |
| CE-EXPORT | docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115; manifest historical 8099e3ff; 22/22 hashes | PASS_HASH historical / low | not rehashed without delta | Audit: compare changed blobs only | stable fingerprint manifest |
| CE-DB-GOV | pg_constraint c61 f81 p88 u34 =264 | PASS_AGGREGATE / object HOLD | SELECT 2026-11-18 | DB architecture: PK/FK identity mapping | individual matches |
| CE-DB-GLOBAL | historical export 1996; previously reported live 2109, +113 unproven | HOLD_SEMANTIC / high | 0/1996 object comparisons this run | DB architecture: scope/definition matching | every object classified |

## Progress by layer (this execution unless historical)
- CID11 selected correction 1/1 PASS_STATIC, **not** clinical homologation.
- Export integrity 22/22 = 100% **historical**; no fingerprint reprocessing.
- Governance aggregate 1/1 SELECT PASS; individual historical constraints 0/1996 reconciled this round.
- Previous PR #73 CI 3/4 PASS, 1 FAIL (historical); CI on new HEAD NOT_RUN.
- Clinical tool homologation 0/24 this round; parsers fixed 0/16; imports fixed 0/5.
- PR #71 and four priority branch HEADs NOT_READ this round.
- Local unit/adversarial tests NOT_RUN.
- **Global completion estimate: NOT_ESTIMABLE**, acceptance denominator not established; inventory is not homologation.

## Next safe actions
Inspect latest CI on CID11 commit and checkpoint commit; reconcile remaining five source contracts against their respective policy JSON; inspect parser branch contents before any copy; compare DB PK/FK by object identity and canonical definition with SELECT only. No blocked merge or publication.
