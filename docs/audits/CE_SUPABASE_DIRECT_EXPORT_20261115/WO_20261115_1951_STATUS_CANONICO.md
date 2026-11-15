# CE / CKO / NCOS — WO-20261115-1951: inventário de estados reais de promoção

**Escopo:** somente leitura; projeto Supabase `pgsybzggewhinaniybiy`; branch de auditoria PR #73. **HOLD_HUMAN**, sem autorização de publicação, DDL, DML ou merge.

## Fontes e rastreabilidade
- PostgreSQL: `pg_attribute` para `cko_governance.controlled_artifacts`; `SELECT status,count(*) ... GROUP BY status` no mesmo objeto; `pg_proc` com `pg_get_functiondef` e referência a `change_control_state`. Consultado em 2026-11-15.
- GitHub: PR #73, HEAD anterior `65699b5f6d8645912f4ada15f2dfad5d57307d54`, base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`, draft.
- Referência normativa técnica: https://supabase.com/docs/guides/database/postgres/row-level-security ; https://www.postgresql.org/docs/current/ddl-rowsecurity.html (consulta documental pendente).

## Delta observado
A tabela física `cko_governance.controlled_artifacts` possui 15 colunas, incluindo `artifact_class`, `status`, `current_version_ref`, `normative_refs`, `schema_refs` e `human_gate_mode`. O censo de valores de `status` retornou **30 valores distintos** e **530 registros**. Exemplos: `ACTIVE` 225, `CONTROLLED_CANDIDATE` 159, `FINAL_TECHNICAL_WITH_SCOPED_HOLDS` 45, `CANDIDATE` 20, `FINAL_CONTROLLED` 16, `RECOVERED_RECONCILIATION_CANDIDATE` 16, `RECOVERED_HISTORICAL_PENDING_SUCCESSOR_RECONCILIATION` 9, `CANDIDATE_HOLD` 7, `PASS_WITH_SCOPED_HOLDS` 5; demais 28. **Nenhum status isoladamente comprova publicação clínica.**

O filtro restrito a funções no schema `cko_governance` que referenciam textualmente `change_control_state` retornou **3 funções**: `agent_w3_coord_family_execute_v1` (invoker), `change_request_authorized` (definer), `guard_pilot_baseline_promotion` (definer). O censo anterior de quatro funções abrangia outros schemas; **não são resultados contraditórios**. Busca textual não prova inexistência de chamadas indiretas.

## Decisões e gates
- **PASS_CATALOG:** 15/15 colunas físicas catalogadas; 30/30 status retornados pelo agrupamento, 530 registros.
- **HOLD_SEMANTIC:** não inferir `PILOT_BASELINE` publicado por substring em `status`. A expressão de promoção deve ser testada contra os 30 status reais e contra casos negativos artificiais antes de qualquer correção de função.
- **HOLD_SECURITY:** inventariar EXECUTE/USAGE e caminhos de escrita indireta do guard.
- **HOLD_PRIVACY:** auditoria de payload JSONB e minimização LGPD.
- **NOT_RUN:** testes dinâmicos, CI e rollback; **0 migrations, 0 seeds, 0 merges, 0 ferramentas homologadas de 24**.

## Próxima ação independente
Produzir teste offline parametrizado de classificação de status (30 casos reais + casos adversariais), sem alterar SQL produtivo. Em seguida confrontar as 24 ferramentas candidatas com `ce_platform.clinical_tools` e `clinical_evidence_bindings` por chave e significado; somente após diff semântico, teste e rollback, propor integração. Não criar tabelas paralelas.

## Registro incremental
| Objeto | Fingerprint lógico | Commit-base | Status | Próxima ação |
|---|---|---|---|---|
| `cko_governance.controlled_artifacts` | 15 colunas; 30 status; 530 linhas (2026-11-15) | `65699b5f` | PASS_CATALOG / HOLD_SEMANTIC | classificador de status |
| `cko_governance.change_control_state` | 3 funções textuais no schema de governança | `65699b5f` | HOLD_SECURITY | chamadas e privilégios |
