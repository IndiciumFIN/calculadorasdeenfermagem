# CE / CKO / NCOS — WO 2026-11-17 08:53 BRT — governed verifier deterministic source scope

Authority: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` only. All database queries SELECT-only. Candidate is NOT deployed. No merge/migration/seed/DDL/DML.

## Verified delta and checkpoint
- Previous audit checkpoint: `WO_20261117_0750_GOVERNED_VERIFIER_SCOPE.md`; Git blob SHA from this read not captured (content was read). Previous verified source verifier blob `cbb3a23d3a392c1e902aae33229ad302f05b0de6`.
- **Functional code correction committed** on `feat/ce-tools-governed-backend-20261115`: commit `64f8e7d9cf9edadccb66d3e541eb604a48357062`, updated verifier blob `1bb7ce41fff15820ed9a980b6b793d1fbf54bc70`.
- Replaced `root.rglob('*')` unrestricted traversal with deterministic `git ls-files --cached -z` inventory. Explicitly exclude two generated manifests, sort/deduplicate, reject missing/symlink/escaping indexed files, fail closed when Git inventory unavailable; hash payload once and use its length.
- Existing unit suite remains mandatory before generating candidate manifests; no clinical publication.
- Export README Git blob `a0e074bf9da401a3d50dd761536bcad3a9b96150` re-read unchanged. Historical inventory: 59 schemas, 678 relations (612 physical tables, 49 views, 17 sequences), 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies.
- Fresh SELECT: non-pg schemas = **59**, relations counted by relkind r/p/v/m/f = **661**. The historical 678 includes **17 sequences**, excluded by the live SELECT relkind filter; **do not classify this as schema drift**. Recount by identical object taxonomy before comparison.
- `main...feat/ce-tools-governed-backend-20261115` read before correction: 14 ahead / 0 behind, base SHA `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. Code commit adds one ahead; no merge.

## Object/work-order register
| Branch / object | Fingerprint / delta | Status and risk | Owner / next action / acceptance |
|---|---|---|---|
| tools / scripts/verify_governed_tools.py | old blob cbb3a23d3a392c1e902aae33229ad302f05b0de6 -> new 1bb7ce41fff15820ed9a980b6b793d1fbf54bc70; commit 64f8e7d | FIX_COMMITTED / HOLD_TEST, medium | Engineering: run Python unit suite and adversarial reproducibility twice in isolated checkout, untracked cache injection, symlink/missing file and staged delta; require byte-identical manifest/checksums for unchanged index/worktree |
| tools / 24 governed contracts | unchanged candidate branch, no per-tool fingerprints refreshed | HOLD_CLINICAL, high | Clinical reviewers: evidence-backed 24/24 signoff before release |
| metamodel / canonical PK-FK | no fresh per-file delta | HOLD_SEMANTIC, high | Data architecture: compare physical PK/FK/dictionary against candidate SQL; prohibit competing tables |
| corpus M08/M09 / atoms | no fresh delta | HOLD_PROVENANCE, high | Editorial/legal: verify primary sources, licenses, semantic dedup |
| parsers / normalization | no fresh delta | HOLD_VERIFY, medium | Engineering: regression tests and contract normalization |
| physical PostgreSQL / object taxonomy | SELECT 59 schemas; 661 relkind r/p/v/m/f; historical 678 includes 17 sequences | PASS_SELECT / HOLD_RECOUNT, low | DBA: count with consistent relkind including sequences; validate catalog export fingerprint before claiming delta |
| CKO closure guard / agent identity | previous md5(pg_get_functiondef) 46e2f53d4f434dbe3eb319a47f8ef8f9, method differs from older fingerprint | HOLD_SECURITY, high | Security: privileged caller and identity provenance isolated tests; no reprocessing without delta |
| PR #73 and workspace PR #71 | HEAD and checks not revalidated | NOT_RUN / HOLD_MERGE | Engineering: inspect current HEAD/checks and conflict/rollback before merge |

## Acceptance counters (not completion percentages)
- Source-scope defect: **1/1 code fix committed** (100% of this identified edit), **0/1 validated by executed tests**.
- Live SQL SELECT: **1/1 PASS**. Object category comparison **0/1 homologated**.
- Tools clinically homologated: historical **0/24**; semantic contracts historically **0/20**; neither refreshed.
- Unit tests **0 executed / NOT_RUN**; CI **NOT_RUN**; adversarial tests **NOT_RUN**.
- Global completion estimate: **NOT ESTIMABLE** (no unified acceptance denominator). Inventories are not homologation.

## Gates
No DDL, DML, migrations, seeds, permission change, merge, deployment, or branch deletion. Clinical/legal/security/LGPD/copyright/provenance gates remain fail-closed. Next independent task: run isolated tests on code correction and reconcile SQL catalog taxonomy, then PR HEAD/checks.
