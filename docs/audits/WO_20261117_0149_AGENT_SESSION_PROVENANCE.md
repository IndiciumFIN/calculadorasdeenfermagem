# CE / CKO / NCOS — WO 2026-11-17 01:49 BRT — agent session provenance

Status: PASS_STATIC / HOLD_SECURITY. Physical source exclusively Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. No database mutation, promotion or merge.

## Parent, provenance and delta
Parent: `docs/audits/WO_20261117_0053_AGENT_IDENTITY_TRUST_BOUNDARY.md`; last recorded commit `903fb95e949ef53f3a0300e892f3773a9cb099d0`. GitHub comparison main vs audit branch before this commit: ahead 56, behind 0; main SHA `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
Direct-export README checked on this branch: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies; historical inventory only, not a fresh count or homologation. README expressly excludes full data export and consistent snapshot/restore.

## New live PostgreSQL evidence (2026-11-17)
Initial SELECT against pg_proc using pg_get_functiondef across all routines failed (aggregate-function error); corrected to pg_proc.prosrc with prokind='f' and cko_% namespace. Corrected SELECT succeeded.
Query searched `prosrc ILIKE '%cko.agent_id%'` OR `prosrc ILIKE '%set_config(%'` in cko_% functions. Exactly **one** function matched: `cko_governance.guard_material_finding_closure_learning_v1()`, md5(prosrc) `bfd24b5c361d73bb706c797133ad9b0c`, unchanged from parent. The function requires validated learning controls for closure of material findings; separate Capetinha independence check depends on session `cko.agent_id` equaling `AGT-CAPETINHA-001` and finding ID prefix. No matching setter was found in this *restricted static search*. This does NOT prove absence of setters outside cko_% schemas, SQL dynamic calls, clients or session manipulation. No runtime adversarial test performed.

## Work register
| Branch/object | SHA/fingerprint | Delta | Status | Risk | Test / owner / next / acceptance |
|---|---|---|---|---|---|
| audit/ce-supabase-migration-first-20261115 | prior `903fb95e949ef53f3a0300e892f3773a9cb099d0` | 56 ahead / 0 behind before commit | PASS_GIT_READ | medium | Engineering: review accumulated diff and PR #73 checks before merge |
| closure guard | md5(prosrc) `bfd24b5c361d73bb706c797133ad9b0c` | no body delta; only expanded setter search | PASS_STATIC / HOLD_SECURITY | high | Security: inspect cross-schema setters, caller role ACL, adversarial isolated tests for missing/spoofed session setting; acceptance: identity derived from trusted authorization, fail-closed |
| direct export README | SHA not recorded in this run | verified limitations | PASS_READ / HOLD_SEMANTIC | medium | DBA: manifest verification and live semantic crosswalk before approval |
| tools branch (24 tools), metamodel, corpus M08/M09, parsers | HEAD/fingerprint not checked this run | none | NOT_RUN | high | Engineering: inspect branch SHAs, compare to main, tests and object-level semantic delta |
| PR #73 and workspace PR #71 | HEAD/checks not checked | none | NOT_RUN | high | Engineering: verify PR heads, status and CI before integration |

## Progress and gates
- Direct-export inventory: historical 678/678 relations documented, **not current live re-count**; no homologation inferred.
- Targeted static function search: 1/1 matched function inspected; scope limited to cko_% routines, not whole estate.
- Clinical tools: historical 0/24 homologated; current verification NOT_RUN.
- Semantic contracts: historical 0/20 homologated; current verification NOT_RUN.
- PostgreSQL catalog queries: 1 FAIL (initial scope/query), 1 PASS (corrected). Dynamic tests 0 NOT_RUN. CI 0 NOT_RUN.
- Overall percentage: **NOT ESTIMABLE** (no validated denominator across acceptance criteria).
- HOLD_SECURITY: session identity trust boundary and indirect write paths; HOLD_HUMAN: clinical/legal/provenance licensing; no candidate publication.
- No DDL/DML, migrations, seeds, grants, deploy, branch deletion or merge.

## Next safe work
1. Expand SELECT-only inspection to all non-system schemas for references to `cko.agent_id` and setters; inspect caller privileges and authorization source without executing effectful functions.
2. Independently reconcile priority branch heads and PR checks; select code-only test improvements with regression evidence.
3. Keep per-object fingerprints and delta gating, skip previously validated bodies without change. Preserve fail-closed and rollback requirements.
