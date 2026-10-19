# PMO — P1-C-B: árvores Git completas e percentual de avanço

## Resultado e denominadores

- Listadas e fixadas **15/15 branches** do GitHub, com `head_sha` e `tree_sha`.
- Percorridas integralmente **15/15 árvores** até as entradas de blob no commit fixado. **11/15** couberam em resposta recursiva única; **4/15** exigiram decomposição em subárvores.
- Total de **58.710 ocorrências de blob** nas 15 árvores. **Não são 58.710 arquivos únicos**: várias branches contêm conteúdo e caminhos sobrepostos.
- Falhas residuais de traversal: zero nos lotes finalmente fechados; a API não informou truncamento nas respostas aceitas.
- Artefato auditável: `CE_PMO_GIT_BRANCH_TREES_P1CB_20261019_CANDIDATE.json` com SHA de HEAD e árvore por branch e método de leitura.

## Métricas de progresso não intercambiáveis

| Métrica | Numerador / denominador | Percentual | O que comprova |
|---|---:|---:|---|
| Enumeração das árvores Git das branches observadas | 15 / 15 | **100,0%** | Listagens de entradas para HEADs fixados; não é conciliação de conteúdo |
| Integridade dos ZIPs externos locais | 13 / 13 | **100,0%** | Payload CRC/size, sem certificação documental |
| Subetapas técnicas predefinidas da P1 | 4 / 6 | **66,7%** | Trabalho técnico executado; não é gate P1 aprovado |
| Gates de confiabilidade PMO formalmente homologados | 0 / 8 | **0,0%** | Homologação ainda não concedida |
| Projeto integral CE | denominador ainda não conciliado | **Não mensurável com confiança** | Evitar percentual arbitrário |

**Seis subetapas técnicas P1 usadas como denominador:** (1) enumerar/hash local, (2) leitura CRC ZIP, (3) cruzar SHA local-ZIP, (4) enumerar árvores Git, (5) cruzar todos os blobs Git com as fontes e os membros ZIP, (6) classificar aliases/variantes/conflitos. As quatro primeiras possuem evidências técnicas; as duas últimas ainda não.

## Pendências concretas

1. **P1-C-C**: comparar conteúdo Git por blob SHA com arquivos locais/ZIPs, obtendo conjuntos `EXACT`, `ZIP_ONLY`, `GIT_ONLY`, `DIVERGENT` sem somar ocorrências como arquivos distintos.
2. **P1-C-D**: classificar divergências por caminho, versão, origem, direito e precedência; nenhuma exclusão automática.
3. **P1-D custódia**: manifesto detalhado privado, congelamento de cutoff e readback durável, sem expor nomes dos uploads em GitHub público.
4. **P2**: conflitos históricos, cinco snapshots e quatro PRs ainda exigem decisão rastreável.
5. **P3–P5**: contratos/WO, conteúdos e normativos, testes adversariais independentes, evidências clínicas/jurídicas e fechamento.
6. **M24** continua `HOLD`, a aprovação final é do usuário, e nenhuma ação produtiva foi executada.

## FIND e aprendizado

**PMO-FIND-P1CB-001**: respostas `git/trees?recursive=1` de quatro branches volumosas foram rejeitadas pelo tamanho. Tratar erro como inventário incompleto e percorrer subárvores até confirmação de conclusão. Não interpretar resposta não truncada de uma subárvore como cobertura da árvore inteira.

**PMO-FIND-P1CB-002**: contar blobs somados em branches pode superestimar volume real. É obrigatória apuração de SHA Git único e de chaves de proveniência antes de informar cobertura integral.

**PMO-FIND-P1CB-003**: percentuais precisam ter denominador e objeto explícitos; progresso técnico de P1 não equivale a homologação PMO, e nenhum dos dois equivale a conclusão de CE.

Estado de execução documental: `IN_PROGRESS`. Estado de homologação: `HOLD`. Branch produtiva `main` não modificada por este trabalho.
