# PMO P1-C-A — Conciliação local × ZIP × GitHub (parcial)

**Decisão:** consolidar equivalências exatas locais/ZIP e iniciar árvore Git. Não declarar universo completo, nem deduplicar destrutivamente.

## Conteúdo endereçado por SHA256

Executado `ce_pmo_local_zip_reconcile_v01.py` sobre a população local existente no momento da leitura, com verificação de integridade ZIP obrigatória. O scanner não extrai arquivos, não lê Drive, não escreve fontes e expõe somente agregado.

| Unidade | Observação | Interpretação correta |
|---|---:|---|
| Arquivos regulares locais no snapshot | 780 | População transitória do workspace; diferente da baseline P1-A de 768 |
| Hashes únicos locais | 732 | Deduplicação por **bytes**, não por autoria ou versão |
| Membros regulares ZIP | 1.956 | Podem repetir conteúdo entre ZIPs |
| Hashes únicos de membros ZIP | 1.295 | Cardinalidade de conteúdo, não de documentos canônicos |
| Hashes comuns local/ZIP | 621 | Equivalência binária comprovada neste escopo |
| Caminhos locais com bytes idênticos em ZIP | 669 | Caminho local preservado; sem exclusão |
| Hashes ZIP sem cópia como arquivo solto local | 674 | **Não** afirmar ausência do GitHub antes de confrontar árvores |
| Hashes locais sem equivalente em ZIP | 111 | Não afirmar ausência remota antes do confronto |
| Conteúdos ZIP em múltiplos contêineres | 333 | Duplicação inter-ZIP por conteúdo, sem autorização para descarte |

Suíte de testes do reconciliador: 4/4 PASS (mesmo conteúdo, conteúdo diferente, vazio e escopo indevido).

## GitHub: preflight parcial com origem congelada

- GitHub REST retornou **15 branches** na página de 100, incluindo a branch documental PMO adicionada após o histórico anterior de 14 branches.
- Baseline de comparação inicial: `main` em `e0f62491b104f4a97c6025a6393cabc2e7ada30e`, árvore raiz `bf5be2752ccdabada2a1dc602a71c9a15338c504`.
- Lidas apenas árvores **não recursivas** de raiz (23 entradas), `docs` (33) e `contracts` (8), todas com `truncated=false` na resposta. Não foram comparados todos os blobs das 15 branches.

## FINDs e aprendizados

| FIND | Achado | Tratamento |
|---|---|---|
| PMO-FIND-P1C-001 | Mesma informação pode existir como arquivo solto e dentro de vários ZIPs. | Usar content SHA como índice auxiliar e preservar cada ocorrência/origem. |
| PMO-FIND-P1C-002 | `ZIP-only` é diferente de `GitHub-missing`. | Não abrir FIND de perda até confronto de árvores/blob completo. |
| PMO-FIND-P1C-003 | População muda com geração de evidências novas. | Congelar snapshot e registrar deltas; P1-A continua histórico de 768. |
| PMO-FIND-P1C-004 | A contagem de branches mudou ao adicionar recuperação PMO. | Versionar cutoff de contagens, jamais substituir observações anteriores sem rótulo. |
| PMO-FIND-P1C-005 | Subárvore Git lida sem recursão não fornece cobertura integral. | Prosseguir por árvores fixadas e verificar truncation/paginação. |

## Pendências bloqueantes da **homologação**, não da consolidação

1. Enumerar 15 árvores Git completas por commit fixado e comparar blob SHA/versão/caminhos sem truncamento.
2. Relacionar membros ZIP e arquivos soltos às variantes Git; separar `EXACT`, `DIVERGENT`, `ARCHIVE_ONLY`, `GIT_ONLY` e `UNKNOWN`.
3. Preservar manifesto detalhado em armazenamento privado aprovado, com controle de acesso e prova de readback.
4. A integridade técnica P1-B não comprova direitos de uso, semântica nem autorização clínica.

**Sem alterações à `main`, à política produtiva, ao Kernel ou ao conteúdo de fontes. M24 permanece HOLD.**
