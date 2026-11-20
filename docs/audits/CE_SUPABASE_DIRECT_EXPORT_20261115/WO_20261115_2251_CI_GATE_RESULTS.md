# WO 2026-11-15 22:51 BRT — CI gates and catalog scope

## Scope and provenance
- Repo: IndiciumFIN/calculadorasdeenfermagem; PR #73, draft/open; head at inspection: `5ebdc7735eb51d67e12e5ec4e0950a7d20d64c5f`; base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Supabase project: `pgsybzggewhinaniybiy`, read-only SELECT. No Neon, SOT or WU-TRIB.
- Fingerprint (GitHub head): `5ebdc7735eb51d67e12e5ec4e0950a7d20d64c5f`. Workflow run identifiers serve as CI evidence fingerprints; no file SHA reprocessing performed.

## CI results (actual, not inferred)
At head `5ebdc773`, GitHub Actions returned:
- CE Migration-first Supabase provenance: PASS, run 43783129870.
- Pipeline Determinístico: PASS, run 43783129924.
- CI - Validação: PASS, run 43783129872.
- Canonical repository invariants: FAIL, run 43783129926.
  - Job `Canonical contracts and CLI smoke`: FAIL at step `Verify canonical source and policy references`; earlier compile and deterministic negative tests PASS.
  - Job `Full admission blockers (fail closed)`: FAIL at step `Reject unresolved parser or import dependencies`.
- The failing workflow is an admission gate: NO MERGE. Logs/underlying precise assertions not yet recovered. Do not bypass or weaken checks.

## Physical catalog scope check
SELECT current_database(), count(information_schema.schemata), count(pg_class filtered relkind r/p/v/m/f and non-pg namespaces):
- database=postgres, 151 information_schema schemata, 661 relations with the above filter.
- These are **NOT** directly comparable to export's 59 schemas / 678 relations, because inclusion rules differ. Do not claim drift from this comparison. Recompute with manifest's exact scope/filter before comparison.
- Baseline export claims (pending exact manifest reconciliation): 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 policies.

## Status and next actions
- PASS: PR state/HEAD and 4 workflow run conclusions verified; SELECT catalog scope check executed.
- FAIL: canonical invariants 1/4 workflows; two failed job steps identified.
- HOLD_SECURITY/HOLD_HUMAN: 24/24 clinical tools not homologated; semantic promotion statuses, RLS, privacy, audit equivalence; SQL candidate deployment; PR merge.
- NOT_RUN: dynamic SQL tests, 24-tool semantic crosswalk, exhaustive branch reconciliation.
- Next: retrieve failing assertions, fix references and unresolved parser/import dependencies in isolated code PR with tests; do not change fail-closed behavior. Then inspect PR #73 manifest exact filters, compare per-object hashes, and reconcile the 24 tools.
- Change count: 1 audit document; 0 migrations/seeds/merges/production mutations. No global completion percentage claimed.
