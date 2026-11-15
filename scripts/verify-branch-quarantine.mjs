#!/usr/bin/env node
/**
 * CE-BRANCH-QUARANTINE-20261115: fail-closed check for operational branch selection.
 * This guard is not an organization-wide GitHub ruleset or a branch-deletion action.
 */
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

export const POLICY_ID = 'CE-BRANCH-QUARANTINE-20261115';
export function normalizeRef(ref) {
  if (typeof ref !== 'string' || !ref.trim()) throw Error('REF_REQUIRED');
  return ref.trim().replace(/^refs\/heads\//, '').replace(/^refs\/remotes\/origin\//, '');
}
export function validateRegistry(registry) {
  if (registry?.policyId !== POLICY_ID || registry?.schemaVersion !== '1.0.0' ||
      registry?.releaseGate !== 'HOLD_HUMAN' || !Array.isArray(registry.entries) ||
      registry.entries.length !== 11) throw Error('QUARANTINE_REGISTRY_INVALID');
  const seen = new Set();
  for (const item of registry.entries) {
    const key = item?.repository + ':' + item?.branch;
    if (seen.has(key) || !/^IndiciumFIN\/[a-zA-Z0-9._-]+$/.test(item.repository) ||
        !/^[a-zA-Z0-9._/-]+$/.test(item.branch) ||
        item.branch === 'main' || !/^[a-f0-9]{40}$/.test(item.observedSha) ||
        item.aheadByAtObservation !== 0 ||
        !['QUARANTINED_PENDING_DELETE','BACKUP_RETAINED'].includes(item.status) ||
        item.historicalReadOnlyAllowed !== true || !Array.isArray(item.prohibit) ||
        !['source','base','merge','deploy','workflow','new-development'].every(x => item.prohibit.includes(x))) {
      throw Error('QUARANTINE_REGISTRY_ENTRY_INVALID:' + key);
    }
    seen.add(key);
  }
  return registry.entries;
}
export function assertRefAllowed(registry, repository, ref, purpose = 'source') {
  const entries = validateRegistry(registry);
  if (typeof repository !== 'string' || !/^IndiciumFIN\/[a-zA-Z0-9._-]+$/.test(repository)) throw Error('REPOSITORY_REQUIRED');
  const branch = normalizeRef(ref);
  if (!['source','base','merge','deploy','workflow','new-development'].includes(purpose)) throw Error('PURPOSE_INVALID');
  const item = entries.find(x => x.repository === repository && x.branch === branch);
  if (item && item.prohibit.includes(purpose)) {
    throw Error('QUARANTINED_BRANCH:' + repository + ':' + branch + ':' + purpose + ':' + item.deletionGate);
  }
  return 'PASS:' + repository + ':' + branch + ':' + purpose;
}
export function assertEventAllowed(registry, env) {
  const repository = env.GITHUB_REPOSITORY;
  const event = env.GITHUB_EVENT_NAME;
  if (!event) throw Error('GITHUB_EVENT_NAME_REQUIRED');
  if (event === 'pull_request' || event === 'pull_request_target') {
    if (!env.GITHUB_HEAD_REF || !env.GITHUB_BASE_REF) throw Error('PR_REFS_REQUIRED');
    assertRefAllowed(registry, repository, env.GITHUB_HEAD_REF, 'source');
    assertRefAllowed(registry, repository, env.GITHUB_BASE_REF, 'base');
  } else if (event === 'push' || event === 'workflow_dispatch') {
    assertRefAllowed(registry, repository, env.GITHUB_REF_NAME, 'workflow');
  } else throw Error('UNSUPPORTED_EVENT:' + event);
  return 'PASS_EVENT:' + event;
}
function main() {
  const registry = JSON.parse(readFileSync(new URL('../registers/governance/branch-quarantine.v1.json', import.meta.url), 'utf8'));
  validateRegistry(registry);
  const args = process.argv.slice(2);
  let result;
  if (args.length === 1 && args[0] === '--check-event') {
    result = assertEventAllowed(registry, process.env);
  } else if (args.length === 6 && args[0] === '--repo' && args[2] === '--ref' && args[4] === '--purpose') {
    result = assertRefAllowed(registry, args[1], args[3], args[5]);
  } else {
    throw Error('USAGE: --check-event | --repo <owner/repo> --ref <branch> --purpose <source|base|merge|deploy|workflow|new-development>');
  }
  console.log(result);
}
if (process.argv[1] && fileURLToPath(import.meta.url) === fileURLToPath(new URL('file://' + process.argv[1]))) {
  try { main(); } catch (e) { console.error('HOLD_BRANCH_QUARANTINE', e.message); process.exitCode = 1; }
}
