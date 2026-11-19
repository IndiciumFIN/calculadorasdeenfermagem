# CE / CKO / NCOS — checkpoint 2026-11-19 12:52 BRT

## Immutable baseline and scope
- PR #73: DRAFT, OPEN, head `audit/ce-supabase-migration-first-20261115` at `b10f9a9d07a119822ff5d7fe14cb713bad950f54` before this checkpoint; base `main` `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Previous program: `docs/audits/WO_20261119_1152_CI_ADMISSION_RECHECK.md`, blob `b3e4ea945b4209cc14f339a1ed94a5a4b833e577`.
- Supabase truth: Calculadoras-Smart `pgsybzggewhinaniybiy` ONLY. SELECT-only query on `pg_constraint` and `pg_namespace`; no database mutation.
- Export manifest `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`, 22 source files, NON_ATOMIC_ACROSS_QUERIES / HOLD_HUMAN; `constraints.jsonl` declared blob `83642780302397204b39796e1bd3604a77c68f53`.
- Historic inventory (not approval): 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies.

## CI evidence on baseline SHA
- PASS `44548656254` CE provenance; PASS `44548656385` deterministic pipeline; PASS `44548656188` CI validation.
- FAIL `44548656159` canonical invariants, jobs `135646052586` and `135646053245`. Read both complete logs. Compilation and deterministic negative tests PASS; CLI import and Kernel registry smoke SKIPPED because prior guard failed.
- Exact guard report: 20 source contracts, 20 kernel policies, 1 ERROR (`contracts/fonts`) and 19 PENDING (16 missing parser paths, 3 namespace findings). **Do not report 5 outstanding namespace findings**: current report contains exactly 3, at `packages/cli/kernel/__init__.py`, `packages/cli/kernel/core.py`, `packages/cli/validators/registry.py`. Earlier count 5 is historical, not current.
- Two previously edited CLI files were inspected: `packages/cli/main.py` blob `bec5bfa0db972988495dd847c4a4df4c7887a2ee`; `packages/cli/kernel/cli.py` blob `66c9efb6e6e47c228d1a261f82af6b47e53c84c3`. Both use `packages.cli.*` imports; no claim of executable smoke PASS.
- No bypass of canonical guard. Exit code 2 is the intended fail-closed behavior.

## SELECT-only physical counts by schema and constraint type
| schema | CHECK | FK | PK | UNIQUE | total |
|---|---:|---:|---:|---:|---:|
| ce_platform | 3 | 135 | 96 | 18 | 252 |
| cko_governance | 61 | 81 | 88 | 34 | 264 |
| public | 53 | 71 | 48 | 25 | 197 |
| selected total | 117 | 287 | 232 | 77 | 713 |

No new individual constraint equivalence verified; prior historical crosswalk 8/1996 (0.40%). No reprocessing of validated fingerprints.

## Work orders / immutable object registry
| WO | Object, SHA/fingerprint | Delta this run | Status | Risk | Test | Owner / next action | Acceptance |
|---|---|---|---|---|---|---|---|
| CE-CI-01 | run 44548656159; jobs 135646052586/135646053245 | current 1 ERROR + 19 PENDING confirmed | FAIL | high | compile PASS; negative PASS; smoke SKIPPED | engineering: repair root cause, never disable guard | same SHA all required CI and smoke PASS |
| CE-CLI-02 | main.py bec5bfa0; kernel/cli.py 66c9efb6 | verified canonical imports; 3 remaining paths specifically identified | HOLD_HUMAN | high | static read PASS, executable NOT_RUN | engineering: inspect __init__.py, core.py, validators/registry.py and add negative/smoke tests | 3/3 paths resolved, CLI/Kernel smoke PASS |
| CE-PARSER-03 | integration/cko-parsers-catalog-20261114; 16 parser paths | 16 still missing in current guard | FAIL | high | NOT_RUN | engineering: port verified parsers selectively with source/license checks | 16/16 tested, no stubs |
| CE-TOOLS-04 | feat/ce-tools-governed-backend-20261115 | no validated delta | HOLD_HUMAN | clinical | NOT_RUN | clinical engineering: 24 tools safety tests | 24/24 approved |
| CE-META-05 | feat/cko-catalog-metamodel-automated-20261114 | no validated delta | HOLD_HUMAN | high | NOT_RUN | data governance: PK/FK, dictionary crosswalk | approved object-by-object |
| CE-CORPUS-06 | feat/cko-m08-m09-corpus-atomic-20261114 | no validated delta | HOLD_HUMAN | clinical/legal | NOT_RUN | editorial/legal: provenance and rights | accepted source-backed atoms |
| CE-DB-07 | MANIFEST 8099e3ff; constraints.jsonl 83642780 | 713 grouped physical constraints read; no object match | HOLD_HUMAN | high | SELECT PASS_READ | data engineering: fingerprint-based PK/FK comparisons | 1996/1996 audited with semantic deltas |
| CE-WS-08 | dev-chatgpt-workspace PR #71 | no new verification | HOLD_HUMAN | medium | NOT_RUN | workspace engineering: independent CI | preview and build accepted |
| CE-GOV-09 | PR #73 baseline b10f9a9d | CI 3/4, global FAIL | HOLD_HUMAN | critical | CI FAIL | governance: preserve release veto | all clinical, legal, security gates approved |

## Measured coverage / estimates
- CI workflow pass: 3/4 (75%), **global FAIL**, on baseline `b10f9a9d`.
- Individual semantic constraints reconciled historically: 8/1996 = 0.40%; newly reconciled 0.
- Parser acceptance: 0/16; tools accepted: 0/24; remaining namespace findings resolved: 0/3 in this run (not 0/5).
- CI after this checkpoint commit: NOT_RUN at authoring; local tests: NOT_RUN; code fixes: 0.
- **Global completion estimate: NOT_AFFIRMED (denominator undefined)**. No claim that physical inventory is clinical homologation.

## Safety and next steps
1. Inspect and fix three exact namespace paths, execute CLI and Kernel smoke in CI with negative tests, then check new SHA.
2. Reuse individually verified parsers; avoid broad cherry-pick, legacy directory deletion, and fake implementations.
3. Continue SELECT-only object-level crosswalk, respecting manifest non-atomicity and fingerprint deduplication.
4. Independently evaluate 24 tools, metamodel, M08/M09 corpus and workspace PR #71.
5. No DDL/DML, migrations, seeds, merges, deploys, branch deletion, candidate promotion, or clinical/legal bypass.

Sources: GitHub PR #73 and Actions logs observed 2026-11-19; Supabase pg_catalog SELECT 2026-11-19; export manifest observation 2026-11-15.
