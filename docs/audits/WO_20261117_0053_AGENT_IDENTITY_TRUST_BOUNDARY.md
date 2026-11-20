# CE / CKO / NCOS — WO 2026-11-17 00:53 BRT — agent identity trust boundary

Status: PASS_STATIC / HOLD_SECURITY. Physical source ONLY Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. SQL SELECT only. No publication or production mutation.

## Parent and delta
Parent checkpoint: `docs/audits/WO_20261116_2347_MATERIAL_FINDINGS_TRIGGER_EFFECTS.md` (fetched on branch). Prior fingerprint `bfd24b5c361d73bb706c797133ad9b0c` verified unchanged in live PostgreSQL; no redundant body reprocessing. Git comparison before commit: main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`, audit branch 55 ahead / 0 behind. Prior recorded commit `4d66403d03dd5547d78c88a828cf1a663a4a6846`.

## Physical evidence (2026-11-17)
1. First catalog query searched the wrong schema (`cko_validation`) for three functions; returned zero rows. Corrected scope using prior checkpoint (`cko_governance`). Query outcome FAIL_SCOPE then PASS.
2. `cko_governance.guard_material_finding_closure_learning_v1`: live md5(prosrc) `bfd24b5c361d73bb706c797133ad9b0c`; SECURITY DEFINER, fixed search_path. A material finding closure requires a validated learning link. Additional self-closure prohibition is conditional on `current_setting('cko.agent_id',true)='AGT-CAPETINHA-001'` and `finding_id LIKE 'FIND-CAP-%'`. When session setting is absent or different, that specific self-closure predicate does not fire. This is a **potential identity trust-boundary weakness**, not demonstrated exploitability; the learning gate remains in place.
3. Static search across `cko_%` functions returned 3 references to agent setting/token: `cko_governance.guard_material_finding_closure_learning_v1` fingerprint `bfd24b5c361d73bb706c797133ad9b0c`, `cko_governance.route_material_finding_to_super_v1` fingerprint `dc8a3838886f7f2ba9a3f38631866242`, `cko_validation.run_capetinha_scan_v1` fingerprint `9a35c50128b0ae7ba61737e3eb0ae0d8`. No `set_config` substring in these three bodies; static search does NOT establish absence of external session-setting writers, dynamic SQL, or privileged callers.

## Work register
| Object / branch | SHA / fingerprint | Delta | Status | Risk | Test / owner / next action / acceptance |
|---|---|---|---|---|---|
| Audit branch | prior commit `4d66403d03dd5547d78c88a828cf1a663a4a6846` | new checkpoint | PASS_GIT_READ | low | GitHub owner: preserve branch; no merge |
| Closure guard | `bfd24b5c361d73bb706c797133ad9b0c` | identity conditional confirmed | PASS_STATIC / HOLD_SECURITY | high | Security: trace agent identity source and caller roles; isolated adversarial tests for absent/forged setting; fail-closed acceptance |
| Router | `dc8a3838886f7f2ba9a3f38631866242` | reference only, no delta verified | HOLD_VERIFY | medium | Security: trace context; do not repeat full review without delta |
| Scan function | `9a35c50128b0ae7ba61737e3eb0ae0d8` | reference only | HOLD_VERIFY | high | Security: inspect invoker authorization and effects in isolated tests |
| PR #73, tools, catalog, corpus, parsers; workspace PR #71 | HEAD SHA not checked this run | none | NOT_RUN | high | Engineering: fetch HEAD/checks and reconcile with candidate SQL before code changes |
| Direct export inventory | historical 59 schemas / 678 relations / 255 migrations / 7246 columns / 1996 constraints / 1268 indexes / 100 RLS policies | no recount | PASS_HISTORICAL_QUANT_ONLY | medium | DB owner: validate manifest hashes before treating as current |

## Progress and gates
- Static closure guard body: 1/1 inspected this round (100% **inspection only**); authorization dynamically homologated 0/1 (0%).
- Clinical tools: 0/24 homologated per previous checkpoint (0%; not revalidated).
- Semantic contracts: 0/20 homologated per previous checkpoint (0%; not revalidated).
- Branch priority reconciliation: 0/5 verified this round (0% run coverage, not product completion).
- Global completion: **not estimable**; denominator of acceptance criteria not consolidated.
- SQL: initial wrong-schema query 1 FAIL_SCOPE; corrected function query 1 PASS; static cross-schema query 1 PASS. Unit tests/CI NOT_RUN. No DDL/DML, migrations, seeds, ACL, deploy, merge or deletion.

## Next independent work
Trace role-to-agent identity binding (application layer and PostgreSQL invokers); build isolated negative tests and fail-closed guard design, with rollback/idempotency and security review before changing SQL. Separately reconcile 24-tool backend and parsers with catalog metadata. Preserve clinical, copyright, LGPD, provenance and legal gates; candidate content remains unpublished.
