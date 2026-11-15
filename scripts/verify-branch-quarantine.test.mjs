import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {assertRefAllowed, assertEventAllowed, validateRegistry, normalizeRef} from './verify-branch-quarantine.mjs';
const manifest = JSON.parse(readFileSync(new URL('../registers/governance/branch-quarantine.v1.json', import.meta.url), 'utf8'));
test('manifesto completo, 11 referencias e nenhuma duplicata', () => {
  assert.equal(validateRegistry(manifest).length, 11);
  assert.equal(new Set(manifest.entries.map(x => x.repository + ':' + x.branch)).size, 11);
});
test('quarentena bloqueia branch ativa como fonte/base/deploy', () => {
  for (const purpose of ['source','base','merge','deploy','workflow','new-development']) {
    assert.throws(() => assertRefAllowed(manifest,'IndiciumFIN/dev-chatgpt-workspace','integration/structural-overlay-20261101',purpose),/QUARANTINED_BRANCH/);
  }
});
test('backup permanece indisponivel para selecao operacional', () => {
  assert.throws(() => assertRefAllowed(manifest,'IndiciumFIN/calculadorasdeenfermagem-backup-20261031','cursor/wf-v3','source'),/QUARANTINED_BRANCH/);
});
test('main e candidato nao bloqueado continuam elegiveis ao teste; nao recebem GO clinico', () => {
  assert.match(assertRefAllowed(manifest,'IndiciumFIN/calculadorasdeenfermagem','main','base'),/^PASS:/);
  assert.match(assertRefAllowed(manifest,'IndiciumFIN/calculadorasdeenfermagem','review/cko-w7-public-evidence-20261114','source'),/^PASS:/);
});
test('normaliza referencias git corretamente', () => {
  assert.equal(normalizeRef('refs/heads/cursor/wf-v3'),'cursor/wf-v3');
  assert.equal(normalizeRef('refs/remotes/origin/cursor/wf-v3'),'cursor/wf-v3');
});
test('falha fechado para registro adulterado, ref desconhecida ou informacao ausente', () => {
  assert.throws(() => validateRegistry({...manifest,entries: manifest.entries.slice(1)}),/REGISTRY_INVALID/);
  assert.throws(() => assertRefAllowed(manifest,'IndiciumFIN/calculadorasdeenfermagem','', 'source'),/REF_REQUIRED/);
  assert.throws(() => assertEventAllowed(manifest,{GITHUB_EVENT_NAME:'pull_request',GITHUB_REPOSITORY:'IndiciumFIN/calculadorasdeenfermagem'}),/PR_REFS_REQUIRED/);
});
test('workflow bloqueia PR de branch quarentenada', () => {
  assert.throws(() => assertEventAllowed(manifest,{GITHUB_EVENT_NAME:'pull_request',GITHUB_REPOSITORY:'IndiciumFIN/calculadorasdeenfermagem',GITHUB_HEAD_REF:'cursor/wf-v3',GITHUB_BASE_REF:'main'}),/QUARANTINED_BRANCH/);
});
