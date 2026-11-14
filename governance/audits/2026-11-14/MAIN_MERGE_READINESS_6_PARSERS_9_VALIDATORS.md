# NCOS/CKO — main merge readiness and non-bypassable release HOLD

**Checkpoint:** 2026-11-14 (Brazil/São Paulo)  
**Repository:** `IndiciumFIN/calculadorasdeenfermagem`  
**Candidata:** `integration/cko-parsers-catalog-20261114` / PR #61 (draft; stacked on PR #60)  
**Main base SHA:** `e0f62491b104f4a97c6025a6393cabc2e7ada30e`  
**Decision:** `MAIN_MERGE_HOLD` — user authorization for merge received, but mandatory technical/reviewer gates remain unsatisfied. **Clinical and editorial publication remain independently NO-GO.**

## Changes executed in this checkpoint

1. DATASUS CID-10 V2008 `CID-10-CATEGORIAS.CSV` metadata-only parser and adversarial tests, `KERNEL-POLICY-003@1.1.0`, documentation with WHO/CBCD rights HOLD.
2. ANVISA medical devices `TA_PRODUTO_SAUDE_SITE.csv` metadata-only parser; multiple manufacturer rows preserved, source IDs/hashes, privacy/rights HOLD, tests and `KERNEL-POLICY-009@1.1.0`.
3. **15 source-contract validator declarations** normalized into arrays exactly matching their canonical `KERNEL-POLICY-*` lists. Five others already matched. Total: **20 source contracts / 20 policy links**.
4. `scripts/verify_repository_integrity.py` now emits an **error** for source/policy validator drift, missing/invalid canonical arrays and duplicate references. Added negative regression cases (including valid `cid10_validator` with embedded digits) to `tests/test_repository_integrity.py`.
5. CI runs `test_repository_integrity.py` and archives the strict-admission JSON evidence even on FAIL.

## Evidence checked, not inferred

- [GitHub Actions #43609255509](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43609255509): **Combined parser/catalog/Kernel tests PASS**.
- Same run: **Strict canonical admission FAIL (correct and required)** with `repository_structural_pass=true`, `source_contract_ast_pass=true`, `missing_parsers=6`, `validator_holds=9`, `unimplemented_policy_validators=8`, `unconditional_true_validators=0`, `technical_admission_pass=false`, `clinical_release_allowed=false`, `editorial_publication_allowed=false`.
- GitHub PR reviews: **0** on #60 and **0** on #61 at checkpoint. No independent approval is asserted.
- `main` remains at `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. No merge, production deployment, Supabase mutation or clinical/editorial release executed in this checkpoint.

## Remaining P0 mandatory dependency groups

### Six source parsers still absent
| Contract | Required parser | Blocking validation |
|---|---|---|
| `atlas` | `packages/cli/parsers/atlas.py` | Precise official corpus, edition and legal operations not yet fixed; `HOLD_SOURCE` |
| `cdsi` | `packages/cli/parsers/cdsi.py` | MS/CGPNI official export/schema/version and rights pending |
| `esavi` | `packages/cli/parsers/esavi.py` | ANVISA official surveillance schema, de-identification and rights pending |
| `pni` | `packages/cli/parsers/pni.py` | PNI versioned export/schema, privacy and source rights pending |
| `sinan` | `packages/cli/parsers/sinan.py` | DATASUS SINAN record layout, LGPD/privacy and safety controls pending |
| `taco` | `packages/cli/parsers/taco.py` | UNICAMP TACO edition, machine-readable distribution and rights pending |

**Do not create empty Python files or fake fixtures as proof of source support.** Source → policy → validator → WO → Kernel → audit must hold before recognition.

### Nine validators remain in formal HOLD
`catmat_validator`, `cid10_validator`, `cid11_validator`, `cvx_validator`, `human_review_validator`, `loinc_validator`, `mesh_validator`, `ncm_validator`, `schema_validator`. Their direct `validate` calls deny unverified input; no true implementation/independent source membership is attested. Replacing denial with regex-only success would be a regression.

### Human/external gates
- **GitHub independent reviewer** for the exact PR head(s), anti-self-approval verified, and branch-protection evidence. The connected GitHub integration previously returned 403 for branch-protection read; do not claim it is enabled.
- The 46 M08/M09 clinical claims remain `HOLD_HUMAN`, plus source rights and editorial/release decisions by content/version/hash.
- CI of stacked PR #60 → #61 must pass the combined **strict** gate, not only technical subsets; production release requires separate professional/rights/security approval.
- Maintain technical branch promotion distinct from site deployment and atomized clinical content publication.

## Safe merge procedure after gate clearance

1. Complete six parsers from authoritative versioned formats and resolve nine validator holds without bypass.
2. Re-run strict gate; attach JSON evidence plus full CI logs and source/license chain.
3. Obtain independent technical review bound to current HEAD, verify GitHub protection and align stacked branches.
4. Merge PR #61 to its parent branch, rerun integrated tests, then merge the parent PR #60 into `main` with `expected_head_sha`. Verify actual HEAD, required workflows and independent clinical release hold afterward.
5. Do not delete source branches or promote contents until evidence is captured and approved.
