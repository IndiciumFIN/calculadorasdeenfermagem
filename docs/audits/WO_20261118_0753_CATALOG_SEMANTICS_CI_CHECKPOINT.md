# CE / CKO / NCOS — checkpoint 2026-11-18 07:53 BRT

## Baseline and safeguards
Previous checkpoint commit: `84e3327e788adef793c945a960d866271773733d`; checkpoint blob `f71cda36b01f031e47bb922ea34ff16a43e43fdd`. Export MANIFEST.json Git blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`, 22/22 Git fingerprints PASS in previous round, unchanged and **not reprocessed**. Physical source exclusively Calculadoras-Smart `pgsybzggewhinaniybiy`; project confirmed ACTIVE_HEALTHY on 2026-11-18. Never use SOT, Neon, accounting, WU-TRIB. SELECT-only; no DDL/DML, migrations, seeds, merges, deploys or deletion.

## New measured delta — catalog discrepancy requiring semantic reconciliation
Two live SELECT-only PostgreSQL queries on 2026-11-18:
- `SELECT count(*) FROM pg_catalog.pg_constraint` => **2109**.
- Same catalog joined to `pg_namespace` filtered `nspname='cko_governance'` => **264**.
- `SELECT count(*) FROM information_schema.table_constraints WHERE table_schema='cko_governance'` => **1293**.
- `pg_constraint WHERE contype='f'` => **681** global FKs.
- Live `cko_governance` pg_constraint breakdown: check=61, foreign key=81, primary key=88, unique=34; sum **264**.
- Export of 2026-11-15: **1996** constraints across the historical inventory (59 schemas, 678 relations, 255 migrations, 7246 columns, 1268 indexes, 100 RLS policies).
**Do not conflate these figures**. Current pg_constraint total minus historical export = +113 objects numerically, but NOT a verified object-level delta. The 1293 information_schema rows vs 264 pg_constraint objects is a catalog-semantic discrepancy, not evidence of 1029 new constraints. Need exact object identity and visibility/partition/constraint mapping investigation before conclusions. No table creation or schema repair authorized.

## GitHub CI — confirmed on previous checkpoint commit
Commit `84e3327e788adef793c945a960d866271773733d`:
- CI - Validação: PASS, run 44280367751.
- Pipeline Determinístico: PASS, run 44280367770.
- CE Migration-first Supabase provenance (NO SQL): PASS, run 44280367889.
- Canonical repository invariants: FAIL, run 44280367820.
Canonical failed jobs: `Full admission blockers (fail closed)` (reject unresolved parser/import dependencies) and `Canonical contracts and CLI smoke` (verify canonical source/policy references). Compilation and deterministic negative tests passed in latter job. No rerun or local unit/adversarial tests this round. Do not promote.

## Priority branches and PRs
Branch existence verified by GitHub search this round: `feat/ce-tools-governed-backend-20261115`, `feat/cko-catalog-metamodel-automated-20261114`, `feat/cko-m08-m09-corpus-atomic-20261114`, `integration/cko-parsers-catalog-20261114`, and audit branch. Branch HEAD SHAs NOT_REVALIDATED. PR #73 and workspace PR #71: direct issue search did not return a matching result; state/HEAD/checks **NOT_VERIFIED**, not presumed closed or absent.

## Versioned work orders (delta / status / risk / test / owner / acceptance)
| WO / scope | SHA, fingerprint or delta | Status / risk | Tests this round | Owner / next action | Acceptance |
|---|---|---|---|---|---|
| CE-CATALOG-PG / live all schemas | live count 2109; historical 1996; numeric +113 only, no identity delta | HOLD_SEMANTIC / high | 2 scoped SELECT queries PASS | DB architecture: reconcile object-level namespace, table OID, name, type and definitions against 1996 export records | Every discrepancy classified with comparable scope and verified fingerprints |
| CE-CATALOG-GOV / cko_governance | pg_constraint 264 vs information_schema 1293, type counts 61/81/88/34 | HOLD_SEMANTIC / high | SELECT PASS | DB architecture: investigate catalog row semantics and partition/inheritance/visibility | Document exact reasons for count difference, no unexplained PK/FK |
| CE-CI-73 / canonical workflow | baseline 84e3327e; run 44280367820 FAIL | FAIL / high | 3/4 workflow PASS, 1 FAIL | Engineering: inspect logs, fix contracts and dependencies with tests | Mandatory CI all PASS on same HEAD |
| CE-PARSERS / integration branch | historical 16 parsers, 5 imports, current fingerprints NOT_VERIFIED | HOLD_VERIFY / high | NOT_RUN | Engineering: verify paths/imports, fix independently | Zero unresolved dependencies, CI PASS |
| CE-TOOLS-24 / tools branch | branch exists, HEAD NOT_VERIFIED | HOLD_HUMAN / high | NOT_RUN | Clinical engineering: contract and safety tests | 24/24 separately homologated |
| CE-METAMODEL / catalog branch | branch exists, HEAD NOT_VERIFIED | HOLD_SEMANTIC / high | NOT_RUN | CKO: PK/FK, dictionaries, metamodels | No unexplained semantic delta |
| CE-CORPUS / M08-M09 branch | branch exists, HEAD NOT_VERIFIED | HOLD_PROVENANCE / high | NOT_RUN | Editorial/legal: normative source, licensing, atom fingerprint dedup | All promoted atoms licensed and traced |
| CE-EXPORT-22 / 2026-11-15 snapshot | MANIFEST blob 8099e3ff; 22/22 previous PASS_HASH, no delta inspected | PASS_HASH historical / medium | NOT_RUN intentionally | Audit: physical/source consistency check | Same-scope independent physical reconciliation |
| CE-WORKSPACE / PR #71 | PR search no match, HEAD NOT_VERIFIED | HOLD_VERIFY / medium | NOT_RUN | PMO: inspect exact PR metadata/checks | Verified scope and CI |
| CE-PROVENANCE / normative FK | historical ON DELETE CASCADE; no new definition fingerprint | HOLD_HUMAN / high | NOT_RUN | Clinical/legal: retention assessment | Signed retention and provenance approval |

## Layer denominators and global estimate
- Export Git integrity: **22/22 = 100% historical PASS_HASH**, 0 repeated this round; not physical homologation.
- CI on previous commit: **3/4 = 75% workflow success**, global FAIL; current checkpoint CI NOT_RUN.
- Priority branch existence: **5/5 verified**; HEAD verification **0/5**, separate from existence.
- Live catalog counts: **2/2 targeted SELECT queries executed**; **0/1996** object-level historical export constraints reconciled in this round, not a claim about all-time work.
- Clinical tools: **0/24 approvals verified this round**, no inferred rejection.
- Parser/import corrections: **0/16** and **0/5** this round, historical issue counts not revalidated.
- PR HEADs: **0/2** verified this round.
- **Global completion estimate: NOT_ESTIMABLE** without common acceptance denominator and evidence.

## Changes, tests and next actions
Actual change: this versioned checkpoint; no functional code change. SELECT-only queries PASS; Git branch existence 5 PASS; previous commit workflow read 3 PASS/1 FAIL; local unit/adversarial NOT_RUN; PR HEAD NOT_VERIFIED. Next: obtain PR #73/#71 metadata and HEADs, read failed job logs, compare source validator contracts, reconcile pg_constraint object identities with export and SQL candidates, fix only verified code deltas and run CI. Fail-closed and clinical, legal, LGPD, security, copyright and provenance gates remain mandatory. Candidate material not published.
