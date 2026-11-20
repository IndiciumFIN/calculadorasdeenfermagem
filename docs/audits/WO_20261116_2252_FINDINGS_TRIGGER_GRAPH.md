# CE / CKO / NCOS — WO 2026-11-16 22:52 BRT — findings trigger graph

Status: PASS_CATALOG / HOLD_SECURITY. Source of physical truth: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. No production writes.

## Checkpoint and delta
Parent verified: `docs/audits/WO_20261116_2150_CAPETINHA_NESTED_UPSERT.md`, blob SHA `ac17c198a11e079e8030e21855f34038ba1d3a5c`, commit `cb0b613e84ed6af4a70939b1f69e0cf964335fdb` verified with GitHub fetch. Parent function definition fingerprint MD5 `4db7fb182121c0aacda9aae9592793de` (not reprocessed). This round extends the effect graph to table constraints and triggers.

## Physical PostgreSQL evidence (SELECT only)
- `cko_validation.findings`: primary key `findings_pkey` on `finding_id`; FK `findings_validation_run_id_fkey` on `validation_run_id` referencing `cko_validation.runs(validation_run_id)`.
- RLS disabled; FORCE RLS disabled; 0 policies. This is a **security review flag**, not proof of public access.
- 3 non-internal triggers and 2 internal FK triggers, all enabled `O`.
- User triggers: `cko_enqueue_material_finding_learning` -> `cko_governance.enqueue_material_finding_learning_v1`; `cko_guard_material_finding_closure_learning` -> `cko_governance.guard_material_finding_closure_learning_v1`; `cko_route_material_finding_super` -> `cko_governance.route_material_finding_to_super_v1`.
- Internal triggers: `RI_FKey_check_ins` and `RI_FKey_check_upd`.
- Columns definition fingerprint MD5 `cdae7d8eb8cc545155525fcdd7b26f41` from ordered `pg_attribute` signature. Trigger function body fingerprints (`md5(prosrc)`, **not** `md5(pg_get_functiondef)`): enqueue `1664d7596f034eef66ca8507e95c77da`, guard `bfd24b5c361d73bb706c797133ad9b0c`, route `dc8a3838886f7f2ba9a3f38631866242`.
- Static `prosrc ILIKE` search for `capetinha_raise_finding_v1` returned one caller: `cko_validation.run_capetinha_scan_v1`, source MD5 `9a35c50128b0ae7ba61737e3eb0ae0d8`; textual search is not a complete call graph.

## Work-order register
| Branch/object | SHA / fingerprint | Delta | Status | Risk | Test / owner / next action |
|---|---|---|---|---|---|
| `cko_validation.findings` | columns MD5 `cdae7d8eb8cc545155525fcdd7b26f41` | 2 constraints, 5 triggers, RLS off | PASS_CATALOG / HOLD_SECURITY | HIGH, nested effects and RLS | 3 SELECT PASS, 1 initial SQL FAIL corrected; security owner: examine ACL, trigger bodies and write reachability |
| `cko_governance.enqueue_material_finding_learning_v1` | prosrc MD5 `1664d7596f034eef66ca8507e95c77da` | discovered trigger | HOLD_SECURITY | HIGH | security owner: inspect transitive writes |
| `cko_governance.guard_material_finding_closure_learning_v1` | prosrc MD5 `bfd24b5c361d73bb706c797133ad9b0c` | discovered trigger | HOLD_SECURITY | HIGH | security owner: verify status transitions |
| `cko_governance.route_material_finding_to_super_v1` | prosrc MD5 `dc8a3838886f7f2ba9a3f38631866242` | discovered trigger | HOLD_SECURITY | HIGH | security owner: inspect queue/event effects |
| `feat/ce-tools-governed-backend-20261115` | SHA NOT_RECHECKED | no verified delta | HOLD_HUMAN | clinical | clinical reviewer: 24 contract acceptance tests |
| `feat/cko-catalog-metamodel-automated-20261114`, `feat/cko-m08-m09-corpus-atomic-20261114`, `integration/cko-parsers-catalog-20261114` | SHA NOT_RECHECKED | no verified delta | HOLD_VERIFY | provenance | CKO owner: reconcile fingerprints |
| CE PR #73; workspace PR #71 | SHA NOT_RECHECKED | no verified delta | HOLD_VERIFY | release | CI owner: verify heads, checks and conflicts |

## Measured coverage, tests, acceptance
- Target table constraints: 2/2 cataloged (PASS inventory, not security signoff); triggers: 5/5 cataloged (PASS inventory).
- This round: 3 SELECT queries PASS; 1 exploratory SELECT FAIL (`pg_get_functiondef` filter issue), corrected by `prosrc` query PASS. Unit tests / CI NOT_RUN; dynamic invocation NOT_RUN.
- Historical inventory only, not recounted: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies.
- Clinical approvals: 0/24 carried forward; semantic contracts: 0/20 carried forward. Global completion estimate: NOT ESTIMABLE (no accepted denominator).
- Acceptance: verify trigger bodies and downstream side effects, ACL/RLS and caller privileges, isolated rollback/idempotency/status transitions, source provenance, clinical/legal/security approval. Fail-closed; no publication of candidates.
- No DDL/DML, migrations, seeds, production function invocation, ACL edits, merges or branch deletion. No functional correction or CI in this round.
- Sources: PostgreSQL catalogs `pg_constraint`, `pg_trigger`, `pg_proc`, `pg_class`, `pg_namespace`, `pg_attribute`, `pg_policy` via SELECT on 2026-11-16; GitHub parent commit and file fetched 2026-11-16. No external normatives used.
