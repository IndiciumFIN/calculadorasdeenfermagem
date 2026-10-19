# FIND — cadeia PMO / Git / guardião não é enforcement fim a fim

**Cutoff:** 2026-10-19. **Gravidade:** CRÍTICA para garantia operacional; não implica mutação ou incidente confirmado.

## Evidência observada

- GitHub REST `GET /repos/IndiciumFIN/calculadorasdeenfermagem/rulesets/25297030`: ruleset `Protecao`, `enforcement=disabled`, `conditions.ref_name.include=[]`, `required_status_checks=[]`.
- `GET /repos/IndiciumFIN/calculadorasdeenfermagem/branches/main/protection`: HTTP 403, integração sem acesso de leitura a esse endpoint. A ausência de acesso **não** comprova proteção efetiva.
- Guardião local `ce_pmo_inventory_guard_v01.py` é preflight por invocação, não GitHub Action obrigatória nem Kernel authoritative admission. Originalmente aceitava lista `gates=[]` porque não verificava cardinalidade dos oito gates. Corrigido localmente; testes negativos adicionados.
- Os três artefatos da fila documental e PMO (registro, fila, recibo) tiveram leitura de retorno exata via GitHub neste ciclo anterior; isso prova publicação documental, **não** proteção da branch contra writes não conformes.

## Ação corretiva candidata

1. `GUARD-01`: bloquear ausência, duplicidade ou PASS indevido em gates; confrontar mestre x fila x fontes; testes adversariais. **Implementação local feita, 21/21 PASS; publicação ainda depende de readback.**
2. `GUARD-02`: definir verificação independente obrigatória do plano de publicação (paths, hashes, CAS, segredo, readback) e falhar fechado se não executada. **Pendente implementação de mecanismo remoto.**
3. `GUARD-03`: sob FIND→política→validador→tarefa→WO→admissão Kernel, instalar/verificar CI e ruleset realmente ativos e bloqueantes, com checks requeridos e testes negativos remotos; requer autorização operacional separada. **HOLD.**
4. `GUARD-04`: auditar separação PMO controller / publisher / auditor, refetch de HEAD e correspondência exata por commit, além do recibo externo apend-only. **Procedimento documentado, enforcement remoto não comprovado.**

## Critério de aceite

Evidência direta de ruleset/CI ativo e escopado, checks obrigatórios, tentativas adversariais de write bloqueadas por controle servidor, políticas e validadores versionados, Kernel autoritativo e auditoria independente. Até lá: `GUARDIAN_SERVER_ENFORCEMENT=NOT_PROVEN`, `G-PMO-05/06=HOLD`, `project_execution_allowed=false`.

**Preservação:** nenhuma edição de ruleset, CI produtiva, Kernel, main ou conteúdo foi autorizada/realizada nesta análise.
