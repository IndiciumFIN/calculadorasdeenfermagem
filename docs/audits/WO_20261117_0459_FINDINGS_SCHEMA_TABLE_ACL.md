# CE / CKO / NCOS — WO 2026-11-17 04:59 BRT — ACL table/schema boundary

Status: PASS_CATALOG / HOLD_SECURITY. Physical source: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Queries strictly SELECT. No writes, migrations, merges or publication.

## Checkpoint and delta
Previous checkpoint commit `e98aa490eab44c050e68ed1c1fd46dd94e78da1a`; audit branch comparison before this commit: 59 ahead / 0 behind main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. Previous function fingerprint MD5(prosrc) `bfd24b5c361d73bb706c797133ad9b0c` **not recomputed**; no claim of changed function definition. Historical inventory README Git blob SHA `a0e074bf9da401a3d50dd761536bcad3a9b96150`, fetched this round and unchanged relative to prior checkpoint.

Two live SELECT-only catalog queries on `cko_validation.findings`: relrowsecurity=false; has_schema_privilege(USAGE) for anon/authenticated/service_role=false for all 3; has_table_privilege(UPDATE) for these roles=false for all 3. 6/6 role/object permission flags false (3 schema USAGE + 3 table UPDATE). This narrows direct-access exposure; **does not certify security** because SECURITY DEFINER, trigger invokers, role inheritance and indirect privileged paths remain. Earlier trigger function EXECUTE=true for 3 roles must not be conflated with direct UPDATE privilege. An exploratory query requested two additional table names in cko_validation but returned only findings; no inference about other schema locations.

## Versioned work register
| Branch/object/file | SHA/fingerprint and delta | Status/risk | Owner / test / next action / acceptance |
|---|---|---|---|
| `cko_validation.findings` | Live ACL/relrowsecurity result 2026-11-17 04:59 BRT; no prior equivalent ACL matrix | PASS_CATALOG / HOLD_SECURITY high | Security+DBA: inspect trigger source table and caller chain; isolated adversarial tests for session identity; accept only verified fail-closed behavior |
| `cko_governance.guard_material_finding_closure_learning_v1()` | Historical MD5(prosrc) `bfd24b5c361d73bb706c797133ad9b0c`; NOT rehashed | HOLD_SECURITY high | Security: establish trusted agent identity, check effective invoker and bypass routes |
| `feat/ce-tools-governed-backend-20261115` | Previous Git compare 14 ahead/0 behind, 33 files; not rechecked | HOLD_VERIFY high | Engineering+clinical: 24 tool contracts, test evidence, clinical gate |
| `feat/cko-catalog-metamodel-automated-20261114` | Previous compare 22 ahead/0 behind, 48 files; not rechecked | HOLD_VERIFY high | Data architecture: PK/FK, dictionary, metamodel semantic crosswalk |
| `feat/cko-m08-m09-corpus-atomic-20261114` | Previous compare 8 ahead/0 behind, 8 files; not rechecked | HOLD_PROVENANCE high | Editorial/legal: license, normatives and atom fingerprint delta |
| `integration/cko-parsers-catalog-20261114` | Previous compare 163 ahead/0 behind, 175 files; not rechecked | HOLD_VERIFY high | Engineering: parsers, regression tests and semantic dedup |
| `audit/ce-supabase-migration-first-20261115` | 59 ahead/0 behind main before this commit | PASS_GIT_READ medium | Engineering: assess checks and safe changes before PR integration |
| `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/README.md` | Git blob `a0e074bf9da401a3d50dd761536bcad3a9b96150` | PASS_READ / HOLD_SEMANTIC | DBA: compare live object hashes and inventory; no bulk reprocessing without delta |
| PR #73 and workspace PR #71 | HEAD/checks not fetched | NOT_RUN | Engineering: revalidate PR state, HEAD, CI and review gates |

## Coverage and evidence
- PostgreSQL catalog SELECT: 2/2 PASS. Direct-access matrix for findings: 6/6 flags checked; all false; this is **not** homologation.
- Export inventory (historical, not recounted): 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. Metadata snapshot, not backup.
- Clinical tools: historical 0/24 homologated; semantic contracts historical 0/20 homologated; both not retested.
- Unit tests: 0 NOT_RUN. CI: 0 NOT_RUN. Dynamic security tests: 0 NOT_RUN.
- Global completion: NOT ESTIMABLE; no accepted-criteria denominator. Do not equate extraction and certification.

## Gates and next actions
HOLD_SECURITY on `cko.agent_id` session trust and indirect privileged invocation. HOLD_HUMAN on clinical/legal/provenance. Continue independent branch/contract work and add isolated regression tests. No DDL/DML, seeds, migrations, merges, branch deletions, production publication, or grants authorized. Source: connected PostgreSQL catalogs, checked 2026-11-17; GitHub repository checkpoint and README fetched same round.
