# DATASUS CID-10 V2008 — categorias CSV, candidato técnico

**Contrato:** `contracts/fontes/cid10.json`.  
**Parser:** `packages/cli/parsers/cid10.py@1.0.0`.  
**Política:** `KERNEL-POLICY-003@1.1.0`.  
**Estado:** `HOLD_SOURCE / HOLD_RIGHTS / HOLD_HUMAN`; nenhuma publicação, inferência clínica ou recomendação.

Fontes:
- Origem oficial DATASUS: http://www2.datasus.gov.br/cid10/V2008/downloads/CID10CSV.zip
- Especificação de tabelas CID-10 versão brasileira: http://www2.datasus.gov.br/cid10/V2008/downloads/descrcsv.htm
- Descrição das categorias e subcategorias: https://ademilsonfp.github.io/br-cid10-csv-docs/index.html
- Ministério da Saúde, documentação oficial: https://bvsms.saude.gov.br/bvs/publicacoes/produtos_servicos_datasus.pdf

## Escopo exato

Somente uma cópia extraída e custodiada de `CID-10-CATEGORIAS.CSV` da distribuição **V2008**, com separador `;` e bytes CP1252; o conjunto completo inclui capítulos, grupos, categorias e subcategorias, mas os outros três não são processados por este módulo. O arquivo de categorias contém cabeçalho `CAT;CLASSIF;DESCRICAO;DESCRABREV;REFER;EXCLUIDOS;`; o delimitador final é parte do formato.

O chamador fornece `source_id`, `document_id`, `edition=V2008`, `table_name` e `expected_sha256` do arquivo extraído. O hash verifica bytes, não a autenticidade DATASUS, a licença nem a validade de um código em uma edição.

O parser exige código de categoria com letra e dois dígitos, sem repetição, e `CLASSIF` vazio/`+`/`*`. Campos descritivos são analisados apenas para presença/tamanho e **não** são reutilizados na saída. São gerados identificadores de categoria candidatos, marcador e hashes de proveniência. O lote inteiro é rejeitado se houver formato desconhecido, campos a mais ou a menos, classificação inválida, duplicidades e dados suspeitos.

## Pendências obrigatórias

- Conferir um snapshot oficial completo e seus 2.045 códigos de categoria; cabeçalho e quoting de releases reais podem exigir ajustes versionados. Testes sintéticos apenas comprovam o subconjunto implementado.
- Implementar a validação de membership/versão para `cid10_validator` e o schema oficial para `schema_validator`; ambos permanecem em `HOLD`.
- Comprovar autorização de direitos de distribuição: a CID-10 e sua tradução portuguesa possuem direitos de OMS/CBCD/Edusp; **não republicar descrições** sem análise jurídica.
- Confrontar origem/edição/hash, dicionário, grafo e relações de capítulos, grupos e subcategorias antes de aceitar uma entidade clínica.
- `KERNEL-POLICY-003` exige SHA-256, WO, revisão humana independente, direitos por operação e `publication_allowed=false`.

Arquivos de teste: `tests/test_cid10_category_parser.py` e `tests/test_cid10_policy_failclosed.py`.
