# CE / CKO / NCOS — checkpoint 2026-11-19 02:48 BRT

## Descoberta de rastreabilidade: branch efetiva da PR #73
Leitura direta GitHub: PR #73 OPEN/DRAFT tem head `audit/ce-supabase-migration-first-20261115`, base `main`. O checkpoint anterior `WO_20261119_0150_CI_PG_TYPED_SCOPE_CHECKPOINT.md` foi lido na branch **distinta** `review/cko-w7-public-evidence-20261114` (blob `be54c08b97e7d7644e5e3936da612386f62466f1`; commit histórico informado `f4906d2a7d5244ba27fc93fb79d3dd548f4fa8f1`). **Não assumir que esse commit integra a PR #73.** Esta atualização é escrita na branch real da PR #73, sem merge.

PR #71 de `IndiciumFIN/dev-chatgpt-workspace`: OPEN/DRAFT; head `fix/ce-tanstack-vercel-build-no-migrations-20261114`, base `main`. HOLD_VERIFY; nenhum merge.

## Evidência GitHub e fingerprints
Comparação `main...audit/ce-supabase-migration-first-20261115`: ahead 121, behind 0, merge-base `e0f62491b104f4a97c6025a6393cabc2e7ada30e` (comparação executada nesta rodada; não é SHA do HEAD). Manifesto do export `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`; `contracts/fontes/cid10.json` blob `a38ab1a1924be155591d2e79e9d4d70b9cd5949a`. Sem delta comprovado nesses dois blobs: não reprocessados.

Manifesto (observação 2026-11-15) declara snapshot **NON_ATOMIC_ACROSS_QUERIES**, aprovação **HOLD_HUMAN**, 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies; 22 arquivos exportados. São quantidades informadas no manifesto, **não homologação**.

## CI observado
No SHA histórico `f4906d2a7d5244ba27fc93fb79d3dd548f4fa8f1`, a consulta GitHub retornou: CKO Curriculum and Market Read-only Audit PASS (run 44461190358); Pipeline Determinístico PASS (44461190392); CI - Validação PASS (44461190366); Canonical repository invariants FAIL (44461190413). **3/4 PASS entre os quatro workflows listados; global FAIL.** Esses resultados se referem à branch histórica, não constituem validação do HEAD da PR #73. CI deste novo commit NOT_RUN; smoke NOT_RUN.

## Supabase único: SELECT-only
Projeto `pgsybzggewhinaniybiy`. Consulta:
```sql
SELECT n.nspname AS schema_name, c.contype, count(*)::int AS total
FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace
WHERE n.nspname IN ('cko_governance','ce_platform','ce_research_candidate','calculadoras_de_enfermagem','cko_device','cko_orch','cko_ai','cko_validation')
GROUP BY 1,2 ORDER BY 1,2;
```
Resultado: 8 schemas, 1075 constraints (CHECK 283, FK 396, PK 322, UNIQUE 74), mesmas quantidades do checkpoint anterior. **PASS_READ / NO_DELTA_AGGREGATE**, não prova igualdade objeto a objeto. Crosswalk 0/1996 HOLD_SEMANTIC; escopo e snapshot ainda não harmonizados. Nenhuma mutação.

## Programa de trabalho / work orders
| WO / objeto | Fingerprint, delta | Estado / teste | Risco | Responsável / próxima ação | Critério de aceite |
|---|---|---|---|---|---|
| CE-PR73 / branch | head `audit/ce-supabase-migration-first-20261115`; comparação 121/0 | PASS_READ; CI HEAD NOT_RUN | alto | engenharia: capturar HEAD SHA e CI no mesmo SHA | 4/4 workflows exigidos e smoke PASS |
| CE-CI / invariants | run 44461190413 FAIL no SHA histórico f4906d2a | FAIL histórico | alto | engenharia: obter logs e corrigir parsers/imports isoladamente | invariants PASS sem desabilitar gates |
| CE-EXPORT / MANIFEST | blob 8099e3ff; snapshot não atômico | PASS_READ; HOLD_HUMAN | alto | auditoria: definir escopo/snapshot; hashes 22/22 históricos, NOT_RUN agora | fingerprints e contagens por objeto coerentes |
| CE-PG / constraints | SELECT 8 schemas, 1075; sem delta agregado | PASS_READ; 0/1996 crosswalk | alto | dados: cruzar nome/schema/tabela/tipo/definição | 1996/1996 reconciliadas ou justificadas |
| CE-TOOLS / 24 ferramentas | branch feat/ce-tools-governed-backend-20261115; SHA individual não capturado | HOLD_VERIFY 0/24 | alto | engenharia + clínica: auth/RLS/testes | 24/24 gates |
| CE-METAMODEL | branch feat/cko-catalog-metamodel-automated-20261114; SHA não capturado | HOLD_VERIFY | alto | arquitetura: PK/FK, dicionário, consumers fonts | equivalência + smoke |
| CE-CORPUS / M08/M09 | branch feat/cko-m08-m09-corpus-atomic-20261114; SHA não capturado | HOLD_VERIFY | alto | curadoria: licença/proveniência/dedup | átomos auditáveis |
| CE-PARSERS / 16 | branch integration/cko-parsers-catalog-20261114; SHA não capturado | FAIL histórico; 0/16 corrigidos nesta rodada | alto | engenharia: comparar implementação e testar | 16/16 PASS |
| CE-IMPORTS / 5 | fingerprint individual pendente | FAIL histórico; 0/5 corrigidos nesta rodada | alto | engenharia: smoke imports | 5/5 PASS |
| CE-LEGACY / contracts/fonts | sem inventário de consumidores | HOLD_HUMAN | alto | engenharia: inventariar antes de remover | zero regressões |
| CE-WORKSPACE / PR71 | OPEN/DRAFT, head fix/ce-tanstack-vercel-build-no-migrations-20261114 | HOLD_VERIFY | alto | engenharia: CI e permissões | gates independentes PASS |

## Progresso e decisão
CI histórico 3/4 (75% dos workflows listados, não do projeto); branches prioritárias com HEAD capturado nesta rodada 0/4; ferramentas 0/24; parsers corrigidos 0/16; imports 0/5; crosswalk 0/1996; export 22/22 hashes históricos, NOT_RUN atual. **Estimativa global de conclusão: NÃO AFERÍVEL** por ausência de denominador de homologação. Nenhum código funcional alterado; correção documental de associação PR/branch e programa persistente. Não houve DDL/DML, migrations, seeds, deploy, merges, exclusões ou publicação de candidatos. Gates clínicos, jurídicos, LGPD, segurança, direitos autorais e proveniência permanecem fail-closed. Nenhuma fonte oficial externa nova consultada.
