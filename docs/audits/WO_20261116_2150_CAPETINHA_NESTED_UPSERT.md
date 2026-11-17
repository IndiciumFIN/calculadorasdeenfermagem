# CE/CKO/NCOS — WO 2026-11-16 21:50 BRT — nested CAPETINHA write-path

State: PASS_STATIC / PASS_ACL_CATALOG / HOLD_SECURITY. Physical source of truth: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. No DDL, DML, migrations, seeds, function invocation, deployment, or merge.

## Checkpoint, SHA and delta
- Parent checkpoint: `docs/audits/WO_20261116_2052_CAPETINHA_WRITE_PATH.md`, blob SHA `587b29e90c7190eb14f8c926ad94fe59dfbd2993`; prior branch commit `c55568c26e07e97f3767f0a88b27e4d0fc884ebd` (from prior checkpoint, not independently refetched as branch HEAD).
- Newly examined DB object: `cko_validation.capetinha_raise_finding_v1(text,text,text,text,jsonb)`; definition MD5 `4db7fb182121c0aacda9aae9592793de` from `md5(pg_get_functiondef(p.oid))`. This is a DB definition fingerprint, not Git SHA.
- Delta: nested callee of `run_capetinha_scan_v1` performs `INSERT INTO cko_validation.findings ... ON CONFLICT(finding_id) DO UPDATE`, and returns deterministic `FIND-CAP-` plus first 20 MD5 hex characters of `rule_id|subject_ref`. This is a **third direct write target** in the transitive path, beyond `capetinha_scan_runs` and `capetinha_observations` identified previously.
- Upsert preserves `OPEN_SCOPED%` and `CLASSIFIED_HOLD%` statuses, otherwise resets status to `OPEN`; inspect workflow safety and collision semantics. Do not treat deterministic ID as proof of end-to-end idempotency.
- `SECURITY DEFINER`, owner `postgres`, `search_path=pg_catalog, cko_validation`, VOLATILE; explicit ACL `{postgres=X/postgres}`. Effective EXECUTE for `anon`, `authenticated`, `service_role`: false. Schema USAGE for `anon` and `authenticated`: false. Direct execution by these roles is not established; privileged indirect callers remain unverified.

## Register and acceptance
| Branch / object | Fingerprint / SHA | Delta | Status | Risk | Test, owner and next action |
|---|---|---|---|---|---|
| `cko_validation.capetinha_raise_finding_v1` | DB MD5 `4db7fb182121c0aacda9aae9592793de` | Nested UPSERT into `findings` | PASS_STATIC / HOLD_SECURITY | HIGH: status transitions and privileged indirect invocation | 2 SELECT catalog queries PASS; security reviewer: trace callers, triggers, constraints and RLS; isolated transactional fixtures for conflict/status preservation |
| `cko_validation.run_capetinha_scan_v1` | DB MD5 `c8fde3f1bb9dfdb64eb31000f7109387` from previous WO | Transitive third write target | HOLD_SECURITY | HIGH | Do not invoke; owner: security and validation reviewers; derive full effect graph |
| `feat/ce-tools-governed-backend-20261115` | SHA NOT_RECHECKED | 24 candidates, no delta verified | HOLD_HUMAN | Clinical | Owner: clinical; validate 24 contracts individually |
| `feat/cko-catalog-metamodel-automated-20261114`, `feat/cko-m08-m09-corpus-atomic-20261114`, `integration/cko-parsers-catalog-20261114` | SHA NOT_RECHECKED | No delta verified | HOLD_VERIFY | Provenance/semantic | Owner: CKO; inspect only changed fingerprints |
| workspace PR #71 / CE PR #73 | NOT_RECHECKED this round | No merge | HOLD_VERIFY | CI/release | Owner: CI; refresh PR state and tests |

## Measured progress and gates
- Nested callee static inspection: 1/1 PASS (100% inspection, **not approval**).
- Nested callee dynamic authorization: 0/1 homologated, HOLD_SECURITY.
- Prior inventory: 678/678 relations counted, **not re-counted**; prior 59 schemas, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies are historical, not newly verified.
- Clinical tools: 0/24 homologated (carried forward); semantic contracts: 0/20 homologated (carried forward).
- This round: PostgreSQL catalog SELECT 2 PASS, 0 FAIL; unit/CI NOT_RUN; dynamic invocation NOT_RUN.
- Overall completion estimate: **NOT ESTIMABLE** (acceptance denominator not established).
- Acceptance: complete caller/effect graph, prove least privilege and status-transition safety, verify isolated idempotency and rollback, clinical/legal/LGPD/provenance signoff; fail-closed, candidate not published.
- Next independent task: inspect `cko_validation.findings` constraints/triggers and callers of the nested function, then implement static regression tests in a code branch without touching production data.

Sources: PostgreSQL `pg_proc`, `pg_namespace`, `pg_get_functiondef`, `has_function_privilege`, `has_schema_privilege` via read-only SELECT, 2026-11-16. GitHub checkpoint file fetched 2026-11-16. No external normatives used.
