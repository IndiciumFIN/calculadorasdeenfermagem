# Compras.gov.br / CATMAT — contrato de ingestão somente de metadados

Estado: **HOLD_SOURCE / HOLD_RIGHTS / HOLD_HUMAN**. Produção ou uso clínico não autorizado.

**Fontes oficiais** consultadas em 14/11/2026:
- Portal de dados abertos: https://www.gov.br/compras/pt-br/cidadao/portal-de-dados-abertos
- Swagger API: https://dadosabertos.compras.gov.br/swagger-ui/index.html
- Endpoint `GET /modulo-material/4_consultarItemMaterial`, catálogo de itens materiais (CATMAT)
- Documentação oficial: https://www.gov.br/compras/pt-br/cidadao/portal-de-dados-abertos/documentacao-interativa-da-api-de-dados-abertos

**Implementação candidata**: `packages/cli/parsers/catmat.py`, `contracts/fontes/catmat.json`, `KERNEL-POLICY-013@1.1.0`.

O parser lê **uma única resposta JSON capturada fora do módulo**. Verifica SHA-256, `source_id`, `document_id`, `captured_at` com fuso horário, número da página e metadados coerentes (`resultado`, `totalRegistros`, `totalPaginas`, `paginasRestantes`). Aceita no máximo 500 registros por página e 5 MB por resposta.

Para cada material, exige `codigoItem`, `codigoGrupo`, `codigoClasse`, `codigoPdm`, `statusItem` booleano e `descricaoItem` não vazia. Produz somente identificadores/estado administrativo candidatos e hashes, sem transportar descrição integral. Rejeita lote completo se aparecer duplicidade, tipo inválido, página inconsistente, valores não finitos, chaves JSON duplicadas, SHA divergente ou bytes inválidos.

**Limites de segurança**: O hash verifica a integridade dos bytes em relação ao valor fornecido, mas não autentica a origem do snapshot nem os direitos. A presença do código no CATMAT não prova adequação clínica, autorização de compra, equivalência entre produtos, disponibilidade, estado no momento atual ou validade em outro catálogo. Campos opcionais e outros módulos não são inferidos.

Cada linha contém `source_origin_verified=false`, `catalog_membership_verified=false`, `rights_verified=false`, `status=HOLD_HUMAN`, `clinical_approved=false`, `publication_allowed=false`, `release_allowed=false`.

A política exige SHA, WO, revisão humana independente e direitos por operação. O `catmat_validator` e `schema_validator` continuam impedidos enquanto seus testes reais não comprovarem operação. Os testes sintéticos validam o subconjunto de forma técnica, mas não substituem corpus oficial pinado.

Referência operacional: `tests/test_catmat_parser.py` e `tests/test_catmat_policy_failclosed.py`.
