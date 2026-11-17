# CE / CKO / NCOS — WO 2026-11-17 02:54 BRT — cross-schema agent session scan

Status: PASS_STATIC / HOLD_SECURITY. Source of physical truth: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. No database mutation.

## Provenance and delta
Parent checkpoint: `docs/audits/WO_20261117_0149_AGENT_SESSION_PROVENANCE.md`, prior recorded commit `c7b5ebd45f5d87e8a6808f0c6d7fef8f4f3570e2`. Current GitHub comparison before this commit: `main` SHA `e0f62491b104f4a97c6025a6393cabc2e7ada30e`, audit branch 57 ahead, 0 behind. Parent document blob SHA `c4124ea1aec5839544e8f82e477f88eff5153759`. Direct-export README blob SHA `a0e074bf9da401a3d50dd761536bcad3a9b96150`.

SELECT-only live catalog query expanded from `cko_%` to **all non-system schemas**, selecting pg_proc functions whose `prosrc` contains `cko.agent_id`, `set_config`, or a regex for SET cko.agent_id. Four matching functions: one CKO closure guard, two realtime, one storage. No function body changed or was reprocessed; only fingerprints and match flags inspected. The three platform functions mention generic `set_config` but **do not reference `cko.agent_id`**. This does not rule out client-side SET, dynamic SQL, external callers, or uninspected procedures.

## Object-level register
| Object | Fingerprint MD5(prosrc) | Delta / classification | Risk | Test, owner, action and acceptance |
|---|---|---|---|---|
| `cko_governance.guard_material_finding_closure_learning_v1()` | `bfd24b5c361d73bb706c797133ad9b0c` | unchanged; sole explicit `cko.agent_id` reference | HOLD_SECURITY / high | Security: establish trusted identity, caller ACL and isolated spoof/missing-value tests; acceptance fail-closed |
| `realtime.apply_rls(jsonb,integer)` | `f6d88df1b7c7e31dad695cb3921d6c6c` | generic `set_config` only, no agent ID reference | PASS_STATIC / low | Platform owner: no CKO change proposed |
| `realtime.authorize(text,text,text,text,text,text[],text[])` | `02a98c45e6f7b838efb1c72729b71eef` | generic `set_config` only | PASS_STATIC / low | Platform owner: no CKO change proposed |
| `storage.delete_lifecycle_objects(uuid[])` | `d84f28d3c58807042d7263e40c62ac12` | generic `set_config` only | PASS_STATIC / low | Platform owner: no CKO change proposed |
| `audit/ce-supabase-migration-first-20261115` | parent commit `c7b5ebd45f5d87e8a6808f0c6d7fef8f4f3570e2` | comparison 57 ahead / 0 behind | PASS_GIT_READ / medium | Engineering: review diff and CI before merge |
| Direct-export README | Git blob `a0e074bf9da401a3d50dd761536bcad3a9b96150` | historical inventory only | PASS_READ / HOLD_SEMANTIC | DBA: reconcile physical catalog before approval |
| Priority tool/metamodel/corpus/parser branches; PR #73 and workspace PR #71 | HEAD not checked this round | NOT_RUN | high | Engineering: fetch heads/checks and compare semantic fingerprints; accept only tested delta |

## Coverage, tests and blocking gates
- Query: **1/1 SELECT PASS**; returned **4/4 matches classified**. This is a *search-result denominator*, not proof of exhaustive execution paths.
- Historical direct export: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. Not recounted; no equivalence or homologation inferred.
- Clinical tools: historical **0/24 homologated**, current verification NOT_RUN. Semantic contracts: historical **0/20 homologated**, current verification NOT_RUN.
- Dynamic tests **0 NOT_RUN**; code unit tests **0 NOT_RUN**; CI **NOT_RUN**. Overall completion percentage **NOT ESTIMABLE** without a validated acceptance-criteria denominator.
- HOLD_SECURITY: untrusted `cko.agent_id` session setting and indirect caller paths. HOLD_HUMAN: clinical, licensing, provenance and legal sign-off. Candidate is not published.
- No DDL/DML, migrations, seeds, privileges, deployment, branch deletion or merge.

## Next independent actions
1. Inspect invoker ACL and client-side references to `cko.agent_id`; design isolated fail-closed regression tests.
2. Fetch current HEADs/CI for PR #73 and workspace PR #71, and four priority feature branches; reconcile code/SQL/catalog object-level delta.
3. Only propose a safe code patch after actual code and tests are inspected; preserve immutable evidence and rollback criteria.
