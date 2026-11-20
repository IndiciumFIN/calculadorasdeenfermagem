# WO 2026-11-16 19:57 BRT — triagem cross-schema do controle DDL

## Escopo e origem
Projeto físico único Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Consultas exclusivamente SELECT sobre `pg_proc` e `pg_namespace`, filtrando `prokind IN ('f','p')` e excluindo `pg_catalog` e `information_schema`. Continuidade de `WO_20261116_1852_DDL_CALLER_STATIC_SCAN.md` (blob `2caafa067865dbe4cb0578fc9eb99bea936eee4b`), commit anterior informado `36de4b4bf32dab22ac9dd15a2287bdf41735e87f`. Comparação GitHub anterior a este commit: `main` e0f62491b104f4a97c6025a6393cabc2e7ada30e; branch de auditoria 50 commits à frente e zero atrás.

## Delta verificado
Pesquisa cross-schema em `pg_proc.prosrc` por `change_control_state` OU `destructive_writes_blocked`: **4 rotinas** retornadas, versus 3 na triagem limitada a `cko_governance`. Nova candidata: `cko_validation.run_capetinha_scan_v1` (SECURITY DEFINER). As outras são `cko_governance.agent_w3_coord_family_execute_v1` (INVOKER), `cko_governance.change_request_authorized` (DEFINER), `cko_governance.guard_pilot_baseline_promotion` (DEFINER). Padrão textual regex de escrita direta na tabela: **0/4**. Uma tentativa de consulta usando `pg_get_functiondef` sobre todas as entradas de `pg_proc` falhou (42809, agregados); consulta corrigida para `prosrc` e `prokind` foi executada com sucesso. Nenhuma rotina foi invocada.

## Registro incremental
| Objeto | Fingerprint lógico / SHA de base | Delta | Status | Risco | Responsável e próxima ação / aceite |
|---|---|---|---|---|---|
| Cross-schema `pg_proc.prosrc` | `pg_proc:prosrc:ILIKE(control_state OR blocked):20261116` / `2caafa0` | 4 referências; +1 vs triagem anterior | PASS_INVENTORY / HOLD_SECURITY | SQL dinâmico e chamadas indiretas não cobertos | Engenharia: verificar definição completa da nova rotina e dependências; aceite com grafo e testes isolados |
| `cko_validation.run_capetinha_scan_v1` | `pg_proc:cko_validation:run_capetinha_scan_v1` / `2caafa0` | nova referência, DEFINER | HOLD_SECURITY | potencial alcance privilegiado | Segurança: revisar corpo, EXECUTE, USAGE e invocadores; não executar |
| 3 funções previamente catalogadas | `pg_proc:cko_governance:control_state` / `2caafa0` | sem delta na triagem | PASS_INVENTORY / HOLD_SECURITY | dependências e ACL transitiva | Segurança: manter fingerprint validado sem reprocessamento integral |

Fingerprints são identificadores lógicos, não hashes criptográficos. Resultado de regex não demonstra ausência de escritores. Busca em `prosrc` não cobre views, código cliente, SQL dinâmico, dependências por OID ou caminhos administrativos.

## Cobertura e critérios
- Referências retornadas cross-schema: **4/4 classificadas (100% dos resultados desta consulta)**; universo completo de invocadores não determinado.
- Referências em `cko_governance`: **3/3** sem delta textual nesta consulta.
- Inventário físico informado anteriormente: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 policies; **não recontado nesta execução**.
- Ferramentas clínicas: **0/24 homologadas**, contratos **0/20 homologados** conforme checkpoint anterior; **não reavaliados**.
- Testes: consulta inicial FAIL (42809); consulta corrigida PASS; CI NOT_RUN; testes dinâmicos NOT_RUN; testes clínicos NOT_RUN.
- Estimativa global de conclusão: **não aferível** (sem denominador de critérios de aceite homologados). Não inferir porcentagem do inventário.
- HOLD_SECURITY: examinar a nova rotina, dependências e autorização efetiva; HOLD_HUMAN: publicação clínica, jurídica, migrations e merges.
- Próximos passos: inspecionar corpo e privilégios da rotina nova via SELECT; verificar branches prioritárias e CI; corrigir código somente com testes e rollback.
- Nenhum DDL/DML, migration, seed, alteração de ACL, merge ou publicação. Rollback documental: revert deste commit; banco inalterado.
