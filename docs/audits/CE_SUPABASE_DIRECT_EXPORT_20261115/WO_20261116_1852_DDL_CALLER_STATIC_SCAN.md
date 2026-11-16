# WO 2026-11-16 18:52 — Triagem estática de invocadores do controle DDL

## Origem e escopo
Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; somente SELECT em `pg_proc` e `pg_namespace`, com `pg_get_functiondef`, `has_schema_privilege`. Continuidade verificada do commit `c8f86902ecb3822c9ebe34d53883283044768857`, arquivo `WO_20261116_1751_ADMIN_ROLE_ACL.md` (blob `799ba719cb711d36c7a2ebbc9371b34971969ddb`). Branch `audit/ce-supabase-migration-first-20261115`. Consulta sem alterações de dados.

## Delta físico
Pesquisa textual das definições de funções em `cko_governance` por `change_control_state` OU `destructive_writes_blocked`: 3 funções encontradas: `agent_w3_coord_family_execute_v1(p_agent_id text)` (SECURITY INVOKER), `change_request_authorized(p_operation text,p_schema text,p_table text)` (SECURITY DEFINER), `guard_pilot_baseline_promotion()` (SECURITY DEFINER). Proprietário `postgres` em 3/3; `search_path` explícito em 3/3. `anon` e `authenticated` sem USAGE do schema em 3/3. Busca textual simples de padrão `UPDATE%change_control_state` ou `INSERT%change_control_state`: 0/3 correspondências. **Isto não prova inexistência de escritores**: SQL dinâmico, funções em outros schemas, triggers, chamadas externas e ordem do texto podem escapar à busca.

## Registro incremental
| Objeto | Fingerprint lógico | SHA de referência | Delta | Estado | Risco | Próxima ação / aceite |
|---|---|---|---|---|---|---|
| `cko_governance.change_control_state` | `pg_proc:cko_governance:ILIKE(change_control_state OR destructive_writes_blocked):20261116` | `c8f8690` | 3 funções candidatas identificadas | PASS_INVENTORY / HOLD_SECURITY | bypass administrativo e invocação indireta | expandir busca cross-schema e dependências; testes isolados de autorização |
| `cko_governance.change_request_authorized` | `pg_proc:change_request_authorized:textual-ref` | `c8f8690` | SECURITY DEFINER confirmado, sem USAGE dos papéis públicos | PASS_INVENTORY / HOLD_SECURITY | privilégios transitivos | inspecionar grafo de chamadas e configuração de API |
| `cko_governance.guard_pilot_baseline_promotion` | `pg_proc:guard_pilot_baseline_promotion:textual-ref` | `c8f8690` | dependência textual encontrada | PASS_INVENTORY / HOLD_SECURITY | promoção não autorizada | validar trigger e caminhos de execução |

Fingerprints acima são identificadores lógicos da consulta, não hashes criptográficos do catálogo; não alegar equivalência semântica.

## Cobertura e gates
- Busca textual em funções do schema: 3/3 resultados examinados (PASS de triagem; denominador não é o total de possíveis invocadores).
- Matriz ACL administrativa anterior: 48/48 verificações de catálogo, não reprocessadas.
- Relações inventariadas anteriormente: 678/678 quantitativas; sem homologação semântica nesta rodada.
- Ferramentas homologadas: 0/24; contratos homologados: 0/20 (últimos checkpoints, não reavaliados).
- CI, testes dinâmicos e testes clínicos: NOT_RUN.
- Global: não aferível sem denominador de critérios de aceite.
- HOLD_SECURITY: análise de invocadores cross-schema, SQL dinâmico, funções SECURITY DEFINER e testes de autorização.
- HOLD_HUMAN: migrations, merge bloqueado, publicação clínica e jurídica.

## Próxima execução
1. Ampliar consulta SELECT para todos os schemas de aplicação, incluindo dependências de `pg_depend` e triggers.
2. Conferir head atual da PR #73, CI e branches prioritárias; não presumir hashes.
3. Retomar correções seguras e testes das 24 ferramentas e parsers após comparação semântica.
4. Preservar dados candidatos, RLS, LGPD e fail-closed.

Nenhum DDL/DML, migration, seed, alteração de ACL ou merge. Rollback do checkpoint: revert do commit documental; banco inalterado.
