# PMO — INV-QUEUE-POST-CLOSURE-001: descoberta após fechamento

## Regra imutável de ordenação

Uma descoberta posterior a `CLOSED_TECHNICAL`, `CLOSED_ADMINISTRATIVE` ou `CANDIDATE_FOR_CLOSURE` **não reabre nem reexecuta** a atividade original. O registrador abre FIND com identidade e proveniência, documenta investigação causal, registra correção proposta/implementada, cria atividade distinta com novo ID e **acrescenta ao final da fila vigente**, antes do gate separado de homologação. Tarefas antigas preservam ordem, evidências e estados; reclassificação só por decisão independente com FIND rastreável. Não inserir nova tarefa no meio, nem antecipar nova tarefa por simples prioridade.

## Contrato mínimo de nova atividade

`id`, `origin_find_id`, `discovered_after_closure`, `prior_closed_reference`, `investigation`, `root_cause`, `correction`, `evidence_required`, `acceptance`, `mode`, `status`, `release_gate`, `enqueue_position`, `execution_order`, `source_refs`, `affected_scope`. O FIND documenta *o que aconteceu, por que aconteceu, causa/controle, correção, teste e aprendizado*. Se uma causa continuar desconhecida, `root_cause=UNDER_INVESTIGATION` e a atividade fica `HOLD_INVESTIGATION`, nunca um PASS inventado.

## Separação de riscos

- Descoberta documental nova: entra na cauda sem bloquear tarefas independentes já elegíveis.
- Falha que afete uma operação específica (segredo, corrupção, permissão, hash, risco clínico): aquela operação é contida pela política existente. Isso **não** suspende a fila geral nem dispensa o registro na cauda.
- Caso a descoberta já esteja em FIND/tarefa de intenção equivalente: referenciar e acrescentar evidência àquela identidade; não gerar duplicidade para alcançar outra posição.
- Execução produtiva continua sujeita a política, validador, tarefa/WO, admissão Kernel, testes e auditoria. Nenhuma classificação administrativa em `CLOSED` promove à main ou concede aprovação clínica/jurídica.

## Aceite determinístico

O guardião rejeita duplicidade de IDs/FINDs, ausência de investigação/correção, alteração da ordem prefixada, estados `EXECUTED` sem evidências e atividades depois do gate final. O último bloco de tarefas é reservado às descobertas, e a homologação permanece como evento **fora da fila**, dependente de todas as atividades e da aprovação final do titular.
