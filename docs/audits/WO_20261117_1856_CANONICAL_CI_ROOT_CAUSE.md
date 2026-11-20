# WO — 2026-11-17 18:56 BRT — CI canonical failure diagnosis

## Scope and provenance
Repository: IndiciumFIN/calculadorasdeenfermagem; PR #73. Prior checkpoint: 7343a08b4d2a2a0dc15b3546e624c1671b5e4dfa (reported; no HEAD revalidation in this work order). GitHub Actions run 44153056914; jobs 134286293348 and 134286293754; logs inspected directly on 2026-11-17. Supabase authoritative project: pgsybzggewhinaniybiy. No database write or query this round.

## Evidence / findings
- Job 134286293348 (Canonical contracts and CLI smoke): FAIL at step 7, Verify canonical source and policy references. Previous steps setup, installation, compilation and deterministic negative tests PASS. CLI and kernel smoke SKIPPED.
- Job 134286293754 (Full admission blockers, fail closed): FAIL at step 4, Reject unresolved parser or import dependencies.
- Both jobs ran scripts/verify_repository_integrity.py; output schema CE-CANONICAL-INTEGRITY-1.0.0, source_contract_count=20, kernel_policy_count=20, error=1, pending=21, structural_pass=false, strict_pass=false.
- Error LEGACY_SOURCE_DIR: contracts/fonts must be reconciled with canonical contracts/fontes. Do not delete/rename until inventory and consumers are compared.
- Pending: 16 MISSING_PARSER findings for anvisa_dev, anvisa_med, atlas, catmat, cdsi, cid10, cid11, esavi, fhir_vitais, medlineplus, mesh, pni, sies, sinan, taco, vacinas_cdc. 5 PACKAGE_IMPORT_NAMESPACE findings: packages/cli/kernel/__init__.py, kernel/cli.py, kernel/core.py, main.py, validators/registry.py.
- No parser stub or bypass is authorized; fail-closed remains correct.

## Work orders
| ID | Object / fingerprint | Delta | Status | Risk | Test / acceptance | Owner / next action |
|---|---|---|---|---|---|---|
| CE-CI-001 | workflow run 44153056914 / job 134286293348 | First detailed log diagnosis | FAIL | high | Structural verifier returns zero errors without suppressing legitimate checks; deterministic tests PASS | Engineering: inspect contracts/fonts content, references and canonical equivalent, prepare safe code fix |
| CE-CI-002 | run 44153056914 / job 134286293754 | First detailed log diagnosis | HOLD_HUMAN | high | 16 parsers have verified implementations or explicit governed dependency resolution; strict test PASS | Parsers/clinical evidence team: map against integration/cko-parsers-catalog-20261114, license and provenance |
| CE-CI-003 | five import paths above | First detailed log diagnosis | HOLD_VERIFY | medium | python -m packages.cli.main smoke with namespace isolation PASS | Engineering: inspect import graph, correct imports with regression tests |
| CE-DB-001 | historical constraints.jsonl 1,996 rows | No newly verified delta | HOLD_VERIFY | high | Individual semantic comparison including PK/FK, schema, definition and provenance | Database governance: SELECT only on pgsybzggewhinaniybiy |
| CE-TOOLS-001 | scripts/verify_governed_tools.py blob 1bb7ce41fff15820ed9a980b6b793d1fbf54bc70 (historical) | Not rechecked | HOLD_TEST | medium | deterministic repeat, symlinks, untracked files, tampering PASS | Engineering: isolated tests |
| CE-PR-071 | workspace PR #71 | Not rechecked | HOLD_CI | high | diagnose PMO and library jobs, CI green | Workspace team |

## Measurable coverage (do not confuse inspection with admission)
- GitHub Actions jobs investigated: 2/2 = 100% of selected failed jobs, both FAIL.
- Structural findings classified: 22/22 = 100% of reported findings (1 error + 21 pending), not remediated.
- Parser dependencies missing: 16/16 reported; validated implementations: 0/16 in this run (NOT_RUN, not a claim of nonexistence across branches).
- Import namespace pending: 5/5 reported, tests NOT_RUN.
- Historical individually compared constraints: 5/1996 = 0.25% (not repeated in this run).
- Clinical tool homologation: historical 0/24, not revalidated.
- Global completion estimate: NOT ESTIMABLE; acceptance criteria denominator not consolidated.

## Gates and restrictions
No DDL, DML, migration, seed, merge, deployment, permission change or branch deletion. Candidate artifacts are not published. Clinical, legal, security, LGPD, licensing and provenance gates remain fail-closed. No external normative sources consulted this run. GitHub Actions logs are primary evidence; links: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44153056914/jobs/134286293348 and https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44153056914/jobs/134286293754.

## Next checkpoint
Read current PR #73 HEAD and workflow source; inspect legacy directory contents, compare parser branch and imports; implement a minimal safe fix with tests if proven; check PR #71 jobs; preserve independent DB semantic work with SELECT only. CI must remain blocked until evidence supports release.
