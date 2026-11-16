# WO — 2026-11-16 03:55 BRT — checkpoint físico e controle de não duplicação

## Origem e HEAD
- Repositório IndiciumFIN/calculadorasdeenfermagem, PR #73, branch audit/ce-supabase-migration-first-20261115; HEAD observado antes deste checkpoint: cf09144602002f632059c40d9b4df96943e8ea95; base main e0f62491b104f4a97c6025a6393cabc2e7ada30e.
- PR #73: OPEN, DRAFT, não mesclada; mergeable=true é somente condição GitHub, não liberação dos gates.
- Baseline: docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json, 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices e 100 policies. Manifesto anterior; não afirmar validação semântica objeto a objeto.

## SELECT executado no projeto pgsybzggewhinaniybiy
```sql
SELECT c.relkind, count(*)::int AS n
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE c.relkind IN ('r','p','v','S')
  AND n.nspname NOT LIKE 'pg_%'
  AND n.nspname <> 'information_schema'
GROUP BY c.relkind ORDER BY c.relkind;
```
Resultado físico: S=17, p=1, r=611, v=49, total=678. PASS somente para contagem por classe, 678/678; 0/678 equivalências individuais verificadas nesta rodada. Não confundir escopo com schemas do manifesto.

## Incremental e bloqueios
| Unidade | Referência/fingerprint | Status | Delta desta rodada | Próxima ação |
|---|---|---|---|---|
| PR #73 | HEAD cf09144602002f632059c40d9b4df96943e8ea95 | DRAFT/HOLD | metadados revalidados | conferir CI pós HEAD |
| catálogo pg_class | SQL acima; classes S17,p1,r611,v49 | PASS_COUNT_ONLY | 678/678 contagem confirmada | confronto individual schema+nome+tipo+hash |
| reconciliation 20 pares | governance/migrations/2026-11-14/legacy-fonts-reconciliation.json (branch integration/cko-parsers-catalog-20261114) | HOLD_VERIFY | 0/20 revalidados | verificar cada blob e normalização |
| 16 parsers ausentes | workflow 43783129926 | HOLD | 0/16 corrigidos | mapear implementações sem stubs |
| 5 imports de namespace | workflow 43783129926 | HOLD | 0/5 corrigidos | conferir imports e testes |
| 24 ferramentas clínicas | feat/ce-tools-governed-backend-20261115 | HOLD_HUMAN | 0/24 homologadas | crosswalk físico e gates |

## Segurança e testes
SQL somente SELECT, sem funções com efeitos colaterais. Nenhuma migration, seed, DDL/DML, alteração de RLS, merge ou exclusão. Testes/CI desta rodada: NOT_RUN. Gate clínico, jurídico, licença, LGPD, proveniência e publicação: HOLD_HUMAN. Rollback do único artefato desta rodada: revert do commit documental. Próxima rodada deve priorizar validação independente dos 20 pares e teste real dos parsers, evitando repetir inventários já fechados.
