# WHO ICD-11 MMS JSON-LD — controlled technical candidate

**Scope**: `packages/cli/parsers/icd11.py` / contract `contracts/fontes/cid11.json` / policy `KERNEL-POLICY-004@1.1.0`.

## Normative sources (checked 2026-11-14)
- WHO ICD-API v2 official API and OAuth specifications: https://icd.who.int/docs/icd-api/APIDoc-Version2/
- WHO official ICD JSON-LD schema: https://icd.who.int/docs/icd-api/ICD-schema/
- WHO release list, including 2026 version: https://icd.who.int/icdapi/
- WHO API v2.6 release notes: https://icd.who.int/docs/icd-api/ReleaseNotes-Version2.6/

## Accepted subset
Only one **already downloaded, SHA-256 pinned** JSON-LD WHO ICD-11 MMS **category** entity response from a versioned `/icd/release/11/{releaseId}/mms/{id}` URI. The caller supplies `source_id`, `document_id`, explicit `release_id` (YYYY-MM), and trusted-manifest `expected_sha256`. This module does **not** obtain WHO OAuth credentials or make requests.

The parser rejects Foundation responses, unspecific unversioned/latest entities, blocks/chapters/window entities, multiple parents, release mismatches, duplicate JSON object keys, invalid WHO source context, oversized payloads, and malformed identifiers. No inference of mapping to ICD-10, SNOMED, NANDA/NIC/NOC or clinical appropriateness is allowed. The narrow code regex is a technical guard, **not** proof of membership in WHO release. Unsupported WHO variants must be implemented via a separate reviewed contract rather than silently accepted.

Only source/document identifiers, code/URIs/parent candidate, declared release, input SHA, record SHA and language metadata are returned. **No title, definition, synonyms, annotations, exclusion details, coding notes or postcoordination content** are emitted.

## Critical limitations and release controls
- SHA-256 match proves byte equality only; not origin authentication, proper WHO attribution, licensing or code correctness.
- The declared release ID is checked against the URI but not externally independently verified; origin and reference membership remain explicitly false.
- Every record is `HOLD_HUMAN`, `publication_allowed=false`, `rights_verified=false`, `release_allowed=false`.
- `KERNEL-POLICY-004` requires WO, human review, SHA-256 and rights clearance.
- `cid11_validator` and `schema_validator` are still unsafe stubs: they must stay in `VALIDATOR_HOLDS` until implemented and independently tested.
- WHO license and permissions must be checked for the intended operation, release and distribution method. The parser does not authorize reuse.
- Do not claim that one parsed JSON-LD entity completes the ICD-11 catalog, WHO edition, or Brazil-specific coding system.

## Test traceability
`tests/test_icd11_mms_parser.py` includes positive metadata subset, integrity, release mismatch, malicious source/URLs, invalid JSON, duplicated keys, publication spoofing, and rights omission. `tests/test_icd11_policy_failclosed.py` binds policy/source/parser and tests Kernel HOLD. Mandatory repository CI remains strict FAIL while other contract parsers are missing.
