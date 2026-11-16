# WO — 2026-11-16 — ANVISA contract semantic drift

Scope: CE/CKO only. No production writes.

## Evidence
- Source branch: integration/cko-parsers-catalog-20261114
- New regression test commit: 7fce0d726499a8b35f989fa25006599b65401ea6
- Canonical `contracts/fontes/anvisa_dev.json`: blob SHA `54372d627c73a7b9ccdb8ce9b39281fd15d22e55`; `validators` is a nonempty array and `source_contract` points to canonical path.
- Legacy `main:contracts/fonts/anvisa_dev.json`: blob SHA `7f25153f5dbdff7695ac452ed98d88677b9cf072`; `validators` is a scalar string and `source_contract` is absent.
- Canonical `contracts/fontes/anvisa_dou.json`: blob SHA `7ad43853784754937320425833cebfd94c24f868`.
- Semantic result: FAIL equivalence for anvisa_dev (not merely a path rename). The previously reported fingerprint drift must not be resolved by blind hash refresh.
- Git compare main...integration branch at query time: ahead 159, behind 0; branch PR #73 still requires separate diff.
- Physical PostgreSQL SELECT, project pgsybzggewhinaniybiy: r=611, p=1, v=49, S=17; total=678. Quantitative PASS only, no object-level approval.

## Change
Added `tests/test_anvisa_contract_shape.py` to the parser integration branch, checking nonempty array validators and canonical source_contract for both ANVISA contracts. Tests NOT_RUN in GitHub Actions at this checkpoint; no merge.

## Gates and next actions
- PASS: file contents and blob hashes retrieved, regression test committed, read-only catalog counts.
- FAIL: legacy vs canonical anvisa_dev semantic equivalence.
- HOLD_VERIFY: remaining 19/20 legacy/canonical contract pairs, 16 parser references, 5 imports, CI execution.
- HOLD_HUMAN: clinical/legal licensing, 24 tool releases and PR #73 merge.
- Next: execute the new test in CI, compare all 20 contract pairs by normalized JSON structure with explicit type checks, then cherry-pick only validated fixes into the PR #73 integration branch.
- Rollback of this isolated test commit: revert commit 7fce0d7 on the integration branch; no database rollback required.
