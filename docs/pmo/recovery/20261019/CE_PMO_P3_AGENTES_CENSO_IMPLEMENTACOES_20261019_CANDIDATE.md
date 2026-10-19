# CE PMO — P3: censo de implementações e reconciliação preliminar de agentes
**Cutoff:** 2026-10-19. **Status:** READ_ONLY_DOCUMENTARY_CANDIDATE / NOT_HOMOLOGATED. **Tarefas:** P3-A e P3-B (ambas permanecem sem fechamento). Sem execução produtiva, edição de código, mudança de política ou reabertura de tarefa anterior.

## Evidência Git conferida
| Fonte | Ref | Git blob SHA | Achado |
|---|---|---|---|
| Registry legado | `cursor/fix-governance-gaps-ec54:agents/registry.json` | `6c94be5e8a319f8999e224c9891ba4bc7571e17c` | v1.2.0: 110 entradas; 2 recertificações declaradas 'vigente', 108 'candidato' |
| Consulta simples de papéis | `cursor/fix-governance-gaps-ec54:packages/cli/agentes.py` | `37ad6654383010a86e4c8d969fe75e8e9160d9d5` | quatro papéis estáticos, consulta de papéis; não é dispatcher persistente |
| Kernel legado | `cursor/fix-governance-gaps-ec54:packages/cli/kernel.py` | `87bb5f2e62bcc6a71e5ed995115921e031705700` | CLI histórica separada; evidência de código, não de admissão produtiva |
| Kernel main | `main:packages/cli/kernel/core.py` | `7649f6e1f0160184e1014308cc05c90a5eb659e9` | implementação diferente; exige teste de import, validators e política |
| Policy registry main | `main:packages/cli/kernel/policy_registry.py` | `041bfaf4151effd05de7cb33a5458a53a2ab04af` | carrega JSONs; não prova que política candidata esteja admitida |
| Teste histórico | `main:docs/AGENT_TEST_STATUS.md` | `0b4cb09c71604a3313dba955554696cac5c64dd5` | teste de agente sem resposta textual no cutoff histórico |
| Catálogo PMO | `pmo/recovery-controlled-20261019:CE_PMO_AGENT_REGISTRY_20261019_CANDIDATE.json` | `6156c083b85c285f9acb438ea385344e71201a07` | 23 IDs PMO, 0 implantações verificadas |
| Matriz de tarefas/WOs | `CE_PMO_CROSSWALK_CE04_38_PR2_WO164_20261019_CANDIDATE.json` | `69d9422dbf585d66b741689f8cdce35c5bccc1bd` | 38 tarefas CE04, 164 JSONs WO PR2, zero correspondências diretas de ID |

## Interpretação controlada
- **110 registros legados, 23 IDs de papéis PMO e 4 papéis da CLI são universos heterogêneos**; não somar como 137 agentes ativos nem fundir automaticamente por semelhança nominal.
- A declaração de recertificação `vigente` em dois registros é dado do artefato, não verificação de conexão, invocabilidade ou recertificação por autoridade atual.
- Há dois caminhos de Kernel com conteúdo diferente. Não substituir, selecionar vencedor ou registrar runtime PROD sem análise de contratos, testes, política/validador, WO e receipt.
- O relato M20 de 14 stubs/M21 exit 78 é **evidência histórica em PMO**, mas os relatórios originais não foram localizados no caminho documental consultado neste microlote. Exigir fonte e readback antes de novo PASS.
- O conjunto de 102 WOs históricas não possui prova de equivalência com as 164 WO do PR2; preservar os denominadores e a identidade histórica separada.
- `WO-CE04-RECON-20261017` na branch de auditoria, blob `19a37c6563ac0e54026c3dd49770438457f03f4c`, mantém `DRAFT_NOT_ADMITTED` e `admission.status=NOT_REQUESTED`.

## Crosswalk inicial de funções (CANDIDATE_LINK, nunca SAME_AS comprovado)
| Papel PMO | Legado relacionado por função | Natureza |
|---|---|---|
| P4-INGESTOR-LINEAGE | AGT-EXTRATOR-001 e `extrator` da CLI | Possível sobreposição de competência; contrato e função diferentes |
| P5-EVIDENCE-AUDITOR / P3-INDEPENDENT-AUDITOR | AGT-AUDITOR-001 e `auditor` da CLI | Possível sobreposição, sem identidade comum |
| P4-ATOMIZER-TRIAGE | `atomizador` da CLI | Possível alias de papel, execução não comprovada |
| PMO-GUARDIAN / AG-NR-01 | regras declaradas no legado | Não declarar equivalência até policy/version/receipt |

## Próximo microlote P3
1. Ler contrato/schema e políticas correspondentes de cada família, sem roteamento entre schemas por semelhança.
2. Indexar os 110 registros do legado por ID, função, modelo, ações, prompt, status e recertificação, com hash e aliases candidatos; sem copiar segredos.
3. Conferir testes e implementação real dos 14 stubs mencionados em M20; classificar `SPEC_ONLY | STUB | LOCAL_TESTED | KERNEL_ADMITTED | DEPLOYED_VERIFIED` exclusivamente com evidência.
4. Emitir crosswalk por identidade, candidato e incompatibilidade, referenciando FINDs anteriores; manter produção em HOLD.
5. Aplicar novos testes positivos/negativos em ambiente isolado quando código e fixtures estiverem disponíveis; relatório e auditoria segregada P5.

**Gates:** P3-A=PARTIAL; P3-B=PARTIAL/NOT_CLOSED; `PMO_TRUSTED=false`, oito gates de homologação HOLD. A fila formal de 12 tarefas permanece intacta, com POST-001 na cauda. Achados adicionais devem vincular-se ao P3, não criar uma 13a tarefa automaticamente ou reexecutar ações encerradas.
