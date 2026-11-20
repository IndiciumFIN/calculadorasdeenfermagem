# CE/CKO/NCOS — WO 2026-11-17 11:53 BRT — constraint scope reconciliation

Authority: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` only. SELECT-only. No Neon/SOT, no accounting content analysis, no DDL/DML/merge.

## New evidence and delta
- Prior checkpoint `WO_20261117_1053_PK_FK_CONSTRAINT_DELTA.md` blob `36efa89b1bfa0660136872d8d10460092b2f22d8`.
- Export README blob `a0e074bf9da401a3d50dd761536bcad3a9b96150`; MANIFEST blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`; constraints export blob as declared in manifest `83642780302397204b39796e1bd3604a77c68f53`, record_count 1996. Snapshot NON_ATOMIC_ACROSS_QUERIES, dated 2026-11-15.
- Current catalog SELECT: `pg_constraint` with non-system namespace yields 1997 total; **1996 with conrelid <> 0 (table constraints)** and **1 with conrelid = 0 (non-table/domain constraint)**. Therefore historical 1996 and current 1996 table constraints agree quantitatively. The earlier +1 arose from a broader query scope; no physical schema mutation is established.
- Separate scope-limited SELECT excluding accounting schema found 1964 total, 1 non-table, 1 not validated, zero partition-parent or nonlocal constraints. These counts are NOT comparable to the full historical snapshot because of exclusions. Do not use accounting objects in CE crosswalk.
- Three PostgreSQL SELECTs PASS this round (one per-schema taxonomy, one scope-limited, one exact table/non-table distinction). No SQL mutation.

## Work register / fingerprint delta
| Object | Fingerprint / delta | Status / risk | Owner, next action, acceptance |
|---|---|---|---|
| constraint count | 1997 total vs 1996 table-only; one non-table, resolved filter scope | PASS_COUNT / HOLD_SEMANTIC, medium | DBA: compare 1996 exported constraint keys and definitions to current table constraints; zero unexplained per-object delta |
| inventory manifest | Git blob 8099e3ff225224eb00e8eb5accd6d8365ddfcf14, newly read; export constraints blob 83642780302397204b39796e1bd3604a77c68f53 | PASS_READ / medium | DBA: verify exported rows against SELECT and semantic PK/FK |
| verifier 24 tools | previous blob 1bb7ce41fff15820ed9a980b6b793d1fbf54bc70; not reprocessed, no observed delta | HOLD_TEST / medium | Engineering: deterministic/adversarial isolated test |
| four priority branches | prior checkpoint: tools 15/0, metamodel 22/0, corpus 8/0, parsers 163/0; NOT rechecked this round | HOLD_VERIFY / high | Engineering: revalidate heads and compare file-level SHA/delta |
| PR #73 and workspace PR #71 | previous OPEN/DRAFT, current HEAD/checks NOT_RUN | HOLD_MERGE / high | Engineering: verify checks, safety, rollback and approvals |
| clinical 24 tools | historical 0/24 accepted, not revalidated | HOLD_HUMAN / high | Clinical reviewer: tests, source provenance and authorization |
| semantic contracts | historical 0/20 accepted, not revalidated | HOLD_VERIFY / high | Data architect: crosswalk code/SQL/catalog, dedup |
| M08/M09 atoms/parsers | no fingerprint reprocessed this round | HOLD_PROVENANCE / high | Editorial/legal and engineering: sources, license, tests |
| CKO agent identity | previous HOLD_SECURITY; not retested | HOLD_SECURITY / high | Security: trustworthy invoker identity and adversarial tests |

## Acceptance denominators and tests
- Constraint **count agreement 1/1 = 100%** (table-only scope), NOT semantic acceptance.
- Constraint object-level semantic comparison **0/1996 = 0% verified this round**, not a claim that all 1996 are defective.
- Prior relation count 678/678, historical prior checkpoint, NOT re-counted.
- SQL SELECT **3/3 PASS**; Git HEAD comparisons **0/4 NOT_RUN**; isolated unit/adversarial **NOT_RUN**; CI **NOT_RUN**.
- Clinical acceptance historical **0/24**; semantic contracts historical **0/20**, neither revalidated.
- Global completion estimate **NOT ESTIMABLE** (no consolidated criteria denominator).

## Safety and next actions
Maintain fail-closed and human gates for clinical/legal/LGPD/copyright/security/provenance. Candidate content not published. No migrations, seeds, privileges, deploy, merge or branch deletion. Next independent action: compare exported constraints by canonical (schema, table, name, type, definition) and inspect branch tests. No external official normative sources consulted this round.