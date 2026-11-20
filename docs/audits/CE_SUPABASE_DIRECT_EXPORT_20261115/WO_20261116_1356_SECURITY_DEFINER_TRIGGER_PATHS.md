# WO — SECURITY DEFINER: invocação por triggers (2026-11-16 13:56 BRT)

## Origem e fingerprint de estado
- Supabase físico: Calculadoras-Smart `pgsybzggewhinaniybiy`; consulta somente SELECT em pg_proc/pg_namespace/pg_trigger/pg_depend, 2026-11-16.
- PR #73: head `1be129164ab310c09be376f56759742734eb91b5`, base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; aberta/draft, 44 commits, 55 arquivos alterados. Fingerprint lógico: projeto + head SHA + query abaixo + data da observação; reexecutar apenas após delta de catálogo/branch.
- Fonte de checkpoint anterior: WO_20261116_1256_SECURITY_DEFINER_DEFAULT_ACL.md.

## Evidência nova (sem invocar funções)
Consulta pg_proc + pg_trigger confirmou 20 funções SECURITY DEFINER com EXECUTE efetivo a anon e authenticated; ambas roles sem USAGE no schema cko_governance. Dessas 20, 6 têm associação a triggers comuns: audit_protected_row_change (47), block_uncontrolled_destructive_change (94), enqueue_material_finding_learning_v1 (1), guard_material_finding_closure_learning_v1 (1), guard_pilot_baseline_promotion (1), route_material_finding_to_super_v1 (1). Total de 145 associações a triggers; as outras 14 funções têm 0 associações em pg_trigger. Os nomes guard_cko_ddl_end e guard_cko_sql_drop têm 0 triggers comuns, mas podem ser usados como event triggers: NÃO concluir ausência de invocação sem consultar pg_event_trigger.

## Estados e cobertura
- Inventário de funções privilegiadas: 35/35 PASS (checkpoint anterior); 20/35 com EXECUTE efetivo para roles examinadas.
- Triagem de triggers comuns entre funções com EXECUTE: 20/20 PASS de inventário; 6/20 com trigger comum, 14/20 sem trigger comum (não implica inalcançabilidade).
- Avaliação de caminhos indiretos/event triggers/API: 0/20 HOLD_SECURITY; testes dinâmicos 0/20 NOT_RUN.
- Relações quantitativas: 678/678 PASS de contagem em checkpoint anterior; homologação semântica não demonstrada.
- Ferramentas clínicas homologadas: 0/24 HOLD_HUMAN; contratos homologados: 0/20 HOLD_VERIFY.
- Percentual global: NÃO AFERIDO; não inferir conclusão a partir da contagem física.

## Risco, decisão e próxima ação
HOLD_SECURITY: triggers podem executar funções com privilégios do proprietário em operações realizadas por outras roles. Ausência de USAGE no schema não basta para provar ausência de caminho indireto. Não revogar EXECUTE nem alterar triggers sem matriz de dependências, teste de regressão, rollback idempotente e aprovação específica.
Próximo SELECT: pg_event_trigger, pg_depend, pg_get_functiondef, políticas e grants de funções invocadoras; classificar caminho direto/indireto por papel e endpoint, sem executar funções com efeitos colaterais. Depois revisar CI e parsers com testes reais.

## Segurança
Nenhuma DDL/DML, migration, seed, merge, mudança de ACL ou publicação nesta rodada. Gate clínico, jurídico, LGPD e publicação permanecem HOLD_HUMAN.
