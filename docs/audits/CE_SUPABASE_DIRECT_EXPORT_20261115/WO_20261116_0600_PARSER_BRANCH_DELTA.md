# WO 2026-11-16 06:00 — Parser branch delta

Status: HOLD_VERIFY. Scope: GitHub metadata only; Supabase not queried in this checkpoint.

## Verified refs
- PR #73: open, draft, unmerged; head `ffe09b883be8975bbdcf1f714faf67a94f30e984`; base `main` `e0f62491b104f4a97c6025a6393cabc2e7ada30e` before this commit.
- `integration/cko-parsers-catalog-20261114` vs main: ahead 159, behind 0.
- Parser integration vs PR #73 audit branch: ahead 159, behind 39 (diverged). Therefore do not merge wholesale.
- GitHub compare reports removal of legacy `contracts/fonts/*.json` and modifications to canonical `contracts/fontes/*.json`, including `anvisa_dev.json`; changes are not evidence of semantic equivalence.

## Gates and next action
- FAIL/HOLD: `anvisa_dev.json` fingerprint drift reported in previous WO; revalidate bytes and normalized JSON against historical manifest before any transport.
- HOLD: verify all 20 pairs, file hashes and canonical contract fields; inspect 16 missing parser targets and 5 namespace imports against current HEAD.
- HOLD: selective cherry-pick or reconstruction only after test evidence and dependency check. Preserve clinical provenance and fail-closed validators.
- NOT_RUN: CI and local tests this run.
- NOT_RUN: PostgreSQL catalog SELECT this run. Previous inventory 678/678 is quantitative only; 0/678 semantic matches newly validated.
- 0/24 clinical tools homologated; 0 migrations, seeds, merges, or production SQL writes.

Source: GitHub connector get_pr_info PR #73 and compare_commits main...integration and audit...integration, queried 2026-11-16. This checkpoint is an incremental metadata record, not a completion claim.
