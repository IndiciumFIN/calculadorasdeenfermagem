# P0 — recuperação candidata de componentes canônicos entre branches (16/11/2026)

EPIC #74, PR #70. Comparação **read-only** da branch `review/cko-w7-public-evidence-20261114` (base SHA `fa7eaa0a8499acebe9fb0be585c97b8f348a702e`) com três branches existentes, via GitHub Compare Commits. Não foi executado cherry-pick nem merge; nenhum componente foi declarado homologado.

| Branch candidata | Git compare (base...head) | Divergência | Evidências concretas | Decisão |
|---|---|---|---|---|
| `fix/canonical-structural-cli-registry-20261114` | https://github.com/IndiciumFIN/calculadorasdeenfermagem/compare/review/cko-w7-public-evidence-20261114...fix/canonical-structural-cli-registry-20261114 | 18 commits ahead / 101 behind | Remove `contracts/fonts/*`; altera `packages/cli/kernel/core.py`, `packages/cli/kernel/cli.py`, `policy_registry.py`, validadores e workflow | **PRIORITY_CANDIDATE** para 1 erro estrutural e 5 imports; HOLD_TEST_AND_REVIEW |
| `integrate/p0-cko-existing-source-parsers-20261114` | https://github.com/IndiciumFIN/calculadorasdeenfermagem/compare/review/cko-w7-public-evidence-20261114...integrate/p0-cko-existing-source-parsers-20261114 | 21 ahead / 101 behind | Adiciona workflows FHIR, MedlinePlus, MeSH, altera três políticas; remove legado `contracts/fonts/*`; manifesto de reconciliação | **CANDIDATE_PARTIAL**; não equivale a 16 parsers resolvidos |
| `integration/cko-parsers-catalog-20261114` | https://github.com/IndiciumFIN/calculadorasdeenfermagem/compare/review/cko-w7-public-evidence-20261114...integration/cko-parsers-catalog-20261114 | 163 ahead / 101 behind | Altera 15 contratos `contracts/fontes/*`, adiciona workflows de catálogo e integrações; remove legado | **HOLD_SCOPE_RISK**: branch ampla, não portar sem revisão por arquivo |

## Interpretação e prevenção de duplicidade

- As três branches divergem da mesma base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; mudanças em `contracts/fonts/*` se sobrepõem. **Não somar** arquivos/commits como correções independentes.
- A existência de workflows `cko-fhir-vitals-parser.yml`, `cko-medlineplus-parser.yml` e `cko-mesh-parser.yml` **não comprova** implementação funcional nem cobertura dos 16 parsers. Requer inspeção de módulos reais, fixtures, testes negativos e contratos de fontes.
- As alterações de namespace CLI na branch `fix/canonical-structural-cli-registry-20261114` são a menor candidata aparente para investigação, mas ainda não foram testadas na branch W7 nem comparadas linha a linha; não promover.
- Como a comparação foi contra branch divergente, os valores `ahead/behind` são métricas de Git, não progresso percentual da correção.

## Próximos gates

1. Inspecionar os arquivos reais alterados em `fix/canonical-structural-cli-registry-20261114` e identificar os cinco imports e dependências efetivamente resolvidos.
2. Examinar os módulos parser e testes nas duas branches de integração; exigir cobertura para os 16 itens individualmente, sem stubs.
3. Reconciliar o diretório legado preservando contratos e referências, com testes canônicos de não regressão e evidência de licenciamento/proveniência.
4. Aplicar mudanças apenas após análise de conflito e autorização de escopo, na branch de revisão, nunca na main; manter gates FAIL-closed.

## CI e bloqueios

Commit-base `fa7eaa0a8499acebe9fb0be585c97b8f348a702e`: CKO read-only PASS https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43944428597 ; pipeline PASS https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43944428662 ; CI PASS https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43944428577 ; canonical invariants FAIL https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43944428739 . Este relatório não constitui teste de correção.

`HOLD_CI_CANONICAL` 22 achados anteriores (1 diretório, 16 parsers, 5 imports) **não reclassificados como corrigidos**; `HOLD_SOURCE`, `HOLD_RIGHTS`, `HOLD_HUMAN` permanecem. Denominadores curriculares inalterados: 65 especialidades; 114 programas; 14/65 especialidades representadas por vagas; 38/1055 microaulas candidatas no subconjunto Trabalho/Urgência.
