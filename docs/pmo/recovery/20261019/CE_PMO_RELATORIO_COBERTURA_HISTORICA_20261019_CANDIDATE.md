# CE PMO — Recuperação de evidências CE-01 a CE-06 e execuções anteriores

**Cutoff:** 2026-10-19. **Objetivo:** alimentar o `AG-NR-01` com evidências históricas para impedir retrabalho, sem converter artefatos encontrados em alegações de execução concluída.

## Universo efetivamente inspecionado neste microlote

| Fonte | Quantidade | Procedimento | Estado de aceite |
|---|---:|---|---|
| `CE_MASTER_CONTINUITY_20261018(1).zip` | **350 membros** | Abertura em memória, triagem de paths, SHA256 do conteúdo de cada membro, locator privado representado por hash | Evidência histórica localizada, não aprovação de tarefa |
| Rodadas `CE_Rxx` dentro do ZIP | **62 identificadores de rodada**, R06–R72 | Classificação por localização de membro; lacunas de números de rodada preservadas | Rodada documentada, não assinatura de conclusão |
| Relatórios locais `CE_Mxx*.md` | **54 artefatos**, **37 marcos** distintos | SHA256 de bytes locais e identidade de relatório | Candidato documental, não execução homologada |
| Continuidade anterior | **347 arquivos preservados** (declaração de handoff) | Confronto contextual; denominador diferente dos 350 membros atuais | Não assumir identidade automática entre populações |

O índice detalhado está em `CE_PMO_INDICE_EVIDENCIAS_HISTORICAS_CE01_CE06_M_20261019_CANDIDATE.json`. Sua origem é reproduzível por `ce_pmo_history_census_v01.py`. Identificadores de membros ZIP são hashes, não paths privados expostos.

## Revisão por frente

| Frente | Recuperado | Não concluir sem prova nova |
|---|---|---|
| CE-01 Git/migração | 15 árvores branch, 9.569 blobs únicos; snapshots históricos; 22 propostas de remoção | Todas as decisões canônicas fechadas, merge autorizado |
| CE-02 fontes/normativos | Evidência de 1.020 registros estruturais e dezenas de rodadas R; 20 amostras normativas de um ciclo | Avaliação clínica, documental, licença ou semântica a 100% |
| CE-03 Supabase/Kernel | 303 outbox e 61 relações históricas em handoffs; nenhum SQL executado no ciclo GAPS6 | Estado vivo do banco, WO admitida, alteração produtiva |
| CE-04 conciliação | 65 metadados classificados (59 caminhos exatos, seis fragmentados em 14 partes); 38 tarefas no registro histórico | Conclusão das 38; naquele readback **0 encerradas**, com 35 pendentes Kernel, duas aguardando preflight e uma HOLD |
| CE-05 CI/segurança | Evidence report e ruleset `25297030`, confirmado desabilitado | Bloqueio obrigatório remoto, proteção atual da `main` |
| CE-06 auditoria | 14/14 testes locais específicos do ciclo e parecer histórico | Auditoria integral, CI, Kernel e publicação liberados |

## Como o AG-NR-01 passa a usar isso

- **Mesmo trabalho executado e comprovado:** bloqueia repetição e remete ao resultado original. Seed inicial P1-A/P1-B/P1-C-C.
- **Arquivo documental histórico com nome de destino correspondente:** `HOLD_PRIOR_DOCUMENTARY_EVIDENCE_REVIEW`, não `ALREADY_EXECUTED`.
- **Frente CE documentada em archive indexado:** `HOLD_PRIOR_FRONT_EVIDENCE_REVIEW` quando o candidato ainda não tem identidade de execução reconciliada.
- **Fonte/escopo não representado ou index indisponível:** `HOLD_HISTORICAL_COVERAGE_INCOMPLETE` ou `HOLD_HISTORICAL_INDEX_NOT_LOADED`.
- **Tarefa CE04 aberta historicamente:** não marcar como executada; consultar e relacionar a tarefa/WO existente e as evidências por resultado antes de criar outra.

## Pendências de fechamento do inventário de execuções

1. Importar e confrontar por ID/intent os registros individuais das 38 tarefas CE04, 76 WOs PR2, 102 WOs de outra população, e todos os recibos Git; preservar identidade documental distinta.
2. Verificar evidências de execução dos M01–M43, inclusive marcos sem arquivo `CE_Mxx` no root (não presumir ausência de trabalho).
3. Confrontar os 13 ZIPs/1.956 membros da cadeia de aquisição, outras branches, PRs, registros locais e recibos, sem duplicar o censo P1.
4. Determinar por trabalho `FIND → política → validador → tarefa → WO → Kernel → teste → auditoria → commit/readback`, diferenciando `DOCUMENTED_ONLY`, `EXECUTED_AWAITING_VALIDATION`, `AUDITED_COMPLETE` e `HOLD`.
5. Integrar o gate de forma obrigatória no GitHub e no Kernel mediante autoridade válida. Atualmente o CLI é fail-closed, mas opcional para quem não o invoca.

**Conclusão:** ampliou-se materialmente a cobertura de evidências; **histórico de execuções ainda não é integral nem reconciliado**. Não atualizar `historical_coverage` para `HISTORY_RECONCILED`; não elevar P1, gates PMO ou percentual global com base apenas neste índice.
