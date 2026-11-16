# CDC CVX flat file — source-bound candidate parser

Status: **HOLD_HUMAN / NO CLINICAL OR EDITORIAL PUBLICATION**  
Parser: `packages/cli/parsers/vacinas.py` / version 1.0.0  
Contract: `contracts/fontes/vacinas_cdc.json` / policy `KERNEL-POLICY-007@1.1.0`

## Official primary references (retrieved 2026-11-14)
- CDC IIS Vaccine Data Code Sets (release publication listed **2026-09-18**): https://www.cdc.gov/iis/code-sets/index.html
- CDC CVX administered-vaccine code table (US jurisdiction and historical status meanings): https://www2.cdc.gov/vaccines/iis/iisstandards/vaccines.asp?rpt=cvx
- Flat file: https://www2.cdc.gov/vaccines/iis/iisstandards/downloads/CVX.txt
- CDC notes CVX is for HL7 reporting and statuses include Active, Inactive, Pending, Non-US, Never Active. The administrative status is **not** clinical authorization in Brazil.

## Input contract
A local, previously downloaded immutable CDC CVX.txt **snapshot** supplied as bytes or UTF-8 text. No parser network requests. The caller must provide `source_id`, `document_id`, declared `release_date` (`YYYY-MM-DD`), and a trusted-manifest `expected_sha256`. Hash is verified against the complete raw bytes, including optional UTF-8 BOM. Manifest origin, publisher signature and rights are **not proved merely by checksum match**.

The CDC downloadable flat-file record has seven pipe-separated fields, without header:
1. CVX code (leading zeros preserved)
2. Short description (validated but **not exported**)
3. Full description (validated but **not exported**)
4. Notes (validated but **not exported**)
5. US vaccine status
6. Nonvaccine flag
7. Update date (`YYYY/MM/DD`)

Malformed or mixed batches are rejected atomically, including duplicate codes, unsafe bytes, invalid field counts, unknown statuses and dates later than the declared release. The parser outputs only candidate code, US status, nonvaccine marker, ISO update date, source/document IDs and digests.

## Mandatory HOLD
- `publication_allowed=false`, `clinical_approved=false`, `release_allowed=false` for every output row.
- Policy requires SHA-256, a WO, human review and rights review; stub `cvx_validator` and `schema_validator` remain in Kernel HOLD.
- No patient information or vaccination recommendations are processed.
- CDC status `Active` does not mean appropriate, available, or licensed for Brazilian clinical use.
- The code set may include historic records or non-vaccine items. Do not convert metadata into clinical advice.
- Content rights and attribution must be reviewed before reusing human-readable descriptions, notes or tables; none are exported here.
- Source snapshot may not match CDC's newest published release; pin the actual date and SHA for each run.

## Tests and gate
- `tests/test_cvx_flat_file_parser.py`: positive, negative, corrupt, hashes, dates, duplicate codes, BOM, confidentiality.
- `tests/test_cvx_policy_failclosed.py`: policy, contracts, stub holds.
- Repository strict gate must still fail while **other source parsers remain absent**. A successfully parsed CVX file is never automatically a released clinical claim.
