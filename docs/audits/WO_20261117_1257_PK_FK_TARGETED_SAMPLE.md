# CE / CKO / NCOS — WO 2026-11-17 12:57 BRT — targeted PK/FK catalog sampling

Authority: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` only. Read-only SQL. No Neon, SOT, accounting analysis, DDL/DML, migration, seed or merge.

## Evidence and delta
- Previous checkpoint commit: `7c9f8ffa7595f2cce9c12c119cafcd28b59fdc66` (11:53), verified via GitHub fetch_commit.
- Export manifest at `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` read directly from audit branch: project ref matches; observation 2026-11-15; NON_ATOMIC_ACROSS_QUERIES; HOLD_HUMAN; 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 table constraints, 1268 indexes, 100 RLS policies. Exported constraints Git blob `83642780302397204b39796e1bd3604a77c68f53`. No claim of atomic snapshot.
- Verifier `scripts/verify_governed_tools.py` in `feat/ce-tools-governed-backend-20261115`: current fetched Git blob `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70`, same as prior checkpoint: **no delta**, skip reprocessing.
- New targeted PostgreSQL SELECT: `pg_constraint` joined to `pg_class` and `pg_namespace`, restricted to `cko_governance` and `cko_validation`, PK/FK only, ordered, LIMIT 40. Query succeeded; 40 rows returned, including `cko_governance.agent_appointments` PK `appointment_id` and FKs to `agent_registry`, `agent_job_profiles`, `cko_ai.selection_decisions`. Observed FK actions `ON DELETE RESTRICT` for sampled relationships. **Sampling is not semantic reconciliation**.
- New observation: governance agent tables have multiple cross-schema FK edges; their integrity must be evaluated against SQL candidates and canonical dictionary before approval. No physical drift established.

## Work register
| Object / branch | Fingerprint / delta | Status and risk | Owner / next action / acceptance |
|---|---|---|---|
| Export manifest | exported constraint blob `83642780...`; unchanged reference | PASS_READ / medium | DBA: compare canonical keys and normalized definitions for 1996 exported table constraints against catalog |
| `cko_governance.agent_appointments` | catalog PK and FK definitions sampled, no baseline per-object fingerprint established | PASS_SAMPLE / HOLD_SEMANTIC, high | Data architect: map PK/FK to dictionary and candidate SQL; zero unexplained semantic deltas |
| 24-tool verifier | Git blob `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70`; no delta | HOLD_TEST / medium | Engineering: run deterministic and adversarial isolated tests; acceptance repeatable manifest |
| metamodel, M08/M09, parsers branches | HEADs not revalidated in this round | HOLD_VERIFY / high | Engineering/editorial: SHA-level crosswalk, licensing and provenance |
| PR #73 / workspace PR #71 | checks and HEADs not revalidated this round | HOLD_MERGE / high | Engineering: verify CI and approvals; no merge |
| CKO identity and privileged trigger | prior HOLD_SECURITY, not re-executed | HOLD_SECURITY / high | Security: invoker identity and adversarial tests |
| Clinical 24 tools | 0/24 historically accepted; not revalidated | HOLD_HUMAN / high | Clinical reviewer: source-backed test evidence and authorization |
| Semantic contracts | 0/20 historically accepted; not revalidated | HOLD_VERIFY / high | Architect: evidence-backed crosswalk |

## Metrics and gates
- Catalog SELECT 1/1 PASS. Targeted result 40 PK/FK records sampled; **40 is not the denominator for acceptance**.
- Historical quantitative count agreement: 1996/1996 table constraints, NOT re-counted this round. Per-object semantic acceptance: 0/1996 verified this round (NOT_RUN for full comparison).
- Git file reads 2/2 PASS; prior commit read 1/1 PASS. Functional branch HEAD comparisons 0/4 NOT_RUN. PR checks NOT_RUN.
- Unit, adversarial, CI tests NOT_RUN. No code fix this round. Global completion estimate **NOT ESTIMABLE**: no consolidated acceptance denominator.
- No external normative source consulted. Candidate remains unpublished. Maintain clinical, legal, copyright, LGPD, provenance, fail-closed and security gates.

## Next independent work
Fetch exported constraint records in bounded batches; compare normalized `(schema, table, name, type, definition)` against PostgreSQL SELECT with stable fingerprinting and explicit methodology. Run isolated verifier tests, then inspect PR HEAD/checks and semantic mappings. No destructive action authorized.
