# WO — 2026-11-16 12:28 BRT — SECURITY DEFINER / EXECUTE (READ ONLY)

## Escopo e origem
- Fonte física: Supabase Calculadoras-Smart, project_id `pgsybzggewhinaniybiy`, catálogo `pg_proc` + `pg_namespace`; SELECT executado em 2026-11-16.
- Fonte GitHub: PR #73, branch `audit/ce-supabase-migration-first-20261115`, HEAD antes deste checkpoint `6a4fb687d428963002b05911fed8b50ceb2ad947`; base main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Fingerprint lógico desta evidência: `cko_governance|pg_proc|prosecdef|has_function_privilege(anon/authenticated,EXECUTE)|has_schema_privilege(anon/authenticated,USAGE)|2026-11-16`. Hash criptográfico do conjunto de linhas: NOT_COMPUTED; não confundir com SHA de arquivo.

## Resultado físico (SELECT)
| Indicador | Numerador/denominador | Status |
| --- | ---: | --- |
| Funções em cko_governance | 161/161 enumeradas | PASS inventário pontual |
| Funções SECURITY DEFINER | 35/161 | PASS quantitativo |
| SECURITY DEFINER com EXECUTE efetivo para anon | 20/35 | HOLD_SECURITY |
| SECURITY DEFINER com EXECUTE efetivo para authenticated | 20/35 | HOLD_SECURITY |
| Das 20, schema USAGE por anon | 0/20 | PASS de barreira de schema; não prova isolamento fim a fim |
| Das 20, schema USAGE por authenticated | 0/20 | PASS de barreira de schema; não prova isolamento fim a fim |
| Testes de chamada por papel / RPC / API | 0/20 | NOT_RUN |
| Revisão de corpos, ownership, invocadores e cadeias de chamadas | 0/20 | HOLD_VERIFY |
| Ferramentas clínicas homologadas | 0/24 | HOLD_HUMAN |

### Funções afetadas (20, identidade de nome; overloads precisam de revisão por assinatura)
`audit_protected_row_change`, `b2_render_audit_report_v1`, `b2_run_reperformance_v1`, `b3_learning_gate_v1`, `b3_render_audit_report_v1`, `b3_run_reperformance_v1`, `b4_render_aud8l_report_v1`, `b4_run_reperformance_v1`, `b4_validate_e2e_v1`, `b6_clinical_engine_v1`, `b6_clinical_renderer_v1`, `b6_clinical_runtime_v1`, `block_uncontrolled_destructive_change`, `change_request_authorized(text,text,text)`, `enqueue_material_finding_learning_v1`, `guard_cko_ddl_end`, `guard_cko_sql_drop`, `guard_material_finding_closure_learning_v1`, `guard_pilot_baseline_promotion`, `route_material_finding_to_super_v1`.

**Interpretação:** `has_function_privilege(..., 'EXECUTE')=true` não implica invocabilidade externa quando `USAGE` do schema é negado. Funções trigger/event trigger não são diretamente invocáveis por `SELECT` normal. Não afirmar exposição confirmada; investigar caminhos indiretos, ownership, roles adicionais, API exposed schemas, SECURITY DEFINER chains e default privileges. Todas as 20 funções amostradas tinham `proconfig` com `search_path` explícito, mas isso não homologa seus corpos nem seus privilégios.

## Deltas e programa de trabalho
1. **P0 SECURITY — HOLD_VERIFY**: mapear `prokind`, `pg_get_functiondef`, owners, grants explícitos, `PUBLIC`, schema usage, dependências e chamadas de funções por outras rotinas. Não executar corpos de função com efeitos.
2. **P0 SECURITY — HOLD_HUMAN**: decidir se `EXECUTE` deve ser revogado para `PUBLIC`/roles em migrations candidatas; qualquer mudança física exige testes de compatibilidade, rollback idempotente e autorização específica.
3. **P1 CI — FAIL histórico / NOT_RUN nesta rodada**: retomar 22 achados canônicos e 20 pares de contratos sem repetir hashes já validados.
4. **P1 INTEGRATION — HOLD_VERIFY**: branch `feat/ce-tools-governed-backend-20261115` comparada com main em 2026-11-16: 14 commits à frente, 0 atrás; 24 ferramentas ainda sem homologação clínica.
5. **P1 CONTENT — HOLD_VERIFY**: metamodelo, dicionário, normativos e atomização aguardam verificação semântica com inventário de origem.

## Critérios de aceite e reversão
- PASS somente após revisão de privilégio *e* alcançabilidade por papel, testes negativos e evidência versionada.
- Nenhum SQL de escrita, migration, seed, alteração de RLS ou merge nesta rodada; rollback de dados: não aplicável. Reversão documental por revert do commit deste arquivo.
- Estimativa global: NÃO AFERIDA (sem denominador canônico de critérios de aceite). Inventário físico 678/678 apenas quantitativo, não equivale a 100% operacional.
