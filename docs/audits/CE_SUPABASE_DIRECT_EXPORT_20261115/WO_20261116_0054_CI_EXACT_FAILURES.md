# WO — 2026-11-16 00:54 BRT — CI canonical blockers

Source: GitHub Actions run https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43783129926 ; jobs 133024663806 and 133024664041. Evidence obtained by reading complete job logs on 2026-11-16. Previous reconciliation commit b976bb9b74af3fee305f2b6669929b6ca7397f58.

## Exact failure

Command: `python scripts/verify_repository_integrity.py --output /tmp/canonical-structural.json` exits 2; strict variant also exits 2. Output schema CE-CANONICAL-INTEGRITY-1.0.0: source_contract_count=20; kernel_policy_count=20; error=1; pending=21; structural_pass=false; strict_pass=false.

* FAIL: LEGACY_SOURCE_DIR, `contracts/fonts` exists; canonical path is `contracts/fontes/`. Inspect files and consumers before removal or migration; do not delete blindly.
* HOLD: 16 MISSING_PARSER references: anvisa_dev, anvisa_med, atlas, catmat, cdsi, cid10, cid11 (icd11.py), esavi, fhir_vitais (fhir.py), medlineplus, mesh, pni, sies, sinan, taco, vacinas_cdc (vacinas.py). Cross-reference integration/cko-parsers-catalog-20261114 and inspect licenses, provenance and tests before integration.
* HOLD: 5 PACKAGE_IMPORT_NAMESPACE references: packages/cli/kernel/__init__.py, kernel/cli.py, kernel/core.py, main.py, validators/registry.py. Test `python -m packages.cli.main` without suppressing errors.

CI job 133024663806: canonical source/policy references FAIL; earlier compile and deterministic negative tests PASS. Job 133024664041: parser/import dependency gate FAIL. No attempt to weaken fail-closed checks.

## Incremental registry

| Object | Evidence fingerprint | Status | Next action |
|---|---|---|---|
| scripts/verify_repository_integrity.py | workflow run 43783129926 / jobs 133024663806,133024664041 | FAIL | Inspect canonical directory and consumers |
| contracts/fonts | LEGACY_SOURCE_DIR | FAIL | Inventory and compare semantics with contracts/fontes |
| packages/cli/parsers | 16 MISSING_PARSER | HOLD | Reconcile parser branch and validate tests/licensing |
| packages/cli imports | 5 PACKAGE_IMPORT_NAMESPACE | HOLD | Run import smoke and fix namespace |

No production SQL, DDL/DML, migrations, merges, or clinical publication. The 678/678 earlier comparison only covers relation-class counts, not object-by-object fingerprints. PR #73 remains HOLD_HUMAN pending full CI, security and clinical/legal gates.
