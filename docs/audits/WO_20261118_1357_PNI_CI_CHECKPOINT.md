# CE / CKO / NCOS — checkpoint 2026-11-18 13:57 BRT

## Physical source, scope and safety
GitHub repository `IndiciumFIN/calculadorasdeenfermagem`, PR #73, branch `audit/ce-supabase-migration-first-20261115`. Exclusive physical truth Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. No other database. PostgreSQL SELECT only; no DDL, DML, migration, seed, merge, deletion or candidate publication. Fail-closed clinical, legal, provenance, copyright, security and LGPD gates.

## Actual delta / work orders

| WO / object | SHA / fingerprint / delta | Status / risk | Test / evidence | Owner and next action | Acceptance |
|---|---|---|---|---|---|
| CE-PNI / `contracts/fontes/pni.json` | blob `a80aad32fc50344e3852353ca222cb20c5f5e123` -> `f41336fdcfff422a8d148c57980479a12ca39706`; scalar `validators` to `["schema_validator"]`; policy 012 blob `edd8cddd184f99a0af2c9010b88750bfc7ded3b6` | PASS_STATIC / medium; global admission FAIL | Source and policy direct GitHub reads; code commit `5ffe6b300e0602901a227a83c0b891424b1351f2`; post-fix CI NOT_RUN | Engineering: verify CI exact new SHA | Source/policy match and canonical CI green |
| CE-CI-PR73 | prior SHA `2d153206f3fefa6501f2280efa9a0a80825947aa`; run IDs 44341166405, 44341166347, 44341166515, 44341166605 | FAIL / high | 3/4 PASS, canonical FAIL; two jobs fail at source-policy and parser/import admission | Engineering: resolve proven remaining sources and dependencies | 4/4 required workflows PASS on final HEAD |
| CE-PARSERS / `integration/cko-parsers-catalog-20261114` | 16 missing parser paths in current CI, exact integration branch HEAD NOT_RUN | FAIL / high | Job 134931209655 logs; no code change | Engineering: inspect parser branch and port only verified tested implementations | 0 missing parsers, smoke PASS |
| CE-IMPORTS / `packages/cli/**` | 5 namespace findings; file hashes not yet compared | FAIL / high | Job 134931209655 | Engineering: inspect actual imports, repair with regression tests | 0 namespace errors |
| CE-SOURCE-SIES / `contracts/fontes/sies.json` | blob `97d91f8f4df6f83a6f848cb4df5caefe0a1971ae`; scalar validator, policy 016 NOT_READ | FAIL / medium | Direct source read, CI SOURCE_VALIDATOR_SCHEMA | Engineering: compare exact policy 016 before fix | Exact canonical array, no duplicate |
| CE-EXPORT / `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` | historical manifest blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`; observation 2026-11-15, 22 source files | PASS_HASH historical / low | Manifest read; 22/22 previously verified, no delta established; NOT_REHASHED | Audit: rehash only upon delta | 22/22 fingerprints unchanged |
| CE-SUPABASE / `cko_governance` | c61, f81, p88, u34 =264 constraints; no aggregate change | PASS_AGGREGATE / HOLD_OBJECT_MAPPING | SELECT `pg_constraint` scoped to schema | DB architecture: compare per-object identities | No unexplained PK/FK/check differences |
| CE-GLOBAL-CONSTRAINTS | historical 1996 vs prior live 2109; +113 not proven as individual changes | HOLD_SEMANTIC / high | Object-by-object NOT_RUN | DB architecture: compare canonical definitions and fingerprints | 1996 historical records classified |
| CE-TOOLS / `feat/ce-tools-governed-backend-20261115` | 24 candidates; HEAD NOT_RUN | HOLD_HUMAN / high | Clinical validation NOT_RUN | Clinical engineering: tool-by-tool safety and provenance | 24/24 individually accepted |
| CE-METAMODEL / `feat/cko-catalog-metamodel-automated-20261114` | branch located historically, HEAD NOT_RUN | HOLD_VERIFY / medium | Semantic comparison NOT_RUN | Architecture: dictionary and PK/FK crosswalk | No competing canonical identity |
| CE-CORPUS / `feat/cko-m08-m09-corpus-atomic-20261114` | branch found this round, HEAD NOT_RUN | HOLD_HUMAN / high | License and source NOT_RUN | Clinical/legal: atom provenance and license | Every accepted atom sourced and licensed |
| CE-WORKSPACE / PR #71 | last reported HEAD `1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d`; not re-read | HOLD_VERIFY / high | CI NOT_RUN | Frontend: verify SSR/auth/preview/no-migration | All required checks and review |

## Measured progress (not clinical homologation)
- Export Git blob integrity: historical 22/22 = 100%; fingerprints not reprocessed.
- PNI contract selected: 1/1 PASS_STATIC; total source-contract denominator NOT_ESTABLISHED.
- Previous CI on exact previous checkpoint SHA: 3/4 PASS = 75%, **global FAIL**; CI on new code and documentation HEAD NOT_RUN.
- Supabase governance aggregate: 1/1 read grouping; historical global constraint object mapping this round 0/1996.
- Clinical tools revalidated this round: 0/24; parser fixes this round 0/16; namespace fixes 0/5.
- Priority branch HEADs verified this round: 0/4. PR #71 current HEAD NOT_RUN.
- Local unit, adversarial and smoke tests this round: NOT_RUN.
- **Global completion estimate: NOT_ESTIMABLE** until acceptance denominator established.

## Evidence and next sequence
GitHub Actions run `44341166347`, observed 2026-11-18; canonical job `134931209354` fails source references; full admission job `134931209655` reports 16 missing parsers and 5 namespace findings. Three other workflows on previous SHA PASS. Policy 012 and PNI source compared; PNI fixed in commit above. Supabase SELECT only confirms stable aggregate. Next: check post-fix CI on exact HEAD; compare SIES to policy 016; inspect integration parser implementations and imports; reconcile PostgreSQL object fingerprints without writing; keep PR #73 draft. No external normative source asserted in this round.
