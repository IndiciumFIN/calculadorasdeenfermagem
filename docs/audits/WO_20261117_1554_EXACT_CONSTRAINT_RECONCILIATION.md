# CE / CKO / NCOS — WO 2026-11-17 15:54 BRT — exact PK/FK export-to-catalog comparison

## Scope, provenance and safety
Source of truth: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Current database access: one SELECT over `pg_constraint`, `pg_class`, `pg_namespace`; no writes. GitHub source: `IndiciumFIN/calculadorasdeenfermagem`, branch `audit/ce-supabase-migration-first-20261115`. Prior checkpoint file blob `22f8cd4e053d56033ff200a5daf030a4d8db9671`; export manifest blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`; constraints export blob `83642780302397204b39796e1bd3604a77c68f53`. Historical export 2026-11-15 is NON_ATOMIC_ACROSS_QUERIES and HOLD_HUMAN. No Neon, SOT, accounting or WU-TRIB.

## Actual delta and reconciliation
Compared exact canonical tuple (schema, table, constraint name, constraint type, pg_get_constraintdef(..., true)) for the five targeted objects against `constraints.jsonl` (1996 JSONL records). **5/5 exact matches**, 0 missing, 0 extra within this narrowly scoped query, 0 definition differences. The preceding checkpoint had checked live definitions but had NOT compared the individual export records. This is a new comparison result, **not** evidence that deletion semantics or legal retention are safe. Physical delta: NONE OBSERVED for these five definitions since the 2026-11-15 export.

## Versioned work-order / fingerprint register
| WO | Branch/file/object | Fingerprint / evidence | Delta | Status | Risk | Test | Responsible / next action | Acceptance |
|---|---|---|---|---|---|---|---|---|
| CE-REF-01 | `cko_governance.architecture_layer_bindings_pkey` | export blob `83642780...`; `PRIMARY KEY (profile_id, architecture_layer_id, implementation_layer_id)` | exact export/live match | PASS_DEFINITION / HOLD_SEMANTIC | medium | 1/1 SELECT comparison PASS | metamodel owner: reconcile code persistence and candidate SQL | all 3 key columns correctly handled |
| CE-REF-02 | `cko_governance.artifact_normative_bindings_artifact_id_fkey` | export blob `83642780...`; FK controlled_artifacts ON DELETE CASCADE | exact match; no proven physical delta | PASS_DEFINITION / HOLD_PROVENANCE | high | 1/1 SELECT comparison PASS; deletion tests NOT_RUN | provenance/security: prove immutable audit and retention without destructive tests on production | no loss of normative traceability |
| CE-REF-03 | `artifact_normative_bindings` version FK, unique and PK | export blob `83642780...`; three matching definitions | 3/3 exact matches | PASS_DEFINITION / HOLD_SEMANTIC | medium | 3/3 SELECT comparison PASS | metamodel owner: verify unique identity, null semantics and version links | dictionary and code agree |
| CE-TOOLS-24 | `feat/ce-tools-governed-backend-20261115` | main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; 15 ahead/0 behind; 33 files | no compare-count delta vs preceding checkpoint | HOLD_TEST | high | Git compare PASS; isolated verifier tests NOT_RUN | backend: deterministic/adversarial test suite | 24/24 gated tools and repeatable manifests |
| CKO-META | `feat/cko-catalog-metamodel-automated-20261114` | previous 22 ahead / 48 files (not rechecked this run) | unknown | HOLD_VERIFY | medium | NOT_RUN | catalog owner: SQL/code dictionary alignment | 20/20 contracts evidenced |
| CKO-ATOMS | `feat/cko-m08-m09-corpus-atomic-20261114` | previous 8 ahead / 8 files (not rechecked) | unknown | HOLD_PROVENANCE | high | NOT_RUN | editorial/clinical: source and rights audit | every atom licensed and traced |
| CKO-PARSERS | `integration/cko-parsers-catalog-20261114` | previous 163 ahead / 175 files (not rechecked) | unknown | HOLD_TEST | medium | NOT_RUN | parser owner: isolated deterministic tests | validated extraction |
| CE-PR73 / WORKSPACE-PR71 | PRs #73 and #71 | previous draft/open metadata; HEAD and CI not rechecked | unknown | HOLD_MERGE | high | NOT_RUN | integrator: HEAD, CI, security and rollback review | gates met before merge |

## Progress, scope and limitations
- Targeted export/live definition reconciliation: **5/5 (100% of 5 selected definitions)**, PASS_DEFINITION; semantic approval 0/5 (not yet approved).
- Full exported table constraints: **5/1996 (0.25%)** exact definitions checked by this round's methodology; other 1991 not checked. This is coverage, not homologation.
- Git branch comparison: **1/4 (25%)** rechecked this round; other 3 previous evidence only.
- Clinical tools: **0/24 homologated** per historical record, NOT_REVALIDATED; semantic contracts **0/20** historical, NOT_REVALIDATED.
- Unit tests / adversarial tests / CI: NOT_RUN. Database SELECT: 1/1 PASS. File reads: 3/3 PASS.
- Global completion estimate: **NOT ESTIMABLE**; cross-layer acceptance denominator missing.
- Historical physical inventory (not recounted): 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 table constraints, 1268 indexes, 100 RLS policies.

## Next independent work
Batch the remaining 1991 constraints by canonical key and normalized definition without rechecking these five absent fingerprint delta; compare candidate SQL, code and dictionary; test verifier determinism in isolated environment; fetch PR HEAD/checks. Preserve fail-closed, clinical/legal/LGPD/copyright gates. No DDL, DML, migrations, seeds, deployment, merge or deletion authorized.
