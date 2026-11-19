# CE / CKO / NCOS — checkpoint 2026-11-19 01:50 BRT

## Escopo, referência e proibições
Fonte anterior: commit `78e4d9afb90bf211ac770607e6b57cbd9cba77e2`, checkpoint `docs/audits/WO_20261119_0047_SCHEMA_SCOPE_CI_CHECKPOINT.md` (blob `a4be2f99fe97bb7d0cc5bd521a192f9135756d6c`). Banco único `pgsybzggewhinaniybiy`; somente SELECT. Não usar Neon, Supabase SOT, conteúdo contábil, DDL/DML, migrations, seeds, merge ou deploy. Nenhum fingerprint previamente aprovado reprocessado sem delta.

## CI observado no commit anterior
`78e4d9afb90bf211ac770607e6b57cbd9cba77e2`: Pipeline Determinístico PASS (run 44453999944), Proveniência Supabase PASS (44453999854), CI - Validação PASS (44453999844), Canonical repository invariants FAIL (44453999856). **3/4 PASS, global FAIL**. Jobs detalhados, smoke e CI após este checkpoint NOT_RUN. PR #73 permanece NO-GO até revalidação.

## Branches comparadas novamente com main
| Branch | Ahead | Behind | Arquivos alterados | Fingerprint de referência |
|---|---:|---:|---:|---|
| feat/ce-tools-governed-backend-20261115 | 15 | 0 | 33 | base e0f62491b104f4a97c6025a6393cabc2e7ada30e |
| feat/cko-catalog-metamodel-automated-20261114 | 22 | 0 | 48 | base e0f62491b104f4a97c6025a6393cabc2e7ada30e |
| feat/cko-m08-m09-corpus-atomic-20261114 | 8 | 0 | 8 | base e0f62491b104f4a97c6025a6393cabc2e7ada30e |
| integration/cko-parsers-catalog-20261114 | 163 | 0 | 175 | base e0f62491b104f4a97c6025a6393cabc2e7ada30e |

Comparação 4/4 PASS_READ; HEADs individuais 0/4 NOT_CAPTURED. Branch metamodelo propõe remoção de `contracts/fonts/*`, incluindo `DIRECTORY_OBSOLETO.json`; **não remover sem análise de consumidores**. Ferramentas continuam candidatas, não publicadas.

## Novo SELECT físico: constraints por tipo em oito namespaces explicitamente clínicos/CKO
Consulta executada: `SELECT n.nspname AS schema_name,c.contype AS constraint_type,count(*) AS total FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname IN ('cko_governance','ce_platform','ce_research_candidate','calculadoras_de_enfermagem','cko_device','cko_orch','cko_ai','cko_validation') GROUP BY n.nspname,c.contype ORDER BY n.nspname,c.contype`.

| Schema | CHECK | FK | PK | UNIQUE | Total |
|---|---:|---:|---:|---:|---:|
| calculadoras_de_enfermagem | 88 | 26 | 22 | 2 | 138 |
| ce_platform | 3 | 135 | 96 | 18 | 252 |
| ce_research_candidate | 63 | 30 | 23 | 1 | 117 |
| cko_ai | 10 | 28 | 17 | 2 | 57 |
| cko_device | 27 | 36 | 28 | 12 | 103 |
| cko_governance | 61 | 81 | 88 | 34 | 264 |
| cko_orch | 26 | 35 | 27 | 3 | 91 |
| cko_validation | 5 | 25 | 21 | 2 | 53 |
| **Amostra explícita** | **283** | **396** | **322** | **74** | **1075** |

A amostra de oito schemas é uma **subseleção diagnóstica**, não whitelist aprovada, nem reconciliação do export de 59 schemas/1996 constraints. Não comparar totais de snapshots ou escopos distintos. Crosswalk individual 0/1996 HOLD_SEMANTIC. Não foram consultados objetos contábeis.

## Work orders — estado e aceites
| WO / objeto | Delta / fingerprint | Status / teste | Risco | Responsável / próxima ação | Aceite |
|---|---|---|---|---|---|
| CE-CI-73 / PR #73 | SHA 78e4d9af; 4 workflows verificados | FAIL 3/4; smoke NOT_RUN | alto | engenharia: logs de jobs e correção isolada | 4/4 PASS e smoke no mesmo SHA |
| CE-PG-SCOPE / pg_constraint | SELECT agrupado acima, 8 schemas e 1075 constraints | PASS_READ; HOLD_SEMANTIC | alto | dados: whitelist a partir do manifesto de export | 1996/1996 crosswalk com justificativas |
| CE-EXPORT / hashes | 22/22 PASS_HASH histórico, nenhum delta comprovado | NOT_RUN atual | médio | auditoria: revalidar somente delta | hash/snapshot coerentes |
| CE-TOOLS / branch 15 ahead | 33 arquivos | HOLD_VERIFY 0/24 | alto | engenharia/clínica: auth, RLS, testes | 24/24 com gates |
| CE-METAMODEL / branch 22 ahead | 48 arquivos; remoções legacy candidatas | HOLD_VERIFY | alto | arquitetura: dicionário, PK/FK e consumidores | equivalência e smoke |
| CE-CORPUS / branch 8 ahead | 8 arquivos | HOLD_VERIFY | alto | curadoria: licença, proveniência e dedup | átomos auditáveis |
| CE-PARSERS / branch 163 ahead | 175 arquivos | FAIL histórico, 0/16 corrigidos nesta rodada | alto | engenharia: reaproveitamento seletivo | 16/16 PASS |
| CE-IMPORTS / 5 históricos | fingerprint individual não capturado | FAIL histórico, 0/5 corrigidos | alto | engenharia: smoke/import isolado | 5/5 PASS |
| CE-LEGACY / contracts/fonts | diferença de branch observada | HOLD_VERIFY | alto | engenharia: inventariar consumidores | nenhuma regressão |
| CE-WORKSPACE-71 / PR #71 | HEAD histórico 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d, não relido agora | HOLD_VERIFY | alto | engenharia: CI/auth/RLS | gates independentes |

## Progresso e decisão
CI 3/4 workflows PASS (75% dos workflows, **não do projeto**); comparações 4/4; HEADs 0/4; ferramentas revalidadas 0/24; parsers corrigidos 0/16; imports 0/5; crosswalk 0/1996. Export informado: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 policies RLS — **não homologado nesta rodada**. Testes locais/adversariais NOT_RUN; CI novo NOT_RUN. **Estimativa global: NÃO AFERÍVEL** (denominador de aceite ausente).

Nenhuma correção funcional nesta rodada. Somente comparação GitHub, verificação de workflows, SELECT físico e atualização deste checkpoint. PRs sem merge, candidatos não publicados; gates clínicos, jurídicos, LGPD, segurança, copyright e proveniência permanecem fail-closed. Nenhuma fonte oficial externa nova usada.
