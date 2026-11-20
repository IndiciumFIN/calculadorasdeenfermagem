# CE/CKO/NCOS — checkpoint 2026-11-17 19:57 BRT

## Provenance and scope
Authoritative database: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` only. GitHub primary repository `IndiciumFIN/calculadorasdeenfermagem`. Previous checkpoint `docs/audits/WO_20261117_1856_CANONICAL_CI_ROOT_CAUSE.md`, blob `4cfc89f3d0a821ad445a3160b0f5dfa3e86c3a4b`. Prior CI run 44153056914. No DDL/DML, migrations, seeds, merge, deployment or branch deletion.

## New code-level delta (verified by GitHub fetch)
`scripts/verify_repository_integrity.py` on `audit/ce-supabase-migration-first-20261115`: blob `f6e74d988cfbe623e4a5f903b555c314482cbf40`.
Same path on `integration/cko-parsers-catalog-20261114`: blob `f6d72d91455c530d5bc3f9fbed283b389851b151`.
**Delta confirmed**: parser integration branch adds canonical validation of policy validator IDs (regex, uniqueness), source validator schema and exact source/policy validator list parity, with findings `SOURCE_VALIDATOR_SCHEMA` and `SOURCE_VALIDATOR_POLICY_DRIFT`. The audit branch's verifier checks only whether policy validators is a nonempty list. This is a genuine semantic verification gap, not grounds to copy code blindly; needs isolated tests and review before cherry-pick. No SHA-256 content fingerprint computed; Git blob SHA is the verified identity.

`contracts/fonts` and `contracts/fontes` are real GitHub directories at the audit ref, but directory fetch endpoint cannot enumerate their contents. The legacy directory is not safe to delete without inventory.

## Independent authoritative DB SELECT
Queried `pg_constraint` for `cko_governance.architecture_layer_bindings` and `cko_governance.artifact_normative_bindings`: 5 definitions returned. Triple PK `(profile_id,architecture_layer_id,implementation_layer_id)`; normative binding FK to controlled_artifacts remains `ON DELETE CASCADE`. No observed definition delta against prior five-row checkpoint; this was a repeat read, not a fresh export-to-catalog comparison. Provenance retention still HOLD_HUMAN.

## CI status
Fetched jobs for run 44153056914: 2/2 selected jobs still failure; deterministic negative tests step PASS; canonical source/policy verification FAIL; CLI smoke SKIPPED; strict blocker check FAIL. This is a historical run, not a fresh PR HEAD CI validation. PR #73 and workspace PR #71 current HEADs/checks NOT_RUN.

## Work orders
| ID | Object / Git blob fingerprint | Delta | State | Risk | Test and acceptance | Owner / next action |
|---|---|---|---|---|---|---|
| CE-VERIFY-DELTA | scripts/verify_repository_integrity.py: audit `f6e74d98...`, parsers `f6d72d91...` | Added validator schema and source/policy parity in parser branch | HOLD_TEST | high | fixtures for duplicate/malformed IDs and mismatch; deterministic negative tests and CI green | Engineering: test and port guarded checks |
| CE-LEGACY-DIR | contracts/fonts vs contracts/fontes | Both directories confirmed, contents not enumerated | HOLD_VERIFY | high | enumerate blobs and consumers; no unreviewed deletion | Engineering |
| CE-PARSER-16 | 16 missing parsers from prior run | no fresh delta verified | HOLD_VERIFY | high | verified implementations, licensing, provenance, smoke | Parsers team |
| CE-IMPORT-5 | five namespace paths from prior run | no fresh delta verified | HOLD_VERIFY | medium | module import smoke PASS | Engineering |
| CE-DB-PROV | cko_governance.artifact_normative_bindings FK | definition unchanged in SELECT | HOLD_HUMAN | high | demonstrate historical retention and rollback idempotence | DB/provenance governance |
| CE-PR73/71 | PR #73 and workspace PR #71 | no current HEAD recheck | HOLD_CI | high | current SHA and required checks green | Engineering |

## Measured coverage
- Historical CI failed jobs re-read: 2/2, both FAIL.
- Selected DB constraints returned: 5/5, PASS_READ only; historical full individual comparison 5/1996 = 0.25%, NOT repeated.
- Verifier variants fetched: 2/2; code-level delta identified, not tested.
- Clinical homologation: historical 0/24, NOT revalidated.
- Parser implementations: 0/16 verified in this round, NOT_RUN.
- Import issues: 0/5 tested, NOT_RUN.
- Tests executed this round: 0; CI new runs: 0.
- Global completion estimate: **NOT ESTIMABLE**, no unified acceptance denominator.

## Gates and next actions
Keep fail-closed. Candidate is not published. Prioritize minimal safe verifier parity fix with regression tests; inventory legacy directories; check parser implementations and namespace imports; validate current PR HEADs/CI; compare database catalog vs export by stable keys, not counts alone. No external normative source consulted.