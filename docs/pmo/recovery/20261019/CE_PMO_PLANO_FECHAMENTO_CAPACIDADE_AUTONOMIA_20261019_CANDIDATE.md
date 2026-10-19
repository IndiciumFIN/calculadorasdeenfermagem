# CE — Plano de fechamento por capacidade, dependência e autoridade

**Corte:** 2026-10-19. **Estado:** CANDIDATE / NÃO HOMOLOGADO. **Repositório:** `IndiciumFIN/calculadorasdeenfermagem`, branch documental `pmo/recovery-controlled-20261019`. **Controle:** PMO-PLAN-AUTONOMY-015.

## Decisão operacional

O objetivo é concluir **100% da parcela tecnicamente executável pelo assistente dentro das permissões existentes**, preservando toda evidência, sem confundir conclusão documental, conclusão técnica e homologação. A aprovação final do Leivis ocorrerá **ao término**, não por tarefa. Não há autorização para publicar em `main`, ativar o Kernel, aprovar direitos ou declarar validade clínica.

A unidade de medição é **entrega verificável com critério de aceite e recibo**, e não número de conversas, arquivos ou porcentagem inferida. O denominador global do projeto **continua não reconciliado**. Uma tarefa pode encerrar um escopo delimitado e manter exceções identificadas; a exceção segue para o fim da fila ou gate final conforme a invariante `INV-QUEUE-POST-CLOSURE-001`.

## Retrato comprovado — não equivale à conclusão integral

| Evidência delimitada | Medida | Leitura correta |
| --- | ---: | --- |
| Fila ordenada P1–P5 | 12 tarefas (11 originais + POST-001) | Nenhuma deve ser marcada integralmente `DONE` por inferência |
| Fechamentos delimitados | 2 `CLOSED`, 3 candidatos | Cinco subescopos, não cinco frentes concluídas |
| Árvores Git imutavelmente enumeradas | 15/15 | Enumeração, não conciliação de versões/conflitos |
| ZIPs com CRC verificado | 13 ZIPs / 1.956 membros | Integridade CRC delimitada, não cadeia de custódia universal |
| CE04 estrutural (marco posterior ao ZIP-base) | 53/65 | Não é percentual do projeto nem validação clínica |
| Fontes CE04 | 61 objetos / 49 URLs distintas | Inventário, não licenças aprovadas |
| Contratos WO PR2 | 164 JSON | Inventário, não admissão produtiva do Kernel |
| Validador independente local | 25 PASS / 3 HOLD | Testes executados, mas segregação/escopos históricos continuam pendentes |
| Gates de homologação PMO | 0/8 PASS, 8 HOLD | Homologação não liberada |

## Matriz de execução e responsabilidade

| Frente / fila | O que consigo executar e provar sem nova aprovação | Limite que não devo ultrapassar sozinho | Critério de aceite delimitado |
| --- | --- | --- | --- |
| P1-CD-01 | Classificar 1.295 conteúdos ZIP distintos contra 15 árvores Git fixadas; emitir correspondência SHA, aliases, versões, sem-presença-em-tip e exceções por objeto | Ausência de blob no *tip* não é perda; não inventar transformação, origem ou custódia | Matriz rastreável + contagens reproduzíveis + exceções explícitas |
| P1-D-01 e POST-001 | Separar cutoffs 768 / 771 / 823, inspecionar metadados e identificar quais diferenças são demonstráveis; documentar ausência do manifesto original de 768 | Não afirmar delta exato nem reconstrução sem os bytes/manifesto da época | Registro de cutoffs por evidência, FIND, causa, reparo, saldo irresolúvel |
| P2-00 / P2-01 | Conferir HEAD/base/ancestralidade/PRs; estudar 22 deleções propostas e sobreposições PR2/3/4/6 caso a caso, sem descartar arquivos | Merge, deleção, substituição e promoção que afetem fonte única exigem revisão de impacto e autorização específica | Matriz arquivo/branch/versão/ação sugerida e testes de não perda |
| P3-A / P3-B | Conciliar os universos de 38 tarefas CE04, 164 WO PR2 e 102 WO históricas; testar estaticamente 14 stubs M20, contratos, guardas, RBAC e comportamento `exit78` M21 | Não afirmar que agentes executam, que os WOs foram admitidos, que há proteção obrigatória em CI/Kernel | Mapeamento por identidade + testes locais + lacunas de runtime nominadas |
| P4-A / P4-D | Catalogar fontes, URLs, titularidade alegada e versões; montar matriz normativa cláusula–requisito–artefato–prova–responsável para ISO, COSO e demais fontes *efetivamente aplicáveis* | Não presumir acesso integral a normas licenciadas, legitimidade de direitos, aplicabilidade jurídica ou eficácia clínica | Cada requisito rastreado à versão/fonte e lacuna `HOLD`, sem conformidade autodeclarada |
| P4-F / conteúdos | Categorizar 285 achados semânticos, 7 arquivos grandes e estratégia de atomização controlada; aprimorar ingestor/extrator, fixtures, testes e dry-runs isolados | Atomização produtiva das 7 fontes requer cadeia de direitos, esquema/política, WO e admissão autorizada; revisão clínica por profissional habilitado | Matriz fonte→claim→CID→WO→teste→HOLD e artefatos locais reproduzíveis |
| P5-01 | Reexecutar testes e readback de GitHub, blobs, fila, PMO, histórico, ZIP e provas negativas; registrar relatório e desvios | Meu próprio relatório não satisfaz parecer independente segregado nem habilita ruleset | Resultados reproduzíveis, SHA, evidências e lista de HOLD por gate |
| P5-02 / final | Preparar dossiê de release, checklist F0–F11, planos de rollback, matriz de exceções e recomendação condicional | Não homologar por Leivis, promover `main`, aprovar alteração de regras ou declarar E2E/Kernel clínico-seguro sem prova | Pacote para decisão com PASS/HOLD/FAIL, escopo e riscos residuais |

## Natureza exata dos impedimentos

1. **Autonomia imediata:** leitura, reconciliação e correções documentais, ferramentas/testes isolados, publicação versionada somente na branch PMO já autorizada e verificação de SHA. Executar em sequência da fila vigente; não reiniciar escopos `CLOSED`/`CANDIDATE`.
2. **Dependências operacionais ou fontes externas:** evidência original por item da população 768; identidades dos cinco arquivos M24 históricos não recuperáveis até aqui; fontes/licenças/versões oficiais; acesso para testar instalação de CI/Kernel, RBAC, Supabase, E2E e segurança; validador segregado. Uma aprovação genérica do usuário **não fabrica** evidência faltante nem substitui auditor independente.
3. **Autoridade específica de Leivis / proprietários:** definir tolerância a exceções residuais; autorizar alterações de infraestrutura, exclusões/merges que afetem conteúdo, promoções e eventual admissão produtiva; deliberar sobre prioridades se houver mudança material. Tais atos não são presumidos pelo pedido de execução integral.
4. **Pareceres habilitados além de Leivis:** direito de reprodução/licenças e decisões clínicas, segurança/compliance aplicável e auditoria independente quando exigida pelos critérios definidos. Leivis pode nomear/reconhecer responsáveis, mas o assistente não deve emitir essas aprovações em nome deles.
5. **Aprovação final de Leivis:** somente após entregar o dossiê e a revisão integral de pendências; homologação é etapa externa ao fim da fila e permanece `HOLD`.

## Sequenciamento para maximizar execução possível

| Onda | Trabalho concreto | Saída e passagem de controle |
| --- | --- | --- |
| A — estabilização | Preservar closures delimitadas, readback PMO, execução de guards e registro do plano atual | PMO e fila íntegros; nenhum status herdado reaberto |
| B — P1 | P1-CD-01, classificação e tratamento documental de P1-D-01; POST-001 apenas na posição final da fila | Universo de objetos classificado; custódia irreconstruível como exceção formal |
| C — P2 | Encerrar análise de 15 árvores, PRs e 22 conflitos não destrutivos | Decisões recomendadas + dependências de autorização isoladas |
| D — P3 e P4 | Contratos/guards, fontes, direitos, requisitos normativos, 285 achados e sete grandes arquivos em dry-run | Dossiês e testes; produção permanece gateada |
| E — P5 | Auditoria local independente em metodologia, rechecagem F0–F11, segurança, E2E quando houver runtime autorizado | Relatório de aceites delimitados e residual por gate |
| F — fim da fila e homologação | Executar atividades supervenientes **apensadas ao final**, revarrer, colher evidência segregada e submeter pacote | 100% das atividades autonomamente elegíveis **efetivamente aceitas**; exceções técnicas e aprovações remanescentes explícitas |

**Ordem normativa real:** a fila registra P1-CD-01, P1-D-01, P2-00, P2-01, P3-A, P3-B, P4-A, P4-D, P4-F, P5-01, P5-02 e POST-001. A tabela de ondas é uma visão de dependências e especialidades; **não autoriza mover POST-001**, quebrar prioridades nem ultrapassar bloqueios. Trabalhos independentes podem ser investigados em paralelo sem alterar a fila ou consumir aprovação antecipada.

## Definição de 100% do que é executável por mim

Só declarar `AUTONOMOUS_SCOPE_100_PERCENT` quando: (i) cada parcela admissível e verificável da fila tem artefato final, hash e teste de aceite; (ii) os itens impossível/externos estão separados com responsável, requisito de evidência e próximo gatilho; (iii) todos os FINDs supervenientes foram investigados e suas tarefas colocadas **no fim** da fila antes da homologação, com estado transparente; (iv) o guarda, a fila, inventário e PMO permanecem consistentes; (v) leitura remota após publicação corresponde aos hashes locais; e (vi) o relatório final não promove HOLD para PASS sem evidência.

**Situação neste corte:** `NOT_ACHIEVED`. Não existe denominador fechado e auditado da execução autônoma por critério de aceite; por isso **não divulgar percentual artificial**. `pmo_trusted=false`, `project_execution_allowed=false`, 8/8 gates de homologação `HOLD`. O marco M24 está **administrativamente fechado**, porém seus cinco objetos desconhecidos não se tornam conteúdos processados. Direitos, clínica e Kernel seguem nas suas próprias frentes e não são pretexto para reabrir M24.

## Tratamento obrigatório de descobertas tardias

Aplicar `INV-QUEUE-POST-CLOSURE-001`: FIND com evidência → investigação e causa raiz → correção/medida preventiva → **nova atividade apensada na cauda** antes da homologação → teste/recibo. Não reabrir nem bloquear atividades já `CLOSED` ou `CANDIDATE_FOR_CLOSURE` por descoberta retrospectiva; nunca esconder risco material (isolar o risco no escopo correspondente). Revisar sempre a fila e o projeto integral após o último item.

## Referências de verdade única

- `CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json`
- `CE_PMO_FILA_EXECUCAO_P1_P5_20261019_CANDIDATE.json`
- `CE_PMO_FECHAMENTOS_DELIMITADOS_20261019_CANDIDATE.json`
- `CE_PMO_VARREDURA_FINAL_P1_P5_F0_F11_20261019_CANDIDATE.json`
- `CE_PMO_INVARIANTE_FILA_POS_FECHAMENTO_20261019_CANDIDATE.md`

Este documento consolida **um plano de fechamento**, não substitui recibos de execução, gates técnicos ou aprovação final.
