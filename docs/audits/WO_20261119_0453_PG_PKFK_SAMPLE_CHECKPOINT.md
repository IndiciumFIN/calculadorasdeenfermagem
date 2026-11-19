# CE / CKO / NCOS — checkpoint 2026-11-19 04:53 BRT

## Escopo, proveniência e delta
Repositório IndiciumFIN/calculadorasdeenfermagem, branch da PR #73 `audit/ce-supabase-migration-first-20261115`. Checkpoint antecedente `WO_20261119_0354_CI_JOB_LOGS_SCOPE_CHECKPOINT.md` blob SHA `7123ae44eb85e1a244ffaa10fd19198f2077c3b3`, conteúdo relido nesta rodada. Export `MANIFEST.json` blob SHA `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`, relido sem delta identificado. Banco único `pgsybzggewhinaniybiy`. Nenhum Neon ou Supabase alternativo.

## Nova evidência física, somente SELECT
Consulta `pg_constraint JOIN pg_namespace JOIN pg_class` restrita a `ce_platform`, `cko_governance`, `public`, contype p/f, ORDER BY schema/tabela/constraint, LIMIT 25. **25/25 definições PK/FK lidas**, não comparadas com export, portanto **0/1996 reconciliadas**. A amostra retornada pertence a `ce_platform`. Exemplos de relações físicas: `ce_platform.alert_rules(owner_user_id) -> auth.users(id) ON DELETE CASCADE`; `ce_platform.assessments(canonical_id) -> ce_platform.canonical_objects(canonical_id) ON DELETE CASCADE`; `ce_platform.career_path_steps` possui PK composta `(path_id,ordinal)` e FK `target_canonical_id -> ce_platform.canonical_objects(canonical_id)`. Nenhuma deduplicação automática ou inferência de equivalência com SQL candidato. Contagem dos três schemas confirmada novamente: ce_platform 252; cko_governance 264; public 197 = 713. Os 1996 do export são escopo/snapshot distinto; não usar diferença agregada como drift.

Manifesto histórico observado 2026-11-15: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS; `NON_ATOMIC_ACROSS_QUERIES`, `HOLD_HUMAN`. Fingerprints dos 22 arquivos somente históricos; 0/22 hashes reprocessados nesta rodada porque não foi detectado delta no manifesto.

## GitHub
PR #73 localizada; checkpoint antecedente registra 3/4 workflows PASS e Canonical invariants FAIL no run 44467750661; **CI do HEAD atual não consultado nesta rodada**. PR #71 do workspace consultada: bloqueio preview Vercel externo/cota e gates de contratos/auth independentes, DRAFT/NO-GO; não confundir com PR #73 do repositório principal. Nenhum merge.

## Programa de trabalho (WO)
| WO / objeto | SHA/fingerprint e delta | Estado / teste | Risco | Responsável / próxima ação | Aceite |
|---|---|---|---|---|---|
| PR73 / CI | checkpoint anterior blob 7123ae44; CI anterior run 44467750661 | FAIL histórico; HEAD atual NOT_RUN | alto | Engenharia: capturar HEAD e jobs atuais | 4/4 workflows + smoke PASS |
| Legado contracts/fonts | run 44467750661; sem delta inspecionado | FAIL histórico | alto | Engenharia: mapear consumidores antes de remover | zero consumidores e smoke PASS |
| Parsers | 16 ausentes no run anterior; sem novo fingerprint | 0/16 corrigidos, HOLD_VERIFY | alto | Engenharia: comparar branch integration por SHA | 16/16 com testes |
| Imports | 5 namespace errors históricos | 0/5 corrigidos, HOLD_VERIFY | alto | Engenharia: corrigir import sem stubs | 5/5 smoke PASS |
| Export / MANIFEST | blob 8099e3ff; sem delta observado | PASS_READ; 22/22 hashes históricos, NOT_RUN atual | alto | Auditoria: validar snapshot e hashes em delta | snapshot comparável |
| Catálogo constraints | SELECT 25 PK/FK e contagem 713 | 25/25 PASS_READ; 0/1996 MATCH | alto | Dados: confrontar `constraints.jsonl` por schema, tabela, tipo e definição | 1996/1996 reconciliadas ou justificadas |
| Ferramentas | branch `feat/ce-tools-governed-backend-20261115`, SHA não capturado | 0/24 revalidadas | alto | Engenharia/clínica: checar catálogo, RLS, licença | 24/24 gates |
| Metamodelo | `feat/cko-catalog-metamodel-automated-20261114`, SHA não capturado | HOLD_VERIFY | alto | Arquitetura: crosswalk PK/FK/dicionário | equivalência documentada |
| Corpus M08/M09 | `feat/cko-m08-m09-corpus-atomic-20261114`, SHA não capturado | HOLD_VERIFY | alto | Curadoria: claims/átomos/rights/dedup | proveniência e licença |
| Workspace PR71 | PR consultada 2026-11-19; sem HEAD novo | HOLD_BUILD / NO-GO | alto | Engenharia: preview e auth/contratos | preview + gates PASS |

## Métricas, gates e decisão
CI histórico 3/4 (75% dos workflows, **não** conclusão); 25/25 amostra física lida; 0/1996 constraints reconciliadas; 0/24 ferramentas revalidadas; 0/16 parsers e 0/5 imports corrigidos. Denominadores de homologação de metamodelo, corpus e direitos não consolidados. **Estimativa global de conclusão: NÃO AFERÍVEL.** Testes novos NOT_RUN; CI novo NOT_RUN. Nenhuma correção funcional nesta rodada. Gates clínicos, jurídicos, segurança, LGPD, direitos autorais, proveniência e publicação fail-closed; candidato não publicado. Sem DDL/DML, migrations, seeds, merges, deploys ou exclusões. Fontes oficiais externas novas: nenhuma.
