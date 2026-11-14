# CKO — MeSH XML Descriptor Metadata (candidato, não publicação)

**Estado:** `TECHNICAL_CANDIDATE / HOLD_RIGHTS / HOLD_NORMATIVE / HOLD_HUMAN`. WO #41.

## Especificações NLM
- https://www.nlm.nih.gov/mesh/xmlmesh.html — formato Descriptor/Concept/Term e UI persistente
- https://www.nlm.nih.gov/mesh/xml_data_elements.html — elementos oficiais
- https://www.nlm.nih.gov/databases/download/mesh.html — downloads por ano/DTD
- https://www.nlm.nih.gov/databases/download/terms_and_conditions.html — direitos

## Escopo técnico atual
- Parser de `DescriptorRecordSet` XML MeSH, de stream `pathlib.Path` ou XML pequeno em memória.
- Preserva `DescriptorUI`, `DescriptorName`, `DescriptorClass`, IDs de conceitos, árvore e referências `SeeRelatedDescriptor` apenas como candidatos.
- Valida formatos de UI, conceitos, árvore, duplicatas, referência a descritor do mesmo conjunto, proveniência obrigatória, versão anual informada externamente.
- Não gera links `KNOWLEDGE_ATOM` aprovados, nem afirma que produção 2026/2027 foi conferida. `production_year_verified=false`.
- Proteção XXE via defusedxml. Não acessa URL/DTD externo. Limite 1GB para arquivo em streaming, 64MB para entrada em memória.
- Omitimos conteúdo de `ScopeNote`, `Annotation`, `TermList`, sinônimos e definições originais na saída.

## Gates / riscos
- Não reproduzir conteúdo MeSH publicamente sem conferir condições NLM e eventuais licenças de terceiros por operação. A existência de XML disponível para download **não** é autorização geral de publicação.
- `mesh_validator` e `schema_validator` ainda não passam testes negativos: Kernel deve permanecer em HOLD.
- Dataset real, DTD do ano, arquivos de Qualifier/SCR, datas de alteração e validação completa da nomenclatura ainda não homologados. Este parser cobre **somente Descriptors**, não MeSH integral.
- IDs `SeeRelated` podem ser vínculos candidatos apenas; um descriptor sem destino válido rejeita o lote no modo estrito.
- Para promover, exigir WO, direitos, licença, auditoria, testes com amostras oficiais, revisão especializada de terminologias e propagação dos relacionamentos no metamodelo e dicionário canônico.
