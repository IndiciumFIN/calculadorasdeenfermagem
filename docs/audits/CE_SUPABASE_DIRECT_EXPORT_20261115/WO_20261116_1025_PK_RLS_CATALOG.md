# WO — 2026-11-16 10:25 BRT — catálogo PK/RLS (SELECT only)

## Escopo e origem
- Supabase físico: Calculadoras-Smart, project_id `pgsybzggewhinaniybiy`.
- GitHub PR #73: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/73 ; HEAD observado `586239821a5d34cc1144926de35eb1a845945721`; base `main` `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; draft, open, unmerged.
- Catálogo consultado via SELECT em `pg_class`, `pg_namespace`, `pg_constraint`, `pg_policy`; filtro `relkind IN ('r','p')`, schemas `ce_platform` e `cko_governance`.
- Fingerprint lógico do snapshot: project + schema + relkind + contagens PK/RLS/policy + data 2026-11-16; **não é hash criptográfico de todos os objetos**. A verificação por objeto continua pendente.

## Resultados físicos observados
| Schema | Tabelas | Com PK | RLS habilitado | RLS habilitado sem política | RLS desabilitado |
|---|---:|---:|---:|---:|---:|
| ce_platform | 96 | 96 | 96 | 62 | 0 |
| cko_governance | 88 | 88 | 3 | 3 | 85 |
| Total | 184 | 184 | 99 | 65 | 85 |

## Interpretação e bloqueios
- PASS estrutural: PK em 184/184 tabelas consultadas; NÃO equivale a validação de integridade referencial, dados ou FKs.
- HOLD_SECURITY: 62 tabelas ce_platform com RLS ativo e nenhuma política; isso normalmente nega acesso por roles sujeitas a RLS, mas requer teste efetivo por papel e análise de grants/serviços. Não inferir exposição pública.
- HOLD_SECURITY: 85 tabelas cko_governance sem RLS habilitado; verificar grants, schemas expostos e uso de funções SECURITY DEFINER antes de classificar risco. As outras 3 têm RLS habilitado sem políticas.
- HOLD_HUMAN: nenhuma mudança de política, grants, migrations, publicação clínica ou merge autorizada por esta verificação.
- NOT_RUN: CI, testes de role-based authorization e diffs semânticos por objeto nesta rodada.

## Programa incremental / critérios de aceite
1. P0 — cruzar as 184 tabelas por OID/nome/colunas/PK/FK/grants/RLS/policies com o inventário versionado, gerando fingerprint por objeto. Estado: 184/184 PK contadas; 0/184 objetos homologados semanticamente. Próxima ação: SELECT catálogo detalhado + diff, sem DDL.
2. P0 — 62 ce_platform RLS sem política: verificar intended deny-by-default versus necessidade funcional por papel. Estado: HOLD_SECURITY; não criar política permissiva automaticamente.
3. P0 — 85 cko_governance sem RLS: verificar grants e exposição de API. Estado: HOLD_SECURITY.
4. P0 — PR #73 permanece DRAFT/HOLD; executar CI e comparar branches/contratos antes de merge.
5. P1 — 20 contratos: 2/20 examinados anteriormente, 0/20 homologados; 16 parsers pendentes; 24 ferramentas clínicas 0/24 homologadas. Valores herdados do programa anterior, não revalidados nesta consulta.

## Delta e rollback
- Banco: 0 DDL, 0 DML, 0 migrations, 0 seeds; rollback de banco não aplicável.
- Código: apenas documentação; reversão por revert do commit documental se necessário.
- Progresso global: não aferível de modo auditável. Inventário de 678 relações não implica prontidão operacional.
