# CE / CKO / NCOS — work program checkpoint 2026-11-18 12:54 BRT

## Scope, physical truth and baseline
Repository: IndiciumFIN/calculadorasdeenfermagem, branch `audit/ce-supabase-migration-first-20261115`, PR #73 OPEN DRAFT. Prior checkpoint commit `2aa0ede12fa251ad3807aeb2ec9e1c0d8676e635`, prior checkpoint file blob `97e759735f8c98f29f7abb71ecb7b1aa42e7d621`. This round's functional fix commit `ce1890375774a7ee144c11779022ea733ab307ee`. Physical database exclusively Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. No other database used.

## Verified delta and traceable work orders

| WO / object | Fingerprint, delta | Status / risk | Test and evidence | Owner / next action | Acceptance |
|---|---|---|---|---|---|
| CE-SOURCE-MEDLINEPLUS `contracts/fontes/medlineplus.json` | blob `ab13a39bc6ae5f6ef444b197bfea0deb60f8d6e0` -> `3a1e98114e06e3becf656d9fe3ed3bac8a867aaa`; scalar `validators` -> array `["schema_validator"]`; policy 015 blob `f8220b3a19fb183f39cd7199b573265ad04781fc` | PASS_STATIC / medium; admission still FAIL | Direct file comparison against `contracts/policies/KERNEL-POLICY-015.json`; commit `ce189037...`; CI post-fix NOT_RUN | Engineering: verify same-HEAD canonical reference CI | validator schema PASS plus no other policy mismatches |
| CE-PR73 / audit branch | pre-fix HEAD `2aa0ede12fa251ad3807aeb2ec9e1c0d8676e635`; new fix `ce189037...` | DRAFT / high | PR metadata read; post-fix CI NOT_RUN | Engineering: retain draft until all gates | Required CI green on exact final SHA and signoffs |
| CE-CI-CANONICAL | run `44328477693` FAIL at previous HEAD; jobs `134886097270`, `134886097885` | FAIL / high | Logs read: SOURCE_VALIDATOR_SCHEMA on multiple sources, 16 MISSING_PARSER, 5 PACKAGE_IMPORT_NAMESPACE; compilation and negative tests PASS, CLI smoke skipped | Engineering: compare each remaining source against exact policy, implement parsers and imports only with tests | No source-policy mismatches; CLI smoke and full admission PASS |
| CE-EXPORT / MANIFEST | blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`; no detected manifest delta | PASS_HASH historical 22/22 / low | Manifest read; hashes previously validated; NOT_REPROCESSED | Audit: rehash only after manifest delta | 22/22 verified with unchanged fingerprints |
| CE-SUPABASE / governance constraints | live SELECT c61 f81 p88 u34 =264, no aggregate delta | PASS_AGGREGATE / HOLD_OBJECT_MAPPING, medium | PostgreSQL catalog SELECT this round | DB architecture: compare object identities and definitions | No unexplained PK/FK or check delta |
| CE-CONSTRAINT-DELTA / global | historical 1996 vs previously reported live 2109 (+113); no object-level proof | HOLD_SEMANTIC / high | Object-level comparison NOT_RUN | DB architecture: fingerprint schema/table/name/type/definition | 1996 historical records classified, new objects distinguished |
| CE-TOOLS / `feat/ce-tools-governed-backend-20261115` | branch exists; exact HEAD NOT_RUN; 24 candidates | HOLD_HUMAN / high | Branch search PASS; clinical tests NOT_RUN | Clinical engineering: independently validate 24 tools | 24/24 clinically accepted, provenance and safety |
| CE-METAMODEL / `feat/cko-catalog-metamodel-automated-20261114` | branch exists; exact HEAD NOT_RUN | HOLD_VERIFY / medium | Branch search PASS | Architecture: semantic dictionary/PK/FK crosswalk | No duplicate canonical identity |
| CE-CORPUS / `feat/cko-m08-m09-corpus-atomic-20261114` | branch exists; exact HEAD NOT_RUN | HOLD_HUMAN / high | Branch search PASS | Clinical/legal: trace source and license for each atom | Licensed, sourced atoms only |
| CE-PARSERS / `integration/cko-parsers-catalog-20261114` | branch exists; exact HEAD NOT_RUN | FAIL_ADMISSION / high | CI lists 16 missing parser paths and 5 import namespace findings | Engineering: compare branch parser content, implement and test | 0 missing parsers and 0 namespace issues |
| CE-WORKSPACE / PR #71 | HEAD `1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d`; OPEN DRAFT | HOLD_VERIFY / high | PR read; current CI NOT_RUN | Frontend: validate SSR, auth, preview and no-migration build | Required checks, RLS/auth review and preview accepted |

## CI on previous exact PR #73 HEAD
- `44328477719` provenance PASS
- `44328477670` CI validation PASS
- `44328477706` deterministic pipeline PASS
- `44328477693` canonical invariants FAIL (two failed jobs)
- Overall 3/4 PASS (75% of these four workflows); **global FAIL**. CI on new functional commit and this checkpoint: NOT_RUN, not presumed green.

## Quantified coverage and estimates
- Historical Git export integrity: 22/22 PASS (100%, historical, no delta detected).
- Source contract fixes this round: 1/1 selected source PASS_STATIC; full source inventory denominator NOT_ESTABLISHED.
- CI prior exact SHA: 3/4 PASS, global FAIL.
- Supabase governance aggregate: 1/1 grouping PASS_READ; object-by-object reconciled this round 0/1996 historical records.
- Clinical tool acceptance this round: 0/24 revalidated (not a claim of 0 historical approvals).
- Parser/import admission resolved this round: 0/16 parsers, 0/5 imports.
- Priority branch existence: 4/4 found; exact branch HEADs 0/4 verified.
- PR head reads: 2/2 (PR #73 pre-fix; PR #71 current); post-fix PR #73 head and checks NOT_RUN.
- Global completion estimate: **NOT_ESTIMABLE**, no unified acceptance denominator; inventories do not imply homologation.

## Safety, sources, and next work
Sources observed 2026-11-18: GitHub PR #73 and #71; GitHub Actions `44328477693` logs; GitHub source and policy blobs; Supabase `pg_catalog.pg_constraint` SELECT; export MANIFEST (observation 2026-11-15). No DDL/DML, migrations, seeds, deploy, merge, deletion, candidate publication or external normative claim. Clinical, legal, security, LGPD, copyright and provenance gates remain fail-closed. Next: CI on final HEAD, resolve next proven policy mismatch, compare parser integration branch and tests; independent catalog crosswalk and tool/corpus provenance tasks continue despite HOLD_HUMAN.
