"use strict";
/** CE safe active-tree removal admission preflight. Candidate; NOT an authoritative Kernel receipt verifier. */
const SHA40 = /^[0-9a-f]{40}$/;
const SHA64 = /^[0-9a-f]{64}$/;
const ID = /^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$/;
function checkRemoval(input) {
  const errors = [];
  const fail = (code) => errors.push(code);
  if (!input || typeof input !== "object" || Array.isArray(input)) return { pass: false, errors: ["INVALID_INPUT"] };
  if (input.operation !== "DELETE_ACTIVE_TREE_FILES") fail("OPERATION_NOT_ALLOWED");
  if (input.deleteBranches || input.rewriteHistory || input.forcePush || input.deleteRefs) fail("HISTORY_BRANCH_OPERATION_DENIED");
  if (input.repository !== "IndiciumFIN/calculadorasdeenfermagem") fail("REPOSITORY_MISMATCH");
  if (typeof input.branch !== "string" || !input.branch.startsWith("feat/") || input.branch.includes("..")) fail("BRANCH_NOT_ISOLATED");
  if (input.branch === "main" || input.branch === "master") fail("DEFAULT_BRANCH_DIRECT_WRITE_DENIED");
  if (!SHA40.test(input.expectedHead || "") || input.expectedHead !== input.observedHead) fail("PINNED_HEAD_MISMATCH");
  if (!ID.test(input.policyId || "") || !SHA64.test(input.policyDigest || "") || input.policyStatus !== "ADMITTED") fail("POLICY_NOT_ADMITTED");
  if (!ID.test(input.woId || "") || !SHA64.test(input.manifestDigest || "") || input.woStatus !== "ADMITTED") fail("WO_NOT_ADMITTED");
  const a = input.kernelReceipt;
  if (!a || a.issuer !== "AUTHORITATIVE_KERNEL" || a.verification !== "VERIFIED_EXTERNALLY" ||
      a.woId !== input.woId || a.policyDigest !== input.policyDigest ||
      a.manifestDigest !== input.manifestDigest || a.branch !== input.branch ||
      a.expectedHead !== input.expectedHead || !ID.test(a.receiptId || "")) fail("KERNEL_RECEIPT_BINDING_INVALID");
  const checks = input.evidence || {};
  for (const k of ["findLinked","causeInvestigated","provenanceComplete","accuracyValidated","completenessValidated","dependencyScanPassed","securityReviewPassed","licenseReviewPassed","independentAuditPassed","rollbackRestoreTestPassed","registerPrepared","dryRunPassed"]) {
    if (checks[k] !== true) fail("EVIDENCE_MISSING_" + k);
  }
  if (!Array.isArray(input.files) || input.files.length === 0 || input.files.length > 100) {
    fail("INVALID_MANIFEST_POPULATION");
  } else {
    const seen = new Set();
    for (const f of input.files) {
      if (!f || typeof f.path !== "string" || f.path.startsWith("/") || f.path.includes("\\") ||
          f.path.split("/").some(x => !x || x === "." || x === "..") ||
          /[\x00-\x1f*?\[\]{}]/.test(f.path) || f.path === ".git" || f.path.startsWith(".git/")) {
        fail("UNSAFE_PATH"); continue;
      }
      if (seen.has(f.path)) fail("DUPLICATE_PATH");
      seen.add(f.path);
      if (!SHA40.test(f.expectedBlob || "") || f.expectedBlob !== f.observedBlob) fail("BLOB_MISMATCH");
      if (f.classification !== "APPROVED_REMOVE" || f.dependencyStatus !== "CLEAR") fail("FILE_NOT_APPROVED");
    }
  }
  return { pass: errors.length === 0, executionAuthorized: false, requiresExternalKernelReceiptVerifier: true, errors: [...new Set(errors)].sort() };
}
module.exports = { checkRemoval };
