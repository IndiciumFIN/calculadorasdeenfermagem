# CE — AG-NR-01: Guardião determinístico anti-retrabalho

**Tipo:** `GUARDIAN / VALIDATION` (contrato P3 existente, sem política paralela). **Implementação:** `ce_pmo_no_rework_agent_v01.py`; integração com `ce_pmo_inventory_guard_v01.py`; testes `test_ce_pmo_no_rework_agent_v01.py` e `test_ce_pmo_inventory_guard_v01.py`.

## Objetivo e posição obrigatória

Antes de atribuir ou executar uma tarefa, confrontar a intenção, o escopo, a versão e o resultado anterior com um ledger de execução. A tarefa **não pode ser recriada com outro ID para contornar um trabalho já executado**. O primeiro registro deve continuar rastreável e ser reutilizado para evidência, auditoria e eventual revalidação.

## Regras

1. Identidade composta de projeto, domínio, operação, intenção, escopo, snapshot, política, validador, schema, destino, parâmetros, saídas, fontes, jurisdição, idioma, licença e cutoff. `semantic_intent_key` usa essas dimensões e **não** o `task_id`. A assinatura de trabalho prevista em P3 (incluindo `task_id`) permanece para vincular tentativas; são propósitos distintos.
2. Match exato já executado: `BLOCK_ALREADY_EXECUTED_REUSE_EVIDENCE`; executado não homologado exige **revalidar, não reexecutar**. Match exato em andamento: `BLOCK_CONCURRENT_EXECUTION`.
3. Mesmo ID com payload diferente, ou mesma família com cutoff diferente: `HOLD_VERSION_OR_CUTOFF_VARIANT`, sem deduplicação ou aprovação automática.
4. Histórico ausente, evidência de execução incompleta, fontes não reconhecidas, ledger vazio/ambíguo ou execução produtiva sem Kernel: BLOCK/HOLD. A população histórica **ainda não foi inteiramente conciliada**: `HOLD_HISTORICAL_COVERAGE_INCOMPLETE` para tarefas aparentemente novas.
5. `ALLOW_PREFLIGHT_ONLY` só é possível em simulação de histórico integralmente reconciliado, escopo documental novo e justificativa explícita. **Nunca representa WO admitida, permissão de produção nem homologação.**

## Contrato de integração

Exemplo de execução local, read-only:

```bash
python ce_pmo_no_rework_agent_v01.py --candidate CANDIDATE_TASK.json --ledger CE_PMO_LEDGER_ANTI_RETRABALHO_20261019_CANDIDATE.json --master CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json
```

`exit 0` = candidato novo elegível **somente ao próximo preflight documental**; `exit 2` = BLOCK/HOLD. O guardião principal aceita `--candidate-task` e `--history-ledger` junto com `--pmo` para a mesma decisão. Quando candidato é informado sem ledger, ou ledger sem candidato, bloqueia.

## Lacunas explícitas (FIND)

- Ledger inicial contém somente três execuções P1 recuperadas (`P1-A`, `P1-B`, `P1-C-C`), todas `EXECUTED_AWAITING_VALIDATION`, não aprovações de conteúdo. As 38 CE04, 76 WOs PR2, 102 históricas e outros microlotes precisam de importação independente antes de se declarar cobertura integral.
- Não há transação atômica de reserva/lease de tarefas, assinatura de ledger, CAS de snapshot no Kernel nem prova de CI obrigatória. Um agente que ignore o CLI não será parado pelo servidor; ruleset GitHub `25297030` está desabilitado no readback anterior. **Não anunciar bloqueio universal ainda.**
- Persistir identidade e `work_signature`, registro FIND/CAPA, WO, Kernel admission ID, commit, recibo remoto e auditoria por tentativa; registrar atualização de fonte como revalidação, nunca reextração automática.

**Critério de aceite para enforcement fim a fim:** histórico reconciliado, gate obrigatório em todos os caminhos de atribuição/admissão, Kernel transacional e CI/ruleset com testes adversariais remotos bloqueados e readback independente. Até lá: `AG-NR-01=LOCAL_FAIL_CLOSED_VALIDATED / SERVER_ENFORCEMENT_HOLD`.
