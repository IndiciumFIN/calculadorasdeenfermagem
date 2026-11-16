# P0 — revisão estática de dois parsers NLM candidatos (MeSH e MedlinePlus)

**Data:** 2026-11-16. **EPIC:** #74. **Branch alvo:** `review/cko-w7-public-evidence-20261114`. **Fonte candidata:** `integrate/p0-cko-existing-source-parsers-20261114`. Somente documentação de triagem; não representa teste executado ou integração.

## Proveniência por arquivo

| Artefato | Git blob SHA verificado via GitHub | Escopo |
|---|---|---|
| `packages/cli/parsers/mesh.py` | `14ad9871227e39a22046588b0f6ea9dea8435a42` | Metadados MeSH DescriptorRecordSet |
| `tests/test_mesh_parser.py` | `5704561d8f26bf7a55956d60301a5a6f99f61249` | Testes sintéticos de ID, links, XML malformado, determinismo, direitos |
| `packages/cli/parsers/medlineplus.py` | `aaff2ee68199184fc6d566b02c6f0388391811af` | Metadados MedlinePlus health-topics XML |
| `tests/test_medlineplus_parser.py` | `0de38d977817407c345a0bb85765a5069a985e1c` | Testes sintéticos de metadados, duplicatas, links, entidades XML, limites |

URLs de revisão: https://github.com/IndiciumFIN/calculadorasdeenfermagem/blob/integrate/p0-cko-existing-source-parsers-20261114/packages/cli/parsers/mesh.py ; https://github.com/IndiciumFIN/calculadorasdeenfermagem/blob/integrate/p0-cko-existing-source-parsers-20261114/packages/cli/parsers/medlineplus.py . Especificações declaradas: https://www.nlm.nih.gov/mesh/xmlmesh.html e https://medlineplus.gov/xmldescription.html .

## Achados novos da leitura do código (não inferir execução)

1. **MeSH:** `production_year` é fornecido pelo chamador e a saída declara explicitamente `production_year_verified=False`. Não usar ano declarado como ano autenticado da edição. `HOLD_SOURCE_VERSION` até associar o arquivo oficial, data, checksum e termos aplicáveis.
2. **MeSH:** `verify_related=False` admite referências externas órfãs em recortes parciais; os IDs continuam marcados `candidate` e `publication_allowed=False`. A opção não autoriza materializar arestas canônicas. Para lote completo, exigir `verify_related=True` e verificar cobertura.
3. **MedlinePlus:** `date_generated` é interpretada do atributo XML, sem autenticação externa da origem ou da edição. Exigir URL da distribuição oficial, hash, data de captura e prova de correspondência. `HOLD_SOURCE_VERSION`.
4. **MedlinePlus:** a validação de `mesh_descriptor_ids_candidate` exige prefixo `D` e sufixo numérico, mas não verifica o comprimento esperado nem existência no vocabulário MeSH da mesma edição. Requer teste de crosswalk versionado antes de qualquer relacionamento; `HOLD_SEMANTIC_LINK`.
5. Ambos extraem metadados sem notas de escopo/sumários e emitem `HOLD_HUMAN`, `clinical_approved=False`, `publication_allowed=False`. Esses controles são observados estaticamente, não prova de segurança integral ou autorização de reprodução.
6. MeSH usa `defusedxml` e limites de tamanho/contagem; MedlinePlus também usa `defusedxml` e limite de payload. A instalação efetiva da dependência, execução dos testes e consumo de memória precisam ser medidos em checkout isolado.

## Critérios para admissão futura

- Repetir fetch por SHA imutável e comparar com W7; não cherry-pick da branch divergente.
- Executar os testes sintéticos de ambos os parsers e testes negativos de XML, crosswalk MeSH por edição, hashes, direitos e privacidade em ambiente isolado.
- Exigir política por operação: **metadados indexáveis não equivalem a licença de redistribuição de textos, descritores ou resumos**.
- Manter `HOLD_CI_CANONICAL`, `HOLD_SOURCE_VERSION`, `HOLD_RIGHTS` e `HOLD_HUMAN` até evidências específicas e revisão; nenhuma promoção clínica.

## Métricas e CI

Do lote de 16 parsers bloqueados, três implementações candidatas foram localizadas (FHIR, MeSH, MedlinePlus): **3/16 = 18,75% em descoberta**, **0/16 integrados e validados**. Esta revisão aprofundou **2/3 candidatos** por leitura de código e testes, sem execução local. **0/22 bloqueios canônicos resolvidos**.

No commit anterior `d5246adf0b9a055541d4250068445ab7d460e2a3`: [CKO read-only audit PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43974668023), [pipeline PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43974667953), [CI PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43974667970), [invariantes canônicos FAIL](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43974667797). Esses runs não validam este documento.

Baseline não alterada: **65/65** especialidades catalogadas (não homologadas), **14/65** com anúncios na amostra (21,54%), **38/1055** microaulas candidatas de Trabalho/Urgência (3,60%).
