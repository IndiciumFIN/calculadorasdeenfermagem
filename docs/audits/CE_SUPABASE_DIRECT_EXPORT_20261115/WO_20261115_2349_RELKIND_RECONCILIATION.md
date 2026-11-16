# WO 2026-11-15 23:49 BRT — reconciliação de classes de relações PostgreSQL

## Proveniência
- Fonte física: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; somente SELECT em pg_catalog.pg_class/pg_namespace; sem Neon/SOT/WU-TRIB.
- GitHub PR #73; baseline commit `80d8de8fb830d162f602f8a8e200196f69a9a722`; manifest blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`.
- Inventário original `MANIFEST.json`: 612 physical_tables, 49 views, 17 sequences, total 678 relations; snapshot não atômico.
- Query read-only:
```sql
SELECT c.relkind, count(*)::int AS n
FROM pg_catalog.pg_class c
JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname NOT IN ('pg_catalog','information_schema')
  AND n.nspname NOT LIKE 'pg_toast%'
  AND n.nspname NOT LIKE 'pg_temp%'
  AND c.relkind IN ('r','p','v','m','f','S')
GROUP BY c.relkind ORDER BY c.relkind;
```

## Evidência nova e delta
| relkind | Quantidade física | Classificação |
|---|---:|---|
| r | 611 | tabelas ordinárias |
| p | 1 | tabela particionada |
| v | 49 | views |
| S | 17 | sequências |
| m, f | 0 | materializadas/foreign tables no escopo |
| **Total** | **678** | **PASS_COUNT** |

- `r+p = 612/612`, `v = 49/49`, `S = 17/17`, `total = 678/678`: **delta de contagem zero** para quatro agregações comparáveis.
- O levantamento anterior de 661 relações excluía as 17 sequências; portanto, a diferença 678 - 661 = 17 decorre do filtro de `relkind`, **não é drift demonstrado**.
- Não comprova igualdade de nomes, OIDs, colunas, hashes, constraints, RLS, conteúdo ou consistência transacional. Os 59 schemas continuam pendentes de confronto com filtro idêntico.

## CI e bloqueios preservados
- GitHub Actions run `43783129926`: jobs `Canonical contracts and CLI smoke` e `Full admission blockers (fail closed)` permanecem FAIL na consulta desta rodada.
- Passos falhos: `Verify canonical source and policy references` e `Reject unresolved parser or import dependencies`. Logs de assertions não recuperados; não modificar os gates por inferência.
- PASS: SQL SELECT, reconciliação de contagens de relações 678/678, manifesto e classes de objeto examinados.
- FAIL: 2 jobs de admissão; NO MERGE.
- HOLD_SEMANTIC / HOLD_HUMAN: 24 ferramentas (0/24 homologadas), publicação, RLS, licenças, LGPD, equivalência editorial e classificação de status.
- NOT_RUN: testes dinâmicos, diffs por objeto, CI novo, correções funcionais.

## Fingerprint e próxima ação
- Chave de reconciliação: `pgsybzggewhinaniybiy:pg_class:relkind:r,p,v,m,f,S:exclude_system:2026-11-15T23:49-03:00`.
- Último commit de referência: `80d8de8fb830d162f602f8a8e200196f69a9a722`.
- Próximo: confrontar nomes+schemas+tipos das 678 relações com `relations.json`, por fingerprint; depois colunas/PK/FK e crosswalk das 24 ferramentas. Recuperar logs exatos do CI antes de corrigir código.
- Rollback: remover somente este arquivo documental em commit reversível; nenhuma migration, seed, DDL, DML, merge ou alteração de produção foi executada.
