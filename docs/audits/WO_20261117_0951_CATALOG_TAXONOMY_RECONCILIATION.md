# CE/CKO/NCOS — WO 2026-11-17 09:51 BRT — verifier follow-up and catalog taxonomy

Authority: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` only. SELECT-only. Candidate NOT published. No migrations/DDL/DML/merge.

## Evidence this run
- Functional verifier commit `64f8e7d9cf9edadccb66d3e541eb604a48357062` fetched and confirmed; `scripts/verify_governed_tools.py` blob `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70` unchanged from previous checkpoint. No delta: do not rehash/reprocess.
- Previous WO `WO_20261117_0853_GOVERNED_VERIFIER_FIX.md` blob `02e99765aa2ea93c8aed18945befd3fc2567d5bb`.
- SELECT non-system schemas: 59. SELECT pg_class relkind taxonomy: r=611, p=1, v=49, S=17; total **678** = 612 tables + 49 views + 17 sequences, exact match to reported inventory by identical taxonomy. This is **inventory reconciliation only**, not structural/clinical homologation. Columns, constraints, indexes, RLS, migrations NOT re-counted this run.
- main comparisons: tools 15 ahead/0 behind/33 files; metamodel 22/0/48; corpus 8/0/8; parsers 163/0/175. Compare counts are not semantic acceptance.
- PR #73 and workspace PR #71 both OPEN/DRAFT and mergeable reported true (GitHub metadata); checks/HEAD SHA NOT_RUN, merge blocked by gates.

## Work-order / fingerprint register
| Object | SHA / fingerprint and delta | Status / risk | Responsible, next action, acceptance |
|---|---|---|---|
| tools verifier | blob `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70`; delta none | FIX_COMMITTED / HOLD_TEST; medium | Engineering: isolated repeatability and adversarial tests; byte-identical outputs, fail-closed missing/symlink/untracked |
| PostgreSQL relation taxonomy | SELECT 611 r + 1 p + 49 v + 17 S = 678; reported 678 | PASS_SELECT / HOLD_SEMANTIC; medium | DBA: compare PK/FK, catalog dictionaries and candidate SQL; no competing tables |
| tools contracts | 24 candidates; no per-tool delta assessed | HOLD_CLINICAL; high | Clinical owner: 24/24 evidence and validation |
| metamodel branch | 22 ahead, 48 files; per-file fingerprints not refreshed | HOLD_SEMANTIC; high | Data architect: canonical PK/FK and normative crosswalk |
| corpus branch | 8 ahead, 8 files; per-atom fingerprints not refreshed | HOLD_PROVENANCE; high | Editorial/legal: licenses, sources, semantic dedup |
| parsers branch | 163 ahead, 175 files; per-file fingerprints not refreshed | HOLD_TEST; medium | Engineering: regression and normalization |
| PR #73 / workspace #71 | both open draft; HEAD/checks not verified | HOLD_MERGE; high | Engineering: verify HEAD, CI, security and rollback before merge |
| CKO agent identity | prior guard fingerprint method disputed; no new delta checked | HOLD_SECURITY; high | Security: isolated trust boundary tests |

## Acceptance counters / percentages
- Catalog taxonomy count reconciled: 678/678 = 100% **count reconciliation only**; semantic checks 0/1 in this WO.
- Four priority branch compare reads: 4/4 = 100% metadata comparison, **not integration**.
- Verifier fix commit: 1/1; executed tests 0/1 = 0% verification.
- Historical clinical acceptance 0/24 = 0%, NOT refreshed. Historical semantic contracts 0/20 = 0%, NOT refreshed.
- SQL SELECT queries 2/2 PASS (schema count and relkind taxonomy). Unit tests NOT_RUN, CI NOT_RUN, adversarial NOT_RUN.
- Global completion estimate: NOT ESTIMABLE; no consolidated acceptance denominator.

## Gates and next independent task
Fail-closed clinical, legal, copyright, LGPD, provenance, security. No publication, schema write, seed, migration, privilege change, merge, or branch deletion. Run isolated verifier tests; compare PK/FK and dictionary by SELECT; inspect PR HEAD/checks and implement only tested safe code corrections.
