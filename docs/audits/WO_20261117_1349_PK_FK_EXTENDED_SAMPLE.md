# CE / CKO / NCOS — WO 2026-11-17 13:49 BRT — PK/FK expanded sample and branch refresh

Authority: only Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. SELECT only. No Neon, SOT, accounting/WU-TRIB, DDL/DML, migration, seed, deployment or merge.

## Source and checkpoints
- Prior WO: `docs/audits/WO_20261117_1257_PK_FK_TARGETED_SAMPLE.md`, blob SHA `c9416f50e59171592d28f153903d5ae963ec3339`; read successfully.
- Direct export manifest: blob SHA `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`, dated 2026-11-15; `NON_ATOMIC_ACROSS_QUERIES`, `HOLD_HUMAN`. Inventory **historical**: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 table constraints, 1268 indexes, 100 RLS policies. No full recount.
- SQL SELECT: `pg_constraint` JOIN `pg_class` JOIN `pg_namespace`, scoped to `cko_governance` and `cko_validation`, types p/f, deterministic ORDER BY, LIMIT 50. **50 rows returned**. Extended the preceding 40-row sample by 10 ordered rows; first 40 overlap, not 90 unique. Found composite PK `architecture_layer_bindings(profile_id, architecture_layer_id, implementation_layer_id)`; FK `artifact_normative_bindings_artifact_id_fkey` uses `ON DELETE CASCADE`. This is a **review candidate**, not proof of unsafe behavior.
- Branch comparisons against main: tools 15 ahead/0 behind/33 files; metamodel 22/0/48; corpus M08/M09 8/0/8; parsers 163/0/175. All comparisons PASS_READ, no merge authorization. Main compare base SHA `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.

## Object-level work register
| Object / branch | SHA/fingerprint and delta | Status / risk | Owner, next action, acceptance |
|---|---|---|---|
| Export manifest | Git blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`; baseline read, no change established | PASS_READ / medium | Data architect: stable key+definition matching against 1996 table constraints; 0 unexplained deltas |
| Governance PK/FK sample | 50 rows, 40 overlapping preceding sample; no per-object canonical hash established | PASS_SAMPLE / HOLD_SEMANTIC, high | DBA: match exact schema/table/name/type/definition to export and SQL candidate; no false 50/1996 acceptance |
| `cko_governance.architecture_layer_bindings` | composite PK observed; no prior object fingerprint | HOLD_SEMANTIC / medium | Data architect: check dictionary and ORM support for composite identity |
| `cko_governance.artifact_normative_bindings` | FK `artifact_normative_bindings_artifact_id_fkey` CASCADE observed | HOLD_REVIEW / high | Security/data architect: trace lifecycle, provenance and deletion semantics; require explicit safety evidence |
| `feat/ce-tools-governed-backend-20261115` | 15 ahead, 0 behind, 33 files; verifier blob previously `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70`, NOT re-fetched | HOLD_TEST / high | Engineering: isolated deterministic/adversarial tests; clinical 0/24 historical |
| `feat/cko-catalog-metamodel-automated-20261114` | 22 ahead, 0 behind, 48 files | HOLD_SEMANTIC / high | Architect: map catalog/PK/FK/dictionary and canonical atoms |
| `feat/cko-m08-m09-corpus-atomic-20261114` | 8 ahead, 0 behind, 8 files | HOLD_PROVENANCE / high | Editorial/legal: source rights and atomic evidence |
| `integration/cko-parsers-catalog-20261114` | 163 ahead, 0 behind, 175 files | HOLD_TEST / high | Engineering: isolated parser tests and schema contracts |
| PR #73 and workspace PR #71 | HEAD/checks NOT_RUN this round | HOLD_MERGE / high | Engineering: verify SHA, CI, review and rollback before merge |
| Privileged trigger / `cko.agent_id` | prior HOLD_SECURITY; no new test | HOLD_SECURITY / high | Security: trusted identity and adversarial invoker tests |

## Acceptance accounting
- PostgreSQL SELECT: **1/1 PASS**.
- Git compare: **4/4 PASS_READ**.
- Historical table-constraint count agreement **1996/1996**, not revalidated in this round; full semantic reconciliation **0/1996 in this round**, NOT_RUN.
- Extended sample: 50 rows read, 10 additional rows vs previous LIMIT 40; NOT homologated.
- Clinical tools **0/24 historical**, semantic contracts **0/20 historical**: not revalidated.
- Unit/adversarial/CI tests **NOT_RUN**; PR checks **NOT_RUN**; no new functional code change.
- **Global completion estimate: NOT ESTIMABLE** without consolidated criterion denominators.
- No official external normative source used this round. Candidate unpublished. Fail-closed; LGPD, rights, clinical/legal/security and provenance gates retained.

## Next work
1. Compare bounded export JSONL and live catalog by canonical constraint key and normalized definition, without treating non-atomic export as transaction snapshot.
2. Review cascade deletion of normative bindings, and composite PK handling in metamodel/ORM.
3. Execute isolated verifier and parser tests; fetch PR HEADs/checks; fix only reproducible code defects and commit evidence.
