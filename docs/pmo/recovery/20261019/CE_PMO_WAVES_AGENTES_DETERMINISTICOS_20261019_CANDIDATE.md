# CE — PMO: waves, especialistas determinísticos e testes de saída

**Corte:** 2026-10-19. **Estado:** `CANDIDATE / PMO_TRUSTED=false / STOP_WORK_OPERATIONAL`.

## Estimativa controlada

O PMO pode alcançar elegibilidade de auditoria em **6 waves principais**, com contingência de **até 2 waves adicionais** para exceções de escopo. Esta não é previsão de prazo fixo. A conclusão operacional do projeto só terá número definitivo de waves após o fechamento do universo documental e do PMO; estimativa conservadora **8–12 waves adicionais**, condicionadas a Kernel funcional, qualificação clínica/direitos, 7 grandes, M24, CI/E2E e auditoria.

| Wave | Objetivo | Trabalho concorrente sem mutação remota | Gate de saída determinístico |
| --- | --- | --- | --- |
| P0 — Custódia | Congelar HEADs, fontes, backups e exceção documental; salvar M40–M43 elegíveis | inventariante + custodiante | bytes, SHA-256, destinos e readbacks individuais; nenhuma perda ou exposição de dados privados |
| P1 — Universo | Classificar todo o workspace e árvores Git/Library/snapshots, além dos 145 arquivos já inventariados parcialmente | inventariante + especialista Git | toda população tem denominação, total, escopo/cutoff, itens ausentes e limites; nenhum compare truncado tratado como total |
| P2 — Identidade e história | Reconciliar 14 branches, quatro PRs, cinco snapshots, caminhos divergentes e versões | especialista Git + proveniência | identidade por path+Git blob+SHA, variantes preservadas, 22 exclusões/7+3 divergências/2 overlaps não confundidos |
| P3 — Governança e tarefas | Associar 38 tarefas, 76 WOs PR2 e 102 WOs históricas, FINDs, CAPAs, decisões e contratos | tarefas/WOs + especialista normativo | nenhuma população misturada, nem recorrência duplicada, nem WO considerada admitida sem evidência |
| P4 — Validação e riscos | Executar QA adversarial do PMO, segurança e direitos, com checker segregado | especialista de testes + auditor independente | testes de falhas comuns e casos negativos; zero PASS falso, zero missing desconhecido, M24 5 sob HOLD |
| P5 — Fechamento PMO | Consolidar PMO, publicar em branch isolada, verificar commit/bytes/restore e parecer independente | orquestrador único + auditor independente | G-PMO-01..08 comprovados ou HOLD explícito, release do PMO elegível sem liberar o projeto operacional |

## Papéis e limites de autoridade

1. **Inventário/Custódia:** varredura recursiva de arquivos, ZIPs e versões; saída `path, size, sha256, origin, storage, evidence, cutoff` ordenada e imutável.
2. **Git/Reconciliação:** refs, trees completas, PRs e classes `IDENTICAL / DIVERGENT / UNIQUE / CONFLICT_HOLD` com SHA verificável.
3. **Tarefas/FIND/Contratos:** chaves `namespace + original_id + version`, alias, parentesco de recorrência, validador e decision trail sem encerramento artificial.
4. **Conteúdo/Normativos:** conciliar 65 CE04, 1.020 metadados, direitos e ressalvas; nunca reexecutar extração enquanto PMO não confiável.
5. **QA/Auditoria independente:** rejeitar hash falsificado, estado incorreto, tarefa órfã, duplicação semântica, população misturada, M24 contada, readback divergente, segredo/publicação sensível e autocertificação.

**Orquestração:** somente o agente principal faz commits de PMO, serializados em microlotes. Os especialistas apenas leem e emitem candidatos; resultados são importados pelo reconciliador com validações determinísticas e prova de origem. Não confundir agente especializado de análise com executor determinístico: determinismo reside nos schemas, hashes, políticas, regras de ordenação e testes reproduzíveis.

## Achados da auditoria de planejamento — correções obrigatórias

- PMO-REV-001: 145 arquivos são **escopo selecionado**, não inventário completo. Há top-level excluído e diretórios internos; inventariar sem apagar os originais.
- PMO-REV-002: confirmação de persistência do ZIP no script não pode ser inferida do nome; requer readback externo.
- PMO-REV-003: `NO_REMOTE_MUTATIONS` conflita com a exceção documental de 19/10; estabelecer `NO_REMOTE_MUTATIONS_EXCEPT_PMO_DOCUMENTARY_BRANCH`.
- PMO-REV-004: a dispensa temporária de Kernel é apenas para a custódia PMO, não para o projeto ou produção; gate PMO próprio por escopo.
- PMO-REV-005: recibos da versão corrente devem ser externos/append-only; um registro não certifica o próprio conteúdo mutável.
- PMO-REV-006: gerador de inventário atual sobrescreve o relatório local; versionar saídas com atomicidade/checkpoint para uso em produção documental.
- PMO-REV-007: a fonte histórica de 102 WOs é evidência conversacional; localizar arquivo autoritativo antes de reconciliar.

## Condição de retorno às outras frentes

`PMO_TRUSTED=true` exige inventário fechado por população, evidências verificáveis, ledger FIND/CAPA sem duplicação, teste adversarial, auditoria independente, readback GitHub e prova de restauração do registro. Até lá, apenas preservação documental PMO na branch isolada, sem remoções. O aceite de negócio do projeto permanece reservado ao final.
