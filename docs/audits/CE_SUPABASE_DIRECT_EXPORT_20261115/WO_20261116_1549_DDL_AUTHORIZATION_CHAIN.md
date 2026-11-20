# WO — Cadeia de autorização dos event triggers CKO (2026-11-16 15:49 BRT)

## Origem e controle incremental
- Banco físico exclusivo: Calculadoras-Smart `pgsybzggewhinaniybiy`. Consultas somente SELECT.
- Branch: `audit/ce-supabase-migration-first-20261115`; base main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; comparação nesta rodada: 46 commits ahead, 0 behind.
- Checkpoint de entrada: `WO_20261116_1456_EVENT_TRIGGERS.md`, blob `58c69adde2e25a450f76c449574c946bbab6ec43`.
- Fingerprint lógico de consulta: projeto + nomes das funções + consulta a `pg_proc`, `pg_namespace` e `pg_get_functiondef` em 2026-11-16. Guardar definições completas apenas em consulta controlada; não confundir fingerprint lógico com SHA criptográfico de conteúdo.

## Nova evidência física
- `cko_governance.guard_cko_sql_drop()` e `cko_governance.guard_cko_ddl_end()` são SECURITY DEFINER, owner postgres, search_path restrito a `pg_catalog, cko_governance`; chamam `cko_governance.change_request_authorized('DDL',schema,'*')`.
- `cko_governance.change_request_authorized(text,text,text)` é SQL STABLE SECURITY DEFINER, owner postgres, mesmo search_path.
- A autorização consulta `cko_governance.change_control_state`, `cko_governance.change_requests` e `current_setting('cko.change_request_id',true)`; exige status APPROVED/EXECUTING, validade temporal, operação/escopo, backup_ref e rollback_plan conforme flags. Ausência de solicitação retorna false quando `destructive_writes_blocked` está ativo ou ausente.
- **Ponto de revisão crítica:** quando `destructive_writes_blocked=false`, a função retorna true antes de verificar a change request. Isso pode ser um mecanismo intencional de manutenção, mas sua governança e autorização de alteração do estado precisam ser demonstradas. Não classificar como vulnerabilidade confirmada sem análise de grants, RLS e processos.
- **Ponto de revisão estática:** conferir em teste isolado o predicado `LIKE` que seleciona schemas `cko_%` e o escape de underscore. Nenhum DDL foi executado para testar os event triggers.

## Status e programa
| Objeto/camada | Evidência | Estado | Próxima ação |
|---|---|---|---|
| 2 funções de event trigger CKO | 2/2 definições lidas | PASS inventário | Testes estáticos de cobertura de schemas |
| Função de autorização | 1/1 definição lida | PASS inventário | Revisar estado, grants, trilha de aprovação e GUC |
| Segurança da cadeia completa | 0/3 homologadas | HOLD_SECURITY | Matriz de acesso e testes negativos em ambiente isolado |
| Relações físicas | 678/678 (checkpoint anterior) | PASS quantitativo | Diferença semântica PK/FK e SQL candidato |
| Ferramentas clínicas | 0/24 homologadas | HOLD_HUMAN | Testes e revisão clínica |
| Contratos | 0/20 homologados | HOLD_VERIFY | CI e parsers |
| CI nesta rodada | 0 executados | NOT_RUN | Rodar testes de regressão |
| Percentual global | denominador de aceite não consolidado | NÃO AFERIDO | Criar matriz canônica de critérios |

## Gates e reversão
Nenhuma modificação no banco, nas ACLs, em funções, triggers, migrations, seeds ou na main. Reversão deste checkpoint: reverter exclusivamente o commit documental. Alterações futuras de banco requerem autorização específica, diff semântico, teste isolado e rollback idempotente. Não promover candidatos sem gates clínicos, jurídicos e de segurança.

## Próxima execução
1. SELECT para inspecionar grants/ownership/RLS de `change_control_state` e `change_requests` e possíveis rotas de escrita.
2. Conferir o predicado de seleção dos schemas em teste estático isolado e corrigir apenas se reproduzido.
3. Prosseguir com CI dos parsers e delta das 24 ferramentas, preservando fingerprints já validados.
