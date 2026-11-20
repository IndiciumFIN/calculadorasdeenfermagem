# CE / CKO / NCOS — checkpoint 2026-11-19 05:52 BRT

## Escopo e origem
PR #73 `audit/ce-supabase-migration-first-20261115` HEAD inicial `2fbc0fd2a5c982a7a11507944982dbaa361f8c2b`, DRAFT/NO-GO. Export `MANIFEST.json` blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`, `constraints.jsonl` blob `83642780302397204b39796e1bd3604a77c68f53`; sem delta nos blobs examinados. Checkpoint anterior blob `fd2922c1cca718b0f922bd13632342ea80e6744e`. Banco único `pgsybzggewhinaniybiy` (Calculadoras-Smart); somente SELECT.

## Avanço material: primeiro crosswalk de constraints
Confrontadas as primeiras 8 linhas de `constraints.jsonl` com consulta física por `schema_name=account_palm`, `relation_name=atomization_eval_sample_v1`, `name`, `constraint_type`, `deferrable`, `initially_deferred` e `pg_get_constraintdef(oid,true)`. **8/8 identidade, tipo, flags e semântica estrutural coincidentes**; CHECK difere apenas em parênteses externos de formatação, sem diferença no predicado. Duas FK, uma UNIQUE, uma PK e quatro CHECK; nenhuma diferença de referências/colunas/valores constatada. Estado `PASS_SEMANTIC_SAMPLE`, não homologação clínica nem snapshot global. O export é `NON_ATOMIC_ACROSS_QUERIES` e `HOLD_HUMAN`; 8/1996 verificadas, 1988 ainda não verificadas. Não confundir 35 definições adicionais PK/FK lidas nesta rodada (OFFSET 25 LIMIT 35) com crosswalk.

## CI
Quatro workflows associados ao HEAD inicial: CE Migration-first Supabase provenance run 44483207393 PASS; Pipeline Determinístico run 44483207384 PASS; CI - Validação run 44483207736 PASS; Canonical repository invariants run 44483207462 FAIL. CI após este checkpoint NOT_RUN. Nenhuma correção de código nesta rodada.

## Programa de trabalho / WOs
| WO/objeto | SHA/fingerprint/delta | Estado/teste | Risco | Responsável e próxima ação | Critério de aceite |
|---|---|---|---|---|---|
| PR73/CI | HEAD inicial 2fbc0fd2; 4 runs acima | 3/4 PASS, global FAIL | alto | Engenharia: diagnosticar canonical jobs, corrigir código e smoke | 4/4 PASS e smoke |
| constraints: account_palm.atomization_eval_sample_v1 | export blob 83642780; 8 nomes e definições confrontados; delta semântico 0/8 | 8/8 PASS_SEMANTIC_SAMPLE | médio | Dados: manter fingerprint e verificar apenas delta | identidade + predicado + FK + flags |
| constraints restantes | export blob 83642780; 1988 não confrontadas | 8/1996 total PASS_SAMPLE | alto | Dados: crosswalk por lotes com snapshot/escopo | 1996/1996 comparadas ou justificadas |
| Amostra física PK/FK | 35 definições adicionais, OFFSET 25; sem crosswalk | 35/35 PASS_READ | médio | Dados: casar por nome e definição com export | crosswalk individual |
| Export histórico | MANIFEST blob 8099e3ff, 22 arquivos; sem delta observado | PASS_READ; hashes históricos 22/22, NOT_RUN atual | alto | Auditoria: verificar deltas de arquivo | snapshot consistente |
| 24 ferramentas | feat/ce-tools-governed-backend-20261115; HEAD não capturado | 0/24 revalidadas NOT_RUN | alto | Engenharia/clínica: RLS, direitos, contratos | 24/24 gates |
| Metamodelo | feat/cko-catalog-metamodel-automated-20261114; HEAD não capturado | HOLD_VERIFY | alto | Arquitetura: PK/FK/dicionário | semântica comprovada |
| Corpus M08/M09 | feat/cko-m08-m09-corpus-atomic-20261114; HEAD não capturado | HOLD_VERIFY | alto | Curadoria: direitos, proveniência, dedup | átomos rastreáveis |
| Parsers | integration/cko-parsers-catalog-20261114; 16 falhas históricas | 0/16 corrigidos | alto | Engenharia: comparar implementação e imports | 16/16 testes |
| Imports | 5 erros históricos | 0/5 corrigidos | alto | Engenharia: smoke sem stubs | 5/5 PASS |
| contracts/fonts | legado detectado em CI anterior | FAIL histórico | alto | Engenharia: mapear consumidores antes de remover | zero consumidores + smoke |
| Workspace PR71 | HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d | DRAFT/NO-GO | alto | Engenharia: preview externo, auth | build, auth e release gates |

## Métricas e decisão
Crosswalk físico semântico 8/1996 (0,40% da lista histórica; **não** homologação), 35/35 novas definições lidas, CI 3/4 PASS (75% de workflows, global FAIL), 0/24 ferramentas revalidadas, 0/16 parsers corrigidos, 0/5 imports corrigidos. Estimativa global de conclusão: **NÃO AFERÍVEL**, denominadores de aceite clínico/jurídico/funcional não consolidados. Testes locais NOT_RUN; CI novo NOT_RUN. Sem DDL/DML, migration, seed, merge, deploy, exclusão ou publicação. Gates fail-closed, LGPD, licenças, proveniência, segurança e clínica preservados. Fontes externas novas: nenhuma.
