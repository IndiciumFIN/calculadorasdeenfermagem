# CE / CKO / NCOS — checkpoint 2026-11-19 07:50 BRT

## Escopo e proveniência
PR #73 (DRAFT): `audit/ce-supabase-migration-first-20261115`, HEAD de entrada `969618eca1e8bf8f719a02268140857066297206`. Checkpoint anterior `WO_20261119_0653_CI_BRANCH_PG_CHECKPOINT.md`, blob `8380e5ac9f115d7cf4f702261ea12a6cd6503a1d`. Banco físico exclusivo `pgsybzggewhinaniybiy`. Consultas somente SELECT. Nenhuma publicação.

## Delta verificado nesta rodada
- GitHub Actions HEAD 969618ec: Pipeline Determinístico 44500618034 PASS; CE Migration-first Supabase provenance 44500618138 PASS; CI - Validação 44500618231 PASS; Canonical repository invariants 44500618163 FAIL. Jobs falhos: 135479104770 Full admission blockers; 135479105050 Canonical contracts and CLI smoke. Logs integrais lidos; exit code 2 fail-closed. Pendências reportadas: diretório legado contracts/fonts, 16 MISSING_PARSER, 5 PACKAGE_IMPORT_NAMESPACE. Não houve evidência de resolução; correções funcionais NOT_RUN.
- Export `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` relido com grafia correta. `project_ref=pgsybzggewhinaniybiy`, `snapshot_consistency=NON_ATOMIC_ACROSS_QUERIES`, `approval_state=HOLD_HUMAN`, `source_file_count=22`. Inventário: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 policies. Esses números são inventário, não homologação.
- Supabase SELECT de pg_catalog.pg_constraint/pg_namespace: ce_platform 3 CHECK+135 FK+96 PK+18 UNIQUE=252; cko_governance 61+81+88+34=264; public 53+71+48+25=197. Total 713. Não comparar esse subconjunto ao total do export sem harmonização de escopo/snapshot.
- PR #71 workspace permanece DRAFT/NO-GO; preview, auth e homologação independentes pendentes.

## Work orders / fingerprints / risco / responsável / aceite
| WO | Objeto e referência | Delta e teste | Status | Risco | Responsável e próxima ação | Aceite |
|---|---|---|---|---|---|---|
| 01 | PR73 HEAD 969618ec; CI run 44500618163 | logs dos 2 jobs lidos; 3/4 workflows PASS | FAIL | alto | Engenharia: mapear consumidores e corrigir imports/parsers com smoke | 4/4 PASS + testes negativos |
| 02 | contracts/fonts | legado detectado no CI; SHA de arquivo não capturado | HOLD_HUMAN | alto | Engenharia: inventário de consumidores antes de remoção | zero consumidores quebrados |
| 03 | packages/cli/parsers/*.py | 16 MISSING_PARSER; fingerprints por arquivo pendentes | FAIL | alto | Engenharia: comparar integration/cko-parsers-catalog-20261114 e testar implementações reais | 16/16 PASS |
| 04 | packages/cli/{kernel,main,validators} | 5 PACKAGE_IMPORT_NAMESPACE | FAIL | alto | Engenharia: smoke python -m packages.cli.main e testes | 5/5 PASS |
| 05 | MANIFEST.json | releitura da versão no HEAD; hash não recapturado | PASS_READ | médio | Dados: verificar SHA em próxima leitura | identidade e escopo confirmados |
| 06 | constraints.jsonl | blob histórico 83642780302397204b39796e1bd3604a77c68f53; 8/1996 previamente confrontadas; sem delta demonstrado | HOLD_SEMANTIC | alto | Dados: cruzar por schema, tabela, nome, tipo, definição, PK/FK e fingerprint; pular 8 sem delta | 1996/1996 classificadas |
| 07 | ce_platform | SELECT: 252 constraints | PASS_READ | médio | Dados: crosswalk individual | equivalência objeto a objeto |
| 08 | cko_governance | SELECT: 264 constraints | PASS_READ | médio | Dados: crosswalk individual | equivalência objeto a objeto |
| 09 | public | SELECT: 197 constraints | PASS_READ | alto | Dados: verificar grants/RLS/PK/FK | zero exposição indevida |
| 10 | feat/ce-tools-governed-backend-20261115 | 24 ferramentas; SHA individual NOT_CAPTURED | NOT_RUN | alto | Engenharia/clínica: contrato e RLS, testes | 24/24 gates |
| 11 | feat/cko-catalog-metamodel-automated-20261114 | SHA individual NOT_CAPTURED | HOLD_VERIFY | alto | Arquitetura: dicionário, modelo, normativos | correspondência semântica |
| 12 | feat/cko-m08-m09-corpus-atomic-20261114 | SHA individual NOT_CAPTURED | HOLD_VERIFY | alto | Curadoria: licenças, proveniência e dedup | átomos rastreáveis |
| 13 | integration/cko-parsers-catalog-20261114 | SHA individual NOT_CAPTURED | HOLD_VERIFY | alto | Engenharia: confronto seletivo, sem stubs | testes de parsers |
| 14 | workspace PR71 | DRAFT; SHA atual NOT_CAPTURED | HOLD_VERIFY | alto | Engenharia: CI, preview, auth | gates independentes PASS |

## Percentuais e decisão
CI do HEAD de entrada: 3/4 (75% dos workflows, global FAIL); diagnóstico dos jobs falhos 2/2 (100% leitura); crosswalk histórico 8/1996 (0,40% cobertura, não homologação); ferramentas 0/24 (0% revalidação); parsers 0/16 (0% correção confirmada); imports 0/5 (0% correção confirmada). **Estimativa global de conclusão: NÃO AFERÍVEL** (denominadores clínicos/jurídicos/funcionais não consolidados). Testes locais novos NOT_RUN; CI após este checkpoint NOT_RUN. Nenhuma correção funcional nesta rodada. Próxima execução: corrigir código comprovadamente com testes; evitar repetição de diagnóstico sem delta. Fontes externas normativas novas: nenhuma. Sem DDL/DML, migration, seed, merge, deploy, exclusão ou publicação. Fail-closed e gates LGPD, direitos autorais, clínicos, jurídicos e segurança mantidos.
