# CE/CKO/NCOS — WO 2026-11-17 10:53 BRT — PK/FK catalog reconciliation

Authority: ONLY Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. SQL SELECT only. Candidate NOT published. No DDL/DML/migration/seed/merge.

## Evidence and delta
- Last checkpoint `WO_20261117_0951_CATALOG_TAXONOMY_RECONCILIATION.md` blob `c4bb62d9f09c0f879fe690e95f2997a6795d910c`.
- Tools verifier `scripts/verify_governed_tools.py` blob `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70`, unchanged. Avoid repeated fingerprint processing; isolated tests still NOT_RUN.
- PostgreSQL SELECT pg_class non-system relkind: r=611, p=1, v=49, S=17; 678/678 quantitative inventory reconciliation; no semantic acceptance.
- **New SELECT pg_constraint non-system connamespace:** CHECK(c)=536, FOREIGN KEY(f)=681, PRIMARY KEY(p)=610, UNIQUE(u)=170; **1997** total, against reported historical **1996**. Difference +1, **HOLD_RECONCILE**, not evidence of schema mutation: original export query/filter and timestamp not yet compared. Never silently overwrite historical count. Need per-schema and per-OID diff, partition/inherited constraints, historical export source and query.
- Git comparisons vs main: tools 15 ahead/0 behind/33 files; metamodel 22/0/48; M08/M09 8/0/8; parsers 163/0/175. Main comparison base commit `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. Metadata only.
- PR #73: OPEN/DRAFT, head branch `audit/ce-supabase-migration-first-20261115`, base main; PR #71 workspace OPEN/DRAFT, head `fix/ce-tanstack-vercel-build-no-migrations-20261114`, base main. PR HEAD commit SHAs and CI statuses NOT_RUN; do not merge.

## Object work register
| Object | Fingerprint / delta | Status / risk | Owner / next action / acceptance |
|---|---|---|---|
| verifier script | Git blob `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70`, no delta | HOLD_TEST / medium | Engineering: execute isolated deterministic and adversarial tests; identical outputs, untracked ignored, symlink/missing fail-closed |
| physical relation taxonomy | 611+1+49+17=678; no count delta | PASS_SELECT / HOLD_SEMANTIC | DBA: crosswalk SQL candidate and real catalog |
| constraint taxonomy | 536 c + 681 f + 610 p + 170 u = 1997; +1 vs historical 1996 | HOLD_RECONCILE / high | DBA: reproduce exact 2026-11-15 query and compare individual constraints by schema/table/name/definition; zero unexplained delta |
| tools branch | 15 ahead/33 changed; per-file fingerprints NOT_RUN | HOLD_CLINICAL / high | Engineering and clinical reviewer: validate 24/24 tools and provenance |
| metamodel branch | 22 ahead/48 changed | HOLD_SEMANTIC / high | Data architect: canonical PK/FK/dictionary relationships and semantic dedup |
| M08/M09 corpus | 8 ahead/8 changed | HOLD_PROVENANCE / high | Editorial/legal: atom license, source and dedup |
| parser branch | 163 ahead/175 changed | HOLD_TEST / medium | Engineering: isolated parser regression |
| PR #73 / workspace PR #71 | both OPEN/DRAFT, head branch verified, SHA/checks NOT_RUN | HOLD_MERGE / high | Engineering: validate SHA, checks, rollback and approvals |
| agent identity | prior guard fingerprint methodology disputed, no delta checked | HOLD_SECURITY / high | Security: trust-boundary adversarial tests |

## Acceptance counters
- Relations count: 678/678 = 100% **quantitative count only**.
- Constraint count agreement: 0/1 = 0% **comparison checks** (1997 != 1996), NOT a platform completion rate.
- Branch metadata comparisons: 4/4 = 100% reads, NOT semantic integration.
- Clinical tools accepted: 0/24 historical, not revalidated; semantic contracts: 0/20 historical, not revalidated.
- PostgreSQL SELECT queries 2/2 PASS; Git comparisons 4/4 PASS_READ; unit/adversarial/CI NOT_RUN.
- **Global completion estimate: NOT ESTIMABLE**, acceptance denominator not consolidated.

## Gates
Fail-closed; no publication, DDL/DML, migrations, seeds, privilege changes, merges or branch deletions. Clinical/legal/LGPD/copyright/security/provenance require human acceptance. Next independent action: reproduce the one-constraint delta by exact original export methodology and run isolated verifier tests.
