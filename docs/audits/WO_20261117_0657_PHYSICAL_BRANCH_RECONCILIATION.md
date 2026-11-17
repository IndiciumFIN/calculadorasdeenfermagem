# CE / CKO / NCOS — WO 2026-11-17 06:57 BRT — physical boundary and prioritized Git reconciliation

Status: PASS_READ / HOLD_SECURITY / HOLD_CLINICAL / HOLD_PROVENANCE / HOLD_MERGE. Physical source of truth: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` ONLY. No Neon, accounting, or other Supabase project. Database operation: SELECT only.

## Actual checkpoint and immutable references
- Previous WO `docs/audits/WO_20261117_0557_TRIGGER_SCOPE_BRANCH_REFRESH.md`: blob SHA `b5b20e664ccfa60f8a25c8214d8035274678830d`, read live this run.
- Export README `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/README.md`: blob SHA `a0e074bf9da401a3d50dd761536bcad3a9b96150`, re-fetched and unchanged from earlier reference.
- Git main comparison base SHA `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. Audit branch before this commit: 61 ahead / 0 behind main (prior 60 ahead; +1 documented checkpoint).
- PostgreSQL SELECT returned `cko_validation.findings`: ordinary table (relkind r), owner postgres, RLS disabled, **3 application triggers**. This is a catalog observation, not proof of accessible bypass or full privilege safety. No routine body rehashed, because no delta was established; prior `cko_governance.guard_material_finding_closure_learning_v1` MD5 `bfd24b5c361d73bb706c797133ad9b0c` remains HISTORICAL, not revalidated.

## Branch / file / object register (2026-11-17 06:57 BRT)
| Scope | Fingerprint / Git delta | Status and risk | Responsible / next action / acceptance |
|---|---|---|---|
| `cko_validation.findings` | SELECT owner postgres, relkind r, RLS=false, 3 application triggers; no claim of changed schema | PASS_CATALOG; HOLD_SECURITY high | DBA/security: review privileged writers, SECURITY DEFINER call paths, identity origin; isolated adversarial tests required |
| `feat/ce-tools-governed-backend-20261115` | 14 ahead/0 behind, 33 changed files; includes `scripts/verify_governed_tools.py` and governed-tools manifest; unchanged counts from prior | PASS_GIT_READ; HOLD_CLINICAL high | Engineering/clinical: run offline manifest verifier, map 24 contracts to live catalog and official sources; accept 24/24 only after independent validation |
| `feat/cko-catalog-metamodel-automated-20261114` | 22 ahead/0 behind, 48 files; workflows `canonical-invariants.yml`, `cko-canonical-catalog.yml` | PASS_GIT_READ; HOLD_SEMANTIC high | Data architect: compare PK/FK/dictionary/metamodel/atom references and collision keys, no duplicate schema creation |
| `feat/cko-m08-m09-corpus-atomic-20261114` | 8 ahead/0 behind, 8 files; manifest and `test_validate_atomic_content.py` | PASS_GIT_READ; HOLD_PROVENANCE high | Editorial/legal: validate hash and rights per source atom, no protected originals published |
| `integration/cko-parsers-catalog-20261114` | 163 ahead/0 behind, 175 files; parser CI workflows present | PASS_GIT_READ; HOLD_VERIFY high | Engineering: parser tests, semantic dedup, regression and evidence |
| `audit/ce-supabase-migration-first-20261115` | 61 ahead/0 behind prior to this commit; README blob as above | PASS_GIT_READ; HOLD_MERGE | Engineering: PR #73 HEAD/checks/approval and security gate |
| `IndiciumFIN/dev-chatgpt-workspace` PR #71 | HEAD/checks not fetched this run | NOT_RUN / HOLD_VERIFY | Engineering: verify CI, conflicts and relevance before any merge |

## Quantitative coverage — do not confuse with acceptance
- Git topology: 5/5 branches compared with main = 100% of **requested branch comparisons**, NOT integration completion.
- Live physical catalog query: 1/1 SELECT PASS; 1/1 targeted relation inspected; no full inventory recount.
- Historical snapshot: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies (README; NOT revalidated live).
- Clinical tools: historical 0/24 homologated (0% historical); semantic contracts: historical 0/20 homologated (0% historical). No new acceptance evidence.
- Unit tests 0 NOT_RUN; CI 0 NOT_RUN; dynamic security tests 0 NOT_RUN; PR #73 and #71 HEAD/checks NOT_RUN.
- Global estimate: **NOT ESTIMABLE** (no consolidated acceptance denominator). No invented percentage.

## Delta, controls, acceptance
This run re-fetched both checkpoints, confirmed unchanged export README SHA, refreshed all four priority branch comparisons and audit branch, and checked one live catalog relation. No functional correction is justified without verified code-vs-catalog discrepancy and regression tests. Next independent work order: inspect `scripts/verify_governed_tools.py` and its manifest, run offline tests, and prepare a code-only fail-closed fix if a reproducible failure exists. Then reconcile catalog PK/FK/atoms without reprocessing unchanged fingerprints. No DDL/DML, seeds, migrations, ACL changes, deployment, merge or branch deletion. HOLD_SECURITY and HOLD_HUMAN continue to block publication.

Official technical sources checked 2026-11-17: PostgreSQL system catalogs on connected Supabase, GitHub contents and compare APIs. This document is an evidence checkpoint, not certification.
