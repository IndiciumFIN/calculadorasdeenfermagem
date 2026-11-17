# CE / CKO / NCOS — WO 2026-11-17 05:57 BRT — trigger boundary and branch refresh

Status: PASS_CATALOG / PASS_GIT_READ / HOLD_SECURITY / HOLD_CLINICAL. Source of physical truth: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. All database queries SELECT only. No DDL/DML, migrations, seeds, merge, deploy or permission changes.

## Checkpoint and verified delta
Prior Git commit `88ffc041fc61338de294fdd79547ac57eb14c483` (2026-11-17 04:59 BRT). Prior WO blob SHA `ac6bf3782f1fad2c894c3a5d6cd4321db6897d07`. Prior function MD5(prosrc) `bfd24b5c361d73bb706c797133ad9b0c` NOT rehashed; no detected delta claimed.

Live PostgreSQL catalog SELECT confirmed trigger `cko_guard_material_finding_closure_learning` is **BEFORE UPDATE OF status FOR EACH ROW** on `cko_validation.findings`, executing `cko_governance.guard_material_finding_closure_learning_v1()`. This clarifies the precise trigger firing condition; it does NOT demonstrate protection of other UPDATE paths, bypass resistance, or trusted agent identity.

Live privilege SELECT rechecked 3 roles (anon, authenticated, service_role) × 5 flags (schema USAGE, table SELECT/INSERT/UPDATE/DELETE): 15/15 evaluated, all false. This is an ACL inventory, NOT security homologation. Indirect privileged execution remains untested.

## Versioned register (Git comparisons to main; refreshed 2026-11-17)
| Object/branch | SHA / fingerprint / delta | Status, risk | Owner, next test and acceptance |
|---|---|---|---|
| `cko_validation.findings` trigger | Catalog definition above, new firing-scope evidence; SQL 1/1 PASS | PASS_CATALOG / HOLD_SECURITY high | Security+DBA: inspect privileged writers, trigger enablement, adversarial isolated UPDATE tests; fail-closed acceptance |
| `cko_validation.findings` ACL | 15/15 privilege flags false; prior 6/6 expanded | PASS_CATALOG / HOLD_SECURITY high | DBA: audit indirect SECURITY DEFINER paths and role inheritance |
| `cko_governance.guard_material_finding_closure_learning_v1` | Historical MD5 `bfd24b5c361d73bb706c797133ad9b0c`, not reprocessed | HOLD_SECURITY high | Security: prove trusted `cko.agent_id` and cannot spoof; isolated tests |
| `feat/ce-tools-governed-backend-20261115` | 14 ahead / 0 behind main; 33 changed files; no Git delta from prior | HOLD_CLINICAL high | Engineering+clinical: verify 24 tool contracts and source provenance, acceptance per tool |
| `feat/cko-catalog-metamodel-automated-20261114` | 22 ahead / 0 behind; 48 files; no Git delta | HOLD_VERIFY high | Data architecture: semantic PK/FK/dictionary/metamodel crosswalk |
| `feat/cko-m08-m09-corpus-atomic-20261114` | 8 ahead / 0 behind; 8 files; no Git delta | HOLD_PROVENANCE high | Editorial/legal: license and atomic source trace |
| `integration/cko-parsers-catalog-20261114` | 163 ahead / 0 behind; 175 files; no Git delta | HOLD_VERIFY high | Engineering: parser tests, dedup and regression |
| `audit/ce-supabase-migration-first-20261115` | 60 ahead / 0 behind; 71 files before this commit; prior 59 ahead, +1 WO commit | PASS_GIT_READ / HOLD_MERGE | Engineering: check PR #73 HEAD/checks, no blocked merge |
| `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/README.md` | Historical blob SHA `a0e074bf9da401a3d50dd761536bcad3a9b96150`; not refetched | HOLD_SEMANTIC | DBA: compare live catalog hashes on delta only |
| PR #73; workspace PR #71 | GitHub search found both PR URLs; HEAD/checks not retrieved | HOLD_VERIFY | Engineering: fetch PR HEAD, CI and gates before merge |

## Progress and tests
- PostgreSQL: 2/2 SELECT PASS; trigger mapping 1/1; privilege flags 15/15 evaluated (all false).
- Git: 5/5 branch comparisons PASS_READ. This is topology only, not semantic approval.
- Historical export inventory (not recounted): 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies.
- Clinical homologation: historical 0/24 tools; semantic contracts historical 0/20; neither retested.
- Unit tests 0 NOT_RUN; CI 0 NOT_RUN; dynamic security 0 NOT_RUN.
- Global completion estimate: **NOT ESTIMABLE**; no consolidated acceptance denominator. Physical inventory must not be counted as certification.

## Controls
HOLD_SECURITY: agent identity via session setting, indirect privileged paths and trigger scope. HOLD_HUMAN: clinical, legal, licensing and provenance. Candidate not published. Next independent WO: inspect code contracts and static regression tests for 24 tools and parser catalog; preserve fingerprints without delta. Official sources: connected PostgreSQL system catalogs and GitHub compare API, checked 2026-11-17.
