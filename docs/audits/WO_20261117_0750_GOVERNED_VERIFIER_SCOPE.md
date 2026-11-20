# CE / CKO / NCOS — WO 2026-11-17 07:50 BRT — governed tools verifier scope and function fingerprint

State: PASS_READ / HOLD_VERIFY / HOLD_SECURITY / HOLD_CLINICAL / HOLD_MERGE. Only physical authority: Supabase Calculadoras-Smart pgsybzggewhinaniybiy. Database action: SELECT only.

## Verified checkpoint and delta
- Previous checkpoint WO_20261117_0657_PHYSICAL_BRANCH_RECONCILIATION.md Git blob SHA `1f89186c0aafc6699de323673adec670b6e5535b`.
- Export README blob SHA `a0e074bf9da401a3d50dd761536bcad3a9b96150`, unchanged. Inventory **historical**, not live recounted: 59 schemas / 678 relations / 255 migrations / 7246 columns / 1996 constraints / 1268 indexes / 100 RLS policies.
- Direct SELECT `md5(pg_get_functiondef(p.oid))` for `cko_governance.guard_material_finding_closure_learning_v1()` returned `46e2f53d4f434dbe3eb319a47f8ef8f9`, SECURITY DEFINER=true. Earlier fingerprint `bfd24b5c361d73bb706c797133ad9b0c` used an **unverified hashing method**; these hashes cannot be compared as evidence of code delta until the original canonical hashing expression is recovered. DO NOT mark function changed or reprocess as changed.
- Inspected `scripts/verify_governed_tools.py` on `feat/ce-tools-governed-backend-20261115`, blob SHA `cbb3a23d3a392c1e902aae33229ad302f05b0de6`. It uses `root.rglob('*')` over every file except the two output manifests, rather than an explicit source allowlist/tracked-file set. Therefore untracked local files, cache artifacts and potentially .git internals can enter candidate checksums, making verification environment-dependent. This is a **code review finding**, not a reproduced test failure. Also the verifier writes manifest/checksums, so it must not be run in a source checkout without controlled output location and rollback.
- Inspected `scripts/verify_supabase_snapshot.py`, blob SHA `1aa27db9798a08159d667c89a1d724c952dc024b`; its read-only manifest verification has not been executed.
- Four priority branch comparisons to main: tools 14 ahead / 0 behind / 33 files; metamodel 22 / 0 / 48; corpus 8 / 0 / 8; parsers 163 / 0 / 175. Base commit `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. No semantic integration implied.

## Work-order register
| Object | Fingerprint / delta | Status / risk | Responsible and next action / acceptance |
|---|---|---|---|
| governed-tools verifier | blob `cbb3a23d3a392c1e902aae33229ad302f05b0de6`; newly identified unrestricted filesystem enumeration | HOLD_VERIFY / medium | Engineering: constrain deterministic tracked source set, exclude generated/cache/.git, add adversarial tests for untracked files and repeated runs; require byte-identical outputs and 24 contract assertions |
| closure guard | md5(pg_get_functiondef) `46e2f53d4f434dbe3eb319a47f8ef8f9`; non-comparable with historical MD5 | HOLD_SECURITY / high | Security/DBA: recover original fingerprint algorithm, review privileged caller paths and agent identity trust; isolated tests |
| Supabase snapshot | README blob `a0e074bf9da401a3d50dd761536bcad3a9b96150` | PASS_READ / HOLD_RESTORE | Data architecture: verify manifest offline, no database mutation; independently reconcile PK/FK, catalog and semantic contracts |
| tools branch | 14 ahead, 33 files | PASS_GIT_READ / HOLD_CLINICAL | Engineering/clinical: 24/24 evidence-backed approvals required |
| metamodel branch | 22 ahead, 48 files | PASS_GIT_READ / HOLD_SEMANTIC | Data architect: PK/FK and canonical dictionary crosswalk, no duplicate tables |
| M08/M09 corpus branch | 8 ahead, 8 files | PASS_GIT_READ / HOLD_PROVENANCE | Editorial/legal: rights, primary evidence and atom dedup |
| parsers branch | 163 ahead, 175 files | PASS_GIT_READ / HOLD_VERIFY | Engineering: parser regression and normalization |
| PR #73 and workspace PR #71 | HEAD/checks not retrieved this round | NOT_RUN / HOLD_MERGE | Engineering: check CI, conflicts, permissions before merge |

## Quantitative control and acceptance
- Branch comparisons 4/4 PASS_READ = 100% of **this round's requested branch reads**, not completion.
- SQL SELECT 1/1 PASS. Function 1/1 catalog record returned; security approval 0/1.
- Verifier scripts 2/2 inspected; unit tests 0 executed (NOT_RUN); CI 0 (NOT_RUN); adversarial tests 0 (NOT_RUN).
- Clinical homologation historical 0/24; semantic contract homologation historical 0/20; no new approvals.
- Global completion estimate: **NOT ESTIMABLE**, missing consolidated acceptance denominator.
- No DDL/DML, migrations, seeds, merges, deployment, branch deletion or candidate publication. No functional code changes this round: fix is pending controlled regression setup and reproducibility check.
- Sources checked 2026-11-17: connected GitHub file/compare API, connected PostgreSQL catalog SELECT. No external clinical normatives used this round.
