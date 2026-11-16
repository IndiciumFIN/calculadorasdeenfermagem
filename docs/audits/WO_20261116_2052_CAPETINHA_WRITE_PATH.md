# CE/CKO/NCOS — WO 2026-11-16 20:52 BRT — CAPETINHA write-path triage

**State:** PASS_CATALOG / HOLD_SECURITY / HOLD_HUMAN. **Target physical database:** Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` (PostgreSQL 17). All database statements in this round were SELECT on catalogs; no routine invoked, no migration/DDL/DML/seed/merge/deploy.

## Checkpoint and immutable references
- Previous PR #73 head: `69314e609c98dc0fa14919570521eda8bd1ee9db` (open/draft, base main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`); workspace PR #71 open/draft. Do not merge.
- Physical catalog definition fingerprint: `md5(pg_get_functiondef(cko_validation.run_capetinha_scan_v1())) = c8fde3f1bb9dfdb64eb31000f7109387`. This is a **PostgreSQL MD5 fingerprint of function definition**, not a SHA-256 of a repository file.
- Prior cross-schema scan WO `WO_20261116_1957_CROSS_SCHEMA_DDL_SCAN.md`: 4 text references; this round inspects the **newly discovered function only**, not previously validated fingerprints.
- Direct export reference `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/`: previously recorded 59 schemas, 678 relations (including 17 sequences), 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. **Not re-counted in this round.**

## Object delta and evidence
| Branch/object | Fingerprint / SHA | Delta | Status | Risk | Test / owner / next action |
|---|---|---|---|---|---|
| `cko_validation.run_capetinha_scan_v1()` | DB function MD5 `c8fde3f1bb9dfdb64eb31000f7109387` | Prior text-reference scan did not establish effects. **Actual PL/pgSQL body INSERTs** into `cko_validation.capetinha_scan_runs` and `cko_validation.capetinha_observations`, and invokes `cko_validation.capetinha_raise_finding_v1` | PASS_STATIC / HOLD_SECURITY | HIGH: side effects if invoked; prior negative textual write-pattern result was a false negative | SELECT catalog PASS; dynamic invocation NOT_RUN. Security reviewer: trace nested function, triggers and grants, verify transactional/idempotency properties in isolation |
| `cko_validation.run_capetinha_scan_v1()` grants | same MD5 | `SECURITY DEFINER`, owner `postgres`, configured `search_path`, `provolatile='v'`; effective EXECUTE false for both `anon` and `authenticated`, and schema USAGE false | PASS_ACL_SCOPE / HOLD_REACHABILITY | HIGH: indirect privileged callers not excluded | SELECT catalog PASS; inspect invocation graph and service/admin roles without calling function |
| `feat/ce-tools-governed-backend-20261115` | unchanged / SHA NOT_RECHECKED | 24 tools remain candidates | HOLD_HUMAN | Clinical/legal | 0/24 homologated from previous checkpoint; inspect independently |
| `feat/cko-catalog-metamodel-automated-20261114`, `feat/cko-m08-m09-corpus-atomic-20261114`, `integration/cko-parsers-catalog-20261114` | NOT_RECHECKED | no claims of new validation | HOLD_VERIFY | Semantic/provenance | owner: CKO reviewers; compare source hashes and test deltas |
| Workspace PR #71 | OPEN/DRAFT (GitHub read this round) | no release | HOLD_BUILD_OUTPUT_API | Deployment | owner: workspace CI; verify Nitro output config before any deployment |

**Important correction:** `run_capetinha_scan_v1` is not read-only. Never run `SELECT cko_validation.run_capetinha_scan_v1()` for inspection: a SELECT that invokes this VOLATILE function performs writes. The previous cross-schema string-search finding 'no direct writes matched' must not be treated as a safety clearance. The current static check establishes two direct INSERT targets, but **not** exhaustive nested effects.

## Acceptance and progress
- Catalog inspection of newly prioritized function: **1/1 PASS** (100% *inspection only*).
- Function dynamic authorization/reachability: **0/1 approved** (0%; HOLD_SECURITY).
- Clinical tools: **0/24 approved** (0%; carried forward, not retested).
- Semantic contracts: **0/20 approved** (0%; carried forward, not retested).
- Physical inventory: **678/678 previously counted**, NOT_RUN this round, not semantic approval.
- Overall completion estimate: **NOT ESTIMABLE**; no audited denominator of cross-layer acceptance criteria.
- Tests: SELECT catalog **2 PASS**, code unit/CI **NOT_RUN**, dynamic function **NOT_RUN**. No failed query this round.
- Release criteria: proof of invocation graph, isolation/rollback/idempotency, authorization and least privilege, privacy/provenance and clinical/legal sign-off; fail closed until satisfied.
- Next independent WO: inspect `capetinha_raise_finding_v1` definition/ACL and static caller graph, then re-evaluate the misleading lexical SQL scan guard with negative fixtures. Do not mutate the physical database.

Sources: Supabase PostgreSQL catalogs `pg_proc`, `pg_namespace`, `pg_get_functiondef`, `has_function_privilege`, `has_schema_privilege`, queried 2026-11-16; GitHub PR #73 and workspace PR #71 fetched 2026-11-16. No external normative source consulted this round.
