# CE / CKO / NCOS — checkpoint 2026-11-18 11:48 BRT

## Baseline and identity
Previous versioned checkpoint: `docs/audits/WO_20261118_1053_PR73_CI_HEAD_REVALIDATION.md`, blob `cb22ff4b4f2df6a8030c17cc56889fdbfea3d5c9`. PR #73 HEAD before this checkpoint: `ffe7b4fc56adee9c260567ca8042359c68dbf55a`, open DRAFT, base main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. PR #71 open DRAFT; prior verified HEAD `1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d` (not independently re-fingerprinted here). No merges authorized.

## Fresh CI evidence, exact prior PR #73 HEAD
GitHub Actions commit `ffe7b4fc56adee9c260567ca8042359c68dbf55a`: Pipeline Determinístico run 44318547257 PASS; Canonical repository invariants run 44318546858 FAIL; CE Migration-first Supabase provenance run 44318546653 PASS; CI - Validação run 44318546931 PASS. Global gate FAIL (3/4). Previous failing jobs identified as canonical source-policy reference validation and unresolved parser/import admission; no claim of repaired jobs. Workflow results for this newly authored checkpoint commit NOT_RUN.

## Physical truth — SELECT-only
Project `pgsybzggewhinaniybiy` / Calculadoras-Smart verified via connected Supabase projects. SELECT grouped `pg_catalog.pg_constraint` by type in `cko_governance`: CHECK 61, FK 81, PK 88, UNIQUE 34, total 264; aggregate unchanged from prior checkpoint. No database writes. Manifest `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` read, project matches, snapshot marked NON_ATOMIC_ACROSS_QUERIES, HOLD_HUMAN. Historical coverage: 59 schemas, 678 relations, 255 migrations, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS; 22/22 Git blob hashes previously verified and NOT_REPROCESSED (no manifest delta detected). The manifest is not a physical dump or clinical acceptance.

## Work orders and acceptance
| WO / object | Fingerprint / delta | Status / risk | Evidence / test | Owner and next action | Acceptance |
|---|---|---|---|---|---|
| CE-PR73 / audit branch | HEAD `ffe7b4fc...` vs prior `907ce405...`; new checkpoint delta | PASS_READ / high | GitHub PR metadata | Engineering: retain draft | All required CI PASS on same HEAD; safety gates signed |
| CE-CI / canonical | run 44318546858 FAIL; same failure class | FAIL / high | GitHub Actions conclusion | Engineering: inspect precise canonical source-policy failure, patch proven mismatch | reference validator and CLI smoke PASS |
| CE-PARSER / integration branch | unresolved dependency class; exact HEAD NOT_RUN | HOLD_VERIFY / high | previous admission failure; no new local tests | Engineering: compare import namespace and parser files, test negative paths | zero unresolved parser/import dependencies |
| CE-WORKSPACE / PR #71 | prior HEAD `1976da6...`, current SHA NOT_RUN | HOLD_VERIFY / medium | prior PR read, no new CI | Frontend: verify exact head and checks | required CI PASS without migrations |
| CE-SUPABASE / governance | counts c61/f81/p88/u34; delta 0 aggregate | PASS_AGGREGATE / HOLD_OBJECT_MAPPING, medium | SELECT PASS | DB architecture: compare PK/FK object identities and definitions | zero unexplained differences |
| CE-EXPORT / manifest | blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`; 22/22 historical | PASS_HASH historical / low | manifest read; individual hashes NOT_REPROCESSED | Audit: only rerun on fingerprint delta | stable per-file blobs |
| CE-TOOLS / feat/ce-tools-governed-backend-20261115 | 24 candidates; branch HEAD NOT_RUN | HOLD_HUMAN / high | clinical acceptance NOT_RUN | Clinical engineering: validate 24 tools | 24/24 independently accepted |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | HEAD NOT_RUN | HOLD_VERIFY / medium | NOT_RUN | Architecture: semantic dictionary/PK-FK dedup | no conflicting canonical identity |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | HEAD NOT_RUN | HOLD_HUMAN / high | NOT_RUN | Clinical content: source/license/atom trace | evidence and license accepted for every published atom |
| CE-CONSTRAINT-DELTA / global | export 1996 vs prior live 2109; numeric delta +113 not object proof | HOLD_SEMANTIC / high | identity reconciliation NOT_RUN | DB architecture: compare type, schema, table, definition, fingerprint | every genuine delta classified |

## Measurable coverage, not homologation
Git export hashes 22/22 PASS historical (100%); governance aggregate 1/1 PASS; PR #73 HEAD 1/1 read; PR #73 required workflows 3/4 PASS (global FAIL); object-by-object constraints 0/1996 reconciled this round; tools 0/24 revalidated this round; parsers 0/16 and imports 0/5 corrected this round; new local/adversarial tests NOT_RUN; PR #71 current CI NOT_RUN. **Global completion estimate: NOT_ESTIMABLE**: no unified acceptance denominator. No invented percentages.

## Safety and sources
Only SELECT and GitHub metadata/file reads plus this checkpoint commit. No DDL/DML, migrations, seeds, deploy, merge, branch deletion or publication. Fail-closed; preserve clinical/legal/security/LGPD/copyright/provenance gates. Sources: connected GitHub PR #73, Actions runs 44318547257/44318546858/44318546653/44318546931, Supabase SELECT and GitHub manifest; observed 2026-11-18. Next: inspect canonical failure output and parser import paths; perform independent tool, metamodel and corpus work, keeping HOLD_HUMAN where required.
