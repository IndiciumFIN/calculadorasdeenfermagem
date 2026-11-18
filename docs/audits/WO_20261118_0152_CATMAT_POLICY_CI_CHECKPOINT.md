# CE / CKO / NCOS — checkpoint 2026-11-18 01:52 BRT

## Scope and safeguards
Only GitHub IndiciumFIN/calculadorasdeenfermagem and Supabase Calculadoras-Smart (pgsybzggewhinaniybiy) were accessed; no Neon, SOT or accounting corpus. No DDL/DML/migrations/seeds/merge/deploy. No candidate promoted. Clinical, legal, LGPD, copyright, provenance and security gates remain fail-closed.

## Work orders / object ledger
| WO | Object / branch | Prior fingerprint / SHA | Current fingerprint / SHA | Delta | Status | Risk | Test/evidence | Responsible / next action | Acceptance |
|---|---|---|---|---|---|---|---|---|---|
| CE-CATMAT-013 | contracts/fontes/catmat.json on audit/ce-supabase-migration-first-20261115 | blob cb1af111303c56a109bb89d97c9bf1c99099ef99 | blob fd9b62b9e9ca7e9335e1eb71b23b842a93573a28 | validators string -> exact two-element array required by policy 013 | PASS_CODE / HOLD_CI | medium | GitHub commit ca325d75dd53c024551741e180f072d74dfa6458; matched policy blob 1a1d144fd965833ee90d56acea6b8bb4c63b3c0f and parser-branch blob fd9b62b9e9ca7e9335e1eb71b23b842a93573a28; unit tests NOT_RUN | CE engineering: run canonical verifier and adversarial tests | strict canonical validation PASS, no policy weakening |
| CE-CI-73 | audit branch PR #73 | prior checkpoint f056a3023094e48e142b98d58ea712b085b911ac | latest known correction ca325d75dd53c024551741e180f072d74dfa6458 | CATMAT fix; PR HEAD not freshly fetched | HOLD_CI | high | prior commit workflow runs 44234020599 FAIL canonical, 44234020601 PASS pipeline, 44234020600 PASS validation, 44234020648 PASS provenance; new CI NOT_RUN/NOT_VERIFIED | CE engineering: check new HEAD workflows | all required checks PASS |
| CE-DB-PROVENANCE | cko_governance.artifact_normative_bindings, pgsybzggewhinaniybiy | prior historical fingerprint unchanged | SELECT returned four constraints | no observed delta | HOLD_HUMAN | high | SELECT pg_constraint; FK artifact_id ON DELETE CASCADE | Clinical/legal/data steward: retention impact analysis | documented provenance retention policy and safe rollback |
| CE-TOOLS-24 | feat/ce-tools-governed-backend-20261115 | main e0f62491b104f4a97c6025a6393cabc2e7ada30e | 15 ahead / 0 behind, 33 changed files | comparison only | HOLD_VERIFY | high | GitHub compare PASS_READ; functional tests NOT_RUN | CE engineering: validate 24 governed tools | 24/24 evidence-backed tool gates |
| CE-METAMODEL | feat/cko-catalog-metamodel-automated-20261114 | main e0f62491b104f4a97c6025a6393cabc2e7ada30e | 22 ahead / 0 behind, 48 changed files | comparison only | HOLD_VERIFY | high | GitHub compare PASS_READ | CKO ontology: reconcile dictionary, PK/FK and canonical catalog | zero unreviewed semantic conflicts |
| CE-CORPUS | feat/cko-m08-m09-corpus-atomic-20261114 | main e0f62491b104f4a97c6025a6393cabc2e7ada30e | 8 ahead / 0 behind, 8 changed files | comparison only | HOLD_VERIFY | high | GitHub compare PASS_READ | CKO content: check normative provenance and licensing | 100% admitted atoms traceable and licensed |
| CE-PARSERS | integration/cko-parsers-catalog-20261114 | main e0f62491b104f4a97c6025a6393cabc2e7ada30e | 163 ahead / 0 behind, 175 changed files | comparison only; CATMAT file parity achieved | HOLD_VERIFY | high | GitHub compare PASS_READ | CE engineering: resolve 16 parsers and 5 imports | canonical verifier and smoke tests PASS |
| CE-WORKSPACE-71 | dev-chatgpt-workspace PR #71 | historical PR evidence only | current HEAD not verified | none | HOLD_VERIFY | high | NOT_RUN this round | Workspace owner: inspect failing PMO/library CI | required CI PASS |
| CE-EXPORT | docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/ | reported 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies | manifest.json path lookup 404; no new fingerprint | none | HOLD_VERIFY | medium | directory manifest not verified; inventory is historical user-supplied | CE audit: locate manifest and verify checksums | manifest and counts verified directly |

## Quantitative controls
- Priority Git branch comparisons: 4/4 PASS_READ (100% inspection only).
- CATMAT source-policy exact validator reconciliation: 1/1 PASS_CODE; CI approval 0/1 verified in this round (NOT_RUN, not FAIL).
- Previously compared export constraints: 5/1996 (0.25%, historical); this round physical constraint read 4/4, not additional export comparisons.
- 24 clinical tools: 0/24 confirmed homologated (historical, not revalidated).
- Parsers: 0/16 newly resolved this round; imports 0/5 newly resolved.
- CI on prior checkpoint: 3/4 PASS, 1/4 FAIL; current commit CI NOT_VERIFIED.
- Global completion estimate: NOT ESTIMABLE (no comprehensive acceptance denominator). Inventory counts do not establish homologation.

## Next independent tasks
Run tests for CATMAT contract and verify new GitHub Actions; inspect next source-policy mismatches without duplicating validated fingerprints; reconcile parsers/imports and code/SQL/physical catalog with SELECT only; inspect PR #71; verify export manifest path and SHA. No merge until gates and rollback requirements are met.
