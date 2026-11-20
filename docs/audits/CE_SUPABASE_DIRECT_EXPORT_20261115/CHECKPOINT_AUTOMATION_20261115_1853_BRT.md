# CE/CKO/NCOS — checkpoint incremental 2026-11-15 18:53 BRT

## Escopo e fonte física
Projeto único `pgsybzggewhinaniybiy` (Calculadoras-Smart). SQL executado: exclusivamente SELECT sobre `pg_class`, `pg_namespace` e `pg_proc`. Nenhum DDL, DML, migration, seed, merge ou deploy. Neon/SOT/WU-TRIB excluídos.

## Referências e fingerprints
- PR #73 https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/73: OPEN/DRAFT, head `c6db7956e32fdac06e57e106e69b2e814c5497cd` no início desta rodada; base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; 24 commits, 38 arquivos alterados. Mergeable não equivale a aprovação.
- Inventário base `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/` e checkpoint `CHECKPOINT_AUTOMATION_20261115_0553_BRT.md`: reutilizados, não reprocessados integralmente.
- Fingerprints de candidatos já registrados no checkpoint base: SQL `aa736b0d0f1d3487326d77f346e9f710d032346a`, seed `fd0f701c7737d3419dd6088216a3381980b1d046`. HOLD sem implantação.

## WO-CE-20261115-1853 — busca de caminhos indiretos para change_control_state
SELECT catálogo: `cko_governance.change_control_state` (owner postgres, RLS false, 0 triggers de usuário), `controlled_artifacts` (4 triggers), `change_audit_ledger` (2 triggers). Não inferir ausência de proteção por RLS=false sem avaliar grants e exposição.

Busca `pg_proc.prosrc ILIKE '%change_control_state%'` identificou **4 funções com referência textual**:
1. `cko_governance.agent_w3_coord_family_execute_v1(text)`: leitura de estado para oversight; SECURITY INVOKER.
2. `cko_governance.change_request_authorized(text,text,text)`: consulta estado e change_requests; SECURITY DEFINER.
3. `cko_governance.guard_pilot_baseline_promotion()`: consulta `baseline_promotion_guard`; SECURITY DEFINER.
4. `cko_validation.run_capetinha_scan_v1()`: consulta estado de lockdown; SECURITY DEFINER.

Trechos próximos às referências indicam SELECT, não escrita explícita nesses trechos. **Não prova inexistência de escritores indiretos**: SQL dinâmico, chamadas transitivas, aplicações externas e papéis privilegiados continuam não examinados. O estado `baseline_promotion_guard=true` é evidência da rodada anterior, não foi novamente lido aqui.

## Gates e resultados
| Controle | Estado | Próxima ação |
|---|---|---|
| PR #73 head e draft | PASS | manter draft |
| 3 relações e contagem de triggers | PASS_CATALOG | analisar grants/ACL e políticas de acesso |
| 4 funções que mencionam change_control_state | PASS_SEARCH | revisar corpos completos, SQL dinâmico e cadeias de chamadas |
| Escritores efetivos e autorização de mudança de estado | HOLD_SECURITY | mapear roles, ACL, API e chamadas transitivas |
| Equivalência ce_tool_audit versus ledger | HOLD_SEMANTIC | matriz por evento |
| CI e testes negativos RLS | NOT_RUN | executar em ambiente isolado |
| 24 ferramentas clínicas | 0/24 HOMOLOGADAS | HOLD_HUMAN |
| SQL candidato e seed | 0/2 EXECUTADOS | HOLD_HUMAN |
| Merges | 0 | bloqueados |

## Delta com denominadores
- Relações alvo verificadas no catálogo nesta rodada: 3/3.
- Funções com referência textual inspecionadas por contexto: 4/4 resultados da busca; cobertura de escritores indiretos desconhecida.
- Ferramentas homologadas: 0/24. SQL candidatos aplicados: 0/2.
- Percentual global de conclusão: indisponível por falta de denominador de aceitação por camada.

Próxima rodada: privilégios herdados e cadeias de chamada do estado de controle; testes dinâmicos de MIME/streaming; crosswalk de entidades existentes antes de criar qualquer tabela. Sem autorização de produção.
