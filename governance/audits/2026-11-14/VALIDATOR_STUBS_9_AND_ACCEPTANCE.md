# CKO / NCOS — auditoria dos nove validadores com implementação incondicional

**Data de corte:** 2026-11-14  
**Escopo:** candidata `integration/cko-parsers-catalog-20261114`, derivada de PR #60 e #61.  
**Decisão:** `HOLD_VALIDATOR` / `HOLD_HUMAN`. Este documento **não aprova** fontes, licenças, conteúdos, tabelas ou publicação.

## Evidência direta de código (Git blob SHA-1)

Os nove módulos abaixo apresentam `validate(...): return True, None`, e `test_suite()` mistura casos esperados como falsos que o método atual aprova. A presença do módulo ou a compilação não comprova validação. Em todos os casos, a implementação efetiva precisa ter testes negativos e contraprovas baseadas no contrato de fonte.

| Prioridade | Validador | Git blob auditado | Critério de aceite — obrigatório |
|---|---|---|---|
| P0 | `human_review_validator.py` | `a49707cc254183a89cf706551d3e7ebf1ac6ff4a` | Verificar recibo de revisor habilitado, independente, ligado a claim/documento/versão/blob, escopo de aprovação e direitos; negar autodeclaração, revogação ou alterações após assinatura |
| P0 | `schema_validator.py` | `bb592d99017ee524e6952ea407501f1223edac1f` | Resolver schema versionado por ID de contrato confiável; validar campos/tipos/limites; rejeitar schema ausente, inválido, trocado ou não permitido |
| P1 | `mesh_validator.py` | `a9367a05bb398fbebcfb4693a5af1f285b2f21ef` | Conferir identificadores e relações contra versão íntegra e autorizada dos descritores NLM MeSH; rejeitar estruturas e referências órfãs; preservar direitos |
| P1 | `loinc_validator.py` | `7d68b901d6975bbfaa85b13d309e06bb1b20d3c2` | Validar forma, existência e versão de código LOINC em referência versionada e permitida; rejeitar códigos fabricados/inativos ou sem catálogo autorizado |
| P1 | `cvx_validator.py` | `33c8f02c7add19eacc1b7e79909666170b4a6d8a` | Confrontar identificador CVX com catálogo oficial CDC e estado na versão de referência; rejeitar rótulos e códigos inventados |
| P1 | `cid10_validator.py` | `ec4cddacc9420be9e86e21347f17b20c7dbb4746` | Confrontar código e subcategoria com edição adotada de CID-10; não confundir verificação sintática com validade clínica |
| P1 | `cid11_validator.py` | `dcc4c26a09aa8d92aa851df7337e3aec60945f56` | Validar URI/identificador e release de CID-11 contra edição OMS aprovada; não reutilizar a regex CID-10 |
| P1 | `catmat_validator.py` | `280ea941eb692cd2e2189a2d04060b408cde9988` | Confirmar código e descrição na versão congelada do catálogo oficial de materiais, com proveniência e validade de uso |
| P1 | `ncm_validator.py` | `6e2da81de2b1447a2563320c368abfec57ec708b` | Verificar NCM no catálogo oficial e sua vigência para classificação de materiais; validação de oito dígitos não basta |

## Contrato uniforme para substituição

1. **FIND:** localizar referência oficial, edição/release, hash, data de obtenção, licença e limitação de uso. Se faltar, `HOLD_SOURCE`.
2. **Política:** ligar o validador a `source_contract`, `policy_id`, versão de schema e campos obrigatórios. Não inferir aprovação pelo título da fonte.
3. **Motor:** implementar verificação determinística; exceções, dependências ausentes, IDs desconhecidos, referências sem versão e dados ambíguos devem falhar fechados.
4. **Testes:** casos positivos oficiais/verificáveis, negativos adversariais, fraude de evidência, referência órfã, versão trocada, payload vazio e replicabilidade.
5. **WO/G6:** segregação executor/revisor, recibo anti-forja e aprovação de direitos e conteúdo por versão/sha.
6. **Integração:** comparar saída com dicionário, metamodelo, grafo e contratos; sem publicação e sem registrar sucesso para `return True` incondicional.
7. **Aceitação:** requer PASS local + CI combinado + revisão independente + ausência de regressão no Kernel; só então atualizar o inventário.

**Importante:** `sha256_validator.py` não integra este conjunto de nove; possui lógica de verificação de formato de digest, porém checagem de **formato hexadecimal não prova integridade do conteúdo subjacente**. A decisão de integridade exige cálculo do hash sobre bytes canônicos da entrada.

## Evidência de CI

- PR #60: CI estrito e pipeline determinístico PASS; `canonical-invariants` FAIL por parsers ausentes.
- PR #61: [Actions #43602399673](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43602399673), `Combined parser, catalog, Kernel tests` PASS; `Strict canonical admission` FAIL intencional, 13 `MISSING_PARSER`, 0 erros estruturais.
- Resultado não é liberação; 46 claims M08/M09 permanecem `HOLD_HUMAN` até revisão independente.

## Próximo lote de implementação

Priorizar `human_review_validator` e `schema_validator` sob especificação e evidência de fonte/autoridade formal; em paralelo, construir fixtures verificáveis por terminologia e versão para os sete restantes. Nenhum stub deve ser substituído por validação só de regex e anunciado como completo.
