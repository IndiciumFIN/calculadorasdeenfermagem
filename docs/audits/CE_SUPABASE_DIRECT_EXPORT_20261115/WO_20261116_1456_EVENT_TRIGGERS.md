# WO — Event triggers e caminhos privilegiados (2026-11-16 14:56 BRT)

## Escopo e origem
- Supabase físico exclusivo: Calculadoras-Smart `pgsybzggewhinaniybiy`.
- Branch de auditoria: `audit/ce-supabase-migration-first-20261115`; checkpoint anterior `WO_20261116_1356_SECURITY_DEFINER_TRIGGER_PATHS.md` (blob `5b4d422e1bf3d2b3758c2066b14e429b4760f41e`).
- Consulta exclusivamente SELECT: `SELECT e.evtname,e.evtevent,e.evtenabled,n.nspname,p.proname,p.prosecdef FROM pg_event_trigger e JOIN pg_proc p ON p.oid=e.evtfoid JOIN pg_namespace n ON n.oid=p.pronamespace ORDER BY e.evtname LIMIT 100;`.
- Fingerprint lógico: project-id + SQL acima + data 2026-11-16; resultado catalogado nesta WO. Não reexecutar sem delta relevante.

## Resultado físico novo
9 event triggers ativos (evtenabled=O) encontrados. Dois são funções SECURITY DEFINER em `cko_governance`:
1. `cko_emergency_ddl_guard_drop` — evento `sql_drop` → `cko_governance.guard_cko_sql_drop`.
2. `cko_emergency_ddl_guard_end` — evento `ddl_command_end` → `cko_governance.guard_cko_ddl_end`.
Outro SECURITY DEFINER: `ensure_rls` (`public.rls_auto_enable`), evento `ddl_command_end`.
Outros seis event triggers pertencem a `extensions` e não são SECURITY DEFINER segundo pg_proc: `issue_graphql_placeholder`, `issue_pg_cron_access`, `issue_pg_graphql_access`, `issue_pg_net_access`, `pgrst_ddl_watch`, `pgrst_drop_watch`.

## Interpretação e gates
- **PASS de inventário:** 9/9 event triggers listados; 2 caminhos de evento para funções privilegiadas `cko_governance` que não aparecem em `pg_trigger` comum.
- **HOLD_SECURITY:** invocação efetiva, cadeia de dependências, permissões por role e efeitos laterais não testados. Não confundir privilégio EXECUTE ou associação a evento com exposição HTTP.
- **NOT_RUN:** testes dinâmicos, CI, testes de autorização e rollback.
- **HOLD_HUMAN:** nenhuma autorização para alterar grants, triggers, funções, migrations ou publicar.
- Ferramentas homologadas 0/24; contratos homologados 0/20; relações contadas anteriormente 678/678, sem homologação semântica. Progresso global NÃO AFERIDO.

## Próxima ação e critérios de aceite
1. SELECT de `pg_depend`, `pg_proc` e `pg_get_functiondef` das duas funções `cko_governance`; identificar chamadas indiretas e ações que exigem privilégios de DDL.
2. Comparar SQL candidato com o catálogo físico e registrar fingerprints por objeto sem duplicar tabelas.
3. Executar CI de parsers/contratos e corrigir apenas falhas reproduzidas.
4. Para liberar segurança: matriz role → endpoint → função → tabela, teste negativo de autorização, evidência de rollback idempotente e revisão humana quando aplicável.

Nenhum DDL/DML, seed, migration, merge, alteração de ACL ou execução de função privilegiada foi realizado.
