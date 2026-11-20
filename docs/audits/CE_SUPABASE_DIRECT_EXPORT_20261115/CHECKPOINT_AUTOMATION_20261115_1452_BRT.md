# CE / NCOS — checkpoint 2026-11-15 14:52 BRT

Projeto: Supabase `pgsybzggewhinaniybiy`; modo READ_ONLY; sem Neon, sem WU-TRIB/SOT.

## Evidência nova — censo completo do trigger de auditoria

Consulta executada diretamente em `pg_trigger`, `pg_class` e `pg_namespace`, filtrando `NOT t.tgisinternal` e `t.tgfoid='cko_governance.audit_protected_row_change()'::regprocedure`. Agregação por schema e bitmask `tgtype`.

| Schema | Triggers | Tabelas distintas | INSERT | UPDATE | DELETE |
|---|---:|---:|---:|---:|---:|
| cko_ai | 9 | 9 | 0 | 9 | 9 |
| cko_evidence | 2 | 2 | 0 | 2 | 2 |
| cko_governance | 28 | 28 | 0 | 28 | 28 |
| cko_master | 2 | 2 | 0 | 2 | 2 |
| cko_regulatory | 2 | 2 | 0 | 2 | 2 |
| cko_validation | 4 | 4 | 0 | 4 | 4 |
| **Total** | **47** | **47** | **0** | **47** | **47** |

**PASS_DB_READONLY**: a função é vinculada a 47 tabelas em seis schemas. O censo anterior era parcial: `cko_validation` também tem quatro tabelas protegidas. **HOLD_EVENT_COVERAGE**: nenhum dos 47 triggers observa INSERT. Os eventos de publicação, revogação e aprovação editorial não estão comprovados. Isso impede declarar equivalência com `public.ce_tool_audit` candidato.

## Continuidade e próximos gates

- Fonte base: PR #73, inventário `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/`, snapshot 59 schemas/678 relações/255 migrations. Esta rodada **não** recontou todo o snapshot, apenas os triggers da função específica.
- **HOLD_SEMANTIC**: mapear eventos de negócio e as tabelas de ferramentas; distinguir proteção genérica UPDATE/DELETE de trilha editorial INSERT/publicação/revogação.
- **HOLD_PRIVACY**: revisar retenção e minimização de JSONB before/after no ledger.
- **NOT_RUN**: testes Python/TS, CI, RLS negativos, integração dinâmica.
- **HOLD_HUMAN**: migrations, seeds, merges, publicação clínica/jurídica.
- 0 alterações SQL/DDL/DML; 0/24 ferramentas homologadas; 0 merges. O commit deste checkpoint é documental, sem correção de código nesta rodada.
- Próxima tarefa executável: analisar gatilhos e rotas do ciclo de publicação, comparar os contratos do candidato com o ledger existente e produzir testes negativos em ambiente isolado.

## Controle incremental

| Objeto | Fingerprint lógico | Estado | Próxima ação |
|---|---|---|---|
| `cko_governance.audit_protected_row_change()` e triggers associados | regprocedure + pg_trigger.tgtype, 47 linhas, 6 schemas, INSERT=0 | PASS_INVENTORY / HOLD_EVENT_COVERAGE | comparar INSERT/publicação/revogação |
| PR #73 snapshot | MANIFEST blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14` | PASS_METADATA_PREVIOUS | CI de hashes |
| SQL ferramentas | blob `aa736b0d0f1d3487326d77f346e9f710d032346a` | HOLD_SEMANTIC_PREVIOUS | crosswalk por evento |
