# CE / CKO / NCOS — WO 2026-11-17 16:53 BRT — PR HEAD and CI gates

## Scope and authoritative source
GitHub IndiciumFIN/calculadorasdeenfermagem and IndiciumFIN/dev-chatgpt-workspace; only physical database consulted: Supabase Calculadoras-Smart pgsybzggewhinaniybiy, SELECT-only. Historical manifest blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14, observation 2026-11-15, NON_ATOMIC_ACROSS_QUERIES and HOLD_HUMAN. Prior checkpoint blob 35b12c49135f75861a761d54e06fbf51ac3a1daf. No Neon, SOT, accounting, WU-TRIB.

## Newly verified delta
- PR #73 head f989009d0f6be96171a4e348195e113a9354022a, base e0f62491b104f4a97c6025a6393cabc2e7ada30e; draft/open; combined commit status API returned ZERO statuses. This is NOT CI PASS: workflow/check-run coverage unverified.
- Workspace PR #71 head 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d, base dacfaa6bc29fd213ffc4d63998b4dd669d10854b; draft/open; TWO Vercel statuses FAILURE, target reports build-rate-limit. Distinguish platform quota from code correctness; NO-GO until successful rerun and independent tests.
- Four branch comparisons against main all zero behind; ahead/files: governed tools 15/33; metamodel 22/48; M08/M09 8/8; parsers 163/175. Same counts as preceding evidence; no branch count delta.
- Supabase SELECT reconfirmed five targeted constraints and the ON DELETE CASCADE FK, with no definition delta versus prior checkpoint. Fingerprint of unchanged export constraints: blob 83642780302397204b39796e1bd3604a77c68f53. No redundant export-vs-live reprocessing; five exact matches are historical evidence, not a fresh full comparison.

## Work orders / fingerprint and risk register
| WO | Branch/file/object | SHA/fingerprint | Delta | Status | Risk | Test | Responsible / next action | Acceptance |
|---|---|---|---|---|---|---|---|---|
| CE-PR73 | audit/ce-supabase-migration-first-20261115 PR73 | HEAD f989009d0f6be96171a4e348195e113a9354022a | HEAD confirmed; 0 statuses | HOLD_CI | high | combined-status READ_PASS; workflow checks NOT_RUN | CI owner: fetch workflow/check-runs, validate security and rollback | required CI green, gates signed |
| WS-PR71 | fix/ce-tanstack-vercel-build-no-migrations-20261114 PR71 | HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d | 2 Vercel failures confirmed | FAIL_CI / HOLD_MERGE | high | combined-status READ_PASS; 2 failures | workspace CI owner: resolve build-rate-limit, rerun and inspect logs | successful independent build; no migrations in build |
| CE-TOOLS-24 | feat/ce-tools-governed-backend-20261115 | main e0f62491; 15 ahead, 33 files; verifier blob 1bb7ce41fff15820ed9a980b6b793d1fbf54bc70 (previous evidence) | no compare-count delta | HOLD_TEST | high | Git compare PASS; verifier isolated tests NOT_RUN | backend owner: determinism, symlink, untracked tests | 24/24 tools validated |
| CKO-META | feat/cko-catalog-metamodel-automated-20261114 | 22 ahead, 48 files | no count delta | HOLD_SEMANTIC | medium | Git compare PASS | catalog owner: PK/FK, dictionary, SQL candidate crosswalk | 20/20 evidenced contracts |
| CKO-ATOMS | feat/cko-m08-m09-corpus-atomic-20261114 | 8 ahead, 8 files | no count delta | HOLD_PROVENANCE | high | Git compare PASS | editorial/clinical owner: rights and provenance | all atoms traceable/licensed |
| CKO-PARSERS | integration/cko-parsers-catalog-20261114 | 163 ahead, 175 files | no count delta | HOLD_TEST | medium | Git compare PASS | parser owner: isolated tests | deterministic validated extraction |
| CE-FK | cko_governance.artifact_normative_bindings | export blob 83642780; FK ON DELETE CASCADE | unchanged | HOLD_PROVENANCE | high | SELECT 1/1 PASS; deletion tests NOT_RUN | provenance owner: non-destructive retention proof | immutable audit lineage |
| CE-EXPORT | docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json | 8099e3ff225224eb00e8eb5accd6d8365ddfcf14 | no manifest delta observed | HOLD_HUMAN | medium | file READ_PASS | data steward: atomic snapshot strategy | provenance of each export slice |

## Measured coverage, not homologation
- Branch comparisons 4/4 (100% of four requested branches) PASS_READ.
- PR HEADs 2/2 (100% of requested PRs) PASS_READ; CI approval 0/2 (0%), PR73 missing status coverage, PR71 two failures.
- Selected live constraints 5/5 returned by SELECT (100% selected); exact export/live match 5/1996 (0.25%) per previous checkpoint; remaining 1991 not reconciled.
- Clinical tools 0/24 historically homologated, not revalidated; semantic contracts 0/20 historically, not revalidated.
- Database SELECT 1/1 PASS; unit/adversarial tests NOT_RUN; CI jobs NOT_RUN in this round; read of existing statuses 2/2 PASS.
- Historical physical inventory only: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 table constraints, 1268 indexes, 100 RLS policies. Not recounted.
- Global completion estimate: NOT ESTIMABLE; consolidated acceptance denominator unavailable.

## Safety and next actions
No DDL/DML, migrations, seeds, deploy, merge, privilege changes or branch deletion. Preserve fail-closed, clinical/legal/LGPD/copyright/provenance gates. First investigate PR71 CI quota and PR73 check-run coverage, then isolated verifier tests and canonical-key semantic crosswalk without reprocessing unchanged fingerprints. Candidate data not published.
