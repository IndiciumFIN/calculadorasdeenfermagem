# Matriz de evidências primárias para correção — 19/11/2026

**EPIC #74 / PR #70 — candidato, sem homologação.** Esta matriz separa evidência observada, solução proposta e prova de aceite. Não promove conteúdo clínico.

## A. Taxonomia COFEN — WO-04/05/06

**Fonte primária:** https://www.cofen.gov.br/resolucao-cofen-no-581-2018/ — Resolução COFEN 581/2018, com alterações e decisões oficiais indicadas na própria página (incluindo 263/2023, 264/2023 e 21/2024). **Fato verificado:** anexo diferencia itens principais e subalíneas; Home Care é subárea de Assistência Domiciliária e Hemodinâmica é subárea de Cardiologia. Não inflar denominador nem somar subárea como especialidade independente. O registro versionado `specialties/COFEN_581_SPECIALTIES_65_AND_SUBAREAS_v0.5.0.jsonl` já contém `child_lines` e `source_line_is_subarea_not_independent_headline` para essas subáreas.

**Monitoramento normativo:** https://cofen.gov.br/gt-conclui-proposta-de-revisao-sobre-registro-das-especialidades-de-profissionais-da-enfermagem/ (notícia oficial de 25/09/2026) relata proposta de revisão da 581/2018; **não demonstra promulgação ou vigência de nova resolução**. Ação: registrar `PROPOSAL_NOT_NORMATIVE`, monitorar Diário Oficial/portal COFEN antes de qualquer migração do denominador 65. Aceite: confronto documental de ato publicado, vigência e diff da lista, com revisão humana.

## B. Invariantes canônicos — correções de implementação

**Evidência local primária:** `scripts/verify_repository_integrity.py` (blob `f6e74d988cfbe623e4a5f903b555c314482cbf40`) usa `legacy = root / "contracts/fonts"`, classifica `LEGACY_SOURCE_DIR` como `error`, `MISSING_PARSER` como `pending` e verifica `BROKEN_IMPORT` para imports top-level `kernel` e `validators`. No SHA `f4906d2a`, o workflow https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44461190413 falhou com 1 error + 21 pending; os logs dos jobs 135348089213/135348089482 foram lidos.

**Import observado:** `packages/cli/main.py` (blob `79fe358e7698c0eddf70357fac696daac0abc1e6`) usa `from kernel.core import Kernel, Decision`, `from kernel.policy_registry import ...`, `from validators.registry import ...`. Correção candidata: imports ancorados em `packages.cli.kernel` / `packages.cli.validators`, ajustados em conjunto nos cinco arquivos sinalizados, preservando execução como módulo e testes de regressão. Não afirmar compatibilidade sem executar `python -m packages.cli.main --help` e `python -m unittest discover` no SHA corrigido.

**Fonte legada:** inspecionar `contracts/fonts` e referências antes de mover/excluir; evidência do verificador indica existência, não prova duplicidade nem autoriza deleção. Gate: diff de contratos, links de políticas e testes determinísticos.

## C. Reaproveitamento de parsers reais em branches existentes

Foram lidos diretamente pelo GitHub os três arquivos abaixo; **existência não é aprovação de integração**:

| Contrato | Branch de origem | Arquivo | Blob SHA |
|---|---|---|---|
| FHIR R4 sinais vitais | `feat/cko-parser-fhir-vitals-r4-20261114` | `packages/cli/parsers/fhir.py` | `64e0aaef0274794b04d8187d9c802e87d42317b1` |
| NLM MedlinePlus XML | `feat/cko-parser-medlineplus-xml-20261114` | `packages/cli/parsers/medlineplus.py` | `aaff2ee68199184fc6d566b02c6f0388391811af` |
| NLM MeSH XML | `feat/cko-parser-mesh-xml-20261114` | `packages/cli/parsers/mesh.py` | `14ad9871227e39a22046588b0f6ea9dea8435a42` |

Referências normativas declaradas pelos próprios arquivos: https://hl7.org/fhir/R4/observation-vitalsigns.html ; https://medlineplus.gov/xmldescription.html ; https://www.nlm.nih.gov/mesh/xmlmesh.html . **A leitura não verificou execução dos testes dessas branches nem licenças de redistribuição.**

Próximos gates por parser: revisar código integral e fixtures, contrato, dependências (inclusive `defusedxml`), direitos/atribuição, entradas malformadas e XML adversarial, limites, hashes, idempotência, ausência de PII e saídas sem conteúdo protegido. Só depois propor cherry-pick/integração na W7. Restantes 13 parsers continuam `HOLD_IMPLEMENTATION` por objeto.

## D. WO-05 — mercado, direitos e dados

**Fonte primária de IDs COFEN:** resolução acima. **Fonte primária para cada anúncio:** URL oficial de recrutamento do empregador; exigir ID, empregador, data de observação, cargo, status, requisitos e URL; `NOT_VERIFIED` não equivale a vaga aberta. Chave de dedup: plataforma+empregador+job_id, mais colisões de job_id e URL normalizada. Subáreas não ampliam a contagem de 65. Separar 41 anúncios candidatos/21 especialidades (32,31%) de registros com segunda revisão independente. Não usar amostra não probabilística como estimativa nacional.

**Direitos:** reutilizar URL, identificador, metadados e rótulos de habilidades de autoria própria; não copiar anúncios ou resumos integrais. HOLD_RIGHTS por obra/operação; não inferir licença por acesso público.

## E. Testes e limites desta rodada

**Executado:** leitura dos arquivos reais do GitHub, três parsers em branches, verificador, CLI, contrato FHIR, registro COFEN e logs anteriores; consulta das páginas oficiais COFEN e documentação GitHub Actions. **Não executado:** testes locais, CI novo, verificação de vigência em Diário Oficial, revisão humana COFEN, revisão jurídica/licenças, dedup 41/41, alteração de parser ou imports. **Sem autorização para main, Supabase, produção ou publicação clínica.**

GitHub Actions: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs informa que reruns usam o SHA/ref originais; portanto **reexecutar o workflow antigo não testa um novo commit**. Aceite: novo run associado ao SHA corrigido, com logs e resultados reais.
