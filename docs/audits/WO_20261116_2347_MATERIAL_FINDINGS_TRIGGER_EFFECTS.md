# CE / CKO / NCOS — WO 2026-11-16 23:47 BRT — material findings trigger effects

Status: PASS_CATALOG / HOLD_SECURITY. Physical source exclusively Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Read-only SQL; no production writes.

## Parent checkpoint and delta
Parent: `docs/audits/WO_20261116_2252_FINDINGS_TRIGGER_GRAPH.md`, GitHub blob SHA `aaca089f3b4d20cb082cc574670aec33ce606f71` (fetched this round). Prior three trigger-function fingerprints were rechecked and UNCHANGED; no fingerprint-valid work reprocessed. Delta is full static body analysis, timing/event definitions, and downstream table ACL/RLS. CE PR #73 and workspace PR #71 fetched: both OPEN; draft/NO-GO according to their issue descriptions. PR head SHAs and CI NOT_CHECKED.

## Physical evidence, SELECT only (2026-11-16)
- `cko_governance.enqueue_material_finding_learning_v1`: prosrc MD5 `1664d7596f034eef66ca8507e95c77da`, SECURITY DEFINER, owner postgres, fixed search_path. AFTER INSERT OR UPDATE OF severity,status. For material OPEN/OPEN_SCOPED/CLASSIFIED_HOLD finding, INSERT `cko_governance.error_learning_links` ON CONFLICT DO NOTHING, deterministic id `ELL-AUTO-` + hash; root cause initially PENDING.
- `cko_governance.guard_material_finding_closure_learning_v1`: prosrc MD5 `bfd24b5c361d73bb706c797133ad9b0c`, SECURITY DEFINER, owner postgres, fixed search_path. BEFORE UPDATE OF status. Blocks material closure without validated root cause and linked learning/training/regression/policy control; additionally blocks Capetinha self-closure when `cko.agent_id='AGT-CAPETINHA-001'` and finding id `FIND-CAP-%`. Risk: session-setting identity is not independently proven trustworthy; authorization reachability needs audit.
- `cko_governance.route_material_finding_to_super_v1`: prosrc MD5 `dc8a3838886f7f2ba9a3f38631866242`, SECURITY DEFINER, owner postgres, fixed search_path. AFTER INSERT OR UPDATE OF severity,status,description,evidence_refs. INSERT `cko_governance.super_notifications` ON CONFLICT DO UPDATE; unresolved notifications may be requeued, resolved notifications preserve delivery_status.
- All three downstream tables (`cko_validation.findings`, `cko_governance.error_learning_links`, `cko_governance.super_notifications`) have RLS disabled, FORCE disabled, zero policies; direct INSERT privileges for anon/authenticated/service_role returned false. This is not proof of inaccessible indirect privileged execution.
- All three functions unchanged relative to prior recorded fingerprints. No dynamic invocation.

## Register / work orders
| Object/branch | SHA or fingerprint | Delta | Status | Risk | Test / owner / next action / acceptance |
|---|---|---|---|---|---|
| Parent WO | blob `aaca089f3b4d20cb082cc574670aec33ce606f71` | read | PASS | low | GitHub fetch PASS |
| enqueue trigger function | `1664d7596f034eef66ca8507e95c77da` | identified insert into error_learning_links | PASS_STATIC / HOLD_SECURITY | high | Security owner: verify trigger effects and downstream constraints; isolated idempotence test required |
| closure guard function | `bfd24b5c361d73bb706c797133ad9b0c` | closure and self-closure predicates | PASS_STATIC / HOLD_SECURITY | high | Security owner: validate caller identity source, spoofability and state matrix; adversarial tests required |
| routing trigger function | `dc8a3838886f7f2ba9a3f38631866242` | notification upsert and requeue | PASS_STATIC / HOLD_SECURITY | high | Security owner: test retry/idempotence and resolved notification invariants |
| 3 target tables | physical RLS off, 0 policies | no direct INSERT for 3 checked roles | PASS_CATALOG / HOLD_SECURITY | high | Security owner: ACL/schema USAGE, transitive callers, invoker privileges |
| CE PR #73 | head SHA NOT_CHECKED | open | HOLD_SECURITY | high | CI owner: verify head/checks before merge |
| workspace PR #71 | head SHA NOT_CHECKED | open, NO-GO | HOLD_BUILD | high | Build owner: external preview and auth/CI gates |
| `feat/ce-tools-governed-backend-20261115` | NOT_CHECKED | 24 tools | HOLD_HUMAN | clinical | Clinical owner: per-tool evidence and contract tests |
| `feat/cko-catalog-metamodel-automated-20261114`, `feat/cko-m08-m09-corpus-atomic-20261114`, `integration/cko-parsers-catalog-20261114` | NOT_CHECKED | no proven delta | HOLD_VERIFY | provenance | CKO owner: hashes, SQL crosswalk, license, parsers |

## Coverage, tests, gates
- Trigger-function static bodies 3/3 inspected (100% of this scoped set, NOT full system); trigger definitions 3/3; downstream table RLS/INSERT ACL 3/3. PASS_CATALOG only, not security approval.
- SELECT calls 3/3 PASS (function definitions, downstream ACL/RLS, trigger definitions). GitHub checkpoint/PR reads PASS. Unit tests 0 NOT_RUN; CI 0 NOT_RUN; dynamic SQL/function execution 0 NOT_RUN.
- Historical inventory NOT_RECOUNTED: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies. Clinical 0/24 homologated (carried forward); semantic contracts 0/20 (carried forward). Global estimated completion NOT_ESTIMABLE (no consolidated accepted denominator).
- Acceptance: caller graph, effective privilege checks, immutable provenance, trustworthy identity, isolated rollback/idempotence, negative status-transition tests, clinical/legal/security approvals. No candidate publication, DDL/DML, migrations, seeds, merges, grants, branch deletion.
- Sources: direct PostgreSQL `pg_proc`, `pg_trigger`, `pg_class`, `pg_policy`, `has_table_privilege` SELECT; GitHub checkpoint, CE PR #73 and workspace PR #71 fetched 2026-11-16. No external normatives used.
