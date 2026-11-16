# WO — 2026-11-16 12:56 BRT — SECURITY DEFINER default EXECUTE ACL

## Escopo e evidência física
- Projeto: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` (único SOT físico). Consulta somente SELECT em `pg_proc`, `pg_namespace`, `pg_depend`, `has_function_privilege`; nenhum corpo executado.
- GitHub origem: PR #73, branch `audit/ce-supabase-migration-first-20261115`; checkpoint anterior `904e9b7436db0a90a13881fe8fc96fe957fc9f4e`.
- Fingerprint lógico: `pgsybzggewhinaniybiy/cko_governance/pg_proc/prosecdef/proacl/prokind/proowner/anon+authenticated-EXECUTE/2026-11-16T12:56-03:00`. SHA de linhas: NOT_COMPUTED. Não tratar fingerprint lógico como hash criptográfico.

## Resultado novo — somente leitura
| Controle | Resultado | Estado |
| --- | ---: | --- |
| Funções totais em `cko_governance` | 161/161 | PASS quantitativo |
| Funções `SECURITY DEFINER` | 35/161 | PASS quantitativo |
| Funções `SECURITY DEFINER` com `proacl IS NULL` (ACL padrão) | 20/35 | HOLD_SECURITY |
| Funções `SECURITY DEFINER` com EXECUTE efetivo por `anon` | 20/35 | HOLD_SECURITY |
| Funções `SECURITY DEFINER` com EXECUTE efetivo por `authenticated` | 20/35 | HOLD_SECURITY |
| Funções `SECURITY DEFINER` com ACL explícita e sem EXECUTE efetivo por esses papéis | 15/35 | PASS pontual |
| Funções `SECURITY DEFINER` com `proconfig IS NULL` | 0/35 | PASS configuração presente; conteúdo não auditado |
| Owners de funções `SECURITY DEFINER` | 35/35 `postgres` | HOLD_SECURITY para privilégio elevado |
| Classes `prokind` em todo o schema | 161 funções ordinárias (`f`) | PASS inventário |
| Testes dinâmicos de RPC/autorização | 0/20 | NOT_RUN |
| Ferramentas clínicas homologadas | 0/24 | HOLD_HUMAN |

As 20 funções com ACL padrão coincidem com as 20 que retornam EXECUTE efetivo para os dois papéis examinados. Isto é consistente com privilégio padrão de execução de funções para PUBLIC, mas **não prova alcançabilidade**: checkpoint anterior confirmou ausência de USAGE do schema para esses papéis. Não revogar automaticamente: algumas funções são triggers e uma mudança pode quebrar fluxos internos. `pg_depend` aponta 47 dependentes de trigger para `audit_protected_row_change`, 94 para `block_uncontrolled_destructive_change`, e 1 para cada uma de `enqueue_material_finding_learning_v1`, `guard_material_finding_closure_learning_v1`, `guard_pilot_baseline_promotion`, `route_material_finding_to_super_v1`; esses números são dependências catalogadas, não número de chamadas possíveis.

## Programa incremental — próximo delta
1. **P0 / HOLD_SECURITY** — auditar por assinatura `pg_get_function_identity_arguments`, `prorettype`, `pg_event_trigger`, `pg_trigger`, `pg_depend`, `pg_get_functiondef` e invocadores, sem executar função. Mapear RPC/exposed schemas e privilégios indiretos por papel.
2. **P0 / HOLD_HUMAN** — propor, em branch e migration candidata não aplicada, REVOKE seletivo e grants explícitos necessários, com testes negativos, rollback idempotente, impacto de triggers e autorização específica.
3. **P1 / FAIL histórico** — resolver 22 achados do CI canônico e divergências semânticas dos 20 contratos; revalidar apenas fingerprints alterados.
4. **P1 / HOLD_VERIFY** — reconciliar SQL candidato e 24 ferramentas, metamodelo, dicionário e corpus M08/M09 contra objetos reais.

## Critérios e segurança
- PASS segurança exige privilégio efetivo, caminho de invocação, testes por papel, isolamento de API, ausência de escalonamento e revisão de `SECURITY DEFINER`/search_path.
- Não houve DDL/DML, migration, seed, mudança de grants, merge ou execução de funções. Rollback de dados não aplicável; documento reversível via git revert.
- Cobertura física de relações previamente inventariadas: 678/678 quantitativa, não homologação semântica. Cobertura de ACL para SECURITY DEFINER neste schema: 35/35 catalogadas; homologação de alcançabilidade 0/20. Percentual global: NÃO AFERIDO, denominador de critérios de aceite ainda incompleto.
