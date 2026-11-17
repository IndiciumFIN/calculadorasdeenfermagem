# CE / CKO / NCOS — WO 2026-11-17 17:52 BRT — GitHub Actions gate discovery

## Scope and evidence
Primary IndiciumFIN/calculadorasdeenfermagem, complementary IndiciumFIN/dev-chatgpt-workspace; sole physical source Supabase Calculadoras-Smart pgsybzggewhinaniybiy. Read-only SELECT; no Neon, SOT, accounting or WU-TRIB. Previous checkpoint WO_20261117_1653_PR_HEAD_CI_GATE_RECONCILIATION.md read successfully. Export manifest Git blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14; observation 2026-11-15, NON_ATOMIC_ACROSS_QUERIES, HOLD_HUMAN.

## Material delta: CI status API was insufficient
GitHub combined commit status for CE PR #73 HEAD f989009d0f6be96171a4e348195e113a9354022a returned zero statuses, **but workflow runs API returned FOUR completed GitHub Actions runs**:
- Canonical repository invariants — FAILURE, run 44153056914, https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44153056914
- CE Migration-first Supabase provenance (NO SQL) — SUCCESS, run 44153057324, https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44153057324
- Pipeline Determinístico — SUCCESS, run 44153056971, https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44153056971
- CI - Validação — SUCCESS, run 44153057086, https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44153057086

Workspace PR #71 HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d has TWO Vercel FAILURE commit statuses (build-rate-limit), and THREE completed GitHub Actions runs:
- PMO candidate unit regressions (non-release) — FAILURE, run 43685117078, https://github.com/IndiciumFIN/dev-chatgpt-workspace/actions/runs/43685117078
- Verificar bibliotecas — sem deploy — FAILURE, run 43685117070, https://github.com/IndiciumFIN/dev-chatgpt-workspace/actions/runs/43685117070
- Remediate better-auth candidate safely — SKIPPED, run 43685117113, https://github.com/IndiciumFIN/dev-chatgpt-workspace/actions/runs/43685117113

Workflow runs are returned by a first-page, PR-triggered-run filter; not an exhaustive check-suite audit. Job logs and precise failure causes NOT_READ. The earlier 'no CI status' finding for CE #73 must be superseded: three success, one failure, NO-GO. Do not infer code correctness from Vercel rate-limit.

## Work orders, fingerprints, deltas, acceptance
| WO | Object / branch | Fingerprint | Delta | State | Risk | Evidence/test | Owner and next action | Acceptance |
|---|---|---|---|---|---|---|---|---|
| CE-CI73 | PR73 / audit/ce-supabase-migration-first-20261115 | HEAD f989009d0f6be96171a4e348195e113a9354022a | 4 Actions runs discovered (3 success, 1 failure) | FAIL_CI / HOLD_MERGE | HIGH | workflow-run API PASS_READ; no jobs/logs read | CI owner: inspect failed invariants job and remediate in branch | all required checks pass; rollback and security review |
| WS-CI71 | PR71 / dev-chatgpt-workspace | HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d | 3 Actions (2 failure, 1 skipped) in addition to 2 Vercel failures | FAIL_CI / HOLD_MERGE | HIGH | workflow-run and combined-status APIs PASS_READ | Workspace owner: inspect both failed Actions jobs, Vercel quota independently | independent tests and build PASS; no migration in build |
| CE-TOOLS | feat/ce-tools-governed-backend-20261115/scripts/verify_governed_tools.py | blob 1bb7ce41fff15820ed9a980b6b793d1fbf54bc70 | no blob delta | HOLD_TEST | HIGH | Git file read PASS; isolated tests NOT_RUN | Backend owner: deterministic tests with dirty tree, symlink, untracked and missing tracked files | 24/24 tools, repeatable checksums |
| CE-PROVENANCE | cko_governance.artifact_normative_bindings | export constraints blob 83642780302397204b39796e1bd3604a77c68f53 | five SELECT definitions unchanged | HOLD_PROVENANCE | HIGH | SELECT PASS; no deletion simulation | Data governance owner: prove immutable historical lineage for ON DELETE CASCADE | retention evidence without destructive test |
| CKO-META | feat/cko-catalog-metamodel-automated-20261114 | previous compare 22 ahead / 48 files | NOT_RECHECKED | HOLD_SEMANTIC | MEDIUM | NOT_RUN this round | Catalog owner: PK/FK and dictionary crosswalk | 20/20 evidenced contracts |
| CKO-ATOMS | feat/cko-m08-m09-corpus-atomic-20261114 | previous compare 8 ahead / 8 files | NOT_RECHECKED | HOLD_PROVENANCE | HIGH | NOT_RUN this round | Editorial owner: source rights and lineage | licensed and traceable atoms |
| CKO-PARSERS | integration/cko-parsers-catalog-20261114 | previous compare 163 ahead / 175 files | NOT_RECHECKED | HOLD_TEST | MEDIUM | NOT_RUN this round | Parser owner: isolated regression | deterministic extraction |

## Measured layer coverage (not homologation)
- GitHub Actions PR-head discovery: 2/2 PR HEADs queried (100% scoped), 7 runs observed: CE 3 SUCCESS / 1 FAILURE; workspace 0 SUCCESS / 2 FAILURE / 1 SKIPPED.
- CE PR73 green among observed runs 3/4 (75%), **not an approval rate**; workspace 0/3 green (0%, one skipped).
- Combined statuses: CE 0 statuses (not proof of absent Actions); workspace 2/2 failures.
- Database targeted SELECT 1/1 PASS, five returned constraints; historical exact export/live matches 5/1996 (0.25%), remaining 1991 NOT_RUN.
- Historical clinical tool homologation 0/24; semantic contracts 0/20, neither revalidated. Unit/adversarial tests 0 executed in this run; workflow jobs only observed, not rerun.
- Historical inventory: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 table constraints, 1268 indexes, 100 RLS policies. No new full count.
- Global completion estimate: NOT ESTIMABLE, no consolidated acceptance denominator.

## Safety and continuation
No DDL/DML, migration, seed, merge, deployment, clinical publication or branch deletion. Fail-closed gates preserved. Next: inspect failed CI jobs and test verifier locally; reconcile semantically without reprocessing unchanged fingerprints.
