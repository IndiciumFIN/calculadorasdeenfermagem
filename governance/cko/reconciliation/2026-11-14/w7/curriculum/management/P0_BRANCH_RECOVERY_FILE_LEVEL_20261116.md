# P0 — recuperação seletiva de branches: inventário de arquivos reais (16/11/2026)

Escopo: EPIC #74, PR #70, branch W7 `review/cko-w7-public-evidence-20261114`. **Somente diagnóstico candidato**. Comparação GitHub `base=W7; head=branch candidata`; a divergência histórica impede cherry-pick ou merge indiscriminado.

## Branches comparadas em 16/11

| Branch candidata | Ahead / behind vs W7 | Diferenças de arquivo retornadas | Evidência específica |
|---|---:|---:|---|
| `fix/canonical-structural-cli-registry-20261114` | +18 / -102 | 45 | remoção de `contracts/fonts/*`, alterações em `packages/cli/kernel/*`, testes de exit codes e fail-closed |
| `integrate/p0-cko-existing-source-parsers-20261114` | +21 / -102 | 67 | três parsers concretos FHIR/MeSH/MedlinePlus e testes; também inclui mudanças estruturais sobrepostas |
| `integration/cko-parsers-catalog-20261114` | +163 / -102 | 175 retornados | alterações em contratos, políticas, parsers e testes; **resultado de compare potencialmente limitado**, não afirmar inventário exaustivo |

URLs: https://github.com/IndiciumFIN/calculadorasdeenfermagem/compare/review/cko-w7-public-evidence-20261114...fix/canonical-structural-cli-registry-20261114 ; https://github.com/IndiciumFIN/calculadorasdeenfermagem/compare/review/cko-w7-public-evidence-20261114...integrate/p0-cko-existing-source-parsers-20261114 ; https://github.com/IndiciumFIN/calculadorasdeenfermagem/compare/review/cko-w7-public-evidence-20261114...integration/cko-parsers-catalog-20261114

## Evidências diretas por arquivo

1. `packages/cli/parsers/fhir.py` (branch `integrate/p0-cko-existing-source-parsers-20261114`, Git blob SHA `64e0aaef0274794b04d8187d9c802e87d42317b1`): parser real com `PARSER_API_VERSION=1.0.0`, contrato `contracts/fontes/fhir_vitais.json`, especificação HL7 FHIR R4, tratamento de Observation/Bundle, validação UCUM/LOINC, limites de entrada e exceção `ParseHold`. Fonte normativa declarada: https://hl7.org/fhir/R4/observation-vitalsigns.html . **Existência de implementação não equivale a aprovação de segurança ou execução validada na W7**.
2. `tests/test_fhir_vitals_parser.py` (mesma branch, blob `4fd8e63950761f806cecccfe3db51037a8a369da`): testes com observações sintéticas, unidade/LOINC, pressão arterial, determinismo, ausência de identificadores privados e HOLD_HUMAN. Inspecionado o conteúdo, **não executado neste ciclo**.
3. `governance/migrations/2026-11-14/legacy-fonts-reconciliation.json` (mesma branch, blob `9085556302394f1e40339a392b13e6b79bc66e78`): manifesta comparação histórica de 20 JSONs legados com `contracts/fontes/` e seus Git blob SHA. O manifesto **declara** igualdade após excluir `source_contract`, mas a presente execução não repetiu a comparação binária completa.
4. A branch `integrate/p0-cko-existing-source-parsers-20261114` também acrescenta `packages/cli/parsers/mesh.py` (180 linhas), `medlineplus.py` (203 linhas), e `fhir.py` (212 linhas) segundo compare; cada implementação exige leitura integral, teste isolado e revisão dos contratos antes de seleção.

## Decisão de reconciliação

- `CANDIDATE_REUSE` para os três parsers, **não** `RESOLVED`: implementar integração seletiva somente após verificar SHA, dependências, testes, fonte, licença, política e inexistência de implementação mais nova na W7.
- `CANDIDATE_LEGACY_CLEANUP` para `contracts/fonts`: não excluir nem renomear automaticamente; reconciliar os 20 pares pelo conteúdo e referências de política, preservando trilha de migração.
- `HOLD_CI_CANONICAL`: a execução https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43944428739 falhou; não converter testes de branch em PASS da W7.
- `HOLD_HUMAN`: revisão de integração, política e segurança; `HOLD_SOURCE`: fontes/versões e compatibilidade de todos os demais parsers; `HOLD_RIGHTS`: licença de cada fonte por operação.

## Próxima ação verificável

Fazer diff **por arquivo** entre a W7 e a branch candidata, testar os três parsers com fixtures sintéticas em checkout isolado, reconciliar contratos/políticas e mapear explicitamente quais dos 16 bloqueios são resolvidos por cada arquivo. Só então propor correção testável, sem merge na main, sem alteração de produção e sem publicação clínica.

## Métricas (não misturar estágios)

- Branches comparadas: **3/3 (100% do lote desta rodada)**.
- Parsers concretos localizados na branch candidata: **3/16 (18,75% dos 16 pendentes)**, **0/16 integrados e validados na W7**.
- Achados canônicos resolvidos na W7: **0/22 (0%)**.
- Baseline do manifesto: **65/65** especialidades inventariadas; **14/65 (21,54%)** com anúncios na amostra; **38/1055 (3,60%)** microaulas candidatas do subconjunto Trabalho/Urgência. Nenhuma dessas métricas comprova homologação curricular ou publicação.
