# CE / CKO / NCOS — WO 2026-11-17 03:54 BRT — trigger execution privilege boundary

Status: PASS_CATALOG / HOLD_SECURITY. Physical truth: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. SELECT-only. No DDL/DML.

## Checkpoint and delta
Previous verified Git commit: `553d0c93302c1ebd755863d9bfaded83b8ee611b`. Prior object fingerprint MD5(prosrc): `bfd24b5c361d73bb706c797133ad9b0c`; **not directly comparable** to this round's MD5(pg_get_functiondef), `46e2f53d4f434dbe3eb319a47f8ef8f9`. Do not classify this as code change without equal-algorithm comparison. The Git audit branch was 58 ahead / 0 behind main before this commit; main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.

Live SELECT against pg_proc/pg_namespace for `cko_governance.guard_material_finding_closure_learning_v1()`: owner `postgres`; SECURITY DEFINER=true; effective function EXECUTE privilege checks for `anon`, `authenticated`, `service_role` all returned **true**. This corrects any assumption that EXECUTE is unavailable, but a trigger function's EXECUTE privilege alone does not establish an independently callable route or ability to UPDATE its table. Investigate pg_trigger, table ACL, schema USAGE, caller identity and the trusted source of `cko.agent_id` before claiming exploitability. No privileged function invoked.

## Work register
| Object/branch | SHA/fingerprint and delta | Status/risk | Owner, test, next action, acceptance |
|---|---|---|---|
| `cko_governance.guard_material_finding_closure_learning_v1()` | MD5(functiondef) `46e2f53d4f434dbe3eb319a47f8ef8f9`; previous MD5(prosrc) `bfd24b5c361d73bb706c797133ad9b0c` (different methods) | HOLD_SECURITY / high | Security+DBA: verify schema/table ACL, trigger firing context and untrusted session GUC; isolated fail-closed spoof/missing-ID tests required |
| `feat/ce-tools-governed-backend-20261115` | main compare 14 ahead/0 behind, 33 changed files | HOLD_VERIFY / high | Engineering+clinical: reconcile 24 tools, tests and safety gates before integration |
| `feat/cko-catalog-metamodel-automated-20261114` | 22 ahead/0 behind, 48 changed files | HOLD_VERIFY / high | Data architecture: compare canonical PK/FK and semantic dictionary |
| `feat/cko-m08-m09-corpus-atomic-20261114` | 8 ahead/0 behind, 8 changed files | HOLD_PROVENANCE / high | Editorial/legal: source licenses and atom fingerprint delta |
| `integration/cko-parsers-catalog-20261114` | 163 ahead/0 behind, 175 changed files | HOLD_VERIFY / high | Engineering: parser contracts, dedup and tests |
| `audit/ce-supabase-migration-first-20261115` | 58 ahead/0 behind before current commit | PASS_GIT_READ / medium | Engineering: review and CI before PR merge |
| `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/README.md` | previous blob SHA `a0e074bf9da401a3d50dd761536bcad3a9b96150`; content read, no semantic delta asserted | PASS_READ / HOLD_SEMANTIC | DBA: reconcile source inventory against current catalog |
| PR #73; workspace PR #71 | HEAD and checks not fetched this round | NOT_RUN / medium | Engineering: fetch PR HEAD/checks and review |

## Coverage and tests
- Live PostgreSQL SELECT: **1/1 PASS**. Function ACL flags: **3/3 returned true**, not authorization certification.
- Branch comparison: **5/5 PASS_READ** (four priorities + audit), not code/semantic approval.
- Direct-export historical inventory: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. NOT recounted; export is not backup.
- Clinical homologation: historical **0/24**; semantic contracts historical **0/20**. Not revalidated in this round.
- Unit tests 0 NOT_RUN; CI 0 NOT_RUN; dynamic security tests 0 NOT_RUN. No functional code fix in this round.
- Global completion: **not estimable** (no consolidated accepted-criteria denominator). Inventory coverage must not be confused with homologation.

## Blocking gates
HOLD_SECURITY on session identity and indirect privileged paths; HOLD_HUMAN clinical/legal/provenance; no migration, merge, production publish or destructive changes authorized. Next independent task: inspect priority branch file deltas and write regression tests in a dedicated branch; maintain fingerprint-based no-reprocessing policy.
